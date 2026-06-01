"""
04C_training_pairs.py — Step 4C: Training Pair Construction

For each respondent in the training split, finds K=5 demographically similar
neighbors observed on a DIFFERENT DDAY_STRATA within the same CYCLE_YEAR.
The pair index structure (not full data copies) is saved so the training loop
can randomly sample one of K neighbors per epoch for stochastic diversity.

Matching logic:
  Exact match on: AGEGRP, SEX, MARSTH, HHSIZE, LFTAG
  Fuzzy match on: PR, CMA, HRSWRK, NOCS, TOTINC (within ±1 bin)

Usage:
    python 04C_training_pairs.py           # full dataset
    python 04C_training_pairs.py --sample  # 500-respondent sample
"""

import argparse
import os
from collections import Counter

import numpy as np
import pandas as pd
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

K = 5             # number of neighbors per (source, target_strata) pair
N_TOTINC_BINS = 6 # quantile bins for continuous TOTINC fuzzy matching

EXACT_COLS = ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG"]
FUZZY_COLS = ["PR", "CMA", "HRSWRK", "NOCS"]   # TOTINC handled separately


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", action="store_true",
                   help="Use 500-respondent sample files for local testing")
    p.add_argument("--output_dir", default=None,
                   help="Where to save pairs (default: same as data dir)")
    p.add_argument("--proportional", action="store_true",
                   help="G1: replicate pair rows proportional to target-stratum population frequency")
    return p.parse_args()


def load_metadata(out_dir: str, split: str) -> pd.DataFrame:
    path = os.path.join(out_dir, f"step4_{split}_meta.csv")
    return pd.read_csv(path, low_memory=False)


def bin_totinc(meta: pd.DataFrame) -> pd.Series:
    """
    Bin TOTINC into N_TOTINC_BINS quantile bins within each CYCLE_YEAR.
    Returns a Series of integer bin labels aligned with meta.index.
    """
    bins = pd.Series(np.zeros(len(meta), dtype=int), index=meta.index)
    for cy, grp in meta.groupby("CYCLE_YEAR"):
        vals = grp["TOTINC"].fillna(grp["TOTINC"].median())
        try:
            labels = pd.qcut(vals, q=N_TOTINC_BINS, labels=False, duplicates="drop")
        except ValueError:
            # Fallback: all same bin if too few unique values
            labels = pd.Series(0, index=grp.index)
        bins.loc[grp.index] = labels.fillna(0).astype(int)
    return bins


