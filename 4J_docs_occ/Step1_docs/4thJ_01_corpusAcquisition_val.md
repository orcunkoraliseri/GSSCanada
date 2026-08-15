# Step 1 — Corpus acquisition. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_01_corpusAcquisition.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**RUN ON SPAIN, 2026-08-14. Fourteen gates: thirteen scored, thirteen PASS, `G1.7b` permanently
`NOT CHECKED`. Every scored gate has been seen failing and the coverage clause is SATISFIED.**
Output: `outputs_step1/gate_report_step1_spain.txt`. 🔴 **The step is still not done: `V1.a` fires on
one country of four**, and it must fire until the UK, France and Italy files exist. A green battery on
one country is not a partial pass of Step 1; it is a full pass of the part of Step 1 that has data.

Every threshold below was pre-registered before Spain arrived, and none was moved when it did. **Four
corrections have been made to this document since**, all defects in the specification rather than in
the data, all in the progress log: the gate count (twelve → fourteen), `G1.11`'s basis (slot-level →
episode-level), the `999` sentinel that was a real INE code, and `G1.8` narrowed after INE's
methodology text was actually opened.

✅ **`G1.7b`'s retirement is verified against the primary source**, not against the citation that was
written from memory — `_local_runs/4J/raw/spain/meth_t25304471.pdf`, printed p. 34, step 3, quoted in
the progress log. 🔴 **The same reading showed `G1.8`'s reference is calibrated too** (CALMAR, pp.
35-36), which is why it is now narrowed to the one defect it can still detect.

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
| **G1.4** Code-list membership | Codes outside the declared coding list; an off-by-one column read | 100 % of `act_raw`, **`act2_raw`** and `loc_raw` inside the edition declared in `codebook_facts_<country>.md`. 🔴 **A blank `act2_raw` is not a code and is not tested against the list**; the runner prints, separately, how many episodes are *not recorded*, *recorded and blank*, and *recorded with a value*, per country | **project-chosen** |
| **G1.5** Parse completeness | 🔴 The reader silently swallowing what it does not understand | `parse_report` names **every** dropped or unparsed row, and the count of unexplained drops is **0**. A drop with a written reason is allowed; a drop without one is a FAIL | **project-chosen**, from 3J's most expensive reader lesson |
| **G1.6** Provenance | A file that cannot be traced to a source, or a hash computed after the fact | Every archive has an md5, a URL and a download date in the manifest, and the md5 recomputed from disk **matches** | **project-chosen** |
| **G1.7a** Weight presence and sign | A weight column absent, null, or read as text | Weight variables present on every declared file, **finite and strictly positive on 100 % of rows**, and **more than one distinct value** — a constant weight column is a column that was not read | **derived from the design** — an unequal-probability sample cannot have a constant weight |
| **G1.7b** ~~Weighted total vs published population~~ | — | 🔴 **RETIRED 2026-08-14. Permanently `NOT CHECKED`, never scored.** INE's estimator (METH p. 34, step 3) is ratio-adjusted to the population projection, so the weights are calibrated to the exact figure this compared them against. The estimate and the published total are still **printed** as a diagnostic, labelled as evidence of nothing | **circular** — the reference derives from the source it audits |
| **G1.7c** Cross-file weight identity | 🔴 **The defect G1.7 was named for: a weight column read from the wrong position** | The same respondent's weight is **bit-identical across every delivered file that carries it** (Spain: `FACTORF` in `CINDIV`, `DIARIO1`, `DIARIO2`, `MHOGAR`), for **100 %** of respondents. Recomputed by the gate runner **from the raw fixed-width files using the layout offsets**, never from the reader's own output. A country whose delivery carries weights in only one file is **`NOT CHECKED`, printed, never a pass** | **derived from the delivery** — one survey weight per person, restated in several files, is an identity the file must satisfy whatever its values are |
| **G1.7d** Weight magnitude vs the declared layout | A decimal point read in the wrong place; a field width misdeclared | Every weight strictly **below the maximum the layout's integer width allows** (Spain: 6 integer digits, so `< 1e6`) and **at or above 1.0** — a weight under 1 represents less than one person, which no design produces. The runner prints observed **min, max and distinct count** before any verdict | **derived** — the reference is the layout document, which is a different artefact from the microdata being audited |
| **G1.8** Demographic marginals | The wrong extract, or **a subsample presented as the full file** — 🔴 **and nothing else. Narrowed 2026-08-14 after the METH text was read.** | Weighted age × sex distribution within **±1.0 pp** per cell of the country's own published table for that wave. 🔴 **This gate cannot detect a wrong weight, and the tolerance is not an accuracy claim.** INE's step 4 (METH p. 35-36) uses CALMAR to force the estimated population *by age group and sex in each autonomous community* to equal the demographic projection, so on the **complete** file the agreement is imposed, not earned — the observed 0.02-0.30 pp is calibration residual between two vintages of the same projection. What survives is real and is the whole reason to keep it: **the weights belong to the full respondent set, so any subsample of rows stops reproducing the marginals.** That is a property of the ROW SET, which the calibration cannot rescue | **project-chosen** tolerance |
| **G1.9** Diary-days-per-respondent | Assuming multi-day structure a country does not have | Recorded per country and asserted against `codebook_facts`. **Spain must read 1.** A country whose measured value disagrees with its codebook is a FAIL, not a note | **derived from the codebook** |
| **G1.10** Constant-field invariance | `mode` or `scheme` varying inside a wave, which would mean the extract mixes instruments | Exactly one distinct value of each per country | **derived from decision 6** |
| **G1.11** Secondary-activity three-state integrity | 🔴 A reader collapsing *recorded and blank* into *not recorded*, or filling blanks with a code | 🔴 **Corrected 2026-08-14, second entry below — this is an EPISODE-level identity, not a slot-level one.** The count of **episodes** carrying a **non-blank** secondary activity in the emitted table equals the count obtained by **rebuilding the episodes from the raw fixed-width file inside the gate runner, with its own transcribed layout offsets and its own implementation of the split key and the first-of-run rule**, importing nothing from the reader. **Exact, no tolerance.** 🔴 The Spanish figure of **340,269 of 2,778,480 slots is the reader's own count, and it is a slot-level quantity that is not the reference for anything** — episode-level and slot-level accounting are genuinely different numbers here, because 11,216 episodes mix a blank and a non-blank `ASECU` across their own slots. The reference is the independent episode-level recount, and the two must agree. A country that does not field the variable is `NOT CHECKED`, printed, never a pass | **derived from the raw delivery** — the reference is recounted through a path the reader cannot reach, so a reader that miscollapses cannot also move the reference |

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
| Set one `act_raw` to a value outside the list — 🔴 **`99Z`, not `999`, corrected 2026-08-14** | G1.4 | G1.3 |
| **Set one `act2_raw` to `99Z`** | **G1.4** | G1.3, G1.5 — *no row moves, so the completeness gate that shadows everything else stays clean* |
| 🔴 **Why not `999`:** `999` is a **valid INE code** (row 117 of the transcribed activity list, *"Otro empleo del tiempo no especificado"*), so the original perturbation set a legal code and tested nothing. Found by the runner 2026-08-14. **Every country's out-of-list sentinel is checked against that country's own transcribed list before it is used** — a sentinel that turns out to be a real code is a perturbation that silently cannot fire | — | — |
| 🔴 **Rewrite every blank `act2_raw` as a code, or every code as blank** | **G1.11** | all others — *no row moves and every code stays inside the list, so the defect is invisible to the rest of the battery* |
| Make the reader skip a malformed row without logging it | G1.5 | all others |
| Corrupt one byte of an archive after hashing | G1.6 | all others |
| ~~Multiply one weight column by 10~~ **RETIRED** — it broke nothing. It cannot change a sign, and the only gate it moved was `G1.7b`, which cannot fail | — | — |
| **Set one respondent's weight to `-1`** | **G1.7a** | G1.7c, G1.7d, G1.8 |
| **Overwrite the whole weight column with a single constant** | **G1.7a** (distinct-count clause) | G1.6 — the archives are untouched |
| 🔴 **Replace one respondent's `FACTORF` in `CINDIV` with another respondent's valid `FACTORF`** | **G1.7c** | G1.7a, G1.7d — *the value is positive, in range and correctly formatted; it is simply the wrong person's. Nothing else in the battery can see it* |
| **Divide one respondent's weight by 10⁴ in every file that carries it** | **G1.7d** | G1.7a (still positive), **G1.7c** (still identical across files — the edit is applied consistently, which is what isolates the magnitude check) |
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

