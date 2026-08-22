# -*- coding: utf-8 -*-
"""`G6.6` -- regression on held-IN countries. The forgetting gate, generation side.

  usage: python 4thJ_step6_g66_heldin.py --gen DIR --leg 4 --step2 DIR
                                         --eurostat DIR --g64 JSON --out JSON

`G4.9` already covers forgetting on the LOSS side: per-country held-in probe loss at
the final checkpoint within +5 % of its own best during training. `G6.6` is the
GENERATION side of the same worry, and the two are not interchangeable -- a model can
hold its probe loss and still generate a degraded day.

WHAT IS SCORED
--------------
Each country is a DONOR in exactly two folds and HELD OUT in one. That asymmetry is
free evidence and this gate is built on it:

    fold `es`  ->  generate at `uk` prefixes and at `it` prefixes
    fold `uk`  ->  generate at `es` prefixes and at `it` prefixes
    fold `it`  ->  generate at `es` prefixes and at `uk` prefixes

Six (fold, donor) batches. Each is scored with `G6.4`'s own machinery -- level-1 time
budget against the DONOR's published tables -- so the numbers are commensurable with
the held-out numbers by construction and not by assertion.

THE TWO CLAUSES
---------------
  1. ABSOLUTE. The donor country's MAPE must clear `G6.4`'s bar (15.0 %). A model that
     cannot reproduce a country it was TRAINED on has no standing to be read on a
     country it was not.

  2. PAIRED, and this is the forgetting clause. For donor `D` in fold `F`, compare
     `MAPE(F, D)` -- `D` held IN -- against `MAPE(D, D)` -- the same country scored in
     the fold that holds it OUT, read from the `G6.4` artefact. Held-in is the easier
     task; the model saw that country's diaries. 🔴 **Held-in scoring WORSE than
     held-out is the alarm this gate exists to raise**, and it is the direction, not
     the magnitude, that carries the meaning.

🔴 THE TOLERANCE ON CLAUSE 2 IS 0.0 pp AND IS RULED. `D-S6-12` question 2, ruled (a)
on 2026-08-22: the strict reading stands. Held-in scoring worse than held-out by ANY
margin is the alarm, so clause 2 is a DIRECTIONAL non-inferiority guard and the methods
must describe it as one rather than as a calibrated tolerance. Do not widen it to
accommodate a result.

🔴 `FINDING 93`, 2026-08-22. On the Leg-4 pilot this clause read 5 of 6 PASS and the
reading was an artefact of the OTHER side of the comparison: `es`'s held-out reference
was 363.44 %, which was `FINDING 90` itself -- a 1-minute published cell -- so any
held-in score beat it and every pair referencing Spain passed by default. Under the APE
floor that reference is 42.57 % and the board is 2 of 6. NEVER quote the 5/6.

🔴 THE REGISTERED PERTURBATION CANNOT BE RUN FROM THIS MODULE. The val doc registers
"train country-by-country sequentially -> G6.6", and that needs its own adapter --
`4thJ_step4_train.py --perturbation sequential_countries` already implements the lever
(`FINDING 6`), but it is a TRAINING run, not a re-score. The four injections below are
scoring-side and fell the gate honestly; the sequential-training one is a NAMED GAP
and is printed as such.
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
import decoder as dec
from encoder import load_bit_positions

MIN_RECORDS = 20      # identical to G6.4: below this a band is NOT SCORED
MAPE_MAX = 15.0       # G6.4's bar, reused verbatim -- NOT a second project choice
SCOPE = ("es", "uk", "it")

PERTURBATIONS = ["null", "wrong_tables", "flatten_to_ac0", "degrade_donor",
                 "sequential_countries"]


def pairs():
    """(fold, donor) for every fold and every country that fold trained on."""
    return [(f, d) for f in SCOPE for d in SCOPE if d != f]


def gen_path(gen_dir, leg, fold, donor):
    return os.path.join(gen_dir,
                        "generated_leg%d_%s_g66%s.jsonl" % (leg, fold, donor))


def load_batch(path):
    if not os.path.exists(path):
        return None
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    return rows or None


def band_budgets(rows, bp, weights=None):
    """Split a batch by scoreable age band, exactly as `G6.4` does.

    The GENERATED arm is unweighted: the prefixes were drawn from the fitted
    synthetic population, so re-weighting would apply the raking twice. The CORPUS
    arm carries `weight_dia_cal` (`FINDING 53`) and is the calibration arm."""
    by = collections.defaultdict(lambda: ([], []))
    for i, r in enumerate(rows):
        d = dec.decode_record(r["text"], bp)
        w = None if weights is None else weights[i]
        band = L1.AGE_BAND_MAP.get(r.get("strat_age_band")
                                   or d["prefix"]["strat_age_band"])
        by["ALL"][0].append(d)
        by["ALL"][1].append(w)
        if band:
            by[band][0].append(d)
            by[band][1].append(w)
    return by


def perturb(name, budget_map, donor):
    """Scoring-side injections. `budget_map` is {aggregate: minutes/day}; the return
    is a NEW map, and the published side is signalled by the returned donor key."""
    if name == "null":
        return budget_map, donor
    if name == "wrong_tables":
        # score the donor's output against a country whose token was never used
        other = [c for c in SCOPE if c != donor][0]
        return budget_map, other
    if name == "flatten_to_ac0":
        # a model that forgot everything and sleeps all day
        m = {k: 0.0 for k in budget_map}
        m["AC0"] = float(sum(budget_map.values()))
        return m, donor
    if name == "degrade_donor":
        # a 40 % shift out of paid work and study into personal care -- the shape a
        # half-forgotten country would take, big enough to clear the bar, not a wipe
        m = dict(budget_map)
        moved = 0.0
        for k in ("AC2", "AC3"):
            if k in m:
                moved += m[k] * 0.40
                m[k] = m[k] * 0.60
        m["AC0"] = m.get("AC0", 0.0) + moved
        return m, donor
    if name == "sequential_countries":
        return None, donor      # NOT A RE-SCORE. Needs its own training run.
    raise ValueError("unknown perturbation %r" % name)


def score_pair(rows, bp, eurostat, donor, wave, held_out_mape, tol_pp, pert,
               weights=None):
    """One (fold, donor) batch, both clauses, under one injection."""
    by = band_budgets(rows, bp, weights)
    out = {"n": len(rows), "bands": {}}
    mapes, maes = [], []
    for band in L1.SCOREABLE_BANDS:
        recs, ws = by.get(band, ([], []))
        if len(recs) < MIN_RECORDS:
            out["bands"][band] = {"blocked": True, "n": len(recs)}
            continue
        m = L1.budget(recs, None if weights is None else ws)
        m2, pub_country = perturb(pert, m, donor)
        if m2 is None:
            out["bands"][band] = {"blocked": True, "n": len(recs),
                                  "reason": "perturbation needs a training run"}
            continue
        pub = L1.published(eurostat, pub_country, age=band, wave=wave)
        g = L1.gate_g6_4(m2, pub, band)
        g["published_country"] = pub_country
        out["bands"][band] = g
        mapes.append((g["mape"], band))
        maes.append((g["mae"], band))
    if not mapes:
        out["blocked"] = True
        return out
    worst = max(mapes)[0]
    out["worst_mape"] = worst
    # 🔴 `D-S6-12` item 1 point 3: MAE in min/day is reported BESIDE the MAPE on every
    # pair, and the band each of them calls worst is named. Over `G6.6`'s eighteen
    # cells the two are NEGATIVELY rank-correlated (Spearman -0.5604, `FINDING 90`),
    # so they will often disagree. The verdict is the MAPE; the minutes are the
    # context without which the percentage has repeatedly been misread.
    out["worst_mae_min_day"] = max(maes)[0]
    out["worst_band_by_mape"] = max(mapes)[1]
    out["worst_band_by_mae"] = max(maes)[1]
    # clause 1 -- absolute, G6.4's bar
    c1 = worst <= MAPE_MAX
    # clause 2 -- paired against the same country held OUT
    if held_out_mape is None:
        c2, c2_note = None, ("NOT SCORED: no held-out MAPE for this country in the "
                             "G6.4 artefact. NOT SCORED is not a pass.")
        out["blocked_clause2"] = True
    else:
        c2 = (worst - held_out_mape) <= tol_pp
        c2_note = None
    out["held_out_mape"] = held_out_mape
    out["delta_pp"] = None if held_out_mape is None else worst - held_out_mape
    out["clause1_absolute"] = c1
    out["clause2_paired"] = c2
    out["clause2_note"] = c2_note
    out["passes"] = bool(c1 and c2 is True)
    return out


def read_g64_heldout(path, country):
    """The same country's WORST scoreable-band MAPE in the fold that holds it OUT.
    🔴 Read BY FILE from the G6.4 artefact, never re-derived here: a gate that
    recomputes its own reference can drift from the gate it claims to be comparable
    with, and this comparison is only meaningful if both sides used one scorer."""
    if not path or not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    f = (d.get("folds") or {}).get(country)
    if not f or f.get("blocked"):
        return None
    vals = [g["mape"] for b, g in (f.get("bands") or {}).items()
            if b != "ALL" and not g.get("blocked")]
    return max(vals) if vals else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen")
    ap.add_argument("--corpus", help="4J_step3_corpus.jsonl -- the CALIBRATION arm")
    ap.add_argument("--harmonised", help="harmonised.parquet, for weight_dia_cal")
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--eurostat", required=True)
    ap.add_argument("--g64", help="G6.4 artefact -- supplies the held-OUT reference")
    ap.add_argument("--wave", default="2010")
    ap.add_argument("--tolerance-pp", type=float, default=0.0,
                    help="clause 2 slack in MAPE points. 🔴 D-S6-12 question 2 "
                         "RULED (a) 2026-08-22: the band STAYS at 0.0 pp -- a strict "
                         "non-inferiority test, declared in the methods as a "
                         "DIRECTIONAL guard and not a calibrated tolerance. Do not "
                         "widen it to accommodate a result.")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if not (a.gen or a.corpus):
        ap.error("one of --gen or --corpus is required")
    if a.corpus and not a.harmonised:
        ap.error("--corpus needs --harmonised for weight_dia_cal (FINDING 53)")
    arm = "generated" if a.gen else "corpus"

    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))

    print("=" * 78)
    print("G6.6 -- regression on held-IN countries, %s arm, wave %s"
          % (arm.upper(), a.wave))
    print("=" * 78)
    print("clause 1  absolute:  worst scoreable-band MAPE <= %.1f %% (G6.4's bar, reused)"
          % MAPE_MAX)
    print("           APE floor:  published cells < %.1f min/day are scored on an "
          "absolute" % L1.PUBLISHED_FLOOR_MIN)
    print("                       tolerance of %.1f min/day instead (D-S6-12 item 1)"
          % L1.FLOOR_MAE_MAX)
    print("clause 2  paired:    held-IN MAPE - held-OUT MAPE <= %.2f pp" % a.tolerance_pp)
    print("          the DIRECTION is the finding: held-in is the easier task.")
    if arm == "generated" and a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")
    if arm == "corpus":
        print("\n🔴 CALIBRATION ARM. Clause 1 and the injections are calibrated")
        print("   against ground truth here. CLAUSE 2 IS NOT SCORED on this arm: a real")
        print("   corpus does not belong to a fold, so there is no held-in / held-out")
        print("   pair to compare. That is a gap, not a pass.\n")

    out = {"arm": arm, "leg": a.leg, "wave": a.wave, "tolerance_pp": a.tolerance_pp,
           "mape_max": MAPE_MAX, "pairs": {}, "perturbations": {},
           "provenance": "LEG-4 PILOT -- NOT REPORTABLE" if a.leg == 4 else None}

    batches, missing = {}, []
    if arm == "corpus":
        G64 = importlib.import_module("4thJ_step6_g64_run")
        for c in SCOPE:
            rows, ws, dropped = G64.load_corpus(a.corpus, a.harmonised, c)
            print("corpus %s: %d diaries%s"
                  % (c, len(rows),
                     ("  (%d dropped for a null weight)" % dropped) if dropped else ""))
            batches[("corpus", c)] = (rows, ws)
    else:
        for fold, donor in pairs():
            p = gen_path(a.gen, a.leg, fold, donor)
            rows = load_batch(p)
            if rows is None:
                missing.append(p)
            else:
                batches[(fold, donor)] = (rows, None)

    if missing:
        print("🔴 BLOCKED -- %d of 6 (fold, donor) batches do not exist:" % len(missing))
        for p in missing:
            print("     %s" % os.path.basename(p))
        print("   Generate them with 4thJ_step7_generate.sh, giving the FOLD's adapter")
        print("   the DONOR's Step 5 prefixes and --tag g66<donor>. NOT SCORED is not")
        print("   a pass, and this module exits 2 rather than print a board.")
        out["blocked"] = True
        out["missing_batches"] = missing
        if a.out:
            json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2, sort_keys=True)
            print("written: %s" % a.out)
        return 2

    if arm == "corpus":
        # clause 2 is structurally unavailable here, and it is reported as NOT
        # SCORED rather than silently satisfied by comparing a country with itself.
        heldout = {c: None for c in SCOPE}
        print("held-OUT reference: NOT APPLICABLE on the corpus arm")
    else:
        heldout = {c: read_g64_heldout(a.g64, c) for c in SCOPE}
        print("held-OUT reference, read BY FILE from %s:" % (a.g64 or "(none given)"))
        for c in SCOPE:
            print("   %s  %s" % (c, "NOT AVAILABLE" if heldout[c] is None
                                 else "%.2f %%" % heldout[c]))

    board = collections.Counter()
    for (fold, donor), (rows, ws) in sorted(batches.items()):
        r = score_pair(rows, bp, a.eurostat, donor, a.wave,
                       heldout[donor], a.tolerance_pp, "null", ws)
        out["pairs"]["%s/%s" % (fold, donor)] = r
        if r.get("blocked"):
            print("\nfold %s, donor %s: BLOCKED" % (fold, donor))
            board["BLOCKED"] += 1
            continue
        print("\nfold %s, donor %s  n=%d  worst MAPE %.2f %%  held-out %s  delta %s"
              % (fold, donor, r["n"], r["worst_mape"],
                 "n/a" if r["held_out_mape"] is None else "%.2f %%" % r["held_out_mape"],
                 "n/a" if r["delta_pp"] is None else "%+.2f pp" % r["delta_pp"]))
        # 🔴 `D-S6-12` item 1 point 3: the minutes are printed beside the percentage,
        # and where the two disagree about the worst band that disagreement is named.
        print("   worst by MAPE %s %.2f %%  |  worst by MAE %s %.2f min/day%s"
              % (r["worst_band_by_mape"], r["worst_mape"],
                 r["worst_band_by_mae"], r["worst_mae_min_day"],
                 "" if r["worst_band_by_mape"] == r["worst_band_by_mae"]
                 else "   <- the two bases DISAGREE (FINDING 90)"))
        # on the corpus arm clause 2 is NOT SCORED, so the verdict is clause 1 alone
        ok = r["clause1_absolute"] if arm == "corpus" else r["passes"]
        print("   clause 1 absolute %s | clause 2 paired %s -> %s"
              % ("PASS" if r["clause1_absolute"] else "FAIL",
                 "NOT SCORED" if r["clause2_paired"] is None
                 else ("PASS" if r["clause2_paired"] else "FAIL"),
                 "PASS" if ok else "FAIL"))
        r["arm_verdict"] = ok
        board["PASS" if ok else "FAIL"] += 1
    out["board"] = dict(board)
    print("\nBOARD over the %s: %s"
          % ("three countries (clause 1 only)" if arm == "corpus"
             else "six (fold, donor) pairs", dict(board)))
    return finish(a, out, batches, bp, heldout)


def finish(a, out, batches, bp, heldout):
    """The perturbation battery and the coverage clause, on the same code path."""
    print("\n" + "=" * 78)
    print("PERTURBATIONS -- a gate that has never been seen falling is not a gate")
    print("=" * 78)
    seen = []
    for pert in PERTURBATIONS:
        if pert == "sequential_countries":
            out["perturbations"][pert] = {
                "runnable": False,
                "note": "NOT RUN, and NOT RUNNABLE from this module. The registered "
                        "lever is a TRAINING run -- 4thJ_step4_train.py "
                        "--perturbation sequential_countries, which trains one "
                        "country per epoch so the country trained first is "
                        "measurably forgotten. It needs an adapter of its own. This "
                        "is a NAMED GAP, not a pass."}
            print("  %-22s 🔴 NOT RUNNABLE HERE -- needs its own training run (NAMED GAP)"
                  % pert)
            continue
        fell = []
        for (fold, donor), (rows, ws) in sorted(batches.items()):
            r = score_pair(rows, bp, a.eurostat, donor, a.wave,
                           heldout[donor], a.tolerance_pp, pert, ws)
            ok = (r["clause1_absolute"] if out["arm"] == "corpus" else r["passes"])
            if not r.get("blocked") and not ok:
                fell.append("%s/%s" % (fold, donor))
        out["perturbations"][pert] = {"runnable": True, "fell": fell}
        print("  %-22s fell: %s" % (pert, ",".join(fell) if fell else "(nothing)"))
        if pert != "null" and fell:
            seen.append(pert)

    null_fell = out["perturbations"]["null"]["fell"]
    cov = {"passes": bool(seen) and not null_fell,
           "seen_failing_via": seen,
           "no_op_perturbations": [p for p in PERTURBATIONS
                                   if p not in ("null", "sequential_countries")
                                   and not out["perturbations"][p]["fell"]],
           "named_gap": "sequential_countries"}
    out["coverage_clause"] = cov
    print("\ncoverage clause: %s" % ("PASS" if cov["passes"] else "FAIL"))
    if cov["no_op_perturbations"]:
        print("  🔴 no-op injections: %s" % ",".join(cov["no_op_perturbations"]))
    print("  🔴 the registered sequential-training perturbation is a NAMED GAP and is")
    print("     not covered by any injection above.")

    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=2, sort_keys=True,
                  default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
