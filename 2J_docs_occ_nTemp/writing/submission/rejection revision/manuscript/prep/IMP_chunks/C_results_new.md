# 3. Results

The subsections below trace one path through the pipeline. Sections 3.1 and 3.2 show how the
at-home pattern itself differs between 2022 and three stated 2030 assumptions. Section 3.3 shows
what this does to annual electricity by end use. Section 3.4 shows how it reshapes the daily load
curve. Section 3.5 shows what a simplified average-profile scheduling method would have shown
instead on the same households. Section 3.6 compares the simulated load shape with a year of real
measured data for one city. Sections 3.7 and 3.8 report two robustness checks briefly, with full
detail in the Supplementary Information.

## 3.1 Occupancy change

The at-home occupancy series is built on a stock frame of 144,465 census households (Sections 2.3
and 2.5). It covers the 2022 survey cycle directly. It also covers four 2030 variants built from the
scenario construction of Section 2.5. The values below are read at one representative point, a
weekday at noon (hour 12).

At weekday noon in 2022, 47.8 percent of the stock is at home. For 2030, four variants were run side
by side rather than a single projection: three scenarios and one control. The main scenario assumes
the pandemic-era rise in at-home behaviour persists in full. Under it, the noon share moves from 47.8
percent to 50.1 percent. The partial-persistence scenario assumes half of that shift has faded by
2030 (46.2 percent). The full-reversion scenario assumes the shift has faded completely, so 2030 sits
back on the pre-pandemic trend (42.3 percent). The no-change control reproduces the 2022 pattern
unmodified (47.8 percent). This value is identical to the 2022 value to the last reported digit. It is
an acceptance check on the scenario-construction code, not a scenario in its own right. These four
numbers describe the household schedules built under each stated persistence assumption (Section
2.5). They are a designed comparison of assumptions. They do not claim that any single one of them is
what will actually occur in 2030.

Figure 6 shows the full 24-hour series by hour of day, for weekdays and weekends. It covers the 2022
stock baseline, the three 2030 scenarios (main persistence, partial persistence and full reversion)
and the no-change control. All lines use the 144,465-household stock frame. The no-change control
coincides with the 2022 line by construction.

![](../impl/T94_out/fig02_athome_by_hour.png){width=16cm}

**Figure 6.** At-home fraction by hour of day, weekday and weekend, 2022 and 2030.

Averaged over the whole weekday, 74.4 percent of household-hours are spent at home in 2022. The three
2030 scenarios move this whole-day weekday share by 1.49 percentage points (main scenario), negative
0.85 percentage points (partial persistence) and negative 3.21 percentage points (full reversion).
These are the designed steps from 2022, not attained targets. The scenarios carry forward or remove a
pandemic-era break. This break is measured on the survey respondents themselves. In 2022, the
national weekday at-home rate sits 4.73 percentage points above where the 2005 to 2015 trend would
have placed it. The gap is 7.67 percentage points when every survey cycle is first reweighted to the
housing stock's age, sex and labour-force mix. This standardized measure is the sensitivity behind
the standardized-reversion variant. The main scenario keeps that break and adds the 2005 to 2015
trend carried forward. This is why its step (1.49 percentage points) is positive. The full-reversion
scenario removes the break and keeps the trend. This is why its step is negative.

## 3.2 The 2030 scenarios

Three named 2030 scenarios, plus one standardized sensitivity variant, are compared on the
households they share. The four scenario arms were built and sampled independently. They do not all
cover the same households. The main scenario has 1,200 households, the full-reversion scenario
1,198, the partial-persistence scenario 1,200 and the standardized-reversion variant 1,199. Every
cross-scenario comparison in this subsection, and in the scenario load shapes of Section 3.4, uses
only the 1,198 households present in all four arms. All numbers below refer to this common set.

Under the full-reversion scenario, stock-weighted whole-building electricity use falls by 0.1225
percent from 2022 to 2030 (95 percent confidence interval negative 0.1480 to negative 0.0964
percent). This is a real change, since the interval excludes zero. Under the partial-persistence
scenario, the equivalent change is 0.0117 percent, with a confidence interval of negative 0.0065 to
0.0351 percent. Because that interval contains zero, this is no detectable change at this sample
size, not an increase. The standardized-reversion variant recomputes the trend and the pandemic-era
jump after reweighting every survey cycle to the housing stock's age, sex and labour-force mix. Under
this variant, whole-building electricity falls by 0.4408 percent (95 percent confidence interval
negative 0.4668 to negative 0.4136 percent). This is the largest change of the three scenario arms.
Of the eight end-use meters, fan electricity shows no change in any of the three arms (0.0 percent,
interval 0.0 to 0.0).

