"""
04A_sample_assembly.py — Step 4A-sample: Stratified Sub-Sampler over an existing
G2-format tensor bundle. Phase 6 Stage A/B infrastructure.

Reads outputs_step4_G2/ (or any G2-schema dir), draws a stratified slice keyed by
CYCLE_YEAR × DDAY_STRATA × HHSIZE, enforces a per-rare-cop-channel-per-stratum
floor, and writes a byte-compatible G2 bundle to outputs_step4_G2_sample<N>/
ready for 04C_training_pairs.py --sample_dir and 04D_train.py --data_dir.

Stage A:  --frac 0.02  -> outputs_step4_G2_sample2/   (~3000 respondents)
Stage B:  --frac 0.20  -> outputs_step4_G2_sample20/  (~30000 respondents)

Seed=42 frozen across cycles so Stage A ⊂ Stage B ⊂ G2 (nested subsamples; not
required by the plan, but it's free and helps narrative continuity if Stage B
needs to debug Stage A surprises).

Usage:
    python 04A_sample_assembly.py --src outputs_step4_G2 --frac 0.02
    python 04A_sample_assembly.py --src outputs_step4_G2 --frac 0.20 \
        --out outputs_step4_G2_sample20
"""

import argparse
import json
import os
import shutil
import sys
from collections import Counter

import numpy as np
import pandas as pd
import torch

# Windows console (cp1252) chokes on unicode in print statements; on Linux/cluster
# this is a no-op. Wrap in try/except so script still runs under environments that
# don't expose reconfigure (Python <3.7 / piped output / Jupyter).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

COP_NAMES = [
    "Alone", "Spouse", "Children", "parents", "otherInFAMs",
    "otherHHs", "friends", "others", "colleagues",
]
RARE_COP_INDICES = [3, 4, 6, 7, 8]   # parents, otherInFAMs, friends, others, colleagues
RARE_COP_NAMES   = [COP_NAMES[i] for i in RARE_COP_INDICES]
MIN_PER_RARE_CELL = 200              # spec floor: ≥200 respondents per rare-cop × stratum


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="outputs_step4_G2",
                   help="Source G2-format directory (relative to script dir or absolute)")
    p.add_argument("--out", default=None,
                   help="Output directory. Default: outputs_step4_G2_sample<pct>")
    p.add_argument("--frac", type=float, default=0.02,
                   help="Sample fraction of TRAIN respondents (e.g. 0.02 for 2%)")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _stratify_keys(meta: pd.DataFrame) -> np.ndarray:
    """Compose CYCLE_YEAR × DDAY_STRATA × HHSIZE strata key."""
    cy = meta["CYCLE_YEAR"].astype(int).astype(str)
    ds = meta["DDAY_STRATA"].astype(int).astype(str)
    hh = meta["HHSIZE"].fillna(-1).astype(int).astype(str)
    return (cy + "_" + ds + "_" + hh).values


def _draw_stratified(meta: pd.DataFrame, frac: float, seed: int) -> np.ndarray:
    """Stratified sample of integer row indices into meta. Returns sorted unique idx."""
    rng = np.random.default_rng(seed)
    keys = _stratify_keys(meta)
    out = []
    for k in np.unique(keys):
        cell_idx = np.where(keys == k)[0]
        n_cell = len(cell_idx)
        n_pick = max(1, int(round(n_cell * frac)))
        n_pick = min(n_pick, n_cell)
        picked = rng.choice(cell_idx, size=n_pick, replace=False)
        out.append(picked)
    return np.sort(np.concatenate(out))


def _enforce_rare_cop_floor(
    meta: pd.DataFrame,
    cop_bin: np.ndarray,        # (n, 48, 9)
    cop_avail: np.ndarray,      # (n, 48, 9)
    sel: np.ndarray,            # currently selected indices (1-D int)
    seed: int,
) -> np.ndarray:
    """
    For each (DDAY_STRATA, rare-cop-channel) cell, ensure ≥MIN_PER_RARE_CELL
    respondents in `sel` have at least one slot where the channel is observed
    AND positive. Top up by drawing from the full population (deduplicated).
    """
    rng = np.random.default_rng(seed + 1)
    sel = set(int(i) for i in sel)
    n_total = len(meta)
    dds = meta["DDAY_STRATA"].astype(int).values
    # Per-respondent boolean: "did this respondent ever have channel c observed=1?"
    ever_pos = (cop_bin * cop_avail).any(axis=1)   # (n, 9)

    for c, name in zip(RARE_COP_INDICES, RARE_COP_NAMES):
        for s in [1, 2, 3]:
            stratum_mask = dds == s
            in_cell_pos = ever_pos[:, c] & stratum_mask
            cur = sum(1 for i in np.where(in_cell_pos)[0] if int(i) in sel)
            if cur >= MIN_PER_RARE_CELL:
                continue
            shortfall = MIN_PER_RARE_CELL - cur
            pool = [int(i) for i in np.where(in_cell_pos)[0] if int(i) not in sel]
            if len(pool) <= shortfall:
                add = pool
            else:
                add = rng.choice(pool, size=shortfall, replace=False).tolist()
            if len(add) < shortfall:
                print(f"  WARN: rare-cop floor unmet for {name} × stratum {s} — "
                      f"have {cur + len(add)}, want {MIN_PER_RARE_CELL} (pool exhausted)")
            sel.update(int(i) for i in add)
    return np.array(sorted(sel), dtype=np.int64)


