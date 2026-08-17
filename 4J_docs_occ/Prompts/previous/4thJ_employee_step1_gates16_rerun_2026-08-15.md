# 4J — EMPLOYEE TASK: bring three readers and three gate runners to the SIXTEEN-gate specification, then re-run all three on Speed

### Hand this to a **fresh** employee session as its first message. Do not resume a long thread.
#### Written 2026-08-15 by the manager, after decisions M-1 to M-5. Scope: `4thJ_read_uk.py`, all three `4thJ_gates_step1_<country>.py`, and one full re-run of the Step 1 battery on **Spain, the UK and Italy**.

---

## YOUR ROLE

You are the **employee**. You execute exactly what is written here, in order, and you stop. You do not
redesign a gate, you do not move a threshold, you do not add a country, and you do not improve the
specification. **If the specification is wrong, you write the finding down and stop.** A gate that
fails is a result, not a bug to be worked around.

Read these two documents before you touch anything. They are the specification; this prompt is a work
order, not a paraphrase you may implement instead:

* `../Step1_docs/4thJ_01_corpusAcquisition.md` — the work items, the **intermediate record contract**,
  and the new section **"CONTRACT CHANGES M-1 to M-5"**
* `../Step1_docs/4thJ_01_corpusAcquisition_val.md` — **sixteen** gates, the perturbation table, the
  coverage clause, the vacuity guards, and the progress log entry of 2026-08-15 explaining why each
  change was made

---

## 🔴 STATE BEFORE YOU START

Spain, the UK and Italy are all built. **All three were scored against the FOURTEEN-gate
specification, and three gates FAIL on real, unperturbed data:** Italy `G1.6`, UK `G1.4`, UK `G1.7a`.
Every one of those FAILs was reported honestly by the employee who found it. **They are not yours to
argue with.**

The manager has since taken five decisions, M-1 to M-5. **The specification is now sixteen gates and
none of the code implements it.**

🔴 **AND THE CORPUS CHANGED THE SAME DAY. Author decision 16, 2026-08-15: FRANCE IS EXCLUDED.** The
corpus is **three countries — Spain, the UK, Italy — and all three are built.** Two consequences for
this round, and the second one is the point of it:

* **`V1.a`'s threshold moved from 4 to 3**, because it is decision 6 written in executable form and the
  author amended decision 6 on a dated line. 🔴 **It is not a flag, not a tolerance, and not a
  precedent for touching any other guard.** If you find yourself wanting to move a second threshold in
  this round, you are doing something this prompt did not ask for.
* 🔴 **So `V1.a` should NOT fire on this round — and that means THIS ROUND CAN CLOSE STEP 1.** Every
  previous Step 1 battery ran knowing it was partial. This one is not partial. **Treat every verdict
  accordingly: there is no later country coming to catch what you wave through.**

🔴 **Why this round exists, in one sentence you should keep in view the whole time.** A gate that
FAILs at baseline **cannot be seen falling**, so every perturbation aimed at it reports `DID NOT FIRE`
— and across the two reports that silenced **five arms**, including Italy's md5 arm and the UK's
entire weight arm. This round is what recovers them.

---

## 🔴 THE ONE IDEA BEHIND EVERY CHANGE BELOW

Same as the last round, and it has not changed: **every check reaches its reference through a path the
defect cannot travel.**

* `G1.7c`, `G1.7d`, `G1.11` and the new **`G1.12`** re-read the **raw delivered files themselves**.
* 🔴 **They must not import anything from `4thJ_read_<country>.py`** — not its layout tables, not its
  column resolution, not its sentinel mapping, not its output. A check fed by the reader cannot detect
  a reader that read the wrong column, and that is the exact defect these gates exist for.
* Re-declare offsets / column names / sentinel mappings **inside the gate runner**, and **print them**,
  so a human can compare the two declarations by eye. Two independent transcriptions that agree are
  evidence; one transcription used twice is not.

If you find yourself writing `from 4thJ_read_uk import ...` in a gate runner, stop and re-read this.

---

## HARD RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`. Never bare `python` on the login node,
  not even a one-line import check. Every job requests `-t 7-00:00:00 --partition=ps`. Flagged three
  times on this account; a fourth is suspension. **This round runs on Speed** — see TASK 0.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* **Verify a backup is non-empty before overwriting anything.** `[ -s "$BK" ]`.
* **Never count lines with PowerShell.** Use `wc -l`.
* **You do not touch `acquisition_manifest.json` or either Step 1 progress log** except where TASK 6
  tells you to, and you do not merge the two outstanding country fragments — those are the manager's.
* **You never search the web.** Every fact comes from the delivery on disk.

---

## TASK 0 — get the raw archives onto `/speed-scratch`, then run there

