#!/usr/bin/env python3
"""
step9_validate.py — Phase 5: paired Δ validation for Step 9 cluster run.

Loads all hourly_meters.csv files from the step9 run, computes:
  - Paired Δ (activity − baseline) per end-use per cell
  - SHEU ±15% gate for activity equipment + lighting
  - Sleep/away zero-check (h02-h05 activity equipment)
  - 2022→2030 differential: activity vs baseline
Writes results to cluster_run_results.csv and prints a validation table.

Usage:
  python step9_validate.py --root /speed-scratch/o_iseri/step9_run \
                           --out  /speed-scratch/o_iseri/step9_run/cluster_run_results.csv
"""
import argparse
import csv
import os
import sys
from pathlib import Path

# SHEU targets per dtype (from activity_loads.SHEU_BY_DTYPE, DR-1 §9.4)
SHEU_EQUIP_NET   = {'SingleD': 3252.0, 'HighRise': 1474.0, 'MidRise': 1718.0, 'OtherDwelling': 2691.0}
FRIDGE_KWH_IDF   = 448.0  # always-on fridge baseload injected alongside STEP9_Equip
SHEU_EQUIP_GROSS = {k: v + FRIDGE_KWH_IDF for k, v in SHEU_EQUIP_NET.items()}
SHEU_LIGHT       = {'SingleD': 1262.0, 'HighRise':  736.0, 'MidRise':  736.0, 'OtherDwelling': 1100.0}

CELL_DTYPE = {
    'SingleD__Winnipeg_7A':  'SingleD',
    'HighRise__Montreal_6A': 'HighRise',
    'MidRise__Toronto_5A':   'MidRise',
}

