"""
16CEN15GSS Occupancy to BEM Conversion Module

Converts 5-minute ABM profiles into Hourly BEM Schedules for
EnergyPlus/Honeybee building energy simulations.

Pipeline:
1. Load full aggregated data from HH_aggregation
2. Resample 5-minute to 60-minute resolution
3. Calculate occupancy fractions and metabolic rates
4. Generate BEM-ready CSV and visualization plots

Output Format:
- 60-minute resolution
- Fractional occupancy (0-1)
- Metabolic rate (Watts per person)
- Residential variables (DTYPE, BEDRM, etc.)
"""

import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs): return iterable
import matplotlib.pyplot as plt
import seaborn as sns


# =============================================================================
# CLASS: BEMConverter
# =============================================================================

class BEMConverter:
    """
    Converts 5-minute ABM profiles into Hourly BEM Schedules.
    
    Output format:
        - 60-minute resolution
        - Fractional occupancy (0-1)
        - Metabolic rate (W)
        - Includes residential variables (DTYPE, BEDRM, etc.)
    """

    def __init__(self, output_dir: Path):
        """
        Initialize BEMConverter.
        
        Args:
            output_dir: Directory for output files.
        """
        self.output_dir = output_dir

        # 2024 Compendium of Physical Activities Mapping (Activity Code -> Watts)
        # Assumes 1 MET ~= 70 Watts (Avg adult 70kg)
        self.metabolic_map = {
            '1': 125,   # Work & Related (~1.8 MET - Standing/Office)
            '2': 175,   # Household Work (~2.5 MET - Cleaning/Cooking)
            '3': 190,   # Caregiving (~2.7 MET - Active child/elder care)
            '4': 195,   # Shopping (~2.8 MET - Walking with cart)
            '5': 70,    # Sleep (~1.0 MET - Sleeping/Lying quietly)
            '6': 105,   # Eating (~1.5 MET - Sitting eating)
            '7': 170,   # Personal Care (~2.4 MET - Dressing/Showering)
            '8': 110,   # Education (~1.6 MET - Sitting in class/Studying)
            '9': 90,    # Socializing (~1.3 MET - Sitting talking)
            '10': 85,   # Passive Leisure (~1.2 MET - TV/Reading + fidgeting)
            '11': 245,  # Active Leisure (~3.5 MET - Walking/Exercise)
            '12': 105,  # Volunteer (~1.5 MET - Light effort)
            '13': 140,  # Travel (~2.0 MET - Driving/Walking mix)
            '14': 135,  # Miscellaneous (~1.9 MET - Standing/Misc tasks)
            '0': 0      # Empty
        }

        # DTYPE Mapping (Code -> Description)
        self.dtype_map = {
            '1': "SingleD",   # Single Detached
            '2': "SemiD",     # Semi-Detached
            '3': "Attached",  # Row/Attached
            '4': "DuplexD",   # Duplex
            '5': "HighRise",  # High-Rise Apartment
            '6': "MidRise",   # Mid-Rise Apartment
            '7': "OtherA",    # Other Attached
            '8': "Movable",   # Mobile Home
            # Fallbacks
            'Apartment': "Apt (Unspec.)",
            'Other dwelling': "Other"
        }

        # PR Mapping (Code -> Region Name)
        self.pr_map = {
            '10': "Atlantic",
            '24': "Quebec",
            '35': "Ontario",
            '46': "Prairies",
            '48': "Alberta",
            '59': "BC"
        }

    def process_households(self, df_full: pd.DataFrame) -> pd.DataFrame:
        """
        Process all households and generate BEM schedules.
        
        Args:
            df_full: Full aggregated DataFrame from HH_aggregation.
            
        Returns:
            DataFrame with hourly BEM schedules.
        """
        print(f"\n   Starting BEM Conversion (Hourly Resampling)...")

        # 1. Prepare Time Index
        df_full['datetime'] = pd.to_datetime(df_full['Time_Slot'], format='%H:%M')

        # 2. Map Activities to Watts (Vectorized)
        print("   Mapping metabolic rates...")
        df_full['watts_5min'] = df_full['occActivity'].apply(self._calculate_watts)

        # 3. Group by Household & DayType
        groups = df_full.groupby(['SIM_HH_ID', 'Day_Type'])

        bem_schedules = []

        # List of residential variables to carry over
        target_res_cols = ['DTYPE', 'BEDRM', 'CONDO', 'ROOM', 'REPAIR', 'PR']
        # Also check for Census-prefixed versions
        census_res_cols = ['Census_HHSIZE']

        for (hh_id, day_type), group in tqdm(groups, desc="Generating Schedules"):
            # Get Static Attributes (First row of the group)
            # Try both HHSIZE and Census_HHSIZE
            if 'HHSIZE' in group.columns:
                hh_size = group['HHSIZE'].iloc[0]
            elif 'Census_HHSIZE' in group.columns:
                hh_size = group['Census_HHSIZE'].iloc[0]
            else:
                hh_size = 1  # Default fallback

            # Extract residential vars safely (handle if missing)
            res_data = {}
            for col in target_res_cols:
                # Check both original and Census-prefixed
                if col in group.columns:
                    val = group[col].iloc[0]
                elif f'Census_{col}' in group.columns:
                    val = group[f'Census_{col}'].iloc[0]
                else:
                    val = "Unknown"

                # Apply DTYPE Mapping
                if col == 'DTYPE':
                    val_str = str(int(val)) if pd.notnull(val) and val != "Unknown" else str(val)
                    res_data[col] = self.dtype_map.get(val_str, val)
                # Apply PR Mapping
                elif col == 'PR':
                    val_str = str(int(val)) if pd.notnull(val) and val != "Unknown" else str(val)
                    res_data[col] = self.pr_map.get(val_str, val)
                else:
                    res_data[col] = val

            # --- HOURLY RESAMPLING ---
            g_indexed = group.set_index('datetime')

            # Resample 5min -> 60min (Mean)
            hourly = g_indexed.resample('60min').agg({
                'occPre': 'mean',       # Fraction of hour home (0.0 - 1.0)
                'occDensity': 'mean',   # Avg social density
                'watts_5min': 'mean'    # Avg metabolic rate
            }).reset_index()

            # --- BEM FORMULAS ---
            # 1. Reconstruct People Count: (1 person + Social Density) * Presence Fraction
            estimated_count = hourly['occPre'] * (hourly['occDensity'] + 1)

            # 2. Normalize to Schedule (0-1) by dividing by HH Capacity
            occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)

            # 3. Create Result DataFrame
            data_dict = {
                'SIM_HH_ID': hh_id,
                'Day_Type': day_type,
                'Hour': hourly['datetime'].dt.hour,
                'HHSIZE': hh_size,
                **res_data,
                'Occupancy_Schedule': occupancy_sched.round(3),
                'Metabolic_Rate': hourly['watts_5min'].round(1)
            }

            hourly_df = pd.DataFrame(data_dict)
            bem_schedules.append(hourly_df)

        # Combine
        return pd.concat(bem_schedules, ignore_index=True)

    def _calculate_watts(self, act_str: str) -> float:
        """
        Parses activity string '1,5' -> maps to Watts -> returns average.
        
        Args:
            act_str: Activity string (comma-separated codes).
            
        Returns:
            Average metabolic rate in Watts.
        """
        if act_str == "0":
            return 0

        codes = str(act_str).split(',')
        watts = [self.metabolic_map.get(c.strip(), 100) for c in codes]
        return sum(watts) / len(watts)


