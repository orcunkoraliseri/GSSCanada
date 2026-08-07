import pandas as pd
import os
import glob

def analyze_tus_stats():
    # Define paths to Occupancy CSVs
    base_dir = "0_Occupancy/Outputs"
    
    # We need to find where the actual TUS data is stored. 
    # Based on previous context, it seems to be in subfolders like 0_Occupancy/Outputs_05CEN05GSS/ ...
    
    years = ['2005', '2015', '2025']
    stats = {}
    
    print("Analyzing TUS Occupancy Statistics...\n")
    
    for year in years:
        # Search for the residential occupancy CSV
        # It's usually named something like 'Occupancy_Census_2005_...csv ' or similar
        search_pattern = f"0_Occupancy/Outputs_*/*{year}*.csv"
        files = glob.glob(search_pattern)
        
        # Filter for the main aggregated file if possible
        # Or just pick the first likely candidate. 
        # Let's try to be specific if we can find the specific file structure.
        
        if '2005' in year:
            search_path = "0_Occupancy/Outputs_06CEN05GSS/HH_aggregation/06CEN05GSS_Full_Aggregated_sample5pct.csv"
        elif '2015' in year:
            search_path = "0_Occupancy/Outputs_16CEN15GSS/HH_aggregation/16CEN15GSS_Full_Aggregated_sample5pct.csv"
        elif '2025' in year:
            # Assuming similar structure for 2025
            search_path = "0_Occupancy/Outputs_24CEN25GSS/HH_aggregation/24CEN25GSS_Full_Aggregated_sample5pct.csv"
            
        if not os.path.exists(search_path):
            # Try finding via glob if exact path is wrong
            potential_files = glob.glob(f"0_Occupancy/Outputs_*{year}*/{year}*_Residential_Occupancy.csv")
            if potential_files:
                search_path = potential_files[0]
            else:
                # Try broader search
                potential_files = glob.glob(f"0_Occupancy/Outputs_*{year}*/*.csv")
                # Filter out obvious non-data files
                potential_files = [f for f in potential_files if "Occupancy" in f and "Validation" not in f]
                if potential_files:
                    search_path = potential_files[0]
                else:
                    print(f"[{year}] Could not find occupancy file.")
                    continue
        
        print(f"[{year}] Loading: {search_path}")
        
        try:
            df = pd.read_csv(search_path)
            
            # Long-format processing
            if 'occPre' not in df.columns:
                 print(f"  Warning: 'occPre' column not found in {search_path}")
                 print(f"  Available columns: {df.columns.tolist()[:10]}...")
                 continue
                 
            # 'occPre' appears to be the presence indicators (0 or 1, or density?)
            # Based on head output: 0 means absent.
            
            vals = df['occPre'].values
            
            # Mean Occupancy Value (Raw)
            mean_occ_val = vals.mean()
            
            # Active Time Fraction (Presence > 0.3)
            # If occPre is binary (0/1), this is the same as mean.
            # If occPre is people count, this is fraction with at least 1 person?
            # Assuming occPre is the relevant "Presence" metric.
            
            active_fraction = (vals > 0.3).mean()
            
            # Active Hours per day
            active_hours = active_fraction * 24
            
            stats[year] = {
                'Mean Occupancy': mean_occ_val,
                'Active Fraction': active_fraction,
                'Active Hours/Day': active_hours
            }
            
            print(f"  Mean Occupancy Value: {mean_occ_val:.3f}")
            print(f"  Active Fraction (>0.3): {active_fraction:.3f}")
            print(f"  Avg Active Hours/Day: {active_hours:.2f} hrs")
            print("-" * 30)
            
        except Exception as e:
            print(f"  Error processing file: {e}")

    print("\n--- Comparative Summary ---")
    for year, data in stats.items():
        print(f"{year}: {data['Active Hours/Day']:.2f} active hours/day")

if __name__ == "__main__":
    analyze_tus_stats()
