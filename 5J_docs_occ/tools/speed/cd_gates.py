# 5J campaign design gates C1-C7 (+ seen-failing on scratch copies). Runs on Speed. Reads the written csv files from disk only.
import csv, io, math, os, sys, collections, hashlib
R = "/speed-scratch/o_iseri/5J/campaign_prep/"
OUT = R + "out/"
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--runs-pattern", default=OUT + "campaign_runs_%s.csv", help="path pattern of the run tables, %s = country")
_ap.add_argument("--no-seenfail", action="store_true", help="skip the seen-failing section (used on the OLD tables)")
ARGS = _ap.parse_args()
PATTERN = ARGS.runs_pattern
SCR = R + "scratch/"
POOLS = ["dev", "val", "test"]
P = 3
COLS = ["run_id", "country", "climate_id", "building_id", "class", "k", "n_floors", "n_dwellings", "pool", "building_split",
        "replicate", "seed", "placement"]


def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


def wr(p, rows):
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


hsplit = {(r["country"], r["household_id"].split("_", 1)[1]): r["split"] for r in rd(OUT + "splits_households.csv")}
ktab = {r["building_id"]: r for r in rd(OUT + "k_table_es_it.csv")}
bsplit = {r["building_id"]: r["split"] for r in rd(OUT + "splits_buildings.csv")}
climates = collections.defaultdict(list)
for r in rd(R + "in/climates_es_it.csv"):
    climates[r["country"]].append(r["climate_id"])
pools = {cc: {p: [h for (c, h), s in hsplit.items() if c == cc and s == p] for p in POOLS} for cc in ("es", "it")}


def slots(row):
    out = []
    for it in row["placement"].split(";"):
        j, h = it.split(":", 1)
        out.append((int(j), h))
    return out


def base_key(row):
    rid = row["run_id"]
    parts = rid.split("_")
    return (row["building_id"], row["pool"], parts[4])


def g_c1_slots(cc, rows):
    bad = []
    for cl in climates[cc]:
        for b in sorted(b for b in ktab if ktab[b]["country"] == cc and ktab[b]["class"] in ("MFH", "AB")):
            cnt = collections.Counter()
            for r in rows:
                if r["building_id"] == b and r["climate_id"] == cl and r["replicate"] == "0" and r["pool"] in POOLS:
                    for j, h in slots(r):
                        cnt[h] += 1
            allh = [h for p in POOLS for h in pools[cc][p]]
            low = [h for h in allh if cnt[h] < P]
            if low:
                bad.append("%s/%s %d hh below %d (min %d)" % (b, cl, len(low), P, min(cnt[h] for h in allh)))
    return (not bad, "all MFH/AB buildings x %d climates: every household >= %d dwellings" % (len(climates[cc]), P) if not bad else "; ".join(bad[:4]))


def distinct_below(cc, rows):
    """(building, climate, household) triples whose household (in its own pool) sits in fewer than min(3, n_dwellings) DISTINCT dwelling indices."""
    out = []
    for cl in climates[cc]:
        for b in sorted(b for b in ktab if ktab[b]["country"] == cc and ktab[b]["class"] in ("MFH", "AB")):
            n = int(ktab[b]["n_dwellings"])
            bar = min(P, n)
            seen = collections.defaultdict(set)
            for r in rows:
                if r["building_id"] == b and r["climate_id"] == cl and r["replicate"] == "0" and r["pool"] in POOLS:
                    for j, h in slots(r):
                        seen[h].add(j)
            for p in POOLS:
                for h in pools[cc][p]:
                    if len(seen[h]) < bar:
                        out.append((b, cl, h, len(seen[h]), bar))
    return out


def g_c1_distinct(cc, rows):
    low = distinct_below(cc, rows)
    per_cl = collections.Counter(cl for _, cl, _, _, _ in low)
    pairs = {(b, h) for b, _, h, _, _ in low}
    bld_ = sorted({b for b, _, _, _, _ in low})
    det = ("all MFH/AB buildings x %d climates: every household in >= min(3, n_dwellings) DISTINCT dwellings" % len(climates[cc])) if not low else \
        "(building, household) pairs below the bar: %d; per climate %s; buildings %s" % (len(pairs), dict(per_cl), ",".join(bld_[:8]))
    return (not low, det)


def g_c2(cc, rows):
    bad = 0
    for r in rows:
        if r["pool"] in POOLS:
            for j, h in slots(r):
                if hsplit.get((cc, h)) != r["pool"]:
                    bad += 1
        elif r["pool"] == "b0":
            for j, h in slots(r):
                if h != cc + "_avg":
                    bad += 1
        else:
            bad += 1
    return (bad == 0, "%d rows checked, %d slots with a household outside the run's pool" % (len(rows), bad))


