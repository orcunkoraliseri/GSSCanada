#!/usr/bin/env python
"""
4J Step 7, work item 7.6 -- THE CHAINING RULE. THE CPU HALF ONLY.

    "Nothing in this plan says how a household's 8,760 hours are assembled from
     generated days"  --  `RL17` Part D, and it is still the gap.

WHAT THIS MODULE DOES AND DOES NOT DO
-------------------------------------
Work item 7.6's definition of done has five items. Two of them are CPU work and
this module does those two:

  item 3  a cheap pre-screen on the assembled 8,760-hour arrays -- aggregate
          coincidence and mean pairwise cross-correlation. The step document
          calls it "a screen, NOT a substitute", because `RL21` claims a shift in
          it "guarantees" a shift in simulated peak, which is an unsupported
          causal claim with an invented threshold.
  item 4  the activity-vocabulary check, computed on the HELD data rather than
          taken from `RL21`.

It does NOT do items 1, 2 or 5, and it does NOT close open decision 14:

  item 2  aggregate coincident peak POWER and heating/cooling ENERGY are
          EnergyPlus outputs. Step 8. Nothing here is a watt.
  G7.18   the 25 % escalation trigger is defined on peak DEMAND. It is therefore
          NOT EVALUATED here, and no number below may be substituted for it.

THE SEED SPREAD IS THE POINT, NOT DECORATION
--------------------------------------------
The validation document pre-registers it: *"if the spread across seeds within a
rule exceeds the spread between rules, the experiment has told us nothing about
chaining, and the deliverable is that finding, not a chosen rule."* So every
metric is computed at >= 5 seeds per rule and the two spreads are printed side by
side, with the verdict written by the numbers rather than by whoever reads them.

`RL21`'s CRITERION ASKS FOR A QUANTITY THE SURVEYS DO NOT CONTAIN
-----------------------------------------------------------------
"count distinct activity codes per synthetic individual per MONTH ... the
realistic value is computed on the held ISTAT data". Measured: ISTAT gives every
respondent exactly ONE diary day, and so does Spain. Only the UK has two, and in
7,897 of 7,920 cases the two are one weekday and one weekend day. **No person in
any of the three surveys has a month of days**, so a monthly vocabulary has no
empirical reference anywhere in the corpus. What the corpus CAN anchor is the
one-day vocabulary and, in the UK alone, the increment a SECOND day adds. Both
are computed here and labelled for what they are.
"""

import argparse
import collections
import importlib
import io
import json
import math
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

S = importlib.import_module("4thJ_step7_schedules")
import decoder as dec
from encoder import load_bit_positions

#: The pre-registered sweep. `independent` and `static` are the endpoints;
#: `habit` is the same code at four interior persistence values. The selftest of
#: the emitter proves rho=0 IS independent and rho=1 IS static, so this is one
#: axis sampled at six points, not three unrelated rules.
RULE_POINTS = (("independent", 0.0), ("habit", 0.25), ("habit", 0.50),
               ("habit", 0.75), ("habit", 0.90), ("static", 1.0))

#: >= 5, pre-registered. "A single realisation per rule is a curve with no error
#: bar, therefore no way to be wrong, therefore no way to fail."
DEFAULT_SEEDS = (11, 22, 33, 44, 55)


def _label(rule, rho):
    return rule if rule != "habit" else "habit_rho%.2f" % rho


# --------------------------------------------------------------------------
# metrics on the assembled year
# --------------------------------------------------------------------------
def _mean(xs):
    xs = list(xs)
    return sum(xs) / float(len(xs)) if xs else float("nan")


