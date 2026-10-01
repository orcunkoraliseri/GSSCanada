# 5J Step 7 design ruling (manager, 2026-10-01 04:21 EDT, under the author's go-ahead; author asleep)

Replaces every DRAFT item of `Step7_docs/5thJ_07_speedDistrict.md` 7A-7D. Facts: `impl/2026-10-01_step7_facts.md`. Step 6 is
closed (S passes G5J.3 in 31/32, 31/32, 26/28 test cells), so the district spread is reported as a validated-model spread, with
Step 6's limits (absolute load weak on new buildings; seed dependence; Spain only here).

## R7-1 The district: archetype twins of 100 real Madrid buildings
* Source: ES-MAD-BERRUGUETE (4J Step 10 Madrid stock, 1,151 eligible buildings, 11,976 dwellings; Catastro/OpenUBEM payloads
  `layouts/{relation,way}/<id>.json`). Sample **100 buildings**, stratified by class in proportion to the 1,151 (at least 5 per
  class), seed 20261001, list written and md5-sealed before any surrogate or EnergyPlus run (val 3.2).
* Each real building becomes its **archetype twin**: the 5J builder (`tools/5thJ_idf_mz.py`, unchanged) fed with the building's
  TABULA code (OpenUBEM `archetype_id` minus the trailing `.001`; every one of the 24 Spanish codes exists in the 5J campaign),
  infiltration and orientation sampled exactly as the campaign sampled them (they are unknown for real buildings), Madrid 2010
  EPW. Geometry, dwelling count and envelope come from TABULA, as in training. What is real: the mix of classes and periods.
* Why not the real geometry: the 4J no-core runs are heating-only with a fixed 3 W/m2 gain and a different interior model, so
  surrogate error would be mixed with builder error and cooling/equipment could not be checked (3J/4J review issue 4). The
  paper states: "a district of archetype twins of real Madrid buildings". The real dwelling count of each building is listed
  next to its twin's (size gap reported, not corrected).
* In range / out of range: a twin is "out of range" when any of its static inputs is clipped (rules AMENDMENT 2), e.g. AB.06
  twins carry the TABULA V_C inconsistency of es_B40; and "seen" when its code was a development building of Step 5. Both are
  counted and scored separately in R7-4.

## R7-2 Households
* Pool = the 60 campaign Spanish households (the model saw 40 in training) + **500 new Spanish households** drawn from the
  9,541 by the same weighted rule and seed scheme as households-v2 (seed 6, size strata as the population), built with the
  same trigger (`5thJ_step9_trigger_act2.py --hids`) and `hh_build.py`, on Speed. A 10-household pilot first (time and disk
  per household measured); if 500 does not fit 4 CPU-h, take the largest of 300 / 200 that fits, stated.
* A draw gives every dwelling of every twin one household, sampled with replacement by weight from the 560, each dwelling
  independently (seeded per draw). Households new to the model are flagged.

## R7-3 Draws and the surrogate
* The pinned S3 (md5 78271da9...) predicts every dwelling of the district for each draw; district hourly demand per draw = sum
  over dwellings (heating, cooling, equipment, total electricity).
* Number of draws: **measured, not assumed**. A 10-draw pilot on one A100 slice gives seconds per dwelling-year; N = the
  largest of 1,000 / 500 / 200 that fits 24 GPU-hours on at most 4 slices (the spec's 100,000 is not affordable at ~0.1 s per
  dwelling-year for ~1,000 dwellings; stated).
* Reported (`outputs_step7/district_spread.csv`): median and 90 % interval of annual and of peak-hour district demand per end
  use; the running median and interval width against the number of draws (how many draws until the interval settles;
  He 2015 question); same for the subset of dwellings in range.

## R7-4 The EnergyPlus check
* **20 draws** chosen by a recorded seed before any surrogate output exists (val 3.2), every twin, run through EnergyPlus with
  the 5J builder and campaign wrapper (`sbatch` arrays, at most 30 CPUs; ~2,000 runs, ~1 s per dwelling, ~6 CPU-h).
  Integrity as G5J.1 (complete, 8,760 h per flat, not cut short) before any comparison.
* Reported (`outputs_step7/district_check.csv`): per dwelling and per draw, S vs EnergyPlus CV(RMSE) and NMBE per end use; the
  district total per draw (annual and peak hour) S vs EnergyPlus; and whether the 20-draw spread (max - min of the district
  annual total) is reproduced by S; each split by in range / out of range and seen / new code and seen / new household.
  Reported, not gated.

## R7-5 Speed (G5J.7, reported)
* From job clock lines on the same node type: EnergyPlus wall seconds per dwelling-year (median over the R7-4 runs, one CPU,
  build + run + extract) against S per dwelling-year batched on one A100 slice and on one CPU core (load and write included).
  `outputs_step7/speed.md`.

## Order (employee tasks)
A. `Step7_docs/impl/2026-10-01_wp5_district_TASK.md`: sample + twins + sealed lists, household pilot + build, draw seeds
   sealed, surrogate pilot (timing) -> N fixed by R7-3. B. (after A is verified) full draws, EnergyPlus check, speed, outputs.
