# Step 3 — Serialisation and tokenisation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 3. Validation: `4thJ_03_serialisation_val.md`

---

## STATUS

**✅ FORMAT DECIDED (`RL07`, field semantics from `RL02`). ✅ TOKENIZER DECIDED 2026-08-14 by our own
measurement. Implementation OPEN, nothing built.**

---

## AIM

Turn one harmonised episode table into text the model reads, and back again **exactly**.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| Episode form, not slot form | `RL07`, measured: 196-326 tokens against 924-1310 |
| Tuple is `DUR,ACT,LOC,COP` — **no `START`** | `RL07`. Start is the running sum; carrying it is redundant and misdescribes what the model emits |
| `LOC` is the real HETUS code, **not** `RL07`'s invented 1-6 | `RL02`. 🔴 **But not "10-39":** Spain carries `41`, public transport (F-ES-3, D-S2-3). The serialised alphabet is whatever `crosswalk_location.csv` emits, read from that file, never written here as a range |
| `COP` is ~~five~~ 🔴 **SIX** shared flags, not one digit, **packed as a single decimal integer 0-63** (D-S3-1, measured — 8 tokens/episode, no worse than the old single digit) | `RL02`, **widened by D-S2-8, 2026-08-16**: all three countries record parent co-presence (Spain `PADRES`; UK `WithMother` OR `WithFather`; Italy `cmadre` OR `cpadre`), so `cop_parent` is shared, not a Spanish extra. 🔴 **Country-extra flags are carried in `harmonised.parquet` and are not serialised** (D-S2-2) — a symbol only one country can emit leaks country identity into a leave-one-country-out design |
| `ACT` keeps **3 digits** | Author decision 6 |
| **No tokens are added to the vocabulary** | `RL05`. LoRA freezes embeddings; unfreezing costs ~16.8 GB of optimizer state and breaks GGUF and vLLM export |
| 🔴 **No mnemonic code remapping** | Our own measurement. It saves 12.9 % on Qwen and **costs 5.5 %** on the OLMo tokenizer we adopted |
| Tokenizer: **OLMo / dolma2 BPE** (`allenai/Olmo-3-1025-7B`, and identically `allenai/OLMo-2-0425-1B` for Leg-4) | Speed jobs 1234177, 1234199, 1234216 |

### The measurement that decided the tokenizer

One 25-episode diary in the adopted form, measured on Speed:

| Tokenizer | `311` | `45` | Episode | Full diary |
|---|---|---|---|---|
| **OLMo 2 / OLMo 3** | **1** | **1** | **8** | **200** |
| Qwen 2.5 / 3 / 3.5 | 3 | 2 | 12 | 303 |
| Mistral NeMo | 3 | 2 | 12 | 303 |
| Mistral 7B v0.3 | 4 | 3 | 13 | 304 |
| Llama 3.1, Gemma | *gated — not measured, nothing claimed* | | | |

**34 % shorter sequences for the identical string.** Leg-4 and Leg-5 share this tokenizer and this
vocabulary byte for byte, so **the serialised corpus is produced once and used by both legs.**

---

## INPUTS

* `../Step2_docs/outputs_step2/harmonised.parquet`
* `../Step2_docs/outputs_step2/copresence_availability.md` — the prefix must not claim a flag a
  country never recorded

---

## WORK ITEMS

### 3.1 — The record

```
<conditioning prefix>  |  DUR,ACT,LOC,COP  DUR,ACT,LOC,COP  ...  <eor>
```

**Prefix fields**, in a fixed order, all drawn from the design strata so that Step 5's unweighted-loss
argument holds:

`country`, `age band`, `sex`, `household type`, `economic status`, `day type`, `season`,
**`MODE`**, **`SCHEME`**

🔴 **`MODE` and `SCHEME` are constant across the entire training corpus** (paper self-completion;
ACL 2008/2010). They teach the model nothing today and cost a handful of tokens. They exist so that
adding a wave, or seventeen Track A countries, never changes the record format.

