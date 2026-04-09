# Task 4 — W7: Co-presence Encoding Audit (Phase A)

**SWOT Item:** W7 — Co-presence is encoded but its semantic consistency is fragile  
**Phase:** A (read-only audit). Phase B NOT triggered.  
**Date:** 2026-04-09  
**Inputs (read-only):**
- `2J_docs_occ_nTemp/02_harmonizeGSS.py` — co-presence harmonization block
- `2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data Harmonization - Category-CoPresence.csv`
- `2J_docs_occ_nTemp/outputs_step3/merged_episodes.csv` (1,049,480 rows, 4 cycles)

---

## Step 1 — Code Audit: `02_harmonizeGSS.py` co-presence block

### 1A. Raw column → unified column mapping (`COPRESENCE_MAP`)

| Unified column | 2005 raw | 2010 raw | 2015 raw | 2022 raw |
|----------------|----------|----------|----------|----------|
| Alone | ALONE | ALONE | TUI_06A | TUI_06A |
| Spouse | SPOUSE | SPOUSE | TUI_06B | TUI_06B |
| Children | CHILDHSD | CHILDHSD | TUI_06C | TUI_06C |
| parents | PARHSD | PARHSD | TUI_06E | TUI_06E |
| otherInFAMs | MEMBHSD | MEMBHSD | TUI_06D | TUI_06D |
| otherHHs | OTHFAM | OTHFAM | TUI_06G | TUI_06G |
| friends | FRIENDS | FRIENDS | TUI_06H | TUI_06H |
| others | OTHERS | OTHERS | TUI_06J | TUI_06J |
| colleagues | *(NaN)* | *(NaN)* | TUI_06I | TUI_06I |

### 1B. OR-merge: unmapped columns absorbed into unified targets

For **2005 and 2010** (Step C of `harmonize_copresence`):

| Unmapped raw column | Semantic meaning | Absorbed into |
|---------------------|-----------------|---------------|
| NHSDCL15 | Children of respondent living outside HH, age <15 | Children (OR-merge with CHILDHSD) |
| NHSDPAR | Parents or parents-in-law living outside HH | parents (OR-merge with PARHSD) |
| NHSDC15P | Children of respondent living outside HH, age ≥15 | otherInFAMs (OR-merge with MEMBHSD) |
| *(none)* | colleagues not measured 2005/2010 | colleagues = pd.NA |

For **2015 and 2022** (Step C of `harmonize_copresence`):

| Unmapped raw column | Semantic meaning | Absorbed into |
|---------------------|-----------------|---------------|
| TUI_06F | Other household adult(s) | otherInFAMs (OR-merge with TUI_06D) |
| TUI_06I | Colleague(s) / classmate(s) | colleagues (direct copy) |

### 1C. Missing-code handling

Before any renaming (Step A), the code replaces `{7, 8, 9}` → `pd.NA` on all raw
co-presence columns. This covers the "not asked" (7), "not stated" (8), and
"don't know" (9) codes documented in the codebook for every cycle.

### 1D. OR-merge logic

```
result = 1   if any source == 1          (person was present)
result = 2   if no source == 1, any == 2 (person was absent)
result = NaN if all sources are NaN       (not measured)
```

This logic correctly resolves conflicts: a single "present" reading from any
contributing column sets the merged result to 1 regardless of other sources.

---

## Step 2 — Codebook Cross-Check

Source: `Data Harmonization - Category-CoPresence.csv`

### 2A. Encoding direction (1 = present or 1 = absent?)

Across all four cycles the raw unique values are `{1, 2, 9}` (after 7/8 dropped):

