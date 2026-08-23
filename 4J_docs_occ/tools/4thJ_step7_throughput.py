# -*- coding: utf-8 -*-
"""Step 7, work item 7.2 -- the throughput comparison, before the campaign is sized.

  usage: python 4thJ_step7_throughput.py --step2 DIR --prefixes FILE --out DIR
                                         [--n 200] [--models a,b]

🔴 The claim this exists to test, in the step document's own words: *"`Olmo-3-1025-7B`
has no grouped-query attention -- 32 KV heads against Qwen's 4 -- so its KV cache
is about nine times larger per token, against which the 34 % token saving buys
back only part. KV cache is what limits vLLM's concurrent batch."*

So the two numbers that matter are NOT both throughput. They are:

  * **diaries/second** on the same prompts under the same grammar, and
  * **the KV cache the engine could actually allocate**, in tokens, which is what
    caps concurrency and therefore what sizes the campaign.

Both are read from the engine rather than from the log, and every one of them is
guarded with `getattr` -- vLLM moves these attributes between minor versions and a
`throughput_comparison.md` containing a silently-defaulted zero would be worse
than no file at all.

🔴 **The BASE models are compared, with no adapter.** The question is about the
backbone's attention shape, which the LoRA does not change; loading a fold adapter
would make the two rows differ by adapter as well as by backbone.

🔴 **Eager mode.** `FINDING 79`: `envs/step7` shares `envs/step4`'s stdlib and
dynamo refuses to trace it. Both models are measured the same way, so the
COMPARISON is sound, but the absolute diaries/s is a floor, not a ceiling, and the
generated document says so on its own face.
"""

import argparse
import importlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

grammar = importlib.import_module("4thJ_step7_grammar")
ebnf = importlib.import_module("4thJ_step7_ebnf")

DEFAULT_MODELS = ["allenai/Olmo-3-1025-7B", "Qwen/Qwen2.5-7B"]


class NotRun(RuntimeError):
    pass


def engine_facts(llm):
    """Everything the sizing decision needs, each one guarded. A missing field is
    reported as `null` and named, never defaulted to a number."""
    out = {}
    cfg = getattr(getattr(llm, "llm_engine", None), "vllm_config", None)
    cache = getattr(cfg, "cache_config", None)
    model = getattr(cfg, "model_config", None)
    par = getattr(cfg, "parallel_config", None)

    blocks = getattr(cache, "num_gpu_blocks", None)
    bsize = getattr(cache, "block_size", None)
    out["num_gpu_blocks"] = blocks
    out["block_size"] = bsize
    out["kv_cache_tokens"] = (blocks * bsize) if (blocks and bsize) else None
    out["gpu_memory_utilization"] = getattr(cache, "gpu_memory_utilization", None)
    out["max_model_len"] = getattr(model, "max_model_len", None)
    out["dtype"] = str(getattr(model, "dtype", None))
    out["tensor_parallel_size"] = getattr(par, "tensor_parallel_size", None)
    if out["kv_cache_tokens"] and out["max_model_len"]:
        out["max_concurrency_at_max_len"] = round(
            out["kv_cache_tokens"] / float(out["max_model_len"]), 2)

    # The attention shape the comparison is ABOUT. Read from the HF config the
    # engine loaded, not from a table in a document.
    hf = getattr(model, "hf_config", None) or getattr(model, "hf_text_config", None)
    for k in ("num_attention_heads", "num_key_value_heads", "hidden_size",
              "num_hidden_layers", "head_dim", "vocab_size"):
        out[k] = getattr(hf, k, None)
    if out.get("num_attention_heads") and out.get("num_key_value_heads"):
        out["gqa_group_size"] = out["num_attention_heads"] / float(out["num_key_value_heads"])
    # bytes of KV per token = 2 (K and V) * layers * kv_heads * head_dim * 2 (bf16)
    hd = out.get("head_dim")
    if hd is None and out.get("hidden_size") and out.get("num_attention_heads"):
        hd = out["hidden_size"] // out["num_attention_heads"]
        out["head_dim"] = hd
    # `FINDING 97`: OLMo 3 is a HYBRID -- its config carries `layer_types` with
    # 24 `sliding_attention` layers (window 4096) against 8 `full_attention`.
    # Deriving from `num_hidden_layers` alone reported a pool 3.05x the size of
    # the physical card. The uniform figure is KEPT, under a name that says what
    # it assumes, so the old number stays readable next to the corrected one.
    lt = getattr(hf, "layer_types", None)
    out["sliding_window"] = getattr(hf, "sliding_window", None)
    if lt:
        counts = {}
        for name in lt:
            counts[name] = counts.get(name, 0) + 1
        out["layer_types"] = counts
        out["full_attention_layers"] = counts.get("full_attention", 0)
        out["hybrid_attention"] = len(counts) > 1
    else:
        out["layer_types"] = None
        out["full_attention_layers"] = out.get("num_hidden_layers")
        out["hybrid_attention"] = False
    if hd and out.get("num_hidden_layers") and out.get("num_key_value_heads"):
        kvh = out["num_key_value_heads"]
        out["kv_bytes_per_token_all_layers_assumption"] = (
            2 * out["num_hidden_layers"] * kvh * hd * 2)
        full = out.get("full_attention_layers") or out["num_hidden_layers"]
        out["kv_bytes_per_token"] = 2 * full * kvh * hd * 2
    return out


