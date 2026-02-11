import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# BASE DIR: ../../../ from this script (occ_utils/plotting/script.py -> eSim/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add eSim root to sys.path to import bem_utils
sys.path.append(str(BASE_DIR))

try:
    from bem_utils import idf_optimizer
except ImportError:
    print("Error: Could not import bem_utils. Ensure script is run from project root or correct path.")
    sys.exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

GSS_2025_FILE = BASE_DIR / "BEM_Setup/BEM_Schedules_2025.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "Fig_4_1_3_Default_vs_Classification.png"

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
    """Load DOE MidRise Apartment schedules from schedule.json via bem_utils."""
    print("1. Loading Default Schedules...")
    try:
        # idf_optimizer loads from BEM_Setup/Templates/schedule.json
        defaults = idf_optimizer.load_standard_residential_schedules(verbose=True)
        
        # Extract Weekday profiles
        occ = np.array(defaults['occupancy']['Weekday'])
        met = np.array([defaults['activity']] * 24) # Constant 95W usually
        
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
# MAIN PLOTTING
# =============================================================================

def generate_plot():
    # 1. Load Data
    def_occ, def_met = load_default_schedules()
    gss_occ, gss_met = load_gss_2025_data()
    
    if def_occ is None or gss_occ is None:
        return

    hours = np.arange(24)
    
    # 2. Create Figure (1x2 Horizontal)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), constrained_layout=True)
    
    # --- Panel (a): Occupancy Fraction ---
    ax = axes[0]
    
    # Plot Lines
    ax.plot(hours, def_occ, color=COLORS['Default'], linestyle='--', linewidth=3, label='Default (DOE MidRise)')
    ax.plot(hours, gss_occ['mean'], color=COLORS['GSS'], linewidth=3, label='2025 GSS (Mean)')
    
    # Shading (Std Dev for GSS)
    ax.fill_between(hours, gss_occ['mean'] - gss_occ['std'], gss_occ['mean'] + gss_occ['std'],
                    color=COLORS['GSS'], alpha=0.15, label='±1 Std Dev')
    
    # Discrepancy Shading
    # Red where Default > GSS
    ax.fill_between(hours, def_occ, gss_occ['mean'], where=(def_occ > gss_occ['mean']),
                    color=COLORS['Fill_Over'], alpha=0.5, interpolate=True)
    # Blue where GSS > Default
    ax.fill_between(hours, def_occ, gss_occ['mean'], where=(gss_occ['mean'] > def_occ),
                    color=COLORS['Fill_Under'], alpha=0.5, interpolate=True)
    
    # Annotations
    # Night Overestimate (0-6)
    annotate_zone(ax, 1, 5, "Night Overestimate\n(+39%)", 0.8, color=COLORS['Default'], arrow_y=0.8)
    
    # Morning Transition (drop mismatch)
    # Default drops sharply at 8am. GSS is gradual.
    annotate_zone(ax, 7, 9, "Morning\nTransition", 0.55, color='gray', arrow_y=0.45)
    
    # Styling
    ax.set_title("(a) Hourly Occupancy Fraction", fontweight='bold', loc='left')
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Occupancy Fraction")
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(loc='lower left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # --- Panel (b): Metabolic Rate ---
    ax = axes[1]
    
    # Plot Lines
    ax.plot(hours, def_met, color=COLORS['Default'], linestyle='--', linewidth=3, label='Default (95 W)')
    ax.plot(hours, gss_met['mean'], color=COLORS['GSS'], linewidth=3, label='2025 GSS (Mean)')
    
    # Shading (Std Dev for GSS)
    ax.fill_between(hours, gss_met['mean'] - gss_met['std'], gss_met['mean'] + gss_met['std'],
                    color=COLORS['GSS'], alpha=0.15, label='±1 Std Dev')
    
    # Discrepancy Shading
    ax.fill_between(hours, def_met, gss_met['mean'], where=(def_met > gss_met['mean']),
                    color=COLORS['Fill_Over'], alpha=0.5, interpolate=True)
    ax.fill_between(hours, def_met, gss_met['mean'], where=(gss_met['mean'] > def_met),
                    color=COLORS['Fill_Under'], alpha=0.5, interpolate=True)

    # Annotations
    # Sleep Phase (0-6) - GSS ~70W vs Default 95W
    annotate_zone(ax, 1, 5, "Sleep Phase\n(70W vs 95W)", 85, color='black', arrow_y=82)

    # Midday Overestimate (big gap)
    annotate_zone(ax, 10, 14, "Midday Overestimate\n(+60%)", 75, color=COLORS['Default'], arrow_y=75)
    
    # Styling
    ax.set_title("(b) Hourly Metabolic Rate (W/person)", fontweight='bold', loc='left')
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Metabolic Rate (W)")
    ax.set_ylim(40, 160) # GSS Mean goes down to ~57, +std to ~120. Default 95.
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 25, 4))
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Save
    print(f"3. Saving plot to: {OUTPUT_FILE}")
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print("Done.")

if __name__ == "__main__":
    generate_plot()
