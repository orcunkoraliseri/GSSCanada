"""
06CEN05GSS Profile Matcher Module

Matches Census 2006 agents with GSS 2005 schedules based on demographic profiles.
Uses tiered matching to find optimal schedule assignments, then expands schedules
for simulation.

Pipeline:
1. Load aligned Census and GSS data
2. Match profiles using MatchProfiler (tiered matching)
3. Save matched keys as lightweight CSV
4. Expand full schedules using ScheduleExpander
"""

import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
from tqdm import tqdm


# =============================================================================
# CLASS 1: MatchProfiler (The Linker)
# =============================================================================

class MatchProfiler:
    """
    Assigns GSS Schedule IDs to Census Agents using tiered matching.
    Matches based on demographic variables that exist in both datasets.
    
    Matching Tiers:
        Tier 1: Perfect Match (all columns)
        Tier 2: Core Demographics (HHSIZE, AGEGRP, SEX, MARSTH, LFTAG)
        Tier 3: Key Constraints (HHSIZE, AGEGRP)
        Tier 4: Fail-safe (HHSIZE only)
        Tier 5: Random fallback
    """

    def __init__(
        self,
        df_census: pd.DataFrame,
        df_gss: pd.DataFrame,
        dday_col: str = "DDAY",
        id_col: str = "occID",
        cols_match_t1: list = None
    ):
        """
        Initialize the MatchProfiler.
        
        Args:
            df_census: Aligned Census DataFrame.
            df_gss: Aligned GSS DataFrame with episode data.
            dday_col: Column name for day type in GSS.
            id_col: Column name for unique ID in GSS.
            cols_match_t1: Custom columns for Tier 1 matching.
        """
        print(f"\n{'=' * 60}")
        print(f"  INITIALIZING PHASE 2: MATCH PROFILER")
        print(f"{'=' * 60}")

        self.df_census = df_census.copy()
        self.id_col = id_col
        self.dday_col = dday_col

        # --- MATCHING TIERS (Based on aligned columns) ---
        # Tier 1: All available matched columns
        if cols_match_t1 is None:
            self.cols_t1 = [
                "HHSIZE", "AGEGRP", "MARSTH", "SEX",
                "KOL", "NOCS", "PR", "LFTAG", "TOTINC",
                "CMA", "ATTSCH"
            ]
        else:
            self.cols_t1 = cols_match_t1

        # Tier 2: Core Demographics
        self.cols_t2 = [
            "HHSIZE", "AGEGRP", "SEX", "MARSTH", "LFTAG", "PR"
        ]

        # Tier 3: Key Constraints
        self.cols_t3 = ["HHSIZE", "AGEGRP", "SEX"]

        # Tier 4: Fail-safe
        self.cols_t4 = ["HHSIZE"]

        # Split & Flatten GSS to create "Catalogs"
        print(f"   Splitting GSS by Day Type ({dday_col})...")

        # Only include columns that actually exist in GSS
        available_t1 = [c for c in self.cols_t1 if c in df_gss.columns]
        missing_t1 = list(set(self.cols_t1) - set(available_t1))

        if missing_t1:
            print(f"   Warning: The following columns are MISSING in GSS:")
            print(f"     {missing_t1}")

        # Catalog columns must include all available match columns
        catalog_cols = list(set([self.id_col] + available_t1 + ["HHSIZE"]))

        # Weekday Catalog (DDAY: 2-6 for Mon-Fri)
        raw_wd = df_gss[df_gss[self.dday_col].isin([2, 3, 4, 5, 6])]
        self.catalog_wd = raw_wd[catalog_cols].drop_duplicates(subset=[self.id_col])

        # Weekend Catalog (DDAY: 1=Sunday, 7=Saturday)
        raw_we = df_gss[df_gss[self.dday_col].isin([1, 7])]
        self.catalog_we = raw_we[catalog_cols].drop_duplicates(subset=[self.id_col])

        print(f"   Catalogs Created:")
        print(f"     Weekday: {len(self.catalog_wd):,} unique profiles")
        print(f"     Weekend: {len(self.catalog_we):,} unique profiles")

    def run_matching(self) -> pd.DataFrame:
        """
        Run matching for all Census agents.
        
        Returns:
            DataFrame with matched IDs and tier info for each agent.
        """
        print(f"\n  Starting Matching Loop...")
        results = []
        
        for idx, agent in tqdm(
            self.df_census.iterrows(),
            total=len(self.df_census),
            desc="Matching"
        ):
            # Find Weekday Match
            wd_id, wd_tier = self._find_best_match(agent, self.catalog_wd)
            # Find Weekend Match
            we_id, we_tier = self._find_best_match(agent, self.catalog_we)

            row = agent.to_dict()
            row['MATCH_ID_WD'] = wd_id
            row['MATCH_TIER_WD'] = wd_tier
            row['MATCH_ID_WE'] = we_id
            row['MATCH_TIER_WE'] = we_tier
            results.append(row)

        df_result = pd.DataFrame(results)
        
        # Print matching statistics
        self._print_match_stats(df_result)
        
        return df_result

    def _find_best_match(
        self,
        agent: pd.Series,
        catalog: pd.DataFrame
    ) -> tuple:
        """
        Find the best matching GSS profile for a Census agent.
        
        Args:
            agent: Single Census agent row.
            catalog: GSS catalog (weekday or weekend).
            
        Returns:
            Tuple of (matched_id, tier_name)
        """
        # Tier 1: Perfect Match
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t1:
            if col in catalog.columns and col in agent.index:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty:
            return matches.sample(1)[self.id_col].values[0], "1_Perfect"

        # Tier 2: Core Demographics
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t2:
            if col in catalog.columns and col in agent.index:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty:
            return matches.sample(1)[self.id_col].values[0], "2_Core"

        # Tier 3: Key Constraints
        mask = np.ones(len(catalog), dtype=bool)
        for col in self.cols_t3:
            if col in catalog.columns and col in agent.index:
                mask &= (catalog[col] == agent[col])
        matches = catalog[mask]
        if not matches.empty:
            return matches.sample(1)[self.id_col].values[0], "3_Constraints"

        # Tier 4: Fail-safe (HHSIZE only)
        mask = (catalog["HHSIZE"] == agent["HHSIZE"])
        matches = catalog[mask]
        if not matches.empty:
            return matches.sample(1)[self.id_col].values[0], "4_FailSafe"

        # Tier 5: Random fallback
        return catalog.sample(1)[self.id_col].values[0], "5_Random"

    def _print_match_stats(self, df_matched: pd.DataFrame) -> None:
        """Print matching tier statistics."""
        print(f"\n{'=' * 60}")
        print(f"  MATCHING STATISTICS")
        print(f"{'=' * 60}")
        
        for day_type, col in [("Weekday", "MATCH_TIER_WD"), ("Weekend", "MATCH_TIER_WE")]:
            print(f"\n  {day_type}:")
            tier_counts = df_matched[col].value_counts().sort_index()
            total = len(df_matched)
            for tier, count in tier_counts.items():
                pct = count / total * 100
                print(f"    {tier}: {count:,} ({pct:.1f}%)")


