# 5J campaign design (Spain + Italy), Part A (k table), Part B (splits), Part C (run tables). Runs on Speed only.
# Reads: R/in/{buildings,climates,households}_es_it.csv (es+it rows only), R/out/dwelling_count_{es,it}.csv, R/tabula_in/.
import csv, hashlib, io, json, math, os, random, sys, platform, collections, importlib
R = "/speed-scratch/o_iseri/5J/campaign_prep/"
OUT = R + "out/"   # inputs (dwelling counts) are read from here
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--distinct-flats", dest="distinct", action="store_true", default=True)
_ap.add_argument("--no-distinct-flats", dest="distinct", action="store_false", help="old v1 behaviour (no repair)")
_ap.add_argument("--outdir", default=OUT, help="where tables are WRITTEN (default R/out/)")
ARGS = _ap.parse_args()
WOUT = ARGS.outdir if ARGS.outdir.endswith("/") else ARGS.outdir + "/"
os.makedirs(WOUT, exist_ok=True)
REPO = R + "repo/"
sys.path.insert(0, REPO + "5J_docs_occ/tools")
print("python", sys.version.split()[0], "host", platform.node())
mz = importlib.import_module("5thJ_idf_mz")
mz._j5.TOOLS_4J = REPO + "4J_docs_occ/tools"
s8 = mz._s8
CC = {"es": 0, "it": 1}
CLASSES = ["SFH", "TH", "MFH", "AB"]
POOLS = ["dev", "val", "test"]
P = 3


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8")))


bld = rd(R + "in/buildings_es_it.csv")
clim = rd(R + "in/climates_es_it.csv")
hh = rd(R + "in/households_es_it.csv")
assert {r["country"] for r in bld} == {"es", "it"} and {r["country"] for r in hh} == {"es", "it"}
assert {r["country"] for r in clim} == {"es", "it"}
print("INPUT rows buildings=%d climates=%d households=%d (only es/it present)" % (len(bld), len(clim), len(hh)))
print("INPUT md5 households_es_it.csv", md5(R + "in/households_es_it.csv"))

# ------------------------------------------------------------------ Part A: k per building
info = {}
for cc in CC:
    rows, _ = s8.load_rows(R + "tabula_in/", cc)
    rowby = {r["Code_Building"]: r for r in rows}
    TAB = OUT + "dwelling_count_%s.csv" % cc
    for b in [r for r in bld if r["country"] == cc]:
        d = s8.derive(rowby[b["archetype_code"]])
        F = int(round(d["n_storey"]))
        assert abs(d["n_storey"] - F) < 1e-9 and d["cls"] == b["class"], (b["building_id"], d["cls"], b["class"])
        if b["class"] in ("MFH", "AB"):
            k, n_apt, _ = mz.k_from_tabula(TAB, d["code"], F)
            n_dw = k * F
        else:
            k, n_apt, n_dw = 1, float("nan"), 1
        info[b["building_id"]] = {"cc": cc, "cls": b["class"], "code": d["code"], "F": F, "k": k, "n_dw": n_dw, "n_apt": n_apt,
                                  "num": int(b["building_id"].split("_B")[1])}
for cc in ("it", "es"):
    print("=== TABULA n_Apartment vs modelled dwellings, %s (per Code_Building; modelled = k x n_Storey) ===" % cc)
    print("code | class | n_Storey | TABULA n_Apartment | k | modelled n_dwellings | difference")
    seen = set()
    for bid in sorted(info):
        i = info[bid]
        if i["cc"] == cc and i["cls"] in ("MFH", "AB") and i["code"] not in seen:
            seen.add(i["code"])
            print("KTABLE_%s %s | %s | %d | %g | %d | %d | %+g" % (cc.upper(), i["code"], i["cls"], i["F"], i["n_apt"], i["k"], i["n_dw"], i["n_dw"] - i["n_apt"]))
