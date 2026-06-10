#!/usr/bin/env python3
"""
step8_val_v2.py — Stage 4 validation for corrected v2 campaign (953111).

Checks:
  1. L&E gate: InteriorLights > 50 kWh/yr and InteriorEquipment > 1000 kWh/yr per run
     (bug caused these to be ~0; threshold is well below smoke-test values of ~130 / ~6500)
  2. Peak-hour gate: reports distribution of facility-electricity peak hour across all runs
  3. EUI: reads Electricity + Gas intensity from eplustbl.csv (kBtu/ft2 -> kWh/m2)
  4. Corrupt comparison: for 1 sample per cell, compares peak hour between v2 and corrupt archive

Usage (on cluster):
  python step8_val_v2.py [--v2-root <path>] [--corrupt-root <path>] [--n-sample <int>]

Outputs a plain-text summary to stdout.  Intended to run as a SLURM job; PASS/FAIL lines
allow quick grep on the log.
"""
import os
import sys
import csv
import argparse
import glob as _glob
from collections import defaultdict

import numpy as np
import pandas as pd

V2_DEFAULT      = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/campaign_N50"
CORRUPT_DEFAULT = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_CORRUPT_953076/campaign_N50"

YEARS = ["2005", "2010", "2015", "2022", "2030"]

# Thresholds
LE_LIGHTS_MIN_KWH  = 50.0    # per-run annual; smoke gave ~128-151
LE_EQUIP_MIN_KWH   = 1000.0  # per-run annual; smoke gave ~6252-6790
J_TO_KWH           = 1.0 / 3_600_000.0
KBTU_FT2_TO_KWH_M2 = 3.154591


def list_cells(root):
    return sorted(d for d in os.listdir(root)
                  if os.path.isdir(os.path.join(root, d)) and "__" in d)


def list_samples(cell_dir):
    return sorted(d for d in os.listdir(cell_dir)
                  if os.path.isdir(os.path.join(cell_dir, d)) and d.startswith("sample_"))


def read_hourly(path):
    df = pd.read_csv(path, index_col=0)
    df.index = df.index.astype(int)
    return df


def annual_kwh(df, col):
    if col not in df.columns:
        return np.nan
    return float(df[col].sum() * J_TO_KWH)


def facility_peak_hour(df):
    col = "Electricity:Facility"
    if col not in df.columns:
        return np.nan
    vals = df[col].values
    return int(np.argmax(vals) % 24)


def read_eui_eplustbl(tbl_path):
    """Parse eplustbl.csv for Electricity + NatGas intensity (kWh/m2) on conditioned area."""
    try:
        lines = open(tbl_path, encoding="latin-1").readlines()
    except OSError:
        return np.nan
    in_section = False
    for i, line in enumerate(lines):
        if "Utility Use Per Conditioned Floor Area" in line:
            in_section = True
        if in_section and ",Total," in line:
            parts = line.split(",")
            try:
                elec_kbtu = float(parts[2]) if len(parts) > 2 and parts[2].strip() else 0.0
                gas_kbtu  = float(parts[3]) if len(parts) > 3 and parts[3].strip() else 0.0
                return (elec_kbtu + gas_kbtu) * KBTU_FT2_TO_KWH_M2
            except ValueError:
                continue
    return np.nan