def measure(repo, prompts, text, sp_kwargs, gpu_mem, max_len):
    import torch
    from vllm import LLM, SamplingParams
    import gc

    t0 = time.time()
    llm = LLM(model=repo, dtype="bfloat16", gpu_memory_utilization=gpu_mem,
              max_model_len=max_len, seed=sp_kwargs["seed"], enforce_eager=True)
    load_s = time.time() - t0

    facts = engine_facts(llm)
    tok = llm.get_tokenizer()
    prompt_tokens = sum(len(tok.encode(p)) for p in prompts)

    kw = dict(sp_kwargs)
    if text is not None:
        from importlib import import_module
        gen = import_module("4thJ_step7_generate")
        _, extra = gen.structured_params(text)
        kw.update(extra)
    params = SamplingParams(**kw)

    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    outs = llm.generate(prompts, params)
    gen_s = time.time() - t0
    peak = torch.cuda.max_memory_allocated()
    # `FINDING 97`: this is 0.0 on vLLM v1 -- the model lives in a WORKER process
    # and the parent's allocator never sees it. A structurally null field must not
    # be printed as a measured zero. The device counters below are the real ones.
    free_b, total_b = torch.cuda.mem_get_info()

    out_tokens = sum(len(o.outputs[0].token_ids) for o in outs)
    row = dict(
        model=repo, n=len(outs),
        engine_load_seconds=round(load_s, 2),
        generate_seconds=round(gen_s, 2),
        diaries_per_second=round(len(outs) / max(gen_s, 1e-9), 4),
        prompt_tokens_total=prompt_tokens,
        prompt_tokens_mean=round(prompt_tokens / float(len(prompts)), 2),
        output_tokens_total=out_tokens,
        output_tokens_mean=round(out_tokens / float(len(outs)), 2),
        output_tokens_per_second=round(out_tokens / max(gen_s, 1e-9), 2),
        torch_peak_allocated_gib=(round(peak / (1024. ** 3), 3) if peak else None),
        torch_peak_is_null_in_parent_process=(not peak),
        device_total_gib=round(total_b / (1024. ** 3), 3),
        device_used_gib=round((total_b - free_b) / (1024. ** 3), 3),
    )
    row.update(facts)
    if row.get("kv_cache_tokens") and row.get("kv_bytes_per_token"):
        row["kv_cache_gib"] = round(
            row["kv_cache_tokens"] * row["kv_bytes_per_token"] / (1024. ** 3), 3)
        if row.get("kv_bytes_per_token_all_layers_assumption"):
            row["kv_cache_gib_all_layers_assumption"] = round(
                row["kv_cache_tokens"]
                * row["kv_bytes_per_token_all_layers_assumption"] / (1024. ** 3), 3)
        # 🔴 The guard `FINDING 97` should have had. A KV pool cannot exceed the
        # device. If it does, the DERIVATION is wrong, not the card -- say so
        # loudly and record it rather than emitting an impossible number.
        row["kv_cache_gib_exceeds_device"] = bool(
            row.get("device_total_gib") and row["kv_cache_gib"] > row["device_total_gib"])
        if row["kv_cache_gib_exceeds_device"]:
            print("🔴 REFUSED AS A MEASUREMENT: derived KV pool %.3f GiB > device %.3f GiB"
                  % (row["kv_cache_gib"], row["device_total_gib"]))

    del llm
    gc.collect()
    torch.cuda.empty_cache()
    return row


