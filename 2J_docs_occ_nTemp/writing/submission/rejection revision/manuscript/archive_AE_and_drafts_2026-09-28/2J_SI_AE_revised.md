# Supplementary Information

This Supplementary Information accompanies the main manuscript. Sections S1 to S11 cover the
generative occupancy model and how it was selected. They also cover diary validation, the cost of
post-hoc calibration, schedule completion and the donor draw. The remaining sections cover household
sampling for the building simulation, annual schedule assembly, clustering-aware confidence intervals
and the supplementary figures.

## S1 Generative model architecture

The day-type completion step needs a model that takes one observed diary per respondent. From it,
the model must produce the two missing day-types for that respondent. These are the other days of
the week that the respondent did not report. The model must also produce simple presence signals for
the household. The chosen model has three parts built on a shared encoder:

- A 6-layer Transformer encoder reads the respondent's demographic and survey information. After
  encoding there are 90 input variables. They include age group, sex, marital status, household
  size, province and labour-force variables. They also include survey cycle-year, survey collection
  mode, school attendance, work-from-home status and commute mode.
- A 6-layer decoder generates the activity sequence one half-hour slot at a time, for all 48 slots
  of the day. At each slot it gives which of 14 activity types the person is doing.
- A separate, parallel set of small output heads covers the same 48 slots. These heads predict
  whether the person is at home and who else is present. There are 9 co-presence channels, such as
  spouse and children. A gradient-detach barrier cuts these heads off from the activity decoder's
  training signal. Training the activity sequence therefore does not disturb the at-home and
  co-presence predictions, and vice versa.

The model has about 29.25 million parameters and an internal width of 384. It separates "what the
person is doing" from "whether they are home and with whom". This separation distinguishes it from
the competing designs. Those designs mixed the two signals and did not clear the selection checks
(Section S2). Table S1 summarizes the architecture as a model card. It describes the final model:
the chosen generator plus the post-hoc marginal raking calibration step described below. More than
40 candidates were tried, and four of them cleared all four selection checks. The chosen model had
the lowest composite score among these four (Section S2).

**Table S1.** Calibrated generator model card.

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
self-completion. The work-from-home flag records the pandemic-era change directly.

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

Two notable candidates did not clear the checks. One masked-discrete-diffusion design scored the
best composite of the whole search (0.559). It did not meet two of the four checks: its at-home
error was 7.81 pp and its activity-distance was 0.0529. The cross-attention decoders with the best
training loss broke down at generation time. Their co-presence errors were 20 or more percentage
points.

*Post-hoc calibration.* A marginal raking step per (cycle x day-type x slot) is applied after
inference. It makes each stratum's at-home marginal match its target exactly. The cost is that about
1.8 to 2.1 percent of slot-records end up with a mismatched activity label. Their activity label no
longer matches their own at-home flag. This is harmless to the building energy model, which reads
only the at-home flag. Before raking, the raw per-cell at-home gap reached 15.37 percentage points.

*Inference.* Activities are sampled at temperature 0.8. The binary heads are thresholded at 0.5. Two
consistency rules are applied afterward. Sleep at night implies at home. Work implies away when the
work-from-home flag is not set.

*Output.* The output is 192,183 diary-days: about 128,000 synthesized and 64,000 observed.

The model works with a fixed activity codebook and a fixed set of co-presence columns. Table S2
lists the 14 activity categories and the nine co-presence columns.

**Table S2.** Activity codebook and co-presence columns.

*Activity categories.* Every diary slot is assigned one of 14 activity categories. These are work
(paid work and telework), household work and maintenance, caregiving, purchasing, sleep, eating and
drinking, and personal care. The rest are education, socializing, passive leisure, active leisure,
community or volunteer activity, travel, and miscellaneous. The number of raw survey activity codes
mapped onto this 14-category scheme differs by survey cycle. There are 182 raw codes in 2005, 264 in
2010, 64 in 2015 and 121 in 2022. There are zero disambiguation conflicts across all four cycles.

*Co-presence columns.* Nine unified co-presence columns record who else is present with the
respondent. They are alone, spouse or partner, children under 15, parents or parents-in-law, and
other household members 15 or over. The others are other household members, friends, other persons,
and work colleagues. These nine columns are built from ten raw survey columns. Colleagues is not
collected in 2005 or 2010, so it is entirely missing for those two cycles. Per-cycle non-missing
rates are about 20 percent in 2005 and 19.3 percent in 2010. They are 0.1 percent in 2015 and 6.8
percent in 2022.

## S2 Model selection search

