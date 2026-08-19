# Step 3 — Serialisation and tokenisation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 3. Validation: `4thJ_03_serialisation_val.md`

---

## STATUS

**✅ FORMAT DECIDED (`RL07`, field semantics from `RL02`). ✅ TOKENIZER DECIDED 2026-08-14 by our own
measurement.** 🟢 **✅ BUILT, 2026-08-17 — `/speed-scratch/o_iseri/4J_step3_corpus.jsonl`, 73,254
records, Speed job 1255620, round-trip 100 % exact.** All ten Step 3 decisions closed (D-S3-1 …
D-S3-10). 🔴 **NOT yet DONE: the independent sixteen-gate battery has not run**, and until it reports,
every number above is the build's own self-report. See the Progress Log entries of 2026-08-17 (night),
and read the two author rulings there before quoting `G3.5` or the null-`act` handling.

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

`country`, `age band`, `sex`, `household type`, `economic status`, `day type`

🔴 **SIX fields — D-S3-11 (author, 2026-08-17, evening) removed `MODE` and `SCHEME`.** They are
documented below as constants across the corpus. They are not. Job `1256012` measured **two** `mode`
values and **three** `scheme` values (`eet_2009_2010`, `uktus_2014_2015`, `usodeltempo_2013_2014`),
each one a module constant **hard-coded in its country's reader** — `4thJ_read_spain.py:130`,
`4thJ_read_uk.py:42`, `4thJ_read_italy.py:108` — never read from a respondent. They therefore carried
exactly what `country` already carries and nothing else, and under LOCO they handed the held-out
country a symbol training never showed the model. Collapsing them to one invented constant was
considered and **refused**: `hetus_acl2008` exists in no source file, and inventing a value at
serialisation time is the silent fill this project does not do to research data. Both columns stay in
`harmonised.parquet` and are simply never serialised, exactly like the six `strat_*_raw` carriers.
**`G3.10` passes because the corpus stopped carrying years, not because its regex was narrowed.**

🔴 **Was eight fields, not nine — `season` was dropped on 2026-08-17 by D-S2-19.** Spain's `TRIM` and
Italy's `meseri` are each delivered pre-banded, their boundaries are offset by one month at every
edge, neither is a union of the other, and neither country ships anything finer. No non-trivial season
classification is expressible in all three deliveries, so the stratum is dropped for all three rather
than kept for the two that agree. `strat_season_raw` still ships in the table and is never serialised.

🔴 **Where these eight come from, added 2026-08-17 after D-S2-18, because until that date five of them
came from nowhere.** `harmonised.parquet` as shipped on 2026-08-16 carried `country`, `mode` and
`scheme` and **none of the others.** Step 2 is being re-run with eleven added columns; this table
is the contract between the two steps and the encoder reads these column names and no others:

| Prefix field | Column | |
|---|---|---|
| country | `country` | 🔴 **lowercased on read** (D-S2-16) |
| age band | `strat_age_band` | `11-14, 15-24, …, 65-74, 75+` — unions of Italy's `claseta2` bands (D-S2-18 rule 2, approved D-S2-19) |
| sex | `strat_sex` | `male, female` |
| household type | `strat_hh_type` | five bands plus `unknown`; **no band splits on child age** — Italy's `tipfa2m` carries no age qualifier |
| economic status | `strat_econ_status` | six bands plus `unknown` |
| day type | `strat_day_type` | `weekday, saturday, sunday`; the UK source is `ddayw`, not `DiaryDay_Act` |
| ~~MODE~~ | ~~`mode`~~ | 🔴 **REMOVED by D-S3-11.** Not constant: two values, hard-coded per reader. Column kept in the table, never serialised |
| ~~SCHEME~~ | ~~`scheme`~~ | 🔴 **REMOVED by D-S3-11.** Not constant: three values, each carrying its survey's field years. Column kept in the table, never serialised |

🔴 **The six `strat_*_raw` carriers are NOT serialised.** They exist so the banding can be re-derived
from the shipped table; putting a national source value into the prefix would emit a symbol only one
country can produce, which is the leak D-S2-2 closed for co-presence and D-S2-18 closes here.

🔴 **If the additive round drops a stratum** — because one country cannot supply it — **it is dropped
from the prefix for all three countries.** *(This clause fired twice: D-S2-19 dropped `season`,
D-S3-11 dropped `mode` and `scheme`.)* `G3.7` counts **the shipped fields, not a number** — which is
why the count could move from nine to eight to six without the clause being rewritten. **A prefix
that carries a field for two countries and blanks it for the third is forbidden**, and if the dropped
stratum is household type or economic status, Step 5's 5B has to be re-argued before anything is
trained.

🔴 ~~**`MODE` and `SCHEME` are constant across the entire training corpus** (paper self-completion;
ACL 2008/2010). They teach the model nothing today and cost a handful of tokens. They exist so that
adding a wave, or seventeen Track A countries, never changes the record format.~~
**FALSE, and struck by D-S3-11 on 2026-08-17.** Job `1256012` measured two `mode` values and three
`scheme` values. The claim was true of the corpus as conceived — one harmonised HETUS instrument —
and never true of the corpus Step 2 shipped. The stated justification was also self-defeating: the
fields were kept so that adding a wave would never change the record format, but if a future wave
ever gave them real variety they would be a leak again, which is the defect being repaired. A slot
that is only safe while it is empty does not earn its tokens. **Both fields are gone from the
prefix.**

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

🟢 **CLEARED, 2026-08-17 (night). Nothing on this list still blocks Step 3.** Both items below are
resolved and are kept as the record of what had to happen first.

* ~~Blocked on the **D-S2-18 additive round** — eleven stratum columns, the D-S2-19 band set, a
  eighteen-gate Step 2 re-run.~~ ✅ **It landed.** `harmonised.parquet` carries 51 columns and all
  eight prefix fields have a source. `season` is not among them; D-S2-19 dropped it.