🔴 **A gate that is `NOT CHECKED` is outside the clause, and that exemption is stated once, here.**
The clause applies to gates that PASS. `G1.7b` is retired and permanently `NOT CHECKED`, so demanding
it be seen failing would be demanding the impossible — but the exemption is only sound because
`NOT CHECKED` is **printed on every run and never counted as a pass**. A retired gate that quietly
disappeared from the report instead would take its hole with it.

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
  **Measured on Spain, 2026-08-14: this happened.** It was `G1.7b`, it is retired, and `G1.8`
  survived the same test because INE calibrates to stratum totals rather than to age × sex cells,
  which leaves the composition free to disagree.
* 🔴 **After the redesign, no gate in this step compares a weighted total against a published
  population.** `G1.7c` and `G1.7d` check that the weight column is *the column we think it is*; they
  do not check that the weights are *correct*, and no offline check can. Whether INE's calibration is
  sound is INE's claim, cited, not ours to verify — and saying so is the honest boundary, not a gap
  to be filled with a comparison that cannot fail.

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

### 2026-08-14 — first run, on Spain. Ten gates scored, nine seen failing, **the probe FAILS**

Runner: `../tools/4thJ_gates_step1_spain.py`. Full output in
`outputs_step1/gate_report_step1_spain.txt`. One country, so this is a partial round by construction.

