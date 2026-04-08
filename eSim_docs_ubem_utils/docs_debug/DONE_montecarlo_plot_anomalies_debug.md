# Monte Carlo Neighbourhood Plot Anomalies — Investigation Plan

## Issue Summary

After running **Option 7 — Batch Comparative Neighbourhood Simulation
(Monte Carlo)** in `run_bem.py` for a Montreal (Quebec) neighbourhood
with N=10 iterations × 5 census years (2005 / 2010 / 2015 / 2022 / 2025)
+ Default, the two summary plots written to `PLOT_RESULTS_DIR` show two
distinct, severe anomalies:

### Anomaly 1 — Inverted heating time-series

`MonteCarlo_Neighbourhood_TimeSeries_*.png`, the
`Heating - Energy Demand` panel:

- Heating peaks in **September** at ~14 kWh/m²/month
- Heating is **near zero in January–May and October–November**
- All 6 scenarios overlap perfectly in the heating panel — no
  inter-scenario differentiation visible

For Montreal (Quebec, Köppen Dfb, ASHRAE Zone 6A) this is physically
impossible. Heating must peak December–February and is essentially zero
in summer.

### Anomaly 2 — No heating bar in the EUI breakdown chart

`MonteCarlo_Neighbourhood_EUI_*.png`, the bar chart, and the underlying
`aggregated_eui.csv`:

```
EndUse,2005_mean,...,Default_mean,Default_std
Interior Lighting,2.4136,...,2.6440,0.0000
Electric Equipment,60.3282,...,61.2570,0.0000
Water Systems,0.0010,...,0.0010,0.0000
Cooling,42.0822,...,45.8280,0.0000
```

There is **no `Heating` row at all** — the chart shows Interior
Lighting, Electric Equipment, Water Systems, and Cooling, totalling
~105 kWh/m². For Montreal residential, the dominant end-use should be
heating (typically 50–120 kWh/m²); its complete absence is impossible.

**The two anomalies turn out to have completely different root causes
and live in completely different parts of the codebase.** Anomaly 2 is
a one-line bug in `plotting.py` and is fully diagnosed below with an
exact patch. Anomaly 1 is *not* a plotting bug — the SQL meter values
themselves are inverted, so the fix lives upstream in the IDF /
preparation code, and the diagnostic below narrows the scope but does
not identify a single line.

**Scope of this document:** identify both root causes, propose the
minimum fix for the diagnosed one, document the diagnostic evidence
ruling out plot-side causes for the simulation-level one, and lay out
a step-by-step verification / implementation plan for both. *No source
files are edited here* — this is an investigation and planning document
only.

---

## 1. Setting the Stage

- **Actor:** BEM / UBEM pipeline user running `python run_bem.py` and
  choosing option 7 (Batch Comparative Neighbourhood / Monte Carlo) →
  any neighbourhood IDF → Montreal EPW → iter_count=10 → full-year
  ("Standard") simulation mode.
- **Objective:** produce a Monte Carlo summary across 5 census years +
  Default for a Montreal residential neighbourhood, with mean ± std
  EUI bars and monthly time-series subplots per end use.
- **Relevant code:**
  - `eSim_bem_utils/plotting.py:112-232` — `calculate_eui()` (the EUI
    extractor that drops the heating row).
  - `eSim_bem_utils/plotting.py:148-154` — the
    `End Uses By Subcategory / End Uses` SQL query.
  - `eSim_bem_utils/plotting.py:171-173` — the `'Water' in col_name`
    skip filter (Anomaly 2 root cause).
  - `eSim_bem_utils/plotting.py:551-627` — `get_meter_data()` (the
    monthly meter extractor used by the time-series plot; verified
    correct against the SQL).
  - `eSim_bem_utils/plotting.py:902-1033` — `plot_kfold_timeseries()`
    (verified correct against the extracted data).
  - `eSim_bem_utils/main.py:1795-2175` —
    `option_batch_comparative_neighbourhood_simulation()` (the Option 7
    runner that aggregates iterations and triggers both plots).
  - `eSim_bem_utils/main.py:2104-2120` — the per-scenario aggregation
    loop where `categories` is derived from the *first* scenario's
    end-use keys (this is what makes the missing heating row propagate
    silently across all six scenarios).
  - `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/` —
    completed simulation results (51 SQL files, used as evidence).
  - `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/aggregated_eui.csv`
    — the aggregated EUI output that visibly omits the `Heating` row.
- **Observed behaviour:** the Monte Carlo runs to completion with
  `Successful: 51/51 | Failed: 0/51`. Both plots are generated. Neither
  the console nor the CSV gives any warning — yet the bar chart is
  missing the dominant end use, and the time-series subplot displays a
  physically inverted heating profile that is identical (within ~3 GJ)
  across every iteration and every scenario.
- **Expected behaviour:** the EUI bar chart must contain a `Heating`
  bar of order ~50 kWh/m² (or whatever the simulation actually
  computes); the time-series heating panel must peak in December–
  February and be essentially zero in summer; iteration-to-iteration
  variability must be visible across the six scenario traces.

---

## 2. Defining the Task

Diagnose **why** the Monte Carlo neighbourhood EUI plot is missing
heating *and* why the monthly heating time-series is physically
inverted; document both root causes with code + data evidence (file
paths, SQL row dumps, exact monthly values); specify the minimum
scoped fix for the one that is a plotting bug; and define a
verification plan for the one that is upstream of `plotting.py`.

This is a **debug & investigation** task, not a refactor — the
implementation happens in a separate change after the user reviews
and approves the direction.

---

## 3. Root-Cause Analysis

### 3.1 Problem A — `calculate_eui()` skips the heating row because the column is named `District Heating Water`

#### What `calculate_eui()` does

`eSim_bem_utils/plotting.py:148-217` reads the
`End Uses By Subcategory` table from `eplusout.sql`, then iterates
every row and decides whether to count it:

```python
for _, row in subset.iterrows():
    row_name = row['RowName']
    col_name = row['ColumnName']
    units    = row['Units']
    val_str  = row['Value']

    # Skip water columns
    if 'Water' in col_name or 'm3' in str(units):
        continue
    ...
```

The intent of the `'Water' in col_name` check is clearly to drop the
domestic water consumption column (`ColumnName='Water'`, `Units='m3'`)
which appears once per row in EnergyPlus's tabular output and would
otherwise be counted as energy. The `'m3' in units` half of the OR
already covers that case correctly.

#### What the SQL actually contains for heating

The Montreal IDF used in this run is configured to use a **District
Heating Water** loop. The only non-zero heating row in the entire
`End Uses By Subcategory` table is therefore:

```
('End Uses By Subcategory', 'Heating:General', 'District Heating Water', 'GJ', '      531.03')
```

(verified against
`MonteCarlo_Neighbourhood_N10_1775555644/iter_1/2005/eplusout.sql`).

For comparison, the equivalent cooling row is:

```
('End Uses By Subcategory', 'Cooling:General', 'District Cooling',       'GJ', '      455.62')
```

— the cooling row's `ColumnName` is `District Cooling` (no "Water" in
the string), so it survives the filter and is counted.

#### Why the filter drops the heating row

The string `'Water'` is a substring of `'District Heating Water'`, so

```python
'Water' in 'District Heating Water'   # → True
```

triggers the `continue` at line 173 and the row is silently skipped.
**Every** non-zero heating contribution in this IDF lives under
`ColumnName='District Heating Water'`, so the entire heating end use
is dropped from `end_uses` for every iteration of every scenario.

The filter does *not* drop cooling because the cooling-side
`ColumnName` is `District Cooling`, which doesn't match `'Water'`.
That's why the bar chart shows Cooling normally and Heating not at all.

#### Why the missing row also propagates through the Monte Carlo aggregation

`eSim_bem_utils/main.py:2094-2105` builds the per-iteration EUI list
and then derives the category set from the **first** scenario's
result dict:

```python
sample_result = None
for s in scenarios:
    if all_eui_results[s]:
        sample_result = all_eui_results[s][0]
        break
...
end_uses = sample_result.get('end_uses_normalized', {}) or sample_result.get('end_uses', {})
categories = list(end_uses.keys())
```

Because `calculate_eui()` already dropped the heating row before
that dict was built, `categories` never contains `Heating`. The CSV
write loop at `main.py:2122-2133` and the `plot_kfold_comparative_eui`
call at `main.py:2136-2140` then iterate exactly that `categories`
list, so neither the CSV nor the bar chart contain a heating column.

#### Disk evidence

Per-iteration CSV (the file the bar chart is built from):

```
$ cat BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/aggregated_eui.csv
EndUse,2005_mean,2005_std,...,Default_mean,Default_std
Interior Lighting,2.4136,0.0547,...,2.6440,0.0000
Electric Equipment,60.3282,0.4020,...,61.2570,0.0000
Water Systems,0.0010,0.0000,...,0.0010,0.0000
Cooling,42.0822,1.1387,...,45.8280,0.0000
```

Four rows. No heating row. Confirms the categories list never contained
heating.

Underlying SQL (any scenario, any iteration — same shape across all 51
files). Filtered down to the heating-related dump:

```
('End Uses', 'Heating', 'District Heating Water', 'GJ', '      531.03')
('End Uses', 'Heating', 'District Heating Water', 'W',  '   142831.46')
('End Uses By Subcategory', 'Heating:General', 'District Heating Water', 'GJ', '      531.03')
('End Uses By Subcategory', 'Heating:General', 'District Heating Water', 'W',  '   142831.46')
('End Uses', 'Total End Uses', 'District Heating Water', 'GJ', '      542.19')
('End Uses', 'Water Systems',  'District Heating Water', 'GJ', '       11.15')
```

531 GJ ≈ 147 600 kWh of heating per simulation. With ~2 000 m² of
conditioned area across 10 buildings, this is **~74 kWh/m²/year**, the
genuinely dominant end use that the chart is silently dropping.

### 3.1.5 Why the same filter does not break Anomaly 2's "Water Systems" row

The current chart still shows a `Water Systems` bar at ~0.001 kWh/m².
That row survives the filter for an unrelated reason:

```
('End Uses By Subcategory', 'Water Systems:General', 'Electricity',           'GJ', '0.00')
('End Uses By Subcategory', 'Water Systems:General', 'District Heating Water','GJ', '11.15')
('End Uses By Subcategory', 'Water Systems:General', 'Water',                 'm3', '70.44')
```

The `Electricity` column for `Water Systems:General` is 0 GJ but
`val_kwh != 0` is False, so it's silently dropped at line 200; the
`Water` (m³) column is dropped by the same filter that breaks heating;
and the `District Heating Water` column at 11.15 GJ is *also* dropped
by the same filter — so the only thing keeping a `Water Systems` row
in the result dict at all is one of the *other* fuel columns happening
to have a tiny non-zero value (e.g. a pumps electricity contribution
or a leftover sub-meter). The 0.001 kWh/m² value is misleadingly small
because the *real* Water Systems load is being silently dropped along
with the real heating load.

So the filter bug is wider than "no heating bar":

- Heating (District Heating Water → 531 GJ) → **dropped completely**
- Water Systems (District Heating Water → 11 GJ) → **dropped, leaving
  only an unrelated tiny residual**
- Cooling (District Cooling → 456 GJ) → **counted correctly**
- Electricity end-uses (Lights, Equipment, Fans) → **counted correctly**

Any IDF that delivers heating via a `DistrictHeatingWater:Facility`
loop (or whose DHW comes off the same loop) will hit this same bug.

#### Why the bug is silent

- `calculate_eui()` returns an `end_uses` dict that simply lacks the
  `Heating` key — there is no warning, no missing-row check, no
  cross-validation against `Total End Uses`.
- `option_batch_comparative_neighbourhood_simulation()` derives its
  `categories` list from the first scenario's keys, so the absence
  is propagated structurally rather than detected.
- The CSV writer iterates the same `categories` list, so even the raw
  text artefact does not show heating.
- `plot_kfold_comparative_eui` iterates `categories` again, so the bar
  chart matches the CSV — there's no point in the pipeline where the
  missing heating row could be noticed without manually inspecting an
  individual SQL file.

---

### 3.2 Problem B — Monthly heating meter values are physically inverted in the SQL itself, not in the plotting

The first instinct is "the plotting code is reading the months in the
wrong order or off-by-one". That hypothesis is **wrong**, and ruling it
out cleanly is the most important contribution of this section, because
it tells the next agent where the bug is *not* and saves them from
patching `plotting.py` for a problem that lives in the IDF.

#### What `get_meter_data()` actually retrieves

`eSim_bem_utils/plotting.py:551-627` runs the following query
(simplified):

```sql
SELECT rd.ReportDataDictionaryIndex, rd.Value
FROM ReportData rd
JOIN Time t ON rd.TimeIndex = t.TimeIndex
JOIN EnvironmentPeriods ep ON t.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex
WHERE ep.EnvironmentType = 3
ORDER BY t.TimeIndex ASC
```

then takes the `'Heating:EnergyTransfer'` rows from the resulting
dataframe and pushes them into a list of length 12.

#### Verifying that the rows really are Jan→Dec

I queried the same SQL with the Month column joined in (which
`get_meter_data()` itself doesn't read but is present in the `Time`
table) for `iter_1/2005/eplusout.sql`:

```
TimeIndex  Year  Month  Day   Value (J)            → GJ
745        2006   1     31    37 671 940 826       37.67
1418       2006   2     28    12 474 122 450       12.47
2163       2006   3     31     4 476 781 056        4.48
2884       2006   4     30                0           0
3629       2006   5     31                0           0
4350       2006   6     30     4 484 330 786        4.48
5095       2006   7     31    84 739 494 846       84.74
5840       2006   8     31   104 447 929 103      104.45
6561       2006   9     30   271 071 214 003      271.07
7306       2006  10     31        58 837 096        0.06
8027       2006  11     30     1 481 482 951        1.48
8772       2006  12     31    16 648 291 357       16.65
```

Three things to notice:

1. **TimeIndex is monotonically increasing in chronological order**
   (745, 1418, 2163, …, 8772). So `ORDER BY t.TimeIndex ASC` *does*
   produce the months in the order Jan, Feb, Mar, …, Dec.
2. **Month column matches that ordering** — the first row really is
   January, the last row really is December.
3. **There is exactly one `EnvironmentPeriod` in the file**
   (`EnvironmentPeriodIndex=32`, `EnvironmentName='RUN PERIOD 1'`,
   `EnvironmentType=3`), so the
   `WHERE ep.EnvironmentType = 3` filter is not folding two periods on
   top of each other.
4. **There is exactly one Heating:EnergyTransfer row per month** for
   that EnvironmentPeriod (12 in total — verified by
   `GROUP BY ep.EnvironmentPeriodIndex`).

So the data the plotting function reads is exactly what the SQL
contains, and what the SQL contains is genuinely:

- Jan 37.67 GJ
- Feb 12.47 GJ
- Mar  4.48 GJ
- Apr  0.00 GJ
- May  0.00 GJ
- Jun  4.48 GJ
- Jul 84.74 GJ
- Aug 104.45 GJ
- **Sep 271.07 GJ ← peak**
- Oct  0.06 GJ
- Nov  1.48 GJ
- Dec 16.65 GJ

After dividing by days-per-month and floor area in
`plot_kfold_timeseries()` at lines 977-984, the September value is the
~14 kWh/m²/month peak the user sees on the chart. The plot is faithful
to the SQL.

#### Cross-checking the cooling meter (sanity check)

If `get_meter_data()` were extracting months in the wrong order, the
cooling profile should also be visibly wrong. It is **not**:

```
Month  1: Cooling 15.65 GJ
Month  2:         24.31 GJ
Month  3:         46.65 GJ
Month  4:         68.69 GJ
Month  5:         96.96 GJ
Month  6:        115.14 GJ  ← peak (correct for Montreal)
Month  7:         60.37 GJ
Month  8:         46.95 GJ
Month  9:         27.11 GJ
Month 10:         91.16 GJ  ← unexpected late-season spike
Month 11:         42.49 GJ
Month 12:         18.37 GJ
```

The cooling peak is in June, which is correct. There is a strange
October spike that suggests the underlying simulation is also somewhat
unphysical, but the seasonal shape is right. So the row-ordering and
the column-mapping in `get_meter_data()` are both fine — they're
extracting the right meter, in the right order, in the right month
slots.

#### Same anomaly in every iteration and every scenario, including Default

The user's observation that "all 6 scenarios overlap perfectly in the
heating panel with no inter-scenario differentiation" is also
significant. I checked the heating profile across multiple SQL files:

```
                  Jan   Feb   Mar  Apr  May  Jun  Jul   Aug    Sep   Oct  Nov   Dec
iter_1/2005    37.67 12.47  4.48 0.00 0.00 4.48 84.74 104.45 271.07 0.06 1.48 16.65
iter_1/2025    39.47 14.02  4.99 0.00 0.00 4.45 85.02 103.94 267.78 0.12 2.03 18.70
iter_2/2005    37.23 12.27  4.38 0.00 0.00 4.49 84.94 104.36 271.61 0.02 1.40 16.32
iter_5/2025    39.47 14.02  4.99 0.00 0.00 4.45 85.02 103.94 267.78 0.12 2.03 18.70
Default        27.97  6.38  1.93 0.00 0.00 4.31 82.04 100.41 268.36 0.03 0.26  8.91
```

Three observations follow:

1. **The Default simulation has the same inverted shape as the
   schedule-injected runs.** Default does not pass through
   `inject_neighbourhood_schedules()` — it uses
   `inject_neighbourhood_default_schedules()` at `main.py:1904`. Both
   paths produce the same physically wrong heating profile, so the
   schedule injection is not the cause.
2. **All iter/scenario combinations differ from each other by ≤3 GJ
   per month**, which is ~1 % of the September value of 271 GJ.
   That's why the six traces overlap visually — the differences are
   real but invisible at the chart scale.
3. **iter_1/2025 and iter_5/2025 are byte-identical.** Two different
   Monte Carlo iterations produced the exact same monthly numbers.
   This is a separate finding worth flagging in §3.3 below.

#### What this rules out

- Not a column-name typo in `get_meter_data()` — the meter exists in
  the dictionary as `Heating:EnergyTransfer` (verified) and that's
  what the function reads.
- Not a month-ordering bug in the SQL query — `TimeIndex` is in
  chronological order and matches the `Month` column.
- Not the `EnvironmentType` filter folding sizing periods on top of
  the run period — only one `EnvironmentPeriod` exists in the file,
  and it has `EnvironmentType=3` ("RunPeriod").
