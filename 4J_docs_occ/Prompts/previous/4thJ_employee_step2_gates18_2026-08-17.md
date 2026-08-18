# Employee task — Step 2 battery, eighteen gates. Re-earn the result on the rebuilt table

**Role: employee.** You audit. You do not design gates, you do not choose thresholds, and 🔴 **you
never move a threshold, widen a band, or adjust a perturbation because something fails.** A gate that
fails is a result. A perturbation that reports `DID NOT FIRE` is reported as `DID NOT FIRE`.

**Governing spec:** `4J_docs_occ/Step2_docs/4thJ_02_harmonisation_val.md` — gate table, perturbation
table and vacuity guards **verbatim**. Read `4thJ_02_harmonisation.md` for **D-S2-18**, which is why
this round exists, **D-S2-19** for the approved band set and the dropped `season` stratum, and
**D-S2-12** as amended for the eleven new columns.

---

## WHAT CHANGED, AND WHAT DID NOT

`tools/4thJ_gates_step2.py` exists and ran clean on 2026-08-16: 15 of 15 scored gates PASS, 15 of 15
seen failing, coverage satisfied, `G2.10` `NOT CHECKED`.

🔴 **That result is not carried forward.** D-S2-18 added eleven columns to `harmonised.parquet` —
**five** harmonised conditioning strata and six `_raw` carriers, `season` having been dropped from the
prefix by D-S2-19 while `strat_season_raw` still ships — and **a result earned against a narrower table is not a
result about this one.** Everything re-runs.

**Your additions: `G2.17`, `G2.18`, four perturbations, `V2.j`, `V2.k`.** Sixteen gates become
**eighteen**, seventeen perturbations become **twenty-one**, nine guards become **eleven**.

🔴 **Do not touch the sixteen existing gates.** Not to tidy them, not to refactor a shared helper into
them, not to "align" `G2.17` with `G2.11`'s style. The only acceptable diff to `G2.1`-`G2.16` is none.

---

## 🔴 CLUSTER RULES

* **`sbatch` only.** Never a blocking `srun`, never bare python on the login node, not even a
  one-liner. Every job `-t 7-00:00:00`, partition `ps`, CPU only.
* tcsh login shell: no `2>&1` in ssh commands, no bash `while ... done` loops, **one `sacct` call, not
  a poll loop.**
* Speed interpreter `/speed-scratch/o_iseri/envs/step4/bin/python`.

## 🔴 NO PARKING — you never wait for a job

Submit with `sbatch`, write the JobID into your implementation doc, and **end your turn** saying "job
N submitted, state written to `<path>`". **No background polls, no sleeps, no no-op command to hold
the turn open, no "waiting for the notification".** The manager watches the queue and spawns a fresh
agent to collect the result. Waiting is the most expensive thing you can do: every wake re-sends your
whole transcript and produces nothing.

**Your state goes to disk as it happens**, in
`Step2_docs/impl/2026-08-17_step2-gates18.md` — create it first, before any job:

