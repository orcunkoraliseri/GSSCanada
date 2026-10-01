# WP1 campaign design (Spain + Italy) - implementation state
Task doc:   Step2_docs/impl/2026-09-30_wp1_campaign_design_TASK.md
Status:     DONE (2026-09-30 16:30 EDT)
Speed root: R=/speed-scratch/o_iseri/5J/campaign_prep/   (read-only: every other 5J/ folder; the parallel households folder was not touched)
Local copies: Step2_docs/outputs_step2/ (dwelling_count_it.csv, k_table_es_it.csv, splits_households.csv, splits_buildings.csv, campaign_runs_es.csv, campaign_runs_it.csv, campaign_design.md; logs partA_1404126.out, design_1404128.out, gates_1404129.out, timing_1404133.out)
Scripts on Speed R/ (copies in the scratchpad only): cp_partA_tabula.py (copy of mz_partA_tabula.py with a country argument), cd_design.py, cd_gates.py, cd_timing_build.py, cd_arith.py, cd_extract_timing.py (sed copy of mzp_extract.py), *.sbatch

## Ledger
(append-only)
- 1404126 . Part A: TABULA reader (copy, country argument), Italy + Spain control . COMPLETED 0:0 24 s . R/logs/partA_1404126.out . CONTROL_ES_REPRODUCES PASS (byte equal to multizone/tabula/dwelling_count_es.csv)
- 1404128 . Parts B + C: k table, splits, run tables (cd_design.py) . COMPLETED 0:0 . R/logs/design_1404128.out
- 1404129 . gates C1-C7 + seen-failing (cd_gates.py) . COMPLETED 0:0 2 s . R/logs/gates_1404129.out . SUMMARY PASS=14 FAIL=0 NOT_EVALUABLE=0, SEENFAIL fired 7/7, EXIT_CODE 0
- 1404133 . Part D: build + run the 2 biggest buildings (timing only), extract, du, df, arithmetic . COMPLETED 0:0 3:23 . R/logs/timing_1404133.out

## Verified (read from the Speed logs, copies in outputs_step2/)
- Italian k table (16 MFH/AB codes), printed in design_1404128.out and campaign_design.md section 3; Spanish control rule reproduces re-pilot k (B21 k 2, 12 dwellings; AB.06 78 -> 77).
- Italian TABULA file has 42 Code_Building rows (32 used by the 40+40 buildings... 8 per class for 4 classes; 10 combined SFH-TH / MFH-AB codes not used); the task said 24. Used codes have 3 identical rows each.
- Splits: households 40/10/10 per country; buildings 30/5/5 per country, every class in every split (BSPLIT lines in design_1404128.out). md5 in campaign_design.md section 2.
- Run counts: Spain 4,768 (4,548 main + 120 B0 + 100 replicates), Italy 4,501 (4,281 + 120 + 100). C5: observed = formula in all 16 class/pool cells per country.
- Gates C1-C7 all PASS both countries; each seen failing on a scratch copy (planted defects, scratch files in R/scratch/seenfail_*).
- Timing: es_B40 77 zones 75 s MaxRSS 266208 kB du 345460 kB 0 Severe Completed Successfully; it_B37 48 zones 45 s MaxRSS 249576 kB du 214604 kB 0 Severe Completed Successfully.
- Disk: raw df line `filer-speed:/userdata/speed_scratch 133040906960896 86833891835904 46207015124992  66% /nfs/speed-scratch`; PREFLIGHT_DISK free_bytes=46207015124992 used_5J=2691998502; parser cross-checked with stat -f (equal), 3 broken inputs refused.
- Arithmetic: 17.84 CPU-hours both countries (0.59 h at 30 CPUs), extracted 16.88 GB, peak disk 27.49 GB.

## Decisions (not in the task doc)
- Replicate inputs: "first 5 buildings by id" of SFH/TH = B01..B05 (all SFH); MFH/AB 5 buildings = max-dwelling building + first 2 MFH + first 2 AB by id (excluding it). Tie for Italy's largest (it_B37 and it_B38, 48 each): lowest id taken.
- run_id uses the lower-case city name and building number: es_madrid_B21_dev_1. SFH/TH: pool = household's own split, r = position in that pool. B0: pool `b0`, r 1, placement `<cc>_avg` in every slot.
- Swap rule: nearest following slot first (as ruled); when none fits (clash near the end of a pool's last run) the nearest preceding slot that fits was used (49 of 136 swaps). A deviation from the ruling, reported.
- n_floors / n_dwellings come from the builder's own derive() and k_from_tabula(); Italian timing run uses Bologna 2014 EPW, Spanish households (timing only).
- Block per task: equal estimated seconds (about 2,400 s), not equal counts; 40 tasks in 6 arrays; estimate only.

## Next
Manager verifies; manager freezes the design; Step 3 campaign task.

## WHAT I DID NOT VERIFY
- That the parallel households task leaves `households.csv` unchanged (splits drawn from md5 e0a3a5e5c83fdca1552036e3f4aeaa2b) or that `es_avg` / `it_avg` exist and are named that way.
- Extraction time per run (only the whole timing job, 203 s, is known), so the 40-task block plan is an estimate; Turin, Milan, Valencia, Seville timings were not run.
- That TABULA n_Apartment is a published value (carried from the builder task); the 10 unused Italian combined codes were not examined.
- Any UK file (none opened by design). Italian buildings were only built for it_B37, not for all 40 (the other Italian IDFs are untested for area gates; the builder has only run on it_B37 here).
- The hand check of one MFH run count was by reading the formula, not from the csv by eye.

## Verified (manager) 2026-09-30 16:30 EDT (from `date`): mostly ACCEPTED, ONE DEFECT, design NOT frozen
Own Speed job 1404137 (`/speed-scratch/o_iseri/5J/mz_pilot/mgr/mgr_verify_cd.py`, own code), plus sacct:
- Splits: 40/10/10 households per country. Rows: es 4,768, it 4,501, 100 replicates each, 120 B0 each: as reported.
- Run counts from the formula ceil(pool x 3 / n): es_B21 (n=12) dev 10 / val 3 / test 3 per climate; it_B37 (n=48)
  3/1/1: equal. No run mixes pools; no household twice in one run; placement identical in the 3 climates.
- Timing: T_es_B40 77 zones 75 s (status.txt; sacct gives only the whole job, 00:03:23), T_it_B37 48 zones 45 s.
- Disk: raw df line fields = size 133040906960896, used 86833891835904, avail 46207015124992 -> free 46.2 TB, the
  preflight number is the avail field. Plan (about 27.5 GB peak) is far below.
- 🔴 DEFECT (C1 counts the wrong thing, failure class: a gate that passes by counting slots): on es_B21, 10 of the 60
  households sit in FEWER than 3 DISTINCT flats in every climate (they get 3 placements, but two land on the same
  flat index). The ruling is "each household in at least 3 flats"; a repeated flat adds no new position. it_B37
  (n=48): 0 such households. The employee's C1 counted placements, not distinct dwellings. Fix task:
  `Step2_docs/impl/2026-09-30_wp1_campaign_design_fix_TASK.md`.
- Also: the design scripts live only on Speed and in the employee's scratchpad; the fix task copies them into
  `tools/speed/` (reproducibility).
- The backward-swap fallback (49 of 136 swaps) is accepted: the rule's aim (no household twice in a run) holds.
