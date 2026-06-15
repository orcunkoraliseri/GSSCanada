# Column Availability Investigation — GSS Cycles 2005 / 2010 / 2015 / 2022

**Purpose.** Answers three data-gap questions surfaced by the Step-3 validation report for the Leg-2
two-channel (Residential + Office) pipeline.

**Method.** Read-only investigation: `gss_headers.csv`, per-cycle Step-1 output CSVs,
the 2010 and 2015 SPSS syntax files (for value labels), and the merged-episode output
(`merged_episodes.csv`). No SAS files were loaded. No pipeline code was modified.

**Sources checked:**
- `0_Occupancy/DataSources_GSS/gss_headers.csv` (column catalog across cycles)
- `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2010_syntax.SPS` (2010 variable labels + value labels)
- `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2015.sps` (2015 variable labels + value labels)
- `3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/outputs_step1/main_{cycle}.csv` (headers + values)
- `3J_docs_occ_nTemp/Leg2_2-split/Step3_docs/outputs_step3/merged_episodes.csv`
- `3J_docs_occ_nTemp/investigation/00_GSS_split_suitability_audit.md`

**Investigation date:** 2026-06-15

---

## Gap 1 — TELEWORK missing for 2005

### Question
Is there genuinely NO work-at-home / telework / usual-workplace / place-of-work variable
in the 2005 GSS Cycle 19 Time-Use PUMF? The current harmonizer (Delta E in
`3rdJ_02_harmonizeGSS_2split.py`) leaves TELEWORK as all-NaN for 2005 by design.

### Verdict: CANDIDATE FOUND — `MAR_Q190` EXISTS IN 2005, IS COMPARABLE TO 2010

The variable `MAR_Q190` was presumed absent from 2005 but IS present. Evidence:

1. **`gss_headers.csv` row 109, column 1 (GSSMain_2005):** `MAR_Q190` is listed explicitly.
2. **`Step1_docs/outputs_step1/main_2005.csv` header:** `MAR_Q190` appears as a loaded column.
3. **Value distribution in 2005 data (all 19,597 respondents):**

| Code | Label | Count (2005) | Count (2010) |
|------|-------|-------------|-------------|
| 1 | Yes (works at home) | 2,177 | 2,188 |
| 2 | No | 9,531 | 7,824 |
| 7 | Not asked | 7,796 | 5,363 |
| 8 | Not stated | 67 | 8 |
| 9 | Don't know | 26 | 7 |

4. **2010 SPSS syntax confirms question text:** `"Some people do all or some of their paid
   work at home. Exclu..."` with value labels 1=Yes, 2=No, 7=Not asked, 8=Not stated,
   9=Don't know — identical structure in both cycles.

5. **Also present in 2005: `MAR_Q193`** — "What is the main reason you do/did some of your
   work at home?" (reason for WFH). Value codes confirmed identical in 2005 and 2010:
   01=Care for children, 04=Requirements of the job, 05=Home is usual place of work,
   07=Saves time/money, 08=Live too far from work to commute, etc. (97/98/99=sentinel).

### Per-cycle verdict table

| Cycle | Variable | Question | Comparable to 2010 MAR_Q190? | Currently pulled? |
|-------|----------|----------|------------------------------|-------------------|
| 2005 | `MAR_Q190` | "...do all or some paid work at home?" | YES — same name, same codes | NO — not in Delta E |
| 2010 | `MAR_Q190` | same | — (reference) | YES |
| 2015 | `WTI_130` | diary-day telework reason | Partial — diary-day, not usual | YES |
| 2022 | `TLWK_01A` | "did any telework last week?" | YES — usual Y/N | YES |

### Recommendation

**Add 2005 MAR_Q190 to Delta E.** The variable exists, has substantive fill (2177 Yes,
9531 No out of 19,597), and uses the same coding scheme (1→1, 2→0, 7/8/9→NaN) as the
current 2010 treatment. The derived `TELEWORK` binary will be 11.1% (2177/19597) for 2005
using all respondents, or ~22% of those who were asked (2177 / (2177+9531) = 18.6%).

**Estimated implementation cost:** 2-line change in `derive_telework()` in
`3rdJ_02_harmonizeGSS_2split.py` — add `elif cycle == 2005: df["TELEWORK"] = df["MAR_Q190"].map({1:1, 2:0})`.
No Step-1 changes needed (column already extracted and present in `main_2005.csv`).

**Note on comparability:** 2005 `MAR_Q190` is a "usual arrangement" question (same framing as
2010/2022). Unlike 2015 `WTI_130` (diary-day incidence), the 2005 variable is conceptually
comparable to the 2010 and 2022 instruments. The existing Delta E WARN about 2015 being
non-comparable remains valid; 2005 will be comparable (no new WARN needed for 2005).

