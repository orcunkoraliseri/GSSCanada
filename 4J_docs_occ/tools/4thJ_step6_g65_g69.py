# -*- coding: utf-8 -*-
"""Step 6 — `G6.5` (the frozen FAIL criteria) and `G6.9` (nearest-neighbour
discrimination), both on the level-1 time budget.

  usage: python 4thJ_step6_g65_g69.py --gen DIR --leg 4 --step2 DIR
                                      --eurostat DIR --g61 JSON --g64 JSON
                                      --out JSON [--folds es,uk,it]

---------------------------------------------------------------------------
🔴 READING 1 — `G6.5` INVENTS NOTHING. It is an AND over three frozen criteria.
---------------------------------------------------------------------------

`prereg.md` freezes `G6.5` as: the claim FAILS if **any** of

    1. MAE >= the raked-donor null            -- computed by `G6.1`, read here
    2. MAPE > 20 %                             -- computed by `G6.4`, read here
    3. the sign of the country's divergence
       from the European mean is INVERTED      -- computed HERE, nowhere else

Criteria 1 and 2 are read out of the two artefacts that already produce them, by
file, so that `G6.5` cannot disagree with `G6.1` or `G6.4` about a number they
share. Only criterion 3, the **sign arm**, is new code. That is deliberate: the
val doc's own perturbation table says the sign arm exists *separately* precisely
because a 25 % shift in one category moves `G6.4` and the MAPE arm while an
inverted divergence moves the sign arm and NOT `G6.4`.

---------------------------------------------------------------------------
🔴 READING 2 — WHAT "THE EUROPEAN MEAN" IS, AND WHY IT HAD TO BE BUILT
---------------------------------------------------------------------------

**Eurostat publishes no EU aggregate for `tus_00age`.** Probed 2026-08-22: the
table's `geo` dimension carries **22 countries and no `EU27`, no `EU28`, no
`EA`** (AT BE BG DE EE EL ES FI FR HU IT LT LU LV NL NO PL RO RS SI TR UK). The
European mean is therefore CONSTRUCTED, and the construction is a choice:

  * 🟢 IMPLEMENTED: the **unweighted mean over every HETUS country with a complete
    level-1 profile in that age band**, from `tus_00age_ALLGEO_2010_TIME_SP_T.json`
    (md5 `86eeb1b290519d25ab134731e3a813d2`), the fold country included.
    Self-inclusion attenuates a divergence by at most 1/n with n ~ 20, which is
    below the rounding floor of the published `h:mm` strings.
  * NOT population-weighted. Weighting by population would make the mean a
    Germany-and-Turkey mean; the quantity the claim is about is a mean over
    NATIONAL DAILY PATTERNS, one country one vote.
  * NOT restricted to the two donor countries. A three-country mean would make
    "European" mean "the other two", and the sign of a divergence from a mean of
    two is a coin toss.

🔴 This basis is a CHOICE and it is not in `prereg.md`, which names the quantity
and not its construction. It is raised as a decision, not defaulted silently.

---------------------------------------------------------------------------
🔴 READING 3 — THE SIGN ARM ONLY SCORES DIVERGENCES THE TABLES ACTUALLY ASSERT
---------------------------------------------------------------------------

A country whose published `AC2` sits one minute above the European mean has no
sign to invert: the published value is `h:mm` and rounds to the minute, so the
divergence is inside its own rounding floor. An aggregate is scored only when the
PUBLISHED divergence exceeds `SIGN_FLOOR_MIN` minutes/day. Aggregates below the
floor are reported as `not_scored`, and **not scored is not a pass** — they are
counted and named in the artefact.

---------------------------------------------------------------------------
🔴 READING 4 — `G6.9` NEEDS A MARGIN, AND THE MARGIN IS NOT FREE
---------------------------------------------------------------------------

`G6.9` requires the held-out country's generated profile to be closer to its own
published tables than to any other country's *"by a margin exceeding the between-
country spread"*. `spread` is implemented as the **mean pairwise MAE between the
published profiles of the countries compared**, in the same band. So a fold whose
three published profiles are nearly identical demands a nearly-zero margin, and a
fold where they are far apart demands a large one — which is the only reading
under which the criterion is not trivially satisfiable by a bad model.

🔴 The comparison set is the **three in-scope countries**, not all 22. Adding the
other 19 would let a model be nearest to Norway and still "pass" the parts of the
claim that matter; the question `G6.9` exists to answer is whether the model
mapped the held-out country onto one of the two it was TRAINED on.
"""

