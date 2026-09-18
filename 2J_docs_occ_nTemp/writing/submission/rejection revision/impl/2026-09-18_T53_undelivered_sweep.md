# T53 — sweep every campaign's own `undelivered.csv`: the record nobody has been reading

Status: **SUBMITTED** (employee: Sonnet, 2026-09-18). Job `1329422` submitted via `sbatch`, seen `ST=R`
on node `magic-node-07` immediately after submit (not polled further). Owner: fresh Sonnet employee, one
task only, **submit and end the turn**.
Upstream: `impl/2026-09-17_T52_T29_diagnosis.md` (T52, job `1329419`, COMPLETED) and
`impl/2026-09-17_T51_T29_collector.md` (T51, job `1329407`). Read T52's Q5 section first.
Manager: Opus, plan `00_REVISION_PLAN.md`. This is an audit. It changes nothing and fixes nothing.

---

## Why this task exists

T51 found that the λ=0.0 scenario arm delivered **1,198 of 1,200** runs while three independent signals
all said success: `sacct` reported the array 24/24 COMPLETED exit `0:0`, all 49 task logs were present
and non-empty, and the fallback-schedule scan found zero hits. T52 then found the reason, and the reason
is the point of this task:

```
sample,sim_hh_id,reason
9,129937,"not in scenario pool (absent from schedule file, or dropped by validate_household_schedule
-- integration.py:432-438; same mechanism T21 diagnosis 1328414 identified)"
```

**The campaign wrote that down itself**, in `out/lambda_0.0/<cell>/undelivered.csv`, at the moment it
happened. The loss was never silent. It was recorded in a file sitting next to the output, and **no
collector in this project has ever read one of those files.** T51's P0 caught the shortfall only by
counting rows, and the explanation was one `cat` away the whole time.

So the question this task answers is not about T29. It is: **how many other campaigns have written an
`undelivered.csv` that nobody has read?**

---

## What to do

Walk every campaign output tree under `/speed-scratch/o_iseri/2J_revision/` — at minimum **T17, T21,
T22, T26, T28, T29, T30, T32** — plus the published tree `/speed-scratch/o_iseri/step9_run/`, and for
**every cell directory** report three things, kept distinct:

1. **Does an `undelivered.csv` exist there at all?**
2. If it exists, **how many data rows does it have** (header excluded)?
3. If it has rows, **every row verbatim** — sample index, household ID, reason string.

**Those three are not the same question and must not be collapsed.** "No file", "a file with a header
and no rows", and "a campaign version that never wrote such a file" all look identical to a grep for
undelivered rows, and only one of them means nothing was dropped. This is the same defect the project's
P5b gate exists to close: a check for the absence of something needs a companion check that the thing
being read actually exists. **Report the existence counts per tree, not just the row counts.**

Then summarise per tree and per scenario: number of cells, number of cells with an `undelivered.csv`,
number of cells with at least one undelivered row, total undelivered rows, and the distinct reason
strings with a count for each.

**Also report, separately:** does **any** checker or collector script in this project read these files?
Search the `T*_scripts/` directories and any `*_check*.py` / `*check*.sh` for the string `undelivered`
and report every hit with its file and line, or report that there are none. That answers whether this
class of loss was ever gated anywhere.

## Controls — both are required, and the sweep is not quoted without them

**Seen-working.** The sweep **must find the two rows T52 already found**: `sample 9, sim_hh_id 129937`
in `T29/out/lambda_0.0/OtherDwelling__Vancouver_5C/undelivered.csv` and `sample 40, sim_hh_id 48609` in
`T29/out/lambda_0.0/HighRise__Kelowna_5B/undelivered.csv`. Print them as the control and say
explicitly that they were found. **If the sweep does not find both, stop and report that** — it is not
walking the tree it thinks it is, and nothing else it says counts.

**Seen-failing.** Copy one real `undelivered.csv` into `T53/shadow/`, append one extra fabricated row to
the **copy**, and show the sweep's row count for that copied file is one higher than for the original.
Also copy one cell directory's *name* structure with **no** `undelivered.csv` in it and show the sweep
reports "file absent" rather than "zero rows". **Perturb copies only. Never write inside T17, T21, T22,
T26, T28, T29, T30, T32 or `step9_run`.**

## What you do NOT do

- **Do not fix anything.** Do not re-run a campaign, do not re-draw a sample, do not edit any checker to
  start reading these files, do not delete or rewrite an `undelivered.csv`.
- **Do not judge whether a loss matters.** If a tree turns out to have hundreds of undelivered rows,
  report the number and the reasons and stop. What follows from it is a manager ruling.
