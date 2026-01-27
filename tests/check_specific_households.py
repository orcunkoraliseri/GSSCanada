
"""
Script to visualize specific households requested by the user.
2015: HH36087, HH59325
2025: HH4272, HH3041, HH882
"""
import os
import sys
import matplotlib.pyplot as plt

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from bem_utils import integration

SCHEDULES_DIR = os.path.join(ROOT_DIR, "BEM_Setup")

def visualize_specific_households(year_tag, target_ids):
    print(f"\n--- Checking 20{year_tag} Dataset ---")
    csv_path = os.path.join(SCHEDULES_DIR, f"BEM_Schedules_20{year_tag}.csv")
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    all_schedules = integration.load_schedules(csv_path)
    
    found_data = []
    for hid in target_ids:
        # Check integer or string matches
        if hid in all_schedules:
            found_data.append((hid, all_schedules[hid]))
        elif str(hid) in all_schedules:
            found_data.append((str(hid), all_schedules[str(hid)]))
        else:
            print(f"❌ HH {hid} NOT FOUND in dataset.")

    if not found_data:
        return

    # Plot
    num_plots = len(found_data)
    fig, axes = plt.subplots(1, num_plots, figsize=(6*num_plots, 5), squeeze=False)
    fig.suptitle(f"Specific Households Check - 20{year_tag}", fontsize=14)
    
    hours = range(24)
    
    for idx, (hid, data) in enumerate(found_data):
        ax = axes[0, idx]
        
        # Plot Weekday and Weekend
        for dtype, color, label in [('Weekday', 'green', 'Weekday'), ('Weekend', 'blue', 'Weekend')]:
            day_data = data.get(dtype, [])
            if day_data:
                sorted_data = sorted(day_data, key=lambda x: x['hour'])
                presence = [entry['occ'] for entry in sorted_data]
                if len(presence) < 24: presence.extend([0]*(24-len(presence)))
                presence = presence[:24]
                
                ax.plot(hours, presence, label=label, color=color, linewidth=2, alpha=0.7)
                if dtype == 'Weekday':
                    ax.fill_between(hours, 0, presence, color=color, alpha=0.1)
            else:
                print(f"  HH {hid} missing {dtype} data")

        # Metadata
        meta = data.get('metadata', {})
        title = f"HH: {hid}\nSize: {meta.get('hhsize','?')}, Type: {meta.get('dtype','?')}"
        ax.set_title(title)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("Hour")
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.grid(True, alpha=0.3)
        if idx == 0:
            ax.set_ylabel("Occupancy")
        ax.legend()

    plt.tight_layout()
    out_file = os.path.join(ROOT_DIR, f"check_hh_{year_tag}.png")
    plt.savefig(out_file)
    print(f"✅ Saved plot to {out_file}")

if __name__ == "__main__":
    # Requested IDs
    targets_2015 = [36087, 59325]
    targets_2025 = [4272, 3041, 882]
    
    visualize_specific_households('15', targets_2015)
    visualize_specific_households('25', targets_2025)
