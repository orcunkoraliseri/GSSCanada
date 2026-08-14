#!/usr/bin/env python
"""
4J: measure how each candidate tokenizer actually encodes our diary serialisation.

Why this exists
---------------
RL18 (2026-08-14) made two claims that decide open decision 3 and the serialisation schema,
and they contradict each other inside the same table:

  CLAIM 1 (RL18 D2)  Qwen2.5 / Gemma / Mistral-NeMo split a 3-digit activity code into 3 tokens,
                     Llama 3.1 into 1, Mistral 7B v0.3 into 4.
  CLAIM 2 (RL18 D2)  the episode string "45,311,11,0;" costs 10 tokens in Qwen2.5, with "45"
                     counted as ONE token.
  -> If digits really split individually, "45" must cost TWO tokens, the episode is 11 not 10,
     and the mnemonic saving claimed in RL18 D3 is smaller than reported.

  CLAIM 3 (RL18 D3)  every 2-letter lowercase string aa..zz and common 3-letter mnemonics
                     (wrk, slp, eat) are EXACTLY 1 token in Qwen2.5, so remapping the ~145
                     activity codes to mnemonics erases the tokenizer penalty at zero cost.

This script settles all three by asking the tokenizers, not a report. No training, no GPU,
CPU only, a few minutes.

Run it with sbatch. Never on the login node.
"""

import os
import sys
import traceback

# One row per candidate. Gated repos need HF_TOKEN in the environment; if it is absent the
# row reports GATED rather than crashing the run.
MODELS = [
    ("Qwen/Qwen2.5-0.5B",              "pilot leg, Apache 2.0"),
    ("Qwen/Qwen2.5-1.5B",              "pilot leg, Apache 2.0"),
    ("Qwen/Qwen2.5-7B",                "current first choice, Apache 2.0"),
    ("meta-llama/Llama-3.1-8B",        "GATED, licence disqualified, measured for reference only"),
    ("google/gemma-2-9b",              "GATED"),
    ("google/gemma-3-4b-pt",           "GATED, pilot-size Google model"),
    ("mistralai/Mistral-7B-v0.3",      "Apache 2.0"),
    ("mistralai/Mistral-Nemo-Base-2407", "Apache 2.0"),
    ("allenai/OLMo-2-1124-7B",         "Apache 2.0"),
]

# The strings that decide the dispute.
SINGLE = ["0", "11", "45", "011", "111", "311", "411", "911", "145"]

# Our adopted episode form: DUR,ACT,LOC,COP;
EPISODE_NUM = "45,311,11,0;"
EPISODE_MNE = "45,wrk,11,0;"

# A realistic diary: 25 episodes, numeric codes, and the same diary with mnemonic codes.
_DUR = [480, 20, 35, 10, 55, 15, 240, 30, 45, 15, 60, 25, 20, 90, 15, 35, 10, 120,
        20, 40, 15, 30, 25, 65, 45]
_ACT = ["311", "411", "111", "911", "311", "121", "411", "211", "511", "311", "111",
        "621", "411", "811", "311", "911", "121", "821", "411", "211", "311", "511",
        "111", "911", "311"]
_MNE = ["slp", "wrk", "eat", "trv", "slp", "was", "wrk", "hwk", "chd", "slp", "eat",
        "shp", "wrk", "tvw", "slp", "trv", "was", "soc", "wrk", "hwk", "slp", "chd",
        "eat", "trv", "slp"]
_LOC = ["11", "31", "11", "91", "11", "11", "31", "11", "11", "11", "11", "41", "31",
        "11", "11", "91", "11", "21", "31", "11", "11", "11", "11", "91", "11"]
_COP = ["0", "1", "2", "0", "0", "0", "1", "2", "3", "0", "2", "1", "1", "2", "0",
        "0", "0", "3", "1", "2", "0", "3", "2", "0", "0"]

DIARY_NUM = "".join(
    "%d,%s,%s,%s;" % (d, a, l, c) for d, a, l, c in zip(_DUR, _ACT, _LOC, _COP)
)
DIARY_MNE = "".join(
    "%d,%s,%s,%s;" % (d, a, l, c) for d, a, l, c in zip(_DUR, _MNE, _LOC, _COP)
)

# 3-letter mnemonics we would actually want to use if the trick works.
MNEMONICS_3 = ["slp", "wrk", "eat", "trv", "shp", "tvw", "soc", "hwk", "chd", "was",
               "stu", "spo", "vol", "rst", "cln", "cok", "gar", "pcw", "rdg", "hob"]


def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def census_two_letter(tok):
    """How many of the 676 two-letter lowercase strings are exactly one token."""
    ok = []
    for a in "abcdefghijklmnopqrstuvwxyz":
        for b in "abcdefghijklmnopqrstuvwxyz":
            s = a + b
            if n_tok(tok, s) == 1:
                ok.append(s)
    return ok


