#!/usr/bin/env python
"""
4J: measure the token cost of five candidate COP (co-presence) packings, in situ,
inside a complete episode tuple and inside a complete 25-episode diary.

Why this exists
----------------
COP became six binary flags on 2026-08-16 (was five; the sixth is "with a parent").
Six flags must reach the model without costing six tokens per episode. RL18 got a
prior packing question wrong by counting a bare fragment ("45" alone) instead of the
fragment as it sits inside the full episode string, where BPE merges across the comma
and semicolon change the token boundaries. This script never measures a bare string;
every number below is measured inside "DUR,ACT,LOC,<COP-encoding>;" or inside the full
25-episode diary built from that pattern.

Tokenizer: OLMo / dolma2 BPE. Model id used here: allenai/OLMo-2-0425-1B. This is NOT
the paper's backbone (allenai/Olmo-3-1025-7B) -- it is used as a stand-in because it
carries an identical vocabulary and is far smaller to download. That substitution is
stated again in the output below.

Run with sbatch. Never on the login node.
"""

import os
import sys
import traceback

MODEL = "allenai/OLMo-2-0425-1B"
NOTE = ("stand-in for allenai/Olmo-3-1025-7B: identical dolma2 BPE vocabulary, "
        "used here only because it is far smaller to download")

# ---------------------------------------------------------------------------
# The 25-episode diary skeleton (DUR, ACT, LOC), independent of the COP packing.
# Durations are multiples of 10 and sum to 1440 (24h). Activity codes are 3-digit.
# Location codes include "41" (above 39, Spain public transport).
# ---------------------------------------------------------------------------
_DUR = [480, 240, 30, 20, 10, 40, 30, 60, 20, 10, 90, 30, 20, 10, 50, 30, 20, 10, 60,
        30, 20, 10, 40, 30, 50]
_ACT = ["311", "411", "111", "911", "311", "121", "411", "211", "511", "311", "111",
        "621", "411", "811", "311", "911", "121", "821", "411", "211", "311", "511",
        "111", "911", "311"]
_LOC = ["11", "31", "11", "91", "11", "11", "31", "11", "11", "11", "11", "41", "31",
        "11", "11", "91", "11", "21", "31", "11", "11", "11", "11", "91", "11"]

assert len(_DUR) == len(_ACT) == len(_LOC) == 25
assert sum(_DUR) == 1440
assert all(d % 10 == 0 for d in _DUR)

# Per-episode COP integer value (0-63), one per episode, deterministic and varied:
# v_i = (7*i + 3) mod 64. Not claimed to be realistic co-presence patterns, only a
# varied, reproducible sweep of six-bit values across the diary.
_COP_VALS = [(7 * i + 3) % 64 for i in range(25)]

# The representative single episode uses v = 22, matching the manager's own worked
# example (binary 010110 / octal 26 / hex 16 / bits 0,1,0,1,1,0 are all v=22).
REP_DUR, REP_ACT, REP_LOC, REP_V = 30, "311", "11", 22


def enc_decimal(v):
    return str(v)


def enc_binary6(v):
    return format(v, "06b")


def enc_octal2(v):
    return format(v, "02o")


def enc_hex2(v):
    return format(v, "02x")


def enc_baseline(v):
    return ",".join(format(v, "06b"))


CANDIDATES = [
    ("1_decimal_0-63", enc_decimal, "single decimal integer, 0-63"),
    ("2_six_chars", enc_binary6, "six characters, e.g. 010110"),
    ("3_two_octal", enc_octal2, "two octal digits, e.g. 26"),
    ("4_two_hex", enc_hex2, "two hex characters, e.g. 16"),
    ("5_baseline_csv_bits", enc_baseline, "six comma-separated digits, do-nothing baseline"),
]


def episode_str(dur, act, loc, cop_enc):
    return "%d,%s,%s,%s;" % (dur, act, loc, cop_enc)


def diary_str(enc_fn):
    parts = []
    for dur, act, loc, v in zip(_DUR, _ACT, _LOC, _COP_VALS):
        parts.append(episode_str(dur, act, loc, enc_fn(v)))
    return "".join(parts)


