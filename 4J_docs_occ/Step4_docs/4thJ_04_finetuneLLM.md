# Step 4 — Model: the fine-tuned open-weight LLM

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 4. Validation: `4thJ_04_finetuneLLM_val.md`

---

## STATUS

**✅ FAMILY DECIDED 2026-08-14 by our own measurement. ✅ RECIPE DECIDED by `RL05`. ✅ LEGS FIXED by
the author. ✅ FOLD SCOPE DECIDED 2026-08-14 by the author. Implementation OPEN, nothing trained.**

---

## AIM

One open-weight base model and one recipe, applied once per held-out country, each fold emitting a
serialised diary conditioned on a person.

🔴 **Reworded 2026-08-19. It read "One model, fine-tuned once".** With the decision-11 rotation there
is one base model and one recipe but **one adapter per fold** — "fine-tuned once" describes a single
joint fine-tune, which would put the held-out country into the training set and make Step 6
unscoreable. The same wording had to be corrected in both submission figures on the same day.

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

## 🔴 THIS STEP IS THREE TRAINING RUNS, NOT ONE. DECIDED 2026-08-14, COUNT CORRECTED 2026-08-19

*(The heading read FOUR until author decision 16 excluded France on 2026-08-15. The argument below is
unchanged and is the part that matters; only the count moved.)*

Decision 11 holds every country out in turn, and **a fold is a separate model.** A single adapter
trained on all three countries has seen every country's diaries and can be scored on none of them. So
the unit of work in this step is the **fold**, not the run, and the document said "one Leg-5 run"
until this section was written.

| Run | Legs | Count | Why |
|---|---|---|---|
| **Primary** — rsLoRA r=32, all linear | Leg-4 **and** Leg-5 | 🔴 **3 each**, one per held-out country — **was 4 until author decision 16 excluded France, 2026-08-15** | The reported models. Step 6 scores **three** folds and Step 7 generates per fold |
| **Ceiling** — full fine-tune, 8-bit AdamW | Leg-5 | **1**, on a pre-named fold | Answers "does LoRA underfit a far-from-pretraining target". One measurement settles that; four would settle it four times |
| **Comparison arm** — `Qwen/Qwen2.5-7B`, same recipe | Leg-5 | **1**, the **same** pre-named fold | States what the alternative backbone cost. The training-side backbone argument is already closed by measurement |

🔴 **FIVE Leg-5 jobs and THREE Leg-4 jobs** — three primary folds per leg, one ceiling, one Qwen
comparison arm. *(Was six and four; author decision 16, 2026-08-15, excluded France, so the rotation
is three-fold. The ceiling and Qwen arms are still single-fold and still on the pre-named fold, which
is still held-out **Spain** — the alphabetical-ISO rule that chose it returns the same answer with
France removed, so nothing about the pre-registration moved.)* Leg-4 rotation is nearly free at 1.48 B
and is run in full
because the detectors in 4.4 are what the pilot exists to exercise, per fold.

### 🔴 The pre-named fold is named before the first fold trains, never after

The ceiling and comparison runs sit on **one** fold, so which fold that is becomes a choice — and a
choice made after any result is visible is the same defect decision 11 was adopted to remove, arriving
by a different door. Naming it late would let the full fine-tune be pointed at whichever fold the
primary run did worst on, which is selecting on the outcome.

* **The fold is written into `../Step6_docs/outputs_step6/prereg.md` and frozen with it, before the
  first training job is submitted.**
* ✅ **The fold is held-out SPAIN. Confirmed by the author 2026-08-14, before any fold was trained.**
  The rule that produced it was alphabetical by ISO country code — `ES` sorts first — and the rule
  matters more than the country: 🔴 **a rule fixed in advance is what makes this a pre-registration
  rather than a preference.** The confirmation is dated here because *when* it was taken is the thing
  a reviewer would check, and it was taken while no result existed to be influenced by.
* **After the freeze it cannot move.** If the fold has to change, every fold is re-run from the new
  design and the old results are discarded, not mixed — the same clause as Step 6's freeze.

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
* **`HF_HOME` and `TORCH_HOME` on `/speed-scratch`, weights pre-staged**, and training runs with
  `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` so a run cannot silently re-resolve a repo mid-job
  and train on a revision the manifest does not name.
