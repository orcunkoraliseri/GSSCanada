import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
import sys

# BASE DIR: ../../../ from this script
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# CONFIGURATION
# =============================================================================

FILE_BEM_2005 = BASE_DIR / "0_Occupancy/Outputs_06CEN05GSS/occToBEM/06CEN05GSS_BEM_Schedules_sample25pct.csv"
FILE_BEM_2010 = BASE_DIR / "0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv"
FILE_BEM_2015 = BASE_DIR / "0_Occupancy/Outputs_16CEN15GSS/occToBEM/16CEN15GSS_BEM_Schedules_sample25pct.csv"
FILE_BEM_2022 = BASE_DIR / "0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct.csv"
FILE_BEM_2025 = BASE_DIR / "0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv"

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "BEM_Presence_Evolution_v2.png"

YEARS = ['2005', '2010', '2015', '2022', '2025']
FILES = [FILE_BEM_2005, FILE_BEM_2010, FILE_BEM_2015, FILE_BEM_2022, FILE_BEM_2025]

# Style Colors — default (GSS cycles)
PALETTE_PRESENCE = {'Weekday': 'green', 'Weekend': 'teal'}
BAR_COLORS = {'Weekday': '#4CAF50', 'Weekend': '#009688'}  # Material Green & Teal

# Style Colors — 2025 (classified/forecasted data)
PALETTE_PRESENCE_2025 = {'Weekday': '#E64A19', 'Weekend': '#FF8F00'}  # Deep Orange & Amber
BAR_COLORS_2025 = {'Weekday': '#F4511E', 'Weekend': '#FFB300'}  # Material Deep Orange & Amber

# =============================================================================
# FUNCTIONS
# =============================================================================

def load_bem_data(file_path, year_label):
    print(f"   Loading {year_label} BEM schedules...")
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return None

    try:
        # Load columns used for both plots
        cols = ['Hour', 'Day_Type', 'Occupancy_Schedule']
        df = pd.read_csv(file_path, usecols=cols)
        return df
    except Exception as e:
        print(f"   ⚠️ Error reading {year_label}: {e}")
        return None

def compute_summary_metrics(df):
    """
    Computes:
    1. Mean Daily Occupied Hours = Mean(Occupancy_Schedule) * 24
    2. Daytime Occupancy Fraction = Mean(Occupancy_Schedule) for Hours 9-16 (09:00-17:00)
    """
    metrics = []

    for dtype in ['Weekday', 'Weekend']:
        subset = df[df['Day_Type'] == dtype]
        if subset.empty:
            continue

        # 1. Daily Occupied Hours
        mean_occ = subset['Occupancy_Schedule'].mean()
        daily_hours = mean_occ * 24

        # 2. Daytime Fraction (09:00 - 17:00 => Hours 9 to 16 inclusive)
        daytime_subset = subset[(subset['Hour'] >= 9) & (subset['Hour'] <= 16)]
        daytime_frac = daytime_subset['Occupancy_Schedule'].mean() if not daytime_subset.empty else 0

        metrics.append({
            'Day_Type': dtype,
            'Daily_Hours': daily_hours,
            'Daytime_Fraction': daytime_frac
        })

    return pd.DataFrame(metrics)

