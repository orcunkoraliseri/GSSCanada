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
| **G3.8** Prefix honesty | Conditioning on a flag a country never recorded | No record asserts a co-presence flag that `copresence_availability.md` marks "not recorded" for that country | **derived from Step 2** |
| **G3.9** Constant-field invariance | `MODE` or `SCHEME` varying, which would mean the corpus mixes instruments | Exactly **one** distinct value of each across the whole corpus | **derived from decision 6** |
| **G3.10** No `YEAR` token | A temporal axis creeping back in | The string `YEAR`, and any four-digit year, appears **zero** times in any prefix | **derived from author decision 3** |
| **G3.11** Split integrity | A respondent's two diary days straddling train and held-out | Intersection of respondent IDs across splits: **0** | **project-chosen**, and it is the leakage that would inflate every downstream number |
| **G3.12** Vocabulary containment | A silent vocabulary extension | The set of token IDs used by the corpus is a subset of the base tokenizer's vocabulary, and `len(tokenizer)` equals the published base value | **derived from the no-added-tokens decision** |

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

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate that the format is a *good* format. `RL07` measured that; this step checks
  we implemented what was decided.
* It does **not** check secondary activities, because the tuple does not carry them. If a later step
  needs them, Step 2 is where they were dropped and Step 3 is where that became irreversible.
* It does **not** test the grammar. Whether a generated string is legal is Step 7; whether a *real*
  record serialises legally is here, and the two are different questions with different failure modes.
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
