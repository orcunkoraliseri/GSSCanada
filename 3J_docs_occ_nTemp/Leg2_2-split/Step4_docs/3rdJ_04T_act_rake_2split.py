# -*- coding: utf-8 -*-
"""
3rdJ_04T_act_rake_2split.py — Step 4T (Leg-2): act30 Conditional Re-Rake.

Implementation plan: 2J_to_3J_improvement_implementation.md, Task 1 (audit Item 2).

Closes Gate A (FLOATING-rate excess) by re-raking the 14-category act30_* activity
channel CONDITIONALLY on the final (hom30, wrk30) occupancy state, WITHOUT touching
the binary hom30/wrk30 channels themselves. Run AFTER 3rdJ_04M_mindwell_2split.py —
04M edits hom30/wrk30 only; if act30 were conditioned before 04M, the smoother would
re-break the conditioning it depends on.

Background: 3rdJ_04L_joint_rake_2split.py rakes hom30/wrk30 to match observed
per-(CYCLE_YEAR x DDAY_STRATA x slot) marginals but carries act30 forward untouched
(04L header lines 21-23). Result: many synthetic slots say "activity = Work" (act30==1)
while the person's raked physical state is neither AT_HOME nor AT_WORK — the
physically-impossible FLOATING state (3rdJ_04P_work_wrk30_discordance.py). Work
activity while hom30=1 (TELEWORK) is legitimate and is this paper's core WFH signal;
it must be preserved, never zeroed.

Method — ported from 2J's proven fix (2J_docs_occ_nTemp/05_postlink_rake.py:118-319:
_round_to_sum, _rake_categorical_slot, _rake_act_group, _run_act30_conditional_rake),
extended from 2J's 2-way hom30=1/0 conditioning to a 3-way occupancy state:
    STATE_WORK    (wrk30==1)                     -> rake to observed AT-WORK act mix
    STATE_HOME    (hom30==1 & wrk30==0)           -> rake to observed AT-HOME act mix
                                                      (contains legitimate TELEWORK share
                                                      -- never zeroed)
    STATE_NEITHER (hom30==0 & wrk30==0)           -> rake to observed NEITHER act mix
                                                      (near-zero work share -> this is the
                                                      mechanism that closes Gate A; no hard
                                                      lock on act30==Work)
Cell = (CYCLE_YEAR x DDAY_STRATA x slot x LFTAG-or-pooled), with 2J's MIN_OBS_FOR_LFTAG
sparsity gate pooling thin LFTAG cells up to the (CYCLE_YEAR, DDAY_STRATA)-level target
(OD-I2, resolved 2026-07-15: keep 2J's design, do not switch).

3J-specific extension (not present in 2J's source data): ~2% of syn rows have LFTAG==NaN
(2J's aug pool never has this). Rather than silently leaving those rows completely
unraked (they would match no LFTAG group in 2J's literal group-membership logic), this
port folds NaN-LFTAG rows into the same "pooled" (CYCLE_YEAR, DDAY_STRATA)-level group as
the sparsity-thin LFTAG values. This is a data-completeness fix, not a design change --
flagged explicitly in the Task-1 Progress Log.

Only act30_* columns are ever written. hom30_*/wrk30_* are read-only inputs throughout
and come out of this script byte-identical to the input CSV.

Usage:
    py -3 3rdJ_04T_act_rake_2split.py \
        --in_csv  outputs_step4/sweep/R5_raked_mindwell/augmented_diaries.csv \
        --out_dir outputs_step4/sweep/R5_raked_mindwell_actv2 \
        [--seed 42] [--smoke] [--smoke_frac 0.05]

Dependencies: pandas, numpy (no other non-stdlib requirements).
Build: 2026-07-15 (employee, Claude Sonnet 5)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

N_SLOTS = 48
CYCLES = [2005, 2010, 2015, 2022]
STRATA = [1, 2, 3]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK_COLS = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]

# act30 category range: 1..14 inclusive (matches 04F_validation.py / 2J convention).
ACT_MIN = 1
ACT_MAX = 14
ACT_CATEGORIES = list(range(ACT_MIN, ACT_MAX + 1))
WORK_CAT = 1

# Sparsity guard, ported unchanged from 2J 05_postlink_rake.py:66.
MIN_OBS_FOR_LFTAG = 30

# ── 3-way occupancy state (derived from hom30/wrk30; NEVER mutated by this script) ──
STATE_NEITHER = 0   # hom30==0 & wrk30==0  -> FLOATING when act30==WORK_CAT
STATE_HOME    = 1   # hom30==1 & wrk30==0  -> includes legitimate TELEWORK
STATE_WORK    = 2   # wrk30==1             -> AT-WORK
STATES = (STATE_WORK, STATE_HOME, STATE_NEITHER)
STATE_LABELS = {STATE_WORK: "WORK", STATE_HOME: "HOME", STATE_NEITHER: "NEITHER"}


def _compute_state(hom_arr: np.ndarray, wrk_arr: np.ndarray) -> np.ndarray:
    """(n, T) hom30/wrk30 float arrays -> (n, T) int8 3-way state array.
    Assumes hom30==1 & wrk30==1 never co-occurs (guaranteed by the upstream 04L joint
    rake's mutual-exclusion guarantee + 04M's per-channel-only smoothing); if it ever
    does, wrk30==1 wins (STATE_WORK), matching the 04L "both=1: 0 (expect 0)" invariant
    this script assumes but does not enforce."""
    state = np.zeros(hom_arr.shape, dtype=np.int8)   # default STATE_NEITHER == 0
    state[wrk_arr == 1] = STATE_WORK
    state[(wrk_arr != 1) & (hom_arr == 1)] = STATE_HOME
    return state


# ── Ported verbatim from 2J 05_postlink_rake.py:118-144 ──────────────────────────

def _round_to_sum(props, categories, n):
    """Largest-remainder rounding: proportions (dict cat -> prop; missing/NaN
    treated as 0, need not sum to 1) -> integer counts over `categories` that
    sum EXACTLY to n. Returns None if there is no usable observed reference
    (all-zero proportions) -- caller should skip raking that (cell, slot)."""
    raw = {}
    for c in categories:
        v = props.get(c, 0.0)
        v = 0.0 if (v is None or (isinstance(v, float) and np.isnan(v))) else float(v)
        raw[c] = max(0.0, v)
    total = sum(raw.values())
    if total <= 0:
        return None
    scaled = {c: raw[c] / total * n for c in categories}
    floors = {c: int(np.floor(v)) for c, v in scaled.items()}
    remainder = n - sum(floors.values())
    if remainder > 0:
        order = sorted(categories, key=lambda c: (scaled[c] - floors[c]), reverse=True)
        for c in order[:remainder]:
            floors[c] += 1
    elif remainder < 0:
        order = sorted(categories, key=lambda c: (scaled[c] - floors[c]))
        for c in order[:(-remainder)]:
            if floors[c] > 0:
                floors[c] -= 1
    return floors


# ── Ported verbatim from 2J 05_postlink_rake.py:147-207 ──────────────────────────

def _rake_categorical_slot(cur_vals, target_counts, categories, left_vals, right_vals, rng):
    """14-way minimal-move categorical rake for one (cell, slot) subset.
    Computes per-category deficit/surplus vs `target_counts`, moves the minimum
    number of records surplus-category -> deficit-category. Records whose
    neighbouring slot (left_vals/right_vals -- same records, adjacent time slots,
    pre-filtered by the caller to NaN-out neighbours that do not share the current
    3-way state) already holds the destination category are preferred (extends
    existing activity runs instead of creating isolated one-off transitions).
    Ties broken with `rng` (shared, seeded, never reseeded mid-run).

    Returns: (new_vals, n_moved). No record is moved more than once per call.
    """
    new_vals = cur_vals.copy()
    n = len(new_vals)
    cur_counts  = {c: int(np.sum(new_vals == c)) for c in categories}
    diff        = {c: int(target_counts.get(c, 0)) - cur_counts[c] for c in categories}
    deficits    = {c: d for c, d in diff.items() if d > 0}
    surplus_rem = {c: -d for c, d in diff.items() if d < 0}
    if not deficits or not surplus_rem:
        return new_vals, 0

    n_moved = 0
    for dcat in sorted(deficits.keys()):
        need = deficits[dcat]
        while need > 0:
            src_cats = [c for c, b in surplus_rem.items() if b > 0]
            if not src_cats:
                break
            candidates = np.where(np.isin(new_vals, src_cats))[0]
            if len(candidates) == 0:
                break
            bnd_pri = ((left_vals[candidates] == dcat) | (right_vals[candidates] == dcat)).astype(np.int8)
            noise   = rng.random(len(candidates))
            order   = np.lexsort((noise, -bnd_pri))
            take_n  = min(need, len(candidates))
            chosen  = candidates[order[:take_n]]
            for idx in chosen:
                if need == 0:
                    break
                src = new_vals[idx]
                if surplus_rem.get(src, 0) <= 0:
                    continue   # already exhausted by an earlier pick within `chosen`
                new_vals[idx] = dcat
                surplus_rem[src] -= 1
                n_moved += 1
                need -= 1
    return new_vals, n_moved


# ── 3-way extension of 2J's _rake_act_group (05_postlink_rake.py:210-274) ────────

def _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, wrk_p, rng, categories=ACT_CATEGORIES):
    """Runs the 48-slot act30 categorical rake for one (cy x stratum x LFTAG-or-
    pooled) group. Each slot is split into 3-way (WORK / HOME / NEITHER) subsets
    BEFORE raking, and each subset is raked independently against the matching
    state-conditioned observed target -- this guarantees a record's activity code
    can only be drawn from the observed distribution of records that share its OWN
    current 3-way physical state at that exact slot. hom30/wrk30 are read-only here
    (never mutated). Mutates df in place (act_p columns, syn_g_idx rows only).
    Returns total records moved across all 48 slots."""
    if not syn_g_idx or not obs_g_idx:
        return 0

    act_arr     = df.loc[syn_g_idx, act_p].values.astype(float)   # (n_g, 48) -- mutated locally
    hom_arr_syn = df.loc[syn_g_idx, hom_p].values.astype(float)
    wrk_arr_syn = df.loc[syn_g_idx, wrk_p].values.astype(float)
    obs_act_arr = df.loc[obs_g_idx, act_p].values.astype(float)
    obs_hom_arr = df.loc[obs_g_idx, hom_p].values.astype(float)
    obs_wrk_arr = df.loc[obs_g_idx, wrk_p].values.astype(float)

    state_syn = _compute_state(hom_arr_syn, wrk_arr_syn)   # (n_g, 48) int8
    state_obs = _compute_state(obs_hom_arr, obs_wrk_arr)

    n_moved = 0

    for t in range(N_SLOTS):
        for st in STATES:
            syn_rows = np.where(state_syn[:, t] == st)[0]
            if len(syn_rows) == 0:
                continue
            obs_rows = np.where(state_obs[:, t] == st)[0]
            if len(obs_rows) == 0:
                continue   # no observed reference for this (slot, state) -- leave as-is
            obs_vals_t = obs_act_arr[obs_rows, t]
            obs_vals_t = obs_vals_t[~np.isnan(obs_vals_t)]
            if len(obs_vals_t) == 0:
                continue
            counts = {c: float(np.sum(obs_vals_t == c)) for c in categories}

            target_counts = _round_to_sum(counts, categories, len(syn_rows))
            if target_counts is None:
                continue

            cur_vals = act_arr[syn_rows, t]
            # Boundary preference must only fire when the NEIGHBOURING slot shares
            # this same 3-way state st -- generalizes 2J's hom-status gate (its
            # lines 251-267) from 2 states to 3, for the same reason: a neighbour in
            # a DIFFERENT physical state must not bias this state's rake toward
            # extending a run across a hom/wrk state transition.
            if t > 0:
                left = act_arr[syn_rows, t - 1]
                left = np.where(state_syn[syn_rows, t - 1] == st, left, np.nan)
            else:
                left = np.full(len(syn_rows), np.nan)
            if t < N_SLOTS - 1:
                right = act_arr[syn_rows, t + 1]
                right = np.where(state_syn[syn_rows, t + 1] == st, right, np.nan)
            else:
                right = np.full(len(syn_rows), np.nan)

            new_vals, n_mv = _rake_categorical_slot(cur_vals, target_counts, categories, left, right, rng)
            act_arr[syn_rows, t] = new_vals
            n_moved += n_mv

    df.loc[syn_g_idx, act_p] = act_arr
    return n_moved


# ── 3-way extension of 2J's _run_act30_conditional_rake (05_postlink_rake.py:277-331) ──

def _run_act30_conditional_rake(df, act_p, hom_p, wrk_p, obs_mask, syn_mask, rng):
    """Step: 14-way act30 rake per (CYCLE_YEAR x DDAY_STRATA x slot x LFTAG
    [sparsity-gated, <MIN_OBS_FOR_LFTAG obs -> pooled to (cy,s)-level target]), run
    SEPARATELY for the WORK / HOME / NEITHER 3-way state of each cell (inside
    _rake_act_group) so activity codes never cross a physical-state boundary.

    3J extension vs 2J: adds the CYCLE_YEAR outer loop (2J's single-source aug pool
    has no cycle dimension; 3J's does, matching 04L's cy x s cell grid) and folds
    syn rows with LFTAG==NaN into the pooled group alongside sparsity-thin LFTAG
    values (2J's source data has no NaN LFTAG; see module docstring).

    Returns (total_moves, diagnostics dict) including LFTAG pooling-rate stats.
    """
    total_moves = 0
    lftag_drop_log = []
    has_lftag = "LFTAG" in df.columns

    lftag_vals = (sorted(v for v in df.loc[obs_mask, "LFTAG"].dropna().unique().tolist())
                  if has_lftag else [])

    n_cells_total = 0
    n_cells_thin  = 0
    n_syn_rows_seen   = 0
    n_syn_rows_pooled = 0

    for cy in CYCLES:
        for s in STRATA:
            obs_cs_mask = obs_mask & (df["CYCLE_YEAR"] == cy) & (df["DDAY_STRATA"] == s)
            syn_cs_mask = syn_mask & (df["CYCLE_YEAR"] == cy) & (df["DDAY_STRATA"] == s)
            if not obs_cs_mask.any() or not syn_cs_mask.any():
                print(f"  cy={cy} s={s}: no syn or obs rows -- skip", flush=True)
                continue

            n_syn_rows_seen += int(syn_cs_mask.sum())

            if not has_lftag:
                groups = [("no_lftag_col", obs_cs_mask, syn_cs_mask)]
            else:
                obs_by_lftag = {l: int((obs_cs_mask & (df["LFTAG"] == l)).sum()) for l in lftag_vals}
                thin = [l for l in lftag_vals if obs_by_lftag.get(l, 0) < MIN_OBS_FOR_LFTAG]
                ok   = [l for l in lftag_vals if l not in thin]
                n_cells_total += len(lftag_vals)
                n_cells_thin  += len(thin)
                if thin:
                    lftag_drop_log.append({"cy": cy, "s": s, "thin": thin,
                                            "obs_counts": {l: obs_by_lftag[l] for l in thin}})
                    print(f"  cy={cy} s={s}: LFTAG {thin} sparsity-gated "
                          f"(<{MIN_OBS_FOR_LFTAG} obs diaries) -- pooled to (cy,s)-level target",
                          flush=True)

                groups = [(l, obs_cs_mask & (df["LFTAG"] == l), syn_cs_mask & (df["LFTAG"] == l))
                          for l in ok]

                # Pool thin LFTAG values AND rows with missing LFTAG (3J extension,
                # see module docstring) into one (cy,s)-level target group.
                pooled_syn_mask = syn_cs_mask & (df["LFTAG"].isin(thin) | df["LFTAG"].isna())
                if pooled_syn_mask.any():
                    groups.append(("pooled", obs_cs_mask, pooled_syn_mask))   # obs ref = whole (cy,s) cell
                    n_syn_rows_pooled += int(pooled_syn_mask.sum())

            for label, obs_g_mask, syn_g_mask in groups:
                obs_g_idx = df.index[obs_g_mask].tolist()
                syn_g_idx = df.index[syn_g_mask].tolist()
                if not obs_g_idx or not syn_g_idx:
                    continue
                n_moved_g = _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, wrk_p, rng)
                total_moves += n_moved_g
                print(f"  cy={cy} s={s} LFTAG={label}: {len(syn_g_idx)} syn rows, "
                      f"{n_moved_g:,} act30 moves", flush=True)

    pooling_rate_cells_pct = (100.0 * n_cells_thin / n_cells_total) if n_cells_total else float("nan")
    pooling_rate_rows_pct  = (100.0 * n_syn_rows_pooled / n_syn_rows_seen) if n_syn_rows_seen else float("nan")

    print(f"  Total act30 moves: {total_moves:,}", flush=True)
    print(f"  LFTAG pooling rate (cells, i.e. distinct LFTAG values sparsity-gated "
          f"across all cy x s cells): {pooling_rate_cells_pct:.1f}% ({n_cells_thin}/{n_cells_total})",
          flush=True)
    print(f"  LFTAG pooling rate (syn rows routed into a pooled group, incl. NaN LFTAG): "
          f"{pooling_rate_rows_pct:.1f}% ({n_syn_rows_pooled:,}/{n_syn_rows_seen:,})", flush=True)
    if pooling_rate_cells_pct > 50.0:
        print("  *** FLAG: >50% of (cy,s,LFTAG) cells pooled up -- report to manager, "
              "do not switch design unilaterally (OD-I2). ***", flush=True)

    return total_moves, {
        "lftag_dropped": lftag_drop_log,
        "n_cells_total": n_cells_total,
        "n_cells_thin": n_cells_thin,
        "pooling_rate_cells_pct": pooling_rate_cells_pct,
        "n_syn_rows_seen": n_syn_rows_seen,
        "n_syn_rows_pooled": n_syn_rows_pooled,
        "pooling_rate_rows_pct": pooling_rate_rows_pct,
    }


# ── 04P-style work-state decomposition (inline, mirrors 3rdJ_04P_work_wrk30_discordance.py) ──

def _measure_work_state(df: pd.DataFrame) -> dict:
    """Work-activity slot decomposition: AT-WORK / TELEWORK / FLOATING, mirroring
    3rdJ_04P_work_wrk30_discordance.py's measure() exactly."""
    if len(df) == 0:
        return {"n": 0, "n_work": 0}
    a = df[ACT_COLS].to_numpy(dtype=float)
    h = df[HOM_COLS].to_numpy(dtype=float)
    w = df[WRK_COLS].to_numpy(dtype=float)
    work = (a == WORK_CAT)
    n_work = int(work.sum())
    out = {"n": len(df), "n_work": n_work}
    if n_work == 0:
        return out
    atwork   = int((work & (w == 1)).sum())
    telework = int((work & (w == 0) & (h == 1)).sum())
    floating = int((work & (w == 0) & (h == 0)).sum())
    out.update({
        "atwork_pct":   round(100.0 * atwork / n_work, 3),
        "telework_pct": round(100.0 * telework / n_work, 3),
        "floating_pct": round(100.0 * floating / n_work, 3),
    })
    return out


# ── CLI / main ─────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Step 4T (Leg-2): act30 conditional re-rake on the final (hom30,wrk30) state"
    )
    p.add_argument("--in_csv", required=True,
                   help="Input augmented_diaries.csv (post-04M, e.g. R5_raked_mindwell/)")
    p.add_argument("--out_dir", required=True,
                   help="Output dir (NEW dir -- never the input's dir), e.g. R5_raked_mindwell_actv2/")
    p.add_argument("--seed", type=int, default=42, help="RNG seed (default 42, matches 2J/04L convention)")
    p.add_argument("--smoke", action="store_true",
                   help="Stratified subsample (by CYCLE_YEAR x DDAY_STRATA x IS_SYNTHETIC) for a fast local smoke run")
    p.add_argument("--smoke_frac", type=float, default=0.05,
                   help="Fraction sampled per stratum in --smoke mode (default 0.05)")
    return p.parse_args()