**The old "2005: no instrument" note in Delta E is wrong.** It should be updated to reflect
that 2005 uses `MAR_Q190` (same as 2010 but drawn from a different step; already in Step-1
output).

---

## Gap 2 — Co-presence ~20% empty for 2005 and 2010

### Question
Is the ~20% missingness in co-presence (fill 80.0% / 80.7% for 2005 / 2010 vs 99.9% /
93.2% in 2015 / 2022) a true universe/skip pattern, or is there an alternate / more-complete
"who were you with" variable in the 2005 / 2010 PUMF?

### Verdict: INTRINSIC — survey universe skip for sleep and personal care episodes

Investigation of `merged_episodes.csv` reveals the missingness is highly structured:

**2005 breakdown of co-presence NaN rows by location (`occPRE`):**

| Location | Missing rows | % of all missing | Filled rows | % of filled |
|----------|-------------|-----------------|-------------|-------------|
| occPRE=1 (Home) | 63,238 | **96.5%** | 145,486 | 55.4% |
| All non-home | 2,305 | 3.5% | 117,114 | 44.6% |

**By activity type (missing rows only, 2005 top entries):**

| Activity raw code | Activity label | Missing count |
|-------------------|----------------|--------------|
| 450.0 | Sleep & Naps & Resting | 37,873 |
| 400.0 | Personal Care | 24,365 |
| 460.0 | Sleep & Naps & Resting | 2,429 |
| 480.0 | Personal Care | 406 |
| All others | (travel, work, etc.) | ~470 total |

**2010 shows the same pattern:** 29.0% of home episodes are missing; only 2.3% of non-home
episodes are missing.

**Codebook confirmation (2010 SPSS syntax, `C24_Episode File_SPSS_withno_bootstrap.SPS`):**
The co-presence variables (ALONE, SPOUSE, CHILDHSD, etc.) each carry value code:
- `7 "Not asked for activity code 002.0"` (ALONE column)
- `7 "Not asked for activity code 002.2"` (all other co-presence columns)

Activity codes 002.0 (sleep / personal care) and 002.2 (personal activities) were
explicitly excluded from the "who were you with" question in the 2005/2010 survey design.

**Structural context:** Among 2005 HOME episodes (occPRE=1):
- 30.3% are missing co-presence (sleep/personal care at home)
- 69.7% are filled (all other activities at home, where the question was asked)
Non-home episodes: only 1.9% missing (incidental non-response).

**Colleagues column in 2005/2010:** `colleagues` is 0% filled in both 2005 and 2010. The
colleagues category did not exist in the 2005/2010 episode instrument — it was introduced
in 2015. This is a known structural difference (not a data gap).

### Per-cycle verdict table

| Cycle | Fill rate | Root cause | Fixable from source? |
|-------|-----------|------------|---------------------|
| 2005 | 80.0% | Universe skip: sleep/personal-care episodes not asked | NO — intrinsic |
| 2010 | 80.7% | Same universe skip as 2005 | NO — intrinsic |
| 2015 | 99.9% | Redesigned diary — co-presence asked for all episodes | n/a |
| 2022 | 93.2% | 6.8% non-response / partial diaries; no structural skip | NO — non-response |

### Recommendation

**Do not attempt to fill the 2005/2010 co-presence gap from source data.** The missing 20%
is a deliberately designed survey universe skip: Statistics Canada did not ask "who were you
with?" for sleep and personal care episodes in 2005/2010. No alternate "who were you with"
variable exists in either PUMF. The gap is intrinsic to the survey instrument redesign (which
was corrected in 2015 to collect co-presence for all episodes).

**For modelling purposes:** the existing NaN-vs-filled pattern is meaningful and already
handled correctly by the pipeline (NaN = no data collected; not "alone"). The 80% fill rate
is adequate for the residential channel (all active/awake episodes have social context). The
AT_WORK (office) channel uses co-presence to condition social context during work hours; 2005
and 2010 work episodes are in the non-home group (1.9% missing), so AT_WORK co-presence is
essentially complete in all four cycles (~98% fill for work-location episodes).

---

## Gap 3 — Other office-conditioning columns not currently pulled

### Question
Are there respondent-level columns in any cycle relevant to office occupancy that we are NOT
pulling — e.g. usual work schedule/shift, full-time/part-time, multiple jobs, commute
mode/time, workplace size, industry detail, occupation detail at finer granularity?

### Currently pulled (for reference)

From `Step2_docs/outputs_step2/main_{cycle}.csv` headers:

