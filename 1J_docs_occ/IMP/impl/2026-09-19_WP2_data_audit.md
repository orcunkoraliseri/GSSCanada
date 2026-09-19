# WP2 data audit (1J JBPS revision) — task and implementation state

Task doc:   this file (sections "Task" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §2 comment 2, P4, P7, P8; §5 WP2
Status:     DONE

## Task

READ-ONLY. You change no code, no data and no manuscript. You only read, count and write into THIS file.

Paper: JBPS 266775447, submitted PDF `1J_docs_occ/IMP/86e336cb-ac8c-4230-946f-20ff060f5bc4.pdf`
(PDF page N = manuscript page N-1). Reading copy: `1J_docs_occ/manuscript/1st_Occ_Journal.md`.
Pipeline code: `eSim/eSim_occ_utils/{06CEN05GSS,11CEN10GSS,16CEN15GSS,21CEN22GSS,25CEN22GSS_classification}`
and `eSim/eSim_bem_utils/`. Outputs: `0_Occupancy/Outputs_*`, `0_Occupancy/Outputs_CENSUS`,
`0_Occupancy/Outputs_GSS`, `0_Occupancy/DataSources_GSS`, `0_Occupancy/DataSources_CENSUS`.

Answer four questions. Every answer cites `file:line` or a file path plus the exact count you read.

**Q1. Region.** For each cycle (2005, 2010, 2015, 2022, and the 2025 generated cohort), does the
code filter or weight Census or GSS records by province (PR = 24 Quebec), by CMA (Montreal = 462),
or by anything regional? Look at alignment, ProfileMatching, HH_aggregation, occToBEM and the
25CEN22GSS_classification scripts. Report what the code does, not what the paper says. If the
"province" Tier-1 matching variable exists, say whether it forces a Quebec match or only a
same-province match with the Census household (which may be anywhere in Canada).

**Q2. Survey weights.** Are GSS weights (e.g. WGHT_PER, WTBS_*, WGHT_EPI) or Census weights
(WEIGHT) used anywhere when building schedules, aggregating households, or computing the reported
occupancy metrics (occupied hours, daytime fraction 09:00-17:00)? `file:line` for every use, and
say "no use found" with the grep pattern you ran if none.

**Q3. Sample sizes per cycle**, re-derived from the files (never copied from the paper):
Census PUMF records (persons and households, national and Quebec) as actually read by the
pipeline; GSS respondents (national and Quebec); GSS diary episodes; households after cleaning /
aggregation; households in the pool used for simulation; the number actually simulated (the paper
says 100 per scenario-NU pairing); and the 2025 cohort (the paper says 323 households, p. 9).
Give each count with the file it came from. If a count cannot be found, write NOT FOUND and why.

**Q4. Household filter for simulation (P4).** The paper (p. 12) says only single-detached
households with 2 to 4 persons were kept. Find the filter in code (`file:line`), and report which
dwelling types and household sizes the six Neighbourhood Unit simulations actually drew from.

## Rules

- Python: `python` is not on the Bash PATH on this machine. Find the repo's interpreter (try `py`,
  a conda/venv under the repo or user profile) and write down which one you used.
- Never read a multi-MB file whole into your context; use `wc -l`, `head`, `grep -n`, or a short
  script that prints only counts. Scripts go in the session scratchpad, not the repo.
- If a check is ambiguous, write what you found and what is unclear. NOT FOUND beats a guess.
- Write state into this file as you go (below), not only at the end.
- Stop at about 150k tokens of context: write state, say "handoff needed".
- End your turn with the one-line status and the path of this file.

## Verified

Python used: `py` (Windows Python launcher) -> Python 3.13.5, pandas 2.3.3. `python`/`python3` on Git
Bash PATH resolve to a WindowsApps stub, not usable; `py` works and has pandas.

All counts below were re-derived with `py` one-off scripts in the session scratchpad (not saved to
repo) or with `wc -l` / `awk -F','` on the actual CSVs. No number was copied from the manuscript.

**Census PUMF (raw file actually read by each cycle's `*_alignment.py`, i.e. `cen*_filtered.csv`,
NOT `cen*_filtered2.csv` — that second file belongs to the separate 25CEN22GSS_classification
preprocessing path, see Decisions):**

