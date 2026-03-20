# Step 2 Open Failures — Investigation & Resolution Plan

**File:** `02_harmonizeGSS_openFailures.md`
**Status:** ❌ 2 unresolved failures blocking full-fidelity Step 3 pooling
**Source validation check:** `02_harmonizeGSS_val.py` → method1_schema

---

## Overview

Two schema failures remain from Step 2 harmonization. Both are detected by the **Method 1 (Unified Schema Audit)** check in `02_harmonizeGSS_val.py`, which asserts that all four cycle files share identical column sets after harmonization.

| Failure | File | Detection |
|---------|------|-----------|
| RF-A: POWST column never derived; residual CTW columns pollute Main schema | `main_<cycle>.csv` | Main column mismatch |
| RF-B: Episode raw source columns retained; 3 schema-level differences across cycles | `episode_<cycle>.csv` | Episode column mismatch |

---

## RF-A: CTW Residual Columns Polluting Main Schema

> **Resolution decision:** `POWST` is **dropped from the pipeline schema**. It was never implemented, has no source variable in 2005 (Cycle 19), and its only downstream functional reference (Model 1 WFH constraint) is fully covered by the episode-level `AT_HOME` flag already derived from the diary. The diary directly records where a person was each slot — if they worked from home, both `occACT=1` (Work) and `AT_HOME=1` appear in the data. A demographic-level POWST habit indicator adds no information that the model cannot learn from the actual diary sequences.

### Confirmed State (from `outputs_step2/main_*.csv` column audit)

The real failure is that after `derive_mode()` consumes the CTW checkbox batteries to produce `MODE`, the raw CTW columns are **not dropped**. They leak into the final Main output with inconsistent naming across cycles:

| Cycle | CTW residuals in harmonized output |
|-------|-----------------------------------|
| 2005 | None (no CTW source exists) |
| 2010 | `CTW_Q140_C01` through `CTW_Q140_C09` (9 columns) |
| 2015 | `CTW_140A` through `CTW_140I` (9 columns) |
| 2022 | `CTW_140A`, `CTW_140B`, `CTW_140C`, `CTW_140D`, `CTW_140E`, `CTW_140I`, `CTW140GR` (7 columns) |

These cycle-specific column sets cause the Method 1 schema audit to fail on Main files.

### Fix — RF-A (one change only)

Drop CTW columns at the end of `derive_mode()` in `02_harmonizeGSS.py`:

```python
def derive_mode(df: pd.DataFrame, cycle: int) -> pd.DataFrame:
    # ... existing MODE derivation logic (unchanged) ...

    # Drop all CTW source columns — MODE has been derived; nothing else needs them
    df = df.drop(
        columns=[c for c in df.columns if c.startswith(("CTW_Q140", "CTW_140", "CTW140"))],
        errors="ignore"
    )
    return df
```

No new column, no codebook lookup, no derivation needed.

### Pass Criteria — RF-A

- [ ] Zero CTW residual columns in any `main_<cycle>.csv` output
- [ ] All four Main files share identical column sets (method1_schema passes)
- [ ] `POWST` removed from Step 1A variable table and Step 2A discrepancy table in `00_GSS_Occupancy_Pipeline.md`

---

## RF-B: Episode Column Mismatch

### Confirmed State (from `outputs_step2/episode_*.csv` column audit)

The validation check `all(epi_cols[c] == epi_cols[2005] for c in CYCLES)` fails because the four harmonized episode files have different column sets.

**Full symmetric difference (2015/2022 vs 2005/2010):**

| Column | 2005 | 2010 | 2015 | 2022 | Category |
|--------|------|------|------|------|----------|
| `ACTCODE` | ✅ | ✅ | ❌ | ❌ | Raw source col retained (2005/2010 only) |
| `PLACE` | ✅ | ✅ | ❌ | ❌ | Raw source col retained (2005/2010 only) |
| `TUI_01` | ❌ | ❌ | ✅ | ✅ | Raw source col retained (2015/2022 only) |
| `LOCATION` | ❌ | ❌ | ✅ | ✅ | Raw source col retained (2015/2022 only) |
| `TOTEPISO` | ❌ | ❌ | ✅ (18–n) | ❌ | Total episodes per respondent — 2015-only |
| `TUI_07` | ❌ | ❌ | ✅ | ✅ | Technology use — expected absent 2005/2010 |
| `TUI_10` | ❌ | ❌ | ✅ (mostly 96) | ❌ | Well-being — 2015 only |
| `TUI_15` | ❌ | ❌ | ❌ | ✅ (values 1–5, 9) | Unknown 2022 column — likely well-being |

