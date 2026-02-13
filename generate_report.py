import os
import sqlite3
import pandas as pd
import numpy as np
import scipy.stats as stats
import glob
import re

# Use statsmodels if available, otherwise skip advanced stats or implement manually
try:
    import statsmodels.stats.multicomp as mc
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# Paths
base_dir = r"BEM_Setup\SimResults\MonteCarlo_N5_1771005117"
report_csv = os.path.join(base_dir, "Quebec_Comparative_Analysis_Report.csv")

# Constants
KBTU_TO_KWH = 0.29307107
FT2_TO_M2 = 0.09290304

def get_total_energy(cursor, row_name):
    # Sum all energy sources for a given row
    cols = ['Electricity', 'Natural Gas', 'Propane', 'Fuel Oil No 1', 'Fuel Oil No 2', 
            'Coal', 'Diesel', 'Gasoline', 'Other Fuel 1', 'Other Fuel 2', 
            'District Cooling', 'District Heating Water', 'District Heating Steam']
    
    total_kwh = 0.0
    for col in cols:
        cursor.execute("SELECT Value, Units FROM TabularDataWithStrings WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' AND TableName='End Uses' AND RowName=? AND ColumnName=?", (row_name, col))
        res = cursor.fetchone()
        if res and res[0]:
            val = float(res[0])
            unit = res[1]
            
            if unit == 'kBtu':
                total_kwh += val * KBTU_TO_KWH
            elif unit == 'GJ':
                total_kwh += val * 277.778
            elif unit == 'J':
                total_kwh += val / 3600000.0
            elif unit == 'kWh':
                total_kwh += val
            else:
                pass
    return total_kwh

def get_area(cursor):
    # Net Conditioned Building Area
    cursor.execute("SELECT Value, Units FROM TabularDataWithStrings WHERE ReportName='AnnualBuildingUtilityPerformanceSummary' AND TableName='Building Area' AND RowName='Net Conditioned Building Area' AND ColumnName='Area'")
    res = cursor.fetchone()
    if res:
        val = float(res[0])
        unit = res[1]
        if unit == 'ft2':
            return val * FT2_TO_M2
        elif unit == 'm2':
            return val
    return 1.0 # Avoid div by zero

# 1. Determine Location Name
location_name = "Unknown" 
err_files = glob.glob(os.path.join(base_dir, "**", "eplusout.err"), recursive=True)
if err_files:
    try:
        with open(err_files[0], 'r', errors='ignore') as f:
            content = f.read()
            match = re.search(r'Weather File.*?([A-Z]{2,3})_([A-Z]{2})_([^\.]+)', content, re.IGNORECASE)
            if match:
                city_part = match.group(3).split('.')[0]
                location_name = city_part
    except:
        pass

if location_name == "Unknown":
    html_files = glob.glob(os.path.join(base_dir, "**", "eplustbl.htm"), recursive=True)
    if html_files:
        try:
            with open(html_files[0], 'r', errors='ignore') as f:
                content = f.read()
                match = re.search(r'Weather File.*?<td[^>]*>([^<]+)<', content)
                if match:
                    weather_info = match.group(1)
                    city_match = re.search(r'([A-Za-z]+)\.', weather_info)
                    if city_match:
                        location_name = city_match.group(1)
        except:
            pass

print(f"Detected Location: {location_name}")

# READ HOURLY AND PEAK PROFILES BEFORE OVERWRITING
hourly_lines = []
peak_lines = []
if os.path.exists(report_csv):
    try:
        with open(report_csv, 'r') as f:
            lines = f.readlines()
        
        in_hourly = False
        in_peak = False
        
        for line in lines:
            if "[SECTION] Hourly Load Profiles" in line:
                in_hourly = True
                in_peak = False
                hourly_lines.append(line.strip())
                continue
            if "[SECTION] Peak Load Characteristics" in line:
                in_hourly = False
                in_peak = True
                peak_lines.append(line.strip())
                continue
            
            if in_hourly:
                hourly_lines.append(line.strip())
            elif in_peak:
                peak_lines.append(line.strip())
                
    except Exception as e:
        print(f"Warning: Could not read existing report sections: {e}")


data = []

# Iterations
iter_dirs = glob.glob(os.path.join(base_dir, "iter_*"))
for iter_dir in iter_dirs:
    iter_num = int(os.path.basename(iter_dir).split("_")[1])
    
    for scenario in ["2005", "2015", "2025"]:
        sql_path = os.path.join(iter_dir, scenario, "eplusout.sql")
        if os.path.exists(sql_path):
            try:
                conn = sqlite3.connect(sql_path)
                c = conn.cursor()
                
                area = get_area(c)
                
                heating = get_total_energy(c, 'Heating') / area
                cooling = get_total_energy(c, 'Cooling') / area
                lighting = get_total_energy(c, 'Interior Lighting') / area
                equipment = get_total_energy(c, 'Interior Equipment') / area
                dhw = get_total_energy(c, 'Water Systems') / area
                
                conn.close()

                data.append({
                    "Iteration": iter_num,
                    "Scenario": scenario,
                    "Heating": heating,
                    "Cooling": cooling,
                    "Lighting": lighting,
                    "Equipment": equipment,
                    "DHW": dhw
                })
            except:
                pass

