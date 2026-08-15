# Step 1 — Corpus definition and acquisition

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 1. Validation: `4thJ_01_corpusAcquisition_val.md`

---

## STATUS

**Definition ✅ CLOSED (author decisions 5 and 6, 2026-08-14). Acquisition OPEN and executable.
Nothing is downloaded. This is the first step in the project that produces a file.**

---

## AIM

Get four national HETUS microdata files onto `/speed-scratch`, in a documented state, with their
codebooks, and know exactly what each one contains before anything is harmonised.

Not "acquire as much time-use data as possible". The corpus is fixed; this step executes it.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where it was taken |
|---|---|
| **HETUS only. No Canada, no United States** | Author decision 5. Parent doc, scope table |
| **Four countries, one wave each** | Author decision 6 |
| **Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10** | Author decision 6, from `RL17` Part B1 |
| Earlier waves are **held-out validation, never training data** | Author decision 6, parent 1B |
| **Newer waves are excluded too** — UK 2020-21, Italy 2022-23, Spain 2024-25, France 2024-25 | Parent 1B-bis |
| Track A (Eurostat SUF) runs in parallel, never on the critical path | `RL01`, parent 1C |
| The parser tolerates **both** reported file shapes | Parent 2A-bis; `RL17` A1 adjudicated for relational but the file is not in hand |

🔴 **The one thing that would reopen decision 6** is a delivered file that does not match its
inventory row — for example a UK 2014-15 file that turns out to be 15-minute slots. That is a
finding, not a reason to add a wave.

🔴 **Do not "upgrade" a country to its most recent wave during acquisition.** It is the obvious thing
to do when a newer file is sitting next to the one on the list, and it would silently break the
corpus: UK 2020-21 is online lockdown fieldwork at 16+, Italy 2022-23 is ACL 2020 plus web/app
collection, and Spain 2024-25 and France 2024-25 have no released microdata at all. The four waves on
the list are **all paper self-completion under one coding generation**, which is what keeps `ACT` at
three digits for Step 9. **The Eurostat HETUS 2020 round will not release microdata before 2027**, so
there is no newer obtainable corpus to be tempted by either.

---

## INPUTS

None. This is the head of the pipeline.

---

## WORK ITEMS

### 1.1 — Obtain the four files

| # | Source | Wave | Route | Credential | Owner action |
|---|---|---|---|---|---|
| A | INE *Encuesta de Empleo del Tiempo* (Spain) | 2009-10 | direct microdata download | **none** | Download. Start here: it is the only source that needs nothing |
| B | UK Data Service, SN 8128 | 2014-15 | End User Licence | free registration | Register, accept EUL, download |
| C | Progedo / ADISP (France) | 2009-10 | academic registration | free registration | Register, request, download |
| D | ISTAT Micro.dati (Italy) | 2013-14 | free application | application, 2-8 weeks | **HELD already from paper 1** — confirm the held copy is the same wave and the same extract before assuming it is |

**Definition of done:** four archives on `/speed-scratch/o_iseri/4J/raw/<country>/`, each with its
codebook, each with a recorded md5, each with the URL and date it came from written into
`outputs_step1/acquisition_manifest.json`.

🔴 **Record the md5 at download time, not later.** A hash computed after a file has been touched is a
hash of what we have, not of what they sent.

### 1.2 — Read each codebook before writing any parser code

For each file, extract and record, **from the codebook rather than from a report**:

* file shape: relational (`INDFILE` / `DDFILE` / `EFILE`) or one flat wide file;
* whether `START` and `DURATION` exist natively, or whether episodes must be reconstructed from slots;
* the exact weight variable names;
* the activity coding list edition, and its depth (2-digit or 3-digit);
* the location coding list;
* the co-presence fields and how many there are;
* slot length, diary origin hour, minimum age, diary days per respondent;
* the collection mode.

**Definition of done:** `outputs_step1/codebook_facts_<country>.md`, one per country, each stating
which page or table of which codebook each fact came from. Facts with no citation are marked
`NOT FOUND` and stay that way.

### 1.3 — Write the shape-agnostic reader

One reader per country is acceptable and probably necessary; a single reader with four branches is
not required. What **is** required:

* it emits one common intermediate record regardless of input shape;
* it **itemises everything it could not parse** and fails on it. 🔴 A reader that returns `0.0` or
  silently drops a row it does not understand blames the system under test for its own gap — this
  cost 16 spurious FAILs in 3J and the remedy there was to fix the reader, never the band;
* it never infers a value it did not read.

**Intermediate record, one row per episode:**

