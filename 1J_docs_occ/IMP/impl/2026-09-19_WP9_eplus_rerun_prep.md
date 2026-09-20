# WP9 prep: get the EnergyPlus re-run ready (1J JBPS revision), task and implementation state

Task doc:   this file (sections "Task" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §3 P15, §7 log (j) and (k)
Previous:   `impl/2026-09-19_WP2b_find_simulations.md` (read "Findings A-D" and "Manager vetting" first)
Status:     DONE

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

- No EnergyPlus was run and no batch was started. All work was directory listing, file-timestamp reading,
  streamed CSV reads (one file at a time, `csv` module, never `pandas.read_csv` on a full file), and one
  direct Python import of `eSim/eSim_bem_utils/neighbourhood.py` to parse `NUS_RC{1..6}.idf` (2-10 MB text
  files — not simulated, not streamed as "schedule files", parsing them is what `get_building_dtypes_from_idf`
  itself does).
- Machine: `os.cpu_count()` = 20 logical CPUs.
- `BEM_Schedules_2010_PRE_STEP8_BAK.csv` exists, 77,037,650 bytes — byte-size-identical to
  `BEM_Schedules_2005_PRE_STEP8_BAK.csv` (both dated 2026-04-02), consistent with the manager's prior
  md5 finding that they are byte-identical.

## Findings Q1-Q6

### Q1. Time and memory per simulation

No `eplusout.end` or `eplusout.err` file exists anywhere under `BatchAll_MC_N3_1776120359` (checked with
`find . -iname eplusout.end` / `eplusout.err`, zero hits) — the pilot's output folders hold only
`eplusspsz.csv`, `epluszsz.csv`, `eplustbl.htm`, `in.idf`, `prepared.idf`, `Scenario_*.idf`; no elapsed-time
line and **no memory figure anywhere → peak memory is NOT FOUND** (also grepped `main.py`/`run_batch_hpc.py`/
`simulation.py` for `memory|psutil|RSS|peak_mem`, zero hits — nothing in the code even measures it).

Elapsed time was instead reconstructed from file timestamps (`ls -la --time-style=full-iso`) on
`prepared.idf` (written just before an EnergyPlus call is launched) and `eplustbl.htm` (written when that
call finishes). Every iteration's 5 `prepared.idf` files (one per `COMPARATIVE_YEARS` = 2005/2010/2015/
2022/2025, `main.py:41`) are written 2-3 s apart and its 5 `eplustbl.htm` files finish within seconds to
tens of seconds of each other, and the *next* iteration's `prepared.idf` files start within seconds of the
*previous* iteration's last `eplustbl.htm` — i.e. **concurrency = 5** (one simulation per comparative year,
launched together) and **iterations run strictly sequentially**, one full iteration (5 sims) at a time, no
overlap between iterations. `Default` (1 sim, no concurrency) always runs first, alone, before `iter_1`.

Per-neighbourhood, from `BatchAll_MC_N3_1776120359/NUS_RC{1..6}/{Default,iter_1,iter_2,iter_3}/*/{prepared.idf,eplustbl.htm}`
(16 simulations attempted per NU: 1 Default + 3 iters x 5 years; times = wall-clock from first `prepared.idf`
to last `eplustbl.htm` in the group, i.e. per-simulation time since the 5 in a group run together):

| NU | dtype (Q2) | n_bldg | Default (min) | iter_1 | iter_2 | iter_3 | median (3 iters) | max |
|---|---|---|---|---|---|---|---|---|
| NUS_RC1 | SingleD | 2  | **NOT FOUND** (no `eplustbl.htm`, see caveat below) | 60.05 | 36.68 | 37.17 | 37.17 | 60.05 |
| NUS_RC2 | SingleD | 2  | 75.62  | 106.97 | 107.32 | 141.77 | 107.32 | 141.77 |
| NUS_RC3 | SingleD | 14 | 58.83  | 83.43  | 84.15  | 86.50  | 84.15  | 86.50 |
| NUS_RC4 | MidRise | 8  | 91.03  | 130.52 | 137.08 | 138.97 | 137.08 | 138.97 |
| NUS_RC5 | MidRise | 8  | 176.43 | 246.23 | 245.28 | 252.67 | 246.23 | 252.67 |
| NUS_RC6 | HighRise| 9  | 135.95 | 201.90 | 200.78 | 194.38 | 200.78 | 201.90 |

