# 4. Discussion

Section 1.5 asked whether, and how, occupancy-driven change reshapes the residential load curve at
stock scale, under explicit work-from-home scenarios carried to 2030. Section 3 gives a specific
answer. Under the main scenario, annual whole-building electricity in 2030 is nearly unchanged from
2022, rising by 0.1209 percent (Section 3.3), while the timing of demand and the mix of end uses move
more than that total does. The comparison across the three named 2030 scenarios, plus one
standardized-reversion check (Section 3.2), is this paper's main message about uncertainty: the
full-reversion scenario shows a small but real fall in annual electricity, the partial-persistence
scenario shows no change that the data can tell apart from zero, and the standardized-reversion
variant shows the largest and clearest fall of the three. Only a change whose confidence interval
excludes zero is discussed below as a change; where an interval contains zero, this paper says so and
does not describe it as a rise or a fall.

The paired, within-household design used throughout Sections 3.2 to 3.4 is what lets a change of this
size be told apart from noise: because each simulated household is compared against itself across 2022
and 2030 rather than against a different sample, the reported confidence intervals reflect the
occupancy-driven signal specifically, one of this paper's scientific contributions (Section 1.5).
Because households in this study also share a city and an archetype, whether the interval method
accounts for that clustering matters for some metrics and not for others (Section 3.8): the
clustering-aware interval used for midday share throughout this paper is about 40 percent wider than a
plain interval that ignores clustering, while the equivalent comparison for load factor is a
negligible 2 percent narrower. Both methods keep both metrics on the same side of zero, so no
conclusion in this paper changes depending on which interval is used, but the difference is the reason
the wider, clustering-aware interval is the one reported in Section 3.4.

For grid planning, Section 3.4 has a direct reading. Under the main
scenario, a larger share of annual energy moves into the middle of the day: midday share rises by 0.73
percentage points. The ratio of average to peak hourly load also rises: load factor rises by 0.49
percentage points. Both changes exclude zero. Peak demand and the evening ramp, which are point
estimates, both fall slightly under the main scenario, from 47.207 to 46.332 kilowatts and from 7.852
to 7.768 kilowatts respectively.
Timing, not only the annual total, is material to how a grid operator plans for peak demand, the
evening ramp and demand-response programs (Denholm et al. 2015).

Section 3.5 isolates what the household-level model used throughout this paper adds over a simpler
average-profile method that keeps each household's own calibrated design power but assigns every
household in a city-and-archetype cell the same schedule. For the one cell used as an illustration,
single-detached homes in Toronto in 2022, the annual totals differ by 725.84 kilowatt-hours, about 9
percent (8,225.56 under the full model against 8,951.40 under the average-profile method). What
differs far more sharply is household-to-household diversity in peak timing, which
the average-profile method collapses almost to zero by construction: a circular standard deviation of
peak hour of 3.493 hours under the full model against 0.084 hours under the average-profile method in
2022, and 3.255 hours against 0.053 hours in 2030. This is the clearest demonstration in this paper of
what the household-level, diary-based model adds: the spread of when different households peak, which
only a model built at the household level can represent, and which sets how individual peaks combine
into the stock's load curve. The annual totals also differ, but by far less than the timing does.

The generative model behind these results was chosen from a broader search (Section 3.8): it has the
best combined score among four candidates that passed all four selection checks, and the choice holds
in 19 of 21 threshold variations, changing only under the strictest tightening of the at-home check.
Two of the thresholds were set at values an earlier model version already reached, so the selection
is best read as robust to moderate threshold changes, not as independently justified by them.

Section 3.6 compares the simulated load shape against a year of real measured hourly electricity data
for Toronto and for Ontario in 2022. This is a check on the simulated shape, not a validation of the
model as a whole. On the shoulder-season weekday comparison, simulated midday share (0.3787) sits
reasonably close to the measured value (0.3513), while the simulated peak hour (17.0) arrives earlier
in the day than the measured peak hour (18.69), and the simulated peak-to-average ratio (2.1367) is
lower than the measured one (2.3231): the simulated shape peaks earlier and less sharply than the
measured one in this comparison. All twelve period-and-day-type groups are shown in Figure
8.

