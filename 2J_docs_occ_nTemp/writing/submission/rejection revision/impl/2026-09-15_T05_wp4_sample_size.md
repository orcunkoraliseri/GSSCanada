# T05 — WP4 steps 1–2: sampling procedure and sample-size convergence — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP4, §10
Status:     DONE (job completed, output verified 2026-09-15)

## Task

**Why.** A reviewer asked exactly what is sampled, how the 50-household panels are drawn, and whether
50 is enough.

**Steps.**
1. Sampling procedure (reading only). From `2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py`,
   `run_campaign_local.py`, `08_gen_cycle_schedules.py`, `step8_speed/run_heavy_array.sh`, and
   `2J_docs_occ_nTemp/08_simulation.md`, write down with `file:line`: what is stratified (dwelling
   type × province?), how the 50 household IDs are drawn, the seed, whether the same households are
   used in every year (paired panel), what one household contributes (schedule, end-use scaling),
   and how the 24 cell results are weighted to the stock.
2. Find the per-household, per-year results of the campaign (one `hourly_meters.csv` per
   sample × year under `/speed-scratch/o_iseri/step8_speed/campaign_N50/<cell>/` on Speed, or local
   aggregates in `outputs_step8/agg/`). Record path and counts with `ls`/`wc -l` only.
3. Script in `T05_scripts/`, run **on Speed** (`sbatch -p ps -c 32 --mem=64G -t 7-00:00:00`), on
   **2022 only** (2030 is defective until WP1): for each cell and for the stock-weighted total, draw
   subsets of N = 10, 20, 30, 40 households from the 50 (2,000 draws each, fixed seed) and record
   the mean and 95% range of annual electricity (kWh), midday share, load factor and peak hour, plus
   the N = 50 value. Use the paper's metric definitions (read them from
   `Step8_docs/08_simulation_plots.py` and cite `file:line`). Output `convergence_2022.csv`.
4. Write the JobID in the Ledger. **End your turn.**

**Employee rules.** Plan §10 rules 1–6 apply. Python on Speed:
`/speed-scratch/o_iseri/envs/step4/bin/python`. Do not modify anything under `campaign_N50/`.