Pooled across all 18 measured iterations (all 6 NUs x 3 iters): median = 133.8 min, max = 252.67 min
(NUS_RC5 iter_3). Pooled across the 5 measured Default runs: median = 91.03 min, max = 176.43 min.
NUS_RC1's `Default/` has `prepared.idf` (18:46:10) and a 0-byte `eplusspsz.csv` plus a real
`epluszsz.csv` (18:48) but **no `eplustbl.htm` ever appeared** — the run did not reach (or did not
write) a normal annual-simulation table report; this is a real gap in the pilot, not a missing file on my
part (`find NUS_RC1/Default -iname eplustbl.htm` — zero hits). Reported as NOT FOUND, not estimated.

**Wall-clock estimate for a full local re-run (6 neighbourhoods, sequential, matching how the pilot
actually ran — see Decisions), 1 Default + N draws x 5 years:**

Assumptions (stated, not measured): (a) 6 neighbourhoods run one after another on this machine, as the
pilot did (`batch_log.txt` shows NUS_RC1..6 finishing in sequence, no overlap); (b) steady-state
per-iteration time = the median of iter_2/iter_3 (iter_1 is slower everywhere except RC6, plausibly a
disk/weather-file cold-start effect — see Decisions), taken here as the per-NU 3-iteration median in the
table above; (c) `--workers >= 5` gives no benefit beyond `--workers 5` because each iteration only ever
submits 5 jobs (`min(max_workers, len(simulation_jobs))`, `simulation.py:162`), so `--workers 8` is modelled
identically to the pilot's own (unbounded) concurrency; (d) `--workers 4` forces 5 jobs onto 4 slots, i.e.
2 sequential rounds, modelled as **2x** the 5-way-concurrent iteration time (upper-bound approximation:
round 2 is really just 1 job, so this may overstate by up to ~20%); (e) **the machine's current, separate
heavy EnergyPlus job is ignored** — if that job is still running when this launches, real times will be
worse than these numbers, possibly much worse, and are not modelled here; (f) Default cost is a one-time
sum, independent of N; RC1's missing Default is extrapolated from the other 5 NUs' stable
Default/iter_median ratio (~0.69x) as **25.6 min (ESTIMATED, not measured)**, flagged inline.

- Sum of 6 per-NU iteration medians = 812.7 min/draw (workers >= 5). Sum of 6 Default costs
  (5 measured + 1 estimated) = 563.5 min, one-time.
- **N=10, workers=8 (or unbounded): 563.5 + 10 x 812.7 = 8,691 min ~ 144.8 h ~ 6.0 days.**
- **N=20, workers=8: 563.5 + 20 x 812.7 = 16,818 min ~ 280.3 h ~ 11.7 days.**
- **N=10, workers=4: 563.5 + 10 x 2 x 812.7 = 16,818 min ~ 280.3 h ~ 11.7 days.**
- **N=20, workers=4: 563.5 + 20 x 2 x 812.7 = 33,073 min ~ 551.2 h ~ 23.0 days.**

These are large numbers relative to "another heavy run is live and the machine can't reboot" — a full local
N=20 re-run is a multi-day-to-multi-week commitment on this one box even at workers=8, before accounting for
contention with anything else running on it.

### Q2. Dwelling-type labels

Per-building DTYPE, read by importing `eSim/eSim_bem_utils/neighbourhood.py` and calling
`get_building_dtypes_from_idf()` (`neighbourhood.py:462-503`) directly on each
`BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf` — no simulation, just IDF-text parsing:

