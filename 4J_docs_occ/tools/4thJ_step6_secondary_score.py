# -*- coding: utf-8 -*-
"""`G6.2` and `G6.3` — SCORE the model against the secondary nulls.

  usage: python 4thJ_step6_secondary_score.py --gen DIR --leg 4 --step2 DIR
                                              --eurostat DIR [--folds es,uk,it]

`tools/4thJ_step6_secondary_nulls.py` BUILDS them and reports their construction;
`secondary_nulls.json` is its artefact. Like `G6.1`'s builder it scores nothing.
This turns each into a level-1 time budget and takes the same margin, on the same
metric, against the same published column, so `G6.1`, `G6.2` and `G6.3` are three
readings of one comparison rather than three different comparisons.

🔴 **Both nulls are IMPORTED, never rebuilt here.** `build_pooled` carries
`D-S6-7` (a)'s equal-country-mass renormalisation and `build_all_neighbours`
carries `D-S6-6` (a)'s refusal to nominate a single neighbour. Re-deriving either
in this file would be a second copy of a ruling.

🔴 **`G6.2` is SIX nulls, two per fold, and neither of a fold's pair is the
result.** `D-S6-6` (a) dropped the word *nearest*. Reporting one without its
sibling is exactly the gate-shopping the ruling exists to prevent, so this module
prints both and refuses to reduce them to one number.

🔴 **`G6.2` and `G6.3` are REPORTED, not thresholded** — the gate table says so.
A margin is printed with its sign; no PASS/FAIL is emitted for either.
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
sn = importlib.import_module("4thJ_step6_secondary_nulls")
import decoder as dec
from encoder import load_bit_positions

MIN_RECORDS = 20


def corpus_index(corpus_path, bitpos):
    """(country, pid, diary_day) -> decoded record. The join key the secondary
    nulls' donor dicts already carry."""
    out = {}
    for line in open(corpus_path, encoding="utf-8"):
        r = json.loads(line)
        out[(r["country"], r["pid"], r["diary_day"])] = dec.decode_record(r["text"], bitpos)
    return out


def score_one(donors, ws, index, gen_recs, gen_bands, fold, eurostat, wave):
    rows = {}
    nb = [L1.AGE_BAND_MAP.get(d["strat_age_band"]) for d in donors]
    for band in L1.SCOREABLE_BANDS:
        mi = [i for i, b in enumerate(gen_bands) if b == band]
        ni = [i for i, b in enumerate(nb) if b == band]
        if len(mi) < MIN_RECORDS or len(ni) < MIN_RECORDS:
            rows[band] = {"blocked": True, "n_model": len(mi), "n_null": len(ni)}
            continue
        pub = L1.published(eurostat, fold, age=band, wave=wave)
        m = L1.budget([gen_recs[i] for i in mi])
        recs = [index[(donors[i]["country"], donors[i]["pid"], donors[i]["diary_day"])]
                for i in ni]
        n = L1.budget(recs, weights=[ws[i] for i in ni])
        m_mae, n_mae = L1.mae(m, pub), L1.mae(n, pub)
        rows[band] = {"n_model": len(mi), "n_null": len(ni),
                      "model_mae": round(m_mae, 4), "null_mae": round(n_mae, 4),
                      "margin": round(n_mae - m_mae, 4),
                      "published_source": pub["_source"]}
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--eurostat", required=True)
    ap.add_argument("--corpus", default=sn.CORPUS)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--wave", default="2010")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))
    print("=" * 78)
    print("G6.2 (six single-donor nulls) and G6.3 (pooled, EQUAL COUNTRY MASS)")
    print("=" * 78)
    print("metric: MAE of the level-1 budget vs the published table, min/day")
    print("🔴 BOTH ARE REPORTED, NOT THRESHOLDED. No PASS/FAIL is emitted.")
    print("🔴 G6.2 is TWO nulls per fold. Neither is the result; the pair is.")
    if a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    weights, null_keys = sn.load_weight_table()
    index = corpus_index(a.corpus, bp)
    print("corpus index: %d diaries | weight field: weight_dia_cal | "
          "null-weight diaries: %d" % (len(index), len(null_keys)))

    out = {"leg": a.leg, "wave": a.wave, "folds": {}}
    for fold in a.folds.split(","):
        gp = os.path.join(a.gen, "generated_leg%d_%s_constrained.jsonl" % (a.leg, fold))
        if not os.path.exists(gp):
            print("\n%s: no generated batch at %s -- NOT SCORED" % (fold, gp))
            continue
        gen_rows = [json.loads(l) for l in open(gp, encoding="utf-8") if l.strip()]
        gen_recs = [dec.decode_record(r["text"], bp) for r in gen_rows]
        gen_bands = [L1.AGE_BAND_MAP.get(r["strat_age_band"]) for r in gen_rows]

        print("\n" + "-" * 78)
        print("fold %s  |  %d generated diaries" % (fold, len(gen_rows)))
        print("-" * 78)

        fold_out = {}
        nulls = [("G6.3 pooled", sn.build_pooled(fold, weights, corpus=a.corpus,
                                                 null_keys=null_keys))]
        for donors, ws, meta in sn.build_all_neighbours(fold, weights, corpus=a.corpus,
                                                        null_keys=null_keys):
            nulls.append(("G6.2 donor=%s" % meta["neighbour"], (donors, ws, meta)))

        for label, (donors, ws, meta) in nulls:
            rows = score_one(donors, ws, index, gen_recs, gen_bands, fold,
                             a.eurostat, a.wave)
            print("\n  %s   (%d donors, raked=%s)"
                  % (label, len(donors), meta.get("raked")))
            print("    %-8s %6s %7s %9s %9s %10s"
                  % ("band", "n_mod", "n_null", "model MAE", "null MAE", "margin"))
            for band in L1.SCOREABLE_BANDS:
                r = rows[band]
                if r.get("blocked"):
                    print("    %-8s %6d %7d   NOT SCORED"
                          % (band, r["n_model"], r["n_null"]))
                    continue
                print("    %-8s %6d %7d %9.3f %9.3f %+10.3f"
                      % (band, r["n_model"], r["n_null"], r["model_mae"],
                         r["null_mae"], r["margin"]))
            fold_out[label] = {"meta": {k: meta.get(k) for k in
                                        ("null", "neighbour", "raked", "ess",
                                         "ess_frac", "marginals_source",
                                         "worst_strata_gap_pp")},
                               "bands": rows}
        out["folds"][fold] = fold_out

    print("\n" + "=" * 78)
    print("🔴 Reported, not thresholded. A G6.2 margin quoted without its sibling "
          "donor country\n   is the gate-shopping D-S6-6 (a) exists to prevent.")
    print("=" * 78)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
