"""P10 step 5: in-memory counterfactual products on ONE frame (no file written, no simulation).

CF-2022-anchor : stock AUG + diaries from the Step-6 anchor (AUG CYCLE_YEAR==2022 & IS_SYNTHETIC==0),
                 assembled with the SAME function the frozen Y2005/2010/2015 products use
                 (3rdJ_08A_gen_historical_products_4split.py::demo_assemble), then Step-7 convert().
CF-2030-matched: stock AUG + 2030 _C_v2 diaries matched on AGEGRP/SEX/LFTAG/NOCS
                 (3rdJ_07_aug_to_bem_4split.py::demo_assemble_2030, the function Step 7 already uses
                 for the post-FINDING-6 office product), then convert().
Control        : shipped assemble_2030() path re-run in memory must reproduce the shipped
                 BEM_Schedules_4split_2030_central.csv weekday means (proves the reader).
All functions are imported from the frozen scripts; nothing is re-implemented.
"""
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pandas as pd

J3 = Path(__file__).resolve().parents[4]
S8 = J3 / "Leg3_4-split/Step8_docs/3rdJ_08A_gen_historical_products_4split.py"
spec = importlib.util.spec_from_file_location("h08a", S8)
h08a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h08a)
step7 = h08a.step7
S7 = step7.OUT_DIR
BIZH = list(range(9, 17))


def res_levels(bem):
    r = {}
    for dt in ("Weekday", "Weekend"):
        v = bem[bem.Day_Type == dt].groupby("Hour").Occupancy_Schedule.mean().reindex(range(24)).values
        r[dt] = v
    return r


def pr(lbl, r):
    print(f"  {lbl:60s} WD day={r['Weekday'].mean():.4f} 09-17h={r['Weekday'][BIZH].mean():.4f} | "
          f"WE day={r['Weekend'].mean():.4f} 09-17h={r['Weekend'][BIZH].mean():.4f}", flush=True)


def off_levels(off, band):
    r = {}
    for dt in ("Weekday", "Weekend"):
        s = off[(off.office_archetype == "Office_Knowledge") & (off.BAND == band) & (off.Day_Type == dt)].sort_values("Hour")
        r[dt] = s.AT_WORK_fraction.values
    return r


stock = pd.read_csv(step7.AUG, low_memory=False)
d30 = pd.read_csv(step7.D2030, low_memory=False)
lookup = pd.read_csv(step7.LOOKUP_OFFICE)
results = {}

# --- shipped products, read back (reference) ---
for lbl, f in (("SHIPPED Y2022 (281d96c0)", "BEM_Schedules_4split_2022.csv"),
               ("SHIPPED 2030 central (d36388c8)", "BEM_Schedules_4split_2030_central.csv")):
    results[lbl] = res_levels(pd.read_csv(S7 / f, usecols=["Day_Type", "Hour", "Occupancy_Schedule"]))
    pr(lbl, results[lbl])

# --- control: shipped 2030 path re-run in memory ---
print("\n[CONTROL] assemble_2030(hybrid) in memory (must equal the shipped central file)", flush=True)
bem_ctrl = step7.convert(step7.complete_day_types(step7.assemble_2030("hybrid")))
results["CONTROL re-run 2030 central"] = res_levels(bem_ctrl)
pr("CONTROL re-run 2030 central", results["CONTROL re-run 2030 central"])
shipped = pd.read_csv(S7 / "BEM_Schedules_4split_2030_central.csv", usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"])
m = shipped.merge(bem_ctrl[["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"]], on=["SIM_HH_ID", "Day_Type", "Hour"], suffixes=("_s", "_c"))
print(f"  CONTROL row match: {len(m)}/{len(shipped)} rows joined; max |diff| = {np.abs(m.Occupancy_Schedule_s - m.Occupancy_Schedule_c).max():.4f}")
# negative control: the same comparison against the Y2022 file must show a large difference
y22 = pd.read_csv(S7 / "BEM_Schedules_4split_2022.csv", usecols=["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"])
m2 = y22.merge(bem_ctrl[["SIM_HH_ID", "Day_Type", "Hour", "Occupancy_Schedule"]], on=["SIM_HH_ID", "Day_Type", "Hour"], suffixes=("_s", "_c"))
print(f"  NEG CONTROL (vs Y2022 file): mean |diff| = {np.abs(m2.Occupancy_Schedule_s - m2.Occupancy_Schedule_c).mean():.4f} (must be >> 0)")

# --- CF-2022-anchor ---
print("\n[CF-2022-anchor] stock + obs22 (CYCLE 2022, real) via 08A demo_assemble", flush=True)
pool22 = stock[(stock.CYCLE_YEAR == 2022) & (stock.IS_SYNTHETIC == 0)].copy()
asm22 = h08a.demo_assemble(stock, pool22)
bem22 = step7.convert(step7.complete_day_types(asm22))
results["CF Y2022 on anchor frame"] = res_levels(bem22)
pr("CF Y2022 on anchor frame (2022 real diaries, stock HHs)", results["CF Y2022 on anchor frame"])
off22 = step7.build_office_multiplier(asm22, "observed", lookup)
o = off_levels(off22, "observed")
print(f"  CF office Office_Knowledge 2022-anchor WD day={o['Weekday'].mean():.4f} 09-17h={o['Weekday'][BIZH].mean():.4f} | "
      f"WE day={o['Weekend'].mean():.4f}")
results["CF office 2022 anchor"] = o

# --- CF-2030-matched ---
for band in ("conservative", "hybrid", "fullyhybrid"):
    print(f"\n[CF-2030-matched] {band}: stock + 2030 diaries matched on AGEGRP/SEX/LFTAG/NOCS", flush=True)
    asm = step7.demo_assemble_2030(stock, d30[d30.BAND == band].copy())
    bem = step7.convert(step7.complete_day_types(asm))
    k = f"CF 2030 {band} matched"
    results[k] = res_levels(bem)
    pr(k, results[k])

print("\nWEEKDAY HOURLY (clock h 0..23)")
for k in ("SHIPPED Y2022 (281d96c0)", "CF Y2022 on anchor frame", "SHIPPED 2030 central (d36388c8)", "CF 2030 hybrid matched"):
    print(f"  {k:40s}", " ".join(f"{x:.3f}" for x in results[k]["Weekday"]))
pd.to_pickle(results, Path(__file__).with_suffix(".pkl"))