**How many candidates.** Over 40 candidate model designs were tried in a staged search. Each design
was first trained on a small 2% slice of the data, then on 20%, then on the full data. Clearly weak
designs could thus be dropped early, without spending full training time on them. The candidates
covered several families. These were simple statistical (Markov chain) models, autoregressive
sequence models, variational autoencoders and GAN-style models. They also included cross-attention
architectures and masked discrete-diffusion models.

**The four checks used to keep or reject a candidate.** A candidate had to pass all four checks to
be considered:
- The distance between the generated mix of activities and the real mix. This is a Jensen-Shannon
  divergence, capped at 0.05.
- The error of the generated at-home percentage against observed data. It is measured in percentage
  points and capped at 5.3 pp.
- The error of the generated share of time spent with a spouse or partner. It is capped at 5.0
  percentage points.
- A single combined score that blends several of the above. It is capped just under 1.045.

**Where the four thresholds come from.** The thresholds were carried over from an earlier baseline
model. They were not derived independently. Two of them equal that baseline model's own scores: the
combined-score cap of 1.045 and the at-home error cap of 5.3 pp. The activity-distance cap (0.05) is
a convention. The co-presence cap was set at 5 percentage points, tighter than the 10 points used
for the baseline. None of the four has an independent basis, such as a survey sampling-error floor.
This is a limitation of the selection procedure. The threshold-sensitivity result below shows how
much the choice of model depends on it.

**Which candidates passed.** Four candidates clear all four thresholds. They are the chosen model
and three variants of it with parts of its output-head design changed. Passing was necessary but not
sufficient. The chosen model was picked because it has the lowest (best) combined score of the four.
Some notable designs did not clear the thresholds. One masked-diffusion candidate produced the single
best combined score of the entire search. It did not meet the activity-distance and at-home checks.
Its at-home error was 7.81 percentage points, well above the 5.3 pp cap. The combined score alone is
therefore not a reliable stand-in for the four individual checks. Several cross-attention designs
achieved the best training performance of any family. However, they broke down when asked to
generate new diaries. Their co-presence errors were 19 to 23 percentage points, nearly four times the
5.0 pp cap. Good training performance therefore does not guarantee that a generated diary will look
right when actually sampled.

**Threshold-sensitivity result.** A follow-up check moved each of the four thresholds up and down by
10% and 20%. The thresholds were moved one at a time and all four together. The aim was to see
whether small changes to the checks would have changed which model is picked. There were 21 tested
variations. In all of them, the same four candidates pass together (the chosen model and the three
variants above), with one exception. The exception is a 20% tightening of the at-home-error check,
either alone or together with the other three. In that case, only one other variant still passes and
would be selected instead. In every scenario where the chosen model is still eligible, it remains the
one selected. The selection is therefore not sensitive to small changes in three of the four
thresholds. It is sensitive to the fourth, the at-home-error check, only at the most aggressive 20%
tightening tested.

## S3 Diary validation on a held-out year

Two related checks test whether the model's generated diaries for the most recent survey year (2022)
look like real 2022 behaviour.

**The ceiling.** A single distributional distance ceiling of 0.10 was fixed for every day type:
weekday, Saturday and Sunday. It was fixed before either check was run. Both checks are reported
against it.

**Held-out-year test.** Here the model was trained only through the second-most-recent survey year
(2015). It was then asked to generate diaries for the entirely unseen 2022 year. On weekdays the
generated diaries scored 0.0619, within the 0.10 ceiling.

**Backcast reconstruction.** Separately, the fully trained model, which has now seen 2022 data, was
asked to reconstruct 2022 diaries. It used the real 2022 respondent information. On weekdays this
scored 0.0630, also within the 0.10 ceiling.

**Weekends do not meet the ceiling.** On weekends both checks score well above 0.10. The
held-out-year test scores 0.1817 (Saturday) and 0.1843 (Sunday). The backcast scores 0.1637 and
0.1618. No looser weekend ceiling is used.

The weekend gap is concentrated in one identifiable part of the evaluation set. That set mixes two
kinds of rows. The first kind is diaries genuinely observed on that day type. The second kind is
diaries the model had to synthesize, because the respondent reported a different day type. On the
genuinely observed 2022 weekend diaries alone, the distance is 0.036 (Saturday) and 0.040 (Sunday).
Both are well inside the 0.10 ceiling. The synthesized rows sit 0.138 to 0.175 from the observed
distribution. Weekend diaries are fewer, and weekend behaviour is more varied. Raising the weekend
training weight twice moved the score by about 0.005. The gap therefore does not appear to be an
optimization shortfall. The synthesized weekend days are a limitation of the diary completion step.