* ~~Blocked on `outputs_step3/act2_coverage.md`, Italy unmeasured, and an unrun token-cost
  measurement.~~ ✅ **Overtaken by the author's ruling on `ACT2`, which admitted it to the tuple as an
  empty-field form** — two adjacent commas when absent, no sentinel. The corpus was emitted with
  `ACT2` in it, so the "before `corpus.jsonl` is emitted" deadline was met rather than missed.
  `G3.15` is the gate that now guards it.

🔴 **One thing does still stand between this step and DONE, and it is item 6 below:** the independent
sixteen-gate battery has not run. **A corpus that exists is not a corpus that passed.**

**What this step blocks:** Step 4 has no input without it. Step 7's grammar is defined against this
record format, so a format change here is a Step 7 change.

---

## DEFINITION OF DONE

1. ✅ Record format frozen, prefix field order fixed and written down. **SIX prefix fields (D-S3-11
   struck `mode` and `scheme`; was eight), D-S3-8 delimiters.**
2. ✅ `COP` packing chosen **by measurement**, and the measurement recorded.
3. ✅ Round-trip exact on 100 % of the corpus — **73,254 / 73,254 diaries, job 1255620.**
4. ✅ All four tokenizer assertions pass on the full corpus, not a sample.
5. ✅ Corpus emitted with a respondent-level split — **58,801 / 6,533, intersection 0.**
6. ✅ **DONE, and it must be quoted with its qualifier: 19 of 20 gates PASS at baseline, all 19 were
   seen failing, `COVERAGE CLAUSE VERDICT: PASS`, and 21 of 21 perturbations felled their named
   gate — with one gate red by ruling, not by defect.** 🔴 **Never write this as 20 of 20.** The
   battery ran twice under `sbatch`: job `1256012` on the eight-field corpus (two baseline FAILs, a
   FAILing coverage clause, four unexpected `G3.1` falls, and a fifth defect found off-run — it is
   the run that found the defects, and its numbers are superseded for every prefix-dependent gate),
   then job `1257441` on the six-field rebuild after D-S3-11 / D-S3-12 / D-S3-13 were ruled and
   applied. The single remaining baseline FAIL is `G3.9` on the **UK fold alone** —
   `strat_hh_type = unknown`, 551 diaries — which **D-S3-14 ruled (a)**: it stays, as a declared and
   quantified limitation. `G3.13`, `G3.14 (b)`, `G3.15 (b)` and `G3.16` import nothing from
   `encoder.py` or `decoder.py`, as required. Evidence: `outputs_step3/gates_out/` (1256012) and
   `outputs_step3/gates_out_v2/` (1257441), both kept whole, neither overwriting the other.

🔴 **Items 1-5 above were re-established on the rebuilt corpus, not carried over on trust.** Job
`1257441` re-read all 2,024,068 rows and re-emitted from scratch: 73,254 records again, 0 rows and 0
diaries dropped, encode→decode 73,254 / 73,254 exact, `detokenize(tokenize(text)) == text` 73,254 /
73,254 at **character** level (D-S3-13), `<eor>` present on 73,254 / 73,254, 0 of 159 `ACT` codes
failing the one-token assertion, and the same respondent-level split under seed 42. Token stats moved
with the shorter prefix — **median 256.0 / p99 632.0 / max 1178** — and 🔴 **the `G3.5` band was NOT
re-tightened to match**; headroom against the ruled 1200 simply went from 9 tokens to 22.

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

### 2026-08-17 — 🔴 **The prefix had no source. Work item 3.1 now names its columns, and Step 3 is blocked again**

Step 3 was about to be handed to an employee. The manager checked its inputs first and found that
**six of the nine prefix fields do not exist in `harmonised.parquet`** — age band, sex, household
type, economic status, day type and season. The table supplies `country`, `mode` and `scheme`.

* **Neither document was wrong.** D-S2-12 specified a record contract and lists everything it carries;
  work item 3.1 specifies a record format and lists everything it needs. 🔴 **The defect lived between
  them, and it was found by reading one against the other** — the third defect of this class on this
  project, after `G9.14`'s missing half of F-ES-6 and the Step 4 / Step 6 fold-contract mismatch.
* 🔴 **`G3.7` would have caught it after `corpus.jsonl` was built.** Prefix completeness is
  pre-registered at zero records missing a field, so the corpus would have been emitted, the gate
  would have failed on 100 % of records, and Step 3 would have been rebuilt in full. The gate was
  working; it just sits downstream of the cheapest place to catch this.
* **The cheap repair was refused.** Cutting the prefix to what we hold would remove household type and
  economic status, and the parent plan's **5B** rests on the prefix containing the design strata —
  that is what makes the sampling mechanism conditionally ignorable and the training loss unweighted.
  **Dropping them reopens a decision `RL09` closed and that Step 5, Step 6 and the methods section all
  stand on.**
* **Resolved by D-S2-18**, an additive round on Steps 1 and 2. Work item 3.1 now carries the column
  table, the lowercase rule (D-S2-16) and the prohibition on serialising the `_raw` carriers.
* 🔴 **One contingency decided in advance rather than when it bites:** a stratum any country cannot
  supply is dropped **for all three** *(this fired twice: `season` by D-S2-19, then `mode` and
  `scheme` by D-S3-11, leaving six)*. **Never carried by two
  countries and blanked for the third** — that emits a symbol only some countries produce, which is
  D-S2-2's leak in the prefix instead of in `COP`.

**Nothing was serialised, no threshold moved, and the tuple is still `DUR,ACT,LOC,COP`.** Step 3 is
blocked on the additive round and on its own outstanding measurement — Italy's `act2` coverage, and
the token cost of a five-element tuple.

### 2026-08-17 (evening) — 🔴 **D-S3-1 re-verified and SURVIVES; D-S3-2 ACT2 IN; D-S3-3 `G3.5` re-based; D-S3-4 / D-S3-5 opened on the nulls**

Two measurements came back, jobs **1255223** (COP re-verification) and **1255237** (ACT2 tuple cost),
both against the real 2,024,068-row `harmonised.parquet`. Four crashed attempts preceded them and are
kept in `impl/2026-08-17_na-fix-rerun.md`; the substantive cause was one defect class hit at two
sites — a null guard written as `isinstance(x, float) and pd.isna(x)`, which misses `pd.NA`, the
sentinel that pandas' nullable dtypes actually use.

