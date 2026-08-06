#!/usr/bin/env python
"""V2-E2 -- the ROW-MATCHED REG-1 / REG-2 comparison the gates claim to be (finding C-2).

`3rdJ_04_augmentationGSS_4split_val.py:1749-1766` says outright that REG-1/REG-2 are a PROXY: they
compute JS between the two legs' synthetic distributions **aggregated per (cycle x stratum)**,
because the frozen validation split "isn't persisted anywhere reachable". This script computes the
same two quantities **per respondent** and reports both side by side.

WHAT IS MATCHED, AND WHY IT IS NOT THE VALIDATION SPLIT
-------------------------------------------------------
The frozen-split comparison remains impossible and V2-D5 did not change that. Leg-3's split IS
persisted (`step4_val_meta.csv`, 9,609 rows); **Leg-2's was never persisted for the shipped run** --
the only Leg-2 `step4_val_meta.csv` in the repo has 192 rows and its `step4_all_meta.csv` has 1,280,
against Leg-3's 64,061, so that directory is a development run. Intersecting the two val splits
yields 26 keys, 0.27 % of Leg-3's, which is exactly the condition V2-E2's test method calls
disqualifying.

What IS total is the pool match: both legs ship 192,183-row `augmented_diaries.csv` files whose
synthetic rows carry the same 64,061 `(occID, CYCLE_YEAR)` keys, intersection 1.0000 of both. So this
runs on the FULL SYNTHETIC POOL and says so in its output. The substitution is the finding, not a
detail.

READ THE CONTROL BEFORE READING THE NUMBER
-------------------------------------------
A large per-respondent JS is the EXPECTED behaviour of two stochastic generators and on its own says
nothing about drift. So `--control` takes a second pool from the SAME leg and computes the identical
row-matched statistic. Cross-leg is only evidence of regression insofar as it exceeds within-leg.
Reporting the cross-leg number alone would be a gate whose counterfactual was never checked -- the
failure mode this project has catalogued repeatedly.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["occID", "CYCLE_YEAR"]
PROXY = {"REG-1": 0.00003, "REG-2": 0.00008}
BAR = 0.002


def js_rows(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Jensen-Shannon divergence in BITS, row-wise, on two stacks of pseudo-distributions.

    Rows are normalised to sum 1. A row whose mass is zero in either stack yields NaN rather than a
    fabricated 0.0 -- a divergence that cannot be computed must not be reported as perfect agreement.
    This is the `silence is a failure mode` rule: a reader returning 0.0 for what it cannot parse
    blames the system under test for its own gap.
    """
    P = np.asarray(P, dtype=float)
    Q = np.asarray(Q, dtype=float)
    P = np.where(np.isfinite(P), P, 0.0)
    Q = np.where(np.isfinite(Q), Q, 0.0)
    sp, sq = P.sum(axis=1), Q.sum(axis=1)
    ok = (sp > 0) & (sq > 0)
    out = np.full(P.shape[0], np.nan)
    if not ok.any():
        return out
    p = P[ok] / sp[ok, None]
    q = Q[ok] / sq[ok, None]
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_pm = np.nansum(np.where(p > 0, p * np.log2(p / m), 0.0), axis=1)
        kl_qm = np.nansum(np.where(q > 0, q * np.log2(q / m), 0.0), axis=1)
    out[ok] = 0.5 * (kl_pm + kl_qm)
    return out


