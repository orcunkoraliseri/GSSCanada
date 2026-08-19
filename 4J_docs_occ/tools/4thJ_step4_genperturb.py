"""
Step 4 -- the GENERATION-SIDE perturbations, and the two gates they must fell.

The other nine perturbations in `4thJ_04_finetuneLLM_val.md` are training-side and live
as `--perturbation` flags on the trainer. These four act on an ALREADY-GENERATED set,
which is why they are here: a perturbation and its baseline must be provably the SAME
generation, not two sampling runs that differ for reasons nobody controlled.

  modal_day              replace every diary in a stratum with that stratum's modal day
                         -> G4.1 must FAIL at the LOWER end.  G4.7 must stay clean.
  duplicate_500          duplicate one diary 500x inside a stratum
                         -> G4.1 lower.  G4.3 stays clean (it never sees this set).
  blank_evening          destroy the conditioning of the 18:00-23:00 slots ONLY
                         -> G4.4 must FAIL on the evening window and STAY CLEAN on the
                            morning window.
  within_stratum_shuffle permute diaries inside each stratum cell
                         -> G4.1 must STAY CLEAN. That is the whole point of G4.12:
                            the shuffle preserves within-stratum variance exactly, so a
                            battery that only watches G4.1 cannot see it at all.
  null                   change nothing -> nothing may move.

🔴 blank_evening is an INTERPRETATION and is recorded as one. The val doc says "blank the
evening slots' conditioning only", but this corpus conditions on a single whole-day
prefix -- there is no slot-wise conditioning channel to blank. The executable form used
here permutes the STRATUM LABELS attached to the evening slots and leaves every other
slot's labels intact, which destroys evening MI while provably leaving morning MI
untouched. That is the same failure the clause describes, reached by the only lever this
record format actually has.

Usage:
  python 4thJ_step4_genperturb.py --fold es --generated <generated_*.jsonl> \
      --perturbation all
"""

import argparse
import importlib
import json
import os
import random
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TH = importlib.import_module("4thJ_step4_thresholds")
DIAG = importlib.import_module("4thJ_step4_diagnostics")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")

PERTURBATIONS = ["null", "modal_day", "duplicate_500", "blank_evening",
                 "within_stratum_shuffle"]

# what each perturbation MUST fell, pre-registered here and never edited after a result
EXPECTED = {
    "null":                   {"must_fail": [],           "must_stay_clean": ["G4.1", "G4.4", "G4.7"]},
    "modal_day":              {"must_fail": ["G4.1"],     "must_stay_clean": ["G4.7"]},
    "duplicate_500":          {"must_fail": ["G4.1"],     "must_stay_clean": []},
    "blank_evening":          {"must_fail": ["G4.4"],     "must_stay_clean": []},
    "within_stratum_shuffle": {"must_fail": [],           "must_stay_clean": ["G4.1"]},
}


def gate_g4_1(real_texts, gen_texts):
    real_by, gen_by = defaultdict(list), defaultdict(list)
    for t in real_texts:
        d = DIAG.prefix_dict(t)
        v = at_home_share(t)
        if d and v is not None:
            real_by[DIAG.stratum_key(d)].append(v)
    for d, t in gen_texts:
        v = at_home_share(t)
        if d and v is not None:
            gen_by[DIAG.stratum_key(d)].append(v)
    rows = []
    for s, rv in real_by.items():
        gv = gen_by.get(s, [])
        if len(rv) < TH.G4_1_MIN_STRATUM_N or len(gv) < TH.G4_1_MIN_STRATUM_N:
            continue
        vr, vg = float(np.var(rv)), float(np.var(gv))
        if vr <= 0:
            continue
        rows.append({"stratum": "|".join(s), "vr": vg / vr,
                     "n_real": len(rv), "n_gen": len(gv)})
    if len(rows) < TH.V4_A_MIN_STRATA:
        return {"gate": "G4.1", "verdict": "FAIL",
                "reason": "V4.a: only %d strata reach N >= %d on BOTH sides. A variance "
                          "gate evaluated on that many strata is satisfied by nothing, so "
                          "it FAILs rather than skipping."
                          % (len(rows), TH.G4_1_MIN_STRATUM_N),
                "n_scorable_strata": len(rows)}
    low = [r for r in rows if r["vr"] < TH.G4_1_VR_LOW]
    high = [r for r in rows if r["vr"] > TH.G4_1_VR_HIGH]
    return {"gate": "G4.1", "verdict": "PASS" if not low and not high else "FAIL",
            "statistic": TH.G4_1_STATISTIC, "n_scorable_strata": len(rows),
            "n_below_band_COLLAPSE_END": len(low), "n_above_band": len(high),
            "which_end": ("lower (collapse)" if low and not high else
                          "upper" if high and not low else
                          "both" if low and high else "none"),
            "min_vr": min(r["vr"] for r in rows), "max_vr": max(r["vr"] for r in rows)}