import argparse
import collections
import importlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

L1 = importlib.import_module("4thJ_step6_level1")
G64 = importlib.import_module("4thJ_step6_g64_run")
import decoder as dec
from encoder import load_bit_positions

MIN_RECORDS = 20
SIGN_FLOOR_MIN = 2.0        # minutes/day; below this the published divergence is noise.
                            # 🟢 D-S6-10 item 2, CONFIRMED 2026-08-22.
# 🟢 D-S6-10 item 1 (a), ruled 2026-08-22: the DIMENSIONLESS relative-margin bar
# for `G6.9`. Perfect model 1.0, equidistant 0.0, bar at the natural midpoint.
G69_REL_MARGIN_MIN = 0.5
MAPE_MAX_G65 = 20.0         # 🔴 prereg §6 criterion 2, frozen. NOT the 15 % of `G6.4`.
ALLGEO = "tus_00age_ALLGEO_2010_TIME_SP_T.json"
SCOPE = ("es", "uk", "it")


class Blocked(Exception):
    pass


def profile_from_allgeo(path, geo, age, wave="2010", unit="TIME_SP", sex="T"):
    """One country's level-1 profile out of the all-geography table.

    🔴 `AC9A` is the SUM OF ITS CHILDREN here too (`D-S6-8` item 1). Two modules
    reading the same table under two different `AC9A` rules would be the
    country-dependent basis `FINDING 53` exists to forbid.
    """
    get, idx = L1._jsonstat(path)
    G = geo.upper()
    if G not in idx["geo"]:
        raise Blocked("%s is not in %s" % (G, os.path.basename(path)))
    kw = dict(freq="A", unit=unit, sex=sex, age=age, geo=G, time=wave)
    kids = [get(acl00=a, **kw) for a in L1.AC9A_CHILDREN]
    if any(v is None for v in kids):
        raise Blocked("%s/%s: AC9A children incomplete" % (G, age))
    out = {}
    for a in L1.AGGREGATES:
        v = sum(kids) if a == "AC9A" else get(acl00=a, **kw)
        if v is None:
            raise Blocked("%s/%s: %s is absent" % (G, age, a))
        out[a] = v
    return out


def european_mean(path, age, wave="2010"):
    """Unweighted mean over every country with a COMPLETE profile in this band."""
    get, idx = L1._jsonstat(path)
    used, skipped = [], {}
    acc = collections.Counter()
    for g in sorted(idx["geo"]):
        try:
            p = profile_from_allgeo(path, g, age, wave)
        except Blocked as e:
            skipped[g] = str(e)
            continue
        used.append(g)
        for a in L1.AGGREGATES:
            acc[a] += p[a]
    if len(used) < 5:
        raise Blocked("only %d countries have a complete %s profile; a European "
                      "mean over %d is not a European mean" % (len(used), age, len(used)))
    mean = {a: acc[a] / float(len(used)) for a in L1.AGGREGATES}
    mean["_countries"] = used
    mean["_n_countries"] = len(used)
    mean["_skipped"] = skipped
    return mean


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------
def gate_g6_5_sign(model, pub, euro, floor=SIGN_FLOOR_MIN):
    """Criterion 3 alone: is the sign of the country's divergence inverted?"""
    rows, inverted, not_scored = [], [], []
    for a in L1.AGGREGATES:
        dp = pub[a] - euro[a]
        dm = model[a] - euro[a]
        if abs(dp) < floor:
            not_scored.append(a)
            rows.append(dict(aggregate=a, published_div=dp, model_div=dm,
                             scored=False,
                             reason="published divergence %.2f is inside the %.1f "
                                    "min/day floor" % (dp, floor)))
            continue
        bad = (dp > 0) != (dm > 0)
        if bad:
            inverted.append(a)
        rows.append(dict(aggregate=a, published_div=dp, model_div=dm, scored=True,
                         inverted=bad))
    return dict(passes=not inverted, inverted=inverted, not_scored=not_scored,
                n_scored=len(L1.AGGREGATES) - len(not_scored), floor_min=floor,
                rows=rows)