```
# Step 2 battery, eighteen gates — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step2_gates18_2026-08-17.md
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per job: JobID · what · state · exit · output path (append-only, failures kept)
## Verified      <- numbers actually read, and where from
## Decisions     <- what this task doc did not decide, and what you assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

Nothing of value may exist only in your context. Never read a multi-MB file into it — `wc -l`,
`grep -n`, `tail -c`, `head`. Past roughly 150k tokens, stop, write state, and say a handoff is needed.

---

## THE TWO NEW GATES — implement the val doc's rows, not this summary

Read the rows. They carry the thresholds and the provenance. What follows is only what is easy to
implement wrongly.

**`G2.17` has two sub-clauses and M-7 attribution applies** — the report says *which clause* fell.

* **(a)** zero nulls in every shipped `strat_*` column, every country. A missing national value must
  already have become the declared `unknown` band; **null is not an acceptable state here** and a null
  is a FAIL, not a note.
* **(b)** zero `(country, hid, pid, diary_day)` groups carrying more than one distinct value of any
  `strat_*` column. 🔴 **(b) exists because (a) cannot see it.** A stratum read at the episode grain
  instead of the person-day grain is fully populated and simply wrong.

**`G2.18` has two sub-clauses, same attribution rule.**

* **(a)** zero band values emitted by **exactly one** of the three countries. 🔴 **If this fires, report
  it — the repair is to coarsen the classification and that is the manager's call, not yours.** Plus
  the escalation clause on `unknown`'s share.
* **(b)** in `crosswalk_strata.csv`, zero Italian source bands mapping to more than one target band,
  for every stratum Italy delivers pre-banded. 🔴 **This clause reads the crosswalk, not the parquet.**
  It is D-S2-13's rule generalised, and it fires at design time rather than after a rebuild.

## THE FOUR NEW PERTURBATIONS

The val doc's rows, on **copies** in your own output directory, never on the shipped artefacts. Each
must break **exactly one** gate, and the "must stay clean" column is part of the test:

1. Null one respondent's `strat_econ_status` → **G2.17 (a)**.
2. Give one respondent's second half-day a different `strat_day_type` → **G2.17 (b)**, and **(a) must
   stay clean.**
3. Prefix Italy's household-type bands with `it_` → **G2.18 (a)**, and `G2.17`, `G2.3`, `G2.4` clean.
4. Split the Italian age band `04` into two target bands → **G2.18 (b)**, and `G2.17` clean.

## THE TWO NEW GUARDS

* **`V2.j`** — import the band vocabulary from the shipped `crosswalk_strata.csv`. FAIL if the file is
  missing, if a `strat_*` column has no rows in it, if a band in the parquet is absent from it, or if
  a stratum's rows do not cover all three countries. 🔴 **Print the full country × band cross-tab for
  all six strata before any verdict.** Two bands with equal prevalence make a swap between them
  invisible to `G2.18 (a)`, and only the printed table shows whether the gate could see anything.
  **This is the fourth instance of one rule** — `V2.e`, `V2.f`, `V2.h` and now `V2.j`: **import the
  shipped list, never restate it in the validator.**
* **`V2.k`** — FAIL unless the rebuilt table reproduces the accepted table's counts exactly:

| | ES | UK | IT |
|---|---|---|---|
| **episodes** | **446,547** | **567,381** | **1,010,140** |
| **splits** | **37,830** | **0** | **0** |

  🔴 **Its reference is the previous accepted table, which this run did not author.** Hard-code the
  four numbers from the val doc; do not read them out of the parquet you are auditing.

---

## 🔴 ACCEPTANCE TESTS

1. **All twenty-one perturbations ran**, including the null one, and the null one moved **nothing**.
2. Every perturbation felled its named gate, or reported `DID NOT FIRE` with evidence.
3. No perturbation felled a gate its row lists under "must stay clean".
4. The coverage cross-tab is printed, and **every gate that passes on real data was made to fall by
   something.**
5. Every `NOT CHECKED` carries its one-line reason and stays outside the scored tally. **`G2.10` is
   still `NOT CHECKED`** — we hold no published national table, and a re-tabulation of our own data
   shares an ancestor with the thing it audits. **`NOT CHECKED` is never a pass.**
6. `G2.3` is still not demonstrated independently of `G2.4`. **Report that standing limitation again;
   do not add a perturbation to fix it** — adding a row to a pre-registered table is the author's call.
7. **No threshold moved, no existing gate edited, no perturbation adjusted.** State it in terms.

## DELIVERABLE

The updated `tools/4thJ_gates_step2.py`, the reports under your `--out` directory, and a Progress Log
**fragment** at `outputs_step2/proglog_step2_gates18.md` for the manager to merge, ending with a
section headed **WHAT I DID NOT VERIFY**.

Report anything this document did not decide for you, and say plainly what you assumed.