**Baseline: 10 scored, 10 PASS, 0 FAIL, 1 NOT CHECKED.**

| Gate | Result |
|---|---|
| G1.1 | PASS — 19,295 diaries against INE's stated 19,295 |
| G1.2 | PASS — 0 of 19,295 diaries fail to sum to 1440 min |
| G1.3 | PASS — 0 of 430,754 durations are not multiples of 10 |
| G1.4 | PASS — no activity or location code outside the list transcribed from INE's methodology |
| G1.5 | PASS — 2,778,480 slots represented against 2,778,480 delivered, zero unexplained drops |
| G1.6 | PASS — 8 archives, every md5 recomputed from disk matches, every URL and date present |
| **G1.7a** | PASS — every diary and individual weight strictly positive |
| **G1.7b** | 🔴 **NOT CHECKED** — see below |
| G1.8 | PASS — worst cell 0.30 pp against a tolerance of 1.0 pp |
| G1.9 | PASS — measured 1 diary day per respondent, codebook states 1, Spain must read 1 |
| G1.10 | PASS — one distinct `mode`, one distinct `scheme` |

**V1.a fired**, as it must: one country of four. It was reported, not lowered, and not escaped with a
single-country flag.

---

#### 🔴 The probe FAILS, and it fails on the gate this document warned about

`G1.7a` **passes on the real data and nothing in the pre-registered perturbation set ever made it
fall.** The coverage clause caught it. This is a defect in the validation design, not in Spain.

The mechanism is the one written into "WHAT THIS STEP'S VALIDATION DOES NOT COVER". G1.7 was
specified as two things at once: weights present and positive, **and** the weighted total within
±2 % of a published population. METH p. 34 sets out INE's estimator, and step 3 of it is *a separate
ratio estimator adjusted to the population projection in each stratum*. **The weights are calibrated
to the very figure the gate compares them against, so that half of G1.7 cannot fail** — it was
therefore split out as `G1.7b` and reported `NOT CHECKED`, with the numbers printed (estimate
41,004,668 against 41,746,705, a 1.78 % difference) so the reader can see they are inside the
tolerance and understand why that means nothing.

What is left of G1.7 is "weights are strictly positive", and the pre-registered perturbation for it —
*multiply one weight column by 10* — **cannot break that.** A gate whose only detection power lived
in a circular comparison is a gate with no detection power. 🔴 **G1.7 needs redesigning before Step 1
can be called done. That is a manager's call and it was not taken here.**

#### Three perturbations do not attribute

Pre-registered as one-gate-each; measured otherwise. Reported rather than tuned away.

| Perturbation | Expected | Actually fell |
|---|---|---|
| drop last 5 % of episode rows | G1.1 | G1.1, **G1.2, G1.5** |
| delete one episode from one diary | G1.2 | G1.2, **G1.5** |
| rewrite one duration 30 → 25 | G1.3 | G1.3, **G1.2, G1.5** |
| drop every respondent over 65 | G1.8 (coverage case) | G1.8, G1.1, G1.5 |

