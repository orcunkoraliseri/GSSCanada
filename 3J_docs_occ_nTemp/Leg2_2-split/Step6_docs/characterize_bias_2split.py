#!/usr/bin/env python3
"""
characterize_bias_2split.py  (2026-06-26)

Characterises the weekday home/work LEVEL bias to design calibration B (the
post-hoc, no-retrain correction of the deliverable's weekday occupancy level).

For weekday rows (DDAY_STRATA==1) it computes per-slot HOME/WORK means for:
  - observed 2022                 (ground truth)
  - backcast 2022                 (reconstructed_2022_diaries_2split.csv, temp 0.8)
  - 2030 deliverable, per band    (2030_synthetic_diaries_2split.csv)

Delta-method bias    = backcast_gen_2022 - observed_2022   (per slot)
Bias-corrected 2030  = deliverable_2030 - bias             (per slot; home up, work down)
Reports day-means + validity (corrected stays in [0,1]) and a COMPOSITION-vs-
INTENSITY breakdown: per-person business-hours WORK fraction histogram (obs vs
deliverable) — tells us if over-work is "too many office-day people" (composition,
fixable by day-type reweight) or "office-day people at work too long" (intensity,
needs intra-diary editing).  CPU-only, reads existing CSVs.
"""
import argparse
import numpy as np
import pandas as pd

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
BIZ = list(range(10, 26))  # 0-indexed; business slots 11-26 (1-indexed)
BANDS = ["conservative", "hybrid", "fullyhybrid"]


def daymean(arr2d):
    return float(arr2d.mean())