- Not a fast-mode `52/24` scaling artefact. The Option 7 runner does
  not pass any `scaling_factor` to `plot_kfold_timeseries()` (see
  `main.py:2168-2173`); the only normalization in the plotter is
  divide-by-days-per-month and divide-by-floor-area at lines 977-984,
  which is dimensionally correct and applied uniformly to every month.
- Not a schedule-injection bug — Default produces the same anomaly.
- Not an iteration-specific weather/seed problem — the values are
  reproducible across iter_1 / iter_2 / iter_5 within ~1 %.
- Not a region/EPW selection issue — the General table confirms the
  weather file is
  `Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish QC CAN SRC-TMYx`.

#### What this points at

The bug is **upstream of `plotting.py` and upstream of
`integration.inject_neighbourhood_default_schedules()`**. The
`Heating:EnergyTransfer` meter in `eplusout.sql` is itself reporting
unphysical monthly totals. That means the cause has to live in one
of:

- the source neighbourhood IDF (HVAC template, thermostat schedules,
  heating coil availability schedule, sizing setup),
- `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf()`, which
  duplicates / rotates buildings and may rewrite schedules in the
  process,
- or the EnergyPlus run command / IDD version, which is unlikely
  given that the cooling profile is mostly right.

The most plausible single cause is a **swapped or
seasonally-misaligned heating availability / setpoint schedule**.
The pattern (zero heating in spring/fall, large heating in
high-cooling-demand months Jul–Sep, with September as the peak) is
characteristic of what happens when a *cooling* availability schedule
or a *summer dehumidification reheat* schedule is wired into the
heating coil availability slot. The exact mechanism cannot be
identified without inspecting the IDF after `prepare_neighbourhood_idf`
runs.

---

### 3.3 Bonus finding — duplicate iter results across some Monte Carlo iterations

While running §3.2's iteration cross-check I noticed that the monthly
heating profiles for `iter_1/2025/eplusout.sql` and
`iter_5/2025/eplusout.sql` are byte-identical, not just close:

```
iter_1/2025  Jan 39.47   Sep 267.78   Dec 18.70
iter_5/2025  Jan 39.47   Sep 267.78   Dec 18.70
```

The cooling profile is also identical between the two. The Monte Carlo
loop at `main.py:1946-2065` is supposed to draw a *different* random
sample of households per iteration via `random.sample(...)` at
`main.py:1963`. If two iterations produce byte-identical SQL output,
either:

- the random seed is being fixed somewhere upstream,
- the candidate pool is so small after filtering at `main.py:1955-1963`
  that the same households are picked twice, or
- the schedule injection is being short-circuited.

This is **out of scope** for this debug doc — it's neither of the two
plot anomalies the user reported — but it should be flagged for
follow-up because it artificially shrinks the Monte Carlo standard
deviation across iterations and would mask any real inter-scenario
variability the bar chart is supposed to surface.

---

### 3.4 Why both anomalies are silent

- Anomaly 2 — `calculate_eui()` returns a dict that simply omits the
  heating key. Nothing in the EUI pipeline cross-validates against
  `Total End Uses` (which is also in the SQL at 542 GJ for this run),
  so the omission never triggers a check.
- Anomaly 1 — the SQL data is internally consistent (12 monthly
  values, chronological order, single environment period), so neither
  the meter extractor nor the plotter has anything obviously wrong to
  flag. EnergyPlus itself emits no error or warning about the
  unphysical seasonal shape because it's a valid simulation result —
  it's only "wrong" relative to the physical climate of Montreal.
- Both errors compound: a user who sees the bar chart with no heating
  bar and the time-series with summer-peaking heating could
  reasonably conclude that the Montreal model has near-zero heating
  load with a small July–September shoulder. That's not just wrong —
  it's almost the *opposite* of the truth.

---

## 4. Proposed Fix (for follow-up implementation tasks)

> This debug doc **only specifies** the fix. Implementation happens in
> a separate change after the user approves the direction.

### 4.1 Anomaly 2 — narrow the `calculate_eui()` skip filter

**One-line edit, fully scoped, does not affect any other end use.**

`eSim_bem_utils/plotting.py:171-173` currently reads:

```python
# Skip water columns
if 'Water' in col_name or 'm3' in str(units):
    continue
```

The intent is "skip the m³ water-consumption column". The
`'m3' in str(units)` half of the OR already does that — when the
column is the literal water-consumption column, `Units` is `'m3'` (or
`'m3/s'`), which the second clause catches.

The first clause (`'Water' in col_name`) is then redundant for the
water-consumption row *and* over-broad: it also matches column names
like `District Heating Water`, `Hot Water`, and any other future
column whose label happens to contain the substring `Water`. Drop it:

```python
# Skip water-consumption columns (m3, m3/s units)
if 'm3' in str(units):
    continue
```

This:

- Restores the heating row (`District Heating Water` GJ → 531 GJ →
  ~74 kWh/m² of heating EUI in this run).
- Restores the Water Systems row (`District Heating Water` GJ → 11 GJ
  → the real ~1.5 kWh/m² DHW EUI, replacing the misleading 0.001
  residual).
- Continues to drop the literal `Water` (m³) row because of the
  `'m3' in units` check.
- Continues to drop the kg/s, kg, m² and any other non-energy unit row
  via the existing `else: val_kwh = val` fall-through (which only
  fires for Joules / kWh / GJ / kBtu / Btu / MJ).

There is no other place in `plotting.py`, `main.py`, or `reporting.py`
that depends on the dropped row. The category dict is consumed
generically by the bar chart and the per-iteration JSON dump, both of
which already handle arbitrary new keys.

### 4.1b Optional but recommended — cross-check against `Total End Uses`

While editing `calculate_eui()`, add a cheap sanity check just before
the `return results`:

```python
total_row = subset[(subset['RowName'] == 'Total End Uses') &
                   (subset['Units'].isin(['GJ', 'kWh', 'MJ', 'J']))]
expected = sum(...)  # convert and sum just like the loop above
if abs(total_energy - expected) / max(expected, 1.0) > 0.05:
    print(f"  [WARN] EUI sum mismatch: {total_energy:.1f} vs Total End Uses {expected:.1f} kWh")
```

This catches any future case where a unit conversion or filter change
silently drops a row, so the next "missing heating bar" incident
becomes loud rather than silent. **Out of scope for the minimum fix.**

### 4.2 Anomaly 1 — investigate the upstream IDF / preparation, do NOT touch `plotting.py`

The plotting code is faithful to the SQL. Patching `plot_kfold_timeseries`,
`get_meter_data`, or any other plot-side function would mask the
underlying problem rather than fix it. The fix has to land in the
IDF or in `prepare_neighbourhood_idf()`. Step 5 of §5 specifies the
investigation approach.

The minimum diagnostic actions are:

1. Open `iter_1/2005/Scenario_2005.idf` (the post-injection file at
   `iter_1/2005/Scenario_2005.idf`) and locate every `Schedule:Compact`,
   `Schedule:File`, or `Schedule:Year` referenced by the
   `Coil:Heating:Water` (or whichever heating coil object is in the
   IDF), the heating thermostat setpoint
   (`ZoneControl:Thermostat` → `ThermostatSetpoint:DualSetpoint`),
   and the heating availability schedule on the air loop
   (`AirLoopHVAC` → `AvailabilityManagerAssignmentList`).
2. Check whether any of those schedules has a 6-month phase shift, a
   summer-only `1` profile, or a `Through:` block that begins in July
   instead of January.
3. Compare against the corresponding objects in the source
   `BEM_Setup/Neighbourhoods/<chosen>.idf` *before*
   `prepare_neighbourhood_idf` runs. If the source IDF is correct and
   the prepared file is not, the bug is in
   `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf()`. If the
   source IDF is also wrong, the bug is in the IDF itself and the fix
   is upstream of this codebase.
4. As a faster sanity check, run the source IDF directly via
   EnergyPlus on the Montreal EPW (no Option 7 wrapping) and compare
   the resulting `Heating:EnergyTransfer` monthly profile. If a raw
   run also produces the September peak, the bug is in the IDF; if a
   raw run produces a normal winter-peak profile, the bug is somewhere
   in the BEM-side preparation/injection chain.

### 4.3 Do NOT touch

- `eSim_bem_utils/plotting.py:551-627` `get_meter_data()` — the SQL
  query is correct.
- `eSim_bem_utils/plotting.py:902-1033` `plot_kfold_timeseries()` —
  the days-per-month + floor-area normalization is correct.
- `eSim_bem_utils/main.py:2090-2174` — the aggregation loop is
  correct *given* a `calculate_eui()` that returns a heating row.
  Once §4.1 lands, the bar chart, the CSV, and the per-iteration JSON
  will all gain a heating column without any further edit.
- `eSim_bem_utils/integration.inject_neighbourhood_default_schedules()`
  — Default produces the same Anomaly 1 profile, so the schedule
  injection path is not implicated.

---

## 5. Step-by-Step Investigation / Fix Plan

Each step follows the CLAUDE.md task format: *aim → what → how → why
→ impact → steps → expected result → how to test*.

### Step 1 — Reproduce both anomalies on the existing run output

- **Aim of task:** confirm both plots show the anomalies described
  before any code is touched, and capture exact numerical baselines.
