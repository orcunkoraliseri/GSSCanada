#!/usr/bin/env python3
"""
r2d_analysis.py  —  Step 1 of Round-2d: Corrected aggregate level shift.

Reads r2c_per_cell.csv and computes, for each (cell, year):
  agg_level_pct = 100 * |slope_eui * mean_docc_daily| / mean_eui

And per cell (both years):
  agg_paired_pct = 100 * |mean_slope * (mean_docc_2030 - mean_docc_2022)| / mean_eui_avg

Writes r2d_aggregate_corrected.csv (48 rows) and prints the borderline set.
Borderline threshold: >= 1.3% (within ~0.5 pp of the 1.80% MC CI half-width).
Stop condition: if borderline set > 10 cell*years (~500 runs), report and exit.
"""

import os
import sys
import pandas as pd
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R2C_CELL = os.path.join(
    HERE, "..", "r2c_output_sensitivity", "r2c_per_cell.csv"
)
OUT_CSV = os.path.join(HERE, "r2d_aggregate_corrected.csv")

BORDERLINE_THRESH = 1.3   # % — cells at or above this get a spot-check
MC_CI_HW = 1.80           # % — the actual MC CI half-width (the decision line)
MAX_BORDER_RUNS = 500     # stop if borderline set would require more than this

# --------------------------------------------------------------------------
print("=== r2d_analysis.py: Corrected aggregate level shift ===\n")

df = pd.read_csv(R2C_CELL)
print(f"  Loaded {len(df)} cell×year rows from r2c_per_cell.csv")

# --- Per cell×year: aggregate level shift ---
# agg_level_pct = 100 * |slope_eui * mean_docc_daily| / mean_eui
# mean_docc_daily is the SIGNED mean Δocc (disk − IDF, as stored in r2c)
df["agg_level_pct"] = (
    100.0 * np.abs(df["slope_eui"] * df["mean_docc"]) / df["mean_eui"]
)

# --- Per cell: aggregate paired shift ---
# Pivot to get 2022 and 2030 side by side for each cell
y22 = df[df["year"] == 2022].set_index("cell")
y30 = df[df["year"] == 2030].set_index("cell")

paired_rows = {}
for cell in y22.index:
    if cell not in y30.index:
        continue
    r22 = y22.loc[cell]
    r30 = y30.loc[cell]
    mean_slope = (r22["slope_eui"] + r30["slope_eui"]) / 2.0
    delta_docc = r30["mean_docc"] - r22["mean_docc"]     # Δ(mean_docc) between years
    mean_eui = (r22["mean_eui"] + r30["mean_eui"]) / 2.0
    agg_paired_pct = 100.0 * abs(mean_slope * delta_docc) / mean_eui
    paired_rows[cell] = agg_paired_pct

paired_series = pd.Series(paired_rows, name="agg_paired_pct")
df = df.set_index("cell")
df["agg_paired_pct"] = paired_series
df = df.reset_index()

# --- Annotate r2c metric for comparison ---
# r2c used mean_abs_docc (mean of |Δocc| per HH); our corrected metric uses mean_docc (signed)
df["r2c_mean_abs_deui_pct"] = df["mean_abs_deui_pct"]   # rename for clarity in output

# --- Select columns and sort ---
out_cols = [
    "cell", "year", "n_hh",
    "slope_eui", "r2_eui", "mean_eui",
    "mean_docc",           # signed mean Δocc (disk − IDF)
    "mean_abs_docc",       # mean |Δocc| per HH (r2c's metric)
    "agg_level_pct",       # corrected: slope × |mean_docc| / mean_eui
    "agg_paired_pct",      # paired: mean_slope × |Δmean_docc| / mean_eui_avg
    "r2c_mean_abs_deui_pct",   # r2c's (incorrect) per-HH mean |ΔEUI%|
]
out = df[out_cols].sort_values(["cell", "year"])
out.to_csv(OUT_CSV, index=False, float_format="%.4f")
print(f"  Saved: {OUT_CSV}\n")

# --- Print ranked table ---
print(f"{'Cell':<35} {'Yr':>4}  {'slope':>6}  {'mean_docc':>9}  {'agg_level%':>10}  {'agg_paired%':>11}  {'r2c_abs%':>8}")
print("-" * 100)
for _, row in out.sort_values("agg_level_pct", ascending=False).iterrows():
    flag_l = " *** ABOVE CI" if row["agg_level_pct"] >= MC_CI_HW else \
             (" *  BORDER"   if row["agg_level_pct"] >= BORDERLINE_THRESH else "")
    flag_p = " *** ABOVE CI" if (pd.notna(row["agg_paired_pct"]) and row["agg_paired_pct"] >= MC_CI_HW) else \
             (" *  BORDER"   if (pd.notna(row["agg_paired_pct"]) and row["agg_paired_pct"] >= BORDERLINE_THRESH) else "")
    paired_str = f"{row['agg_paired_pct']:10.3f}" if pd.notna(row["agg_paired_pct"]) else f"{'':>10}"
    print(f"{row['cell']:<35} {row['year']:>4}  {row['slope_eui']:>6.2f}  {row['mean_docc']:>9.4f}  "
          f"{row['agg_level_pct']:>10.3f}{flag_l}   {paired_str}{flag_p}   {row['r2c_mean_abs_deui_pct']:>8.3f}")