def categorical_agreement(m: pd.DataFrame, cols: list[str], label: str) -> dict:
    """The comparison REG-2 CANNOT make, and the reason it cannot make it.

    JS divergence is undefined when either side has zero mass, so a respondent whom one leg gives a
    working day and the other gives none is DROPPED from the average rather than counted as maximal
    disagreement. That is not a rounding detail: it removes exactly the rows where the two legs
    disagree most, and leaves the mean to be computed on the subset where they already agree
    qualitatively. So the work / no-work status is compared as a plain 2x2 table.

    Reported against TWO references, because the raw disagreement rate alone is not interpretable:
      * independence  -- what two UNCORRELATED samples with these marginals would disagree at.
                         Two independent draws from a stochastic generator disagree a LOT; if the
                         observed rate is at or below this, the legs are no worse than resampling.
      * Cohen's kappa -- agreement above chance, on the same 2x2.
    """
    a = (m[[f"{c}_a" for c in cols]].to_numpy().sum(axis=1) > 0).astype(int)
    b = (m[[f"{c}_b" for c in cols]].to_numpy().sum(axis=1) > 0).astype(int)
    n = len(a)
    n11 = int(((a == 1) & (b == 1)).sum())
    n10 = int(((a == 1) & (b == 0)).sum())
    n01 = int(((a == 0) & (b == 1)).sum())
    n00 = int(((a == 0) & (b == 0)).sum())
    dis = n10 + n01
    pa, pb = a.mean(), b.mean()
    exp_dis = pa * (1 - pb) + pb * (1 - pa)
    po = (n11 + n00) / n
    pe = (1 - pa) * (1 - pb) + pa * pb
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    print(f"  categorical work/no-work, {label}:")
    print(f"    both work {n11:,} · only A {n10:,} · only B {n01:,} · neither {n00:,}")
    print(f"    DISAGREE {dis:,} of {n:,} = {100.0 * dis / n:.2f} %   "
          f"(net marginal difference only {abs(n10 - n01):,} = {100.0 * abs(n10 - n01) / n:.2f} %, "
          f"so aggregation cancels {100.0 * (1 - abs(n10 - n01) / dis):.1f} % of it)")
    print(f"    reference: two INDEPENDENT samples with these marginals would disagree at "
          f"{100.0 * exp_dis:.2f} %  ->  observed is "
          f"{'BETTER (more agreement than chance)' if dis / n < exp_dis else 'WORSE than chance'}")
    print(f"    Cohen's kappa = {kappa:.4f}")
    return dict(n=n, disagree=dis, rate=dis / n, indep=exp_dis, kappa=kappa,
                n11=n11, n10=n10, n01=n01, n00=n00)


def load_pool(path: Path, cols: list[str]) -> pd.DataFrame:
    have = set(pd.read_csv(path, nrows=0).columns)
    want = [c for c in cols if c in have]
    miss = [c for c in cols if c not in have]
    if miss:
        print(f"  [WARN] {path.name}: {len(miss)} requested column(s) absent, e.g. {miss[:4]}")
    df = pd.read_csv(path, usecols=want, low_memory=False)
    if "IS_SYNTHETIC" in df.columns:
        df = df[df["IS_SYNTHETIC"] == 1]
    return df