| Cycle | File | Persons (nat) | Households (nat) | Persons (QC) | Households (QC) |
|---|---|---|---|---|---|
| 2006 (05GSS) | `0_Occupancy/Outputs_CENSUS/cen06_filtered.csv` | 309,841 | 124,358 | 73,860 (REGION==2) | 31,895 |
| 2011 (10GSS) | `0_Occupancy/Outputs_CENSUS/cen11_filtered.csv` | 333,008 | 133,192 | 79,580 (PR==24) | 34,458 |
| 2016 (15GSS) | `0_Occupancy/Outputs_CENSUS/cen16_filtered.csv` | 343,330 | 140,720 | 79,498 (PR==24) | 35,306 |
| 2021 (22GSS) | `0_Occupancy/Outputs_CENSUS/cen21_filtered.csv` | 361,915 | 149,789 | 82,992 (PR==24) | 37,512 |

Counted as: rows = persons; `HH_ID.nunique()` = households; QC = `PR==24` except 2006, whose raw
header has `REGION` not `PR` (2006 census has no SGC province column); `06CEN05GSS_alignment.py:296-312`
confirms `REGION==2` = Quebec for that file.

**GSS respondents and diary episodes (post-harmonisation `Aligned_GSS_*.csv`, the file
`*_alignment.py` actually hands to `ProfileMatcher`):**

| Cycle | File | Episodes (rows) | Respondents (unique occID) | QC respondents (PR==24) | QC episodes |
|---|---|---|---|---|---|
| 2005 | `0_Occupancy/Outputs_06CEN05GSS/alignment/Aligned_GSS_2005.csv` | 234,743 | 13,519 | 2,717 | 47,266 |
| 2010 | `0_Occupancy/Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv` | 219,584 | 11,748 | 1,798 | 30,966 |
| 2015 | `0_Occupancy/Outputs_16CEN15GSS/alignment/Aligned_GSS_2015.csv` | 241,227 | 15,240 | 3,139 | 52,291 |
| 2022 | `0_Occupancy/Outputs_21CEN22GSS/alignment/Aligned_GSS_2022.csv` | 145,417 | 10,618 | 2,084 | 28,906 |

