# 4. Discussion

Section 1.4 asked whether, and how, occupancy-driven change reshapes the residential load curve at
stock scale up to 2030. Under the main scenario, annual
whole-building electricity in 2030 is nearly unchanged from 2022 (Section 3.3). The timing of demand
and the mix of end uses move more than that total does. Only a change whose confidence interval
excludes zero is discussed as a change.

For grid planning, timing matters more than the annual total. Under the main scenario, midday share
rises by 0.73 percentage points and load factor by 0.49 percentage points, and both changes exclude
zero (Section 3.4). A grid operator plans for peak demand, the evening ramp and demand-response
programs from timing, not only from the annual total (Denholm et al. 2015).

The spread across the 2030 scenarios (Section 3.2) is this paper's main message about uncertainty.
Full reversion gives a small but real fall in annual electricity. Partial persistence gives no change
that the data can tell apart from zero. The standardized-reversion check gives the largest and
clearest fall. This spread rests on an open question: what happens to work from home after 2022
(Section 1.3). In Canada, 18.7 percent of employed people worked mostly from home in May 2024. This
was down 1.4 percentage points from May 2023 and 3.7 points from May 2022 (Statistics Canada 2024b).
If that fall continues, the partial-persistence and full-reversion scenarios are not less plausible
than the main, full-persistence scenario. The scenarios therefore form a range of outcomes, not a
central estimate with two side cases.

The paired, within-household design lets changes of this size be told apart from noise. Each
simulated household is compared against itself in 2022 and 2030, so the intervals reflect the
occupancy-driven signal (Section 1.4). Households also share a city and an archetype, so clustering
matters for some metrics (Section 3.8). For midday share, the clustering-aware interval used in
Section 3.4 is about 40 percent wider than a plain interval. No conclusion changes with the interval
method.

Section 3.5 shows what the household-level model adds over an average-profile method. That method
gives every household in a city-and-archetype cell the same schedule. In the illustrative cell, the
annual totals differ by about 9 percent. Household-to-household diversity in peak timing differs far
more, because the average-profile method collapses it almost to zero by construction. Only a
household-level model can represent this spread, and it sets how individual peaks combine into the
stock's load curve.

The measured-data comparison in Section 3.6 is a check on the simulated shape, not a validation of
the model as a whole. Simulated midday share sits reasonably close to the measured value. The
simulated shape peaks earlier and less sharply than the measured one (Figure 12).

The end-use survey check (Section 3.3) is a check against a fitted target, because the same survey
data also calibrates the model. All 48 archetype-by-city-by-year cells fall within plus or minus 15
percent of that target, so the calibration behaves as intended. This is not independent evidence that
the diurnal shape is correct. The measured comparison in Section 3.6 is that separate, second kind of
check.

One result runs against a simple intuition. Under the main scenario, interior lighting and interior
equipment both fall very slightly, and both changes exclude zero (Section 3.3). At the same time, the
at-home share and the midday share both rise. More time at home therefore does not mean more plug
load in these simulations, and no causal account is offered.

This study differs from its closest external precedent, Chen et al. (2022), on one axis. Their
stock-scale, paired simulation design evaluates an already-elapsed period. This paper carries
occupancy through the pandemic-era break to 2030, under more than one explicit persistence
assumption. The two studies otherwise share most of the framework dimensions in Table A1.

Nothing in the pipeline is specific to Canada beyond its calibration data (Section 1.4). Any country
with a repeated national time-use survey, a census-type household frame and a national end-use energy
benchmark could build the same design. The American Time Use Survey and the Harmonised European Time
Use Survey already supply such time-use data. Only the resulting magnitudes would be expected to
differ.


# 5. Limitations

This work has twelve limitations. The first nine bear directly on the results. The last three concern
modelling assumptions.

**Scope.** The study covers six Canadian cities (Toronto, Kelowna, Vancouver, Montreal, Calgary and
Winnipeg) and four dwelling types (single-detached, other low-rise, mid-rise and high-rise). It uses
one country's time-use survey, Canada's General Social Survey, and the cities do not cover every
Canadian climate. The measured check uses residential electricity load shapes for Toronto and Ontario
in 2022 only. It excludes natural gas heating and the other cities, so it is a shape check, not a full
energy validation.

**Only home energy is inside the system boundary.** More time at home moves some activity, and its
energy use, out of offices, schools and other workplaces. Those buildings are not simulated. The
results describe the residential side of the shift, not its net effect on total building energy use.

**The comparison with the authors' earlier simulation campaign is not household-paired.** Diaries now
come only from the most recent survey year, so a different set of households passes the simulation
engine's data-quality check. The ratios against the earlier campaign (Section 3.6) therefore compare
model versions, not the same households. The 2022-to-2030 comparisons hold households fixed and are
not affected.

**Only one building envelope is used, for every city and dwelling type.** An existing-stock envelope
needed a published U-value and solar heat gain coefficient for the main existing window type. That
type is double-glazed clear glass with a 13 mm air gap, about 74% of single-detached window area. No
source prints these two values, so every building uses the current building-code envelope. This is
conservative in one respect, since older windows lose more heat than modelled.