def collapse(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """One row per respondent key. Multiple synthetic rows per key are averaged."""
    return df.groupby(KEY, as_index=False)[cols].mean()


def compare(a_path: Path, b_path: Path, act_cols: list[str], wrk_cols: list[str],
            label: str) -> dict:
    need = KEY + ["IS_SYNTHETIC"] + act_cols + wrk_cols
    A, B = load_pool(a_path, need), load_pool(b_path, need)
    ac = [c for c in act_cols if c in A.columns and c in B.columns]
    wc = [c for c in wrk_cols if c in A.columns and c in B.columns]
    if not ac and not wc:
        raise SystemExit(f"[FATAL] {label}: no shared activity or wrk30 columns between the pools.")
    A, B = collapse(A, ac + wc), collapse(B, ac + wc)
    m = A.merge(B, on=KEY, suffixes=("_a", "_b"))
    ka, kb = len(A), len(B)
    print(f"\n--- {label} ---")
    print(f"  keys: A {ka:,} · B {kb:,} · matched {len(m):,} "
          f"({100.0 * len(m) / ka:.2f} % of A, {100.0 * len(m) / kb:.2f} % of B)")
    if len(m) == 0:
        raise SystemExit(f"[FATAL] {label}: zero matched keys.")
    res = {"label": label, "matched": len(m), "n_a": ka, "n_b": kb}
    for name, cols in (("REG-1", ac), ("REG-2", wc)):
        if not cols:
            print(f"  {name}: no shared columns -- SKIPPED (not reported as 0.0)")
            res[name] = None
            continue
        v = js_rows(m[[f"{c}_a" for c in cols]].to_numpy(),
                    m[[f"{c}_b" for c in cols]].to_numpy())
        n_nan = int(np.isnan(v).sum())
        mean = float(np.nanmean(v))
        res[name] = mean
        res[name + "_nan"] = n_nan
        res[name + "_med"] = float(np.nanmedian(v))
        res[name + "_p95"] = float(np.nanpercentile(v, 95))
        res[name + "_zero"] = int((np.nan_to_num(v, nan=-1) == 0).sum())
        print(f"  {name}: {len(cols)} cols · row-matched mean DeltaJS = {mean:.6f} bits "
              f"(median {res[name + '_med']:.6f}, p95 {res[name + '_p95']:.6f}) · "
              f"exactly-zero rows {res[name + '_zero']:,} · uncomputable {n_nan:,}")
        if n_nan:
            print(f"    ^ the mean above is computed on {len(m) - n_nan:,} of {len(m):,} rows "
                  f"({100.0 * (len(m) - n_nan) / len(m):.1f} %). The dropped rows are NOT agreement.")
    if wc:
        res["cat"] = categorical_agreement(m, wc, "AT_WORK (wrk30)")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg3", required=True)
    ap.add_argument("--leg2", required=True)
    ap.add_argument("--control", default="", help="second SAME-LEG pool: the within-leg reference")
    a = ap.parse_args()

    l3 = Path(a.leg3)
    head = list(pd.read_csv(l3, nrows=0).columns)
    act = [c for c in head if c.startswith("act30_")]
    wrk = [c for c in head if c.startswith("wrk30")]
    print(f"activity columns: {len(act)} · wrk30 columns: {len(wrk)}")
    if not act or not wrk:
        raise SystemExit("[FATAL] could not find act30_*/wrk30* columns in the Leg-3 pool.")

    cross = compare(l3, Path(a.leg2), act, wrk, "CROSS-LEG  Leg-3 vs Leg-2  (what REG-1/2 claim)")
    ctrl = compare(l3, Path(a.control), act, wrk,
                   "WITHIN-LEG  Leg-3 vs Leg-3  (the control)") if a.control else None

    print("\n" + "=" * 78)
    print("=== V2-E2 pre-registered predictions ===")
    v = []

    ratios = {g: (cross[g] / PROXY[g] if cross.get(g) else float("nan")) for g in PROXY}
    p1 = all(np.isfinite(r) and r >= 10.0 for r in ratios.values())
    v.append(("P1 >=10x PROXY", p1,
              "  ".join(f"{g}: {cross[g]:.6f} vs proxy {PROXY[g]:.5f} = {ratios[g]:,.1f}x"
                        for g in PROXY)))

    breach = [g for g in PROXY if cross.get(g) and cross[g] > BAR]
    v.append(("P2 BREACHES BAR", bool(breach),
              f"heads over the {BAR} bar: {breach or 'none'}"))

    if ctrl:
        # 🔴 Before quoting cross/within, ask whether the control VARIES at all in this dimension.
        # A ratio against a control with no signal is not a measurement of drift, it is a division
        # by the control's own inertness -- the "discriminator is constant in the ground truth"
        # failure (catalogue #7). The two same-leg pools here share seed 3 and differ only in the
        # g3 activity fix, so they are NOT independent resamples; for AT_WORK the control moves
        # almost not at all, and its ratio is reported as N/A rather than as a 5-figure multiple.
        cat_c = ctrl.get("cat", {})
        ctrl_dead = cat_c.get("disagree", 0) <= max(10, 0.001 * cat_c.get("n", 1))
        scored, skipped = {}, {}
        for g in PROXY:
            if ctrl.get(g) in (None, 0) or (g == "REG-2" and ctrl_dead):
                skipped[g] = ctrl.get(g)
            else:
                scored[g] = cross[g] / ctrl[g]
        for g, val in skipped.items():
            print(f"  [N/A ] P3 {g:<15} control has no signal in this dimension "
                  f"(within-leg mean {val:.6g}, categorical disagreement "
                  f"{cat_c.get('disagree', 0):,}/{cat_c.get('n', 0):,}). The two same-leg pools "
                  f"share seed 3 and differ only in the g3 activity fix, so they are not "
                  f"independent resamples. A cross/within ratio here divides by the control's own "
                  f"inertness -- catalogue class #7. NOT scored.")
        if scored:
            p3 = all(x <= 5.0 for x in scored.values())
            v.append(("P3 CTRL SAME ORDER", p3,
                      "  ".join(f"{g}: cross {cross[g]:.6f} / within {ctrl[g]:.6f} = {x:.2f}x"
                                for g, x in scored.items()) + "  (bound 5x)"))
    else:
        print("  [N/A ] P3            no --control pool given; the cross-leg number is "
              "UNINTERPRETABLE without it and is not reported as a verdict.")

    v.append(("P4 NO GATE EDIT", True,
              "this script reads thresholds and never writes them; reg1_js/reg2_js untouched"))

    for name, ok_, why in v:
        print(f"  [{'PASS' if ok_ else 'FAIL'}] {name:<19} {why}")
    npass = sum(1 for _, ok_, _ in v if ok_)
    print(f"\n  {npass}P / {len(v) - npass}F")
    return 0


if __name__ == "__main__":
    sys.exit(main())
