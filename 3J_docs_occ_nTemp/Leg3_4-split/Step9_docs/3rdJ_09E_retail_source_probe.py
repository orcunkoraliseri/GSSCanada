"""FINDING 7 -- which 2030 retail source actually reaches the BEM, and is it the calibrated one?

The frame probe (3rdJ_09E_retail_frame_probe.py) returned a huge apparent frame effect. Before
believing it, the control had to be checked -- the FINDING 6 lesson. It has a CONFOUND: the control
draws from `D2030` = `..._C_v2.csv`, the CALIBRATED 2030 pool, while the shipped retail base is
built by `3rdJ_06_retail_lever_4split.py::load_pooled_raw()` from `2030_diaries_{band}_raw.csv`, the
RAW pool. So that probe varied two things at once and can prove neither.

This probe separates them. Three sources, same quantity (`ret30` mean per DDAY_STRATA, per PR),
same treatment:

    RAW   pooled 2030_diaries_{band}_raw.csv          <- what the shipped retail product is built on
    CAL   ..._C_v2.csv, the calibrated pool           <- what every OTHER 2030 channel is built on
    OBS   the augmented 2022 stock                    <- the observed anchor both should respect

Two questions, and they are separable:

  Q1 SOURCE CONSISTENCY.  RAW vs CAL, same frame, same rows-per-stratum construction. Any
     difference here is calibration, not population. If it is large, the retail channel is being
     fed from an uncalibrated artefact while the rest of the 2030 pipeline uses the calibrated one.
  Q2 WEEKLY CONTRAST.     Saturday/weekday ratio under each source, against OBS. Retail presence is
     strongly weekend-peaked in observed time-use data; a source that flattens or inverts that has
     lost the signal the retail channel exists to carry.

No threshold is invented after the fact: Q1 is material if any day-type mean differs by >10 %
(the level survives into `multiplier` only through the peak, but a >10 % source discrepancy is a
provenance defect regardless of whether it moves energy). Q2 is material if RAW's Sat/weekday ratio
falls outside OBS's ratio +/-25 %.

Usage:  py -3 3rdJ_09E_retail_source_probe.py
"""
from __future__ import annotations

import gc
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STEP7 = os.path.join(HERE, "..", "Step7_docs", "3rdJ_07_aug_to_bem_4split.py")
S6OUT = os.path.join(HERE, "..", "Step6_docs", "outputs_step6")

BANDS = ["conservative", "hybrid", "fullyhybrid"]
STRATUM = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
QC_PR, AB_PR = 24, 48          # as used by 3rdJ_06_retail_lever_4split.py
OBS_QC, OBS_AB = 2, 4          # the 2022 stock's REGION coding, per build_retail_product_2022


def load_step7():
    spec = importlib.util.spec_from_file_location("step7_mod", os.path.abspath(STEP7))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def stratum_means(path, RET, pr_col_values, label):
    """Return {(stratum, pr_label): 48-array} + {(stratum,'ALL'): 48-array}, memory-guarded."""
    cols = ["DDAY_STRATA", "PR"] + RET
    df = pd.read_csv(path, low_memory=False, usecols=cols)
    out = {}
    for s in (1, 2, 3):
        sub = df[df["DDAY_STRATA"] == s]
        out[(s, "ALL")] = sub[RET].to_numpy(float).mean(axis=0) if len(sub) else np.full(48, np.nan)
        for lbl, code in pr_col_values:
            p = sub[sub["PR"] == code]
            out[(s, lbl)] = p[RET].to_numpy(float).mean(axis=0) if len(p) else np.full(48, np.nan)
    n = len(df)
    del df
    gc.collect()
    print(f"  loaded {label}: {n:,} rows", flush=True)
    return out, n


def pooled_raw(RET):
    """Reproduce load_pooled_raw(): concatenate the 3 raw band files, then take stratum means.
    Pooling THEN averaging is not the same as averaging the 3 band means unless the bands have
    equal per-stratum counts, so this follows the lever script's own order of operations."""
    frames = []
    for b in BANDS:
        p = os.path.join(S6OUT, f"2030_diaries_{b}_raw.csv")
        frames.append(pd.read_csv(p, low_memory=False, usecols=["DDAY_STRATA", "PR"] + RET))
    df = pd.concat(frames, ignore_index=True)
    del frames
    gc.collect()
    out = {}
    for s in (1, 2, 3):
        sub = df[df["DDAY_STRATA"] == s]
        out[(s, "ALL")] = sub[RET].to_numpy(float).mean(axis=0)
        for lbl, code in (("QC", QC_PR), ("AB", AB_PR)):
            p = sub[sub["PR"] == code]
            out[(s, lbl)] = p[RET].to_numpy(float).mean(axis=0) if len(p) else np.full(48, np.nan)
    n = len(df)
    del df
    gc.collect()
    print(f"  loaded RAW pooled: {n:,} rows", flush=True)
    return out, n


