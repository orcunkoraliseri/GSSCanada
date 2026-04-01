"""
21CEN22GSS Profile Matcher Module

Matches Census 2021 agents with GSS 2022 schedules based on aligned
demographic profiles, then expands the matched schedules for downstream
household aggregation and BEM conversion.
"""

from __future__ import annotations

import pathlib
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm


# =============================================================================
# MATCHING CONFIGURATION
# =============================================================================

DEFAULT_SAMPLE_PCT = 10.0

DEFAULT_TIER_1 = [
    "HHSIZE",
    "AGEGRP",
    "SEX",
    "MARSTH",
    "KOL",
    "PR",
    "LFTAG",
    "CMA",
]

DEFAULT_TIER_2 = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "LFTAG", "PR"]
DEFAULT_TIER_3 = ["HHSIZE", "AGEGRP", "SEX"]
DEFAULT_TIER_4 = ["HHSIZE"]


# =============================================================================
# MATCH PROFILER
# =============================================================================

class MatchProfiler:
    """
    Assign GSS schedules to Census agents using tiered matching.
    """

    def __init__(
        self,
        df_census: pd.DataFrame,
        df_gss: pd.DataFrame,
        dday_col: str = "DDAY",
        id_col: str = "occID",
        cols_match_t1: List[str] | None = None,
    ):
        print(f"\n{'=' * 60}")
        print("  INITIALIZING PHASE 2: MATCH PROFILER")
        print(f"{'=' * 60}")

        self.df_census = df_census.copy()
        self.df_gss = df_gss.copy()
        self.id_col = id_col
        self.dday_col = dday_col
        self.cols_t1 = cols_match_t1 or DEFAULT_TIER_1
        self.cols_t2 = DEFAULT_TIER_2
        self.cols_t3 = DEFAULT_TIER_3
        self.cols_t4 = DEFAULT_TIER_4

        for frame in (self.df_census, self.df_gss):
            for col in set(self.cols_t1 + self.cols_t2 + self.cols_t3 + self.cols_t4 + [self.dday_col]):
                if col in frame.columns:
                    frame[col] = pd.to_numeric(frame[col], errors="coerce")

        print(f"   Splitting GSS by Day Type ({dday_col})...")
        available_t1 = [c for c in self.cols_t1 if c in self.df_gss.columns]
        missing_t1 = sorted(list(set(self.cols_t1) - set(available_t1)))
        if missing_t1:
            print("   Warning: Missing Tier 1 columns in GSS:")
            print(f"     {missing_t1}")

        catalog_cols = list(dict.fromkeys([self.id_col, self.dday_col, "HHSIZE"] + available_t1))
        dday_vals = self.df_gss[self.dday_col]

        raw_wd = self.df_gss[dday_vals.isin([2, 3, 4, 5, 6])]
        raw_we = self.df_gss[dday_vals.isin([1, 7])]

        self.catalog_wd = raw_wd[catalog_cols].drop_duplicates(subset=[self.id_col]).copy()
        self.catalog_we = raw_we[catalog_cols].drop_duplicates(subset=[self.id_col]).copy()

        print("   Catalogs Created:")
        print(f"     Weekday: {len(self.catalog_wd):,} unique profiles")
        print(f"     Weekend: {len(self.catalog_we):,} unique profiles")

    def run_matching(self) -> pd.DataFrame:
        print("\n  Starting Matching Loop...")
        results = []

        for idx, agent in tqdm(self.df_census.iterrows(), total=len(self.df_census), desc="Matching"):
            wd_id, wd_tier = self._find_best_match(agent, self.catalog_wd)
            we_id, we_tier = self._find_best_match(agent, self.catalog_we)

            row = agent.to_dict()
            row["MATCH_ID_WD"] = wd_id
            row["MATCH_TIER_WD"] = wd_tier
            row["MATCH_ID_WE"] = we_id
            row["MATCH_TIER_WE"] = we_tier
            results.append(row)

        df_result = pd.DataFrame(results)
        self._print_match_stats(df_result)
        return df_result

    def _find_best_match(self, agent: pd.Series, catalog: pd.DataFrame) -> Tuple[object, str]:
        if catalog.empty:
            return pd.NA, "0_EmptyCatalog"

        for tier_cols, tier_name in [
            (self.cols_t1, "1_Perfect"),
            (self.cols_t2, "2_Core"),
            (self.cols_t3, "3_Constraints"),
            (self.cols_t4, "4_FailSafe"),
        ]:
            mask = np.ones(len(catalog), dtype=bool)
            for col in tier_cols:
                if col in catalog.columns and col in agent.index:
                    agent_val = pd.to_numeric(pd.Series([agent[col]]), errors="coerce").iloc[0]
                    if pd.isna(agent_val):
                        mask &= False
                    else:
                        mask &= catalog[col] == agent_val
            matches = catalog[mask]
            if not matches.empty:
                return matches.sample(1, random_state=42)[self.id_col].values[0], tier_name

        return catalog.sample(1, random_state=42)[self.id_col].values[0], "5_Random"

    def _print_match_stats(self, df_matched: pd.DataFrame) -> None:
        print(f"\n{'=' * 60}")
        print("  MATCHING STATISTICS")
        print(f"{'=' * 60}")

        for day_type, col in [("Weekday", "MATCH_TIER_WD"), ("Weekend", "MATCH_TIER_WE")]:
            print(f"\n  {day_type}:")
            tier_counts = df_matched[col].value_counts(dropna=False).sort_index()
            total = len(df_matched)
            for tier, count in tier_counts.items():
                pct = (count / total * 100) if total else 0
                print(f"    {tier}: {count:,} ({pct:.1f}%)")