### Root Cause Analysis

**Issue B1 — Raw source columns not dropped after derivation:**
The episode harmonization pipeline derives `occACT` (from `ACTCODE` or `TUI_01`) and `occPRE` (from `PLACE` or `LOCATION`), but does **not drop** the original raw columns. Since the raw column names differ by cycle, they propagate into the output as cycle-specific residuals. This is identical in structure to the CTW residuals in RF-A.

**Issue B2 — `TOTEPISO` not standardized:**
`TOTEPISO` (total number of episodes per respondent) appears only in the 2015 episode file. It is not present in 2005/2010 (where it would need to be computed from `EPINO` max per respondent) nor in 2022 (where it may have been removed or renamed). It was never added to the unified schema.

**Issue B3 — `TUI_07` (tech use) not filled for 2005/2010:**
Per the pipeline specification (`00_GSS_Occupancy_Pipeline.md` §1B), `TUI_07` is listed as "Absent" for 2005 and "Uncertain" for 2010. The harmonization script correctly leaves it out for those cycles, but this creates a schema mismatch. It should be added as a `NaN`-filled column in 2005/2010 to unify the schema.

**Issue B4 — `TUI_10` vs `TUI_15` — well-being column rename in 2022:**
`TUI_10` (subjective well-being scale) is present in 2015 but absent from 2022. The 2022 episode file contains `TUI_15` instead, with values `{1, 2, 3, 4, 5, 9}` — consistent with a 5-point well-being scale (1=very happy → 5=very unhappy, 9=not stated). This is almost certainly the 2022 equivalent of `TUI_10`. The pipeline doc confirms `wellbeing` as the unified target column name, available only for 2015/2022.

**Observed `TUI_15` distribution (2022 episode):**

| Value | Count | Likely meaning |
|-------|-------|----------------|
| 5 | 60,769 | Very unhappy / Strongly agree (or scale endpoint) |
| 4 | 56,316 | |
| 3 | 35,467 | Neutral |
| 2 | 5,452 | |
| 1 | 1,943 | Very happy / Strongly disagree |
| 9 | 8,131 | Not stated / sentinel |

> ⚠️ **Scale direction must be confirmed:** If TUI_10 (2015) and TUI_15 (2022) use opposite scale directions, they must be harmonized before being pooled into a single `wellbeing` column.

---

### Investigation Steps — RF-B

**Step RF-B1: Confirm `TUI_15` = well-being in 2022**
- Inspect 2022 PUMF Episode user guide or codebook for `TUI_15` variable label
- Confirm scale endpoints (1=unhappy vs 1=happy) and compare with `TUI_10` scale in 2015 codebook
- If reversed: add a recode step to align directions before renaming to `wellbeing`

**Step RF-B2: Decide on `TOTEPISO` handling**
- Option A (recommended): Drop `TOTEPISO` entirely — it is derivable from `EPINO` max per `occID` in all cycles, making the stored version redundant
- Option B: Retain and standardize — compute `TOTEPISO` for 2005/2010/2022 from episode data; fill from raw for 2015
- Decision needed: whether downstream steps (Step 3, Model 1) require this column

**Step RF-B3: Implement drop of raw source columns**

Add explicit column drops to `harmonize_episode()`:

```python
def harmonize_episode(df, cycle, act_crosswalk, pre_crosswalk):
    df = apply_activity_crosswalk(df, cycle, act_crosswalk)
    validate_activity_crosswalk(df, cycle, ...)
    df = apply_presence_crosswalk(df, cycle, pre_crosswalk)
    df = harmonize_copresence(df, cycle)
    df = check_diary_closure(df, cycle)
    df["CYCLE_YEAR"] = cycle

    # Drop raw source columns — replaced by derived occACT, occPRE
    raw_drop = ["ACTCODE", "TUI_01", "PLACE", "LOCATION"]
    df = df.drop(columns=[c for c in raw_drop if c in df.columns], errors="ignore")

    # Drop TOTEPISO (derivable from EPINO; not part of unified schema)
    df = df.drop(columns=["TOTEPISO"], errors="ignore")   # pending RF-B2 decision

    return df
```

**Step RF-B4: Standardize `TUI_07` across all cycles**

```python
# In harmonize_episode(), after copresence harmonization:
if "TUI_07" not in df.columns:
    df["TUI_07"] = pd.NA    # Absent for 2005 (confirmed) and 2010 (uncertain)
```

**Step RF-B5: Unify well-being column → `wellbeing`**

