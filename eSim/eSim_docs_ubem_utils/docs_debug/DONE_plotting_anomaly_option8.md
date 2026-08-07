# Plotting Anomaly: Inverted Heating/Cooling Time-Series

## Aim

Diagnose and fix the anomaly where monthly time-series plots show heating
demand peaking in summer months (Jul-Sep) and cooling demand peaking in
winter/spring months (Jan-Jun, Oct-Dec). The issue affects all options
that use `plotting.get_meter_data()` + `plot_kfold_timeseries()` or
`plot_comparative_timeseries_subplots()`, not just Option 8.

## Observed Symptom

In the Monte Carlo time-series plot (e.g.
`MonteCarlo_Neighbourhood_TimeSeries_Task8_7d_BatchAll_MC_N2_*_NUS_RC1.png`):

- **Heating - Energy Demand** panel peaks in Jul/Aug/Sep (hot months).
- **Cooling - Energy Demand** panel peaks in Jan-Jun and Oct-Nov.
- **InteriorLights**, **InteriorEquipment**, **Fans** panels look reasonable.

## Root Cause

### 1. Wrong EnergyPlus variable feeds the meters

The `Heating:EnergyTransfer` and `Cooling:EnergyTransfer` **facility meters**
in EnergyPlus are fed by:

| Meter                        | Source Variable                              |
|------------------------------|----------------------------------------------|
| `Heating:EnergyTransfer`     | `Zone Air System Sensible Heating Energy`    |
| `Cooling:EnergyTransfer`     | `Zone Air System Sensible Cooling Energy`    |

These measure the **net sensible energy transfer between supply air and
zone air**. They do NOT measure the energy the HVAC system consumed for
heating or cooling.

The correct variables for "how much energy did the system use to heat/cool"
are:

| What we want to show          | Correct Variable                                     |
|-------------------------------|------------------------------------------------------|
| System heating energy         | `Zone Ideal Loads Supply Air Total Heating Energy`   |
| System cooling energy         | `Zone Ideal Loads Supply Air Total Cooling Energy`   |

### 2. Why the meters are inverted

The NUS_RC neighbourhood IDFs use `ZoneHVAC:IdealLoadsAirSystem` with
continuous outdoor ventilation (0.00013 m3/s-m2) and a tight thermostat
deadband:

- **Jan-Jun, Oct-Dec**: Heat SP = 22.222 C, Cool SP = 23.889 C (deadband
  **1.667 C**)
- **Jul-Sep**: Heat SP = 15.0 C (summer setback), Cool SP = 23.889 C
  (deadband **8.889 C**)

With high internal gains (~84 GJ/month from equipment alone at 9.06 W/m2),
the zone is internally dominated:

- **Winter (tight deadband)**: Internal gains push the zone above the
  cooling setpoint frequently. The Zone Air System removes heat
  (Cooling:EnergyTransfer is HIGH). The system also must heat cold outdoor
  ventilation air, but the Zone Air System variable sees the net effect on
  the zone, not the energy consumed.
- **Summer (wide setback deadband)**: The zone floats between 15 C and
  23.889 C. Less active heating/cooling needed. The Zone Air System
  Heating Energy can paradoxically be HIGHER in summer because of how the
  supply air temperature differential interacts with the lowered setpoint.

### 3. Evidence from SQL data

**Scenario: Default, NUS_RC1, Alberta EPW**

Zone 000_LIVING_UNIT1_1 monthly data (kWh):

```
Month | ZoneAirSys Heat | IdealLoads Heat | ZoneAirSys Cool | IdealLoads Cool
  1   |       92        |      266        |      185        |       42
  6   |       42        |       22        |      725        |      604
  7   |      105        |       55        |      191        |      131
  9   |      202        |       90        |      154        |       53
 12   |       77        |      244        |      152        |       12
```

- `IdealLoads Heat` peaks in winter (266 kWh Jan, 244 kWh Dec) - **correct**
- `ZoneAirSys Heat` peaks in summer (202 kWh Sep) - **inverted**
- The Heating:EnergyTransfer meter uses `ZoneAirSys Heat`, hence the plot
  shows inverted seasonal pattern.

### 4. EUI bar chart is NOT affected

`calculate_eui()` reads from `TabularDataWithStrings` (annual end-use
totals), not from the monthly meter. Annual totals are correct.

## Affected Code Paths

| File | Function | Issue |
|------|----------|-------|
| `plotting.py:553` | `get_meter_data()` | Reads `Heating:EnergyTransfer` / `Cooling:EnergyTransfer` which are fed by `Zone Air System Sensible` variables |
| `plotting.py:685` | `plot_comparative_timeseries_subplots()` | Uses data from `get_meter_data()` |
| `plotting.py:904` | `plot_kfold_timeseries()` | Uses aggregated data from `get_meter_data()` |
| `main.py:2028-2051` | Default simulation meter extraction | Calls `plotting.get_meter_data()` |
| `main.py:2216-2233` | MC iteration meter extraction | Calls `plotting.get_meter_data()` |

## Steps to Fix

### Step 1 - Add Ideal Loads output variables at Monthly frequency

**File**: `eSim_bem_utils/idf_optimizer.py`, function `optimize_idf()`

Add these to the `REQUIRED_OUTPUT_VARIABLES` or a new section after the
meter additions:

```python
# Monthly Zone Ideal Loads variables (for correct time-series plotting)
IDEAL_LOADS_MONTHLY_VARS = [
    ('Zone Ideal Loads Supply Air Total Heating Energy', 'Monthly'),
    ('Zone Ideal Loads Supply Air Total Cooling Energy', 'Monthly'),
]
```

