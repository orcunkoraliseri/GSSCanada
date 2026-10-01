# -*- coding: utf-8 -*-
"""Part 2, Part D: write the split run_id lists (Spain + Italy) from the frozen run tables and the two splits CSVs. Speed job only.
Writes /speed-scratch/o_iseri/5J/splits/<name>.txt (sorted, one run_id per line) and splits.md5; prints counts, the overlap table, gates.
"""
import csv, hashlib, io, os, sys
R = "/speed-scratch/o_iseri/5J/campaign/"
OUT = "/speed-scratch/o_iseri/5J/splits/"
NAMES = ["development", "validation", "test_new_households", "test_new_buildings", "test_both_new", "unused",
         "b0_dev", "b0_val", "b0_test", "replicates", "loco_es", "loco_it"]
PARTITION = NAMES[:10]
HH_ALLOWED = {"dev": {"development", "validation", "test_new_buildings"}, "val": {"validation", "unused"},
              "test": {"test_new_households", "test_both_new", "unused"}}
BL_ALLOWED = {"dev": {"development", "validation", "test_new_households"}, "val": {"validation", "unused"},
              "test": {"test_new_buildings", "test_both_new", "unused"}}
MAIN5 = ["development", "validation", "test_new_households", "test_new_buildings", "test_both_new"]


def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def classify(pool, bs):
    if (pool, bs) == ("dev", "dev"):
        return "development"
    if (pool, bs) in (("val", "dev"), ("val", "val"), ("dev", "val")):
        return "validation"
    if (pool, bs) == ("test", "dev"):
        return "test_new_households"
    if (pool, bs) == ("dev", "test"):
        return "test_new_buildings"
    if (pool, bs) == ("test", "test"):
        return "test_both_new"
    if (pool, bs) in (("val", "test"), ("test", "val")):
        return "unused"
    raise ValueError("unexpected pool/building_split %s/%s" % (pool, bs))