def g_c3(cc, rows):
    groups = collections.defaultdict(list)
    for r in rows:
        if r["replicate"] == "0":
            groups[base_key(r)].append((r["climate_id"], r["placement"], r["seed"]))
    bad = 0
    for k, v in groups.items():
        if len({c for c, _, _ in v}) != len(climates[cc]) or len(v) != len(climates[cc]) or len({(p, s) for _, p, s in v}) != 1:
            bad += 1
    return (bad == 0, "%d run groups, %d not identical across the %d climates" % (len(groups), bad, len(climates[cc])))


def g_c4(cc, rows):
    cnt = collections.Counter()
    for r in rows:
        if r["replicate"] == "0" and r["class"] in ("SFH", "TH") and r["pool"] in POOLS:
            cnt[(r["building_id"], slots(r)[0][1], r["climate_id"])] += 1
    exp = [(b, h, cl) for b in ktab if ktab[b]["country"] == cc and ktab[b]["class"] in ("SFH", "TH")
           for p in POOLS for h in pools[cc][p] for cl in climates[cc]]
    missing = [k for k in exp if cnt[k] == 0]
    extra = [k for k, n in cnt.items() if n > 1]
    unexpected = [k for k in cnt if k not in set(exp)]
    return (not (missing or extra or unexpected), "expected %d combos, present exactly once: %d, missing %d, repeated %d, unexpected %d"
            % (len(exp), sum(1 for k in exp if cnt[k] == 1), len(missing), len(extra), len(unexpected)))


