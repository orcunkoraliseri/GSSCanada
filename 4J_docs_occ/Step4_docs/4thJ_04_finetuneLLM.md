# Step 4 — Model: the fine-tuned open-weight LLM

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 4. Validation: `4thJ_04_finetuneLLM_val.md`

---

## STATUS

**✅ FAMILY DECIDED 2026-08-14 by our own measurement. ✅ RECIPE DECIDED by `RL05`. ✅ LEGS FIXED by
the author. Implementation OPEN, nothing trained.**

---

## AIM

One model, fine-tuned once, that emits a serialised diary conditioned on a person.

Not the best possible generative model of a diary — `RL06` is explicit that a from-scratch 10 M
conditional Transformer beats it on fidelity, cost, throughput and structural validity. **The LLM has
exactly one justification, cross-national transfer, and this step exists to make Step 6 possible.**

---

## THE TWO LEGS

Series numbering continues from 3J, which ended at Leg-3.

| Leg | Checkpoint | Params | Role |
|---|---|---|---|
| **Leg-4, pilot** | `allenai/OLMo-2-0425-1B` | 1.48 B | Shakes out the pipeline. **Byte-identical tokenizer and vocabulary to Leg-5**, so the Step 3 corpus is used unchanged and never regenerated between legs |
| **Leg-5, reported** | `allenai/Olmo-3-1025-7B` | 7.30 B | The model the paper reports |

🔴 **Two things Leg-4 cannot tell us, and they must not be read off it.** Its context is **4,096**,
which caps sequence packing; and `Olmo2ForCausalLM` routes to vLLM's **generic Transformers fallback**
while `Olmo3ForCausalLM` has a native kernel. **No throughput, latency or packing number from Leg-4
extrapolates to Leg-5.** Leg-4 validates correctness: does the grammar hold, do the detectors fire,
does the conditioning bite.

---

## WHY THIS BACKBONE — THE MEASUREMENT, NOT THE REPORT

| Repo | `311` | Diary | Licence | Gated | vLLM | Context |
|---|---|---|---|---|---|---|
| **`allenai/Olmo-3-1025-7B`** | **1 tok** | **200** | Apache 2.0 | no | **native `olmo3`** | 65,536 (sliding 4,096) |
| `allenai/OLMo-2-0425-1B` | 1 tok | 200 | Apache 2.0 | no | ❌ generic fallback | 4,096 |
| `Qwen/Qwen2.5-7B` | 3 tok | 303 | Apache 2.0 | no | native `qwen2` | 131,072 |
| `mistralai/Mistral-7B-v0.3` | 4 tok | 304 | Apache 2.0 | no | — | — |
| `meta-llama/Llama-3.1-8B` | *not measured* | — | Community | **manual gate** | native | 131,072 |

Speed jobs `1234177`, `1234192`, `1234199`, `1234211`, `1234216`, `1234219`. Scripts in `../tools/`.

🔴 **`RL18` recommended `Qwen/Qwen2.5-7B` and was wrong twice** — a mis-counted token figure, and a
Llama licence clause that does not exist in Llama 3.1. Both are documented in the parent document's
second-round vetting record. **`Qwen/Qwen2.5-7B` is retained as the named comparison arm**, not
discarded: the paper reports what the alternative would have cost.

🔴 **The cost of this choice, and it is real.** `Olmo-3-1025-7B` has **no grouped-query attention** —
32 KV heads against Qwen's 4, head dimension 128 in both. KV cache per token:

* OLMo 3 7B: 2 × 32 × 32 × 128 × 2 = **512 KB/token**
* Qwen 2.5 7B: 2 × 28 × 4 × 128 × 2 = **56 KB/token**

About **nine times** more, against which the 34 % token saving buys back only part. This is arithmetic
from measured config values, **not a benchmark**, and it bears on Step 7 where KV cache limits the
concurrent batch. **Action: run the vLLM throughput comparison on Leg-5 checkpoints before Step 7 is
sized.**

---

## THE RECIPE — DECIDED BY `RL05`, DO NOT RELITIGATE

* **Base checkpoint, never instruct.** RLHF and DPO alignment suppress tail entropy and pull toward
  modal output, which is precisely the failure Tier 2 exists to catch. This is an argument, not a
  preference.
* **SFT with completion-only loss masking.** The prefix is ~25 tokens and the body 200 to 500;
  computing loss on static demographic keys wastes capacity.
* **rsLoRA, r = 32, on all linear layers** (`q,k,v,o,gate,up,down`). Attention-only LoRA underfits.
  Rank-stabilised scaling because plain α/r slows learning above r = 32.
* **Full fine-tuning with 8-bit AdamW as the CEILING run**, not the primary. `RL05` is explicit that
  LoRA underfits when the target is far from the pretraining distribution, and our target is about as
  far as it gets. It fits in 80 GB, so **it is a measurement we can afford and therefore must make.**
* **QLoRA rejected** — for sufficiency (we have 80 GB), not on `RL05`'s degradation figure, which
  rests partly on an unverifiable Tier-3 source.
* **Packed sequences with block-diagonal attention masks.** Removes ~60 % padding waste without
  cross-contamination between diaries.
* **bf16.** V100 and P6 nodes have no hardware bf16.
* 🔴 **Joint multi-country training, never sequential.** Sequential costs 40 to 70 % on earlier
  countries. One model, country token in the prefix.

