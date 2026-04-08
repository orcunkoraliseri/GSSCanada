"""
21CEN22GSS Occupancy to BEM Conversion Module

Converts 5-minute household profiles into hourly BEM schedules for
EnergyPlus/Honeybee simulations.
"""

from __future__ import annotations

import pathlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm


# =============================================================================
# BEM CONVERTER
# =============================================================================

class BEMConverter:
    """
    Convert 5-minute ABM profiles into hourly BEM schedules.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metabolic_map = {
            "1": 125,
            "2": 175,
            "3": 190,
            "4": 195,
            "5": 70,
            "6": 105,
            "7": 170,
            "8": 110,
            "9": 90,
            "10": 85,
            "11": 245,
            "12": 105,
            "13": 140,
            "14": 135,
            "0": 0,
        }

        self.dtype_map = {
            "1": "SingleD",
            "2": "Apartment",
            "3": "OtherDwelling",
        }

        self.pr_map = {
            "10": "Atlantic",
            "24": "Quebec",
            "35": "Ontario",
            "46": "Prairies",
            "48": "Alberta",
            "59": "BC",
        }

    def process_households(self, df_full: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the full 5-minute household table to hourly BEM schedules.
        """
        print("\n   Starting BEM Conversion (Hourly Resampling)...")

        df_full = df_full.copy()
        df_full["datetime"] = pd.to_datetime(df_full["Time_Slot"], format="%H:%M")
        print("   Mapping metabolic rates...")
        df_full["watts_5min"] = df_full["occActivity"].apply(self._calculate_watts)

        groups = df_full.groupby(["SIM_HH_ID", "Day_Type"])
        bem_schedules = []

        target_res_cols = ["DTYPE", "BEDRM", "CONDO", "ROOM", "REPAIR", "PR"]
        tier_cols = ["MATCH_TIER_WD", "MATCH_TIER_WE"]

        for (hh_id, day_type), group in tqdm(groups, desc="Generating Schedules"):
            hh_size = self._get_scalar(group, ["HHSIZE", "Census_HHSIZE"], default=1)

            res_data = {}
            for col in target_res_cols:
                val = self._get_scalar(group, [col, f"Census_{col}"], default="Unknown")

                if col == "DTYPE":
                    val_str = self._normalize_dtype_value(val)
                    res_data[col] = self.dtype_map.get(val_str, val_str)
                elif col == "PR":
                    val_str = self._normalize_numeric_value(val)
                    res_data[col] = self.pr_map.get(val_str, val_str)
                else:
                    res_data[col] = val

            g_indexed = group.set_index("datetime")
            hourly = g_indexed.resample("60min").agg(
                {
                    "occPre": "mean",
                    "occDensity": "mean",
                    "watts_5min": "mean",
                }
            ).reset_index()

            estimated_count = hourly["occPre"] * (hourly["occDensity"] + 1)
            occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)

            wd_tier = group["MATCH_TIER_WD"].iloc[0] if "MATCH_TIER_WD" in group.columns else ""
            we_tier = group["MATCH_TIER_WE"].iloc[0] if "MATCH_TIER_WE" in group.columns else ""
            match_tier = max(wd_tier, we_tier) if (wd_tier or we_tier) else ""

            data_dict = {
                "SIM_HH_ID": hh_id,
                "Day_Type": day_type,
                "Hour": hourly["datetime"].dt.hour,
                "HHSIZE": hh_size,
                **res_data,
                "MATCH_TIER": match_tier,
                "Occupancy_Schedule": occupancy_sched.round(3),
                "Metabolic_Rate": hourly["watts_5min"].round(1),
            }

            bem_schedules.append(pd.DataFrame(data_dict))

        return pd.concat(bem_schedules, ignore_index=True)

    def _get_scalar(self, group: pd.DataFrame, columns: list[str], default=None):
        for col in columns:
            if col in group.columns:
                series = group[col].dropna()
                if not series.empty:
                    return series.iloc[0]
        return default

    def _normalize_numeric_value(self, val) -> str:
        if pd.isna(val) or val == "Unknown":
            return "Unknown"
        try:
            return str(int(float(val)))
        except Exception:
            return str(val)

    def _normalize_dtype_value(self, val) -> str:
        if pd.isna(val) or val == "Unknown":
            return "Unknown"
        if isinstance(val, str) and val in self.dtype_map.values():
            return val
        return self._normalize_numeric_value(val)

    def _calculate_watts(self, act_str: str) -> float:
        if act_str == "0":
            return 0

        codes = str(act_str).split(",")
        watts = [self.metabolic_map.get(c.strip(), 100) for c in codes]
        return sum(watts) / len(watts)


