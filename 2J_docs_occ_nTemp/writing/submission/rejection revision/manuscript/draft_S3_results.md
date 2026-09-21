# 3. Results

The subsections below trace one path through the rebuilt pipeline: how the at-home pattern itself
differs between 2022 and three stated 2030 assumptions (3.1, 3.2), what that does to annual
electricity by end use (3.3), how it reshapes the daily load curve (3.4), what a simplified
average-profile scheduling method would have shown instead on the same households (3.5), how the
simulated load shape compares with a year of real measured data for one city (3.6), and two
robustness checks reported briefly here with full detail in the Supplementary Information (3.7,
3.8).

## 3.1 Occupancy change

The at-home occupancy series is built on a stock frame of 144,465 census households (Section 2.5,
Section 2.9), covering the 2022 survey cycle directly and four 2030 variants built from the
scenario construction of Section 2.7. The values below are read at one representative point, a
weekday at noon (hour 12), with the full 24-hour, weekday-and-weekend series shown in Figure
[R1-athome].

At weekday noon in 2022, 47.8 percent of the stock is at home. For 2030, four variants were run
side by side rather than a single projection: a main scenario that assumes the pandemic-era rise in
at-home behaviour persists in full (47.8 percent moving to 50.1 percent); a partial-persistence
scenario that assumes half of that shift has faded by 2030 (46.2 percent); a full-reversion scenario
that assumes the shift has faded completely and 2030 sits back on the pre-pandemic trend (42.3
percent); and a no-change control that reproduces the 2022 pattern unmodified (47.8 percent,
identical to the 2022 value to the last reported digit, itself an acceptance check on the
scenario-construction code rather than a scenario in its own right). These four numbers describe
the household schedules built under each stated persistence assumption (Section 2.7); they are a
designed comparison of assumptions, not a claim that any single one of them is what will actually
occur in 2030.

Averaged over the whole weekday, 74.4 percent of household-hours are spent at home in 2022. The
three 2030 scenarios move this whole-day weekday share by 1.49 percentage points (main scenario),
negative 0.85 percentage points (partial persistence) and negative 3.21 percentage points (full
reversion); these are the designed steps from 2022, not attained targets. The pandemic-era break
that the scenarios carry forward or remove is measured on the survey respondents themselves: in
2022 the national weekday at-home rate sits 4.73 percentage points above where the 2005 to 2015
trend would have placed it, and 7.67 percentage points above it when every survey cycle is first
reweighted to the housing stock's age, sex and labour-force mix (the standardized sensitivity behind the
standardized-reversion variant). The main scenario keeps that break and adds the 2005 to 2015
trend carried forward, which is why its step (1.49 percentage points) is positive; the full-reversion
scenario removes the break and keeps the trend, which is why its step is negative.

**Figure [R1-athome].** [image to be inserted from the WP11 output] Weekday and weekend at-home
fraction by hour of day, 2022 stock baseline and four 2030 variants (main persistence scenario,
partial-persistence scenario, full-reversion scenario, no-change control), on the 144,465-household
stock frame.

## 3.2 The 2030 scenarios

Three named 2030 scenarios, plus one standardized sensitivity variant, are compared on the
households they share. The four scenario arms were built and sampled independently and do not all
cover the same households (1,200 for the main scenario, 1,198 for the full-reversion scenario, 1,200
for the partial-persistence scenario and 1,199 for the standardized-reversion variant); every
cross-scenario comparison in this subsection, and in Figures [R4-loadshape] and [R4-heatmap], uses
only the 1,198 households present in all four arms. This restriction is stated once here rather than
repeated at every number below.

Under the full-reversion scenario (code S-None), stock-weighted whole-building electricity use falls
by 0.1225 percent from 2022 to 2030 (95 percent confidence interval negative 0.1480 to negative
0.0964 percent), a real change since the interval excludes zero. Under the partial-persistence
scenario (code S-Partial), the equivalent change is 0.0117 percent with a confidence interval of
negative 0.0065 to 0.0351 percent: because that interval contains zero, this is no detectable change
at this sample size, not an increase. Under the standardized-reversion variant (code S-Revert-std,
built with the trend and the pandemic-era jump recomputed after reweighting every survey cycle to
the housing stock's age, sex and labour-force mix), whole-building electricity falls by 0.4408 percent (95
percent confidence interval negative 0.4668 to negative 0.4136 percent), the largest change of the
three scenario arms. Across all eight end-use meters and all three scenario arms, fan electricity
shows no change in any arm (0.0 percent, interval 0.0 to 0.0), read directly from each arm's own
file rather than assumed.