# =============================================================================
# CLASS 2: ScheduleExpander (The Retriever)
# =============================================================================

class ScheduleExpander:
    """
    Retrieves and expands schedules for matched Census agents.
    Takes matched Census DataFrame and raw GSS DataFrame to retrieve
    original variable-length episode lists.
    """

    def __init__(self, df_gss_raw: pd.DataFrame, id_col: str = "occID"):
        """
        Initialize the ScheduleExpander.
        
        Args:
            df_gss_raw: Raw GSS DataFrame with all episodes.
            id_col: Column name for unique ID.
        """
        print(f"\n{'=' * 60}")
        print(f"  INITIALIZING PHASE 4: SCHEDULE EXPANDER")
        print(f"{'=' * 60}")

        self.df_gss_raw = df_gss_raw
        self.id_col = id_col

        # Index GSS by occID for instant retrieval
        print("   Indexing GSS Episodes for fast retrieval...")
        self.gss_indexed = self.df_gss_raw.set_index(self.id_col).sort_index()
        
        # Count episodes per ID
        episode_counts = self.df_gss_raw.groupby(self.id_col).size()
        print(f"   Indexed {len(episode_counts):,} unique IDs")
        print(f"   Episodes per ID: min={episode_counts.min()}, max={episode_counts.max()}, "
              f"mean={episode_counts.mean():.1f}")

    def get_episodes(self, matched_id) -> pd.DataFrame:
        """
        Retrieve episodes for a specific Schedule ID.
        
        Args:
            matched_id: The occID to retrieve episodes for.
            
        Returns:
            DataFrame of episodes, or None if not found.
        """
        try:
            return self.gss_indexed.loc[[matched_id]].copy()
        except KeyError:
            return None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def verify_sample(
    df_matched: pd.DataFrame,
    expander: ScheduleExpander,
    n: int = 5
) -> None:
    """
    Verify expansion by sampling a few agents.
    
    Args:
        df_matched: Matched Census DataFrame.
        expander: ScheduleExpander instance.
        n: Number of samples to verify.
    """
    print(f"\n  VERIFYING EXPANSION (Sample of {n})")
    print("-" * 50)
    
    for i, agent in df_matched.head(n).iterrows():
        id_wd = agent['MATCH_ID_WD']
        id_we = agent['MATCH_ID_WE']
        ep_wd = expander.get_episodes(id_wd)
        ep_we = expander.get_episodes(id_we)
        count_wd = len(ep_wd) if ep_wd is not None else 0
        count_we = len(ep_we) if ep_we is not None else 0
        print(f"   Agent {i}: Weekday={count_wd} episodes | Weekend={count_we} episodes")