# =============================================================================
# VISUALIZATION
# =============================================================================

def visualize_bem_distributions(df_bem: pd.DataFrame, output_dir: Path = None) -> None:
    """
    Generate temporal and non-temporal validation plots.
    """
    print("\n   GENERATING BEM DISTRIBUTION PLOTS...")

    if output_dir is None:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    path_temporal = output_dir / "21CEN22GSS_BEM_temporals.png"
    path_nontemporal = output_dir / "21CEN22GSS_BEM_non_temporals.png"

    sns.set_theme(style="whitegrid")

    fig1, axes1 = plt.subplots(3, 2, figsize=(16, 15))

    sns.histplot(
        data=df_bem, x="Occupancy_Schedule", bins=20, kde=False,
        color="green", alpha=0.6, ax=axes1[0, 0]
    )
    axes1[0, 0].set_title("Population Distribution: Occupancy Fractions")
    axes1[0, 0].set_xlabel("Occupancy (0=Empty, 1=Full)")

    active_watts = df_bem[df_bem["Metabolic_Rate"] > 0]
    sns.histplot(
        data=active_watts, x="Metabolic_Rate", bins=30, kde=True,
        color="orange", alpha=0.6, ax=axes1[0, 1]
    )
    axes1[0, 1].set_title("Population Distribution: Metabolic Rates (Occupied)")
    axes1[0, 1].set_xlabel("Watts per Person")

    sns.lineplot(
        data=df_bem, x="Hour", y="Occupancy_Schedule", hue="Day_Type",
        estimator="mean", errorbar=("sd", 1),
        palette={"Weekday": "green", "Weekend": "teal"}, ax=axes1[1, 0]
    )
    axes1[1, 0].set_title("Population Trend: Average Presence Schedule")
    axes1[1, 0].set_ylim(0, 1.05)
    axes1[1, 0].set_xticks(range(0, 25, 4))

    sns.lineplot(
        data=active_watts, x="Hour", y="Metabolic_Rate", hue="Day_Type",
        estimator="mean", errorbar=None,
        palette={"Weekday": "orange", "Weekend": "red"}, ax=axes1[1, 1]
    )
    axes1[1, 1].set_title("Population Trend: Average Metabolic Intensity (Heat Output)")
    axes1[1, 1].set_xticks(range(0, 25, 4))

    occupancy_check = df_bem.groupby("SIM_HH_ID")["Occupancy_Schedule"].max()
    valid_ids = occupancy_check[occupancy_check > 0].index

    if len(valid_ids) > 0:
        sample_id = np.random.choice(valid_ids)
        sample_data = df_bem[df_bem["SIM_HH_ID"] == sample_id]

        wd_data = sample_data[sample_data["Day_Type"] == "Weekday"].sort_values("Hour")
        we_data = sample_data[sample_data["Day_Type"] == "Weekend"].sort_values("Hour")

        def plot_dual_axis(ax, data, title):
            if data.empty:
                ax.text(0.5, 0.5, "No Data", ha="center")
                return
            x = data["Hour"]
            ax.fill_between(x, data["Occupancy_Schedule"], color="green", alpha=0.3, label="Occupancy")
            ax.set_ylim(0, 1.1)
            ax.set_ylabel("Occupancy Fraction", color="green", fontsize=10)
            ax.tick_params(axis="y", labelcolor="green")
            ax2 = ax.twinx()
            ax2.plot(x, data["Metabolic_Rate"], color="darkorange", linewidth=2.5, label="Heat Gain")
            ax2.set_ylabel("Metabolic Rate (W)", color="darkorange", fontsize=10)
            ax2.tick_params(axis="y", labelcolor="darkorange")
            ax2.set_ylim(0, 300)
            ax.set_title(title, fontsize=12, fontweight="bold")
            ax.set_xticks(range(0, 25, 4))
            ax.set_xlabel("Hour of Day")
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc="upper left")

        plot_dual_axis(axes1[2, 0], wd_data, f"Sample Household #{sample_id}: Weekday Schedule")
        plot_dual_axis(axes1[2, 1], we_data, f"Sample Household #{sample_id}: Weekend Schedule")
    else:
        axes1[2, 0].text(0.5, 0.5, "No Valid Samples Found", ha="center")
        axes1[2, 1].axis("off")

    plt.tight_layout()
    fig1.savefig(path_temporal, dpi=150)
    plt.close(fig1)
    print(f"   Temporal Plot saved: {path_temporal.name}")

    cols_static = [c for c in ["SIM_HH_ID", "DTYPE", "BEDRM", "ROOM", "PR"] if c in df_bem.columns]
    df_static = df_bem[cols_static].drop_duplicates(subset=["SIM_HH_ID"])

    if len(df_static) > 0 and len(cols_static) > 1:
        fig2, axes2 = plt.subplots(2, 2, figsize=(15, 12))
        axes2 = axes2.flatten()

        if "DTYPE" in df_static.columns:
            sns.countplot(
                data=df_static, x="DTYPE", hue="DTYPE",
                palette="viridis", ax=axes2[0], legend=False
            )
            axes2[0].set_title("Distribution of Dwelling Types")
            axes2[0].tick_params(axis="x", rotation=15, labelsize=8)
            axes2[0].set_ylabel("Count of Households")
        else:
            axes2[0].text(0.5, 0.5, "DTYPE missing", ha="center")

        if "BEDRM" in df_static.columns:
            sns.countplot(
                data=df_static, x="BEDRM", hue="BEDRM",
                palette="magma", ax=axes2[1]
            )
            axes2[1].set_title("Distribution of Bedroom Counts")
            axes2[1].set_ylabel("Count of Households")
        else:
            axes2[1].text(0.5, 0.5, "BEDRM missing", ha="center")

        if "ROOM" in df_static.columns:
            sns.histplot(
                data=df_static, x="ROOM", discrete=True,
                color="purple", alpha=0.7, ax=axes2[2]
            )
            axes2[2].set_title("Distribution of Total Room Counts")
            axes2[2].set_ylabel("Count of Households")
        else:
            axes2[2].text(0.5, 0.5, "ROOM missing", ha="center")

        if "PR" in df_static.columns:
            pr_order = ["Atlantic", "Quebec", "Ontario", "Prairies", "Alberta", "BC"]
            sns.countplot(
                data=df_static, x="PR", hue="PR",
                order=pr_order,
                palette="coolwarm", ax=axes2[3], legend=False
            )
            axes2[3].set_title("Distribution by Region (PR)")
            axes2[3].tick_params(axis="x", rotation=15, labelsize=8)
            axes2[3].set_ylabel("Count of Households")
        else:
            axes2[3].text(0.5, 0.5, "PR missing", ha="center")

        plt.tight_layout()
        fig2.savefig(path_nontemporal, dpi=150)
        plt.close(fig2)
        print(f"   Non-Temporal Plot saved: {path_nontemporal.name}")
    else:
        print("   Skipped Non-Temporal plots (Residential columns missing).")