def census_three_letter(tok):
    return [m for m in MNEMONICS_3 if n_tok(tok, m) == 1]


def measure(repo, note):
    from transformers import AutoTokenizer

    print("=" * 78)
    print("MODEL   %s" % repo)
    print("NOTE    %s" % note)
    try:
        tok = AutoTokenizer.from_pretrained(repo)
    except Exception as exc:
        print("STATUS  COULD NOT LOAD")
        print("REASON  %s: %s" % (type(exc).__name__, str(exc)[:300]))
        print("        (gated repo needs HF_TOKEN, or the compute node has no network)")
        return None

    print("STATUS  loaded")
    print("CLASS   %s" % type(tok).__name__)
    print("VOCAB   %s" % getattr(tok, "vocab_size", "unknown"))

    print("-- single strings, tokens each, bare and with a leading space")
    for s in SINGLE:
        bare = tok.tokenize(s)
        lead = tok.tokenize(" " + s)
        print("   %-5s bare=%d %-28s lead=%d %s"
              % (s, len(bare), str(bare)[:28], len(lead), str(lead)[:28]))

    print("-- one episode")
    e_num = n_tok(tok, EPISODE_NUM)
    e_mne = n_tok(tok, EPISODE_MNE)
    print("   numeric  %-14s %d tokens  %s" % (EPISODE_NUM, e_num, tok.tokenize(EPISODE_NUM)))
    print("   mnemonic %-14s %d tokens  %s" % (EPISODE_MNE, e_mne, tok.tokenize(EPISODE_MNE)))

    print("-- one full diary, 25 episodes")
    d_num = n_tok(tok, DIARY_NUM)
    d_mne = n_tok(tok, DIARY_MNE)
    print("   numeric  %d tokens" % d_num)
    print("   mnemonic %d tokens   (saving %d, %.1f%%)"
          % (d_mne, d_num - d_mne, 100.0 * (d_num - d_mne) / max(d_num, 1)))

    print("-- mnemonic feasibility")
    two = census_two_letter(tok)
    three = census_three_letter(tok)
    print("   two-letter aa..zz that are exactly 1 token: %d of 676" % len(two))
    print("   of the 20 candidate 3-letter mnemonics, 1 token: %d  %s" % (len(three), three))
    print("   enough 1-token labels for ~145 activity codes: %s"
          % ("YES" if len(two) + len(three) >= 145 else "NO"))

    return {
        "repo": repo,
        "vocab": getattr(tok, "vocab_size", 0),
        "code3": n_tok(tok, "311"),
        "pair": n_tok(tok, "45"),
        "epi_num": e_num,
        "epi_mne": e_mne,
        "diary_num": d_num,
        "diary_mne": d_mne,
        "two": len(two),
    }


def main():
    print("4J tokenizer measurement")
    print("transformers cache: %s" % os.environ.get("HF_HOME", "(default)"))
    try:
        import transformers
        print("transformers version: %s" % transformers.__version__)
    except Exception:
        print("FATAL: transformers is not importable in this environment.")
        traceback.print_exc()
        sys.exit(1)

    rows = []
    for repo, note in MODELS:
        try:
            r = measure(repo, note)
        except Exception:
            print("UNEXPECTED FAILURE on %s" % repo)
            traceback.print_exc()
            r = None
        if r:
            rows.append(r)

    print()
    print("=" * 78)
    print("SUMMARY  (tokens; 'code3' is the string 311, 'pair' is the string 45)")
    print("%-34s %6s %6s %5s %8s %8s %9s %9s"
          % ("model", "vocab", "code3", "pair", "epi_num", "epi_mne", "diary_num", "diary_mne"))
    for r in rows:
        print("%-34s %6d %6d %5d %8d %8d %9d %9d"
              % (r["repo"], r["vocab"], r["code3"], r["pair"],
                 r["epi_num"], r["epi_mne"], r["diary_num"], r["diary_mne"]))

    print()
    print("VERDICTS TO READ OFF THIS TABLE")
    print(" 1. RL18 says code3 is 1 for Llama and 3 for Qwen/Gemma/NeMo, 4 for Mistral 7B v0.3.")
    print(" 2. RL18 counts 'pair' (45) as 1 token for Qwen. If pair is 2 here, RL18's episode")
    print("    and diary arithmetic is wrong and so is the size of the mnemonic saving.")
    print(" 3. The mnemonic trick is only real if diary_mne is close to the Llama diary_num")
    print("    AND at least 145 one-token labels exist.")
    print(" 4. Our own earlier estimate was 196 to 326 tokens per diary. Compare diary_num.")
    print("A row that failed to load proves nothing about that model. Stage its files and re-run.")


if __name__ == "__main__":
    main()
