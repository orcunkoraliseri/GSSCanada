# 3. Results

The subsections below trace one path through the pipeline: how the at-home pattern itself
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
2.

At weekday noon in 2022, 47.8 percent of the stock is at home. For 2030, four variants were run
side by side rather than a single projection, three scenarios and one control: a main scenario that assumes the pandemic-era rise in
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

![](../impl/T94_out/fig02_athome_by_hour.png){width=16cm}

**Figure 2.** Weekday and weekend at-home
fraction by hour of day, 2022 stock baseline, three 2030 scenarios (main persistence, partial
persistence, full reversion) and a no-change control, on the 144,465-household stock frame. The
no-change control coincides with the 2022 line by construction.

## 3.2 The 2030 scenarios

Three named 2030 scenarios, plus one standardized sensitivity variant, are compared on the
households they share. The four scenario arms were built and sampled independently and do not all
cover the same households (1,200 for the main scenario, 1,198 for the full-reversion scenario, 1,200
for the partial-persistence scenario and 1,199 for the standardized-reversion variant); every
cross-scenario comparison in this subsection, and in Figure 4, uses
only the 1,198 households present in all four arms. This restriction is stated once here rather than
repeated at every number below.

Under the full-reversion scenario, stock-weighted whole-building electricity use falls
by 0.1225 percent from 2022 to 2030 (95 percent confidence interval negative 0.1480 to negative
0.0964 percent), a real change since the interval excludes zero. Under the partial-persistence
scenario, the equivalent change is 0.0117 percent with a confidence interval of
negative 0.0065 to 0.0351 percent: because that interval contains zero, this is no detectable change
at this sample size, not an increase. Under the standardized-reversion variant (built with the trend and the pandemic-era jump recomputed after reweighting every survey cycle to
the housing stock's age, sex and labour-force mix), whole-building electricity falls by 0.4408 percent (95
percent confidence interval negative 0.4668 to negative 0.4136 percent), the largest change of the
three scenario arms. Of the eight end-use meters, fan electricity shows no change in any of the
three arms (0.0 percent, interval 0.0 to 0.0).

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
more than the total does; that is the pattern the rest of this Results section documents. Per
simulated building, weighted to the national stock, whole-building electricity use is 117,942.5 kWh
in 2022 and 118,049.8 kWh in 2030, over 1,200 simulated buildings, 300 per archetype (Figure 3); this
level mixes single homes and multi-unit buildings, so it is a stock-weighted building average, not a
per-dwelling figure.

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
calibration target by comparing simulated and survey end-use totals; this is a descriptive check
with a band of plus or minus 15 percent around the fitted target, not an independent validation
against outside data. All 48 archetype-by-city-by-year cells pass this check.
Energy use intensity, taken as total site energy of all fuels divided by net conditioned floor area
and summed over the 50 simulated buildings of each archetype in all six cities (300 simulations per
archetype and year), is 116.0 kWh/m² for single-detached houses, 100.5 kWh/m² for other dwellings,
107.8 kWh/m² for mid-rise and 78.6 kWh/m² for high-rise buildings in 2022. The 2030 main-scenario
values are 116.3, 100.6, 107.8 and 78.6 kWh/m²; these are simulated levels, not a tested change.

![](../impl/T94_out/fig03_annual_by_enduse.png){width=16cm}

**Figure 3.** Panel A: stock-weighted
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

Peak demand and evening ramp are point estimates: stock-weighted peak demand falls from 47.207 kW
in 2022 to 46.332 kW in 2030, and the stock-weighted evening ramp falls from 7.852 kW to 7.768 kW.

The stock-average weekday load shape for 2030 (Figure 4, the 1,198 common households)
reaches its maximum at hour 17 of the day under the main scenario, the partial-persistence scenario
and the full-reversion scenario, and at hour 18 under the standardized-reversion variant; hour 17
uses the same clock-aligned hour numbering as the rest of the framework (Section 2.5's four-hour
roll), corresponding to the late-afternoon hour beginning around 5 p.m. The standardized-reversion
variant also shows a visibly lower midday load and a higher evening peak than the other three arms.
Sections 3.5 and 3.6 report two other
kinds of peak-timing evidence: household-level circular-mean ranges from the full model, and a
measured-data comparison for one city.

Figure 6 shows the percent change for each of the eight end-use meters in each hour of the day. For
whole-building electricity, consumption falls slightly in the overnight and late-evening hours and
rises through the daytime hours, consistent with more of the stock being home during the day. These
hourly values are point estimates and are read as a pattern rather than as individual changes.

![](../impl/T94_out/fig04_intraday_load_shape.png){width=16cm}

**Figure 4.** Intraday weekday load shape,
2030, all four scenario arms, on the 1,198 households common to all four.

![](../impl/T94_out/fig05_peak_loadfactor_ramp.png){width=16cm}

**Figure 5.** Stock-weighted peak demand,
evening ramp and load factor, 2022 versus 2030, main scenario. The error bar on load factor is the 95
percent confidence interval on the 2022 to 2030 change.

![](../impl/T94_out/fig06_enduse_hour_change.png){width=16cm}

**Figure 6.** End-use by hour percent-change
heatmap, 2022 to 2030, main scenario, stock-weighted and averaged over all days of the year.

## 3.5 Comparison with an average-profile model

To isolate what the household-level diary-based schedule contributes over a simpler description of
occupancy, the full model (used throughout Sections 3.1 to 3.4) was compared against an
average-profile arm that keeps each household's own calibrated design power but replaces its
individual schedule with the average schedule of its own archetype-and-city cell (Section 2.12). A
separate fixed-schedule arm is not part of this comparison,
since it is not a home-for-home comparison.

