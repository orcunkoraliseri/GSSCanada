"""P10 step 6: cross-check from the frozen cells' channel_hourly.csv (people columns).

Hour index: row r of channel_hourly.csv = hour r of the 2006 run period, RunPeriod starts Sunday
(injected_resized.idf RunPeriod, 'Day of Week for Start Day' = Sunday), no holidays. Weekday =
day-of-week Mon..Fri. Business hours = rows with hour-of-day 9..16 (09:00-17:00). DST is applied
by the IDF, so summer schedule hours are shifted by one; this is a cross-check, not a re-derivation.

Also: are the 27 residential households the same in Y2022 and 2030 cells? And the expected
people ratio from the schedule products restricted to those 27 households (HHSIZE-weighted).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
CELLS = J3 / "Leg3_4-split/Step8_docs/campaign_local_deliverable"
S7 = J3 / "Leg3_4-split/Step7_docs/outputs_step7"
H8 = J3 / "Leg3_4-split/Step8_docs/outputs_step8/historical_schedules"

hrs = np.arange(8760)
dow = (hrs // 24) % 7          # 0 = Sunday
hod = hrs % 24
wd = (dow >= 1) & (dow <= 5)
biz = wd & (hod >= 9) & (hod <= 16)

prod = {"Y2005": H8 / "BEM_Schedules_4split_2005.csv", "Y2010": H8 / "BEM_Schedules_4split_2010.csv",
        "Y2015": H8 / "BEM_Schedules_4split_2015.csv", "Y2022": S7 / "BEM_Schedules_4split_2022.csv",
        "B_cons": S7 / "BEM_Schedules_4split_2030_cons.csv", "B_central": S7 / "BEM_Schedules_4split_2030_central.csv",
        "B_opt": S7 / "BEM_Schedules_4split_2030_opt.csv"}
pcache = {}


def prod_expect(scen, hh_ids):
    if scen not in pcache:
        pcache[scen] = pd.read_csv(prod[scen], usecols=["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "Occupancy_Schedule"])
    d = pcache[scen]
    d = d[d.SIM_HH_ID.isin(hh_ids) & (d.Day_Type == "Weekday")]
    d = d.assign(p=d.HHSIZE * d.Occupancy_Schedule)
    g = d.groupby("Hour").p.sum()
    return g.reindex(range(24)).values


rows = []
for bld in ("Tall", "SuperTall"):
    for city in ("MTL", "CLG"):
        hh = {}
        for scen in ("Y2005", "Y2010", "Y2015", "Y2022", "B_cons", "B_central", "B_opt"):
            cell = CELLS / f"{scen}__{bld}__{city}"
            ch = pd.read_csv(cell / "channel_hourly.csv", usecols=["office_people", "residential_people"])
            man = json.load(open(cell / "manifest.json", encoding="utf-8"))
            ids = [int(v) for v in man["inject_mixed_use_result"]["residential"]["assignment"].values()]
            hh[scen] = ids
            e = prod_expect(scen, ids)
            rows.append(dict(cell=f"{bld}__{city}", scen=scen,
                             res_people_wd_biz=ch.residential_people.values[biz].mean(),
                             res_people_wd_day=ch.residential_people.values[wd].mean(),
                             off_people_wd_biz=ch.office_people.values[biz].mean(),
                             prod_res_people_wd_biz=e[9:17].mean(), prod_res_people_wd_day=e.mean()))
        same = all(hh[s] == hh["Y2022"] for s in hh)
        print(f"{bld}__{city}: same 27 households in all 7 scenarios? {same}")
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.round(3).to_string(index=False))
print("\nRatios to Y2022 (weekday 09-17h):")
for c, g in df.groupby("cell"):
    g = g.set_index("scen")
    for s in ("Y2015", "B_cons", "B_central", "B_opt"):
        print(f"  {c:16s} {s:10s} residential cell {g.loc[s,'res_people_wd_biz']/g.loc['Y2022','res_people_wd_biz']:.3f}"
              f"  product(27HH) {g.loc[s,'prod_res_people_wd_biz']/g.loc['Y2022','prod_res_people_wd_biz']:.3f}"
              f"  | office cell {g.loc[s,'off_people_wd_biz']/g.loc['Y2022','off_people_wd_biz']:.3f}")
df.to_csv(Path(__file__).with_suffix(".csv"), index=False)