def at_home_share(text):
    try:
        _, body = DIAG.split_prefix_body(text)
    except ValueError:
        return None
    eps = DIAG.parse_episodes(body)
    total = sum(e[0] for e in eps)
    if total <= 0:
        return None
    home = sum(e[0] for e in eps if e[3] == TH.LOC_AT_HOME)
    return home / float(total)


def gate_g4_4(real_pairs, gen_pairs, evening_label_permuted=False, rng=None):
    mi_real = DIAG.mi_curve(real_pairs)
    if evening_label_permuted:
        lo, hi = TH.G4_4_EVENING_WINDOW
        s0, s1 = lo // TH.G4_4_SLOT_MINUTES, hi // TH.G4_4_SLOT_MINUTES
        mi_gen = mi_curve_with_evening_labels_permuted(gen_pairs, s0, s1, rng)
    else:
        mi_gen = DIAG.mi_curve(gen_pairs)
    ev_r = DIAG.window_mean(mi_real, TH.G4_4_EVENING_WINDOW)
    ev_g = DIAG.window_mean(mi_gen, TH.G4_4_EVENING_WINDOW)
    mo_r = DIAG.window_mean(mi_real, TH.G4_4_MORNING_WINDOW)
    mo_g = DIAG.window_mean(mi_gen, TH.G4_4_MORNING_WINDOW)
    ev_ratio = ev_g / ev_r if ev_r else float("nan")
    mo_ratio = mo_g / mo_r if mo_r else float("nan")
    ev_v = "PASS" if ev_ratio >= TH.G4_4_MIN_MI_RATIO else "FAIL"
    mo_v = "PASS" if mo_ratio >= TH.G4_4_MIN_MI_RATIO else "FAIL"
    return {"gate": "G4.4", "verdict": "PASS" if ev_v == "PASS" and mo_v == "PASS" else "FAIL",
            "evening_window_1800_2300": {"ratio": ev_ratio, "verdict": ev_v,
                                         "mi_real": ev_r, "mi_generated": ev_g},
            "morning_window_0600_1100": {"ratio": mo_ratio, "verdict": mo_v,
                                         "mi_real": mo_r, "mi_generated": mo_g},
            "min_ratio": TH.G4_4_MIN_MI_RATIO,
            "note": "the two windows are scored and reported SEPARATELY, because "
                    "'demographically appropriate mornings and generic evenings' is a "
                    "failure that a single averaged number hides"}


def mi_curve_with_evening_labels_permuted(pairs, s0, s1, rng):
    attrs = [f for f in TH.PREFIX_FIELDS if f != "country"]
    slots = defaultdict(lambda: defaultdict(list))
    for d, text in pairs:
        for slot, act in DIAG.slot_activities(text).items():
            for a in attrs:
                slots[slot][a].append((d[a], act))
    per_slot = {}
    for slot, byattr in slots.items():
        vals = []
        for a, pl in byattr.items():
            if len(pl) < 30:
                continue
            xs = [p[0] for p in pl]
            ys = [p[1] for p in pl]
            if s0 <= slot < s1:
                xs = xs[:]
                rng.shuffle(xs)   # destroy the association in THIS window only
            vals.append(DIAG.mutual_information(xs, ys))
        if vals:
            per_slot[slot] = float(np.mean(vals))
    return per_slot


def gate_g4_7(gen_texts):
    n = len(gen_texts)
    ok = sum(1 for _d, t in gen_texts if t.rstrip().endswith(TH.G4_7_EOR))
    return {"gate": "G4.7", "verdict": "PASS" if n and ok == n else "FAIL",
            "n": n, "n_terminated": ok}


