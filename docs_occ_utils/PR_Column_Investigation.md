# Investigation Report: Missing 'PR' Column in BEM Schedules

## Issue
The `PR` (Province/Region) column is present in the `Profile Matching` step but is missing from the final `06CEN05GSS_BEM_Schedules.csv` output.

## Tracing the Column

1.  **Step 2: Profile Matching (`06CEN05GSS_ProfileMatcher.py`)**
    *   The column `PR` is successfully read from the Census data.
    *   In the `generate_full_expansion` function (lines 295+), `PR` is included in the `carry_vars` list:
        ```python
        carry_vars = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "PR", "TOTINC", ...]
        ```
    *   It is renamed to `Census_PR` when collecting episodes:
        ```python
        ep_wd[f'Census_{var}'] = agent[var]  # Becomes Census_PR
        ```
    *   **Result:** The column exists as `Census_PR` in the output `06CEN05GSS_Full_Schedules.csv`.

2.  **Step 3: Household Aggregation (`06CEN05GSS_HH_aggregation.py`)**
    *   The script reads `06CEN05GSS_Full_Schedules.csv`.
    *   It aggregates time-varying data but preserves static metadata for each agent:
        ```python
        meta = person_data.iloc[0].drop(labels=time_varying_cols, errors='ignore')
        ```
    *   Since `Census_PR` is not in `time_varying_cols`, it is preserved.
    *   **Result:** The column exists as `Census_PR` in `06CEN05GSS_Full_Aggregated.csv`.

3.  **Step 4: BEM Conversion (`06CEN05GSS_occToBEM.py`)**
    *   **The Drop Happens Here.**
    *   In the `process_households` method, the script explicitly filters which static columns to carry over to the final schedule:
        ```python
        # Line 113
        target_res_cols = ['DTYPE', 'BEDRM', 'CONDO', 'ROOM', 'REPAIR']
        ```
    *   The script iterates specifically through this list to extract values. Any column not in this list (like `PR` or `Census_PR`) is ignored and excluded from the final DataFrame.

## Solution

To include the `PR` column in the final output `06CEN05GSS_BEM_Schedules.csv`, you need to modify `06CEN05GSS_occToBEM.py`.

### Required Change

In `06CEN05GSS_occToBEM.py`, verify the `target_res_cols` list in the `process_households` method and add `'PR'` to it.

**File:** `occ_utils/06CEN05GSS/06CEN05GSS_occToBEM.py`
**Location:** Inside `process_households` method (around line 113)

```python
# MODIFY this line:
target_res_cols = ['DTYPE', 'BEDRM', 'CONDO', 'ROOM', 'REPAIR', 'PR']
```

**Why this works:**
The script already contains logic to automatically look for a `Census_` prefix if the distinct column name is not found:

```python
if col in group.columns:
    val = group[col].iloc[0]
elif f'Census_{col}' in group.columns:
    val = group[f'Census_{col}'].iloc[0]
```

By simply adding `'PR'` to the list, the script will find `Census_PR` in the input data and include it in the output as `PR`.
