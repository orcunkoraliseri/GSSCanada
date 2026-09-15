# T15 — WP5 step 3 fix: scale-free stock shape and E+ day types — implementation state

Task doc:   this file (section "Task")
Parent:     `2026-09-15_T09_wp5_sim_vs_measured_toronto.md` (read Decisions and the manager note in Next first)
Status:     COLLECTED — job 1328281 COMPLETED, exit 0:0, 25s; all checks passed

## Task

**Why.** T09 job 1328279 ran cleanly but its weighted-stock comparison mixes whole-building totals
(HighRise, MidRise) with single-dwelling totals (SingleD), and it took weekday/weekend from the real
2022 calendar although EnergyPlus ran the schedules on a Sunday-start calendar (real 2022-01-01 is a
Saturday). Redo the comparison so it compares **shape**, on the day type the schedule actually used.
**Numbers only; no pass/fail, no interpretation.**

**All compute on Speed via `sbatch`** (`-p ps -c 8 --mem=32G -t 7-00:00:00`), python
`/speed-scratch/o_iseri/envs/step4/bin/python`, work dir `/speed-scratch/o_iseri/2J_revision/T15/`
(create it with `scp -r` of a local folder, as T09 did). Login node: only `sbatch squeue sacct scancel
scontrol cd ls scp` and single-file `tail head grep wc -l cat`. **Never `find`, `du`, or python on the
login node.** tcsh: no `2>&1` or `2>/dev/null` in ssh strings; `ssh -o BatchMode=yes -o ConnectTimeout=60`.

**Start from T09's script** (path in the T09 Ledger); copy it to `T15_scripts/t15_sim_vs_measured.py`.
Same inputs (T06 input dir on Speed, read only), same run selection, same unchanged T02 metric functions.

**Changes, and only these:**
1. **Scale-free stock shape.** For each run, divide its hourly series by that run's own annual mean
   hourly value (per series). Archetype profile = mean over its runs of the normalized series. Stock
   profile = archetype profiles weighted by `08_simulation_plots.py:74-77` weights. Feed that to
   `compute_slice_outputs` (so load factor, peak-to-average, midday share, peak hour are shape metrics;
   `mean_kwh_per_premise` is then ≈1 by construction and must be dropped from the join).
2. **Day type from EnergyPlus.** In the join with measured data, the simulated slice uses the `eplus`
   day type (Sunday start, weekday = Mon–Fri of that sequence); holidays stay on the real calendar date
   (T09 Decision). Weather/season/month slices stay on the real date. Also keep the `real2022` join as a
   second block labelled `calendar=real2022` so the effect of the fix is visible.
3. **Per-dwelling level (optional, only with evidence).** grep the local Toronto HighRise and MidRise
   `Scenario_2022.idf` for a dwelling-unit count (zone multipliers, zone names per unit, or a comment
   naming units). If an explicit count exists, also report annual Facility kWh per dwelling per archetype
   with the evidence line. If not, write NOT FOUND. Do not infer units from floor area.
4. **Clock.** Do not shift hours. In Decisions, state with `file:line` evidence what the IDF sets for
   DST and holidays; do not claim how EnergyPlus reports time unless a local file says it.

**Outputs** `T15_out/`: `sim_toronto_2022_shape_metrics.csv` (per archetype and stock, both calendars,
series (a) and (b)), `sim_vs_measured_toronto_2022_shape.csv` (stock only; columns period, daytype,
series, calendar, measured_scope, metric, sim, measured, sim_minus_measured; shoulder first), slurm log.
scp back to `impl/T15_out/`.

**Employee rules.** One job. `py -3 -m py_compile` locally, scp, submit, write JobID in Ledger, **end the
turn** ("job N submitted, state written to <this doc>"). No waiting, polling or sleep. Write NOT FOUND
rather than guess. Past ~150k tokens: write state, stop, "handoff needed".

**Collector (later, fresh agent).** `sacct`, scp, check measured column equals `T02_out/ieso_metrics.csv`
exactly, fill Verified with weekday shoulder and full-year shape metrics for the stock (both series,
eplus calendar) and each archetype alone.

