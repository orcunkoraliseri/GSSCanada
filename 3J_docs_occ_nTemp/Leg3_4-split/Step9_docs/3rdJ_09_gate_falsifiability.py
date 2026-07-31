"""Every Step-9 gate must be SEEN FAILING on a controlled perturbation before its PASS counts."""
import os, shutil, subprocess, json, sys, pandas as pd, numpy as np
SRC, S9 = "fake_agg", r"C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step9_docs\3rdJ_09_activityDrivenLoads_4split.py"
def run(d, out):
    subprocess.run([sys.executable, S9, "--agg-dir", d, "--outdir", out],
                   capture_output=True, text=True)
    return {g["gate"]: g["status"] for g in json.load(open(os.path.join(out, "step9_gates.json")))}
def prep(name):
    d = f"pert_{name}"
    if os.path.isdir(d): shutil.rmtree(d)
    shutil.copytree(SRC, d)
    return d
base = run(SRC, "pert_base_out")
CASES = {}

d = prep("g8o")                                   # office lever made degenerate
a = pd.read_csv(f"{d}/agg_annual.csv")
m = a.scenario.isin(["sens_office_cons", "sens_office_opt"]) & (a.channel == "office")
ref = a[(a.scenario == "B_central") & (a.channel == "office")].groupby(["building","city","end_use","fuel"]).energy_J.first()
a.loc[m, "energy_J"] = a[m].apply(lambda r: ref.get((r.building, r.city, r.end_use, r.fuel), r.energy_J), axis=1)
a.to_csv(f"{d}/agg_annual.csv", index=False); CASES["G8o"] = d

d = prep("coinc")                                 # stacked peak above the sum of channel peaks
p = pd.read_csv(f"{d}/agg_peak.csv"); p["coincidence_factor"] = 1.15
p.to_csv(f"{d}/agg_peak.csv", index=False); CASES["S9-COINC"] = d

d = prep("area")                                  # Tag-2 census misses 5 % of the floor area
mt = pd.read_csv(f"{d}/agg_meta.csv"); mt["unclassified_area_m2"] = mt.total_building_area_m2 * .05
mt.to_csv(f"{d}/agg_meta.csv", index=False); CASES["S9-AREA"] = d

d = prep("eui")                                   # retail pushed far out of its as-modelled band
a = pd.read_csv(f"{d}/agg_annual.csv"); a.loc[a.channel == "retail", "energy_J"] *= 3.0
a.to_csv(f"{d}/agg_annual.csv", index=False); CASES["S9-EUI-retail"] = d

d = prep("peak")                                  # office peaks at 03:00
p = pd.read_csv(f"{d}/agg_peak.csv"); p.loc[p.channel == "office", "peak_hour_circular"] = 3.0
p.to_csv(f"{d}/agg_peak.csv", index=False)
di = pd.read_csv(f"{d}/agg_diurnal.csv")
mk = (di.channel == "office"); di.loc[mk, "hour"] = (di.loc[mk, "hour"] + 15) % 24
di.to_csv(f"{d}/agg_diurnal.csv", index=False); CASES["S9-PEAK-office"] = d

d = prep("we")                                    # office busier at the weekend than on weekdays
di = pd.read_csv(f"{d}/agg_diurnal.csv")
di.loc[(di.channel == "office") & (di.daytype == "WE"), "W"] *= 12.0
di.to_csv(f"{d}/agg_diurnal.csv", index=False); CASES["S9-WE-office"] = d

d = prep("cells")                                 # one cell missing from the aggregation
for f in ("agg_meta.csv",):
    t = pd.read_csv(f"{d}/{f}"); t.iloc[:-1].to_csv(f"{d}/{f}", index=False)
CASES["S9-CELLS"] = d

d = prep("schema")                                # two output schemas mixed in one campaign
mt = pd.read_csv(f"{d}/agg_meta.csv"); mt.loc[0, "OUTPUT_SCHEMA_HASH"] = "deadbeef"
mt.to_csv(f"{d}/agg_meta.csv", index=False); CASES["S9-SCHEMA"] = d

d = prep("plat")                                  # cells from two platforms compared
mt = pd.read_csv(f"{d}/agg_meta.csv"); mt.loc[0, "PLATFORM"] = "linux"
mt.to_csv(f"{d}/agg_meta.csv", index=False); CASES["S9-PLATFORM"] = d

d = prep("long")                                  # era axis flattened
a = pd.read_csv(f"{d}/agg_annual.csv")
r = a[a.scenario == "Y2015"].groupby(["building","city","channel","end_use","fuel"]).energy_J.first()
mk = a.scenario.isin(["Y2005","Y2010","Y2022"])
a.loc[mk, "energy_J"] = a[mk].apply(lambda x: r.get((x.building,x.city,x.channel,x.end_use,x.fuel), x.energy_J), axis=1)
a.to_csv(f"{d}/agg_annual.csv", index=False); CASES["S9-LONG-office"] = d

d = prep("residev")                               # residential occupancy made midday-dominant
di = pd.read_csv(f"{d}/agg_diurnal.csv")
mk = (di.channel == "residential") & (di.metric == "people")
di.loc[mk, "hour"] = (di.loc[mk, "hour"] + 12) % 24   # rotate evening rise onto midday
di.to_csv(f"{d}/agg_diurnal.csv", index=False); CASES["S9-PEAK-residential"] = d

d = prep("inject")                                # injection no longer changes the SHAPE
di = pd.read_csv(f"{d}/agg_diurnal.csv")
mt = pd.read_csv(f"{d}/agg_meta.csv")
basecells = set(mt.loc[mt.scenario == "Default_NECB", "cell_tag"])
mk = (di.channel == "residential") & (di.metric == "people") & (~di.cell_tag.isin(basecells))
src = di[(di.channel == "residential") & (di.metric == "people") & (di.cell_tag.isin(basecells))]
lut = src.groupby(["season", "daytype", "hour"])["W"].mean()
di.loc[mk, "W"] = [lut.get((r.season, r.daytype, r.hour), r.W) for r in di[mk].itertuples()]
di.to_csv(f"{d}/agg_diurnal.csv", index=False); CASES["S9-INJECTION"] = d

print(f"{'gate':<20}{'baseline':<10}{'perturbed':<10}  verdict")
ok = True
for gate, d in CASES.items():
    st = run(d, d + "_out")
    good = base.get(gate) == "PASS" and st.get(gate) == "FAIL"
    ok &= good
    print(f"{gate:<20}{base.get(gate,'-'):<10}{st.get(gate,'-'):<10}  {'SEEN FAILING' if good else '*** NOT FALSIFIABLE ***'}")
print("\nALL GATES FALSIFIABLE" if ok else "\n*** SOME GATES COULD NOT BE MADE TO FAIL ***")
