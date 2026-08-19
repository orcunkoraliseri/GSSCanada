#!/usr/bin/env python
"""
D-S4-3 (author ruling, 2026-08-19) -- the G4.6 alpha-sweep.

WHY THIS EXISTS. `G4.6` FAILs at baseline on every trained adapter with
`max_logit_diff` around 2.5e-4 to 4.7e-4 against a 1e-4 band, and the two
explanations offered so far are both dead:

  * bf16 storage rounding -- DEAD (FINDING 27). `4thJ_step4_train.py` calls
    `model.float()` BEFORE the measurement, so the merge already happens in
    float32 storage. The ruling that was on the table ("upcast for the merge")
    was already in force and would have changed nothing.
  * run-to-run nondeterminism -- DEAD (FINDING 21). The repeat floor is
    0.000e+00. But that control compares the SAME kernel with the SAME reduction
    order against itself, so zero was guaranteed by construction and it bounds
    nothing about the quantity G4.6 measures (FINDING 27b).

What is left is RE-ASSOCIATION. The two things G4.6 differences are not two runs
of one computation, they are two DIFFERENT computations that agree in exact
arithmetic:

    unmerged:  x.W  +  s.((x.A).B)      one full GEMM, one rank-r path, one add
    merged:    x.(W + s.BA)             one full GEMM on a different matrix

Their float32 rounding differs, and that difference should scale with the
magnitude of the delta being folded in.

WHAT THIS MEASURES. Scale `B` by alpha, so the merged delta becomes alpha.s.BA,
and measure the gate's own statistic at each alpha:

  * drift falls LINEARLY with alpha  -> the residual IS the delta's own
    re-association error. It cannot be engineered away, it is proportional to
    how much the adapter learned, and `G4.6` at 1e-4 is unsatisfiable for any
    adapter that trained -- exactly as it is satisfiable only for one that did
    not (`freeze_adapter`).
  * drift PLATEAUS at small alpha    -> there is a constant floor that has
    nothing to do with the adapter, and that floor is the number the band should
    be ruled against.

NOTHING HERE CHANGES A VERDICT. No band is moved, no gate is re-pointed, no
`EXPECTED` row is touched. This script writes a JSON and a table and stops.
The AUTHOR rules afterwards, with the number in hand.

Two controls are built in and both are cheap:
  * alpha = 0 must give EXACTLY 0.0 -- `B = 0` means `W + 0 = W` bitwise, which
    is the `freeze_adapter` result reproduced from the other direction. Anything
    else means this script is wrong, not that the merge is.
  * alpha = 1 is measured TWICE, first and last. `(W + D) - D` is not bitwise
    `W` in floating point, so a sweep that merges and unmerges repeatedly can
    contaminate its own later readings. The repeat says by how much. If the two
    alpha = 1 rows disagree by anything near the effect being measured, the
    sweep is inconclusive and must be reported as such.

usage:
    python 4thJ_step4_g46_alpha_sweep.py --fold es \
        --adapter /speed-scratch/o_iseri/4J_step4/runs_perturb/leg4_perturb_fold_es/adapter
"""

import argparse
import importlib
import json
import os
import random
import sys

import torch

