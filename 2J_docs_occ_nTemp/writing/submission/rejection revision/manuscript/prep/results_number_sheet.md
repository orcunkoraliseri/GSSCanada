# Results number sheet (T79)

Built 2026-09-21 by a reading-only employee task (`impl/2026-09-21_T79_wp10_results_number_sheet.md`).
Every value below was read directly from an accepted output file (local copy or a direct cluster
read/`scp` of a file under 2 MB into `impl/T79_in/`); nothing here was computed by this task. Grouped
by the new Results order (plan WP10 Structure item 3, R1-R9). A "quotable number" here means a
stock-level or headline quantity a Results sentence would cite, not every row of the underlying
per-cell CSV -- the full per-cell breakdown is always in the cited source file.

Binding restrictions in force on every row (see task doc for full text):
- **Item 40 / (da):** absolute per-dwelling kWh only for SingleD and for equipment/lighting meters;
  every other meter's per-dwelling figure is `NOT_EVALUABLE`.
- **Item 30 / (cd) / (dh):** cross-scenario comparisons only on the 1,198 common households.
- **(cf):** claim the designed 2030 SHIFT, never the absolute LEVEL of the at-home share.
- **(cg)-(cs):** a 2022->2030 change is a "change" only if its own interval excludes zero. Rows
  marked `NOT_EVALUABLE` because the interval contains zero are never described as a change.
- **Item 39 / (db):** midday-share interval must be the cluster-aware one (wider); never the retired
  "1.0-3.3% narrower" figure.
- **Item 29:** no target-attainment claim from gate P2 (not used by any row below).
- **T04 / R3-7:** "chosen among four passing candidates," never "the only one that passed."
- **A5:** corrected validator's 48/48 is the reported number; original script's 12/48 is a
  seen-failing control only.
- **No peak or ramp CI exists (T71/T68):** always reported as "no interval available."

---

