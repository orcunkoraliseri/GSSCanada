#!/usr/bin/env python3
"""
mutex_check_backcast_2split.py  (2026-06-26)

Decides whether applying the deliverable's 6H mutual_exclusion_resolve to the
backcast reconstruction collapses the weekday MAD residual.  The backcast gate
currently scores RAW (pre-mutex) two-channel output vs mutually-exclusive
observed diaries; the deliverable applies mutex (job 987039: 10188 conflicts
resolved).  This recomputes the gate PRE vs POST mutex on the EXISTING
reconstructed CSV(s) — CPU-only, no model, no GPU.

Diagnostic: weekday day-mean HOME/WORK/OTHER(=1-H-W).  If pre-mutex OTHER < 0,
the heads OVERLAP (home+work>1 per cell) and mutex is the fix.  If pre-mutex
OTHER >= 0 and post-mutex still over-predicts, the residual is genuine
"other-activity under-prediction" (mutex won't help).
"""
import argparse
import numpy as np
import pandas as pd

WORK_ACT_0IDX = 0  # matches module:125 (Work = activity 0, 0-indexed; act30==1)

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
ACT = [f"act30_{i:03d}" for i in range(1, 49)]


def js_divergence(p, q):
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def mutual_exclusion_resolve(gen_act, gen_home, gen_work):
    # exact replica of module:2113
    gen_home = gen_home.copy().astype(float)
    gen_work = gen_work.copy().astype(float)
    conflict = (gen_home == 1) & (gen_work == 1)
    n_conflict = int(conflict.sum())
    if n_conflict > 0:
        is_work_act = (gen_act == WORK_ACT_0IDX)
        gen_home[conflict & is_work_act] = 0
        gen_work[conflict & ~is_work_act] = 0
    return gen_home, gen_work, n_conflict


def gate(oh, ow, gh, gw, strata, label):
    print(f"  --- gate [{label}] ---")
    print(f"  {'S':<3}{'n':>7} {'JShome':>8}{'JSwork':>8}{'MADhome':>8}{'MADwork':>8}"
          f"{'dHome':>8}{'dWork':>8}  PASS?")
    for s in [1, 2, 3]:
        m = (strata == s)
        if m.sum() == 0:
            continue
        ohp, ghp = oh[m].mean(0), gh[m].mean(0)
        owp, gwp = ow[m].mean(0), gw[m].mean(0)
        jsh, jsw = js_divergence(ohp, ghp), js_divergence(owp, gwp)
        madh = float(np.abs(ohp - ghp).mean())
        madw = float(np.abs(owp - gwp).mean())
        dh = abs(gh[m].mean() - oh[m].mean())
        dw = abs(gw[m].mean() - ow[m].mean())
        ok = (madh < 0.10) and (madw < 0.10)
        print(f"  {s:<3}{m.sum():>7} {jsh:>8.4f}{jsw:>8.4f}{madh:>8.4f}{madw:>8.4f}"
              f"{dh:>8.4f}{dw:>8.4f}  {'PASS' if ok else 'FAIL'}")


def process(recon_path, obs):
    print("\n" + "=" * 92)
    print(f"RECON: {recon_path}")
    print("=" * 92)
    try:
        rec = pd.read_csv(recon_path).reset_index(drop=True)
    except Exception as e:
        print(f"  [ERROR] could not read: {e}")
        return
    n = min(len(obs), len(rec))
    if len(obs) != len(rec):
        print(f"  [WARN] length mismatch {len(obs)} vs {len(rec)} — truncating to {n}")
    o = obs.iloc[:n].reset_index(drop=True)
    rec = rec.iloc[:n].reset_index(drop=True)

    oh = o[HOM].values.astype(float)
    ow = o[WRK].values.astype(float)
    gh = rec[HOM].values.astype(float)
    gw = rec[WRK].values.astype(float)
    ga = rec[ACT].values.astype(int) - 1
    strata = o["DDAY_STRATA"].values

    print(f"  gen_home values: min={gh.min():.2f} max={gh.max():.2f} "
          f"n_unique={len(np.unique(gh))}  (expect binary 0/1)")

    gate(oh, ow, gh, gw, strata, "PRE-mutex (raw, as the gate scores it now)")

    gh2, gw2, nconf = mutual_exclusion_resolve(ga, gh, gw)
    tot = gh.size
    print(f"  mutex conflicts (home==1 & work==1): {nconf:,} / {tot:,} cells "
          f"({100.0 * nconf / tot:.2f}%)")
    gate(oh, ow, gh2, gw2, strata, "POST-mutex (deliverable-consistent)")

    m1 = (strata == 1)

    def means(h, w):
        return h[m1].mean(), w[m1].mean(), 1.0 - h[m1].mean() - w[m1].mean()

    oH, oW, oO = means(oh, ow)
    pH, pW, pO = means(gh, gw)
    qH, qW, qO = means(gh2, gw2)
    print(f"  weekday day-mean  HOME / WORK / OTHER(=1-H-W):")
    print(f"    observed    {oH:.3f} / {oW:.3f} / {oO:.3f}")
    print(f"    pre-mutex   {pH:.3f} / {pW:.3f} / {pO:.3f}   (OTHER<0 => head overlap)")
    print(f"    post-mutex  {qH:.3f} / {qW:.3f} / {qO:.3f}")


def main():
    base = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
            "Leg2_2-split/Step6_docs/outputs_step6")
    data_default = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
                    "Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=data_default)
    ap.add_argument("--recon_pooled",
                    default=f"{base}/reconstructed_2022_diaries_2split.csv")
    ap.add_argument("--recon_ft",
                    default=f"{base}/reconstructed_2022_diaries_2split_W_2022_ft_2split.csv")
    args = ap.parse_args()

    usecols = set(HOM + WRK + ACT + ["CYCLE_YEAR", "DDAY_STRATA"])
    obs = pd.read_csv(args.data, usecols=lambda c: c in usecols)
    obs = obs[obs["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    print(f"observed 2022 rows = {len(obs):,}")

    process(args.recon_pooled, obs)   # canonical W_pooled_2030 backcast (temp 0.8)
    process(args.recon_ft, obs)       # supplementary W_2022_ft backcast
    print("\nDONE.")


if __name__ == "__main__":
    main()
