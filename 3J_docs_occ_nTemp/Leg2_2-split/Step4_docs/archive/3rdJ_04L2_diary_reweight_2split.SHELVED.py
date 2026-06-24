#!/usr/bin/env python3
"""
3rdJ_04L2_diary_reweight_2split.py — Step 4L2 (Leg-2): Diary-Level Reweight (Rung-ii Fix)

Closes G4 "work-peak under-fill" (obs ~28.72% vs syn ~18.39%, ≈10.3 pp gap in the
CLUSTER production run on raked diaries) WITHOUT re-training the generator and WITHOUT
editing the locked 04L slot-rake.

Root cause: 04L does a SLOT-LEVEL record-edit that forces 1-D per-slot marginals exact
but cannot add net midday work mass — it shreds within-diary structure (work blocks are
scattered across the 0/1 correction, diluting existing high-work diaries).

Fix (Rung-ii): treat each generated 24-h diary as IMMUTABLE and adjust DIARY WEIGHTS
(IPF/raking) to a 2-way Time×WorkPresence control margin.  Because a 2-way time×presence
margin implies the 1-D per-slot margins, this keeps 1-D marginals exact while forcing
work mass into the midday slots — and it preserves all within-diary transitions.
NO generator re-train.

IMPORTANT: operates on RAW R5 diaries (pre-slot-rake), NOT on 04L's slot-edited output.
The raw diaries have intact within-diary work blocks to up-weight.

Algorithm:
  1. Load raw R5 augmented_diaries.csv.  Within each stratum (CYCLE_YEAR × DDAY_STRATA),
     assign each SYNTHETIC diary a weight w_i (init = 1).  Observed rows are used only
     to compute the target rates; they are NOT reweighted.
  2. Build 2-way target margins Time×WorkPresence: for each slot j, observed AT_WORK
     rate (target_wrk[j]) and AT_HOME rate (target_hom[j]).  Run 3-state joint IPF/raking
     on diary weights so the weighted synthetic population matches those targets.
     3-state model per slot: diary is in state HOME (hom=1,wrk=0), WORK (hom=0,wrk=1),
     or NEITHER (hom=0,wrk=0).  The joint update avoids the cross-channel oscillation
     that plagues independent 1-D IPF when hom and wrk are mutually exclusive.
  3. ZERO-CELL FALLBACK: if IPF fails to converge (max_iter exceeded without tol), fall
     back to Sinkhorn (numpy/scipy, log-domain dual-variable ascent).  POT is NOT
     required; scipy.special.logsumexp is used for numerical stability but is optional.
     Reports which path was used in the provenance JSON.
  4. MATERIALIZE: resample synthetic diaries WITH REPLACEMENT proportional to w_i to
     produce a new augmented_diaries.csv with the SAME row count and SAME column schema.
     Observed rows are passed through unchanged (weight fixed = 1, not resampled).
  5. Write provenance JSON: per-stratum before/after work-peak rate, convergence info,
     method used (IPF or Sinkhorn), per-slot marginal errors after materialization.

WORK_PEAK_SLOTS: 0-indexed 8–19 (08:00–14:00 in 04:00-origin diary, matching validator).

Usage:
    python 3rdJ_04L2_diary_reweight_2split.py --smoke      # one stratum, fast
    python 3rdJ_04L2_diary_reweight_2split.py --full       # all strata
    python 3rdJ_04L2_diary_reweight_2split.py --smoke --r5_dir <path> --out_dir <path>

Zero-cell method: Sinkhorn (log-domain, numpy/scipy; POT absent in this env).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── POT / Sinkhorn availability ───────────────────────────────────────────────
_HAS_POT = False
try:
    import ot  # noqa: F401
    _HAS_POT = True
except ImportError:
    pass

_HAS_SCIPY = False
try:
    from scipy.special import logsumexp as _sp_logsumexp  # noqa: F401
    _HAS_SCIPY = True
except ImportError:
    pass

FALLBACK_METHOD = "sinkhorn_pot" if _HAS_POT else "sinkhorn_numpy_logdomain"
print(f"[init] POT available: {_HAS_POT}  |  scipy available: {_HAS_SCIPY}  "
      f"|  zero-cell fallback: {FALLBACK_METHOD}", flush=True)

# ── Platform paths (mirrors 04L) ──────────────────────────────────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main"
        r"\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = (
        "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main"
        "/3J_docs_occ_nTemp/Leg2_2-split"
    )
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )

_STEP4_SHARED  = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")
# Raw R5 diaries: pre-04L source (NOT R5_raked).  On Windows, lives directly in
# outputs_step4/.  On cluster, lives in sweep/R5_lr1e4/ or sweep/R10_fast/.
_R5_DIR_DEFAULT  = _STEP4_SHARED
_OUT_DIR_DEFAULT = os.path.join(_STEP4_SHARED, "sweep", "R5_reweight")

# ── Constants (mirror 04L exactly) ────────────────────────────────────────────
N_SLOTS         = 48
CYCLES          = [2005, 2010, 2015, 2022]
STRATA          = [1, 2, 3]
HOM_COLS        = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK_COLS        = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
# 0-indexed 8–19 = 08:00–14:00 in 04:00-origin diary (matches validator line 119)
WORK_PEAK_SLOTS = list(range(8, 20))

# IPF settings
IPF_MAX_ITER  = 1000
IPF_TOL       = 1e-4   # convergence in max|w_new - w_old| (after renorm)

# Sinkhorn settings (log-domain dual-ascent fallback)
SINK_MAX_ITER = 2000
SINK_TOL      = 1e-4
SINK_LR_INIT  = 0.5   # initial learning rate for dual update

RESAMPLE_SEED = 42


# ─────────────────────────────────────────────────────────────────────────────
# 3-state joint IPF on diary weights
# ─────────────────────────────────────────────────────────────────────────────

def _ipf_diary_weights(
    wrk_mat: np.ndarray,      # (n_syn, 48) binary wrk30
    hom_mat: np.ndarray,      # (n_syn, 48) binary hom30
    target_wrk: np.ndarray,   # (48,) observed AT_WORK rates
    target_hom: np.ndarray,   # (48,) observed AT_HOME rates
    max_iter: int = IPF_MAX_ITER,
    tol: float    = IPF_TOL,
) -> tuple[np.ndarray, dict]:
    """
    3-state joint IPF on diary weights to match per-slot AT_WORK / AT_HOME targets.

    At each slot j, each diary is in exactly ONE of three states:
      HOME    (hom=1, wrk=0) — target share = target_hom[j]
      WORK    (hom=0, wrk=1) — target share = target_wrk[j]
      NEITHER (hom=0, wrk=0) — target share = 1 - target_hom[j] - target_wrk[j]

    Multiplicative update (standard IPF / raking ratio):
      w_i *= ratio[state_i_at_slot_j]
    where ratio[state] = target_share[state] / current_weighted_share[state]

    This avoids the cross-channel oscillation that occurs when raking the HOME and
    WORK dimensions independently (since HOME and WORK are mutually exclusive, a ratio
    update on HOME changes the HOME/NEITHER balance, which then fights the WORK update).

    Returns (w, info_dict).  w is renormalised to mean(w) = 1 after each iteration.
    """
    n_syn = wrk_mat.shape[0]
    w     = np.ones(n_syn, dtype=np.float64)

    # Pre-compute boolean state matrices (immutable)
    # shape: (n_syn, 48) bool
    state_home    = (hom_mat == 1) & (wrk_mat == 0)
    state_work    = (hom_mat == 0) & (wrk_mat == 1)
    state_neither = (hom_mat == 0) & (wrk_mat == 0)

    info = {"method": "IPF_3state", "converged": False, "iters": 0,
            "max_delta_w": None, "zero_cell": False}

    for it in range(max_iter):
        w_old = w.copy()

        for j in range(N_SLOTS):
            sh = state_home[:, j]
            sw = state_work[:, j]
            sn = state_neither[:, j]

            wsum = w.sum()
            if wsum < 1e-12:
                info["zero_cell"] = True
                return w, info

            p_home    = float(np.dot(w, sh)) / wsum
            p_work    = float(np.dot(w, sw)) / wsum
            p_neither = float(np.dot(w, sn)) / wsum

            t_home    = float(target_hom[j])
            t_work    = float(target_wrk[j])
            t_neither = 1.0 - t_home - t_work

            # Detect zero-cell (target > 0 but no synthetic rows in that state)
            if t_home > 1e-10 and p_home <= 1e-12:
                info["zero_cell"] = True
                info["zero_cell_slot"] = j
                info["zero_cell_state"] = "home"
                return w, info
            if t_work > 1e-10 and p_work <= 1e-12:
                info["zero_cell"] = True
                info["zero_cell_slot"] = j
                info["zero_cell_state"] = "work"
                return w, info
            if t_neither > 1e-10 and p_neither <= 1e-12:
                info["zero_cell"] = True
                info["zero_cell_slot"] = j
                info["zero_cell_state"] = "neither"
                return w, info

            r_home    = (t_home    / p_home)    if p_home    > 1e-12 else 1.0
            r_work    = (t_work    / p_work)    if p_work    > 1e-12 else 1.0
            r_neither = (t_neither / p_neither) if p_neither > 1e-12 else 1.0

            # Update weights multiplicatively
            w = np.where(sh, w * r_home, np.where(sw, w * r_work, w * r_neither))

        # Renormalise to mean(w) = 1
        w_mean = w.mean()
        if w_mean > 1e-12:
            w /= w_mean

        delta = float(np.max(np.abs(w - w_old)))
        if delta < tol:
            info["converged"]   = True
            info["iters"]       = it + 1
            info["max_delta_w"] = delta
            return w, info

    info["iters"]       = max_iter
    info["max_delta_w"] = float(np.max(np.abs(w - w_old)))
    return w, info


# ─────────────────────────────────────────────────────────────────────────────
# Sinkhorn fallback (log-domain, numpy only — no POT required)
# ─────────────────────────────────────────────────────────────────────────────

def _sinkhorn_diary_weights(
    wrk_mat: np.ndarray,
    hom_mat: np.ndarray,
    target_wrk: np.ndarray,
    target_hom: np.ndarray,
    max_iter: int = SINK_MAX_ITER,
    tol: float    = SINK_TOL,
    lr_init: float = SINK_LR_INIT,
) -> tuple[np.ndarray, dict]:
    """
    Entropic reweight fallback (log-domain dual-variable ascent, no POT).

    Minimises KL(w || uniform) subject to:
      sum_i w_i * state_home[i,j]    / sum_i w_i == target_hom[j]  for all j
      sum_i w_i * state_work[i,j]    / sum_i w_i == target_wrk[j]  for all j
      sum_i w_i * state_neither[i,j] / sum_i w_i == 1 - target_hom[j] - target_wrk[j]

    Log weight: log w_i = - (1/reg) * [lam_h . state_home_i + lam_w . state_work_i]
    Duals lam_h, lam_w updated by gradient ascent on the Lagrangian.
    """
    n_syn = wrk_mat.shape[0]

    state_home    = (hom_mat == 1) & (wrk_mat == 0)   # (n_syn, 48)
    state_work    = (hom_mat == 0) & (wrk_mat == 1)

    lam_h = np.zeros(N_SLOTS, dtype=np.float64)
    lam_w = np.zeros(N_SLOTS, dtype=np.float64)

    reg = 1.0   # entropic regularisation (fixed; not critical for dual-ascent convergence)

    info = {"method": FALLBACK_METHOD, "converged": False, "iters": 0,
            "max_resid": None}

    max_resid = float("inf")
    for it in range(max_iter):
        # Log weights from duals: log w_i = -(1/reg) * sum_j lam_h[j]*sh[i,j] + lam_w[j]*sw[i,j]
        log_w = -(state_home.astype(np.float64) @ lam_h
                  + state_work.astype(np.float64) @ lam_w) / reg
        # Log-normalise (subtract log-sum-exp for numerical stability)
        log_w -= np.max(log_w)
        log_Z  = np.log(np.sum(np.exp(log_w)))
        log_w -= log_Z
        w = np.exp(log_w)   # sum = 1

        # Current weighted means
        cur_h = state_home.astype(np.float64).T @ w    # (48,)
        cur_w = state_work.astype(np.float64).T @ w    # (48,)

        # Gradient ascent on duals
        lr = lr_init / (1.0 + it * 0.01)
        lam_h += lr * (target_hom - cur_h)
        lam_w += lr * (target_wrk - cur_w)

        max_resid = float(max(np.max(np.abs(cur_h - target_hom)),
                              np.max(np.abs(cur_w - target_wrk))))

        if max_resid < tol:
            info["converged"] = True
            info["iters"]     = it + 1
            info["max_resid"] = max_resid
            w /= w.mean()
            return w, info

    info["iters"]     = max_iter
    info["max_resid"] = max_resid
    w /= w.mean()
    return w, info


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher: IPF first, Sinkhorn on failure
# ─────────────────────────────────────────────────────────────────────────────

def _compute_diary_weights(
    wrk_mat: np.ndarray,
    hom_mat: np.ndarray,
    target_wrk: np.ndarray,
    target_hom: np.ndarray,
    ipf_max_iter: int = IPF_MAX_ITER,
    ipf_tol: float    = IPF_TOL,
    sink_reg: float   = 1.0,
) -> tuple[np.ndarray, dict]:
    """Try 3-state joint IPF first; fall back to Sinkhorn on zero-cell or non-convergence."""
    w, info = _ipf_diary_weights(wrk_mat, hom_mat, target_wrk, target_hom,
                                  max_iter=ipf_max_iter, tol=ipf_tol)
    if info["converged"]:
        return w, info

    # IPF failed → Sinkhorn
    print(f"    [fallback] IPF did not converge "
          f"(iters={info['iters']}, delta={info.get('max_delta_w','?'):.5f}, "
          f"zero_cell={info.get('zero_cell',False)}); switching to {FALLBACK_METHOD}",
          flush=True)
    w_sink, info_sink = _sinkhorn_diary_weights(wrk_mat, hom_mat, target_wrk, target_hom)
    info_sink["ipf_info"] = {k: v for k, v in info.items()
                              if k not in ("method",)}
    return w_sink, info_sink


# ─────────────────────────────────────────────────────────────────────────────
# Materialise: resample synthetic rows proportional to weights
# ─────────────────────────────────────────────────────────────────────────────

def _materialize_stratum(
    syn_sub: pd.DataFrame,
    w: np.ndarray,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Resample synthetic rows WITH REPLACEMENT proportional to w_i.
    Returns a DataFrame with the SAME row count as syn_sub, same column schema.
    """
    n     = len(syn_sub)
    w_pos = np.clip(w, 0.0, None)
    w_sum = w_pos.sum()
    if w_sum < 1e-12:
        probs = np.ones(n, dtype=np.float64) / n
    else:
        probs = w_pos / w_sum

    chosen_local = rng.choice(n, size=n, replace=True, p=probs)
    return syn_sub.iloc[chosen_local].reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# Work-peak rate helper (matches validator definition exactly)