def gate_g6_5(fold, band, mae, null_mae, mape, sign):
    """🔴 The frozen AND. Any one criterion fails the claim for this cell."""
    reasons = []
    if mae is None or null_mae is None:
        reasons.append("criterion 1 NOT EVALUABLE: no MAE or no null MAE on file")
    elif mae >= null_mae:
        reasons.append("criterion 1: MAE %.2f >= raked-donor null %.2f" % (mae, null_mae))
    if mape is None:
        reasons.append("criterion 2 NOT EVALUABLE: no MAPE on file")
    elif mape > MAPE_MAX_G65:
        reasons.append("criterion 2: MAPE %.2f %% > %.1f %%" % (mape, MAPE_MAX_G65))
    if not sign["passes"]:
        reasons.append("criterion 3: divergence sign INVERTED on %s"
                       % ", ".join(sign["inverted"]))
    return dict(fold=fold, band=band, passes=not reasons, reasons=reasons,
                mae=mae, null_mae=null_mae, mape=mape, mape_max=MAPE_MAX_G65,
                sign=sign)


def gate_g6_9(model, pubs, own, rel_min=G69_REL_MARGIN_MIN):
    """Nearest-neighbour discrimination over the three in-scope countries.

    🟢 `D-S6-10` item 1, ruled 2026-08-22, option (a). The margin clause is a
    DIMENSIONLESS RELATIVE margin:

            (MAE_runner - MAE_own) / MAE(own_pub, runner_pub)  >  0.5

    🔴 It replaces the original absolute clause `margin > mean pairwise spread`,
    which `FINDING 88` proved **unsatisfiable by a perfect model**: the numerator is
    ONE pairwise distance and the old bar was the MEAN of three, so a model sitting
    exactly on its own published table failed 7 of 9 corpus cells. The new form is
    scale-free and self-normalising against the pair actually in contention:

        perfect model   -> MAE_own = 0, ratio = 1.0
        equidistant     -> ratio = 0.0
        bar at 0.5      -> the natural midpoint, and the point at which the model is
                           closer to its own table than to the runner-up by half the
                           distance that separates the two published tables

    The denominator is the published-vs-published distance for THIS pair, not the
    three-country average: the question is whether the model discriminates between
    the two candidates it could plausibly be confused between.
    """
    d = {c: L1.mae(model, pubs[c]) for c in pubs}
    order = sorted(d, key=lambda c: d[c])
    nearest = order[0]
    runner = order[1] if order[0] == own else order[0]
    # 🔴 the runner-up is the nearest country that is NOT `own`, even when the model
    # already lands on the wrong country. Reading `order[1]` unconditionally would,
    # in exactly that case, measure the gap to the SECOND wrong country and could
    # report a healthy margin for a model that had just misidentified itself.
    if runner == own:
        runner = order[1]
    cs = sorted(pubs)
    pairs = dict(("%s-%s" % (cs[i], cs[j]), L1.mae(pubs[cs[i]], pubs[cs[j]]))
                 for i in range(len(cs)) for j in range(i + 1, len(cs)))
    spread = sum(pairs.values()) / float(len(pairs))
    key = "%s-%s" % tuple(sorted((own, runner)))
    denom = pairs[key]
    margin = d[runner] - d[own]
    rel = None if denom <= 0 else margin / denom
    reasons = []
    if nearest != own:
        reasons.append("nearest published profile is %s (MAE %.2f) not %s (%.2f)"
                       % (nearest, d[nearest], own, d[own]))
    if denom <= 0:
        reasons.append("NOT SCORED: the published %s and %s profiles are identical, "
                       "so the relative margin has no denominator. NOT SCORED is not "
                       "a pass." % (own, runner))
    elif rel <= rel_min:
        reasons.append("relative margin %.4f over the runner-up %s does not exceed "
                       "%.2f (absolute margin %.2f, published %s distance %.2f)"
                       % (rel, runner, rel_min, margin, key, denom))
    return dict(passes=not reasons, reasons=reasons, mae_by_country=d,
                nearest=nearest, own=own, runner_up=runner, margin=margin,
                relative_margin=rel, relative_margin_min=rel_min,
                published_pair=key, published_pair_distance=denom,
                between_country_spread=spread,
                spread_basis_note="`between_country_spread` is REPORTED ONLY. It was "
                                  "the pre-D-S6-10 bar and is kept so every reading "
                                  "before 2026-08-22 can be re-derived; it is NOT in "
                                  "the verdict.",
                pairwise=pairs)


