# -*- coding: utf-8 -*-
"""Run `G6.4` — the level-1 time budget — on a batch, and write the artefact.

  usage: python 4thJ_step6_g64_run.py --gen DIR --leg 4 --step2 DIR
                                      --eurostat DIR --out JSON [--folds es,uk,it]
         python 4thJ_step6_g64_run.py --corpus FILE --harmonised PARQUET ...

Two sources, and the pair is the point:

  * `--gen`  scores a GENERATED batch. Unweighted, because the synthetic population
    it was prompted from is already the fitted marginals -- re-weighting it would
    apply the raking twice.
  * `--corpus` scores the REAL harmonised corpus, weighted by `weight_dia_cal`.
    🔴 This is the CALIBRATION arm and it is not optional: a gate whose own ground
    truth cannot pass it is not measuring the model, and until the corpus arm was
    run this gate reported a 31 % error on travel that belonged to the crosswalk.
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

MIN_RECORDS = 20   # below this a band is NOT SCORED, and NOT SCORED is not a pass


def load_generated(gen_dir, leg, fold):
    p = os.path.join(gen_dir, "generated_leg%d_%s_constrained.jsonl" % (leg, fold))
    if not os.path.exists(p):
        return None, p
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return rows, p


def load_corpus(path, harmonised, fold):
    import pyarrow.parquet as pq
    df = pq.read_table(harmonised, columns=["country", "pid", "diary_day",
                                            "weight_dia_cal"]).to_pandas()
    df["country"] = df["country"].str.lower()
    df = df.drop_duplicates(subset=["country", "pid", "diary_day"])
    W = {(r.country, r.pid, r.diary_day): float(r.weight_dia_cal) for r in df.itertuples()}
    rows, weights, dropped = [], [], 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        if r["country"] != fold:
            continue
        w = W.get((r["country"], r["pid"], r["diary_day"]))
        if w is None or math.isnan(w):
            dropped += 1
            continue
        rows.append(r)
        weights.append(w)
    return rows, weights, dropped


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen")
    ap.add_argument("--corpus")
    ap.add_argument("--harmonised")
    ap.add_argument("--leg", type=int, default=4)
    ap.add_argument("--step2", required=True)
    ap.add_argument("--eurostat", required=True)
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--wave", default="2010")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if not (a.gen or a.corpus):
        ap.error("one of --gen or --corpus is required")
    if a.corpus and not a.harmonised:
        ap.error("--corpus needs --harmonised for weight_dia_cal (FINDING 53)")

    bp = load_bit_positions(os.path.join(a.step2, "crosswalk_copresence.csv"))
    arm = "generated" if a.gen else "corpus"

    print("=" * 78)
    print("G6.4 -- level-1 time budget, %s arm, wave %s" % (arm.upper(), a.wave))
    print("=" * 78)
    print("bit positions (read live): %s" % bp)
    print("crosswalk: 910 -> AC9A | 995-997,999 -> AC99NSP | 998 -> AC4-8")
    print("AC9A: the SUM OF ITS SEVEN CHILDREN, never the published parent")
    print("APE floor (D-S6-12 item 1): published cells < %.1f min/day are marked `!`"
          % L1.PUBLISHED_FLOOR_MIN)
    print("            and scored on an absolute %.1f min/day tolerance, not on a "
          "percentage" % L1.FLOOR_MAE_MAX)
    if arm == "generated" and a.leg == 4:
        print("\n🔴 LEG-4 PILOT -- NOT REPORTABLE.\n")

    out = {"arm": arm, "leg": a.leg, "wave": a.wave, "folds": {}}
    for fold in a.folds.split(","):
        if arm == "generated":
            rows, path = load_generated(a.gen, a.leg, fold)
            weights = None
            dropped = 0
        else:
            rows, weights, dropped = load_corpus(a.corpus, a.harmonised, fold)
            path = a.corpus
        if not rows:
            print("\n%s: NO RECORDS at %s -- NOT SCORED, and NOT SCORED is not a pass"
                  % (fold, path))
            out["folds"][fold] = {"blocked": True, "reason": "no records at %s" % path}
            continue

        by = collections.defaultdict(lambda: ([], []))
        for i, r in enumerate(rows):
            d = dec.decode_record(r["text"], bp)
            w = None if weights is None else weights[i]
            band = L1.AGE_BAND_MAP.get(r.get("strat_age_band")
                                       or d["prefix"]["strat_age_band"])
            for k in (["ALL"] + ([band] if band else [])):
                by[k][0].append(d)
                by[k][1].append(w)

        print("\n%s  %d records from %s%s"
              % (fold, len(rows), os.path.basename(path),
                 ("  (%d dropped for a null weight)" % dropped) if dropped else ""))
        fold_out = {"n": len(rows), "source": path, "dropped_null_weight": dropped,
                    "bands": {}}
        for band in ("ALL",) + L1.SCOREABLE_BANDS:
            recs, ws = by.get(band, ([], []))
            if len(recs) < MIN_RECORDS:
                print("  %-8s n=%4d  NOT SCORED (< %d records)" % (band, len(recs), MIN_RECORDS))
                fold_out["bands"][band] = {"blocked": True, "n": len(recs)}
                continue
            m = L1.budget(recs, None if weights is None else ws)
            pub = L1.published(a.eurostat, fold,
                               age=("TOTAL" if band == "ALL" else band), wave=a.wave)
            g = L1.gate_g6_4(m, pub, band)
            # `D-S6-12` item 1: a cell whose published value is below the APE floor
            # is marked `!`, so the reader can see at once which cells the percentage
            # was NOT taken over. `FINDING 90` was invisible precisely because it was
            # not marked.
            cells = "  ".join("%s %.0f/%.0f%s" % (r["aggregate"], r["model"],
                                                  r["published"],
                                                  "" if r["basis"] == "APE" else "!")
                              for r in g["rows"])
            print("  %-8s n=%4d  %-4s MAPE=%7.2f %%  MAE=%6.2f  %s"
                  % (band, len(recs), "PASS" if g["passes"] else "FAIL",
                     g["mape"], g["mae"], cells))
            for r in g["reasons"]:
                print("           - %s" % r)
            if band == "ALL":
                print("           context only: TOTAL's population base is not stated "
                      "and our floor is age 11")
            g["model_budget"] = m
            g["ac9a_parent_minus_children"] = pub["_ac9a_parent_minus_children"]
            fold_out["bands"][band] = g
        out["folds"][fold] = fold_out

    board = collections.Counter()
    for f, r in out["folds"].items():
        for b, g in (r.get("bands") or {}).items():
            if b == "ALL" or g.get("blocked"):
                continue
            board["PASS" if g["passes"] else "FAIL"] += 1
    out["board_scoreable_bands"] = dict(board)
    print("\n" + "=" * 78)
    print("BOARD over the three EXACT age bands (ALL excluded -- different "
          "population base): %s" % dict(board))
    print("=" * 78)

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True, default=str)
        print("written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
