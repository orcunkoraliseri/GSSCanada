import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import calendar

# --- Configuration ---
SCENARIOS = ["Default", "2005", "2015", "2025"]
# We use Toronto as the representative for peak timing analysis
CITY = "Toronto (5A)"
CITY_FOLDER = "MonteCarlo_N60_1771006398"

# --- Helpers ---

# --- Helpers ---

def get_conditioned_area_from_zones(cursor):
    """
    Calculates Conditioned Floor Area by summing areas of conditioned zones.
    Excludes Garage, Attic, Plenum.
    """
    try:
        cursor.execute("SELECT ZoneName, FloorArea, Multiplier FROM Zones")
        rows = cursor.fetchall()
        
        total_area = 0.0
        
        for row in rows:
            name = row[0].upper()
            area = float(row[1])
            mult = float(row[2])
            
            # Simple heuristic for Conditioned Zones
            if "GARAGE" in name: continue
            if "ATTIC" in name: continue
            if "PLENUM" in name: continue
            
            # Use Multiplier if it exists (though usually 1 for modeled zones)
            total_area += area * mult
            
        if total_area > 0:
            return total_area
    except Exception as e:
        print(f"Error calculating area from Zones: {e}")
        
    return 1.0 # Fallback

def format_timestamp(month, day, hour):
    """Formats month index, day, hour into MMM DD HH:00"""
    month_str = calendar.month_name[int(month)][:3]
    return f"{month_str} {int(day):02d} {int(hour):02d}:00"

def extract_peak_data(sql_path):
    """
    Extracts peak heating and cooling loads (sum of all zones) and their timestamps.
    Normalized by Conditioned Floor Area of the modeled zones.
    """
    if not os.path.exists(sql_path):
        return None
        
    try:
        conn = sqlite3.connect(sql_path)
        
        # 1. Get Conditioned Area (Modeled only)
        area = get_conditioned_area_from_zones(conn.cursor())
        # print(f"DEBUG: Using Conditioned Area = {area:.2f} m² for normalization.")
        
        # 2. Variable Mapping
        vars_to_fetch = {
            'Heating': 'Zone Air System Sensible Heating Energy',
            'Cooling': 'Zone Air System Sensible Cooling Energy'
        }
        
        peaks = {}
        
        for key, var_name in vars_to_fetch.items():
            # Find all indices for this variable (all zones)
            query_ids = f"SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name='{var_name}'"
            ids_df = pd.read_sql_query(query_ids, conn)
            
            if ids_df.empty:
                # Fallback to older names if needed, but usually consistent
                print(f"Warning: No variables found for {var_name}")
                return None
            
            ids_list = ",".join(map(str, ids_df['ReportDataDictionaryIndex'].tolist()))
            
            # Query all data for these indices
            # Group by TimeIndex to sum across ALL zones (including semi-conditioned like Garage/Attic if they have load)
            query_data = f"""
                SELECT 
                    rd.TimeIndex, SUM(rd.Value) as TotalValue
                FROM ReportData rd
                WHERE rd.ReportDataDictionaryIndex IN ({ids_list})
                GROUP BY rd.TimeIndex
                ORDER BY TotalValue DESC
                LIMIT 1
            """
            
            # Fetch Peak
            peak_row = pd.read_sql_query(query_data, conn)
            
            if peak_row.empty:
                return None
                
            peak_val = peak_row.iloc[0]['TotalValue']
            peak_time_index = peak_row.iloc[0]['TimeIndex']
            
            # Get Timestamp details
            query_time = f"SELECT Month, Day, Hour FROM Time WHERE TimeIndex={peak_time_index}"
            time_row = pd.read_sql_query(query_time, conn)
            m, d, h = time_row.iloc[0]['Month'], time_row.iloc[0]['Day'], time_row.iloc[0]['Hour']
            
            # Convert J to W/m2 (J / 3600 / area)
            peak_power = (peak_val / 3600.0) / area
            
            timestamp = format_timestamp(m, d, h-1) # Subtract 1 to match 0-23
            
            peaks[key] = {
                'Value': peak_power,
                'Time': timestamp
            }
            
        conn.close()
        return peaks
        
    except Exception as e:
        print(f"Error reading {sql_path}: {e}")
        return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    base_dir = os.path.join(project_root, "BEM_Setup", "SimResults", CITY_FOLDER)
    output_dir = os.path.join(project_root, "eSim_occ_utils", "plotting")
    
    results = []
    
    print(f"Analyzing Peak Loads for {CITY}...")
    
    for scenario in SCENARIOS:
        if scenario == "Default":
            sql_path = os.path.join(base_dir, "Default", "eplusout.sql")
        else:
            sql_path = os.path.join(base_dir, "iter_1", scenario, "eplusout.sql")
            
        peaks = extract_peak_data(sql_path)
        
        if peaks:
            results.append({
                "Scenario": scenario,
                "Peak Heating (W/m²)": peaks['Heating']['Value'], # Keep as float for plotting
                "Time (Heating)": peaks['Heating']['Time'],
                "Peak Cooling (W/m²)": peaks['Cooling']['Value'],
                "Time (Cooling)": peaks['Cooling']['Time']
            })
        else:
            print(f" -> Failed to extract peaks for {scenario}")

    if results:
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save CSV (Format floats for display)
        df_display = df.copy()
        df_display["Peak Heating (W/m²)"] = df_display["Peak Heating (W/m²)"].map('{:.2f}'.format)
        df_display["Peak Cooling (W/m²)"] = df_display["Peak Cooling (W/m²)"].map('{:.2f}'.format)
        
        print("\nTable 4.3.4: Peak Heating and Cooling Loads")
        print(df_display.to_string(index=False))
        
        csv_path = os.path.join(output_dir, "Table_4.3.4_Peak_Loads.csv")
        df_display.to_csv(csv_path, index=False)
        print(f"\nTable saved to: {csv_path}")
        
        # Plot Figure
        plot_peak_loads(df, output_dir)