* 🔴 **Correction, measured 2026-08-14: compute nodes on `ps` DO have outbound network.** This document
  said they did not, and `RL11` implied it. The tokenizer jobs (1234176, 1234177, 1234192, 1234199)
  ran `pip install` and pulled tokenizer files from Hugging Face **from inside `sbatch`**, and job
  1245620 stages the weights the same way. **Offline is a discipline we impose on training runs, not a
  property of the node**, and the distinction matters because it is the difference between "the
  download must happen on the login node" — which the top rule forbids — and "the download is an
  ordinary batch job".
* **`--signal=B:SIGUSR1@600`** with a checkpoint-and-exit handler, plus periodic stateful checkpoints
  including optimizer, scheduler, RNG **and sampler position**.
* `/speed-scratch` purges after 90 days.

---

## WORK ITEMS

### 4.1 — Pre-stage weights — ✅ **DONE 2026-08-14, Speed job 1245620, 3 of 3**

| Repo | Role | Revision | Size | Shards |
|---|---|---|---|---|
| `allenai/Olmo-3-1025-7B` | Leg-5 primary | `a81bae42db3975be1671e27b9c9a56da1a9f980f` | 13.603 GiB | 3 |
| `allenai/OLMo-2-0425-1B` | Leg-4 pilot | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | 5.541 GiB | 2 |
| `Qwen/Qwen2.5-7B` | comparison arm | `d149729398750b98c0af14eb82c78cfe92750796` | 14.196 GiB | 4 |

Under `/nfs/speed-scratch/o_iseri/hf_cache/hub/`, 33.34 GiB, 8 minutes. Copied into
`outputs_step4/staged_weights.json`. 🔴 **These three hashes are what a run manifest cites, and G4.11
fails a run that names a checkpoint without one.**

🔴 **`/speed-scratch` purges after 90 days and training is weeks away**, behind the UK and France
acquisitions. **Re-run the job before the first training submission and compare the hashes.** If a
repo moved in the interval, the hash changes — which is the entire reason the file records hashes
rather than paths.

**Three** checkpoints, not two: Leg-5, Leg-4 and the comparison arm.

🔴 **Staged by `sbatch`, never on the login node.** `../tools/4thJ_stage_weights.sh` on partition `ps`,
16 GB, `-t 7-00:00:00`. The earlier text said "downloaded on the login node", which the project's top
rule forbids outright — a 15 GB `huggingface_hub` download is bare python on `speed-submit2`.

**The deliverable is `staged_weights.json`, not the files.** It records the resolved commit hash, the
local path, the byte size and the shard count of each repo, and the hash is read from the snapshot
directory name rather than from a second API call that could resolve a different revision. 🔴 **A model
repo can be updated in place; a checkpoint named without a revision is not a reproducible
checkpoint**, and G4.11 fails a run whose manifest omits it.

**This item can run before anything else in the project is finished** — it depends on no corpus, no
decision and no acquisition, which is why it went first.

### 4.2 — Leg-4 pilot runs, one per fold

Full pipeline, small model, short schedule, 🔴 **three folds** *(was four; decision 16)*. **The success
criterion is not a metric — it is that every detector in 4.4 fires when it should and stays silent
when it should not.**

🔴 **Run fold 1 of Leg-4 to completion and read it before submitting the other two.** The pilot
exists to find wiring defects, and finding one after three jobs have run costs three jobs.

### 4.2-bis — 🔴 The pre-registration is frozen before the first Leg-5 job, not before Step 6

`../Step6_docs/outputs_step6/prereg.md` names the rotation, the nulls, every threshold, the FAIL
criteria, the second hold-out **and the pre-named fold of the section above**. Step 6 owns the file;
**this step owns the deadline.** It is frozen with a recorded md5 **before the first Leg-5 training
job is submitted**, because after that point a training run exists whose result could inform it.

A pre-registration written after the first model has been trained is a description, and the difference
does not show up anywhere in the output.

### 4.3 — Leg-5 runs

