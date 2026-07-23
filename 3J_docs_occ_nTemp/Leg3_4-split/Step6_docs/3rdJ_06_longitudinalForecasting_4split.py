# -*- coding: utf-8 -*-
"""
3rdJ_06_longitudinalForecasting_4split.py
Step 6 (Leg-3, Track A): Longitudinal Forecasting — Three-Channel 4-Split

Port of Leg-2's 3rdJ_06_longitudinalForecasting_2split.py (fork base, 2350
lines) extended with the AT_RETAIL channel. Leg-2 file is READ-ONLY / template
only — not imported, not modified. Implements progressive fine-tuning +
TrendEncoder4Split forecasting from four GSS cycles (2005/2010/2015/2022) to
project joint AT_HOME + AT_WORK + AT_RETAIL occupancy schedules to 2030.

Model: JSeriesHybrid4Split (imported from 3rdJ_04B_model_4split.py — LOCKED,
never modified here).
Training machinery: component_losses, diversity_loss, exclusivity_loss,
    PCGrad, js_divergence, TASK_GROUPS, LAMBDA_DIV imported from Leg-3's own
    3rdJ_04D_train_4split.py (module import — __main__ NOT triggered). Leg-3's
    Step-4 already made the fixed-alpha decision (WEIGHT_MODE=fixed,
    alpha_resid:alpha_work:alpha_retail = 1.0:0.5:0.3 + PCGrad) — Leg-2's
    UncertaintyWeighting mode is NOT ported (dr_L3-13: never SLAW/UW/GradNorm/
    DWA/CAGrad for Leg-3).
Deliverable decode: generate_nucleus(), calibrate_retail_prob(),
    exclusivity_projection(), apply_activity_override_3ch(),
    enforce_min_dwell_row() imported from Leg-3's own
    3rdJ_04E_inference_4split.py (module import — __main__ NOT triggered).
    3rdJ_04B_model_4split.py is NOT modified — nucleus top-p truncation lives
    entirely in 04E's external wrapper, reused here unchanged.
Progressive loop (warm-start / per-cycle subset / recency weights): NEW code
    here, ported structurally from Leg-2 Step-6.

Sub-steps implemented:
  6A  run_input_audit()      — 13 assertions/prints on the raw pool CSV,
                                extended with an AT_RETAIL COVID triple-signal.
  6B  TrendEncoder4Split, compute_drift_matrix_4split(), compute_wfh_rate()
      run_substage_a(), run_substage_b(), run_substage_c()
      run_substage_d_phase_i(), run_substage_d_phase_ii(band)
      run_all()
  6B2 assemble_scenario_2030_4split.py (separate file)
  6H  mutual_exclusion_resolve() [3-way hard-assertion guard], call_mindwell()

Usage:
    py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split.py --stage audit --data <csv>
    py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split.py --smoke --stage A --data <csv>
    py -3 -X utf8 3rdJ_06_longitudinalForecasting_4split.py --stage all --data <csv>
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
    _LEG3_BASE = os.path.normpath(
        r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split"
    )
elif os.path.isdir("/speed-scratch/o_iseri"):
    _LEG3_BASE = "/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split"
else:
    _LEG3_BASE = os.path.join(
        os.path.expanduser("~"),
        "GSSCanada", "GSSCanada-main", "3J_docs_occ_nTemp", "Leg3_4-split",
    )

STEP4_DIR  = os.path.join(_LEG3_BASE, "Step4_docs")
STEP4_DATA = os.path.join(STEP4_DIR, "outputs_step4")
STEP5_DIR  = os.path.join(_LEG3_BASE, "Step5_docs")
# Backcast REFERENCE only (never training) — Step-5 locked/raked pool of record.
# Comparison-only per the runbook (OD-1 discipline: train on raw, never raked).
# Not loaded by this script's stages; recorded here for provenance / future
# validator use.
STEP5_LOCKED_POOL = os.path.join(
    STEP5_DIR, "outputs_step5", "3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
)
STEP6_DIR  = os.path.join(_LEG3_BASE, "Step6_docs")
OUTPUT_DIR = os.path.join(STEP6_DIR, "outputs_step6")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

# Raw (pre-rake) training pool default. Per Step-4's own Progress Log
# (3rdJ_04_augmentationGSS_4split.md, 2026-07-21 entry): "DECISION (user-
# confirmed 2026-07-21): accept the seed_3_g3fix pool WHOLESALE" — the G3
# co-presence-fix rerun of the winning seed_3 checkpoint supersedes the
# original seed_3/augmented_diaries.csv (mtime 2026-07-21 13:04 > 2026-07-19
# 18:11; activities 99.9998% identical to seed_3, co-presence internally
# consistent post-fix). seed_3 is PRESERVED, not deleted — this default just
# points at the more-precise, decision-confirmed pool. `--data` overrides.
_RAW_POOL_CANDIDATES = [
    os.path.join(STEP4_DATA, "seed_3_g3fix", "augmented_diaries.csv"),
    os.path.join(STEP4_DATA, "seed_3", "augmented_diaries.csv"),
    os.path.join(STEP4_DATA, "augmented_diaries.csv"),
]


def _default_raw_pool_path() -> str:
    for p in _RAW_POOL_CANDIDATES:
        if os.path.isfile(p):
            return p
    return _RAW_POOL_CANDIDATES[0]  # report-and-fail with the canonical path


# ── Import LOCKED Step-4 modules (import-only; never edit) ───────────────────

sys.path.insert(0, STEP4_DIR)

# 04B: model class (LOCKED — architecture, do not touch)
_04b = importlib.import_module("3rdJ_04B_model_4split")
JSeriesHybrid4Split = _04b.JSeriesHybrid4Split

# 04D: fixed-alpha + PCGrad loss machinery (module import does NOT run __main__)
_04d = importlib.import_module("3rdJ_04D_train_4split")
component_losses  = _04d.component_losses
diversity_loss    = _04d.diversity_loss
exclusivity_loss  = _04d.exclusivity_loss
PCGrad            = _04d.PCGrad
js_divergence      = _04d.js_divergence   # numpy (p, q) -> float
TASK_GROUPS        = _04d.TASK_GROUPS     # ["resid", "work", "retail"]
LAMBDA_DIV          = _04d.LAMBDA_DIV

# 04E: deliverable decode (nucleus AR + retail calibration + exclusivity
# projection + activity override + min-dwell) — reused verbatim, not
# reimplemented (module import does NOT run __main__)
_04e = importlib.import_module("3rdJ_04E_inference_4split")
generate_nucleus          = _04e.generate_nucleus
calibrate_retail_prob     = _04e.calibrate_retail_prob
exclusivity_projection    = _04e.exclusivity_projection
apply_activity_override_3ch = _04e.apply_activity_override_3ch
enforce_min_dwell_row      = _04e.enforce_min_dwell_row

# ── Constants ─────────────────────────────────────────────────────────────────

N_SLOTS      = 48
N_ACT        = 14
N_COP        = 9
N_AUX        = 12   # [AT_HOME | AT_WORK | AT_RETAIL | 9 co-presence]  (Leg-3)
CYCLE_YEARS  = [2005, 2010, 2015, 2022]
CYCLE_MAP    = {2005: 0, 2010: 1, 2015: 2, 2022: 3}

# Business-hours slots [09:00, 17:00) = slots 11..26 (1-indexed from 04:00 origin).
# 0-indexed: slots 10..25 (slot 10 = 09:00-09:30 … slot 25 = 16:30-17:00)
BIZ_SLOTS_0IDX = list(range(10, 26))  # 0-indexed, 16 slots

# Recency weights per cycle (per-sample multiplier on the loss) — verbatim Leg-2
RECENCY_WEIGHTS = {2005: 0.10, 2010: 0.20, 2015: 0.30, 2022: 0.40}

# Fixed-alpha task weights (Delta D, Leg-3 Step-4's own frozen decision) —
# order matches TASK_GROUPS = ["resid", "work", "retail"]
DEFAULT_ALPHAS = {"resid": 1.0, "work": 0.5, "retail": 0.3}
LAMBDA_EXCL = 0.05  # exclusivity soft-penalty weight (Delta C/E), active throughout
                     # Step-6 fine-tuning (no warmup-only-retail-head phase here —
                     # the retail head is already warm from Step-4's own 2-phase
                     # schedule by the time Step-6 warm-starts from its checkpoint).

# Deliverable decode settings (runbook 6F: T 0.7 + nucleus p=0.9 + min-dwell,
# never greedy) — used for D1 backcast AND D2 2030 generation.
DELIVERABLE_TEMPERATURE = 0.7
DELIVERABLE_TOP_P       = 0.9
DELIVERABLE_MIN_DWELL   = 2
# Exclusivity projection thresholds — identical to Step-4's own 04E defaults
# (theta_home/work/retail), so Step-6's decode chain matches Step-4's exactly.
THETA_HOME   = 0.50
THETA_WORK   = 0.40
THETA_RETAIL = 0.15

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

# aux_seq column order — MUST match step4_feature_config.json's "aux_order"
# ([AT_HOME, AT_WORK, AT_RETAIL] + 9 co-presence channels, in that order).
AUX_HOME_IDX   = 0
AUX_WORK_IDX   = 1
AUX_RETAIL_IDX = 2
AUX_COP_START  = 3

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
    13 assertions / prints over the raw pool CSV, extended with the
    AT_RETAIL COVID triple-signal (home up, work down, retail down).
    Returns the loaded dataframe for reuse.
    """
    print("\n" + "=" * 60)
    print("SUB-STEP 6A — INPUT AUDIT (4-split)")
    print("=" * 60)
    print(f"  Loading: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"  Rows: {len(df):,}  Cols: {len(df.columns)}")

    # --- 1. Row count (informational only; 4-split pool size differs from 2-split) ---
    n = len(df)
    print(f"  [1] Row count {n:,}")

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

    # --- 7b. ret30 columns [Leg-3 NEW] ---
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]
    missing_ret = [c for c in ret_cols if c not in df.columns]
    assert not missing_ret, f"Missing ret30 columns: {missing_ret[:5]}"
    ret_vals = df[ret_cols].values.flatten()
    ret_vals = ret_vals[~np.isnan(ret_vals.astype(float))]
    assert set(np.unique(ret_vals)).issubset({0.0, 1.0}), \
        f"ret30 non-binary values: {np.unique(ret_vals)}"
    ret_rate = float(ret_vals.mean())
    print(f"  [7b] ret30_001..048 present (48 cols); values in {{0,1}}; "
          f"overall positive rate={ret_rate:.4f}  PASS")

    # --- 8. Co-presence columns ---
    cop_expected = [f"{ch}30_{i:03d}" for ch in COP_COLS for i in range(1, 49)]
    missing_cop = [c for c in cop_expected if c not in df.columns]
    assert not missing_cop, f"Missing co-presence columns: {missing_cop[:5]}"
    print(f"  [8] 9 x 48 = 432 co-presence columns present  PASS")

    # --- 9. Mutual-exclusion overlap (MEASURE, do not assert 0) — now 3-way ---
    hom_arr = df[hom_cols].values.astype(float)
    wrk_arr = df[wrk_cols].values.astype(float)
    ret_arr = df[ret_cols].values.astype(float)
    active = (hom_arr == 1).astype(int) + (wrk_arr == 1).astype(int) + (ret_arr == 1).astype(int)
    total_slots = hom_arr.size
    overlap_rate = float((active > 1).sum()) / total_slots
    flag_str = "FLAG: >5% overlap — model pathology" if overlap_rate > 0.05 else "OK (expected ~0 post-04E exclusivity projection)"
    print(f"  [9] >1-of-3-channel co-occurrence rate: {overlap_rate:.4f}  {flag_str}")

    # --- 10. TELEWORK ---
    assert "TELEWORK" in df.columns, "TELEWORK column missing"
    tw_nan_frac = df["TELEWORK"].isna().mean()
    print(f"  [10] TELEWORK present  PASS  (NaN fraction: {tw_nan_frac:.3f})")

    # --- 11. NOCS and NAICS ---
    assert "NOCS" in df.columns, "NOCS column missing"
    assert "NAICS" in df.columns, "NAICS column missing"
    print(f"  [11] NOCS and NAICS present  PASS")

    # --- 12. Per-cycle AT_HOME, AT_WORK, AT_RETAIL, WFH_RATE ---
    print("  [12] Per-cycle summary (WD only, stratum==1):")
    wd = df[df["DDAY_STRATA"] == 1]
    for cy in expected_cy:
        cydf = wd[wd["CYCLE_YEAR"] == cy]
        if len(cydf) == 0:
            continue
        h_arr = cydf[hom_cols].values.astype(float)
        w_arr = cydf[wrk_cols].values.astype(float)
        r_arr = cydf[ret_cols].values.astype(float)

        at_home_wd  = float(h_arr.mean())
        at_work_wd  = float(w_arr.mean())
        at_retail_wd = float(r_arr.mean())

        # WFH_RATE: slots 11..26 (1-indexed) = indices 10..25 (0-indexed)
        wfh_rate = compute_wfh_rate(cydf, cy)
        print(f"    {cy}  AT_HOME_WD={at_home_wd:.4f}  AT_WORK_WD={at_work_wd:.4f}  "
              f"AT_RETAIL_WD={at_retail_wd:.4f}  WFH_RATE={wfh_rate:.4f}")

    # --- 13. COVID triple-signal check (informational) [Leg-3: home/work/retail] ---
    wd22 = wd[wd["CYCLE_YEAR"] == 2022]
    wd15 = wd[wd["CYCLE_YEAR"] == 2015]
    if len(wd22) > 0 and len(wd15) > 0:
        h22 = float(wd22[hom_cols].values.astype(float).mean())
        h15 = float(wd15[hom_cols].values.astype(float).mean())
        w22 = float(wd22[wrk_cols].values.astype(float).mean())
        w15 = float(wd15[wrk_cols].values.astype(float).mean())
        r22 = float(wd22[ret_cols].values.astype(float).mean())
        r15 = float(wd15[ret_cols].values.astype(float).mean())
        print(f"  [13] COVID signal: AT_HOME 2022 vs 2015: {h22:.4f} vs {h15:.4f} "
              f"(delta {h22-h15:+.4f})  |  AT_WORK 2022 vs 2015: {w22:.4f} vs {w15:.4f} "
              f"(delta {w22-w15:+.4f})  |  AT_RETAIL 2022 vs 2015: {r22:.4f} vs {r15:.4f} "
              f"(delta {r22-r15:+.4f})")
        if h22 > h15 and w22 < w15 and r22 < r15:
            print("      COVID TRIPLE signal CONFIRMED: AT_HOME up, AT_WORK down, AT_RETAIL down.")
        else:
            print("      [WARN] COVID triple signal not clearly confirmed on the raw pool "
                  "(soft blocker — investigate, do not hard-fail per the val plan).")

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

    home_or_wact = (h_biz == 1) | (a_biz == 1)  # act raw=1 corresponds to Work cat
    return float(home_or_wact.mean())


