# 11CEN10GSS Pipeline – Structured Sub-Tasks

**Reference plan**: `docs_pipelines/11CEN10GSS_plan.md`
**Reference pipelines**: `eSim_occ_utils/06CEN05GSS/` and `eSim_occ_utils/16CEN15GSS/`
**Target folder**: `eSim_occ_utils/11CEN10GSS/`
**Output folder**: `0_Occupancy/Outputs_11CEN10GSS/`

All paths below are relative to the project root: `/Users/orcunkoraliseri/Desktop/Postdoc/occModeling/`

### Progress snapshot

| Task | Status |
|------|--------|
| T0.1 – T0.3 (Episode preprocessing) | ✅ Done — `out10EP_ACT_PRE_coPRE.csv` created (283,287 rows) |
| T1.1 – T1.9 (Alignment script) | ✅ Done — script implemented and executed |
| TF.1 Fix `harmonize_pr()` for Census 2011 province codes | ✅ Fixed in `11CEN10GSS_alignment.py` |
| TF.2 Fix duplicate `DDAY`/`DDAY.1` column | ✅ Fixed in `11CEN10GSS_alignment.py` |
| TF.3 Verify `harmonize_marsth()` | ✅ Verified against `cen11.sps` and documented |
| TF.4 Verify `harmonize_totinc()` refusal codes | ✅ Verified against `GSSMain_2010_syntax.SPS` and filtered |
| TF.5 Re-run alignment | ✅ Re-run complete |
| T2.1 – T2.3 (Profile Matching) | ✅ Done — `11CEN10GSS_ProfileMatcher.py` created |
| T3.1 – T3.3 (HH Aggregation) | ✅ Done — `11CEN10GSS_HH_aggregation.py` created |
| T4.1 – T4.3 (BEM Conversion) | ✅ Done — `11CEN10GSS_occToBEM.py` created |
| T5.1 (`__init__.py`) | ✅ Done |
| **TD.1 Step 0 bug fixes applied to code** | ✅ Done — `occACT`, `start`, `end`, `Spouse`, `Children`, `otherInFAMs` added to `step0.py`; ROOM filter added to `alignment.py` (2026-03-31 17:36) |
| **TD.2 Re-run full pipeline from step0 after bug fixes** | ⬜ Not started — all current outputs predate the step0 fixes |

**Critical note (2026-04-01):** The code fixes in `step0.py` (17:36) were applied 5+ hours after `out10EP_ACT_PRE_coPRE.csv` (12:17) and all downstream outputs (alignment 12:46, ProfileMatching 12:49, HH_aggregation 13:11, occToBEM 13:18) were generated. The existing output files are stale and still contain all three bugs from `debug_11CEN10GSS.md`. TD.2 must be completed before these outputs can be used.

---

## Step 0 — GSS 2010 Episode Preprocessing (Pre-requisite)

These tasks produce the processed episode CSV that Step 1 depends on. Run once before the main pipeline.

---

### T0.1 — Parse GSS 2010 Episode DAT File

**What to do**
Read the raw fixed-width episode data file `C24EPISODE_withno_bootstrap.DAT` using its SPSS syntax schema and convert it to a pandas DataFrame.

**How to do it**
1. Open `0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS`.
2. Parse the `DATA LIST` block to extract variable names and column positions (start–end as 0-indexed tuples). The format is `VARNAME  XXXXX - XXXXX` where numbers are 1-indexed.
3. Use `pd.read_fwf()` with the extracted `colspecs` and `names` to read `C24EPISODE_withno_bootstrap.DAT`.
4. Extract only these columns: `RECID`, `EPINO`, `DDAY`, `ACTCODE`, `STARTMIN`, `ENDMIN`, `DURATION`, `PLACE`, `ALONE`, `SPOUSE`, `CHILDHSD`, `MEMBHSD`.
5. Rename `RECID` → `occID`.

**Expected result**
A DataFrame with ~300,000–500,000 rows (one row per episode) and columns: `occID`, `EPINO`, `DDAY`, `ACTCODE`, `STARTMIN`, `ENDMIN`, `DURATION`, `PLACE`, `ALONE`, `SPOUSE`, `CHILDHSD`, `MEMBHSD`.

**How to test**
- `len(df) > 100000` — file is not empty
- `df['occID'].nunique() > 10000` — at least 10,000 unique respondents
- `df['DDAY'].dropna().isin([1,2,3,4,5,6,7]).all()` — day codes are valid
- `df['DURATION'].min() >= 0` — no negative durations

---

### T0.2 — Compute PRE and coPRE Columns

**What to do**
Add two derived columns to the episode DataFrame:
- `PRE` (presence at home): binary flag indicating the person was at home during the episode
- `coPRE` (co-presence): binary flag indicating at least one other household member was present

**How to do it**
1. For `PRE`: check the `PLACE` column. In GSS 2010 Cycle 24, `PLACE == 1` means "at home / respondent's home". Set `PRE = 1` where `PLACE == 1`, else `PRE = 0`.
   - Verify this by checking the codebook section in `C24_Episode File_SPSS_withno_bootstrap.SPS` for the `PLACE` value labels. Look for the label that means "respondent's home" (typically code 1 in all GSS cycles).
2. For `coPRE`: set `coPRE = 1` where any of `SPOUSE`, `CHILDHSD`, or `MEMBHSD` equals 1, else `coPRE = 0`.
   ```python
   df['PRE'] = (df['PLACE'] == 1).astype(int)
   df['coPRE'] = ((df['SPOUSE'] == 1) | (df['CHILDHSD'] == 1) | (df['MEMBHSD'] == 1)).astype(int)
   ```

**Expected result**
The DataFrame now has two new binary columns `PRE` and `coPRE`. Both contain only 0 and 1. `PRE` should be 1 for roughly 30–50% of episodes (people spend a lot of time at home).

**How to test**
- `df['PRE'].isin([0, 1]).all()` — no unexpected values
- `df['coPRE'].isin([0, 1]).all()` — no unexpected values
- `df['PRE'].mean()` is between 0.25 and 0.65 — sanity check on home presence rate

---

### T0.3 — Save Processed Episode CSV

**What to do**
Save the processed episode DataFrame as `out10EP_ACT_PRE_coPRE.csv` in the GSS 2010 episode folder.

**How to do it**
```python
output_path = Path("0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/out10EP_ACT_PRE_coPRE.csv")
df.to_csv(output_path, index=False)
```

**Expected result**
File `out10EP_ACT_PRE_coPRE.csv` exists with columns: `occID`, `EPINO`, `DDAY`, `ACTCODE`, `STARTMIN`, `ENDMIN`, `DURATION`, `PLACE`, `ALONE`, `SPOUSE`, `CHILDHSD`, `MEMBHSD`, `PRE`, `coPRE`.

**How to test**
- File exists at the specified path
- `pd.read_csv(output_path).columns.tolist()` contains all expected columns
- Compare column list to `out05EP_ACT_PRE_coPRE.csv` (GSS 2005 equivalent) — should match

---

## Step 1 — Alignment (`11CEN10GSS_alignment.py`)

Create the file `eSim_occ_utils/11CEN10GSS/11CEN10GSS_alignment.py`. Tasks T1.1 through T1.9 build up the complete script in order. The reference implementation is `eSim_occ_utils/16CEN15GSS/16CEN15GSS_alignment.py`.

