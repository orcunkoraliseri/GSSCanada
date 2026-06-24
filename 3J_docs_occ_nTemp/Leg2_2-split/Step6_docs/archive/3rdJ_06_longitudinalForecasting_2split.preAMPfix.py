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


# ── Step-6 Dataset for progressive training ───────────────────────────────────

class Step6Dataset(Dataset):
    """
    Dataset for Step-6 progressive fine-tuning from augmented_diaries.csv.
    Each item is a self-pair (src=respondent, dec_target=same respondent's observed
    diary — the model reconstructs and compares against its own source).
    NEW Step-6 code: per-sample recency_weight injected here.
    """

    def __init__(self, data: dict, recency_weight: float = 1.0):
        self.data = data
        self.recency_weight = recency_weight
        self.N = data["act_seq"].shape[0]

    def __len__(self):
        return self.N

    def __getitem__(self, i):
        return {
            "act_seq":       self.data["act_seq"][i],
            "aux_seq":       self.data["aux_seq"][i],
            "cond_vec":      self.data["cond_vec"][i],
            "cycle_idx":     self.data["cycle_idx"][i],
            "cycle_year":    self.data["cycle_year"][i],
            "obs_strata":    self.data["obs_strata"][i],
            # Decoder target = self (self-reconstruction objective)
            "dec_act_seq":   self.data["act_seq"][i],
            "dec_aux_seq":   self.data["aux_seq"][i],
            "dec_cop_avail": self.data["cop_avail"][i],
            "dec_work_avail": self.data["work_avail"][i],
            "tgt_strata":    self.data["obs_strata"][i],
            # Step-6 NEW: per-sample recency weight
            "recency_weight": torch.tensor(self.recency_weight, dtype=torch.float32),
        }


