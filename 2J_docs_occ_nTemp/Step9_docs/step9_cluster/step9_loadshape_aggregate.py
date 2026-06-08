#!/usr/bin/env python3
"""
step9_loadshape_aggregate.py — Aggregate hourly_meters.csv across full 24-cell grid.

Pure stdlib (csv, os, glob). Streams one file at a time; never holds all files in RAM.

Output dir: /speed-scratch/o_iseri/step9_run/loadshape/
  loadshape_profiles.csv   — mean diurnal W per (cell, year, arm, hour_of_day)
  peak_hours.csv           — peak hour-of-day per (cell, year, arm)
  peak_shift_summary.csv   — activity − baseline peak shift per (cell, year)
"""
import csv
import glob
import os

ROOT = '/speed-scratch/o_iseri/step9_run/idfs'
OUT_DIR = '/speed-scratch/o_iseri/step9_run/loadshape'
PATTERN = os.path.join(ROOT, '*', '*', '*', '*', 'hourly_meters.csv')

# Columns to read (in this order → index 0..4 in sums arrays)
NEED = [
    'InteriorEquipment:Electricity',          # 0 equip_bldg
    'Zone Electric Equipment Electricity Energy',  # 1 equip_zone
    'InteriorLights:Electricity',             # 2 light_bldg
    'Zone Lights Electricity Energy',         # 3 light_zone
    'Electricity:Facility',                   # 4 facility
]

# Global accumulators
# sums[(cell, year, arm, hod)] = [float*5]  — running sum of Joules
# counts[(cell, year, arm, hod)] = int       — number of contributing rows
# hh_sets[(cell, year, arm)] = set of sample strings
sums = {}
counts = {}
hh_sets = {}

skipped = 0
processed = 0
skip_log = []

all_files = sorted(glob.glob(PATTERN))
print(f'Files found: {len(all_files)}')

for fpath in all_files:
    parts = fpath.split('/')
    # parts: ..., idfs, CELL, ARM, SAMPLE, YEAR, hourly_meters.csv
    cell   = parts[-5]
    arm    = parts[-4]
    sample = parts[-3]
    year   = parts[-2]

    try:
        with open(fpath, newline='') as f:
            reader = csv.reader(f)
            header = next(reader)

            try:
                h_idx = header.index('hour')
                col_idxs = [header.index(c) for c in NEED]
            except ValueError as e:
                msg = f'SKIP missing-col {e}: {fpath}'
                print(msg)
                skip_log.append(msg)
                skipped += 1
                continue

            # Per-file temp buffers (24 slots each)
            tmp_sums   = [[0.0] * 5 for _ in range(24)]
            tmp_counts = [0] * 24
            row_count = 0

            for row in reader:
                row_count += 1
                hod = int(row[h_idx]) % 24
                s = tmp_sums[hod]
                for i, ci in enumerate(col_idxs):
                    s[i] += float(row[ci])
                tmp_counts[hod] += 1

        if row_count != 8760:
            msg = f'SKIP row-count={row_count}: {fpath}'
            print(msg)
            skip_log.append(msg)
            skipped += 1
            continue

        # Merge temp buffers into global accumulators
        arm_key = (cell, year, arm)
        for hod in range(24):
            key = (cell, year, arm, hod)
            if key not in sums:
                sums[key]   = [0.0] * 5
                counts[key] = 0
            gs = sums[key]
            ts = tmp_sums[hod]
            for i in range(5):
                gs[i] += ts[i]
            counts[key] += tmp_counts[hod]

        if arm_key not in hh_sets:
            hh_sets[arm_key] = set()
        hh_sets[arm_key].add(sample)
        processed += 1

    except Exception as exc:
        msg = f'SKIP error {exc}: {fpath}'
        print(msg)
        skip_log.append(msg)
        skipped += 1

print(f'\nProcessed: {processed}  Skipped: {skipped}')

# ── Write outputs ────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)