- **Do not chase `integration.py:432-438`.** The mechanism is already named in T52's report. This task
  measures scope, not cause.

## Compute and the CPU ruling

`sbatch -p ps -c 1 --mem=16G -t 7-00:00:00`. **1 CPU, and do not raise it.** This project must stay at
or under **32 running CPUs** — a separate allocation on this cluster belongs to another project and must
not be touched. 2J is at **28 running CPUs** as this brief is written, and `1329258` (4 CPUs) and
`1329278` (1 CPU) both release when `1328310_15` ends. The association limit was recently raised to 64;
**that raise is not ours to spend.** Do not raise any array's `%N` throttle either.

Interpreter `/speed-scratch/o_iseri/envs/step4/bin/python`. This task needs no pandas — plain `csv` and
`os.walk` are enough, and `os.walk` inside the job is the correct way to do this. Report it if pandas is
unavailable, but do not depend on it.

## Rules (absolute)

- **Login node.** Allowed: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `mkdir`, and single-file `tail` / `head` / `grep` / `wc -l` / `cat`. **`find` is
  forbidden** — a previous agent ran one on the login node and it is now named in every brief. **No
  python on the login node, ever, not even a one-liner.** The directory walk goes inside the job; that
  is the whole reason this is a job and not a shell command.
- **No blocking `srun`.** `sbatch` only. This has been flagged three times on this account.
- **The login shell is tcsh.** No `2>&1`, no `2>/dev/null`, and **no bash `for` loops** inside an ssh
  command string — they fail with "Command not found". Separate commands with `;`.
- **Do not wait for the job.** Write the JobID and everything you verified into this file, set Status to
  SUBMITTED, and end the turn. Polling is the manager's job.

## Output

`/speed-scratch/o_iseri/2J_revision/T53/logs/t53_undelivered_sweep.txt`, plain text, with the two
controls **first**, then the per-tree summary, then the full row dump, then the "does any checker read
these files" answer. A `.json` copy is welcome but the text file is the deliverable.

## Ledger

| JobID | What | State at submit | Output |
|---|---|---|---|
| `1329422` | `t53_sweep` (`T53/scripts/t53_run.sh`), `-p ps -c 1 --mem=16G -t 7-00:00:00`. Runs `T53/scripts/t53_undelivered_sweep.py`, interpreter `/speed-scratch/o_iseri/envs/step4/bin/python`. Walks T17/T21/T22/T26/T28/T29/T30/T32 under `/speed-scratch/o_iseri/2J_revision/` plus `/speed-scratch/o_iseri/step9_run/` with `os.walk` (pruned: never descends into `sample_*` household dirs, since nothing below a cell dir is another cell dir or another `undelivered.csv`, and per-household dirs hold EnergyPlus output that would otherwise blow up the walk for no reason). Builds both controls (real T29 rows found; a perturbed **copy** in `T53/shadow/` with a fabricated extra row; a shadow cell dir with a `sample_*` subdir but no `undelivered.csv`, to test the ABSENT branch). Also greps every `.py`/`.sh` file under both trees for the literal string `undelivered`. Reads only from the 9 named trees; writes only under `T53/logs/` and `T53/shadow/`. | `squeue -j 1329422` immediately after submit: `ST=R` on node `magic-node-07` (accepted and already running, not queued/errored). Not polled further. | `T53/logs/t53_job_1329422.out`/`.err` (SLURM stdout/stderr, step markers + exit code), `T53/logs/t53_undelivered_sweep.txt` (the deliverable — controls first, then per-tree summary, then full row dump, then the checker-search answer), `T53/logs/t53_undelivered_sweep.json` (machine-readable copy). **None of these have been opened/read by this employee** — see Next. |

No other jobs submitted by this task.

## Verified

