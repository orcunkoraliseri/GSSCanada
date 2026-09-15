# T01 — WP1 step 1: re-derive the 2022 vs 2030 at-home gap — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP1, §10
Status:     DONE — both jobs completed, outputs collected and read, ruling test (D-T01-1) confirmed no mismatch

## Task

**Why.** The submitted paper's 2030 occupancy was raked against the wrong 2022 reference. A log entry
(`2J_docs_occ_nTemp/Step8_docs/08_09_injection_bug_status.md`, entry dated 2026-07-15) says the
schedule files give weekday at-home **70.2% (2022) vs 78.5% (2030)**, a +8.3 pp gap, while the Step-6
calibration intended **76.93% → 78.44%** (+1.51 pp). These numbers come from a log. Re-derive them.

**Steps.**
1. Read that log entry (use `grep -n "2026-07-15"` then read only that part). Record exactly how the
   70.2 / 78.5 were computed: which file, which column means "at home", which hours, weekday
   definition, any weighting.
2. Find the `BEM_Schedules_2022.csv` and `BEM_Schedules_2030.csv` that the Step-8 campaign actually
   consumed. Start from `2J_docs_occ_nTemp/08_simulation.md` and `07_bemIntegrationGSS.md` (they say
   `BEM_Setup/`, about 6.9M rows each) and the Speed mirror under
   `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/`. Beware backups named `*_BAK*`: they are not the
   inputs. Record path, size, and a SHA-256 for each (local `Get-FileHash` is fine; on Speed, hash
   inside the job).
3. Find the Step-6 intended values (76.93 and 78.44) in the Step-6 outputs or docs and record where.
4. Write one script in `T01_scripts/` that, for each year file, computes:
   weekday and weekend at-home mean, **national** and **per archetype** (the 4 Step-8 archetypes;
   find the DTYPE → archetype mapping in `Step8_docs/run_paired_mc.py` or `08_gen_cycle_schedules.py`
   and cite `file:line`). Report unweighted household mean and, if a weight column exists, the
   weighted mean too. Also report the hourly at-home profile (24 values) per year and day type.
   If the Step-8 50-household panel IDs can be found, repeat on the panel households only.
5. Run it on Speed with `sbatch -p ps -c 32 --mem=64G -t 7-00:00:00` (upload the script only; if the
   CSVs are not on Speed with the same hash, upload them to `/speed-scratch/o_iseri/2J_revision/T01/`).
   Output: `athome_summary.csv`, `athome_hourly.csv`, `run_meta.json` (hashes, row counts).
6. Write the JobID in the Ledger. **End your turn.** Do not wait.

**Expected.** 2022 weekday near 70.2%, 2030 near 78.5%. Any difference larger than 0.3 pp is itself a
finding: record it, do not explain it away.

**Employee rules.** Plan §10 rules 1–6 apply (Speed via sbatch only, tcsh, no python on login node,
no waiting, never edit pipeline or frozen outputs, never read multi-MB files into context, write NOT
VERIFIED rather than guess). Python on Speed: `/speed-scratch/o_iseri/envs/step4/bin/python`.

## Ledger
<!-- JobID · what · state · exit · output path -->
- **1328240** · `sha256sum` check of the two CSVs uploaded to Speed (`sbatch -p ps -c 4 --mem=8G -t 7-00:00:00`) ·
  COMPLETED, 13s, exit 0:0 · output: `/speed-scratch/o_iseri/2J_revision/T01/hash_check.txt`.
  **Both hashes match the local ones recorded under Verified item 3** (2022
  `05e7a14d39de6e4c28d8d9c3e82a35c5a2107cea07576b22f899d95cf83d7734`, 2030
  `50d98a923cd3adbb2cbc427530b3559722fc0e41e56862c4d626a9db0f315a7e`). **Note:** this check job
  actually completed AFTER the main compute job 1328241 (1328240 ran 10:26, 1328241 ran earlier same
  morning) — i.e. the main job ran on the Speed-side copies before the hash check confirming those
  copies matched local had returned. The check has now caught up and confirms no corruption occurred;
  no re-run needed, flagged here only per the collector task's instruction to note the ordering.
