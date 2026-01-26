"""
Debug script to visualize the Occupancy Integration logic.

Generates comparison plots showing:
1. Presence Schedule (from TUS data)
2. Lighting Schedule (Presence Filter with solar visual)
3. Equipment Schedule (Presence Filter)
4. DHW Schedule (Presence Filter)

Creates 4 visualizations: Default, 2005, 2015, 2025 datasets.
"""
import csv
import os
import random
import sys

import matplotlib.pyplot as plt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bem_utils import schedule_generator
from bem_utils import integration


# --- Configuration ---
EPW_PATH = os.path.join(
    os.path.dirname(__file__),
    "BEM_Setup", "WeatherFile",
    "CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx.epw"
)

SCHEDULES_DIR = os.path.join(
    os.path.dirname(__file__),
    "BEM_Setup"
)

# Default schedules (ApartmentMidrise baseline)
DEFAULT_LIGHT = [
    0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.3, 0.2,
    0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.7, 0.9, 0.9,
    0.8, 0.6, 0.4, 0.2
]
DEFAULT_EQUIP = [
    0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.5, 0.4,
    0.4, 0.4, 0.5, 0.4, 0.4, 0.4, 0.5, 0.6, 0.7, 0.7,
    0.6, 0.5, 0.4, 0.3
]
DEFAULT_WATER = [
    0.05, 0.05, 0.05, 0.05, 0.1, 0.3, 0.5, 0.4, 0.2, 0.1,
    0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.4,
    0.3, 0.2, 0.1, 0.05
]

# Hypothetical presence (for default visualization)
DEFAULT_PRESENCE = [
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5,  # 0-7: Home (Sleep/Wake)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # 8-15: Away (Work)
    0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5   # 16-23: Home (Evening)
]


def load_presence_from_csv(year_tag: str, day_type: str = "Weekday") -> tuple[list[float], str]:
    """
    Load presence schedule from BEM_Schedules CSV files using integration.load_schedules().

    Args:
        year_tag: '05', '15', or '25' for the year dataset.
        day_type: 'Weekday' or 'Weekend'.

    Returns:
        Tuple of (presence_list, hh_id) for a random household.
    """
    csv_path = os.path.join(SCHEDULES_DIR, f"BEM_Schedules_20{year_tag}.csv")
    
    if not os.path.exists(csv_path):
        print(f"  Warning: {csv_path} not found")
        return DEFAULT_PRESENCE, "default"

    try:
        # Use integration.load_schedules() to properly parse the CSV
        all_schedules = integration.load_schedules(csv_path)

        if not all_schedules:
            print(f"  Warning: No households found in {csv_path}")
            return DEFAULT_PRESENCE, "default"

        # Pick a random household
        hh_id = random.choice(list(all_schedules.keys()))
        hh_data = all_schedules[hh_id]

        # Extract presence values for the specified day type
        day_data = hh_data.get(day_type, [])
        if not day_data:
            print(f"  Warning: No {day_type} data for HH {hh_id}")
            return DEFAULT_PRESENCE, str(hh_id)

        # Sort by hour and extract occ values
        sorted_data = sorted(day_data, key=lambda x: x['hour'])
        presence = [entry['occ'] for entry in sorted_data]

        # Ensure we have 24 hours
        if len(presence) < 24:
            presence.extend([0.0] * (24 - len(presence)))

        return presence[:24], str(hh_id)

    except Exception as e:
        print(f"  Error loading CSV: {e}")
        return DEFAULT_PRESENCE, "default"


