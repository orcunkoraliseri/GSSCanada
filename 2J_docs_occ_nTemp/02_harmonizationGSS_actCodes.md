# Activity Code Crosswalk Implementation Plan
## Mapping 4 Coding Schemes → 14 Unified `occACT` Categories

---

## Goal

Apply the user's pre-built activity harmonization to map all four cycle-specific activity coding schemes to a **unified 14-category scheme**. The crosswalk is defined in an Excel workbook with one sheet per cycle — each sheet is a clean, conflict-free lookup table ready for direct ingestion.

**Primary data source** (user-provided, read-only):

| File | Content |
|---|---|
| [activityCategories - execution.xlsx](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_activityCodes/Data%20Harmonization_activityCategories%20-%20execution.xlsx) | 4 sheets (one per cycle), each with `[Edited Main Category, Main Activity, Explanation]` |

**Supporting reference files** (for context/documentation only):

| File | Content |
|---|---|
| [mainActivityCategoryList.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_activityCodes/Data%20Harmonization%20-%20mainActivityCategoryList.csv) | 14 main category definitions with descriptions + exceptions |
| [Category-Occ_Act.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_activityCodes/Data%20Harmonization%20-%20Category-Occ_Act.csv) | Multi-cycle side-by-side mapping (for documentation) |
| [GSS_ActList.csv](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/references_activityCodes/Data%20Harmonization%20-%20GSS_ActList.csv) | Full hierarchical code trees for all 4 cycles |

---

## The 14-Category Target Scheme

| `occACT` | Category Name | Description |
|---|---|---|
| 1 | Work & Related | Paid/unpaid work, job searching, overtime, work-related breaks |
| 2 | Household Work & Maintenance | Cooking, cleaning, laundry, repairs, gardening, pet care |
| 3 | Caregiving & Help | Caring for children, adults, or non-household members |
| 4 | Purchasing Goods & Services | Shopping, errands, personal/financial/government/medical services |
| 5 | Sleep & Naps & Resting | Night sleep, naps, lying down |
| 6 | Eating & Drinking | All eating and drinking activities |
| 7 | Personal Care | Grooming, hygiene, personal medical care |
| 8 | Education | Classes, studying, homework, training events |
| 9 | Socializing | Visiting, parties, weddings, bars, clubs |
| 10 | Passive Leisure | Relaxing, reading, watching TV, gaming, music |
| 11 | Active Leisure | Sports, exercise, hobbies, outdoor recreation |
| 12 | Community & Volunteer | Civic participation, religious services, volunteering |
| 13 | Travel | All travel between locations for any purpose |
| 14 | Miscellaneous / Idle | Waiting, unspecified, or unclassifiable time |

---

## Excel Workbook Structure

The workbook has **4 sheets**, one per cycle. Each sheet has identical structure:

| Column | Content | Example |
|---|---|---|
| `Edited Main Category` | Target category code (1–14) | `5` |
| `Main Activity` | Raw cycle-specific code | `450` (2005), `450.0` (2010), `1` (2015), `101` (2022) |
| `Explanation` | Activity label/description | `Night sleep/essential sleep` |

### Per-Sheet Statistics

| Sheet | Rows | Code Range | Conflicts |
|---|---|---|---|
| `2005codebook` | 183 | 2.0 – 995.0 (integer ACTCODE) | **Zero** ✅ |
| `2010codebook` | 263 | 11.0 – 995.0 (float ACTCODE with decimals) | **Zero** ✅ |
| `2015codebook` | 64 | 1.0 – 95.0 (integer TUI_01) | **Zero** ✅ |
| `2022codebook` | 120 | 101.0 – 9999.0 (integer TUI_01) | **Zero** ✅ |

> [!NOTE]
> ✅ **All previous disambiguation issues are resolved** — the execution workbook has zero conflicting codes in all 4 cycles. The 7 ambiguous 2005 codes identified earlier from the CSV have already been resolved in this workbook.

### Category Distribution Per Cycle

| Category | 2005 codes | 2010 codes | 2015 codes | 2022 codes |
|---|---|---|---|---|
| 1 (Work) | 14 | 15 | 6 | 9 |
| 2 (Household) | 21 | 25 | 10 | 22 |
| 3 (Caregiving) | 20 | 41 | 10 | 11 |
| 4 (Purchasing) | 14 | 29 | 3 | 5 |
| 5 (Sleep) | 3 | 3 | 1 | 5 |
| 6 (Eating) | 2 | 2 | 1 | 3 |
| 7 (Personal Care) | 4 | 6 | 3 | 6 |
| 8 (Education) | 9 | 12 | 5 | 6 |
| 9 (Socializing) | 8 | 8 | 2 | 3 |
| 10 (Passive Leisure) | 36 | 46 | 11 | 10 |
| 11 (Active Leisure) | 18 | 36 | 5 | 7 |
| 12 (Community) | 11 | 17 | 5 | 13 |
| 13 (Travel) | 23 | 23 | 1 | 17 |
| 14 (Miscellaneous) | — | — | 1 | 3 |

