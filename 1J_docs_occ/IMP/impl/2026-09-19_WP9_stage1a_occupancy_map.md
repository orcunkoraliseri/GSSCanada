# WP9 Stage 1a: map how each cycle computes occupancy (1J JBPS revision), task and implementation state

Task doc:   this file (sections "Why" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7 log (m) and (n)
Source:     `1J_docs_occ/IMP/investigate/inv_1J-01_REPORT_fable.md` R1, R2, section 6 Stage 0 and Stage 1
Status:     DONE

## Why

The paper's five occupancy input files (2005, 2010, 2015, 2022, 2025) must be rebuilt before any energy re-run.
Two faults were confirmed by the manager (plan log (m)):
- **Day-type swap (2005, 2015).** `06CEN05GSS_alignment.py:883` and `16CEN15GSS_alignment.py:58` rename the 3-code
  `DVTDAY` (1 Weekday, 2 Saturday, 3 Sunday; `GSSMain_2015.sps:1412-1415`) to `DDAY`, and
  `*_ProfileMatcher.py:101-106` reads `DDAY` as a 7-code day of week (weekday = 2..6, weekend = 1, 7).
- **Night count (2005, 2010).** `06CEN05GSS_occToBEM.py:176-179` computes `occPre * (occDensity + 1) / hh_size`,
  where `occDensity` counts "who was with you" flags, which are 9 (not asked) during sleep in GSS 2005 and 2010.

The author ruled (log (n)): **occupancy = household members actually at home / household size, by the same method
in all five years.** Before any code changes, the manager needs a map of how each of the five pipelines builds the
occupancy column today, and where the new rule goes.

## Task

READ-ONLY apart from this file and scratch scripts in your session scratchpad. Cite `file:line` for every claim and
give the exact value read. `NOT FOUND` is an acceptable answer. Do not change any code or data file.

The five pipelines:
- 2005 `eSim/eSim_occ_utils/06CEN05GSS/`, 2010 `11CEN10GSS/`, 2015 `16CEN15GSS/`, 2022 `21CEN22GSS/`
  (alignment -> ProfileMatcher -> HH_aggregation -> occToBEM; 2010 and 2022 also have a `*_step0.py`);
- 2025 `eSim/eSim_occ_utils/25CEN22GSS_classification/` (`run_step1.py`, `run_step2.py`, `run_step3.py`).
  **Never modify** `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.

**Q1. How does each pipeline turn diaries into the hourly `Occupancy_Schedule`?** For each of the five, give the
chain of functions from per-person presence to the final column, with `file:line`, and the formula used. Say which
use the `occDensity` (social contact) count and which do not. For 2022 and 2025, say which script produced
`BEM_Setup/BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` (md5 34a1f8fa...) and `BEM_Setup/BEM_Schedules_2025.csv`
(md5 3e34561b...) if that can be traced.

**Q2. Does every household member have a presence grid?** The GSS has one diary respondent per household, aged 15
or over. In these pipelines, a census household's members are matched to GSS donors (ProfileMatcher). For each
pipeline: are all members, including children under 15, given a donor diary? If not, what does the code do with
them (`file:line`)? Measure on one output per cycle: the share of households where the number of persons with a
presence grid equals `HHSIZE` (use an intermediate output that carries per-person rows; name the file).

**Q3. Where does ruling A go?** Fable points at `_aggregate_household`, which already computes `occupancy_count`
and keeps only "at least one present" (`06CEN05GSS_HH_aggregation.py:230-233`). For each pipeline:
- the exact place where a per-hour count of members at home can be kept (a new column, no other change);
- the exact line in the converter that must use `count / HHSIZE` instead of `(occDensity + 1) / hh_size`;
- anything else that reads `occDensity` downstream (metabolic rate? `grep -n occDensity`) and would break.
Write the proposed change as a short diff sketch in this file; do NOT apply it.

**Q4. Day-type fix.** Confirm `DVTDAY` is 3-code in 2005 too (distinct values in
`0_Occupancy/Outputs_06CEN05GSS/alignment/Aligned_GSS_2005.csv`, counts of distinct respondents per value; also for
2015). Check 2010, 2022 and 2025 carry a real 7-code day (counts). Propose the smallest fix (a diff sketch) and list
every other place that reads `DDAY` in the 2005 and 2015 chains.

**Q5. Rebuild cost and inputs.** For each of the five, the command(s) that rebuild the BEM schedule file from its
inputs, the input files needed (paths, sizes), whether they exist locally, and whether the 25 % sample
(`sample25pct`) is drawn with a fixed seed (`file:line`). The rebuild will run on the Speed cluster with `sbatch`,
so list any hard-coded Windows paths that would break there.

## Rules

- Stream big CSVs (`csv` module or pandas `usecols` + `chunksize`); never load a whole multi-MB file into your
  context; print only summaries.
- Use `py`, not `python`. Run nothing on the cluster. Run no EnergyPlus. The local machine carries another heavy
  run: keep any scan to one process at a time.
- Write findings into this file as you go (state lives on disk). End with Status DONE and a `Next` line.

---

## Findings

Scratch scripts (re-runnable): `C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\7ac8b9b9-c77e-419c-ad41-0aaeaf7638da\scratchpad\q2_coverage.py`, `...\q4_dday.py`. Paths below are relative to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\` unless absolute. No code or data file was changed; only this doc and the two scratch scripts were written.

### Q1. Diaries -> hourly `Occupancy_Schedule`, per pipeline

All five converters share one formula: `estimated_count = occPre * (occDensity + 1)`, `Occupancy_Schedule = clip(estimated_count / hh_size, upper=1.0)`. All five USE `occDensity`.

- **2005**: `06CEN05GSS_alignment.py` -> `06CEN05GSS_ProfileMatcher.py` (`_find_best_match`, tiered) -> `06CEN05GSS_HH_aggregation.py::_aggregate_household` builds `occPre` (`:229-233`, binary "at least one present") and `occDensity` (`:235-237`, `dens_stack.sum(axis=0)`) per household per 5-min slot -> `06CEN05GSS_occToBEM.py::process_households`: hourly resample (`:169-170`, mean of `occPre`/`occDensity`), formula at `:176` (`estimated_count`) and `:179` (`occupancy_sched`), `hh_size` from `HHSIZE`/`Census_HHSIZE` (`:134-140`).
- **2010**: same chain, plus `11CEN10GSS_step0.py` (episode preprocessing) runs first, automatically, inside `11CEN10GSS_main.py::run_step0()` (`:81-103`, called unconditionally at `:342`). `_aggregate_household` in `11CEN10GSS_HH_aggregation.py`: `occPre` `:202-206`, `occDensity` `:208-210`. Converter `11CEN10GSS_occToBEM.py`: formula at `:159` / `:160`, `hh_size` at `:119-129`.
- **2015**: chain has an EXTRA step not in the other four: `16CEN15GSS_main.py` full pipeline (`:260-263`) is alignment -> ProfileMatcher -> **DTYPE_expansion** (`16CEN15GSS_DTYPE_expansion.py`, refines dwelling type only, does not touch occupancy columns) -> HH_aggregation -> occToBEM. `_aggregate_household` in `16CEN15GSS_HH_aggregation.py`: `occPre` `:228-232`, `occDensity` `:234-236`. Converter `16CEN15GSS_occToBEM.py`: formula at `:175` / `:178`.
- **2022 (five-pipeline / "classic" chain)**: `21CEN22GSS_step0.py` also runs automatically (`21CEN22GSS_main.py::run_step0()`, called unconditionally at `:197`) -> alignment -> ProfileMatcher -> `21CEN22GSS_HH_aggregation.py::_aggregate_household` (`occPre` `:167-175`, `occDensity` `:178`) -> `21CEN22GSS_occToBEM.py::process_households` (formula `:170`/`:171`). **This whole script carries a self-written deprecation banner** (`21CEN22GSS_occToBEM.py:1-25`, dated 2026-08-04, "🔴 DEPRECATED ... SUPERSEDED, DO NOT USE FOR NEW WORK"): it says the production `BEM_Setup/BEM_Schedules_2022.csv` (dated 2026-07-09) is actually built by a DIFFERENT script, `2J_docs_occ_nTemp/07_aug_to_bem.py::convert()` (its own `occ48 = df.groupby(keys)[HOM].mean()`, no `occDensity` used there), and this file's own output survives only as the frozen snapshot named in the task doc.
  - **Traced: `BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` (md5 `34a1f8fa4f5fa04a4e860c0271f366ab`, re-hashed and confirmed) was produced by the deprecated `21CEN22GSS_occToBEM.py`** (the `occDensity`-based formula), not by `07_aug_to_bem.py`. Its md5 matches `0_Occupancy/Outputs_21CEN22GSS/occToBEM/21CEN22GSS_BEM_Schedules_sample25pct.csv` per the prior Fable investigation (not re-hashed here, file is 103 MB; one scan at a time was already spent re-hashing the CLASSIC_BAK copy itself).
  - The current production `BEM_Schedules_2022.csv` (no CLASSIC_BAK suffix) is NOT one of the "five pipelines" this task is scoped to (it lives under `2J_docs_occ_nTemp/`, not `eSim/eSim_occ_utils/21CEN22GSS/`); its exact occupancy semantics (what `HOM`/`hom30_*` actually represent — single respondent diary, or an already-aggregated household fraction) were **not traced further** — out of the stated scope and would need a second pass through `05_census_linkage.py` (also outside the five pipelines).
- **2025**: `run_step1.py` (CVAE train/forecast, TensorFlow) -> `run_step2.py` (`run_assemble_household` -> `run_profile_matcher` [same tiered `MatchProfiler`] -> `run_postprocessing` [DTYPE refine] -> `run_household_aggregation`, calls `HouseholdAggregator.process_all` in `previous/eSim_dynamicML_mHead.py`, same `_aggregate_household` code: `occPre` `:2082-2093`, `occDensity` `:2095-2100`) -> `run_step3.py::run_bem_conversion` -> `BEMConverter.process_households` in the same `previous/eSim_dynamicML_mHead.py`, formula at `:2401` / `:2404`, `hh_size` at `:2365`.
  - **Traced and CONFIRMED by md5: `BEM_Setup/BEM_Schedules_2025.csv` (`3e34561bb96f2cdd0107ea5bdef1432e`) is byte-identical to `0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv`**, which is exactly `run_step3.py`'s declared output path (`OUTPUT_DIR/"BEM_Schedules_2025.csv"`, `OUTPUT_DIR` = `occ_config.OUTPUT_DIR` = `Outputs_CENSUS`, `run_step3.py:103-105,131`). So the 2025 file's producer is directly confirmed, not just inferred from file lineage.

### Q2. Presence grid coverage — census agents under 15 are dropped BEFORE any matching, in all five pipelines

All five pipelines run a `harmonize_agegrp()` in their alignment step that maps Census age code `<= 2` (StatCan PUMF: ages 0-14) to a sentinel `96` and then DROPS every row carrying it, before `ProfileMatcher`/`MatchProfiler` ever runs. So **no household member under 15 is ever matched to a GSS donor diary in any of the five years** — they are removed from the population, not assigned an adult's diary as a fallback.

- 2005: `06CEN05GSS_alignment.py:49` (`if x <= 2: return 96  # 0-14 -> Skip (children)`), drop at `:60`.
- 2010: `11CEN10GSS_alignment.py:288` (`if x <= 2: return 96`), drop at `:299`.
- 2015: `16CEN15GSS_alignment.py:394-395` (`if x <= 2: return 96  # 0-14 -> Skip`), drop at `:413`.
- 2022: `21CEN22GSS_alignment.py:320-321` (`if x <= 2: return 96`), drop at `:339`.
- 2025: `eSim_dynamicML_mHead_alignment.py:245` (`if x <= 2: return 96  # 0-14 -> Skip`), drop at `:256`. (This file is on the "never modify" list — read only, confirmed unmodified.)

`HHSIZE` itself is the untouched raw census household-size variable (only capped at 6/7+, e.g. `06CEN05GSS_alignment.py:142-161`), so it still counts children; the per-person rows do not.

**Measured** (share of households where count(distinct `PID`) == `HHSIZE`, streamed with `q2_coverage.py`, one file at a time):
- 2005, `Outputs_06CEN05GSS/ProfileMatching/06CEN05GSS_Matched_Keys_sample25pct.csv`: 28,455 households, 98.4% equal, 1.5% short, 0.1% over.
- 2010, `Outputs_11CEN10GSS/ProfileMatching/11CEN10GSS_Matched_Keys_sample25pct.csv`: 32,480 households, 64.0% equal, 35.4% short, 0.6% over.
- 2015, `Outputs_16CEN15GSS/ProfileMatching/16CEN15GSS_Matched_Keys_sample25pct.csv`: 31,163 households, 69.6% equal, 30.3% short, 0.1% over.
- 2022, `Outputs_21CEN22GSS/ProfileMatching/21CEN22GSS_Matched_Keys_sample25pct.csv`: 36,909 households, 64.1% equal, 35.3% short, 0.7% over.
- 2025, `0_Occupancy/Outputs_Aligned/Matched_Population_Keys.csv`: 23,882 households, 37.4% equal, 62.5% short, 0.2% over.

2005 is an outlier (98.4% vs 64-70% for 2010/2015/2022 and 37% for 2025) despite running the identical code path; not explained (see WHAT I DID NOT VERIFY). A small "over" tail (0.1-0.7%) exists in every file — not investigated.

### Q3. Where Ruling A goes

- **New per-hour count column (additive, one line, right after the existing count is thrown away):**
  - 2005: `06CEN05GSS_HH_aggregation.py:232` (`occupancy_count = presence_binary.sum(axis=0)`) -> add `hh_df['occCount'] = occupancy_count` immediately after; `:233` already reduces it to the binary `occPre` that ships today.
  - 2010: `11CEN10GSS_HH_aggregation.py:205` (count) / `:206` (binary).
  - 2015: `16CEN15GSS_HH_aggregation.py:231` (count) / `:232` (binary).
  - 2022: `21CEN22GSS_HH_aggregation.py:174` (count) / `:175` (binary).
  - 2025: `25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py:2090` (count) / `:2093` (binary) — inside `_aggregate_household`, the same function body as the other four (copy-pasted), confirmed by identical STEP B/C comments.
- **Converter line to change (`(occDensity+1)/hh_size` -> `occCount/HHSIZE`):**
  - 2005: `06CEN05GSS_occToBEM.py:176` (`estimated_count = ...`) and `:179` (`occupancy_sched = ...`) -> replace with `occupancy_sched = (hourly['occCount'] / hh_size).clip(upper=1.0)`, and add `'occCount': 'mean'` to the resample `.agg()` dict at `:169-170`.
  - 2010: `11CEN10GSS_occToBEM.py:159` / `:160`, resample dict `:153-154`.
  - 2015: `16CEN15GSS_occToBEM.py:175` / `:178`, resample dict `:168-169`.
  - 2022: `21CEN22GSS_occToBEM.py:170` / `:171`, resample dict `:164-165` (this file is DEPRECATED — see Q1 — so this edit only matters if the "classic" chain is kept as the five-pipeline path; the production `07_aug_to_bem.py` is untouched by this ruling and was not investigated further).
  - 2025: `25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py:2401` / `:2404`, resample dict `:2392-2395`.
- **Diff sketch (identical shape in all five converter files), example for 2005:**
  ```
  # 06CEN05GSS_HH_aggregation.py, inside _aggregate_household, after line 232:
  hh_df['occPre'] = (occupancy_count >= 1).astype(int)
  + hh_df['occCount'] = occupancy_count            # NEW: raw per-slot headcount, no other change

  # 06CEN05GSS_occToBEM.py, inside process_households:
  hourly = g_indexed.resample('60min').agg({
      'occPre': 'mean',
      'occDensity': 'mean',
  +   'occCount': 'mean',
      ...
  })
  - estimated_count = hourly['occPre'] * (hourly['occDensity'] + 1)
  - occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)
  + occupancy_sched = (hourly['occCount'] / hh_size).clip(upper=1.0)
  ```
  NOT applied — sketch only, per task rules.
- **Everything else that reads `occDensity` downstream:** grepped all of `eSim/` (`grep -rn occDensity`, glob `*.py`). It appears in exactly 9 files — the same 5 `*_HH_aggregation.py` (build it) and 5 `*_occToBEM.py` (consume it in the formula) minus one path collapsed (`previous/eSim_dynamicML_mHead.py` holds both roles for 2025) = 9 total. Every other hit inside those files is diagnostic/plotting only (`ghosts` sanity check, `interesting_ids` scatter selection, `fill_between`/`plot` calls for QA figures) — **no metabolic-rate or any other functional consumer of `occDensity` exists anywhere in `eSim/`.** Metabolic rate is computed separately from `occActivity`/watts maps, untouched by this ruling.

### Q4. Day-type

**Distinct `occID` per `DDAY` value** (streamed with `q4_dday.py`, one file at a time; re-derived independently, matches the prior Fable investigation's numbers exactly for 2005/2015):
- 2005 (`Outputs_06CEN05GSS/alignment/Aligned_GSS_2005.csv`): DDAY=1: 9,539; DDAY=2: 1,915; DDAY=3: 2,065. **3 codes only** — confirms `DVTDAY` is 3-code (StatCan "type of day": 1 Weekday, 2 Saturday, 3 Sunday).
- 2015 (`Outputs_16CEN15GSS/alignment/Aligned_GSS_2015.csv`): DDAY=1: 10,750; DDAY=2: 2,181; DDAY=3: 2,309. Same 3-code pattern.
- 2010 (`Outputs_11CEN10GSS/alignment/Aligned_GSS_2010.csv`): 7 codes, 1,497-1,798 each (roughly 1/7 of ~11,748 total) — real 7-code day of week.
- 2022 (`Outputs_21CEN22GSS/alignment/Aligned_GSS_2022.csv`): 7 codes, 1,403-1,691 each — real 7-code day of week.
- 2025's source diaries (`0_Occupancy/Outputs_Aligned/Aligned_GSS_2022.csv`, the file the 25CEN22GSS_classification chain actually reads): 7 codes, 855-1,054 each — also a real 7-code day of week (2025 reuses 2022's GSS diaries, confirmed independently of the 2022 five-pipeline copy).

**Root cause (unchanged from the prior investigation, re-confirmed here):** `06CEN05GSS_alignment.py:883` and `16CEN15GSS_alignment.py:58` both do `'DVTDAY': 'DDAY'` — a straight rename, no code remap — and `*_ProfileMatcher.py:101-106` (both years, identical: `catalog_wd` = `DDAY.isin([2,3,4,5,6])`, `catalog_we` = `DDAY.isin([1,7])`) then reads the renamed column as if it were the real 7-code day of week. Code 1 (true Weekday) lands in the Weekend catalogue; codes 2,3 (Saturday, Sunday) land in the Weekday catalogue.

**Every other place `DDAY` is read in the 2005 and 2015 chains** (grepped both directories for `DDAY`): only the rename (`alignment.py`) and the two `isin(...)` catalogue splits + the `dday_col="DDAY"` constructor arg (`ProfileMatcher.py:43-44/101-106/605` for 2005, `:44/101-106/604` for 2015). `HH_aggregation.py` and `occToBEM.py` never reference `DDAY` — they only see the `Day_Type` string ("Weekday"/"Weekend") that `ProfileMatcher` already assigned, so the smallest fix is entirely upstream of them.

**Smallest fix (diff sketch, not applied):** replace the raw rename with a value remap, right where `RENAME_MAP_05`/`RENAME_MAP_15` are defined (`06CEN05GSS_alignment.py:880-897`, `16CEN15GSS_alignment.py:47-59`) or immediately after the GSS file is loaded and renamed:
```
DVTDAY_TO_DDAY = {1: 4, 2: 7, 3: 1}   # 1=Weekday -> mid-week code(4); 2=Saturday -> 7; 3=Sunday -> 1
df_gss['DDAY'] = df_gss['DDAY'].map(DVTDAY_TO_DDAY)   # after the RENAME_MAP_0X rename, before ProfileMatcher
```
This keeps the rest of the chain (which expects a 7-code `DDAY`) unchanged. Fable's report already flagged that a post-hoc label swap on the finished CSVs is not guaranteed identical to a full regeneration (`06CEN05GSS_HH_aggregation.py:396-401` behaves asymmetrically between day types) — not re-verified here, carried over as a caveat.

### Q5. Rebuild cost and inputs

**Commands** (none run; read from each `*_main.py` / `run_step*.py`):
- 2005: `py 06CEN05GSS_main.py --sample 25 --run 5` (full pipeline: alignment, matching, HH-aggregation, BEM; `06CEN05GSS_main.py:174-207,328-368`).
- 2010: `py 11CEN10GSS_main.py --sample 25 --run 5` — Step 0 (episode preprocessing) runs automatically first regardless of `--run` (`11CEN10GSS_main.py:342`).
- 2015: `py 16CEN15GSS_main.py --sample 25 --run <full-pipeline option>` — the menu has an extra DTYPE-Expansion step (`16CEN15GSS_main.py:260-263`), so the "run 5" full-pipeline shortcut used for the other years maps to a different option number here; exact numeric flag not re-derived, use the interactive menu's "Run Full Pipeline" entry.
- 2022: `py 21CEN22GSS_main.py --sample 25 --run 5` — Step 0 also runs automatically first (`21CEN22GSS_main.py:197`).
- 2025: no single CLI command — edit the `__main__` boolean flags and run three files in order: `py run_step1.py` (CVAE; `RUN_TRAINING`/`RUN_TESTING`/`RUN_FORECASTING`/`RUN_VISUAL_VALIDATION`, all `True` by default, `run_step1.py` tail), `py run_step2.py` (six sub-steps, all flags `False` by default — must be flipped `True` in order, `run_step2.py:325-347`), `py run_step3.py` (`RUN_BEM_CONVERSION=True` by default, `run_step3.py:158-161`). A trained CVAE already exists on disk (`0_Occupancy/saved_models_cvae/cvae_encoder.keras`, `cvae_decoder.keras`, both dated Apr 8), so `RUN_TRAINING`/`RUN_TESTING` could be set `False` to skip retraining and reuse it — cuts the only ML-training cost in all five pipelines; not verified that the saved model matches the current alignment code.

**Fixed seed for `sample25pct` — yes, seed 42, in all four census-flow pipelines** (2025 has no equivalent sampling step — see below):
- 2005: `06CEN05GSS_ProfileMatcher.py:522` (`random_state: int = 42`), applied at `:546` (`np.random.seed(random_state)`).
- 2010: `11CEN10GSS_ProfileMatcher.py:431` / `:455`.
- 2015: `16CEN15GSS_ProfileMatcher.py:521` / `:545`.
- 2022: `21CEN22GSS_ProfileMatcher.py:333` / `:340`.
- 2025: no `sample25pct` step at all — `run_step2.py`/`run_step3.py` take no `sample_pct` argument; `BEM_Schedules_2025.csv` covers the full forecasted population (23,882 households). `05_census_linkage.py` (a DIFFERENT, non-five-pipeline script) reads the *2022* `sample25pct` file as one of its own inputs and separately seeds `np.random.seed(42)` at `:142`, but that is not part of the 2025 chain this task traces.

**Input files, sizes, local existence** (all confirmed present, `ls -la`):
- Raw GSS: `0_Occupancy/DataSources_GSS/Main_files/GSSMain_2005.sas7bdat` (321 MB), `GSSMain_2010.DAT` (270 MB) + `GSSMain_2010_syntax.SPS`, `GSSMain_2015.txt` (102 MB) + `GSSMain_2015.sps`, `GSSMain_2022.sas7bdat` (40 MB). 2025 reuses the 2022 GSS diaries (no separate raw file).
- GSS episode data: raw `DataSources_GSS/Episode_files/GSS_20XX_episode/...` present for all four years (2005 `.SAV` 215+27 MB, 2010 `.DAT` 22 MB, 2015 `GSS29PUMFE.txt` 1.39 GB, 2022 `.sas7bdat` 471 MB); PRE-PROCESSED versions already cached at `0_Occupancy/Outputs_GSS/out0{5,10,15,22}EP_ACT_PRE_coPRE.csv` (all four present, 14.7-19.8 MB each) — a rebuild can reuse these instead of re-parsing the huge raw files, if the alignment scripts are pointed at them (not verified whether the scripts do this by default or always reprocess raw).
- Census: `Outputs_CENSUS/cen06_filtered.csv` / `cen11_filtered.csv` / `cen16_filtered.csv` / `cen21_filtered.csv` all present (24-38 MB each); the household-linked intermediates `2006_LINKED.csv` and `2016_LINKED.csv` exist under `Outputs_CENSUS/`, and `2011_LINKED.csv` / `2021_LINKED.csv` exist at the paths each script actually expects (`DataSources_CENSUS/census_2011/2011_LINKED.csv`, `Outputs_21CEN22GSS/alignment/2021_LINKED.csv`) — all four are also regenerated automatically by `assemble_households()` inside `alignment.main()` on every run, so their absence would not block a rebuild.
- 2025-only: CVAE inputs under `0_Occupancy/DataSources_CENSUS/` (not separately enumerated here) and the saved model pair above.

**Hard-coded Windows paths that would break on Speed:** only one, `eSim/eSim_occ_utils/occ_config.py:23` (`_DEFAULT_BASE_DIR = Path(r'C:\Users\o_iseri\...')`), and it is inside a `platform.system()=='Windows'` branch (`:20-25`) so it is inert on Linux. **But its Linux fallback (`:24-25`, `Path.home()/'GSSCanada'/'Occupancy'`) does not point at this repo's `0_Occupancy/` at all**, and `occ_config.py:39-40` silently `mkdir(parents=True, exist_ok=True)`s that wrong location with no error — so an `sbatch` job MUST set the `GSS_BASE_DIR` environment variable (`occ_config.py:29`) to the mirrored `0_Occupancy` path, or it will silently write into an empty tree instead of failing loudly. No other hard-coded Windows path exists anywhere in the five pipeline directories or `occ_config.py` (`grep -rn "C:\\Users\|C:/Users"` across all five directories — one hit total, the line above).

## Verified

- `BEM_Setup/BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` md5 = `34a1f8fa4f5fa04a4e860c0271f366ab` (re-hashed locally, matches task doc's quoted `34a1f8fa...`).
- `BEM_Setup/BEM_Schedules_2025.csv` md5 = `3e34561bb96f2cdd0107ea5bdef1432e`, identical to `0_Occupancy/Outputs_CENSUS/BEM_Schedules_2025.csv` (re-hashed both, byte-identical; matches task doc's quoted `3e34561b...`).
- Formula `estimated_count = occPre*(occDensity+1)`, `occupancy_sched = clip(estimated_count/hh_size, upper=1.0)` read verbatim (not paraphrased) in all five converter files at the line numbers cited in Q1/Q3.
- `harmonize_agegrp()`'s "0-14 -> Skip" drop read verbatim in all five alignment files at the line numbers cited in Q2.
- Household person-count-vs-HHSIZE shares (Q2) computed by streaming the actual `*_Matched_Keys_sample25pct.csv` / `Matched_Population_Keys.csv` files, chunksize 200,000 rows, one file at a time.
- `DDAY` distinct-respondent counts (Q4) computed by streaming the actual `Aligned_GSS_20XX.csv` files, chunksize 300,000 rows, one file at a time; 2005 and 2015 numbers match the prior (Fable) investigation exactly, giving independent confirmation.
- File existence/sizes in Q5 read directly via `ls -la` / `find`, not inferred.

## Decisions

- Read `07_aug_to_bem.py` (the production 2022/2030 converter, not one of the five pipelines) only far enough to answer Q1's specific traceability question for the CLASSIC_BAK file; did not trace its `HOM`/`hom30_*` semantics or the upstream `05_census_linkage.py` build, since both are outside the six directories the task scopes Q1-Q5 to. Flagged as unverified below rather than guessed at.
- For 2015's exact `--run` menu number (Q5), did not execute the script or grep every menu-print line to resolve the integer, since running anything was disallowed and the number is cosmetic (the step order and full-pipeline step list are already fully documented). Recommended the interactive "Run Full Pipeline" menu entry instead of guessing a number.
- Did not attempt to explain 2005's Q2 outlier (98.4% vs 64-70%/37% elsewhere) beyond noting it runs the identical code path; a root cause would need reading the 2006 Census PUMF documentation, which is not on disk (see below).

## Next

Hand this doc to the manager for Ruling A/B sign-off (plan §7 log (n) already rules occupancy = present/HHSIZE; this doc gives the five exact insertion points). Suggested next employee task: apply the Q3 diff (new `occCount` column + converter line swap) to all five pipelines in one small, reviewable edit, gated on a rebuild-and-recheck of the three-check gate from the prior investigation (day-type direction, night presence >=0.70, md5 change) — do not fold in the Q4 day-type fix in the same commit (separate bug, separate diff, per Fable's report R1 vs R2).

## WHAT I DID NOT VERIFY

- Why 2005's Q2 coverage (98.4% households with persons==HHSIZE) is so much higher than 2010/2015/2022 (64-70%) and 2025 (37%) despite identical drop-code logic. Not the 2006 Census PUMF age-universe documentation (not on disk locally) vs. a genuine household-composition difference in the sampled 25% pool.
- Whether the alignment scripts, when re-run, actually read the cached `Outputs_GSS/out0{5,10,15,22}EP_ACT_PRE_coPRE.csv` files or always reprocess the much larger raw episode files (`.SAV`/`.txt`/`.sas7bdat`) — this changes the real rebuild wall-clock materially and was not traced function-by-function.
- The exact `--run` integer for 2015's full-pipeline shortcut (menu has one extra step vs the other three years).
- `07_aug_to_bem.py`'s `HOM`/`hom30_*` semantics and whether the current production `BEM_Schedules_2022.csv` (not CLASSIC_BAK) already implements something equivalent to Ruling A or not — out of this task's stated scope (it is not one of the five pipelines), but relevant to whether Ruling A, once applied to the "classic" chain, would also need porting there for the paper's actual production 2022 numbers.
- Whether the trained CVAE (`saved_models_cvae/`) is still compatible with the current alignment code if `RUN_TRAINING` is skipped for a 2025 rebuild.
- Nothing was run on the cluster; nothing in `2J_docs_occ_nTemp/` or `3J_docs_occ_nTemp/` beyond the one traceability check in Q1.
- The GSS 2005 codebook for `DVTDAY`/`AGEGR10` age-band definitions is not on disk; all age/day-code claims rest on the code comments and the 2010/2015 `.sps`/`.SPS` syntax files plus the measured value distributions.

Status: DONE
