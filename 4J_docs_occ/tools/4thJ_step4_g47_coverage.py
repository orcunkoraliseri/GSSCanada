"""
Step 4 -- the ONE gate the coverage clause has never seen fall: G4.7.

THE GAP, STATED EXACTLY
-----------------------
The coverage clause FAILs on all three LOCO folds -- es (1274884), uk (1274964), it
(1281612) -- and on all three for the SAME reason:

    Gates that PASS at baseline and were NEVER felled by any perturbation: ['G4.7']

G4.7 does have a lever: `strip_eor_1pct`, training-side, and G4.7 IS credited there. But
that credit was earned on the 600-record PILOT battery, not on any LOCO fold. D-S4-6 was
ruled (a) -- one-fold credit counts, and the fold must be named every time -- so a credit
earned on the pilot is not a credit on `es`, `uk` or `it`. The three folds the paper
reports have a gate that passes and has never been shown to have power on them.

WHY THIS SCRIPT AND NOT A RE-RUN
--------------------------------
Felling G4.7 on a LOCO fold by the training-side lever costs a full ~5-hour training run
per fold, to demonstrate a detector whose rule is `n_terminated == n`. G4.7 is scored on
GENERATED text, so it can be felled on the generation side for zero GPU: strip the
terminator from the already-persisted generated set and re-score. That is the same class
of demonstration as `modal_day` and `duplicate_500`, which are also post-hoc edits of
generated text, and it runs on CPU against files that already exist for all three folds.

🔴 WHAT THIS DOES **NOT** CLAIM. It does not show that TRAINING can break termination.
It shows that G4.7's detector responds to the failure it is written to catch, on this
fold's own generated set. That is what the coverage clause asks for and it is all that is
claimed here. If the author wants the stronger training-side demonstration on a full fold,
that is a GPU cost decision and is not taken by this script.

🔴 WHY IT IS A SEPARATE FILE. `4thJ_step4_genperturb.py` carries the EXPECTED map with the
comment "pre-registered here and never edited after a result". Results are in. Adding a row
to that map now would edit a pre-registered structure after the fact, which is the move
this project forbids everywhere else. The lever therefore lives here, declared here, and
folding it into the genperturb map is an AUTHOR decision, not a tidy-up.

PRE-DECLARED, BEFORE ANY RUN
----------------------------
    must_fail        : G4.7   -- G4_7_REQUIRED_FRACTION is 1.0, so ONE non-terminated
                                 diary is enough. At --rate 0.01 of 600 that is 6.
    must_stay_clean  : G4.1   -- stripping a trailing terminator must not move a variance
                                 ratio computed over episode durations. This is NOT assumed:
                                 G4.1 is re-scored on the perturbed set and any movement is
                                 printed as UNDECLARED COLLATERAL (the FINDING 26 class).

VACUITY GUARDS
--------------
    * If G4.7 is already FAIL at baseline, the credit is VOID -- a gate down before the
      perturbation cannot be seen falling (FINDING 29's rule, applied here rather than
      re-derived).
    * If the perturbation changes 0 diaries, that is a FAIL of this script, not a negative
      result about G4.7.

Usage (CPU partition -- no GPU, does not contend with training):
  python 4thJ_step4_g47_coverage.py --fold uk \
      --generated /speed-scratch/o_iseri/4J_step4/diagnostics/generated_primary_uk.jsonl
"""

