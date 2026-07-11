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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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

# ── --joint additions (2026-07-09, Task B / Improvement 1) ────────────────────
# act30 category range: confirmed via 04F_validation.py's N_ACT=14 / activity_dist()
# clip(acts-1, 0, 13) convention -- categories are 1..14 inclusive.
ACT_MIN = 1
ACT_MAX = 14
ACT_CATEGORIES = list(range(ACT_MIN, ACT_MAX + 1))

# 9 co-presence channels, ported verbatim from step4_Speed_Cluster/04L_joint_rake_test.py
# (COP_CHANNELS there; read-only reference, not modified). Matches 04F_validation.py's
# COP_COLS exactly -- no deviation from the plan's channel list.
COP_CHANNELS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]

# Sparsity guard: (DDAY_STRATA x LFTAG) cells with fewer observed diaries than this
# are dropped from the LFTAG dimension and pooled into a stratum-level target instead.
MIN_OBS_FOR_LFTAG = 30


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


# ── --joint: categorical (14-way) minimal-move rake ────────────────────────────

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
        # Shouldn't happen with floor-based rounding, but guard anyway.
        order = sorted(categories, key=lambda c: (scaled[c] - floors[c]))
        for c in order[:(-remainder)]:
            if floors[c] > 0:
                floors[c] -= 1
    return floors


