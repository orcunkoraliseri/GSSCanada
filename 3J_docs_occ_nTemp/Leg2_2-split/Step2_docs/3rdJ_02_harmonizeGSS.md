# 3rdJ Step 2 — Data Harmonization (Leg-2 Two-Channel Split)

## Goal

Port the Leg-1 GSS harmonizer (`2J_docs_occ_nTemp/02_harmonizeGSS.py`) to the Leg-2
Residential + Office two-channel pipeline. Residential logic is kept bit-identical to
Leg 1; the only additions are the five Office-channel deltas required to derive AT_WORK,
unified NOCS, unified NAICS, and TELEWORK binary across cycles 2005, 2010, 2015, 2022.

## Reference

- **Leg-1 template:** `2J_docs_occ_nTemp/02_harmonizeGSS.py` (786 lines)
- **Pipeline spec:** `3J_docs_occ_nTemp/Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md`
  - §2A: occPRE==2 crosswalk (PLACE=02 / LOCATION=301 / LOCATION=3301 per cycle)
  - §2B: WFH coding wrinkle (2022 LOCATION=3300 = home, not work)
- **Step-1 format references:**
  - `3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/3rdJ_01_readingGSS_2split.py`
  - `3J_docs_occ_nTemp/Leg2_2-split/Step1_docs/3rdJ_01_readingGSS.md`

## Data Source Inventory

| Input | Source | Location |
|-------|--------|----------|
| main_{cycle}.csv (× 4) | Step-1 output | `Step1_docs/outputs_step1/` |
| episode_{cycle}.csv (× 4) | Step-1 output | `Step1_docs/outputs_step1/` |
| Activity crosswalk Excel | Leg-1 references | `2J_docs_occ_nTemp/references_activityCodes/` |
| Presence crosswalk Excel | Leg-1 references | `2J_docs_occ_nTemp/references_Pre_coPre_Codes/` |

## Proposed Changes (Leg-2 Deltas)

### Delta A — Platform-detection path block
Identical to Step-1 Leg-2 reader: `_WIN_BASE`, `_SPEED_BASE`, `_MAC_BASE` in `__main__`.
Input/output resolved to absolute paths; passed as explicit arguments to `harmonize_all()`.

### Delta B — AT_WORK binary on every episode row
```python
df["AT_WORK"] = (df["occPRE"] == 2).astype(int)
```
Inserted in `apply_presence_crosswalk()` immediately after the `AT_HOME` line.
`occPRE==2` maps to workplace across all four cycles via the existing crosswalk table:
- 2005/2010: PLACE = 02
- 2015: LOCATION = 301
- 2022: LOCATION = 3301

**WFH coding wrinkle (2022):** paid-work-at-home is coded LOCATION=3300 (home), NOT
workplace. Therefore AT_WORK is ~6% lower in 2022 than raw workplace presence implies.
This is correct for office-zone BEM (home-workers belong in the residential channel).
Work-vs-school gating is deferred to Step 5 (archetype linkage); occPRE==2 includes
"at work or school" for 2015/2022, which is documented and accepted at this stage.

### Delta C — NOCS unification
2015 and 2022 already carry NOCS (renamed at Step 1 via MAIN_RENAME_MAP).
2005 retains `SOC91C10`; 2010 retains `NOCS2006_C10` (Step-1 reader left raw names).
`unify_nocs(df, cycle)` renames to NOCS for 2005/2010 only; drops source column.

### Delta D — NAICS unification
Per-cycle raw column → unified NAICS column:
- 2005: NAICS2002_C16 → NAICS
- 2010: NAICS2007_C16 → NAICS
- 2015: NAIC12CY → NAICS
- 2022: NAIC22CY → NAICS

Sentinel codes ≥ 90 (97, 98, 99) are set to pd.NA after rename.

### Delta E — TELEWORK binary
Output: `TELEWORK` column (Int8 nullable, {0, 1, NaN}).

| Cycle | Source variable | Coding | Instrument type |
|-------|----------------|--------|-----------------|
| 2005  | —              | all NaN | no instrument |
| 2010  | MAR_Q190       | 1→1, 2→0 | usual Y/N |
| 2015  | WTI_130        | 1..9→1, 96→0 | diary-day (NOT usual prevalence) |
| 2022  | TLWK_01A       | 1→1, 2→0 | usual Y/N (last week) |

**Flag:** 2015 WTI_130 is a diary-day incidence measure, not a usual-arrangement
instrument. Treat 2015 TELEWORK as diary-day prevalence only; not comparable to
2010/2022 usual Y/N rates.

## Module Structure Summary

