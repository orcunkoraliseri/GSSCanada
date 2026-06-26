#!/usr/bin/env python3
"""
profile_forecast_weekday_2split.py  (2026-06-26)

Settles whether the weekday "evening work-latch" seen in the temp=0.0 backcast
(job 987039 / verify 1005383) is also present in the temp~0.8 FORECAST deliverable
(which is what Step 7 consumes), and whether min-dwell post-processing changes it.

CPU-only, pure CSV-in (no torch, no model).  For each forecast CSV it prints the
weekday (DDAY_STRATA==1 if present, else all rows) per-slot mean occupancy profile
plus 'latch indicators':
    NIGHT_START = WORK/HOME mean over slots 1-8   (should be WORK~0, HOME~0.95)
    MIDDAY      = WORK/HOME mean over slots 13-22
    NIGHT_END   = WORK/HOME mean over slots 40-48  (should be WORK~0.02-0.05, HOME~0.9+)
A latched model shows NIGHT_END WORK ~0.45-0.50 and HOME ~0.50 (never returns home).
"""
import argparse
import numpy as np
import pandas as pd

HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]


def slot_mean(arr, lo, hi):  # 1-indexed inclusive
    return float(arr[lo - 1:hi].mean())


def profile_csv(path, label, band=None):
    print("\n" + "=" * 90)
    print(f"FILE: {label}")
    print(f"      {path}")
    print("=" * 90)
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"  [ERROR] could not read: {e}")
        return
    print(f"  rows={len(df):,}  cols={len(df.columns)}")
    cols = set(df.columns)
    print(f"  has DDAY_STRATA={'DDAY_STRATA' in cols}  has BAND={'BAND' in cols}  "
          f"has hom30_001={'hom30_001' in cols}  has wrk30_001={'wrk30_001' in cols}")
    if "hom30_001" not in cols or "wrk30_001" not in cols:
        print("  [SKIP] occupancy columns absent — printing first 30 column names:")
        print("   ", list(df.columns)[:30])
        return

    if band is not None and "BAND" in cols:
        df = df[df["BAND"] == band]
        print(f"  filtered BAND=={band}: rows={len(df):,}")
    if "DDAY_STRATA" in cols:
        df = df[df["DDAY_STRATA"] == 1]
        print(f"  filtered weekday (DDAY_STRATA==1): rows={len(df):,}")
    else:
        print("  [NOTE] no DDAY_STRATA — profiling ALL rows (weekday + weekend mixed)")
    if len(df) == 0:
        print("  [SKIP] no rows after filter")
        return

    h = df[HOM].values.astype(float)
    w = df[WRK].values.astype(float)
    hp = h.mean(0)
    wp = w.mean(0)

    print(f"  LATCH INDICATORS (weekday):")
    print(f"    NIGHT_START (slots 1-8)   WORK={slot_mean(wp,1,8):.3f}  HOME={slot_mean(hp,1,8):.3f}   "
          f"(healthy WORK~0.02, HOME~0.95)")
    print(f"    MIDDAY      (slots 13-22) WORK={slot_mean(wp,13,22):.3f}  HOME={slot_mean(hp,13,22):.3f}")
    print(f"    NIGHT_END   (slots 40-48) WORK={slot_mean(wp,40,48):.3f}  HOME={slot_mean(hp,40,48):.3f}   "
          f"(healthy WORK~0.02-0.05, HOME~0.90+; LATCHED WORK~0.47, HOME~0.50)")

    latched = slot_mean(wp, 40, 48) > 0.20
    print(f"    >>> VERDICT: {'LATCHED (evening work does NOT release)' if latched else 'HEALTHY (work releases in evening)'}")

    print("  full per-slot profile [slot: HOME  WORK]:")
    for t in range(48):
        print(f"    slot {t+1:02d}  HOME {hp[t]:.3f}   WORK {wp[t]:.3f}")


def main():
    base = ("/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/"
            "Leg2_2-split/Step6_docs/outputs_step6")
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=f"{base}/2030_diaries_conservative_raw.csv")
    ap.add_argument("--mindwell", default=f"{base}/2030_diaries_conservative_mindwell.csv")
    ap.add_argument("--deliverable", default=f"{base}/2030_synthetic_diaries_2split.csv")
    args = ap.parse_args()

    # 1. raw forecast (temp~0.8, PRE min-dwell) — does the temp=0.8 sample latch?
    profile_csv(args.raw, "RAW conservative forecast (pre-mindwell)")
    # 2. post min-dwell conservative — does mindwell change it?
    profile_csv(args.mindwell, "MIN-DWELL conservative (post-processed)")
    # 3. final deliverable, conservative band — what Step 7 actually eats
    profile_csv(args.deliverable, "DELIVERABLE 2030_synthetic_diaries_2split.csv", band="conservative")

    print("\nDONE.")


if __name__ == "__main__":
    main()
