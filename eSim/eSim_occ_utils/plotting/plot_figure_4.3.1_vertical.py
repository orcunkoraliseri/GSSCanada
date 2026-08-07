"""Figure 4.3.1 — Energy Demand by City, Version 2.

Changes vs. v1
--------------
* Grid layout changed from 2 rows × 3 columns  (rows = load type)
  to **3 rows × 2 columns** (rows = city, columns = Heating / Cooling).
  Row 0 → Toronto (5A), Row 1 → Montreal (6A), Row 2 → Winnipeg (7).
* Font sizes doubled for research-paper legibility.
* Colour palette upgraded to vivid, fully-opaque shades with subtle bar
  edges and cleaner spines (top/right removed).
* Uniform y-axis limits shared per column (Heating / Cooling) so city
  rows are directly comparable.
"""

import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# =============================================================================
# FONT-SIZE CONSTANTS  (roughly 2× the original values)
# =============================================================================

FS_TITLE: int = 22       # subplot titles
FS_AXIS_LABEL: int = 18  # x/y axis labels
FS_TICK: int = 16        # tick labels
FS_ANNOT: int = 16       # percentage annotations

# =============================================================================
# COLOUR PALETTE
# =============================================================================

CLR_HEATING: str = "#d62728"      # muted red (matches v1)
CLR_HEATING_EDGE: str = "#d62728" # same, no separate edge
CLR_COOLING: str = "#1f77b4"      # muted blue (matches v1)
CLR_COOLING_EDGE: str = "#1f77b4" # same, no separate edge
BAR_ALPHA: float = 0.6            # matches v1 transparency

CLR_ANNOT: str = "#2C3E50"        # near-black for percentage labels
CLR_GRID: str = "#dde1e7"         # light grey grid


# =============================================================================
# DATA PARSING
# =============================================================================

def parse_report_csv(file_path: str) -> dict | None:
    """Parse a Comparative Analysis Report CSV for Annual Energy Demand.

    Args:
        file_path: Absolute path to the CSV file.

    Returns:
        Dict mapping scenario → {load_type → (mean, std)}, or None on
        failure.  Example::

            {
                "Default": {"Heating": (67.3, 1.2), "Cooling": (1.83, 0.05)},
                "2025":    {"Heating": (71.2, 2.1), "Cooling": (1.61, 0.12)},
            }
    """
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return None

    metrics: dict = {}

    try:
        with open(file_path, "r", encoding="latin-1") as fh:
            lines = fh.readlines()

        # Locate the "Annual Energy Demand Metrics" section header.
        start_idx = -1
        for i, line in enumerate(lines):
            if "[SECTION] Annual Energy Demand Metrics (Aggregated)" in line:
                start_idx = i + 2  # skip section header + column header
                break

        if start_idx == -1:
            print(f"Error: Annual Metrics section not found in {file_path}")
            return None

        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                break
            parts = line.split(",")
            if len(parts) < 4:
                continue

            category, scenario = parts[0], parts[1]
            try:
                mean_val = float(parts[2])
                std_val = float(parts[3])
            except ValueError:
                continue

            if category in ("Heating", "Cooling"):
                metrics.setdefault(scenario, {})[category] = (
                    mean_val,
                    std_val,
                )

    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing {file_path}: {exc}")
        return None

    return metrics


# =============================================================================
# PLOTTING
# =============================================================================

