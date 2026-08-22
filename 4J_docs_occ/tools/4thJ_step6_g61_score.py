# -*- coding: utf-8 -*-
"""`G6.1` — SCORE the model against the raked-donor null.

  usage: python 4thJ_step6_g61_score.py --gen DIR --leg 4 --step2 DIR
                                        --eurostat DIR [--folds es,uk,it] [--out JSON]

`tools/4thJ_step6_g61_rake_folds.py` answered the question that came first — *can
the null be BUILT for this fold?* — and said so in its own words: **"IT DOES NOT
SCORE ANYTHING."** This does. It is the pre-registered bar and the headline gate:

    prereg §5: "If a fine-tuned LLM cannot beat a demographically raked pool of
    real European donors on the held-out country, the transfer claim fails. There
    is no weaker reading of that sentence."

---------------------------------------------------------------------------
The quantity
---------------------------------------------------------------------------

prereg §6 FAIL criterion 1 is **"MAE ≥ the raked-donor null"**, and `G6.4` fixes
what the error is measured on: the **level-1 time budget** against the held-out
country's published Eurostat table. So both sides produce a level-1 budget in
minutes/day, both are scored against the SAME published column, and the margin is
the difference of their two MAEs. `tools/4thJ_step6_level1.py` owns the crosswalk
and `4thJ_step6_rakeddonor.score_margin` owns the comparison, including its Guard 1
— both sides must have been raked onto or prompted from the same marginals.

🔴 **Restriction to an age band happens AFTER raking, never before.** The null is
raked onto the whole synthetic population, exactly as the model was prompted from
the whole synthetic population; taking the `Y25-44` slice of each afterwards is a
conditional budget on both sides. Raking separately per band would build three
different nulls and quietly make each one easier.

🔴 **The three registered collapses are imported from the runner**, not restated.
A second copy of that list is the `V7.c` failure mode with different nouns.
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
rd = importlib.import_module("4thJ_step6_rakeddonor")
rf = importlib.import_module("4thJ_step6_g61_rake_folds")
import decoder as dec
from encoder import load_bit_positions

MIN_RECORDS = 20


def load_donors(corpus_path, held_out, bitpos):
    """Every diary NOT from the held-out country, with its strata AND its text."""
    strata, recs = [], []
    for line in open(corpus_path, encoding="utf-8"):
        r = json.loads(line)
        if r["country"] == held_out:
            continue
        f = r["text"].split("|", 1)[0].split(",")
        d = {"country": r["country"]}
        for v in rf.VARS:
            d[v] = f[rf.PFX[v]]
        strata.append(d)
        recs.append(dec.decode_record(r["text"], bitpos))
    return strata, recs


def build_null(fold, corpus_path, bitpos):
    """The raked-donor null for one fold: donor records plus their IPF weights."""
    tgt, n_pop = rf.target_from_population(fold)
    strata, recs = load_donors(corpus_path, fold, bitpos)

    coll = {"strat_hh_type": {"unknown": "other_complex"}}
    if "homemaker" not in tgt["strat_econ_status"]:
        coll["strat_econ_status"] = {"homemaker": "other_inactive"}
    for cat in set(d["strat_econ_status"] for d in strata):
        if cat not in tgt["strat_econ_status"] and cat != "homemaker":
            coll.setdefault("strat_econ_status", {})[cat] = "other_inactive"
    unreg = rf.check_registered(coll)
    if unreg:
        raise SystemExit("REFUSED: collapse(s) not registered in %s: %s"
                         % (rf.ADDENDUM, "; ".join("%s: %s->%s" % t for t in unreg)))

    source = "population_%s.csv|D-S5-11b" % fold
    res = rd.rake(strata, tgt, fold, marginals_source=source, collapse=coll)
    return dict(strata=strata, records=recs, weights=res["weights"],
                iterations=res["iterations"], max_dev_pp=res["max_dev_pp"],
                marginals_source=source, n_population=n_pop,
                collapses=coll)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--eurostat", required=True)
    ap.add_argument("--corpus", default=rf.CORPUS)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--wave", default="2010")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))
    print("=" * 78)
    print("G6.1 -- margin over the RAKED-DONOR NULL, the pre-registered bar")
    print("=" * 78)
    print("metric: MAE of the level-1 time budget vs the published table, min/day")
    print("lower is better; the margin is null_MAE - model_MAE and must be > 0 STRICTLY")
    if a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    out = {"leg": a.leg, "wave": a.wave, "folds": {}}
    for fold in a.folds.split(","):
        gp = os.path.join(a.gen, "generated_leg%d_%s_constrained.jsonl" % (a.leg, fold))
        if not os.path.exists(gp):
            print("\n%s: no generated batch at %s -- NOT SCORED" % (fold, gp))
            out["folds"][fold] = {"blocked": True, "reason": "no batch at %s" % gp}
            continue

        print("\n" + "-" * 78)
        print("fold %s  (donors = %s)"
              % (fold, "+".join(x for x in ("es", "uk", "it") if x != fold)))
        print("-" * 78)
        null = build_null(fold, a.corpus, bp)
        print("  null: %d donors raked onto population_%s.csv (%d persons) in %d "
              "iterations, worst margin %.5f pp"
              % (len(null["records"]), fold, null["n_population"],
                 null["iterations"], null["max_dev_pp"]))
        print("  collapses: %s" % json.dumps(null["collapses"], sort_keys=True))

        gen_rows = [json.loads(l) for l in open(gp, encoding="utf-8") if l.strip()]
        gen_recs = [dec.decode_record(r["text"], bp) for r in gen_rows]
        gen_bands = [L1.AGE_BAND_MAP.get(r["strat_age_band"]) for r in gen_rows]
        null_bands = [L1.AGE_BAND_MAP.get(s["strat_age_band"]) for s in null["strata"]]
        print("  model: %d generated diaries from %s" % (len(gen_rows), os.path.basename(gp)))

        fold_out = {"bands": {}, "null": {k: null[k] for k in
                                          ("iterations", "max_dev_pp",
                                           "marginals_source", "n_population")}}
        print("\n  %-8s %6s %6s %9s %9s %10s %s"
              % ("band", "n_mod", "n_null", "model MAE", "null MAE", "margin", "verdict"))
        for band in L1.SCOREABLE_BANDS:
            mi = [i for i, b in enumerate(gen_bands) if b == band]
            ni = [i for i, b in enumerate(null_bands) if b == band]
            if len(mi) < MIN_RECORDS or len(ni) < MIN_RECORDS:
                print("  %-8s %6d %6d   NOT SCORED (< %d records on one side)"
                      % (band, len(mi), len(ni), MIN_RECORDS))
                fold_out["bands"][band] = {"blocked": True,
                                           "n_model": len(mi), "n_null": len(ni)}
                continue
            pub = L1.published(a.eurostat, fold, age=band, wave=a.wave)
            m_bud = L1.budget([gen_recs[i] for i in mi])
            n_bud = L1.budget([null["records"][i] for i in ni],
                              weights=[null["weights"][i] for i in ni])
            m_mae, n_mae = L1.mae(m_bud, pub), L1.mae(n_bud, pub)
            # Guard 1: both sides on the SAME marginals. The model was prompted
            # from `population_<c>.csv`; the null was raked onto it.
            sc = rd.score_margin(m_mae, n_mae, lower_is_better=True,
                                 model_source=null["marginals_source"],
                                 null_source=null["marginals_source"])
            print("  %-8s %6d %6d %9.3f %9.3f %+10.3f %s"
                  % (band, len(mi), len(ni), m_mae, n_mae, sc["margin"],
                     "PASS" if sc["passes"] else "FAIL"))
            fold_out["bands"][band] = dict(
                n_model=len(mi), n_null=len(ni),
                model_mae=round(m_mae, 4), null_mae=round(n_mae, 4),
                margin=round(sc["margin"], 4), passes=sc["passes"], strict=sc["strict"],
                model_budget=m_bud, null_budget=n_bud,
                published_source=pub["_source"])
        out["folds"][fold] = fold_out

    board = collections.Counter()
    for f, r in out["folds"].items():
        for b, g in (r.get("bands") or {}).items():
            if g.get("blocked"):
                board["NOT SCORED"] += 1
            else:
                board["PASS" if g["passes"] else "FAIL"] += 1
    out["board"] = dict(board)
    print("\n" + "=" * 78)
    print("G6.1 BOARD: %s" % dict(board))
    print("=" * 78)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