The activity-resolved equipment and lighting check against the national end-use energy survey (Section
3.3, and Section 1.5's first practical contribution) is, by design, a check against a fitted target
rather than an independent validation: the same survey data that supplies the target also calibrates
the model. All 48 archetype-by-city-by-year cells fall inside the band
of plus or minus 15 percent around that fitted target. This result shows the calibration behaves as
intended; it is not, on its own, independent evidence that the underlying diurnal shape is correct,
which is why Section 3.6's measured comparison is reported as a separate, second kind of check rather
than folded into this one.

One result in Section 3.3 runs against a simple intuition. Under the main scenario, interior lighting and interior equipment both fall
very slightly from 2022 to 2030, lighting by 0.0157 percent and equipment by 0.0066 percent, both
changes excluding zero, at the same time as the at-home share and the midday share both rise. More
time spent at home therefore does not translate into more plug load in these simulations; no causal
account of this result is offered here.

The scenario spread in Section 3.2 rests on an open question this paper's own material does not
settle: what happens to work from home after 2022 (Section 1.3). In Canada, 18.7 percent of
employed people worked mostly from home in May 2024, down 1.4 percentage points from May 2023 and
3.7 points from May 2022 (Statistics Canada 2024b). If that fall continues, the
partial-persistence and full-reversion scenarios in Section 3.2 are not less plausible than the main,
full-persistence scenario. The scenarios are therefore best read as a range of outcomes, not as a
central estimate with two side cases.

Against the closest external precedent identified in Section 1.2, Chen et al. (2022), this study
differs on one specific axis: that stock-scale, paired simulation design evaluates an already-elapsed
period, while this paper carries occupancy through the pandemic-era break to a stated future year,
2030, under more than one explicit persistence assumption. This is the one difference claimed here;
the two studies otherwise share most of the framework dimensions listed in Table 1, and no wider
novelty claim is made.

Nothing in the pipeline used to produce these results is specific to Canada beyond its calibration data
(Section 1.5). Any country with a repeated national time-use survey, a census-type household frame
linking diaries to a dwelling stock, and a national end-use energy benchmark, of the kind already
supplied elsewhere by the American Time Use Survey and the Harmonised European Time Use Survey, could
build the same generator, the same held-out-year evaluation, and the same paired stock-scale design
for its own housing stock; only the resulting magnitudes would be expected to differ. Section 5 states
the scope and data limitations that bound this study; nothing above should be read as contradicting
that section.


# 5. Limitations

This work has twelve limitations. The first nine bear directly on the results reported above; the
last three concern modelling assumptions. Each is given together with what it does and does not
affect.

**Scope.** The study covers six Canadian cities (Toronto, Kelowna, Vancouver, Montreal, Calgary and
Winnipeg) and four dwelling types (single-detached houses, other low-rise houses, mid-rise apartments
and high-rise apartments), built from one country's time-use survey (Canada's General Social Survey).
No other country's time-use data is used, and the six cities do not represent every Canadian climate.
The check against real-world data is a comparison to measured residential electricity load shapes for
Toronto and the province of Ontario in one year, 2022; it is not a whole-building energy measurement
(it excludes natural gas heating and is not available for the other five cities), so it should be
read as a shape check, not a full energy validation.

**Only home energy is inside the system boundary.** More time at home moves some activity, and its
energy use, out of offices, schools and other workplaces. This study simulates homes only, so any
change in the energy use of those other buildings is not estimated, and the results describe the
residential side of the shift, not its net effect on total building energy use.

**The comparison with the authors' earlier simulation campaign is not household-paired.** The
model of occupant behaviour used here draws diaries only from the most recent survey year, unlike an
earlier version that mixed in older survey years. This choice changes which households pass the
simulation engine's own data-quality check, so the pool of households actually simulated differs
between versions: for one representative city-and-type cell (single-detached houses in the Montreal
region), the current pool holds 16,326 households against 16,208 in the earlier version, 320
households belong to one pool but not the other, and the same random seed therefore draws a
different sample of households in the two versions. The ratios against the earlier campaign in
Section 3.6 therefore compare model versions, not the same households; this does not affect the
2022-to-2030 comparisons, which hold the same households fixed within this study.