**D-S3-1 stands, and now on the right alphabet.** The accepted packing measurement (job 1252633) had
hard-coded numeric LOC placeholders instead of the four `crosswalk_location.csv` `target_class`
strings that D-S2-3 mandates. Re-measured with the real strings, per diary: decimal-0-63 **217.5**
median, six-chars **242.5**, two-octal 217.5, two-hex 218.0, unpacked CSV bits 467.5. 🔴 **The
ordering did not change and the reason for the choice did not change** — every candidate moved up by
roughly the same amount, decimal is still tied-cheapest, six-chars is still above 220. **The wrong
alphabet did not change the answer, and that is a result, not a licence** — it was checked, not
assumed. `tools/4thJ_cop_measure.py` was left exactly as it is, defect and all, as the record of what
was actually run.

**D-S3-2 — `ACT2` ENTERS THE TUPLE, as an empty-field slot before `LOC`.** Decided by the author on
the measurement, 2026-08-17. The tuple becomes:

```
DUR,ACT,ACT2,LOC,COP
```

with **the field left empty when there is no secondary activity**, not filled with a sentinel. Per
episode the placement is indistinguishable — ACT2 costs a flat **+2 tokens** in all four forms, and
Part A cannot discriminate at all. Per diary it discriminates sharply, because **77 % of episodes
carry no secondary activity** and the absent-encoding is therefore what dominates: empty-field before
LOC **238.0** median (+13, +5.8 % over the 225.0 baseline), empty-field after COP 257.0, and either
`'98'`-sentinel form **275.0 (+50, +22 %)**. The `'98'` sentinel was verified legal — it is absent
from all 43 shipped ACT2 target codes, so it does not repeat the `999` failure class — it is simply
the expensive choice, paid on every one of the 53,417 absent episodes. 🔴 **This had to be decided
before `corpus.jsonl` exists**: a fifth element added afterwards invalidates the corpus, the Step 7
grammar and every trained fold.

**D-S3-3 — `G3.5`'s band is RE-BASED on the measured distribution.** Decided by the author,
2026-08-17. 🔴 **This is a threshold moved after seeing the result, and it is recorded as one.** The
band was median ≤ 220 / p99 ≤ 400, anchored on a **single hand-made 25-episode diary measured at 200
tokens** — a point, never a distribution. Real diaries: **225.0 median / 559.0 p99 with no ACT2 at
all**, and 238.0 / 580.0 with it. The justification for re-basing is that **the band is broken before
ACT2 or COP packing is considered** — no encoding choice available to us brings the p99 under 400,
because the p99 diary simply has far more episodes than 25 — so the band was measuring the benchmark,
not the corpus. The new band must be set from the real distribution, stated in
`4thJ_03_serialisation_val.md` with this reason attached, and **must not be set to whatever the
corpus happens to produce** — it is a context-budget limit and has to stay one.

**D-S3-4 (null `LOC`) and D-S3-5 (null `COP`) — OPEN, imputation to be assessed first.** The two
measurements surfaced missingness that no earlier round had quantified:

* **`loc_class` is null on 24,800 rows, inside 8,873 of 73,254 diaries (12.1 %).** The measurement
  script dropped those diaries from its own sample and said so rather than silently including them.
* **All six `cop_*` flags are null together on 68,464 rows, inside 9,298 diaries — and only in the
  UK.** Zero in ES, zero in IT. A row has all six or none, which reads as "co-presence not collected
  for this episode", not as six independent missing values. They are currently encoded as `0`, which
  is **indistinguishable from a genuine "alone: no, everyone else: no"** — and being UK-only, it is a
  country-specific artefact the model could learn as a UK trait, which is D-S2-2's leak arriving
  through the back door.

🔴 **The author's ruling on both is conditional and in this order:** measure whether imputation from
neighbouring episodes is defensible; **if it is not, fall back to an explicit `unknown` LOC class and
an explicit out-of-range "not reported" COP code.** Neither fallback drops data, and neither is
silent. What "defensible" means is a measurement, not an opinion — whether the null is a short gap
between two known and *agreeing* neighbours, or a long run, or the head or tail of a diary with no
neighbour at all. **Nothing is imputed until that table exists.**

**Still true: nothing has been serialised.** `corpus.jsonl` does not exist. D-S3-4 and D-S3-5 block
its emission, because both change what a tuple can contain.

### 2026-08-17 (night) — 🔴 **D-S3-4 and D-S3-5 CLOSED against the pre-registered rule; D-S3-3's band set; Step 3 unblocked**

The null-structure measurement returned, Speed job **1255285**, COMPLETED exit 0, 00:01:59, against the
full 2,024,068-row table. Transcribed in full in `4thJ_03b_null_structure.md`; the measurement was
read-only and imputed nothing.

**The rule was written before the numbers existed** and is quoted here as it was pre-registered in
`Prompts/4thJ_employee_step3_nulls_2026-08-17.md`:

> Imputation is adopted only if it covers **≥ 99 %** of that field's null episodes under the strict
> rule — `interior_agree` with run length ≤ 2. Otherwise the explicit class is used alone, for 100 %
> of them.

**The measurement, against that rule:**

| field | imputable under the strict rule | share of null episodes | residual | threshold |
|---|---:|---:|---:|---|
| `loc_class` | 4,280 | **17.26 %** | 20,520 | ≥ 99 % |
| `cop_*` | 19,882 | **29.04 %** | 48,582 | ≥ 99 % |

🔴 **Neither field is close, and the failure is not marginal — it is a factor of three to five.** The
rule fires as written and the imputation branch is **not available**. It is worth recording *why* it
failed, because the reason is stronger than the arithmetic: **`interior_disagree` is the single largest
bucket for both fields** — 62 % of null `loc_class` episodes and 38 % of null `cop_*` episodes sit
between two known neighbours that **carry different values**. The neighbours do not agree, so there is
nothing to carry across. Edge cases (`whole_diary`, `head`, `tail`) account for only 12–15 %. The
missingness is not a scatter of short gaps in otherwise-constant stretches; **it lands precisely where
the location or the company is changing**, which is the one place a neighbour cannot speak for it.

