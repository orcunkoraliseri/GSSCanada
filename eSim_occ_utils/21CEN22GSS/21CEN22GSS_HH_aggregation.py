"""
21CEN22GSS Household Aggregation Module

Transforms matched 2021/2022 expanded schedules into 5-minute household
profiles for downstream BEM conversion.
"""

from __future__ import annotations

import math
import pathlib
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    def tqdm(iterable, **kwargs):
        return iterable


# =============================================================================
# HOUSEHOLD AGGREGATOR
# =============================================================================

class HouseholdAggregator:
    """
    Build 5-minute household grids from expanded schedule rows.
    """

    def __init__(self, resolution_min: int = 5):
        self.res = resolution_min
        self.slots = int(1440 / self.res)
        self.social_cols = [
            "Spouse",
            "Children",
            "parents",
            "Friends",
            "otherHHs",
            "Others",
            "otherInFAMs",
        ]

    def process_all(self, df_expanded: pd.DataFrame) -> pd.DataFrame:
        """
        Group by household/day and aggregate to a 288-slot daily grid.
        """
        print("   Grouping data by Household and Day Type...")

        time_varying_cols = [
            "start",
            "end",
            "EPINO",
            "occACT",
            "occPRE",
            "social_sum",
            "Spouse",
            "Children",
            "parents",
            "Friends",
            "otherHHs",
            "Others",
            "otherInFAMs",
        ]

        groups = df_expanded.groupby(["SIM_HH_ID", "Day_Type"])
        full_data_results = []

        for (hh_id, day_type), group_df in tqdm(groups, desc="Processing Households"):
            if "AgentID" not in group_df.columns:
                raise ValueError(
                    "Error: 'AgentID' column missing. Please re-run ProfileMatcher."
                )

            people_grids_map = {}
            people_meta_map = {}

            for agent_id, person_data in group_df.groupby("AgentID"):
                grid = self._create_individual_grid(person_data)
                people_grids_map[agent_id] = grid

                meta = person_data.iloc[0].drop(labels=time_varying_cols, errors="ignore")
                people_meta_map[agent_id] = meta

            hh_profile = self._aggregate_household(list(people_grids_map.values()))

            for agent_id, p_grid in people_grids_map.items():
                combined = pd.concat([hh_profile, p_grid], axis=1)

                meta = people_meta_map[agent_id]
                for col_name, val in meta.items():
                    combined[col_name] = val

                combined["SIM_HH_ID"] = hh_id
                combined["Day_Type"] = day_type
                combined["AgentID"] = agent_id

                full_data_results.append(combined)

        return pd.concat(full_data_results, ignore_index=True)

    def _create_individual_grid(self, episodes: pd.DataFrame) -> pd.DataFrame:
        """
        Convert variable-length episodes into fixed 5-minute resolution arrays.
        """
        loc_grid = np.zeros(self.slots, dtype=int)
        act_grid = np.zeros(self.slots, dtype=int)
        dens_grid = np.zeros(self.slots, dtype=int)

        valid_social = [c for c in self.social_cols if c in episodes.columns]
        pre_col = "occPRE" if "occPRE" in episodes.columns else "PRE"
        act_col = "occACT" if "occACT" in episodes.columns else "ACTCODE"
        start_col = "start" if "start" in episodes.columns else "STARTMIN"
        end_col = "end" if "end" in episodes.columns else "ENDMIN"

        episodes_social = episodes[valid_social].replace({1: 1, 2: 0, 9: 0}).fillna(0)
        is_home = (episodes[pre_col] == 1).astype(int)

        episodes = episodes.copy()
        episodes["social_sum"] = episodes_social.sum(axis=1) * is_home

        for _, row in episodes.iterrows():
            s_raw = int(row[start_col])
            s_min = (s_raw // 100) * 60 + (s_raw % 100)

            e_raw = int(row[end_col])
            e_min = (e_raw // 100) * 60 + (e_raw % 100)

            s_idx = int(np.floor(s_min / self.res))
            e_idx = int(np.floor(e_min / self.res))

            s_idx = max(0, min(s_idx, self.slots - 1))
            e_idx = max(0, min(e_idx, self.slots))

            if e_idx > s_idx:
                loc_grid[s_idx:e_idx] = row[pre_col]
                act_grid[s_idx:e_idx] = row[act_col]
                dens_grid[s_idx:e_idx] = row["social_sum"]
            elif e_idx < s_idx:
                loc_grid[s_idx:] = row[pre_col]
                act_grid[s_idx:] = row[act_col]
                dens_grid[s_idx:] = row["social_sum"]

                loc_grid[:e_idx] = row[pre_col]
                act_grid[:e_idx] = row[act_col]
                dens_grid[:e_idx] = row["social_sum"]

        return pd.DataFrame(
            {
                "ind_occPRE": loc_grid,
                "ind_occACT": act_grid,
                "ind_density": dens_grid,
            }
        )

    def _aggregate_household(self, people_grids: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate individual grids to household presence, density, and activity.
        """
        time_slots = pd.date_range("00:00", "23:55", freq=f"{self.res}min").strftime("%H:%M")
        hh_df = pd.DataFrame({"Time_Slot": time_slots})

        if not people_grids:
            hh_df["occPre"] = 0
            hh_df["occDensity"] = 0
            hh_df["occActivity"] = "0"
            return hh_df

        loc_stack = np.vstack([p["ind_occPRE"].values for p in people_grids])
        presence_binary = (loc_stack == 1).astype(int)
        occupancy_count = presence_binary.sum(axis=0)
        hh_df["occPre"] = (occupancy_count >= 1).astype(int)

        dens_stack = np.vstack([p["ind_density"].values for p in people_grids])
        hh_df["occDensity"] = dens_stack.sum(axis=0)

        act_stack = np.vstack([p["ind_occACT"].values for p in people_grids])
        activity_sets = []

        for t in range(self.slots):
            acts_at_t = act_stack[:, t]
            pres_at_t = presence_binary[:, t]
            valid_acts = acts_at_t[pres_at_t == 1]

            if len(valid_acts) > 0:
                unique_acts = sorted(np.unique(valid_acts))
                unique_acts = [str(a) for a in unique_acts if a > 0]
                act_str = ",".join(unique_acts) if unique_acts else "0"
            else:
                act_str = "0"

            activity_sets.append(act_str)

        hh_df["occActivity"] = activity_sets
        return hh_df


# =============================================================================
# VALIDATION
# =============================================================================

def validate_household_aggregation(
    df_full: pd.DataFrame,
    report_path: Optional[Path] = None,
) -> bool:
    """
    Perform basic logical checks on the aggregated output and optionally save a report.
    """
    logs = []

    def log(message: str) -> None:
        print(message)
        logs.append(str(message))

    log(f"\n{'=' * 60}")
    log("  VALIDATING HOUSEHOLD AGGREGATION")
    log(f"{'=' * 60}")

    all_passed = True

    log("\n1. CHECKING TIME GRID COMPLETENESS...")
    if "AgentID" not in df_full.columns:
        log("   Error: 'AgentID' column missing.")
        return False

    counts = df_full.groupby(["AgentID", "Day_Type"]).size()
    if (counts == 288).all():
        log(f"   [OK] All {len(counts):,} person-days have exactly 288 time slots.")
    else:
        errors = counts[counts != 288]
        log(f"   [ERROR] Found {len(errors)} incomplete profiles.")
        log(f"      Sample errors: {errors.head().to_dict()}")
        all_passed = False

    log("\n2. CHECKING LOGIC (Presence vs. Density)...")
    empty_house = df_full[df_full["occPre"] == 0]
    ghosts = empty_house[empty_house["occDensity"] > 0]
    if len(ghosts) == 0:
        log("   [OK] No social density detected in empty houses.")
    else:
        log(f"   [ERROR] Found {len(ghosts):,} rows where House is Empty but Density > 0.")
        all_passed = False

    log("\n3. CHECKING ACTIVITY STRINGS...")
    if "occActivity" in empty_house.columns:
        ghost_activities = empty_house[empty_house["occActivity"].astype(str) != "0"]
        if len(ghost_activities) == 0:
            log("   [OK] Activity is correctly marked '0' when empty.")
        else:
            log(f"   [ERROR] Found {len(ghost_activities):,} rows with activities in empty house.")
            all_passed = False

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(logs) + "\n", encoding="utf-8")

    return all_passed


def visualize_multiple_households(
    df_full: pd.DataFrame,
    n_samples: int = 16,
    output_img_path: Optional[Path] = None,
    report_path: Optional[Path] = None,
) -> None:
    import matplotlib.pyplot as plt

    msg_start = f"\n4. GENERATING VISUAL VERIFICATION PLOT ({n_samples} Households)..."
    print(msg_start)

    if report_path and report_path.exists():
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(msg_start + "\n")

    interesting_ids = df_full[df_full["occDensity"] > 1]["SIM_HH_ID"].unique()
    if len(interesting_ids) == 0:
        print("   Warning: No high-density households found. Sampling random ones.")
        interesting_ids = df_full["SIM_HH_ID"].unique()

    actual_n = min(n_samples, len(interesting_ids))
    sample_ids = np.random.choice(interesting_ids, actual_n, replace=False)

    cols = 4
    rows = math.ceil(actual_n / cols)
    figsize_height = rows * 3

    fig, axes = plt.subplots(rows, cols, figsize=(15, figsize_height), sharex=False)
    axes = np.array(axes).flatten()

    for i, ax in enumerate(axes):
        if i < actual_n:
            hh_id = sample_ids[i]
            mask = (df_full["SIM_HH_ID"] == hh_id) & (df_full["Day_Type"] == "Weekday")
            df_hh = df_full[mask].copy()

            if df_hh.empty:
                mask = (df_full["SIM_HH_ID"] == hh_id) & (df_full["Day_Type"] == "Weekend")
                df_hh = df_full[mask].copy()

            df_plot = df_hh[["Time_Slot", "occPre", "occDensity"]].drop_duplicates()
            x = range(len(df_plot))

            if df_plot.empty:
                ax.text(0.5, 0.5, "No Data", ha="center")
                continue

            ax.fill_between(x, df_plot["occPre"], step="pre", color="green", alpha=0.3, label="Occupied")
            ax.set_ylim(0, 1.2)
            ax.set_yticks([])
            ax.set_ylabel("Presence", fontsize=8, color="green")

            ax2 = ax.twinx()
            ax2.plot(x, df_plot["occDensity"], color="blue", linewidth=1.5, label="Density")
            ax2.set_ylabel("Density", fontsize=8, color="blue")
            ax2.tick_params(axis="y", labelsize=8)

            ax.set_title(f"Household #{hh_id}", fontsize=10, fontweight="bold", pad=3)

            ticks = np.arange(0, 288, 48)
            if len(df_plot) >= 288:
                labels = [df_plot["Time_Slot"].iloc[j] for j in ticks if j < len(df_plot)]
            else:
                labels = [""] * len(ticks)
            ax.set_xticks(ticks[:len(labels)])
            ax.set_xticklabels(labels, rotation=45, fontsize=8)
            ax.grid(True, alpha=0.2)

            if i == 0:
                lines, lbls = ax.get_legend_handles_labels()
                lines2, lbls2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, lbls + lbls2, loc="upper left", fontsize=8)
        else:
            ax.axis("off")

    plt.tight_layout()

    if output_img_path:
        output_img_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_img_path, dpi=150)
        msg_end = f"   [OK] Batch Plot saved to: {output_img_path.name}"
        print(msg_end)
        if report_path and report_path.exists():
            with open(report_path, "a", encoding="utf-8") as f:
                f.write(msg_end + "\n")

    plt.close()


# =============================================================================
# MAIN
# =============================================================================

def main(sample_pct: int = 10, skip_validation: bool = False) -> None:
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR

    input_dir = BASE_DIR / "Outputs_21CEN22GSS" / "ProfileMatching"
    output_dir = BASE_DIR / "Outputs_21CEN22GSS" / "HH_aggregation"
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"_sample{sample_pct}pct" if sample_pct < 100 else ""
    expanded_file = input_dir / f"21CEN22GSS_Full_Schedules{suffix}.csv"

    output_file = output_dir / f"21CEN22GSS_Full_Aggregated{suffix}.csv"
    report_path = output_dir / f"21CEN22GSS_Validation_HH{suffix}.txt"
    plot_path = output_dir / f"21CEN22GSS_Validation_Plot{suffix}.png"

    print("=" * 60)
    print("  21CEN22GSS HOUSEHOLD AGGREGATION")
    print("=" * 60)

    print("\n1. Loading Expanded Schedules...")
    if not expanded_file.exists():
        print(f"   Error: {expanded_file.name} not found.")
        print(f"   Run ProfileMatcher first with --sample {sample_pct}")
        return

    df_expanded = pd.read_csv(expanded_file, low_memory=False)
    print(f"   Loaded: {len(df_expanded):,} rows")
    print(f"   Unique Households: {df_expanded['SIM_HH_ID'].nunique():,}")
    print(f"   Unique Agents: {df_expanded['AgentID'].nunique():,}")

    aggregator = HouseholdAggregator(resolution_min=5)

    print("\n2. Starting Process (Grid Construction + Aggregation)...")
    df_final = aggregator.process_all(df_expanded)

    print(f"\n3. Saving Full Integrated Data to: {output_file.name}...")
    df_final.to_csv(output_file, index=False)

    print("\n" + "=" * 60)
    print("  VERIFICATION")
    print("=" * 60)
    print(f"   Total Rows: {len(df_final):,}")
    print(f"   Total Columns: {len(df_final.columns)}")
    print(f"   Sample Columns: {list(df_final.columns[:5])} ... {list(df_final.columns[-3:])}")
    print("\n   Household Presence (occPre) Stats:")
    print(f"     - Home slots: {(df_final['occPre'] == 1).sum():,}")
    print(f"     - Away slots: {(df_final['occPre'] == 0).sum():,}")

    if not skip_validation:
        validate_household_aggregation(df_final, report_path=report_path)
        visualize_multiple_households(
            df_full=df_final,
            n_samples=16,
            output_img_path=plot_path,
            report_path=report_path,
        )
        print(f"\n   Validation Report saved to: {report_path.name}")

    print("\n" + "=" * 60)
    print("  [OK] HOUSEHOLD AGGREGATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Household Aggregation: Census 2021 + GSS 2022")
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Sample percentage used in ProfileMatcher (default: 10)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation step",
    )
    args = parser.parse_args()

    main(sample_pct=args.sample, skip_validation=args.skip_validation)
