# 5J multizone Part C, job 1: build IDFs, area gates, seen-failing gate tests. Runs on Speed. Spain only.
import csv, io, json, math, os, re, sys, platform
R = "/speed-scratch/o_iseri/5J/multizone/"
REPO = R + "repo/"
PILOT = "/speed-scratch/o_iseri/5J/pilot/"
sys.path.insert(0, REPO + "5J_docs_occ/tools")
print("python", sys.version.split()[0], "host", platform.node())
import importlib
mz = importlib.import_module("5thJ_idf_mz")
j5 = mz._j5
s8 = mz._s8
j5.TOOLS_4J = REPO + "4J_docs_occ/tools"   # runtime override of the wrapper hard-coded Windows path (md5 of the 4J tool only)
print("modules: 5thJ_idf_mz from", mz.__file__, "| 4thJ_step8_idf from", s8.__file__)
BUILDINGS = ["es_B07", "es_B16", "es_B21", "es_B33", "es_B37"]
PATCH_NAMES = ["mz_geometry", "mz_areas", "mz_windows", "mz_mass", "mz_pairs", "mz_people", "mz_appliances",
               "mz_outputs"]

bt = {}
for r in csv.DictReader(io.open(REPO + "buildings.csv", encoding="utf-8")):
    if r["building_id"] in BUILDINGS:
        bt[r["building_id"]] = r
assert sorted(bt) == sorted(BUILDINGS), sorted(bt)
rows, _ = s8.load_rows(REPO, "es")
rowby = {r["Code_Building"]: r for r in rows}
cnt = {}
for r in csv.DictReader(io.open(R + "tabula/dwelling_count_es.csv", encoding="utf-8")):
    cnt.setdefault(r["code"], set()).add(r["n_dwellings_tabula"])
hids = [r["hid"] for r in csv.DictReader(io.open(REPO + "pilot_hids_es.csv", encoding="utf-8"))]
assert len(hids) == 10, hids
inputs = PILOT + "inputs/"
folders = sorted(os.listdir(inputs))
HH = []
for h in hids:
    cand = [f for f in folders if f.endswith("__es_" + h)]
    assert cand, "no pilot folder for " + h
    fdir = inputs + cand[0] + "/"
    txt = io.open(fdir + "in.idf", encoding="utf-8").read()
    m1 = re.search(r"HH_es_%s_People,[^;]*?\n\s+(\d+),\s+!- Number of People" % h, txt, re.S)
    m2 = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % h, txt, re.S)
    assert m1 and m2, "People/ElectricEquipment not found for " + h
    hh = {"hid": h, "fold": "es", "n_members": int(m1.group(1)), "presence_csv": fdir + "presence_HH_es_%s.csv" % h,
          "appliance_csv": fdir + "elec_HH_es_%s.csv" % h, "appliance_peak_w": float(m2.group(1)),
          "peak_w_source": fdir + "in.idf"}
    assert os.path.exists(hh["presence_csv"]) and os.path.exists(hh["appliance_csv"])
    HH.append(hh)
    print("HOUSEHOLD %s members=%d design_w=%.4f read_from=%s" % (h, hh["n_members"], hh["appliance_peak_w"], cand[0]))

os.makedirs(R + "runs", exist_ok=True)
os.makedirs(R + "seenfail", exist_ok=True)
manifest = []
ok_all = True
meta_out = {}
for b in BUILDINGS:
    br = bt[b]
    row = rowby[br["archetype_code"]]
    ach, north = float(br["infiltration_ach"]), float(br["north_axis_deg"])
    d = s8.derive(row)
    F = int(round(d["n_storey"]))
    cls = d["cls"]
    vals = cnt.get(d["code"])
    if cls in ("SFH", "TH"):
        k, basis = 1, "SFH/TH k=1 by design"
    else:
        n_dw_t = float(sorted(vals)[0])
        k = max(1, int(math.floor(n_dw_t / F + 0.5)))
        basis = "TABULA n_Apartment=%g / n_Storey=%d = %.4f -> k=%d (half up) [not a test-only k]" % (n_dw_t, F, n_dw_t / F, k)
    n_dw = 1 if cls in ("SFH", "TH") else F * k
    placement = {j: HH[j % 10] for j in range(n_dw)}
    print("BUILDING %s code=%s class=%s floors=%d k=%d dwellings=%d | %s" % (b, d["code"], cls, F, k, n_dw, basis))
    print("BUILDING %s aspect_source=%s fallback=%s W=%.3f D=%.3f" % (b, d["aspect_source"], d["aspect_fallback"], d["width"], d["depth"]))
    idf, meta = mz.build_mz(row, k, placement, ach, north)
    got = [ln.split()[1] for ln in meta["patch_lines"]]
    miss = [p for p in PATCH_NAMES if p not in got]
    print("PATCHCHECK %s %s missing=%s" % (b, "PASS" if not miss else "FAIL", miss))
    ok_all &= not miss
    rd = R + "runs/%s__mz/" % b
    os.makedirs(rd, exist_ok=True)
    io.open(rd + "model.idf", "w", encoding="utf-8", newline="\n").write(idf)
    saved = io.open(rd + "model.idf", encoding="utf-8").read()
    for st, g, det in mz.check_area_gates(saved, row):
        print("%s %s %s %s" % (st, g, b, det))
        ok_all &= (st == "PASS")
    meta["basis_k"] = basis
    json.dump(meta, io.open(rd + "meta.json", "w", encoding="utf-8"), indent=1, default=str)
    manifest.append((b + "__mz", "mz", b, rd + "model.idf"))
    cidf, cmeta = mz.build_mz(row, 1, {0: HH[0]}, ach, north, collapse=True)
    cd = R + "runs/%s__collapse/" % b
    os.makedirs(cd, exist_ok=True)
    io.open(cd + "model.idf", "w", encoding="utf-8", newline="\n").write(cidf)
    json.dump(cmeta, io.open(cd + "meta.json", "w", encoding="utf-8"), indent=1, default=str)
    manifest.append((b + "__collapse", "collapse", b, cd + "model.idf"))
    for st, g, det in mz.check_area_gates(io.open(cd + "model.idf", encoding="utf-8").read(), row):
        print("%s %s %s_collapse %s" % (st, g, b, det))
    sidf, smeta = j5.build(row, HH[0], infiltration_ach=ach, north_axis_deg=north)
    sd = R + "runs/%s__single/" % b
    os.makedirs(sd, exist_ok=True)
    io.open(sd + "model.idf", "w", encoding="utf-8", newline="\n").write(sidf)
    manifest.append((b + "__single", "single", b, sd + "model.idf"))
    meta_out[b] = {"k": k, "zones": len(meta["zones"]), "floors": F, "class": cls}

