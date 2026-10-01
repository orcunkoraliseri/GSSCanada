# 5J campaign prep, Part D step 1 (Speed): build the two big IDFs for the TIMING + DISK check (not design runs).
# es_B40 (Spain, most dwellings) and it_B37 (Italy, most dwellings; tie with it_B38, lowest id taken), each filled with Spanish
# pilot households round-robin (TIMING ONLY).
import csv, hashlib, io, json, os, re, sys, platform
R = "/speed-scratch/o_iseri/5J/campaign_prep/"
T = R + "timing/"
REPO = R + "repo/"
PILOT = "/speed-scratch/o_iseri/5J/pilot/"
sys.path.insert(0, REPO + "5J_docs_occ/tools")
import importlib
print("python", sys.version.split()[0], "host", platform.node())
mz = importlib.import_module("5thJ_idf_mz")
mz._j5.TOOLS_4J = REPO + "4J_docs_occ/tools"
s8 = mz._s8


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


info = json.load(io.open(R + "out/info_es_it.json"))
bt = {r["building_id"]: r for r in csv.DictReader(io.open(R + "in/buildings_es_it.csv", encoding="utf-8"))}
folders = sorted(os.listdir(PILOT + "inputs"))
byhid = {}
for f in folders:
    b, h = f.split("__es_")
    byhid.setdefault(h, f)
pil = sorted(byhid)
print("PILOT_HOUSEHOLDS found %d: %s" % (len(pil), " ".join(pil)))
HH = {}
for h in pil:
    fdir = PILOT + "inputs/" + byhid[h] + "/"
    txt = io.open(fdir + "in.idf", encoding="utf-8").read()
    m1 = re.search(r"HH_es_%s_People,[^;]*?\n\s+(\d+),\s+!- Number of People" % h, txt, re.S)
    m2 = re.search(r"HH_es_%s_Appliances,[^;]*?\n\s+([0-9.]+),\s+!- Design Level \{W\}" % h, txt, re.S)
    HH[h] = {"hid": h, "fold": "es", "n_members": int(m1.group(1)), "presence_csv": fdir + "presence_HH_es_%s.csv" % h,
             "appliance_csv": fdir + "elec_HH_es_%s.csv" % h, "appliance_peak_w": float(m2.group(1)), "peak_w_source": fdir + "in.idf"}
    assert os.path.exists(HH[h]["presence_csv"]) and os.path.exists(HH[h]["appliance_csv"])
TARGETS = [("T_es_B40", "es_B40", "es", PILOT + "epw/es_madrid_2009_2010_y2010.epw"),
           ("T_it_B37", "it_B37", "it", R + "epw/it_bologna_2013_2014_y2014.epw")]
os.makedirs(T + "runs", exist_ok=True)
man = []
epws = []
ok_all = True
for rid, bid, cc, epw in TARGETS:
    i = info[bid]
    rows, _ = s8.load_rows(R + "tabula_in/", cc)
    row = {r["Code_Building"]: r for r in rows}[bt[bid]["archetype_code"]]
    placement = {j: HH[pil[j % len(pil)]] for j in range(i["n_dw"])}
    plc = ";".join("%d:%s" % (j, pil[j % len(pil)]) for j in range(i["n_dw"]))
    idf, meta = mz.build_mz(row, i["k"], placement, float(bt[bid]["infiltration_ach"]), float(bt[bid]["north_axis_deg"]))
    rd = T + "runs/%s/" % rid
    os.makedirs(rd, exist_ok=True)
    io.open(rd + "model.idf", "w", encoding="utf-8", newline="\n").write(idf)
    saved = io.open(rd + "model.idf", encoding="utf-8").read()
    res = mz.check_area_gates(saved, row)
    npass = sum(1 for s, g, _ in res if s == "PASS")
    print("AREAGATES %s %s %d/%d PASS %s" % (rid, bid, npass, len(res), "; ".join("%s %s" % (s, g) for s, g, _ in res if s != "PASS")))
    ok_all &= (npass == len(res))
    print("BUILT %s building=%s class=%s floors=%d k=%d dwellings=%d zones=%d epw=%s (households: Spanish pilot, round robin, TIMING ONLY)"
          % (rid, bid, i["cls"], i["F"], i["k"], i["n_dw"], len(meta["zones"]), os.path.basename(epw)))
    meta["design_row"] = {"run_id": rid}
    json.dump(meta, io.open(rd + "meta.json", "w", encoding="utf-8"), indent=1, default=str)
    man.append([rid, bid, i["cls"], i["k"], i["F"], i["n_dw"], 0, "NA", plc, rd + "model.idf", md5(rd + "model.idf"), md5(epw), "midnight", len(meta["zones"])])
    epws.append((rid, epw))
with io.open(T + "run_manifest.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["run_id", "building_id", "class", "k", "n_floors", "n_dwellings", "replicate", "seed", "placement", "idf",
                "idf_md5", "epw_md5", "clock_origin", "n_zones"])
    for m in man:
        w.writerow(m)
with io.open(T + "epw_map.txt", "w") as fh:
    for rid, e in epws:
        fh.write("%s %s\n" % (rid, e))
print("TIMING_BUILD", "PASS" if ok_all else "FAIL", "zones:", [(m[0], m[13]) for m in man])
sys.exit(0 if ok_all else 1)
