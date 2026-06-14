# Validation Plan — `01_readingGSS` Step 1 Extraction (Leg 2 — 2-Channel Split)
## Ensuring Correct Reading Flow Before Step 2 · Residential + Office Two-Channel Pipeline

---

## Goal

Validate that all GSS Main and Episode files were read correctly and completely — including the **new office-gating columns** required by the Leg-2 two-channel split — before proceeding to harmonization. The validation script (`01_readingGSS_2split_val.py`) will produce a structured console report and optionally save it to `outputs_step1/validation_report.txt`.

The residential column set is **unchanged from Leg 1** and the corresponding checks are **reused directly** (tagged ✅ reused (Leg 1)). The new validation surface is the office employment-gating variables added in Step 1A (activity last week, worked last week, LF status, hours worked, class of worker, NOC, NAICS, telework / WFH), tagged ⚠️ NEW (Leg 2).

---

## Validation Methods

Below are **5 alternative validation approaches**, ordered from lightweight to comprehensive. They can be used individually or combined.

---

### Method 1 — Schema & Shape Audit (Recommended — Fast)

**What it checks:** Column presence, data types, row counts, and NaN rates per cycle — for both the residential carry-over columns and the new office-gating columns.

| Check | Logic | Pass Criteria |
|---|---|---|
| Residential column presence ✅ reused (Leg 1) | Compare loaded columns vs. expected `MAIN_COLS_*` / `EPISODE_COLS_*` constants (same as Leg 1) | All expected residential columns present in all four cycles |
| Office column presence ⚠️ NEW (Leg 2) | Check per-cycle presence of: `MAR_Q100` / `ACT7DAYS` / `ACT7DAYC`; `LFSGSS`; `WKWEHR_C` / `WHWD140C` / `WHWD140G`; `MAR_Q172` / `WET_120`; `SOC91C10` / `NOCS2006_C10` / `NOC1110Y` / `NOCLBR_Y`; `NAICS2002_C16` / `NAICS2007_C16` / `NAIC12CY` / `NAIC22CY`; `MAR_Q190` / `WTI_130` / `TLWK_01A`–`D` | Present in the cycle they belong to (see cycle map in §1A of `00_2split_Occupancy_Pipeline.md`) |
| 2015 `WET_120` EXPECTED MISS ⚠️ NEW (Leg 2) | Check 2015 Main for `WET_120`; if absent, flag as `❌ EXPECTED` not `❌ FAIL` | Column absent → log "KNOWN SUPPRESSED in 2015 PUMF — expected miss, not a bug"; NOC/NAICS serve as archetype proxy for 2015 |
| Row count sanity ✅ reused (Leg 1) | Compare against known GSS respondent counts from documentation | Within ±5% of documented values |
| NaN rate per column ✅ reused (Leg 1) | `df.isnull().mean()` | No residential column is 100% NaN; office columns are NaN where expected (e.g., telework NaN for non-workers) |
| Dtype consistency ✅ reused (Leg 1) | Check numeric columns are numeric, not object/string | Weight columns (`WGHT_*`) must be float; NOC/NAICS codes must be int or categorical, not free text |

**Pros:** Very fast (<1 sec), no external data needed; catches the WET_120 suppression explicitly.
**Cons:** Does not verify *content* correctness; a present-but-misaligned column still passes.

---

### Method 2 — Cross-Cycle Category Comparison (Recommended — Content Check)

**What it checks:** Whether the unique categories in demographic and office-gating columns are plausible and consistent across cycles.

```
For each shared variable (residential + office):
  1. Extract unique values per cycle
  2. Print side-by-side comparison table
  3. Flag unexpected values (e.g., negative codes, values outside known ranges)
  4. Flag cycles where a variable has drastically different category counts
```

**Residential variables** ✅ reused (Leg 1):