def main():
    md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
    print("INPUT_MD5 splits_households.csv", md5(R + "integrity/in/splits_households.csv"), "(design doc: 797a90683e26c42ee90d6bcc02112132)")
    print("INPUT_MD5 splits_buildings.csv", md5(R + "integrity/in/splits_buildings.csv"), "(design doc: 7e3bf4edcd187f2b03ebb0f21e5c88d7)")
    hh_split = {r["household_id"]: r["split"] for r in rd(R + "integrity/in/splits_households.csv")}
    bl_split = {r["building_id"]: r["split"] for r in rd(R + "integrity/in/splits_buildings.csv")}
    runs = []
    for cc in ("es", "it"):
        for r in rd(R + "in/campaign_runs_%s.csv" % cc):
            assert r["country"] == cc and r["run_id"].startswith(cc + "_")
            runs.append(r)
    print("RUNS", len(runs))
    lists = {n: [] for n in NAMES}
    member = {}
    mism = []
    hh_in = {}
    bl_in = {}
    for r in runs:
        rid, cc = r["run_id"], r["country"]
        toks = [t.split(":", 1)[1] for t in r["placement"].split(";")]
        bs = bl_split[r["building_id"]]
        if bs != r["building_split"]:
            mism.append("%s building_split %s != splits_buildings %s" % (rid, r["building_split"], bs))
        if int(r["replicate"]) > 0:
            name = "replicates"
        elif r["pool"] == "b0":
            assert all(t == cc + "_avg" for t in toks), ("B0 run with a non-average household", rid)
            name = "b0_" + bs
        else:
            name = classify(r["pool"], bs)
            for t in toks:
                hs = hh_split[cc + "_" + t]
                if hs != r["pool"]:
                    mism.append("%s household %s split %s != pool %s" % (rid, t, hs, r["pool"]))
                hh_in.setdefault(cc + "_" + t, set()).add(name)
            bl_in.setdefault(r["building_id"], set()).add(name)
        lists[name].append(rid)
        lists["loco_" + cc].append(rid)
        member[rid] = name
    print("PLACEMENT_SPLIT_MISMATCHES", len(mism), mism[:3])
    ids = [r["run_id"] for r in runs]
    in_partition = {}
    for n in PARTITION:
        for rid in lists[n]:
            in_partition.setdefault(rid, []).append(n)
    bad_part = [i for i in ids if len(in_partition.get(i, [])) != 1]
    print("GATE every planned run in exactly one of the 10 partition lists:", "PASS" if not bad_part and len(in_partition) == len(ids) == len(set(ids)) else "FAIL %d" % len(bad_part),
          "(runs=%d, in partition=%d)" % (len(ids), len(in_partition)))
    print("GATE loco_es + loco_it = all runs:", "PASS" if len(lists["loco_es"]) + len(lists["loco_it"]) == len(ids) and not set(lists["loco_es"]) & set(lists["loco_it"]) else "FAIL")
    lists_hh = {n: set() for n in MAIN5}
    lists_bl = {n: set() for n in MAIN5}
    for r in runs:
        n = member[r["run_id"]]
        if n in MAIN5:
            for t in r["placement"].split(";"):
                lists_hh[n].add(r["country"] + "_" + t.split(":", 1)[1])
            lists_bl[n].add(r["building_id"])
    print("OVERLAP_TABLE ids shared by two of the five main lists (diagonal = ids in the list); columns in the same order as rows")
    print("  order: %s" % ", ".join(MAIN5))
    for kind, L in (("household", lists_hh), ("building", lists_bl)):
        print("-- %s ids" % kind)
        for a in MAIN5:
            print("   %-20s %s" % (a, " ".join("%4d" % len(L[a] & L[b]) for b in MAIN5)))
    viol_h = [(h, sorted(s - HH_ALLOWED[hh_split[h]])) for h, s in hh_in.items() if s - HH_ALLOWED[hh_split[h]]]
    viol_b = [(b, sorted(s - BL_ALLOWED[bl_split[b]])) for b, s in bl_in.items() if s - BL_ALLOWED[bl_split[b]]]
    print("GATE household ids in a list their split does not allow:", "PASS 0" if not viol_h else "FAIL %d %s" % (len(viol_h), viol_h[:3]))
    print("GATE building ids in a list their split does not allow:", "PASS 0" if not viol_b else "FAIL %d %s" % (len(viol_b), viol_b[:3]))
    tt = [h for h, s in hh_in.items() if hh_split[h] == "test" and (s & {"development", "validation"})]
    tb = [b for b, s in bl_in.items() if bl_split[b] == "test" and (s & {"development", "validation"})]
    print("GATE test households in development or validation:", "PASS 0" if not tt else "FAIL %d" % len(tt))
    print("GATE test buildings in development or validation:", "PASS 0" if not tb else "FAIL %d" % len(tb))
    print("GATE placements and run-table splits agree with the two splits CSVs:", "PASS" if not mism else "FAIL %d" % len(mism))
    print("HOUSEHOLD_COUNTS by split label: %s" % {s: sum(1 for v in hh_split.values() if v == s) for s in ("dev", "val", "test")})
    os.makedirs(OUT, exist_ok=True)
    for n in NAMES:
        p = OUT + n + ".txt"
        if os.path.exists(p):
            os.chmod(p, 0o660)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("".join(i + "\n" for i in sorted(lists[n])))
    back = {n: [ln.strip() for ln in io.open(OUT + n + ".txt", encoding="utf-8")] for n in NAMES}
    ok = all(back[n] == sorted(lists[n]) and len(back[n]) == len(set(back[n])) for n in NAMES)
    allb = [i for n in PARTITION for i in back[n]]
    print("GATE files read back: sorted, no duplicates, partition covers every run once:", "PASS" if ok and sorted(allb) == sorted(ids) else "FAIL")
    print("COUNTS per list (total, es, it)")
    for n in NAMES:
        print("  %-22s total=%5d es=%5d it=%5d" % (n, len(back[n]), sum(1 for i in back[n] if i.startswith("es_")), sum(1 for i in back[n] if i.startswith("it_"))))
    if os.path.exists(OUT + "splits.md5"):
        os.chmod(OUT + "splits.md5", 0o660)
    with io.open(OUT + "splits.md5", "w", encoding="utf-8", newline="\n") as fh:
        for n in NAMES:
            fh.write("%s  %s.txt\n" % (md5(OUT + n + ".txt"), n))
    for n in NAMES:
        os.chmod(OUT + n + ".txt", 0o440)
    os.chmod(OUT + "splits.md5", 0o440)
    print("SPLITS_WRITTEN_READONLY", OUT)


main()