---

### T1.1 — Script Skeleton, Imports, and Column Constants

**What to do**
Create `eSim_occ_utils/11CEN10GSS/11CEN10GSS_alignment.py` with the module docstring, all imports, and the two column-mapping constants `COLS_MAIN_10` and `RENAME_MAP_10`.

**How to do it**
1. Copy the import block from `16CEN15GSS_alignment.py` (same libraries: `pandas`, `pathlib`, `os`, `math`, `re`, `uuid`, `matplotlib`, `seaborn`).
2. Add the module docstring:
   ```
   11CEN10GSS Alignment Module
   Reads GSS 2010 (Cycle 24) data, merges with demographics, and aligns with
   Census 2011 for occupancy modeling.
   ```
3. Define `COLS_MAIN_10`:
   ```python
   COLS_MAIN_10 = [
       'RECID', 'PRV', 'HSDSIZEC', 'AGEGR10', 'SEX', 'MARSTAT',
       'LANHSDC', 'ACT7DAYS', 'LUC_RST', 'INCM', 'DVTDAY', 'WGHT_PER',
   ]
   ```
4. Define `RENAME_MAP_10`:
   ```python
   RENAME_MAP_10 = {
       'RECID': 'occID', 'PRV': 'PR', 'HSDSIZEC': 'HHSIZE',
       'AGEGR10': 'AGEGRP', 'SEX': 'SEX', 'MARSTAT': 'MARSTH',
       'LANHSDC': 'KOL', 'ACT7DAYS': 'LFTAG', 'LUC_RST': 'CMA',
       'INCM': 'TOTINC', 'DVTDAY': 'DDAY',
   }
   ```

**Expected result**
File exists, imports run without error, constants are accessible.

**How to test**
Run `python -c "import importlib.util; spec = importlib.util.spec_from_file_location('a', '11CEN10GSS_alignment.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print(m.COLS_MAIN_10)"` — should print the column list without errors.

---

### T1.2 — Implement GSS 2010 File Reader

**What to do**
Implement two functions in `11CEN10GSS_alignment.py`:
- `parse_sps_colspec(sps_filepath)` — parses variable names and column positions from an SPSS `.SPS` file
- `read_gss_2010_main(dat_path, sps_path, cols_to_extract)` — reads the fixed-width `GSSMain_2010.DAT`

**How to do it**
Copy both functions verbatim from `16CEN15GSS_alignment.py` (`parse_sps_colspec` and `read_gss_2015_main`). Rename `read_gss_2015_main` → `read_gss_2010_main` and update the docstring year references. The parsing logic is identical — both use the same SPSS `.SPS` format.

Key paths to use inside the function (as defaults or documentation):
- `dat_path`: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010.DAT`
- `sps_path`: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010_syntax.SPS`

**Expected result**
`read_gss_2010_main()` returns a DataFrame with the columns listed in `COLS_MAIN_10` (those that exist in the SPS). Expect ~17,000–20,000 rows (GSS 2010 Cycle 24 sample size).

**How to test**
```python
df = read_gss_2010_main(dat_path, sps_path, COLS_MAIN_10)
assert len(df) > 10000
assert 'RECID' in df.columns
assert 'AGEGR10' in df.columns
assert df['SEX'].isin([1, 2, 9]).all()  # basic value check
```

---

### T1.3 — Implement GSS 2010 Merge Function

**What to do**
Implement `read_merge_save_gss_2010(dat_path, sps_path, episode_path, cols_main, rename_dict, output_csv_path)` which:
1. Reads the GSS 2010 main file
2. Reads the pre-processed episode CSV (`out10EP_ACT_PRE_coPRE.csv`)
3. Merges demographics onto episodes
4. Renames columns using `RENAME_MAP_10`
5. Saves the result to CSV

**How to do it**
Copy `read_merge_save_gss_2015` from `16CEN15GSS_alignment.py` and rename it to `read_merge_save_gss_2010`. Change the merge key logic: in GSS 2010 the main file key is `RECID` (not `PUMFID`), but after renaming via `RENAME_MAP_10` it becomes `occID`. The episode file already has `occID` (set in T0.2).

The merge logic should be:
```python
# Rename RECID → occID in main file before merge
df_main = df_main.rename(columns={'RECID': 'occID'})
df_merged = pd.merge(df_episode, df_main, on='occID', how='left')
```

After merging, apply `RENAME_MAP_10` to the remaining un-renamed columns (AGEGR10, HSDSIZEC, etc.).

**Expected result**
A merged DataFrame where every episode row also carries the respondent's demographic variables. Row count should equal the episode file row count. A new CSV is saved at `output_csv_path`.

**How to test**
- `df_merged['occID'].isna().sum() == 0` — all episodes have a matched respondent
- `'AGEGRP' in df_merged.columns` — rename applied correctly
- `df_merged['DDAY'].isin([1,2,3,4,5,6,7]).all()` — day codes intact after merge

---

### T1.4 — Implement Harmonization: AGEGRP, SEX, MARSTH, NOCS

**What to do**
Implement four harmonization functions in `11CEN10GSS_alignment.py`:
- `harmonize_agegrp(df_census, df_gss)`
- `harmonize_sex(df_census, df_gss)`
- `harmonize_marsth(df_census, df_gss)`
- `harmonize_nocs(df_census, df_gss)`

**How to do it**
Copy all four functions verbatim from `06CEN05GSS_alignment.py`. No logic changes are needed — Census 2011 and GSS 2010 use identical encodings for these variables.

Verify the Census 2011 mappings match:
- `AGEGRP`: Census 3–13 → GSS 1–7 (same 2006 mapping)
- `SEX`: both use 1=Male, 2=Female
- `MARSTH`: Census 1–3, GSS 1–6 → collapse GSS 3,4,5,6 → 3
- `NOCS`: both use 1–10, map GSS 97/98 → 99

**Expected result**
After calling each function, both DataFrames share the same unique value sets for the respective column.

**How to test**
For each function, after calling it:
```python
assert set(df_census['AGEGRP'].unique()) == set(df_gss['AGEGRP'].unique())
# repeat for SEX, MARSTH, NOCS
```

---

### T1.5 — Implement Harmonization: HHSIZE, KOL, PR

**What to do**
Implement three harmonization functions:
- `harmonize_hhsize(df_census, df_gss)`
- `harmonize_kol(df_census, df_gss)`
- `harmonize_pr(df_census, df_gss)`

**How to do it**

**`harmonize_hhsize`**: Copy from `06CEN05GSS_alignment.py`. Census 2011 caps at 6+.

**`harmonize_kol`**: Copy from `06CEN05GSS_alignment.py`. GSS 2010 uses `LANHSDC` (household language, already renamed to `KOL` via `RENAME_MAP_10`). Before applying the function, check what unique values appear in `df_gss['KOL']` and compare to Census 2011 `KOL` values (1=English, 2=French, 3=Both, 4=Neither). If the encodings are incompatible (e.g. GSS has more categories), print a warning and drop both datasets' rows that don't map to [1, 2, 3].

