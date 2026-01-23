import pandas as pd
import matplotlib.pyplot as plt
import os

def inspect_hh_2189():
    base_dir = "/Users/orcunkoraliseri/Desktop/Postdoc/eSim/BEM_Setup"
    years = ['2005', '2015', '2025']
    found_year = None
    hh_data = pd.DataFrame()
    
    for year in years:
        csv_path = os.path.join(base_dir, f"BEM_Schedules_{year}.csv")
        print(f"Loading {csv_path}...")
        try:
            df = pd.read_csv(csv_path)
            res = df[df['SIM_HH_ID'] == 2189]
            if not res.empty:
                print(f"Found HH 2189 in {year} data ({len(res)} rows).")
                hh_data = res.copy()
                found_year = year
                break
        except Exception as e:
            print(f"Error loading {year}: {e}")

    if hh_data.empty:
        print("HH 2189 not found in ANY year!")
        return
        
    print(f"Analyzing HH 2189 from {found_year}...")
    
    profile = hh_data.groupby('Hour')['Occupancy_Schedule'].mean()
    
    # Default Water Profile (from integration.py)
    default_water = [
        0.05, 0.05, 0.05, 0.05, 0.1, 0.3, 0.5, 0.4, 0.2, 0.1,
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.4,
        0.3, 0.2, 0.1, 0.05
    ]
    
    # Default Light Profile
    default_light = [
        0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.3, 0.2,
        0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.7, 0.9, 0.9,
        0.8, 0.6, 0.4, 0.2
    ]

    # Plot
    plt.figure(figsize=(10, 6))
    
    # Plot Occupancy
    plt.plot(profile.index, profile.values, 'g-', linewidth=2, label='HH 2189 Occupancy (2005)')
    plt.fill_between(profile.index, 0, profile.values, color='green', alpha=0.1)
    
    # Plot Defaults
    plt.plot(range(24), default_water, 'b--', label='Default Water Profile')
    plt.plot(range(24), default_light, 'r--', label='Default Light Profile')
    
    # Highlight Coincidence
    # If Occupancy > 0.3, Active Floor applies.
    # Water Active Floor was 0.05 (now 0.01), but user asked about previous result.
    # Previous result used 0.05.
    
    plt.title("HH 2189 (2005) Occupancy vs Default Profiles")
    plt.xlabel("Hour of Day")
    plt.ylabel("Fraction")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = "debug_hh_2189_analysis.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")

if __name__ == "__main__":
    inspect_hh_2189()