```
country, wave, hid, pid, diary_day, episode_index,
start_min, duration_min, act_raw, act2_raw, loc_raw,
cop_raw[5], cop_extra_<country>_<field> ...,
mode, scheme, weight_ind, weight_dia
```

`mode` and `scheme` are constant per country here and become the constant prefix fields of Step 3B.
They are carried from Step 1 so that no later step has to guess them.

🔴 **Two fields were added on 2026-08-14, after the Spanish file, and both exist for the same reason:
a recorded field is never discarded at Step 1.**

* **`act2_raw` — secondary activity (finding F-ES-6).** Spain records it on **340,269 of 2,778,480
  slots, 12.2 %**, and the original contract had nowhere to put it. It is now carried. **Three states
  must be distinguishable and must never be collapsed:** *not recorded by the instrument* (a country
  property), *recorded and blank* (the respondent reported no secondary activity), and *recorded with
  a value*. A country that does not field it emits **missing**, never blank, and never `0`.
* **`cop_extra_<country>_<field>` — country-specific co-presence flags (finding F-ES-2, decision
  D-S2-2).** Spain fields six flags, not five. The Spanish reader already emitted all six as named
  columns, which was a **deliberate deviation** from this contract; the contract now matches what the
  reader did rather than the reader being changed to match the contract.

🔴 **Neither field is serialised at Step 3 by that decision alone.** Step 1 decides what is *kept*;
Step 3 decides what is *written into the token stream*, and those are different questions with
different costs. See Step 3, 3B-bis.

**Definition of done:** `outputs_step1/episodes_<country>.parquet` plus a per-country parse report
naming every dropped or unparsed row.

### 1.4 — File the Eurostat entity-recognition enquiry

Not blocking, and **more valuable than it was**: our four waves *are* the HETUS 2010 round, so Track A
would widen the corpus from four countries to seventeen with no harmonisation change at all. With
four countries, leave-one-country-out trains on three, which is limitation C4.