# =============================================================================
# VISUALIZATION FUNCTION
# =============================================================================

def visualize_bem_distributions(df_bem: pd.DataFrame, output_dir: Path = None) -> None:
    """
    Generates validation plots for BEM schedules.
    
    Creates two plot files:
    1. Temporal plots (occupancy/metabolic distributions and sample household)
    2. Non-temporal plots (residential variable distributions)
    
    Args:
        df_bem: BEM schedules DataFrame.
        output_dir: Directory for output plots.
    """
    print(f"\n   GENERATING BEM DISTRIBUTION PLOTS...")

    if output_dir is None:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Define paths
    path_temporal = output_dir / "16CEN15GSS_BEM_temporals.png"
    path_nontemporal = output_dir / "16CEN15GSS_BEM_non_temporals.png"

    # Set style
    sns.set_theme(style="whitegrid")

    # =========================================================
    # 1. TEMPORAL PLOTS (3x2 Grid)
    # =========================================================
    fig1, axes1 = plt.subplots(3, 2, figsize=(16, 15))

    # --- ROW 1: HISTOGRAMS ---
    # Top-Left: Occupancy Distribution
    sns.histplot(
        data=df_bem, x='Occupancy_Schedule', bins=20, kde=False,
        color='green', alpha=0.6, ax=axes1[0, 0]
    )
    axes1[0, 0].set_title("Population Distribution: Occupancy Fractions")
    axes1[0, 0].set_xlabel("Occupancy (0=Empty, 1=Full)")

    # Top-Right: Metabolic Distribution
    active_watts = df_bem[df_bem['Metabolic_Rate'] > 0]
    sns.histplot(
        data=active_watts, x='Metabolic_Rate', bins=30, kde=True,
        color='orange', alpha=0.6, ax=axes1[0, 1]
    )
    axes1[0, 1].set_title("Population Distribution: Metabolic Rates (Occupied)")
    axes1[0, 1].set_xlabel("Watts per Person")

    # --- ROW 2: AVERAGE PROFILES ---
    # Mid-Left: Average Presence
    sns.lineplot(
        data=df_bem, x='Hour', y='Occupancy_Schedule', hue='Day_Type',
        estimator='mean', errorbar=('sd', 1),
        palette={'Weekday': 'green', 'Weekend': 'teal'}, ax=axes1[1, 0]
    )
    axes1[1, 0].set_title("Population Trend: Average Presence Schedule")
    axes1[1, 0].set_ylim(0, 1.05)
    axes1[1, 0].set_xticks(range(0, 25, 4))

    # Mid-Right: Average Metabolic
    sns.lineplot(
        data=active_watts, x='Hour', y='Metabolic_Rate', hue='Day_Type',
        estimator='mean', errorbar=None,
        palette={'Weekday': 'orange', 'Weekend': 'red'}, ax=axes1[1, 1]
    )
    axes1[1, 1].set_title("Population Trend: Average Metabolic Intensity (Heat Output)")
    axes1[1, 1].set_xticks(range(0, 25, 4))

    # --- ROW 3: SAMPLE HOUSEHOLD ---
    occupancy_check = df_bem.groupby('SIM_HH_ID')['Occupancy_Schedule'].max()
    valid_ids = occupancy_check[occupancy_check > 0].index

    if len(valid_ids) > 0:
        sample_id = np.random.choice(valid_ids)
        sample_data = df_bem[df_bem['SIM_HH_ID'] == sample_id]

        wd_data = sample_data[sample_data['Day_Type'] == 'Weekday'].sort_values('Hour')
        we_data = sample_data[sample_data['Day_Type'] == 'Weekend'].sort_values('Hour')

        def plot_dual_axis(ax, data, title):
            if data.empty:
                ax.text(0.5, 0.5, "No Data", ha='center')
                return
            x = data['Hour']

            ax.fill_between(x, data['Occupancy_Schedule'], color='green', alpha=0.3, label='Occupancy')
            ax.set_ylim(0, 1.1)
            ax.set_ylabel("Occupancy Fraction", color='green', fontsize=10)
            ax.tick_params(axis='y', labelcolor='green')

            ax2 = ax.twinx()
            ax2.plot(x, data['Metabolic_Rate'], color='darkorange', linewidth=2.5, label='Heat Gain')
            ax2.set_ylabel("Metabolic Rate (W)", color='darkorange', fontsize=10)
            ax2.tick_params(axis='y', labelcolor='darkorange')
            ax2.set_ylim(0, 250)

            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xticks(range(0, 25, 4))
            ax.set_xlabel("Hour of Day")

            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left')

        plot_dual_axis(axes1[2, 0], wd_data, f"Sample Household #{sample_id}: Weekday Schedule")
        plot_dual_axis(axes1[2, 1], we_data, f"Sample Household #{sample_id}: Weekend Schedule")

    else:
        axes1[2, 0].text(0.5, 0.5, "No Valid Samples Found", ha='center')
        axes1[2, 1].axis('off')

    plt.tight_layout()
    fig1.savefig(path_temporal, dpi=150)
    plt.close(fig1)
    print(f"   ✅ Temporal Plot saved: {path_temporal.name}")

    # =========================================================
    # 2. NON-TEMPORAL PLOTS (Residential Variables)
    # =========================================================
    # Added PR to the list
    cols_static = [c for c in ['SIM_HH_ID', 'DTYPE', 'BEDRM', 'ROOM', 'PR'] if c in df_bem.columns]
    df_static = df_bem[cols_static].drop_duplicates(subset=['SIM_HH_ID'])

    if len(df_static) > 0 and len(cols_static) > 1:
        # Changed to 2x2 grid to accommodate 4 plots
        fig2, axes2 = plt.subplots(2, 2, figsize=(15, 12))
        axes2 = axes2.flatten()  # Flatten to access by index 0-3

        # Plot DTYPE
        if 'DTYPE' in df_static.columns:
            sns.countplot(
                data=df_static, x='DTYPE', hue='DTYPE',
                palette='viridis', ax=axes2[0], legend=False
            )
            axes2[0].set_title("Distribution of Dwelling Types")
            axes2[0].tick_params(axis='x', rotation=15, labelsize=8)
            axes2[0].set_ylabel("Count of Households")
        else:
            axes2[0].text(0.5, 0.5, "DTYPE missing", ha='center')

        # Plot BEDRM
        if 'BEDRM' in df_static.columns:
            sns.countplot(
                data=df_static, x='BEDRM', hue='BEDRM',
                # palette='magma', ax=axes2[1], legend=False
                palette='magma', ax=axes2[1]
            )
            axes2[1].set_title("Distribution of Bedroom Counts")
            axes2[1].set_ylabel("Count of Households")
        else:
            axes2[1].text(0.5, 0.5, "BEDRM missing", ha='center')

        # Plot ROOM
        if 'ROOM' in df_static.columns:
            sns.histplot(
                data=df_static, x='ROOM', discrete=True,
                color='purple', alpha=0.7, ax=axes2[2]
            )
            axes2[2].set_title("Distribution of Total Room Counts")
            axes2[2].set_ylabel("Count of Households")
        else:
            axes2[2].text(0.5, 0.5, "ROOM missing", ha='center')

        # Plot PR (New)
        if 'PR' in df_static.columns:
            # Geographic Sort (East -> West)
            pr_order = ["Atlantic", "Quebec", "Ontario", "Prairies", "Alberta", "BC"]
            sns.countplot(
                data=df_static, x='PR', hue='PR',
                order=pr_order,
                palette='coolwarm', ax=axes2[3], legend=False
            )
            axes2[3].set_title("Distribution by Region (PR)")
            axes2[3].tick_params(axis='x', rotation=15, labelsize=8)
            axes2[3].set_ylabel("Count of Households")
        else:
            axes2[3].text(0.5, 0.5, "PR missing", ha='center')

        plt.tight_layout()
        fig2.savefig(path_nontemporal, dpi=150)
        plt.close(fig2)
        print(f"   ✅ Non-Temporal Plot saved: {path_nontemporal.name}")
    else:
        print("   ⚠️ Skipped Non-Temporal plots (Residential columns missing).")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main(sample_pct: int = 10) -> None:
    """
    Entry point for BEM conversion.
    
    Args:
        sample_pct: Sample percentage used in previous steps (for file naming).
    """
    # --- 1. Define Paths ---
    BASE_DIR = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/eSim/Occupancy")
    
    INPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "HH_aggregation"
    OUTPUT_DIR = BASE_DIR / "Outputs_16CEN15GSS" / "occToBEM"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Input file from HH_aggregation
    suffix = f"_sample{sample_pct}pct" if sample_pct < 100 else ""
    full_data_path = INPUT_DIR / f"16CEN15GSS_Full_Aggregated{suffix}.csv"
    
    # Output files
    output_path = OUTPUT_DIR / f"16CEN15GSS_BEM_Schedules{suffix}.csv"
    
    print("=" * 60)
    print("  16CEN15GSS OCCUPANCY TO BEM CONVERSION")
    print("=" * 60)
    
    # --- 2. Load Data ---
    print("\n1. Loading Household Data...")
    if not full_data_path.exists():
        print(f"   Error: {full_data_path.name} not found.")
        print(f"   Run HH_aggregation first with --sample {sample_pct}")
        return
    
    df_full = pd.read_csv(full_data_path, low_memory=False)
    print(f"   Loaded: {len(df_full):,} rows")
    print(f"   Unique Households: {df_full['SIM_HH_ID'].nunique():,}")

    # --- 3. Initialize Converter ---
    converter = BEMConverter(output_dir=OUTPUT_DIR)

    # --- 4. Run Conversion ---
    df_bem = converter.process_households(df_full)

    # --- 5. Save ---
    print(f"\n2. Saving Hourly BEM Input to: {output_path.name}")
    df_bem.to_csv(output_path, index=False, float_format='%.3f')

    # --- 6. Verify ---
    print("\n" + "=" * 60)
    print("  VERIFICATION: Sample Household")
    print("=" * 60)

    pd.options.display.float_format = '{:.3f}'.format

    cols_to_show = ['SIM_HH_ID', 'Hour', 'DTYPE', 'BEDRM', 'ROOM', 
                    'Occupancy_Schedule', 'Metabolic_Rate']
    valid_cols = [c for c in cols_to_show if c in df_bem.columns]

    print(df_bem[valid_cols].head(12).to_string(index=False))

    # --- 7. Generate Visualizations ---
    print("\n3. Generating Visualization Plots...")
    visualize_bem_distributions(df_bem, output_dir=OUTPUT_DIR)

    print("\n" + "=" * 60)
    print("  [OK] BEM CONVERSION COMPLETE")
    print("  Ready for EnergyPlus/Honeybee!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Occupancy to BEM Conversion: Census 2016 + GSS 2015"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="Sample percentage used in previous steps (default: 10)"
    )
    args = parser.parse_args()
    
    main(sample_pct=args.sample)
