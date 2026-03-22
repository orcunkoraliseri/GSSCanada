# Co-Presence Integration Plan — Steps 1 / 2 / 3 + Validation

**Status:** Draft
**Date:** 2026-03-22
**Scope:** End-to-end fix: expose all raw co-presence columns in Step 1, OR-merge unmapped variants in Step 2, confirm flow-through in Step 3, add plots in all three validation reports.

---

## 1. Problem Statement

### 1.1 What the user observes
Running Step 3 produces `merged_episodes.csv` that contains the 8 unified co-presence columns (`Alone`, `Spouse`, `Children`, `parents`, `otherInFAMs`, `otherHHs`, `friends`, `others`). However **three 2005/2010 columns and two 2015/2022 columns that capture additional social contacts are currently silently dropped** in `harmonize_copresence()` rather than being merged into the unified schema:

| Dropped column | Cycle | Concept | Currently |
|---|---|---|---|
| `NHSDCL15` | 2005, 2010 | Children of respondent outside HH, < 15 yrs | Dropped |
| `NHSDC15P` | 2005, 2010 | Children of respondent outside HH, ≥ 15 yrs | Dropped |
| `NHSDPAR` | 2005, 2010 | Parents / parents-in-law outside HH | Dropped |
| `TUI_06F` | 2015, 2022 | Other household adult(s) | Dropped |
| `TUI_06I` | 2015, 2022 | Colleague(s) / classmate(s) | Dropped |

Additionally, **no co-presence plots exist in any validation report**, making it impossible to visually inspect data quality.

### 1.2 Root cause in `harmonize_copresence()` (02_harmonizeGSS.py L454–468)
```python
cols_to_drop = [
    c
    for c in df.columns
    if c.startswith(("NHSD", "TUI_06")) and c not in rename_map.values()
]
df = df.drop(columns=cols_to_drop, errors="ignore")
```
This pattern drops **all** NHSD* and TUI_06* columns that aren't in the rename target list, discarding potentially valid social-contact information.

---

## 2. Reference: Harmonization CSV

Source: `references_Pre_coPre_Codes/Data Harmonization - Category-CoPresence.csv`

The reference establishes the **8 unified columns** and their value scheme:
- Values: `1` = Yes (present), `2` = No, `9` → `NaN` (missing)
- 2005/2010 extras {7, 8} also map to `NaN`

Full raw-to-unified mapping:

| 2005/2010 Raw | 2015/2022 Raw | Unified Column | Status |
|---|---|---|---|
| `ALONE` | `TUI_06A` | `Alone` | Currently mapped |
| `SPOUSE` | `TUI_06B` | `Spouse` | Currently mapped |
| `CHILDHSD` | `TUI_06C` | `Children` | Currently mapped |
| `FRIENDS` | `TUI_06H` | `friends` | Currently mapped |
| `OTHFAM` | `TUI_06G` | `otherHHs` | Currently mapped |
| `OTHERS` | `TUI_06J` | `others` | Currently mapped |
| `PARHSD` | `TUI_06E` | `parents` | Currently mapped |
| `MEMBHSD` | `TUI_06D` | `otherInFAMs` | Currently mapped |
| `NHSDCL15` | _(none)_ | `Children` | **Plan: OR-merge** |
| `NHSDC15P` | _(none)_ | `otherInFAMs` | **Plan: OR-merge** |
| `NHSDPAR` | _(none)_ | `parents` | **Plan: OR-merge** |
| _(none)_ | `TUI_06F` | `otherInFAMs` | **Plan: OR-merge** |
| _(none)_ | `TUI_06I` | `colleagues` | **Plan: new column** |

---

## 3. Harmonization Strategy for Unmapped Columns

### 3.1 OR-merge logic
For binary 1/2/NaN columns, OR-merge means: the unified column equals `1` if **any** contributing raw column equals `1`, else `2` if all are non-missing and none is `1`, else `NaN`.

