#!/usr/bin/env python3
"""
step9_loadshape_plots.py — Diurnal load-shape and peak-hour-shift figures for Step 9.

Reads 3 CSVs from Step9_docs/ (downloaded from Speed after s9_loadshape job):
  loadshape_profiles.csv
  peak_hours.csv
  peak_shift_summary.csv

Produces:
  figS6_diurnal_equip.png  — equipment diurnal, 4 archetype panels, 2022
  figS7_peak_shift.png     — equipment peak-hour shift lollipop, 2022, 24 cells
  figS8_diurnal_light.png  — lighting diurnal, 4 archetype panels, 2022

Usage:
  python step9_loadshape_plots.py
  python step9_loadshape_plots.py --profiles path/to/loadshape_profiles.csv \
                                  --peaks path/to/peak_hours.csv \
                                  --shift path/to/peak_shift_summary.csv \
                                  --out path/to/figures/
"""
import argparse
import csv
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = Path(__file__).resolve().parent

DTYPE_COLORS = {
    'SingleD':       '#2166ac',
    'OtherDwelling': '#4dac26',
    'MidRise':       '#d6604d',
    'HighRise':      '#762a83',
}
DTYPE_ORDER = ['SingleD', 'OtherDwelling', 'MidRise', 'HighRise']


def _cell_label(cell):
    arch, city = cell.split('__')
    city_short = city.replace('_', ' ')
    return f'{arch}\n{city_short}'