# 1. loadshape_profiles.csv
profiles_path = os.path.join(OUT_DIR, 'loadshape_profiles.csv')
with open(profiles_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['cell', 'year', 'arm', 'hour_of_day',
                'equip_bldg_W', 'equip_zone_W', 'light_bldg_W', 'light_zone_W',
                'facility_W', 'n_hh'])
    for key in sorted(sums.keys()):
        cell, year, arm, hod = key
        cnt = counts[key]
        s   = sums[key]
        n   = len(hh_sets.get((cell, year, arm), set()))
        w.writerow([
            cell, year, arm, hod,
            round(s[0] / cnt / 3600, 6),
            round(s[1] / cnt / 3600, 6),
            round(s[2] / cnt / 3600, 6),
            round(s[3] / cnt / 3600, 6),
            round(s[4] / cnt / 3600, 6),
            n,
        ])
print(f'Wrote: {profiles_path}')

# 2. peak_hours.csv — argmax of mean diurnal per (cell, year, arm)
# Build diurnal arrays from sums/counts
diurnal = {}  # (cell, year, arm) -> {'eq_b': [24], 'eq_z': [24], 'lt_b': [24], 'lt_z': [24]}
for key, s in sums.items():
    cell, year, arm, hod = key
    ak = (cell, year, arm)
    if ak not in diurnal:
        diurnal[ak] = {'eq_b': [0.0]*24, 'eq_z': [0.0]*24,
                       'lt_b': [0.0]*24, 'lt_z': [0.0]*24}
    cnt = counts[key]
    diurnal[ak]['eq_b'][hod] = s[0] / cnt / 3600
    diurnal[ak]['eq_z'][hod] = s[1] / cnt / 3600
    diurnal[ak]['lt_b'][hod] = s[2] / cnt / 3600
    diurnal[ak]['lt_z'][hod] = s[3] / cnt / 3600

peaks_path = os.path.join(OUT_DIR, 'peak_hours.csv')
with open(peaks_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['cell', 'year', 'arm',
                'equip_bldg_peak_h', 'equip_zone_peak_h',
                'light_bldg_peak_h', 'light_zone_peak_h', 'n_hh'])
    for ak in sorted(diurnal.keys()):
        cell, year, arm = ak
        d = diurnal[ak]
        n = len(hh_sets.get(ak, set()))
        w.writerow([
            cell, year, arm,
            d['eq_b'].index(max(d['eq_b'])),
            d['eq_z'].index(max(d['eq_z'])),
            d['lt_b'].index(max(d['lt_b'])),
            d['lt_z'].index(max(d['lt_z'])),
            n,
        ])
print(f'Wrote: {peaks_path}')

# 3. peak_shift_summary.csv — activity peak − baseline peak per (cell, year)
peak_lookup = {}  # (cell, year, arm) -> {eq_b, eq_z, lt_b, lt_z}
for ak, d in diurnal.items():
    cell, year, arm = ak
    peak_lookup[ak] = {
        'eq_b': d['eq_b'].index(max(d['eq_b'])),
        'eq_z': d['eq_z'].index(max(d['eq_z'])),
        'lt_b': d['lt_b'].index(max(d['lt_b'])),
        'lt_z': d['lt_z'].index(max(d['lt_z'])),
    }

cell_years = sorted(set((cell, year) for cell, year, arm in diurnal.keys()))

shift_path = os.path.join(OUT_DIR, 'peak_shift_summary.csv')
with open(shift_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['cell', 'year',
                'equip_bldg_shift', 'equip_zone_shift',
                'light_bldg_shift', 'light_zone_shift'])
    for cell, year in cell_years:
        bl = peak_lookup.get((cell, year, 'baseline'))
        ac = peak_lookup.get((cell, year, 'activity'))
        if bl is None or ac is None:
            print(f'WARN: missing baseline or activity for {cell}/{year} — skipped in shift table')
            continue
        w.writerow([
            cell, year,
            ac['eq_b'] - bl['eq_b'],
            ac['eq_z'] - bl['eq_z'],
            ac['lt_b'] - bl['lt_b'],
            ac['lt_z'] - bl['lt_z'],
        ])
print(f'Wrote: {shift_path}')

# 4. n_hh summary per bucket
print('\nn_hh per (cell, year, arm) bucket:')
for ak in sorted(hh_sets.keys()):
    n = len(hh_sets[ak])
    flag = ' <50' if n < 50 else ''
    print(f'  {ak[0]}/{ak[1]}/{ak[2]}: n_hh={n}{flag}')

print(f'\nSkip log ({len(skip_log)} entries):')
for entry in skip_log:
    print(f'  {entry}')

print('\nDone.')