def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def sweep_worst_case(tok, enc_fn):
    """All 64 values of v, each embedded in the representative episode tuple.
    Returns (max_tokens, [values achieving max], per_value_dict)."""
    per_value = {}
    for v in range(64):
        s = episode_str(REP_DUR, REP_ACT, REP_LOC, enc_fn(v))
        per_value[v] = n_tok(tok, s)
    max_tok = max(per_value.values())
    worst = [v for v, t in per_value.items() if t == max_tok]
    return max_tok, worst, per_value


def main():
    print("4J COP packing measurement")
    print("transformers cache: %s" % os.environ.get("HF_HOME", "(default)"))
    try:
        import transformers
        print("transformers version: %s" % transformers.__version__)
    except Exception:
        print("FATAL: transformers is not importable in this environment.")
        traceback.print_exc()
        sys.exit(1)

    from transformers import AutoTokenizer

    print("=" * 78)
    print("MODEL   %s" % MODEL)
    print("NOTE    %s" % NOTE)
    try:
        tok = AutoTokenizer.from_pretrained(MODEL)
    except Exception as exc:
        print("STATUS  COULD NOT LOAD")
        print("REASON  %s: %s" % (type(exc).__name__, str(exc)[:300]))
        sys.exit(1)

    print("STATUS  loaded")
    print("CLASS   %s" % type(tok).__name__)
    print("VOCAB   %s" % getattr(tok, "vocab_size", "unknown"))

    print()
    print("-- diary skeleton (shared across all candidates)")
    print("   DUR (25, multiples of 10, sum=%d): %s" % (sum(_DUR), _DUR))
    print("   ACT (25, 3-digit):                  %s" % _ACT)
    print("   LOC (25, includes 41 > 39):          %s" % _LOC)
    print("   per-episode COP integer v (0-63), v_i=(7i+3) mod 64: %s" % _COP_VALS)
    print("   representative episode uses DUR=%d ACT=%s LOC=%s v=%d"
          % (REP_DUR, REP_ACT, REP_LOC, REP_V))

    results = []
    for name, enc_fn, desc in CANDIDATES:
        print()
        print("=" * 78)
        print("CANDIDATE %s -- %s" % (name, desc))

        rep_encoded = enc_fn(REP_V)
        rep_str = episode_str(REP_DUR, REP_ACT, REP_LOC, rep_encoded)
        rep_tokens = tok.tokenize(rep_str)
        rep_n = len(rep_tokens)
        print("   representative episode string: %r" % rep_str)
        print("   representative episode tokens (%d): %s" % (rep_n, rep_tokens))

        d_str = diary_str(enc_fn)
        d_n = n_tok(tok, d_str)
        print("   full 25-episode diary string: %r" % d_str)
        print("   full 25-episode diary tokens: %d" % d_n)

        max_tok, worst_vals, per_value = sweep_worst_case(tok, enc_fn)
        print("   worst case over all 64 values of v, in the representative episode slot:")
        print("     max tokens = %d, achieved at v in %s" % (max_tok, worst_vals))
        print("     (min tokens = %d, at v in %s)"
              % (min(per_value.values()),
                 [v for v, t in per_value.items() if t == min(per_value.values())]))

        results.append({
            "name": name,
            "desc": desc,
            "rep_str": rep_str,
            "rep_tokens": rep_n,
            "diary_str": d_str,
            "diary_tokens": d_n,
            "worst_tokens": max_tok,
            "worst_values": worst_vals,
        })

    print()
    print("=" * 78)
    print("SUMMARY  (tokens; episode = representative episode w/ v=22; diary = 25 episodes;")
    print("          worst = max tokens for that episode slot swept over all 64 COP values)")
    print("%-24s %8s %8s %8s %s" % ("candidate", "episode", "diary", "worst", "worst_at_v"))
    for r in results:
        print("%-24s %8d %8d %8d %s"
              % (r["name"], r["rep_tokens"], r["diary_tokens"], r["worst_tokens"], r["worst_values"]))

    print()
    print("Reference: prior measurement on this vocabulary (jobs 1234177/1234199/1234216) found")
    print("a 25-episode diary with single-digit COP costs 200 tokens (8 tokens/episode).")


if __name__ == "__main__":
    main()