def markdown(rows, cfg, n, constrained):
    L = []
    L.append("# Step 7, work item 7.2 — throughput comparison\n")
    L.append("🔴 **LEG-4 PILOT CONTEXT, BASE MODELS, EAGER MODE.** No adapter is loaded: "
             "the question is about the backbone's attention shape, which LoRA does not "
             "change. `torch.compile` is off for the reason in `FINDING 79`, so every "
             "diaries/second below is a **floor**. Both models were measured the same "
             "way, on the same prompts, under the same grammar, so the *comparison* is "
             "sound even though the absolute numbers are not a ceiling.\n")
    L.append("* prompts: **%d**, drawn from the Step 5 prefix pool" % n)
    L.append("* grammar: **%s**" % ("constrained (completion root)" if constrained else "OFF"))
    L.append("* sampling: temperature %s, top_p %s, top_k %s, max_new_tokens %s, seed %s\n"
             % (cfg["temperature"], cfg["top_p"], cfg["top_k"],
                cfg["max_new_tokens"], cfg["generation_seed"]))

    L.append("## The claim under test\n")
    L.append("The step document states OLMo 3 has **no grouped-query attention — 32 KV heads "
             "against Qwen's 4** — so its KV cache is *\"about nine times larger per token\"*, "
             "and that KV cache is what caps vLLM's concurrent batch. The table below "
             "reads both halves of that from the engine, not from the claim.\n")
    L.append("\U0001f534 **`FINDING 97`: the nine is wrong, and the table below "
             "is the corrected one.** OLMo 3 is a **hybrid** -- its `layer_types` are "
             "24 `sliding_attention` (window 4096) against 8 `full_attention`. Deriving "
             "KV bytes from `num_hidden_layers` alone reported a pool **3.05x the "
             "physical card**. Every `KV bytes / token` and `KV cache GiB` below counts "
             "the **full-attention layers only**; the old uniform-layer figure is kept "
             "beside it under a name that says what it assumes.\n")

    hdr = ["metric"] + [r["model"] for r in rows]
    L.append("| " + " | ".join(hdr) + " |")
    L.append("|" + "---|" * len(hdr))

    def line(label, key, fmt="%s"):
        vals = []
        for r in rows:
            v = r.get(key)
            vals.append("**NOT REPORTED BY THIS vLLM**" if v is None else (fmt % v))
        L.append("| %s | %s |" % (label, " | ".join(vals)))

    line("attention heads", "num_attention_heads")
    line("KV heads", "num_key_value_heads")
    line("GQA group size", "gqa_group_size", "%.1f")
    line("layers", "num_hidden_layers")
    line("of which **full-attention**", "full_attention_layers")
    line("sliding window", "sliding_window")
    line("head dim", "head_dim")
    line("vocab size", "vocab_size", "%d")
    line("**KV bytes / token** (bf16, full layers)", "kv_bytes_per_token", "%d")
    line("KV bytes / token *if all layers were full*", "kv_bytes_per_token_all_layers_assumption", "%d")
    L.append("|  |" + "  |" * len(rows))
    line("KV cache blocks", "num_gpu_blocks")
    line("block size", "block_size")
    line("**KV cache tokens**", "kv_cache_tokens", "%d")
    line("KV cache GiB", "kv_cache_gib", "%.3f")
    line("KV cache GiB *if all layers were full*", "kv_cache_gib_all_layers_assumption", "%.3f")
    line("\U0001f534 derived pool exceeds the device", "kv_cache_gib_exceeds_device")
    line("**max concurrency @ max_model_len**", "max_concurrency_at_max_len", "%.2f")
    line("device total (GiB)", "device_total_gib", "%.3f")
    line("**device used after load (GiB)**", "device_used_gib", "%.3f")
    line("torch peak allocated (GiB), parent process", "torch_peak_allocated_gib", "%.3f")
    L.append("|  |" + "  |" * len(rows))
    line("prompt tokens / diary", "prompt_tokens_mean", "%.2f")
    line("output tokens / diary", "output_tokens_mean", "%.2f")
    line("engine load (s)", "engine_load_seconds", "%.2f")
    line("generate (s)", "generate_seconds", "%.2f")
    line("**diaries / second**", "diaries_per_second", "%.4f")
    line("output tokens / second", "output_tokens_per_second", "%.2f")

    L.append("\n## Reading\n")
    if len(rows) == 2:
        a, b = rows
        for key, label, fmt in (("kv_bytes_per_token", "KV bytes per token", "%.2f×"),
                                ("kv_cache_tokens", "KV cache tokens", "%.2f×"),
                                ("diaries_per_second", "diaries per second", "%.2f×"),
                                ("output_tokens_mean", "output tokens per diary", "%.2f×")):
            x, y = a.get(key), b.get(key)
            if x and y:
                L.append("* **%s**: `%s` is %s `%s`."
                         % (label, a["model"], fmt % (x / float(y)), b["model"]))
    L.append("\n🔴 The tokenizers differ, so *output tokens per diary* is the token-saving "
             "half of the trade and *KV bytes per token* is the cost half. Neither one "
             "decides on its own; **diaries per second** and **max concurrency** are what "
             "the campaign is sized from.\n")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--step2", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--prefixes", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument("--gpu-mem", type=float, default=0.90)
    ap.add_argument("--max-model-len", type=int, default=2048)
    ap.add_argument("--no-grammar", action="store_true")
    a = ap.parse_args(argv)

    with open(a.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    gen = importlib.import_module("4thJ_step7_generate")
    prefixes, pool = gen.load_prefixes(a.prefixes, a.n, cfg.get("prompt_seed", 42))
    prompts = [r["prefix"] + grammar.PREFIX_BODY_SEP for r in prefixes]

    alph = grammar.build_alphabets(a.step2)
    text = None if a.no_grammar else ebnf.build_ebnf(alph, whole_record=False)

    print("=" * 78)
    print("Step 7.2 throughput comparison -- %d prompts from a pool of %d" % (len(prompts), pool))
    print("models: %s" % a.models)
    print("grammar: %s" % ("OFF" if a.no_grammar else "%d chars, completion root" % len(text)))
    print("=" * 78)

    sp_kwargs = dict(temperature=cfg["temperature"], top_p=cfg["top_p"],
                     top_k=cfg["top_k"] if cfg["top_k"] else -1,
                     max_tokens=cfg["max_new_tokens"], seed=cfg["generation_seed"],
                     stop=[grammar.EOR], include_stop_str_in_output=True)

    rows = []
    for repo in a.models.split(","):
        print("\n" + "-" * 78)
        print("measuring %s" % repo)
        print("-" * 78)
        rows.append(measure(repo, prompts, text, sp_kwargs, a.gpu_mem, a.max_model_len))
        print(json.dumps(rows[-1], indent=2, sort_keys=True))

    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, "throughput_comparison.json")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(dict(rows=rows, n=len(prompts), constrained=not a.no_grammar,
                       sampling=sp_kwargs, prefix_pool=pool), fh, indent=2, sort_keys=True,
                  default=str)
    mp = os.path.join(a.out, "throughput_comparison.md")
    with open(mp, "w", encoding="utf-8") as fh:
        fh.write(markdown(rows, cfg, len(prompts), not a.no_grammar))
    print("\nwritten: %s\nwritten: %s" % (jp, mp))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotRun as e:
        print("THROUGHPUT COMPARISON NOT RUN -- %s" % e)
        sys.exit(2)
