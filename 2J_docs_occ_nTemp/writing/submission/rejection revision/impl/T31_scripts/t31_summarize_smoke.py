#!/usr/bin/env python3
"""t31_summarize_smoke.py -- T31 phase A smoke summarizer.

Scans a smoke output tree with three labelled trees:
    <smoke-root>/out/unmodified/sample_*_HH*/<year>/hourly_meters.csv
    <smoke-root>/out/current/sample_*_HH*/<year>/hourly_meters.csv
    <smoke-root>/out/mechanism_test/sample_*_HH*/<year>/hourly_meters.csv

hourly_meters.csv columns (Step8_docs/eSim_bem_utils_2J/main.py:2106-2109,
Step8_docs/08_simulation_plots.py:80-86, read this session): "hour" plus
meter columns in Joules, including "Electricity:Facility" (site total,
already includes lights+equip+fan -- never add components to it) and
"Heating:EnergyTransfer" (thermal zone heating load). Annual value =
sum(column) / 3.6e6 -> kWh (same J->kWh convention as
08_simulation_plots.py:450).

Writes one row per (label, sample, hh_id, year) to --out, plus prints an
E0 (current vs unmodified, expect <=0.001% relative difference on both
Electricity:Facility and Heating:EnergyTransfer) and an E1 (mechanism_test
vs unmodified, expect an INCREASE in annual heating) verdict per matched
(sample, hh_id) pair to stdout -- this script is called from t31_smoke.sh,
so those verdict lines land in the job's own log file.

Standard library only (csv, glob, os, re, argparse).
"""
import argparse
import csv
import glob
import os
import re
import sys

FACILITY_COL = "Electricity:Facility"
HEATING_COL = "Heating:EnergyTransfer"
J_PER_KWH = 3.6e6

_SAMP_RE = re.compile(r"^sample_(\d+)_HH(.+)$", re.IGNORECASE)


def annual_sums(hourly_meters_csv):
    """Return (facility_kWh, heating_kWh, n_rows, has_facility, has_heating)."""
    fac_sum = 0.0
    heat_sum = 0.0
    n_rows = 0
    with open(hourly_meters_csv, newline="", encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        has_facility = FACILITY_COL in (r.fieldnames or [])
        has_heating = HEATING_COL in (r.fieldnames or [])
        for row in r:
            n_rows += 1
            if has_facility:
                try:
                    fac_sum += float(row[FACILITY_COL])
                except (ValueError, TypeError):
                    pass
            if has_heating:
                try:
                    heat_sum += float(row[HEATING_COL])
                except (ValueError, TypeError):
                    pass
    return fac_sum / J_PER_KWH, heat_sum / J_PER_KWH, n_rows, has_facility, has_heating


def collect(out_root, label):
    """Return {(sample, hh_id): {"facility_kWh":..,"heating_kWh":..,"n_rows":..}}
    across every year dir found under this label's output tree."""
    results = {}
    base = os.path.join(out_root, label)
    if not os.path.isdir(base):
        return results
    for name in sorted(os.listdir(base)):
        m = _SAMP_RE.match(name)
        if not m:
            continue
        sample, hh_id = int(m.group(1)), m.group(2)
        sample_dir = os.path.join(base, name)
        for year in sorted(os.listdir(sample_dir)):
            hm = os.path.join(sample_dir, year, "hourly_meters.csv")
            if not os.path.exists(hm):
                continue
            fac, heat, n_rows, has_fac, has_heat = annual_sums(hm)
            results[(sample, hh_id, year)] = {
                "facility_kWh": fac, "heating_kWh": heat, "n_rows": n_rows,
                "has_facility": has_fac, "has_heating": has_heat,
            }
    return results


def pct_diff(a, b):
    if a == 0 and b == 0:
        return 0.0
    denom = abs(a) if a != 0 else abs(b)
    return abs(a - b) / denom * 100.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-root", required=True, help="T31/smoke directory (contains out/<label>/...)")
    ap.add_argument("--out", required=True, help="output CSV path (T31/smoke/e0_e1.csv)")
    args = ap.parse_args()

    out_root = os.path.join(args.smoke_root, "out")
    labels = ["unmodified", "current", "mechanism_test"]
    by_label = {lbl: collect(out_root, lbl) for lbl in labels}

    rows = []
    for lbl in labels:
        for (sample, hh_id, year), d in sorted(by_label[lbl].items()):
            rows.append({
                "label": lbl, "sample": sample, "hh_id": hh_id, "year": year,
                "facility_kWh": f"{d['facility_kWh']:.6f}",
                "heating_kWh": f"{d['heating_kWh']:.6f}",
                "n_rows": d["n_rows"],
            })

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["label", "sample", "hh_id", "year", "facility_kWh", "heating_kWh", "n_rows"])
        w.writeheader()
        w.writerows(rows)
    print(f"[t31_summarize_smoke] wrote {len(rows)} rows -> {args.out}")

    fail = 0
    # --- E0: current must equal unmodified within 0.001% on both metrics ---
    keys = sorted(set(by_label["unmodified"]) & set(by_label["current"]))
    if not keys:
        print("[E0] FAIL: no matching (sample,hh_id,year) rows between unmodified and current")
        fail = 1
    for key in keys:
        u = by_label["unmodified"][key]
        c = by_label["current"][key]
        fac_pct = pct_diff(u["facility_kWh"], c["facility_kWh"])
        heat_pct = pct_diff(u["heating_kWh"], c["heating_kWh"])
        ok = fac_pct <= 0.001 and heat_pct <= 0.001
        print(f"[E0] {key}: facility_kWh unmodified={u['facility_kWh']:.6f} current={c['facility_kWh']:.6f} "
              f"diff%={fac_pct:.6f} | heating_kWh unmodified={u['heating_kWh']:.6f} current={c['heating_kWh']:.6f} "
              f"diff%={heat_pct:.6f} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            fail = 1

    # --- E1: mechanism_test heating must be HIGHER than unmodified ---
    keys = sorted(set(by_label["unmodified"]) & set(by_label["mechanism_test"]))
    if not keys:
        print("[E1] FAIL: no matching (sample,hh_id,year) rows between unmodified and mechanism_test")
        fail = 1
    for key in keys:
        u = by_label["unmodified"][key]
        m = by_label["mechanism_test"][key]
        delta = m["heating_kWh"] - u["heating_kWh"]
        pct_up = (delta / u["heating_kWh"] * 100.0) if u["heating_kWh"] else float("nan")
        ok = delta > 0
        print(f"[E1] {key}: heating_kWh unmodified={u['heating_kWh']:.6f} mechanism_test={m['heating_kWh']:.6f} "
              f"delta={delta:.6f} ({pct_up:.2f}% change) -> {'PASS (rises)' if ok else 'FAIL (did not rise)'}")
        if not ok:
            fail = 1

    return fail


if __name__ == "__main__":
    sys.exit(main())