with io.open(WOUT + "k_table_es_it.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["building_id", "country", "class", "code", "n_floors", "tabula_n_apartment", "k", "n_dwellings"])
    for bid in sorted(info):
        i = info[bid]
        w.writerow([bid, i["cc"], i["cls"], i["code"], i["F"], "" if i["cls"] in ("SFH", "TH") else "%g" % i["n_apt"], i["k"], i["n_dw"]])
for cc in CC:
    mx = max((i["n_dw"], b) for b, i in info.items() if i["cc"] == cc)
    print("MAX_DWELLINGS %s %s dwellings=%d floors=%d" % (cc, mx[1], mx[0], info[mx[1]]["F"]))

# ------------------------------------------------------------------ Part B: splits
hh_rows = []
for cc in CC:
    rows = sorted([r for r in hh if r["country"] == cc], key=lambda r: int(r["draw_order"]))
    assert len(rows) == 60 and len({r["hid"] for r in rows}) == 60
    hh_rows += rows
pools = {cc: {p: [r["hid"] for r in hh_rows if r["country"] == cc and r["split_draft"] == p] for p in POOLS} for cc in CC}
for cc in CC:
    print("POOLS %s dev=%d val=%d test=%d" % (cc, len(pools[cc]["dev"]), len(pools[cc]["val"]), len(pools[cc]["test"])))
    sizes = collections.Counter((r["split_draft"], r["size"]) for r in hh_rows if r["country"] == cc)
    for p in POOLS:
        print("HH_BY_SIZE %s %s %s" % (cc, p, " ".join("size%s=%d" % (s, n) for (pp, s), n in sorted(sizes.items()) if pp == p)))
with io.open(WOUT + "splits_households.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["household_id", "country", "split"])
    for r in hh_rows:
        w.writerow([r["household_id"], r["country"], r["split_draft"]])
bsplit = {}
for cc, c in CC.items():
    rng = random.Random(7000 + c)
    ids = {cl: sorted(b["building_id"] for b in bld if b["country"] == cc and b["class"] == cl) for cl in CLASSES}
    for cl in CLASSES:
        assert len(ids[cl]) == 10, (cc, cl)
        l = list(ids[cl])
        rng.shuffle(l)
        bsplit[l[0]] = "test"
        bsplit[l[1]] = "val"
        for x in l[2:]:
            bsplit[x] = "dev"
    dev = sorted(b for b in bsplit if b.startswith(cc + "_") and bsplit[b] == "dev")
    t = rng.choice(dev)
    dev.remove(t)
    bsplit[t] = "test"
    v = rng.choice(dev)
    dev.remove(v)
    bsplit[v] = "val"
    cnt = collections.Counter((info[b]["cls"], s) for b, s in bsplit.items() if b.startswith(cc + "_"))
    tot = collections.Counter(s for b, s in bsplit.items() if b.startswith(cc + "_"))
    print("BSPLIT %s dev=%d val=%d test=%d" % (cc, tot["dev"], tot["val"], tot["test"]))
    for cl in CLASSES:
        print("BSPLIT_CLASS %s %s dev=%d val=%d test=%d" % (cc, cl, cnt[(cl, "dev")], cnt[(cl, "val")], cnt[(cl, "test")]))
    assert tot["dev"] == 30 and tot["val"] == 5 and tot["test"] == 5
    assert all(cnt[(cl, s)] >= 1 for cl in CLASSES for s in POOLS)
with io.open(WOUT + "splits_buildings.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["building_id", "country", "class", "split"])
    for b in bld:
        w.writerow([b["building_id"], b["country"], b["class"], bsplit[b["building_id"]]])

# ------------------------------------------------------------------ Part C: run tables
COLS = ["run_id", "country", "climate_id", "building_id", "class", "k", "n_floors", "n_dwellings", "pool", "building_split",
        "replicate", "seed", "placement"]
swap_count = collections.Counter()
fallback_count = collections.Counter()


def mfh_runs(cc, bid, pool_idx):
    """list of (r, [hids], seeds) for one MFH/AB building and one pool."""
    i = info[bid]
    c = CC[cc]
    pool = pools[cc][POOLS[pool_idx]]
    n_dw = i["n_dw"]
    n_runs = -(-len(pool) * P // n_dw)
    slots = n_runs * n_dw
    n_perm = -(-slots // len(pool))
    seq, seeds = [], []
    for m in range(n_perm):
        assert m < 10
        seed = 100000 * c + 1000 * i["num"] + 10 * pool_idx + m
        seeds.append(seed)
        l = list(pool)
        random.Random(seed).shuffle(l)
        seq += l
    seq = seq[:slots]
    if n_dw <= len(pool):
        for x in range(slots):
            s0 = (x // n_dw) * n_dw
            if seq[x] in seq[s0:x]:
                done = False
                for y in range(x + 1, slots):
                    ry = (y // n_dw) * n_dw
                    run_y = seq[ry:ry + n_dw]
                    others = run_y[:y - ry] + run_y[y - ry + 1:]
                    if seq[y] not in seq[s0:x] and seq[x] not in others:
                        seq[x], seq[y] = seq[y], seq[x]
                        swap_count[(cc, bid)] += 1
                        done = True
                        break
                if not done:
                    # fallback, NOT in the ruling (nearest PRECEDING slot); counted and reported
                    for y in range(x - 1, -1, -1):
                        ry = (y // n_dw) * n_dw
                        run_y = seq[ry:ry + n_dw]
                        others = run_y[:y - ry] + run_y[y - ry + 1:]
                        if seq[y] not in seq[s0:x] and seq[x] not in others:
                            seq[x], seq[y] = seq[y], seq[x]
                            swap_count[(cc, bid)] += 1
                            fallback_count[(cc, bid)] += 1
                            done = True
                            break
                if not done:
                    raise SystemExit("NO SWAP FOUND %s %s pool %d slot %d" % (cc, bid, pool_idx, x))
    runs = [seq[r * n_dw:(r + 1) * n_dw] for r in range(n_runs)]
    if ARGS.distinct:
        repair_distinct(cc, bid, POOLS[pool_idx], runs, n_dw, pool)
    return [(r + 1, runs[r], ";".join(str(s) for s in seeds)) for r in range(n_runs)]


# ---- PATCH distinct-flats (2026-09-30): every household in >= min(3, n) DISTINCT flats of a building (its pool)
repair_swaps = collections.Counter()
repair_stuck = []
repair_log = collections.Counter()


def _flats(runs, h):
    return [j for run in runs for j, x in enumerate(run) if x == h]


def repair_distinct(cc, bid, pool, runs, n, pool_list):
    pool_size = len(pool_list)
    t = min(P, n)
    order = list(pool_list)
    guard = 0
    stuck = set()
    while True:
        guard += 1
        if guard > 100000:
            raise SystemExit("REPAIR guard hit %s %s" % (bid, pool))
        h = None
        for x in order:
            if x not in stuck and len(set(_flats(runs, x))) < t:
                h = x
                break
        if h is None:
            break
        fl = _flats(runs, h)
        # first (run a, flat f) whose flat is repeated among h's slots
        a = f = None
        for ra, run in enumerate(runs):
            for j, x in enumerate(run):
                if x == h and fl.count(j) >= 2:
                    a, f = ra, j
                    break
            if a is not None:
                break
        done = False
        hset = set(fl)
        for b in range(len(runs)):
            for g in range(n):
                h2 = runs[b][g]
                if h2 == h or g in hset:
                    continue
                # simulate the swap: (a,f) <- h2, (b,g) <- h
                runs[a][f], runs[b][g] = h2, h
                ok = len(set(_flats(runs, h2))) >= t
                if ok and n <= pool_size:
                    ok = len(set(runs[a])) == len(runs[a]) and len(set(runs[b])) == len(runs[b])
                if ok:
                    repair_swaps[(cc, bid)] += 1
                    repair_log[(cc, bid, pool)] += 1
                    done = True
                    break
                runs[a][f], runs[b][g] = h, h2      # undo
            if done:
                break
        if not done:
            print("REPAIR_STUCK %s %s %s" % (bid, pool, h))
            repair_stuck.append((bid, pool, h))
            stuck.add(h)


def base_runs(cc):
    res = []
    for b in sorted(x["building_id"] for x in bld if x["country"] == cc):
        i = info[b]
        if i["cls"] in ("SFH", "TH"):
            for p in POOLS:
                for r, h in enumerate(pools[cc][p], 1):
                    res.append({"bid": b, "pool": p, "r": r, "placement": "0:%s" % h, "seed": "NA"})
        else:
            for pi, p in enumerate(POOLS):
                for r, hl, sd in mfh_runs(cc, b, pi):
                    res.append({"bid": b, "pool": p, "r": r, "placement": ";".join("%d:%s" % (j, h) for j, h in enumerate(hl)), "seed": sd})
        res.append({"bid": b, "pool": "b0", "r": 1, "placement": ";".join("%d:%s_avg" % (j, cc) for j in range(i["n_dw"])), "seed": "NA"})
    return res


def row_of(cc, cl, base, rep):
    i = info[base["bid"]]
    rid = "%s_%s_%s_%s_%d" % (cc, cl["city"].lower(), base["bid"].split("_")[1], base["pool"], base["r"])
    if rep:
        rid += "_rep%d" % rep
    return {"run_id": rid, "country": cc, "climate_id": cl["climate_id"], "building_id": base["bid"], "class": i["cls"], "k": i["k"],
            "n_floors": i["F"], "n_dwellings": i["n_dw"], "pool": base["pool"], "building_split": bsplit[base["bid"]], "replicate": rep,
            "seed": base["seed"], "placement": base["placement"]}


for cc in CC:
    cls_ = [c for c in clim if c["country"] == cc]
    assert len(cls_) == 3
    base = base_runs(cc)
    rows = []
    for cl in cls_:
        for b_ in base:
            rows.append(row_of(cc, cl, b_, 0))
    ids = sorted(b for b in info if info[b]["cc"] == cc)
    sfhth = [b for b in ids if info[b]["cls"] in ("SFH", "TH")][:5]
    mx = max((info[b]["n_dw"], -info[b]["num"], b) for b in ids if info[b]["cls"] in ("MFH", "AB"))[2]
    mf = [b for b in ids if info[b]["cls"] == "MFH" and b != mx][:2]
    ab = [b for b in ids if info[b]["cls"] == "AB" and b != mx][:2]
    rb = sfhth + mf + ab + [mx]
    assert len(rb) == 10 and len(set(rb)) == 10, rb
    for b in rb:
        src = [x for x in base if x["bid"] == b and x["pool"] == "dev" and x["r"] == 1]
        assert len(src) == 1
        for n in range(1, 11):
            rows.append(row_of(cc, cls_[0], src[0], n))
    with io.open(WOUT + "campaign_runs_%s.csv" % cc, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("RUNS_WRITTEN %s rows=%d md5=%s" % (cc, len(rows), md5(WOUT + "campaign_runs_%s.csv" % cc)))
    print("REPLICATE_INPUTS %s %s (max-dwelling building last)" % (cc, " ".join(rb)))
for k_, v in sorted(swap_count.items()):
    print("SWAPS %s %s swaps=%d fallback_backward=%d" % (k_[0], k_[1], v, fallback_count.get(k_, 0)))
print("SWAPS_TOTAL %d (fallback %d)" % (sum(swap_count.values()), sum(fallback_count.values())))
print("PATCH cd_design distinct-flats %s (flag distinct=%s)" % ("OK" if ARGS.distinct else "OFF (old v1 behaviour)", ARGS.distinct))
for k_, v in sorted(repair_log.items()):
    print("REPAIR_SWAPS %s %s %s swaps=%d" % (k_[0], k_[1], k_[2], v))
print("REPAIR_SWAPS_TOTAL %d" % sum(repair_swaps.values()))
print("REPAIR_STUCK_COUNT %d" % len(repair_stuck))
for f in ("splits_households.csv", "splits_buildings.csv", "k_table_es_it.csv"):
    print("MD5 %s %s" % (f, md5(WOUT + f)))
json.dump({b: {k: v for k, v in i.items() if k != "n_apt"} for b, i in info.items()}, io.open(WOUT + "info_es_it.json", "w"))
print("DESIGN_DONE")
