# T02 — WP5 step 3a: measured Ontario residential hourly profiles (IESO) — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP5, §8 audit, §10
Status:     DONE — 1328239 FAILED (exit 1:0); fixed v2 resubmitted as 1328255, COMPLETED exit 0:0, outputs verified (see Ledger)

## Task

**Why.** Reviewers asked for a check of our simulated hourly load shape against measured residential
electricity. The Ontario system operator (IESO) publishes open hourly residential consumption by
postal area: `https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/`. A previous agent looked
at January only, with the wrong midday window. **Do not reuse its numbers.** Build the measured side
properly.

**Steps.**
1. Read our metric definitions in the code: load factor, midday share (which hours exactly), peak
   hour, peak-to-average ratio, evening ramp if present. Start with `grep -n` for `midday`,
   `load_factor`, `peak` in `2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py` and
   `Step8_docs/interim_report_gen.py`. Record each definition with `file:line`, and whether our
   EnergyPlus hourly timestamps are hour-ending.
2. Open the IESO directory listing (small fetch is fine locally) and one file header. Record the file
   naming, versions (`_v1`, `_v2`: always take the highest version per month), columns, whether
   `HOUR` is 1–24 hour-ending, the customer types present, and the licence/terms link if shown.
3. Write one script in `T02_scripts/` that, run **on Speed** (compute nodes have outbound network),
   downloads every month of **2019, 2021, 2022, 2023** (add 2020 for completeness), keeps
   `CUSTOMER_TYPE == Residential`, and for each hour sums `TOTAL_CONSUMPTION` and `PREMISE_COUNT`
   over FSAs to get kWh per premise. Scopes: **Ontario (all FSAs)** and **Toronto (FSAs starting
   with `M`)**. Day types: weekday, weekend; Ontario statutory holidays go to a separate "holiday"
   class (list the dates used). Periods: each month, winter (Dec–Feb), shoulder (Apr–May, Sep–Oct),
   summer (Jun–Aug), full year.
4. For each scope × year × period × day type: the mean 24-hour profile (kWh per premise), the
   normalized profile (sums to 1), and every metric from step 1 using **our** definitions. Also the
   2019 → 2022 change for each metric.
5. Outputs: `ieso_profiles_long.csv` (scope, year, period, daytype, hour_ending, kwh_per_premise,
   share, n_days, mean_premises), `ieso_metrics.csv`, `ieso_manifest.csv` (file name, version, bytes,
   SHA-256, rows kept). Keep raw zips on Speed only.
6. Submit with `sbatch -p ps -c 32 --mem=64G -t 7-00:00:00` from `/speed-scratch/o_iseri/2J_revision/T02/`.
   Write the JobID in the Ledger. **End your turn.**

**Known limits to record, not fix.** The measured data includes air conditioning and electric
heating; our simulated electricity meter does not include heating or cooling (those are thermal
meters). Shoulder months are therefore the fairest comparison. No dwelling-type or heating-fuel split
exists in this dataset. Premises may include some non-households classed as residential: check the
IESO notes and record what they say.

**Employee rules.** Plan §10 rules 1–6 apply. Python on Speed:
`/speed-scratch/o_iseri/envs/step4/bin/python` (check `pandas` imports at job start).

## Ledger
- 2026-09-15 · JobID **1328239** · partition `ps`, `-c 32 --mem=64G -t 7-00:00:00`, name `T02_ieso` ·
  submitted from `/speed-scratch/o_iseri/2J_revision/T02/` · script
  `/speed-scratch/o_iseri/2J_revision/T02/impl_scripts/ieso_wp5_build.py` (local copy:
  `impl/T02_scripts/ieso_wp5_build.py`) · state at submission: **PENDING** (`sacct -j 1328239 -X`
  confirmed the job exists, account `chachemv`, 0 CPUs allocated yet) · stdout/err:
  `/speed-scratch/o_iseri/2J_revision/T02/out/T02_ieso_1328239.out` · no exit code yet.
- Runs entirely on the compute node (downloads IESO zips itself via `urllib`, no login-node fetch of
  the full data). Outputs on Speed: `T02/out/ieso_profiles_long.csv`, `T02/out/ieso_metrics.csv`,
  `T02/out/ieso_manifest.csv`. Raw zips kept in `T02/raw/` on Speed only, not copied here.
