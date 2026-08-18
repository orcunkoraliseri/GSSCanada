# Employee task — Step 3: measure `ACT2`, then build the encoder, the decoder and the corpus

**Role: employee.** You execute and you measure. 🔴 **Every design decision in Step 3 is already
taken** — see B0. You do not move a threshold, you do not impute a value, you do not add a token to the
vocabulary, and you do not write or run the gates.

**Governing specs:** `4J_docs_occ/Step3_docs/4thJ_03_serialisation.md` (work items 3.1 to 3.5, and
**3.2-bis** in full) and `4thJ_03_serialisation_val.md`. Read both before anything else.

---

## 🔴 STATUS, 2026-08-17 (night): TASK A IS CLOSED — GO STRAIGHT TO TASK B

The additive round landed. `harmonised.parquet` carries the eleven D-S2-18 / D-S2-19 stratum columns —
**51 columns, 2,024,068 rows** — at
`/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`. If the table you find
has 40 columns, **stop and say so.**

All five Task A rulings are taken. **Read section B0 first**; it lists them and tells you what not to
re-run.

---

## 🔴 CLUSTER RULES — VIOLATING THESE COSTS THE ACCOUNT

* **`sbatch` only.** Never a blocking `srun`, **never bare python on the login node, not even a
  one-liner.** Every job `-t 7-00:00:00`, partition `ps`, CPU only — tokenizer work needs no GPU.
* tcsh login shell: no `2>&1` in ssh commands, no bash `while ... done` loops, **one `sacct` call, not
  a poll loop.**
* 🔴 **Submit through a shipped `.sh` launcher, never a hand-rolled `sbatch --wrap`.** Copy
  `/speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh` and change the job name, the
  `--output` path and the script it calls. **The venv is `ENVDIR=/speed-scratch/o_iseri/envs/4j_tok`**
  — it carries pandas, pyarrow and transformers. `envs/step4` has **no transformers**, and two jobs in
  this exact family died in two seconds against it, having exercised nothing.

## 🔴 NO PARKING — you never wait for a job

Submit with `sbatch`, write the JobID into your implementation doc, and **end your turn** saying "job
N submitted, state written to `<path>`". **No background polls, no sleeps, no no-op command to hold
the turn open, no "waiting for the notification".** The manager watches the queue and spawns a fresh
agent to collect the result. Waiting is the most expensive thing you can do: every wake re-sends your
whole transcript and produces nothing.

**Your state goes to disk as it happens**, in `Step3_docs/impl/2026-08-17_step3-build.md` — create it
first, before any job:

