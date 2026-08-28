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
| **Comparison arm** — `Qwen/Qwen2.5-7B`, same recipe | Leg-5 | **1**, the **same** pre-named fold | States what the alternative backbone cost. The training-side backbone argument is already closed by measurement. 🟢 **DONE 2026-08-27, job `1287613` `COMPLETED 0:0`, 13:33:05 — the backbone does NOT fix `G4.1` (FAIL 3/3 epochs, band difference `0.029` against the `es` noise floor `0.529`); it costs stability (`G4.9` FAIL, epoch-1 runaway), +24 % wall and +16 % VRAM. Truncation measured: train 0.0247 % / val 0.0543 %, both far under `D-S4-17`'s 1.0 %. See the 2026-08-27 entry.** Submitted 2026-08-26 (night, last) — `tools/4thJ_step4_qwen_fold.sh`, outputs redirected to `runs_leg5_qwen` / `diagnostics_leg5_qwen` |

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

🟢 **`D-S4-17` RULED 2026-08-26 — OPTION (A), AND IT WAS RULED WHILE THE JOB WAS STILL `PD`.** `--max-len 1280` **stays fixed on every arm**; the Qwen arm is reported with its **exact measured truncation rate printed beside its losses**, under a pre-declared **≤ 1.0 %** contamination threshold — above it the arm is flagged CONTAMINATED and escalates before any claim is made. 🔴 **The number had not been seen by anyone when the decision was taken**, which is the point of the document.

🔴 **Why the question existed: `--max-len` is NOT backbone-neutral.** The table above measures the same diary at **200 OLMo tokens against 303 Qwen tokens**, and `311` at **1 token against 3** — so a fixed token budget is a **tighter** budget for Qwen. Holding the number constant does not hold the constraint constant. `DiaryDataset` sliced `(prefix + body)[:max_len]` **silently**; it now **counts** truncated records and prints a `TRUNCATION` line for **every** run, OLMo arms included, so this arm has a baseline. ⚪ It is a **counter, not a gate** — no `G4.x` id, no band, no verdict — and it was seen both silent and firing before the arm was submitted.

🔴 **Three directives that reach the manuscript.** (1) Report the Qwen comparison **strictly on fold `es`**, as `prereg.md:90` pre-registers. (2) State that `G4.2`'s delimiter parsing is evaluated on **Qwen's native vocabulary** — the verdict is comparable across arms, the numbers are not. (3) `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` stays frozen; **no re-runs and no threshold alterations permitted.**

🔴 **What may never be done, whatever the count:** raise `--max-len` on the Qwen arm alone and still call the two arms *"the same recipe"*. Record: `../Step10_docs/docs/2026-08-26_D-S4-17_the-qwen-arm-truncation-decision.md`.

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

---

### 2026-08-26 — PERTURBATION-BATTERY COVERAGE IS CLOSED AS A DECLARED LIMITATION

Record: `Step4_docs/impl/2026-08-26_perturbation-coverage-closed-as-limitation.md`.

The item was carried as IN PROGRESS on the assumption that four perturbations were "still owed".
They are not owed; they are **undemonstrated by ruling**. Re-derived from the artefacts rather
than quoted: across all four `genperturb` outputs — `genperturb_{es,it,uk}.json` and
`genperturb_f29/genperturb_es.json` — there are **20 recorded `G4.1` verdicts and all 20 have
`n_scorable_strata = 0`**. `D-S4-11` (i) re-labelled them `NOT COMPUTED`, and the one change that
would make them non-vacuous — re-pointing the perturbation side at `real_ref` — was refused in the
author's own words because it "would change the basis of a scored gate after all three folds were
scored". 🔴 **Re-running the battery is the one action guaranteed not to change this item**, which
is why it is closed rather than left open.

🔴 **Correction to the checklist note.** It said the coverage clause "also FAILs on `es` and `uk`".
Measured: `coverage_clause: FAIL` on **all three** folds, and `G4.7` PASSes under every one of the
five levers in every fold. The note understated it.

🔴 **No lever was added to fell `G4.7`, deliberately.** Writing one now, after all folds are
scored, is the same act refused for `G4.1`; doing it for one gate and not the other would be
inconsistent in the direction that flatters the result. `G4.7` is recorded as **passing at
baseline and never demonstrated falling**, the same class of declared limitation as the four
`G4.1` levers.

