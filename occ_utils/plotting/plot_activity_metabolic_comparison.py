import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# BASE DIR: ../../../ from this script (occ_utils/plotting/script.py -> eSim/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# CONFIGURATION
# =============================================================================

# Files
FILE_ACT_2005 = BASE_DIR / "Occupancy/Outputs_06CEN05GSS/HH_aggregation/06CEN05GSS_Full_Aggregated_sample5pct.csv"
FILE_ACT_2015 = BASE_DIR / "Occupancy/Outputs_16CEN15GSS/HH_aggregation/16CEN15GSS_Full_Aggregated_sample10pct.csv"
FILE_ACT_2025 = BASE_DIR / "Occupancy/Outputs_CENSUS/Full_data.csv"

FILE_BEM_2005 = BASE_DIR / "BEM_Setup/BEM_Schedules_2005.csv"
FILE_BEM_2015 = BASE_DIR / "BEM_Setup/BEM_Schedules_2015.csv"
FILE_BEM_2025 = BASE_DIR / "BEM_Setup/BEM_Schedules_2025.csv"

# Output Directory: Same as this script
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "BEM_Activity_Metabolic_Comparison.png"

# Activity Mapping (Code -> Full Name)
ACTIVITY_MAP = {
    '1': 'Work & Related',
    '2': 'Household Work',
    '3': 'Caregiving',
    '4': 'Shopping',
    '5': 'Sleep',
    '6': 'Eating',
    '7': 'Personal Care',
    '8': 'Education',
    '9': 'Socializing',
    '10': 'Passive Leisure',
    '11': 'Active Leisure',
    '12': 'Volunteer',
    '13': 'Travel',
    '14': 'Miscellaneous',
    '0': 'Other'
}

# Order for plotting (1-14 + Other)
CATEGORY_ORDER = [
    'Sleep', 'Personal Care', 'Eating', 
    'Work & Related', 'Education', 
    'Household Work', 'Caregiving', 'Shopping',
    'Socializing', 'Passive Leisure', 'Active Leisure', 'Volunteer', 'Miscellaneous',
    'Travel', 'Other'
]