The same pattern holds for the load-shape metrics. Under the full-reversion scenario, midday energy
share changes by negative 0.127 percentage points (95 percent confidence interval negative 0.307 to
positive 0.061 percentage points). This is no detectable change at this sample size. Under the
partial-persistence scenario, load factor changes by 0.026 percentage points (95 percent confidence
interval negative 0.042 to positive 0.092 percentage points). This is also no detectable change.
Under the standardized-reversion variant, both shape metrics show a change that excludes zero. Midday
share falls by 1.383 percentage points (95 percent confidence interval negative 1.610 to negative
1.138). Load factor falls by 1.365 percentage points (95 percent confidence interval negative 1.475
to negative 1.253). This is the most clearly separable shape change among the three scenario arms.

## 3.3 Annual energy by end use

Under the main scenario, annual electricity is nearly flat. Whole-building electricity use, weighted
to the national housing stock, rises by 0.1209 percent from 2022 to 2030 (95 percent confidence
interval 0.0981 to 0.1407 percent). This is a small but real change, since the interval excludes
zero. Underneath that near-flat total, the mix of end uses moves more than the total does. So does
the timing of demand (Section 3.4). The rest of this Results section documents that pattern. Per
simulated building, weighted to the national stock, whole-building electricity use is 117,942.5 kWh
in 2022 and 118,049.8 kWh in 2030. These values come from 1,200 simulated buildings, 300 per
archetype. This level mixes single homes and multi-unit buildings. It is therefore a stock-weighted
building average, not a per-dwelling figure.

Among the individual meters, interior lighting falls by 0.0157 percent (95 percent confidence
interval negative 0.0274 to negative 0.0043 percent). Interior equipment falls by 0.0066 percent (95
percent confidence interval negative 0.0119 to negative 0.0012 percent). Both intervals exclude zero.
Fan electricity shows no change (0.0 percent, interval 0.0 to 0.0). Heating energy transfer falls by
0.2905 percent (95 percent confidence interval negative 0.4049 to negative 0.1746 percent). Cooling
energy transfer rises by 0.5947 percent (95 percent confidence interval 0.5235 to 0.6523 percent).
Water-systems energy transfer rises by 0.5806 percent (95 percent confidence interval 0.3419 to
0.7845 percent). The remaining HVAC-and-domestic-hot-water electricity rises by 0.3578 percent (95
percent confidence interval 0.2863 to 0.4166 percent). These three rises all exclude zero.

Heating, cooling, water systems, and the HVAC and domestic-hot-water remainder are reported only at
the whole-building level. No per-dwelling divisor exists for these meters. Per-dwelling annual energy
is reported only for equipment and lighting, the two meters with a defined per-dwelling divisor.
Stock-weighted interior lighting falls from 1,062.7 to 1,062.6 kWh per dwelling per year. Interior
equipment falls from 3,075.5 to 3,075.3 kWh per dwelling per year. These are levels, not a
bootstrapped change. Figure 7 shows these annual results for the main scenario, 2022 versus 2030.
Panel A shows stock-weighted whole-building annual energy by end use for all eight meters. Panel B
shows stock-weighted per-dwelling annual energy for interior equipment and interior lighting only.

![](../impl/T94_out/fig03_annual_by_enduse.png){width=16cm}

**Figure 7.** Annual energy by end use, 2022 versus 2030, main scenario.

As an additional check, simulated equipment and lighting energy were compared against their fitted
SHEU calibration target. The check compares simulated and survey end-use totals. It is descriptive,
with a band of plus or minus 15 percent around the fitted target. It is not an independent validation
against outside data. All 48 archetype-by-city-by-year cells pass this check. Energy use intensity is
taken as total site energy of all fuels divided by net conditioned floor area. It is summed over the
50 simulated buildings of each archetype in all six cities, giving 300 simulations per archetype and
year. In 2022, it is 116.0 kWh/m² for single-detached houses, 100.5 kWh/m² for other dwellings, 107.8
kWh/m² for mid-rise and 78.6 kWh/m² for high-rise buildings. The 2030 main-scenario values are 116.3,
100.6, 107.8 and 78.6 kWh/m². These are simulated levels, not a tested change.

## 3.4 Load shape: peak, load factor, midday share, ramp

