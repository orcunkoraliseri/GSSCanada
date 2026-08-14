#!/usr/bin/env python
"""
4J: the three things job 1234211 could not settle.

Job 1234211 read the licence metadata for every candidate. Three gaps remain, and each one
is load-bearing for open decision 3, so each is closed here rather than assumed.

  A  The OLMo repos carry NO LICENSE file. Their only licence statement is the Hugging Face
     cardData tag "apache-2.0". A tag is metadata, not a licence. Read the model card itself
     and find the sentence Ai2 actually wrote.

  B  meta-llama/Llama-3.1-8B is gated=manual, so we could not read its licence from the repo
     and therefore have NOT verified with our own eyes the Section 1.b clause on which the
     whole Llama disqualification rests. Fetch the licence Meta publishes openly and search
     it for the clause.

  C  Qwen3 is absent from RL18 entirely, yet vLLM registers Qwen3ForCausalLM natively and
     Qwen3-8B is Apache 2.0 with 16 M downloads a month. Before the plan documents name a
     backbone, measure the Qwen3 tokenizer on the same strings as every other row, and find
     out whether Qwen3 has a base checkpoint at pilot size.

CPU only, metadata and text only, no weights.
Run with sbatch. Never on the login node.
"""

import json
import re
import sys
import traceback
import urllib.request

# ------------------------------------------------------------------ A, model cards
CARDS = [
    "allenai/Olmo-3-1025-7B",
    "allenai/Olmo-3-1125-32B",
    "allenai/OLMo-2-0425-1B",
    "mistralai/Mistral-7B-v0.3",
]
CARD_URL = "https://huggingface.co/%s/raw/main/README.md"

# ------------------------------------------------------------------ B, the Llama clause
LLAMA_SOURCES = [
    "https://www.llama.com/llama3_1/license/",
    "https://huggingface.co/meta-llama/Llama-3.1-8B/raw/main/LICENSE",
    "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE",
]
CLAUSE = "improve any other large language model"

# ------------------------------------------------------------------ C, Qwen3
QWEN_API = "https://huggingface.co/api/models?author=Qwen&search=Qwen3&limit=200"
QWEN3_MEASURE = ["Qwen/Qwen3-8B", "Qwen/Qwen3-4B-Base", "Qwen/Qwen3-1.7B-Base",
                 "Qwen/Qwen3-0.6B-Base"]
REFERENCE = ["allenai/Olmo-3-1025-7B", "Qwen/Qwen2.5-7B"]

SINGLE = ["0", "11", "45", "011", "111", "311", "411", "911", "145"]
EPISODE_NUM = "45,311,11,0;"

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


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 4J-check"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", "replace")


