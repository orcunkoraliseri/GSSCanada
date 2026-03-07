# Presence & Co-Presence Harmonization Plan
## Mapping Location Codes → 18 Unified `occPRE` and Social Contact → 8 Unified Co-Presence Columns

---

## Goal

Apply the user's pre-built harmonization for two episode-level variable groups:

1. **Presence (`occPRE`)** — Map 4 cycle-specific location coding schemes to a **unified 18-category** location scheme
2. **Co-Presence** — Consolidate 10+ cycle-specific social contact columns to **8 unified binary** co-presence columns

**Primary data sources** (user-provided, read-only):

| File | Content |
|---|---|
| [presenceCategories - execution.xlsx](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data%20Harmonization_presenceCategories%20-%20execution.xlsx) | 3 sheets with clean `[Edited Location, Location]` lookup tables |
| [Category-CoPresence.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data%20Harmonization%20-%20Category-CoPresence.csv) | Per-cycle social contact column mappings and unified names |

---

## Part A — Presence (Location) Harmonization

### Excel Workbook Structure

The workbook has **3 sheets** with identical structure:

| Column | Content |
|---|---|
| `Edited Location` | Target unified code (1–18) |
| `Location` | Raw cycle-specific PLACE/LOCATION code |

### Per-Sheet Statistics

| Sheet | Rows | Raw Code Range |
|---|---|---|
| `2005-2010codebook` | 24 | PLACE 1–99 |
| `2015codebook` | 27 | LOCATION 300–999 |
| `2022codebook` | 29 | LOCATION 3300–9999 |

### The 18-Category Location Scheme (from execution workbook)

| `occPRE` | Location | 2005/2010 `PLACE` | 2015 `LOCATION` | 2022 `LOCATION` |
|---|---|---|---|---|
| 1 | Home | 1 | 300 | 3300 |
| 2 | Work / School | 2, 8 | 301, 302 | 3301, 3302 |
| 3 | Other home | 3 | 303 | 3303 |
| 4 | Outdoor | 9 | 304, 305 | 3304, 3305 |
| 5 | Shopping (grocery / store / mall) | 6, 7 | 306 | 3306 |
| 6 | Library, museum or theatre | 10 | 307 | 3307 |
| 7 | Restaurant, bar or club | 4 | 309 | 3309 |
| 8 | Place of worship | 5 | 310 | 3310 |
| 9 | Other / Elsewhere | 11 | 308, 311, 312 | 3308, 3311, 3312 |
| 10 | Travel — Car (driver) | 12 | 313 | 3313 |
| 11 | Travel — Car (passenger) | 13 | 314 | 3314 |
| 12 | Travel — Walk | 14 | 315 | 3315 |
| 13 | Travel — Public transit | 15, 16, 18 | 316, 320 | 3316 |
| 14 | Travel — Airplane | 20 | 317 | 3317 |
| 15 | Travel — Bicycle | 17 | 318 | 3318 |
| 16 | Travel — Taxi / Limousine | 19 | 319 | 3320 |
| 17 | Travel — Other | 21 | 321 | 3319, 3323, 3399 |
| 18 | Skip / Not stated | 97, 98, 99 | 996, 997, 998, 999 | 9996, 9997, 9998, 9999 |

> [!NOTE]
> **Key differences from the earlier CSV-based plan** (now corrected per execution workbook):
> - `PLACE 18` (Boat/ferry) → **13** (Public transit), not 17 (Travel-Other)
> - `302` / `3302` (Away on business) → **2** (Work/School) ✅ resolved
> - `3399` (Travel - not stated) → **17** (Travel-Other), not 18 (Skip)

### Update to Existing `occPRE` Definition

The existing `02_harmonizationGSS.md` defined `occPRE` as binary (home=1, not-home=0). This plan **replaces** that with the granular 18-category scheme + a derived `AT_HOME` binary column:

```python
episode_df["AT_HOME"] = (episode_df["occPRE"] == 1).astype(int)
```

### Implementation

```python
import openpyxl

PRESENCE_EXCEL = (
    "references_Pre_coPre_Codes/"
    "Data Harmonization_presenceCategories - execution.xlsx"
)

PRES_SHEET_CYCLE_MAP: dict[str, list[int]] = {
    "2005-2010codebook": [2005, 2010],  # Same mapping for both cycles
    "2015codebook": [2015],
    "2022codebook": [2022],
}


def build_presence_crosswalks(
    excel_path: str,
) -> dict[int, dict[int, int]]:
    """Build {cycle_year: {raw_location_code: occPRE}} from the execution Excel.

    Args:
        excel_path: Path to the presence execution workbook.

    Returns:
        Dictionary mapping cycle years to their raw-code→occPRE lookups.
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    crosswalks: dict[int, dict[int, int]] = {}

    for sheet_name, cycle_years in PRES_SHEET_CYCLE_MAP.items():
        ws = wb[sheet_name]
        lookup: dict[int, int] = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            unified = int(row[0])
            raw_code = int(row[1])
            lookup[raw_code] = unified
        # Same lookup for all cycles sharing this sheet
        for year in cycle_years:
            crosswalks[year] = lookup

    return crosswalks


def apply_presence_crosswalk(
    episode_df: pd.DataFrame,
    cycle_year: int,
    crosswalk: dict[int, int],
) -> pd.DataFrame:
    """Map raw location codes to unified 18-category occPRE.

    Args:
        episode_df: Episode DataFrame with raw location column.
        cycle_year: Survey cycle year.
        crosswalk: {raw_code: occPRE} lookup dictionary.

    Returns:
        DataFrame with 'occPRE' (1–18), 'occPRE_raw' (original code),
        and 'AT_HOME' (derived binary flag).
    """
    raw_col = "PLACE" if cycle_year in (2005, 2010) else "LOCATION"
    episode_df["occPRE_raw"] = episode_df[raw_col]
    episode_df["occPRE"] = episode_df[raw_col].map(crosswalk)
    episode_df["AT_HOME"] = (episode_df["occPRE"] == 1).astype(int)
    return episode_df
```