**D-S3-4 — CLOSED. Null `LOC` becomes an explicit fifth class, `unknown`.** The alphabet of the `LOC`
field is now the four `crosswalk_location.csv` `target_class` strings plus one:

```
at_home | other_place | private_transport | public_transport | unknown
```

Applied to **24,800 episodes in 8,873 diaries** — 0 in ES, 8,007 in IT, 16,793 in UK. 🔴 **Null `LOC`
is NOT UK-only**, which every earlier note in this document implied by omission; Italy carries a third
of it. That matters, because a code present in two countries out of three is far less of a country
marker than one present in a single country.

**D-S3-5 — CLOSED. Null `COP` becomes an explicit out-of-range code, `64`.** The `COP` field is a
single decimal integer with no leading zeros (D-S3-1); its range widens from **0-63** to **0-64**,
where **64 is not a bit pattern at all** — it is one greater than the largest legal one, and therefore
cannot collide with any of the 64 real co-presence combinations. Applied to **68,464 episodes in 9,298
diaries, all UK.**

* 🔴 **This is the repair of a real leak, not an accounting nicety.** Those 68,464 episodes were being
  written as `0`, which is indistinguishable from a genuine *"alone: no, partner: no, children: no,
  parent: no, other household: no, other persons: no"*. Being UK-only, a spurious `0` is a **UK
  fingerprint the model could learn as a UK trait** — D-S2-2's leak arriving through the back door,
  and precisely what `G3.8` exists to police. `64` says "not collected" out loud instead.
* Token cost was **not separately measured** and is not expected to need measuring: `64` is a
  two-character decimal in a field whose measured 0-63 candidate already carries two-character values
  on 54 of its 64 codes. Recorded as an assumption, not a measurement.

**Why an explicit class rather than a partial imputation, restated so it is not re-litigated later.**
Any residual still needs the explicit class, so a partial imputation ships **two** mechanisms where
one would do, and the model must learn both. The explicit class ships one mechanism and **never invents
a value that was not observed**. A hybrid is the worst of the three outcomes. At 17 % and 29 % coverage
the question does not even reach that argument, but the argument is why 99 % was the bar rather than a
majority.

**One observation the measurement surfaced and this decision does NOT act on.** Part 3 shows the null
rate is elevated within particular activity codes — `cop_*` on `act` 999 at 32.5 % of its own rows,
`loc_class` on 972 and 900 at 12 % and 7.5 %, against a 1-4 % baseline — while no single code dominates
by share. 🔴 **If those are travel codes, the location is recoverable from the activity rather than from
the neighbours, which is a different and better mechanism than imputation and is untouched by this
decision.** No activity-code label mapping was available to the measurement, so **whether they are
travel codes is unverified**. It is recorded as an open lead, not a plan, and nothing in Step 3 depends
on it.

**D-S3-3 — the new `G3.5` band, set.** Per the author's ruling the band is re-based, and per the same
ruling it must be **a context budget and not a curve fit**. The band is therefore anchored on the
training sequence length, which is the only thing that can actually truncate a record:

| | old | new | where the number comes from |
|---|---:|---:|---|
| median | ≤ 220 | **≤ 300** | reporting threshold, measured 238.0 plus declared headroom |
| p99 | ≤ 400 | **≤ 700** | reporting threshold, measured 580.0 plus declared headroom |
| max | *(none)* | **≤ 1024** | 🔴 **the binding one** — half the 2048-token packing window (`RL05`) |

* **The binding threshold is `max ≤ 1024`, and it is a budget, not a fit.** `RL05` packs training
  sequences to 2048 tokens; a record longer than the window is truncated, silently, and a truncated
  diary is a corrupted one. 1024 is that window with a factor-of-two margin, so that no record can be
  truncated and at least two records can share a packed sequence. The measured max is 751.
* **The median and p99 are reporting thresholds with declared headroom of roughly 26 % and 21 %.** The
  headroom exists for one stated reason: **the `unknown` and `64` codes decided above are not in any
  measured distribution** — the 238.0 / 580.0 / 751 figures come from job 1255237, which predates both.
  The headroom is the allowance for them, declared in advance rather than granted afterwards.
* 🔴 **If the corpus lands above these, the band has failed and the answer is not to move it again.**
  This threshold has now been moved once, on the record, for a stated reason. A second move would be
  gate-shopping, and the two are only distinguishable by whether the reason was written down first.

### 2026-08-17 (night, later) — three spec gaps the build hit, ruled on

The Task B employee stopped on three things this document had never decided and said so rather than
coding around them. All three are manager rulings, taken on the spot, and none of them is a threshold.

**D-S3-6 — the age band is serialised VERBATIM, and `V3.c`'s alphabet widens to admit `-` and `+`.**
`strat_age_band`'s frozen values are `11-14, 15-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+` (D-S2-19),
and the hyphen and plus are the only characters in the whole record outside `[a-z0-9_,;|]`. The
employee's own solution was a closed two-way lookup — `11-14 → 11_14`, `75+ → 75plus` — which it
flagged rather than shipping silently. 🔴 **It is refused, and the reason is not aesthetic.** A
transliteration is a mapping the encoder authors and the decoder must invert, and **an encoder and a
decoder that agree with each other about a wrong mapping round-trip perfectly and mean something
else** — the exact defect class `G3.14 (b)` and the bit-order perturbation exist for, reintroduced
voluntarily in a field where no gate is watching for it. The band labels are frozen upstream; shipping
them unchanged means there is no mapping to get wrong. Widening the alphabet by two characters costs
nothing and removes a failure class. `V3.c` is amended; **it is not widened again for anything else.**

**D-S3-7 — the held-out split is 90/10 by respondent, seed 42.** Neither fraction nor seed was
specified anywhere. 90/10 matches the project's existing practice and 10 % of 73,254 diaries is ~7,300
records, ample for the ordinary held-out set. 🔴 **This is not the LOCO fold** — folds are Step 4's, and
the two must never be conflated.