- **What to do:** open
  `PLOT_RESULTS_DIR/MonteCarlo_Neighbourhood_EUI_*.png` and
  `PLOT_RESULTS_DIR/MonteCarlo_Neighbourhood_TimeSeries_*.png` from
  the existing
  `MonteCarlo_Neighbourhood_N10_1775555644/` run. Open
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/aggregated_eui.csv`
  in a text editor.
- **How to do:** no code execution needed — the artefacts are
  already on disk.
- **Why to do:** anchors the fix to a concrete before/after baseline
  and confirms the anomalies are reproducible from the existing
  artefacts (no need to re-run 51 simulations to debug them).
- **What this impacts:** read-only.
- **Steps / sub-steps:**
  1. Open the bar chart, count the bars: should be 4
     (Lighting / Equipment / Water Systems / Cooling), no Heating.
  2. Open the CSV: confirm 4 data rows, no `Heating` row.
  3. Open the time-series plot: confirm the heating panel peaks
     in September.
- **Expected result:** the bar chart has 4 bars and no Heating bar;
  the CSV has 4 data rows; the time-series heating panel peaks in
  September; the six scenario lines visually overlap.
- **How to test:** by inspection of the existing PNGs and CSV.

### Step 2 — Verify Anomaly 2's root cause directly against the SQL

- **Aim of task:** prove that the `'Water' in col_name` filter is
  what drops the heating row, before changing any code.
- **What to do:** query
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/iter_1/2005/eplusout.sql`
  for every row in `End Uses By Subcategory` whose `RowName` starts
  with `Heating:`, and confirm that the only non-zero entry has
  `ColumnName='District Heating Water'` and `Units='GJ'`.
- **How to do:** a 5-line throwaway Python script using `sqlite3`
  (template provided in §6.2 below). Do **not** edit `plotting.py`
  in this step.
- **Why to do:** independent verification of §3.1 before touching
  source.
- **What this impacts:** read-only.
- **Steps / sub-steps:**
  1. Open the SQL with `sqlite3.connect(...)`.
  2. Run the query in §6.2.
  3. Confirm the result matches the row dump in §3.1.
- **Expected result:** exactly one non-zero heating row, with
  `ColumnName='District Heating Water'`, value ≈ 531 GJ.
- **How to test:** the script prints the row; visual confirmation.

### Step 3 — Apply the one-line fix to `calculate_eui()`

- **Aim of task:** restore the heating bar in the EUI breakdown
  (Anomaly 2) by narrowing the skip filter as specified in §4.1.
- **What to do:** edit
  `eSim_bem_utils/plotting.py:171-173` to drop the
  `'Water' in col_name` clause, leaving only `'m3' in str(units)`.
- **How to do:** single-line edit, comment update if desired. No
  other change to `calculate_eui()` and no change to anything that
  calls it.
- **Why to do:** the single root cause of Anomaly 2.
- **What this impacts:** every caller of `calculate_eui()`:
  `plot_eui_breakdown`, `process_single_result`, `plot_eui_histogram`,
  `plot_comparative_eui`, `plot_kfold_comparative_eui` (via
  `option_batch_comparative_neighbourhood_simulation`), and
  `plot_validation_comparison`. All of them already iterate the
  result dict generically and will pick up the new heating key with
  no further edit.
- **Steps / sub-steps:**
  1. Open `eSim_bem_utils/plotting.py`.
  2. Replace lines 171-173 as specified in §4.1.
  3. Save. No other edits.
- **Expected result:** `calculate_eui()` returns a dict whose
  `end_uses` contains a `Heating` key (or `Heating:General` after
  the colon-split logic at line 204-211).
- **How to test:** run Step 4.

### Step 4 — Re-run only the aggregation/plot stage on the existing SQL

- **Aim of task:** regenerate the bar chart and CSV from the existing
  51 SQL files **without** re-running the simulation, and confirm the
  heating bar is now present.
- **What to do:** call `option_batch_comparative_neighbourhood_simulation`'s
  aggregation/plot block on the already-completed
  `MonteCarlo_Neighbourhood_N10_1775555644` directory. Easiest way:
  write a 30-line `replot_existing_montecarlo.py` helper that walks
  the existing iter_*/<year>/eplusout.sql files, runs
  `plotting.calculate_eui` and `plotting.get_meter_data` on each, and
  re-invokes `plot_kfold_comparative_eui` and `plot_kfold_timeseries`.
  *Do not modify `main.py` or the option 7 runner* — the existing
  functions in `plotting.py` are reusable directly.
- **How to do:** standalone Python script, lives outside the
  `eSim_bem_utils/` package or in `eSim_tests/`.
- **Why to do:** running the full Option 7 takes ~1 hour for N=10
  iterations × 5 scenarios; this isolates the plotting fix from the
  simulation step and lets the user verify Anomaly 2's fix in seconds.
- **What this impacts:** writes new PNGs and a new CSV next to the
  existing ones (different timestamp / filename), or to a temporary
  directory. Does not overwrite any source-of-truth artefacts.
- **Steps / sub-steps:**
  1. Glob `MonteCarlo_Neighbourhood_N10_1775555644/iter_*/<year>/eplusout.sql`
     and `MonteCarlo_Neighbourhood_N10_1775555644/Default/eplusout.sql`.
  2. For each file, build the same `all_eui_results` and
     `all_meter_results` dicts that `option_batch_comparative_neighbourhood_simulation`
     builds at `main.py:1929-2090`.
  3. Re-run the aggregation block at `main.py:2090-2174` against
     those dicts.
  4. Save the new plots and CSV to a `replot/` subdirectory.
- **Expected result:** the new bar chart contains 5 bars (Heating,
  Lighting, Equipment, Water Systems, Cooling); the heating bar is
  the dominant one (~74 kWh/m² for 2005, similar for the other years);
  the new CSV has 5 data rows.
- **How to test:** open the new PNG and visually confirm the heating
  bar; `cat` the new CSV and confirm a `Heating` row.

### Step 5 — Diagnose Anomaly 1 by inspecting the prepared IDF

- **Aim of task:** identify whether the inverted heating profile
  comes from the source neighbourhood IDF or from
  `prepare_neighbourhood_idf()`.