**`harmonize_pr`**: Copy from `06CEN05GSS_alignment.py`. Census 2011 uses the same 2-digit province codes as Census 2006. GSS 2010 uses the same province codes as GSS 2015. Apply identical mapping:
```python
census_to_gss_pr = {1:10, 2:24, 3:35, 4:46, 5:48, 6:59}
gss_pr_mapping = {10:10, 11:10, 12:10, 13:10, 24:24, 35:35, 46:46, 47:46, 48:48, 59:59}
```

**Expected result**
- `HHSIZE`: both [1, 2, 3, 4, 5, 6]
- `KOL`: both [1, 2, 3] (or subset)
- `PR`: both [10, 24, 35, 46, 48, 59]

**How to test**
```python
assert set(df_census['HHSIZE'].unique()).issubset({1,2,3,4,5,6})
assert set(df_gss['HHSIZE'].unique()).issubset({1,2,3,4,5,6})
assert set(df_census['PR'].unique()) == set(df_gss['PR'].unique())
```

---

### T1.6 — Implement Harmonization: LFTAG, CMA, ATTSCH

**What to do**
Implement three more harmonization functions:
- `harmonize_lftag(df_census, df_gss)`
- `harmonize_cma(df_census, df_gss)`
- `harmonize_attsch(df_census, df_gss)` — with a guard for GSS 2010 availability

**How to do it**

**`harmonize_lftag`**: Copy from `06CEN05GSS_alignment.py`. GSS 2010 uses `ACT7DAYS` (renamed to `LFTAG`). Same 1–5 output categories.

**`harmonize_cma`**: Census 2011 uses **3-digit CMA codes** (e.g. 505=Ottawa, 535=Toronto, 825=Calgary, 835=Edmonton, 933=Vancouver). Map to 3 categories matching GSS `LUC_RST`:
```python
def map_census_cma_2011(x):
    try:
        x = int(float(x))
    except:
        return 99
    # Large CMAs (population >= 500,000)
    if x in [505, 535, 825, 835, 933, 408, 421, 462, 532, 550, 568, 580, 602, 611, 612, 620, 630]:
        return 1  # CMA ≥500k
    if 1 <= x <= 995:
        return 2  # Other CA/CMA
    if x in [996, 997, 998, 999]:
        return 3  # Rural / not CMA
    return 99
```
Drop GSS rural (LUC_RST=3) to align with Census (which only has 1 and 2 after mapping). If Census does include rural, keep 3 as well — verify from data.

**`harmonize_attsch`**: Check first if `ATTSCH` exists in GSS 2010 `df_gss`:
```python
def harmonize_attsch(df_census, df_gss):
    if 'ATTSCH' not in df_gss.columns:
        print("  [!] ATTSCH not found in GSS 2010 — dropping from Census too.")
        df_census = df_census.drop(columns=['ATTSCH'], errors='ignore')
        return df_census, df_gss
    # otherwise apply same mapping as 06CEN05GSS
    ...
```

**Expected result**
- `LFTAG`: both [1, 2, 3, 4, 5]
- `CMA`: both [1, 2] or [1, 2, 3] (must match)
- `ATTSCH`: either both [1, 2] or dropped from both

**How to test**
```python
assert set(df_census['LFTAG'].unique()) == set(df_gss['LFTAG'].unique())
assert 'ATTSCH' not in df_census.columns or set(df_census['ATTSCH'].unique()) == set(df_gss['ATTSCH'].unique())
```

---

### T1.7 — Implement Harmonization: TOTINC (Both Continuous)

**What to do**
Implement `harmonize_totinc(df_census, df_gss)`. Unlike other pipelines where only Census income is continuous, in this pipeline **both** Census 2011 `TOTINC` and GSS 2010 `TOTINC` (renamed from `INCM`) are continuous dollar values. Both must be binned into the same categorical scheme.

**How to do it**
Define a single binning function and apply it to both DataFrames:
```python
def map_income_to_category(x):
    try:
        x = float(x)
    except:
        return 99
    if x <= 0:     return 1
    if x < 5000:   return 2
    if x < 10000:  return 3
    if x < 15000:  return 4
    if x < 20000:  return 5
    if x < 30000:  return 6
    if x < 40000:  return 7
    if x < 50000:  return 8
    if x < 60000:  return 9
    if x < 80000:  return 10
    if x < 100000: return 11
    return 12

def harmonize_totinc(df_census, df_gss):
    # GSS: INCM may have refusal codes (97, 98, 99) — drop them
    df_gss['TOTINC'] = pd.to_numeric(df_gss['TOTINC'], errors='coerce')
    df_gss = df_gss[df_gss['TOTINC'].notna()].copy()
    df_gss = df_gss[~df_gss['TOTINC'].isin([97, 98, 99])].copy()
    df_gss['TOTINC'] = df_gss['TOTINC'].apply(map_income_to_category).astype(int)
    df_gss = df_gss[df_gss['TOTINC'] != 99].copy()

    # Census: drop refusals, then bin
    df_census['TOTINC'] = pd.to_numeric(df_census['TOTINC'], errors='coerce')
    df_census = df_census[df_census['TOTINC'].notna()].copy()
    df_census['TOTINC'] = df_census['TOTINC'].apply(map_income_to_category).astype(int)
    df_census = df_census[df_census['TOTINC'] != 99].copy()

    print(f"    Census TOTINC unique: {sorted(df_census['TOTINC'].unique())}")
    print(f"    GSS TOTINC unique: {sorted(df_gss['TOTINC'].unique())}")
    return df_census, df_gss
```

**Expected result**
Both `df_census['TOTINC']` and `df_gss['TOTINC']` contain only integer values in [1, 12].

**How to test**
```python
assert df_census['TOTINC'].isin(range(1, 13)).all()
assert df_gss['TOTINC'].isin(range(1, 13)).all()
assert set(df_census['TOTINC'].unique()) == set(df_gss['TOTINC'].unique())
```

---

### T1.8 — Implement Census 2011 Household Assembly

**What to do**
Implement `assemble_households(csv_file_path, target_year, output_dir, start_id=100)`. This function reads the filtered Census 2011 CSV, derives `HHSIZE` if it is missing, reconstructs households with unique `SIM_HH_ID` values, and saves a linked CSV.

**How to do it**
1. Copy `assemble_households()` from `16CEN15GSS_alignment.py` into `11CEN10GSS_alignment.py`.
2. Add a `HHSIZE` derivation step immediately after loading the data:
   ```python
   if 'HHSIZE' not in df_population.columns:
       print("   [!] HHSIZE not found — deriving from HH_ID counts...")
       df_population['HHSIZE'] = df_population.groupby('HH_ID')['HH_ID'].transform('count')
       df_population.loc[df_population['HHSIZE'] >= 7, 'HHSIZE'] = 6
       print(f"   Derived HHSIZE distribution:\n{df_population['HHSIZE'].value_counts().sort_index()}")
   ```
3. The rest of the household assembly logic (Phase 1 singles, Phase 2 families via `CF_RP`, Phase 3 roommates) is identical to `16CEN15GSS_alignment.py`.

Input path: `0_Occupancy/DataSources_CENSUS/census_2011/cen11_filtered.csv` (or `0_Occupancy/DataSources_CENSUS/cen11_filtered.csv` — check which exists).
Output path: `0_Occupancy/DataSources_CENSUS/census_2011/2011_LINKED.csv`