**Definition of done:** the enquiry is sent to Concordia's Office of Research and the date is
recorded. **Not** "a report says Concordia is not on the list" — that is already known and is not the
same as having asked.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step1/acquisition_manifest.json` | Step 1 validation; the Data Availability statement |
| `outputs_step1/codebook_facts_<country>.md` | Step 2, which harmonises against these facts and not against any report |
| `outputs_step1/episodes_<country>.parquet` | Step 2 |
| `outputs_step1/parse_report_<country>.txt` | Step 1 validation gate G1.5 |

---

## HOW IT RUNS

Speed conventions, and they are not negotiable:

* **`sbatch` only. Never a blocking `srun`, never bare `python` on the login node.**
* Every job requests the full seven days: `-t 7-00:00:00`, `--partition=ps`.
* `HF_HOME`, `PIP_CACHE_DIR`, `TMPDIR` all under `/speed-scratch/o_iseri/`.
* Downloads happen **locally or on the login node via `scp`**, not inside a compute job — compute
  nodes have no outbound network.
* `/speed-scratch` purges after 90 days. Final artefacts get copied off.

---

## WHAT BLOCKS THIS STEP

Nothing blocks 1.1 to 1.3. Item 1.4 is independent.

🔴 **What this step blocks:** everything. Steps 2 to 9 have no input until 1.3 emits a file.

---

## DEFINITION OF DONE FOR THE WHOLE STEP

1. Four archives on disk with recorded md5s and provenance.
2. Four codebook-fact documents, every fact cited or marked `NOT FOUND`.
3. Four episode parquets, plus parse reports naming every unparsed row.
4. All Step 1 gates in the validation document PASS, **and each has been seen failing** on a
   deliberately broken input.
5. The Eurostat enquiry sent, with a date.

---

## PROGRESS LOG

Append-only. Never delete or reformat an existing entry.

### 2026-08-14 — step document created

* Corpus definition closed by author decisions 5 and 6. Acquisition not started.
* 🔴 Note for whoever executes 1.2: `RL01` and `RL02` gave **contradictory** file shapes and `RL17`
  adjudicated for the relational one. **The parser still handles both.** A verdict from a report is
  not a file, and the cost of being agnostic is a few hours against a defect discovered in month
  three.

### 2026-08-14 — newer waves recorded as excluded

* Added the "do not upgrade a country to its most recent wave" instruction and the decision row for
  UK 2020-21, Italy 2022-23, Spain 2024-25 and France 2024-25. Source: parent 1B-bis.
* 🔴 The failure this guards against is not a judgement call at a meeting. It is an acquisition-time
  reflex: a newer file sits beside the listed one, it looks like a free upgrade, and the mode change
  it carries is invisible until Step 3 tokenises a coding list nobody expected.

### 2026-08-14 — execution round issued for Spain

* Author asked for Steps 0, 1 and 2 to begin. **Step 0 is closed** and produced no executable work.
  **Step 2 was not started and no Step 2 prompt was written**, because it consumes all four
  `episodes_<country>.parquet` and none exists.
* Employee prompt written: `../Prompts/4thJ_employee_step1_spain_2026-08-14.md`. Scope is work item
  1.1 **row A only**, plus 1.2, 1.3 and the full validation battery including the perturbation set and
  the coverage clause. Not run yet; nothing is downloaded.
* 🔴 **Why Spain alone and not all four.** Three of the four sources need the author in person — UKDS
  needs an End User Licence accepted in their name, Progedo/ADISP needs academic registration, and the
  Italian file is held from paper 1 and has to be located and identified before it can be confirmed as
  the same wave and the same extract. An employee cannot register or accept a licence on anyone's
  behalf, so putting all four in one task doc would have produced a prompt that stalls on its second
  row. Item 1.4 stays with the author for the same reason.
* The Spanish reader is written first **because it fixes the intermediate-record contract**, not
  because Spain is easiest. The other three readers are each written against their own codebook once
  that codebook is in hand.
* Recorded for whoever runs it: **V1.a must fire on this round** — the runner FAILs below four
  countries, and that is correct behaviour on a one-country pass, not a bug to be escaped with a
  `--single-country` flag.

### 2026-08-14 — Spain executed. 1.1, 1.2 and 1.3 done. **The first file in paper 4 exists.**

**1.1 — obtained.** INE *Encuesta de Empleo del Tiempo* 2009-2010, open download, no credential.
Eight artefacts, every md5 taken at download time before the archive was opened, all recorded in
`outputs_step1/acquisition_manifest.json` with URL and date.

* `datos_emptiem0910.zip`, 8,623,518 bytes, md5 `b38d01933e8d2cecec1b652c855fd64d`
* `disreg_emptiem0910.zip`, 165,012 bytes, md5 `59af0472dae16cd657a289071f9ea20a`
* methodology, 127 pages, md5 `0d360d282e6df2fb91d2948d218e8a8c`, plus the three questionnaires,
  the fieldwork evaluation and the methodology annex

🔴 **`RL01`'s entry-point URL is dead.** It gives `cid=1254736176860` under `/dyngs/INEbase/es/`,
which returns **HTTP 404**. The live operation is `cid=1254736176815` with no `/es/` segment, found
by navigating INEbase from the *Condiciones de vida* category. The report listed that URL as Tier 1,
opened in full. **It was not opened.** Route salvaged, table discarded — the usual outcome.

**Still outstanding on 1.1:** the archives are on the local workstation, **not** on
`/speed-scratch/o_iseri/4J/raw/spain/`. The `scp` has not been done and the manifest says so rather
than implying otherwise.

**1.2 — codebooks read.** `outputs_step1/codebook_facts_spain.md`, every fact cited to a sheet and
row of INE's record-layout workbook or a page of INE's methodology. Nothing came from a report.
INE's own stated record counts reconcile exactly against the delivery on all five files we read, and
each file's byte size is a whole multiple of its declared width plus CRLF, which reaches the same
counts by a second route.

The activity and location lists were transcribed out of the methodology into
`crosswalk_source_spain_activity.csv` (116 codes, ten major groups) and
`crosswalk_source_spain_location.csv` (20 codes), so that gate G1.4 has a reference INE wrote.

**Seven findings, recorded in full in `codebook_facts_spain.md`.** The four that change work:

* 🔴 **F-ES-1. Spain's diary day starts at 06:00, not 04:00.** Step 2 has "04:00 origin" as decided.
  `INTERVALO` 1 is 06:00-06:10 and 144 is 05:50-06:00. The hours 04:00 to 06:00 belong to a
  different calendar day than the one the respondent reported, so no 04:00 day can be built from a
  Spanish diary. **This is a harmonisation decision and it is the manager's.**
* 🔴 **F-ES-2. Co-presence has six flags in Spain, not five.** `RL02` said five and Step 2 item 2.3
  is written around five. Spain fields `SOLO`, `PAREJA`, **`PADRES`**, `MENOR`, `OTMH`, `OTCON`,
  coded 1 = yes and 6 = no. `MENOR` is narrower than "children": minors **under 10 who live with
  you**. The reader emits all six as named columns instead of packing them into `cop_raw[5]`.
  **That is a deliberate deviation from this specification**, taken because the alternative was to
  throw away a recorded field, and it needs a decision before Step 2.
* 🔴 **F-ES-3. `RL02`'s "10-19 stationary, 20-39 transport" is wrong.** In Spain `21-29` are
  *places* — restaurant, shops, hotel, beach, sports centre, street — and **`41` is public
  transport**, the only code above 39. A filter written `10 <= LOC <= 39` drops every
  public-transport episode and mislabels seven stationary codes as travel. `41` is in the file.
* **F-ES-4. The home-code warning is confirmed and it is worse than `RL02` stated.** Code `11` is
  "house, garage, vegetable plot, garden or grounds, provided they are in or attached to the dwelling
  building", **and working from home is coded `11` as well.** The conditioned volume is not
  recoverable from location alone.

Two smaller ones: INE's prose says 115 three-digit activity groups where its own annex lists 116 and
the file uses exactly those 116 (F-ES-5); and secondary activity `ASECU` is recorded on 12.2 % of
slots with nowhere to go in the Step 1 record (F-ES-6).

**1.3 — reader written and run.** `../tools/4thJ_read_spain.py`.

* File shape is **relational**, eight fixed-width ASCII files. `RL17`'s adjudication was right and
  `RL01`/`RL02`'s flat-file claim was wrong, but the parser was agnostic until the file said so.
* The diary is **not** delivered with native `START`/`DURATION`. It is 144 fixed 10-minute slots per
  diary. Episodes are reconstructed by collapsing runs that agree on activity, location and all six
  co-presence flags.
* **19,295 diaries, 2,778,480 slots, 430,754 episodes**, 22.32 episodes per diary.
* Every diary has exactly 144 slots. **One diary day per respondent**, measured, not assumed.
* `outputs_step1/episodes_spain.parquet` and `outputs_step1/parse_report_spain.txt`.
* **Zero rows dropped, zero unparsed, zero unexplained.** The reader raises and emits nothing rather
  than writing a partial table; there is no path through it that returns a number for a row it did
  not understand.

**1.4 — not done, and not ours.** The Eurostat entity-recognition enquiry goes to Concordia's Office
of Research in the author's own name.

### 2026-08-14 (later) — reader updated: `act2_raw` carried, `cop_padres` renamed. Re-emitted.

Employee task: `../Prompts/4thJ_employee_step1_gates_rerun_2026-08-14.md`. `../tools/4thJ_read_spain.py`
changed, run locally against the same raw files as the first pass (the Spanish archives are local; this
did not touch the cluster).

* **`act2_raw` (secondary activity, F-ES-6) is now carried**, closing the "NOT CARRIED: ASECU" line the
  first run's parse report printed. Sourced from `ASECU`, aggregated to episode level the same way
  `act_raw` is — first-of-run — and stored in a nullable pandas **`string`** column so `pd.NA` (not
  recorded) and `""` (recorded and blank) cannot collapse into each other going through parquet. Spain
  fields `ASECU` on every `DIARIO2` row, so no Spanish episode is `pd.NA`; the dtype supports that state
  now so the column does not need widening when the other three countries are read.
* **Episode-level states, of 430,754 episodes: not recorded 0, recorded and blank 349,954, recorded
  with a value 80,800.** Printed in `parse_report_spain.txt`. 🔴 This is a different number from
  F-ES-6's 340,269-of-2,778,480 **slot**-level figure — episodes are built from `APRIN` + `LUGAR` + the
  six co-presence flags, not from `ASECU`, so a first-of-run summary at episode grain is not the same
  quantity as a slot-level count. Measured for the record: 11,216 of 430,754 episodes mix a blank and a
  non-blank `ASECU` across their own underlying slots. This is a property of collapsing to episode
  level under the existing split key, not a parsing defect — flagged here because it is exactly the
  kind of thing 1.3's own text warns is easy to get subtly wrong, and because it is the reason the
  validation document's `G1.11` compares two independent re-derivations of the same first-of-run
  quantity rather than the slot-level figure against anything.
* **`cop_padres` renamed to `cop_extra_es_padres`**, per D-S2-2's naming convention for country-extra
  co-presence flags (`cop_extra_<country>_<field>`). No other co-presence column touched.
* **Re-emitted `episodes_spain.parquet` and `parse_report_spain.txt`.** Both prior versions backed up
  (`*.bak_2026-08-14`) and the backups verified non-empty before the originals were overwritten.
  **19,295 diaries, 2,778,480 slots, 430,754 episodes — unchanged.** Adding the column did not change
  the parse.
* The full twelve-gate battery was re-run against this reader; see the progress log in
  `4thJ_01_corpusAcquisition_val.md` for the result.
