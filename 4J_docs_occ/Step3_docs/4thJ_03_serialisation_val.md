# Step 3 — Serialisation and tokenisation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_03_serialisation.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That the text handed to the model **is** the harmonised data, losslessly, and that the tokenizer sees
it the way we measured it would.

This step is the cheapest place in the pipeline to catch an encoding defect and the most expensive
place to miss one: every downstream number is computed on this text.

---

## GATES

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G3.1** Round-trip exactness | Any lossy encoding | `decode(encode(d)) == d` **field by field**, 100 % of the corpus. Not string equality — a comparison of decoded structures | **project-chosen**, and exactness is not a tolerance |
| **G3.2** Duration closure in the serialised text | An encoder that drops or merges an episode | Parsing `corpus.jsonl` back out, `sum(DUR) == 1440` for 100 % of records | **derived from the instrument** |
| **G3.3** Tokenizer round-trip | A vocabulary mismatch that silently mangles codes | `tokenize(detokenize(ids)) == ids` on **100 %** of the corpus, not a 1,000-record sample | `RL05` failure mode 4 |
| **G3.4** One-token codes | The tokenizer advantage we chose the backbone for failing to materialise | **100 %** of 3-digit `ACT` codes encode to exactly 1 token | **measured** — Speed jobs 1234177, 1234199 |
| **G3.5** Diary token budget | Records that will not pack | Median diary ≤ **220** tokens, p99 ≤ **400**. 🔴 Report the **distribution**, and report which end any exceedance sits at | **project-chosen**, anchored on the measured 200-token benchmark |
| **G3.6** Terminator presence | A model that never stops generating | **100 %** of records end with `<eor>` | `RL05` failure mode 7 |
| **G3.7** Prefix completeness | A stratum silently missing from the conditioning | Every record carries all nine prefix fields; count of records with a missing or empty field: **0** | **project-chosen** |
| **G3.8** Prefix honesty | Conditioning on a flag a country never recorded | No record asserts a co-presence flag that `copresence_availability.md` marks "not recorded" for that country. 🔴 **The flag set is SIX after D-S2-8, not five**, and the sixth (`cop_parent`) is the one every country records — so if it is ever marked "not recorded" for a country, that is a crosswalk bug, not a data fact | **derived from Step 2** |
| **G3.9** Constant-field invariance | `MODE` or `SCHEME` varying, which would mean the corpus mixes instruments | Exactly **one** distinct value of each across the whole corpus | **derived from decision 6** |
| **G3.10** No `YEAR` token | A temporal axis creeping back in | The string `YEAR`, and any four-digit year, appears **zero** times in any prefix | **derived from author decision 3** |
| **G3.11** Split integrity | A respondent's two diary days straddling train and held-out | Intersection of respondent IDs across splits: **0** | **project-chosen**, and it is the leakage that would inflate every downstream number |
| **G3.12** Vocabulary containment | A silent vocabulary extension | The set of token IDs used by the corpus is a subset of the base tokenizer's vocabulary, and `len(tokenizer)` equals the published base value | **derived from the no-added-tokens decision** |
| **G3.14** `COP` packing integrity — **two sub-clauses, M-7 attribution applies** | (a) a `COP` field that is out of range or has two spellings; (b) 🔴 **an encoder and decoder that agree with each other and disagree with the crosswalk about which bit is which flag** | **(a)** every serialised `COP` parses as an integer in **0-63** written with **no leading zeros** — a corpus carrying both `7` and `07` holds two spellings of one value and the measured 8-token cost no longer holds. Violations: **0**. **(b)** per country and per flag, the count of episodes with that bit set — decoded using the `bit_position` column of `crosswalk_copresence.csv` — equals the count of that flag set in `harmonised.parquet`. Discrepancy: **0** episodes | **(a)** derived from D-S3-1, the measured packing, job 1252633. **(b)** 🔴 **derived from Step 2's crosswalk, and the gate MUST read the bit order from that file — never import it from `encoder.py` or `decoder.py`.** A gate that takes the order from the encoder is auditing the encoder against itself |

---

## EVERY GATE MUST BE SEEN FAILING

Each perturbation applies to a copy and must break **exactly one** gate.

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Drop `LOC` from the decoder's parse | G3.1 | G3.2 |
| Merge two adjacent episodes, summing their durations | G3.2 must stay **clean** (the sum is preserved) and **G3.1** must fail | 🔴 *This is the case that shows why G3.2 alone is insufficient* |
| Swap in a tokenizer with a different vocabulary | G3.3, G3.4, G3.12 — a **coverage** case, scored as such | — |
| Zero-pad codes to 4 digits (`0311`) | G3.4 | G3.1 |
| Inject one 60-episode diary | G3.5 at the **upper** end, and the report must say *upper* | G3.2 |
| Strip `<eor>` from 1 % of records | G3.6 | G3.1 |
| Blank one prefix field on 10 records | G3.7 | G3.8 |
| Assert "with partner" on a country that does not record it | G3.8 | G3.7 |
| Set `MODE` to a second value on one record | G3.9 | all others |
| Add `YEAR=2013` to the prefix | G3.10 | G3.7 — *the record is still complete, which is the point* |
| Split by diary instead of by respondent | G3.11 | all others |
| Call `tokenizer.add_tokens(["<act311>"])` | G3.12 | G3.1 |
| Zero-pad `COP` to two digits (`07` for `7`) | G3.14 **(a)** | G3.1 — *it still round-trips, which is the point*; G3.4, which is about `ACT` |
| 🔴 **Reverse the bit order in the encoder AND the decoder together, leaving `crosswalk_copresence.csv` untouched** | G3.14 **(b)** | **G3.1 must stay clean** — encoder and decoder agree perfectly and mean something else. *This is the symmetric-defect class, and it is why (b) reads the order from the crosswalk* |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.** Note that the tokenizer-swap row is deliberately a multi-gate perturbation and is scored for
coverage only — **it cannot attribute**, and a perturbation that moves three gates tells you nothing
about which one caught the defect.

