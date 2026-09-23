# Supplementary Information

Companion Supplementary Information to the main manuscript. Sections S1 to S11 cover the generative
occupancy model and its selection, diary validation, post-hoc calibration cost, schedule completion
and the donor draw, household sampling for the building simulation, annual schedule assembly, clustering-aware confidence
intervals, and the supplementary figures.

## S1 Generative model architecture

The day-type completion step needs a model that can take one observed diary per respondent and
produce the two missing day-types (the other days of the week not directly reported) for that
respondent, along with simple presence signals for the household. The chosen model has three parts
built on a shared encoder:

- A 6-layer Transformer encoder that reads the respondent's demographic and survey information
  (90 input variables after encoding: age group, sex, marital status, household size, province,
  labour-force variables, survey cycle-year, survey collection mode, school attendance, work-from-home
  status, and commute mode).
- A 6-layer decoder that generates the activity sequence (which of 14 activity types the person is
  doing) one half-hour slot at a time, for all 48 slots of the day.
- A separate, parallel set of small output heads that predict, for the same 48 slots, whether the
  person is at home and who else is present (9 co-presence channels: spouse, children, and so on).
  These heads are cut off from the activity decoder's training signal (a gradient-detach barrier),
  so training the activity sequence does not disturb the at-home/co-presence predictions and vice
  versa.

The model has about 29.25 million parameters and an internal width of 384. Separating "what the
person is doing" from "whether they are home and with whom" is what distinguishes this design from the
competing designs that mixed the two signals and did not clear the selection checks (Section S2).
The architecture is summarized in Table S1, with the activity codebook in Table S2.

**Table S1.** Calibrated generator model card.

Final model: the chosen generator plus the post-hoc marginal raking calibration step described below.
It had the lowest composite score among the four candidates that cleared all four selection checks,
out of more than 40 candidates tried (Section S2).

*Architecture.*

| Component | Specification |
|------------------------|----------------------------------------------------------------------------|
| Encoder | Shared 6-layer Transformer encoder |
| Activity decoder | 6-layer autoregressive decoder, 14-category activity sequence, 48 half-hour slots |
| Binary heads | Parallel non-autoregressive binary heads: at-home flag plus 9 co-presence channels (colleagues masked for 2005/2010); a gradient-detach barrier separates these heads from the activity decoder |
| Model width | 384 |
| Attention heads | 8 |
| Feed-forward width | 1,536 |
| Dropout | 0.1 |
| Parameter count | About 29.25 million |

*Conditioning variables (90 inputs after encoding).*

| Variable group | Variables | Type |
|-------------------|-------------------------------------------------------------|-------------------|
| Demographics | age group, sex, marital status, household size, province, census metropolitan area, official-language knowledge, labour-force activity, hours worked, occupation, class of worker, day-type stratum (weekday, Saturday, Sunday) | 12 categorical variables, one-hot encoded |
| Additional demographics | school attendance, work-from-home status, commute mode | 3 categorical variables, one-hot encoded |
| Continuous | Household income, standardized | 1 continuous variable |
| Binary flags | Survey collection mode (whether the diary was collected by telephone interview or filled in online), income-source flag | 2 binary flags |
| Learned embedding (injected separately, not part of the 90-input vector) | Survey cycle-year | learned, 16-dimension |

Note: the collection-mode flag records the survey's shift from telephone interviews to online
self-completion; the work-from-home flag records the pandemic-era change directly.

*Training.*

| Item | Value |
|-------------------------------------|---------------------------------------------------------------|
| Data split (stratified by cycle and day type) | 70/15/15, giving 44,843 / 9,609 / 9,609 records |
| Nearest-neighbour supervision | 5 demographic neighbours; neighbour-disagreement floor 0.1888 |
| Learning rate | 1e-4, 2,000-step warm-up then cosine decay |
| Batch size | 256 |
| Early stopping | 10 epochs' patience |
| Loss weights | at-home weight 0.9, activity weight 0.5, co-presence weight 0.5 |
| Label smoothing | 0.05 |

*Selection-check results for the chosen model.*

