#!/usr/bin/env python
"""D-S4-12 arm (a) -- SCORER STABILITY for G4.4.

Author ruling 2026-08-24, option (a). The question: did G4.4 flip FAIL -> PASS on the
`es` fold because the D-S4-8 `eos_token_id` repair changed the GENERATED TEXT (H1), or
because the scorer itself is unstable (H0)?

This arm holds the text fixed and re-runs the scorer on the PRE-REPAIR generated set that
was deliberately kept as a control. No model is loaded, no GPU is used, nothing is
generated: the same estimator, the same real reference, the same frozen thresholds.

PRE-REGISTERED PREDICTION (written before the run): the evening ratio reproduces the
recorded pre-repair value 0.544 within +/- 0.01. If it does, the scorer is stable and the
flip cannot be attributed to it. If it does not, H0 is live and the flip is uninterpretable.

Nothing here is a gate verdict. `4thJ_step4_thresholds.py` is FROZEN and only read.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib
DIAG = importlib.import_module("4thJ_step4_diagnostics")
TH = importlib.import_module("4thJ_step4_thresholds")

PRED_RATIO = 0.544
PRED_TOL = 0.01


def score_g4_4(real_pairs, gen_pairs):
    mi_real = DIAG.mi_curve(real_pairs)
    mi_gen = DIAG.mi_curve(gen_pairs)
    out = {}
    for name, w in (("evening_window_1800_2300", TH.G4_4_EVENING_WINDOW),
                    ("morning_window_0600_1100", TH.G4_4_MORNING_WINDOW)):
        r = DIAG.window_mean(mi_real, w)
        g = DIAG.window_mean(mi_gen, w)
        ratio = g / r if r else float("nan")
        out[name] = {"mi_real": r, "mi_generated": g, "ratio": ratio,
                     "verdict": "PASS" if ratio >= TH.G4_4_MIN_MI_RATIO else "FAIL"}
    out["verdict"] = ("PASS" if out["evening_window_1800_2300"]["verdict"] == "PASS"
                      and out["morning_window_0600_1100"]["verdict"] == "PASS" else "FAIL")
    out["min_ratio"] = TH.G4_4_MIN_MI_RATIO
    return out


def load_gen(path):
    pairs = []
    n = 0
    for line in open(path, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        n += 1
        r = json.loads(line)
        d = DIAG.prefix_dict(r["prompt_text"])
        if d:
            pairs.append((d, r["text"]))
    return pairs, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    ap.add_argument("--generated", required=True, nargs="+",
                    help="one or more generated_*.jsonl; each is scored separately")
    ap.add_argument("--out", required=True)
    # arm (a) makes the 0.544 stability call on its FIRST file; arm (b) uses the same
    # scorer only to put two seeds through one estimator and must NOT be read as a
    # stability call, so the mode is explicit rather than positional.
    ap.add_argument("--mode", default="stability", choices=["stability", "spread"])
    args = ap.parse_args()

    print("=" * 78)
    print("D-S4-12 ARM (a) -- G4.4 SCORER STABILITY, fold %s" % args.fold)
    print("no model, no generation: the text is held FIXED and only the scorer re-runs")
    print("pre-registered prediction: evening ratio = %.3f +/- %.3f on the PRE-REPAIR set"
          % (PRED_RATIO, PRED_TOL))
    print("=" * 78)

    sm = json.load(open(DIAG.MANIFEST_IN, "r", encoding="utf-8"))
    fold_m = sm["folds"][args.fold]
    val_recs = DIAG.read_jsonl(fold_m["heldin_val"]["path"])
    # FINDING 11: the real MI curve is the WHOLE held-in set, exactly as the diagnostics
    # run that produced the recorded numbers. A different real side would not be a re-run.
    real_ref = DIAG.read_jsonl(fold_m["train"]["path"]) + val_recs
    real_pairs = [(DIAG.prefix_dict(r["text"]), r["text"]) for r in real_ref]
    real_pairs = [(d, t) for d, t in real_pairs if d]
    print("real reference: %d diaries (%d with a readable prefix)"
          % (len(real_ref), len(real_pairs)))

    results = []
    for gp in args.generated:
        gen_pairs, n_lines = load_gen(gp)
        g4 = score_g4_4(real_pairs, gen_pairs)
        ev = g4["evening_window_1800_2300"]["ratio"]
        mo = g4["morning_window_0600_1100"]["ratio"]
        print("\n-- %s" % gp)
        print("   %d lines, %d scorable" % (n_lines, len(gen_pairs)))
        print("   G4.4 %s  evening %.3f (%s)  morning %.3f (%s)"
              % (g4["verdict"], ev, g4["evening_window_1800_2300"]["verdict"],
                 mo, g4["morning_window_0600_1100"]["verdict"]))
        results.append({"generated": gp, "n_lines": n_lines,
                        "n_scorable": len(gen_pairs), "G4.4": g4})

    # the stability call is made on the FIRST file only, which the caller must point at
    # the pre-repair control. It is stated explicitly so a mis-ordered call is visible.
    if args.mode == "spread":
        evs = [r["G4.4"]["evening_window_1800_2300"]["ratio"] for r in results]
        mos = [r["G4.4"]["morning_window_0600_1100"]["ratio"] for r in results]
        spread_ev, spread_mo = max(evs) - min(evs), max(mos) - min(mos)
        verdict = ("SEED SPREAD -- evening %.4f, morning %.4f over %d generations. "
                   "Pre-registered expectation: < 0.10." % (spread_ev, spread_mo, len(evs)))
        print()
        print(verdict)
        res = {"decision": "D-S4-12 arm (b), author ruling 2026-08-24",
               "gate": "G4.4", "fold": args.fold, "mode": "spread",
               "expected_spread_below": 0.10,
               "evening_ratios": evs, "morning_ratios": mos,
               "spread_evening": spread_ev, "spread_morning": spread_mo,
               "real_reference_diaries": len(real_ref), "runs": results,
               "spread_verdict": verdict,
               "note": ("REPORTED, NOT A GATE VERDICT. A second seed exists to bound "
                        "sampling noise; it never replaces the frozen-seed result.")}
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        print("written: %s" % args.out)
        return

    first = results[0]
    ev0 = first["G4.4"]["evening_window_1800_2300"]["ratio"]
    within = abs(ev0 - PRED_RATIO) <= PRED_TOL
    verdict = ("SCORER STABLE -- the pre-repair evening ratio reproduces at %.4f, "
               "|delta| = %.4f <= %.3f. H0 (scorer drift) does not explain the flip."
               % (ev0, abs(ev0 - PRED_RATIO), PRED_TOL)) if within else (
              "🔴 SCORER NOT STABLE -- the pre-repair evening ratio re-reads %.4f, "
              "|delta| = %.4f > %.3f against the recorded %.3f. The FAIL -> PASS flip "
              "is NOT interpretable as a text change until this is explained."
              % (ev0, abs(ev0 - PRED_RATIO), PRED_TOL, PRED_RATIO))
    print("\n" + verdict)

    res = {"decision": "D-S4-12 arm (a), author ruling 2026-08-24",
           "gate": "G4.4", "fold": args.fold,
           "prediction": {"evening_ratio": PRED_RATIO, "tolerance": PRED_TOL,
                          "declared": "before the run"},
           "real_reference_diaries": len(real_ref),
           "runs": results,
           "stability_verdict": verdict,
           "note": ("REPORTED, NOT A GATE VERDICT. This arm cannot change any recorded "
                    "G4.4 result; it says only whether the scorer is the explanation.")}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("written: %s" % args.out)


if __name__ == "__main__":
    main()
