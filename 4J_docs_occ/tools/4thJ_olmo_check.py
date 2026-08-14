#!/usr/bin/env python
"""
4J: the two checks that decide whether OLMo 2 can displace Qwen2.5 as the backbone.

The tokenizer measurement (job 1234177) showed allenai/OLMo-2-1124-7B writes a 3-digit
activity code in ONE token (200-token diary against Qwen's 303) and is Apache 2.0.
Before acting on that, two things RL18 never checked:

  CHECK A  context window and family sizes.
           OLMo 2 is reputed to be 4096, against Qwen2.5's 32768. 4096 is ample for one
           300-token diary but it caps how many diaries we can pack per sequence, and it
           caps few-shot prompting at generation time. Also: does the family HAVE a small
           pilot size, the way Qwen gives us 0.5B and 1.5B for Leg 4?

  CHECK B  serving stack. We plan vLLM + XGrammar for constrained generation. If vLLM does
           not register the OLMo 2 architecture, the whole generation leg has no engine.

Read from the model configs and from the vLLM / XGrammar sources themselves, not from a
report. CPU only, no GPU, a few minutes.

Run with sbatch. Never on the login node.
"""

import sys
import traceback
import urllib.request

CONFIGS = [
    ("allenai/OLMo-2-0425-1B",      "OLMo 2, candidate Leg-4 pilot size"),
    ("allenai/OLMo-2-1124-7B",      "OLMo 2, the row that started this"),
    ("allenai/OLMo-2-1124-13B",     "OLMo 2, next size up"),
    ("allenai/OLMo-2-0325-32B",     "OLMo 2, largest"),
    ("Qwen/Qwen2.5-0.5B",           "Qwen, current Leg-4 pilot"),
    ("Qwen/Qwen2.5-7B",             "Qwen, current first choice"),
]

FIELDS = [
    "architectures", "max_position_embeddings", "rope_theta", "sliding_window",
    "vocab_size", "hidden_size", "num_hidden_layers", "num_attention_heads",
    "num_key_value_heads", "tie_word_embeddings", "torch_dtype",
]

# Sources we read directly. Raw files, one request each.
SOURCES = [
    ("vLLM model registry",
     "https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/models/registry.py",
     ["Olmo", "Qwen2ForCausalLM", "Qwen3"]),
    ("XGrammar tokenizer_info",
     "https://raw.githubusercontent.com/mlc-ai/xgrammar/main/python/xgrammar/tokenizer_info.py",
     ["VocabType", "BYTE_LEVEL", "BYTE_FALLBACK", "RAW", "detect"]),
]


def check_configs():
    from transformers import AutoConfig

    print("=" * 78)
    print("CHECK A -- context window, and whether the family has a pilot size")
    print("=" * 78)
    rows = []
    for repo, note in CONFIGS:
        print("-" * 78)
        print("MODEL  %s" % repo)
        print("NOTE   %s" % note)
        try:
            cfg = AutoConfig.from_pretrained(repo)
        except Exception as exc:
            print("STATUS COULD NOT LOAD -- %s: %s" % (type(exc).__name__, str(exc)[:200]))
            print("       (repo may not exist under this name, or is gated, or no network)")
            continue
        print("STATUS exists")
        d = cfg.to_dict()
        for f in FIELDS:
            if f in d:
                print("   %-24s %s" % (f, d[f]))
        rows.append({
            "repo": repo,
            "arch": (d.get("architectures") or ["?"])[0],
            "ctx": d.get("max_position_embeddings", 0),
            "params_hint": d.get("num_hidden_layers", 0),
        })
    return rows


def check_sources():
    print()
    print("=" * 78)
    print("CHECK B -- does the serving stack know these architectures")
    print("=" * 78)
    for name, url, needles in SOURCES:
        print("-" * 78)
        print("SOURCE %s" % name)
        print("URL    %s" % url)
        try:
            with urllib.request.urlopen(url, timeout=60) as fh:
                text = fh.read().decode("utf-8", "replace")
        except Exception as exc:
            print("STATUS COULD NOT FETCH -- %s: %s" % (type(exc).__name__, str(exc)[:200]))
            print("       (compute node may have no outbound network to github)")
            continue
        print("STATUS fetched, %d bytes" % len(text))
        lines = text.splitlines()
        for needle in needles:
            hits = [l.strip() for l in lines if needle in l]
            print("   %-18s %d matching lines" % (needle, len(hits)))
            for h in hits[:8]:
                print("      | %s" % h[:110])


def main():
    print("4J OLMo-2 vs Qwen2.5 backbone check")
    try:
        import transformers
        print("transformers version: %s" % transformers.__version__)
    except Exception:
        print("FATAL: transformers not importable")
        traceback.print_exc()
        sys.exit(1)

    rows = []
    try:
        rows = check_configs()
    except Exception:
        print("UNEXPECTED FAILURE in CHECK A")
        traceback.print_exc()

    try:
        check_sources()
    except Exception:
        print("UNEXPECTED FAILURE in CHECK B")
        traceback.print_exc()

    print()
    print("=" * 78)
    print("SUMMARY")
    print("%-28s %-26s %10s" % ("model", "architecture", "context"))
    for r in rows:
        print("%-28s %-26s %10d" % (r["repo"], r["arch"], r["ctx"]))
    print()
    print("HOW TO READ IT")
    print(" A1. context: 4096 is enough for one ~300-token diary, but at 32768 we can pack")
    print("     ~100 diaries per sequence instead of ~13, which changes training throughput.")
    print(" A2. a family without a 0.5B-to-1.5B member cannot give us the cheap Leg-4 pilot.")
    print(" A3. an architecture absent from the vLLM registry has no generation engine for us.")
    print(" A row that failed to load or fetch proves nothing. It only means we could not look.")


if __name__ == "__main__":
    main()