```
unified = 1   if any(raw_i == 1)
unified = 2   if all(raw_i ∈ {2, NaN}) and at least one is 2
unified = NaN if all contributing columns are NaN
```

Implementation helper (new function `or_merge_copresence`):
```python
def or_merge_copresence(df, target_col, source_cols):
    """OR-merge multiple binary (1/2/NaN) columns into target_col."""
    available = [c for c in source_cols if c in df.columns]
    if not available:
        return df
    # Convert to bool: True = present (value == 1)
    presence = df[available].apply(lambda s: s == 1)
    # If any source is 1 → 1; if all sources are 2 → 2; else NaN
    any_present = presence.any(axis=1)
    all_absent  = (df[available] == 2).all(axis=1)
    result = pd.Series(pd.NA, index=df.index, dtype="Int8")
    result[any_present] = 1
    result[~any_present & all_absent] = 2
    df[target_col] = result
    return df
```

### 3.2 Per-column strategy

#### 2005 & 2010
| Target Unified Col | Sources to OR-merge | Rationale |
|---|---|---|
| `Children` | `CHILDHSD`, `NHSDCL15` | Both capture children < 15 (in-HH vs out-HH) |
| `parents` | `PARHSD`, `NHSDPAR` | Both capture parents (in-HH vs out-HH) |
| `otherInFAMs` | `MEMBHSD`, `NHSDC15P` | MEMBHSD = HH members ≥15; NHSDC15P = respondent's children ≥15 outside HH |

**After OR-merge, drop:** `NHSDCL15`, `NHSDC15P`, `NHSDPAR`

#### 2015 & 2022
| Target Unified Col | Sources to OR-merge | Rationale |
|---|---|---|
| `otherInFAMs` | `TUI_06D`, `TUI_06F` | TUI_06D = HH children ≥15; TUI_06F = other HH adults → both are non-primary HH members |
| `colleagues` | `TUI_06I` | Unique category; NaN-fill for 2005/2010 |

**After OR-merge, drop:** `TUI_06D` (merged into otherInFAMs), `TUI_06F` (merged), `TUI_06I` (merged into colleagues)

### 3.3 New unified column: `colleagues`
Add `colleagues` to the 8-column schema → **9 unified columns total**.
- Source: `TUI_06I` (2015, 2022)
- 2005, 2010: always `NaN` (concept not measured)
- Add to `EPISODE_COMMON_COLS` in Step 3.

---

## 4. Implementation Tasks by File

---

### 4.1  `01_readingGSS.py` — Step 1

**What needs to change:** Nothing structural — all unmapped raw columns are already in the `EPISODE_COLS_*` lists. Verify the final CSV outputs contain them.

**Verification checklist:**
- [ ] `NHSDCL15`, `NHSDC15P`, `NHSDPAR` present in `outputs_step1/episode_2005.csv` and `episode_2010.csv`
- [ ] `TUI_06F`, `TUI_06I` present in `outputs_step1/episode_2015.csv` and `episode_2022.csv`
- [ ] Values are raw (1/2/7/8/9) — no recoding at this step

**No code changes required** unless verification shows a column was accidentally omitted from an `EPISODE_COLS_*` list.

---

### 4.2  `02_harmonizeGSS.py` — Step 2

#### Change 1: Add `or_merge_copresence` helper (insert before `harmonize_copresence`)

```python
def or_merge_copresence(
    df: pd.DataFrame, target_col: str, source_cols: list[str]
) -> pd.DataFrame:
    """OR-merge binary (1/2/NaN) source columns into target_col.

    Rules:
        result = 1   if any source == 1
        result = 2   if no source == 1 and at least one source == 2
        result = NaN if all sources are NaN
    """
    available = [c for c in source_cols if c in df.columns]
    if not available:
        return df
    any_present  = (df[available] == 1).any(axis=1)
    any_absent   = (df[available] == 2).any(axis=1)
    result = pd.Series(pd.NA, index=df.index, dtype="Int8")
    result[any_present] = 1
    result[~any_present & any_absent] = 2
    df[target_col] = result
    return df
```

