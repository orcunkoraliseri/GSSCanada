"""
D-S6-1 option (b): re-split 4J_step3_corpus.jsonl by HOUSEHOLD instead of by respondent.

Ruled by the author 2026-08-18. `4thJ_06_transfer.md` specifies the second hold-out as
"a random sample of households"; `4thJ_step3_build.py` split by respondent and flagged
that at its line 20 as an ASSUMPTION. This script makes the corpus match the spec.

WHAT THIS CHANGES:  the value of the `split` field on each record. Nothing else.
WHAT THIS MUST NOT CHANGE:  the `text` of any record, the record count, the record
order, or any of the four key fields. All four are ASSERTED here, not assumed -- if any
of them moves, the script fails and writes nothing.

The selection method deliberately MIRRORS the build's, line for line, so that the only
difference between the old split and the new one is the unit:

    rng = np.random.default_rng(42)
    units = <unique keys, in order of first appearance>
    heldout = units[rng.permutation(len(units))[:round(len(units) * 0.10)]]

    build:      unit = (country, hid, pid)      <- respondent
    this file:  unit = (country, hid)           <- household

A different shuffle procedure would confound "we changed the unit" with "we changed the
draw", and the point of this change is to be able to say exactly what moved.

It also MEASURES the leak that the change removes -- the number of households that had
members on both sides of the old respondent split -- because that number is the whole
justification for D-S6-1 and it belongs in prereg.md rather than in an argument.

Reads   /speed-scratch/o_iseri/4J_step3_corpus.jsonl
Writes  /speed-scratch/o_iseri/4J_step3_corpus.jsonl            (re-labelled, in place)
        /speed-scratch/o_iseri/4J_step3_corpus_respondent_split.jsonl   (the old file, kept)
        /speed-scratch/o_iseri/4J_split_report_household.md
"""

import json
import os
import shutil
import sys
from collections import defaultdict

import numpy as np

CORPUS = "/speed-scratch/o_iseri/4J_step3_corpus.jsonl"
BACKUP = "/speed-scratch/o_iseri/4J_step3_corpus_respondent_split.jsonl"
REPORT = "/speed-scratch/o_iseri/4J_split_report_household.md"

SPLIT_SEED = 42          # identical to 4thJ_step3_build.py
HELDOUT_FRACTION = 0.10  # identical to 4thJ_step3_build.py

EXPECTED_RECORDS = 73254
EXPECTED_DIARIES = {"es": 19140, "it": 38260, "uk": 15854}
EXPECTED_RESPONDENTS = 65334


def fail(msg):
    print()
    print("!" * 78)
    print("FAIL: %s" % msg)
    print("!" * 78)
    sys.exit(1)


