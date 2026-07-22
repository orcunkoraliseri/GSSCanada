# -*- coding: utf-8 -*-
"""
3rdJ_04A_assembly_4split.py — Step 4A (Leg-3, four-channel split): Training
Dataset Assembly with AT_RETAIL as a third binary occupancy channel.

Ported from Leg-2's 3rdJ_04A_assembly_2split.py (2-channel: AT_HOME + AT_WORK).
Leg-2 file is READ-ONLY / template only — not imported, not modified.

Merges hetus_30min.csv + copresence_30min.csv + work_30min.csv + retail_30min.csv
(retail_30min.csv is Leg-3 NEW, Step 3), encodes the demographic conditioning
vector (one-hot + continuous + binary; UNCHANGED from Leg-2 per the runbook —
no retail-specific conditioning is added), recodes co-presence from GSS coding
(1=Yes, 2=No) to binary (1/0) with a per-slot availability mask, builds the
AT_WORK and AT_RETAIL tracks + availability masks, builds the 48-slot x
12-feature aux token sequences, then splits respondents 70/15/15 stratified by
CYCLE_YEAR x DDAY_STRATA (seed=42).

LEG-3 DELTA A (per 3rdJ_04_augmentationGSS_4split.md, FROZEN):
  1. Read retail_30min.csv (RETL30_001..048) alongside work_30min.csv.
     aux_seq grows from width 11 to width 12:
         [AT_HOME(1) | AT_WORK(1) | AT_RETAIL(1) | 9 co-presence]
     AT_HOME is column index 0, AT_WORK is index 1, AT_RETAIL is index 2
     (inserted as the 3rd plane, BEFORE the 9 co-presence planes — CONTRACT
     ordering), co-presence indices 3..11.
  2. Build retail_avail (n,48) bool mask mirroring work_avail (True where the
     RETL30 slot is non-NaN in the source file).
  3. Conditioning vector (cond_vec) is UNCHANGED from Leg-2 — WORK_SCHEDULE /
     NAICS / TELEWORK stay as-is; no new retail conditioning columns.
  4. Emit retail_pos_weight = (1-freq)/freq for AT_RETAIL (computed on train
     split, masked by retail_avail), added to feature config, mirroring
     work_pos_weight.
  5. All paths repointed to Leg3_4-split/Step4_docs/outputs_step4/ and to the
     Leg-3 Step-3 inputs (Step3_docs/outputs_step3/).

Usage:
    py -3 -X utf8 3rdJ_04A_assembly_4split.py           # full dataset
    py -3 -X utf8 3rdJ_04A_assembly_4split.py --sample  # ~2% stratified sample
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler

# Windows console (cp1252) chokes on unicode in print statements; on Linux/cluster
# this is a no-op. Wrap in try/except so script still runs under environments that
# don't expose reconfigure.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Platform-detection path block (mirrors Leg-3 Step3 3rdJ_03_mergingGSS_4split.py) ──
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

INPUT_DIR = os.path.join(_LEG3_BASE, "Step3_docs", "outputs_step3")
OUTPUT_DIR = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")

# ── Co-presence column order: colleagues is index 8 (masked for 2005/2010) ──
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
N_SLOTS = 48
N_COP = 9
N_AUX = 12  # [AT_HOME | AT_WORK | AT_RETAIL | 9 co-presence]  [Leg-3 delta]
N_ACT_CLASSES = 14

# CYCLE_YEAR -> integer index for learned embedding in model
CYCLE_MAP = {2005: 0, 2010: 1, 2015: 2, 2022: 3}

# One-hot categorical columns in the conditioning vector (Leg-2 identical)
CAT_COLS = [
    "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA",
    "KOL", "LFTAG", "HRSWRK", "NOCS", "COW", "DDAY_STRATA",
    "ATTSCH", "POWST", "MODE",
]
CONT_COLS = ["TOTINC"]                          # standardized continuous
BIN_COLS = ["COLLECT_MODE", "TOTINC_SOURCE"]    # binary flags

# Leg-2 conditioning columns (UNCHANGED in Leg-3 — no retail-specific cond, per
# the runbook: "retail presence is population-behavioural, not occupation-gated")
WORK_SCHEDULE_CATS = list(range(1, 10))  # categories 1..9, NaN -> all-zero
NAICS_COL = "NAICS"
WORK_SCHEDULE_COL = "WORK_SCHEDULE"
TELEWORK_COL = "TELEWORK"


# ── Helpers ─────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", action="store_true",
                   help="Stratified ~2%% subsample for local smoke testing "
                        "(writes the SAME artifact names into outputs_step4/)")
    p.add_argument("--sample_frac", type=float, default=0.02,
                   help="Sample fraction (default 0.02 = 2%%)")
    p.add_argument("--sample_min", type=int, default=400,
                   help="Minimum total sample rows (default 400)")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_data(input_dir: str):
    """Load the four Leg-3 input files (always full files; sampling happens later)."""
    hetus = pd.read_csv(os.path.join(input_dir, "hetus_30min.csv"), low_memory=False)
    cop = pd.read_csv(os.path.join(input_dir, "copresence_30min.csv"), low_memory=False)
    work = pd.read_csv(os.path.join(input_dir, "work_30min.csv"), low_memory=False)
    retail = pd.read_csv(os.path.join(input_dir, "retail_30min.csv"), low_memory=False)
    return hetus, cop, work, retail


def merge_inputs(hetus: pd.DataFrame, cop: pd.DataFrame, work: pd.DataFrame,
                  retail: pd.DataFrame):
    """
    Positional concat: occID is NOT unique within a file (same PUMFID across
    cycles). The unique row key is (occID, CYCLE_YEAR). All four files share the
    same row order (verified by element-wise occID check).
    """
    assert len(hetus) == len(cop), f"Row mismatch: hetus={len(hetus)}, cop={len(cop)}"
    assert len(hetus) == len(work), f"Row mismatch: hetus={len(hetus)}, work={len(work)}"
    assert len(hetus) == len(retail), f"Row mismatch: hetus={len(hetus)}, retail={len(retail)}"
    assert (hetus["occID"].values == cop["occID"].values).all(), \
        "occID order mismatch between hetus_30min and copresence_30min"
    assert (hetus["occID"].values == work["occID"].values).all(), \
        "occID order mismatch between hetus_30min and work_30min"
    assert (hetus["occID"].values == retail["occID"].values).all(), \
        "occID order mismatch between hetus_30min and retail_30min"

    cop_slot_cols = [f"{ch}30_{s:03d}" for ch in COP_COLS for s in range(1, N_SLOTS + 1)]
    missing = [c for c in cop_slot_cols if c not in cop.columns]
    assert not missing, (
        f"copresence_30min.csv missing {len(missing)} of {len(cop_slot_cols)} "
        f"expected slot columns (e.g. {missing[:3]}). Regenerate via Step 3."
    )

    work_slot_cols = [f"WORK30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    missing_w = [c for c in work_slot_cols if c not in work.columns]
    assert not missing_w, (
        f"work_30min.csv missing {len(missing_w)} of {len(work_slot_cols)} "
        f"expected WORK30 slot columns (e.g. {missing_w[:3]}). Regenerate via Step 3 Phase J."
    )

    retail_slot_cols = [f"RETL30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    missing_r = [c for c in retail_slot_cols if c not in retail.columns]
    assert not missing_r, (
        f"retail_30min.csv missing {len(missing_r)} of {len(retail_slot_cols)} "
        f"expected RETL30 slot columns (e.g. {missing_r[:3]}). Regenerate via Step 3."
    )

    df = pd.concat(
        [hetus.reset_index(drop=True),
         cop[cop_slot_cols].reset_index(drop=True),
         work[work_slot_cols].reset_index(drop=True),
         retail[retail_slot_cols].reset_index(drop=True)],
        axis=1,
    )
    return df, cop_slot_cols, work_slot_cols, retail_slot_cols


def build_cop_avail_and_recode(df: pd.DataFrame):
    """
    GSS coding: 1=present, 2=absent, NaN=missing.
    Recode to binary 0/1; build boolean availability mask.

    Returns:
        cop_bin   (n, 48, 9) float32 — recoded binary values (NaN -> 0)
        cop_avail (n, 48, 9) bool    — True where source was non-NaN
    """
    n = len(df)
    cop_arr = np.empty((n, N_SLOTS, N_COP), dtype=np.float64)
    for col_idx, col_name in enumerate(COP_COLS):
        cols = [f"{col_name}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
        cop_arr[:, :, col_idx] = df[cols].values
    cop_avail = ~np.isnan(cop_arr)
    cop_bin = np.where(cop_avail, (cop_arr == 1).astype(np.float32), 0.0)
    return cop_bin.astype(np.float32), cop_avail.astype(bool)


def build_work_track(df: pd.DataFrame):
    """
    Build the AT_WORK track + availability mask from WORK30_*.

    WORK30 is binary 1/0, may contain NaN (slot not derivable).

    Returns:
        work_bin   (n, 48) float32 — binary AT_WORK values (NaN -> 0)
        work_avail (n, 48) bool    — True where WORK30 slot non-NaN
    """
    work_cols = [f"WORK30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    work_arr = df[work_cols].values.astype(np.float64)
    work_avail = ~np.isnan(work_arr)
    work_bin = np.where(work_avail, (work_arr == 1).astype(np.float32), 0.0)
    return work_bin.astype(np.float32), work_avail.astype(bool)


def build_retail_track(df: pd.DataFrame):
    """
    [Leg-3 NEW] Build the AT_RETAIL track + availability mask from RETL30_*,
    mirroring build_work_track exactly.

    RETL30 is binary 1/0, may contain NaN (slot not derivable).

    Returns:
        retail_bin   (n, 48) float32 — binary AT_RETAIL values (NaN -> 0)
        retail_avail (n, 48) bool    — True where RETL30 slot non-NaN
    """
    retail_cols = [f"RETL30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    retail_arr = df[retail_cols].values.astype(np.float64)
    retail_avail = ~np.isnan(retail_arr)
    retail_bin = np.where(retail_avail, (retail_arr == 1).astype(np.float32), 0.0)
    return retail_bin.astype(np.float32), retail_avail.astype(bool)


def encode_demographics(df: pd.DataFrame, encoders=None, scaler=None):
    """
    Build the pre-computed conditioning vector (all features except CYCLE_YEAR,
    which gets a learned embedding in the model). UNCHANGED from Leg-2 (per the
    runbook: no retail-specific conditioning is added — retail presence is
    population-behavioural, not occupation-gated).

    Leg-2 additions appended AFTER the Leg-1 block (so Leg-1 indices unchanged):
      - WORK_SCHEDULE one-hot (cats 1..9, NaN -> all-zero)
      - NAICS one-hot industry bucket (NaN -> all-zero)
      - TELEWORK binary (NaN -> 0) + telework_known indicator bit

    Returns:
        cond_vec     (n, d_cond) float32
        cycle_idx    (n,)        int64
        feat_config  dict — encoding metadata for feature_config.json
        encoders     dict — category->index maps per column
        scaler       fitted StandardScaler for TOTINC
    """
    n = len(df)
    parts = []
    feat_config = {}

    if encoders is None:
        encoders = {}

    # ── One-hot categorical columns (Leg-1/Leg-2 identical) ─────────────
    for col in CAT_COLS:
        if col not in df.columns:
            print(f"  WARNING: {col} not found in data, skipping")
            continue
        vals = df[col].fillna(-1).astype(int).values
        if col not in encoders:
            cats = sorted(np.unique(vals))
            encoders[col] = {int(v): i for i, v in enumerate(cats)}
        cat_map = encoders[col]
        n_cats = len(cat_map)
        oh = np.zeros((n, n_cats), dtype=np.float32)
        for i, v in enumerate(vals):
            if v in cat_map:
                oh[i, cat_map[v]] = 1.0
        parts.append(oh)
        feat_config[col] = {"type": "one-hot", "n_cats": n_cats, "categories": cat_map}

    # ── Continuous: standardized TOTINC (Leg-1/Leg-2 identical) ─────────
    for col in CONT_COLS:
        if col not in df.columns:
            print(f"  WARNING: {col} not found in data, skipping")
            continue
        vals = df[col].fillna(0.0).values.reshape(-1, 1).astype(np.float64)
        if scaler is None:
            scaler = StandardScaler()
            scaled = scaler.fit_transform(vals).astype(np.float32)
        else:
            scaled = scaler.transform(vals).astype(np.float32)
        parts.append(scaled)
        feat_config[col] = {
            "type": "continuous",
            "mean": float(scaler.mean_[0]),
            "std": float(scaler.scale_[0]),
        }

    # ── Binary flags (Leg-1/Leg-2 identical) ────────────────────────────
    for col in BIN_COLS:
        if col in df.columns:
            raw = df[col]
            if raw.dtype == object:
                vals = pd.factorize(raw.fillna("missing"))[0].astype(np.float32)
            else:
                vals = raw.fillna(0).astype(np.float32).values
        else:
            print(f"  INFO: {col} not in data, deriving from CYCLE_YEAR")
            vals = (df["CYCLE_YEAR"] == 2022).astype(np.float32).values
        parts.append(vals.reshape(-1, 1))
        feat_config[col] = {"type": "binary"}

    # ── Leg-2 WORK_SCHEDULE one-hot (cats 1..9, NaN -> all-zero) [unchanged] ──
    if WORK_SCHEDULE_COL in df.columns:
        if WORK_SCHEDULE_COL not in encoders:
            encoders[WORK_SCHEDULE_COL] = {int(c): i for i, c in enumerate(WORK_SCHEDULE_CATS)}
        ws_map = encoders[WORK_SCHEDULE_COL]
        n_cats = len(ws_map)
        oh = np.zeros((n, n_cats), dtype=np.float32)
        raw = df[WORK_SCHEDULE_COL].values
        for i, v in enumerate(raw):
            if pd.notna(v):
                iv = int(v)
                if iv in ws_map:
                    oh[i, ws_map[iv]] = 1.0  # out-of-range / NaN -> all-zero row
        parts.append(oh)
        feat_config[WORK_SCHEDULE_COL] = {
            "type": "one-hot", "n_cats": n_cats, "categories": ws_map,
            "note": "NaN -> all-zero",
        }
    else:
        print(f"  WARNING: {WORK_SCHEDULE_COL} not found, skipping (Leg-2 cond)")

    # ── Leg-2 NAICS one-hot industry bucket (NaN -> all-zero) [unchanged] ────
    if NAICS_COL in df.columns:
        if NAICS_COL not in encoders:
            raw = df[NAICS_COL]
            cats = sorted(int(v) for v in raw.dropna().unique())
            encoders[NAICS_COL] = {int(v): i for i, v in enumerate(cats)}
        na_map = encoders[NAICS_COL]
        n_cats = len(na_map)
        oh = np.zeros((n, n_cats), dtype=np.float32)
        raw = df[NAICS_COL].values
        for i, v in enumerate(raw):
            if pd.notna(v):
                iv = int(v)
                if iv in na_map:
                    oh[i, na_map[iv]] = 1.0  # NaN -> all-zero row
        parts.append(oh)
        feat_config[NAICS_COL] = {
            "type": "one-hot", "n_cats": n_cats, "categories": na_map,
            "note": "NaN -> all-zero",
        }
    else:
        print(f"  WARNING: {NAICS_COL} not found, skipping (Leg-2 cond)")

    # ── Leg-2 TELEWORK binary + telework_known indicator bit [unchanged] ────
    if TELEWORK_COL in df.columns:
        raw = df[TELEWORK_COL]
        known = raw.notna().astype(np.float32).values            # 1 if non-NaN
        # value -> 0/1: GSS telework binaries commonly use 1=yes; treat ==1 as 1.
        tele = np.where(raw.notna().values, (raw.values == 1).astype(np.float32), 0.0)
        parts.append(tele.reshape(-1, 1).astype(np.float32))
        parts.append(known.reshape(-1, 1))
        feat_config[TELEWORK_COL] = {"type": "binary", "note": "NaN -> 0"}
        feat_config["TELEWORK_KNOWN"] = {
            "type": "binary", "note": "1 if TELEWORK non-NaN else 0",
        }
    else:
        print(f"  WARNING: {TELEWORK_COL} not found, skipping (Leg-2 cond)")

    cond_vec = np.concatenate(parts, axis=1).astype(np.float32)

    cycle_idx = df["CYCLE_YEAR"].map(CYCLE_MAP).fillna(0).astype(np.int64).values
    return cond_vec, cycle_idx, feat_config, encoders, scaler


def split_respondents(df: pd.DataFrame, random_state: int = 42):
    """70/15/15 split stratified by CYCLE_YEAR x DDAY_STRATA. Returns row indices."""
    strat = df["CYCLE_YEAR"].astype(str) + "_" + df["DDAY_STRATA"].astype(str)
    n = len(df)
    row_idx = np.arange(n)

    n_test = int(round(n * 0.15))
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=n_test, random_state=random_state)
    trainval_pos, test_pos = next(sss1.split(row_idx, strat))

    n_val = int(round(n * 0.15))
    trainval_strat = strat.iloc[trainval_pos].reset_index(drop=True)
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=n_val, random_state=random_state)
    train_sub, val_sub = next(sss2.split(trainval_pos, trainval_strat))

    return trainval_pos[train_sub], trainval_pos[val_sub], test_pos


def subsample_stratified(df: pd.DataFrame, frac: float, min_rows: int, seed: int):
    """
    Stratified ~frac subsample of ROW INDICES keyed by CYCLE_YEAR x DDAY_STRATA.
    Guarantees >= min_rows total (and >= 1 per cell). Returns sorted unique idx.
    """
    rng = np.random.default_rng(seed)
    keys = (df["CYCLE_YEAR"].astype(int).astype(str) + "_"
            + df["DDAY_STRATA"].astype(int).astype(str)).values
    out = []
    for k in np.unique(keys):
        cell = np.where(keys == k)[0]
        n_pick = max(1, int(round(len(cell) * frac)))
        n_pick = min(n_pick, len(cell))
        out.append(rng.choice(cell, size=n_pick, replace=False))
    sel = np.sort(np.concatenate(out))
    # Top up to min_rows if needed (draw from remaining pool, stratification kept loose)
    if len(sel) < min_rows:
        remaining = np.setdiff1d(np.arange(len(df)), sel)
        extra_n = min(min_rows - len(sel), len(remaining))
        if extra_n > 0:
            extra = rng.choice(remaining, size=extra_n, replace=False)
            sel = np.sort(np.concatenate([sel, extra]))
    return sel


def pack_tensors(sub_df, act_seq, home_seq, work_seq, work_avail,
                  retail_seq, retail_avail, cop_bin, cop_avail, cond_vec, cycle_idx):
    """
    Bundle selected rows into a dict of PyTorch tensors.
    aux_seq = [AT_HOME | AT_WORK | AT_RETAIL | 9 co-pres]: shape (n, 48, 12).
    [Leg-3 delta] AT_RETAIL inserted as the 3rd plane, BEFORE the 9 co-presence
    planes (CONTRACT ordering: 0=home, 1=work, 2=retail, 3..11=cop).
    """
    aux_seq = np.concatenate(
        [home_seq[:, :, np.newaxis], work_seq[:, :, np.newaxis],
         retail_seq[:, :, np.newaxis], cop_bin], axis=2
    )  # (n, 48, 12)

    return {
        "act_seq":      torch.tensor(act_seq,      dtype=torch.long),     # (n,48) 0-indexed
        "aux_seq":      torch.tensor(aux_seq,      dtype=torch.float32),  # (n,48,12)
        "cop_avail":    torch.tensor(cop_avail,    dtype=torch.bool),     # (n,48,9)
        "work_avail":   torch.tensor(work_avail,   dtype=torch.bool),     # (n,48)
        "retail_avail": torch.tensor(retail_avail, dtype=torch.bool),     # (n,48) [Leg-3 NEW]
        "cond_vec":     torch.tensor(cond_vec,     dtype=torch.float32),  # (n,d_cond)
        "cycle_idx":    torch.tensor(cycle_idx,    dtype=torch.long),     # (n,)
        "cycle_year":   torch.tensor(sub_df["CYCLE_YEAR"].values, dtype=torch.long),
        "obs_strata":   torch.tensor(sub_df["DDAY_STRATA"].values, dtype=torch.long),
        "wght_per":     torch.tensor(sub_df["WGHT_PER"].fillna(1.0).values, dtype=torch.float32),
        "occ_ids":      torch.tensor(sub_df["occID"].fillna(0).astype(np.int64).values, dtype=torch.long),
    }


def _pos_weight(values: np.ndarray, default: float = 1.001) -> float:
    """(1-freq)/freq positive weight, clamped > 1 to keep training asserts happy."""
    if len(values) == 0:
        return default
    freq = float(values.mean())
    pw = (1.0 - freq) / max(freq, 1e-9)
    return round(max(pw, 1.0 + 1e-3), 6)


# ── Main ────────────────────────────────────────────────────────────────────

def run(args):
    input_dir = INPUT_DIR
    out_dir = OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 64)
    print(f"Step 4A (Leg-3, 4-split) — Three-Channel Assembly  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 64)
    print(f"  INPUT_DIR : {input_dir}")
    print(f"  OUTPUT_DIR: {out_dir}")

    # ── Load ────────────────────────────────────────────────────────────
    print("\n[1/7] Loading data...")
    hetus, cop, work, retail = load_data(input_dir)
    print(f"  hetus_30min:      {hetus.shape}")
    print(f"  copresence_30min: {cop.shape}")
    print(f"  work_30min:       {work.shape}")
    print(f"  retail_30min:     {retail.shape}  [Leg-3 NEW]")

    # ── A1: Merge (positional concat) ───────────────────────────────────
    print("\n[2/7] Joining hetus + copresence + work + retail (positional, same row order)...")
    df, _, _, _ = merge_inputs(hetus, cop, work, retail)
    print(f"  Merged shape: {df.shape}")
    print(f"  Unique occIDs: {df['occID'].nunique()}")
    n_full = len(df)
    if n_full != 64061:
        print(f"  WARNING: expected 64061 rows, got {n_full}")

    # ── Optional stratified subsample (--sample) ────────────────────────
    if args.sample:
        sel = subsample_stratified(df, args.sample_frac, args.sample_min, args.seed)
        df = df.iloc[sel].reset_index(drop=True)
        print(f"\n  [SAMPLE] stratified subsample: {len(df)} / {n_full} rows "
              f"(frac={args.sample_frac}, min={args.sample_min}, seed={args.seed})")

    # ── A2: Demographic conditioning vector ─────────────────────────────
    print("\n[3/7] Encoding demographics (Leg-2 block UNCHANGED — no retail conditioning)...")
    cond_vec, cycle_idx, feat_config, encoders, scaler = encode_demographics(df)
    d_cond = cond_vec.shape[1]
    print(f"  Conditioning vector shape: ({len(df)}, {d_cond})")
    print(f"  d_cond = {d_cond}")

    # ── A3: Sequence token construction ─────────────────────────────────
    print("\n[4/7] Building sequence tokens...")

    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    act_seq = df[act_cols].values.astype(np.int64) - 1  # (n,48) 0-indexed (raw 1..14 -> 0..13)

    hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    home_seq = df[hom_cols].values.astype(np.float32)   # (n,48) already 0/1

    cop_bin, cop_avail = build_cop_avail_and_recode(df)          # (n,48,9)
    work_seq, work_avail = build_work_track(df)                  # (n,48), (n,48)
    retail_seq, retail_avail = build_retail_track(df)             # (n,48), (n,48) [Leg-3 NEW]

    print(f"    act_seq:      {act_seq.shape}")
    print(f"    home_seq:     {home_seq.shape}")
    print(f"    work_seq:     {work_seq.shape}   (AT_WORK)")
    print(f"    work_avail:   {work_avail.shape}  True rate={work_avail.mean():.3f}")
    print(f"    retail_seq:   {retail_seq.shape}   (AT_RETAIL)  [Leg-3 NEW]")
    print(f"    retail_avail: {retail_avail.shape}  True rate={retail_avail.mean():.3f}  [Leg-3 NEW]")
    print(f"    cop_bin:      {cop_bin.shape}")

    # Validate co-presence / work / retail
    old_mask = np.isin(df["CYCLE_YEAR"].values, [2005, 2010])
    assert cop_bin[old_mask, :, 8].sum() == 0, "BUG: colleagues non-zero for 2005/2010"
    assert set(np.unique(cop_bin[cop_avail])).issubset({0.0, 1.0}), \
        "BUG: recoded co-presence outside {0,1}"
    assert set(np.unique(work_seq[work_avail])).issubset({0.0, 1.0}), \
        "BUG: AT_WORK outside {0,1}"
    assert set(np.unique(retail_seq[retail_avail])).issubset({0.0, 1.0}), \
        "BUG: AT_RETAIL outside {0,1}"
    print("  OK colleagues=0 for 2005/2010; cop & work & retail values in {0,1}")

    # AT_HOME / AT_WORK / AT_RETAIL positive rates per cycle (masked by availability)
    print("\n  === AT_HOME / AT_WORK / AT_RETAIL POSITIVE RATES BY CYCLE ===")
    for cy in [2005, 2010, 2015, 2022]:
        m = df["CYCLE_YEAR"].values == cy
        if not m.any():
            continue
        home_rate = float(home_seq[m].mean())
        wa = work_avail[m]
        wvals = work_seq[m][wa]
        work_rate = float(wvals.mean()) if wvals.size else float("nan")
        work_av_rate = float(wa.mean())
        ra = retail_avail[m]
        rvals = retail_seq[m][ra]
        retail_rate = float(rvals.mean()) if rvals.size else float("nan")
        retail_av_rate = float(ra.mean())
        print(f"    {cy}: AT_HOME={home_rate:.3f}  "
              f"AT_WORK={work_rate:.3f} (avail={work_av_rate:.3f})  "
              f"AT_RETAIL={retail_rate:.3f} (avail={retail_av_rate:.3f})")

    # ── A4: Train / val / test split ────────────────────────────────────
    print("\n[5/7] Splitting train / val / test (70/15/15 stratified, seed=42)...")
    train_idx, val_idx, test_idx = split_respondents(df, random_state=args.seed)
    assert len(np.intersect1d(train_idx, val_idx)) == 0, "LEAK: train n val"
    assert len(np.intersect1d(train_idx, test_idx)) == 0, "LEAK: train n test"
    assert len(np.intersect1d(val_idx, test_idx)) == 0, "LEAK: val n test"
    print(f"  Train: {len(train_idx)} | Val: {len(val_idx)} | Test: {len(test_idx)}")

    # ── Class frequencies / pos_weights (training split only) ───────────
    print("\n[6/7] Computing class frequencies + pos_weights (train split)...")
    COP7_INDICES = [0, 1, 2, 3, 6, 7, 8]
    COP7_NAMES = ["Alone", "Spouse", "Children", "parents", "friends", "others", "colleagues"]
    cop_pos_weights = {}
    for name, ci in zip(COP7_NAMES, COP7_INDICES):
        avail_mask = cop_avail[train_idx, :, ci]
        vals = cop_bin[train_idx, :, ci][avail_mask]
        cop_pos_weights[name] = _pos_weight(vals)

    # AT_HOME pos_weight (always available -> no mask)
    home_pos_weight = _pos_weight(home_seq[train_idx].flatten())

    # AT_WORK pos_weight (masked by work_avail)
    wa_tr = work_avail[train_idx]
    work_vals_tr = work_seq[train_idx][wa_tr]
    work_pos_weight = _pos_weight(work_vals_tr)

    # AT_RETAIL pos_weight (masked by retail_avail) — [Leg-3 NEW]
    ra_tr = retail_avail[train_idx]
    retail_vals_tr = retail_seq[train_idx][ra_tr]
    retail_pos_weight = _pos_weight(retail_vals_tr)

    act_train_flat = act_seq[train_idx].flatten()
    act_counts = np.bincount(act_train_flat, minlength=N_ACT_CLASSES).astype(float)
    act_class_freqs = [round(v, 6) for v in (act_counts / act_counts.sum()).tolist()]

    print(f"  home_pos_weight:   {home_pos_weight:.4f}")
    print(f"  work_pos_weight:   {work_pos_weight:.4f}  (AT_WORK, masked by work_avail)")
    print(f"  retail_pos_weight: {retail_pos_weight:.4f}  (AT_RETAIL, masked by retail_avail)  [Leg-3 NEW]")
    print(f"  cop_pos_weights:   { {k: f'{v:.3f}' for k, v in cop_pos_weights.items()} }")

    # ── Save datasets ───────────────────────────────────────────────────
    print("\n[7/7] Saving tensor datasets + metadata + config...")

    meta_cols = ["occID", "CYCLE_YEAR", "DDAY_STRATA", "AGEGRP", "SEX",
                 "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA",
                 "HRSWRK", "NOCS", "TOTINC", "WGHT_PER",
                 "ATTSCH", "POWST"]
    meta_cols = [c for c in meta_cols if c in df.columns]

    for split_name, row_idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
        sub_df = df.iloc[row_idx].reset_index(drop=True)
        tensors = pack_tensors(
            sub_df,
            act_seq[row_idx], home_seq[row_idx],
            work_seq[row_idx], work_avail[row_idx],
            retail_seq[row_idx], retail_avail[row_idx],
            cop_bin[row_idx], cop_avail[row_idx],
            cond_vec[row_idx], cycle_idx[row_idx],
        )
        pt_path = os.path.join(out_dir, f"step4_{split_name}.pt")
        torch.save(tensors, pt_path)
        print(f"  Saved {pt_path}  (n={len(sub_df)})")
        sub_df[meta_cols].to_csv(
            os.path.join(out_dir, f"step4_{split_name}_meta.csv"), index=False
        )

    # Full metadata for inference merge (all respondents)
    all_meta_cols = ["occID", "CYCLE_YEAR", "SURVYEAR", "DDAY_STRATA",
                     "AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA",
                     "HRSWRK", "NOCS", "TOTINC", "WGHT_PER", "COLLECT_MODE",
                     "NAICS", "TELEWORK", "WORK_SCHEDULE"]
    all_meta_cols = [c for c in all_meta_cols if c in df.columns]
    df[all_meta_cols].to_csv(os.path.join(out_dir, "step4_all_meta.csv"), index=False)

    # feature_config.json
    feature_config = {
        "d_cond":             int(d_cond),
        "n_activity_classes": N_ACT_CLASSES,
        "n_copresence":       N_COP,
        "n_slots":            N_SLOTS,
        "n_aux":              N_AUX,
        "cycle_map":          CYCLE_MAP,
        "cop_col_names":      COP_COLS,
        "aux_order":          ["AT_HOME", "AT_WORK", "AT_RETAIL"] + COP_COLS,
        "feature_parts":      feat_config,
        "split_sizes": {
            "train": int(len(train_idx)),
            "val":   int(len(val_idx)),
            "test":  int(len(test_idx)),
        },
        "cop_pos_weights":    cop_pos_weights,
        "act_class_freqs":    act_class_freqs,
        "home_pos_weight":    home_pos_weight,
        "work_pos_weight":    work_pos_weight,
        "retail_pos_weight":  retail_pos_weight,
    }
    if args.sample:
        feature_config["sample_frac"] = float(args.sample_frac)
        feature_config["sample_seed"] = int(args.seed)
    cfg_path = os.path.join(out_dir, "step4_feature_config.json")
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(feature_config, f, indent=2)
    print(f"  Saved {cfg_path}")

    print(f"\nOK 04A (Leg-3, 4-split) complete.")
    print(f"  d_cond = {d_cond}  |  n_aux = {N_AUX}  |  work_pos_weight = {work_pos_weight:.4f}  "
          f"|  retail_pos_weight = {retail_pos_weight:.4f}")
    print(f"  Output dir: {out_dir}")
    return feature_config


def main():
    run(parse_args())


if __name__ == "__main__":
    main()
