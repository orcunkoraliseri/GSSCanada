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
| Track A (Eurostat SUF) runs in parallel, never on the critical path | `RL01`, parent 1C |
| The parser tolerates **both** reported file shapes | Parent 2A-bis; `RL17` A1 adjudicated for relational but the file is not in hand |

🔴 **The one thing that would reopen decision 6** is a delivered file that does not match its
inventory row — for example a UK 2014-15 file that turns out to be 15-minute slots. That is a
finding, not a reason to add a wave.

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
start_min, duration_min, act_raw, loc_raw, cop_raw[5],
mode, scheme, weight_ind, weight_dia
```

`mode` and `scheme` are constant per country here and become the constant prefix fields of Step 3B.
They are carried from Step 1 so that no later step has to guess them.

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
