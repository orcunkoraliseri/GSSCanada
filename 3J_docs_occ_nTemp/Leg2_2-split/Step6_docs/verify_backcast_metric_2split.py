#!/usr/bin/env python3
"""
verify_backcast_metric_2split.py  (2026-06-26)

Proves the Step-6 backcast gate metric fix WITHOUT re-running the multi-day
model.  Reads the ALREADY-written 2022 reconstruction + observed 2022 and
recomputes, per DDAY_STRATA:

  OLD metric  = js_divergence(obs_<ch>[m].flatten(), gen_<ch>[m].flatten())
                -> element-wise per-(person,slot) binary overlap (memorisation);
                   saturates near ln2 for sparse channels even when the mean
                   is matched.  This is what failed all 3 strata in job 987039.

  NEW metric  = js_divergence(obs_<ch>[m].mean(0), gen_<ch>[m].mean(0))   (SHAPE)
                + MAD = |obs_prof - gen_prof|.mean()                       (LEVEL)
                + day-mean gap dHome/dWork                                 (LEVEL)
                -> marginal per-slot occupancy profile, consistent with the
                   agg_js / validate() usage elsewhere in the codebase.

PASS (new) keys on per-slot MAD < 0.10 on BOTH channels (level-aware, honest:
a genuine weekday COVID-under-capture gap will still FAIL, as it should).

CPU-only, pure CSV-in (no torch, no GPU, no model).  Row alignment: the
reconstruction was written in the order of df[CYCLE_YEAR==2022].reset_index,
so re-filtering the same observed CSV the same way aligns rows 1:1; strata are
taken from the observed frame.
"""
import argparse
import numpy as np
import pandas as pd

LN2 = float(np.log(2.0))  # natural-log JS upper bound ~0.6931


def js_divergence(p, q):
    # identical to 3rdJ_04D_train_2split.py:539
    p = np.clip(p / (p.sum() + 1e-12), 1e-12, None)
    q = np.clip(q / (q.sum() + 1e-12), 1e-12, None)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data",
        default="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
                "Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv",
    )
    ap.add_argument(
        "--recon",
        default="/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
                "Leg2_2-split/Step6_docs/outputs_step6/reconstructed_2022_diaries_2split.csv",
    )
    args = ap.parse_args()

    hom = [f"hom30_{i:03d}" for i in range(1, 49)]
    wrk = [f"wrk30_{i:03d}" for i in range(1, 49)]
    act = [f"act30_{i:03d}" for i in range(1, 49)]

    print(f"natural-log JS upper bound = {LN2:.4f}\n")
    print(f"[load] observed: {args.data}")
    usecols = list(set(hom + wrk + act + ["CYCLE_YEAR", "DDAY_STRATA"]))
    obs = pd.read_csv(args.data, usecols=lambda c: c in usecols)
    obs = obs[obs["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    print(f"       observed 2022 rows = {len(obs):,}")

    print(f"[load] reconstructed: {args.recon}")
    rec = pd.read_csv(args.recon).reset_index(drop=True)
    print(f"       reconstructed rows = {len(rec):,}")

    n = min(len(obs), len(rec))
    if len(obs) != len(rec):
        print(f"  [WARN] length mismatch ({len(obs)} vs {len(rec)}) — truncating to {n}")
    obs = obs.iloc[:n].reset_index(drop=True)
    rec = rec.iloc[:n].reset_index(drop=True)

    oh = obs[hom].values.astype(float)
    ow = obs[wrk].values.astype(float)
    oa = obs[act].values.astype(int) - 1
    gh = rec[hom].values.astype(float)
    gw = rec[wrk].values.astype(float)
    ga = rec[act].values.astype(int) - 1
    strata = obs["DDAY_STRATA"].values

    print("\n" + "=" * 100)
    print("PER-STRATUM COMPARISON  (OLD = element-wise flatten | NEW = per-slot profile)")
    print("=" * 100)
    hdr = (f"{'S':<3}{'n':>7} | {'OLD_JSh':>8}{'OLD_JSw':>8} | "
           f"{'JSact':>7}{'NEW_JSh':>8}{'NEW_JSw':>8} | "
           f"{'MADh':>7}{'MADw':>7} | {'dHome':>7}{'dWork':>7} | PASS?")
    print(hdr)
    print("-" * 100)
    for s in [1, 2, 3]:
        m = (strata == s)
        if m.sum() == 0:
            continue
        # OLD (the bug)
        old_jh = js_divergence(oh[m].flatten(), gh[m].flatten())
        old_jw = js_divergence(ow[m].flatten(), gw[m].flatten())
        # NEW
        ohp, ghp = oh[m].mean(0), gh[m].mean(0)
        owp, gwp = ow[m].mean(0), gw[m].mean(0)
        oap = np.bincount(oa[m].flatten(), minlength=14).astype(float)
        gap = np.bincount(ga[m].flatten(), minlength=14).astype(float)
        js_act = js_divergence(oap, gap)
        new_jh = js_divergence(ohp, ghp)
        new_jw = js_divergence(owp, gwp)
        mad_h = float(np.abs(ohp - ghp).mean())
        mad_w = float(np.abs(owp - gwp).mean())
        dh = abs(gh[m].mean() - oh[m].mean())
        dw = abs(gw[m].mean() - ow[m].mean())
        ok = (mad_h < 0.10) and (mad_w < 0.10)
        print(f"{s:<3}{m.sum():>7} | {old_jh:>8.4f}{old_jw:>8.4f} | "
              f"{js_act:>7.4f}{new_jh:>8.4f}{new_jw:>8.4f} | "
              f"{mad_h:>7.4f}{mad_w:>7.4f} | {dh:>7.4f}{dw:>7.4f} | "
              f"{'PASS' if ok else 'FAIL'}")

    # Weekday (stratum 1) profile dump so we can SEE where any residual gap lives
    m1 = (strata == 1)
    if m1.sum() > 0:
        print("\n" + "=" * 100)
        print("WEEKDAY (stratum 1) per-slot occupancy profile  obs vs gen  [slot: HOMEobs/HOMEgen  WORKobs/WORKgen]")
        print("=" * 100)
        ohp, ghp = oh[m1].mean(0), gh[m1].mean(0)
        owp, gwp = ow[m1].mean(0), gw[m1].mean(0)
        for t in range(48):
            tag = " <biz" if 10 <= t <= 25 else ""
            print(f"  slot {t+1:02d}  HOME {ohp[t]:.3f}/{ghp[t]:.3f}   "
                  f"WORK {owp[t]:.3f}/{gwp[t]:.3f}{tag}")
        biz = list(range(10, 26))
        print(f"\n  biz-hours (slots 11-26) mean  HOME obs={oh[m1][:,biz].mean():.4f} "
              f"gen={gh[m1][:,biz].mean():.4f}   "
              f"WORK obs={ow[m1][:,biz].mean():.4f} gen={gw[m1][:,biz].mean():.4f}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
