#!/usr/bin/env python3
"""
3rdJ_06_calibrate_C_activity_weekend_2split.py  (2026-06-26)  --  Calibration-C

Post-hoc correction of three Step-6 drifts in the 2030 deliverable:
  0. Weekend wrk30 inflation  (calibration-B capped weekday work only; weekend night wrk30
                               was ~22% vs observed ~2-3%). FIX (2026-06-26 Fix C): added
                               Stage 0 to cap weekend wrk30 to observed-2022 weekend level.
  1. Weekend home occupancy drop  (weekend hom30 was not the calibration-B focus).
  2. Activity-code collapse       (act30 un-calibrated; sleep 34.6 -> 22.8 pct of slots).

Core principle: WHERE people are (home/work/out) is the forecast -- kept.
WHAT they do given location is taken from real 2022, conditional on state.
Weekend wrk30 is capped to observed 2022 level in Stage 0 (trim-only: 1->0 flips only).
Weekday wrk30 is NEVER modified.

Stage 0 -- weekend work cap (wrk30, DDAY_STRATA in {2,3} only) [added 2026-06-26]:
  Per slot: if 2030 weekend wrk30 rate > observed-2022 weekend rate, flip the excess
  working person-slots (1->0), seed=42.  Never fabricate work (no 0->1 flips).
  Weekday wrk30 (DDAY_STRATA=1) untouched.

Stage 1 -- weekend home restore (hom30, DDAY_STRATA in {2,3} only):
  Per (stratum x slot): raise/lower 2030 weekend home rate to observed 2022 level by
  flipping OUT<->HOME person-slots (seed=42, never touching wrk30=1 rows).
  Now also handles rows freed from Stage 0 (rows that were working and are now OUT/HOME).
  Then apply 04M min-dwell smoother to weekend hom30 rows.
  Weekday (DDAY_STRATA=1) hom30 left untouched.

Stage 2 -- activity restore (act30, ALL strata, conditional on state):
  State per (row, slot) AFTER Stage 1: WORK if wrk30=1; HOME if hom30=1; else OUT.
  For each (slot x state) cell, donor-resample 2030 act30 from the observed 2022
  act30 pool in that cell (vectorized: one rng.choice per cell). Fallback to
  all-slot state pool if cell < 20 samples.

I/O:
  Input A (2030): Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell.csv
  Input B (2022): Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv
  Output C:       Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv

seed=42. pandas + numpy only. Atomic write (.tmp -> os.replace). No new packages.
Build: 2026-06-26 (employee, Claude Sonnet 4.6)
Fix C added: 2026-06-26 (Stage 0 weekend work cap; triggered by Step-7 validator E.4 FAIL).
Design: Step7_docs/3rdJ_07_bemIntegration_2split.md -- POST-HOC CALIBRATION-C section.
"""

from __future__ import annotations