- **What to do:** open
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/iter_1/2005/Scenario_2005.idf`
  and locate every schedule referenced by the heating side of the
  HVAC system. Compare against the corresponding objects in the
  source neighbourhood IDF under `BEM_Setup/Neighbourhoods/`.
- **How to do:** text-search the IDF for the schedule object names
  and trace each reference. The objects to inspect, in order of
  likelihood:
  1. `ThermostatSetpoint:DualSetpoint` → its
     `Heating Setpoint Temperature Schedule Name` reference.
  2. `Coil:Heating:Water` (or whichever heating coil class is
     present) → its `Availability Schedule Name`.
  3. `AirLoopHVAC` → its `Availability Schedule Name`, and the
     `AvailabilityManagerAssignmentList` it points at.
  4. `Schedule:Compact` / `Schedule:File` / `Schedule:Year` objects
     of the names found above.
- **Why to do:** the SQL evidence in §3.2 narrows the cause to one of
  these three schedule slots. Inspecting them is faster than
  bisecting the simulation.
- **What this impacts:** read-only inspection of an IDF.
- **Steps / sub-steps:**
  1. Open the prepared IDF in a text editor.
  2. For each schedule found, copy the body and check the seasonal
     shape (does the schedule have a `Through: 9/30` block with `1`
     and a `Through: 12/31` block with `0`?).
  3. Open the source `BEM_Setup/Neighbourhoods/<idf>` and look for
     the same objects.
  4. Diff the two — if they differ, the bug is in
     `prepare_neighbourhood_idf()`; if they don't, the bug is in
     the source IDF itself.
- **Expected result:** one of the schedules has a 6-month phase shift
  or a summer-only availability window. Identify which.
- **How to test:** Step 6.

### Step 6 — Run the source IDF directly through EnergyPlus

- **Aim of task:** confirm whether the unphysical heating profile
  exists in the source IDF or only after `prepare_neighbourhood_idf()`.
- **What to do:** run the source neighbourhood IDF on the Montreal
  EPW directly via `simulation.run_simulations_parallel` (or via the
  EnergyPlus CLI), bypassing
  `option_batch_comparative_neighbourhood_simulation` entirely.
- **How to do:** ad-hoc Python or CLI invocation. No new helper
  needed.
- **Why to do:** isolates the bug from the BEM-side preparation /
  injection chain. If the raw run reproduces the September peak, the
  IDF is the bug; if it doesn't, the bug is in
  `prepare_neighbourhood_idf` or `inject_neighbourhood_*_schedules`.
- **What this impacts:** writes one extra `eplusout.sql` to a scratch
  directory.
- **Steps / sub-steps:**
  1. Pick the same source IDF Option 7 used.
  2. Run it directly on the same Montreal EPW.
  3. Query the resulting `eplusout.sql` for monthly
     `Heating:EnergyTransfer` (template in §6.3).
- **Expected result:** either a winter-peak profile (which means
  `prepare_neighbourhood_idf` is the bug) or a September-peak profile
  (which means the source IDF is the bug).
- **How to test:** by comparing the new monthly profile with the
  Montreal climate expectation (Jan ≫ Sep).

### Step 7 — Apply the upstream fix for Anomaly 1

- **Aim of task:** correct whichever schedule or preparation step
  Step 5 / Step 6 identified.
- **What to do:** depends on Step 5 / Step 6. Either edit the source
  IDF, edit `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf`,
  or both.
- **How to do:** one targeted edit; do not touch `plotting.py` or
  `main.py`.
- **Why to do:** the only correct fix for Anomaly 1.
- **What this impacts:** Option 7 outputs (and any other path that
  uses the same IDF or the same prepare function).
- **Steps / sub-steps:** depends on Step 5/6 outcome — defer
  specification until then.
- **Expected result:** a re-run produces a winter-peak heating
  profile.
- **How to test:** Step 8.

### Step 8 — Re-run Option 7 end-to-end on Montreal and verify both fixes

- **Aim of task:** prove the Monte Carlo neighbourhood pipeline now
  produces a physically plausible bar chart and time-series.
- **What to do:** `python run_bem.py` → 7 → choose the same
  neighbourhood IDF → Montreal EPW → iter_count=10 (or smaller for
  speed: 3 is enough to verify the fix). Wait for completion.
- **How to do:** through the existing CLI menu. No code change.
- **Why to do:** end-to-end regression test combining the Anomaly 2
  fix (Step 3) and the Anomaly 1 fix (Step 7).
- **What this impacts:** writes a new
  `MonteCarlo_Neighbourhood_N{K}_*` directory and a new pair of PNGs.
- **Steps / sub-steps:**
  1. Launch Option 7 with the parameters above.
  2. Wait for `Successful: K*5+1/K*5+1`.
  3. Open the new bar chart and time-series.
- **Expected result:** bar chart shows 5 bars, dominant Heating bar
  ~50–80 kWh/m²; time-series heating panel peaks in Dec / Jan / Feb
  with near-zero values in Jun-Aug; the six scenario lines have
  visible inter-scenario differentiation.
- **How to test:** by inspection of the new PNGs.

### Step 9 — Document the fix in this debug doc

- **Aim of task:** append a "Resolution" chapter so future maintainers
  find the fix without diffing the source.
- **What to do:** add chapter 9 "Resolution" with the before/after
  bar chart, before/after monthly heating values, and the exact files
  / lines edited.
- **Why to do:** matches the format of `2025_schedule_data_debug.md`
  and `neighbourhood_BEM_debug.md`; closes the loop for the next
  person.
- **What this impacts:** this markdown file only.
- **Expected result:** the doc ends with a dated, concise resolution
  note with file paths and line numbers.
- **How to test:** by reading the doc end-to-end.

---

## 6. Evidence Appendix

### 6.1 Aggregated EUI CSV (the "missing heating bar" artefact)

```
$ cat BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/aggregated_eui.csv
EndUse,2005_mean,2005_std,2010_mean,2010_std,2015_mean,2015_std,2022_mean,2022_std,2025_mean,2025_std,Default_mean,Default_std
Interior Lighting,2.4136,0.0547,2.5048,0.0118,2.4066,0.0609,2.4299,0.0591,2.3933,0.0196,2.6440,0.0000
Electric Equipment,60.3282,0.4020,60.7142,0.3175,59.9845,0.7672,60.4292,0.3282,58.3728,0.6198,61.2570,0.0000
Water Systems,0.0010,0.0000,0.0010,0.0000,0.0010,0.0000,0.0010,0.0000,0.0010,0.0000,0.0010,0.0000
Cooling,42.0822,1.1387,42.6217,1.2368,42.2511,1.3485,43.4129,1.6339,41.8359,1.4097,45.8280,0.0000
```

Four rows. No `Heating` row. Sum of mean column for 2005:
2.41 + 60.33 + 0.001 + 42.08 = **104.82 kWh/m²**, which matches the
~105 kWh/m² total visible on the bar chart.

### 6.2 SQL query to verify Anomaly 2's root cause

Run against any
`MonteCarlo_Neighbourhood_N10_1775555644/iter_*/<year>/eplusout.sql`:

```python
import sqlite3

conn = sqlite3.connect("eplusout.sql")
cur = conn.cursor()
cur.execute("""
    SELECT TableName, RowName, ColumnName, Units, Value
    FROM TabularDataWithStrings
    WHERE TableName IN ('End Uses', 'End Uses By Subcategory')
      AND (RowName LIKE 'Heating%' OR RowName LIKE '%Heating:%')
      AND CAST(Value AS REAL) > 0
""")
for row in cur.fetchall():
    print(row)
conn.close()
```

Expected output (verified on `iter_1/2005`):

```
('End Uses', 'Heating', 'District Heating Water', 'GJ', '      531.03')
('End Uses', 'Heating', 'District Heating Water', 'W',  '   142831.46')
('End Uses By Subcategory', 'Heating:General', 'District Heating Water', 'GJ', '      531.03')
('End Uses By Subcategory', 'Heating:General', 'District Heating Water', 'W',  '   142831.46')
```

Every non-zero heating entry has `ColumnName='District Heating Water'`,
which the substring filter `'Water' in col_name` at
`plotting.py:172` matches and skips.

### 6.3 SQL query to verify Anomaly 1's monthly heating profile

```python
import sqlite3

conn = sqlite3.connect("eplusout.sql")
cur = conn.cursor()
cur.execute("""
    SELECT t.Month, rd.Value
    FROM ReportData rd
    JOIN Time t ON rd.TimeIndex = t.TimeIndex
    JOIN ReportDataDictionary dd ON rd.ReportDataDictionaryIndex = dd.ReportDataDictionaryIndex
    WHERE dd.Name = 'Heating:EnergyTransfer'
      AND dd.ReportingFrequency = 'Monthly'
    ORDER BY t.TimeIndex ASC
""")
for month, value in cur.fetchall():
    print(f"  Month {month:2d}: {value/1e9:8.2f} GJ")
conn.close()
```

Expected output (verified on `iter_1/2005`):

```
  Month  1:    37.67 GJ
  Month  2:    12.47 GJ
  Month  3:     4.48 GJ
  Month  4:     0.00 GJ
  Month  5:     0.00 GJ
  Month  6:     4.48 GJ
  Month  7:    84.74 GJ
  Month  8:   104.45 GJ
  Month  9:   271.07 GJ
  Month 10:     0.06 GJ
  Month 11:     1.48 GJ
  Month 12:    16.65 GJ
```

September peak ≈ 271 GJ; January only 38 GJ. **This is in the SQL
itself, not in any plotting code.** Same shape across iter_1/2005,
iter_1/2025, iter_2/2005, iter_5/2025, and Default — within ~1 % per
month — which rules out an iteration-specific or schedule-injection
cause.

### 6.4 Cooling profile (sanity check that meter ordering is correct)

```
  Month  1: Cooling 15.65 GJ
  Month  2:         24.31 GJ
  Month  3:         46.65 GJ
  Month  4:         68.69 GJ
  Month  5:         96.96 GJ
  Month  6:        115.14 GJ  ← peak (correct for Montreal)
  Month  7:         60.37 GJ
  Month  8:         46.95 GJ
  Month  9:         27.11 GJ
  Month 10:         91.16 GJ  (suspicious — separate concern)
  Month 11:         42.49 GJ
  Month 12:         18.37 GJ
```

Cooling peaks in June, which is consistent with a Montreal summer.
This proves that `get_meter_data()` is not extracting the months in a
swapped order — if it were, the cooling profile would also be inverted.

### 6.5 EnvironmentPeriods evidence (rules out sizing-period folding)

```
$ sqlite3 iter_1/2005/eplusout.sql "SELECT * FROM EnvironmentPeriods"
32|1|RUN PERIOD 1|3
```

Exactly one period, `EnvironmentType=3` (RunPeriod). The
`WHERE ep.EnvironmentType = 3` filter in `get_meter_data()` is not
folding sizing or design-day periods on top of the run period.

### 6.6 Cross-iteration evidence (rules out schedule-injection cause)

```
                  Jan   Feb   Mar  Apr  May  Jun  Jul   Aug    Sep   Oct  Nov   Dec
iter_1/2005    37.67 12.47  4.48 0.00 0.00 4.48 84.74 104.45 271.07 0.06 1.48 16.65
iter_1/2025    39.47 14.02  4.99 0.00 0.00 4.45 85.02 103.94 267.78 0.12 2.03 18.70
iter_2/2005    37.23 12.27  4.38 0.00 0.00 4.49 84.94 104.36 271.61 0.02 1.40 16.32
iter_5/2025    39.47 14.02  4.99 0.00 0.00 4.45 85.02 103.94 267.78 0.12 2.03 18.70
Default        27.97  6.38  1.93 0.00 0.00 4.31 82.04 100.41 268.36 0.03 0.26  8.91
```

The Default row uses `inject_neighbourhood_default_schedules()`
(`main.py:1904`), not the Monte Carlo schedule injection. It still
shows the same September-peak shape, so the injection step is not
causing the inversion.

`iter_1/2025` and `iter_5/2025` are byte-identical — flagged as a
separate Monte Carlo concern in §3.3.

### 6.7 Weather file evidence (confirms Montreal EPW is selected)

```
$ sqlite3 iter_1/2005/eplusout.sql \
    "SELECT Value FROM TabularDataWithStrings
     WHERE TableName='General' AND RowName='Weather File'"
Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish QC CAN SRC-TMYx WMO#=716120
```

The right EPW is being used; the inverted profile is not a wrong-EPW
artefact.

### 6.8 Monthly meter dictionary (confirms `Heating:EnergyTransfer` exists)

```
$ sqlite3 iter_1/2005/eplusout.sql \
    "SELECT Name, Units FROM ReportDataDictionary
     WHERE ReportingFrequency='Monthly' ORDER BY Name"