Work item 1.1's definition of done says the archives live on `/speed-scratch/o_iseri/4J/raw/<country>/`
and they do not; they are on the local workstation under `_local_runs/4J/raw/{spain,uk,italy}/`
(145 MB + 320 MB + 145 MB). **This is the outstanding half of 1.1 and this round closes it.**

1. `scp -r` each country tree to `/speed-scratch/o_iseri/4J/raw/<country>/`. `scp` is on the allowed
   login-node list.
2. 🔴 **Re-verify every md5 on the cluster side after the copy**, against the manifest fragments. A
   transfer that corrupted a byte must be caught here and not by `G1.6a` looking like a data finding.
   Record the verification in the run log.
3. Copy the three readers, the three gate runners and `outputs_step1/` to
   `/speed-scratch/o_iseri/4J/`.
4. **One `sbatch` job per country**, three jobs, each `-p ps -t 7-00:00:00`, each writing its own
   `out_<country>.txt`. Do not chain them into one job — a country that crashes must not take the
   other two with it.

**Definition of done:** three archives on `/speed-scratch` with md5s re-verified after transfer, three
job IDs recorded.

---

## TASK 1 — M-1: `loc_raw` becomes a three-state field

**Contract change. Read "CONTRACT CHANGES M-1 to M-5 → M-1" in the implementation document first.**

* `loc_raw` becomes a **nullable pandas `string`** column carrying three states that must stay
  separable through the parquet round-trip: **not recorded** (`pd.NA`), **recorded and blank** (`""`),
  **recorded with a value**. Exactly `act2_raw`'s treatment.
* **UK reader (`4thJ_read_uk.py`) changes**: `WhereWhen == -9` maps to **state 2, `""`**, the same
  mapping the reader already applies to `What_Oth1/2/3`. That is the whole change.
* **Spain and Italy readers do not change** — both field a location on every episode and emit state 3
  throughout. **Re-emit their parquets anyway**, so all three are written by code that matches the
  current contract, and confirm the counts do not move (ES 430,754; IT 1,077,657; UK 587,632).
* 🔴 **A value enters state 2 only if that country's delivery declares it a missingness sentinel, with
  a citation.** There is no rule that negative values are sentinels and **you may not invent one.**
* **Add a sentinel table to each `codebook_facts_<country>.md`**: field, sentinel value, the
  delivery's own label for it, the citation, the measured count. The UK's `-9` in `WhereWhen` is
  7,117 of 587,632 per F-UK-15 — **re-measure it, do not copy it.** If a country has no sentinel,
  write the table with a single row saying so.

🔴 **`4276` (F-UK-9) is not a sentinel and must keep failing `G1.4`.** If your change makes it pass,
you have implemented M-1 wrongly. This is the first thing to check.

---

## TASK 2 — M-2: split `G1.6` into `G1.6a` and `G1.6b`

* **`G1.6a`, integrity** — md5 recorded at receipt, recomputed from disk, must match. Scored for every
  country **independently of any URL**. Print each archive's `hashed_at` before the verdict.
* **`G1.6b`, provenance** — source URL and date present. **Threshold unchanged. Italy FAILs it, and
  that FAIL is expected and correct.** Do not add a URL, do not reconstruct one from the delivery's
  printed archive pages, do not mark it `NOT CHECKED`.
* **Manifest fragments gain two fields per archive**: `hashed_at` (`download` | `receipt_from_author`)
  and `provenance_source` (`fetched_by_us` | `author_attested` | `NOT FOUND`). Fill them from what is
  actually known. 🔴 **`NOT FOUND` is the honest value for Italy and you write it.**
* **`corrupt_archive_byte` now targets `G1.6a` alone** and **must fire on all three countries,
  Italy included**. That is the arm this split exists to recover; if it still does not fire on Italy,
  say so loudly and stop.
* **New perturbation `strip_url_from_manifest`** — remove one archive's URL. Must fell **`G1.6b`
  alone**, with `G1.6a` clean.

---

## TASK 3 — M-3: re-scope `G1.7a`

New threshold, in two clauses, **both required to PASS**:

1. Present, finite, strictly positive and **more than one distinct value**, on every row **for which
   the delivery computed a weight**.
2. **Every row without a weight carries a delivery-declared non-productive status code.** For the UK
   those codes are in the delivery (`DMFlag`, `HhOut`); read them from the raw file and **name the
   exact codes you accepted, with their counts, in the report**.

🔴 **A missing weight on a row the delivery flags as productive is a FAIL.**

* `weight_ind` and `weight_dia` become **nullable** in the record contract. The count of corpus rows
  with no weight is **printed per country on every run**.
