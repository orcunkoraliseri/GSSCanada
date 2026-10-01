# -*- coding: utf-8 -*-
"""5J Step 7 part D: the draw rule as code (Speed; Spain only). Library + job entry (python s7_draws.py seal).
ASSIGNMENT RULE (R7-2/R7-3). A draw d has a seed s_d (draws.json "seeds"[d]). For every twin in id order (es_T001 ...) a generator
random.Random("<s_d>|<twin_id>") draws, with replacement, n_dwellings households from the pool UNIFORMLY (manager ruling 04:34:
the pool is itself a weight-proportional draw) (random.Random.choices(hids, k=n_dwellings)); dwelling j gets the j-th draw. Pool = hh/pool.csv
(the 60 campaign households + the new ones), in file order; column `weight` (diary weight of the lowest-pid member) is NOT used here.
SEEDS. draws.json: per-draw seeds for 1,000 draws = random.Random(20261003).getrandbits(62) in order; the 20 EnergyPlus-check draw
indices = sorted(random.Random("20261003|check").sample(range(200), 20)) (range 0..199 so every one of them exists whatever N is chosen).
Both are written and sealed (md5 into in/SEALS.md5) BEFORE any surrogate or EnergyPlus run (validation 3.2)."""
import io, json, os, random, sys
import s7_common as s7

N_MAX = 1000
N_CHECK = 20
CHECK_RANGE = 200


def make_seeds(master=s7.SEED_DRAWS, n=N_MAX):
    rng = random.Random(master)
    return [rng.getrandbits(62) for _ in range(n)]


def make_check_indices(master=s7.SEED_DRAWS):
    return sorted(random.Random("%d|check" % master).sample(range(CHECK_RANGE), N_CHECK))


def load_pool(path=None):
    rows = s7.read_csv(path or (s7.HH + "pool.csv"))
    return [r["hid"] for r in rows], [float(r["weight"]) for r in rows], rows


def load_twins(path=None):
    rows = s7.read_csv(path or (s7.IN + "twins_info_es.csv"))
    rows.sort(key=lambda r: r["twin_id"])
    return [(r["twin_id"], r["class"], int(r["twin_dwellings"]), r) for r in rows]


def assign(seed, twins, hids, weights):
    """{twin_id: [hid of dwelling 0, 1, ...]} for one draw."""
    out = {}
    for tid, _cls, nd, _r in twins:
        rng = random.Random("%d|%s" % (seed, tid))
        out[tid] = rng.choices(hids, k=nd)          # manager ruling 2026-10-01 04:34: UNIFORM over the pool (the pool is already a weight-proportional sample; weighting again counts weight twice). `weights` kept in the signature, unused.
    return out


def placement(hid_list):
    return ";".join("%d:%s" % (j, h) for j, h in enumerate(hid_list))


def main():
    s7.stamp("s7_draws seal start")
    fails = []

    def gate(name, ok, text=""):
        print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
        if not ok:
            fails.append(name)
    for nm in ("sample_buildings.csv", "twins_es.csv", "twins_info_es.csv"):
        gate("input_%s_is_sealed_and_unchanged" % nm, any(l.split()[1] == nm and l.split()[0] == s7.md5(s7.IN + nm) for l in io.open(s7.IN + "SEALS.md5") if len(l.split()) == 2))
    hids, w, prow = load_pool()
    twins = load_twins()
    gate("pool_loaded", len(hids) == len(set(hids)) and len(hids) > 60, "pool=%d" % len(hids))
    seeds = make_seeds()
    gate("seeds_distinct", len(set(seeds)) == N_MAX)
    chk = make_check_indices()
    gate("check_indices_20_distinct_inside_0_199", len(set(chk)) == 20 and max(chk) < CHECK_RANGE)
    dj = s7.IN + "draws.json"
    doc = {"master_seed": s7.SEED_DRAWS, "n_draws_max": N_MAX, "seeds": seeds, "check_indices": chk, "check_index_range": "0..%d" % (CHECK_RANGE - 1),
           "seed_rule": "random.Random(20261003).getrandbits(62) x 1000", "check_rule": "sorted(random.Random('20261003|check').sample(range(200), 20))",
           "assignment_rule": "see s7_draws.py header: per twin random.Random('<seed>|<twin_id>').choices(pool hids, k=n_dwellings), UNIFORM (manager ruling 04:34)",
           "pool_csv_md5": s7.md5(s7.HH + "pool.csv"), "twins_info_md5": s7.md5(s7.IN + "twins_info_es.csv"), "pool_size": len(hids), "n_twin_dwellings": sum(t[2] for t in twins)}
    if os.path.exists(dj):
        old = json.load(io.open(dj, encoding="utf-8"))
        gate("existing_draws_json_equals_the_rule", old["seeds"] == seeds and old["check_indices"] == chk)
    else:
        with io.open(dj, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1)
    s7.seal(dj)
    print("CHECK_INDICES %s" % chk)
    # ---- assignment checks
    a0 = assign(seeds[0], twins, hids, w)
    a0b = assign(seeds[0], twins, hids, w)
    a1 = assign(seeds[1], twins, hids, w)
    gate("same_seed_same_assignment", a0 == a0b)
    gate("two_draws_with_different_seeds_differ (validation 1.3; the check must FAIL on the same seed)", a0 != a1)
    gate("seen_failing_same_seed_twice_would_not_differ", not (a0 != a0b))
    gate("every_twin_gets_one_household_per_dwelling", all(len(a0[t[0]]) == t[2] for t in twins), "dwellings=%d" % sum(len(v) for v in a0.values()))
    gate("every_assigned_hid_is_in_the_pool_and_has_a_folder", all(h in set(hids) for v in a0.values() for h in v) and all(os.path.exists(s7.POOL + "es_%s/household.json" % h) for v in a0.values() for h in set(v)))
    # ---- printed examples of draw 0
    byhid = {r["hid"]: r for r in prow}
    ex = []
    for tid, _c, nd, _r in twins:
        for j in range(nd):
            ex.append((tid, j, a0[tid][j]))
    for tid, j, h in (ex[0], ex[len(ex) // 2], ex[-1]):
        r = byhid[h]
        print("EXAMPLE draw 0 (seed %d): twin %s dwelling %d -> household %s weight %s source %s trained_by_model %s members %s" % (seeds[0], tid, j, h, r["weight"], r["source"], r["trained_by_model"], r["n_members"]))
    newshare = sum(1 for _t, _j, h in ex if byhid[h]["source"] == "new") / float(len(ex))
    trained = sum(1 for _t, _j, h in ex if byhid[h]["trained_by_model"] == "1") / float(len(ex))
    print("DRAW0 share of dwellings with a NEW household (not one of the 60) %.3f ; with a household the model was trained on %.3f ; dwellings %d" % (newshare, trained, len(ex)))
    print("SUMMARY fails=%d %s" % (len(fails), fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "seal":
        main()
