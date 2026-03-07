# Validation Plan — `02_harmonizeGSS` Step 2 Harmonization
## Ensuring Cross-Cycle Alignment Before Step 3 Merge

---

## Goal

Validate that all Main and Episode files have been harmonized correctly: unified column names, consistent category codes, sentinel values converted to NaN, metadata flags applied, activity codes crosswalked, and diary integrity preserved. The validation script (`02_harmonizeGSS_val.py`) will produce a styled HTML report with embedded charts.

**Input**: 8 harmonized CSVs from `outputs_step2/` (4 Main + 4 Episode)
**Output**: `outputs_step2/step2_validation_report.html`

---

## Validation Methods

Below are **9 validation methods**, ordered from structural checks to content verification to visual summaries. All are recommended and will be combined into a single HTML report.

---

### Method 1 — Unified Schema Audit

**What it checks:** Whether all 4 harmonized Main files share identical column sets, and all 4 Episode files share identical column sets — the core requirement of Step 2.

| Check | Logic | Pass Criteria |
|---|---|---|
| Main column identity | `set(main_2005.columns) == set(main_2010.columns) == set(main_2015.columns) == set(main_2022.columns)` | Exact match across all 4 cycles |
| Episode column identity | Same as above for episode files | Exact match across all 4 cycles |
| Column count | `len(main.columns)` per cycle | All cycles have same count |
| Column order | `main_2005.columns.tolist() == main_2022.columns.tolist()` | Identical ordering |
| Expected Main columns present | Check for: `occID`, `AGEGRP`, `SEX`, `MARSTH`, `HHSIZE`, `PR`, `CMA`, `LFTAG`, `COW`, `NOCS`, `HRSWRK`, `ATTSCH`, `KOL`, `MODE`, `TOTINC`, `WGHT_PER`, `DDAY`, `SURVMNTH`, `CYCLE_YEAR`, `SURVYEAR`, `COLLECT_MODE`, `TUI_10_AVAIL`, `BS_TYPE`, `TOTINC_SOURCE` | All present in every cycle |
| Expected Episode columns present | Check for: `occID`, `EPINO`, `WGHT_EPI`, `occACT`, `start`, `end`, `occPRE`, `Spouse`, `Children`, `Friends`, `otherHHs`, `Others`, `CYCLE_YEAR`, `DIARY_VALID` | All present in every cycle |

**Visual output:** Table showing column names × cycle with ✅/❌ per cell.

**Why it matters:** If any column is missing or misnamed in one cycle, the Step 3 `LEFT JOIN` will fail or produce unexpected NaN columns.

---

### Method 2 — Row Count Preservation Audit

**What it checks:** Whether harmonization preserved all respondents (no accidental row drops) and row counts match Step 1 expectations.

| Check | Logic | Pass Criteria |
|---|---|---|
| Main row counts | Compare `len(harmonized_main)` vs. `len(step1_main)` per cycle | Exact match (harmonization should not drop rows) |
| Episode row counts | Same for episode files | Exact match |
| Unique occID counts (Main) | `main.occID.nunique()` per cycle | Match Step 1 unique RECID/PUMFID counts |
| Unique occID counts (Episode) | `episode.occID.nunique()` per cycle | Match Step 1 |
| ID linkage | `set(episode.occID) ⊆ set(main.occID)` per cycle | ≥95% overlap (ideally 100%) |

**Visual output:** Grouped bar chart comparing Step 1 vs. Step 2 row counts per cycle, for both Main and Episode files.

**Why it matters:** Catches accidental filtering, row duplication, or merge errors during harmonization.

---

### Method 3 — Sentinel Value Elimination Audit

**What it checks:** Whether the sentinel codes (96/97/98/99) documented in the implementation plan have been correctly converted to NaN, and that valid codes were not incorrectly nullified.

