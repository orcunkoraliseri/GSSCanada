#!/usr/bin/env python
"""
Selftest for `4thJ_step7_chaining.py` (Step 7 work item 7.6, CPU half).

The metrics in that module decide whether open decision 14 has anything to
decide. A metric that is wrong in the same direction for every rule would still
produce a clean-looking ranking, so each one is checked here against a series
whose answer is known by construction.

Runs offline. No GPU, no network, no corpus.
"""

import collections
import importlib
import io
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

C = importlib.import_module("4thJ_step7_chaining")
S = importlib.import_module("4thJ_step7_schedules")

OK = 0
BAD = 0


def check(name, cond, detail=""):
    global OK, BAD
    if cond:
        OK += 1
        print("  ok   %s" % name)
    else:
        BAD += 1
        print("  FAIL %s   %s" % (name, detail))


def close(a, b, tol=1e-9):
    return a is not None and abs(a - b) <= tol


print("=" * 74)
print("4thJ_step7_chaining_selftest")
print("=" * 74)

# --------------------------------------------------------------------------
print("\n[1] correlation, and the constant-series trap")
# --------------------------------------------------------------------------
a = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
b = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
c = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
k = [0.5] * 6
check("identical series correlate at +1", close(C._pearson(a, b), 1.0))
check("mirrored series correlate at -1", close(C._pearson(a, c), -1.0))
check("a CONSTANT series returns None, not 0.0",
      C._pearson(a, k) is None, C._pearson(a, k))
check("... and None is what keeps a flat schedule out of the mean",
      C._pearson(k, k) is None)

# --------------------------------------------------------------------------
print("\n[2] the pre-screen, on series whose answers are known")
# --------------------------------------------------------------------------
# two households, perfectly in phase: aggregate swings 0 -> 1
p = C.prescreen([[0.0, 1.0] * 12, [0.0, 1.0] * 12], n_pairs=20, seed=1)
check("in-phase aggregate peaks at 1.0", close(p["peak_aggregate"], 1.0))
check("in-phase aggregate troughs at 0.0", close(p["trough_aggregate"], 0.0))
check("in-phase annual mean is 0.5", close(p["annual_mean"], 0.5))
check("in-phase max ramp is 1.0", close(p["max_ramp"], 1.0))
check("in-phase pair correlation is +1", close(p["mean_pair_corr"], 1.0))

# two households in antiphase: the AGGREGATE is flat even though each swings
q = C.prescreen([[0.0, 1.0] * 12, [1.0, 0.0] * 12], n_pairs=20, seed=1)
check("antiphase aggregate is FLAT at 0.5", close(q["peak_aggregate"], 0.5)
      and close(q["trough_aggregate"], 0.5))
check("antiphase max ramp is 0", close(q["max_ramp"], 0.0))
check("antiphase pair correlation is -1", close(q["mean_pair_corr"], -1.0))
check("the two cells share an annual mean but not a peak -- which is why "
      "annual mean alone cannot see coincidence",
      close(p["annual_mean"], q["annual_mean"])
      and not close(p["peak_aggregate"], q["peak_aggregate"]))
check("constant pairs are counted, never averaged in",
      C.prescreen([[0.5] * 24, [0.5] * 24], n_pairs=20, seed=1)["n_pairs_constant"] > 0)

# --------------------------------------------------------------------------
print("\n[3] the vocabulary metrics")
# --------------------------------------------------------------------------
cal = S.year_day_types(2011)


def day(codes):
    return {"acts": [(10, c) for c in codes], "flags": [], "prefix": None}


# one person who does exactly the same three things every single day
same = [day(["011", "021", "031"]) for _ in cal]
v = C.vocabulary([same], cal)
check("a person repeating one day has a monthly vocabulary of 3",
      close(v["vocab_month_mean"], 3.0), v["vocab_month_mean"])
check("... and a daily vocabulary of 3", close(v["vocab_day_mean"], 3.0))
check("... and adjacent-day jaccard of 1.0 on same-type days",
      close(v["jaccard_adjacent_same_day_type"], 1.0))
check("... and 1.0 across day types too",
      close(v["jaccard_adjacent_cross_day_type"], 1.0))
check("twelve person-months, one per calendar month",
      v["n_person_months"] == 12, v["n_person_months"])
check("365 person-days", v["n_person_days"] == 365, v["n_person_days"])

# a person whose activities never repeat: monthly vocabulary must grow
distinct = [day(["%03d" % (i % 900)]) for i in range(365)]
v2 = C.vocabulary([distinct], cal)
check("a person who never repeats has a monthly vocabulary near the month "
      "length", v2["vocab_month_mean"] > 28.0, v2["vocab_month_mean"])