TH = importlib.import_module("4thJ_step4_thresholds")
TR = importlib.import_module("4thJ_step4_train")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--alphas", default="1,0.1,0.01,0.001,0,1")
    ap.add_argument("--max-len", type=int, default=1280)
    ap.add_argument("--out", default=os.path.join(STEP4, "g46_alpha_sweep.json"))
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    # The base repo and revision are read from the run manifest that sits beside the
    # adapter, never guessed and never re-derived from a config -- an alpha sweep run
    # against a different checkpoint from the one that produced the FAIL would be
    # measuring a different model and saying so about this one.
    run_dir = os.path.dirname(os.path.abspath(args.adapter.rstrip("/\\")))
    mans = [f for f in os.listdir(run_dir) if f.startswith("run_manifest_")]
    if len(mans) != 1:
        TR.fail("expected exactly one run_manifest_*.json beside the adapter, found %d "
                "in %s" % (len(mans), run_dir))
    man = json.load(open(os.path.join(run_dir, mans[0]), "r", encoding="utf-8"))
    repo, rev = man["base_repo"], man["base_revision"]
    print("adapter   %s" % args.adapter)
    print("base      %s @ %s" % (repo, rev))
    print("manifest  %s (run %s, perturbation %r)"
          % (mans[0], man.get("run"), man.get("perturbation")))

    shard_manifest = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    val_recs = TR.read_jsonl(shard_manifest["folds"][args.fold]["heldin_val"]["path"])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(repo, revision=rev)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None \
        else tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(repo, revision=rev,
                                                 torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, args.adapter)
    model.to(device)
    model.eval()
    # Same upcast as the gate (D-S4-1), for the same reason: the comparison and the
    # merge must both happen in float32 or the storage rounding swamps the signal.
    model.float()

    base = getattr(model, "base_model", None)
    if not (hasattr(base, "merge_adapter") and hasattr(base, "unmerge_adapter")):
        TR.fail("this peft build exposes no merge_adapter/unmerge_adapter")

    # The SAME sample the gate draws -- same seed, same N, same truncation -- so the
    # alpha = 1 row is directly comparable with the `max_logit_diff` already on the
    # record rather than being a second, differently-drawn measurement.
    rng = random.Random(TH.SEED)
    samp = rng.sample(val_recs, min(TH.G4_6_SAMPLE_N, len(val_recs)))
    ids = [tokenizer(s["text"], add_special_tokens=False)["input_ids"][:args.max_len]
           for s in samp]

    b_params = [(n, p) for n, p in model.named_parameters() if "lora_B" in n]
    if not b_params:
        TR.fail("no lora_B parameters found -- nothing to scale, so the sweep would "
                "report the same number five times and call it a plateau")
    print("lora_B tensors: %d" % len(b_params))
    b_orig = {n: p.detach().clone() for n, p in b_params}

    alphas = [float(a) for a in args.alphas.split(",")]
    rows = []
    for idx, alpha in enumerate(alphas):
        with torch.no_grad():
            for n, p in b_params:
                p.copy_(b_orig[n] * alpha)
        diff, n_pos, max_abs_logit = 0.0, 0, 0.0
        for i in range(0, len(ids), TH.G4_6_MICRO_BATCH):
            chunk = ids[i:i + TH.G4_6_MICRO_BATCH]
            n = max(len(x) for x in chunk)
            inp = torch.tensor([x + [pad_id] * (n - len(x)) for x in chunk]).to(device)
            att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x in chunk]).to(device)
            with torch.no_grad():
                a = model(input_ids=inp, attention_mask=att).logits.float()
            base.merge_adapter()
            with torch.no_grad():
                b = model(input_ids=inp, attention_mask=att).logits.float()
            base.unmerge_adapter()
            m = att.bool().unsqueeze(-1)          # padded positions never compete (FINDING 15)
            d = (a - b).abs().masked_fill(~m, 0.0)
            diff = max(diff, float(d.max()))
            max_abs_logit = max(max_abs_logit, float(a.abs().masked_fill(~m, 0.0).max()))
            n_pos += int(att.sum())
            del a, b, d, m
            if device == "cuda":
                torch.cuda.empty_cache()
        label = "%g" % alpha
        if idx and alpha in alphas[:idx]:
            label += " (repeat, contamination check)"
        rows.append({"alpha": alpha, "label": label, "max_logit_diff": diff,
                     "max_abs_logit": max_abs_logit,
                     "relative": diff / max_abs_logit if max_abs_logit else None,
                     "n_positions_compared": n_pos,
                     "verdict_at_1e-4": "PASS" if diff < TH.G4_6_MAX_LOGIT_DIFF else "FAIL"})
        print("alpha %-32s max_logit_diff=%.6e  rel=%.3e  %s"
              % (label, diff, rows[-1]["relative"] or float("nan"),
                 rows[-1]["verdict_at_1e-4"]), flush=True)

    with torch.no_grad():                      # leave the adapter as we found it
        for n, p in b_params:
            p.copy_(b_orig[n])

    # --- read the shape off the numbers, and say plainly when it cannot be read ---
    verdict = {}
    one = [r for r in rows if r["alpha"] == 1.0]
    zero = [r for r in rows if r["alpha"] == 0.0]
    if zero and zero[0]["max_logit_diff"] != 0.0:
        verdict["control_alpha0"] = ("VIOLATED -- alpha=0 gave %.3e, not exactly 0. B=0 "
                                     "means W+0=W bitwise, so this script is at fault "
                                     "and no conclusion may be drawn from the sweep."
                                     % zero[0]["max_logit_diff"])
    elif zero:
        verdict["control_alpha0"] = "OK -- exactly 0.0, reproducing freeze_adapter"
    if len(one) >= 2:
        spread = abs(one[0]["max_logit_diff"] - one[-1]["max_logit_diff"])
        verdict["control_repeat_alpha1"] = {
            "first": one[0]["max_logit_diff"], "last": one[-1]["max_logit_diff"],
            "spread": spread,
            "reading": ("merge/unmerge contamination is %.1f %% of the alpha=1 reading; "
                        "the sweep is only conclusive to that precision"
                        % (100.0 * spread / one[0]["max_logit_diff"]
                           if one[0]["max_logit_diff"] else float("nan")))}
    small = [r for r in rows if 0 < r["alpha"] < 1]
    if one and small:
        # linear in alpha means drift/alpha is constant; a plateau means drift is
        # constant. Report BOTH ratios and let the numbers, not this script, decide.
        verdict["shape"] = {
            "drift_over_alpha": {("%g" % r["alpha"]): r["max_logit_diff"] / r["alpha"]
                                 for r in small + [one[0]]},
            "drift": {("%g" % r["alpha"]): r["max_logit_diff"] for r in small + [one[0]]},
            "how_to_read": "if drift_over_alpha is roughly CONSTANT the residual is the "
                           "delta's own re-association error and G4.6 at 1e-4 is "
                           "unsatisfiable for any adapter that trained; if drift is "
                           "roughly constant instead, there is a floor to band against."}
    out = {"gate": "G4.6", "decision": "D-S4-3", "adapter": args.adapter,
           "base_repo": repo, "base_revision": rev, "fold": args.fold,
           "band_unchanged": TH.G4_6_MAX_LOGIT_DIFF, "sample_n": len(samp),
           "measured_in": "float32 (D-S4-1)", "storage_dtype_restored": True,
           "tf32_matmul": bool(getattr(torch.backends.cuda.matmul, "allow_tf32", False)),
           "rows": rows, "controls_and_shape": verdict,
           "note": "REPORTED, NOT ACTED ON. No band moved, no gate re-pointed."}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("\n" + json.dumps(verdict, indent=2))
    print("\nwrote %s" % args.out)
    print("DONE.")


if __name__ == "__main__":
    main()
