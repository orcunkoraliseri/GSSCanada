#!/usr/bin/env python
"""V3-J1 -- falsifier for the person-level retail gate (RW9).

Five arms, all in memory.  THE SHIPPED POOL IS NEVER WRITTEN TO.

  F0 control   the pool as it ships                    -- the measurement itself
  F1 shuffle   synthetic vectors permuted within cell  -- MUST FAIL (lift ~ 0)
  F2 zero      synthetic retail deleted                -- MUST FAIL, must not crash
  F3 half      50 % of synthetic rows permuted         -- MUST land between F1 and F0
  F4 copy      synthetic := the person's own observed  -- MUST PASS (positive control)

F1 proves the gate can fail.  F4 proves it can pass.  Without F4 a gate that
always reads ~ 0 is indistinguishable from a broken one -- and that distinction
turned out to be the whole question here, so the positive control is not
ceremony.

Usage:  python falsify_person_retail_gate.py [pool.csv] [n_perm]
Exit code 1 if any required verdict is not met.
"""

import sys
import numpy as np

import person_retail_gate as G

POOL = ("outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv")


def _cell_of_synthetic(df):
    """The null's own cell definition, for the synthetic rows, in df order."""
    obs = df[df.IS_SYNTHETIC == 0]
    syn = df[df.IS_SYNTHETIC == 1]
    import pandas as pd
    pos = pd.Series(np.arange(len(obs)),
                    index=pd.MultiIndex.from_arrays([obs.occID, obs.CYCLE_YEAR]))
    partner = pos.reindex(
        pd.MultiIndex.from_arrays([syn.occID, syn.CYCLE_YEAR])).to_numpy().astype(np.int64)
    stacked = np.column_stack([syn.CYCLE_YEAR.to_numpy(), syn.PR.to_numpy(),
                               syn.DDAY_STRATA.to_numpy(),
                               obs.DDAY_STRATA.to_numpy()[partner]])
    _, cell = np.unique(stacked, axis=0, return_inverse=True)
    return syn.index.to_numpy(), cell, obs.index.to_numpy()[partner]


def arm(df, kind, seed=7):
    """Return a copy of df with the synthetic retail block perturbed."""
    out = df.copy()
    if kind == "control":
        return out
    syn_idx, cell, obs_idx = _cell_of_synthetic(df)
    R = df.loc[syn_idx, G.RET_COLS].to_numpy()
    rng = np.random.default_rng(seed)

    if kind == "zero":
        R = np.zeros_like(R)
    elif kind == "copy":
        R = df.loc[obs_idx, G.RET_COLS].to_numpy()
    elif kind in ("shuffle", "half"):
        order = np.argsort(cell, kind="stable")
        perm = order[np.lexsort((rng.random(cell.size), cell[order]))]
        newR = R.copy()
        if kind == "shuffle":
            newR[order] = R[perm]
        else:
            take = rng.random(order.size) < 0.5
            newR[order[take]] = R[perm[take]]
        R = newR
    else:
        raise ValueError(kind)

    out.loc[syn_idx, G.RET_COLS] = R
    return out


def main():
    pool = sys.argv[1] if len(sys.argv) > 1 else POOL
    n_perm = int(sys.argv[2]) if len(sys.argv) > 2 else G.N_PERM
    print(f"pool    : {pool}")
    print(f"n_perm  : {n_perm}   bands: PASS lift>={G.PASS_LIFT} & z>={G.PASS_Z} · "
          f"WARN lift>={G.WARN_LIFT} · FAIL below   (pre-registered 2026-08-06)\n")

    base = G.load_pool(pool)
    before = base[G.RET_COLS].to_numpy().sum()

    rows = {}
    for kind in ("control", "shuffle", "zero", "half", "copy"):
        r = G.run(pool, n_perm=n_perm, df=arm(base, kind))
        rows[kind] = r
        print(f"{kind:8s} J1a lift {r['a']['lift']:+.4f} z {r['a']['z']:6.1f} "
              f"{r['a_verdict'].upper():4s}   |   J1b lift {r['b']['lift']:+.4f} "
              f"z {r['b']['z']:6.1f} {r['b_verdict'].upper():4s}")

    after = base[G.RET_COLS].to_numpy().sum()
    print(f"\nshipped pool untouched: retail mass {before:,} -> {after:,} "
          f"({'OK' if before == after else 'MUTATED -- ABORT'})")

    checks = []
    c, s, z, h, k = (rows[x] for x in ("control", "shuffle", "zero", "half", "copy"))
    checks.append(("F1 shuffle FAILs on J1a", s["a_verdict"] == "fail"))
    checks.append(("F1 shuffle lift within +/-0.02 of 0",
                   abs(s["a"]["lift"]) < 0.02))
    checks.append(("F2 zero FAILs on both, no exception",
                   z["a_verdict"] == "fail" and z["b_verdict"] == "fail"))
    checks.append(("F2 states WHY rather than printing 0",
                   "UNDEFINED" in z["a_reason"] or "undefined" in z["a_reason"]))
    checks.append(("F3 half lies strictly between F1 and F0",
                   s["a"]["lift"] < h["a"]["lift"] < c["a"]["lift"]))
    checks.append(("F4 copy PASSes on J1a", k["a_verdict"] == "pass"))
    checks.append(("F4 copy lift >= 2.0", k["a"]["lift"] >= 2.0))
    checks.append(("shipped pool not mutated", before == after))

    print()
    ok = True
    for name, good in checks:
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
        ok &= bool(good)
    print(f"\n{sum(g for _, g in checks)}/{len(checks)} required conditions met")

    print("\nF0 control, in full:")
    for lvl, tag, txt in G.format_lines(c):
        print(f"  [{lvl.upper():4s}] {tag} | {txt}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
