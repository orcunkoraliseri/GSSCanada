
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import io

def parse_report_csv(file_path):
    """
    Parses the Comparative Analysis Report CSV to extract Annual Metrics (Mean and StdDev).
    Returns a dictionary: {Scenario: {'Heating': (mean, std), 'Cooling': (mean, std)}}
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
            if len(parts) < 4:
                continue
                
            category = parts[0] # Heating, Cooling
            scenario = parts[1] # 2025, Default
            
            try:
                mean_val = float(parts[2])
                std_val = float(parts[3])
            except ValueError:
                continue
            
            if category in ['Heating', 'Cooling']:
                if scenario not in metrics:
                    metrics[scenario] = {}
                metrics[scenario][category] = (mean_val, std_val)
                
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None
        
    return metrics

def plot_figure(data, output_dir):
    """
    Generates Figure 4.3.1
    data: dict {City: {Scenario: {'Heating': (mean, std), ...}}}
    output_dir: str (path detailed in main)
    """
    cities = ["Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]
    scenarios = ["Default", "2005", "2010", "2015", "2022", "2025"]
    scenario_labels = ["Def", "'05", "'10", "'15", "'22", "'25"] # Shortened for grid
    
    # 2 Rows (Heating, Cooling), 3 Columns (Cities)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    
    colors = {'Heating': '#d62728', 'Cooling': '#1f77b4'} # Red, Blue
    
    # Data extraction helpers
    def get_vals(city_d, cat):
        means, stds = [], []
        for s in scenarios:
            v = city_d.get(s, {}).get(cat, (0, 0))
            means.append(v[0])
            stds.append(v[1])
        return means, stds

    # Set common Y-limits per row
    # Row 0: Heating (find max)
    max_h = 0
    for city in cities:
        hm, _ = get_vals(data.get(city, {}), 'Heating')
        max_h = max(max_h, max(hm) if hm else 0)
    
    # Row 1: Cooling (find max)
    max_c = 0
    for city in cities:
        cm, _ = get_vals(data.get(city, {}), 'Cooling')
        max_c = max(max_c, max(cm) if cm else 0)
        
    ylim_h = (0, max_h * 1.2)
    ylim_c = (0, max_c * 1.2)
    
    bar_width = 0.6
    index = np.arange(len(scenarios))
    
    for col, city in enumerate(cities):
        city_data = data.get(city, {})
        
        # Annotation Helper
        def annotate_bars(ax, means, stds, baseline_val, is_heating):
            for i, val in enumerate(means):
                if i == 0:
                    pass
                else:
                    if baseline_val > 0:
                        pct = ((val - baseline_val) / baseline_val) * 100
                        label = f"{pct:+.1f}%"
                        
                        # Use (val + std) to clear the error bar
                        std_val = stds[i] if i < len(stds) else 0
                        max_scale = max_h if is_heating else max_c
                        y_pos = (val + std_val) + (max_scale * 0.05)
                        
                        ax.text(i, y_pos, label, 
                                ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0, color='black')

        # Row 0: Heating
        ax_h = axes[0, col]
        h_means, h_stds = get_vals(city_data, 'Heating')
        
        ax_h.bar(index, h_means, bar_width, yerr=h_stds, 
                 capsize=4, color=colors['Heating'], alpha=0.6, label='Heating')
        
        annotate_bars(ax_h, h_means, h_stds, h_means[0] if h_means else 0, True)

        ax_h.set_title(city, fontsize=12, fontweight='bold')
        ax_h.set_ylim(ylim_h)
        ax_h.grid(axis='y', linestyle='--', alpha=0.5)
        
        if col == 0:
            ax_h.set_ylabel('Heating (kWh/m²)', fontsize=10)
        else:
            ax_h.tick_params(labelleft=False)

        # Row 1: Cooling
        ax_c = axes[1, col]
        c_means, c_stds = get_vals(city_data, 'Cooling')
        
        ax_c.bar(index, c_means, bar_width, yerr=c_stds, 
                 capsize=4, color=colors['Cooling'], alpha=0.6, label='Cooling')
        
        annotate_bars(ax_c, c_means, c_stds, c_means[0] if c_means else 0, False)

        ax_c.set_ylim(ylim_c)
        ax_c.grid(axis='y', linestyle='--', alpha=0.5)
        ax_c.set_xticks(index)
        ax_c.set_xticklabels(scenario_labels)
        
        if col == 0:
            ax_c.set_ylabel('Cooling (kWh/m²)', fontsize=10)
        else:
            ax_c.tick_params(labelleft=False)

    plt.tight_layout()
    
    # Save
    output_path = os.path.join(output_dir, "Figure_4.3.1_Energy_Demand.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

def main():
    # Get the script's directory (eSim_occ_utils/plotting)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to reach GSSCanada-main (root)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Define paths relative to project root
    base_dir = os.path.join(project_root, "BEM_Setup", "SimResults")
    output_dir = os.path.join(project_root, "eSim_occ_utils", "plotting")
    
    # Ensure output directory exists (though it should since script is in it)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    locations = {
        "Toronto (5A)": os.path.join("MonteCarlo_N60_1771006398", "Ontario_Comparative_Analysis_Report.csv"),
        "Montreal (6A)": os.path.join("MonteCarlo_N60_1771001406", "Quebec_Comparative_Analysis_Report.csv"),
        "Winnipeg (7)": os.path.join("MonteCarlo_N60_1771010812", "Prairies_Comparative_Analysis_Report.csv")
    }
    
    all_data = {}
    
    print(f"Reading Data from: {base_dir}")
    for city, rel_path in locations.items():
        full_path = os.path.join(base_dir, rel_path)
        metrics = parse_report_csv(full_path)
        if metrics:
            all_data[city] = metrics
        else:
            print(f"Failed to load data for {city} from {full_path}")
            
    if all_data:
        plot_figure(all_data, output_dir)
    else:
        print("No data loaded. Exiting.")

if __name__ == "__main__":
    main()
