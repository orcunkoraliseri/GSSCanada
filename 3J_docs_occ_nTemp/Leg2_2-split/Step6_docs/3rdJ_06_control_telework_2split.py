# -*- coding: utf-8 -*-
"""
3rdJ_06_control_telework_2split.py
STEP-6 (Leg-2) CONTROL TEST — "Is TELEWORK learnable?" diagnostic probe.

WHY THIS EXISTS
---------------
The degenerate Step-6 run (job 982868) produced IDENTICAL occupancy across all
three WFH bands. Root cause (confirmed by code read, 2026-06-24): Step6Dataset
SELF-PAIRS each diary (src == tgt == same row), turning the 04B source->target
translator into an identity autoencoder that copies the ground-truth occupancy
fed through aux_seq. Every Step-6 checkpoint (W_2005..W_pooled_2030) is therefore
a COPIER and is useless for this question.

This probe does NOT touch the broken Step-6 checkpoints. It loads the GOOD
Step-4 translator (R5_lr1e4 best_model.pt — trained with 04C cross-day KNN pairs)
and asks the single decision-driving question:

    On the correctly-trained translator, when we flip TELEWORK 0 -> 1 on the SAME
    employed 2022 respondents (everything else held fixed), does business-hours
    AT_HOME actually move?

    MOVES  -> TELEWORK is learnable; the bug is purely Step-6's self-pairing.
              Fix = rebuild Step-6 progressive training with 04C/04D cross-day
              pairs, then re-run.  (the expensive ~8 h GPU retrain is justified)

    FLAT   -> the learned TELEWORK response is ~0 even on the good model.
              No pairing fix will create band sensitivity; switch to the
              documented post-hoc TELEWORK-reweight fallback instead.

It faithfully reuses the REAL inference plumbing (build_tensors_from_df,
build_model, model.generate) imported from the Step-6 module, so the result
is directly comparable to the forecast that collapsed.

DESIGN
------
* Cohort: employed (LFTAG==1), weekday (DDAY_STRATA==1), 2022 respondents.
* Contrast: ALL-0 vs ALL-1 TELEWORK (maximal contrast — if even this does not
  move occupancy, the response is flat). Same source rows in both arms.
* temperature: 0.0 (deterministic — isolates the TELEWORK bit with zero sampling
  noise) AND 0.8 (the actual forecast temperature, for direct comparison to the
  collapsed run).
* The encoder still receives the real 2022 source aux_seq — exactly as the
  forecast does — so this measures whether TELEWORK can pull the heads off the
  source anchor in the realistic path.

CPU-only, no GPU required (small model, a few thousand rows). Runs in minutes.

Usage (defaults resolve to the R5_lr1e4 artifacts on Speed):
    python 3rdJ_06_control_telework_2split.py --n 3000
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys

import numpy as np
import pandas as pd
import torch

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Import the Step-6 module (import-safe: __main__-guarded). This transitively
#    imports the LOCKED 04B model + 04D helpers and resolves Speed/Windows paths. ─
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
_s6 = importlib.import_module("3rdJ_06_longitudinalForecasting_2split")

build_tensors_from_df = _s6.build_tensors_from_df
build_model           = _s6.build_model
load_feature_config   = _s6.load_feature_config
BIZ_SLOTS_0IDX        = _s6.BIZ_SLOTS_0IDX
STEP4_DATA            = _s6.STEP4_DATA

R5_DIR      = os.path.join(STEP4_DATA, "sweep", "R5_lr1e4")
R5_CKPT     = os.path.join(R5_DIR, "checkpoints", "best_model.pt")
R5_DATA     = os.path.join(R5_DIR, "augmented_diaries.csv")


def _generate_occupancy(model, df, feat_cfg, device, temperature):
    """Run model.generate over df; return (home (N,48), work (N,48), act (N,48))."""
    tensors = build_tensors_from_df(df, feat_cfg, device)
    N = len(df)
    bs = 256
    homes, works, acts = [], [], []
    with torch.no_grad():
        for s in range(0, N, bs):
            sl = slice(s, s + bs)
            g_act, g_home, g_work, _, _ = model.generate(
                tensors["act_seq"][sl],
                tensors["aux_seq"][sl],
                tensors["cond_vec"][sl],
                tensors["cycle_idx"][sl],
                tensors["obs_strata"][sl],
                temperature=temperature,
            )
            homes.append(g_home.cpu())
            works.append(g_work.cpu())
            acts.append(g_act.cpu())
    return (torch.cat(homes).numpy(),
            torch.cat(works).numpy(),
            torch.cat(acts).numpy())


def _wfh_proxy(home, act):
    """WFH_RATE proxy over business-hours slots: AT_HOME OR Work-activity (0-idx 0)."""
    h_biz = home[:, BIZ_SLOTS_0IDX]
    a_biz = act[:, BIZ_SLOTS_0IDX]
    return float(((h_biz == 1) | (a_biz == 0)).mean())


def run_control(data_path, ckpt_path, n, strata, device):
    print("=" * 72)
    print("STEP-6 CONTROL — TELEWORK sensitivity on the GOOD Step-4 translator")
    print("=" * 72)
    print(f"  checkpoint : {ckpt_path}")
    print(f"  data       : {data_path}")
    print(f"  device     : {device}")

    if not os.path.isfile(ckpt_path):
        sys.exit(f"[FATAL] checkpoint not found: {ckpt_path}")
    if not os.path.isfile(data_path):
        sys.exit(f"[FATAL] data not found: {data_path}")

    feat_cfg = load_feature_config()
    df = pd.read_csv(data_path, low_memory=False)

    # Cohort: 2022 weekday employed
    m = (df["CYCLE_YEAR"] == 2022)
    if "DDAY_STRATA" in df.columns:
        m &= (df["DDAY_STRATA"] == strata)
    if "LFTAG" in df.columns:
        m &= (df["LFTAG"] == 1)
    df = df[m].copy().reset_index(drop=True)
    print(f"  cohort     : 2022 / strata={strata} / employed -> {len(df):,} rows")
    if len(df) == 0:
        sys.exit("[FATAL] empty cohort after filtering.")
    if n and len(df) > n:
        df = df.sample(n=n, random_state=42).reset_index(drop=True)
        print(f"  sampled    : {len(df):,} rows (seed 42)")

    # Load the GOOD Step-4 translator once (build_model adopts the ckpt architecture).
    model, _, mc = build_model(feat_cfg, False, device, ckpt_path)
    model.eval()
    print(f"  model cfg  : d_model={mc.get('d_model')} N_enc={mc.get('N_enc')} "
          f"N_dec={mc.get('N_dec')} d_cond={mc.get('d_cond')}")

    # Two arms: all-TELEWORK=0 vs all-TELEWORK=1, identical source rows.
    arms = {}
    for tw in (0, 1):
        d = df.copy()
        d["TELEWORK"] = tw
        d["TELEWORK_KNOWN"] = 1
        d["CYCLE_YEAR"] = 2022  # inference embedding (mirrors forecast path)
        arms[tw] = d

    print("\n  TELEWORK=1 should RAISE business-hours AT_HOME and LOWER AT_WORK.\n")
    print(f"  {'temp':>5} {'home_TW0':>9} {'home_TW1':>9} {'dHome':>8} "
          f"{'work_TW0':>9} {'work_TW1':>9} {'dWork':>8} "
          f"{'WFH_TW0':>8} {'WFH_TW1':>8} {'rows_chg':>8}")

    det_dhome = None
    for temp in (0.0, 0.8):
        h0, w0, a0 = _generate_occupancy(model, arms[0], feat_cfg, device, temp)
        h1, w1, a1 = _generate_occupancy(model, arms[1], feat_cfg, device, temp)

        hb0, hb1 = h0[:, BIZ_SLOTS_0IDX], h1[:, BIZ_SLOTS_0IDX]
        wb0, wb1 = w0[:, BIZ_SLOTS_0IDX], w1[:, BIZ_SLOTS_0IDX]

        d_home = hb1.mean() - hb0.mean()
        d_work = wb1.mean() - wb0.mean()
        wfh0, wfh1 = _wfh_proxy(h0, a0), _wfh_proxy(h1, a1)

        # fraction of respondents whose business-hours home-fraction changed at all
        f0 = hb0.mean(axis=1)
        f1 = hb1.mean(axis=1)
        rows_changed = float((np.abs(f1 - f0) > 1e-9).mean())

        print(f"  {temp:>5.1f} {hb0.mean():>9.4f} {hb1.mean():>9.4f} {d_home:>+8.4f} "
              f"{wb0.mean():>9.4f} {wb1.mean():>9.4f} {d_work:>+8.4f} "
              f"{wfh0:>8.4f} {wfh1:>8.4f} {rows_changed:>8.3f}")

        if temp == 0.0:
            det_dhome = d_home

    # ── Verdict from the deterministic (temp=0) arm ───────────────────────────
    print("\n" + "-" * 72)
    if det_dhome is None:
        verdict = "INCONCLUSIVE — no deterministic arm computed."
    elif det_dhome >= 0.02:
        verdict = (f"MOVES (dHome={det_dhome:+.4f} >= +0.02). TELEWORK IS learnable on the "
                   f"good translator -> the bug is purely Step-6 self-pairing. "
                   f"PROCEED with the 04C/04D cross-day-pairing retrain.")
    elif abs(det_dhome) < 0.005:
        verdict = (f"FLAT (|dHome|={abs(det_dhome):.4f} < 0.005). Learned TELEWORK response "
                   f"is ~0 even on the good model -> a pairing fix will NOT create band "
                   f"sensitivity. Use the documented POST-HOC TELEWORK-REWEIGHT fallback.")
    else:
        verdict = (f"WEAK (dHome={det_dhome:+.4f}). Borderline learned response; inspect "
                   f"the per-temp table before committing to the ~8 h retrain.")
    print("VERDICT:", verdict)
    print("-" * 72)


def parse_args():
    p = argparse.ArgumentParser(description="Step-6 TELEWORK sensitivity control probe")
    p.add_argument("--data", default=R5_DATA,
                   help="augmented_diaries.csv (default: R5_lr1e4 raw on Speed)")
    p.add_argument("--ckpt", default=R5_CKPT,
                   help="Step-4 translator checkpoint (default: R5_lr1e4 best_model.pt)")
    p.add_argument("--n", type=int, default=3000,
                   help="cohort sample size (default 3000; 0 = all)")
    p.add_argument("--strata", type=int, default=1,
                   help="DDAY_STRATA to test (default 1 = weekday)")
    p.add_argument("--cpu", action="store_true", help="force CPU even if CUDA present")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dev = torch.device("cuda" if (torch.cuda.is_available() and not args.cpu) else "cpu")
    run_control(args.data, args.ckpt, args.n, args.strata, dev)
