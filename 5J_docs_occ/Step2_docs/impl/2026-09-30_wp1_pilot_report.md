# 5J pilot part 2 (check the 50 runs, write the report) - implementation state
Task doc:   5J_docs_occ/Step2_docs/impl/2026-09-30_wp1_pilot_report_TASK.md (incl. AMENDMENT 2026-09-30: all compute on Speed)
Status:     DONE (checker ran; result is FAIL on one gate, 4.2a, see Verified; manager to verify and rule)
## Ledger (append-only)
- 1401744 (check job, part 1) - COMPLETED 0:0, 2 h 15 min (from part 1 state).
- 1401745 array (first pilot) - all 50 FAILED 1:0 in 1-2 s (in.idf symlink clash); superseded by 1403962 + 1403963. Kept, not dropped.
- 1403962 (pilot task 1) - COMPLETED 0:0, 8 s. 1403963 (tasks 2-50) - all 49 COMPLETED 0:0, 2-7 s (sacct, read 2026-09-30 15:18).
- 1404017 - report job run 1: checker crashed-in-gate (2.4 and 4.1 NOT_EVALUABLE: my parser looked for the GJ header on the wrong line; end-use table header is the next non-blank line). COMPLETED 0:0, 21 s. Outputs kept in `report/run1_2026-09-30/`. Superseded.
- 1404018 - run 2 (parser fixed): COMPLETED 0:0, 33 s; 4.2a FAIL, 4.3 WARN, 2.4/4.1 evaluable. Kept in `report/run2_2026-09-30/`. Superseded only because I added the full failing-run list to 4.2a and the 25-point shift table to 4.3b.
- 1404021 - FINAL report job: COMPLETED 0:0, 39 s. Main checker EXIT=1 (only FAIL gate 4.2a). Seen-failing block exit 0. Outputs on Speed `/speed-scratch/o_iseri/5J/pilot/report/`: `check_main.out`, `check_main.exit`, `check_seenfail.out`, `job_1404021.out`, `scratch/` (symlink trees). Checker md5 on Speed 055b2f07b6079d03a0a60b458fb9d39e = local.
- Scripts (new): `5J_docs_occ/tools/5thJ_pilot_check.py`, `5J_docs_occ/tools/5thJ_pilot_seenfail.py`. Job script: `report/5J_pilot_report_job.sh` (Speed).
## Step 1 (copy back, done locally with scp)
`_5J_data/surrogate/pilot/speed_results/`: `extracted/` 50 csv; `runs/<P001..P050>/` each with `status.txt` and `eplusout.err` (50 + 50 files); `md5_speed.txt`, `md5_summary.txt` (`MD5 equal=127 differ=0 missing=0`), `preflight.txt`. Counts read with `ls | wc -l`: 50, 50, 50, 50. Raw run folders NOT copied. (The err files are at `runs/<id>/eplus_out/eplusout.err` on Speed; locally they sit directly in `runs/<id>/`.)
## Verified (numbers read from check_main.out, job 1404021)
- SUMMARY `PASS=14 FAIL=1 WARN=3 INFO=10 NOT_EVALUABLE=0`, exit code 1 (FAIL-severity gate not passing: 4.2a).
- PASS: 2.1 (100 files), 2.2 (50 of 50 Completed, 0 severe; status.txt agrees with the err files, 0 disagreements), 2.3 (200 series x 8,760), 2.4 (worst relative diff 0.083 %, P006 electricity), 2.5 (11 of 11 fields, 50 midnight) and 2.5b (model.idf md5 and schedule md5 re-hashed from the run folder = manifest, 50 of 50), 3.1 (156 pairs, 0 identical, 5 buildings), 3.2 (0 identical pairs in every class, heating used), 3.4, P.1 (378 PATCH lines = 42 inputs x 9, none missing), P.2 (50 of 50 `PATCH model_idf_rename OK`), 5.1, 5.2, 5.3.
- 3.3 replicates (B07/es_02822 and B16/es_00494, 5 repeats each): max hourly spread about 1e-7 J for heating and cooling, 0 for electricity and appliance; annual relative spread at most 5.3e-16. Noise floor is rounding.
- 4.2a FAIL: 13 runs have cooling in Jan, Feb or Dec (max 0.285 kWh in one hour): P001-P008 and P046-P050 = all 13 runs of building es_B07 (SFH, ES.05 archetype, 81.4 m2, infiltration 0.94 ACH, north 243.26). No other building has winter cooling.
- 4.2b WARN: 37 of 50 runs have 0.1-0.3 kWh of heating in Jul-Aug (P001-P008 none).
- 4.1 WARN (median per class outside 0.5x..2x of the wrapper 55 m2 box, 190-196 heat / 87-89 cool kWh/m2): per class (kWh/m2, median): SFH 81.4 m2 heat 124.7 cool 131.5; TH 125.4 m2 heat 188.9 cool 96.3; MFH 92.6 m2 heat 675.2 cool 256.3; AB 215.8-223.8 m2 heat 729.4 cool 158.9.
- 4.3 WARN: electricity mean higher in present hours than absent hours for 25 of 42 inputs (59.5 %, needs 90 %). 4.3b (diagnostic, shifts the presence series by k hours): pass count is 42/42 for k=-12..-8 and k=+11..+12, worst (0/42) at k=+3..+4, 25/42 at k=0. The presence and electricity series of the same household look about 12 h out of phase. NOT investigated; both files come from one household in es_60 (Decision 7 of part 1 says the presence files are the rotated ones; the appliance files were not checked for the same rotation).
- 5.1: median 2.0 s, p90 6.0 s, max 8 s; CPU median 1.88 s; max RSS 211 MB; CPU-hours = 22,160 x 2.0 / 3600 = 12.31 (12.00 with the time.txt wall median).
- 5.2: median raw folder 3.47 MB, extracted 0.505 MB; 32 in flight + all runs = 11.31 GB; preflight 43.0 TB free, user quota 9.2 of 10.0 TB (0.80 TB headroom): PASS.
- 5.3: 8 / 16 / 32 CPUs = 1.54 / 0.77 / 0.38 h, all finish 2026-09-30, all before 11 Oct; no 2E cut needed. Compute time only.
- Seen failing (each in a scratch copy, every case's own gate flipped; control = only 4.2a FAIL): 3.1 -> `FAIL 3.1 ... identical_pairs=1 ['es_B07:es_00494==es_00739']` (2.4 also FAILs, expected); 2.2 -> `FAIL 2.2 runs_parsed=50 err_files_completed_and_0_severe=49 severe_lines_total=1 bad=['P001(completed=True severe=1 fatal=0)']` (plus `WARN 2.2b` status.txt disagrees); 2.4 -> `FAIL 2.4 runs=50 targets=4 fails=1 ['P001:facility_elec_J hourly=8.4449 annual=8.36 GJ']`. Full lines in `outputs_step2/pilot_report.md`.
- Report written: `Step2_docs/outputs_step2/pilot_report.md`.
## Decisions (not in the task doc)
1. Gate 2.4 annual source = the `eplustbl.csv` End Uses table (the IDF asks `Output:Table:SummaryReports, AllSummary` with `CommaAndHTML`). It prints 2 decimals of GJ, so tolerance = 0.1 % + 0.005 GJ; the plain 0.1 % rule also holds for every run (worst 0.083 %).
2. Floor area = "Total Building Area" from each run's `eplustbl.csv` (`buildings.csv` has no area column). Class from an ES-only copy of `buildings.csv` (`grep '^es_'`).
3. 4.2 split: 4.2a (cooling in Jan-Feb-Dec) is FAIL-severity as in the val doc; 4.2b (heating in Jul-Aug) WARN.
4. 4.3 is computed per input (42), replicate 1 only, "present" = presence value > 0.5, electricity = `facility_elec_J`.
5. 4.1 "far" = median outside 0.5x..2x of the four wrapper values (no reference range was given; TABULA/4J ranges not opened).
6. 5.1 formula uses the status.txt median (2 s, whole seconds); finer time.txt and whole-task sacct medians given as sensitivities (same order).
7. Added gates not in the task: 2.5b (re-hash idf and schedules from the run folder), P.2, 4.3b (diagnostic), 2.2b.
## Next
Manager verifies (re-derive: one run's annual electricity from `extracted/<id>.csv`; one replicate spread; the median seconds from the 50 status files; checker SUMMARY and exit code) and rules: campaign size and CPU share (O-3, O-5), what to do about 4.2a (B07 winter cooling), the very high MFH/AB loads (4.1), and the presence/electricity phase question (4.3b) before any campaign run.
## WHAT I DID NOT VERIFY
- Why B07 cools in winter, why MFH/AB heating is 675-745 kWh/m2, and why presence and electricity look about 12 h out of phase. Only measured.
- Val 4.1 "range 4J reported for the same archetype and weather": no TABULA or 4J number was read; only the four wrapper test values were used.
- That the campaign inputs can be built at the pilot's speed (input build time not measured); queue wait and array start-up not in 5.3.
- Disk: free space is the 2026-09-29 21:51 preflight, not re-measured today; quota headroom (0.8 TB) is small; `du` was not run.
- Val 1.1 seen failing (design tables) not part of this task.
- I ran `head -60` on `outputs_step2/buildings.csv` once, which shows UK building-parameter rows (design table, no UK diary data, no UK licensed rows); I did not use them and then made an ES-only copy. No UK diary file or the pooled 4J corpus was opened. `python3 --version` was tried locally once and printed nothing (no python was run).
- Not run locally: no python, no EnergyPlus. Every computation ran in Speed jobs 1404017, 1404018, 1404021.

## Verified (manager) 2026-09-30 ~15:45 EDT: report ACCEPTED as a measurement; campaign NOT released (design issue D2-8)
Re-derived on Speed (manager jobs, awk/grep, Spain only; outputs in `/speed-scratch/o_iseri/5J/pilot/report/mgr_diag*_*.out`):
- P001 annual electricity from `extracted/P001.csv` = 8.3613 GJ, 8,760 rows; eplustbl Interior Equipment = 8.36 GJ. Match (1404027).
- Median seconds from the 50 status files = 2 (p90 6, max 8). Match. Checker `check_main.exit` = `MAIN EXIT=1`,
  SUMMARY PASS=14 FAIL=1 WARN=3 INFO=10 NOT_EVALUABLE=0. Match. Replicate spread read from the 3.3 line (≈1e-7 J
  heating/cooling, 0 electricity), not recomputed.
- **4.3 WARN explained (gate definition, not a clock error).** Presence file, appliance file and extracted
  electricity are on one clock (hour-of-day means, P001, job 1404025). The gate calls hours with presence <= 0.5
  "absent", so a 2-person household with one person home (presence 0.5, often cooking) counts as absent. With
  absent = presence exactly 0 (nobody home): 38 of 38 runs have higher electricity when someone is home, 4 skipped
  (never empty) (job 1404026). Verdict WARN stays as recorded; the campaign gate uses presence == 0.
- **4.2a FAIL cause read (verdict stays FAIL).** IdealLoads Heat Recovery Type = None, no outdoor air object, so not
  the lesson-9 defect the gate targets. P001 winter cooling = 3 hours (17:00-18:59), 0.18 kWh a year: solar through
  65.9 m2 of glass (SHGC 0.70) on an 81 m2 floor plus appliances, above 26 C. B16 has 0 such hours. Real physics.
- 🔴 **4.1 WARN = a design defect, D2-8.** The 4J box (`4thJ_step8_idf.py` derive, lines 266-267) is the WHOLE
  building: height = n_Storey x h_room, floor = one plate (A_C_Ref / n_Storey), roof and ground exposed. EnergyPlus
  floor area = one plate, so per-m2 is inflated by n_Storey; and for MFH (4-6 storeys) and AB (6-9 storeys) ONE
  household's people and appliances heat or cool a whole block (B21 volume 1,389 m3; B37 4,856 m3). The spec says
  targets are "per dwelling". SFH/TH are one dwelling (physics fine, only the per-m2 divisor is wrong).
- 🔴 **Electricity is a pass-through.** Facility electricity = appliance design level x the household's appliance
  schedule (no lighting, no HVAC electricity): the same household gives identical electricity on every building
  (e.g. P003 = P011 = P029 = P037). No building physics is in that target.
Rulings: O-5 CPU share = 30 CPUs (squeue 15:22 EDT: only the author's 1-CPU job; 1J is submitted). O-3: the
DRAFT size (22,160 runs ≈ 12.3 CPU-h) needs no cut. Campaign waits on the author's D2-8 ruling (and, for the UK
arrays, the UK household script + UKDS project line).
