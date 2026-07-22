# -*- coding: utf-8 -*-
"""
3rdJ_04T_act_rake_4split.py — Step 4T (Leg-3, four-split): act30 Conditional Re-Rake.

Forked from Leg-2's 3rdJ_04T_act_rake_2split.py (see that file's docstring for full
lineage back to 2J's 05_postlink_rake.py). Extends the 3-way occupancy state
(WORK / HOME / NEITHER) to a 4-way state that adds AT_RETAIL, per the Leg-3 design
freeze Delta H (3rdJ_04_augmentationGSS_4split.md, "Post-hoc chain: 3-channel rake +
min-dwell + 4-way act-rake").

Closes Gate GA (FLOATING-rate excess) by re-raking the 14-category act30_* activity
channel CONDITIONALLY on the final (hom30, wrk30, ret30) occupancy state, WITHOUT
touching the binary hom30/wrk30/ret30 channels themselves. Run AFTER
3rdJ_04M_mindwell_4split.py — 04M edits hom30/wrk30/ret30 only; if act30 were
conditioned before 04M, the smoother would re-break the conditioning it depends on.

Background: 3rdJ_04L_joint_rake_4split.py rakes hom30/wrk30/ret30 to match observed
per-(CYCLE_YEAR x DDAY_STRATA x slot) marginals (3-channel exclusive rake) but carries
act30 forward untouched. Result: many synthetic slots say "activity = Work" (act30==1)
or "activity = Shopping" (act30==4) while the person's raked physical state does not
support that activity label — the physically-impossible FLOATING state
(3rdJ_04P_discordance_4split.py). Work activity while hom30=1 (TELEWORK) is legitimate
and is this paper's core WFH signal; it must be preserved, never zeroed. Likewise,
shopping activity while hom30=1 (e.g. online ordering) or wrk30=1 (e.g. workplace
purchasing) is not zeroed — this script only rakes TOWARD the observed distribution,
never hard-locks a state to a single category.

Method — ported from Leg-2's 3-way extension of 2J's proven fix
(2J_docs_occ_nTemp/05_postlink_rake.py:118-319: _round_to_sum, _rake_categorical_slot,
_rake_act_group, _run_act30_conditional_rake), further extended from Leg-2's 3-way
hom30/wrk30/neither conditioning to a 4-way occupancy state:
    STATE_WORK    (wrk30==1)                              -> rake to observed AT-WORK
                                                              act mix
    STATE_RETAIL  (wrk30!=1 & ret30==1)                    -> rake to observed
                                                              AT-RETAIL act mix
                                                              (naturally concentrates on
                                                              act30==RETAIL_CAT; NO hard
                                                              lock)
    STATE_HOME    (wrk30!=1 & ret30!=1 & hom30==1)         -> rake to observed AT-HOME
                                                              act mix (contains
                                                              legitimate TELEWORK share
                                                              -- never zeroed)
    STATE_NEITHER (wrk30!=1 & ret30!=1 & hom30!=1)         -> rake to observed NEITHER
                                                              act mix (near-zero
                                                              work/shopping share -- this
                                                              is the mechanism that
                                                              closes Gate GA; no hard
                                                              lock on act30==Work or
                                                              act30==Shopping)

State priority (deterministic tie-break): WORK > RETAIL > HOME > NEITHER. 04L's
3-channel exclusive joint rake guarantees hom30/wrk30/ret30 mutual exclusivity
(overlap ~= 0 by construction), so this ordering is a deterministic safety net for the
residual near-zero overlap, not an expected code path.

Cell = (CYCLE_YEAR x DDAY_STRATA x slot x LFTAG-or-pooled), with 2J's MIN_OBS_FOR_LFTAG
sparsity gate pooling thin LFTAG cells up to the (CYCLE_YEAR, DDAY_STRATA)-level target
(OD-I2, resolved 2026-07-15: keep 2J's design, do not switch). 3J's NaN-LFTAG pool-up
extension (rows with LFTAG==NaN folded into the pooled group) carries forward unchanged
from Leg-2's 04T.

Only act30_* columns are ever written. hom30_*/wrk30_*/ret30_* are read-only inputs
throughout and come out of this script byte-identical to the input CSV (RuntimeError
raised before any write if that invariant is violated).

Usage:
    py -3 3rdJ_04T_act_rake_4split.py \
        --in_csv  outputs_step4/sweep/<BASE>_raked3_mindwell/augmented_diaries.csv \
        --out_dir outputs_step4/sweep/<BASE>_raked3_mindwell_actv \
        [--seed 42] [--smoke] [--smoke_frac 0.05]

Dependencies: pandas, numpy (no other non-stdlib requirements).
Build: 2026-07-20 (employee, Claude Sonnet 5) — forked from Leg-2 3rdJ_04T_act_rake_2split.py.
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
RET_COLS = [f"ret30_{s:03d}" for s in range(1, N_SLOTS + 1)]   # Leg-3: lowercase ret30_*
                                                                 # diary-pool naming --
                                                                 # distinct from Step-3's
                                                                 # RETL30_* tiler columns.
ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]

# act30 category range: 1..14 inclusive (matches 04F_validation.py / 2J convention).
ACT_MIN = 1
ACT_MAX = 14
ACT_CATEGORIES = list(range(ACT_MIN, ACT_MAX + 1))
WORK_CAT = 1
# Diagnostic-only constant (04P-style decomposition / provenance reporting).
# NEVER used as a rake target -- the rake always draws from the OBSERVED
# state-conditioned act30 distribution, never a hard-coded category.
RETAIL_CAT = 4   # "Purchasing Goods & Services" (act30/occACT 1..14 scheme).

# Sparsity guard, ported unchanged from 2J 05_postlink_rake.py:66.
MIN_OBS_FOR_LFTAG = 30

# ── 4-way occupancy state (derived from hom30/wrk30/ret30; NEVER mutated by this
#    script) ───────────────────────────────────────────────────────────────────
STATE_NEITHER = 0   # hom30==0 & wrk30==0 & ret30==0  -> FLOATING when act30 is
                     #   Work/Shopping-coded
STATE_HOME    = 1   # hom30==1 & wrk30==0 & ret30==0  -> includes legitimate TELEWORK
STATE_RETAIL  = 2   # ret30==1 & wrk30==0             -> AT-RETAIL
STATE_WORK    = 3   # wrk30==1                        -> AT-WORK
STATES = (STATE_WORK, STATE_RETAIL, STATE_HOME, STATE_NEITHER)
STATE_LABELS = {STATE_WORK: "WORK", STATE_RETAIL: "RETAIL", STATE_HOME: "HOME",
                STATE_NEITHER: "NEITHER"}


def _compute_state(hom_arr: np.ndarray, wrk_arr: np.ndarray, ret_arr: np.ndarray) -> np.ndarray:
    """(n, T) hom30/wrk30/ret30 float arrays -> (n, T) int8 4-way state array.

    Priority (deterministic tie-break): WORK > RETAIL > HOME > NEITHER, implemented as
    three sequential overwrites (lowest priority first, highest last -- last write
    wins for the ~0% of rows where more than one channel is simultaneously ==1).
    04L's 3-channel exclusive joint rake guarantees hom30/wrk30/ret30 mutual
    exclusivity (overlap ~= 0 by construction); this ordering is a deterministic
    safety net, not an expected code path -- mirrors the 3-way Leg-2 script's
    "both=1: 0 (expect 0)" invariant, extended to three channels."""
    state = np.zeros(hom_arr.shape, dtype=np.int8)   # default STATE_NEITHER == 0
    state[hom_arr == 1] = STATE_HOME
    state[ret_arr == 1] = STATE_RETAIL
    state[wrk_arr == 1] = STATE_WORK
    return state


# ── Ported verbatim from 2J 05_postlink_rake.py:118-144 (via Leg-2 04T) ──────────

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


# ── Ported verbatim from 2J 05_postlink_rake.py:147-207 (via Leg-2 04T) ──────────

def _rake_categorical_slot(cur_vals, target_counts, categories, left_vals, right_vals, rng):
    """14-way minimal-move categorical rake for one (cell, slot) subset.
    Computes per-category deficit/surplus vs `target_counts`, moves the minimum
    number of records surplus-category -> deficit-category. Records whose
    neighbouring slot (left_vals/right_vals -- same records, adjacent time slots,
    pre-filtered by the caller to NaN-out neighbours that do not share the current
    4-way state) already holds the destination category are preferred (extends
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


# ── 4-way extension of Leg-2's 3-way _rake_act_group ─────────────────────────────

def _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, wrk_p, ret_p, rng,
                     categories=ACT_CATEGORIES):
    """Runs the 48-slot act30 categorical rake for one (cy x stratum x LFTAG-or-
    pooled) group. Each slot is split into 4-way (WORK / RETAIL / HOME / NEITHER)
    subsets BEFORE raking, and each subset is raked independently against the
    matching state-conditioned observed target -- this guarantees a record's
    activity code can only be drawn from the observed distribution of records that
    share its OWN current 4-way physical state at that exact slot. hom30/wrk30/ret30
    are read-only here (never mutated). Mutates df in place (act_p columns,
    syn_g_idx rows only). Returns total records moved across all 48 slots."""
    if not syn_g_idx or not obs_g_idx:
        return 0

    act_arr     = df.loc[syn_g_idx, act_p].values.astype(float)   # (n_g, 48) -- mutated locally
    hom_arr_syn = df.loc[syn_g_idx, hom_p].values.astype(float)
    wrk_arr_syn = df.loc[syn_g_idx, wrk_p].values.astype(float)
    ret_arr_syn = df.loc[syn_g_idx, ret_p].values.astype(float)
    obs_act_arr = df.loc[obs_g_idx, act_p].values.astype(float)
    obs_hom_arr = df.loc[obs_g_idx, hom_p].values.astype(float)
    obs_wrk_arr = df.loc[obs_g_idx, wrk_p].values.astype(float)
    obs_ret_arr = df.loc[obs_g_idx, ret_p].values.astype(float)

    state_syn = _compute_state(hom_arr_syn, wrk_arr_syn, ret_arr_syn)   # (n_g, 48) int8
    state_obs = _compute_state(obs_hom_arr, obs_wrk_arr, obs_ret_arr)

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
            # this same 4-way state st -- generalizes Leg-2's 3-way state gate
            # (its own generalization of 2J's 2-way hom-status gate) so a neighbour
            # in a DIFFERENT physical state must not bias this state's rake toward
            # extending a run across a hom/wrk/ret state transition.
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


