"""Figure 4.1.4: Household Size Influence on Occupancy Patterns.

Generates a 1x2 horizontal figure comparing weekday and weekend
occupancy profiles for each household size (1–5 persons) using
2025 GSS-derived BEM schedules.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GSS_FILE = BASE_DIR / "BEM_Setup" / "BEM_Schedules_2025.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "Fig_4_1_4_HHSize_Occupancy.png"

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_context("paper", font_scale=1.4)

# Distinct colour per household size
COLORS = {
    1: "#E24A33",  # Red-orange
    2: "#348ABD",  # Blue
    3: "#988ED5",  # Purple
    4: "#8EBA42",  # Green
    5: "#FBC15E",  # Gold
}

LABELS = {
    1: "1-person",
    2: "2-person",
    3: "3-person",
    4: "4-person",
    5: "5-person",
}


# =============================================================================
# MAIN
# =============================================================================

def generate_plot() -> None:
    """Load data, compute stats, and render the 2x2 figure."""
    print("Loading 2025 GSS data …")
    cols = ["Hour", "Day_Type", "Occupancy_Schedule", "HHSIZE", "SIM_HH_ID"]
    df = pd.read_csv(GSS_FILE, usecols=cols)

    # Household counts per size
    hh_counts = (
        df.drop_duplicates("SIM_HH_ID")
        .groupby("HHSIZE")["SIM_HH_ID"]
        .nunique()
    )
    print(f"Household counts:\n{hh_counts}\n")

    # Unique sizes present in data
    sizes = sorted(df["HHSIZE"].unique())

    # Create figure (2x2 Grid)
    fig = plt.figure(figsize=(16, 10), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 2])

    day_types = ["Weekday", "Weekend"]
    panel_labels_row1 = ["(a) Weekday Occupancy", "(b) Weekend Occupancy"]
    panel_labels_row2 = ["(c) Weekday Metrics", "(d) Weekend Metrics"]

    hours = np.arange(24)

    # LOOP 1: Top Row (Curves)
    for i, (day_type, panel_label) in enumerate(zip(day_types, panel_labels_row1)):
        ax = fig.add_subplot(gs[0, i])
        subset = df[df["Day_Type"] == day_type]

        for size in sizes:
            grp = subset[subset["HHSIZE"] == size]
            stats = grp.groupby("Hour")["Occupancy_Schedule"].agg(["mean", "std"])

            color = COLORS.get(size, "gray")
            label = f"{LABELS.get(size, str(size))}"

            # Plot Line
            ax.plot(hours, stats["mean"], color=color, linewidth=2.5, label=label)
            # Shade Std Dev
            ax.fill_between(
                hours,
                stats["mean"] - stats["std"],
                stats["mean"] + stats["std"],
                color=color,
                alpha=0.12,
            )

        # Styling Row 1
        ax.set_title(panel_label, fontweight="bold", loc="left")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Occupancy Fraction")
        ax.set_ylim(-0.05, 1.1)
        ax.set_xlim(0, 23)
        ax.set_xticks(range(0, 25, 4))
        if i == 0:
            ax.legend(loc="lower left", frameon=True, fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)

    # LOOP 2: Bottom Row (Bars + Markers)
    for i, (day_type, panel_label) in enumerate(zip(day_types, panel_labels_row2)):
        ax = fig.add_subplot(gs[1, i])
        subset = df[df["Day_Type"] == day_type]
        
        # Compute Metrics per HHSIZE
        occ_hours = []
        daytime_pcts = []
        x_labels = []
        bar_colors = []

        for size in sizes:
            grp = subset[subset["HHSIZE"] == size]
            # Occupied Hours (Mean * 24)
            mean_24h = grp.groupby("Hour")["Occupancy_Schedule"].mean()
            occ_hrs = mean_24h.sum()
            occ_hours.append(occ_hrs)
            
            # Daytime Occupancy % (09:00 - 16:59, i.e. hours 9-16 inclusive)
            # Note: "09-17" usually implies 09:00 to 17:00 (8 hours)
            daytime_mean = grp[grp["Hour"].between(9, 16)]["Occupancy_Schedule"].mean()
            daytime_pcts.append(daytime_mean * 100)
            
            x_labels.append(LABELS.get(size, str(size)))
            bar_colors.append(COLORS.get(size, "gray"))

        x_indices = np.arange(len(sizes))

        # Bar Chart (Occupied Hours) - Left Axis
        bars = ax.bar(x_indices, occ_hours, color=bar_colors, alpha=0.7, width=0.6, label="Occupied Hours")
        ax.set_ylabel("Occupied Hours (h)")
        ax.set_ylim(0, 24)
        ax.set_xticks(x_indices)
        ax.set_xticklabels(x_labels, rotation=45, ha="right")
        
        # Twin Axis (Daytime %) - Right Axis
        ax2 = ax.twinx()
        ax2.plot(x_indices, daytime_pcts, color="black", marker="D", markersize=8, linewidth=2, linestyle="-", label="Daytime Occ %")
        ax2.set_ylabel("Daytime Occupancy % (09-17)", color="black")
        ax2.set_ylim(0, 80) # Based on max ~56%
        ax2.grid(False)  # Disable grid on right axis to avoid misalignment
        
        # Value Labels
        # For Bars - place at bottom of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., 1.0,
                    f'{height:.1f}h',
                    ha='center', va='bottom', fontsize=12, color='black')
            
        # For Markers
        for x, y in zip(x_indices, daytime_pcts):
            ax2.text(x, y + 5, f'{y:.1f}%', ha='center', va='bottom', fontsize=12, color='black')

        # Styling Row 2
        ax.set_title(panel_label, loc="left")
        ax.grid(True, axis='y', linestyle="--", alpha=0.4)

    # Super-title
    fig.suptitle(
        "Presence Schedule & Metrics by Household Size (2025 GSS)",
        fontsize=16,
        fontweight="bold",
        y=1.02,
    )

    print(f"Saving to: {OUTPUT_FILE}")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    print("Done.")


if __name__ == "__main__":
    generate_plot()