---

## Implementation Approach

### Step 1 — Parse the Excel Workbook into Lookup Dictionaries

```python
import openpyxl

ACTIVITY_EXCEL = (
    "references_activityCodes/"
    "Data Harmonization_activityCategories - execution.xlsx"
)

SHEET_CYCLE_MAP: dict[str, int] = {
    "2005codebook": 2005,
    "2010codebook": 2010,
    "2015codebook": 2015,
    "2022codebook": 2022,
}


def build_activity_crosswalks(
    excel_path: str,
) -> dict[int, dict[float | int, int]]:
    """Build {cycle_year: {raw_code: category_num}} from the execution Excel.

    Each sheet has columns: [Edited Main Category, Main Activity, Explanation].
    Row 1 is the header; data starts at row 2.

    Args:
        excel_path: Path to the execution Excel workbook.

    Returns:
        Dictionary mapping cycle years to their raw-code→category lookups.
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    crosswalks: dict[int, dict[float | int, int]] = {}

    for sheet_name, cycle_year in SHEET_CYCLE_MAP.items():
        ws = wb[sheet_name]
        lookup: dict[float | int, int] = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            category = int(row[0])
            raw_code = row[1]  # float for 2010, int-like for others
            lookup[raw_code] = category
        crosswalks[cycle_year] = lookup

    return crosswalks
```

### Step 2 — Apply Crosswalk to Episode Data

```python
def apply_activity_crosswalk(
    episode_df: pd.DataFrame,
    cycle_year: int,
    crosswalk: dict[float | int, int],
) -> pd.DataFrame:
    """Map raw activity codes to unified 14-category scheme.

    Args:
        episode_df: Episode DataFrame with raw activity code column.
        cycle_year: Survey cycle year (2005, 2010, 2015, 2022).
        crosswalk: {raw_code: category_number} lookup dictionary.

    Returns:
        DataFrame with new 'occACT' column (1–14) and preserved
        'occACT_raw' column (original code).
    """
    raw_col = "ACTCODE" if cycle_year in (2005, 2010) else "TUI_01"
    episode_df["occACT_raw"] = episode_df[raw_col]
    episode_df["occACT"] = episode_df[raw_col].map(crosswalk)
    # Codes not found in crosswalk → NaN (will be flagged in validation)
    return episode_df
```

### Step 3 — Handle Special Cases

| Case | Handling |
|---|---|
| **2010 decimal precision** | Ensure raw ACTCODE values are loaded as floats, not integers (e.g., `80.1` ≠ `801`). Compare with single-decimal precision |
| **Unmapped codes** | Any raw code not found in the crosswalk dict → `occACT = NaN`. Report these in validation |
| **"Not stated" sentinels** | Already mapped in the workbook: 2005/2010 code 995 → 10 (Passive Leisure per workbook); 2015 code 95 → 14; 2022 code 9999 → 14 |

---

## Columns Added to Episode CSVs

| Column | Type | Description |
|---|---|---|
| `occACT` | `int` (1–14) or NaN | Unified 14-category activity code |
| `occACT_raw` | `int` or `float` | Original cycle-specific raw code (preserved for auditing) |
| `occACT_label` | `str` | Category name from the 14-category list (optional, for readability) |

---

## Validation Checks (in `02_harmonizeGSS_val.py`)

| Check | Logic | Pass Criteria |
|---|---|---|
| Unique `occACT` values | `episode.occACT.dropna().unique()` per cycle | Only {1, 2, …, 14} |
| Coverage | % of episodes with non-NaN `occACT` | ≥99% per cycle |
| Unmapped code report | Episodes where `occACT` is NaN but `occACT_raw` is not NaN | List with counts |
| Time-weighted distribution | `sum(duration)` per `occACT` as % of total diary time, per cycle | Sleep ~30–35%, Work ~10–15%, Travel ~5–8% |
| Cross-cycle consistency | Compare `occACT` distributions across all 4 cycles | No category should be >5× different across cycles |
| Bidirectional audit | Every `occACT` 1–14 has episodes in every cycle | No empty categories |

**Visual output**: Stacked bar chart per cycle showing % diary time per category (14 bars × 4 cycles).

---

## User Review

> [!NOTE]
> ✅ **All items approved** — execution workbook has zero conflicts, 14-category scheme confirmed, all disambiguations pre-resolved.

> [!NOTE]
> **`occACT` vs. `occACT_raw`**: The harmonization will output both the unified 14-category code (`occACT`) and the original raw code (`occACT_raw`). This preserves full granularity for potential future analysis at finer resolutions.