**Expected result**
`2011_LINKED.csv` contains all Census 2011 persons with `SIM_HH_ID` and `PID` columns added. Persons sharing a household share the same `SIM_HH_ID`. Validation message: `[OK] VALIDATION: All households have correct member counts.`

**How to test**
```python
df = pd.read_csv('2011_LINKED.csv')
size_counts = df.groupby('SIM_HH_ID')['PID'].count()
target_sizes = df.groupby('SIM_HH_ID')['HHSIZE'].first()
assert (size_counts == target_sizes).all(), "Household size mismatch"
assert df['SIM_HH_ID'].nunique() > 1000
```

---

### T1.9 — Implement data_alignment() and check_value_alignment(), and main()

**What to do**
Implement the top-level orchestration function `data_alignment()`, the validation function `check_value_alignment()`, and the `main()` entry point that wires everything together.

**How to do it**

**`data_alignment(census_csv_path, gss_csv_path, output_dir, target_year="2010")`**:
Copy from `06CEN05GSS_alignment.py` and update:
- Call harmonization functions in this order: `harmonize_agegrp`, `harmonize_cma`, `harmonize_hhsize`, `harmonize_kol`, `harmonize_lftag`, `harmonize_marsth`, `harmonize_nocs`, `harmonize_pr`, `harmonize_sex`, `harmonize_totinc`, `harmonize_attsch`
- Save outputs as `Aligned_Census_2010.csv` and `Aligned_GSS_2010.csv`
- Output directory: `0_Occupancy/Outputs_11CEN10GSS/alignment/`

**`check_value_alignment(df1, df2, ...)`**: Copy verbatim from `06CEN05GSS_alignment.py`. Set:
```python
TARGET_COLS = ['AGEGRP', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']
```

**`main()`**: Define file paths using `occ_config.py` base paths, then call:
1. `read_merge_save_gss_2010(...)` → produces merged GSS CSV
2. `assemble_households(...)` → produces `2011_LINKED.csv`
3. `data_alignment(...)` → runs all harmonization + saves aligned CSVs
4. `check_value_alignment(...)` → prints alignment report

**Expected result**
Running `python 11CEN10GSS_alignment.py` produces:
- `0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv`
- `0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv`
- Console output showing alignment check with all columns as `MATCH`

**How to test**
```python
import pandas as pd
cen = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
gss = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')
expected_cols = ['AGEGRP', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']
for col in expected_cols:
    if col in cen.columns and col in gss.columns:
        assert set(cen[col].unique()) == set(gss[col].unique()), f"Mismatch in {col}"
print("All alignment checks passed.")
```

---

---

## Step 1 Bug Fixes — Must complete before Step 2

These tasks fix the two confirmed bugs and two unverified issues discovered after running Step 1. Run all four, then re-run `python 11CEN10GSS_alignment.py` to regenerate the aligned CSVs before proceeding to Step 2.

---

### TF.1 — Fix `harmonize_pr()`: Census 2011 uses 2-digit province codes

**What to do**
Replace the `harmonize_pr()` function body in `eSim_occ_utils/11CEN10GSS/11CEN10GSS_alignment.py`. The current version uses a mapping built for Census 2006 (regional codes 1–6), which produces all-99 results for Census 2011's 2-digit province codes, causing every Census row to be dropped.

**How to do it**
In `11CEN10GSS_alignment.py`, find `def harmonize_pr(` and replace the entire function body with:

```python
def harmonize_pr(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing PR...")

    # Census 2011 uses 2-digit Statistics Canada province codes directly
    cen11_pr_map = {
        10: 10, 11: 10, 12: 10, 13: 10,  # Atlantic provinces → NL representative
        24: 24,                             # Quebec
        35: 35,                             # Ontario
        46: 46, 47: 46,                    # MB + SK → MB (Prairies representative)
        48: 48,                             # Alberta
        59: 59,                             # British Columbia
        # 60 (YT), 61 (NT), 62 (NU) → not in dict → map to 99 → dropped
    }
    df_census['PR'] = pd.to_numeric(df_census['PR'], errors='coerce').fillna(99).astype(int)
    df_census['PR'] = df_census['PR'].map(cen11_pr_map).fillna(99).astype(int)
    df_census = df_census[~df_census['PR'].isin([99])].copy()

    # GSS 2010: same 2-digit codes, same consolidation
    gss_pr_mapping = {10:10, 11:10, 12:10, 13:10, 24:24, 35:35, 46:46, 47:46, 48:48, 59:59}
    df_gss['PR'] = pd.to_numeric(df_gss['PR'], errors='coerce').fillna(99).astype(int)
    df_gss['PR'] = df_gss['PR'].map(gss_pr_mapping).fillna(99).astype(int)
    df_gss = df_gss[~df_gss['PR'].isin([99])].copy()

    print(f"    Census PR unique: {sorted(df_census['PR'].unique())}")
    print(f"    GSS PR unique: {sorted(df_gss['PR'].unique())}")
    return df_census, df_gss
```

**Expected result**
After re-running `data_alignment()`, `Aligned_Census_2010.csv` has non-zero rows (expect 250,000–330,000). Census `PR` unique values should be `[10, 24, 35, 46, 48, 59]`.

**How to test**
```python
import pandas as pd
df = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
assert len(df) > 100000, f"Still empty or too few rows: {len(df)}"
assert set(df['PR'].unique()) == {10, 24, 35, 46, 48, 59}, f"Unexpected PR values: {df['PR'].unique()}"
print(f"Census rows after fix: {len(df)}")
```

---

### TF.2 — Fix duplicate `DDAY`/`DDAY.1` column in GSS aligned output

**What to do**
Edit `read_merge_save_gss_2010()` in `11CEN10GSS_alignment.py` to drop the `DVTDAY` column from the merged DataFrame before renaming, preventing the duplicate `DDAY` column from appearing in `Aligned_GSS_2010.csv`.

**How to do it**
In `read_merge_save_gss_2010()`, find the block that starts with `rename_adjusted = {k: v for k, v in rename_dict.items() if k != 'RECID'}` and replace it with:

```python
# Drop DVTDAY if DDAY is already present from the episode file (prevents DDAY / DDAY.1 duplicate)
if 'DVTDAY' in df_merged.columns and 'DDAY' in df_merged.columns:
    df_merged = df_merged.drop(columns=['DVTDAY'])

rename_adjusted = {k: v for k, v in rename_dict.items() if k != 'RECID' and k in df_merged.columns}
df_merged = df_merged.rename(columns=rename_adjusted)
```

**Expected result**
`Aligned_GSS_2010.csv` contains exactly one day-type column named `DDAY`. No `DDAY.1` column.

**How to test**
```python
import pandas as pd
df = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')
assert 'DDAY' in df.columns, "DDAY column missing"
assert 'DDAY.1' not in df.columns, "Duplicate DDAY.1 still present"
assert df['DDAY'].isin([1,2,3,4,5,6,7]).all(), "Unexpected DDAY values"
print("DDAY column OK — no duplicates")
```

---

### TF.3 — Verify `harmonize_marsth()` against Census 2011 codebook

**What to do**
Confirm that the current `harmonize_marsth()` mapping is correct for Census 2011's `MARSTH` coding scheme, then add an inline comment documenting the Census 2011 categories.