| Variable | Expected Categories | Flag If |
|---|---|---|
| Age group | 5–8 bins (10-yr groups) | >15 categories or <3 |
| Sex | 2 values (1/2) | >3 categories |
| Marital status | 4–6 categories | >10 categories |
| Household size | 1–6+ categories | >20 or negative values |
| Province / Region | 5–13 codes | <3 or >15 |
| Urban / Rural (CMA) | 2–5 codes | >10 |
| Income | Varies by cycle regime | All NaN for any cycle |

**Office-gating variables** ⚠️ NEW (Leg 2):

| Variable | Expected Categories | Flag If |
|---|---|---|
| Activity last week (`MAR_Q100` / `ACT7DAYS` / `ACT7DAYC`) | 4–10 codes (work, school, retired, unemployed, …) | >20 codes or all NaN |
| LF status (`LFSGSS` / derived) | 3–5 codes (employed, unemployed, not-in-LF, …) | >10 codes |
| Hours worked (`WKWEHR_C` / `WHWD140C` / `WHWD140G`) | Continuous or banded; ≥1 distinct non-zero values | All-zero or all-NaN |
| Class of worker (`MAR_Q172` / `WET_120`) | 3–6 codes (employee, self-employed, unpaid family, …); **absent in 2015 — expected** | >15 codes or present-but-all-NaN in a non-2015 cycle |
| NOC occupation (`SOC91C10` / `NOCS2006_C10` / `NOC1110Y` / `NOCLBR_Y`) | ~10 C10 buckets (the `_C10` / `_Y` suffix signals collapsed 10-category version) | >15 or <5 categories; or a non-C10 full code appearing instead |
| NAICS industry (`NAICS2002_C16` / `NAICS2007_C16` / `NAIC12CY` / `NAIC22CY`) | ~16 C16 / CY buckets (industry sector level) | >25 or <8 categories |
| Telework (`MAR_Q190` / `WTI_130` / `TLWK_01A`–`D`) | Mostly NaN/valid-skip (only employed teleworkers have codes); small non-NaN share (<20%) | Non-NaN share >50% (would indicate a misread sentinel) |

> **Telework note.** The telework columns are expected to be sparse — in 2005 the variable does not exist (`MAR_Q190` in 2010 only). The 2022 columns (`TLWK_01A`–`D`) capture the COVID jump; a non-trivial non-NaN share (10–20%) in 2022 vs near-zero in 2005 is the correct longitudinal signal. Flag only if the 2022 non-NaN rate is implausibly low (<1%) or the earlier cycles are implausibly high (>10%).

**Pros:** Catches misaligned columns (e.g., wrong cycle variable extracted), encoding errors, and the NOC/NAICS bucket-count sanity in one pass.
**Cons:** Requires manual interpretation of the side-by-side output table.

---

### Method 3 — Episode Integrity Check (Recommended — Critical for Pipeline)

**What it checks:** Whether the episode file structure is valid for downstream HETUS conversion, and whether `occPRE` — the source of the AT_WORK derivation — is present and non-null on every row.

**Residential episode checks** ✅ reused (Leg 1):

| Check | Logic | Pass Criteria |
|---|---|---|
| Diary completeness | `groupby(occID).duration.sum()` or infer from STARTIME/ENDTIME | Majority of respondents sum to 1440 min |
| Episode count per person | `groupby(occID).size()` | Typical range: 10–30 episodes per person |
| Activity code range | `unique()` on ACTCODE / TUI_01 | No values outside known code list |
| Time ordering | STARTIME < ENDTIME per episode | >99% of episodes pass |
| ID linkage | Check occID overlap between Main and Episode | >95% of Episode IDs appear in Main |

**Office-specific `occPRE` checks** ⚠️ NEW (Leg 2):

