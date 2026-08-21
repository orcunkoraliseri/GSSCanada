"""
Step 4 -- G4.1's MISSING NOISE FLOOR, measured from ONE FROZEN ADAPTER.

WHY THIS EXISTS
---------------
Every "resolved / not resolved" call made about G4.1 in this project so far -- FINDING 37
refusing a PASS at 0.61x the spread, the D-S4-5 entries refusing both the FAIL and the
PASS on fold `uk` -- leans on a spread taken from a REPLICATE PAIR OF TRAINING RUNS. That
number confounds two different things:

    (1) sampling variance   -- G4.1 is computed on ancestrally sampled text
                               (do_sample=True, temperature=1.0, top_p=1.0), so two reads
                               of the SAME weights differ.
    (2) weight divergence   -- two training runs at the same seed are not bit-identical on
                               a GPU, so the weights themselves differ.

G4.6 has a repeat-noise floor (0.000e+00, two identical unmerged forward passes). G4.1 has
never had one. This script supplies it by holding (2) at exactly zero: ONE adapter, loaded
once, never trained, generation repeated under K different torch seeds. Whatever spread
comes out is (1) alone, and it is a LOWER BOUND on the spread of any two training runs.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
* It does not train. It is generation only -- roughly the cost of one G4.1 probe per seed.
* It does not move a band, re-score a fold, or produce a verdict for any fold. Its output
  is a RESOLUTION, to be quoted next to G4.1 readings, never in place of one.
* It does not re-implement G4.1. It imports the TRAINER's own `gate_g4_1` and the
  TRAINER's own `generate_samples`, so the number it produces is on the same basis as the
  readings it is meant to calibrate. A reimplementation would measure a different gate.

THE ONE THING THAT MAKES THE MEASUREMENT VALID
----------------------------------------------
The prefix draw must be IDENTICAL across seeds, or this measures the draw as well as the
sampling. `generate_samples` opens with `rng = random.Random(TH.SEED)` -- a FRESH generator
seeded from the constant on every call -- so the stratified draw is already reproducible
and is NOT affected by torch.manual_seed. Only `model.generate` consumes the torch RNG.
That is asserted at run time below, not assumed: the first seed's draw is recorded and
every later seed's draw is compared against it, and a mismatch is a hard FAIL.

VACUITY GUARD (V4-style, and it has teeth)
------------------------------------------
If two seeds produce BYTE-IDENTICAL generated text, the seed is not reaching the sampler
and a spread of 0.000 would be an artefact rather than a result -- exactly the "gate that
cannot be seen failing" problem this project keeps hitting. That case FAILS the run and
says so; it is never reported as "G4.1 has no sampling noise".

Usage (compute node only -- this needs a GPU):
  python 4thJ_step4_g41_seedfloor.py --fold uk \
      --adapter /speed-scratch/o_iseri/4J_step4/runs/leg4_primary_fold_uk/adapter \
      --seeds 13,101,1009,7919,104729
"""

import argparse
import importlib
import json
import os
import statistics
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TH = importlib.import_module("4thJ_step4_thresholds")
DIAG = importlib.import_module("4thJ_step4_diagnostics")
TR = importlib.import_module("4thJ_step4_train")

STEP4 = DIAG.STEP4
MANIFEST_IN = DIAG.MANIFEST_IN
STAGED = DIAG.STAGED