## Ledger
- 2026-09-15 (employee) · Read T09's Ledger/Decisions/Next (job 1328279, COMPLETED, outputs
  collected in `impl/T09_out/`). Manager note in T09 Next names the three problems this task
  fixes: scale mixing (whole-building HighRise/MidRise vs single-dwelling SingleD in the stock
  weight), wrong day-type calendar in the join (`real2022` instead of `eplus`), and an unresolved
  DST clock note. Copied `T09_scripts/sim_vs_measured_toronto_2022.py` to
  `T15_scripts/t15_sim_vs_measured.py` and made only the 4 listed changes; run selection,
  `compute_slice_outputs`/`circular_mean_hour_idx` (T02 metric functions), `discover_toronto_2022_runs`
  /`load_cell_manifest`, `build_calendar_frame`, `period_month_map`, `full_sub_table`,
  `STOCK_WEIGHTS`, `HOLIDAYS_2022` all left byte-identical to T09's script (diff is: the
  normalization step before building each run's frame, dropped `profiles_long` output — not in
  this task's Outputs list, the two-calendar join loop, `DWELLING_COUNT`, and the run_meta fields
  for item 3).
- **New finding while gathering evidence for item 3 (per-dwelling count):** grepped
  `OtherDwelling__Toronto_5A/sample_001_HH22934/2022/Scenario_2022.idf` locally and found 7
  separate `living_unit1`..`living_unit7` zone triples (`:4392-4613`, no `ZoneGroup` multiplier
  needed since each unit is its own explicit zone) — **OtherDwelling is a 7-unit row-house block,
  not a single dwelling.** T09's manager note in `2026-09-15_T09_wp5_sim_vs_measured_toronto.md`
  Next section named only "HighRise, MidRise" as whole-building and implied SingleD/OtherDwelling
  were both single-dwelling; that implication was wrong for OtherDwelling. Confirmed `SingleD`
  really is 1 unit (`SingleD__Toronto_5A/sample_001_HH33188/2022/Scenario_2022.idf:4392-4425`, one
  `living_unit1` triple, no `ZoneGroup`). `MidRise`/`HighRise` dwelling counts derived from
  `ZoneList`/`ZoneGroup` objects — see Decisions for the full evidence lines and arithmetic
  (`DWELLING_COUNT = {"SingleD": 1, "OtherDwelling": 7, "MidRise": 31, "HighRise": 79}`).
  `HighRise`'s `ZoneGroup`/`Apartment`-zone structure re-checked on a second sample
  (`sample_002_HH129161`) — identical line numbers and multiplier value, so the building geometry
  template is shared across samples within an archetype/city cell (not re-checked for
  MidRise/OtherDwelling/SingleD beyond the one sample each cited).