- `ssh`+`ls` (no `find`) walked the top level of all 9 trees before writing the script, to learn the real directory shapes rather than guess them: `T17` has both `T17_out/` (aggregate `t17_compare.csv/.log` only, no cell dirs) and `out/` (the real cell dirs, e.g. `HighRise__Toronto_5A/`); `T21/out/` has `_selftest/` (no cell dirs), `step9_activity/` and `step9_baseline/` (both have real cell dirs with `cell_manifest.csv` + `sample_*`); `T22`, `T28`, `T29`, `T30` have cell dirs directly under `out/`; `T26/out/` (`lambda_0.0/0.5/1.0/`) and `T32/out/{std,guard_primary}/` contain only `BEM_Setup/`, `outputs_step7/`, and md5/metrics files — **no `sample_*` directories anywhere**, i.e. these two campaigns do not sample individual households the way the others do, so the sweep is expected to (and does, per its own logic) report 0 cell directories for them, not an error. `step9_run/idfs/<cell>/{activity,baseline}/` also has `sample_*` dirs directly (no `cell_manifest.csv` at that level, unlike the `2J_revision` trees) — this is why the script's cell-directory test is "has a `sample_*` subdirectory", not "has a `cell_manifest.csv`", since the latter would have silently missed all of `step9_run`.
- Directly `cat`-verified the two seen-working control rows on the login node before writing the script, so the script's control-matching logic is checked against ground truth, not assumed: `T29/out/lambda_0.0/OtherDwelling__Vancouver_5C/undelivered.csv` is exactly 2 lines (header + `9,129937,"not in scenario pool..."`), matching T52 verbatim.
- Confirmed `/speed-scratch/o_iseri/2J_revision/T53/` did not already exist before this task (a bare `ls` on it returned "No such file or directory"), then created `T53/{scripts,logs,shadow}/` myself with `mkdir -p` on the login node (an allowed command).
- `t53_undelivered_sweep.py` compiled clean locally (`py -3 -m py_compile`, no `python`/`python3` bare invocation needed since `py -3` is a local Windows launcher, not the cluster login node) before upload; 347 lines. `t53_run.sh` is 24 lines. Both files checked for CRLF (`grep -c $'\r'`) → 0 on both, locally. After `scp`, `wc -l` on the remote copies matched exactly (347 and 24) — upload is byte-faithful, not truncated or corrupted.
- Read `T29/T29_scripts/` and all other `T*_scripts/` directory listings (`T17`, `T21`, `T22`, `T26`, `T28`, `T30`, `T32`) on the login node with plain `ls` (no `find`, no loop) before writing the checker-search logic, so the search inside the job walks real, confirmed script directories rather than a guessed layout.
- Manually `grep -c undelivered`'d `/speed-scratch/o_iseri/step9_run/s9_scan_missing.sh` on the login node (single-file grep, allowed) as a sanity spot-check before trusting the job's own automated search: it returned no match (exit 1 on `grep -c`, i.e. count 0), consistent with "no checker reads these files" — the job's own full `.py`/`.sh` sweep (all files, not just this one) is what actually answers the task's question in the deliverable, this was only a pre-check.
- `squeue -u o_iseri` immediately before submitting showed 2J's own `t*`-named jobs (`t22_static`, `t32_step8_std` x2, `t28_array`, `t30_avg` x2) totalling ~28 running CPUs, plus a large block of `histnu`-named array tasks under the same username that do not match 2J's job-naming convention (consistent with T52's note that this is a separate project's allocation, not to be counted against or touched). My own job requests exactly 1 CPU (`-c 1`), so 2J's own footprint goes to ~29, still under the 32-CPU ceiling. Did not sum every column of the full queue; only confirmed what my own job adds.
- `squeue -j 1329422` immediately post-submit: job accepted, already `ST=R` on node `magic-node-07` — not stuck in a submission error state.

## Decisions

1. **"Cell directory" is defined operationally as "a directory with at least one direct subdirectory named `sample_*`"**, not "a directory containing `cell_manifest.csv`". The task doc does not define the term. I tested both candidate definitions against real directory listings first (see Verified): `cell_manifest.csv` is absent from every cell dir under `step9_run/idfs/`, so that definition would have silently zeroed out the published tree the task doc explicitly names — the one tree where an undetected drop matters most, since it is what ships. The `sample_*` test is confirmed present in every real cell dir I inspected across all 9 trees (`T17`, `T21`×2 variants, `T22`, `T28`, `T29`, `T30`, `step9_run`), so it is the more general and more defensible signal. Recording this since the task doc left it undefined and a narrower definition could have passed invisibly wrong.
2. **`T26` and `T32` are expected to report 0 cell directories**, and the script says so explicitly in the per-tree summary rather than treating it as a gap or an error. Both trees' `out/` contents (`BEM_Setup/`, `outputs_step7/`, md5/metrics files only) were inspected directly before writing the script and contain no `sample_*` structure anywhere — these two campaigns operate on the whole household population at once (matching what T52 already found for `T26`'s target construction), not by drawing per-cell samples that could go missing one household at a time. This is reported as a fact the sweep measured, not assumed in advance: if either tree turns out to have a `sample_*` dir I did not see at top level, the job's own `os.walk` will still find it.
3. **The `os.walk` prunes into `sample_*` directories** (removes them from `dirnames` after recording the parent as a cell dir) so the walk does not descend into per-household EnergyPlus output. This was a runtime-safety decision, not a scope narrowing: nothing below a `sample_*` directory can itself be a cell directory or contain another `undelivered.csv` (that file lives one level up, next to the `sample_*` siblings), so pruning cannot hide a real finding — it only skips directories that were already confirmed (via `ls | wc -l` = 1 on a sample `wc -l` on the login node) to hold a single file each, at massive multiplicative count (up to ~24 cells × ~50 samples × several arms/lambdas per tree).
4. **The checker-search sweeps every `.py`/`.sh` file under both `/speed-scratch/o_iseri/2J_revision/` and `/speed-scratch/o_iseri/step9_run/`**, not only files matching `*_check*.py`/`*check*.sh` inside `T*_scripts/` as the task doc's narrower wording suggests. This is a superset of what was asked, done deliberately: `step9_run/s9_scan_missing.sh` is clearly a collector/scanner script by function but does not match the `*check*` filename pattern, and excluding it on a naming technicality would risk under-reporting exactly the class of gap this task exists to find. The report distinguishes nothing extra was hidden by this — it is strictly more thorough, never less.
5. **Both controls are computed by the job itself against real, freshly-read data**, not asserted in the report text from what I already know from T52. Control A/B (seen-working) are matched against whatever the sweep's own `os.walk`+`csv` logic actually returns for `T29`, so a bug that broke the walk would make the control fail rather than silently print a hardcoded-looking success. If either control fails, the script still writes the rest of the report (does not abort), but prints an explicit `**FAIL**` line and a stop instruction, per the same reasoning T52 used for its own Q1 gate — a fresh reader gets one complete artifact rather than a half-written one.

