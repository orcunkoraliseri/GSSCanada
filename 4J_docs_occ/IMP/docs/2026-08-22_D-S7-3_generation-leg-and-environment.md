# `D-S7-3` — for the author, 2026-08-22

## Step 7 cannot generate a single diary today, and the question is not *how* to unblock it but *on which model* — the only adapters that exist are the **Leg-4 pilot**

**Scope** one decision, in full. Nothing in this file changes any artefact.
`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched and stays untouched whatever is ruled.

| | |
|---|---|
| **Raised by** | working out what "continue Step 7" concretely means, 2026-08-22 |
| **Blocks** | Step 7 items 7.2–7.7, and through them Step 6 items 6.3, 6.4, 6.5, and Steps 8 and 9 |
| **Does not block** | anything already closed — Steps 1, 2, 3, 5, Step 6 items 6.1 and 6.2 |
| **Record** | `Step7_docs/4thJ_07_constrainedGeneration.md`, work items 7.2 and 7.3 |

🔴 **First, a correction I owe you.** In this conversation I twice said `D-S7-2` was still open. **It is
not.** You ruled it **(a)** on 2026-08-20 — the travel requirement is dropped from the grammar and
`G7.3` became a reported rate — and it is applied in `tools/4thJ_step7_grammar.py`. I was reading a
stale line. The one artefact that still said "open" was the `G7.3` row of
`4thJ_07_constrainedGeneration_val.md`; it has been corrected to record the ruling. **This document
replaces the `D-S7-2` document you asked for, because that decision is already made.**

---

## 1. What is actually on disk, verified by listing rather than assumed

### The environment on Speed

`/speed-scratch/o_iseri/envs/step4/lib/python3.10/site-packages/`:

| package | present | needed for |
|---|---|---|
| `torch`, `transformers`, `peft`, `accelerate` | 🟢 yes | what Step 4 already did |
| `vllm` | 🔴 **NO** | items 7.2, 7.3 — the whole generation campaign |
| `xgrammar` | 🔴 **NO** | the constraint machinery, and `G7.10` (oracle agreement) |
| `bitsandbytes` | 🔴 **NO** | Leg-5 training at 7 B |

⚪ **One thing I had recorded wrongly and have now checked:** the note that the ceiling run "needs
`nvidia_a100_7g.80gb` and has neither" is **half wrong**. `sinfo` shows
`gpu:nvidia_a100_7g.80gb:1` on `speed-[37,39-43]` in partition `ps`, one slice per node. **The 80 GB
MIG slice exists and is requestable.** Only `bitsandbytes` is missing, and that is a `pip install`.

### The adapters

All three LOCO folds are trained and their runs completed. **They are Leg-4.**
`Step5_docs/outputs_step5/generation_config_es.json` names
`"base_repo": "allenai/OLMo-2-0425-1B"`, revision `a1847dff35000b4271fa70afc5db10fd29fedbdf`.

`Step4_docs/4thJ_04_finetuneLLM.md:34-44` is explicit about what that is:

> | **Leg-4, pilot** | `allenai/OLMo-2-0425-1B` | 1.48 B | Shakes out the pipeline |
> | **Leg-5, reported** | `allenai/Olmo-3-1025-7B` | 7.30 B | **The model the paper reports** |
>
> 🔴 *Two things Leg-4 cannot tell us … Its context is 4,096 … and `Olmo2ForCausalLM` routes to
> vLLM's generic Transformers fallback while `Olmo3ForCausalLM` has a native kernel. No throughput,
> latency or packing number from Leg-4 extrapolates to Leg-5. Leg-4 validates correctness.*

🔴 **So the model we have is, by our own written plan, the pilot — and it is specifically the one the
plan says throughput cannot be measured on.** Item 7.2 exists to compare `Olmo-3-1025-7B` against
`Qwen2.5-7B`; neither has been trained.

## 2. Why this is a decision and not a task

Unblocking the environment is mechanical: install `vllm`, `xgrammar`, `bitsandbytes` into a Step 7
env, one `sbatch`. What is **not** mechanical is what runs first afterwards, because Step 6's items
6.3–6.5 have never been executed even once, on any model. Every one of their gates — the three nulls'
margins, the joint-structure scores, the fictional-country control, the four privacy attacks with
their three controls — has been **built or specified but never run against generated text**. The same
is true of `G7.5`–`G7.13`: `G7.13` has been run on the real corpus and seen failing twice, but 🔴
**never against a generated batch**, which the Step 7 progress log states plainly.

**Discovering a defect in that machinery during the Leg-5 campaign is the expensive way to discover
it.** `FINDING 1` is the precedent: a plain `[:4000]` cap on a country-ordered shard nearly trained
the pilot on Italy alone, and it was the `V4.f` vacuity guard that caught it, not the threshold.

## 3. The options

### 🟢 (a) — RECOMMENDED: build the environment, then run the WHOLE chain on Leg-4 as a rehearsal, then Leg-5 for the paper

1. Build `envs/step7` with `vllm` + `xgrammar` (+ `bitsandbytes` for later), one `sbatch`.
2. `G7.10` — oracle versus XGrammar on 10,000 strings. It needs no adapter at all, only the grammar
   that is already built and green at 44/44. **It is the cheapest gate in the step and it is
   currently the only one that can run.**
3. Generate a **small** batch per fold with the existing Leg-4 adapters. Run every Step 7 gate and
   then Step 6 items 6.3, 6.4 and 6.5 end to end on it.
4. Train Leg-5, re-run the identical chain, and **that** is the paper.

* **Why:** it turns 6.3–6.5 from never-executed into rehearsed, at 1.48 B instead of 7.30 B, before
  any expensive run. It also front-loads the privacy audit, which is the item most likely to return an
  unpleasant surprise and the one that gates release.
* 🔴 **The condition that makes it safe:** every number from the Leg-4 pass is stamped
  **`LEG-4 PILOT — NOT REPORTABLE`** in the artefact itself, not just in a doc. The risk of a
  rehearsal is that a rehearsal number gets quoted; that risk is handled in the file format, the way
  `marginals_source` handles it for the nulls.
* **Cost:** one extra generation pass at 1 B. Small.
* ⚪ It costs **nothing** in Step 6 terms: the nulls are built from real diaries and do not depend on
  which model generated anything, so no null is rebuilt between the two passes.

### ⚪ (b) — Build the environment, train Leg-5 first, run the chain once

* **Why:** no rehearsal numbers exist to be misquoted, and no time is spent on a model the paper does
  not report.
* 🔴 **Cost:** the first execution of 6.3, 6.4, 6.5, the privacy audit and nine Step 7 gates happens
  on the run that matters, at 7 B. Any defect found there costs a 7 B re-run. And item 7.2 says the
  throughput comparison must happen **before the campaign is sized**, so Leg-5 training would precede
  a measurement that is meant to be able to change the backbone.

### ⚪ (c) — Report Leg-4 as the paper's model; drop Leg-5

* **Why:** everything needed already exists except the environment. Fastest path to a complete result.
* 🔴 **Cost:** it overturns a leg structure you fixed, on a 1.48 B model with a 4,096 context, and
  `Olmo2ForCausalLM` on vLLM's generic fallback runs the most expensive stage of the project on the
  slow path. The parent document's backbone choice — OLMo 3 over the OLMo 2 checkpoint that first
  looked best — exists **only** because of the native-kernel criterion. This option throws away the
  reason for the choice.

### ⚪ (d) — Skip vLLM: generate with HuggingFace `transformers` plus our own `LogitsProcessor`

* **Why:** no vLLM install; the hand-written oracle already exists.
* 🔴 **Cost:** `RL12` puts a naive processor at **50–200 %** latency overhead against XGrammar's ~8 %,
  on a campaign of 10⁵–10⁶ diaries. And `G7.10` **cannot exist** under this option: it is defined as
  agreement *between* the oracle and XGrammar, so removing one side removes the gate that catches a
  grammar bug. The parent document keeps the hand-written processor "as a unit-test oracle only", in
  those words.

## 4. What each ruling costs to apply

| ruling | first `sbatch` | before the paper's number exists |
|---|---|---|
| **(a)** | env build, then `G7.10`, then a small Leg-4 batch | env + Leg-4 rehearsal + Leg-5 training + Leg-5 campaign |
| **(b)** | env build, then Leg-5 training | env + Leg-5 training + Leg-5 campaign |
| **(c)** | env build, then the Leg-4 campaign | env + Leg-4 campaign |
| **(d)** | Leg-5 training (no env build) | Leg-5 training + a much slower campaign, and `G7.10` is dropped |

⚪ In every case `prereg.md` is untouched, and nothing already closed is reopened. **The three Step 6
nulls stand whatever is ruled** — they are weightings over real diaries and never read a model.

---

## Answer box

> **`D-S7-3`:**  (a) rehearse on Leg-4 then Leg-5 / (b) Leg-5 only / (c) Leg-4 is the paper /
> (d) no vLLM  → **(a) Rehearse on Leg-4 pilot then run Leg-5 for the paper — front-load all gate & pipeline verification at 1.48 B before the 7 B campaign.**

> **Sub-question, only if (a) or (b):** may I install `vllm`, `xgrammar` and `bitsandbytes` into a new
> `/speed-scratch/o_iseri/envs/step7`, leaving `envs/step4` untouched?  → **YES — create `/speed-scratch/o_iseri/envs/step7` in isolation, keeping `envs/step4` frozen.**

---

## Author's Ruling & Directives (2026-08-22)

| Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|
| **`D-S7-3`** | 🟢 **Option (a)** | **Execute complete downstream chain on Leg-4 pilot as a rehearsal pass, followed by Leg-5 training and final campaign for the paper.** | 1. Create `/speed-scratch/o_iseri/envs/step7` (`vllm`, `xgrammar`, `bitsandbytes`).<br>2. Run `G7.10` (oracle vs XGrammar on 10k strings).<br>3. Generate small Leg-4 batch per fold to rehearse Step 7 gates & Step 6 items 6.3–6.5 end-to-end.<br>4. Train Leg-5 (OLMo-3-1025-7B) on 80GB MIG slice and execute paper campaign. |
| **Sub-question (Env)** | 🟢 **Approved (YES)** | Create isolated virtual environment for Step 7 without disturbing Step 4. | Install required packages into `/speed-scratch/o_iseri/envs/step7`. |

---

### Detailed Rulings and Directives

#### 1. Choice: Option (a) — Rehearsal on Leg-4 Pilot, Report on Leg-5
* **Scientific Rationale**:
  1. **Risk mitigation before heavy compute**: Step 6 items 6.3–6.5 (privacy audits, joint-structure metrics, controls) and Step 7 gates (`G7.5`–`G7.13`) have never been executed on model-generated outputs. Testing them at 1.48 B catches integration defects, schema mismatches, and corner-case crashes before launching 7 B training.
  2. **Preservation of primary design**: Leg-5 (`allenai/Olmo-3-1025-7B`) remains the official, reported model of record for the paper, preserving the native-kernel vLLM performance and architectural commitments.
  3. **Strict provenance tagging**: All rehearsal outputs and gate evaluations from the Leg-4 pass must explicitly bear the metadata tag:
     ```json
     "provenance": "LEG-4 PILOT — NOT REPORTABLE"
     ```
     ensuring that pilot calibration figures are never conflated with final paper results.

#### 2. Sequence of Execution
1. **Environment Setup**:
   Submit sbatch to create `/speed-scratch/o_iseri/envs/step7` with:
   - `vllm`
   - `xgrammar`
   - `bitsandbytes`
   Leaving `/speed-scratch/o_iseri/envs/step4` pristine.
2. **Immediate Gate Verification**:
   Execute `G7.10` (oracle agreement on 10,000 strings against XGrammar) to validate grammar compilation in vLLM.
3. **Pilot Rehearsal Campaign**:
   Generate a pilot batch per fold (e.g. $N=600$ or $1{,}000$ diaries) using existing Leg-4 adapters, and pipe through Step 7 verification and Step 6.3–6.5 evaluation scripts.
4. **Leg-5 Execution**:
   Train Leg-5 on the requestable 80 GB MIG slice (`gpu:nvidia_a100_7g.80gb:1`), verify Step 4 gates, and execute the full generation campaign.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is unchanged. Nothing is running on Speed.
