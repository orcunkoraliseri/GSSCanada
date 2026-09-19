# WP9 prep: get the EnergyPlus re-run ready (1J JBPS revision), task and implementation state

Task doc:   this file (sections "Task" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §3 P15, §7 log (j) and (k)
Previous:   `impl/2026-09-19_WP2b_find_simulations.md` (read "Findings A-D" and "Manager vetting" first)
Status:     IN PROGRESS

## Why

The paper's six-neighbourhood EnergyPlus results must be re-run:
- the 2010 scenario was an exact copy of 2005, because the April 2005 and 2010 schedule files are byte-identical;
- the figures came from a 3-draw pilot (`BEM_Setup/SimResults/BatchAll_MC_N3_1776120359`).

The author approved the re-run on 2026-09-19. The cluster is full, and **another heavy local run is
going on right now** (about 10 EnergyPlus processes, 82 % CPU, 37 of 64 GB RAM free at 11:40). The author
reaches this machine only remotely and **cannot reboot it**: a memory freeze locks them out. So this task
**runs no simulation**. It only measures and reads, so that the manager can fix the inputs, the draw count
and the worker count, and then launch.

## Task

READ-ONLY, apart from this file and scratch scripts in the session scratchpad. Answer Q1 to Q6 with `file:line`
or file path plus the exact value read.

**Q1. Time and memory per simulation (from the pilot, no new runs).**
- In `BatchAll_MC_N3_1776120359/NUS_RC*/{Default,iter_*}/**`, read each simulation's EnergyPlus elapsed time
  (`eplusout.end` or the last lines of `eplusout.err`: "Elapsed Time").
- From the file timestamps, work out how many ran at the same time.
- Report per neighbourhood: the number of simulations, the median and max minutes per simulation, and the
  concurrency.
- Then estimate the wall-clock time of a full re-run (6 neighbourhoods; 1 Default plus N draws x 5 years
  each) for N = 10 and N = 20, with 4 and with 8 parallel workers. State the assumptions.
- If any log records peak memory, report it. If none does, say NOT FOUND.

**Q2. Dwelling-type labels: will each building get a household of its own type?**
- List the dwelling types each neighbourhood's buildings are assigned. Use
  `eSim/eSim_bem_utils/neighbourhood.py` (the function around lines 464-503) on
  `BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf`: import and call it, do not simulate.
- List the distinct `DTYPE` labels and household counts in each candidate schedule file:
  - April set: `BEM_Setup/BEM_Schedules_2005_PRE_STEP8_BAK.csv`, `..._2015_PRE_STEP8_BAK.csv`,
    `..._2022_CLASSIC_BAK_2026-05-31.csv`, `BEM_Schedules_2025.csv`;
  - June set: `BEM_Setup/BEM_Schedules_2005.csv`, `_2010.csv`, `_2015.csv`, `_2022.csv`.
- With `DTYPE_FALLBACK` (`eSim/eSim_bem_utils/main.py:49-58`), say for each set and each neighbourhood which
  buildings would get a household of a *different* type (for example, row houses getting detached-house
  households because the file has no `Attached` label).

**Q3. The June files.**
- Which script wrote `BEM_Setup/BEM_Schedules_2005/2010/2015.csv` on 2026-06-08?
- What bug did the `*_BUG4H_BAK_2026-06-08.csv` backups precede? Search the 2J docs
  (`2J_docs_occ_nTemp/`), for example for "BUG4H", "4H" or "BEM_Schedules_2005".
- Confirm that 2005, 2010 and 2015 differ in their schedule values: per file, stream the mean
  `Occupancy_Schedule` and the mean `Metabolic_Rate`.
- Report the mean daily occupied hours per file, so the manager can compare them with the paper's
  Section 4.1 values (2005 15.5 h, 2010 11.9 h, 2015 17.5 h, 2022 15.9 h).

**Q4. Is there a correct April-era 2010 schedule file anywhere on this machine?** Look for example in
`0_Occupancy/Outputs_11CEN10GSS/occToBEM/`, other `BEM_Setup/*BAK*` files, and `_local_runs\`. Give its path,
columns, household count and dwelling-type labels, and whether its format matches the April 2005 file.

**Q5. Pairing and seeds.** In `main.py:1970-2135` (`_run_mc_neighbourhood`) and `run_batch_hpc.py`:
- Is the random draw seeded? Give the seed and its `file:line`, or "not seeded".
- For iteration k, do all five years use households matched to the *same* base households (paired
  design)? Quote the lines.

**Q6. How to launch it locally, non-interactively.**
- Give the exact command that runs the six-neighbourhood Monte Carlo batch from the command line
  (`run_batch_hpc.py` arguments, or another entry point) with a chosen N, output folder and worker count.
- Name the worker-count environment variable (`eSim/eSim_bem_utils/simulation.py:156-160`).
- Name the EnergyPlus executable and weather file it uses on this machine, and where it writes.
- Say whether it can resume after an interruption (skips finished iterations) or starts again.

## Rules

- **Run no EnergyPlus simulation, and start no batch.** Another heavy local run is going on, and a memory
  freeze locks the author out of this machine.
- **Never load a whole schedule file into memory** (they are 77 to 674 MB). Stream them line by line (the
  `csv` module or `awk`). One process at a time, no parallel scans.
- Python: `py` (3.13, pandas) or `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`.
  Bare `python` is a broken stub.
- Do not touch the cluster. Change, move or delete nothing outside this file and the scratchpad.
- NOT FOUND beats a guess. Write state into this file as you go.
- Stop at about 150k tokens of context, write state, and say "handoff needed".
- End your turn with a one-line status and the path of this file.

## Verified
(employee fills)

## Findings Q1-Q6
(employee fills)

## Decisions
(anything this task did not decide, and what was assumed)

## Next
(exact next action for a cold agent)

## WHAT I DID NOT VERIFY
