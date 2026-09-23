"""P10 step 3: reproduce the Table-6 "-10.51 pp" and the Step-6 metric of record from the files.

Definition tried first (from Step8_docs/3rdJ_08_implementation_improvements.md "Defaut 4" table,
row "Post-calibration, livrable 2030 _C vs OBS2022"): population-pooled work presence = mean of
wrk30_001..048 over all rows (all BAND, all DDAY_STRATA, all LFTAG) of the 2030 _C file, minus the
same mean over OBS2022 = AUG[CYCLE_YEAR==2022 & IS_SYNTHETIC==0]. Cohen's d on per-person day-means,
pooled SD. Read-only.

Negative control: the same code on a deliberately wrong anchor (AUG all 2022 rows, contaminated) and
on the wrong 2030 file must NOT give -10.51.
"""
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
AUG = J3 / "Leg3_4-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
S6 = J3 / "Leg3_4-split/Step6_docs/outputs_step6"
C_OLD = S6 / "2030_synthetic_diaries_4split_calibrated_mindwell_C.csv"      # 7c105ef3
C_V2 = S6 / "2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv"    # 5aa74f44
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
BIZ = list(range(10, 26))
NONBIZ = [i for i in range(48) if i not in BIZ]

meta = ["CYCLE_YEAR", "IS_SYNTHETIC", "DDAY_STRATA", "LFTAG"]
a = pd.read_csv(AUG, low_memory=False, usecols=meta + WRK + HOM)
obs22 = a[(a.CYCLE_YEAR == 2022) & (a.IS_SYNTHETIC == 0)]
all22 = a[a.CYCLE_YEAR == 2022]
syn22 = a[(a.CYCLE_YEAR == 2022) & (a.IS_SYNTHETIC == 1)]
hist = a[(a.CYCLE_YEAR < 2022) & (a.IS_SYNTHETIC == 0)]


def dm(df, cols=WRK):
    return df[cols].to_numpy(float).mean(axis=1)


def delta(x, y, cols=WRK):
    """x minus y, in pp, and Cohen's d (pooled SD) on per-person day-means."""
    a1, b1 = dm(x, cols), dm(y, cols)
    sp = np.sqrt(((len(a1) - 1) * a1.var(ddof=1) + (len(b1) - 1) * b1.var(ddof=1)) / (len(a1) + len(b1) - 2))
    return 100 * (a1.mean() - b1.mean()), (a1.mean() - b1.mean()) / sp, a1.mean(), b1.mean()


print(f"OBS2022 n={len(obs22)}  all-2022 n={len(all22)}  SYN2022 n={len(syn22)}  hist-obs n={len(hist)}")
print("pre-cal SYN2022 vs OBS2022 : %+.2f pp d=%+.3f  (%.4f vs %.4f)" % delta(syn22, obs22))

for tag, p in (("OLD _C 7c105ef3", C_OLD), ("NEW _C_v2 5aa74f44", C_V2)):
    d = pd.read_csv(p, low_memory=False, usecols=["BAND", "DDAY_STRATA", "LFTAG"] + WRK + HOM)
    print(f"\n== {tag}: rows={len(d)}")
    print("  2030 vs OBS2022, pooled   : %+.2f pp d=%+.3f  (%.4f vs %.4f)" % delta(d, obs22))
    print("  2030 vs hist obs 05/10/15 : %+.2f pp d=%+.3f" % delta(d, hist)[:2])
    for b in ("conservative", "hybrid", "fullyhybrid"):
        print(f"  band {b:12s} vs OBS2022 : %+.2f pp d=%+.3f" % delta(d[d.BAND == b], obs22)[:2])
    # negative controls: wrong anchor
    print("  NEG CTRL vs contaminated all-2022 anchor: %+.2f pp" % delta(d, all22)[0])
    # metric of record: weekday, LFTAG==1, 2022-only real anchor, per slot group
    o = obs22[(obs22.DDAY_STRATA == 1) & (obs22.LFTAG == 1)]
    w = d[(d.DDAY_STRATA == 1) & (d.LFTAG == 1)]
    for lbl, idx in (("nonBIZ32", NONBIZ), ("all48", list(range(48))), ("BIZ16", BIZ)):
        cols = [WRK[i] for i in idx]
        print(f"  metric of record WD LFTAG1 {lbl:8s}: %+.2f pp" % delta(w, o, cols)[0])
    # composition
    wd = d[d.DDAY_STRATA == 1]
    print("  weekday LFTAG==1 share in 2030 pool: %d/%d = %.2f%%" % ((wd.LFTAG == 1).sum(), len(wd), 100 * (wd.LFTAG == 1).mean()))
    print("  LFTAG counts (all rows):", d.LFTAG.value_counts(dropna=False).sort_index().to_dict())

for lbl, df in (("AUG all cycles", a), ("OBS2022", obs22)):
    wd = df[df.DDAY_STRATA == 1]
    print("\n%s weekday LFTAG==1 share: %d/%d = %.2f%%" % (lbl, (wd.LFTAG == 1).sum(), len(wd), 100 * (wd.LFTAG == 1).mean()))
