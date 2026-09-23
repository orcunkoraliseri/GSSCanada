"""P10 step 7: are the Step-6 2030 calibration targets built on the same population frame they are
applied to? Stage B is conditioned on LFTAG==1 (3rdJ_06_calibrate_C_4split.py:455,461-462).
Stages C0 (weekend work, :532-535), C1 (weekend home, :644-647) and RETAIL (:732-737) take their
target from ALL obs22 rows and apply it to ALL 2030 rows. obs22 is a labour-force frame (LFTAG 1/2
only); the 2030 pool is ~44 % LFTAG==3. Measure, per LFTAG stratum, the 2030 _C_v2 level against
the obs22 level. Read-only.
"""
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
AUG = J3 / "Leg3_4-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
C_V2 = J3 / "Leg3_4-split/Step6_docs/outputs_step6/2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv"
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
RET = [f"ret30_{i:03d}" for i in range(1, 49)]
cols = ["DDAY_STRATA", "LFTAG"]
a = pd.read_csv(AUG, low_memory=False, usecols=cols + ["CYCLE_YEAR", "IS_SYNTHETIC"] + HOM + WRK + RET)
o = a[(a.CYCLE_YEAR == 2022) & (a.IS_SYNTHETIC == 0)]
d = pd.read_csv(C_V2, low_memory=False, usecols=cols + ["BAND"] + HOM + WRK + RET)


def m(df, c):
    return df[c].to_numpy(float).mean() if len(df) else float("nan")


print("obs22 LFTAG counts:", o.LFTAG.value_counts(dropna=False).to_dict())
for name, strata in (("WEEKEND (2,3)", [2, 3]), ("WEEKDAY (1)", [1])):
    print(f"\n== {name}   (day-mean over 48 slots; pp vs obs22 same stratum)")
    oo = o[o.DDAY_STRATA.isin(strata)]
    print(f"  obs22 ALL rows       n={len(oo):5d} home={m(oo,HOM):.4f} work={m(oo,WRK):.4f} retail={m(oo,RET):.4f}")
    for lf in (1, 2):
        s = oo[oo.LFTAG == lf]
        print(f"  obs22 LFTAG={lf}        n={len(s):5d} home={m(s,HOM):.4f} work={m(s,WRK):.4f} retail={m(s,RET):.4f}")
    for b in ("conservative", "hybrid", "fullyhybrid"):
        dd = d[(d.BAND == b) & d.DDAY_STRATA.isin(strata)]
        print(f"  2030 {b:12s} ALL n={len(dd):5d} home={m(dd,HOM):.4f} ({100*(m(dd,HOM)-m(oo,HOM)):+.2f}) "
              f"work={m(dd,WRK):.4f} ({100*(m(dd,WRK)-m(oo,WRK)):+.2f}) retail={m(dd,RET):.4f} ({100*(m(dd,RET)-m(oo,RET)):+.2f})")
        for lf in (1, 2, 3):
            s = dd[dd.LFTAG == lf]
            ol = oo[oo.LFTAG == lf] if lf in (1, 2) else oo
            tag = "vs obs22 same LFTAG" if lf in (1, 2) else "vs obs22 ALL (no LFTAG=3 in anchor)"
            print(f"      LFTAG={lf} n={len(s):5d} home={m(s,HOM):.4f} ({100*(m(s,HOM)-m(ol,HOM)):+.2f}) "
                  f"work={m(s,WRK):.4f} ({100*(m(s,WRK)-m(ol,WRK)):+.2f}) retail={m(s,RET):.4f} ({100*(m(s,RET)-m(ol,RET)):+.2f})  [{tag}]")
