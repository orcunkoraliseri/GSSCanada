# 4J — EMPLOYEE TASK: bring the Spanish reader and the Step 1 gate battery up to specification, then re-run

### Hand this to a **fresh** employee session as its first message. Do not resume a long thread.
#### Written 2026-08-14 by the manager. Scope: `4thJ_read_spain.py`, `4thJ_gates_step1_spain.py`, and one full re-run of the Step 1 battery on Spain.

---

## YOUR ROLE

You are the **employee**. You execute exactly what is written here, in order, and you stop. You do not
redesign a gate, you do not move a threshold, you do not add a country, and you do not improve the
specification. **If the specification is wrong, you write the finding down and stop.** A gate that
fails is a result, not a bug to be worked around.

Read these two documents before you touch anything. They are the specification; this prompt is a
work order, not a paraphrase you may implement instead:

* `../Step1_docs/4thJ_01_corpusAcquisition.md` — the work items and the **intermediate record
  contract**
* `../Step1_docs/4thJ_01_corpusAcquisition_val.md` — **twelve** gates, the perturbation table, the
  coverage clause, the vacuity guards, and the progress log explaining why G1.7 was redesigned

---

## 🔴 STATE BEFORE YOU START

Step 1 ran on Spain on 2026-08-14 and **the probe FAILED.** Ten gates scored, ten PASS — and the
coverage clause caught that `G1.7a` had never been made to fall by anything in the perturbation set.
The manager redesigned the gate. **The runner still implements the old one.**

Since that run, three things changed in the specification and none of them is in the code:

1. **`G1.7` became `G1.7a` / `G1.7b` / `G1.7c` / `G1.7d`.**
2. **`G1.11` was added** and **`G1.4` was widened**, after the author decided finding F-ES-6.
3. **The intermediate record contract gained `act2_raw`**, and the Spanish reader's own parse report
   currently prints `NOT CARRIED: ASECU`.

**Step 1 is not done and will not be done until the whole battery has been re-run against the current
specification, coverage clause included.**

---

## 🔴 THE ONE IDEA BEHIND EVERY CHANGE BELOW

The old `G1.7` compared a weighted total against a published population — and INE calibrates its
weights *to that very figure*. **A gate whose reference derives from the source it audits cannot
fail.** It sat green for a whole run while measuring nothing.

Every new check below therefore reaches its reference through **a path the defect cannot travel**:

* `G1.7c` and `G1.7d` and `G1.11` **re-read the raw fixed-width files themselves.**
* 🔴 **They must not import anything from `4thJ_read_spain.py`** — not its layout tables, not its
  parsing helpers, not its output. A check fed by the reader cannot detect a reader that read the
  wrong column, and that is the exact defect these gates exist for.
* **Re-declare the byte offsets inside the gate runner, transcribed from the record-layout workbook**,
  and **print them** so a human can compare the two declarations by eye. Two independent
  transcriptions that agree are evidence; one transcription used twice is not.

If you find yourself writing `from 4thJ_read_spain import ...` in the gate runner, stop and re-read
this section.

---

## HARD RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`. Never bare `python` on the login node,
  not even a one-line import check. Every job requests `-t 7-00:00:00 --partition=ps`. Flagged three
  times on this account; a fourth is suspension. **This task can run locally and probably should** —
  the Spanish archives are on the local workstation and the file is small.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell. Use `wc -l`.
* Verify a backup is non-empty (`[ -s "$BK" ]`) before truncating anything.
* **Do not create files that are not listed under a Definition of done below.**
* Do not touch `codebook_facts_spain.md`. It is a record of what the codebooks say, and nothing you
  do here changes what they say.

---

## TASK 1 — The reader carries the secondary activity and the country-extra flag

`4thJ_read_spain.py` reads `ASECU` and then discards it, printing `NOT CARRIED`. The record contract
now includes it, so it is carried.

### 1.1 Add `act2_raw`, with three states kept distinguishable

🔴 **This is the part that is easy to get subtly wrong, and no downstream gate other than `G1.11`
would notice.** Three states must survive into the parquet and stay separable:

| State | Meaning | Representation |
|---|---|---|
| **not recorded** | the instrument does not field a secondary activity at all | `pd.NA` |
| **recorded and blank** | the instrument fields it and this slot has none | `""` (empty string) |
| **recorded with a value** | a code | the 3-character code |

Use a pandas **`string`** dtype so `pd.NA` and `""` do not collapse into each other. 🔴 **An object
column round-tripped through parquet is exactly where the two silently merge**, and a reader that
merges them moves no row and emits no illegal code — nothing except `G1.11` can see it.