def main():
    base = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
            "Leg2_2-split/Step6_docs/outputs_step6")
    data_default = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
                    "Leg2_2-split/Step4_docs/outputs_step4/sweep/R5_lr1e4/augmented_diaries.csv")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=data_default)
    ap.add_argument("--recon", default=f"{base}/reconstructed_2022_diaries_2split.csv")
    ap.add_argument("--deliverable", default=f"{base}/2030_synthetic_diaries_2split.csv")
    a = ap.parse_args()

    usecols = set(HOM + WRK + ["CYCLE_YEAR", "DDAY_STRATA", "LFTAG"])
    obs = pd.read_csv(a.data, usecols=lambda c: c in usecols)
    obs = obs[obs["CYCLE_YEAR"] == 2022].reset_index(drop=True)
    rec = pd.read_csv(a.recon).reset_index(drop=True)
    n = min(len(obs), len(rec))
    obs = obs.iloc[:n].reset_index(drop=True)
    rec = rec.iloc[:n].reset_index(drop=True)
    print(f"obs 2022 rows={len(obs):,}  recon rows={len(rec):,}")

    m1 = (obs["DDAY_STRATA"].values == 1)
    emp = (obs["LFTAG"].values == 1) if "LFTAG" in obs.columns else np.ones(len(obs), bool)
    we = m1 & emp
    print(f"weekday rows={m1.sum():,}  weekday-employed rows={we.sum():,}")

    oh = obs[HOM].values.astype(float); ow = obs[WRK].values.astype(float)
    gh = rec[HOM].values.astype(float); gw = rec[WRK].values.astype(float)

    o_h, o_w = oh[m1].mean(0), ow[m1].mean(0)   # observed weekday per-slot
    g_h, g_w = gh[m1].mean(0), gw[m1].mean(0)   # backcast weekday per-slot
    bias_h = g_h - o_h
    bias_w = g_w - o_w

    print("\n" + "=" * 96)
    print("WEEKDAY per-slot:  obs(H/W)  backcast(H/W)  bias=gen-obs(H/W)")
    print("=" * 96)
    for t in range(48):
        tag = " <biz" if t in BIZ else ""
        print(f"  slot {t+1:02d}  obs {o_h[t]:.3f}/{o_w[t]:.3f}   "
              f"rec {g_h[t]:.3f}/{g_w[t]:.3f}   bias {bias_h[t]:+.3f}/{bias_w[t]:+.3f}{tag}")
    print(f"\n  WEEKDAY day-mean  HOME  obs={daymean(oh[m1]):.4f} backcast={daymean(gh[m1]):.4f} "
          f"bias={daymean(gh[m1])-daymean(oh[m1]):+.4f}")
    print(f"  WEEKDAY day-mean  WORK  obs={daymean(ow[m1]):.4f} backcast={daymean(gw[m1]):.4f} "
          f"bias={daymean(gw[m1])-daymean(ow[m1]):+.4f}")

    # ── deliverable per band + bias-corrected target ────────────────────────
    deliv = pd.read_csv(a.deliverable)
    has_band = "BAND" in deliv.columns
    has_str = "DDAY_STRATA" in deliv.columns
    print("\n" + "=" * 96)
    print("2030 DELIVERABLE weekday day-mean + DELTA-METHOD bias-corrected target")
    print("=" * 96)
    print(f"  deliverable has BAND={has_band} DDAY_STRATA={has_str} LFTAG={'LFTAG' in deliv.columns}")
    for band in BANDS:
        sub = deliv
        if has_band:
            sub = sub[sub["BAND"] == band]
        if has_str:
            sub = sub[sub["DDAY_STRATA"] == 1]
        if len(sub) == 0:
            print(f"  [{band}] no weekday rows")
            continue
        dh = sub[HOM].values.astype(float)
        dw = sub[WRK].values.astype(float)
        d_h, d_w = dh.mean(0), dw.mean(0)            # deliverable per-slot
        corr_h = np.clip(d_h - bias_h, 0.0, 1.0)     # home up
        corr_w = np.clip(d_w - bias_w, 0.0, 1.0)     # work down
        pre_clip_h = d_h - bias_h
        pre_clip_w = d_w - bias_w
        print(f"\n  [{band}]  weekday rows={len(sub):,}")
        print(f"    HOME day-mean: deliverable={d_h.mean():.4f}  corrected(target)={corr_h.mean():.4f}  "
              f"(+{corr_h.mean()-d_h.mean():.4f})")
        print(f"    WORK day-mean: deliverable={d_w.mean():.4f}  corrected(target)={corr_w.mean():.4f}  "
              f"({corr_w.mean()-d_w.mean():+.4f})")
        print(f"    corrected validity: HOME pre-clip [{pre_clip_h.min():.3f},{pre_clip_h.max():.3f}] "
              f"WORK pre-clip [{pre_clip_w.min():.3f},{pre_clip_w.max():.3f}] "
              f"(outside [0,1] => clipping needed at some slots)")

    # ── composition vs intensity: biz-hours WORK fraction per person ────────
    print("\n" + "=" * 96)
    print("COMPOSITION vs INTENSITY — per-person business-hours WORK fraction (weekday EMPLOYED)")
    print("=" * 96)
    bins = [0.0, 0.1, 0.5, 0.9, 1.01]
    labels = ["[0,0.1) home-day", "[0.1,0.5) light", "[0.5,0.9) office", "[0.9,1] full-office"]

    def hist(frac):
        h, _ = np.histogram(frac, bins=bins)
        return h / max(len(frac), 1)

    obs_bw = ow[we][:, BIZ].mean(1)
    print(f"  observed 2022 (n={we.sum():,}):")
    for lab, v in zip(labels, hist(obs_bw)):
        print(f"      {lab:<22} {v:.3f}")
    print(f"      mean biz-work fraction = {obs_bw.mean():.4f}")

    rec_bw = gw[we][:, BIZ].mean(1)
    print(f"  backcast 2022 (same rows):")
    for lab, v in zip(labels, hist(rec_bw)):
        print(f"      {lab:<22} {v:.3f}")
    print(f"      mean biz-work fraction = {rec_bw.mean():.4f}")

    if has_band:
        dc = deliv[deliv["BAND"] == "conservative"]
        if has_str:
            dc = dc[dc["DDAY_STRATA"] == 1]
        if "LFTAG" in dc.columns:
            dc = dc[dc["LFTAG"] == 1]
        if len(dc) > 0:
            dl_bw = dc[WRK].values.astype(float)[:, BIZ].mean(1)
            print(f"  2030 deliverable conservative weekday-employed (n={len(dc):,}):")
            for lab, v in zip(labels, hist(dl_bw)):
                print(f"      {lab:<22} {v:.3f}")
            print(f"      mean biz-work fraction = {dl_bw.mean():.4f}")

    print("\nDONE.")


if __name__ == "__main__":
    main()
