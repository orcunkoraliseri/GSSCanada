"""P10R: weekday/weekend levels of the new Step-7 products next to the frozen ones (read-only summary).
Residential: hourly HH-mean Occupancy_Schedule, WD 09-17h = clock h 9..16 (as P10 / gate a).
Office: Office_Knowledge AT_WORK_fraction.  Retail: at_retail_fraction day-mean per Day_Type (QC, AB)."""
from pathlib import Path
import pandas as pd, numpy as np
J3 = Path(__file__).resolve().parents[4]
OLD = J3 / "Leg3_4-split/Step7_docs/outputs_step7"
NEW = J3 / "Leg3_4-split/Step7_docs/outputs_step7_P10R"
BIZ = list(range(9, 17))
def res(p):
    d = pd.read_csv(p, usecols=["Day_Type", "Hour", "Occupancy_Schedule"])
    r = {dt: d[d.Day_Type == dt].groupby("Hour").Occupancy_Schedule.mean().reindex(range(24)).values for dt in ("Weekday", "Weekend")}
    return f"WD day={r['Weekday'].mean():.4f} WD09-17={r['Weekday'][BIZ].mean():.4f} WE day={r['Weekend'].mean():.4f}"
def off(p, band):
    d = pd.read_csv(p); d = d[(d.office_archetype == "Office_Knowledge") & (d.BAND == band)]
    wd = d[d.Day_Type == "Weekday"].sort_values("Hour").AT_WORK_fraction.values
    we = d[d.Day_Type == "Weekend"].sort_values("Hour").AT_WORK_fraction.values
    return f"WD day={wd.mean():.4f} WD09-17={wd[BIZ].mean():.4f} WE day={we.mean():.4f} n={int(d.n_persons.max())}"
def ret(p):
    d = pd.read_csv(p)
    return " ".join(f"{pr}/{dt[:3]}={g.at_retail_fraction.mean():.4f}" for (pr, dt), g in d.groupby(["PR", "Day_Type"]))
print("RESIDENTIAL")
for f in ["BEM_Schedules_4split_2022.csv"] + [f"BEM_Schedules_4split_2030_{b}.csv" for b in ("cons", "central", "opt")]:
    print(f"  {f:40s} OLD {res(OLD / f)}\n  {'':40s} NEW {res(NEW / f)}")
print("OFFICE (Office_Knowledge)")
old30 = OLD / "office_presence_multiplier_2030_BAK_2026-08-02.csv"   # the file the frozen cells injected (1536c98c)
print(f"  2022 observed   OLD {off(OLD / 'office_presence_multiplier_2022.csv', 'observed')}\n  {'':15s} NEW {off(NEW / 'office_presence_multiplier_2022.csv', 'observed')}")
for b in ("conservative", "hybrid", "fullyhybrid"):
    print(f"  2030 {b:12s} OLD(injected) {off(old30, b)}\n  {'':17s} NEW {off(NEW / 'office_presence_multiplier_2030.csv', b)}")
print("RETAIL at_retail_fraction day-mean")
print(f"  2022 OLD {ret(OLD / 'retail_presence_multiplier_2022.csv')}\n  2022 NEW {ret(NEW / 'retail_presence_multiplier_2022.csv')}")
for b in ("cons", "central", "opt"):
    print(f"  2030 {b:7s} OLD(injected) {ret(OLD / f'retail_presence_multiplier_2030_{b}_BAK_2026-08-02.csv')}\n  2030 {b:7s} NEW {ret(NEW / f'retail_presence_multiplier_2030_{b}.csv')}")
