# Step 7 part A: district twins, household pool, sealed draws, timing pilots - implementation state
Task doc:   Step7_docs/impl/2026-10-01_wp5_district_TASK.md   (design: 2026-10-01_step7_design.md, R7-1..R7-5)
Status:     IN PROGRESS (chain submitted 2026-10-01 04:32 EDT; nothing has run yet)
Speed root: /speed-scratch/o_iseri/5J/district/  (code/ in/ in/ref/ hh/ store/ pilot/ out/ ep/ logs/). Local code: tools/speed/s7_*.

## Ledger (one line per job; append only)
- 1405226 s7_stage     (copies read-only sources into district/code, md5 compared)                    pending, no dependency
- 1405227 s7_sample    parts A + B: sample 100, twins, IDF build once each, seals          after 1405226
- 1405228 s7_hhdraw    part C0: list of 500 new Spanish households (seed 6, weights, size strata)   after 1405226
- 1405229 s7_hhpilot   part C: 10-household pilot (timed) + folders + checks                     after 1405228
- 1405230 s7_hhfull    part C: size rule (500 / 300 / 200 from pilot seconds) + full build + pool.csv   after 1405229
- 1405231 s7_draws     part D: draws.json (1,000 seeds, 20 check indices) sealed + assignment checks      after 1405227 AND 1405230
- 1405232 s7_gpu       part E: store draws 0-9, S3 predictions, timing, N rule (1 A100 slice)      after 1405231
- 1405233 s7_eptable   part F: 2,000-run table (20 check draws), pilot table (100 runs), plan, seals   after 1405231
- 1405234 s7_eppilot   part F: array 1-4 (%4 = 4 CPUs), the campaign task code on the pilot table   after 1405233
- 1405235 s7_epcheck   part F: G5J.1-style integrity (camp_integrity subset mode) + timing lines     after 1405234 (afterany)
Submit script: tools/speed/s7_submit.sh (copy in district/code/). Logs: district/logs/s7_*_<jobid>.out.

## Verified
(nothing yet)

