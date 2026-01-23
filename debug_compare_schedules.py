import matplotlib.pyplot as plt
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bem_utils import integration

def compare_schedules():
    """
    Generates a comparison plot of Default vs. Projected schedules for a hypothetical day.
    """
    # 1. Define Standard "Default" Schedules (from integration.py fallback values)
    # Lighting: Low day, high evening
    default_light = [
        0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.3, 0.2, 
        0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.7, 0.9, 0.9, 
        0.8, 0.6, 0.4, 0.2
    ]
    # Equipment: Moderate flat profile
    default_equip = [
        0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.5, 0.4, 
        0.4, 0.4, 0.5, 0.4, 0.4, 0.4, 0.5, 0.6, 0.7, 0.7, 
        0.6, 0.5, 0.4, 0.3
    ]
    # Hot Water: Peaks morning/evening
    default_water = [
        0.05, 0.05, 0.05, 0.05, 0.1, 0.3, 0.5, 0.4, 0.2, 0.1,
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.4,
        0.3, 0.2, 0.1, 0.05
    ]

    # 2. Define a Hypothetical TUS Presence Profile
    # Scenario: Working adult (Away 9am-5pm), Home evening
    # 1 = Present, 0 = Absent
    # Hours: 0-7 (Sleep/Home), 8-9 (Leave), 10-16 (Away), 17 (Return), 18-23 (Home)
    presence_tusp = [
        1, 1, 1, 1, 1, 1, 1, 1,  # 0-7: Home (Sleep)
        0.5, 0, 0, 0, 0, 0, 0, 0,  # 8-15: Away (Work)
        0.5, 1, 1, 1, 1, 1, 1, 1   # 16-23: Home (Evening)
    ]
    
    threshold = 0.3
    presence_mask = [1.0 if p > threshold else 0.0 for p in presence_tusp]
    
    # 3. Apply Integration Logic (Current implementation)
    # Logic:
    #   - If Present: Use Default
    #   - If Absent: Use 0 (or 0.35 for Equip)
    
    proj_light = []
    proj_equip = []
    proj_water = []
    
    for h in range(24):
        p = presence_mask[h]
        
        # Lighting: Max(Default, 0.50) if present, 0.05 if absent
        if p > 0:
            proj_light.append(max(default_light[h], 0.50))
        else:
            proj_light.append(0.05)
        
        # Equipment: Max(Default, 0.50) if present, 0.35 if absent
        if p > 0:
            proj_equip.append(max(default_equip[h], 0.50))
        else:
            proj_equip.append(0.35)
            
        # Water: Max(Default, 0.0) if present, 0 if absent
        if p > 0:
            proj_water.append(max(default_water[h], 0.0))
        else:
            proj_water.append(0.0)

    # 4. Plotting
    hours = range(24)
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Plot Lighting
    ax = axes[0]
    ax.plot(hours, default_light, 'r--', label='Default Schedule', alpha=0.7)
    ax.plot(hours, proj_light, 'b-', label='Projected (TUS Integrated)', linewidth=2)
    ax.fill_between(hours, 0, 1, where=[p>0 for p in presence_mask], 
                    color='yellow', alpha=0.1, label='Occupant Present (TUS)')
    ax.set_title("Lighting Comparison")
    ax.set_ylabel("Fraction")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot Equipment
    ax = axes[1]
    ax.plot(hours, default_equip, 'r--', label='Default Schedule', alpha=0.7)
    ax.plot(hours, proj_equip, 'b-', label='Projected (TUS Integrated)', linewidth=2)
    ax.fill_between(hours, 0, 1, where=[p>0 for p in presence_mask], 
                    color='yellow', alpha=0.1, label='Occupant Present (TUS)')
    ax.axhline(0.35, color='gray', linestyle=':', label='Baseload (0.35)')
    ax.set_title("Equipment Comparison")
    ax.set_ylabel("Fraction")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot Water
    ax = axes[2]
    ax.plot(hours, default_water, 'r--', label='Default Schedule', alpha=0.7)
    ax.plot(hours, proj_water, 'b-', label='Projected (TUS Integrated)', linewidth=2)
    ax.fill_between(hours, 0, 1, where=[p>0 for p in presence_mask], 
                    color='yellow', alpha=0.1, label='Occupant Present (TUS)')
    ax.set_title("Hot Water Comparison")
    ax.set_ylabel("Fraction")
    ax.set_xlabel("Hour of Day")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = 'debug_schedule_comparison.png'
    plt.savefig(output_path)
    print(f"Comparison plot saved to {output_path}")

if __name__ == "__main__":
    compare_schedules()
