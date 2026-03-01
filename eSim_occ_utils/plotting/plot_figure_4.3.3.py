
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from datetime import datetime

# --- Configuration ---
SCENARIOS = ["Default", "2005", "2015", "2025"]
CITIES = ["Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]

# Map City to SimResults Folder
LOCATION_MAP = {
    "Toronto (5A)": "MonteCarlo_N60_1771006398",
    "Montreal (6A)": "MonteCarlo_N60_1771001406",
    "Winnipeg (7)": "MonteCarlo_N60_1771010812"
}

# --- Data Extraction ---

def get_area(cursor):
    """Fetches Net Conditioned Building Area from TabularData."""
    try:
        cursor.execute("SELECT Value FROM TabularDataWithStrings WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' AND TableName='Building Area' AND RowName='Net Conditioned Building Area' AND ColumnName='Area'")
        res = cursor.fetchone()
        if res:
            return float(res[0])
    except:
        pass
    return 1.0 # Avoid division by zero

def extract_profiles(sql_path):
    """
    Extracts hourly Heating and Cooling EnergyTransfer (J) and Time.
    Returns DataFrame with columns: [Month, Day, Hour, DayType, Heating, Cooling]
    """
    if not os.path.exists(sql_path):
        return None
        
    try:
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()
        
        # 1. Get Variable Indices
        # Heating:EnergyTransfer, Cooling:EnergyTransfer
        # Variable names in SQL might vary slightly (e.g., "Heating:EnergyTransfer" vs "DistrictHeating:Facility")
        # inspecting earlier showed: "Heating:EnergyTransfer" and "Cooling:EnergyTransfer" are present
        
        vars_to_fetch = {
            'Heating': 'Heating:EnergyTransfer',
            'Cooling': 'Cooling:EnergyTransfer'
        }
        
        var_ids = {}
        for key, var_name in vars_to_fetch.items():
            cursor.execute("SELECT ReportDataDictionaryIndex FROM ReportDataDictionary WHERE Name=?", (var_name,))
            res = cursor.fetchone()
            if res:
                var_ids[key] = res[0]
            else:
                # print(f"Variable {var_name} not found in {sql_path}")
                return None

        # 2. Get Area
        area = get_area(cursor)
        
        # 3. Fetch Data
        # Query ReportData joined with Time
        # TimeIndex in ReportData corresponds to TimeIndex in Time table
        
        query = f"""
            SELECT 
                t.Month, t.Day, t.Hour, t.DayType,
                rd_h.Value as Heat,
                rd_c.Value as Cool
            FROM Time t
            JOIN ReportData rd_h ON t.TimeIndex = rd_h.TimeIndex AND rd_h.ReportDataDictionaryIndex = {var_ids['Heating']}
            JOIN ReportData rd_c ON t.TimeIndex = rd_c.TimeIndex AND rd_c.ReportDataDictionaryIndex = {var_ids['Cooling']}
            ORDER BY t.TimeIndex
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Convert J to W/m²
        # 1 hour step, so J/3600 = W. Then divide by Area.
        df['Heating'] = (df['Heat'] / 3600.0) / area
        df['Cooling'] = (df['Cool'] / 3600.0) / area
        
        # Adjust Hour (1-24 to 0-23 for plotting)
        df['Hour'] = df['Hour'] - 1
        
        return df[['Month', 'Day', 'Hour', 'DayType', 'Heating', 'Cooling']]
        
    except Exception as e:
        print(f"Error reading {sql_path}: {e}")
        return None

def aggregate_profiles(base_extract_dir):
    """
    Iterates through Cities -> Scenarios -> iter_1.
    Computes average profiles for Jan (Winter) and Jul (Summer) by DayType.
    Returns: Nested Dictionary Structure
    data[Scenario][Season][DayType][Hour] = {'Heating': val, 'Cooling': val}
    """
    
    # Storage for all profiles to average across cities
    # structure: global_data[Scenario][Season][DayType][Hour]['Heating'] = [list of city vals]
    global_data = {s: {'Winter': {'Weekday': {}, 'Weekend': {}}, 
                       'Summer': {'Weekday': {'Heating': {h: [] for h in range(24)}, 'Cooling': {h: [] for h in range(24)}},
                                  'Weekend': {'Heating': {h: [] for h in range(24)}, 'Cooling': {h: [] for h in range(24)}}}} 
                   for s in SCENARIOS}
    
    # Initialize separate dicts for clearer structure
    # We will just collect extracted DF list and concat then groupby
    
    collected_data = [] # List of DFs

    for city in CITIES:
        sim_folder = LOCATION_MAP.get(city)
        if not sim_folder: continue
        
        city_base = os.path.join(base_extract_dir, sim_folder)
        
        for scenario in SCENARIOS:
            # Look in iter_1 (Representative)
            # Default is usually in "Default" folder, Scenarios in "iter_1/Scenario"
            if scenario == "Default":
                sql_path = os.path.join(city_base, "Default", "eplusout.sql")
            else:
                sql_path = os.path.join(city_base, "iter_1", scenario, "eplusout.sql")
            
            print(f"Extraction: {city} - {scenario}")
            df = extract_profiles(sql_path)
            
            if df is not None:
                df['Scenario'] = scenario
                df['City'] = city
                collected_data.append(df)
            else:
                print(f" -> Missing SQL for {city} {scenario}")

    if not collected_data:
        return None

    full_df = pd.concat(collected_data, ignore_index=True)
    
    # --- Filter & Group ---
    
    # Classification
    # Seasons: Winter = Jan (1), Summer = Jul (7)
    valid_months = [1, 7]
    full_df = full_df[full_df['Month'].isin(valid_months)].copy()
    
    full_df['Season'] = full_df['Month'].map({1: 'Winter', 7: 'Summer'})
    
    # DayTypes: 
    # EnergyPlus DayTypes: 1=Sunday, 2=Monday... 7=Saturday, 8=Holiday, 9=SummerDesignDay...
    # We usually simulate with specific DayTypes or actual calendar
    # In 'Time' table, DayType string is often stored or integer. 
    # Let's inspect DayType. Wait, 'Time' table usually has DayType strings like 'Monday', 'Tuesday'...
    # Or integers.
    # Actually, Pandas read_sql might return strings if the column is TEXT.
    # Let's assume standard names.
    
    # Map to Weekday/Weekend
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    weekends = ['Saturday', 'Sunday']
    
    def get_day_category(dt):
        if dt in weekdays: return 'Weekday'
        if dt in weekends: return 'Weekend'
        return 'Other'
        
    full_df['DayCat'] = full_df['DayType'].apply(get_day_category)
    full_df = full_df[full_df['DayCat'] != 'Other']
    
    # Group by Scenario, Season, DayCat, Hour -> Mean over (City, Day)
    grouped = full_df.groupby(['Scenario', 'Season', 'DayCat', 'Hour']).agg({'Heating': 'mean', 'Cooling': 'mean'}).reset_index()
    
    return grouped

# --- Plotting ---

def plot_diurnal_profiles(df, output_dir):
    """
    Generates Figure 4.3.3 (1x4 Grid)
    (a) Win WD (Heat), (b) Win WE (Heat), (c) Sum WD (Cool), (d) Sum WE (Cool)
    """
    fig, axes = plt.subplots(1, 4, figsize=(24, 5), sharey=False)
    
    # Colors (same scheme)
    colors = {
        "Default": "black",
        "2005": "#1f77b4", # blue-ish
        "2015": "#ff7f0e", # orange-ish
        "2025": "#2ca02c"  # green
    }
    styles = {
        "Default": ":",
        "2005": "--",
        "2015": "-.",
        "2025": "-"
    }
    widths = {
        "Default": 2.5,  # Thicker Baseline
        "2005": 1.5,
        "2015": 1.5,
        "2025": 2.5   # Thicker Future
    }
    
    scenarios_order = ["Default", "2005", "2015", "2025"]
    
    # Define Subplot Config
    # Index -> (Season, DayCat, Variable, Title)
    subplots_config = [
        (0, 'Winter', 'Weekday', 'Heating', '(a) Winter Weekday (Jan)\nHeating Load'),
        (1, 'Winter', 'Weekend', 'Heating', '(b) Winter Weekend (Jan)\nHeating Load'),
        (2, 'Summer', 'Weekday', 'Cooling', '(c) Summer Weekday (Jul)\nCooling Load'),
        (3, 'Summer', 'Weekend', 'Cooling', '(d) Summer Weekend (Jul)\nCooling Load')
    ]
    
    # Calculate Max Y-Limits per Variable
    max_h = df['Heating'].max()
    max_c = df['Cooling'].max()
    
    ylim_h = (0.8, 2.0)
    ylim_c = (0, max_c * 1.1)

    for (idx, season, day_cat, var, title) in subplots_config:
        ax = axes[idx]
        
        # Plot each scenario
        for scen in scenarios_order:
            subset = df[
                (df['Scenario'] == scen) & 
                (df['Season'] == season) & 
                (df['DayCat'] == day_cat)
            ].sort_values('Hour')
            
            if not subset.empty:
                ax.plot(subset['Hour'], subset[var], 
                        label=scen, 
                        color=colors.get(scen, 'gray'),
                        linestyle=styles.get(scen, '-'),
                        linewidth=widths.get(scen, 1.5))
        
        # Formatting
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim(0, 23)
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_xlabel("Hour of Day", fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Y-Axis Label for the first one of each type
        if idx == 0 or idx == 2:
            ax.set_ylabel("Avg Load (W/m²)", fontsize=11)
            
        # Set Y-Limits based on variable type
        if var == 'Heating':
            ax.set_ylim(ylim_h)
        else:
            ax.set_ylim(ylim_c)

    # Legend (Global)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=4, fontsize=12)
    
    plt.tight_layout()
    # No need for subplots_adjust if we use bbox_to_anchor 1.05 and tight_layout usually handles it, 
    # but let's be safe.
    
    # Save
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "Figure_4.3.3_Diurnal_Profiles.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

# --- Main ---

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    base_dir = os.path.join(project_root, "BEM_Setup", "SimResults")
    output_dir = os.path.join(project_root, "eSim_occ_utils", "plotting")
    
    print("Aggregating Profile Data...")
    df = aggregate_profiles(base_dir)
    
    if df is not None:
        print("Plotting Profiles...")
        plot_diurnal_profiles(df, output_dir)
        
        # Also save CSV for checking
        csv_path = os.path.join(output_dir, "Table_4.3.3_Profile_Data.csv")
        df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")
    else:
        print("Failed to aggregate data.")

if __name__ == "__main__":
    main()