```
# Step 3 build — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step3_build_2026-08-17.md
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per job: JobID · what · state · exit · output path (append-only, failures kept)
## Verified      <- numbers actually read, and where from
## Decisions     <- what this task doc did not decide, and what you assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

This matters more here than anywhere else: **Task A ends in a stop for an author ruling**, and the
agent that resumes into Task B will be a different one. It starts from this file, not from your
transcript. Never read a multi-MB file into context — `wc -l`, `grep -n`, `tail -c`, `head`. Past
roughly 150k tokens, stop, write state, and say a handoff is needed.

---

# TASK A — THE TWO MEASUREMENTS, THEN **STOP**

## A1. `act2_coverage.md` — three countries, and the bases are not interchangeable

Complete `outputs_step3/act2_coverage.md`. **Italy has never been measured** and the file is not
complete without it.

Report per country:

* the **episode-level** share — episodes whose `act2_raw` is in the *recorded with a value* state,
  over that country's total episodes — measured from Step 1's accepted run
  **`Step1_docs/outputs_step1/run_20260816-2210`**;
* the **slot-level** share **for Spain only.** 🔴 **The UK and Italy ship episodes natively and have no
  slot base at all.** For them the episode share is the only rate that exists and must be labelled as
  one. **Never quote one base as the other** — they differ by a factor that depends on episode length,
  so a mixed-base comparison compares instrument design, not behaviour;
* the same episode share on the **post-filter** `harmonised.parquet` base, in its own column, clearly
  labelled. The corpus is built on that population, not on Step 1's.

**Already measured, to be re-derived rather than copied** — if your number disagrees, **report the
disagreement, do not silently adopt either**: Spain 340,269 of 2,778,480 slots (12.2 %) and 80,800 of
430,754 episodes (18.8 %); the UK 163,105 of 587,632 episodes (27.75 %).

🔴 **A rate quoted without its denominator is not a rate.** Every figure carries its numerator, its
denominator and its base.

**Also record, because Step 1 measured it and it bears on any aggregation rule:** Spain has 11,216
episodes mixing blank and non-blank `ASECU` and 13,009 carrying more than one distinct value, and the
reader keeps **first-of-run**. Measure the same two counts for Italy and the UK.

## A2. The token cost of a five-element tuple

The surviving argument in 3.2-bis is token cost and nothing else — the leak argument is **retired**,
because all three countries record a secondary activity. So measure it, exactly the way `COP` packing
was measured (D-S3-1, job 1252633).

**Five candidates:**

| # | Form | Absent secondary spelled as |
|---|---|---|
| 0 | `DUR,ACT,LOC,COP` — **the baseline, four elements** | — |
| 1 | `DUR,ACT,ACT2,LOC,COP` | a declared 2-digit sentinel |
| 2 | `DUR,ACT,LOC,COP,ACT2` | a declared 2-digit sentinel |
| 3 | `DUR,ACT,ACT2,LOC,COP` | an empty field |
| 4 | `DUR,ACT,LOC,COP,ACT2` | an empty field |

**Three conditions, all three deliberate, and each one killed a previous measurement on this project:**

1. 🔴 **In situ, never a bare string.** Measure inside a complete episode tuple **and** inside complete
   real diaries. BPE merges across the comma and the semicolon, so the cost of `45` alone is not its
   cost inside `20,311,11,45;`. **`RL18` reached the wrong recommendation by exactly this error** —
   8 tokens for a fragment that costs 11 in context.
2. 🔴 **Sweep every value in the shipped `ACT2` vocabulary and report the WORST case**, not a lucky
   example. A form costing 1 token for one code and 2 for another costs 2.
3. 🔴 **Verify the sentinel is not a legal code**, against the shipped secondary target list. Step 1
   pre-registered `999` as an out-of-list perturbation for Spain and **`999` turned out to be a real
   INE code**, so the perturbation tested nothing. A sentinel that is secretly valid is the same defect
   one level down.

**Measure on real data, not on a representative string.** Take a random sample of **at least 2,000
diaries** from `harmonised.parquet`, serialise each under all five candidates, and report **median and
p99 tokens per diary** for each. 🔴 **Compare against `G3.5`'s pre-registered band — median ≤ 220,
p99 ≤ 400.** That band is what rejected six-character binary `COP` packing at 225, before any real
record existed, and it applies here unchanged.

Tokenizer: `allenai/OLMo-2-0425-1B` as the stated stand-in for the 7B backbone's OLMo/dolma2 vocab —
**state that it is a stand-in and that the vocabulary identity is a premise you did not re-derive**,
exactly as the `COP` round did.

## A3. 🛑 STOP HERE

Deliverables: `outputs_step3/act2_coverage.md` and
`outputs_step3/act2_tuple_measurement.md` — the table, the exact strings measured, the sweep, and the
worst case.

**Then message the manager (`main`) and wait.** 🔴 **Whether `ACT2` enters the tuple is an author
decision taken on your number.** If it does, it must happen **before `corpus.jsonl` is emitted** — a
fifth element added afterwards invalidates the corpus, the Step 7 grammar and every trained fold.

---

# TASK B — ENCODER, DECODER, CORPUS

## 🔴 B0. TASK A IS CLOSED. THE FIVE DECISIONS IT WAS WAITING ON ARE ALL TAKEN

**Do not re-run any Task A measurement.** Jobs **1255223**, **1255237** and **1255285** are collected
and the author has ruled. Read `Step3_docs/4thJ_03_serialisation.md`, entries "2026-08-17 (evening)"
and **"2026-08-17 (night)"**, and the **current** `4thJ_03_serialisation_val.md` — it now has
**sixteen** gates, and `G3.5`'s band has changed. What binds you:

| | decision | what you build |
|---|---|---|
| **D-S3-1** | `COP` is a **single decimal integer, no leading zeros** | re-verified on the correct `LOC` alphabet; ordering unchanged |
| **D-S3-2** | `ACT2` **enters** the tuple, **before `LOC`**, and is **left empty** when absent | `DUR,ACT,ACT2,LOC,COP` — never a `98` sentinel, never a space |
| **D-S3-3** | `G3.5` re-based | median ≤ **300**, p99 ≤ **700**, **max ≤ 1024** — the max binds |
| **D-S3-4** | null `LOC` → an explicit **fifth class, `unknown`** | 24,800 episodes: **0 ES / 8,007 IT / 16,793 UK** |
| **D-S3-5** | null `COP` → an explicit **out-of-range `64`** | 68,464 episodes, **all UK**; range widens to **0-64** |
| **D-S3-6** | `strat_age_band` ships **verbatim** — `11-14` … `75+` | **no transliteration table**; `V3.c`'s alphabet admits `-` and `+` for this field alone |
| **D-S3-7** | held-out split **90/10 by respondent, seed 42** | not the LOCO fold |
| **D-S3-8** | delimiters: `\|` prefix↔body, comma within the prefix | as built |
| **D-S3-9** | null `act` → the explicit code **`000`** | 8,709 episodes in 5,248 diaries: **ES 3,786 / IT 333 / UK 4,590** |

Imputation was measured and **refused by a pre-registered rule**: only 17.26 % of null `LOC` and
29.04 % of null `COP` episodes sit between two *agreeing* neighbours, against a 99 % bar. See
`Step3_docs/4thJ_03b_null_structure.md`. 🔴 **Do not impute anything, anywhere, for any reason.**

**One Task A deliverable was never written** and you finish it as a transcription job, not a re-run:
`outputs_step3/act2_tuple_measurement.md`, from the tables already in
`Step3_docs/impl/2026-08-17_na-fix-rerun.md` (job 1255237 — the five candidate forms, the in-situ Part
A strings, the Part B per-diary distribution, and the statement that `'98'` was verified absent from
the 43 shipped `ACT2` target codes). Copy the numbers, change none of them.

## B1. `encoder.py` and `decoder.py` (work item 3.3)

```
<conditioning prefix>  |  DUR,ACT,ACT2,LOC,COP  DUR,ACT,ACT2,LOC,COP  ...  <eor>
```

🔴 **Five elements, and `ACT2` is empty — two adjacent commas — on the 77 % of episodes that have no
secondary activity.** `30,311,,at_home,22;` is a correct episode. A space is not an empty field and
`V3.c` will refuse it: **whitespace is not in the declared alphabet.**

**The prefix, in this fixed order**, read from these columns and no others:

`country` · `strat_age_band` · `strat_sex` · `strat_hh_type` · `strat_econ_status` ·
`strat_day_type` · `mode` · `scheme`

🔴 **Eight fields, not nine — D-S2-19 dropped `season`**, because Spain's `TRIM` and Italy's `meseri`
are each delivered pre-banded and mutually irreconcilable. `strat_season_raw` ships in the table and is
never serialised.

* 🔴 **Lowercase `country` on read** (D-S2-16), and **every join to a Step 2 crosswalk must assert it
  matched** — non-zero distinct matched keys per country, or the run FAILs. An un-normalised join
  returns zero rows per country and passes everything vacuously.
* 🔴 **The six `strat_*_raw` columns are NOT serialised.** Nor is `weight_*`, nor `act_raw`,
  `act2_raw`, `loc_raw`, nor any `cop_extra_*` or `act2_extra_*`. A symbol only one country can emit
  is a country marker inside a leave-one-country-out design.
* 🔴 **There is no `YEAR` field and no four-digit year anywhere in the prefix** (`G3.10`).
* **`COP` is a single decimal integer 0-64, no leading zeros** (D-S3-1, widened by D-S3-5). 🔴 **Read
  the bit order from `crosswalk_copresence.csv`'s `bit_position` column. Never hard-code it** — an
  encoder and decoder that agree with each other and disagree with the crosswalk round-trip perfectly
  and mean something else, which is the defect `G3.14 (b)` exists for.
* 🔴 **`COP = 64` means "co-presence not collected for this episode"** and is emitted **only** where
  all six `cop_*` flags are null — 68,464 episodes, every one of them UK. **It is one greater than the
  largest legal bit pattern**, so it cannot collide with any real combination. It is **not** a bit
  pattern and **must not be decoded as one**: `decode(64)` returns the null state, not six false flags.
  Those episodes were previously written as `0`, which is indistinguishable from a genuine *"alone: no,
  everyone else: no"* — and being UK-only, that made it a **UK fingerprint the model could learn**.
  Repairing that is the whole reason `64` exists.
* 🔴 **`ACT = 000` means "the diary entry here was not a usable activity"** (D-S3-9), emitted on the
  **8,709 episodes where `act` is null** — ES 3,786, IT 333, UK 4,590. Every one of them comes from
  one of eight source codes Step 2 declined to map **on purpose**, as diary-quality markers rather than
  activities; they are registered in `crosswalk_unmapped.md` and **Step 2 is not reopening**. `000` was
  verified free before it was chosen — not a legal target code, absent from the `act` column — whereas
  `998` and `999` are both taken. **Durations are untouched**, so `sum(DUR)` still closes at 1440.
  🔴 **Report the token count of `000` explicitly.** `G3.4` requires every 3-digit `ACT` code to be
  exactly one token and `000` has never been tokenised; **if it is two tokens, say so and stop** — the
  code changes, the gate does not.
* **`ACT` is the 3-digit target code**; `LOC` is whatever `crosswalk_location.csv` emits, **never a
  numeric range** (D-S2-3) — **plus the fifth class `unknown`** for a null `loc_class` (D-S3-4).
  The `LOC` alphabet is exactly: `at_home`, `other_place`, `private_transport`, `public_transport`,
  `unknown`, **one spelling each, lowercase.**
* **`ACT2`** is either **empty** or one of the **43 shipped `ACT2` target codes**. Nothing else — no
  sentinel, no `98`, no `NA`, no whitespace.
* 🔴 **The loader drops nothing, silently or otherwise.** It prints, per country, rows and diaries read
  and rows and diaries dropped, **before** anything else, and FAILs if the drop count is non-zero
  (`V3.i`). This is not a formality: `4thJ_cop_reverify.py` excluded 8,873 diaries with a null
  `loc_class` episode from its own sample, and the only reason anyone knows is that it printed the
  number. **A record the loader never offered the encoder is invisible to `G3.1` by construction** —
  the corpus and the loader's frame agree perfectly, and every round-trip gate passes.
* 🔴 **`pd.NA`, not `NaN`.** `loc_class`, `act2` and the six `cop_*` flags are pandas nullable dtypes.
  A null test written as `isinstance(x, float) and pd.isna(x)` **misses `pd.NA` and crashes** —
  `int(pd.NA)` raises, and `pd.NA == ""` returns `pd.NA`, whose truth value raises. Use `pd.isna(x)`
  **alone, and before any `==` comparison.** This defect class has cost four failed jobs on this exact
  data, at two separate sites, and you are touching all three affected columns at once.

**Requirement: `decode(encode(d)) == d` exactly, for 100 % of the corpus, compared field by field, not
as a string.**

## B2. The four tokenizer assertions (work item 3.4)

Over the **full corpus**, not a sample: `tokenize(detokenize(ids)) == ids`; every 3-digit `ACT` code is
**exactly 1 token**; no record exceeds the context budget; **100 % of records end with `<eor>`.** 🔴 A
corpus where some completions do not terminate produces a model whose generation never stops.

🔴 **No tokens are added to the vocabulary** (`RL05`): LoRA freezes embeddings, unfreezing costs about
16.8 GB of optimizer state and breaks GGUF and vLLM export. `len(tokenizer)` must equal the published
base value.

## B3. Emit the corpus (work item 3.5)

`outputs_step3/corpus.jsonl`, one record per diary, **with a held-out split by respondent, never by
diary** — a person's two diary days may not straddle it. The UK fields two days per respondent; Spain
and Italy field one. 🔴 **This split is the ordinary held-out set. It is NOT the leave-one-country-out
fold** — folds are Step 4's, and confusing the two would leak.

Also `outputs_step3/token_stats.md`: the token-length distribution per country and per stratum —
**median, p99 and max** — reported against `G3.5`'s **current** band, **median ≤ 300, p99 ≤ 700,
max ≤ 1024**, and saying **which end** any exceedance sits at (`V3.d`).

🔴 **The 200-token benchmark is dead and you do not report against it.** It was one hand-made
25-episode string. The band was re-based by the author on the measured distribution (D-S3-3) and the
**max is the binding clause**: `RL05` packs training sequences to 2048 tokens, a longer record is
**silently truncated**, and 1024 is that window halved for margin. The measured max before the
`unknown` and `64` codes was 751.

🔴 **If the corpus exceeds the band, report it and stop. Do not move it.** It has been moved once, on
the record, with the reason written down first. A second move is gate-shopping, and from the inside the
two look identical.

---

## 🔴 ACCEPTANCE TESTS — state each one in your report

1. The tuple you built is `DUR,ACT,ACT2,LOC,COP` with `ACT2` **empty** when absent — quote one real
   serialised episode of each kind, present and absent, in your report.
2. Round-trip exact on **100 %** of the corpus, field by field. **`decode(64)` returns the null
   co-presence state, and `decode` of `unknown` returns a null `loc_class`** — not a value.
3. All four tokenizer assertions run on the **full corpus**, not a sample. `len(tokenizer)` unchanged.
4. The split is by respondent; the intersection of respondent IDs across splits is **0**.
5. The bit order came from `crosswalk_copresence.csv`. Say so, and say which column you read.
6. 🔴 **The loader dropped nothing.** Print rows and diaries read per country and confirm they are
   **446,547 / 1,010,140 / 567,381** and **19,140 / 38,260 / 15,854**, totalling **2,024,068** and
   **73,254**. A different number is a stop, not an adjustment.
7. 🔴 **The three explicit-null counts reconcile against `harmonised.parquet`, per country**:
   `LOC == unknown` = **0 / 8,007 / 16,793** (ES / IT / UK), `COP == 64` = **0 / 0 / 68,464**,
   `ACT == 000` = **3,786 / 333 / 4,590**. These are `G3.16`'s thresholds and they are hard numbers,
   not a shape check.
9. 🔴 **`strat_age_band` is serialised verbatim** — `11-14`, `75+` — with **no transliteration table**
   (D-S3-6). A mapping the encoder authors and the decoder must invert is the symmetric-defect class
   volunteered into a field no gate is watching.
10. **The token count of `000` is reported.** If it is not exactly 1, that is a stop.
8. **No threshold moved, nothing was imputed, and nothing was added to the vocabulary.** State all
   three in terms.

## DELIVERABLES

`outputs_step3/act2_tuple_measurement.md` (transcription — see B0), `encoder.py`, `decoder.py`,
`corpus.jsonl`, `token_stats.md`, and a Progress Log **fragment** at
`outputs_step3/proglog_step3_build.md` for the manager to merge, ending with a section headed
**WHAT I DID NOT VERIFY**.

🔴 **You build. You do not validate.** The sixteen gates are a **separate task in a separate session**
(`4thJ_employee_step3_gates_2026-08-17.md`) and they are written by someone who has not seen your
encoder. Do not write them, do not pre-run them, and do not "check them informally" — an author who
grades their own work is `G3.1` auditing the encoder against itself, one level up.

Report anything this document did not decide for you, and say plainly what you assumed. 🔴 **Stopping
on something odd is worth more here than coding around it** — three of the four new Step 2 decisions
came from an employee doing exactly that.