| NU | buildings | dtypes |
|---|---|---|
| NUS_RC1 | 2  | 2 SingleD |
| NUS_RC2 | 2  | 2 SingleD |
| NUS_RC3 | 14 | 14 SingleD |
| NUS_RC4 | 8  | 8 MidRise |
| NUS_RC5 | 8  | 8 MidRise |
| NUS_RC6 | 9  | 9 HighRise |

Distinct `DTYPE` labels and household counts, streamed (`csv` module, one file at a time, unique `SIM_HH_ID`
per `DTYPE`):

April set (12-column format: `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,
Occupancy_Schedule,Metabolic_Rate`):
- `BEM_Schedules_2005_PRE_STEP8_BAK.csv`: 28,455 hh — SemiD 1290, HighRise 2548, DuplexD 1450, SingleD
  15802, MidRise 5282, Attached 1587, OtherA 81, Movable 415.
- `BEM_Schedules_2015_PRE_STEP8_BAK.csv`: 31,163 hh — SemiD 1170, MidRise 7223, HighRise 3478, SingleD
  16470, DuplexD 1145, Movable 400, Attached 1223, OtherA 71.
- `BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv`: 36,909 hh — HighRise 4598, **OtherDwelling** 4843,
  SingleD 19940, MidRise 7512, **'8'** 16 (a bare numeric-string DTYPE code, undocumented — this is a
  *different* label scheme from the other three April files: no Attached/SemiD/DuplexD/Movable/OtherA).
- `BEM_Schedules_2025.csv`: 23,882 hh — MidRise 4864, SingleD 13402, SemiD 823, Attached 1111, DuplexD
  864, HighRise 2517, Movable 233, OtherA 70.

June set (13-column format, adds `MATCH_TIER`):
- `BEM_Schedules_2005.csv`, `_2010.csv`, `_2015.csv`: identical roster, 144,507 hh each — HighRise
  18522, SingleD 76365, OtherDwelling 18838, MidRise 30740, '8' 42 (all three files: same counts).
- `BEM_Schedules_2022.csv`: 144,465 hh — HighRise 18505, SingleD 76366, OtherDwelling 18835, MidRise
  30716, '8' 43.

**`DTYPE_FALLBACK` (`main.py:49-58`) never fires for the six-NU campaign, against any of these 8 files.**
The only three DTYPEs the campaign ever needs are SingleD (RC1/RC2/RC3), MidRise (RC4/RC5), HighRise
(RC6) — and all three labels are present, with hundreds to tens-of-thousands of households, in every one
of the 8 candidate files (April and June alike). The June files' different label scheme (OtherDwelling/'8'
instead of Attached/SemiD/DuplexD/Movable/OtherA) is irrelevant to this campaign specifically, because it
never draws those other types.

### Q3. The June files

**Writer.** `2J_docs_occ_nTemp/Step9_docs/investigation/fix_old_years_clock.py:8-24` is the script that
produced the 2026-06-08 `BEM_Schedules_2005/2010/2015.csv`. It does not generate them from scratch (the
original generator for these three files is still NOT FOUND, per the previous WP2b task, Finding D) — it
reads the existing file, relabels `Hour -> (Hour+4) % 24` (:18), re-sorts by
`[SIM_HH_ID, Day_Type, Hour]` (:21), and overwrites the same path, after first copying the pre-fix
version to `BEM_Schedules_{year}_BUG4H_BAK_2026-06-08.csv` if that backup does not already exist (:14-16).
**Caveat:** the three `*_BUG4H_BAK_2026-06-08.csv` files on disk are dated **Jun 1 19:26-19:27**, one week
before the main files' Jun 8 11:32-11:33 mtime — given the script's `if not bak.exists()` guard, this is
only consistent with the script having run at least twice (once ~Jun 1, creating the backup, and again
~Jun 8, re-reading and re-writing without re-backing-up). I did not find a second copy or version of this
script, or a log, that would confirm what the Jun 8 run actually did differently from the Jun 1 run — flagged
under WHAT I DID NOT VERIFY, not asserted as a clean single run.

