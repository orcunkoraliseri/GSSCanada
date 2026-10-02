import json, collections, csv, io, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure5 as m
R = json.load(open("win5_check_results.json"))
NEW = m.NEW
ch = {}
for ln in open(NEW + "/changed_stems.txt"):
    s, r = ln.rstrip("\r\n").split("\t"); ch[s] = r
by = {r["stem"]: r for r in R}
# degenerate csv comparison, per stem (all 1172 rows)
dg = {r["stem"]: r for r in csv.DictReader(io.open(NEW + "/degenerate_2026-10-05.csv", encoding="utf-8"))}
bad = []
tot_claim = 0; tot_area = 0.0
for s, r in dg.items():
    n = int(r["n_deleted"]); a = float(r["total_area_m2"])
    tot_claim += n; tot_area += a
    mine = by[s]["surf_deleted"] + by[s]["win_deleted"]
    marea = by[s]["surf_deleted_area"] + by[s]["win_deleted_area"]
    if ch.get(s) == "degenerate" or n:
        if mine != n or abs(marea - a) > 1e-6:
            bad.append((s, n, mine, a, marea))
print("degenerate csv: rows", len(dg), "claim n_deleted total", tot_claim, "area total", round(tot_area, 4))
print("stems with n_deleted>0 in their csv:", sum(1 for r in dg.values() if int(r["n_deleted"]) > 0), "== changed degenerate group:", set(s for s, r in dg.items() if int(r["n_deleted"]) > 0) == set(s for s, g in ch.items() if g == "degenerate"))
print("per-stem mismatches (their n_deleted/area vs my surfaces+windows deleted):", len(bad), bad[:5])
print("mine total deleted surfaces", sum(by[s]["surf_deleted"] for s in dg), "windows", sum(by[s]["win_deleted"] for s in dg), "area (surf+win)", round(sum(by[s]["surf_deleted_area"] + by[s]["win_deleted_area"] for s in dg if ch.get(s) == "degenerate"), 4))
print("max single area (surf)", max(by[s]["surf_deleted_maxarea"] for s in dg if ch.get(s) == "degenerate"), "window", max((by[s]["win_deleted_area"] for s in dg if ch.get(s) == "degenerate")))
# flat_count group
F = [by[s] for s in ch if ch[s] == "flat_count"]
cnt = collections.Counter((r["flats_new"] - r["flats_old"]) for r in F)
print("flat_count group: flats_old != flats_new:", sum(1 for r in F if r["flats_old"] != r["flats_new"]), "delta distribution (new-old):", sorted(cnt.items()))
print("floors old->new same:", sum(1 for r in F if r["floors_old"] == r["floors_new"]), "of", len(F), "; floors sum old/new", sum(r["floors_old"] for r in F), sum(r["floors_new"] for r in F))
print("zones minus flats (non-conditioned zones) old/new:", sum(r["zones_old"] - r["flats_old"] for r in F), sum(r["zones_new"] - r["flats_new"] for r in F))
# dwelling_counts csv vs our flats
prep = {r["building_id"]: r["stem"] for r in csv.DictReader(io.open(NEW + "/prepared_buildings.csv", encoding="utf-8"))}
dc = list(csv.DictReader(io.open(NEW + "/dwelling_counts_2026-10-05.csv", encoding="utf-8")))
print("dwelling_counts rows", len(dc), "mapped", sum(1 for r in dc if r["building_id"] in prep))
neq_old = neq_new = 0; changed_in_file = 0; src = collections.Counter()
for r in dc:
    s = prep.get(r["building_id"])
    if s is None: continue
    if int(r["old_count"]) != int(r["new_count"]): changed_in_file += 1
    src[r["dwellings_source"]] += 1
    if by[s]["flats_new"] != int(r["new_count"]): neq_new += 1
    if by[s]["flats_old"] != int(r["old_count"]): neq_old += 1
print("file: old_count != new_count in", changed_in_file, "rows; my flats_new != their new_count in", neq_new, "stems; my flats_old != their old_count in", neq_old, "; sources", dict(src))
print("sum new_count", sum(int(r["new_count"]) for r in dc), "sum old_count", sum(int(r["old_count"]) for r in dc), "sum my flats_new", sum(r["flats_new"] for r in R), "sum my flats_old", sum(r["flats_old"] for r in R))
cs = set(prep[r["building_id"]] for r in dc if int(r["old_count"]) != int(r["new_count"]))
print("stems whose count changed in their file:", len(cs), "== my flats changed set:", cs == set(r["stem"] for r in R if r["flats_old"] != r["flats_new"]), "; subset of flat_count group:", cs <= set(s for s, g in ch.items() if g == "flat_count"))
# per-stem csv
cols = ["stem", "group", "bytes_equal", "any_diff", "zones_old", "zones_new", "flats_old", "flats_new", "floors_old", "floors_new", "surf_old", "surf_new", "area_old", "area_new", "win_old", "win_new", "warea_old", "warea_new", "surf_deleted", "surf_added", "surf_modified", "win_deleted", "win_added", "win_modified", "surf_deleted_area", "win_deleted_area", "cons_same", "md5_old", "md5_new"]
with io.open("win5_check_per_stem.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(cols)
    for r in sorted(R, key=lambda r: r["stem"]):
        r = dict(r); r["group"] = ch.get(r["stem"], "unchanged")
        w.writerow([("%.6f" % r[c]) if isinstance(r[c], float) else r[c] for c in cols])
print("wrote win5_check_per_stem.csv")
# examples of flat_count: one with MATERIAL:NOMASS change
print("flat_count sample (stem old->new flats, surf):", [(r["stem"], r["flats_old"], r["flats_new"], r["surf_old"], r["surf_new"]) for r in F[:5]])
# unexplained: the 1001 unchanged
U = [r for r in R if r["stem"] not in ch]
print("unchanged group", len(U), "byte equal", sum(r["bytes_equal"] for r in U), "any_diff", sum(r["any_diff"] for r in U))
# check on the new-flat mean sizes