def _rake_categorical_slot(cur_vals, target_counts, categories, left_vals, right_vals, rng):
    """14-way minimal-move categorical rake for one (cell, slot) subset.
    Generalizes _rake_binary_slot to N categories: computes per-category
    deficit/surplus vs `target_counts`, moves the minimum number of records
    surplus-category -> deficit-category. Records whose neighbouring slot
    (left_vals/right_vals -- same records, adjacent time slots) already holds
    the destination category are preferred (boundary-preference analog of
    _boundary_mask: extends existing activity runs instead of creating
    isolated one-off transitions). Ties broken with `rng` (shared, seeded 42,
    never reseeded).

    cur_vals      : (n,) array of current category values (NOT mutated --
                    caller writes the returned array back into the parent
                    frame; this guarantees a record is inspected against a
                    stable per-call snapshot).
    target_counts : dict {category -> integer target count}; every entry in
                    `categories` should be present (missing treated as 0);
                    should sum to n (from _round_to_sum).
    categories    : list of all valid category codes (e.g. 1..14).
    left_vals, right_vals : (n,) arrays, neighbouring-slot activity values for
                    the SAME n records (NaN where no neighbour exists, e.g.
                    slot boundaries).
    rng           : shared np.random.default_rng.

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


def _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, rng, categories=ACT_CATEGORIES):
    """Runs the 48-slot act30 categorical rake for one (stratum x LFTAG-or-
    pooled) group. Each slot is split into hom30=1 / hom30=0 subsets BEFORE
    raking, and each subset is raked independently against the matching
    hom-conditioned observed target -- this is what guarantees home-activity
    codes never land on hom30=0 records (and vice versa): a record can only
    receive a category drawn from the observed distribution of records that
    share its OWN current hom30 value at that exact slot. Mutates df in place
    (act_p columns, syn_g_idx rows only; hom_p is read-only here). Returns
    total records moved across all 48 slots."""
    if not syn_g_idx or not obs_g_idx:
        return 0

    act_arr     = df.loc[syn_g_idx, act_p].values.astype(float)   # (n_g, 48) -- mutated locally
    hom_arr_syn = df.loc[syn_g_idx, hom_p].values.astype(float)
    obs_act_arr = df.loc[obs_g_idx, act_p].values.astype(float)
    obs_hom_arr = df.loc[obs_g_idx, hom_p].values.astype(float)

    n_g = act_arr.shape[0]
    n_moved = 0

    for t in range(N_SLOTS):
        for h in (1.0, 0.0):
            syn_rows = np.where(hom_arr_syn[:, t] == h)[0]
            if len(syn_rows) == 0:
                continue
            obs_rows = np.where(obs_hom_arr[:, t] == h)[0]
            if len(obs_rows) == 0:
                continue   # no observed reference for this (slot, hom-status) -- leave as-is
            obs_vals_t = obs_act_arr[obs_rows, t]
            obs_vals_t = obs_vals_t[~np.isnan(obs_vals_t)]
            if len(obs_vals_t) == 0:
                continue
            counts = {c: float(np.sum(obs_vals_t == c)) for c in categories}
            props  = {c: counts[c] for c in categories}   # _round_to_sum normalizes internally

            target_counts = _round_to_sum(props, categories, len(syn_rows))
            if target_counts is None:
                continue

            cur_vals = act_arr[syn_rows, t]
            # Boundary preference must only fire when the NEIGHBOURING slot shares
            # this same hom-status h -- otherwise a hom=1 (home) neighbour's activity
            # would bias the hom=0 (away) rake toward extending a "home" run across
            # the hom30 transition, defeating the whole point of the hom-status
            # split (found via the observed-population-weighted reconstruction test,
            # 2026-07-09: predicted 15.38% vs actual 18.04% pre-fix -- this closed
            # most of that 2.66pp gap in a synthetic re-check).
            if t > 0:
                left = act_arr[syn_rows, t - 1]
                left = np.where(hom_arr_syn[syn_rows, t - 1] == h, left, np.nan)
            else:
                left = np.full(len(syn_rows), np.nan)
            if t < N_SLOTS - 1:
                right = act_arr[syn_rows, t + 1]
                right = np.where(hom_arr_syn[syn_rows, t + 1] == h, right, np.nan)
            else:
                right = np.full(len(syn_rows), np.nan)

            new_vals, n_mv = _rake_categorical_slot(cur_vals, target_counts, categories, left, right, rng)
            act_arr[syn_rows, t] = new_vals
            n_moved += n_mv

    df.loc[syn_g_idx, act_p] = act_arr
    return n_moved


def _run_act30_conditional_rake(df, act_p, hom_p, obs_mask, syn_mask, rng):
    """Step 2 of --joint: 14-way act30 rake per (DDAY_STRATA x slot x LFTAG
    [sparsity-gated, <MIN_OBS_FOR_LFTAG obs -> pooled to stratum level]), run
    SEPARATELY for the hom30=1 and hom30=0 subsets of each cell (inside
    _rake_act_group) so home-activities never get assigned to away-records
    and vice versa. Returns (total_moves, diagnostics dict).

    If `df` has no "LFTAG" column at all (e.g. 06_forecast_rake.py's --joint
    reuse against 2030_synthetic_diaries.csv, which does not carry LFTAG),
    the LFTAG dimension is skipped structurally and each stratum is raked as
    a single group -- this is distinct from the sparsity guard (which pools
    specific thin LFTAG *values* within a stratum that does have the column)."""
    total_moves = 0
    lftag_drop_log = []
    has_lftag = "LFTAG" in df.columns

    lftag_vals = (sorted(v for v in df.loc[obs_mask, "LFTAG"].dropna().unique().tolist())
                  if has_lftag else [])

    for s in STRATA:
        obs_s_mask = obs_mask & (df["DDAY_STRATA"] == s)
        syn_s_mask = syn_mask & (df["DDAY_STRATA"] == s)
        if not obs_s_mask.any() or not syn_s_mask.any():
            print(f"  stratum {s}: no syn or obs rows -- skip", flush=True)
            continue

        if not has_lftag:
            groups = [("no_lftag_col", obs_s_mask, syn_s_mask)]
        else:
            obs_s_by_lftag = {l: int((obs_s_mask & (df["LFTAG"] == l)).sum()) for l in lftag_vals}
            thin = [l for l in lftag_vals if obs_s_by_lftag.get(l, 0) < MIN_OBS_FOR_LFTAG]
            ok   = [l for l in lftag_vals if l not in thin]
            if thin:
                lftag_drop_log.append((s, thin, {l: obs_s_by_lftag[l] for l in thin}))
                print(f"  stratum {s}: LFTAG {thin} sparsity-gated "
                      f"(<{MIN_OBS_FOR_LFTAG} obs diaries) -- pooled to stratum-level target", flush=True)

            groups = [(l, obs_s_mask & (df["LFTAG"] == l), syn_s_mask & (df["LFTAG"] == l)) for l in ok]
            if thin:
                pooled_syn_mask = syn_s_mask & df["LFTAG"].isin(thin)
                if pooled_syn_mask.any():
                    groups.append(("pooled", obs_s_mask, pooled_syn_mask))   # obs ref = whole stratum

        for label, obs_g_mask, syn_g_mask in groups:
            obs_g_idx = df.index[obs_g_mask].tolist()
            syn_g_idx = df.index[syn_g_mask].tolist()
            if not obs_g_idx or not syn_g_idx:
                continue
            n_moved_g = _rake_act_group(df, syn_g_idx, obs_g_idx, act_p, hom_p, rng)
            total_moves += n_moved_g
            print(f"  stratum {s} LFTAG={label}: {len(syn_g_idx)} syn rows, "
                  f"{n_moved_g:,} act30 moves", flush=True)

    print(f"  Total act30 moves: {total_moves:,}", flush=True)
    return total_moves, {"lftag_dropped": lftag_drop_log}


def _run_cop_rake(df, obs_mask, syn_mask, rng):
    """Step 3 of --joint: 9-channel co-presence rake, ported from 04L Step 2
    (standalone per-(DDAY_STRATA x slot) binary marginal -- NOT conditional on
    hom30, matching 04K's per-slot measurement approach). Replaces the dormant
    Spouse30-only Step 3. Binarizes synthetic COP at 0.5 first (soft prob ->
    hard 0/1, same fix as 04L / the existing Spouse step), then minimal-flip
    rakes each channel independently; skips any (channel, cell, slot) whose
    observed target is NaN (colleagues is NaN for 2005/2010 diaries)."""
    diag = {"channels": {}}

    channel_cols = {}
    all_cop_cols = []
    for ch in COP_CHANNELS:
        cols = [f"{ch}30_{t:03d}" for t in range(1, N_SLOTS + 1)]
        present = [c for c in cols if c in df.columns]
        if present:
            channel_cols[ch] = present
            all_cop_cols.extend(present)

    if not channel_cols:
        print("  No COP columns found -- skip", flush=True)
        return 0, diag

    print(f"  COP channels found: {list(channel_cols.keys())}", flush=True)

    syn_soft = df.loc[syn_mask, all_cop_cols].to_numpy(dtype=float)
    df.loc[syn_mask, all_cop_cols] = (np.nan_to_num(syn_soft, nan=0.0) >= 0.5).astype(float)

    total_flips = 0
    for ch, cols in channel_cols.items():
        ch_flips = 0
        for s in STRATA:
            obs_s_mask = obs_mask & (df["DDAY_STRATA"] == s)
            syn_s_mask = syn_mask & (df["DDAY_STRATA"] == s)
            obs_s_idx  = df.index[obs_s_mask].tolist()
            syn_s_idx  = df.index[syn_s_mask].tolist()
            if not obs_s_idx or not syn_s_idx:
                continue

            obs_rates = np.nanmean(df.loc[obs_s_idx, cols].values.astype(float), axis=0)
            cop_arr   = df.loc[syn_s_idx, cols].values.astype(float)
            n_s       = len(syn_s_idx)

            for t in range(len(cols)):
                if np.isnan(obs_rates[t]):
                    continue   # skip -- no observed reference (e.g. colleagues, 2005/2010)
                tgt = max(0, min(n_s, int(round(obs_rates[t] * n_s))))
                bnd = _boundary_mask(cop_arr, t)
                ch_flips += _rake_binary_slot(cop_arr[:, t], tgt, bnd, rng)

            df.loc[syn_s_idx, cols] = cop_arr

        total_flips += ch_flips
        diag["channels"][ch] = ch_flips
        print(f"  channel={ch:12s}: {ch_flips:,} flips", flush=True)

    print(f"  Total COP flips: {total_flips:,}", flush=True)
    return total_flips, diag


# ── --joint diagnostics (report-only, not gates yet) ───────────────────────────

def _transition_matrix(act_arr, categories=ACT_CATEGORIES):
    """(n, T) act30 array -> normalized 14x14 slot-to-slot transition frequency
    matrix (row=from-category, col=to-category), pooled over all 47 adjacent
    slot pairs."""
    n_cat = len(categories)
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    mat = np.zeros((n_cat, n_cat))
    T = act_arr.shape[1]
    for t in range(T - 1):
        a = act_arr[:, t]
        b = act_arr[:, t + 1]
        valid = ~np.isnan(a) & ~np.isnan(b)
        ai = np.array([cat_to_idx.get(v, -1) for v in a[valid]])
        bi = np.array([cat_to_idx.get(v, -1) for v in b[valid]])
        keep = (ai >= 0) & (bi >= 0)
        if not keep.any():
            continue
        idx = ai[keep] * n_cat + bi[keep]
        mat += np.bincount(idx, minlength=n_cat * n_cat).reshape(n_cat, n_cat)
    total = mat.sum()
    return mat / total if total > 0 else mat


def _coherence_pct(hom_arr, act_arr, home_acts=HOME_ACTS):
    """% of (hom30==0) synthetic slot-records whose act30 is a home activity
    -- the global incoherence rate (not just newly-flipped records)."""
    away_mask = (hom_arr == 0.0)
    total_away = int(away_mask.sum())
    if total_away == 0:
        return 0.0
    bad = int(np.isin(act_arr[away_mask], list(home_acts)).sum())
    return bad / total_away * 100.0


def _cop_cell_slot_max_gap(df, obs_mask, syn_mask, channel_cols):
    """Max |gap| pp across (DDAY_STRATA x channel x slot), standalone per-slot
    marginal -- same metric as 04L's _cop_slot_max_gap, generalized over
    STRATA cells instead of CYCLE_YEARxSTRATA (this file has no per-row
    CYCLE_YEAR grouping in its existing hom30 rake either)."""
    max_gap = 0.0
    for s in STRATA:
        obs_s = df.loc[obs_mask & (df["DDAY_STRATA"] == s)]
        syn_s = df.loc[syn_mask & (df["DDAY_STRATA"] == s)]
        if len(obs_s) == 0 or len(syn_s) == 0:
            continue
        for ch, cols in channel_cols.items():
            obs_ps = np.nanmean(obs_s[cols].values.astype(float), axis=0)
            syn_ps = np.nanmean(syn_s[cols].values.astype(float), axis=0)
            gaps = np.abs(syn_ps - obs_ps) * 100.0
            valid = gaps[~np.isnan(gaps)]
            if len(valid):
                max_gap = max(max_gap, float(valid.max()))
    return max_gap


def _lftag_work_share_gap(df, obs_mask, syn_mask, act_p):
    """Per-LFTAG paid-work share (act30==1) gap, obs vs syn -- same measure as
    04F_validation.py gate 6.2's work_prop, broken out per LFTAG level."""
    def work_prop(mask, lftag):
        sub = df.loc[mask & (df["LFTAG"] == lftag), act_p]
        if len(sub) == 0:
            return float("nan")
        return float((sub.values == 1).mean())

    lftags = sorted(v for v in df.loc[obs_mask, "LFTAG"].dropna().unique().tolist())
    gaps = {}
    for l in lftags:
        wo = work_prop(obs_mask, l)
        ws = work_prop(syn_mask, l)
        gap = abs(wo - ws) * 100.0 if not (np.isnan(wo) or np.isnan(ws)) else float("nan")
        gaps[l] = {"obs_pct": wo * 100.0, "syn_pct": ws * 100.0, "gap_pp": gap}
    return gaps


def _print_joint_diagnostics(df, obs_mask, syn_mask, syn_idx, act_p, hom_p,
                              channel_cols, act_pre, hom_pre):
    """Prints the diagnostics Task B's plan specifies -- report-only, not
    gated yet: per-cell-slot COP max, coherence % before/after, act30
    transition-matrix drift, per-LFTAG work-share gap."""
    print("\n" + "=" * 72, flush=True)
    print("JOINT-RAKE DIAGNOSTICS (report-only -- not gates yet)", flush=True)
    print("=" * 72, flush=True)

    # Per-cell-slot COP max (post-rake only -- pre-rake COP state wasn't
    # binarized/snapshotted separately here; see 04L for the isolated pre/post
    # COP comparison on a single model).
    if channel_cols:
        cop_max_post = _cop_cell_slot_max_gap(df, obs_mask, syn_mask, channel_cols)
        print(f"\n  Per-cell-slot COP max gap (post-rake): {cop_max_post:.3f} pp "
              f"(target < 19.85 pp)", flush=True)

    # Coherence % before/after
    act_post = df.loc[syn_idx, act_p].values.astype(float)
    hom_post = df.loc[syn_idx, hom_p].values.astype(float)
    coh_pre  = _coherence_pct(hom_pre, act_pre)
    coh_post = _coherence_pct(hom_post, act_post)
    print(f"\n  Coherence (hom30==0 slot-records with act30 in HOME_ACTS):", flush=True)
    print(f"    pre  (post-Step1, pre-act/COP rake): {coh_pre:.3f}%", flush=True)
    print(f"    post (post-Steps2-3):                {coh_post:.3f}%", flush=True)
    print(f"    Δ: {coh_post - coh_pre:+.3f} pp  (target: below current ~1.8-2.1% baseline)", flush=True)

    # act30 transition-matrix drift
    trans_pre  = _transition_matrix(act_pre)
    trans_post = _transition_matrix(act_post)
    drift = float(np.abs(trans_post - trans_pre).mean())
    print(f"\n  act30 transition-matrix drift (mean |Δ| of 14x14 slot-to-slot "
          f"frequency matrix, synthetic pre vs post): {drift:.6f}", flush=True)
    print(f"    (no threshold -- evidence for OD-2, convergence/coherence trade-off)", flush=True)

    # Per-LFTAG work-share gap
    gaps = _lftag_work_share_gap(df, obs_mask, syn_mask, act_p)
    print(f"\n  Per-LFTAG paid-work share (act30==1), obs vs syn (post-rake):", flush=True)
    for l, g in gaps.items():
        print(f"    LFTAG={l}: obs={g['obs_pct']:.2f}%  syn={g['syn_pct']:.2f}%  "
              f"gap={g['gap_pp']:.2f} pp", flush=True)

    print("=" * 72, flush=True)


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


# ── --joint pipeline (Task B / Improvement 1, 2026-07-09) ──────────────────────
#
# Fully separate from main() by design: main() above is left byte-for-byte
# untouched so the default (no-args) path is guaranteed unchanged. main_joint()
# duplicates the small Step-1 hom30-rake block (same algorithm/order/constants
# as main()'s Step 1 -- this mirrors the codebase's existing convention of
# duplicating _boundary_mask/_rake_binary_slot between this file and
# 06_forecast_rake.py rather than cross-importing low-level helpers) and then
# runs the new act30-conditional (Step 2) and 9-channel COP (Step 3) rakes,
# replacing the dormant Spouse30-only Step 3 for this path only.
#
# NOTE: this function is implemented and unit-tested (see _test_joint_rake_toy.py)
# but per the Task-B scope for this session has NOT been run against the real
# 21CEN22GSS_aug_Full_Schedules.csv -- that full run is a separate later step
# (B4 in the Live progress checklist), gated on Task A's linked population
# being fully validated first.

def main_joint():
    print("=" * 72, flush=True)
    print("05_postlink_rake.py --joint - Phase 8B-5b JOINT 3-Head Calibration", flush=True)
    print("=" * 72, flush=True)
    print(f"  Full_Schedules : {_FULL_SCHED_PATH}", flush=True)
    print(f"  Matched_Keys   : {_MATCHED_KEYS_PATH}", flush=True)

    print(f"\nLoading {_FULL_SCHED_PATH.name} ...", flush=True)
    df = pd.read_csv(str(_FULL_SCHED_PATH), low_memory=False)
    n_total = len(df)
    print(f"  {n_total:,} rows x {df.shape[1]} cols", flush=True)
    assert n_total == EXPECTED_ROWS, f"Row count {n_total} != {EXPECTED_ROWS}"

    if "DDAY_STRATA" not in df.columns:
        print("  DDAY_STRATA absent, merging from Matched_Keys ...", flush=True)
        keys = pd.read_csv(str(_MATCHED_KEYS_PATH), usecols=["PP_ID", "DDAY_STRATA"])
        df = df.merge(keys, on="PP_ID", how="left")

    hom_p = [c for c in HOM_COLS if c in df.columns]
    assert len(hom_p) == 48, f"Only {len(hom_p)}/48 hom30 cols found"
    hom_flat = df[hom_p].values.ravel()
    hom_flat_nn = hom_flat[~np.isnan(hom_flat)]
    assert set(np.unique(hom_flat_nn)).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 before raking"
    print("  hom30 schema OK (hard 0/1 confirmed)", flush=True)

    act_p = [c for c in ACT_COLS if c in df.columns]
    assert len(act_p) == 48, f"Only {len(act_p)}/48 act30 cols found"
    assert "LFTAG" in df.columns, "LFTAG column required for --joint act30 conditioning"

    syn_mask = df["IS_SYNTHETIC"] == 1
    obs_mask = df["IS_SYNTHETIC"] == 0
    syn_idx  = df.index[syn_mask].tolist()
    n_syn = len(syn_idx)
    n_obs = int(obs_mask.sum())
    print(f"  synthetic={n_syn:,}  observed={n_obs:,}", flush=True)

    # HH group sizes (for floor guard -- ported from main(), see below)
    hh_sizes = df.groupby("HH_ID").size().rename("_hh_size")
    df = df.merge(hh_sizes.reset_index(), on="HH_ID", how="left")

    # Pre-rake snapshot (floor guard needs pre_means; hom_syn_pre unused here,
    # act_pre/hom_pre below are the diagnostics' own separate pre-Step-2 snapshot)
    hom_syn_pre_step1 = df.loc[syn_idx, hom_p].values.astype(float).copy()
    pre_means_step1   = hom_syn_pre_step1.mean(axis=1)
    sp_single         = (df.loc[syn_idx, "_hh_size"].values == 1)

    rng = np.random.default_rng(42)

    # ── Step 1: hom30 rake (same algorithm/order as main()'s Step 1, unchanged) ─
    print("\n[Step 1] Raking hom30 per (DDAY_STRATA x slot) ...", flush=True)
    total_hom_flips = 0
    for s in STRATA:
        obs_s_mask = obs_mask & (df["DDAY_STRATA"] == s)
        syn_s_mask = syn_mask & (df["DDAY_STRATA"] == s)
        obs_s_idx  = df.index[obs_s_mask].tolist()
        syn_s_idx  = df.index[syn_s_mask].tolist()
        if not syn_s_idx or not obs_s_idx:
            print(f"  stratum {s}: no syn or obs rows -- skip", flush=True)
            continue

        obs_rates = df.loc[obs_s_idx, hom_p].values.astype(float).mean(axis=0)
        hom_arr   = df.loc[syn_s_idx, hom_p].values.astype(float)
        n_s       = len(syn_s_idx)

        for t in range(N_SLOTS):
            tgt = max(0, min(n_s, int(round(obs_rates[t] * n_s))))
            bnd = _boundary_mask(hom_arr, t)
            total_hom_flips += _rake_binary_slot(hom_arr[:, t], tgt, bnd, rng)

        df.loc[syn_s_idx, hom_p] = hom_arr
        print(f"  stratum {s}: {n_s} syn rows raked", flush=True)

    print(f"  Total hom30 flips: {total_hom_flips:,}", flush=True)

    # ── Step 1b: Floor guard (ported from main()'s Step 2, unchanged logic) ──
    # Without this, single-person synthetic HHs whose Step-1 rake dropped their
    # daily mean AT_HOME below 0.30 stay below floor -- main()'s gate 4.4
    # ("Per-HH mean AT_HOME out-of-range [0.3,1.0]") would regress under
    # --joint otherwise. Must run before the hom_after_step1 snapshot below,
    # since it's the last step allowed to touch hom30 (Steps 2-3 must not).
    print("\n[Step 1b] Floor guard for single-person synthetic HHs ...", flush=True)
    hom_syn_post_rake = df.loc[syn_idx, hom_p].values.astype(float)
    post_means_rake   = hom_syn_post_rake.mean(axis=1)

    needs_guard = (sp_single &
                   (post_means_rake < FLOOR_THRESHOLD) &
                   (pre_means_step1 >= FLOOR_THRESHOLD))
    guard_count = 0

    if needs_guard.any():
        guard_positions = np.where(needs_guard)[0]
        for pos in guard_positions:
            idx     = syn_idx[pos]
            row_hom = hom_syn_post_rake[pos].copy()
            cur_sum = row_hom.sum()
            for t in NIGHT_SLOTS_IDX:
                if cur_sum >= FLOOR_TARGET_SUM:
                    break
                if row_hom[t] == 0.0:
                    row_hom[t] = 1.0
                    cur_sum += 1.0
            df.loc[idx, hom_p] = row_hom
            guard_count += 1

    print(f"  Triggered: {guard_count} single-person HHs restored", flush=True)

    # Snapshot state right after Step 1 (+1b) -- used for (a) the hom30-unchanged
    # invariant across Steps 2-3, and (b) the diagnostics' "pre" baseline.
    hom_after_step1 = df[hom_p].copy()
    act_pre = df.loc[syn_idx, act_p].values.astype(float).copy()
    hom_pre = df.loc[syn_idx, hom_p].values.astype(float).copy()

    # ── Step 2: act30 conditional rake ──────────────────────────────────────
    print("\n[Step 2] Raking act30 per (DDAY_STRATA x slot x LFTAG "
          "[sparsity-gated]), separately for hom30=1 / hom30=0 ...", flush=True)
    total_act_moves, act_diag = _run_act30_conditional_rake(
        df, act_p, hom_p, obs_mask, syn_mask, rng)

    assert df[hom_p].equals(hom_after_step1), \
        "hom30 modified during act30 rake -- ABORT (Steps 2-3 must never touch hom30)"

    # ── Step 3: COP rake (9 channels, replaces dormant Spouse30-only step) ──
    print("\n[Step 3] Raking 9 COP channels (standalone per-(DDAY_STRATA x slot), "
          "ported from 04L Step 2) ...", flush=True)
    channel_cols = {}
    for ch in COP_CHANNELS:
        cols = [f"{ch}30_{t:03d}" for t in range(1, N_SLOTS + 1)]
        present = [c for c in cols if c in df.columns]
        if present:
            channel_cols[ch] = present
    total_cop_flips, cop_diag = _run_cop_rake(df, obs_mask, syn_mask, rng)

    assert df[hom_p].equals(hom_after_step1), \
        "hom30 modified during COP rake -- ABORT (Steps 2-3 must never touch hom30)"

    # ── Final assertions ─────────────────────────────────────────────────────
    final_hom_flat = df[hom_p].values.ravel()
    final_hom_nn   = final_hom_flat[~np.isnan(final_hom_flat)]
    assert set(np.unique(final_hom_nn)).issubset({0.0, 1.0}), \
        "hom30 not hard 0/1 after joint rake -- ABORT"
    assert len(df) == EXPECTED_ROWS, \
        f"Row count {len(df)} != {EXPECTED_ROWS} -- ABORT"
    act_flat = df[act_p].values.ravel()
    act_flat_nn = act_flat[~np.isnan(act_flat)]
    assert act_flat_nn.min() >= ACT_MIN and act_flat_nn.max() <= ACT_MAX, \
        f"act30 out of valid range [{ACT_MIN},{ACT_MAX}] after joint rake -- ABORT"
    print(f"\nAssertions: hom30 hard 0/1 OK; hom30 unchanged by Steps 2-3 OK; "
          f"row count {len(df):,} OK; act30 in [{ACT_MIN},{ACT_MAX}] OK", flush=True)

    # ── Diagnostics (print-only, not gates) ──────────────────────────────────
    _print_joint_diagnostics(df, obs_mask, syn_mask, syn_idx, act_p, hom_p,
                              channel_cols, act_pre, hom_pre)

    # ── Atomic write (same pattern as main()) ────────────────────────────────
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
    print(f"RAKED FILE WRITTEN (--joint): {n_written:,} rows -> {out_path}", flush=True)

    print("\n" + "=" * 72, flush=True)
    print("Summary (--joint):", flush=True)
    print(f"  hom30 flips total   : {total_hom_flips:,}", flush=True)
    print(f"  floor guard restorations : {guard_count}", flush=True)
    print(f"  act30 moves total   : {total_act_moves:,}", flush=True)
    print(f"  COP flips total     : {total_cop_flips:,}", flush=True)
    if act_diag.get("lftag_dropped"):
        print(f"  LFTAG sparsity-gated cells: {len(act_diag['lftag_dropped'])} "
              f"(stratum, [thin LFTAG], obs counts) -- see [Step 2] log above", flush=True)
    print("=" * 72, flush=True)
    print("ALL DONE (--joint).", flush=True)


def _parse_cli():
    import argparse
    p = argparse.ArgumentParser(
        description="05_postlink_rake.py -- post-linkage raking. "
                     "Default (no flags) = hom30-only path, unchanged from the "
                     "pre-2026-07-09 script. --joint = 3-head joint calibration "
                     "(hom30 -> act30-conditional -> 9-channel COP)."
    )
    p.add_argument("--joint", action="store_true",
                    help="Run the joint 3-head calibration pipeline instead of "
                         "the default hom30-only path.")
    return p.parse_args()


if __name__ == "__main__":
    _args = _parse_cli()
    if _args.joint:
        main_joint()
    else:
        main()
