
import pandas as pd
import os
import glob
import sys

# Define paths
base_dir = "BEM_Setup"
files = {
    '2005': "BEM_Schedules_2005.csv",
    '2015': "BEM_Schedules_2015.csv",
    '2025': "BEM_Schedules_2025.csv"
}

print("=== Occupancy Statistics Report ===")

for year, filename in files.items():
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        print(f"{year}: File not found at {path}")
        continue
        
    try:
        # Load CSV
        # Use simple read_csv, assuming headers are correct as verified
        df = pd.read_csv(path)
        
        # Check integrity
        if 'Occupancy_Schedule' not in df.columns:
            print(f"{year}: Missing 'Occupancy_Schedule' column")
            continue
            
        # Basic Stats across all rows (simplest metric)
        mean_occ = df['Occupancy_Schedule'].mean()
        zeros = (df['Occupancy_Schedule'] == 0).mean() * 100
        
        print(f"\nYear: {year}")
        print(f"  Total Rows: {len(df)}")
        print(f"  Unique Households: {df['SIM_HH_ID'].nunique()}")
        print(f"  Average Occupancy (Global): {mean_occ:.4f}")
        print(f"  % Zero Occupancy Hours: {zeros:.2f}%")
        
        # Weekday 8am-5pm specific stats (Working hours)
        working_hours = df[
            (df['Day_Type'] == 'Weekday') & 
            (df['Hour'] >= 8) & 
            (df['Hour'] <= 16)
        ]
        if not working_hours.empty:
            work_mean = working_hours['Occupancy_Schedule'].mean()
            print(f"  Avg Occupancy (Weekday 8am-4pm): {work_mean:.4f}")

        # Weekend Stats
        weekend_rows = df[df['Day_Type'] == 'Weekend']
        if not weekend_rows.empty:
            weekend_mean = weekend_rows['Occupancy_Schedule'].mean()
            print(f"  Avg Occupancy (Weekend): {weekend_mean:.4f}")
        else:
            print("  WARNING: No 'Weekend' rows found!")

        # Check for fractional vs binary
        unique_vals = df['Occupancy_Schedule'].unique()
        binary = all(x in [0.0, 1.0] for x in unique_vals[:100]) # approximate check
        print(f"  Values appear binary (0/1): {binary}")

            
    except Exception as e:
        print(f"{year}: Error analyzing - {e}")

print("\n=== End Report ===")
