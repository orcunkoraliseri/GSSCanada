# -*- coding: utf-8 -*-
"""5J Step 9e: Model A building split (Madrid, Bologna). Task: Step9_docs/impl/2026-10-01_wp9e_building_split_TASK.md.
Reads only the windowed wall table (full file name). UK licence: nothing UK is named or opened; rows of other districts are refused.
Reuses tools/5thJ_design_tables.py rng_for (same pattern as split_hids in 5thJ_modelA_households.py).
"""
import collections
import csv
import hashlib
import importlib.util
import io
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
STEP9 = os.path.join(os.path.dirname(HERE), "Step9_docs")
# Base switch (additive; old behaviour is the default): MODELA_VINTAGE=win_2026-10-02 reads the `_win2` wall table and writes impl/buildsplit_win2/
# Step 9j: win_2026-10-03 reads `_win3` and writes impl/buildsplit_win3/; any other value (or none) = the old default.
# Step 9o: win_2026-10-05 reads `_win5`, writes impl/buildsplit_win5/ and covers Madrid only (the only district delivered on that tag).
_SUF = {"win_2026-10-02": "win2", "win_2026-10-03": "win3", "win_2026-10-05": "win5"}.get(os.environ.get("MODELA_VINTAGE"), "win")
WALL = os.path.join(STEP9, "impl", "2026-10-01_wp9c_wall_table_%s.csv" % _SUF)
OUT = os.path.join(STEP9, "impl", "buildsplit" if _SUF == "win" else "buildsplit_" + _SUF)
DISTRICTS = ("ES-MAD-BERRUGUETE", "IT-BOL-GALVANI2")
EXPECT = {"ES-MAD-BERRUGUETE": 1165, "IT-BOL-GALVANI2": 1171}
_CTRY = os.environ.get("MODELA_COUNTRY", "")   # step 9p (additive): IT with win_2026-10-05 = Bologna, own names `_bol5`
if _CTRY not in ("", "IT") or (_CTRY and _SUF != "win5"):
    sys.exit("MODELA_COUNTRY must be empty or IT, and IT only with win_2026-10-05")
_BOL5 = (_CTRY == "IT")
if _BOL5:
    WALL = os.path.join(STEP9, "impl", "2026-10-01_wp9c_wall_table_bol5.csv")
    OUT = os.path.join(STEP9, "impl", "buildsplit_bol5")
if _SUF == "win5":
    DISTRICTS = ("ES-MAD-BERRUGUETE",)
    if _BOL5:
        DISTRICTS = ("IT-BOL-GALVANI2",)
        EXPECT = {"IT-BOL-GALVANI2": 1167}   # step 9p: measured independently in item 1 (1,179 stems minus 12 buildings with one `_whole` zone per floor)
    else:
        EXPECT = {"ES-MAD-BERRUGUETE": 1164}   # step 9o: measured, 1,172 stems minus 8 buildings with one `_whole` zone per floor (wp9o_win5/cmp_tables5_stdout.txt)
SEED = 9102
SPLITS = ("dev", "val", "test")
CLASSES = ("AB", "TH", "MFH", "SFH")
BANDS = ("1", "2-8", "9-24", "25+")
RUNS_PER = {"dev": 9, "val": 6, "test": 6}
HDR = ["stem", "building_id", "class", "band", "n_flats", "no_outdoor_wall"]

spec = importlib.util.spec_from_file_location("dt5j", os.path.join(HERE, "5thJ_design_tables.py"))
dt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dt)


def band_of(n):
    return "1" if n == 1 else "2-8" if n <= 8 else "9-24" if n <= 24 else "25+"


def md5b(b):
    return hashlib.md5(b).hexdigest()