The common term is **G1.5**, which compares slots represented against the 2,778,480 INE delivered.
Any row that disappears is a completeness failure, so G1.5 moves with almost everything. It is a
correct check and a poor attributor, and the pre-registered table assumed it was neither.
`duration 30 → 25` also breaks the day's closure, so it necessarily moves G1.2 as well; only a
compensating edit elsewhere in the same diary could isolate G1.3.

#### What did behave exactly as pre-registered

The **null perturbation moved nothing** — the cheapest case and the one that proves the battery is
not satisfiable by a no-op. `act → 999`, the silent-skip reader, the corrupted archive byte, the
false 2-day declaration and the second `mode` value each broke exactly the one gate named for it.

#### G1.8 is a real check, and it is the strongest result here

Its reference is INE's *Estadística Continua de Población*, table 56934, resident population by
single year of age and sex at 1 July 2010, frozen into `outputs_step1/` with its md5. That series is
demographic accounting and **is not a re-tabulation of the EET file**, so for age × sex composition
the reference and the target do not share an ancestor. INE's calibration is to a stratum total, not
to age × sex cells, which leaves the composition free to disagree — and it does not: the worst of ten
cells is 0.30 pp. Computed the way INE computes, as the mean of the four day-type subsample
estimates. Getting the weight semantics wrong would not have landed inside 0.30 pp.

#### Two things this run did not establish

* Nothing about the other three countries, and V1.a says so on every line of the output.
* Whether Spain's 116 activity codes are the Eurostat ACL code for code. G1.4 proves the file stays
  inside the list **INE published**, which is a different and weaker claim. The crosswalk is Step 2.

---

### 2026-08-14 — G1.7 redesigned. The probe's own failure is what specified the replacement

Manager decision, on the author's word. The run above FAILed its coverage clause on `G1.7a`, and this
entry is the response. **Nothing here was tuned to make the probe green** — the retired half stays
visible as `NOT CHECKED` and the replacement gates are new checks that can fall.

**What was wrong.** `G1.7` asked two questions under one ID: *is the weight column there and
positive*, and *does the weighted total match the published population*. The second carried all the
detection power and **could not fail**, because INE calibrates to the figure it was compared against.
The first cannot fail either under the perturbation written for it — multiplying a weight by 10 does
not change its sign. So the gate as a whole was **untestable on both halves at once**, and that only
became visible when the coverage clause refused to accept a pass nothing had shaken.

**The replacement, in four parts.**

* **`G1.7a` kept and tightened** — present, finite, strictly positive, **and more than one distinct
  value**. The distinct-count clause is new: a column read as a constant is the single most likely
  shape of "read the wrong bytes" that positivity alone waves through.
* **`G1.7b` retired, not repaired.** Permanently `NOT CHECKED`, printed on every run with both
  numbers so a reader can see the comparison and see why it means nothing. 🔴 **It is not deleted.** A
  retired gate that vanishes from the report takes the knowledge of its hole with it, and the next
  session re-invents it.
* **`G1.7c`, cross-file weight identity — this is the actual replacement.** One survey weight per
  person, restated in `CINDIV`, `DIARIO1`, `DIARIO2` and `MHOGAR`, must be bit-identical in all four.
  🔴 **The runner recomputes it from the raw fixed-width files using the layout offsets, never from
  the reader's output** — a check fed by the reader could not detect a reader that read the wrong
  column, which is the defect the gate exists for. The four files have different layouts, so an
  offset error in one cannot produce the same wrong value in another.
* **`G1.7d`, magnitude against the declared layout.** Below the maximum the declared integer width
  allows, and at or above 1.0. **Its reference is the LAYOUT document, a different artefact from the
  microdata being audited** — which is the property `G1.7b` never had.

**Four perturbations, and the isolation is the point.** Setting one weight to `-1` fells `G1.7a`
alone. Replacing one respondent's `FACTORF` with **another respondent's valid `FACTORF`** fells
`G1.7c` alone — the value is positive, correctly formatted and inside range, so it is invisible to
every other gate in the battery; that is the measure of what `G1.7c` adds. Dividing a weight by 10⁴
**in every file that carries it** fells `G1.7d` alone, the consistency of the edit being what keeps
`G1.7c` clean. The retired `weight × 10` perturbation is struck from the table with its reason.

