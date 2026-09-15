# WP1 step 2 — 2030 re-targeting spec (manager design)

Plan: `../00_REVISION_PLAN.md` §3 WP1, §10 Wave 2. Facts: `2026-09-15_T11_wp1_chain_facts.md`, `2026-09-15_T01_wp1_athome_gap.md`.
Status: DESIGN — stage A (diagnostic, T12) must return before stage B (build) is briefed.

## 1. What the code actually does (read by manager, 2026-09-15)

- 2022 schedules: `07_aug_to_bem.py:204` reads the linked stock `21CEN22GSS_aug_Full_Aggregated_excl.csv`
  (285,367 persons). **Each person keeps the diary they were linked with.**
- 2030 schedules: `assemble_2030()` (`07_aug_to_bem.py:182-193`) keeps the same stock persons but
  **overwrites every person's `act30`/`hom30` with a random diary from the 2030 pool, matched on day
  type (`DDAY_STRATA`) only** (`:188-192`). Age, work status, household size and dwelling play no part
  in the draw.
- The 2030 pool is raked to `obs_2022 + 8 × pre-COVID slope` (`06_forecast_rake.py:138-165`), with
  `obs_2022` from real 2022 respondents in `augmented_diaries.csv` (person level, 76.93 % weekday).
- Household schedule value = mean of members' `hom30`, slot pairs averaged to hours, +4 h roll
  (`07_aug_to_bem.py:97,103,109`). The mean is linear, so independent random draws give a household
  mean equal to the pool's person mean in expectation. **78.44 % pool → 78.5 % schedules is exactly
  what this predicts.** The +8.3 pp gap is therefore "2022 stock diaries average ~70 %" vs "2030 pool
  averages ~78 %", not a slope effect.
- The stock carries `CYCLE_YEAR`, `IS_SYNTHETIC`, `WGHT_PER`. If stock persons were linked to diaries
  from 2005/2010/2015 cycles or to synthetic diaries, that alone could explain a 2022 level of ~70 %.

## 2. Two defects, not one

- **D-a Anchor.** The 2030 target is anchored to a population (real 2022 respondents) that is not the
  population in the 2022 schedules.
- **D-b Draw.** The 2030 draw breaks the person–diary link that the 2022 file keeps. Even with a
  correct anchor, 2022→2030 differences would mix the forecast change with a composition change
  (who gets which diary). A reviewer who reads the paired-panel claim will expect the same people
  with changed behaviour.

## 3. Chosen design (D1, delta on the stock)

2030 = the **same stock persons with their own 2022 stock diaries**, raked slot by slot to

    target_2030[s,t] = stock_2022[s,t] + 8 × pre_slope[s,t]        clamp [0,1]

- `stock_2022[s,t]` = person-level `hom30` mean of the stock file itself, same weighting the 2022
  schedule build implies (unweighted, `07_aug_to_bem.py:97` uses a plain mean).
- `pre_slope[s,t]` = unchanged, from `06_forecast_rake.py:150-155` (real 2005/2010/2015 respondents).
- Rake = the existing binary-flip rake (`06_forecast_rake.py`, seed 42, run-boundary preference,
  `--joint` keeps `act30` consistent), applied to stock rows instead of the synthetic 2030 pool.
- Then `complete_day_types` + `convert` exactly as for 2022.

Rejected: **D2** keep the random draw and only re-anchor. Fixes D-a, leaves D-b, and the composition
change still enters every 2022→2030 delta.

Scenarios (WP2) come free: S-Revert/S-Partial are different `target_2030` arrays on the same stock.

## 4. Acceptance tests (each must be seen failing on the current build first)

- **N0 null forecast.** With `pre_slope = 0`, the 2030 build must equal the 2022 file: household
  weekday and weekend at-home means within 0.05 pp, national and per archetype. The **current**
  machinery run with a zero-change pool must be shown to fail N0 (expected ~+6 pp) — stage A does this.
- **N1 intended step.** With real slopes, 2022→2030 weekday household at-home change within 0.5 pp of
  the mean of `8 × pre_slope` over weekday slots (≈ +1.5 pp; stage A re-measures it).
- **N2 integrity.** `07_bemIntegrationGSS_val.py --year 2030` 28/28; row count 6,934,320; 144,465 HH.
- **N3 no leakage.** 2022 schedule file md5 unchanged by the build.

## 5. Decision rule for stage A results (fixed before the data is seen)

- If stock person-level weekday `hom30` is 69–72 % and the zero-change pool reproduces ~77 % through
  the current draw → §1 is confirmed → brief stage B with D1.
- If the stock level is ~77 % (so the 70 % arises inside `complete_day_types`/`convert`) → D1 is not
  enough; manager re-designs before any build.
- If the stock is mostly non-2022 `CYCLE_YEAR` diaries → stop and tell the author before stage B:
  the 2022 schedules themselves would then not be 2022 behaviour, which is a bigger paper question.

## 5b. Stage A outcome and author decision (2026-09-15)

- Branch 3 fired (77.7 % of stock persons carry a 2005/2010/2015 diary). Author chose **option (a):
  rebuild the 2022 stock from 2022-cycle diaries only**, then D1 for 2030 on the rebuilt stock.
- Consequences: `stock_2022` in §3 means the **rebuilt** stock; N3 is replaced by "the old 2022 file is
  untouched and the new one is written under `T13_out/`"; both 2022 and 2030 halves are re-run.
- Added acceptance test **N4 linkage quality:** linkage tier shares and match counts, old build vs 2022-only
  build, reported per archetype (reported, not banded; a large rise in fallback tiers goes to the author).
- **Author instruction (2026-09-15): "fix it" — mitigate the smaller-pool risk inside the design, not just
  report it.** Rules for the build, fixed before any data is seen:
  1. Donor pool = **all** 2022-cycle diaries, real and synthetic (the Step-4 augmentation exists to enlarge
     exactly this pool). Older cycles are never used as donors.
  2. If a census person has no 2022 donor at the strictest tier, relax matching keys **within 2022 only**,
     least important key first, in the existing tier order (T13 Q2 gives the order).
  3. Donor reuse is allowed, but cap how many times one diary is reused per region-tier cell if the
     linkage has such a control; report the max and 99th-percentile reuse count old vs new.
  4. N4 compares old vs new for: share per tier, reuse counts, and the weekday at-home level of **real**
     2022 respondents vs the rebuilt stock (the rebuilt stock should now sit near 74.6-76.9 %, not 69.8 %).
  5. If the strict-tier share falls by more than 10 points, manager tests one more lever (e.g. drop the
     weakest key globally) before any Step-8 run, and records both builds.

## 6. Stage B (T13 reading first, then build)

Build script in `T13_scripts/` (no edits to pipeline scripts; new outputs under `T13_out/`), run on
Speed, N0–N3, then 1,200 Step-8 + 2,400 Step-9 re-runs of the 2030 half (plan WP1 step 4).