def compute_table_metrics(df):
    """
    Computes table metrics per year:
    - Weekday/Weekend occupied hours
    - Morning departure (first hour after 5am where weekday mean occ < 0.5)
    - Evening return (first hour after noon where weekday mean occ > 0.5)
    - Daytime vacancy % = (1 - daytime_fraction) * 100 for weekday 09-17
    """
    metrics = {}

    for dtype in ['Weekday', 'Weekend']:
        subset = df[df['Day_Type'] == dtype]
        if subset.empty:
            metrics[f'{dtype}_Hours'] = '—'
            continue
        metrics[f'{dtype}_Hours'] = f"{subset['Occupancy_Schedule'].mean() * 24:.1f}"

    # Weekday-specific metrics
    wd = df[df['Day_Type'] == 'Weekday']
    if not wd.empty:
        hourly = wd.groupby('Hour')['Occupancy_Schedule'].mean()

        daytime = wd[(wd['Hour'] >= 9) & (wd['Hour'] <= 16)]
        daytime_frac = daytime['Occupancy_Schedule'].mean() if not daytime.empty else 0
        metrics['Daytime_Vacancy'] = f"{(1 - daytime_frac) * 100:.1f}"

        # Morning departure: first hour (5-12) where mean occupancy drops below 0.5
        dep = next((h for h in range(5, 13) if h in hourly.index and hourly[h] < 0.5), None)
        metrics['Departure'] = f"{dep:02d}:00" if dep is not None else '—'

        # Evening return: first hour (13-22) where mean occupancy rises above 0.5
        ret = next((h for h in range(13, 23) if h in hourly.index and hourly[h] > 0.5), None)
        metrics['Return'] = f"{ret:02d}:00" if ret is not None else '—'
    else:
        metrics['Daytime_Vacancy'] = '—'
        metrics['Departure'] = '—'
        metrics['Return'] = '—'

    return metrics

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("  PRESENCE SCHEDULE EVOLUTION PLOT GENERATOR (3-ROW GRID)")
    print("="*60)

    # Load Data
    data_map = {}
    for year, fpath in zip(YEARS, FILES):
        df = load_bem_data(fpath, year)
        if df is not None:
            data_map[year] = df

    # Prepare Figure with GridSpec: 3 rows x 5 columns
    fig = plt.figure(figsize=(34, 17))
    gs = gridspec.GridSpec(3, 5, figure=fig, height_ratios=[1, 1, 1],
                           hspace=0.20, wspace=0.3)
    sns.set_theme(style="whitegrid")

    # --- LOOP THROUGH YEARS (COLUMNS) FOR ROW 0 & 1 ---
    for i, year in enumerate(YEARS):
        ax_top = fig.add_subplot(gs[0, i])
        ax_btm = fig.add_subplot(gs[1, i])

        if year not in data_map:
            ax_top.text(0.5, 0.5, "No Data", ha='center')
            ax_btm.text(0.5, 0.5, "No Data", ha='center')
            continue

        df = data_map[year]

        # Use red-orange palette for 2025 (classified/forecasted data)
        palette_line = PALETTE_PRESENCE_2025 if year == '2025' else PALETTE_PRESENCE
        palette_bar  = BAR_COLORS_2025       if year == '2025' else BAR_COLORS

        # --- ROW 0: PRESENCE CURVES ---
        sns.lineplot(
            data=df,
            x='Hour',
            y='Occupancy_Schedule',
            hue='Day_Type',
            palette=palette_line,
            estimator='mean',
            errorbar=('sd', 1),  # Mean +/- 1 SD
            ax=ax_top,
            legend=(i==0)  # Only legend on first plot
        )

        ax_top.set_title(f"{year} - Presence Schedule", fontsize=14, fontweight='bold')
        ax_top.set_ylim(0, 1.05)
        ax_top.set_xticks(range(0, 25, 4))
        ax_top.set_ylabel("Occupancy Probability" if i == 0 else "")
        ax_top.set_xlabel("")
        ax_top.grid(True, linestyle='--', alpha=0.6)

        # --- ROW 1: SUMMARY METRICS ---
        metrics_df = compute_summary_metrics(df)

        if not metrics_df.empty:
            # Dual Axis Plot

            # 1. Bar Chart (Daily Hours) - Left Axis
            sns.barplot(
                data=metrics_df,
                x='Day_Type',
                y='Daily_Hours',
                palette=palette_bar,
                ax=ax_btm,
                alpha=0.7,
                edgecolor='black'
            )

            ax_btm.set_title(f"{year} - Summary Metrics", fontsize=12, fontweight='bold')
            ax_btm.set_ylabel("Avg. Daily Occupied Hours" if i == 0 else "")
            ax_btm.set_xlabel("")
            ax_btm.set_ylim(0, 20)

            # Annotate bars
            for p in ax_btm.patches:
                ax_btm.annotate(f'{p.get_height():.1f}h',
                               (p.get_x() + p.get_width() / 2., p.get_height()),
                               ha='center', va='bottom', fontsize=10,
                               fontweight='bold', xytext=(0, 3),
                               textcoords='offset points')

            # 2. Line/Point Chart (Daytime Fraction) - Right Axis
            ax_right = ax_btm.twinx()

            x_coords = range(len(metrics_df))
            fractions = metrics_df['Daytime_Fraction'].values

            ax_right.plot(x_coords, fractions, color='darkred', marker='o', markersize=8, linewidth=2, linestyle='-', label='Daytime (09-17) Fraction')

            # Label points
            for x, y in zip(x_coords, fractions):
                ax_right.annotate(f'{y:.2f}',
                                 (x, y),
                                 ha='center', va='bottom',
                                 fontsize=14, color='white', fontweight='bold',
                                 xytext=(0, 6), textcoords='offset points')

            ax_right.set_ylabel("Daytime Occupancy Fraction (09-17)", color='darkred')
            ax_right.tick_params(axis='y', labelcolor='darkred')
            ax_right.set_ylim(0, 1.0)

            # Clean up x-axis labels from seaborn
            ax_btm.set_xticklabels(metrics_df['Day_Type'])

        else:
             ax_btm.text(0.5, 0.5, "No Metrics", ha='center')

    # --- EXPORT METRICS TABLE AS CSV ---
    print("\n3. Computing metrics table...")

    # DOE prototype default baseline (hardcoded reference values)
    table_metrics = {
        'Default': {
            'Weekday_Hours': '16.4', 'Weekend_Hours': '16.4',
            'Departure': '08:00', 'Return': '18:00', 'Daytime_Vacancy': '74.4'
        }
    }
    for year in YEARS:
        if year in data_map:
            table_metrics[year] = compute_table_metrics(data_map[year])

    all_cols    = ['Default'] + YEARS
    metric_keys = ['Weekday_Hours', 'Weekend_Hours', 'Departure', 'Return', 'Daytime_Vacancy']
    row_labels  = [
        'Weekday occupied hours (h)',
        'Weekend occupied hours (h)',
        'Morning departure',
        'Evening return',
        'Daytime vacancy (09-17) %',
    ]

    csv_rows = []
    for key, label in zip(metric_keys, row_labels):
        row = {'Metric': label}
        for col in all_cols:
            row[col] = table_metrics.get(col, {}).get(key, '—')
        csv_rows.append(row)

    csv_path = OUTPUT_FILE.with_suffix('.csv')
    pd.DataFrame(csv_rows).to_csv(csv_path, index=False)
    print(f"   ✅ Table saved to: {csv_path}")

    # --- ROW 2: PER-YEAR POINT PLOTS (Occupied Hours & Daytime Vacancy) ---
    default_weekday = float(table_metrics['Default']['Weekday_Hours'])
    default_vacancy = float(table_metrics['Default']['Daytime_Vacancy'])

    hours_ylim = (10, 20)
    perc_ylim  = (35, 90)

    evo_lines, evo_labels = [], []

    for i, year in enumerate(YEARS):
        ax1 = fig.add_subplot(gs[2, i])
        ax2 = ax1.twinx()

        m = table_metrics.get(year)
        if m is None:
            ax1.text(0.5, 0.5, "No Data", ha='center', transform=ax1.transAxes)
            continue

        try:
            wkd_val = float(m['Weekday_Hours'])
        except (ValueError, KeyError):
            wkd_val = np.nan
        try:
            wnd_val = float(m['Weekend_Hours'])
        except (ValueError, KeyError):
            wnd_val = np.nan
        try:
            vac_val = float(m['Daytime_Vacancy'])
        except (ValueError, KeyError):
            vac_val = np.nan

        # Plot single points (no connecting lines)
        l1 = ax1.plot([0], [wkd_val], marker='o', color='#1f77b4', linestyle='None',
                       markersize=14, label='Weekday occupied hours (h)')
        l2 = ax1.plot([0], [wnd_val], marker='s', color='#ff7f0e', linestyle='None',
                       markersize=14, label='Weekend occupied hours (h)')
        l4 = ax2.plot([0], [vac_val], marker='^', color='#2ca02c', linestyle='None',
                       markersize=14, label='Daytime vacancy (%)')

        # Default baselines
        l3 = ax1.axhline(y=default_weekday, color='#1f77b4', linestyle='--', alpha=0.3,
                          label='Default Hours')
        l5 = ax2.axhline(y=default_vacancy, color='#2ca02c', linestyle='--', alpha=0.3,
                          label='Default Vacancy')

        # Axis limits & formatting
        ax1.set_ylim(hours_ylim)
        ax2.set_ylim(perc_ylim)
        ax1.set_xticks([0])
        ax1.set_xticklabels([year], fontweight='bold', fontsize=11)
        ax1.set_title(f"{year} - Metrics", fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.4)

        # Only show left Y-labels on first subplot, right on last
        if i == 0:
            ax1.set_ylabel('Hours', color='#1f77b4', fontweight='bold')
            ax1.tick_params(axis='y', labelcolor='#1f77b4')
        else:
            ax1.set_yticklabels([])
            ax1.tick_params(axis='y', length=0)

        if i == len(YEARS) - 1:
            ax2.set_ylabel('Percentage (%)', color='#2ca02c', fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='#2ca02c')
        else:
            ax2.set_yticklabels([])
            ax2.tick_params(axis='y', length=0)

        # Collect legend items from first iteration
        if i == 0:
            evo_lines = l1 + l2 + [l3] + l4 + [l5]
            evo_labels = [l.get_label() for l in evo_lines]

    # Add a single-line legend below the 3rd row
    if evo_lines:
        fig.subplots_adjust(bottom=0.07)
        fig.legend(evo_lines, evo_labels, loc='lower center',
                   bbox_to_anchor=(0.5, 0.01), ncol=5, framealpha=0.95,
                   fontsize=13)

    # Save
    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"\n✅ Plot saved to: {OUTPUT_FILE}")
    plt.close(fig)

if __name__ == "__main__":
    main()
