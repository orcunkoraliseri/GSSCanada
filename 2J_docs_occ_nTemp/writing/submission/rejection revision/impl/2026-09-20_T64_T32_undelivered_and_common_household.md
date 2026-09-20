# T64 — T32: locate and read its own `undelivered.csv`, apply item 30's common-household rule

Task doc: this file.
Upstream: `impl/2026-09-17_T52_T29_diagnosis.md` (item 30, the common-household ruling),
`impl/2026-09-18_T53_undelivered_sweep.md` (the sweep method — T53 already confirmed T32's `out/std/` and
`out/guard_primary/` trees, at top level, contain no `sample_*` cell directories, only population-level
tables: `BEM_Setup/`, `outputs_step7/`, `t32_metrics_*.csv`, `t32_person_table_*.csv`,
`t32_targets_*.csv`). Plan §5 item 33 (`00_REVISION_PLAN.md`, entry (cn)) already states, from a source the
manager has not re-verified, that T32 has an `undelivered.csv` row identical to T29's dropped household
(`OtherDwelling__Vancouver_5C`, sample 9, `sim_hh_id 129937`). **Find that file yourself — do not take its
existence or contents on faith from the plan text.**
Manager: Opus. Status: IN PROGRESS — job 1340676 submitted, unread. See Ledger for JobID and the
driver-script grep result (no match anywhere in T32's call chain).

## Why this task exists

Two things are still owed for T32 (job `1329220`, S-Revert-std campaign, already ACCEPTED on G0/SC1/SC4/SC5
in log (br) — **do not re-score those, they are closed**):

1. **Nobody has read T32's own `undelivered.csv`.** T53's sweep covered T17/T21/T22/T26/T28/T29/T30/T32 and
   the published tree, but T53 defined a "cell directory" as one containing a `sample_*` subdirectory, and
   T32 has none at the top level it checked (`out/std/`, `out/guard_primary/`) — meaning **T53 most likely
   never actually found T32's `undelivered.csv`, if T32 writes one from a different location** (e.g. inside
   `BEM_Setup/`, a working/temp directory not yet listed under `out/`, or a scratch dir referenced in
   `T32_scripts/t32_scenario.py` that is cleaned up post-run). Item 33's claim needs its source pinned down.
2. **Item 30's ruling**: any cross-scenario comparison must be computed on the household set common to
   *both* sides being compared, never assumed to share every household. If T32 (S-Revert-std) excludes any
   household that T26's own scenario builds (λ=0.0, λ=0.5, or the 2030 main file) include, or vice versa,
   that must be stated in counts before any number that compares T32 against another scenario is quoted.

## What to do

1. **Read the driver script first, on the login node** (single-file, allowed):
   `cat`/`grep` `/speed-scratch/o_iseri/2J_revision/T32/T32_scripts/t32_scenario.py` and
   `t32_job.sh` for the literal string `undelivered` and for wherever it writes its scenario-pool output
   (look for the same construction T29/T26 use — `validate_household_schedule`,
   `integration.py:432-438`-style rejection, or a bespoke path). Report the exact line numbers and what you
   find. If the string does not appear anywhere in T32's own scripts, **say so plainly** — that would mean
   item 33's claim is either about a different job, or T32 reuses a shared library file
   (e.g. `integration.py`) that writes it on T32's behalf without T32's own driver naming the string, and
   you must then grep the shared library it imports instead of stopping at "not found".
2. **Locate the actual file(s) inside an `sbatch` job**, not on the login node — walking directories to find
   a filename is exactly the case the login-node rule exists for. Reuse T53's `os.walk` approach: walk
   `/speed-scratch/o_iseri/2J_revision/T32/` fully (there is no `find` restriction inside a job) and report
   every path matching `*undelivered*.csv` found, with row counts and, if any rows exist, every row
   verbatim (sample index / household ID / reason string, same shape as T53's report).
3. **If a file is found containing the item-33 row** (`OtherDwelling__Vancouver_5C`, sample 9, household
   `129937`), treat that as the seen-working control — confirm it verbatim and say so explicitly. If it is
   NOT found where item 33 said it would be, do not assume item 33 was fabricated: search more broadly
   inside the same job (the full T32 tree, not just `out/`) before concluding it doesn't exist, and report
   exactly what you did search.
4. **Apply the common-household rule.** For each of T32's two output variants (`std`, `guard_primary`),
   compare its delivered household set (from whatever manifest/pool file it writes — check
   `t32_person_table_std.csv`/`t32_person_table_primary.csv` for a household-ID column) against T26's own
   λ=0.0, λ=0.5 and main-2030 household sets (T26's outputs are under
   `/speed-scratch/o_iseri/2J_revision/T26/`). Report, per pair of scenarios that might ever be compared in
   the manuscript, the size of the symmetric difference (households in one but not the other) — not just a
   single "matches / doesn't match" verdict.
5. **State plainly whether any of this changes T32's own already-ACCEPTED numbers** (G0/SC1/SC4/SC5 from
   log (br)) or only bears on comparisons *between* T32 and another campaign. Do not re-derive or re-score
   the accepted numbers — only say whether the household-set finding here touches their basis.