The same pattern holds for the load-shape metrics. Under the full-reversion scenario, midday energy
share changes by negative 0.127 percentage points (95 percent confidence interval negative 0.307 to
positive 0.061 percentage points): no detectable change at this sample size. Under the
partial-persistence scenario, load factor changes by 0.026 percentage points (95 percent confidence
interval negative 0.042 to positive 0.092 percentage points): also no detectable change. Under the
standardized-reversion variant, both shape metrics show a change that excludes zero: midday share
falls by 1.383 percentage points (95 percent confidence interval negative 1.610 to negative 1.138)
and load factor falls by 1.365 percentage points (95 percent confidence interval negative 1.475 to
negative 1.253). This is the most clearly separable shape change among the three scenario arms.

## 3.3 Annual energy by end use

Under the main scenario, annual electricity is nearly flat: whole-building electricity use, weighted
to the national housing stock, rises by 0.1209 percent from 2022 to 2030 (95 percent confidence
interval 0.0981 to 0.1407 percent), a small but real change since the interval excludes zero.
Underneath that near-flat total, the mix of end uses, and (Section 3.4) the timing of demand, move
more than the total does; that is the pattern the rest of this Results section documents. At the
stock level, whole-building electricity use is 117,942.5 kWh in 2022 and 118,049.8 kWh in
2030, on a simulated stock of 1,200 households, 300 per archetype (Figure [R3-enduse]).

Among the individual meters, interior lighting falls by 0.0157 percent (95 percent confidence
interval negative 0.0274 to negative 0.0043 percent) and interior equipment falls by 0.0066 percent
(95 percent confidence interval negative 0.0119 to negative 0.0012 percent); both exclude zero. Fan
electricity shows no change (0.0 percent, interval 0.0 to 0.0). Heating energy transfer falls by
0.2905 percent (95 percent confidence interval negative 0.4049 to negative 0.1746 percent). Cooling
energy transfer rises by 0.5947 percent (95 percent confidence interval 0.5235 to 0.6523 percent),
water-systems energy transfer rises by 0.5806 percent (95 percent confidence interval 0.3419 to
0.7845 percent), and the remaining HVAC-and-domestic-hot-water electricity rises by 0.3578 percent
(95 percent confidence interval 0.2863 to 0.4166 percent); all three exclude zero. Heating, cooling,
water systems, and the HVAC and domestic-hot-water remainder are reported only at the whole-building
level, since no per-dwelling divisor exists for these meters. Per-dwelling annual energy is reported
only for equipment and lighting, the two meters with a defined per-dwelling divisor: stock-weighted
interior lighting falls from 1,062.7 to 1,062.6 kWh per dwelling per year, and interior equipment
falls from 3,075.5 to 3,075.3 kWh per dwelling per year (levels, not a bootstrapped change).

As an additional check, equipment and lighting energy were compared against their fitted SHEU
calibration target using a corrected version of the check that compares simulated and survey end-use totals; this is a
report-only check with a band of plus or minus 15 percent around the fitted target, not an
independent validation against outside data. On the rebuilt runs, all 48 archetype-by-city-by-year
cells pass this check. The original, uncorrected version of the same script had reported only 12 of
48 passing; that shortfall traced to an arithmetic error in the script itself for multi-unit
buildings, since fixed, and the 12-of-48 figure is retained only as a control confirming the fix,
never as a project result. No energy-use-intensity figure is available for this rebuild on this
basis; the previously published per-archetype energy-use-intensity table has no reproduced source in
the rebuild: [NUMBER NEEDED: EUI].

**Figure [R3-enduse].** [image to be inserted from the WP11 output] Panel A: stock-weighted
whole-building annual energy by end use, 2022 versus 2030, main scenario, all eight meters. Panel B:
stock-weighted per-dwelling annual energy for interior equipment and interior lighting only, the two
meters with a defined per-dwelling divisor.

## 3.4 Load shape: peak, load factor, midday share, ramp

Load factor, the ratio of the year's mean hourly load to its single annual peak hourly load
(Section 2.10), rises under the main scenario by
0.49 percentage points from 2022 to 2030 (95 percent confidence interval 0.41 to 0.57 percentage
points), a change that excludes zero. Midday share, the fraction of annual energy delivered between
09:00 and 17:00, rises by 0.73 percentage points (95 percent confidence interval 0.62 to 0.86
percentage points, using the interval that accounts for households sharing a city and an archetype;
Section 3.8 reports how much wider this interval is than one that ignores that clustering, and why
the wider one is used here). Both changes exclude zero.

Peak demand and evening ramp are reported as point values only, since no confidence interval is
available for either metric in the accepted output: stock-weighted peak demand falls from 47.207 kW
in 2022 to 46.332 kW in 2030, and the stock-weighted evening ramp falls from 7.852 kW to 7.768 kW;
no interval is available for either figure.

