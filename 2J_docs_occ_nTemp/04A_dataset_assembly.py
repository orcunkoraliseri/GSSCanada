"""
04A_dataset_assembly.py — Step 4A: Unified Training Dataset Assembly

Merges hetus_30min.csv + copresence_30min.csv, encodes the demographic
conditioning vector (one-hot + continuous + binary), recodes co-presence
from GSS coding (1=Yes, 2=No) to binary (1/0) with a per-slot availability
mask for loss masking, builds the 48-slot × 11-feature token sequences, then
splits respondents 70/15/15 stratified by CYCLE_YEAR × DDAY_STRATA.

Usage:
    python 04A_dataset_assembly.py           # full dataset → outputs_step4/
    python 04A_dataset_assembly.py --sample  # 500-row sample → outputs_step4_test/
"""

import argparse
import json
import os

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Co-presence column order: colleagues is index 8 (masked for 2005/2010) ──
COP_COLS = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
N_SLOTS = 48
N_COP = 9

# CYCLE_YEAR → integer index for learned embedding in model
CYCLE_MAP = {2005: 0, 2010: 1, 2015: 2, 2022: 3}

# One-hot categorical columns in the conditioning vector
CAT_COLS = [
    "AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA",
    "KOL", "LFTAG", "HRSWRK", "NOCS", "COW", "DDAY_STRATA",
]
CONT_COLS = ["TOTINC"]          # standardized continuous
BIN_COLS = ["COLLECT_MODE", "TOTINC_SOURCE"]   # binary flags


# ── Helpers ─────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", action="store_true",
                   help="Use 500-respondent SAMPLE files for local testing")
    return p.parse_args()


def load_data(sample: bool, step3_dir: str):
    suffix = "_SAMPLE" if sample else ""
    hetus = pd.read_csv(
        os.path.join(step3_dir, f"hetus_30min{suffix}.csv"), low_memory=False
    )
    cop = pd.read_csv(
        os.path.join(step3_dir, f"copresence_30min{suffix}.csv"), low_memory=False
    )
    return hetus, cop


def build_cop_avail_and_recode(df: pd.DataFrame):
    """
    Extract co-presence from merged df.
    GSS coding: 1=present, 2=absent, NaN=missing.
    Recode to binary 0/1; build boolean availability mask.

    Returns:
        cop_bin   (n, 48, 9) float32 — recoded binary values
        cop_avail (n, 48, 9) bool    — True where source was non-NaN
    """
    n = len(df)
    cop_arr = np.empty((n, N_SLOTS, N_COP), dtype=np.float64)

    for col_idx, col_name in enumerate(COP_COLS):
        cols = [f"{col_name}30_{s:03d}" for s in range(1, N_SLOTS + 1)]
        cop_arr[:, :, col_idx] = df[cols].values  # NaN propagates automatically

    cop_avail = ~np.isnan(cop_arr)                   # True where not NaN
    cop_bin = np.where(cop_avail, (cop_arr == 1).astype(np.float32), 0.0)

    return cop_bin.astype(np.float32), cop_avail.astype(bool)


