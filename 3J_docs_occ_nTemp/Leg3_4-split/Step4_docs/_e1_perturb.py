#!/usr/bin/env python
"""V2-E1 falsifier: build ZERO and SHUFFLE perturbations of the shipped Step-4 pool.

ZERO    -- every ret30_* value set to 0. The literal dead head.
SHUFFLE -- the ret30_* block permuted ACROSS ROWS with a fixed seed. Every marginal is preserved
           exactly (column means, the diurnal shape, the overall rate); all person-level content is
           destroyed. This is the perturbation that separates "the gate measures skill" from "the
           gate measures marginals".

The shipped directory is never written to. Each variant is a full copy, and the support files
fetched from Speed (step4_training_log.csv &c.) are copied in unchanged -- deliberately, because
RW1/RW2 read that log and the whole point is that a pool perturbation cannot reach it.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split"
           r"\Step4_docs\outputs_step4\sweep\seed_3_g3fix_raked3_mindwell_actv")
SUPPORT = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\_e1_from_speed")
OUT = Path(r"C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\_e1_perturbed")
SEED = 20260805


def build(mode: str) -> Path:
    d = OUT / mode
    d.mkdir(parents=True, exist_ok=True)
    for f in SUPPORT.iterdir():
        shutil.copy2(f, d / f.name)
    for name in ("W3_EFFICACY.txt",):
        if (SRC / name).exists():
            shutil.copy2(SRC / name, d / name)

    df = pd.read_csv(SRC / "augmented_diaries.csv", low_memory=False)
    ret = [c for c in df.columns if c.startswith("ret30")]
    if not ret:
        raise SystemExit("[FATAL] no ret30_* columns found -- refusing to write a variant.")
    before_sum = float(df[ret].to_numpy(dtype=float).sum())
    before_means = df[ret].mean().to_numpy(dtype=float)

    if mode == "baseline":
        pass
    elif mode == "zero":
        df[ret] = 0
    elif mode == "shuffle":
        # Permute the retail block across ROWS. UNCONDITIONAL column marginals are invariant by
        # construction; the row-to-person association is destroyed.
        # 🔴 This is BROADER than "destroy person-level skill": RW6/RW7 read rates CONDITIONED on
        # day type and province, and a global permutation destroys those too. Kept because it is
        # informative, but `shuffle_strat` below is the perturbation that isolates the person.
        rng = np.random.default_rng(SEED)
        idx = rng.permutation(len(df))
        df[ret] = df[ret].to_numpy()[idx]
    elif mode == "shuffle_strat":
        # Permute the retail block WITHIN (cycle x day-type-stratum x province) cells. Every
        # conditional marginal RW6/RW7 can read is preserved exactly -- only the association
        # between a retail vector and the PERSON carrying it is destroyed. This is the clean test
        # of "does any retail gate measure person-level skill".
        rng = np.random.default_rng(SEED)
        strat = [c for c in ("CYCLE_YEAR", "DDAY_STRATA", "PR") if c in df.columns]
        block = df[ret].to_numpy().copy()
        pos = np.arange(len(df))
        for _, g in df.groupby(strat, dropna=False):
            gi = pos[df.index.get_indexer(g.index)]
            block[gi] = block[rng.permutation(gi)]
        df[ret] = block
        print(f"           stratified on {strat}, "
              f"{df.groupby(strat, dropna=False).ngroups:,} cells")
    else:
        raise SystemExit(f"[FATAL] unknown mode {mode}")

    after_sum = float(df[ret].to_numpy(dtype=float).sum())
    after_means = df[ret].mean().to_numpy(dtype=float)
    df.to_csv(d / "augmented_diaries.csv", index=False)

    print(f"  [{mode}] rows {len(df):,} · ret30 cols {len(ret)} · "
          f"total mass {before_sum:,.0f} -> {after_sum:,.0f}")
    if mode.startswith("shuffle"):
        drift = float(np.abs(after_means - before_means).max())
        print(f"           max per-column marginal drift = {drift:.3e} "
              f"({'MARGINALS PRESERVED' if drift < 1e-12 else 'MARGINALS MOVED -- perturbation is not clean'})")
        moved = int((df[ret].to_numpy() != pd.read_csv(SRC / 'augmented_diaries.csv',
                                                       usecols=ret, low_memory=False).to_numpy()).any(axis=1).sum())
        print(f"           rows whose retail vector changed = {moved:,} of {len(df):,} "
              f"({100.0 * moved / len(df):.1f} %)")
    return d


if __name__ == "__main__":
    modes = sys.argv[1:] or ["baseline", "zero", "shuffle"]
    for m in modes:
        build(m)
    print("done")
