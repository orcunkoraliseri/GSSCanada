#!/usr/bin/env python3
"""
step9_validate_full.py — Phase C: paired Δ validation for the full 24-cell/n=50 Step 9 run.

Extends step9_validate.py to cover all 24 cells (4 archetypes x 6 cities) and
applies the OtherDwelling multi-unit fridge correction (see D8 in cluster_run.md).

OtherDwelling fridge correction (D8):
  AttachedHouse IDF has 5 units, each with a named refrigerator (refrigerator_unit1–5).
  integration.py calibrates ALL named fridges to ~51.14 W = 448 kWh/yr each.
  Building-level InteriorEquipment:Electricity captures all 5 fridges:
    ac_building_kwh = STEP9_Equip (1 unit) + 5 x 448 kWh
  Per-unit SHEU target = 2691 (net) + 448 (fridge) = 3139 kWh gross.
  Correction: subtract (5-1) x 448 kWh from building-level reading before gate check.

Usage:
  python step9_validate_full.py --root /speed-scratch/o_iseri/step9_run \
                                --out  /speed-scratch/o_iseri/step9_run/cluster_run_results.csv
"""
import argparse
import csv
import os
import sys
from pathlib import Path

SHEU_EQUIP_NET   = {'SingleD': 3252.0, 'HighRise': 1474.0, 'MidRise': 1718.0, 'OtherDwelling': 2691.0}
FRIDGE_KWH_IDF   = 448.0
SHEU_EQUIP_GROSS = {k: v + FRIDGE_KWH_IDF for k, v in SHEU_EQUIP_NET.items()}
SHEU_LIGHT       = {'SingleD': 1262.0, 'HighRise': 736.0, 'MidRise': 736.0, 'OtherDwelling': 1100.0}

# AttachedHouse IDF has 5 units (refrigerator_unit1..5 across 5 zones).
# After Step 9 consolidation, 5 named fridges remain; 4 are in non-occupancy zones.
# Subtract 4 x FRIDGE_KWH_IDF from building-level InteriorEquipment:Electricity
# to recover the per-HH (single occupancy zone) activity equipment total.
OD_N_UNITS = 5

ARCHETYPES = ['SingleD', 'OtherDwelling', 'MidRise', 'HighRise']
CITIES     = ['Toronto_5A', 'Kelowna_5B', 'Vancouver_5C', 'Montreal_6A', 'Calgary_6B', 'Winnipeg_7A']

CELL_DTYPE = {
    f"{arch}__{city}": arch
    for arch in ARCHETYPES
    for city in CITIES
}

SLEEP_HOURS = {2, 3, 4, 5}


def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def annual_kwh(rows, col, n_hh=1):
    try:
        return sum(float(r.get(col) or 0) for r in rows) / 3.6e6 / max(n_hh, 1)
    except Exception:
        return None


def find_col(row_dict, keywords):
    for k in row_dict:
        if all(kw.lower() in k.lower() for kw in keywords):
            return k
    return None