One illustrative cell: for the single-detached archetype in Toronto in 2022, whole-building
electricity use is 8,225.56 kWh under the full model and 8,951.40 kWh under the average-profile arm,
a difference of 725.84 kWh for this single cell. The two arms differ far more in
household-to-household diversity of peak timing than in this annual total. Household-level dispersion
in peak hour (a circular standard deviation, since peak hour wraps at midnight, Section 2.10) for the
same cell is 3.493 hours under the full model against 0.084 hours under the average-profile arm in
2022, and 3.255 hours against 0.053 hours in 2030: the average-profile arm collapses household-to-
household diversity in peak timing almost to zero, which follows directly from assigning every
sampled household the same schedule by construction, not from a data finding. Across the six
simulated cities, the full model's household-level circular mean peak hour for the single-detached
archetype ranges from 15.05 to 16.78 hours in 2022 and from 15.24 to 16.62 hours in 2030. Figure 7
shows the same comparison stock-weighted over all 24 cells.

![](../impl/T94_out/fig07_full_vs_average_profile.png){width=16cm}

**Figure 7.** Full model versus
average-profile arm, stock-weighted, 2022 and 2030: annual whole-building electricity, peak demand,
load factor, midday share, evening ramp and household-to-household spread of peak hour. Error bars on
load factor and midday share are 95 percent confidence intervals on the paired difference between the
two arms.

## 3.6 Independent measured check, Toronto/Ontario 2022

The simulated Toronto load shape was compared against a year of real measured hourly residential
electricity data for Toronto, and for Ontario as a whole, in 2022 (Table 2 names the measured data
source; Section 2.10 defines load factor and midday share, and both sides use the same 09:00-17:00
midday window). On a shoulder-season weekday, the simulated load factor is 0.4680 against a measured
Toronto value of 0.4305, a difference of 0.0376. Simulated midday share is 0.3787 against a measured
0.3513; simulated peak-to-average ratio is 2.1367 against a measured 2.3231; and the simulated mean
peak hour is 17.0 against a measured 18.69, both on an hour-ending clock. The Ontario-wide measured
series gives the same reading for this period and day type (peak hour 18.42, peak-to-average ratio
2.2002). The other Toronto period and day-type combinations (winter, summer and the full year;
weekends and holidays), twelve groups in total, are read the same way and shown in full in Figure 8
rather than repeated here. All values in this comparison are point statistics.

Two further checks support the plausibility of these results. First, the Toronto 2022 annual
whole-building electricity of the present simulations was compared with the authors' earlier
simulation campaign on the same Toronto archetypes, built with an earlier version of the occupancy
model; the change of occupancy model barely moved the annual total: the ratio of present to earlier
is 1.0075 for single-detached, 0.9997 for other-dwelling, 1.0017 for mid-rise and 1.0072 for
high-rise, all within 0.8 percent of one. Second, the single-detached archetype, which holds one
dwelling per building, uses 8,225.56 kWh of whole-building electricity per dwelling in 2022; the
other three archetypes hold several dwellings per building and are compared through the
whole-building ratios above.

![](../impl/T94_out/fig08_measured_vs_simulated.png){width=16cm}

**Figure 8.** Simulated versus measured
load-shape metrics, Toronto, 2022, for twelve period and day-type groups: load factor, peak-to-average
ratio, midday share and mean peak hour.

## 3.7 Sample-size check

A separate sampling check compares the confidence-interval half-width obtained from the study's
standard 50-household sample against larger samples of 150 and 200 households, across the four Montreal
archetype cells and six load-shape and energy metrics (24 cell-by-metric combinations; full detail in the
Supplementary Information, Figure S1). The half-width is larger at 200 households than at
150 households in all 24 of 24 tested combinations. This is a change in how the interval is computed
at each sample size, not evidence that the estimate does not settle with more households: the
200-household interval uses a parametric interval on the real full sample, while the smaller sizes
use a bootstrap of 1,000 subsamples drawn from that same 200-household set, and the two methods are
not expected to produce the same half-width even when the underlying estimate is stable. One
illustrative cell, the single-detached archetype in Montreal, shows a half-width of 2.4475 kWh at 150
households against 4.2046 kWh at 200 households for the 2022-to-2030 electricity change. The check
covers Montreal only.

## 3.8 Robustness of model selection and intervals

**Model selection.** Four candidate models clear all four selection checks at their original
thresholds; the model used throughout this paper is the candidate with the best combined score among
the four that passed all checks. Its own scores are an activity Jensen-Shannon divergence of 0.0191, an at-home
root-mean-square error of 4.57 percentage points, a spousal co-presence gap of negative 2.03
percentage points, and a composite score of 0.6355 (Supplementary Information Table
S1). A threshold-sensitivity check, varying each of the four check thresholds
individually by 10 percent and then by 20 percent, finds that the selected model changes in 2 of 21
tested scenarios (both a 20 percent tightening of the at-home threshold), where only one other
candidate meets all four checks and is selected instead; in the remaining 19
of 21 scenarios the selected model stays eligible and is still chosen. Selection is therefore not
sensitive to moderate changes in three of the four thresholds, and sensitive to the fourth only at
the most aggressive tightening tested (Supplementary Information Figure S2). The thresholds were
carried over from an earlier baseline version of the model rather than derived from an independent
basis such as survey sampling error, which is a limitation of the selection procedure
(Supplementary Information Section S2).

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
Information Table S3).


