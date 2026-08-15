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
| `COP` is **five shared flags**, not one digit | `RL02`. 🔴 **Country-extra flags are carried in `harmonised.parquet` and are not serialised** (D-S2-2) — a symbol only one country can emit leaks country identity into a leave-one-country-out design |
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

### 3.2 — The `COP` packing decision

Five binary flags must reach the model without costing five tokens per episode. Options, to be
decided at implementation and **recorded with the measurement that decided it**:

* a single 0-31 integer (one token on this tokenizer if the value is a single small number — verify);
* two digits;
* five characters.

**Whatever is chosen, discarding flags to save tokens is forbidden.** Paper 1 identifies co-presence
handling as the source of load overestimation, and the flags are why we can fix it.

**Definition of done:** the packing is chosen by measuring token cost on the real tokenizer, and the
measurement is in `outputs_step3/cop_packing_measurement.md`.

### 3.2-bis — 🔴 Secondary activity: **kept in the data, not in the record. Decided 2026-08-14**

Finding F-ES-6: Spain records a secondary activity on **340,269 of 2,778,480 slots, 12.2 %**, and the
Step 1 record originally had nowhere to put it. Author call, on the manager's recommendation, taken
for precision:

* **`act2_raw` is carried** through Step 1 and Step 2, in the intermediate record and in
  `harmonised.parquet`. Nothing recorded is discarded, and **three states stay distinguishable**: not
  recorded by the instrument, recorded and blank, recorded with a value.
* **It is not serialised into the `DUR,ACT,LOC,COP` tuple today.** Two reasons, and only the first is
  about tokens:
  1. 🔴 **Coverage is measured on one country out of four.** A field that Spain records and the other
     three may not becomes a symbol only Spain can emit, which leaks country identity into a
     leave-one-country-out design. That is the same argument that keeps the country-extra co-presence
     flags out of `COP` (D-S2-2), and it is the stronger of the two.
  2. It would add a fifth element to every episode tuple, on a record whose whole justification in 3A
     is its token economy.
* **The decision to serialise it closes when, and only when, all four coverage rates are measured.**
  Write them into `outputs_step3/act2_coverage.md`, per country, as a share of episodes. Then:
  * if **all four** record it at a usable rate, serialising it becomes a real option and is decided by
    a token-cost measurement, exactly as `COP` packing is in 3.2;
  * if **any country does not record it**, it stays out of the record permanently and the reason is
    written into the limitations, not left implicit.
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

**Definition of done for this item:** `outputs_step3/act2_coverage.md` exists with four measured
rates **on both bases**, and this section records the decision those rates forced, including the
aggregation rule if the field is serialised.

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
