# -*- coding: utf-8 -*-
"""`G6.7` part 2 — score the fictional-country control.

  usage: python 4thJ_step6_g67_score.py --fold es --manifest JSON --gen DIR
                                        --corpus FILE --harmonised PARQUET
                                        --step2 DIR --leg 4 --out JSON

---------------------------------------------------------------------------
🔴 THE TWO CLAUSES, AND HOW EACH IS OPERATIONALISED (`D-S6-11` item 3)
---------------------------------------------------------------------------

The spec: *"the generated time budget must track the perturbation with slope
>= 0.8, and the residual against any real country's profile must not be the
smallest for a country whose token was not used."*

**CLAUSE 1 -- SLOPE, IN TWO PARTS SINCE `D-S6-13`.** Pooled OLS of generated on
expected across all (level, aggregate) points, each aggregate CENTRED on its own mean
first. Without centring the fit is dominated by `AC0`, which is 600+ min/day in every
cell and would drag any slope towards 1.0 whatever the model did with the small
aggregates. Per-aggregate slopes are reported beside the pooled one.

🔴 `D-S6-13`, ruled (c) + (d) on 2026-08-22, after `FINDING 91`. The pooled fit ran
over all six aggregates and **could not tell an attenuated model from an indifferent
one**. Two facts force the change and both are measured, not argued:

  * **Budget closure.** The six aggregates sum to 1439.2-1439.6 of 1440 minutes at
    every level in every fold, so the deviations are constrained to sum to zero. Any
    amplitude the model fails to deliver on the active channels is FORCED into the
    residual bucket `AC4-8` with the opposite sign: its slope is **-1.259** in `es`
    (R2 0.843) and **-1.023** in `uk` (R2 0.732). Pooling then averages an
    attenuated-positive set against a forced-negative one and lands near zero. A model
    with uniform gain `g < 1` does NOT score pooled ~ `g`; it scores far below it, by
    an amount that depends on which bucket absorbs the residual. `AC4-8` is a
    DEPENDENT quantity, not a sixth independent measurement, and it is excluded by
    name from the fit -- it is still reported.
  * **The pooled number said the opposite of the truth.** Board 0.0358 / 0.2437 /
    0.1899 against a 0.80 bar reads as "the model ignores the conditioning vector".
    But `AC2` is the highest-R2 aggregate of six in two folds of three (`es` 0.845,
    `uk` **0.981**, `it` **0.984**) while delivering only 18 / 57 / 13 % of the
    requested amplitude. The model orders the five levels almost perfectly and then
    under-delivers. That is an AMPLITUDE DEFICIT, which a 7B model at three epochs can
    plausibly close; it is not a comprehension failure, which it could not.

So clause 1 now has two parts, and a batch must clear both:

  1. **STEERING** -- on the targeted channel `AC2`, R2 >= 0.80 AND slope > 0. This is
     what `ignore_prefix` cannot fake: that injection scores R2 0.0000 by
     construction, against baseline `it`'s 0.1899 pooled. It is the discrimination the
     single pooled statistic lacked.
  2. **AMPLITUDE** -- pooled slope >= 0.80 over the FIVE independent channels
     (`AC0`, `AC1_TR`, `AC2`, `AC3`, `AC9A`), with `AC4-8` excluded.

**CLAUSE 2 -- STEREOTYPE.** Under a fictional token NO real country's token was
used, so the literal reading has no referent. The operative question the clause
asks is whether the model followed the conditioning vector or fell back on a
national pattern, and that is directly measurable:

    MAE(generated, EXPECTED at this level)  <  MAE(generated, country c's own
                                                  overall profile)  for every c

If a real country's national profile explains the output better than the
conditioning vector the model was actually given, the model is reciting a
country. 🔴 This is an operationalisation, not the spec's words, and it is
raised as a decision rather than adopted silently.

**Every real-country profile is built from the CORPUS, not from Eurostat.** The
levels span all eight age bands and Eurostat's only all-ages row is `TOTAL`,
whose population base is unstated -- which is exactly what `D-S6-8` item 2 ruled
out of any verdict.
"""

import argparse
import collections
import importlib
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

L1 = importlib.import_module("4thJ_step6_level1")
import decoder as dec
from encoder import load_bit_positions

SLOPE_MIN = 0.8

