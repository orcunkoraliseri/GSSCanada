"""P10 step 4: weekday at-home (residential) and at-work (office) levels by clock hour, 2022 vs 2030,
from (a) the schedule products the frozen cells injected, (b) the survey frames behind them.

Read-only. Clock hour convention = the Step-7 one: 48 half-hour slots from 04:00, pairs averaged,
np.roll(+4) (3rdJ_07_aug_to_bem_4split.py:325-331, :447-449).
"""
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
BASE = J3.parent
S7 = J3 / "Leg3_4-split/Step7_docs/outputs_step7"
AUG = J3 / "Leg3_4-split/Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv"
C_V2 = J3 / "Leg3_4-split/Step6_docs/outputs_step6/2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv"
LOOKUP = BASE / "0_Occupancy/processed/office_archetype_lookup.csv"
HOM = [f"hom30_{i:03d}" for i in range(1, 49)]
WRK = [f"wrk30_{i:03d}" for i in range(1, 49)]
BIZH = list(range(9, 17))   # clock 09:00-17:00


def to_clock(v48):
    return np.roll(np.asarray(v48, float).reshape(24, 2).mean(axis=1), 4)


def fmt(v):
    return " ".join(f"{x:.3f}" for x in v)


def summ(lbl, v):
    v = np.asarray(v)
    print(f"  {lbl:58s} day={v.mean():.4f}  09-17h={v[BIZH].mean():.4f}")
    return v


