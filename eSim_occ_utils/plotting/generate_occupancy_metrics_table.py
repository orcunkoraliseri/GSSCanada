import pandas as pd
import numpy as np
import sys
from pathlib import Path

# BASE DIR: ../../../ from this script
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# CONFIGURATION
# =============================================================================

FILES = {
    '2005': BASE_DIR / "0_BEM_Setup/BEM_Schedules_2005.csv",
    '2015': BASE_DIR / "0_BEM_Setup/BEM_Schedules_2015.csv",
    '2025': BASE_DIR / "0_BEM_Setup/BEM_Schedules_2025.csv"
}

OUTPUT_CSV = Path(__file__).resolve().parent / "Table_4_1_1_Occupancy_Metrics.csv"
OUTPUT_MD = Path(__file__).resolve().parent / "Table_4_1_1_Occupancy_Metrics.md"

# Default Schedule (DOE MidRise Apartment) - Weekday
# From idf_optimizer.py _get_fallback_schedules
DEFAULT_PROFILE_WEEKDAY = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.85,  # 0-7
    0.39, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, # 8-15
    0.30, 0.52, 0.87, 0.87, 0.87, 1.0, 1.0, 1.0  # 16-23
]
# Weekend is same as weekday for this specific default profile
DEFAULT_PROFILE_WEEKEND = list(DEFAULT_PROFILE_WEEKDAY)

# =============================================================================
# METRIC FUNCTIONS
# =============================================================================

def get_occupied_hours(profile_24h):
    """Sum of hourly fractions * 1 hour."""
    return sum(profile_24h)

def get_daytime_vacancy(profile_24h):
    """
    Daytime Vacancy % (09:00 - 17:00 => Hours 9 to 16 inclusive)
    Vacancy = 1 - Occupancy
    """
    # Slice hours 9 to 16 (8 hours total)
    # Indices 9, 10, ... 16
    daytime_vals = profile_24h[9:17]
    if len(daytime_vals) == 0: return 0.0
    
    mean_occ = sum(daytime_vals) / len(daytime_vals)
    vacancy_pct = (1.0 - mean_occ) * 100
    return vacancy_pct

def get_transition_times(profile_24h):
    """
    Find Morning Departure (steepest drop) and Evening Return (steepest rise).
    Returns formatted strings HH:MM.
    Using simple discrete derivative max/min.
    """
    # Calculate gradients: diff[i] = profile[i] - profile[i-1] (wrapping around?)
    # Or profile[i+1] - profile[i].
    # Let's use np.diff.
    
    # We want hour of occurrence. 
    # Morning: 05:00 to 12:00
    # Evening: 12:00 to 24:00
    
    diffs = np.diff(profile_24h, prepend=profile_24h[-1]) 
    # diff at index i is change FROM i-1 TO i.
    # If index 8 (08:00) is 0.39 and index 7 (07:00) is 0.85, diff is -0.46. 
    # This change happens "at" 08:00 (leading up to it). 
    # Let's say departure time is the hour where the drop ends or begins?
    # Usually "Morning Departure" is approximated by the center of the drop.
    # For simplicity: The hour index with the minimum gradient (steepest drop).
    
    # Restrict search windows
    morning_window = range(5, 13) # 05:00 to 12:00
    evening_window = range(12, 24) # 12:00 to 23:00
    
    # Morning Departure
    min_diff = 0
    dep_hour = -1
    for h in morning_window:
        if diffs[h] < min_diff:
            min_diff = diffs[h]
            dep_hour = h
    
    # Evening Return (Max rise)
    max_diff = 0
    ret_hour = -1
    for h in evening_window:
        if diffs[h] > max_diff:
            max_diff = diffs[h]
            ret_hour = h
            
    # Format HH:MM (Assuming event happens "at" the hour mark)
    def fmt(h): return f"{h:02d}:00" if h >= 0 else "—"
    
    return fmt(dep_hour), fmt(ret_hour)

# =============================================================================
# PROCESSING
# =============================================================================