## R1 -- Occupancy change (2015/2022/2030, at-home by hour)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| At-home fraction, Weekday Hour=12, 2022 baseline (stock, 144,465 households) | 0.478204 | fraction (0-1) | none exists in source | `T76/logs/t76_run_meta.json` (`seen_working_control.2022_baseline`); full 24-hour series in `T76/out/figures/fig01_athome_by_hour.csv` (`series=2022_baseline`) | `seen_working_control` block; CSV rows `series=2022_baseline,day_type=Weekday` | (do), 3rd T76 entry, 2026-09-21 | Point value only, `no_ci_in_source=true`. Source = `T18c/nbf` frozen 2022 stock schedule, the same file T20/T26 were built from. | Figure 1 (WP11 numbering) |
| At-home fraction, Weekday Hour=12, 2030 main/persist (real OLS trend projected forward) | 0.501469 | fraction (0-1) | none | same files, `series=2030_main_persist` | same | (do) | Point value only. "main" = real trend; nesting-confirmed identical to lambda=1.0. | Figure 1 |
| At-home fraction, Weekday Hour=12, 2030 null (no-forecast-change control) | 0.478204 | fraction (0-1) | none | same files, `series=2030_null` | same | (do) | Reproduces 2022 baseline exactly -- confirms T20's own N0 acceptance check (cells 100% equal). | Figure 1 |
| At-home fraction, Weekday Hour=12, 2030 S-Partial (lambda=0.5, half the pandemic jump persists) | 0.462105 | fraction (0-1) | none | same files, `series=2030_lambda_0.5_partial` | same | (do) | Point value only. | Figure 1 |
| At-home fraction, Weekday Hour=12, 2030 S-None (lambda=0.0, pandemic jump fully reverts) | 0.422563 | fraction (0-1) | none | same files, `series=2030_lambda_0.0_revert` | same | (do) | Point value only. | Figure 1 |
| Full 24-hour x 2-day-type series for all five plotted scenarios | -- | fraction (0-1) | none | `T76/out/figures/fig01_athome_by_hour.csv` (13,959 bytes, scp'd to `impl/T79_in/fig01_athome_by_hour.csv`) | whole file, 6 series x 2 day types x 24 hours | (do) | Row-count control: all six source files read exactly 6,934,320 rows each; nesting control confirms lambda=1.0 == main in all 48 cells. No 2015 or pre-2022 at-home-by-hour series exists anywhere in this rebuild -- only the single 2022 baseline plus five 2030 variants. | Figure 1 |
| 2015 and earlier at-home-by-hour data | NOT VERIFIED | -- | -- | none found in T70-T79 outputs | -- | -- | **No source located in this task's file list.** `t76_run_meta.json`'s own provenance note states this is "the SAME file... T20 (2030 main/null) and T26 (lambda arms) were all derived FROM," i.e. the rebuild's earliest point is the 2022 stock. A 2005/2010/2015 pre-pandemic occupancy number, if quoted, must be sourced from an earlier Step-6 forecasting artifact not in this task's scope -- flag for manager. | -- |

---

## R2 -- 2030 scenarios (WFH-persistence household basis and stock-weighted change)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Household basis per arm: S-Full 1200, S-None 1198, S-Partial 1200, S-Revert-std 1199; four-way common basis | 1198 | households | n/a | `T69/out/cross_scenario_common_basis.csv` (scp'd, `impl/T79_in/t69_cross_scenario_common_basis.csv`) | whole file (11 rows) | (dh), (cd) [item 30 ruling] | **Any cross-scenario comparison must use the 1,198 common households, never the per-arm totals.** Reproduced 3 separate times (T69, T71, this task) with no discrepancy. | Figures 3, 5 |
| S-None (revert): Electricity:Facility stock-weighted % change 2022->2030 | -0.1225 | percent | [-0.1480, -0.0964] | `T69/out/S-None/enduse_change_2022_2030.csv` (scp'd) | row `level=stock_weighted, metric=Electricity:Facility` | (dh) | QUOTABLE, excludes zero. CI method: `stock_weighted_cluster_bootstrap`, 24-from-24 cells with replacement. | Figure 3/5 (scenario decomposition) |
| S-Partial: Electricity:Facility stock-weighted % change 2022->2030 | +0.0117 | percent | [-0.0065, +0.0351] | `T69/out/S-Partial/enduse_change_2022_2030.csv` | same row | (dh) | **NOT_EVALUABLE -- interval contains zero.** Never described as a change. | -- |
| S-Revert-std: Electricity:Facility stock-weighted % change 2022->2030 | -0.4408 | percent | [-0.4668, -0.4136] | `T69/out/S-Revert-std/enduse_change_2022_2030.csv` | same row | (dh) | QUOTABLE, excludes zero. `S-Revert-std` = T32, population mix held fixed; kept labelled distinctly from the two lambda arms per Ruling 5. | -- |
| S-None: midday_share stock-weighted change | -0.001273 | absolute fraction | [-0.003070, +0.000615] | `T69/out/S-None/enduse_change_2022_2030.csv` | row `metric=midday_share` | (dh) | **NOT_EVALUABLE -- interval contains zero.** CI is a NEW bootstrap for this arm (not a T67 file reuse) -- ruled correct and necessary at (dh) item 2 because T67 never scored these scenario trees. | -- |
| S-Partial: load_factor stock-weighted change | +0.000257 | absolute fraction | [-0.000418, +0.000917] | `T69/out/S-Partial/enduse_change_2022_2030.csv` | row `metric=load_factor` | (dh) | **NOT_EVALUABLE -- interval contains zero.** | -- |
| S-Revert-std: midday_share and load_factor stock-weighted change | -0.01383 / -0.01365 | absolute fraction | [-0.01610,-0.01138] / [-0.01475,-0.01253] | `T69/out/S-Revert-std/enduse_change_2022_2030.csv` | rows `metric=midday_share`/`load_factor` | (dh) | Both QUOTABLE, excludes zero -- the S-Revert-std arm shows the largest, most clearly separable shape change of the three scenario arms. | Figure 3 |
| All 8 end-use meters x 3 scenario arms, full CI table | -- | mixed | -- | `T69/out/{S-None,S-Partial,S-Revert-std}/enduse_change_2022_2030.csv` (all three scp'd) | whole files, `level=stock_weighted` rows | (dh) | Fan electricity is `0.0/[0,0]` (no schedule sensitivity in this meter, NOT_EVALUABLE by the zero-interval rule) in every arm -- read directly, not assumed. | -- |
| S-Full vs S-None/S-Partial/S-Revert-std -- same 8 meters for the main occupancy build | see R3 below | -- | -- | `T68/out/enduse_change_2022_2030.csv` | -- | (de) | S-Full is the "main" (real OLS trend) build; it is the R3 headline, listed once there rather than duplicated here. | -- |

---

## R3 -- Annual energy by end use (2022 vs 2030, stock-weighted, S-Full/main scenario)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Electricity:Facility (total), stock-weighted % change 2022->2030 (S-Full) | +0.1209 | percent | [+0.0981, +0.1407] | `T68/out/enduse_change_2022_2030.csv` (scp'd) | row `level=stock_weighted, metric=Electricity:Facility` | (de) | QUOTABLE, excludes zero. This is the rebuild's replacement for the archived "+0.6 to +1.2% to 2030" figure -- see Also-list. | Figure 2, 4 |
| Interior lights, stock-weighted % change | -0.0157 | percent | [-0.0274, -0.0043] | same file | row `metric=InteriorLights:Electricity` | (de) | QUOTABLE, excludes zero. Also has a per-dwelling absolute (item 40 allows lights). | Figure 2 |
| Interior equipment, stock-weighted % change | -0.0066 | percent | [-0.0119, -0.0012] | same file | row `metric=InteriorEquipment:Electricity` | (de) | QUOTABLE, excludes zero. Also has a per-dwelling absolute (item 40 allows equipment). | Figure 2 |
| Fan electricity, stock-weighted % change | 0.0 | percent | [0.0, 0.0] | same file | row `metric=Fan Electricity Energy` | (de) | **NOT_EVALUABLE -- zero-width interval at zero.** No divisor exists for this meter (item 40), and no change either. | -- |
| Heating (EnergyTransfer), stock-weighted % change | -0.2905 | percent | [-0.4049, -0.1746] | same file | row `metric=Heating:EnergyTransfer` | (de) | QUOTABLE, excludes zero. Whole-building only (item 40: no divisor for this meter). | Figure 2 |
| Cooling (EnergyTransfer), stock-weighted % change | +0.5947 | percent | [+0.5235, +0.6523] | same file | row `metric=Cooling:EnergyTransfer` | (de) | QUOTABLE, excludes zero. Whole-building only. | Figure 2 |
| Water systems (EnergyTransfer), stock-weighted % change | +0.5806 | percent | [+0.3419, +0.7845] | same file | row `metric=WaterSystems:EnergyTransfer` | (de) | QUOTABLE, excludes zero. Whole-building only. `n_zero_2022_denominator_excluded=0` (MidRise water-meter absence does not recur on the rebuilt tree). | Figure 2 |
| HVAC+DHW electricity (remainder), stock-weighted % change | +0.3578 | percent | [+0.2863, +0.4166] | same file | row `metric=HVACDHW:Electricity` | (de) | QUOTABLE, excludes zero. Whole-building only. | Figure 2 |
| Whole-building stock-weighted annual kWh by end use, 2022 vs 2030 raw levels (all 8 meters) | see table | kWh | none (levels, not a bootstrapped change) | `T71/out/fig02_annual_by_enduse.csv` (local, `impl/T71_out/`) | whole file (16 data rows) | (dk) | Levels only; e.g. Electricity:Facility total 117,942.5 kWh (2022) -> 118,049.8 kWh (2030), stock of 1,200 households (300 per archetype). | Figure 2 (fig02) |
| Per-dwelling stock-weighted kWh, lights and equipment only (the only two meters item 40 allows) | Lights 1062.7 -> 1062.6; Equip 3075.5 -> 3075.3 | kWh/dwelling/yr | none (levels) | same file | rows `Interior lights`/`Interior equipment` | (dk) | Every other meter's per-dwelling column reads `NOT_EVALUABLE (no derived unit divisor)` -- read directly, not summarized. | Figure 2 |

---

## R4 -- Load shape, peak, load factor, midday share, ramp

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Load factor, stock-weighted change 2022->2030 (S-Full) | +0.004943 | absolute fraction | [+0.004128, +0.005743] | `T71/out/fig04_peak_loadfactor_ramp_ci.csv` (local) / `T68/out/enduse_change_2022_2030.csv` | row `metric=load_factor` | (dk)/(de) | QUOTABLE, excludes zero. Reused verbatim from `T67/out/real_correcteddata/ci_reproduction_t67.csv` (`cell_cluster_bootstrap_GENUINE` row) per Ruling 6, not recomputed. **Replaces the archived "+0.0117" figure -- new value is less than half the old one; see Also-list.** | Figure 4 |
| Midday share, stock-weighted change 2022->2030 (S-Full), plain pooled interval | +0.0073235 | absolute fraction | [+0.006451, +0.008195] (plain, Eq.16 method) | `manuscript/draft_SI_clustering_ci.md` number trace table | S.10 table row "Midday share: Plain pooled" | (db) [item 39 closed] | Do not quote the plain interval alone -- see next row. | SI Figure/Table (clustering) |
| Midday share, stock-weighted change 2022->2030 (S-Full), **cluster-aware interval (use this one)** | +0.0073235 | absolute fraction | [+0.006160, +0.008593] | `manuscript/draft_SI_clustering_ci.md` / `T67/out/real_correcteddata/ci_reproduction_t67.csv` | S.10 table row "Midday share: Genuine cell-cluster bootstrap" | (db) | QUOTABLE, excludes zero either way, but **39.8% wider than the plain interval** -- per item 39's Ruling 5, the main-text sentence must cite this wider interval, not the plain one. **Replaces the archived "+0.37 pp" figure -- new value (0.73 pp) is roughly double; see Also-list.** | Figure 4, SI S.10 |
| Peak demand, stock-weighted, 2022 vs 2030 (S-Full) | 47.207 -> 46.332 | kW | **no interval available** | `T71/out/fig04_peak_loadfactor_ramp_ci.csv` | row `metric=peak_kW_annual` | (dk) | **NOT_EVALUABLE -- no bootstrapped CI exists in the accepted WP6 output for this metric**, at any level. Point values only, must be shown hatched/visually distinct per (dk)'s own figure design. | Figure 4 |
| Evening ramp, stock-weighted mean, 2022 vs 2030 (S-Full) | 7.852 -> 7.768 | kW | **no interval available** | same file | row `metric=evening_ramp_kW_mean` | (dk) | **NOT_EVALUABLE -- no CI exists**, same reason as peak. | Figure 4 |
| Intraday load shape (weekday, whole-year average, 2030, Electricity:Facility), by scenario, all 24 hours x 4 scenario arms | -- | kW | none | `T71/out/fig03_intraday_load_shape.csv` (local, 97 data rows) | whole file | (dk) | Household basis: n=1198 (four-way common). S-Revert-std shows a flatter midday and higher evening peak than the other three arms -- visually confirmed by the manager, not just asserted from the CSV. | Figure 3 |
| End-use x hour percent-change heatmap (season=all, daytype=all) | -- | percent (point estimate) | **none -- descriptive only** | `T71/out/fig05_enduse_hour_diff.csv` (local, 192 cells) | whole file | (dk) | **Not an individually quotable change claim.** No bootstrap interval exists at this end-use x hour granularity; 0 of 192 cells silently marked NOT_EVALUABLE (verified directly), but the heatmap itself is descriptive, not CI-backed. Do not cite a single cell's percent as a "change" in prose. | Figure 5 (first reviewer's own ask) |
| Full-grid mean peak HOUR (stock-weighted, all 6 cities), 2022 vs 2030 | **NOT VERIFIED** | -- | -- | none found | -- | -- | **No stock-weighted or full-6-city aggregate mean-peak-hour number exists in any T68/T69/T71 accepted deliverable.** `T68/out/grid_metrics.csv` carries `peak_hour_annual`/`mean_peak_hour_circ` per household (2,400 rows), never aggregated to a stock point value, and `enduse_change_2022_2030.csv` has no CI row for it either. The closest available number is T73's Toronto-only WP5 comparison (R6 below), which is a different basis. **Flag for manager: WP6 may need a peak-hour aggregation step added before the Results section can restate the archived "17.0-17.7 h band" claim.** | -- |

---

## R5 -- Full model vs average-profile arm (Figure 6, WP3)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Comparison table, full model (T21) vs average-profile arm (T30), all 24 cells x 2 years x per-cell metrics | 1,104 rows (850 QUOTABLE / 254 NOT_EVALUABLE) | mixed | per-row, mostly "no CI available" | `T77/out/fig06_comparison_table.csv` (scp'd, `impl/T79_in/`) | whole file | (dq) | **PASS certifies controls and row counts, not every individual row** -- any number quoted must be checked against that row's own `quotable`/`quotable_reason` columns first (T77's own report language). Static arm (T19/T22) intentionally excluded -- CLOSED as not home-for-home, checklist item c8. | Figure 6 |
| Example row -- SingleD/Toronto_5A/2022, Electricity:Facility whole-building kWh: full model vs average-profile arm | 8,225.56 vs 8,951.40 (delta +725.84) | kWh | no CI available (no established cross-arm bootstrap in this project) | same file | row 2 | (dq) | QUOTABLE as a per-cell illustration; not a stock-weighted headline (no stock aggregate row exists in this file -- `level` column is `per_cell` throughout, never `stock_weighted`). | Figure 6 |
| Household-level peak-hour spread (Mardia circular SD), full model vs average-profile arm, SingleD/Toronto_5A | 2022: 3.493 h (full) vs 0.084 h (avg-arm); 2030: 3.255 h (full) vs 0.053 h (avg-arm) | hours | n/a (point circular SD) | `T77/out/household_peak_spread_both_arms.csv` (scp'd, 96 rows) | rows 2-5 | (dq) | QUOTABLE, per-cell illustration of the design contrast: the full model preserves real household-to-household diversity in peak timing; the average-profile arm collapses it almost to zero by construction. Full 96-row table (24 cells x 2 years x 2 arms) has the complete picture. | Figure 6 |
| Household-level peak-hour circular mean and morning-leaning share, full model, SingleD across 6 cities | 2022: 15.05-16.78 h; 2030: 15.24-16.62 h (per-city range, SingleD only shown) | hours | n/a (circular quantity; compare directly, do not subtract) | `T77/out/fig06_comparison_table.csv` | rows for `metric="Peak hour (circular mean...)"`, `arch=SingleD` | (dq) | QUOTABLE per-cell. This is the closest rebuilt equivalent to the archived "~15.1 h household-level circular mean" claim, but it is per-cell (SingleD only shown here), not a single stock-weighted number -- see Also-list. | Figure 6 |

---

## R6 -- Measured vs simulated check (Toronto/Ontario 2022, rebuilt runs)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Toronto, shoulder, weekday: load_factor sim vs measured | 0.4680 (sim) vs 0.4305 (measured), diff +0.0376 | dimensionless | none | `T73/out/sim_vs_measured_toronto_2022_shape_rebuilt.csv` (local, 1,760 rows) | row `period=shoulder,daytype=weekday,measured_scope=Toronto,metric=load_factor` | (dm)/(dj) | QUOTABLE as a point comparison. No CI on either side (this is a stock-weighted point statistic, not a bootstrap output). | Figure 7 |
| Toronto, shoulder, weekday: midday_share, peak_to_avg, mean_peak_hour sim vs measured | midday 0.3787 vs 0.3513; peak/avg 2.1367 vs 2.3231; peak hour 17.0 vs 18.69 | mixed | none | same file | same row group | (dm)/(dj) | QUOTABLE point comparisons. | Figure 7 |
| Summer and winter weekday equivalents (Toronto and Ontario scopes) | see file | mixed | none | same file | rows `period=summer`/`winter, daytype=weekday` | (dm)/(dj) | QUOTABLE point comparisons; representative rows read directly (12 real-world period/day-type groups total across the figure). | Figure 7 |
| **max_kwh_per_premise sim vs measured -- NOT COMPARABLE** | e.g. 2.006 (sim) vs 1.617 (measured), Toronto shoulder weekday | kWh/premise | none | same file | column `max_kwh_per_premise` | (dm) | **Never quote as a like-for-like comparison.** T73's own finding: this one metric is on a different measuring scale between sim and measured despite sharing a column name (confirmed by reading both source scripts). Figure 7 draws this bar hatched and labelled "not comparable." | Figure 7 |
| Rebuild vs old (retired) whole-building annual electricity sanity ratio, all 4 archetypes | SingleD 1.0075; OtherDwelling 0.9997; MidRise 1.0017; HighRise 1.0072 | ratio | n/a | `T73/out/t70_run_meta.json` (local) | `c5_rebuild_vs_old_sanity_bound` | (dj) | QUOTABLE as a validation statement (occupancy-only rebuild barely moved annual electricity, all within 0.1-0.7%), not as a Results headline number itself. | -- |
| Annual Facility kWh per dwelling, 2022, by archetype (T15/T70 DWELLING_COUNT basis) | SingleD 8,225.56; OtherDwelling 6,775.56; MidRise 8,808.77; HighRise 5,011.07 | kWh/dwelling/yr | none | `T73/out/t70_run_meta.json` | `annual_facility_kwh_per_dwelling_estimate` | (dj) | **FLAG FOR MANAGER -- possible divisor conflict with item 40.** This per-dwelling figure divides whole-building `Electricity:Facility` by T15's geometry-derived `DWELLING_COUNT` (OtherDwelling=7, MidRise=31, HighRise=79), which is NOT the same divisor T66's corrected validator uses for the SAME archetypes on the equipment/lighting meters (MidRise=33 equip/36 light, HighRise=81/90). Item 40 rules "every meter other than equipment/lighting has NO derived divisor" for WP6; this WP5 number was computed and accepted independently (dj), before item 40 existed, on a different meter (Facility total) with a different divisor. Not reconciled anywhere in the plan log -- whether this WP5 per-dwelling number is safe to quote in the Results section, or should be restricted to SingleD (divisor=1, no ambiguity) plus whole-building figures only for the other three archetypes, is an open ruling. | -- |

---

## R7 -- Sample-size check (N=200 convergence, SI)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| N=200 half-width vs N=150 half-width, all 24 (cell, metric) combinations | half-width INCREASES at N=200 vs N=150 in all 24/24 combinations | mixed (native units per metric) | n/a | `T75/logs/t75_run_meta.json` (scp'd, `impl/T79_in/`) / `T28/out/t28_b4_convergence.csv` (not fetched, cluster-only, 432 rows) | `finding_n200_method_switch` block | (do), 2nd T75 entry | **This is a method-switch artifact, not evidence of under-convergence.** N=200 uses a parametric Student-t CI on the real full sample; N=10-150 use a percentile CI of 1000 bootstrap subsample draws from that same 200. Must be stated as such if quoted, never as "uncertainty does not shrink with N." | Figure 8 (SI) |
| Example: SingleD__Montreal_6A, `elec_facility_kWh_delta_2022to2030`, half-width at N=150 vs N=200 | 2.4475 (N=150) vs 4.2046 (N=200) | kWh | n/a (these ARE the half-widths, not a further CI) | same file | `finding_n200_method_switch.examples[0]` | (do) | QUOTABLE as an illustration of the method-switch finding above. Montreal-only, 4 archetypes -- T28's B4 check never scored the other two cities used elsewhere in the paper (inherited scope, unresolved representativeness question). | Figure 8 |
| Row-count / precondition controls | 144/144 expected delta rows found; T54 precondition B0/B1/B2/B5=PASS, B3/B4=REPORT (no band by design) | -- | -- | same file | `controls.row_count_completeness`, `t54_precondition` | (do) | Both fired clean -- cited for provenance, not itself a Results number. | -- |

---

## R8 -- Model-selection threshold sensitivity (SI)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Candidates clearing all 4 published gates at the original (baseline) thresholds | 4 candidates (J3, J5_X1, J5_X2, J5_B) | count | n/a | `T74/out/figures/fig09_threshold_sensitivity.csv` (local, 25 rows) / `manuscript/draft_SI_model_selection.md` trace table | row `pct=0, scenario=baseline_original`, `n_passing_4of4=4` | (do), 1st T74 entry | **J3 is never the SOLE model to clear all four gates (`matches_J3_only=False` on all 21 tested scenarios, including the published baseline).** Per T04/R3-7 and this project's own binding rule, must be written as "the candidate with the best combined score among those that cleared all four checks," never "the only candidate to clear all four checks." | Figure 9 (SI) |
| J3's own gate scores (chosen model) | act JS 0.0191; AT_HOME RMS 4.57 pp; Spouse gap -2.03 pp; composite 0.6355 | mixed | n/a | `manuscript/draft_SI_model_selection.md` trace table | row "J3 gate scores" | draft SI, Status: DONE | QUOTABLE, re-derived from `step4_training_v4.md:341-344` by the T04/T36 tasks, not from the archived manuscript. | SI Table B1 |
| Threshold-sensitivity result: selection flips away from J3 | 2 of 21 scenarios (`at_home_max -20%`, `all -20%`), selected model becomes J5_X1 with only 1 of 4-6 candidates passing | -- | n/a | `T74/out/figures/fig09_threshold_sensitivity.csv` / `T74/out/figures/run_meta.json` (local) | `selected_model_changes_from_j3` | (do) | QUOTABLE. In every other scenario (19 of 21) the chosen model remains eligible and is still selected -- selection is not sensitive to small (+-10%) changes in 3 of 4 thresholds, and sensitive to the 4th (at-home error) only at the most aggressive -20% tightening tested. | Figure 9 |
| Threshold provenance (why the 4 gates sit where they do) | composite<1.045 and AT_HOME<=5.3pp equal the F1 baseline's own scores; act_JS<=0.05 has no independent rationale; Spouse gate tightened 10pp->5pp with no stated reason | -- | n/a | `manuscript/draft_SI_model_selection.md` trace table | row "Threshold provenance" | draft SI, from T04 (`git log -S`) | QUOTABLE as a stated limitation of the selection procedure, not an error in the chosen model. | SI S.2 |

---

## R9 -- Clustering-aware intervals (SI)

| Quantity | Value | Unit | Interval | Source file | Location | Accepting entry | Restriction | Figure |
|---|---|---|---|---|---|---|---|---|
| Midday share: plain pooled interval width vs genuine cell-cluster-bootstrap width | 0.00174 vs 0.00243 | absolute fraction | plain [0.00645,0.00819]; cluster [0.00616,0.00859] | `manuscript/draft_SI_clustering_ci.md` | S.10 table | (db) | QUOTABLE. **Cluster-aware interval is 39.8% wider** -- a real, material effect of household clustering by city/archetype; both methods exclude zero, so no conclusion flips, but the plain interval understates uncertainty for this metric. Same point estimate underlies the R4 midday-share row above. | SI S.10 |
| Load factor: plain pooled interval width vs genuine cell-cluster-bootstrap width | 0.00165 vs 0.00161 | absolute fraction | plain [0.00412,0.00577]; cluster [0.00413,0.00574] | same file | S.10 table | (db) | QUOTABLE. Cluster-aware interval is only 2.3% narrower (negligible, within Monte Carlo noise) -- the plain interval is adequate for this metric on its own. | SI S.10 |
| Retired stratified-bootstrap widths (DO NOT QUOTE) | 1.05% / 3.3% narrower than plain | -- | -- | same file | S.10, "A retired, invalid number" paragraph | (db) | **NEVER cite as evidence clustering is immaterial.** `method_b_cluster_bootstrap` was a mislabeled STRATIFIED bootstrap (held cells fixed, resampled within-cell) -- the opposite of a real cluster bootstrap, and it also used pre-rebuild data. Kept only as a labelled historical control. | -- |

---

## Also list -- every number the ARCHIVED manuscript's Abstract/Results/Conclusion quoted, with its status now

Read from `archive/2J_manuscript_submission.md` lines 1-30 (Abstract/Highlights) and 360-490
(Results/Discussion/Limitations/Conclusion).

| Archived number | Where | Status now |
|---|---|---|
| 64,061 GSS diaries; ~192,183 calibrated diary-days | Abstract, Highlights | **NOT RESULTS-SECTION, OUT OF SCOPE.** Data/methods count (augmentation step), not a WP6-11 rebuild output. Not re-derived or re-read by this task. |
| 144,507-household 2021 Census stock frame | Abstract | **RETIRED / SUPERSEDED.** All rebuilt work (T20/T21/T26/T76) uses the refined 144,465-household frame confirmed directly in `T76/logs/t76_run_meta.json` (`n_rows_read=6,934,320 = 144,465 x 24 x 2`). The archived Limitations section (line 459) itself documents the 2026-07-09 relink that produced this refined frame. |
| 6,000 paired EnergyPlus runs (campaign total, 2005-2030) | Abstract, §5.2, Conclusion item 1 | **NO SOURCE FOUND for a rebuilt equivalent.** The WP6/WP11 rebuild scope is 2022/2030 only (T21: 2,400 household-years = 24 cells x 2 years x 50 households). No 2005/2010/2015 leg has been re-simulated or re-read in this revision. |
| 48 of 48 cell-years SHEU-calibrated within +/-2.7% | Abstract, §5.2, §5.4, Conclusion item 1/4 | **REPLACED BY the A5 gate number (item 40 / entry (da)): corrected validator scores 48/48 PASS at full grid** (`T66/out` corrected `step9_validate_full_corrected.py`). The original script's 12/48 is a seen-failing control only, never a result (binding rule, this task doc). Whether 48/48 PASS is the same statistic as "within +/-2.7%" is not established here -- flag for manager: the two claims may not be numerically equivalent, only structurally similar (both "all 48 cells pass a gate"). |
| SHEU EUI table: 115/108/100/78 kWh/m2 (2022), 116/108/101/79 (2030), by archetype | Table 5, §5.2 | **NO SOURCE FOUND.** This EUI-per-area comparison against SHEU regional ranges was never re-derived on the rebuilt (T21) runs by any task T66-T79. Out of this rebuild's scope as currently scoped. |
| +5.2 pp weekday at-home break, 2015->2022 (demographically standardized) | §5.1, Conclusion item 2 | **NO SOURCE FOUND in T70-T79 outputs.** T76's earliest series is the 2022 stock baseline; no 2015 comparator was read. If this number is still to be quoted, it must come from an earlier Step-6 forecasting artifact, not verified by this task. |
| +2.2 to +3.9 pp, 2030 vs pre-pandemic (flagged "provisional" in the archived Limitations, §7) | §5.1, Conclusion item 2 | **RETIRED as stated; no single reproduced replacement figure.** The archived text itself flags this as provisional pending a post-relink recalibration. T76/T26's own SC2 acceptance check (2026-09-15, not re-read by this task) established the expected ORDER (Revert < Partial < Persist), but no single rebuilt pp figure matching this exact claim was found in T70-T79 outputs -- flag for manager. |
| +1.4 to +2.6% annual electricity across the COVID break (2015->2022) | §5.2, Discussion, Conclusion item 3 | **NO SOURCE FOUND.** Rebuild scope is 2022-2030 only; no 2015-2022 leg exists in T66-T79. |
| +0.6 to +1.2% annual electricity, 2022->2030 | §5.2, Discussion, Conclusion item 3 | **REPLACED BY R3's stock-weighted Electricity:Facility change: +0.1209% [+0.0981, +0.1407]** (`T68/out/enduse_change_2022_2030.csv`, entry (de)). **The rebuilt number is roughly an order of magnitude smaller** than the archived figure -- material difference, flag for manager/author before use. |
| Delta midday share +0.37 pp; Delta load factor +0.012 (both CI exclude zero) | §5.3, Conclusion item 3 | **REPLACED BY R4/R9's numbers: midday share +0.732 pp [cluster-aware CI +0.616, +0.859]; load factor +0.494 pp [+0.413, +0.574].** Midday share is roughly double the archived figure; load factor is roughly 40% smaller. Both still exclude zero. Material differences on both -- flag for manager/author. |
| Mean peak hour stays within 17.0-17.7 h band across all 5 survey/forecast cycles | §5.3, Discussion, Conclusion item 3 | **NO SOURCE FOUND for a stock-weighted, full-6-city rebuilt equivalent** -- see R4's flagged gap. The closest available number, T73's Toronto-only WP5 comparison (R6), gives 17.0-18.0 h depending on season, a different basis (single city, measured-vs-simulated check, not the multi-cycle stock trajectory). |
| Household-level circular mean peak hour ~15.1 h in 2022 and 2030; 22-25% morning-leaning nationally | §5.3 | **PARTIALLY REPLACED.** T77's `fig06_comparison_table.csv` gives per-cell circular means for the full model (T21): SingleD ranges 15.05-16.78 h (2022) and 15.24-16.62 h (2030) across the 6 cities -- see R5. No single stock-weighted national number was computed; the archived "~15.1 h" and "22-25%" figures are close in magnitude to the SingleD per-cell range but are not the same statistic (stock-weighted across all 4 archetypes vs per-cell SingleD-only as read here). Flag for manager: a stock-weighted aggregate would need to be built from T77's full per-cell table, not this task's job (reading only). |
| Coincidence factor below unity (stock aggregate flatter than any single dwelling) | §5.3 | **NOT VERIFIED.** No coincidence-factor number (ratio of coincident stock peak to sum of individual household peaks) was found in any T68/T69/T71/T77 output read by this task. |
| Presence-only baseline plug-load 6,550-6,870 kWh vs SHEU targets 3,139-3,700 kWh; activity model lands on ~3,700 kWh anchor | §5.4, Discussion | **NO SOURCE FOUND.** This is the Step-9 activity-vs-presence-baseline comparison (T48-family files per T75's own relevance judgement, which excluded them from the N=200 figure as a DIFFERENT check). Not re-read by this task; out of the WP6/WP11/WP5 file list this task was scoped to. |
| Building-level equipment peak-hour shift 0 +/- 1 h (mean -0.12 h, sigma 0.39 h), 24 cells | §5.4, Discussion, Conclusion item 4 | **NO SOURCE FOUND in T70-T79 outputs.** This is the A6 stop-rule metric (plan (bw): "A6 (peak-shift) unaffected, stays PASSED per (ce)/(bw)"), sourced from the published `/speed-scratch/o_iseri/step9_run/loadshape/peak_shift_summary.csv`, not re-read by this task (not in the T68-T77 file list this task was scoped to). |
| 4,800 paired baseline-vs-activity runs, 4,795 with complete meter output (archived) vs 4,790 (source doc) | §5.4 | **UNRESOLVED DISCREPANCY, carried forward, not fixed by this task.** `manuscript/draft_SI_model_selection.md`'s own trace table already flags 4,795 (archived) vs 4,790 (`09_activityDrivenLoads_val.md`) as unreconciled. Not re-derived here (out of the T66-T79 file list). |
| Weighted fraction at home: 62.7% (2005), 62.3% (2010), 64.5% (2015), 70.6% (2022) | §5.1 | **NO SOURCE FOUND.** Multi-cycle (2005-2022) at-home levels; not part of any T66-T79 output. |
| Match-tier distribution: Tier-1 44.94%, Tier-2 21.39%, Tier-3 33.67%, FailSafe 0.00% | §7 Limitations | **NOT RESULTS-SECTION, OUT OF SCOPE.** Census-GSS linkage QA metric, not touched by WP6/WP11/WP5 rebuild tasks. |
| Weather-adjusted +7.9% residential electricity increase (external benchmark); ~20% WFH workdays vs 5% pre-pandemic; ~+12% structural residential in-home energy demand | §6 Discussion | **NOT RESULTS-SECTION, OUT OF SCOPE.** External literature figures cited for context, not this project's own measured numbers. |

---

## Ledger

No cluster jobs run by this task (reading only). Every cluster file used was either already local
(from T71/T73/T74's own accepted `_out/` folders) or fetched via `scp` into `impl/T79_in/`, all under
2 MB:

| File | Size | Source path on cluster |
|---|---|---|
| `t75_run_meta.json` | 6,819 B | `/speed-scratch/o_iseri/2J_revision/T75/logs/t75_run_meta.json` |
| `fig08_n200_convergence.csv` | 19,810 B | `/speed-scratch/o_iseri/2J_revision/T75/out/figures/fig08_n200_convergence.csv` |
| `t76_run_meta.json` | 7,730 B | `/speed-scratch/o_iseri/2J_revision/T76/logs/t76_run_meta.json` |
| `fig01_athome_by_hour.csv` | 13,959 B | `/speed-scratch/o_iseri/2J_revision/T76/out/figures/fig01_athome_by_hour.csv` |
| `t77_report.txt` | 2,807 B | `/speed-scratch/o_iseri/2J_revision/T77/logs/t77_report.txt` |
| `controls.json` (T77) | 3,207 B | `/speed-scratch/o_iseri/2J_revision/T77/out/controls.json` |
| `fig06_comparison_table.csv` | 310,197 B | `/speed-scratch/o_iseri/2J_revision/T77/out/fig06_comparison_table.csv` |
| `household_peak_spread_both_arms.csv` | 9,086 B | `/speed-scratch/o_iseri/2J_revision/T77/out/household_peak_spread_both_arms.csv` |
| `t77_run_meta.json` | 999 B | `/speed-scratch/o_iseri/2J_revision/T77/out/run_meta.json` |
| `t77_run_meta_part2.json` | 893 B | `/speed-scratch/o_iseri/2J_revision/T77/out/run_meta_part2.json` |
| `t68_run_meta.json` | 3,729 B | `/speed-scratch/o_iseri/2J_revision/T68/out/run_meta.json` |
| `t68_controls.json` | 2,616 B | `/speed-scratch/o_iseri/2J_revision/T68/out/controls.json` |
| `t68_enduse_change_2022_2030.csv` | 76,717 B | `/speed-scratch/o_iseri/2J_revision/T68/out/enduse_change_2022_2030.csv` |
| `t69_cross_scenario_common_basis.csv` | 501 B | `/speed-scratch/o_iseri/2J_revision/T69/out/cross_scenario_common_basis.csv` |
| `t69_S-None_run_meta.json` | 8,457 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-None/run_meta.json` |
| `t69_S-None_controls.json` | 2,562 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-None/controls.json` |
| `t69_S-None_enduse_change_2022_2030.csv` | 81,155 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-None/enduse_change_2022_2030.csv` |
| `t69_S-Partial_run_meta.json` | 7,731 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Partial/run_meta.json` |
| `t69_S-Partial_controls.json` | 2,550 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Partial/controls.json` |
| `t69_S-Partial_enduse_change_2022_2030.csv` | 86,369 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Partial/enduse_change_2022_2030.csv` |
| `t69_S-Revert-std_run_meta.json` | 8,165 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Revert-std/run_meta.json` |
| `t69_S-Revert-std_controls.json` | 2,563 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Revert-std/controls.json` |
| `t69_S-Revert-std_enduse_change_2022_2030.csv` | 77,911 B | `/speed-scratch/o_iseri/2J_revision/T69/out/S-Revert-std/enduse_change_2022_2030.csv` |

Skipped (too large for the 2 MB scp allowance, not read): `T68/out/enduse_annual.csv` (2.1 MB),
`T68/out/enduse_hourly_profile.csv` (511 MB), `T69/out/*/enduse_annual.csv` (~2.2 MB each),
`T69/out/*/enduse_hourly_profile.csv` (~510 MB each), `T77/out/enduse_annual.csv` (2.2 MB),
`T77/out/closure.csv`/`grid_metrics.csv` (not needed once the change-table and comparison-table
files were confirmed sufficient), `T68/out/grid_metrics.csv` (535 KB -- header read via `ssh head -1`
only, full file not fetched; confirmed it carries no stock-weighted peak-hour aggregate). Local files
already present and read without a fresh scp: `T71_out/*`, `T73_out/*`, `T74_out/figures/*`
(all pre-existing from the accepting tasks' own uploads).

## Verified

Every value in the R1-R9 tables above was read directly from the cited file during this task (not
copied from a plan-log summary), except where the plan-log entry's own quoted number was
cross-checked against the file and found to match exactly (R7's `finding_n200_method_switch`
example, R8's `matches_J3_only` global finding). Household-count and controls-fired claims (S-Full
1200/S-None 1198/S-Partial 1200/S-Revert-std 1199; four-way common basis 1198;
`controls_all_fired=true` on T68/T69/T77) were each re-read from their own `run_meta.json`/
`controls.json`, not assumed from a prior entry's prose.

## Decisions

1. **Granularity:** "one row per quotable number" is interpreted as one row per distinct
   stock-level or headline quantity a Results sentence would cite, not one row per CSV data row
   (several source files have 250-1,760 rows). Full per-cell breakdowns are always pointed at via
   the cited file, never transcribed in full here.
2. Where a metric exists only per-cell with no stock-weighted aggregate (R5's Figure 6 table, part
   of R1's household-level circular-mean claim), the sheet says so explicitly rather than silently
   presenting one cell's number as if it were the stock figure.
3. Two possible divisor conflicts were found and are written up as open items rather than resolved
   silently: (a) T70/T73's WP5 per-dwelling `Electricity:Facility` divisor (T15's geometry-based
   `DWELLING_COUNT`) versus T66's corrected WP6 equipment/lighting divisor -- different numbers for
   the same archetypes (R6); (b) whether the archived "48/48 within +/-2.7%" SHEU-calibration claim
   is the same statistic as the rebuild's A5 "48/48 PASS" gate, or only structurally similar
   (Also-list).
4. Did not attempt to build a stock-weighted mean-peak-hour or coincidence-factor number myself
   (would be new computation, outside this task's reading-only scope) -- both are recorded as gaps
   for the manager/a future task to close before the Results section can restate the archived
   17.0-17.7 h band claim.

## Next

Manager/WP10: (1) rule on the two divisor-conflict/statistic-equivalence flags in Decisions #3; (2)
decide whether a peak-hour aggregation task is needed before Results can state a mean-peak-hour
number (R4's flagged gap); (3) confirm whether the household-level circular-mean/morning-leaning
national figure needs a dedicated stock-weighted computation from T77's full per-cell table, or
whether the per-cell SingleD range in R5 is sufficient for the Results text; (4) begin drafting
Results (Section 3) from this sheet, in the R1-R9 order.

## WHAT I DID NOT VERIFY

- Did not open `T68/out/enduse_annual.csv`, `T69/out/*/enduse_annual.csv`, `T77/out/enduse_annual.csv`
  (each ~2.1-2.2 MB) or any `enduse_hourly_profile.csv` (~510 MB each) -- all over or too close to
  the 2 MB scp allowance; recorded as "not read, too large" per the task doc's own instruction.
- Did not open `T68/out/grid_metrics.csv` or `T77/out/grid_metrics.csv`/`closure.csv` in full (535 KB
  and 300 KB respectively) -- only `T68`'s header was read via a single `ssh head -1` command to
  confirm the column list (no stock-weighted peak-hour column exists), per the login-node allow-list
  (`head` of one small file). The 2,400-row body was not read.
- Did not verify any PNG pixel content by eye (Figures 1, 6, 7, 8, 9's images were not viewed by this
  task) -- only the numeric CSVs/`run_meta.json`/report files behind them, consistent with a
  reading-only, no-new-verification task (the plan log's own entries (dk)-(dq) already record the
  manager's visual inspection of each figure).
- Did not re-read `draft_S2_framework.md`, `draft_S7_limitations.md`, or `draft_SI_schedule_completion.md`
  in full -- only `draft_SI_clustering_ci.md` and `draft_SI_model_selection.md` were read in full, as
  the two SI drafts whose own trace tables cover R8/R9. Any Results-relevant number those other three
  files might carry was not captured here.
- Did not verify the archived manuscript's own line numbers beyond lines 1-30 and 360-490 (the exact
  range the task doc specified); did not check whether the Methods or Data sections (not in that
  range) quote additional numbers that might also need a status.
- Did not attempt to reconcile the "48/48 within +/-2.7%" (archived SHEU-calibration claim) against
  the "48/48 PASS" (rebuild A5 gate) statistic-equivalence question raised in the Also-list -- flagged
  for the manager, not resolved.
- Did not check whether `T48`'s peak-shift-summary files (the A6 stop-rule source, referenced in
  plan (bw)) or the Step-9 activity-vs-baseline plug-load files (§5.4's archived numbers) exist in a
  form this task could read -- out of the T66-T79 file list this task was scoped to; both are marked
  NO SOURCE FOUND in the Also-list rather than searched for further.

## Status: DONE
