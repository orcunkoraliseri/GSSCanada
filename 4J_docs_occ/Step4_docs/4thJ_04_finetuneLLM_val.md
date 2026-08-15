# Step 4 — Fine-tuned LLM. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_04_finetuneLLM.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing trained.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

Three things, in order of how badly they would hurt:

1. **The model did not collapse.** Everyone in a stratum getting the modal day matches aggregate
   marginals while being useless for building energy, because the entire value of occupant modelling
   is diversity. Paper 1 documents argmax producing "overly uniform occupant characteristics" at
   neighbourhood scale; `RL03` independently reports severe within-group variance collapse in the
   silicon-sampling literature. **Two independent literatures naming the same failure is why this is
   instrumented from the first training run rather than at evaluation.**
2. **The model is listening to the conditioning.** If it is not, every downstream claim is void.
3. **The training loop did what we think it did.** Padding, masking, merging, termination.

---

## GATES

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G4.1** Within-stratum variance ratio | 🔴 **Distribution collapse** | `0.80 ≤ VR ≤ 1.25` for **every** stratum with N ≥ 100, logged every validation epoch. 🔴 Report which **end** any failure sits at | **project-chosen**, pre-specified ±20 % band |
| **G4.2** Delimiter-vs-content perplexity split | Loss falling while content degenerates | Automatic halt if delimiter loss < 0.05 **and** activity entropy < 1.5 nats. Reported every epoch regardless | `RL05` |
| **G4.3** Shuffled-prefix cross-entropy | The model ignoring its conditioning | Cross-entropy under permuted prefixes must exceed the true-prefix value by **≥ 0.15 nats/token**. Below that, conditioning is not driving generation | **project-chosen** |
| **G4.4** Slot-wise mutual information | Demographically appropriate mornings, generic evenings | MI(attributes ; activity) computed per slot against the empirical curve. 🔴 **The 18:00-23:00 window is scored separately and reported separately** | **project-chosen** |
| **G4.5** Padding labels | Training on padding | 100 % of pad and prompt positions carry label `-100` | `RL05` failure mode 5 |
| **G4.6** Adapter merge drift | Merged and unmerged models diverging | Max logit difference on a fixed sample **< 1e-4** | `RL05` failure mode 6 |
| **G4.7** Termination | Generation that never stops | 100 % of training completions terminate with `<eor>` | `RL05` failure mode 7 |
| **G4.8** Tokenizer round-trip | Vocabulary mismatch | `tokenize(detokenize(ids)) == ids` on 1,000 cases before any large generation run | `RL05` failure mode 4 |
| **G4.9** Per-country probe stability | Catastrophic forgetting | Per-country held-in probe loss at final checkpoint within **+5 %** of its own best value during training | **project-chosen** |
| **G4.10** Memory and walltime | A run that cannot be repeated | Peak VRAM recorded; run completes inside 7 days. **Reported, not thresholded** | operational |
| **G4.11** Checkpoint provenance | An unreproducible model | Base repo **revision hash**, corpus md5, config and seed recorded per run. 🔴 A checkpoint named without a revision is not a reproducible checkpoint | **project-chosen** |
| **G4.13** 🔴 **Fold isolation** | The held-out country reaching its own fold's training data | Per fold, the count of training records whose `country` equals the held-out country is **exactly 0**, counted **from the shard the trainer actually loaded**, never from the config or the filename. Run at training start, not at scoring time | **derived from decision 11** |
| **G4.14** 🔴 **Pre-registration precedence** | A pre-registration written after a model exists | Every run manifest carries the `prereg.md` md5, all manifests carry the **same** value, and that value equals the md5 recorded **before the first Leg-5 submission**. Missing field, mismatched field, or a changed file: **FAIL** | **derived from decision 11's freeze clause** |

---

## 🔴 THE GATE THAT MEASURES SKILL RATHER THAN MARGINALS

G4.1 to G4.4 are all computed over generated output. A battery of that shape can measure the
**aggregate** and be entirely blind to whether the model links a person to *their own* behaviour.

**G4.12 — the within-stratum shuffle test.** Permute generated diaries **within
(country × age band × sex × household type × day type)** cells. Every conditional marginal is
preserved exactly; the association between a person and their day is destroyed.

* **Requirement: G4.3 and G4.4 must both degrade materially under the shuffle.**
* 🔴 **If every gate returns the identical status under the shuffle, the battery measures marginals,
  not skill**, and the conditioning claim is unsupported regardless of what the other numbers say.
* Cheap to run, needs no retraining, and it is the single most informative check in this step.

---

## EVERY GATE MUST BE SEEN FAILING