**What this does not do.** No gate here now checks that the weights are *right*. It cannot be done
offline, `G1.7b` only appeared to do it, and the honest statement is in "what this validation does not
cover" rather than in a tolerance nobody could fail.

**Generality.** `G1.7c` needs a delivery that restates the weight in more than one file. Spain does.
If UK, France or Italy delivers weights in a single file, `G1.7c` is **`NOT CHECKED` for that
country, printed** — never a pass, and never a reason to drop the gate for the countries that can
run it.

**Still to do, and it is an employee task, not this document's:** `../tools/4thJ_gates_step1_spain.py`
implements `G1.7`/`G1.7a`/`G1.7b` and the retired perturbation. It must be updated to this
specification and the whole battery re-run before Step 1 is called done. **Step 1 remains not done.**

### 2026-08-14 (later) — `G1.11` added, `G1.4` widened, after F-ES-6 was decided

* **F-ES-6 is decided: `act2_raw` is carried.** The record contract gains it, so the battery has to
  cover it. Two changes, both additive; **no threshold was moved and no gate was made easier.**
* **`G1.4` widened** to test `act2_raw` for code-list membership alongside `act_raw` and `loc_raw`.
  🔴 **A blank is not a code and is not tested against the list** — treating "no secondary activity"
  as an illegal code would fail the gate on 87.8 % of Spanish slots and teach the next session to
  loosen it.
* **`G1.11` added** because the defect that matters here is invisible to everything else. A reader
  that collapses *recorded and blank* into *not recorded* moves no row, drops nothing, and emits no
  code outside the list: G1.1, G1.2, G1.4 and G1.5 all stay green. 🔴 **Its reference is a recount of
  non-blank secondary-activity positions from the raw fixed-width file**, using the layout offsets,
  never the reader's own parse report — a reader-fed check cannot detect a reader that miscollapses.
* **The Spanish figure of 340,269 is the quantity under test, not the reference.** It came from the
  reader. The gate passes when the independent recount agrees with it.
* Step 1 now has **twelve gates**. The battery has not been re-run against any of this, and Step 1
  remains not done.

### 2026-08-14 (later still) — battery re-run against the twelve-gate specification. **The probe PASSES**

Employee task: `../Prompts/4thJ_employee_step1_gates_rerun_2026-08-14.md`. Reader:
`../tools/4thJ_read_spain.py`. Runner: `../tools/4thJ_gates_step1_spain.py`. Full output in
`outputs_step1/gate_report_step1_spain.txt`. Both scripts and both outputs were replaced; prior
versions backed up (`*.bak_2026-08-14`) and the backups verified non-empty before the originals were
overwritten. One country, so this remains a partial round by construction (V1.a fires, correctly).

**Reader change carried by this round, recorded in full in `4thJ_01_corpusAcquisition.md`:** `act2_raw`
(secondary activity, F-ES-6) is now carried in a nullable pandas `string` column, three states kept
separable through the parquet round-trip; `cop_padres` renamed to `cop_extra_es_padres` per D-S2-2.
**19,295 diaries, 2,778,480 slots, 430,754 episodes — unchanged.**

**Baseline: 13 scored, 13 PASS, 0 FAIL, 1 NOT CHECKED.**

| Gate | Result | Detail |
|---|---|---|
| G1.1 | PASS | 19,295 diaries against INE's stated 19,295 |
| G1.2 | PASS | 0 of 19,295 diaries fail to sum to 1,440 min |
| G1.3 | PASS | 0 of 430,754 durations are not multiples of 10 |
| G1.4 | PASS | no `act_raw`/`loc_raw`/`act2_raw` code outside the transcribed list; `act2_raw` states (ES): not_recorded 0, recorded_and_blank 349,954, recorded_with_value 80,800 |
| G1.5 | PASS | 2,778,480 slots represented against 2,778,480 delivered, zero unexplained drops |
| G1.6 | PASS | 8 archives, every md5 recomputed from disk matches |
| G1.7a | PASS | all weights strictly positive; distinct values weight_dia 8,039, weight_ind 8,039 (both > 1) |
| G1.7b | 🔴 NOT CHECKED | printed only: weighted estimate 41,004,668 vs ECP 41,746,705 (1.78 %) — evidence of nothing |
| G1.7c | PASS | 19,295 respondents, `FACTORF` bit-identical across CINDIV/DIARIO1/DIARIO2/MHOGAR, 0 mismatches |
| G1.7d | PASS | observed min 264.94, max 113,238.82, 8,039 distinct values, bounds [1.0, 1e6) |
| G1.8 | PASS | worst cell (25-44, female) 0.30 pp against 1.0 pp tolerance |
| G1.9 | PASS | measured 1 diary day per respondent, codebook states 1 |
| G1.10 | PASS | one distinct `mode`, one distinct `scheme` |
| G1.11 | PASS | independent recount from raw DIARIO2 (own-transcribed offsets, first-of-run ASECU over 430,754 independently rebuilt episodes): 80,800 non-blank; emitted table: 80,800 non-blank |