---

## 🔴 THE ONE CHECK THAT COMES THROUGH A PATH THE DEFECT CANNOT REACH

G3.1 to G3.12 all read the encoder's own output through the decoder we wrote. **If encoder and
decoder share a wrong assumption, every gate above passes.** Internal consistency is not verification.

**G3.13 — independent re-derivation.** Take 500 random serialised records, parse them with a
**separately written, minimal parser that does not import anything from `encoder.py` or
`decoder.py`**, and reconstruct the per-diary Level-1 time budget. Compare against the same quantity
computed directly from `harmonised.parquet`.

* Threshold: agreement to **< 1 minute per diary per category**.
* 🔴 This is the only gate in Step 3 whose two sides do not share an ancestor, and it is therefore the
  only one that can catch a symmetric encoder/decoder error. **Do not let it be refactored to import
  the shared module for convenience** — that would silently reduce it to G3.1.

🔴 **Amended 2026-08-16: G3.14 sub-clause (b) joins it, on the same principle and for one specific
defect.** Its reference is `crosswalk_copresence.csv`, which the encoder does not author, so an
encoder and decoder that share a wrong bit order cannot hide from it. **The same refactoring ban
applies verbatim**: the moment G3.14 takes the bit order from `encoder.py` for convenience, it stops
being an independent check and becomes a restatement of G3.1. Two gates now depend on not doing that.

---

## VACUITY GUARDS

* **V3.a** — the runner FAILs if it read fewer records than `token_stats.md` says exist. A battery
  that scans a subset it chose itself is the same failure as a vacuous gate, one level up.
* **V3.b** — it prints record count, token count, distinct `MODE`/`SCHEME` values and vocabulary size
  **before** any verdict.
* **V3.c** — any character in the serialised corpus that is not in the declared alphabet (digits,
  comma, semicolon, the prefix delimiters, `<eor>`) is **printed and refused**.
* **V3.d** — G3.5 must report which **end** it fails at. A band gate quoted only as "how many are
  inside" hides an inversion in which the failing end has flipped.
* **V3.e** — G3.14 **FAILs, rather than skipping**, if `crosswalk_copresence.csv` is missing, has no
  `bit_position` column, carries fewer than **six** flag rows, or its bit positions are not exactly
  `{0,1,2,3,4,5}`. 🔴 A gate whose reference file is absent has not passed; it has not run.
* **V3.f** — G3.14 prints the **per-country, per-flag prevalence from both sides** — corpus-decoded and
  `harmonised.parquet` — **before** any verdict. Two flags with equal prevalence make a swap between
  them invisible to sub-clause (b), and only the printed table shows whether the gate had the
  resolution to see anything at all.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate that the format is a *good* format. `RL07` measured that; this step checks
  we implemented what was decided.
* It does **not** check secondary activities, because the tuple does not carry them. If a later step
  needs them, Step 2 is where they were dropped and Step 3 is where that became irreversible.
  🔴 **Amended 2026-08-16: that exclusion is no longer settled.** 3.2-bis's leak argument — the
  stronger of its two — is retired now that all three countries are known to record a secondary
  activity, so only the token-cost argument stands and it is a measurement. **If the measurement puts
  `ACT2` into the tuple, it must happen before `corpus.jsonl` is emitted**, and this validation
  document gains the gates for a five-element tuple at that moment. A fifth element added afterwards
  invalidates the corpus, the Step 7 grammar and every trained fold.
* It does **not** test the grammar. Whether a generated string is legal is Step 7; whether a *real*
  record serialises legally is here, and the two are different questions with different failure modes.
* 🔴 It does **not** catch a `COP` bit swap between two flags of **equal prevalence**. G3.14 (b)
  compares per-flag counts, so swapping two flags that happen to be set on the same number of episodes
  is invisible to it. V3.f prints both sides' prevalence precisely so that this blind spot is visible
  in the report rather than assumed away.
* 🔴 It does **not** test whether a packed 0-63 integer is as **learnable** as six positional
  characters. D-S3-1 was decided on token cost, which is what was measured; the model must now recover
  64 arbitrary codes instead of reading six aligned slots, and no gate here can say whether that costs
  accuracy. The packing freezes when `corpus.jsonl` is emitted, so the only place to test it is a
  **Step 4 ablation on a subset, beforehand**.
