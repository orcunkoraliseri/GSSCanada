# -*- coding: utf-8 -*-
"""
3rdJ_04Q_make_s10_sample.py — 10% Pair-Level Stratified Subsample for MDLM Ablation.

PURPOSE
-------
Produce a 10% subsample of the Step-4 training dataset (outputs_step4/) that
both the AR baseline (04D) and the MDLM (04D_mdlm) can train on.  Having BOTH
arms train on the EXACT SAME 10% subset makes the ablation apples-to-apples
(no data-scale confound).

SUBSAMPLE STRATEGY
------------------
Pair-level stratification by cycle x day-type (obs_strata).

The key field is the SOURCE respondent's (cycle_year, obs_strata) stratum.
Within each stratum we draw 10% of the UNIQUE SOURCE respondents (not pairs),
then keep all training pairs whose src_idx falls in the selected set.  This
ensures:
  (a) The stratum distribution of sources is preserved at 10%.
  (b) All neighbour pairs of selected sources are included (not a random 10%
      of pairs), so the K-nearest-neighbour structure of training_pairs.pt
      is intact.

Seed: 42 throughout.

OUTPUT (outputs_step4_s10/)
---------------------------
  step4_train.pt          — subset of step4_train.pt respondents
  step4_val.pt            — FULL step4_val.pt (unchanged; val set is not subsampled)
  step4_test.pt           — FULL step4_test.pt (unchanged)
  training_pairs.pt       — subset of training_pairs.pt (src_idx re-indexed)
  step4_feature_config.json — copy (unchanged; d_cond etc. are identical)
  step4_all_meta.csv      — subset of rows matching selected respondents

Re-indexing: src_idx in training_pairs.pt is re-indexed to the contiguous
0..(n_selected-1) range of the subsampled step4_train.pt.  tgt_k_indices
are re-indexed the same way (only pairs where ALL K targets are also in the
selected set are kept; otherwise the pair is dropped).  This preserves the
Dataset.__getitem__ contract of 04D's Step4DatasetMDLM.

Usage:
    py -3 -X utf8 3rdJ_04Q_make_s10_sample.py           # 10% (default)
    py -3 -X utf8 3rdJ_04Q_make_s10_sample.py --frac 0.05   # 5% for quick test
"""

from __future__ import annotations

import argparse
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

# ── Platform-detection path block ─────────────────────────────────────────────
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

SRC_DIR  = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4")
DST_DIR  = os.path.join(_LEG2_BASE, "Step4_docs", "outputs_step4_s10")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--frac",     type=float, default=0.10,
                   help="Fraction of source respondents to sample (default 0.10)")
    p.add_argument("--seed",     type=int,   default=42)
    p.add_argument("--src_dir",  default=None, help="Override source directory")
    p.add_argument("--dst_dir",  default=None, help="Override destination directory")
    return p.parse_args()


def stratified_sample_sources(src_strata_np, cycle_np, frac, rng):
    """
    Select frac of the unique source respondents, stratified by
    (cycle_year, obs_strata) bucket.

    Parameters
    ----------
    src_strata_np : (n,) int — obs_strata for each respondent
    cycle_np      : (n,) int — cycle_year for each respondent
    frac          : float   — target fraction (e.g. 0.10)
    rng           : np.random.Generator

    Returns
    -------
    selected_idx  : sorted array of selected respondent indices (in 0..n-1)
    """
    n = len(src_strata_np)
    key = cycle_np * 10 + src_strata_np   # unique bucket per (year, strata)

    selected = []
    for g in np.unique(key):
        members = np.where(key == g)[0]
        k = max(1, int(round(len(members) * frac)))
        chosen = rng.choice(members, size=min(k, len(members)), replace=False)
        selected.extend(chosen.tolist())

    return np.sort(np.array(selected, dtype=np.int64))


def subset_tensor_dict(data: dict, idx: np.ndarray) -> dict:
    """Return a new dict with each tensor sliced to idx."""
    return {k: v[idx] for k, v in data.items()}