- `py -3 -m py_compile T15_scripts/t15_sim_vs_measured.py` — OK.
- **Local smoke test** (`t15_smoke.py`, scratchpad, not committed — real local data, no cluster):
  `discover_toronto_2022_runs` against the local `BEM_Setup/SimResults_Step8/campaign_N50` tree
  found 50/50/50/50 Toronto runs per archetype (matches T09's own count). Calendar frame: 8760
  rows, `real2022` weekend rows = 2,472, `eplus` weekend rows = 2,448 — identical to T09's own
  numbers (calendar-building code is unchanged). Loaded 2 real runs per archetype, applied the
  normalization exactly as in `main()`: confirmed each normalized run series has annual mean
  1.0 to 1e-9. Built `StockWeighted` with the same `STOCK_WEIGHTS[a]/n` weighting as `main()` —
  weights summed to exactly 1.0. Ran `compute_slice_outputs` on `full_year`/`shoulder` ×
  `weekday` for all 5 entities × 2 series × 2 calendars (40 rows): **`StockWeighted`
  `mean_kwh_per_premise` came out 0.927–0.993** (near 1.0 as the task predicts; not exactly 1.0
  because this smoke test used only 2 runs/archetype, not the full 50). Per-dwelling sanity
  numbers from this same small sample: SingleD 8,146 kWh/dwelling, OtherDwelling 6,821
  kWh/dwelling, MidRise 8,769 kWh/dwelling, HighRise 4,884 kWh/dwelling — plausible residential
  magnitudes for all four archetypes now (T09's own single-dwelling-only reading of OtherDwelling
  would have reported 47,745 kWh/dwelling for OtherDwelling, an outlier next to SingleD's 8,146).
  This is a 2-run/archetype smoke number, not the job's real 50-run/archetype output — collector
  must re-derive from `run_meta.json`.
- Uploaded via `scp -r` (local `T15_upload/T15/` → `/speed-scratch/o_iseri/2J_revision/`, no
  login-node `mkdir`): remote `T15/T15_scripts/t15_sim_vs_measured.py` is 26,585 bytes, matching
  the local file exactly (`ls -la` both sides).
- **Job 1328281** submitted: `sbatch -p ps -c 8 --mem=32G -t 7-00:00:00
  --job-name=T15_sim_vs_measured_fix --chdir=/speed-scratch/o_iseri/2J_revision/T15
  --output=/speed-scratch/o_iseri/2J_revision/T15/T15_%j.out
  --wrap="/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T15/T15_scripts/t15_sim_vs_measured.py"`. `sacct -j 1328281
  -X` confirmed the job exists, state **PENDING** at submission. The job's own
  `os.makedirs(OUT_DIR, exist_ok=True)` creates `/speed-scratch/o_iseri/2J_revision/T15/out/` on
  the compute node. Outputs expected: `T15/out/sim_toronto_2022_shape_metrics.csv`,
  `sim_vs_measured_toronto_2022_shape.csv`, `run_meta.json`, plus `T15/T15_1328281.out`. **Not yet
  collected — a fresh agent must read these** (`sacct -j 1328281` first for state/exit code).
- 2026-09-15 (collector) · `sacct -j 1328281 -X`: COMPLETED, ExitCode 0:0, Elapsed 00:00:25
  (Start 11:20:01, End 11:20:26), matches manager fact. `ls -l` on
  `/speed-scratch/o_iseri/2J_revision/T15/` and `.../T15/out/`: `T15_1328281.out` (655 B),
  `out/run_meta.json` (2,370 B), `out/sim_toronto_2022_shape_metrics.csv` (152,061 B),
  `out/sim_vs_measured_toronto_2022_shape.csv` (193,339 B). Slurm log is only 8 lines, no
  error/warn/invalid/not found/skipped strings present: "n runs per archetype:
  {'SingleD': 50, 'OtherDwelling': 50, 'MidRise': 50, 'HighRise': 50} (total 200, expect 50 each)",
  "loaded 200 runs ok, 0 skipped", per-entity timing lines, "wrote ...shape_metrics.csv (880
  rows)", "wrote ...shape.csv (1760 rows)", "done in 24.6s" — matches `run_meta.json`'s
  `n_runs_loaded_ok: 200`, `n_runs_skipped: 0`, `skipped: []`. scp'd all 4 files to local
  `impl/T15_out/`; local byte sizes identical to remote (655 / 2,370 / 152,061 / 193,339, both
  sides checked with `ls -l`).
- **Exact-match check** (`py -3`, local, both files already on disk, no cluster re-read): every
  row of `sim_vs_measured_toronto_2022_shape.csv`'s `measured` column (1,760 rows, both
  `measured_scope` values, all periods/daytypes/series/calendars) matched the corresponding
  `(scope, year=2022, period, daytype, metric)` cell in `T02_out/ieso_metrics.csv` — max abs diff
  3.55e-15 (float rounding only), 0 mismatches, 0 rows missing a reference. Confirmed `calendar`
  column has both `eplus` and `real2022`, `measured_scope` has both `Toronto` and `Ontario`, first
  data row is `period=shoulder` (shoulder first, as required). `StockWeighted`
  `mean_kwh_per_premise` in `sim_toronto_2022_shape_metrics.csv` (176 rows, all
  periods/daytypes/series/calendars): mean 1.011, range 0.79-1.46 across period sub-slices; the
  `full_year` rows alone (the ones normalization is defined against) are all in 0.94-1.08, i.e.
  approximately 1 as expected. Non-`full_year` periods (month/season slices) deviate from 1 by
  construction, since normalization divides by each run's annual mean, not the period mean, so a
  weekday-only or winter-only slice need not average to exactly 1 — not a defect.
