# TASK (employee, Sonnet): 5J Step 4: gate definitions, scorer, noise floor, perturbation table (validation only)

Written 2026-09-30 18:57 EDT (from `date`) by the 5J manager. Read first, in full: `Step4_docs/5thJ_04_freezeGates.md`
(the spec: 4A, 4B, 4C) and `Step4_docs/5thJ_04_freezeGates_val.md` (every gate you must print), the Overview table of
gates (`5thJ_00_Occupancy_Surrogate_Pipeline_Overview.md`, around line 109), `Step3_docs/impl/2026-09-30_wp2_campaign_part2.md`
(splits, replicates, loader) and `tools/speed/split_loader.py`, `tools/speed/camp_integrity.py`.
State file: create `Step4_docs/impl/2026-09-30_freeze.md` (Task doc / Status / Ledger / Verified / Decisions / Next /
WHAT I DID NOT VERIFY); `date` before every stamp.

## Hard rules
* 🔴 ALL compute on Speed via sbatch (`-p ps -t 7-00:00:00 --exclude=antenna1`, `-c` up to 8, `--mem` up to 32G,
  python `/speed-scratch/o_iseri/envs/step4/bin/python -u`; at most 30 CPUs in total at once). Locally ONLY edit/write
  files, ssh/scp, ls, read small files. Login node: sbatch/squeue/sacct/scancel/scp/ls, single-file cat/tail/wc -l.
  At most 6 sacct checks of 30 s per job; then "manager to read" and stop.
* 🔴 NO TEST DATA: read runs ONLY through `split_loader.load_split` and ONLY `development`, `validation`, `b0_dev`,
  `b0_val`, `replicates`. Never read a `test_*`, `b0_test` or `unused` run, never create `gates_frozen.md5`
  (the manager does that after the author gives the ASHRAE page). Log every file opened by the scorer; gate 2.3
  checks that log has 0 test opens.
* 🔴 UK licence: Spain and Italy only; no UK file; no folder-wide search or wildcard that could match a UK file.
* Speed folder `R=/speed-scratch/o_iseri/5J/freeze/` (create). Campaign outputs read-only.
* Past ~150k tokens: stop, write state, "handoff needed".

## Manager rulings for this step (write them into `gates_frozen.md` with "ruled by the manager 2026-09-30")
1. **Pairs under "every flat tested" (D2-8, ruling A).** A pair = two households A, B in the SAME flat index of the
   same building and the same climate, in two different runs, both runs in the same split. For SFH/TH that is the
   pre-registered pair exactly; for MFH/AB the neighbours differ between the two runs, so ΔEP includes a neighbour
   effect: this is stated as a limitation, not removed. All such pairs are used (enumerate them; count per class,
   split, country). Secondary score, reported not gated: each flat's effect against the same flat of its B0 run
   (average household everywhere).
2. **Scores work on pair-level sufficient statistics** (per pair and target: n, ΣΔEP, ΣΔS, ΣΔEP², ΣΔS², ΣΔEP·ΔS,
   Σ(ΔEP−ΔS)², annual ΣΔEP and ΣΔS), so R² over the hours of all pairs of a class and the bootstrap never hold
   hourly pair series in memory. Write the formula for R² from these sums and test it against a direct computation
   on 20 pairs (equal to 1e-9).
3. **Noise floor.** Per target and class: SD of the annual total over the repeats of one input, from the 200
   Step 3 replicates (10 repeats x 20 inputs). The campaign measured spread 0 kWh on every target, so the floor is
   0 and "above the floor" means ΣΔEP ≠ 0 at the file resolution (write the resolution: `%.8g`). Write plainly that
   the 4J non-determinism did not reproduce in 5J. k = 2 stays. The < 30 pairs NOT_EVALUABLE rule stays and is seen
   failing with a planted high floor (val 5.2).
4. **"Good" stand-in.** Because the floor is 0, the "good" stand-in = EnergyPlus + Gaussian noise with SD = 10 % of
   that run's hourly SD per target (seed fixed), NOT noise at the floor size (that would be EnergyPlus itself). It
   must pass every gate (val 2.0). The "B1" stand-in for the null = the same construction with an independent seed.
5. **Targets scored:** heating, cooling, equipment electricity, total electricity (COP 3.0 ASSUMED), per class
   (SFH, TH, MFH, AB) and per country; never pooled over classes or end uses. G5J.5 uses total electricity.
6. **G5J.2 band:** CV(RMSE) ≤ 30 % and |NMBE| ≤ 10 % hourly, written as "ASHRAE Guideline 14, a reference; SOURCE
   PAGE PENDING (author)". Everything else can be final; the band line keeps this marker until the author gives the
   page, and gate 1.1 prints FAIL until then (that is expected, write it).

## Parts
A. `outputs_step4/gates_frozen.md`: every definition of spec 4A with the rulings above, every threshold with its
   source or "chosen by the author/manager on <date>" (val 1.2), the exit-code meaning (spec 4C), the bootstrap
   (two-way cluster: buildings and households resampled independently, pairs kept when both households AND the
   building are drawn, 2,000 resamples, fixed seed; never by hour or run), and the pair rule.
B. Scorer `tools/speed/5thJ_04_scorer.py` (+ sbatch): inputs = a predictions folder laid out like `extracted/` and
   a split name; outputs one line per gate per class per target and `SUMMARY PASS=.. FAIL=.. NOT_EVALUABLE=..`; exit
   0/1/2 as in 4C; a crashed section prints NOT_EVALUABLE. The bootstrap function is named for what it does
   (`two_way_cluster_bootstrap`), resampling unit cited by line (val 3.1, 3.3).
C. Noise floor table (val 5.1) and the planted high-floor NOT_EVALUABLE (val 5.2).
D. Perturbation table on the VALIDATION split (`outputs_step4/perturbations.md`, spec 4B): the good stand-in, then
   each row (delete one run -> G5J.1; training-mean per hour of year -> G5J.2; building-mean over households ->
   G5J.3, with the G5J.2 verdict of that row written per target and class = the paper's premise, val 2.1b; shift 2 h
   -> G5J.5; good stand-in as its own control -> G5J.4 reads "control passes"). Before/after verdict lines printed.
E. Bootstrap null (val 3.2): S = B1 stand-ins, 200 null repetitions, share of intervals covering 0 (pass ≥ 93 %).
   Size the jobs so the whole step stays under 30 CPUs; write CPU-hours used.
F. Planted crash (val 4.3): one section raises; SUMMARY shows NOT_EVALUABLE and exit 1.
G. The test reader: show `load_split("test_new_households")` refused now (val 4.2 first half); the second half
   (opens after the freeze) is the manager's, after the ASHRAE page.

## Report back (short, plain)
Pair counts per class/country (validation); noise floor table; good stand-in SUMMARY; the five perturbation rows
(before/after lines); bootstrap null coverage; planted-crash lines; the refusal line; md5 of `gates_frozen.md` and the
scorer (inside a job); JobIDs; CPU-hours. Status "DONE except freeze (ASHRAE page pending)", Next = "manager verifies;
author gives the ASHRAE Guideline 14 page; manager freezes".

## What the manager will re-derive
One pair's R² contribution from the two runs' extracted files against the sufficient statistics; the pair count of
one building; the null coverage number from the job output; that the scorer's file-open log has 0 test files.