def create_visualization(
    presence_schedule: list[float],
    title: str,
    output_filename: str,
    show_solar: bool = True
) -> None:
    """
    Create a 4-panel visualization for schedule integration.

    Args:
        presence_schedule: List of 24 hourly presence values.
        title: Title for the plot.
        output_filename: Filename to save the plot.
        show_solar: Whether to show solar radiation in lighting panel.
    """
    # Initialize generators
    lighting_gen = schedule_generator.LightingGenerator(epw_path=EPW_PATH)

    # Generate schedules
    proj_light = lighting_gen.generate(
        presence_schedule, default_schedule=DEFAULT_LIGHT, day_type='Weekday'
    )

    equip_filter = schedule_generator.PresenceFilter(DEFAULT_EQUIP, presence_schedule)
    proj_equip = equip_filter.apply(presence_schedule)

    water_filter = schedule_generator.PresenceFilter(DEFAULT_WATER, presence_schedule)
    proj_water = water_filter.apply(presence_schedule)

    # Get solar profile for visualization
    solar_profile = lighting_gen._get_annual_average_solar()

    # --- Plotting ---
    hours = range(24)
    fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
    fig.suptitle(title, fontsize=14, fontweight='bold')

    # Color scheme
    COLOR_PRESENCE = '#4CAF50'
    COLOR_DEFAULT = '#FF5722'
    COLOR_PROJECTED = '#2196F3'
    COLOR_SOLAR = '#FFC107'

    # Panel 1: Presence Schedule
    ax = axes[0]
    ax.bar(hours, presence_schedule, color=COLOR_PRESENCE, alpha=0.7, label='Presence (TUS)')
    ax.set_title("1. Presence Schedule (from TUS/Census)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Occupancy Fraction")
    ax.set_ylim(0, 1.2)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Panel 2: Lighting (with solar visual)
    ax = axes[1]
    
    if show_solar:
        ax2 = ax.twinx()
        ax2.fill_between(hours, 0, solar_profile, color=COLOR_SOLAR, alpha=0.2, label='Solar Radiation')
        ax2.axhline(150, color=COLOR_SOLAR, linestyle=':', linewidth=2, label='Threshold (150 Wh/m²)')
        ax2.set_ylabel("Solar Radiation (Wh/m²)", color=COLOR_SOLAR)
        ax2.tick_params(axis='y', labelcolor=COLOR_SOLAR)
        ax2.set_ylim(0, max(solar_profile) * 1.2 if max(solar_profile) > 0 else 300)
        ax2.legend(loc='upper right')

    ax.step(hours, DEFAULT_LIGHT, where='mid', color=COLOR_DEFAULT, linestyle='--',
            label='Default Schedule', alpha=0.7)
    ax.step(hours, proj_light, where='mid', color=COLOR_PROJECTED, linewidth=2,
            label='Projected (Presence Filter)')
    ax.set_title("2. Lighting: Presence Filter Method", fontsize=12, fontweight='bold')
    ax.set_ylabel("Lighting Fraction")
    ax.set_ylim(0, 1.2)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    # Panel 3: Equipment (Presence Filter)
    ax = axes[2]
    ax.step(hours, DEFAULT_EQUIP, where='mid', color=COLOR_DEFAULT, linestyle='--',
            label='Default Schedule', alpha=0.7)
    ax.step(hours, proj_equip, where='mid', color=COLOR_PROJECTED, linewidth=2,
            label='Projected (Presence Filter)')
    ax.axhline(equip_filter.active_load, color='green', linestyle=':',
               alpha=0.5, label=f'Active Load (Max={equip_filter.active_load:.2f})')
    ax.axhline(equip_filter.base_load, color='gray', linestyle=':',
               alpha=0.5, label=f'Base Load (Min={equip_filter.base_load:.2f})')
    ax.fill_between(hours, 0, 1, where=[p > 0 for p in presence_schedule],
                    color=COLOR_PRESENCE, alpha=0.1)
    ax.set_title("3. Equipment: Presence Filter Method",
                 fontsize=12, fontweight='bold')
    ax.set_ylabel("Equipment Fraction")
    ax.set_ylim(0, 1.2)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Panel 4: DHW (Presence Filter)
    ax = axes[3]
    ax.step(hours, DEFAULT_WATER, where='mid', color=COLOR_DEFAULT, linestyle='--',
            label='Default Schedule', alpha=0.7)
    ax.step(hours, proj_water, where='mid', color=COLOR_PROJECTED, linewidth=2,
            label='Projected (Presence Filter)')
    ax.axhline(water_filter.active_load, color='green', linestyle=':',
               alpha=0.5, label=f'Active Load (Max={water_filter.active_load:.2f})')
    ax.axhline(water_filter.base_load, color='gray', linestyle=':',
               alpha=0.5, label=f'Base Load (Min={water_filter.base_load:.2f})')
    ax.fill_between(hours, 0, 1, where=[p > 0 for p in presence_schedule],
                    color=COLOR_PRESENCE, alpha=0.1)
    ax.set_title("4. DHW: Presence Filter Method",
                 fontsize=12, fontweight='bold')
    ax.set_ylabel("DHW Fraction")
    ax.set_xlabel("Hour of Day")
    ax.set_ylim(0, 1.0)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Final adjustments
    plt.xticks(range(0, 24, 2))
    plt.tight_layout()

    # Save
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"  ✅ Saved: {output_filename}")


def visualize_default():
    """Generate visualization using pre-defined hypothetical presence."""
    print("\n📊 Generating Default (Hypothetical) Visualization...")
    create_visualization(
        presence_schedule=DEFAULT_PRESENCE,
        title="Schedule Integration - Default (Hypothetical Presence)",
        output_filename="debug_schedule_default.png"
    )


def visualize_real_datasets():
    """Generate visualizations using real 05, 15, 25 datasets."""
    datasets = ['05', '15', '25']

    for year in datasets:
        print(f"\n📊 Generating 20{year} Dataset Visualization...")
        presence, hh_id = load_presence_from_csv(year, day_type="Weekday")
        
        create_visualization(
            presence_schedule=presence,
            title=f"Schedule Integration - 20{year} Dataset (HH: {hh_id})",
            output_filename=f"debug_schedule_{year}.png"
        )


def main():
    """Generate all 4 visualizations."""
    print("=" * 60)
    print("Schedule Integration Debug Visualizations")
    print("=" * 60)

    # Set random seed for reproducibility
    random.seed(42)

    # Generate all visualizations
    visualize_default()
    visualize_real_datasets()

    print("\n" + "=" * 60)
    print("✅ All visualizations complete!")
    print("Generated files:")
    print("  - debug_schedule_default.png (Hypothetical)")
    print("  - debug_schedule_05.png (2005 Dataset)")
    print("  - debug_schedule_15.png (2015 Dataset)")
    print("  - debug_schedule_25.png (2025 Dataset)")
    print("=" * 60)


if __name__ == "__main__":
    main()