# --- Identify borderline set ---
border_level = df[df["agg_level_pct"] >= BORDERLINE_THRESH][["cell", "year"]].copy()
border_level["trigger"] = "level"

border_paired_cells = df[
    df["agg_paired_pct"].notna() & (df["agg_paired_pct"] >= BORDERLINE_THRESH)
]["cell"].unique()

# For paired-triggered cells, add BOTH years
paired_rows_list = []
for cell in border_paired_cells:
    for yr in [2022, 2030]:
        paired_rows_list.append({"cell": cell, "year": yr, "trigger": "paired"})
border_paired_df = pd.DataFrame(paired_rows_list) if paired_rows_list else pd.DataFrame(columns=["cell","year","trigger"])

border_all = pd.concat([border_level, border_paired_df], ignore_index=True)
border_all = border_all.drop_duplicates(subset=["cell", "year"])
border_all = border_all.sort_values(["cell", "year"]).reset_index(drop=True)

# Annotate trigger reasons
def get_triggers(cell, year):
    reasons = []
    row = df[(df["cell"] == cell) & (df["year"] == year)]
    if not row.empty and row.iloc[0]["agg_level_pct"] >= BORDERLINE_THRESH:
        reasons.append("level")
    if cell in border_paired_cells:
        reasons.append("paired")
    return "+".join(reasons) if reasons else "?"

border_all["trigger"] = border_all.apply(
    lambda r: get_triggers(r["cell"], r["year"]), axis=1
)

n_border = len(border_all)
n_runs   = n_border * 50  # 50 HH per cell×year

print(f"\n{'='*80}")
print(f"BORDERLINE SELECTION (agg_level or agg_paired >= {BORDERLINE_THRESH}%)")
print(f"{'='*80}")
print(f"\n  Found {n_border} cell×year(s) = {n_runs} spot-check runs\n")

print(f"{'Cell':<35} {'Year':>4}  {'agg_level%':>10}  {'agg_paired%':>11}  {'Trigger'}")
print("-" * 80)
for _, r in border_all.iterrows():
    row = df[(df["cell"] == r["cell"]) & (df["year"] == r["year"])].iloc[0]
    paired_str = f"{row['agg_paired_pct']:10.3f}" if pd.notna(row["agg_paired_pct"]) else f"{'N/A':>10}"
    print(f"{r['cell']:<35} {r['year']:>4}  {row['agg_level_pct']:>10.3f}  {paired_str}  {r['trigger']}")

# --- Stop condition ---
if n_runs > MAX_BORDER_RUNS:
    print(f"\n*** STOP: {n_runs} runs > {MAX_BORDER_RUNS} threshold. REPORT TO MANAGER before Step 2.")
    sys.exit(1)
else:
    print(f"\n  Run count ({n_runs}) is within the {MAX_BORDER_RUNS}-run threshold — proceed to Step 2.")

# --- Write borderline cell list for sbatch ---
border_csv = os.path.join(HERE, "r2d_borderline_cells.csv")
border_all.to_csv(border_csv, index=False)
print(f"  Saved borderline cell list: {border_csv}")

# --- Comparison vs r2c ---
print(f"\n{'='*80}")
print("COMPARISON vs r2c FLAG (how much the corrected metric differs)")
print(f"{'='*80}")
r2c_overall = df["mean_abs_deui_pct"].mean()
corr_level_overall = df["agg_level_pct"].mean()
paired_overall = df["agg_paired_pct"].dropna().mean()
print(f"\n  r2c FLAG used:              mean|ΔEUI%| (per-HH abs)  = {r2c_overall:.3f}%  (was 2.935%)")
print(f"  Corrected level (this run): agg_level_pct mean         = {corr_level_overall:.3f}%")
print(f"  Corrected paired (this run):agg_paired_pct mean        = {paired_overall:.3f}%")
print(f"  MC CI half-width:           {MC_CI_HW}%")
print(f"\n  Key insight: r2c FLAG used mean|Δocc| per HH ({df['mean_abs_docc'].mean():.4f} avg)")
print(f"  which is ~{df['mean_abs_docc'].mean()/df['mean_docc'].abs().mean():.1f}x the signed mean_docc ({df['mean_docc'].abs().mean():.4f} avg)")
print(f"  Noise that averages out inflated r2c by that factor.")
print(f"\nDone.\n")
