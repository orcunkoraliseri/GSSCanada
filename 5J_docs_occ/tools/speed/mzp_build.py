# 5J multi-zone RE-PILOT, job 1 (Speed, Spain only): design table, household md5, 36 IDFs, gates, seen-failing.
# Usage: python -u mzp_build.py <expected_md5_of_presence_HH_es_07222.csv (local side)>
# Reads (Spanish only): R/design_in/{hids_es60,pilot_hids_es,dwelling_count_es}.csv, R/hh/*, multizone/repo/buildings.csv
# (Spanish rows only, verified below), multizone/repo/archetype_parameters_es.csv. No UK file is opened.
import csv, hashlib, io, json, math, os, random, re, sys, platform

R = "/speed-scratch/o_iseri/5J/mz_pilot/"
REPO = R + "repo/"
MZ0 = "/speed-scratch/o_iseri/5J/multizone/"     # read-only
PILOT = "/speed-scratch/o_iseri/5J/pilot/"       # read-only
EPW = PILOT + "epw/es_madrid_2009_2010_y2010.epw"
EPW_MD5 = "110b364912226ee4d2a5b5411eab81da"
sys.path.insert(0, REPO + "5J_docs_occ/tools")
print("python", sys.version.split()[0], "host", platform.node())
import importlib
mz = importlib.import_module("5thJ_idf_mz")
j5 = mz._j5
s8 = mz._s8
j5.TOOLS_4J = REPO + "4J_docs_occ/tools"
print("modules: 5thJ_idf_mz from", mz.__file__, "| 4thJ_step8_idf from", s8.__file__)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


print("MD5 tool 5thJ_idf_mz.py", md5(REPO + "5J_docs_occ/tools/5thJ_idf_mz.py"))
print("MD5 tool 4thJ_step8_idf.py (mine) %s (multizone copy) %s" % (md5(REPO + "4J_docs_occ/tools/4thJ_step8_idf.py"),
                                                                   md5(MZ0 + "repo/4J_docs_occ/tools/4thJ_step8_idf.py")))
assert md5(EPW) == EPW_MD5, md5(EPW)
print("EPW md5 OK", EPW_MD5)
exp = sys.argv[1]
got = md5(R + "hh/presence/presence_HH_es_07222.csv")
print("STAGING_MD5_ONE_FILE local=%s speed=%s %s" % (exp, got, "PASS" if exp == got else "FAIL"))
assert exp == got

# ---- Spanish building rows only ---------------------------------------------------------------
os.makedirs(R + "design", exist_ok=True)
os.makedirs(R + "logs", exist_ok=True)
os.makedirs(R + "runs", exist_ok=True)
allrows = list(csv.DictReader(io.open(MZ0 + "repo/buildings.csv", encoding="utf-8")))
bad = [r["building_id"] for r in allrows if not r["building_id"].startswith("es_") or r["country"] != "es"]
print("BUILDINGS_CSV rows=%d non_spanish_rows=%d (must be 0; this file was already filtered to es by the builder task)"
      % (len(allrows), len(bad)))
assert not bad
bt = {r["building_id"]: r for r in allrows}
BUILDINGS = ["es_B07", "es_B16", "es_B21", "es_B33", "es_B37"]
rows, _ = s8.load_rows(MZ0 + "repo/", "es")
rowby = {r["Code_Building"]: r for r in rows}
TAB = R + "design_in/dwelling_count_es.csv"

# ---- households ----------------------------------------------------------------------------------
hids60 = [r["hid"] for r in csv.DictReader(io.open(R + "design_in/hids_es60.csv", encoding="utf-8"))]
pilot_hids = [r["hid"] for r in csv.DictReader(io.open(R + "design_in/pilot_hids_es.csv", encoding="utf-8"))]
assert len(hids60) == 60 and len(set(hids60)) == 60 and len(pilot_hids) == 10 and set(pilot_hids) <= set(hids60)
by_dw = {r["hid"]: r for r in csv.DictReader(io.open(R + "hh/enduse_by_dwelling_es.csv", encoding="utf-8"))}
H60IDF = R + "hh/step9_objects_es.idf"
md5lines = []
for h in hids60:
    for p in (R + "hh/presence/presence_HH_es_%s.csv" % h, R + "hh/elec/elec_HH_es_%s.csv" % h):
        assert os.path.exists(p), p
        md5lines.append("%s  %s" % (md5(p), p[len(R):]))