# ── Feature encoding: build cond_vec from df row(s) ─────────────────────────
# Replicated from 04A (featurization is inside its __main__-guarded data
# pipeline). d_cond is fully driven by step4_feature_config.json (Leg-3:
# d_cond=120); this code is unchanged from Leg-2 in structure.

def build_cond_vec_from_df(df: pd.DataFrame, feat_cfg: dict) -> np.ndarray:
    """
    Build the (N, d_cond) conditioning vector from a dataframe slice of the
    raw pool CSV using the step4_feature_config.json spec. Returns float32
    numpy array of shape (N, d_cond).
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
                        m1 = cats.get(-1, None)
                        if m1 is not None:
                            oh[i, m1] = 1.0
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
    Build all tensors needed for model inference from raw-pool rows.
    Returns dict with act_seq, aux_seq (width-12: home/work/retail/9cop),
    cond_vec, cycle_idx, work_avail, retail_avail, obs_strata.
    """
    N = len(df)
    act_cols = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]   # [Leg-3 NEW]
    cop_cols = [f"{ch}30_{i:03d}" for ch in COP_COLS for i in range(1, 49)]

    # Activity: raw 1..14 -> 0-indexed (subtract 1)
    act_np = df[act_cols].fillna(5).values.astype(np.int64) - 1
    act_np = np.clip(act_np, 0, N_ACT - 1)
    act_seq = torch.tensor(act_np, dtype=torch.long, device=device)

    # Home / work / retail: shape (N, 48)
    hom_np = df[hom_cols].fillna(0).values.astype(np.float32)
    wrk_np = df[wrk_cols].fillna(0).values.astype(np.float32)
    ret_np = df[ret_cols].fillna(0).values.astype(np.float32)   # [Leg-3 NEW]

    # Co-presence: (N, 48, 9) — columns are ordered as COP_COLS x slots
    cop_mat = np.zeros((N, N_SLOTS, N_COP), dtype=np.float32)
    for c_idx, ch in enumerate(COP_COLS):
        ch_cols = [f"{ch}30_{i:03d}" for i in range(1, 49)]
        present = [c for c in ch_cols if c in df.columns]
        if present:
            cop_mat[:, :len(present), c_idx] = df[present].fillna(0).values.astype(np.float32)

    # aux_seq: (N, 48, 12) = [AT_HOME | AT_WORK | AT_RETAIL | 9 cop]
    # Order MUST match step4_feature_config.json's "aux_order" (Leg-3 delta).
    aux_np = np.concatenate([
        hom_np[:, :, None],   # (N, 48, 1)
        wrk_np[:, :, None],   # (N, 48, 1)
        ret_np[:, :, None],   # (N, 48, 1)  [Leg-3 NEW]
        cop_mat,              # (N, 48, 9)
    ], axis=-1)
    aux_seq = torch.tensor(aux_np, dtype=torch.float32, device=device)

    # work_avail / retail_avail: True where the column is present (proxy:
    # all-True — the raw pool has no NaN 0/1 occupancy values, mirroring Leg-2).
    work_avail   = torch.ones(N, N_SLOTS, dtype=torch.bool, device=device)
    retail_avail = torch.ones(N, N_SLOTS, dtype=torch.bool, device=device)   # [Leg-3 NEW]

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
        "act_seq":      act_seq,
        "aux_seq":      aux_seq,
        "cond_vec":     cond_vec,
        "cycle_idx":    cycle_idx,
        "work_avail":   work_avail,
        "retail_avail": retail_avail,   # [Leg-3 NEW]
        "obs_strata":   obs_strata,
    }


# ── Cross-day KNN pairing (ported UNCHANGED from Leg-2 — channel-agnostic) ───
#
# Operates only on demographic/stratum columns, never touches activity/home/
# work/retail arrays, so no Leg-3 changes are needed here. This is the fix
# for the known Leg-2 self-pairing bug (src==tgt -> identity autoencoder ->
# backcast JS = -0.0000). Structural guarantee: build_cycle_pairs() only ever
# draws candidates from a DIFFERENT DDAY_STRATA than the source's own
# (`s_tgt != s_obs`), and additionally filters `j != src_i` within that
# different-stratum candidate pool — so t == s is structurally impossible.
# No extra runtime assert is added (would duplicate this structural guarantee).

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
    Build cross-day KNN pairs for a single cycle's subset, exactly per 04C logic.
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
    Dataset for Step-6 progressive fine-tuning from the raw pool CSV.
    Uses cross-day KNN pairs (src≠tgt, different DDAY_STRATA) exactly
    mirroring 04C/04D semantics (ported unchanged from Leg-2). Adds
    dec_retail_avail alongside dec_work_avail [Leg-3 NEW].
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
            # Decoder target: cross-day KNN neighbour (t≠s, different stratum).
            # Decoder target's own stratum is what the model must generate FOR
            # (renamed to tgt_strata to match 04B's generate()/forward() kwarg
            # name — same tensor Leg-2 called "tgt_strata" via obs_strata[t]).
            "dec_act_seq":     self.data["act_seq"][t],
            "dec_aux_seq":     self.data["aux_seq"][t],
            "dec_cop_avail":   self.data["cop_avail"][t],
            "dec_work_avail":  self.data["work_avail"][t],
            "dec_retail_avail": self.data["retail_avail"][t],   # [Leg-3 NEW]
            "tgt_strata":      self.data["obs_strata"][t],
            # Step-6 NEW: per-sample recency weight
            "recency_weight": torch.tensor(self.recency_weight, dtype=torch.float32),
        }