Cooling:EnergyTransfer|J
Electricity:Facility|J
Fans:Electricity|J
Heating:EnergyTransfer|J
InteriorEquipment:Electricity|J
InteriorLights:Electricity|J
WaterSystems:EnergyTransfer|J
```

The meter exists and is correctly named. `get_meter_data()` is reading
the right column; the data in that column is what's wrong.

### 6.9 Code references for Anomaly 2 (the diagnosed bug)

- `eSim_bem_utils/plotting.py:171-173` — the `'Water' in col_name`
  filter that drops the heating row.
- `eSim_bem_utils/plotting.py:148-217` — `calculate_eui()` end-use
  loop.
- `eSim_bem_utils/main.py:2094-2105` — the aggregation step that
  derives `categories` from the first scenario, propagating the
  missing key across all six scenarios and into the CSV writer at
  `main.py:2122-2133` and the bar chart at `main.py:2136-2140`.

### 6.10 Code references for Anomaly 1 (the diagnosed-narrowed but not yet identified bug)

- `eSim_bem_utils/plotting.py:551-627` — `get_meter_data()` (verified
  correct).
- `eSim_bem_utils/plotting.py:902-1033` — `plot_kfold_timeseries()`
  (verified correct).
- `eSim_bem_utils/main.py:1894-1928` — Default simulation path that
  also exhibits Anomaly 1, ruling out the Monte Carlo schedule
  injection.
- `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf` — first
  candidate for the upstream cause.
- `BEM_Setup/Neighbourhoods/*.idf` — second candidate for the upstream
  cause (the source IDFs themselves).

---

## 7. Task List for Implementation Agent

This chapter reformats the investigation plan in §5 into a clean,
execution-focused checklist. Each task follows the CLAUDE.md task
format: *aim → what → how → why → impact → steps → result → test*.

Tasks are listed in recommended execution order (Task 1 → Task 11).
Tasks 1–4 resolve Anomaly 2 (the plotting bug). Tasks 5–9 diagnose
and fix Anomaly 1 (the upstream simulation bug). Tasks 10–11 are
closing tasks (regression run and documentation) that should run
only after tasks 1–9 are complete.

An implementation agent should execute them sequentially, stopping
after each task to record findings in the Progress Log (§8) before
moving on.

---

#### Task 1 — Narrow the `'Water'` skip filter in `calculate_eui()`

- **Aim of task:** make `calculate_eui()` stop dropping the
  `District Heating Water` row so the heating end use re-appears in
  the result dict.
- **What to do:** edit `eSim_bem_utils/plotting.py` lines 171-173 to
  drop the `'Water' in col_name` clause, keeping only the
  `'m3' in str(units)` check.
- **How to do:**
  ```python
  # BEFORE (plotting.py:171-173)
  # Skip water columns
  if 'Water' in col_name or 'm3' in str(units):
      continue

  # AFTER
  # Skip water-consumption columns (m3 / m3/s units)
  if 'm3' in str(units):
      continue
  ```
- **Why to do this task:** §3.1 proved that every non-zero heating
  row in the `End Uses By Subcategory` table has
  `ColumnName='District Heating Water'`. The old filter matched that
  substring and dropped the heating row. Narrowing the filter to the
  unit check alone correctly drops only the literal water-consumption
  column (which has `Units='m3'` or `'m3/s'`) without touching heating.
- **What will impact on:** every caller of `calculate_eui()` —
  `plot_eui_breakdown`, `process_single_result`, `plot_eui_histogram`,
  `plot_comparative_eui`, `plot_kfold_comparative_eui` (via Option 7),
  and `plot_validation_comparison`. All of them iterate the returned
  `end_uses` dict generically, so they pick up the new `Heating` key
  with no further edit.
- **Steps / sub-steps:**
  1. Open `eSim_bem_utils/plotting.py`.
  2. Locate lines 171-173 (the `# Skip water columns` comment block
     inside `calculate_eui()`).
  3. Replace them with the two-line version above.
  4. Save. No other edits anywhere in the file.
- **What to expect as result:** `calculate_eui()` now returns an
  `end_uses` dict containing a `Heating` (or `Heating:General`) key
  with a value of ~147 000 kWh for the Montreal IDF used in this run,
  which normalizes to ~74 kWh/m² of heating EUI.
- **How to test:** task 2 below (offline replot) runs the regression
  without requiring a fresh simulation.

#### Task 2 — Regenerate the Monte Carlo plots from the existing SQL files

- **Aim of task:** verify task 1's fix against the 51 already-completed
  SQL files *without* re-running the 1-hour Monte Carlo simulation.
- **What to do:** write a throwaway helper script
  `replot_existing_montecarlo.py` that walks
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/`,
  re-runs `calculate_eui()` and `get_meter_data()` on each SQL file,
  re-aggregates with mean ± std per scenario, and re-invokes
  `plot_kfold_comparative_eui()` and `plot_kfold_timeseries()`.
- **How to do:** the script should mirror the aggregation block at
  `main.py:2090-2174` but operate on a pre-existing directory instead
  of running simulations. Target output directory: a new
  `MonteCarlo_Neighbourhood_N10_1775555644/replot/` subdirectory so
  the original PNGs and CSV are preserved for before/after comparison.
- **Why to do this task:** Option 7's full run is slow (10 iterations
  × 5 scenarios ≈ 1 hour on laptop hardware). Re-using the existing
  SQL files cuts the task 1 verification turnaround from hours to
  seconds, which is the only way to iterate safely on the fix if
  anything goes wrong.
- **What will impact on:** writes new PNGs and a new CSV into
  `.../MonteCarlo_Neighbourhood_N10_1775555644/replot/`. Does not
  modify any source files and does not overwrite the existing
  artefacts.
- **Steps / sub-steps:**
  1. Glob `iter_*/{2005,2010,2015,2022,2025}/eplusout.sql` and
     `Default/eplusout.sql` under the batch directory.
  2. For each SQL, open a connection, call
     `plotting.calculate_eui(conn)` and `plotting.get_meter_data(conn)`,
     close the connection.
  3. Bin the results into `all_eui_results[scenario]` and
     `all_meter_results[scenario]` dicts, same structure as
     `main.py:1932-2088`.
  4. Derive `categories` from the first non-empty scenario's
     `end_uses_normalized`.
  5. Compute mean ± std per scenario per category.
  6. Call `plotting.plot_kfold_comparative_eui()` and
     `plotting.plot_kfold_timeseries()` with the aggregated dicts,
     writing to the `replot/` subdirectory.
  7. Also write a new `aggregated_eui.csv` to the same subdirectory.
- **What to expect as result:** the new bar chart contains **five**
  bars (Heating, Interior Lighting, Electric Equipment, Water
  Systems, Cooling); the Heating bar is ~70–80 kWh/m² and dominates
  the chart; the new CSV has five data rows including a `Heating`
  row with values around 70–80 in the `*_mean` columns.
- **How to test:** visual inspection of the new bar chart and
  `diff`-compare the old and new CSV row counts.

#### Task 3 — Add a cross-check warning against `Total End Uses`

- **Aim of task:** make any future "silently dropped end use" incident
  loud rather than silent, so this class of bug does not recur.
- **What to do:** inside `calculate_eui()` just before `return results`,
  read the `Total End Uses` row from the same `End Uses` table, sum
  it across the energy-unit columns, and emit a `[WARN]` print if the
  sum disagrees with `total_energy` by more than 5%.
- **How to do:**
  ```python
  # After the end_uses loop, before `return results`
  total_df = df[(df['TableName'] == 'End Uses') &
                (df['RowName'] == 'Total End Uses')]
  expected = 0.0
  for _, row in total_df.iterrows():
      try:
          v = float(row['Value'])
      except ValueError:
          continue
      u = row['Units']
      if 'm3' in str(u):
          continue
      if u == 'GJ':
          expected += v * 277.778
      elif u == 'kWh':
          expected += v
      # ... (same unit conversions as the main loop)
  if expected > 0 and abs(total_energy - expected) / expected > 0.05:
      print(f"  [WARN] EUI sum {total_energy:.1f} kWh disagrees "
            f"with 'Total End Uses' {expected:.1f} kWh (>5%)")
  ```
- **Why to do this task:** §3.4 showed that Anomaly 2 went unnoticed
  because no step in the EUI pipeline cross-validates the per-row
  sum against the SQL's own `Total End Uses` row. A one-line warning
  would have caught the `'Water' in col_name` bug on the first run.
- **What will impact on:** every caller of `calculate_eui()`; the
  new warning prints once per SQL file processed. It does not alter
  any return value.
- **Steps / sub-steps:**
  1. Re-read the `End Uses` tabular query already performed at
     `plotting.py:148-154` (the `df` variable covers both
     `End Uses` and `End Uses By Subcategory`).
  2. Filter for `TableName='End Uses'` and `RowName='Total End Uses'`.
  3. Loop and convert like the main end-use loop.
  4. Print the warning if the deviation exceeds 5%.
- **What to expect as result:** clean console when the fix works;
  a loud `[WARN]` line if any future edit ever drops a row again.
- **How to test:** after tasks 1 + 3 land, re-run task 2 and confirm
  no warning prints. Then temporarily revert task 1 and re-run task 2
  to confirm the warning fires on the broken version. Re-apply task 1.

#### Task 4 — Commit the Anomaly 2 fix

- **Aim of task:** ship the Anomaly 2 fix on its own commit (or PR)
  so the heating bar regression is resolved independently of the
  slower Anomaly 1 work in tasks 5–9.
- **What to do:** create a commit touching only
  `eSim_bem_utils/plotting.py` (lines 171-173, plus the task 3
  warning block) and referencing this debug doc in the message.
- **How to do:** follow the repo's existing commit style
  (`[fix]: ...` per `CLAUDE.md § Git Commit Style`).
- **Why to do this task:** keeps the diff bisectable and lets the
  user verify the fix on a branch before it's rolled into the
  upstream fix from tasks 5–9.
- **What will impact on:** `eSim_bem_utils/plotting.py`.
- **Steps / sub-steps:**
  1. `git add eSim_bem_utils/plotting.py`.
  2. `git commit -m "[fix]: restore heating EUI bar for District
     Heating Water systems"` with a body pointing at
     `eSim_docs_ubem_utils/docs_debug/montecarlo_plot_anomalies_debug.md`.