| Check | Logic | Pass Criteria |
|---|---|---|
| `occPRE` presence on episode rows | `"occPRE" in episode_df.columns` for every cycle | Column present in all four cycle episode files |
| `occPRE` non-null rate | `episode_df["occPRE"].isnull().mean()` per cycle | NaN rate <5% (sentinels / not-stated only) |
| `occPRE` value range | `episode_df["occPRE"].unique()` | Values within 1–18 (the 18-category harmonized scheme); flag any value outside this range |
| AT_WORK derivability | `(episode_df["occPRE"] == 2).sum() / len(episode_df)` per cycle | Non-zero across all cycles; share in plausible range (2–10% of episode rows represent work-location episodes, consistent with audit §2 ~6–7% of episode-time) |
| AT_WORK not derived yet | AT_WORK column itself is NOT expected in Step-1 output | Confirm `"AT_WORK"` column absent — it is derived in Step 2/3, not Step 1 |

> **Framing.** AT_WORK is derived in Step 2/3 tiling (`occPRE == 2`). Step 1's job is only to carry `occPRE` correctly onto every episode row. The non-trivial but small AT_WORK-compatible share (~6–7% of episode-time) is the sanity signal: if `occPRE == 2` accounts for 0% or 30%+, something went wrong at read time.

**Pros:** Directly validates the most critical assumption for downstream AT_WORK tiling; catches a missing `occPRE` before it propagates to Step 3.
**Cons:** Slightly slower (~5–10 sec per cycle due to groupby); manual threshold judgment needed for the AT_WORK share.

---

### Method 4 — Weight Distribution Sanity Check

**What it checks:** Whether survey weights look reasonable (not corrupted during read). This check is **fully reused from Leg 1** — the office split does not change the weight columns.

✅ reused (Leg 1) — all checks below are unchanged:

| Check | Logic | Pass Criteria |
|---|---|---|
| Weight range | `min()`, `max()`, `mean()` for WGHT_PER / WGHT_EPI | All positive; no extreme outliers (>10× mean) |
| Weight sum | `WGHT_PER.sum()` per cycle | Should approximate Canadian population (~25–38M depending on year) |
| Zero weights | Count of `WGHT == 0` | Should be 0 or very small |

**Pros:** Catches file truncation or format parsing errors; costs almost nothing to run.
**Cons:** Requires rough knowledge of expected population totals; does not detect office-specific issues.

> **Note.** Because the office channel is gated to employed workers in downstream steps (not in Step 1), there is no cycle-specific office sub-weight to check here. Step 1 should carry the full person weights unchanged; office gating will reduce the effective weighted N in Step 2.

---

### Method 5 — Visual Summary Dashboard (Optional — Most Comprehensive)

**What it checks:** Everything above, presented as a visual HTML report with charts; extended with office-specific panels for the Leg-2 columns.

**Residential panels** ✅ reused (Leg 1):
- Bar chart: row counts per cycle (Main vs Episode)
- Heatmap: NaN rates per column × cycle
- Box plots: weight distributions per cycle
- Category frequency tables: side-by-side for all residential demographic variables
- Episode density histogram: episodes per respondent per cycle

**Office-specific panels** ⚠️ NEW (Leg 2):
- **NOC × NAICS cross-tab heatmap** — respondent count (weighted) in each NOC bucket × NAICS sector cell, per cycle. Verifies that the two bucketing variables are jointly plausible and that no single cell dominates implausibly.
- **Telework-rate-per-cycle bar chart** — share of employed respondents with a non-NaN telework flag (`MAR_Q190` / `WTI_130` / `TLWK_01A`), by cycle. Should show a near-zero or very small rate in 2005/2010, a small uptick in 2015, and a marked jump in 2022 (the COVID WFH signal — consistent with the ~17.4% telework share documented in `00_GSS_split_suitability_audit.md` §5).
- **`occPRE` distribution bar** — share of episode rows in each of the 18 `occPRE` categories, per cycle. Category 2 (workplace) should be the second-largest after category 1 (home); a visible COVID-era dip from 2015 to 2022 (reflecting WFH coding to home, not work) is expected and correct.
- **2015 WET_120 suppression notice** — a plain-text panel in the HTML report flagging: "Class-of-worker (`WET_120`) is suppressed in the 2015 PUMF and is absent from `main_2015.csv`. This is an expected miss documented in `00_GSS_split_suitability_audit.md` §A. NOC/NAICS serve as archetype proxies for the 2015 cycle."