def main():
    m = load_step7()
    RET = m.RET

    print("loading the three sources ...", flush=True)
    RAW, n_raw = pooled_raw(RET)
    CAL, n_cal = stratum_means(m.D2030, RET, [("QC", QC_PR), ("AB", AB_PR)], "CAL (_C_v2)")
    OBS, n_obs = stratum_means(m.AUG, RET, [("QC", OBS_QC), ("AB", OBS_AB)], "OBS (2022 stock)")

    # ---- cross-check: does RAW reproduce the SHIPPED base column? --------------------------
    # If it does not, this probe is measuring something other than what ships, and every number
    # below is void. This is the check the frame probe did not have.
    lev = pd.read_csv(os.path.join(S6OUT, "at_retail_fraction_2030_plateau.csv"))
    worst = 0.0
    for s in (1, 2, 3):
        for grp in ("ALL", "QC", "AB"):
            g = lev[(lev["DDAY_STRATA"] == s) & (lev["PR_GROUP"] == grp)].sort_values("slot")
            if g.empty:
                continue
            d = np.abs(g["at_retail_fraction_2030_base"].to_numpy(float) - RAW[(s, grp)])
            worst = max(worst, float(np.nanmax(d)))
    print(f"\nRAW reproduces the shipped base column: max|diff| = {worst:.3e} "
          f"({'OK' if worst < 1e-9 else 'MISMATCH -- this probe does not measure what ships'})")
    if worst >= 1e-9:
        print("  Refusing to report Q1/Q2 off a source I cannot reproduce.")
        sys.exit(1)

    # ---- Q1: source consistency, RAW vs CAL, same frame ------------------------------------
    print("\nQ1  SOURCE CONSISTENCY -- RAW (what retail uses) vs CAL (what everything else uses)")
    print(f"    same pool frame; RAW n={n_raw:,}  CAL n={n_cal:,}")
    print(f"    {'day':<10}{'PR':<5}{'RAW mean':>11}{'CAL mean':>11}{'CAL/RAW':>10}"
          f"{'pkRAW clk':>10}{'pkCAL clk':>10}")
    q1_worst = 0.0
    for s in (1, 2, 3):
        for grp in ("ALL", "QC", "AB"):
            r, c = RAW[(s, grp)], CAL[(s, grp)]
            rm, cm = float(np.nanmean(r)), float(np.nanmean(c))
            ratio = cm / rm if rm else float("nan")
            q1_worst = max(q1_worst, abs(ratio - 1.0))
            # CLOCK hour, not diary-origin. `ret30` slots start at 04:00, and Step-7 applies
            # np.roll(arr, 8) before anything downstream sees them. Printing the un-rolled index
            # would understate every peak by 4 h -- the +4h offset bug this project has already
            # been bitten by once.
            print(f"    {STRATUM[s]:<10}{grp:<5}{rm:>11.5f}{cm:>11.5f}{ratio:>10.3f}"
                  f"{int(np.nanargmax(np.roll(r, 8)))//2:>10}"
                  f"{int(np.nanargmax(np.roll(c, 8)))//2:>10}")
    print(f"    worst |CAL/RAW - 1| = {q1_worst:.3f}  -> "
          f"{'MATERIAL: the two 2030 sources disagree' if q1_worst > 0.10 else 'consistent'}")

    # ---- Q2: weekly contrast against the observed anchor -----------------------------------
    print("\nQ2  WEEKLY CONTRAST -- Saturday / Weekday mean retail presence")
    print("    (observed time-use has retail presence clearly weekend-peaked; a 2030 source that")
    print("     flattens or inverts this has lost the signal the retail channel carries)")
    print(f"    {'PR':<5}{'OBS':>10}{'RAW':>10}{'CAL':>10}{'RAW/OBS':>10}{'CAL/OBS':>10}")
    verdict_q2 = []
    for grp in ("ALL", "QC", "AB"):
        def ratio(src):
            wd, sa = float(np.nanmean(src[(1, grp)])), float(np.nanmean(src[(2, grp)]))
            return sa / wd if wd else float("nan")
        o, r, c = ratio(OBS), ratio(RAW), ratio(CAL)
        print(f"    {grp:<5}{o:>10.3f}{r:>10.3f}{c:>10.3f}{r/o:>10.3f}{c/o:>10.3f}")
        verdict_q2.append(abs(r / o - 1.0))
    print(f"    worst |RAW/OBS - 1| = {max(verdict_q2):.3f}  -> "
          f"{'MATERIAL: RAW does not preserve the observed weekly contrast' if max(verdict_q2) > 0.25 else 'preserved'}")

    print("\nWHAT PROPAGATES, and what does not -- stated so Q2 is not over-read:")
    print("  Retail is injected as `multiplier` = 0.95 x peak-normalised shape")
    print("  (commercial_integration.py:1311), and build_retail_product_2030 normalises each")
    print("  (Day_Type, PR) group by ITS OWN base peak. So the Saturday/weekday LEVEL contrast in")
    print("  Q2 is divided out and never reaches EnergyPlus -- in either source. Q2 is evidence")
    print("  about which artefact is trustworthy, NOT a claim that energy moves.")
    print("  What DOES propagate is the within-day shape and the peak HOUR (the clock columns in")
    print("  Q1). Any energy claim needs a simulated cell, not this table.")


if __name__ == "__main__":
    main()