# ############################################################################
# 2026-08-20 (evening) -- DO NOT SUBMIT IS LIFTED. D-S4-7 RULED (a).
#
# The block that stood here asked one question: which G4.7 does the coverage
# clause read? The author answered it by decision, not by measurement:
#
#   G4.7  == the GENERATED sample.   <- what this script scores
#   G4.15 == the training-shard <eor> check (new ID, corpus well-formedness).
#
# 4thJ_step4_genperturb.gate_g4_7 was inspected and scores generated text, so it
# is the correct scorer under the ruling, and the V6.b two-scorers-one-ID
# collision is dissolved: the other scorer now has its own ID.
#
# 🔴 BUT READ THIS BEFORE RUNNING IT, BECAUSE THE REASON TO RUN IT HAS CHANGED.
# The coverage complaint is ALREADY DISCHARGED without this script. Under the
# re-pointed gate the epoch lines in the three fold logs ARE G4.7, and they read
#     es 1284898  600/600, 600/600     PASS PASS
#     uk 1284911  600/600, 600/600     PASS PASS
#     it 1284912  600/600, 599/600     PASS, FAIL   <- fold-level failure, no GPU
# So G4.7 has been SEEN FAILING on a LOCO fold's real output, which is what the
# clause asked for.
#
# What this script adds is strictly weaker and still worth having: that the
# detector responds to an INJECTED failure, not only to a spontaneous one.
# Report it as a demonstration of detector response. Do NOT report it as the
# answer to the coverage clause -- the it fold is that answer.
#
# 🔴 The TRAINER has not been changed yet. It still prints the shard check under
# the name G4.7. Any new run reproduces the mislabelling until that is edited.
#
# See D-S4-7 in Step4_docs/outputs_step4/proglog_step4_gates.md.
# ############################################################################


import argparse
import importlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TH = importlib.import_module("4thJ_step4_thresholds")
DIAG = importlib.import_module("4thJ_step4_diagnostics")
GP = importlib.import_module("4thJ_step4_genperturb")

STEP4 = DIAG.STEP4

# Pre-registered here, before the first run of this script, and not edited afterwards.
EXPECTED = {"strip_eor_gen": {"must_fail": ["G4.7"], "must_stay_clean": ["G4.1"]}}