def generate_full_expansion(
    df_matched: pd.DataFrame,
    expander: ScheduleExpander,
    output_path: Path,
    census_id_col: str = "PP_ID"
) -> None:
    """
    Expand and save full schedules for all matched agents.
    
    Args:
        df_matched: Matched Census DataFrame.
        expander: ScheduleExpander instance.
        output_path: Path to save expanded schedules.
        census_id_col: Column to use as Census agent identifier.
    """
    print(f"\n  Expanding Schedules for {len(df_matched):,} agents...")
    all_episodes = []

    # Variables to carry over from Census (including SIM_HH_ID for HH aggregation)
    # Demographics + Residential variables for BEM
    carry_vars = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "PR", "TOTINC", 
                  "KOL", "NOCS", "LFTAG", "CMA", "ATTSCH",
                  "DTYPE", "BEDRM", "ROOM", "CONDO", "REPAIR"]  # Residential for BEM


    for idx, agent in tqdm(
        df_matched.iterrows(),
        total=len(df_matched),
        desc="Expanding"
    ):
        # Get Census ID (use PP_ID or index)
        census_id = agent.get(census_id_col, idx)
        # Get Household ID for aggregation
        hh_id = agent.get('SIM_HH_ID', idx)

        # Expand Weekday
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])
        if ep_wd is not None:
            ep_wd = ep_wd.copy()
            ep_wd['Census_ID'] = census_id
            ep_wd['SIM_HH_ID'] = hh_id
            ep_wd['Day_Type'] = 'Weekday'
            ep_wd['AgentID'] = idx

            # Carry over Census variables
            for var in carry_vars:
                if var in agent.index:
                    ep_wd[f'Census_{var}'] = agent[var]

            all_episodes.append(ep_wd)

        # Expand Weekend
        ep_we = expander.get_episodes(agent['MATCH_ID_WE'])
        if ep_we is not None:
            ep_we = ep_we.copy()
            ep_we['Census_ID'] = census_id
            ep_we['SIM_HH_ID'] = hh_id
            ep_we['Day_Type'] = 'Weekend'
            ep_we['AgentID'] = idx

            # Carry over Census variables
            for var in carry_vars:
                if var in agent.index:
                    ep_we[f'Census_{var}'] = agent[var]

            all_episodes.append(ep_we)

    if all_episodes:
        full_df = pd.concat(all_episodes, ignore_index=True)
        print(f"   Sorting expanded data...")
        full_df = full_df.sort_values(by=['Census_ID', 'Day_Type', 'AgentID'])
        full_df.to_csv(output_path, index=False)
        print(f"   Saved Expanded File: {len(full_df):,} rows to {output_path.name}")
    else:
        print("   Warning: No episodes were expanded!")


# =============================================================================
# VALIDATION FUNCTION
# =============================================================================