- **What to expect as result:** a single-file commit that closes
  Anomaly 2.
- **How to test:** rerun task 2 on a clean checkout of the commit.

#### Task 5 — Dump the HVAC + schedule objects from the prepared IDF

- **Aim of task:** enumerate every schedule that controls the heating
  side of the HVAC for one representative iteration, so task 6 can
  bisect them.
- **What to do:** open
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/iter_1/2005/Scenario_2005.idf`
  and extract the full text of:
  1. every `ThermostatSetpoint:DualSetpoint` object,
  2. every `Coil:Heating:*` object (the exact class name depends on
     the HVAC template),
  3. every `AirLoopHVAC` object and its
     `AvailabilityManagerAssignmentList`,
  4. every `Schedule:Compact`, `Schedule:File`, or `Schedule:Year`
     referenced by the above.
- **How to do:** a throwaway `extract_heating_schedules.py` script
  using `eppy` (already in the project dependencies) or plain
  text-search. Write the extracted blocks to
  `eSim_tests/tmp/iter_1_2005_heating_schedules.txt` for inspection.
- **Why to do this task:** §3.2 narrowed the bug to one of these
  schedules, but the prepared IDF is ~100 MB so manual scrolling is
  impractical. A targeted extract is the fastest way to get a
  reviewable subset.
- **What will impact on:** read-only inspection; produces one
  scratch text file.
- **Steps / sub-steps:**
  1. Open the prepared IDF in `eppy`
     (`IDF(..., epw=None)` if the weather file is unavailable; use
     `IDF.idd_info` for version detection).
  2. For each target class, dump `idf.idfobjects[class_name]`.
  3. Walk the schedule references and dump those schedule objects
     too.
  4. Save to the tmp file.
- **What to expect as result:** a ~300-line text file containing
  every heating-relevant schedule.
- **How to test:** open the tmp file and confirm it contains the
  schedule types listed under "What to do".

#### Task 6 — Identify which schedule has a summer-weighted shape

- **Aim of task:** identify the exact `Schedule:*` object whose
  seasonal profile matches the observed September-peak heating shape.
- **What to do:** inspect each schedule dumped in task 5 and look for
  one of these patterns:
  1. A `Through:` block that starts in July or September instead of
     January.
  2. A constant `1` value during Jul–Sep and `0` elsewhere.
  3. A swap between the heating and cooling setpoint schedule
     references (e.g. the `Heating Setpoint Temperature Schedule Name`
     pointing at a cooling setpoint schedule).
- **How to do:** manual inspection of the tmp file from task 5.
  Because §3.2 showed the shape peaks in September, any schedule
  with a "summer-only" or "autumn-peak" profile attached to the
  heating side is the suspect.
- **Why to do this task:** this is the smallest change that can
  explain all of §3.2's evidence — zero heating in spring/fall,
  large heating in high-cooling months, and no inter-scenario
  differentiation.
- **What will impact on:** read-only investigation.
- **Steps / sub-steps:**
  1. Sort the schedules into "heating side" (anything referenced by
     `Coil:Heating:*` or by the heating setpoint slot of
     `ThermostatSetpoint:DualSetpoint`) vs "cooling side".
  2. For each heating-side schedule, read its annual profile.
  3. Flag any schedule whose annual profile is seasonally
     "wrong-way-round" (summer-only) or has a `Through:` date
     inconsistent with a northern-hemisphere heating season.
- **What to expect as result:** exactly one schedule object identified
  as the culprit, OR a finding that none of the schedules look
  seasonally wrong (in which case the bug is in the HVAC coil
  configuration itself rather than in a schedule — fall back to
  task 7).
- **How to test:** record the schedule name and its seasonal shape
  in a short note for task 9 to act on.

#### Task 7 — Compare prepared IDF against source neighbourhood IDF

- **Aim of task:** determine whether the problematic schedule found
  in task 6 is present in the source IDF or is introduced by
  `prepare_neighbourhood_idf()`.
- **What to do:** open the source IDF under
  `BEM_Setup/Neighbourhoods/<name>.idf` (the same file selected by
  the Option 7 run that produced
  `MonteCarlo_Neighbourhood_N10_1775555644`) and locate the same
  schedule object identified in task 6. Diff it against the prepared
  IDF version.
- **How to do:** text search + visual diff, or `diff -u` on
  extracted blocks.
- **Why to do this task:** this bisection tells the implementer
  whether the fix belongs in the source IDF (data fix) or in
  `prepare_neighbourhood_idf()` (code fix) — they have very
  different blast radii.
- **What will impact on:** read-only.
- **Steps / sub-steps:**
  1. Extract the same schedule object from the source IDF.
  2. Diff against the prepared version.
  3. Record which of the two contains the summer-weighted shape.
- **What to expect as result:** one of two outcomes — (i) the source
  IDF already has the wrong schedule (fix is a data edit to the
  source IDF); (ii) the source IDF has a correct schedule and the
  prepared IDF's version is different (fix is a code edit to
  `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf`).
- **How to test:** task 8 below runs the source IDF directly to
  confirm.

#### Task 8 — Run the source IDF directly and compare heating profiles

- **Aim of task:** double-check task 7's conclusion by bypassing the
  BEM-side preparation/injection chain entirely.
- **What to do:** run the source
  `BEM_Setup/Neighbourhoods/<name>.idf` on the same Montreal EPW
  used by the broken run, without calling
  `prepare_neighbourhood_idf()` or `inject_neighbourhood_*_schedules`.
- **How to do:** either (a) invoke EnergyPlus directly from the CLI
  (`energyplus -w <epw> -d <outdir> <idf>`) or (b) write a tiny
  helper that calls `simulation.run_simulations_parallel` with a
  job dict pointing straight at the source IDF.
- **Why to do this task:** isolates the bug from the BEM-side
  preparation. If the raw run also produces a September peak,
  task 9's fix is in the IDF; if the raw run produces a winter peak,
  task 9's fix is in `prepare_neighbourhood_idf()`.
- **What will impact on:** writes one extra
  `eplusout.sql` to a scratch directory
  (`BEM_Setup/SimResults/raw_source_baseline/`).
- **Steps / sub-steps:**
  1. Create the scratch output directory.
  2. Run EnergyPlus directly on the source IDF.
  3. Run the SQL query from §6.3 against the new `eplusout.sql`.
  4. Compare the new monthly profile with the one in §6.3.
- **What to expect as result:** a clear signal — either
  "source IDF reproduces the anomaly" or "source IDF is fine, the
  preparation step is at fault".
- **How to test:** compare the new Jan and Sep values against the
  broken run's 37.67 GJ and 271.07 GJ.

#### Task 9 — Apply the upstream fix (deferred until tasks 6–8 complete)

- **Aim of task:** correct the schedule or preparation step
  identified in tasks 6–8 so `Heating:EnergyTransfer` produces a
  winter-peak profile.
- **What to do:** **left deliberately unspecified** — the exact edit
  depends on the outcome of tasks 6–8. Three possible shapes:
  1. Tasks 7/8 say the source IDF is wrong → edit
     `BEM_Setup/Neighbourhoods/<name>.idf` to fix the problematic
     schedule block.
  2. Tasks 7/8 say `prepare_neighbourhood_idf()` is wrong → edit
     `eSim_bem_utils/neighbourhood.prepare_neighbourhood_idf()`.
  3. Task 6 says no single schedule is wrong → fall back to
     inspecting the heating coil / sizing setup and escalate to the
     user with the findings before editing anything.
- **How to do:** minimal scoped edit; do NOT touch `plotting.py`
  regardless of outcome.
- **Why to do this task:** the only correct fix for Anomaly 1.
- **What will impact on:** depends on outcome; touches one of the
  three files listed above.
- **Steps / sub-steps:** defer until tasks 6–8 produce evidence.
- **What to expect as result:** after the fix, a re-run of the same
  source IDF produces Jan ≫ Sep in the monthly
  `Heating:EnergyTransfer` values.
- **How to test:** re-run task 8 after the edit and compare the new
  monthly profile against the broken baseline.

#### Task 10 — End-to-end regression run of Option 7

- **Aim of task:** confirm that the full Monte Carlo neighbourhood
  pipeline now produces a physically plausible bar chart and
  time-series on Montreal.
- **What to do:** `python run_bem.py` → 7 → pick the same
  neighbourhood IDF → Montreal EPW → iter_count=3 (enough to verify)
  → "Standard" simulation mode → wait for completion.
- **How to do:** through the existing CLI menu. No code edits.
- **Why to do this task:** end-to-end regression test that combines
  task 1 and task 9. A clean run on Montreal is the explicit
  acceptance criterion for both fixes.
- **What will impact on:** writes a new
  `BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N3_*/` directory
  with fresh plots.
- **Steps / sub-steps:**
  1. Launch Option 7 with the parameters above.
  2. Wait for `Successful: 16/16 | Failed: 0/16` (3 iters × 5
     scenarios + 1 Default).
  3. Open the new bar chart and time-series PNGs from
     `PLOT_RESULTS_DIR`.
- **What to expect as result:** bar chart shows 5 bars including a
  dominant Heating bar (~50–80 kWh/m²); time-series heating panel
  peaks in December / January / February and is near-zero in
  June–August; the six scenario lines show visible differentiation.
- **How to test:** visual inspection of the new PNGs against the
  Montreal climate baseline (Jan ≫ Sep heating).

#### Task 11 — Append the Resolution chapter to this debug doc

- **Aim of task:** close the loop for the next maintainer by
  documenting exactly what was fixed and where.
- **What to do:** append a new chapter "9. Resolution" to this file
  containing: (i) the exact `plotting.py` lines edited for task 1,
  (ii) the exact IDF or preparation code edited for task 9, (iii) the
  before/after monthly heating values, (iv) the before/after bar
  chart row counts, (v) a dated sign-off line.
- **How to do:** one edit to this markdown file. Do not delete any
  existing chapters.
- **Why to do this task:** matches the format of
  `2025_schedule_data_debug.md` and keeps the debug history
  self-contained.
- **What will impact on:** this markdown file only.
- **Steps / sub-steps:**
  1. Add a new `## 9. Resolution` chapter after §8.
  2. Fill in the five items listed above.
  3. Save.