| Check | Threshold | Chosen model's result | Result |
|---------------------------------|----------------------------------|-------------------|--------------|
| Activity-distribution distance | 0.05 or below | 0.0191 | Met |
| At-home error | 5.3 percentage points or below | 4.57 pp | Met |
| Spousal co-presence gap (absolute) | 5.0 percentage points or below | 2.03 pp | Met |
| Composite score | Below 1.045 | 0.6355 | Met |

The origin of the four thresholds is described in Section S2.

Two notable candidates that did not clear the checks: one masked-discrete-diffusion design scored the
best composite of the whole search (0.559) but did not meet two of the four checks (at-home error 7.81 pp;
activity-distance 0.0529); the best-training-loss cross-attention decoders broke down at generation
time, with co-presence errors of 20 or more percentage points.

*Post-hoc calibration.* A per-(cycle x day-type x slot) marginal raking step is applied after
inference; it makes each stratum's at-home marginal match its target exactly. The cost is that about
1.8 to 2.1 percent of slot-records end up with an activity label that no longer matches its own at-home
flag; this is harmless to the building energy model, which reads only the at-home flag. Before raking,
the raw per-cell at-home gap reached 15.37 percentage points.

*Inference.* Activities are sampled at temperature 0.8; the binary heads are thresholded at 0.5; two
consistency rules are applied afterward (sleep at night implies at home; work implies away when the
work-from-home flag is not set).

*Output.* 192,183 diary-days (about 128,000 synthesized and 64,000 observed).

**Table S2.** Activity codebook and co-presence columns.

*Activity categories.* Every diary slot is assigned one of 14 activity categories: work (paid work and
telework), household work and maintenance, caregiving, purchasing, sleep, eating and drinking, personal
care, education, socializing, passive leisure, active leisure, community or volunteer activity, travel,
and miscellaneous. The number of raw survey activity codes mapped onto this 14-category scheme differs
by survey cycle (182 raw codes in 2005, 264 in 2010, 64 in 2015, 121 in 2022), with zero disambiguation
conflicts across all four cycles; the underlying per-code crosswalk is not reproduced here.

*Co-presence columns.* Nine unified co-presence columns record who else is present with the respondent:
alone, spouse or partner, children under 15, parents or parents-in-law, other household members 15 or
over, other household members, friends, other persons, and work colleagues. These nine columns are
built from ten raw survey columns (colleagues is not collected in 2005 or 2010, so it is entirely
missing for those two cycles). Per-cycle non-missing rates are about 20 percent in 2005, 19.3 percent
in 2010, 0.1 percent in 2015 and 6.8 percent in 2022.

## S2 Model selection search

**How many candidates.** Over 40 candidate model designs were tried in a staged search: first
trained on a small 2% slice of the data, then 20%, then the full data, so that clearly weak designs
could be dropped early without spending full training time on them. The candidates covered several
different families: simple statistical (Markov chain) models, autoregressive sequence models,
variational autoencoders, GAN-style models, cross-attention architectures, and masked
discrete-diffusion models.

**The four checks used to keep or reject a candidate.** A candidate had to pass all four of these to
be considered:
- How different the generated mix of activities is from the real mix (a Jensen-Shannon
  divergence, capped at 0.05).
- How far off the generated at-home percentage is from observed data (an error measure in
  percentage points, capped at 5.3 pp).
- How far off the generated share of time spent with a spouse or partner is (capped at 5.0
  percentage points).
- A single combined score blending several of the above (capped just under 1.045).

**Where the four thresholds come from.** The thresholds were carried over from an earlier baseline
model rather than derived independently. Two of them (the combined-score cap of 1.045 and the at-home
error cap of 5.3 pp) equal that baseline model's own scores. The activity-distance cap (0.05) is a
convention, and the co-presence cap was set at 5 percentage points, tighter than the 10 points used
for the baseline. None of the four has an independent basis such as a survey sampling-error floor.
This is a limitation of the selection procedure; the threshold-sensitivity result below shows how
much the choice of model depends on it.