def apply_perturbation(name, gen_pairs, rng):
    if name == "null":
        return list(gen_pairs), {"changed": 0}
    by = defaultdict(list)
    for i, (d, t) in enumerate(gen_pairs):
        by[DIAG.stratum_key(d)].append(i)
    out = list(gen_pairs)

    if name == "modal_day":
        changed = 0
        for k, idxs in by.items():
            if len(idxs) < 2:
                continue
            counts = defaultdict(int)
            for i in idxs:
                counts[gen_pairs[i][1]] += 1
            modal = max(counts.items(), key=lambda kv: kv[1])[0]
            for i in idxs:
                if out[i][1] != modal:
                    changed += 1
                out[i] = (gen_pairs[i][0], modal)
        return out, {"changed": changed, "n_strata_touched": len(by)}

    if name == "duplicate_500":
        big = max(by.items(), key=lambda kv: len(kv[1]))
        k, idxs = big
        src = gen_pairs[idxs[0]][1]
        n_dup = min(500, len(idxs))
        for i in idxs[:n_dup]:
            out[i] = (gen_pairs[i][0], src)
        return out, {"changed": n_dup, "stratum": "|".join(k),
                     "note": "capped at the cell size; the val doc says 500x and the "
                             "cell may be smaller, so the actual count is reported"}

    if name == "within_stratum_shuffle":
        shuffled, n_moved, n_stuck = DIAG.within_stratum_permutation(
            gen_pairs, lambda it: DIAG.stratum_key(it[0]), rng)
        out = [(d, s[1]) for (d, _t), s in zip(gen_pairs, shuffled)]
        return out, {"changed": n_moved, "singletons_could_not_move": n_stuck}

    if name == "blank_evening":
        # handled inside gate_g4_4 via evening_label_permuted -- the text is untouched
        return list(gen_pairs), {"changed": 0,
                                 "note": "acts on the MI estimator's label association "
                                         "for the evening window only; the diary text is "
                                         "deliberately not modified"}
    raise SystemExit("unknown perturbation %s" % name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    ap.add_argument("--generated", required=True,
                    help="generated_*.jsonl written by 4thJ_step4_diagnostics.py")
    ap.add_argument("--perturbation", default="all")
    ap.add_argument("--out", default=os.path.join(STEP4, "genperturb"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("=" * 78)
    print("GENERATION-SIDE PERTURBATIONS -- FOLD %s, HELD-OUT COUNTRY %s"
          % (args.fold, args.fold))   # V4.h, before any verdict
    print("=" * 78)

    sm = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    val_recs = DIAG.read_jsonl(sm["folds"][args.fold]["heldin_val"]["path"])
    real_texts = [r["text"] for r in val_recs]
    real_pairs = [(DIAG.prefix_dict(t), t) for t in real_texts]
    real_pairs = [(d, t) for d, t in real_pairs if d]

    gen_recs = DIAG.read_jsonl(args.generated)
    gen_pairs = []
    for r in gen_recs:
        d = DIAG.prefix_dict(r["prompt_text"])
        if d:
            gen_pairs.append((d, r["text"]))
    print("real (held-in val): %d   generated: %d" % (len(real_pairs), len(gen_pairs)))

    names = PERTURBATIONS if args.perturbation == "all" else [args.perturbation]
    results = {}
    for name in names:
        rng = random.Random(TH.SEED)
        pert, info = apply_perturbation(name, gen_pairs, rng)
        g1 = gate_g4_1(real_texts, pert)
        g4 = gate_g4_4(real_pairs, pert,
                       evening_label_permuted=(name == "blank_evening"),
                       rng=random.Random(TH.SEED))
        g7 = gate_g4_7(pert)
        verdicts = {"G4.1": g1["verdict"], "G4.4": g4["verdict"], "G4.7": g7["verdict"]}

        exp = EXPECTED[name]
        fell = [g for g, v in verdicts.items() if v == "FAIL"]
        attribution = []
        for g in exp["must_fail"]:
            attribution.append("%s expected FAIL -> %s %s"
                               % (g, verdicts.get(g),
                                  "AS EXPECTED" if verdicts.get(g) == "FAIL"
                                  else "🔴 DID NOT FALL"))
        for g in exp["must_stay_clean"]:
            attribution.append("%s expected clean -> %s %s"
                               % (g, verdicts.get(g),
                                  "AS EXPECTED" if verdicts.get(g) == "PASS"
                                  else "🔴 UNEXPECTED FALL -- FINDING"))
        results[name] = {"info": info, "verdicts": verdicts, "fell": fell,
                         "expected": exp, "attribution": attribution,
                         "G4.1": g1, "G4.4": g4, "G4.7": g7}
        print()
        print("-- %s -- %s" % (name, info))
        for line in attribution:
            print("   " + line)
        print("   verdicts: %s" % verdicts)

    # coverage clause
    base = results.get("null", {}).get("verdicts", {})
    passing_at_baseline = [g for g, v in base.items() if v == "PASS"]
    never_felled = [g for g in passing_at_baseline
                    if not any(g in r["fell"] for n, r in results.items() if n != "null")]
    coverage = "PASS" if not never_felled else "FAIL"
    print()
    print("=" * 78)
    print("BASELINE (null) verdicts: %s" % base)
    print("Gates that PASS at baseline and were NEVER felled by any perturbation: %s"
          % never_felled)
    print("COVERAGE CLAUSE VERDICT: %s" % coverage)
    if never_felled:
        print("🔴 A gate that passes and cannot be made to fall has not been shown to "
              "have power. This is a FAIL of the probe, not of the model.")
    print("=" * 78)

    path = os.path.join(args.out, "genperturb_%s.json" % args.fold)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"fold": args.fold, "generated": args.generated,
                   "results": results, "baseline": base,
                   "never_felled": never_felled, "coverage": coverage},
                  fh, indent=2, sort_keys=True, default=str)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