def load_cycle_data(df_cycle: pd.DataFrame, feat_cfg: dict, device: torch.device,
                    cycle_year: int) -> dict:
    """
    Build tensor dict for a single cycle's rows + cross-day KNN pairs.
    """
    tensors = build_tensors_from_df(df_cycle, feat_cfg, device)
    N = len(df_cycle)

    cop_avail = torch.ones(N, N_SLOTS, N_COP, dtype=torch.bool, device="cpu")
    work_avail   = torch.ones(N, N_SLOTS, dtype=torch.bool, device="cpu")
    retail_avail = torch.ones(N, N_SLOTS, dtype=torch.bool, device="cpu")   # [Leg-3 NEW]

    pairs = build_cycle_pairs(df_cycle, seed=42)

    return {
        "act_seq":      tensors["act_seq"].cpu(),
        "aux_seq":      tensors["aux_seq"].cpu(),
        "cond_vec":     tensors["cond_vec"].cpu(),
        "cycle_idx":    tensors["cycle_idx"].cpu(),
        "cycle_year":   torch.full((N,), cycle_year, dtype=torch.long),
        "obs_strata":   tensors["obs_strata"].cpu(),
        "cop_avail":    cop_avail,
        "work_avail":   work_avail,
        "retail_avail": retail_avail,   # [Leg-3 NEW]
        "pairs":        pairs,
    }


# ── Progressive training loop (NEW Step-6 code) ───────────────────────────────

def build_model(feat_cfg: dict, smoke: bool, device: torch.device,
                warm_start_path: str = None) -> tuple:
    """
    Build JSeriesHybrid4Split. NO weighter (Leg-2's UncertaintyWeighting is NOT
    ported — Leg-3 uses fixed-alpha scalarization, §3 of the builder prompt).
    Returns (model, model_config).
    Warm-start block: ported unchanged from Leg-2 (assert d_cond match, adopt
    checkpoint's saved model_config wholesale) — architecture-agnostic.
    """
    d_cond = feat_cfg["d_cond"]
    n_aux  = feat_cfg.get("n_aux", N_AUX)
    if smoke:
        model_config = {
            "model_type": "J3", "d_model": 64, "n_heads": 2, "d_ff": 256,
            "N_enc": 2, "N_dec": 2, "d_act": 16, "d_cycle": 16, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": n_aux, "d_cond": d_cond,
        }
    else:
        model_config = {
            "model_type": "J3", "d_model": 256, "n_heads": 8, "d_ff": 1024,
            "N_enc": 6, "N_dec": 6, "d_act": 32, "d_cycle": 32, "dropout": 0.1,
            "n_activity_classes": 14, "n_copresence": 9, "n_slots": 48,
            "n_aux": n_aux, "d_cond": d_cond,
        }

    if warm_start_path and os.path.isfile(warm_start_path):
        ck = torch.load(warm_start_path, map_location=device, weights_only=False)
        saved_cfg = ck.get("model_config", model_config)
        if saved_cfg.get("d_cond") not in (None, d_cond):
            raise ValueError(
                f"Warm-start d_cond mismatch: ckpt={saved_cfg.get('d_cond')} "
                f"vs current={d_cond}"
            )
        model_config = saved_cfg
        model = JSeriesHybrid4Split(model_config).to(device)
        model.load_state_dict(ck["model_state"])
        print(f"  Warm-start loaded: {warm_start_path}")
    else:
        model = JSeriesHybrid4Split(model_config).to(device)

    return model, model_config


# ── Deliverable decode helper (D1 backcast + D2 2030) ─────────────────────────
#
# Wraps Step-4's OWN generate_nucleus() (04E) + calibration + exclusivity
# projection + activity override + min-dwell — reused verbatim per §6 of the
# builder prompt (do not reimplement decode logic; do not touch 04B).

def decode_deliverable(model, act_t, aux_t, cond_t, cidx_t, tgt_strata_t,
                       retail_pos_weight: float,
                       temperature: float = DELIVERABLE_TEMPERATURE,
                       top_p: float = DELIVERABLE_TOP_P,
                       home_thr: float = THETA_HOME,
                       work_thr: float = THETA_WORK,
                       retail_thr: float = THETA_RETAIL,
                       min_dwell: int = DELIVERABLE_MIN_DWELL) -> tuple:
    """
    Deliverable-settings decode (T 0.7 + nucleus p=0.9 + min-dwell) — never
    greedy. Returns (act_np, home_np, work_np, retail_np, raw_isr, post_isr)
    all numpy, shape (N,48) except the two ISR scalars.
    """
    (act_tok, _gh, _gw, _gcop, _gcop_probs,
     home_sig, work_sig, retail_sig) = generate_nucleus(
        model, act_t, aux_t, cond_t, cidx_t, tgt_strata_t,
        temperature=temperature, top_p=top_p,
    )
    act_np       = act_tok.cpu().numpy()
    home_p       = home_sig.cpu().numpy()
    work_p       = work_sig.cpu().numpy()
    retail_p_raw = retail_sig.cpu().numpy()

    # Delta C/F#3: -ln(k) calibration shift (prob-space identity)
    retail_p_cal = calibrate_retail_prob(retail_p_raw, retail_pos_weight)

    # Delta G: exclusivity projection (raw ISR + post-projection ISR)
    home_bin, work_bin, retail_bin, raw_isr, post_isr = exclusivity_projection(
        home_p, work_p, retail_p_cal, home_thr, work_thr, retail_thr,
    )

    N = act_np.shape[0]
    home_out   = np.zeros_like(home_bin)
    work_out   = np.zeros_like(work_bin)
    retail_out = np.zeros_like(retail_bin)
    for i in range(N):
        h, w, r = apply_activity_override_3ch(act_np[i], home_bin[i], work_bin[i], retail_bin[i])
        w = enforce_min_dwell_row(w, min_dwell)
        r = enforce_min_dwell_row(r, min_dwell)
        home_out[i] = h
        work_out[i] = w
        retail_out[i] = r

    return act_np, home_out, work_out, retail_out, raw_isr, post_isr


def run_one_epoch(
    model, optimizer, pcgrad,
    loader: DataLoader,
    device: torch.device,
    feat_cfg: dict,
    alphas: dict,
    lambda_excl: float = LAMBDA_EXCL,
) -> dict:
    """
    One training epoch (fp32 — AMP disabled; mirrors 04D non-AMP path AND
    Leg-2's Step-6 AMP-removal fix). Fixed-alpha + PCGrad across 3 task groups
    (resid=act+home+cop, work, retail), diversity loss + exclusivity loss as
    extra terms, per-sample recency weight applied consistently (Leg-2 Step-6
    NEW code) to both the task losses (pre-PCGrad) and the extra terms.

    AMP NOTE (ported from Leg-2, 2026-06-23 fix): AMP/GradScaler intentionally
    disabled — PCGrad does multiple manual backward calls which are
    incompatible with a single scaler.scale(total).backward().
    """
    model.train()
    act_weights = None
    if "act_class_freqs" in feat_cfg:
        freqs = np.array(feat_cfg["act_class_freqs"], dtype=float)
        freqs = np.maximum(freqs, 1e-6)
        cw = 1.0 / np.sqrt(freqs)
        cw = cw / cw.mean()
        cw[WORK_ACT_0IDX] *= 5.0  # Work boost — Step-6-specific class weight,
                                   # orthogonal to the §3 task-alpha scheme,
                                   # ported unchanged from Leg-2.
        act_weights = torch.tensor(cw, dtype=torch.float32, device=device)

    home_pw   = torch.tensor([feat_cfg.get("home_pos_weight", 1.0)],
                             dtype=torch.float32, device=device)
    work_pw   = torch.tensor([feat_cfg.get("work_pos_weight", 7.26434)],
                             dtype=torch.float32, device=device)
    retail_pw = torch.tensor([feat_cfg.get("retail_pos_weight", 49.0)],
                             dtype=torch.float32, device=device)

    epoch_losses = {"act": 0.0, "home": 0.0, "work": 0.0, "retail": 0.0,
                    "cop": 0.0, "div": 0.0, "excl": 0.0, "total": 0.0}
    n_batches = 0

    for batch in loader:
        batch_dev = {}
        for k, v in batch.items():
            if isinstance(v, torch.Tensor):
                batch_dev[k] = v.to(device)
            else:
                batch_dev[k] = v

        optimizer.zero_grad()

        output = model(batch_dev)
        comp = component_losses(
            output, batch_dev,
            act_weights=act_weights,
            home_pos_weight=home_pw,
            work_pos_weight=work_pw,
            retail_pos_weight=retail_pw,
            cop_pos_weight=None,
            wght_per=None,   # Step-6 deviation: WGHT_PER survey-weighting is
                             # NOT wired here (not part of the builder prompt's
                             # deltas; Leg-2's own Step-6 also did not wire it;
                             # component_losses() falls back to uniform ones).
        )
        div  = diversity_loss(output, batch_dev)
        excl = exclusivity_loss(output, batch_dev) if lambda_excl > 0 else torch.tensor(0.0, device=device)

        rw = batch_dev.get("recency_weight", torch.ones(1, device=device))
        rw_mean = rw.mean()

        L_resid  = comp["act"] + comp["home"] + comp["cop"]
        L_work   = comp["work"]
        L_retail = comp["retail"]
        task_w = {
            "resid":  alphas["resid"]  * L_resid  * rw_mean,
            "work":   alphas["work"]   * L_work   * rw_mean,
            "retail": alphas["retail"] * L_retail * rw_mean,
        }
        extra = (LAMBDA_DIV * div + lambda_excl * excl) * rw_mean
        total_loss = sum(task_w.values()) + extra

        if pcgrad is not None:
            pcgrad.backward([task_w[t] for t in TASK_GROUPS], retain_all=True)
            extra_grads = torch.autograd.grad(extra, pcgrad.params, allow_unused=True)
            for p, eg in zip(pcgrad.params, extra_grads):
                if eg is not None:
                    p.grad = (p.grad if p.grad is not None else torch.zeros_like(p)) + eg
            # total_loss already computed above for logging — PCGrad wrote .grad directly.
        else:
            total_loss.backward()

        optimizer.step()

        epoch_losses["act"]    += float(comp["act"].detach().item())
        epoch_losses["home"]   += float(comp["home"].detach().item())
        epoch_losses["work"]   += float(comp["work"].detach().item())
        epoch_losses["retail"] += float(comp["retail"].detach().item())
        epoch_losses["cop"]    += float(comp["cop"].detach().item())
        epoch_losses["div"]    += float(div.detach().item())
        epoch_losses["excl"]   += float(excl.detach().item())
        epoch_losses["total"]  += float(total_loss.detach().item())
        n_batches += 1

    if n_batches > 0:
        for k in epoch_losses:
            epoch_losses[k] /= n_batches
    return epoch_losses