def load():
    with io.open(WALL, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    other = collections.Counter(r["district"] for r in rows if r["district"] not in DISTRICTS)
    print("rows read %d; rows in other districts (skipped, not opened further): %d" % (len(rows), sum(other.values())))
    use = collections.defaultdict(list)
    unusable = collections.Counter()
    for r in rows:
        d = r["district"]
        if d not in DISTRICTS:
            continue
        if r["zone_map_reason"].strip():
            unusable[d] += 1
            continue
        n = int(r["n_flats"])
        nw = sum(int(r[k] or 0) for k in ("outdoor_eligible_rectangle", "outdoor_too_small", "outdoor_triangle", "outdoor_other_shape"))
        use[d].append({"stem": r["stem"], "building_id": r["building_id"], "class": r["building_type"],
                       "band": band_of(n), "n_flats": n, "no_outdoor_wall": int(nw == 0)})
    print("unusable per district:", dict(unusable))
    return use


def split(use, seed):
    """-> {district: {split: [rows]}}"""
    res = {}
    for d in DISTRICTS:
        res[d] = {s: [] for s in SPLITS}
        strata = collections.defaultdict(list)
        for r in use[d]:
            strata[(r["class"], r["band"])].append(r)
        for (c, b) in sorted(strata):
            rs = sorted(strata[(c, b)], key=lambda r: r["stem"])
            rng = dt.rng_for(seed, "bsplit", d, c, b)
            rng.shuffle(rs)
            n = len(rs)
            nd, nv = int(round(0.70 * n)), int(round(0.15 * n))
            res[d]["dev"] += rs[:nd]
            res[d]["val"] += rs[nd:nd + nv]
            res[d]["test"] += rs[nd + nv:]
        for s in SPLITS:
            res[d][s].sort(key=lambda r: r["stem"])
    return res


def list_bytes(rows):
    sio = io.StringIO()
    w = csv.writer(sio, lineterminator="\n")
    w.writerow(HDR)
    for r in rows:
        w.writerow([r[k] for k in ("stem", "building_id", "class", "band", "n_flats", "no_outdoor_wall")])
    return sio.getvalue().encode("utf-8")


def write_lists(res, folder):
    os.makedirs(folder, exist_ok=True)
    md5 = {}
    for d in DISTRICTS:
        for s in SPLITS:
            b = list_bytes(res[d][s])
            p = os.path.join(folder, "%s_%s.csv" % (d, s))
            with io.open(p, "wb") as fh:
                fh.write(b)
            md5[(d, s)] = md5b(b)
    return md5


def overlap(res):
    """returns {district: set of stems in more than one split}"""
    out = {}
    for d in DISTRICTS:
        seen = collections.Counter()
        for s in SPLITS:
            for r in res[d][s]:
                seen[r["stem"]] += 1
        out[d] = {k for k, v in seen.items() if v > 1}
    return out


def verdict(name, ok, msg):
    print("CHECK %s %s %s" % (name, "PASS" if ok else "FAIL", msg))
    return ok


def main():
    use = load()
    res = split(use, SEED)
    os.makedirs(OUT, exist_ok=True)
    md5 = write_lists(res, OUT)
    print("\nLIST MD5")
    for d in DISTRICTS:
        for s in SPLITS:
            print("%s_%s.csv n=%d md5=%s" % (d, s, len(res[d][s]), md5[(d, s)]))

    # strata table
    srows = []
    empty = []
    for d in DISTRICTS:
        for c in CLASSES:
            for b in BANDS:
                n = sum(1 for r in use[d] if r["class"] == c and r["band"] == b)
                if n == 0:
                    continue
                k = {s: sum(1 for r in res[d][s] if r["class"] == c and r["band"] == b) for s in SPLITS}
                srows.append([d, c, b, n, k["dev"], k["val"], k["test"]])
                if k["val"] == 0 or k["test"] == 0:
                    empty.append((d, c, b, n, k["dev"], k["val"], k["test"]))
        for c in sorted({r["class"] for r in use[d]} - set(CLASSES)):
            print("NOTE unexpected class", d, c)
    sb = io.StringIO()
    w = csv.writer(sb, lineterminator="\n")
    w.writerow(["district", "class", "band", "n", "dev", "val", "test"])
    w.writerows(srows)
    with io.open(os.path.join(OUT, "strata.csv"), "wb") as fh:
        fh.write(sb.getvalue().encode("utf-8"))
    print("\nSTRATA (district class band n dev val test)")
    for r in srows:
        print(*r)
    print("\nstrata.csv md5 =", md5b(sb.getvalue().encode("utf-8")))
    print("\nSTRATA WITH EMPTY VAL OR TEST (D9-2 not evaluable): %d" % len(empty))
    for e in empty:
        print(*e)
    print("no_outdoor_wall flagged:", {d: sum(r["no_outdoor_wall"] for r in use[d]) for d in DISTRICTS})

    # run plan
    print("\nRUN PLAN")
    tot_runs = tot_flats = 0
    for d in DISTRICTS:
        runs = flats = 0
        percls = collections.defaultdict(int)
        percls_fl = collections.defaultdict(int)
        for s in SPLITS:
            for r in res[d][s]:
                k = RUNS_PER[s]
                runs += k
                flats += k * r["n_flats"]
                percls[r["class"]] += k
                percls_fl[r["class"]] += k * r["n_flats"]
        print("%s runs=%d flats_over_runs=%d buildings=%d" % (d, runs, flats, sum(len(res[d][s]) for s in SPLITS)))
        for c in sorted(percls):
            print("  class %s runs=%d flats_over_runs=%d" % (c, percls[c], percls_fl[c]))
        tot_runs += runs
        tot_flats += flats
    print("TOTAL runs=%d flats_over_runs=%d" % (tot_runs, tot_flats))

    # checks
    print("\nCHECKS")
    ok_all = True
    cnt = {d: sum(len(res[d][s]) for s in SPLITS) for d in DISTRICTS}
    ids_ok = True
    for d in DISTRICTS:
        allst = [r["stem"] for s in SPLITS for r in res[d][s]]
        ids_ok &= (len(allst) == len(set(allst)) == len(use[d]) and set(allst) == {r["stem"] for r in use[d]})
    ok_all &= verdict("1_exactly_one_split", ids_ok and all(cnt[d] == EXPECT[d] for d in DISTRICTS),
                      "counts %s expected %s" % (cnt, EXPECT))
    ov = overlap(res)
    ok_all &= verdict("2_no_common_stem", all(not v for v in ov.values()), "overlapping stems %s" % {d: len(v) for d, v in ov.items()})
    # planted
    bad = copy_planted = {d: {s: list(res[d][s]) for s in SPLITS} for d in DISTRICTS}
    PD = DISTRICTS[0]   # step 9p: the planted stem comes from the first district of the run (Madrid for every old value: unchanged)
    victim = res[PD]["test"][0]
    copy_planted[PD]["dev"] = copy_planted[PD]["dev"] + [victim]
    ovp = overlap(copy_planted)
    named = {d: v for d, v in ovp.items() if v}
    planted_fired = (named == {PD: {victim["stem"]}})
    verdict("3a_planted_overlap_check", not all(not v for v in ovp.values()),
            "check verdict on planted copy = FAIL (expected); named %s; planted %s -> %s" % (named, victim["stem"], "exactly that building" if planted_fired else "WRONG"))
    ok_all &= planted_fired
    ovu = overlap(res)
    ok_all &= verdict("3b_unplanted_again", all(not v for v in ovu.values()), "overlapping stems %s" % {d: len(v) for d, v in ovu.items()})
    # determinism
    res2 = split(use, SEED)
    md5b2 = {(d, s): md5b(list_bytes(res2[d][s])) for d in DISTRICTS for s in SPLITS}
    ok_all &= verdict("4a_same_seed_identical", md5b2 == md5, "%d of %d md5 equal" % (len(md5), len(md5)) if md5b2 == md5 else "DIFFER")
    res3 = split(use, SEED + 1)
    md5b3 = {(d, s): md5b(list_bytes(res3[d][s])) for d in DISTRICTS for s in SPLITS}
    differ = sum(1 for k in md5 if md5b3[k] != md5[k])
    ok_all &= verdict("4b_other_seed_differs", differ == len(md5), "%d of %d lists differ with seed %d" % (differ, len(md5), SEED + 1))   # step 9o: len(md5) = 6 with two districts (unchanged), 3 on win5
    print("\nALL CHECKS", "PASS" if ok_all else "FAIL")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