#### Coverage clause: **SATISFIED**

Every gate that PASSes on the real data was made to fall by at least one perturbation in the set. 13 of
13 scored gates seen failing. `G1.7b` is exempt (permanently `NOT CHECKED`, printed on every run).

| Gate | Made to fall by |
|---|---|
| G1.1 | drop_last_5pct_rows, drop_over_65 |
| G1.2 | drop_last_5pct_rows, delete_one_episode, duration_30_to_25 |
| G1.3 | duration_30_to_25 |
| G1.4 | act_to_999, act2_to_999 |
| G1.5 | drop_last_5pct_rows, delete_one_episode, duration_30_to_25, reader_skips_silently, drop_over_65 |
| G1.6 | corrupt_archive_byte |
| G1.7a | weight_negative_one, weight_constant |
| G1.7c | factorf_swap_cindiv |
| G1.7d | divide_weight_1e4_all_files |
| G1.8 | weight_constant, drop_over_65 |
| G1.9 | declare_spain_2_days |
| G1.10 | second_mode_value |
| G1.11 | drop_last_5pct_rows, drop_over_65, act2_rewrite_nonblank_to_blank |

#### The struck perturbation

`weight_times_10` (multiply one weight column by 10) is removed from the set, as specified, and not
replaced by a repaired version of itself. It broke nothing on the prior run: it cannot change a sign,
and the only gate it moved was `G1.7b`, which cannot fail. Recorded so it is not helpfully reinstated.

#### What did not attribute

Five perturbations moved more than the gate they were named for. All five are **row-removal or
row-rewrite collateral**, the same mechanism recorded in the first run for `G1.5`, now also reaching
`G1.2` (duration closure, when the removed row was mid-diary) and `G1.11` (its independent recount is
fixed against the raw file, so removing episodes from the emitted table alone breaks the count it is
compared to):

| Perturbation | Expected | Also moved |
|---|---|---|
| drop_last_5pct_rows | G1.1 | G1.2, G1.5, G1.11 |
| delete_one_episode | G1.2 | G1.5 |
| duration_30_to_25 | G1.3 | G1.2, G1.5 |
| weight_constant | G1.7a | G1.8 — overwriting every diary weight with one constant necessarily changes the weighted demographic marginals too; not claimed clean by the pre-registered table for this case |
| drop_over_65 | G1.8 (coverage case, pre-registered to also move G1.1) | G1.1, G1.5, G1.11, for the same row-removal reason |

None of this is tuned away. `G1.5` and `G1.11` in particular are correct checks and poor attributors by
the same structural reason: both compare a count derived from the emitted table against a fixed
external reference, so any row that disappears from the table moves both regardless of which gate a
perturbation was written for.

#### An implementation bug found and fixed during this round, recorded so it is not silently reintroduced

The first draft of `G1.7d` computed magnitude across every row of all four raw files, including
`MHOGAR`'s full 25,895 household members. `MHOGAR` carries `FACTORF` = `0000000000000000` for the
6,600 members who are not individual-questionnaire-plus-diary respondents (25,895 − 19,295 = 6,600,
confirmed against the raw file) — a placeholder, not a weight the design ever produced; the reader
itself never reads `MHOGAR.FACTORF` for anyone but a joined respondent either. Checking the whole file
made the null perturbation itself fail `G1.7d` (min observed 0.0), which is disallowed by construction
("nothing may fail" on the null). Fixed by restricting `G1.7d`, like `G1.7c`, to the 19,295 respondents.
🔴 This was a defect in this round's own gate code, not a finding about the data or the specification —
recorded because a check that fails the null perturbation is exactly the failure mode the null case
exists to catch, and it did.

