import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# BASE DIR: ../../../ from this script (eSim_occ_utils/plotting/script.py -> eSim/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add eSim root to sys.path to import eSim_bem_utils
sys.path.append(str(BASE_DIR))

try:
    from eSim_bem_utils import idf_optimizer
except ImportError:
    print("Error: Could not import eSim_bem_utils. Ensure script is run from project root or correct path.")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

GSS_2025_FILE = BASE_DIR / "0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "Fig_4_1_3_v2.png"

# Plot Styling
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.4)

COLORS = {
    'Default': '#D62728',   # Red
    'GSS': '#1F77B4',       # Blue
    'Fill_Over': '#ffcccc', # Light Red (Default > GSS)
    'Fill_Under': '#cce5ff' # Light Blue (GSS > Default)
}

# =============================================================================
# DATA LOADING
# =============================================================================

def load_default_schedules():
    """Load DOE MidRise Apartment schedules from schedule.json via eSim_bem_utils."""
    print("1. Loading Default Schedules...")
    try:
        defaults = idf_optimizer.load_standard_residential_schedules(verbose=True)

        occ = np.array(defaults['occupancy']['Weekday'])
        met = np.array([defaults['activity']] * 24)  # Constant 95W usually

        return occ, met
    except Exception as e:
        print(f"Error loading defaults: {e}")
        return None, None

def load_gss_2025_data():
    """Load 2025 GSS Weekday data."""
    print("2. Loading 2025 GSS Data...")
    try:
        cols = ['Hour', 'Day_Type', 'Occupancy_Schedule', 'Metabolic_Rate']
        df = pd.read_csv(GSS_2025_FILE, usecols=cols)

        # Filter Weekday
        df_wd = df[df['Day_Type'] == 'Weekday']

        # Compute Hourly Stats
        occ_stats = df_wd.groupby('Hour')['Occupancy_Schedule'].agg(['mean', 'std'])
        met_stats = df_wd.groupby('Hour')['Metabolic_Rate'].agg(['mean', 'std'])

        return occ_stats, met_stats

    except Exception as e:
        print(f"Error loading GSS data: {e}")
        return None, None

# =============================================================================
# ANNOTATION HELPERS
# =============================================================================

def annotate_zone(ax, x_start, x_end, text, y_pos, color='black', arrow_y=None):
    """Add an annotation for a specific time zone."""
    mid_x = (x_start + x_end) / 2

    if arrow_y is not None:
        ax.annotate(text, xy=(mid_x, arrow_y), xytext=(mid_x, y_pos),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                    ha='center', va='center', fontsize=10, color=color,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.9))
    else:
        ax.text(mid_x, y_pos, text, ha='center', va='center', fontsize=10, color=color,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.9))

# =============================================================================
# BAR CHART HELPER
# =============================================================================