# ── 4-way extension of Leg-2's _run_act30_conditional_rake ───────────────────────

def _run_act30_conditional_rake(df, act_p, hom_p, wrk_p, ret_p, obs_mask, syn_mask, rng):
    """Step: 14-way act30 rake per (CYCLE_YEAR x DDAY_STRATA x slot x LFTAG
    [sparsity-gated, <MIN_OBS_FOR_LFTAG obs -> pooled to (cy,s)-level target]), run
    SEPARATELY for the WORK / RETAIL / HOME / NEITHER 4-way state of each cell
    (inside _rake_act_group) so activity codes never cross a physical-state
    boundary.

    Leg-3 extension vs Leg-2: adds the ret_p (ret30_*) channel to the state
    computation (3-way -> 4-way); the CYCLE_YEAR outer loop and NaN-LFTAG pool-up
    (rows with LFTAG==NaN folded into the pooled group alongside sparsity-thin
    LFTAG values) both carry forward unchanged from Leg-2's 04T.

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
                n_moved_g = _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, wrk_p, ret_p, rng)
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


# ── 04P-style work-state decomposition (inline, mirrors 3rdJ_04P_discordance_4split.py) ──

def _measure_work_state(df: pd.DataFrame) -> dict:
    """Work-activity slot decomposition: AT-WORK / TELEWORK / RETAIL-incompatible /
    FLOATING, mirroring 3rdJ_04P_discordance_4split.py's measure() exactly (Leg-3's
    4-way extension of Leg-2's AT-WORK/TELEWORK/FLOATING 3-way decomposition; buckets
    stay mutually exclusive by construction given upstream hom30/wrk30/ret30
    exclusivity)."""
    if len(df) == 0:
        return {"n": 0, "n_work": 0}
    a = df[ACT_COLS].to_numpy(dtype=float)
    h = df[HOM_COLS].to_numpy(dtype=float)
    w = df[WRK_COLS].to_numpy(dtype=float)
    r = df[RET_COLS].to_numpy(dtype=float)
    work = (a == WORK_CAT)
    n_work = int(work.sum())
    out = {"n": len(df), "n_work": n_work}
    if n_work == 0:
        return out
    atwork           = int((work & (w == 1)).sum())
    telework         = int((work & (w != 1) & (h == 1)).sum())
    retail_incompat  = int((work & (w != 1) & (h != 1) & (r == 1)).sum())
    floating         = int((work & (w != 1) & (h != 1) & (r != 1)).sum())
    out.update({
        "atwork_pct":           round(100.0 * atwork / n_work, 3),
        "telework_pct":         round(100.0 * telework / n_work, 3),
        "retail_incompat_pct":  round(100.0 * retail_incompat / n_work, 3),
        "floating_pct":         round(100.0 * floating / n_work, 3),
    })
    return out


def _measure_retail_state(df: pd.DataFrame) -> dict:
    """Shopping-activity slot decomposition (RETAIL_CAT, diagnostic-only, symmetric
    counterpart to _measure_work_state): AT-RETAIL / HOME-SHOPPING / WORK-SHOPPING /
    FLOATING. Not part of the GA-3 gate; reported in provenance for completeness.
    RETAIL_CAT is used ONLY here and in printouts -- never as a rake target."""
    if len(df) == 0:
        return {"n": 0, "n_shop": 0}
    a = df[ACT_COLS].to_numpy(dtype=float)
    h = df[HOM_COLS].to_numpy(dtype=float)
    w = df[WRK_COLS].to_numpy(dtype=float)
    r = df[RET_COLS].to_numpy(dtype=float)
    shop = (a == RETAIL_CAT)
    n_shop = int(shop.sum())
    out = {"n": len(df), "n_shop": n_shop}
    if n_shop == 0:
        return out
    atretail    = int((shop & (r == 1)).sum())
    home_shop   = int((shop & (r != 1) & (h == 1)).sum())
    work_shop   = int((shop & (r != 1) & (h != 1) & (w == 1)).sum())
    floating    = int((shop & (r != 1) & (h != 1) & (w != 1)).sum())
    out.update({
        "atretail_pct":   round(100.0 * atretail / n_shop, 3),
        "home_shop_pct":  round(100.0 * home_shop / n_shop, 3),
        "work_shop_pct":  round(100.0 * work_shop / n_shop, 3),
        "floating_pct":   round(100.0 * floating / n_shop, 3),
    })
    return out


# ── CLI / main ─────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Step 4T (Leg-3): act30 conditional re-rake on the final (hom30,wrk30,ret30) state"
    )
    p.add_argument("--in_csv", required=True,
                   help="Input augmented_diaries.csv (post-04M, e.g. <BASE>_raked3_mindwell/)")
    p.add_argument("--out_dir", required=True,
                   help="Output dir (NEW dir -- never the input's dir), e.g. <BASE>_raked3_mindwell_actv/")
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
    print("3rdJ_04T_act_rake_4split.py -- act30 conditional re-rake (4-way state)")
    print(f"  in_csv     : {args.in_csv}")
    print(f"  out_dir    : {args.out_dir}")
    print(f"  seed       : {args.seed}")
    print(f"  smoke      : {args.smoke} (frac={args.smoke_frac})")
    print("=" * 70)

    print("\nLoading CSV ...", flush=True)
    df = pd.read_csv(args.in_csv, low_memory=False)
    print(f"  Rows: {len(df):,}   Cols: {len(df.columns):,}")

    required = HOM_COLS[:1] + WRK_COLS[:1] + RET_COLS[:1] + ACT_COLS[:1] + \
        ["CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s) in input CSV: {missing}")

    if args.smoke:
        print(f"\n[SMOKE] Stratified subsample @ frac={args.smoke_frac} (seed={args.seed}) ...")
        df = _stratified_smoke_sample(df, args.smoke_frac, args.seed)
        print(f"  Smoke rows: {len(df):,}")

    # Snapshot hom30/wrk30/ret30 BEFORE the rake -- must come out byte-identical.
    hom_before = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_before = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    ret_before = df[RET_COLS].to_numpy(dtype=float, copy=True)

    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_mask = df["IS_SYNTHETIC"] == 1
    print(f"\n  Observed rows: {int(obs_mask.sum()):,}   Synthetic rows: {int(syn_mask.sum()):,}")

    print("\n--- Before (04P-style decomposition) ---")
    before_obs = _measure_work_state(df.loc[obs_mask])
    before_syn = _measure_work_state(df.loc[syn_mask])
    print(f"  OBS : n_work={before_obs.get('n_work', 0):,}  "
          f"AT-WORK={before_obs.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_obs.get('telework_pct', float('nan')):.2f}%  "
          f"RETAIL-incompat={before_obs.get('retail_incompat_pct', float('nan')):.2f}%  "
          f"FLOATING={before_obs.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_work={before_syn.get('n_work', 0):,}  "
          f"AT-WORK={before_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={before_syn.get('telework_pct', float('nan')):.2f}%  "
          f"RETAIL-incompat={before_syn.get('retail_incompat_pct', float('nan')):.2f}%  "
          f"FLOATING={before_syn.get('floating_pct', float('nan')):.2f}%")

    before_obs_retail = _measure_retail_state(df.loc[obs_mask])
    before_syn_retail = _measure_retail_state(df.loc[syn_mask])
    print(f"  OBS : n_shop={before_obs_retail.get('n_shop', 0):,}  "
          f"AT-RETAIL={before_obs_retail.get('atretail_pct', float('nan')):.2f}%  "
          f"FLOATING={before_obs_retail.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_shop={before_syn_retail.get('n_shop', 0):,}  "
          f"AT-RETAIL={before_syn_retail.get('atretail_pct', float('nan')):.2f}%  "
          f"FLOATING={before_syn_retail.get('floating_pct', float('nan')):.2f}%")

    print("\n--- Running conditional rake ---", flush=True)
    rng = np.random.default_rng(args.seed)
    total_moves, diag = _run_act30_conditional_rake(
        df, ACT_COLS, HOM_COLS, WRK_COLS, RET_COLS, obs_mask, syn_mask, rng
    )

    print("\n--- After (04P-style decomposition) ---")
    after_obs = _measure_work_state(df.loc[obs_mask])
    after_syn = _measure_work_state(df.loc[syn_mask])
    print(f"  OBS : n_work={after_obs.get('n_work', 0):,}  "
          f"AT-WORK={after_obs.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={after_obs.get('telework_pct', float('nan')):.2f}%  "
          f"RETAIL-incompat={after_obs.get('retail_incompat_pct', float('nan')):.2f}%  "
          f"FLOATING={after_obs.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_work={after_syn.get('n_work', 0):,}  "
          f"AT-WORK={after_syn.get('atwork_pct', float('nan')):.2f}%  "
          f"TELEWORK={after_syn.get('telework_pct', float('nan')):.2f}%  "
          f"RETAIL-incompat={after_syn.get('retail_incompat_pct', float('nan')):.2f}%  "
          f"FLOATING={after_syn.get('floating_pct', float('nan')):.2f}%")

    after_obs_retail = _measure_retail_state(df.loc[obs_mask])
    after_syn_retail = _measure_retail_state(df.loc[syn_mask])
    print(f"  OBS : n_shop={after_obs_retail.get('n_shop', 0):,}  "
          f"AT-RETAIL={after_obs_retail.get('atretail_pct', float('nan')):.2f}%  "
          f"FLOATING={after_obs_retail.get('floating_pct', float('nan')):.2f}%")
    print(f"  SYN : n_shop={after_syn_retail.get('n_shop', 0):,}  "
          f"AT-RETAIL={after_syn_retail.get('atretail_pct', float('nan')):.2f}%  "
          f"FLOATING={after_syn_retail.get('floating_pct', float('nan')):.2f}%")

    # ── Guardrail: hom30/wrk30/ret30 byte-identical ─────────────────────────────
    hom_after = df[HOM_COLS].to_numpy(dtype=float, copy=True)
    wrk_after = df[WRK_COLS].to_numpy(dtype=float, copy=True)
    ret_after = df[RET_COLS].to_numpy(dtype=float, copy=True)
    hom_identical = np.array_equal(hom_before, hom_after)
    wrk_identical = np.array_equal(wrk_before, wrk_after)
    ret_identical = np.array_equal(ret_before, ret_after)
    print(f"\n  hom30 byte-identical to input: {hom_identical}")
    print(f"  wrk30 byte-identical to input: {wrk_identical}")
    print(f"  ret30 byte-identical to input: {ret_identical}")
    if not (hom_identical and wrk_identical and ret_identical):
        raise RuntimeError(
            "INVARIANT VIOLATION: hom30/wrk30/ret30 changed during the act30 rake. "
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
            "script": "3rdJ_04T_act_rake_4split.py",
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
            "ret30_byte_identical": bool(ret_identical),
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
        "retail_state_decomposition": {
            "obs_before": before_obs_retail, "obs_after": after_obs_retail,
            "syn_before": before_syn_retail, "syn_after": after_syn_retail,
        },
    }
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2, default=str)
    print(f"  Wrote provenance -> {prov_path}")

    print(f"\nOK 04T complete. Total act30 moves: {total_moves:,}")
    print("=" * 70)


if __name__ == "__main__":
    main()