def validate_matching_quality(
    df_matched: pd.DataFrame,
    expander: ScheduleExpander,
    save_path: Path = None
) -> None:
    """
    Validates profile matching quality by analyzing tier distribution
    and behavioral consistency.
    
    Args:
        df_matched: DataFrame with matched Census-GSS keys.
        expander: ScheduleExpander instance for episode retrieval.
        save_path: Optional path to save validation report.
    """
    # Buffer to capture output
    report_buffer = []

    def log(message: str) -> None:
        """Print and append to buffer."""
        print(message)
        report_buffer.append(message)

    log(f"\n{'=' * 60}")
    log(f"  VALIDATION REPORT: PROFILE MATCHING QUALITY")
    log(f"{'=' * 60}")

    # --- METHOD 1: TIER DISTRIBUTION ---
    log(f"\n1. MATCH QUALITY (TIER DISTRIBUTION)")
    log("-" * 40)

    for day_type in ['WD', 'WE']:
        col = f'MATCH_TIER_{day_type}'
        if col in df_matched.columns:
            counts = df_matched[col].value_counts(normalize=True) * 100
            log(f"\n   [{day_type} Matching Tiers]")
            for tier, pct in sorted(counts.items()):
                log(f"      - {tier}: {pct:.1f}%")

    # --- METHOD 2: BEHAVIORAL CONSISTENCY (Workers) ---
    log(f"\n2. BEHAVIORAL CONSISTENCY (Workers vs. Non-Workers)")
    log("-" * 40)

    # Filter for Employed (LFTAG 1 or 2 = Employed full-time/part-time)
    # Note: For 2005 GSS, we use LFTAG instead of COW
    sample_size = min(500, len(df_matched))
    
    if 'LFTAG' in df_matched.columns:
        workers = df_matched[df_matched['LFTAG'].isin([1, 2])]
        if len(workers) > sample_size:
            workers = workers.sample(sample_size, random_state=42)
        worker_label = "LFTAG 1-2 (Employed)"
    else:
        # Fallback: random sample
        workers = df_matched.sample(min(sample_size, len(df_matched)), random_state=42)
        worker_label = "Random Sample"

    log(f"\n   Analyzing {len(workers)} workers ({worker_label})...")
    
    work_minutes = []

    for _, agent in workers.iterrows():
        # Get Weekday episodes
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])

        if ep_wd is not None and 'occACT' in ep_wd.columns:
            # Filter for Work Activities
            # GSS Work Codes typically start with '1', '0', or '8'
            work_acts = ep_wd[ep_wd['occACT'].astype(str).str.startswith(('1', '0', '8'))]

            total_duration = 0
            for _, row in work_acts.iterrows():
                s = row.get('start', 0)
                e = row.get('end', 0)

                # Fix for midnight wrap
                if e < s:
                    duration = (e + 1440) - s
                else:
                    duration = e - s

                total_duration += duration

            work_minutes.append(total_duration)

    avg_work = np.mean(work_minutes) if work_minutes else 0
    log(f"\n   Average Work Duration for 'Employees': {avg_work:.0f} minutes/day")
    log(f"   (Based on {len(work_minutes)} workers with valid schedules)")

    if avg_work < 60:
        log("      WARNING: Low work duration. Check 'occACT' filter codes.")
    elif avg_work > 300:
        log("      SUCCESS: Employees performing ~5-8 hours of work.")
    else:
        log("      NOTE: Work duration moderate. May reflect part-time mix.")

    # --- METHOD 3: EPISODE COUNT SANITY CHECK ---
    log(f"\n3. EPISODE COUNT SANITY CHECK")
    log("-" * 40)
    
    sample_for_check = df_matched.head(100)
    wd_counts = []
    we_counts = []
    
    for _, agent in sample_for_check.iterrows():
        ep_wd = expander.get_episodes(agent['MATCH_ID_WD'])
        ep_we = expander.get_episodes(agent['MATCH_ID_WE'])
        if ep_wd is not None:
            wd_counts.append(len(ep_wd))
        if ep_we is not None:
            we_counts.append(len(ep_we))
    
    if wd_counts:
        log(f"   Weekday Episodes: min={min(wd_counts)}, max={max(wd_counts)}, avg={np.mean(wd_counts):.1f}")
    if we_counts:
        log(f"   Weekend Episodes: min={min(we_counts)}, max={max(we_counts)}, avg={np.mean(we_counts):.1f}")

    log(f"\n{'=' * 60}")

    # Save to file
    if save_path:
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(report_buffer))
            print(f"\n   Validation Report saved to: {save_path.name}")
        except Exception as e:
            print(f"\n   Error saving report: {e}")



# SAMPLING FUNCTIONS
# =============================================================================