def spread(vals):
    """max - min. Reported alongside stdev because with K = 5 the range is the honest
    statistic and a stdev over five points invites a confidence it has not earned."""
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        return None
    return max(vals) - min(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True, choices=["es", "uk", "it"])
    ap.add_argument("--adapter", required=True,
                    help="peft adapter dir. ONE adapter, used for every seed. Required: "
                         "a base-model run would measure the base model's sampling noise, "
                         "which is not the quantity G4.1 readings need calibrating "
                         "against.")
    ap.add_argument("--run-type", default="primary",
                    choices=["pilot", "primary", "ceiling", "qwen", "perturb"])
    ap.add_argument("--leg", type=int, default=4, choices=[4, 5])
    ap.add_argument("--seeds", default="13,101,1009,7919,104729",
                    help="comma-separated torch seeds. Fixed defaults, written here "
                         "BEFORE any result, so the seed set cannot be chosen to widen "
                         "or narrow the spread.")
    ap.add_argument("--gen-n", type=int, default=600)
    ap.add_argument("--gen-stratified-k", type=int, default=6)
    ap.add_argument("--gen-batch", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=1200)
    ap.add_argument("--out", default=os.path.join(STEP4, "g41_seedfloor"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if len(seeds) < 3:
        raise SystemExit("at least 3 seeds: a spread over two points is a difference, "
                         "not a spread.")

    # V4.h -- fold and held-out country named BEFORE any number exists
    print("=" * 78)
    print("G4.1 SAMPLING-NOISE FLOOR -- FOLD %s, HELD-OUT COUNTRY %s" % (args.fold, args.fold))
    print("ONE FROZEN ADAPTER, %d SEEDS, NO TRAINING. Weight divergence = 0 by construction."
          % len(seeds))
    print("seeds (fixed in the source before any result): %s" % seeds)
    print("=" * 78)

    sm = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    fold_m = sm["folds"][args.fold]
    val_recs = DIAG.read_jsonl(fold_m["heldin_val"]["path"])
    # FINDING 11, and it must match the trainer exactly: G4.1's real side is the whole
    # held-in set, not the validation split.
    train_recs = DIAG.read_jsonl(fold_m["train"]["path"])
    real_ref = [{"text": r["text"], "country": r.get("country")}
                for r in train_recs + val_recs]
    real_texts = [r["text"] for r in real_ref]
    print("prefix pool (held-in val): %d   real reference set: %d"
          % (len(val_recs), len(real_ref)))

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    staged = json.load(open(STAGED, "r", encoding="utf-8"))
    repo = DIAG.MODEL_FOR["pilot"] if args.leg == 4 else DIAG.MODEL_FOR[args.run_type]
    rev = next((r["revision"] for r in staged["repos"] if r["repo_id"] == repo), None)
    if rev is None:
        raise SystemExit("no staged revision for %s" % repo)
    tokenizer = AutoTokenizer.from_pretrained(repo, revision=rev)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev,
                                                 torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, args.adapter)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()
    print("base %s @ %s + adapter %s" % (repo, rev, args.adapter))
    if device != "cuda":
        print("🔴 NO GPU. This will run, and it will take hours. Not an error, but it "
              "means the job was submitted to the wrong partition.")

    rows, first_draw, first_texts = [], None, None
    for seed in seeds:
        torch.manual_seed(seed)
        if device == "cuda":
            torch.cuda.manual_seed_all(seed)
        sample, gen_texts = TR.generate_samples(
            model, tokenizer, val_recs, device, args.gen_n,
            max_new_tokens=args.max_len, stratified_k=args.gen_stratified_k,
            gen_batch=args.gen_batch, ref_recs=real_ref)

        # ---- the draw must be identical across seeds, or this measures two things ----
        draw_key = [r["text"] for r in sample]
        if first_draw is None:
            first_draw = draw_key
        elif draw_key != first_draw:
            raise SystemExit(
                "🔴 THE PREFIX DRAW MOVED BETWEEN SEEDS. generate_samples is supposed to "
                "reseed its own random.Random(TH.SEED) on every call, so torch.manual_seed "
                "cannot reach it. It did reach it. Every number this script would print "
                "would confound sampling noise with draw noise. This is a FINDING, not a "
                "flaky run -- stop and read generate_samples.")

        # ---- vacuity guard: a seed that does not reach the sampler is not a result ----
        if first_texts is None:
            first_texts = gen_texts
        elif gen_texts == first_texts:
            raise SystemExit(
                "🔴 VACUITY: seed %d produced byte-identical text to seed %d. The seed is "
                "not reaching model.generate, so a spread of 0.000 would be an artefact of "
                "the harness, not a property of G4.1. FAIL rather than report a floor of "
                "zero." % (seed, seeds[0]))

        g1 = TR.gate_g4_1(real_texts, gen_texts)
        g1["seed"] = seed
        rows.append(g1)
        print("seed %-7d G4.1 %-4s  %d below / %d above  worst %.3f/%.3f  end=%s  "
              "strata=%d"
              % (seed, g1["verdict"],
                 g1.get("n_below_band_COLLAPSE_END", -1), g1.get("n_above_band", -1),
                 g1.get("worst_low", float("nan")), g1.get("worst_high", float("nan")),
                 g1.get("which_end", "?"), g1.get("n_scorable_strata", -1)),
              flush=True)

    # ------------------------------------------------------------------ the floor
    lows = [r.get("worst_low") for r in rows]
    highs = [r.get("worst_high") for r in rows]
    verdicts = [r["verdict"] for r in rows]
    s_low, s_high = spread(lows), spread(highs)

    print("=" * 78)
    print("G4.1 SAMPLING-NOISE FLOOR, FOLD %s -- ONE ADAPTER, %d SEEDS, NO TRAINING"
          % (args.fold, len(seeds)))
    print("  worst_low : %s" % ["%.3f" % v for v in lows])
    print("  worst_high: %s" % ["%.3f" % v for v in highs])
    print("  SPREAD (max-min)  worst_low = %.3f   worst_high = %.3f" % (s_low, s_high))
    if len(lows) >= 3:
        print("  stdev             worst_low = %.3f   worst_high = %.3f"
              % (statistics.stdev(lows), statistics.stdev(highs)))
    print("  verdicts: %s" % verdicts)

    # 🔴 The result that would matter most, and it is named here before it is seen.
    if len(set(verdicts)) > 1:
        print("🔴 THE VERDICT ITSELF IS NOT STABLE UNDER RESEEDING. The same frozen "
              "adapter both PASSES and FAILS G4.1 depending only on the sampler's seed. "
              "That is a property of the gate, not of any fold, and it means NO single "
              "G4.1 reading anywhere in Step 4 -- including every D-S4-5 verdict "
              "checkpoint -- is reportable without this spread beside it.")
    else:
        print("The verdict is stable across all %d seeds (%s). The spread above still "
              "bounds what any single reading can resolve." % (len(seeds), verdicts[0]))

    print("🔴 READING RULE, registered here rather than after the numbers: this spread is "
          "a LOWER BOUND on the run-to-run spread of two TRAINED replicates, because it "
          "holds weight divergence at exactly zero. A G4.1 difference smaller than it is "
          "not resolved by any argument.")
    print("=" * 78)

    out = {"gate": "G4.1", "measurement": "sampling-noise floor, frozen adapter",
           "fold": args.fold, "adapter": args.adapter, "base_repo": repo,
           "base_revision": rev, "seeds": seeds, "gen_n": args.gen_n,
           "stratified_k": args.gen_stratified_k,
           "weight_divergence": "zero by construction -- one adapter, never trained",
           "per_seed": rows,
           "spread_worst_low": s_low, "spread_worst_high": s_high,
           "verdict_stable_under_reseed": len(set(verdicts)) == 1,
           "is_a_verdict_for_any_fold": False,
           "note": "a resolution, to be quoted next to G4.1 readings and never in place "
                   "of one"}
    path = os.path.join(args.out, "g41_seedfloor_%s.json" % args.fold)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