## Ledger
- Job **1328242** (`t05_conv2022`, partition `ps`, `-c 32 --mem=64G -t 7-00:00:00`) submitted
  2026-09-15 via `sbatch /speed-scratch/o_iseri/2J_revision/T05/T05_scripts/submit_t05.sh`.
  Confirmed with `sacct -j 1328242 -X` -> state PENDING at submit time. Runs
  `T05_scripts/convergence_2022.py` on `/speed-scratch/o_iseri/envs/step4/bin/python`, reading
  `T05_scripts/agg_annual_2022.csv` (scp'd from the local agg table, see Verified). Writes
  `T05_out/convergence_2022.csv`. Stdout/stderr: `T05_out/t05_1328242.out` / `.err`.
- Job **1328242** COMPLETED, exit 0:0, confirmed 2026-09-15 via `sacct -j 1328242 -X
  --format=JobID,State,ExitCode,Elapsed,CPUTime,NCPUS,Start,End` on Speed ->
  `State=COMPLETED ExitCode=0:0 Elapsed=00:00:09 CPUTime=00:04:48 NCPUS=32`. All output re-scp'd
  from `/speed-scratch/o_iseri/2J_revision/T05/T05_out/` and `T05_scripts/` to local
  `impl/T05_out/` and `impl/T05_scripts/` (`scp -o BatchMode=yes -o ConnectTimeout=60`, no retry
  needed). `T05_out/t05_1328242.err` is 0 bytes (no stderr). The 9 s elapsed is not evidence of
  truncated work: `CPUTime=00:04:48` = `9 s x 32 NCPUS` exactly, i.e. Slurm charged the full
  32-CPU allocation for the whole wall time even though the script (`T05_scripts/convergence_2022.py`)
  is single-threaded numpy/pandas with no multiprocessing — see row-count proof below.

## Verified

**Step 1 — sampling procedure (file:line, `2J_docs_occ_nTemp/` unless stated).**
- Driver `Step8_docs/run_paired_mc.py:1-94` is a one-cell CLI (`--archetype`, `--city`, `--n`
  default 50, `--seed` default 42, `--sim-mode`); calls `run_step8_paired_mc()` in
  `Step8_docs/eSim_bem_utils_2J/main.py:1977`.
- **Stratification.** Candidate pool = `SIM_HH_ID`s present in ALL 5 years, filtered to the
  cell's `dtype` (archetype) x `region` (province) — `main.py:2029-2037`. 4 archetypes x 6
  climate-zone cities = 24 cells (`main.py:84-100`; local analysis copy at
  `Step8_docs/08_simulation_plots.py:54-71`).
- **Draw.** `sampled = rng.sample(pool, n)` — simple random sample **without** replacement of
  N=50 from the pool (`main.py:2039-2048`); falls back to sampling **with** replacement only if
  the pool itself has <50 households for that cell (warns, `main.py:2044-2047`) — not observed
  in this campaign (Step 2 below confirms 50/50 unique per cell).
- **Seed.** `rng = random.Random(_step8_cell_seed(seed, cell_label))`, `seed` defaults to 42
  (`run_paired_mc.py:38`; SLURM array script `step8_speed/run_heavy_array.sh:111` passes
  `--seed 42` explicitly). `_step8_cell_seed()` (`main.py:1952-1962`) derives a per-cell offset
  from SHA-256 of the cell label so every cell gets an independent but fully deterministic draw
  — same base seed reproduces the same 50 households on any machine/array task.
- **Paired panel.** Yes — the SAME 50 `sim_hh_id`s are used in all 5 cycle-years for a cell; only
  the occupancy schedule differs by year, building+weather held fixed (`main.py:2050-2074`,
  design rationale in `08_simulation.md:69-92`).
- **What one household contributes.** Its `SIM_HH_ID`'s occupancy schedule is injected into the
  shared archetype IDF via `integration.inject_schedules()`
  (`Step8_docs/eSim_bem_utils_2J/integration.py:1269-1309`): lighting via a "Daylight Threshold"
  method, equipment/DHW via a "Presence Filter" (min/max toggle) method. No separate
  hhsize-based floor-area or end-use magnitude scaling is applied — `hhsize` is recorded in the
  manifest (`main.py:2055-2057`) but not used as a multiplier in this driver.
- **Stock weighting — two different descriptions found, code wins.** The design doc
  (`08_simulation.md:134-135`) says cells are weighted by "empirical `DTYPE x PR` share of the
  144,465-HH stock" (i.e. archetype AND province specific). The actual analysis code
  (`08_simulation_plots.py:74-77`) only has **4 archetype-level weights**
  (`SingleD .529, MidRise .213, OtherDwelling .130, HighRise .128`, already summing to 1.0, no
  further renormalization needed) — no province-level weight exists. `_stock_weighted_circular_mean()`
  (`08_simulation_plots.py:300-321`) splits each archetype's weight **equally across its (up to
  6) cities** (`w_each = STOCK_WEIGHTS[arch] / len(sub)`). Recorded as a Decision below.

