# 4J — EMPLOYEE TASK: Step 1 sixteen-gate re-run, ROUND 2

**Issued by the manager, 2026-08-16. Hand this to a FRESH employee session.**

🔴 **Read ONLY this file, the three gate runners, and the three readers. Do NOT read the pipeline
document, the step specifications, or `RESUME.md`.** The previous employee on this task burned 517k
tokens re-reading files and was stopped mid-work. Everything you need is below.

---

## WHY THIS ROUND EXISTS

Round 1 (Speed jobs `1251980`/`1251981`/`1251982`, 2026-08-16) completed `0:0` but its `G1.6a` result
is **VOID**. `G1.6a` FAILed on all three countries because the gate trusted the manifest's `local_path`
literally, and those are Windows workstation paths (`C:/Users/o_iseri/...`) that do not exist on the
cluster — so every archive reported "missing on disk". The archives are fine; `md5sum` on the cluster
matched all 13 files before any job ran.

Because `G1.6a` FAILed at baseline it **could not be seen falling**, so `corrupt_archive_byte` reported
`newly-failed []` and Spain's `null` perturbation printed `🔴 NULL PERTURBATION MOVED A GATE`.

---

## THE REFERENCE IMPLEMENTATION

`4J_docs_occ/tools/4thJ_gates_step1_uk.py` **already carries M-6 and M-7** (edited 2026-08-16 21:19).
It is **UNTESTED** — no dry run was ever completed. Read it first. The relevant places:

| What | Where in the UK file |
|---|---|
| `subclauses` dict on `GateResult` | lines 132–137 |
| `G1.4` returning per-field sub-clauses | lines 230–279 |
| `resolve_archive()` + the two problem strings | lines 317–361 |
| country-root `--raw` and the internally derived deep dir | lines 796–810 |
| sub-clause comparison in the perturbation loop | lines ~1040 |

`4thJ_gates_step1_spain.py` and `4thJ_gates_step1_italy.py` are **UNTOUCHED**: no M-6, no M-7.

---

## TASK 1 — port M-6 to Spain and Italy

**M-6:** `G1.6a` resolves every manifest-recorded archive **under `--raw` at invocation time**, keeping
the manifest's relative sub-path. `local_path` stays in the manifest untouched, as provenance — **do not
edit any `local_path` value in any manifest fragment.**

Two **distinct** problem strings, copied verbatim from the UK file — do not invent a third wording:

* `md5 mismatch`
* `recorded location not resolvable under --raw`

A corrupted byte and a bad deployment can then never be confused again.

## TASK 2 — port M-7 to Spain and Italy

**M-7:** sub-clause attribution when a gate FAILs at baseline for a pre-registered unrelated reason.
Compare the gate's own **computed detail per field** instead of its verdict: `loc_raw` moving from
`codes_outside_list=[]` to `['-8']` counts as **FIRED at sub-clause level**.

🔴 **Additive only. M-7 may never turn a FAIL into a PASS.** Same `subclauses` dict shape as the UK file.

## TASK 3 — run-stamped output directory

Every job this round writes into **`Step1_docs/outputs_step1/run_<YYYYMMDD-HHMM>/`**, one stamp shared
by all four jobs, passed in explicitly — never computed independently inside each job.

Both the **reader** and the **gate runner** write there. This is the point: no leftover parquet from
round 1 may satisfy a vacuity guard. **Copy nothing back into `outputs_step1/` afterwards.**

## TASK 4 — V1.a moves to a fourth job

🔴 **Manager decision, 2026-08-16, and it narrows the hand-off text on purpose:** only **`V1.a`** moves
out of the per-country jobs. `V1.b` (inputs printed before any verdict), `V1.c` (status read from the
computing process) and `V1.d` (unrecognised code printed and refused) are **per-run properties of one
country's battery and stay exactly where they are.** Moving them would make them unfalsifiable.

Write `tools/4thJ_vacuity_step1.py`: reads the run-stamped dir, scores `V1.a` **once per round** —
FAIL below 3 countries with an `episodes_<country>.parquet` present — and writes
`vacuity_report_step1.txt` into the same run dir. Submit it with
`--dependency=afterok:<es>:<it>:<uk>`.