def compute_pair_indices(meta: pd.DataFrame, split: str,
                         proportional_targets: bool = False) -> dict:
    """
    For each respondent in meta, find K nearest neighbors per target stratum.

    Returns dict:
        src_idx       (n_pairs,)    — integer index into meta (row position)
        tgt_k_indices (n_pairs, K)  — K neighbor row positions
        tgt_strata    (n_pairs,)    — target DDAY_STRATA (1,2,3)

    proportional_targets (G1): replicate each (src, s_tgt) row by an integer
    factor proportional to pop_freq[s_tgt] among non-observed strata, so that
    the WeightedRandomSampler in 04D sees target strata in population proportion
    rather than uniform 33/33/33.
    """
    meta = meta.reset_index(drop=True)
    n = len(meta)

    # Pre-compute TOTINC bins for fuzzy matching
    totinc_bin = bin_totinc(meta).values  # (n,)

    # Convert key columns to numpy arrays for fast indexing
    col_arrays = {}
    for col in EXACT_COLS + FUZZY_COLS:
        if col in meta.columns:
            col_arrays[col] = meta[col].fillna(-999).astype(int).values
        else:
            col_arrays[col] = np.full(n, -999, dtype=int)

    cycle_year = meta["CYCLE_YEAR"].values
    dday_strata = meta["DDAY_STRATA"].values

    # DDAY_STRATA frequency for inverse-frequency weighting (imbalance mitigation)
    strata_counts = Counter(dday_strata)
    strata_inv_freq = {s: 1.0 / cnt for s, cnt in strata_counts.items()}

    # G1: population frequency per stratum (used only when proportional_targets=True)
    pop_freq = {s: strata_counts.get(s, 0) / n for s in [1, 2, 3]}

    all_src_idx    = []
    all_tgt_k_idx  = []
    all_tgt_strata = []

    # Group respondents by (CYCLE_YEAR, DDAY_STRATA) for efficient candidate lookup
    # key: (cycle_year, strata) → list of row indices
    strata_groups: dict = {}
    for i in range(n):
        key = (int(cycle_year[i]), int(dday_strata[i]))
        strata_groups.setdefault(key, []).append(i)

    n_no_neighbors = 0

    for src_i in range(n):
        cy     = int(cycle_year[src_i])
        s_obs  = int(dday_strata[src_i])
        target_strata_list = [s for s in [1, 2, 3] if s != s_obs]

        # G1: integer replication counts — proportional to population frequency
        # of each non-observed stratum.  Deterministic: no randomness used.
        # With pop_freq ≈ {WD:0.71, Sat:0.14, Sun:0.15}:
        #   WD source  → Sat:1, Sun:1  (ratio ≈ 1:1, unchanged)
        #   Sat source → WD:5, Sun:1   (ratio ≈ 5:1)
        #   Sun source → WD:5, Sat:1   (ratio ≈ 5:1)
        if proportional_targets:
            target_pop_w = {s: pop_freq.get(s, 0.0) for s in target_strata_list}
            min_w = min(v for v in target_pop_w.values() if v > 0)
            target_n_reps = {s: max(1, round(target_pop_w[s] / min_w))
                             for s in target_strata_list}
        else:
            target_n_reps = {s: 1 for s in target_strata_list}

        for s_tgt in target_strata_list:
            candidates = strata_groups.get((cy, s_tgt), [])
            # Exclude self (shouldn't happen since s_tgt != s_obs, but guard anyway)
            candidates = [j for j in candidates if j != src_i]

            if len(candidates) == 0:
                n_no_neighbors += 1
                # Last-resort fallback: pick from same cycle, any other strata
                fallback = [j for j in range(n)
                            if j != src_i and cycle_year[j] == cy and dday_strata[j] == s_tgt]
                if not fallback:
                    continue
                candidates = fallback

            # Score each candidate
            scores = _score_candidates(
                src_i, candidates, col_arrays, totinc_bin
            )

            # Top-K by score (descending); pad with replacement if fewer than K
            top_k_count = min(K, len(candidates))
            top_indices = np.argsort(scores)[::-1][:top_k_count]
            top_cands   = [candidates[i] for i in top_indices]

            # Pad to exactly K using random draws with replacement from top candidates
            if len(top_cands) < K:
                rng = np.random.default_rng(seed=src_i * 3 + s_tgt)
                extra = rng.choice(top_cands, size=K - len(top_cands), replace=True).tolist()
                top_cands = top_cands + extra

            for _ in range(target_n_reps[s_tgt]):
                all_src_idx.append(src_i)
                all_tgt_k_idx.append(top_cands)
                all_tgt_strata.append(s_tgt)

    if n_no_neighbors > 0:
        print(f"  WARNING: {n_no_neighbors} (src, target_strata) combinations "
              f"had no candidates and were skipped.")

    return {
        "src_idx":       torch.tensor(all_src_idx,   dtype=torch.long),
        "tgt_k_indices": torch.tensor(all_tgt_k_idx, dtype=torch.long),  # (n_pairs, K)
        "tgt_strata":    torch.tensor(all_tgt_strata, dtype=torch.long),
    }