def create_grouped_bars(ax, labels, default_vals, gss_vals, title, ylabel, ylim):
    """Draw a grouped bar chart comparing Default vs 2025 GSS on a subplot axis."""
    bar_width = 0.35
    x = np.arange(len(labels))

    rects1 = ax.bar(x - bar_width / 2, default_vals, bar_width,
                    label='Default', color=COLORS['Fill_Over'],
                    edgecolor=COLORS['Default'], linewidth=1.5)
    rects2 = ax.bar(x + bar_width / 2, gss_vals, bar_width,
                    label='2025 GSS', color=COLORS['Fill_Under'],
                    edgecolor=COLORS['GSS'], linewidth=1.5)

    ax.set_ylabel(ylabel, fontweight='bold')
    ax.set_title(title, fontweight='bold', loc='left')
    ax.set_xticks(x)
    wrapped_labels = [lbl.replace(' ', '\n') for lbl in labels]
    ax.set_xticklabels(wrapped_labels, fontsize=9)
    ax.legend(fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.set_ylim(*ylim)

    ax.bar_label(rects1, padding=3, fmt='%.3g', fontsize=9)
    ax.bar_label(rects2, padding=3, fmt='%.3g', fontsize=9)

# =============================================================================
# TABLE 4.1.3 — Numerical summary data
# =============================================================================

SUMMARY = {
    # Occupancy ratios (0-1): weekday, weekend
    'occ_labels':   ['Weekday\nOccupancy', 'Weekend\nOccupancy'],
    'occ_default':  [0.684, 0.684],
    'occ_gss':      [0.465, 0.502],

    # Daytime occupancy (%)
    'day_labels':   ['Daytime\nOcc (09-17)'],
    'day_default':  [25.60],
    'day_gss':      [27.60],

    # Metabolic rates (W)
    'met_labels':   ['Mean\nMet. Rate', 'Peak\nMet. Rate'],
    'met_default':  [95.0, 95.0],
    'met_gss':      [72.7, 95.0],
}

# =============================================================================
# MAIN PLOTTING
# =============================================================================

def generate_plot():
    # 1. Load Data
    def_occ, def_met = load_default_schedules()
    gss_occ, gss_met = load_gss_2025_data()

    if def_occ is None or gss_occ is None:
        return

    hours = np.arange(24)

    # 2. Create Figure — 1 row, 5 columns
    fig, axes = plt.subplots(1, 5, figsize=(28, 6), constrained_layout=True)

    # -------------------------------------------------------------------------
    # Panel (a): Occupancy Fraction  [col 0]
    # -------------------------------------------------------------------------
    ax = axes[0]

    ax.plot(hours, def_occ, color=COLORS['Default'], linestyle='--', linewidth=3,
            label='Default (DOE MidRise)')
    ax.plot(hours, gss_occ['mean'], color=COLORS['GSS'], linewidth=3, label='2025 GSS (Mean)')

    ax.fill_between(hours, gss_occ['mean'] - gss_occ['std'], gss_occ['mean'] + gss_occ['std'],
                    color=COLORS['GSS'], alpha=0.15, label='±1 Std Dev')

    ax.fill_between(hours, def_occ, gss_occ['mean'], where=(def_occ > gss_occ['mean']),
                    color=COLORS['Fill_Over'], alpha=0.5, interpolate=True)
    ax.fill_between(hours, def_occ, gss_occ['mean'], where=(gss_occ['mean'] > def_occ),
                    color=COLORS['Fill_Under'], alpha=0.5, interpolate=True)

    annotate_zone(ax, 1, 5, "Night Overestimate\n(+39%)", 0.8, color=COLORS['Default'], arrow_y=0.8)
    annotate_zone(ax, 7, 9, "Morning\nTransition", 0.55, color='gray', arrow_y=0.45)

    ax.set_title("(a) Hourly Occupancy Fraction", fontweight='bold', loc='left')
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Occupancy Fraction")
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(loc='lower left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)

    # -------------------------------------------------------------------------
    # Panel (b): Metabolic Rate  [col 1]
    # -------------------------------------------------------------------------
    ax = axes[1]

    ax.plot(hours, def_met, color=COLORS['Default'], linestyle='--', linewidth=3,
            label='Default (95 W)')
    ax.plot(hours, gss_met['mean'], color=COLORS['GSS'], linewidth=3, label='2025 GSS (Mean)')

    ax.fill_between(hours, gss_met['mean'] - gss_met['std'], gss_met['mean'] + gss_met['std'],
                    color=COLORS['GSS'], alpha=0.15, label='±1 Std Dev')

    ax.fill_between(hours, def_met, gss_met['mean'], where=(def_met > gss_met['mean']),
                    color=COLORS['Fill_Over'], alpha=0.5, interpolate=True)
    ax.fill_between(hours, def_met, gss_met['mean'], where=(gss_met['mean'] > def_met),
                    color=COLORS['Fill_Under'], alpha=0.5, interpolate=True)

    annotate_zone(ax, 1, 5, "Sleep Phase\n(70W vs 95W)", 85, color='black', arrow_y=82)
    annotate_zone(ax, 10, 14, "Midday Overestimate\n(+60%)", 75, color=COLORS['Default'], arrow_y=75)

    ax.set_title("(b) Hourly Metabolic Rate (W/person)", fontweight='bold', loc='left')
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Metabolic Rate (W)")
    ax.set_ylim(40, 160)
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)

    # -------------------------------------------------------------------------
    # Panel (c): Mean Occupancy Ratio  [col 2]
    # -------------------------------------------------------------------------
    create_grouped_bars(
        axes[2],
        labels=SUMMARY['occ_labels'],
        default_vals=SUMMARY['occ_default'],
        gss_vals=SUMMARY['occ_gss'],
        title='(c) Mean Occupancy\n(Ratio 0–1)',
        ylabel='Occupancy Ratio',
        ylim=(0, 0.85),
    )

    # -------------------------------------------------------------------------
    # Panel (d): Daytime Occupancy %  [col 3]
    # -------------------------------------------------------------------------
    create_grouped_bars(
        axes[3],
        labels=SUMMARY['day_labels'],
        default_vals=SUMMARY['day_default'],
        gss_vals=SUMMARY['day_gss'],
        title='(d) Daytime Occupancy\n(09:00–17:00)',
        ylabel='Percentage (%)',
        ylim=(0, 35),
    )

    # -------------------------------------------------------------------------
    # Panel (e): Metabolic Rates (W)  [col 4]
    # -------------------------------------------------------------------------
    create_grouped_bars(
        axes[4],
        labels=SUMMARY['met_labels'],
        default_vals=SUMMARY['met_default'],
        gss_vals=SUMMARY['met_gss'],
        title='(e) Metabolic Rates\n(W/person)',
        ylabel='Watts (W)',
        ylim=(0, 115),
    )

    # -------------------------------------------------------------------------
    # Global title and save
    # -------------------------------------------------------------------------
    fig.suptitle(
        'Table 4.1.3 — Schedule Discrepancies: Default vs 2025 GSS-Derived Patterns',
        fontsize=14, fontweight='bold', y=1.02
    )

    print(f"3. Saving plot to: {OUTPUT_FILE}")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print("Done.")

if __name__ == "__main__":
    generate_plot()