#### Change 2: Replace `harmonize_copresence` body

**Current logic (L454–468):** renames, drops all NHSD*/TUI_06* that aren't rename targets, replaces {7,8,9} → NaN.

**New logic:**

```python
def harmonize_copresence(df: pd.DataFrame, cycle: int) -> pd.DataFrame:
    rename_map = COPRESENCE_MAP.get(cycle, {})

    # Step A: Standardize missing codes BEFORE rename (so names are consistent)
    all_raw_copre = list(rename_map.keys()) + (
        ["NHSDCL15", "NHSDC15P", "NHSDPAR"] if cycle in (2005, 2010)
        else ["TUI_06F", "TUI_06I"]
    )
    for col in all_raw_copre:
        if col in df.columns:
            df[col] = df[col].replace({7: pd.NA, 8: pd.NA, 9: pd.NA})

    # Step B: Rename primary columns to unified names
    df = df.rename(columns=rename_map)

    # Step C: OR-merge unmapped columns into existing unified columns
    if cycle in (2005, 2010):
        df = or_merge_copresence(df, "Children",    ["Children",    "NHSDCL15"])
        df = or_merge_copresence(df, "parents",     ["parents",     "NHSDPAR"])
        df = or_merge_copresence(df, "otherInFAMs", ["otherInFAMs", "NHSDC15P"])
        df["colleagues"] = pd.NA
    else:  # 2015, 2022
        df = or_merge_copresence(df, "otherInFAMs", ["otherInFAMs", "TUI_06F"])
        if "TUI_06I" in df.columns:
            df["colleagues"] = df["TUI_06I"].copy()
        else:
            df["colleagues"] = pd.NA

    # Step D: Drop all residual raw co-presence columns
    raw_to_drop = [
        c for c in df.columns
        if c in {"NHSDCL15", "NHSDC15P", "NHSDPAR", "TUI_06D", "TUI_06F", "TUI_06I"}
    ]
    df = df.drop(columns=raw_to_drop, errors="ignore")

    return df
```

#### Change 3: Update `COPRESENCE_MAP` — add `TUI_06D` back as a primary rename (it feeds `otherInFAMs` before OR-merge)

No change needed in `COPRESENCE_MAP` — `TUI_06D → otherInFAMs` is already there. The OR-merge in Step C will read the already-renamed `otherInFAMs` alongside the raw `TUI_06F`.

**Note:** The rename map renames `TUI_06D → otherInFAMs` first (Step B), so in Step C we OR-merge `["otherInFAMs", "TUI_06F"]` — `TUI_06F` is still raw at that point. This ordering is correct.

---

### 4.3  `02_harmonizeGSS_val.py` — Step 2 Validation

Add a new section **"Co-Presence Quality Report"** to the HTML output.

#### Plots to add (per cycle, in a tabbed or per-cycle layout):

**Plot 1 — Co-presence prevalence bar chart**
- X-axis: unified column names (Alone, Spouse, Children, parents, otherInFAMs, otherHHs, friends, others, colleagues)
- Y-axis: % of episodes where value = 1 (presence = Yes), weighted by `WGHT_EPI`
- One grouped bar per cycle (2005, 2010, 2015, 2022)
- Use matplotlib or plotly; save to HTML as inline figure
- Title: `"Co-presence prevalence by category and cycle (weighted % of episodes)"`

**Plot 2 — Missing rate heatmap**
- Rows: unified co-presence columns
- Columns: cycles
- Cell value: % NaN
- Color: sequential (white = 0%, dark red = 100%)
- Helps identify whether unmapped columns are now correctly populated vs still NaN

**Plot 3 — "Alone vs. With Someone" pie / bar per cycle**
- Two bars per cycle: `Alone=1` share vs `Alone=2` share (excluding NaN)
- Validates that the solo/social split is plausible across cycles