def encode_demographics(df: pd.DataFrame, encoders=None, scaler=None):
    """
    Build the pre-computed conditioning vector (all features except CYCLE_YEAR,
    which gets a learned embedding in the model).

    Returns:
        cond_vec     (n, d_cond) float32
        cycle_idx    (n,)        int64
        feat_config  dict — encoding metadata for feature_config.json
        encoders     dict — category→index maps per column
        scaler       fitted StandardScaler for TOTINC
    """
    n = len(df)
    parts = []
    feat_config = {}

    if encoders is None:
        encoders = {}

    # ── One-hot categorical columns ──────────────────────────────────────
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

    # ── Continuous: standardized TOTINC ─────────────────────────────────
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

    # ── Binary flags ────────────────────────────────────────────────────
    for col in BIN_COLS:
        if col in df.columns:
            raw = df[col]
            if raw.dtype == object:
                # String-valued flag (e.g. TOTINC_SOURCE: 'SELF' / 'CRA')
                # → factorize to integer codes 0/1
                vals = pd.factorize(raw.fillna("missing"))[0].astype(np.float32)
            else:
                vals = raw.fillna(0).astype(np.float32).values
        else:
            # Derive from CYCLE_YEAR when column absent
            print(f"  INFO: {col} not in data, deriving from CYCLE_YEAR")
            vals = (df["CYCLE_YEAR"] == 2022).astype(np.float32).values
        parts.append(vals.reshape(-1, 1))
        feat_config[col] = {"type": "binary"}

    cond_vec = np.concatenate(parts, axis=1)

    # CYCLE_YEAR → integer index; kept separate for model's Embedding layer
    cycle_idx = (
        df["CYCLE_YEAR"].map(CYCLE_MAP).fillna(0).astype(np.int64).values
    )

    return cond_vec, cycle_idx, feat_config, encoders, scaler


def split_respondents(df: pd.DataFrame, random_state: int = 42):
    """
    70 / 15 / 15 split stratified by CYCLE_YEAR × DDAY_STRATA.
    Returns three numpy arrays of INTEGER ROW INDICES into df.
    (occID is not unique across cycles, so we split by row position.)
    """
    strat = df["CYCLE_YEAR"].astype(str) + "_" + df["DDAY_STRATA"].astype(str)
    n = len(df)
    row_idx = np.arange(n)

    # Carve out test (15%)
    n_test = int(round(n * 0.15))
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=n_test, random_state=random_state)
    trainval_pos, test_pos = next(sss1.split(row_idx, strat))

    # Carve out val (15% of total) from the remaining pool
    n_val = int(round(n * 0.15))
    trainval_strat = strat.iloc[trainval_pos].reset_index(drop=True)
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=n_val, random_state=random_state)
    train_sub, val_sub = next(sss2.split(trainval_pos, trainval_strat))

    train_row_idx = trainval_pos[train_sub]
    val_row_idx   = trainval_pos[val_sub]
    test_row_idx  = test_pos
    return train_row_idx, val_row_idx, test_row_idx


