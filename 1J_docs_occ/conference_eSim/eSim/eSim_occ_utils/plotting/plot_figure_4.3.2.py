
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def parse_report_csv(file_path):
    """
    Parses the Comparative Analysis Report CSV to extract Annual Metrics (Mean).
    Returns a dictionary: {Scenario: {'Heating': mean, 'Cooling': mean}}
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

def plot_temporal_trend(data, output_dir):
    """
    Generates Figure 4.3.2 (2x3 Grid: Heating Top, Cooling Bottom)
    data: dict {City: {Scenario: {'Heating': mean, 'Cooling': mean}}}
    """
    cities = ["Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]
    years = [2005, 2010, 2015, 2022, 2025]
    scenarios = ["2005", "2010", "2015", "2022", "2025"]
    
    # 2 Rows (Heating, Cooling), 3 Columns (Cities)
    fig, axes = plt.subplots(2, 3, figsize=(15, 7), sharex=True)
    
    colors = {'Heating': '#d62728', 'Cooling': '#1f77b4', 'Total': 'black'}
    
    ylim_h = (65, 95)
    ylim_c = (1.2, 2.2)
    
    # Calculate Max for annotation headroom
    max_h, max_c = 95, 2.2
    
    for col, city in enumerate(cities):
        city_data = data.get(city, {})
        
        # Extract Data
        h_vals = [city_data.get(s, {}).get('Heating', 0) for s in scenarios]
        c_vals = [city_data.get(s, {}).get('Cooling', 0) for s in scenarios]
        
        # Baselines
        def_h = city_data.get('Default', {}).get('Heating', 0)
        def_c = city_data.get('Default', {}).get('Cooling', 0)
        
        # --- Row 0: Heating ---
        ax_h = axes[0, col]
        ax_h.plot(years, h_vals, marker='s', color=colors['Heating'], linewidth=2, label='Heating Trend')
        ax_h.axhline(def_h, color='gray', linestyle=':', linewidth=2, label='Static Baseline')
        
        ax_h.set_title(city, fontsize=12, fontweight='bold')
        ax_h.set_ylim(ylim_h)
        ax_h.grid(True, linestyle='--', alpha=0.3)
        
        # Annotation Heating Gap (2025)
        if def_h > 0:
            last_h = h_vals[-1]
            pct = ((last_h - def_h) / def_h) * 100
            ax_h.annotate(f"{pct:+.1f}%", 
                          xy=(2025, last_h), xycoords='data',
                          xytext=(2025, last_h + (max_h * 0.08)), textcoords='data',
                          arrowprops=dict(arrowstyle="->", color=colors['Heating']),
                          ha='center', fontsize=9, fontweight='bold')
                          
        if col == 0:
            ax_h.set_ylabel('Annual Heating (kWh/m²)', fontsize=10)
        
        # --- Row 1: Cooling ---
        ax_c = axes[1, col]
        ax_c.plot(years, c_vals, marker='^', color=colors['Cooling'], linewidth=2, label='Cooling Trend')
        ax_c.axhline(def_c, color='gray', linestyle=':', linewidth=2, label='Static Baseline')
        
        ax_c.set_ylim(ylim_c)
        ax_c.grid(True, linestyle='--', alpha=0.3)
        ax_c.set_xticks(years)

        # Annotation Cooling Gap (2025)
        if def_c > 0:
            last_c = c_vals[-1]
            pct = ((last_c - def_c) / def_c) * 100
            ax_c.annotate(f"{pct:+.1f}%", 
                          xy=(2025, last_c), xycoords='data',
                          xytext=(2025, last_c + (max_c * 0.1)), textcoords='data',
                          arrowprops=dict(arrowstyle="->", color=colors['Cooling']),
                          ha='center', fontsize=9, fontweight='bold')
        
        if col == 0:
            ax_c.set_ylabel('Annual Cooling (kWh/m²)', fontsize=10)

    # Combined Legend
    h_h, l_h = axes[0, 0].get_legend_handles_labels()
    h_c, l_c = axes[1, 0].get_legend_handles_labels()
    
    # Consolidate unique labels
    new_h, new_l = [], []
    for h, l in zip(h_h + h_c, l_h + l_c):
        if l not in new_l:
            new_h.append(h)
            new_l.append(l)
            
    fig.legend(new_h, new_l, loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=3, fontsize=10)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.85) # Make room for legend
    
    # Save
    output_path = os.path.join(output_dir, "Figure_4.3.2_Temporal_Trend.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

def main():
    # Dynamic paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    base_dir = os.path.join(project_root, "BEM_Setup", "SimResults")
    output_dir = os.path.join(project_root, "eSim_occ_utils", "plotting")
    
    locations = {
        "Toronto (5A)": os.path.join("MonteCarlo_N60_1771006398", "Ontario_Comparative_Analysis_Report.csv"),
        "Montreal (6A)": os.path.join("MonteCarlo_N60_1771001406", "Quebec_Comparative_Analysis_Report.csv"),
        "Winnipeg (7)": os.path.join("MonteCarlo_N60_1771010812", "Prairies_Comparative_Analysis_Report.csv")
    }
    
    all_data = {}
    
    print("Reading Data for temporal trend analysis...")
    for city, rel_path in locations.items():
        full_path = os.path.join(base_dir, rel_path)
        metrics = parse_report_csv(full_path)
        if metrics:
            all_data[city] = metrics
        else:
            print(f"Failed to load data for {city} from {full_path}")
            
    if all_data:
        plot_temporal_trend(all_data, output_dir)
    else:
        print("Error: No data loaded.")

if __name__ == "__main__":
    main()