def process_dataset(name, file_path=None, manual_profile=None):
    print(f"   Processing {name}...")
    
    metrics = {}
    
    if manual_profile:
        # manual_profile should be tuple (weekday, weekend)
        prof_wd, prof_we = manual_profile
        
        # Weekday Metrics
        metrics['Weekday occupied hours (h)'] = get_occupied_hours(prof_wd)
        
        # Weekend Metrics
        metrics['Weekend occupied hours (h)'] = get_occupied_hours(prof_we)
        
        # Transitions (Weekday only usually)
        dep, ret = get_transition_times(prof_wd)
        metrics['Morning departure time'] = dep
        metrics['Evening return time'] = ret
        
        # Daytime Vacancy (Weekday)
        metrics['Daytime vacancy (09–17), %'] = get_daytime_vacancy(prof_wd)
        
    elif file_path:
        try:
            # Load only needed columns
            df = pd.read_csv(file_path, usecols=['Hour', 'Day_Type', 'Occupancy_Schedule'])
            
            # --- Weekday Profile ---
            df_wd = df[df['Day_Type'] == 'Weekday']
            if not df_wd.empty:
                prof_wd = df_wd.groupby('Hour')['Occupancy_Schedule'].mean().reindex(range(24)).fillna(0).values
            else:
                prof_wd = np.zeros(24)
                
            # --- Weekend Profile ---
            df_we = df[df['Day_Type'] == 'Weekend']
            if not df_we.empty:
                prof_we = df_we.groupby('Hour')['Occupancy_Schedule'].mean().reindex(range(24)).fillna(0).values
            else:
                prof_we = np.zeros(24)
                
            # Compute Metrics
            metrics['Weekday occupied hours (h)'] = get_occupied_hours(prof_wd)
            metrics['Weekend occupied hours (h)'] = get_occupied_hours(prof_we)
            
            dep, ret = get_transition_times(prof_wd)
            metrics['Morning departure time'] = dep
            metrics['Evening return time'] = ret
            
            metrics['Daytime vacancy (09–17), %'] = get_daytime_vacancy(prof_wd)
            
        except Exception as e:
            print(f"   ⚠️ Error processing {name}: {e}")
            return None
            
    return metrics

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("  RELATIONAL OCCUPANCY METRICS TABLE GENERATOR")
    print("="*60)
    
    results = {}
    
    # 1. Process Default
    results['Default'] = process_dataset('Default', manual_profile=(DEFAULT_PROFILE_WEEKDAY, DEFAULT_PROFILE_WEEKEND))
    
    # 2. Process Datasets
    for year, fpath in FILES.items():
        if fpath.exists():
            res = process_dataset(year, file_path=fpath)
            if res:
                results[year] = res
        else:
            print(f"   ❌ File not found: {fpath}")
            
    # 3. Format Output
    # Rows: Metrics
    # Cols: Scenarios
    metric_order = [
        'Weekday occupied hours (h)',
        'Weekend occupied hours (h)',
        'Morning departure time',
        'Evening return time',
        'Daytime vacancy (09–17), %'
    ]
    
    # Create DataFrame
    df_out = pd.DataFrame(index=metric_order, columns=['Default', '2005', '2015', '2025'])
    
    for col in df_out.columns:
        if col in results:
            for row in df_out.index:
                val = results[col].get(row, '—')
                # Format numbers
                if isinstance(val, float):
                    if '%' in row:
                        df_out.at[row, col] = f"{val:.1f}"
                    elif '(h)' in row:
                        df_out.at[row, col] = f"{val:.1f}"
                    else:
                        df_out.at[row, col] = str(val)
                else:
                    df_out.at[row, col] = str(val)
    
    # 4. Save CSV
    df_out.to_csv(OUTPUT_CSV)
    print(f"\n✅ CSV saved to: {OUTPUT_CSV}")
    
    # 5. Create Markdown (Manual formatting to avoid tabulate dependency)
    def to_md(df):
        lines = []
        # Header
        header = "| Metric | " + " | ".join(df.columns) + " |"
        lines.append(header)
        # Separator
        lines.append("|---|" + "|".join(["---"] * len(df.columns)) + "|")
        # Body
        for idx, row in df.iterrows():
            line = f"| {idx} | " + " | ".join(str(x) for x in row) + " |"
            lines.append(line)
        return "\n".join(lines)

    md_content = to_md(df_out)
    
    full_md = f"""# Table 4.1.1: Residential Occupancy Metrics by Period

{md_content}

> **Notes**:
> - **Default** is based on DOE MidRise Apartment standard schedule.
> - **Morning Departure / Evening Return** are estimated based on the hour of steepest change in the mean weekday profile.
> - **Daytime Vacancy** is calculated for the 09:00–17:00 period on weekdays.
"""
    
    with open(OUTPUT_MD, 'w') as f:
        f.write(full_md)
        
    print(f"✅ Markdown saved to: {OUTPUT_MD}")
    
    # Print to console
    print("\n" + md_content)

if __name__ == "__main__":
    main()