**How to do it**
1. Open `0_Occupancy/DataSources_CENSUS/cen11.sps` and search for the `MARSTH` value labels.
2. Verified Census 2011 MARSTH codes:
   - 1 = Never legally married and not living common law
   - 2 = Legally married and not separated
   - 3 = Living common law
   - 4 = Separated and not living common law
   - 5 = Divorced and not living common law
   - 6 = Widowed and not living common law
3. If confirmed, add a comment to the function explaining the mapping:
   ```python
   # Census 2011 MARSTH: 1=Single, 2=Married, 3=Common-law, 4=Sep, 5=Div, 6=Widowed
   # GSS 2010 MARSTAT:   1=Married, 2=Common-law, 3=Widowed, 4=Sep, 5=Div, 6=Single
   # Mapping: Census 1 -> GSS 6, Census 2+3 -> GSS 1+2, Census 4+5+6 -> GSS 3+4+5
   ```
4. If Census 2011 MARSTH uses different codes, update the function accordingly.

**Expected result**
The `harmonize_marsth()` function has a comment block confirming the category mapping is correct for Census 2011. Both DataFrames have `MARSTH` values in `{1, 2, 3}`.

**How to test**
```python
import pandas as pd
df_cen = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
df_gss = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')
assert set(df_cen['MARSTH'].unique()).issubset({1, 2, 3})
assert set(df_gss['MARSTH'].unique()).issubset({1, 2, 3})
assert set(df_cen['MARSTH'].unique()) == set(df_gss['MARSTH'].unique())
print(f"MARSTH OK: {sorted(df_cen['MARSTH'].unique())}")
```

---

### TF.4 — Verify and fix `harmonize_totinc()` refusal code handling for GSS 2010

**What to do**
Check the actual refusal codes used for `INCM` in the GSS 2010 main file and ensure they are dropped before income categorization, not misinterpreted as low-dollar income values.

**How to do it**
1. Open `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010_syntax.SPS`.
2. Search for the `INCM` variable label section (look for `VALUE LABELS` or `/INCM`). The verified refusal/missing codes are `97`, `98`, and `99`.
3. In `harmonize_totinc()`, update the GSS side to explicitly filter those codes before using the categorical `1`–`12` values:

```python
def harmonize_totinc(df_census: pd.DataFrame, df_gss: pd.DataFrame) -> tuple:
    print("  Harmonizing TOTINC...")

    # GSS 2010: INCM is categorical 1-12. Filter refusal codes first.
    GSS_INCM_REFUSAL = [97, 98, 99]
    df_gss['TOTINC'] = pd.to_numeric(df_gss['TOTINC'], errors='coerce')
    df_gss = df_gss[~df_gss['TOTINC'].isin(GSS_INCM_REFUSAL)].copy()
    df_gss = df_gss[df_gss['TOTINC'].notna()].copy()
    df_gss['TOTINC'] = df_gss['TOTINC'].astype(int)

    # Census 2011: TOTINC is continuous dollars — bin to the same 12 categories
    df_census['TOTINC'] = pd.to_numeric(df_census['TOTINC'], errors='coerce')
    df_census = df_census[df_census['TOTINC'].notna()].copy()
    df_census['TOTINC'] = df_census['TOTINC'].apply(map_income_to_category).astype(int)
    df_census = df_census[df_census['TOTINC'] != 99].copy()

    print(f"    Census TOTINC unique: {sorted(df_census['TOTINC'].unique())}")
    print(f"    GSS TOTINC unique: {sorted(df_gss['TOTINC'].unique())}")
    return df_census, df_gss
```

**Expected result**
Both `TOTINC` columns contain only values in `{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}`. No refusal codes present.

**How to test**
```python
import pandas as pd
df_cen = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
df_gss = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')
assert set(df_cen['TOTINC'].unique()).issubset(set(range(1, 13)))
assert set(df_gss['TOTINC'].unique()).issubset(set(range(1, 13)))
print(f"Census TOTINC: {sorted(df_cen['TOTINC'].unique())}")
print(f"GSS TOTINC: {sorted(df_gss['TOTINC'].unique())}")
```

---

### TF.5 — Re-run alignment and confirm outputs are valid

**What to do**
After completing TF.1–TF.4, re-run `11CEN10GSS_alignment.py` to regenerate both aligned CSVs with all fixes applied. Run the full alignment check.

**How to do it**
```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/eSim_occ_utils/11CEN10GSS
python 11CEN10GSS_alignment.py
```

**Expected result**
Console output shows:
- All harmonization steps complete without errors
- Each step prints non-empty unique value lists for both Census and GSS
- `check_value_alignment()` output shows `MATCH` for all columns in `TARGET_COLS_10`
- `Aligned_Census_2010.csv` has > 100,000 rows
- `Aligned_GSS_2010.csv` has ~250,000 rows with no `DDAY.1` column

**How to test**
```python
import pandas as pd
cen = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
gss = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')

print(f"Census rows: {len(cen)}")
print(f"GSS rows: {len(gss)}")

assert len(cen) > 100000, "Census output still too small"
assert 'DDAY.1' not in gss.columns, "Duplicate DDAY column still present"

target_cols = ['AGEGRP', 'CMA', 'HHSIZE', 'KOL', 'LFTAG', 'MARSTH', 'NOCS', 'PR', 'SEX', 'TOTINC']
for col in target_cols:
    if col in cen.columns and col in gss.columns:
        cv = set(cen[col].dropna().unique())
        gv = set(gss[col].dropna().unique())
        status = "MATCH" if cv == gv else "MISMATCH"
        print(f"  {col:10s} {status}")
```

---

## Step 2 — Profile Matching (`11CEN10GSS_ProfileMatcher.py`)

Create `eSim_occ_utils/11CEN10GSS/11CEN10GSS_ProfileMatcher.py`. Reference: `16CEN15GSS_ProfileMatcher.py`.

---

### T2.1 — Implement MatchProfiler Class

**What to do**
Implement the `MatchProfiler` class with its `__init__` method. This class takes aligned Census and GSS DataFrames and builds weekday/weekend catalogs for tiered matching.

**How to do it**
Copy the `MatchProfiler` class from `16CEN15GSS_ProfileMatcher.py`. Update only:
1. The `cols_t1` default list to match the 11CEN10GSS columns:
   ```python
   self.cols_t1 = ["HHSIZE", "AGEGRP", "MARSTH", "SEX", "KOL", "PR", "LFTAG", "TOTINC", "CMA"]
   ```
2. The `cols_t2` list:
   ```python
   self.cols_t2 = ["HHSIZE", "AGEGRP", "SEX", "MARSTH", "LFTAG", "PR"]
   ```
3. Add `ATTSCH` to `cols_t1` and `cols_t2` only if `ATTSCH` is present in both aligned DataFrames (add an `if 'ATTSCH' in df_gss.columns` guard).

The day-type split logic is identical:
- Weekday catalog: `DDAY ∈ {2, 3, 4, 5, 6}`
- Weekend catalog: `DDAY ∈ {1, 7}`

**Expected result**
`MatchProfiler` initializes without error. `self.catalog_wd` and `self.catalog_we` are non-empty DataFrames with unique `occID` rows.