Figure 8 shows the stock-average weekday load shape for 2030 under all four scenario arms, on the
1,198 households common to all four. The curve reaches its maximum at hour 17 of the day under the
main scenario, the partial-persistence scenario and the full-reversion scenario. It peaks at hour 18
under the standardized-reversion variant. Hour 17 uses the same clock-aligned hour numbering as the
rest of the framework (the four-hour roll of Section 2.3). It corresponds to the late-afternoon hour
beginning around 5 p.m. The standardized-reversion variant also shows a visibly lower midday load and
a higher evening peak than the other three arms. Sections 3.5 and 3.6 report two other kinds of
peak-timing evidence. These are household-level circular-mean ranges from the full model, and a
measured-data comparison for one city.

![](../impl/T94_out/fig04_intraday_load_shape.png){width=16cm}

**Figure 8.** Intraday weekday load shape in 2030 under all four scenario arms.

Load factor is the ratio of the year's mean hourly load to its single annual peak hourly load
(Section 2.6). Under the main scenario, it rises by 0.49 percentage points from 2022 to 2030 (95
percent confidence interval 0.41 to 0.57 percentage points). This change excludes zero. Midday share
is the fraction of annual energy delivered between 09:00 and 17:00. It rises by 0.73 percentage
points (95 percent confidence interval 0.62 to 0.86 percentage points). This interval accounts for
households sharing a city and an archetype. Section 3.8 reports how much wider this interval is than
one that ignores that clustering, and why the wider one is used here. Both changes exclude zero.

Peak demand and evening ramp are point estimates. Stock-weighted peak demand falls from 47.207 kW in
2022 to 46.332 kW in 2030. The stock-weighted evening ramp falls from 7.852 kW to 7.768 kW. Figure 9
shows peak demand, evening ramp and load factor for the main scenario, 2022 versus 2030, all
stock-weighted. The error bar on load factor is the 95 percent confidence interval on the 2022 to
2030 change.

![](../impl/T94_out/fig05_peak_loadfactor_ramp.png){width=16cm}

**Figure 9.** Peak demand, evening ramp and load factor, 2022 versus 2030, main scenario.

Figure 10 shows the percent change for each of the eight end-use meters in each hour of the day. It
covers 2022 to 2030 under the main scenario, stock-weighted and averaged over all days of the year.
For whole-building electricity, consumption falls slightly in the overnight and late-evening hours.
It rises through the daytime hours, consistent with more of the stock being home during the day.
These hourly values are point estimates. They are read as a pattern rather than as individual
changes.

![](../impl/T94_out/fig06_enduse_hour_change.png){width=16cm}

**Figure 10.** Percent change by end use and hour of day, 2022 to 2030.

## 3.5 Comparison with an average-profile model

This comparison isolates what the household-level diary-based schedule contributes over a simpler
description of occupancy. The full model, used throughout Sections 3.1 to 3.4, was compared against
an average-profile arm. This arm keeps each household's own calibrated design power. It replaces the
household's individual schedule with the average schedule of its own archetype-and-city cell
(Section 2.6). A separate fixed-schedule arm is not part of this comparison, since it is not a
home-for-home comparison.

One illustrative cell is the single-detached archetype in Toronto in 2022. Whole-building electricity
use is 8,225.56 kWh under the full model and 8,951.40 kWh under the average-profile arm. This is a
difference of 725.84 kWh for this single cell. The two arms differ far more in household-to-household
diversity of peak timing than in this annual total. This diversity is measured as household-level
dispersion in peak hour. It uses a circular standard deviation, since peak hour wraps at midnight
(Section 2.6). For the same cell, it is 3.493 hours under the full model against 0.084 hours under
the average-profile arm in 2022. In 2030, it is 3.255 hours against 0.053 hours. The average-profile
arm thus collapses household-to-household diversity in peak timing almost to zero. This follows
directly from assigning every sampled household the same schedule by construction. It is not a data
finding. Across the six simulated cities, the full model's household-level circular mean peak hour
for the single-detached archetype ranges from 15.05 to 16.78 hours in 2022. It ranges from 15.24 to
16.62 hours in 2030.

Figure 11 shows the same comparison stock-weighted over all 24 cells, for 2022 and 2030. It covers
annual whole-building electricity, peak demand, load factor, midday share, evening ramp and the
household-to-household spread of peak hour. The error bars on load factor and midday share are 95
percent confidence intervals on the paired difference between the two arms.

![](../impl/T94_out/fig07_full_vs_average_profile.png){width=16cm}

**Figure 11.** Full model versus average-profile arm, stock-weighted, 2022 and 2030.

## 3.6 Independent measured check, Toronto/Ontario 2022