for p in (R + "hh/enduse_by_dwelling_es.csv", H60IDF):
    md5lines.append("%s  %s" % (md5(p), p[len(R):]))
io.open(R + "design/household_md5.txt", "w", encoding="utf-8", newline="\n").write("\n".join(md5lines) + "\n")
print("HOUSEHOLD_MD5 lines=%d (60 presence + 60 appliance + 2) written to design/household_md5.txt" % len(md5lines))
HH = {}
for h in hids60:
    peak_idf = j5._design_level_from_idf(H60IDF, h)
    peak_csv = float(by_dw[h]["elec_peak_w"])
    assert abs(peak_idf - peak_csv) < 0.005, (h, peak_idf, peak_csv)
    HH[h] = {"hid": h, "fold": "es", "n_members": int(by_dw[h]["n_members"]),
             "presence_csv": R + "hh/presence/presence_HH_es_%s.csv" % h,
             "appliance_csv": R + "hh/elec/elec_HH_es_%s.csv" % h, "appliance_peak_w": peak_idf,
             "peak_w_source": H60IDF}
print("HOUSEHOLDS built for %d hids (peak_w idf == csv within 0.005 W for all)" % len(HH))

# ---- Part B: the design ----------------------------------------------------------------------
info = {}
for b in BUILDINGS:
    br = bt[b]
    row = rowby[br["archetype_code"]]
    d = s8.derive(row)
    F = int(round(d["n_storey"]))
    k, n_apt, _ln = mz.k_from_tabula(TAB, d["code"], F)
    cls = d["cls"]
    assert cls == br["class"], (cls, br["class"])
    n_dw = 1 if cls in ("SFH", "TH") else F * k
    info[b] = {"row": row, "code": d["code"], "cls": cls, "F": F, "k": k, "n_dw": n_dw, "n_apt": n_apt,
               "ach": float(br["infiltration_ach"]), "north": float(br["north_axis_deg"]), "num": int(b.split("B")[1])}
    print("BUILDING %s code=%s class=%s floors=%d k=%d dwellings=%d (TABULA n_Apartment %g)" % (b, d["code"], cls, F, k, n_dw, n_apt))


def perm_placement(b, r):
    seed = 5000 + info[b]["num"] * 10 + r
    rng = random.Random(seed)
    order = []
    while len(order) < info[b]["n_dw"]:
        p = list(hids60)
        rng.shuffle(p)
        order.extend(p)
    return seed, order[:info[b]["n_dw"]]


design = []


def add(b, hid_list, replicate, seed):
    rid = "MZ%03d" % (len(design) + 1)
    design.append({"run_id": rid, "building_id": b, "class": info[b]["cls"], "k": info[b]["k"], "n_floors": info[b]["F"],
                   "n_dwellings": info[b]["n_dw"], "replicate": replicate, "seed": seed,
                   "placement": ";".join("%d:%s" % (j, h) for j, h in enumerate(hid_list))})


for b in ("es_B07", "es_B16"):
    for h in pilot_hids:
        add(b, [h], 0, "NA")
perms = {}
for b in ("es_B21", "es_B33", "es_B37"):
    for r in (1, 2):
        seed, order = perm_placement(b, r)
        perms[(b, r)] = (seed, order)
        add(b, order, 0, seed)
for rep in range(1, 6):
    add("es_B07", [pilot_hids[0]], rep, "NA")
for rep in range(1, 6):
    seed, order = perms[("es_B37", 1)]
    add("es_B37", order, rep, seed)