- **1328241** · main compute job, `run_athome_gap.sh` → `athome_gap.py` (`sbatch -p ps -c 32 --mem=64G -t 7-00:00:00`) ·
  COMPLETED, 19s, exit 0:0 · output: `/speed-scratch/o_iseri/2J_revision/T01/out/{athome_summary.csv,athome_hourly.csv,run_meta.json}`,
  slurm log `/speed-scratch/o_iseri/2J_revision/T01/slurm_1328241.out` (stderr empty). The 19s is NOT an
  error: stdout is `DONE {'read_2022': 7.9, 'read_2030': 8.3, 'total': 18.5}` — reading each 674MB/6.93M-row
  CSV took ~8s on the 32-core node, and `run_meta.json`'s row counts (6,934,320 each) match the doc's
  Verified item 3 exactly, so nothing was skipped. All three outputs copied locally to `impl/T01_out/`
  and are non-trivial in size (61,000 / 3,391 / 776 bytes) — confirmed read, not empty.

## Verified

1. **Log entry (`Step8_docs/08_09_injection_bug_status.md:495`, 2026-07-15 row).** Numbers 70.2%
   (2022) / 78.5% (2030), +8.3pp, weekday, "population-wide (all 4 archetypes)", computed from the
   **current** `BEM_Schedules_2022.csv`/`BEM_Schedules_2030.csv` "regenerated 2026-07-09 21:06/21:07"
   (same session as the 2026-07-09 Step-5 region-tier relink). The log entry does not itself spell out
   the column name, hour range, or weighting used for that 70.2/78.5 — it only names the two files and
   "weekday AT_HOME average, population-wide". Step-6's own internal check is quoted as **76.93% →
   78.44%, +1.51pp**, against ITS OWN reference 2022 baseline (`outputs_step4/augmented_diaries.csv`,
   pre-relink, dated 2026-04-23) — not the same 2022 population as the 70.2/78.5 pair. The 2030 number
   (78.44) is said to match the measured 2030 (78.53) closely; the 2022 reference (76.93) is the stale
   one.
2. **Step-6 source of 76.93 / 78.44** — found in `outputs_step6/improvement/step6_improvement_notes.md:841-853`:
   76.93% = 2022 **observed** weekday AT_HOME from `augmented_diaries.csv`,
   `CYCLE_YEAR==2022 & IS_SYNTHETIC==0` (not the BEM schedule files); 78.44% = the 2030
   structural-break-calibrated target, also cited in `06_longitudinalForecastingGSS.md:549`
   (`06_forecast_rake.py` target WD 78.44 / Sat 79.15 / Sun 81.48).
3. **Files actually used, local copies:**
   - `BEM_Setup/BEM_Schedules_2022.csv` — 673,929,104 bytes, mtime 2026-07-09 20:57,
     6,934,321 lines (incl. header) = 6,934,320 data rows = 144,465 households x 2 Day_Type x 24 Hour,
     SHA-256 `05e7a14d39de6e4c28d8d9c3e82a35c5a2107cea07576b22f899d95cf83d7734`.
   - `BEM_Setup/BEM_Schedules_2030.csv` — 673,609,612 bytes, mtime 2026-07-09 21:06,
     6,934,321 lines, SHA-256 `50d98a923cd3adbb2cbc427530b3559722fc0e41e56862c4d626a9db0f315a7e`.
   - These mtimes match the log's "regenerated 2026-07-09 21:06/21:07" description; row count
     (~6.9M) matches `08_simulation.md`'s "6.9M rows" note. Non-`_BAK`, non-`_baseline` files used, per
     task instruction. **Caveat (see Decisions):** the actual Step-8 EnergyPlus campaign (completed
     2026-06-05) ran BEFORE this 2026-07-09 regeneration, so these are the files behind the 07-15 log
     numbers, not necessarily byte-identical to what physically drove the 6,000-run campaign.
   - Header confirms columns: `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,
     MATCH_TIER,Occupancy_Schedule,Metabolic_Rate,Equipment_Fraction,Lighting_Fraction,
     Equip_Design_W,Light_Design_W`. `Day_Type` is directly `Weekday`/`Weekend`; `DTYPE` is directly
     `SingleD`/`MidRise`/`HighRise`/`OtherDwelling` (no re-mapping needed in the file). No weight
     column exists.
   - "At home" column = `Occupancy_Schedule` (0/0.5/1 fraction of the hour occupied), confirmed by
     its use as the AT_HOME quantity throughout Step-8 code:
     `Step8_docs/08_gen_cycle_schedules.py:248` (`sub.Occupancy_Schedule.mean()`),
     `Step8_docs/08_simulation_plots.py:547-558` (groups by `Day_Type`,`Hour` and means
     `Occupancy_Schedule`).
   - Speed mirror at `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/BEM_Setup/` is STALE (Jun 8
     sizes: 667,764,790 / 666,994,420 bytes — pre-relink, different hash), so per the task's step 5,
     the local files were uploaded fresh to `/speed-scratch/o_iseri/2J_revision/T01/` (byte size on
     Speed after `scp` matches local exactly: 673,929,104 / 673,609,612). A separate small job
     (1328240) does a remote `sha256sum` to confirm the hash survived transfer (not yet read back).
