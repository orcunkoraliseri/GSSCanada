# 4J — EMPLOYEE TASK: bring the **United Kingdom** through Step 1, codebook to gate battery

### Hand this to a **fresh** employee session as its first message. Do not resume a long thread.
#### Written 2026-08-14 by the manager. Scope: UKTUS 2014-15 (UK Data Service SN 8128) only. **Do not touch Spain, Italy or France.**

---

## YOUR ROLE

You are the **employee**. You execute exactly what is written here, in order, and you stop. You do not
redesign a gate, you do not move a threshold, you do not add a country, and you do not improve the
specification. **If the specification is wrong, you write the finding down and stop.** A gate that
fails is a result, not a bug to be worked around.

Read these before you touch anything. They are the specification; this prompt is a work order, not a
paraphrase you may implement instead:

* `../Step1_docs/4thJ_01_corpusAcquisition.md` — work items 1.2 and 1.3, and the **intermediate
  record contract** (the block beginning "Intermediate record, one row per episode")
* `../Step1_docs/4thJ_01_corpusAcquisition_val.md` — **fourteen** gates, the perturbation table, the
  coverage clause, the vacuity guards, and the progress log
* `../Step1_docs/outputs_step1/codebook_facts_spain.md` — **the template for your own deliverable.**
  Match its shape: every fact carries the document and page it came from, and a fact you cannot find
  is written `NOT FOUND` and stays that way
* `../tools/4thJ_read_spain.py` and `../tools/4thJ_gates_step1_spain.py` — **reference implementations
  only.** Spain is a fixed-width relational delivery and the UK is not. Copy the discipline, never the
  parsing.

---

## 🔴 THE ONE IDEA BEHIND THIS WHOLE TASK

**Spain is not the template for the data. It is only the template for the rigour.**

The Spanish reader was written first because it fixed the record contract. It is now very easy to
assume the UK delivery is Spain with different column names. It is not, and the differences below are
already measured. **Every fact you write must come from the UK's own documentation**, not from the
Spanish file, not from this prompt, and not from what you remember about time-use surveys.

Where this prompt states a number, it is stated so you can **notice if you disagree with it**. If your
measurement differs from a number below, that is a finding: write it down and say which is right.

---

## HARD RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`, never bare `python` on the login node,
  not even a one-line import check. Flagged three times on this account; a fourth is suspension.
  **This task runs entirely on the local workstation.** You have no reason to touch the cluster at all.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell. Use `wc -l`.
* Verify a backup is non-empty (`[ -s "$BK" ]`) before truncating anything.
* **Do not create files that are not listed under the Definition of done.**
* **Do not modify anything belonging to Spain** — not `4thJ_read_spain.py`, not
  `4thJ_gates_step1_spain.py`, not `codebook_facts_spain.md`, not `episodes_spain.parquet`. If your
  work implies a Spanish file is wrong, that is a finding for the manager, not an edit.
* Python: `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`. Bare `python` on this
  workstation hits the Windows Store stub and fails.

---

## TASK 0 — Unpack, hash, and register the delivery