def validate_bem_schedule(df_bem: pd.DataFrame, report_path: Path | None = None) -> bool:
    """
    Validate hourly row counts and value ranges.
    """
    logs = []

    def log(message: str) -> None:
        print(message)
        logs.append(str(message))

    log(f"\n{'=' * 60}")
    log("  VALIDATING BEM CONVERSION")
    log(f"{'=' * 60}")

    all_passed = True

    counts = df_bem.groupby(["SIM_HH_ID", "Day_Type"]).size()
    if (counts == 24).all():
        log(f"   [OK] All {len(counts):,} household-days have exactly 24 hourly rows.")
    else:
        bad = counts[counts != 24]
        log(f"   [ERROR] Found {len(bad)} household-days with non-24-hour output.")
        log(f"      Sample errors: {bad.head().to_dict()}")
        all_passed = False

    occ_min = df_bem["Occupancy_Schedule"].min()
    occ_max = df_bem["Occupancy_Schedule"].max()
    met_min = df_bem["Metabolic_Rate"].min()
    if occ_min < 0 or occ_max > 1:
        log(f"   [ERROR] Occupancy_Schedule out of range: min={occ_min}, max={occ_max}")
        all_passed = False
    else:
        log(f"   [OK] Occupancy_Schedule within [0, 1] (min={occ_min:.3f}, max={occ_max:.3f}).")

    if met_min < 0:
        log(f"   [ERROR] Metabolic_Rate has negative values: min={met_min}")
        all_passed = False
    else:
        log(f"   [OK] Metabolic_Rate is non-negative (min={met_min:.1f}).")

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(logs) + "\n", encoding="utf-8")

    return all_passed