The simulated Toronto load shape was compared against a year of real measured hourly residential
electricity data for Toronto, and for Ontario as a whole, in 2022. Table 1 names the measured data
source. Section 2.6 defines load factor and midday share. Both sides use the same 09:00 to 17:00
midday window. On a shoulder-season weekday, the simulated load factor is 0.4680 against a measured
Toronto value of 0.4305, a difference of 0.0376. Simulated midday share is 0.3787 against a measured
0.3513. Simulated peak-to-average ratio is 2.1367 against a measured 2.3231. The simulated mean peak
hour is 17.0 against a measured 18.69, both on an hour-ending clock. The Ontario-wide measured series
gives the same reading for this period and day type (peak hour 18.42, peak-to-average ratio 2.2002).
The other Toronto period and day-type combinations cover winter, summer and the full year, and
weekends and holidays. They are read the same way. Figure 12 shows all twelve period and day-type
groups for four metrics: load factor, peak-to-average ratio, midday share and mean peak hour. All
values in this comparison are point statistics.

![](../impl/T94_out/fig08_measured_vs_simulated.png){width=16cm}

**Figure 12.** Simulated versus measured load-shape metrics, Toronto, 2022.

Two further checks support the plausibility of these results. First, the Toronto 2022 annual
whole-building electricity of the present simulations was compared with the authors' earlier
simulation campaign on the same Toronto archetypes. That campaign used an earlier version of the
occupancy model. The change of occupancy model barely moved the annual total. The ratio of present
to earlier is 1.0075 for single-detached, 0.9997 for other-dwelling, 1.0017 for mid-rise and 1.0072
for high-rise. All four are within 0.8 percent of one. Second, the single-detached archetype holds
one dwelling per building. It uses 8,225.56 kWh of whole-building electricity per dwelling in 2022.
The other three archetypes hold several dwellings per building. They are compared through the
whole-building ratios above.

## 3.7 Sample-size check

A separate sampling check compares the confidence-interval half-width from the study's standard
50-household sample against larger samples of 150 and 200 households. It covers the four Montreal
archetype cells and six load-shape and energy metrics, giving 24 cell-by-metric combinations. Full
detail is in the Supplementary Information (Figure S1). The half-width is larger at 200 households
than at 150 households in all 24 of 24 tested combinations. This reflects a change in how the
interval is computed at each sample size. It is not evidence that the estimate does not settle with
more households. The 200-household interval uses a parametric interval on the real full sample. The
smaller sizes use a bootstrap of 1,000 subsamples drawn from that same 200-household set. The two
methods are not expected to produce the same half-width, even when the underlying estimate is
stable. One illustrative cell is the single-detached archetype in Montreal. For the 2022-to-2030
electricity change, it shows a half-width of 2.4475 kWh at 150 households against 4.2046 kWh at 200
households. The check covers Montreal only.

## 3.8 Robustness of model selection and intervals

**Model selection.** Four candidate models clear all four selection checks at their original
thresholds. The model used throughout this paper is the candidate with the best combined score among
these four. Its activity Jensen-Shannon divergence is 0.0191. Its at-home root-mean-square error is
4.57 percentage points. Its spousal co-presence gap is negative 2.03 percentage points. Its composite
score is 0.6355 (Supplementary Information Table S1). A threshold-sensitivity check varies each of
the four check thresholds individually, first by 10 percent and then by 20 percent. The selected
model changes in 2 of 21 tested scenarios. Both are a 20 percent tightening of the at-home
threshold. In these two, only one other candidate meets all four checks, and it is selected instead.
In the remaining 19 of 21 scenarios, the selected model stays eligible and is still chosen. Selection
is therefore not sensitive to moderate changes in three of the four thresholds. It is sensitive to
the fourth only at the most aggressive tightening tested (Supplementary Information Figure S2). The
thresholds were carried over from an earlier baseline version of the model. They were not derived
from an independent basis such as survey sampling error. This is a limitation of the selection
procedure (Supplementary Information Section S2).

**Clustering-aware intervals.** Households in this study share a city and an archetype. A resampling
method that accounts for that clustering (a cell-level cluster bootstrap) was therefore compared
against a plain pooled interval that ignores it. The comparison covers the two shape metrics used in
Section 3.4. For midday share, the cluster-aware interval is 0.00243 wide against 0.00174 for the
plain interval. It is about 40 percent wider, a real and material effect of clustering. The interval
used in Section 3.4 is this wider, cluster-aware one. For load factor, the cluster-aware interval is
0.00161 wide against 0.00165 for the plain interval. It is about 2 percent narrower, a negligible
difference within Monte Carlo noise. Both methods keep both metrics' intervals on the same side of
zero. No conclusion in this paper therefore flips depending on which interval is used. However, the
midday-share result shows that ignoring household clustering can understate uncertainty for some
metrics and not for others (Supplementary Information Table S3).