For Spain, `ASECU` is fielded, so **no Spanish row is `pd.NA`.** The `pd.NA` state exists for the
three countries not yet acquired, and the column must support it now rather than be widened later.

Aggregate to episode level the same way `act_raw` is aggregated. Record in the parse report how many
episodes fall in each of the three states.

### 1.2 Rename `cop_padres` to `cop_extra_es_padres`

D-S2-2 names country-extra co-presence flags `cop_extra_<country>_<field>`. The reader currently emits
`cop_padres`. Rename it. 🔴 **`PADRES` is never folded into the shared "other household members"
flag** — it is a distinct national concept and the whole point of the extra column is that it stays
distinct.

### 1.3 Re-emit

Re-run the reader. `episodes_spain.parquet` and `parse_report_spain.txt` are both replaced.
**Back both up first and check the backup is non-empty before overwriting.**

🔴 **The diary, slot and episode counts must not change**: 19,295 diaries, 2,778,480 slots, 430,754
episodes. If any of them moves, adding a column changed the parse, and that is a finding — **write it
down and stop.**

---

## TASK 2 — The gate runner implements the current twelve gates

Work through the gate table in the validation document. It is the specification; what follows is the
list of what changed, not a replacement for reading it.

### 2.1 `G1.4` — widened

Test `act2_raw` for code-list membership alongside `act_raw` and `loc_raw`. 🔴 **A blank is not a code
and is not tested against the list.** Exclude blanks from the membership test, then print, separately
and per country, the counts of *not recorded*, *recorded and blank*, and *recorded with a value*.

### 2.2 `G1.7a` — kept, tightened

Present, finite, strictly positive on 100 % of rows, **and more than one distinct value**. The
distinct-count clause is the new half: a column read as a constant is the likeliest shape of "read the
wrong bytes", and positivity alone waves it straight through.

### 2.3 `G1.7b` — retired, and it stays visible

Permanently `NOT CHECKED`. **Never scored, never counted as a pass, and never deleted.** Keep printing
both numbers — the weighted estimate and INE's published total — labelled explicitly as evidence of
nothing, with the reason (METH p. 34, step 3: the estimator is ratio-adjusted to the population
projection in each stratum).

🔴 **Do not delete it and do not repair it.** A retired gate that vanishes from the report takes the
knowledge of its hole with it, and the next session re-invents the same circular check.

### 2.4 `G1.7c` — cross-file weight identity. **This is the actual replacement**

One survey weight per person, restated by INE in four delivered files. It must be **bit-identical in
all four** for 100 % of respondents.

* Spain: `FACTORF` in `CINDIV`, `DIARIO1`, `DIARIO2`, `MHOGAR`. **The four files declare it at
  different byte offsets**, which is what gives the check its power: an offset error in one file
  cannot produce the same wrong value in another.
* **Read all four from the raw fixed-width files, in the gate runner, with offsets you transcribed
  yourself.** Compare as **raw strings before any numeric conversion** — "bit-identical" means the
  characters, not two floats that round to the same value.
* A country whose delivery carries the weight in only one file is **`NOT CHECKED`, printed, never a
  pass.**

### 2.5 `G1.7d` — magnitude against the declared layout

Every weight strictly below the maximum the layout's integer width allows — Spain declares 6 integer
digits, so `< 1e6` — and at or above `1.0`. **A weight under 1 represents less than one person, which
no design produces.** Print observed min, max and distinct count **before** the verdict.

🔴 **Its reference is the layout document, a different artefact from the microdata being audited.**
That is the property `G1.7b` never had, and it is the reason this gate is worth having.

### 2.6 `G1.11` — secondary-activity three-state integrity

Count the slots carrying a **non-blank** `ASECU` **by re-reading the raw fixed-width file** with your
own transcribed offsets, and require it to equal the count in the emitted episode table. **Exact, no
tolerance.**

🔴 **The Spanish figure of 340,269 of 2,778,480 is the reader's own number. It is the quantity under
test, not the reference.** The reference is your independent recount. Do not hard-code 340,269 as an
expected value anywhere — if you do, you have rebuilt `G1.7b` in a new place.

A country that does not field the variable is `NOT CHECKED`, printed, never a pass.

---

## TASK 3 — The perturbation set

Each perturbation is applied **to a copy** of the parsed data, in memory, and must break **exactly
one** gate. The table in the validation document is the specification. What changed:

