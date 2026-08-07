from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from cross_cycle_plot_utils import (
    CYCLE_COLORS,
    OUTPUT_DIR,
    compute_mean_profiles,
    load_all_cycles,
    prepare_heatmap_matrices,
)


OUTPUT_PRIMARY = OUTPUT_DIR / "BEM_Temporal_CrossCycle_Comparison.png"
OUTPUT_SPAGHETTI = OUTPUT_DIR / "BEM_Temporal_Spaghetti_Comparison.png"
LOAD_COLUMNS = ["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule", "Metabolic_Rate"]
CYCLES = ["2005", "2010", "2015", "2022", "2025"]


def _heatmap_cmap(cycle: str) -> str:
    return "Oranges" if cycle == "2025" else "Greens"


def _plot_heatmap_slice(ax, matrix, cycle: str, start: int, end: int, show_xlabel: bool, show_ylabel: bool) -> None:
    subset = matrix.iloc[start:end]
    if subset.empty:
        ax.text(0.5, 0.5, "No Data", ha="center", va="center", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    image = ax.imshow(subset.to_numpy(), aspect="auto", cmap=_heatmap_cmap(cycle), vmin=0, vmax=1)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
    ax.set_xticklabels(["0", "4", "8", "12", "16", "20", "23"] if show_xlabel else [])
    ax.set_xlabel("Hour" if show_xlabel else "", fontsize=10)
    ax.set_ylabel("Households" if show_ylabel else "", fontsize=10)
    ax.set_yticks([])
    return image


def save_primary_figure(data_map) -> None:
    heatmaps = prepare_heatmap_matrices(data_map, sample_size=150, seed=42)

    fig, axes = plt.subplots(
        4,
        5,
        figsize=(22, 12),
        sharex=False,
        sharey="row",
        gridspec_kw={"height_ratios": [1, 1, 1, 1]},
    )
    fig.subplots_adjust(left=0.07, right=0.965, top=0.91, bottom=0.06, hspace=0.08, wspace=0.12)

    last_image = None

    for col_idx, cycle in enumerate(CYCLES):
        axes[0, col_idx].set_title(cycle, fontsize=13, fontweight="bold", pad=8)

        weekday = heatmaps[cycle]["Weekday"]
        weekend = heatmaps[cycle]["Weekend"]
        weekday_split = int(np.ceil(len(weekday) / 2)) if len(weekday) else 0
        weekend_split = int(np.ceil(len(weekend) / 2)) if len(weekend) else 0

        last_image = _plot_heatmap_slice(
            axes[0, col_idx],
            weekday,
            cycle,
            0,
            weekday_split,
            show_xlabel=False,
            show_ylabel=(col_idx == 0),
        )
        _plot_heatmap_slice(
            axes[1, col_idx],
            weekday,
            cycle,
            weekday_split,
            len(weekday),
            show_xlabel=False,
            show_ylabel=(col_idx == 0),
        )
        _plot_heatmap_slice(
            axes[2, col_idx],
            weekend,
            cycle,
            0,
            weekend_split,
            show_xlabel=False,
            show_ylabel=(col_idx == 0),
        )
        _plot_heatmap_slice(
            axes[3, col_idx],
            weekend,
            cycle,
            weekend_split,
            len(weekend),
            show_xlabel=True,
            show_ylabel=(col_idx == 0),
        )

    fig.text(0.015, 0.72, "Weekday\nSample\nHouseholds", fontsize=11, fontweight="bold", va="center")
    fig.text(0.015, 0.28, "Weekend\nSample\nHouseholds", fontsize=11, fontweight="bold", va="center")
    fig.suptitle(
        "Cross-Cycle Temporal Comparison of Occupancy-Derived Schedules",
        fontsize=15,
        fontweight="bold",
        y=0.97,
    )

    if last_image is not None:
        cbar = fig.colorbar(last_image, ax=axes[:, :], fraction=0.012, pad=0.015)
        cbar.set_label("Occupancy Fraction (0 = Away, 1 = Full Occupancy)", fontsize=10)

    fig.savefig(OUTPUT_PRIMARY, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUTPUT_PRIMARY}")


def save_spaghetti_figure(data_map) -> None:
    heatmaps = prepare_heatmap_matrices(data_map, sample_size=80, seed=42)
    mean_profiles = compute_mean_profiles(data_map)

    fig, axes = plt.subplots(2, 5, figsize=(22, 8), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.88, bottom=0.12, hspace=0.28, wspace=0.15)

    for col_idx, cycle in enumerate(CYCLES):
        axes[0, col_idx].set_title(cycle, fontsize=12, fontweight="bold")
        for row_idx, day_type in enumerate(["Weekday", "Weekend"]):
            ax = axes[row_idx, col_idx]
            matrix = heatmaps[cycle][day_type]
            line_color = CYCLE_COLORS[cycle]

            if not matrix.empty:
                for _, row in matrix.iterrows():
                    ax.plot(range(24), row.to_numpy(dtype=float), color=line_color, alpha=0.08, linewidth=0.6)

            stats = mean_profiles[cycle][day_type]
            ax.fill_between(
                stats.index,
                stats["q25"].to_numpy(dtype=float),
                stats["q75"].to_numpy(dtype=float),
                color=line_color,
                alpha=0.18,
            )
            ax.plot(stats.index, stats["mean"].to_numpy(dtype=float), color="black", linewidth=2.2)
            ax.plot(stats.index, stats["mean"].to_numpy(dtype=float), color=line_color, linewidth=1.5)
            ax.set_xlim(0, 23)
            ax.set_ylim(0, 1)
            ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            ax.set_xlabel("Hour" if row_idx == 1 else "", fontsize=10)
            ax.set_ylabel(day_type if col_idx == 0 else "", fontsize=10)

    fig.text(0.5, 0.03, "Black line = mean profile, shaded band = interquartile range", ha="center", fontsize=10)
    fig.suptitle(
        "Supplementary Cross-Cycle Spaghetti Comparison of Household Occupancy Schedules",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    fig.savefig(OUTPUT_SPAGHETTI, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUTPUT_SPAGHETTI}")


def main() -> None:
    print("=" * 72)
    print("BEM temporal cross-cycle comparison")
    print("=" * 72)
    data_map, _ = load_all_cycles(LOAD_COLUMNS)
    save_primary_figure(data_map)
    save_spaghetti_figure(data_map)


if __name__ == "__main__":
    main()