SLEEP_HOURS = {2, 3, 4, 5}   # h02-h05 index


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

    # n_hh: number of sampled HH aggregated (each HH = 8760 hourly rows)
    n_hh = max(1, len(bl_rows) // 8760)

    # Baseline: zone-level meters give per-unit load for HighRise/MidRise.
    # Activity: after S9 consolidation all zones except the occupancy zone are
    # zeroed, so extract_meters.py "last-zone wins" gives 0 for zone-level meters.
    # Use building-level meters for activity (InteriorEquipment / InteriorLights),
    # which equal per-unit load because only one zone carries non-zero load after S9.
    bl_sample = bl_rows[0] if bl_rows else {}
    ac_sample = ac_rows[0] if ac_rows else {}
    elec_col     = find_col(bl_sample, ['Electricity:Facility'])
    equip_col    = find_col(bl_sample, ['Zone Electric Equipment Electricity Energy'])
    light_col    = find_col(bl_sample, ['Zone Lights Electricity Energy'])
    ac_equip_col = find_col(ac_sample, ['InteriorEquipment:Electricity'])
    ac_light_col = find_col(ac_sample, ['InteriorLights:Electricity'])

    # Electricity (facility-level, same for both)
    if elec_col is None:
        results['elec_col'] = 'MISSING'
    else:
        results['elec_col'] = elec_col
        results['bl_elec_kwh'] = annual_kwh(bl_rows, elec_col, n_hh)
        results['ac_elec_kwh'] = annual_kwh(ac_rows, elec_col, n_hh)
        if results['bl_elec_kwh'] is not None and results['ac_elec_kwh'] is not None:
            results['delta_elec_kwh'] = results['ac_elec_kwh'] - results['bl_elec_kwh']

    # Equipment: zone-level for BL, building-level for AC
    results['equip_col'] = equip_col or 'MISSING'
    results['ac_equip_col'] = ac_equip_col or 'MISSING'
    if equip_col:
        results['bl_equip_kwh'] = annual_kwh(bl_rows, equip_col, n_hh)
    if ac_equip_col:
        results['ac_equip_kwh'] = annual_kwh(ac_rows, ac_equip_col, n_hh)
    if results.get('bl_equip_kwh') is not None and results.get('ac_equip_kwh') is not None:
        results['delta_equip_kwh'] = results['ac_equip_kwh'] - results['bl_equip_kwh']

    # Lighting: zone-level for BL, building-level for AC
    results['light_col'] = light_col or 'MISSING'
    results['ac_light_col'] = ac_light_col or 'MISSING'
    if light_col:
        results['bl_light_kwh'] = annual_kwh(bl_rows, light_col, n_hh)
    if ac_light_col:
        results['ac_light_kwh'] = annual_kwh(ac_rows, ac_light_col, n_hh)
    if results.get('bl_light_kwh') is not None and results.get('ac_light_kwh') is not None:
        results['delta_light_kwh'] = results['ac_light_kwh'] - results['bl_light_kwh']

    # SHEU gates (±15%) — activity equipment compared to GROSS target (net + fridge)
    for label, sheu_map in [('equip', SHEU_EQUIP_GROSS), ('light', SHEU_LIGHT)]:
        target = sheu_map.get(dtype, sheu_map['SingleD'])
        results[f'sheu_target_{label}'] = target
        ac_val = results.get(f'ac_{label}_kwh')
        if ac_val is not None:
            pct = (ac_val - target) / target * 100
            results[f'sheu_pct_{label}'] = pct
            results[f'sheu_gate_{label}'] = 'PASS' if abs(pct) <= 15 else 'FAIL'

    # Sleep/away zero-check (h02-h05) — use building-level column for activity
    _sleep_col = ac_equip_col or equip_col
    if _sleep_col:
        sleep_vals = [float(r.get(_sleep_col) or 0) for r in ac_rows if int(r.get('hour', -1)) in SLEEP_HOURS]
        if sleep_vals:
            mean_sleep_wh = sum(sleep_vals) / len(sleep_vals) / 3600
            results['sleep_equip_mean_wh'] = mean_sleep_wh
            results['sleep_check'] = 'PASS' if mean_sleep_wh < 300 else 'WARN'

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/speed-scratch/o_iseri/step9_run")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    manifest_path = os.path.join(args.root, "step9_manifest.csv")
    if not os.path.exists(manifest_path):
        print(f"ERROR: manifest not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = list(csv.DictReader(f))

    # Group by (cell, year) → {treatment: rows_list_of_hourly_dicts}
    # Each (cell, hh_id, year, treatment) has one hourly_meters.csv
    # We aggregate per (cell, year, treatment) across all HH
    data = {}   # (cell, year, treatment) -> [hourly rows × all HH concatenated]
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

    # Validate per (cell, year)
    all_results = []
    cells = sorted({k[0] for k in data})
    years = ['2022', '2030']

    print("\n=== Step 9 Validation Results ===\n")
    header = f"{'Cell':25s} {'Year':6s} {'Treat':8s} {'BL equip':>10} {'AC equip':>10} {'Δ equip':>9} {'SHEU%':>7} {'Gate':6} | {'BL light':>9} {'AC light':>9} {'Δ light':>8} {'LG%':>7} {'Gate':6} | sleep"
    print(header)
    print("-" * len(header))

    for cell in cells:
        for year in years:
            bl_key = (cell, year, 'baseline')
            ac_key = (cell, year, 'activity')
            if bl_key not in data or ac_key not in data:
                print(f"  {cell}/{year}: MISSING (baseline={bl_key in data}, activity={ac_key in data})")
                continue

            r = validate_cell_year(cell, year, data[bl_key], data[ac_key])
            all_results.append(r)

            bl_eq = r.get('bl_equip_kwh', float('nan'))
            ac_eq = r.get('ac_equip_kwh', float('nan'))
            de    = r.get('delta_equip_kwh', float('nan'))
            sp    = r.get('sheu_pct_equip', float('nan'))
            eg    = r.get('sheu_gate_equip', '?')
            bl_lt = r.get('bl_light_kwh', float('nan'))
            ac_lt = r.get('ac_light_kwh', float('nan'))
            dl    = r.get('delta_light_kwh', float('nan'))
            lp    = r.get('sheu_pct_light', float('nan'))
            lg    = r.get('sheu_gate_light', '?')
            slp   = r.get('sleep_check', '?')

            def fmt(v): return f"{v:10.0f}" if v == v else f"{'---':>10}"
            def fmts(v): return f"{v:+7.1f}%" if v == v else f"{'---':>7}"

            print(f"{cell:25s} {year:6s} act/bl   {fmt(bl_eq)} {fmt(ac_eq)} {fmt(de)} {fmts(sp)} {eg:6} | {fmt(bl_lt)} {fmt(ac_lt)} {fmt(dl)} {fmts(lp)} {lg:6} | {slp}")

    # 2022→2030 differential
    print("\n--- 2022→2030 Differential (Δequip kWh) ---")
    for cell in cells:
        r22 = next((r for r in all_results if r['cell'] == cell and r['year'] == '2022'), None)
        r30 = next((r for r in all_results if r['cell'] == cell and r['year'] == '2030'), None)
        if r22 and r30:
            ac_d22 = r22.get('delta_equip_kwh', 0) or 0
            ac_d30 = r30.get('delta_equip_kwh', 0) or 0
            bl_d22 = r22.get('bl_equip_kwh', 0) or 0
            bl_d30 = r30.get('bl_equip_kwh', 0) or 0
            ac22   = r22.get('ac_equip_kwh', 0) or 0
            ac30   = r30.get('ac_equip_kwh', 0) or 0
            bl22   = bl_d22
            bl30   = bl_d30
            ac_trend  = (ac30 - ac22) if ac22 else float('nan')
            bl_trend  = (bl30 - bl22) if bl22 else float('nan')
            sharpness = (ac_trend - bl_trend) if (ac_trend == ac_trend and bl_trend == bl_trend) else float('nan')
            print(f"  {cell:25s}  activity Δ22→30: {ac_trend:+.0f} kWh  baseline Δ22→30: {bl_trend:+.0f} kWh  extra sharpness: {sharpness:+.0f} kWh")

    # Overall gate summary
    print("\n--- Gate Summary ---")
    passes = sum(1 for r in all_results if r.get('sheu_gate_equip') == 'PASS' and r.get('sheu_gate_light') == 'PASS')
    total  = len(all_results)
    print(f"  SHEU ±15% gate: {passes}/{total} cell×year combos pass")
    if passes < total:
        print("  FAILING rows:")
        for r in all_results:
            if r.get('sheu_gate_equip') != 'PASS' or r.get('sheu_gate_light') != 'PASS':
                print(f"    {r['cell']} {r['year']}  equip={r.get('sheu_pct_equip','?'):.1f}%  light={r.get('sheu_pct_light','?'):.1f}%")

    # Save CSV
    out_path = args.out or os.path.join(args.root, "cluster_run_results.csv")
    if all_results:
        keys = list(all_results[0].keys())
        with open(out_path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(all_results)
        print(f"\nResults saved: {out_path}")

    if passes == total:
        print("\n=== VALIDATION: ALL GATES PASS ===")
        sys.exit(0)
    else:
        print(f"\n=== VALIDATION: {total - passes} gate(s) FAIL — stop and report ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