import os
import shutil
import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths (resolved relative to this script's location)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent              # Step6_docs/
BASE = HERE.parent.parent.parent                    # GSSCanada-main/

IN_A = HERE / "outputs_step6" / "2030_synthetic_diaries_2split_calibrated_mindwell.csv"
IN_B = (BASE / "3J_docs_occ_nTemp" / "Leg2_2-split"
        / "Step5_docs" / "outputs_step5"
        / "3rdJ_25CEN_aug_Full_Aggregated_excl.csv")
OUT_C = HERE / "outputs_step6" / "2030_synthetic_diaries_2split_calibrated_mindwell_C.csv"

# ---------------------------------------------------------------------------
# Column groups
# ---------------------------------------------------------------------------
N_SLOTS = 48
HOM = [f"hom30_{i:03d}" for i in range(1, N_SLOTS + 1)]
WRK = [f"wrk30_{i:03d}" for i in range(1, N_SLOTS + 1)]
ACT = [f"act30_{i:03d}" for i in range(1, N_SLOTS + 1)]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MIN_DWELL     = 2    # 04M default: min contiguous run length; 1-slot blips merged
SMALL_CELL    = 20   # fallback threshold: pool size below this uses all-slot pool
WEEKEND_STRATA = [2, 3]
WEEKDAY_STRATA = [1]
BANDS          = ["conservative", "hybrid", "fullyhybrid"]

# State codes (internal)
STATE_OUT  = 0
STATE_HOME = 1
STATE_WORK = 2

# MET map (verbatim from 3rdJ_07_aug_to_bem_2split.py OD-7A; for diagnostic only)
MET = {
    0: 0, 1: 125, 2: 175, 3: 190, 4: 195, 5: 70, 6: 105,
    7: 170, 8: 110, 9: 90, 10: 85, 11: 245, 12: 105, 13: 140, 14: 135,
}

# Daytime slots (1-indexed 11-26 = 09:00-17:00; 0-indexed 10-25)
DAYTIME_IDX = list(range(10, 26))   # 16 slots, 0-indexed
DAYTIME_HOM = [HOM[i] for i in DAYTIME_IDX]


# ---------------------------------------------------------------------------
# Min-dwell smoother (ported verbatim from 3rdJ_04M_mindwell_2split.py)
# ---------------------------------------------------------------------------
def apply_min_dwell(arr: np.ndarray, min_dwell: int = 2) -> tuple[np.ndarray, int]:
    """Apply minimum-dwell smoothing to a (N_rows, 48) binary float array.

    Any contiguous run of identical values with length < min_dwell that has the
    opposite value on BOTH sides (interior) or one side (edge) is replaced by the
    neighbour value. NaN slots are left untouched. Returns (smoothed_arr, n_changed).
    """
    if min_dwell <= 1:
        return arr.copy(), 0

    arr = arr.copy()
    n_rows, n_cols = arr.shape
    total_changed = 0

    for _pass in range(min_dwell):
        changed_this_pass = 0

        for i in range(n_cols):
            col_i = arr[:, i]
            nan_i = np.isnan(col_i)

            if i == 0:
                right = arr[:, 1]
                nan_r = np.isnan(right)
                valid = ~nan_i & ~nan_r
                flip = valid & (col_i != right)
                arr[flip, i] = right[flip]
                changed_this_pass += int(flip.sum())

            elif i == n_cols - 1:
                left = arr[:, n_cols - 2]
                nan_l = np.isnan(left)
                valid = ~nan_i & ~nan_l
                flip = valid & (col_i != left)
                arr[flip, i] = left[flip]
                changed_this_pass += int(flip.sum())

            else:
                left  = arr[:, i - 1]
                right = arr[:, i + 1]
                nan_l = np.isnan(left)
                nan_r = np.isnan(right)
                valid = ~nan_i & ~nan_l & ~nan_r
                flip  = valid & (col_i != left) & (col_i != right)
                arr[flip, i] = left[flip]   # flip to left (= right, both differ from centre)
                changed_this_pass += int(flip.sum())

        total_changed += changed_this_pass
        if changed_this_pass == 0:
            break

    return arr, total_changed


# ---------------------------------------------------------------------------
# Atomic write helper
# ---------------------------------------------------------------------------
def atomic_write(df: pd.DataFrame, path: Path) -> None:
    """Write df atomically (.tmp -> os.replace). Back up pre-existing target once."""
    today = datetime.date.today().isoformat()
    if path.exists():
        bak = path.parent / f"{path.stem}_BAK_{today}{path.suffix}"
        if not bak.exists():
            shutil.copy2(path, bak)
            print(f"  Backed up -> {bak.name}", flush=True)
    tmp_path = str(path) + ".tmp"
    df.to_csv(tmp_path, index=False)
    os.replace(tmp_path, str(path))
    print(f"  WROTE {path.name}: {len(df):,} rows", flush=True)


# ---------------------------------------------------------------------------
# Diagnostic: compute mean WD metabolic per band from act30 (pre-Step7 proxy)
# ---------------------------------------------------------------------------
def met_proxy(df: pd.DataFrame) -> dict[str, float]:
    """Compute mean WD Metabolic_Rate (W) per band using the MET map (proxy for Step-7 output)."""
    wd_mask = df["DDAY_STRATA"] == 1
    result = {}
    for band in BANDS:
        sub = df[wd_mask & (df["BAND"] == band)]
        if len(sub) == 0:
            result[band] = float("nan")
            continue
        arr = sub[ACT].values.astype(float)   # (N, 48)
        met_arr = np.vectorize(lambda v: MET.get(int(v) if not np.isnan(v) else 0, 0))(arr)
        result[band] = float(met_arr.mean())
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    rng = np.random.default_rng(42)

    print("=" * 70, flush=True)
    print("3rdJ_06_calibrate_C_activity_weekend_2split.py -- Calibration-C", flush=True)
    print(f"  Input A (2030): {IN_A}", flush=True)
    print(f"  Input B (2022): {IN_B}", flush=True)
    print(f"  Output C:       {OUT_C}", flush=True)
    print("=" * 70, flush=True)

    # ── Pre-flight checks ────────────────────────────────────────────────────
    if not IN_A.exists():
        raise FileNotFoundError(f"Input A not found: {IN_A}")
    if not IN_B.exists():
        raise FileNotFoundError(f"Input B not found: {IN_B}")

    # ── Load inputs ──────────────────────────────────────────────────────────
    print("\n[LOAD] Reading inputs ...", flush=True)

    df_2030 = pd.read_csv(IN_A, low_memory=False)
    print(f"  Input A rows: {len(df_2030):,}  |  BAND = {sorted(df_2030['BAND'].unique())}  "
          f"|  DDAY_STRATA counts = {df_2030['DDAY_STRATA'].value_counts().to_dict()}",
          flush=True)
    assert len(df_2030) >= 111_024, f"Input A unexpectedly small ({len(df_2030)} rows); sync full deliverable."

    # For Input B, read only the columns we need
    needed_b = set(HOM + WRK + ACT + ["DDAY_STRATA"])
    obs22 = pd.read_csv(IN_B, low_memory=False, usecols=lambda c: c in needed_b)
    print(f"  Input B rows: {len(obs22):,}  |  "
          f"DDAY_STRATA counts = {obs22['DDAY_STRATA'].value_counts().to_dict()}",
          flush=True)

    # Working copy (will be modified in-place on array views, then written)
    out = df_2030.copy()

    # Snapshot original wrk30 and weekday hom30 for integrity checks
    wrk_orig = df_2030[WRK].values.copy()
    wd_mask_orig = df_2030["DDAY_STRATA"].isin(WEEKDAY_STRATA).values
    hom_wd_orig = df_2030.loc[wd_mask_orig, HOM].values.copy()

    # ── BASELINE diagnostics (before) ────────────────────────────────────────
    print("\n[BASELINE] Pre-calibration diagnostics:", flush=True)

    act_before = df_2030[ACT].values.astype(float)
    sleep_before = float((act_before == 5).mean())
    print(f"  Sleep (code 5) share BEFORE: {sleep_before:.4f} ({sleep_before:.1%})", flush=True)

    we_mask_b4 = df_2030["DDAY_STRATA"].isin(WEEKEND_STRATA)
    we_day_before = float(df_2030.loc[we_mask_b4, DAYTIME_HOM].values.mean())
    print(f"  WE daytime (slots 11-26) hom30 BEFORE: {we_day_before:.4f}", flush=True)

    print(f"  WD daytime (slots 11-26) hom30 by band BEFORE:", flush=True)
    wd_day_before = {}
    wd_mask_b4 = df_2030["DDAY_STRATA"] == 1
    for band in BANDS:
        v = float(df_2030.loc[wd_mask_b4 & (df_2030["BAND"] == band), DAYTIME_HOM].values.mean())
        wd_day_before[band] = v
        print(f"    {band}: {v:.4f}", flush=True)

    met_before = met_proxy(df_2030)
    print(f"  WD mean Metabolic proxy BEFORE (W): "
          f"conservative={met_before['conservative']:.1f}  "
          f"hybrid={met_before['hybrid']:.1f}  "
          f"fullyhybrid={met_before['fullyhybrid']:.1f}", flush=True)

    # Weekend wrk30 baseline (before Stage 0)
    we_wrk_before = float(out.loc[out["DDAY_STRATA"].isin(WEEKEND_STRATA), WRK].values.mean())
    print(f"  WE overall wrk30 rate BEFORE Stage 0: {we_wrk_before:.4f} ({we_wrk_before:.1%})", flush=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 0: Weekend work cap (wrk30, DDAY_STRATA in {2, 3} only)  [added 2026-06-26]
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[STAGE 0] Weekend work cap (trim-only: 1->0 flips, seed=42)", flush=True)
    print("  Target = obs-2022 weekend per-slot wrk30 mean. Weekday wrk30 untouched.", flush=True)

    total_s0_flipped = 0
    for stratum in WEEKEND_STRATA:
        obs_str = obs22[obs22["DDAY_STRATA"] == stratum]
        d30_mask = (out["DDAY_STRATA"] == stratum).values
        n = int(d30_mask.sum())

        if len(obs_str) == 0 or n == 0:
            print(f"  Stratum {stratum}: no rows -- skip", flush=True)
            continue

        print(f"\n  -- Stratum {stratum} (Sat=2 / Sun=3)  "
              f"n_2030={n:,}  n_2022_obs={len(obs_str):,} --", flush=True)

        # Per-slot observed-2022 weekend wrk30 target
        target_wrk = obs_str[WRK].mean().values.astype(float)  # shape (48,)

        # Extract current wrk30 for this stratum (writable local copy)
        wrk_s = out.loc[d30_mask, WRK].values.astype(float).copy()  # (n, 48)
        rate_before_stratum = float(wrk_s.mean())

        n_flipped_stratum = 0
        for s in range(N_SLOTS):
            p_obs = float(target_wrk[s])
            p_30 = float(wrk_s[:, s].mean())

            if p_30 <= p_obs + 1e-9:
                continue  # 2030 at or below observed -- no trimming needed

            # Trim: flip round((p30 - p_obs) * n) from 1 -> 0
            n_flip = int(round((p_30 - p_obs) * n))
            if n_flip <= 0:
                continue

            working_idx = np.where(wrk_s[:, s] == 1)[0]
            if len(working_idx) == 0:
                continue

            n_flip = min(n_flip, len(working_idx))
            chosen = rng.choice(working_idx, size=n_flip, replace=False)
            wrk_s[chosen, s] = 0.0
            n_flipped_stratum += n_flip

        # Write modified wrk30 back to out
        out.loc[d30_mask, WRK] = wrk_s

        rate_after_stratum = float(wrk_s.mean())
        obs_rate = float(target_wrk.mean())
        print(f"    Person-slots flipped (1->0): {n_flipped_stratum:,}", flush=True)
        print(f"    Overall wrk30 rate: obs22={obs_rate:.4f}  "
              f"before={rate_before_stratum:.4f}  after={rate_after_stratum:.4f}", flush=True)
        total_s0_flipped += n_flipped_stratum

    we_wrk_after_s0 = float(out.loc[out["DDAY_STRATA"].isin(WEEKEND_STRATA), WRK].values.mean())
    print(f"\n  [STAGE 0 summary] Total person-slots flipped: {total_s0_flipped:,}", flush=True)
    print(f"  WE wrk30 rate: BEFORE={we_wrk_before:.4f}  AFTER={we_wrk_after_s0:.4f}", flush=True)

    # Re-snapshot wrk_orig AFTER Stage 0: Stage 1 + Stage 2 integrity checks verify
    # that wrk30 is NOT further modified after this point (weekday was always untouched,
    # weekend was intentionally capped in Stage 0 above).
    wrk_orig = out[WRK].values.copy()
    print("  [OK] wrk_orig re-snapshotted post Stage-0 "
          "(Stage 1/2 checks now enforce no further change)", flush=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 1: Weekend home restore
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[STAGE 1] Weekend home restore (DDAY_STRATA in {2, 3})", flush=True)
    print("  wrk30 locked (Stage 0 done); weekday hom30 untouched; Stage 1 touches weekend hom30 only.", flush=True)

    for stratum in WEEKEND_STRATA:
        obs_str  = obs22[obs22["DDAY_STRATA"] == stratum]
        d30_mask = (out["DDAY_STRATA"] == stratum).values
        d30_idx  = np.where(d30_mask)[0]
        n        = len(d30_idx)

        if len(obs_str) == 0 or n == 0:
            print(f"  Stratum {stratum}: no rows -- skip", flush=True)
            continue

        print(f"\n  -- Stratum {stratum} (Sat=2 / Sun=3)  "
              f"n_2030={n:,}  n_2022_obs={len(obs_str):,} --", flush=True)

        # Per-slot target from 2022 observed
        target = obs_str[HOM].mean().values.astype(float)   # shape (48,)

        # Extract current arrays for this stratum
        hom_s = out.loc[d30_mask, HOM].values.astype(float)  # (n, 48)
        wrk_s = out.loc[d30_mask, WRK].values.astype(float)  # (n, 48)

        n_up = 0
        n_dn = 0

        for s in range(N_SLOTS):
            p_obs = float(target[s])
            p_30  = float(hom_s[:, s].mean())
            diff  = p_obs - p_30

            if abs(diff) < 1e-9:
                continue

            if diff > 0:
                # Need more HOME: flip OUT -> HOME (among hom30=0 AND wrk30=0)
                n_flip = int(round(diff * n))
                if n_flip <= 0:
                    continue
                cands = np.where((hom_s[:, s] == 0) & (wrk_s[:, s] == 0))[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                hom_s[chosen, s] = 1.0
                n_up += n_flip
            else:
                # Need less HOME: flip HOME -> OUT (among hom30=1 AND wrk30=0)
                n_flip = int(round((-diff) * n))
                if n_flip <= 0:
                    continue
                cands = np.where((hom_s[:, s] == 1) & (wrk_s[:, s] == 0))[0]
                if len(cands) == 0:
                    continue
                n_flip = min(n_flip, len(cands))
                chosen = rng.choice(cands, size=n_flip, replace=False)
                hom_s[chosen, s] = 0.0
                n_dn += n_flip

        print(f"    Slots flipped UP (OUT->HOME):   {n_up:,}", flush=True)
        print(f"    Slots flipped DOWN (HOME->OUT): {n_dn:,}", flush=True)

        # Before/after daytime summary
        hom_before_day = float(out.loc[d30_mask, DAYTIME_HOM].values.mean())
        hom_after_day  = float(hom_s[:, DAYTIME_IDX].mean())
        target_day     = float(target[DAYTIME_IDX].mean())
        print(f"    Daytime (slots 11-26) hom30: before={hom_before_day:.4f}  "
              f"after={hom_after_day:.4f}  target={target_day:.4f}", flush=True)

        # Write back the modified hom30
        out.loc[d30_mask, HOM] = hom_s

    # Apply 04M min-dwell smoother to ALL weekend hom30 rows
    print("\n  Applying 04M min-dwell smoother (min_dwell=2) to weekend hom30 rows ...", flush=True)
    we_mask = out["DDAY_STRATA"].isin(WEEKEND_STRATA).values
    hom_we  = out.loc[we_mask, HOM].values.astype(float)
    hom_we_smooth, n_md_changed = apply_min_dwell(hom_we, MIN_DWELL)
    out.loc[we_mask, HOM] = hom_we_smooth
    print(f"    Min-dwell: {n_md_changed:,} weekend hom30 slots changed", flush=True)

    # Mutex resolve: wrk30 is authoritative (asserted byte-identical below) — a person
    # cannot be home while at work. apply_min_dwell smooths hom30 with no knowledge of
    # wrk30 and can re-raise hom30 on a wrk30==1 weekend slot; clear those conflicts here.
    hom_we2 = out.loc[we_mask, HOM].values
    wrk_we2 = out.loc[we_mask, WRK].values
    conflict_we = (hom_we2 == 1) & (wrk_we2 == 1)
    n_mx = int(conflict_we.sum())
    if n_mx:
        hom_we2[conflict_we] = 0
        out.loc[we_mask, HOM] = hom_we2
    print(f"    Mutex resolve: {n_mx:,} weekend hom30=1 & wrk30=1 conflicts cleared (hom30->0)", flush=True)

    # ── Stage 1 integrity checks ──────────────────────────────────────────────
    assert (out[WRK].values == wrk_orig).all(), "INTEGRITY FAIL: wrk30 modified in Stage 1!"
    print("  [OK] wrk30 untouched (Stage 1 integrity verified)", flush=True)

    n_conflict_all = int(((out[HOM].values == 1) & (out[WRK].values == 1)).sum())
    assert n_conflict_all == 0, f"INTEGRITY FAIL: {n_conflict_all} hom30&wrk30 mutex conflicts remain!"
    print("  [OK] Mutual exclusion enforced (0 hom30 & wrk30 conflicts)", flush=True)

    wd_hom_after1 = out.loc[wd_mask_orig, HOM].values
    assert (wd_hom_after1 == hom_wd_orig).all(), "INTEGRITY FAIL: weekday hom30 modified in Stage 1!"
    print("  [OK] Weekday hom30 untouched (Stage 1 integrity verified)", flush=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 2: Activity restore (act30, all strata, conditional on state)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[STAGE 2] Activity restore (act30, ALL strata, conditional on state)", flush=True)
    print("  State: WORK if wrk30=1; HOME if hom30=1 (and wrk30=0); else OUT.", flush=True)
    print("  Pool source: observed 2022 act30 per (slot x state) cell.", flush=True)
    print("  Vectorized: one rng.choice per (slot x state) cell.", flush=True)

    # Extract 2022 arrays
    obs_hom = obs22[HOM].values.astype(float)  # (N22, 48)
    obs_wrk = obs22[WRK].values.astype(float)  # (N22, 48)
    obs_act = obs22[ACT].values.astype(float)  # (N22, 48)

    # Pre-compute per-state fallback pools (all-slot concatenation per state)
    print("  Building 2022 fallback pools (all-slot per state) ...", flush=True)
    fallback: dict[int, np.ndarray] = {STATE_OUT: [], STATE_HOME: [], STATE_WORK: []}
    for s in range(N_SLOTS):
        wk_s = obs_wrk[:, s]
        hm_s = obs_hom[:, s]
        ak_s = obs_act[:, s]
        st_s = np.where(wk_s == 1, STATE_WORK, np.where(hm_s == 1, STATE_HOME, STATE_OUT))
        for st in (STATE_OUT, STATE_HOME, STATE_WORK):
            vals = ak_s[st_s == st]
            vals = vals[~np.isnan(vals) & (vals >= 0)]
            if len(vals) > 0:
                fallback[st].append(vals)

    state_names = {STATE_OUT: "OUT", STATE_HOME: "HOME", STATE_WORK: "WORK"}
    for st in (STATE_OUT, STATE_HOME, STATE_WORK):
        if fallback[st]:
            fallback[st] = np.concatenate(fallback[st]).astype(float)
        else:
            fallback[st] = np.array([5.0])  # sleep as last resort
        print(f"    Fallback pool [{state_names[st]}]: {len(fallback[st]):,} samples", flush=True)

    # Current out arrays (post Stage 1)
    out_hom = out[HOM].values.astype(float)  # (N_2030, 48)
    out_wrk = out[WRK].values.astype(float)  # (N_2030, 48)
    out_act = out[ACT].values.astype(float)  # (N_2030, 48)

    total_cells    = 0
    total_fallback = 0
    total_assigned = 0

    for s in range(N_SLOTS):
        # 2022 pool for this slot: act30 values grouped by state
        obs_wk_s = obs_wrk[:, s]
        obs_hm_s = obs_hom[:, s]
        obs_ak_s = obs_act[:, s]
        obs_st_s = np.where(obs_wk_s == 1, STATE_WORK,
                            np.where(obs_hm_s == 1, STATE_HOME, STATE_OUT))

        # 2030 state for this slot (post Stage 1)
        out_wk_s = out_wrk[:, s]
        out_hm_s = out_hom[:, s]
        out_st_s = np.where(out_wk_s == 1, STATE_WORK,
                            np.where(out_hm_s == 1, STATE_HOME, STATE_OUT))

        for st in (STATE_OUT, STATE_HOME, STATE_WORK):
            # Observed 2022 pool for (slot=s, state=st)
            pool = obs_ak_s[obs_st_s == st]
            pool = pool[~np.isnan(pool) & (pool >= 0)]
            used_fallback = False
            if len(pool) < SMALL_CELL:
                pool = fallback[st]
                used_fallback = True
                total_fallback += 1

            # 2030 row indices in this state at slot s
            idx_2030 = np.where(out_st_s == st)[0]
            if len(idx_2030) == 0:
                continue

            # Vectorized draw: one call per cell
            draws = rng.choice(pool, size=len(idx_2030), replace=True)
            out_act[idx_2030, s] = draws.astype(float)

            total_cells    += 1
            total_assigned += len(idx_2030)

    out[ACT] = out_act

    print(f"  Cells processed: {total_cells}  (of {N_SLOTS * 3} = 48x3 possible)", flush=True)
    print(f"  Cells using fallback pool: {total_fallback}", flush=True)
    print(f"  Total person-slots reassigned: {total_assigned:,}", flush=True)

    # ── Stage 2 integrity check ───────────────────────────────────────────────
    assert (out[WRK].values == wrk_orig).all(), "INTEGRITY FAIL: wrk30 modified in Stage 2!"
    print("  [OK] wrk30 untouched (Stage 2 integrity verified)", flush=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Verification diagnostics (post-calibration)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[VERIFY] Post-calibration diagnostics:", flush=True)

    # Check 1: Sleep share
    act_after = out[ACT].values.astype(float)
    sleep_after = float((act_after == 5).mean())
    sleep_flag = "PASS" if 0.33 <= sleep_after <= 0.36 else "WARN"
    print(f"  [1] Sleep (code 5) share: {sleep_before:.4f} -> {sleep_after:.4f} "
          f"(target ~0.34-0.35)  [{sleep_flag}]", flush=True)

    # Check 2 proxy: WD mean Metabolic per band from act30
    met_after = met_proxy(out)
    for band in BANDS:
        flag = "PASS" if 108 <= met_after[band] <= 112 else "WARN"
        print(f"  [2] WD mean Metabolic proxy [{band}]: "
              f"{met_before[band]:.1f} -> {met_after[band]:.1f} W  "
              f"(target ~108-112 W)  [{flag}]", flush=True)

    # Check 3: Weekend daytime home occupancy
    we_mask_out = out["DDAY_STRATA"].isin(WEEKEND_STRATA)
    we_day_after = float(out.loc[we_mask_out, DAYTIME_HOM].values.mean())
    we_flag = "PASS" if 0.52 <= we_day_after <= 0.57 else "WARN"
    print(f"  [3] WE daytime (slots 11-26) hom30: {we_day_before:.4f} -> {we_day_after:.4f} "
          f"(target ~0.52-0.56)  [{we_flag}]", flush=True)

    # Per-stratum detail
    for stratum in WEEKEND_STRATA:
        st_mask = out["DDAY_STRATA"] == stratum
        val = float(out.loc[st_mask, DAYTIME_HOM].values.mean())
        obs_val = float(obs22.loc[obs22["DDAY_STRATA"] == stratum, DAYTIME_HOM].values.mean())
        lbl = "Sat" if stratum == 2 else "Sun"
        print(f"    Stratum {stratum} ({lbl}): after={val:.4f}  2022_obs={obs_val:.4f}", flush=True)

    # Check 4: WFH weekday gain preserved
    wd_mask_out = out["DDAY_STRATA"] == 1
    print(f"  [4] WD daytime hom30 by band (should be conservative < hybrid < fullyhybrid):", flush=True)
    wd_day_after: dict[str, float] = {}
    for band in BANDS:
        before = wd_day_before[band]
        after  = float(out.loc[wd_mask_out & (out["BAND"] == band), DAYTIME_HOM].values.mean())
        wd_day_after[band] = after
        delta  = after - before
        print(f"    {band}: before={before:.4f}  after={after:.4f}  delta={delta:+.4f}", flush=True)
    wfh_ok = (wd_day_after["conservative"] < wd_day_after["hybrid"] < wd_day_after["fullyhybrid"])
    print(f"    Ordering conservative < hybrid < fullyhybrid: {'PASS' if wfh_ok else 'FAIL'}",
          flush=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Atomic write
    # ─────────────────────────────────────────────────────────────────────────
    print(f"\n[WRITE] {OUT_C.name}", flush=True)
    atomic_write(out, OUT_C)

    print("\n" + "=" * 70, flush=True)
    print("CALIBRATION-C COMPLETE", flush=True)
    print(f"  Output: {OUT_C}", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    main()
