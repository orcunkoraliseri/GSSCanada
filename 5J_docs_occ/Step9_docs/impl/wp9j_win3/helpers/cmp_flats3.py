# 9j item 3: static_win2 vs static_win3 flats + the "changed flat sits in a building with a flipped wall" rule. Run from Step9_docs/impl with py.
import csv, hashlib
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
pb = {}
for r in csv.DictReader(open("wp9j_win3/win3_check_per_building.csv", encoding="utf-8")):
    pb[r["stem"]] = int(r["changed_walls_vs_old"])
for d in ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2"):
    a = list(csv.DictReader(open("static_win2/flats_%s.csv" % d, encoding="utf-8")))
    b = list(csv.DictReader(open("static_win3/flats_%s.csv" % d, encoding="utf-8")))
    cols = list(a[0].keys())
    orient = [c for c in cols if (c.startswith("wall_") and c[5] in "NESW") or (c.startswith("win_") and c[4] in "NESW")]
    other = [c for c in cols if c not in orient]
    print(d, "rows win2", len(a), "win3", len(b), "same order of (stem,zone):", [(x["stem"], x["zone"]) for x in a] == [(x["stem"], x["zone"]) for x in b])
    print(" flats with any non-orientation column different:", sum(1 for x, y in zip(a, b) if any(x[c] != y[c] for c in other)))
    def changed(x, y): return any(x[c] != y[c] for c in orient)
    ch = [(x, y) for x, y in zip(a, b) if changed(x, y)]
    bad = [x["zone"] for x, y in ch if pb.get(x["stem"], 0) == 0]
    mirror = sum(1 for x, y in ch if all(abs(float(x["wall_%s_m2" % k]) - float(y["wall_%s_m2" % OPP[k]])) < 1e-3 for k in "NESW"))
    print(" flats with orientation columns changed:", len(ch), "of", len(a), "; in buildings with NO flipped wall (must be 0):", len(bad), bad[:3], "; exact N<->S,E<->W mirror among them:", mirror)
    nb = len({x["stem"] for x, y in ch})
    nflip = sum(1 for s, v in pb.items() if v > 0 and any(x["stem"] == s for x in a[:0]))
    print(" buildings with a changed flat:", nb)
    tot_ok = all(abs(sum(float(x["wall_%s_m2" % k]) for k in "NESW") - sum(float(y["wall_%s_m2" % k]) for k in "NESW")) < 1e-3 and abs(sum(float(x["win_%s_m2" % k]) for k in "NESW") - sum(float(y["win_%s_m2" % k]) for k in "NESW")) < 1e-3 for x, y in zip(a, b))
    print(" wall total and window total per flat equal win2/win3:", tot_ok)
    # seen failing: plant one changed orientation value in a flat of a building with no flipped wall
    cand = [i for i, x in enumerate(b) if pb.get(x["stem"], 0) == 0]
    bb = [dict(r) for r in b]; i = cand[0]; bb[i]["wall_N_m2"] = "%.4f" % (float(bb[i]["wall_N_m2"]) + 1.0)
    plant_bad = [x["zone"] for x, y in zip(a, bb) if changed(x, y) and pb.get(x["stem"], 0) == 0]
    print(" PLANT one flat edited in a building without flipped wall: rule reports", len(plant_bad), "(must be", len(bad) + 1, ")")
    # buildings tables
    b1 = open("static_win2/buildings_%s.csv" % d, "rb").read(); b2 = open("static_win3/buildings_%s.csv" % d, "rb").read()
    print(" buildings table byte-equal win2/win3:", b1 == b2, hashlib.md5(b2).hexdigest())
    print(" flats md5 win2", hashlib.md5(open("static_win2/flats_%s.csv" % d, "rb").read()).hexdigest(), "win3", hashlib.md5(open("static_win3/flats_%s.csv" % d, "rb").read()).hexdigest())
    print(" buildings with a flipped wall (changed_walls_vs_old > 0) in this district:", sum(1 for r in csv.DictReader(open("wp9j_win3/win3_check_per_building.csv", encoding="utf-8")) if r["district"] == d and int(r["changed_walls_vs_old"]) > 0))
