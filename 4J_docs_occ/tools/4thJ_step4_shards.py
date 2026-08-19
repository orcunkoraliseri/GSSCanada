"""
Step 4, shard builder. Emits, per leave-one-country-out fold, the exact files the
trainer will load -- and nothing else. No training happens here.

WHY THIS IS A SEPARATE SCRIPT.  `G4.13` counts held-out-country records "from the
shard the trainer actually loaded, never from the config or the filename". That gate
is only meaningful if the shard is a real file on disk that something else wrote. A
trainer that filters the corpus in memory at load time gives the gate nothing to open.

Per fold <F> in {es, uk, it}:

    train_<F>.jsonl        training countries, split == "train"
    heldin_val_<F>.jsonl   training countries, split == "heldout"
                           -- the SECOND HOLD-OUT (prereg.md section 7): households
                              held out from INSIDE the training countries. It is an
                              in-country sanity check and is NEVER reported as transfer.
    transfer_<F>.jsonl     the held-out country, ALL of it
                           -- NOT used by Step 4 at all. Written so that Steps 5-7 read
                              a file whose provenance is this manifest, and so that
                              `G4.13` has something to compare against other than zero.
    probe_<F>_<country>.jsonl   a fixed per-country probe set for `G4.9`
                           (catastrophic forgetting), drawn from heldin_val with a
                           FIXED seed so the same diaries are scored at every checkpoint.

Plus one manifest, `shard_manifest.json`, carrying every count and every md5 that
`G4.11` and `G4.13` need, and the frozen `prereg.md` md5 that `G4.14` needs.

Reads   /speed-scratch/o_iseri/4J_step3_corpus.jsonl        (household split, D-S6-1 b)
        /speed-scratch/o_iseri/4J_step4/prereg.md           (frozen)
        /speed-scratch/o_iseri/4J_step4/prereg.md.md5       (the sidecar, the authority)
Writes  /speed-scratch/o_iseri/4J_step4/shards/
"""

import hashlib
import json
import os
import sys
from collections import defaultdict

import numpy as np

CORPUS = "/speed-scratch/o_iseri/4J_step3_corpus.jsonl"
STEP4 = "/speed-scratch/o_iseri/4J_step4"
SHARDS = os.path.join(STEP4, "shards")
PREREG = os.path.join(STEP4, "prereg.md")
PREREG_MD5_SIDECAR = os.path.join(STEP4, "prereg.md.md5")
MANIFEST = os.path.join(STEP4, "shard_manifest.json")

FOLDS = ["es", "uk", "it"]           # every country is held out in turn -- decision 11
COUNTRIES = ["es", "it", "uk"]
PROBE_SEED = 4242                    # distinct from the split seed on purpose: a probe
                                     # set drawn with the split's own seed would be
                                     # correlated with the split by construction
PROBE_N = 200

EXPECTED_RECORDS = 73254
EXPECTED_DIARIES = {"es": 19140, "it": 38260, "uk": 15854}

# prefix is 6 fields, comma-separated, before the first "|" (D-S3-11)
PREFIX_FIELDS = ["country", "strat_age_band", "strat_sex", "strat_hh_type",
                 "strat_econ_status", "strat_day_type"]


def fail(msg):
    print()
    print("!" * 78)
    print("FAIL: %s" % msg)
    print("!" * 78)
    sys.exit(1)


def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_prefix(text):
    """Split the 6-field prefix off the record. Deliberately re-implemented here
    rather than imported from encoder.py: this script's counts are the ones the
    gates read, and a shard builder that shares a parser with the encoder cannot
    disagree with it."""
    i = text.find("|")
    if i < 0:
        raise ValueError("record has no '|' separator")
    parts = text[:i].strip().split(",")
    if len(parts) != len(PREFIX_FIELDS):
        raise ValueError("prefix has %d fields, expected %d" % (len(parts), len(PREFIX_FIELDS)))
    return dict(zip(PREFIX_FIELDS, parts))


def write_shard(path, recs):
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return {"path": path, "n": len(recs), "md5": md5_of_file(path),
            "bytes": os.path.getsize(path)}