The stock-average weekday load shape for 2030 (Figure [R4-loadshape], the 1,198 common households)
reaches its maximum at hour 17 of the day under the main scenario, the partial-persistence scenario
and the full-reversion scenario, and at hour 18 under the standardized-reversion variant; hour 17
uses the same clock-aligned hour numbering as the rest of the framework (Section 2.5's four-hour
roll), corresponding to the late-afternoon hour beginning around 5 p.m. The standardized-reversion
variant also shows a visibly flatter midday and a higher evening peak than the other three arms. No
stock-weighted, all-city mean-peak-hour trend across multiple survey cycles, and no coincidence-factor
figure, exists in the rebuilt outputs; neither is stated here. Sections 3.5 and 3.6 report two other
kinds of peak-timing evidence: household-level circular-mean ranges from the full model, and a
measured-data comparison for one city.

The end-use-by-hour percent-change heatmap (Figure [R4-heatmap], 192 cells, all eight end-use meters
by 24 hours) is descriptive. For whole-building electricity it shows consumption falling slightly in
the overnight and late-evening hours and rising through the daytime hours, consistent with more of
the stock being home during the day. No single cell in this heatmap is quoted here as an individually tested
change, since no confidence interval exists at this hour-by-end-use granularity.

**Figure [R4-loadshape].** [image to be inserted from the WP11 output] Intraday weekday load shape,
2030, all four scenario arms, on the 1,198 households common to all four.

**Figure [R4-peak-lf-ramp].** [image to be inserted from the WP11 output] Peak demand and evening
ramp, 2022 versus 2030, point values with no confidence interval (shown visually distinct from load
factor, which carries a confidence interval).

**Figure [R4-heatmap].** [image to be inserted from the WP11 output] End-use by hour percent-change
heatmap, 2022 to 2030, main scenario, descriptive only.

## 3.5 Comparison with an average-profile model

To isolate what the household-level diary-based schedule contributes over a simpler description of
occupancy, the full model (used throughout Sections 3.1 to 3.4) was compared against an
average-profile arm that keeps each household's own calibrated design power but replaces its
individual schedule with the average schedule of its own archetype-and-city cell (Section 2.12). A
separate fixed-schedule arm was built earlier in this project but is not part of this comparison,
since it is not a home-for-home comparison and was excluded on that basis. The comparison table
covers 1,104 rows across 24 cells and both years; 850 of these rows carry a usable point comparison
and 254 do not, and any single number drawn from this table was checked against its own row before
being quoted here.

One illustrative cell: for the single-detached archetype in Toronto in 2022, whole-building
electricity use is 8,225.56 kWh under the full model and 8,951.40 kWh under the average-profile arm,
a difference of 725.84 kWh; this is a per-cell illustration, not a stock-weighted figure, and no
confidence interval is available for this cross-arm comparison. The two arms differ far more in
household-to-household diversity of peak timing than in this annual total. Household-level dispersion
in peak hour (a circular standard deviation, since peak hour wraps at midnight, Section 2.10) for the
same cell is 3.493 hours under the full model against 0.084 hours under the average-profile arm in
2022, and 3.255 hours against 0.053 hours in 2030: the average-profile arm collapses household-to-
household diversity in peak timing almost to zero, which follows directly from assigning every
sampled household the same schedule by construction, not from a data finding. Across the six
simulated cities, the full model's household-level circular mean peak hour for the single-detached
archetype ranges from 15.05 to 16.78 hours in 2022 and from 15.24 to 16.62 hours in 2030; this range
is reported for the single-detached archetype only, since that is the only archetype for which the
accepted comparison table's per-city rows were read for this draft.

**Figure [R5-comparison].** [image to be inserted from the WP11 output] Full model versus
average-profile arm: annual whole-building electricity and household-level peak-hour statistics, by
cell.

## 3.6 Independent measured check, Toronto/Ontario 2022

The simulated load shape was compared against a year of real measured hourly electricity data for
Toronto and for Ontario as a whole in 2022 (Section 2.10 defines each metric and names the
measured data source). For the shoulder season on a weekday, the simulated load factor is 0.4680
against a measured value of 0.4305, a difference of 0.0376. Simulated midday share is 0.3787 against
a measured 0.3513; simulated peak-to-average ratio is 2.1367 against a measured 2.3231; and the
simulated peak hour is 17.0 against a measured 18.69. Summer and winter weekday comparisons for both
the Toronto and the Ontario measured scopes are read the same way, twelve real-world period-and-
day-type groups in total, and are shown in full in Figure [R6-measured] rather than repeated here. No
confidence interval exists on either side of any of these comparisons; they are point statistics, not
bootstrapped.

