"""
05_postlink_rake.py — Phase 8B-5b: Post-Linkage AT_HOME (and Spouse30) Raking.

Rakes IS_SYNTHETIC==1 rows in 21CEN22GSS_aug_Full_Schedules.csv so that
per-(DDAY_STRATA × slot) synthetic hom30 rate equals the observed (IS_SYNTHETIC==0)
per-(DDAY_STRATA × slot) rate. Spouse30 raked only if check 6.3 fails (>3 pp diff).
Floor guard restores night hom30 for single-person synthetic HHs that drop below 0.30.

Algorithm:
  Step 1 — hom30 rake: for each (DDAY_STRATA × slot), minimal-flip synthetic hom30
           (already hard 0/1) to match observed rate. Boundary-preferred, seed=42.
  Step 2 — Floor guard: for single-person synthetic HHs whose daily mean dropped
           <0.30 (and was >=0.30 pre-rake), restore hom30=1 at night slots (1-8)
           until mean >=0.30.
  Step 3 — Spouse30 rake (only if check 6.3 fails): binarize synthetic Spouse30
           at 0.5, then minimal-flip per (DDAY_STRATA × slot) to observed mean.

Writes back atomically (.tmp + os.replace).
Run from any directory; paths are derived from the script location.
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

_HERE = Path(__file__).resolve().parent          # 2J_docs_occ_nTemp/
_BASE = _HERE.parent                              # GSSCanada-main/
_AUG_DIR = _BASE / "0_Occupancy" / "Outputs_21CEN22GSS" / "aug_pipeline"
_FULL_SCHED_PATH = _AUG_DIR / "21CEN22GSS_aug_Full_Schedules.csv"
_MATCHED_KEYS_PATH = _AUG_DIR / "21CEN22GSS_aug_Matched_Keys.csv"

EXPECTED_ROWS = 286_537
N_SLOTS = 48
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
SPOUSE_COLS = [f"Spouse30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
STRATA = [1, 2, 3]
NIGHT_SLOTS_IDX = list(range(8))     # 0-indexed 0..7 = hom30_001..008 (04:00-07:30)
FLOOR_THRESHOLD = 0.30
FLOOR_TARGET_SUM = FLOOR_THRESHOLD * N_SLOTS     # 14.4 => need sum >= 15
SPOUSE_GATE_PP = 3.0
HOME_ACTS = {2, 3, 5, 6, 7, 10}     # HH Work, Caregiving, Sleep, Eating, PersonalCare, PassiveLeisure


# ── Minimal-flip helpers (reused from 04L_joint_rake_test.py) ─────────────────

def _boundary_mask(arr, t):
    """(n, T) binary float → (n,) bool: slot t is at run boundary."""
    val_t = arr[:, t]
    left  = (arr[:, t - 1] != val_t) if t > 0           else np.ones(len(arr), dtype=bool)
    right = (arr[:, t + 1] != val_t) if t < arr.shape[1] - 1 else np.ones(len(arr), dtype=bool)
    return left | right


def _rake_binary_slot(arr_col, target_count, boundary, rng):
    """Flip arr_col (in-place 1-D view) to hit target_count ones.
    Prefers boundary records; breaks ties with rng. Returns flip count."""
    n_cur = int(np.sum(arr_col == 1.0))
    delta = target_count - n_cur
    if delta == 0:
        return 0
    if delta > 0:
        candidates = np.where(arr_col == 0.0)[0]
        n_flip = min(delta, len(candidates))
    else:
        candidates = np.where(arr_col == 1.0)[0]
        n_flip = min(-delta, len(candidates))
    if n_flip == 0:
        return 0
    bnd_pri = boundary[candidates].astype(np.int8)
    noise   = rng.random(len(candidates))
    order   = np.lexsort((noise, -bnd_pri))
    chosen  = candidates[order[:n_flip]]
    arr_col[chosen] = 1.0 - arr_col[chosen]
    return n_flip


# ── Check 6.3 helper ──────────────────────────────────────────────────────────

def _check_6_3(df):
    """Compute check 6.3 (Spouse30 global mean diff aug vs obs).
    Returns (aug_pp, obs_pp, diff_pp) or (None, None, None) if cols absent."""
    sp_p = [c for c in SPOUSE_COLS if c in df.columns]
    if not sp_p:
        return None, None, None
    obs = df[df["IS_SYNTHETIC"] == 0]
    aug_sp = float(df[sp_p].mean(axis=0).mean() * 100)
    obs_sp = float(obs[sp_p].mean(axis=0).mean() * 100)
    return aug_sp, obs_sp, abs(aug_sp - obs_sp)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72, flush=True)
    print("05_postlink_rake.py - Phase 8B-5b Post-Linkage Raking", flush=True)
    print("=" * 72, flush=True)
    print(f"  Full_Schedules : {_FULL_SCHED_PATH}", flush=True)
    print(f"  Matched_Keys   : {_MATCHED_KEYS_PATH}", flush=True)

    # Load Full_Schedules
    print(f"\nLoading {_FULL_SCHED_PATH.name} ...", flush=True)
    df = pd.read_csv(str(_FULL_SCHED_PATH), low_memory=False)
    n_total = len(df)
    print(f"  {n_total:,} rows x {df.shape[1]} cols", flush=True)
    assert n_total == EXPECTED_ROWS, f"Row count {n_total} != {EXPECTED_ROWS}"

    # Merge DDAY_STRATA if absent
    if "DDAY_STRATA" not in df.columns:
        print("  DDAY_STRATA absent, merging from Matched_Keys ...", flush=True)
        keys = pd.read_csv(str(_MATCHED_KEYS_PATH), usecols=["PP_ID", "DDAY_STRATA"])
        df = df.merge(keys, on="PP_ID", how="left")

    # Validate hom30 schema
    hom_p = [c for c in HOM_COLS if c in df.columns]
    assert len(hom_p) == 48, f"Only {len(hom_p)}/48 hom30 cols found"
    hom_flat = df[hom_p].values.ravel()
    hom_flat_nn = hom_flat[~np.isnan(hom_flat)]
    assert set(np.unique(hom_flat_nn)).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 before raking"
    print(f"  hom30 schema OK (hard 0/1 confirmed)", flush=True)

    syn_mask = df["IS_SYNTHETIC"] == 1
    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_idx  = df.index[syn_mask].tolist()
    n_syn = len(syn_idx)
    n_obs = int(obs_mask.sum())
    print(f"  synthetic={n_syn:,}  observed={n_obs:,}", flush=True)

    # Check 6.3 on UNRAKED linked file
    aug_sp, obs_sp, diff63_pre = _check_6_3(df)
    if diff63_pre is not None:
        print(f"\nCheck 6.3 (pre-rake):  aug_spouse={aug_sp:.2f}%  "
              f"obs_spouse={obs_sp:.2f}%  diff={diff63_pre:.2f} pp", flush=True)
        do_spouse_rake = diff63_pre > SPOUSE_GATE_PP
        if do_spouse_rake:
            print(f"  Spouse30 rake: YES -- 6.3 fails (>{SPOUSE_GATE_PP:.0f}pp)", flush=True)
        else:
            print(f"  Spouse30 rake: NO -- 6.3 passes (<={SPOUSE_GATE_PP:.0f}pp)", flush=True)
    else:
        do_spouse_rake = False
        print("\nCheck 6.3: Spouse30 columns absent -- skip", flush=True)

    # HH group sizes (for floor guard)
    hh_sizes = df.groupby("HH_ID").size().rename("_hh_size")
    df = df.merge(hh_sizes.reset_index(), on="HH_ID", how="left")

    # Capture pre-rake state for floor guard & coherence cost
    hom_syn_pre = df.loc[syn_idx, hom_p].values.astype(float).copy()   # (n_syn, 48)
    pre_means   = hom_syn_pre.mean(axis=1)                               # (n_syn,)
    sp_single   = (df.loc[syn_idx, "_hh_size"].values == 1)             # (n_syn,) bool

    # Step 1: Rake hom30 per (DDAY_STRATA x slot)
    print("\n[Step 1] Raking hom30 per (DDAY_STRATA x slot) ...", flush=True)
    rng = np.random.default_rng(42)
    total_hom_flips = 0

    for s in STRATA:
        obs_s_mask = obs_mask & (df["DDAY_STRATA"] == s)
        syn_s_mask = syn_mask & (df["DDAY_STRATA"] == s)
        obs_s_idx  = df.index[obs_s_mask].tolist()
        syn_s_idx  = df.index[syn_s_mask].tolist()
        if not syn_s_idx or not obs_s_idx:
            print(f"  stratum {s}: no syn or obs rows -- skip", flush=True)
            continue

        obs_rates = df.loc[obs_s_idx, hom_p].values.astype(float).mean(axis=0)  # (48,)
        hom_arr   = df.loc[syn_s_idx, hom_p].values.astype(float)               # (n_s, 48)
        n_s       = len(syn_s_idx)

        for t in range(N_SLOTS):
            tgt = max(0, min(n_s, int(round(obs_rates[t] * n_s))))
            bnd = _boundary_mask(hom_arr, t)
            total_hom_flips += _rake_binary_slot(hom_arr[:, t], tgt, bnd, rng)

        df.loc[syn_s_idx, hom_p] = hom_arr
        print(f"  stratum {s}: {n_s} syn rows raked", flush=True)

    print(f"  Total hom30 flips: {total_hom_flips:,}", flush=True)

    # Step 2: Floor guard
    print("\n[Step 2] Floor guard for single-person synthetic HHs ...", flush=True)
    hom_syn_post_rake = df.loc[syn_idx, hom_p].values.astype(float)   # (n_syn, 48)
    post_means_rake   = hom_syn_post_rake.mean(axis=1)

    needs_guard = (sp_single &
                   (post_means_rake < FLOOR_THRESHOLD) &
                   (pre_means >= FLOOR_THRESHOLD))
    guard_count = 0

    if needs_guard.any():
        guard_positions = np.where(needs_guard)[0]
        for pos in guard_positions:
            idx       = syn_idx[pos]
            row_hom   = hom_syn_post_rake[pos].copy()
            cur_sum   = row_hom.sum()
            for t in NIGHT_SLOTS_IDX:
                if cur_sum >= FLOOR_TARGET_SUM:
                    break
                if row_hom[t] == 0.0:
                    row_hom[t] = 1.0
                    cur_sum += 1.0
            df.loc[idx, hom_p] = row_hom
            guard_count += 1

    print(f"  Triggered: {guard_count} single-person HHs restored", flush=True)

    # Step 3: Spouse30 rake (conditional)
    total_sp_flips = 0
    sp_p = [c for c in SPOUSE_COLS if c in df.columns]
    if do_spouse_rake and sp_p:
        print(f"\n[Step 3] Raking Spouse30 ({len(sp_p)} cols) per "
              "(DDAY_STRATA x slot) ...", flush=True)

        syn_sp_soft = df.loc[syn_mask, sp_p].to_numpy(dtype=float)
        df.loc[syn_mask, sp_p] = (np.nan_to_num(syn_sp_soft, nan=0.0) >= 0.5).astype(float)

        for s in STRATA:
            obs_s_mask = obs_mask & (df["DDAY_STRATA"] == s)
            syn_s_mask = syn_mask & (df["DDAY_STRATA"] == s)
            obs_s_idx  = df.index[obs_s_mask].tolist()
            syn_s_idx  = df.index[syn_s_mask].tolist()
            if not syn_s_idx or not obs_s_idx:
                continue

            obs_sp_rates = np.nanmean(
                df.loc[obs_s_idx, sp_p].values.astype(float), axis=0)
            sp_arr = df.loc[syn_s_idx, sp_p].values.astype(float)
            n_s    = len(syn_s_idx)

            for t in range(len(sp_p)):
                if np.isnan(obs_sp_rates[t]):
                    continue
                tgt = max(0, min(n_s, int(round(obs_sp_rates[t] * n_s))))
                bnd = _boundary_mask(sp_arr, t)
                total_sp_flips += _rake_binary_slot(sp_arr[:, t], tgt, bnd, rng)

            df.loc[syn_s_idx, sp_p] = sp_arr

        print(f"  Total Spouse30 flips: {total_sp_flips:,}", flush=True)

        aug_sp2, obs_sp2, diff63_post = _check_6_3(df)
        print(f"  Check 6.3 (post-rake): aug={aug_sp2:.2f}%  "
              f"obs={obs_sp2:.2f}%  diff={diff63_post:.2f} pp "
              f"({'PASS' if diff63_post <= SPOUSE_GATE_PP else 'FAIL'})", flush=True)
    else:
        if not do_spouse_rake:
            print("\n[Step 3] Spouse30 rake skipped (check 6.3 passes pre-rake).",
                  flush=True)

    # Hard-binary assert on hom30
    final_hom_flat = df[hom_p].values.ravel()
    final_hom_nn   = final_hom_flat[~np.isnan(final_hom_flat)]
    assert set(np.unique(final_hom_nn)).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 after rake -- ABORT"
    assert len(df) == EXPECTED_ROWS, \
        f"Row count {len(df)} != {EXPECTED_ROWS} -- ABORT"
    print(f"\nAssertions: hom30 hard 0/1 OK  row count {len(df):,} OK", flush=True)

    # Coherence cost
    hom_syn_final = df.loc[syn_idx, hom_p].values.astype(float)
    act_p = [c for c in ACT_COLS if c in df.columns]
    incoherence_count = 0
    total_1to0 = int(((hom_syn_pre == 1.0) & (hom_syn_final == 0.0)).sum())
    total_0to1 = int(((hom_syn_pre == 0.0) & (hom_syn_final == 1.0)).sum())

    if act_p:
        act_syn = df.loc[syn_idx, act_p].values
        flipped_1to0 = (hom_syn_pre == 1.0) & (hom_syn_final == 0.0)
        for t in range(N_SLOTS):
            col_flip = flipped_1to0[:, t]
            if not col_flip.any():
                continue
            acts_t = act_syn[col_flip, t]
            acts_float = acts_t.astype(float)
            incoherence_count += int(np.isin(acts_float, list(HOME_ACTS)).sum())

    print(f"\nCoherence cost (hom30 flips vs act30):", flush=True)
    print(f"  Flips 1->0 (away-ified): {total_1to0:,}", flush=True)
    print(f"  Flips 0->1 (homed-back, floor guard+hom rake): {total_0to1:,}", flush=True)
    print(f"  New act/hom incoherences (1->0 flip AND act30 in HOME_ACTS): "
          f"{incoherence_count:,}", flush=True)

    # Atomic write
    df = df.drop(columns=["_hh_size"])
    out_path = str(_FULL_SCHED_PATH)
    tmp_path = out_path + ".tmp"
    print(f"\nWriting to {tmp_path} ...", flush=True)
    df.to_csv(tmp_path, index=False)

    n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1
    if n_written != EXPECTED_ROWS:
        os.remove(tmp_path)
        raise RuntimeError(
            f"Row count mismatch after write: {n_written} != {EXPECTED_ROWS}. "
            f"Truncated tmp removed; {out_path} not overwritten."
        )

    os.replace(tmp_path, out_path)
    print(f"RAKED FILE WRITTEN: {n_written:,} rows -> {out_path}", flush=True)

    print("\n" + "=" * 72, flush=True)
    print("Summary:", flush=True)
    print(f"  hom30 flips total          : {total_hom_flips:,}", flush=True)
    print(f"  floor guard restorations   : {guard_count}", flush=True)
    if do_spouse_rake:
        print(f"  Spouse30 flips             : {total_sp_flips:,}", flush=True)
    else:
        print(f"  Spouse30 flips             : 0 (check 6.3 passed, rake skipped)", flush=True)
    print(f"  new act/hom incoherences   : {incoherence_count:,}", flush=True)
    print("=" * 72, flush=True)
    print("ALL DONE.", flush=True)


if __name__ == "__main__":
    main()