# `D-S6-13` (c) + (d), ruled 2026-08-22. All three numbers are pre-registered here and
# none is tuned to an observed result: `SLOPE_MIN` is unchanged, `STEER_R2_MIN` reuses
# the same 0.80, and the excluded bucket is named rather than chosen by size.
RESIDUAL_AGGREGATE = "AC4-8"                 # the closure balancer -- reported, not fitted
ACTIVE_AGGREGATES = [a for a in L1.AGGREGATES if a != RESIDUAL_AGGREGATE]
STEER_AGGREGATE = "AC2"                      # the channel the lambda tilt targets
STEER_R2_MIN = 0.80


def ols(x, y):
    n = len(x)
    if n < 3:
        raise ValueError("a slope over %d points is not a slope" % n)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    if sxx <= 0:
        raise ValueError("the predictor has zero variance -- the perturbation "
                         "did not perturb (see the amplitude guard in the manifest)")
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    slope = sxy / sxx
    syy = sum((v - my) ** 2 for v in y)
    r2 = (sxy * sxy) / (sxx * syy) if syy > 0 else float("nan")
    return slope, my - slope * mx, r2


def national_profiles(corpus, harmonised, bitpos):
    """Each real country's OWN overall level-1 budget, weighted. All ages."""
    import pyarrow.parquet as pq
    df = pq.read_table(harmonised, columns=["country", "pid", "diary_day",
                                            "weight_dia_cal"]).to_pandas()
    df["country"] = df["country"].str.lower()
    df = df.drop_duplicates(subset=["country", "pid", "diary_day"])
    W = {(r.country, r.pid, r.diary_day): float(r.weight_dia_cal)
         for r in df.itertuples()}
    rows = collections.defaultdict(lambda: ([], []))
    for line in open(corpus, encoding="utf-8"):
        r = json.loads(line)
        w = W.get((r["country"], r["pid"], r["diary_day"]))
        if w is None or w != w:
            continue
        rows[r["country"]][0].append(dec.decode_record(r["text"], bitpos))
        rows[r["country"]][1].append(w)
    return dict((c, L1.budget(recs, ws)) for c, (recs, ws) in rows.items())


PERTURBATIONS = ["null", "ignore_prefix", "recite_country", "flatten"]


def perturb(name, generated, expected, national, fold):
    """Injections act on the GENERATED budgets, level by level.

    `ignore_prefix` is the defect `G6.7` exists to catch: a model that emits the
    same day whatever it is conditioned on. `recite_country` is the other one:
    a model reciting a donor country regardless of the vector.
    """
    g = [dict(x) for x in generated]
    if name == "null":
        return g
    if name == "ignore_prefix":
        mean = dict((a, sum(x[a] for x in g) / float(len(g))) for a in L1.AGGREGATES)
        return [dict(mean) for _ in g]
    if name == "recite_country":
        donor = [c for c in sorted(national) if c != fold][0]
        return [dict((a, national[donor][a]) for a in L1.AGGREGATES) for _ in g]
    if name == "flatten":
        # follows the perturbation at HALF strength -- the slope band, not the sign
        mean = dict((a, sum(x[a] for x in g) / float(len(g))) for a in L1.AGGREGATES)
        return [dict((a, mean[a] + 0.5 * (x[a] - mean[a])) for a in L1.AGGREGATES)
                for x in g]
    raise ValueError(name)