@torch.no_grad()
def validate_cycle(model, data_dict: dict, device: torch.device,
                   n_sample: int = 1000) -> dict:
    """
    Quick internal validation on a cycle's data dict (diagnostic-only path —
    kept greedy temperature=0.0 per §6 of the builder prompt). Returns mean
    JS, home_gap, work_gap, retail_gap.
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

    act_np    = data_dict["act_seq"][idx].numpy()
    home_np   = data_dict["aux_seq"][idx, :, AUX_HOME_IDX].numpy()
    work_np   = data_dict["aux_seq"][idx, :, AUX_WORK_IDX].numpy()
    retail_np = data_dict["aux_seq"][idx, :, AUX_RETAIL_IDX].numpy()

    g_act, g_home, g_work, _, _, retail_sigmoid = model.generate(
        act_t, aux_t, cond_t, cidx_t, strat_t, temperature=0.0,
        return_retail_probs=True,
    )
    g_act    = g_act.cpu().numpy()
    g_home   = g_home.cpu().numpy()
    g_work   = g_work.cpu().numpy()
    g_retail = (retail_sigmoid.cpu().numpy() > 0.5).astype(np.float32)

    ref_dist = np.bincount(act_np.flatten(), minlength=N_ACT).astype(float)
    gen_dist = np.bincount(g_act.flatten(), minlength=N_ACT).astype(float)
    js_val   = js_divergence(ref_dist, gen_dist)

    home_gap   = abs(float(g_home.mean()) - float(home_np.mean()))
    work_gap   = abs(float(g_work.mean()) - float(work_np.mean()))
    retail_gap = abs(float(g_retail.mean()) - float(retail_np.mean()))
    val_score = js_val + 0.5 * (home_gap + work_gap + retail_gap) / 3.0

    return {"val_js": js_val, "home_gap": home_gap,
            "work_gap": work_gap, "retail_gap": retail_gap,
            "val_score": val_score}


def progressive_train(
    model, model_config: dict,
    train_dicts: list,   # list of (cycle_year, data_dict, recency_weight) for training cycles
    val_dict: dict,      # data_dict for validation (the "true future" held-out cycle)
    val_cycle: int,
    save_path: str,
    feat_cfg: dict,
    device: torch.device,
    alphas: dict = None,
    max_epochs: int = 30,
    patience: int = 5,
    batch_size: int = 64,
    lr: float = 1e-4,
    use_pcgrad: bool = True,
    smoke: bool = False,
) -> dict:
    """
    Step-6 progressive training phase. Combines multiple cycle dicts with
    per-sample recency weights, runs warm-started training with early-stop
    on val_dict's val_score. Returns val metrics at best checkpoint.
    """
    if alphas is None:
        alphas = DEFAULT_ALPHAS
    if smoke:
        max_epochs = 3
        batch_size = 16

    from torch.utils.data import ConcatDataset
    datasets = []
    for (cy, d, rw) in train_dicts:
        ds = Step6Dataset(d, d["pairs"], recency_weight=rw)
        datasets.append(ds)

    combined_dataset = ConcatDataset(datasets)
    loader = DataLoader(combined_dataset, batch_size=batch_size,
                        shuffle=True, num_workers=0,
                        pin_memory=(device.type == "cuda"))

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    plateau = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.95, patience=3
    )
    pcgrad_obj = PCGrad(model.parameters()) if use_pcgrad else None

    best_val_score = float("inf")
    patience_counter = 0
    best_metrics = {}

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(max_epochs):
        t0 = time.time()
        for ds in datasets:
            ds.resample()

        epoch_loss = run_one_epoch(
            model, optimizer, pcgrad_obj,
            loader, device, feat_cfg, alphas,
        )

        val_metrics = validate_cycle(model, val_dict, device)
        plateau.step(val_metrics["val_score"])

        elapsed = time.time() - t0
        print(
            f"  epoch {epoch+1}/{max_epochs} | "
            f"loss={epoch_loss['total']:.4f} "
            f"act={epoch_loss['act']:.4f} home={epoch_loss['home']:.4f} "
            f"work={epoch_loss['work']:.4f} retail={epoch_loss['retail']:.4f} | "
            f"val_js={val_metrics['val_js']:.4f} "
            f"h_gap={val_metrics['home_gap']:.4f} "
            f"w_gap={val_metrics['work_gap']:.4f} "
            f"r_gap={val_metrics['retail_gap']:.4f} | "
            f"{elapsed:.1f}s"
        )

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
                "alphas": alphas,
                "val_js": val_metrics["val_js"],
                "home_gap": val_metrics["home_gap"],
                "work_gap": val_metrics["work_gap"],
                "retail_gap": val_metrics["retail_gap"],
                "val_score": best_val_score,
            }, save_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stop at epoch {epoch+1} (patience={patience})")
                break

    if os.path.isfile(save_path):
        ck = torch.load(save_path, map_location=device, weights_only=False)
        model.load_state_dict(ck["model_state"])

    return best_metrics


# ── DRIFT_MATRIX computation ──────────────────────────────────────────────────

def compute_drift_matrix_4split(
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
    Compute JS divergence per {14 activities x 3 DDAY_STRATA} plus AT_HOME,
    AT_WORK, AT_RETAIL [Leg-3 NEW] mean shifts per stratum (signed).
    Writes DRIFT_MATRIX_{from}{to}_4split.csv and returns the DataFrame.
    Internal diagnostic path — kept greedy (temperature=0.0) per §6.
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

    act_obs    = future_data["act_seq"][idx].numpy()
    home_obs   = future_data["aux_seq"][idx, :, AUX_HOME_IDX].numpy()
    work_obs   = future_data["aux_seq"][idx, :, AUX_WORK_IDX].numpy()
    retail_obs = future_data["aux_seq"][idx, :, AUX_RETAIL_IDX].numpy()
    strata_np = future_data["obs_strata"][idx].numpy()

    with torch.no_grad():
        g_act, g_home, g_work, _, _, retail_sigmoid = model.generate(
            act_t, aux_t, cond_t, cidx_t, str_t, temperature=0.0,
            return_retail_probs=True,
        )
    g_act    = g_act.cpu().numpy()
    g_home   = g_home.cpu().numpy()
    g_work   = g_work.cpu().numpy()
    g_retail = (retail_sigmoid.cpu().numpy() > 0.5).astype(np.float32)

    rows = []
    for s in [1, 2, 3]:
        mask = (strata_np == s)
        if mask.sum() == 0:
            continue
        ref_dist = np.bincount(act_obs[mask].flatten(), minlength=N_ACT).astype(float)
        gen_dist = np.bincount(g_act[mask].flatten(),  minlength=N_ACT).astype(float)
        js_per_act = []
        for a in range(N_ACT):
            p = np.array([ref_dist[a], ref_dist.sum() - ref_dist[a] + 1e-9])
            q = np.array([gen_dist[a], gen_dist.sum() - gen_dist[a] + 1e-9])
            js_per_act.append(js_divergence(p, q))

        at_home_drift   = float(g_home[mask].mean())   - float(home_obs[mask].mean())
        at_work_drift   = float(g_work[mask].mean())   - float(work_obs[mask].mean())
        at_retail_drift = float(g_retail[mask].mean()) - float(retail_obs[mask].mean())   # [Leg-3 NEW]
        agg_js = js_divergence(ref_dist, gen_dist)

        row = {
            "cycle_from": cycle_from,
            "cycle_to":   cycle_to,
            "stratum":    s,
            "aggregate_JS": agg_js,
            "AT_HOME_drift":   at_home_drift,
            "AT_WORK_drift":   at_work_drift,
            "AT_RETAIL_drift": at_retail_drift,   # [Leg-3 NEW]
        }
        for a in range(N_ACT):
            row[f"JS_act{a+1:02d}_{ACT_NAMES[a].replace(' ','_').replace('/','-')}"] = js_per_act[a]
        rows.append(row)

    dm = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    dm.to_csv(save_path, index=False)
    print(f"  DRIFT_MATRIX saved: {save_path}")

    # COVID TRIPLE-signal check on DRIFT_MATRIX_1522 [Leg-3: extended to retail]
    if cycle_from == 2015 and cycle_to == 2022:
        wd_row = dm[dm["stratum"] == 1]
        if len(wd_row) > 0:
            at_home_shift   = float(wd_row["AT_HOME_drift"].iloc[0])
            at_work_shift   = float(wd_row["AT_WORK_drift"].iloc[0])
            at_retail_shift = float(wd_row["AT_RETAIL_drift"].iloc[0])
            print(f"  [COVID triple-signal check] WD AT_HOME_drift={at_home_shift:+.4f}  "
                  f"AT_WORK_drift={at_work_shift:+.4f}  AT_RETAIL_drift={at_retail_shift:+.4f}")
            home_ok   = at_home_shift >= 0.05
            work_ok   = at_work_shift < 0.0
            retail_ok = at_retail_shift < 0.0
            if not home_ok:
                print("  [WARN] AT_HOME drift < +5pp — COVID AT_HOME signal may be absent.")
            if not work_ok:
                print("  [WARN] AT_WORK drift not clearly negative — COVID WFH surge not captured.")
            if not retail_ok:
                print("  [WARN] AT_RETAIL drift not clearly negative — COVID in-store collapse not captured.")
            if home_ok and work_ok and retail_ok:
                print("  [COVID triple-signal] CONFIRMED (soft blocker satisfied).")
            else:
                print("  [COVID triple-signal] NOT all 3 legs confirmed — soft blocker, investigate "
                      "(per val plan §3.5-3.7, this does not hard-fail).")

    return dm


# ── TrendEncoder4Split ────────────────────────────────────────────────────────

class TrendEncoder4Split(nn.Module):
    """
    Small Transformer that ingests three DRIFT_MATRIXes as a 3-token temporal
    sequence and emits a joint 2030 projection for AT_HOME, AT_WORK, AT_RETAIL.

    Input:  3 drift matrices (DRIFT_0510, DRIFT_1015, DRIFT_1522), each
            flattened to the quadruple [AT_HOME_drift, AT_WORK_drift,
            AT_RETAIL_drift, aggregate_JS] per stratum (input_dim = 3 strata x
            4 = 12, inferred automatically from vector length).
    Output: 2030-projected per-stratum value for all 3 channels.
            Shape: (1, n_output) where n_output = 3 strata x 3 channels = 9
            [Leg-3: was 6 = 3x2 in Leg-2 — MUST be passed explicitly].
    """

    def __init__(self, input_dim: int, d_model: int = 64, n_heads: int = 4,
                 n_layers: int = 2, n_output: int = 9):
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
        [Leg-3] Pulls the quadruple [AT_HOME_drift, AT_WORK_drift,
        AT_RETAIL_drift, aggregate_JS] per stratum instead of Leg-2's triple;
        n_output=9 (3 strata x 3 channels) passed explicitly.
        """
        vecs = []
        for path in dm_paths:
            dm = pd.read_csv(path)
            row_vals = []
            for s in [1, 2, 3]:
                sr = dm[dm["stratum"] == s]
                if len(sr) > 0:
                    row_vals += [
                        float(sr["AT_HOME_drift"].iloc[0]),
                        float(sr["AT_WORK_drift"].iloc[0]),
                        float(sr["AT_RETAIL_drift"].iloc[0]),   # [Leg-3 NEW]
                        float(sr["aggregate_JS"].iloc[0]),
                    ]
                else:
                    row_vals += [0.0, 0.0, 0.0, 0.0]
            vecs.append(row_vals)

        input_dim = len(vecs[0])
        drift_tensor = torch.tensor([vecs], dtype=torch.float32, device=device)
        # (1, 3, input_dim)

        encoder = cls(input_dim=input_dim, n_output=9).to(device)
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
        rng = np.random.default_rng(seed)
        perm = rng.permutation(N)
        n_val = max(1, int(round(val_frac * N)))
        val_idx = perm[:n_val]
        tr_idx  = perm[n_val:]
        return df.iloc[tr_idx].reset_index(drop=True), df.iloc[val_idx].reset_index(drop=True)

    strat_y = df[strat_col].values if strat_col in df.columns else np.zeros(N, dtype=int)
    counts = np.bincount(strat_y.astype(int))
    if counts.min() >= 2:
        try:
            sss = StratifiedShuffleSplit(n_splits=1, test_size=val_frac, random_state=seed)
            for tr, vl in sss.split(np.arange(N), strat_y):
                pass
            return df.iloc[tr].reset_index(drop=True), df.iloc[vl].reset_index(drop=True)
        except ValueError:
            pass

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
    Returns (model, model_config, dm_0510).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE A — BASE TRAINING ON 2005 DATA (4-split)")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    df_2005 = df[df["CYCLE_YEAR"] == 2005].copy().reset_index(drop=True)
    df_2010 = df[df["CYCLE_YEAR"] == 2010].copy().reset_index(drop=True)

    print(f"  2005 rows: {len(df_2005):,}  2010 (held-out): {len(df_2010):,}")

    df_train, df_val = robust_train_val_split(df_2005, val_frac=0.20)
    print(f"  Split: train={len(df_train)}, val={len(df_val)}")

    td_train = load_cycle_data(df_train, feat_cfg, device, 2005)
    td_val   = load_cycle_data(df_val,   feat_cfg, device, 2005)
    td_2010  = load_cycle_data(df_2010,  feat_cfg, device, 2010)

    model, model_config = build_model(feat_cfg, smoke, device, warm_start_path=None)
    print(f"  Model params: {sum(p.numel() for p in model.parameters()):,}")

    save_path = os.path.join(MODELS_DIR, "W_2005_4split.pt")
    metrics = progressive_train(
        model, model_config,
        train_dicts=[(2005, td_train, RECENCY_WEIGHTS[2005])],
        val_dict=td_val,
        val_cycle=2005,
        save_path=save_path,
        feat_cfg=feat_cfg,
        device=device,
        alphas=DEFAULT_ALPHAS,
        max_epochs=30 if not smoke else 3,
        patience=5,
        batch_size=64 if not smoke else 16,
        smoke=smoke,
    )
    print(f"  Stage A done. val_js={metrics['val_js']:.4f}  "
          f"h_gap={metrics['home_gap']:.4f}  w_gap={metrics['work_gap']:.4f}  "
          f"r_gap={metrics['retail_gap']:.4f}")

    dm_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_0510_4split.csv")
    dm_0510 = compute_drift_matrix_4split(
        model, td_2010, device,
        cycle_from=2005, cycle_to=2010,
        save_path=dm_path,
        n_sample=min(2000, len(df_2010)),
    )
    return model, model_config, dm_0510