* **Primary, three runs**: rsLoRA r=32, all linear, 3 epochs, packed, bf16. One per held-out country.
  Each trains on the **other two** countries only, asserted per run, not assumed from a filename.
  🔴 **CORRECTED 2026-08-19. This read "four runs … the other three countries", which was true before
  author decision 16 EXCLUDED FRANCE on 2026-08-15.** The corpus is Italy, Spain and the UK. **The
  "asserted per run, not assumed from a filename" clause is the part that matters and it is unchanged
  — `G4.13` checks it, and on the `uk` fold it reported `heldout-country records in train = 0` with
  `by_country={'es': 17332, 'it': 34366}`, which is the assertion doing its job.**
* **Ceiling, one run**: full fine-tune, 8-bit AdamW, same data, same schedule, **on the pre-named
  fold**.
* **Comparison arm, one run**: `Qwen/Qwen2.5-7B`, same recipe, **same pre-named fold**, so the paper
  can state what the alternative cost.

🔴 **The ceiling and the comparison arm are single-fold measurements and must be reported as such.**
Quoting either as a general result across the corpus would be quoting one fold as three (corrected from "as four", 2026-08-19, decision 16).

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
| `outputs_step4/leg5_adapter_fold_<country>/` — **four** | Step 7, one per fold. 🔴 **Never released** — `RL10` |
| `outputs_step4/leg5_ceiling_fold_<country>/` — **one** | Step 4 validation, the recipe comparison in the methods |
| `outputs_step4/leg5_qwen_fold_<country>/` — **one** | The comparison arm reported in the methods |
| `outputs_step4/training_metrics.csv` | Step 4 validation. Carries a `fold` and a `run_type` column; **one row set per run, never merged across folds** |
| `outputs_step4/conditioning_diagnostics.md` | Step 5, Step 6. Reported per fold |
| `outputs_step4/run_manifest_<run>.json` | G4.11 and G4.13 — base revision hash, corpus md5, config, seed, held-out country, and the frozen `prereg.md` md5 |

🔴 **There is no throughput artefact in this step.** The vLLM comparison lives once, in
`../Step7_docs/outputs_step7/throughput_comparison.md`, item 7.2. A second copy of a measurement
drifts from the first, and the copy that drifts is the one being quoted.

---

## WHAT BLOCKS THIS STEP

Step 3's corpus, and 🔴 **the frozen `prereg.md`** — see 4.2-bis. The corpus blocks the work; the
pre-registration blocks the *first submission*, which is a different deadline and is the one that is
easy to miss.

**What this step blocks:** Steps 6 and 7 entirely.

---

## DEFINITION OF DONE

1. `prereg.md` frozen and its md5 recorded **before the first Leg-5 job is submitted**, naming the
   pre-named fold.
2. All **three** Leg-4 folds complete and every detector in 4.4 has been **seen firing** on a
   deliberately broken input.
3. **Three** Leg-5 primary folds complete inside the seven-day walltime, each asserted to have trained
   on **two** countries and not three. 🔴 *(Was four folds trained on three countries; author decision
   16, 2026-08-15, excluded France. `G4.13` counts this from the shard the trainer actually loaded, and
   its threshold — exactly 0 records of the held-out country — does not move.)*
4. Ceiling and comparison-arm runs complete on the pre-named fold, and are reported as single-fold.
5. Conditioning diagnostics run and reported, **per fold**, including the evening-slot check.
6. All Step 4 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* Backbone, legs and recipe all fixed. Nothing trained.
* 🔴 The KV-cache arithmetic above is **derived from measured config values, not benchmarked.** It is
  written here rather than in a footnote because it is the one number that could reverse the backbone
  choice, and it is the one number we have not run.

### 2026-08-14 (second entry) — the step is rewritten for four folds; the ceiling run is scoped

* 🔴 **This document was written for one Leg-5 run while decision 11 had already made it four**, and
  Step 6 stated that "Step 4's output contract already said one adapter per leave-one-out fold" when
  the contract said `outputs_step4/leg5_adapter/`, singular. **Caught by cross-reading the two
  documents against each other, not by either one on its own** — which is the argument for reading a
  step's neighbours before trusting its interfaces.
* ✅ **Author decision 2026-08-14: the ceiling run and the Qwen comparison arm run on ONE pre-named
  fold**, not four. Four primary folds at each leg, one ceiling, one comparison arm. **Six Leg-5 jobs
  and four Leg-4 jobs.**
