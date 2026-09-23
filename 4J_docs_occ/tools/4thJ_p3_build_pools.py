# -*- coding: utf-8 -*-
"""P3 (2026-09-23) -- build the real and raked-donor diary pools that
`4thJ_step9_trigger.py --pool PATH` reads.

Design doc: writing/submission/IMP/impl/P3_appliance_real_and_donor.md, step 2.
This script does NOT modify `4thJ_step9_trigger.py`'s behaviour; it only writes
two new jsonl files per held-out country `c`, in the exact record shape
`4thJ_step7_schedules.load_pool` already reads (one JSON object per line with a
`text` field in the SAME encoded format the Step 3 corpus and the Step 7
generated batches both already use -- confirmed by inspection, not assumed):

  real_<c>.jsonl   -- country c's OWN real diaries from the Step 3 corpus,
                      drawn uniformly (the weight `4thJ_step6_g61_score.py`
                      uses for its "model"/real side is `None`, i.e. every
                      diary counts once -- `L1.budget(records)` is called with
                      no `weights=` argument for that side; confirmed by
                      reading the call, not guessed).
  raked_<c>.jsonl  -- the OTHER two countries' real diaries, raked by the SAME
                      code and the SAME target as `G6.1`
                      (`4thJ_step6_g61_rake_folds.py` / `4thJ_step6_rakeddonor.py`,
                      target `population_<c>.csv`), then drawn with probability
                      proportional to the raked IPF weight, fixed seed, and the
                      leading country token of each drawn diary's `text`
                      rewritten to `c` ("labelled as country c"). `STRATUM_FIELDS`
                      in `4thJ_step7_schedules.py` never includes country, so
                      this label change affects no lookup the trigger performs;
                      it is bookkeeping only. The original donor country is kept
                      alongside as `donor_country` for the C-c control.

Pool size per country = the generated pool's own size for that country
(`Step7_docs/outputs_step7/generated_<leg>_<fold>_constrained.jsonl` line count).

    python 4thJ_p3_build_pools.py --root <4J_docs_occ>
"""
import argparse
import hashlib
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import importlib

rf = importlib.import_module("4thJ_step6_g61_rake_folds")
rd = importlib.import_module("4thJ_step6_rakeddonor")

FOLDS = ("es", "uk", "it")
# Fixed seed for every P3 pool draw (real sample and raked weighted draw
# alike). Not tuned, not re-drawn; picked once and recorded here.
P3_SEED = 20260923


def generated_pool_size(root, fold, leg):
    path = os.path.join(root, "Step7_docs", "outputs_step7",
                        "generated_%s_%s_constrained.jsonl" % (leg, fold))
    if not os.path.exists(path):
        raise SystemExit("no generated pool at %s -- cannot size the P3 pools"
                         % path)
    n = 0
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n, path