🔴 **The memory arithmetic in `RL18` is for Qwen2.5-7B and does not transfer unchecked.** It gives
18.27 GB LoRA / 48.86 GB full FT. OLMo 3 7B is slightly smaller in parameters but has no GQA and uses
sliding-window attention, so the activation and cache terms differ. **Both still fit in one 80 GB
slice, which is the conclusion that matters. Re-derive the specific numbers on the actual model
before sizing a sweep.**

---

## HARDWARE, MEASURED 2026-08-13

`sinfo -N -o '%N|%P|%f|%G|%m|%T'`. Not an estimate.

| Nodes | Partitions | GPU | Per node |
|---|---|---|---|
| `speed-37`, `speed-39`-`43` | `ps`, `pt`, `cl` | **A100 MIG** | `nvidia_a100_7g.80gb` ×1, `2g.20gb` ×9, `1g.20gb` ×3 |
| `xailab` | `ps`, `cl`, `xi` | RTX 6000 48 GB | ×4 |

**Large slot for training, 20 GB slices for sweeps and the leave-one-country-out array.**

* 🔴 **No distributed training across MIG slices.** There is no peer-to-peer path between slices of
  one physical GPU. One instance, one job.
* 🔴 **Never request multi-GPU on the Tesla P6 nodes** (`speed-01`, `05`, `17`) — `RL11` reports
  `DataParallel` crashes the physical node.
* **Everything offline**: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HOME` and `TORCH_HOME` on
  `/speed-scratch`, weights pre-staged. Compute nodes have no outbound network.
* **`--signal=B:SIGUSR1@600`** with a checkpoint-and-exit handler, plus periodic stateful checkpoints
  including optimizer, scheduler, RNG **and sampler position**.
* `/speed-scratch` purges after 90 days.

---

## WORK ITEMS

### 4.1 — Pre-stage weights

Both checkpoints downloaded on the login node and placed under `/speed-scratch/o_iseri/hf_cache`.
Record the revision hash of each. 🔴 **A model repo can be updated in place; a checkpoint named
without a revision is not a reproducible checkpoint.**

### 4.2 — Leg-4 pilot run

Full pipeline, small model, short schedule. **The success criterion is not a metric — it is that
every detector in 4.4 fires when it should and stays silent when it should not.**

### 4.3 — Leg-5 primary run and the ceiling run

* Primary: rsLoRA r=32, all linear, 3 epochs, packed, bf16.
* Ceiling: full fine-tune, 8-bit AdamW, same data, same schedule.
* Comparison arm: `Qwen/Qwen2.5-7B`, same recipe, so the paper can state what the alternative cost.

### 4.4 — In-run detectors, wired before the first run

Each must fire **within one training run**, not at evaluation.

1. **Low loss, degenerate output.** Delimiters are most of the sequence, so loss can fall while
   content collapses. Log validation perplexity **separately for delimiter tokens and activity-code
   tokens**, plus the entropy of generated activity sequences. Automatic halt if delimiter loss
   < 0.05 while activity entropy < 1.5 nats.
2. 🔴 **Distribution collapse.** Within-stratum variance ratio against real data, logged **every
   validation epoch as a training metric**. This is the failure that would silently destroy the paper.
3. **Catastrophic forgetting.** Largely designed out by joint training; a fixed probe set per country
   is still scored at every checkpoint.
4. **Tokenizer mismatch.** Assert `tokenize(detokenize(ids)) == ids` on 1,000 cases before any large
   generation run.
5. **Training on padding.** Assert every pad and prompt position carries label `-100`.
6. **Adapter merge drift.** Score merged and unmerged on the same fixed sample; require max logit
   difference < 1e-4.
7. **Missing EOS.** Assert 100 % of training completions terminate.

> The shape of these is inherited: the 3J wiring gate exists because a Leg-2 bug passed every
> input-side check and was only caught output-side. **Instrument the output, not the intent.**

### 4.5 — Conditioning diagnostics, on the first trained model

Our whole claim is that demographics drive the schedule.

1. **Shuffled-prefix test.** Score test diaries under permuted demographic prefixes. Cross-entropy
   must rise sharply. **If it does not, the model is ignoring the conditioning and nothing downstream
   matters.**
2. **Slot-wise mutual information** between conditioning attributes and generated activity, compared
   to the empirical curve, **watching the evening slots specifically.** Demographically appropriate
   mornings and generic evenings is the exact failure shape.

Named fallback if conditioning proves weak: classifier-free guidance at decode time.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step4/leg5_adapter/` | Step 7. 🔴 **Never released** — `RL10` |
| `outputs_step4/training_metrics.csv` | Step 4 validation |
| `outputs_step4/conditioning_diagnostics.md` | Step 5, Step 6 |
| `outputs_step4/throughput_leg5.md` | Step 7 campaign sizing |

---

## WHAT BLOCKS THIS STEP

Step 3's corpus.

**What this step blocks:** Steps 6 and 7 entirely.

---

## DEFINITION OF DONE

1. Leg-4 completes and every detector in 4.4 has been **seen firing** on a deliberately broken input.
2. Leg-5 primary and ceiling runs complete inside the seven-day walltime.
3. Conditioning diagnostics run and reported, including the evening-slot check.
4. The vLLM throughput comparison against `Qwen/Qwen2.5-7B` recorded.
5. All Step 4 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* Backbone, legs and recipe all fixed. Nothing trained.
* 🔴 The KV-cache arithmetic above is **derived from measured config values, not benchmarked.** It is
  written here rather than in a footnote because it is the one number that could reverse the backbone
  choice, and it is the one number we have not run.