One metric in this file, the maximum kWh per premise, is not comparable between the simulated and
the measured side despite sharing a column name: the two sides measure this quantity on different
scales (for example, 2.006 simulated against 1.617 measured for the Toronto shoulder weekday cell),
so Figure [R6-measured] draws this comparison hatched and labelled not comparable, and no value from
this row is used as a like-for-like statement anywhere in this paper.

Two further checks support the rebuild's plausibility. First, a sanity ratio between the
occupancy-only rebuild and the previously published (and now superseded) campaign shows the
occupancy rebuild barely moved annual whole-building electricity: the ratio is 1.0075 for
single-detached, 0.9997 for other-dwelling, 1.0017 for mid-rise and 1.0072 for high-rise, all within
0.8 percent of one. Second, annual whole-building electricity per dwelling for 2022 is quotable
only for the single-detached archetype, 8,225.56 kWh per dwelling per year, since this is the one
archetype with an unambiguous divisor of one dwelling per building; the equivalent per-dwelling
figures for the other three archetypes would need a building-to-dwelling divisor for whole-building
electricity, which is defined only for the equipment and lighting meters, so those three
archetypes are reported here only through the whole-building sanity ratios above, not as per-dwelling
energy figures.

**Figure [R6-measured].** [image to be inserted from the WP11 output] Simulated versus measured
load-shape metrics, Toronto and Ontario, 2022, by season and day type; maximum kWh per premise shown
hatched and labelled not comparable.

## 3.7 Sample-size check

A separate sampling check compares the confidence-interval half-width obtained from the project's
standard 50-household sample against a larger, 150-to-200-household check, across 24 cells and
multiple load-shape and energy metrics (144 of 144 expected rows found; full detail in the
Supplementary Information, Figure [R7-n200-SI]). The half-width is larger at 200 households than at
150 households in all 24 of 24 tested combinations. This is a change in how the interval is computed
at each sample size, not evidence that the estimate does not settle with more households: the
200-household interval uses a parametric interval on the real full sample, while the smaller sizes
use a bootstrap of 1,000 subsamples drawn from that same 200-household set, and the two methods are
not expected to produce the same half-width even when the underlying estimate is stable. One
illustrative cell, the single-detached archetype in Montreal, shows a half-width of 2.4475 kWh at 150
households against 4.2046 kWh at 200 households for the 2022-to-2030 electricity change; this example
and the check as a whole covers Montreal only.

## 3.8 Robustness of model selection and intervals

**Model selection.** Four candidate models clear all four selection checks at their original
thresholds; the model used throughout this paper is the candidate with the best combined score among
the four that passed all checks. Its own scores are an activity Jensen-Shannon divergence of 0.0191, an at-home
root-mean-square error of 4.57 percentage points, a spousal co-presence gap of negative 2.03
percentage points, and a composite score of 0.6355 (Supplementary Information Table
[R8-modelcard-SI]). A threshold-sensitivity check, varying each of the four check thresholds
individually by 10 percent and then by 20 percent, finds that the selected model changes in 2 of 21
tested scenarios (both a 20 percent tightening of the at-home threshold), where selection instead
falls to a different candidate with only one of four to six candidates passing; in the remaining 19
of 21 scenarios the selected model stays eligible and is still chosen. Selection is therefore not
sensitive to moderate changes in three of the four thresholds, and sensitive to the fourth only at
the most aggressive tightening tested (Supplementary Information Figure [R8-threshold-SI]). Two of
the four thresholds were set to match values already achieved by an earlier baseline version of the
model, one threshold has no stated independent rationale, and one check was tightened during
development from 10 to 5 percentage points with no stated reason; this threshold provenance is
reported as a stated limitation of the selection procedure, not as an error in the chosen model.

**Clustering-aware intervals.** Because households in this study share a city and an archetype, a
resampling method that accounts for that clustering (a cell-level cluster bootstrap) was compared
against a plain pooled interval that ignores it, for the two shape metrics used in Section 3.4. For
midday share, the cluster-aware interval is 0.00243 wide against 0.00174 for the plain interval,
about 40 percent wider, a real and material effect of clustering; the interval used in Section 3.4 is
this wider, cluster-aware one. For load factor, the cluster-aware interval is 0.00161 wide against
0.00165 for the plain interval, about 2 percent narrower, a negligible difference within Monte Carlo
noise. Both methods keep both metrics' intervals on the same side of zero, so no conclusion in this
paper flips depending on which interval is used, but the midday-share result shows that ignoring
household clustering can understate uncertainty for some metrics and not for others (Supplementary
Information Table [R9-clustering-SI]).