def load_corpus(root):
    """Every corpus record, with its raw `text` and its decoded strata."""
    corpus = os.path.join(root, "Step3_docs", "outputs_step3",
                          "4J_step3_corpus.jsonl")
    out = []
    with io.open(corpus, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            f = r["text"].split("|", 1)[0].split(",")
            d = {"country": r["country"], "text": r["text"]}
            for v in rf.VARS:
                d[v] = f[rf.PFX[v]]
            out.append(d)
    return out, corpus


def relabel_country(text, new_country):
    """Rewrite ONLY the leading country token of the encoded `text` field.

    `STRATUM_FIELDS` in `4thJ_step7_schedules.py` is
    `("strat_age_band", "strat_sex", "strat_hh_type", "strat_econ_status")`
    plus `strat_day_type` -- country is never a stratum key, so this changes
    no lookup the trigger performs. It exists only because the design calls
    for the raked pool to be "labelled as country c".
    """
    prefix, rest = text.split("|", 1)
    fields = prefix.split(",")
    fields[0] = new_country
    return ",".join(fields) + "|" + rest


def build_real_pool(all_recs, c, pool_size, seed):
    pool = [r for r in all_recs if r["country"] == c]
    if len(pool) < pool_size:
        raise SystemExit("real pool for %s has only %d records, need %d"
                         % (c, len(pool), pool_size))
    rng = random.Random(("p3real", seed, c))
    return rng.sample(pool, pool_size)


def build_raked_pool(all_recs, c, pool_size, seed):
    donors = [r for r in all_recs if r["country"] != c]
    tgt, n_pop = rf.target_from_population(c)

    # Same collapse logic as `4thJ_step6_g61_rake_folds.run()` / g61_score's
    # `build_null()` -- reused, not re-derived, so a fourth collapse cannot
    # appear here without the registry (`4thJ_step6_g61_rake_folds.
    # REGISTERED_COLLAPSES`) catching it.
    coll = {"strat_hh_type": {"unknown": "other_complex"}}
    if "homemaker" not in tgt["strat_econ_status"]:
        coll["strat_econ_status"] = {"homemaker": "other_inactive"}
    for cat in set(d["strat_econ_status"] for d in donors):
        if cat not in tgt["strat_econ_status"] and cat != "homemaker":
            coll.setdefault("strat_econ_status", {})[cat] = "other_inactive"
    unreg = rf.check_registered(coll)
    if unreg:
        raise SystemExit(
            "REFUSED (raked pool %s): collapse(s) not registered in %s: %s"
            % (c, rf.ADDENDUM,
               "; ".join("%s: %s->%s" % t for t in unreg)))

    res = rd.rake(donors, tgt, c,
                 marginals_source="population_%s.csv|D-S5-11b|P3" % c,
                 collapse=coll)
    rng = random.Random(("p3raked", seed, c))
    drawn = rng.choices(donors, weights=res["weights"], k=pool_size)
    return drawn, res


def write_pool(records, path, relabel_to=None):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in records:
            text = r["text"]
            if relabel_to is not None:
                text = relabel_country(text, relabel_to)
            out = {"text": text,
                  "provenance": "P3_%s" % (relabel_to or r["country"]),
                  "donor_country": r["country"]}
            fh.write(json.dumps(out, sort_keys=True) + "\n")
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--leg", default="leg5")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=P3_SEED)
    args = ap.parse_args(argv)
    out_dir = args.out or os.path.join(args.root, "Step9_docs",
                                       "outputs_step9_P3", "pools")

    all_recs, corpus_path = load_corpus(args.root)
    print("corpus loaded: %d records from %s" % (len(all_recs), corpus_path))

    ok = True
    for c in FOLDS:
        pool_size, gen_path = generated_pool_size(args.root, c, args.leg)
        print("fold %s: generated pool size = %d (%s)" % (c, pool_size, gen_path))

        real = build_real_pool(all_recs, c, pool_size, args.seed)
        real_path = os.path.join(out_dir, "real_%s.jsonl" % c)
        real_md5 = write_pool(real, real_path, relabel_to=None)
        n_wrong = sum(1 for r in real if r["country"] != c)
        print("  real_%s.jsonl: %d records, md5=%s, wrong-country rows=%d"
              % (c, len(real), real_md5, n_wrong))

        raked, rake_res = build_raked_pool(all_recs, c, pool_size, args.seed)
        raked_path = os.path.join(out_dir, "raked_%s.jsonl" % c)
        raked_md5 = write_pool(raked, raked_path, relabel_to=c)
        n_self_donor = sum(1 for r in raked if r["country"] == c)
        print("  raked_%s.jsonl: %d records, md5=%s, iterations=%d, "
              "max_dev_pp=%.5f pp"
              % (c, len(raked), raked_md5, rake_res["iterations"],
                 rake_res["max_dev_pp"]))
        c_ok = (n_self_donor == 0)
        ok = ok and c_ok
        print("  C-c no-self-donor for %s (donor_country == %s count, must be "
              "0): %d -- %s" % (c, c, n_self_donor, "PASS" if c_ok else "FAIL"))

    print("")
    print("P3 pool build: %s" % ("ALL C-c CHECKS PASS" if ok else "C-c FAILED -- DO NOT USE THESE POOLS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