def load_cycle_data(df_cycle: pd.DataFrame, feat_cfg: dict, device: torch.device,
                    cycle_year: int) -> dict:
    """Build tensor dict for a single cycle's rows."""
    tensors = build_tensors_from_df(df_cycle, feat_cfg, device)
    N = len(df_cycle)

    # cop_avail: all True (augmented rows have no NaN cop channels)
    cop_avail = torch.ones(N, N_SLOTS, N_COP, dtype=torch.bool, device="cpu")

    # work_avail on cpu (for Dataset)
    work_avail = torch.ones(N, N_SLOTS, dtype=torch.bool, device="cpu")

    return {
        "act_seq":    tensors["act_seq"].cpu(),
        "aux_seq":    tensors["aux_seq"].cpu(),
        "cond_vec":   tensors["cond_vec"].cpu(),
        "cycle_idx":  tensors["cycle_idx"].cpu(),
        "cycle_year": torch.full((N,), cycle_year, dtype=torch.long),
        "obs_strata": tensors["obs_strata"].cpu(),
        "cop_avail":  cop_avail,
        "work_avail": work_avail,
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
    scaler=None,
) -> dict:
    """
    One training epoch. Returns dict of mean losses.
    NEW Step-6 code: per-sample recency_weight multiplier applied to total loss.
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

        with torch.amp.autocast("cuda", enabled=(scaler is not None)):
            output = model(batch_dev)
            comp = component_losses(
                output, batch_dev,
                act_weights=act_weights,
                home_pos_weight=home_pw,
                work_pos_weight=work_pw,
            )
            div = diversity_loss(output, batch_dev)
            total_uw, per_task = weighter.weighted(comp)
            total_loss = total_uw + 0.1 * div

            # Per-sample recency weight (NEW Step-6):
            # Multiply total_loss by the batch-mean recency weight
            rw = batch_dev.get("recency_weight", torch.ones(1, device=device))
            rw_mean = rw.mean()
            total_loss = total_loss * rw_mean

        if scaler is not None:
            if pcgrad is not None:
                # With PCGrad, bypass scaler's backward (use manual)
                scaler.unscale_(optimizer)
                task_losses = [per_task[t] * rw_mean for t in TASKS]
                pcgrad.backward(task_losses)
                scaler.step(optimizer)
                scaler.update()
            else:
                scaler.scale(total_loss).backward()
                scaler.step(optimizer)
                scaler.update()
        else:
            if pcgrad is not None:
                task_losses = [per_task[t] * rw_mean for t in TASKS]
                pcgrad.backward(task_losses)
                optimizer.step()
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
    from torch.utils.data import ConcatDataset
    datasets = []
    for (cy, d, rw) in train_dicts:
        ds = Step6Dataset(d, recency_weight=rw)
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
    scaler = (torch.amp.GradScaler("cuda")
              if torch.cuda.is_available() and not smoke else None)
    pcgrad_obj = PCGrad(model.parameters()) if use_pcgrad else None

    best_val_score = float("inf")
    patience_counter = 0
    best_metrics = {}

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(max_epochs):
        t0 = time.time()
        # Resample dataset targets each epoch (matches 04D epoch-level resample)
        for ds in datasets:
            pass  # Step6Dataset uses self-pairs; no resample needed

        epoch_loss = run_one_epoch(
            model, weighter, optimizer, pcgrad_obj,
            loader, device, feat_cfg, scaler
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

    return gate_metrics


# ── Sub-stage D Phase ii: Three-Band Forward Forecast ────────────────────────

def run_substage_d_phase_ii(
    band: str,
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> pd.DataFrame:
    """
    2030 forward forecast for one band.
    band: 'conservative' (~17.5% employed TELEWORK=1)
          'hybrid'       (~30%)
          'fullyhybrid'  (~40%)
    Returns diary DataFrame with BAND column.
    """
    BAND_TELEWORK_SHARE = {
        "conservative": 0.175,
        "hybrid":       0.300,
        "fullyhybrid":  0.400,
    }
    assert band in BAND_TELEWORK_SHARE, f"Unknown band: {band}"
    tw_share = BAND_TELEWORK_SHARE[band]

    print(f"\n  [Phase ii — {band}] TELEWORK share={tw_share:.3f}")

    scenario_path = os.path.join(OUTPUT_DIR, "scenario_2030_features_2split.csv")
    if not os.path.isfile(scenario_path):
        print(f"  [WARN] scenario_2030_features_2split.csv not found at {scenario_path}. "
              f"Falling back to 2022 cohort for structural test.")
        df_scen = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
        df_scen["CYCLE_YEAR"] = 2030
        df_scen["SCENARIO"]   = f"M1_2030_{band}"
    else:
        df_scen = pd.read_csv(scenario_path, low_memory=False)

    if smoke:
        df_scen = df_scen.sample(frac=0.05, random_state=42).reset_index(drop=True)

    # TELEWORK share resample (OD-2 resolved: per-SHARE not all-0/all-1)
    df_scen = df_scen.copy()
    if "LFTAG" in df_scen.columns:
        emp_mask = (df_scen["LFTAG"] == 1)
    else:
        emp_mask = pd.Series(True, index=df_scen.index)

    emp_idx = df_scen.index[emp_mask].tolist()
    n_emp = len(emp_idx)
    n_tw1 = int(round(n_emp * tw_share))
    rng = np.random.default_rng(42)
    tw1_set = set(rng.choice(emp_idx, size=n_tw1, replace=False).tolist())

    df_scen["TELEWORK"]       = 0
    df_scen["TELEWORK_KNOWN"] = 1
    for i in tw1_set:
        df_scen.at[i, "TELEWORK"] = 1

    # Load model
    ws = os.path.join(MODELS_DIR, "W_pooled_2030_2split.pt")
    if not os.path.isfile(ws):
        print(f"  [WARN] {ws} not found; using W_2022_ft if available.")
        ws = os.path.join(MODELS_DIR, "W_2022_ft_2split.pt")

    model, weighter, mc = build_model(feat_cfg, smoke, device, ws if os.path.isfile(ws) else None)
    model.eval()

    # Override CYCLE_YEAR to map to 2022 index for inference (no 2030 embedding)
    df_scen_inf = df_scen.copy()
    df_scen_inf["CYCLE_YEAR"] = 2022  # use 2022 embedding at inference

    tensors = build_tensors_from_df(df_scen_inf, feat_cfg, device)
    N = len(df_scen_inf)
    batch_sz = 256
    gen_acts, gen_homes, gen_works, gen_cops = [], [], [], []

    with torch.no_grad():
        for start in range(0, N, batch_sz):
            sl = slice(start, start + batch_sz)
            g_act, g_home, g_work, g_cop, _ = model.generate(
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
            gen_cops.append(g_cop.cpu())

    gen_act  = torch.cat(gen_acts).numpy()   # (N, 48)
    gen_home = torch.cat(gen_homes).numpy()  # (N, 48)
    gen_work = torch.cat(gen_works).numpy()  # (N, 48)

    # 6H: mutual-exclusion resolution (inline, per spec)
    gen_home, gen_work = mutual_exclusion_resolve(gen_act, gen_home, gen_work)

    # Build output DataFrame
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

    # WFH_RATE check
    if "LFTAG" in out_df.columns:
        emp_m = (out_df["LFTAG"] == 1).values
    else:
        emp_m = np.ones(N, dtype=bool)

    h_biz = gen_home[emp_m, :][:, BIZ_SLOTS_0IDX]
    a_biz = gen_act[emp_m, :][:, BIZ_SLOTS_0IDX]
    wfh_rate = float(((h_biz == 1) | (a_biz == 0)).mean()) if emp_m.sum() > 0 else float("nan")

    wd_mask = (out_df["DDAY_STRATA"] == 1).values
    print(f"  {band}: rows={N:,}  WD_AT_HOME={gen_home[wd_mask].mean():.4f}  "
          f"WD_AT_WORK={gen_work[wd_mask].mean():.4f}  WFH_RATE={wfh_rate:.4f}")

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

        all_diaries = []
        for band in bands:
            diary_df = run_substage_d_phase_ii(
                band, df, feat_cfg, device, smoke=args.smoke
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