| Check | Logic | Pass Criteria |
|---|---|---|
| Sentinel codes removed | For each column in `SENTINEL_MAP`, check `df[col].isin(sentinel_values).sum() == 0` | Zero sentinel residuals per column |
| NaN rate comparison | Compare NaN% per column between Step 1 and Step 2 | NaN% should increase by ~sentinel% for recoded columns |
| Valid code preservation | For columns with known valid ranges (e.g., `AGEGRP` 1–7), verify no valid values were lost | `set(df[col].dropna().unique()) ⊆ expected_valid_range` |
| Over-nullification check | For `occID`, `WGHT_PER`, `WGHT_EPI`: verify zero new NaNs introduced | NaN count unchanged from Step 1 |

**Visual output:**
- **Heatmap**: NaN% per column × cycle (harmonized data), side-by-side with Step 1 NaN heatmap
- **Delta table**: NaN count increase per column per cycle, annotated with whether the increase matches the expected sentinel count

**Why it matters:** The most common harmonization bug is either (a) missing some sentinel values, leaving them as valid data, or (b) over-zealously nullifying valid codes like `AGEGR10 = 7` or `HSDSIZEC = 6`.

---

### Method 4 — Category Recoding Verification

**What it checks:** Whether each recoded demographic variable now has the expected unified categories across all 4 cycles.

For each variable, verify:

| Variable | Expected Unified Values | Special Checks |
|---|---|---|
| `SEX` | {1, 2} | No other values; no NaN (should be complete) |
| `MARSTH` | {1, 2, 3, 4, 5, 6} + NaN | Old sentinels (8, 9, 99) gone |
| `AGEGRP` | {1, 2, 3, 4, 5, 6, 7} | Identical across all cycles |
| `HHSIZE` | {1, 2, 3, 4, 5} or {1, 2, 3, 4, 5, 6} | Check if HHSIZE was collapsed; 2022 should match others |
| `PR` | PRV codes (10–59) for 2010+ or REGION (1–5) for 2005 | Flag 2005 coarser granularity |
| `CMA` | {1, 2, 3} | No change expected |
| `LFTAG` | {1, 2, 3, 4, 5} + NaN | Old sentinels (8, 9, 97, 98, 99) gone |
| `COW` | Valid worker codes + NaN | Sentinels removed |
| `HRSWRK` | Continuous or binned + NaN | Sentinels removed |
| `ATTSCH` | Valid education codes + NaN | Sentinels removed |
| `KOL` | Valid language codes + NaN | Sentinels removed |
| `MODE` | Valid commute codes + NaN | 2005 should be all NaN; 2022 from ATT_150C |
| `TOTINC` | Categorical brackets or discretized + NaN | Sentinels removed |

**Visual output:** One stacked-bar chart per variable showing % distribution across categories for each cycle. This is the key "big picture" chart — it should show smooth, plausible demographic distributions across cycles with no unexpected category spikes or drops.

**Why it matters:** Incorrect recoding would show as (a) unexpected categories appearing, (b) a category that is implausibly large (e.g., 50% of respondents in a sentinel code), or (c) distribution shapes that break dramatically between cycles for no methodological reason.

---

### Method 5 — Activity Code Crosswalk Verification

**What it checks:** Whether the activity code crosswalk produced valid, complete mappings to the unified 14-category `occACT` scheme (see [02_harmonizationGSS_actCodes.md](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizationGSS_actCodes.md)).

| Check | Logic | Pass Criteria |
|---|---|---|
| Unique code count | `episode.occACT.nunique()` per cycle | ≤14 for all cycles (plus NaN for unmapped) |
| All codes in valid range | `episode.occACT.dropna().isin(range(1, 15)).all()` | True for all cycles |
| Unmapped code rate | % of episodes where `occACT` is NaN after crosswalk, excluding original "not stated" codes | <2% per cycle (ideally <0.5%) |
| Coverage per category | For each of the 14 categories, count episodes × cycle | No category should be completely empty in any cycle |
| Raw code audit | For 2005 (182 → 14) and 2010 (264 → 14), check that every raw ACTCODE maps to exactly one `occACT` | No raw codes left unmapped |
| 2022 mapping | Verify all 121 raw TUI_01_2022 codes are accounted for in the crosswalk | Zero orphan codes |
| Time-weighted activity distribution | Compute `sum(duration) per occACT` as % of total diary time, per cycle | Sleep ~30–35%, Work ~10–15%, Travel ~5–8% |

