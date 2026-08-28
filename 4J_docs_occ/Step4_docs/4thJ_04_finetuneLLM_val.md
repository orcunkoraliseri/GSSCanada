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
| **G4.7** Termination | Generation that never stops | 🔴 **D-S4-7 (2026-08-20): 100 % of the GENERATED sample terminates with `<eor>`, scored every validation epoch and at every mid-epoch probe.** Until this ruling the row said *training completions*, which is the corpus and not the model — see `G4.15` | `RL05` failure mode 7 |
| **G4.8** Tokenizer round-trip | Vocabulary mismatch | `tokenize(detokenize(ids)) == ids` on 1,000 cases before any large generation run | `RL05` failure mode 4 |
| **G4.9** Per-country probe stability | Catastrophic forgetting | Per-country held-in probe loss at final checkpoint within **+5 %** of its own best value during training | **project-chosen** |
| **G4.10** Memory and walltime | A run that cannot be repeated | Peak VRAM recorded; run completes inside 7 days. **Reported, not thresholded** | operational |
| **G4.11** Checkpoint provenance | An unreproducible model | Base repo **revision hash**, corpus md5, config and seed recorded per run. 🔴 A checkpoint named without a revision is not a reproducible checkpoint | **project-chosen** |
| **G4.13** 🔴 **Fold isolation** | The held-out country reaching its own fold's training data | Per fold, the count of training records whose `country` equals the held-out country is **exactly 0**, counted **from the shard the trainer actually loaded**, never from the config or the filename. Run at training start, not at scoring time | **derived from decision 11** |
| **G4.14** 🔴 **Pre-registration precedence** | A pre-registration written after a model exists | Every run manifest carries the `prereg.md` md5, all manifests carry the **same** value, and that value equals the md5 recorded **before the first Leg-5 submission**. Missing field, mismatched field, or a changed file: **FAIL** | **derived from decision 11's freeze clause** |
| **G4.15** 🔴 **Corpus termination** | A training shard whose completions do not end | 100 % of the records in the shard **the trainer actually loaded** terminate with `<eor>`, read once before the first optimiser step. This is `G4.7`'s old threshold and old arithmetic under a new id | **`D-S4-7` (2026-08-20), from `FINDING 46`** |
| **G4.16** 🔴 **Diary closure (`G4.7`'s companion)** | A termination reading that cannot tell a broken model from a broken harness | 100 % of the **GENERATED** sample **CONTAINS** `<eor>`, scored on the same texts and at the same checkpoints as `G4.7`. `G4.7` reads *endswith*, `G4.16` reads *contains*; the pair is read together and **neither number may be reported alone**. `n_more_than_one_eor` is recorded beside it, **not thresholded** — it is the direct fingerprint of the `D-S4-8` batch-padding defect | **`D-S4-8` (2026-08-23), from `FINDING 56`** |

🔴 **How to read `G4.16` with `G4.7`.** This is the whole reason the gate exists, so it is written
here rather than left to the reader:

| `G4.16` | `G4.7` | what it means |
|---|---|---|
| **PASS** | **PASS** | clean |
| **PASS** | **FAIL** | **HARNESS.** Every diary closes; generation ran on past the terminator. This is Leg-5 `es` exactly — `107/600` under `G4.7`, `600/600` under `G4.16` |
| **FAIL** | **FAIL** | **MODEL.** Diaries do not close at all |
| **FAIL** | **PASS** | **impossible** — *endswith* implies *contains*. The trainer prints this as an incoherence and the run must not be read |

🔴 **What `G4.16` cost us by not existing.** Leg-4 read `G4.7` `600/600` on all three folds for three
weeks. That was a `generation_config.json` default in the 1B repo covering for a harness that never had
a working multi-sequence stop, and **no gate in the battery could see it** — the one number that would
have (`n_more_than_one_eor`) was never computed. The defect surfaced only when the 7B repo happened not
to ship the same default. `gates must be seen failing` catches a gate that cannot fall; it does not
catch a gate that **passes for the wrong reason**, and a companion reading is the cheapest thing that
does.

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
| Strip `<eor>` from 1 % of **training** completions (`strip_eor_1pct`) | **G4.15** — 🔴 **not `G4.7`, since `D-S4-7`.** This lever edits `train_recs`; it cannot reach the generated sample | G4.1, **G4.7** |
| 🔴 Strip `<eor>` from 1 % of the **generated** texts (`strip_eor_gen`, `4thJ_step4_g47_coverage.py`) | **G4.7** | G4.1 — *and it is deliberately NOT wired into the trainer: felling a generated-side gate from inside a training run costs ~5 h per fold to demonstrate a detector whose rule is `n_terminated == n`, and the standalone script scores a `generated_*.jsonl` that already exists* |
| 🔴 **`D-S4-8`: strip EVERY `<eor>` from 1 % of the generated texts (`strip_all_eor_gen`, same script)** | **G4.16**, and `G4.7` with it | — *nothing is declared clean here on purpose: a diary with no terminator anywhere cannot end with one either, so the two gates fall together and that is correct* |
| 🔴 **`D-S4-8` discrimination arm: `strip_eor_gen` must fell `G4.7` and LEAVE `G4.16` STANDING** | — | **`G4.16`** — *this is the check that the pair is worth having. If the trailing-only lever fells `G4.16` too, the two gates are one gate and the pair should be withdrawn rather than reported* |
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

---

## 🔴 RULINGS ON GATE DESIGN, RECORDED IN THIS DOC (2026-08-19)

D-S4-1 and D-S4-2 (2026-08-18) were applied in code and recorded only in
`outputs_step4/proglog_step4_gates.md`. They are cross-referenced here so that this doc,
which is what a reader checks a verdict against, does not describe a gate that no longer
exists. **D-S4-4 below is a change of MEASUREMENT BASIS and is registered here BEFORE the
run that reports under it, per the discipline set in Step 3 for `G3.9` and `G3.3`.**

| | ruling | effect on this doc |
|---|---|---|
| **D-S4-1** (2026-08-18) | `G4.6` is measured in **float32**. Band UNCHANGED at `1e-4` | none — the arithmetic precision of the comparison moved, not the threshold |
| **D-S4-2** (2026-08-18) | `G4.8` asserts tokenizer **identity against the base checkpoint** and *then* round-trip | the "Swap the tokenizer / must fail `G4.8`" row is now reachable before generation |
| **D-S4-3** (2026-08-19) | `G4.6`'s residual is measured by an **α-sweep** before anything is ruled. **Nothing is decided by this entry** | none. The band stays `1e-4` and `G4.6` stays a standing FAIL until the sweep reports |
| **D-S4-4** (2026-08-19) | 🔴 `G4.2`'s **first arm is re-based onto FORCED delimiters only.** Band UNCHANGED at `0.05` | the paragraph below replaces the tacit definition of "delimiter loss" |

### D-S4-4 — what "delimiter loss" now means, and why it changed

`G4.2`'s first arm is `delimiter loss < 0.05`: *the model has learned the record format
almost perfectly.* It was scored over every token whose decoding is entirely delimiter
characters — **which includes the two-comma token that encodes an absent `ACT2`.** Whether
a respondent recorded a secondary activity is a **content** decision, not a format one, and
scoring it in this arm made the arm a statement about the corpus rather than about the
model.

Measured on the corpus the trainer read (`4J_step3_corpus.jsonl`, md5
`ca89d2295603c547f2384a40dd1909ba`; scripts `tools/4thJ_step4_g42_*`), an oracle that
predicts `P(act2 empty | country, act)` as well as the data allows — fitted on 80 % of the
`uk`+`it` records, scored on the held-out 20 % — still pays **0.0480 nats per delimiter
token, 96 % of the 0.05 band**, before the model predicts a single real delimiter. Richer
conditioning does not rescue it (`(country, act, loc, dur band)` → 0.0477). **The arm was
therefore unsatisfiable by construction, for any model and any training budget** — which is
the true reason behind FINDING 25's extrapolation to 10¹² records.

**The band is NOT moved.** What moves is the token set:

* `delimiter_loss` — scored over delimiters whose presence the record grammar **forces**.
  This is the number the arm reads. Any delimiter token containing `,,` is excluded.
* `delimiter_loss_all_basis` — the pre-ruling number over every delimiter token, still
  computed and still printed, so every reading before 2026-08-19 (`0.1094`, `0.1022`, …)
  stays comparable.
* `act2_slot_loss` — the excluded tokens, reported on their own line. They are **not**
  moved into the content bucket: `content_loss` is `G4.9`'s input, `G4.9` has been seen
  falling and is credited in DoD item 6, and re-basing a working gate's input to repair a
  different gate is not a repair.

🔴 **Two costs, declared rather than absorbed.** (1) Dropping the `,,` token also drops the
`ACT`-terminating comma fused into it, which *is* forced — the exclusion is slightly wider
than the defect. It makes the arm **harder** to pass, so the error runs in the conservative
direction, but it is an error and it is written down. (2) The premise that `,,` is one pure
delimiter token was reached arithmetically (122.3 measured delimiter tokens per record
against 124.0 predicted by a merged `,,` and 145.8 by standalone commas) and is being
**measured** by `tools/4thJ_step4_g42_token_census.py` on the tokenizer itself. **If that
census fails, D-S4-4 is withdrawn, not adjusted.**

🔴 **REGISTRATION.** This basis was chosen **after** seeing the `0.1094` readings. It may
never be presented as pre-registered. It must be **seen failing** before it is credited.

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| 🔴 **`collapse_content` — flatten `ACT`/`ACT2` to one constant, leave `DUR`/`LOC`/`COP` real** | **`G4.2`**, both arms together (`V4.d` is strict `AND`) | `G4.5`, **`G4.15`** (the lever leaves every `<eor>` in place in the corpus, which is what `G4.15` reads), `G4.11`, `G4.13`, `G4.14` — 🔴 **`G4.7` is no longer a free entry on this list**: since `D-S4-7` it reads the GENERATED sample, and whether a model trained on collapsed content still terminates is an empirical question this table cannot answer in advance. Declared, not verified — but **`G4.9` is a KNOWN collateral fall at 4,000 records and above** (FINDING 26), dose-dependent, and must be quoted with any use of this lever |

**Pre-registered outcome, written before the run.** Arm two is already nailed
(`gen_entropy = 0.000` at every budget). Arm one now depends on whether the **forced-basis**
clean delimiter loss crosses `0.05`. Removing the `act2` share from the last reading leaves
roughly `0.075`, which is **still above the band**. So: if the clean baseline does not cross
`0.05` on the forced basis, **the demonstration is VOID and is reported VOID**, `G4.2`
remains in `never made to fall`, and the coverage clause stays `FAIL`. D-S4-4 makes the arm
**satisfiable in principle**; it does not make it pass, and a re-point that is followed by a
pass it did not earn would be the band change this project refuses, wearing a different name.

---

### 2026-08-20 (night) — `D-S4-7` applied: `G4.7` moves to the generated sample, the corpus check becomes `G4.15`

🔴 **`FINDING 46` in one line: `G4.7` never once looked at the model.** It was scored on
`train_recs`, before the first optimiser step, so the only thing it could ever measure was the
Step 3 build. It read `31560/31560` at the start of the `it` fold — and that fold's epoch 1 then
generated **599 terminated diaries out of 600**. One diary ran past its terminator, the trainer
printed the count on the epoch line, and **no gate in the battery scored it.**

**What changed in `tools/4thJ_step4_train.py`** (1,808 → 1,867 lines, backup
`4thJ_step4_train.py.bak_ds47`, md5 `f6746949271e0164de0fa31de66499c0`):

* `gate_g4_15(recs)` — the corpus reading, **byte-for-byte the old arithmetic and the old
  threshold** (`TH.G4_7_REQUIRED_FRACTION`, unchanged at `1.0`), under a new id. Run once at
  training start; carried in `gates_at_start` where `G4.7` used to sit.
* `gate_g4_7(gen_texts)` — the same rule applied to the **generated sample**, scored at every
  validation epoch and at every `D-S4-5` mid-epoch probe. It writes `g4_7_verdict` into the
  metrics row and `G4.7` into `detectors["epochs"]`, and the epoch line now prints a verdict
  instead of a bare count.
* No threshold moved, no band moved, and no other gate changed what it reads.

🟢 **The re-pointed gate has already been seen failing, on real output, at zero compute cost.**
Replayed against the three fold logs already on disk: `es` PASS, `uk` PASS, `it` **600/600 at
epoch 0 and 599/600 at epoch 1 → FAIL**. That is the first model-side defect any Step 4 gate has
caught on a LOCO fold. It co-occurs with the `it` epoch-1 runaway (`G4.1` FAIL with all six strata
**above** the band); co-occurrence is not causation and is recorded as co-occurrence.

🔴 **The perturbation table had to move with it.** `strip_eor_1pct` edits the corpus, so since
this ruling it fells **`G4.15`**, not `G4.7` — a run scored against the old table would credit the
fall to a gate the lever cannot reach. `G4.7`'s own lever is `strip_eor_gen` in
`tools/4thJ_step4_g47_coverage.py`, which was written for exactly this basis and needs no training
run. **It is deliberately not duplicated inside the trainer:** one lever, one implementation, no
drift.

⚪ **Two comments inside the trainer that named the wrong gate were corrected** (`DiaryDataset`
and the `strip_eor_1pct` block, both of which explained themselves in terms of "`G4.7` reads
`train_recs`" — true before the ruling, false after it).

🔴 **Still owed:** the gate count in the 2026-08-14 entry above ("Fourteen gates, fifteen
perturbations") is now **fifteen gates, sixteen perturbations**. Left as written, because that
entry is a dated record of what was true when it was written; the current count is the gate table
at the top of this document.

### 2026-08-27 (Qwen comparison arm, `1287613`) — NO GATE, BAND OR THRESHOLD MOVED; ONE GATE SEPARATED THE TWO BACKBONES

Record: `4thJ_04_finetuneLLM.md`, entry 2026-08-27. Job `1287613` `COMPLETED 0:0`, 13:33:05,
fold `es`, `Qwen/Qwen2.5-7B` rev `d149729398750b98c0af14eb82c78cfe92750796`, LoRA.

🟢 **`G4.11` PASS 16/16 on this manifest.** `trainable: "lora"` is present, so the arm satisfies the
key that `FINDING 157` added and that the shipped ceiling manifest fails by design. This is the
first run whose manifest was written by the tightened emitter and scored by the tightened gate.

🟢 **`D-S4-17` verified on file, not asserted.** `max_len 1280` on all three `es` arms
(`1286209`, `1287378`, `1287613`), read from each job's own stdout invocation line. Truncation on
the Qwen arm: **train 12/48,594 = 0.0247 %, val 3/5,520 = 0.0543 %**, against `D-S4-17`'s 1.0 %
`CONTAMINATED` bar. 🔴 **The two Llama arms carry no measured rate** — the instrumentation
post-dates them — and their tokenizer differs, so their rate may not be inferred from Qwen's.
A methods sentence claiming equal truncation across arms would be unsupported.

🔴 **`G4.1` FAIL 3/3 epochs on both backbones, and the difference is below its own noise floor.**
Worst band `1.568` (primary) vs `1.539` (Qwen) — a gap of **0.029** against the `es` sampling-noise
floor of **0.529** from `D-S4-16`, i.e. **18× inside** it. **Only the verdict is comparable**; the
band counts are not. Reporting the Qwen arm as an improvement would be reporting noise.

🔴 **`G4.9` is the only gate that separates the arms, and it separated them for a visible reason.**
Primary PASS, Qwen **FAIL**. Qwen's held-out `content` is **0.5187 → 1.2261 → 0.8739** — epoch 1 is
a runaway carrying `G4.1 [V4.a: only 1 scorable strata]` and `G4.7 [gen-terminated 558/600]` with
it. ⚪ `G4.9` was designed to catch exactly a non-monotone checkpoint sequence, and the earlier note
in this document that *"`regression = 0.0` in all six is guaranteed by a two-epoch monotone run,
not earned — Leg 5's three epochs are the first place `G4.9` can say anything"* is now discharged:
**`G4.9` has said something, and it said FAIL on a real three-epoch run.** That is the gate's first
substantive verdict.

🟢 **Coverage clause PASS on the generation-side perturbation probe, by the correct route.**
`G4.1`, `G4.4` and `G4.7` are all FAIL at the null baseline, so each is printed
`NOT ASSESSABLE as STAY CLEAN` or `VOID` rather than credited — *a gate down before the
perturbation cannot be seen falling*. **Gates credited as seen falling on this probe: none.
Gates passing at baseline and never felled: none.** No gate was quietly banked.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` recomputed inside the job and equal to
`Step6_docs/outputs_step6/prereg.md`. `G4.3` FAIL on both arms (rise `0.1062` primary,
`0.0387` Qwen, need ≥ 0.15); `G4.6` FAIL on both; `G4.10` `REPORTED_NOT_THRESHOLDED` on both.
**No threshold, band or gate definition changed in this entry.**