| Cycle | Column | Question wording | 1 means | 2 means |
|-------|--------|-----------------|---------|---------|
| 2005/2010 | ALONE | "Social contacts — alone?" | **Yes (alone)** | No |
| 2005/2010 | SPOUSE | "Social contacts — with spouse/partner?" | **Yes (with spouse)** | No |
| 2005/2010 | CHILDHSD | "Social contacts — with children of HH <15?" | **Yes** | No |
| 2005/2010 | PARHSD | "Social contacts — with parent(s)/parent(s)-in-law in HH?" | **Yes** | No |
| 2005/2010 | MEMBHSD | "Social contacts — with other member(s) of the HH (incl. children ≥15)?" | **Yes** | No |
| 2005/2010 | OTHFAM | "Social contacts — with other family member(s) outside HH?" | **Yes** | No |
| 2005/2010 | FRIENDS | "Social contacts — with friends outside HH?" | **Yes** | No |
| 2005/2010 | OTHERS | "Social contacts — with others outside HH?" | **Yes** | No |
| 2005/2010 | NHSDCL15 | "Social contacts — with children of respondent outside HH, age <15?" | **Yes** | No |
| 2005/2010 | NHSDPAR | "Social contacts — with parent(s)/parent(s)-in-law outside HH?" | **Yes** | No |
| 2005/2010 | NHSDC15P | "Social contacts — with children of respondent outside HH, age ≥15?" | **Yes** | No |
| 2015/2022 | TUI_06A | "Social contact — Alone" | **Yes (alone)** | No |
| 2015/2022 | TUI_06B | "Social contact — With spouse/partner" | **Yes** | No |
| 2015/2022 | TUI_06C | "Social contact — With household children, age <15" | **Yes** | No |
| 2015/2022 | TUI_06D | "Social contact — With household child(ren), 15 years or older" | **Yes** | No |
| 2015/2022 | TUI_06E | "Social contact — With parent(s) or parent(s)-in-law" | **Yes** | No |
| 2015/2022 | TUI_06F | "Social contact — With other household adult(s)" | **Yes** | No |
| 2015/2022 | TUI_06G | "Social contact — With other family member(s) from other households" | **Yes** | No |
| 2015/2022 | TUI_06H | "Social contact — With friends" | **Yes** | No |
| 2015/2022 | TUI_06I | "Social contact — With colleague(s), classmate(s)" | **Yes** | No |
| 2015/2022 | TUI_06J | "Social contact — With other people" | **Yes** | No |

**Finding:** Encoding direction is **1 = present ("yes")** in every raw column in
every cycle, confirmed in both 2005/2010 (questionnaire wording) and 2015/2022
(TUI label). The OR-merge logic, which treats 1 as "present", is correct.

### 2B. Semantic consistency of column-to-column mapping

| Unified | 2005/2010 semantic | 2015/2022 semantic | Match? | Notes |
|---------|-------------------|-------------------|--------|-------|
| Alone | "alone?" | "Alone" | ✅ Identical | — |
| Spouse | "with spouse/partner?" | "With spouse/partner" | ✅ Identical | — |
| Children | "with HH children <15" + "children outside HH <15" (NHSDCL15) | "with HH children, age <15" only | ⚠️ Scope difference | 2005/2010 broader by NHSDCL15; adds non-HH children |
| parents | "with parents/parents-in-law in HH" + "outside HH" (NHSDPAR) | "with parent(s) or parent(s)-in-law" (no HH restriction) | ✅ Effectively equivalent | 2015/2022 question drops in/out distinction; net coverage similar |
| otherInFAMs | "other HH members (incl. children ≥15)" + "children outside HH ≥15" (NHSDC15P) | "HH children ≥15" (TUI_06D) + "other HH adults" (TUI_06F) | ⚠️ Scope difference | 2005/2010 includes outside-HH older children via NHSDC15P; 2015/2022 does not |
| otherHHs | "other family members outside HH" (OTHFAM) | "other family member(s) from other households" (TUI_06G) | ✅ Identical | — |
| friends | "friends outside HH" (FRIENDS) | "With friends" (TUI_06H) | ✅ Effectively identical | — |
| others | "others outside HH" (OTHERS) | "With other people" (TUI_06J) | ⚠️ Wording broadened | 2015/2022 drops "living outside household" qualification; in practice acts as catch-all; see §3 |
| colleagues | *(not measured)* | "colleague(s), classmate(s)" (TUI_06I) | N/A — expected | — |

**Three scope differences noted.** None involve an encoding flip (the 1/2
direction is consistent). They are pre-existing instrument differences between
survey generations, not harmonization errors. Details in §3.

---

## Step 3 — Output Sanity Check: per-cycle `== 1` shares

Computed on `merged_episodes.csv` (unweighted, over non-NaN episodes only).

### 3A. Episode counts and NaN rates

| Cycle | Total episodes | NaN rate (primary 8 cols) | NaN rate (colleagues) |
|-------|----------------|--------------------------|----------------------|
| 2005 | 328,143 | 20.0% | 100% (not measured) |
| 2010 | 279,151 | 19.3% | 100% (not measured) |
| 2015 | 274,108 | 0.1% | 0.1% |
| 2022 | 168,078 | 6.8% | 6.8% |

The 20% / 19.3% NaN rates in 2005/2010 are confirmed by Step 3 validation
(pre-existing data quality for early cycles, not introduced by harmonization).

### 3B. Per-cycle share of `== 1` (% of observed, non-NaN episodes)