def _score_candidates(
    src_i: int,
    candidates: list,
    col_arrays: dict,
    totinc_bin: np.ndarray,
) -> np.ndarray:
    """
    Score each candidate vs the source respondent.

    Exact match on AGEGRP, SEX, MARSTH, HHSIZE, LFTAG: +1 each (max 5)
    Fuzzy match on PR, CMA, HRSWRK, NOCS, TOTINC (±1 bin): +1 each (max 5)
    """
    n_cands = len(candidates)
    scores  = np.zeros(n_cands, dtype=np.float32)
    cand_arr = np.array(candidates)

    # Exact matches
    for col in EXACT_COLS:
        arr = col_arrays.get(col)
        if arr is None:
            continue
        scores += (arr[cand_arr] == arr[src_i]).astype(np.float32)

    # Fuzzy matches (within ±1 integer bin/code)
    for col in FUZZY_COLS:
        arr = col_arrays.get(col)
        if arr is None:
            continue
        scores += (np.abs(arr[cand_arr] - arr[src_i]) <= 1).astype(np.float32)

    # TOTINC: within ±1 quantile bin
    scores += (np.abs(totinc_bin[cand_arr] - totinc_bin[src_i]) <= 1).astype(np.float32)

    return scores


def inspect_pairs(pairs: dict, meta: pd.DataFrame):
    """Print Test 2 inspection outputs from the testing spec."""
    n_pairs = len(pairs["src_idx"])
    K_actual = pairs["tgt_k_indices"].shape[1]

    print(f"\n  Total pairs: {n_pairs}  (expect ~{2 * len(meta)} for full split)")
    per_strata = Counter(pairs["tgt_strata"].tolist())
    print(f"  Pairs per target strata: {dict(sorted(per_strata.items()))}")

    # Pick first pair for detailed inspection
    src_i  = pairs["src_idx"][0].item()
    k_idxs = pairs["tgt_k_indices"][0].tolist()
    s_tgt  = pairs["tgt_strata"][0].item()
    src    = meta.iloc[src_i]
    tgt    = meta.iloc[k_idxs[0]]

    print(f"\n  === SOURCE RESPONDENT (pair 0) ===")
    print(f"    occID={src['occID']}  CYCLE_YEAR={src['CYCLE_YEAR']}  "
          f"DDAY_STRATA={src['DDAY_STRATA']}(observed)")
    print(f"    AGEGRP={src.get('AGEGRP','?')}  SEX={src.get('SEX','?')}  "
          f"MARSTH={src.get('MARSTH','?')}")

    print(f"\n  === TARGET STRATA: {s_tgt} (K={K_actual} neighbors) ===")
    print(f"    Neighbor occIDs: {[meta.iloc[i]['occID'] for i in k_idxs]}")
    print(f"    Sampled neighbor: occID={tgt['occID']}  "
          f"DDAY_STRATA={tgt['DDAY_STRATA']}  CYCLE_YEAR={tgt['CYCLE_YEAR']}")

    # Exact match score for sampled neighbor
    score = 0
    for col in EXACT_COLS:
        if col in meta.columns and src.get(col) == tgt.get(col):
            score += 1
    print(f"    Exact-match score: {score}/5  (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG)")

    # No self-pairing
    for i in range(min(50, len(pairs["src_idx"]))):
        si = pairs["src_idx"][i].item()
        for ti in pairs["tgt_k_indices"][i].tolist():
            assert si != ti, f"FAIL: self-pairing at pair {i}"
    print("  ✓ No self-pairing in first 50 pairs")

    # Target cycle matches source cycle
    for i in range(min(50, len(pairs["src_idx"]))):
        si = pairs["src_idx"][i].item()
        for ti in pairs["tgt_k_indices"][i].tolist():
            assert meta.iloc[si]["CYCLE_YEAR"] == meta.iloc[ti]["CYCLE_YEAR"], \
                f"FAIL: cross-cycle pair at {i}"
    print("  ✓ All sampled neighbors share CYCLE_YEAR with source (first 50)")

    # Target reuse analysis
    tgt_sampled = [pairs["tgt_k_indices"][i, 0].item()
                   for i in range(len(pairs["src_idx"]))]
    reuse_counts = Counter(tgt_sampled)
    print(f"\n  Unique targets used: {len(reuse_counts)} / {n_pairs} pairs")
    most_reused = reuse_counts.most_common(1)[0]
    print(f"  Most reused target: row {most_reused[0]}  used {most_reused[1]} times")