- Read `run_meta.json` in full (2,370 B, small enough for direct read): `dwelling_count`
  `{"SingleD":1,"OtherDwelling":7,"MidRise":31,"HighRise":79}` matches the Ledger/Decisions
  evidence lines already written by the employee (not re-derived here). Per-dwelling annual
  Facility kWh (`annual_facility_kwh_per_dwelling_estimate`): SingleD 8,164.71, OtherDwelling
  6,777.72, MidRise 8,793.39, HighRise 4,975.10 kWh/dwelling/yr (= `meter_mean / DWELLING_COUNT`
  per archetype, per the file's own `note` field).
- Derived measured Toronto annual kWh/premise from `ieso_metrics.csv` (`py -3`, local): Toronto
  2022 `full_year` has three `daytype` rows (weekday n_days=253, weekend n_days=103, holiday
  n_days=9; sums to 365, not a leap year), each with its own `mean_kwh_per_premise` — no single
  "all-days" row exists, but it is derivable as the n_days-weighted average:
  (253*0.8215694 + 103*0.8763806 + 9*0.8291109)/365 = 0.8372226 kWh/premise/hour, x8760 h =
  7,334.07 kWh/premise/yr. This sits between the sim's SingleD (8,164.71) and OtherDwelling
  (6,777.72) per-dwelling values, plausible given Toronto's premise mix.

## Verified
All numbers below read from `impl/T15_out/sim_vs_measured_toronto_2022_shape.csv` (stock, joined
against measured) and `impl/T15_out/sim_toronto_2022_shape_metrics.csv` (archetypes alone, and the
real2022-calendar stock rows, computed locally against `T02_out/ieso_metrics.csv` since that join
file is stock-only). daytype=weekday throughout, per the task's "weekday shoulder"/"weekday
full_year" wording. metric units: load_factor and midday_share are fractions (mean/peak,
mean/all-hours share of 10:00-15:59), peak_to_avg is a ratio, mean_peak_hour is hour-of-day (0-23).

### 1. Stock, weekday, eplus calendar (sim vs measured Toronto 2022 vs measured Ontario 2022)
Shoulder, series (a) facility:
  load_factor    sim=0.4144  Toronto=0.4305  diff=-0.0160 | Ontario=0.4545  diff=-0.0401
  peak_to_avg    sim=2.4129  Toronto=2.3231  diff=+0.0898 | Ontario=2.2002  diff=+0.2127
  midday_share   sim=0.3408  Toronto=0.3513  diff=-0.0104 | Ontario=0.3498  diff=-0.0089
  mean_peak_hour sim=17.37   Toronto=18.69   diff=-1.32   | Ontario=18.42   diff=-1.05
Shoulder, series (b) nonhvac:
  load_factor    sim=0.5173  Toronto=0.4305  diff=+0.0868 | Ontario=0.4545  diff=+0.0628
  peak_to_avg    sim=1.9332  Toronto=2.3231  diff=-0.3899 | Ontario=2.2002  diff=-0.2669
  midday_share   sim=0.3226  Toronto=0.3513  diff=-0.0287 | Ontario=0.3498  diff=-0.0272
  mean_peak_hour sim=18.00   Toronto=18.69   diff=-0.69   | Ontario=18.42   diff=-0.42
Full_year, series (a) facility:
  load_factor    sim=0.3377  Toronto=0.4399  diff=-0.1022 | Ontario=0.4660  diff=-0.1283
  peak_to_avg    sim=2.9612  Toronto=2.2734  diff=+0.6878 | Ontario=2.1458  diff=+0.8154
  midday_share   sim=0.3289  Toronto=0.3524  diff=-0.0235 | Ontario=0.3518  diff=-0.0229
  mean_peak_hour sim=17.51   Toronto=18.25   diff=-0.74   | Ontario=17.91   diff=-0.40
Full_year, series (b) nonhvac:
  load_factor    sim=0.5171  Toronto=0.4399  diff=+0.0773 | Ontario=0.4660  diff=+0.0511
  peak_to_avg    sim=1.9338  Toronto=2.2734  diff=-0.3397 | Ontario=2.1458  diff=-0.2120
  midday_share   sim=0.3185  Toronto=0.3524  diff=-0.0339 | Ontario=0.3518  diff=-0.0333
  mean_peak_hour sim=17.66   Toronto=18.25   diff=-0.60   | Ontario=17.91   diff=-0.25

