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

d = prep("g8r")                                   # retail lever made degenerate (mirror of G8o)
a = pd.read_csv(f"{d}/agg_annual.csv")
m = a.scenario.isin(["sens_retail_cons", "sens_retail_opt"]) & (a.channel == "retail")
ref = a[(a.scenario == "B_central") & (a.channel == "retail")].groupby(["building","city","end_use","fuel"]).energy_J.first()
a.loc[m, "energy_J"] = a[m].apply(lambda r: ref.get((r.building, r.city, r.end_use, r.fuel), r.energy_J), axis=1)
a.to_csv(f"{d}/agg_annual.csv", index=False); CASES["G8r"] = d

d = prep("peakretail")                            # retail peaks at 03:00 (mirror of S9-PEAK-office)
p = pd.read_csv(f"{d}/agg_peak.csv"); p.loc[p.channel == "retail", "peak_hour_circular"] = 3.0
p.to_csv(f"{d}/agg_peak.csv", index=False)
di = pd.read_csv(f"{d}/agg_diurnal.csv")
mk = (di.channel == "retail"); di.loc[mk, "hour"] = (di.loc[mk, "hour"] + 15) % 24
di.to_csv(f"{d}/agg_diurnal.csv", index=False); CASES["S9-PEAK-retail"] = d

d = prep("coinc")                                 # stacked peak above the sum of channel peaks
p = pd.read_csv(f"{d}/agg_peak.csv"); p["coincidence_factor"] = 1.15
p.to_csv(f"{d}/agg_peak.csv", index=False); CASES["S9-COINC"] = d

d = prep("area")                                  # Tag-2 census misses 5 % of the floor area
mt = pd.read_csv(f"{d}/agg_meta.csv"); mt["unclassified_area_m2"] = mt.total_building_area_m2 * .05
mt.to_csv(f"{d}/agg_meta.csv", index=False); CASES["S9-AREA"] = d

for _ch in ("retail", "office", "hotel"):         # each banded channel pushed out of its band
    d = prep(f"eui_{_ch}")                        # (on the real campaign office/hotel already FAIL;
    a = pd.read_csv(f"{d}/agg_annual.csv")        #  the fixture has them PASS, so they need a case
    a.loc[a.channel == _ch, "energy_J"] *= 3.0    #  too or the coverage check below stays red)
    a.to_csv(f"{d}/agg_annual.csv", index=False); CASES[f"S9-EUI-{_ch}"] = d

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

# S9-LONG-UNINJECTED (T9-8) -- this gate does NOT read --agg-dir at all: it imports
# 3rdJ_08D_campaign_cells.py from a path fixed relative to the Step9 script itself
# (_load_campaign_cells_module()), so perturbing agg_*.csv cannot touch it. The only way to
# perturb what this gate actually checks is to perturb that module's own
# DELIBERATE_CHANNEL_EXCEPTIONS constant -- make a historical era (Y2015) wrongly claim hotel as
# an EXPECTED channel, exactly the task instruction ("perturb the expected/excluded channel list
# so a historical cell carries a hotel channel"). This mutates the real Step-8 source file for the
# duration of one subprocess call and restores it byte-for-byte in a `finally`, verified after
# restore -- a probe must never leave the pipeline it is testing in a different state than it
# found it.
CC_PATH = os.path.abspath(os.path.join(os.path.dirname(S9), "..", "Step8_docs",
                                        "3rdJ_08D_campaign_cells.py"))
_orig_cc = open(CC_PATH, encoding="utf-8").read()
_needle = '"Y2015": frozenset(ALL_CHANNELS - {"hotel"}),'
_pert_cc = _orig_cc.replace(_needle, '"Y2015": frozenset(ALL_CHANNELS),')
assert _pert_cc != _orig_cc, ("DELIBERATE_CHANNEL_EXCEPTIONS text has changed upstream -- update "
                               "this probe's _needle before trusting S9-LONG-UNINJECTED's PASS")
d = prep("longuninj")
try:
    with open(CC_PATH, "w", encoding="utf-8") as f:
        f.write(_pert_cc)
    st_longuninj = run(d, d + "_out")
finally:
    with open(CC_PATH, "w", encoding="utf-8") as f:
        f.write(_orig_cc)
    _restored = open(CC_PATH, encoding="utf-8").read()
    assert _restored == _orig_cc, ("RESTORE FAILED -- 3rdJ_08D_campaign_cells.py was left modified "
                                    "by the falsifiability probe; fix this before doing anything else")
PRECOMPUTED = {"S9-LONG-UNINJECTED": st_longuninj}
CASES["S9-LONG-UNINJECTED"] = None   # sentinel: already run above, not via the generic agg-dir path

print(f"{'gate':<20}{'baseline':<10}{'perturbed':<10}  verdict")
ok = True
all_st = {}
for gate, d in CASES.items():
    st = PRECOMPUTED[gate] if d is None else run(d, d + "_out")
    all_st[gate] = st
    good = base.get(gate) == "PASS" and st.get(gate) == "FAIL"
    ok &= good
    print(f"{gate:<20}{base.get(gate,'-'):<10}{st.get(gate,'-'):<10}  {'SEEN FAILING' if good else '*** NOT FALSIFIABLE ***'}")
print("\nALL NAMED GATES FALSIFIABLE" if ok else "\n*** SOME NAMED GATES COULD NOT BE MADE TO FAIL ***")

# -- COVERAGE ------------------------------------------------------------------------------
# The table above only checks the ONE gate each case is named for. That is not the same question
# as "is every PASS gate covered by some perturbation?" -- and the difference is not academic:
# on 2026-07-31 this probe reported 13/13 SEEN FAILING while G8r (one of the three headline G8
# gates) and S9-PEAK-retail had never been made to fail by anything. A gate nobody perturbs is
# indistinguishable from a gate that cannot fail. Fold coverage into the exit status so a future
# gate added without a case is loud instead of silent.
seen_failing = {g for st in all_st.values() for g in base
                if base[g] == "PASS" and st.get(g) == "FAIL"}
never = sorted(g for g, s in base.items() if s == "PASS" and g not in seen_failing)
covered = sorted(g for g, s in base.items() if s == "PASS" and g in seen_failing)
print(f"\nCOVERAGE -- {len(covered)}/{len(covered) + len(never)} baseline-PASS gates were made to "
      f"fail by at least one perturbation (a case often flips more than the gate it is named for)")
if never:
    ok = False
    print(f"*** {len(never)} PASS GATE(S) NEVER SEEN FAILING BY ANY CASE: {', '.join(never)} ***")
    print("*** Their PASS is not yet evidence. Add a perturbation before quoting the scorecard. ***")
else:
    print("every baseline-PASS gate has been seen failing")

# INFO gates carry no PASS/FAIL claim, so no perturbation can flip them and none is attempted --
# say so explicitly, so their absence from the table above is not mistaken for missed coverage.
info_gates = sorted(g for g, s in base.items() if s == "INFO")
untested_info = [g for g in info_gates if g not in CASES]
print(f"\nINFO gates (no PASS/FAIL claim, out of this probe's scope by design, "
      f"{len(untested_info)}): {', '.join(untested_info)}")
