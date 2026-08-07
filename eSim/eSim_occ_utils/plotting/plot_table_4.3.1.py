
import pandas as pd
import os
import io

def parse_report_csv(file_path):
    """
    Parses the Comparative Analysis Report CSV to extract Annual Metrics.
    Returns a dictionary: {Scenario: {'Heating': val, 'Cooling': val}}
    """
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None

    metrics = {}
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find start of Annual Metrics section
        start_idx = -1
        for i, line in enumerate(lines):
            if "[SECTION] Annual Energy Demand Metrics (Aggregated)" in line:
                start_idx = i + 2 # Skip header
                break
        
        if start_idx == -1:
            print(f"Error: Could not find Annual Metrics section in {file_path}")
            return None

        # Parse lines until empty line
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if not line:
                break
            
            parts = line.split(',')
            if len(parts) < 3:
                continue
                
            category = parts[0] # Heating, Cooling
            scenario = parts[1] # 2025, Default
            try:
                mean_val = float(parts[2])
            except ValueError:
                continue
            
            if category in ['Heating', 'Cooling']:
                if scenario not in metrics:
                    metrics[scenario] = {}
                metrics[scenario][category] = mean_val
                
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None
        
    return metrics

def calculate_changes(metrics):
    """
    Calculates % change vs Default for each scenario.
    Returns dict: {Scenario: "Heating% / Cooling%"}
    """
    if 'Default' not in metrics:
        return None
        
    def_heat = metrics['Default'].get('Heating', 0)
    def_cool = metrics['Default'].get('Cooling', 0)
    
    results = {}
    
    for scen, vals in metrics.items():
        if scen == 'Default':
            continue
            
        heat_val = vals.get('Heating', 0)
        cool_val = vals.get('Cooling', 0)
        
        # Calculate % Change
        if def_heat > 0:
            pct_heat = ((heat_val - def_heat) / def_heat) * 100
        else:
            pct_heat = 0.0
            
        if def_cool > 0:
            pct_cool = ((cool_val - def_cool) / def_cool) * 100
        else:
            pct_cool = 0.0
            
        # Format: "+X% / -X%"
        results[scen] = "{:+.1f}% / {:+.1f}%".format(pct_heat, pct_cool)
        
    return results

def main():
    # Input files
    base_dir = r"BEM_Setup\SimResults"
    
    # Map City Name -> File Path
    locations = {
        "Toronto (5A)": r"MonteCarlo_N60_1771006398\Ontario_Comparative_Analysis_Report.csv",
        "Montreal (6A)": r"MonteCarlo_N60_1771001406\Quebec_Comparative_Analysis_Report.csv",
        "Winnipeg (7)": r"MonteCarlo_N60_1771010812\Prairies_Comparative_Analysis_Report.csv"
    }
    
    all_data = {}
    
    print("Processing Reports...")
    for city, rel_path in locations.items():
        full_path = os.path.join(base_dir, rel_path)
        print(f"  Reading {city} from {full_path}")
        
        metrics = parse_report_csv(full_path)
        if metrics:
            changes = calculate_changes(metrics)
            if changes:
                all_data[city] = changes
            else:
                print(f"    Error: Could not calculate changes for {city} (Missing Default?)")
    
    # Create DataFrame
    # Rows: 2005, 2015, 2025
    # Cols: City Names
    
    scenarios = ["2005", "2015", "2025"]
    table_data = []
    
    for scen in scenarios:
        row = {"Scenario": f"{scen} GSS"} # Rename as requested
        for city in ["Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]:
            if city in all_data and scen in all_data[city]:
                row[city] = all_data[city][scen]
            else:
                row[city] = "N/A"
        table_data.append(row)
        
    df = pd.DataFrame(table_data)
    
    # Reorder columns
    cols = ["Scenario", "Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]
    df = df[cols]
    
    print("\nGenerated Table 4.3.1:")
    print(df.to_string(index=False))
    
    # Save to requested location
    output_dir = r"eSim_occ_utils\plotting"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "Table_4.3.1_Annual_Energy_Demand.csv")
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