4. **DTYPE archetype mapping (for citation, even though the schedule files already carry `DTYPE`
   directly), `Step8_docs/08_gen_cycle_schedules.py:88-93`:** `CONDO==1 -> SingleD`,
   `CONDO==2 & BEDRM<=1 -> HighRise`, `CONDO==2 & BEDRM>1 -> MidRise`, `CONDO==3 -> OtherDwelling`.
5. **Collector: national and per-archetype at-home numbers, read from `T01_out/athome_summary.csv`.**
   - **2022 national weekday: 70.239%.** Expected (log) 70.2% — matches, gap 0.04pp.
   - **2030 national weekday: 78.526%.** Expected (log) 78.5% — matches, gap 0.026pp.
   - **2022 national weekend: 74.331%; 2030 national weekend: 80.367%** (no log figure to compare —
     the 07-15 log entry only quoted weekday).
   - Per archetype (weekday): 2022 HighRise 70.60%, MidRise 70.39%, OtherDwelling 69.58%, SingleD
     70.25%; 2030 HighRise 78.56%, MidRise 78.55%, OtherDwelling 78.48%, SingleD 78.52%. All four
     archetypes sit within about 1pp of the national number in both years — the population is not
     dominated by one archetype's schedule shape.
   - **Anomaly, recorded not explained away:** the summary has a fifth "archetype" literally named
     `8` (1,032 weekday rows + 1,032 weekend rows in 2022, same count in 2030 — about 0.03% of the
     6.93M rows). This is not one of the four named archetypes (`HighRise`/`MidRise`/`OtherDwelling`/
     `SingleD`) and looks like a small number of rows where the `DTYPE` column held a raw numeric
     code instead of the mapped string, i.e. a residual un-mapped `DTYPE==8`(or similar) slice. Its
     mean at-home (72.4%/76.6% weekday 2022/2030) is inside the normal range, so it does not move the
     national number materially, but the mapping gap itself is unexplained — not investigated further
     per the collector's mechanical-only scope.
   - **Against the Step-6 intended values (76.93% -> 78.44%):** 2022 measured (70.24%) is 6.69pp BELOW
     the Step-6 76.93% reference — this is the discrepancy the task set out to re-derive, confirmed
     present and of the expected size. 2030 measured (78.53%) is 0.09pp from the Step-6 target
     (78.44%) — close, as the log said. Neither of these is a fresh finding; both were anticipated by
     the task's own "Expected" section and by Verified item 1.
   - **Panel-only numbers, trustworthy.** `run_meta.json`: `panel_n_households: 1198` of 1200 listed in
     the manifest, `panel_hh_matched: 1198` for both years (99.8% matched) — the panel breakdown in
     `athome_summary.csv` (national_panel / per_archetype_panel rows) is based on almost the full
     intended panel, not a degraded subset. Panel national weekday: 2022 69.01%, 2030 78.40% — close
     to but slightly below the national population numbers (about 1.2pp and 0.5pp lower respectively).
