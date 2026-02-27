"""Plot presence evolution — Version 2.

Changes vs. v1
--------------
* Grid layout changed from 2 rows × 3 columns to 3 rows × 2 columns.
  Each row corresponds to one year (2005 / 2015 / 2025).
  Left column: Presence Schedule; Right column: Summary Metrics.
* All font sizes roughly doubled for publication readability.
* Output file: BEM_Presence_Evolution_Comparison_v2.png (original untouched).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# BASE DIR: ../../../ from this script
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# CONFIGURATION
# =============================================================================

FILE_BEM_2005 = BASE_DIR / "BEM_Setup/BEM_Schedules_2005.csv"
FILE_BEM_2015 = BASE_DIR / "BEM_Setup/BEM_Schedules_2015.csv"
FILE_BEM_2025 = BASE_DIR / "BEM_Setup/BEM_Schedules_2025.csv"

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "BEM_Presence_Evolution_Comparison_v2.png"

YEARS: list[str] = ["2005", "2015", "2025"]
FILES: list[Path] = [FILE_BEM_2005, FILE_BEM_2015, FILE_BEM_2025]

# Style Colors
PALETTE_PRESENCE: dict[str, str] = {"Weekday": "green", "Weekend": "teal"}
BAR_COLORS: dict[str, str] = {
    "Weekday": "#4CAF50",
    "Weekend": "#009688",
}  # Material Green & Teal

# =============================================================================
# FONT SIZE CONSTANTS  (roughly 2× the original values)
# =============================================================================

FS_TITLE: int = 26       # subplot titles
FS_AXIS_LABEL: int = 20  # x/y axis labels
FS_TICK: int = 18        # tick labels
FS_LEGEND: int = 18      # legend text
FS_BAR_ANNOT: int = 20   # bar height annotations
FS_POINT_ANNOT: int = 22 # daytime fraction point labels

# =============================================================================
# FUNCTIONS
# =============================================================================


def load_bem_data(file_path: Path, year_label: str) -> pd.DataFrame | None:
    """Load BEM schedule CSV for one year.

    Args:
        file_path: Path to the CSV file.
        year_label: Human-readable year string used in log messages.

    Returns:
        DataFrame with columns [Hour, Day_Type, Occupancy_Schedule], or None
        on failure.
    """
    print(f"   Loading {year_label} BEM schedules...")
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return None
    try:
        cols = ["Hour", "Day_Type", "Occupancy_Schedule"]
        return pd.read_csv(file_path, usecols=cols)
    except Exception as exc:
        print(f"   ⚠️ Error reading {year_label}: {exc}")
        return None


def compute_summary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily occupied hours and daytime occupancy fraction.

    Metrics per Day_Type:
    * Daily_Hours       — mean(Occupancy_Schedule) × 24
    * Daytime_Fraction  — mean(Occupancy_Schedule) for Hours 9–16 (09:00–17:00)

    Args:
        df: DataFrame with columns [Hour, Day_Type, Occupancy_Schedule].

    Returns:
        DataFrame with columns [Day_Type, Daily_Hours, Daytime_Fraction].
    """
    metrics: list[dict] = []
    for dtype in ["Weekday", "Weekend"]:
        subset = df[df["Day_Type"] == dtype]
        if subset.empty:
            continue
        mean_occ = subset["Occupancy_Schedule"].mean()
        daily_hours = mean_occ * 24
        daytime_subset = subset[
            (subset["Hour"] >= 9) & (subset["Hour"] <= 16)
        ]
        daytime_frac = (
            daytime_subset["Occupancy_Schedule"].mean()
            if not daytime_subset.empty
            else 0.0
        )
        metrics.append(
            {
                "Day_Type": dtype,
                "Daily_Hours": daily_hours,
                "Daytime_Fraction": daytime_frac,
            }
        )
    return pd.DataFrame(metrics)


def _plot_presence(
    ax: plt.Axes,
    df: pd.DataFrame,
    year: str,
    show_legend: bool,
) -> None:
    """Draw the hourly presence schedule curve on *ax*.

    Args:
        ax: Target Axes object.
        df: BEM schedule DataFrame for the given year.
        year: Year label used in the subplot title.
        show_legend: Whether to render the legend on this axes.
    """
    sns.lineplot(
        data=df,
        x="Hour",
        y="Occupancy_Schedule",
        hue="Day_Type",
        palette=PALETTE_PRESENCE,
        estimator="mean",
        errorbar=("sd", 1),
        ax=ax,
        legend=show_legend,
    )
    ax.set_title(
        f"{year} — Presence Schedule",
        fontsize=FS_TITLE,
        fontweight="bold",
    )
    ax.set_ylim(0, 1.05)
    ax.set_xticks(range(0, 25, 4))
    ax.set_ylabel("Occupancy Probability", fontsize=FS_AXIS_LABEL)
    ax.set_xlabel("Hour of Day", fontsize=FS_AXIS_LABEL)
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.grid(True, linestyle="--", alpha=0.6)
    if show_legend:
        legend = ax.get_legend()
        if legend:
            legend.set_title("Day Type", prop={"size": FS_LEGEND})
            for text in legend.get_texts():
                text.set_fontsize(FS_LEGEND)


