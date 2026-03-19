# Column Naming Discrepancy — Investigation Plan

## Root Cause Analysis

There are **two separate causes** that together produce the confusion.

---

### Cause 1 — Step 1 keeps raw GSS names; Step 2 applies renaming

`01_readingGSS.py` is intentionally a "data collection only" step. It reads the raw
SPSS/SAS/DAT files and **saves columns under their original GSS names** without any
renaming. The raw names differ per cycle because Statistics Canada changed questionnaire
variable names across cycles:

| Unified Target | 2005 raw | 2010 raw | 2015 raw | 2022 raw |
|---|---|---|---|---|
| `SEX` | `sex` (lowercase) | `SEX` | `SEX` | `GENDER2` |
| `MARSTH` | `marstat` | `MARSTAT` | `MARSTAT` | `MARSTAT` |
| `LFTAG` | `LFSGSS` | `ACT7DAYS` | `ACT7DAYS` | `ACT7DAYC` |
| `PR` | `REGION` | `PRV` | `PRV` | `PRV` |

`02_harmonizeGSS.py` then applies `MAIN_RENAME_MAP` (per-cycle dictionaries) to produce
the unified schema (e.g. `SEX`, `MARSTH`, `AGEGRP`, etc.).

**Result:** The CSVs that feed the Step 1 validation contain raw names. The CSVs that
feed the Step 2 validation contain unified names → the reports look different.

---

### Cause 2 — Step 1 validation uses a separate human-readable label dictionary

In `01_readingGSS_val.py`, the `DEMO_VARS` dictionary (line 50–97) maps **human-friendly
labels** (e.g., `"Sex / Gender"`, `"Marital Status"`) to per-cycle raw column names.
These labels appear as the **y-axis row headers in Chart 3** of the Step 1 report.

The Step 2 validator (`02_harmonizeGSS_val.py`) uses the harmonized column names
directly (e.g., `"SEX"`, `"MARSTH"`) as labels in Chart 4, because all four cycles now
share the same schema.

**Result:** Chart 3 in Step 1 says `"Sex / Gender"` → Chart 4 in Step 2 says `"SEX"`.

---

## Is this a real problem?

The discrepancy is correct **by design** for the current pipeline structure:
- Step 1 = raw data, heterogeneous names per cycle.
- Step 2 = harmonized data, unified names.

However, the naming mismatch makes cross-step comparison harder and is a readability
concern. The pipeline documentation (`00_GSS_Occupancy_Documentation.md` Step 1A table)
already lists the **intended unified names** (`SEX`, `MARSTH`, etc.) for all columns —
suggesting the renaming was always meant to happen, just placed in Step 2 for separation
of concerns.

---

## Recommended Fix: Move Renaming Into Step 1

> [!IMPORTANT]
> **Design decision:** Move the per-cycle column renaming from `02_harmonizeGSS.py`
> (Phase G `harmonize_main`) into `01_readingGSS.py` (after reading). This means Step 1
> outputs already use the unified schema names. Step 2 then only needs to handle
> **category recoding**, **sentinel elimination**, and other harmonization logic — with
> no renaming step required.

### What changes

---

#### [MODIFY] [01_readingGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/01_readingGSS.py)

Add a `MAIN_RENAME_MAP` and `EPISODE_RENAME_MAP` constant (transplanted verbatim from
`02_harmonizeGSS.py`) near the top of the file, below `MAIN_COLS_*` constants.

Add a helper function `apply_rename_map(df, cycle)` that calls `df.rename(columns=...)`.

In `read_gss_main()` and `read_gss_episode()`, call `apply_rename_map()` on the
returned DataFrame before returning it.

The output CSVs (`main_2005.csv`, `main_2010.csv` etc.) will then use unified names.

**No logic change** — only renaming is moved. The values stay as raw GSS codes until
Step 2 recodes them.

---

#### [MODIFY] [02_harmonizeGSS.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS.py)

Remove `MAIN_RENAME_MAP` and `EPISODE_RENAME_MAP` constants (lines 17–114).

In `harmonize_main()` (around line 638), remove the `df.rename(columns=rename_dict)`
call — the columns are already renamed by Step 1.

In `harmonize_episode()` (around line 666), same: remove the rename call.

All recode functions (`recode_sex`, `recode_marsth`, etc.) already operate on the
**unified names** (`df["SEX"]`, `df["MARSTH"]`) — so they will work unchanged.

---

#### [MODIFY] [01_readingGSS_val.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/01_readingGSS_val.py)

Update the `DEMO_VARS` dictionary to use unified column names instead of raw per-cycle
names. Since Step 1 now outputs renamed columns, every cycle column reference becomes
the same unified name:

```python
# Before (raw per-cycle names)
"Sex / Gender": {"2005": "sex", "2010": "SEX", "2015": "SEX", "2022": "GENDER2"}

# After (unified name, same for all cycles)
"SEX": {"2005": "SEX", "2010": "SEX", "2015": "SEX", "2022": "SEX"}
```

Apply the same update for all other variables in `DEMO_VARS`.
Also update `EXPECTED_MAIN_COLS` and `EXPECTED_EPISODE_COLS` to use the new unified names
so the schema audit (Method 1) still passes.

The human-friendly row labels (e.g. `"Sex / Gender"`) can be kept as dictionary keys
but should be consistent with the Step 2 label so the two reports tell the same story.
Alternatively, switch to using the unified code names as keys to exactly match the
Step 2 report — your choice.

---

#### [MODIFY] [02_harmonizeGSS_val.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS_val.py)

`STEP1_SEX_COL` (line 51) maps cycles to their raw sex column name for the regression
check. After the fix, Step 1 already outputs `"SEX"` for all cycles, so this dict
becomes `{2005: "SEX", 2010: "SEX", 2015: "SEX", 2022: "SEX"}`. Update accordingly.

---

## Verification Plan

### Automated (terminal commands)

Run Step 1 after the changes and compare output column names:

```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp
python 01_readingGSS.py
```

Check that `outputs/main_2005.csv` (and other cycles) now have column `SEX` instead of
`sex`, `MARSTH` instead of `marstat`, etc.:

```bash
python -c "
import pandas as pd
for year in [2005, 2010, 2015, 2022]:
    df = pd.read_csv(f'outputs/main_{year}.csv', nrows=1)
    print(year, df.columns.tolist())
"
```

Then run Step 2 and verify no row count changes and all harmonized columns present:

```bash
python 02_harmonizeGSS.py
```

Inspect that both validation HTML reports (re-generated automatically) now use the same
column labels in their charts.

### Manual Verification

Open both HTML reports side-by-side in a browser and confirm:
- Chart 3 y-axis labels in `step1_validation_report.html` match Chart 4 y-axis labels
  in `step2_validation_report.html`.
- Row counts in both reports are unchanged from before the fix.
- No new failures or errors appear in either report's scorecard.

```
open /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs/step1_validation_report.html
open /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/outputs_step2/step2_validation_report.html
```
