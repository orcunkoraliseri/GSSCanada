"""Step 9k: azcheck.csv for the final base _win_2026-10-03 (same rule as 9i: first outdoor 4-vertex wall where point test and edge test both say outward = main;
first wall where both say inward = control_inward, if any). Uses the own classifier of tools/5thJ_modelA_win2_check.py on the delivered base IDF."""
import os, sys, math, csv, importlib
os.environ["MODELA_VINTAGE"] = "win_2026-10-03"
T = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools"; sys.path.insert(0, T); sys.dont_write_bytecode = True
M = importlib.import_module("5thJ_modelA_idf"); C = importlib.import_module("5thJ_modelA_win2_check")
EU = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/%s_win_2026-10-03/idfs/%s.idf"
ES, IT = "ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"
B = [(ES, "919761afea1827b3"), (ES, "1271cddbf6bd1e8a"), (ES, "0275c53572b2ff9f"), (IT, "504fa19567bbc2b7"), (IT, "1ef46361a8060ff9"), (IT, "13c60875a803e164")]
def az(v):
    sx = sy = 0.0
    for i in range(len(v)):
        x1, y1, z1 = v[i]; x2, y2, z2 = v[(i + 1) % len(v)]
        sx += y1 * z2 - z1 * y2; sy += z1 * x2 - x1 * z2
    return math.degrees(math.atan2(sx, sy)) % 360.0
rows = [["district", "stem", "role", "wall_name", "point_class", "edge_class", "newell_az", "geom_outward_az"]]
for d, s in B:
    text = M.read_text(EU % (d, s)); objs = M.objects(text)
    surf, floors, fedges, fup = {}, {}, {}, {}
    for o in objs:
        if o["kw"] == "BUILDINGSURFACE:DETAILED":
            x = M.surface_of(o); surf[x["name"]] = x
            if x["type"] == "floor":
                floors.setdefault(x["zone"], []).append(x["verts"]); vv = x["verts"]
                fup[x["zone"]] = fup.get(x["zone"], 0) or (C.newell(vv)[2] > 0)
                for i in range(len(vv)): fedges.setdefault(x["zone"], set()).add((C._k(vv[i]), C._k(vv[(i + 1) % len(vv)])))
    main = ctl = None
    nin = 0
    for x in surf.values():
        if x["type"] != "wall" or x["bc"] != "outdoors" or len(x["verts"]) != 4: continue
        n = C.newell(x["verts"]); nn = math.hypot(n[0], n[1]); polys = floors.get(x["zone"], [])
        ecls = C.edge_class(x, fedges, fup); pcls = "unc"
        if nn > 0 and polys:
            wx = sum(v[0] for v in x["verts"]) / 4; wy = sum(v[1] for v in x["verts"]) / 4
            p_in = any(C.inside((wx + .05 * n[0] / nn, wy + .05 * n[1] / nn), pl) for pl in polys)
            m_in = any(C.inside((wx - .05 * n[0] / nn, wy - .05 * n[1] / nn), pl) for pl in polys)
            pcls = "in" if (p_in and not m_in) else "out" if (m_in and not p_in) else "unc"
        a = az(x["verts"])
        if pcls == "out" and ecls == "out" and main is None: main = [d, s, "main", x["name"], pcls, ecls, "%.4f" % a, "%.4f" % a]
        if pcls == "in" and ecls == "in":
            nin += 1
            if ctl is None: ctl = [d, s, "control_inward", x["name"], pcls, ecls, "%.4f" % a, "%.4f" % ((a + 180) % 360)]
    print(s, "main:", main[3] if main else None, "| walls both tests call inward:", nin)
    rows.append(main)
    if ctl: rows.append(ctl)
with open("azcheck.csv", "w", newline="") as f: csv.writer(f, lineterminator="\n").writerows(rows)
print("rows written:", len(rows) - 1)