def _load_split(src_dir: str, split: str):
    tensors = torch.load(
        os.path.join(src_dir, f"step4_{split}.pt"),
        map_location="cpu", weights_only=False,
    )
    meta = pd.read_csv(os.path.join(src_dir, f"step4_{split}_meta.csv"), low_memory=False)
    return tensors, meta


def _slice_tensors(tensors: dict, idx: np.ndarray) -> dict:
    """Slice every (n, ...) tensor in the bundle by the given row indices."""
    out = {}
    idx_t = torch.from_numpy(idx).long()
    n = next(iter(tensors.values())).shape[0]
    for k, v in tensors.items():
        if not isinstance(v, torch.Tensor):
            out[k] = v
            continue
        if v.shape[0] != n:
            out[k] = v   # not a per-respondent tensor (e.g. metadata buffers)
            continue
        out[k] = v[idx_t]
    return out


def _compute_cop_pos_weights(cop_bin: np.ndarray, cop_avail: np.ndarray) -> dict:
    """Mirror 04A_dataset_assembly.py cop_pos_weights logic on the sampled train slice."""
    COP7_INDICES = [0, 1, 2, 3, 6, 7, 8]
    COP7_NAMES   = ["Alone", "Spouse", "Children", "parents", "friends", "others", "colleagues"]
    out = {}
    for name, ci in zip(COP7_NAMES, COP7_INDICES):
        avail = cop_avail[:, :, ci]
        vals  = cop_bin[:, :, ci][avail]
        freq  = float(vals.mean()) if len(vals) > 0 else 0.5
        pw    = (1.0 - freq) / max(freq, 1e-9)
        out[name] = round(max(pw, 1.0 + 1e-3), 6)   # clamp ≥1 to keep training assert happy
    return out


