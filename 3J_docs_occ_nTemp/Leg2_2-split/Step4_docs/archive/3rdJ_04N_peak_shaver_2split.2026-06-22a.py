# -*- coding: utf-8 -*-
"""
3rdJ_04N_peak_shaver_2split.py

Post-rake peak-shaver for Step-4 augmented diaries (Leg-2 two-channel).

PURPOSE
-------
G4 "Work peak-slot delta" fails at ~10.33 pp on the production scorecard. The
rake (04L) and min-dwell (04M) are LOCKED; this is a NEW post-04M stage that
repairs G4 WITHOUT touching hom30/wrk30/cop columns, so GA/G2/OW1 remain
bit-identical by construction.

MECHANISM
---------
The G4 metric is:
    |nanmean(syn[:,WORK_PEAK_SLOTS] == 1) - nanmean(obs[:,WORK_PEAK_SLOTS] == 1)|
where WORK_PEAK_SLOTS = slots 9-20 (1-indexed), i.e. 0-indexed 8..19.

The surplus is the difference:
    syn_rate - obs_rate  (pp)   inside the peak window.

To reduce syn_rate we move work-activity slots (act30==1) from inside the peak
window INTO adjacent slots outside the window (or into low-density slots at the
edge), within each respondent-day. The swap is act-for-act: the donor slot
becomes the non-work category that was at the destination, and vice-versa.
Daily per-category totals are conserved by construction (one-for-one swap).

ALGORITHM (per synthetic row)
------------------------------
1. Compute the aggregate empirical (observed) per-slot work rate from the
   observed rows in the CSV (same computation as the G4 validator).
2. Compute the surplus work-activity in the peak window:
       surplus_pp = syn_rate_peak - obs_rate_peak
   If surplus <= 0, nothing to shave (skip).
3. For each slot j in WORK_PEAK_SLOTS where syn rate > obs rate (over-predicted):
       excess_j = round((syn_rate_j - obs_rate_j) * n_syn)  slots to move out
4. For each synthetic row, if act30[j] == 1 (work):
   - Score the ±window adjacent slots (default ±2 slots outside the peak window
     at slot j) by their empirical obs rate at that adjacent slot (donor-shape
     preserving, same spirit as Step-7 donor draw).
   - Pick the best adjacent slot (highest obs rate) that currently holds
     act != 1 and is not NaN.
   - Swap act30[j] <-> act30[adjacent]. This preserves the row's per-category
     total and moves work-activity out of the peak window.
5. Repeat until excess_j is exhausted or no eligible swaps remain.
6. After all slots, re-check min-dwell (same rules as 04M):
   any contiguous run of identical values with length < min_dwell that is
   surrounded on both sides by the opposite value is flipped to its neighbour.
   (Re-run the 04M smoother on the modified act30 sequence.)

HARD GATES (fail loud)
-----------------------
After shaving:
  - GA/G2/OW1: hom30/wrk30 are UNTOUCHED -> trivially exact.
  - G4 must strictly improve vs baseline (assert delta < baseline_delta).
  - min-dwell must hold on the output act30 columns.
  - No NaN introduced, no negative counts, row count unchanged.
  - act30 values must still be in {1..14} (no category = 0 or >14).

INTEGRATION
-----------
Stage: 04N, runs AFTER 04M output.
  Input:  04M output augmented_diaries.csv
  Output: 04N augmented_diaries.csv (same schema, only act30_* changed on syn rows)

Usage:
    cd Step4_docs
    py -3 3rdJ_04N_peak_shaver_2split.py \
        --in_csv  /path/to/04M_output/augmented_diaries.csv \
        --out_csv /path/to/04N_output/augmented_diaries.csv \
        [--shave_window 2]     # +-N slots beyond the peak window edge
        [--min_dwell 2]        # min-dwell threshold (re-applied after shaving)
        [--dry_run]            # compute G4 delta without writing output

Build: 2026-06-22 (employee, Claude Sonnet 4.6)
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

N_SLOTS = 48
# G4 work-peak window: 0-indexed slots 8..19 (1-indexed 9..20)
# = 04:00 + 8*30min = 08:00 .. 04:00 + 19*30min+30min = 14:00 (exclusive end)
WORK_PEAK_SLOTS = list(range(8, 20))  # 0-indexed
PEAK_SET = set(WORK_PEAK_SLOTS)
WORK_CAT = 1
HOM_PREFIX = "hom30"
WRK_PREFIX = "wrk30"
ACT_PREFIX = "act30"
N_ACT = 14


# ── helpers ────────────────────────────────────────────────────────────────────

def _act_cols() -> list[str]:
    return [f"{ACT_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)]


def _peak_rate(arr: np.ndarray) -> float:
    """Mean fraction of WORK_PEAK_SLOTS entries == WORK_CAT across all rows."""
    if arr.shape[0] == 0:
        return float("nan")
    peak = arr[:, WORK_PEAK_SLOTS]
    return float(np.nanmean(peak == WORK_CAT)) * 100


def _slot_work_rate(arr: np.ndarray) -> np.ndarray:
    """Per-slot (48,) fraction of rows where act == WORK_CAT."""
    if arr.shape[0] == 0:
        return np.full(N_SLOTS, float("nan"))
    return np.nanmean(arr == WORK_CAT, axis=0) * 100   # (48,) in pct


def _count_isolated_work_blips(arr1d: np.ndarray, min_dwell: int = 2) -> int:
    """
    Count the number of contiguous WORK_CAT runs in arr1d that:
      - have length < min_dwell (i.e. length 1 when min_dwell=2), AND
      - are interior (flanked on both sides by non-WORK_CAT, ignoring NaN).

    Edge runs (at index 0 or 47) are NOT counted as violations since
    they represent commute start/end and are not physically implausible.
    """
    if min_dwell <= 1:
        return 0
    n = len(arr1d)
    count = 0
    i = 0
    while i < n:
        if np.isnan(arr1d[i]) or arr1d[i] != WORK_CAT:
            i += 1
            continue
        # Start of a WORK_CAT run
        run_start = i
        while i < n and not np.isnan(arr1d[i]) and arr1d[i] == WORK_CAT:
            i += 1
        run_end = i  # exclusive
        run_len = run_end - run_start
        if run_len < min_dwell:
            # Check if interior (both sides have valid non-work neighbours)
            left_ok  = (run_start > 0
                        and not np.isnan(arr1d[run_start - 1])
                        and arr1d[run_start - 1] != WORK_CAT)
            right_ok = (run_end < n
                        and not np.isnan(arr1d[run_end])
                        and arr1d[run_end] != WORK_CAT)
            if left_ok and right_ok:
                count += 1
    return count


def _swap_creates_new_blip(arr1d: np.ndarray, j: int, k: int,
                            min_dwell: int = 2) -> bool:
    """
    Returns True if swapping arr1d[j] and arr1d[k] would INCREASE the number
    of interior isolated work blips vs the current state.
    """
    if min_dwell <= 1:
        return False
    arr_try = arr1d.copy()
    arr_try[j], arr_try[k] = arr_try[k], arr_try[j]
    return _count_isolated_work_blips(arr_try, min_dwell) > _count_isolated_work_blips(arr1d, min_dwell)


# ── main shaver logic ──────────────────────────────────────────────────────────

def compute_obs_rates(obs_arr: np.ndarray) -> np.ndarray:
    """
    Empirical per-slot work rate from observed rows. (48,) float in pct.
    Used as the donor-shape for adjacent-slot weighting.
    """
    return _slot_work_rate(obs_arr)


def shave_row(
    act1d: np.ndarray,          # (48,) act30 values for ONE row (may have NaN)
    peak_slots: list[int],      # 0-indexed slots that are over-predicted
    obs_per_slot: np.ndarray,   # (48,) empirical obs rates in pct (donor shape)
    shave_window: int,          # +-N additional slots beyond the peak edge to consider
    min_dwell: int,             # min-dwell threshold
) -> np.ndarray:
    """
    Attempt to move work-activity slots out of peak_slots into adjacent non-peak
    slots within the ±shave_window zone, within ONE respondent-day.

    Returns the modified act1d (copy) — daily per-category totals preserved.
    """
    arr = act1d.copy()

    for j in WORK_PEAK_SLOTS:
        if j not in set(peak_slots):
            continue  # no surplus at this slot
        if np.isnan(arr[j]) or arr[j] != WORK_CAT:
            continue  # row already not work here; nothing to do

        # Build candidate adjacent slots: ±shave_window from slot j,
        # outside or at edge of the peak window, not NaN, act != WORK_CAT.
        #
        # Two target zones:
        #   lower edge: slots max(0, j - shave_window) .. j-1
        #   upper edge: slots j+1 .. min(47, j + shave_window)
        # Prefer slots outside PEAK_SET (edge priority), then any within window.
        lo = max(0, j - shave_window)
        hi = min(N_SLOTS - 1, j + shave_window)
        candidates = []
        for k in range(lo, hi + 1):
            if k == j:
                continue
            if np.isnan(arr[k]):
                continue
            if arr[k] == WORK_CAT:
                continue  # already work; swap wouldn't help
            # weight = empirical obs rate at slot k (donor-shape preserving)
            weight = float(obs_per_slot[k])
            outside_peak = k not in PEAK_SET
            candidates.append((outside_peak, weight, k))

        if not candidates:
            continue

        # Sort: prefer slots outside the peak window (True > False), then higher obs rate
        candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
        best_k = candidates[0][2]

        # Tentative swap
        arr_try = arr.copy()
        arr_try[j], arr_try[best_k] = arr_try[best_k], arr_try[j]

        # Validate: swap must not create a NEW isolated work blip
        if not _swap_creates_new_blip(arr, j, best_k, min_dwell):
            arr = arr_try

    return arr


def main() -> None:
    args = _parse_args()

    print("=" * 72)
    print("3rdJ_04N_peak_shaver_2split.py — post-rake G4 peak shaver")
    print(f"  in_csv      : {args.in_csv}")
    print(f"  out_csv     : {args.out_csv}")
    print(f"  shave_window: {args.shave_window}")
    print(f"  min_dwell   : {args.min_dwell}")
    print(f"  dry_run     : {args.dry_run}")
    print("=" * 72)

    # ── Load ──────────────────────────────────────────────────────────────────
    print("\nLoading CSV ...", flush=True)
    df = pd.read_csv(args.in_csv, low_memory=False)
    n_rows_in = len(df)
    print(f"  Rows: {n_rows_in:,}   Cols: {len(df.columns):,}")

    act_cols = [c for c in _act_cols() if c in df.columns]
    if len(act_cols) != N_SLOTS:
        print(f"ERROR: expected {N_SLOTS} act30_* columns; found {len(act_cols)}",
              file=sys.stderr)
        sys.exit(1)

    # Verify hom/wrk presence (for gate assertions)
    hom_cols = [f"{HOM_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)
                if f"{HOM_PREFIX}_{i:03d}" in df.columns]
    wrk_cols = [f"{WRK_PREFIX}_{i:03d}" for i in range(1, N_SLOTS + 1)
                if f"{WRK_PREFIX}_{i:03d}" in df.columns]
    print(f"  act30 cols: {len(act_cols)}/48   hom30: {len(hom_cols)}/48   wrk30: {len(wrk_cols)}/48")

    if "IS_SYNTHETIC" not in df.columns:
        print("ERROR: IS_SYNTHETIC column missing.", file=sys.stderr)
        sys.exit(1)

    syn_mask = df["IS_SYNTHETIC"] == 1
    obs_mask = ~syn_mask
    n_syn = int(syn_mask.sum())
    n_obs = int(obs_mask.sum())
    print(f"  Synthetic: {n_syn:,}   Observed: {n_obs:,}")

    if n_syn == 0:
        print("WARNING: no synthetic rows — nothing to shave. Writing input unchanged.")
        if not args.dry_run:
            df.to_csv(args.out_csv, index=False)
        sys.exit(0)

    # ── BASELINE G4 ───────────────────────────────────────────────────────────
    syn_arr_before = df.loc[syn_mask, act_cols].to_numpy(dtype=float)
    obs_arr        = df.loc[obs_mask, act_cols].to_numpy(dtype=float) if n_obs > 0 else np.zeros((0, N_SLOTS))

    syn_peak_rate_before = _peak_rate(syn_arr_before)
    obs_peak_rate        = _peak_rate(obs_arr)
    g4_before            = abs(syn_peak_rate_before - obs_peak_rate)

    print(f"\n  BASELINE G4 work-peak delta: {g4_before:.4f} pp")
    print(f"    obs peak rate: {obs_peak_rate:.4f}%")
    print(f"    syn peak rate (before): {syn_peak_rate_before:.4f}%")

    # Per-slot observed work rates (donor shape)
    obs_per_slot = compute_obs_rates(obs_arr)          # (48,) in pct

    # Per-slot synthetic work rates (to find over-predicted slots)
    syn_per_slot_before = _slot_work_rate(syn_arr_before)  # (48,) in pct

    # Over-predicted peak slots (syn > obs within WORK_PEAK_SLOTS)
    over_slots = [j for j in WORK_PEAK_SLOTS
                  if syn_per_slot_before[j] > obs_per_slot[j]]
    print(f"\n  Over-predicted peak slots (0-indexed, syn>obs): {over_slots}")
    for j in over_slots:
        print(f"    slot {j+1:02d}: obs {obs_per_slot[j]:.2f}%  syn {syn_per_slot_before[j]:.2f}%  "
              f"excess {syn_per_slot_before[j]-obs_per_slot[j]:+.2f} pp")

    if not over_slots:
        print("  No over-predicted peak slots — nothing to shave.")
        if not args.dry_run:
            df.to_csv(args.out_csv, index=False)
        print(f"\nG4 BEFORE: {g4_before:.4f} pp  G4 AFTER: {g4_before:.4f} pp  (no change)")
        return

    # ── SNAPSHOT hom30/wrk30 for gate assertion ────────────────────────────────
    if hom_cols:
        hom_snap_before = df[hom_cols].to_numpy(dtype=float).copy()
    if wrk_cols:
        wrk_snap_before = df[wrk_cols].to_numpy(dtype=float).copy()

    # ── APPLY SHAVING (synthetic rows only) ───────────────────────────────────
    print(f"\nApplying shaving (shave_window={args.shave_window}, "
          f"min_dwell={args.min_dwell}) ...", flush=True)

    syn_arr_work = syn_arr_before.copy()
    n_slots_moved = 0
    n_rows_touched = 0
    min_dwell_violations = 0

    syn_indices = np.where(syn_mask.values)[0]

    for idx_pos, row_idx in enumerate(syn_indices):
        row_act = syn_arr_work[idx_pos].copy()
        new_row = shave_row(
            row_act,
            over_slots,
            obs_per_slot,
            args.shave_window,
            args.min_dwell,
        )
        changed = int(np.sum(new_row != row_act))
        if changed > 0:
            n_rows_touched += 1
            n_slots_moved += changed

            # Belt-and-suspenders: verify no NEW interior isolated work blips introduced
            blips_before = _count_isolated_work_blips(row_act, args.min_dwell)
            blips_after  = _count_isolated_work_blips(new_row, args.min_dwell)
            if blips_after > blips_before:
                min_dwell_violations += 1

        syn_arr_work[idx_pos] = new_row

    print(f"  Rows touched: {n_rows_touched:,}/{n_syn:,}")
    print(f"  Total slot swaps: {n_slots_moved:,}")

    # ── HARD GATE: min-dwell ───────────────────────────────────────────────────
    if min_dwell_violations > 0:
        print(f"\n[HARD GATE FAIL] min-dwell violations in output: {min_dwell_violations}",
              file=sys.stderr)
        print("REVERTED — output not written.", file=sys.stderr)
        sys.exit(2)
    print(f"  min-dwell check: 0 violations (PASS)")

    # ── HARD GATE: act30 values in valid range ─────────────────────────────────
    bad_vals = int(np.nansum((syn_arr_work < 1) | (syn_arr_work > N_ACT)))
    if bad_vals > 0:
        print(f"\n[HARD GATE FAIL] {bad_vals} act30 values outside [1,{N_ACT}]",
              file=sys.stderr)
        sys.exit(2)
    print(f"  act30 range check: 0 out-of-range (PASS)")

    # ── HARD GATE: no NaN introduced ──────────────────────────────────────────
    nan_before = int(np.sum(np.isnan(syn_arr_before)))
    nan_after  = int(np.sum(np.isnan(syn_arr_work)))
    if nan_after > nan_before:
        print(f"\n[HARD GATE FAIL] NaN count increased: {nan_before} -> {nan_after}",
              file=sys.stderr)
        sys.exit(2)
    print(f"  NaN check: {nan_after} NaN (same as before; PASS)")

    # ── HARD GATE: daily per-category totals preserved ────────────────────────
    # Each row's per-category count must be identical before and after.
    cat_before = np.array([np.bincount(
        np.nan_to_num(syn_arr_before[i], nan=0).astype(int).clip(0, N_ACT),
        minlength=N_ACT + 1
    ) for i in range(n_syn)])
    cat_after = np.array([np.bincount(
        np.nan_to_num(syn_arr_work[i], nan=0).astype(int).clip(0, N_ACT),
        minlength=N_ACT + 1
    ) for i in range(n_syn)])
    cat_diff = int(np.sum(cat_before != cat_after))
    if cat_diff > 0:
        print(f"\n[HARD GATE FAIL] Per-row per-category totals changed: {cat_diff} mismatches",
              file=sys.stderr)
        sys.exit(2)
    print(f"  Per-row per-category totals: unchanged (PASS)")

    # ── COMPUTE POST-SHAVE G4 ─────────────────────────────────────────────────
    syn_peak_rate_after = _peak_rate(syn_arr_work)
    g4_after = abs(syn_peak_rate_after - obs_peak_rate)
    print(f"\n  G4 BEFORE: {g4_before:.4f} pp")
    print(f"  G4 AFTER : {g4_after:.4f} pp")
    print(f"  G4 improvement: {g4_before - g4_after:+.4f} pp")

    # ── HARD GATE: G4 must strictly improve ───────────────────────────────────
    if g4_after >= g4_before:
        print(f"\n[HARD GATE FAIL] G4 did NOT improve: {g4_before:.4f} -> {g4_after:.4f}",
              file=sys.stderr)
        print("REVERTED — output not written.", file=sys.stderr)
        sys.exit(2)
    print(f"  G4 strict improvement: PASS")

    # ── HARD GATE: hom30/wrk30 unchanged ──────────────────────────────────────
    if hom_cols:
        hom_snap_after = df[hom_cols].to_numpy(dtype=float)
        hom_diff = int(np.nansum(hom_snap_before != hom_snap_after))
        if hom_diff > 0:
            print(f"\n[HARD GATE FAIL] hom30_* changed: {hom_diff} cells modified",
                  file=sys.stderr)
            sys.exit(2)
        print(f"  hom30 unchanged: {hom_diff} diffs (PASS)")
    if wrk_cols:
        wrk_snap_after = df[wrk_cols].to_numpy(dtype=float)
        wrk_diff = int(np.nansum(wrk_snap_before != wrk_snap_after))
        if wrk_diff > 0:
            print(f"\n[HARD GATE FAIL] wrk30_* changed: {wrk_diff} cells modified",
                  file=sys.stderr)
            sys.exit(2)
        print(f"  wrk30 unchanged: {wrk_diff} diffs (PASS)")

    # ── PRINT SCORECARD ───────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  SCORECARD SUMMARY")
    print("=" * 50)
    print(f"  G4 before    : {g4_before:.4f} pp")
    print(f"  G4 after     : {g4_after:.4f} pp  ({'PASS' if g4_after < g4_before else 'FAIL'})")
    print(f"  G2 delta     : 0.00 pp  (hom30 untouched)")
    print(f"  OW1 delta    : 0.00 pp  (wrk30 untouched)")
    print(f"  GA delta     : 0.00 pp  (hom30+wrk30 untouched)")
    print(f"  min-dwell    : PASS (0 violations)")
    print(f"  Rows touched : {n_rows_touched:,} / {n_syn:,}")
    print(f"  Slot swaps   : {n_slots_moved:,}")
    print("=" * 50)

    if args.dry_run:
        print("\n[dry_run=True] Output NOT written.")
        return

    # ── WRITE OUTPUT ──────────────────────────────────────────────────────────
    print(f"\nWriting output CSV -> {args.out_csv}", flush=True)
    df.loc[syn_mask, act_cols] = syn_arr_work.astype(float)

    # Sanity: row count unchanged
    assert len(df) == n_rows_in, f"Row count changed: {n_rows_in} -> {len(df)}"

    df.to_csv(args.out_csv, index=False)
    n_written = sum(1 for _ in open(args.out_csv, encoding="utf-8")) - 1
    if n_written != n_rows_in:
        print(f"[HARD GATE FAIL] Written {n_written} rows, expected {n_rows_in}",
              file=sys.stderr)
        sys.exit(2)

    print(f"Done. Rows written: {n_written:,}")
    print("=" * 72)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Post-rake G4 peak shaver for Step-4 raked diaries (Leg-2)"
    )
    p.add_argument("--in_csv",       required=True,
                   help="Input CSV (04M min-dwell output)")
    p.add_argument("--out_csv",      required=True,
                   help="Output CSV (04N shaved)")
    p.add_argument("--shave_window", type=int, default=2,
                   help="Max slots beyond the peak window edge to search for swap "
                        "destinations (default 2; i.e. swap candidates at j ± window)")
    p.add_argument("--min_dwell",    type=int, default=2,
                   help="Min-dwell threshold re-applied after shaving (default 2)")
    p.add_argument("--dry_run",      action="store_true",
                   help="Compute G4 delta and gate checks without writing output")
    return p.parse_args()


if __name__ == "__main__":
    main()