🔴 **There is no `YEAR` field and there never will be.** Naming the instrument cannot be
extrapolated; naming the time invites exactly the projection this paper does not make.

### 3.2 — The `COP` packing decision — 🔴 **DECIDED 2026-08-16, D-S3-1**

**`COP` is serialised as a single decimal integer, 0-63.** Measured, not asserted: Speed job
**1252633**, OLMo/dolma2 BPE (`allenai/OLMo-2-0425-1B`, stated stand-in for the 7B backbone's vocab),
every candidate measured in situ inside `DUR,ACT,LOC,<COP>;` and inside a full 25-episode diary, with
all 64 values swept. Full table and the exact strings: `outputs_step3/cop_packing_measurement.md`.

| Candidate | Worst case, tokens/episode | 25-episode diary |
|---|---|---|
| **decimal 0-63 — CHOSEN** | **8**, all 64 values | **200** |
| two octal digits | 8, all 64 values | 200 |
| two hex characters | 9, whenever a hex digit is a-f | 210 |
| six characters `010110` | 9, all 64 values | 225 |
| six comma-separated digits (do-nothing baseline) | 18 | 450 |

Three things this measurement settles, and they are worth separating:

* **Six flags cost nothing.** 8 tokens per episode is exactly what the *old single-digit* `COP` field
  cost. Widening the flag set from one digit to six packed bits is **free**, so D-S2-8 imposed no
  token penalty and no gate needs relaxing on its account.
* **The do-nothing baseline more than doubles the corpus.** 450 against 200 tokens per diary. That is
  the number that justifies packing at all, and it is now quantified rather than assumed.
* 🔴 **Six-character binary was rejected on a pre-registered threshold, not on taste.** At 225 tokens
  per diary it sits **above `G3.5`'s median band of 220** before a single real record is serialised.
  Choosing it would have meant moving `G3.5`, which is the one move this project does not make.

Decimal was taken over octal — they tie at 8 — because a raw corpus a human can read without an
octal-to-binary step is cheaper to audit, and no measurement separates them.

🔴 **The bit order is part of the decision and must be frozen where the flags are defined, not here.**
`crosswalk_copresence.csv` (D-S2-8) gains a `bit_position` column, 0-5, and the encoder reads the
order from that file rather than hard-coding it. Two encoders disagreeing about which bit is
`cop_alone` produce a corpus that round-trips perfectly through `G3.1` and means something else —
the failure mode `G3.13` exists for.

**Open, and honestly open:** this was commissioned as a *token-cost* measurement and it answers only
that. Whether a packed integer is as **learnable** as six positional characters is unmeasured; a model
must recover 64 arbitrary codes rather than read six aligned slots. It is not free to revisit — the
packing is fixed once `corpus.jsonl` exists — so if it is to be tested, the place is a Step 4 ablation
on a subset, before the full corpus is emitted.

---

*The original statement of the problem, retained because the reasoning is the record:*

🔴 **SIX** binary flags must reach the model without costing six tokens per episode *(superseded:
"five"; D-S2-8 promoted `cop_parent` to the shared core on 2026-08-16, so the packed range is **0-63**,
not 0-31)*. Options, to be decided at implementation and **recorded with the measurement that decided
it**:

* a single **0-63** integer;
* six characters, `010110`;
* two octal digits, or two hex characters;
* six comma-separated digits — the do-nothing baseline, measured so the saving is quantified rather
  than asserted.

🔴 **Measure each candidate IN SITU, inside a complete episode tuple and a complete 25-episode diary
— never as a bare string.** BPE merges across the comma and the semicolon, so the cost of `45` alone
is not its cost inside `20,311,11,45;`. **`RL18` reached the wrong recommendation by exactly this
error**, counting a bare fragment at 8 tokens when in context it was 11. That near-miss is recorded in
this document's first Progress Log entry and it applies here verbatim.

🔴 **Sweep all 64 values and report the worst case, not a lucky example.** A packing that costs 1 token
for `7` and 2 for `63` costs 2. The value range is small enough that there is no excuse for sampling it.

**Whatever is chosen, discarding flags to save tokens is forbidden.** Paper 1 identifies co-presence
handling as the source of load overestimation, and the flags are why we can fix it.

**Definition of done:** the packing is chosen by measuring token cost on the real tokenizer, and the
measurement is in `outputs_step3/cop_packing_measurement.md`. 🔴 **No `COP` gate is pre-registered
before that file exists** — a threshold written ahead of the measurement is a threshold chosen to be
passed.
**✅ DONE 2026-08-16.** The file exists, the packing is decimal 0-63, and `G3.14` was pre-registered
*after* the number, in that order.

### 3.2-bis — 🔴 Secondary activity: **kept in the data, not in the record. Decided 2026-08-14**

Finding F-ES-6: Spain records a secondary activity on **340,269 of 2,778,480 slots, 12.2 %**, and the
Step 1 record originally had nowhere to put it. Author call, on the manager's recommendation, taken
for precision:

* **`act2_raw` is carried** through Step 1 and Step 2, in the intermediate record and in
  `harmonised.parquet`. Nothing recorded is discarded, and **three states stay distinguishable**: not
  recorded by the instrument, recorded and blank, recorded with a value.
* **It is not serialised into the `DUR,ACT,LOC,COP` tuple today.** Two reasons, and only the first is
  about tokens:
  1. ~~🔴 **Coverage is measured on one country out of four.** A field that Spain records and the other
     three may not becomes a symbol only Spain can emit, which leaks country identity into a
     leave-one-country-out design.~~ 🔴 **THIS REASON IS RETIRED, 2026-08-16.** All three countries in
     the corpus record a secondary activity — Spain `ASECU`, the UK `What_Oth1`, Italy `catcon` — so
     it is **not** a symbol only one country can emit and the leak argument does not apply to it.
     *(It still applies, unchanged, to the country-extra co-presence flags and to the UK's second and
     third secondary columns, per D-S2-2 and D-S2-7.)*
  2. It would add a fifth element to every episode tuple, on a record whose whole justification in 3A
     is its token economy. **This is now the only surviving reason**, and it is a measurement question,
     not a principle.
* ~~**The decision to serialise it closes when, and only when, all four coverage rates are measured.**~~
  🔴 **Rewritten 2026-08-16 for the three-country corpus.** The branch that would have kept the field
  out permanently — *"if any country does not record it"* — is **CLOSED: every country records it.**
  What remains is the token-cost branch. Write the rates into `outputs_step3/act2_coverage.md`, per
  country, **on both bases** (see below), then decide by measuring token cost exactly as `COP` packing
  is decided in 3.2.
* 🔴 **D-S2-7 changed what would be serialised, and it is not what this section assumed.** Italy's
  `catcon` is `CLS-var13` — 34 flat 2-digit modalities, *a different and coarser classification, not a
  truncation of `catpri`* (F-IT-3). So the harmonised `ACT2` is **2-digit, arity 1, and carries its own
  crosswalk**, while `ACT` stays 3-digit. If `ACT2` is ever serialised it enters the tuple as a
  **2-digit** symbol, and the asymmetry with `ACT` must be stated in the record format rather than
  discovered by whoever writes the encoder.
* **Measured so far, and the bases are not interchangeable:** Spain **12.2 % of slots / 18.8 % of
  episodes**; the UK **27.75 % of episodes** (`What_Oth1`; the UK ships episodes natively, so it has no
  slot base at all); **Italy is not yet measured.** 🔴 **`act2_coverage.md` is not complete until Italy
  is measured**, and a rate quoted without its denominator is not a rate.
* 🔴 **Until that file exists, no step may condition on `act2`, and no gate may test it as though the
  corpus carried it.** Carrying a field is not the same as using it, and the difference has to stay
  visible in the documents or a later session will find the column and assume it was blessed.

**Where it is already load-bearing:** Step 9. An appliance triggered by an activity that is only ever
*secondary* — a television on while eating, a washing machine running while the respondent does
something else — is exactly the load paper 1 got wrong by construction. That is why the field is kept
even though it is not serialised.

🔴 **And Step 9 does not receive it, which this section originally implied it would.** Step 9 consumes
Step 7's **generated** diaries, and those carry no `act2` precisely because it is not serialised.
Resolved 2026-08-14 in `../Step9_docs/4thJ_09_enduseLoads.md`: the appliance trigger fires from the
primary code alone, and `act2` is used only to **calibrate** `P(appliance | primary activity)` on the
real corpus, never as a runtime field. Gate `G9.14` asserts that. **Read the two sections together —
separately, each looks complete.**

🔴 **If the four coverage rates come back usable and this field is serialised after all, that has to
happen before `corpus.jsonl` is emitted.** A fifth tuple element added later invalidates the corpus,
the Step 7 grammar and every trained fold.

🔴 **The coverage rate is not one number, and Step 1 measured why. Added 2026-08-14.** `act2_raw` is
carried at **episode** level, and the episode split key does not include `ASECU`, so a single episode
can span several different secondary activities. Measured on Spain: of 430,754 episodes, **11,216 mix
a blank and a non-blank `ASECU` across their own slots and 13,009 carry more than one distinct
value.** The reader keeps **first-of-run**, the same rule it uses for `act_raw`, and `G1.11` proves
that rule is reproducible from the raw file — **it does not prove it is the right rule, and for those
13,009 episodes it is not.**

Consequences this item must settle, not Step 1:

* **`act2_coverage.md` records BOTH accountings per country** — the slot-level share (Spain: 340,269
  of 2,778,480, 12.2 %) and the episode-level share (Spain: 80,800 of 430,754, 18.8 %) — **and never
  quotes one as the other.** They differ by a factor that depends on episode length, so a
  cross-country comparison drawn from mixed bases would compare instrument design, not behaviour.
* **If this field is ever serialised, first-of-run is a decision that has to be taken deliberately.**
  The alternatives are splitting episodes on `ACT2` as well, which raises the episode count and the
  token cost that 3A exists to control, or carrying a "mixed" symbol. 🔴 **Choosing by inheriting
  Step 1's convenience default is how a modelling choice gets made without anyone deciding it.**
* **Step 9's calibration is affected before any of that.** `P(appliance | primary activity)` is
  calibrated from the real corpus, and if it is calibrated from first-of-run `act2` it is calibrated
  from a lossy summary of the secondary stream. **Measure it on slots, not episodes** — Step 9 needs
  a rate, not a timing, and the slot-level accounting is the one that has not thrown information away.

**Definition of done for this item:** `outputs_step3/act2_coverage.md` exists with **three** measured
rates *(superseded: "four", decision 16)* **on both bases where both bases exist** — 🔴 **the UK and
Italy ship episodes natively and have no slot base, so for them the episode share is the only rate and
must be labelled as such, never silently compared to Spain's slot share** — and this section records
the decision those rates forced, including the aggregation rule if the field is serialised.

### 3.3 — The encoder and the decoder

Two functions, and the decoder is not optional:

* `encode(diary) -> str`
* `decode(str) -> diary`

**Requirement: `decode(encode(d)) == d` exactly, for 100 % of the corpus**, compared field by field,
not as a string. Reversibility is what makes the episode form lossless: each episode unpacks to
`DUR / 10` identical slots.

### 3.4 — Tokenizer assertions before any training run

From `RL05`'s failure-mode list, run once over 1,000 sampled records and again over the full corpus:

* `tokenize(detokenize(ids)) == ids`;
* every 3-digit `ACT` code is **1 token**;
* no record exceeds the context budget;
* 100 % of records terminate with the `<eor>` marker. 🔴 A corpus where some completions do not
  terminate produces a model whose generation never stops.

### 3.5 — Emit the training corpus

`outputs_step3/corpus.jsonl` — one record per diary, with a held-out split that is **by respondent,
never by diary**, so a person's two diary days cannot straddle the split.

Also emit `outputs_step3/token_stats.md`: token-length distribution per country, per stratum, and the
packing efficiency actually achieved against the 200-token benchmark.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step3/corpus.jsonl` | Step 4 (both legs) |
| `outputs_step3/encoder.py` + `decoder.py` | Step 7 — the decoder is what turns generated text back into diaries |
| `outputs_step3/token_stats.md` | Step 4 sequence-packing configuration |
| `outputs_step3/cop_packing_measurement.md` | The methods section |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`. CPU only — tokenizer work needs no GPU. Reuse the venv pattern from
`../tools/4thJ_tok_setup_and_run.sh`; it does not touch `envs/step4`.

---

## WHAT BLOCKS THIS STEP

Step 2 must have emitted `harmonised.parquet`.

**What this step blocks:** Step 4 has no input without it. Step 7's grammar is defined against this
record format, so a format change here is a Step 7 change.

---

## DEFINITION OF DONE

1. Record format frozen, prefix field order fixed and written down.
2. `COP` packing chosen **by measurement**, and the measurement recorded.
3. Round-trip exact on 100 % of the corpus.
4. All four tokenizer assertions pass on the full corpus, not a sample.
5. Corpus emitted with a respondent-level split.
6. All Step 3 gates PASS **and each has been seen failing**.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* Tokenizer closed by our own measurement rather than by `RL18`, which recommended the opposite on a
  mis-counted figure: it reported the mnemonic episode `45,wrk,11,0;` at 8 Qwen tokens when it is 11.
* 🔴 **The mnemonic remapping was one edit away from entering this document as a design element.**
  It would have made every diary 5.5 % *longer* on the tokenizer we actually adopted. Recorded
  because the near-miss is the useful part: a workaround devised for one tokenizer was about to be
  written into the serialisation schema for another.

### 2026-08-14 (later) — F-ES-6 decided. Item 3.2-bis added

* **Secondary activity is kept in the data and kept out of the record**, on the author's instruction
  to favour precision. Carrying it costs a column; serialising it costs a fifth tuple element and,
  more importantly, risks a symbol only Spain is known to emit.
* 🔴 **The leak argument is the reason, not the token budget.** A field present for one country and
  absent for three is a country marker, and a country marker inside a leave-one-country-out design
  measures our bookkeeping rather than transfer. Same argument as the country-extra co-presence flags
  in D-S2-2, and it should be quoted together with it.
* **The decision closes on a measurement.** Four coverage rates in `outputs_step3/act2_coverage.md`.
  All four usable, serialisation becomes a token-cost question decided the way `COP` packing is; any
  country missing it, the field stays out permanently and the reason goes into the limitations rather
  than staying implicit.
* **Until that file exists, no step conditions on `act2` and no gate tests it.** Written down because
  a later session will find the column in `harmonised.parquet` and reasonably assume it was blessed.

### 2026-08-14 (third entry) — the Step 9 half of F-ES-6 was missing, and is now written

* 🔴 **This document said `act2` is "already load-bearing in Step 9". Step 9 never receives it.** Step 9
  consumes Step 7's *generated* diaries, which carry no secondary activity precisely because it is not
  serialised. Both documents were internally consistent; the defect lived **between** them.
* **Found by reading the two steps against each other**, which is the only way this class of gap is
  found. Neither document is wrong on its own, and neither would have failed a review of itself.
* **Resolved without changing the record format**: the trigger fires from the primary code, `act2`
  calibrates the trigger probability on the real corpus, and `G9.14` asserts `act2` never appears among
  the trigger's runtime columns. 🔴 **A trigger reading an absent column raises nothing — it silently
  never fires**, which is why that gate exists rather than a comment.
* **A deadline is now explicit:** if the four coverage rates make serialisation the right call, it has
  to happen **before `corpus.jsonl` is emitted.** A fifth tuple element added afterwards invalidates
  the corpus, the grammar and every trained fold.

### 2026-08-14 (third entry) — 3.2-bis extended after Step 1 measured `act2` at episode level

The Step 1 gate re-run on Spain (`../Step1_docs/outputs_step1/gate_report_step1_spain.txt`) produced a
fact this item needed and did not have: **the secondary-activity coverage rate is different at slot
level and at episode level, and the gap is not a rounding artefact.** 340,269 of 2,778,480 slots
(12.2 %) against 80,800 of 430,754 episodes (18.8 %), because **11,216 episodes mix blank and
non-blank `ASECU` and 13,009 carry more than one distinct value.**

Three things added to 3.2-bis, none of which changes the decision F-ES-6 already took:

* **`act2_coverage.md` must carry both bases per country**, and never quote one as the other. Mixed
  bases across four countries would compare episode length, which is instrument design, rather than
  the behaviour the rate is supposed to describe.
* 🔴 **First-of-run is Step 1's aggregation convenience, not a modelling decision.** If `act2` is ever
  serialised, the rule is chosen here, deliberately, against the token cost of splitting episodes on
  `ACT2`. Inheriting the default silently is how a choice gets made without anyone making it.
* **Step 9 calibrates `P(appliance | primary activity)` on SLOTS, not episodes.** It needs a rate, not
  a timing, and the slot accounting has not discarded the multi-value runs.

No threshold moved and nothing was serialised. The item's Definition of done now requires both bases.

### 2026-08-16 — 🔴 `COP` is SIX flags, not five. The `act2` leak argument is retired. The packing measurement is commissioned

Step 2 closed its three heterogeneities today (D-S2-6, D-S2-7, D-S2-8) and three of those consequences
land here, in the record format, before anything is built.

* 🔴 **`COP` packs SIX flags, so the packed range is 0-63, not 0-31.** D-S2-8 found that `PADRES` was
  never a Spanish extra: all three countries record parent co-presence, Spain in one flag, the UK in
  two (`WithMother`, `WithFather`) and Italy in two (`cmadre`, `cpadre`). A shared flag every country
  records belongs in the serialised tuple; the two-column national forms stay as extras and stay out,
  under the same rule as before. **This is a widening of the shared core forced by measurement, not a
  format change of convenience** — and it had to reach this document before the packing was measured,
  because a five-flag measurement would have been the right answer to the wrong question.
* 🔴 **The `act2` leak argument is RETIRED, and it was the stronger of the two reasons.** 3.2-bis kept
  secondary activity out of the tuple mainly because it was measured on one country of four and might
  have become a symbol only Spain could emit. **All three countries record it** — Spain `ASECU`, the
  UK `What_Oth1`, Italy `catcon` — so that argument no longer applies to this field. **The branch that
  would have excluded it permanently is closed.** What survives is the token-cost argument alone, and
  that is a measurement, not a principle. It is decided the way `COP` packing is.
* 🔴 **But D-S2-7 changed what would be serialised.** Italy's `catcon` is `CLS-var13`: 34 flat 2-digit
  modalities, a *different and coarser* classification, **not a truncation of `catpri`** (F-IT-3). So
  the harmonised `ACT2` is arity 1, 2-digit, with its own crosswalk, while `ACT` keeps 3 digits. **If
  `ACT2` ever enters the tuple it enters as a 2-digit symbol**, and that asymmetry is written here
  rather than left for whoever writes the encoder to discover.
* **`act2_coverage.md` now needs three rates, not four, and the bases are not interchangeable.**
  Spain 12.2 % of slots / 18.8 % of episodes; the UK 27.75 % of episodes; **Italy still unmeasured.**
  🔴 **The UK and Italy ship episodes natively and have no slot base at all**, so for them the episode
  share is the only rate that exists and must be labelled as one. Comparing it to Spain's slot share
  would compare instrument design.
* **The `COP` packing measurement is commissioned on Speed**, five candidates for the six bits, each
  measured **in situ** inside a full episode tuple and a full 25-episode diary, **sweeping all 64
  values and reporting the worst case.** 🔴 **In situ and worst case are both deliberate.** `RL18`
  reached the wrong recommendation on this project by counting a bare fragment — 8 tokens for an
  episode that costs 11 in context — and the near-miss is recorded in this document's first entry. A
  packing that is 1 token for `7` and 2 for `63` costs 2, and 64 values is small enough that sampling
  it has no excuse.
* 🔴 **No `COP` gate is pre-registered until that measurement exists.** A threshold written before the
  measurement is a threshold chosen to be passed.

**Nothing was serialised, no threshold moved, and the tuple is still `DUR,ACT,LOC,COP`.** Step 3 stays
blocked on `harmonised.parquet`, which is blocked on the Step 1 sixteen-gate round now running as Speed
jobs 1252522 / 1252523 / 1252524 / 1252525.

### 2026-08-16 (later) — 🔴 **D-S3-1: `COP` IS A DECIMAL INTEGER 0-63. The measurement came back**

The measurement commissioned earlier today returned. Speed job **1252633** (COMPLETED, 42 s,
`sbatch -p ps --mem=16G -t 7-00:00:00`), tokenizer `allenai/OLMo-2-0425-1B` as the stated stand-in for
the backbone's OLMo/dolma2 vocabulary, script `tools/4thJ_cop_measure.py`, report at
`outputs_step3/cop_packing_measurement.md`. All five candidates measured **in situ** inside a full
episode tuple and a full 25-episode diary, and **all 64 values swept** — both conditions were met, so
the `RL18` failure mode is closed for this measurement.

**Result, worst case per episode / per 25-episode diary:** decimal 0-63 → **8 / 200**; two octal
digits → 8 / 200; two hex chars → 9 / 210 (whenever a hex digit is a-f); six characters → 9 / 225;
six comma-separated digits, the do-nothing baseline → 18 / 450.

**Decision: candidate 1, a single decimal integer 0-63.** Three findings, kept separate because they
are separate:

* **Widening `COP` from one digit to six packed flags is free.** 8 tokens per episode is what the old
  single-digit field already cost. **D-S2-8 therefore imposed no token penalty**, and no threshold
  anywhere needs relaxing on its account. Had this come back at 10, the six-flag decision would have
  had to be re-argued against the budget; it did not.
* **The do-nothing baseline more than doubles the corpus** — 450 against 200 tokens per diary. The
  saving is now quantified rather than asserted, which is the whole reason the baseline was measured.
* 🔴 **Six-character binary was rejected by a pre-registered threshold, not by preference.** At 225
  tokens per diary it exceeds `G3.5`'s median band of **220** before a single real record exists.
  Adopting it would have required moving `G3.5`, and moving a threshold to admit a choice is the
  failure this project spends most of its effort avoiding. Decimal beat octal only on auditability —
  they tie at 8, and nothing measured separates them.

**Consequence written into Step 2, not left implicit:** `crosswalk_copresence.csv` gains a
`bit_position` column, 0-5, and the encoder **reads the bit order from that file**. A hard-coded order
in the encoder is a defect `G3.1` cannot see — encoder and decoder would agree perfectly and mean
something else. That is precisely the class `G3.13` exists for.

🔴 **Recorded as open, because it is:** this was commissioned as a token-cost question and answers only
that. Whether a packed integer is as **learnable** as six positional characters is unmeasured — the
model must recover 64 arbitrary codes instead of reading six aligned slots. The packing is frozen once
`corpus.jsonl` exists, so if it is ever to be tested the place is a **Step 4 ablation on a subset,
before the full corpus is emitted**. Not a blocker; a decision with a known unmeasured edge.

Order of operations was observed: **the file existed, then the packing was chosen, then `G3.14` was
pre-registered in the validation document.** The gate followed the number.

Also carried over from the employee's report, unverified here and flagged as such: the claimed vocabulary
identity between `OLMo-2-0425-1B` and `Olmo-3-1025-7B` was a **premise of the task, not re-derived**,
and the earlier 200-token reference from jobs 1234177 / 1234199 / 1234216 was quoted, not re-run.