print("DESIGN runs=%d (expected 36: 20 SFH/TH + 6 MFH/AB + 10 replicates)" % len(design))
assert len(design) == 36
cols = ["run_id", "building_id", "class", "k", "n_floors", "n_dwellings", "replicate", "seed", "placement"]
with io.open(R + "design/mz_pilot_runs.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(cols)
    for d_ in design:
        w.writerow([d_[c] for c in cols])
print("DESIGN written R/design/mz_pilot_runs.csv")
# how many times does each household visit each floor position? (INFO for the report)
pos = {}
for d_ in design:
    if d_["n_dwellings"] > 1 and d_["replicate"] == 0:
        i = info[d_["building_id"]]
        for item in d_["placement"].split(";"):
            j, h = item.split(":")
            fl = int(j) // i["k"]
            pos.setdefault(h, set()).add((d_["building_id"], fl))
print("DESIGN_INFO households placed in a multi-dwelling run: %d of 60; distinct (building,floor) cells used: %d"
      % (len(pos), len({c for s in pos.values() for c in s})))

# ---- Part C: build -------------------------------------------------------------------------------
PATCH_NAMES = ["mz_geometry", "mz_areas", "mz_windows", "mz_mass", "mz_pairs", "mz_people", "mz_appliances", "mz_outputs"]
n_patch_total = 0
ok_all = True
manifest = []
for d_ in design:
    rid, b = d_["run_id"], d_["building_id"]
    i = info[b]
    placement = {int(x.split(":")[0]): HH[x.split(":")[1]] for x in d_["placement"].split(";")}
    _k, _n, kline = mz.k_from_tabula(TAB, i["code"], i["F"])
    assert _k == i["k"]
    idf, meta = mz.build_mz(i["row"], i["k"], placement, i["ach"], i["north"])
    got = [ln.split()[1] for ln in meta["patch_lines"]]
    miss = [p for p in PATCH_NAMES if p not in got]
    n_p = len(got) + 1                                   # + mz_k
    n_patch_total += n_p
    print("PATCHCHECK %s %s %s PATCH lines present=%d (8 builder + mz_k) missing=%s" % (rid, b, "PASS" if not miss else "FAIL", n_p, miss))
    ok_all &= not miss
    rd = R + "runs/%s/" % rid
    os.makedirs(rd, exist_ok=True)
    io.open(rd + "model.idf", "w", encoding="utf-8", newline="\n").write(idf)
    saved = io.open(rd + "model.idf", encoding="utf-8").read()
    res = mz.check_area_gates(saved, i["row"])
    npass = sum(1 for s, g, _ in res if s == "PASS")
    print("AREAGATES %s %s %d/%d PASS %s" % (rid, b, npass, len(res), "; ".join("%s %s" % (s, g) for s, g, _ in res if s != "PASS")))
    ok_all &= (npass == len(res))
    for s, g, det in res:
        if g.startswith("total_capacity"):
            print("%s %s %s %s" % (s, g, rid, det))
    meta["design_row"] = d_
    json.dump(meta, io.open(rd + "meta.json", "w", encoding="utf-8"), indent=1, default=str)
    manifest.append([rid, b, d_["class"], d_["k"], d_["n_floors"], d_["n_dwellings"], d_["replicate"], d_["seed"], d_["placement"],
                     rd + "model.idf", md5(rd + "model.idf"), EPW_MD5, "midnight", len(meta["zones"])])
print("PATCH_TOTAL lines=%d over %d IDFs (expected 36 x 9 = 324)" % (n_patch_total, len(design)))
ok_all &= (n_patch_total == 324)
with io.open(R + "run_manifest.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["run_id", "building_id", "class", "k", "n_floors", "n_dwellings", "replicate", "seed", "placement", "idf",
                "idf_md5", "epw_md5", "clock_origin", "n_zones"])
    for m in manifest:
        w.writerow(m)
print("MANIFEST %d runs" % len(manifest))