def main():
    args = parse_args()
    src_dir = args.src_dir or SRC_DIR
    dst_dir = args.dst_dir or DST_DIR

    if args.frac != 0.10:
        # Adjust dst_dir to reflect custom fraction
        pct = int(round(args.frac * 100))
        dst_dir = dst_dir.replace("_s10", f"_s{pct:02d}")

    os.makedirs(dst_dir, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    print("=" * 60)
    print(f"Step 4Q — 10% stratified subsample (frac={args.frac}, seed={args.seed})")
    print(f"  src: {src_dir}")
    print(f"  dst: {dst_dir}")
    print("=" * 60)

    # ── Load source files ──────────────────────────────────────────────────────
    print("\n[1/5] Loading step4_train.pt ...")
    train_data  = torch.load(os.path.join(src_dir, "step4_train.pt"),
                             map_location="cpu", weights_only=False)
    n_train     = len(train_data["act_seq"])
    print(f"  step4_train.pt: {n_train} respondents")

    print("[1/5] Loading training_pairs.pt ...")
    pairs       = torch.load(os.path.join(src_dir, "training_pairs.pt"),
                             map_location="cpu", weights_only=False)
    n_pairs     = len(pairs["src_idx"])
    print(f"  training_pairs.pt: {n_pairs} pairs")

    # ── Stratified source selection ────────────────────────────────────────────
    print(f"\n[2/5] Selecting {args.frac*100:.0f}% of sources (stratified) ...")
    strata_np = train_data["obs_strata"].numpy().astype(int)
    cycle_np  = train_data["cycle_year"].numpy().astype(int)

    selected_src_abs = stratified_sample_sources(strata_np, cycle_np, args.frac, rng)
    print(f"  Selected {len(selected_src_abs)} / {n_train} source respondents "
          f"({100*len(selected_src_abs)/n_train:.1f}%)")

    # ── Build old-index -> new-index mapping for train set ────────────────────
    selected_set = set(selected_src_abs.tolist())
    old_to_new   = {old: new for new, old in enumerate(selected_src_abs)}

    # ── Filter training pairs ─────────────────────────────────────────────────
    print("\n[3/5] Filtering training pairs ...")
    src_idx_np   = pairs["src_idx"].numpy()
    tgt_k_np     = pairs["tgt_k_indices"].numpy()   # (n_pairs, K)

    # Keep a pair if BOTH its source AND all K targets are in the selected set.
    src_mask = np.isin(src_idx_np, selected_src_abs)
    tgt_mask = np.all(np.isin(tgt_k_np, selected_src_abs), axis=1)
    keep_mask = src_mask & tgt_mask

    # If no pair passes the joint filter (very small frac), fall back to src-only.
    if keep_mask.sum() == 0:
        print("  WARNING: no pairs pass joint src+tgt filter; falling back to src-only.")
        keep_mask = src_mask

    new_src_idx = np.array([old_to_new[i] for i in src_idx_np[keep_mask]], dtype=np.int64)
    new_tgt_k   = np.array(
        [[old_to_new[j] for j in row] for row in tgt_k_np[keep_mask]], dtype=np.int64
    )
    # Handle case where tgt_k was not fully re-indexable (should not happen if joint filter)
    new_pairs = {
        "src_idx":        torch.from_numpy(new_src_idx),
        "tgt_k_indices":  torch.from_numpy(new_tgt_k),
    }
    # Carry over any extra keys in pairs dict
    for k, v in pairs.items():
        if k not in ("src_idx", "tgt_k_indices"):
            new_pairs[k] = v[keep_mask] if (isinstance(v, torch.Tensor) and v.shape[0] == n_pairs) else v

    print(f"  Kept {keep_mask.sum()} / {n_pairs} pairs "
          f"({100*keep_mask.sum()/n_pairs:.1f}%)")

    # ── Subset train tensors ───────────────────────────────────────────────────
    print("\n[4/5] Subsetting train tensors ...")
    train_sub = subset_tensor_dict(train_data, selected_src_abs)

    # ── Copy / save ───────────────────────────────────────────────────────────
    print("\n[5/5] Saving ...")

    torch.save(train_sub, os.path.join(dst_dir, "step4_train.pt"))
    print(f"  step4_train.pt saved ({len(selected_src_abs)} respondents)")

    torch.save(new_pairs, os.path.join(dst_dir, "training_pairs.pt"))
    print(f"  training_pairs.pt saved ({keep_mask.sum()} pairs)")

    # Val and test are NEVER subsampled (keep full for consistent validation)
    for split in ["val", "test"]:
        src_f = os.path.join(src_dir, f"step4_{split}.pt")
        dst_f = os.path.join(dst_dir, f"step4_{split}.pt")
        if os.path.isfile(src_f):
            shutil.copy2(src_f, dst_f)
            print(f"  step4_{split}.pt copied (full)")
        else:
            print(f"  WARNING: step4_{split}.pt not found at {src_f}")

    # Feature config: copy unchanged (d_cond, act_class_freqs etc. are global)
    cfg_src = os.path.join(src_dir, "step4_feature_config.json")
    cfg_dst = os.path.join(dst_dir, "step4_feature_config.json")
    if os.path.isfile(cfg_src):
        shutil.copy2(cfg_src, cfg_dst)
        print(f"  step4_feature_config.json copied")
    else:
        print(f"  WARNING: step4_feature_config.json not found at {cfg_src}")

    # Metadata CSV: subset to selected respondents' occ_ids
    meta_src = os.path.join(src_dir, "step4_all_meta.csv")
    meta_dst = os.path.join(dst_dir, "step4_all_meta.csv")
    if os.path.isfile(meta_src):
        meta      = pd.read_csv(meta_src, low_memory=False)
        occ_ids   = train_sub["occ_ids"].numpy() if "occ_ids" in train_sub else None
        if occ_ids is not None and "occID" in meta.columns:
            meta_sub  = meta[meta["occID"].isin(occ_ids)]
        else:
            meta_sub  = meta   # can't filter without occ_ids; keep full
        meta_sub.to_csv(meta_dst, index=False)
        print(f"  step4_all_meta.csv saved ({len(meta_sub)} rows / {len(meta)} total)")
    else:
        print(f"  WARNING: step4_all_meta.csv not found at {meta_src}")

    # Write a small provenance JSON
    prov = {
        "frac": args.frac, "seed": args.seed,
        "n_train_full": int(n_train),
        "n_train_sub":  int(len(selected_src_abs)),
        "n_pairs_full": int(n_pairs),
        "n_pairs_sub":  int(keep_mask.sum()),
        "strategy":     "pair-level stratified by (cycle_year x obs_strata); "
                        "10pct of unique source respondents per bucket; "
                        "all K-nearest-neighbour targets of selected sources kept "
                        "(pairs where any tgt is outside the selected set are dropped)",
        "src_dir":      src_dir,
        "dst_dir":      dst_dir,
    }
    with open(os.path.join(dst_dir, "s10_subsample_provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print(f"\nDone. 10% subsample written to: {dst_dir}")
    print(f"  Use --data_dir {dst_dir} for both 04D (AR baseline) and 04D_mdlm training.")


if __name__ == "__main__":
    main()