**Which candidates passed.** Four candidates clear all four thresholds: the chosen model and three
variants of it with parts of its output-head design changed. Passing was necessary but not
sufficient; the chosen model was picked because it has the lowest (best) combined score of the four.
Some notable designs did not clear the thresholds: one masked-diffusion candidate produced the single
best combined score of the entire search, but did not meet the activity-distance and at-home checks (its
at-home error was 7.81 percentage points, well above the 5.3 pp cap), showing that the combined score
alone is not a reliable stand-in for the four individual checks. Several cross-attention designs
achieved the best training performance of any family but broke down when asked to generate new
diaries, producing co-presence errors of 19 to 23 percentage points, nearly four times the 5.0 pp
cap; this shows that training performance does not guarantee that a generated diary will look right
when actually sampled.

**Threshold-sensitivity result.** A follow-up check moved each of the four thresholds up and down by
10% and 20%, one at a time and all four together, to see whether small changes to the checks would
have changed which model is picked. Across every one of the 21 tested variations, the same four
candidates (the chosen model and the three variants above) pass together except when the at-home-error check is
tightened by 20% (either alone or together with the other three), in which case only one other
variant still passes and would be selected instead. In every scenario where the chosen model is still
eligible, it remains the one selected. The selection is therefore not sensitive to small changes in
three of the four thresholds, and is sensitive to the fourth (the at-home-error check) only at the
most aggressive 20% tightening tested.

## S3 Diary validation on a held-out year

Two related checks assess whether the model's generated diaries for the most recent survey year
(2022) look like real 2022 behaviour.

**The ceiling.** A single distributional distance ceiling of 0.10 was fixed for every day type
(weekday, Saturday and Sunday) before either check was run, and both checks are reported against it.

**Held-out-year test.** The model, trained only through the second-most-recent survey year (2015),
was asked to generate diaries for the entirely unseen 2022 year. On weekdays the generated diaries
scored 0.0619, within the 0.10 ceiling.

**Backcast reconstruction.** Separately, the fully trained model (which has now seen 2022 data) was
asked to reconstruct 2022 diaries using the real 2022 respondent information. On weekdays this
scored 0.0630, also within the 0.10 ceiling.

**Weekends do not meet the ceiling.** On weekends both checks score well above 0.10: 0.1817
(Saturday) and 0.1843 (Sunday) in the held-out-year test, and 0.1637 and 0.1618 in the backcast. No
looser weekend ceiling is used.

The weekend gap is concentrated in one identifiable part of the evaluation set. That set
mixes two kinds of rows: diaries genuinely observed on that day type, and diaries the model had to
synthesize because the respondent reported a different day type. Scored on the genuinely observed
2022 weekend diaries alone, the distance is 0.036 (Saturday) and 0.040 (Sunday), well inside the
0.10 ceiling; the synthesized rows sit 0.138 to 0.175 from the observed distribution. Weekend
diaries are fewer and weekend behaviour is more varied, and raising the weekend training weight
twice moved the score by about 0.005, so the gap does not appear to be an optimization shortfall.
The synthesized weekend days are therefore a limitation of the diary completion step.

## S4 Post-hoc calibration (raking) cost

After the model generates diaries, a calibration step ("raking") is applied that nudges the
generated at-home percentages, slot by slot, to match their target values exactly. This step is
needed because the raw generated output, while close, is not perfectly calibrated to the target
at-home percentages. The cost of this adjustment is that roughly 1.8-2.1% of individual
slot-records end up with an activity label that no longer matches its own at-home flag (for example,
a slot still labelled "away" activity after being nudged to "at home"). This is treated as harmless
for the building energy model, because the energy model reads only the at-home flag to decide
occupancy; it does not read the activity label for that purpose.

## S5 From one diary day to a full year of hourly values

**Two separate reductions turn one diary day into part of a year-long hourly schedule.** The
underlying diary is recorded in 48 half-hour slots per person per day. The first reduction folds each
person's day down to 24 hourly values by averaging each pair of half-hour slots (hour h takes the
average of slots 2h and 2h+1), then averages across every member of the household to get one
occupancy fraction and one metabolic rate per household per hour. Because the survey diary starts its
clock at 4 a.m. rather than midnight, the 24 hourly values are then shifted by 4 hours so that hour 0
lines up with real midnight, matching the weather file's clock.