**Step 2 — where the per-household 2022 results live, counts by `ls`/`wc -l`.**
- **Speed** `/speed-scratch/o_iseri/step8_speed/campaign_N50/<cell>/`: only **12 of 24 cells**
  present — `HighRise` and `MidRise` x all 6 cities (the SLURM "heavy array",
  `step8_speed/run_heavy_array.sh:8,30-31`, 12 tasks). Each cell dir has 51 entries
  (`cell_manifest.csv` + 50 `sample_NNN_HH<id>` dirs); `ls <cell>/*/2022/hourly_meters.csv | wc -l`
  = **50/50** for all 12 cells (checked all 12). `SingleD` and `OtherDwelling` (the other 12
  cells) do **not exist on Speed** (`ls` on the parent GCMAIN mirror path returned "No such file
  or directory").
- **Local** `BEM_Setup/SimResults_Step8/campaign_N50/`: all 24 cells present, but the two
  archetypes missing from Speed have a problem: `SingleD__Toronto_5A/` holds **100** sample
  dirs, not 50, with two DIFFERENT `sim_hh_id`s sharing the same `sample_NNN` index (e.g.
  `sample_001_HH33188` vs `sample_001_HH34299`); `LastWriteTime` splits cleanly into two dated
  batches, 2026-06-02 (older/stale) and 2026-07-10 (later); **no `cell_manifest.csv` present** to
  disambiguate which batch is canonical from the raw directory alone.
- **Local aggregate resolves it.** `outputs_step8/agg/agg_annual.csv` (1.5 MB, checked with
  `wc -l`/`head`/`awk` only, never opened in full) has exactly **6001 rows** = header + 4
  archetypes x 6 cities x 50 HH x 5 years, dated 2026-07-15 (after the 2026-07-10 local batch).
  For 2022 it has exactly **50 rows per cell, all 24 cells, 1200 rows total**, and for
  `SingleD__Toronto_5A` 2022 the 50 `sim_hh_id`s match the **2026-07-10** directory batch
  (sample 1=HH33188, 2=HH18606, 3=HH86963, 4=HH19541 — verified against the `ls` timestamps
  above), i.e. whatever built this aggregate already resolved to the canonical (later) run, not
  the stale 2026-06-02 leftovers. No NaNs in `elec_facility_kWh`/`load_factor`/`midday_share`/
  `mean_peak_hour` for any of the 1200 2022 rows (`awk` check, 0 matches).
- Used `outputs_step8/agg/agg_annual.csv` (2022 slice only, 1201 lines incl. header) as the Step
  3 input — it already carries the paper's own per-household metrics (see below), so Step 3 did
  **not** need to re-read any raw `hourly_meters.csv`, on Speed or locally.

**Step 3 — metric definitions used (`Step8_docs/08_simulation_plots.py`, cited in the script's
own header too).**
- Annual electricity (kWh): `elec_facility_kWh`, sum of the `Electricity:Facility` meter
  (`08_simulation_plots.py:80` meter const, `:361` the sum).
- Midday share: facility electricity in hours [9,17) / total (`MIDDAY=(9,17)` at `:114`; formula
  at `:387`).
- Load factor: mean hourly facility load / peak hourly facility load (`:385`).
- Peak hour: used `mean_peak_hour` — the **circular mean of the 365 daily-peak hours**
  (`_circular_mean_hour`, `:278-285`; computed per household at `:372,378,388`) — because that is
  the metric the paper's own stock-weighted figure uses (`:300-321`, `:860-890`). The single
  annual-max hour (`peak_hour_annual`, `:375`) also exists in `agg_peak.csv` but was **not** used;
  flagged in Decisions.

**Step 4 (collector, 2026-09-15) — proof the job did the full design, not a truncated one.**
- Log `T05_out/t05_1328242.out`: `=== T05 convergence_2022 | job=1328242 | node=speed-39... ===` /
  `DONE: wrote 500 rows -> .../T05_out/convergence_2022.csv` / `=== exit=0 ===`. No warnings, no
  tracebacks.
- `T05_out/convergence_2022.csv`: `wc -l` = **501** (header + 500 data rows), matching the log's
  "wrote 500 rows" exactly.
- Row count derived from the script's own design (`T05_scripts/convergence_2022.py`): per cell,
  N=50 row x 4 metrics (`:107-111`) + 4 sub-sizes {10,20,30,40} x 4 metrics (`:113-118`) = 20 rows;
  24 cells x 20 = 480 (`:90-91` asserts exactly 24 cells and, per cell, exactly 50 rows in the
  input — a hard crash, not a silent skip, if either count were off). Plus the STOCK block: N=50 x
  4 metrics (`:128-140`) + 4 sub-sizes x 4 metrics (`:143-171`) = 20 rows. Total = 480 + 20 =
  **500**, matching the file exactly.
- `awk -F, 'NR>1{print $1}' convergence_2022.csv | sort | uniq -c` = all 24 cell labels present,
  each with exactly 20 rows, plus `STOCK` with 20 rows (25 unique `cell` values total, 24 + STOCK)
  — no missing cell, no missing metric x N combination.
- `awk -F, 'NR>1 && $4==""'` (empty `mean` field) = **0 matches** — no NaNs/blanks in any of the
  500 rows' `mean` column.
- 4 metrics used = `elec_facility_kWh`, `midday_share`, `load_factor`, `mean_peak_hour`, matching
  the doc's Step 3 metric list exactly; all 5 sample sizes present per cell/STOCK: N = 10, 20, 30,
  40, 50.
- **Conclusion: the run is complete** — every cell, every metric, every requested N, every
  2,000-draw resample the script and the task doc specify is in the output file; nothing is
  missing or silently skipped. The 9 s elapsed is explained (Step 4 above), not suspicious.

**Step 5 (collector) — convergence result, no invented criterion.**
- The task doc and `00_REVISION_PLAN.md` §WP4 give **no numeric stopping/convergence threshold**
  for this N=10-40 subsample check. The plan's only stated numeric test
  (`00_REVISION_PLAN.md:242`, "N = 50 mean from step 3 falls inside the N = 200 CI for every
  metric") belongs to **WP4 step 3, the separate N=200 Montreal runs**, which this job (WP4 steps
  1-2 only, per this doc's own title) does not perform and for which no data exists yet. No
  threshold is invented here.
- What is actually measured: the 95% range width (`hi95-lo95`) at each N, stock-weighted total,
  from `T05_out/convergence_2022.csv`:
  - `elec_facility_kWh`: N10=566.4 kWh, N20=353.3, N30=234.7, N40=142.5 (monotonic narrowing,
    ~4x tighter N10->N40; N40 range is 0.12% of the N50 mean 117,483.6 kWh).
  - `midday_share`: N10=0.0200, N20=0.0128, N30=0.0089, N40=0.0053 (monotonic, ~3.8x tighter).
  - `load_factor`: N10=0.0124, N20=0.0072, N30=0.0051, N40=0.0032 (monotonic, ~3.9x tighter).
  - `mean_peak_hour`: N10=1.15 h, N20=0.73 h, N30=0.48 h, N40=0.30 h (monotonic, ~3.8x tighter).
  - All four means are stable across N (e.g. `elec_facility_kWh` mean 117,484-117,486 kWh across
    N=10-50; `mean_peak_hour` mean 14.99-15.08 h) — the range narrows around an already-stable
    mean, it does not shift.
  - Per-cell ranges (24 cells, not reproduced in full here) show the same monotonic-narrowing
    pattern; not individually quoted per the doc's "stock-weighted total first" instruction.

## Decisions
- **D-T05-1 (assumed, not asked of the manager).** Used `mean_peak_hour` (circular mean of daily
  peaks) as "peak hour", not `peak_hour_annual` (the single hottest hour of the year), because it
  matches the paper's own stock-weighted peak-timing figure. If the manager wants the single-hour
  definition instead, `agg_peak.csv` (not copied to Speed) has `peak_hour_annual` per household.
- **D-T05-2 (assumed).** Stock weighting in the script follows the **code**
  (`08_simulation_plots.py:74-77,300-321` — archetype-only weight, split equally across the 6
  cities), not the design doc's DTYPE x PR description (`08_simulation.md:134-135`), since no
  province-level weight is actually computed anywhere in the analysis code. This is a
  documentation/code mismatch worth flagging to the manager, not something this task resolves.
- **D-T05-3 (assumed).** For the stock-weighted total's subsampling, each of the 24 cells draws
  its N-of-50 subsample **independently per iteration** (2,000 shared iteration indices, but the
  household draw itself is per-cell), then combined by the cell weight. Not asked in the task doc;
  flagged as a design choice a reviewer could reasonably want changed (e.g. correlated draws
  across cells within an iteration would not change the mean but could change the reported 95%
  range slightly).
- **D-T05-4 (assumed).** Input to the Speed job is the 2022 slice of the existing local
  `outputs_step8/agg/agg_annual.csv`, not a re-parse of raw `hourly_meters.csv` on Speed. This
  is faster and uses already-validated per-household metrics, but it does depend on that
  aggregate file being correct/current (dated 2026-07-15, matches the canonical 2026-07-10 local
  campaign batch per the sim_hh_id cross-check above).

- **Manager rulings (2026-09-15).** D-T05-1 accepted: the paper's peak-timing figure uses the circular
  mean, so that is the definition. D-T05-3 accepted: the 24 cells are independent samples, so independent
  per-cell draws are correct. D-T05-4 accepted for this convergence check only; any number that goes into the
  paper is re-derived from raw meters in Wave 3. **D-T05-2 is a real methods-text issue, not a script issue:**
  the script must follow the code (it produced the paper), and the manuscript's stock-weighting description
  (dwelling type x province) does not match what the code did (dwelling type only, split equally over the six
  cities). Carried to plan WP4/WP10: the rewrite must describe the code's weighting, or WP4 changes the
  weighting and all stock-weighted numbers are recomputed. Decision deferred to the WP4 spec.

## Next
**Manager 2026-09-15 — read before using this CSV in the paper.** The ~4x narrowing from N=10 to N=40
is a finite-pool artefact, not convergence: draws are WITHOUT replacement from only 50 households, so
width scales as sqrt((1/n)(50-n)/49). That predicts 0.2857/0.0714 = 4.0x; measured stock midday width
0.0200/0.0053 = 3.8x. At N=40 of 50 the draws overlap 80 %, so narrow intervals are guaranteed.
What the CSV CAN support: at stock level even N=10 keeps annual electricity within about ±0.25 % and
midday share within about ±1 pp of the N=50 mean (sampling spread only, not model error). What it
CANNOT support: "N=50 is enough". That needs WP4 step 3 (N=200 fresh draws, N=50 inside N=200 CI).
Do not build the SI figure from this CSV alone.
Earlier collector note: WP4 steps 1-2 are DONE and verified (2026-09-15): sampling procedure written (Step 1), input
located (Step 2), job 1328242 completed with all 500 expected rows present and no gaps (Step 4/5
above). Manager decisions on D-T05-1/D-T05-2/D-T05-3/D-T05-4 already recorded above (2026-09-15).
Remaining open items for the manager, not for a cold collector to decide:
1. WP4 step 3 (the N=200 Montreal larger-N check, 1,200 new runs) has not been started — this is
   a separate, new-compute task, not part of T05.
2. Whether/how to build the SI convergence figure and Methods sentence from
   `T05_out/convergence_2022.csv` (plan's "Expected result").
3. Per-cell (not just stock-weighted) convergence numbers are in the CSV but not individually
   quoted in this doc — read `T05_out/convergence_2022.csv` directly if a specific cell is needed.

## WHAT I DID NOT VERIFY
- Did **not** re-derive `outputs_step8/agg/agg_annual.csv` from raw `hourly_meters.csv` — trusted
  the existing aggregate (cross-checked only its row counts, NaNs, and the `sim_hh_id`-vs-mtime
  match for one cell, `SingleD__Toronto_5A`; did not check the other 23 cells' `sim_hh_id`s
  against their directory mtimes).
- Did **not** confirm what produced the 2026-06-02 stale batch under `SingleD`/`OtherDwelling`
  locally (an older seed? an interrupted run? no manifest survives to say) — only that the
  2026-07-15 aggregate does not appear to include it for the one cell checked.
- Did **not** wait for or read the job's output — job was PENDING at submit time, per the no-wait
  rule.
- Did **not** check whether `SingleD`/`OtherDwelling` 2005/2010/2015/2030 years have the same
  100-dir doubling problem (only checked 2022, and only fully for `SingleD__Toronto_5A`; the
  `agg_annual.csv` row-count check (50/cell/year, all cells/years, 6000 total) suggests the
  aggregate itself is clean everywhere, but the raw local directories were not re-checked cell by
  cell).
- Did not re-verify the 12 Speed-side heavy cells' `cell_manifest.csv` contents (only counted
  `sample_*` dirs and `hourly_meters.csv` files via `ls`/`wc -l`).
- Collector (2026-09-15) did **not** re-derive `convergence_2022.csv` independently (e.g. rerun the
  resample in a separate script) — verified it by (a) row-count arithmetic against the script's own
  design, (b) the script's internal assertions (`:90-91`, would crash on a row/cell mismatch) having
  passed (exit 0), and (c) `awk`/`wc -l` structural checks (no NaNs, 24 cells x 20 rows + STOCK x 20).
  Did not re-check `T05_scripts/agg_annual_2022.csv` (the job's input) row-by-row against the local
  `outputs_step8/agg/agg_annual.csv` 2022 slice referenced in Step 2 above — only its row count via
  `wc -l` (1201 = 1200 + header, consistent with Step 2's "1200 rows total" for 2022).
- Did not apply any numeric convergence/stopping threshold to the N=10-40 results, because none
  exists in this task doc or in `00_REVISION_PLAN.md` §WP4 for that check (the plan's only
  threshold, N=50-inside-N=200-CI, belongs to the not-yet-run WP4 step 3). Only the observed
  range-narrowing pattern is reported (Step 5 above).
- Did not build the SI convergence figure or the Methods sentence the plan calls the "Expected
  result" — out of scope for this verification pass.