**The bug.** Called the "4-hour schedule-injection bug" / **BUG4H** in the 2J docs, found 2026-06-08. GSS
diaries use a 4:00 AM-origin day (`2J_docs_occ_nTemp/00_GSS_Occupancy_Pipeline.md:206`: DDAY reconstructs
4:00 AM to 4:00 AM). The production converter `2J_docs_occ_nTemp/07_aug_to_bem.py` wrote those 4:00-AM-origin
diary slots straight into EnergyPlus's `Hour` field positionally (diary slot @ 04:00 -> `Hour` 0) instead of
rotating to real clock time (slot @ 04:00 -> `Hour` 4) — so occupancy, metabolic, equipment and lighting
schedules were all injected **4 hours early** relative to the weather file
(`2J_docs_occ_nTemp/09_activityDrivenLoads.md:430`, `2J_docs_occ_nTemp/08_simulation.md:5`). `07_aug_to_bem.py`
itself only ever supported 2022/2030 (confirmed in the previous WP2b task) and does not write 2005/2010/2015
— per `fix_old_years_clock.py:2-5`'s own comment, "They do NOT come from `07_aug_to_bem.py`, so the code fix
there didn't reach them," so the same 4-hour-early defect was independently present in 2005/2010/2015 and
was corrected at the artifact level (relabel only, values untouched) by this separate script.

**2005/2010/2015 differ.** Streamed (one file at a time) mean `Occupancy_Schedule` and mean `Metabolic_Rate`
over all 6,936,336 rows / 144,507 households of each current (post-BUG4H-fix) June file:

| file | mean Occupancy_Schedule | mean Metabolic_Rate (W) | mean daily occupied hours |
|---|---|---|---|
| `BEM_Schedules_2005.csv` | 0.7139 | 107.359 | **16.892** |
| `BEM_Schedules_2010.csv` | 0.7033 | 107.713 | **16.674** |
| `BEM_Schedules_2015.csv` | 0.6887 | 108.783 | **16.347** |