**D-S3-8 — delimiters: `|` between prefix and body, comma within the prefix.** As the employee built
it. A parser splits on `|` first, so the comma is unambiguous despite the tuple also using commas.

**Noted, not a defect:** `unknown` now appears as a value in three places — `strat_econ_status`,
`strat_hh_type` and, after D-S3-4, `LOC`. The positions are fixed so no parser can confuse them, and
the token means the same thing in all three: **not recorded.** That consistency is worth keeping rather
than renaming one of them.

🔴 **One correction to D-S3-3's arithmetic, and it does not change the band.** The employee pointed out
that the 238.0 / 580.0 / 751 figures were measured on **bare episode chains, with no prefix and no
`<eor>`**, while a real record carries both — roughly 20 to 30 tokens more. The headroom declared in
D-S3-3 was declared for the `unknown` and `64` codes; **it must absorb the prefix as well.** It does:
median ~263 against ≤ 300, p99 ~605 against ≤ 700, max ~776 against ≤ 1024. The band stands, but the
median's spare room is now roughly 12 %, not 26 %, **and it is recorded here rather than discovered
when `G3.5` fires.** The build reports full-record numbers; those are the ones `G3.5` scores.

### 2026-08-17 (night, later still) — 🔴 **D-S3-9 OPENED: `act` is null on 5,248 diaries, and Step 3 is blocked again**

The first build ran, Speed job **1255349**, and **refused to emit the corpus**:

```
diaries OK: 68006, diaries FAILED: 5248
  ('es', '00005', '00005_01', '6'): EncodeError: act is null
FATAL: round-trip is NOT 100% (5248/73254 diaries failed) -- corpus NOT emitted.
```

🔴 **The encoder was right to stop, and the run is a success in the only sense that matters here.** It
was told round-trip must be exact on 100 % of the corpus and it refused to ship 92.8 % of one. The
alternative — emitting what encoded and reporting a rate — is how a partial corpus becomes the corpus.

**Loader accounting was clean in the same run**, and this is what makes the finding trustworthy:
2,024,068 rows and 73,254 diaries read, **0 dropped**, matching the pre-registered per-country totals
exactly. `V3.i` did its job on its first outing. **The nulls are in the table, not in the reading of
it**, which is the distinction the four loader-level perturbations were written for.

**Why this is not simply a fifth instance of D-S3-4.** `loc_class`, `cop_*` and `act2` are
**conditioning** fields. 🔴 **`act` is the generation target** — the sequence of activities *is* the
product of this pipeline. An explicit `unknown` activity code would teach the model that "unknown" is a
legitimate thing to emit, and every schedule it generates could then contain hours the model cannot
name. Dropping the affected diaries instead costs **7.2 % of the corpus** and changes the population.
Both are real costs, neither is obviously smaller, and that is the author's call.

🔴 **But it may not be a Step 3 question at all, and that is measured first.** `act` is a harmonised
target code produced by a **Step 2 crosswalk** from a raw source code. Two different worlds:

* **World A** — `act_raw` is itself null. The respondent reported nothing. A Step 3 decision.
* **World B** — `act_raw` carries a value and the crosswalk could not map it. 🔴 **That is a Step 2
  coverage hole, Step 2 reopens, and Step 3 does not encode around it.** Burying a mapping defect
  inside the model's *target* vocabulary would make it permanent and put every downstream number on top
  of it.

**Pre-registered before the numbers exist**, in
`Prompts/4thJ_employee_step3_null_act_2026-08-17.md`: *if any country shows a non-zero
`raw_present_unmapped` count, D-S3-9 is not a Step 3 decision — Step 2 reopens. If it is zero, the
author chooses between an explicit code and dropping the diaries.* The measurement also checks whether
`000`, `998` and `999` are free as 3-digit strings, **because `999` was pre-registered as an
out-of-list sentinel in Step 1 and turned out to be a real INE code** — a sentinel that is secretly
valid tests nothing.

**Nothing is encoded and no corpus exists.** `corpus.jsonl` was not emitted and must not be until
D-S3-9 closes.

### 2026-08-17 (night, close) — 🔴 **D-S3-9 CLOSED. The rule fired on the wrong question, and the correction matters more than the answer**

Speed job **1255401**, COMPLETED exit 0, 00:00:23. Transcribed in `4thJ_03c_null_act.md`.

**Part 1 confirmed the extent and reconciled it to the failed build**: 8,709 rows in 5,248 diaries —
**ES 3,786 / IT 333 / UK 4,590**, or **0.848 % / 0.033 % / 0.809 %** of each country's episodes,
**0.430 %** overall. The 5,248 matches job 1255349's failing-diary count exactly, and all six
per-country row and diary totals match the pre-registered numbers.

**Part 2 returned a clean and unexpected result: World A is EMPTY.** Not one null `act` has a null
`act_raw`. **All 8,709 are `raw_present_unmapped`**, and they come from just **eight distinct source
codes**: ES `900` (3,308) and `399` (478); IT `997` (176) and `90` (157); UK `9000` (2,706), `9940`
(1,670), `9980` (157) and `9999` (57).

🔴 **My pre-registered rule would have fired, and it would have been wrong.** It said a non-zero
`raw_present_unmapped` count means a Step 2 coverage hole and Step 2 reopens. It is a **coverage hole
by decision, not by omission**: `4thJ_02_harmonisation.md` names **these same eight codes** and records
that they are *"almost all diary-quality markers — 'illegible activity', 'queryable', 'a phrase that
does not describe an activity' — rather than activities, which is the right thing for a target
vocabulary of real activities not to contain."* They are registered in `crosswalk_unmapped.md`, the
register `G2.1` reads, and *"the null is readable precisely because the code is listed there."*
**Step 2 does not reopen. It already answered this and wrote the answer down.**

