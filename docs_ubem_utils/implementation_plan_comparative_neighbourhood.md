# Option 5: Comparative Neighbourhood Simulation

## Goal
Add a new menu option to run 4 parallel neighbourhood simulations comparing schedules from 2005, 2015, 2025, and Default (no schedule injection).

## Key Differences from Single-Building Comparative (Option 3)

| Aspect | Option 3 (Single) | Option 5 (Neighbourhood) |
|--------|-------------------|--------------------------|
| Input IDF | Single building | Multi-building neighbourhood |
| Schedules | 1 household per scenario | 24+ households per scenario |
| Preparation | `inject_schedules()` | `prepare_neighbourhood_idf()` + `inject_neighbourhood_schedules()` |
| Matching | Match by hhsize | Match all 24 buildings consistently |

## Proposed Changes

---

### [NEW] `option_comparative_neighbourhood_simulation()` in [main.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/bem_utils/main.py)

**Workflow:**
1. Select Neighbourhood IDF (from `NEIGHBOURHOODS_DIR`)
2. Select Weather File → Infer region
3. Load schedules from all 3 CSVs (2005, 2015, 2025) with region filter
4. Get building count from IDF
5. For each scenario (2025/2015/2005/Default):
   - Create scenario subdirectory
   - `prepare_neighbourhood_idf()` → explode master objects
   - `inject_neighbourhood_schedules()` (or skip for Default) → assign per-building schedules
   - Add job to parallel queue
6. Run all 4 simulations in parallel using `run_simulations_parallel()`
7. Extract EUI results from each scenario
8. Generate comparative plots (EUI bar chart + time-series)

---

### [MODIFY] Menu in [main.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/eSim/bem_utils/main.py)

Add Option 5 to menu:
```
5. Comparative neighbourhood simulation (2025/2015/2005/Default)
```

Renumber existing Option 5 (Visualize) → Option 6

---

## Household Matching Strategy

For consistency across scenarios, we need the **same 24 buildings** to have **similar household profiles**.

**Approach:** Match by household size distribution
1. Load 2025 schedules first → randomly select 24 households
2. Record hhsize for each building index: `[2, 3, 4, 2, ...]`
3. For 2015/2005, find households matching those hhsizes
4. For Default, skip schedule injection entirely

---

## Verification Plan

### Automated Tests
```bash
python3 run_bem.py
# Select Option 5
# Select NUs_RC1.idf
# Select Toronto weather
# Confirm 4 parallel simulations run
# Verify plots generated in SimResults_Plotting/
```

### Expected Output
- 4 scenario folders: `2025/`, `2015/`, `2005/`, `Default/`
- Comparative EUI bar chart comparing all 4 scenarios
- Time-series subplot showing monthly patterns

---

## Estimated Implementation: ~150 lines of code

---

## Implementation Corrections (Applied)

The following corrections were made during implementation to ensure consistency with Option 3:

### 1. Dwelling Type Filter Added
- Added step to prompt user for dwelling type selection (SingleD, MidRise, etc.)
- Filter applied to `load_schedules()` calls for all years
- Matches Option 3's workflow

### 2. Time-Series Plot Added
- Added extraction of meter data using `get_meter_data()`
- Added call to `plot_comparative_timeseries_subplots()` 
- Generates monthly kWh/m² comparison across all 4 scenarios

### 3. Default Case Handling Fixed
- **Before:** Used `prepare_neighbourhood_idf()` which created placeholder schedules with no data
- **After:** Uses `idf_optimizer.prepare_idf_for_simulation()` to keep original IDF schedules intact
- Now matches Option 3's behavior - true baseline comparison
