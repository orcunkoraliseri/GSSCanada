# Step 1 — Corpus acquisition. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_01_corpusAcquisition.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. No artefact exists, so no gate has been run and none has been seen failing.**
Every threshold below is pre-registered: it is fixed now, before the data arrives, so that it cannot
be chosen to fit what the data turns out to be.

---

## WHAT THIS STEP MUST PROVE

That the file on disk is **the file we think it is**, that we have read **all** of it, and that
what the parser emitted is a faithful re-expression of what the survey recorded.

Nothing about behaviour, nothing about the model. This step validates *custody and completeness*.

---

## GATES

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G1.1** Row-count reconciliation | A truncated download, a partial extract, a silently skipped file | Episode-row count per country equals the count stated in that country's own codebook or published methodology report, **exactly**. No tolerance | **project-chosen**, and exactness is the point |
| **G1.2** Duration closure | Episodes that do not tile the day; a reconstruction bug | For every diary: `sum(duration_min) == 1440`. **100 % of diaries**, no exceptions | **derived from the instrument** — a time-use diary covers a day by construction |
| **G1.3** Quantisation | A wave whose slot length is not what the inventory claims | 100 % of durations are multiples of **10**. 🔴 **If any country fails this, that country's wave is not admissible to the Step 7 tally automaton and the finding is escalated, not resampled away** | **derived from the Step 7 grammar** |
| **G1.4** Code-list membership | Codes outside the declared coding list; an off-by-one column read | 100 % of `act_raw`, `loc_raw` inside the edition declared in `codebook_facts_<country>.md` | **project-chosen** |
| **G1.5** Parse completeness | 🔴 The reader silently swallowing what it does not understand | `parse_report` names **every** dropped or unparsed row, and the count of unexplained drops is **0**. A drop with a written reason is allowed; a drop without one is a FAIL | **project-chosen**, from 3J's most expensive reader lesson |
| **G1.6** Provenance | A file that cannot be traced to a source, or a hash computed after the fact | Every archive has an md5, a URL and a download date in the manifest, and the md5 recomputed from disk **matches** | **project-chosen** |
| **G1.7** Weight presence and range | A weight column read from the wrong position | Weight variables present, all strictly positive, and the weighted respondent total is within **±2 %** of the country's published population total for the survey's target age range | **project-chosen** tolerance; the published total is external |
| **G1.8** Demographic marginals | The wrong extract, or a subsample presented as the full file | Weighted age × sex distribution within **±1.0 pp** per cell of the country's own published table for that wave | **project-chosen** tolerance |
| **G1.9** Diary-days-per-respondent | Assuming multi-day structure a country does not have | Recorded per country and asserted against `codebook_facts`. **Spain must read 1.** A country whose measured value disagrees with its codebook is a FAIL, not a note | **derived from the codebook** |
| **G1.10** Constant-field invariance | `mode` or `scheme` varying inside a wave, which would mean the extract mixes instruments | Exactly one distinct value of each per country | **derived from decision 6** |

---

## 🔴 EVERY GATE MUST BE SEEN FAILING BEFORE IT IS TRUSTED

A gate is trusted because it has been seen failing, not because it is green. Each perturbation below
is applied **to a copy** of a parsed file, in memory, and **must break exactly one gate** — a
perturbation that moves two gates cannot attribute what it broke.

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Drop the last 5 % of episode rows | G1.1 | G1.2 on the surviving diaries |
| Delete one episode from one diary | G1.2 | G1.1 (count is checked per country, so state which) |
| Rewrite one duration from 30 to 25 | G1.3 | G1.4 |
| Set one `act_raw` to `999` | G1.4 | G1.3 |
| Make the reader skip a malformed row without logging it | G1.5 | all others |
| Corrupt one byte of an archive after hashing | G1.6 | all others |
| Multiply one weight column by 10 | G1.7 | G1.8 |
| Drop every respondent over 65 | G1.8 | G1.1 must **also** fail — this perturbation moves two, so it is scored as a **coverage** case, not an attribution case |
| Declare Spain as 2 diary days in `codebook_facts` | G1.9 | all others |
| Set `mode` on one row to a second value | G1.10 | all others |
| 🔴 **Null perturbation: change nothing** | **nothing may fail** | everything |

**The null perturbation is not optional.** It is the cheapest case to build and it tests the guard's
*strictness* rather than its reach: a gate satisfiable by nothing moving is a gate that will certify a
no-op as a success.

### Coverage clause

After running the set, cross-tabulate every perturbation against the baseline and **fail the probe if
any gate that PASSes on the real data was never made to fall by anything in the set.** A probe that
checks only the gate each perturbation was named for, then prints `10/10 SEEN FAILING`, reads as
complete while a headline gate has never once been tested. That is a green instrument reporting on a
subset it chose itself.

---

## VACUITY GUARDS

Checks on the checks. Each **fails** rather than passing quietly.

* **V1.a** — the gate runner FAILs if it scanned fewer than **4** countries. A battery that runs over
  an empty or partial set must report, not go green.
* **V1.b** — the runner prints the row count, file list and md5 of everything it read, **before** any
  verdict. A summary line that did not read the measurement may not print a conclusion.
* **V1.c** — every gate's exit status is read from the process that computed it, never from a pipe
  tail. 🔴 A check that cannot distinguish *found nothing* from *could not run* is not a check.
* **V1.d** — any code, unit, or column name the reader does not recognise is **printed and refused**,
  not assumed harmless. An unrecognised value silently treated as benign is how two separate 3J
  defects happened.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

Stated explicitly, because a caution that is silent about an arm reads as clearance for it.

* It does **not** check that the four countries are comparable to each other. That is Step 2.
* It does **not** check the activity semantics — only that codes are inside their declared list. A
  code that is valid but means something different in this wave than in the ACL edition we assume is
  Step 2's problem, and it is a real one.
* It does **not** validate the held Italian file against paper 1's analysis. That comparison is the
  control and it belongs to Step 6.
* 🔴 **G1.7 and G1.8 compare against published national tables. If those tables were themselves
  derived from the same microdata extract we are checking, the reference and the target share an
  ancestor and the gate cannot fail.** Confirm the published table is a *design-weighted population*
  figure, not a re-tabulation of the public-use file, before quoting either gate as evidence.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Ten gates and eleven perturbations pre-registered before any data exists. Zero run, zero seen
  failing.
* 🔴 G1.3 is the gate that would have caught the UK 2000-01 problem — 15-minute slots, durations that
  are multiples of 15, inadmissible to a tally automaton built on multiples of 10 — **if that wave
  had been in the corpus.** Author decision 6 removed it before the gate had to. The gate stays
  because the same defect can arrive in any file that is not what its inventory row says.