def strip_eor_gen(gen_pairs, rate, rng):
    """Remove the terminator from `rate` of the generated diaries, chosen uniformly."""
    out = list(gen_pairs)
    n = len(out)
    k = max(1, int(round(rate * n)))
    idxs = rng.sample(range(n), min(k, n))
    changed = 0
    for i in idxs:
        d, t = out[i]
        stripped = t.rstrip()
        if stripped.endswith(TH.G4_7_EOR):
            out[i] = (d, stripped[: -len(TH.G4_7_EOR)].rstrip())
            changed += 1
    return out, {"selected": len(idxs), "changed": changed}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    ap.add_argument("--generated", required=True,
                    help="generated_*.jsonl written by 4thJ_step4_diagnostics.py for THIS "
                         "fold. Baseline and perturbation must be the same generation.")
    ap.add_argument("--rate", type=float, default=0.01)
    ap.add_argument("--out", default=os.path.join(STEP4, "g47_coverage"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    # V4.h -- fold and held-out country named BEFORE any verdict
    print("=" * 78)
    print("G4.7 COVERAGE DEMONSTRATION -- FOLD %s, HELD-OUT COUNTRY %s"
          % (args.fold, args.fold))
    print("lever: strip_eor_gen @ rate %.3f   pre-declared must_fail=%s must_stay_clean=%s"
          % (args.rate, EXPECTED["strip_eor_gen"]["must_fail"],
             EXPECTED["strip_eor_gen"]["must_stay_clean"]))
    print("=" * 78)

    sm = json.load(open(DIAG.MANIFEST_IN, "r", encoding="utf-8"))
    val_recs = DIAG.read_jsonl(sm["folds"][args.fold]["heldin_val"]["path"])
    real_texts = [r["text"] for r in val_recs]

    gen_recs = DIAG.read_jsonl(args.generated)
    gen_pairs = []
    for r in gen_recs:
        d = DIAG.prefix_dict(r["prompt_text"])
        if d:
            gen_pairs.append((d, r["text"]))
    print("real (held-in val): %d   generated: %d" % (len(real_texts), len(gen_pairs)))
    if not gen_pairs:
        raise SystemExit("🔴 no generated diaries parsed -- nothing to demonstrate on.")

    base_g7 = GP.gate_g4_7(gen_pairs)
    base_g1 = GP.gate_g4_1(real_texts, gen_pairs)
    print("BASELINE  G4.7 %s (%d/%d terminated)   G4.1 %s"
          % (base_g7["verdict"], base_g7["n_terminated"], base_g7["n"],
             base_g1["verdict"]))

    pert, info = strip_eor_gen(gen_pairs, args.rate, random.Random(TH.SEED))
    print("perturbation: selected %d, actually stripped %d"
          % (info["selected"], info["changed"]))
    if info["changed"] == 0:
        raise SystemExit(
            "🔴 THE PERTURBATION CHANGED NOTHING. Every selected diary was already "
            "missing its terminator, or the terminator is not %r. This is a FAIL of this "
            "script -- it is NOT a negative result about G4.7." % TH.G4_7_EOR)

    pert_g7 = GP.gate_g4_7(pert)
    pert_g1 = GP.gate_g4_1(real_texts, pert)
    print("PERTURBED G4.7 %s (%d/%d terminated)   G4.1 %s"
          % (pert_g7["verdict"], pert_g7["n_terminated"], pert_g7["n"],
             pert_g1["verdict"]))

    # ---------------------------------------------------------------- attribution
    credited = False
    if base_g7["verdict"] != "PASS":
        verdict = ("VOID -- G4.7 is already %s at baseline on this fold. A gate down "
                   "before the perturbation cannot be seen falling."
                   % base_g7["verdict"])
    elif pert_g7["verdict"] == "FAIL":
        credited = True
        verdict = ("🟢 G4.7 SEEN FALLING ON FOLD %s. Baseline PASS -> perturbed FAIL, "
                   "%d of %d diaries left unterminated. Per D-S4-6 (a) this credit names "
                   "the fold and is NOT transferable to the other two."
                   % (args.fold, pert_g7["n"] - pert_g7["n_terminated"], pert_g7["n"]))
    else:
        verdict = ("🔴 G4.7 DID NOT FALL although %d diaries were left unterminated. "
                   "G4_7_REQUIRED_FRACTION is %.2f, so this should be impossible. The "
                   "gate, not the perturbation, is what to read next."
                   % (info["changed"], TH.G4_7_REQUIRED_FRACTION))
    print(verdict)

    # must_stay_clean, checked rather than asserted
    collateral = None
    if base_g1["verdict"] == "PASS" and pert_g1["verdict"] != "PASS":
        collateral = ("🔴 UNDECLARED COLLATERAL: G4.1 was PASS at baseline and is %s under "
                      "strip_eor_gen. The terminator is reaching the episode parse. This "
                      "is the FINDING 26 class and it weakens the attribution above."
                      % pert_g1["verdict"])
    elif base_g1["verdict"] != "PASS":
        collateral = ("G4.1 is %s at baseline on this fold, so must_stay_clean is NOT "
                      "ASSESSABLE here. Recorded, not silently passed."
                      % base_g1["verdict"])
    else:
        collateral = "G4.1 stayed PASS under the perturbation, as declared."
    print(collateral)

    out = {"gate": "G4.7", "fold": args.fold, "lever": "strip_eor_gen",
           "rate": args.rate, "generated_file": args.generated,
           "pre_declared": EXPECTED["strip_eor_gen"],
           "baseline": {"G4.7": base_g7, "G4.1": base_g1},
           "perturbed": {"G4.7": pert_g7, "G4.1": pert_g1},
           "n_changed": info["changed"], "credited_seen_falling": credited,
           "verdict_text": verdict, "must_stay_clean_note": collateral,
           "scope": "generation-side demonstration only; does NOT show that training can "
                    "break termination"}
    path = os.path.join(args.out, "g47_coverage_%s.json" % args.fold)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