* **New perturbation `weight_blank_on_productive_row`** — blank one weight on a row the delivery calls
  productive. Must fell **`G1.7a` alone**. 🔴 **If it does not fire, M-3 removed detection power
  instead of redirecting it, and you write that down and stop — do not adjust the perturbation.**
* With `G1.7a` passing at baseline on the UK, **`weight_negative_one` and `weight_constant` must now
  actually fire there.** Both currently report `DID NOT FIRE`. Confirm both.

---

## TASK 4 — M-4: condition `G1.7d` on the weighting convention

* **Each `codebook_facts_<country>.md` gains a required fact: the weighting convention, cited**, as
  one of **expansion** / **normalised** / **not declared**. Spain is *expansion* (INE expansion
  factors). The UK is *normalised* (NATCEN p. 31, mean ≈ 1). **Establish Italy's from ISTAT's own
  text — do not infer it from the observed values, and do not copy Spain's.**
* Bounds: expansion → `[1.0, 10^declared_integer_width)`. normalised → `> 0` **and mean within ±1 %
  of 1.0**. not declared → `NOT CHECKED`, printed, never a pass.
* 🔴 **The upper-bound half needs a declared layout width. The UK ships none, so that half stays
  `NOT CHECKED` for the UK.** M-4 does not rescue it and you must not make it look rescued.
* **New perturbation `weight_scale_10x_normalised`** — multiply the **whole** normalised weight column
  by 10, normalised-convention countries only. Must fell **`G1.7d`'s mean clause alone**, with `G1.7a`
  and `G1.7c` clean.

---

## TASK 5 — M-5 and the new gate `G1.12`

**M-5**: the UK's `weight_dia` is **`dia_wt_a`**. It already is — this task is to confirm it in code
and state the citation (NATCEN p. 31 §7.4 c/d; CTUR p. 13) in the reader's own comment and in
`codebook_facts_uk.md`. `dia_wt_b` stays carried as `weight_dia_b`. **Change nothing else.**

**`G1.12` — `loc_raw` three-state integrity and sentinel inventory.** Build it exactly the way
`G1.11` is built:

* Recount the three `loc_raw` states **from the raw delivered file inside the gate runner**, with its
  **own** column resolution and its **own** sentinel mapping, importing nothing from the reader.
* Require exact agreement with the emitted parquet. **No tolerance.**
* **Print the full inventory**: every distinct out-of-list value per field, with its count, per
  country — so an undeclared sentinel is visible on the page before `G1.4` fails on it.
* **Two new perturbations.** `loc_sentinel_to_code` (rewrite every declared sentinel as a valid
  location code) must fell **`G1.12` alone** — no row moves and every value is in-list, so `G1.1`,
  `G1.2`, `G1.4` and `G1.5` stay green. `loc_undeclared_sentinel` (set one `loc_raw` to `-8`, not
  declared, not in list) must fell **`G1.4` alone**.
* 🔴 **`loc_undeclared_sentinel` is M-1's own audit. If it does not fire, the sentinel exclusion
  disarmed the membership test — write that down and stop. The decision gets reversed, not the
  perturbation.**

---

## TASK 6 — run all three, report, and stop

* **Sixteen gates**: `G1.1`-`G1.5`, `G1.6a`, `G1.6b`, `G1.7a`-`G1.7d`, `G1.8`-`G1.12`. Print all
  sixteen for every country, with `NOT CHECKED` printed and never counted as a pass.
* **The full perturbation set including the six new ones**, plus the **null perturbation** — nothing
  may fail on the null, and a gate that FAILs at baseline must be reported as such rather than
  swallowed into the null's result.
* **The coverage clause**, per country. 🔴 **If it FAILs, that is the deliverable.** Do not invent a
  perturbation to make it green.
* 🔴 **`V1.a` must NOT fire** — three countries of three, after decision 16. **If it fires, the runner
  is still carrying the old threshold and you fix the runner, not the guard.**
* **Outputs**, overwriting the current ones after backing them up and verifying the backups non-empty:
  `episodes_<country>.parquet`, `parse_report_<country>.txt`, `gate_report_step1_<country>.txt`,
  and the updated `codebook_facts_<country>.md`.
* **Progress log**: emit **one fragment per country**, `proglog_entries_gates16_<country>.md`, in
  `outputs_step1/`. 🔴 **Do not append to either Step 1 document yourself** — three countries in one
  round is one writer, but the manager already owes two merges into those files and will not have
  three collide.

**Report back, in this order and nothing else:** the three job IDs; the sixteen-gate table per
country; which of the six new perturbations fired and which did not; the coverage clause verdict per
country; and every place where the specification was wrong.

🔴 **The two audit perturbations (`loc_undeclared_sentinel`, `weight_blank_on_productive_row`) come
first in that report.** If either failed to fire, that is the only thing the manager needs from this
round.