# Colors for Years (Consistent across rows)
YEAR_COLORS = {
    '2005': '#2196F3', # Blue
    '2015': '#FF9800', # Orange
    '2025': '#4CAF50'  # Green
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def process_activity_data_chunk(file_path, year_label, chunksize=100000):
    print(f"   Processing {year_label} activity data from: {file_path.name}")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return None

    category_counts = {cat: 0.0 for cat in CATEGORY_ORDER}
    
    try:
        header = pd.read_csv(file_path, nrows=0).columns.tolist()
        act_col = 'occActivity' if 'occActivity' in header else 'occACT'
        
        chunk_iter = pd.read_csv(file_path, usecols=[act_col], chunksize=chunksize)
        
        for chunk in chunk_iter:
            chunk = chunk.dropna(subset=[act_col])
            act_series = chunk[act_col].astype(str)
            counts = act_series.value_counts()
            
            for act_str, count in counts.items():
                if not act_str: continue
                codes = act_str.split(',')
                weight = 1.0 / len(codes)
                
                for code in codes:
                    cat = ACTIVITY_MAP.get(code.strip(), 'Other')
                    if cat in category_counts:
                        category_counts[cat] += count * weight
            
    except Exception as e:
        print(f"   ⚠️ Error processing {year_label}: {e}")
        return None
        
    total_weight = sum(category_counts.values())
    if total_weight == 0:
        return None
        
    hours_per_day = {k: (v / total_weight) * 24 for k, v in category_counts.items()}
    return hours_per_day

def process_bem_profiles(file_path, year_label):
    print(f"   Processing {year_label} metabolic profiles from: {file_path.name}")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return None
        
    try:
        df = pd.read_csv(file_path, usecols=['Hour', 'Metabolic_Rate'])
    except Exception as e:
        print(f"   ⚠️ Error reading {year_label}: {e}")
        return None
        
    df_occ = df[df['Metabolic_Rate'] > 1.0].copy()
    
    if df_occ.empty:
        return None
        
    hourly_profile = df_occ.groupby('Hour')['Metabolic_Rate'].mean()
    hourly_profile = hourly_profile.reindex(range(24), fill_value=0)
    
    return hourly_profile

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("  ACTIVITY & METABOLIC COMPARISON PLOT GENERATOR (2x3 GRID)")
    print("="*60)
    
    # --- 1. Process Activity Data ---
    print("\n1. Processing Activity Time Allocation...")
    activity_data = {}
    years = ['2005', '2015', '2025']
    files_act = [FILE_ACT_2005, FILE_ACT_2015, FILE_ACT_2025]
    
    for y_label, f_path in zip(years, files_act):
        res = process_activity_data_chunk(f_path, y_label)
        if res:
            activity_data[y_label] = res
            
    df_act = pd.DataFrame(activity_data).T 
    # Ensure all columns exist
    for cat in CATEGORY_ORDER:
        if cat not in df_act.columns:
            df_act[cat] = 0.0
    df_act = df_act[CATEGORY_ORDER] # Reorder
    
    # --- 2. Process Metabolic Profiles ---
    print("\n2. Processing Metabolic Profiles...")
    metabolic_profiles = {}
    files_bem = [FILE_BEM_2005, FILE_BEM_2015, FILE_BEM_2025]
    
    for y_label, f_path in zip(years, files_bem):
        res = process_bem_profiles(f_path, y_label)
        if res is not None:
            metabolic_profiles[y_label] = res
            
    # --- 3. Plotting ---
    print("\n3. Generating Figure...")
    
    # Layout: 2 Rows, 3 Columns
    fig, axes = plt.subplots(2, 3, figsize=(20, 12), constrained_layout=True)
    sns.set_theme(style="whitegrid")
    
    # Function to add value labels
    def add_labels(ax):
        for p in ax.patches:
            height = p.get_height()
            if height > 0.1: # Threshold to avoid clutter
                ax.annotate(f'{height:.1f}', 
                            (p.get_x() + p.get_width() / 2., height), 
                            ha = 'center', va = 'center', 
                            xytext = (0, 5), 
                            textcoords = 'offset points',
                            fontsize=8)

    # --- ROW 1: ACTIVITY DISTRIBUTION (Vertical Bars) ---
    for i, year in enumerate(years):
        ax = axes[0, i]
        
        if year in df_act.index:
            vals = df_act.loc[year]
            
            # Add grid BEFORE plotting bars (so it appears behind)
            ax.grid(True, axis='y', linestyle='--', alpha=0.6, zorder=0)
            
            # Plot bars with higher zorder
            vals.plot(kind='bar', ax=ax, color=YEAR_COLORS[year], width=0.8, edgecolor='black', alpha=0.8, zorder=3)
            
            ax.set_title(f"{year} - Activity Distribution", fontsize=14, fontweight='bold')
            ax.set_ylabel("Hours / Day" if i == 0 else "")
            ax.set_xlabel("")
            ax.set_ylim(0, 10.5) 
            
            # Labels rotated
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            add_labels(ax)
            
        else:
            ax.text(0.5, 0.5, "No Data", ha='center')

    # --- ROW 2: METABOLIC PROFILES (Line Plots) ---
    max_met = 0
    for p in metabolic_profiles.values():
        max_met = max(max_met, p.max())
    y_limit = max(max_met * 1.1, 160)
        
    for i, year in enumerate(years):
        ax = axes[1, i]
        
        if year in metabolic_profiles:
            profile = metabolic_profiles[year]
            
            # Plot Profile
            ax.plot(profile.index, profile.values, color=YEAR_COLORS[year], linewidth=3, label='Metabolic Rate')
            # Fill under curve
            ax.fill_between(profile.index, profile.values, color=YEAR_COLORS[year], alpha=0.1)
            
            # 95W Reference
            ax.axhline(95, color='darkred', linestyle='--', linewidth=2, label='Default (95W)')
            
            ax.set_title(f"{year} - Metabolic Profile", fontsize=14, fontweight='bold')
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Watts (W)" if i == 0 else "")
            ax.set_ylim(0, y_limit)
            ax.set_xticks(range(0, 25, 4))
            ax.grid(True, linestyle='--', alpha=0.6)
            
            if i == 0:
                ax.legend(loc='upper left', frameon=True)
            else:
                ax.text(1, 102, "95W Default (DOE Prototype)", color='darkred', fontsize=12, fontweight='bold')
                
        else:
             ax.text(0.5, 0.5, "No Data", ha='center')

    # Save
    fig.savefig(OUTPUT_FILE, dpi=300)
    print(f"\n✅ Plot saved to: {OUTPUT_FILE}")
    plt.close(fig)

if __name__ == "__main__":
    main()