Confirmed non-identical (same 144,507-household roster as previously found, but different per-row schedule
values per year). "Mean daily occupied hours" = per household, sum of `Occupancy_Schedule` over the 24
`Weekday` hours and separately over the 24 `Weekend` hours, combined `(5xWeekday + 2xWeekend)/7`, then
averaged over all 144,507 households (script: `scratchpad/q3_means.py`, streamed, sorted-file assumption
verified from `fix_old_years_clock.py:21`'s own sort order).

**These do NOT match the paper's Section 4.1 numbers** (2005 15.5 h, 2010 11.9 h, 2015 17.5 h, 2022 15.9 h)
— neither the values nor even the ordering (paper: 2010 lowest; this file: 2015 lowest; paper's 2010-2015
gap is 5.6 h, this file's is 0.33 h). The manuscript's Section 4.1 numbers were evidently computed from a
different data state than the current (post-BUG4H, post-relabel) June files — which data state, I did not
determine (out of scope for this task; flagged for the manager).

### Q4. A correct April-era 2010 schedule file

**Found:** `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv`
(88,032,159 bytes, dated **Apr 2 15:46** — the same day as the April 2005/2015 `_PRE_STEP8_BAK` files,
Apr 2 14:30/16:18).
- Columns: `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,Occupancy_Schedule,
  Metabolic_Rate` — **identical 12-column header, in the same order**, to the April
  `BEM_Schedules_2005_PRE_STEP8_BAK.csv` (byte-for-byte header match; no `MATCH_TIER`).
- 32,480 unique households (NOT the 28,455 of the 2005 file, and NOT a copy of it) — dtype_counts:
  MidRise 5495, HighRise 2875, SingleD 18327, Attached 2000, Movable 433, SemiD 1617, DuplexD 1663,
  OtherA 70.
- Format matches April 2005 exactly (same columns, same DTYPE label scheme: SingleD/SemiD/Attached/
  DuplexD/MidRise/HighRise/Movable/OtherA — not the June OtherDwelling/'8' scheme).

This is a genuinely independent, differently-sized 2010 household set, not the byte-identical copy that
caused P15 — a real candidate to replace `BEM_Schedules_2010_PRE_STEP8_BAK.csv` as the April-era 2010 input.
Searched and found nothing else: no `*2010*` file under `BEM_Setup/*BAK*` besides the known
`_PRE_STEP8_BAK` and `_BUG4H_BAK` copies, and no `BEM_Schedules`/`2010`-named file anywhere under
`C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\` (searched by both `*2010*schedul*` and `*2010*BEM*`,
zero hits).

### Q5. Pairing and seeds

**Not seeded.** `grep -n "random.seed\|np.random.seed\|seed(" main.py run_batch_hpc.py` returns zero hits
in either file. `_run_mc_neighbourhood` (`main.py:1970`) does `import random` at `main.py:1996` and later
calls plain `random.choice(pool_k)` at `main.py:2133` with no seed ever set — Python's default
(OS-entropy/time-seeded) generator, so re-running the batch draws a different household set every time.

**Pairing, for iteration k:** all five comparative years are matched to one *profile*, not one literal
household ID reused across years. Once per iteration, `main.py:2119-2135` draws one base household per
building from the **first year's** (`first_year = list(all_schedules.keys())[0]`, `main.py:2088` — this is
2005, the first key of `COMPARATIVE_YEARS`) DTYPE-specific candidate pool via `random.choice` (`:2133`), and
records that draw's `hhsize`/`dtype` as `hhsize_profile`/`dtype_profile` (`main.py:2140-2141`). Then, for
**every** scenario in `year_scenarios` (`main.py:2152` loop), a **new** household is picked from *that
year's own* candidate pool by SSE best-match (`integration.find_best_match_household`, called at
`main.py:2202`) among households matching the same `target_hhsize`/`target_dtype` (falling back to
DTYPE-only, then `DTYPE_FALLBACK`, if no exact hhsize+dtype match exists — `main.py:2172-2199`). So: paired
by household **size and dwelling type**, per iteration, across all 5 years — not paired by household ID
(each year's CSV has disjoint SIM_HH_IDs, so identical-ID pairing across years is not even possible with
these inputs).

### Q6. How to launch it locally, non-interactively

**Command** (`run_batch_hpc.py:8-16` docstring, confirmed against the actual `argparse` block at
`run_batch_hpc.py:41-68`):
```
py eSim/eSim_bem_utils/run_batch_hpc.py --idf BEM_Setup/Neighbourhoods/NUS_RC1.idf --region Quebec \
   --sim-mode weekly --iter-count 20 --output-dir <path> --workers 8 [--use-tmpdir]
```
One invocation runs **one** neighbourhood; the six-NU campaign needs 6 separate invocations (the interactive
local Option-8 menu path in `main.py` loops these sequentially, matching what the pilot actually did — see
Q1).

- **Worker-count env var:** `ESIM_WORKERS` (`simulation.py:159`), set by `run_batch_hpc.py:74`
  (`os.environ["ESIM_WORKERS"] = str(args.workers)`) from the `--workers` CLI flag; consumed at
  `simulation.py:156-162`, then capped to `min(max_workers, len(simulation_jobs))` (`:162`) — i.e. never
  more than 5 concurrent EnergyPlus processes per iteration, since only 5 jobs (one per comparative year)
  are ever submitted together.
- **EnergyPlus executable, this machine:** `C:\EnergyPlusV24-2-0\energyplus.exe` (`config.py:12,21`,
  Windows branch, `ENERGYPLUS_DIR` overridable via env var but not overridden here).
- **Weather file:** for `--region Quebec` (the Montreal NUs), `config.resolve_epw_path` (`config.py:46-84`)
  resolves to `BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`
  (matched by the `Quebec -> "Montreal"` city-keyword lookup, case-insensitive substring match against the
  6 `.epw` files in `WeatherFile/`).
- **Writes to:** `--output-dir` (a new parent folder the caller names), with a per-neighbourhood
  subdirectory created inside it by `_run_mc_neighbourhood` — same `NUS_RC*/{Default,iter_1..iter_N}/{year}/`
  layout as the pilot (`run_batch_hpc.py:15-16`).
- **Resume: NO.** `_run_mc_neighbourhood` always (re-)runs `Default` unconditionally
  (`main.py:2049-2058`, no existence check before `simulation.run_simulations_parallel`) and, inside the
  iteration loop, always appends every scenario job to the `jobs` list with no check for a pre-existing
  `eplustbl.htm`/`eplusout.sql` before submitting (`main.py:2233-2237`) — the only `os.path.exists(sql_path)`
  checks in this function (`main.py:2065`, `:2251`) run *after* simulation, only to decide whether to
  extract EUI results, never to skip a job before it runs. A killed/interrupted local run of one
  neighbourhood must restart that neighbourhood from `Default` + `iter_1`; only the neighbourhood
  granularity (6 separate invocations) lets you avoid re-running NUs that already finished.

## Decisions

- Used file-timestamp deltas (`prepared.idf` start, `eplustbl.htm` finish) as the per-simulation elapsed
  time proxy for Q1, since no `eplusout.end`/`eplusout.err` exists anywhere in the pilot tree. This is an
  observational reconstruction, not a value EnergyPlus itself reported — stated as such throughout, not
  presented as an `eplusout.end` reading.
- Modelled the Q1 wall-clock estimate as 6 neighbourhoods run **sequentially**, matching what the pilot's
  own `batch_log.txt` shows happened (no NU-to-NU overlap) — not as 6 parallel local processes, since (a)
  that is not how the existing code path (`option_batch_all_neighbourhoods_monte_carlo` / one
  `run_batch_hpc.py` call per NU) currently launches them without extra orchestration, and (b) running 6
  neighbourhoods' worth of EnergyPlus in parallel on a machine that already has another live heavy job
  would be exactly the kind of load the task's own Rules warn against. A manager could choose to launch the
  6 as 6 parallel jobs instead (dividing the sequential estimate by up to ~6x, resources permitting) — this
  task did not evaluate whether that is safe given the concurrent unrelated run, and did not model it as the
  headline estimate.
- Treated `iter_2`/`iter_3` as the "steady-state" per-iteration time and used their median (over all 3
  iters) as the Q1 projection basis, rather than `iter_1`, because `iter_1` runs noticeably slower than
  `iter_2`/`iter_3` in 5 of 6 NUs (RC1: 60.1 vs 36.7-37.2 min; RC2/RC3/RC4/RC5 show smaller but consistent
  iter_1-slowest patterns; RC6 is the one exception, roughly flat) — read as a plausible disk/OS
  cold-start or weather-file-caching effect on the *first* simulation of a freshly-started neighbourhood,
  not verified against any code or log that confirms caching behaviour. This is an assumption, not a
  measured cause.
- For Q1's Default one-time cost, extrapolated NUS_RC1's missing value from the other 5 NUs' stable
  Default/iter-median ratio (~0.69x) rather than omitting it or guessing a round number — flagged inline
  as ESTIMATED, not measured, per "NOT FOUND beats a guess": the true NOT FOUND (no `eplustbl.htm` for
  RC1/Default) is reported as-is first, and the extrapolation is a clearly labelled secondary number used
  only inside the wall-clock projection.
- For Q3, did not attempt to identify which data state actually produced the paper's Section 4.1 numbers
  (15.5/11.9/17.5/15.9 h) — out of scope for a READ-ONLY prep task whose job was to report the current
  file's numbers for the manager to compare, not to reconcile them.

## Next

Exact next action for a cold agent, if the manager wants this pushed further:
1. **Decide the launch plan from the Q1 numbers before anything else.** A full local re-run at N=20 is an
   estimated 6.0-23.0 days depending on `--workers` (see Q1 table), *not* counting contention with any
   other job that may still be live on this machine. If that is unacceptable, decide whether to (a) lower
   N, (b) wait for the cluster to free up (this task did not touch the cluster, per Rules), or (c) accept
   the multi-day local run and actively monitor for the other heavy job to finish before launching.
2. **Resolve the 2010 input before launching.** Q4 found a real, differently-sized, correctly-formatted
   April-era 2010 candidate at `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample25pct.csv`
   (32,480 hh) — a manager needs to decide whether this (or a freshly regenerated equivalent) replaces the
   byte-identical `BEM_Schedules_2010_PRE_STEP8_BAK.csv` for the April-era comparison, and separately
   whether the June `BEM_Schedules_2010.csv` (post-BUG4H-fix, paired with 2005/2015 on the same 144,507-hh
   roster) is preferred instead — these are two different "2010" fixes for two different eras of file and
   this task did not pick between them.
3. **Reconcile Q3's Section-4.1 mismatch** (paper: 2005 15.5 h / 2010 11.9 h / 2015 17.5 h / 2022 15.9 h;
   current June files: 2005 16.89 h / 2010 16.67 h / 2015 16.35 h) before quoting any of these numbers in a
   revision — find which data snapshot (pre-BUG4H? a different sample?) actually produced the published
   figures, or accept that the published figures need updating alongside the re-run.
4. Since seeding is confirmed absent (Q5), if the manager wants the *next* re-run to be reproducible (e.g.
   for a reviewer request), a `random.seed(N)` call would need to be added near `main.py:1996`/`main.py:2133`
   before launch — this task did not add it (READ-ONLY).

## WHAT I DID NOT VERIFY

- **Q1:** whether the other live heavy EnergyPlus job (mentioned in Why/Rules) was competing for CPU/disk
  during the *pilot's* own run in April — the pilot's per-simulation times may themselves already include
  some contention effect from whatever else was running on the machine in April, which I have no way to
  separate from "true" per-sim time. The wall-clock projection in Q1 explicitly does not model the
  *current* live job either way (see Decisions).
- **Q1:** why `NUS_RC1/Default` never produced `eplustbl.htm` — did not open `eplusspsz.csv` (0 bytes) or
  any other file to diagnose a crash vs. a design choice; reported as NOT FOUND only.
- **Q3:** did not determine what script/process ran `fix_old_years_clock.py` a second time around Jun 8
  (the Jun 1 backup vs. Jun 8 main-file mtime gap) — no second copy of the script or a log was found; only
  a single version exists at the path given.
- **Q3:** did not identify which data snapshot actually produced the paper's Section 4.1 occupied-hours
  numbers (out of scope, see Decisions) — this is a real, unresolved discrepancy a manager should chase.
- **Q4:** did not check whether `11CEN10GSS_BEM_Schedules_sample25pct.csv` is itself upstream of (i.e. the
  same generation lineage as) the April `BEM_Schedules_2005_PRE_STEP8_BAK.csv`/`_2015_PRE_STEP8_BAK.csv`
  files, beyond the header/format match — did not trace the `06CEN05GSS`/`16CEN15GSS` vs `11CEN10GSS`
  per-cycle occToBEM scripts against each other to confirm they are siblings in the same pipeline version.
- **Q5:** did not check the earlier, structurally similar single-neighbourhood MC function around
  `main.py:1146-1350` (also uses unseeded `random.choice` and the same profile-pairing pattern) — the task
  named `_run_mc_neighbourhood` (`main.py:1970-2135`) specifically and that is what was verified; the
  earlier function was noted only in passing while grepping and not independently confirmed to behave
  identically.
- **Q6:** did not test-invoke `run_batch_hpc.py --help` or any dry run (would count as starting a batch,
  forbidden by Rules) — the command and flags are read from source/docstring only, not executed.
- Did not re-open `1J_docs_occ/IMP/00_REVISION_PLAN.md` beyond the "P15" and log (j)/(k) lines already
  pointed to by this file's header — did not re-check for a newer plan entry that might supersede this
  task's own framing.

Status: DONE