**The simulated at-home level runs a little high against an independent benchmark.** The chosen 2022
stock spends 75.04% of time at home against a 72.3% observed anchor. The gap of 2.74 points is just
outside the allowed band of 2 percentage points, and the band was not widened. The gap comes mostly
from synthetic diaries and unweighted averaging; the real, weighted 2022 respondents sit at 72.31%.

**Weekend behaviour is harder to reproduce than weekday behaviour.** A distance ceiling of 0.10 was
fixed for every day type in advance. Weekdays pass, but Saturday and Sunday score 0.16 to 0.18 in both
validation checks. The gap sits almost entirely in weekend days the model filled in from other day
types; observed weekend diaries alone pass. Extra weekend training weight barely moved the gap. A wider ceiling of 0.20, considered after
these scores were seen, is not used (Section S3).

**The 2030 results are a scenario, not a forecast.** The 2030 schedules keep the same households and
diary assignments as 2022; only the at-home slots are re-raked (Section 2.5). The target is the 2022
level plus eight years of a linear trend fitted to 2005, 2010 and 2015 respondents, minus the part of
the pandemic-era shift assumed to fade. It is clipped to 0% to 100%. Population, policy and household
composition stay fixed, and no probabilistic range is given. The scenarios bracket one assumption:
how much of the 2022 shift persists.

**Saturday and Sunday are simulated as one day.** The building energy model reads only a weekday and
a weekend pattern per household. Saturday and Sunday are pooled into that weekend pattern, although
the diary model calibrates each day separately. This discards a measured difference between the two
days for every household and year, at the interface rather than in the occupant model (Section S6).

**The survey's method of collecting diaries changed in the same year that carries the pandemic
break.** Diaries for 2005, 2010 and 2015 came from telephone interviews; 2022 used a self-administered
electronic questionnaire. The collection-mode indicator is zero for the earlier cycles and one only
for 2022, so the method change and the pandemic-era shift are perfectly confounded. The direction of
the 2022 step (more time at home than in 2015) is supported by the wider pandemic literature. Its
exact size, and the 2030 scenarios built on it, carry a survey-design effect this study cannot
measure or remove.

**Three further limitations concern modelling assumptions.** First, 2030 uses the same typical-year
weather file as 2022, so the results isolate behaviour change from climate change. Second, matching
census households to diaries assumes the diary is independent of anything outside the matching
characteristics, which these data cannot test. Third, occupant metabolic heat comes from fixed
standard values per activity (Section 2.3) and is not calibrated against measured internal gains.


# 6. Conclusion

This paper asked whether, and how, occupancy-driven change reshapes the Canadian residential load
curve at stock scale under explicit work-from-home scenarios carried to 2030 (Section 1.4). The
timing of demand and the mix of end uses move more than the annual total does. The principal
findings are as follows.

1. In 2022 the national weekday at-home rate sits 4.73 percentage points above the 2005 to 2015
   trend. The three 2030 scenarios move the whole-day weekday at-home share by between 1.49 and
   negative 3.21 percentage points from 2022. The size of the move depends on how much of that break
   persists.
2. Under the main persistence scenario, annual whole-building electricity in 2030 is nearly unchanged
   from 2022, rising by 0.12 percent.
3. Under the main scenario, midday energy share rises by 0.73 percentage points and load factor by
   0.49 percentage points. Both changes exclude zero. This change matters most for grid planning, not
   the near-flat annual total.
4. The size, and even the direction, of the 2030 change depends on the persistence assumption. A full
   reversion to the pre-pandemic trend gives a small real fall in annual electricity. Partial
   persistence gives no change the data can tell apart from zero. A standardized-reversion check
   gives the largest fall of the three scenarios tested.
5. A household-level, diary-based schedule and a simpler average-profile method differ in annual
   total by about 9 percent in the illustrative cell. They give very different pictures of when
   different households reach their own peak. The average-profile method collapses
   household-to-household diversity in peak timing almost to zero by construction. The full model
   preserves it.
6. Against a year of measured Toronto and Ontario electricity data, the simulated load shape sits
   reasonably close to measured behaviour on some measures and not on others. The simulated peak
   arrives earlier in the day than the measured peak. The simulated peak-to-average ratio is lower
   than the measured one. This is a check on the simulated shape, not a validation of the model as a
   whole.

The practical message is that this behavioural shift is mainly a shaping question for the electricity
system, not a sizing one. Annual demand changes little under any of the scenarios tested. Under the
main scenario, the share of energy delivered in the middle of the day and the ratio of average to
peak load both rise. Grid and distribution planning that tracks only annual totals would miss this.

Three items from the limitations in Section 5 remain for future work. First, the 2030 scenarios use
the same typical-year weather file as 2022. A projected future-climate weather file would separate
behavioural change from climate change. Second, the measured check covers only Toronto and Ontario
electricity in one year. Extending it to other cities and years would show more fully where the
simulated shape matches measured behaviour. Third, a citable, Canada-specific account of the
work-from-home trend after 2022 could narrow the scenario range tested here. The range would then no
longer need to run from full persistence to full reversion.