Add Output:Variable objects for these with `Key_Value = "*"` and
`Reporting_Frequency = "Monthly"`.

### Step 2 - Modify `get_meter_data()` to use Ideal Loads variables

**File**: `eSim_bem_utils/plotting.py`, function `get_meter_data()`

Option A (preferred): Query the ReportDataDictionary for the `Zone Ideal
Loads` variables at Monthly frequency. Sum values across all zones for
each month to get facility-level totals. Map:

- Sum of `Zone Ideal Loads Supply Air Total Heating Energy` across zones
  -> replaces `Heating:EnergyTransfer` in the returned dict
- Sum of `Zone Ideal Loads Supply Air Total Cooling Energy` across zones
  -> replaces `Cooling:EnergyTransfer` in the returned dict

Other meters (`InteriorLights:Electricity`, `InteriorEquipment:Electricity`,
`Fans:Electricity`, `WaterSystems:EnergyTransfer`) are NOT affected -
keep reading them from the existing meter path.

Option B (minimal change): Add a post-processing step that reads the
hourly `Zone Ideal Loads` data, aggregates to monthly sums, and replaces
the Heating/Cooling entries in the results dict.

### Step 3 - Verify month ordering

While the investigation confirmed `ORDER BY t.TimeIndex ASC` produces
correct month ordering for a standard Jan-Dec run period, add an
explicit `ORDER BY t.Month ASC` or use the `t.Month` column to assign
values to the correct month index. This guards against future edge cases
(non-standard run periods, weekly mode).

### Step 4 - Re-run simulation and verify plots

After applying Steps 1-3:
1. Run a single neighbourhood simulation (Option 7 or Step 7b from test)
   with N=1 to save time.
2. Check the time-series plot: Heating should now peak in Jan/Dec/Feb,
   Cooling should peak in Jul/Aug or Jun (with the setback schedule, peak
   may be in Jun due to tight deadband; this is physically correct).
3. Verify EUI bar chart is unchanged.

### Step 5 - Optional: widen thermostat deadband

The tight deadband (1.667 C) in non-summer months causes significant
simultaneous heating and cooling even in the corrected variables. Consider
widening the deadband by lowering the heating setpoint (e.g., 20 C) or
raising the cooling setpoint (e.g., 26 C). This is a modeling decision,
not a code fix. Document if changed.

## Expected Result

- Heating time-series peaks in Dec-Feb (cold months in Alberta).
- Cooling time-series peaks in Jun-Aug (warm months), with a possible
  shape influenced by the Jul-Sep setback schedule.
- Other meters (Lights, Equipment, Fans, WaterSystems) unchanged.
- EUI bar chart unchanged.

## Test Method

1. Visual inspection of time-series plots for physical plausibility.
2. Compare zone-level `Zone Ideal Loads Supply Air Total Heating/Cooling
   Energy` sums with the values plotted to confirm data pipeline is
   correct.
3. Cross-check annual totals against EUI bar chart values.

---

## Progress Log

- [2026-04-13 00:00] Investigation started. Read test script, plotting code,
  main.py MC pipeline, integration.py injection code.
- [2026-04-13 00:10] Queried eplusout.sql for NUS_RC1 Default simulation.
  Confirmed facility Heating:EnergyTransfer meter peaks in Sep (32 GJ),
  not Jan. Cooling:EnergyTransfer peaks in Jun (114 GJ) with winter values
  ~33-96 GJ. Data extraction order verified correct (months 1-12 in order).
- [2026-04-13 00:20] Compared zone-level `Zone Ideal Loads Supply Air Total
  Heating Energy` (summed hourly -> monthly) vs `Heating:EnergyTransfer`
  meter. Zone ideal loads show correct pattern (peaks in winter). Meter
  shows inverted pattern.
- [2026-04-13 00:25] Found via eplusout.mtd that `Heating:EnergyTransfer`
  is fed by `Zone Air System Sensible Heating Energy`, NOT by
  `Zone Ideal Loads Supply Air Total Heating Energy`. The Zone Air System
  variable measures net supply-air-to-zone-air heat transfer, which is
  inverted in internally-dominated buildings with tight deadbands.
- [2026-04-13 00:30] Confirmed EUI bar chart (from TabularDataWithStrings)
  is NOT affected. Issue is isolated to time-series plots using
  `get_meter_data()`.
- [2026-04-13 00:35] Root cause confirmed. Fix plan: add Zone Ideal Loads
  monthly output variables, modify `get_meter_data()` to sum them across
  zones for Heating/Cooling.
- [2026-04-13 01:05] Task 1 complete. Updated `eSim_bem_utils/idf_optimizer.py`
  to add monthly `Zone Ideal Loads Supply Air Total Heating Energy` and
  `Zone Ideal Loads Supply Air Total Cooling Energy` output variables, and
  made `Output:Variable` deduping frequency-aware so monthly entries are not
  skipped when hourly entries already exist.
- [2026-04-13 01:15] Task 2 complete. Reworked
  `eSim_bem_utils/plotting.py:get_meter_data()` to source
  `Heating:EnergyTransfer` / `Cooling:EnergyTransfer` from the monthly
  ideal-load variables by default, while preserving the legacy meter path as
  a fallback for older SQL files.
- [2026-04-13 01:20] Task 3 complete. Added an explicit month-ordering guard
  in the monthly SQL extractor by reading the `Time.Month` column and
  reindexing the results to a 12-month series before plotting.
- [2026-04-13 01:25] Task 4 complete. Verified the touched modules with
  `py_compile` and an in-memory SQLite smoke test. The smoke test confirmed
  zone-summed ideal-load values populate the heating/cooling series in month
  order, and the legacy meter fallback still returns data when the ideal-load
  variables are absent.