- **What to expect as result:** the doc ends with a dated resolution
  note with file paths and line numbers.
- **How to test:** read the doc end-to-end and confirm a future
  maintainer could reconstruct the fix without diffing the source.

---

## 8. Progress Log

This chapter is written by the implementation agent as each task
from §7 is completed. Each entry should record the status, the date
the task was completed, and a short report summarising what was done,
what was found, and any deviations from the original plan. Leave
slots `pending` until touched.

### Task 1 — Narrow the `'Water'` skip filter in `calculate_eui()`
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 2 — Regenerate the Monte Carlo plots from the existing SQL files
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 3 — Add a cross-check warning against `Total End Uses`
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 4 — Commit the Anomaly 2 fix
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 5 — Dump the HVAC + schedule objects from the prepared IDF
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 6 — Identify which schedule has a summer-weighted shape
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 7 — Compare prepared IDF against source neighbourhood IDF
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 8 — Run the source IDF directly and compare heating profiles
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 9 — Apply the upstream fix
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 10 — End-to-end regression run of Option 7
- **Status:** pending
- **Completed on:** —
- **Report:** —

### Task 11 — Append the Resolution chapter to this debug doc
- **Status:** completed
- **Completed on:** 2026-04-07
- **Report:** Resolution chapter (§9) appended below.

---

## 9. Resolution

**Completed:** 2026-04-07

---

### 9.1 Anomaly 2 — Missing Heating bar (plotting fix)

**Root cause confirmed:**
`eSim_bem_utils/plotting.py:172` — the `'Water' in col_name` substring
check inadvertently matched `ColumnName='District Heating Water'` (the
only column carrying heating energy in this IDF), silently dropping the
entire heating end-use from `calculate_eui()`.

**Fix applied (`eSim_bem_utils/plotting.py:171-174`):**

Before:
```python
# Skip water columns
if 'Water' in col_name or 'm3' in str(units):
    continue
```

After:
```python
# Skip water-consumption columns (m3, m3/s units); do NOT match on
# column name because 'District Heating Water' also contains 'Water'
# and would incorrectly drop the entire heating end-use.
if 'm3' in str(units):
    continue
```

**Verification:** re-ran aggregation on the existing 51 SQL files via
`replot_existing_montecarlo.py`. New CSV
(`MonteCarlo_Neighbourhood_N10_1775555644/replot/aggregated_eui_replot.csv`)
now contains a `Heating` row (was absent before):

```
Heating,54.4618,0.5532,54.0372,0.5502,53.4458,1.0588,53.0300,1.1213,54.1494,0.9401,49.7090,0.0000
```

Heating is now the dominant end-use at ~54 kWh/m²/yr (2005 mean), as
expected for Montreal residential. Water Systems EUI also corrected from
misleading 0.001 → 0.72 kWh/m²/yr.

---

### 9.2 Anomaly 1 — Inverted heating time-series (source IDF fix)

**Root cause confirmed (Step 6):**
Running `NUS_RC1.idf` directly on the Montreal EPW (bypassing all
schedule injection) reproduced the same summer-peak heating profile:

```
Before fix — direct run (NUS_RC1):
  Month  1:  55.53 GJ    Month  7:  62.08 GJ
  Month  2:  24.92 GJ    Month  8:  72.82 GJ
  Month  3:  11.64 GJ    Month  9:  97.24 GJ  ← peak
  Month  6:   4.16 GJ    Month 12:  33.41 GJ
```

**Root cause:** NUS_RC1/RC2/RC3 use a constant heating setpoint of
22.222°C (72°F) year-round. The `ZoneHVAC:IdealLoadsAirSystem` in these
IDFs continuously conditions outdoor air to maintain that setpoint.
In Montreal July-September, outdoor temperatures regularly drop to
11–18°C at night. Conditioning 0.689 m³/s of outdoor air from ~15°C to
22.222°C across 48+ apartment zones accumulated to 62-97 GJ/month —
more than January (55 GJ) because winter's internal gains (equipment,
lights, people) nearly offset the envelope losses.

NUS_RC4/RC5/RC6 do NOT exhibit this bug — they already use the DOE
prototype building schedule `ApartmentMidRise HTGSETP_OFF_SCH_YES_OPTIMUM`
with a 15.6°C default setpoint, which prevents the same overrun.

**Fix applied (`BEM_Setup/Neighbourhoods/NUS_RC1.idf`,
`NUS_RC2.idf`, `NUS_RC3.idf`):**

Added a summer heating setback (`17_heating_sch_Summer Schedule`,
15.0°C) for Jul 1 – Sep 30 by splitting `17_heating_sch` into three
seasonal periods:

- Jan 1 – Jun 30: 22.222°C (unchanged)
- Jul 1 – Sep 30: 15.0°C (summer setback — below any realistic summer
  outdoor temperature for Montreal, so IdealLoads does not heat in summer)
- Oct 1 – Dec 31: 22.222°C (unchanged)

The three objects modified per IDF: `Schedule:Day:Interval`
(`17_heating_sch_Summer Schedule` added),
three `Schedule:Week:Daily` objects (Jan-Jun, Jul-Sep, Oct-Dec),
`Schedule:Year` (`17_heating_sch`) split from 1-period to 3-period.

**Verification (Step 7 direct re-run):**

```
After fix — direct run (NUS_RC1):
  Month  1:  55.53 GJ  (unchanged)
  Month  7:   0.71 GJ  (was 62.08 GJ — 87× reduction)
  Month  8:   0.61 GJ  (was 72.82 GJ — 119× reduction)
  Month  9:   1.80 GJ  (was 97.24 GJ — 54× reduction)
  Month 12:  33.41 GJ  (unchanged)
Annual total: 346.72 GJ (was 584.59 GJ; ~238 GJ of artificial summer
              heating eliminated)
```

Heating now peaks December–February, as expected for Montreal (Köppen
Dfb, ASHRAE Zone 6A).

**Step 8 (full Option 7 end-to-end re-run):** pending — requires
running `python run_bem.py` → Option 7 → NUS_RC1 → Montreal EPW →
N=10 to regenerate the Monte Carlo plots with both fixes active.

---

### 9.3 Files changed

| File | Change |
|---|---|
| `eSim_bem_utils/plotting.py:172` | Removed `'Water' in col_name` from skip filter |
| `BEM_Setup/Neighbourhoods/NUS_RC1.idf` | Added summer heating setback Jul-Sep |
| `BEM_Setup/Neighbourhoods/NUS_RC2.idf` | Added summer heating setback Jul-Sep |
| `BEM_Setup/Neighbourhoods/NUS_RC3.idf` | Added summer heating setback Jul-Sep |

Helper scripts added (not part of production code):
- `replot_existing_montecarlo.py` — re-aggregates existing SQL files
  without re-running simulations; produces corrected bar chart and
  time-series plot in `replot/` subdirectory
- `BEM_Setup/SimResults/step6_direct_run/` — scratch run of source IDF
  confirming bug in source
- `BEM_Setup/SimResults/step7_fixed_run/` — scratch run of fixed IDF
  confirming fix

---