def strip_tags(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", html))


# ================================================================== A
def check_cards():
    print("=" * 78)
    print("A -- what the model card itself says about the licence")
    print("=" * 78)
    for repo in CARDS:
        print("-" * 78)
        print("REPO %s" % repo)
        try:
            text = fetch(CARD_URL % repo)
        except Exception as exc:
            print("   COULD NOT READ CARD -- %s: %s" % (type(exc).__name__, str(exc)[:140]))
            continue
        print("   card is %d bytes" % len(text))
        # The YAML front matter carries the machine-readable declaration.
        if text.startswith("---"):
            end = text.find("\n---", 3)
            front = text[:end if end > 0 else 400]
            for ln in front.splitlines():
                if "licen" in ln.lower():
                    print("   front matter | %s" % ln.strip()[:120])
        hits = 0
        for ln in text.splitlines():
            low = ln.lower()
            if "licen" in low or "apache" in low:
                hits += 1
                if hits <= 8:
                    print("   body         | %s" % ln.strip()[:150])
        if not hits:
            print("   NO licence sentence in the card body. The tag is the only statement.")


# ================================================================== B
def check_llama():
    print()
    print("=" * 78)
    print("B -- the Llama 3.1 clause, read rather than cited")
    print("=" * 78)
    print('   searching for: "%s"' % CLAUSE)
    settled = False
    for url in LLAMA_SOURCES:
        print("-" * 78)
        print("SOURCE %s" % url)
        try:
            raw = fetch(url)
        except Exception as exc:
            print("   COULD NOT FETCH -- %s: %s" % (type(exc).__name__, str(exc)[:140]))
            continue
        text = strip_tags(raw) if "<" in raw[:200] else raw
        print("   fetched %d bytes, %d after tag stripping" % (len(raw), len(text)))
        low = text.lower()
        i = low.find(CLAUSE)
        if i < 0:
            print("   CLAUSE NOT PRESENT in this document.")
            continue
        settled = True
        print("   CLAUSE FOUND at offset %d. Surrounding text:" % i)
        print("      ...%s..." % text[max(0, i - 500):i + 300].strip())
        break
    if not settled:
        print()
        print("   NOT VERIFIED. Every source failed or lacked the clause. The Llama")
        print("   disqualification therefore still rests on a report, not on our reading.")


# ================================================================== C
def n_tok(tok, s):
    return len(tok.encode(s, add_special_tokens=False))


def discover_qwen3():
    print()
    print("=" * 78)
    print("C1 -- does Qwen3 have a BASE checkpoint at pilot size")
    print("=" * 78)
    try:
        data = json.loads(fetch(QWEN_API))
    except Exception as exc:
        print("   COULD NOT FETCH -- %s: %s" % (type(exc).__name__, str(exc)[:140]))
        return []
    print("   %d Qwen3 repos returned" % len(data))
    # Qwen3 names its pretrained checkpoints "-Base"; the bare name is the post-trained one.
    base = sorted(m.get("id", "?") for m in data
                  if m.get("id", "").endswith("-Base")
                  and not any(t in m.get("id", "").lower()
                              for t in ("fp8", "awq", "gptq", "int4", "int8", "moe", "a3b",
                                        "a22b", "omni", "vl", "coder", "embedding",
                                        "reranker", "guard")))
    print("   BASE checkpoints (name ends in -Base, no quantised or non-text variants)")
    for m in base:
        print("      %s" % m)
    if not base:
        print("      NONE FOUND -- check whether the naming convention changed")
    return base


def measure(repo):
    from transformers import AutoConfig, AutoTokenizer
    print("-" * 78)
    print("MODEL  %s" % repo)
    ctx, arch = 0, "?"
    try:
        cfg = AutoConfig.from_pretrained(repo).to_dict()
        arch = (cfg.get("architectures") or ["?"])[0]
        ctx = cfg.get("max_position_embeddings", 0)
        print("   architectures            %s" % cfg.get("architectures"))
        print("   max_position_embeddings  %s" % ctx)
        print("   sliding_window           %s" % cfg.get("sliding_window"))
        print("   vocab_size               %s" % cfg.get("vocab_size"))
        print("   num_hidden_layers        %s" % cfg.get("num_hidden_layers"))
    except Exception as exc:
        print("   CONFIG COULD NOT LOAD -- %s: %s" % (type(exc).__name__, str(exc)[:180]))
    try:
        tok = AutoTokenizer.from_pretrained(repo)
    except Exception as exc:
        print("   TOKENIZER COULD NOT LOAD -- %s: %s" % (type(exc).__name__, str(exc)[:180]))
        return None
    for s in SINGLE:
        print("   %-5s %d  %s" % (s, len(tok.tokenize(s)), tok.tokenize(s)))
    d_num, d_mne = n_tok(tok, DIARY_NUM), n_tok(tok, DIARY_MNE)
    print("   episode  %-14s %d tokens" % (EPISODE_NUM, n_tok(tok, EPISODE_NUM)))
    print("   diary numeric  %d tokens" % d_num)
    print("   diary mnemonic %d tokens" % d_mne)
    return {"repo": repo, "arch": arch, "ctx": ctx,
            "code3": n_tok(tok, "311"), "pair": n_tok(tok, "45"),
            "diary_num": d_num, "diary_mne": d_mne}


def main():
    print("4J final verification round")
    try:
        check_cards()
    except Exception:
        traceback.print_exc()
    try:
        check_llama()
    except Exception:
        traceback.print_exc()

    try:
        found = discover_qwen3()
    except Exception:
        traceback.print_exc()
        found = []

    print()
    print("=" * 78)
    print("C2 -- Qwen3 tokenizer, same strings as every other row")
    print("=" * 78)
    todo = []
    for r in QWEN3_MEASURE + REFERENCE:
        if r not in todo:
            todo.append(r)
    for r in found:
        if r not in todo:
            todo.append(r)
    rows = []
    for repo in todo:
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
    print("SUMMARY")
    print("%-32s %-22s %8s %5s %5s %8s %9s"
          % ("model", "architecture", "context", "cd3", "pair", "diary_n", "diary_mne"))
    for r in rows:
        print("%-32s %-22s %8d %5d %5d %8d %9d"
              % (r["repo"], r["arch"], r["ctx"], r["code3"], r["pair"],
                 r["diary_num"], r["diary_mne"]))
    print()
    print("HOW TO READ IT")
    print(" 1. if Qwen3 still splits 311 into three tokens, Qwen3 changes nothing about the")
    print("    tokenizer argument and the OLMo advantage stands.")
    print(" 2. a repo that failed to load proves nothing about it. We could not look.")


if __name__ == "__main__":
    main()