The second reduction concerns day types: each household ends up with only two such 24-hour
profiles, a Weekday profile and a Weekend profile, not seven separate days. How a household gets both
profiles when the survey observed only one day (the donor draw) is described in Section S7. How those
two 24-hour profiles become 8,760 hourly values covering a full simulated year is described in
Section S9.

## S6 Day-type strata: why weekday, Saturday and Sunday are handled separately

Each survey respondent reports a diary for exactly one day, and that day is recorded as one of three
strata: a weekday, a Saturday, or a Sunday. These three are kept separate through the earlier stages
of the pipeline (the generative model, the raking step) because at-home behaviour genuinely differs
across all three, not just between weekdays and weekends. The size of that difference in the
2022 stock is a daily at-home share of 74.1 percent on weekdays, 76.0 percent on Saturdays and 78.9 percent
on Sundays (per person, unweighted, averaged over the 48 half-hour slots of the day).

At the point where the schedule is handed to the building energy model, the three strata are reduced
to two: Saturday and Sunday are pooled into a single Weekend profile, and only Weekday and Weekend
profiles are carried forward. This is a deliberate simplification, not an oversight, and it has a
known cost: pooling loses the calibrated difference between Saturday and Sunday entirely, in both
years. The size of the difference that is lost is 2.9 percentage points in 2022 (Saturday 76.0 percent,
Sunday 78.9 percent) and 2.3 points in the 2030 main scenario (Saturday 77.9 percent, Sunday 80.2
percent), in the same unit as above; in both years people are at home more on Sunday. This is a
limitation of the two-day-type design: the building energy model consumes only a Weekday/Weekend
schedule, and carrying a third day type through to that stage would require changing the building
energy model itself.

## S7 The donor pool and the draw rule for completing a missing day type

**What problem this step solves.** Because each respondent reports only one day, most households
have a diary for only one of the two profiles a schedule needs (Weekday or Weekend), not both. Before
a household's schedule can be built, the missing profile has to be filled in from somewhere. This is
a separate, later step from the demographic donor-matching that assigns every household its first
diary (covered in the main text): that earlier step decides which diary a household starts with; this
step decides what happens to the day type that diary does not cover.

**The donor pool.** The pool a missing day type is filled from is simple: every person-record in the
same year's data that already carries the needed day type. A household missing its Weekend profile
draws from every record tagged Saturday or Sunday (the two are pooled into one donor pool, matching
the Weekend target); a household missing its Weekday profile draws from every record tagged weekday.
Unlike the earlier demographic donor-matching step, this donor pool is not narrowed by age, sex,
household size or any other demographic key: any record of the right day type is eligible. Only the
recipient household's own dwelling and household attributes (household size, dwelling type, province
and so on) are kept; the donor supplies only the activity sequence and at-home flags for the missing
day. For the 2030 scenario year, the donor pool is the already-assembled 2030 file itself, so a
donor's occupancy still reflects the 2030 scenario rather than 2022 behaviour.

**The draw rule.** The draw is made once per household member who needs the missing day type, not
once per household: each member independently draws its own donor row from the pool described above.
This means two members of the same household missing the same day type can end up with donors from
two different donor households. The draw is made with a fixed random-number seed (seed 42), so given
the same input file the same recipient always receives the same donor row; running the completion
step twice on the same input produces byte-identical output. A direct consequence of the per-member
draw is that the completed day's within-household presence pattern (who is home at the same time as
whom) is synthetic for imputed days, not observed. This is treated as harmless to the building energy
model specifically because that model reads only each household's overall occupancy fraction and
metabolic rate for each hour, not which individual members are home together.

**Why a donor draw rather than a copied day.** An earlier version of this step filled a missing
day by copying the household's own observed day onto the missing slot (a Weekday-only household's
Saturday and Sunday would simply repeat its Weekday diary). This was found to bias the calibrated
weekend average downward by 2.76 percentage points, because a household's own weekday diary carries
weekday behaviour into a weekend slot and weekend at-home rates are the higher of the two. The
donor-draw method described above was adopted specifically to remove this bias, and it does: because it draws a genuine
weekend (or weekday) diary rather than repeating the household's own day, the calibrated weekend
marginal is preserved rather than diluted.

