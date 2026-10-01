# TASK (employee, Sonnet): 5J Step 7 part B: the draws, the EnergyPlus check, speed, outputs

Written 2026-10-01 05:46 EDT by the 5J manager (`date` before every stamp you write). Read first, in full:
`Step7_docs/impl/2026-10-01_step7_design.md` (R7-1 to R7-5), `Step7_docs/impl/2026-10-01_wp5_district.md` (part A state, incl.
the MANAGER rulings of 04:34 and 05:46: uniform draws; N rule and writers), `Step7_docs/impl/2026-10-01_wp5_district_TASK.md`
(hard rules: they bind you unchanged), `Step7_docs/5thJ_07_speedDistrict.md` and `_val.md`, and the part A code
`tools/speed/s7_*.py` (reuse it; change nothing that part A sealed). State file: append to `..._wp5_district.md` under
"## PART B" (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules (short)
As part A. Sealed inputs (`district/in/SEALS.md5`) are checked at the start of every job and never rewritten. Pinned S3 only
(md5 78271da9...). GPU at most 4 slices; all 5J jobs <= 30 CPUs. Spain only. Never wait: submit the chain, write JobIDs, end.

## Parts (one chain)
A. **Writer + N** (GPU, 1 slice): a draw writer that, per draw, writes the district HOURLY totals (8,760 x 4 targets) and every
   dwelling's ANNUAL totals (4 targets), not per-dwelling hourly files. Time 10 draws (draws 0-9; load / predict / write
   separated), then N = the largest of 1,000 / 500 / 200 that fits 24 GPU slice-hours in total (print the N_RULE lines as
   part A did). Check: the 10 district totals equal the sums of part A's per-dwelling hourly files of draws 0-9 (<= 1e-6
   relative).
B. **All draws** (GPU array, <= 4 slices): draws 0..N-1 with that writer into `district/draws/`. Print per-task timing lines.
C. **EnergyPlus, the other 19 check draws** (CPU array, <= 26 CPUs while GPU jobs hold 12... keep the 5J total <= 30): the
   1,900 remaining runs of `district_runs_es.csv` through the campaign wrapper exactly as the pilot (1405248), then the same
   integrity check on all 2,000 (C10/C11 NOT_EVALUABLE by design).
D. **S on the 20 check draws** (GPU): per-dwelling HOURLY predictions (the part A pilot writer) for the 20 check draws.
E. **Comparison** (CPU, after C and D): `outputs_step7/district_check.csv` and a summary: per dwelling and draw, CV(RMSE) and
   NMBE of S against EnergyPlus per target; per draw, district annual and peak-hour totals S vs EnergyPlus; the spread of the
   district annual total over the 20 draws (max - min, SD) for S and for EnergyPlus; every result split by in range / out of
   range twin (part A RANGE list), seen / new code, and seen / new household (`trained_by_model`). Reported, not gated.
F. **Spread** (CPU, after B): `outputs_step7/district_spread.csv`: median and 90 % interval of the district annual and peak-hour
   demand per target over the N draws; the running median and interval width at 10, 20, 50, 100, 200, 500, 1,000 draws; the
   same for the in-range dwellings only.
G. **Speed** (`outputs_step7/speed.md`): EnergyPlus wall seconds per dwelling-year (median over the 2,000 runs, build + run +
   extract, one CPU; and EnergyPlus alone); S seconds per dwelling-year on one A100 slice for (i) predict only, (ii) predict +
   district write, (iii) predict + per-dwelling hourly write; and S on ONE CPU core (a CPU job, 1 CPU, 1 draw, threads = 1),
   all from the jobs' own clock lines, node names printed.
H. Copy the three outputs to `Step7_docs/outputs_step7/`; state file; Next = "manager verifies part B; Step 7 closes".

## Report back (short, plain)
JobIDs; N; the headline numbers of E, F and G; status.

## What the manager will re-derive
One dwelling's CV(RMSE) in one check draw from the two files; one draw's district annual total from the per-dwelling annual
file; the speed ratio from the clock lines.
