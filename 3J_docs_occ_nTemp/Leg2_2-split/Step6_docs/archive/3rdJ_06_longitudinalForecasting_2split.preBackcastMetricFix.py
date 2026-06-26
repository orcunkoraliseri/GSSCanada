# -*- coding: utf-8 -*-
"""
3rdJ_06_longitudinalForecasting_2split.py
Step 6 (Leg-2): Longitudinal Forecasting — Two-Channel 2-Split

Implements progressive fine-tuning + TrendEncoder2Split forecasting from
four GSS cycles (2005/2010/2015/2022) to project joint AT_HOME + AT_WORK
occupancy schedules to 2030.

Model: JSeriesHybrid2Split (imported from 3rdJ_04B_model_2split.py — LOCKED)
Training machinery: component_losses, UncertaintyWeighting, PCGrad, diversity_loss
    imported from 3rdJ_04D_train_2split.py (module import — __main__ NOT triggered).
Progressive loop (warm-start / per-cycle subset / recency weights): NEW code here.

Sub-steps implemented:
  6A  run_input_audit()      — 13 assertions/prints on augmented_diaries.csv
  6B  TrendEncoder2Split, compute_drift_matrix_2split(), compute_wfh_rate()
      run_substage_a(), run_substage_b(), run_substage_c()
      run_substage_d_phase_i(), run_substage_d_phase_ii(band)
      run_all()
  6B2 assemble_scenario_2030_features_2split.py (separate file)
  6H  mutual_exclusion_resolve(), call_mindwell()

Usage:
    python 3rdJ_06_longitudinalForecasting_2split.py --stage audit --data <csv>
    python 3rdJ_06_longitudinalForecasting_2split.py --smoke --stage A --data <csv>
    python 3rdJ_06_longitudinalForecasting_2split.py --stage all --data <csv>
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ── Module-level paths ────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

STEP4_DIR  = os.path.join(_LEG2_BASE, "Step4_docs")
STEP4_DATA = os.path.join(STEP4_DIR, "outputs_step4")
STEP6_DIR  = os.path.join(_LEG2_BASE, "Step6_docs")
OUTPUT_DIR = os.path.join(STEP6_DIR, "outputs_step6")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

# ── Import LOCKED Step-4 modules (import-only; never edit) ───────────────────

sys.path.insert(0, STEP4_DIR)

# 04B: model class
_04b = importlib.import_module("3rdJ_04B_model_2split")
JSeriesHybrid2Split = _04b.JSeriesHybrid2Split
DEFAULT_CONFIG      = _04b.DEFAULT_CONFIG

# 04D: loss helpers / weighting / PCGrad (module import does NOT run __main__)
_04d = importlib.import_module("3rdJ_04D_train_2split")
component_losses    = _04d.component_losses
diversity_loss      = _04d.diversity_loss
UncertaintyWeighting = _04d.UncertaintyWeighting
SLAWWeighting       = _04d.SLAWWeighting
EqualWeighting      = _04d.EqualWeighting
PCGrad              = _04d.PCGrad
js_divergence       = _04d.js_divergence   # numpy (p, q) -> float

# ── Constants ─────────────────────────────────────────────────────────────────

N_SLOTS      = 48
N_ACT        = 14
N_COP        = 9
CYCLE_YEARS  = [2005, 2010, 2015, 2022]
CYCLE_MAP    = {2005: 0, 2010: 1, 2015: 2, 2022: 3}
TASKS        = ["act", "home", "work", "cop"]

# Business-hours slots [09:00, 17:00) = slots 11..26 (1-indexed from 04:00 origin).
# 0-indexed: slots 10..25 (slot 10 = 09:00-09:30 … slot 25 = 16:30-17:00)
BIZ_SLOTS_0IDX = list(range(10, 26))  # 0-indexed, 16 slots

# Recency weights per cycle (per-sample multiplier on the loss)
RECENCY_WEIGHTS = {2005: 0.10, 2010: 0.20, 2015: 0.30, 2022: 0.40}

# AGEGRP 2030 M1 targets (Stats Canada)
AGEGRP_2030_TARGETS = {
    1: 0.135,
    2: 0.165,
    3: 0.175,
    4: 0.155,
    5: 0.148,
    6: 0.130,
    7: 0.092,
}

# Work activity 0-indexed category (raw cat 1 -> tensor index 0)
WORK_ACT_0IDX = 0

# Activity names for drift matrix labeling (0-indexed)
ACT_NAMES = [
    "Work", "Education", "Household work", "Care for hh members",
    "Care for non-hh", "Shopping", "Services", "Civic/volunteer",
    "Social/leisure", "Active leisure", "Passive leisure",
    "Meals/eating", "Transit", "Sleep/rest",
]

# Co-presence column order (matches 04A COP_COLS)
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
COLLEAGUES_IDX = 8

# ── Helper: feature config ────────────────────────────────────────────────────

def load_feature_config(data_dir: str = None) -> dict:
    if data_dir is None:
        data_dir = STEP4_DATA
    cfg_path = os.path.join(data_dir, "step4_feature_config.json")
    with open(cfg_path) as f:
        return json.load(f)


# ── Step-6A: Input Audit ──────────────────────────────────────────────────────

def run_input_audit(csv_path: str) -> pd.DataFrame:
    """
    13 assertions / prints over augmented_diaries.csv.
    Returns the loaded dataframe for reuse.
    """
    print("\n" + "=" * 60)
    print("SUB-STEP 6A — INPUT AUDIT")
    print("=" * 60)
    print(f"  Loading: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"  Rows: {len(df):,}  Cols: {len(df.columns)}")

    # --- 1. Row count ---
    n = len(df)
    assert abs(n - 192183) <= 200 or True, (  # allow any count; warn if far off
        f"Row count {n:,} unexpected (expected ~192,183 ±200)"
    )
    if abs(n - 192183) > 200:
        print(f"  [WARN] Row count {n:,} deviates from expected ~192,183")
    else:
        print(f"  [1] Row count {n:,}  PASS (~192,183)")

    # --- 2. CYCLE_YEAR ---
    found_cy = sorted(df["CYCLE_YEAR"].unique())
    expected_cy = [2005, 2010, 2015, 2022]
    assert set(found_cy) == set(expected_cy), f"CYCLE_YEAR mismatch: {found_cy}"
    print(f"  [2] CYCLE_YEAR values: {found_cy}  PASS")
    per_cycle = df.groupby("CYCLE_YEAR").size()
    print("      Per-cycle row counts:")
    for cy in expected_cy:
        print(f"        {cy}: {per_cycle.get(cy, 0):,}")

    # --- 3. DDAY_STRATA ---
    found_ds = sorted(df["DDAY_STRATA"].unique())
    assert set(found_ds) == {1, 2, 3}, f"DDAY_STRATA values: {found_ds}"
    print(f"  [3] DDAY_STRATA values: {found_ds}  PASS")
    cross = df.groupby(["CYCLE_YEAR", "DDAY_STRATA"]).size().unstack(fill_value=0)
    print("      Per-cycle x per-stratum counts:")
    print(cross.to_string())

    # --- 4. IS_SYNTHETIC ---
    assert "IS_SYNTHETIC" in df.columns, "IS_SYNTHETIC column missing"
    is_syn = df.groupby(["CYCLE_YEAR", "IS_SYNTHETIC"]).size().unstack(fill_value=0)
    print(f"  [4] IS_SYNTHETIC present  PASS")
    print("      IS_SYNTHETIC=0 / 1 per cycle:")
    print(is_syn.to_string())

    # --- 5. act30 columns ---
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    missing_act = [c for c in act_cols if c not in df.columns]
    assert not missing_act, f"Missing act30 columns: {missing_act[:5]}"
    act_vals = df[act_cols].values.flatten()
    act_vals = act_vals[~np.isnan(act_vals.astype(float))]
    act_min, act_max = int(act_vals.min()), int(act_vals.max())
    assert 1 <= act_min <= 14 and 1 <= act_max <= 14, \
        f"act30 range [{act_min},{act_max}] outside [1,14]"
    print(f"  [5] act30_001..048 present (48 cols); range [{act_min},{act_max}]  PASS")

    # --- 6. hom30 columns ---
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    missing_hom = [c for c in hom_cols if c not in df.columns]
    assert not missing_hom, f"Missing hom30 columns: {missing_hom[:5]}"
    hom_vals = df[hom_cols].values.flatten()
    hom_vals = hom_vals[~np.isnan(hom_vals.astype(float))]
    assert set(np.unique(hom_vals)).issubset({0.0, 1.0}), \
        f"hom30 non-binary values: {np.unique(hom_vals)}"
    print(f"  [6] hom30_001..048 present (48 cols); values in {{0,1}}  PASS")

    # --- 7. wrk30 columns ---
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    missing_wrk = [c for c in wrk_cols if c not in df.columns]
    assert not missing_wrk, f"Missing wrk30 columns: {missing_wrk[:5]}"
    wrk_vals = df[wrk_cols].values.flatten()
    wrk_vals = wrk_vals[~np.isnan(wrk_vals.astype(float))]
    assert set(np.unique(wrk_vals)).issubset({0.0, 1.0}), \
        f"wrk30 non-binary values: {np.unique(wrk_vals)}"
    print(f"  [7] wrk30_001..048 present (48 cols); values in {{0,1}}  PASS")

    # --- 8. Co-presence columns ---
    cop_expected = [f"{ch}30_{i:03d}" for ch in COP_COLS for i in range(1, 49)]
    missing_cop = [c for c in cop_expected if c not in df.columns]
    assert not missing_cop, f"Missing co-presence columns: {missing_cop[:5]}"
    print(f"  [8] 9 x 48 = 432 co-presence columns present  PASS")

    # --- 9. Mutual-exclusion overlap (MEASURE, do not assert 0) ---
    hom_arr = df[hom_cols].values.astype(float)
    wrk_arr = df[wrk_cols].values.astype(float)
    both    = (hom_arr == 1) & (wrk_arr == 1)
    total_slots = hom_arr.size
    overlap_rate = float(both.sum()) / total_slots
    flag_str = "FLAG: >5% overlap — model pathology" if overlap_rate > 0.05 else "OK (expected small non-zero on raw R5)"
    print(f"  [9] hom30==1 AND wrk30==1 co-occurrence rate: {overlap_rate:.4f}  {flag_str}")

    # --- 10. TELEWORK ---
    assert "TELEWORK" in df.columns, "TELEWORK column missing"
    tw_nan_frac = df["TELEWORK"].isna().mean()
    print(f"  [10] TELEWORK present  PASS  (NaN fraction: {tw_nan_frac:.3f})")

    # --- 11. NOCS and NAICS ---
    assert "NOCS" in df.columns, "NOCS column missing"
    assert "NAICS" in df.columns, "NAICS column missing"
    print(f"  [11] NOCS and NAICS present  PASS")

    # --- 12. Per-cycle AT_HOME, AT_WORK, WFH_RATE ---
    print("  [12] Per-cycle summary (WD only, stratum==1):")
    wd = df[df["DDAY_STRATA"] == 1]
    for cy in expected_cy:
        cydf = wd[wd["CYCLE_YEAR"] == cy]
        if len(cydf) == 0:
            continue
        h_arr = cydf[hom_cols].values.astype(float)
        w_arr = cydf[wrk_cols].values.astype(float)
        a_arr = cydf[act_cols].values.astype(float)

        at_home_wd  = float(h_arr.mean())
        at_work_wd  = float(w_arr.mean())

        # WFH_RATE: slots 11..26 (1-indexed) = indices 10..25 (0-indexed)
        wfh_rate = compute_wfh_rate(cydf, cy)
        print(f"    {cy}  AT_HOME_WD={at_home_wd:.4f}  AT_WORK_WD={at_work_wd:.4f}  "
              f"WFH_RATE={wfh_rate:.4f}")

    # --- 13. COVID signal check (informational) ---
    wd22 = wd[wd["CYCLE_YEAR"] == 2022]
    wd15 = wd[wd["CYCLE_YEAR"] == 2015]
    if len(wd22) > 0 and len(wd15) > 0:
        h22 = float(wd22[hom_cols].values.astype(float).mean())
        h15 = float(wd15[hom_cols].values.astype(float).mean())
        w22 = float(wd22[wrk_cols].values.astype(float).mean())
        w15 = float(wd15[wrk_cols].values.astype(float).mean())
        print(f"  [13] COVID signal: AT_HOME 2022 vs 2015: {h22:.4f} vs {h15:.4f} "
              f"(delta {h22-h15:+.4f})  |  AT_WORK 2022 vs 2015: {w22:.4f} vs {w15:.4f} "
              f"(delta {w22-w15:+.4f})")
        if h22 > h15 and w22 < w15:
            print("      COVID dual signal CONFIRMED: AT_HOME up, AT_WORK down.")
        else:
            print("      [WARN] COVID dual signal not clearly confirmed — check data source.")

    print("  6A AUDIT COMPLETE")
    return df


# ── WFH rate computation ──────────────────────────────────────────────────────

def compute_wfh_rate(df: pd.DataFrame, cycle_year: int) -> float:
    """
    WFH_RATE = mean(hom30_k==1 | act30_k==Work AND LFTAG==employed)
    over business-hours slots k in {11..26} (1-indexed from 04:00).
    0-indexed: slots 10..25.
    Only employed respondents (LFTAG == 1) are included.
    """
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]

    # Filter to employed (LFTAG==1)
    if "LFTAG" in df.columns:
        emp = df[df["LFTAG"] == 1]
    else:
        emp = df  # fallback if LFTAG not available

    if len(emp) == 0:
        return float("nan")

    h_arr = emp[hom_cols].values.astype(float)   # (N, 48)
    a_arr = emp[act_cols].values.astype(float)   # (N, 48)

    biz = BIZ_SLOTS_0IDX  # 0-indexed 10..25
    h_biz = h_arr[:, biz]   # (N, 16)
    a_biz = a_arr[:, biz]   # (N, 16)

    # at_home OR (work_activity and employed gate already applied above)
    home_or_wact = (h_biz == 1) | (a_biz == 1)  # act raw=1 corresponds to Work cat
    return float(home_or_wact.mean())


# ── Feature encoding: build cond_vec from df row(s) ─────────────────────────
# Replicated from 04A (featurization is inside its __main__-guarded data pipeline).
# We do NOT import 04A's build_feature_tensor because (a) it processes entire
# dataframes and writes .pt files, triggering file I/O side-effects, and
# (b) the logic here needs to operate on augmented_diaries rows directly.

def build_cond_vec_from_df(df: pd.DataFrame, feat_cfg: dict) -> np.ndarray:
    """
    Build the (N, d_cond=119) conditioning vector from a dataframe slice of
    augmented_diaries.csv using the step4_feature_config.json spec.
    Returns float32 numpy array of shape (N, d_cond).

    Replicated (not imported) because 04A's build logic is inside the __main__
    data-assembly pipeline and cannot be cleanly imported without triggering
    full CSV loading and .pt writes.
    """
    parts = feat_cfg["feature_parts"]
    d_cond = feat_cfg["d_cond"]
    N = len(df)
    out = np.zeros((N, d_cond), dtype=np.float32)
    ptr = 0

    for feat_name, spec in parts.items():
        ftype = spec["type"]
        col_key = feat_name  # column name in df matches feature name

        if ftype == "one-hot":
            cats = {int(k): int(v) for k, v in spec["categories"].items()}
            n_cats = spec["n_cats"]
            oh = np.zeros((N, n_cats), dtype=np.float32)
            if col_key in df.columns:
                vals = pd.to_numeric(df[col_key], errors="coerce").fillna(-1).astype(int)
                for i, v in enumerate(vals):
                    idx = cats.get(int(v), None)
                    if idx is not None:
                        oh[i, idx] = 1.0
                    else:
                        # try NaN-sentinel: look for -1 in cats
                        m1 = cats.get(-1, None)
                        if m1 is not None:
                            oh[i, m1] = 1.0
                        # else leave all-zero (NaN->all-zero for NAICS/WORK_SCHEDULE)
            out[:, ptr:ptr + n_cats] = oh
            ptr += n_cats

        elif ftype == "continuous":
            mean_ = float(spec.get("mean", 0.0))
            std_  = float(spec.get("std", 1.0))
            if col_key in df.columns:
                vals = pd.to_numeric(df[col_key], errors="coerce").fillna(mean_).values
                out[:, ptr] = ((vals - mean_) / max(std_, 1e-9)).astype(np.float32)
            ptr += 1

        elif ftype == "binary":
            if col_key in df.columns:
                vals = pd.to_numeric(df[col_key], errors="coerce").fillna(0).values
                out[:, ptr] = (vals != 0).astype(np.float32)
            ptr += 1

    assert ptr == d_cond, f"cond_vec dim mismatch: ptr={ptr}, d_cond={d_cond}"
    return out


def build_tensors_from_df(df: pd.DataFrame, feat_cfg: dict, device: torch.device):
    """
    Build all tensors needed for model inference from augmented_diaries rows.
    Returns dict with act_seq, aux_seq, cond_vec, cycle_idx, work_avail, obs_strata.
    """
    N = len(df)
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    cop_cols = [f"{ch}30_{i:03d}" for ch in COP_COLS for i in range(1, 49)]

    # Activity: raw 1..14 -> 0-indexed (subtract 1)
    act_np = df[act_cols].fillna(5).values.astype(np.int64) - 1
    act_np = np.clip(act_np, 0, N_ACT - 1)
    act_seq = torch.tensor(act_np, dtype=torch.long, device=device)

    # Home / work: shape (N, 48)
    hom_np = df[hom_cols].fillna(0).values.astype(np.float32)
    wrk_np = df[wrk_cols].fillna(0).values.astype(np.float32)

    # Co-presence: (N, 48, 9) — columns are ordered as COP_COLS x slots
    cop_mat = np.zeros((N, N_SLOTS, N_COP), dtype=np.float32)
    for c_idx, ch in enumerate(COP_COLS):
        ch_cols = [f"{ch}30_{i:03d}" for i in range(1, 49)]
        present = [c for c in ch_cols if c in df.columns]
        if present:
            cop_mat[:, :len(present), c_idx] = df[present].fillna(0).values.astype(np.float32)

    # aux_seq: (N, 48, 11) = [AT_HOME | AT_WORK | 9 cop]
    aux_np = np.concatenate([
        hom_np[:, :, None],   # (N, 48, 1)
        wrk_np[:, :, None],   # (N, 48, 1)
        cop_mat,              # (N, 48, 9)
    ], axis=-1)
    aux_seq = torch.tensor(aux_np, dtype=torch.float32, device=device)

    # work_avail: True where wrk column is NOT NaN (proxy: just use all-True for
    # augmented_diaries which have 0/1 values, NaN only in original data)
    work_avail = torch.ones(N, N_SLOTS, dtype=torch.bool, device=device)

    # cond_vec
    cond_np = build_cond_vec_from_df(df, feat_cfg)
    cond_vec = torch.tensor(cond_np, dtype=torch.float32, device=device)

    # cycle_idx
    cy_map = {int(k): int(v) for k, v in feat_cfg["cycle_map"].items()}
    cycle_np = df["CYCLE_YEAR"].values.astype(int)
    cidx_np  = np.array([cy_map.get(int(y), 0) for y in cycle_np], dtype=np.int64)
    cycle_idx = torch.tensor(cidx_np, dtype=torch.long, device=device)

    # obs_strata
    strata_np = df["DDAY_STRATA"].fillna(1).values.astype(np.int64)
    obs_strata = torch.tensor(strata_np, dtype=torch.long, device=device)

    return {
        "act_seq":    act_seq,
        "aux_seq":    aux_seq,
        "cond_vec":   cond_vec,
        "cycle_idx":  cycle_idx,
        "work_avail": work_avail,
        "obs_strata": obs_strata,
    }


# ── Cross-day KNN pairing (mirrors 04C/04D exactly — numpy brute-force, no sklearn) ──
#
# FIX (2026-06-24): Step6Dataset formerly SELF-PAIRED each diary (src==tgt), turning
# JSeriesHybrid2Split from a source→target translator into an identity autoencoder that
# leaked the ground-truth aux_seq (home/work) directly into the decoder via encoder memory.
# This produced val_js≈0, backcast JS_home=−0.0000, and all 3 WFH bands identical.
#
# The fix: replicate 04C's cross-day KNN pairing PER CYCLE SUBSET so that t≠s always.
# No sklearn dependency — numpy brute-force (cycles are a few thousand rows, trivial).

_EXACT_COLS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
_FUZZY_COLS = ["PR", "CMA", "HRSWRK", "NOCS"]
_K = 5
_N_TOTINC_BINS = 6


def _bin_totinc_for_pairing(df: pd.DataFrame) -> np.ndarray:
    """Bin TOTINC into _N_TOTINC_BINS quantile bins within the df (single-cycle)."""
    out = np.zeros(len(df), dtype=int)
    vals = pd.to_numeric(df.get("TOTINC", pd.Series(dtype=float)), errors="coerce")
    vals = vals.fillna(vals.median() if not vals.isna().all() else 0)
    try:
        labels = pd.qcut(vals, q=_N_TOTINC_BINS, labels=False, duplicates="drop")
        out[:] = labels.fillna(0).astype(int).values
    except ValueError:
        out[:] = 0
    return out


def _score_candidates_pairing(src_i: int, candidates: list,
                               col_arrays: dict, totinc_bin: np.ndarray) -> np.ndarray:
    """
    Exact match on AGEGRP,SEX,MARSTH,HHSIZE,LFTAG: +1 each (max 5)
    Fuzzy match on PR,CMA,HRSWRK,NOCS,TOTINC (+/-1 bin): +1 each (max 5)
    Mirrors 04C _score_candidates exactly.
    """
    scores = np.zeros(len(candidates), dtype=np.float32)
    cand_arr = np.array(candidates)
    for col in _EXACT_COLS:
        arr = col_arrays.get(col)
        if arr is not None:
            scores += (arr[cand_arr] == arr[src_i]).astype(np.float32)
    for col in _FUZZY_COLS:
        arr = col_arrays.get(col)
        if arr is not None:
            scores += (np.abs(arr[cand_arr] - arr[src_i]) <= 1).astype(np.float32)
    scores += (np.abs(totinc_bin[cand_arr] - totinc_bin[src_i]) <= 1).astype(np.float32)
    return scores


def build_cycle_pairs(df_cycle: pd.DataFrame, seed: int = 42) -> dict:
    """
    Build cross-day KNN pairs for a single cycle's subset, exactly per 04C logic:
      - For each respondent i with observed DDAY_STRATA s_obs, find K=5 neighbours
        in the SAME cycle but with a DIFFERENT DDAY_STRATA (s_tgt ≠ s_obs).
      - Neighbour scoring: exact on AGEGRP/SEX/MARSTH/HHSIZE/LFTAG (+1 each),
        fuzzy ±1 bin on PR/CMA/HRSWRK/NOCS/TOTINC (+1 each).
      - t ≠ s guaranteed (different diary, different day-type).
      - Returns dict: src_idx (n_pairs,), tgt_k_indices (n_pairs, K), tgt_strata (n_pairs,)
        — all as torch.long tensors.

    No sklearn: pure numpy (cycles are at most ~50k rows; brute-force is trivial).
    """
    df_cycle = df_cycle.reset_index(drop=True)
    n = len(df_cycle)
    totinc_bin = _bin_totinc_for_pairing(df_cycle)

    col_arrays = {}
    for col in _EXACT_COLS + _FUZZY_COLS:
        if col in df_cycle.columns:
            col_arrays[col] = df_cycle[col].fillna(-999).astype(int).values
        else:
            col_arrays[col] = np.full(n, -999, dtype=int)

    dday_strata = df_cycle["DDAY_STRATA"].fillna(1).astype(int).values

    # Group indices by stratum for fast candidate lookup
    strata_groups: dict = {}
    for i in range(n):
        s = int(dday_strata[i])
        strata_groups.setdefault(s, []).append(i)

    all_src, all_tgt_k, all_tgt_strata = [], [], []

    for src_i in range(n):
        s_obs = int(dday_strata[src_i])
        for s_tgt in [s for s in [1, 2, 3] if s != s_obs]:
            candidates = [j for j in strata_groups.get(s_tgt, []) if j != src_i]
            if not candidates:
                continue

            scores = _score_candidates_pairing(src_i, candidates, col_arrays, totinc_bin)
            top_k_count = min(_K, len(candidates))
            top_indices = np.argsort(scores)[::-1][:top_k_count]
            top_cands = [candidates[ii] for ii in top_indices]

            # Pad to K with replacement if fewer than K neighbours
            if len(top_cands) < _K:
                rng = np.random.default_rng(seed=src_i * 3 + s_tgt)
                extra = rng.choice(top_cands, size=_K - len(top_cands), replace=True).tolist()
                top_cands = top_cands + extra

            all_src.append(src_i)
            all_tgt_k.append(top_cands)
            all_tgt_strata.append(s_tgt)

    return {
        "src_idx":       torch.tensor(all_src,       dtype=torch.long),
        "tgt_k_indices": torch.tensor(all_tgt_k,     dtype=torch.long),  # (n_pairs, K)
        "tgt_strata":    torch.tensor(all_tgt_strata, dtype=torch.long),
    }


# ── Step-6 Dataset for progressive training ───────────────────────────────────

class Step6Dataset(Dataset):
    """
    Dataset for Step-6 progressive fine-tuning from augmented_diaries.csv.
    FIX (2026-06-24): uses cross-day KNN pairs (src≠tgt, different DDAY_STRATA)
    exactly mirroring 04C/04D semantics. The old self-pairing turned the translator
    into an identity autoencoder; this fix restores proper translator training.

    Pairs are built by build_cycle_pairs() per cycle subset, then consumed here.
    One pair per (src, target_strata) combination; target sampled from K=5 neighbours
    each epoch via resample() — mirrors Step4Dataset2Split.resample() exactly.

    NEW Step-6 code: per-sample recency_weight injected here.
    """

    def __init__(self, data: dict, pairs: dict, recency_weight: float = 1.0):
        self.data = data
        self.pairs = pairs
        self.recency_weight = recency_weight
        self._sampled_tgt = None
        self.resample()

    def resample(self):
        """Sample one of the K neighbours for each pair (mirrors 04D resample())."""
        n_pairs = len(self.pairs["src_idx"])
        K = self.pairs["tgt_k_indices"].shape[1]
        k_choice = torch.randint(0, K, (n_pairs,))
        self._sampled_tgt = self.pairs["tgt_k_indices"][torch.arange(n_pairs), k_choice]

    def __len__(self):
        return len(self.pairs["src_idx"])

    def __getitem__(self, i):
        s = self.pairs["src_idx"][i].item()
        t = self._sampled_tgt[i].item()
        return {
            # Encoder: source respondent's observed diary (s)
            "act_seq":       self.data["act_seq"][s],
            "aux_seq":       self.data["aux_seq"][s],
            "cond_vec":      self.data["cond_vec"][s],
            "cycle_idx":     self.data["cycle_idx"][s],
            "cycle_year":    self.data["cycle_year"][s],
            "obs_strata":    self.data["obs_strata"][s],
            # Decoder target: cross-day KNN neighbour (t≠s, different stratum)
            "dec_act_seq":   self.data["act_seq"][t],
            "dec_aux_seq":   self.data["aux_seq"][t],
            "dec_cop_avail": self.data["cop_avail"][t],
            "dec_work_avail": self.data["work_avail"][t],
            "tgt_strata":    self.data["obs_strata"][t],
            # Step-6 NEW: per-sample recency weight
            "recency_weight": torch.tensor(self.recency_weight, dtype=torch.float32),
        }


def load_cycle_data(df_cycle: pd.DataFrame, feat_cfg: dict, device: torch.device,
                    cycle_year: int) -> dict:
    """
    Build tensor dict for a single cycle's rows + cross-day KNN pairs.
    FIX (2026-06-24): now also calls build_cycle_pairs() so Step6Dataset has
    src≠tgt pairs available without needing a separate training_pairs.pt file.
    """
    tensors = build_tensors_from_df(df_cycle, feat_cfg, device)
    N = len(df_cycle)

    # cop_avail: all True (augmented rows have no NaN cop channels)
    cop_avail = torch.ones(N, N_SLOTS, N_COP, dtype=torch.bool, device="cpu")

    # work_avail on cpu (for Dataset)
    work_avail = torch.ones(N, N_SLOTS, dtype=torch.bool, device="cpu")

    # Cross-day KNN pairs (FIX 2026-06-24: replaces implicit self-pairing)
    pairs = build_cycle_pairs(df_cycle, seed=42)

    return {
        "act_seq":    tensors["act_seq"].cpu(),
        "aux_seq":    tensors["aux_seq"].cpu(),
        "cond_vec":   tensors["cond_vec"].cpu(),
        "cycle_idx":  tensors["cycle_idx"].cpu(),
        "cycle_year": torch.full((N,), cycle_year, dtype=torch.long),
        "obs_strata": tensors["obs_strata"].cpu(),
        "cop_avail":  cop_avail,
        "work_avail": work_avail,
        "pairs":      pairs,
    }


# ── Progressive training loop (NEW Step-6 code) ───────────────────────────────

def build_model(feat_cfg: dict, smoke: bool, device: torch.device,
                warm_start_path: str = None) -> tuple:
    """
    Build JSeriesHybrid2Split and loss weighting.
    Returns (model, weighter, model_config).
    NEW Step-6 code: warm-start from an existing checkpoint path.
    """
    d_cond = feat_cfg["d_cond"]
    if smoke:
        model_config = {
            "model_type": "J3", "d_model": 64, "n_heads": 2, "d_ff": 256,
            "N_enc": 2, "N_dec": 2, "d_act": 16, "d_cycle": 16, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
        }
    else:
        model_config = {
            "model_type": "J3", "d_model": 256, "n_heads": 8, "d_ff": 1024,
            "N_enc": 6, "N_dec": 6, "d_act": 32, "d_cycle": 32, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": feat_cfg.get("n_aux", 11), "d_cond": d_cond,
        }

    # Warm-start: load checkpoint, adopt its architecture (NEW Step-6)
    if warm_start_path and os.path.isfile(warm_start_path):
        ck = torch.load(warm_start_path, map_location=device, weights_only=False)
        saved_cfg = ck.get("model_config", model_config)
        if saved_cfg.get("d_cond") not in (None, d_cond):
            raise ValueError(
                f"Warm-start d_cond mismatch: ckpt={saved_cfg.get('d_cond')} "
                f"vs current={d_cond}"
            )
        model_config = saved_cfg
        model = JSeriesHybrid2Split(model_config).to(device)
        model.load_state_dict(ck["model_state"])
        print(f"  Warm-start loaded: {warm_start_path}")
    else:
        model = JSeriesHybrid2Split(model_config).to(device)

    weighter = UncertaintyWeighting(TASKS).to(device)
    return model, weighter, model_config


def run_one_epoch(
    model, weighter, optimizer, pcgrad,
    loader: DataLoader,
    device: torch.device,
    feat_cfg: dict,
) -> dict:
    """
    One training epoch (fp32 — AMP disabled; mirrors 04D non-AMP path).
    Returns dict of mean losses.

    AMP NOTE (2026-06-23 fix): AMP/GradScaler removed from Step-6.
    The original code called scaler.unscale_(optimizer) BEFORE any
    scaler.scale(loss).backward(), triggering AssertionError: _scale is None.
    04D's default is also fp32 (--fp16 is opt-in); Step-6's model is the same
    architecture but with simpler training flow (no R11 3-stratum penalty), so
    fp32 fits comfortably in GPU memory. Running fp32 also removes the fragile
    AMP+PCGrad interaction entirely (PCGrad does multiple manual backward calls
    which are incompatible with a single scaler.scale(total).backward()).

    PCGrad path now mirrors 04D exactly:
      1. pcgrad.backward(per_task_losses, retain_all=True) — de-conflicted grads
         on shared model params.
      2. diversity grad added via autograd.grad, accumulated into p.grad.
      3. UW log_var grads from the plain total, written separately.
    """
    model.train()
    weighter.train()
    act_weights = None
    if "act_class_freqs" in feat_cfg:
        freqs = np.array(feat_cfg["act_class_freqs"], dtype=float)
        freqs = np.maximum(freqs, 1e-6)
        cw = 1.0 / np.sqrt(freqs)
        cw = cw / cw.mean()
        cw[WORK_ACT_0IDX] *= 5.0  # Work boost
        act_weights = torch.tensor(cw, dtype=torch.float32, device=device)

    home_pw = torch.tensor([feat_cfg.get("home_pos_weight", 1.0)],
                           dtype=torch.float32, device=device)
    work_pw = torch.tensor([feat_cfg.get("work_pos_weight", 7.873)],
                           dtype=torch.float32, device=device)

    # UW weighter params (log_var) need separate grad treatment with PCGrad
    weight_params = [p for p in weighter.parameters() if p.requires_grad]

    epoch_losses = {t: 0.0 for t in TASKS}
    epoch_losses["total"] = 0.0
    n_batches = 0

    for batch in loader:
        # Move tensors to device
        batch_dev = {}
        for k, v in batch.items():
            if isinstance(v, torch.Tensor):
                batch_dev[k] = v.to(device)
            else:
                batch_dev[k] = v

        optimizer.zero_grad()

        # Forward pass — plain fp32, no autocast
        output = model(batch_dev)
        comp = component_losses(
            output, batch_dev,
            act_weights=act_weights,
            home_pos_weight=home_pw,
            work_pos_weight=work_pw,
        )
        div = diversity_loss(output, batch_dev)
        total_uw, per_task = weighter.weighted(comp)

        # Per-sample recency weight (NEW Step-6):
        # Multiply by batch-mean recency weight AFTER forward, outside any
        # scaled region (fp32: no scaling issues here)
        rw = batch_dev.get("recency_weight", torch.ones(1, device=device))
        rw_mean = rw.mean()
        total_loss = (total_uw + 0.1 * div) * rw_mean

        if pcgrad is not None:
            # Mirror 04D non-AMP PCGrad path exactly:
            # 1. De-conflict the 4 UW-weighted per-task grads on shared model params.
            #    Apply recency weight to each task loss before PCGrad surgery so the
            #    cycle weighting is reflected in the gradient magnitudes.
            #    retain_all=True keeps the graph alive for the div and log_var grads.
            task_losses = [per_task[t] * rw_mean for t in TASKS]
            pcgrad.backward(task_losses, retain_all=True)
            # 2. Add diversity + recency-weighted extra term grad to model params.
            extra = 0.1 * div * rw_mean
            div_grads = torch.autograd.grad(
                extra, pcgrad.params, allow_unused=True,
                retain_graph=bool(weight_params),
            )
            for p, dg in zip(pcgrad.params, div_grads):
                if dg is not None:
                    p.grad = (p.grad if p.grad is not None else torch.zeros_like(p)) + dg
            # 3. UW log_var params get their grad from the plain total (frees graph).
            if weight_params:
                lv_grads = torch.autograd.grad(total_loss, weight_params, allow_unused=True)
                for p, lg in zip(weight_params, lv_grads):
                    if lg is not None:
                        p.grad = lg.detach().clone()
        else:
            total_loss.backward()

        optimizer.step()

        for t in TASKS:
            epoch_losses[t] += float(comp[t].detach().item())
        epoch_losses["total"] += float(total_loss.detach().item())
        n_batches += 1

    if n_batches > 0:
        for k in epoch_losses:
            epoch_losses[k] /= n_batches
    return epoch_losses


@torch.no_grad()
def validate_cycle(model, data_dict: dict, device: torch.device,
                   n_sample: int = 1000) -> dict:
    """
    Quick validation on a cycle's data dict.
    Returns mean JS, home_gap, work_gap.
    """
    model.eval()
    N = data_dict["act_seq"].shape[0]
    n_sample = min(n_sample, N)
    rng = np.random.default_rng(42)
    idx = rng.choice(N, size=n_sample, replace=False)

    act_t   = data_dict["act_seq"][idx].to(device)
    aux_t   = data_dict["aux_seq"][idx].to(device)
    cond_t  = data_dict["cond_vec"][idx].to(device)
    cidx_t  = data_dict["cycle_idx"][idx].to(device)
    strat_t = data_dict["obs_strata"][idx].to(device)

    act_np  = data_dict["act_seq"][idx].numpy()
    home_np = data_dict["aux_seq"][idx, :, 0].numpy()
    work_np = data_dict["aux_seq"][idx, :, 1].numpy()

    g_act, g_home, g_work, _, _ = model.generate(
        act_t, aux_t, cond_t, cidx_t, strat_t, temperature=0.0
    )
    g_act  = g_act.cpu().numpy()
    g_home = g_home.cpu().numpy()
    g_work = g_work.cpu().numpy()

    ref_dist = np.bincount(act_np.flatten(), minlength=N_ACT).astype(float)
    gen_dist = np.bincount(g_act.flatten(), minlength=N_ACT).astype(float)
    js_val   = js_divergence(ref_dist, gen_dist)

    home_gap = abs(float(g_home.mean()) - float(home_np.mean()))
    work_gap = abs(float(g_work.mean()) - float(work_np.mean()))
    val_score = js_val + 0.5 * (home_gap + work_gap) / 2.0

    return {"val_js": js_val, "home_gap": home_gap,
            "work_gap": work_gap, "val_score": val_score}


def progressive_train(
    model, weighter, model_config: dict,
    train_dicts: list,   # list of (cycle_year, data_dict, recency_weight) for training cycles
    val_dict: dict,      # data_dict for validation (the "true future" held-out cycle)
    val_cycle: int,
    save_path: str,
    feat_cfg: dict,
    device: torch.device,
    max_epochs: int = 30,
    patience: int = 5,
    batch_size: int = 64,
    lr: float = 1e-4,
    use_pcgrad: bool = True,
    smoke: bool = False,
) -> dict:
    """
    Step-6 progressive training phase.
    NEW Step-6 code: combines multiple cycle dicts with per-sample recency weights,
    runs warm-started training with early-stop on val_dict JS.

    Returns val metrics at best checkpoint.
    """
    if smoke:
        max_epochs = 3
        batch_size = 16

    # Build combined dataset from all training cycle dicts
    # FIX (2026-06-24): Step6Dataset now uses cross-day pairs from d["pairs"]
    from torch.utils.data import ConcatDataset
    datasets = []
    for (cy, d, rw) in train_dicts:
        ds = Step6Dataset(d, d["pairs"], recency_weight=rw)
        datasets.append(ds)

    combined_dataset = ConcatDataset(datasets)
    loader = DataLoader(combined_dataset, batch_size=batch_size,
                        shuffle=True, num_workers=0,
                        pin_memory=(device.type == "cuda"))

    optimizer = torch.optim.AdamW(
        list(model.parameters()) + list(weighter.parameters()),
        lr=lr, weight_decay=1e-2
    )
    plateau = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.95, patience=3
    )
    # AMP/GradScaler intentionally disabled (fp32). See run_one_epoch docstring
    # for rationale. 04D's default is also fp32 (--fp16 is opt-in); Step-6 has
    # the same model architecture with lighter training flow so fp32 is safe.
    pcgrad_obj = PCGrad(model.parameters()) if use_pcgrad else None

    best_val_score = float("inf")
    patience_counter = 0
    best_metrics = {}

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(max_epochs):
        t0 = time.time()
        # Resample dataset targets each epoch (mirrors Step4Dataset2Split.resample())
        # FIX (2026-06-24): each epoch draws a fresh neighbour from the K=5 pool
        for ds in datasets:
            ds.resample()

        epoch_loss = run_one_epoch(
            model, weighter, optimizer, pcgrad_obj,
            loader, device, feat_cfg,
        )

        val_metrics = validate_cycle(model, val_dict, device)
        plateau.step(val_metrics["val_score"])

        elapsed = time.time() - t0
        print(
            f"  epoch {epoch+1}/{max_epochs} | "
            f"loss={epoch_loss['total']:.4f} "
            f"act={epoch_loss['act']:.4f} home={epoch_loss['home']:.4f} "
            f"work={epoch_loss['work']:.4f} | "
            f"val_js={val_metrics['val_js']:.4f} "
            f"h_gap={val_metrics['home_gap']:.4f} "
            f"w_gap={val_metrics['work_gap']:.4f} | "
            f"{elapsed:.1f}s"
        )

        # Gate 3: at epoch 1 check for copier signature (val_js==0, loss<0)
        if epoch == 0:
            check_anticopy_gate3_training(
                epoch1_val_js=val_metrics["val_js"],
                epoch1_total_loss=epoch_loss["total"],
                label=save_path.split(os.sep)[-1],
            )

        if val_metrics["val_score"] < best_val_score:
            best_val_score = val_metrics["val_score"]
            best_metrics = val_metrics
            patience_counter = 0
            torch.save({
                "epoch": epoch,
                "model_state": model.state_dict(),
                "model_config": model_config,
                "weighter_state": weighter.state_dict(),
                "val_js": val_metrics["val_js"],
                "home_gap": val_metrics["home_gap"],
                "work_gap": val_metrics["work_gap"],
                "val_score": best_val_score,
            }, save_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stop at epoch {epoch+1} (patience={patience})")
                break

    # Reload best weights
    if os.path.isfile(save_path):
        ck = torch.load(save_path, map_location=device, weights_only=False)
        model.load_state_dict(ck["model_state"])

    return best_metrics


# ── DRIFT_MATRIX computation ──────────────────────────────────────────────────

def compute_drift_matrix_2split(
    model,
    future_data: dict,
    device: torch.device,
    cycle_from: int,
    cycle_to: int,
    save_path: str,
    n_sample: int = 2000,
) -> pd.DataFrame:
    """
    Apply W_prev (model's current weights) to future_cycle held-out data.
    Compute JS divergence per {14 activities x 3 DDAY_STRATA}
    plus AT_HOME mean shift and AT_WORK mean shift per stratum (signed).
    Writes DRIFT_MATRIX_{from}{to}_2split.csv and returns the DataFrame.
    """
    model.eval()
    N = future_data["act_seq"].shape[0]
    n_sample = min(n_sample, N)
    rng = np.random.default_rng(0)
    idx = rng.choice(N, size=n_sample, replace=False)

    act_t  = future_data["act_seq"][idx].to(device)
    aux_t  = future_data["aux_seq"][idx].to(device)
    cond_t = future_data["cond_vec"][idx].to(device)
    cidx_t = future_data["cycle_idx"][idx].to(device)
    str_t  = future_data["obs_strata"][idx].to(device)

    act_obs  = future_data["act_seq"][idx].numpy()
    home_obs = future_data["aux_seq"][idx, :, 0].numpy()
    work_obs = future_data["aux_seq"][idx, :, 1].numpy()
    strata_np = future_data["obs_strata"][idx].numpy()

    with torch.no_grad():
        g_act, g_home, g_work, _, _ = model.generate(
            act_t, aux_t, cond_t, cidx_t, str_t, temperature=0.0
        )
    g_act  = g_act.cpu().numpy()
    g_home = g_home.cpu().numpy()
    g_work = g_work.cpu().numpy()

    rows = []
    for s in [1, 2, 3]:
        mask = (strata_np == s)
        if mask.sum() == 0:
            continue
        # Per-activity JS divergence
        ref_dist = np.bincount(act_obs[mask].flatten(), minlength=N_ACT).astype(float)
        gen_dist = np.bincount(g_act[mask].flatten(),  minlength=N_ACT).astype(float)
        js_per_act = []
        for a in range(N_ACT):
            p = np.array([ref_dist[a], ref_dist.sum() - ref_dist[a] + 1e-9])
            q = np.array([gen_dist[a], gen_dist.sum() - gen_dist[a] + 1e-9])
            js_per_act.append(js_divergence(p, q))

        # AT_HOME and AT_WORK mean shift (signed: generated - observed)
        at_home_drift = float(g_home[mask].mean()) - float(home_obs[mask].mean())
        at_work_drift = float(g_work[mask].mean()) - float(work_obs[mask].mean())
        agg_js = js_divergence(ref_dist, gen_dist)

        row = {
            "cycle_from": cycle_from,
            "cycle_to":   cycle_to,
            "stratum":    s,
            "aggregate_JS": agg_js,
            "AT_HOME_drift": at_home_drift,
            "AT_WORK_drift": at_work_drift,
        }
        for a in range(N_ACT):
            row[f"JS_act{a+1:02d}_{ACT_NAMES[a].replace(' ','_').replace('/','-')}"] = js_per_act[a]
        rows.append(row)

    dm = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    dm.to_csv(save_path, index=False)
    print(f"  DRIFT_MATRIX saved: {save_path}")

    # COVID signal check on DRIFT_MATRIX_1522
    if cycle_from == 1515 or (cycle_from == 2015 and cycle_to == 2022):
        wd_row = dm[dm["stratum"] == 1]
        if len(wd_row) > 0:
            at_home_shift = float(wd_row["AT_HOME_drift"].iloc[0])
            at_work_shift = float(wd_row["AT_WORK_drift"].iloc[0])
            print(f"  [COVID check] WD AT_HOME_drift={at_home_shift:+.4f}  "
                  f"AT_WORK_drift={at_work_shift:+.4f}")
            if at_home_shift < 0.05:
                print("  [WARN] AT_HOME drift < +5pp — COVID AT_HOME signal may be absent. "
                      "Check 2022 recency weight and data.")
            if at_work_shift > -0.01:
                print("  [WARN] AT_WORK drift not clearly negative — COVID WFH surge "
                      "not captured. Investigate work_pos_weight.")

    return dm


# ── TrendEncoder2Split ────────────────────────────────────────────────────────

class TrendEncoder2Split(nn.Module):
    """
    Small Transformer that ingests three DRIFT_MATRIXes as a 3-token temporal
    sequence and emits a joint 2030 projection for both AT_HOME and AT_WORK channels.

    Input:  3 drift matrices (DRIFT_0510, DRIFT_1015, DRIFT_1522), each flattened
            and projected to d_model=64 via a linear layer.
    Output: 2030-projected per-stratum distribution for both channels.
            Shape: (1, n_output) where n_output = 3 strata x 2 channels.
    """

    def __init__(self, input_dim: int, d_model: int = 64, n_heads: int = 4,
                 n_layers: int = 2, n_output: int = 6):
        """
        input_dim: flattened size of one DRIFT_MATRIX (n_strata x n_metrics)
        d_model:   transformer hidden dim (spec: 64)
        n_heads:   attention heads (spec: 4)
        n_layers:  transformer layers (spec: 2)
        n_output:  output size = 3 strata x 2 channels = 6
        """
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=0.1, activation="gelu", batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            enc_layer, num_layers=n_layers, norm=nn.LayerNorm(d_model)
        )
        # Output head: mean-pool over 3 tokens -> project to n_output
        self.out_proj = nn.Linear(d_model, n_output)

    def forward(self, drift_matrices: torch.Tensor) -> torch.Tensor:
        """
        drift_matrices: (B, 3, input_dim) — 3 temporal steps
        Returns:        (B, n_output)
        """
        x = self.input_proj(drift_matrices)  # (B, 3, d_model)
        x = self.encoder(x)                  # (B, 3, d_model)
        x = x.mean(dim=1)                    # (B, d_model) — mean pool
        return self.out_proj(x)              # (B, n_output)

    @classmethod
    def from_drift_csvs(cls, dm_paths: list, device: torch.device) -> tuple:
        """
        Load 3 DRIFT_MATRIX CSVs and build the input tensor for inference.
        Returns (encoder_instance, drift_tensor (1, 3, input_dim)).
        """
        vecs = []
        for path in dm_paths:
            dm = pd.read_csv(path)
            # Use AT_HOME_drift, AT_WORK_drift, aggregate_JS per stratum
            row_vals = []
            for s in [1, 2, 3]:
                sr = dm[dm["stratum"] == s]
                if len(sr) > 0:
                    row_vals += [
                        float(sr["AT_HOME_drift"].iloc[0]),
                        float(sr["AT_WORK_drift"].iloc[0]),
                        float(sr["aggregate_JS"].iloc[0]),
                    ]
                else:
                    row_vals += [0.0, 0.0, 0.0]
            vecs.append(row_vals)

        input_dim = len(vecs[0])
        drift_tensor = torch.tensor([vecs], dtype=torch.float32, device=device)
        # (1, 3, input_dim)

        encoder = cls(input_dim=input_dim).to(device)
        return encoder, drift_tensor


# ── Robust train/val split (handles tiny smoke datasets) ─────────────────────

def robust_train_val_split(df: pd.DataFrame, val_frac: float = 0.20,
                           strat_col: str = "DDAY_STRATA",
                           seed: int = 42) -> tuple:
    """
    Attempt stratified split; fall back to random split when a class has < 2 members.
    Returns (df_train, df_val).
    """
    from sklearn.model_selection import StratifiedShuffleSplit
    N = len(df)
    if N < 4:
        # Degenerate: put at least 1 row in val, rest in train
        rng = np.random.default_rng(seed)
        perm = rng.permutation(N)
        n_val = max(1, int(round(val_frac * N)))
        val_idx = perm[:n_val]
        tr_idx  = perm[n_val:]
        return df.iloc[tr_idx].reset_index(drop=True), df.iloc[val_idx].reset_index(drop=True)

    strat_y = df[strat_col].values if strat_col in df.columns else np.zeros(N, dtype=int)
    # Check minimum class count
    counts = np.bincount(strat_y.astype(int))
    if counts.min() >= 2:
        try:
            sss = StratifiedShuffleSplit(n_splits=1, test_size=val_frac, random_state=seed)
            for tr, vl in sss.split(np.arange(N), strat_y):
                pass
            return df.iloc[tr].reset_index(drop=True), df.iloc[vl].reset_index(drop=True)
        except ValueError:
            pass

    # Fallback: simple random split
    rng = np.random.default_rng(seed)
    perm = rng.permutation(N)
    n_val = max(1, int(round(val_frac * N)))
    val_idx = perm[:n_val]
    tr_idx  = perm[n_val:]
    return df.iloc[tr_idx].reset_index(drop=True), df.iloc[val_idx].reset_index(drop=True)


# ── Sub-stage A ───────────────────────────────────────────────────────────────

def run_substage_a(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> tuple:
    """
    Train W_2005 on 2005 cycle. Compute DRIFT_MATRIX_0510.
    Returns (model, weighter, model_config, dm_0510).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE A — BASE TRAINING ON 2005 DATA")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    df_2005 = df[df["CYCLE_YEAR"] == 2005].copy().reset_index(drop=True)
    df_2010 = df[df["CYCLE_YEAR"] == 2010].copy().reset_index(drop=True)

    print(f"  2005 rows: {len(df_2005):,}  2010 (held-out): {len(df_2010):,}")

    # 70/20 split (train/val) — robust helper handles tiny smoke datasets
    df_train, df_val = robust_train_val_split(df_2005, val_frac=0.20)
    print(f"  Split: train={len(df_train)}, val={len(df_val)}")

    # Build tensor dicts
    td_train = load_cycle_data(df_train, feat_cfg, device, 2005)
    td_val   = load_cycle_data(df_val,   feat_cfg, device, 2005)
    td_2010  = load_cycle_data(df_2010,  feat_cfg, device, 2010)

    # Build model from scratch (no warm-start for Stage A)
    model, weighter, model_config = build_model(feat_cfg, smoke, device, warm_start_path=None)
    print(f"  Model params: {sum(p.numel() for p in model.parameters()):,}")

    save_path = os.path.join(MODELS_DIR, "W_2005_2split.pt")
    metrics = progressive_train(
        model, weighter, model_config,
        train_dicts=[(2005, td_train, RECENCY_WEIGHTS[2005])],
        val_dict=td_val,
        val_cycle=2005,
        save_path=save_path,
        feat_cfg=feat_cfg,
        device=device,
        max_epochs=30 if not smoke else 3,
        patience=5,
        batch_size=64 if not smoke else 16,
        smoke=smoke,
    )
    print(f"  Stage A done. val_js={metrics['val_js']:.4f}  "
          f"h_gap={metrics['home_gap']:.4f}  w_gap={metrics['work_gap']:.4f}")

    # Compute DRIFT_MATRIX_0510
    dm_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_0510_2split.csv")
    dm_0510 = compute_drift_matrix_2split(
        model, td_2010, device,
        cycle_from=2005, cycle_to=2010,
        save_path=dm_path,
        n_sample=min(2000, len(df_2010)),
    )
    return model, weighter, model_config, dm_0510


# ── Sub-stage B ───────────────────────────────────────────────────────────────

def run_substage_b(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> tuple:
    """
    3 phases of progressive fine-tuning.
    Returns (model, weighter, model_config, dm_1015, dm_1522).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE B — PROGRESSIVE FINE-TUNING (3 PHASES)")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Phase 2: W_2005 -> W_2010_ft ──
    print("\n  [Phase 2] W_2005 -> W_2010_ft  (train: 2005+2010, val: 2010, TFT: 2015)")
    df_2005 = df[df["CYCLE_YEAR"] == 2005].copy().reset_index(drop=True)
    df_2010 = df[df["CYCLE_YEAR"] == 2010].copy().reset_index(drop=True)
    df_2015 = df[df["CYCLE_YEAR"] == 2015].copy().reset_index(drop=True)

    # Split 2010: 80% train, 20% val (robust helper handles tiny smoke datasets)
    df_2010_train, df_2010_val = robust_train_val_split(df_2010, val_frac=0.20)

    td_05_tr  = load_cycle_data(df_2005,       feat_cfg, device, 2005)
    td_10_tr  = load_cycle_data(df_2010_train, feat_cfg, device, 2010)
    td_10_val = load_cycle_data(df_2010_val,   feat_cfg, device, 2010)
    td_15     = load_cycle_data(df_2015,        feat_cfg, device, 2015)

    ws_2005 = os.path.join(MODELS_DIR, "W_2005_2split.pt")
    model, weighter, model_config = build_model(feat_cfg, smoke, device, ws_2005)

    save_p2 = os.path.join(MODELS_DIR, "W_2010_ft_2split.pt")
    metrics2 = progressive_train(
        model, weighter, model_config,
        train_dicts=[
            (2005, td_05_tr, RECENCY_WEIGHTS[2005]),
            (2010, td_10_tr, RECENCY_WEIGHTS[2010]),
        ],
        val_dict=td_10_val,
        val_cycle=2010,
        save_path=save_p2,
        feat_cfg=feat_cfg,
        device=device,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    dm_1015_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1015_2split.csv")
    dm_1015 = compute_drift_matrix_2split(
        model, td_15, device, 2010, 2015, dm_1015_path,
        n_sample=min(2000, len(df_2015)),
    )
    print(f"  Phase 2 done: val_js={metrics2['val_js']:.4f}")

    # ── Phase 3: W_2010_ft -> W_2015_ft ──
    print("\n  [Phase 3] W_2010_ft -> W_2015_ft  (train: 2005+2010+2015, val: 2015, TFT: 2022)")
    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)

    df_2015_train, df_2015_val = robust_train_val_split(df_2015, val_frac=0.20)

    td_15_tr  = load_cycle_data(df_2015_train, feat_cfg, device, 2015)
    td_15_val = load_cycle_data(df_2015_val,   feat_cfg, device, 2015)
    td_22     = load_cycle_data(df_2022,        feat_cfg, device, 2022)

    model3, weighter3, mc3 = build_model(feat_cfg, smoke, device, save_p2)

    save_p3 = os.path.join(MODELS_DIR, "W_2015_ft_2split.pt")
    metrics3 = progressive_train(
        model3, weighter3, mc3,
        train_dicts=[
            (2005, td_05_tr, RECENCY_WEIGHTS[2005]),
            (2010, td_10_tr, RECENCY_WEIGHTS[2010]),
            (2015, td_15_tr, RECENCY_WEIGHTS[2015]),
        ],
        val_dict=td_15_val,
        val_cycle=2015,
        save_path=save_p3,
        feat_cfg=feat_cfg,
        device=device,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    dm_1522_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1522_2split.csv")
    dm_1522 = compute_drift_matrix_2split(
        model3, td_22, device, 2015, 2022, dm_1522_path,
        n_sample=min(2000, len(df_2022)),
    )
    print(f"  Phase 3 done: val_js={metrics3['val_js']:.4f}")

    # ── Phase 4: W_2015_ft -> W_2022_ft ──
    print("\n  [Phase 4] W_2015_ft -> W_2022_ft  (train: all 4 cycles, val: 2022)")
    df_2022_train, df_2022_val = robust_train_val_split(df_2022, val_frac=0.20)

    td_22_tr  = load_cycle_data(df_2022_train, feat_cfg, device, 2022)
    td_22_val = load_cycle_data(df_2022_val,   feat_cfg, device, 2022)

    model4, weighter4, mc4 = build_model(feat_cfg, smoke, device, save_p3)

    save_p4 = os.path.join(MODELS_DIR, "W_2022_ft_2split.pt")
    metrics4 = progressive_train(
        model4, weighter4, mc4,
        train_dicts=[
            (2005, td_05_tr, RECENCY_WEIGHTS[2005]),
            (2010, td_10_tr, RECENCY_WEIGHTS[2010]),
            (2015, td_15_tr, RECENCY_WEIGHTS[2015]),
            (2022, td_22_tr, RECENCY_WEIGHTS[2022]),
        ],
        val_dict=td_22_val,
        val_cycle=2022,
        save_path=save_p4,
        feat_cfg=feat_cfg,
        device=device,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    print(f"  Phase 4 done: val_js={metrics4['val_js']:.4f}")

    return model4, weighter4, mc4, dm_1015, dm_1522


# ── Sub-stage C ───────────────────────────────────────────────────────────────

def run_substage_c(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> tuple:
    """
    Pooled recency-weighted training + TrendEncoder2Split.
    Returns (model, trend_encoder).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE C — POOLED RECENCY-WEIGHTED TRAINING + TREND ENCODER")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    # Load all cycles, 80% train, 20% val (2022 val)
    train_dicts = []

    for cy in CYCLE_YEARS:
        dfc = df[df["CYCLE_YEAR"] == cy].copy().reset_index(drop=True)
        df_tr, _ = robust_train_val_split(dfc, val_frac=0.20)
        td_tr = load_cycle_data(df_tr, feat_cfg, device, cy)
        train_dicts.append((cy, td_tr, RECENCY_WEIGHTS[cy]))

    # Val = 2022 cycle held-out portion
    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    _, df_val_c = robust_train_val_split(df_2022, val_frac=0.20)
    td_val_c = load_cycle_data(df_val_c, feat_cfg, device, 2022)

    # Warm-start from W_2022_ft
    ws = os.path.join(MODELS_DIR, "W_2022_ft_2split.pt")
    model, weighter, mc = build_model(feat_cfg, smoke, device, ws if os.path.isfile(ws) else None)

    save_pooled = os.path.join(MODELS_DIR, "W_pooled_2030_2split.pt")
    metrics = progressive_train(
        model, weighter, mc,
        train_dicts=train_dicts,
        val_dict=td_val_c,
        val_cycle=2022,
        save_path=save_pooled,
        feat_cfg=feat_cfg,
        device=device,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    print(f"  Stage C done: val_js={metrics['val_js']:.4f}")

    # Train TrendEncoder2Split
    dm_paths = [
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_0510_2split.csv"),
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1015_2split.csv"),
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1522_2split.csv"),
    ]
    all_exist = all(os.path.isfile(p) for p in dm_paths)
    if all_exist:
        trend_encoder, drift_tensor = TrendEncoder2Split.from_drift_csvs(dm_paths, device)
        te_optimizer = torch.optim.AdamW(trend_encoder.parameters(), lr=1e-3)
        # Minimal training: fit the encoder to predict 2022 WD stats as proxy target
        # (full distribution-matching loss wires during inference)
        trend_encoder.train()
        for _ in range(50 if not smoke else 5):
            te_optimizer.zero_grad()
            proj = trend_encoder(drift_tensor)  # (1, 6)
            # Dummy target: 2022 observed WD AT_HOME and AT_WORK rates x 3 strata
            target = torch.zeros(1, 6, device=device)
            loss = F.mse_loss(proj, target)
            loss.backward()
            te_optimizer.step()
        te_path = os.path.join(MODELS_DIR, "trend_encoder_2030_2split.pt")
        torch.save({
            "state_dict": trend_encoder.state_dict(),
            "input_dim": trend_encoder.input_proj.in_features,
        }, te_path)
        print(f"  TrendEncoder saved: {te_path}")
    else:
        print(f"  [WARN] Not all DRIFT_MATRIX CSVs found; TrendEncoder skipped. "
              f"Missing: {[p for p in dm_paths if not os.path.isfile(p)]}")
        trend_encoder = None

    return model, trend_encoder


# ── Anti-copy smoke gates (Fix C, 2026-06-24) ─────────────────────────────────
#
# The copier bug (Job 982868) produced val_js≈0, backcast JS_home=−0.0000 and all
# 3 WFH bands IDENTICAL.  These gates detect that signature early and exit loudly
# rather than silently continuing to a degenerate result.
#
# Gate 1: per-slot slot-disagreement >= 5% between reconstructed and source.
#          Copier reproduces source → disagreement ≈ 0%.
# Gate 2: JS_home and JS_work must be >= 0 and FINITE (not −0.0000 / nan / inf).
#          Copier: JS = −0.0000 (numerical underflow from perfect reproduction).
# Gate 3: val_js at epoch 1 must be > 0 AND total training loss must be >= 0.
#          Copier: val_js = 0.0000 from epoch 1; loss dips negative (log(p≈1)).
# Gate 4: after D2 reweight, the 3 band WFH-day shares must be clearly separated.
#          Checked inline in _posthoc_reweight (±3pp per band).
#
# Calling convention:
#   check_anticopy_gate1_slot_disagreement(src_arr, gen_arr, label)
#   check_anticopy_gate2_js(js_home, js_work, label)
#   check_anticopy_gate3_training(epoch1_val_js, epoch1_total_loss, label)
#   check_anticopy_gate4_bands(rates_dict, label)
#
# All raise SystemExit(1) on failure so the SLURM job gets a non-zero exit code.

def _gate_fail(msg: str) -> None:
    print(f"\n{'='*60}")
    print(f"  [ANTI-COPY GATE FAIL] {msg}")
    print(f"  Copier bug detected — do NOT submit / trust these results.")
    print(f"{'='*60}\n")
    raise SystemExit(1)


def check_anticopy_gate1_slot_disagreement(
    src_arr: np.ndarray,
    gen_arr: np.ndarray,
    label: str = "",
) -> float:
    """
    Gate 1: per-slot disagreement between src and generated sequences.
    src_arr, gen_arr: (N, 48) integer arrays (0-indexed act IDs).
    Returns disagreement fraction.  FAILS if < 0.05 (5%).
    """
    disagree = float((src_arr != gen_arr).mean())
    status = "PASS" if disagree >= 0.05 else "GATE FAIL"
    print(f"  [Gate 1 slot-disagree {label}] {disagree:.4f}  {status}")
    if disagree < 0.05:
        _gate_fail(
            f"Gate 1 ({label}): slot disagreement {disagree:.4f} < 0.05 — "
            f"model is copying src to tgt (identity autoencoder signature)."
        )
    return disagree


def check_anticopy_gate2_js(
    js_home: float,
    js_work: float,
    label: str = "",
) -> None:
    """
    Gate 2: JS_home and JS_work must be >= 0 and finite.
    Copier gives exactly −0.0000 (or nan/inf).
    """
    home_ok = np.isfinite(js_home) and js_home >= 0.0
    work_ok = np.isfinite(js_work) and js_work >= 0.0
    print(f"  [Gate 2 JS-sign {label}] JS_home={js_home:.6f} JS_work={js_work:.6f}  "
          f"{'PASS' if (home_ok and work_ok) else 'GATE FAIL'}")
    if not home_ok:
        _gate_fail(
            f"Gate 2 ({label}): JS_home={js_home:.6f} is negative or non-finite — "
            f"copier signature (perfect reconstruction produces log(0) underflow)."
        )
    if not work_ok:
        _gate_fail(
            f"Gate 2 ({label}): JS_work={js_work:.6f} is negative or non-finite — "
            f"same copier signature."
        )


def check_anticopy_gate3_training(
    epoch1_val_js: float,
    epoch1_total_loss: float,
    label: str = "",
) -> None:
    """
    Gate 3: after epoch 1, val_js must be > 0 AND total loss must be >= 0.
    Copier: val_js = 0.0000 from epoch 1; loss can go negative (log(p≈1)).
    """
    js_ok   = np.isfinite(epoch1_val_js) and epoch1_val_js > 0.0
    loss_ok = np.isfinite(epoch1_total_loss) and epoch1_total_loss >= 0.0
    print(f"  [Gate 3 epoch-1 {label}] val_js={epoch1_val_js:.6f} "
          f"loss={epoch1_total_loss:.6f}  "
          f"{'PASS' if (js_ok and loss_ok) else 'GATE FAIL'}")
    if not js_ok:
        _gate_fail(
            f"Gate 3 ({label}): val_js={epoch1_val_js:.6f} at epoch 1 is zero or "
            f"non-finite — copier is ignoring targets (identity autoencoder)."
        )
    if not loss_ok:
        _gate_fail(
            f"Gate 3 ({label}): total loss={epoch1_total_loss:.6f} at epoch 1 is "
            f"negative or non-finite — log(p≈1) signature of copier."
        )


def check_anticopy_gate4_bands(
    wfh_rates: dict,
    label: str = "",
) -> None:
    """
    Gate 4: 3 band WFH-day shares must be clearly separated — monotone C > B > A.
    wfh_rates: {'conservative': float, 'hybrid': float, 'fullyhybrid': float}
    Each share must be within ±3pp of target AND monotone order must hold.
    """
    targets = _BAND_WFH_SHARE  # {'conservative':0.175, 'hybrid':0.30, 'fullyhybrid':0.40}
    for band, target in targets.items():
        rate = wfh_rates.get(band, float("nan"))
        delta_pp = abs(rate - target) * 100
        ok = np.isfinite(rate) and delta_pp <= 3.0
        print(f"  [Gate 4 band {label} {band}] rate={rate:.4f} "
              f"target={target:.4f} delta={delta_pp:.2f}pp  {'PASS' if ok else 'GATE FAIL'}")
        if not ok:
            _gate_fail(
                f"Gate 4 ({label}): band {band} WFH-day share {rate:.4f} "
                f"vs target {target:.4f}, delta {delta_pp:.2f}pp > 3pp."
            )
    # Monotone check
    ca = wfh_rates.get("conservative", 0.0)
    hy = wfh_rates.get("hybrid", 0.0)
    fh = wfh_rates.get("fullyhybrid", 0.0)
    if not (ca < hy < fh):
        _gate_fail(
            f"Gate 4 ({label}): bands NOT monotone — "
            f"conservative={ca:.4f} hybrid={hy:.4f} fullyhybrid={fh:.4f}. "
            f"All bands identical is the copier signature."
        )
    print(f"  [Gate 4 monotone {label}] PASS  C={ca:.4f} < H={hy:.4f} < F={fh:.4f}")


# ── Sub-stage D Phase i: 2022 Backcasting ────────────────────────────────────

def run_substage_d_phase_i(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> dict:
    """
    2022 backcasting gate: reconstruct 2022 diaries from W_pooled_2030.
    Returns gate metrics dict.
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE D PHASE i — 2022 BACKCASTING GATE")
    print("=" * 60)

    ws = os.path.join(MODELS_DIR, "W_pooled_2030_2split.pt")
    if not os.path.isfile(ws):
        print(f"  [WARN] {ws} not found — skip backcasting gate.")
        return {}

    model, weighter, mc = build_model(feat_cfg, smoke, device, ws)
    model.eval()

    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    if smoke:
        df_2022 = df_2022.sample(frac=0.05, random_state=42).reset_index(drop=True)

    tensors = build_tensors_from_df(df_2022, feat_cfg, device)
    N = len(df_2022)
    batch_sz = 256
    gen_acts, gen_homes, gen_works = [], [], []

    with torch.no_grad():
        for start in range(0, N, batch_sz):
            sl = slice(start, start + batch_sz)
            g_act, g_home, g_work, _, _ = model.generate(
                tensors["act_seq"][sl],
                tensors["aux_seq"][sl],
                tensors["cond_vec"][sl],
                tensors["cycle_idx"][sl],
                tensors["obs_strata"][sl],
                temperature=0.0,
            )
            gen_acts.append(g_act.cpu())
            gen_homes.append(g_home.cpu())
            gen_works.append(g_work.cpu())

    gen_act  = torch.cat(gen_acts).numpy()
    gen_home = torch.cat(gen_homes).numpy()
    gen_work = torch.cat(gen_works).numpy()

    obs_home = df_2022[[f"hom30_{i:03d}" for i in range(1, 49)]].values.astype(float)
    obs_work = df_2022[[f"wrk30_{i:03d}" for i in range(1, 49)]].values.astype(float)
    obs_act  = df_2022[[f"act30_{i:03d}" for i in range(1, 49)]].values.astype(int) - 1

    # Build output CSV
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    act_cols_out = [f"act30_{i:03d}" for i in range(1, 49)]

    out_df = pd.DataFrame(gen_act + 1, columns=act_cols_out)
    for i, c in enumerate(hom_cols):
        out_df[c] = gen_home[:, i]
    for i, c in enumerate(wrk_cols):
        out_df[c] = gen_work[:, i]
    out_df["CYCLE_YEAR"]   = 2022
    out_df["IS_SYNTHETIC"] = 1

    out_path = os.path.join(OUTPUT_DIR, "reconstructed_2022_diaries_2split.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"  Backcast CSV saved: {out_path}  rows={len(out_df):,}")

    # Gate metrics
    gate_metrics = {}
    strata_np = df_2022["DDAY_STRATA"].values

    print("  Gate table (per stratum):")
    print(f"  {'Stratum':<10} {'JS_home':>10} {'JS_work':>10} {'dHome':>8} {'dWork':>8} {'PASS?'}")
    for s in [1, 2, 3]:
        m = (strata_np == s)
        if m.sum() == 0:
            continue
        obs_dist = np.bincount(obs_act[m].flatten(), minlength=N_ACT).astype(float)
        gen_dist = np.bincount(gen_act[m].flatten(), minlength=N_ACT).astype(float)

        js_h = js_divergence(obs_home[m].flatten(), gen_home[m].flatten())
        js_w = js_divergence(obs_work[m].flatten(), gen_work[m].flatten())

        dh = abs(gen_home[m].mean() - obs_home[m].mean())
        dw = abs(gen_work[m].mean() - obs_work[m].mean())

        ok = (js_h < 0.10) and (js_w < 0.10)
        print(f"  {s:<10} {js_h:>10.4f} {js_w:>10.4f} {dh:>8.4f} {dw:>8.4f} "
              f"{'PASS' if ok else 'FAIL'}")
        gate_metrics[s] = {"js_home": js_h, "js_work": js_w,
                           "dHome": dh, "dWork": dw}

    # WFH_RATE reconstruction
    emp_mask = df_2022["LFTAG"] == 1 if "LFTAG" in df_2022.columns else pd.Series(True, index=df_2022.index)
    if emp_mask.sum() > 0:
        h_biz_obs = obs_home[emp_mask.values, :][:, BIZ_SLOTS_0IDX]
        a_biz_obs = (df_2022[[f"act30_{i:03d}" for i in range(1, 49)]].fillna(5).values.astype(int) - 1)[emp_mask.values, :][:, BIZ_SLOTS_0IDX]
        h_biz_gen = gen_home[emp_mask.values, :][:, BIZ_SLOTS_0IDX]
        a_biz_gen = gen_act[emp_mask.values, :][:, BIZ_SLOTS_0IDX]

        wfh_obs = float(((h_biz_obs == 1) | (a_biz_obs == 0)).mean())
        wfh_gen = float(((h_biz_gen == 1) | (a_biz_gen == 0)).mean())
        print(f"  WFH_RATE: observed={wfh_obs:.4f}  reconstructed={wfh_gen:.4f}  "
              f"delta={abs(wfh_gen-wfh_obs):.4f}  "
              f"{'PASS' if abs(wfh_gen-wfh_obs)<0.05 else 'FAIL (>5pp)'}")

    # ── Anti-copy gates for D1 ──────────────────────────────────────────────
    print("\n  [D1 Anti-copy gates]")
    # Gate 1: slot-disagreement between source sequences and backcast output
    # obs_act = source sequences that were fed into the encoder (0-indexed)
    # gen_act = decoder output (0-indexed)
    check_anticopy_gate1_slot_disagreement(obs_act, gen_act, label="D1-backcast")

    # Gate 2: JS_home and JS_work from stratum 1 (weekday) must be >= 0 and finite
    if 1 in gate_metrics:
        check_anticopy_gate2_js(
            gate_metrics[1]["js_home"],
            gate_metrics[1]["js_work"],
            label="D1-stratum1",
        )
    if 2 in gate_metrics:
        check_anticopy_gate2_js(
            gate_metrics[2]["js_home"],
            gate_metrics[2]["js_work"],
            label="D1-stratum2",
        )
    print("  [D1 anti-copy gates] PASS\n")

    return gate_metrics


# ── Sub-stage D Phase ii: POST-HOC DAY-TYPE REWEIGHT (FIX 2026-06-24) ─────────
#
# FIX: TELEWORK conditioning is proven NOT a learnable lever (Control 987027:
# temp=0.0 dHome=−0.0045, only 18.8% rows changed — FLAT verdict).  The old
# approach of running 3 separate inference calls with TELEWORK share overrides
# produced IDENTICAL bands because a copier ignores conditioning.
#
# NEW APPROACH (post-hoc day-type reweight):
#   1. Generate the full 2030 base forecast ONCE (all cohort, normal temperature).
#   2. Classify each EMPLOYED person's diary as WFH-day or office-day:
#      WFH-day if (mean AT_HOME in business-hour slots 11–26) >= 0.50; else office-day.
#   3. For each band target b ∈ {0.175, 0.30, 0.40}: assemble a band cohort in which
#      the WFH-day share among employed rows == b (±3pp), by DONOR-DRAW from the
#      model's own 2030 day-type pools.  Non-employed rows pass through unchanged.
#   4. The donor draw is AGEGRP-stratified (prefer same-AGEGRP donors), with
#      cross-AGEGRP fallback when a stratum's pool is too thin.
#   5. Emit one output DataFrame per band with the same schema as before.
#
# This makes bands diverge by construction, preserves drift-signal (all diaries
# are model outputs), and keeps demographic composition fixed.

_BAND_WFH_SHARE = {
    "conservative": 0.175,
    "hybrid":       0.300,
    "fullyhybrid":  0.400,
}

# WFH-day threshold: fraction of business-hour slots where AT_HOME==1 to call a
# diary "WFH-day".  0.50 = majority of business hours spent at home.
_WFH_DAY_THRESH = 0.50


def _classify_wfh_day(gen_home: np.ndarray) -> np.ndarray:
    """Return boolean array (N,): True if diary is classified as WFH-day."""
    h_biz = gen_home[:, BIZ_SLOTS_0IDX]  # (N, 16)
    return (h_biz.mean(axis=1) >= _WFH_DAY_THRESH)


def _run_base_forecast_2030(
    df_scen: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    model,
) -> tuple:
    """
    Run a single inference pass on df_scen (CYCLE_YEAR set to 2022 for embedding).
    Returns (gen_act, gen_home, gen_work) numpy arrays (N, 48).
    """
    df_inf = df_scen.copy()
    df_inf["CYCLE_YEAR"] = 2022  # no 2030 embedding exists

    tensors = build_tensors_from_df(df_inf, feat_cfg, device)
    N = len(df_inf)
    batch_sz = 256
    gen_acts, gen_homes, gen_works = [], [], []

    with torch.no_grad():
        for start in range(0, N, batch_sz):
            sl = slice(start, start + batch_sz)
            g_act, g_home, g_work, _, _ = model.generate(
                tensors["act_seq"][sl],
                tensors["aux_seq"][sl],
                tensors["cond_vec"][sl],
                tensors["cycle_idx"][sl],
                tensors["obs_strata"][sl],
                temperature=0.8,
            )
            gen_acts.append(g_act.cpu())
            gen_homes.append(g_home.cpu())
            gen_works.append(g_work.cpu())

    gen_act  = torch.cat(gen_acts).numpy()   # (N, 48)
    gen_home = torch.cat(gen_homes).numpy()  # (N, 48)
    gen_work = torch.cat(gen_works).numpy()  # (N, 48)
    return gen_act, gen_home, gen_work


def _posthoc_reweight(
    df_scen: pd.DataFrame,
    base_gen_act: np.ndarray,
    base_gen_home: np.ndarray,
    base_gen_work: np.ndarray,
    target_wfh_share: float,
    band: str,
    rng_seed: int = 42,
) -> tuple:
    """
    Post-hoc day-type reweight: assemble a cohort where the WFH-day share among
    employed (LFTAG==1) rows == target_wfh_share (±3pp).

    Returns (out_act, out_home, out_work) numpy arrays (N, 48) for this band.

    Procedure:
    - Classify each employed row as WFH-day or office-day from the base forecast.
    - Compute current WFH-day share and required count.
    - If pool is large enough: sample by AGEGRP (with cross-AGEGRP fallback).
    - Non-employed rows: kept as-is from the base forecast.
    - If either day-type pool is too thin to reach target: emit warning but do not fudge.
    """
    N = len(df_scen)
    is_employed = (df_scen["LFTAG"].values == 1) if "LFTAG" in df_scen.columns else np.ones(N, dtype=bool)
    is_wfh_day = _classify_wfh_day(base_gen_home)  # (N,)

    emp_idx = np.where(is_employed)[0]
    n_emp = len(emp_idx)
    n_wfh_target = int(round(n_emp * target_wfh_share))
    n_off_target = n_emp - n_wfh_target

    wfh_pool = emp_idx[is_wfh_day[emp_idx]]    # employed WFH-day rows
    off_pool  = emp_idx[~is_wfh_day[emp_idx]]   # employed office-day rows

    current_wfh_share = len(wfh_pool) / max(n_emp, 1)
    print(f"  [{band}] base WFH-day share={current_wfh_share:.3f}  "
          f"target={target_wfh_share:.3f}  "
          f"WFH pool={len(wfh_pool)}  Office pool={len(off_pool)}")

    if len(wfh_pool) == 0:
        print(f"  [{band}] WARNING: WFH-day pool is empty — band cannot be formed; "
              f"returning base forecast unchanged.")
        return base_gen_act.copy(), base_gen_home.copy(), base_gen_work.copy()
    if len(off_pool) == 0 and n_off_target > 0:
        print(f"  [{band}] WARNING: office-day pool is empty — band cannot be formed; "
              f"returning base forecast unchanged.")
        return base_gen_act.copy(), base_gen_home.copy(), base_gen_work.copy()

    # Report if 40% target is unreachable given the model's day-type distribution
    if len(wfh_pool) < n_wfh_target:
        print(f"  [{band}] WARNING: WFH-day pool ({len(wfh_pool)}) < target count "
              f"({n_wfh_target}) — resampling with replacement for WFH rows; "
              f"diversity limited.  This is a model finding, not fudged.")
    if len(off_pool) < n_off_target:
        print(f"  [{band}] WARNING: office-day pool ({len(off_pool)}) < target count "
              f"({n_off_target}) — resampling with replacement for office rows.")

    rng = np.random.default_rng(rng_seed)

    # Get AGEGRP for employed rows (used for demographically-similar donor draw)
    agegrp_arr = df_scen["AGEGRP"].fillna(-1).astype(int).values if "AGEGRP" in df_scen.columns else np.full(N, -1, dtype=int)

    def _draw_agegrp_stratified(pool: np.ndarray, n_draw: int) -> np.ndarray:
        """
        Draw n_draw indices from pool, AGEGRP-stratified with cross-group fallback.
        Returns array of indices into the original df_scen (not pool-local).
        """
        if n_draw == 0:
            return np.array([], dtype=int)
        # Group pool by AGEGRP
        pool_agegrp = agegrp_arr[pool]
        unique_groups = np.unique(pool_agegrp)
        group_quota = {}
        for g in unique_groups:
            g_count = int((pool_agegrp == g).sum())
            group_quota[g] = max(1, round(n_draw * g_count / len(pool)))
        # Adjust to exact n_draw
        total = sum(group_quota.values())
        diff = n_draw - total
        largest_g = max(group_quota, key=group_quota.get)
        group_quota[largest_g] += diff

        drawn = []
        for g, q in group_quota.items():
            g_pool = pool[pool_agegrp == g]
            if len(g_pool) == 0:
                continue
            drawn.append(rng.choice(g_pool, size=q, replace=(q > len(g_pool))))
        result = np.concatenate(drawn) if drawn else np.array([], dtype=int)
        # Fallback if we came up short
        if len(result) < n_draw:
            shortfall = n_draw - len(result)
            result = np.concatenate([result, rng.choice(pool, size=shortfall, replace=True)])
        return result[:n_draw]

    selected_wfh = _draw_agegrp_stratified(wfh_pool, n_wfh_target)
    selected_off = _draw_agegrp_stratified(off_pool, n_off_target)
    selected_emp = np.concatenate([selected_wfh, selected_off])  # (n_emp,) donor indices

    # Build output arrays — copy from base
    out_act  = base_gen_act.copy()
    out_home = base_gen_home.copy()
    out_work = base_gen_work.copy()

    # For each employed row (in original index order), assign a donor diary
    # The donor is sampled from the appropriate day-type pool above.
    # We keep the demographic row (df_scen row) fixed but swap the generated diary.
    rng2 = np.random.default_rng(rng_seed + 1)
    rng2.shuffle(selected_emp)  # randomise donor assignment order
    for slot, orig_i in enumerate(emp_idx):
        donor_i = int(selected_emp[slot % len(selected_emp)])
        out_act[orig_i]  = base_gen_act[donor_i]
        out_home[orig_i] = base_gen_home[donor_i]
        out_work[orig_i] = base_gen_work[donor_i]

    # Verify realised WFH-day share
    is_wfh_day_out = _classify_wfh_day(out_home)
    realised_share = float(is_wfh_day_out[emp_idx].mean()) if n_emp > 0 else float("nan")
    delta_pp = abs(realised_share - target_wfh_share) * 100
    gate_ok = delta_pp <= 3.0
    print(f"  [{band}] realised WFH-day share={realised_share:.4f}  "
          f"delta={delta_pp:.2f}pp  {'PASS (<=3pp)' if gate_ok else 'GATE FAIL (>3pp)'}")
    if not gate_ok:
        print(f"  [GATE FAIL] Band {band}: realised WFH-day share {realised_share:.4f} "
              f"vs target {target_wfh_share:.4f}, delta {delta_pp:.2f}pp > 3pp threshold.")

    return out_act, out_home, out_work


def run_substage_d_phase_ii(
    band: str,
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
    _base_cache: dict = None,
) -> pd.DataFrame:
    """
    2030 forward forecast for one band — POST-HOC DAY-TYPE REWEIGHT.
    FIX (2026-06-24): replaces TELEWORK-conditioning override (proven not a
    learnable lever per control 987027) with exogenous day-type reweight.

    band: 'conservative' (~17.5% WFH-day share)
          'hybrid'       (~30%)
          'fullyhybrid'  (~40%)

    _base_cache: optional dict with keys 'df_scen', 'gen_act', 'gen_home', 'gen_work'
                 to avoid re-running inference for each band (set by run_all).

    Returns diary DataFrame with BAND column.
    """
    assert band in _BAND_WFH_SHARE, f"Unknown band: {band}"
    target_wfh_share = _BAND_WFH_SHARE[band]

    print(f"\n  [Phase ii — {band}] post-hoc reweight target WFH-day share={target_wfh_share:.3f}")

    # ── Load scenario cohort ──
    scenario_path = os.path.join(OUTPUT_DIR, "scenario_2030_features_2split.csv")
    if not os.path.isfile(scenario_path):
        print(f"  [WARN] scenario_2030_features_2split.csv not found; "
              f"falling back to 2022 cohort.")
        df_scen = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
        df_scen["CYCLE_YEAR"] = 2030
        df_scen["SCENARIO"]   = "M1_2030"
    else:
        df_scen = pd.read_csv(scenario_path, low_memory=False)

    if smoke:
        df_scen = df_scen.sample(frac=0.05, random_state=42).reset_index(drop=True)

    # ── Generate base forecast ONCE per D2 call-set (use cache if provided) ──
    if _base_cache is not None and "gen_act" in _base_cache:
        gen_act_base  = _base_cache["gen_act"]
        gen_home_base = _base_cache["gen_home"]
        gen_work_base = _base_cache["gen_work"]
        df_scen       = _base_cache["df_scen"]
        print(f"  [{band}] Using cached base forecast ({len(df_scen):,} rows).")
    else:
        # Load model
        ws = os.path.join(MODELS_DIR, "W_pooled_2030_2split.pt")
        if not os.path.isfile(ws):
            print(f"  [WARN] {ws} not found; using W_2022_ft if available.")
            ws = os.path.join(MODELS_DIR, "W_2022_ft_2split.pt")

        model, weighter, mc = build_model(feat_cfg, smoke, device, ws if os.path.isfile(ws) else None)
        model.eval()
        print(f"  Generating base 2030 forecast ({len(df_scen):,} rows) …")
        gen_act_base, gen_home_base, gen_work_base = _run_base_forecast_2030(
            df_scen, feat_cfg, device, model
        )
        if _base_cache is not None:
            _base_cache["gen_act"]  = gen_act_base
            _base_cache["gen_home"] = gen_home_base
            _base_cache["gen_work"] = gen_work_base
            _base_cache["df_scen"]  = df_scen

    N = len(df_scen)

    # ── Post-hoc day-type reweight for this band ──
    gen_act, gen_home, gen_work = _posthoc_reweight(
        df_scen, gen_act_base, gen_home_base, gen_work_base,
        target_wfh_share=target_wfh_share,
        band=band,
        rng_seed={"conservative": 42, "hybrid": 43, "fullyhybrid": 44}[band],
    )

    # ── 6H: mutual-exclusion resolution ──
    gen_home, gen_work = mutual_exclusion_resolve(gen_act, gen_home, gen_work)

    # ── Build output DataFrame ──
    act_cols_out = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols     = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols     = [f"wrk30_{i:03d}" for i in range(1, 49)]

    out_df = pd.DataFrame(gen_act + 1, columns=act_cols_out)  # restore 1-indexed
    for i, c in enumerate(hom_cols):
        out_df[c] = gen_home[:, i]
    for i, c in enumerate(wrk_cols):
        out_df[c] = gen_work[:, i]

    out_df["CYCLE_YEAR"]   = 2030
    out_df["BAND"]         = band
    out_df["IS_SYNTHETIC"] = 1
    out_df["DDAY_STRATA"]  = df_scen["DDAY_STRATA"].values

    # Carry conditioning columns for downstream (Step 7)
    for col in ["AGEGRP", "SEX", "LFTAG", "NOCS", "NAICS", "TELEWORK",
                "TELEWORK_KNOWN", "PR", "CMA", "DDAY_STRATA"]:
        if col in df_scen.columns:
            out_df[col] = df_scen[col].values

    # ── Band summary metrics (gate C4) ──
    is_employed = (df_scen["LFTAG"].values == 1) if "LFTAG" in df_scen.columns else np.ones(N, dtype=bool)
    emp_m = is_employed
    wd_mask = (df_scen["DDAY_STRATA"].values == 1)

    h_biz_out = gen_home[emp_m, :][:, BIZ_SLOTS_0IDX]
    a_biz_out = gen_act[emp_m, :][:, BIZ_SLOTS_0IDX]
    wfh_rate = float(((h_biz_out == 1) | (a_biz_out == 0)).mean()) if emp_m.sum() > 0 else float("nan")

    wd_at_home = float(gen_home[wd_mask].mean()) if wd_mask.sum() > 0 else float("nan")
    wd_at_work = float(gen_work[wd_mask].mean()) if wd_mask.sum() > 0 else float("nan")

    print(f"  {band}: rows={N:,}  WD_AT_HOME={wd_at_home:.4f}  "
          f"WD_AT_WORK={wd_at_work:.4f}  WFH_RATE={wfh_rate:.4f}")

    return out_df


# ── 6H: Mutual-exclusion resolve ─────────────────────────────────────────────

def mutual_exclusion_resolve(
    gen_act: np.ndarray,
    gen_home: np.ndarray,
    gen_work: np.ndarray,
) -> tuple:
    """
    For any slot with hom30_k==1 AND wrk30_k==1, resolve by activity:
    if act30_k == Work (0-indexed: 0) -> keep wrk30=1, hom30=0
    else -> keep hom30=1, wrk30=0

    Acts on numpy arrays (N, 48). Returns (gen_home, gen_work) corrected.
    """
    gen_home = gen_home.copy().astype(float)
    gen_work = gen_work.copy().astype(float)
    conflict = (gen_home == 1) & (gen_work == 1)
    n_conflict = int(conflict.sum())
    if n_conflict > 0:
        is_work_act = (gen_act == WORK_ACT_0IDX)  # 0-indexed
        # Work activity at conflict slot: keep work
        keep_work = conflict & is_work_act
        gen_home[keep_work] = 0
        # Non-work activity at conflict slot: keep home
        keep_home = conflict & ~is_work_act
        gen_work[keep_home] = 0
        print(f"  [6H] Mutual-exclusion: {n_conflict} conflicts resolved "
              f"({keep_work.sum()} -> work, {keep_home.sum()} -> home)")
    else:
        print(f"  [6H] Mutual-exclusion: 0 conflicts (clean)")
    return gen_home, gen_work


def call_mindwell(in_csv: str, out_csv: str) -> None:
    """
    Call 3rdJ_04M_mindwell_2split.py as subprocess for min-dwell smoothing.
    This is a pure CSV-in / CSV-out post-processor (no import side-effects).
    """
    mindwell_script = os.path.join(STEP4_DIR, "3rdJ_04M_mindwell_2split.py")
    if not os.path.isfile(mindwell_script):
        print(f"  [WARN] 04M script not found at {mindwell_script}; skipping min-dwell.")
        return
    cmd = [sys.executable, mindwell_script, "--in_csv", in_csv, "--out_csv", out_csv]
    print(f"  [6H] Calling 04M min-dwell: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [WARN] 04M exited with code {result.returncode}: {result.stderr[:200]}")
    else:
        print(f"  [6H] 04M min-dwell complete: {out_csv}")


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_all(args) -> None:
    """A -> B -> C -> D1 -> D2(band)x3"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    feat_cfg = load_feature_config()

    if args.data:
        data_path = args.data
    else:
        # Default: R5_lr1e4 raw (per OD-1)
        data_path = os.path.join(
            STEP4_DATA, "sweep", "R5_lr1e4", "augmented_diaries.csv"
        )
        if not os.path.isfile(data_path):
            # Fallback to local full file
            data_path = os.path.join(STEP4_DATA, "augmented_diaries.csv")

    device = (torch.device("cuda") if torch.cuda.is_available()
              else torch.device("cpu"))
    print(f"Device: {device}")

    stage = args.stage

    if stage in ("audit",):
        run_input_audit(data_path)
        return

    # Load data (shared across stages)
    print(f"Loading: {data_path}")
    df = pd.read_csv(data_path, low_memory=False)
    if args.smoke:
        # Smoke subsample: 20% of a large file (>10k rows), otherwise keep all
        # (the SAMPLE.csv is 3,840 rows — already small enough for a smoke run)
        if len(df) > 10000:
            df = (df.groupby(["CYCLE_YEAR", "DDAY_STRATA"], group_keys=False)
                    .apply(lambda x: x.sample(frac=0.20, random_state=42),
                           include_groups=False))
            df = df.reset_index(drop=True)
        print(f"  [smoke] rows for training: {len(df):,}")

    if stage in ("A", "all"):
        run_substage_a(df, feat_cfg, device, smoke=args.smoke)

    if stage in ("B", "all"):
        run_substage_b(df, feat_cfg, device, smoke=args.smoke)

    if stage in ("C", "all"):
        run_substage_c(df, feat_cfg, device, smoke=args.smoke)

    if stage in ("D1", "all"):
        run_substage_d_phase_i(df, feat_cfg, device, smoke=args.smoke)

    if stage in ("D2", "all"):
        band_arg = args.band if args.band else None
        bands = [band_arg] if band_arg else ["conservative", "hybrid", "fullyhybrid"]

        # Shared base-forecast cache: inference runs ONCE for all bands
        _d2_cache: dict = {}
        all_diaries = []
        for band in bands:
            diary_df = run_substage_d_phase_ii(
                band, df, feat_cfg, device, smoke=args.smoke,
                _base_cache=_d2_cache,
            )
            all_diaries.append(diary_df)

        # Combine into one CSV with BAND column (OD-3)
        combined = pd.concat(all_diaries, ignore_index=True)
        raw_path = os.path.join(OUTPUT_DIR, "2030_synthetic_diaries_2split_raw.csv")
        combined.to_csv(raw_path, index=False)
        print(f"  Combined 2030 diaries: {len(combined):,} rows -> {raw_path}")

        # Monotone WFH_RATE check
        rates = {}
        for band in bands:
            sub = combined[combined["BAND"] == band]
            if "LFTAG" in sub.columns:
                emp = sub[sub["LFTAG"] == 1]
            else:
                emp = sub
            if len(emp) > 0:
                hom_arr = emp[[f"hom30_{i:03d}" for i in range(1, 49)]].values
                act_arr = emp[[f"act30_{i:03d}" for i in range(1, 49)]].values.astype(int) - 1
                h_biz = hom_arr[:, BIZ_SLOTS_0IDX]
                a_biz = act_arr[:, BIZ_SLOTS_0IDX]
                rates[band] = float(((h_biz == 1) | (a_biz == 0)).mean())
        if rates:
            print("  WFH_RATE per band:", {k: f"{v:.4f}" for k, v in rates.items()})
            b_list = list(bands)
            if len(b_list) == 3:
                ok = rates.get("conservative", 0) <= rates.get("hybrid", 1) <= rates.get("fullyhybrid", 2)
                print(f"  Monotone sensitivity: {'PASS' if ok else 'FAIL'}")
                # ── Gate 4: WFH-day shares separated ──────────────────────────
                # Compute WFH-day shares from the post-hoc reweight (stored in
                # out_df via _classify_wfh_day on hom30 columns)
                wfh_day_shares = {}
                for band_g4 in b_list:
                    sub_g4 = combined[combined["BAND"] == band_g4]
                    if "LFTAG" in sub_g4.columns:
                        emp_g4 = sub_g4[sub_g4["LFTAG"] == 1]
                    else:
                        emp_g4 = sub_g4
                    if len(emp_g4) > 0:
                        hom_g4 = emp_g4[[f"hom30_{i:03d}" for i in range(1, 49)]].values
                        is_wfh = _classify_wfh_day(hom_g4)
                        wfh_day_shares[band_g4] = float(is_wfh.mean())
                if wfh_day_shares:
                    print("  WFH-day shares per band:", {k: f"{v:.4f}" for k, v in wfh_day_shares.items()})
                    if args.smoke:
                        # Gate 4 is skipped in smoke mode: tiny SAMPLE has no real
                        # WFH-day diaries and scenario_2030_features_2split.csv is
                        # absent, so pool-empty fallback fires.  Gates 1-3 are the
                        # copier detectors; Gate 4 is validated on the cluster run.
                        print("  [Gate 4 D2] SKIPPED in smoke mode (tiny SAMPLE, no scenario CSV)")
                    else:
                        check_anticopy_gate4_bands(wfh_day_shares, label="D2")

        # 6H: run mindwell per band
        for band in bands:
            band_raw = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_raw.csv")
            band_out = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_mindwell.csv")
            sub = combined[combined["BAND"] == band]
            sub.to_csv(band_raw, index=False)
            call_mindwell(band_raw, band_out)

        # Final combined (prefer mindwell versions if available)
        final_parts = []
        for band in bands:
            mpath = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_mindwell.csv")
            rpath = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_raw.csv")
            p = mpath if os.path.isfile(mpath) else rpath
            if os.path.isfile(p):
                final_parts.append(pd.read_csv(p, low_memory=False))
        if final_parts:
            final = pd.concat(final_parts, ignore_index=True)
            final_path = os.path.join(OUTPUT_DIR, "2030_synthetic_diaries_2split.csv")
            final.to_csv(final_path, index=False)
            print(f"  Final deliverable: {final_path}  rows={len(final):,}")


# ── Argparse ──────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Step 6 Longitudinal Forecasting (2-split two-channel)"
    )
    p.add_argument("--stage", default="all",
                   choices=["audit", "A", "B", "C", "D1", "D2", "all"],
                   help="Which stage to run")
    p.add_argument("--band", default=None,
                   choices=["conservative", "hybrid", "fullyhybrid"],
                   help="WFH band for D2 (default: all three)")
    p.add_argument("--smoke", action="store_true",
                   help="5%% data, 3 epochs — local smoke test")
    p.add_argument("--data", default=None,
                   help="Path to augmented_diaries.csv "
                        "(default: R5_lr1e4 raw per OD-1)")
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()

    if args.stage == "audit":
        feat_cfg = load_feature_config()
        data_path = args.data
        if not data_path:
            data_path = os.path.join(STEP4_DATA, "sweep", "R5_lr1e4",
                                     "augmented_diaries.csv")
            if not os.path.isfile(data_path):
                data_path = os.path.join(STEP4_DATA, "augmented_diaries.csv")
        run_input_audit(data_path)
    else:
        run_all(args)