# =============================================================================
# SCHEDULE EXPANDER
# =============================================================================

class ScheduleExpander:
    """
    Retrieve all episode rows for a matched `occID`.
    """

    def __init__(self, df_gss_raw: pd.DataFrame, id_col: str = "occID"):
        print(f"\n{'=' * 60}")
        print("  INITIALIZING PHASE 4: SCHEDULE EXPANDER")
        print(f"{'=' * 60}")

        self.df_gss_raw = df_gss_raw.copy()
        self.id_col = id_col

        print("   Indexing GSS Episodes for fast retrieval...")
        self.gss_indexed = self.df_gss_raw.set_index(self.id_col).sort_index()
        episode_counts = self.df_gss_raw.groupby(self.id_col).size()
        print(f"   Indexed {len(episode_counts):,} unique IDs")
        print(
            f"   Episodes per ID: min={episode_counts.min()}, max={episode_counts.max()}, "
            f"mean={episode_counts.mean():.1f}"
        )

    def get_episodes(self, matched_id) -> pd.DataFrame | None:
        try:
            return self.gss_indexed.loc[[matched_id]].copy()
        except KeyError:
            return None


# =============================================================================
# HELPERS
# =============================================================================

def verify_sample(df_matched: pd.DataFrame, expander: ScheduleExpander, n: int = 5) -> None:
    print(f"\n  VERIFYING EXPANSION (Sample of {n})")
    print("-" * 50)

    for i, agent in df_matched.head(n).iterrows():
        ep_wd = expander.get_episodes(agent["MATCH_ID_WD"])
        ep_we = expander.get_episodes(agent["MATCH_ID_WE"])
        count_wd = len(ep_wd) if ep_wd is not None else 0
        count_we = len(ep_we) if ep_we is not None else 0
        print(f"   Agent {i}: Weekday={count_wd} episodes | Weekend={count_we} episodes")


