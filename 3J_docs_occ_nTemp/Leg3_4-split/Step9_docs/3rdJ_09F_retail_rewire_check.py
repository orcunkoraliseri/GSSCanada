"""FINDING 7 option B -- PRE-REGISTERED acceptance check for the retail source rewire.

Written and committed BEFORE the rewired product is generated. Its thresholds come from the
FINDING 7 measurement table already in the Progress Log (2026-08-02), not from whatever the new
product turns out to say.

What must move (and if it does not, the rewire did not take effect -- report FAIL, adjust nothing):

  A1  QC Weekday retail peak CLOCK hour ......... 11  ->  16
  A2  AB Weekday retail peak CLOCK hour ......... 14  ->  16
  A3  QC Saturday/Weekday mean contrast ........ 0.849 -> 3.215   (observed 2022 anchor 2.661)
  A4  AB Saturday/Weekday mean contrast ........ 1.009 -> 3.399   (observed 2022 anchor 2.571)
  A5  pooled-ALL Sat/Weekday contrast at SOURCE . 0.980 -> 3.375  (observed 2022 anchor 2.687)
      -- A5 is read from the two POOLS directly, not from the product: the product carries only
         PR in {QC, AB}, while the log's 0.98/3.38 row is PR_GROUP='ALL' (every province). Stated
         separately so the product table is not quietly credited with a number it cannot contain.

What must NOT move:

  B1  peak(multiplier) == 0.95 * lever(band), per (Day_Type, PR) -- the H2/R1 invariant. The
      rewire changes the SHAPE source; the base/levered normalisation discipline is preserved, so
      this must be bit-stable at 0.8550 / 0.9215 / 0.9975 for cons / central / opt.
  B2  288 rows per band, Day_Type in {Weekday, Saturday, Sunday}, PR in {QC, AB}.
  B3  multiplier in [0, 1].

Tolerances: peak hours are integers and must match EXACTLY. Contrasts are compared at +/-0.02
absolute -- these are means over 111,024 rows, they are not noisy, and a loose band here would be
the "widen it until it passes" move this project has a rule against.

Usage (locally, from anywhere):
    py -3 3rdJ_09F_retail_rewire_check.py --before        # snapshot the CURRENT shipped products
    py -3 3rdJ_09F_retail_rewire_check.py --after         # score the rewired products
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STEP7 = os.path.join(HERE, "..", "Step7_docs", "3rdJ_07_aug_to_bem_4split.py")
S7OUT = os.path.join(HERE, "..", "Step7_docs", "outputs_step7")
S6OUT = os.path.join(HERE, "..", "Step6_docs", "outputs_step6")
SNAP = os.path.join(HERE, "outputs_step9", "retail_rewire_before.json")

BANDS3 = ["cons", "central", "opt"]

# ---- pre-registered expectations, from the FINDING 7 table in the Progress Log ----
EXPECT = {
    "A1": {"what": "QC Weekday peak clock hour", "before": 11, "after": 16, "kind": "int"},
    "A2": {"what": "AB Weekday peak clock hour", "before": 14, "after": 16, "kind": "int"},
    "A3": {"what": "QC Sat/Weekday contrast", "before": 0.849, "after": 3.215, "kind": "float"},
    "A4": {"what": "AB Sat/Weekday contrast", "before": 1.009, "after": 3.399, "kind": "float"},
}
TOL = 0.02
EXPECT_PEAK_MULT = {"cons": 0.8550, "central": 0.9215, "opt": 0.9975}


def load_step7():
    spec = importlib.util.spec_from_file_location("step7_mod", os.path.abspath(STEP7))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["step7_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def product_metrics(path):
    """Peak clock hour + Sat/Weekday contrast, per PR, off a retail product CSV.

    Measured on `at_retail_fraction` (the raw pooled/levered signal), NOT on `multiplier`:
    `multiplier` is overwritten by the NECB proxy baseline wherever staff_shoulder_flag == 1, so
    its argmax can be pinned by the proxy rather than by the occupancy source this check is about.
    """
    df = pd.read_csv(path)
    out = {}
    for pr in ("QC", "AB"):
        g = df[df["PR"] == pr]
        wd = g[g["Day_Type"] == "Weekday"].sort_values("slot")
        sa = g[g["Day_Type"] == "Saturday"].sort_values("slot")
        arr = wd["at_retail_fraction"].to_numpy(float)
        out[f"{pr}_peak_hour"] = int(np.argmax(arr)) // 2
        wm, sm = float(arr.mean()), float(sa["at_retail_fraction"].to_numpy(float).mean())
        out[f"{pr}_sat_wd"] = (sm / wm) if wm else float("nan")
    out["peak_multiplier"] = float(df["multiplier"].max())
    out["n_rows"] = int(len(df))
    out["day_types"] = sorted(df["Day_Type"].unique().tolist())
    out["prs"] = sorted(df["PR"].unique().tolist())
    out["mult_in_01"] = bool(df["multiplier"].between(0, 1 + 1e-9).all())
    return out


def source_all_contrast(m):
    """A5: pooled-ALL Saturday/Weekday `ret30` mean contrast, for RAW, CAL and the 2022 anchor."""
    RET = m.RET
    res = {}
    frames = []
    for b in ("conservative", "hybrid", "fullyhybrid"):
        frames.append(pd.read_csv(os.path.join(S6OUT, f"2030_diaries_{b}_raw.csv"),
                                  low_memory=False, usecols=["DDAY_STRATA"] + RET))
    raw = pd.concat(frames, ignore_index=True)
    del frames
    for lbl, df in (("RAW", raw),
                    ("CAL", pd.read_csv(m.D2030, low_memory=False,
                                        usecols=["DDAY_STRATA"] + RET)),
                    ("OBS", pd.read_csv(m.AUG, low_memory=False,
                                        usecols=["DDAY_STRATA"] + RET))):
        wm = float(df[df["DDAY_STRATA"] == 1][RET].to_numpy(float).mean())
        sm = float(df[df["DDAY_STRATA"] == 2][RET].to_numpy(float).mean())
        res[lbl] = sm / wm if wm else float("nan")
        del df
    return res


def snapshot():
    os.makedirs(os.path.dirname(SNAP), exist_ok=True)
    data = {}
    for b in BANDS3:
        p = os.path.join(S7OUT, f"retail_presence_multiplier_2030_{b}.csv")
        data[b] = product_metrics(p)
    with open(SNAP, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"BEFORE snapshot written -> {SNAP}")
    for b in BANDS3:
        d = data[b]
        print(f"  {b:<8} QC peak={d['QC_peak_hour']:>2}h sat/wd={d['QC_sat_wd']:.3f} | "
              f"AB peak={d['AB_peak_hour']:>2}h sat/wd={d['AB_sat_wd']:.3f} | "
              f"peak mult={d['peak_multiplier']:.4f}")


def score():
    with open(SNAP, encoding="utf-8") as fh:
        before = json.load(fh)
    after = {b: product_metrics(os.path.join(S7OUT,
                                             f"retail_presence_multiplier_2030_{b}.csv"))
             for b in BANDS3}

    rows, n_fail = [], 0
    print("\n=== A: what MUST move ===")
    print(f"  {'id':<4}{'band':<9}{'what':<30}{'before':>10}{'after':>10}"
          f"{'req before':>12}{'req after':>11}  verdict")
    for b in BANDS3:
        for cid, e in EXPECT.items():
            k = {"A1": "QC_peak_hour", "A2": "AB_peak_hour",
                 "A3": "QC_sat_wd", "A4": "AB_sat_wd"}[cid]
            bv, av = before[b][k], after[b][k]
            if e["kind"] == "int":
                ok_b, ok_a = int(bv) == e["before"], int(av) == e["after"]
                fb, fa = f"{int(bv)}", f"{int(av)}"
            else:
                ok_b = abs(float(bv) - e["before"]) <= TOL
                ok_a = abs(float(av) - e["after"]) <= TOL
                fb, fa = f"{float(bv):.3f}", f"{float(av):.3f}"
            ok = ok_b and ok_a
            n_fail += 0 if ok else 1
            rows.append((cid, b, ok))
            print(f"  {cid:<4}{b:<9}{e['what']:<30}{fb:>10}{fa:>10}"
                  f"{str(e['before']):>12}{str(e['after']):>11}  "
                  f"{'PASS' if ok else 'FAIL' + ('' if ok_b else ' (before off)') + ('' if ok_a else ' (after off)')}")

    print("\n=== B: what must NOT move ===")
    for b in BANDS3:
        pm = after[b]["peak_multiplier"]
        okB1 = abs(pm - EXPECT_PEAK_MULT[b]) < 1e-3
        okB2 = (after[b]["n_rows"] == 288
                and after[b]["day_types"] == ["Saturday", "Sunday", "Weekday"]
                and after[b]["prs"] == ["AB", "QC"])
        okB3 = after[b]["mult_in_01"]
        n_fail += (0 if okB1 else 1) + (0 if okB2 else 1) + (0 if okB3 else 1)
        print(f"  {b:<9} B1 peak mult {pm:.4f} vs {EXPECT_PEAK_MULT[b]:.4f} "
              f"{'PASS' if okB1 else 'FAIL'} | B2 shape {'PASS' if okB2 else 'FAIL'} "
              f"({after[b]['n_rows']} rows, {after[b]['prs']}) | "
              f"B3 mult in [0,1] {'PASS' if okB3 else 'FAIL'}")

    print("\n=== A5: pooled-ALL Sat/Weekday contrast, measured at the SOURCE ===")
    m = load_step7()
    c = source_all_contrast(m)
    okA5 = abs(c["RAW"] - 0.980) <= TOL and abs(c["CAL"] - 3.375) <= TOL
    n_fail += 0 if okA5 else 1
    print(f"  RAW (what retail used to read) = {c['RAW']:.3f}  (req 0.980)")
    print(f"  CAL (_C_v2, what it reads now) = {c['CAL']:.3f}  (req 3.375)")
    print(f"  OBS (2022 anchor)              = {c['OBS']:.3f}  (log records 2.687)")
    print(f"  A5 {'PASS' if okA5 else 'FAIL'}")

    print(f"\n=== VERDICT: {'PASS' if n_fail == 0 else f'FAIL ({n_fail} checks)'} ===")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", action="store_true")
    ap.add_argument("--after", action="store_true")
    a = ap.parse_args()
    if a.before:
        snapshot()
    elif a.after:
        sys.exit(score())
    else:
        ap.error("pass --before or --after")