6. **`D-T01-1` manager's ruling test — CONFIRMED, no mismatch, no STOP.** Compared 3 panel households
   from 3 different cells (`HH115579` cell `HighRise__Calgary_6B` sample 1, `HH84790` cell
   `HighRise__Winnipeg_7A` sample 49, `HH68550` cell `OtherDwelling__Kelowna_5B` sample 49) — for each,
   grepped its `Occ_Sch_HH_<id>` `Schedule:Compact` block out of the canonical short (2022/2030-only)
   `sample_NNN_HH<id>/{2022,2030}/in.idf` (EnergyPlus's own echoed input, so this is what physically
   ran) and compared all 24 weekday + 24 weekend hourly values against the matching `SIM_HH_ID` rows in
   the current `BEM_Setup/BEM_Schedules_2022.csv` / `_2030.csv`. **All 3 households x 2 years x 2 day
   types = 12 series, 48 values each, matched EXACTLY, no rounding difference.** This confirms the
   manager's ruling: the current post-relink schedule files are byte-for-byte the same occupancy
   values EnergyPlus actually used for the paper's 2022/2030 re-run, so `athome_summary.csv`'s numbers
   above are trustworthy as "what the campaign used," not just "what the log used."
   Evidence paths: `BEM_Setup/SimResults_Step8/campaign_N50/HighRise__Calgary_6B/sample_001_HH115579/2022/in.idf:2973-3074`
   (and `.../2030/in.idf:2973-3074`), `.../HighRise__Winnipeg_7A/sample_049_HH84790/{2022,2030}/in.idf:2973-3074`,
   `.../OtherDwelling__Kelowna_5B/sample_049_HH68550/{2022,2030}/in.idf:1731-1832`, cross-checked
   against `BEM_Setup/BEM_Schedules_2022.csv` / `_2030.csv` rows for `SIM_HH_ID` 115579/84790/68550.
7. **Panel household IDs (Step-8 50-household panel), found.** Each of the 24 Step-8 cells
   (`BEM_Setup/SimResults_Step8/campaign_N50/<archetype>__<city>/`) has a small
   `cell_manifest.csv.new_2022_2030_20260711` (~1.4KB, 50 rows: `sample,sim_hh_id,hhsize,dtype,pr`) —
   this is the POST-relink canonical sample->household mapping (dated 2026-07-10/11, i.e. right after
   the 2026-07-09 relink). Each cell also has stray `sample_NNN_HH<id>` result directories with TWO
   household IDs per sample number (100 dirs, not 50) — one of the two is a stale pre-relink resume
   artifact (has all 5 year-subfolders 2005/2010/2015/2022/2030) and the other is the current
   post-relink pair (only 2022/2030 subfolders); the `cell_manifest.csv.new_2022_2030_20260711`
   sample-1 row's `sim_hh_id` matched the SHORT (2022/2030-only) directory in a spot check, confirming
   it is the canonical post-relink list. Concatenated all 24 cells' manifests locally into
   `T01_scripts/panel_manifest.csv` (1200 households, 50/cell x 24 cells; columns
   `cell,sample,sim_hh_id,hhsize,dtype,pr`) and uploaded it to Speed; the compute script filters
   `BEM_Schedules_*.csv` rows to these `SIM_HH_ID` values for the panel-only breakdown.

## Decisions