def main():
    args = parse_args()

    src_dir = args.src if os.path.isabs(args.src) else os.path.join(SCRIPT_DIR, args.src)
    if not os.path.isdir(src_dir):
        raise FileNotFoundError(f"Source dir not found: {src_dir}")

    out_dir = args.out
    if out_dir is None:
        pct = int(round(args.frac * 100))
        out_dir = os.path.join(SCRIPT_DIR, f"outputs_step4_G2_sample{pct}")
    elif not os.path.isabs(out_dir):
        out_dir = os.path.join(SCRIPT_DIR, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 60)
    print(f"Step 4A-sample — Stratified Sub-Sampler (frac={args.frac})")
    print("=" * 60)
    print(f"  src: {src_dir}")
    print(f"  out: {out_dir}")
    print(f"  seed: {args.seed}")

    # ── Train ────────────────────────────────────────────────────────────
    print("\n[1/4] Sampling train split (stratified by CYCLE × DDAY_STRATA × HHSIZE)...")
    train_t, train_m = _load_split(src_dir, "train")
    n_train_full = len(train_m)
    print(f"  Source train: {n_train_full} respondents")

    sel = _draw_stratified(train_m, args.frac, args.seed)
    print(f"  Initial stratified pick: {len(sel)} respondents")

    cop_bin   = train_t["aux_seq"][:, :, 1:].numpy()           # (n, 48, 9)
    cop_avail = train_t["cop_avail"].numpy()                    # (n, 48, 9)
    sel = _enforce_rare_cop_floor(train_m, cop_bin, cop_avail, sel, args.seed)
    print(f"  After rare-cop floor enforcement: {len(sel)} respondents")
    print(f"  Effective frac: {len(sel) / n_train_full:.4f}")

    train_t_sub = _slice_tensors(train_t, sel)
    train_m_sub = train_m.iloc[sel].reset_index(drop=True)

    # ── Val + Test ───────────────────────────────────────────────────────
    # Use the same frac on val and test; no rare-cop floor (val/test are not used
    # for K=5 pair construction, only for held-out scoring).
    print("\n[2/4] Sampling val split (proportional, no floor)...")
    val_t, val_m = _load_split(src_dir, "val")
    val_sel = _draw_stratified(val_m, args.frac, args.seed)
    print(f"  Val: {len(val_m)} -> {len(val_sel)} respondents")
    val_t_sub = _slice_tensors(val_t, val_sel)
    val_m_sub = val_m.iloc[val_sel].reset_index(drop=True)

    print("\n[3/4] Sampling test split (proportional, no floor)...")
    test_t, test_m = _load_split(src_dir, "test")
    test_sel = _draw_stratified(test_m, args.frac, args.seed)
    print(f"  Test: {len(test_m)} -> {len(test_sel)} respondents")
    test_t_sub = _slice_tensors(test_t, test_sel)
    test_m_sub = test_m.iloc[test_sel].reset_index(drop=True)

    # ── Write G2-compatible bundle ───────────────────────────────────────
    print("\n[4/4] Writing G2-format bundle to output dir...")

    torch.save(train_t_sub, os.path.join(out_dir, "step4_train.pt"))
    torch.save(val_t_sub,   os.path.join(out_dir, "step4_val.pt"))
    torch.save(test_t_sub,  os.path.join(out_dir, "step4_test.pt"))
    train_m_sub.to_csv(os.path.join(out_dir, "step4_train_meta.csv"), index=False)
    val_m_sub.to_csv(os.path.join(out_dir, "step4_val_meta.csv"), index=False)
    test_m_sub.to_csv(os.path.join(out_dir, "step4_test_meta.csv"), index=False)
    print(f"  Saved {os.path.join(out_dir, 'step4_train.pt')}")
    print(f"  Saved {os.path.join(out_dir, 'step4_val.pt')}")
    print(f"  Saved {os.path.join(out_dir, 'step4_test.pt')}")

    # ── Rebuild step4_all_meta.csv from the three sampled splits ─────────
    src_all_meta_path = os.path.join(src_dir, "step4_all_meta.csv")
    if os.path.isfile(src_all_meta_path):
        src_all_meta = pd.read_csv(src_all_meta_path, low_memory=False)
        keep = pd.concat(
            [train_m_sub[["occID", "CYCLE_YEAR"]],
             val_m_sub[["occID", "CYCLE_YEAR"]],
             test_m_sub[["occID", "CYCLE_YEAR"]]],
            ignore_index=True,
        ).drop_duplicates()
        all_meta_sub = src_all_meta.merge(keep, on=["occID", "CYCLE_YEAR"], how="inner")
        all_meta_sub.to_csv(os.path.join(out_dir, "step4_all_meta.csv"), index=False)
        print(f"  Saved {os.path.join(out_dir, 'step4_all_meta.csv')} ({len(all_meta_sub)} rows)")
    else:
        print(f"  WARN: source has no step4_all_meta.csv — skipping")

    # ── Recompute feature_config (cop_pos_weights + act_class_freqs use sample) ──
    src_cfg_path = os.path.join(src_dir, "step4_feature_config.json")
    with open(src_cfg_path) as f:
        feat_cfg = json.load(f)

    new_cop_bin   = train_t_sub["aux_seq"][:, :, 1:].numpy()
    new_cop_avail = train_t_sub["cop_avail"].numpy()
    feat_cfg["cop_pos_weights"] = _compute_cop_pos_weights(new_cop_bin, new_cop_avail)

    act_flat = train_t_sub["act_seq"].numpy().flatten()
    act_counts = np.bincount(act_flat, minlength=14).astype(float)
    feat_cfg["act_class_freqs"] = [round(v, 6) for v in (act_counts / act_counts.sum()).tolist()]
    feat_cfg["split_sizes"] = {
        "train": int(len(train_m_sub)),
        "val":   int(len(val_m_sub)),
        "test":  int(len(test_m_sub)),
    }
    feat_cfg["sample_frac"]      = float(args.frac)
    feat_cfg["sample_seed"]      = int(args.seed)
    feat_cfg["sample_source"]    = os.path.basename(src_dir.rstrip(os.sep))

    out_cfg_path = os.path.join(out_dir, "step4_feature_config.json")
    with open(out_cfg_path, "w") as f:
        json.dump(feat_cfg, f, indent=2)
    print(f"  Saved {out_cfg_path}")

    # ── Per-rare-cop-cell coverage report (for paper / progress log) ─────
    print("\n  === RARE COP COVERAGE (sampled train) ===")
    dds_sub = train_m_sub["DDAY_STRATA"].astype(int).values
    ever_pos_sub = (new_cop_bin * new_cop_avail).any(axis=1)   # (n_sample, 9)
    for c, name in zip(RARE_COP_INDICES, RARE_COP_NAMES):
        line = f"  {name:>14}:"
        for s in [1, 2, 3]:
            cnt = int(((dds_sub == s) & ever_pos_sub[:, c]).sum())
            mark = "✓" if cnt >= MIN_PER_RARE_CELL else "!"
            line += f"  s{s}={cnt:>4} {mark}"
        print(line)

    # ── strata_inv_freq.npy mirror (used by 04D DATA_SIDE_SAMPLING path) ─
    strata_counts_train = Counter(train_m_sub["DDAY_STRATA"].astype(int).values)
    sif = np.array(
        [1.0 / max(strata_counts_train.get(s, 1), 1) for s in range(4)],
        dtype=np.float32,
    )
    np.save(os.path.join(out_dir, "strata_inv_freq.npy"), sif)

    print(f"\n✓ 04A_sample_assembly complete. Next step:")
    print(f"  python 04C_training_pairs.py --sample_dir {os.path.relpath(out_dir, SCRIPT_DIR)}")


if __name__ == "__main__":
    main()