**Visual output:**
- **Bar chart**: Unique `occACT` code count per cycle (should be ≤14)
- **Heatmap**: 14 activity categories × 4 cycles, color = % of total diary time — visualizes cross-cycle consistency
- **Table**: All 14 categories with episode counts per cycle and % of diary time
- **Unmapped codes table**: List of raw codes per cycle that could not be mapped, with episode count and % impact

**Why it matters:** Activity codes are the **primary output variable** for the entire pipeline. An incorrect crosswalk corrupts all downstream models. The time-weighted distribution comparison is the strongest validation — if sleep is ~33% of diary time in all cycles, the crosswalk is likely correct.

---

### Method 6 — Location Recoding Verification

**What it checks:** Whether `occPRE` (home presence) is correctly derived from the cycle-specific location codes.

| Check | Logic | Pass Criteria |
|---|---|---|
| Binary encoding | `episode.occPRE.dropna().unique()` | Only {0, 1} |
| Home presence rate | `episode.occPRE.mean()` per cycle | Expected ~55–70% (people spend majority of diary time at home) |
| Cross-cycle consistency | Compare home presence rate across cycles | Rates should be similar (±10pp), with possible COVID-related increase in 2022 |
| Missing rate | `episode.occPRE.isna().mean()` per cycle | <5% (only original "not stated" locations → NaN) |
| Activity × location plausibility | For `occACT` = sleep: `occPRE` should be ~95%+ at home | Sleep episodes overwhelmingly at home |
| Activity × location plausibility | For `occACT` = paid work (office): `occPRE` should be <50% at home (pre-2022) | Paid work mostly not at home (except 2022 WFH) |

**Visual output:**
- **Bar chart**: Home presence rate per cycle
- **Cross-tab heatmap**: Top 10 activities × home/not-home % per cycle

**Why it matters:** The `occPRE` / `AT_HOME` flag is the central occupancy variable for BEM/UBEM integration. An error in location recoding (e.g., swapping home=1 for home=300) would invert the entire occupancy model.

---

### Method 7 — Metadata Flag Audit

**What it checks:** Whether all appended metadata columns have the correct, constant values per cycle.

| Flag | 2005 Expected | 2010 Expected | 2015 Expected | 2022 Expected |
|---|---|---|---|---|
| `CYCLE_YEAR` | 2005 (constant) | 2010 (constant) | 2015 (constant) | 2022 (constant) |
| `SURVYEAR` | 2005 (constant) | 2010 (constant) | 2015 (constant) | 2022 (constant) |
| `SURVMNTH` | All NaN | All NaN | 1–12 (varies) | 1–12 (varies) |
| `COLLECT_MODE` | 0 (constant) | 0 (constant) | 0 (constant) | 1 (constant) |
| `TUI_10_AVAIL` | 0 (constant) | 0 (constant) | 1 (constant) | 1 (constant) |
| `BS_TYPE` | `MEAN_BS` (constant) | `MEAN_BS` (constant) | `STANDARD_BS` (constant) | `STANDARD_BS` (constant) |
| `TOTINC_SOURCE` | `SELF` (constant) | `SELF` (constant) | `SELF` (constant) | `CRA` (constant) |

**Checks:**
- Each flag must have exactly one unique value per cycle (except `SURVMNTH` which varies within 2015/2022)
- `SURVMNTH` for 2005/2010 must be 100% NaN
- `SURVMNTH` for 2015/2022 must have values in {1, 2, …, 12} with reasonable monthly distribution (not all in one month)

**Visual output:** Table with flag values × cycle, colored green/red per cell. For `SURVMNTH`, show a small bar chart of monthly distribution for 2015 and 2022.

**Why it matters:** These flags are conditioning variables for the Transformer models. Incorrect flags (e.g., `COLLECT_MODE = 1` for a CATI cycle) would corrupt the model's ability to disentangle mode effects from behavioral change.

---

### Method 8 — Diary Closure QA (Episode Integrity)

**What it checks:** Whether the diary integrity constraint (all episodes sum to 1440 minutes per respondent) is satisfied after harmonization.