**Pros:** Single artifact to review; captures the COVID WFH jump visually; shareable with collaborators.
**Cons:** Requires matplotlib/seaborn; longer to build and run; the NOC×NAICS heatmap may be sparse for some cycle/sector combinations.

---

## Recommended Combination

For a practical validation before Step 2, combine **Methods 1 + 2 + 3 + 5** into a single script:

1. **Schema & Shape Audit** → confirms nothing broke during reading, and explicitly logs the 2015 WET_120 expected miss.
2. **Cross-Cycle Category Comparison** → confirms the right office columns were extracted and have plausible bucket counts (NOC ~10, NAICS ~16, telework sparse).
3. **Episode Integrity Check** → confirms `occPRE` is carried on every episode row and the AT_WORK-compatible share is non-trivial but small.
4. **Visual Summary Dashboard** → produces an HTML report with the NOC×NAICS heatmap and the telework-rate bar to capture the COVID jump visually.

Method 4 (weights) is included as a free add-on — it costs negligible time and catches file-corruption errors before any downstream steps.

---

## Proposed Output

### [NEW] `01_readingGSS_2split_val.py`

A validation script that:
1. Loads the 8 CSV files from `Step1_docs/outputs_step1/` (4 Main + 4 Episode: `main_2005.csv`, `main_2010.csv`, `main_2015.csv`, `main_2022.csv`, `episode_2005.csv`, `episode_2010.csv`, `episode_2015.csv`, `episode_2022.csv`)
2. Runs the selected validation methods (Methods 1–3 + 5 recommended)
3. Prints a structured console report with ✅ / ❌ / ⚠️ per check; logs the 2015 WET_120 miss as `❌ EXPECTED` not `❌ FAIL`
4. Saves the console report to `outputs_step1/validation_report.txt`
5. Optionally saves the HTML dashboard (with office-specific panels) alongside the text report

> **Windows encoding note (inherited from Leg 1).** The script uses Unicode emoji in print statements (✅, ❌, ⚠️). Run with `py -X utf8` or set `PYTHONIOENCODING=utf-8` in the parent shell to avoid cp1252 encoding crashes on Windows.

---

## Verification

The validation script itself passes if:
- All 8 CSV files load without error
- No check produces an unacknowledged `❌` — that is, every failure is either genuinely clean or explicitly documented (the 2015 `WET_120` suppression is the only pre-declared expected miss)
- The `occPRE` column is present and non-null (<5% NaN) in all four episode files
- The NOC and NAICS columns show plausible bucket counts per cycle (~10 and ~16 respectively)
- The telework bar shows a visible 2015→2022 jump (the COVID WFH signal)

Known-acceptable cross-cycle differences that should NOT be flagged as failures:
- 2015 `WET_120` absent — suppressed in PUMF, use NOC/NAICS as proxy
- 2005 telework variable absent — `MAR_Q190` exists only from 2010; 2005 telework NaN is expected
- 2022 AT_WORK-compatible `occPRE==2` share slightly lower than 2015 — WFH coding to home (LOCATION=3300) is physically correct; the office channel should not count WFH workers

---

## Progress Log

### 2026-06-13 — Initial Leg-2 Step-1 validation doc authored

Scope: defines how to verify the 8 Step-1 CSVs (4 Main + 4 Episode across cycles 2005/2010/2015/2022) are correct before Step 2 harmonization, with specific attention to the office-gating columns new to the Leg-2 two-channel split. Residential checks are reused unchanged from the Leg-1 counterpart (`2J_docs_occ_nTemp/01_readingGSS_val.md`); the new validation surface covers activity-last-week, worked-last-week, LF status, hours worked, class of worker (NOC, NAICS, COW), and telework/WFH variables.