**The lesson is about the rule, not the codes.** The rule split the world on a *mechanical* test —
"does `act_raw` carry a value?" — and inferred intent from it. **A deliberate refusal and an accidental
omission look identical to that test.** There was a third world and the rule had no room for it. The
measurement was still worth running: it produced the eight codes, and the eight codes are what made the
Step 2 entry findable. 🔴 **What should have happened is a search of Step 2's own documentation before
a rule was written about Step 2's behaviour** — the same discipline this project applies to gates,
applied one level up to itself.

**D-S3-9 — CLOSED by the author, 2026-08-17: null `act` becomes the explicit code `000`.** Same shape
as D-S3-4 and D-S3-5, and the reasoning that decided it was the **country skew of the alternative**:
dropping the 5,248 affected diaries removes **17.0 % of UK diaries, 12.0 % of Spanish and 0.65 % of
Italian** — a country-correlated population difference **manufactured by us**, arriving inside a
leave-one-country-out design, which is exactly where a country-shaped artefact does its damage. It is
the same argument that forced the ES `121` / UK `1310` lunch-break correction in Step 2. The cost paid
instead is that the model can emit `000`, meaning *"the diary entry here was unusable"*; at 0.43 % of
episodes it is learnt as rare.

* 🔴 **`000` was verified free before it was chosen.** Part 5: `000` is **not** a legal target code in
  `crosswalk_activity.csv` and appears **nowhere** in the `act` column. **`998` and `999` are both
  taken** — each is a legal target code *and* already present in the data, so either would have
  repeated the `999` failure class exactly: Step 1 pre-registered `999` as an out-of-list perturbation
  for Spain, `999` turned out to be a real INE code, and the perturbation tested nothing.
* **Durations are untouched**, so `G3.2`'s `sum(DUR) == 1440` still closes. Nothing is dropped and no
  diary changes length. Total minutes affected: **ES 0.304 %, IT 0.018 %, UK 0.245 %**; the median
  affected diary loses **10 to 40 minutes**, though the worst loses 850.
* **1,301 episodes carry a present `act2` with a null `act`** — a secondary activity recorded where the
  primary was unusable. Under `000` they serialise as `DUR,000,<act2>,LOC,COP`, which is odd-looking
  and honest. Recorded so nobody later reads it as an encoder bug.
* 🔴 **One thing the rebuild must check and report, because it can invalidate the choice:** `G3.4`
  requires **100 % of 3-digit `ACT` codes to be exactly one token**. `000` has never been tokenised.
  **If it costs two tokens, `G3.4` fails and the code must change** — to another verified-free 3-digit
  string, not by relaxing `G3.4`.

**Overlap, for the record** (Part 4): of the 5,248 null-`act` diaries, **2,009** also have a null
`loc_class` and **2,001** a null `cop_*`. Row-level: 2,615 rows null in both `act` and `loc_class`,
1,651 in both `act` and `cop_*`.

**Step 3's record format is frozen** — the block below stands regardless of how D-S3-9 resolves, since
neither branch changes the tuple's shape:

```
<6-field prefix> | DUR,ACT,ACT2,LOC,COP  …  <eor>     (was 8 before D-S3-11)
```

with `ACT2` empty when absent, `LOC` drawn from five classes, and `COP` an integer in 0-64. Nothing has
been serialised yet; `corpus.jsonl` may now be emitted.

---

### 2026-08-17 (night, corpus emitted) — the corpus exists, and `G3.5`'s binding clause failed

Speed job **1255620** (COMPLETED, exit `0:0`, 08:18) applied D-S3-9 (`000`) and D-S3-6 (verbatim age
bands) and emitted `4J_step3_corpus.jsonl`, **73,254 records**. Output:
`/speed-scratch/o_iseri/4J_step3_build_1255620.out`.

**Everything the build was asked to prove, it proved.**

* Loader accounting clean a second time — 446,547 / 1,010,140 / 567,381 rows and 19,140 / 38,260 /
  15,854 diaries, **0 dropped**.
* **Round-trip 100 % exact on 73,254 / 73,254 diaries.** The 5,248 that failed in job 1255349 now pass.
* Explicit-null reconciliation matches the pre-registered numbers **exactly**, all nine cells:
  `unknown` loc 0 / 8,007 / 16,793; `COP == 64` 0 / 0 / 68,464; **`ACT == 000` 3,786 / 333 / 4,590.**
* 🔴 **`000` tokenises to exactly 1 token**, so `G3.4` holds and D-S3-9 needs no fallback code. All
  **159** distinct `ACT` codes in the corpus are 1 token; `len(tokenizer) = 100278`, no tokens added
  (`RL05`). `tokenize(detokenize(ids)) == ids` on 73,254 / 73,254, and every record ends `<eor>`.
* Split integrity: 58,801 train and 6,533 heldout respondents, **intersection 0**.

**🔴 And the band failed, at the one clause declared binding.**

| | band | measured | |
|---|---:|---:|---|
| median | ≤ 300 | **275.0** | within |
| p99 | ≤ 700 | **647.0** | within |
| max | **≤ 1024** | **1191** | 🔴 **FAIL — 4 records of 73,254 exceed it** |

Per country: ES max 755, IT max 1024 — *exactly at the boundary, not over* — **UK max 1191**. The four
over-length records are the UK's, which is the same country that carries every `COP == 64` and the
larger `unknown`-location share, and the UK's median (354) and p99 (755) are the highest of the three;
its p99 alone is over the p99 band, though the band is scored on the pooled corpus where it passes.

**This entry does not move the threshold, and the next one must not either.** The band was moved once
already, on the record, and this document wrote down in advance what happens if the corpus lands above
it: *"the band has failed and the answer is not to move it again … A second move would be
gate-shopping, and the two are only distinguishable by whether the reason was written down first."*
That sentence was written before this number existed, and it binds now.

**Why it failed — my arithmetic, not the corpus.** The 1024 was set against job 1255237's measured max
of **751**, which was the *bare episode-tuple* form: no prefix, no `<eor>`. I corrected that
mid-course and estimated the real max at **~776**. It is 1191. The estimate was wrong because it
assumed the per-episode cost stayed near 11 tokens while the three new explicit codes — `unknown`,
`64` and `000` — were being added to the very records that were already longest. The headroom was
declared for exactly those codes; **it was declared too small.**

