# TASK (employee, Sonnet): 5J Step 4 fix 1b: fill perturbations.md from the finished jobs (docs only, no new compute)

Written 2026-09-30 19:56 EDT (from `date`) by the 5J manager. Read first: `impl/2026-09-30_freeze_fix1_TASK.md` (parts D and E
and its hard rules, which apply unchanged), `impl/2026-09-30_freeze_fix1.md` (its "Next" list is your checklist),
`outputs_step4/perturbations.md` (skeleton), `outputs_step4/gates_frozen.md`.

All jobs are finished (manager read sacct 19:56): 1404395 stand-ins COMPLETED; scorers 1404398-1404402 COMPLETED;
1404403 sc_highfloor exit 2 (= SOME NOT_EVALUABLE, as planted; sacct shows FAILED 2:0, write that this is the intended exit);
1404404 summary COMPLETED. Manager re-derivation 1404408 (own code) agreed: effgood R² Italy AB heating 0.9947 / cooling
0.9942 / equipment 0.9937 / total 0.9937 and Spain MFH 0.9929 / 0.9922 / 0.9918 / 0.9918; pairs 1,032 and 3,570; per-pair
noise SD / SD of the occupancy difference 0.083-0.095; peak share 92.5 % and 93.4 %; 14 open logs, 0 lines naming a locked run
(`/speed-scratch/o_iseri/5J/mz_pilot/logs/mgr_s4b_1404408.out`).

## Do
1. On the login node read only with single-file cat/tail/grep: `R/out/perturb_summary_eff.txt`, `R/out/perturb_summary.txt`,
   `R/logs/standins_eff_1404395.out`, `R/logs/score_sc_highfloor_1404403.out`, `R/logs/score_sc_crash_1404318.out`,
   `R/logs/null_1404323.out` (tail). R = `/speed-scratch/o_iseri/5J/freeze/`.
2. Fill `outputs_step4/perturbations.md` (replace the skeleton table; keep the header's source lines): row 0 good
   ("ASHRAE-good, effect-blind"), rows 1-5 on effgood, planted high floor, planted crash, null — exactly as the fix-1 task
   part D says, plain words, every number with its source file. Add the manager re-derivation line above. Add a short
   "What this shows" paragraph (4-6 sentences, no claims beyond the numbers): an hourly-accurate stand-in can pass the load
   band on every cell yet miss the occupancy effect on heating/cooling; a building-mean stand-in (no occupancy effect) passes
   the load band on 16 of 32 cells; the gates catch each planted fault. Tables are fine in this file.
3. Append to `impl/2026-09-30_freeze_fix1.md`: Ledger lines for the finished jobs, "Verified" numbers you read, Status
   "DONE except freeze (ASHRAE page pending)"; and to the parent `impl/2026-09-30_freeze.md` one line pointing to fix 1.
4. Do NOT edit `gates_frozen.md` (its md5 was taken in 1404397); do not create `gates_frozen.md5`; no compute.
Report back in under 120 words.