All four files carry a harmonised `PR` column with the same 6-value scheme (10,24,35,46,48,59), so
`PR==24` is directly comparable across cycles (`harmonize_pr()` in each cycle's `*_alignment.py`).

**Households after cleaning/aggregation — three different pipeline branches give three different
numbers for the 2022 cycle; I could not establish which one the published manuscript numbers trace
to (see Decisions):**

- `21CEN22GSS_HH_aggregation.py` output (the branch actually called from `21CEN22GSS_main.py:86`,
  i.e. the documented pipeline), 25%-sample variant:
  `0_Occupancy/Outputs_21CEN22GSS/HH_aggregation/21CEN22GSS_Full_Aggregated_sample25pct.csv`
  → 92,938 unique `SIM_HH_ID` (awk unique-count on column 46, 68s over ~41M rows).
  Same branch, 2005 cycle: `0_Occupancy/Outputs_06CEN05GSS/HH_aggregation/06CEN05GSS_Full_Aggregated_sample25pct.csv`
  → 73,347 unique `SIM_HH_ID` (column 26, 21s over ~31M rows).
- A second, separate "aug_pipeline" branch (not called by `21CEN22GSS_main.py`; provenance not
  traced further): `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated.csv`
  is already one-row-per-household (wide format) → 286,536 households (`wc -l` minus header).
- The top-level BEM staging files (`BEM_Setup/BEM_Schedules_*.csv`, see next table) show yet a third
  number (144,465 for 2022). None of these three numbers equals another.

**Households in the pool actually used for simulation** (`BEM_Setup/BEM_Schedules_<year>.csv`,
top-level `BEM_Setup/`, distinct from `0_Occupancy/`; counted via unique `SIM_HH_ID`):

| File | Households (nat) | DTYPE breakdown | HHSIZE breakdown |
|---|---|---|---|
| `BEM_Schedules_2005.csv` | 144,507 | SingleD 76,365 / MidRise 30,740 / OtherDwelling 18,838 / HighRise 18,522 / `"8"` 42 | 1:42,422 2:50,619 3:21,581 4:19,346 5:10,539 |
| `BEM_Schedules_2010.csv` | 144,507 | identical to 2005, digit-for-digit | identical to 2005 |
| `BEM_Schedules_2015.csv` | 144,507 | identical to 2005, digit-for-digit | identical to 2005 |
| `BEM_Schedules_2022.csv` | 144,465 | SingleD 76,366 / MidRise 30,716 / OtherDwelling 18,835 / HighRise 18,505 / `"8"` 43 | 1:42,412 2:50,623 3:21,547 4:19,348 5:10,535 |
| `BEM_Schedules_2025.csv` | 23,882 | SingleD 13,402 / MidRise 4,864 / HighRise 2,516 / Attached 1,111 / DuplexD 864 / SemiD 823 / Movable 232 / OtherA 70 | 1:7,042 2:7,348 3:4,447 4:4,059 5:986 |

2005/2010/2015 are three different MD5s (`43e0c8a2…`, `5e974297…`, `0675e387…`) but an *identical*
household population, DTYPE mix and HHSIZE mix — only the per-hour schedule *values* differ between
them. This was not something I could explain from the code read in this session; flagged, not fixed.

**Number actually simulated (100 per scenario-NU pairing).** Not independently re-derived. The
Monte-Carlo output files only ever contain post-hoc `mean`/`std` per end-use per scenario
(`BEM_Setup/SimResults/BatchAll_MC_N20_v2/NUS_RC*/aggregated_eui.csv`, 6-7 lines each, columns
`<year>_mean,<year>_std`), consistent with an ensemble-and-aggregate design, but the literal
household count (100) is not recorded in any output file I found — no per-household raw result
files remain on disk for this batch. The SSE-selection code that would produce a top-100 cut exists
(`eSim/eSim_bem_utils/integration.py:98-134` `filter_matching_households`, sorted ascending by SSE)
but nothing in the surviving code slices the result to exactly the top 100 in a script I could
identify as the one that produced Figure 15 (see Q4 and Decisions).

**2025 cohort (paper says 323 households).** Not found. `BEM_Setup/BEM_Schedules_2025.csv` has
23,882 unique `SIM_HH_ID`. `0_Occupancy/Outputs_CENSUS/forecasted_population_2025_LINKED.csv` has
118,274 unique `SIM_HH_ID` (248,528 person-rows). `grep -rn "323" eSim/**/*.py` returns zero matches
anywhere in the pipeline code. NOT FOUND — no file or code path in scope produces the number 323.

## Findings Q1-Q4

**Q1 (Region).** No cycle and no script filters Census or GSS records down to Quebec only. What the
code does is (a) recode province codes to a common scale in `harmonize_pr()`
(`eSim/eSim_occ_utils/21CEN22GSS/21CEN22GSS_alignment.py:432-454`, same function name/shape in the
2005/2010/2015 files, e.g. `11CEN10GSS_alignment.py:289-339`, `16CEN15GSS_alignment.py:569-... `),
and (b) require EXACT equality on the recoded `PR` value (and separately on a 2-category `CMA`
"major-CMA vs. not" flag) as part of Tier-1 matching in every cycle's `ProfileMatcher`:
`DEFAULT_TIER_1` includes `"PR"` and `"CMA"` in all four cycles
(`21CEN22GSS_ProfileMatcher.py:26-35`; `06CEN05GSS_ProfileMatcher.py:68-74`;
`11CEN10GSS_ProfileMatcher.py:68-71`; `16CEN15GSS_ProfileMatcher.py:69-72`), and the match loop
enforces `catalog[col] == agent_val` for every Tier-1 column (`21CEN22GSS_ProfileMatcher.py:126-133`).
So: a Quebec Census household can only Tier-1-match a Quebec GSS respondent, a BC household only a
BC respondent, etc. — this is **same-province matching**, not a forced Quebec match, and Census
households may be (and are) from anywhere in Canada (see the national counts above: Quebec is
~22-25% of national persons in every cycle, not 100%). `CMA` is similarly a same-bucket
("one of Montreal/Quebec-City/Calgary/Edmonton/Vancouver" vs. "elsewhere") match, not
Montreal-specific — the code maps `[462,535,825,835,933] -> 1` (`21CEN22GSS_alignment.py:496-497`),
grouping five different CMAs into one category, so a "CMA==1" match does not mean "same city".
The 2025 synthetic-cohort pipeline (`25CEN22GSS_classification/05_census_linkage.py`) uses the same
design: `MATCH_KEYS` includes `PR` and `CMA` (line 75), with an optional `--region-tier` flag that
folds province to a 5-region level only as a Tier-2 fallback for 2005's incompatible legacy PR
encoding (lines 56-72, 916-922) — still same-region, never Quebec-only.

**Q2 (Survey weights).** No use found. `WGHT_PER` is read as a raw column in four places
(`eSim/eSim_occ_utils/21CEN22GSS/21CEN22GSS_alignment.py:34`,
`eSim/eSim_occ_utils/11CEN10GSS/11CEN10GSS_alignment.py:25`,
`eSim/eSim_occ_utils/25CEN22GSS_classification/05_census_linkage.py:236,246`,
`eSim/eSim_occ_utils/gss_reader.py:75,119,155`) and carried through into intermediate CSVs as a
passenger column, but is never multiplied against anything or passed to a weighted-mean/np.average
call anywhere in `eSim/eSim_occ_utils/` or `eSim/eSim_bem_utils/`. The script that actually computes
the paper's headline occupancy metrics uses a plain unweighted `.groupby('Hour')['Occupancy_Schedule'].mean()`
(`eSim/eSim_occ_utils/plotting/generate_occupancy_metrics_table.py:136,143`). `WGHT_EPI` exists as a
raw column in the 2005 and 2015 GSS source data (visible in `Aligned_GSS_2005.csv` /
`Aligned_GSS_2015.csv` headers) but `grep -rn "WGHT_EPI" eSim/**/*.py` returns zero matches — it is
never even read into a variable. `grep -rn "WTBS_"` and a Census `WEIGHT` column: zero matches
anywhere under `eSim/` (the only WTBS_/WEIGHT hits in the whole repo are in unrelated 2J/3J/4J
project trees, out of this task's scope). Census PUMF `WEIGHT`: not present as a retained column in
any `cen*_filtered*.csv` I inspected. Grep patterns run: `WGHT_PER|WTBS_|WGHT_EPI|WEIGHT\b|\bWGHT\b`
and `np\.average|weighted|weights=` over `eSim/**/*.py`.

**Q3 (Sample sizes).** See Verified table above for the full per-cycle numbers. Headline: Census and
GSS national/Quebec counts are solid and cycle-consistent. The "households after
cleaning/aggregation" number is ambiguous — three pipeline branches on disk give three different
counts for 2022 (92,938 / 286,536 / 144,465) and I could not determine from the code which one (if
any) is what the manuscript's Table numbers trace back to; only `21CEN22GSS_HH_aggregation.py` is
the branch actually invoked by `21CEN22GSS_main.py:86`. The "100 best-matching households per
scenario-NU pairing" (paper, Section 3.5) could not be independently re-counted because the
surviving simulation outputs are already aggregated to mean/std. The 2025 cohort's 323 figure (paper
p.9/p.10 depending on PDF pagination) does not match any household count found in any 2025-cohort
output file in scope (23,882 or 118,274 depending on pipeline stage); NOT FOUND.

**Q4 (Household filter, P4).** A DTYPE filter exists and is real: `load_schedules(csv_path,
dwelling_type=...)` filters strictly by `row_dtype != dwelling_type`
(`eSim/eSim_bem_utils/integration.py:359-363`), and it is called with `dwelling_type="SingleD"` in at
least the diagnostic script `eSim/eSim_tests/task30_dump_sse.py:37`. But **no HHSIZE 2-4 filter
exists anywhere in the BEM/simulation code I could find.** `load_schedules()` (the function every
simulation entry point uses to build its household pool) takes only `dwelling_type` and `region`
parameters — no household-size argument at all (`integration.py:323-335`). I grepped exhaustively
for any HHSIZE-based restriction (`isin([2,3,4])`, `2 <= ... <= 4`, `hhsize >= 2 and ... <= 4`, plain
"2 to 4") across `eSim/eSim_bem_utils/`, `eSim/eSim_tests/`, and `eSim/eSim_occ_utils/` and found
none; the only HHSIZE range filters anywhere in scope are `HHSIZE.isin([1,2,3,4,5])` in the
upstream harmonisation step (`21CEN22GSS_alignment.py:355,357`,
`25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py:272`), which keeps sizes 1 through 5,
not 2 through 4, and is not a simulation-selection filter — it runs at GSS/Census harmonisation, long
before any BEM household is chosen. So the code that is demonstrably in the repo can select
single-detached households of ANY size (1-5), ranked purely by SSE match to `TARGET_WORKING_PROFILE`
(`integration.py:98-134`); I found no code path that additionally restricts to 2-4 persons. Applying
DTYPE=="SingleD" alone to the 2022 pool gives 76,366 households spanning all five HHSIZE values
1-5 (`BEM_Schedules_2022.csv`, see Verified table); restricting further to HHSIZE in {2,3,4} (a
filter I could not find implemented) would leave 55,097 of those. I could not locate the specific
script that produced the published Figure 15 six-NU campaign (only aggregated `mean/std` outputs
survive under `BEM_Setup/SimResults/`), so I cannot rule out that an unfound script applies the
2-4 filter; I can only report that none of the code I read does.

## Decisions

- Treated `cen*_filtered.csv` (no "2") as the Census file actually read by the published per-cycle
  pipeline, because it is the literal path opened in each `*_alignment.py`'s `main()`
  (e.g. `21CEN22GSS_alignment.py:668`, `cen_reader.py:30-33`). `cen*_filtered2.csv` is a parallel
  output written by `eSim_datapreprocessing.py` for the separate 25CEN22GSS_classification (2025
  synthetic-cohort) preprocessing path and was NOT used for the Q3 Census counts, though its
  existence is noted in Verified.
- Did not pick a winner among the three "households after aggregation" numbers for 2022 (92,938 /
  286,536 / 144,465). This needed a manager decision (which pipeline run backs the submitted
  manuscript) that is outside a read-only audit's authority to assume.
- Assumed QC = `PR==24` is the correct Quebec test for the harmonised 2010/2015/2022 files and
  `REGION==2` for 2006, based on the explicit code comments in `06CEN05GSS_alignment.py:296-312` and
  `25CEN22GSS_classification/05_census_linkage.py:50-70` (`REGION_FOLD`, `_PR_MAP`). Not independently
  cross-checked against a StatCan codebook in this session.
- Did not try to reconcile the identical 2005/2010/2015 `BEM_Schedules_*.csv` household
  population/DTYPE/HHSIZE mix (different MD5, same demographic composition) — flagged as a finding,
  not investigated further; could mean a fixed comparison-household-pool design (plausible, given
  Section 3.5's "isolate behavioral evolution effects from occupancy category differences") or a
  data-pipeline artifact. Left for the manager to judge which.

## Next

Exact next action for a cold agent, if this needs to go further:
1. Ask the manuscript's author (or grep `1J_docs_occ/IMP/00_REVISION_PLAN.md` and any Step-8/Step-9
   working notes not read in this session) which of the three 2022 "aggregated households" numbers
   (92,938 / 286,536 / 144,465) is the one behind the manuscript's Table/sample-size claims, and
   whether `aug_pipeline` is a superseded/abandoned branch or the one actually used.
2. Locate (or accept as lost) the actual script/log that ran the six-NU, 36-pairing, 100-household
   Monte Carlo campaign referenced by Figure 15 — search `BEM_Setup/SimResults/*/logs` or any batch
   job manifest not yet inspected — to confirm or refute the "100 per pairing" and the
   single-detached-2-to-4-person filter claims directly against code, since I found the DTYPE filter
   but never the HHSIZE 2-4 filter or the literal N=100 slice.
3. Re-derive the 323-household 2025-cohort figure from whichever earlier pipeline stage (before
   DTYPE expansion / before the 848,528-row forecast) actually produces exactly 323 rows — not found
   in this session; grep `eSim/eSim_occ_utils/25CEN22GSS_classification/run_step1.py` /
   `run_step2.py` output logs (not opened in this session) for a printed household count near 323.

## WHAT I DID NOT VERIFY

- Which of the three "households after aggregation" pipeline branches (HH_aggregation/sample25pct,
  aug_pipeline, or the top-level BEM_Schedules staging files) is the one whose numbers ended up in
  the submitted manuscript.
- The literal "100 best-matching households selected per scenario-NU pairing" and the "single-
  detached, 2-4 persons" filter as applied to the ACTUAL six-NU campaign that produced Figure 15 —
  I verified the SSE-ranking code and the DTYPE filter exist, but found no HHSIZE 2-4 filter and no
  surviving per-household record of the campaign, so I could not confirm the filter or the N=100 cut
  against code+data together, only against code alone (DTYPE) or claims alone (the rest).
  For the six-NU campaign, checked `BEM_Setup/SimResults/BatchAll_MC_N20_v2/` and
  `BatchAll_MC_N3_1776120359/` only; did not check `Sim_plots/`, `_sql_cache/`, or `interim_report/`
  contents in any depth, nor any HPC batch logs, for a manifest listing the selected household IDs.
- The 323-household 2025 cohort figure — could not find it anywhere in data or code in scope.
- Did not open `eSim/eSim_occ_utils/25CEN22GSS_classification/run_step1.py`, `run_step2.py`,
  `run_step3.py`, or `main_classification.py` bodies in full (only grepped them) — the 2025 cohort's
  323 figure or its stratification-grid logic may be documented in a part of those files not read.
- Did not verify the Census `WEIGHT` variable is genuinely absent from the raw PUMF (only checked
  the pipeline's `Outputs_CENSUS` filtered outputs, not the original StatCan source files under
  `DataSources_CENSUS/`).
- Did not check `eSim/eSim_occ_utils/16CEN15GSS/16CEN15GSS_DTYPE_expansion.py` or the ML
  classification scripts for any additional region- or weight-related logic beyond the grep hits
  already reported (title/comment context only).
- Did not reconcile the 43/42-household `DTYPE=="8"` anomaly seen in every `BEM_Schedules_*.csv`
  (an unmapped numeric DTYPE code slipping through) — noted in passing, not investigated.