## S4 Post-hoc calibration (raking) cost

After the model generates diaries, a calibration step called raking is applied. It nudges the
generated at-home percentages, slot by slot, to match their target values exactly. The step is
needed because the raw generated output is close to, but not exactly at, the target at-home
percentages. The cost is that roughly 1.8 to 2.1% of individual slot-records end up with a
mismatched activity label. Their activity label no longer matches their own at-home flag. An example
is a slot still labelled with an "away" activity after being nudged to "at home". This is treated as
harmless for the building energy model. That model reads only the at-home flag to decide occupancy.
It does not read the activity label for that purpose.

## S5 From one diary day to a full year of hourly values

**Two separate reductions turn one diary day into part of a year-long hourly schedule.** The
underlying diary has 48 half-hour slots per person per day. The first reduction folds each person's
day down to 24 hourly values. It averages each pair of half-hour slots: hour h takes the average of
slots 2h and 2h+1. It then averages across every member of the household. This gives one occupancy
fraction and one metabolic rate per household per hour. The survey diary starts its clock at 4 a.m.,
not at midnight. The 24 hourly values are therefore shifted by 4 hours, so that hour 0 lines up with
real midnight. This matches the weather file's clock.

The second reduction concerns day types. Each household ends up with only two 24-hour profiles, a
Weekday profile and a Weekend profile, not seven separate days. Section S7 describes how a household
gets both profiles when the survey observed only one day (the donor draw). Section S9 describes how
those two 24-hour profiles become 8,760 hourly values covering a full simulated year.

## S6 Day-type strata: why weekday, Saturday and Sunday are handled separately

Each survey respondent reports a diary for exactly one day. That day is recorded as one of three
strata: a weekday, a Saturday or a Sunday. The three strata are kept separate through the earlier
stages of the pipeline, namely the generative model and the raking step. This is because at-home
behaviour genuinely differs across all three, not just between weekdays and weekends. In the 2022
stock, the daily at-home share is 74.1 percent on weekdays, 76.0 percent on Saturdays and 78.9
percent on Sundays. These shares are per person, unweighted, and averaged over the 48 half-hour
slots of the day.

When the schedule is handed to the building energy model, the three strata are reduced to two.
Saturday and Sunday are pooled into a single Weekend profile. Only the Weekday and Weekend profiles
are carried forward. This is a deliberate simplification with a known cost. Pooling loses the
calibrated difference between Saturday and Sunday entirely, in both years. In the same unit as above,
the lost difference is 2.9 percentage points in 2022 (Saturday 76.0 percent, Sunday 78.9 percent).
It is 2.3 points in the 2030 main scenario (Saturday 77.9 percent, Sunday 80.2 percent). In both
years people are at home more on Sunday. This is a limitation of the two-day-type design. The
building energy model consumes only a Weekday/Weekend schedule. Carrying a third day type through to
that stage would require changing the building energy model itself.

## S7 The donor pool and the draw rule for completing a missing day type

**What problem this step solves.** Each respondent reports only one day. Most households therefore
have a diary for only one of the two profiles a schedule needs, Weekday or Weekend. Before a
household's schedule can be built, the missing profile has to be filled in. This step is separate
from, and later than, the demographic donor-matching that assigns every household its first diary
(covered in the main text). That earlier step decides which diary a household starts with. This step
decides what happens to the day type that diary does not cover.

**The donor pool.** The pool for a missing day type is simple. It is every person-record in the same
year's data that already carries the needed day type. A household missing its Weekend profile draws
from every record tagged Saturday or Sunday. The two days are pooled into one donor pool, matching
the Weekend target. A household missing its Weekday profile draws from every record tagged weekday.
Unlike the earlier demographic donor-matching step, this donor pool is not narrowed by any
demographic key, such as age, sex or household size. Any record of the right day type is eligible.
Only the recipient household's own dwelling and household attributes are kept, such as household
size, dwelling type and province. The donor supplies only the activity sequence and at-home flags
for the missing day. For the 2030 scenario year, the donor pool is the already-assembled 2030 file
itself. A donor's occupancy therefore still reflects the 2030 scenario rather than 2022 behaviour.

**The draw rule.** The draw is made once per household member who needs the missing day type, not
once per household. Each such member independently draws its own donor row from the pool described
above. Two members of the same household missing the same day type can therefore get donors from two
different donor households. The draw uses a fixed random-number seed (seed 42). Given the same input
file, the same recipient always receives the same donor row. Running the completion step twice on the
same input produces byte-identical output. The per-member draw has a direct consequence for imputed
days. Their within-household presence pattern, meaning who is home at the same time as whom, is
synthetic, not observed. This is treated as harmless to the building energy model specifically. That
model reads only each household's overall occupancy fraction and metabolic rate for each hour. It
does not read which individual members are home together.

