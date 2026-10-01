# -*- coding: utf-8 -*-
"""5J Step 4 helper: count pairs of one split from the run tables only (no extracted file is opened). Speed job only.
usage: frz_paircount.py <split_name>   (development/validation only)"""
import sys, csv, io, collections, itertools
sys.path.insert(0, "/speed-scratch/o_iseri/5J/campaign")
import split_loader as sl
split = sys.argv[1]
assert split in ("development", "validation", "b0_dev", "b0_val", "replicates")
ids = set(sl.load_split(split))
rows = []
for cc in ("es", "it"):
    for r in csv.DictReader(io.open("/speed-scratch/o_iseri/5J/campaign/in/campaign_runs_%s.csv" % cc, encoding="utf-8")):
        if r["run_id"] in ids:
            rows.append(r)
print("split", split, "runs", len(rows))
grp = collections.defaultdict(list)
for r in rows:
    grp[(r["climate_id"], r["building_id"])].append(r)
cnt = collections.Counter(); flatpairs = collections.Counter(); runs_c = collections.Counter(); flats_c = collections.Counter()
sizes = collections.Counter()
for (cl, b), rs in grp.items():
    cls = rs[0]["class"]; cc = rs[0]["country"]
    sizes[len(rs)] += 1
    nd = int(rs[0]["n_dwellings"])
    runs_c[(cc, cls)] += len(rs)
    flats_c[(cc, cls)] += nd * len(rs)
    for j in range(nd):
        toks = [dict(x.split(":", 1) for x in r["placement"].split(";"))[str(j)] for r in rs]
        for a, c in itertools.combinations(range(len(rs)), 2):
            if toks[a] != toks[c]:
                flatpairs[(cc, cls)] += 1
        cnt[(cc, cls)] += 0
print("groups", len(grp), "runs-per-group histogram", sorted(sizes.items()))
for k in sorted(set(runs_c)):
    print("CELL", k, "runs", runs_c[k], "dwelling_series", flats_c[k], "pairs", flatpairs[k])
print("TOTAL pairs", sum(flatpairs.values()), "dwelling_series", sum(flats_c.values()))
