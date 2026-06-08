#!/usr/bin/env python3
"""
r2d_extract.py  --  Step 3 of Round-2d: extract disk-run EUIs and classify.

Reads:
  - /speed-scratch/o_iseri/step8_r2d/<cell>/sample_*_HH*/<year>/eplustbl.csv
    (disk-schedule spot-check outputs; 50 per cell*year)
  - r2c_per_hh.csv (as-run EUIs from the original campaign)
  - r2d_borderline_cells.csv (the 7 borderline cell*year entries)

Computes per cell*year:
  actual_shift_pct  = 100 * (mean(EUI_disk) - mean(EUI_asrun)) / mean(EUI_asrun)
  actual_paired_pct = 100 * [(mean_disk_2030 - mean_disk_2022) -
                              (mean_asrun_2030 - mean_asrun_2022)] / mean(EUI_asrun_2022)
  WITHIN  if |actual_shift_pct| <= 1.80%
  EXCEEDS if |actual_shift_pct| >  1.80%

Writes r2d_results.csv (per cell*year: disk mean EUI, as-run mean EUI, shift, paired shift, verdict).
Prints the per-cell classification and final verdict.

Run LOCALLY (after scp-ing spot-check outputs from cluster), or on the cluster with adjusted R2D_ROOT.
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# Adjust this path when running locally (after scp)
# or set env var R2D_ROOT to override
R2D_ROOT = os.environ.get(
    "R2D_ROOT",
    "/speed-scratch/o_iseri/step8_r2d"   # cluster default
)
R2C_HH_CSV = os.path.join(HERE, "..", "r2c_output_sensitivity", "r2c_per_hh.csv")
BORDER_CSV  = os.path.join(HERE, "r2d_borderline_cells.csv")
OUT_CSV     = os.path.join(HERE, "r2d_results.csv")
MC_CI_HW    = 1.80   # %

print("=== r2d_extract.py: Step 3 EUI extraction + classification ===\n")
print(f"  R2D_ROOT: {R2D_ROOT}")
print(f"  R2C_HH:   {R2C_HH_CSV}")

# ---- Load reference data ------------------------------------------------
border = pd.read_csv(BORDER_CSV)
r2c_hh = pd.read_csv(R2C_HH_CSV)
# Ensure year is string for matching
r2c_hh["year"] = r2c_hh["year"].astype(str)

print(f"\n  Borderline set: {len(border)} cell*year rows")

# ---- Extract disk-run EUIs from eplustbl.csv ----------------------------
def parse_eplustbl_eui(path):
    """Return conditioned-area EUI (kBtu/ft2) from eplustbl.csv, or None."""
    try:
        df = pd.read_csv(path, header=None)
        # Look for 'Total Site Energy' row and 'Energy Per Conditioned Building Area'
        for i, row in df.iterrows():
            if "Total Site Energy" in str(row.iloc[0]):
                # Try columns for kBtu/ft2 value (typically col 3 or 4)
                for col in range(1, min(len(row), 8)):
                    try:
                        val = float(str(row.iloc[col]).replace(",", ""))
                        if 1.0 < val < 1000.0:   # plausible EUI range kBtu/ft2
                            return val
                    except (ValueError, TypeError):
                        pass
        return None
    except Exception:
        return None


def parse_eplustbl_eui_robust(path):
    """
    Parse eplustbl.csv for per-conditioned-area EUI (kBtu/ft2).

    Matches r2c_analysis.py extract_eui: reads lines starting with
    ',Total Site Energy,' and takes parts[4] (index 4 after comma-split),
    which is eui_site_cond_kbtu_ft2.  This is the same column stored in
    r2c_per_hh.csv as 'eui_cond', ensuring apples-to-apples comparison.

    Line format: ,Total Site Energy,<total_kbtu>,<per_total_area>,<per_cond_area>,...
    """
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            for line in f:
                if line.startswith(",Total Site Energy,"):
                    parts = line.split(",")
                    # parts[4] = per conditioned building area (kBtu/ft2)
                    try:
                        val = float(parts[4].strip())
                        if 1.0 < val < 2000.0:   # sanity range for residential EUI
                            return val
                    except (IndexError, ValueError):
                        pass
        return None
    except Exception:
        return None


disk_records = []
n_found = 0
n_missing = 0

for _, row in border.iterrows():
    cell = row["cell"]
    year = str(int(row["year"]))
    arch = cell.split("__")[0]
    city = cell.split("__")[1]

    cell_dir = os.path.join(R2D_ROOT, cell)
    pattern  = os.path.join(cell_dir, f"sample_*_HH*", year, "eplustbl.csv")
    tbl_files = sorted(glob.glob(pattern))

    if not tbl_files:
        print(f"  WARN: no eplustbl.csv found for {cell}/{year} — sims not yet complete?")
        n_missing += 1
        continue

    for tbl in tbl_files:
        # Extract HH id from directory name (sample_NNN_HH<id>)
        parts = tbl.replace("\\", "/").split("/")
        sample_dir = next((p for p in parts if p.startswith("sample_")), "")
        hh_id_str = sample_dir.split("_HH")[-1] if "_HH" in sample_dir else ""
        try:
            hh_id = int(hh_id_str)
        except ValueError:
            hh_id = -1

        eui = parse_eplustbl_eui_robust(tbl)
        if eui is None:
            print(f"  WARN: could not parse EUI from {tbl}")
            continue
        disk_records.append({"cell": cell, "year": year, "hh_id": hh_id, "eui_disk": eui})
        n_found += 1

print(f"\n  Disk EUI records parsed: {n_found}  ({n_missing} cell*year groups missing)")

if n_found == 0:
    print("\n  No disk EUIs found — have the spot-check sims completed?")
    print("  Run this script after the cluster jobs finish and you scp the results.")
    sys.exit(1)

disk_df = pd.DataFrame(disk_records)
disk_df["year"] = disk_df["year"].astype(str)

# ---- Compute per-cell*year means ----------------------------------------
disk_mean = disk_df.groupby(["cell", "year"])["eui_disk"].agg(
    mean_eui_disk="mean", n_disk="count"
).reset_index()

asrun_mean = (
    r2c_hh.groupby(["cell", "year"])["eui_cond"]
    .agg(mean_eui_asrun="mean", n_asrun="count")
    .reset_index()
)

merged = disk_mean.merge(asrun_mean, on=["cell", "year"], how="inner")
merged["actual_shift_pct"] = (
    100.0 * (merged["mean_eui_disk"] - merged["mean_eui_asrun"]) / merged["mean_eui_asrun"]
)

# ---- Classify level verdict -----------------------------------------------
merged["level_verdict"] = merged["actual_shift_pct"].abs().map(
    lambda v: "WITHIN" if v <= MC_CI_HW else "EXCEEDS"
)

# ---- Compute paired shift per cell (2022 vs 2030) -------------------------
paired_rows = []
cells_with_both_years = merged.groupby("cell").filter(
    lambda g: set(g["year"].astype(str)) >= {"2022", "2030"}
)["cell"].unique()

for cell in cells_with_both_years:
    sub = merged[merged["cell"] == cell].set_index("year")
    if "2022" not in sub.index or "2030" not in sub.index:
        continue
    disk_delta  = sub.loc["2030", "mean_eui_disk"]  - sub.loc["2022", "mean_eui_disk"]
    asrun_delta = sub.loc["2030", "mean_eui_asrun"] - sub.loc["2022", "mean_eui_asrun"]
    denom = sub.loc["2022", "mean_eui_asrun"]
    paired_pct = 100.0 * (disk_delta - asrun_delta) / denom
    paired_rows.append({
        "cell": cell,
        "actual_paired_pct": paired_pct,
        "paired_verdict": "WITHIN" if abs(paired_pct) <= MC_CI_HW else "EXCEEDS"
    })

if paired_rows:
    paired_df = pd.DataFrame(paired_rows)
    merged = merged.merge(paired_df, on="cell", how="left")
else:
    merged["actual_paired_pct"] = float("nan")
    merged["paired_verdict"] = ""

# ---- Save results ----------------------------------------------------------
merged.to_csv(OUT_CSV, index=False, float_format="%.4f")
print(f"\n  Results saved: {OUT_CSV}\n")

# ---- Print classification table -------------------------------------------
print(f"{'Cell':<35} {'Yr':>4}  {'EUI_disk':>9}  {'EUI_asrun':>9}  {'shift%':>7}  {'Lvl':>7}  {'paired%':>8}  {'Paired':>7}")
print("-" * 105)
for _, row in merged.sort_values(["cell", "year"]).iterrows():
    p_str  = f"{row['actual_paired_pct']:8.3f}" if pd.notna(row.get("actual_paired_pct")) else f"{'N/A':>8}"
    pv_str = row.get("paired_verdict", "")
    print(f"{row['cell']:<35} {row['year']:>4}  {row['mean_eui_disk']:>9.3f}  "
          f"{row['mean_eui_asrun']:>9.3f}  {row['actual_shift_pct']:>+7.3f}  "
          f"{row['level_verdict']:>7}  {p_str}  {pv_str}")

# ---- Final verdict --------------------------------------------------------
n_exceeds_level  = (merged["level_verdict"] == "EXCEEDS").sum()
n_exceeds_paired = (merged.get("paired_verdict", pd.Series(dtype=str)) == "EXCEEDS").sum()
exceeds_cells = merged[merged["level_verdict"] == "EXCEEDS"][["cell", "year", "actual_shift_pct"]].values.tolist()

print(f"\n{'='*80}")
print("VERDICT")
print(f"{'='*80}")
print(f"  MC CI half-width threshold: {MC_CI_HW}%")
print(f"  Level EXCEEDS: {n_exceeds_level} cell*year(s)")
print(f"  Paired EXCEEDS: {n_exceeds_paired} cell(s)")

if n_exceeds_level == 0 and n_exceeds_paired == 0:
    print("\n  ** OPTION A CONFIRMED at output level **")
    print("  ALL borderline cells are WITHIN the MC CI for both level and paired shift.")
    print("  Gap moves no reported cell-mean EUI / WFH delta-EUI beyond MC noise.")
    print("  Recommend: adopt-as-run + methods documentation.")
else:
    print(f"\n  ** {n_exceeds_level + n_exceeds_paired} cell(s) EXCEED the CI — SCOPED RE-SIM recommended **")
    print("  Cells that exceed (return to manager for GO on re-sim):")
    for cell, year, shift in exceeds_cells:
        print(f"    {cell} / {year}:  actual_shift = {shift:+.3f}%")
    print(f"\n  Recommended: re-sim ONLY these cells ({len(exceeds_cells) * 50} runs), not the full 2400.")
    print("  DO NOT launch without explicit manager/user GO.")

print()
