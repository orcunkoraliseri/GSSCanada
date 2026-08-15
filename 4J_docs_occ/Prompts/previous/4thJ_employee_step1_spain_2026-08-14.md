# 4J — EMPLOYEE TASK: Step 1 executed on Spain, end to end

### Hand this to a **fresh** employee session as its first message. Do not resume a long thread.
#### Written 2026-08-14 by the manager. Scope: Step 1 work items 1.1 (Spain row only), 1.2, 1.3, and the Step 1 gate battery run on Spain.

---

## YOUR ROLE

You are the **employee**. You execute exactly what is written here, in order, and you stop. You do not
redesign the corpus, you do not add a country, you do not relitigate a decision, and you do not
improve the specification. If the specification is wrong, you **write the finding down and stop** —
you do not fix it yourself.

Read these two documents before you touch anything. They are the specification and you implement
them, not this prompt's paraphrase of them:

* `../Step1_docs/4thJ_01_corpusAcquisition.md` — the work items
* `../Step1_docs/4thJ_01_corpusAcquisition_val.md` — the ten gates and the perturbation table

---

## 🔴 STATE BEFORE YOU START

**Nothing in this project has ever been downloaded.** You are producing the first file in paper 4.
Every threshold in the validation document is **pre-registered**: it was fixed before the data
arrived, precisely so it cannot be adjusted to fit what the data turns out to be. **You may not move
a threshold.** If Spain fails a gate, Spain failed the gate, and that is the deliverable.

---

## WHY SPAIN AND ONLY SPAIN

Four countries are in the corpus: Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10. Three of
them need a human being to register or apply in their own name — UKDS SN 8128 needs an End User
Licence, Progedo/ADISP needs academic registration, and the Italian file is already held from paper 1
and has to be located and identified by the author. **Spain is the only source in the entire HETUS
2010 round that needs no credential at all.** So Spain goes first, alone, and it carries the whole
reader design with it.

🔴 **Do not download the other three. Do not create an account anywhere. Do not accept a licence on
anyone's behalf.**

🔴 **Do not "upgrade" Spain to a newer wave.** Spain 2024-25 has no released microdata, and 2002-03 is
a different coding generation. **The wave is 2009-10.** A newer file sitting next to the listed one
is not a free upgrade; it is a silent corpus break that will not surface until Step 3.

---

## HARD RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`. Never bare `python` on the login node,
  not even a one-line import check. Every job requests `-t 7-00:00:00 --partition=ps`. This has been
  flagged three times on this account; a fourth is suspension.
* **Downloads happen locally or on the login node via `scp`.** Compute nodes have no outbound network.
* `HF_HOME`, `PIP_CACHE_DIR`, `TMPDIR` all under `/speed-scratch/o_iseri/`.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell. Use `wc -l`.
* Verify a backup is non-empty (`[ -s "$BK" ]`) before truncating anything.
* Do not create files that are not listed under a Definition of done below.

---

## WORK ITEM A — obtain the Spanish file (spec item 1.1, row A)

INE publishes *Encuesta de Empleo del Tiempo* 2009-10 microdata as an open download. The entry point
reported by `RL01` is:

```
https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176860&menu=resultados&idp=1254735976608
```

🔴 **That URL came from a deep-research report and has not been opened by anyone on this project.**
Treat it as a lead, not as a fact. If it 404s or lands on a different survey, navigate INEbase
yourself and **record the URL you actually used**.

INE ships fixed-width ASCII plus separate syntax files (SPSS / SAS / R) that carry the column layout.
**Take the syntax files too.** Without them the ASCII is unreadable and you will be tempted to guess
column positions, which is the single worst thing you can do in this step.

**Definition of done**

1. Archives on `/speed-scratch/o_iseri/4J/raw/spain/`, with the codebook/methodology PDF and the
   syntax files beside them.
2. `outputs_step1/acquisition_manifest.json` with, for every file: the URL, the download date, the
   byte size, and the **md5**.

🔴 **Compute the md5 at download time, before the file is opened, moved or unzipped.** A hash taken
afterwards is a hash of what we have, not of what they sent, and it certifies nothing.

---

## WORK ITEM B — read the codebook before writing one line of parser code (spec item 1.2)

From the **codebook and the syntax files**, never from `RL01`, `RL02` or `RL17`, record:

* file shape: relational (household / diary / episode files) or one flat wide file;
* whether `START` and `DURATION` exist natively, or whether episodes must be reconstructed from the
  144 ten-minute slots;
* the exact weight variable names;
* the activity coding list edition and its depth (2-digit or 3-digit);
* the location coding list;
* the co-presence fields and how many there are;
* slot length, diary origin hour, minimum age, diary days per respondent;
* the collection mode.

**Definition of done:** `outputs_step1/codebook_facts_spain.md`, in which **every fact names the page
or table it came from**. A fact you could not find is written as `NOT FOUND` and it stays `NOT FOUND`.
Do not fill a gap from a report. Do not fill a gap from what the other countries do.

Two things you are likely to meet, flagged so they are not surprises:

* **Spain fields one diary day per respondent.** Gate G1.9 asserts exactly that. If the file says
  otherwise, that is a finding of the first order — write it down and stop.