**🔴 What is and is not actually at risk.** The clause exists for one reason: `RL05` packs training
sequences to **2048** tokens, and a record longer than the window is silently truncated, which
corrupts a diary. **At 1191 no record is truncated** — the safety property the clause protects is
intact with 857 tokens to spare. What fails is the **factor-of-two margin**, whose stated purpose is
that at least two records can share a packed sequence. That is a packing-efficiency property, not a
correctness one. **The distinction matters and it does not resolve the decision**, because a declared
threshold that is missed and then reasoned away is a moved threshold with extra steps.

**Open as D-S3-10, for the author.** The corpus is emitted and sound; `G3.5` reports FAIL on its max
clause and the gate battery will re-report it. What the author decides is whether Step 3 ships with
that FAIL standing on the record, or whether the four records are handled some other way. **No repair
is applied here, and the corpus is not rebuilt on my own authority.**

**Tokenizer premise, restated so it is not lost.** The build tokenised with
`allenai/OLMo-2-0425-1B` as a stand-in for `allenai/Olmo-3-1025-7B`, on the premise of an identical
dolma2 BPE vocabulary and because it is far smaller to download. `len(tokenizer) = 100278` is
consistent with that premise. 🔴 **The premise was assumed, not re-derived**, and every token number in
this entry — including the 1191 — rests on it.

### 2026-08-17 (night, close) — D-S3-10 CLOSED by the author: the band goes to 1200

Put to the author with the three options and their costs — ship with the FAIL standing, drop the four
diaries, or move the threshold — **the author chose to raise `max` from 1024 to 1200.**

🔴 **This overrides the refusal written two entries above, and the override is the author's, not
mine.** Both sentences stand in this document, in that order, and neither is edited out. That is the
whole point of having written the refusal down first: a threshold moved against a rule that exists and
is visible is a different object from a threshold moved against no rule at all. Anyone reading this
file can see the number it was, the number it is, who moved it and what was known at the time.

**What was declined and why it matters.** Dropping the four diaries would have turned every gate green
at a cost of 0.005 % of the corpus. It was not taken, and it should not be: deleting the records that
fail a check is the same act as moving the check, and it would have felled the loader-drop clause
(`V3.i`, zero rows and zero diaries dropped) instead — trading a visible red mark for a hidden one.

**The three consequences, recorded now.**

1. **`G3.5`'s max is a fit, not a budget.** 1200 against an observed 1191 is **nine tokens of
   headroom**. The safety property survives — nothing is near `RL05`'s 2048-token window, so no record
   is silently truncated — but the factor-of-two margin is gone. 🔴 **A fourth country, a wider prefix,
   an extra field, or a tokenizer that is not the dolma2 vocabulary will breach this clause**, and it
   has no reserve left to absorb any of them.
2. **The perturbation was re-checked before the battery runs, not after.** The last move disarmed the
   `G3.5` row silently. Against 1200, the 150-episode injected diary is roughly 1,650-1,950 tokens plus
   prefix and `<eor>` — it still fires, with about 40 % margin instead of 60 %. It is **not** raised
   again; a perturbation that fires works, and inflating it would only mask the next move.
3. **The paper must state this.** `G3.5` is now the one threshold in Step 3 that was set after seeing
   its own data, and it was set twice. It is not enough for that to be true in this file; it belongs in
   the validation section of the write-up in the same plain terms.

**Step 3's substantive work is complete.** The corpus stands at `/speed-scratch/o_iseri/4J_step3_corpus.jsonl`,
73,254 records, 100 % exact round-trip, all nine explicit-code reconciliations matching, `000` at one
token, no added vocabulary. What remains is the independent gate battery — sixteen gates, twenty-one
perturbations, `V3.a`-`V3.i` — which has not run and whose result is not assumed here.

---

### 2026-08-17 (night, later) — Definition-of-Done item 6 is IN FLIGHT, not met. Speed job `1256012`.

The independent sixteen-gate / twenty-one-perturbation battery was submitted and is **RUNNING**.
Details, assumptions and the pre-registered contradiction it carries are in
`4thJ_03_serialisation_val.md`'s entry of the same date; execution state for a cold agent is in
`Step3_docs/impl/2026-08-17_step3-gates.md`.

🔴 **Step 3 remains NOT DONE.** Every number in this document is still the build's own self-report.
When `1256012` reports, item 6 is ticked from *its* output or not at all — and if it disagrees with a
figure written here, **the battery is the witness and this document is the claim.**

**Housekeeping, same night:** all six completed employee prompts moved to `Prompts/previous/`; the
Step 1 and Step 2 Progress Log fragments were merged into their working docs under manager's notes.
`outputs_step3/proglog_step3_gates.md` does not exist yet — the battery writes it. There is no
`proglog_step3_build.md`; the build's Progress Log entries were written directly into this file, which
is why they are here and not in `outputs_step3/`.

---

### 2026-08-18 — 🟢 **STEP 3 IS DONE. The battery reported twice, this document did not survive the first run, and it did survive the second.**

**Definition-of-Done item 6 is now ticked from the battery's own output**, which is the only way it
was ever allowed to be ticked. The record, in order:

* **Job `1256012`** (eight-field prefix) — `COMPLETED`, `0:0`, 03:07:55. **Two gates FAILed at
  baseline, the coverage clause FAILed, four `G3.1` cells fell that `4thJ_03_serialisation_val.md`
  had pre-registered as clean, and a fifth defect was found off-run.** Four decisions were raised.
  🔴 **This run's numbers are superseded for every prefix-dependent gate** — the prefix itself
  changed underneath them — but the run is not superseded: it is the run that found the defects, and
  its 25 reports plus its `.out` are kept whole in `outputs_step3/gates_out/`.
* **D-S3-11, D-S3-12, D-S3-13 ruled by the author the same night**, applied to
  `encoder.py`, `decoder.py`, `4thJ_step3_build.py` and `4thJ_gates_step3.py`, and verified 10/10 on
  a synthetic three-country fixture **before** the cluster was touched. A fixture is not the corpus,
  and it was not treated as one.