---

## Number trace table

| Value as written | Sheet row (R#, quantity) | File |
|---|---|---|
| 144,465 households | R1, stock frame | `T76/logs/t76_run_meta.json` |
| 47.8 percent (2022 baseline, weekday hour 12) | R1, at-home fraction 2022 baseline | `t76_run_meta.json`; `fig01_athome_by_hour.csv` |
| 50.1 percent (2030 main/persist) | R1, at-home fraction 2030 main/persist | same files |
| 47.8 percent (2030 null control) | R1, at-home fraction 2030 null | same files |
| 46.2 percent (2030 S-Partial) | R1, at-home fraction 2030 S-Partial | same files |
| 42.3 percent (2030 S-None) | R1, at-home fraction 2030 S-None | same files |
| 1,200 / 1,198 / 1,200 / 1,199 households; 1,198 common | R2, household basis per arm | `T69/out/cross_scenario_common_basis.csv` |
| 0.1225 percent [-0.1480, -0.0964] (S-None Facility) | R2, S-None Electricity:Facility change | `T69/out/S-None/enduse_change_2022_2030.csv` |
| 0.0117 percent [-0.0065, +0.0351] (S-Partial Facility) | R2, S-Partial Electricity:Facility change | `T69/out/S-Partial/enduse_change_2022_2030.csv` |
| 0.4408 percent [-0.4668, -0.4136] (S-Revert-std Facility) | R2, S-Revert-std Electricity:Facility change | `T69/out/S-Revert-std/enduse_change_2022_2030.csv` |
| 0.0 percent [0.0, 0.0] (fan, every arm) | R2, all 8 end-use meters x 3 arms | `T69/out/{S-None,S-Partial,S-Revert-std}/enduse_change_2022_2030.csv` |
| -0.127 pp [-0.307, +0.061] (S-None midday_share, from -0.001273 [-0.003070, +0.000615]) | R2, S-None midday_share change | `T69/out/S-None/enduse_change_2022_2030.csv` |
| 0.026 pp [-0.042, +0.092] (S-Partial load_factor, from 0.000257 [-0.000418, +0.000917]) | R2, S-Partial load_factor change | `T69/out/S-Partial/enduse_change_2022_2030.csv` |
| -1.383 pp [-1.610, -1.138] (S-Revert-std midday_share, from -0.01383 [-0.01610, -0.01138]) | R2, S-Revert-std midday_share change | `T69/out/S-Revert-std/enduse_change_2022_2030.csv` |
| -1.365 pp [-1.475, -1.253] (S-Revert-std load_factor, from -0.01365 [-0.01475, -0.01253]) | R2, S-Revert-std load_factor change | `T69/out/S-Revert-std/enduse_change_2022_2030.csv` |
| 0.1209 percent [0.0981, 0.1407] (Facility, S-Full) | R3, Electricity:Facility stock-weighted change | `T68/out/enduse_change_2022_2030.csv` |
| 117,942.5 kWh (2022) / 118,049.8 kWh (2030); 1,200 households, 300/archetype | R3, whole-building annual kWh levels | `T71/out/fig02_annual_by_enduse.csv` |
| 0.0157 percent [-0.0274, -0.0043] (interior lights) | R3, interior lights change | `T68/out/enduse_change_2022_2030.csv` |
| 0.0066 percent [-0.0119, -0.0012] (interior equipment) | R3, interior equipment change | same file |
| 0.0 percent [0.0, 0.0] (fan, S-Full) | R3, fan change | same file |
| 0.2905 percent [-0.4049, -0.1746] (heating) | R3, heating change | same file |
| 0.5947 percent [0.5235, 0.6523] (cooling) | R3, cooling change | same file |
| 0.5806 percent [0.3419, 0.7845] (water systems) | R3, water systems change | same file |
| 0.3578 percent [0.2863, 0.4166] (HVAC/DHW electricity) | R3, HVAC+DHW electricity change | same file |
| 1,062.7 -> 1,062.6 kWh/dwelling/yr (lights) | R3, per-dwelling stock-weighted kWh | `T71/out/fig02_annual_by_enduse.csv` |
| 3,075.5 -> 3,075.3 kWh/dwelling/yr (equipment) | R3, per-dwelling stock-weighted kWh | same file |
| 48 of 48 cells pass (corrected A5) | Also-list, SHEU row; header restriction (A5) | `T66/out` corrected `step9_validate_full_corrected.py` (via sheet Also-list) |
| 12 of 48 (original A5, control only) | Also-list, SHEU row; header restriction (A5) | original `step9_validate_full.py` (via sheet Also-list) |
| plus or minus 15 percent (A5 band, report-only) | (ds) Ruling 2, A5 definition (not a sheet row; band wording per task instruction) | `impl/2026-09-17_T48_A5_A6_fullgrid.md:17` |
| 0.49 pp [0.41, 0.57] (load factor, from 0.004943 [0.004128, 0.005743]) | R4, load factor stock-weighted change | `T71/out/fig04_peak_loadfactor_ramp_ci.csv` |
| 0.73 pp [0.62, 0.86] (midday share, cluster-aware, from 0.0073235 [0.006160, 0.008593]) | R4, midday share change (cluster-aware) | `manuscript/draft_SI_clustering_ci.md`; `T67/out/real_correcteddata/ci_reproduction_t67.csv` |
| 47.207 -> 46.332 kW (peak demand) | R4, peak demand, no interval | `T71/out/fig04_peak_loadfactor_ramp_ci.csv` |
| 7.852 -> 7.768 kW (evening ramp) | R4, evening ramp, no interval | same file |
| hour 17 max (S-Full, S-Partial, S-None); hour 18 max (S-Revert-std) | (ds) Ruling 3(a); R4 intraday load shape row | `impl/T71_out/fig03_intraday_load_shape.csv`; hour convention cross-checked in `impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md` (manager collection, grep of `T68/out/enduse_hourly_profile.csv` at hour 17) |
| 1,198 households (fig03 basis) | R4, intraday load shape row | `T71/out/fig03_intraday_load_shape.csv` |
| 192 cells, 0 NOT_EVALUABLE (heatmap) | R4, end-use x hour heatmap row | `T71/out/fig05_enduse_hour_diff.csv` |
| 1,104 rows (850 quotable / 254 NOT_EVALUABLE) | R5, comparison table row | `T77/out/fig06_comparison_table.csv` |
| 8,225.56 vs 8,951.40 kWh, delta 725.84 kWh | R5, example row | same file |
| 3.493 h vs 0.084 h (2022); 3.255 h vs 0.053 h (2030) | R5, household peak-hour spread | `T77/out/household_peak_spread_both_arms.csv` |
| 15.05-16.78 h (2022); 15.24-16.62 h (2030), SingleD range | R5, circular mean and morning-leaning share | `T77/out/fig06_comparison_table.csv` |
| 0.4680 vs 0.4305, diff 0.0376 (load_factor) | R6, Toronto shoulder weekday row | `T73/out/sim_vs_measured_toronto_2022_shape_rebuilt.csv` |
| 0.3787 vs 0.3513 (midday_share) | R6, same row group | same file |
| 2.1367 vs 2.3231 (peak_to_avg) | R6, same row group | same file |
| 17.0 vs 18.69 (peak hour) | R6, same row group | same file |
| 12 period/day-type groups | R6, summer/winter equivalents row | same file |
| 2.006 vs 1.617 (max_kwh_per_premise, not comparable) | R6, max_kwh_per_premise row | same file |
| 1.0075 / 0.9997 / 1.0017 / 1.0072 (rebuild-vs-old ratio) | R6, sanity ratio row | `T73/out/t70_run_meta.json` |
| 8,225.56 kWh/dwelling/yr (SingleD only) | R6, per-dwelling Facility kWh row; (ds) Ruling 1 | `T73/out/t70_run_meta.json` |
| 24 of 24 combinations, half-width larger at N=200 | R7, N=200 vs N=150 row | `T75/logs/t75_run_meta.json` |
| 2.4475 kWh (N=150) vs 4.2046 kWh (N=200), Montreal SingleD | R7, example row | same file |
| 144/144 rows found | R7, row-count control row | same file |
| 4 candidates (J3, J5_X1, J5_X2, J5_B) | R8, candidates clearing all 4 gates | `T74/out/figures/fig09_threshold_sensitivity.csv`; `manuscript/draft_SI_model_selection.md` |
| act JS 0.0191; AT_HOME RMS 4.57 pp; Spouse gap -2.03 pp; composite 0.6355 | R8, J3 gate scores | `manuscript/draft_SI_model_selection.md` |
| 2 of 21 scenarios flip; 19 of 21 unchanged | R8, threshold-sensitivity result | `T74/out/figures/fig09_threshold_sensitivity.csv`; `run_meta.json` |
| threshold provenance description | R8, threshold provenance row | `manuscript/draft_SI_model_selection.md` |
| 0.00174 vs 0.00243 (midday share widths, about 40% wider) | R9, midday share width comparison | `manuscript/draft_SI_clustering_ci.md` |
| 0.00165 vs 0.00161 (load factor widths, about 2% narrower) | R9, load factor width comparison | `manuscript/draft_SI_clustering_ci.md` |

## Figure and table references used

| Placeholder tag | WP11 sheet numbering | Content | Source file(s) |
|---|---|---|---|
| Figure [R1-athome] | WP11 Figure 1 | 24-hour at-home fraction by hour, 2022 baseline + four 2030 variants | `fig01_athome_by_hour.csv` |
| Figure [R3-enduse] | WP11 Figure 2 | Annual energy by end use, whole-building (Panel A) and per-dwelling equip/lights (Panel B) | `fig02_annual_by_enduse.csv` |
| Figure [R4-loadshape] | WP11 Figure 3 | Intraday weekday load shape, 2030, four scenario arms | `fig03_intraday_load_shape.csv` |
| Figure [R4-peak-lf-ramp] | WP11 Figure 4 | Peak, load factor (with CI), evening ramp, 2022 vs 2030 | `fig04_peak_loadfactor_ramp_ci.csv` |
| Figure [R4-heatmap] | WP11 Figure 5 | End-use x hour percent-change heatmap | `fig05_enduse_hour_diff.csv` |
| Figure [R5-comparison] | WP11 Figure 6 | Full model vs average-profile arm: comparison table + household peak-hour spread | `fig06_comparison_table.csv`, `household_peak_spread_both_arms.csv` |
| Figure [R6-measured] | WP11 Figure 7 | Simulated vs measured Toronto/Ontario 2022 load-shape metrics | `sim_vs_measured_toronto_2022_shape_rebuilt.csv` |
| SI Figure [R7-n200-SI] | WP11 Figure 8 (SI) | N=200 vs N=150 convergence check | `t75_run_meta.json`, `T28/out/t28_b4_convergence.csv` |
| SI Figure [R8-threshold-SI] | WP11 Figure 9 (SI) | Model-selection threshold-sensitivity | `fig09_threshold_sensitivity.csv` |
| SI Table [R8-modelcard-SI] | SI Table B1 | J3 gate scores | `manuscript/draft_SI_model_selection.md` |
| SI Table [R9-clustering-SI] | SI Table S.10 | Clustering-aware vs plain interval widths | `manuscript/draft_SI_clustering_ci.md` |

Note: every figure number above is a placeholder tag, not a manuscript figure number, per the task
doc's own instruction (manuscript Figure 1 is the workflow diagram; the WP11 sheet's own Figure 1-9
numbering is one position behind wherever the workflow diagram is inserted).