**How to test**
```python
import pandas as pd
cen = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_Census_2010.csv')
gss = pd.read_csv('0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv')
mp = MatchProfiler(cen, gss)
assert len(mp.catalog_wd) > 1000
assert len(mp.catalog_we) > 500
print(f"WD catalog: {len(mp.catalog_wd)}, WE catalog: {len(mp.catalog_we)}")
```

---

### T2.2 — Implement run_matching() and save_matched_keys()

**What to do**
Implement `MatchProfiler.run_matching()` which iterates over all Census agents and assigns a weekday GSS ID and a weekend GSS ID using the tiered matching strategy. Then implement `save_matched_keys(output_path, sample_pct)` which saves the result.

**How to do it**
Copy `run_matching()` and any `_match_agent()` or `_lookup()` helper methods verbatim from `16CEN15GSS_ProfileMatcher.py`. No logic changes are needed — the tiered matching algorithm is dataset-agnostic.

The output DataFrame (matched keys) should have columns:
```
PID, SIM_HH_ID, occID_WD, occID_WE, Tier_WD, Tier_WE, HHSIZE, AGEGRP, SEX, ...
```

Save path: `0_Occupancy/Outputs_11CEN10GSS/ProfileMatching/11CEN10GSS_Matched_Keys_sample{pct}pct.csv`

**Expected result**
Every row in the sampled Census DataFrame has a non-null `occID_WD` and `occID_WE`. Tier 5 (random fallback) should be less than 5% of assignments.

**How to test**
```python
df_keys = pd.read_csv('...Matched_Keys_sample10pct.csv')
assert df_keys['occID_WD'].isna().sum() == 0
assert df_keys['occID_WE'].isna().sum() == 0
tier_dist = df_keys['Tier_WD'].value_counts(normalize=True)
print(f"Tier distribution (WD):\n{tier_dist}")
assert tier_dist.get(5, 0) < 0.05, "Too many Tier 5 fallbacks"
```

---

### T2.3 — Implement ScheduleExpander and main()

**What to do**
Implement the `ScheduleExpander` class (expands matched keys into full per-person episode schedules) and the `main(sample_pct)` entry point.

**How to do it**
Copy `ScheduleExpander` verbatim from `16CEN15GSS_ProfileMatcher.py`. Update paths only:
- Input: `Matched_Keys_sample{pct}pct.csv` from `Outputs_11CEN10GSS/ProfileMatching/`
- GSS episode source: `out10EP_ACT_PRE_coPRE.csv` from `DataSources_GSS/Episode_files/GSS_2010_episode/`
- Output: `11CEN10GSS_Full_Schedules_sample{pct}pct.csv` in `Outputs_11CEN10GSS/ProfileMatching/`

The `main(sample_pct=10)` function should:
1. Load aligned Census and GSS data
2. Sample Census at `sample_pct`%
3. Initialize `MatchProfiler` and call `run_matching()`
4. Save matched keys CSV
5. Initialize `ScheduleExpander` and expand schedules
6. Save full schedules CSV

**Expected result**
Two files saved:
- `11CEN10GSS_Matched_Keys_sample10pct.csv`
- `11CEN10GSS_Full_Schedules_sample10pct.csv`

**How to test**
```python
df_sched = pd.read_csv('11CEN10GSS_Full_Schedules_sample10pct.csv')
assert 'occID' in df_sched.columns
assert 'ACTCODE' in df_sched.columns
assert 'STARTMIN' in df_sched.columns
assert len(df_sched) > len(matched_keys)  # each person has multiple episodes
```

---

## Step 3 — Household Aggregation (`11CEN10GSS_HH_aggregation.py`)

Create `eSim_occ_utils/11CEN10GSS/11CEN10GSS_HH_aggregation.py`. Reference: `16CEN15GSS_HH_aggregation.py`.

---

### T3.1 — Implement HouseholdAggregator Class and Step A (Schedule Grid)

**What to do**
Implement the `HouseholdAggregator` class `__init__` and **Step A**: expand individual episode-level schedules into a 5-minute time-slot grid (288 slots per day) for each Census agent.

**How to do it**
Copy the `HouseholdAggregator` class from `16CEN15GSS_HH_aggregation.py`. Update only:
- Input paths: use `Outputs_11CEN10GSS/ProfileMatching/` and `DataSources_GSS/Episode_files/GSS_2010_episode/`
- Version prefix: `11CEN10GSS` (used in output file names)

Step A logic: for each person (`PID`), map each episode to its time slots using `STARTMIN` and `ENDMIN` (divided by 5 to get slot index). Assign `ACTCODE` and `PRE` to each slot.

**Expected result**
A per-person, 288-column grid where each column is a 5-minute slot. Values in grid cells are activity codes (or 0 if no episode covers that slot).

**How to test**
```python
# Each person should have exactly 288 time slots
assert grid.shape[1] == 288
# Slots must be covered (no all-zero rows unless person was truly inactive all day)
assert (grid.sum(axis=1) > 0).mean() > 0.9
```

---

### T3.2 — Implement Steps B, C, D (Presence and Activity Aggregation)

**What to do**
Implement the household-level aggregation in three sub-steps:
- **Step B** (`occPre`): binary household presence — is at least 1 person home?
- **Step C** (`occDensity`): count of household members present at each slot
- **Step D** (`occActivity`): set of activities happening in the household at each slot

**How to do it**
Copy Steps B, C, and D from `16CEN15GSS_HH_aggregation.py`. No logic changes needed. All three operate on the per-person grid produced in Step A, grouped by `SIM_HH_ID`.

- Step B: `occPre[hh, t] = 1 if any member has PRE[t] == 1 else 0`
- Step C: `occDensity[hh, t] = sum(PRE[t] for all members in hh)`
- Step D: `occActivity[hh, t] = set(ACTCODE[t] for all members in hh)`

**Expected result**
A household-level DataFrame with 288 columns per metric (`occPre_0`...`occPre_287`, `occDensity_0`...`occDensity_287`, `occActivity_0`...`occActivity_287`) indexed by `SIM_HH_ID`.

**How to test**
```python
assert df_agg['occPre_0'].isin([0, 1]).all()
assert df_agg['occDensity_0'].between(0, 7).all()  # max HHSIZE=6, allow small overcount
assert df_agg[['occPre_' + str(i) for i in range(288)]].max().max() == 1
```

---

### T3.3 — Implement main() and Save Outputs

**What to do**
Implement `main(sample_pct=10)` which runs the full aggregation pipeline and saves two output files.

**How to do it**
Copy `main()` from `16CEN15GSS_HH_aggregation.py` and update:
- Version string: `11CEN10GSS`
- Input: `11CEN10GSS_Full_Schedules_sample{pct}pct.csv`
- Outputs (save to `Outputs_11CEN10GSS/HH_aggregation/`):
  - `11CEN10GSS_Full_Aggregated_sample{pct}pct.csv` — household-level grid
  - `11CEN10GSS_Full_Schedules_sample{pct}pct.csv` — individual expanded schedules (copy from ProfileMatching or re-save here)

**Expected result**
- `Full_Aggregated`: one row per household, 288 × 3 time-slot columns
- `Full_Schedules`: one row per episode per person
- Console prints total number of households processed

