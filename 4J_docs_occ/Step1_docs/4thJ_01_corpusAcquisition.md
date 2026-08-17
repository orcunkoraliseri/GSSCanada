# Step 1 — Corpus definition and acquisition

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 1. Validation: `4thJ_01_corpusAcquisition_val.md`

---

## STATUS

**Definition ✅ CLOSED (author decisions 5 and 6, 2026-08-14). Acquisition OPEN and executable.
Nothing is downloaded. This is the first step in the project that produces a file.**

---

## AIM

🔴 **THREE national HETUS microdata files, not four, from 2026-08-15 (author decision 16 — France is
excluded).** Get them onto `/speed-scratch`, in a documented state, with their codebooks, and know
exactly what each one contains before anything is harmonised. *(Superseded: "Get four national HETUS
microdata files…".)*

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
| ~~C~~ | ~~Progedo / ADISP (France)~~ | ~~2009-10~~ | — | — | 🔴 **STRUCK 2026-08-15 by author decision 16. France is excluded from the corpus.** Demande n°38663 was submitted 2026-08-14 with no published turnaround; the project will not hold on it. **The row is struck, not deleted** — if France arrives before any fold is evaluated it can still be re-admitted in full, and after that point it can only ever be an extra held-out country. See decision 16 in the parent plan's progress log |
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

---

### 🔴 CONTRACT CHANGES M-1 to M-5, decided 2026-08-15 after the UK and Italian rounds

Five things the two parallel rounds put on the manager's desk. All five are decided here. **Three are
contract changes, two are gate-basis changes, and every basis change is written down as one** in
`4thJ_01_corpusAcquisition_val.md`. None of them was closed by editing a gate to clear a FAIL.

#### M-1 — `loc_raw` gains the same three-state provision `act2_raw` has

**The defect was ours, not the delivery's.** The UK fields `-9` ("No answer/refused", DD value label)
in both `What_Oth1/2/3` and in `WhereWhen`. The reader maps it to *recorded and blank* for the three
secondary-activity columns — because the contract gives them three states — and passes it through
raw for `loc_raw`, because the contract gives `loc_raw` only one. One sentinel, two treatments, and
`G1.4` fails on 7,117 of 587,632 UK episodes (1.211 %) for the inconsistency (F-UK-15).

**Decision: fix the contract, then the reader. `G1.4`'s threshold is not moved.**

* **`loc_raw` is now a three-state field on the same terms as `act2_raw`** — *not recorded by the
  instrument*, *recorded and blank*, *recorded with a value* — in a nullable pandas `string` column,
  the three states separable through the parquet round-trip. Spain and Italy field a location on
  every episode and emit state 3 throughout, so nothing about either changes.
* **A value enters the "recorded and blank" state only if that country's own delivery declares it a
  missingness sentinel, with a citation, in `codebook_facts_<country>.md`.** The UK's `-9` qualifies
  on the data dictionary's own value label. 🔴 **There is no rule that negative values are sentinels
  and none may be invented.** An out-of-list value with no declared-sentinel citation stays a `G1.4`
  FAIL — which is exactly what keeps **`4276`** (F-UK-9, one episode of 587,632, labelled nowhere in
  the delivery) failing after this decision, as it must.
* **Each country's `codebook_facts` gains a sentinel table**: field, sentinel value, the delivery's
  own label for it, the citation, and the measured count. New gate **`G1.12`** checks the reader's
  `loc_raw` three-state emission against an independent recount from the raw file, exactly as
  `G1.11` does for `act2_raw`.

🔴 **Consequence for Step 2, flagged and not decided here:** 1.211 % of UK episodes have no location.
An episode with no location cannot emit a `LOC` symbol, and Spain and Italy have no equivalent hole.
That is Step 2's to close, and it now has a field to close it in.

#### M-2 — `G1.6` splits: integrity and provenance are two different claims

Italy FAILs `G1.6` because a hand-delivered archive has no per-file source URL and the employee
correctly refused to invent one. 🔴 **The verdict is not the expensive part. Because `G1.6` already
FAILs at baseline, `corrupt_archive_byte` could not fire, so Italy's md5 arm is UNTESTED** — a whole
detection arm lost to a bookkeeping gap. France arrives by the same hand-delivered route.

**Decision: split the gate. Do not move the provenance threshold.**

* **`G1.6a`, integrity** — every archive has an md5 recorded at receipt and the md5 recomputed from
  disk matches. Scored for every country, independently of any URL. This is what `corrupt_archive_byte`
  tests, and it can now fire for Italy and for France.
* **`G1.6b`, provenance** — every archive has a source URL and a date. **Threshold unchanged.** Italy
  FAILs it today and will keep failing it until the record is filled in.
* 🔴 **The Italian FAIL is a defect in our own custody record, not in the file.** The fix is the
  author supplying the URL and date the Italian archive was downloaded from, recorded in the manifest
  as `provenance_source: author_attested` with the attestation date. If the author cannot supply it,
  it stays `NOT FOUND`, `G1.6b` keeps failing, and that goes into the Data Availability statement.
* **The manifest gains `hashed_at`**, one of `download` or `receipt_from_author`, per archive, printed
  by `G1.6a` on every run. An attested URL is as good as one we typed ourselves; **an attested hash is
  not** — the project's own rule is that a hash taken after a file has been touched is a hash of what
  we have, not of what they sent. The two tiers are printed, never silently equal.
* **France's prompt must record the URL, the date and the md5 at the moment of download**, in the
  browser, before the file is moved.

#### M-3 — `G1.7a`'s "zero missing" bar is replaced by a conditional one, not widened

The UK ships `dia_wt_a`/`dia_wt_b` as a blank on 89 of 587,632 episode rows (2 of 16,533 person-days)
and `ind_wt` as a blank on 23 of 8,274 persons. All carry the delivery's own non-productive status
codes, `DMFlag = -6` and `HhOut = 598` (F-UK-8).

🔴 **Spain's `G1.7d` population precedent does not transfer, and it is worth saying why.** Spain
excluded `MHOGAR`'s 6,600 non-respondent members because **those rows carry no diary and enter no
corpus**. The 2 UK person-days *do* carry a diary — their episodes are present and sum to 1,440
minutes — so they enter the corpus. The population argument that rescued Spain is unavailable here.

**Decision, and the population is written down as the rule requires.**

* **Step 1's population is every diary the survey collected. Nothing is dropped for lacking a weight.**
  Step 1 is custody, not selection.
* **`G1.7a` is re-scoped** (basis change, recorded): present, finite, strictly positive and
  **more than one distinct value** on every row *for which the delivery computed a weight*, **and**
  every row without a weight must carry a delivery-declared non-productive status code. 🔴 **A missing
  weight on a row the delivery flags as productive is a FAIL.** This is not the old bar loosened — it
  is a strictly harder condition to satisfy by accident, because a reader that failed to parse a
  weight column would blank rows the delivery calls productive, and that now fails where "100 % of
  rows" would merely have failed for the wrong reason.
* **`weight_ind` and `weight_dia` are nullable**, and the count of corpus rows carrying no weight is
  printed per country on every run. Step 8's population construction may not silently treat an absent
  weight as zero.
* Recorded because it is the whole reason this could not be left standing: with `G1.7a` FAILing at
  baseline, **`weight_negative_one` and `weight_constant` both DID NOT FIRE on the UK.** The entire
  weight-check arm was dark on one of three built countries.

#### M-4 — `G1.7d`'s `>= 1.0` clause is conditioned on the declared weighting convention

UK weights are normalised to mean ≈ 1.000 and **60.3 % sit below 1.0** (F-UK-13). The `>= 1.0` clause
was derived from *"a weight under 1 represents less than one person, which no design produces"* — and
that reasoning is **only true of an expansion weight**. For a normalised weight it is simply false.
The clause is not being loosened; it was **wrong for that class of weight** and never should have been
applied to one.

**Decision: `codebook_facts_<country>.md` must state the weighting convention, cited, as one of**

| Convention | `G1.7d` bound |
|---|---|
| **expansion** — the weight is a count of population units represented | `[1.0, 10^declared_integer_width)`. Spain: `[1.0, 1e6)` |
| **normalised** — the weight has mean 1 by construction | `> 0`, and **mean within ±1 % of 1.0**. The `>= 1.0` clause does not apply |
| **not declared** | `NOT CHECKED`, printed, never a pass |

* 🔴 **The upper-bound half stays keyed to a declared layout width, so it remains `NOT CHECKED` for
  the UK** — the delivery is tab-delimited free text and ships no layout. M-4 does not rescue that,
  and does not pretend to.
* The ±1 % band is derived, not fitted: the only defect a mean-vs-1 comparison can catch is an
  order-of-magnitude misread of the decimal point, which lands 900 % away. **Recorded honestly: the
  UK's means (1.000322, 1.000182, 1.000000) were measured before this band was written**, so the band
  is not blind — but its headroom is roughly 30× the observed deviation and its reference is NatCen's
  normalisation statement, a different artefact from the microdata, which is the property `G1.7d`
  exists to have.

#### M-5 — the UK's `weight_dia` is `dia_wt_a`

`dia_wt_a` ("diary weight — analysis at diary level/event level") balances the sample by month **and
day of week** and matches age/sex to the population within each; `dia_wt_b` ("analysis at individual
level") balances by month only and **has no day-of-week adjustment** (NATCEN p. 31 §7.4 c and d).

**Decision: `weight_dia` = `dia_wt_a`.** Three reasons, in order of weight:

1. **Our unit is the person-day.** One corpus row is one diary. That is exactly the grain NatCen
   documents `dia_wt_a` for, and exactly the grain CTUR's own worked example uses it at
   (`svyset psu [pw=dia_wt_a], strata(strata)`, CTUR p. 13).
2. **Day of week is load-bearing for this paper.** The corpus deliberately mixes weekdays and weekend
   days and the output is an occupancy schedule. A weight with no day-of-week adjustment would carry
   whatever day-type imbalance the fieldwork left, straight into the thing we are modelling.
3. It is the delivery's own documented default for diary-level analysis.

`dia_wt_b` stays carried as `weight_dia_b` and is never silently substituted. **This freezes into
`prereg.md` before the first Leg-5 submission.** 🔴 **Named reopen trigger, and only this one:** if
Step 5 or Step 6 ever moves the unit of analysis from the person-day to the person — pooling a
respondent's two days into one record, which only the UK can even pose — `dia_wt_b` becomes the
correct field and the choice is re-taken then, in writing, before anything is trained.

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

🔴 **Rewritten 2026-08-15 for the three-country corpus (author decision 16).**

1. **Three** archives on `/speed-scratch` with md5s recorded at receipt and re-verified after transfer,
   plus `hashed_at` and `provenance_source` per archive (M-2).
2. **Three** codebook-fact documents, every fact cited or marked `NOT FOUND`, each now also carrying
   the **sentinel table** (M-1) and the **weighting convention** (M-4).
3. **Three** episode parquets, plus parse reports naming every unparsed row.
4. All **sixteen** Step 1 gates PASS, **and each has been seen failing** on a deliberately broken
   input, coverage clause SATISFIED, per country. 🔴 **`G1.6b` is expected to FAIL on Italy** until the
   author supplies the download URL, and that FAIL is not a reason to hold the step open — it is
   recorded in the Data Availability statement.
5. The Eurostat enquiry sent, with a date.
6. Both manager merges done: the per-country progress-log fragments appended, and the manifest
   fragments merged into `acquisition_manifest.json`.

🔴 **`V1.a` now FAILs below THREE countries, not four**, because decision 6 moved. That is the *only*
reason it moved, it moved by a dated author decision, and it is not a precedent for touching any other
guard. *(Superseded: four archives, four codebook documents, four parquets, fourteen gates.)*

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

### 2026-08-15 — the UK and Italy executed in parallel; **M-1 to M-5 decided by the manager**

**1.1, 1.2 and 1.3 are done for three of four countries.** UKDS SN 8128 (UKTUS 2014-15) and ISTAT
*Uso del Tempo* 2013-14 were built by two employees running concurrently against
`../Prompts/4thJ_employee_step1_uk_2026-08-14.md` and `..._italy_2026-08-14.md`. Artefacts in
`outputs_step1/`; counts, findings and gate results in the two `codebook_facts_<country>.md` files and
the two gate reports. **France is still with Progedo (demande n°38663) and `V1.a` still fires, 3 of 4.**

🔴 **Because they ran concurrently, neither employee wrote to `acquisition_manifest.json` or to either
Step 1 progress log.** Each emitted a fragment. **Both merges are still outstanding**, and this entry
is not one of them — it is the manager's decision round, written on the same day.

**The two rounds forced five decisions, and all five are now taken: M-1 to M-5**, in the new section
"CONTRACT CHANGES M-1 to M-5" above. Summary of what moves in *this* document:

* **The intermediate record gains a three-state `loc_raw`** (M-1), on the same terms as `act2_raw`.
* **`weight_ind` and `weight_dia` become nullable** (M-3), and no later step may read an absent weight
  as zero.
* **The manifest gains `hashed_at` and `provenance_source`** per archive (M-2).
* **`codebook_facts_<country>.md` gains two required facts**: a **sentinel table** (field, value, the
  delivery's own label, citation, measured count — M-1) and the **weighting convention**, cited, as
  *expansion* / *normalised* / *not declared* (M-4).
* **The UK's `weight_dia` is `dia_wt_a`** (M-5), with `dia_wt_b` carried alongside and one named
  reopen trigger.

🔴 **What this costs, stated up front:** the UK reader must change (M-1) and all three gate runners
must be rebuilt to the sixteen-gate specification, then **all three batteries re-run**. Spain and Italy
field a location on every episode, so neither reader changes for M-1 — but both are re-run, because a
country is scored against the current specification or it is not scored.

**Still outstanding on 1.1, and now the first thing that can use the cluster:** the raw archives for
all three countries are on the local workstation under `_local_runs/4J/raw/`, **not** on
`/speed-scratch/o_iseri/4J/raw/`. The `scp` has not been done and the manifest says so rather than
implying otherwise.

### 2026-08-15 (later) — 🔴 **AUTHOR DECISION 16: FRANCE EXCLUDED. Acquisition is COMPLETE at three.**

The author excluded France because Progedo demande n°38663 has no arrival date and the project will not
wait on it. Row C of work item 1.1 is **struck** (not deleted), and the AIM and definition of done above
are rewritten for three countries. **`V1.a`'s threshold moves from 4 to 3.**

🔴 **`V1.a` moved for one reason and it must not be generalised.** It is decision 6 expressed as code;
the author amended decision 6 in writing, on a dated line, so the guard follows. **It is not a flag, not
a tolerance, and not a precedent** — every other threshold in Step 1, including the five taken earlier
the same day, is untouched.

**What is left of Step 1:** the sixteen-gate re-run on the three countries, the two manager merges, and
the Eurostat enquiry (1.4). 🔴 **None of it waits on anyone outside this project**, which is the whole
point of the decision. The re-admission window, if France ever turns up, is in the parent plan's
progress log: full re-admission is possible only **before the first fold is scored**.

---

## 🔴 MERGE 1 of 2, done by the manager 2026-08-15 — the two parallel employees' entries, appended verbatim

The UK and Italian Step 1 rounds ran **concurrently** on 2026-08-14/15 and were forbidden from writing
to this file, precisely so neither could overwrite the other. Each emitted a fragment
(`outputs_step1/proglog_entries_uk.md`, `..._italy.md`) and **the two sections below are those
fragments, appended unedited.**

🔴 **They appear AFTER the manager's M-1..M-5 and decision-16 entries even though they describe work
that happened before them.** The log is append-only and may not be reordered, so the ordering is stated
here rather than repaired. **Read them as the record of the fourteen-gate rounds they were written
about** — everything they say about `V1.a` firing at "one country of four", about `G1.4`/`G1.6`/`G1.7a`
FAILing, and about specification gaps "left for the manager" was true when written and has since been
superseded by M-1 to M-5 and by decision 16.

---

### ⬇ appended verbatim from `outputs_step1/proglog_entries_uk.md`

### 2026-08-14/15 — UK executed. 1.2 and 1.3 done, 1.1 executed for the archive already in hand

Employee task: `../Prompts/4thJ_employee_step1_uk_2026-08-14.md`. Scope: UKTUS 2014-15 (UKDA SN
8128), work items 1.2 and 1.3 plus the full Step 1 validation battery on the archive the author had
already downloaded and delivered to the workstation. Nothing was acquired, downloaded or registered
for by this session.

**1.1 (partial, as scoped).** The delivery
(`Datasets/UK-TUS-20260815T031737Z-1-001.zip`, a Google Drive export wrapper around the actual UKDS
zip) was unpacked to `_local_runs/4J/raw/uk/`, mirroring Spain's `raw/spain/` layout (archives kept,
`unpacked/` beside them). Every archive and every one of the 17 delivered files was md5'd; the inner
UKDS zip's filename is itself a content-addressed SHA-256 and this session's independent SHA-256
recomputation matches it, a second, stronger integrity signal on top of md5. Recorded in
`outputs_step1/acquisition_manifest_uk.json` — a **fragment**, not a write to the shared
`acquisition_manifest.json`, so the parallel Italy session was not overwritten; the manager merges
it. DOI `http://doi.org/10.5255/UKDA-SN-8128-1` and licence (End User Licence, UKDS EUL) are both
taken verbatim from the delivered `UKDA_Study_8128_Information.htm` and `read8128.htm`; no literal
download URL is printed anywhere in the delivery and is recorded `NOT FOUND` rather than guessed.

**1.2 — codebooks read.** `outputs_step1/codebook_facts_uk.md`, every fact cited to a UKDA data
dictionary, the CTUR processing report or the NatCen/NISRA technical report, by printed page.
Fifteen findings recorded in full there. The four the manager flagged in advance were all confirmed,
measured, and in one case corrected:

* **`eptime` is minutes, `tid` is the START slot** (F-UK-1) — established two independent ways
  (a documented Stata-code equivalence and a direct row-level cross-check), not assumed.
* **Three secondary activities exist** (`What_Oth1/2/3`, F-UK-2), coverage 27.75 % / 2.72 % / 0.23
  %. All three carried (`act2_raw`, `act2_extra_uk_2`, `act2_extra_uk_3`), none merged, none dropped.
* **Two diary weights**, both carried (`weight_dia_a`, `weight_dia_b`); the contract's single
  `weight_dia` is populated from `dia_wt_a`, the documented default for diary/event-level analysis
  (CTUR p. 13, NATCEN p. 31, both cited), and the choice is flagged pre-registration-relevant per
  the work order.
* **Nine co-presence fields**, all emitted as named columns. `WithMiss` is genuine missingness;
  🔴 **`WithNA` turned out NOT to be a missingness flag for this wave** — it is a UK2000-01
  backward-compatibility concordance marker, since 2014-15 (unlike 2000-01) *does* code co-presence
  for sleep/work/education episodes (F-UK-4). Recorded so Step 2/3 do not misread it.

Two findings the work order did not anticipate, both surfaced by measurement rather than assumed
away: a single undocumented activity code (`4276`) appears once in 587,632 episodes with no label
anywhere in the delivered dictionary (F-UK-9); and the location field (`WhereWhen`) carries its own
missingness sentinel (`-9`, 1.211 % of episodes) that the intermediate-record contract has no
three-state provision for, the same shape of gap as the secondary-activity one but for `loc_raw`
(F-UK-15) — **both left for the manager to close, not resolved here.**

UK weights turned out to be **normalised (mean ≈ 1.000)**, not raw expansion factors like Spain's
`FACTORF` — roughly 60 % of real UK diary and individual weights are strictly below 1.0 (F-UK-13),
which matters directly for `G1.7d` below.

The activity and location code lists were transcribed from the UKDA data dictionary's own value
labels into `crosswalk_source_uk_activity.csv` (277 codes) and `crosswalk_source_uk_location.csv`
(35 codes), matching the Spanish files' shape.

**1.3 — reader written and run.** `../tools/4thJ_read_uk.py`.

* File shape is **six flat tab-delimited files**, not relational in Spain's sense. The UK ships
  **native episodes** (`tid` = start slot, `eptime` = duration in minutes) — the reader reconstructs
  nothing, the opposite of the Spanish reader's slot-collapsing.
* Two files read: `uktus15_diary_ep_long.tab` (587,632 episodes) and `uktus15_individual.tab`
  (11,421 people, demographics and `ind_wt`). Four files deliberately not read, with reasons
  (F-UK-14): `uktus15_household.tab`, `uktus15_diary_wide.tab`, `uktus15_wksched.tab`, and
  `uktus15_dv_time_vars.tab` (read only by the gate runner, independently, for `G1.7c`).
* **8,274 distinct people, 16,533 (person, diary_day) diaries, 587,632 episodes.** Every diary sums
  to exactly 1,440 minutes, 0 exceptions. Diary days per respondent measured at max 2 (design), with
  8,259 of 8,274 people completing both.
* 🔴 `diary_day` is populated from the survey's own 1st/2nd-day ordinal (`daynum`), **not** a
  day-of-week code as it is for Spain — 3 of 8,259 two-day respondents land on the same day of week
  on both their days, so only `daynum` is collision-free (F-UK-6). This means `diary_day` carries a
  different *kind* of value across the two countries' emitted tables; flagged for Step 2/3.
* Three-state secondary-activity handling implemented with a pandas nullable `string` dtype, exactly
  as the reconstructed-vs-native distinction requires. Weight columns converted to `float64`, with
  the delivery's own literal blank-space sentinel (not `-9`, not empty string) mapped to `NaN` and
  counted, never silently coerced (F-UK-8): 89 episode rows / 2 person-days for the diary weights,
  1,551 episode rows / 23 people for the individual weight.
* `outputs_step1/episodes_uk.parquet` (587,632 rows, 32 columns) and
  `outputs_step1/parse_report_uk.txt`. **Zero rows dropped, zero unparsed, zero unexplained** — the
  reader raises and emits nothing on any condition it cannot explain.

**1.1, remainder — not this session's to do.** Transfer to `/speed-scratch` was not attempted; this
task ran entirely on the local workstation per the work order, and the cluster was not touched at
all.

**1.4 — not done, and not this employee's.**

---

### ⬇ appended verbatim from `outputs_step1/proglog_entries_italy.md`

### 2026-08-15 — Italy executed. Work items 1.1 (Italy row only), 1.2 and 1.3 done. **The second country file in paper 4 exists.**

**1.1 — registered, not acquired by this session.** `uso_tempo_2013_IT.zip` and
`Nota_metodologica-2013.pdf` (38 pp. as delivered) were provided directly to the author by ISTAT on
2026-08-14 and copied into `_local_runs/4J/raw/italy/` by this employee session on 2026-08-15, all
four archives hashed on the local copy and reconciled byte-for-byte against the originals in
`4J_docs_occ/Datasets/IT TUS/` before unpacking. Fragment written to
`outputs_step1/acquisition_manifest_italy.json` (Italy entry only; `acquisition_manifest.json`
itself was not touched, per the work order, because the UK employee is working in the same file in
parallel). 🔴 **No per-file download URL exists anywhere in this delivery** — these files were never
fetched by a live download, so `url` is recorded `NOT FOUND` rather than invented; this is why
`G1.6` fails (see the validation entry above).

🔴 **Licence finding: this is ISTAT's mIcro.STAT public-use file, not the mFR.**
`Nota_metodologica.pdf` (the excluded 2023 volunteering module) describes an *mFR* (*File di
microdati per la ricerca*) release; the 2013-14 diary is a **different and more restricted
product**, ISTAT's own open mIcro.STAT public-use file — stated on the cover pages of
`Nota_metodologica-2013.pdf` and `uso_tempo_DescrizioneFile_Individuo__Anno 2013.pdf`, and
explained on the latter's p.3: the mFR carries higher informational content and requires a
justified request and the President of ISTAT's authorisation; mIcro.STAT does not. This bears on
Step 5's release decision and is recorded in `codebook_facts_italy.md`, finding F-IT-1.

The 2023 volunteering pair (`Nota_metodologica.pdf`, `UsoTempo_2023_IT.zip`) was hashed, copied
into the workspace, and recorded as present and explicitly excluded — not unpacked, not read.

**1.2 — codebook read.** `outputs_step1/codebook_facts_italy.md`, every fact cited to a Tracciato
HTML row, a classification file, a questionnaire page, or a methodology page. **Fourteen findings**,
`F-IT-1` through `F-IT-14`, recorded in full in the codebook. The five things the work order flagged
as "already measured" were all confirmed independently from ISTAT's own documentation: tab-delimited
with a header row (not fixed-width); native episodes with explicit clock start/end times and a
04:00 diary-day wrap (measured: exactly one wrap-episode per diary, all 41,229 diaries then sum to
exactly 1,440 minutes); `catcon` is a genuinely separate, coarser 2-digit/34-modality classification
from `catpri`'s 3-digit/146-code list (`F-IT-3`); eight co-presence fields, whose value domain
(blank, or the field's own fixed ordinal) had to be established by direct inspection because no
classification list documents them (`F-IT-4`); and blank is literally recorded spaces matching the
field's declared width, established the same way (`F-IT-6`, which also records that
`HelpTracciato_DELIMITED.html` does not in fact state a blank-field convention for this survey's
variables, contrary to what the task prompt assumed — read first, as instructed, and found not to
say what it was expected to say).

Two further findings change what later steps can rely on: **ISTAT's own weighting methodology is
calibrated to sex × nine age-class regional population totals** (Nota_metodologica-2013.pdf p.12),
putting `G1.7b` in the same circular family as Spain's, and narrowing what `G1.8` could ever detect
even with a reference (`F-IT-9`); and **no published Italian age×sex population table for 2013-14
exists anywhere in this delivery** — the methodology PDF is itself an incomplete excerpt (its own
page numbers jump from printed p.26 to printed p.95) — so `G1.8` cannot even run the narrowed check
(`F-IT-10`). Minimum age is **3**, not Spain's 10, with parent-proxy completion permitted for ages
3-10 (`F-IT-11`). Diary origin hour is **04:00** (QUEST-DG p.2), diary days per respondent measured
and asserted at **1**.

The activity, secondary-activity and location lists were transcribed out of ISTAT's own
classification HTML files into `crosswalk_source_italy_activity.csv` (146 leaf codes — 145
three-digit plus one genuine two-digit leaf, `90`, stored in the field as `"90 "` with a trailing
space rather than zero-padded, finding `F-IT-5`), `crosswalk_source_italy_activity2.csv` (34 codes,
`catcon`'s own list), and `crosswalk_source_italy_location.csv` (53 codes), so that gate `G1.4` has
a reference ISTAT wrote. All three lists were verified to cover the delivered file's observed
alphabet exactly (after the `catpri` right-strip finding `F-IT-5` is applied).

**1.3 — reader written and run.** `../tools/4thJ_read_italy.py`.

* File shape is **two flat tab-delimited files with a header row** (`DiarioGiornaliero`,
  `Individui`), joined on `profam`+`proind`. Not relational in Spain's eight-file sense, and not
  fixed-width — the parser was written to resolve every column by name, never by position, and to
  refuse (not assume) any unrecognised value.
* The diary is delivered as **native episodes** with explicit `oraini`/`minini`/`orafin`/`minfin`.
  No slot reconstruction. `duration_min` is computed with an explicit 04:00 wrap: exactly one
  episode per diary (41,229 of 41,229) wraps past midnight in naive clock arithmetic, and adding
  1,440 minutes to that one episode alone closes every diary to exactly 1,440.
* **41,229 diary respondents, 1,077,657 episodes**, 26.14 episodes per diary.
* Every respondent has exactly one diary day, measured, not assumed.
* `outputs_step1/episodes_italy.parquet` and `outputs_step1/parse_report_italy.txt`.
* **Zero rows dropped, zero unparsed, zero unexplained.** `act2_raw` (from `catcon`) is carried in a
  nullable pandas `string` column: not_recorded 0, recorded_and_blank 819,659, recorded_with_value
  257,998 — Italy fields `catcon` on every row, so (as for Spain) no Italian episode is ever "not
  recorded."
* All eight co-presence fields are carried as their own named columns
  (`cop_extra_it_daso` … `cop_extra_it_aperco`), following the Spanish precedent of never folding a
  recorded flag into another — none of Italy's eight maps unambiguously onto Spain's five-slot
  scheme, so all eight are carried as country-extras rather than a partial, guessed mapping.
* The join against `Individui` for `weight_ind` (`coefin`) and `weight_dia` (`coefi2`) is measured
  clean: **0 episodes unmatched to a non-blank diary weight**, of 1,077,657.

**1.4 — not done, and not ours.** Unchanged from the Spanish entry: the Eurostat entity-recognition
enquiry is the author's, in person.

---

### 🔴 Manager's note on the two appended entries, 2026-08-15

**Both are accepted as the record of their rounds. Two things in them are already superseded and one
line in each is now wrong, and saying so here is cheaper than a later session re-deriving it:**

* **"`V1.a` fires on one country of four"** — `V1.a`'s threshold is now **3**, by author decision 16.
* **"left for the manager to close"** (F-UK-15, the `loc_raw` sentinel; F-UK-2's three secondary
  activities) — **closed the same day as M-1 and F-ES-6 respectively.**
* **The UK's "`weight_dia` populated from `dia_wt_a`… flagged pre-registration-relevant"** — confirmed
  as **M-5**, with the reasoning written down rather than left as a default inherited from the
  delivery's documentation.
* **Italy's `G1.6` FAIL** — the gate has since been **split** (M-2). The integrity half (`G1.6a`) will
  score for Italy; the provenance half (`G1.6b`) **still FAILs and is meant to.**

🔴 **What was NOT verified independently and is recorded as such:** the perturbation batteries
themselves, Italy's `G1.2`/`G1.11` arithmetic, and every codebook citation except the two the manager
opened personally (ISTAT `!Leggimi.html`'s stated counts, and the UK's `4276` and `-9` frequencies).
They are read from the artefacts, which is the standard — but they were not re-derived.

### 2026-08-16 — second sixteen-gate round PREPARED BUT NOT SUBMITTED; runner fixes M-6 and M-7

The first sixteen-gate round completed (`0:0`; ES 18m32s, IT 1m39s, UK 2m24s) but its `G1.6a` result is
**VOID**: the gate trusted the manifest's `local_path` literally, and those are Windows workstation paths
that do not exist on the cluster, so all 13 archives — PDFs and a `.doc` among them — reported "missing on
disk". The archives are intact; TASK 0's own `md5sum` on the cluster matched every file before any job ran.
Because `G1.6a` FAILed at baseline it could not be seen falling, so `corrupt_archive_byte` reported
`newly-failed []` and Spain's `null` perturbation printed `🔴 NULL PERTURBATION MOVED A GATE`.

Three manager decisions for the second round: **M-6**, `G1.6a` resolves each archive under `--raw` at
invocation time while `local_path` stays in the manifest as provenance, with two distinct problem strings
(`md5 mismatch` vs `recorded location not resolvable under --raw`); **M-7**, sub-clause attribution so a
gate FAILing at baseline for a pre-registered unrelated reason no longer masks perturbations — this is why
M-1 was **not** reversed despite `DID NOT FIRE` on the UK; and the `V1.a` race fix — run-stamped output
directories plus the vacuity guards moved into a fourth job under `--dependency=afterok:`.

🔴 **State at close of day: `4thJ_gates_step1_uk.py` carries M-6 and M-7 but is untested; the Spain and
Italy runners are untouched; no job was submitted.** Full hand-off, including the acceptance tests that
decide whether the round is accepted, is in `Prompts/RESUME.md` under the 2026-08-16 21:30 block.

### 2026-08-16 — Round 2: M-6 and M-7 ported, `V1.a` moved out of the per-country runners, round ACCEPTED

Employee fragment merged from `outputs_step1/run_20260816-2140/proglog_entries_round2.md`. The gate
results and their acceptance are in `4thJ_01_corpusAcquisition_val.md`; what follows is the
implementation record.

**M-6 ported into Spain and Italy** from the UK reference implementation, which had carried it
untested. `resolve_manifest_path()` resolves every manifest entry relative to the manifest's own
`local_root`, **under `--raw` at invocation time**, never taking `local_path` literally, and keeps the
two problem strings verbatim: `md5 mismatch` and `recorded location not resolvable under --raw`. 🔴
`local_path` and `local_root` are read, never rewritten — they are provenance, and a manifest that
rewrites its own recorded location cannot testify about anything.

**M-7 ported for shape parity.** It did not engage for Spain or Italy this round and was not expected
to: neither country's `G1.4` FAILs at baseline, so there was no masked arm to recover. It engaged on
the UK, on all four arms, and the cluster's own report confirms it.

**One finding the employee reached from a dry run rather than from any document, and it is the useful
kind.** Spain's and Italy's raw trees keep unpacked files under an `unpacked/` sub-directory of the
country root — the layout the UK already had. M-6 needs `--raw` to be the **country root** (to match
`local_root`), while the runners' own raw re-reads need the **`unpacked/`** directory. Both runners now
split the two the way the UK file already did. 🔴 **This changes the invocation convention for Spain and
Italy** — round 1 passed the `unpacked/` directory as `--raw`, round 2 passes the country root. It is
the same class of bug M-6 exists to fix, and it was invisible in round 1 only because neither runner
had M-6 code yet to be wrong about `--raw` with.

**`tools/4thJ_vacuity_step1.py` written.** It scores `V1.a` **once per round** from the run-stamped
`--out` directory and writes `vacuity_report_step1.txt`. 🔴 **`V1.b`, `V1.c` and `V1.d` were deliberately
NOT moved** — they are properties of one country's own battery, and centralising them would make them
unfalsifiable.

**Run-stamped output directory adopted:** `outputs_step1/run_20260816-2140/`. Static reference inputs
are copied read-only into it; nothing is copied back into the flat `outputs_step1/` and nothing already
there was overwritten. This is what let `V1.a` pass on **this round's own parquets** rather than on
leftovers.

🔴 **A defect found in the round, fixed in code, not by re-running.** The per-country runners still
computed and printed `V1.a` themselves, at a moment when the other countries' jobs had not finished —
so Italy's and the UK's reports say `FIRED (2 of 3)` while the round-level report says `PASS (3 of 3)`.
The print is being removed from all three runners; `vacuity_report_step1.txt` is the authority. **The
battery is not re-run for it**, because no scored result changes. See the validation document for the
full reasoning.

**What was not independently verified**, carried forward from the employee's own account and not
resolved here: byte-identity between the cluster copies of the four tools and the local repo copies (no
md5 was run); byte-identity of the static reference files already sitting in the cluster's flat
`outputs_step1/`. Both are worth closing before Step 2 consumes these parquets, and neither affects the
gate verdicts read this round.

### 2026-08-16 — 🔴 **Merge 2 of 2 was REFUSED, correctly. D-S1-6: the manifest becomes a root-keyed union**

The employee sent to perform merge 2 of 2 **stopped and refused**, and it was the right call. Recorded
here in full because the refusal is more useful than the merge would have been.

**What it found.** The three files do not share a shape, on two independent grounds:

* `acquisition_manifest.json` is **Spain's manifest, flat at the JSON root** — there is no `"es"` key and
  there never was. `acquisition_manifest_italy.json` is flat in the same way.
* `acquisition_manifest_uk.json` is `{"_note": ..., "uk": {...}}`, and its own `_note` **assumes** the
  root manifest is already `{"es": ..., "uk": ...}`. It never was. The note documented a merge that
  could not be performed as written.
* Worse, the UK's per-file provenance is **not a `files[]` array at all**: it is `outer_archive`,
  `inner_archive` and `delivered_files_md5[17]`, because that delivery arrived as one nested archive
  rather than a set of separately downloaded files. Its own `shape_deviation_note` says so deliberately.
  **"Number of archive entries" is therefore not a common quantity**, and the verification the task
  asked for — input counts summing to the output count — was not defined.

Counts observed, for the record and **not summed**: Spain `files[]` 8 (+1 external reference); Italy
`files[]` 4; the UK 1 outer + 1 inner + 17 delivered md5s.

🔴 **A merge performed here would have invented a reconciliation, and the invented part would have been
the provenance.** That is the one thing this manifest exists to carry.

**D-S1-6, the manager's decision.** `acquisition_manifest.json` becomes a **root-keyed union**,
`{"es": ..., "it": ..., "uk": ...}`, with **each country's entry carried across unchanged, including its
own field names.** The UK keeps `outer_archive`/`inner_archive`/`delivered_files_md5`; Spain and Italy
keep `files[]`. **No shape normalisation, none at all**, and every `local_path` and `local_root` survives
verbatim. Spain's flat file is copied to `acquisition_manifest_spain.json`, which is what it should have
been called from the start, and the three fragments remain the per-country record.

**Three consequences, and the third is the expensive one.**

1. Each gate runner reads `acquisition_manifest.json` and indexes into its own country key. Everything
   downstream of the unwrapping is untouched — this changes *where the entry is found*, not *how it is
   read*.
2. 🔴 **A runner that cannot find its country key must raise and stop, never fall back to reading the
   file flat.** A silent fallback would let `G1.6a` keep passing on the old shape forever, which is the
   quiet form of the defect and the harder one to notice.
3. 🔴 **The battery is re-run as round 3, and that is not optional.** `G1.6a`'s input file changed shape,
   so its basis changed, and **a basis change is not an additive fix.** Shipping a manifest no gate has
   read in its new shape would be exactly the "gate that cannot fail" this project keeps writing guards
   against. The `V1.a` print fix rides along for free — which incidentally reverses the earlier decision
   *not* to re-run for it, and removes the contradiction from the archive rather than annotating it.

**What round 3 must show, or it is rejected:** `G1.6a` still PASSes on all three countries reading the
merged manifest; `corrupt_archive_byte` still fells `G1.6a` on all three; `strip_url_from_manifest` still
fells `G1.6b` on the UK; **Italy's `G1.6b` and the UK's `G1.4` `4276` baseline FAILs are both still
there**; `V1.a` PASSes 3 of 3 from the round-level report; and the three per-country reports contain **no
`V1.a` verdict line at all**.

**The `V1.a` print removal is done** (fragment `run_20260816-2140/proglog_merge2_and_v1a_fix.md`), with
the computation and both print sites gone from all three runners — `grep -n "v1a"` returns nothing — and
`V1.b`/`V1.c`/`V1.d` verified untouched.

**Carried forward, not verified:** the three edited runners were **never syntax-checked** — the edits are
textual and no python was run anywhere, per the login-node rule. A parse error would surface as a failed
round-3 job rather than as a bad result, which is the acceptable failure mode, but it is recorded rather
than assumed. Also unverified: md5 identity of the scp'd run-stamped directory (byte sizes only were
compared, 32 of 32 matching), and whether any now-unused import became dead code in the three runners.

### 2026-08-16 (later) — D-S1-6 executed: the union manifest is built, verified and round 3 is submitted

Merged from `outputs_step1/run_20260816-2140/proglog_manifest_union_and_round3.md`.

**The union was built and checked twice, not once.** Spain's pre-merge flat file was copied to
`acquisition_manifest_spain.json` (the name it should always have had), the existing backup was
confirmed non-empty and byte-identical before anything was written, and the union
`{"es":…, "it":…, "uk":…}` was written with **no shape normalisation**: Spain and Italy keep `files[]`,
the UK keeps `outer_archive`/`inner_archive`/`delivered_files_md5`. Entry counts matched
fragment-to-merged on all three (es 8/8, it 4/4, uk 19/19 = 1 outer + 1 inner + 17 delivered), and
`local_path`/`local_root` were compared **both on the parsed JSON and on the raw file text**, 17 strings
in total, 0 differences and 0 missing. The UK fragment's `_note` was dropped and quoted in full in the
fragment, so the wrong assumption it recorded is preserved rather than deleted.

🔴 **The runner edits refuse rather than fall back, and that is the load-bearing detail.** Each of the
three gate runners now indexes its own country key and `raise SystemExit` if the key is absent. The
tempting alternative — fall back to reading the file flat when the key is missing — would let `G1.6a`
keep passing forever on the old Spain-only shape, which is exactly the class of silent success this
round exists to remove. Nothing downstream of the unwrapping was touched: the md5 logic,
`resolve_manifest_path()` and both M-6 problem strings are byte-for-byte unchanged, and the UK runner's
existing `man.get("uk", {})` call sites were left alone rather than rewritten.

**All three files `py_compile` cleanly**, which also closes the "never syntax-checked" hole recorded
against the previous employee.

**Round 3 submitted**, stamp `run_20260816-2210`, `-p ps -t 7-00:00:00` throughout: ES 1252724,
IT 1252726, UK 1252727, vacuity 1252728 on `afterok` of the three. The `--raw` convention from round 2
(country root, not `unpacked/`) is unchanged; the only content change to the job scripts is that Italy
and the UK now copy the union `acquisition_manifest.json` into the run directory instead of their old
per-country fragment filename.

**What the employee explicitly did not verify, carried forward rather than dropped:** no round-3 report
was read by that employee, so nothing in its "what the manager will check" section is a result; the
edited runners were never *executed* anywhere before submission; the recorded md5s were not
independently recomputed against the files on disk, which is `G1.6a`'s own job; and the UK's `G1.6a`
loop body was not re-read line by line to confirm it iterates exactly outer + inner + delivered and
nothing else, so the UK entry-count check rests on an assumed counting rule. The Spanish and Italian
counting rules **were** read from source (`4thJ_gates_step1_spain.py:471`,
`4thJ_gates_step1_italy.py:321`).

### 2026-08-16 (later) — round 3 read for Italy and the UK: the merge held

Read directly from `run_20260816-2210/gate_report_step1_italy.txt` and `..._uk.txt`, not from a summary.
Four of the five acceptance points already hold on these two countries:

* **`G1.6a` PASS on both, reading the union.** Italy resolves 4 archives under
  `--raw=/speed-scratch/o_iseri/4J/raw/italy`, `problems: []`; the UK resolves outer + inner + 17
  delivered files, `problems: []`.
* **`corrupt_archive_byte` still fells `G1.6a`** on both — Italy `newly-failed ['G1.6a']`, the UK
  `failed ['G1.4','G1.6a']` with `already failing at baseline, not newly moved: ['G1.4']`, which is the
  M-7 attribution doing its job.
* **`strip_url_from_manifest` still fells the UK's `G1.6b`.**
* 🔴 **Both expected baseline FAILs are still there** — Italy `gates FAIL: 1` (`G1.6b`), the UK
  `gates FAIL at baseline: ['G1.4']`. Either of them clearing would have meant the merge broke something
  and the round would have been rejected.
* **The per-country `V1.a` verdict line is gone** on both, replaced by the one-line pointer to
  `vacuity_report_step1.txt`.

Spain (1252724) was still RUNNING and the vacuity job (1252728) still PENDING on its dependency when
this was written, so **the round is not yet accepted**: point 5 needs `V1.a` PASS 3 of 3 from the
round-level report, and Spain's own report is unread.

### 2026-08-16 (later still) — 🟢 **Step 1 round 3 is ACCEPTED**, `run_20260816-2210`

Spain (1252724, 00:18:21) and the round-level vacuity job (1252728, on `afterok` of all three) both
COMPLETED. All five acceptance points recorded before the round was submitted were checked against the
reports themselves, not against a summary.

1. **`G1.6a` PASS on all three, reading the union manifest.** Spain: *"8 archives checked, resolved
   under `--raw=/speed-scratch/o_iseri/4J/raw/spain` (M-6, never `local_path` taken literally), md5
   recomputed from disk vs recorded, independent of any URL; problems: []"*. Italy 4 archives, the UK
   outer + inner + 17 delivered, both `problems: []`. **D-S1-6's merge did not cost a single md5.**
2. **`corrupt_archive_byte` still fells `G1.6a`** on all three.
3. **`strip_url_from_manifest` still fells `G1.6b`** — Spain and the UK.
4. 🔴 **Both expected baseline FAILs survived the merge**: Italy's `G1.6b` and the UK's `G1.4`
   (`4276`). This was the point that could have rejected the round. A merge that silently *fixed* a
   known FAIL would have meant the runner had stopped reading the thing it audits, and the round would
   have been thrown away rather than celebrated.
5. **`V1.a` PASS 3 of 3 at round level** — `countries with an episodes_<country>.parquet present:
   ['ES','IT','UK'] (3 of 3)`, `missing: []`, threshold *FAIL below 3 of 3*, scan restricted to this
   run's own `--out` dir. And the per-country reports carry **no `V1.a` verdict line**, only the
   pointer (Spain, line 37: *"scored once per round in `vacuity_report_step1.txt`; deliberately not
   computed here"*). The round-2 defect — one guard printed in two places with two answers — is gone,
   and it was fixed by deletion, not by relabelling.

**Spain's own battery is unchanged by the merge**: 15 gates scored, 15 PASS, 0 FAIL, **15 of 15 seen
failing**, coverage clause satisfied. `G1.7b` remains `NOT CHECKED` and is excluded from the scored
set — unchanged from round 2, and still not a pass.

**Standing Step-1 state after this round: `G1.6b` FAILs for Italy and `G1.4` FAILs for the UK. Neither
is a defect in the battery; both are real properties of the delivered data and are quoted as such
wherever Step 1 is cited. Step 1 is closed for Step 2's purposes.**