# Default
default_dir = os.path.join(base_dir, "Default")
if os.path.exists(os.path.join(default_dir, "eplusout.sql")):
    try:
        conn = sqlite3.connect(os.path.join(default_dir, "eplusout.sql"))
        c = conn.cursor()
        area = get_area(c)
        heating = get_total_energy(c, 'Heating') / area
        cooling = get_total_energy(c, 'Cooling') / area
        lighting = get_total_energy(c, 'Interior Lighting') / area
        equipment = get_total_energy(c, 'Interior Equipment') / area
        dhw = get_total_energy(c, 'Water Systems') / area
        conn.close()
        
        data.append({
            "Iteration": 1,
            "Scenario": "Default",
            "Heating": heating,
            "Cooling": cooling,
            "Lighting": lighting,
            "Equipment": equipment,
            "DHW": dhw
        })
    except:
        pass

df = pd.DataFrame(data)
print(f"Data Extraction Complete. Rows: {len(df)}")

# --- Report Generation ---
output_lines = []

# 1. Annual Energy Demand Metrics
output_lines.append("[SECTION] Annual Energy Demand Metrics (Aggregated)")
output_lines.append("Category,Scenario,Mean(kWh/m2),StdDev,CI_Lower,CI_Upper")

scenarios = ["2025", "2015", "2005", "Default"]
metrics = ["Heating", "Cooling", "Lighting", "Equipment", "DHW"]

for metric in metrics:
    for scen in scenarios:
        subset = df[df["Scenario"] == scen]
        vals = subset[metric].values
        if len(vals) == 0:
            continue
        
        mean_val = np.mean(vals)
        std_val = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
        
        # 95% CI
        if len(vals) > 1 and std_val > 0:
            ci = stats.t.interval(0.95, len(vals)-1, loc=mean_val, scale=stats.sem(vals))
            ci_lower, ci_upper = ci
        else:
            ci_lower, ci_upper = mean_val, mean_val
            
        output_lines.append(f"{metric},{scen},{mean_val:.4f},{std_val:.4f},{ci_lower:.4f},{ci_upper:.4f}")

output_lines.append("")

# 2. Statistical Variability
output_lines.append("[SECTION] Statistical Variability (Reference: Default)")
output_lines.append("Category,Comparison,P-Value,Significant?,Cohens_D")

for metric in metrics:
    # ANOVA (2005, 2015, 2025)
    anova_groups = []
    anova_labels = []
    for s in ["2005", "2015", "2025"]:
        v = df[df["Scenario"] == s][metric].values
        if len(v) > 0:
            anova_groups.append(v)
            anova_labels.extend([s]*len(v))
            
    if len(anova_groups) > 1:
         f_stat, p_val = stats.f_oneway(*anova_groups)
         sig = "Yes" if p_val < 0.05 else "No"
         output_lines.append(f"{metric},ANOVA (2005-2015-2025),{p_val:.5f},{sig},-")

    # Comparisons vs Default
    default_vals = df[df["Scenario"] == "Default"][metric].values
    if len(default_vals) > 0:
        default_mean = np.mean(default_vals)
        default_std = np.std(default_vals, ddof=1) if len(default_vals) > 1 else 0.0
        
        for scen in ["2025", "2015", "2005"]:
            scen_vals = df[df["Scenario"] == scen][metric].values
            if len(scen_vals) > 0:
                # T-test
                if default_std == 0:
                     t_stat, p_val = stats.ttest_1samp(scen_vals, default_mean)
                else:
                     t_stat, p_val = stats.ttest_ind(scen_vals, default_vals, equal_var=False)

                # Cohen's d
                scen_mean = np.mean(scen_vals)
                scen_std = np.std(scen_vals, ddof=1)
                
                if default_std == 0:
                     cohens_d = (scen_mean - default_mean) / scen_std if scen_std > 0 else 0
                else:
                     n1, n2 = len(scen_vals), len(default_vals)
                     s_pooled = np.sqrt(((n1 - 1) * scen_std**2 + (n2 - 1) * default_std**2) / (n1 + n2 - 2))
                     cohens_d = (scen_mean - default_mean) / s_pooled if s_pooled > 0 else 0
                
                sig = "Yes" if p_val < 0.05 else "No"
                output_lines.append(f"{metric},{scen} vs Default,{p_val:.5f},{sig},{cohens_d:.4f}")

output_lines.append("")

# 3. Raw Data
output_lines.append("[SECTION] Raw Simulation Data (Per Simulation)")
output_lines.append("Run_ID,Scenario,Heating,Cooling,Lighting,Equipment,DHW")
df_sorted = df.sort_values(by=["Scenario", "Iteration"])
for idx, row in df_sorted.iterrows():
    output_lines.append(f"{int(row['Iteration'])},{row['Scenario']},{row['Heating']:.4f},{row['Cooling']:.4f},{row['Lighting']:.4f},{row['Equipment']:.4f},{row['DHW']:.4f}")
output_lines.append("")

# 4. Hourly Profiles (Append Original)
if hourly_lines:
    output_lines.append("[SECTION] Hourly Load Profiles (kW)")
    output_lines.extend(hourly_lines)
    output_lines.append("")

# 5. Peak Load (Append Original)
if peak_lines:
    output_lines.append("[SECTION] Peak Load Characteristics")
    output_lines.extend(peak_lines)
    output_lines.append("")

# Write Final Output
with open(report_csv, 'w') as f:
    f.write("\n".join(output_lines))
    
print(f"Report updated at: {report_csv}")
