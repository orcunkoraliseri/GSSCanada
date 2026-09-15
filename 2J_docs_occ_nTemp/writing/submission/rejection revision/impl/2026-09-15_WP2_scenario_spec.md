# WP2 — 2030 work-from-home scenarios: design spec (manager)

Plan: `../00_REVISION_PLAN.md` §3 WP2. Builds on D1 (`2026-09-15_WP1_step2_retargeting_spec.md` §3) and its
implementation T20 (`2026-09-15_T20_wp1_d1_2030_build.md`, `T20_scripts/t20_d1.py`).
Status: DESIGN FIXED 2026-09-15, before any scenario data is seen. Author delegated design choices
(plan log n).

## 1. What the existing code computes (read by manager)
- `06_forecast_rake.py:100-123`: `obs[yr,s,t]` = **unweighted** mean `hom30` of real respondents
  (`IS_SYNTHETIC==0`) per cycle and day stratum.
- `:150-161`: per slot, a straight line through 2005/2010/2015 gives `pre_slope[s,t]` (per year) and a
  trend; the comment at `:130` names the COVID jump `jump[s,t] = obs[2022,s,t] − trend[s,t](2022)`; the
  2030 target is `obs_2022 + 8 × pre_slope` (= trend 2030 + jump: the jump persists fully).

## 2. One family, one parameter
Every scenario uses the same stock, the same slopes and the same D1 rake. Only the share of the COVID
jump that survives to 2030, `λ`, changes:

    target_λ[s,t] = clamp( stock_2022[s,t] + 8 × pre_slope[s,t] − (1 − λ) × jump[s,t] , 0, 1 )

- **S-Persist, λ = 1:** identical to T20 `main` (the jump stays).
- **S-Partial, λ = 0.5:** half the jump is gone by 2030.
- **S-Revert, λ = 0:** the jump is gone. 2030 sits on the pre-COVID trend, expressed as a shift on the stock.
- **S-Grow:** not built. It needs an external number (deep-research prompt, WP12.3c). No number, no scenario.

`stock_2022` = rebuilt Arm N stock (T18), so the anchor defect (D-a) stays fixed for every scenario.
`jump` and `pre_slope` come from exactly the `06_forecast_rake.py:100-161` computation on the full
all-cycle `augmented_diaries.csv`, imported or copied with a line citation.

**Manager decision: unstandardized jump (primary).** The plan text said "demographically standardized 2015
level". The slope is unstandardized in the published code, and a standardized jump with an unstandardized
slope would break the nesting (λ = 1 would no longer equal T20 `main`). So the primary jump is the code's
own. As a reported sensitivity only, the build also prints a standardized jump: all four cycles' real
respondents reweighted to the rebuilt stock's AGEGRP × SEX × LFTAG counts (collapse LFTAG, then SEX, for
empty cells; report collapsed cells), with the line refitted. **If the national weekday mean of the
standardized jump differs from the primary by more than 1.0 pp, the manager adds S-Revert-std as an extra
scenario.** Fixed now.

## 3. Acceptance (each scenario)
- **SC0 nesting.** The λ = 1 build equals T20 `main` `BEM_Schedules_2030.csv` occupancy columns exactly
  (share of equal cells = 1.0), or the scenario builds are not used.
- **SC1 intended step.** Household weekday at-home change vs Arm N 2022 is within 0.5 pp of the mean over
  weekday slots of `target_λ − stock_2022`; Sat/Sun and per archetype reported.
- **SC2 order.** Weekday household at-home: Revert < Partial < Persist (strict). Reported per archetype.
- **SC3 jump sanity (reported, not banded).** The national weekday mean of `jump`, and the at-home change
  2022→2030 under S-Revert. S-Revert is expected to be negative if the jump exceeds the 8-year trend.
- **SC4 integrity.** Validator 28/28; same rows and household IDs as Arm N 2022; Arm N and T20 outputs
  md5 unchanged.
- **SC5 rake.** Achieved vs target per stratum × slot; max abs diff reported, flag > 0.5 pp.
- After EnergyPlus (T21-style runs, 1,200 Step-8 runs per scenario): plan WP2 sanity "S-Revert 2022→2030
  shape deltas of opposite sign to S-Persist" is **reported, not required**. It holds only if S-Revert's
  at-home change has the opposite sign, which SC3 shows first.

## 4. Order
T20 collector passes N0–N2 → T26 (scenario schedule builds S-Partial, S-Revert, λ = 1 nesting check) →
Step-8 runs for the two new scenarios, on the same 1,200 households as T21's 2030 runs.

## 5. Addendum (manager, 2026-09-15, after T26): S-Revert-std, triggered by the §2 rule
T26 measured the standardized weekday jump at 7.67 pp against 4.73 pp primary (+2.94 pp, over the 1.0 pp trigger
fixed in §2 before data). So S-Revert-std is built. Definition, the λ = 0 member of the standardized family:

    target_std[s,t] = clamp( stock_2022[s,t] + 8 × pre_slope_std[s,t] − jump_std[s,t] , 0, 1 )

`pre_slope_std` and `jump_std` are exactly the per-slot arrays of `T26_scripts/t26_scenario.py:146-183`
(`compute_standardized_jump`: real respondents of all four cycles reweighted to the rebuilt stock's
AGEGRP × SEX × LFTAG counts, line refitted). Same stock, same D1 rake, same validator. Only S-Revert gets a
standardized twin: for λ = 1 the standardized family breaks nesting (§2), and S-Partial-std adds no new question.
Acceptance: SC1 (within 0.5 pp of the weekday mean of `target_std − stock_2022`), SC4 (0 FAIL, rows and IDs equal,
upstream md5 unchanged), SC5 (flag > 0.5 pp), and two reported numbers, not banded: the weekday at-home change
2022→2030, and its difference from S-Revert (expected below S-Revert because the standardized jump is larger;
the slope also changes, so the sign is reported, not required). A regression guard: the same code with
`--jump-basis primary` must reproduce T26's λ = 0 output exactly (share of equal cells = 1.0), which is the
check that it can fail. Energy runs: 1,200 Step-8 runs of 2030 on T21's households (T29 addendum).