## Decisions (the task doc did not decide these; the manager can overrule)
1. Eligible buildings = building ids found in cells/ and cells_failed/ of the 4J Madrid campaign folder; the job checks the count against preflight_report.json (1,151) and the sum of dwellings_total against 11,976. The payload field `dwellings_total` is the real dwelling count (equals the drawn dwellings, rule R11 of the 4J campaign), `storeys` the real storeys.
2. Stratification uses the class in the TABULA code of archetype_id (token 3); the payload building_type is cross-tabulated against it in the log. Allocation = largest remainder over the class counts, then every class lifted to at least 5.
3. Twin infiltration and north: one Latin hypercube over the 100 twins (campaign function `lhs`, 0.3-1.0 and 0-360, 4 and 2 decimals), seed 20261002 through random.Random("20261002|twins|es"). The campaign drew its Latin hypercube per class of 10; here per all 100 (the campaign's rule applied to this sample size).
4. Twin period label = the label of the same code in campaign/in/buildings_es_it.csv (every code is there); the twin's own IDF is built with a placement cycling over the 60 campaign households (only the geometry and size are recorded).
5. Household draw: the 500 new households are drawn from the Spanish households NOT among the 60 (positive weight), stratified by size in proportion to the remaining counts (largest remainder), key log(1-u)/w, rng_for(6,"hh","es"), shuffled; any prefix is roughly stratified. The 10-household pilot = the first 10 of that list. The pilot is built in its own trigger run (own calibration group; timing only); the full set is a separate trigger run that includes those 10 again.
6. Full-set size rule uses the pilot's TOTAL seconds (corpus load included) / 10 x N: conservative. 500 if pilot <= 288 s; 300 if <= 480 s; else 200. The trigger run calibrates the stock electricity to the published target on the households given, so the new households are calibrated as one group of N and the 60 as a group of 60 (different groups, same target; mean electricity of each group is printed by the trigger). Not corrected.
7. Draw weights: the pool is the 60 + new households, each with its own diary weight; a draw samples with replacement BY THAT WEIGHT (as R7-2 says). Note for the manager: the new households were themselves selected with probability proportional to the weight, so weighting again counts weight twice (heavy households appear more often than in the population). The rule is implemented as ruled; changing it is one line in tools/speed/s7_draws.py (weights=None) and must happen before the seals.
8. Check-draw indices are sampled from 0..199 so that they exist whatever N is chosen (N >= 200 in every case).
9. N rule (R7-3): "fits 24 GPU-hours on at most 4 slices" is read strictly as 24 GPU slice-hours in total (N x district dwellings x seconds per dwelling-year with load + predict + per-dwelling write). The wall-clock reading (24 h on 4 slices = 96 slice-hours) is printed beside it in the log (N_RULE lines). The manager decides which reading holds.
10. EnergyPlus pilot draw = the first (smallest) of the 20 check indices; 4 blocks balanced by estimated seconds (not the campaign 2,400 s rule) so the array size is fixed at submission; the campaign task code (camp_task.py) and integrity code (camp_integrity.py, subset mode) are used unchanged, with the twin rows added to the building table by s7_common.install_twins (camp_common.static patched at run time, file untouched).
11. In subset mode camp_integrity gives NOT_EVALUABLE for C10 (no replicates) and C11 (no B0 runs); these two are expected and listed as such.

## Next
Wait for the chain (the manager polls). If a job fails, read its log in district/logs/, fix the s7_* file locally, scp it to district/code/, and resubmit that job and everything after it (s7_submit.sh lines). Then fill this file: class counts, twin sizes, household time and MB, N, pilot timings, in-range list. Then: "manager verifies part A; then part B (full draws, the 19 remaining EnergyPlus draws, comparison, speed)".

## WHAT I DID NOT VERIFY
(nothing ran yet: all code is unexecuted as of this stamp; no local syntax check is possible because nothing runs on the local machine; the first jobs print SYNTAX_OK lines)

## UPDATE 2026-10-01 04:34 EDT (employee, end of turn; the chain keeps running, nobody is waiting on it)
Passed and read from logs (district/logs/):
- 1405226 stage COMPLETED (md5 of every staged file equal to its source; split_loader equal to freeze copy).
- 1405227 sample COMPLETED exit 0, 35 s: 1,151 eligible = preflight 1,151; dwellings_total sum 11,976 = preflight; payload type = code class in all 1,151. Class counts of the 1,151: SFH 8, TH 50, MFH 12, AB 1,081. Sample of 100: SFH 5, TH 5, MFH 5, AB 85. 14 distinct codes; 78 twins with a code seen in dev buildings, 22 new. All 100 twin IDFs built, all patch lines and area gates OK. Seals (md5): sample_buildings.csv 91daedf1a902d13bfa608fd18171d7d4, twins_es.csv 52b372b5b22debb0550bf3a3e89ae8e6, twins_info_es.csv 94c081a762f2c8344428db1f0eb313e1.
- TWIN SIZE vs REAL (reported, not corrected): real dwellings of the 100 = 1,173; twin dwellings = 2,034 (ratio 1.73). By class: SFH 7 vs 5, TH 5 vs 5, MFH 43 vs 62, AB 1,118 vs 1,962. Only 11 of 100 twins have the same dwelling count as the real building; the gap is the AB archetypes (e.g. AB.06 twin = 77 flats vs real buildings of 1 to 11). MANAGER: this size gap is large; the district is 2,034 dwellings per draw, not about 1,173.
- 1405228 hhdraw COMPLETED: 500 new households (sizes 157/231/73/33/5/1 for 1..6 persons), none in the 60, reproducible, another seed gives another list; list md5 1a1e805c0254956a04553004c2cb9c52.
- 1405229 hhpilot COMPLETED exit 0: 10 households, trigger 35 s total (corpus load included), RSS 248 MB, trigger output 2.8 MB (0.28 MB per household; folders 0.158 MB per household); all checks PASS (8,760 rows, presence in [0,1], design level > 0; checker seen failing on 5 planted faults).
- 1405230 hhfull RUNNING at 04:33: size rule chose N=500 (35 s x 50 = 1,750 s estimate < 14,400 s).
Not yet run / not yet read: 1405230 (finish), 1405231 draws, 1405232 gpu, 1405233 eptable, 1405234 eppilot, 1405235 epcheck. All their code is untested until it runs.
Next: read those logs in order; the fix route is in the Next section above.

## MANAGER RULINGS (2026-10-01 04:34 EDT; before job 1405231 ran)
* Decision 7 overruled: draws sample the 560-household pool UNIFORMLY (the pool is itself a weight-proportional draw; weighting
  again counts weight twice). `tools/speed/s7_draws.py` changed (one line + header + rule string), md5 b251eb06..., copied to
  `district/code/` while 1405231 was PENDING; the weighted copy is archived (`tools/speed/archive_s7_pre_ruling/`).
* Decision 9: the strict reading holds (24 GPU slice-hours in total).
* Decisions 1-6, 8, 10, 11: accepted.
* Twin size gap (2,034 twin vs 1,173 real dwellings, AB archetypes): accepted as ruled in R7-1 (reported, not corrected). The
  paper states that each twin has the TABULA archetype's size, and the district results are per twin district, with the real
  dwelling count beside it.

## MANAGER (2026-10-01 05:04 EDT): chain read; EnergyPlus pilot fixed and resubmitted
* 1405230 hhfull COMPLETED: 500 new households, every one checked (0 bad), pool 560 (60 campaign + 500 new; 40 trained by S),
  pool.csv md5 5c9f1996...; 1405231 draws COMPLETED with the UNIFORM rule (s7_draws.py b251eb06...): draws.json sealed
  825ac39d..., check draws [4, 12, 23, 29, 30, 44, 62, 63, 64, 72, 81, 84, 102, 115, 125, 131, 148, 163, 168, 180];
  1405233 run table COMPLETED (2,000 runs, sealed c0135055..., pilot = draw 4, 100 runs).
* 1405234 EnergyPlus pilot FAILED in all 4 tasks: `ModuleNotFoundError: camp_task` (the stage job copied camp_common and
  camp_integrity but not camp_task). The check job 1405235 then reported C07 FAIL and C03-C05 NOT_EVALUABLE on all 100 runs
  (the integrity check did fire on a run that never happened). Fix: `s7_stage.sbatch` now stages camp_task.py too; a one-off
  job 1405247 copied `campaign/camp_task.py` (md5 d355bffa..., unchanged) into `district/code/`; pilot re-submitted as 1405248
  (afterok 1405247), check 1405249 (afterany). No run folder was written by the failed pilot (C06 PASS, 0 done files).
* GPU pilot 1405232 RUNNING; out of range: 17 of 100 twins (871 of 2,034 dwellings), mainly the 10 AB.06 twins (77 dwellings
  each, the TABULA code of es_B40: V_C inconsistency and size beyond development), clipped as AMENDMENT 2 says.

## MANAGER VERIFIED part A + RULING on N (2026-10-01 05:46 EDT)
* Read: GPU pilot 1405232 (all CHECK PASS; S md5 78271da9...; 10 draws x 2,034 dwellings; seconds per dwelling-year load
  0.00002, predict 0.0274, per-dwelling hourly write 0.0949, total 0.1223); EnergyPlus pilot 1405248 (100/100 runs passed,
  integrity 9 PASS, 0 FAIL, 2 NOT_EVALUABLE by design: no replicates, no B0; median 25.9 s per run build+run+extract, EnergyPlus
  alone 16.8 s; 1.63 s per dwelling-year; 0.92 CPU-h per draw).
* Own code (job, `mgr/mgr_s7a_check.py` md5 82b13a58...): draw-0 assignment of 3 dwellings by the uniform rule from the sealed
  seed and pool = the job's EXAMPLE lines (02905, 08135, 02149); TABULA static columns of 3 twins (SFH.03, AB.05, AB.06) = the
  campaign building of the same code (max abs diff 0); EnergyPlus median 16.8 s from the 100 done files = the check job.
* Ruling (R7-3 addendum): the district spread needs district hourly totals and per-dwelling ANNUAL totals, not per-dwelling
  hourly files; those are written only for the 20 check draws (they are compared with EnergyPlus). N is fixed in part B from a
  10-draw timing of that writer: the largest of 1,000 / 500 / 200 that fits 24 GPU slice-hours (with predict alone ~0.027 s per
  dwelling-year, 1,000 draws need ~15.5 slice-hours). The pilot's N=200 (computed with per-dwelling hourly writes) is superseded.
  G5J.7 reports all three times: predict only, predict + district write, predict + per-dwelling hourly write.
* Part A DONE. Next: part B (`impl/2026-10-01_wp5_district_B_TASK.md`).

## PART B (employee, started 2026-10-01 05:46 EDT; task doc `2026-10-01_wp5_district_B_TASK.md`)
Status: IN PROGRESS (chain submitted 05:54 EDT; the code of part B is untested until its jobs run; only imports and syntax were run, job 1405272: IMPORT_OK for all six new modules).
New code (tools/speed/, copies in district/code/): `s7_draws_gpu.py` (modes time | run | hourly | cpu), `s7_wcheck.py` (writer vs per-dwelling hourly files), `s7_ep_rest.py` (the 1,900 remaining EnergyPlus runs, 15 blocks), `s7_spread.py` (F), `s7_compare.py` (E), `s7_speed.py` (G), sbatch files `s7_b*.sbatch`, chain `s7_bsubmit.sh`. Part A files unchanged (s7_gpu_pilot.py, s7_draws.py, s7_common.py ...). Outputs of part B: `district/out_step7/` (district_spread.csv, district_check*.csv/.md, speed.md); draw files `district/draws/d<DDDD>.npz`; S per-dwelling hourly files of the 20 check draws `district/pred_check/`.

### Ledger (one line per job; append only)
- 1405271 s7_bsyntax  (prelude compile of all s7_*.py)                                  FAILED exit 3 (SyntaxError in s7_speed.py: a missing `)`), fixed, superseded by 1405272
- 1405272 s7_bsyntax  (compile + import of the 6 new modules)                           COMPLETED, IMPORT_OK x6
- 1405273 s7_bgtime   part A: draws 0-9 timed (load / predict / district write), N rule, writer checks; GPU 1 slice     no dependency
- 1405274 s7_bghourly part D: per-dwelling HOURLY predictions of the 20 check draws (pilot writer path) into district/pred_check/; GPU 1 slice   no dependency
- 1405275 s7_bgcpu    part G: S on ONE CPU core (1 CPU, threads 1), draw 0, district writer, timed                     no dependency
- 1405276 s7_bwa      writer check a: draws 0-9 files vs part A per-dwelling hourly files (rel 1e-6), planted fault must be caught   after 1405273
- 1405277 s7_bgrun    part B: array 1-20 %3 (3 GPU slices), task t = draws 50(t-1)..50t-1 capped at N (N read from out/n_chosen_B.txt; tasks past N do nothing; draws 0-9 already written by 1405273 are skipped)   after 1405273
- 1405278 s7_bwb      writer check b: the 20 check draws of draws/ vs pred_check/ per-dwelling hourly sums                after 1405277 AND 1405274
- 1405279 s7_bspread  part F: district_spread.csv (+ validation 1.1, 1.3, 1.4 lines)                                   after 1405277
- 1405280 s7_bep_rest part C prep: table of the 1,900 remaining runs (sealed table minus pilot), 15-block plan, ids of all 2,000                no dependency
- 1405281 s7_bep      part C: EnergyPlus array 1-15 %15 (15 CPUs), the campaign task code via s7_ep_task.py, as the pilot 1405248                   after 1405280
- 1405282 s7_bepcheck integrity (camp_integrity subset mode, unchanged) over all 2,000 runs + timing lines (exit 0 always; read its lines)   afterany 1405281
- 1405283 s7_bcompare part E: district_check*.csv/.md (6 CPUs)                                                          after 1405282 AND 1405274
- 1405284 s7_bspeed   part G: speed.md from done jsons + SPEED_S lines of 1405273, 1405274, 1405275 logs                   after 1405273, 1405274, 1405275, 1405282
Logs: district/logs/s7_<name>_<jobid>.out (array: _<jobid>_<task>.out). CPU count at peak: 3 GPU jobs x 3 + the D job 3 + 15 EnergyPlus + 1 (CPU speed) + 2 (writer check) = 30; GPU slices at most 4 (1 A + 1 D, then 3 B + 1 D).

### Verified
(nothing yet; the jobs above have only just been submitted)

### Decisions (the task doc did not decide these; the manager can overrule)
1. N rule: N x 2,034 dwellings x (load + predict + district write) seconds per dwelling-year from the 10-draw timing job, <= 24 slice-hours, same strict reading as part A; N written to `district/out/n_chosen_B.txt` (the part A file `pilot/n_chosen.txt` = 200 is left untouched and superseded by the ruling).
2. Draws 0-9 written by the timing job are reused by the array (identical writer, file carries writer version, draw and seed; skipped only if all three match).
3. District file per draw: hourly totals of all dwellings and of in-range twins (8,760 x 4 each), per-dwelling annual totals (2,034 x 4), twin index, dwelling index, household id. "In range" = the part A range file (twin level); each job re-derives the per-twin clipping from its own flats table and compares it with that file.
4. Check draws 0-9 vs part A files: the draw file is also compared with the pilot's in-memory district sums (part A job 1405232) inside the timing job; the files-based comparison runs in 1405276. Relative tolerance 1e-6 on the annual total, per-dwelling annual, and (largest hourly difference / peak-hour total). The planted fault adds 1e-5 of the annual total to one hour of one dwelling (the quantity itself) and must be caught.
5. EnergyPlus "rest" blocks: 15 blocks balanced by the estimated seconds (campaign estimate), array %15, 1 CPU each (the pilot used 4 blocks). Integrity check on all 2,000 uses the part A check script unchanged (C10, C11 NOT_EVALUABLE by design).
6. S on one CPU core runs float32 (no bf16 autocast on the CPU), draw 0 (2,034 dwelling-years), one thread; it can take hours (7-day limit); only the final SPEED_S line matters.
7. Metric conventions in E = the frozen scorer's (e = S - EnergyPlus; CV(RMSE) = RMSE/mean(E); NMBE = sum(e)/sum(E); empty where mean(E) = 0), here per dwelling over 8,760 h and per run over all its dwelling-hours.
8. Outputs beyond the three named files: district_check_runs.csv, district_check_draws.csv, district_check_spread.csv, district_check_summary.md (E), all in `district/out_step7/`. Copy to `Step7_docs/outputs_step7/` is not done yet (jobs run for hours; nobody waits): by scp after 1405284, see Next.

## Next
1. Manager (or a fresh employee) polls: first the early jobs (1405273 time, 1405280 rest prep) and their `CHECK ... FAIL` / `GATE ... FAIL` lines; if a part B script is wrong, fix the s7_* file locally, scp to district/code/, resubmit that job and its dependents (s7_bsubmit.sh lines).
2. When 1405284 is done: scp `district/out_step7/{district_spread.csv,district_check.csv,district_check_runs.csv,district_check_draws.csv,district_check_spread.csv,district_check_summary.md,speed.md}` to `Step7_docs/outputs_step7/`, fill Verified here, set Status DONE. Then: "manager verifies part B; Step 7 closes".

## WHAT I DID NOT VERIFY
Nothing of part B has run yet. Only the syntax and the module imports (job 1405272). In particular unverified: the writer's equality with the part A files, N, the EnergyPlus runs and integrity of the 1,900 new runs, the comparison, the spread and the speed numbers.

### Early read (employee, 05:55 EDT, from the logs; chain still running)
* 1405280 rest prep COMPLETED: all 4 gates PASS; 1,900 rest runs, 15 blocks of about 2,920 estimated seconds each (total 43,795 s); pilot's 100 done files present; rest table md5 caca700c... (derived, not sealed).
* 1405273 time job, first 16 checks PASS (sealed inputs, S md5 78271da9..., store files, 20,340 flats rows for draws 0-9, per-twin range = part A file with 17 out-of-range twins, clipped values 93,550 = 9,355 x 10). Predict / write / N not yet printed.

## MANAGER (2026-10-01 07:26 EDT): part B read so far; two comparison bugs fixed
* N = 1,000 (timing job 1405273: 0.0275 s per dwelling-year with the district writer; 15.6 GPU slice-hours, fits 24). Draws array
  1405277 running (3 slices). EnergyPlus: all 2,000 check runs done, integrity 9 PASS / 0 FAIL / 2 NOT_EVALUABLE by design;
  1.675 s per dwelling-year (median, build + run + extract), 1.083 s EnergyPlus alone; 18.8 CPU-h.
* Speed (1405284, `district/out_step7/speed.md`): S on one A100 slice 0.0275 s per dwelling-year (district output) = 61x faster
  than EnergyPlus; with per-dwelling hourly files 0.121 s = 14x; S on ONE CPU core 1.384 s = 1.2x (about EnergyPlus's speed).
  The speed gain needs a GPU: a RESULT for the paper.
* Comparison 1405283 FAILED in its own self-test: it expected CV(RMSE) = 10 % for a 10 % scale-up, which holds only for a
  constant series (CV = 0.1 * sqrt(mean E^2) / mean E); NMBE = 10 % was right. Manager fixed the test's expected value (metric
  code unchanged). Re-run 1405334 passed the self-test, compared all 20 draws (40,680 dwelling-years, files written) and then
  failed in the summary (columns held formatted strings). Manager fix: numeric conversion of both tables
  (`s7_compare.py` md5 78a40427...). Re-run 1405337 submitted.

## MANAGER (2026-10-01 07:31 EDT): comparison read and re-derived
* 1405337 COMPLETED (SUMMARY fails=0): 40,680 dwelling-years. All dwellings: heating median CV(RMSE) 38.6 %, pooled annual NMBE
  +10.2 %; cooling 106.3 % / +10.0 %; equipment 3.5 % / -0.7 %; total electricity 29.9 % / +5.8 %. In-range twins: heating
  27.1 % / -7.6 %, total 21.9 % / -2.5 %; out-of-range twins: heating 165.1 % / +58.1 %, total 67.0 % / +20.0 %. Household new
  vs trained to the model: no difference. District annual totals over the 20 draws: Pearson r S vs EnergyPlus 0.97 (heating),
  0.98 (cooling), 0.9999 (equipment), 0.999 (total); range ratio S/E 0.84-1.01. => the surrogate reproduces the draw-to-draw
  spread well and the district level with a bias that comes from the out-of-range twins (a RESULT; same message as Step 6).
* The summary's last table had its column headings in the wrong order (the csv was right): fixed in `s7_compare.py`
  (md5 00244046...), re-run 1405341.
* Own code (`mgr/mgr_s7b_check.py` md5 87c9d56f...): es_madrid_es_T001_d004 dwelling 0 heating CV(RMSE) 27.9056 %, NMBE
  -18.0049 %, total 20.9860 % / -14.5870 % = `district_check.csv` row; draw-writer file layout read (hourly_all, hourly_inrange,
  annual per dwelling); the writer-vs-hourly check of all 20 check draws is job 1405278 (pending on the draws).
* Speed ratio re-derived from the clock lines: 1.675 / 0.02752 = 61; 1.675 / 0.1213 = 14; 1.675 / 1.384 = 1.2.

## MANAGER (2026-10-01 08:17 EDT): re-run read; state at session handover
* 1405341 COMPLETED (exit 0, SUMMARY fails=0, 07:33): heading order now right; numbers as 07:31. Added from the by-building-code
  table: twins whose TABULA code was NEVER in development do much worse (heating median CV(RMSE) 164.3 %, pooled NMBE +64.0 %;
  total 66.9 % / +21.7 %) than codes seen in development (heating 25.7 % / -9.8 %; total 21.1 % / -3.6 %). District peak hour:
  heating peak in the same hour in 20/20 draws, cooling 0/20 (cooling peak-hour level within 3.6 %), total 9/20.
* At 08:17: draws array 1405277 tasks 1-7 COMPLETED, 8-10 RUNNING, 11-20 PENDING (about 45 min per task, 3 slices: about
  2.5 h more); writer check 1405278 and spread 1405279 wait on it. Outputs of E and G are in `district/out_step7/`; not yet
  copied (copy after 1405279).
* MANAGER 10:21 EDT: own-code check queued for the 1,000-draw spread: `tools/speed/mgr_s7c_check.py` (copy in /speed-scratch/o_iseri/5J/mgr/),
  job 1405460 afterok:1405279 (syntax job 1405459). Part 1 = check draw 4 rebuilt from its 100 per-dwelling hourly files (gzip+csv,
  no project module) vs d0004.npz; part 2 = annual from the per-dwelling ANNUAL array + own percentiles vs district_spread.csv
  (tolerance 2e-5, csv is %.6g); part 3 = settling list for the paper. Two planted faults. Exit 0/1/2. Draws at 10:21: 750 files.

## MANAGER (2026-10-01 13:15 EDT): STEP 7 VERIFIED (writer check + own recount, run on the desktop)
* Where it ran: the author allowed half the desktop (<=10 CPUs, ~31 GB) because the account CPU cap (64) was held by other
  projects' arrays and 1405278/1405460/1405373 sat PENDING (AssocGrpCpuLimit) for hours. Spain-only files copied by tar from
  /speed-scratch/o_iseri/5J (district/code, in, out, out_step7, draws 1,000 files, pred_check/es_madrid_2010 2,000 files; TAR_RC=0)
  to `_local_runs/5J_s7/`. `district/code_local/` = sed copies with only the path constant changed (diff read: FIVE in
  s7_common/s5_common, SPLIT_DIR/GATE_FILE in split_loader; s7_draws.py and s7_wcheck.py unchanged). Python 3.13, numpy 2.3.5
  (Speed 2.2.6), pandas 2.3.3. The three Speed jobs were then CANCELLED (ours, still pending; results in hand).
* Writer check (s7_wcheck.py b, log `_local_runs/5J_s7/district/logs/s7_bwcheckb_local.out`): READ_FILES 20 draws 2,000 files;
  WCHECK PASS on all 20 check draws; worst annual rel 4.41e-10, hourly/peak 1.10e-09, dwelling annual 5.82e-09 (tol 1e-6);
  PLANTED draw 4 CAUGHT=True (annual rel 1.00e-05); SUMMARY fails=0; EXIT 0.
* Own recount (mgr_s7c_check.py, only D path changed, log `_local_runs/5J_s7/mgr/mgr_s7c_check_local.out`): draw 4 rebuilt from
  100 per-twin gz files = d0004.npz (annual rel 4.3e-10, hourly 7.5e-10, all and in range); 1,000 draw files read; csv vs own
  percentiles 112 rows worst rel 4.65e-06 (tol 2e-5); both planted faults caught; SUMMARY fails=0; EXIT 0.
* 🔴 Recount CHANGES one paper claim: the "first n within 5 %" numbers (50 annual, 500 peak) do NOT stay within 5 % after that
  n (stays-within False for 13 of 16 series; e.g. heating annual width ratio 1.03 at 50, 0.93 at 100, 0.95 at 200). True
  statement used in 3.8: medians within 0.1 % of the 1,000-draw value from 100 draws on (equipment peak 0.3 %); width from the
  first 500 draws within 6 % of the 1,000-draw width for all 8 scope-all series, within 5 % for 5 of 8. Gate 1.4 (first half
  within 5 %, WARN) = WARN on 3 of 8 scope-all series (cooling peak 0.943, equipment annual 0.946, total annual 0.944) + in-range
  total annual 0.936: kept as a WARN result, no gate changed.
* Outputs copied: `Step7_docs/outputs_step7/` (7 files, md5 equal to the run tree; district_spread.csv 62209987...).
