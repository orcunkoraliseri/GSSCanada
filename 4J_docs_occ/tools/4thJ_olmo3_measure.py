#!/usr/bin/env python
"""
4J: measure OLMo 3 the same way we measured the others.

Why. Job 1234177 showed allenai/OLMo-2-1124-7B writes a 3-digit activity code in ONE token
(200-token diary against Qwen2.5's 303) and is Apache 2.0. Job 1234192 then found the one
objection to it: vLLM registers Olmo2ForCausalLM only against the generic Transformers
fallback backend, while Olmo3ForCausalLM has a NATIVE vLLM implementation.

So if OLMo 3 keeps the OLMo 2 tokenizer, it removes the objection. This job asks:

  Q1  which OLMo 3 base checkpoints exist, and at which sizes (is there a Leg-4 pilot size)
  Q2  what context window (OLMo 2 was 4096 at every size, Qwen2.5-7B is 131072)
  Q3  does it keep the one-token-per-3-digit-code property
  Q4  same diary cost, numeric and mnemonic, directly comparable to the 1234177 table

Repo names are DISCOVERED from the HF API, not guessed, so a rename cannot silently give us
an empty answer. CPU only.

Run with sbatch. Never on the login node.
"""

import json
import sys
import traceback
import urllib.request

# ---------------------------------------------------------------- discovery
API = "https://huggingface.co/api/models?author=allenai&search=%s&limit=200"
SEARCHES = ["OLMo-3", "Olmo-3", "OLMo3"]

# Reference rows, so the new numbers land in the same table as job 1234177.
REFERENCE = ["allenai/OLMo-2-1124-7B", "Qwen/Qwen2.5-7B"]

# ---------------------------------------------------------------- the strings under test
SINGLE = ["0", "11", "45", "011", "111", "311", "411", "911", "145"]
EPISODE_NUM = "45,311,11,0;"
EPISODE_MNE = "45,wrk,11,0;"

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

DIARY_NUM = "".join("%d,%s,%s,%s;" % t for t in zip(_DUR, _ACT, _LOC, _COP))
DIARY_MNE = "".join("%d,%s,%s,%s;" % t for t in zip(_DUR, _MNE, _LOC, _COP))

MNEMONICS_3 = ["slp", "wrk", "eat", "trv", "shp", "tvw", "soc", "hwk", "chd", "was",
               "stu", "spo", "vol", "rst", "cln", "cok", "gar", "pcw", "rdg", "hob"]


def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def discover():
    print("=" * 78)
    print("Q1 -- which OLMo 3 repos exist under allenai, from the HF API")
    print("=" * 78)
    found = {}
    for term in SEARCHES:
        url = API % term
        try:
            with urllib.request.urlopen(url, timeout=60) as fh:
                data = json.loads(fh.read().decode("utf-8", "replace"))
        except Exception as exc:
            print("SEARCH %-10s COULD NOT FETCH -- %s: %s"
                  % (term, type(exc).__name__, str(exc)[:160]))
            continue
        print("SEARCH %-10s %d results" % (term, len(data)))
        for m in data:
            mid = m.get("id" if "id" in m else "modelId", "?")
            found[mid] = m.get("downloads", 0)
    if not found:
        print("NOTHING FOUND. Either no network to the HF API, or the naming changed.")
        return []
    print()
    print("all OLMo 3 repos seen, by downloads")
    for mid in sorted(found, key=lambda k: -found[k]):
        print("   %-46s downloads=%s" % (mid, found[mid]))
    # Base checkpoints only: our recipe fine-tunes a base, not an Instruct/SFT/DPO/RLVR chat model.
    base = [m for m in found
            if not any(t in m.lower() for t in
                       ("instruct", "sft", "dpo", "rlvr", "think", "chat", "gguf", "rl-zero"))]
    print()
    print("kept as BASE candidates (no instruct/sft/dpo/rlvr/think/chat/gguf)")
    for m in sorted(base):
        print("   %s" % m)
    return sorted(base)


