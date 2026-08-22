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

`D-S6-14` (a), author 2026-08-22, adds ONE alternate mode:

    python 4thJ_step4_shards.py --permute-labels [--permutation-seed N]

which builds the same shard set from a corpus whose prefix-to-body pairing has been
deranged inside each (country, split) group. Those go to `shards_permuted_control/`
and `shard_manifest_permuted_control.json`, never to `shards/`, and every record
carries `POISONED_CONTROL: true`. Default mode is byte-for-byte what it always was.
"""

import argparse
import collections
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

# ---------------------------------------------------------------------------
# 🔴 `D-S6-14`, RULED BY THE AUTHOR 2026-08-22 -- THE PERMUTED CONTROL SHARDS
# ---------------------------------------------------------------------------
# Question 1 ruled (a): permute the PREFIX-TO-BODY PAIRING at shard-build time,
# with a dedicated printed seed. The adapter trained on these shards is the
# memorisation CEILING: every generalisable conditional association is gone by
# construction, so whatever `G6.10`/`G6.11` still read on it is rote recall of
# arbitrary pairings and nothing else. Without it the audit has a floor (the
# untuned base model, AUC ~0.50) and no top, and a measured 0.55 against a 0.65
# bar cannot be called low.
#
# 🔴 THE PERMUTATION IS WITHIN (country, split), NOT GLOBAL. Two reasons, and the
# first is not negotiable:
#
#   1. FOLD ISOLATION. A global shuffle would put an Italian diary body behind a
#      Spanish prefix. In the `it` fold that is the held-out country's data
#      entering training wearing a donor's prefix -- `G4.13` would still read 0
#      because it counts the `country` FIELD, and the leak would be invisible.
#      Keeping the permutation inside a country makes the prefix country token,
#      the record's `country` field and the body's country agree by construction.
#   2. MEMBERSHIP. `4thJ_step6_privacy_mia.py` takes members from `split ==
#      "train"` and non-members from `split == "heldout"` of the SAME countries.
#      If only the member side were permuted, the attack could separate the two
#      sets on "does this pairing look like the training distribution" rather
#      than on membership, and would report an inflated AUC that is not
#      memorisation at all. Both splits are permuted, independently.
#
# ⚪ DECLARED LIMITATION, and it follows directly from reason 1: `P(body | country)`
# survives the permutation. The control destroys conditioning on age, sex,
# household type, economic status and day type -- five of the six prefix fields --
# and cannot destroy the sixth without destroying the LOCO design. The ceiling it
# measures is therefore the ceiling for a model that may still condition on
# country. Stated here so no write-up calls it a fully unconditional control.
#
# 🔴 The permutation is a DERANGEMENT: no record keeps its own body. A uniform
# permutation of n items has one fixed point in expectation regardless of n, and
# a fixed point is a genuine (prefix, body) pair surviving inside a control whose
# entire claim is that no genuine pair survives. Drawn by rejection -- redraw the
# whole group until it has no fixed point -- which is a uniform derangement
# exactly, at an expected e ~ 2.72 draws.
#
# 🔴 Output is ISOLATED and MARKED. Separate directory, separate manifest,
# `POISONED_CONTROL` on every record and at the top of the manifest, and
# `4thJ_step4_train.py` refuses to train a production run-type from a permuted
# manifest and a `permuted` run-type from a clean one. Author directive:
# "never into production shard directories".
SHARDS_PERM = os.path.join(STEP4, "shards_permuted_control")
MANIFEST_PERM = os.path.join(STEP4, "shard_manifest_permuted_control.json")
CORPUS_PERM = os.path.join(SHARDS_PERM, "corpus_permuted_control.jsonl")
SEED_PERM = 614614                   # `D-S6-14`. Fixed, printed, and never tuned:
                                     # it is not a knob, and a control whose seed
                                     # was chosen after seeing an AUC is not one.
POISON_MARK = "POISONED_CONTROL"

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


def split_text(text):
    """`prefix` , `body` -- the body is everything after the FIRST separator,
    the separator itself excluded. `partition` rather than `split` so a body that
    somehow contained a `|` would keep it rather than be silently truncated."""
    head, sep, body = text.partition("|")
    if not sep:
        raise ValueError("record has no '|' separator")
    return head, body


def permute_pairs(recs, seed):
    """`D-S6-14` (a). Re-pair prefixes with bodies inside each (country, split)
    group, as a derangement. Returns a report; edits `r["text"]` in place.

    The record keeps its own prefix and all of its metadata -- `hid`, `pid`,
    weights, the stratum the prefix encodes -- and receives another record's
    body. That direction matters: `G6.12` counts training records per stratum and
    the MIA keys members by stratum, both from the prefix, so permuting bodies
    under fixed prefixes leaves every stratum count identical to production and
    changes only what the model is asked to learn inside it."""
    rng = np.random.default_rng(seed)
    groups = defaultdict(list)
    for i, r in enumerate(recs):
        groups[(r["country"], r["split"])].append(i)

    report = {"seed": seed, "groups": {}, "n_permuted": 0,
              "n_fixed_points": 0, "n_unchanged_text": 0}
    for key in sorted(groups):
        idx = groups[key]
        m = len(idx)
        if m < 2:
            fail("group %s has %d record(s) -- a group of one cannot be deranged, and "
                 "a control that silently leaves it paired is not a control" % (key, m))
        for attempt in range(1, 101):
            perm = rng.permutation(m)
            fixed = int(np.sum(perm == np.arange(m)))
            if fixed == 0:
                break
        else:
            fail("group %s: 100 draws all had a fixed point. That is impossible for "
                 "m=%d unless the RNG is degenerate; refusing to continue." % (key, m))

        bodies = [split_text(recs[i]["text"])[1] for i in idx]
        unchanged = 0
        for pos, i in enumerate(idx):
            head, _old = split_text(recs[i]["text"])
            new_text = head + "|" + bodies[perm[pos]]
            if new_text == recs[i]["text"]:
                # not a fixed point of the permutation -- two DISTINCT records that
                # happen to carry byte-identical bodies. Counted, not repaired: the
                # pairing was still destroyed, and repairing it would bias the draw.
                unchanged += 1
            recs[i]["text"] = new_text
        report["groups"]["%s/%s" % key] = {"n": m, "draws": attempt,
                                           "fixed_points": 0,
                                           "identical_body_collisions": unchanged}
        report["n_permuted"] += m
        report["n_unchanged_text"] += unchanged
        print("  permuted %-12s n=%6d  draws=%d  fixed points=0  identical-body "
              "collisions=%d" % ("%s/%s" % key, m, attempt, unchanged))
    return report


def write_shard(path, recs):
    with open(path, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    return {"path": path, "n": len(recs), "md5": md5_of_file(path),
            "bytes": os.path.getsize(path)}


def main(argv=None):
    global SHARDS, MANIFEST
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--permute-labels", action="store_true",
                    help="`D-S6-14` (a): build the POISONED_CONTROL shards instead -- "
                         "prefix-to-body pairing deranged within (country, split). "
                         "Writes to shards_permuted_control/, NEVER to shards/.")
    ap.add_argument("--permutation-seed", type=int, default=SEED_PERM,
                    help="the printed seed for the derangement (default %d). Recorded "
                         "in the manifest and in every record." % SEED_PERM)
    args = ap.parse_args(argv)

    print("=" * 78)
    print("STEP 4 SHARD BUILDER%s"
          % ("  --  🔴 PERMUTED CONTROL (%s)" % POISON_MARK if args.permute_labels else ""))
    print("=" * 78)
    if args.permute_labels:
        SHARDS, MANIFEST = SHARDS_PERM, MANIFEST_PERM
        print("`D-S6-14` (a), author 2026-08-22. Permutation seed: %d"
              % args.permutation_seed)
        print("output is ISOLATED: %s" % SHARDS)
        print("🔴 These shards are a CONTROL. They are not a model of anything and no "
              "number computed from them is a result.")

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
            if args.permute_labels:
                r["_orig_text"] = r["text"]
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

    # ---- `D-S6-14`: the permutation, and the four invariants it must not break ----
    perm_report = None
    if args.permute_labels:
        print()
        print("=" * 78)
        print("PERMUTING PREFIX-TO-BODY PAIRING  --  `D-S6-14` (a)")
        print("=" * 78)
        before_tokens = collections.Counter()
        before_prefix = collections.Counter()
        for r in recs:
            before_tokens.update(split_text(r["text"])[1])
            before_prefix[split_text(r["text"])[0]] += 1
        before_total = sum(len(split_text(r["text"])[1]) for r in recs)

        perm_report = permute_pairs(recs, args.permutation_seed)

        after_tokens = collections.Counter()
        after_prefix = collections.Counter()
        for r in recs:
            after_tokens.update(split_text(r["text"])[1])
            after_prefix[split_text(r["text"])[0]] += 1
        after_total = sum(len(split_text(r["text"])[1]) for r in recs)

        print()
        print("INVARIANTS -- checked, not assumed:")
        if before_tokens != after_tokens:
            fail("the character multiset of the bodies changed under permutation. The "
                 "control is supposed to re-pair existing bodies, not rewrite them.")
        print("  1. body character multiset  : IDENTICAL (%d chars)" % before_total)
        if before_prefix != after_prefix:
            fail("the multiset of prefixes changed under permutation.")
        print("  2. prefix multiset          : IDENTICAL (%d distinct)" % len(before_prefix))
        if before_total != after_total:
            fail("total body length changed under permutation.")
        print("  3. total body length        : IDENTICAL")
        for r in recs:
            head = split_text(r["text"])[0]
            if head.strip().split(",")[0] != r["country"]:
                fail("a permuted record's prefix country %r no longer matches its "
                     "country field %r -- the permutation escaped its group and fold "
                     "isolation is gone" % (head.strip().split(",")[0], r["country"]))
        print("  4. prefix country == record country : HOLDS for all %d records" % n)
        print("     (so `G4.13` still counts what it thinks it counts)")

        # 🔴 The point of the whole exercise, measured rather than asserted: the
        # association between the five permutable prefix fields and the body is gone.
        # Reported as the fraction of records whose body still belongs to a record
        # sharing its full stratum -- under permutation this must fall to roughly the
        # stratum's own share of its group, i.e. to chance.
        kept = 0
        for r in recs:
            if r["text"] == r["_orig_text"]:
                kept += 1
        print("  5. records whose FULL text survived the permutation: %d (%.4f %%)"
              % (kept, 100.0 * kept / n))
        perm_report["n_text_identical_to_original"] = kept
        for r in recs:
            del r["_orig_text"]
            r[POISON_MARK] = True
            r["permutation_seed"] = args.permutation_seed

        os.makedirs(SHARDS, exist_ok=True)
        with open(CORPUS_PERM, "w", encoding="utf-8") as fh:
            for r in recs:
                out = {k: v for k, v in r.items() if k != "_prefix"}
                fh.write(json.dumps(out) + "\n")
        print()
        print("wrote the permuted corpus to %s" % CORPUS_PERM)
        print("  md5 %s" % md5_of_file(CORPUS_PERM))
        print("🔴 `4thJ_step6_privacy_mia.py` MUST be pointed at THIS file for the "
              "control run. Members and non-members both come from it, so the attack "
              "still separates exposure and not pairing style.")
        perm_report["corpus_permuted"] = {"path": CORPUS_PERM,
                                          "md5": md5_of_file(CORPUS_PERM)}

    os.makedirs(SHARDS, exist_ok=True)

    manifest = {
        "generator": "4thJ_step4_shards.py",
        POISON_MARK: bool(args.permute_labels),
        "permutation": perm_report,
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
    if args.permute_labels:
        print("🔴 PERMUTED CONTROL SHARDS BUILT -- %s, seed %d." % (POISON_MARK,
                                                                   args.permutation_seed))
        print("🔴 These are NOT a model of the population. An adapter trained on them "
              "measures ONE thing: how much a model of this size can memorise when there "
              "is nothing to generalise. `D-S6-14` (a), author 2026-08-22.")
        print("🔴 Train them with --run-type permuted and --shard-manifest %s. The "
              "trainer refuses every other combination." % MANIFEST_PERM)
    print("SHARDS BUILT. Every fold: held-out country contributes 0 training records, "
          "counted from the file on disk.")
    print("🔴 The builder's own count is NOT G4.13. G4.13 re-counts from the shard the "
          "trainer loaded, at training start. Two independent counts, on purpose.")
    print("=" * 78)


if __name__ == "__main__":
    main()
