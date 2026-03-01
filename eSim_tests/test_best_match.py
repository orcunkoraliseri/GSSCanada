
import os
import sys
import pandas as pd
import numpy as np
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eSim_bem_utils import integration

# Target "Standard Working Day" Profile (Matches integration.py)
TARGET_WORKING_PROFILE = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5,  # 0-7: Home (Sleep/Wake)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # 8-15: Away (Work)
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5   # 16-23: Home (Evening)
]

def analyze_best_match():
    base_dir = "BEM_Setup"
    files = {
        '2005': "BEM_Schedules_2005.csv",
        '2015': "BEM_Schedules_2015.csv",
        '2025': "BEM_Schedules_2025.csv"
    }
    
    print("=== Best Match Selection Analysis ===")
    print("Target Profile: Standard Working Day (Away 8am-4pm)")
    
    for year, filename in files.items():
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            continue
            
        print(f"\n--- {year} ---")
        # Load schedules using integration.load_schedules (reuses logic)
        # Note: limiting to 1 dwelling type to speed up? Let's just load first 1000 rows?
        # load_schedules reads whole file. It's fast enough (~50MB).
        schedules = integration.load_schedules(path)
        
        # 1. Calculate Average Occupancy of the "Population"
        all_weekday_means = []
        for hh_id, data in schedules.items():
            if 'Weekday' in data:
                occ = [x['occ'] for x in data['Weekday']]
                all_weekday_means.append(sum(occ)/24.0)
        
        pop_mean = sum(all_weekday_means) / len(all_weekday_means) if all_weekday_means else 0
        print(f"Population Mean Occupancy: {pop_mean:.4f}")
        
        # 2. Find Best Match
        best_hh = integration.find_best_match_household(schedules)
        print(f"Selected Best Match HH: {best_hh}")
        
        # 3. Analyze Selected Household
        if best_hh and 'Weekday' in schedules[best_hh]:
            profile = schedules[best_hh]['Weekday']
            occ_vals = [x['occ'] for x in profile]
            
            sel_mean = sum(occ_vals)/24.0
            print(f"Selected HH Mean Occupancy: {sel_mean:.4f}")
            
            # Print profile (simplified)
            print(f"Profile: {['%.2f' % x for x in occ_vals]}")
            
            # Compare
            diff = sel_mean - pop_mean
            print(f"Difference from Pop Mean: {diff:.4f}")
            
            # Check zeros
            zeros = len([x for x in occ_vals if x < 0.1])
            print(f"Hours Absent (<0.1): {zeros}")
            
            # Evening Stats (Significance for Lighting)
            # 17:00 to 23:00 (Hours 17-23)
            evening_vals = occ_vals[17:24]
            evening_mean = sum(evening_vals) / len(evening_vals)
            print(f"Evening Mean Occupancy (17-23h): {evening_mean:.4f}")

            
        else:
            print("Could not analyze selected household.")

if __name__ == "__main__":
    analyze_best_match()