**How to test**
```python
df_agg = pd.read_csv('11CEN10GSS_Full_Aggregated_sample10pct.csv')
assert 'SIM_HH_ID' in df_agg.columns
assert 'occPre_0' in df_agg.columns
assert df_agg['SIM_HH_ID'].nunique() == len(df_agg)  # one row per household
```

---

## Step 4 — BEM Conversion (`11CEN10GSS_occToBEM.py`)

Create `eSim_occ_utils/11CEN10GSS/11CEN10GSS_occToBEM.py`. Reference: `16CEN15GSS_occToBEM.py`.

---

### T4.1 — Implement BEMConverter Class and Lookup Tables

**What to do**
Implement the `BEMConverter` class with its `__init__` and the static lookup tables: metabolic rate map, DTYPE map, and PR map.

**How to do it**
Copy the `BEMConverter` class from `16CEN15GSS_occToBEM.py`. Update the lookup tables for Census 2011 DTYPE codes:

```python
METABOLIC_MAP = {
    '1': 125, '2': 125, '3': 70, '5': 70, '6': 100,
    '7': 80, '8': 80, '9': 80, '10': 80, '11': 245,
    '12': 80, '13': 80, '14': 70, '15': 70,
}

# Census 2011 detailed DTYPE (verify codes from cen11.sps)
DTYPE_MAP = {
    1: 'SingleDetached',
    2: 'SemiDetached',
    3: 'RowHouse',
    4: 'DuplexFlat',
    5: 'ApartmentHighRise',
    6: 'ApartmentLowRise',
    7: 'OtherSingleAttached',
    8: 'MovableDwelling',
}

PR_MAP = {10: 'Atlantic', 24: 'Quebec', 35: 'Ontario',
          46: 'Prairie', 48: 'Alberta', 59: 'BC'}
```

> Note: Census 2011 provides detailed DTYPE codes directly — **no DTYPE expansion step is needed** (unlike 16CEN15GSS which used a Random Forest classifier to refine coarse codes).

**Expected result**
`BEMConverter` initializes without error. Lookup tables are accessible as class attributes.

**How to test**
```python
bc = BEMConverter(input_path=..., output_dir=...)
assert 1 in bc.DTYPE_MAP
assert '1' in bc.METABOLIC_MAP
```

---

### T4.2 — Implement Hourly Aggregation and BEM Output

**What to do**
Implement the core conversion logic in `BEMConverter`: aggregate the 5-minute household grids (288 slots) to hourly resolution (24 slots), compute fractional occupancy and per-person metabolic rate for each hour, and attach residential attribute columns.

**How to do it**
Copy the hourly aggregation method from `16CEN15GSS_occToBEM.py`. No logic changes needed:
- Group 288 slots into 24 hours (12 slots per hour)
- `fractional_occ[h] = mean(occPre[h*12 : (h+1)*12])` → value in [0, 1]
- `met_rate[h] = weighted average of metabolic rates for activities in that hour`

Then merge residential attributes from Census 2011:
- Load `Aligned_Census_2010.csv`
- Join `DTYPE`, `BEDRM`, `ROOM`, `CONDO`, `REPAIR`, `PR` to each household by `SIM_HH_ID`

Output columns:
```
SIM_HH_ID, Hour_0...Hour_23, MetRate_0...MetRate_23, DTYPE, BEDRM, ROOM, CONDO, REPAIR, PR
```

**Expected result**
`11CEN10GSS_BEM_Schedules_sample10pct.csv` with all above columns. `Hour_*` values are in [0, 1]. `MetRate_*` values are ≥ 0.

**How to test**
```python
df_bem = pd.read_csv('11CEN10GSS_BEM_Schedules_sample10pct.csv')
hour_cols = [f'Hour_{i}' for i in range(24)]
assert df_bem[hour_cols].min().min() >= 0.0
assert df_bem[hour_cols].max().max() <= 1.0
assert df_bem['DTYPE'].isin(DTYPE_MAP.keys()).all()
assert df_bem['PR'].isin(PR_MAP.keys()).all()
```

---

### T4.3 — Implement main() and Final Validation

**What to do**
Implement `main(sample_pct=10)` and add a final sanity-check print block comparing BEM output statistics to Census 2011 benchmarks.

**How to do it**
Copy `main()` from `16CEN15GSS_occToBEM.py` and update version string and paths:
- Input: `11CEN10GSS_Full_Aggregated_sample{pct}pct.csv`
- Output: `0_Occupancy/Outputs_11CEN10GSS/occToBEM/11CEN10GSS_BEM_Schedules_sample{pct}pct.csv`

Add a validation block at the end of `main()`:
```python
print("\n--- BEM Output Validation ---")
print(f"Total households: {len(df_bem)}")
print(f"DTYPE distribution:\n{df_bem['DTYPE'].value_counts()}")
print(f"PR distribution:\n{df_bem['PR'].value_counts()}")
print(f"Mean daytime occupancy (Hour_9 to Hour_17): {df_bem[['Hour_' + str(i) for i in range(9,18)]].mean().mean():.3f}")
print(f"Mean nighttime occupancy (Hour_0 to Hour_6): {df_bem[['Hour_' + str(i) for i in range(0,7)]].mean().mean():.3f}")
# Nighttime should be > daytime (people are home at night)
```

**Expected result**
`11CEN10GSS_BEM_Schedules_sample10pct.csv` is saved. Validation block prints reasonable values: nighttime occupancy > daytime occupancy (expected for residential buildings).

**How to test**
```python
night_occ = df_bem[['Hour_' + str(i) for i in range(0, 7)]].mean().mean()
day_occ = df_bem[['Hour_' + str(i) for i in range(9, 18)]].mean().mean()
assert night_occ > day_occ, "Nighttime occupancy should exceed daytime for residential"
print("BEM output validation passed.")
```

---

## Step 5 — Package Initialization

### T5.1 — Create `__init__.py`

**What to do**
Create `eSim_occ_utils/11CEN10GSS/__init__.py` to mark the directory as a Python package, consistent with `06CEN05GSS` and `16CEN15GSS`.

**How to do it**
Create an empty file (or with a one-line docstring):
```python
"""11CEN10GSS: Census 2011 + GSS 2010 occupancy modeling pipeline."""
```

**Expected result**
File exists at `eSim_occ_utils/11CEN10GSS/__init__.py`.

**How to test**
From `eSim_occ_utils/` parent directory:
```python
import importlib
spec = importlib.util.find_spec('11CEN10GSS')
# Or simply: python -c "from eSim_occ_utils import 11CEN10GSS" (if on path)
```

---

---

## TD. Post-Fix Re-run (Required)

These tasks track the pipeline re-run needed after the step0 and alignment bug fixes from `debug_11CEN10GSS.md` were applied to the code on 2026-03-31 17:36.

### TD.1 — Confirm what was fixed in the code (Done)

**Status: ✅ Done**

The following changes were made to the code before step0 was last run:

In `11CEN10GSS_step0.py`:
- Added `ACT_MAP_10` dict and `_map_actcode()` — maps raw 3-digit ACTCODE to harmonized 1-14
- Added `_min_to_hhmm()` — converts decimal minutes (0–1440) to HHMM integer
- Derives `occACT`, `start`, `end`, `occPRE`, `Spouse`, `Children`, `otherInFAMs` before saving