def plot_peak_loads(df, output_dir):
    """Generates Figure 4.3.4 (1x2 Subplots: Heating Left, Cooling Right)"""
    scenarios = df["Scenario"]
    heating = df["Peak Heating (W/m²)"].astype(float)
    cooling = df["Peak Cooling (W/m²)"].astype(float)
    
    x = np.arange(len(scenarios))
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    
    # Subplot 1: Heating
    ax_h = axes[0]
    bars_h = ax_h.bar(x, heating, color='#d62728', alpha=0.6)
    ax_h.set_title('(a) Peak Heating Load', fontsize=12, fontweight='bold')
    ax_h.set_ylabel('Peak Load (W/m²)', fontsize=11)
    ax_h.set_xticks(x)
    ax_h.set_xticklabels(scenarios, rotation=0)
    ax_h.set_ylim(0, heating.max() * 1.15) # Headroom
    ax_h.grid(axis='y', linestyle='--', alpha=0.5)

    # Subplot 2: Cooling
    ax_c = axes[1]
    bars_c = ax_c.bar(x, cooling, color='#1f77b4', alpha=0.6)
    ax_c.set_title('(b) Peak Cooling Load', fontsize=12, fontweight='bold')
    ax_c.set_ylabel('Peak Load (W/m²)', fontsize=11)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(scenarios, rotation=0)
    ax_c.set_ylim(0, cooling.max() * 1.15) # Headroom
    ax_c.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Annotate Function
    def autolabel(ax, rects, times):
        for rect, time_str in zip(rects, times):
            # Extract Month Day from "MMM DD HH:00"
            parts = time_str.split(' ')
            month_day = f"{parts[0]} {parts[1]}"
            height = rect.get_height()
            
            # 1. Date on the center of the bar
            ax.annotate(month_day,
                        xy=(rect.get_x() + rect.get_width() / 2, height / 2),
                        ha='center', va='center', fontsize=12, color='white', fontweight='bold')
            
            # 2. Peak Load + Unit on top of the bar
            ax.annotate(f'{height:.2f} W/m²',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    autolabel(ax_h, bars_h, df["Time (Heating)"])
    autolabel(ax_c, bars_c, df["Time (Cooling)"])
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, "Figure_4.3.4_Peak_Loads.png")
    plt.savefig(output_path, dpi=300)
    print(f"Figure saved to: {output_path}")

if __name__ == "__main__":
    main()
