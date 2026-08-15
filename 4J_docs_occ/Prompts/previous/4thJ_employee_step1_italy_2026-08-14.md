# 4J — EMPLOYEE TASK: bring **Italy** through Step 1, codebook to gate battery

### Hand this to a **fresh** employee session as its first message. Do not resume a long thread.
#### Written 2026-08-14 by the manager. Scope: ISTAT *Uso del tempo* 2013-2014 only. **Do not touch Spain, the UK or France.**

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
  only.** Spain is a fixed-width relational delivery and Italy is not. Copy the discipline, never the
  parsing.

---

## 🔴 THE ONE IDEA BEHIND THIS WHOLE TASK

**Spain is not the template for the data. It is only the template for the rigour.**

The Spanish reader was written first because it fixed the record contract. It is now very easy to
assume the Italian delivery is Spain with Italian column names. It is not, and the differences below
are already measured. **Every fact you write must come from ISTAT's own documentation**, not from the
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

Everything is in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Datasets\IT TUS\`:

| File | What it is |
|---|---|
| `uso_tempo_2013_IT.zip` | 🔴 **THE DATA.** Microdata + record layouts + code lists, 2013-14 wave |
| `Nota_metodologica-2013.pdf` | 🔴 **THE METHODOLOGY**, 38 pp., *"Periodo di riferimento: anno 2013-2014"* |
| `Nota_metodologica.pdf` | 7 pp. — the **2023 volunteering module**. Not ours |
| `UsoTempo_2023_IT.zip` | 🔴 **NOT A DIARY.** Contains only `UsoTempo_Microdati_2023_Volontariato` |

🔴 **Use only `uso_tempo_2013_IT.zip` and `Nota_metodologica-2013.pdf`.** The 2023 pair is the
volunteering module of a later wave: it has **no time-use diary in it at all**, and decision 4 fixes
one wave per country. Record in `codebook_facts_italy.md` that they were present and excluded, and why.
**Do not read them into anything.**

1. Unpack `uso_tempo_2013_IT.zip` to
   `C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\4J\raw\italy\`, mirroring how Spain sits at
   `..\raw\spain\` (archives kept, `unpacked\` beside them). Copy the two PDFs there as well.
2. **md5 every archive and every delivered data file.** 🔴 **Do not edit
   `acquisition_manifest.json`.** Another employee is working on the UK in parallel and would overwrite
   you. Instead write a fragment to
   `../Step1_docs/outputs_step1/acquisition_manifest_italy.json`, containing **only** the `italy`
   entry, in exactly the structure the existing Spanish entry uses in `acquisition_manifest.json` —
   read that file to copy its shape, but do not write to it. The manager merges the fragment.
3. Record the URL and download date. The author obtained these from ISTAT on **2026-08-14**. 🔴 **If
   the delivery does not print its own source URL, record what it does print and mark the rest
   `NOT FOUND`** — do not reconstruct a plausible ISTAT URL from memory.
4. Record the licence / access condition exactly as ISTAT states it. `Nota_metodologica.pdf` describes
   its file as *"File di microdati per la ricerca"* (mFR); establish what the **2013-14 diary** release
   is, from its own documentation. 🔴 This matters beyond Step 1 — Step 5's release decision turns on
   it — and mFR and public-use files carry **different** redistribution terms.

🔴 **The plan's work item 1.1 says the Italian copy is "HELD already from paper 1 — confirm the held
copy is the same wave and the same extract."** This is a fresh download, not the paper-1 copy. Record
that. If a paper-1 Italian extract is not present on this workstation, write that it could not be
compared and move on — **do not go looking for it.**

---

## TASK 1 — `codebook_facts_italy.md` (work item 1.2)

**Write this before you write one line of reader code.** This is the whole point of work item 1.2, and
it is the step where Spain's real findings came from.

Your sources, and you must cite which:

* `METADATI/uso_tempo_Tracciato_Anno 2013_DiarioGiornaliero.html` — the daily-diary record layout
* `METADATI/uso_tempo_Tracciato_Anno 2013_Individui.html` — the individual file layout
* `METADATI/Classificazioni/*.html` — the code lists, one per coded variable
* `METADATI/uso_tempo_Questionario_Diario_Giornaliero__Anno 2013.pdf` — the instrument
* `METADATI/HelpTracciato_DELIMITED.html` — 🔴 **read this first.** It states how the delimited files
  are to be read, and it is the document that tells you what a blank field means
* `Nota_metodologica-2013.pdf` — sampling, fieldwork, **and the weighting methodology**. Section
  *"La metodologia di calcolo dei pesi campionari"*. See TASK 3.4

🔴 **These files are `cp1252`-encoded, not UTF-8.** Decoding them as UTF-8 mangles every accented
character and will corrupt the labels you transcribe. Verify the encoding rather than assuming either
way, and record what you found.

Reproduce every row of the `codebook_facts_spain.md` fact table for Italy: file shape, native
`START`/`DURATION`, weight variable names, activity coding list and its **edition and depth**, location
coding list, co-presence fields **and how many**, slot length, diary origin hour, minimum age, diary
days per respondent, collection mode. Then add the counts table — see G1.1 below.

### 🔴 Five things about Italy that are already measured, and that you must resolve properly

These came from the manager's inspection of the delivery. Each is a place where copying Spain silently
produces a wrong file.

**1.1 — It is tab-delimited with a header row, not fixed-width.** The first line of
`MICRODATI/uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt` is the variable names. Spain's byte
offsets have no analogue here. Do not build a fixed-width parser.

**1.2 — The diary is native episodes with explicit clock times**: `ordepi` (episode number),
`oraini`/`minini` (start hour/minute), `orafin`/`minfin` (end hour/minute). Spain is 144 fixed 10-minute
slots reconstructed with a first-of-run rule; **Italy ships episodes already.** Do not reconstruct.

🔴 **`duration_min` must be computed from the start and end times, and the diary day wraps.** The first
observed episode starts at 04:00, so an episode ending at 03:50 the following morning is a *later*
episode, not a negative duration. Establish the origin hour from the documentation, cite it, and make
the wrap explicit in the code. A silently negative or 1440-off duration is exactly what `G1.2` exists
to catch — **let it catch it, do not pre-empt it with a clamp.**

**1.3 — The secondary activity is on a COARSER list than the primary.** `catpri` is **3 digits**;
`catcon` is **2 digits** with roughly 34 modalities (`01`, `02`, `03`, `11`, `12`, … `95`). Spain's
`ASECU` shares the primary's list. 🔴 **They are two different classifications and `catcon` codes must
be validated against `catcon`'s own list, never against `catpri`'s.** Validating one against the other
would fail every row, or worse, pass by coincidence on the two-digit prefixes.

Write this up as a finding (`F-IT-n`): the cross-national secondary-activity classification is not
common, and what Step 2 does about it is the manager's decision, not yours.

**1.4 — Co-presence is eight fields**: `daso` (alone), `cmadre`, `cpadre`, `cconiu`, `cfigli`,
`cfrate`, `afacon`, `aperco`. Spain fields six. The contract's `cop_raw[5]` holds five. Follow the
Spanish precedent exactly: **emit every recorded flag as its own named column, never fold one into
another**, and record the mapping and the count as a finding. 🔴 Note that Italy separates *mother* and
*father* where Spain has a single `PADRES` — that is a real difference and it is the manager's to
harmonise at Step 2.

**1.5 — Blank is a real, recorded state and it is literally spaces.** The first diary episode has
`catcon` = `"  "` (two blanks) in a tab-delimited field. This is the *recorded and blank* state and it
must not become "missing". See the three-state rule in TASK 2 — this is the country where getting it
wrong is easiest, because a delimiter-separated blank looks like nothing at all.

### Also establish, and do not skip

* **Diary days per respondent.** Spain measures 1. Measure Italy and assert it against the codebook
  (gate `G1.9`). If it is more than 1, every per-diary gate below is **per diary-day**.
* **Diary origin hour.** Spain's is 06:00 (finding F-ES-1). Find Italy's and cite it.
* **Minimum age.** Spain's is 10. Find Italy's.
* **The weight variable.** 🔴 **There is no weight column in the daily-diary layout.** Find where the
  weights live — the `Individui` file, most likely — name them exactly, and establish whether any
  weight is restated in more than one delivered file. This determines `G1.7c`; see 3.5.
* **Which files you are NOT reading.** `DiarioSettimanale` (the weekly diary) is not an input to this
  pipeline. Record it as not read, with the reason, the way Spain recorded `HTR1`/`HTR2`/`SD`.

**Definition of done:** `../Step1_docs/outputs_step1/codebook_facts_italy.md`, plus
`crosswalk_source_italy_activity.csv` and `crosswalk_source_italy_location.csv` transcribed from the
`Classificazioni` files, matching the Spanish files' shape. 🔴 **Transcribe `catcon`'s list too**, as a
third file `crosswalk_source_italy_activity2.csv`, because it is a genuinely separate classification.

---

## TASK 2 — `4thJ_read_italy.py` (work item 1.3)

One reader per country is expected. Write `../tools/4thJ_read_italy.py`. It emits the **same
intermediate record** as Spain:

```
country, wave, hid, pid, diary_day, episode_index,
start_min, duration_min, act_raw, act2_raw, loc_raw,
cop_raw[5], cop_extra_<country>_<field> ...,
mode, scheme, weight_ind, weight_dia
```

* `country` = `"IT"`.
* `wave` = the wave as ISTAT states it (the methodology says 2013-2014; the file's `anno` column says
  2013 — 🔴 **record both and say which you used and why**).
* `hid` / `pid`: build from `profam` and `proind`. 🔴 **Keep them as strings.** They are zero-padded
  (`000001`, `01`) and converting to integer destroys the padding and can collide across the file.
* `mode` and `scheme` are constant per country and are carried so no later step guesses them. Take
  them from the codebook, not from Spain's values.
* `weight_ind` / `weight_dia`: from wherever TASK 1 established the weights live, joined on the
  person key. 🔴 **If the diary and the individual file do not join cleanly for every episode, that is
  a finding — report the unmatched count and do not drop the rows silently.**

### 🔴 The three-state rule, which is the easiest thing here to get subtly wrong

Three states must survive into the parquet and stay separable for `act2_raw`:

| State | Meaning | Representation |
|---|---|---|
| **not recorded** | the instrument does not field it at all | `pd.NA` |
| **recorded and blank** | the instrument fields it and this episode has none | `""` (empty string) |
| **recorded with a value** | a code | the code, as a string |

Italy fields `catcon`, so **no Italian row is `pd.NA`** — the blanks are the *recorded and blank*
state. Use a pandas **`string`** dtype. 🔴 **An object column round-tripped through parquet is exactly
where `pd.NA` and `""` silently merge**, and a reader that merges them moves no row and emits no
illegal code — nothing except `G1.11` can see it.

🔴 **A tab-delimited file read with pandas defaults destroys this distinction before you reach the
dtype question.** `"  "` becomes `NaN` under default NA handling. Read with `keep_default_na=False`,
`dtype=str`, `sep="\t"`, and the encoding you established. Then decide, **from
`HelpTracciato_DELIMITED.html` and not from taste**, whether a field of spaces should be stripped to
`""` — and whichever you decide, apply it identically in the reader and, independently, in the gate
runner, and state it in both reports.

### Parse completeness

It **itemises everything it could not parse and fails on it.** A reader that returns `0.0` or silently
drops a row it does not understand blames the system under test for its own gap — that cost 16
spurious FAILs in 3J. It never infers a value it did not read.

**Definition of done:** `../Step1_docs/outputs_step1/episodes_italy.parquet` and
`parse_report_italy.txt`, the parse report naming every dropped or unparsed row and printing the
three-state counts for `act2_raw`.

---

## TASK 3 — `4thJ_gates_step1_italy.py`: the fourteen gates on Italy

Work through the gate table in the validation document. It is the specification. What follows is what
is **Italy-specific**, not a replacement for reading it.

### 🔴 3.0 — The independence requirement, restated for a delimited file

`G1.7c`, `G1.7d` and `G1.11` exist to catch **a reader that read the wrong column**. So:

* 🔴 **The gate runner must not import anything from `4thJ_read_italy.py`** — not its column maps, not
  its helpers, not its output. A check fed by the reader cannot detect the reader.
* Spain's version of this was re-transcribing byte offsets. Italy is tab-delimited, so the equivalent
  is: **the gate runner identifies its columns independently, by name, from its own transcription of
  the `Tracciato` layout**, and **prints both the reader's column map and its own** so a human can
  compare them by eye. Two independent transcriptions that agree are evidence; one used twice is not.
* 🔴 **Resolve columns by name, never by position**, and **fail loudly if a name is absent** rather
  than falling back to an index.

### 3.1 — `G1.1` row-count reconciliation

Spain worked because INE prints its own record counts. **Find whether ISTAT prints episode, individual
and household record counts** — check `Nota_metodologica-2013.pdf` and the `Tracciato` files.

🔴 **If no delivered document states the counts, `G1.1` is `NOT CHECKED` for Italy — printed, never a
pass, never scored.** Do **not** substitute your own count as the reference; that is precisely the
circularity that retired `G1.7b`. Report it as a finding.

*(For orientation only, and not a reference: the manager measured the daily diary at 1,077,658 lines
and `Individui` at 44,867 lines, both including the header row.)*

### 3.2 — `G1.2` duration closure

Every diary must sum to 1440 minutes, 100 % of diaries, no exceptions. 🔴 **This is the gate most
likely to expose a wrap-around bug in your duration arithmetic**, and that is a good thing. If it
fails, find out whether the defect is your reader or the delivered data **before** you write anything
down — and if it is the data, report which diaries and how many, and stop.

### 3.3 — `G1.3` quantisation

100 % of durations are multiples of **10**. 🔴 **If Italy fails this, the wave is not admissible to the
Step 7 tally automaton and the finding is escalated, not resampled away.** Report the distribution of
offending durations; do not round anything.

### 3.4 — `G1.7b`, and the question you must actually answer

`G1.7b` is retired **for Spain**, because INE's estimator (METH p. 34, step 3) is ratio-adjusted to the
population projection, so the weights are calibrated to the very figure the gate compared them
against.

🔴 **Circularity is a property of the source, so it does not transfer and it does not exempt. You must
establish it for Italy from ISTAT's own weighting methodology** — `Nota_metodologica-2013.pdf`,
section *"La metodologia di calcolo dei pesi campionari"*.

* If ISTAT's weighting **is** calibrated to a population total or to age × sex margins, then `G1.7b` is
  `NOT CHECKED` for Italy for the same reason, **and you cite the page**, and `G1.8` is narrowed the
  same way Spain's was — read the `G1.8` row in the validation document before you decide what it can
  still detect.
* If it is **not** calibrated that way, `G1.7b` is a live gate for Italy and you score it.
* 🔴 **"Spain retired it, so Italy does too" is not an answer, and neither is "surveys are usually
  calibrated."** Cite the page or write `NOT FOUND` and mark the gate `NOT CHECKED` for lack of an
  established reference — which is a different reason, and you must say which reason applies.

Either way: **never delete a retired gate, and never score it as a pass.** Keep printing both numbers,
labelled as evidence of nothing, with the reason.

### 3.5 — `G1.7c` cross-file weight identity

Spain's power came from `FACTORF` appearing in four files at four different byte offsets. **Establish
whether any Italian weight is restated across more than one delivered file.**

* If yes: require bit-identity **as raw strings before any numeric conversion**, 100 % of respondents,
  read independently by the gate runner.
* 🔴 **If the weight is carried in only one file, `G1.7c` is `NOT CHECKED` — printed, never a pass.**
  That is already written into the gate. Do not invent a substitute check to make the report look
  fuller.

### 3.6 — `G1.7d` weight magnitude against the declared layout

Every weight strictly below the maximum the declared width allows, and at or above 1.0 — a weight
under 1 represents less than one person, which no design produces. Print observed min, max and
distinct count **before** the verdict.

🔴 The `Tracciato` declares a length and a decimal count per variable; **that declaration is your
reference**, and it is a different artefact from the microdata under test, which is the whole reason
the gate is worth having. If the declaration is absent, say so and mark `NOT CHECKED`.

🔴 **Test this against real Italian weights before you assume the ≥ 1.0 clause holds.** Some agencies
publish scaled or normalised weights with a mean of 1, which puts perfectly valid weights below 1. If
that is what ISTAT ships, **that is a finding and a specification question for the manager — not a
threshold for you to move.** Report it and mark the gate.

### 3.7 — `G1.8` demographic marginals

Weighted age × sex within ±1.0 pp per cell of Italy's own published table for that wave. 🔴 **Read the
narrowed `G1.8` row in the validation document first.** If ISTAT calibrates to age × sex (see 3.4), the
agreement on the complete file is imposed, not earned, and the gate detects only **a subsample
presented as the full file**. Record it that way rather than reporting a false clean pass.

If no published Italian table for the wave is in the delivery, `NOT CHECKED`, printed, and a finding.
**Do not go looking for one online** — literature and web search are out of scope by hard project rule.

### 3.8 — `G1.4` code-list membership

100 % of `act_raw`, `act2_raw` and `loc_raw` inside the edition declared in `codebook_facts_italy.md`.
🔴 **`act2_raw` is tested against `catcon`'s own 2-digit list, not against `catpri`'s** — see 1.3.
🔴 **A blank is not a code and is not tested against the list.** Print, separately, the counts of *not
recorded*, *recorded and blank*, and *recorded with a value*.

### 3.9 — `G1.11` secondary-activity three-state integrity

**Episode-level identity.** The count of episodes carrying a non-blank `catcon` in the emitted table
must equal the count obtained by **re-reading the delivered file inside the gate runner with its own
independent column resolution**, importing nothing from the reader. **Exact, no tolerance.**

🔴 **Do not hard-code any count the reader produced as the reference.** The reader's number is the
quantity under test. If you hard-code it, you have rebuilt `G1.7b` in a new place.

🔴 **Apply exactly the same blank/whitespace convention here as in the reader**, and say in the report
which convention it is. If the two differ, this gate will fail for a reason that has nothing to do with
the defect it exists to catch.

*(Note: Spain needed a first-of-run episode rebuild here because Spain is slot-level. Italy ships
episodes, so the recount is direct — but it must still be **independent**, which is the part that
matters.)*

---

## TASK 4 — The perturbation set and the coverage clause

Each perturbation is applied **to a copy** of the parsed data, in memory, and must break **exactly
one** gate. The table in the validation document is the specification; adapt each case to Italian
column names, **not to Italian convenience**.

Every case in that table applies, plus:

* 🔴 **Rewrite every blank `act2_raw` as a code, or every code as blank** → `G1.11` alone. No row
  moves and every code stays inside the list, so the defect is invisible to the rest of the battery.
* **Null perturbation: change nothing** → **nothing may fail.** 🔴 Keep this one. On Spain it caught a
  real defect in the employee's own gate code.
* 🔴 **Use a sentinel that is genuinely outside the Italian code list, and prove it is** by checking it
  against your transcribed list before you use it. On Spain the pre-registered `999` turned out to be
  a **real INE code** and the perturbation could not fire. Print the sentinel you chose and the check
  that it is absent. 🔴 **Remember `catpri` and `catcon` have different lists** — a sentinel outside one
  may sit inside the other.

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

1. `uso_tempo_2013_IT.zip` unpacked to `_local_runs\4J\raw\italy\`, every md5 recorded in
   `../Step1_docs/outputs_step1/acquisition_manifest_italy.json`, with URL, date and access condition,
   and the 2023 volunteering pair recorded as present and excluded.
2. `../Step1_docs/outputs_step1/codebook_facts_italy.md`, every fact cited to a document and page,
   `NOT FOUND` where it is not found, and the findings numbered `F-IT-1`, `F-IT-2`, …
3. `../Step1_docs/outputs_step1/crosswalk_source_italy_activity.csv`,
   `crosswalk_source_italy_activity2.csv` and `crosswalk_source_italy_location.csv`.
4. `../tools/4thJ_read_italy.py`, emitting `../Step1_docs/outputs_step1/episodes_italy.parquet` and
   `parse_report_italy.txt` with the three-state counts printed.
5. `../tools/4thJ_gates_step1_italy.py`, importing nothing from the reader for `G1.7c`, `G1.7d` or
   `G1.11`, printing both column-map transcriptions.
6. The full battery run — baseline, every perturbation, the null — with the coverage clause evaluated
   and its verdict printed, written to
   `../Step1_docs/outputs_step1/gate_report_step1_italy.txt`.
7. 🔴 **Do not edit `4thJ_01_corpusAcquisition_val.md` or `4thJ_01_corpusAcquisition.md`.** The UK
   employee is appending to the same two files in parallel and one of you would silently overwrite the
   other's entry. **Write your two progress-log entries to a single new file instead:**
   `../Step1_docs/outputs_step1/proglog_entries_italy.md`, containing two clearly headed sections —
   *"for `4thJ_01_corpusAcquisition_val.md`"* and *"for `4thJ_01_corpusAcquisition.md`"* — written as
   finished, append-ready progress-log entries in the same style as the existing ones. The manager
   appends them.
8. The validation entry must contain: the baseline table, which gates were seen failing and under
   what, the coverage-clause verdict, anything that did not attribute, and every gate you marked
   `NOT CHECKED` **with the reason**. The implementation entry records the Italian reader and what the
   delivery turned out to be.

---

## WHAT IS NOT YOURS TO DECIDE

* **Do not move a threshold.** Every one is pre-registered.
* **Do not validate `catcon` against `catpri`'s list**, and do not propose a mapping between them.
* **Do not fold any co-presence flag into another**, and do not merge `cmadre` and `cpadre`.
* **Do not touch the 2023 volunteering files** beyond recording that they exist and are excluded.
* **Do not resurrect `G1.7b`** for Spain, and do not assume its fate for Italy either way — establish
  it from ISTAT's own methodology and cite the page.
* **Do not hard-code any number the reader produced** as a gate's reference.
* **Do not acquire, download, or register for anything**, and **do not search the web or the
  literature.** France is with Progedo and is the author's, in person.
* **Do not touch the UK.** Another employee is working on it in parallel, in the same repository. Every
  file you create is Italy-named; if you find yourself editing a UK or Spanish file, stop.
* 🔴 **If the specification and the Italian delivery genuinely cannot both be satisfied, stop and write
  the finding.** That is a real deliverable and it is how Spain's four specification defects were
  found.