⚪ Step 4 stays closed with four failing gates — `G4.1`, `G4.3`, `G4.6`, `G4.12`. Never written up
as clean. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` unchanged.

### 2026-08-26 (evening) — 🟢 THE CEILING RUN IS DONE. `1287378`, `COMPLETED 0:0`. THE ANSWER TO ITS QUESTION IS **NO**.

This document declared the ceiling's purpose on 2026-08-14, before any fold trained:
*"Answers 'does LoRA underfit a far-from-pretraining target'. One measurement settles that."*
It has been measured, on the pre-named fold **`es`**, and it settles it.

🔴 **LoRA does not underfit.** Full fine-tune of all **7,377,965,056** parameters against the
adapter's **79,953,920** (**92×**), everything else identical — same corpus md5, same shard md5,
same seed 42, same lr/batch/accum/epochs/`max_len`, same base revision:

| epoch | primary `train_loss` | ceiling `train_loss` |
|---|---|---|
| 0 | 0.559465 | **0.566805** |
| 1 | 0.525521 | **0.532635** |
| 2 | 0.508305 | **0.513494** |

The ceiling ends **higher** at every epoch; `content_loss` ties at epoch 2 (0.8636 vs 0.8653). ⚪ The
arms also differ in optimiser (`AdamW8bit` vs 32-bit `AdamW`), so the gap's *magnitude* is not
attributable to capacity — but the direction that mattered is settled: full fine-tuning recovers no
loss that the adapter left on the table.

🔴 **`G4.1` is NOT improved by the ceiling and must never be reported as improved.** Both arms FAIL
all three epochs. The band counts differ (`es` ceiling worst `1.508` vs primary `1.568` at epoch 2)
by an order of magnitude **less** than `G4.1`'s own `es` sampling-noise floor of **0.529** measured
under `D-S4-16`. Only the verdict is comparable.

⚪ The `bitsandbytes` blocker carried by `Step4_docs/impl/2026-08-18_step4-training.md` is spent:
`0.50.1` runs against `torch 2.5.1+cu121`, `AdamW8bit` exercised on a card, peak VRAM **46.14 GiB**
in 8:45:36 on the `nvidia_a100_7g.80gb` profile.

⚪ Filed and **not** fixed here: the ceiling's `run_manifest_*.json` still records `lora_r 32` /
`lora_alpha 64` / `use_rslora true` and writes to a directory named `adapter/` for a run that used
no adapter. Owed before the methods section quotes that manifest.

🔴 **This is one fold.** Per this document's own rule, quoting it as a corpus-wide result would be
quoting one fold as three. **The Qwen comparison arm — the other single-fold Leg-5 run — is still
owed.** Full record: `outputs_step4/proglog_step4_gates.md`, entry 2026-08-26 (evening),
`FINDING 155`–`FINDING 157`.

🟢 **`FINDING 157` DISCHARGED 2026-08-26 (night, last), script edit only, no re-run.**
`tools/4thJ_step4_train.py` now emits `"trainable": "full"` for a ceiling run, nulls the
`lora_*` keys with a `lora_note` saying why, splits `adapter_dir` / `weights_dir`, and names the
saved directory `weights/` instead of `adapter/` — only the ceiling branch moves.
🔴 **`G4.11` was TIGHTENED to require `trainable`** (`n_required` 15 → 16) and was seen
refusing the defect on four shapes including **the shipped ceiling manifest, which now FAILS on
`trainable` — intended, and never to be repaired by loosening the gate.**
🔴 **The shipped manifest is NOT edited** — it is the record of what job `1287378` wrote and
must keep agreeing with its own stdout log. The corrected labels live in a sidecar,
`outputs_step4/leg5_ceiling_fold_es/run_manifest_leg5_ceiling_fold_es.CORRECTION.json`, with each
shipped value preserved beside its correction. 🔴 **The methods section quotes the CORRECTION
file, never the shipped manifest's `lora_r` / `lora_alpha` / `use_rslora` / `targets`.**

### 2026-08-27 — 🟢 THE QWEN COMPARISON ARM IS DONE. `1287613`, `COMPLETED 0:0`, 13:33:05. THE BACKBONE IS NOT THE REASON `G4.1` FAILS.

This closes the last of the eight Leg-4/Leg-5 jobs. The arm was pre-registered on 2026-08-14 and
its question was *"what does the alternative backbone cost?"* — asked of the training side, on the
one pre-named fold, `es`.

🟢 **`D-S4-17` HELD: the recipe is identical on every axis but one.** Read from the two shipped
manifests, not asserted: `corpus_md5 ca89d2295603c547f2384a40dd1909ba` and
`train_shard.md5 3b15432e25d1df09a1e65c764a87f562` are **the same file** as the `es` arms;
`seed 42`, `epochs 3`, `lr 1e-4`, `batch_size 2`, `grad_accum 8`, **`max_len 1280`**,
`lora_r 32` / `lora_alpha 64` / `use_rslora true`, the same seven target modules,
`prereg_md5 e4243e07cdd80c9c846b91f40e3e8c45`. `base_repo` is the only field that moves:
`Qwen/Qwen2.5-7B` at revision `d149729398750b98c0af14eb82c78cfe92750796`. `trainable: "lora"`, so
this manifest **passes** the tightened `G4.11` (16/16) that the ceiling manifest fails by design.

🟢 **The truncation rate was measured, and the arm is NOT contaminated.** `D-S4-17` set the bar at
1.0 %: **train 12 of 48,594 (0.0247 %), longest record 1,509 tokens; val 3 of 5,520 (0.0543 %),
longest 1,700 tokens**, tokenizer `Qwen/Qwen2.5-7B` at `max_len 1280`. Both are **~20–40× under the
bar**, so the comparison below is a comparison of backbones and not of truncation.
🔴 **The asymmetry that must travel with it:** the truncation instrumentation post-dates the Llama
arms, so `1286209` (primary `es`) and `1287378` (ceiling `es`) have **no measured rate**. They ran
the same `--max-len 1280` — verified in both stdout logs — but a *different tokenizer*, so their
rate may not be assumed equal to Qwen's. **Never write "both arms truncated equally"; write that
one arm was measured and the other was not.**

**Epoch-2 comparison, fold `es`, LoRA both sides, single-variable:**

| epoch-2 quantity | primary `1286209` (Llama) | Qwen `1287613` |
|---|---|---|
| `delim` | **0.0734** | 0.1090 |
| `content` | **0.8653** | 0.8739 |
| `entropy` | 3.307 | 3.478 |
| `G4.1` | FAIL, worst `0.750 / 1.568` | FAIL, worst `0.892 / 1.539` |
| `G4.3` CE rise (need ≥ 0.15) | FAIL, **0.1062** | FAIL, **0.0387** |
| `G4.7` | FAIL | FAIL (gen-terminated 599/600) |
| `G4.6` | FAIL | FAIL, `max_logit_diff 1.470e-02` |
| `G4.9` | **PASS** | 🔴 **FAIL** |
| peak VRAM / wall | 19.98 GiB / 37,211 s | 23.14 GiB / 45,339 s |

🔴 **`G4.1` IS NOT IMPROVED BY THE BACKBONE AND MUST NEVER BE REPORTED AS IMPROVED.** Both arms
**FAIL all three epochs**. The worst-band figures differ by `1.568 − 1.539 = 0.029`, which is
**18× smaller** than `G4.1`'s own `es` sampling-noise floor of **0.529** measured under `D-S4-16`.
⚪ **Only the verdict is comparable** — the same sentence the ceiling arm earned, now earned twice,
from opposite directions: more capacity does not fix `G4.1` and a different backbone does not fix
`G4.1`.

🔴 **`G4.9` is the one gate where the arms genuinely differ, and the mechanism is visible in the
epoch line.** `G4.9` asks for monotone improvement across checkpoints inside one run. Qwen's
`content` runs **0.5187 → 1.2261 → 0.8739**: epoch 1 is a runaway, not a plateau, and it carries
`G4.1 FAIL [V4.a: only 1 scorable strata]` and `G4.7 FAIL [gen-terminated 558/600]` with it.
The Llama arm is monotone and passes. ⚪ This is a **stability** difference under an identical
recipe, not a capability difference, and it is the honest answer to "what does the alternative
backbone cost": **it costs stability, 24 % more wall-clock and 16 % more VRAM, and it buys nothing
a gate can see.**

🟢 **The generation-side perturbation probe ran and its coverage clause PASSES.** `G4.1`/`G4.4`/
`G4.7` are all **FAIL at the null baseline**, so all three are correctly reported
`NOT ASSESSABLE as STAY CLEAN` / `VOID` rather than credited; **gates credited as seen falling on
this probe: none**; **gates that pass at baseline and were never felled: none**. `prereg.md`
md5 verified live inside the job against `Step6_docs/outputs_step6/prereg.md` — equal.

🔴 **One correction to the 2026-08-26 (evening) ceiling entry above, filed additively and not
repaired in place.** That entry reads *"`content_loss` ties at epoch 2 (0.8636 vs 0.8653)"* in a
paragraph whose table columns are `primary | ceiling`, which reads as primary `0.8636`. The stdout
logs say the opposite: **ceiling `1287378` is 0.8636 and primary `1286209` is 0.8653.** The
conclusion the entry draws — that the two tie — is unaffected, and the `train_loss` table above it
is correct as printed. ⚪ Recorded because the pair is quoted in the methods and the labels must be
the right way round when it is.

🔴 **This is one fold, and it is now the SECOND single-fold Leg-5 result.** Neither the ceiling nor
this arm may be quoted as a corpus-wide result. Both are single-fold measurements on the same
pre-named fold `es`, and the methods must say so in the same sentence that quotes them.