# ---------------------------------------------------------------------------
def read_g61(path):
    """null MAE per (fold, band), out of `G6.1`'s own artefact. 🔴 Read by FILE,
    never recomputed: two modules that recompute the same bar can disagree about
    it, and the one a reader would believe is whichever printed last."""
    if not path or not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for fold, fo in (d.get("folds") or {}).items():
        for band, b in ((fo.get("bands")) or {}).items():
            if isinstance(b, dict) and b.get("null_mae") is not None:
                out[(fold, band)] = float(b["null_mae"])
    return out


def read_g64(path):
    """MAE and MAPE per fold per band, out of `G6.4`'s own artefact."""
    if not path or not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for fold, fo in (d.get("folds") or {}).items():
        for band, b in (fo.get("bands") or {}).items():
            if isinstance(b, dict) and not b.get("blocked"):
                out[(fold, band)] = (b.get("mae"), b.get("mape"))
    return out


# ---------------------------------------------------------------------------
# 🔴 THE PERTURBATION BATTERY. The val doc's own table, implemented.
#
#   "Shift the generated time budget by 25 % on one category"  -> G6.4, G6.5 MAPE
#                                                                 arm; NOT G6.9
#   "Invert the sign of the country's divergence"               -> G6.5 SIGN arm;
#                                                                 NOT G6.4
#   "Score the held-out country against its neighbour's tables" -> G6.9; NOT G6.4
#
# The middle one is the reason the sign arm is a separate criterion at all, so it
# is not enough that it fells `G6.5` -- it must fell `G6.5` WITHOUT the MAPE arm
# having fallen first. That is checked, not assumed.
# ---------------------------------------------------------------------------
PERTURBATIONS = ["null", "shift25", "invert_sign", "neighbour_tables"]


