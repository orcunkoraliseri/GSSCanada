from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cross_cycle_plot_utils import (
    CYCLE_COLORS,
    OUTPUT_DIR,
    build_non_temporal_distributions,
    load_all_cycles,
)


OUTPUT_FILE = OUTPUT_DIR / "BEM_NonTemporal_CrossCycle_Comparison.png"
LOAD_COLUMNS = ["SIM_HH_ID", "DTYPE", "BEDRM", "ROOM", "PR"]
ROW_VARIABLES = ["DTYPE", "BEDRM", "ROOM", "PR"]
ROW_LABELS = {
    "DTYPE": "Dwelling Type",
    "BEDRM": "Bedrooms",
    "ROOM": "Rooms",
    "PR": "Region",
}


def format_category_labels(variable: str, categories: list[object]) -> list[str]:
    labels: list[str] = []
    for value in categories:
        if variable in {"BEDRM", "ROOM"}:
            if pd.isna(value):
                labels.append("NA")
                continue
            as_float = float(value)
            labels.append(str(int(as_float)) if as_float.is_integer() else f"{as_float:g}")
        else:
            label = str(value)
            if variable == "DTYPE" and label == "OtherDwelling":
                label = "Other"
            labels.append(label)
    return labels


def main() -> None:
    print("=" * 72)
    print("BEM non-temporal cross-cycle comparison")
    print("=" * 72)

    data_map, _ = load_all_cycles(LOAD_COLUMNS)
    distributions, category_orders = build_non_temporal_distributions(data_map)

    fig, axes = plt.subplots(4, 5, figsize=(22, 13.2), sharey="row", constrained_layout=False)
    fig.subplots_adjust(left=0.08, right=0.995, top=0.93, bottom=0.12, hspace=0.20, wspace=0.18)

    row_maxima = {}
    household_counts = {
        cycle: int(df["SIM_HH_ID"].nunique())
        for cycle, df in data_map.items()
    }

    for variable in ROW_VARIABLES:
        row_maxima[variable] = max(
            (series.max() for series in distributions[variable].values()),
            default=0.0,
        )

    for row_idx, variable in enumerate(ROW_VARIABLES):
        categories = category_orders[variable]
        labels = format_category_labels(variable, categories)
        rotation = 45 if variable in {"DTYPE", "PR"} else 0
        x = np.arange(len(categories))

        for col_idx, cycle in enumerate(["2005", "2010", "2015", "2022", "2025"]):
            ax = axes[row_idx, col_idx]
            series = distributions[variable].get(cycle)
            if series is None:
                ax.text(0.5, 0.5, "No Data", ha="center", va="center", transform=ax.transAxes)
                continue

            ax.bar(x, series.values, color=CYCLE_COLORS[cycle], edgecolor="black", linewidth=0.4, alpha=0.7)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=rotation, ha="right" if rotation else "center", fontsize=9)
            ax.tick_params(axis="y", labelsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.35)
            ax.set_axisbelow(True)
            ax.set_ylim(0, row_maxima[variable] * 1.15 if row_maxima[variable] else 1)

            if col_idx == 0:
                ax.set_ylabel(f"{ROW_LABELS[variable]}\nShare (%)", fontsize=11, fontweight="bold")
            else:
                ax.set_ylabel("")

            if row_idx == 0:
                n_str = f"N={household_counts[cycle]:,}" if cycle in household_counts else ""
                ax.set_title(f"{cycle}\n{n_str}", fontsize=12, fontweight="bold", pad=8, ha="center")

    fig.suptitle(
        "Cross-Cycle Comparison of Occupancy-Derived Non-Temporal Household Attributes",
        fontsize=15,
        fontweight="bold",
        y=0.995,
    )
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
