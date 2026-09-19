"""
Debug script to visualize multiple presence schedules from real datasets.

Creates 5x5 subplot visualizations showing 25 randomly selected presence
schedules from each dataset (2005, 2015, 2025) to verify data correctness.

Output:
- debug_presence_05.png (25 households from 2005)
- debug_presence_15.png (25 households from 2015)
- debug_presence_25.png (25 households from 2025)
"""
import os
import random
import sys

import matplotlib.pyplot as plt

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from eSim_bem_utils import integration


# --- Configuration ---
SCHEDULES_DIR = os.path.join(ROOT_DIR, "BEM_Setup")
NUM_SAMPLES = 25  # 5x5 grid
RANDOM_SEED = 42


def visualize_presence_grid(
    year_tag: str,
    num_samples: int = 16,
    day_type: str = "Weekday"
) -> None:
    """
    Create a 4x4 grid visualization of presence schedules from a dataset.

    Args:
        year_tag: '05', '15', or '25' for the year dataset.
        num_samples: Number of households to sample (should be a perfect square).
        day_type: 'Weekday' or 'Weekend'.
    """
    csv_path = os.path.join(SCHEDULES_DIR, f"BEM_Schedules_20{year_tag}.csv")

    if not os.path.exists(csv_path):
        print(f"  ❌ Error: {csv_path} not found")
        return

    # Load all schedules using integration.load_schedules()
    print(f"\n📊 Loading 20{year_tag} dataset...")
    all_schedules = integration.load_schedules(csv_path)

    if not all_schedules:
        print(f"  ❌ Error: No households found in {csv_path}")
        return

    # Randomly sample households
    all_hh_ids = list(all_schedules.keys())
    sample_size = min(num_samples, len(all_hh_ids))
    sampled_hh_ids = random.sample(all_hh_ids, sample_size)

    print(f"  Selected {sample_size} random households from {len(all_hh_ids)} total")

    # Calculate grid dimensions
    grid_size = int(sample_size ** 0.5)
    if grid_size * grid_size < sample_size:
        grid_size += 1

    # Create figure with subplots
    fig, axes = plt.subplots(
        grid_size, grid_size,
        figsize=(16, 16),
        sharex=True, sharey=True
    )
    fig.suptitle(
        f"Presence Schedules - 20{year_tag} Dataset ({day_type})\n"
        f"{sample_size} Random Households",
        fontsize=16, fontweight='bold'
    )

    # Flatten axes for easy iteration
    axes_flat = axes.flatten() if sample_size > 1 else [axes]

    hours = range(24)

    for idx, hh_id in enumerate(sampled_hh_ids):
        ax = axes_flat[idx]

        # Extract presence values
        hh_data = all_schedules[hh_id]
        day_data = hh_data.get(day_type, [])

        if day_data:
            sorted_data = sorted(day_data, key=lambda x: x['hour'])
            presence = [entry['occ'] for entry in sorted_data]

            # Ensure 24 hours
            if len(presence) < 24:
                presence.extend([0.0] * (24 - len(presence)))
            presence = presence[:24]
        else:
            presence = [0.0] * 24

        # Get household metadata
        metadata = hh_data.get('metadata', {})
        hhsize = metadata.get('hhsize', '?')
        dtype = metadata.get('dtype', '?')

        # Plot
        ax.bar(hours, presence, color='#4CAF50', alpha=0.7, width=0.8)
        ax.set_ylim(0, 1.2)
        ax.set_title(f"HH: {hh_id}\n(Size={hhsize}, Type={dtype})", fontsize=9)
        ax.grid(True, alpha=0.3)

        # Only show x-axis labels on bottom row
        if idx >= (grid_size - 1) * grid_size:
            ax.set_xlabel("Hour")
            ax.set_xticks([0, 6, 12, 18, 23])
        else:
            ax.set_xticks([])

        # Only show y-axis labels on left column
        if idx % grid_size == 0:
            ax.set_ylabel("Occupancy")

    # Hide unused subplots
    for idx in range(sample_size, len(axes_flat)):
        axes_flat[idx].axis('off')

    plt.tight_layout()

    output_path = os.path.join(
        ROOT_DIR,
        f"debug_presence_{year_tag}.png"
    )
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"  ✅ Saved: debug_presence_{year_tag}.png")


def main():
    """Generate presence schedule visualizations for all datasets."""
    print("=" * 60)
    print("Presence Schedule Debug Visualizations")
    print("=" * 60)

    # Set random seed for reproducibility
    random.seed(RANDOM_SEED)

    # Generate visualizations for each dataset
    for year in ['05', '15', '25']:
        visualize_presence_grid(year, num_samples=NUM_SAMPLES, day_type="Weekday")

    print("\n" + "=" * 60)
    print("✅ All visualizations complete!")
    print("Generated files:")
    print("  - debug_presence_05.png (2005 Dataset)")
    print("  - debug_presence_15.png (2015 Dataset)")
    print("  - debug_presence_25.png (2025 Dataset)")
    print("=" * 60)


if __name__ == "__main__":
    main()