## Placeholders left

- `[NUMBER FROM T80: weighted at-home share, 2005/2010/2015 cycles]` -- Section 3.1.
- `[NUMBER FROM T80: 2015-to-2022 at-home break, standardized]` -- Section 3.1.
- `[NUMBER NEEDED: EUI]` -- Section 3.3 (no rebuilt energy-use-intensity figure exists per (ds) Ruling
  2; the archived Table 5 EUI values are not carried forward).

## Reviewer items touched

- 3.1: D16 (re-check occupancy numbers against current files), R3-1 (rebuild on corrected household
  data).
- 3.2: M5, D17, R3-2, R3-4 (more than one 2030 work-from-home path, in the main body), R2-3
  ("scenario-based projection" wording used throughout, not "forecast"), R3-3 (non-causal wording).
- 3.3: M3 (measure the SHEU gap end-use by end-use, stop calling the match "plausible" without
  qualification), R2-6 / Q14 (SHEU agreement is a fitted-target check, not independent validation),
  R3-5 (tuning-fit half of the split).
- 3.4: M4, D15, D19 (load shape, ramp, peak, load factor made prominent and separated), D18 (end-use
  by hour breakdown).
- 3.5: M1 (comparison against an average-profile arm on the same households).
- 3.6: R2-2 (measured Toronto/Ontario check), R3-5 (independent-evidence half of the split).
- 3.7: M2d (sample-size check moved into Results with SI detail).
- 3.8: M2c (gate scores and threshold detail moved to SI, only a summary kept in the main text).
- Not touched by this draft: Q13 (EUI vs SHEU wording in the Conclusion) -- no EUI number exists in
  the rebuild, so this row has nothing to reconcile yet; left for whoever drafts the Conclusion once
  (or if) an EUI figure becomes available.