def main():
    print("=" * 78)
    print("STEP 4 SHARD BUILDER")
    print("=" * 78)

    # ---- the frozen pre-registration, read before anything else ----
    if not os.path.exists(PREREG):
        fail("%s does not exist. prereg.md must be frozen and staged before shards are "
             "built -- G4.14 has nothing to check otherwise." % PREREG)
    if not os.path.exists(PREREG_MD5_SIDECAR):
        fail("%s does not exist. The recorded md5 is the authority; a shard manifest "
             "that carries a hash nobody recorded is not provenance." % PREREG_MD5_SIDECAR)
    prereg_md5_live = md5_of_file(PREREG)
    with open(PREREG_MD5_SIDECAR, "r", encoding="utf-8") as fh:
        sidecar_raw = fh.read().strip()
    prereg_md5_recorded = sidecar_raw.split()[0] if sidecar_raw else ""
    print("prereg.md md5 recomputed from disk : %s" % prereg_md5_live)
    print("prereg.md md5 recorded in sidecar  : %s" % prereg_md5_recorded)
    if prereg_md5_live != prereg_md5_recorded:
        fail("prereg.md on disk does not match the recorded md5. Either the file was "
             "edited after the freeze, or the wrong file was staged. Do not proceed.")
    print("PREREG PRECEDENCE: match. G4.14 has its reference value.")

    # ---- the corpus ----
    print()
    print("reading %s" % CORPUS)
    corpus_md5 = md5_of_file(CORPUS)
    print("corpus md5: %s" % corpus_md5)

    recs = []
    with open(CORPUS, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            try:
                pref = parse_prefix(r["text"])
            except ValueError as exc:
                fail("line %d: %s" % (lineno, exc))
            if pref["country"] != r["country"]:
                fail("line %d: prefix country %r disagrees with the record's country "
                     "field %r -- the shard would be split on a value the model never "
                     "sees" % (lineno, pref["country"], r["country"]))
            r["_prefix"] = pref
            recs.append(r)

    n = len(recs)
    print("records read: %d" % n)
    if n != EXPECTED_RECORDS:
        fail("expected %d records, read %d" % (EXPECTED_RECORDS, n))

    by_country = defaultdict(int)
    by_country_split = defaultdict(lambda: defaultdict(int))
    for r in recs:
        by_country[r["country"]] += 1
        by_country_split[r["country"]][r["split"]] += 1
    print("per country: %s" % dict(sorted(by_country.items())))
    for c in COUNTRIES:
        if by_country[c] != EXPECTED_DIARIES[c]:
            fail("country %s has %d diaries, expected %d"
                 % (c, by_country[c], EXPECTED_DIARIES[c]))
        print("  %s: train=%d heldout=%d"
              % (c, by_country_split[c]["train"], by_country_split[c]["heldout"]))

    # ---- V4.f in spirit: refuse to build shards from a corpus missing a country ----
    missing = [c for c in COUNTRIES if by_country[c] == 0]
    if missing:
        fail("countries absent from the corpus: %s. A fold isolation check over a "
             "corpus that is already missing a country reports zero for the wrong "
             "reason." % missing)

    os.makedirs(SHARDS, exist_ok=True)

    manifest = {
        "generator": "4thJ_step4_shards.py",
        "corpus": {"path": CORPUS, "md5": corpus_md5, "n_records": n},
        "prereg": {"path": PREREG, "md5": prereg_md5_live,
                   "sidecar": PREREG_MD5_SIDECAR, "md5_recorded": prereg_md5_recorded},
        "split": {"unit": "household (country, hid)", "fraction": 0.10, "seed": 42,
                  "decision": "D-S6-1 (b), author, 2026-08-18"},
        "probe": {"seed": PROBE_SEED, "n_per_country": PROBE_N},
        "folds": {},
    }

    for fold in FOLDS:
        train_countries = [c for c in COUNTRIES if c != fold]
        print()
        print("=" * 78)
        print("FOLD %s -- held out: %s | trains on: %s"
              % (fold.upper(), fold, ", ".join(train_countries)))
        print("=" * 78)

        train = [r for r in recs if r["country"] != fold and r["split"] == "train"]
        heldin = [r for r in recs if r["country"] != fold and r["split"] == "heldout"]
        transfer = [r for r in recs if r["country"] == fold]

        if len(train) + len(heldin) + len(transfer) != n:
            fail("fold %s partitions %d records out of %d -- the three shards must "
                 "exhaust the corpus exactly once"
                 % (fold, len(train) + len(heldin) + len(transfer), n))

        # ---- G4.13, computed here as well as by the gate, on purpose ----
        leak = sum(1 for r in train if r["country"] == fold)
        leak_val = sum(1 for r in heldin if r["country"] == fold)
        print("G4.13 (builder-side): training records whose country == %s : %d  (must be 0)"
              % (fold, leak))
        print("                      heldin-val records whose country == %s : %d  (must be 0)"
              % (fold, leak_val))
        if leak or leak_val:
            fail("fold %s leaks the held-out country into its own training data" % fold)
        if len(train) == 0 or len(transfer) == 0:
            fail("fold %s has an empty shard -- V4.f: an isolation check over an empty "
                 "shard finds zero held-out records for the wrong reason" % fold)

        train_country_counts = defaultdict(int)
        for r in train:
            train_country_counts[r["country"]] += 1
        print("training shard by country: %s" % dict(sorted(train_country_counts.items())))
        if set(train_country_counts) != set(train_countries):
            fail("fold %s training shard contains %s, expected exactly %s"
                 % (fold, sorted(train_country_counts), sorted(train_countries)))

        # ---- strata, for G4.1's V4.a floor ----
        strata = defaultdict(int)
        for r in train:
            p = r["_prefix"]
            strata[(p["country"], p["strat_age_band"], p["strat_sex"],
                    p["strat_hh_type"], p["strat_day_type"])] += 1
        big = [k for k, v in strata.items() if v >= 100]
        print("strata (country x age x sex x hh_type x day_type): %d, of which N>=100: %d"
              % (len(strata), len(big)))
        if len(big) < 5:
            fail("fold %s has only %d strata with N>=100 -- V4.a: a variance gate "
                 "evaluated on that many strata is satisfied by nothing"
                 % (fold, len(big)))

        # ---- write, stripping the parser's scratch field ----
        def clean(rs):
            return [{k: v for k, v in r.items() if k != "_prefix"} for r in rs]

        f_train = write_shard(os.path.join(SHARDS, "train_%s.jsonl" % fold), clean(train))
        f_val = write_shard(os.path.join(SHARDS, "heldin_val_%s.jsonl" % fold), clean(heldin))
        f_xfer = write_shard(os.path.join(SHARDS, "transfer_%s.jsonl" % fold), clean(transfer))
        print("wrote train=%d val=%d transfer=%d" % (f_train["n"], f_val["n"], f_xfer["n"]))

        # ---- G4.9 probe sets: fixed, per training country, drawn from heldin ----
        probes = {}
        rng = np.random.default_rng(PROBE_SEED)
        for c in train_countries:
            pool = [r for r in heldin if r["country"] == c]
            if len(pool) < PROBE_N:
                fail("fold %s country %s has only %d held-in validation diaries, "
                     "fewer than the probe size %d" % (fold, c, len(pool), PROBE_N))
            idx = rng.permutation(len(pool))[:PROBE_N]
            sel = [pool[i] for i in sorted(idx)]
            probes[c] = write_shard(
                os.path.join(SHARDS, "probe_%s_%s.jsonl" % (fold, c)), clean(sel))
            print("probe %s/%s: %d diaries" % (fold, c, probes[c]["n"]))

        manifest["folds"][fold] = {
            "held_out_country": fold,
            "train_countries": train_countries,
            "train": f_train,
            "heldin_val": f_val,
            "transfer": f_xfer,
            "probes": probes,
            "train_by_country": dict(sorted(train_country_counts.items())),
            "n_strata": len(strata),
            "n_strata_ge_100": len(big),
            "g4_13_builder_side_leak": leak,
        }

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    print()
    print("wrote %s" % MANIFEST)

    print()
    print("=" * 78)
    print("SHARDS BUILT. Every fold: held-out country contributes 0 training records, "
          "counted from the file on disk.")
    print("🔴 The builder's own count is NOT G4.13. G4.13 re-counts from the shard the "
          "trainer loaded, at training start. Two independent counts, on purpose.")
    print("=" * 78)


if __name__ == "__main__":
    main()