def load_profiles(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            r['hour_of_day'] = int(r['hour_of_day'])
            r['n_hh'] = int(r['n_hh'])
            for col in ('equip_bldg_W', 'equip_zone_W', 'light_bldg_W', 'light_zone_W', 'facility_W'):
                r[col] = float(r[col])
            rows.append(r)
    return rows


def load_peak_hours(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            for col in ('equip_bldg_peak_h', 'equip_zone_peak_h',
                        'light_bldg_peak_h', 'light_zone_peak_h', 'n_hh'):
                r[col] = int(r[col])
            rows.append(r)
    return rows


def load_peak_shift(path):
    rows = []
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            for col in ('equip_bldg_shift', 'equip_zone_shift',
                        'light_bldg_shift', 'light_zone_shift'):
                r[col] = int(r[col])
            rows.append(r)
    return rows


def _archetype_mean_diurnal(profiles, year, arm, metric):
    """Return dict: {dtype: [24 floats]} — mean W across 6 cities per archetype."""
    result = {}
    for dtype in DTYPE_ORDER:
        sums = [0.0] * 24
        cnts = [0] * 24
        for r in profiles:
            if r['year'] != year or r['arm'] != arm:
                continue
            if r['cell'].split('__')[0] != dtype:
                continue
            h = r['hour_of_day']
            sums[h] += r[metric]
            cnts[h] += 1
        result[dtype] = [sums[h] / cnts[h] if cnts[h] > 0 else 0.0 for h in range(24)]
    return result


# ── Fig S6 — Equipment diurnal, 4 archetype panels ───────────────────────────
def fig_s6_diurnal_equip(profiles, out_dir):
    bl_by_dtype = _archetype_mean_diurnal(profiles, '2022', 'baseline', 'equip_bldg_W')
    ac_by_dtype = _archetype_mean_diurnal(profiles, '2022', 'activity', 'equip_bldg_W')

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=False)
    hours = list(range(24))

    for ax_idx, dtype in enumerate(DTYPE_ORDER):
        ax = axes[ax_idx // 2][ax_idx % 2]
        col = DTYPE_COLORS[dtype]
        bl = bl_by_dtype[dtype]
        ac = ac_by_dtype[dtype]

        bl_peak = bl.index(max(bl))
        ac_peak = ac.index(max(ac))

        # Normalize each profile to its own daily mean -> pure shape/timing comparison.
        # Magnitudes are NOT comparable for multi-unit (baseline = whole building;
        # activity = occupancy unit + flat baseload of other units); calibrated annual
        # magnitudes are in figS1. Normalization is monotonic -> peak hour unchanged.
        bl_m = (sum(bl) / 24.0) or 1.0
        ac_m = (sum(ac) / 24.0) or 1.0
        bl_n = [v / bl_m for v in bl]
        ac_n = [v / ac_m for v in ac]

        ax.plot(hours, bl_n, color='gray', lw=1.8, label='Baseline')
        ax.plot(hours, ac_n, color=col,    lw=1.8, label='Activity')
        ax.axhline(1.0, color='black', lw=0.5, alpha=0.25)
        ax.axvline(bl_peak, color='gray', linestyle='--', lw=0.9, alpha=0.8,
                   label=f'BL peak h{bl_peak}')
        ax.axvline(ac_peak, color=col,    linestyle='--', lw=0.9, alpha=0.8,
                   label=f'AC peak h{ac_peak}')

        shift = ac_peak - bl_peak
        shift_str = f'{shift:+d} h' if shift != 0 else 'no shift'
        ax.set_title(f'{dtype}  (BL h{bl_peak} → AC h{ac_peak}, {shift_str})', fontsize=10)
        ax.set_xlabel('Hour of day')
        ax.set_ylabel('Equipment load (x daily mean)')
        ax.set_xticks(range(0, 24, 4))
        ax.legend(fontsize=7.5, loc='upper left')

    fig.suptitle('Fig 7b - Equipment diurnal load shape, 2022 (normalized to daily mean)\n'
                 'Gray = baseline (6-city mean), coloured = activity; dashed = peak hour; '
                 'shape only - calibrated magnitudes in figS1',
                 fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = os.path.join(out_dir, 'figS6_diurnal_equip.png')
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f'  Saved: {out}')


# ── Fig S7 — Equipment peak-hour shift lollipop, 24 cells ────────────────────
def fig_s7_peak_shift(peak_hours, out_dir):
    ph22 = [r for r in peak_hours if r['year'] == '2022']
    bl_map = {r['cell']: r for r in ph22 if r['arm'] == 'baseline'}
    ac_map = {r['cell']: r for r in ph22 if r['arm'] == 'activity'}

    cells = sorted(
        set(bl_map.keys()) & set(ac_map.keys()),
        key=lambda c: (DTYPE_ORDER.index(c.split('__')[0])
                       if c.split('__')[0] in DTYPE_ORDER else 99, c)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(cells))

    for i, cell in enumerate(cells):
        dtype = cell.split('__')[0]
        col = DTYPE_COLORS.get(dtype, 'gray')
        bl_h = bl_map[cell]['equip_bldg_peak_h']
        ac_h = ac_map[cell]['equip_bldg_peak_h']

        # Vertical dumbbell: circle at baseline, diamond at activity
        ax.plot([x[i], x[i]], [bl_h, ac_h], color=col, lw=1.6, alpha=0.7, zorder=3)
        ax.scatter(x[i], bl_h, color='white', edgecolors='gray', s=55, zorder=5,
                   marker='o', linewidths=1.4)
        ax.scatter(x[i], ac_h, color=col,     s=55,  zorder=5, marker='D')

    ax.set_xticks(x)
    ax.set_xticklabels([_cell_label(c) for c in cells], fontsize=5.5, rotation=45, ha='right')
    ax.set_yticks(range(0, 24, 2))
    ax.set_ylabel('Equipment peak hour-of-day')
    ax.set_title(
        'Fig S7 - Equipment baseline -> activity peak-hour shift, 2022 (all 24 cells)\n'
        'Open circle = baseline peak; filled diamond = activity peak; '
        'downward shift = peak moves earlier (evening -> early afternoon)',
        fontsize=10
    )

    # Archetype separator lines
    dtype_counts = {}
    for c in cells:
        d = c.split('__')[0]
        dtype_counts[d] = dtype_counts.get(d, 0) + 1
    sep = 0
    for d in DTYPE_ORDER[:-1]:
        sep += dtype_counts.get(d, 0)
        ax.axvline(sep - 0.5, color='black', lw=0.6, linestyle=':', alpha=0.5)

    handles = [mpatches.Patch(color=DTYPE_COLORS[d], label=d) for d in DTYPE_ORDER
               if d in {c.split('__')[0] for c in cells}]
    handles += [
        plt.Line2D([0], [0], marker='o', color='gray', linestyle='None',
                   markerfacecolor='white', markeredgecolor='gray', markersize=7,
                   label='Baseline peak'),
        plt.Line2D([0], [0], marker='D', color='black', linestyle='None',
                   markersize=7, label='Activity peak'),
    ]
    ax.legend(handles=handles, fontsize=8, loc='upper right', ncol=2)
    fig.tight_layout()
    out = os.path.join(out_dir, 'figS7_peak_shift.png')
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f'  Saved: {out}')


# ── Fig S8 — Lighting diurnal, 4 archetype panels ────────────────────────────
def fig_s8_diurnal_light(profiles, out_dir):
    bl_by_dtype = _archetype_mean_diurnal(profiles, '2022', 'baseline', 'light_bldg_W')
    ac_by_dtype = _archetype_mean_diurnal(profiles, '2022', 'activity', 'light_bldg_W')

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=False)
    hours = list(range(24))

    for ax_idx, dtype in enumerate(DTYPE_ORDER):
        ax = axes[ax_idx // 2][ax_idx % 2]
        col = DTYPE_COLORS[dtype]
        bl = bl_by_dtype[dtype]
        ac = ac_by_dtype[dtype]

        bl_peak = bl.index(max(bl)) if max(bl) > 0 else 0
        ac_peak = ac.index(max(ac)) if max(ac) > 0 else 0

        # Normalize to each profile's daily mean (shape/timing only; calibrated annual
        # lighting magnitudes -- the IDF default undercount vs SHEU -- are in figS2).
        bl_m = (sum(bl) / 24.0) or 1.0
        ac_m = (sum(ac) / 24.0) or 1.0
        bl_n = [v / bl_m for v in bl]
        ac_n = [v / ac_m for v in ac]

        ax.plot(hours, bl_n, color='gray', lw=1.8, label='Baseline')
        ax.plot(hours, ac_n, color=col,    lw=1.8, label='Activity')
        ax.axhline(1.0, color='black', lw=0.5, alpha=0.25)
        ax.axvline(bl_peak, color='gray', linestyle='--', lw=0.9, alpha=0.8,
                   label=f'BL peak h{bl_peak}')
        ax.axvline(ac_peak, color=col,   linestyle='--', lw=0.9, alpha=0.8,
                   label=f'AC peak h{ac_peak}')

        shift = ac_peak - bl_peak
        shift_str = f'{shift:+d} h' if shift != 0 else 'no shift'
        ax.set_title(f'{dtype}  (BL h{bl_peak} → AC h{ac_peak}, {shift_str})', fontsize=10)
        ax.set_xlabel('Hour of day')
        ax.set_ylabel('Lighting load (x daily mean)')
        ax.set_xticks(range(0, 24, 4))
        ax.legend(fontsize=7.5, loc='upper left')

    fig.suptitle('Fig S8 - Lighting diurnal load shape, 2022 (normalized to daily mean)\n'
                 'Gray = baseline (6-city mean), coloured = activity; dashed = peak hour; '
                 'shape only - calibrated magnitudes in figS2',
                 fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = os.path.join(out_dir, 'figS8_diurnal_light.png')
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f'  Saved: {out}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profiles', default=str(HERE / 'loadshape_profiles.csv'))
    ap.add_argument('--peaks',    default=str(HERE / 'peak_hours.csv'))
    ap.add_argument('--shift',    default=str(HERE / 'peak_shift_summary.csv'))
    ap.add_argument('--out',      default=str(HERE / 'figures'))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    profiles   = load_profiles(args.profiles)
    peak_hours = load_peak_hours(args.peaks)

    print(f'Profiles rows: {len(profiles)}')
    print(f'Peak-hours rows: {len(peak_hours)}')

    fig_s6_diurnal_equip(profiles, args.out)
    fig_s7_peak_shift(peak_hours, args.out)
    fig_s8_diurnal_light(profiles, args.out)

    print(f'\nFigs S6–S8 saved to {args.out}/')


if __name__ == '__main__':
    main()