A second, smaller bug in the same draft: the `act2_to_999` perturbation used the literal string `"999"`,
which is itself a valid INE code (row 117 of the transcribed activity list, "Otro empleo del tiempo no
especificado") and so did not test code-list membership at all. Fixed to use `"99Z"`, the same
genuinely out-of-list value `act_to_999` already used for the primary activity.

#### act2_raw and G1.11: what "the count in the emitted episode table" means, made explicit

Episodes are built from `APRIN` + `LUGAR` + the six co-presence flags; `ASECU` is not part of that key
and is aggregated the same way `act_raw` is — first-of-run. Measured directly: of 430,754 episodes,
11,216 mix a blank and a non-blank `ASECU` across their own underlying slots, and 13,009 contain more
than one distinct `ASECU` value. A slot-level accounting (2,778,480 slots, 340,269 non-blank) and an
episode-level accounting are therefore genuinely different quantities, not two measurements of the same
thing — which is exactly why the specification's own text says the reader's 340,269 is not a reference
for anything. `G1.11` is implemented as: independently rebuild episode boundaries from the raw file
using the documented algorithm (not imported from the reader), take first-of-run `ASECU` the same way
the reader takes first-of-run `APRIN`, and require that count to equal what is actually stored in
`episodes_spain.parquet`. Both computations produced 80,800 non-blank episodes, in agreement — that is
the identity `G1.11` is checking (a reader that miscollapsed the three states during the parquet
round-trip would break it), not "does episode aggregation preserve every slot", which no fixed-size
episode field can do without changing the episode count, and the episode count is pinned at 430,754 by
Task 1.3.

**The Spain gate battery now runs clean against the twelve-gate specification**, coverage clause
included. This is one country of four, as V1.a records on every line of the output; whether Step 1 as a
whole is done is not this entry's call, and is a question for the other three countries and the
Eurostat enquiry, neither of which this round touched.

### 2026-08-14 (manager, after verifying the re-run) — two corrections to this document itself

The battery result above is accepted; it was re-derived from
`outputs_step1/gate_report_step1_spain.txt` rather than read off the entry. Two things in **this
document** were wrong, and both were wrong before the employee round rather than because of it.

**1. The gate count is FOURTEEN, not twelve.** The gate table above has fourteen rows: `G1.1` to
`G1.6`, `G1.7a`/`G1.7b`/`G1.7c`/`G1.7d`, and `G1.8` to `G1.11`. **Thirteen are scored and one
(`G1.7b`) is permanently `NOT CHECKED`**, which is exactly what the runner reported. "Twelve" was
written when `G1.11` was added and it counted the `G1.7` split as two parts rather than four; it was
then copied into `4thJ_01_corpusAcquisition.md`, `../Prompts/RESUME.md`, the parent plan and the
employee prompt. 🔴 **Earlier progress-log entries are append-only and keep the wrong number; this
entry is the correction, and the live gate table is the authority.** A stale count is not cosmetic
here — a later session that trusts it will conclude two gates are missing and go looking for them, or
worse, will read "twelve of twelve seen failing" as coverage over a set that has fourteen members.

**2. `G1.11`'s threshold was not implementable as written, and the runner was right to say so.** The
row read "the count of **slots** carrying a non-blank secondary activity ... equals the count in the
emitted **episode** table" — two different quantities, which no correct reader can make equal.
Measured this round: of 430,754 episodes, **11,216 mix a blank and a non-blank `ASECU` across their
own underlying slots** and **13,009 carry more than one distinct `ASECU` value**, so the slot-level
340,269 and the episode-level 80,800 are not two measurements of one number. The gate row is corrected
to state the episode-level identity it was always for: **rebuild the episodes from the raw file inside
the runner, with its own offsets, its own split key and its own first-of-run rule, and require the
non-blank count to equal what is stored in the parquet.**

🔴 **This is a basis change, and it is recorded as one rather than folded in quietly.** What it does
not do is weaken the gate: the reference still arrives through a path the reader cannot reach, which
is the property `G1.7b` lacked and the whole reason `G1.11` exists. What it costs is stated plainly —
`G1.11` now proves that the three states survived the parquet round-trip and that the aggregation is
reproducible from the raw file, and it does **not** prove that first-of-run is the right rule for
`ASECU`. **It is not the right rule for the 13,009 multi-value episodes**, and that is a Step 3
question about what `act2` is for, not a Step 1 question about custody. Recorded here so Step 3 meets
it already knowing.

**Not changed, and deliberately:** no threshold moved, `G1.7b` stays retired and printed, and the
`G1.7d` population restriction the employee applied (19,295 respondents, excluding `MHOGAR`'s 6,600
non-respondent members whose `FACTORF` is an all-zero placeholder) is accepted as the correct
population rather than a loosened bound — those rows carry no diary, enter no corpus, and were never
weights. It is the same population `G1.7c` already used. 🔴 **The null perturbation catching it is the
system working**: a gate that fails on unperturbed data is the one failure mode the null case exists
for, and it fired on the first draft.

**Where this leaves Step 1:** Spain's battery is green and every scored gate has been seen falling.
**Step 1 is not done**, and not for any reason inside this document — `V1.a` fires on one country of
four, and the other three are acquisitions the author makes in person.

### 2026-08-14 (manager) — `G1.7b`'s retirement VERIFIED against the METH text, and `G1.8` narrowed by the same reading

The retirement of `G1.7b` had been taken on a citation — *"METH p. 34, step 3"* — that no one in this
project had opened. **It has now been opened.** The file is local:
`_local_runs/4J/raw/spain/meth_t25304471.pdf`, 127 pages, downloaded and hashed with the archive. Text
extracted with `pypdf` and read directly. 🔴 **This is not deep research and no external source was
consulted — it is our own delivered documentation, and the claim was checked against the artefact we
already hold.**

**Section 3.7.5 ESTIMADORES, printed page 34, is verbatim:**

> *"Para estimar una característica X con la submuestra t en el área geográfica G se ha utilizado un
> estimador que se obtiene a través de los siguientes pasos: 1. Estimador Horvitz-Thompson basado en
> el factor de diseño. 2. Factor de ajuste en cada comunidad autónoma, por grupos de semanas y
> estratos. **3. Estimador de razón separado, para ajustar a la proyección de población en cada
> estrato h.**"*

`P_h` is defined on the same page as *"Proyección de población referida a la mitad del periodo de
encuesta en el estrato h"*. ✅ **`G1.7b`'s retirement is confirmed on the primary text: the weights are
ratio-adjusted to the population projection, so comparing the weighted total against a published
population compares the calibration target with itself.** The gate stays permanently `NOT CHECKED` and
both numbers stay printed.

🔴 **The same page and the next two carry a second finding, which is why reading a citation beats
trusting one.** Printed pages 35-36, step 4, the *final* estimator:

> *"a) La estimación, a partir de la muestra, de la población **por grupos de edad y sexo** en cada
> comunidad **coincida con la proyección de la población**"* … *"b) … la población extranjera en cada
> comunidad coincida con la proyección"* … *"Para este ajuste se utiliza el software **CALMAR**
> desarrollado por la oficina estadística de Francia (INSEE)."*

