#!/usr/bin/env python3
"""
3rdJ Step 4 — G2/OW1 Home/Work Operating-Point Diagnostic (Plan B)
====================================================================
Re-runs model.generate with return_hw_probs=True to capture the raw sigmoid
probabilities for the AT_HOME (home_head) and AT_WORK (work_head) heads BEFORE
the 0.5 binarisation threshold.

For each head it reports, matching the exact validator gate definition (G2 for
AT_HOME, OW1 for AT_WORK — both UNWEIGHTED, NaN-aware, np.nanmean(x) on binary
observed data == np.nanmean(x==1)):

  head          — "HOME" or "WORK"
  obs_prev      — observed prevalence (%) from aux columns of observed respondents
  syn_mean_prob — head's mean predicted sigmoid probability over synthetic strata (%)
  syn_prev@0.5  — synthetic prevalence at the default 0.5 cutoff (%)
  gap@0.5       — |obs_prev - syn_prev@0.5|
  calib_gap     — |obs_prev - syn_mean_prob|  (calibration anchor)
  t_match       — per-head threshold (unweighted quantile) so syn prevalence == obs_prev
  gap@t_match   — residual gap after rank-to-marginal (≈0 if achievable)
  verdict       — OPERATING-POINT (calib_gap<=3.0 pp) or LEARNED-DEFICIT

Decision rule (matches 04G):
  calib_gap <= 3.0 pp  -> OPERATING-POINT (threshold fix closes gap for free)
  calib_gap >  3.0 pp  -> LEARNED-DEFICIT (model-side lever needed)

Analysis-only. Does NOT write or overwrite augmented_diaries.csv.
Writes g2ow1_homework_diagnostic.txt + .csv to --step4_dir.

Run on the cluster via sbatch (GPU required for model.generate).

Usage:
    python 3rdJ_04H_diag_homework_2split.py \\
        --step4_dir /speed-scratch/o_iseri/.../outputs_step4 \\
        [--data_dir ...] [--checkpoint ...]
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import sys

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
model_mod = importlib.import_module("3rdJ_04B_model_2split")
JSeriesHybrid2Split = model_mod.JSeriesHybrid2Split

# ── Platform-detection path block (mirrors 04E) ────────────────────────────────
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
_STEP4_DEFAULT = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")

N_SLOTS = 48
TEMPERATURE = 0.8
BATCH_SIZE = 256


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--step4_dir", required=True,
                   help="Variant output dir containing checkpoints/ and step4_*.pt files")
    p.add_argument("--data_dir", default=None,
                   help="Dir with step4_{train,val,test}.pt (defaults to --step4_dir)")
    p.add_argument("--checkpoint", default=None,
                   help="Path to best_model.pt (defaults to step4_dir/checkpoints/best_model.pt)")
    return p.parse_args()


def load_all_data(data_dir: str):
    """Load and concatenate train/val/test tensor dicts (mirrors 04E load_all_data)."""
    splits = {}
    for split in ["train", "val", "test"]:
        splits[split] = torch.load(
            os.path.join(data_dir, f"step4_{split}.pt"), map_location="cpu", weights_only=False
        )
    keys = list(splits["train"].keys())
    return {k: torch.cat([splits[s][k] for s in ["train", "val", "test"]], dim=0) for k in keys}


def collect_hw_probs(model, data, device):
    """
    Run model.generate with return_hw_probs=True over all respondents x their 2
    synthetic target strata (same loop as 04E run_inference).

    Returns:
        home_probs_all  np.ndarray (N_syn_calls, 48)  — raw sigmoid home probs
        work_probs_all  np.ndarray (N_syn_calls, 48)  — raw sigmoid work probs
        obs_home_all    np.ndarray (N_obs_rows,  48)  — binary observed home
        obs_work_all    np.ndarray (N_obs_rows,  48)  — binary observed work
    """
    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()

    home_prob_chunks = []
    work_prob_chunks = []
    obs_home_chunks = []
    obs_work_chunks = []

    for start in range(0, n, BATCH_SIZE):
        end = min(start + n, n)          # cap to n not start+BATCH_SIZE to avoid IndexError
        end = min(start + BATCH_SIZE, n)
        chunk = list(range(start, end))

        # Collect observed aux (home/work) for this chunk
        for i in chunk:
            obs_aux = data["aux_seq"][i].numpy()   # (48, 11): col0=home, col1=work
            obs_home_chunks.append(obs_aux[:, 0])  # (48,)
            obs_work_chunks.append(obs_aux[:, 1])  # (48,)

        # Build synthetic pairs (same 2-strata logic as 04E)
        syn_idx, syn_strata = [], []
        for i in chunk:
            s_obs = int(obs_strata_all[i])
            for s_tgt in [1, 2, 3]:
                if s_tgt != s_obs:
                    syn_idx.append(i)
                    syn_strata.append(s_tgt)

        if syn_idx:
            act_t  = data["act_seq"][syn_idx].to(device)
            aux_t  = data["aux_seq"][syn_idx].to(device)
            cond_t = data["cond_vec"][syn_idx].to(device)
            cidx_t = data["cycle_idx"][syn_idx].to(device)
            strat  = torch.tensor(syn_strata, dtype=torch.long, device=device)

            with torch.no_grad():
                (_, _, _, _, _,
                 g_home_probs, g_work_probs) = model.generate(
                    act_t, aux_t, cond_t, cidx_t, strat,
                    temperature=TEMPERATURE,
                    apply_safety=False,    # safety not needed for prob capture
                    return_hw_probs=True,
                )
            home_prob_chunks.append(g_home_probs.cpu().numpy())   # (B_syn, 48)
            work_prob_chunks.append(g_work_probs.cpu().numpy())   # (B_syn, 48)

        print(f"  Processed {end}/{n} respondents ({100.0 * end / n:.1f}%)", flush=True)

    home_probs = np.concatenate(home_prob_chunks, axis=0) if home_prob_chunks else np.zeros((0, N_SLOTS))
    work_probs = np.concatenate(work_prob_chunks, axis=0) if work_prob_chunks else np.zeros((0, N_SLOTS))
    obs_home   = np.stack(obs_home_chunks, axis=0) if obs_home_chunks else np.zeros((0, N_SLOTS))
    obs_work   = np.stack(obs_work_chunks, axis=0) if obs_work_chunks else np.zeros((0, N_SLOTS))
    return home_probs, work_probs, obs_home, obs_work


def compute_hw_diagnostic(head_label, obs_binary, syn_probs):
    """
    Compute G2/OW1 operating-point diagnostic for one head.

    Validator definition (G2 and OW1 both use the same pattern — UNWEIGHTED,
    NaN-aware):
        obs_prev  = np.nanmean(obs_block)  * 100   [== np.nanmean(obs==1) for binary]
        syn_prev  = np.nanmean(syn_probs >= 0.5) * 100

    Args:
        head_label  — "HOME" or "WORK"
        obs_binary  — (N_obs, 48) float, binary 0/1 from aux cols of observed rows
        syn_probs   — (N_syn, 48) float, raw sigmoid probabilities from generate()

    Returns dict with keys matching 04G row structure.
    """
    obs_prev     = float(np.nanmean(obs_binary)) * 100.0
    syn_mean_prob = float(np.nanmean(syn_probs)) * 100.0
    syn_prev_05  = float(np.nanmean(syn_probs >= 0.5)) * 100.0
    gap_05       = abs(obs_prev - syn_prev_05)
    calib_gap    = abs(obs_prev - syn_mean_prob)

    flat = syn_probs[~np.isnan(syn_probs)].ravel()
    if flat.size > 0 and not np.isnan(obs_prev):
        q = min(max(1.0 - obs_prev / 100.0, 0.0), 1.0)
        t_match = float(np.quantile(flat, q))
        syn_prev_t = float(np.nanmean(syn_probs >= t_match)) * 100.0
        gap_t = abs(obs_prev - syn_prev_t)
    else:
        t_match = float("nan")
        gap_t   = float("nan")

    verdict = "OPERATING-POINT" if calib_gap <= 3.0 else "LEARNED-DEFICIT"

    return dict(
        head=head_label,
        obs_prev=obs_prev,
        syn_mean_prob=syn_mean_prob,
        syn_prev_05=syn_prev_05,
        gap_05=gap_05,
        calib_gap=calib_gap,
        t_match=t_match,
        gap_t_match=gap_t,
        verdict=verdict,
    )


def main():
    args = parse_args()
    data_dir = args.data_dir or args.step4_dir
    ckpt_path = args.checkpoint or os.path.join(args.step4_dir, "checkpoints", "best_model.pt")

    print("=" * 64)
    print("3rdJ Step 4H — G2/OW1 Home/Work Operating-Point Diagnostic")
    print("=" * 64)
    print(f"  step4_dir:  {args.step4_dir}")
    print(f"  data_dir:   {data_dir}")
    print(f"  checkpoint: {ckpt_path}")

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  device:     {device}")

    print("\n[1/4] Loading tensor datasets...")
    data = load_all_data(data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    print("\n[2/4] Loading model checkpoint...")
    if not os.path.isfile(ckpt_path):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = JSeriesHybrid2Split(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded epoch {ckpt.get('epoch', '?')}  val_JS={ckpt.get('val_js', '?')}  "
          f"work_gap={ckpt.get('work_gap', '?')}")

    print("\n[3/4] Running generate() with return_hw_probs=True...")
    home_probs, work_probs, obs_home, obs_work = collect_hw_probs(model, data, device)
    print(f"  Collected home_probs: {home_probs.shape}  work_probs: {work_probs.shape}")
    print(f"  obs_home: {obs_home.shape}  obs_work: {obs_work.shape}")

    print("\n[4/4] Computing G2/OW1 diagnostics...")
    rows = [
        compute_hw_diagnostic("HOME", obs_home, home_probs),
        compute_hw_diagnostic("WORK", obs_work, work_probs),
    ]

    res = pd.DataFrame(rows)
    out_csv = os.path.join(args.step4_dir, "g2ow1_homework_diagnostic.csv")
    out_txt = os.path.join(args.step4_dir, "g2ow1_homework_diagnostic.txt")
    res.to_csv(out_csv, index=False)

    def fmt(x):
        return "   nan" if (isinstance(x, float) and np.isnan(x)) else f"{x:6.2f}"

    lines = []
    lines.append("G2/OW1 Home/Work Diagnostic (operating-point vs learned-deficit)")
    lines.append(f"step4_dir: {args.step4_dir}")
    lines.append(f"checkpoint: {ckpt_path}")
    lines.append(f"syn generate calls: {home_probs.shape[0]:,}  obs respondents: {obs_home.shape[0]:,}")
    lines.append(f"Validator definition: UNWEIGHTED np.nanmean (G2 and OW1 both)")
    lines.append(f"Verdict threshold: calib_gap <= 3.0 pp => OPERATING-POINT")
    lines.append("=" * 100)
    hdr = (f"{'head':<6} {'obs%':>7} {'meanP%':>8} {'prev@.5%':>10} "
           f"{'gap@.5':>7} {'calibGap':>9} {'t_match':>8} {'gap@t':>7}  verdict")
    lines.append(hdr)
    lines.append("-" * 100)
    for r in rows:
        t_str = "    nan" if np.isnan(r["t_match"]) else f"{r['t_match']:7.4f}"
        lines.append(
            f"{r['head']:<6} {fmt(r['obs_prev']):>7} "
            f"{fmt(r['syn_mean_prob']):>8} {fmt(r['syn_prev_05']):>10} "
            f"{fmt(r['gap_05']):>7} {fmt(r['calib_gap']):>9} "
            f"{t_str:>8} {fmt(r['gap_t_match']):>7}  {r['verdict']}"
        )
    lines.append("=" * 100)
    n_op = sum(1 for r in rows if r["verdict"] == "OPERATING-POINT")
    lines.append(f"OPERATING-POINT heads: {n_op}/{len(rows)}  "
                 f"(calib_gap<=3pp => threshold fix closes gap for free)")
    lines.append(f"LEARNED-DEFICIT heads: {len(rows) - n_op}/{len(rows)}  "
                 f"(need a model-side lever)")

    report = "\n".join(lines)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print("\n" + report, flush=True)
    print(f"\n[diag] wrote {out_txt}")
    print(f"[diag] wrote {out_csv}")


if __name__ == "__main__":
    main()