## Rules (absolute)

- Login node allowed commands only: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `mkdir`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. No `python`, no `find`, no `for`
  loops over directories on the login node — put the directory walk inside the `sbatch` job, same as T53.
- tcsh login shell: no `2>&1`, no `2>/dev/null`.
- Do not edit anything under `T32/` or `T26/`. Write your own script and outputs only under
  `T64/scripts/` and `T64/logs/` (create with `mkdir` on the login node, an allowed command).
- Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python`. Needs no pandas for the file-walk part;
  pandas is fine for the household-set comparison if the CSVs are pandas-friendly, but plain `csv` works
  too — do not block on pandas availability.
- CPU ceiling: 2J stays at or under 32 running CPUs. Nothing else is running for 2J right now (confirm with
  `squeue -u o_iseri -h -o '%.12i %.16j %.8T %.4C'` before submit). Request `-c 1 --mem=16G -t 7-00:00:00`.
- Submit and end the turn. Do not poll. Write the JobID and everything found into this doc's Ledger.
- If you pass roughly 150k tokens, stop, write state, and say "handoff needed" — do not push through.

## What you do NOT do

- Do not re-score T32's G0/SC1/SC4/SC5 (already ACCEPTED, log (br)).
- Do not fix, patch, or re-run T32 or T26. This is read-only diagnosis.
- Do not invent a household-common-set correction algorithm beyond reporting the symmetric-difference
  counts and rows — deciding what to do about a mismatch (drop, footnote, or recompute) is a manager
  ruling, same pattern as item 29/30.

## Output

`/speed-scratch/o_iseri/2J_revision/T64/logs/t64_report.txt`, plain text: (1) what the driver-script grep
found and where, (2) every `undelivered.csv` path found under `T32/` with row counts and full row dumps,
(3) the common-household symmetric-difference table for std/guard_primary vs T26's three household sets,
(4) the plain statement of whether this touches T32's already-accepted numbers.

## Ledger

- 2026-09-20: Login-node `squeue -u o_iseri -h -o '%.12i %.16j %.8T %.4C'` before submit showed 33 RUNNING
  1-CPU tasks total, but `scontrol show job` on both distinct job names showed: array `1340317` ("histnu",
  31 running tasks) has `WorkDir=/nfs/speed-scratch/rhlab/hist_nu_z7a` — **not a 2J job, another lab's work
  under this same account** — and job `1339757` ("wp9_stage3_RC6", 1 running task, `WorkDir=/nfs/home/o/o_iseri`)
  is plausibly 2J's own WP9 work. Treated 2J's own running-CPU count as ~1, well under the 32 ceiling;
  submitted T64's 1-CPU job on top of that. Flagging this for the manager: if `histnu` is in fact 2J-adjacent,
  the ceiling check needs a firmer rule than job-name guessing.
- Job **1340676** (`t64_undeliv`, `sbatch -p ps -c 1 --mem=16G -t 7-00:00:00`, wrapped
  `python scripts/t64_walk.py`) submitted from `/speed-scratch/o_iseri/2J_revision/T64/`. Output:
  `/speed-scratch/o_iseri/2J_revision/T64/logs/slurm_1340676.out` (stdout) and
  `/speed-scratch/o_iseri/2J_revision/T64/logs/t64_report.txt` (the report itself, written by the script).
  Script: `/speed-scratch/o_iseri/2J_revision/T64/scripts/t64_walk.py` (local copy also at
  `2J_docs_occ_nTemp/writing/submission/rejection revision/impl/` is NOT kept — script lives only on
  cluster + this session's scratchpad). One `squeue -j 1340676` check right after submit showed `R` (running,
  0:04 elapsed) on node `speed-07` — not polled further, per no-parking rule.

## Verified

- **Driver-script grep (step 1), done directly on the login node with single-file `grep -n`:**
  `grep -n undelivered T32_scripts/t32_scenario.py` and the same on `t32_job.sh`, `t32_metrics.py`,
  `t32_compare.sh` — **all four exit 1 (no match)**. `t32_scenario.py:1-12` documents its own code base:
  it imports `T26_scripts/t26_scenario.py` via `importlib.util` (not copied), which itself imports
  `T20_scripts/t20_d1.py` the same way (`t32_scenario.py:41-42,70-78`), which in turn dynamically loads
  `06_forecast_rake.py`, `05_postlink_rake.py`, `07_aug_to_bem.py` (`t32_scenario.py:89-90,143-144`).
  Grepped every one of those plus `07_bemIntegrationGSS_val.py` and `activity_loads.py` (all in
  `T26_scripts/`) for `undelivered` — **all exit 1, no match anywhere in the whole call chain.**
  **The literal string "undelivered" does not appear in T32's own scripts nor in any shared-library
  file T32 dynamically loads.** Item 33's claimed mechanism is not sourced from T32's own code path.
- Confirmed via `ls` (single-dir, allowed) the actual T32 tree has a **fourth top-level directory not
  in T53's known list**: `T32/step8_std/` (containing `logs/`, `out/`, `scripts/`), alongside
  `T32_scripts/`, `logs/`, `out/` (with `out/std/`, `out/guard_primary/`). This is new information for
  the manager — T53's sweep, and item 33's source, may not have seen `step8_std/` either.
- Confirmed household-ID files exist and their column: `T32/out/std/t32_person_table_std.csv` and
  `T32/out/guard_primary/t32_person_table_primary.csv` both have `HH_ID` as column 1 (checked with `head -3`).
  T26 has three matching files: `T26/out/lambda_0.0/t26_person_table_lambda_0.0.csv`,
  `T26/out/lambda_0.5/t26_person_table_lambda_0.5.csv`, `T26/out/lambda_1.0/t26_person_table_lambda_1.0.csv`
  (treated as the "main-2030" file per the task doc's naming — this is an inference, since only three
  lambda directories exist and none is literally named "main"; flagged in WHAT I DID NOT VERIFY).

## Decisions

- Treated `T26/out/lambda_1.0/...` as the task doc's "main-2030" household set by elimination (only three
  lambda directories exist: 0.0, 0.5, 1.0). Not confirmed against any text that names lambda_1.0 as "main".
- Job script re-does the driver-script grep itself (Part 1 of the report) for a self-contained artifact,
  in addition to the login-node greps already done and logged above — same files, same method, redundant
  by design so the written report doesn't depend on this doc.
- Used `os.walk` over the FULL `T32_ROOT` (not just `out/`), which now also covers `step8_std/` and
  `T32_scripts/` (in case a leftover `undelivered.csv` sits next to the code) — broader than T53's scope.
- Symmetric-difference table computed for all 6 T32-variant-vs-T26-set pairs plus 4 within-family pairs
  (T32_std vs T32_guard_primary, and the three T26 lambda sets pairwise) for completeness.

## Next

- Read `/speed-scratch/o_iseri/2J_revision/T64/logs/t64_report.txt` (single-file `cat`/`grep` on login
  node) once job 1340676 shows COMPLETED in `sacct -j 1340676`. Report has 4 parts: (1) grep re-confirmation,
  (2) every `*undelivered*.csv` found under T32 with full row dumps, (3) the symmetric-difference table,
  (4) a plain statement that this is read-only and does not itself re-score T32's accepted G0/SC1/SC4/SC5.
- If Part 2 finds zero `undelivered.csv` files anywhere under T32, item 33's claim needs a manager ruling:
  either it names a different job's file, or a file that has since been deleted/cleaned up.
- If any Part 3 symmetric difference is nonzero, no manuscript number comparing that T32-vs-T26 pair may be
  quoted until the manager rules on it (same pattern as items 29/30) — this task does not decide that itself.

## WHAT I DID NOT VERIFY

- Did not confirm that `lambda_1.0` is what the task doc means by "main-2030" — inferred by elimination
  (only 3 lambda dirs exist). If a separate, differently-named main-2030 file exists elsewhere in T26's
  tree, this job's Part 3 table will not include it.
- Did not wait for job 1340676 to finish; one `squeue` check right after submit showed it running
  (0:04 elapsed on `speed-07`), but its actual findings (file contents, row counts, symmetric-difference
  numbers) are UNREAD as of this doc's last edit.
- Did not verify whether job array `1340317` ("histnu", `WorkDir=rhlab/...`) is truly unrelated to 2J —
  inferred from its work directory living under a different lab's scratch path, not from asking anyone.
- Did not check T29's own driver scripts for the literal source of the `OtherDwelling__Vancouver_5C` /
  sample 9 / `sim_hh_id 129937` row referenced in item 33 — out of scope per the task doc (T32-only grep),
  but if Part 2 finds no file, that would be the next place to look to pin down item 33's actual source.
- Did not check whether `T32/step8_std/out/` itself contains its own nested `out/std`-like structure that
  might duplicate or supersede the top-level `T32/out/std/` — only listed it, did not walk it manually
  (the sbatch job's `os.walk` covers it, but I have not read that output yet).