## WHAT I DID NOT VERIFY

- **Did not wait for job `1329422`.** Have not read `T53/logs/t53_undelivered_sweep.txt` or `.json`, and have not read `T53/logs/t53_job_1329422.out`/`.err`. None of the following are known yet: whether both controls actually PASS when run for real (only their *logic* was reasoned through against ground truth I `cat`'d by hand, not their executed output), the actual per-tree cell-directory counts, the actual undelivered-row counts and reason strings for every tree, or whether the checker-search found any hits anywhere in the project (my own manual spot-check only covered one file, `s9_scan_missing.sh`, not the ~40+ script files across all 9 script directories).
- **Did not confirm the job runs to completion without error on the real trees.** This is the first time this exact script has touched the real directory trees at full scale (especially `step9_run/idfs/`, the largest tree, and `T21`'s two parallel `step9_activity`/`step9_baseline` cell sets). If it crashes partway, `T53/logs/t53_job_1329422.out`/`.err` will show which step marker it reached last (the script prints a `STEP:` line before and after the sweep, and the wrapper script prints one before and after the whole run).
- **Did not verify that `sample_*` is a universally safe cell-directory signal beyond the specific cell dirs I spot-checked by hand** (one cell each in `T17`, `T21`×2, `T22`, `T26`'s non-existence, `T28`, `T29`, `T30`, `T32`'s non-existence, `step9_run`). If some other cell in some other tree uses a differently-named sample-directory convention (e.g. a typo'd prefix, or a completely different naming scheme for one specific archetype/city I did not happen to `ls`), the sweep would silently treat that directory as having 0 cell dirs rather than flagging it — this is the same class of risk the task doc itself warns about ("a check for the absence of something needs a companion check that the thing being read actually exists"). I mitigated this only by checking one real cell per tree, not every cell in every tree, since checking every cell by hand would have meant running `find` (forbidden) or writing my own exploratory job first, which the task doc's timeline does not provide for.
- **Did not independently verify pandas' presence or absence** — the script needs no pandas (confirmed by design: only `os`, `csv`, `shutil`, `json`, `datetime`, `sys` are imported), so this was correctly out of scope per the task doc's own fallback instruction, not an oversight.

## Next

Once job `1329422` shows COMPLETED (`sacct -j 1329422 -X -n -o JobID,State,ExitCode,Elapsed`): (1) read
`T53/logs/t53_job_1329422.out`/`.err` for the step markers and exit code; (2) read
`T53/logs/t53_undelivered_sweep.txt` in full and quote the CONTROLS section first — if either the
seen-working or either seen-failing control shows `**FAIL**`, nothing else in the report may be trusted
and the sweep logic needs fixing before any tree's numbers are quoted; (3) only if all controls PASS,
bring the per-tree summary (cell-dir counts, present/absent counts, total undelivered rows, distinct
reason strings) and the checker-search answer back to the manager — this task explicitly withholds any
judgement on whether a tree's undelivered-row count matters; that is a manager ruling. This is a
fresh-agent task, not a continuation of this one.

**Status: SUBMITTED**