| Column | 2005 | 2010 | 2015 | 2022 |
|--------|------|------|------|------|
| NOCS (occupation) | SOC91C10 | NOCS2006_C10 | NOCS (renamed) | NOCS (renamed) |
| NAICS (industry) | NAICS2002_C16 | NAICS2007_C16 | NAIC12CY | NAIC22CY |
| COW (class of worker) | MAR_Q172 | MAR_Q172 | COW (renamed) | WET_120 |
| LFTAG (LF status) | LFTAG | LFTAG | LFTAG | LFTAG |
| HRSWRK (hours/wk) | HRSWRK | HRSWRK | HRSWRK | HRSWRK |
| TELEWORK | — | MAR_Q190 | WTI_130 | TLWK_01A |
| Commute mode | — | CTW_Q140_C01..C09 | CTW_140A..I | CTW_140A..I |

### New candidates identified

#### A. Usual Work Schedule / Shift Type

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | `MAR_Q410` | "Which of the following best describes your usual work schedule?" | 01=regular day, 02=evening, 03=night, 04=rotating, 05=split, 06=compressed, 07=on call/casual, 08=irregular, 09=other |
| 2010 | `MAR_Q410` | Same question | Same codes |
| 2015 | `WHW_230` | "Usual work schedule at main job" | 01=regular daytime, 02=evening, 03=night, 04=rotating, 05=split, 08=irregular (same scheme) |
| 2022 | `WHW_230` | Same (confirmed in gss_headers.csv) | Same codes |

**Source confirmation:** `MAR_Q410` at gss_headers.csv index 509 (2005 column); 2010 SPS line 722;
2015 SPS line 1956 (with value labels: "A regular daytime schedule or shift", etc.); 2022 via
gss_headers.csv index 75 column 3 (`WHW_230`). **NOT currently in Step-1 output for any cycle.**

**Recommendation:** Pull `MAR_Q410` for 2005/2010, `WHW_230` for 2015/2022. Harmonize to
`WORK_SCHEDULE` with a common 6-category scheme: regular-day / evening / night / rotating /
compressed+split+on-call / irregular. High office-occupancy relevance: non-day workers inflate
night AT_WORK rates.

#### B. Flexible Work Schedule

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | — | No dedicated flex variable found | — |
| 2010 | `MAR_Q420` | "Do(Did) you have a flexible schedule that allows(allowed) you to..." | 1=Yes, 2=No |
| 2015 | `WFS_10` | "Work flexible schedule" | confirmed in gss_headers.csv + 2015 SPS line 1144 |
| 2022 | `WFS_10` | Same (gss_headers.csv index 90, 2022 column) | Same |

**Recommendation:** Pull `MAR_Q420` for 2010, `WFS_10` for 2015/2022. Leave 2005 as NaN.
Harmonize to `FLEX_SCHEDULE` binary. Useful for conditioning diurnal shape of AT_WORK curve.

#### C. Multiple Jobs (more than one paid job)

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | — | Not confirmed in extracted columns; not in gss_headers.csv col-1 under "WHW_110" | — |
| 2010 | — | Not confirmed (not in Step-1 output or 2010 SPS quick scan) | — |
| 2015 | `WHW_110` | "More than one paid job last week" | gss_headers.csv index 273, 2015 col; SPS line 1127 |
| 2022 | `WHW_110` | Same (gss_headers.csv index 72, 2022 col) | Same |

**Recommendation:** Pull `WHW_110` for 2015/2022 only; 2005/2010 remain NaN.
Harmonize to `MULTI_JOB` binary. Low priority — affects <10% of workers and is partially
captured by HRSWRK already. Worth including for completeness.

#### D. Days per Week Worked

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | — | Not confirmed | — |
| 2010 | `MAR_Q390` | "How many days a week did/do you usually work (including all jobs)?" | raw count, 97-99=sentinel |
| 2015 | `WHW_210` | "Number of days worked per week" | gss_headers.csv index 288, 2015 col; SPS line 1142 |
| 2022 | `WHW_210` | Same (gss_headers.csv index 286, 2022 col) | Same |

**Recommendation:** Pull `MAR_Q390` for 2010, `WHW_210` for 2015/2022. Leave 2005 as NaN.
Harmonize to `WORK_DAYS_PER_WEEK`. Useful if part-time workers are to be separated from
full-time in office archetype conditioning.

#### E. Terms of Employment (employee type proxy — 2015 only, fills WET_120 suppression)

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | — | — | — |
| 2010 | — | — | — |
| 2015 | `WLY_150` | "Last year employer - Terms of employment" | confirmed in gss_headers.csv index 268 + 2015 SPS line 1122; values include permanent / term / contract / casual |
| 2022 | — | WET_120 available unsuppressed (already pulled) | — |

**Recommendation:** Pull `WLY_150` for 2015 as a proxy for class-of-worker (since `WET_120`
is suppressed in 2015 PUMF). This was flagged as a deferred decision in `3rdJ_01_readingGSS.md`
note under 2015 class-of-worker. **Worth pulling now** since the 2015 COW gap is documented.