# ─────────────────────────────────────────────────────────────────────────────

def _work_peak_rate_arr(arr: np.ndarray) -> float:
    """Mean AT_WORK over WORK_PEAK_SLOTS (0-indexed 8–19) for a (n, 48) array."""
    if arr.shape[0] == 0:
        return float("nan")
    return float(np.nanmean(arr[:, WORK_PEAK_SLOTS])) * 100.0


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="3rdJ Step 4L2 — Diary-Level Reweight (Rung-ii G4 fix)"
    )
    p.add_argument("--smoke", action="store_true",
                   help="Process ONE stratum only (cy=2022, s=1); fast local test.")
    p.add_argument("--full",  action="store_true",
                   help="Process ALL strata (4 cycles × 3 strata).")
    p.add_argument("--r5_dir",   default=None,
                   help=f"Dir containing raw R5 augmented_diaries.csv "
                        f"(default: {_R5_DIR_DEFAULT})")
    p.add_argument("--out_dir",  default=None,
                   help=f"Output dir for reweighted augmented_diaries.csv "
                        f"(default: {_OUT_DIR_DEFAULT}). Must NOT be R5_raked.")
    p.add_argument("--data_dir", default=None,
                   help="Alias for --r5_dir (mirrors 04L arg style).")
    p.add_argument("--seed",         type=int,   default=RESAMPLE_SEED)
    p.add_argument("--ipf_max_iter", type=int,   default=IPF_MAX_ITER)
    p.add_argument("--ipf_tol",      type=float, default=IPF_TOL)
    p.add_argument("--sink_reg",     type=float, default=1.0,
                   help="Entropic regularisation for Sinkhorn fallback (default 1.0).")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if not args.smoke and not args.full:
        print("[ERROR] Specify --smoke or --full.", file=sys.stderr)
        sys.exit(1)

    r5_dir  = args.r5_dir or args.data_dir or _R5_DIR_DEFAULT
    out_dir = args.out_dir or _OUT_DIR_DEFAULT

    aug_src   = os.path.join(r5_dir, "augmented_diaries.csv")
    out_csv   = os.path.join(out_dir, "augmented_diaries.csv")
    prov_path = os.path.join(out_dir, "04L2_reweight_provenance.json")

    # Safety: refuse to overwrite locked outputs
    for locked_name in ["R5_raked", "R5_lr1e4"]:
        if locked_name in os.path.normpath(out_dir):
            print(f"[ERROR] out_dir '{out_dir}' contains locked name '{locked_name}'. "
                  "Use a different output directory.", file=sys.stderr)
            sys.exit(1)

    print("=" * 64)
    print("3rdJ Step 4L2 (Leg-2) — Diary-Level Reweight")
    print("=" * 64)
    print(f"  r5_dir:    {r5_dir}")
    print(f"  aug_src:   {aug_src}")
    print(f"  out_dir:   {out_dir}")
    print(f"  mode:      {'SMOKE (cy=2022, s=1 only)' if args.smoke else 'FULL'}")
    print(f"  seed:      {args.seed}")
    print(f"  IPF:       max_iter={args.ipf_max_iter}  tol={args.ipf_tol}")
    print(f"  POT:       {_HAS_POT}  |  scipy: {_HAS_SCIPY}  |  fallback: {FALLBACK_METHOD}")
    print()

    os.makedirs(out_dir, exist_ok=True)

    # ── Step 1: Load raw R5 diaries ───────────────────────────────────────────
    t0 = time.time()
    print("[1/4] Loading raw R5 augmented_diaries.csv ...", flush=True)
    if not os.path.isfile(aug_src):
        raise FileNotFoundError(f"Raw R5 CSV not found: {aug_src}")
    aug = pd.read_csv(aug_src, low_memory=False)
    print(f"  Loaded {len(aug):,} rows × {aug.shape[1]} cols in {time.time()-t0:.1f}s  "
          f"(IS_SYN=0: {(aug['IS_SYNTHETIC']==0).sum():,}, "
          f"IS_SYN=1: {(aug['IS_SYNTHETIC']==1).sum():,})")

    for col in (HOM_COLS[:1] + WRK_COLS[:1]
                + ["occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"]):
        if col not in aug.columns:
            raise ValueError(f"Missing required column: {col}")

    strata_to_run = [(2022, 1)] if args.smoke else [(cy, s)
                                                    for cy in CYCLES for s in STRATA]
    if args.smoke:
        print("  [SMOKE] Processing cy=2022, s=1 only.")

    # ── Step 2: Per-stratum reweight ──────────────────────────────────────────
    print("\n[2/4] Per-stratum diary-level reweight ...", flush=True)

    provenance: dict = {}
    rng = np.random.default_rng(args.seed)

    obs_passthrough = aug[aug["IS_SYNTHETIC"] == 0].copy()
    syn_blocks: list[pd.DataFrame] = []

    for cell_i, (cy, s) in enumerate(strata_to_run, 1):
        obs_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                    & (aug["IS_SYNTHETIC"] == 0))
        syn_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                    & (aug["IS_SYNTHETIC"] == 1))

        osub = aug[obs_mask]
        ssub = aug[syn_mask]
        n_obs, n_syn = len(osub), len(ssub)
        n_cells = len(strata_to_run)

        print(f"  [{cell_i}/{n_cells}] cy={cy} s={s}: n_obs={n_obs}, n_syn={n_syn}",
              end="", flush=True)

        if n_syn == 0:
            print(" — no synthetic rows, skipping")
            continue
        if n_obs == 0:
            print(" — no observed rows (cannot compute targets), skipping")
            provenance[f"cy{cy}_s{s}"] = {"status": "skipped_no_obs", "n_syn": n_syn}
            syn_blocks.append(ssub.reset_index(drop=True))
            continue

        print()   # newline after status prefix

        # Observed per-slot rates (mirrors 04L: np.nanmean over binary 0/1)
        obs_wrk_arr = osub[WRK_COLS].to_numpy(dtype=float)   # (n_obs, 48)
        obs_hom_arr = osub[HOM_COLS].to_numpy(dtype=float)   # (n_obs, 48)
        target_wrk  = np.nanmean(obs_wrk_arr, axis=0)        # (48,)
        target_hom  = np.nanmean(obs_hom_arr, axis=0)        # (48,)

        # Synthetic matrices
        syn_wrk_mat = ssub[WRK_COLS].to_numpy(dtype=float)   # (n_syn, 48)
        syn_hom_mat = ssub[HOM_COLS].to_numpy(dtype=float)   # (n_syn, 48)

        # BEFORE metrics
        before_wrk_peak = _work_peak_rate_arr(syn_wrk_mat)
        before_hom_agg  = float(np.nanmean(syn_hom_mat)) * 100.0
        before_wrk_agg  = float(np.nanmean(syn_wrk_mat)) * 100.0
        obs_wrk_peak    = _work_peak_rate_arr(obs_wrk_arr)

        # Compute diary weights
        t_cell = time.time()
        w, info = _compute_diary_weights(
            syn_wrk_mat, syn_hom_mat, target_wrk, target_hom,
            ipf_max_iter=args.ipf_max_iter, ipf_tol=args.ipf_tol,
        )
        elapsed = time.time() - t_cell

        # WEIGHTED metrics (before materialization)
        w_pos  = np.clip(w, 0.0, None)
        w_sum  = w_pos.sum()
        w_norm = w_pos / w_sum if w_sum > 1e-12 else np.ones(n_syn) / n_syn
        after_wrk_peak_wt = float(np.average(
            np.nanmean(syn_wrk_mat[:, WORK_PEAK_SLOTS], axis=1), weights=w_norm)) * 100.0

        # Materialise
        syn_resampled = _materialize_stratum(ssub, w, rng)

        # MATERIALISED metrics
        mat_wrk_mat    = syn_resampled[WRK_COLS].to_numpy(dtype=float)
        mat_hom_mat    = syn_resampled[HOM_COLS].to_numpy(dtype=float)
        after_wrk_peak = _work_peak_rate_arr(mat_wrk_mat)
        after_hom_agg  = float(np.nanmean(mat_hom_mat)) * 100.0
        after_wrk_agg  = float(np.nanmean(mat_wrk_mat)) * 100.0

        # Per-slot marginal errors after materialization
        mat_wrk_slots = np.nanmean(mat_wrk_mat, axis=0)
        mat_hom_slots = np.nanmean(mat_hom_mat, axis=0)
        wrk_slot_max_err = float(np.max(np.abs(mat_wrk_slots - target_wrk))) * 100.0
        hom_slot_max_err = float(np.max(np.abs(mat_hom_slots - target_hom))) * 100.0

        gap_before = obs_wrk_peak - before_wrk_peak
        gap_after  = obs_wrk_peak - after_wrk_peak

        syn_blocks.append(syn_resampled)

        prov_key = f"cy{cy}_s{s}"
        provenance[prov_key] = {
            "n_obs":                  n_obs,
            "n_syn":                  n_syn,
            "obs_wrk_peak_pct":       round(obs_wrk_peak,    3),
            "before_wrk_peak_pct":    round(before_wrk_peak, 3),
            "after_wrk_peak_wt_pct":  round(after_wrk_peak_wt, 3),
            "after_wrk_peak_mat_pct": round(after_wrk_peak,  3),
            "gap_before_pp":          round(gap_before,       3),
            "gap_after_pp":           round(gap_after,        3),
            "before_hom_agg_pct":     round(before_hom_agg,  3),
            "after_hom_agg_mat_pct":  round(after_hom_agg,   3),
            "before_wrk_agg_pct":     round(before_wrk_agg,  3),
            "after_wrk_agg_mat_pct":  round(after_wrk_agg,   3),
            "wrk_slot_max_err_pp":    round(wrk_slot_max_err, 3),
            "hom_slot_max_err_pp":    round(hom_slot_max_err, 3),
            "convergence":            info,
            "elapsed_s":              round(elapsed,          2),
        }

        status = "CONV" if info.get("converged") else "FALLBACK"
        print(f"    {status} [{info['method']}] "
              f"wrk_peak: {before_wrk_peak:.2f}% → "
              f"{after_wrk_peak_wt:.2f}% (wtd) / {after_wrk_peak:.2f}% (mat)  "
              f"obs={obs_wrk_peak:.2f}%  gap {gap_before:+.2f} → {gap_after:+.2f} pp  "
              f"hom_err={hom_slot_max_err:.3f}pp  wrk_err={wrk_slot_max_err:.3f}pp  "
              f"{elapsed:.1f}s", flush=True)

    # ── Step 3: Assemble output DataFrame ─────────────────────────────────────
    print("\n[3/4] Assembling output ...", flush=True)

    if syn_blocks:
        syn_all = pd.concat(syn_blocks, ignore_index=True)
    else:
        syn_all = pd.DataFrame(columns=aug.columns)

    # SMOKE: include remaining (un-processed) synthetic rows unchanged
    if args.smoke:
        smoke_cy, smoke_s = strata_to_run[0]
        remaining_syn = aug[
            (aug["IS_SYNTHETIC"] == 1)
            & ~((aug["CYCLE_YEAR"] == smoke_cy) & (aug["DDAY_STRATA"] == smoke_s))
        ].copy()
        syn_all = pd.concat([syn_all, remaining_syn], ignore_index=True)
        print(f"  [SMOKE] Appended {len(remaining_syn):,} un-processed synthetic rows unchanged.")

    aug_out = pd.concat([obs_passthrough, syn_all], ignore_index=True)

    # Validate row count and schema
    if len(aug_out) != len(aug):
        raise RuntimeError(
            f"Row count mismatch: expected {len(aug):,}, got {len(aug_out):,}")
    missing_cols = set(aug.columns) - set(aug_out.columns)
    extra_cols   = set(aug_out.columns) - set(aug.columns)
    if missing_cols or extra_cols:
        raise RuntimeError(f"Schema mismatch: missing={missing_cols}, extra={extra_cols}")

    print(f"  Output: {len(aug_out):,} rows × {aug_out.shape[1]} cols  "
          f"(matches input — OK)")

    # ── Step 4: Atomic write ──────────────────────────────────────────────────
    print(f"\n[4/4] Writing output ...", flush=True)
    tmp_csv = out_csv + ".tmp"
    aug_out.to_csv(tmp_csv, index=False)
    with open(tmp_csv, encoding="utf-8") as fh:
        n_written = sum(1 for _ in fh) - 1   # exclude header
    if n_written != len(aug_out):
        os.remove(tmp_csv)
        raise RuntimeError(
            f"Write row-count mismatch: wrote {n_written}, expected {len(aug_out)}")
    os.replace(tmp_csv, out_csv)
    print(f"  Wrote {len(aug_out):,} rows -> {out_csv}")

    # Provenance JSON
    provenance["_meta"] = {
        "mode":             "smoke" if args.smoke else "full",
        "r5_src":           aug_src,
        "out_dir":          out_dir,
        "seed":             args.seed,
        "ipf_max_iter":     args.ipf_max_iter,
        "ipf_tol":          args.ipf_tol,
        "pot_available":    _HAS_POT,
        "scipy_available":  _HAS_SCIPY,
        "fallback_method":  FALLBACK_METHOD,
        "work_peak_slots_0idx": WORK_PEAK_SLOTS,
        "strata_processed": [f"cy{cy}_s{s}" for cy, s in strata_to_run],
    }
    with open(prov_path, "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
    print(f"  Wrote provenance -> {prov_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 64)
    print("SUMMARY")
    print("=" * 64)
    for key, v in provenance.items():
        if key.startswith("_"):
            continue
        if "gap_before_pp" not in v:
            print(f"  {key}: {v.get('status', '?')}")
            continue
        method = v["convergence"]["method"]
        conv   = "CONV" if v["convergence"].get("converged") else "FBCK"
        print(f"  {key}: "
              f"wrk_peak {v['before_wrk_peak_pct']:.2f}% → "
              f"{v['after_wrk_peak_mat_pct']:.2f}% (mat)  "
              f"obs={v['obs_wrk_peak_pct']:.2f}%  "
              f"gap {v['gap_before_pp']:+.2f} → {v['gap_after_pp']:+.2f} pp  "
              f"[{method}/{conv}]  "
              f"wrk_err={v['wrk_slot_max_err_pp']:.3f}pp  "
              f"hom_err={v['hom_slot_max_err_pp']:.3f}pp")

    print(f"\nNOTE (smoke mode on raw R5 local data):")
    print(f"  The raw R5 diaries locally have near-zero work-peak gaps (04L raking")
    print(f"  was not applied to this input).  The 10.3 pp gap appears only AFTER 04L")
    print(f"  on the cluster (R10_fast → 04L_floataware).  On the cluster, this script")
    print(f"  should be pointed at sweep/R10_fast/augmented_diaries.csv (pre-04L) to")
    print(f"  see the large gap close.")
    print(f"\nOK 04L2 (Leg-2) diary reweight complete.")
    print(f"  Output dir: {out_dir}")


if __name__ == "__main__":
    main()