* `RL01` and `RL02` gave **contradictory** file shapes, and `RL17` adjudicated for the relational one.
  A verdict from a report is not a file. See work item C.

---

## WORK ITEM C — the shape-agnostic reader (spec item 1.3)

Write a reader for Spain that emits the common intermediate record, **one row per episode**:

```
country, wave, hid, pid, diary_day, episode_index,
start_min, duration_min, act_raw, loc_raw, cop_raw[5],
mode, scheme, weight_ind, weight_dia
```

`mode` and `scheme` are constant per country and are carried from here so that no later step has to
guess them. They become the constant prefix fields in Step 3B.

Three requirements, and the second is the one this project has already paid for:

1. It emits the common record **regardless of input shape** — flat wide or relational. You are writing
   the Spanish reader, but the record it emits is the contract the other three will meet.
2. 🔴 **It itemises everything it could not parse, and it fails on it.** A reader that returns `0.0`,
   or silently drops a row it does not understand, blames the pipeline for its own gap. That cost
   **16 spurious FAILs in 3J**, and the remedy there was to fix the reader — never to widen the band.
3. It never infers a value it did not read.

**Definition of done:** `outputs_step1/episodes_spain.parquet` plus
`outputs_step1/parse_report_spain.txt` naming **every** dropped or unparsed row with a written reason.

---

## WORK ITEM D — run the Step 1 gates on Spain

Run G1.1 to G1.10 from `4thJ_01_corpusAcquisition_val.md`. Report each one PASS, FAIL or
`NOT CHECKED`. 🔴 **`NOT CHECKED` is a legitimate and required outcome** where the reference does not
exist yet — never print a PASS for a check that could not run.

Gates that will only partly run on one country, and how to handle them:

* **V1.a** fails the runner if it scanned fewer than 4 countries. On this round it **must fire**.
  That is correct behaviour, not a bug. Record it as fired and report the ten gates underneath it.
  Do not disable V1.a, do not lower it to 1, do not add a `--single-country` escape hatch.
* **G1.7 and G1.8** compare against published INE tables. 🔴 Before you quote either as evidence,
  confirm the published table is a **design-weighted population figure**, not a re-tabulation of the
  same public-use file you are checking. If it is a re-tabulation, the reference and the target share
  an ancestor, **the gate cannot fail**, and you report it as `NOT CHECKED` with that reason.

---

## WORK ITEM E — see the gates fail

A gate is trusted because it has been seen failing, not because it is green. Apply each perturbation
in the validation document's table **to an in-memory copy** of the parsed Spanish data and record
which gate fell.

Three parts of that table are not optional:

* **The null perturbation — change nothing, nothing may fail.** It is the cheapest case to build and
  it tests strictness rather than reach. A gate that a no-op can satisfy will certify a no-op as a
  success.
* **The coverage clause.** After the set has run, cross-tabulate every perturbation against the
  baseline and **fail the probe if any gate that PASSed on the real data was never made to fall by
  anything in the set.** Checking only the gate each perturbation was named for, then printing
  `10/10 SEEN FAILING`, is a green instrument reporting on a subset it chose itself.
* **The "drop every respondent over 65" case moves two gates** (G1.8 and G1.1). It is scored as a
  **coverage** case, not an attribution case. Do not try to make it move one.

**Definition of done:** a perturbation results table, gate by gate, saying which fell and which stayed
clean, plus the coverage cross-tabulation.

---

## WHAT YOU DO **NOT** DO ON THIS ROUND

Written out because each of these is the plausible next thing to reach for.

* **You do not start Step 2.** Harmonisation needs all four episode tables. One country cannot build a
  four-column crosswalk, and a crosswalk built from one country and extended by assumption is exactly
  the defect Step 2 exists to prevent.
* **You do not touch Step 0.** It is closed. It is a record, not a work plan.
* **You do not file the Eurostat entity-recognition enquiry** (item 1.4). That is the author's, in
  their own name, through Concordia's Office of Research.
* **You do not write the readers for Italy, UK or France.** Each is written against its own codebook,
  after that codebook is in hand.
* **You do not adjust a threshold, widen a band, or add a tolerance.** If Spain fails, report the
  failure.

---

## HOW TO REPORT BACK

Append **one** entry to the Progress Log of `../Step1_docs/4thJ_01_corpusAcquisition.md`, dated, and
append one to `../Step1_docs/4thJ_01_corpusAcquisition_val.md` covering the gate run. Append-only:
never edit an existing entry.

The entry states, plainly:

1. What was downloaded, from which URL, on which date, with which md5.
2. Which codebook facts were found and which are `NOT FOUND`.
3. Episode-row count, diary count, and whether G1.1 reconciled against INE's own published figure.
4. Every gate: PASS, FAIL or `NOT CHECKED`, with the reason for each `NOT CHECKED`.
5. How many gates were **seen failing**, and which were not, and whether the coverage clause fired.
6. Anything you found that contradicts the specification.

Then stop. Do not begin the next country.

---

## THE ONE THING THAT WOULD REOPEN A CLOSED DECISION

A delivered file that does not match its inventory row — for example durations that are not multiples
of 10, which would make the wave inadmissible to the Step 7 tally automaton (gate G1.3). **That is a
finding to escalate, not something to resample away, and it is not a reason to add a different wave.**
Write it down, stop, and hand it back to the manager.