def sample_data(
    df_census: pd.DataFrame,
    df_gss: pd.DataFrame,
    sample_pct: float = 100.0,
    id_col: str = "occID",
    hh_col: str = "SIM_HH_ID",
    random_state: int = 42
) -> tuple:
    """
    Sample Census and GSS data by percentage, preserving household integrity.
    
    Census: Sample by unique household ID (keeps all members of selected households).
    GSS: Sample by unique occID (keeps all episodes for sampled occupants).
    
    Args:
        df_census: Full Census DataFrame.
        df_gss: Full GSS DataFrame (temporal with multiple rows per occID).
        sample_pct: Percentage of data to sample (1-100).
        id_col: Column for unique occupant ID in GSS.
        hh_col: Column for household ID in Census (default: SIM_HH_ID).
        random_state: Random seed for reproducibility.
        
    Returns:
        Tuple of (sampled_census, sampled_gss)
    """
    if sample_pct >= 100.0:
        print("   Using full dataset (no sampling)")
        return df_census, df_gss
    
    print(f"\n   Sampling {sample_pct}% of data (household-based)...")
    np.random.seed(random_state)
    
    # Sample Census by HOUSEHOLD (keeps all members together)
    unique_hh = df_census[hh_col].unique()
    n_hh = int(len(unique_hh) * sample_pct / 100)
    sampled_hh = np.random.choice(unique_hh, size=n_hh, replace=False)
    df_census_sampled = df_census[df_census[hh_col].isin(sampled_hh)]
    print(f"   Census: {len(df_census):,} -> {len(df_census_sampled):,} persons "
          f"({len(unique_hh):,} -> {len(sampled_hh):,} households)")
    
    # Sample GSS (by unique occID, keeping all episodes per occupant)
    unique_ids = df_gss[id_col].unique()
    n_ids = int(len(unique_ids) * sample_pct / 100)
    sampled_ids = np.random.choice(unique_ids, size=n_ids, replace=False)
    df_gss_sampled = df_gss[df_gss[id_col].isin(sampled_ids)]
    print(f"   GSS: {len(df_gss):,} -> {len(df_gss_sampled):,} rows "
          f"({len(unique_ids):,} -> {len(sampled_ids):,} occupants)")
    
    return df_census_sampled, df_gss_sampled


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main(sample_pct: float = 100.0) -> None:
    """
    Entry point for profile matching.
    
    Args:
        sample_pct: Percentage of data to sample (1-100). Default 100 = full data.
    """
    # --- 1. Define Paths ---
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy")
    
    ALIGNED_DIR = BASE_DIR / "Outputs_06CEN05GSS" / "alignment"
    OUTPUT_DIR = BASE_DIR / "Outputs_06CEN05GSS" / "ProfileMatching"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    aligned_census = ALIGNED_DIR / "Aligned_Census_2005.csv"
    aligned_gss = ALIGNED_DIR / "Aligned_GSS_2005.csv"
    
    print("=" * 60)
    print("  06CEN05GSS PROFILE MATCHING")
    print("=" * 60)
    
    # --- 2. Load Data ---
    print("\n1. Loading Data...")
    df_census = pd.read_csv(aligned_census)
    df_gss = pd.read_csv(aligned_gss, low_memory=False)
    print(f"   Census: {len(df_census):,} rows")
    print(f"   GSS: {len(df_gss):,} rows ({df_gss['occID'].nunique():,} unique occupants)")
    
    # --- 2b. Optional Sampling ---
    df_census, df_gss = sample_data(df_census, df_gss, sample_pct=sample_pct)
    
    # --- 3. Run Matching ---
    matcher = MatchProfiler(df_census, df_gss, dday_col="DDAY", id_col="occID")
    df_matched = matcher.run_matching()
    
    # --- 4. Save Matched Keys (Lightweight) ---
    # Include sample percentage in filename if sampling
    suffix = f"_sample{int(sample_pct)}pct" if sample_pct < 100 else ""
    matched_keys_path = OUTPUT_DIR / f"06CEN05GSS_Matched_Keys{suffix}.csv"
    df_matched.to_csv(matched_keys_path, index=False)
    print(f"\n   Saved Keys: {matched_keys_path.name}")
    
    # --- 5. Expand & Verify ---
    expander = ScheduleExpander(df_gss, id_col="occID")
    verify_sample(df_matched, expander)
    
    # --- 6. Generate Full Expansion ---
    expanded_path = OUTPUT_DIR / f"06CEN05GSS_Full_Schedules{suffix}.csv"
    generate_full_expansion(df_matched, expander, expanded_path)
    
    # --- 7. Validate Matching Quality ---
    print("\n--- Step 7: Running Validation ---")
    validation_path = OUTPUT_DIR / f"06CEN05GSS_Validation{suffix}.txt"
    validate_matching_quality(df_matched, expander, save_path=validation_path)
    
    print("\n" + "=" * 60)
    print("  WORKFLOW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile Matching: Census 2006 to GSS 2005")
    parser.add_argument(
        "--sample",
        type=float,
        default=25,
        help="Percentage of data to sample (1-100). Default: 100 (full data)"
    )
    args = parser.parse_args()
    
    main(sample_pct=args.sample)