# ── Sub-stage B ───────────────────────────────────────────────────────────────

def run_substage_b(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> tuple:
    """
    3 phases of progressive fine-tuning.
    Returns (model, model_config, dm_1015, dm_1522).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE B — PROGRESSIVE FINE-TUNING (3 PHASES, 4-split)")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── Phase 2: W_2005 -> W_2010_ft ──
    print("\n  [Phase 2] W_2005 -> W_2010_ft  (train: 2005+2010, val: 2010, TFT: 2015)")
    df_2005 = df[df["CYCLE_YEAR"] == 2005].copy().reset_index(drop=True)
    df_2010 = df[df["CYCLE_YEAR"] == 2010].copy().reset_index(drop=True)
    df_2015 = df[df["CYCLE_YEAR"] == 2015].copy().reset_index(drop=True)

    df_2010_train, df_2010_val = robust_train_val_split(df_2010, val_frac=0.20)

    td_05_tr  = load_cycle_data(df_2005,       feat_cfg, device, 2005)
    td_10_tr  = load_cycle_data(df_2010_train, feat_cfg, device, 2010)
    td_10_val = load_cycle_data(df_2010_val,   feat_cfg, device, 2010)
    td_15     = load_cycle_data(df_2015,        feat_cfg, device, 2015)

    ws_2005 = os.path.join(MODELS_DIR, "W_2005_4split.pt")
    model, model_config = build_model(feat_cfg, smoke, device, ws_2005)

    save_p2 = os.path.join(MODELS_DIR, "W_2010_ft_4split.pt")
    metrics2 = progressive_train(
        model, model_config,
        train_dicts=[
            (2005, td_05_tr, RECENCY_WEIGHTS[2005]),
            (2010, td_10_tr, RECENCY_WEIGHTS[2010]),
        ],
        val_dict=td_10_val,
        val_cycle=2010,
        save_path=save_p2,
        feat_cfg=feat_cfg,
        device=device,
        alphas=DEFAULT_ALPHAS,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    dm_1015_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1015_4split.csv")
    dm_1015 = compute_drift_matrix_4split(
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

    model3, mc3 = build_model(feat_cfg, smoke, device, save_p2)

    save_p3 = os.path.join(MODELS_DIR, "W_2015_ft_4split.pt")
    metrics3 = progressive_train(
        model3, mc3,
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
        alphas=DEFAULT_ALPHAS,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    dm_1522_path = os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1522_4split.csv")
    dm_1522 = compute_drift_matrix_4split(
        model3, td_22, device, 2015, 2022, dm_1522_path,
        n_sample=min(2000, len(df_2022)),
    )
    print(f"  Phase 3 done: val_js={metrics3['val_js']:.4f}")

    # ── Phase 4: W_2015_ft -> W_2022_ft ──
    print("\n  [Phase 4] W_2015_ft -> W_2022_ft  (train: all 4 cycles, val: 2022)")
    df_2022_train, df_2022_val = robust_train_val_split(df_2022, val_frac=0.20)

    td_22_tr  = load_cycle_data(df_2022_train, feat_cfg, device, 2022)
    td_22_val = load_cycle_data(df_2022_val,   feat_cfg, device, 2022)

    model4, mc4 = build_model(feat_cfg, smoke, device, save_p3)

    save_p4 = os.path.join(MODELS_DIR, "W_2022_ft_4split.pt")
    metrics4 = progressive_train(
        model4, mc4,
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
        alphas=DEFAULT_ALPHAS,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    print(f"  Phase 4 done: val_js={metrics4['val_js']:.4f}")

    return model4, mc4, dm_1015, dm_1522


# ── Sub-stage C ───────────────────────────────────────────────────────────────

def run_substage_c(
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
) -> tuple:
    """
    Pooled recency-weighted training + TrendEncoder4Split.
    Returns (model, trend_encoder).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE C — POOLED RECENCY-WEIGHTED TRAINING + TREND ENCODER (4-split)")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    train_dicts = []
    for cy in CYCLE_YEARS:
        dfc = df[df["CYCLE_YEAR"] == cy].copy().reset_index(drop=True)
        df_tr, _ = robust_train_val_split(dfc, val_frac=0.20)
        td_tr = load_cycle_data(df_tr, feat_cfg, device, cy)
        train_dicts.append((cy, td_tr, RECENCY_WEIGHTS[cy]))

    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    _, df_val_c = robust_train_val_split(df_2022, val_frac=0.20)
    td_val_c = load_cycle_data(df_val_c, feat_cfg, device, 2022)

    ws = os.path.join(MODELS_DIR, "W_2022_ft_4split.pt")
    model, mc = build_model(feat_cfg, smoke, device, ws if os.path.isfile(ws) else None)

    save_pooled = os.path.join(MODELS_DIR, "W_pooled_2030_4split.pt")
    metrics = progressive_train(
        model, mc,
        train_dicts=train_dicts,
        val_dict=td_val_c,
        val_cycle=2022,
        save_path=save_pooled,
        feat_cfg=feat_cfg,
        device=device,
        alphas=DEFAULT_ALPHAS,
        max_epochs=30 if not smoke else 3,
        patience=5,
        smoke=smoke,
    )
    print(f"  Stage C done: val_js={metrics['val_js']:.4f}")

    dm_paths = [
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_0510_4split.csv"),
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1015_4split.csv"),
        os.path.join(OUTPUT_DIR, "DRIFT_MATRIX_1522_4split.csv"),
    ]
    all_exist = all(os.path.isfile(p) for p in dm_paths)
    if all_exist:
        trend_encoder, drift_tensor = TrendEncoder4Split.from_drift_csvs(dm_paths, device)
        te_optimizer = torch.optim.AdamW(trend_encoder.parameters(), lr=1e-3)
        # NOTE (ported Leg-2 caveat, flagged explicitly per §5 of the builder
        # prompt — NOT a completed distribution-matching improvement): this
        # fits the encoder against an ALL-ZERO dummy target for 50 iterations.
        # Despite the runbook language implying real distribution-matching,
        # it isn't one in this code (Leg-2 limitation, ported as-is).
        trend_encoder.train()
        for _ in range(50 if not smoke else 5):
            te_optimizer.zero_grad()
            proj = trend_encoder(drift_tensor)  # (1, 9)
            target = torch.zeros(1, 9, device=device)
            loss = F.mse_loss(proj, target)
            loss.backward()
            te_optimizer.step()
        te_path = os.path.join(MODELS_DIR, "trend_encoder_2030_4split.pt")
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


# ── Anti-copy smoke gates (ported UNCHANGED from Leg-2, Fix C 2026-06-24) ────
#
# The copier bug (Job 982868) produced val_js≈0, backcast JS_home=−0.0000 and
# all 3 WFH bands IDENTICAL. These gates detect that signature early. Ported
# structurally unchanged — channel-agnostic on home/work (retail-specific
# backcast gates belong to the out-of-scope validator, per the builder prompt).

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
    targets = _BAND_WFH_SHARE
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
    ckpt_name: str = "W_pooled_2030_4split.pt",
) -> dict:
    """
    2022 backcasting gate: reconstruct 2022 diaries from a checkpoint, using
    Step-4's OWN generate_nucleus() at DELIVERABLE settings (T 0.7 + nucleus
    p=0.9 + min-dwell) — never greedy (§6 of the builder prompt: the Leg-2
    sticky-attractor artifact at T=0.0). Returns gate metrics dict (3 channels).
    """
    print("\n" + "=" * 60)
    print("SUB-STAGE D PHASE i — 2022 BACKCASTING GATE (4-split)")
    print("=" * 60)

    ws = ckpt_name if os.path.isabs(ckpt_name) else os.path.join(MODELS_DIR, ckpt_name)
    if not os.path.isfile(ws):
        print(f"  [WARN] {ws} not found — skip backcasting gate.")
        return {}
    print(f"  Backcast checkpoint: {ws}")

    model, mc = build_model(feat_cfg, smoke, device, ws)
    model.eval()

    retail_pw_val = feat_cfg.get("retail_pos_weight", 49.0)

    df_2022 = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
    if smoke:
        df_2022 = df_2022.sample(frac=0.05, random_state=42).reset_index(drop=True)

    tensors = build_tensors_from_df(df_2022, feat_cfg, device)
    N = len(df_2022)
    batch_sz = 256
    gen_acts, gen_homes, gen_works, gen_retails = [], [], [], []

    for start in range(0, N, batch_sz):
        sl = slice(start, start + batch_sz)
        g_act, g_home, g_work, g_retail, _raw_isr, _post_isr = decode_deliverable(
            model,
            tensors["act_seq"][sl],
            tensors["aux_seq"][sl],
            tensors["cond_vec"][sl],
            tensors["cycle_idx"][sl],
            tensors["obs_strata"][sl],
            retail_pos_weight=retail_pw_val,
        )
        gen_acts.append(g_act)
        gen_homes.append(g_home)
        gen_works.append(g_work)
        gen_retails.append(g_retail)

    gen_act    = np.concatenate(gen_acts, axis=0)
    gen_home   = np.concatenate(gen_homes, axis=0)
    gen_work   = np.concatenate(gen_works, axis=0)
    gen_retail = np.concatenate(gen_retails, axis=0)

    obs_home   = df_2022[[f"hom30_{i:03d}" for i in range(1, 49)]].values.astype(float)
    obs_work   = df_2022[[f"wrk30_{i:03d}" for i in range(1, 49)]].values.astype(float)
    obs_retail = df_2022[[f"ret30_{i:03d}" for i in range(1, 49)]].values.astype(float)   # [Leg-3 NEW]
    obs_act    = df_2022[[f"act30_{i:03d}" for i in range(1, 49)]].values.astype(int) - 1

    hom_cols = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols = [f"wrk30_{i:03d}" for i in range(1, 49)]
    ret_cols = [f"ret30_{i:03d}" for i in range(1, 49)]
    act_cols_out = [f"act30_{i:03d}" for i in range(1, 49)]

    out_df = pd.DataFrame(gen_act + 1, columns=act_cols_out)
    for i, c in enumerate(hom_cols):
        out_df[c] = gen_home[:, i]
    for i, c in enumerate(wrk_cols):
        out_df[c] = gen_work[:, i]
    for i, c in enumerate(ret_cols):
        out_df[c] = gen_retail[:, i]
    out_df["CYCLE_YEAR"]   = 2022
    out_df["IS_SYNTHETIC"] = 1

    _stem = os.path.splitext(os.path.basename(ckpt_name))[0]
    _tag = "" if _stem == "W_pooled_2030_4split" else "_" + _stem
    out_path = os.path.join(OUTPUT_DIR, f"reconstructed_2022_diaries_4split{_tag}.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"  Backcast CSV saved: {out_path}  rows={len(out_df):,}")

    gate_metrics = {}
    strata_np = df_2022["DDAY_STRATA"].values

    # Profile metric (shape-JS + level-MAD) — never raw flattened-binary JS
    # (Leg-2 saturation artifact; retail is the worst case per the val plan).
    print("  Gate table (per stratum) — marginal per-slot occupancy profiles:")
    print(f"  {'Stratum':<8} {'JSact':>8} {'JShome':>8} {'JSwork':>8} {'JSret':>8} "
          f"{'MADhome':>8} {'MADwork':>8} {'MADret':>8} "
          f"{'dHome':>8} {'dWork':>8} {'dRet':>8} {'PASS?'}")
    for s in [1, 2, 3]:
        m = (strata_np == s)
        if m.sum() == 0:
            continue
        obs_dist = np.bincount(obs_act[m].flatten(), minlength=N_ACT).astype(float)
        gen_dist = np.bincount(gen_act[m].flatten(), minlength=N_ACT).astype(float)
        js_act = js_divergence(obs_dist, gen_dist)

        obs_h_prof = obs_home[m].mean(axis=0);   gen_h_prof = gen_home[m].mean(axis=0)
        obs_w_prof = obs_work[m].mean(axis=0);   gen_w_prof = gen_work[m].mean(axis=0)
        obs_r_prof = obs_retail[m].mean(axis=0); gen_r_prof = gen_retail[m].mean(axis=0)

        js_h = js_divergence(obs_h_prof, gen_h_prof)
        js_w = js_divergence(obs_w_prof, gen_w_prof)
        js_r = js_divergence(obs_r_prof, gen_r_prof)
        mad_h = float(np.abs(obs_h_prof - gen_h_prof).mean())
        mad_w = float(np.abs(obs_w_prof - gen_w_prof).mean())
        mad_r = float(np.abs(obs_r_prof - gen_r_prof).mean())

        dh = abs(gen_home[m].mean()   - obs_home[m].mean())
        dw = abs(gen_work[m].mean()   - obs_work[m].mean())
        dr = abs(gen_retail[m].mean() - obs_retail[m].mean())

        ok = (mad_h < 0.10) and (mad_w < 0.10) and (mad_r < 0.10)
        print(f"  {s:<8} {js_act:>8.4f} {js_h:>8.4f} {js_w:>8.4f} {js_r:>8.4f} "
              f"{mad_h:>8.4f} {mad_w:>8.4f} {mad_r:>8.4f} "
              f"{dh:>8.4f} {dw:>8.4f} {dr:>8.4f} {'PASS' if ok else 'FAIL'}")
        gate_metrics[s] = {"js_act": js_act, "js_home": js_h, "js_work": js_w, "js_retail": js_r,
                           "mad_home": mad_h, "mad_work": mad_w, "mad_retail": mad_r,
                           "dHome": dh, "dWork": dw, "dRetail": dr}

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

    print("\n  [D1 Anti-copy gates]")
    check_anticopy_gate1_slot_disagreement(obs_act, gen_act, label="D1-backcast")
    if 1 in gate_metrics:
        check_anticopy_gate2_js(gate_metrics[1]["js_home"], gate_metrics[1]["js_work"], label="D1-stratum1")
    if 2 in gate_metrics:
        check_anticopy_gate2_js(gate_metrics[2]["js_home"], gate_metrics[2]["js_work"], label="D1-stratum2")
    print("  [D1 anti-copy gates] PASS\n")

    return gate_metrics


# ── Sub-stage D Phase ii: POST-HOC DAY-TYPE REWEIGHT (ported from Leg-2) ─────
#
# FIX carried forward: TELEWORK conditioning is NOT a learnable lever (Leg-2
# control 987027). Office WFH bands ship via post-hoc day-type reweight, NOT
# model-side conditioning. The retail lever (out of scope this session) is
# ALSO post-hoc by design (runbook §6B/6G) but applied by a LATER script
# (3rdJ_06_retail_lever_4split.py, not built here) — D2 here emits the RAW
# model-forecast retail marginal with no lever multiplier.

_BAND_WFH_SHARE = {
    "conservative": 0.175,
    "hybrid":       0.300,
    "fullyhybrid":  0.400,
}
_WFH_DAY_THRESH = 0.50


def _classify_wfh_day(gen_home: np.ndarray) -> np.ndarray:
    h_biz = gen_home[:, BIZ_SLOTS_0IDX]
    return (h_biz.mean(axis=1) >= _WFH_DAY_THRESH)


def _run_base_forecast_2030(
    df_scen: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    model,
) -> tuple:
    """
    Run a single deliverable-settings decode pass on df_scen (CYCLE_YEAR set
    to 2022 for embedding — no 2030 embedding exists). Uses decode_deliverable
    (generate_nucleus + calibration + exclusivity projection + activity
    override + min-dwell), matching D1's decode chain exactly.
    Returns (gen_act, gen_home, gen_work, gen_retail) numpy arrays (N, 48).
    """
    df_inf = df_scen.copy()
    df_inf["CYCLE_YEAR"] = 2022

    tensors = build_tensors_from_df(df_inf, feat_cfg, device)
    N = len(df_inf)
    batch_sz = 256
    retail_pw_val = feat_cfg.get("retail_pos_weight", 49.0)
    gen_acts, gen_homes, gen_works, gen_retails = [], [], [], []

    for start in range(0, N, batch_sz):
        sl = slice(start, start + batch_sz)
        g_act, g_home, g_work, g_retail, _raw_isr, _post_isr = decode_deliverable(
            model,
            tensors["act_seq"][sl],
            tensors["aux_seq"][sl],
            tensors["cond_vec"][sl],
            tensors["cycle_idx"][sl],
            tensors["obs_strata"][sl],
            retail_pos_weight=retail_pw_val,
        )
        gen_acts.append(g_act)
        gen_homes.append(g_home)
        gen_works.append(g_work)
        gen_retails.append(g_retail)

    gen_act    = np.concatenate(gen_acts, axis=0)
    gen_home   = np.concatenate(gen_homes, axis=0)
    gen_work   = np.concatenate(gen_works, axis=0)
    gen_retail = np.concatenate(gen_retails, axis=0)
    return gen_act, gen_home, gen_work, gen_retail


def _posthoc_reweight(
    df_scen: pd.DataFrame,
    base_gen_act: np.ndarray,
    base_gen_home: np.ndarray,
    base_gen_work: np.ndarray,
    base_gen_retail: np.ndarray,
    target_wfh_share: float,
    band: str,
    rng_seed: int = 42,
) -> tuple:
    """
    Post-hoc day-type reweight: assemble a cohort where the WFH-day share
    among employed (LFTAG==1) rows == target_wfh_share (±3pp). Extended to
    carry the retail array through the same donor-swap [Leg-3 NEW] — the
    donor's whole diary (act/home/work/retail) moves together, so retail
    marginal is untouched by the WFH lever by construction (val plan §5.27:
    "no retail-WFH cross-contamination").
    Returns (out_act, out_home, out_work, out_retail) numpy arrays (N, 48).
    """
    N = len(df_scen)
    is_employed = (df_scen["LFTAG"].values == 1) if "LFTAG" in df_scen.columns else np.ones(N, dtype=bool)
    is_wfh_day = _classify_wfh_day(base_gen_home)

    emp_idx = np.where(is_employed)[0]
    n_emp = len(emp_idx)
    n_wfh_target = int(round(n_emp * target_wfh_share))
    n_off_target = n_emp - n_wfh_target

    wfh_pool = emp_idx[is_wfh_day[emp_idx]]
    off_pool  = emp_idx[~is_wfh_day[emp_idx]]

    current_wfh_share = len(wfh_pool) / max(n_emp, 1)
    print(f"  [{band}] base WFH-day share={current_wfh_share:.3f}  "
          f"target={target_wfh_share:.3f}  "
          f"WFH pool={len(wfh_pool)}  Office pool={len(off_pool)}")

    if len(wfh_pool) == 0:
        print(f"  [{band}] WARNING: WFH-day pool is empty — band cannot be formed; "
              f"returning base forecast unchanged.")
        return base_gen_act.copy(), base_gen_home.copy(), base_gen_work.copy(), base_gen_retail.copy()
    if len(off_pool) == 0 and n_off_target > 0:
        print(f"  [{band}] WARNING: office-day pool is empty — band cannot be formed; "
              f"returning base forecast unchanged.")
        return base_gen_act.copy(), base_gen_home.copy(), base_gen_work.copy(), base_gen_retail.copy()

    if len(wfh_pool) < n_wfh_target:
        print(f"  [{band}] WARNING: WFH-day pool ({len(wfh_pool)}) < target count "
              f"({n_wfh_target}) — resampling with replacement for WFH rows; "
              f"diversity limited. This is a model finding, not fudged.")
    if len(off_pool) < n_off_target:
        print(f"  [{band}] WARNING: office-day pool ({len(off_pool)}) < target count "
              f"({n_off_target}) — resampling with replacement for office rows.")

    rng = np.random.default_rng(rng_seed)
    agegrp_arr = df_scen["AGEGRP"].fillna(-1).astype(int).values if "AGEGRP" in df_scen.columns else np.full(N, -1, dtype=int)

    def _draw_agegrp_stratified(pool: np.ndarray, n_draw: int) -> np.ndarray:
        if n_draw == 0:
            return np.array([], dtype=int)
        pool_agegrp = agegrp_arr[pool]
        unique_groups = np.unique(pool_agegrp)
        group_quota = {}
        for g in unique_groups:
            g_count = int((pool_agegrp == g).sum())
            group_quota[g] = max(1, round(n_draw * g_count / len(pool)))
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
        if len(result) < n_draw:
            shortfall = n_draw - len(result)
            result = np.concatenate([result, rng.choice(pool, size=shortfall, replace=True)])
        return result[:n_draw]

    selected_wfh = _draw_agegrp_stratified(wfh_pool, n_wfh_target)
    selected_off = _draw_agegrp_stratified(off_pool, n_off_target)
    selected_emp = np.concatenate([selected_wfh, selected_off])

    out_act    = base_gen_act.copy()
    out_home   = base_gen_home.copy()
    out_work   = base_gen_work.copy()
    out_retail = base_gen_retail.copy()   # [Leg-3 NEW]

    rng2 = np.random.default_rng(rng_seed + 1)
    rng2.shuffle(selected_emp)
    for slot, orig_i in enumerate(emp_idx):
        donor_i = int(selected_emp[slot % len(selected_emp)])
        out_act[orig_i]    = base_gen_act[donor_i]
        out_home[orig_i]   = base_gen_home[donor_i]
        out_work[orig_i]   = base_gen_work[donor_i]
        out_retail[orig_i] = base_gen_retail[donor_i]   # [Leg-3 NEW]

    is_wfh_day_out = _classify_wfh_day(out_home)
    realised_share = float(is_wfh_day_out[emp_idx].mean()) if n_emp > 0 else float("nan")
    delta_pp = abs(realised_share - target_wfh_share) * 100
    gate_ok = delta_pp <= 3.0
    print(f"  [{band}] realised WFH-day share={realised_share:.4f}  "
          f"delta={delta_pp:.2f}pp  {'PASS (<=3pp)' if gate_ok else 'GATE FAIL (>3pp)'}")
    if not gate_ok:
        print(f"  [GATE FAIL] Band {band}: realised WFH-day share {realised_share:.4f} "
              f"vs target {target_wfh_share:.4f}, delta {delta_pp:.2f}pp > 3pp threshold.")

    return out_act, out_home, out_work, out_retail


def run_substage_d_phase_ii(
    band: str,
    df: pd.DataFrame,
    feat_cfg: dict,
    device: torch.device,
    smoke: bool = False,
    _base_cache: dict = None,
) -> pd.DataFrame:
    """
    2030 forward forecast for one office WFH band — POST-HOC DAY-TYPE
    REWEIGHT (ported from Leg-2). Retail channel rides along unmodified (no
    lever applied here — the lever is a separate downstream script per the
    runbook). Returns diary DataFrame with BAND column.
    """
    assert band in _BAND_WFH_SHARE, f"Unknown band: {band}"
    target_wfh_share = _BAND_WFH_SHARE[band]

    print(f"\n  [Phase ii — {band}] post-hoc reweight target WFH-day share={target_wfh_share:.3f}")

    scenario_path = os.path.join(OUTPUT_DIR, "scenario_2030_features_4split.csv")
    if not os.path.isfile(scenario_path):
        print(f"  [WARN] scenario_2030_features_4split.csv not found; "
              f"falling back to 2022 cohort.")
        df_scen = df[df["CYCLE_YEAR"] == 2022].copy().reset_index(drop=True)
        df_scen["CYCLE_YEAR"] = 2030
        df_scen["SCENARIO"]   = "M1_2030"
    else:
        df_scen = pd.read_csv(scenario_path, low_memory=False)

    if smoke:
        df_scen = df_scen.sample(frac=0.05, random_state=42).reset_index(drop=True)

    if _base_cache is not None and "gen_act" in _base_cache:
        gen_act_base    = _base_cache["gen_act"]
        gen_home_base   = _base_cache["gen_home"]
        gen_work_base   = _base_cache["gen_work"]
        gen_retail_base = _base_cache["gen_retail"]
        df_scen         = _base_cache["df_scen"]
        print(f"  [{band}] Using cached base forecast ({len(df_scen):,} rows).")
    else:
        ws = os.path.join(MODELS_DIR, "W_pooled_2030_4split.pt")
        if not os.path.isfile(ws):
            print(f"  [WARN] {ws} not found; using W_2022_ft if available.")
            ws = os.path.join(MODELS_DIR, "W_2022_ft_4split.pt")

        model, mc = build_model(feat_cfg, smoke, device, ws if os.path.isfile(ws) else None)
        model.eval()
        print(f"  Generating base 2030 forecast ({len(df_scen):,} rows) …")
        gen_act_base, gen_home_base, gen_work_base, gen_retail_base = _run_base_forecast_2030(
            df_scen, feat_cfg, device, model
        )
        if _base_cache is not None:
            _base_cache["gen_act"]    = gen_act_base
            _base_cache["gen_home"]   = gen_home_base
            _base_cache["gen_work"]   = gen_work_base
            _base_cache["gen_retail"] = gen_retail_base
            _base_cache["df_scen"]    = df_scen

    N = len(df_scen)

    gen_act, gen_home, gen_work, gen_retail = _posthoc_reweight(
        df_scen, gen_act_base, gen_home_base, gen_work_base, gen_retail_base,
        target_wfh_share=target_wfh_share,
        band=band,
        rng_seed={"conservative": 42, "hybrid": 43, "fullyhybrid": 44}[band],
    )

    # ── 6H: 3-way mutual-exclusion HARD ASSERTION (belt-and-braces final pass;
    # the decode chain already guarantees ISR==0 by construction via
    # exclusivity_projection + apply_activity_override_3ch — this verifies it
    # held through the donor-swap reweight, never silently warns). ──────────
    mutual_exclusion_resolve(gen_home, gen_work, gen_retail, label=f"D2-{band}")

    act_cols_out = [f"act30_{i:03d}" for i in range(1, 49)]
    hom_cols     = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk_cols     = [f"wrk30_{i:03d}" for i in range(1, 49)]
    ret_cols     = [f"ret30_{i:03d}" for i in range(1, 49)]   # [Leg-3 NEW]

    out_df = pd.DataFrame(gen_act + 1, columns=act_cols_out)
    for i, c in enumerate(hom_cols):
        out_df[c] = gen_home[:, i]
    for i, c in enumerate(wrk_cols):
        out_df[c] = gen_work[:, i]
    for i, c in enumerate(ret_cols):
        out_df[c] = gen_retail[:, i]

    out_df["CYCLE_YEAR"]   = 2030
    out_df["BAND"]         = band
    out_df["IS_SYNTHETIC"] = 1
    out_df["DDAY_STRATA"]  = df_scen["DDAY_STRATA"].values

    for col in ["AGEGRP", "SEX", "LFTAG", "NOCS", "NAICS", "TELEWORK",
                "TELEWORK_KNOWN", "PR", "CMA", "DDAY_STRATA"]:
        if col in df_scen.columns:
            out_df[col] = df_scen[col].values

    is_employed = (df_scen["LFTAG"].values == 1) if "LFTAG" in df_scen.columns else np.ones(N, dtype=bool)
    emp_m = is_employed
    wd_mask = (df_scen["DDAY_STRATA"].values == 1)

    h_biz_out = gen_home[emp_m, :][:, BIZ_SLOTS_0IDX]
    a_biz_out = gen_act[emp_m, :][:, BIZ_SLOTS_0IDX]
    wfh_rate = float(((h_biz_out == 1) | (a_biz_out == 0)).mean()) if emp_m.sum() > 0 else float("nan")

    wd_at_home   = float(gen_home[wd_mask].mean())   if wd_mask.sum() > 0 else float("nan")
    wd_at_work   = float(gen_work[wd_mask].mean())   if wd_mask.sum() > 0 else float("nan")
    wd_at_retail = float(gen_retail[wd_mask].mean()) if wd_mask.sum() > 0 else float("nan")

    print(f"  {band}: rows={N:,}  WD_AT_HOME={wd_at_home:.4f}  "
          f"WD_AT_WORK={wd_at_work:.4f}  WD_AT_RETAIL={wd_at_retail:.4f}  WFH_RATE={wfh_rate:.4f}")

    return out_df


# ── 6H: 3-way Mutual-exclusion HARD ASSERTION (never warn) ───────────────────

def mutual_exclusion_resolve(
    gen_home: np.ndarray,
    gen_work: np.ndarray,
    gen_retail: np.ndarray,
    label: str = "",
) -> None:
    """
    [Leg-3, val plan §6H] Hard assertion: (hom∧wrk) = (hom∧ret) = (wrk∧ret) = 0
    across every slot — abort, never warn (the Leg-2 2026-07-17 mutex-bug
    lesson: a calibration-stage smoother re-raised hom30 on wrk30==1 slots
    with no guard, and 4,280 physically-impossible cells reached Step 7/8/9
    undetected). The decode chain (exclusivity_projection +
    apply_activity_override_3ch) already guarantees this by construction —
    this call VERIFIES it held, it does not fix anything.
    """
    hw = int(((gen_home == 1) & (gen_work == 1)).sum())
    hr = int(((gen_home == 1) & (gen_retail == 1)).sum())
    wr = int(((gen_work == 1) & (gen_retail == 1)).sum())
    total = hw + hr + wr
    if total > 0:
        raise AssertionError(
            f"[6H MUTEX GUARD FAIL] {label}: {total} mutex violations found "
            f"(home&work={hw}, home&retail={hr}, work&retail={wr}) — abort per "
            f"the val plan's hard-assertion discipline (never warn)."
        )
    print(f"  [6H] Mutual-exclusion guard {label}: 0 violations (clean, 3-way)")


def call_mindwell(in_csv: str, out_csv: str) -> None:
    """
    Call 3rdJ_04M_mindwell_4split.py as subprocess for min-dwell smoothing.
    Pure CSV-in / CSV-out post-processor (no import side-effects).
    """
    mindwell_script = os.path.join(STEP4_DIR, "3rdJ_04M_mindwell_4split.py")
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
        data_path = _default_raw_pool_path()

    device = (torch.device("cuda") if torch.cuda.is_available()
              else torch.device("cpu"))
    print(f"Device: {device}")

    stage = args.stage

    if stage in ("audit",):
        run_input_audit(data_path)
        return

    print(f"Loading: {data_path}")
    df = pd.read_csv(data_path, low_memory=False)
    if args.smoke:
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
        ckpt = getattr(args, "backcast_ckpt", "W_pooled_2030_4split.pt")
        run_substage_d_phase_i(df, feat_cfg, device, smoke=args.smoke,
                               ckpt_name=ckpt)

    if stage in ("D2", "all"):
        band_arg = args.band if args.band else None
        bands = [band_arg] if band_arg else ["conservative", "hybrid", "fullyhybrid"]

        _d2_cache: dict = {}
        all_diaries = []
        for band in bands:
            diary_df = run_substage_d_phase_ii(
                band, df, feat_cfg, device, smoke=args.smoke,
                _base_cache=_d2_cache,
            )
            all_diaries.append(diary_df)

        combined = pd.concat(all_diaries, ignore_index=True)
        raw_path = os.path.join(OUTPUT_DIR, "2030_synthetic_diaries_4split_raw.csv")
        combined.to_csv(raw_path, index=False)
        print(f"  Combined 2030 diaries: {len(combined):,} rows -> {raw_path}")

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
                        print("  [Gate 4 D2] SKIPPED in smoke mode (tiny sample, no scenario CSV)")
                    else:
                        check_anticopy_gate4_bands(wfh_day_shares, label="D2")

        for band in bands:
            band_raw = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_raw.csv")
            band_out = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_mindwell.csv")
            sub = combined[combined["BAND"] == band]
            sub.to_csv(band_raw, index=False)
            call_mindwell(band_raw, band_out)

        final_parts = []
        for band in bands:
            mpath = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_mindwell.csv")
            rpath = os.path.join(OUTPUT_DIR, f"2030_diaries_{band}_raw.csv")
            p = mpath if os.path.isfile(mpath) else rpath
            if os.path.isfile(p):
                final_parts.append(pd.read_csv(p, low_memory=False))
        if final_parts:
            final = pd.concat(final_parts, ignore_index=True)
            final_path = os.path.join(OUTPUT_DIR, "2030_synthetic_diaries_4split.csv")
            final.to_csv(final_path, index=False)
            print(f"  Final deliverable: {final_path}  rows={len(final):,}")


# ── Argparse ──────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Step 6 Longitudinal Forecasting (4-split three-channel, Leg-3 Track A)"
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
                   help="Path to the raw pool augmented_diaries.csv "
                        "(default: seed_3_g3fix, falls back to seed_3 then "
                        "flat outputs_step4/augmented_diaries.csv)")
    p.add_argument("--backcast_ckpt", default="W_pooled_2030_4split.pt",
                   help="Checkpoint (in models/) used by the D1 backcast gate. "
                        "Default = W_pooled_2030 (the deliverable checkpoint). "
                        "Use W_2022_ft_4split.pt for a supplementary 2022-specialised "
                        "backcast (writes a tagged CSV, does not clobber canonical).")
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()

    if args.stage == "audit":
        feat_cfg = load_feature_config()
        data_path = args.data if args.data else _default_raw_pool_path()
        run_input_audit(data_path)
    else:
        run_all(args)