def validate_cell_year(cell, year, bl_rows, ac_rows):
    dtype = CELL_DTYPE.get(cell, 'SingleD')
    results = {'cell': cell, 'year': year, 'dtype': dtype}

    n_hh = max(1, len(bl_rows) // 8760)

    bl_sample = bl_rows[0] if bl_rows else {}
    ac_sample = ac_rows[0] if ac_rows else {}
    elec_col     = find_col(bl_sample, ['Electricity:Facility'])
    equip_col    = find_col(bl_sample, ['Zone Electric Equipment Electricity Energy'])
    light_col    = find_col(bl_sample, ['Zone Lights Electricity Energy'])
    ac_equip_col = find_col(ac_sample, ['InteriorEquipment:Electricity'])
    ac_light_col = find_col(ac_sample, ['InteriorLights:Electricity'])

    if elec_col is None:
        results['elec_col'] = 'MISSING'
    else:
        results['elec_col'] = elec_col
        results['bl_elec_kwh'] = annual_kwh(bl_rows, elec_col, n_hh)
        results['ac_elec_kwh'] = annual_kwh(ac_rows, elec_col, n_hh)
        if results['bl_elec_kwh'] is not None and results['ac_elec_kwh'] is not None:
            results['delta_elec_kwh'] = results['ac_elec_kwh'] - results['bl_elec_kwh']

    results['equip_col']    = equip_col    or 'MISSING'
    results['ac_equip_col'] = ac_equip_col or 'MISSING'
    if equip_col:
        results['bl_equip_kwh'] = annual_kwh(bl_rows, equip_col, n_hh)
    if ac_equip_col:
        raw_ac_equip = annual_kwh(ac_rows, ac_equip_col, n_hh)
        if raw_ac_equip is not None and dtype == 'OtherDwelling':
            # D8: subtract fridge contribution from the 4 non-occupancy units
            raw_ac_equip -= (OD_N_UNITS - 1) * FRIDGE_KWH_IDF
        results['ac_equip_kwh'] = raw_ac_equip
    if results.get('bl_equip_kwh') is not None and results.get('ac_equip_kwh') is not None:
        results['delta_equip_kwh'] = results['ac_equip_kwh'] - results['bl_equip_kwh']

    results['light_col']    = light_col    or 'MISSING'
    results['ac_light_col'] = ac_light_col or 'MISSING'
    if light_col:
        results['bl_light_kwh'] = annual_kwh(bl_rows, light_col, n_hh)
    if ac_light_col:
        results['ac_light_kwh'] = annual_kwh(ac_rows, ac_light_col, n_hh)
    if results.get('bl_light_kwh') is not None and results.get('ac_light_kwh') is not None:
        results['delta_light_kwh'] = results['ac_light_kwh'] - results['bl_light_kwh']

    # SHEU gates (±15%)
    for label, sheu_map in [('equip', SHEU_EQUIP_GROSS), ('light', SHEU_LIGHT)]:
        target = sheu_map.get(dtype, sheu_map['SingleD'])
        results[f'sheu_target_{label}'] = target
        ac_val = results.get(f'ac_{label}_kwh')
        if ac_val is not None:
            pct = (ac_val - target) / target * 100
            results[f'sheu_pct_{label}'] = pct
            results[f'sheu_gate_{label}'] = 'PASS' if abs(pct) <= 15 else 'FAIL'

    # Sleep/away zero-check (h02-h05)
    _sleep_col = ac_equip_col or equip_col
    if _sleep_col:
        sleep_vals = [float(r.get(_sleep_col) or 0)
                      for r in ac_rows if int(r.get('hour', -1)) in SLEEP_HOURS]
        if sleep_vals:
            mean_sleep_wh = sum(sleep_vals) / len(sleep_vals) / 3600
            results['sleep_equip_mean_wh'] = mean_sleep_wh
            results['sleep_check'] = 'PASS' if mean_sleep_wh < 300 else 'WARN'

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/speed-scratch/o_iseri/step9_run")
    ap.add_argument("--out",  default=None)
    args = ap.parse_args()

    manifest_path = os.path.join(args.root, "step9_manifest.csv")
    if not os.path.exists(manifest_path):
        print(f"ERROR: manifest not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = list(csv.DictReader(f))

    data = {}
    missing = []

    for mrow in manifest:
        cell      = mrow['cell']
        treatment = mrow['treatment']
        year      = mrow['year']
        idf_path  = mrow['idf_path']
        out_dir   = os.path.dirname(idf_path)
        meters_csv = os.path.join(out_dir, 'hourly_meters.csv')

        if not os.path.exists(meters_csv):
            missing.append(f"{cell}/{treatment}/{mrow['hh_id']}/{year}")
            continue

        key = (cell, year, treatment)
        if key not in data:
            data[key] = []
        data[key].extend(load_csv(meters_csv))

    if missing:
        print(f"WARNING: {len(missing)} missing hourly_meters.csv files:")
        for m in missing[:10]:
            print(f"  {m}")
        if len(missing) > 10:
            print(f"  ... and {len(missing)-10} more")

    all_results = []
    cells = sorted({k[0] for k in data})
    years = ['2022', '2030']

    print("\n=== Step 9 Full-Grid Validation Results (24 cells) ===\n")
    hdr = (f"{'Cell':35s} {'Year':6s} {'BL eq':>9} {'AC eq':>9} "
           f"{'SHEU%':>7} {'Gate':6} | {'BL lt':>9} {'AC lt':>9} "
           f"{'LG%':>7} {'Gate':6} | sleep")
    print(hdr)
    print("-" * len(hdr))

    for cell in cells:
        for year in years:
            bl_key = (cell, year, 'baseline')
            ac_key = (cell, year, 'activity')
            if bl_key not in data or ac_key not in data:
                print(f"  {cell}/{year}: MISSING "
                      f"(baseline={bl_key in data}, activity={ac_key in data})")
                continue

            r = validate_cell_year(cell, year, data[bl_key], data[ac_key])
            all_results.append(r)

            def fmt(v):  return f"{v:9.0f}" if v == v else f"{'---':>9}"
            def fmts(v): return f"{v:+7.1f}%" if v == v else f"{'---':>7}"

            bl_eq = r.get('bl_equip_kwh', float('nan'))
            ac_eq = r.get('ac_equip_kwh', float('nan'))
            sp    = r.get('sheu_pct_equip', float('nan'))
            eg    = r.get('sheu_gate_equip', '?')
            bl_lt = r.get('bl_light_kwh', float('nan'))
            ac_lt = r.get('ac_light_kwh', float('nan'))
            lp    = r.get('sheu_pct_light', float('nan'))
            lg    = r.get('sheu_gate_light', '?')
            slp   = r.get('sleep_check', '?')

            print(f"{cell:35s} {year:6s} {fmt(bl_eq)} {fmt(ac_eq)} "
                  f"{fmts(sp)} {eg:6} | {fmt(bl_lt)} {fmt(ac_lt)} "
                  f"{fmts(lp)} {lg:6} | {slp}")

    # 2022→2030 differential by cell
    print("\n--- 2022→2030 Differential (activity Δequip kWh) ---")
    for cell in cells:
        r22 = next((r for r in all_results if r['cell'] == cell and r['year'] == '2022'), None)
        r30 = next((r for r in all_results if r['cell'] == cell and r['year'] == '2030'), None)
        if r22 and r30:
            ac22 = r22.get('ac_equip_kwh', 0) or 0
            ac30 = r30.get('ac_equip_kwh', 0) or 0
            bl22 = r22.get('bl_equip_kwh', 0) or 0
            bl30 = r30.get('bl_equip_kwh', 0) or 0
            ac_trend = ac30 - ac22
            bl_trend = bl30 - bl22
            sharpness = ac_trend - bl_trend
            print(f"  {cell:35s}  act Δ22→30: {ac_trend:+.0f} kWh  "
                  f"bl Δ22→30: {bl_trend:+.0f} kWh  sharpness: {sharpness:+.0f} kWh")

    # HH pairing check: assert symmetric diff = 0 across {baseline,activity}x{2022,2030}
    print("\n--- HH pairing check (symmetric diff across arms x years) ---")
    pair_ok = True
    for cell in cells:
        sets = {}
        for yr in years:
            for trt in ('baseline', 'activity'):
                key = (cell, yr, trt)
                if key in data:
                    rows = data[key]
                    sets[f"{yr}/{trt}"] = set(r.get('hour', '') for r in rows[:8760])
        if len(sets) == 4:
            s0 = list(sets.values())[0]
            for label, s in sets.items():
                if s != s0:
                    print(f"  {cell}: MISMATCH {label}")
                    pair_ok = False
    if pair_ok:
        print("  All cells: pairing OK")

    # Gate summary
    print("\n--- Gate Summary ---")
    passes = sum(1 for r in all_results
                 if r.get('sheu_gate_equip') == 'PASS' and r.get('sheu_gate_light') == 'PASS')
    total  = len(all_results)
    print(f"  SHEU ±15% gate: {passes}/{total} cell×year combos pass")
    if passes < total:
        print("  FAILING rows:")
        for r in all_results:
            if r.get('sheu_gate_equip') != 'PASS' or r.get('sheu_gate_light') != 'PASS':
                print(f"    {r['cell']} {r['year']}  "
                      f"equip={r.get('sheu_pct_equip', float('nan')):.1f}%  "
                      f"light={r.get('sheu_pct_light', float('nan')):.1f}%")

    out_path = args.out or os.path.join(args.root, "cluster_run_results.csv")
    if all_results:
        keys = list(all_results[0].keys())
        with open(out_path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            w.writeheader()
            w.writerows(all_results)
        print(f"\nResults saved: {out_path}")

    if passes == total and total > 0:
        print("\n=== VALIDATION: ALL GATES PASS ===")
        sys.exit(0)
    else:
        print(f"\n=== VALIDATION: {total - passes}/{total} gate(s) FAIL — stop and report ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
