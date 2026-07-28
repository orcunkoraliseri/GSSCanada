"""diag_retail_optvcentral.py -- PURE READ-ONLY diagnostic (does NOT edit driver/injector,
does NOT rerun any simulation). Explains why probe cells B_central (retail=central) and
var_retail (retail=opt) produced byte-identical hourly_meters.csv (job 1169679, P1/P2 FAIL).

Answers, in order: (1) did the driver read different retail CSVs for cell1/cell3? (2) do
the CSVs differ in the PR=QC rows the loader consumes? (3) do the resulting injected
Schedule:Compact objects (MXU_Retail_People_B_central vs MXU_Retail_People_var_retail,
and any separate Lights/Equip retail schedules) differ numerically? (4) verdict.
"""
import json
import os

import numpy as np
import pandas as pd

SCRATCH8 = "/speed-scratch/o_iseri/step8_4split"
CAMP = SCRATCH8 + "/probes/campaign_5670f602"
STEP7 = SCRATCH8 + "/upload/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7"
RETAIL_CENTRAL = STEP7 + "/retail_presence_multiplier_2030_central.csv"
RETAIL_OPT = STEP7 + "/retail_presence_multiplier_2030_opt.csv"

CELLS = {"B_central": 1, "var_retail": 3}

print("=" * 78)
print("Q1: manifest.json retail csv path / md5 / injected_idf_md5 per cell")
print("=" * 78)
manifests = {}
for tag in CELLS:
    mpath = os.path.join(CAMP, tag, "manifest.json")
    with open(mpath, "r", encoding="utf-8") as f:
        m = json.load(f)
    manifests[tag] = m
    r = m["channels_requested"]["retail"]
    print(f"[{tag}] retail.csv_path = {r['csv_path']}")
    print(f"[{tag}] retail.csv_md5  = {r['csv_md5']}")
    print(f"[{tag}] modulated_schedule_names = {m['inject_mixed_use_result']['modulated_schedule_names']}")
    print(f"[{tag}] injected_idf_md5 = {m['injected_idf_md5']}")
same_csv = manifests["B_central"]["channels_requested"]["retail"]["csv_md5"] == \
           manifests["var_retail"]["channels_requested"]["retail"]["csv_md5"]
print(f"-> driver pointed cells at the SAME retail csv? {same_csv}")

print()
print("=" * 78)
print("Q2: do the two source CSVs differ in the PR=QC rows the loader consumes?")
print("=" * 78)
df_c = pd.read_csv(RETAIL_CENTRAL)
df_o = pd.read_csv(RETAIL_OPT)
print(f"central: shape={df_c.shape} cols={list(df_c.columns)}")
print(f"opt    : shape={df_o.shape} cols={list(df_o.columns)}")

sub_c = df_c[df_c["PR"] == "QC"].sort_values(["Day_Type", "slot"]).reset_index(drop=True)
sub_o = df_o[df_o["PR"] == "QC"].sort_values(["Day_Type", "slot"]).reset_index(drop=True)
print(f"QC subset shapes: central={sub_c.shape} opt={sub_o.shape}")

if sub_c.shape != sub_o.shape:
    print("QC subsets have DIFFERENT shapes -- cannot row-align, stopping Q2 comparison here.")
else:
    for col in sub_c.columns:
        a, b = sub_c[col], sub_o[col]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            d = (a - b).abs()
            print(f"  col={col:22s} numeric  max|delta|={d.max():.6g}  n_differing={(d > 1e-12).sum()}")
        else:
            n_diff = int((a.astype(str) != b.astype(str)).sum())
            print(f"  col={col:22s} non-numeric  n_differing={n_diff}")

qc_multiplier_identical = False
if sub_c.shape == sub_o.shape:
    qc_multiplier_identical = np.allclose(sub_c["multiplier"].values, sub_o["multiplier"].values, atol=1e-12)
print(f"-> QC 'multiplier' column identical between central and opt? {qc_multiplier_identical}")

print()
print("=" * 78)
print("Q3: do the injected Schedule:Compact objects differ numerically?")
print("=" * 78)
from eppy.modeleditor import IDF  # noqa: E402