# ---- seen failing (scratch copies only) ---------------------------------------------------
b = "es_B21"
row = rowby[bt[b]["archetype_code"]]
saved = io.open(R + "runs/%s__mz/model.idf" % b, encoding="utf-8").read()


def drop_block(text, surf_name):
    pat = r"BuildingSurface:Detailed,\n  %s,\s.*?;\n" % re.escape(surf_name)
    n = len(re.findall(pat, text, re.S))
    assert n == 1, "drop_block %s matched %d" % (surf_name, n)
    return re.sub(pat, "", text, count=1, flags=re.S)


t1 = drop_block(saved, "S_FLOOR_Z_F00_D00")
io.open(R + "seenfail/B21_drop_floor.idf", "w", encoding="utf-8").write(t1)
res1 = mz.check_area_gates(t1, row)
for st, g, det in res1:
    print("SEENFAIL1_drop_floor %s %s %s" % (st, g, det))
print("SEENFAIL1 zone_floor_area_sum_eq_A_C_Ref must FAIL: %s" %
      ("CONFIRMED" if [s for s, g, _ in res1 if g == "zone_floor_area_sum_eq_A_C_Ref"] == ["FAIL"] else "NOT FAILING"))
t2 = drop_block(saved, "PW_Z_F00_D01_W")
io.open(R + "seenfail/B21_drop_partner.idf", "w", encoding="utf-8").write(t2)
res2 = mz.check_area_gates(t2, row)
for st, g, det in res2:
    print("SEENFAIL2_drop_partner %s %s %s" % (st, g, det))
print("SEENFAIL2 interzone_surfaces_paired must FAIL: %s" %
      ("CONFIRMED" if [s for s, g, _ in res2 if g == "interzone_surfaces_paired"] == ["FAIL"] else "NOT FAILING"))
print("SEENFAIL control (unmodified B21 idf): %s" % [s for s, g, _ in mz.check_area_gates(saved, row)])
row2 = dict(row)
for key in ("U_Wall_1", "U_Wall_2", "U_Wall_3"):
    if row2.get(key, "") not in ("", None):
        row2[key] = repr(float(row2[key]) * 1.10)
d1, d2 = s8.derive(row), s8.derive(row2)
print("SEENFAIL3 u_wall %.4f -> %.4f (x%.4f)" % (d1["u_wall"], d2["u_wall"], d2["u_wall"] / d1["u_wall"]))
idf3, meta3 = mz.build_mz(row2, 1, {0: HH[0]}, float(bt[b]["infiltration_ach"]), float(bt[b]["north_axis_deg"]), collapse=True)
sd3 = R + "runs/%s__collapse_uwall110/" % b
os.makedirs(sd3, exist_ok=True)
io.open(sd3 + "model.idf", "w", encoding="utf-8", newline="\n").write(idf3)
manifest.append((b + "__collapse_uwall110", "collapse_uwall110", b, sd3 + "model.idf"))

with io.open(R + "run_manifest.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["run_id", "kind", "building", "idf"])
    for m in manifest:
        w.writerow(m)
print("MANIFEST %d runs" % len(manifest))
json.dump(meta_out, io.open(R + "building_layout.json", "w", encoding="utf-8"), indent=1)
print("ZONES_PER_BUILDING", json.dumps(meta_out))
print("ALL_AREA_AND_PATCH_GATES", "PASS" if ok_all else "FAIL")