def pack_tensors(sub_df, act_seq, home_seq, cop_bin, cop_avail, cond_vec, cycle_idx):
    """Bundle selected rows into a dict of PyTorch tensors."""
    # aux_seq = [AT_HOME | 9 co-pres]: shape (n, 48, 10)
    aux_seq = np.concatenate([home_seq[:, :, np.newaxis], cop_bin], axis=2)

    return {
        "act_seq":    torch.tensor(act_seq,   dtype=torch.long),       # (n, 48) 0-indexed
        "aux_seq":    torch.tensor(aux_seq,   dtype=torch.float32),    # (n, 48, 10)
        "cop_avail":  torch.tensor(cop_avail, dtype=torch.bool),       # (n, 48, 9)
        "cond_vec":   torch.tensor(cond_vec,  dtype=torch.float32),    # (n, d_cond)
        "cycle_idx":  torch.tensor(cycle_idx, dtype=torch.long),       # (n,)
        "cycle_year": torch.tensor(sub_df["CYCLE_YEAR"].values, dtype=torch.long),
        "obs_strata": torch.tensor(sub_df["DDAY_STRATA"].values, dtype=torch.long),
        "wght_per":   torch.tensor(sub_df["WGHT_PER"].fillna(1.0).values, dtype=torch.float32),
        "occ_ids":    torch.tensor(sub_df["occID"].fillna(0).astype(np.int64).values, dtype=torch.long),
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    step3_dir = os.path.join(SCRIPT_DIR, "outputs_step3")
    out_dir = os.path.join(
        SCRIPT_DIR, "outputs_step4_test" if args.sample else "outputs_step4"
    )
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print(f"Step 4A — Dataset Assembly  {'[SAMPLE MODE]' if args.sample else ''}")
    print("=" * 60)

    # ── Load ────────────────────────────────────────────────────────────
    print("\n[1/6] Loading data...")
    hetus, cop = load_data(args.sample, step3_dir)
    print(f"  hetus_30min:      {hetus.shape}")
    print(f"  copresence_30min: {cop.shape}")

    # ── A1: Merge (positional concat) ───────────────────────────────────
    # occID is NOT unique within each file — the same PUMFID (respondent ID)
    # appears across multiple GSS cycles.  The unique row key is (occID, CYCLE_YEAR).
    # Both files are in the same row order (confirmed by element-wise occID check),
    # so we join positionally rather than via a keyed merge.
    print("\n[2/6] Joining hetus + copresence (positional, same row order)...")
    assert len(hetus) == len(cop), (
        f"Row count mismatch: hetus={len(hetus)}, cop={len(cop)}"
    )
    assert (hetus["occID"].values == cop["occID"].values).all(), (
        "occID order mismatch between hetus_30min and copresence_30min"
    )
    cop_slot_cols = [
        f"{ch}30_{s:03d}"
        for ch in COP_COLS
        for s in range(1, N_SLOTS + 1)
    ]
    missing = [c for c in cop_slot_cols if c not in cop.columns]
    assert not missing, (
        f"copresence_30min.csv is missing {len(missing)} of {len(cop_slot_cols)} "
        f"expected slot columns (e.g. {missing[:3]}). "
        f"File appears wrong — regenerate via 03_mergingGSS.py Phase I."
    )
    df = pd.concat(
        [hetus.reset_index(drop=True),
         cop[cop_slot_cols].reset_index(drop=True)],
        axis=1,
    )

    # Test 1a — merge shape
    print(f"  Merged shape: {df.shape}")
    print(f"  Unique occIDs: {df['occID'].nunique()}")
    print(f"  Unique (occID, CYCLE_YEAR): {df.groupby(['occID', 'CYCLE_YEAR']).ngroups}")
    if not args.sample:
        assert len(df) == 64061, f"Expected 64061, got {len(df)}"
    print(df.head(3).to_string())

    # ── A2: Demographic conditioning vector ─────────────────────────────
    print("\n[3/6] Encoding demographics...")
    cond_vec, cycle_idx, feat_config, encoders, scaler = encode_demographics(df)

    # Test 1b — conditioning vector for respondent 0
    row = df.iloc[0]
    print("\n  === RAW DEMOGRAPHICS (respondent 0) ===")
    for col in ["AGEGRP", "SEX", "MARSTH", "HHSIZE", "PR", "CMA", "KOL",
                "LFTAG", "TOTINC", "HRSWRK", "NOCS", "COW",
                "DDAY_STRATA", "SURVYEAR", "COLLECT_MODE", "TOTINC_SOURCE"]:
        print(f"  {col:>16}: {row.get(col, 'N/A')}")

    d_cond = cond_vec.shape[1]
    print(f"\n  Conditioning vector shape: ({len(df)}, {d_cond})")
    print(f"  Non-zero entries (row 0): {(cond_vec[0] != 0).sum()}")
    print(f"  First 20 values (row 0): {cond_vec[0, :20].tolist()}")
    print(f"  Total conditioning dim (d_cond, excludes CYCLE_YEAR): {d_cond}")

    # ── A3: Sequence token construction ─────────────────────────────────
    print("\n[4/6] Building sequence tokens...")

    # Activity: stored as 0-indexed (0–13) for embedding lookup
    act_cols = [f"act30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    act_seq = df[act_cols].values.astype(np.int64) - 1  # (n, 48)

    # AT_HOME: already binary 0/1 from Step 3
    hom_cols = [f"hom30_{s:03d}" for s in range(1, N_SLOTS + 1)]
    home_seq = df[hom_cols].values.astype(np.float32)   # (n, 48)

    # Co-presence: recode + availability mask
    cop_bin, cop_avail = build_cop_avail_and_recode(df)

    # Test 1c — slot 1 token for respondent 0
    row = df.iloc[0]
    print("\n  === SLOT 1 TOKEN (respondent 0) ===")
    print(f"    occACT (raw): {row['act30_001']}  → stored as {act_seq[0, 0]} (0-indexed)")
    print(f"    AT_HOME:      {row['hom30_001']}")
    for ci, cn in enumerate(COP_COLS):
        raw_v = row.get(f"{cn}30_001")
        print(f"    {cn:>12}: raw={raw_v}  → {cop_bin[0, 0, ci]:.0f}  "
              f"(avail={cop_avail[0, 0, ci]})")

    # Test 1d — full sequence tensor
    print(f"\n  === FULL SEQUENCE TENSOR ===")
    print(f"    act_seq shape:  {act_seq.shape}")    # (n, 48)
    print(f"    home_seq shape: {home_seq.shape}")   # (n, 48)
    print(f"    cop_bin shape:  {cop_bin.shape}")    # (n, 48, 9)
    print(f"    Activity seq (row 0): {act_seq[0].tolist()}")
    print(f"    AT_HOME   seq (row 0): {home_seq[0].tolist()}")

    # Test 1e — NaN rates per cycle
    print("\n  === CO-PRESENCE AVAILABILITY BY CYCLE ===")
    for cy in [2005, 2010, 2015, 2022]:
        mask = df["CYCLE_YEAR"].values == cy
        if not mask.any():
            continue
        prim8_avail = cop_avail[mask, :, :8].mean() * 100
        col_avail   = cop_avail[mask, :, 8].mean() * 100
        print(f"    {cy}: primary 8 NaN={100 - prim8_avail:.1f}%  |  "
              f"colleagues NaN={100 - col_avail:.1f}%")

    print(f"  cop_avail shape: {cop_avail.shape}")
    print(f"  cop_avail True (available) rate overall: {cop_avail.mean():.3f}")

    # Validate: colleagues must be 0 for all 2005/2010 rows
    old_mask = np.isin(df["CYCLE_YEAR"].values, [2005, 2010])
    assert cop_bin[old_mask, :, 8].sum() == 0, \
        "BUG: colleagues is non-zero for 2005/2010 rows"
    print("  ✓ colleagues = 0 for all 2005/2010 rows (mask check passed)")

    # All non-NaN co-presence values should be 0 or 1 after recoding
    available_vals = cop_bin[cop_avail]
    assert set(np.unique(available_vals)).issubset({0.0, 1.0}), \
        "BUG: recoded co-presence contains values outside {0, 1}"
    print("  ✓ All non-NaN co-presence values ∈ {0, 1} after recoding")

    # ── A4: Train / val / test split ───────────────────────────────────
    print("\n[5/6] Splitting train / val / test (70/15/15 stratified)...")
    # Returns row index arrays (not occIDs — occID is not unique across cycles)
    train_idx, val_idx, test_idx = split_respondents(df)

    assert len(np.intersect1d(train_idx, val_idx))  == 0, "LEAK: train ∩ val"
    assert len(np.intersect1d(train_idx, test_idx)) == 0, "LEAK: train ∩ test"
    assert len(np.intersect1d(val_idx,   test_idx)) == 0, "LEAK: val ∩ test"

    # Test 1f — split sizes and stratum distributions
    print(f"  Train: {len(train_idx)} | Val: {len(val_idx)} | Test: {len(test_idx)}")
    for name, row_idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
        sub = df.iloc[row_idx]
        strata = sub["DDAY_STRATA"].value_counts().sort_index().to_dict()
        cycles = sub["CYCLE_YEAR"].value_counts().sort_index().to_dict()
        print(f"  {name}  DDAY_STRATA:{strata}  CYCLE_YEAR:{cycles}")

    # ── Class frequencies for F3 sweep (training split only) ───────────
    # 7 usable COP channels (skip otherInFAMs=4 and otherHHs=5)
    COP7_INDICES = [0, 1, 2, 3, 6, 7, 8]
    COP7_NAMES   = ["Alone", "Spouse", "Children", "parents", "friends", "others", "colleagues"]
    cop_pos_weights = {}
    for name, ci in zip(COP7_NAMES, COP7_INDICES):
        avail_mask = cop_avail[train_idx, :, ci]
        vals = cop_bin[train_idx, :, ci][avail_mask]
        freq = float(vals.mean()) if len(vals) > 0 else 0.5
        pw = (1.0 - freq) / max(freq, 1e-9)
        assert pw > 1.0, f"{name} pos_weight={pw:.4f} ≤ 1 (freq={freq:.4f}) — sign-flip guard"
        cop_pos_weights[name] = round(pw, 6)
    act_train_flat = act_seq[train_idx].flatten()
    act_counts_arr = np.bincount(act_train_flat, minlength=14).astype(float)
    act_class_freqs = [round(v, 6) for v in (act_counts_arr / act_counts_arr.sum()).tolist()]
    print(f"\n  COP pos_weights (7-way): { {k: f'{v:.4f}' for k, v in cop_pos_weights.items()} }")
    print(f"  Activity class freqs (14-way): {[f'{v:.4f}' for v in act_class_freqs]}")

    # ── Save datasets ───────────────────────────────────────────────────
    print("\n[6/6] Saving tensor datasets...")

    # Metadata columns needed by 04C for demographic matching
    meta_cols = ["occID", "CYCLE_YEAR", "DDAY_STRATA", "AGEGRP", "SEX",
                 "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA",
                 "HRSWRK", "NOCS", "TOTINC", "WGHT_PER"]
    meta_cols = [c for c in meta_cols if c in df.columns]

    for split_name, row_idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
        sub_df  = df.iloc[row_idx].reset_index(drop=True)

        tensors = pack_tensors(
            sub_df,
            act_seq[row_idx], home_seq[row_idx],
            cop_bin[row_idx], cop_avail[row_idx],
            cond_vec[row_idx], cycle_idx[row_idx],
        )
        pt_path = os.path.join(out_dir, f"step4_{split_name}.pt")
        torch.save(tensors, pt_path)
        print(f"  Saved {pt_path}  (n={len(sub_df)})")

        # Metadata CSVs — used by 04C (train) and 04E (all splits)
        sub_df[meta_cols].to_csv(
            os.path.join(out_dir, f"step4_{split_name}_meta.csv"), index=False
        )

    # Full metadata for 04E inference (all respondents)
    all_meta_cols = ["occID", "CYCLE_YEAR", "SURVYEAR", "DDAY_STRATA",
                     "AGEGRP", "SEX", "MARSTH", "HHSIZE", "LFTAG", "PR", "CMA",
                     "HRSWRK", "NOCS", "TOTINC", "WGHT_PER", "COLLECT_MODE"]
    all_meta_cols = [c for c in all_meta_cols if c in df.columns]
    df[all_meta_cols].to_csv(os.path.join(out_dir, "step4_all_meta.csv"), index=False)

    # Save feature_config.json
    feature_config = {
        "d_cond":              int(d_cond),
        "n_activity_classes":  14,
        "n_copresence":        9,
        "n_slots":             48,
        "cycle_map":           CYCLE_MAP,
        "cop_col_names":       COP_COLS,
        "feature_parts":       feat_config,
        "split_sizes": {
            "train": int(len(train_idx)),
            "val":   int(len(val_idx)),
            "test":  int(len(test_idx)),
        },
        "cop_pos_weights":  cop_pos_weights,
        "act_class_freqs":  act_class_freqs,
    }
    cfg_path = os.path.join(out_dir, "step4_feature_config.json")
    with open(cfg_path, "w") as f:
        json.dump(feature_config, f, indent=2)
    print(f"  Saved {cfg_path}")

    print(f"\n✓ 04A complete.")
    print(f"  d_cond = {d_cond}  (one-hot + continuous + binary; CYCLE_YEAR excluded)")
    print(f"  Output dir: {out_dir}")


if __name__ == "__main__":
    main()