**That is `G1.8`'s reference.** The weighted age × sex distribution is calibrated to equal the
demographic projection by construction, community by community, and therefore nationally. So `G1.8`
is in the **same family as `G1.7b`** — and the tight numbers it reported (worst cell 0.30 pp against a
1.0 pp tolerance) are calibration residual between two vintages of the same projection, **not the file
agreeing with an independent reference.**

**It is narrowed rather than retired, and the distinction is the point.** `G1.7b` had no power left
once its circularity was seen; `G1.8` keeps one thing the calibration cannot give it: **the weights
belong to the full respondent set, so any subsample of rows stops reproducing the marginals.** The
perturbation set already demonstrates this — `drop_over_65` fells `G1.8`, and it fells it because the
row set changed, not because a weight was wrong. That is exactly the defect the gate's own "what it
detects" column names. **What the gate row now says out loud is that it detects nothing else** — in
particular it cannot detect a misread weight column, which is what `G1.7c` and `G1.7d` are for.

🔴 **The general lesson, recorded because it cost nothing to check and would have cost a reviewer's
question later: a citation in our own document is a claim until someone opens the page.** Two of the
fourteen gates rest on this one methodology section, the retirement of one of them was already
correct, and the reading also revealed that a second gate's provenance column was overstated. No
threshold was moved and no gate was removed.
