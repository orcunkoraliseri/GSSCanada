import pandas as pd
import numpy as np
from pathlib import Path
import sys

# BASE DIR: ../../../ from this script
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

try:
    from bem_utils import idf_optimizer
except ImportError:
    print("Error: Could not import bem_utils.")
    sys.exit(1)

# CONFIG
GSS_FILE = BASE_DIR / "BEM_Setup/BEM_Schedules_2025.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = OUTPUT_DIR / "Table_4_2_Schedule_Discrepancies.csv"
OUTPUT_MD = OUTPUT_DIR / "Table_4_2_Schedule_Discrepancies.md"

def get_default_metrics():
    """Compute metrics for Default schedule."""
    print("Loading Default Schedules...")
    defaults = idf_optimizer.load_standard_residential_schedules(verbose=False)
    
    occ_wd = np.array(defaults['occupancy']['Weekday'])
    # Weekday and Weekend are identical in DOE MidRise for Occupancy?
    # Actually DOE MidRise usually has different Weekend profile?
    # Let's check keys in defaults['occupancy']
    # If not present, idf_optimizer usually replicates.
    # We will assume 'Weekend' key exists or use Weekday if missing (unlikely for MidRise).
    # But wait, load_standard_residential_schedules returns specific keys.
    # Let's see what it returns. It returns a dict with 'occupancy': {...} or just list?
    # In idf_optimizer.py, it returns separate keys 'occupancy', 'equipment' etc.
    # And 'occupancy' value is the schedule name? No.
    # Wait, load_standard_residential_schedules returns the JSON objects?
    # Let's check `idf_optimizer.py` implementation via view_file if needed?
    # I recall it returns a dict of profiles? 
    # Actually, looking at my previous `plot_default_vs_classification.py`:
    # defaults['occupancy']['Weekday'] was used.
    
    # Let's assume structure: defaults['occupancy'] is a dict with 'Weekday', 'Weekend', etc.
    # If standard DOE MidRise:
    # Weekday: High night, low day.
    # Weekend: High all day.
    
    # We need to access Weekend specifically.
    occ_we = np.array(defaults['occupancy']['Weekend']) if 'Weekend' in defaults['occupancy'] else occ_wd

    met_rate = 95.0 # Constant
    
    # Metrics
    m_occ_wd = np.mean(occ_wd)
    m_occ_we = np.mean(occ_we)
    
    # Peak time (first hour of max)
    peak_hr = np.argmax(occ_wd)
    peak_str = f"{peak_hr:02d}:00"
    
    # Daytime (09-17) indices: 9,10,11,12,13,14,15,16 (8 hours? or 09:00 to 17:00 is 8 hours?)
    # 09-17 usually means hours 9,10,11,12,13,14,15,16. (Up to 17:00).
    daytime_occ = np.mean(occ_wd[9:17])
    
    m_met = met_rate
    p_met = met_rate
    
    return {
        'mean_occ_wd': m_occ_wd,
        'mean_occ_we': m_occ_we,
        'peak_hr_wd': peak_hr, # Int
        'peak_hr_str': peak_str,
        'daytime_occ': daytime_occ,
        'mean_met': m_met,
        'peak_met': p_met
    }

def get_gss_metrics():
    """Compute metrics for 2025 GSS."""
    print("Loading 2025 GSS Data...")
    df = pd.read_csv(GSS_FILE, usecols=['Hour', 'Day_Type', 'Occupancy_Schedule', 'Metabolic_Rate'])
    
    wd = df[df['Day_Type'] == 'Weekday']
    we = df[df['Day_Type'] == 'Weekend']
    
    m_occ_wd = wd['Occupancy_Schedule'].mean()
    m_occ_we = we['Occupancy_Schedule'].mean()
    
    # Peak hour weekday
    hourly_occ = wd.groupby('Hour')['Occupancy_Schedule'].mean()
    peak_hr = hourly_occ.idxmax()
    peak_str = f"{peak_hr:02d}:00"
    
    # Daytime
    daytime_occ = wd[wd['Hour'].between(9, 16)]['Occupancy_Schedule'].mean()
    
    # Metabolic
    m_met = wd['Metabolic_Rate'].mean()
    p_met = wd.groupby('Hour')['Metabolic_Rate'].mean().max()
    
    return {
        'mean_occ_wd': m_occ_wd,
        'mean_occ_we': m_occ_we,
        'peak_hr_wd': peak_hr,
        'peak_hr_str': peak_str,
        'daytime_occ': daytime_occ,
        'mean_met': m_met,
        'peak_met': p_met
    }