check("... and adjacent-day jaccard 0.0",
      close(v2["jaccard_adjacent_same_day_type"], 0.0))
check("the two persons are ordered the way RL21 predicts",
      v2["vocab_month_mean"] > v["vocab_month_mean"])

# `000` must not enter the vocabulary as an activity
withnull = [day(["011", None]) for _ in cal]
v3 = C.vocabulary([withnull], cal)
check("a null ACT is not counted as an activity code",
      close(v3["vocab_day_mean"], 1.0), v3["vocab_day_mean"])

# --------------------------------------------------------------------------
print("\n[4] the spread test, including the degenerate case")
# --------------------------------------------------------------------------
check("spread of a constant list is 0", C.spread([2.0, 2.0, 2.0]) == 0.0)
check("spread is max minus min", C.spread([1.0, 5.0, 3.0]) == 4.0)

# --------------------------------------------------------------------------
print("\n[5] the real-corpus anchor, on a fixture whose answer is known")
# --------------------------------------------------------------------------
tmp = tempfile.mkdtemp(prefix="4j_s7_anchor_")
try:
    path = os.path.join(tmp, "corpus.jsonl")
    rows = [
        # a one-day country
        {"country": "xx", "hid": "1", "pid": "p1", "diary_day": "1",
         "text": "xx,25-44,male,single,employed,weekday|"
                 "1440,011,,at_home,0;<eor>"},
        {"country": "xx", "hid": "2", "pid": "p2", "diary_day": "1",
         "text": "xx,25-44,male,single,employed,weekday|"
                 "720,011,,at_home,0;720,021,,at_home,0;<eor>"},
        # a two-day country, one weekday and one sunday, sharing one code
        {"country": "yy", "hid": "3", "pid": "p3", "diary_day": "1",
         "text": "yy,25-44,male,single,employed,weekday|"
                 "720,011,,at_home,0;720,021,,at_home,0;<eor>"},
        {"country": "yy", "hid": "3", "pid": "p3", "diary_day": "7",
         "text": "yy,25-44,male,single,employed,sunday|"
                 "720,011,,at_home,0;720,031,,at_home,0;<eor>"},
    ]
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    anc = C.corpus_anchor(path)
    check("two countries found", sorted(anc) == ["xx", "yy"], sorted(anc))
    check("xx has two persons, one day each",
          anc["xx"]["n_persons"] == 2 and anc["xx"]["days_per_person"] == {1: 2},
          anc["xx"])
    check("xx reports NO second-day accumulation, because there is none",
          "new_codes_from_second_day_mean" not in anc["xx"])
    check("xx mean codes per day is 1.5", close(anc["xx"]["vocab_day_mean"], 1.5))
    check("yy has one person with two days",
          anc["yy"]["n_persons_with_two_days"] == 1)
    check("yy second day adds exactly one NEW code",
          close(anc["yy"]["new_codes_from_second_day_mean"], 1.0))
    check("yy union over two days is 3", close(anc["yy"]["vocab_two_days_mean"], 3.0))
    check("yy jaccard is 1/3", close(anc["yy"]["jaccard_between_the_two_days_mean"],
                                     1.0 / 3.0))
    check("yy pairs a weekday with a sunday, and says so",
          anc["yy"]["day_type_pairs"] == {"sunday,weekday": 1},
          anc["yy"]["day_type_pairs"])
    check("yy has ZERO same-day-type pairs, which is the whole limitation",
          anc["yy"]["n_pairs_same_day_type"] == 0)
finally:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

# --------------------------------------------------------------------------
print("\n[6] fewer than five seeds is REFUSED")
# --------------------------------------------------------------------------
try:
    C.main(["--gen", ".", "--step2", ".", "--crosswalk", ".", "--corpus", ".",
            "--out", os.devnull, "--seeds", "1,2,3"])
except SystemExit as e:
    msg = str(e)
    check("a four-seed campaign is refused with the pre-registered reason",
          "5" in msg and "error bar" in msg, msg)
except Exception as e:
    check("a four-seed campaign is refused", False, "%s: %s" % (type(e).__name__, e))
else:
    check("a four-seed campaign is refused", False, "DID NOT RAISE")

check("the pre-registered sweep has six points on one axis",
      len(C.RULE_POINTS) == 6, C.RULE_POINTS)
check("... with independent and static as the endpoints",
      C.RULE_POINTS[0] == ("independent", 0.0)
      and C.RULE_POINTS[-1] == ("static", 1.0))
check("the default seed set has at least five", len(C.DEFAULT_SEEDS) >= 5)

print("\n" + "=" * 74)
print("%d ok, %d FAILED" % (OK, BAD))
print("=" * 74)
sys.exit(1 if BAD else 0)
