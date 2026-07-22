# -*- coding: utf-8 -*-
"""
3rdJ_04C_pairs_4split.py — Step 4C (Leg-3, four-channel split): Training Pair
Construction.

Ported VERBATIM (logic UNCHANGED) from Leg-2's 3rdJ_04C_pairs_2split.py.
Leg-2 file is READ-ONLY / template only — not imported, not modified.
Per the runbook (K=5 pairing logic is design-frozen): only the platform-
detection path block is repointed to Leg3_4-split/Step4_docs/outputs_step4/.
The K=5 neighbour matching is byte-for-byte the Leg-1/Leg-2 scheme; the
three-channel data layer (AT_HOME + AT_WORK + AT_RETAIL) does not change pair
construction (pairs key off demographics + strata only, not occupancy channels).

For each respondent in the training split, finds K=5 demographically similar
neighbours observed on a DIFFERENT DDAY_STRATA within the same CYCLE_YEAR.

Matching logic:
  Exact match on: AGEGRP, SEX, MARSTH, HHSIZE, LFTAG
  Fuzzy match on: PR, CMA, HRSWRK, NOCS, TOTINC (within +/-1 bin)

Usage:
    py -3 -X utf8 3rdJ_04C_pairs_4split.py           # full dataset
    py -3 -X utf8 3rdJ_04C_pairs_4split.py --sample  # smoke test (same out dir)
"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from collections import Counter

import numpy as np
import pandas as pd
import torch

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Platform-detection path block (mirrors Leg-3 Step3 / 04A) ─────────────────
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

OUTPUT_DIR = os.path.join(_LEG3_BASE, "Step4_docs", "outputs_step4")

K = 5              # number of neighbours per (source, target_strata) pair
N_TOTINC_BINS = 6  # quantile bins for continuous TOTINC fuzzy matching

EXACT_COLS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
FUZZY_COLS = ["PR", "CMA", "HRSWRK", "NOCS"]   # TOTINC handled separately


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", action="store_true",
                   help="Smoke-test mode (reads/writes the same outputs_step4/ artifacts)")
    return p.parse_args()


def load_metadata(out_dir: str, split: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(out_dir, f"step4_{split}_meta.csv"), low_memory=False)


def bin_totinc(meta: pd.DataFrame) -> pd.Series:
    """Bin TOTINC into N_TOTINC_BINS quantile bins within each CYCLE_YEAR."""
    bins = pd.Series(np.zeros(len(meta), dtype=int), index=meta.index)
    for cy, grp in meta.groupby("CYCLE_YEAR"):
        vals = grp["TOTINC"].fillna(grp["TOTINC"].median())
        try:
            labels = pd.qcut(vals, q=N_TOTINC_BINS, labels=False, duplicates="drop")
        except ValueError:
            labels = pd.Series(0, index=grp.index)
        bins.loc[grp.index] = labels.fillna(0).astype(int)
    return bins


def compute_pair_indices(meta: pd.DataFrame, split: str) -> dict:
    """
    For each respondent in meta, find K nearest neighbours per target stratum.

    Returns dict:
        src_idx       (n_pairs,)    — integer index into meta (row position)
        tgt_k_indices (n_pairs, K)  — K neighbour row positions
        tgt_strata    (n_pairs,)    — target DDAY_STRATA (1,2,3)
    """
    meta = meta.reset_index(drop=True)
    n = len(meta)

    totinc_bin = bin_totinc(meta).values

    col_arrays = {}
    for col in EXACT_COLS + FUZZY_COLS:
        if col in meta.columns:
            col_arrays[col] = meta[col].fillna(-999).astype(int).values
        else:
            col_arrays[col] = np.full(n, -999, dtype=int)

    cycle_year = meta["CYCLE_YEAR"].values
    dday_strata = meta["DDAY_STRATA"].values

    all_src_idx, all_tgt_k_idx, all_tgt_strata = [], [], []

    strata_groups: dict = {}
    for i in range(n):
        key = (int(cycle_year[i]), int(dday_strata[i]))
        strata_groups.setdefault(key, []).append(i)

    n_no_neighbors = 0

    for src_i in range(n):
        cy = int(cycle_year[src_i])
        s_obs = int(dday_strata[src_i])
        target_strata_list = [s for s in [1, 2, 3] if s != s_obs]

        for s_tgt in target_strata_list:
            candidates = strata_groups.get((cy, s_tgt), [])
            candidates = [j for j in candidates if j != src_i]

            if len(candidates) == 0:
                n_no_neighbors += 1
                fallback = [j for j in range(n)
                            if j != src_i and cycle_year[j] == cy and dday_strata[j] == s_tgt]
                if not fallback:
                    continue
                candidates = fallback

            scores = _score_candidates(src_i, candidates, col_arrays, totinc_bin)

            top_k_count = min(K, len(candidates))
            top_indices = np.argsort(scores)[::-1][:top_k_count]
            top_cands = [candidates[i] for i in top_indices]

            if len(top_cands) < K:
                rng = np.random.default_rng(seed=src_i * 3 + s_tgt)
                extra = rng.choice(top_cands, size=K - len(top_cands), replace=True).tolist()
                top_cands = top_cands + extra

            all_src_idx.append(src_i)
            all_tgt_k_idx.append(top_cands)
            all_tgt_strata.append(s_tgt)

    if n_no_neighbors > 0:
        print(f"  WARNING: {n_no_neighbors} (src, target_strata) combinations "
              f"had no candidates and were skipped.")

    return {
        "src_idx":       torch.tensor(all_src_idx,    dtype=torch.long),
        "tgt_k_indices": torch.tensor(all_tgt_k_idx,  dtype=torch.long),  # (n_pairs, K)
        "tgt_strata":    torch.tensor(all_tgt_strata, dtype=torch.long),
    }


def _score_candidates(src_i, candidates, col_arrays, totinc_bin) -> np.ndarray:
    """
    Exact match on AGEGRP,SEX,MARSTH,HHSIZE,LFTAG: +1 each (max 5)
    Fuzzy match on PR,CMA,HRSWRK,NOCS,TOTINC (+/-1 bin): +1 each (max 5)
    """
    scores = np.zeros(len(candidates), dtype=np.float32)
    cand_arr = np.array(candidates)

    for col in EXACT_COLS:
        arr = col_arrays.get(col)
        if arr is None:
            continue
        scores += (arr[cand_arr] == arr[src_i]).astype(np.float32)

    for col in FUZZY_COLS:
        arr = col_arrays.get(col)
        if arr is None:
            continue
        scores += (np.abs(arr[cand_arr] - arr[src_i]) <= 1).astype(np.float32)

    scores += (np.abs(totinc_bin[cand_arr] - totinc_bin[src_i]) <= 1).astype(np.float32)
    return scores


def inspect_pairs(pairs: dict, meta: pd.DataFrame):
    n_pairs = len(pairs["src_idx"])
    K_actual = pairs["tgt_k_indices"].shape[1] if n_pairs else K

    print(f"\n  Total pairs: {n_pairs}  (expect ~{2 * len(meta)} for full split)")
    if n_pairs == 0:
        print("  (no pairs — nothing to inspect)")
        return
    per_strata = Counter(pairs["tgt_strata"].tolist())
    print(f"  Pairs per target strata: {dict(sorted(per_strata.items()))}")

    src_i = pairs["src_idx"][0].item()
    k_idxs = pairs["tgt_k_indices"][0].tolist()
    s_tgt = pairs["tgt_strata"][0].item()
    src = meta.iloc[src_i]
    tgt = meta.iloc[k_idxs[0]]

    print(f"\n  === SOURCE RESPONDENT (pair 0) ===")
    print(f"    occID={src['occID']}  CYCLE_YEAR={src['CYCLE_YEAR']}  "
          f"DDAY_STRATA={src['DDAY_STRATA']}(observed)")
    print(f"\n  === TARGET STRATA: {s_tgt} (K={K_actual} neighbours) ===")
    print(f"    Neighbour occIDs: {[meta.iloc[i]['occID'] for i in k_idxs]}")

    score = 0
    for col in EXACT_COLS:
        if col in meta.columns and src.get(col) == tgt.get(col):
            score += 1
    print(f"    Exact-match score: {score}/5  (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG)")

    for i in range(min(50, n_pairs)):
        si = pairs["src_idx"][i].item()
        for ti in pairs["tgt_k_indices"][i].tolist():
            assert si != ti, f"FAIL: self-pairing at pair {i}"
    print("  OK No self-pairing in first 50 pairs")

    for i in range(min(50, n_pairs)):
        si = pairs["src_idx"][i].item()
        for ti in pairs["tgt_k_indices"][i].tolist():
            assert meta.iloc[si]["CYCLE_YEAR"] == meta.iloc[ti]["CYCLE_YEAR"], \
                f"FAIL: cross-cycle pair at {i}"
    print("  OK All sampled neighbours share CYCLE_YEAR with source (first 50)")


def main():
    args = parse_args()
    data_dir = OUTPUT_DIR
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 64)
    print(f"Step 4C (Leg-3, 4-split) — Training Pairs  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 64)
    print(f"  data_dir:   {data_dir}")
    print(f"  output_dir: {output_dir}")

    print("\n[1/3] Loading metadata...")
    train_meta = load_metadata(data_dir, "train")
    val_meta = load_metadata(data_dir, "val")
    print(f"  Train metadata: {train_meta.shape}")
    print(f"  Val metadata:   {val_meta.shape}")
    print(f"  Train DDAY_STRATA distribution: "
          f"{train_meta['DDAY_STRATA'].value_counts().sort_index().to_dict()}")

    print("\n[2/3] Building training pairs (K=5 per source x target strata)...")
    train_pairs = compute_pair_indices(train_meta, "train")

    print("\n[3/3] Building validation pairs...")
    val_pairs = compute_pair_indices(val_meta, "val")

    print("\n  === TRAINING PAIRS INSPECTION ===")
    inspect_pairs(train_pairs, train_meta)

    train_path = os.path.join(output_dir, "training_pairs.pt")
    val_path = os.path.join(output_dir, "val_pairs.pt")
    torch.save(train_pairs, train_path)
    torch.save(val_pairs, val_path)
    print(f"\n  Saved {train_path}")
    print(f"  Saved {val_path}")

    # strata_inv_freq.npy — inverse frequency per stratum index, shape (4,)
    strata_counts_train = Counter(train_meta["DDAY_STRATA"].values)
    strata_inv_freq_arr = np.array(
        [1.0 / strata_counts_train.get(s, 1) for s in range(4)], dtype=np.float32
    )
    sif_path = os.path.join(output_dir, "strata_inv_freq.npy")
    np.save(sif_path, strata_inv_freq_arr)
    print(f"  Saved {sif_path}  (strata 0-3: {strata_inv_freq_arr.tolist()})")

    print(f"\nOK 04C (Leg-3, 4-split) complete.")
    print(f"  Training pairs: {len(train_pairs['src_idx'])} ({len(train_meta)} respondents)")
    print(f"  Val pairs:      {len(val_pairs['src_idx'])}")


if __name__ == "__main__":
    main()