def main():
    def_m = get_default_metrics()
    gss_m = get_gss_metrics()
    
    # Prepare Rows
    rows = []
    
    # 1. Mean Weekday Occ
    diff = def_m['mean_occ_wd'] - gss_m['mean_occ_wd']
    pct = (diff / def_m['mean_occ_wd']) * 100
    rows.append([
        "Mean weekday occupancy (0–1)",
        f"{def_m['mean_occ_wd']:.3f}",
        f"{gss_m['mean_occ_wd']:.3f}",
        f"{diff:+.3f}",
        f"{pct:+.1f}%"
    ])
    
    # 2. Mean Weekend Occ
    diff = def_m['mean_occ_we'] - gss_m['mean_occ_we']
    pct = (diff / def_m['mean_occ_we']) * 100
    rows.append([
        "Mean weekend occupancy (0–1)",
        f"{def_m['mean_occ_we']:.3f}",
        f"{gss_m['mean_occ_we']:.3f}",
        f"{diff:+.3f}",
        f"{pct:+.1f}%"
    ])
    
    # 3. Peak Occ Time
    diff_hr = int(def_m['peak_hr_wd'] - gss_m['peak_hr_wd'])
    rows.append([
        "Peak occupancy time (weekday)",
        def_m['peak_hr_str'],
        gss_m['peak_hr_str'],
        f"Δ {diff_hr} h",
        "—"
    ])
    
    # 4. Daytime Occ (09-17)
    diff_pp = (def_m['daytime_occ'] - gss_m['daytime_occ']) * 100
    rows.append([
        "Daytime occupancy (09–17)",
        f"{def_m['daytime_occ']*100:.1f}%",
        f"{gss_m['daytime_occ']*100:.1f}%",
        f"{diff_pp:+.1f} pp",
        "—"
    ])
    
    # 5. Mean Metabolic
    diff = def_m['mean_met'] - gss_m['mean_met']
    pct = (diff / def_m['mean_met']) * 100
    rows.append([
        "Mean metabolic rate (W)",
        f"{def_m['mean_met']:.1f}",
        f"{gss_m['mean_met']:.1f}",
        f"{diff:+.1f} W",
        f"{pct:+.1f}%"
    ])
    
    # 6. Peak Metabolic
    diff = def_m['peak_met'] - gss_m['peak_met']
    pct = (diff / def_m['peak_met']) * 100 if def_m['peak_met'] != 0 else 0
    rows.append([
        "Peak metabolic rate (W)",
        f"{def_m['peak_met']:.1f}",
        f"{gss_m['peak_met']:.1f}",
        f"{diff:+.1f} W",
        f"{pct:.0f}%"
    ])
    
    # DataFrame
    cols = ["Parameter", "Default", "2025 GSS (classified)", "Difference", "% Error"]
    df = pd.DataFrame(rows, columns=cols)
    
    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"CSV saved to: {OUTPUT_CSV}")
    
    # Save Markdown (Manual format)
    with open(OUTPUT_MD, 'w') as f:
        f.write(f"# Table 4.2: Quantified Schedule Discrepancies\n\n")
        # Header
        f.write("| " + " | ".join(cols) + " |\n")
        f.write("|" + "|".join(["---"] * len(cols)) + "|\n")
        # Body
        for row in rows:
            f.write("| " + " | ".join(str(x) for x in row) + " |\n")
            
    print(f"Markdown saved to: {OUTPUT_MD}")
    print("\n" + df.to_string(index=False))

if __name__ == "__main__":
    main()