- 2026-09-15 (collector) · JobID **1328239** → **FAILED**, exit code `1:0`, elapsed `00:06:20`
  (`sacct -j 1328239 --format=JobID,State,Elapsed,ExitCode,MaxRSS`; `.bat+` step MaxRSS 6,226,084K).
  No manifest/profile/metric CSVs were ever written (the manifest write happens only after the full
  year×month download loop completes in `main()`, and the job died mid-loop) — `T02/out/` on Speed
  holds only the log file. Log copied to `impl/T02_out/T02_ieso_1328239.out`; the one raw zip needed
  to diagnose the failure copied to `impl/T02_out/PUB_HourlyConsumptionByFSA_202308_v1.zip`.
- 2026-09-15 (manager) · JobID **1328255** · supersedes 1328239 · manager reviewed the v1→v2 diff
  (header located by `FSA,DATE,HOUR` prefix; corrupt zip re-downloaded once; no metric/column/scope
  change) and approved · scp'd `ieso_wp5_build_v2.py` to `T02/impl_scripts/` · `sbatch -p ps -c 4
  --mem=16G -t 7-00:00:00 --job-name=T02_ieso_v2 --chdir=/speed-scratch/o_iseri/2J_revision/T02
  --output=.../T02/out/T02_ieso_v2_%j.out --wrap=".../envs/step4/bin/python .../impl_scripts/ieso_wp5_build_v2.py"`
  · **RUNNING** at 00:00:13 on 4 CPUs · outputs expected in `T02/out/`.
- 2026-09-15 (collector) · JobID **1328255** → **COMPLETED**, exit code `0:0`, elapsed `00:04:59`, 4
  CPUs (`sacct -j 1328255 --format=JobID,State,Elapsed,ExitCode,MaxRSS,NCPUS`; `.bat+` MaxRSS
  8,100,776K). Log (`T02_ieso_v2_1328255.out`) has **no `[warn]` lines** and ends `[done] total wall
  time 295s`; `[manifest] wrote ... (60 rows)`, `[out] wrote ieso_profiles_long.csv (10560 rows)`,
  `[out] wrote ieso_metrics.csv (528 rows)`. scp'd (`ls -la` sizes checked first on Speed, nothing
  over 200 MB) to `impl/T02_out/`: `ieso_manifest.csv` (8,153 B), `ieso_metrics.csv` (84,820 B),
  `ieso_profiles_long.csv` (940,897 B), `T02_ieso_v2_1328255.out` (645 B); local sizes match Speed
  exactly.

## Verified
- **Step 1 — our metric definitions** (`2J_docs_occ_nTemp/Step8_docs/08_simulation_plots.py`):
  - `MIDDAY = (9, 17)` at `08_simulation_plots.py:114`, comment "WFH window (09:00-17:00)"; used as
    `fac[:, MIDDAY[0]:MIDDAY[1]]`, a 0-indexed array slice → indices 9-16 (8 hours), at
    `08_simulation_plots.py:387`.
  - `load_factor = mean24/max24` at `08_simulation_plots.py:385`, where `mean24 = fac.mean()`
    (mean of every hourly instance in the slice, not of an averaged 24h profile) and
    `max24 = flat.max()` (single largest instance) — both at `08_simulation_plots.py:383-384`.
  - `peak_to_avg = max24/mean24` at `08_simulation_plots.py:386` (reciprocal of load_factor).
  - `midday_share = fac[:, MIDDAY[0]:MIDDAY[1]].sum()/fac.sum()` at `08_simulation_plots.py:387`
    — sum of midday-window instances over sum of all instances, same "all instances" basis as
    load_factor.
  - `mean_peak_hour`: per-day peak hour = `fac.argmax(axis=1)` (`08_simulation_plots.py:370`), then
    the circular (sin/cos, wraps at 24h) mean of those per-day peak hours via `_circular_mean_hour`
    (`08_simulation_plots.py:278-285`), applied at `08_simulation_plots.py:372`.
  - **Hour convention (inferred, not found as an explicit code comment in this repo):** the array
    index `i` (0-23) lines up with IESO's `HOUR` field (1-24, hour-ending) as `HOUR = i + 1`. Basis:
    MIDDAY array-index slice 9:16 only reproduces the stated real-clock window "09:00-17:00" under
    that mapping (indices 9-16 → HOUR-ending 10-17 → clock intervals 09:00-10:00 through
    16:00-17:00). This is the correction to the plan's own note (`00_REVISION_PLAN.md:534-536`) that
    the prior discarded run used the wrong window (hour-ending 10-16, 7 hours, not our definition).
    EnergyPlus's own hour-ending convention for hourly reports is standard behaviour, not something
    this repo's code comments state outright — flagged as inferred, see WHAT I DID NOT VERIFY.
- **Step 2 — IESO source** (local inspection only, per hard rules): directory listing at
  `https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/` fetched with `curl`. All months
  2019-01 through 2023-12 present, filename pattern
  `PUB_HourlyConsumptionByFSA_YYYYMM_v1.zip`; **no `_v2` or higher found for any 2019-2023 month** —
  script still probes for higher versions per the task's "always take the highest version" rule.
  Downloaded and inspected one file (`PUB_HourlyConsumptionByFSA_202207_v1.zip`, 11,972,098 bytes,
  extracts to a 59,988,025-byte CSV). Header: 3 comment lines (`\\...`) then columns
  `FSA,DATE,HOUR,CUSTOMER_TYPE,PRICE_PLAN,TOTAL_CONSUMPTION,PREMISE_COUNT`. `HOUR` runs 1-24 for one
  FSA/date checked (`L5K`, 2022-07-01) — hour-ending confirmed to start at 1, consistent with the
  task doc's own claim. `CUSTOMER_TYPE` values found in this file (full-file scan, local, I/O only):
  `Residential`, `SGS <50kW`. Multiple `PRICE_PLAN` rows exist per `FSA,DATE,HOUR` (e.g. `Tiered`,
  `TOU`, `Retailer`) — the script sums `TOTAL_CONSUMPTION` and `PREMISE_COUNT` across these when it
  groups by `FSA,DATE,HOUR`, since premises fall under one plan at a time (disjoint subsets). No
  licence/terms/readme file found in the directory listing — see WHAT I DID NOT VERIFY.

- **Step 3 collector — cause of the 1328239 failure** (`out/T02_ieso_1328239.out` tail, confirmed by
  scp'ing the exact raw zip and re-parsing it locally with `zipfile`+`pandas`): the job downloaded
  55 months cleanly (2019-01 .. 2023-07, in `[dl]` log order) then died on 2023-08 inside
  `load_month_df` (`impl/T02_scripts/ieso_wp5_build.py:154`, `pd.read_csv(fh, skiprows=3,
  usecols=USECOLS, ...)`) with `ValueError: Usecols do not match columns, columns expected but not
  found: ['FSA', 'TOTAL_CONSUMPTION', 'DATE', 'PREMISE_COUNT', 'CUSTOMER_TYPE', 'HOUR']`. Reading
  the actual downloaded bytes for `PUB_HourlyConsumptionByFSA_202308_v1.zip` line-by-line shows the
  extracted CSV's first four lines are an application-error banner, not the usual 3 IESO `\\...`
  comment lines: `b'ERROR:\n'`, `b'ORA-28002: the password will expire within 30 days\n'`, two blank
  lines — the real `\\Hourly Consumption...` / `\\Created at...` / `\\For 2023-08` comments and the
  true header (`FSA,DATE,HOUR,CUSTOMER_TYPE,PRICE_PLAN,TOTAL_CONSUMPTION,PREMISE_COUNT`) only start
  at line index 7, not 3. This is an intermittent server-side fault on the IESO reports host (looks
  like an Oracle DB/APEX error page prepended to one HTTP response body) — every other month in the
  same run parsed fine with the hardcoded `skiprows=3`, so it is not a permanent schema change and
  not something to "fix" by changing the data source or column definitions.
- **Fix — small and obvious, written, not submitted:**
  `impl/T02_scripts/ieso_wp5_build_v2.py` (new file, original left untouched). Only `load_month_df`
  changed: it now locates the real header row per file by scanning decoded text for a line starting
  `"FSA,DATE,HOUR"` (`_locate_header_skiprows`, new helper) instead of assuming a fixed `skiprows=3`,
  and if no such line is found in a cached-or-freshly-downloaded zip it deletes that zip and
  retries the download once before raising loudly — this also repairs the corrupt 202308 v1 zip
  already left in `T02/raw/` on Speed, which v1's unconditional cache-reuse branch would otherwise
  keep serving on any resubmit. No change to metric definitions, `USECOLS`, scopes, periods, holiday
  list, or output files. Verified locally (this machine has `pandas 2.3.3`): `py -m py_compile
  ieso_wp5_build_v2.py` exits 0; re-running `_extract_csv_bytes` + `_locate_header_skiprows` +
  `pd.read_csv` against the scp'd `PUB_HourlyConsumptionByFSA_202308_v1.zip` locates the header at
  line 7 and parses 1,386,597 rows with the expected 6 columns and `CUSTOMER_TYPE` values
  `{'Residential', 'SGS <50kW'}` — matches the Step-2 inspection of the 202207 file in this same doc.
  **Resubmit command (manager decides; not run here):** first `scp` the new script to Speed —
  `scp impl/T02_scripts/ieso_wp5_build_v2.py
  o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/2J_revision/T02/impl_scripts/` — then, from
  `/speed-scratch/o_iseri/2J_revision/T02/`:
  `sbatch -p ps -c 4 --mem=16G -t 7-00:00:00 --job-name=T02_ieso_v2
  --chdir=/speed-scratch/o_iseri/2J_revision/T02
  --output=/speed-scratch/o_iseri/2J_revision/T02/out/T02_ieso_v2_%j.out
  --wrap="/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T02/impl_scripts/ieso_wp5_build_v2.py"`
  (resource sizing per collector-task instructions, smaller than the original job's `-c 32
  --mem=64G` — v2 does the same work, so if 4 CPUs / 16G proves too slow or tight, that is a resize
  decision for the manager, not something diagnosed here).

- **Step 3 collector — v2 run outcome, verified from the real outputs:** `ieso_manifest.csv` has 60
  data rows (5 years x 12 months), **all `status == OK`**, no row with `status != OK`
  (`awk -F, 'NR>1 && $8!="OK"' ieso_manifest.csv` → empty). 2023-08 `rows_kept = 861,656`, in line
  with the neighbouring months (2023-07 = 859,526; 2023-09 = 818,453) — the server-error banner that
  killed 1328239 did not reduce the row count once parsed correctly. The v2 log shows no `[dl]` line
  for 2023-08 in this run (only 2023-09 through 2023-12 were freshly downloaded), and the manifest's
  `bytes` for 2023-08 (12,968,087) matches the corrupt cached zip already on Speed exactly — so v2
  reused that same cached file and located the real header at line 7 without needing to delete/retry
  the download, confirming the fix works in production, not just in the local unit check.
- **Ontario/Toronto 2019 vs 2022, shoulder months (Apr-May, Sep-Oct), weekdays only** (from
  `ieso_metrics.csv`, `awk -F, '($1=="Ontario"||$1=="Toronto") && $3=="shoulder" && $4=="weekday"'`):
  - Ontario: mean 0.786 -> 0.838 kWh/premise (+0.052, the printed `2019_to_2022_delta` row), load
    factor 0.570 -> 0.455 (-0.115), peak-to-average 1.755 -> 2.200 (+0.445), midday share 0.335 ->
    0.350 (+0.015), mean peak hour (array-index basis, see below) 18.91 -> 18.42 (-0.49).
  - Toronto: mean 0.657 -> 0.696 kWh/premise (+0.040), load factor 0.543 -> 0.430 (-0.113),
    peak-to-average 1.841 -> 2.323 (+0.482), midday share 0.332 -> 0.351 (+0.019), mean peak hour
    18.98 -> 18.69 (-0.29).
  - Same direction both scopes: mean consumption up, load factor down (peakier), peak-to-average up,
    midday share up slightly, peak hour shifted slightly earlier. Both n_days = 82 for 2022 (85 for
    2019 — one extra weekday in the 2019 Apr-May/Sep-Oct window, not investigated further).
- **Hour-ending question, resolved:** `T02_scripts/ieso_wp5_build_v2.py:20-22` documents that
  `mean_peak_hour` is reported on the **same 0-23 basis as our repo's array index** (`value = HOUR -
  1`; line 327: `hour_idx0 = (daily_peak_hour_idx["HOUR"].to_numpy() - 1)`), i.e. it is already
  directly comparable to the simulated `mean_peak_hour` from `08_simulation_plots.py` with **no
  relabel needed for the Ontario-vs-simulated comparison itself**. A `+1` conversion is only needed
  if a value is quoted in prose as a real clock hour-ending (e.g. Ontario 2019 shoulder weekday
  18.91 -> HOUR-ending ~19.9, i.e. the peak instant falls in the 19:00-20:00 interval).

## Decisions
- **Winter period = calendar-year Dec+Jan+Feb of the same `year`** (not the meteorological season
  spanning into the next calendar year), because the output is keyed by a single `year` column and
  this keeps every period self-contained within the years actually fetched (2019-2023). Mar and Nov
  are in no named season, matching the task spec literally (only 12 individual months + winter +
  shoulder + summer + full_year are built).
- **Holiday dates are fixed, hand-computed, not substitute-day-shifted**, except Canada Day, which
  moves to the following Monday when 1 July falls on a Saturday/Sunday (2023 only, in this range).
  New Year's Day, Family Day (3rd Mon Feb), Good Friday (Easter-2d), Victoria Day (Mon strictly
  before 25 May), Canada Day, Labour Day (1st Mon Sep), Thanksgiving (2nd Mon Oct), Christmas,
  Boxing Day — full list in `impl/T02_scripts/ieso_wp5_build.py` (`HOLIDAYS` dict). Civic Holiday
  (1st Mon Aug) excluded: it is not a province-wide Ontario statutory holiday.
  Christmas/Boxing Day use the literal calendar date even when that falls on a weekend (no
  substitute-day rule applied), to keep the "holiday" class tied to actual household behaviour on
  25/26 Dec rather than a legal-observance date.
- **2019→2022 change**: appended as extra rows in `ieso_metrics.csv` with `year =
  "2019_to_2022_delta"`, value = 2022 metric − 2019 metric, per (scope, period, daytype). Not a
  separate file — the task listed only 3 output files.
- **kWh-per-premise construction**: for each (scope, calendar date, HOUR) instance, sum
  `TOTAL_CONSUMPTION` and `PREMISE_COUNT` over the scope's FSAs first, then divide — this is the
  task's own step-3 wording. The mean 24h profile then averages that per-instance ratio across the
  days in the period/daytype slice (not a ratio-of-sums across days).

## Next
**2026-09-15 (collector):** All requested checks done — job COMPLETED clean, no `[warn]`, no
manifest row with `status != OK`, 2023-08 row count in line with neighbours, Ontario/Toronto 2019 vs
2022 shoulder-weekday metrics pulled, hour-ending convention confirmed (no relabel needed for the
comparison; +1 only if quoting a real clock hour in prose). Outputs are on disk at `impl/T02_out/`
(`ieso_manifest.csv`, `ieso_metrics.csv`, `ieso_profiles_long.csv`, plus both `.out` logs). **Manager
decision needed:** whether/how these Ontario+Toronto measured shoulder-weekday numbers (and the full
`ieso_metrics.csv`, which also has winter/summer/full-year and holiday day types not pulled here) go
into the WP5 write-up, and whether the simulated-vs-measured comparison script/plot is a separate
task.

## WHAT I DID NOT VERIFY
- Whether EnergyPlus's hourly `Facility` meter output is truly hour-ending is **not confirmed by any
  code comment found in this repo** — inferred only from the MIDDAY window matching real clock time
  under that assumption (see Verified). If wrong, `midday_share` and the HOUR↔array-index mapping in
  the build script would need a 1-hour shift.
- No IESO licence/terms-of-use link was found in the directory listing itself — did not search
  IESO's wider site for it (out of scope for "one file header" inspection).
- Whether IESO's own notes (elsewhere on ieso.ca, not in this directory) say anything about
  non-household premises classed as Residential — not checked; flagged in the task as a known limit,
  not resolved here.
- `dr_2J-07`-style unread claims are not used anywhere in this doc.
- 2026-09-15 (collector): only **shoulder x weekday** metrics for Ontario/Toronto 2019/2022 were
  pulled into Verified — winter, summer, full_year, individual months, and the weekend/holiday day
  types in `ieso_metrics.csv` (528 rows total) were not read or checked here.
- `ieso_profiles_long.csv` (10,560 rows: mean and normalized 24h profiles) was not opened — only its
  row count and byte size were confirmed via the log and `ls -la`; the `share` column summing to 1
  per profile was not independently re-checked.
- The 2019 vs 2022 `n_days` mismatch noted above (85 vs 82 weekdays in the shoulder window) was
  observed but not investigated — not checked whether it is a calendar fact (2019/2022 weekday counts
  for Apr-May+Sep-Oct genuinely differ) or a holiday-classification edge case.
- IESO licence/terms link and the non-household-premises question (flagged in the task's "known
  limits") remain unresolved from the earlier entry — not re-checked this turn.
- Did not open or diff `08_simulation_plots.py` against the build script a second time; relied on the
  Step-1 entry already in this doc plus the script's own header comment (`ieso_wp5_build_v2.py:13-22`)
  for the hour-ending reasoning.
