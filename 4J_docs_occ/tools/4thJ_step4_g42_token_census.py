#!/usr/bin/env python
"""
D-S4-4's PRECONDITION, measured instead of inferred.

FINDING 28 rests on one claim about the tokenizer: that an absent ACT2 -- serialised
as TWO ADJACENT COMMAS -- is emitted as a SINGLE token whose decoding is entirely
delimiter characters, so `delimiter_token_ids()` admits it and G4.2's first arm is
charged for a content decision.

That claim was reached ARITHMETICALLY, not observed: the detector reported 675,169
delimiter tokens over 5,520 validation records (122.3 per record), the uk+it mix runs
29.15 episodes per record, five standalone delimiters per episode predicts 145.8 and a
merged ",," predicts 124.0. Close, and still an inference. A THIRD explanation fits the
same count -- delimiters merging with adjacent DIGITS into tokens that are not pure
delimiters at all (",0", "0,"), which would put the act2 decision in the CONTENT bucket
and make D-S4-4 wrong.

This settles it on the tokenizer itself. CPU only, no model, no GPU: it tokenizes real
validation records and prints the census. It changes nothing and rules nothing.

    IF a pure ",," token is present and carries ~1 occurrence per empty-act2 episode,
       D-S4-4's premise holds and the re-point is measuring what it claims to.
    IF NOT, D-S4-4 must be withdrawn and re-derived before it is ever run on a GPU.

usage:
    python 4thJ_step4_g42_token_census.py --fold es [--n 300]
"""

import argparse
import importlib
import json
import os
from collections import Counter

TH = importlib.import_module("4thJ_step4_thresholds")

STEP4 = "/speed-scratch/o_iseri/4J_step4"
MANIFEST_IN = os.path.join(STEP4, "shard_manifest.json")
DELIM_CHARS = set(",;|")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fold", default="es")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--repo", default=None)
    args = ap.parse_args()

    from transformers import AutoTokenizer

    shard_manifest = json.load(open(MANIFEST_IN, "r", encoding="utf-8"))
    val_path = shard_manifest["folds"][args.fold]["heldin_val"]["path"]
    recs = []
    with open(val_path, "r", encoding="utf-8") as fh:
        for line in fh:
            recs.append(json.loads(line))
            if len(recs) >= args.n:
                break
    repo = args.repo or "allenai/OLMo-2-0425-1B"
    tok = AutoTokenizer.from_pretrained(repo)
    print("tokenizer %s  len=%d" % (repo, len(tok)))
    print("records   %d from %s" % (len(recs), val_path))

    # the gate's own definition, reproduced verbatim rather than imported, so that a
    # future edit to the trainer cannot silently change what this census reports
    pure = {}
    for i in range(len(tok)):
        try:
            s = tok.decode([i])
        except Exception:
            continue
        if s and all(ch in DELIM_CHARS for ch in s):
            pure[i] = s
    print("\nPURE delimiter ids (the gate's `delimiter_token_ids`): %d" % len(pure))

    counts = Counter()
    mixed = Counter()           # tokens CONTAINING a delimiter but not pure
    n_tok = 0
    eps_total = 0
    empty_act2 = 0
    for r in recs:
        body = r["text"].split("|", 1)[1]
        b = body[:-len(TH.G4_7_EOR)] if body.endswith(TH.G4_7_EOR) else body
        for ep in [x for x in b.split(";") if x]:
            f = ep.split(",")
            if len(f) == 5:
                eps_total += 1
                if f[2] == "":
                    empty_act2 += 1
        ids = tok(r["text"], add_special_tokens=False)["input_ids"]
        n_tok += len(ids)
        for i in ids:
            if i in pure:
                counts[i] += 1
            else:
                s = tok.decode([i])
                if any(ch in DELIM_CHARS for ch in s):
                    mixed[s] += 1

    n_delim = sum(counts.values())
    print("\n%-8s %-14s %8s %10s" % ("id", "decodes to", "count", "per record"))
    for i, c in counts.most_common():
        print("%-8d %-14s %8d %10.2f" % (i, repr(pure[i]), c, c / len(recs)))
    for i, s in pure.items():
        if i not in counts:
            print("%-8d %-14s %8d %10.2f" % (i, repr(s), 0, 0.0))

    print("\nepisodes %d (%.2f per record), act2 empty %d (%.4f)"
          % (eps_total, eps_total / len(recs), empty_act2, empty_act2 / eps_total))
    print("tokens %d (%.1f per record); pure-delimiter tokens %d (%.2f per record)"
          % (n_tok, n_tok / len(recs), n_delim, n_delim / len(recs)))
    print("detector reported 122.3 pure-delimiter tokens per record on the full 5,520")

    if mixed:
        print("\n🔴 tokens CONTAINING a delimiter but NOT pure (these are scored as "
              "CONTENT, and if a ',,'-bearing one appears here D-S4-4 is aimed at the "
              "wrong token):")
        for s, c in mixed.most_common(20):
            print("   %-16s %8d" % (repr(s), c))
    else:
        print("\nno mixed delimiter/content tokens at all -- every delimiter character "
              "in this corpus lands in a pure delimiter token")

    dd = {i: (s, counts.get(i, 0)) for i, s in pure.items() if ",," in s}
    print("\n--- D-S4-4 PREMISE ---")
    if not dd:
        print("🔴 FAILED: no pure delimiter token contains ',,'. The empty-ACT2 slot is "
              "NOT in the delimiter bucket the way FINDING 28 claims. D-S4-4 must be "
              "withdrawn and re-derived. Do NOT run the re-pointed gate.")
    else:
        tot = sum(c for _, c in dd.values())
        print("ids carrying ',,': %s" % {i: repr(s) for i, (s, _) in dd.items()})
        print("occurrences %d against %d empty-act2 episodes  (ratio %.4f)"
              % (tot, empty_act2, tot / empty_act2 if empty_act2 else float("nan")))
        if empty_act2 and 0.9 <= tot / empty_act2 <= 1.1:
            print("🟢 HOLDS: about one such token per empty-ACT2 episode, which is what "
                  "FINDING 28 asserts and what D-S4-4 removes from the arm.")
        else:
            print("🟡 PARTIAL: the ratio is not ~1, so the ',,' token covers only part "
                  "of the empty-ACT2 slots. Report the ratio; do not round it to 1.")
    print("DONE.")


if __name__ == "__main__":
    main()
