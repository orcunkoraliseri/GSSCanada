#!/usr/bin/env python3
"""
3rdJ_04L_joint_rake_2split.py — Step 4L (Leg-2): Joint AT_HOME + AT_WORK Post-Hoc Raking

Closes G2 (AT_HOME under-predicted) and OW1 (AT_WORK over-predicted) on the R5 (lr1e4)
winner by per-(CYCLE_YEAR x DDAY_STRATA x slot) joint raking of the binary home/work
assignments. Adapts the Leg-1 04L calibration method for the two-channel (home + work)
Leg-2 model.

Method:
  1. Load tensors + R5 checkpoint; run generate(return_hw_probs=True) to get per-slot
     raw sigmoid probs for the home and work heads (no safety filter applied).
  2. From observed rows (IS_SYNTHETIC==0) in the R5 augmented_diaries.csv, compute
     per-(cy x stratum x slot) AT_HOME and AT_WORK rates UNWEIGHTED — matching the
     G2/OW1 validator definition exactly (np.nanmean over binary 0/1 values).
  3. For each (cy x stratum x slot) cell, assign the N_syn person-slots to {home=1,
     work=1, neither} via greedy global-confidence joint raking: sort all (person,
     channel) pairs by descending sigmoid probability; greedily assign each person to
     their highest-confidence eligible channel until quota is met.
     Guarantees: sum(home)==n_home, sum(work)==n_work, never home=1 AND work=1.
  4. Write raked augmented_diaries.csv to outputs_step4/sweep/R5_raked/ (does NOT
     overwrite R5_lr1e4). Activity (act30_*) and COP columns are carried forward
     untouched from R5 — the G3 co-presence threshold block is already applied there.

Usage (cluster):
    sbatch 3rdJ_s4_2split_rakeL.sh

Usage (local):
    python 3rdJ_04L_joint_rake_2split.py
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import shutil
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

# ── Platform detection (mirrors 04E / 04H) ────────────────────────────────────
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
_R5_DIR       = os.path.join(_STEP4_SHARED, "sweep", "R5_lr1e4")
_RAKED_DIR    = os.path.join(_STEP4_SHARED, "sweep", "R5_raked")

N_SLOTS    = 48
TEMPERATURE = 0.8
BATCH_SIZE  = 256
CYCLES  = [2005, 2010, 2015, 2022]
STRATA  = [1, 2, 3]
HOM_COLS = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
WRK_COLS = [f"wrk30_{s:03d}" for s in range(1, N_SLOTS + 1)]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir",   default=None,
                   help="Dir with step4_{train,val,test}.pt (defaults to outputs_step4/)")
    p.add_argument("--r5_dir",     default=None,
                   help="R5 variant dir containing checkpoints/ + augmented_diaries.csv")
    p.add_argument("--output_dir", default=None,
                   help="Output dir for raked augmented_diaries.csv (default: R5_raked)")
    p.add_argument("--temperature", type=float, default=TEMPERATURE,
                   help="Generation temperature for the rake's model.generate "
                        "(should match the 04E temperature used to make the diaries; "
                        f"default {TEMPERATURE}).")
    return p.parse_args()


def load_all_data(data_dir: str):
    """Concatenate train/val/test tensor dicts (mirrors 04E)."""
    splits = {}
    for split in ["train", "val", "test"]:
        splits[split] = torch.load(
            os.path.join(data_dir, f"step4_{split}.pt"), map_location="cpu", weights_only=False
        )
    keys = list(splits["train"].keys())
    return {k: torch.cat([splits[s][k] for s in ["train", "val", "test"]], dim=0) for k in keys}


def collect_hw_probs(model, data, device):
    """
    Run generate(return_hw_probs=True) over all respondents x their 2 synthetic strata.

    Returns dict keyed by (occ_id, cycle_year, s_tgt) ->
        {"p_home": np.ndarray(48,), "p_work": np.ndarray(48,)}
    where p_home/p_work are the raw sigmoid outputs (apply_safety=False).
    """
    model.eval()
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    n = len(data["act_seq"])
    obs_strata_all = data["obs_strata"].numpy()
    cycle_year_all = data["cycle_year"].numpy()
    occ_ids_all    = data["occ_ids"].numpy()

    hw_probs = {}
    for start in range(0, n, BATCH_SIZE):
        end = min(start + BATCH_SIZE, n)
        chunk = list(range(start, end))

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
                (_, _, _, _, _, g_home_probs, g_work_probs) = model.generate(
                    act_t, aux_t, cond_t, cidx_t, strat,
                    temperature=TEMPERATURE,
                    apply_safety=False,
                    return_hw_probs=True,
                )
            g_hp = g_home_probs.cpu().numpy()   # (B_syn, 48)
            g_wp = g_work_probs.cpu().numpy()   # (B_syn, 48)

            for k, (i, s_tgt) in enumerate(zip(syn_idx, syn_strata)):
                key = (int(occ_ids_all[i]), int(cycle_year_all[i]), int(s_tgt))
                hw_probs[key] = {"p_home": g_hp[k], "p_work": g_wp[k]}

        print(f"  Collected {end}/{n} respondents ({100.0 * end / n:.1f}%)", flush=True)

    return hw_probs


def _joint_rake_slot(p_home, p_work, n_home, n_work):
    """
    Greedy global-confidence joint assignment for one (cell x slot).

    Inputs:
        p_home, p_work  — (N,) float32 sigmoid probabilities per person
        n_home, n_work  — integer target counts to assign (1s)

    Outputs:
        new_home, new_work  — (N,) float32 binary arrays

    Guarantees:
        sum(new_home) == n_home
        sum(new_work) == n_work
        no person has new_home==1 AND new_work==1
    """
    N = len(p_home)
    n_home = max(0, min(int(n_home), N))
    n_work = max(0, min(int(n_work), N))

    # Feasibility guard: n_home + n_work must not exceed total persons
    if n_home + n_work > N:
        scale  = N / (n_home + n_work)
        n_home = int(round(n_home * scale))
        n_work = N - n_home

    new_home = np.zeros(N, dtype=np.float32)
    new_work = np.zeros(N, dtype=np.float32)
    if n_home == 0 and n_work == 0:
        return new_home, new_work

    # Build global sorted action list: 2N entries, one per (person, channel)
    actions_prob    = np.empty(2 * N, dtype=np.float32)
    actions_channel = np.empty(2 * N, dtype=np.uint8)
    actions_idx     = np.empty(2 * N, dtype=np.int32)
    actions_prob[:N]    = p_home.astype(np.float32)
    actions_channel[:N] = 0           # 0 = home
    actions_idx[:N]     = np.arange(N, dtype=np.int32)
    actions_prob[N:]    = p_work.astype(np.float32)
    actions_channel[N:] = 1           # 1 = work
    actions_idx[N:]     = np.arange(N, dtype=np.int32)

    order    = np.argsort(-actions_prob, kind="stable")
    assigned = np.zeros(N, dtype=np.uint8)   # 0=unassigned, 1=home, 2=work
    rem_home = n_home
    rem_work = n_work

    for k in order:
        if rem_home == 0 and rem_work == 0:
            break
        ch = int(actions_channel[k])
        i  = int(actions_idx[k])
        if assigned[i] != 0:
            continue
        if ch == 0 and rem_home > 0:
            new_home[i] = 1.0
            assigned[i] = 1
            rem_home   -= 1
        elif ch == 1 and rem_work > 0:
            new_work[i] = 1.0
            assigned[i] = 2
            rem_work   -= 1

    return new_home, new_work


def main():
    global TEMPERATURE
    args = parse_args()
    TEMPERATURE = args.temperature   # rake's generate() reads the module global at call time
    data_dir   = args.data_dir   or _STEP4_SHARED
    r5_dir     = args.r5_dir     or _R5_DIR
    output_dir = args.output_dir or _RAKED_DIR
    ckpt_path  = os.path.join(r5_dir, "checkpoints", "best_model.pt")
    aug_src    = os.path.join(r5_dir, "augmented_diaries.csv")
    raked_path = os.path.join(output_dir, "augmented_diaries.csv")
    prov_path  = os.path.join(output_dir, "g2ow1_rake_provenance.json")

    print("=" * 64)
    print("3rdJ Step 4L (Leg-2) — Joint AT_HOME + AT_WORK Raking")
    print("=" * 64)
    print(f"  data_dir:   {data_dir}")
    print(f"  r5_dir:     {r5_dir}")
    print(f"  output_dir: {output_dir}")
    print(f"  checkpoint: {ckpt_path}")
    print(f"  aug source: {aug_src}")
    print(f"  temperature: {TEMPERATURE}")

    os.makedirs(output_dir, exist_ok=True)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"  device:     {device}")

    # ── Step 1: Load tensors ──────────────────────────────────────────────────
    print("\n[1/5] Loading tensor datasets...")
    data = load_all_data(data_dir)
    n = len(data["act_seq"])
    print(f"  Total respondents: {n}")

    # ── Step 2: Load model checkpoint ────────────────────────────────────────
    print("\n[2/5] Loading model checkpoint...")
    if not os.path.isfile(ckpt_path):
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
    ckpt  = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = JSeriesHybrid2Split(ckpt["model_config"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"  Loaded epoch {ckpt.get('epoch','?')}  val_JS={ckpt.get('val_js','?')}  "
          f"work_gap={ckpt.get('work_gap','?')}")

    # ── Step 3: Collect raw sigmoid probs ────────────────────────────────────
    print("\n[3/5] Running generate(return_hw_probs=True) for sigmoid probs...")
    hw_probs = collect_hw_probs(model, data, device)
    print(f"  Collected {len(hw_probs):,} (occ_id, cy, s_tgt) entries")

    # ── Step 4: Load R5 aug CSV and apply per-(cy x s x slot) joint rake ─────
    print("\n[4/5] Loading R5 augmented_diaries.csv and applying joint rake...")
    if not os.path.isfile(aug_src):
        raise FileNotFoundError(f"R5 augmented_diaries.csv not found: {aug_src}")
    aug = pd.read_csv(aug_src, low_memory=False)
    print(f"  Loaded: {aug.shape}  "
          f"(IS_SYN=0: {(aug['IS_SYNTHETIC']==0).sum():,}, "
          f"IS_SYN=1: {(aug['IS_SYNTHETIC']==1).sum():,})")

    for col in HOM_COLS[:1] + WRK_COLS[:1] + ["occID", "CYCLE_YEAR", "DDAY_STRATA", "IS_SYNTHETIC"]:
        if col not in aug.columns:
            raise ValueError(f"Missing required column in aug CSV: {col}")

    provenance   = {}
    total_cells  = len(CYCLES) * len(STRATA)
    cell_count   = 0

    for cy in CYCLES:
        for s in STRATA:
            cell_count += 1
            obs_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                        & (aug["IS_SYNTHETIC"] == 0))
            syn_mask = ((aug["CYCLE_YEAR"] == cy) & (aug["DDAY_STRATA"] == s)
                        & (aug["IS_SYNTHETIC"] == 1))
            osub = aug[obs_mask]
            ssub = aug[syn_mask]
            n_syn = len(ssub)
            n_obs = len(osub)

            if n_syn == 0:
                print(f"  [{cell_count}/{total_cells}] cy={cy} s={s}: no synthetic rows — skip")
                continue

            print(f"  [{cell_count}/{total_cells}] cy={cy} s={s}: {n_obs} obs, {n_syn} syn",
                  flush=True)

            ssub_idx = ssub.index
            ssub_occ = ssub["occID"].to_numpy(dtype=int)

            # Build (n_syn, 48) sigmoid probability matrices
            p_home_mat  = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            p_work_mat  = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            n_missing = 0
            for k, occ_id in enumerate(ssub_occ):
                key = (int(occ_id), int(cy), int(s))
                if key in hw_probs:
                    p_home_mat[k] = hw_probs[key]["p_home"]
                    p_work_mat[k] = hw_probs[key]["p_work"]
                else:
                    p_home_mat[k] = 0.5   # no-preference fallback
                    p_work_mat[k] = 0.5
                    n_missing += 1
            if n_missing > 0:
                print(f"    WARNING: {n_missing}/{n_syn} syn rows had no hw_probs key "
                      f"— used 0.5 fallback")

            # Observed per-slot rates (used as rake targets)
            obs_hom_arr = (osub[HOM_COLS].to_numpy(dtype=float)
                           if n_obs > 0 else np.full((0, N_SLOTS), np.nan))
            obs_wrk_arr = (osub[WRK_COLS].to_numpy(dtype=float)
                           if n_obs > 0 else np.full((0, N_SLOTS), np.nan))

            # Pre-rake aggregate rates (for provenance)
            before_home = float(np.nanmean(aug.loc[syn_mask, HOM_COLS].to_numpy(dtype=float))) * 100
            before_work = float(np.nanmean(aug.loc[syn_mask, WRK_COLS].to_numpy(dtype=float))) * 100
            obs_home_agg = float(np.nanmean(obs_hom_arr)) * 100 if n_obs > 0 else float("nan")
            obs_work_agg = float(np.nanmean(obs_wrk_arr)) * 100 if n_obs > 0 else float("nan")

            # Per-slot joint rake
            new_hom_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            new_wrk_mat = np.zeros((n_syn, N_SLOTS), dtype=np.float32)
            slot_prov = []
            for j in range(N_SLOTS):
                obs_r_hom = float(np.nanmean(obs_hom_arr[:, j])) if n_obs > 0 else 0.0
                obs_r_wrk = float(np.nanmean(obs_wrk_arr[:, j])) if n_obs > 0 else 0.0
                n_home = int(round(obs_r_hom * n_syn))
                n_work = int(round(obs_r_wrk * n_syn))

                new_h, new_w = _joint_rake_slot(p_home_mat[:, j], p_work_mat[:, j],
                                                n_home, n_work)
                new_hom_mat[:, j] = new_h
                new_wrk_mat[:, j] = new_w

                slot_prov.append({
                    "slot":          j + 1,
                    "obs_home_pct":  round(obs_r_hom * 100, 3),
                    "obs_work_pct":  round(obs_r_wrk * 100, 3),
                    "n_home":        n_home,
                    "n_work":        n_work,
                    "ach_home_pct":  round(float(new_h.mean()) * 100, 3),
                    "ach_work_pct":  round(float(new_w.mean()) * 100, 3),
                })

            # Write raked values back into aug DataFrame
            aug.loc[ssub_idx, HOM_COLS] = new_hom_mat.astype(float)
            aug.loc[ssub_idx, WRK_COLS] = new_wrk_mat.astype(float)

            after_home = float(np.nanmean(new_hom_mat)) * 100
            after_work = float(np.nanmean(new_wrk_mat)) * 100
            both_viol  = int(np.sum((new_hom_mat == 1) & (new_wrk_mat == 1)))

            provenance[f"cy{cy}_s{s}"] = {
                "n_obs":          n_obs,
                "n_syn":          n_syn,
                "n_missing_keys": n_missing,
                "obs_home_agg_pct":  round(obs_home_agg, 3),
                "obs_work_agg_pct":  round(obs_work_agg, 3),
                "before_home_pct":   round(before_home, 3),
                "before_work_pct":   round(before_work, 3),
                "after_home_pct":    round(after_home, 3),
                "after_work_pct":    round(after_work, 3),
                "mutual_excl_viol":  both_viol,
                "slots": slot_prov,
            }
            print(f"    home: {before_home:.1f}% → {after_home:.1f}% (obs {obs_home_agg:.1f}%)  "
                  f"work: {before_work:.1f}% → {after_work:.1f}% (obs {obs_work_agg:.1f}%)  "
                  f"both=1: {both_viol}", flush=True)

    # ── Step 5: Atomic write ──────────────────────────────────────────────────
    print("\n[5/5] Writing raked CSV + provenance JSON...")

    # Global mutual-exclusion spot-check across all rows
    total_both = 0
    for j in range(1, N_SLOTS + 1):
        h = aug[f"hom30_{j:03d}"]
        w = aug[f"wrk30_{j:03d}"]
        total_both += int(((h == 1) & (w == 1)).sum())
    print(f"  Global hom==1 AND wrk==1 violations after rake: {total_both} (expect 0)")

    # Atomic write: .tmp + os.replace
    tmp_path = raked_path + ".tmp"
    aug.to_csv(tmp_path, index=False)
    n_written = sum(1 for _ in open(tmp_path, encoding="utf-8")) - 1   # exclude header
    if n_written != len(aug):
        raise RuntimeError(
            f"Row count mismatch writing {tmp_path}: "
            f"wrote {n_written}, expected {len(aug)}"
        )
    os.replace(tmp_path, raked_path)
    print(f"  Wrote {len(aug):,} rows -> {raked_path}")

    # Copy G3 thresholds provenance from R5 (COP columns are unchanged)
    g3_src = os.path.join(r5_dir, "g3_copresence_thresholds.json")
    if os.path.isfile(g3_src):
        shutil.copy2(g3_src, os.path.join(output_dir, "g3_copresence_thresholds.json"))
        print(f"  Copied G3 thresholds JSON from R5 -> {output_dir}")

    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    print(f"  Wrote rake provenance -> {prov_path}")

    print(f"\nOK 04L (Leg-2) complete.")
    print(f"  Raked dir:  {output_dir}")
    print(f"  Next step (on the cluster):")
    print(f"    sbatch --job-name=R5raked_val --export=ALL,VARIANT=R5_raked "
          f"3rdJ_s4_2split_valsweep.sh")


if __name__ == "__main__":
    main()