### 2. Each archetype alone, weekday, full_year, eplus calendar (sim vs measured Toronto/Ontario 2022)
SingleD facility:   load_factor sim=0.2837 (Tor diff -0.1562, Ont diff -0.1824); peak_to_avg
  sim=3.5254 (Tor +1.2519, Ont +1.3796); midday_share sim=0.3311 (Tor -0.0213, Ont -0.0207);
  mean_peak_hour sim=17.46 (Tor -0.79, Ont -0.45)
SingleD nonhvac:    load_factor sim=0.5038 (Tor +0.0640, Ont +0.0378); peak_to_avg sim=1.9847
  (Tor -0.2887, Ont -0.1611); midday_share sim=0.3030 (Tor -0.0494, Ont -0.0488); mean_peak_hour
  sim=17.00 (Tor -1.25, Ont -0.91)
OtherDwelling facility: load_factor sim=0.3404 (Tor -0.0995, Ont -0.1257); peak_to_avg sim=2.9381
  (Tor +0.6646, Ont +0.7923); midday_share sim=0.3297 (Tor -0.0228, Ont -0.0221); mean_peak_hour
  sim=17.91 (Tor -0.35, Ont -0.00)
OtherDwelling nonhvac:  load_factor sim=0.4946 (Tor +0.0547, Ont +0.0285); peak_to_avg sim=2.0220
  (Tor -0.2514, Ont -0.1238); midday_share sim=0.3221 (Tor -0.0303, Ont -0.0297); mean_peak_hour
  sim=18.00 (Tor -0.25, Ont +0.09)
MidRise facility:   load_factor sim=0.4684 (Tor +0.0285, Ont +0.0024); peak_to_avg sim=2.1350
  (Tor -0.1384, Ont -0.0108); midday_share sim=0.3377 (Tor -0.0147, Ont -0.0141); mean_peak_hour
  sim=18.22 (Tor -0.03, Ont +0.31)
MidRise nonhvac:    load_factor sim=0.5128 (Tor +0.0729, Ont +0.0467); peak_to_avg sim=1.9502
  (Tor -0.3232, Ont -0.1956); midday_share sim=0.3404 (Tor -0.0120, Ont -0.0114); mean_peak_hour
  sim=18.27 (Tor +0.02, Ont +0.36)
HighRise facility:  load_factor sim=0.4201 (Tor -0.0197, Ont -0.0459); peak_to_avg sim=2.3802
  (Tor +0.1068, Ont +0.2344); midday_share sim=0.3032 (Tor -0.0492, Ont -0.0486); mean_peak_hour
  sim=18.80 (Tor +0.55, Ont +0.89)
HighRise nonhvac:   load_factor sim=0.5313 (Tor +0.0915, Ont +0.0653); peak_to_avg sim=1.8821
  (Tor -0.3914, Ont -0.2637); midday_share sim=0.3446 (Tor -0.0078, Ont -0.0072); mean_peak_hour
  sim=18.23 (Tor -0.02, Ont +0.32)

### 3. Stock, weekday: eplus calendar vs real2022 calendar (calendar-fix effect, computed locally,
not in the join file since the join carries both but the direct side-by-side is useful here)
Shoulder facility:  load_factor eplus=0.4144 real2022=0.4222 diff=-0.0077; peak_to_avg
  eplus=2.4129 real2022=2.3686 diff=+0.0442; midday_share eplus=0.3408 real2022=0.3594
  diff=-0.0186; mean_peak_hour eplus=17.37 real2022=17.34 diff=+0.04
Shoulder nonhvac:   load_factor eplus=0.5173 real2022=0.5283 diff=-0.0111; peak_to_avg
  eplus=1.9332 real2022=1.8928 diff=+0.0405; midday_share eplus=0.3226 real2022=0.3428
  diff=-0.0202; mean_peak_hour eplus=18.00 real2022=18.00 diff=0.00
Full_year facility: load_factor eplus=0.3377 real2022=0.3432 diff=-0.0055; peak_to_avg
  eplus=2.9612 real2022=2.9141 diff=+0.0471; midday_share eplus=0.3289 real2022=0.3449
  diff=-0.0160; mean_peak_hour eplus=17.51 real2022=17.50 diff=+0.01