* **Job `1257441`** (six-field rebuild) — `COMPLETED`, `0:0`, 02:23:19.
  **19 of 20 gates PASS at baseline, all 19 were seen falling,
  `Gates that PASS at baseline and were NEVER felled by any perturbation: []`,
  `COVERAGE CLAUSE VERDICT: PASS`, and 21 of 21 "must fail" cells fired.** Reports and `.out` in
  `outputs_step3/gates_out_v2/`.
* **D-S3-14 ruled (a)** — the one remaining baseline FAIL stays. Details below.

**The corpus this document describes was rebuilt, and every figure above it was re-established rather
than carried.** 2,024,068 rows read (es 446,547 · it 1,010,140 · uk 567,381), **0 rows and 0 diaries
dropped**, **73,254 records** written, encode→decode 73,254 / 73,254 exact, `<eor>` on 73,254 /
73,254, 0 of 159 `ACT` codes failing the one-token assertion. Prefix vocabularies as emitted:
country 3, age band 8, sex 2, household type 6 (including `unknown`), economic status 7 (including
`unknown`), day type 3. The eight-field corpus is preserved beside it as
`4J_step3_corpus_1255620_8field.jsonl`; nothing was overwritten.

🔴 **Each of the three rulings was demonstrated on the real corpus, not asserted.** `D-S3-11`:
`G3.10` now PASSes **with its regex untouched**, having FAILed before — one field removed, two red
gates resolved, which is what confirms the diagnosis rather than the patch. `D-S3-12`: `G3.9` reads
ES PASS, IT PASS, UK FAIL, and its new perturbation moves the **Italy** fold PASS → FAIL on 38,260
diaries. `D-S3-13`: `G3.3` goes 73,254 / 73,254 → **0 / 73,254** under the tokenizer swap, while the
retired idempotency count sits beside it at 73,254 / 73,254 under **both** tokenizers — which is
precisely the tautology the re-specification was meant to remove, still visible, still reported, and
no longer scored.

### 🔴 D-S3-14 — ruled (a). One gate is red on purpose, and Step 3 closes with it red.

The author's instruction was *"(b) if possible, otherwise (a)"*. **(b) — folding
`strat_hh_type = unknown` into an existing category — was checked against the sources and is not
available.** Three reasons, each read off a document rather than argued: `crosswalk_strata.csv` maps
the value from a **blank `dhhtype`**, and the Step 1 codebook measures it at **411 blank of 11,421 UK
persons, 3.6 %** — `dhhtype` being UKDA's own *derived*, household-level variable, a blank means
**UKDA's derivation declined to classify that household**, so folding it in asserts a household type
the data provider itself would not assert. Step 1 documents alternative fields for *economic status*
only and **none** for household type, and re-deriving one from the household grid is the "invented
proxy" that note rules out. And **D-S2-19 already named this exact cell in advance** — ES 0.0 % /
IT 0.0 % / UK 3.6 % — ruling that the only repairs available on a prevalence basis are imputation or
dropping rows, with the sanctioned repair being **to coarsen the classification, never to relax the
count**; coarsening cannot reach `unknown`.

**No row was imputed, no row was dropped, and `G3.9` was not touched** — not re-pointed, not relaxed,
not exempted. **The limitation at its true size: 551 diaries of the UK's 15,854 — 3.5 % of one fold,
and only that fold.** 🔴 **And the literal symbol is not unseen by the model:** `unknown` also occurs
in `strat_econ_status`, which **Italy emits**, so under UK-held-out the ES + IT training pair does put
that token in front of the model inside the same six-field prefix. **What is novel at test time is
the field position, not the symbol** — materially weaker than "a token never seen", and it must be
written the weaker way. 🔴 **Step 6 now owes a split report:** the UK fold's scores for
`strat_hh_type = unknown` versus the rest, so this is quantified against outcomes rather than
asserted; if that split cannot be produced, it is reported as un-quantified and said to be so.

### What must travel with this result, every time it is quoted

* 🔴 **"19 of 20", never "20 of 20."** The tally is not rounded up because the twentieth gate is red
  by a ruling we made deliberately and can defend.
* 🔴 **`G3.9`'s coverage cross-tab column is uninformative.** Its top-line verdict is FAIL both
  before *and* after its perturbation, so it cannot be reported as "felled" — **only the Italy fold
  was seen moving**, and that is the claim to make.
* 🔴 **The four `G3.1` `UNEXPECTED FALL -- FINDING` lines are deliberate.** `EXPECTED_EFFECT` in
  `4thJ_gates_step3.py` still declares `G3.1` clean under `zero_pad_act4`, `strip_eor_1pct`,
  `zero_pad_cop2` and `spell_unknown_two_ways`, where it demonstrably FAILs. **That table is the
  pre-registration.** Editing it after seeing the result would erase four findings from every future
  report, so it was left alone and the mismatch is carried as a finding instead.
* **`G3.5` was not re-tightened** when the prefix shrank. The band stays median ≤ 300 / p99 ≤ 700 /
  max ≤ 1200 as ruled in D-S3-10; the measured max fell 1191 → 1178, so headroom went 9 → 22 tokens.
  A band moved to fit a result it was written to test is not a band.

**One documentation defect found and fixed this session**, recorded because it is the kind that
survives: `4thJ_step3_build.py` still printed the superseded `max<=1024` band and therefore announced
"max EXCEEDS band" for a max of 1178 that is comfortably inside the ruled 1200. **The gate itself used
1200 and PASSed** — this was display text only, in the build's self-report, and no result depended on
it. Fixed in place and the script re-copied to `/speed-scratch/o_iseri/`.

**Merged the same day:** `outputs_step3/proglog_step3_gates.md` was appended verbatim to
`4thJ_03_serialisation_val.md` under a manager's note, completing the five-fragment merge named in
`Prompts/RESUME.md`. There is no `proglog_step3_build.md` and there never was — the build's entries
were written straight into this file.
