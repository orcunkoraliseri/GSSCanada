# ⚠️ 2026-07-18: this one-off script reads the PRE-04T augmented_diaries.csv (top-level outputs_step4). The current pool is sweep/R5_raked_mindwell_actv2/. Re-point before any reuse.
"""
Temporary gap analysis script — READ-ONLY, deletes nothing.
Analyzes the FULL_POOL file that Step-5 --full loads:
  3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/outputs_step4/augmented_diaries.csv

WORK_PEAK_SLOTS: 0-indexed 8-19 = 1-indexed cols 009-020 (wrk30_009 .. wrk30_020)
(matches 04L2 definition: range(8,20), 04:00-origin diary, 08:00-14:00 window)
"""
import pandas as pd
import numpy as np

POOL = (
    r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
    r"\3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\outputs_step4\augmented_diaries.csv"
)

# 0-indexed slots 8-19 → 1-indexed column numbers 9-20
PEAK_1IDX = list(range(9, 21))  # 9,10,...,20
WRK_PEAK_COLS = [f"wrk30_{i:03d}" for i in PEAK_1IDX]
COL_1IDX = list(range(1, 21))   # colleagues30_001..020 (all slots 1-20 needed for peak)
# For colleagues we only look at peak slots too
COL_PEAK_COLS = [f"colleagues30_{i:03d}" for i in PEAK_1IDX]

needed_cols = ["DDAY_STRATA", "IS_SYNTHETIC"] + WRK_PEAK_COLS + COL_PEAK_COLS

print(f"Loading {len(needed_cols)} columns from pool file ...")
df = pd.read_csv(POOL, usecols=needed_cols, low_memory=False)

print(f"Total rows loaded: {len(df):,}")

# ── Row counts by origin ──────────────────────────────────────────────────────
n_obs  = (df["DDAY_STRATA"] == 1).sum()
n_syn  = df["DDAY_STRATA"].isin([2, 3]).sum()
n_full = len(df)
print(f"\nRow counts:")
print(f"  DDAY==1  (observed):  {n_obs:,}")
print(f"  DDAY in {{2,3}} (syn):  {n_syn:,}")
print(f"  Total:                {n_full:,}")

# Also check IS_SYNTHETIC vs DDAY for cross-validation
if "IS_SYNTHETIC" in df.columns:
    is_syn_flag = df["IS_SYNTHETIC"].astype(str).str.strip().str.lower().isin(["1","true","yes","1.0"])
    print(f"\nIS_SYNTHETIC==True rows: {is_syn_flag.sum():,}  (cross-check with DDAY-inferred syn: {n_syn:,})")

# ── Work-peak mean rate ────────────────────────────────────────────────────────
# Mean across all 12 peak slots over all rows (scalar = avg slot-level AT_WORK rate)
wrk_arr   = df[WRK_PEAK_COLS].values.astype(float)
col_arr   = df[COL_PEAK_COLS].values.astype(float)

mask_obs  = (df["DDAY_STRATA"] == 1).values
mask_syn  = df["DDAY_STRATA"].isin([2, 3]).values

def mean_rate(arr, mask=None):
    if mask is not None:
        arr = arr[mask]
    return float(np.nanmean(arr)) * 100  # as %

wp_full = mean_rate(wrk_arr)
wp_obs  = mean_rate(wrk_arr, mask_obs)
wp_syn  = mean_rate(wrk_arr, mask_syn)

print(f"\n=== WORK_PEAK mean AT_WORK rate (slots 8-19, 04:00-origin) ===")
print(f"  Full pool:  {wp_full:.2f}%")
print(f"  Observed (DDAY==1):    {wp_obs:.2f}%")
print(f"  Synthetic (DDAY 2/3):  {wp_syn:.2f}%")

# ── Colleagues channel ─────────────────────────────────────────────────────────
# First check if continuous or binary
col_unique = pd.unique(df[COL_PEAK_COLS].values.ravel())
col_unique_nnan = col_unique[~np.isnan(col_unique.astype(float))] if col_unique.dtype != object else col_unique
# Determine dtype
print(f"\n=== colleagues30 peak-slot value distribution ===")
col_vals = df[COL_PEAK_COLS].values.astype(float).ravel()
col_vals_nonan = col_vals[~np.isnan(col_vals)]
print(f"  Min: {np.nanmin(col_vals):.4f}  Max: {np.nanmax(col_vals):.4f}")
print(f"  Unique value count (sample): {len(np.unique(col_vals_nonan[:100000]))}")
print(f"  Values > 1.0: {(col_vals_nonan > 1.0).sum():,}  (non-zero non-binary if >0)")

# Per-worker nonzero rate of colleagues on at-work slots:
# "Among (row,slot) where wrk30>0, fraction where colleagues30>0"
at_work_mask = wrk_arr > 0   # shape (n_rows, 12)
col_pos_mask = col_arr > 0

# Full
aw_slots_full = at_work_mask.sum()
col_pos_full  = (at_work_mask & col_pos_mask).sum()
colrate_full  = col_pos_full / aw_slots_full * 100 if aw_slots_full > 0 else float('nan')

# Observed
aw_obs = at_work_mask[mask_obs]
cp_obs = col_pos_mask[mask_obs]
aw_slots_obs = aw_obs.sum()
col_pos_obs  = (aw_obs & cp_obs).sum()
colrate_obs  = col_pos_obs / aw_slots_obs * 100 if aw_slots_obs > 0 else float('nan')

# Synthetic
aw_syn = at_work_mask[mask_syn]
cp_syn = col_pos_mask[mask_syn]
aw_slots_syn = aw_syn.sum()
col_pos_syn  = (aw_syn & cp_syn).sum()
colrate_syn  = col_pos_syn / aw_slots_syn * 100 if aw_slots_syn > 0 else float('nan')

print(f"\n=== Colleagues: per-worker-slot nonzero rate (on at-work slots) ===")
print(f"  Full pool:  {colrate_full:.2f}%  (at-work slots: {aw_slots_full:,})")
print(f"  Observed:   {colrate_obs:.2f}%  (at-work slots: {aw_slots_obs:,})")
print(f"  Synthetic:  {colrate_syn:.2f}%  (at-work slots: {aw_slots_syn:,})")

# Mean colleagues30 on at-work slots (obs vs syn), for continuous case
mean_col_obs = np.nanmean(col_arr[mask_obs][aw_obs]) if aw_slots_obs > 0 else float('nan')
mean_col_syn = np.nanmean(col_arr[mask_syn][aw_syn]) if aw_slots_syn > 0 else float('nan')
print(f"\n  Mean colleagues30 value on at-work slots:")
print(f"    Observed: {mean_col_obs:.4f}")
print(f"    Synthetic: {mean_col_syn:.4f}")

print("\n=== DONE ===")