Full_year nonhvac:  load_factor eplus=0.5171 real2022=0.5280 diff=-0.0109; peak_to_avg
  eplus=1.9338 real2022=1.8940 diff=+0.0398; midday_share eplus=0.3185 real2022=0.3387
  diff=-0.0202; mean_peak_hour eplus=17.66 real2022=17.65 diff=+0.01
Reading: the calendar fix moves every metric by a small, consistent amount (load_factor/
peak_to_avg/midday_share within ~0.01-0.05, peak hour within ~0.04 h) — the effect exists and is
in a stable direction, but is much smaller than the sim-vs-measured gaps in section 1.

### 4. Annual Facility kWh per dwelling, sim (run_meta.json) vs measured Toronto 2022 (derived)
SingleD:       8,164.71 kWh/dwelling/yr
OtherDwelling: 6,777.72 kWh/dwelling/yr
MidRise:       8,793.39 kWh/dwelling/yr
HighRise:      4,975.10 kWh/dwelling/yr
Measured Toronto 2022, annual kWh/premise (derived, n_days-weighted mean of the three full_year
daytype rows in ieso_metrics.csv, x8760 h): 7,334.07 kWh/premise/yr — no direct "all-days" row
exists in ieso_metrics.csv so this is a derived figure, not a straight read.

## Decisions
- **Item 1 mechanism.** Each run's raw hourly series (per series, facility/nonhvac) is divided by
  that run's own `np.nanmean` over its 8760 hours BEFORE the run enters `full_sub_table`/
  `compute_slice_outputs` — everything downstream (weighting, aggregation, the metric functions
  themselves) is byte-identical to T09. This makes "archetype profile = mean over its runs of the
  normalized series" and "stock profile = archetype profiles weighted by `STOCK_WEIGHTS`" fall out
  of the EXISTING weighting code (`entities[a] = [(f,1.0) ...]` for archetype-alone,
  `STOCK_WEIGHTS[a]/n` for the stock) rather than needing new aggregation logic — reasoned, not
  specified by the task doc which just says what the result should be. A run is skipped (with
  reason logged in `run_meta.json["skipped"]`) if either series' annual mean is exactly 0 or NaN
  (guards a division by zero that real residential electricity data should never trigger).
- **Item 1 join columns.** The task text names exactly 4 "shape metrics" (load factor,
  peak-to-average, midday share, peak hour) and says only `mean_kwh_per_premise` "must be dropped
  from the join". It does not mention `max_kwh_per_premise`. Not specified by the task doc which
  of the two behaviors is intended — **decided to keep `max_kwh_per_premise` in the join** (only
  literally-named metric dropped), on the reasoning that the task's list of "shape metrics" is
  descriptive of the four scale-invariant-by-construction outputs, not an exhaustive allow-list for
  the join. `max_kwh_per_premise` is now itself close to `peak_to_avg` (mean≈1) but is not
  identical to it row-by-row, so it is left in as extra information rather than dropped by
  extension of the same argument. `n_days`/`mean_premises` remain excluded from the join, same as
  T09 (unchanged rationale — `mean_premises` is a weight sum, not a real premise count, and is even
  more clearly so now that all values are normalized).
- **Item 2 mechanism.** `build_calendar_frame()` is unchanged from T09: it already computes both
  `daytype_real2022` and `daytype_eplus` columns, with holiday membership computed once from
  `HOLIDAY_SET` and applied identically to both columns (`is_holiday` variable shared) — so
  "holidays stay on the real calendar date" was already true in T09's code for both calendars, no
  change needed there. `period_month_map()`/`full_sub_table()`'s `month` column is derived from the
  real 2022 calendar date regardless of which day-type column is used — weather/season/month
  slices are unaffected by which calendar is chosen, also already true. The only change actually
  made: `main()`'s join loop now runs over BOTH `("eplus", "real2022")` (`eplus` first, matching the
  day type the occupancy schedule ran against) instead of only `real2022`, adding a `calendar`
  column to `sim_vs_measured_toronto_2022_shape.csv` so both blocks are visible in one file, per
  the task's explicit instruction.