def _stratified_smoke_sample(df: pd.DataFrame, frac: float, seed: int) -> pd.DataFrame:
    """Deterministic stratified subsample by (CYCLE_YEAR, DDAY_STRATA, IS_SYNTHETIC),
    keeping at least min(len(group), 50) rows per stratum so every cell in the rake
    grid still has usable obs/syn rows in smoke mode."""
    def _sample_group(g):
        n = max(50, int(round(len(g) * frac)))
        n = min(n, len(g))
        return g.sample(n=n, random_state=seed)
    out = (df.groupby(["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"], group_keys=False)
             .apply(_sample_group))
    return out.reset_index(drop=True)


def main() -> None:
    args = parse_args()

    print("=" * 70)
    print("3rdJ_04T_act_rake_2split.py -- act30 conditional re-rake (3-way state)")
    print(f"  in_csv     : {args.in_csv}")
    print(f"  out_dir    : {args.out_dir}")
    print(f"  seed       : {args.seed}")
    print(f"  smoke      : {args.smoke} (frac={args.smoke_frac})")
    print("=" * 70)

    print("\nLoading CSV ...", flush=True)
    df = pd.read_csv(args.in_csv, low_memory=False)
    print(f"  Rows: {len(df):,}   Cols: {len(df.columns):,}")

    required = HOM_COLS[:1] + WRK_COLS[:1] + ACT_COLS[:1] + \
        ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s) in input CSV: {missing}")

    if args.smoke:
        print(f"\n[SMOKE] Stratified subsample @ frac={args.smoke_frac} (seed={args.seed}) ...")
        df = _stratified_smoke_sample(df, args.smoke_frac, args.seed)
        print(f"  Smoke rows: {len(df):,}")

    # Snapshot hom30/wrk30 BEFORE the rake -- must come out byte-identical.
    hom_before = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = df[WRK_COLS].to_numpy(dtype=float, copy=True)

    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_mask = df["IS_SYNTHETIC"] == 1
    print(f"\n  Observed rows: {int(obs_mask.sum()):,}   Synthetic rows: {int(syn_mask.sum()):,}")

    print("\n--- Before (04P-style decomposition) ---")
    before_obs = _measure_work_state(df.loc[obs_mask])
    before_syn = _measure_work_state(df.loc[syn_mask])
    print(f"  OBS : n_work={before_obs.get('n_work', 0):,}  "
          f"AT-WORK={before_obs.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_obs.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={before_obs.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_work={before_syn.get('n_work', 0):,}  "
          f"AT-WORK={before_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_syn.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={before_syn.get('floating_pct', float('nan')):.2f}%")

    print("\n--- Running conditional rake ---", flush=True)
    rng = np.random.default_rng(args.seed)
    total_moves, diag = _run_act30_conditional_rake(
        df, ACT_COLS, HOM_COLS, WRK_COLS, obs_mask, syn_mask, rng
    )

    print("\n--- After (04P-style decomposition) ---")
    after_obs = _measure_work_state(df.loc[obs_mask])
    after_syn = _measure_work_state(df.loc[syn_mask])
    print(f"  OBS : n_work={after_obs.get('n_work', 0):,}  "
          f"AT-WORK={after_obs.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={after_obs.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={after_obs.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_work={after_syn.get('n_work', 0):,}  "
          f"AT-WORK={after_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={after_syn.get('telework_pct', float('nan')):.2f}%  "
          f"FLOATING={after_syn.get('floating_pct', float('nan')):.2f}%")

    # ── Guardrail: hom30/wrk30 byte-identical ──────────────────────────────────
    hom_after = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    hom_identical = np.array_equal(hom_before, hom_after)
    wrk_identical = np.array_equal(wrk_before, wrk_after)
    print(f"\n  hom30 byte-identical to input: {hom_identical}")
    print(f"  wrk30 byte-identical to input: {wrk_identical}")
    if not (hom_identical and wrk_identical):
        raise RuntimeError(
            "INVARIANT VIOLATION: hom30/wrk30 changed during the act30 rake. "
            "Aborting write -- this script must only touch act30_*."
        )

    # ── Atomic write ─────────────────────────────────────────────────────────
    os.makedirs(args.out_dir, exist_ok=True)
    out_name = "augmented_diaries_SMOKE.csv" if args.smoke else "augmented_diaries.csv"
    out_path = os.path.join(args.out_dir, out_name)
    tmp_path = out_path + ".tmp"
    print(f"\nWriting -> {out_path}", flush=True)
    df.to_csv(tmp_path, index=False)
    n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1   # exclude header
    if n_written != len(df):
        raise RuntimeError(
            f"Row count mismatch writing {tmp_path}: wrote {n_written}, expected {len(df)}"
        )
    os.replace(tmp_path, out_path)
    print(f"  Wrote {len(df):,} rows -> {out_path}")

    # ── Provenance JSON (mirrors g2ow1_rake_provenance.json conventions) ──────
    prov_name = "act30_rake_provenance_SMOKE.json" if args.smoke else "act30_rake_provenance.json"
    prov_path = os.path.join(args.out_dir, prov_name)
    provenance = {
        "_meta": {
            "script": "3rdJ_04T_act_rake_2split.py",
            "in_csv": os.path.abspath(args.in_csv),
            "out_csv": os.path.abspath(out_path),
            "seed": args.seed,
            "smoke": args.smoke,
            "smoke_frac": args.smoke_frac if args.smoke else None,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "min_obs_for_lftag": MIN_OBS_FOR_LFTAG,
            "total_act30_moves": total_moves,
            "hom30_byte_identical": bool(hom_identical),
            "wrk30_byte_identical": bool(wrk_identical),
        },
        "lftag_pooling": {
            "n_cells_total": diag["n_cells_total"],
            "n_cells_thin": diag["n_cells_thin"],
            "pooling_rate_cells_pct": round(diag["pooling_rate_cells_pct"], 2)
            if not np.isnan(diag["pooling_rate_cells_pct"]) else None,
            "n_syn_rows_seen": diag["n_syn_rows_seen"],
            "n_syn_rows_pooled": diag["n_syn_rows_pooled"],
            "pooling_rate_rows_pct": round(diag["pooling_rate_rows_pct"], 2)
            if not np.isnan(diag["pooling_rate_rows_pct"]) else None,
            "lftag_dropped": diag["lftag_dropped"],
        },
        "work_state_decomposition": {
            "obs_before": before_obs, "obs_after": after_obs,
            "syn_before": before_syn, "syn_after": after_syn,
        },
    }
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, default=str)
    print(f"  Wrote provenance -> {prov_path}")

    print(f"\nOK 04T complete. Total act30 moves: {total_moves:,}")
    print("=" * 70)


if __name__ == "__main__":
    main()