* 🔴 **Naming that fold became a new way to choose late**, so it is frozen into `prereg.md` before the
  first training job, with a rule — alphabetical ISO code, so **Spain** — that has nothing to do with
  any result. The author may name another country before the freeze and none after it.
* **A deadline was missing and is now written down**: `prereg.md` is frozen before the *first Leg-5
  submission*, not merely before Step 6 scores anything. Once a model exists, a pre-registration
  written afterwards is a description of it.
* **The throughput artefact was duplicated across Steps 4 and 7 and is now single**, owned by item
  7.2. The duplicate output row is removed rather than kept in sync.

### 2026-08-14 (third entry) — item 4.1 executed. Speed job 1245620, the project's first training-side job

* ✅ **Three checkpoints staged, 33.34 GiB, eight minutes**, and the three commit hashes are in
  `outputs_step4/staged_weights.json`. **The hashes are the deliverable; the files are a side effect**
  and `/speed-scratch` will purge them long before training starts.
* ✅ **The pre-named fold is confirmed: held-out SPAIN**, author, 2026-08-14, taken while nothing was
  trained.
* 🔴 **Writing the job corrected this document.** It said the checkpoints were "downloaded on the login
  node", which the project's top rule forbids outright — a 15 GB `huggingface_hub` pull is bare python
  on `speed-submit2`. It also said compute nodes have no outbound network, and they do: the tokenizer
  jobs pip-installed and pulled from Hugging Face inside `sbatch`, and so did this one. **The error had
  been sitting in both this document and plan section 4F since they were written**, and it was only
  found by trying to do the thing they described.
* **It went first because it depends on nothing** — no corpus, no acquisition, no decision. Everything
  else in this step waits on Step 3.

---

### `D-S6-14` — Step 4 now also builds a POISONED control shard set (2026-08-22)

`4thJ_step4_shards.py --permute-labels` writes a second, isolated shard set whose prefix-to-body
pairing has been deranged inside each `(country, split)` group with seed **614614**, to
`shards_permuted_control/` and `shard_manifest_permuted_control.json`. Every record carries
`POISONED_CONTROL: true`. Nothing in the default path changed.

`4thJ_step4_train.py` gains `--run-type permuted` and `--shard-manifest`, with an interlock that
refuses a production run-type against a poisoned manifest **and** `permuted` against a clean one —
both seen failing, job 1286303. `4thJ_step4_leg4_fold.sh` and `4thJ_step4_leg5_fold.sh` take an
optional second argument, `primary` (default, unchanged) or `permuted`.

🔴 **Nothing trained on these shards is a Step 4 result.** The adapters exist only to put a top on
the AUC scale `G6.10` and `G6.11` are read against; the Step 4 fidelity gates are expected to fail on
them and that failure means nothing. The construction, its five measured invariants and the ruling
are recorded in `Step6_docs/4thJ_06_transfer.md`.

⚪ **Noticed while checking the control manifest, and it is PRE-EXISTING in production, not
introduced by it.** `G4.9`'s probe sets are drawn per fold with a fixed seed, but the RNG advances
through `train_countries` in order, so a country's probe set is identical across folds only when the
country occupies the same position in both. Measured on `shards/`:

| probe | md5 |
|---|---|
| `probe_it_es.jsonl` | `9d7b9f3892c88a20ee8a096b3d2f90fd` |
| `probe_uk_es.jsonl` | `9d7b9f3892c88a20ee8a096b3d2f90fd` — **byte-identical** |
| `probe_es_it.jsonl` | `6a86475c4638585870b110437f3e41c2` |
| `probe_uk_it.jsonl` | `590a5c46e0a8e4a415e175c38736d845` — **different** |

`es` is first in both of its donor lists, so its 200 diaries are one fixed set; `it` and `uk` are
first in one fold and second in the other, so each has **two different** probe sets.

🔴 This is harmless for `G4.9`, which compares a probe series across checkpoints **within** one run,
and that is all the gate claims. It is NOT harmless for any table that compares probe losses for the
same country **across folds**: such a comparison is like-for-like on `es` and is not on `it` or `uk`.
Recorded rather than repaired — re-seeding per country would change every production probe file, and
that is a basis change, not a fix.