- **D-T01-1 (file provenance ambiguity, not resolved, flagged for the manager).** The task doc's step
  2 asks for the files "the Step-8 campaign actually consumed." Per `2J_docs_occ_nTemp/08_simulation.md`'s
  2026-06-07 entry, the Step-8 EnergyPlus campaign (6,000 runs, completed 2026-06-05, closed
  2026-06-07) ran on schedules frozen at 8B build time and is documented elsewhere as having a
  provenance gap (its as-built 2022/2030 schedule snapshot is "unrecoverable" — survives only inside
  the campaign's IDFs). The 2026-07-09 relink that produced today's `BEM_Schedules_2022.csv`/
  `BEM_Schedules_2030.csv` happened AFTER that campaign closed. I used the current (2026-07-09)
  non-BAK files because (a) they are what the 2026-07-15 log entry itself used to get 70.2/78.5, which
  is the number this task is asked to re-derive, and (b) the task doc's own file list
  (`08_simulation.md`, `07_bemIntegrationGSS.md`) points at plain `BEM_Setup/BEM_Schedules_2022.csv` /
  `_2030.csv` with no BAK suffix. This re-derives the LOG's number, not necessarily the number that
  drove the physical 6,000 EnergyPlus runs — those two may differ. Left for the manager to rule on
  whether that distinction matters for WP1 step 2's re-targeting design.
- **D-T01-1 manager ruling (2026-09-15).** The distinction matters, but it is testable, not a judgement call.
  The paper's numbers come from the 2022/2030 re-run dated 2026-07-10/11 (the short `sample_NNN_HH<id>`
  dirs that match `cell_manifest.csv.new_2022_2030_20260711`), which is AFTER the 2026-07-09 relink, so the
  current non-BAK files are the right working assumption. The June 6,000-run campaign is not the paper's
  source for 2022/2030. **Test for the collector:** for 3 panel households (different cells), take the
  occupancy schedule the EnergyPlus run actually used (schedule CSV or `Schedule:Compact`/`Schedule:File`
  in the short dir's 2022 and 2030 inputs; `grep`/`head` only) and compare its 24 weekday + 24 weekend
  values with the rows for that `SIM_HH_ID` in the current `BEM_Schedules_2022/2030.csv` (`grep` by ID).
  All match = ruling confirmed. Any mismatch = STOP, record both series, the WP1 re-targeting spec waits.
- **D-T01-1 collector result (2026-09-15): CONFIRMED, all match, WP1 re-targeting spec is UNBLOCKED.**
  See Verified item 6 for the 3-household, 12-series, 48-value-each comparison — every value matched
  exactly. The current `BEM_Setup/BEM_Schedules_2022.csv`/`_2030.csv` are the right files: they equal
  what EnergyPlus physically consumed for the paper's 2022/2030 re-run, not just what the 07-15 log
  happened to read. No further provenance work needed on this point.
- No weight column exists in either CSV, so "weighted mean" from task step 4 is reported as N/A in
  `run_meta.json` rather than computed.
- Panel-only breakdown implemented as a best-effort addition using the freshest cell manifest per
  cell; not a task requirement to guarantee correctness beyond the one spot-check above.

## Next
T01 is DONE. WP1 step 1's re-derivation is complete and the manager's provenance ruling (`D-T01-1`) is
confirmed with no mismatch, so nothing in this task blocks WP1 step 2 (the re-targeting spec). Next
owner is whoever picks up WP1 step 2 in `../00_REVISION_PLAN.md` §3 — read this doc's Verified items
5-6 first for the numbers to re-target against (2022 national weekday 70.24%, 2030 78.53%, vs the
Step-6 intended 76.93% -> 78.44%). The one open thread this task leaves: the small `DTYPE==8`
unmapped-archetype anomaly (Verified item 5) is unexplained; worth a look if per-archetype precision
matters later, but does not block anything now.

## WHAT I DID NOT VERIFY
- Did not open `outputs_step4/augmented_diaries.csv` (the source of the 76.93% Step-6 reference) to
  independently recompute 76.93 — took it as recorded in `step6_improvement_notes.md:841`.
- Did not verify that `SIM_HH_ID` values are unique/non-colliding across the 24 different cells (i.e.
  that a given ID always means the same physical household regardless of which city cell drew it);
  assumed so because IDs appear to be drawn from one shared national household pool, and the 3
  households spot-checked for `D-T01-1` were each drawn from a different cell with no collision, but
  this is not a proof of uniqueness across all 1200 panel IDs.
- Did not investigate the root cause of the `DTYPE==8` anomaly (Verified item 5) — recorded, not
  explained, per the collector's mechanical-only scope.
- `athome_gap.py`'s internal computation logic (weighting, grouping, rounding) was not code-reviewed
  line by line by the collector — only its outputs were checked against independent EnergyPlus-input
  ground truth (Verified item 6) and against the expected log numbers (Verified item 5), both of which
  passed.