def plot_figure(data: dict, output_dir: str) -> None:
    """Generate Figure 4.3.1 v2 — 3 rows (cities) × 2 columns (load types).

    Args:
        data: Nested dict ``{city_name: {scenario: {load_type: (mean, std)}}}``.
        output_dir: Directory where the PNG is saved.
    """
    cities: list[str] = ["Toronto (5A)", "Montreal (6A)", "Winnipeg (7)"]
    scenarios: list[str] = ["Default", "2005", "2015", "2025"]
    scenario_labels: list[str] = ["Def", "'05", "'15", "'25"]
    load_types: list[str] = ["Heating", "Cooling"]
    colours: dict[str, tuple[str, str]] = {
        "Heating": (CLR_HEATING, CLR_HEATING_EDGE),
        "Cooling": (CLR_COOLING, CLR_COOLING_EDGE),
    }

    # ── Figure setup ──────────────────────────────────────────────────────────
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig, axes = plt.subplots(
        3, 2,
        figsize=(14, 16),
        sharex=True,
    )
    fig.subplots_adjust(hspace=0.38, wspace=0.12)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _get_vals(
        city_d: dict, load: str
    ) -> tuple[list[float], list[float]]:
        """Extract ordered means and stds for all scenarios."""
        means, stds = [], []
        for s in scenarios:
            v = city_d.get(s, {}).get(load, (0.0, 0.0))
            means.append(v[0])
            stds.append(v[1])
        return means, stds

    # Compute shared y-limits per column so cities are directly comparable.
    col_ymaxes: dict[str, float] = {lt: 0.0 for lt in load_types}
    for city in cities:
        city_d = data.get(city, {})
        for lt in load_types:
            means, stds = _get_vals(city_d, lt)
            # Upper envelope: mean + 1 std
            max_env = max(m + s for m, s in zip(means, stds)) if means else 0
            col_ymaxes[lt] = max(col_ymaxes[lt], max_env)

    ylims: dict[str, tuple[float, float]] = {
        lt: (0.0, col_ymaxes[lt] * 1.25) for lt in load_types
    }

    index = np.arange(len(scenarios))
    bar_width = 0.6

    # ── Draw subplots ─────────────────────────────────────────────────────────
    for row, city in enumerate(cities):
        city_d = data.get(city, {})

        for col, load in enumerate(load_types):
            ax = axes[row, col]
            face_clr, edge_clr = colours[load]
            means, stds = _get_vals(city_d, load)
            baseline = means[0] if means else 0.0

            # Bars with error caps
            ax.bar(
                index,
                means,
                bar_width,
                yerr=stds,
                capsize=5,
                error_kw={"elinewidth": 1.5, "capthick": 1.5,
                           "ecolor": "#555"},
                color=face_clr,
                alpha=BAR_ALPHA,
                label=load,
                zorder=3,
            )

            # Percentage-change annotations (skip baseline bar)
            ymax = ylims[load][1]
            for i, (val, std) in enumerate(zip(means, stds)):
                if i == 0 or baseline <= 0:
                    continue
                pct = (val - baseline) / baseline * 100
                y_pos = (val + std) + ymax * 0.035
                ax.text(
                    i, y_pos,
                    f"{pct:+.1f}%",
                    ha="center", va="bottom",
                    fontsize=FS_ANNOT, fontweight="bold",
                    color=CLR_ANNOT,
                )

            # Axes styling
            ax.set_ylim(ylims[load])
            ax.set_xticks(index)
            ax.set_xticklabels(scenario_labels, fontsize=FS_TICK)
            ax.tick_params(axis="y", labelsize=FS_TICK)
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"{v:.0f}")
            )
            ax.grid(
                axis="y",
                color=CLR_GRID,
                linestyle="--",
                linewidth=0.8,
                zorder=0,
            )
            ax.set_axisbelow(True)

            # Title: "City — Load Type"
            ax.set_title(
                f"{city} — {load}",
                fontsize=FS_TITLE,
                fontweight="bold",
                pad=10,
            )

            # Y-axis label on the leftmost column only
            if col == 0:
                ax.set_ylabel(
                    f"{load} (kWh/m²)",
                    fontsize=FS_AXIS_LABEL,
                    labelpad=8,
                )
            else:
                ax.tick_params(labelleft=False)

    # ── Save ──────────────────────────────────────────────────────────────────
    output_path = os.path.join(output_dir, "Figure_4.3.1_Energy_Demand_v2.png")
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Figure saved to: {output_path}")
    plt.close(fig)


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """Load city CSVs and generate Figure 4.3.1 v2."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    base_dir = os.path.join(project_root, "BEM_Setup", "SimResults")
    output_dir = script_dir  # save alongside the script

    os.makedirs(output_dir, exist_ok=True)

    locations: dict[str, str] = {
        "Toronto (5A)": os.path.join(
            "MonteCarlo_N60_1771006398",
            "Ontario_Comparative_Analysis_Report.csv",
        ),
        "Montreal (6A)": os.path.join(
            "MonteCarlo_N60_1771001406",
            "Quebec_Comparative_Analysis_Report.csv",
        ),
        "Winnipeg (7)": os.path.join(
            "MonteCarlo_N60_1771010812",
            "Prairies_Comparative_Analysis_Report.csv",
        ),
    }

    all_data: dict = {}
    print(f"Reading data from: {base_dir}")

    for city, rel_path in locations.items():
        full_path = os.path.join(base_dir, rel_path)
        metrics = parse_report_csv(full_path)
        if metrics:
            all_data[city] = metrics
        else:
            print(f"Failed to load data for {city} ({full_path})")

    if all_data:
        plot_figure(all_data, output_dir)
    else:
        print("No data loaded. Exiting.")


if __name__ == "__main__":
    main()