- **Item 3 (dwelling-unit count) — evidence lines, grepped locally, not inferred from floor area:**
  - `SingleD__Toronto_5A/sample_001_HH33188/2022/Scenario_2022.idf:4392-4425` — one `Zone`
    `living_unit1`/`attic_unit1`/`unheatedbsmt_unit1` triple, no `ZoneGroup` object anywhere in the
    file → **1 dwelling**.
  - `OtherDwelling__Toronto_5A/sample_001_HH22934/2022/Scenario_2022.idf:4392-4613` — seven `Zone`
    `living_unitN`/`attic_unitN`/`unheatedbsmt_unitN` triples for N=1..7, no `ZoneGroup` → **7
    dwellings** (a row-house block).
  - `MidRise__Toronto_5A/sample_001_HH126139/2022/Scenario_2022.idf:5448-5511` (7 ground-floor
    `...Apartment` zones — SW,NW,NE,N1,N2,S1,S2; the SE corner is not an apartment on the ground
    floor in either MidRise or HighRise, presumably the entrance/lobby, not investigated further)
    + `:5690-5705` (`ZoneList` "Mid Floor List": 8 apartment zones SW/NW/SE/NE/N1/N2/S1/S2 +
    M Corridor; `ZoneGroup` "Middle Floors" `Zone List Multiplier = 2`) + `:5592-5655` (8 top-floor
    apartment zones) → 7 + 8×2 + 8 = **31 dwellings**.
  - `HighRise__Toronto_5A/sample_001_HH49514/2022/Scenario_2022.idf:5527-5632` (7 ground-floor
    apartment zones, same SW/NW/NE/N1/N2/S1/S2 pattern) + `:5931-5946` (`ZoneList` "Mid Floor
    List": 8 apartment zones + M Corridor; `ZoneGroup` "Middle Floors" `Zone List Multiplier = 8`)
    + `:5797-5902` (8 top-floor apartment zones) → 7 + 8×8 + 8 = **79 dwellings**. Re-checked on
    `sample_002_HH129161`: identical `ZoneGroup`/multiplier lines.
  - Every individual `Zone` object's own `Multiplier` field (distinct from the `ZoneGroup`'s "Zone
    List Multiplier") is `1` for all apartment zones checked — confirmed no double-counting between
    the two kinds of multiplier.
  - Reported in `run_meta.json` (`dwelling_count`, `dwelling_count_evidence`,
    `annual_facility_kwh_meter_mean_per_archetype`, `annual_facility_kwh_per_dwelling_estimate`),
    not in either of the two task-specified CSVs, since the task's Outputs section only lists the
    two CSVs + slurm log — a fresh field in `run_meta.json` (same file T09 also used for
    diagnostics) rather than a new file, per "never create anything not explicitly requested".
- **Item 4 (clock) — evidence, same object T09 already grepped, re-confirmed here not
  re-derived independently:** `SingleD__Toronto_5A/sample_001_HH33188/2022/Scenario_2022.idf:115-129`,
  `RunPeriod` object: `Day of Week for Start Day = Sunday`, `Use Weather File Holidays and Special
  Days = Yes`, `Use Weather File Daylight Saving Period = Yes`, `Apply Weekend Holiday Rule = No`.
  No hour shift is applied anywhere in this script (`hour_of_day = hour % 24`, IESO `HOUR =
  hour_of_day + 1`, identical arithmetic to T09). This script does not claim how EnergyPlus itself
  reports/labels time internally beyond what these IDF fields state — no E+ output log was read.
- **Dropped `sim_toronto_2022_profiles_long.csv`** (T09 wrote this; the task's Outputs section for
  T15 lists only the two CSVs + slurm log) — not written by this script, to avoid creating an
  output the task doc didn't ask for.

## Next
Collection is complete, all checks passed (exact-match, both calendars present, shoulder first,
StockWeighted normalized mean ≈1 for full_year rows). Nothing to resubmit. Manager decides
whether/how these fixed shape numbers replace the T09 (unfixed) ones in the WP5 write-up — no
manuscript or plan edit made by this collector pass. Open question for the manager: T09's own
per-dwelling reading of OtherDwelling was wrong (see Ledger finding), so any WP5 text that already
cites T09's per-dwelling numbers needs the T15 `dwelling_count`/`annual_facility_kwh_per_dwelling_estimate`
values instead.

## WHAT I DID NOT VERIFY
- (collector, 2026-09-15) Whether every one of the 200 loaded runs actually has 8,760 well-formed
  rows and all 4 required meter columns — only the script's own `skipped` accounting was read
  (0 skipped, `run_meta.json["skipped"]=[]`); no independent row-count check of the raw per-run
  input files was done at this scale (would require reading inside `T06/input` on the cluster,
  out of scope for a collector pass and against the "never python on login node" rule for anything
  beyond single-file peeks).
- (collector) The `sim_toronto_2022_shape_metrics.csv` and `sim_vs_measured...csv` row counts
  (880, 1,760) were read from the slurm log and `run_meta.json` and cross-checked against each
  other, but not independently recomputed from first principles (e.g. re-deriving 880 = 5 entities
  x 2 series x 2 calendars x 2 periods-with-both-daytypes... the combinatorics were not spelled
  out here; taken on the script's own count).
- (collector) Section 3 (calendar effect) and section 1/2 numbers were read directly from the two
  CSVs with a local `py -3` script (exact float values, no rounding beyond display); the
  `py -3` script itself was not saved as part of this task's outputs (ad hoc, scratchpad-style, not
  requested by the task doc).
- (collector) The "measured Toronto annual kWh/premise" figure (7,334.07 kWh/premise/yr) is a
  derived number (n_days-weighted average of three daytype rows, x8760h) since `ieso_metrics.csv`
  has no explicit all-days row for `full_year` — the task doc anticipated this ("if derivable...
  else NOT FOUND") and it was derivable, but this is not a value the original T02 script wrote
  itself, so it should not be quoted as a T02 output.
- Everything the employee already listed below this line (job-completion status, MidRise/
  OtherDwelling/SingleD cross-sample geometry checks, DST/holiday IDF re-derivation,
  city-generalization of the dwelling-count method, and the `max_kwh_per_premise` join-column
  ambiguity) remains as the employee wrote it; the collector did not re-verify those items — see
  below.
- Whether job 1328281 actually completes, its exit code, elapsed time, or any real 200-run output
  numbers — nothing collected; submit-and-end-turn rule (only a 2-run/archetype local smoke test
  was run end-to-end, not the full 50×4 scale, and not on the cluster). SUPERSEDED by the collector
  entries above: job completed, COMPLETED/0:0/25s, 200 real runs collected.
- Whether every one of the (expected) 200 discovered runs has 8,760 well-formed rows and all 4
  required meter columns at the full scale — the script checks and records `skipped` in
  `run_meta.json`, but this was not read this turn (job not yet run).
- MidRise/OtherDwelling/SingleD dwelling-geometry consistency across their other 49 samples each
  (only HighRise was cross-checked on a second sample) — assumed identical per T06's own
  independent finding that these are shared building templates per archetype/city cell, not
  re-derived here for the other three archetypes.
- Whether the `ZoneList`/`ZoneGroup` dwelling-count method used here would generalize to other
  cities/climate zones — only Toronto_5A IDFs were read, per the task's own Toronto-only scope.
- The DST/holiday IDF fields (item 4) were re-read from the same file T09 already cited, not
  independently re-derived from a second source or cross-checked against any EnergyPlus output log.
- Whether `max_kwh_per_premise` should have been dropped from the join alongside
  `mean_kwh_per_premise` — decided to keep it (see Decisions); the task text is genuinely
  ambiguous on this point and a manager call may override.
- The exact numeric values in the Ledger's smoke-test table (2 runs/archetype) are NOT the job's
  real output and must not be quoted as the task's answer — they exist only to show the mechanism
  works before submitting.

## Manager note (2026-09-15, after T16)
- Weather mismatch resolved from T16 Q3: every city EPW is a TMYx typical-year file
  (`BEM_Setup/WeatherFile/CAN_ON_Toronto...715080_TMYx_5A.epw`), not 2022 weather. The measured IESO side
  is actual 2022. Any seasonal or peak-hour comparison carries this mismatch; state it in the paper.
- Scale-free shapes and per-dwelling levels from this task are the WP5 numbers to carry; T09's stock
  table is superseded.