**Expected miss documented:** `WET_120` (class of worker) is suppressed in the 2015 PUMF and will be absent from `main_2015.csv`. This is a pre-declared expected miss — the validation script must log it as `❌ EXPECTED` and not treat it as a pipeline failure. Source: `00_GSS_split_suitability_audit.md` §4.

**Five methods defined:** Schema & Shape Audit (with office column checklist + 2015 WET_120 handling); Cross-Cycle Category Comparison (with NOC/NAICS bucket counts and telework sparsity check); Episode Integrity Check (with `occPRE` presence, range, and AT_WORK-compatible share); Weight Distribution Sanity Check (fully reused from Leg 1); Visual Summary Dashboard (extended with NOC×NAICS heatmap and telework-rate-per-cycle bar capturing the COVID jump).

**Recommended combination:** Methods 1 + 2 + 3 + 5; script name `01_readingGSS_2split_val.py`; report saved to `outputs_step1/validation_report.txt`.

---

### 2026-06-13 — Validator implemented (01_readingGSS_2split_val.py)

**File:** `3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/01_readingGSS_2split_val.py` (standalone; no dependency on the reader module — all column maps defined inline).

**Methods implemented:**

- **Method 1 — Schema & Shape Audit:** Residential null checks reused from Leg 1. Office column presence checklist runs per-cycle for all 8 office variable groups (activity-last-week, worked-last-week, LF status, hours, class-of-worker, NOC, NAICS, telework + 2022 extras). 2015 `WET_120` absence is logged as `ℹ️ KNOWN SUPPRESSED in 2015 PUMF — expected miss, not a bug` (not a FAIL). All other missing office columns are soft `⚠️ warn` rather than hard failures.

- **Method 2 — Cross-Cycle Category Comparison:** Residential `DEMO_VARS` loop reused. Office extension checks: NOC bucket count ~10 (warn if <5 or >15); NAICS bucket count ~16 (warn if <8 or >25); class-of-worker 3–6 codes (warn if <3 or >15, 2015 WET_120 silently skipped if absent); activity-last-week 4–10 codes (warn if <4 or >20); telework sparsity — FAIL if 2022 non-NaN <1%, WARN if pre-2022 cycles >10%.

- **Method 3 — Episode Integrity Check:** Residential ID-linkage (>95% overlap) and time-ordering (>90% pass rate) reused. Office `occPRE` extension: presence check (FAIL if absent); NaN rate <5% (WARN if exceeded); value range 1–18 (WARN on out-of-range); AT_WORK-compatible share `(occPRE==2).mean()` expected 2–10% (FAIL if 0%, WARN if outside range); `AT_WORK` column itself must be ABSENT (FAIL if present — derived in Step 2/3 only).

- **Method 5 — Visual Summary Dashboard:** Residential charts retained (row counts, episode density violin, NaN heatmap over office columns, time-ordering pass rate). Four office-specific panels added: (5) NOC×NAICS weighted cross-tab heatmap per cycle; (6) telework non-NaN rate per cycle bar (COVID jump visible in 2022); (7) occPRE distribution per cycle (category 2 = workplace, COVID dip 2015→2022 expected); plus a styled WET_120 suppression notice panel in the HTML report. HTML saved to `outputs_step1/validation_report.html`; console saved to `outputs_step1/validation_report.txt`.

**Missing-CSV robustness:** if any of the 8 CSVs is absent, the script logs a clear `⚠️ warn` and skips that cycle's checks — no crash.

**Missing-column robustness:** 2015 `WET_120` → `ℹ️ info` (expected); all other absent office columns → `⚠️ warn`; script never raises `KeyError` on missing columns.

**Windows encoding:** header comment instructs `py -X utf8` on Windows; all file writes use `encoding="utf-8"`; matplotlib uses `Agg` backend (no display required).

**py_compile result:** `py -3 -m py_compile 01_readingGSS_2split_val.py` — CLEAN (exit 0, no errors).