```
3rdJ_02_harmonizeGSS_2split.py
├── SENTINEL_MAP, COPRE_COLS  (verbatim Leg 1)
├── recode_*()                (verbatim Leg 1)
├── build_activity_crosswalks()  (verbatim Leg 1)
├── apply_presence_crosswalk()   (+ Delta B: AT_WORK)
├── harmonize_copresence()       (verbatim Leg 1)
├── check_diary_closure()        (verbatim Leg 1)
├── unify_nocs()                 (NEW — Delta C)
├── unify_naics()                (NEW — Delta D)
├── derive_telework()            (NEW — Delta E)
├── harmonize_main()             (+ calls Deltas C/D/E after Leg-1 recodes)
├── harmonize_episodes()         (verbatim Leg 1)
├── harmonize_all(input, output, act_excel, pre_excel)  (explicit args — Delta A)
└── __main__                     (platform-detect → call harmonize_all)
```

## Expected Result

- `outputs_step2/main_{2005,2010,2015,2022}.csv` — 4 unified Main files with NOCS,
  NAICS, TELEWORK appended; all Leg-1 residential columns preserved bit-identical.
- `outputs_step2/episode_{2005,2010,2015,2022}.csv` — 4 unified Episode files with
  AT_HOME + AT_WORK added; all other Leg-1 episode columns preserved.
- AT_WORK episode-level rate expected ~8-12% for 2005/2010, ~6-10% for 2015/2022.
- TELEWORK rate: 2005=NaN, 2010=~20-35%, 2015=~5-15% (diary-day), 2022=~25-40%.
- NOCS/NAICS coverage: varies by cycle (working adults only; ≥10-70% of respondents).

## Test Method

1. Run `py -3 -X utf8 3rdJ_02_harmonizeGSS_2split.py` locally.
2. Confirm 8 CSV files created in `outputs_step2/`.
3. Confirm per-cycle spot-check console output (row counts, AT_WORK rate, TELEWORK rate).
4. Run validator: `py -3 -X utf8 3rdJ_02_harmonizeGSS_2split_val.py`.
5. Inspect `outputs_step2/step2_validation_report.html` for PASS/WARN/FAIL tally.
6. Target: 0 FAIL; any WARN must be documented and understood.

---

## Progress Log

### 2026-06-14 — Step 2 Harmonizer + Validator Built and Verified

**Deliverables created:**
- `3rdJ_02_harmonizeGSS_2split.py` — main harmonizer (all 5 Leg-2 deltas implemented)
- `3rdJ_02_harmonizeGSS_2split_val.py` — validator (12 methods, 4 new office-channel
  checks: AT_WORK rates, occPRE=2 share, TELEWORK per cycle, NOCS/NAICS coverage)
- `3rdJ_02_harmonizeGSS.md` (this file) + `3rdJ_02_harmonizeGSS_val.md`
- `3rdJ_s2_2split_harmonize.sh` + `3rdJ_s2_2split_valonly.sh` sbatch wrappers
- `outputs_step2/` directory with 8 harmonized CSVs + HTML/TXT validation reports

**Run confirmed locally (`py -3 -X utf8`). Scorecard: PASS 73 / WARN 1 / FAIL 0.**

**Per-cycle AT_WORK rates (episode-level, unweighted):**
- 2005: 7.57%  |  2010: 6.64%  |  2015: 6.29%  |  2022: 4.92%
- 2022 suppression from WFH coding (LOCATION=3300=home) is correct behavior.

**Per-cycle TELEWORK rates:**
- 2005: NaN (no instrument)
- 2010: 21.9% of 10,012 respondents (MAR_Q190 usual Y/N)
- 2015: 7.8% of 17,389 respondents (WTI_130 diary-day — NOT comparable to 2010/2022)
- 2022: 37.6% of 5,069 respondents (TLWK_01A usual Y/N last week)

**NOCS/NAICS coverage after sentinel nullification (codes 95-99 → NaN):**
- NOCS: 2005=65.9%, 2010=64.8%, 2015=60.4%, 2022=56.8% (10 buckets each)
- NAICS: 2005=65.9%, 2010=64.8%, 2015=57.7%, 2022=54.5% (16/19 buckets)

**Single WARN:** 2015 TELEWORK flagged as diary-day measure (expected and documented).

**Bug fixed during run:** `unify_nocs()` was renaming SOC91C10/NOCS2006_C10 → NOCS
but not nullifying sentinel codes 97/98/99 (2005/2010) and 95/96/99 (2015/2022).
Added `NOCS_SENTINELS = {95,96,97,98,99}` nullification step after rename.
Initial run had FAIL 2 on NOCS sentinels; fixed in same session, final run FAIL=0.

**Design decisions documented:**
- AT_WORK includes work+school for 2015/2022 (occPRE==2); gating deferred to Step 5.
- 2022 WFH suppression is correct behavior, not a bug.
- 2015 TELEWORK flagged as diary-day measure in both code docstring and validator.
- NAICS sentinels ≥90 → NaN applied uniformly.

**No blockers.** Step 2 outputs ready for Step 3.
