"""FINDING 7 probe -- does the retail channel carry the SAME frame conflict as office (FINDING 6)?

Context. The user's decision of 2026-08-02 is methodological: every cycle's schedules must be drawn
onto the same sample frame. FINDING 6 fixed that for office. Retail has the identical *structural*
split -- `build_retail_product_2022(stock)` reads the augmented stock, while
`build_retail_product_2030(scenario)` reads the Step-6 lever files, which are built by POOLING the
three `2030_diaries_{band}_raw.csv` pools and never touch the stock at all.

But the two channels are not consumed the same way, and that is what bounds the damage:

    office  commercial_integration.py:1296-1297 -> reads AT_WORK_fraction   (a LEVEL)
    retail  commercial_integration.py:1311      -> reads multiplier         (0.95 x peak-normalised SHAPE)

A frame difference that shifts retail's whole profile up or down therefore CANCELS in the injected
schedule. Only a frame difference that changes the profile's SHAPE survives. This probe measures
which one we actually have, instead of assuming.

Design of the control -- the lesson from the FINDING 6 correction. `at_retail_fraction` is an
ALL-PERSONS activity rate, not an occupation-conditioned curve, so the valid stock-frame control is
`assemble_2030()`'s random within-stratum draw (exactly the frame residential already uses).
`demo_assemble_2030()` would be the WRONG control here for the mirror-image reason it was the right
one for office: NOCS-matching an all-persons aggregate conditions on something the quantity does not
depend on. The office correction of 2026-08-02 was caused by using a control without testing it, so
this probe reports the composition check that justifies its own control (see COMPOSITION below)
rather than asserting the choice is fine.

Reports, per (Day_Type, PR):
  LEVEL  mean ratio pool/stock                       -- cancels downstream, reported for the record
  SHAPE  max |A_norm - B_norm| and RMS, peak-normalised the way Step-7 normalises
  PEAK   the peak HOUR under each frame              -- a moved peak would be a real defect

Usage:  py -3 3rdJ_09E_retail_frame_probe.py
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
S6 = os.path.join(HERE, "..", "Step6_docs", "outputs_step6")

BANDS = ["conservative", "hybrid", "fullyhybrid"]
DAYTYPE3 = {1: "Weekday", 2: "Saturday", 3: "Sunday"}
# Step-7's own PR proxy: QC = region 2 (exact); AB = region 4 (Prairies) -- see
# build_retail_product_2022. Reproduced here so the control uses the SAME mapping.
PR_MAP = [("QC", 2), ("AB", 4)]


def load_step7():
    spec = importlib.util.spec_from_file_location("step7_mod", os.path.abspath(STEP7))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def norm(a):
    p = float(a.max())
    return a / p if p > 0 else np.zeros_like(a)


def main():
    m = load_step7()
    RET = m.RET

    # ---- A: the shipped 2030 base, exactly as build_retail_product_2030 reads it -------------
    lev = pd.read_csv(os.path.join(S6, "at_retail_fraction_2030_plateau.csv"))
    lev = lev[lev["PR_GROUP"].isin(["QC", "AB"])].copy()
    lev["Day_Type"] = lev["day_type"].map(
        {"weekday": "Weekday", "saturday": "Saturday", "sunday": "Sunday"})
    A = {}
    for (dt, pr), g in lev.groupby(["Day_Type", "PR_GROUP"]):
        g = g.sort_values("slot")
        A[(dt, pr)] = np.roll(g["at_retail_fraction_2030_base"].to_numpy(float), 8)

    # ---- B: the same quantity rebuilt on the STOCK frame, pooled over the 3 bands ------------
    # Step-6 pools the bands because retail is not banded by the office/WFH axis (validator gate
    # 5.27). The control pools the same way, so the only difference left is the frame.
    #
    # MEMORY: each assemble_2030() call materialises a full copy of the ~500 MB stock. They are
    # reduced to 48-length means and released one at a time -- never three at once. The local box
    # cannot be rebooted remotely, so a heavy local run gets a hard guard, not optimism.
    print("building the stock-frame control (3 bands x assemble_2030, reduced then released) ...",
          flush=True)
    acc, COMP, comp_rows = {}, {}, []
    for band in BANDS:
        asm = m.assemble_2030(band)
        asm["Day_Type3"] = asm["DDAY_STRATA"].map(DAYTYPE3)
        e = asm["LFTAG"].isin(m.EMPLOYED_LFTAG)
        comp_rows.append((band,
                          float(asm.loc[e, RET].mean(axis=1).mean()),
                          float(asm[RET].mean(axis=1).mean())))
        for pr_lbl, code in PR_MAP:
            for dt in ["Weekday", "Saturday", "Sunday"]:
                sub = asm[(asm["PR"] == code) & (asm["Day_Type3"] == dt)]
                if len(sub) == 0:
                    continue
                acc.setdefault((dt, pr_lbl), []).append(sub[RET].mean().to_numpy(float))
                COMP[(dt, pr_lbl)] = len(sub)
        del asm, e, sub
        gc.collect()

    B = {k: np.roll(np.mean(v, axis=0), 8) for k, v in acc.items()}

    # ---- COMPOSITION: justify the control instead of assuming it --------------------------
    # If the random draw destroyed the retail signal the way it destroyed the office one, the
    # control would be invalid and every number below meaningless. Test it the same way: compare
    # the mean retail rate of a sub-population that should differ from the whole.
    print("\nCOMPOSITION CHECK -- is the all-persons control valid for an all-persons quantity?")
    print("  (the office control failed exactly here; this is the test that catches it)")
    stock = pd.read_csv(m.AUG, low_memory=False, usecols=["LFTAG"] + RET)
    emp = stock["LFTAG"].isin(m.EMPLOYED_LFTAG)
    print(f"    real stock            : employed {stock.loc[emp, RET].mean(axis=1).mean():.6f}   "
          f"all {stock[RET].mean(axis=1).mean():.6f}")
    del stock, emp
    gc.collect()
    for band, e_mean, a_mean in comp_rows:
        print(f"    assemble({band:<12}): employed {e_mean:.6f}   all {a_mean:.6f}")
    print("  Read: employed-vs-all must stay SEPARATED after assembly. If they collapse to the")
    print("        same value the draw has homogenised the population and the control is dead.")

    # ---- the comparison --------------------------------------------------------------------
    print("\nRETAIL FRAME EFFECT -- shipped pool frame (A) vs stock frame (B)")
    print(f"  {'Day_Type':<10}{'PR':<5}{'n_stock':>9}{'lvl A':>9}{'lvl B':>9}"
          f"{'lvl B/A':>9}{'shape dmax':>12}{'shape rms':>11}{'peak hr A':>11}{'peak hr B':>11}")
    worst = 0.0
    for pr_lbl, _ in PR_MAP:
        for dt in ["Weekday", "Saturday", "Sunday"]:
            k = (dt, pr_lbl)
            if k not in A or k not in B:
                continue
            a, b = A[k], B[k]
            an, bn = norm(a), norm(b)
            dmax = float(np.abs(an - bn).max())
            rms = float(np.sqrt(((an - bn) ** 2).mean()))
            worst = max(worst, dmax)
            print(f"  {dt:<10}{pr_lbl:<5}{COMP[k]:>9}{a.mean():>9.4f}{b.mean():>9.4f}"
                  f"{b.mean()/a.mean() if a.mean() else float('nan'):>9.3f}"
                  f"{dmax:>12.4f}{rms:>11.4f}"
                  f"{int(np.argmax(a))//2:>11}{int(np.argmax(b))//2:>11}")

    print(f"\n  worst shape deviation across all 6 cells: {worst:.4f}")
    print("  Threshold for 'material', set BEFORE running (same discipline as the arm-E scorer):")
    print("    < 0.05  -> level-only difference; it cancels in `multiplier`, document as bounded")
    print("    >= 0.05 -> shape moves; the retail 2030 base has to be rebuilt on the stock frame")
    print(f"  VERDICT: {'BOUNDED (document)' if worst < 0.05 else 'MATERIAL (rebuild required)'}")


if __name__ == "__main__":
    main()