def _plot_metrics(
    ax: plt.Axes,
    metrics_df: pd.DataFrame,
    year: str,
) -> None:
    """Draw the summary metrics (bar + twin-axis line) on *ax*.

    Args:
        ax: Target Axes object.
        metrics_df: DataFrame with columns [Day_Type, Daily_Hours,
            Daytime_Fraction].
        year: Year label used in the subplot title.
    """
    # --- Left axis: bar chart (daily occupied hours) ---
    sns.barplot(
        data=metrics_df,
        x="Day_Type",
        y="Daily_Hours",
        palette=BAR_COLORS,
        ax=ax,
        alpha=0.7,
        edgecolor="black",
    )
    ax.set_title(
        f"{year} — Summary Metrics",
        fontsize=FS_TITLE,
        fontweight="bold",
    )
    ax.set_ylabel("Avg. Daily Occupied Hours", fontsize=FS_AXIS_LABEL)
    ax.set_xlabel("", fontsize=FS_AXIS_LABEL)
    # 7 evenly-spaced ticks: 0, 4, 8, 12, 16, 20, 24
    _N_TICKS = 7
    ax.set_ylim(0, 24)
    ax.set_yticks(np.linspace(0, 24, _N_TICKS))
    ax.tick_params(axis="both", labelsize=FS_TICK)

    # Annotate bar heights
    for patch in ax.patches:
        ax.annotate(
            f"{patch.get_height():.1f}h",
            (patch.get_x() + patch.get_width() / 2.0, patch.get_height()),
            ha="center",
            va="bottom",
            fontsize=FS_BAR_ANNOT,
            fontweight="bold",
            xytext=(0, 4),
            textcoords="offset points",
        )

    # Fix x-axis tick labels (seaborn barplot uses numeric ticks by default)
    ax.set_xticks(range(len(metrics_df)))
    ax.set_xticklabels(metrics_df["Day_Type"], fontsize=FS_TICK)

    # --- Right axis: daytime fraction line ---
    ax_right = ax.twinx()
    x_coords = range(len(metrics_df))
    fractions = metrics_df["Daytime_Fraction"].values

    ax_right.plot(
        x_coords,
        fractions,
        color="darkred",
        marker="o",
        markersize=10,
        linewidth=2.5,
        linestyle="-",
        label="Daytime (09–17) Fraction",
    )
    for x, y in zip(x_coords, fractions):
        ax_right.annotate(
            f"{y:.2f}",
            (x, y),
            ha="center",
            va="bottom",
            fontsize=FS_POINT_ANNOT,
            color="white",
            fontweight="bold",
            xytext=(0, 7),
            textcoords="offset points",
        )
    ax_right.set_ylabel(
        "Daytime Occupancy Fraction (09–17)",
        color="darkred",
        fontsize=FS_AXIS_LABEL,
    )
    ax_right.tick_params(
        axis="y", labelcolor="darkred", labelsize=FS_TICK
    )
    ax_right.set_ylim(0, 1.0)
    # Align right-axis ticks to the same interval count as the left axis so
    # that gridlines coincide.  Suppress the right-axis grid to avoid the
    # double-grid visual artefact.
    ax_right.set_yticks(np.linspace(0, 1.0, _N_TICKS))
    ax_right.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"{v:.2f}")
    )
    ax_right.grid(False)


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    """Generate the 3 × 2 presence evolution comparison figure."""
    print("=" * 60)
    print("  PRESENCE SCHEDULE EVOLUTION PLOT GENERATOR v2 (3×2 GRID)")
    print("=" * 60)

    # Load data
    data_map: dict[str, pd.DataFrame] = {}
    for year, fpath in zip(YEARS, FILES):
        df = load_bem_data(fpath, year)
        if df is not None:
            data_map[year] = df

    # Apply global base font size — all explicit sizes multiply from this
    plt.rcParams.update({"font.size": FS_TICK})

    sns.set_theme(style="whitegrid")

    # 3 rows × 2 columns; taller figure to accommodate the extra row
    fig, axes = plt.subplots(
        3, 2, figsize=(18, 22), constrained_layout=True
    )

    for i, year in enumerate(YEARS):
        ax_left = axes[i, 0]   # Presence schedule
        ax_right_col = axes[i, 1]  # Summary metrics

        if year not in data_map:
            ax_left.text(0.5, 0.5, "No Data", ha="center", fontsize=FS_TITLE)
            ax_right_col.text(
                0.5, 0.5, "No Data", ha="center", fontsize=FS_TITLE
            )
            continue

        df = data_map[year]

        # Left subplot — presence schedule (legend only on first row)
        _plot_presence(ax_left, df, year, show_legend=(i == 0))

        # Right subplot — summary metrics
        metrics_df = compute_summary_metrics(df)
        if not metrics_df.empty:
            _plot_metrics(ax_right_col, metrics_df, year)
        else:
            ax_right_col.text(
                0.5, 0.5, "No Metrics", ha="center", fontsize=FS_TITLE
            )

    # Save
    fig.savefig(OUTPUT_FILE, dpi=300)
    print(f"\n✅ Plot saved to: {OUTPUT_FILE}")
    plt.close(fig)


if __name__ == "__main__":
    main()