eplus_idd = os.environ.get("EPLUS_IDD", "")
IDF.setiddname(eplus_idd)


def extract_numeric_sequence(obj):
    """obj.obj = ['Schedule:Compact', Name, 'Fraction', 'Through: ...', 'For: ...',
    'Until: HH:MM', value, ...]. Keep only the numeric value tokens, in order."""
    raw = obj.obj
    vals = []
    for field in raw[3:]:
        s = str(field).strip()
        if s.startswith("Through:") or s.startswith("For:") or s.startswith("Until:"):
            continue
        vals.append(float(s))
    return vals


idfs = {}
sched_by_tag = {}
all_retail_sched_names = {}
for tag in CELLS:
    idf_path = os.path.join(CAMP, tag, "injected.idf")
    idf = IDF(idf_path)
    idfs[tag] = idf
    scs = idf.idfobjects.get("SCHEDULE:COMPACT", [])
    names = [getattr(o, "Name", "") for o in scs]
    retail_names = sorted(n for n in names if "Retail" in n)
    all_retail_sched_names[tag] = retail_names
    want = f"MXU_Retail_People_{tag}"
    match = [o for o in scs if getattr(o, "Name", "") == want]
    if not match:
        print(f"[{tag}] ERROR: schedule '{want}' NOT FOUND among Schedule:Compact objects")
        continue
    sched_by_tag[tag] = match[0]
    print(f"[{tag}] all Schedule:Compact names containing 'Retail': {retail_names}")

if len(sched_by_tag) == 2:
    seq_c = extract_numeric_sequence(sched_by_tag["B_central"])
    seq_o = extract_numeric_sequence(sched_by_tag["var_retail"])
    print(f"[B_central] MXU_Retail_People_B_central   len={len(seq_c)}")
    print(f"[var_retail] MXU_Retail_People_var_retail len={len(seq_o)}")
    if len(seq_c) == len(seq_o):
        arr_c, arr_o = np.array(seq_c), np.array(seq_o)
        d = np.abs(arr_c - arr_o)
        print(f"-> max|delta| between the two PEOPLE schedules = {d.max():.6g}")
        diff_idx = np.where(d > 1e-9)[0]
        print(f"-> n_differing positions = {len(diff_idx)}")
        for i in diff_idx[:5]:
            print(f"     pos {i}: central={arr_c[i]:.4f}  opt={arr_o[i]:.4f}  delta={d[i]:.4f}")
    else:
        print(f"-> LENGTH MISMATCH: cannot diff element-wise ({len(seq_c)} vs {len(seq_o)})")

# Only ONE schedule per channel is created by modulate_baseline() and it is wired to
# PEOPLE, LIGHTS and ELECTRICEQUIPMENT alike (commercial_integration.py inject_mixed_use,
# sch_names[channel] reused across all three obj_classes) -- so report whether a SEPARATE
# retail Lights/Equip schedule name exists at all, rather than assuming one.
print()
print("Separate retail LIGHTS/ELECTRICEQUIPMENT schedule check:")
for tag in CELLS:
    names = all_retail_sched_names[tag]
    extra = [n for n in names if n != f"MXU_Retail_People_{tag}"]
    print(f"[{tag}] retail Schedule:Compact names besides the PEOPLE one: {extra}")

print()
print("=" * 78)
print("VERDICT")
print("=" * 78)
if same_csv:
    print("(A) driver config bug -- both cells read the same retail CSV.")
elif sub_c.shape == sub_o.shape and qc_multiplier_identical:
    print("(B) QC subsets of the two Step-7 products are identical -- nothing to "
          "differentiate. Step-7 product problem, not a wiring problem.")
elif len(sched_by_tag) == 2 and len(seq_c) == len(seq_o) and np.abs(np.array(seq_c) - np.array(seq_o)).max() < 1e-9:
    print("(C) Products differ but injected schedules are identical -- the difference is "
          "lost inside load_retail_series()/modulate_baseline(). See Q2/Q3 numbers above "
          "for where.")
else:
    print("(D) Schedules differ but EnergyPlus output is byte-identical (per job 1169679 "
          "manifest md5s already confirmed identical) -- see Q3 numbers for the schedule-"
          "level diff magnitude.")