def expected_counts(cc):
    e = collections.Counter()
    ncl = len(climates[cc])
    for b, k in ktab.items():
        if k["country"] != cc:
            continue
        n_dw = int(k["n_dwellings"])
        for p in POOLS:
            if k["class"] in ("SFH", "TH"):
                e[(k["class"], p)] += len(pools[cc][p]) * ncl
            else:
                e[(k["class"], p)] += -(-len(pools[cc][p]) * P // n_dw) * ncl
        e[(k["class"], "b0")] += ncl
    return e


def g_c5(cc, rows):
    e = expected_counts(cc)
    o = collections.Counter((r["class"], r["pool"]) for r in rows if r["replicate"] == "0")
    nrep = sum(1 for r in rows if r["replicate"] != "0")
    ok = (e == o) and nrep == 100
    return (ok, "observed==formula for %d class/pool cells; replicates %d (formula 10 inputs x 10); total %d"
            % (len(e), nrep, len(rows)))


def g_c6(cc, rows):
    c = collections.Counter(r["run_id"] for r in rows)
    d = [k for k, n in c.items() if n > 1]
    return (not d, "%d run_ids, %d duplicated" % (len(c), len(d)))


def g_c7(cc, rows):
    bad = 0
    n_ck = 0
    for r in rows:
        s = slots(r)
        if [j for j, _ in s] != list(range(int(r["n_dwellings"]))):
            bad += 1
            continue
        if r["class"] in ("MFH", "AB") and r["pool"] in POOLS and int(r["n_dwellings"]) <= len(pools[cc][r["pool"]]):
            n_ck += 1
            hs = [h for _, h in s]
            if len(set(hs)) != len(hs):
                bad += 1
    return (bad == 0, "slot indices 0..n-1 in every run; %d runs checked for no household twice; %d bad" % (n_ck, bad))


GATES = [("C1_slots", g_c1_slots, "every household in >= 3 dwelling SLOTS of every MFH/AB building (old C1; counts placements)"),
         ("C1_distinct", g_c1_distinct, "every household in >= min(3, n_dwellings) DISTINCT dwellings of every MFH/AB building"), ("C2", g_c2, "no run mixes pools"),
         ("C3", g_c3, "placements identical across the 3 climates"), ("C4", g_c4, "every SFH/TH building x household x climate once"),
         ("C5", g_c5, "run counts equal the formula"), ("C6", g_c6, "no duplicate run_id"),
         ("C7", g_c7, "slot indices complete; no household twice in a run when n_dwellings <= pool")]


def run_gate(name, fn, cc, path):
    try:
        ok, det = fn(cc, rd(path))
        return ("PASS" if ok else "FAIL"), det
    except Exception as ex:
        return "NOT_EVALUABLE", "%s: %s" % (type(ex).__name__, ex)


tally = collections.Counter()
for cc in ("es", "it"):
    p = PATTERN % cc
    for name, fn, desc in GATES:
        st, det = run_gate(name, fn, cc, p)
        tally[st] += 1
        print("GATE %s %s %s | %s | %s" % (name, cc, st, desc, det))

# C5 printed table (INFO)
for cc in ("es", "it"):
    rows = rd(PATTERN % cc)
    e = expected_counts(cc)
    o = collections.Counter((r["class"], r["pool"]) for r in rows if r["replicate"] == "0")
    print("COUNTS %s (class, pool: observed / formula), climates=%d" % (cc, len(climates[cc])))
    for cl in ("SFH", "TH", "MFH", "AB"):
        print("COUNTS %s %s %s" % (cc, cl, " ".join("%s=%d/%d" % (p, o[(cl, p)], e[(cl, p)]) for p in POOLS + ["b0"])))
    nr = sum(1 for r in rows if r["replicate"] != "0")
    n_b0 = sum(1 for r in rows if r["pool"] == "b0")
    n_main = sum(1 for r in rows if r["replicate"] == "0" and r["pool"] != "b0")
    print("COUNTS %s main=%d b0=%d replicates=%d total=%d" % (cc, n_main, n_b0, nr, len(rows)))
    per_cl = collections.Counter(r["climate_id"] for r in rows if r["replicate"] == "0")
    print("COUNTS %s per climate (rep 0, incl b0): %s" % (cc, dict(per_cl)))

# ---------------------------------------------------------------- INFO: position variety per household (floors, end/middle flats)
def position_info(cc, rows):
    c0 = climates[cc][0]
    for cl in ("MFH", "AB"):
        per_fl = collections.Counter()
        per_end = collections.Counter()
        per_mid = collections.Counter()
        both = tot = 0
        ks = collections.Counter()
        for b in sorted(b for b in ktab if ktab[b]["country"] == cc and ktab[b]["class"] == cl):
            kk = int(ktab[b]["k"])
            ks[kk] += 1
            seen = collections.defaultdict(set)
            for r in rows:
                if r["building_id"] == b and r["climate_id"] == c0 and r["replicate"] == "0" and r["pool"] in POOLS:
                    for j, h in slots(r):
                        seen[h].add(j)
            for h, js in seen.items():
                nfl = len({j // kk for j in js})
                nend = sum(1 for j in js if (j % kk) in (0, kk - 1))
                nmid = len(js) - nend
                per_fl[nfl] += 1
                per_end[nend] += 1
                per_mid[nmid] += 1
                tot += 1
                both += 1 if (nend >= 1 and nmid >= 1) else 0
        print("POSITION_INFO %s %s (climate %s; k per building %s; %d building x household pairs)" % (cc, cl, c0, dict(sorted(ks.items())), tot))
        print("POSITION_INFO %s %s distinct floors per household: %s" % (cc, cl, dict(sorted(per_fl.items()))))
        print("POSITION_INFO %s %s distinct END flats per household: %s ; distinct MIDDLE flats: %s ; households with >=1 end and >=1 middle: %d of %d" % (
            cc, cl, dict(sorted(per_end.items())), dict(sorted(per_mid.items())), both, tot))


for cc in ("es", "it"):
    position_info(cc, rd(PATTERN % cc))
    low = distinct_below(cc, rd(PATTERN % cc))
    print("C1_DISTINCT_PAIRS %s (building, climate, household) below the bar: %d ; distinct (building, household) pairs: %d" % (
        cc, len(low), len({(b, h) for b, _, h, _, _ in low})))
    for b in sorted({b for b, _, _, _, _ in low}):
        print("C1_DISTINCT_BUILDING %s %s households below bar (first climate): %d" % (cc, b, len({h for bb, cl, h, _, _ in low if bb == b and cl == climates[cc][0]})))
print("PATCH cd_gates C1_distinct %s" % ("OK" if any(g[0] == "C1_distinct" for g in GATES) else "MISSING"))

if ARGS.no_seenfail:
    print("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d (tables %s, %d gates x 2 countries); seen-failing section SKIPPED (--no-seenfail)" % (
        tally["PASS"], tally["FAIL"], tally["NOT_EVALUABLE"], PATTERN, len(GATES)))
    print("EXIT_CODE 0 (this mode: 0 = the script ran to the end; the verdicts are the GATE lines)")
    sys.exit(0)

# ---------------------------------------------------------------- seen failing, scratch copies only
os.makedirs(SCR, exist_ok=True)


def mut(cc, label, fn):
    rows = rd(PATTERN % cc)
    desc = fn(rows)
    p = SCR + "seenfail_%s_%s.csv" % (label, cc)
    wr(p, rows)
    return p, desc


cc = "es"
base = rd(PATTERN % cc)
c1 = [r for r in base if r["climate_id"] == climates[cc][0] and r["replicate"] == "0" and r["class"] in ("MFH", "AB") and r["pool"] == "val"]
c1.sort(key=lambda r: int(r["n_dwellings"]) * -(-len(pools[cc]["val"]) * P // int(r["n_dwellings"])) - 30)
tgt1 = c1[0]["run_id"]


def m1(rows):
    rows[:] = [r for r in rows if r["run_id"] != tgt1]
    return "dropped run %s" % tgt1


def m2(rows):
    for r in rows:
        if r["class"] in ("MFH", "AB") and r["pool"] == "dev" and r["replicate"] == "0":
            s = r["placement"].split(";")
            s[0] = "0:" + pools[cc]["val"][0]
            r["placement"] = ";".join(s)
            return "planted val household %s in dev run %s" % (pools[cc]["val"][0], r["run_id"])


def m3(rows):
    cl2 = climates[cc][1]
    for r in rows:
        if r["climate_id"] == cl2 and r["class"] in ("MFH", "AB") and r["pool"] == "dev" and r["replicate"] == "0":
            s = r["placement"].split(";")
            s[0] = "0:" + [h for h in pools[cc]["dev"] if h != s[0].split(":")[1]][0]
            r["placement"] = ";".join(s)
            return "changed slot 0 of %s" % r["run_id"]


def m4(rows):
    for r in rows:
        if r["class"] == "SFH" and r["replicate"] == "0" and r["pool"] == "dev":
            rows.remove(r)
            return "dropped SFH run %s" % r["run_id"]


def m5(rows):
    for r in rows:
        if r["class"] == "MFH" and r["replicate"] == "0" and r["pool"] == "test":
            rows.remove(r)
            return "dropped MFH run %s" % r["run_id"]


def m6(rows):
    rows.append(dict(rows[5]))
    return "duplicated row %s" % rows[5]["run_id"]


def m7(rows):
    for r in rows:
        if r["class"] in ("MFH", "AB") and r["pool"] == "dev" and r["replicate"] == "0" and 2 <= int(r["n_dwellings"]) <= 40:
            s = r["placement"].split(";")
            s[1] = "1:" + s[0].split(":")[1]
            r["placement"] = ";".join(s)
            return "household of slot 0 copied to slot 1 in %s" % r["run_id"]


def m1d(rows):
    """plant a repeated flat: household h keeps flat f in run r1 and gets flat f again in run r2 (swap with the household sitting at f in r2)."""
    c0 = climates[cc][0]
    for b in sorted(b for b in ktab if ktab[b]["country"] == cc and ktab[b]["class"] in ("MFH", "AB") and int(ktab[b]["n_dwellings"]) >= 4):
        dev = [r for r in rows if r["building_id"] == b and r["climate_id"] == c0 and r["replicate"] == "0" and r["pool"] == "dev"]
        ent = collections.defaultdict(list)
        for r in dev:
            for j, h in slots(r):
                ent[h].append((r, j))
        for h, e in ent.items():
            if len({j for _, j in e}) >= 3 and len(e) >= 3:
                (r1, f), (r2, g) = e[0], e[1]
                if r1 is r2:
                    continue
                s = slots(r2)
                h3 = s[f][1]
                if h3 == h:
                    continue
                s[g] = (g, h3)
                s[f] = (f, h)
                r2["placement"] = ";".join("%d:%s" % x for x in s)
                return "household %s now has flat %d in %s and %s (swapped with %s)" % (h, f, r1["run_id"], r2["run_id"], h3)
    return "NO PLANT POSSIBLE"


sf = collections.Counter()
for (name, fn, desc), m in zip(GATES, (m1, m1d, m2, m3, m4, m5, m6, m7)):
    p, what = mut(cc, name, m)
    st, det = run_gate(name, fn, cc, p)
    fired = (st == "FAIL")
    sf["fired" if fired else "NOT_FIRED"] += 1
    print("SEENFAIL %s %s (scratch copy %s; %s) | %s" % (name, st, os.path.basename(p), what, det))
    if not fired:
        print("SEENFAIL_PROBLEM %s did not fail on its planted defect" % name)
print("SEENFAIL_SUMMARY fired=%d not_fired=%d (of 8)" % (sf["fired"], sf["NOT_FIRED"]))
print("SUMMARY PASS=%d FAIL=%d NOT_EVALUABLE=%d (real files, 8 gates x 2 countries); SEENFAIL fired=%d/8" % (
    tally["PASS"], tally["FAIL"], tally["NOT_EVALUABLE"], sf["fired"]))
code = 0 if (tally["PASS"] == 16 and sf["fired"] == 8) else 1
print("EXIT_CODE %d (0 = all 16 real gates PASS and all 8 seen-failing fired; 1 = anything else)" % code)
sys.exit(code)