* 🔴 It does **not** establish that 200 tokens per diary is achieved on **our** data. The 200 figure
  was measured on a representative 25-episode string, not on the corpus. G3.5 is what turns that
  benchmark into a measurement, and if the corpus median lands far above it, the throughput arithmetic
  in Step 4 and Step 7 is built on the wrong number.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Thirteen gates, thirteen perturbations, none run.
* 🔴 G3.13 exists because of a rule this project learned the hard way: **at least one check must come
  through a path the defect cannot reach**, or you have confirmed your parser rather than your
  answer. Every other gate here reads the encoder's output with the decoder we wrote.

### 2026-08-16 — effect of D-S2-7 and D-S2-8. No gate added, and that is the point

Step 2 closed its three heterogeneities today. Two reach this document, and **neither produced a new
gate, because neither is yet a measured quantity.**

* **`G3.8` widened, not relaxed:** the co-presence flag set is **six** after D-S2-8, since all three
  countries record parent co-presence. 🔴 **The sixth flag is the one every country records**, so if
  `copresence_availability.md` ever marks `cop_parent` "not recorded" for a country, that is a
  crosswalk bug and `G3.8` is the gate that will say so.
* 🔴 **No `COP` packing gate is pre-registered, deliberately.** The packing is being measured on Speed
  right now — six flags, so 0-63, five candidate encodings, each measured **in situ** inside a full
  tuple and a full 25-episode diary, **sweeping all 64 values for the worst case.** A threshold written
  before that measurement is a threshold chosen to be passed, which is the failure this project
  spends most of its effort avoiding. **The gate follows the number; the number does not follow the
  gate.**
* **The "does not check secondary activities" exclusion is amended rather than left standing.** Its
  justification was that the tuple cannot carry `ACT2`; that rested on 3.2-bis, whose stronger argument
  — a symbol only Spain could emit — is **retired** now that all three countries are known to record
  one. Only token cost stands, and token cost is a measurement. 🔴 **If it puts `ACT2` in the tuple,
  this document gains the five-element gates at that moment and not later**, because a fifth element
  added after `corpus.jsonl` invalidates the corpus, the Step 7 grammar and every trained fold.

**Still thirteen gates, thirteen perturbations, none run.** Step 3 remains blocked on
`harmonised.parquet`, which is blocked on the Step 1 sixteen-gate round.

### 2026-08-16 (later) — 🔴 **G3.14 pre-registered, AFTER the measurement and not before**

The `COP` packing measurement returned (Speed job 1252633) and D-S3-1 fixed the packing at a **single
decimal integer 0-63**. Only then was a gate written. That order was the point of refusing to
pre-register one this morning, and it is recorded here so the sequence is auditable: **file existed →
packing chosen → threshold written.** A threshold written first is a threshold chosen to be passed.

**`G3.14` has two sub-clauses and M-7 attribution applies to both**, so the report says *which clause*
fell, not merely that the gate did:

* **(a) Range and spelling** — every `COP` parses as an integer in 0-63 with **no leading zeros**.
  `7` and `07` are two spellings of one value, and a corpus carrying both invalidates the measured
  8-token cost that justified the packing. Threshold **0** violations.
* **(b) Bit-order fidelity** — per country and per flag, the count of episodes with that bit set,
  decoded using the `bit_position` column of `crosswalk_copresence.csv`, equals the count in
  `harmonised.parquet`. Threshold **0** episodes.

🔴 **(b) is the second gate in this step whose two sides do not share an ancestor.** The defect it
exists for is an encoder and decoder that agree with *each other* and disagree with the crosswalk
about which bit is `cop_alone`. Such a corpus round-trips through `G3.1` perfectly and means something
else entirely. Its perturbation is written to match: **reverse the bit order in encoder and decoder
together**, and `G3.1` must stay **clean** while only `G3.14` falls. The refactoring ban that protects
`G3.13` now protects this clause too — the moment it imports the order from `encoder.py`, it is
`G3.1` wearing a different name.

**Two vacuity guards came with it, because both failure modes have bitten this project before:**

* **V3.e** — the gate **FAILs** if `crosswalk_copresence.csv` is missing, lacks `bit_position`, has
  fewer than six flags, or its positions are not exactly `{0,...,5}`. A gate whose reference is absent
  has not passed. It has not run.
* **V3.f** — per-country, per-flag prevalence is printed from **both** sides before any verdict, because
  **two flags with equal prevalence make a swap between them invisible to (b)**. Only the printed
  table reveals whether the gate had the resolution to see anything, and that limit is recorded below
  rather than left for someone to discover.

**No existing threshold was moved.** `G3.5`'s median band of **220** is in fact what *rejected* the
six-character binary packing, which measured 225 tokens per diary before a single real record was
serialised. The band did its job at the design stage, which is the earliest and cheapest place a
pre-registered threshold can pay for itself.

**Now fourteen gates and fifteen perturbations, none run.** Step 3 remains blocked on
`harmonised.parquet`, which is blocked on the Step 1 sixteen-gate round.