```python
# In harmonize_episode():
if cycle == 2015:
    if "TUI_10" in df.columns:
        df = df.rename(columns={"TUI_10": "wellbeing"})
        df["wellbeing"] = df["wellbeing"].replace({96: pd.NA, 97: pd.NA, 98: pd.NA, 99: pd.NA})
    else:
        df["wellbeing"] = pd.NA

elif cycle == 2022:
    if "TUI_15" in df.columns:
        # ⚠️ Verify scale direction vs TUI_10 before renaming (RF-B1)
        df = df.rename(columns={"TUI_15": "wellbeing"})
        df["wellbeing"] = df["wellbeing"].replace({9: pd.NA})
    else:
        df["wellbeing"] = pd.NA

else:  # 2005, 2010
    df["wellbeing"] = pd.NA
```

---

### Target Unified Episode Schema (post-fix)

After resolving RF-B, all four `episode_<cycle>.csv` files should share exactly these columns:

```
occID, EPINO, DDAY, start, end, duration,
occACT, occACT_raw, occACT_label,
occPRE, occPRE_raw, AT_HOME,
Alone, Spouse, Children, friends, otherHHs, otherInFAMs, others, parents,
TUI_07,         # NaN for 2005/2010
wellbeing,      # NaN for 2005/2010; available for 2015 (TUI_10) and 2022 (TUI_15)
WGHT_EPI,
DIARY_VALID, CYCLE_YEAR
```

> **Note:** `TUI_10_AVAIL` flag is a Main-file metadata column (not episode-level). It correctly indicates where `wellbeing` is non-null (2015, 2022), and can be joined from Main when needed.

### Pass Criteria — RF-B

- [ ] All four `episode_<cycle>.csv` files share identical column sets (method1_schema passes)
- [ ] Zero `ACTCODE`, `TUI_01`, `PLACE`, `LOCATION`, `TOTEPISO`, `TUI_10`, `TUI_15` in any output
- [ ] `TUI_07` present and NaN-filled for 2005/2010; has values for 2015/2022
- [ ] `wellbeing` present in all four; NaN for 2005/2010; non-null rate > 0% for 2015/2022
- [ ] `wellbeing` value set restricted to `{1, 2, 3, 4, 5, NaN}` (scale direction confirmed)

---

## Implementation Order

```
RF-B1 → verify TUI_15 = wellbeing in 2022 (codebook lookup — only remaining external dependency)
RF-B2 → decide TOTEPISO handling (drop recommended)

Then implement in 02_harmonizeGSS.py:
  1. drop CTW residuals at end of derive_mode()          ← RF-A fix (one line)
  2. drop raw episode source columns in harmonize_episode()
  3. standardize TUI_07 NaN fill
  4. unify TUI_10/TUI_15 → wellbeing column
  5. drop TOTEPISO (or standardize)

Also update 00_GSS_Occupancy_Pipeline.md:
  - Remove POWST row from Step 1A variable table
  - Remove POWST row from Step 2A discrepancy table
  - Remove POWST from Step 4 constraint note

Re-run:
  python 02_harmonizeGSS.py
  python 02_harmonizeGSS_val.py
  open outputs_step2/step2_validation_report.html
```

---

## Summary Table

| ID | Failure | Root cause | Files affected | Blocker for |
|----|---------|-----------|----------------|-------------|
| RF-A | CTW residual columns leak into Main with inconsistent naming | `derive_mode()` consumes CTW columns but does not drop them | `main_2010.csv`, `main_2015.csv`, `main_2022.csv` | method1_schema pass |
| ~~POWST~~ | ~~Never derived~~ | **Dropped from schema** — covered by episode-level `AT_HOME` | — | — |
| RF-B1 | Raw source cols (`ACTCODE`, `TUI_01`, `PLACE`, `LOCATION`) not dropped | `harmonize_episode()` does not drop originals after deriving `occACT`/`occPRE` | All four `episode_*.csv` | method1_schema pass |
| RF-B2 | `TOTEPISO` 2015-only; not standardized | Not added to unified schema | `episode_2015.csv` only | method1_schema pass |
| RF-B3 | `TUI_07` absent for 2005/2010 | No NaN-fill step in harmonizer | `episode_2005.csv`, `episode_2010.csv` | method1_schema pass |
| RF-B4 | `TUI_10` (2015) vs `TUI_15` (2022) — well-being not unified | 2022 renamed the variable; no crosswalk implemented | `episode_2015.csv`, `episode_2022.csv` | method1_schema pass; wellbeing conditioning in Model 1 |
