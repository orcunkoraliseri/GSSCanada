#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3rdJ_04R_diag_floating_2split.py — FLOATING state diagnostic (R10_fast, pre-rake)

Answers WHY synthetic FLOATING (act==work, wrk30==0, hom30==0) is ~25% when
observed is ~3%.  Hypothesis: decoding threshold artifact vs genuinely learned
no-location state.

Sections:
  (A) DECOMPOSITION  — AT-WORK / TELEWORK / FLOATING / DOUBLE-POS% at work slots
                       for synthetic + observed; FLOATING split by TELEWORK flag.
  (B) PROBABILITY-MASS TEST — raw sigmoid probs at floating slots via GPU forward
      pass (return_hw_probs=True).  Histogram of max(p_wrk, p_hom) in 0.1 bins.
      VERDICT: >=60% of floating slots in [0.3,0.5) -> THRESHOLD ARTIFACT
               >=60% in [0.0,0.2)                   -> LEARNED no-location
  (C) THRESHOLD SWEEP — re-decode at thr in {0.5,0.45,0.4,0.35,0.3}; report
      FLOATING% and DOUBLE-POSITIVE% at each threshold.
  (D) CONCENTRATION / SHAPE — floating by slot-of-day (48 bins), by stratum,
      by year.  Share of respondents >50% floating on their work slots.
      Syn vs obs floating time-of-day profile comparison (cos-sim + max pp-diff).

Writes a compact text report to --output (default: outputs_step4/diag_floating_R10.txt).
Does NOT modify any CSV.

Usage (cluster, via sbatch pg):
    python 3rdJ_04R_diag_floating_2split.py [options]

Key options:
    --data_dir      DIR with step4_{train,val,test}.pt  (default: outputs_step4/)
    --aug_csv       augmented_diaries.csv to analyse     (default: .../R10_fast/augmented_diaries.csv)
    --checkpoint    best_model.pt                        (default: .../R10_fast/checkpoints/best_model.pt)
    --n_sample      max respondents for forward pass     (default: 2000; 0 = all)
    --output        output txt path
    --smoke         tiny run for local CPU smoke-test (50 respondents)