The archive is at
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Datasets\UK-TUS-20260815T031737Z-1-001.zip`.

It is a Google Drive export wrapper. Inside it is `UK-TUS/8128tab_<hash>_V1.zip`, which is the actual
UK Data Service delivery and unpacks to `UKDA-8128-tab/`.

1. Unpack to `C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\4J\raw\uk\`, mirroring how Spain sits at
   `..\raw\spain\` (archives kept, `unpacked\` beside them).
2. **md5 every archive and every delivered data file.** 🔴 **Do not edit
   `acquisition_manifest.json`.** Another employee is working on Italy in parallel and would overwrite
   you. Instead write a fragment to
   `../Step1_docs/outputs_step1/acquisition_manifest_uk.json`, containing **only** the `uk` entry, in
   exactly the structure the existing Spanish entry uses in `acquisition_manifest.json` — read that
   file to copy its shape, but do not write to it. The manager merges the fragment.
3. 🔴 **The URL and download date.** The author downloaded this from the UK Data Service on
   **2026-08-14** under the End User Licence, study **SN 8128**. Record the study DOI/landing page as
   printed in `UKDA-8128-tab/mrdoc/UKDA/UKDA_Study_8128_Information.htm` and `read8128.htm` — **take
   it from the delivered files, not from memory.** If the delivery does not print a URL, write what it
   does print and mark the rest `NOT FOUND`.
4. Record the licence as **End User Licence (UKDS EUL)**. 🔴 This matters beyond Step 1: the licence
   governs what may be released, and Step 5's release decision already turns on it. Do not paraphrase
   the licence terms; record its name and where it is stated.

---

## TASK 1 — `codebook_facts_uk.md` (work item 1.2)

**Write this before you write one line of reader code.** This is the whole point of work item 1.2, and
it is the step where Spain's real findings came from.

Your sources are the delivered documentation, and you must cite which:

* `mrdoc/allissue/uktus15_diary_ep_long_ukda_data_dictionary.rtf` — the episode file's dictionary
* `mrdoc/allissue/uktus15_individual_ukda_data_dictionary.rtf`
* `mrdoc/allissue/uktus15_household_ukda_data_dictionary.rtf`
* `mrdoc/allissue/uktus15_dv_time_vars_ukda_data_dictionary.rtf`
* `mrdoc/pdf/8128_ctur_report.pdf` and `mrdoc/pdf/8128_natcen_reports.pdf` — the technical reports.
  **The weighting methodology lives here.** Read the weighting section properly; see TASK 3.
* `8128_file_information.rtf`

Reproduce every row of the `codebook_facts_spain.md` fact table for the UK: file shape, native
`START`/`DURATION`, weight variable names, activity coding list and its **edition and depth**, location
coding list, co-presence fields **and how many**, slot length, diary origin hour, minimum age, diary
days per respondent, collection mode. Then add the counts table — see G1.1 below.

### 🔴 Four things about the UK that are already measured, and that you must resolve properly

These came from the manager's inspection of the delivery. They are stated here because each one is a
place where copying Spain silently produces a wrong file.

**1.1 — The episode file is native episodes, with `eptime`.** Spain is 144 fixed 10-minute slots per
diary and the Spanish reader *reconstructs* episodes with a first-of-run rule. **The UK ships episodes
already.** Do not reconstruct anything. Establish from the dictionary what `eptime` actually measures
(a duration in minutes? a slot count?) and cite it. 🔴 **Do not assume it is minutes because it would
be convenient.**

**1.2 — The UK records up to THREE secondary activities**: `What_Oth1`, `What_Oth2`, `What_Oth3`. Spain
records one (`ASECU`) and Italy records one. The intermediate record contract carries **one**
`act2_raw`. 🔴 **This is a specification gap and it is the manager's to close, not yours.**

Your instruction: **carry `act2_raw` from `What_Oth1`**, and **additionally carry `What_Oth2` and
`What_Oth3` as `act2_extra_uk_2` and `act2_extra_uk_3`**, following the exact precedent of
`cop_extra_es_padres` — a recorded field is never discarded at Step 1. Apply the same three-state rule
to all three columns. Then **write the finding** (`F-UK-n`) stating how many episodes carry a second
and a third secondary activity, so the manager can decide what Step 3 serialises. **Do not merge them,
do not pick "the most important one", and do not drop 2 and 3.**

**1.3 — There are TWO diary weights**, `dia_wt_a` and `dia_wt_b`. 🔴 **You do not choose between
them.** Find what the technical report says each one is for, cite the page, record both in
`codebook_facts_uk.md`, and **carry both** into the parquet as `weight_dia_a` and `weight_dia_b`.
Record which one the documentation says is the default for diary-level analysis, **with its citation**,
and write a finding that the choice is pre-registration-relevant and unmade. If the report does not say,
that is `NOT FOUND` and it is a finding, not a coin flip.

**1.4 — Co-presence is nine fields**, including `WithAlone`, `WithOtherYK`, and explicitly `WithMiss`
and `WithNA`. Spain fields six. The contract's `cop_raw[5]` holds five. Follow the Spanish precedent
exactly: **emit every recorded flag as its own named column, never fold one into another**, and record
the mapping and the count as a finding. 🔴 `WithMiss` and `WithNA` are *missingness* fields, not
co-presence categories — record what the dictionary says each means and do not treat them as people.

### Also establish, and do not skip

* **Diary days per respondent.** `daynum` and `DiaryDay_Act` exist, which Spain has no analogue for.
  Spain measures 1. **Measure the UK and assert it against the codebook** (gate G1.9). If the UK is 2
  days per respondent, then every per-diary gate below is **per diary-day**, not per person, and you
  must say so explicitly in your gate report.
* **Diary origin hour.** Spain's is 06:00, which was finding F-ES-1. Find the UK's and cite it.
* **Which files you are NOT reading.** Spain recorded `HTR1`, `HTR2` and `SD` as not read. Do the same
  for `uktus15_wksched.tab` and anything else you do not use, with the reason.

**Definition of done:** `../Step1_docs/outputs_step1/codebook_facts_uk.md`, plus
`crosswalk_source_uk_activity.csv` and `crosswalk_source_uk_location.csv` transcribed from the
delivered code lists, matching the Spanish files' shape.

---

## TASK 2 — `4thJ_read_uk.py` (work item 1.3)

One reader per country is expected. Write `../tools/4thJ_read_uk.py`. It emits the **same intermediate
record** as Spain:

```
country, wave, hid, pid, diary_day, episode_index,
start_min, duration_min, act_raw, act2_raw, loc_raw,
cop_raw[5], cop_extra_<country>_<field> ...,
mode, scheme, weight_ind, weight_dia
```

* `country` = `"UK"`. 🔴 Use `"UK"`, not `"GB"` — every project document says UK, and the fold
  rotation is documented by that name. Note the choice in `codebook_facts_uk.md` in one line.
* `wave` = the wave as the delivery states it.
* `mode` and `scheme` are constant per country and are carried so no later step guesses them. Take
  them from the codebook, not from Spain's values.
* **`weight_dia`**: carry `weight_dia_a` and `weight_dia_b` as described in 1.3 above. If the emitted
  schema needs a single `weight_dia` to satisfy the contract, populate it from the documented default
  **and only if the documentation states one**; otherwise leave the contract field null, carry both
  named columns, and report it.

### 🔴 The three-state rule, which is the easiest thing here to get subtly wrong

Three states must survive into the parquet and stay separable, for `act2_raw` and for
`act2_extra_uk_2` / `act2_extra_uk_3`:

| State | Meaning | Representation |
|---|---|---|
| **not recorded** | the instrument does not field it at all | `pd.NA` |
| **recorded and blank** | the instrument fields it and this episode has none | `""` (empty string) |
| **recorded with a value** | a code | the code, as a string |

Use a pandas **`string`** dtype. 🔴 **An object column round-tripped through parquet is exactly where
`pd.NA` and `""` silently merge**, and a reader that merges them moves no row and emits no illegal
code — nothing except `G1.11` can see it.

🔴 **A `.tab` file read with pandas defaults will destroy this distinction before you ever reach the
dtype question.** An empty field becomes `NaN`, and a sentinel like `-1`, `-8` or `-9` becomes an
integer that looks like a code. Read with `keep_default_na=False`, `dtype=str`, and then map the
delivery's own missing-value conventions **as the data dictionary defines them**, code by code, citing
it. 🔴 **UKDA files commonly use negative sentinels for "does not apply" and "no answer", and those
are two different states.** Whatever you find, itemise it in the parse report.

### Parse completeness

It **itemises everything it could not parse and fails on it.** A reader that returns `0.0` or silently
drops a row it does not understand blames the system under test for its own gap — that cost 16
spurious FAILs in 3J. It never infers a value it did not read.

**Definition of done:** `../Step1_docs/outputs_step1/episodes_uk.parquet` and
`parse_report_uk.txt`, the parse report naming every dropped or unparsed row and printing the
three-state counts for each of the three secondary-activity columns.

---

## TASK 3 — `4thJ_gates_step1_uk.py`: the fourteen gates on the UK

Work through the gate table in the validation document. It is the specification. What follows is what
is **UK-specific**, not a replacement for reading it.

### 🔴 3.0 — The independence requirement, restated for a delimited file

`G1.7c`, `G1.7d` and `G1.11` exist to catch **a reader that read the wrong column**. So:

* 🔴 **The gate runner must not import anything from `4thJ_read_uk.py`** — not its column maps, not
  its helpers, not its output. A check fed by the reader cannot detect the reader.
* Spain's version of this was re-transcribing byte offsets. The UK is tab-delimited, so the equivalent
  is: **the gate runner identifies its columns independently, by name, from its own transcription of
  the data dictionary**, and **prints both the reader's column map and its own** so a human can compare
  them by eye. Two independent transcriptions that agree are evidence; one used twice is not.
* 🔴 **Resolve columns by name, never by position**, and **fail loudly if a name is absent** rather
  than falling back to an index.

### 3.1 — `G1.1` row-count reconciliation

Spain worked because INE prints its own record counts. **Find whether the UKDA delivery prints
episode, individual and household record counts** — check `8128_file_information.rtf`, `read8128.htm`
and the technical reports.

🔴 **If no delivered document states the counts, `G1.1` is `NOT CHECKED` for the UK — printed, never a
pass, never scored.** Do **not** substitute your own count as the reference; that is precisely the
circularity that retired `G1.7b`. Report it as a finding.

*(For orientation only, and not a reference: the manager measured `uktus15_diary_ep_long.tab` at
587,632 lines and `uktus15_individual.tab` at 11,422 lines, both including the header row.)*

### 3.2 — `G1.2` duration closure, and `G1.9`

Every diary must sum to 1440 minutes, 100 % of diaries, no exceptions. 🔴 **If the UK has two diary
days per respondent, the unit is the diary-day** — respondent-level summing would give 2880 and a
gate that "passes" at the wrong unit is worse than one that fails. State the unit you used in the
report.

### 3.3 — `G1.4` code-list membership

100 % of `act_raw`, `act2_raw` and `loc_raw` inside the edition declared in `codebook_facts_uk.md`.
Test `act2_extra_uk_2` and `act2_extra_uk_3` as well. 🔴 **A blank is not a code and is not tested
against the list.** Print, separately per column, the counts of *not recorded*, *recorded and blank*,
and *recorded with a value*.

### 3.4 — `G1.7b`, and the question you must actually answer

`G1.7b` is retired **for Spain**, because INE's estimator (METH p. 34, step 3) is ratio-adjusted to the
population projection, so the weights are calibrated to the very figure the gate compared them
against.

🔴 **Circularity is a property of the source, so it does not transfer and it does not exempt. You must
establish it for the UK from the UK's own weighting methodology**, in `8128_natcen_reports.pdf` or
`8128_ctur_report.pdf`.

* If the UK weighting **is** calibrated to a population total or to age × sex margins, then `G1.7b` is
  `NOT CHECKED` for the UK for the same reason, **and you cite the page**, and `G1.8` is narrowed the
  same way Spain's was — read the `G1.8` row in the validation document before you decide what it can
  still detect.
* If it is **not** calibrated that way, `G1.7b` is a live gate for the UK and you score it.
* 🔴 **"Spain retired it, so the UK does too" is not an answer, and neither is "surveys are usually
  calibrated."** Cite the page or write `NOT FOUND` and mark the gate `NOT CHECKED` for lack of an
  established reference — which is a different reason, and you must say which reason applies.

Either way: **never delete a retired gate, and never score it as a pass.** Keep printing both numbers,
labelled as evidence of nothing, with the reason.

### 3.5 — `G1.7c` cross-file weight identity

Spain's power came from `FACTORF` appearing in four files at four different byte offsets. **Establish
whether any UK weight is restated across more than one delivered file** (for example an individual
weight in `uktus15_individual.tab` and in the episode file).

* If yes: require bit-identity **as raw strings before any numeric conversion**, 100 % of respondents,
  read independently by the gate runner.
* 🔴 **If the weight is carried in only one file, `G1.7c` is `NOT CHECKED` — printed, never a pass.**
  That is already written into the gate. Do not invent a substitute check to make the report look
  fuller.

### 3.6 — `G1.7d` weight magnitude against the declared layout

Every weight strictly below the maximum the declared width allows, and at or above 1.0 — a weight
under 1 represents less than one person, which no design produces. Print observed min, max and
distinct count **before** the verdict.

🔴 Spain's reference was the layout workbook's declared integer width. **If the UK dictionary declares
no width for a delimited file, say so** and state what reference you used instead and why it is not
derived from the data under test. If there is none, `NOT CHECKED`.

🔴 **Test this against real UK weights before you assume the ≥ 1.0 clause holds.** Some agencies
publish scaled or normalised weights with a mean of 1, which puts perfectly valid weights below 1. If
that is what the UK ships, **that is a finding and a specification question for the manager — not a
threshold for you to move.** Report it and mark the gate.

### 3.7 — `G1.8` demographic marginals

Weighted age × sex within ±1.0 pp per cell of the UK's own published table for that wave. 🔴 **Read
the narrowed `G1.8` row in the validation document first.** If the UK weighting calibrates to age × sex
(see 3.4), the agreement on the complete file is imposed, not earned, and the gate detects only **a
subsample presented as the full file**. Record it that way rather than reporting a false clean pass.

If no published UK table for the wave is available in the delivery, `NOT CHECKED`, printed, and a
finding. **Do not go looking for one online** — literature and web search are out of scope for this
task by hard project rule.

### 3.8 — `G1.11` secondary-activity three-state integrity

**Episode-level identity.** The count of episodes carrying a non-blank secondary activity in the
emitted table must equal the count obtained by **re-reading the delivered file inside the gate runner
with its own independent column resolution**, importing nothing from the reader. **Exact, no
tolerance.**

Run it for `act2_raw` and, separately, for `act2_extra_uk_2` and `act2_extra_uk_3`.

🔴 **Do not hard-code any count the reader produced as the reference.** The reader's number is the
quantity under test. If you hard-code it, you have rebuilt `G1.7b` in a new place.

*(Note: Spain needed a first-of-run episode rebuild here because Spain is slot-level and 11,216 Spanish
episodes mix blank and non-blank across their own slots. The UK ships episodes, so the recount is a
direct recount — but it must still be **independent**, which is the part that matters.)*

---

## TASK 4 — The perturbation set and the coverage clause

Each perturbation is applied **to a copy** of the parsed data, in memory, and must break **exactly
one** gate. The table in the validation document is the specification; adapt each case to UK column
names, **not to UK convenience**.

Every case in that table applies, plus:

* **Set one `act2_extra_uk_2` to a code outside the list** → `G1.4`.
* 🔴 **Rewrite every blank `act2_raw` as a code, or every code as blank** → `G1.11` alone. No row
  moves and every code stays inside the list, so the defect is invisible to the rest of the battery.
* **Null perturbation: change nothing** → **nothing may fail.** 🔴 Keep this one. On Spain it caught a
  real defect in the employee's own gate code.
* 🔴 **Use a sentinel that is genuinely outside the UK code list, and prove it is** by checking it
  against your transcribed list before you use it. On Spain the pre-registered `999` turned out to be
  a **real INE code** and the perturbation could not fire. Print the sentinel you chose and the check
  that it is absent.

### The coverage clause

After the set has run, cross-tabulate every perturbation against the baseline and **FAIL the probe if
any gate that PASSes on the real data was never made to fall by anything in the set.**

`NOT CHECKED` gates are exempt, and only because `NOT CHECKED` is printed on every run and never
counted as a pass.

🔴 **If the coverage clause FAILs, that is the deliverable.** Report which gate was never shaken and
stop. **Do not invent a perturbation to make it green** — the clause exists to refuse a pass that
nothing has tested, and a perturbation written after the fact to satisfy it defeats exactly that.

Known not to attribute, and not a defect to tune away: anything that removes rows also fells `G1.5`.
Report it again if it recurs. **Do not weaken `G1.5`.**

---

## VACUITY GUARDS

* **V1.a** — FAIL if fewer than 4 countries were scanned. 🔴 **It will fire. It must fire.** This run
  scans one. Report it; **do not add a single-country escape flag.** It clears when all four countries
  exist, and not before.
* **V1.b** — print row counts, the file list and every md5 **before** any verdict.
* **V1.c** — read each gate's exit status from the process that computed it. 🔴 A check that cannot
  distinguish *found nothing* from *could not run* is not a check.
* **V1.d** — any code, unit or column name the reader does not recognise is **printed and refused**,
  never assumed harmless.

---

## DEFINITION OF DONE

1. Delivery unpacked to `_local_runs\4J\raw\uk\`, every md5 recorded in
   `../Step1_docs/outputs_step1/acquisition_manifest_uk.json`, with URL, date and licence.
2. `../Step1_docs/outputs_step1/codebook_facts_uk.md`, every fact cited to a document and page,
   `NOT FOUND` where it is not found, and the findings numbered `F-UK-1`, `F-UK-2`, …
3. `../Step1_docs/outputs_step1/crosswalk_source_uk_activity.csv` and
   `crosswalk_source_uk_location.csv`.
4. `../tools/4thJ_read_uk.py`, emitting `../Step1_docs/outputs_step1/episodes_uk.parquet` and
   `parse_report_uk.txt` with the three-state counts printed.
5. `../tools/4thJ_gates_step1_uk.py`, importing nothing from the reader for `G1.7c`, `G1.7d` or
   `G1.11`, printing both column-map transcriptions.
6. The full battery run — baseline, every perturbation, the null — with the coverage clause evaluated
   and its verdict printed, written to
   `../Step1_docs/outputs_step1/gate_report_step1_uk.txt`.
7. 🔴 **Do not edit `4thJ_01_corpusAcquisition_val.md` or `4thJ_01_corpusAcquisition.md`.** The Italy
   employee is appending to the same two files in parallel and one of you would silently overwrite the
   other's entry. **Write your two progress-log entries to a single new file instead:**
   `../Step1_docs/outputs_step1/proglog_entries_uk.md`, containing two clearly headed sections —
   *"for `4thJ_01_corpusAcquisition_val.md`"* and *"for `4thJ_01_corpusAcquisition.md`"* — written as
   finished, append-ready progress-log entries in the same style as the existing ones. The manager
   appends them.
8. The validation entry must contain: the baseline table, which gates were seen failing and under
   what, the coverage-clause verdict, anything that did not attribute, and every gate you marked
   `NOT CHECKED` **with the reason**. The implementation entry records the UK reader and what the
   delivery turned out to be.

---

## WHAT IS NOT YOURS TO DECIDE

* **Do not move a threshold.** Every one is pre-registered.
* **Do not choose between `dia_wt_a` and `dia_wt_b`.** Carry both, cite what the report says, report
  the gap.
* **Do not collapse the three secondary activities**, and do not decide what Step 3 serialises.
* **Do not fold any co-presence flag into another.**
* **Do not resurrect `G1.7b`** for Spain, and do not assume its fate for the UK either way — establish
  it from the UK's own methodology and cite the page.
* **Do not hard-code any number the reader produced** as a gate's reference.
* **Do not acquire, download, or register for anything**, and **do not search the web or the
  literature.** France is with Progedo and is the author's, in person.
* **Do not touch Italy.** Another employee is working on it in parallel, in the same repository. Every
  file you create is UK-named; if you find yourself editing an Italian or Spanish file, stop.
* 🔴 **If the specification and the UK delivery genuinely cannot both be satisfied, stop and write the
  finding.** That is a real deliverable and it is how Spain's four specification defects were found.