**Why a donor draw rather than a copied day.** An earlier version of this step filled a missing day
by copying the household's own observed day onto the missing slot. For example, a Weekday-only
household's Saturday and Sunday would simply repeat its Weekday diary. This biased the calibrated
weekend average downward by 2.76 percentage points. The reason is that a household's own weekday
diary carries weekday behaviour into a weekend slot. Weekend at-home rates are the higher of the two.
The donor-draw method was adopted specifically to remove this bias, and it does. It draws a genuine
weekend (or weekday) diary rather than repeating the household's own day. The calibrated weekend
marginal is therefore preserved rather than diluted.

**Historic years use the same mechanism, restricted to their own year.** The 2005, 2010 and 2015
schedule files are built by a separate copy of this same completion step. It is applied only after
each cycle's own diaries have been assembled onto the analytical household frame. The donor pool for
a historic year is drawn only from that year's own diary pool. A 2015 household's missing day type
can therefore never be filled from a 2005 or 2022 record.

## S8 Household sampling for the building simulation

**A separate draw from the donor draw above.** After the schedule files are finished, 50 households
are drawn for each city-and-building-type group used in the building simulation. The draw is without
repeats, unless a group has fewer than 50 households. In that case, draws with repeats are used. The
same 50 households can then be run through the simulation for every year, on the same building and
weather file. This household sample is unrelated to the day-type donor draw of Section S7. It
happens afterward, on the finished schedule files. It decides which households are simulated, not
what those households' schedules contain.

**The sampling pool is not simply "every household in the file."** Before the 50-household sample
is drawn, the finished schedule file passes through a sanity check. The check looks at each
household's 24-hour Weekday and Weekend patterns. It drops any household whose pattern looks
physically implausible. Two rules do the work. The first is a minimum of two occupied hours in a day
type. The second is a limit on how many times presence may switch on and off within the day. Only
households that pass this check are eligible to be sampled. The sampling pool therefore depends on
the exact numeric content of the schedule file, not just on which households are listed in it.

**The two-hour rule interacts with the reversion scenarios, and the direction matters.** The rule
removes households shown as occupied for less than two hours in a day type. The reversion scenarios
are precisely the ones in which time at home falls. The rule therefore preferentially removes the
households that reverted most. What remains leans very slightly toward households that reverted
least. Measured on all 144,465 households, the ordinary 2030 file already excludes 983 households
under these rules. The scenario files exclude a few more. The excess is 27 in the half-reversion
scenario, 70 in one full-reversion arm and 161 in the other. The largest excess is therefore 161
households, or 0.11% of the stock. This bounds the arithmetically possible shift in the national
at-home share at 0.11 percentage points. That bound is inside the 0.5-point tolerance set in advance,
and the realized effect is a fraction of it. The bound is nevertheless several times larger than the
margins by which the scenarios reach their design targets. Those margins are 0.005 to 0.022
percentage points.

**Consequence for the comparison with the earlier simulation campaign.** The schedule files used in
this paper are numerically close to, but not identical to, those of the authors' earlier simulation
campaign (Section 3.6). The sanity check reads the numbers, so it can drop a slightly different set
of households from each version. This holds even though both versions cover the same 144,465
households. For single-detached houses in Montreal, the check drops 103 of 16,430 candidate
households from the 2022 file. It drops 104 from the 2030 file. This leaves a paired pool of 16,326
households, meaning households present and passing the check in both years. The same check applied
to the earlier files leaves a paired pool of 16,208. The two pools differ by 320 households, counting
households in one pool but not the other. The same fixed seed therefore draws a different
50-household sample from each pool. Each draw is deterministic and reproducible from its own files.
The two samples overlap substantially but are not identical. The comparison with the earlier
campaign is therefore not household-paired.

Kelowna and Vancouver share one British Columbia household pool. Across all city and building-type
groups, the stock therefore holds 134,262 distinct candidate households. The check drops 918
households (0.68 percent) from the 2022 file and 921 (0.69 percent) from the 2030 file. From the
earlier files, it drops 797 (0.59 percent) and 1,043 (0.78 percent).

## S9 Assembly to the full year and the reduction to hourly resolution