def measure(repo):
    from transformers import AutoConfig, AutoTokenizer

    print("-" * 78)
    print("MODEL  %s" % repo)
    ctx, arch, vocab_cfg = 0, "?", 0
    try:
        cfg = AutoConfig.from_pretrained(repo).to_dict()
        arch = (cfg.get("architectures") or ["?"])[0]
        ctx = cfg.get("max_position_embeddings", 0)
        vocab_cfg = cfg.get("vocab_size", 0)
        print("   architectures            %s" % cfg.get("architectures"))
        print("   max_position_embeddings  %s" % ctx)
        print("   sliding_window           %s" % cfg.get("sliding_window"))
        print("   vocab_size               %s" % vocab_cfg)
        print("   hidden_size              %s" % cfg.get("hidden_size"))
        print("   num_hidden_layers        %s" % cfg.get("num_hidden_layers"))
        print("   num_key_value_heads      %s" % cfg.get("num_key_value_heads"))
    except Exception as exc:
        print("   CONFIG COULD NOT LOAD -- %s: %s" % (type(exc).__name__, str(exc)[:200]))

    try:
        tok = AutoTokenizer.from_pretrained(repo)
    except Exception as exc:
        print("   TOKENIZER COULD NOT LOAD -- %s: %s" % (type(exc).__name__, str(exc)[:200]))
        return None

    print("   tokenizer class          %s" % type(tok).__name__)
    print("-- single strings, tokens each")
    for s in SINGLE:
        print("   %-5s %d  %s" % (s, len(tok.tokenize(s)), tok.tokenize(s)))

    e_num, e_mne = n_tok(tok, EPISODE_NUM), n_tok(tok, EPISODE_MNE)
    d_num, d_mne = n_tok(tok, DIARY_NUM), n_tok(tok, DIARY_MNE)
    print("-- one episode")
    print("   numeric  %-14s %d tokens  %s" % (EPISODE_NUM, e_num, tok.tokenize(EPISODE_NUM)))
    print("   mnemonic %-14s %d tokens  %s" % (EPISODE_MNE, e_mne, tok.tokenize(EPISODE_MNE)))
    print("-- one full diary, 25 episodes")
    print("   numeric  %d tokens" % d_num)
    print("   mnemonic %d tokens  (saving %d, %.1f%%)"
          % (d_mne, d_num - d_mne, 100.0 * (d_num - d_mne) / max(d_num, 1)))

    two = [a + b for a in "abcdefghijklmnopqrstuvwxyz" for b in "abcdefghijklmnopqrstuvwxyz"
           if n_tok(tok, a + b) == 1]
    three = [m for m in MNEMONICS_3 if n_tok(tok, m) == 1]
    print("-- mnemonic feasibility")
    print("   two-letter aa..zz that are exactly 1 token: %d of 676" % len(two))
    print("   of the 20 candidate 3-letter mnemonics, 1 token: %d  %s" % (len(three), three))

    return {"repo": repo, "arch": arch, "ctx": ctx,
            "vocab": getattr(tok, "vocab_size", vocab_cfg),
            "code3": n_tok(tok, "311"), "pair": n_tok(tok, "45"),
            "epi_num": e_num, "epi_mne": e_mne,
            "diary_num": d_num, "diary_mne": d_mne, "two": len(two)}


def main():
    print("4J OLMo 3 tokenizer and context measurement")
    try:
        import transformers
        print("transformers version: %s" % transformers.__version__)
    except Exception:
        print("FATAL: transformers not importable")
        traceback.print_exc()
        sys.exit(1)

    try:
        candidates = discover()
    except Exception:
        print("UNEXPECTED FAILURE in discovery")
        traceback.print_exc()
        candidates = []

    print()
    print("=" * 78)
    print("Q2 to Q4 -- context and token cost")
    print("=" * 78)
    rows = []
    for repo in candidates + REFERENCE:
        try:
            r = measure(repo)
        except Exception:
            print("UNEXPECTED FAILURE on %s" % repo)
            traceback.print_exc()
            r = None
        if r:
            rows.append(r)

    print()
    print("=" * 78)
    print("SUMMARY  ('code3' is the string 311, 'pair' is the string 45)")
    print("%-40s %-20s %8s %7s %5s %5s %8s %9s"
          % ("model", "architecture", "context", "vocab", "cd3", "pair", "diary_n", "diary_mne"))
    for r in rows:
        print("%-40s %-20s %8d %7d %5d %5d %8d %9d"
              % (r["repo"], r["arch"], r["ctx"], r["vocab"], r["code3"], r["pair"],
                 r["diary_num"], r["diary_mne"]))

    print()
    print("HOW TO READ IT")
    print(" 1. OLMo-2-1124-7B measured 200 tokens per diary, code3=1. If OLMo 3 matches, it")
    print("    keeps the efficiency AND gains the native vLLM kernel OLMo 2 lacks.")
    print(" 2. OLMo 2 was 4096 context at every size. Check whether OLMo 3 lifted that.")
    print(" 3. A size at or under ~2B makes the Leg-4 pilot cheap. Look at the discovered list.")
    print(" 4. A repo that failed to load proves nothing about it. It means we could not look.")


if __name__ == "__main__":
    main()