def main():
    print("=" * 78)
    print("D-S6-1 (b) -- RE-SPLIT BY HOUSEHOLD")
    print("=" * 78)
    print("reading %s" % CORPUS)

    recs = []
    with open(CORPUS, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception as exc:
                fail("line %d is not JSON: %s" % (lineno, exc))
            for f in ("country", "hid", "pid", "diary_day", "split", "text"):
                if f not in r:
                    fail("line %d is missing field %r" % (lineno, f))
            recs.append(r)

    n = len(recs)
    print("records read: %d" % n)
    if n != EXPECTED_RECORDS:
        fail("expected %d records, read %d -- this is not the corpus this script was written for"
             % (EXPECTED_RECORDS, n))

    # ---- what is on disk right now: the respondent split, and its leak ----
    old_split = [r["split"] for r in recs]
    old_counts = defaultdict(int)
    for s in old_split:
        old_counts[s] += 1
    print()
    print("OLD SPLIT (respondent, as built): %s"
          % dict(sorted(old_counts.items())))

    hh_sides = defaultdict(set)       # (country, hid) -> {"train", "heldout"}
    hh_members = defaultdict(set)     # (country, hid) -> {pid, ...}
    for r, s in zip(recs, old_split):
        key = (r["country"], r["hid"])
        hh_sides[key].add(s)
        hh_members[key].add(r["pid"])

    n_households = len(hh_sides)
    split_households = sorted(k for k, v in hh_sides.items() if len(v) > 1)
    multi_person = sorted(k for k, v in hh_members.items() if len(v) > 1)

    print("households (country, hid): %d" % n_households)
    print("households with >1 respondent: %d" % len(multi_person))
    print()
    print("=" * 78)
    print("THE LEAK D-S6-1 REMOVES, MEASURED BEFORE IT IS REMOVED")
    print("=" * 78)
    print("households straddling the OLD respondent split "
          "(members in BOTH train and heldout): %d" % len(split_households))
    if multi_person:
        print("  = %.2f %% of all households, %.2f %% of multi-respondent households"
              % (100.0 * len(split_households) / n_households,
                 100.0 * len(split_households) / len(multi_person)))
    leak_records = sum(1 for r in recs if (r["country"], r["hid"]) in set(split_households))
    print("records living in a straddling household: %d (%.2f %% of the corpus)"
          % (leak_records, 100.0 * leak_records / n))
    leak_by_country = defaultdict(int)
    for k in split_households:
        leak_by_country[k[0]] += 1
    print("straddling households per country: %s" % dict(sorted(leak_by_country.items())))
    if not split_households:
        print("NOTE: zero straddling households. The respondent split was already "
              "household-clean, so (b) changes the draw but removes no leak. "
              "Report it that way -- do not claim a repair that was not needed.")

    # ---- the new split: same procedure, household unit ----
    print()
    print("=" * 78)
    print("NEW SPLIT (household), same seed and same procedure as the build")
    print("=" * 78)

    seen = set()
    households = []      # order of first appearance, mirroring df.drop_duplicates()
    for r in recs:
        key = (r["country"], r["hid"])
        if key not in seen:
            seen.add(key)
            households.append(key)

    if len(households) != n_households:
        fail("household enumeration disagrees with itself: %d vs %d"
             % (len(households), n_households))

    rng = np.random.default_rng(SPLIT_SEED)
    shuffled_idx = rng.permutation(len(households))
    n_heldout_hh = int(round(len(households) * HELDOUT_FRACTION))
    heldout_hh = set(households[i] for i in shuffled_idx[:n_heldout_hh])

    print("households: %d, heldout fraction=%.2f (seed=%d) -> %d heldout households, %d train"
          % (len(households), HELDOUT_FRACTION, SPLIT_SEED,
             len(heldout_hh), len(households) - len(heldout_hh)))

    for r in recs:
        r["split"] = "heldout" if (r["country"], r["hid"]) in heldout_hh else "train"

    # ---- integrity: this is a re-LABEL, and every other field must be untouched ----
    print()
    print("=" * 78)
    print("INTEGRITY -- a re-label must move nothing but the label")
    print("=" * 78)

    new_hh_sides = defaultdict(set)
    for r in recs:
        new_hh_sides[(r["country"], r["hid"])].add(r["split"])
    straddling_now = [k for k, v in new_hh_sides.items() if len(v) > 1]
    if straddling_now:
        fail("%d households still straddle the new split -- the household split is wrong"
             % len(straddling_now))
    print("SPLIT INTEGRITY: households straddling the new split = 0")

    train_hh = set(k for k, v in new_hh_sides.items() if v == {"train"})
    held_hh = set(k for k, v in new_hh_sides.items() if v == {"heldout"})
    inter = train_hh & held_hh
    print("SPLIT INTEGRITY: train households=%d, heldout households=%d, intersection=%d"
          % (len(train_hh), len(held_hh), len(inter)))
    if inter:
        fail("train and heldout household sets intersect")

    # respondents can no longer straddle either -- a respondent lives in one household
    resp_sides = defaultdict(set)
    for r in recs:
        resp_sides[(r["country"], r["hid"], r["pid"])].add(r["split"])
    if any(len(v) > 1 for v in resp_sides.values()):
        fail("a respondent straddles the new split, which is impossible if the "
             "household split is correct -- the key is wrong")
    print("SPLIT INTEGRITY: respondents straddling the new split = 0 (%d respondents)"
          % len(resp_sides))
    if len(resp_sides) != EXPECTED_RESPONDENTS:
        fail("expected %d respondents, found %d" % (EXPECTED_RESPONDENTS, len(resp_sides)))

    new_counts = defaultdict(int)
    for r in recs:
        new_counts[r["split"]] += 1
    print("records: %s" % dict(sorted(new_counts.items())))
    print("heldout record fraction: %.4f  (the household unit does NOT give exactly 0.10 "
          "of records, and it is not adjusted to -- adjusting it would be fitting the "
          "split to a round number)" % (new_counts["heldout"] / float(n)))

    per_country = defaultdict(lambda: defaultdict(int))
    for r in recs:
        per_country[r["country"]][r["split"]] += 1
    hh_per_country = defaultdict(lambda: defaultdict(int))
    for k, v in new_hh_sides.items():
        hh_per_country[k[0]][list(v)[0]] += 1

    print()
    print("PER COUNTRY (diaries / households)")
    for c in sorted(per_country):
        print("  %s: diaries train=%d heldout=%d (total %d, expected %d) | "
              "households train=%d heldout=%d"
              % (c, per_country[c]["train"], per_country[c]["heldout"],
                 per_country[c]["train"] + per_country[c]["heldout"],
                 EXPECTED_DIARIES.get(c, -1),
                 hh_per_country[c]["train"], hh_per_country[c]["heldout"]))
        tot = per_country[c]["train"] + per_country[c]["heldout"]
        if tot != EXPECTED_DIARIES.get(c):
            fail("country %s has %d diaries, expected %d" % (c, tot, EXPECTED_DIARIES.get(c)))

    # ---- write: back up the old file FIRST, verify it, then overwrite ----
    print()
    print("=" * 78)
    print("WRITING")
    print("=" * 78)

    if os.path.exists(BACKUP):
        fail("%s already exists -- refusing to overwrite a backup. Move it aside and re-run."
             % BACKUP)
    shutil.copyfile(CORPUS, BACKUP)
    bk_size = os.path.getsize(BACKUP)
    src_size = os.path.getsize(CORPUS)
    if bk_size == 0 or bk_size != src_size:
        fail("backup is %d bytes against a source of %d -- refusing to overwrite the corpus"
             % (bk_size, src_size))
    print("backed up the respondent-split corpus -> %s (%d bytes, size-matched)"
          % (BACKUP, bk_size))

    tmp = CORPUS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps({
                "country": r["country"], "hid": r["hid"], "pid": r["pid"],
                "diary_day": r["diary_day"], "split": r["split"], "text": r["text"],
            }) + "\n")
    os.replace(tmp, CORPUS)
    print("wrote %d records -> %s" % (n, CORPUS))

    # ---- re-read from disk and prove the text is byte-identical to the backup ----
    print()
    print("VERIFY FROM DISK -- text must be byte-identical to the backup, record for record")
    n_checked = 0
    n_text_diff = 0
    n_key_diff = 0
    n_label_changed = 0
    with open(BACKUP, "r", encoding="utf-8") as fa, open(CORPUS, "r", encoding="utf-8") as fb:
        for la, lb in zip(fa, fb):
            a = json.loads(la)
            b = json.loads(lb)
            n_checked += 1
            if a["text"] != b["text"]:
                n_text_diff += 1
            if (a["country"], a["hid"], a["pid"], a["diary_day"]) != \
               (b["country"], b["hid"], b["pid"], b["diary_day"]):
                n_key_diff += 1
            if a["split"] != b["split"]:
                n_label_changed += 1
    print("records compared: %d" % n_checked)
    print("records whose TEXT differs: %d   (must be 0)" % n_text_diff)
    print("records whose KEY differs: %d    (must be 0)" % n_key_diff)
    print("records whose LABEL changed: %d  (this is the intended change)" % n_label_changed)
    if n_checked != n:
        fail("re-read %d records against %d written" % (n_checked, n))
    if n_text_diff or n_key_diff:
        fail("the re-split moved something other than the label -- corpus is NOT safe to use")

    # ---- report ----
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("# D-S6-1 (b) -- household re-split of `4J_step3_corpus.jsonl`\n\n")
        fh.write("Ruled by the author 2026-08-18. Unit moved from respondent "
                 "`(country, hid, pid)` to household `(country, hid)`; "
                 "seed %d and fraction %.2f unchanged; selection procedure unchanged.\n\n"
                 % (SPLIT_SEED, HELDOUT_FRACTION))
        fh.write("## The leak this removed, measured before removal\n\n")
        fh.write("* households straddling the old respondent split: **%d** of %d "
                 "(%.2f %%)\n" % (len(split_households), n_households,
                                  100.0 * len(split_households) / n_households))
        fh.write("* multi-respondent households: %d\n" % len(multi_person))
        fh.write("* records living in a straddling household: **%d** (%.2f %% of the corpus)\n"
                 % (leak_records, 100.0 * leak_records / n))
        fh.write("* straddling households per country: %s\n\n"
                 % dict(sorted(leak_by_country.items())))
        fh.write("## The new split\n\n")
        fh.write("* households: **%d** -> %d heldout / %d train\n"
                 % (len(households), len(heldout_hh), len(households) - len(heldout_hh)))
        fh.write("* respondents: %d, none straddling\n" % len(resp_sides))
        fh.write("* diaries: **%d heldout / %d train** of %d "
                 "(heldout record fraction %.4f, NOT adjusted to 0.10)\n\n"
                 % (new_counts["heldout"], new_counts["train"], n,
                    new_counts["heldout"] / float(n)))
        fh.write("| country | diaries train | diaries heldout | households train | households heldout |\n")
        fh.write("|---|---|---|---|---|\n")
        for c in sorted(per_country):
            fh.write("| %s | %d | %d | %d | %d |\n"
                     % (c, per_country[c]["train"], per_country[c]["heldout"],
                        hh_per_country[c]["train"], hh_per_country[c]["heldout"]))
        fh.write("\n## Integrity\n\n")
        fh.write("* records compared against the pre-split backup: %d\n" % n_checked)
        fh.write("* records whose `text` differs: **%d**\n" % n_text_diff)
        fh.write("* records whose key differs: **%d**\n" % n_key_diff)
        fh.write("* records whose `split` label changed: %d\n" % n_label_changed)
        fh.write("* households straddling the new split: **0**; "
                 "respondents straddling: **0**\n\n")
        fh.write("The respondent-split corpus is kept at `%s`.\n" % BACKUP)
    print()
    print("wrote %s" % REPORT)
    print()
    print("=" * 78)
    print("D-S6-1 (b) APPLIED. Text unchanged on %d/%d records; only the split label moved."
          % (n_checked - n_text_diff, n_checked))
    print("=" * 78)


if __name__ == "__main__":
    main()