**Only one building envelope is used, for every city and dwelling type.** Confirming a separate,
older envelope for existing homes required a published U-value and solar heat gain coefficient for the
dominant window type of the existing housing stock (double-glazed, clear glass, 13 mm air gap, which
covers about 74% of single-detached window area in the reference source). No source in the literature
search prints these two values for that window type, so the existing-stock envelope variant was not
built, and every simulated building uses the current building-code envelope regardless of its true
vintage. This is conservative in one respect (older windows lose more heat than modelled) and is stated
as a limitation rather than corrected with an assumed number.

**The simulated at-home level runs a little high against an independent benchmark.** An internal check
compares the population's simulated share of time at home against an external observed anchor, with an
allowed band of 2 percentage points. The chosen 2022 housing stock scores 75.04% against a 72.3%
anchor, a gap of 2.74 points, just outside the band; the band was not widened to accommodate this. The
gap traces mostly to how synthetic (model-generated) diaries and unweighted averaging behave, not to
the real, weighted 2022 survey respondents, who sit on the anchor at 72.31%. This is reported as a
result, not hidden or waived.

**Weekend behaviour is harder to reproduce than weekday behaviour.** This study fixed one
distributional-distance ceiling of 0.10 for every day type before looking at results. Weekday scores
pass comfortably (0.0619 to 0.0630). Saturday and Sunday do not meet this ceiling in either of the two
validation checks (0.16 to 0.18). Splitting the weekend evaluation set apart shows the gap sits almost
entirely in diary-days the model had to fill in because a respondent's diary covered a different day
type: genuinely observed weekend diaries alone score 0.036 (Saturday) and 0.040 (Sunday), well inside
the ceiling, while the filled-in weekend rows score 0.138 to 0.175 away from real behaviour. Increasing
the training weight on weekends twice moved this gap by only about 0.005, so it is not simply an
undertrained model. A wider ceiling of 0.20 was considered after these numbers were seen and is
disclosed once in the supplementary material; it is not used anywhere in this paper, and no weekend
result in the main text or the supplementary material should be read as having passed a ceiling that
was set before the fact. Full detail is in the supplementary material, Section S.3.

**The 2030 results are a scenario, not a forecast.** The 2030 schedules keep the exact same households
and the exact same person-to-diary assignments as the chosen 2022 stock; only the at-home slots are
re-raked to a new target (Section 2.7): the 2022 level, plus eight years of a linear trend fitted to
real respondents from 2005, 2010 and 2015 (the years before the survey was disrupted), minus the part
of the 2022 pandemic-era shift assumed to have faded, clipped to stay between 0% and 100%. No
probabilistic uncertainty range, no policy change, and no change in household composition is built
into this projection, which runs on a fixed population. The paper's scenario range (full, half and no
persistence of the 2022 shift, plus a standardized variant) should be read as bracketing one
assumption, how much of that shift persists, not as a probabilistic forecast of 2030 occupancy.

**Saturday and Sunday are simulated as one day.** The schedules handed to the building energy model
carry two daily patterns per household, a weekday pattern and a weekend pattern. Saturday and Sunday
are pooled into that single weekend pattern, although the model that generates the diaries keeps the
three day types apart and calibrates a different at-home level for each. The pooling therefore discards
a genuine, measured difference between the two weekend days for every simulated household and every
simulated year. It is a property of the interface to the building energy model, which reads only a
weekday and a weekend pattern, and not of the occupant model itself; the supplementary material states
where it happens and what size of difference is lost.