* **Struck:** *multiply one weight column by 10*. It broke nothing — it cannot change a sign, and the
  only gate it moved was `G1.7b`, which cannot fail. Remove it **and record why in the progress log**,
  so it is not helpfully reinstated later.
* **Set one respondent's weight to `-1`** → `G1.7a` alone.
* **Overwrite the whole weight column with one constant** → `G1.7a`, distinct-count clause.
* 🔴 **Replace one respondent's `FACTORF` in `CINDIV` with another respondent's valid `FACTORF`** →
  `G1.7c` alone. The value is positive, correctly formatted and inside range; it is simply the wrong
  person's. **Nothing else in the battery can see it, and that is the measure of what `G1.7c` adds.**
* **Divide one respondent's weight by 10⁴ in every file that carries it** → `G1.7d` alone. Applying
  the edit consistently is what keeps `G1.7c` clean; that is the point of the case.
* **Set one `act2_raw` to `999`** → `G1.4`.
* 🔴 **Rewrite every blank `act2_raw` as a code, or every code as blank** → `G1.11` alone.
* **Null perturbation: change nothing** → **nothing may fail.**

### The coverage clause — this is what failed last time

After the set has run, cross-tabulate every perturbation against the baseline and **FAIL the probe if
any gate that PASSes on the real data was never made to fall by anything in the set.**

🔴 **`NOT CHECKED` gates are exempt, and only because `NOT CHECKED` is printed on every run and never
counted as a pass.** A gate that quietly disappeared from the report would not qualify.

**Three perturbations are already known not to attribute** — anything that removes rows also fells
`G1.5`. That is recorded in the progress log as a property of `G1.5`, not a defect to be tuned away.
**Do not "fix" it by weakening `G1.5`.** Report it again if it recurs.

---

## VACUITY GUARDS — verify these still hold after your edits

* **V1.a** — FAIL if fewer than 4 countries were scanned. **It will fire. It must fire.** One country
  of four. Report it; do not add a single-country escape flag.
* **V1.b** — print row counts, the file list and every md5 **before** any verdict.
* **V1.c** — read each gate's exit status from the process that computed it. 🔴 A check that cannot
  distinguish *found nothing* from *could not run* is not a check.
* **V1.d** — any code, unit or column name the reader does not recognise is **printed and refused**,
  never assumed harmless.

---

## DEFINITION OF DONE

1. `../tools/4thJ_read_spain.py` carries `act2_raw` with three separable states and emits
   `cop_extra_es_padres`.
2. `../Step1_docs/outputs_step1/episodes_spain.parquet` and `parse_report_spain.txt` re-emitted, with
   the three counts printed and **19,295 / 2,778,480 / 430,754 unchanged**.
3. `../tools/4thJ_gates_step1_spain.py` implements all twelve gates as specified, importing nothing
   from the reader for `G1.7c`, `G1.7d` or `G1.11`, and printing both offset transcriptions.
4. The full battery re-run, baseline plus every perturbation plus the null, with the coverage clause
   evaluated and its verdict printed. Output replaces
   `../Step1_docs/outputs_step1/gate_report_step1_spain.txt`.
5. A progress-log entry **appended** to `../Step1_docs/4thJ_01_corpusAcquisition_val.md` recording:
   the baseline table, which gates were seen failing and under what, the coverage-clause verdict, the
   struck perturbation and its reason, and anything that did not attribute.
6. A progress-log entry **appended** to `../Step1_docs/4thJ_01_corpusAcquisition.md` recording the
   reader change.

---

## WHAT IS NOT YOURS TO DECIDE

* **Do not move a threshold.** Every one is pre-registered.
* **Do not resurrect `G1.7b`**, and do not replace it with another comparison against a published
  population. No offline check can establish that the weights are *right*, `G1.7b` only appeared to,
  and the honest boundary is already written into the validation document.
* **Do not hard-code 340,269**, or any other number the reader produced, as a gate's reference.
* **Do not acquire, download or register for anything.** UK, France and Italy are the author's, in
  person.
* **Do not condition anything on `act2`** beyond `G1.4` and `G1.11`. Until
  `outputs_step3/act2_coverage.md` exists with four measured rates, the field is carried and not used.
* 🔴 **If the coverage clause FAILs again, that is the deliverable.** Report which gate was never
  shaken and stop. **Do not invent a perturbation to make it green** — the point of the clause is that
  it refuses a pass nothing has tested, and a perturbation written to satisfy it after the fact
  defeats exactly that.
