# -*- coding: utf-8 -*-
"""Step 7, work item 7.4 -- THE THREE-MODEL FIRING-RATE REPORT.

  usage: python 4thJ_step7_firing_rate_report.py --gen DIR --step2 DIR --leg 5
                                                 [--folds es,uk,it] [--out CSV]

`4thJ_07_constrainedGeneration.md:206` fixes the item in one line: *"Untuned base,
fine-tuned unconstrained, fine-tuned constrained. Per stratum."* Two of those three
arms have existed since 2026-08-24; the third needed a generator that could skip
the adapter, which is what `--base-only` added on 2026-08-26.

WHAT A FIRING RATE IS HERE
==========================
`D-S7-4` defines it, and this file does not redefine it: **the share of diaries the
model gets WRONG with the mask off**, per stratum. Two consequences that are easy
to get wrong and are therefore stated:

1. The **untuned base** arm is generated UNCONSTRAINED. A masked base arm would
   report a firing rate of zero by construction and would say nothing at all --
   the mask, not the model, would be doing the work. `--base-only` implies
   `--no-grammar` in the generator for exactly this reason.
2. The **fine-tuned constrained** arm is expected near zero, and that is not a
   result about the model either. It is reported because the three-way contrast is
   the item, and because a constrained arm that is NOT near zero would mean the
   mask is leaking -- which is worth seeing.

🔴 NOTHING HERE IS A GATE. `G7.7` and `G7.8` are scored by
`4thJ_gates_step7.py` on the fine-tuned unconstrained arm and are not re-scored,
re-thresholded or re-stated here. This file reports; it never returns a verdict.

🔴 THE STRATUM KEY AND THE VALIDATOR ARE IMPORTED, NEVER RESTATED. A second copy
of either is the `V7.c` failure mode with different nouns: `stratum_key` and the
alphabet builder come from `4thJ_gates_step7`, and validation is
`grammar.validate_record` under the same PERMISSIVE policy the gates use.

⚪ Every record already carries an `oracle_valid` stamp written at generation time.
This file re-validates anyway and reports any DISAGREEMENT between the stamp and
the re-run, because a silent divergence between the generator's oracle and the
scorer's oracle is the one defect a firing-rate table could not survive.
"""

import argparse
import collections
import csv
import importlib
import io
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

G7 = importlib.import_module("4thJ_gates_step7")
grammar = importlib.import_module("4thJ_step7_grammar")

# The three arms, in the order the item names them, and the filename tag each
# one is written under by `4thJ_step7_generate.py`.
ARMS = [
    ("untuned_base", "base",
     "untuned backbone, NO adapter, mask off (--base-only)"),
    ("finetuned_unconstrained", "nogrammar",
     "fine-tuned adapter, mask off (--no-grammar)"),
    ("finetuned_constrained", "constrained",
     "fine-tuned adapter, mask on -- expected near zero by construction"),
]


def load(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def score_arm(rows, alph):
    """-> (population_rate, {stratum: (n, n_invalid)}, n_stamp_disagreements)"""
    per = collections.defaultdict(lambda: [0, 0])
    n_bad = 0
    n_dis = 0
    for r in rows:
        ok = grammar.validate_record(r["text"], alph, G7.POLICY)[0]
        stamp = r.get("oracle_valid")
        if stamp is not None:
            s = stamp if isinstance(stamp, bool) else (str(stamp) == "True")
            if s != ok:
                n_dis += 1
        k = G7.stratum_key(r)
        per[k][0] += 1
        per[k][1] += 0 if ok else 1
        n_bad += 0 if ok else 1
    rate = n_bad / float(len(rows)) if rows else None
    return rate, per, n_dis


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, help="outputs_step7 directory")
    ap.add_argument("--step2", required=True)
    ap.add_argument("--leg", type=int, default=5, choices=(4, 5))
    ap.add_argument("--folds", default="es,uk,it")
    ap.add_argument("--out", default=None, help="firing_rate_by_stratum.csv")
    a = ap.parse_args(argv)

    alph = grammar.build_alphabets(a.step2)
    folds = [f.strip() for f in a.folds.split(",") if f.strip()]

    print("=" * 78)
    print("7.4 -- THE THREE-MODEL FIRING-RATE REPORT, leg %d" % a.leg)
    print("=" * 78)
    print("firing rate = share of diaries INVALID under the oracle, mask off")
    print("stratum     = (country, age_band, sex, hh_type, day_type), imported "
          "from 4thJ_gates_step7")
    print("V7.a floor  = %d strata carrying >= %d records"
          % (G7.V7A_MIN_STRATA, G7.V7A_MIN_RECORDS))
    print("")

    out_rows = []
    missing = []
    summary = []

    for fold in folds:
        for arm, tag, why in ARMS:
            p = os.path.join(a.gen, "generated_leg%d_%s_%s.jsonl"
                             % (a.leg, fold, tag))
            if not os.path.exists(p):
                missing.append((fold, arm, p))
                print("%-4s %-24s MISSING %s" % (fold, arm, p))
                continue
            rows = load(p)
            rate, per, n_dis = score_arm(rows, alph)
            big = {k: v for k, v in per.items() if v[0] >= G7.V7A_MIN_RECORDS}
            rates = {k: v[1] / float(v[0]) for k, v in big.items()}
            worst = max(rates, key=rates.get) if rates else None
            print("%-4s %-24s n=%-7d population %.6f | %d strata, %d with >= %d "
                  "records | worst-stratum %s | oracle-stamp disagreements %d"
                  % (fold, arm, len(rows), rate, len(per), len(big),
                     G7.V7A_MIN_RECORDS,
                     ("%.6f" % rates[worst]) if worst else "n/a", n_dis))
            print("     %s" % why)
            summary.append(dict(fold=fold, arm=arm, n=len(rows),
                                population_firing_rate=rate,
                                n_strata=len(per), n_strata_ge_min=len(big),
                                worst_stratum_rate=(rates[worst] if worst else None),
                                worst_stratum=(list(worst) if worst else None),
                                v7a_floor_met=(len(big) >= G7.V7A_MIN_STRATA),
                                oracle_stamp_disagreements=n_dis,
                                path=p))
            for k, v in sorted(per.items()):
                out_rows.append({
                    "leg": a.leg, "fold": fold, "arm": arm,
                    "country": k[0], "strat_age_band": k[1], "strat_sex": k[2],
                    "strat_hh_type": k[3], "strat_day_type": k[4],
                    "n": v[0], "n_invalid": v[1],
                    "firing_rate": round(v[1] / float(v[0]), 6),
                    "scorable_at_min_n": int(v[0] >= G7.V7A_MIN_RECORDS),
                })
        print("")

    if missing:
        print("🔴 %d ARM(S) MISSING. The report is INCOMPLETE and says so rather "
              "than presenting two arms as three:" % len(missing))
        for fold, arm, p in missing:
            print("   %s / %s -> %s" % (fold, arm, p))
        print("")

    out = a.out or os.path.join(a.gen, "firing_rate_by_stratum.csv")
    cols = ["leg", "fold", "arm", "country", "strat_age_band", "strat_sex",
            "strat_hh_type", "strat_day_type", "n", "n_invalid", "firing_rate",
            "scorable_at_min_n"]
    with io.open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print("written: %s  (%d rows)" % (out, len(out_rows)))

    js = os.path.splitext(out)[0] + "_summary.json"
    with io.open(js, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps({"leg": a.leg, "arms": summary,
                             "missing": [{"fold": f, "arm": ar, "path": p}
                                         for f, ar, p in missing],
                             "complete": not missing},
                            indent=2, sort_keys=True))
    print("written: %s" % js)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