**The survey's method of collecting diaries changed in the same year that carries the pandemic
break.** For the 2005, 2010 and 2015 cycles, the diaries behind this paper were collected by
telephone interview; starting with the 2022 cycle, the same survey moved to a self-administered
electronic questionnaire that the respondent fills in rather than an interviewer reading it out. This
change in collection method lands on exactly the one survey year, 2022, that this paper also treats
as carrying the pandemic-era shift toward more time spent at home, and there is no earlier or later
wave collected in the new method to compare against, so the two changes cannot be told apart with
these data. The collection-mode indicator in the source data is zero for the
2005, 2010 and 2015 cycles and one only for 2022, so in this design the change of method and the
pandemic-era shift are perfectly confounded: an effect of the new method cannot be estimated
separately from a genuine change in behaviour, in either direction. This paper therefore treats the
possibility that part of the 2022 step reflects how the diaries were collected as neither supported
nor excluded by its own evidence. This does not overturn the direction of the result (more at-home time is
recorded in 2022 than in 2015), which is independently supported by the wider pandemic literature; it
does mean that the exact size of that step, and anything built forward from it, including the 2030
scenarios above (which carry forward all, half or none of this same 2022 step), carries an
amount of survey-design effect that this study cannot measure or remove.

**Three further limitations concern modelling assumptions.** First, the 2030 schedules
use the same typical-year weather file as 2022, not a projected future-climate weather file, so the
results isolate the effect of behaviour change from the effect of a changing climate. Second, matching
census households to survey diaries assumes that, once the matching characteristics are accounted for,
the diary is otherwise assigned independently of anything not captured by those characteristics; this
assumption cannot be tested directly with the data used here. Third, the metabolic heat given off by
occupants is taken from a fixed lookup of standard values per activity (Section 2.5) and is not independently calibrated against
measured internal gains in this study.


# 6. Conclusion

This paper asked whether, and how, occupancy-driven change reshapes the Canadian residential load
curve at stock scale under explicit work-from-home scenarios carried to 2030 (Section 1.5). The
results support a specific answer: the timing of demand and the mix of end uses move more than the
annual total does. The principal findings are as follows.

1. In 2022 the national weekday at-home rate sits 4.73 percentage points above the 2005 to 2015
   trend. The three 2030 scenarios move the whole-day weekday at-home share by between 1.49 and
   negative 3.21 percentage points from 2022, depending on how much of that break persists.
2. Under the main persistence scenario, annual whole-building electricity in 2030 is nearly unchanged
   from 2022, rising by 0.12 percent.
3. Midday energy share and load factor both rise under the main scenario, by 0.73 and 0.49 percentage
   points respectively, and both changes exclude zero; this is the change that matters most for grid
   planning, not the near-flat annual total.
4. The size, and even the direction, of the 2030 change depends on which persistence assumption is
   used: a full reversion to the pre-pandemic trend gives a small real fall in annual electricity, a
   partial-persistence assumption gives no change the data can tell apart from zero, and a
   standardized-reversion check gives the largest fall of the three scenarios tested.
5. A household-level, diary-based schedule and a simpler average-profile method differ in annual
   total by about 9 percent in the illustrative cell, but give very different pictures of when
   different households reach their own peak; the average-profile method collapses household-to-household diversity in peak
   timing almost to zero by construction, while the full model preserves it.
6. Against a year of measured Toronto and Ontario electricity data, the simulated load shape sits
   reasonably close to measured behaviour on some measures and not on others: the simulated peak
   arrives earlier in the day than the measured peak, and the simulated peak-to-average ratio is lower
   than the measured one. This is a check on the simulated shape, not a validation of the model as a
   whole.

The practical message is that this behavioural shift is mainly a shaping question for the electricity
system rather than a sizing one: annual demand changes little under any of the scenarios tested, while
the share of energy delivered in the middle of the day and the ratio of average to peak load both rise
under the main scenario. Grid and distribution planning that tracks only annual totals would miss this.

Three items follow from the limitations in Section 5 and are left here as future work, not claimed as
results. First, the 2030 scenarios use the same typical-year weather file as 2022; a projected
future-climate weather file would separate behavioural change from climate change. Second, the
measured check here covers only Toronto and Ontario electricity in one year; extending it to other
cities and years would give a fuller picture of where the simulated shape
matches measured behaviour. Third, once a citable, Canada-specific account of the work-from-home trend
after 2022 is available, it could narrow the scenario range tested here rather than leave it as a
bracket running from full persistence to full reversion.


