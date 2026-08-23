# Step 7, work item 7.2 — throughput comparison

🔴 **LEG-4 PILOT CONTEXT, BASE MODELS, EAGER MODE.** No adapter is loaded: the question is about the backbone's attention shape, which LoRA does not change. `torch.compile` is off for the reason in `FINDING 79`, so every diaries/second below is a **floor**. Both models were measured the same way, on the same prompts, under the same grammar, so the *comparison* is sound even though the absolute numbers are not a ceiling.

* prompts: **200**, drawn from the Step 5 prefix pool
* grammar: **constrained (completion root)**
* sampling: temperature 1.3, top_p 1.0, top_k 0, max_new_tokens 1200, seed 42

## The claim under test

The step document states OLMo 3 has **no grouped-query attention — 32 KV heads against Qwen's 4** — so its KV cache is *"about nine times larger per token"*, and that KV cache is what caps vLLM's concurrent batch. The table below reads both halves of that from the engine, not from the claim.

| metric | allenai/Olmo-3-1025-7B | Qwen/Qwen2.5-7B |
|---|---|---|
| attention heads | 32 | 28 |
| KV heads | 32 | 4 |
| GQA group size | 1.0 | 7.0 |
| layers | 32 | 28 |
| head dim | 128 | 128 |
| vocab size | 100278 | 152064 |
| **KV bytes / token** (bf16) | 524288 | 57344 |
|  |  |  |
| KV cache blocks | 29074 | 65126 |
| block size | 16 | 16 |
| **KV cache tokens** | 465184 | 1042016 |
| KV cache GiB | 227.141 | 55.650 |
| **max concurrency @ max_model_len** | 227.14 | 508.80 |
| torch peak allocated (GiB) | 0.000 | 0.000 |
|  |  |  |
| prompt tokens / diary | 16.20 | 18.09 |
| output tokens / diary | 100.73 | 140.62 |
| engine load (s) | 171.98 | 204.62 |
| generate (s) | 8.88 | 7.41 |
| **diaries / second** | 22.5331 | 26.9839 |
| output tokens / second | 2269.87 | 3794.35 |

## Reading

* **KV bytes per token**: `allenai/Olmo-3-1025-7B` is 9.14× `Qwen/Qwen2.5-7B`.
* **KV cache tokens**: `allenai/Olmo-3-1025-7B` is 0.45× `Qwen/Qwen2.5-7B`.
* **diaries per second**: `allenai/Olmo-3-1025-7B` is 0.84× `Qwen/Qwen2.5-7B`.
* **output tokens per diary**: `allenai/Olmo-3-1025-7B` is 0.72× `Qwen/Qwen2.5-7B`.

🔴 The tokenizers differ, so *output tokens per diary* is the token-saving half of the trade and *KV bytes per token* is the cost half. Neither one decides on its own; **diaries per second** and **max concurrency** are what the campaign is sized from.
