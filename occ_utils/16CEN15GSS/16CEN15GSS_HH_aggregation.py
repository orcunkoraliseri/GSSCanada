"""
16CEN15GSS Household Aggregation Module

Transforms individual episode lists into aggregated Household Profiles.
Converts variable-length time schedules into fixed 5-minute resolution grids
and aggregates presence, density, and activity at household level.

Pipeline:
1. Load expanded schedules from DTYPE_expansion (refined DTYPE)
2. Create individual 5-minute grids for each person
3. Aggregate to household level (presence, density, activities)
4. Save full integrated data

Resolution: 5 Minutes (288 slots per 24 hours)
"""

import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
from typing import List, Optional
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs): return iterable


# =============================================================================
# CLASS: HouseholdAggregator
# =============================================================================

class HouseholdAggregator:
    """
    Transforms individual episode lists into aggregated Household Profiles.
    Resolution: 5 Minutes (288 slots per 24 hours).

    Steps:
        A: Grid Construction (Individual) - Convert episodes to time slots
        B: Binary Presence (Household) -> 'occPre'
        C: Social Density (Household) -> 'occDensity'
        D: Activity Sets (Household) -> 'occActivity'
    """

    def __init__(self, resolution_min: int = 5):
        """
        Initialize the HouseholdAggregator.
        
        Args:
            resolution_min: Time resolution in minutes (default: 5).
        """
        self.res = resolution_min
        self.slots = int(1440 / self.res)  # 288 slots for 24h

        # Social columns to sum for Step C (excluding 'Alone')
        self.social_cols = [
            'Spouse', 'Children', 'parents', 'Friends',
            'otherHHs', 'Others', 'otherInFAMs'
        ]

    def process_all(self, df_expanded: pd.DataFrame) -> pd.DataFrame:
        """
        Main driver function.
        
        Groups data by Household and Day Type, aggregates,
        and then merges aggregation back to individual grids.
        Includes ALL static columns from the input CSV.
        
        Args:
            df_expanded: Expanded schedules DataFrame from DTYPE_expansion.
            
        Returns:
            DataFrame with aggregated household profiles.
        """
        print(f"   Grouping data by Household and Day Type...")

        # Columns that change per episode and shouldn't be broadcasted statically
        time_varying_cols = [
            'start', 'end', 'EPINO', 'occACT', 'occPRE', 'social_sum',
            'Spouse', 'Children', 'parents', 'Friends',
            'otherHHs', 'Others', 'otherInFAMs'
        ]

        # Group by Household AND Day
        groups = df_expanded.groupby(['SIM_HH_ID', 'Day_Type'])

        full_data_results = []

        # Iterate through each household scenario
        for (hh_id, day_type), group_df in tqdm(groups, desc="Processing Households"):

            # 1. Map AgentID -> Grid DataFrame
            people_grids_map = {}
            # 2. Map AgentID -> Static Metadata (Series)
            people_meta_map = {}

            # Group by 'AgentID' (Unique Index) instead of 'occID'
            if 'AgentID' not in group_df.columns:
                raise ValueError(
                    "Error: 'AgentID' column missing. "
                    "Please re-run ProfileMatcher with the updated script."
                )

            for agent_id, person_data in group_df.groupby('AgentID'):
                # Step A: Create 5-min grid for this person
                grid = self._create_individual_grid(person_data)
                people_grids_map[agent_id] = grid

                # Capture Static Metadata (Take 1st row, drop time-varying)
                meta = person_data.iloc[0].drop(labels=time_varying_cols, errors='ignore')
                people_meta_map[agent_id] = meta

            # 3. Steps B, C, D: Aggregate the household
            hh_profile = self._aggregate_household(list(people_grids_map.values()))

            # 4. INTEGRATION: Merge Household Data + Individual Grid + Static Metadata
            for agent_id, p_grid in people_grids_map.items():
                # a. Concatenate Household Profile + Individual Grid
                combined = pd.concat([hh_profile, p_grid], axis=1)

                # b. Add Static Metadata
                meta = people_meta_map[agent_id]
                for col_name, val in meta.items():
                    combined[col_name] = val

                # Ensure essential keys are correct
                combined['SIM_HH_ID'] = hh_id
                combined['Day_Type'] = day_type
                combined['AgentID'] = agent_id

                full_data_results.append(combined)

        # Combine all individuals into one big dataframe
        return pd.concat(full_data_results, ignore_index=True)

    def _create_individual_grid(self, episodes: pd.DataFrame) -> pd.DataFrame:
        """
        Step A: 5-Minute Grid Construction (Standardization).
        
        Converts variable start/end times into a fixed length array (288 slots).
        
        Args:
            episodes: DataFrame of episodes for one person.
            
        Returns:
            DataFrame with individual grid columns.
        """
        # Initialize blank arrays
        loc_grid = np.zeros(self.slots, dtype=int)
        act_grid = np.zeros(self.slots, dtype=int)
        dens_grid = np.zeros(self.slots, dtype=int)

        # Density Logic: Only count social density if at home
        valid_social = [c for c in self.social_cols if c in episodes.columns]

        # Convert 1=Yes, 2=No, 9=Unknown to Binary (1=Yes, 0=Else)
        episodes_social = episodes[valid_social].replace({1: 1, 2: 0, 9: 0}).fillna(0)

        # MASK: Only count social density if occPRE == 1 (Home)
        is_home = (episodes['occPRE'] == 1).astype(int)

        # Assign to copy to avoid warnings
        episodes = episodes.copy()
        episodes['social_sum'] = episodes_social.sum(axis=1) * is_home

        # Fill the grid based on episodes
        for _, row in episodes.iterrows():
            # Convert HHMM format to total minutes (e.g., 1030 -> 10*60 + 30 = 630)
            s_raw = int(row['start'])
            s_min = (s_raw // 100) * 60 + (s_raw % 100)
            
            e_raw = int(row['end'])
            e_min = (e_raw // 100) * 60 + (e_raw % 100)

            # Convert minutes to slot index
            s_idx = int(np.floor(s_min / self.res))
            e_idx = int(np.floor(e_min / self.res))

            s_idx = max(0, min(s_idx, self.slots - 1))
            e_idx = max(0, min(e_idx, self.slots))

            # Fill range
            if e_idx > s_idx:
                # Normal Case
                loc_grid[s_idx:e_idx] = row['occPRE']
                act_grid[s_idx:e_idx] = row['occACT']
                dens_grid[s_idx:e_idx] = row['social_sum']
            elif e_idx < s_idx:
                # WRAPPED EPISODE
                loc_grid[s_idx:] = row['occPRE']
                act_grid[s_idx:] = row['occACT']
                dens_grid[s_idx:] = row['social_sum']
                
                loc_grid[:e_idx] = row['occPRE']
                act_grid[:e_idx] = row['occACT']
                dens_grid[:e_idx] = row['social_sum']

        # Return dataframe for this individual
        return pd.DataFrame({
            'ind_occPRE': loc_grid,
            'ind_occACT': act_grid,
            'ind_density': dens_grid
        })

    def _aggregate_household(self, people_grids: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Executes Steps B, C, and D combining multiple individual grids.
        
        Args:
            people_grids: List of individual grid DataFrames.
            
        Returns:
            DataFrame with household-level aggregated columns.
        """
        # Create Time Index (00:00, 00:05, ... 23:55)
        time_slots = pd.date_range(
            "00:00", "23:55", freq=f"{self.res}min"
        ).strftime('%H:%M')

        # Dataframe to store final household results
        hh_df = pd.DataFrame({'Time_Slot': time_slots})

        if not people_grids:
            hh_df['occPre'] = 0
            hh_df['occDensity'] = 0
            hh_df['occActivity'] = ""
            return hh_df

        # --- STEP B: Aggregated Presence (Binary) -> occPre ---
        loc_stack = np.vstack([p['ind_occPRE'].values for p in people_grids])
        presence_binary = (loc_stack == 1).astype(int)
        occupancy_count = presence_binary.sum(axis=0)
        hh_df['occPre'] = (occupancy_count >= 1).astype(int)

        # --- STEP C: Social Density -> occDensity ---
        dens_stack = np.vstack([p['ind_density'].values for p in people_grids])
        hh_df['occDensity'] = dens_stack.sum(axis=0)

        # --- STEP D: Aggregated Activity Sets -> occActivity ---
        act_stack = np.vstack([p['ind_occACT'].values for p in people_grids])
        activity_sets = []

        for t in range(self.slots):
            acts_at_t = act_stack[:, t]
            pres_at_t = presence_binary[:, t]

            # Keep activities only for people who are PRESENT (1)
            valid_acts = acts_at_t[pres_at_t == 1]

            if len(valid_acts) > 0:
                unique_acts = sorted(np.unique(valid_acts))
                unique_acts = [str(a) for a in unique_acts if a > 0]
                act_str = ",".join(unique_acts)
            else:
                act_str = "0"

            activity_sets.append(act_str)

        hh_df['occActivity'] = activity_sets

        return hh_df


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_household_aggregation(
    df_full: pd.DataFrame,
    report_path: Optional[Path] = None
) -> bool:
    """
    Performs logical checks on the aggregated data and saves report to txt.
    
    Args:
        df_full: Full aggregated DataFrame.
        report_path: Optional path to save validation report.
        
    Returns:
        True if all checks pass, False otherwise.
    """
    import math
    
    # Buffer to hold log messages
    logs = []

    def log(message: str) -> None:
        print(message)
        logs.append(str(message))

    log(f"\n{'=' * 60}")
    log(f"  VALIDATING HOUSEHOLD AGGREGATION")
    log(f"{'=' * 60}")

    all_passed = True

    # --- CHECK 1: COMPLETENESS ---
    log(f"\n1. CHECKING TIME GRID COMPLETENESS...")
    if 'AgentID' not in df_full.columns:
        log("   Error: 'AgentID' column missing. Cannot validate completeness.")
        return False

    counts = df_full.groupby(['AgentID', 'Day_Type']).size()

    if (counts == 288).all():
        log(f"   [OK] All {len(counts):,} person-days have exactly 288 time slots.")
    else:
        errors = counts[counts != 288]
        log(f"   [ERROR] Found {len(errors)} incomplete profiles.")
        log(f"      Sample errors: {errors.head().to_dict()}")
        all_passed = False

    # --- CHECK 2: LOGIC (Presence vs. Density) ---
    log(f"\n2. CHECKING LOGIC (Presence vs. Density)...")
    empty_house = df_full[df_full['occPre'] == 0]
    ghosts = empty_house[empty_house['occDensity'] > 0]

    if len(ghosts) == 0:
        log(f"   [OK] No social density detected in empty houses.")
    else:
        log(f"   [ERROR] Found {len(ghosts):,} rows where House is Empty but Density > 0.")
        all_passed = False

    # --- CHECK 3: ACTIVITY CONSISTENCY ---
    log(f"\n3. CHECKING ACTIVITY STRINGS...")
    if 'occActivity' in empty_house.columns:
        ghost_activities = empty_house[empty_house['occActivity'].astype(str) != "0"]
        if len(ghost_activities) == 0:
            log(f"   [OK] Activity is correctly marked '0' when empty.")
        else:
            log(f"   [ERROR] Found {len(ghost_activities):,} rows with activities in empty house.")
            all_passed = False

    # --- SAVE REPORT TO FILE ---
    if report_path:
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("\n".join(logs))
                f.write("\n")
        except Exception as e:
            print(f"   Error writing report file: {e}")

    return all_passed


def visualize_multiple_households(
    df_full: pd.DataFrame,
    n_samples: int = 16,
    output_img_path: Optional[Path] = None,
    report_path: Optional[Path] = None
) -> None:
    """
    Generates a Grid Plot for 'n_samples' random households.
    
    Args:
        df_full: Full aggregated DataFrame.
        n_samples: Number of household samples to plot.
        output_img_path: Path to save the batch plot image.
        report_path: Path to append status to report.
    """
    import matplotlib.pyplot as plt
    import math

    msg_start = f"\n4. GENERATING VISUAL VERIFICATION PLOT ({n_samples} Households)..."
    print(msg_start)

    if report_path and report_path.exists():
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(msg_start + "\n")

    # 1. Filter for households with some activity (Density > 1)
    interesting_ids = df_full[df_full['occDensity'] > 1]['SIM_HH_ID'].unique()

    if len(interesting_ids) == 0:
        print("   Warning: No high-density households found. Sampling random ones.")
        interesting_ids = df_full['SIM_HH_ID'].unique()

    # 2. Random Sample
    actual_n = min(n_samples, len(interesting_ids))
    sample_ids = np.random.choice(interesting_ids, actual_n, replace=False)

    # 3. Setup Grid
    cols = 4
    rows = math.ceil(actual_n / cols)
    figsize_height = rows * 3

    fig, axes = plt.subplots(rows, cols, figsize=(15, figsize_height), sharex=False)
    axes = axes.flatten()

    # 4. Plot Loop
    for i, ax in enumerate(axes):
        if i < actual_n:
            hh_id = sample_ids[i]

            # Get Data (Priority: Weekday -> Weekend)
            mask = (df_full['SIM_HH_ID'] == hh_id) & (df_full['Day_Type'] == 'Weekday')
            df_hh = df_full[mask].copy()

            if df_hh.empty:
                mask = (df_full['SIM_HH_ID'] == hh_id) & (df_full['Day_Type'] == 'Weekend')
                df_hh = df_full[mask].copy()

            df_plot = df_hh[['Time_Slot', 'occPre', 'occDensity']].drop_duplicates()
            x = range(len(df_plot))

            if df_plot.empty:
                ax.text(0.5, 0.5, "No Data", ha='center')
                continue

            # Plot Presence (fill)
            ax.fill_between(
                x, df_plot['occPre'], step="pre", 
                color='green', alpha=0.3, label='Occupied'
            )
            ax.set_ylim(0, 1.2)
            ax.set_yticks([])
            ax.set_ylabel("Presence", fontsize=8, color='green')

            # Plot Density (line)
            ax2 = ax.twinx()
            ax2.plot(x, df_plot['occDensity'], color='blue', linewidth=1.5, label='Density')
            ax2.set_ylabel("Density", fontsize=8, color='blue')
            ax2.tick_params(axis='y', labelsize=8)

            ax.set_title(f"Household #{hh_id}", fontsize=10, fontweight='bold', pad=3)

            # X-axis labels
            ticks = np.arange(0, 288, 48)
            if len(df_plot) >= 288:
                labels = [df_plot['Time_Slot'].iloc[j] for j in ticks if j < len(df_plot)]
            else:
                labels = [''] * len(ticks)
            ax.set_xticks(ticks[:len(labels)])
            ax.set_xticklabels(labels, rotation=45, fontsize=8)
            ax.grid(True, alpha=0.2)

            # Legend for first plot only
            if i == 0:
                lines, lbls = ax.get_legend_handles_labels()
                lines2, lbls2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, lbls + lbls2, loc='upper left', fontsize=8)
        else:
            ax.axis('off')

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
# MAIN EXECUTION
# =============================================================================

def main(sample_pct: int = 10, skip_validation: bool = False) -> None:
    """
    Entry point for household aggregation.
    
    Args:
        sample_pct: Sample percentage used in ProfileMatcher (for file naming).
        skip_validation: If True, skip validation step.
    """
    # --- 1. Define Paths (Cross-platform) ---
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from occ_config import BASE_DIR
    
    # Input from DTYPE_expansion (refined DTYPE)
    INPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "DTYPE_expansion"
    OUTPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "HH_aggregation"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Input file from DTYPE_expansion
    suffix = f"_sample{sample_pct}pct" if sample_pct < 100 else ""
    expanded_file = INPUT_DIR / f"16CEN15GSS_Full_Schedules_Refined{suffix}.csv"
    
    # Output files
    output_file = OUTPUT_DIR / f"16CEN15GSS_Full_Aggregated{suffix}.csv"
    report_path = OUTPUT_DIR / f"16CEN15GSS_Validation_HH{suffix}.txt"
    plot_path = OUTPUT_DIR / f"16CEN15GSS_Validation_Plot{suffix}.png"
    
    print("=" * 60)
    print("  16CEN15GSS HOUSEHOLD AGGREGATION")
    print("=" * 60)
    
    # --- 2. Load Data ---
    print("\n1. Loading Expanded Schedules...")
    if not expanded_file.exists():
        print(f"   Error: {expanded_file.name} not found.")
        print(f"   Run DTYPE_expansion first with --sample {sample_pct}")
        return
    
    df_expanded = pd.read_csv(expanded_file, low_memory=False)
    print(f"   Loaded: {len(df_expanded):,} rows")
    print(f"   Unique Households: {df_expanded['SIM_HH_ID'].nunique():,}")
    print(f"   Unique Agents: {df_expanded['AgentID'].nunique():,}")
    
    # --- 3. Initialize Aggregator ---
    aggregator = HouseholdAggregator(resolution_min=5)
    
    # --- 4. Run Process ---
    print("\n2. Starting Process (Padding + Aggregation)...")
    df_final = aggregator.process_all(df_expanded)
    
    # --- 5. Save ---
    print(f"\n3. Saving Full Integrated Data to: {output_file.name}...")
    df_final.to_csv(output_file, index=False)
    
    # --- 6. Basic Verification ---
    print("\n" + "=" * 60)
    print("  VERIFICATION")
    print("=" * 60)
    print(f"   Total Rows: {len(df_final):,}")
    print(f"   Total Columns: {len(df_final.columns)}")
    print(f"   Sample Columns: {list(df_final.columns[:5])} ... {list(df_final.columns[-3:])}")
    
    print(f"\n   Household Presence (occPre) Stats:")
    print(f"     - Home slots: {(df_final['occPre'] == 1).sum():,}")
    print(f"     - Away slots: {(df_final['occPre'] == 0).sum():,}")
    
    # --- 7. Validation ---
    if not skip_validation:
        validate_household_aggregation(df_final, report_path=report_path)
        visualize_multiple_households(
            df_final, n_samples=16, 
            output_img_path=plot_path, 
            report_path=report_path
        )
        print(f"\n   Validation Report saved to: {report_path.name}")
    
    print("\n" + "=" * 60)
    print("  [OK] HOUSEHOLD AGGREGATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Household Aggregation: Census 2016 + GSS 2015"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Sample percentage used in ProfileMatcher (default: 10)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation step"
    )
    args = parser.parse_args()
    
    main(sample_pct=args.sample, skip_validation=args.skip_validation)