**Plot 4 — colleagues column coverage (2015/2022 only)**
- Bar showing % present/absent/missing for `colleagues` in 2015 and 2022
- Confirm `colleagues` is NaN for 2005/2010

#### Implementation notes for val.py:
- Load `outputs_step2/episode_{year}.csv` for each cycle
- Combine into one df with `CYCLE_YEAR` column
- Use `plotly.graph_objects` or `matplotlib` + base64 embedding consistent with existing val pattern
- Insert HTML section after the existing column-presence table

---

### 4.4  `03_mergingGSS.py` — Step 3

#### Change 1: Add `colleagues` to `EPISODE_COMMON_COLS`

```python
EPISODE_COMMON_COLS = [
    "occID",
    "EPINO",
    "WGHT_EPI",
    "start",
    "end",
    "duration",
    "occACT_raw",
    "occACT",
    "occACT_label",
    "occPRE_raw",
    "occPRE",
    "AT_HOME",
    # Co-presence
    "Alone",
    "Spouse",
    "Children",
    "parents",
    "otherInFAMs",
    "otherHHs",
    "friends",
    "others",
    "colleagues",     # ← ADD: TUI_06I from 2015/2022; NaN for 2005/2010
    # Auxiliary (optional)
    "TUI_07",
    # QA flag
    "DIARY_VALID",
    "CYCLE_YEAR",
]
```

`standardize_columns()` already handles missing columns by filling `pd.NA`, so `colleagues` will correctly appear as `NaN` for 2005/2010 if the column is absent in those cycle files.

#### Change 2: No merge logic changes needed
The co-presence columns survive the LEFT JOIN untouched — they are episode-level and are not join keys. No additional action required.

---

### 4.5  `03_mergingGSS_val.py` — Step 3 Validation

Add a new section **"Co-Presence in Merged Dataset"** to the step 3 HTML report.

#### Plots to add:

**Plot 1 — Co-presence column completeness across all cycles**
- A horizontal bar or heatmap: for each co-presence column, show % non-NaN rows split by `CYCLE_YEAR`
- Validates that the OR-merge preserved more data than the old drop approach

**Plot 2 — Weighted co-presence prevalence (full merged set)**
- Same format as Step 2 Plot 1 but using the merged dataset (verifies no data loss from join)
- Grouped bars by cycle, weighted by `WGHT_EPI`

**Plot 3 — Alone vs. not-alone over time of day**
- X-axis: episode start hour (0–23)
- Y-axis: % of episodes where `Alone=1`
- Line per cycle
- Validates temporal plausibility (people less alone during working hours, more alone overnight)

**Plot 4 — Co-presence composition by activity category**
- X-axis: top 10 most frequent `occACT_label` values
- For each activity: stacked bar showing proportion of episodes with each social contact type
- Validates semantic plausibility (e.g., work activities → high `colleagues`, family activities → high `Children`/`Spouse`)

---

### 4.6  `01_readingGSS_val.py` — Step 1 Validation

Add a new section **"Co-Presence Raw Column Coverage"** at the end of the Step 1 report.

#### Plots to add:

**Plot 1 — Raw column presence table**
- For each cycle, show which raw co-presence columns exist and their unique value sets
- Columns: `ALONE/TUI_06A`, `SPOUSE/TUI_06B`, `CHILDHSD/TUI_06C`, `NHSDCL15`, `NHSDC15P`, `NHSDPAR`, `TUI_06D`, `TUI_06E`, `TUI_06F`, `TUI_06G`, `TUI_06H`, `TUI_06I`, `TUI_06J`, `MEMBHSD`, `OTHERS/TUI_06J`, `PARHSD/TUI_06E`
- Rows: 2005, 2010, 2015, 2022
- Cell: green if column present, red if absent

**Plot 2 — Raw missing rate per co-presence column per cycle**
- Heatmap (missing value % before any recoding)
- Highlights where {7, 8, 9} contribute to overall missing after harmonization

---

