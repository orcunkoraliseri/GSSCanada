# -*- coding: utf-8 -*-
"""5J Step 7 part C0 (Speed CPU job): the list of 500 NEW Spanish households (R7-2), drawn like households-v2.
Rule (5thJ_design_tables.draw_households, same weights, same key): households of the Spanish corpus that are not among the 60 campaign
households and have a positive weight (weight = weight_ind of the lowest-pid member, episodes_spain.parquet); strata = household size,
allocation proportional to the stratum counts (largest remainder, as v2); inside a stratum the largest keys log(1-u)/w; seed 6 through
rng_for(6, "hh", "es") (v2 used seed 5); the drawn list is shuffled (v2 did this too), so any prefix is roughly stratified.
Writes hh/hids_es_new500.csv (hid,size,weight,draw_order) and hh/hids_es_pilot10.csv (first 10). Runs twice and compares md5."""
import collections, hashlib, importlib, io, math, os, sys
import s7_common as s7

CORPUS = "/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl"
CORPUS_MD5 = "1a5163445291b54114832e192b0d9a05"
PARQ = "/speed-scratch/o_iseri/4J/outputs_step1/episodes_spain.parquet"
FAILS = []


def gate(name, ok, text=""):
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", text), flush=True)
    if not ok:
        FAILS.append(name)


def draw(dt, sizes, weights, exclude, total, seed):
    by_size = collections.defaultdict(list)
    for hid, s in sizes.items():
        w = weights.get(hid)
        if hid in exclude or w is None or not w > 0:
            continue
        by_size[s].append(hid)
    take = dt.alloc(total, dict((s, len(v)) for s, v in by_size.items()))
    rng = dt.rng_for(seed, "hh", "es")
    drawn = []
    for s in sorted(take):
        keyed = sorted(((math.log(1.0 - rng.random()) / weights[hid], hid) for hid in by_size[s]), reverse=True)
        for _, hid in keyed[:take[s]]:
            drawn.append((s, hid))
    rng.shuffle(drawn)
    return drawn, take, dict((s, len(v)) for s, v in by_size.items())


def main():
    s7.stamp("s7_hh_draw start")
    dt = importlib.import_module("5thJ_design_tables")
    gate("corpus_md5", s7.md5(CORPUS) == CORPUS_MD5, s7.md5(CORPUS))
    sizes = dt.read_household_sizes(CORPUS, "es")
    weights = dt.read_household_weights(PARQ, "weight_ind")
    h60 = [r["hid"] for r in s7.read_csv(s7.IN + "ref/hids_es60.csv")]
    gate("60_campaign_hids_in_corpus_and_weighted", len(h60) == 60 and all(h in sizes and weights.get(h) for h in h60), "n=%d" % len(h60))
    print("POPULATION es households=%d sizes=%s" % (len(sizes), dict(sorted(collections.Counter(sizes.values()).items()))))
    drawn, take, avail = draw(dt, sizes, weights, set(h60), 500, s7.SEED_HH)
    drawn2, _, _ = draw(dt, sizes, weights, set(h60), 500, s7.SEED_HH)
    gate("draw_is_reproducible", drawn == drawn2)
    other, _, _ = draw(dt, sizes, weights, set(h60), 500, s7.SEED_HH + 1)
    gate("another_seed_gives_another_list (seen failing for 'same list for any seed')", other != drawn)
    hids = [h for _, h in drawn]
    gate("500_distinct_none_in_the_60", len(hids) == 500 == len(set(hids)) and not (set(hids) & set(h60)), "n=%d" % len(hids))
    print("ALLOCATION by size (500) %s ; available per size %s" % (take, avail))
    print("SIZE_SHARE_500 %s" % dict(sorted(collections.Counter(s for s, _ in drawn).items())))
    os.makedirs(s7.HH, exist_ok=True)
    rows = [[h, s, "%.6f" % weights[h], i + 1] for i, (s, h) in enumerate(drawn)]
    p500 = s7.HH + "hids_es_new500.csv"
    s7.write_csv(p500, ["hid", "size", "weight", "draw_order"], rows)
    p10 = s7.HH + "hids_es_pilot10.csv"
    s7.write_csv(p10, ["hid", "size", "weight", "draw_order"], rows[:10])
    print("WROTE %s md5=%s ; %s md5=%s" % (p500, s7.md5(p500), p10, s7.md5(p10)))
    print("PILOT10 sizes %s hids %s" % (dict(collections.Counter(r[1] for r in rows[:10])), [r[0] for r in rows[:10]]))
    print("SUMMARY fails=%d %s" % (len(FAILS), FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