**Historic years use the same mechanism, restricted to their own year.** The 2005, 2010 and 2015
schedule files are built by a separate copy of this same completion step, applied only after each
cycle's own diaries have already been assembled onto the analytical household frame. The donor pool
for a historic year is drawn only from that year's own diary pool; there is no path in the code by
which a 2015 household's missing day type could be filled from a 2005 or 2022 record.

## S8 Household sampling for the building simulation

**A separate draw from the donor draw above.** After the schedule files are
finished, 50 households are drawn (without repeats, unless a group has fewer than 50 households, in
which case draws with repeats are used) for each city-and-building-type group used in the building
simulation, so that the same 50 households can be run through the simulation for every year on the
same building and weather file. This household sample is unrelated to the day-type donor draw of
S7: it happens afterward, on the finished schedule files, and it decides which households are
simulated, not what those households' schedules contain.

**The sampling pool is not simply "every household in the file."** Before the 50-household sample is
drawn, the finished schedule file is passed through a sanity check that looks at each household's
24-hour Weekday and Weekend patterns and drops any household whose pattern looks physically
implausible. The two rules that do the work are a minimum of two occupied hours in a day type, and a
limit on how many times presence may switch on and off within the day. Only households that pass
this check are eligible to be sampled. This means the sampling pool depends on the exact numeric
content of the schedule file, not just on which households are listed in it.

**The two-hour rule interacts with the reversion scenarios, and the direction matters.** The rule
removes households shown as occupied for less than two hours in a day type, and the reversion
scenarios are precisely the ones in which time at home falls. It therefore removes, preferentially,
the households that reverted most, and what remains leans very slightly toward households that
reverted least. Measured on all 144,465 households, the ordinary 2030 file already excludes 983
households under these rules; the scenario files exclude a few more, by 27 in the half-reversion scenario, 70 in one full-reversion arm and 161 in the other. The largest
excess is therefore 161 households, or 0.11 % of the stock, which bounds the arithmetically possible
shift in the national at-home share at 0.11 percentage points, inside the 0.5-point tolerance set
in advance, and the realized effect is a fraction of that. The bound is nevertheless several times
larger than the 0.005 to 0.022 percentage-point margins by which the scenarios reach their design
targets.

**Consequence for the comparison with the earlier simulation campaign.** The schedule files used in
this paper are numerically close to, but not identical to, those of the authors' earlier simulation
campaign (Section 3.6). Because the sanity check reads the numbers, it can drop a slightly different
set of households from each version, even though both cover the same 144,465 households. For
single-detached houses in Montreal, the check drops 103 of 16,430 candidate households from the 2022
file and 104 from the 2030 file, leaving a paired pool (households present and passing the check in
both years) of 16,326; the same check applied to the earlier files leaves a paired pool of 16,208. The
two pools differ by 320 households (households in one pool but not the other), so the same fixed seed
draws a different 50-household sample from each. Each draw is deterministic and reproducible from its
own files; the two samples overlap substantially but are not identical, so the comparison with the
earlier campaign is not household-paired.

Across all city and building-type groups (Kelowna and Vancouver share one British Columbia household
pool, so the stock holds 134,262 distinct candidate households), the check drops 918 households
(0.68 percent) from the 2022 file and 921 (0.69 percent) from the 2030 file, against 797 (0.59
percent) and 1,043 (0.78 percent) from the earlier files.

## S9 Assembly to the full year and the reduction to hourly resolution