## Open for the manager

1. (ds) Ruling 3(c) allows "per-cell household circular-mean ranges from T77's table across ALL
   archetypes" as a peak-timing statement. The number sheet's own R5 row only carries this range for
   the single-detached archetype ("SingleD only shown"). This draft quotes only the single-detached
   range and says so explicitly (Section 3.5); a fuller draft would need someone to read the other
   three archetypes' rows out of `fig06_comparison_table.csv` and add them, or a ruling that the
   single-detached range alone satisfies Ruling 3(c).
2. The hour-17-vs-hour-18 clock-time claim in Section 3.4 rests on the T71 manager collection's
   cross-check (a direct grep of the hourly-profile file at "hour 17" matching the plotted value),
   not on an explicit statement in any doc that the hour column is 0-23 clock-aligned rather than
   1-24 position-indexed. Worded cautiously in this draft ("the late-afternoon hour beginning around
   5 p.m."); flag if a firmer statement is needed.
3. All figure references in this draft are bracket placeholders (`[R1-athome]` etc.), per the task
   doc's own instruction, since the manuscript's Figure 1 (workflow diagram) shifts every WP11 figure
   number by one position. These need real Figure N numbers once the final figure list and order is
   fixed.
4. The A5 "48/48 PASS" (corrected validator) versus the archived "48/48 within plus or minus 2.7
   percent" (old SHEU calibration claim) statistic-equivalence question, flagged by the number sheet
   itself, is not resolved in this draft; Section 3.3 only states the corrected 48/48 result in A5's
   own words, per (ds) Ruling 2, and does not claim it is the same statistic as the old figure.
5. The WP5 per-dwelling divisor conflict for OtherDwelling/MidRise/HighRise (flagged in the number
   sheet's R6 row and closed for SingleD only by (ds) Ruling 1) means Section 3.6 reports only a
   whole-building sanity ratio for those three archetypes, never a per-dwelling kWh figure. If the
   divisor conflict is resolved later, Section 3.6 would need a rewrite to add those three numbers.
6. Word count, number of traced numbers, and placeholder count are reported in the summary line of
   this task's final report; not repeated here.

## WHAT I DID NOT VERIFY

- Did not independently re-derive any number in this draft from a raw cluster or local CSV file;
  every value is copied, and every percentage-point conversion from an absolute fraction (for
  example 0.004943 to 0.49 pp) is a straightforward unit conversion of a sheet value, not a new
  statistical computation, per the task's "read a value" allowance.
- Did not open `T66/logs/t66_report.txt`, `T48/logs/` outputs, or any other raw cluster file; the A5
  band description ("plus or minus 15 percent, report-only") and the A6 definition were read only
  from the two named local task docs (`2026-09-20_T66_A5_per_unit_correction_fix.md`,
  `2026-09-17_T48_A5_A6_fullgrid.md`), as the task doc instructed, and A6 itself is not quoted
  anywhere in this draft (no rebuilt A6 number exists on the number sheet).
- Did not read `manuscript/prep/response_map.md` in full; only grepped it for row IDs and one-line
  descriptions to fill "Reviewer items touched." Some matching lines were truncated in the grep
  output ("[Omitted long matching line]") and were not individually opened.
- Did not read `manuscript/draft_S2_framework.md`'s trace table entries beyond what was needed to
  confirm section numbers, equation numbers for load factor/midday share/peak hour/paired-CI, and the
  finding that no ramp-metric equation exists in the code that document traced; Section 3.4's mention
  of "evening ramp" is therefore not tied to any equation number, deliberately.
- Did not view any figure PNG by eye (none exist yet for this draft; all figure blocks are text
  placeholders marked "[image to be inserted from the WP11 output]").
- Did not check this draft's prose against Applied Energy's own house style guide (word limits by
  section, exact caption format, reference style) beyond the plain-language and no-symbol rules given
  in the task doc itself.
- Did not verify the actual rendered word count by any means other than a plain word count of this
  file (reported in the final summary); did not distinguish body-text words from caption or heading
  words in that count.

## Manager addendum (entry (dv)): numbers added to 3.1 after T80

| Value as written | Source |
|---|---|
| 74.4 percent (2022 weekday whole-day at-home share) | `impl/T80_out/athome_daily_mean.csv` row `2022_baseline,Weekday` (0.74425) |
| 1.49 / negative 0.85 / negative 3.21 pp (2030 steps) | same file, `t76_copy_2030_main_persist` 0.75910, `_lambda_0.5_partial` 0.73570, `_lambda_0.0_revert` 0.71217, minus 0.74425; revert step reproduces T26 SC3's -3.2081 pp |
| 4.73 pp and 7.67 pp (weekday jump over 2005-2015 trend; standardized) | `impl/2026-09-15_T26_wp2_scenario_builds.md:272, 293-294` (`slurm_1328377_0.out:192-195`, `t26_std_jump_sensitivity.json`) |
| (69.0 / 68.3 / 67.1 percent, 2005/2010/2015 household schedules) | NOT USED in prose: opposite direction to the respondent trend the scenarios use; see plan (dv) item 41 |