Each household's finished Weekday and Weekend 24-hour profiles are written into the building energy
model as one schedule object per channel. The channels are occupancy, metabolic heat gain, and the
equipment and lighting channels added by the end-use layer. Each object carries a single calendar
block that runs from January 1 through December 31. The block has two named sub-patterns, one for
weekdays and one for weekends. The building energy model's own calendar expands these two 24-hour
patterns into the 8,760 hourly values that the simulation runs on. This expansion is not a separate
step in this pipeline. For each calendar day of the year, the calendar looks up whether that day is a
weekday or a weekend day. It uses the ordinary Monday-through-Sunday calendar. It then repeats the
matching 24-hour pattern for that day. No holidays are distinguished, because the weather files used
carry none. Two artificial sizing days are used to size the building's heating and cooling
equipment. They are forced onto the weekday pattern. Equipment sizing is therefore based on the
busier of the two profiles rather than a fixed separate assumption.

The schedule is never handed to the building energy model at its original 30-minute diary
resolution. Only the hourly reduction from Section S5 is presented at this stage. The finest temporal
detail the building simulation ever sees for occupancy, internal heat gain, plug loads or lighting is
therefore one value per hour. That value is for one of two day types per household, expanded to a
full year by the calendar rule above.

## S10 Does household clustering change the reported uncertainty?

The paired-difference interval of Section 2.6 (Eq. 5) pools every household's 2022-to-2030 change.
It treats each change as an independent observation. In principle, households sharing a city or an
archetype are not independent. A cluster bootstrap was therefore run for comparison. The 24
(archetype, city) cells are resampled with replacement: 24 drawn from 24, repeats allowed. Each drawn
cell keeps its own paired household deltas intact. There is no resampling within a cell, since the
cell is itself the resampling unit. The pooled mean is recomputed over 10,000 replicates (fixed seed
12345) to build a percentile interval.

Both methods were applied to the paired 2022 and 2030 simulation results. These cover 24 cells of 50
households, or 2,400 households. Table S3 gives the intervals from the two methods. All values in
Table S3 are fractions; multiply by 100 for percentage points.

**Table S3.** Clustering-aware versus plain paired-difference confidence intervals for midday share and load factor.

| Metric | Method | Point | 95% interval | Width | Change from plain interval |
|-------------|-------------------------------|-----------|--------------------|-----------|--------------|
| Midday share | Plain pooled (Eq. 5) | 0.00732 | [0.00645, 0.00819] | 0.00174 | n/a |
| Midday share | Cell-cluster bootstrap | 0.00732 | [0.00616, 0.00859] | 0.00243 | 39.8% wider |
| Load factor | Plain pooled (Eq. 5) | 0.00494 | [0.00412, 0.00577] | 0.00165 | n/a |
| Load factor | Cell-cluster bootstrap | 0.00494 | [0.00413, 0.00574] | 0.00161 | 2.3% narrower |

For midday share, accounting for clustering by city and archetype widens the interval by about
two-fifths. The interval still excludes zero, so the 2022 to 2030 change remains distinguishable from
zero. The main text therefore reports the wider, clustering-aware interval for this metric. For load
factor, clustering makes almost no difference. The interval is 2.3 percent narrower, which is within
the bootstrap's own replicate-to-replicate variation. The plain pooled interval is therefore
adequate. Neither interval crosses zero under either method.

## S11 Supplementary figures

Figure S1 shows how the uncertainty of the 2022 to 2030 change depends on sample size. It plots the
half-width of the 95 percent confidence interval against sample size for six load-shape and energy
metrics. It covers the four archetype cells in Montreal (climate zone 6A). Sample sizes are 10, 20,
50, 100, 150 and 200 households. Below 200 households, the half-width is the 2.5th to 97.5th
percentile spread of 1,000 bootstrap subsample means. These means are drawn from the same
200-household set. At 200 households (stars), the half-width is a parametric interval on the full
sample. This is a different statistic, which is why the stars sit above the 150-household points.

![](../impl/T94_out/figS1_sample_size.png){width=16cm}

**Figure S1.** Confidence-interval half-width of the 2022 to 2030 change against sample size.

Figure S2 shows how stable the model selection is when the selection thresholds change (Section S2).
Each panel shifts one threshold, or all four together, by minus 20, minus 10, plus 10 and plus 20
percent. This gives 21 distinct scenarios, including the original thresholds at 0 percent. The y-axis
gives the number of candidates that meet all four checks. The marker shows which candidate is
selected. This is the candidate with the lowest composite score among those that meet all four
checks. The chosen model is selected in 19 of the 21 scenarios. The exceptions are a 20 percent
tightening of the at-home error threshold, alone or with the other three. In those scenarios, only
one other candidate meets all four checks.

![](../impl/T94_out/figS2_threshold_sensitivity.png){width=16cm}

**Figure S2.** Stability of model selection when the selection thresholds change.