Each household's finished Weekday and Weekend 24-hour profiles are written into the building energy
model as one schedule object per channel (occupancy, metabolic heat gain, and the equipment and
lighting channels added by the end-use layer), each carrying a single calendar block that runs from
January 1 through December 31 with two named sub-patterns: one for weekdays, one for weekends. The
building energy model's own calendar, not a separate step in this pipeline, is what expands those two
24-hour patterns into the 8,760 hourly values the simulation actually runs on: for each of the year's
calendar days it looks up whether that day is a weekday or a weekend day by the ordinary
Monday-through-Sunday calendar and repeats the matching 24-hour pattern for that day. No holidays are
distinguished, because the weather files used carry none, and the two artificial sizing days used to
size the building's heating and cooling equipment are forced onto the weekday pattern, so equipment
sizing is based on the busier of the two profiles rather than a fixed separate assumption.

The schedule is never handed to the building energy model at its original 30-minute diary resolution;
only the hourly reduction from S5 is presented at this stage. This means the finest temporal detail
the building simulation ever sees for occupancy, internal heat gain, plug loads or lighting is one
value per hour, for one of two day types per household, expanded to a full year by the calendar rule
above.

## S10 Does household clustering change the reported uncertainty?

Section 2.11's paired-difference interval (Eq. 16) pools every household's 2022-to-2030 change
together and treats each one as an independent observation. Households sharing a city or an
archetype are not independent in principle, so a cluster bootstrap was run for comparison:
the 24 (archetype, city) cells are resampled with replacement (24 drawn from 24, repeats allowed),
each drawn cell's own paired household deltas are kept intact (no resampling within a cell, since
the cell is itself the resampling unit), and the pooled mean is recomputed over 10,000 replicates
(fixed seed 12345) to build a percentile interval.

Applied to the paired 2022 and 2030 simulation results (24 cells of 50 households, 2,400
households), the two methods give the intervals in Table S3.

**Table S3.** Clustering-aware versus plain paired-difference confidence intervals for midday share and load factor.

| Metric | Method | Point | 95% interval | Width | Change from plain interval |
|-------------|-------------------------------|-----------|--------------------|-----------|--------------|
| Midday share | Plain pooled (Eq. 16) | 0.00732 | [0.00645, 0.00819] | 0.00174 | n/a |
| Midday share | Cell-cluster bootstrap | 0.00732 | [0.00616, 0.00859] | 0.00243 | 39.8% wider |
| Load factor | Plain pooled (Eq. 16) | 0.00494 | [0.00412, 0.00577] | 0.00165 | n/a |
| Load factor | Cell-cluster bootstrap | 0.00494 | [0.00413, 0.00574] | 0.00161 | 2.3% narrower |

All values are fractions; multiply by 100 for percentage points.

For midday share, accounting for clustering by city and archetype widens the interval by about
two-fifths, but the interval still excludes zero, so the 2022 to 2030 change remains distinguishable
from zero; the main text therefore reports the wider, clustering-aware interval for this metric. For
load factor, clustering makes almost no difference (2.3 percent narrower, within the bootstrap's own
replicate-to-replicate variation), and the plain pooled interval is adequate. Neither interval crosses
zero under either method.

## S11 Supplementary figures

![](../impl/T94_out/figS1_sample_size.png){width=16cm}

**Figure S1.** Half-width of the 95 percent confidence interval on the 2022 to 2030 change against
sample size, for six load-shape and energy metrics, in the four archetype cells in Montreal (climate
zone 6A). Sample sizes are 10, 20, 50, 100, 150 and 200 households. Below 200 households, the
half-width is the 2.5th to 97.5th percentile spread of 1,000 bootstrap subsample means drawn from the
same 200-household set; at 200 households (stars) it is a parametric interval on the full sample, a
different statistic, which is why the stars sit above the 150-household points.

![](../impl/T94_out/figS2_threshold_sensitivity.png){width=16cm}

**Figure S2.** Stability of model selection when the selection thresholds change. Each panel shifts
one threshold (or all four together) by minus 20, minus 10, plus 10 and plus 20 percent, giving 21
distinct scenarios including the original thresholds at 0 percent. The y-axis gives the number of
candidates that meet all four checks; the marker shows which candidate is selected (lowest composite
score among those that meet all four checks). The chosen model is selected in 19 of the 21 scenarios;
the exceptions are a 20 percent tightening of the at-home error threshold, alone or with the other
three, where only one other candidate meets all four checks.