def scan_cell(cell_dir, n_sample, years=YEARS):
    """Return list of dicts: one per (sample, year)."""
    samples = list_samples(cell_dir)[:n_sample]
    rows = []
    for samp in samples:
        for yr in years:
            csv_path = os.path.join(cell_dir, samp, yr, "hourly_meters.csv")
            tbl_path = os.path.join(cell_dir, samp, yr, "eplustbl.csv")
            if not os.path.exists(csv_path):
                continue
            df = read_hourly(csv_path)
            lights = annual_kwh(df, "InteriorLights:Electricity")
            equip  = annual_kwh(df, "InteriorEquipment:Electricity")
            fac    = annual_kwh(df, "Electricity:Facility")
            peak   = facility_peak_hour(df)
            eui    = read_eui_eplustbl(tbl_path)
            rows.append({
                "sample": samp, "year": yr,
                "lights_kwh": lights, "equip_kwh": equip, "facility_kwh": fac,
                "peak_hour": peak, "eui_kwh_m2": eui,
            })
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--v2-root",      default=V2_DEFAULT)
    p.add_argument("--corrupt-root", default=CORRUPT_DEFAULT)
    p.add_argument("--n-sample",     type=int, default=2)
    args = p.parse_args()

    v2_root      = args.v2_root
    corrupt_root = args.corrupt_root
    n_sample     = args.n_sample

    cells = list_cells(v2_root)
    print(f"\n=== Step-8 v2 Validation  (953111) ===")
    print(f"Campaign : {v2_root}")
    print(f"Cells    : {len(cells)}  |  Samples per cell: {n_sample}  |  Years: {YEARS}")
    print()

    all_rows = []
    for cell in cells:
        cell_dir = os.path.join(v2_root, cell)
        rows = scan_cell(cell_dir, n_sample)
        for r in rows:
            r["cell"] = cell
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    print(f"Scanned {len(df)} run-year pairs across {df['cell'].nunique()} cells.\n")

    # --- Gate 1: L&E ---
    print("--- Gate 1: L&E (lights > 50 kWh/yr, equip > 1000 kWh/yr) ---")
    fail_lights = df[df["lights_kwh"] < LE_LIGHTS_MIN_KWH]
    fail_equip  = df[df["equip_kwh"]  < LE_EQUIP_MIN_KWH]
    if fail_lights.empty and fail_equip.empty:
        print("PASS  All runs pass L&E thresholds.")
    else:
        if not fail_lights.empty:
            print(f"FAIL  {len(fail_lights)} runs below lights threshold ({LE_LIGHTS_MIN_KWH} kWh/yr):")
            print(fail_lights[["cell", "sample", "year", "lights_kwh"]].to_string(index=False))
        if not fail_equip.empty:
            print(f"FAIL  {len(fail_equip)} runs below equip threshold ({LE_EQUIP_MIN_KWH} kWh/yr):")
            print(fail_equip[["cell", "sample", "year", "equip_kwh"]].to_string(index=False))
    print()

    # --- Gate 2: L&E summary ---
    print("--- L&E summary by archetype ---")
    df["archetype"] = df["cell"].str.split("__").str[0]
    for arch, g in df.groupby("archetype"):
        print(f"  {arch:15s}  lights={g['lights_kwh'].mean():.0f}±{g['lights_kwh'].std():.0f} kWh  "
              f"equip={g['equip_kwh'].mean():.0f}±{g['equip_kwh'].std():.0f} kWh  "
              f"facility={g['facility_kwh'].mean():.0f}±{g['facility_kwh'].std():.0f} kWh")
    print()

    # --- Gate 3: Peak hour distribution ---
    print("--- Gate 2: Peak facility electricity hour distribution ---")
    peak_counts = df["peak_hour"].value_counts().sort_index()
    print("  Hour | Count")
    for h, c in peak_counts.items():
        bar = "#" * int(c / peak_counts.max() * 30)
        print(f"  h{int(h):02d}  | {c:4d}  {bar}")
    print()

    # --- EUI summary ---
    eui_valid = df.dropna(subset=["eui_kwh_m2"])
    if not eui_valid.empty:
        print("--- EUI summary (elec+gas, conditioned floor area, kWh/m2/yr) ---")
        for arch, g in eui_valid.groupby("archetype"):
            print(f"  {arch:15s}  EUI = {g['eui_kwh_m2'].mean():.1f}±{g['eui_kwh_m2'].std():.1f} kWh/m2")
        print(f"  Overall          EUI = {eui_valid['eui_kwh_m2'].mean():.1f}±{eui_valid['eui_kwh_m2'].std():.1f} kWh/m2")
        print()

    # --- Corrupt comparison ---
    if os.path.isdir(corrupt_root):
        print("--- Corrupt vs v2 peak-hour comparison (first sample, 2022, all cells) ---")
        print(f"  {'Cell':35s}  corrupt_peak  v2_peak  shift")
        corrupt_cells = set(list_cells(corrupt_root))
        for cell in cells:
            if cell not in corrupt_cells:
                continue
            corrupt_dir = os.path.join(corrupt_root, cell)
            v2_dir      = os.path.join(v2_root, cell)
            c_samps = list_samples(corrupt_dir)
            v_samps = list_samples(v2_dir)
            if not c_samps or not v_samps:
                continue
            # Use same sample index if possible
            c_csv = os.path.join(corrupt_dir, c_samps[0], "2022", "hourly_meters.csv")
            v_csv = os.path.join(v2_dir,      v_samps[0], "2022", "hourly_meters.csv")
            if not os.path.exists(c_csv) or not os.path.exists(v_csv):
                continue
            c_peak = facility_peak_hour(read_hourly(c_csv))
            v_peak = facility_peak_hour(read_hourly(v_csv))
            shift  = (v_peak - c_peak) % 24
            print(f"  {cell:35s}  h{c_peak:02d}           h{v_peak:02d}     +{shift}h")
        print()
    else:
        print(f"[INFO] Corrupt archive not found at {corrupt_root}; skipping comparison.\n")

    # --- Overall verdict ---
    pass_count = (
        (fail_lights.empty and fail_equip.empty)
    )
    print("=== OVERALL VERDICT ===")
    if pass_count:
        print("PASS  L&E gate passed.  Review peak-hour table above for clock sanity.")
    else:
        print("FAIL  One or more gates failed — see details above.")
    print()


if __name__ == "__main__":
    main()