| Check | Logic | Pass Criteria |
|---|---|---|
| Duration computation | For each episode: convert HHMM start/end to minutes, compute duration (handle midnight wrap) | All durations ≥ 0 |
| Diary total | `groupby(occID).sum(duration)` | Must equal 1440 for valid diaries |
| DIARY_VALID flag | Check the `DIARY_VALID` column added by harmonization | Consistent with computed totals |
| Pass rate | `DIARY_VALID.mean()` per cycle | ≥95% |
| Failure analysis | For respondents where sum ≠ 1440, examine: off by how many minutes? Is it a rounding issue (±1 min)? | Characterize the failure mode |
| Episode ordering | `STARTIME[i+1] >= ENDTIME[i]` for consecutive episodes per occID | ≥99% of episode pairs are properly ordered |
| Gap/overlap detection | Check for gaps (ENDTIME[i] < STARTIME[i+1]) or overlaps (ENDTIME[i] > STARTIME[i+1]) | Report % of respondents with gaps/overlaps |
| Episode count distribution | `groupby(occID).size()` | Typical: 10–30 episodes per respondent. Flag if <3 or >80 |

**Visual output:**
- **Histogram**: Diary total minute distribution per cycle (should be a spike at 1440)
- **Bar chart**: DIARY_VALID pass rate per cycle
- **Box plot**: Episode count per respondent per cycle
- **Table**: Top 10 failure modes (diary total → count of respondents)

**Why it matters:** Step 3's HETUS 144-slot conversion requires exactly 1440 minutes. Any respondent failing this check cannot be validly converted and must be excluded. Understanding the failure mode (systematic vs. rounding) informs whether tolerance should be applied.

---

### Method 9 — Pre/Post Harmonization Distribution Comparison (Regression Check)

**What it checks:** Whether harmonization accidentally altered the underlying data distributions beyond the intended recoding. This is a "do no harm" check.

| Check | Logic | Pass Criteria |
|---|---|---|
| Weight distribution preserved | Compare `WGHT_PER` summary stats (mean, std, min, max) between Step 1 and Step 2 per cycle | Exact match (weights should not be touched) |
| Episode weight preserved | Same for `WGHT_EPI` | Exact match |
| Total respondent count | `occID.nunique()` Step 2 vs. Step 1 | Exact match (no respondents dropped) |
| Total episode count | `len(episode_df)` Step 2 vs. Step 1 | Exact match |
| Numeric column ranges | For `HRSWRK`, `TOTINC`: compare range(non-NaN values) Step 1 vs. Step 2 | Step 2 range ⊆ Step 1 range (sentinels removed, no new values added) |
| Time columns | `start` and `end` value ranges per cycle | Same as Step 1 `STARTIME`/`ENDTIME` (rename only, no value changes) |

**Visual output:**
- **Side-by-side box plots**: Weight distributions (Step 1 vs. Step 2) per cycle
- **Delta summary table**: For each numeric column, show Step 1 stats vs. Step 2 stats with diff

**Why it matters:** This catches subtle bugs like accidental type conversion (float→int truncation), row shuffling that corrupts ID linkages, or unintended value transformations applied to columns that should only be renamed.

---

## Proposed Output

### [NEW] [02_harmonizeGSS_val.py](file:///Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp/02_harmonizeGSS_val.py)

A `GSSHarmonizationValidator` class (mirroring `GSSValidator` from Step 1) that:
1. Loads the 8 harmonized CSVs from `outputs_step2/`
2. Loads the 8 Step 1 CSVs from `outputs/` (for comparison checks)
3. Runs all 9 validation methods
4. Produces a styled HTML report at `outputs_step2/step2_validation_report.html`

### Class Architecture