Round 1's `V1.a` fired on IT and UK purely because the three jobs are unchained and Spain takes 18
minutes: IT and UK looked for the sibling parquets before Spain had written its own. **A race, not a
threshold regression.** 🔴 **Do NOT "fix" it by letting the guard find round 1's leftover files — a
guard satisfied by stale files is not a guard.**

## TASK 5 — dry-run all three locally BEFORE submitting

On the Windows box, all three runners, end to end. Round 1's entire defect survived because the dry runs
ran where the Windows `local_path` values happen to exist. **So dry-run with `--raw` pointed at
`_local_runs/4J/raw/<country>/` and confirm `G1.6a` resolves through `--raw`, not through `local_path`.**

Raw trees are under `GSSCanada\_local_runs\4J\raw\` — the parent of `GSSCanada-main\`. Verify with one
`ls` before assuming a layout.

## TASK 6 — submit on Speed

🔴 **`sbatch` only. Never a blocking `srun`, never bare python on the login node, not even a one-liner.**
Every job requests `-t 7-00:00:00`. Partition `ps`.

Four jobs: three per-country (**unchained**, so a country that crashes does not take the other two with
it) plus the vacuity job with `--dependency=afterok:<es>:<it>:<uk>`.

Raw data is already on the cluster at `/speed-scratch/o_iseri/4J/raw/` from round 1's TASK 0, md5-verified
after transfer. **Confirm with one `ls` — do not re-copy 610 MB if it is there.**

Check state with **one** call:
`sacct -j <es>,<it>,<uk>,<vac> --format=JobID,JobName,State,ExitCode,Elapsed`
🔴 **One call, not a loop.** The login shell is **tcsh** — a bash `while ... done` loop dies on
"Illegal variable name" and killed round 1's first poller.

---

## 🔴 ACCEPTANCE TESTS — these decide whether the round is accepted at all

A green gate table without these means nothing.

1. `corrupt_archive_byte` must be seen **NEWLY failing** `G1.6a` on **all three** countries.
2. The `null` perturbation must move **nothing** on Spain.
3. M-7 must recover the **four UK arms** masked by the deliberate `G1.4` `4276` FAIL, including the
   `loc_undeclared_sentinel` audit of M-1.
4. Every `NOT CHECKED` — `G1.7b` on all three, `G1.7c` and `G1.8` on Italy, `G1.8` on the UK — carries a
   **one-line reason from the spec**. `NOT CHECKED` is never a pass.
5. The two M-1..M-5 audit perturbations: `loc_undeclared_sentinel` must fell `G1.4`;
   `weight_blank_on_productive_row` must fell `G1.7a`. 🔴 **If either reports `DID NOT FIRE` and is not
   explained by M-7 sub-clause masking, the decision it audits is REVERSED — M-1 or M-3 respectively —
   and the perturbation is NOT adjusted.** Report it; do not decide it.

**Read the results in this order:** the audit perturbations first, then `V1.a`, then the sixteen gates.

---

## UNTOUCHED BY DESIGN — leave all of it alone

* Italy's **`G1.6b` FAIL** (missing URL + date in our own custody record — the author supplies those).
* The UK's **`G1.4` `4276` FAIL** (F-UK-9, a real data defect, deliberately preserved).
* Every `local_path` field in every manifest fragment.
* **Merge 2 of 2** (`acquisition_manifest_uk.json` + `..._italy.json` → `acquisition_manifest.json`) —
  the manager's, still deferred.
* Every gate threshold. 🔴 **You fix runners this round. You do not move a single threshold.** If a gate
  FAILs on real data, that is the deliverable — report it.

---

## DELIVERABLES

1. `4thJ_gates_step1_spain.py`, `..._italy.py` with M-6 + M-7; `..._uk.py` dry-run-verified.
2. `tools/4thJ_vacuity_step1.py`.
3. `outputs_step1/run_<stamp>/` containing, per country: `episodes_<country>.parquet`,
   `parse_report_<country>.txt`, `gate_report_step1_<country>.txt`, plus `vacuity_report_step1.txt`.
4. The four job IDs and their `sacct` line.
5. A **`proglog_entries_round2.md`** fragment in the run dir: append-only prose, one entry, stating what
   was changed, what each acceptance test returned, and 🔴 **what you did NOT verify independently.**
   The manager merges it. **Do not edit `4thJ_01_corpusAcquisition.md` or its validation document
   yourself.**

**Report back short:** the four job IDs, the five acceptance-test outcomes, the gate tallies per country.
Nothing else.