Each perturbation must break **exactly one** gate. Run them on Leg-4, where a training run is cheap —
**that is what the pilot leg is for.**

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Replace every generated diary in a stratum with that stratum's modal day | **G4.1** at the **lower** end | G4.7 |
| Duplicate one diary 500× inside a stratum | G4.1 lower | G4.3 |
| Freeze the adapter (train zero steps) | G4.3 | G4.5 |
| Train with the prefix removed entirely | G4.3, G4.4 — **coverage** case | — |
| Blank the evening slots' conditioning only | **G4.4** on the 18:00-23:00 window, and G4.4 must stay clean on the morning window | G4.3 (marginally — record it) |
| Set 1 % of pad labels to a real token id | G4.5 | G4.6 |
| Perturb one merged weight by 1e-3 | G4.6 | G4.5 |
| Strip `<eor>` from 1 % of completions | G4.7 | G4.1 |
| Swap the tokenizer | G4.8 | — |
| Train country-by-country sequentially | G4.9 | G4.1 |
| Delete the revision hash from the run manifest | G4.11 | all others |
| 🔴 **Put 1 % of the held-out country's records into that fold's training shard** | **G4.13** | G4.1, G4.3 — *and the fold's downstream score will IMPROVE. Every gate that could see this one is a provenance gate, which is the same shape as Step 6's contamination perturbation* |
| Edit `prereg.md` after fold 1 has been evaluated | **G4.14** | all others — *nothing in the model changes, which is exactly why no other gate can see it* |
| 🔴 **Within-stratum shuffle** | **G4.3 and G4.4 must degrade** | G4.1 **must stay clean** — the shuffle preserves within-stratum variance, and that is exactly why G4.1 cannot substitute for G4.12 |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any gate that passes on the real
model was never made to fall.** Two rows above are deliberately multi-gate and are scored for
coverage only — a perturbation that moves three gates cannot attribute what it broke.

---

## VACUITY GUARDS

* **V4.a** — G4.1 FAILs, rather than skipping, if **fewer than 5 strata** have N ≥ 100. A variance
  gate evaluated on an empty or near-empty set of strata is satisfied by nothing.
* **V4.b** — every gate's severity is **hard**. 🔴 **Grep the validator for `hard=False` or any
  soft-severity flag before trusting a PASS count.** A gate that computes the right answer and then
  declines to call it a failure is a gate that runs and lies.
* **V4.c** — the runner prints strata count, records scored, epochs read and the checkpoint path
  **before** any verdict, and no summary line may print a conclusion it did not compute.
* **V4.d** — G4.2's halt condition uses `<` on both arms, never `<=`. A prediction of movement must
  not be satisfiable by nothing moving.
* **V4.e** — the validator **imports** its thresholds from a single module. A second copy of a band
  drifts invisibly from the first.
* **V4.f** — G4.13 FAILs, rather than passing, if it could not open the training shard or found **zero
  records of any country** in it. 🔴 An isolation check over an empty shard finds zero held-out records
  for the wrong reason, and reports the same number as a clean fold.
* **V4.g** — G4.14 recomputes `prereg.md`'s md5 **from the file on disk** at every run. Reading the
  value the manifest already claims and comparing it to itself is the circularity that retired G1.7b.
* **V4.h** — the runner prints **which fold it is scoring** and which country that fold holds out,
  before any verdict. 🔴 Four folds' metrics in one directory is how a fold's numbers get read under
  another fold's name, and nothing in the numbers themselves would say so.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** test transfer. Every gate here is scored on **held-in** countries. Step 6 is the
  only place the paper's claim is tested, and a model that passes all of Step 4 can still fail Step 6
  completely — that is the design, not a defect.
* It does **not** test structural validity of generated text. That is Step 7, and the distinction
  matters: 100 % validity after masking is a property of the **decoder**, not of the model.
* It does **not** test privacy. The four-attack audit from `RL10` runs in Step 6.
* 🔴 It does **not** transfer to Leg-5 from Leg-4. Leg-4's 4,096 context and generic vLLM fallback
  mean **no throughput, latency or packing number extrapolates.** Correctness gates carry across;
  performance numbers do not, and quoting a Leg-4 throughput as a Leg-5 expectation would be reading
  a different machine.
* 🔴 It does **not** validate the KV-cache arithmetic in the implementation document. That figure is
  derived from config values and has not been benchmarked. Until the throughput comparison is run,
  Step 7's campaign sizing rests on an unmeasured quantity.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Twelve gates, thirteen perturbations, none run.

* 🔴 G4.12, the within-stratum shuffle, is here because of a 3J finding worth restating: **for any
  gate over per-entity data, ask what a within-stratum shuffle of the thing you claim to validate
  would do to the number. If the answer is nothing, the gate validates the aggregate, not the
  model.** In 3J that question turned ten green retail gates into ten gates that had never measured
  skill.

### 2026-08-14 (second entry) — two gates added at the fold boundary

* **Fourteen gates, fifteen perturbations, none run.** `G4.13` fold isolation and `G4.14`
  pre-registration precedence, with `V4.f` to `V4.h`.
* 🔴 **Both new gates guard things that leave no trace in the model.** A fold trained on 1 % of its own
  held-out country produces a *better* score and a normal-looking loss curve; a `prereg.md` edited
  after fold 1 changes no weight at all. **Every check that could catch either is a provenance check**,
  which is the same shape as Step 6's "train including the held-out country" perturbation and the
  reason that one is singled out there.
* **G4.13 counts from the shard the trainer loaded**, not from the config that says which shard it
  should have loaded. A fold whose file list was built wrong is exactly the defect a config-side check
  cannot see, and it is cheap to get right at training start and expensive to discover at Step 6.
* **V4.h exists because four folds now share one output directory.** Nothing in a metrics row says
  which country it held out, so the runner has to say it before it says anything else.
