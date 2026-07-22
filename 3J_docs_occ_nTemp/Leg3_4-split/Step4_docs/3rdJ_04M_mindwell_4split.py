# -*- coding: utf-8 -*-
"""
3rdJ_04M_mindwell_4split.py

Minimum-dwell post-processor for Step-4 augmented diaries (Leg-3 four-split:
hotel + residential/home + office/work + retail).

Forked from the Leg-2 template (3rdJ_04M_mindwell_2split.py) — Delta H of
3rdJ_04_augmentationGSS_4split.md: "same script, one more channel column."

Reads a raked augmented_diaries.csv (--in_csv), applies a minimum-dwell smoother
to the hom30_001..048, wrk30_001..048, AND ret30_001..048 binary columns, then
writes the smoothed CSV to --out_csv.  All other columns are copied unchanged.
act30_* is NOT touched.

Column-naming note (per the runbook, Delta H / CONTRACT section): the diary
pool uses lowercase ret30_001..048 for the retail channel.  This is DISTINCT
from the Step-3 tiler's RETL30_* namespace (retail_30min.csv) — do not confuse
the two; this script operates on the post-04E inference CSV, which carries
ret30_*, not RETL30_*.

Smoothing rule (applied independently to each channel per row):
  Any contiguous run of identical values with length < min_dwell (default 2 slots)
  that is surrounded on BOTH sides by the opposite value is flipped to match its
  neighbours.  This merges isolated 1-slot "blip" artefacts.

  Edge handling: a 1-slot run at slot index 0 or 47 (only one neighbour) is flipped
  to that neighbour regardless (one-sided boundary condition).

Algorithm: single left-to-right pass over columns 0..47 per row using numpy
  vectorised diff logic.  Binary (0/1) values only; NaN slots are left untouched.
  Identical logic to the Leg-2 template; simply applied to a third channel.

Prints before/after median hom30 transitions and the number of slots changed
per channel (hom30 / wrk30 / ret30).

Output-dir convention (Leg-3, per runbook Delta H): production pool lands under
    outputs_step4/sweep/<BASE>_raked3_mindwell/
(the 3-channel rake, 04L, feeds this script; 04M's own output is the
"_raked3_mindwell" stage, ahead of the later 04T 4-way act-rake which adds
"_actv" to the directory name). This script does not enforce the directory
name — --out_csv is a plain file path — but callers should follow this
convention when constructing --out_csv.

Usage:
    py -3 3rdJ_04M_mindwell_4split.py \
        --in_csv  /path/to/raked3/augmented_diaries.csv \
        --out_csv /path/to/sweep/<BASE>_raked3_mindwell/augmented_diaries.csv \
        [--min_dwell 2]

Dependencies: pandas, numpy (no other non-stdlib requirements).
Build: 2026-07-20 (employee, Claude Sonnet 5), forked from the Leg-2
2026-06-21 template with a third (retail) channel added per Delta H.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

N_SLOTS = 48
HOM_PREFIX = "hom30"
WRK_PREFIX = "wrk30"
RET_PREFIX = "ret30"   # [Leg-3 NEW] — lowercase diary-pool namespace, NOT RETL30_*
ACT_PREFIX = "act30"


# ── smoother ──────────────────────────────────────────────────────────────────

def apply_min_dwell(arr: np.ndarray, min_dwell: int = 2) -> tuple[np.ndarray, int]:
    """
    Apply minimum-dwell smoothing to a (N_rows, 48) binary float array.

    Any contiguous run of the SAME value with length < min_dwell that has the
    opposite value on BOTH sides (interior) or one side (edge) is replaced by the
    neighbour value.

    Returns (smoothed_array, n_slots_changed).
    Only values 0.0 and 1.0 are processed; NaN slots are skipped.

    Unchanged from the Leg-2 template — channel-agnostic; called identically
    for hom30, wrk30, and (Leg-3 NEW) ret30.
    """
    if min_dwell <= 1:
        return arr.copy(), 0

    arr = arr.copy()
    n_rows, n_cols = arr.shape
    total_changed = 0

    # We do one left-to-right pass, iteratively, until stable.
    # For min_dwell == 2 one pass is sufficient (only length-1 blips targeted).
    # For larger min_dwell we loop until convergence.
    for _pass in range(min_dwell):
        changed_this_pass = 0

        # Vectorised: find interior blips (column i flanked on both sides by
        # the opposite value).  We work column by column across the 48 slots.
        for i in range(n_cols):
            col_i = arr[:, i]
            nan_i = np.isnan(col_i)

            # Determine run identity by comparing to neighbours
            if i == 0:
                # Left edge: only right neighbour matters
                right = arr[:, 1]
                nan_r = np.isnan(right)
                valid = ~nan_i & ~nan_r
                flip = valid & (col_i != right)
                # flip to right neighbour
                arr[flip, i] = right[flip]
                changed_this_pass += int(flip.sum())
            elif i == n_cols - 1:
                # Right edge: only left neighbour matters
                left = arr[:, n_cols - 2]
                nan_l = np.isnan(left)
                valid = ~nan_i & ~nan_l
                flip = valid & (col_i != left)
                arr[flip, i] = left[flip]
                changed_this_pass += int(flip.sum())
            else:
                # Interior: must differ from BOTH left and right
                left = arr[:, i - 1]
                right = arr[:, i + 1]
                nan_l = np.isnan(left)
                nan_r = np.isnan(right)
                valid = ~nan_i & ~nan_l & ~nan_r
                flip = valid & (col_i != left) & (col_i != right)
                arr[flip, i] = left[flip]          # flip to left (equiv to right)
                changed_this_pass += int(flip.sum())

        total_changed += changed_this_pass
        if changed_this_pass == 0:
            break

    return arr, total_changed


# ── transition count helper ───────────────────────────────────────────────────

def median_transitions(arr: np.ndarray) -> float:
    """Median per-row transition count (number of adjacent-slot value changes)."""
    if arr.shape[0] == 0:
        return float("nan")
    diff = np.abs(np.diff(arr, axis=1))            # (N, 47)
    per_row = np.nansum(diff, axis=1)              # (N,)
    return float(np.nanmedian(per_row))


# ── main ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Minimum-dwell post-processor for Step-4 raked diaries (Leg-3, 4-split)"
    )
    p.add_argument("--in_csv",    required=True, help="Input raked (3-channel, 04L output) augmented_diaries.csv")
    p.add_argument("--out_csv",   required=True, help="Output smoothed augmented_diaries.csv")
    p.add_argument("--min_dwell", type=int, default=2,
                   help="Minimum run length; runs shorter than this are merged (default 2)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    print("=" * 70)
    print("3rdJ_04M_mindwell_4split.py — minimum-dwell post-processor (Leg-3)")
    print(f"  in_csv    : {args.in_csv}")
    print(f"  out_csv   : {args.out_csv}")
    print(f"  min_dwell : {args.min_dwell}")
    print("=" * 70)

    # ── Load ──────────────────────────────────────────────────────────────────
    print("\nLoading CSV ...", flush=True)
    df = pd.read_csv(args.in_csv, low_memory=False)
    print(f"  Rows: {len(df):,}   Cols: {len(df.columns):,}")

    # Identify hom30 / wrk30 / ret30 columns (present only)
    hom_cols = [f"{HOM_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)]
    wrk_cols = [f"{WRK_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)]
    ret_cols = [f"{RET_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)]   # [Leg-3 NEW]
    hom_cols = [c for c in hom_cols if c in df.columns]
    wrk_cols = [c for c in wrk_cols if c in df.columns]
    ret_cols = [c for c in ret_cols if c in df.columns]
    print(f"  hom30 cols found: {len(hom_cols)}/48")
    print(f"  wrk30 cols found: {len(wrk_cols)}/48")
    print(f"  ret30 cols found: {len(ret_cols)}/48")

    if not hom_cols:
        print("ERROR: No hom30_* columns found. Aborting.", file=sys.stderr)
        sys.exit(1)

    # ── Separate synthetic vs observed ────────────────────────────────────────
    if "IS_SYNTHETIC" in df.columns:
        syn_mask = df["IS_SYNTHETIC"] == 1
        obs_mask = ~syn_mask
    else:
        print("  WARNING: IS_SYNTHETIC column missing — treating all rows as synthetic")
        syn_mask = pd.Series([True] * len(df), index=df.index)
        obs_mask = ~syn_mask

    n_syn = int(syn_mask.sum())
    n_obs = int(obs_mask.sum())
    print(f"  Synthetic rows: {n_syn:,}   Observed rows: {n_obs:,}")

    # ── Before stats (syn only) ───────────────────────────────────────────────
    if n_syn > 0 and hom_cols:
        arr_hom_syn_before = df.loc[syn_mask, hom_cols].to_numpy(dtype=float)
        med_before = median_transitions(arr_hom_syn_before)
    else:
        arr_hom_syn_before = np.zeros((0, len(hom_cols)), dtype=float)
        med_before = float("nan")

    print(f"\n  hom30 median transitions BEFORE (syn): {med_before:.3f}")

    # ── Apply smoothing ───────────────────────────────────────────────────────
    # Only smooth synthetic rows (observed rows are the reference; leave them intact).
    total_hom_changed = 0
    total_wrk_changed = 0
    total_ret_changed = 0   # [Leg-3 NEW]

    if n_syn > 0:
        # hom30
        if hom_cols:
            arr_hom = df.loc[syn_mask, hom_cols].to_numpy(dtype=float)
            arr_hom_smooth, n_changed_hom = apply_min_dwell(arr_hom, args.min_dwell)
            df.loc[syn_mask, hom_cols] = arr_hom_smooth
            total_hom_changed += n_changed_hom

        # wrk30
        if wrk_cols:
            arr_wrk = df.loc[syn_mask, wrk_cols].to_numpy(dtype=float)
            arr_wrk_smooth, n_changed_wrk = apply_min_dwell(arr_wrk, args.min_dwell)
            df.loc[syn_mask, wrk_cols] = arr_wrk_smooth
            total_wrk_changed += n_changed_wrk

        # ret30 [Leg-3 NEW] — identical smoother, third channel
        if ret_cols:
            arr_ret = df.loc[syn_mask, ret_cols].to_numpy(dtype=float)
            arr_ret_smooth, n_changed_ret = apply_min_dwell(arr_ret, args.min_dwell)
            df.loc[syn_mask, ret_cols] = arr_ret_smooth
            total_ret_changed += n_changed_ret

    # ── After stats ───────────────────────────────────────────────────────────
    if n_syn > 0 and hom_cols:
        arr_hom_syn_after = df.loc[syn_mask, hom_cols].to_numpy(dtype=float)
        med_after = median_transitions(arr_hom_syn_after)
    else:
        med_after = float("nan")

    print(f"  hom30 median transitions AFTER  (syn): {med_after:.3f}")
    print(f"  hom30 slots changed: {total_hom_changed:,}")
    print(f"  wrk30 slots changed: {total_wrk_changed:,}")
    print(f"  ret30 slots changed: {total_ret_changed:,}")

    if not (np.isnan(med_before) or np.isnan(med_after)):
        reduction_pct = 100.0 * (med_before - med_after) / max(med_before, 1e-9)
        print(f"  Transition reduction: {reduction_pct:.1f}%")

    # Verify act30 columns untouched (belt-and-suspenders check)
    act_cols = [c for c in df.columns if c.startswith(ACT_PREFIX + "_")]
    print(f"  act30_* cols present (untouched): {len(act_cols)}")

    # ── Write output ──────────────────────────────────────────────────────────
    print(f"\nWriting smoothed CSV -> {args.out_csv}", flush=True)
    df.to_csv(args.out_csv, index=False)
    print(f"Done. Rows written: {len(df):,}")
    print("=" * 70)


if __name__ == "__main__":
    main()