"""
from __future__ import annotations

import argparse
import importlib
import os
import platform
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
import torch

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# ── Platform-detection path block (mirrors 04E / 04H / 04L) ──────────────────
_SYSTEM = platform.system()
if _SYSTEM == "Windows":
    _LEG2_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG2_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split"
else:
    _LEG2_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg2_2-split",
    )

_STEP4_SHARED = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")
_R10_DIR      = os.path.join(_STEP4_SHARED, "sweep", "R10_fast")

N_SLOTS      = 48
TEMPERATURE  = 0.8
BATCH_SIZE   = 256
WORK_CAT_CSV = 1          # act30_xxx == 1 in the CSV (raw, 1-indexed)
WORK_CAT_TEN = 0          # 0-indexed tensor value inside the model

# 04:00-origin slot grid.  Slots 0-47 = 04:00-27:30 (every 30 min).
# Commute windows: 07-09h = slots 6-9 (0-indexed), 16-18h = slots 24-27.
# slot_i corresponds to clock time 04:00 + i*30min.
def slot_to_clock(i: int) -> str:
    minutes = 4 * 60 + i * 30
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

COMMUTE_MORNING  = list(range(6, 10))   # 07:00-09:00
COMMUTE_EVENING  = list(range(24, 28))  # 16:00-18:00


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Floating-state diagnostic (R10_fast)")
    p.add_argument("--data_dir",   default=None,
                   help="Dir with step4_{train,val,test}.pt (default: outputs_step4/)")
    p.add_argument("--aug_csv",    default=None,
                   help="Path to augmented_diaries.csv (default: R10_fast/augmented_diaries.csv)")
    p.add_argument("--checkpoint", default=None,
                   help="best_model.pt (default: R10_fast/checkpoints/best_model.pt)")
    p.add_argument("--n_sample",   type=int, default=2000,
                   help="Max respondents to use for GPU forward pass (0=all, default 2000)")
    p.add_argument("--output",     default=None,
                   help="Output txt path (default: outputs_step4/diag_floating_R10.txt)")
    p.add_argument("--smoke",      action="store_true",
                   help="Local CPU smoke-test mode: 50 respondents, relaxed")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_all_data(data_dir: str) -> dict:
    splits = {}
    for split in ["train", "val", "test"]:
        splits[split] = torch.load(
            os.path.join(data_dir, f"step4_{split}.pt"),
            map_location="cpu", weights_only=False,
        )
    keys = list(splits["train"].keys())
    return {k: torch.cat([splits[s][k] for s in ["train", "val", "test"]], dim=0) for k in keys}


# ─────────────────────────────────────────────────────────────────────────────
# Section A — decomposition from CSV binary values
# ─────────────────────────────────────────────────────────────────────────────

def section_a(aug: pd.DataFrame, lines: list) -> dict:
    lines.append("\n" + "=" * 70)
    lines.append("(A) DECOMPOSITION — work-activity slot breakdown")
    lines.append("=" * 70)

    ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    WRK = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]

    def decompose(d: pd.DataFrame, name: str) -> dict:
        a = d[ACT].to_numpy(dtype=float)
        h = d[HOM].to_numpy(dtype=float)
        w = d[WRK].to_numpy(dtype=float)
        work_mask = (a == WORK_CAT_CSV)
        n_work = int(work_mask.sum())
        if n_work == 0:
            lines.append(f"  [{name}] n={len(d):,}  NO work slots — skipping")
            return {}
        at_work    = int((work_mask & (w == 1) & (h == 0)).sum())
        telework   = int((work_mask & (w == 0) & (h == 1)).sum())
        floating   = int((work_mask & (w == 0) & (h == 0)).sum())
        double_pos = int((work_mask & (w == 1) & (h == 1)).sum())
        r = dict(n_rows=len(d), n_work=n_work,
                 pct_atwork=100.0*at_work/n_work,
                 pct_telework=100.0*telework/n_work,
                 pct_floating=100.0*floating/n_work,
                 pct_double=100.0*double_pos/n_work)
        lines.append(f"\n  [{name}] n_rows={r['n_rows']:,}  work_slots={n_work:,}")
        lines.append(f"    AT-WORK   (wrk=1, hom=0):  {r['pct_atwork']:6.2f}%")
        lines.append(f"    TELEWORK  (wrk=0, hom=1):  {r['pct_telework']:6.2f}%  <- legitimate")
        lines.append(f"    FLOATING  (wrk=0, hom=0):  {r['pct_floating']:6.2f}%  <- TARGET")
        lines.append(f"    DOUBLE-POS(wrk=1, hom=1):  {r['pct_double']:6.2f}%  (expect 0)")
        return r

    res = {}
    obs_d = aug[aug["IS_SYNTHETIC"] == 0]
    syn_d = aug[aug["IS_SYNTHETIC"] == 1]
    res["obs"] = decompose(obs_d, "OBS")
    res["syn"] = decompose(syn_d, "SYN")

    # FLOATING split by TELEWORK
    lines.append("\n  FLOATING breakdown by TELEWORK flag (SYN only):")
    if "TELEWORK" in syn_d.columns:
        for tv, label in [(1, "TELEWORK=1"), (0, "TELEWORK=0")]:
            g = syn_d[syn_d["TELEWORK"].fillna(0) == tv]
            if len(g) == 0:
                lines.append(f"    {label}: no rows")
                continue
            a2 = g[[f"act30_{s:03d}" for s in range(1, N_SLOTS+1)]].to_numpy(dtype=float)
            h2 = g[[f"hom30_{s:03d}" for s in range(1, N_SLOTS+1)]].to_numpy(dtype=float)
            w2 = g[[f"wrk30_{s:03d}" for s in range(1, N_SLOTS+1)]].to_numpy(dtype=float)
            wm = (a2 == WORK_CAT_CSV)
            nw = int(wm.sum())
            if nw == 0:
                lines.append(f"    {label}: 0 work slots")
                continue
            fl = int((wm & (w2 == 0) & (h2 == 0)).sum())
            lines.append(f"    {label}: n_rows={len(g):,}  work_slots={nw:,}  FLOATING={100.0*fl/nw:.2f}%")
    else:
        lines.append("    TELEWORK column not found — skipping")
    return res


# ─────────────────────────────────────────────────────────────────────────────
# Section B — raw probability distribution at floating slots (GPU forward pass)
# ─────────────────────────────────────────────────────────────────────────────

def section_b(aug: pd.DataFrame, data: dict, model, device,
              n_sample: int, lines: list) -> dict:
    """
    Run model.generate with return_hw_probs=True on a sample of respondents.
    Collect p_home and p_work at work-activity slots that ended up FLOATING
    (wrk30==0, hom30==0) at 0.5 threshold.  Report histogram of max(p_h, p_w).
    """
    lines.append("\n" + "=" * 70)
    lines.append("(B) PROBABILITY-MASS TEST — raw sigmoid at floating work slots")
    lines.append("=" * 70)

    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n_total = len(data["act_seq"])
    obs_strata_all  = data["obs_strata"].numpy()
    cycle_year_all  = data["cycle_year"].numpy()
    occ_ids_all     = data["occ_ids"].numpy()

    # Only use respondents that HAVE work-activity slots in the CSV (efficiency)
    # We'll run ALL in the sample and filter post-hoc.
    rng = np.random.default_rng(42)
    if n_sample > 0 and n_sample < n_total:
        chosen = rng.choice(n_total, size=n_sample, replace=False)
        chosen = np.sort(chosen)
    else:
        chosen = np.arange(n_total)

    # Build a lookup of (occ_id, cycle_year, s_tgt) -> (act_row, hom_row, wrk_row)
    # for the CSV rows we care about.
    ACT_C = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    HOM_C = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    WRK_C = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    syn = aug[aug["IS_SYNTHETIC"] == 1][
        ["occID", "CYCLE_YEAR", "DDAY_STRATA"] + ACT_C + HOM_C + WRK_C
    ].copy()
    # Index by (occID, CYCLE_YEAR, DDAY_STRATA)
    syn_lookup = {}
    for _, row in syn.iterrows():
        key = (int(row["occID"]), int(row["CYCLE_YEAR"]), int(row["DDAY_STRATA"]))
        syn_lookup[key] = (
            row[ACT_C].to_numpy(dtype=float),
            row[HOM_C].to_numpy(dtype=float),
            row[WRK_C].to_numpy(dtype=float),
        )
    lines.append(f"  CSV synthetic lookup built: {len(syn_lookup):,} (occID,CY,strata) keys")

    # Run forward pass in batches
    all_p_home = []   # prob at (person,slot) where work-act AND floating in CSV
    all_p_work = []

    n_processed = 0
    n_float_slots = 0

    r11_on = getattr(model, "_r11_on", False)
    r11_latent_dim = getattr(model, "r11_latent_dim", 0)
    if r11_on and r11_latent_dim > 0:
        torch.manual_seed(42)
        person_latents = torch.randn(n_total, r11_latent_dim)
    else:
        person_latents = None

    for batch_start in range(0, len(chosen), BATCH_SIZE):
        batch_idx = chosen[batch_start: batch_start + BATCH_SIZE]
        chunk = list(batch_idx)

        syn_idx, syn_strata = [], []
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i)
                    syn_strata.append(s_tgt)

        if not syn_idx:
            n_processed += len(chunk)
            continue

        act_t  = data["act_seq"][syn_idx].to(device)
        aux_t  = data["aux_seq"][syn_idx].to(device)
        cond_t = data["cond_vec"][syn_idx].to(device)
        cidx_t = data["cycle_idx"][syn_idx].to(device)
        strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

        r11_batch = None
        if person_latents is not None:
            r11_batch = person_latents[syn_idx].to(device)

        with torch.no_grad():
            result = model.generate(
                act_t, aux_t, cond_t, cidx_t, strat,
                temperature=TEMPERATURE,
                home_threshold=0.5,
                work_threshold=0.5,
                apply_safety=False,
                return_hw_probs=True,
                r11_latent=r11_batch,
            )
        # 7-tuple: act, home_bin, work_bin, cop_bin, cop_probs, home_probs, work_probs
        g_act        = result[0].cpu().numpy()  # (B, 48) 0-indexed
        g_home_probs = result[5].cpu().numpy()  # (B, 48)
        g_work_probs = result[6].cpu().numpy()  # (B, 48)

        for k, (i, s_tgt) in enumerate(zip(syn_idx, syn_strata)):
            occ_id = int(occ_ids_all[i])
            cy     = int(cycle_year_all[i])
            key    = (occ_id, cy, s_tgt)

            # Get the CSV row for this (person, strata) to know which slots are FLOATING
            csv_entry = syn_lookup.get(key)
            if csv_entry is None:
                continue
            act_csv, hom_csv, wrk_csv = csv_entry

            # act_csv uses raw 1-indexed (WORK_CAT_CSV=1)
            # g_act[k] uses 0-indexed (WORK_CAT_TEN=0)
            # Both should agree: g_act[k]==0 <-> act_csv==1
            for s in range(N_SLOTS):
                is_work_csv  = (act_csv[s] == WORK_CAT_CSV)
                is_float_csv = is_work_csv and (wrk_csv[s] == 0) and (hom_csv[s] == 0)
                if is_float_csv:
                    all_p_home.append(float(g_home_probs[k, s]))
                    all_p_work.append(float(g_work_probs[k, s]))
                    n_float_slots += 1

        n_processed += len(chunk)
        print(f"  [B] Processed {n_processed}/{len(chosen)} respondents "
              f"({100.0*n_processed/len(chosen):.1f}%)  float_slots={n_float_slots}", flush=True)

    lines.append(f"  Sampled respondents: {len(chosen):,}")
    lines.append(f"  Floating work slots found in sample: {n_float_slots:,}")

    if n_float_slots == 0:
        lines.append("  WARNING: no floating slots found in sample — cannot compute histogram")
        return {"n_float_slots": 0}

    p_home_arr = np.array(all_p_home)
    p_work_arr = np.array(all_p_work)
    p_max      = np.maximum(p_home_arr, p_work_arr)

    # Histogram in bins [0,0.1), [0.1,0.2), ..., [0.4,0.5), [0.5,1]
    bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.01]
    labels = ["[0.0,0.1)", "[0.1,0.2)", "[0.2,0.3)", "[0.3,0.4)", "[0.4,0.5)", "[0.5,1.0]"]
    counts, _ = np.histogram(p_max, bins=bins)
    pcts = 100.0 * counts / n_float_slots

    lines.append("\n  max(p_wrk, p_hom) histogram at FLOATING work slots:")
    lines.append("  " + "-" * 42)
    for lb, cnt, pct in zip(labels, counts, pcts):
        bar = "#" * int(pct / 2)
        lines.append(f"  {lb}  {cnt:7d}  {pct:6.2f}%  {bar}")

    # Means
    lines.append(f"\n  mean p_home at floating slots: {p_home_arr.mean():.4f}")
    lines.append(f"  mean p_work at floating slots: {p_work_arr.mean():.4f}")
    lines.append(f"  mean max(p_h,p_w):             {p_max.mean():.4f}")

    # Verdict
    below_02  = float(np.sum(p_max < 0.2)) / n_float_slots
    above_03  = float(np.sum(p_max >= 0.3)) / n_float_slots
    near_half = float(np.sum((p_max >= 0.3) & (p_max < 0.5))) / n_float_slots

    lines.append(f"\n  Verdict check:")
    lines.append(f"    % with max_prob < 0.2  (LEARNED evidence):    {100*below_02:.1f}%")
    lines.append(f"    % with max_prob >= 0.3 (THRESHOLD evidence):  {100*above_03:.1f}%")
    lines.append(f"    % with max_prob in [0.3,0.5) (THRESHOLD key): {100*near_half:.1f}%")

    if near_half >= 0.60:
        verdict_b = "THRESHOLD-ARTIFACT"
        reason_b  = f"{100*near_half:.0f}% of floating slots have max_prob in [0.3,0.5)"
    elif below_02 >= 0.60:
        verdict_b = "LEARNED"
        reason_b  = f"{100*below_02:.0f}% of floating slots have max_prob < 0.2"
    else:
        verdict_b = "MIXED"
        reason_b  = (f"neither criterion met: near_half={100*near_half:.0f}%  "
                     f"below_02={100*below_02:.0f}%")

    lines.append(f"\n  *** B VERDICT: {verdict_b} — {reason_b} ***")

    return {
        "n_float_slots": n_float_slots,
        "hist_pcts": pcts.tolist(),
        "mean_p_home": float(p_home_arr.mean()),
        "mean_p_work": float(p_work_arr.mean()),
        "mean_max": float(p_max.mean()),
        "near_half_pct": float(100*near_half),
        "below_02_pct": float(100*below_02),
        "verdict": verdict_b,
        "reason": reason_b,
        # save arrays for section C
        "_p_home_arr": p_home_arr,
        "_p_work_arr": p_work_arr,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Section C — threshold sweep using raw probs from section B
# ─────────────────────────────────────────────────────────────────────────────

def section_c(aug: pd.DataFrame, data: dict, model, device,
              b_results: dict, n_sample: int, lines: list) -> None:
    """
    Re-decode wrk30/hom30 at thresholds {0.5, 0.45, 0.4, 0.35, 0.3}.
    Report FLOATING% and DOUBLE-POS% at each threshold for SYN work slots.
    Uses a full sweep: re-runs forward pass for ALL sampled respondents.
    """
    lines.append("\n" + "=" * 70)
    lines.append("(C) THRESHOLD SWEEP — FLOATING% and DOUBLE-POS% at work slots")
    lines.append("=" * 70)

    THRESHOLDS = [0.50, 0.45, 0.40, 0.35, 0.30]

    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n_total = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()
    cycle_year_all = data["cycle_year"].numpy()
    occ_ids_all    = data["occ_ids"].numpy()

    rng = np.random.default_rng(42)
    if n_sample > 0 and n_sample < n_total:
        chosen = np.sort(rng.choice(n_total, size=n_sample, replace=False))
    else:
        chosen = np.arange(n_total)

    r11_on = getattr(model, "_r11_on", False)
    r11_latent_dim = getattr(model, "r11_latent_dim", 0)
    if r11_on and r11_latent_dim > 0:
        torch.manual_seed(42)
        person_latents = torch.randn(n_total, r11_latent_dim)
    else:
        person_latents = None

    # Collect per-slot: act(0-indexed), p_home, p_work for ALL sampled syn slots
    all_act   = []   # list of arrays (48,)
    all_ph    = []
    all_pw    = []

    n_processed = 0
    for batch_start in range(0, len(chosen), BATCH_SIZE):
        batch_idx = chosen[batch_start: batch_start + BATCH_SIZE]
        chunk = list(batch_idx)

        syn_idx, syn_strata = [], []
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i)
                    syn_strata.append(s_tgt)

        if not syn_idx:
            n_processed += len(chunk)
            continue

        act_t  = data["act_seq"][syn_idx].to(device)
        aux_t  = data["aux_seq"][syn_idx].to(device)
        cond_t = data["cond_vec"][syn_idx].to(device)
        cidx_t = data["cycle_idx"][syn_idx].to(device)
        strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

        r11_batch = None
        if person_latents is not None:
            r11_batch = person_latents[syn_idx].to(device)

        with torch.no_grad():
            result = model.generate(
                act_t, aux_t, cond_t, cidx_t, strat,
                temperature=TEMPERATURE,
                home_threshold=0.5,
                work_threshold=0.5,
                apply_safety=False,
                return_hw_probs=True,
                r11_latent=r11_batch,
            )
        g_act        = result[0].cpu().numpy()  # (B, 48) 0-indexed
        g_home_probs = result[5].cpu().numpy()  # (B, 48)
        g_work_probs = result[6].cpu().numpy()  # (B, 48)

        for k in range(len(syn_idx)):
            all_act.append(g_act[k])       # (48,)
            all_ph.append(g_home_probs[k]) # (48,)
            all_pw.append(g_work_probs[k]) # (48,)

        n_processed += len(chunk)

    # Stack: (N_syn_samples, 48)
    act_mat = np.stack(all_act, axis=0)    # 0-indexed
    ph_mat  = np.stack(all_ph,  axis=0)
    pw_mat  = np.stack(all_pw,  axis=0)

    work_mask = (act_mat == WORK_CAT_TEN)  # 0-indexed: work==0
    n_work = int(work_mask.sum())
    if n_work == 0:
        lines.append("  No work slots found in sample — skipping sweep")
        return

    lines.append(f"  Sampled syn diary-slots with work activity: {n_work:,}")
    lines.append("\n  threshold | FLOATING%  | DOUBLE-POS% | note")
    lines.append("  " + "-" * 52)

    for thr in THRESHOLDS:
        h_bin = (ph_mat > thr).astype(float)
        w_bin = (pw_mat > thr).astype(float)
        floating   = int((work_mask & (w_bin == 0) & (h_bin == 0)).sum())
        double_pos = int((work_mask & (w_bin == 1) & (h_bin == 1)).sum())
        pct_float  = 100.0 * floating   / n_work
        pct_dbl    = 100.0 * double_pos / n_work
        note = ""
        if thr == 0.50:
            note = "<- baseline"
        lines.append(f"  thr={thr:.2f}   | {pct_float:7.2f}%  | {pct_dbl:9.2f}%  | {note}")


# ─────────────────────────────────────────────────────────────────────────────
# Section D — concentration / shape analysis
# ─────────────────────────────────────────────────────────────────────────────

def section_d(aug: pd.DataFrame, lines: list) -> None:
    lines.append("\n" + "=" * 70)
    lines.append("(D) CONCENTRATION / SHAPE — floating distribution")
    lines.append("=" * 70)

    ACT = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    HOM = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    WRK = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]

    syn = aug[aug["IS_SYNTHETIC"] == 1]
    obs = aug[aug["IS_SYNTHETIC"] == 0]

    def float_by_slot(d: pd.DataFrame):
        a = d[ACT].to_numpy(dtype=float)
        h = d[HOM].to_numpy(dtype=float)
        w = d[WRK].to_numpy(dtype=float)
        wm = (a == WORK_CAT_CSV)
        fl = (wm & (w == 0) & (h == 0))
        n_work_per_slot = wm.sum(axis=0)  # (48,)
        n_float_per_slot = fl.sum(axis=0)  # (48,)
        # avoid division by zero
        rate = np.where(n_work_per_slot > 0, n_float_per_slot / n_work_per_slot, np.nan)
        return rate, n_work_per_slot, n_float_per_slot

    syn_rate, syn_nwork, syn_nfloat = float_by_slot(syn)
    obs_rate, obs_nwork, obs_nfloat = float_by_slot(obs)

    lines.append("\n  FLOATING rate by slot (slot:clock, obs%, syn%):")
    lines.append("  " + "-" * 56)
    for i in range(N_SLOTS):
        clock = slot_to_clock(i)
        o = f"{100*obs_rate[i]:.1f}%" if not np.isnan(obs_rate[i]) else " n/a "
        s = f"{100*syn_rate[i]:.1f}%" if not np.isnan(syn_rate[i]) else " n/a "
        commute_flag = ""
        if i in COMMUTE_MORNING:
            commute_flag = " <- morning commute"
        elif i in COMMUTE_EVENING:
            commute_flag = " <- evening commute"
        lines.append(f"  slot {i:02d} ({clock})  obs={o:>6}  syn={s:>6}  "
                     f"(work_slots syn={int(syn_nwork[i]):,}){commute_flag}")

    # Peak floating slot for syn
    syn_peak = int(np.nanargmax(syn_rate)) if not np.all(np.isnan(syn_rate)) else -1
    lines.append(f"\n  SYN peak floating slot: {syn_peak} ({slot_to_clock(syn_peak)}) "
                 f"= {100*syn_rate[syn_peak]:.1f}%")

    # Shape comparison: cosine similarity between obs and syn slot profiles
    valid = ~(np.isnan(syn_rate) | np.isnan(obs_rate))
    if valid.sum() > 1:
        sv = syn_rate[valid]
        ov = obs_rate[valid]
        sv_n = sv / (np.linalg.norm(sv) + 1e-12)
        ov_n = ov / (np.linalg.norm(ov) + 1e-12)
        cos_sim = float(np.dot(sv_n, ov_n))
        max_pp = float(np.max(np.abs(sv - ov)[valid]) * 100)
        lines.append(f"  Syn vs obs floating profile: cos_sim={cos_sim:.4f}  "
                     f"max_pp_diff={max_pp:.1f}pp")
        if cos_sim > 0.85:
            lines.append("    -> SIMILAR SHAPE (scaled up, more benign — model learned the pattern)")
        else:
            lines.append("    -> DIFFERENT SHAPE (structural defect — model learned wrong pattern)")

    # By stratum
    lines.append("\n  FLOATING% by DDAY_STRATA (SYN):")
    for st, lab in [(1, "Weekday"), (2, "Saturday"), (3, "Sunday")]:
        g = syn[syn["DDAY_STRATA"] == st]
        if len(g) == 0:
            continue
        a2 = g[ACT].to_numpy(dtype=float)
        h2 = g[HOM].to_numpy(dtype=float)
        w2 = g[WRK].to_numpy(dtype=float)
        wm2 = (a2 == WORK_CAT_CSV); nw2 = int(wm2.sum())
        fl2 = int((wm2 & (w2 == 0) & (h2 == 0)).sum())
        lines.append(f"    {lab} (strata={st}): work_slots={nw2:,}  FLOATING={100.0*fl2/nw2:.2f}%" if nw2>0 else f"    {lab}: no work slots")

    # By year
    lines.append("\n  FLOATING% by CYCLE_YEAR (SYN):")
    if "CYCLE_YEAR" in syn.columns:
        for cy in sorted(syn["CYCLE_YEAR"].unique()):
            g = syn[syn["CYCLE_YEAR"] == cy]
            a2 = g[ACT].to_numpy(dtype=float)
            h2 = g[HOM].to_numpy(dtype=float)
            w2 = g[WRK].to_numpy(dtype=float)
            wm2 = (a2 == WORK_CAT_CSV); nw2 = int(wm2.sum())
            fl2 = int((wm2 & (w2 == 0) & (h2 == 0)).sum())
            if nw2 > 0:
                lines.append(f"    {cy}: work_slots={nw2:,}  FLOATING={100.0*fl2/nw2:.2f}%")

    # Share of respondents with >50% floating on their work slots
    lines.append("\n  Respondents by floating fraction on their work slots (SYN):")
    a_mat = syn[ACT].to_numpy(dtype=float)
    h_mat = syn[HOM].to_numpy(dtype=float)
    w_mat = syn[WRK].to_numpy(dtype=float)
    wm_all = (a_mat == WORK_CAT_CSV)
    fl_all = (wm_all & (w_mat == 0) & (h_mat == 0))
    nw_per_row = wm_all.sum(axis=1).astype(float)
    fl_per_row = fl_all.sum(axis=1).astype(float)
    has_work   = nw_per_row > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        frac_float = np.where(has_work, fl_per_row / nw_per_row, np.nan)
    n_has_work = int(has_work.sum())
    if n_has_work > 0:
        thresholds_d = [0.0, 0.1, 0.25, 0.50, 0.75, 1.0]
        for lo, hi in zip(thresholds_d[:-1], thresholds_d[1:]):
            cnt = int(np.sum((frac_float >= lo) & (frac_float < hi)))
            pct = 100.0 * cnt / n_has_work
            lines.append(f"    [{lo:.0%},{hi:.0%}): {cnt:,} respondents ({pct:.1f}%)")
        # >50%
        gt50 = int(np.sum(frac_float > 0.50))
        lines.append(f"\n  Respondents with >50% floating on work slots: "
                     f"{gt50:,} / {n_has_work:,} = {100.0*gt50/n_has_work:.1f}%")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Resolve paths
    data_dir   = args.data_dir   or _STEP4_SHARED
    aug_csv    = args.aug_csv    or os.path.join(_R10_DIR, "augmented_diaries.csv")
    checkpoint = args.checkpoint or os.path.join(_R10_DIR, "checkpoints", "best_model.pt")
    output     = args.output     or os.path.join(_STEP4_SHARED, "diag_floating_R10.txt")
    n_sample   = args.n_sample
    if args.smoke:
        n_sample = 50

    print("=" * 70)
    print("3rdJ Step 4R — FLOATING-state diagnostic (R10_fast)")
    print("=" * 70)
    print(f"  data_dir:   {data_dir}")
    print(f"  aug_csv:    {aug_csv}")
    print(f"  checkpoint: {checkpoint}")
    print(f"  n_sample:   {n_sample} {'(SMOKE)' if args.smoke else ''}")
    print(f"  output:     {output}")

    # Validate inputs
    for f, label in [(aug_csv, "aug_csv"), (checkpoint, "checkpoint")]:
        if not os.path.isfile(f):
            print(f"[ERROR] {label} not found: {f}")
            sys.exit(1)

    # Device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  device: {device}")

    # Load augmented diaries CSV
    print("\n[1/5] Loading augmented_diaries.csv...")
    aug = pd.read_csv(aug_csv, low_memory=False)
    print(f"  Rows: {len(aug):,}  "
          f"obs={int((aug['IS_SYNTHETIC']==0).sum()):,}  "
          f"syn={int((aug['IS_SYNTHETIC']==1).sum()):,}")

    # Load tensor data
    print("\n[2/5] Loading tensor datasets...")
    data = load_all_data(data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n:,}")

    # Load model
    print("\n[3/5] Loading checkpoint...")
    ckpt  = torch.load(checkpoint, map_location=device, weights_only=False)
    model_mod = importlib.import_module("3rdJ_04B_model_2split")
    JSeriesHybrid2Split = model_mod.JSeriesHybrid2Split
    model = JSeriesHybrid2Split(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded epoch={ckpt.get('epoch','?')} val_js={ckpt.get('val_js','?')} "
          f"work_gap={ckpt.get('work_gap','?')}")

    # Run sections
    lines = []
    lines.append(f"\n{'='*70}")
    lines.append("FLOATING DIAGNOSTIC REPORT — R10_fast pre-rake")
    lines.append(f"  aug_csv:    {aug_csv}")
    lines.append(f"  checkpoint: {checkpoint}")
    lines.append(f"  n_sample:   {n_sample}  device: {device}")
    lines.append(f"{'='*70}")

    print("\n[4/5] Running sections A, D (CSV-only, fast)...")
    a_res = section_a(aug, lines)
    section_d(aug, lines)

    print("\n[5/5] Running section B + C (GPU forward pass)...")
    b_res = section_b(aug, data, model, device, n_sample, lines)
    section_c(aug, data, model, device, b_res, n_sample, lines)

    # Final verdict
    lines.append("\n" + "=" * 70)
    lines.append("FINAL VERDICT")
    lines.append("=" * 70)
    b_verdict = b_res.get("verdict", "UNKNOWN")
    b_reason  = b_res.get("reason",  "section B did not produce a verdict")
    lines.append(f"  FLOATING is {b_verdict} because {b_reason}.")
    if a_res.get("syn", {}).get("pct_floating") is not None:
        syn_pct = a_res["syn"]["pct_floating"]
        obs_pct = a_res.get("obs", {}).get("pct_floating", float("nan"))
        lines.append(f"  SYN FLOATING = {syn_pct:.2f}%  OBS FLOATING = {obs_pct:.2f}%")
    lines.append("")

    report = "\n".join(lines)
    print("\n" + report)

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n[OK] Report written to {output}")


if __name__ == "__main__":
    main()
