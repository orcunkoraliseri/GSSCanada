# -*- coding: utf-8 -*-
"""Step 9p item 6: checks on plan_IT-BOL-GALVANI2_win5.csv (provisional lists). Desktop only, no Speed.
(1) counts per building split / pool / mode, households needed; (2) every row's src_idf_md5 equals the md5 file of the delivery (independent source: OpenUBEM `md5_2026-10-05.txt`),
and a PLANTED changed md5 on one row must show up; (3) the OLD Bologna expectation (8,820 rows on the 10-03 lists, 10-03 hold-out) rebuilt by the same plan code and compared with the new rows:
run ids in both / added / dropped / n_flats changed; (4) run_id unique, seed = run_seed_of(run_id), n_flats == zone map rows (independent source: zone_map_bol5.csv)."""
import csv, io, os, sys, collections, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.dirname(HERE); IMP = os.path.dirname(OUTD)
sys.path.insert(0, os.path.normpath(os.path.join(IMP, "..", "..", "tools", "speed")))
sys.dont_write_bytecode = True
import a9_campaign_plan as P
D = "IT-BOL-GALVANI2"
NEWD = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/IT-BOL-GALVANI2_win_2026-10-05"
plan = P.read_csv(OUTD + "/plan_IT-BOL-GALVANI2_win5.csv")
print("plan rows", len(plan), "md5", P.md5_file(OUTD + "/plan_IT-BOL-GALVANI2_win5.csv"))
bs = collections.Counter(r["building_split"] for r in plan)
print("rows per building split:", dict(bs), "| stems per split:", {s: len(set(r["stem"] for r in plan if r["building_split"] == s)) for s in ("dev", "val", "test")})
print("rows per pool:", dict(sorted(collections.Counter((r["pool"]) for r in plan).items())), "| rows per mode:", dict(collections.Counter(r["mode"] for r in plan)))
print("rows per (building split, pool):", dict(sorted(collections.Counter((r["building_split"], r["pool"]) for r in plan).items())))
hh = [r for r in plan if r["pool"] in ("dev", "val", "test")]
print("household-draw rows (dev/val/test pools):", len(hh), "| b0 rows:", sum(1 for r in plan if r["pool"] == "b0"), "| default rows:", sum(1 for r in plan if r["pool"] == "def"))
print("household draws (flat-years) per pool:", {p: sum(int(r["n_flats"]) for r in hh if r["pool"] == p) for p in ("dev", "val", "test")}, "| b0 flat-years", sum(int(r["n_flats"]) for r in plan if r["pool"] == "b0"), "| default flat-years", sum(int(r["n_flats"]) for r in plan if r["pool"] == "def"), "| all", sum(int(r["n_flats"]) for r in plan))
nf = sorted(int(r["n_flats"]) for r in plan if r["pool"] == "def")
print("households (= flats) per building: median %d, mean %.1f, max %d; buildings with 1 flat: %d" % (nf[len(nf) // 2], sum(nf) / len(nf), nf[-1], sum(1 for x in nf if x == 1)))
# (2) md5 against the md5 file, planted
m5 = {}
for ln in io.open(NEWD + "/md5_2026-10-05.txt", encoding="utf-8"):
    p = ln.split()
    if p: m5[p[-1][:-4]] = p[0]
def count_bad(rows):
    return sum(1 for r in rows if m5.get(r["stem"]) != r["src_idf_md5"])
print("rows whose src_idf_md5 differs from md5_2026-10-05.txt:", count_bad(plan))
pl = [dict(r) for r in plan]; pl[1234]["src_idf_md5"] = "0" * 32
print("PLANTED (md5 of row 1,235 set to zeros): rows differing:", count_bad(pl), "-> named", [r["run_id"] for r in pl if m5.get(r["stem"]) != r["src_idf_md5"]])
# (4) other columns
print("run_id unique:", len(set(r["run_id"] for r in plan)) == len(plan), "| seed == run_seed_of(run_id) for all rows:", all(int(r["seed"]) == P.run_seed_of(r["run_id"]) for r in plan))
zm = collections.Counter()
for r in P.read_csv(IMP + "/2026-10-01_wp9c_zone_map_bol5.csv"):
    if r["district"] == D: zm[r["stem"]] += 1
print("n_flats == zone map rows for every plan row:", all(zm.get(r["stem"]) == int(r["n_flats"]) for r in plan))
bad = [dict(r) for r in plan]; bad[500]["n_flats"] = str(int(bad[500]["n_flats"]) + 1)
print("PLANTED (n_flats +1 on one row): rows differing from the zone map:", sum(1 for r in bad if zm.get(r["stem"]) != int(r["n_flats"])))
print("src_idf path prefix:", set(r["src_idf"].rsplit("/idfs/", 1)[0] for r in plan))
# (3) OLD expectation: sealed-style lists on 10-03 (buildsplit_win3 IT, hold-out win3 IT, n_flats from win3 wall table)
lists = {sp: P.read_csv("%s/buildsplit_win3/%s_%s.csv" % (IMP, D, sp)) for sp in ("dev", "val", "test")}
held = set(r["stem"] for r in P.read_csv(IMP + "/heldout_tinyflats_win3.csv") if r["district"] == D)
old_rows, kept = P.build_rows(D, lists, held)
print("OLD expectation on the 10-03 lists: rows", len(old_rows), "(rules R2 say 8,820)", "| buildings dev/val/test", {sp: len(kept[sp]) for sp in kept})
o = {r["run_id"]: r for r in old_rows}; n = {r["run_id"]: r for r in plan}
print("run ids in both", len(set(o) & set(n)), "| only in the old (dropped)", len(set(o) - set(n)), "| only in the new (added)", len(set(n) - set(o)))
both = set(o) & set(n)
print("  of the common: n_flats changed", sum(1 for k in both if o[k]["n_flats"] != n[k]["n_flats"]), "| n_flats equal", sum(1 for k in both if o[k]["n_flats"] == n[k]["n_flats"]), "| seed equal", sum(1 for k in both if str(o[k]["seed"]) == str(n[k]["seed"])), "| building split equal", sum(1 for k in both if o[k]["building_split"] == n[k]["building_split"]))
os_, ns_ = set(r["stem"] for r in old_rows), set(r["stem"] for r in plan)
print("  stems: old plan", len(os_), "new plan", len(ns_), "| in both", len(os_ & ns_), "| only old", len(os_ - ns_), "| only new", len(ns_ - os_))
print("  old split of stems present in both whose split differs in the new plan:", sum(1 for s in os_ & ns_ if {r["building_split"] for r in old_rows if r["stem"] == s} != {r["building_split"] for r in plan if r["stem"] == s}))
print("  rows per mode OLD:", dict(collections.Counter(r["mode"] for r in old_rows)), "| NEW:", dict(collections.Counter(r["mode"] for r in plan)))
print("  total flat-years OLD", sum(int(r["n_flats"]) for r in old_rows), "NEW", sum(int(r["n_flats"]) for r in plan))