| Column | 2005 | 2010 | 2015 | 2022 | Max spread | Flag (>10 pp)? |
|--------|------|------|------|------|-----------|----------------|
| Alone | 51.7% | 46.6% | 49.6% | 54.1% | **7.4 pp** | ✅ No |
| Spouse | 21.7% | 25.1% | 29.4% | 30.8% | **9.1 pp** | ✅ No |
| Children | 13.2% | 15.0% | 9.5% | 8.2% | **6.8 pp** | ✅ No |
| parents | 2.8% | 3.3% | 2.5% | 1.7% | **1.6 pp** | ✅ No |
| otherInFAMs | 3.4% | 4.5% | 3.3% | 3.7% | **1.2 pp** | ✅ No |
| otherHHs | 3.2% | 4.0% | 3.4% | 2.3% | **1.8 pp** | ✅ No |
| friends | 6.9% | 6.2% | 4.6% | 2.9% | **4.0 pp** | ✅ No |
| others | 7.8% | 9.1% | 5.8% | 2.7% | **6.4 pp** | ✅ No |
| colleagues | NaN | NaN | 4.6% | 3.0% | **1.6 pp** | N/A (2 cycles only) |

**No column exceeds the 10 pp flag threshold.** All unique values in the
output are `{1, 2, NaN}` — no unexpected codes survived harmonization.

### 3C. Interpretation of notable spreads

**Alone (7.4 pp, range 46.6–54.1%):**
All values fall within the 25–60% expected range for time-use diaries. The
increase from 2010 → 2022 is consistent with WFH-driven social atomization
(more time alone during the day). No encoding concern.

**Spouse (9.1 pp, range 21.7–30.8%):**
Monotonic increase across all four cycles. Plausible demographic explanations:
(a) population aging raises the share of older respondents who spend daytime
hours at home with a partner; (b) WFH from 2020 onward increases co-location
with spouse. The increase is not consistent with an encoding flip (a flip would
produce a step-change, not a monotonic gradient). Just below the 10 pp flag
threshold. No encoding concern.

**Children (6.8 pp, range 8.2–15.0%):**
The higher rates in 2005/2010 are partly explained by the scope difference
noted in §2B: the 2005/2010 harmonization OR-merges NHSDCL15 (children of
respondent living outside the HH, age <15) into the Children column. This
adds cases that have no equivalent in 2015/2022 (TUI_06C only covers
in-household children). The remaining gap reflects genuine demographic aging
(fewer households with young children over the 17-year window). No encoding
concern.

**others (6.4 pp, range 2.7–9.1%):**
The 2010 peak (9.1%) and 2022 low (2.7%) reflect two overlapping effects:
(a) the 2005/2010 question asks specifically about "others living outside the
household," while TUI_06J asks about "other people" — in 2015/2022 the
survey introduced additional granular categories (TUI_06F for other HH adults,
TUI_06I for colleagues) that would have been grouped into OTHERS in 2005/2010,
so the 2015/2022 residual "others" pool is structurally smaller; (b) the 2022
decline (2.7%) is additionally driven by COVID-era reduction in out-of-HH
social contacts. No encoding concern.

**friends (4.0 pp, range 2.9–6.9%):**
Monotonic decline. Consistent with documented longitudinal trends in social
isolation (fewer social contacts with friends over time), COVID-accelerated in
2022. No encoding concern.

---

## Step 4 — Decision Gate

**Encoding flip check result: CLEAR.**

| Check | Result |
|-------|--------|
| All columns use 1 = present, 2 = absent, consistently in code | ✅ Confirmed |
| Codebook direction matches OR-merge logic | ✅ Confirmed |
| Missing codes 7/8/9 → NaN applied before processing | ✅ Confirmed |
| No unexpected values in merged output (only {1, 2, NaN}) | ✅ Confirmed |
| No column exceeds 10 pp cross-cycle spread | ✅ Confirmed (max 9.1 pp, Spouse) |
| Any spread > 10 pp not explained by demographics | N/A — threshold not reached |

**Phase B is NOT triggered.** No encoding flip found in any of the 9 columns
× 4 cycles. The observed cross-cycle variation in `== 1` shares is
demographically explainable and consistent with a correctly encoded dataset.

**W7 audit note:** Three pre-existing scope differences exist between survey
generations (Children, otherInFAMs, others) that create systematic but small
baseline differences between 2005/2010 and 2015/2022 values. These are
instrument-level differences, not harmonization errors. They are within the
normal tolerance for multi-cycle time-use harmonization and do not warrant a
Phase B rebuild.

---

## Progress Log

**2026-04-09 — Phase A executed (Sonnet)**

Audit executed in full read-only mode. No code changed.

- `02_harmonizeGSS.py` co-presence block (lines 410–539): read only.
- `Data Harmonization - Category-CoPresence.csv`: codebook cross-check
  confirmed 1 = present in all 20 raw columns across all 4 cycles.
- `merged_episodes.csv`: per-cycle `== 1` shares computed; no flag triggered.
- Phase B: NOT triggered. W7 closes as audit-only.