```python
class GSSHarmonizationValidator:
    def __init__(self, step1_dir: str, step2_dir: str):
        """Load Step 1 and Step 2 data for comparison."""

    def load_data(self) -> None:
        """Load all 16 CSVs (8 from Step 1 + 8 from Step 2)."""

    # --- Method 1 ---
    def audit_unified_schema(self) -> None:
        """Verify identical column sets across all 4 Main and Episode files."""

    # --- Method 2 ---
    def audit_row_counts(self) -> None:
        """Compare row counts between Step 1 and Step 2."""

    # --- Method 3 ---
    def audit_sentinel_elimination(self) -> None:
        """Verify sentinel codes are gone, valid codes preserved."""

    # --- Method 4 ---
    def verify_category_recoding(self) -> None:
        """Check each recoded variable has expected unified values."""

    # --- Method 5 ---
    def verify_activity_crosswalk(self) -> None:
        """Validate activity code mapping completeness and distributions."""

    # --- Method 6 ---
    def verify_location_recoding(self) -> None:
        """Check occPRE is binary with plausible home presence rates."""

    # --- Method 7 ---
    def audit_metadata_flags(self) -> None:
        """Verify all metadata flags have correct constant values per cycle."""

    # --- Method 8 ---
    def verify_diary_closure(self) -> None:
        """QA check: diary durations sum to 1440 min per respondent."""

    # --- Method 9 ---
    def compare_pre_post_distributions(self) -> None:
        """Regression check: weights, counts, ranges unchanged."""

    # --- Report Generation ---
    def generate_visuals(self) -> None:
        """Run all chart-producing methods and collect base64 PNGs."""

    def export_html_report(self) -> None:
        """Build styled HTML report with all embedded charts and tables."""
```

---

## HTML Report Structure

The HTML report will follow the same template as Step 1's `step1_validation_report.html`, with the following sections:

| Section | Content | Charts |
|---|---|---|
| **Header** | Title, timestamp, input/output paths | — |
| **1. Schema Audit** | Column presence table (✅/❌) | Column × cycle matrix |
| **2. Row Counts** | Step 1 vs Step 2 counts | Grouped bar chart |
| **3. Sentinel Elimination** | Per-column sentinel residual counts | NaN% heatmap (Step 1 vs Step 2) |
| **4. Category Distributions** | Per-variable unified values | Stacked bar charts (one per variable, ~12 charts) |
| **5. Activity Crosswalk** | Code coverage, unmapped rates | Heatmap (14 categories × 4 cycles) + bar chart |
| **6. Location Recoding** | Home presence rates, binary check | Bar chart + activity×location cross-tab |
| **7. Metadata Flags** | Flag values per cycle | Colored table |
| **8. Diary Closure** | Pass rates, failure modes | Histogram + bar chart + box plot |
| **9. Regression Check** | Weight/count preservation | Side-by-side box plots + delta table |
| **Footer** | Summary pass/fail counts, timestamp | — |

---

## Pass/Fail Summary Criteria

| Method | Pass Criterion | Severity if Failed |
|---|---|---|
| 1. Schema Audit | All 4 Main files identical columns; same for Episode | 🔴 **Critical** — blocks Step 3 |
| 2. Row Counts | Exact match between Step 1 and Step 2 | 🔴 **Critical** — data loss |
| 3. Sentinel Elimination | Zero sentinel residuals in all mapped columns | 🟡 **Warning** — residual sentinels corrupt models |
| 4. Category Recoding | All values within expected unified ranges | 🟡 **Warning** — unexpected codes may cause one-hot encoding errors |
| 5. Activity Crosswalk | ≤14 codes per cycle; <2% unmapped | 🔴 **Critical** — activity codes are the primary output variable |
| 6. Location Recoding | Binary {0, 1} + NaN; home rate 55–70% | 🔴 **Critical** — AT_HOME is the occupancy signal |
| 7. Metadata Flags | Correct constant values per cycle | 🟡 **Warning** — incorrect flags corrupt Transformer conditioning |
| 8. Diary Closure | ≥95% pass rate per cycle | 🟡 **Warning** — sub-95% may indicate systematic data issues |
| 9. Regression Check | Exact match for weights, counts, time ranges | 🔴 **Critical** — unintended data corruption |

---

## Running the Validation

```bash
cd /Users/orcunkoraliseri/Desktop/Postdoc/occModeling/2J_docs_occ_nTemp
python 02_harmonizeGSS_val.py
```

The script will:
1. Print a console summary with ✅/❌ per check
2. Generate and save `outputs_step2/step2_validation_report.html`
3. Exit with code 0 if all critical checks pass, or code 1 if any critical check fails