# =============================================================================
# MAIN
# =============================================================================

def main(sample_pct: int = 10) -> None:
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR

    input_dir = BASE_DIR / "Outputs_21CEN22GSS" / "HH_aggregation"
    output_dir = BASE_DIR / "Outputs_21CEN22GSS" / "occToBEM"
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"_sample{sample_pct}pct" if sample_pct < 100 else ""
    full_data_path = input_dir / f"21CEN22GSS_Full_Aggregated{suffix}.csv"
    output_path = output_dir / f"21CEN22GSS_BEM_Schedules{suffix}.csv"
    report_path = output_dir / f"21CEN22GSS_Validation_BEM{suffix}.txt"

    print("=" * 60)
    print("  21CEN22GSS OCCUPANCY TO BEM CONVERSION")
    print("=" * 60)

    print("\n1. Loading Household Data...")
    if not full_data_path.exists():
        print(f"   Error: {full_data_path.name} not found.")
        print(f"   Run HH_aggregation first with --sample {sample_pct}")
        return

    df_full = pd.read_csv(full_data_path, low_memory=False)
    print(f"   Loaded: {len(df_full):,} rows")
    print(f"   Unique Households: {df_full['SIM_HH_ID'].nunique():,}")

    converter = BEMConverter(output_dir=output_dir)
    df_bem = converter.process_households(df_full)

    print(f"\n2. Saving Hourly BEM Input to: {output_path.name}")
    df_bem.to_csv(output_path, index=False, float_format="%.3f")

    print("\n" + "=" * 60)
    print("  VERIFICATION: Sample Household")
    print("=" * 60)

    pd.options.display.float_format = "{:.3f}".format
    cols_to_show = [
        "SIM_HH_ID",
        "Hour",
        "DTYPE",
        "BEDRM",
        "ROOM",
        "Occupancy_Schedule",
        "Metabolic_Rate",
    ]
    valid_cols = [c for c in cols_to_show if c in df_bem.columns]
    print(df_bem[valid_cols].head(12).to_string(index=False))

    night_occ = df_bem[df_bem["Hour"].isin(range(0, 7))]["Occupancy_Schedule"].mean()
    day_occ = df_bem[df_bem["Hour"].isin(range(9, 18))]["Occupancy_Schedule"].mean()
    print(f"\n   Mean nighttime occupancy (0-6h): {night_occ:.3f}")
    print(f"   Mean daytime occupancy  (9-17h): {day_occ:.3f}")
    if night_occ > day_occ:
        print("   [OK] Nighttime > daytime (expected for residential)")
    else:
        print("   [!] Check: daytime >= nighttime (unexpected for residential)")

    validate_bem_schedule(df_bem, report_path=report_path)

    print("\n3. Generating Visualization Plots...")
    visualize_bem_distributions(df_bem, output_dir=output_dir)

    print("\n" + "=" * 60)
    print("  [OK] BEM CONVERSION COMPLETE")
    print("  Ready for EnergyPlus/Honeybee!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Occupancy to BEM Conversion: Census 2021 + GSS 2022"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Sample percentage used in previous steps (default: 10)",
    )
    args = parser.parse_args()

    main(sample_pct=args.sample)