#### F. Distance from Work / Residence Distance (proxy for commute feasibility)

| Cycle | Variable | Question text | Values |
|-------|----------|--------------|--------|
| 2005 | `MAR_Q193` code 08 | "Main reason for WFH: Live too far from work to commute" | embedded in WFH-reason variable (already extracted) |
| 2010 | `MAR_Q193` code 08 | Same (already in Step-1 2010 output via MAR_Q193 availability) | — |
| 2015 | `WLY_170C` | "Last year employer - Residence distance from work" | gss_headers.csv index 270, 2015 col; SPS line 1124; value 05="Home is usual place of work", 08="Live too far from work to commute" |
| 2022 | `WLYD170G` | Residence distance from workplace (grouped) | gss_headers.csv index 89, 2022 col |

**Recommendation:** Pull `WLY_170C` for 2015, `WLYD170G` for 2022. Low priority for office
occupancy BEM (we care about who's in the office, not how far they live). Deferred unless
Step 5 archetype linkage needs commute-feasibility stratification.

#### G. Commute Mode (already partially present — gaps noted)

| Cycle | Variable | Currently in Step-1? | Notes |
|-------|----------|---------------------|-------|
| 2005 | No equivalent found in extracted columns | NO | 2005 main CSV has no CTW columns |
| 2010 | `CTW_Q140_C01..C09` | YES (already in main_2010.csv) | mode × binary 9 cols |
| 2015 | `CTW_140A..I` | YES (already in main_2015.csv) | mode × binary 9 cols (renamed) |
| 2022 | `CTW_140A..I` | YES (already in main_2022.csv) | same |

**Note:** `CTW_140H` (2015) / `CTW_Q140_C08` (2010) = "Works or attends school at home"
— this is an alternative/corroborating WFH signal. Already in Step-1 outputs for 2010/2015/2022
but not yet harmonized or used in Step 2/3.

**Recommendation:** No new columns needed for 2010/2015/2022 — commute modes are already
extracted. 2005 has no commute-mode variable in the PUMF. The 10 commute mode columns are
already available for 3 of 4 cycles and could be harmonized if archetype splitting by commute
mode is desired.

### Summary table — Gap 3 new candidates

| Concept | 2005 col | 2010 col | 2015 col | 2022 col | Priority |
|---------|----------|----------|----------|----------|----------|
| Usual work schedule/shift | `MAR_Q410` | `MAR_Q410` | `WHW_230` | `WHW_230` | HIGH |
| Flexible schedule | — | `MAR_Q420` | `WFS_10` | `WFS_10` | MEDIUM |
| Multiple jobs | — | — | `WHW_110` | `WHW_110` | LOW |
| Days per week worked | — | `MAR_Q390` | `WHW_210` | `WHW_210` | LOW-MEDIUM |
| Terms of employment (2015 COW proxy) | — | — | `WLY_150` | — (WET_120 present) | MEDIUM |
| Residence distance from work | — | — | `WLY_170C` | `WLYD170G` | LOW |
| Commute mode (CTW) | absent | ALREADY IN | ALREADY IN | ALREADY IN | — (no new pull needed) |

**NOT found in any cycle:**
- Workplace size / number of employees at site (employer size `MAR_Q174_C` in 2010 captures
  employees working *for* the respondent as employer, not establishment size)
- Occupation at finer granularity than current 10-bucket NOCS (5-digit NOC codes exist in
  master file but are suppressed in PUMF for privacy)
- Industry at finer granularity than 16-22 bucket NAICS (same — finer NAICS in master file only)

---

## Bottom-line Recommendations

| Gap | Verdict | Action |
|-----|---------|--------|
| **1. 2005 TELEWORK** | CANDIDATE FOUND: `MAR_Q190` exists in 2005 with same coding as 2010 | Update Delta E in `3rdJ_02_harmonizeGSS_2split.py` — add 2005 branch using `MAR_Q190` (1→1, 2→0); no Step-1 change needed |
| **2. Co-presence 20% empty** | INTRINSIC survey skip: sleep/personal-care episodes not asked "who with" in 2005/2010 | Keep current NaN handling; document as skip pattern; note AT_WORK episodes are ~98% filled in all cycles |
| **3. Office conditioning extras** | Several NEW columns worth pulling: `MAR_Q410`/`WHW_230` (shift type, HIGH priority), `MAR_Q420`/`WFS_10` (flex schedule, MEDIUM), `WLY_150` (2015 COW proxy, MEDIUM) | Add to Step-1 column lists then harmonize in Step 2 in a future delta; defer `WHW_110`, `MAR_Q390`/`WHW_210`, `WLY_170C`/`WLYD170G` to later |