In `11CEN10GSS_alignment.py`:
- Added `ROOM <= 15` filter after loading Census data in `data_alignment()`

These changes are confirmed present in the current source files.

### TD.2 — Re-run the full pipeline from step0

**Status: ⬜ Not started**

**What to do**
Re-run all five pipeline stages in order to regenerate clean, bug-free outputs.

**How to do it**
Run in this sequence (each one after the previous completes):

```
1. python 11CEN10GSS_step0.py
   → regenerates out10EP_ACT_PRE_coPRE.csv with occACT, start, end, Spouse, Children, otherInFAMs

2. python 11CEN10GSS_alignment.py
   → applies ROOM <= 15 filter; reads updated episode file

3. python 11CEN10GSS_ProfileMatcher.py   (--sample 10 or your usual sample)
4. python 11CEN10GSS_HH_aggregation.py  (--sample 10)
5. python 11CEN10GSS_occToBEM.py        (--sample 10)
```

**Why to do it**
All current output files were generated from the pre-fix episode CSV. The `occACT`, `start`, and social alias columns do not exist in `out10EP_ACT_PRE_coPRE.csv`, meaning:
- Every episode is still placed in the wrong 5-minute slot (Bug 1)
- Every active slot still returns 100 W metabolic rate (Bug 2)
- ROOM outliers still appear in the BEM non-temporal plot (Bug 3)
- `occDensity` is still always zero (silent bug)

**Expected result**
After re-running, the BEM temporal plot (`11CEN10GSS_BEM_temporals.png`) must show:
- Clear diurnal residential pattern: high overnight occupancy, dip 9–17h weekdays
- Metabolic rate distribution spread from ~70 W (Sleep) to ~200 W; no spike at 100 W
- Dynamic sample household schedules (not flat lines)

**How to test**
Apply the same five-check validation table from `debug_11CEN10GSS.md` Section "What to expect as results":

| Check | Pass criterion |
|-------|---------------|
| Diurnal occupancy | Night clearly higher than work-hours daytime |
| Metabolic rate distribution | Spread ~70–200 W, not a single spike at 100 W |
| ROOM distribution | No tail beyond 15 rooms |
| Sample household weekday | Dynamic occupancy trace, not flat |
| occDensity | Non-zero for a substantial fraction of `occPre==1` rows |

---

## Task Summary

| Task | Script | What it creates | Status |
|------|--------|-----------------|--------|
| T0.1–T0.3 | `11CEN10GSS_step0.py` | `out10EP_ACT_PRE_coPRE.csv` (283,287 rows) | ✅ Done |
| T1.1–T1.9 | `11CEN10GSS_alignment.py` | Script complete; alignment verified clean | ✅ Done |
| **TF.1** | `11CEN10GSS_alignment.py` | Fix `harmonize_pr()` for Census 2011 province codes | ✅ Done |
| **TF.2** | `11CEN10GSS_alignment.py` | Fix duplicate `DDAY`/`DDAY.1` in GSS output | ✅ Done |
| **TF.3** | `11CEN10GSS_alignment.py` | Verify `harmonize_marsth()` Census 2011 codes + add comment | ✅ Done |
| **TF.4** | `11CEN10GSS_alignment.py` | Verify + fix `harmonize_totinc()` refusal codes | ✅ Done |
| **TF.5** | *(re-run)* | Re-run alignment, confirm both aligned CSVs valid | ✅ Done |
| T2.1 | `11CEN10GSS_ProfileMatcher.py` | MatchProfiler class | ✅ Done |
| T2.2 | `11CEN10GSS_ProfileMatcher.py` | run_matching() + save_matched_keys() | ✅ Done |
| T2.3 | `11CEN10GSS_ProfileMatcher.py` | ScheduleExpander + main() | ✅ Done |
| T3.1 | `11CEN10GSS_HH_aggregation.py` | HouseholdAggregator + Step A grid | ✅ Done |
| T3.2 | `11CEN10GSS_HH_aggregation.py` | Steps B, C, D (occPre, Density, Activity) | ✅ Done |
| T3.3 | `11CEN10GSS_HH_aggregation.py` | main() + save outputs | ✅ Done |
| T4.1 | `11CEN10GSS_occToBEM.py` | BEMConverter class + lookup tables | ✅ Done |
| T4.2 | `11CEN10GSS_occToBEM.py` | Hourly aggregation + residential attributes | ✅ Done |
| T4.3 | `11CEN10GSS_occToBEM.py` | main() + validation | ✅ Done |
| T5.1 | `__init__.py` | Package marker | ✅ Done |
| **TD.1** | `step0.py` / `alignment.py` | Bug fixes applied to code (`occACT`, `start`, `end`, social cols, ROOM filter) | ✅ Done |
| **TD.2** | *(re-run)* | Re-run full pipeline from step0; validate output plots | ⬜ Not started |

---

## Final Verification (2026-03-31)

> **⚠️ Note (2026-04-01):** This verification was completed before the three bugs in `debug_11CEN10GSS.md` were discovered. The code fixes (TD.1) were applied after these outputs were generated. All outputs below are stale and need to be regenerated by running TD.2 before the pipeline can be considered correct.

### 11CEN10GSS Pipeline — Verification Summary ✅

#### Source files (all present)

| File | Status |
|---|---|
| `11CEN10GSS_main.py` | ✅ |
| `11CEN10GSS_step0.py` | ✅ |
| `11CEN10GSS_alignment.py` | ✅ |
| `11CEN10GSS_ProfileMatcher.py` | ✅ |
| `11CEN10GSS_HH_aggregation.py` | ✅ |
| `11CEN10GSS_occToBEM.py` | ✅ |
| `__init__.py` | ✅ |

#### Intermediate files (row counts match plan)

| File | Expected | Actual |
|---|---|---|
| `out10EP_ACT_PRE_coPRE.csv` | 283,287 | **283,287** ✅ |
| `GSS_2010_Merged.csv` | 283,287 | **283,287** ✅ |
| `2011_LINKED.csv` | 337,126 | **337,126** ✅ |

#### Alignment outputs

| File | Expected rows | Actual |
|---|---|---|
| `Aligned_GSS_2010.csv` | 219,584 | **219,584** ✅ (25 columns, no `DDAY.1`) |
| `Aligned_Census_2010.csv` | 273,678 | **273,678** ✅ |

#### Downstream outputs (all present, non-empty)

- **ProfileMatching**: `Full_Schedules` (1M+ rows), `Matched_Keys`, `Validation_sample10pct.txt`
- **HH_aggregation**: `Full_Aggregated` (15M+ rows), `Validation_HH`, `Validation_Plot.png`
- **occToBEM**: `BEM_Schedules` (600K+ rows), two validation plots

#### Validation quality (from the .txt reports)

- Tier distribution is healthy — Tier 4 (FailSafe) is only 2.9% WD / 7.9% WE
- All 54,548 person-days have exactly 288 time slots (5-min resolution)
- No social density logic errors
- BEM output has the expected columns: `SIM_HH_ID`, `Day_Type`, `Hour`, `Occupancy_Schedule`, `Metabolic_Rate`, etc.

**The pipeline completed correctly end-to-end. All expected files exist, row counts match the plan's documented values, and the validation reports are clean.**