def main():
    args = parse_args()
    data_dir = os.path.join(
        SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
    )
    output_dir = args.output_dir if args.output_dir else data_dir
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(f"Step 4C — Training Pairs  {'[SAMPLE MODE]' if args.sample else ''}"
          f"{'  [PROPORTIONAL G1]' if args.proportional else ''}")
    print("=" * 60)
    print(f"  data_dir:   {data_dir}")
    print(f"  output_dir: {output_dir}")

    print("\n[1/3] Loading metadata...")
    train_meta = load_metadata(data_dir, "train")
    val_meta   = load_metadata(data_dir, "val")
    print(f"  Train metadata: {train_meta.shape}")
    print(f"  Val metadata:   {val_meta.shape}")
    print(f"  Train DDAY_STRATA distribution: "
          f"{train_meta['DDAY_STRATA'].value_counts().sort_index().to_dict()}")

    print("\n[2/3] Building training pairs (K=5 per source × target strata)...")
    train_pairs = compute_pair_indices(train_meta, "train",
                                       proportional_targets=args.proportional)

    print("\n[3/3] Building validation pairs...")
    val_pairs   = compute_pair_indices(val_meta, "val",
                                       proportional_targets=args.proportional)

    # Test 2 inspection
    print("\n  === TRAINING PAIRS INSPECTION (Test 2) ===")
    inspect_pairs(train_pairs, train_meta)

    # Save
    train_path = os.path.join(output_dir, "training_pairs.pt")
    val_path   = os.path.join(output_dir, "val_pairs.pt")
    torch.save(train_pairs, train_path)
    torch.save(val_pairs,   val_path)
    print(f"\n  Saved {train_path}")
    print(f"  Saved {val_path}")

    # Save strata_inv_freq for DATA_SIDE_SAMPLING in 04D
    strata_counts_train = Counter(train_meta["DDAY_STRATA"].values)
    strata_inv_freq_arr = np.array(
        [1.0 / strata_counts_train.get(s, 1) for s in range(4)], dtype=np.float32
    )
    sif_path = os.path.join(output_dir, "strata_inv_freq.npy")
    np.save(sif_path, strata_inv_freq_arr)
    print(f"  Saved {sif_path}  (strata 0-3: {strata_inv_freq_arr.tolist()})")

    # G1: log obs_home_rate from target diaries to confirm the proportionality shift
    if args.proportional:
        try:
            tensor_path = os.path.join(data_dir, "step4_train.pt")
            td = torch.load(tensor_path, map_location="cpu", weights_only=False)
            tgt_flat = train_pairs["tgt_k_indices"].reshape(-1)  # (n_pairs * K,)
            home_flat = td["aux_seq"][tgt_flat, :, 0].float()    # (n_pairs * K, 48)
            obs_home_rate_g1 = float(home_flat.mean().item())
            print(f"\n  G1 obs_home_rate (mean AT_HOME across target diaries): {obs_home_rate_g1:.4f}")
            print(f"  (baseline uniform-stratum ~0.725; population-weighted target ~0.65)")
            per_strata = Counter(train_pairs["tgt_strata"].tolist())
            total_p = sum(per_strata.values())
            print(f"  G1 target-strata distribution (weighted): "
                  f"{ {s: f'{v/total_p:.3f}' for s, v in sorted(per_strata.items())} }")
        except Exception as e:
            print(f"\n  WARNING: could not compute obs_home_rate: {e}")

    print(f"\n✓ 04C complete.")
    n_src = len(train_meta)
    print(f"  Training pairs: {len(train_pairs['src_idx'])} "
          f"({'proportional' if args.proportional else 'uniform'}, {n_src} respondents)")
    print(f"  Val pairs:      {len(val_pairs['src_idx'])}")


if __name__ == "__main__":
    main()