# ---- Part A gates: mass (all sides) on every mz IDF is above; seen failing + collapse byte-identity ----------------
rid = "MZ021"            # es_B21 run 1
assert [d_["building_id"] for d_ in design if d_["run_id"] == rid] == ["es_B21"]
saved = io.open(R + "runs/%s/model.idf" % rid, encoding="utf-8").read()
res_old_rule = mz.check_area_gates(saved, info["es_B21"]["row"], mass_rule="pairs_once")
cap = [(s, det) for s, g, det in res_old_rule if g == "total_capacity_eq_c_m_x_A_C_Ref"]
print("SEENFAIL_MASS_pairs_once %s total_capacity_eq_c_m_x_A_C_Ref on %s: %s -> %s"
      % (cap[0][0], rid, cap[0][1], "CONFIRMED (must FAIL)" if cap[0][0] == "FAIL" else "NOT FAILING"))
# also the same gate on the old-rule IDF built with pairs_once: it should PASS (the gate itself works)
old_idf, _om = mz.build_mz(info["es_B21"]["row"], info["es_B21"]["k"], {j: HH[pilot_hids[j % 10]] for j in range(info["es_B21"]["n_dw"])},
                           info["es_B21"]["ach"], info["es_B21"]["north"], mass_rule="pairs_once")
os.makedirs(R + "seenfail", exist_ok=True)
io.open(R + "seenfail/B21_pairs_once.idf", "w", encoding="utf-8", newline="\n").write(old_idf)
r2 = mz.check_area_gates(old_idf, info["es_B21"]["row"], mass_rule="pairs_once")
print("CONTROL_pairs_once_rule_IDF_with_pairs_once_gate %s" % [s for s, g, _ in r2 if g == "total_capacity_eq_c_m_x_A_C_Ref"])
r3 = mz.check_area_gates(old_idf, info["es_B21"]["row"], mass_rule="all_sides")
print("CONTROL_pairs_once_rule_IDF_with_all_sides_gate %s (the all-sides gate must FAIL on the old-rule IDF)"
      % [s for s, g, _ in r3 if g == "total_capacity_all_sides_eq_c_m_x_A_C_Ref"])

folders = sorted(os.listdir(PILOT + "inputs"))
byte_ok = True
for b in BUILDINGS:
    h = pilot_hids[0]
    cand = [f for f in folders if f.endswith("__es_" + h)]
    fdir = PILOT + "inputs/" + cand[0] + "/"
    txt = io.open(fdir + "in.idf", encoding="utf-8").read()
    m1 = re.search(r"HH_es_%s_People,[^;]*?\n\s+(\d+),\s+!- Number of People" % h, txt, re.S)
    m2 = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % h, txt, re.S)
    hh0 = {"hid": h, "fold": "es", "n_members": int(m1.group(1)), "presence_csv": fdir + "presence_HH_es_%s.csv" % h,
           "appliance_csv": fdir + "elec_HH_es_%s.csv" % h, "appliance_peak_w": float(m2.group(1)), "peak_w_source": fdir + "in.idf"}
    cidf, _cm = mz.build_mz(info[b]["row"], 1, {0: hh0}, info[b]["ach"], info[b]["north"], collapse=True)
    ref = open(MZ0 + "runs/%s__collapse/model.idf" % b, "rb").read()
    same = (cidf.encode("utf-8") == ref)
    byte_ok &= same
    print("%s collapse_byte_identical %s new_md5=%s builder_task_md5=%s" % ("PASS" if same else "FAIL", b,
          hashlib.md5(cidf.encode("utf-8")).hexdigest(), hashlib.md5(ref).hexdigest()))
ok_all &= byte_ok
# interior-sides counts for the report
for b in ("es_B21", "es_B33", "es_B37"):
    rdd = [d_["run_id"] for d_ in design if d_["building_id"] == b][0]
    mj = json.load(io.open(R + "runs/%s/meta.json" % rdd))
    print("MASS_INFO %s interior_sides=%d interior_side_area=%.4f capacity=%.1f target=%.1f" % (b, mj["interior_sides"], mj["interior_side_area"],
          mj["areas"]["capacity_j_per_k"], mz.C_M_J_M2K * mj["derive"]["a_ref"]))
print("ALL_BUILD_GATES", "PASS" if ok_all else "FAIL")