def perturb(name, model, pubs, own, euro):
    m = dict(model)
    p = dict((k, dict(v)) for k, v in pubs.items())
    o = own
    if name == "null":
        pass
    elif name == "shift25":
        # one category only, +25 %, mass returned to AC0 so the day still sums.
        d = m["AC3"] * 0.25
        m["AC3"] += d
        m["AC0"] -= d
    elif name == "invert_sign":
        # 🔴 reflect the MODEL through the European mean on every scored aggregate.
        # Distances change hardly at all -- the reflection is a rigid motion about
        # `euro` -- but every divergence sign flips.
        for a in L1.AGGREGATES:
            m[a] = 2.0 * euro[a] - m[a]
    elif name == "neighbour_tables":
        # the held-out country is scored against a DONOR's published tables.
        o = [c for c in sorted(p) if c != own][0]
    else:
        raise ValueError("unknown perturbation %s" % name)
    return m, p, o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen")
    ap.add_argument("--corpus", help="the CALIBRATION arm: the real harmonised "
                    "corpus, weighted. Not optional in practice -- both gates FAIL "
                    "9/9 on the Leg-4 pilot, and a gate already failing cannot be "
                    "SEEN FAILING under a perturbation. The corpus arm is the only "
                    "passing baseline that exists.")
    ap.add_argument("--harmonised", help="parquet carrying weight_dia_cal")
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--eurostat", required=True)
    ap.add_argument("--g61")
    ap.add_argument("--g64")
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--wave", default="2010")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    allgeo = os.path.join(a.eurostat, ALLGEO)
    if not os.path.exists(allgeo):
        print("NOT RUN -- no all-geography table at %s. The European mean cannot "
              "be constructed and `G6.5` criterion 3 is NOT EVALUABLE." % allgeo)
        return 2

    if not (a.gen or a.corpus):
        ap.error("one of --gen or --corpus is required")
    if a.corpus and not a.harmonised:
        ap.error("--corpus needs --harmonised for weight_dia_cal (FINDING 53)")
    arm = "generated" if a.gen else "corpus"

    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))
    nulls = read_g61(a.g61)
    g64 = read_g64(a.g64)

    print("=" * 78)
    print("G6.5 (frozen FAIL criteria) and G6.9 (nearest neighbour), leg %d" % a.leg)
    print("=" * 78)
    print("criterion 1 MAE >= raked-donor null   <- %s (%d cells)"
          % (os.path.basename(a.g61 or "MISSING"), len(nulls)))
    print("criterion 2 MAPE > %.0f %%              <- %s (%d cells)"
          % (MAPE_MAX_G65, os.path.basename(a.g64 or "MISSING"), len(g64)))
    print("criterion 3 divergence sign           <- computed here")
    print("arm: %s" % arm.upper())
    if arm == "generated" and a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    out = {"leg": a.leg, "wave": a.wave, "arm": arm,
           "european_mean_basis": "unweighted mean over every HETUS country with a "
                                  "complete level-1 profile in the band; NOT "
                                  "population-weighted; the fold country included",
           "allgeo_table": os.path.basename(allgeo),
           "sign_floor_min": SIGN_FLOOR_MIN, "folds": {}}
    if arm == "generated" and a.leg == 4:
        out["provenance"] = "LEG-4 PILOT -- NOT REPORTABLE"

    board = collections.Counter()
    fell = collections.defaultdict(set)
    baseline = {}
    for fold in a.folds.split(","):
        if arm == "generated":
            p = os.path.join(a.gen,
                             "generated_leg%d_%s_constrained.jsonl" % (a.leg, fold))
            if not os.path.exists(p):
                print("\n%s: NO BATCH at %s -- NOT SCORED, and NOT SCORED "
                      "is not a pass" % (fold, p))
                out["folds"][fold] = {"blocked": True, "reason": "no batch at %s" % p}
                continue
            rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
            weights = None
            dropped = 0
        else:
            rows, weights, dropped = G64.load_corpus(a.corpus, a.harmonised, fold)
            p = a.corpus
        if dropped:
            print("\n%s: %d records dropped for a null weight_dia_cal"
                  % (fold, dropped))
        by = collections.defaultdict(lambda: ([], []))
        for i, r in enumerate(rows):
            d = dec.decode_record(r["text"], bp)
            b = L1.AGE_BAND_MAP.get(r.get("strat_age_band")
                                    or d["prefix"]["strat_age_band"])
            if b:
                by[b][0].append(d)
                by[b][1].append(None if weights is None else weights[i])
        fo = {"n": len(rows), "source": p, "bands": {}}
        print("\n%s  %d records" % (fold, len(rows)))
        for band in L1.SCOREABLE_BANDS:
            recs, ws = by.get(band, ([], []))
            if len(recs) < MIN_RECORDS:
                print("  %-8s n=%4d  NOT SCORED (< %d records)"
                      % (band, len(recs), MIN_RECORDS))
                fo["bands"][band] = {"blocked": True, "n": len(recs)}
                continue
            model = L1.budget(recs, None if weights is None else ws)
            try:
                euro = european_mean(allgeo, band, a.wave)
                pubs = dict((c, profile_from_allgeo(allgeo, c, band, a.wave))
                            for c in SCOPE)
            except Blocked as e:
                print("  %-8s BLOCKED -- %s" % (band, e))
                fo["bands"][band] = {"blocked": True, "reason": str(e)}
                continue
            mae, mape = g64.get((fold, band), (None, None))
            sign = gate_g6_5_sign(model, pubs[fold], euro)
            g5 = gate_g6_5(fold, band, mae, nulls.get((fold, band)), mape, sign)
            g9 = gate_g6_9(model, pubs, fold)
            baseline[(fold, band)] = (model, pubs, euro, g5, g9)
            board["G6_5_" + ("PASS" if g5["passes"] else "FAIL")] += 1
            board["G6_9_" + ("PASS" if g9["passes"] else "FAIL")] += 1
            fo["bands"][band] = {"blocked": False, "n": len(recs),
                                 "model_budget": model,
                                 "european_mean": dict(
                                     (k, v) for k, v in euro.items()
                                     if not k.startswith("_skipped")),
                                 "G6_5": g5, "G6_9": g9}
            print("  %-8s n=%4d  G6.5 %-4s  G6.9 %-4s  nearest=%s margin=%.2f "
                  "spread=%.2f  sign: %d scored, %d inverted%s"
                  % (band, len(recs), "PASS" if g5["passes"] else "FAIL",
                     "PASS" if g9["passes"] else "FAIL", g9["nearest"],
                     g9["margin"], g9["between_country_spread"],
                     sign["n_scored"], len(sign["inverted"]),
                     ("  [" + ",".join(sign["inverted"]) + "]") if sign["inverted"] else ""))
            for r in g5["reasons"]:
                print("           G6.5 <- %s" % r)
            for r in g9["reasons"]:
                print("           G6.9 <- %s" % r)
        out["folds"][fold] = fo
    out["board"] = dict(board)

    # ---- 🔴 THE PERTURBATION BATTERY ----
    print("\n" + "=" * 78)
    print("PERTURBATIONS -- a gate that has never been seen falling is not a gate")
    print("=" * 78)
    pert = {}
    if not baseline:
        print("  NO SCORED CELL -- nothing to perturb. The battery did NOT run.")
    for name in PERTURBATIONS:
        rec = {"cells": {}, "fell_G6_5": [], "fell_G6_9": [],
               "fell_G6_5_sign_arm_only": []}
        for (fold, band), (model, pubs, euro, b5, b9) in sorted(baseline.items()):
            m, p, own = perturb(name, model, pubs, fold, euro)
            mae, mape = g64.get((fold, band), (None, None))
            sign = gate_g6_5_sign(m, p[fold], euro)
            g5 = gate_g6_5(fold, band, mae, nulls.get((fold, band)), mape, sign)
            g9 = gate_g6_9(m, p, own)
            key = "%s/%s" % (fold, band)
            rec["cells"][key] = {"G6_5": g5["passes"], "G6_9": g9["passes"],
                                 "sign_inverted": sign["inverted"],
                                 "nearest": g9["nearest"], "margin": g9["margin"]}
            if b5["passes"] and not g5["passes"]:
                rec["fell_G6_5"].append(key)
            if b9["passes"] and not g9["passes"]:
                rec["fell_G6_9"].append(key)
            # 🔴 the sign arm ALONE: the cell's other two criteria unchanged from
            # baseline, and only criterion 3 newly failing.
            if (not sign["passes"] and b5["sign"]["passes"]
                    and len(g5["reasons"]) == len(b5["reasons"]) + 1):
                rec["fell_G6_5_sign_arm_only"].append(key)
        pert[name] = rec
        print("  %-18s G6.5 fell in %2d cells (%2d by the SIGN ARM ALONE)   "
              "G6.9 fell in %2d"
              % (name, len(rec["fell_G6_5"]), len(rec["fell_G6_5_sign_arm_only"]),
                 len(rec["fell_G6_9"])))
    out["perturbations"] = pert

    # ---- the coverage clause ----
    seen = {}
    for g in ("G6_5", "G6_9"):
        hit = [n for n, v in pert.items() if v["fell_" + g]]
        seen[g] = hit if hit else "🔴 NEVER SEEN FAILING (or already FAILING at baseline)"
    sign_only = [n for n, v in pert.items() if v["fell_G6_5_sign_arm_only"]]
    seen["G6_5_sign_arm_alone"] = sign_only if sign_only else (
        "🔴 the SIGN ARM was never the reason -- it is not an independent criterion "
        "unless it can fell G6.5 on its own")
    noop = [n for n, v in pert.items()
            if n != "null" and not v["fell_G6_5"] and not v["fell_G6_9"]]
    out["coverage_clause"] = dict(
        seen_failing=seen, no_op_perturbations=noop,
        passes=(not noop and all(isinstance(v, list) and v for v in seen.values())))
    print("\ncoverage clause: %s"
          % ("PASS" if out["coverage_clause"]["passes"] else "🔴 FAIL"))
    for k, v in seen.items():
        print("  %-22s <- %s" % (k, v if isinstance(v, str) else ", ".join(v)))
    if noop:
        print("  🔴 NO-OP PERTURBATIONS (felled nothing): %s" % ", ".join(noop))
    print("\nboard: %s" % dict(board))

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