def generate_full_expansion(
    df_matched: pd.DataFrame,
    expander: ScheduleExpander,
    output_path: Path,
    census_id_col: str = "PP_ID",
) -> None:
    print(f"\n  Expanding Schedules for {len(df_matched):,} agents...")
    all_episodes = []

    carry_vars = [
        "HHSIZE",
        "AGEGRP",
        "SEX",
        "MARSTH",
        "PR",
        "LFTAG",
        "KOL",
        "CMA",
        "DTYPE",
        "BEDRM",
        "ROOM",
        "CONDO",
        "REPAIR",
        "CFSIZE",
        "CF_RP",
        "TOTINC",
        "Alone",
        "Spouse",
        "Children",
        "otherInFAMs",
        "parents",
        "Friends",
        "otherHHs",
        "Others",
        "colleagues",
        "techUse",
        "wellbeing",
    ]

    for idx, agent in tqdm(df_matched.iterrows(), total=len(df_matched), desc="Expanding"):
        census_id = agent.get(census_id_col, idx)
        hh_id = agent.get("SIM_HH_ID", idx)

        for day_type, match_col in [("Weekday", "MATCH_ID_WD"), ("Weekend", "MATCH_ID_WE")]:
            episodes = expander.get_episodes(agent[match_col])
            if episodes is None:
                continue

            episodes = episodes.copy()
            episodes["Census_ID"] = census_id
            episodes["SIM_HH_ID"] = hh_id
            episodes["Day_Type"] = day_type
            episodes["AgentID"] = idx

            for var in carry_vars:
                if var in agent.index:
                    episodes[f"Census_{var}"] = agent[var]

            all_episodes.append(episodes)

    if all_episodes:
        full_df = pd.concat(all_episodes, ignore_index=True)
        full_df = full_df.sort_values(by=["Census_ID", "Day_Type", "AgentID"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        full_df.to_csv(output_path, index=False)
        print(f"   Saved Expanded File: {len(full_df):,} rows to {output_path.name}")
    else:
        print("   Warning: No episodes were expanded!")


def validate_matching_quality(
    df_matched: pd.DataFrame,
    expander: ScheduleExpander,
    save_path: Path | None = None,
) -> None:
    report_buffer = []

    def log(message: str) -> None:
        print(message)
        report_buffer.append(message)

    log(f"\n{'=' * 60}")
    log("  VALIDATION REPORT: PROFILE MATCHING QUALITY")
    log(f"{'=' * 60}")

    log("\n1. MATCH QUALITY (TIER DISTRIBUTION)")
    log("-" * 40)
    for day_type in ["WD", "WE"]:
        col = f"MATCH_TIER_{day_type}"
        if col in df_matched.columns:
            counts = df_matched[col].value_counts(normalize=True) * 100
            log(f"\n   [{day_type} Matching Tiers]")
            for tier, pct in sorted(counts.items()):
                log(f"      - {tier}: {pct:.1f}%")

    log("\n2. EPISODE COUNT SANITY CHECK")
    log("-" * 40)
    sample_for_check = df_matched.head(100)
    wd_counts = []
    we_counts = []
    for _, agent in sample_for_check.iterrows():
        ep_wd = expander.get_episodes(agent["MATCH_ID_WD"])
        ep_we = expander.get_episodes(agent["MATCH_ID_WE"])
        if ep_wd is not None:
            wd_counts.append(len(ep_wd))
        if ep_we is not None:
            we_counts.append(len(ep_we))
    if wd_counts:
        log(f"   Weekday Episodes: min={min(wd_counts)}, max={max(wd_counts)}, avg={np.mean(wd_counts):.1f}")
    if we_counts:
        log(f"   Weekend Episodes: min={min(we_counts)}, max={max(we_counts)}, avg={np.mean(we_counts):.1f}")

    log(f"\n{'=' * 60}")

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text("\n".join(report_buffer), encoding="utf-8")
        print(f"\n   Validation Report saved to: {save_path.name}")


def sample_data(
    df_census: pd.DataFrame,
    df_gss: pd.DataFrame,
    sample_pct: float = 100.0,
    id_col: str = "occID",
    hh_col: str = "SIM_HH_ID",
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if sample_pct >= 100.0:
        print("   Using full dataset (no sampling)")
        return df_census, df_gss

    print(f"\n   Sampling {sample_pct}% of data (household-based)...")
    np.random.seed(random_state)

    unique_hh = df_census[hh_col].dropna().unique()
    n_hh = max(1, int(len(unique_hh) * sample_pct / 100))
    sampled_hh = np.random.choice(unique_hh, size=n_hh, replace=False)
    df_census_sampled = df_census[df_census[hh_col].isin(sampled_hh)]
    print(
        f"   Census: {len(df_census):,} -> {len(df_census_sampled):,} persons "
        f"({len(unique_hh):,} -> {len(sampled_hh):,} households)"
    )

    unique_ids = df_gss[id_col].dropna().unique()
    n_ids = max(1, int(len(unique_ids) * sample_pct / 100))
    sampled_ids = np.random.choice(unique_ids, size=n_ids, replace=False)
    df_gss_sampled = df_gss[df_gss[id_col].isin(sampled_ids)]
    print(
        f"   GSS: {len(df_gss):,} -> {len(df_gss_sampled):,} rows "
        f"({len(unique_ids):,} -> {len(sampled_ids):,} occupants)"
    )

    return df_census_sampled, df_gss_sampled


# =============================================================================
# MAIN
# =============================================================================

def main(sample_pct: float = DEFAULT_SAMPLE_PCT) -> None:
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR

    aligned_dir = BASE_DIR / "Outputs_21CEN22GSS" / "alignment"
    output_dir = BASE_DIR / "Outputs_21CEN22GSS" / "ProfileMatching"
    output_dir.mkdir(parents=True, exist_ok=True)

    aligned_census = aligned_dir / "Aligned_Census_2022.csv"
    aligned_gss = aligned_dir / "Aligned_GSS_2022.csv"

    print("=" * 60)
    print("  21CEN22GSS PROFILE MATCHING")
    print("=" * 60)

    print("\n1. Loading Data...")
    df_census = pd.read_csv(aligned_census, low_memory=False)
    df_gss = pd.read_csv(aligned_gss, low_memory=False)
    print(f"   Census: {len(df_census):,} rows")
    print(f"   GSS: {len(df_gss):,} rows ({df_gss['occID'].nunique():,} unique occupants)")

    df_census, df_gss = sample_data(df_census, df_gss, sample_pct=sample_pct)

    matcher = MatchProfiler(df_census, df_gss, dday_col="DDAY", id_col="occID")
    df_matched = matcher.run_matching()

    suffix = f"_sample{int(sample_pct)}pct" if sample_pct < 100 else ""
    matched_keys_path = output_dir / f"21CEN22GSS_Matched_Keys{suffix}.csv"
    df_matched.to_csv(matched_keys_path, index=False)
    print(f"\n   Saved Keys: {matched_keys_path.name}")

    expander = ScheduleExpander(df_gss, id_col="occID")
    verify_sample(df_matched, expander)

    expanded_path = output_dir / f"21CEN22GSS_Full_Schedules{suffix}.csv"
    generate_full_expansion(df_matched, expander, expanded_path)

    validation_path = output_dir / f"21CEN22GSS_Validation{suffix}.txt"
    validate_matching_quality(df_matched, expander, save_path=validation_path)

    print("\n" + "=" * 60)
    print("  WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Profile Matching: Census 2021 + GSS 2022")
    parser.add_argument(
        "--sample",
        type=float,
        default=DEFAULT_SAMPLE_PCT,
        help="Percentage of data to sample (1-100). Default: 10"
    )
    args = parser.parse_args()

    main(sample_pct=args.sample)
