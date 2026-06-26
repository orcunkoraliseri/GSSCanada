#!/usr/bin/env python3
"""
calibrate_weekday_work_2split.py  (2026-06-26)  —  Calibration B

Post-hoc, no-retrain correction of the 2030 deliverable's weekday WORK over-count.
The trained model leaves weekday-employed people "at work" too long (esp. an
evening/night tail — at work at midnight vs observed ~0.02).  B caps each band's
weekday-employed per-slot WORK rate at the OBSERVED 2022 weekday-employed profile
(real data = the anchor), by trimming work-block TAILS to home (processing slots
48->1 so trailing edges peel first; leading edges next; interior last).  Flipped
WORK slots get a time-appropriate home activity (Sleep at night / Passive leisure
by day).  Non-employed and weekend rows pass through unchanged; WFH-day diaries
are naturally untouched (they are not "at work"), so band WFH-day shares are
preserved.  CPU-only, CSV-in/CSV-out.  Run 04M min-dwell afterwards.
"""
import argparse
import numpy as np
import pandas as pd

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
ACT = [f"act30_{i:03d}" for i in range(1, 49)]
BIZ = list(range(10, 26))            # 0-indexed business slots 11-26
BIZ_SET = set(BIZ)
WORK_ACT, SLEEP_ACT, PASSIVE_ACT = 0, 13, 10   # 0-indexed (module ACT_NAMES)
NIGHT = set(list(range(0, 12)) + list(range(44, 48)))  # 0-idx: 00:00-06:00 & 22:00-24:00
BANDS = ["conservative", "hybrid", "fullyhybrid"]


def classify_wfh_day(home2d):
    return home2d[:, BIZ].mean(1) >= 0.5


def cap_band(W, H, A, target, rng):
    """Cap per-slot work at target by trimming work-block tails to home. In-place."""
    N = W.shape[0]
    n_flips = 0
    for t in range(47, -1, -1):                       # 48 -> 1
        if t in BIZ_SET:                              # leave business hours to the
            continue                                  # band's WFH scenario (also keeps
            # the biz-hours-based WFH-day classification — and band shares — intact)
        rate = W[:, t].mean()
        if rate <= target[t]:
            continue
        n_remove = int(round((rate - target[t]) * N))
        if n_remove <= 0:
            continue
        at_work = np.where(W[:, t] == 1)[0]
        if len(at_work) == 0:
            continue
        trail = at_work if t == 47 else at_work[W[at_work, t + 1] == 0]
        lead = np.array([], int) if t == 0 else at_work[W[at_work, t - 1] == 0]
        order, seen = [], set()
        for grp in (trail, lead, at_work):
            for i in rng.permutation(len(grp)):
                p = int(grp[i])
                if p not in seen:
                    seen.add(p)
                    order.append(p)
        for p in order[:n_remove]:
            W[p, t] = 0
            H[p, t] = 1
            if A[p, t] == WORK_ACT:
                A[p, t] = SLEEP_ACT if t in NIGHT else PASSIVE_ACT
            n_flips += 1
    return n_flips


def daymean(a):
    return float(a.mean())


def main():
    base = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
            "Leg2_2-split/Step6_docs/outputs_step6")
    data_default = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
                    "Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=data_default)
    ap.add_argument("--deliverable", default=f"{base}/2030_synthetic_diaries_2split.csv")
    ap.add_argument("--out", default=f"{base}/2030_synthetic_diaries_2split_calibrated.csv")
    a = ap.parse_args()
    rng = np.random.default_rng(42)

    # ── observed-2022 weekday-employed WORK target (per slot) ────────────────
    usecols = set(HOM + WRK + ["CYCLE_YEAR", "DDAY_STRATA", "LFTAG"])
    obs = pd.read_csv(a.data, usecols=lambda c: c in usecols)
    obs = obs[obs["CYCLE_YEAR"] == 2022]
    owe = obs[(obs["DDAY_STRATA"] == 1) & (obs["LFTAG"] == 1)]
    target = owe[WRK].values.astype(float).mean(0)     # (48,)
    print(f"observed 2022 weekday-employed n={len(owe):,}  "
          f"WORK day-mean target={target.mean():.4f}")

    # ── deliverable ─────────────────────────────────────────────────────────
    deliv = pd.read_csv(a.deliverable)
    print(f"deliverable rows={len(deliv):,}  cols={len(deliv.columns)}")
    out = deliv.copy()

    for band in BANDS:
        mask = ((deliv["BAND"] == band) & (deliv["DDAY_STRATA"] == 1)
                & (deliv["LFTAG"] == 1)).values
        idx = np.where(mask)[0]
        if len(idx) == 0:
            print(f"[{band}] no weekday-employed rows"); continue
        W = deliv.loc[mask, WRK].values.astype(float).copy()
        H = deliv.loc[mask, HOM].values.astype(float).copy()
        A = (deliv.loc[mask, ACT].values.astype(int) - 1).copy()   # 0-indexed

        wfh0 = classify_wfh_day(H).mean()
        w0, h0 = daymean(W), daymean(H)
        nf = cap_band(W, H, A, target, rng)
        wfh1 = classify_wfh_day(H).mean()
        w1, h1 = daymean(W), daymean(H)

        # write back
        out.loc[mask, WRK] = W
        out.loc[mask, HOM] = H
        out.loc[mask, ACT] = A + 1

        print(f"\n[{band}] weekday-employed n={len(idx):,}  flips={nf:,}")
        print(f"   WORK day-mean {w0:.4f} -> {w1:.4f}   HOME day-mean {h0:.4f} -> {h1:.4f}")
        print(f"   WFH-day share {wfh0:.4f} -> {wfh1:.4f}  (should be ~unchanged)")
        print(f"   biz-hours WORK after={W[:, BIZ].mean():.4f}   "
              f"night(40-48) WORK after={W[:, 39:48].mean():.4f}  "
              f"(observed night~0.02)")

    out.to_csv(a.out, index=False)
    print(f"\nWROTE calibrated deliverable: {a.out}  rows={len(out):,}")

    # ── per-slot WORK profile, conservative weekday-employed, before/after/target
    print("\nconservative weekday-employed per-slot WORK  [slot: deliv -> calibrated  (target)]:")
    m = ((deliv["BAND"] == "conservative") & (deliv["DDAY_STRATA"] == 1)
         & (deliv["LFTAG"] == 1)).values
    wb = deliv.loc[m, WRK].values.astype(float).mean(0)
    wa = out.loc[m, WRK].values.astype(float).mean(0)
    for t in range(48):
        tag = " <biz" if t in BIZ else (" <night" if t in NIGHT else "")
        print(f"   slot {t+1:02d}  {wb[t]:.3f} -> {wa[t]:.3f}  ({target[t]:.3f}){tag}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