def score(generated, expected, national, fold):
    xs, ys = [], []
    xs_all, ys_all = [], []
    per_agg = {}
    for a in L1.AGGREGATES:
        x = [e[a] for e in expected]
        y = [g[a] for g in generated]
        mx, my = sum(x) / len(x), sum(y) / len(y)
        xs_all.extend(v - mx for v in x)
        ys_all.extend(v - my for v in y)
        # 🔴 `D-S6-13`: the residual bucket is still MEASURED and still REPORTED -- its
        # near `-1` slope is the evidence for the exclusion, so hiding it would remove
        # the reason for the rule. It is only kept out of the fitted arrays.
        if a in ACTIVE_AGGREGATES:
            xs.extend(v - mx for v in x)
            ys.extend(v - my for v in y)
        try:
            s, _b, r2 = ols(x, y)
            per_agg[a] = {"slope": s, "r2": r2, "fitted": a in ACTIVE_AGGREGATES,
                          "expected_range": max(x) - min(x),
                          "generated_range": max(y) - min(y)}
        except ValueError as e:
            per_agg[a] = {"slope": None, "fitted": a in ACTIVE_AGGREGATES,
                          "reason": str(e)}
    slope, _b, r2 = ols(xs, ys)
    # kept for the record and for the paper: the six-aggregate number this gate used to
    # report, so the correction can be shown rather than asserted.
    slope_all, _b2, r2_all = ols(xs_all, ys_all)

    # 🟢 `D-S6-11` item 3 CONFIRMED, 2026-08-22: the anti-stereotype clause is
    # MAE(gen, EXP(lambda)) < MAE(gen, profile_c) for EVERY real country c, and the
    # `profile_c` are the corpus-weighted REAL national budgets from
    # `national_profiles()` -- not the published tables. It asks whether the model
    # conditioned on the synthetic vector or recited a memorised national day.
    rows = []
    clause2 = True
    for i, g in enumerate(generated):
        d_exp = L1.mae(g, expected[i])
        d_nat = dict((c, L1.mae(g, national[c])) for c in national)
        worst = min(d_nat, key=lambda c: d_nat[c])
        ok = all(d_exp < v for v in d_nat.values())
        clause2 = clause2 and ok
        rows.append({"level": i, "mae_vs_expected": d_exp,
                     "mae_vs_national": d_nat, "nearest_country": worst,
                     "follows_the_vector": ok})
    # 🔴 `D-S6-13` (d): the STEERING part of clause 1. `ignore_prefix` scores R2 0.0000
    # on this by construction; an attenuated model scores 0.98. It is the only part of
    # the gate that separates the two.
    steer = per_agg.get(STEER_AGGREGATE) or {}
    steer_ok = (steer.get("slope") is not None and steer["slope"] > 0.0
                and steer.get("r2") == steer.get("r2")        # not NaN
                and steer.get("r2", 0.0) >= STEER_R2_MIN)

    reasons = []
    if not steer_ok:
        reasons.append("steering: %s slope %s R2 %s -- needs slope > 0 and R2 >= %.2f. "
                       "The model is not tracking the channel the lambda tilt targets."
                       % (STEER_AGGREGATE,
                          "n/a" if steer.get("slope") is None else "%+.4f" % steer["slope"],
                          "n/a" if steer.get("r2") is None else "%.4f" % steer["r2"],
                          STEER_R2_MIN))
    if slope < SLOPE_MIN:
        reasons.append("amplitude: slope %.4f over the %d active aggregates is below "
                       "%.2f (the residual bucket %s is excluded, D-S6-13)"
                       % (slope, len(ACTIVE_AGGREGATES), SLOPE_MIN, RESIDUAL_AGGREGATE))
    if not clause2:
        bad = [r["level"] for r in rows if not r["follows_the_vector"]]
        reasons.append("at level(s) %s a real country's national profile explains "
                       "the output better than the conditioning vector does"
                       % ", ".join(str(b) for b in bad))
    return dict(passes=not reasons, reasons=reasons, pooled_slope=slope,
                pooled_r2=r2, slope_min=SLOPE_MIN, per_aggregate=per_agg,
                active_aggregates=ACTIVE_AGGREGATES,
                excluded_aggregate=RESIDUAL_AGGREGATE,
                steering={"aggregate": STEER_AGGREGATE, "r2_min": STEER_R2_MIN,
                          "slope": steer.get("slope"), "r2": steer.get("r2"),
                          "passes": steer_ok},
                pooled_slope_all_six=slope_all, pooled_r2_all_six=r2_all,
                levels=rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=("es", "uk", "it"))
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--gen", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--harmonised", required=True)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    man = json.load(open(a.manifest, encoding="utf-8"))
    if not man.get("amplitude_guard", {}).get("passes"):
        print("NOT RUN -- the amplitude guard did not pass. %s"
              % man.get("amplitude_guard", {}).get("note", ""))
        return 2
    bitpos = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))

    print("=" * 78)
    print("G6.7 -- fictional-country control, fold %s, leg %d, token %s"
          % (a.fold, a.leg, man["token"]))
    print("=" * 78)
    if a.leg == 4:
        print("🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    expected, generated, missing = [], [], []
    for d in man["levels_detail"]:
        p = os.path.join(a.gen, "generated_leg%d_%s_g67t%02d.jsonl"
                         % (a.leg, a.fold, d["level"]))
        if not os.path.exists(p):
            missing.append(p)
            continue
        rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        recs = [dec.decode_record(r["text"], bitpos) for r in rows]
        generated.append(L1.budget(recs, None))
        expected.append(d["expected_budget"])
    if missing:
        print("NOT RUN -- %d level batch(es) missing, first: %s"
              % (len(missing), missing[0]))
        print("A slope fitted over the levels that happen to exist is not the "
              "gate. Generate them all.")
        return 2

    national = national_profiles(a.corpus, a.harmonised, bitpos)
    base = score(generated, expected, national, a.fold)
    st = base["steering"]
    print("clause 1a steering   %s slope %s  R2 %s (need > 0 and >= %.2f)  -> %s"
          % (st["aggregate"],
             "n/a" if st["slope"] is None else "%+.4f" % st["slope"],
             "n/a" if st["r2"] is None else "%.4f" % st["r2"],
             STEER_R2_MIN, "PASS" if st["passes"] else "FAIL"))
    print("clause 1b amplitude  slope %.4f over %d active aggregates (need >= %.2f)  "
          "R2 %.4f  -> %s"
          % (base["pooled_slope"], len(ACTIVE_AGGREGATES), SLOPE_MIN,
             base["pooled_r2"], "PASS" if base["pooled_slope"] >= SLOPE_MIN else "FAIL"))
    print("           for the record, the OLD six-aggregate fit: slope %.4f  R2 %.4f "
          "-- the difference is budget closure, not the model (D-S6-13)"
          % (base["pooled_slope_all_six"], base["pooled_r2_all_six"]))
    for agg, v in sorted(base["per_aggregate"].items()):
        mark = "" if v.get("fitted") else "   <- EXCLUDED from the fit (closure balancer)"
        if v.get("slope") is None:
            print("  %-8s not fitted: %s%s" % (agg, v["reason"], mark))
        else:
            print("  %-8s slope %+7.3f  R2 %.3f  expected range %6.1f  "
                  "generated range %6.1f%s"
                  % (agg, v["slope"], v["r2"], v["expected_range"],
                     v["generated_range"], mark))
    for r in base["levels"]:
        print("  level %d  MAE vs vector %6.2f  vs %s  -> %s"
              % (r["level"], r["mae_vs_expected"],
                 " ".join("%s %6.2f" % (c, v)
                          for c, v in sorted(r["mae_vs_national"].items())),
                 "follows the vector" if r["follows_the_vector"]
                 else "🔴 recites %s" % r["nearest_country"]))
    for r in base["reasons"]:
        print("  - %s" % r)

    print("\n" + "=" * 78)
    print("PERTURBATIONS -- a gate that has never been seen falling is not a gate")
    print("=" * 78)
    pert = {}
    for name in PERTURBATIONS:
        g = perturb(name, generated, expected, national, a.fold)
        r = score(g, expected, national, a.fold)
        fell = base["passes"] and not r["passes"]
        pert[name] = {"passes": r["passes"], "pooled_slope": r["pooled_slope"],
                      "steering": r["steering"], "fell": fell, "reasons": r["reasons"]}
        print("  %-16s slope %+7.4f  %s R2 %s  %-4s%s"
              % (name, r["pooled_slope"], STEER_AGGREGATE,
                 "  n/a" if r["steering"]["r2"] is None else "%.3f" % r["steering"]["r2"],
                 "PASS" if r["passes"] else "FAIL",
                 "   [FELL]" if fell else ""))
    hit = [n for n, v in pert.items() if v["fell"]]
    noop = [n for n, v in pert.items() if n != "null" and not v["fell"]]
    cov = {"seen_failing": hit or "🔴 NEVER SEEN FAILING (or already FAILING at "
                                  "baseline)",
           "no_op_perturbations": noop, "passes": bool(hit) and not noop}
    print("\ncoverage clause: %s" % ("PASS" if cov["passes"] else "🔴 FAIL"))

    out = {"fold": a.fold, "leg": a.leg, "token": man["token"],
           "manifest": a.manifest, "G6_7": base, "perturbations": pert,
           "coverage_clause": cov,
           "national_profiles": national}
    if a.leg == 4:
        out["provenance"] = "LEG-4 PILOT -- NOT REPORTABLE"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
