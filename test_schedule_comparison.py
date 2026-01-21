#!/usr/bin/env python3
"""
Schedule Comparison Test for Option 5
This script shows the lighting/equipment schedule values that would be applied
for each scenario (2025/2015/2005/Default) WITHOUT running simulations.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eppy.modeleditor import IDF
from bem_utils import integration
import matplotlib.pyplot as plt
import numpy as np


def test_schedule_comparison():
    """Compare schedule values across scenarios."""
    
    # Paths
    IDF_PATH = "BEM_Setup/Neighbourhoods/NUs_RC1.idf"
    SCHEDULE_DIR = "BEM_Setup"
    # Cross-platform EnergyPlus paths
    import platform
    if platform.system() == 'Darwin':  # macOS
        IDD_PATH = "/Applications/EnergyPlus-24-2-0/Energy+.idd"
    elif platform.system() == 'Windows':
        IDD_PATH = r"C:\EnergyPlusV24-2-0\Energy+.idd"
    else:
        IDD_PATH = "/usr/local/EnergyPlus-24-2-0/Energy+.idd"
    
    print("=" * 70)
    print("SCHEDULE COMPARISON TEST (Option 5 - Neighbourhood)")
    print("=" * 70)
    
    # 1. Parse original IDF schedules
    print("\n1. Parsing original IDF schedules...")
    IDF.setiddname(IDD_PATH)
    idf = IDF(IDF_PATH)
    
    # Get LIGHTS schedule
    light_objs = idf.idfobjects.get('LIGHTS', [])
    if light_objs:
        light_sch_name = getattr(light_objs[0], 'Schedule_Name', None)
        light_values = integration.parse_schedule_values(idf, light_sch_name)
        print(f"   LIGHTS schedule: {light_sch_name}")
        if light_values:
            print(f"   Weekday avg: {np.mean(light_values['Weekday']):.3f}")
    else:
        print("   ERROR: No LIGHTS objects found!")
        light_values = None
    
    # Get EQUIPMENT schedule
    equip_objs = idf.idfobjects.get('ELECTRICEQUIPMENT', [])
    if equip_objs:
        equip_sch_name = getattr(equip_objs[0], 'Schedule_Name', None)
        equip_values = integration.parse_schedule_values(idf, equip_sch_name)
        print(f"   EQUIPMENT schedule: {equip_sch_name}")
        if equip_values:
            print(f"   Weekday avg: {np.mean(equip_values['Weekday']):.3f}")
    else:
        print("   ERROR: No ELECTRICEQUIPMENT objects found!")
        equip_values = None
    
    # 2. Load schedule CSVs
    print("\n2. Loading occupancy schedules...")
    schedule_files = {
        '2025': os.path.join(SCHEDULE_DIR, 'BEM_Schedules_2025.csv'),
        '2015': os.path.join(SCHEDULE_DIR, 'BEM_Schedules_2015.csv'),
        '2005': os.path.join(SCHEDULE_DIR, 'BEM_Schedules_2005.csv'),
    }
    
    all_schedules = {}
    for year, csv_path in schedule_files.items():
        if os.path.exists(csv_path):
            schedules = integration.load_schedules(csv_path, region='Ontario')
            all_schedules[year] = schedules
            print(f"   {year}: Loaded {len(schedules)} households")
    
    # 3. Pick a sample household with hhsize=2 (most common size that exists in all years)
    print("\n3. Selecting sample household (target: 2 persons)...")
    target_hhsize = 2
    
    # Find a household with hhsize=3 in 2025
    sample_hh_id = None
    sample_data = None
    for hh_id, data in all_schedules['2025'].items():
        if data.get('metadata', {}).get('hhsize', 0) == target_hhsize:
            sample_hh_id = hh_id
            sample_data = data
            break
    
    if not sample_hh_id:
        print(f"   ERROR: No household with {target_hhsize} persons found in 2025!")
        return
    
    print(f"   Sample: HH {sample_hh_id} ({target_hhsize} persons)")
    
    # 4. Calculate projected schedules for each scenario
    print("\n4. Calculating projected lighting schedules (Weekday)...")
    print("-" * 70)
    
    threshold = 0.3
    scenarios = {}
    
    # Default = original schedule (no modification)
    if light_values:
        scenarios['Default'] = light_values['Weekday']
    
    # For each year, apply presence mask
    for year, schedules in all_schedules.items():
        print(f"   Processing {year}...")
        # Find a household with matching hhsize AND valid data
        found = False
        for hh_id, data in schedules.items():
            hhsize = data.get('metadata', {}).get('hhsize', 0)
            if hhsize == target_hhsize:
                weekday_data = data.get('Weekday', [])
                if weekday_data and len(weekday_data) >= 24:
                    occ_values = [entry['occ'] for entry in sorted(weekday_data, key=lambda x: x['hour'])]
                    
                    # Apply: original × presence_mask
                    if light_values:
                        projected = []
                        for h in range(24):
                            presence = 1.0 if occ_values[h] > threshold else 0.0
                            orig_val = light_values['Weekday'][h]
                            projected.append(orig_val * presence)
                        scenarios[year] = projected
                        print(f"      Found HH {hh_id}, sum={sum(projected):.2f}")
                        found = True
                        break  # Only break when we find valid data
        if not found:
            print(f"      WARNING: No matching household found for {year}!")
    
    # 5. Print comparison table
    print(f"\n{'Hour':<6}", end="")
    for scenario in ['Default', '2025', '2015', '2005']:
        print(f"{scenario:>10}", end="")
    print()
    print("-" * 46)
    
    for h in range(24):
        print(f"{h:02d}:00 ", end="")
        for scenario in ['Default', '2025', '2015', '2005']:
            if scenario in scenarios:
                val = scenarios[scenario][h]
                print(f"{val:>10.3f}", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()
    
    print("-" * 46)
    
    # 6. Calculate totals (daily sum)
    print(f"{'SUM':<6}", end="")
    for scenario in ['Default', '2025', '2015', '2005']:
        if scenario in scenarios:
            total = sum(scenarios[scenario])
            print(f"{total:>10.2f}", end="")
        else:
            print(f"{'N/A':>10}", end="")
    print()
    
    print("\n" + "=" * 70)
    print("KEY INSIGHT:")
    print("  - Default should have the HIGHEST sum (original schedule runs all hours)")
    print("  - 2025/2015/2005 should have LOWER sums (zeroed when away)")
    print("=" * 70)
    
    # 7. Create a simple plot
    fig, ax = plt.subplots(figsize=(12, 6))
    hours = list(range(24))
    
    colors = {'Default': 'brown', '2025': 'darkblue', '2015': 'blue', '2005': 'green'}
    
    for scenario in ['Default', '2025', '2015', '2005']:
        if scenario in scenarios:
            ax.plot(hours, scenarios[scenario], 'o-', label=scenario, 
                   color=colors[scenario], linewidth=2, markersize=4)
    
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Schedule Fraction', fontsize=12)
    ax.set_title('Lighting Schedule Comparison (Weekday)\noriginal_schedule × presence_mask', fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(hours)
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    output_file = "BEM_Setup/SimResults_Plotting/schedule_comparison_test.png"
    plt.savefig(output_file, dpi=150)
    print(f"\nPlot saved to: {output_file}")
    plt.close()


if __name__ == "__main__":
    test_schedule_comparison()