out = {}
print("=" * 100)
print("RESIDENTIAL -- schedule products (Occupancy_Schedule, unweighted mean over SIM_HH_ID)")
res_files = {
    "Y2022 injected  BEM_Schedules_4split_2022.csv (281d96c0)": "BEM_Schedules_4split_2022.csv",
    "2030 cons       BEM_Schedules_4split_2030_cons.csv (df94ff6a)": "BEM_Schedules_4split_2030_cons.csv",
    "2030 central    BEM_Schedules_4split_2030_central.csv (d36388c8)": "BEM_Schedules_4split_2030_central.csv",
    "2030 opt        BEM_Schedules_4split_2030_opt.csv (4462726d)": "BEM_Schedules_4split_2030_opt.csv",
    "2030 central pre-v2 (_C) BAK_2026-07-30 (043e0727)": "BEM_Schedules_4split_2030_central_BAK_2026-07-30.csv",
}
for lbl, f in res_files.items():
    d = pd.read_csv(S7 / f, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
    for dt in ("Weekday", "Weekend"):
        v = d[d.Day_Type == dt].groupby("Hour").Occupancy_Schedule.mean().reindex(range(24)).values
        out[(lbl, dt)] = v
    summ(lbl + " WD", out[(lbl, "Weekday")])
    summ(lbl + " WE", out[(lbl, "Weekend")])
k22 = list(res_files)[0]
kc = list(res_files)[2]
print("\n  Weekday hourly, Y2022  :", fmt(out[(k22, 'Weekday')]))
print("  Weekday hourly, central:", fmt(out[(kc, 'Weekday')]))
print("  Weekday hourly, diff pp:", " ".join(f"{100*x:+.1f}" for x in out[(kc, 'Weekday')] - out[(k22, 'Weekday')]))

print("\n" + "=" * 100)
print("RESIDENTIAL -- the survey frames (person-level hom30, weekday, clock hours)")
a = pd.read_csv(AUG, low_memory=False, usecols=["CYCLE_YEAR", "IS_SYNTHETIC", "DDAY_STRATA", "LFTAG", "NOCS", "AGEGRP"] + HOM + WRK)
d30 = pd.read_csv(C_V2, low_memory=False, usecols=["BAND", "DDAY_STRATA", "LFTAG", "NOCS", "AGEGRP"] + HOM + WRK)
awd = a[a.DDAY_STRATA == 1]
frames = {
    "AUG all cycles, all rows (= frame of the Y2022 product)": awd,
    "AUG CYCLE 2022 only, all rows": awd[awd.CYCLE_YEAR == 2022],
    "AUG CYCLE 2022 real only (= Step-6 obs22 anchor)": awd[(awd.CYCLE_YEAR == 2022) & (awd.IS_SYNTHETIC == 0)],
    "AUG CYCLE 2005 real": awd[(awd.CYCLE_YEAR == 2005) & (awd.IS_SYNTHETIC == 0)],
    "AUG CYCLE 2010 real": awd[(awd.CYCLE_YEAR == 2010) & (awd.IS_SYNTHETIC == 0)],
    "AUG CYCLE 2015 real": awd[(awd.CYCLE_YEAR == 2015) & (awd.IS_SYNTHETIC == 0)],
    "AUG pre-2022 cycles, all rows": awd[awd.CYCLE_YEAR < 2022],
}
for b in ("conservative", "hybrid", "fullyhybrid"):
    w = d30[(d30.BAND == b) & (d30.DDAY_STRATA == 1)]
    frames[f"2030 _C_v2 {b}, all LFTAG (= frame of 2030 residential)"] = w
    frames[f"2030 _C_v2 {b}, LFTAG==1 only"] = w[w.LFTAG == 1]
    frames[f"2030 _C_v2 {b}, LFTAG==3 only"] = w[w.LFTAG == 3]
fr_h = {}
for lbl, df in frames.items():
    fr_h[lbl] = summ(f"{lbl} n={len(df)}", to_clock(df[HOM].to_numpy(float).mean(0)))
print("\n  person-level weekday WORK (all slots, day mean) for the same frames:")
for lbl, df in frames.items():
    print(f"  {lbl:70s} wrk day-mean={df[WRK].to_numpy(float).mean():.4f}")

print("\n  cycle composition of the Y2022 product frame (AUG all rows):",
      a.CYCLE_YEAR.value_counts().sort_index().to_dict(),
      " synthetic share %.2f%%" % (100 * a.IS_SYNTHETIC.mean()))
print("  LFTAG composition AUG (weekday):", awd.LFTAG.value_counts(dropna=False).sort_index().to_dict())
print("  LFTAG composition 2030 hybrid (weekday):",
      d30[(d30.BAND == 'hybrid') & (d30.DDAY_STRATA == 1)].LFTAG.value_counts(dropna=False).sort_index().to_dict())
print("  AGEGRP AUG weekday:", awd.AGEGRP.value_counts(dropna=False).sort_index().to_dict())
print("  AGEGRP 2030 hybrid weekday:",
      d30[(d30.BAND == 'hybrid') & (d30.DDAY_STRATA == 1)].AGEGRP.value_counts(dropna=False).sort_index().to_dict())

print("\n" + "=" * 100)
print("OFFICE -- Office_Knowledge (the archetype every campaign cell injects), AT_WORK_fraction")
off = {
    "Y2022 injected office_presence_multiplier_2022.csv (ff0fc987)": ("office_presence_multiplier_2022.csv", "observed"),
}
for b in ("conservative", "hybrid", "fullyhybrid"):
    off[f"2030 {b} INJECTED _BAK_2026-08-02 (1536c98c, pool-direct)"] = ("office_presence_multiplier_2030_BAK_2026-08-02.csv", b)
    off[f"2030 {b} current (575d17e5, stock-matched, NOT injected)"] = ("office_presence_multiplier_2030.csv", b)
for lbl, (f, band) in off.items():
    d = pd.read_csv(S7 / f)
    for dt in ("Weekday", "Weekend"):
        s = d[(d.office_archetype == "Office_Knowledge") & (d.BAND == band) & (d.Day_Type == dt)].sort_values("Hour")
        out[(lbl, dt)] = s.AT_WORK_fraction.values
    n = int(s.n_persons.iloc[0])
    summ(f"{lbl} WD n={n}", out[(lbl, 'Weekday')])
    summ(f"{lbl} WE", out[(lbl, 'Weekend')])

lk = pd.read_csv(LOOKUP)
kn = set(lk[(lk.is_office == True) & (lk.archetype_label == "Office_Knowledge")].NOCS)
print("\n  Office_Knowledge employed (LFTAG 1/2), weekday, person-level wrk30 by frame:")
for lbl, df in (("AUG all cycles (= frame of Y2022 office)", awd),
                ("AUG CYCLE 2022 real only (= obs22 anchor)", awd[(awd.CYCLE_YEAR == 2022) & (awd.IS_SYNTHETIC == 0)]),
                ("AUG CYCLE 2022 all rows", awd[awd.CYCLE_YEAR == 2022]),
                ("AUG pre-2022 real", awd[(awd.CYCLE_YEAR < 2022) & (awd.IS_SYNTHETIC == 0)])):
    s = df[df.NOCS.isin(kn) & df.LFTAG.isin([1, 2])]
    summ(f"{lbl} n={len(s)}", to_clock(s[WRK].to_numpy(float).mean(0)))

pd.to_pickle(out, Path(__file__).with_suffix(".pkl"))