## 5. Unified Co-Presence Schema (Final — 9 columns)

| Column | Type | Values | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|---|---|
| `Alone` | Int8 | 1/2/NaN | ✓ | ✓ | ✓ | ✓ |
| `Spouse` | Int8 | 1/2/NaN | ✓ | ✓ | ✓ | ✓ |
| `Children` | Int8 | 1/2/NaN | ✓ (OR-merged) | ✓ (OR-merged) | ✓ | ✓ |
| `parents` | Int8 | 1/2/NaN | ✓ (OR-merged) | ✓ (OR-merged) | ✓ | ✓ |
| `otherInFAMs` | Int8 | 1/2/NaN | ✓ (OR-merged) | ✓ (OR-merged) | ✓ (OR-merged) | ✓ (OR-merged) |
| `otherHHs` | Int8 | 1/2/NaN | ✓ | ✓ | ✓ | ✓ |
| `friends` | Int8 | 1/2/NaN | ✓ | ✓ | ✓ | ✓ |
| `others` | Int8 | 1/2/NaN | ✓ | ✓ | ✓ | ✓ |
| `colleagues` | Int8 | 1/2/NaN | NaN | NaN | ✓ | ✓ |

---

## 6. OR-Merge Semantics — Why This Is Valid

| Target | 2005/2010 OR sources | Justification |
|---|---|---|
| `Children` | `CHILDHSD` + `NHSDCL15` | Both are "children of respondent under 15" — the distinction (in-HH vs. out-HH) is not present in 2015/2022 schema, so merging avoids systematic under-counting for 2005/2010 |
| `parents` | `PARHSD` + `NHSDPAR` | Same rationale — 2015/2022 `TUI_06E` captures all parents regardless of HH membership |
| `otherInFAMs` | `MEMBHSD` + `NHSDC15P` (2005/2010); `TUI_06D` + `TUI_06F` (2015/2022) | Both capture HH-adult members; merging avoids under-counting |
| `colleagues` | `TUI_06I` only (2015/2022) | No equivalent in 2005/2010; represent as NaN rather than forcing a spurious merge |

**Important cross-cycle caveat:** After OR-merging, `Children`, `parents`, and `otherInFAMs` are **semantically broader** in 2005/2010 than before (they now include out-of-HH members). Document this in the validation report. Users comparing raw prevalence across cycles should be aware of this expanded scope.

---

## 7. Execution Order

```
1. python 01_readingGSS.py        # verify raw columns are preserved
2. python 02_harmonizeGSS.py      # OR-merge + colleagues column added
3. python 02_harmonizeGSS_val.py  # check co-presence plots Step 2
4. python 03_mergingGSS.py        # colleagues added to EPISODE_COMMON_COLS
5. python 03_mergingGSS_val.py    # check co-presence plots Step 3
```

---

## 8. Acceptance Criteria

- [ ] `outputs_step2/episode_2005.csv` and `episode_2010.csv`: columns `Children`, `parents`, `otherInFAMs` have MORE non-NaN rows than before (OR-merge increases coverage)
- [ ] `outputs_step2/episode_2015.csv` and `episode_2022.csv`: column `colleagues` is populated (not all-NaN)
- [ ] `outputs_step2/episode_2005.csv` and `episode_2010.csv`: column `colleagues` is all-NaN
- [ ] `outputs_step3/merged_episodes.csv`: 9 co-presence columns present, `colleagues` all-NaN for 2005/2010 rows, non-NaN for 2015/2022 rows
- [ ] Step 1 validation HTML: new "Co-Presence Raw Column Coverage" section present
- [ ] Step 2 validation HTML: 4 co-presence plots visible (prevalence bar, missing heatmap, alone pie, colleagues bar)
- [ ] Step 3 validation HTML: 4 co-presence plots visible (completeness, weighted prevalence, alone-over-time, activity composition)
- [ ] No regression in existing Step 3 validation checks (DIARY_VALID, row counts, HETUS slot counts)
