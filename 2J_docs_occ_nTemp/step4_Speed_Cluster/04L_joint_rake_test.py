"""
04L_joint_rake_test.py — Step 4L: Joint Raking Diagnostic (AT_HOME + COP, CPU-only)

COP marginal definition: STANDALONE per-slot marginal — NOT conditional on home.
Rationale: COP channels include "colleagues" (work/out-of-home context) and 04K
treats all 9 channels as per-slot binary rates regardless of AT_HOME value.
Raking COP standalone (step 2 operates on ALL synthetic records per cell, not only
the post-step-1 home subset) is therefore consistent with 04K's measurement approach.

Joint raking order per (model × cell=cycle×stratum × slot):
  Step 1 — AT_HOME: flip minimum records to match per-slot observed home rate from
            hetus_30min.csv. Prefer boundary slots (start/end of home run); break
            ties with fixed RNG(seed=42). Observed reference: hetus_30min.csv.
  Step 2 — Each COP channel: flip minimum records to match per-slot standalone
            observed rate. Observed reference: aug[IS_SYNTHETIC==0] rows (same
            source as 04K). Boundary preference (start/end of channel run); same
            seed. Newly-homed records from step 1 participate here alongside all
            other synthetic records.

Household pairing: SKIPPED — GSS is individual-respondent data; augmented_diaries.csv
does not expose a household-member pairing key across persons. No fabrication.

Note on copresence_30min.csv: per 04I, COP columns (Alone30_*, Spouse30_*, …) live
in augmented_diaries.csv, not in copresence_30min.csv or hetus_30min.csv. This script
therefore uses aug[IS_SYNTHETIC==0] as the COP observed reference (consistent with
04K's _cop_max_gap_per_cell). copresence_30min.csv is loaded and inspected; if it
carries COP columns they are logged, but aug obs_src is used regardless for consistency.

04L reports per-slot MAX gap. 04K reports collapsed MEAN — pre-raking values here
will therefore be larger than 04K's cop_max_gap_pp. Post-raking must still collapse
toward 0 for raked channels; the probe in Step 2 verifies this slot-by-slot.

Usage:
  python 04L_joint_rake_test.py
  python 04L_joint_rake_test.py --base_dir /speed-scratch/o_iseri/occModeling
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

N_SLOTS = 48
CYCLES  = [2005, 2010, 2015, 2022]
STRATA  = [1, 2, 3]

ACT_COLS = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]

# Exact 9-channel list from 04K
COP_CHANNELS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
OLD_CYCLES = {2005, 2010}  # colleagues column = NaN in observed rows for these cycles

ATH_GATE = 3.0   # pp
COP_GATE = 5.0   # pp

# Same paths as 04K's MODELS_REL — do not change
MODELS_REL = {
    "J3":      "outputs_step4_J3/augmented_diaries.csv",
    "J5_X1":   "outputs_step4_J5_X1/augmented_diaries.csv",
    "J6_HC":   "outputs_step4_J6_HC/augmented_diaries.csv",
    "MDLM_G1": "outputs_step4_full/MDLM_G1/augmented_diaries.csv",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base_dir",          default=None,
                   help="Base dir containing outputs_step4_* dirs.")
    p.add_argument("--step3_dir",         default=None,
                   help="Step-3 outputs dir (hetus_30min.csv).")
    p.add_argument("--output_json",       default=None,
                   help="JSON destination for full metrics.")
    p.add_argument("--write_raked_model", default="J3",
                   help="Write augmented_diaries_raked.csv for this model (default J3).")
    p.add_argument("--seed",              type=int, default=42,
                   help="RNG seed for boundary tie-breaking.")
    return p.parse_args()


def _resolve_paths(args):
    base_dir  = args.base_dir  or "/speed-scratch/o_iseri/occModeling"
    step3_dir = args.step3_dir or os.path.join(base_dir, "outputs_step3")
    out_json  = args.output_json or os.path.join(base_dir, "diag_rake_compare.json")
    return base_dir, step3_dir, out_json


# ── Low-level raking helpers ──────────────────────────────────────────────────

def _boundary_mask(arr, t):
    """arr (n, T) binary float. Returns (n,) bool: slot t is at a run boundary.

    For a 1-valued slot: boundary iff adjacent slot is 0 (start/end of home run).
    For a 0-valued slot: boundary iff adjacent slot is 1 (edge of gap, adjacent to run).
    Both cases reduce to the same test: neighbor value differs from current value.
    Edge slots (t=0, t=T-1) are always counted as boundary."""
    val_t = arr[:, t]
    left  = (arr[:, t - 1] != val_t) if t > 0               else np.ones(len(arr), dtype=bool)
    right = (arr[:, t + 1] != val_t) if t < arr.shape[1] - 1 else np.ones(len(arr), dtype=bool)
    return left | right


def _rake_binary_slot(arr_col, target_count, boundary, rng):
    """Flip arr_col (in-place view) to hit target_count ones.
    Prefers boundary records; breaks ties randomly with rng.
    Returns count of flips made.
    arr_col: (n,) float 0/1 view into a 2-D array column."""
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
    order   = np.lexsort((noise, -bnd_pri))   # boundary first, then random
    chosen  = candidates[order[:n_flip]]
    arr_col[chosen] = 1.0 - arr_col[chosen]
    return n_flip


# ── Per-cell gap metrics ──────────────────────────────────────────────────────

def _ath_slot_max_gap(hom_arr, obs_hom_ps):
    """Max |ATH gap| pp across 48 slots. hom_arr: (n_cell, 48); obs_hom_ps: (48,)."""
    syn_ps = hom_arr.mean(axis=0)
    return float(np.abs(syn_ps - obs_hom_ps).max() * 100.0)


def _cop_slot_max_gap(syn_df, obs_src_df, cy):
    """Max |COP gap| pp across all channels × slots (per-slot mean, not collapsed).
    Channels/source consistent with 04K. Returns scalar worst gap across channels."""
    max_gap = 0.0
    for ch in COP_CHANNELS:
        cols = [f"{ch}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
        cs = [c for c in cols if c in syn_df.columns]
        if not cs:
            continue
        syn_ps  = syn_df[cs].values.astype(float).mean(axis=0)
        obs_arr = obs_src_df.reindex(columns=cs).values.astype(float)
        obs_ps  = np.nanmean(obs_arr, axis=0)   # nanmean for colleagues/old cycles
        gaps    = np.abs(syn_ps - obs_ps) * 100.0
        valid   = gaps[~np.isnan(gaps)]
        if len(valid):
            cell_max = float(valid.max())
            if cell_max > max_gap:
                max_gap = cell_max
    return max_gap


# ── Core per-model analysis ───────────────────────────────────────────────────

def analyse_model_rake(model_name, csv_path, obs_df, rng_seed, return_raked=False):
    print(f"\n[{model_name}]  {csv_path}", flush=True)
    if not os.path.exists(csv_path):
        print("  ERROR: file not found — skipping", flush=True)
        return None, None

    aug     = pd.read_csv(csv_path, low_memory=False)
    syn     = aug[aug["IS_SYNTHETIC"] == 1].copy()
    obs_src = aug[aug["IS_SYNTHETIC"] == 0].copy()
    print(f"  rows: aug={len(aug)}  syn={len(syn)}  obs_src={len(obs_src)}", flush=True)

    # Free aug immediately — not needed further; raked CSV is built in main()
    del aug

    # Detect available COP columns (subset of 9 channels may be present)
    avail_cop_cols = {}   # ch -> list of N_SLOTS column names in syn
    for ch in COP_CHANNELS:
        cols = [f"{ch}30_{t + 1:03d}" for t in range(N_SLOTS)]
        present = [c for c in cols if c in syn.columns]
        if present:
            avail_cop_cols[ch] = present
    print(f"  COP channels in syn: {list(avail_cop_cols.keys())}", flush=True)

    # Household pairing check
    hh_cols = [c for c in syn.columns
               if "HH_ID" in c.upper() or c.upper().startswith("HHID")]
    hh_note = (f"HH columns present ({hh_cols}); cross-person pairing not implemented in 04L"
               if hh_cols else
               "N/A — no HH_ID column found; GSS is individual-respondent data")
    print(f"  HH pairing: {hh_note}", flush=True)

    raked = syn.copy()

    # ── FIX 2026-05-30: synthetic COP channels are SOFT probabilities (0–1),
    # unlike AT_HOME (hom30_*) which is hard 0/1. _rake_binary_slot matches
    # ==1.0/==0.0 exactly, so on soft values it flipped almost nothing and the
    # COP marginal never moved (58.95→58.95 in job 940544). Binarize synthetic
    # COP at 0.5 (most-likely state) BEFORE raking — this matches the binary
    # AT_HOME representation and the hard co-presence schedule BEM consumes.
    # Observed COP rows are already 0/1, so targets are unchanged. The post-rake
    # marginal equals the target regardless of threshold; 0.5 only sets the
    # pre-rake starting point (and thus the flip-count / coherence cost).
    _all_cop_cols = [c for cols in avail_cop_cols.values() for c in cols]
    if _all_cop_cols:
        _soft = raked[_all_cop_cols].to_numpy(dtype=float)
        raked[_all_cop_cols] = (np.nan_to_num(_soft, nan=0.0) >= 0.5).astype(float)
        print(f"  COP binarized at 0.5: {len(_all_cop_cols)} synthetic columns "
              f"(soft probabilities → hard 0/1 before raking)", flush=True)

    rng   = np.random.default_rng(rng_seed)

    total_slot_records      = 0
    total_home_slot_records = 0
    total_ath_flips         = 0
    total_cop_flips         = 0

    pre_ath_per_cell  = {}
    post_ath_per_cell = {}
    pre_cop_per_cell  = {}
    post_cop_per_cell = {}

    # Probe tracking: write-back violations across all cells/channels
    probe_writeback_ok        = True
    probe_violations_total    = 0
    # Worst post-COP cell (for targeted diagnosis after the loop)
    worst_cop_post_key        = None
    worst_cop_post_gap        = 0.0

    for cy in CYCLES:
        for s in STRATA:
            obs_c     = obs_df[(obs_df["CYCLE_YEAR"] == cy) & (obs_df["DDAY_STRATA"] == s)]
            obs_src_c = obs_src[(obs_src["CYCLE_YEAR"] == cy) & (obs_src["DDAY_STRATA"] == s)]
            syn_c     = raked[(raked["CYCLE_YEAR"] == cy) & (raked["DDAY_STRATA"] == s)]
            if len(obs_c) == 0 or len(syn_c) == 0:
                continue

            key    = f"{cy}_{s}"
            idx    = syn_c.index.tolist()
            n_cell = len(idx)
            total_slot_records += n_cell * N_SLOTS

            obs_hom_ps = obs_c[HOM_COLS].values.astype(float).mean(axis=0)  # (48,)

            # Pre-rake gaps (same formula as 04K for ATH; per-slot max for COP)
            hom_arr = raked.loc[idx, HOM_COLS].values.astype(float)  # mutable copy
            pre_ath_per_cell[key] = _ath_slot_max_gap(hom_arr, obs_hom_ps)
            pre_cop_per_cell[key] = _cop_slot_max_gap(raked.loc[idx], obs_src_c, cy)

            # ── Step 1: Rake AT_HOME ──────────────────────────────────────────
            for t in range(N_SLOTS):
                tgt = max(0, min(n_cell, int(round(obs_hom_ps[t] * n_cell))))
                bnd = _boundary_mask(hom_arr, t)
                total_ath_flips += _rake_binary_slot(hom_arr[:, t], tgt, bnd, rng)

            raked.loc[idx, HOM_COLS] = hom_arr
            total_home_slot_records += int(hom_arr.sum())

            # ── Step 2: Rake COP channels (standalone per-slot marginal) ──────
            for ch, cop_cols in avail_cop_cols.items():
                n_cop_slots = len(cop_cols)

                # Align observed to syn column order; reindex fills missing with NaN
                obs_arr = obs_src_c.reindex(columns=cop_cols).values.astype(float)
                obs_ps  = np.nanmean(obs_arr, axis=0)   # (n_cop_slots,)

                # Diagnose (a): per-channel non-NaN fraction in observed reference
                if len(obs_arr) > 0:
                    non_nan_frac = float(np.mean(~np.isnan(obs_arr)))
                else:
                    non_nan_frac = 0.0
                n_skipped_slots = int(np.sum(np.isnan(obs_ps)))
                if n_skipped_slots > 0 or non_nan_frac < 0.5:
                    print(f"  OBS-NaN  key={key} ch={ch}: "
                          f"obs_src_c_rows={len(obs_arr)}  "
                          f"non_nan_frac={non_nan_frac:.3f}  "
                          f"skipped_slots={n_skipped_slots}/{n_cop_slots}  "
                          f"(colleagues in old cycles is expected)", flush=True)

                cop_arr = raked.loc[idx, cop_cols].values.astype(float)

                for t in range(n_cop_slots):
                    if np.isnan(obs_ps[t]):
                        continue   # skip slots with no observed reference
                    tgt = max(0, min(n_cell, int(round(obs_ps[t] * n_cell))))
                    bnd = _boundary_mask(cop_arr, t)
                    total_cop_flips += _rake_binary_slot(cop_arr[:, t], tgt, bnd, rng)

                # Write back with explicit DataFrame alignment to ensure assignment sticks
                raked.loc[idx, cop_cols] = pd.DataFrame(
                    cop_arr, index=idx, columns=cop_cols
                )

                # ── Probe (b): re-read and verify write-back stuck ────────────
                post_check = raked.loc[idx, cop_cols].values.astype(float)
                tol_pp = 100.0 / n_cell + 1e-7   # rounding tolerance (1 record / n_cell)
                cell_violations = []
                for t in range(n_cop_slots):
                    if np.isnan(obs_ps[t]):
                        continue  # slot was skipped — not expected to match target
                    post_syn_ps = float(post_check[:, t].mean())
                    gap_pp = abs(post_syn_ps - float(obs_ps[t])) * 100.0
                    if gap_pp > tol_pp:
                        cell_violations.append((gap_pp, t, post_syn_ps, float(obs_ps[t])))

                if cell_violations:
                    probe_writeback_ok = False
                    probe_violations_total += len(cell_violations)
                    cell_violations.sort(reverse=True)
                    print(f"  PROBE-FAIL  key={key} ch={ch}: "
                          f"{len(cell_violations)} write-back violations "
                          f"(n_cell={n_cell}, tol={tol_pp:.2f}pp)", flush=True)
                    for gap_pp, t, psp, osp in cell_violations[:5]:
                        tgt_cnt = int(round(osp * n_cell))
                        print(f"    slot {t+1:03d}: post_syn={psp:.4f}  "
                              f"obs={osp:.4f}  target={tgt_cnt}/{n_cell}  "
                              f"gap={gap_pp:.2f}pp  [write-back violation]", flush=True)
                # ── End probe ─────────────────────────────────────────────────

            # Post-rake gaps
            post_ath_per_cell[key] = _ath_slot_max_gap(
                raked.loc[idx, HOM_COLS].values.astype(float), obs_hom_ps)
            post_cop_per_cell[key] = _cop_slot_max_gap(raked.loc[idx], obs_src_c, cy)

            # Track worst post-COP cell
            if post_cop_per_cell[key] > worst_cop_post_gap:
                worst_cop_post_gap = post_cop_per_cell[key]
                worst_cop_post_key = key

    # ── Diagnose (a): worst post-COP cell — find holding channel/slot ─────────
    if worst_cop_post_key is not None:
        wcy_s, ws_s = worst_cop_post_key.split("_")
        wcy, ws = int(wcy_s), int(ws_s)
        obs_src_w = obs_src[(obs_src["CYCLE_YEAR"] == wcy) & (obs_src["DDAY_STRATA"] == ws)]
        raked_w   = raked[(raked["CYCLE_YEAR"] == wcy) & (raked["DDAY_STRATA"] == ws)]
        n_w = len(raked_w)
        print(f"\n  WORST-COP cell={worst_cop_post_key}  "
              f"post_cop_max={worst_cop_post_gap:.2f}pp  n_cell={n_w}", flush=True)
        for ch in COP_CHANNELS:
            cols_w = [f"{ch}30_{t+1:03d}" for t in range(N_SLOTS)]
            cs_w = [c for c in cols_w if c in raked.columns]
            if not cs_w:
                continue
            syn_ps_w  = raked_w[cs_w].values.astype(float).mean(axis=0)
            obs_arr_w = obs_src_w.reindex(columns=cs_w).values.astype(float)
            obs_ps_w  = np.nanmean(obs_arr_w, axis=0)
            gaps_w    = np.abs(syn_ps_w - obs_ps_w) * 100.0
            valid_w   = gaps_w[~np.isnan(gaps_w)]
            if not len(valid_w):
                continue
            worst_t   = int(np.nanargmax(gaps_w))
            wgap      = float(gaps_w[worst_t])
            wosp      = float(obs_ps_w[worst_t])
            wssp      = float(syn_ps_w[worst_t])
            wtgt      = int(round(wosp * n_w)) if not np.isnan(wosp) else -1
            flag      = "SKIPPED(obs_NaN)" if np.isnan(obs_ps_w[worst_t]) else "raked"
            if flag == "SKIPPED(obs_NaN)" and wgap > COP_GATE:
                flag += " ← COP target undefined; manager must choose alternate obs_src"
            print(f"    ch={ch:12s}  slot={worst_t+1:03d}  "
                  f"obs={wosp:.4f}  syn={wssp:.4f}  target={wtgt}/{n_w}  "
                  f"gap={wgap:.2f}pp  [{flag}]", flush=True)

    # ── Probe summary ─────────────────────────────────────────────────────────
    if probe_violations_total > 0:
        print(f"\n  PROBE SUMMARY [{model_name}]: write-back FAILED — "
              f"{probe_violations_total} violations across cells/channels  "
              f"(pd.DataFrame alignment fix applied; if violations still appear, "
              f"check column dtypes in the DataFrame)", flush=True)
    else:
        print(f"\n  PROBE SUMMARY [{model_name}]: write-back OK — "
              f"all raked slots within tolerance (1/n_cell pp)", flush=True)

    # Note on 04K vs 04L measurement difference (Fix 2d)
    print(f"  NOTE 04K vs 04L: 04L reports per-slot MAX; 04K reports collapsed MEAN — "
          f"pre-raking values here will be larger. Post-raking must still collapse "
          f"toward 0 for raked channels.", flush=True)

    pre_ath_max  = max(pre_ath_per_cell.values(),  default=0.0)
    post_ath_max = max(post_ath_per_cell.values(), default=0.0)
    pre_cop_max  = max(pre_cop_per_cell.values(),  default=0.0)
    post_cop_max = max(post_cop_per_cell.values(), default=0.0)

    flip_pct     = total_ath_flips / max(total_slot_records,      1) * 100.0
    reassign_pct = total_cop_flips / max(total_home_slot_records, 1) * 100.0

    # ── Coherence metrics ─────────────────────────────────────────────────────
    all_idx  = syn.index.tolist()
    hpre     = syn.loc[all_idx,   HOM_COLS].values.astype(float)
    hpost    = raked.loc[all_idx, HOM_COLS].values.astype(float)
    trans_pre  = float(np.abs(np.diff(hpre,  axis=1)).sum(axis=1).mean())
    trans_post = float(np.abs(np.diff(hpost, axis=1)).sum(axis=1).mean())
    trans_dpct = (trans_post - trans_pre) / max(trans_pre, 0.001) * 100.0

    cop_sw_pre_vals, cop_sw_post_vals = [], []
    for ch, cop_cols in avail_cop_cols.items():
        # binarize syn COP (soft→hard) so pre/post switch counts are comparable
        cpre  = (np.nan_to_num(syn.loc[all_idx, cop_cols].to_numpy(dtype=float),
                               nan=0.0) >= 0.5).astype(float)
        cpost = raked.loc[all_idx, cop_cols].values.astype(float)
        cop_sw_pre_vals.append(float(np.abs(np.diff(cpre,  axis=1)).sum(axis=1).mean()))
        cop_sw_post_vals.append(float(np.abs(np.diff(cpost, axis=1)).sum(axis=1).mean()))
    cop_sw_pre  = float(np.mean(cop_sw_pre_vals))  if cop_sw_pre_vals  else 0.0
    cop_sw_post = float(np.mean(cop_sw_post_vals)) if cop_sw_post_vals else 0.0

    result = {
        "n_syn":                    int(len(syn)),
        "hh_note":                  hh_note,
        "cop_channels_found":       list(avail_cop_cols.keys()),
        "pre_ath_max_gap_pp":       round(pre_ath_max,  3),
        "post_ath_max_gap_pp":      round(post_ath_max, 3),
        "pre_cop_max_gap_pp":       round(pre_cop_max,  3),
        "post_cop_max_gap_pp":      round(post_cop_max, 3),
        "flip_pct":                 round(flip_pct,     4),
        "reassign_pct":             round(reassign_pct, 4),
        "total_ath_flips":          total_ath_flips,
        "total_cop_flips":          total_cop_flips,
        "total_slot_records":       total_slot_records,
        "total_home_slot_records":  total_home_slot_records,
        "cop_probe_writeback_ok":   probe_writeback_ok,
        "cop_probe_violations":     probe_violations_total,
        "coherence": {
            "mean_trans_pre":   round(trans_pre,  3),
            "mean_trans_post":  round(trans_post, 3),
            "trans_delta":      round(trans_post - trans_pre, 3),
            "trans_delta_pct":  round(trans_dpct, 2),
            "mean_cop_sw_pre":  round(cop_sw_pre,  3),
            "mean_cop_sw_post": round(cop_sw_post, 3),
            "cop_sw_delta":     round(cop_sw_post - cop_sw_pre, 3),
        },
        "per_cell": {
            k: {
                "pre_ath":  round(pre_ath_per_cell.get(k,  0.0), 3),
                "post_ath": round(post_ath_per_cell.get(k, 0.0), 3),
                "pre_cop":  round(pre_cop_per_cell.get(k,  0.0), 3),
                "post_cop": round(post_cop_per_cell.get(k, 0.0), 3),
            }
            for k in pre_ath_per_cell
        },
    }

    print(f"  ATH  pre={pre_ath_max:.2f}pp → post={post_ath_max:.2f}pp  "
          f"flip%={flip_pct:.2f}", flush=True)
    print(f"  COP  pre={pre_cop_max:.2f}pp → post={post_cop_max:.2f}pp  "
          f"reassign%={reassign_pct:.2f}", flush=True)
    print(f"  Coh  trans {trans_pre:.2f}→{trans_post:.2f} "
          f"(Δ{trans_dpct:+.1f}%)  "
          f"COP_sw {cop_sw_pre:.2f}→{cop_sw_post:.2f}", flush=True)

    # Return raked synthetic cols so main() can build the CSV without a second aug.copy()
    if return_raked:
        modify_cols = HOM_COLS[:]
        for cols in avail_cop_cols.values():
            modify_cols.extend(cols)
        modify_cols = [c for c in modify_cols if c in raked.columns]
        return result, (raked[modify_cols].copy(), syn.index)
    return result, None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    base_dir, step3_dir, out_json = _resolve_paths(args)

    print("=" * 72, flush=True)
    print("04L — Joint Raking Diagnostic (AT_HOME + COP)", flush=True)
    print("=" * 72, flush=True)
    print(f"  base_dir     : {base_dir}", flush=True)
    print(f"  step3_dir    : {step3_dir}", flush=True)
    print(f"  out_json     : {out_json}", flush=True)
    print(f"  raked_model  : {args.write_raked_model}", flush=True)
    print(f"  seed         : {args.seed}", flush=True)

    hetus_path = os.path.join(step3_dir, "hetus_30min.csv")
    if not os.path.exists(hetus_path):
        print(f"ERROR: {hetus_path} not found — aborting", flush=True)
        sys.exit(1)
    print(f"\nLoading observed reference: {hetus_path} ...", flush=True)
    obs_df = pd.read_csv(hetus_path, low_memory=False)
    print(f"  {len(obs_df)} observed rows", flush=True)

    # Inspect copresence_30min.csv (log schema surprise; COP targets still from aug obs_src)
    cop_ref_path = os.path.join(step3_dir, "copresence_30min.csv")
    if os.path.exists(cop_ref_path):
        cop_ref = pd.read_csv(cop_ref_path, low_memory=False)
        probe   = f"{COP_CHANNELS[0]}30_001"
        if probe in cop_ref.columns:
            print(f"  SCHEMA NOTE: copresence_30min.csv DOES carry COP columns — "
                  f"using aug obs_src anyway for consistency with 04K", flush=True)
        else:
            print(f"  copresence_30min.csv loaded ({len(cop_ref)} rows) — "
                  f"no COP columns (consistent with 04I); aug obs_src used for COP targets",
                  flush=True)
    else:
        print(f"  copresence_30min.csv not found; aug obs_src used for COP targets",
              flush=True)

    results       = {}
    raked_syn_out = None   # (raked_cols_df, syn_index) stashed for write_raked_model

    os.makedirs(os.path.dirname(out_json) or ".", exist_ok=True)

    # ── Phase 1: analyse ALL 4 models; write JSON incrementally after each ────
    for model_name, rel_path in MODELS_REL.items():
        csv_path     = os.path.join(base_dir, rel_path)
        return_raked = (model_name == args.write_raked_model)

        res, raked_info = analyse_model_rake(
            model_name, csv_path, obs_df, args.seed,
            return_raked=return_raked,
        )
        if res is not None:
            results[model_name] = res
        if raked_info is not None:
            raked_syn_out = raked_info   # (raked_cols_df, syn_index)

        # Write/rewrite JSON after every model so a late crash preserves completed work
        payload = {
            "run_timestamp":   dt.datetime.now().isoformat(timespec="seconds"),
            "base_dir":        base_dir,
            "step3_dir":       step3_dir,
            "seed":            args.seed,
            "cop_definition":  "standalone_per_slot_marginal_not_conditional_on_home",
            "cop_target_src":  "aug_IS_SYNTHETIC_0 (same as 04K)",
            "hh_pairing":      "skipped_individual_respondent_gss",
            "gates": {"ath_gate_pp": ATH_GATE, "cop_gate_pp": COP_GATE},
            "models": {k: v for k, v in results.items()},
        }
        with open(out_json, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"  JSON WRITTEN: {out_json}", flush=True)

    # ── Summary Table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 92, flush=True)
    print("SUMMARY TABLE — Joint Raking (sorted by total edit cost flip%+reassign% ↑)", flush=True)
    print("=" * 92, flush=True)
    hdr = (f"{'Model':<10} {'ATH-pre':>8} {'ATH-post':>9} {'flip%':>7} "
           f"{'COP-pre':>8} {'COP-post':>9} {'reassign%':>10} {'transΔ%':>8}")
    print(hdr, flush=True)
    print("-" * 92, flush=True)

    valid  = {k: v for k, v in results.items() if v is not None}
    ranked = sorted(valid.items(),
                    key=lambda kv: kv[1]["flip_pct"] + kv[1]["reassign_pct"])

    for rank, (name, r) in enumerate(ranked, 1):
        ap  = r["pre_ath_max_gap_pp"]
        aq  = r["post_ath_max_gap_pp"]
        fp  = r["flip_pct"]
        cp  = r["pre_cop_max_gap_pp"]
        cq  = r["post_cop_max_gap_pp"]
        rp  = r["reassign_pct"]
        tdp = r["coherence"]["trans_delta_pct"]
        ak  = "✓" if aq <= ATH_GATE else " "
        ck  = "✓" if cq <= COP_GATE else " "
        print(f"  {rank}. {name:<8} {ap:>8.2f} {aq:>8.2f}{ak} {fp:>7.2f} "
              f"{cp:>8.2f} {cq:>8.2f}{ck} {rp:>9.2f} {tdp:>+8.1f}%", flush=True)
    print("-" * 92, flush=True)
    print(f"  Gates: ATH ≤ {ATH_GATE:.0f} pp (✓)  COP ≤ {COP_GATE:.0f} pp (✓)", flush=True)
    print("  Note: COP metric is per-slot max (04K uses collapsed mean — "
          "pre values will be larger than 04K's cop_max_gap_pp)", flush=True)

    # ── Verdicts ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 72, flush=True)
    print("VERDICTS", flush=True)
    print("=" * 72, flush=True)

    # V1 — Feasibility
    all_pass = all(
        r["post_ath_max_gap_pp"] <= ATH_GATE and r["post_cop_max_gap_pp"] <= COP_GATE
        for r in valid.values()
    )
    v1_label = "ALL 4 PASS" if all_pass else "NOT all pass"
    print(f"  V1 FEASIBILITY ({v1_label}):", flush=True)
    print(f"       {'Model':<10} {'ATH-post':>9}   {'COP-post':>9}", flush=True)
    for name, r in ranked:
        ak = "✓" if r["post_ath_max_gap_pp"] <= ATH_GATE else "✗"
        ck = "✓" if r["post_cop_max_gap_pp"]  <= COP_GATE else "✗"
        print(f"       {name:<10} {r['post_ath_max_gap_pp']:>8.3f}pp {ak}  "
              f"{r['post_cop_max_gap_pp']:>8.3f}pp {ck}", flush=True)
    if not all_pass:
        print("  !! Unexpected non-zero residuals — inspect per_cell JSON for "
              "cells with extreme observed distributions (raking by construction "
              "hits per-slot targets; non-zero post means cell had no feasible "
              "records to flip, e.g. n_cell too small).", flush=True)

    # V2 — Cost
    passing = [(n, r) for n, r in ranked
               if r["post_ath_max_gap_pp"] <= ATH_GATE and
                  r["post_cop_max_gap_pp"]  <= COP_GATE]
    print(f"\n  V2 COST — total edit cost (flip% + reassign%), rank by ascending cost:",
          flush=True)
    for rank, (name, r) in enumerate(ranked, 1):
        tc  = r["flip_pct"] + r["reassign_pct"]
        tag = ""
        if passing and name == passing[0][0]:
            tag = "  ← BEST raking base (lowest cost, passes both gates)"
        print(f"       {rank}. {name:<10}  flip={r['flip_pct']:.2f}%  "
              f"reassign={r['reassign_pct']:.2f}%  total={tc:.2f}%{tag}", flush=True)
    if not passing:
        print("  !! No model passes both gates — "
              "investigate feasibility (V1) before choosing raking base.", flush=True)

    # V3 — Coherence
    trans_deltas = {n: abs(r["coherence"]["trans_delta_pct"]) for n, r in valid.items()}
    worst_name   = max(trans_deltas, key=trans_deltas.get)
    best_name    = min(trans_deltas, key=trans_deltas.get)
    print(f"\n  V3 COHERENCE — per-person AT_HOME transitions pre→post rake:", flush=True)
    for name, r in ranked:
        coh = r["coherence"]
        print(f"       {name:<10}  trans: {coh['mean_trans_pre']:.2f}→"
              f"{coh['mean_trans_post']:.2f} (Δ{coh['trans_delta_pct']:+.1f}%)  "
              f"COP_sw: {coh['mean_cop_sw_pre']:.2f}→"
              f"{coh['mean_cop_sw_post']:.2f} (Δ{coh['cop_sw_delta']:+.3f})", flush=True)
    print(f"  → Worst: {worst_name} (|Δ|={trans_deltas[worst_name]:.1f}%)  "
          f"Best: {best_name} (|Δ|={trans_deltas[best_name]:.1f}%)", flush=True)
    if trans_deltas[worst_name] > 20.0:
        print(f"  !! Δ={trans_deltas[worst_name]:.1f}% > 20% threshold — "
              f"RECOMMEND coherence-aware raking as follow-up "
              f"(e.g. block-preserve or Hamming-penalized flip selection).", flush=True)
    else:
        print(f"  Δ < 20% for all models — coherence impact acceptable at this threshold.",
              flush=True)

    print("=" * 72, flush=True)

    # ── Phase 2: write raked CSV LAST, atomically, after JSON is fully on disk ─
    raked_path = None
    if raked_syn_out is not None:
        raked_cols_df, syn_index = raked_syn_out
        raked_out_dir = os.path.join(base_dir,
                                     f"outputs_step4_{args.write_raked_model}")
        os.makedirs(raked_out_dir, exist_ok=True)
        raked_path = os.path.join(raked_out_dir, "augmented_diaries_raked.csv")

        # Load aug fresh; modify a single copy in-place; free raked_cols_df before writing
        j3_csv = os.path.join(base_dir, MODELS_REL[args.write_raked_model])
        print(f"\nLoading {args.write_raked_model} aug for raked CSV ...", flush=True)
        aug_write = pd.read_csv(j3_csv, low_memory=False)
        expected_rows = len(aug_write)
        print(f"  aug rows: {expected_rows}  syn rows to update: {len(syn_index)}",
              flush=True)

        # In-place update: never hold aug.copy() + raked simultaneously
        aug_write.loc[syn_index, raked_cols_df.columns] = raked_cols_df.values
        del raked_cols_df   # free before writing full frame

        # Atomic write: .tmp then os.replace() so a kill never leaves a truncated final file
        tmp_path = raked_path + ".tmp"
        print(f"  Writing to {tmp_path} ...", flush=True)
        aug_write.to_csv(tmp_path, index=False)

        # Verify row count before committing
        n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1  # minus header
        if n_written != expected_rows:
            os.remove(tmp_path)
            raise RuntimeError(
                f"Row count mismatch: wrote {n_written} rows, expected {expected_rows}. "
                f"Truncated tmp removed; {raked_path} not overwritten."
            )

        os.replace(tmp_path, raked_path)
        print(f"  RAKED CSV WRITTEN: {n_written} rows → {raked_path}", flush=True)

    print(f"\nALL DONE.  JSON: {out_json}", flush=True)
    if raked_path:
        print(f"            CSV: {raked_path}", flush=True)


if __name__ == "__main__":
    main()