def _pearson(a, b):
    n = len(a)
    ma, mb = _mean(a), _mean(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return None                      # a constant series has no correlation
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return cov / math.sqrt(va * vb)


def prescreen(series_by_household, n_pairs=300, seed=0):
    """DoD item 3. Aggregate coincidence and mean pairwise cross-correlation.

    The aggregate is the MEAN household presence at each hour, so it is in
    [0, 1] and is comparable across cells with different household counts.

    🔴 It is an OCCUPANCY coincidence, not a demand coincidence. The 25 %
    escalation trigger in `G7.18` is defined on peak DEMAND and is not evaluated
    by this number.
    """
    n_h = len(series_by_household)
    n_t = len(series_by_household[0])
    agg = [0.0] * n_t
    for s in series_by_household:
        for t in range(n_t):
            agg[t] += s[t]
    agg = [v / n_h for v in agg]
    ramps = [abs(agg[t] - agg[t - 1]) for t in range(1, n_t)]
    ordered = sorted(agg)
    rng = random.Random(seed)
    corrs = []
    n_const = 0
    for _ in range(n_pairs):
        i = rng.randrange(n_h)
        j = rng.randrange(n_h)
        if i == j:
            continue
        c = _pearson(series_by_household[i], series_by_household[j])
        if c is None:
            n_const += 1
        else:
            corrs.append(c)
    return {
        "n_households": n_h,
        "n_timesteps": n_t,
        "annual_mean": _mean(agg),
        "peak_aggregate": max(agg),
        "trough_aggregate": min(agg),
        "p99_aggregate": ordered[int(0.99 * (n_t - 1))],
        "max_ramp": max(ramps),
        "mean_abs_ramp": _mean(ramps),
        "mean_pair_corr": _mean(corrs) if corrs else None,
        "n_pairs_scored": len(corrs),
        "n_pairs_constant": n_const,
    }


def vocabulary(member_years, cal):
    """DoD item 4, on the SIMULATED side.

    `member_years` is `[[day, ...] x 365, ...]`, one list per person.

    Three numbers, and the third is the one that can be compared to real data:

      `vocab_month`   distinct ACT codes per person per calendar month. This is
                      `RL21`'s criterion. It has NO empirical reference -- see
                      the module docstring.
      `vocab_day`     distinct ACT codes per person per day. Directly comparable
                      to the corpus.
      `jaccard_*`     set overlap between a person's activities on two adjacent
                      days, split by whether the two days share a day type.
                      The cross-type number is the one the UK two-day anchor
                      measures.
    """
    month_of = []
    m, d = 1, 1
    import calendar as _cal
    for _ in range(365):
        month_of.append(m)
        d += 1
        if d > _cal.monthrange(2011, m)[1]:
            m += 1
            d = 1
    per_month = []
    per_day = []
    jac_same = []
    jac_cross = []
    for year in member_years:
        sets = []
        for day in year:
            sets.append(set(a for _, a in day["acts"] if a is not None))
        per_day.extend(len(s) for s in sets)
        acc = collections.defaultdict(set)
        for i, s in enumerate(sets):
            acc[month_of[i]] |= s
        per_month.extend(len(v) for v in acc.values())
        for i in range(1, len(sets)):
            a, b = sets[i - 1], sets[i]
            if not (a | b):
                continue
            j = len(a & b) / float(len(a | b))
            (jac_same if cal[i - 1] == cal[i] else jac_cross).append(j)
    return {
        "vocab_month_mean": _mean(per_month),
        "vocab_day_mean": _mean(per_day),
        "jaccard_adjacent_same_day_type": _mean(jac_same),
        "jaccard_adjacent_cross_day_type": _mean(jac_cross),
        "n_person_months": len(per_month),
        "n_person_days": len(per_day),
    }


# --------------------------------------------------------------------------
# the real-data anchor (T4)
# --------------------------------------------------------------------------
def corpus_anchor(corpus_path):
    """The activity-vocabulary reference, computed on the HELD data.

    Returns per country: diaries, persons, the distribution of diary days per
    person, mean distinct ACT codes per day, and -- where two days exist -- the
    increment the second day adds and the day-type pairing.
    """
    per = collections.defaultdict(list)
    for line in io.open(corpus_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        head, body = r["text"].split("|", 1)
        day_type = head.split(",")[5]
        acts = set()
        for ep in body.replace("<eor>", "").split(";"):
            if ep:
                a = ep.split(",")[1]
                if a != "000":
                    acts.add(a)
        per[(r["country"], r["pid"])].append((day_type, acts))

    out = {}
    for country in sorted(set(k[0] for k in per)):
        rows = [(k, v) for k, v in per.items() if k[0] == country]
        days_per_person = collections.Counter(len(v) for _, v in rows)
        per_day = [len(s) for _, v in rows for _, s in v]
        two = [v for _, v in rows if len(v) == 2]
        rec = {
            "n_persons": len(rows),
            "n_diaries": sum(len(v) for _, v in rows),
            "days_per_person": dict(days_per_person),
            "vocab_day_mean": _mean(per_day),
            "n_persons_with_two_days": len(two),
        }
        if two:
            pairs = collections.Counter(tuple(sorted(d for d, _ in v)) for v in two)
            new = [len(v[1][1] - v[0][1]) for v in two]
            union = [len(v[0][1] | v[1][1]) for v in two]
            jac = [len(v[0][1] & v[1][1]) / float(len(v[0][1] | v[1][1]))
                   for v in two if (v[0][1] | v[1][1])]
            same_type = sum(1 for v in two if v[0][0] == v[1][0])
            rec.update({
                "day_type_pairs": dict((",".join(k), n) for k, n in pairs.items()),
                "n_pairs_same_day_type": same_type,
                "new_codes_from_second_day_mean": _mean(new),
                "vocab_two_days_mean": _mean(union),
                "jaccard_between_the_two_days_mean": _mean(jac),
            })
        out[country] = rec
    return out


# --------------------------------------------------------------------------
# the campaign
# --------------------------------------------------------------------------
def run_cell(pools, households, cal, rule, rho, seed, timestep_min):
    rng = random.Random(seed)
    backoff = collections.Counter()
    series = []
    member_years = []
    for hid, members in households:
        md = [S.assemble_person_year(p, cal, rule, rng, pools, backoff, rho)
              for p in members]
        member_years.extend(md)
        series.append(S.household_year(md, timestep_min))
    out = prescreen(series, seed=seed)
    out.update(vocabulary(member_years, cal))
    out["backoff_full_depth_share"] = (
        backoff[len(S.STRATUM_FIELDS)] / float(sum(backoff.values())))
    return out


def spread(values):
    return (max(values) - min(values)) if values else float("nan")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="4J Step 7 item 7.6 -- chaining pre-screen, CPU half")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--years", default="es:2010,uk:2014,it:2013")
    ap.add_argument("--arm", default="constrained")
    ap.add_argument("--leg", type=int, default=4,
                    help="which generation leg the pool comes from (4 rehearsal, 5 reported)")
    ap.add_argument("--households", type=int, default=100)
    ap.add_argument("--timestep", type=int, default=60)
    ap.add_argument("--seeds", default=",".join(str(s) for s in DEFAULT_SEEDS))
    a = ap.parse_args(argv)

    seeds = [int(s) for s in a.seeds.split(",") if s.strip()]
    if len(seeds) < 5:
        raise SystemExit(
            "REFUSED: %d seeds. The validation document pre-registers at least "
            "5 per rule -- 'a single realisation per rule is a curve with no "
            "error bar, therefore no way to be wrong, therefore no way to "
            "fail'." % len(seeds))
    years = dict(kv.split(":") for kv in a.years.split(","))
    bitpos = load_bit_positions(a.crosswalk)

    print("=" * 78)
    print("T4 -- the activity-vocabulary reference, on the REAL corpus")
    print("=" * 78)
    anchor = corpus_anchor(a.corpus)
    for c in sorted(anchor):
        r = anchor[c]
        print("  %s  persons %6d  diaries %6d  days/person %s"
              % (c, r["n_persons"], r["n_diaries"], r["days_per_person"]))
        print("      distinct ACT codes per DAY, mean  %.3f" % r["vocab_day_mean"])
        if r.get("new_codes_from_second_day_mean") is not None:
            print("      persons with two days             %d" % r["n_persons_with_two_days"])
            print("      ... of which SAME day type        %d" % r["n_pairs_same_day_type"])
            print("      day-type pairs                    %s" % r["day_type_pairs"])
            print("      NEW codes added by the 2nd day    %.3f" % r["new_codes_from_second_day_mean"])
            print("      union over the two days           %.3f" % r["vocab_two_days_mean"])
            print("      jaccard between the two days      %.4f" % r["jaccard_between_the_two_days_mean"])
        else:
            print("      NO person has a second day, so no accumulation can be "
                  "measured in this country at all.")

    board = {"anchor": anchor, "cells": {}, "verdicts": {}}
    for fold in a.folds.split(","):
        fold = fold.strip()
        year = int(years[fold])
        cal = S.year_day_types(year)
        pool_path = os.path.join(a.gen, "generated_leg%d_%s_%s.jsonl"
                                 % (a.leg, fold, a.arm))
        pools, pool_meta = S.load_pool(pool_path, a.step2, bitpos)
        hh_rng = random.Random(1)
        households = S.load_households(a.corpus, fold, a.households, hh_rng)
        print("\n" + "=" * 78)
        print("T3 -- fold %s   year %d   %d households   pool %s (%d days)   %s"
              % (fold, year, len(households), pool_meta["pool_file"],
                 pool_meta["n_days"], pool_meta["provenance"]))
        print("=" * 78)
        hdr = ("  %-16s %6s %8s %8s %8s %9s %9s %9s %9s"
               % ("rule", "seed", "annmean", "peak", "maxramp", "paircorr",
                  "vocab/mo", "vocab/day", "jac_same"))
        print(hdr)
        cells = {}
        for rule, rho in RULE_POINTS:
            lab = _label(rule, rho)
            for seed in seeds:
                m = run_cell(pools, households, cal, rule, rho, seed, a.timestep)
                cells[(lab, seed)] = m
                print("  %-16s %6d %8.4f %8.4f %8.4f %9.4f %9.3f %9.3f %9.4f"
                      % (lab, seed, m["annual_mean"], m["peak_aggregate"],
                         m["max_ramp"], m["mean_pair_corr"],
                         m["vocab_month_mean"], m["vocab_day_mean"],
                         m["jaccard_adjacent_same_day_type"]))
        board["cells"][fold] = dict(("%s|%d" % k, v) for k, v in cells.items())

        # ---- the pre-registered spread test -------------------------------
        print("\n  %-28s %12s %12s %12s   %s"
              % ("metric", "seed spread", "rule spread", "ratio", "verdict"))
        verdicts = {}
        for metric in ("annual_mean", "peak_aggregate", "p99_aggregate",
                       "trough_aggregate", "max_ramp", "mean_pair_corr",
                       "vocab_month_mean", "vocab_day_mean",
                       "jaccard_adjacent_same_day_type"):
            per_rule = collections.defaultdict(list)
            for (lab, seed), m in cells.items():
                per_rule[lab].append(m[metric])
            within = max(spread(v) for v in per_rule.values())
            means = [_mean(v) for v in per_rule.values()]
            between = spread(means)
            allv = [v for vs in per_rule.values() for v in vs]
            # 🔴 A metric that never moves is DEGENERATE, not "seed noise
            # dominates". Both spreads are zero, the ratio is 0/0, and reporting
            # it as a failed contrast would put a verdict on a constant.
            degenerate = (within == 0.0 and between == 0.0)
            ratio = float("nan") if degenerate else (
                between / within if within else float("inf"))
            ok = (not degenerate) and between > within
            verdicts[metric] = {
                "max_within_rule_seed_spread": within,
                "between_rule_spread_of_means": between,
                "ratio": ratio,
                "degenerate_constant_value": allv[0] if degenerate else None,
                "rule_effect_exceeds_seed_noise": bool(ok),
                "per_rule_mean": dict((k, _mean(v)) for k, v in per_rule.items()),
            }
            print("  %-28s %12.6f %12.6f %12s   %s"
                  % (metric, within, between,
                     "n/a" if degenerate else "%.2f" % ratio,
                     ("*** DEGENERATE -- constant at %.6f in every cell, so it "
                      "carries no information about chaining" % allv[0])
                     if degenerate else
                     ("rule effect > seed noise" if ok else
                      "*** SEED NOISE DOMINATES -- tells us nothing about chaining")))
        board["verdicts"][fold] = verdicts

    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(board, indent=2, sort_keys=True, default=str))
    print("\nboard -> %s" % a.out)
    print("\n*** G7.18 IS NOT EVALUATED. Its 25 % escalation trigger is defined "
          "on peak DEMAND and on annual heating/cooling ENERGY, both of which "
          "are EnergyPlus outputs. Nothing above is a watt. Open decision 14 "
          "stays OPEN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