### Columns Added to Episode CSVs

| Column | Type | Description |
|---|---|---|
| `occPRE` | `int` (1–18) | Unified 18-category location code |
| `occPRE_raw` | `int` | Original cycle-specific PLACE/LOCATION code |
| `AT_HOME` | `int` (0 or 1) | Derived binary flag: 1 if `occPRE == 1` |

---

## Part B — Co-Presence Harmonization

### Source Columns Per Cycle

**2005 / 2010** — 10 columns (values: 1=Yes, 2=No, 7=Not asked, 8=Not stated, 9=Don't know):

| Source Column | Description |
|---|---|
| `ALONE` | Social contacts — alone? |
| `SPOUSE` | With spouse/partner? |
| `CHILDHSD` | With HH children < 15? |
| `FRIENDS` | With friends outside HH? |
| `OTHFAM` | With other family outside HH? |
| `NHSDCL15` | With respondent's children outside HH, < 15? |
| `NHSDC15P` | With respondent's children outside HH, ≥ 15? |
| `OTHERS` | With others outside HH? |
| `PARHSD` | With parents/in-laws in HH? |
| `MEMBHSD` | With other HH members (children ≥ 15)? |

**2015 / 2022** — 10 columns (values: 1=Yes, 2=No, 9=Not stated):

| Source Column | Description |
|---|---|
| `TUI_06A` | Alone? |
| `TUI_06B` | With spouse/partner? |
| `TUI_06C` | With HH children < 15? |
| `TUI_06D` | With HH children ≥ 15? |
| `TUI_06E` | With parents/in-laws? |
| `TUI_06F` | With other HH adults? |
| `TUI_06G` | With other family from other HHs? |
| `TUI_06H` | With friends? |
| `TUI_06I` | With colleagues/classmates? |
| `TUI_06J` | With other people? |

### The 8 Unified Co-Presence Columns

| Unified Column | Description | 2005/2010 Source | 2015/2022 Source | Values |
|---|---|---|---|---|
| `Alone` | Was respondent alone? | `ALONE` | `TUI_06A` | 1 = Yes, 2 = No, NaN = Not stated |
| `Spouse` | With spouse/partner? | `SPOUSE` | `TUI_06B` | 1/2/NaN |
| `Children` | With HH children < 15? | `CHILDHSD` | `TUI_06C` | 1/2/NaN |
| `friends` | With friends? | `FRIENDS` | `TUI_06H` | 1/2/NaN |
| `otherHHs` | With other family from other HHs? | `OTHFAM` | `TUI_06G` | 1/2/NaN |
| `others` | With other people? | `OTHERS` | `TUI_06J` | 1/2/NaN |
| `parents` | With parents/in-laws? | `PARHSD` | `TUI_06E` | 1/2/NaN |
| `otherInFAMs` | With other HH members (≥ 15)? | `MEMBHSD` | `TUI_06D` | 1/2/NaN |

### Column Consolidation Rules

**Dropped 2005/2010 columns** (no equivalent in 2015/2022):

| Column | Reason |
|---|---|
| `NHSDCL15` | Respondent's children outside HH < 15 — no 2015/2022 equivalent |
| `NHSDC15P` | Respondent's children outside HH ≥ 15 — no 2015/2022 equivalent |
| `NHSDPAR` | Parents/in-laws outside HH — merged with `parents` |

**Dropped 2015/2022 columns** (not mapped to unified scheme):

| Column | Reason |
|---|---|
| `TUI_06F` | Other HH adults — no direct 2005/2010 equivalent |
| `TUI_06I` | Colleagues/classmates — no 2005/2010 equivalent |

### Sentinel Value Handling

| Value | 2005/2010 Meaning | 2015/2022 Meaning | Unified Handling |
|---|---|---|---|
| 1 | Yes | Yes | **1** (Yes) |
| 2 | No | No | **2** (No) |
| 7 | Not asked | *(not used)* | **NaN** |
| 8 | Not stated | *(not used)* | **NaN** |
| 9 | Don't know | Not stated | **NaN** |

### Implementation

```python
COPRESENCE_MAP: dict[int, dict[str, str]] = {
    2005: {
        "ALONE": "Alone", "SPOUSE": "Spouse", "CHILDHSD": "Children",
        "FRIENDS": "friends", "OTHFAM": "otherHHs", "OTHERS": "others",
        "PARHSD": "parents", "MEMBHSD": "otherInFAMs",
    },
    2010: {
        "ALONE": "Alone", "SPOUSE": "Spouse", "CHILDHSD": "Children",
        "FRIENDS": "friends", "OTHFAM": "otherHHs", "OTHERS": "others",
        "PARHSD": "parents", "MEMBHSD": "otherInFAMs",
    },
    2015: {
        "TUI_06A": "Alone", "TUI_06B": "Spouse", "TUI_06C": "Children",
        "TUI_06H": "friends", "TUI_06G": "otherHHs", "TUI_06J": "others",
        "TUI_06E": "parents", "TUI_06D": "otherInFAMs",
    },
    2022: {
        "TUI_06A": "Alone", "TUI_06B": "Spouse", "TUI_06C": "Children",
        "TUI_06H": "friends", "TUI_06G": "otherHHs", "TUI_06J": "others",
        "TUI_06E": "parents", "TUI_06D": "otherInFAMs",
    },
}


def harmonize_copresence(
    episode_df: pd.DataFrame,
    cycle_year: int,
) -> pd.DataFrame:
    """Rename and clean co-presence columns to unified scheme.

    Args:
        episode_df: Episode DataFrame with raw social contact columns.
        cycle_year: Survey cycle year.

    Returns:
        DataFrame with 8 unified co-presence columns.
        Sentinel values (7, 8, 9) converted to NaN.
    """
    rename_map = COPRESENCE_MAP[cycle_year]
    episode_df = episode_df.rename(columns=rename_map)

    # Drop source columns not in the unified scheme
    cols_to_drop = [
        c for c in episode_df.columns
        if c.startswith(("NHSD", "TUI_06"))
        and c not in rename_map.values()
    ]
    episode_df = episode_df.drop(columns=cols_to_drop, errors="ignore")

    # Convert sentinels to NaN
    unified_cols = list(rename_map.values())
    for col in unified_cols:
        episode_df[col] = episode_df[col].replace(
            {7: pd.NA, 8: pd.NA, 9: pd.NA}
        )

    return episode_df
```

---

## Integration with `02_harmonizeGSS.py`

Both presence and co-presence harmonization will be called within the episode harmonization pipeline:

```python
def harmonize_episode(
    episode_df: pd.DataFrame,
    cycle_year: int,
) -> pd.DataFrame:
    """Full episode harmonization pipeline.

    Order of operations:
    1. apply_activity_crosswalk()     → occACT, occACT_raw
    2. apply_presence_crosswalk()     → occPRE, occPRE_raw, AT_HOME
    3. harmonize_copresence()         → Alone, Spouse, Children, ...
    4. time column rename             → start, end
    5. check_diary_closure()          → DIARY_VALID
    """
    ...
```

---

## Validation Checks (to add to `02_harmonizeGSS_val.py`)

### Presence Validation

| Check | Logic | Pass Criteria |
|---|---|---|
| Unique `occPRE` values | `episode.occPRE.dropna().unique()` per cycle | Only {1, 2, …, 18} |
| Coverage | % of episodes with `occPRE` ∈ {1–17} (excluding 18) | ≥95% per cycle |
| Home rate | % of episodes with `occPRE == 1` | ~55–70% |
| Unmapped codes | Episodes where `occPRE` is NaN but `occPRE_raw` is not NaN | List with counts |
| AT_HOME ↔ occPRE | `AT_HOME == 1` iff `occPRE == 1` | 100% consistency |

### Co-Presence Validation

| Check | Logic | Pass Criteria |
|---|---|---|
| Unified columns present | All 8 co-presence columns exist in each cycle | ✅ all present |
| Value range | Each column's non-NaN values ∈ {1, 2} | True for all |
| Sentinel residuals | No values of 7, 8, or 9 remaining | Zero residuals |
| Alone consistency | When `Alone == 1`, all other co-presence cols should be 2 | ≥95% consistency |
| NaN rate | Per-column NaN% per cycle | <5% for core columns |

**Visual outputs:**
- **Stacked bar chart**: `occPRE` category distribution per cycle (18 categories × 4 cycles)
- **Grouped bar chart**: Co-presence Yes/No/NaN rates per column per cycle

---

## User Review

> [!NOTE]
> ✅ **`302`/`3302` resolved** — the execution workbook maps "Away on business" to **2** (Work/School).

> [!NOTE]
> ✅ **`occPRE` replaces binary `occPRE`** — granular 18-category scheme + derived `AT_HOME` column.

> [!NOTE]
> **Dropped co-presence columns**: 3 from 2005/2010 (`NHSDCL15`, `NHSDC15P`, `NHSDPAR`) and 2 from 2015/2022 (`TUI_06F`, `TUI_06I`) — their information is partially covered by the retained columns.
