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

The paired, within-household design used throughout Sections 3.1 to 3.4 is what lets a change of this
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

For grid planning, the practical reading of Section 3.4 is stated here in plain terms. Under the main
scenario, a larger share of annual energy moves into the middle of the day: midday share rises by 0.73
percentage points. The ratio of average to peak hourly load also rises: load factor rises by 0.49
percentage points. Both changes exclude zero. Peak demand and the evening ramp are reported only as
point values, since no confidence interval is available for either metric, and both fall slightly
under the main scenario, from 47.207 to 46.332 kilowatts and from 7.852 to 7.768 kilowatts
respectively; these two figures describe the simulated stock and are not treated as a tested change.
Timing, not only the annual total, is material to how a grid operator plans for peak demand, the
evening ramp and demand-response programs [CITATION NEEDED: source on why residential load timing, not
only annual energy, matters for grid peak demand, the evening ramp and demand response]. This study
uses 2030 as its horizon because it sits beyond the latest available survey data and because 2030 is a
commonly used planning horizon [CITATION NEEDED: source establishing 2030 as a recognized planning
horizon].

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
[R6-measured].

The activity-resolved equipment and lighting check against the national end-use energy survey (Section
3.3, and Section 1.5's first practical contribution) is, by design, a check against a fitted target
rather than an independent validation: the same survey data that supplies the target also calibrates
the model. On the rebuilt runs, all 48 archetype-by-city-by-year cells fall inside the report-only band
of plus or minus 15 percent around that fitted target. This result shows the calibration behaves as
intended; it is not, on its own, independent evidence that the underlying diurnal shape is correct,
which is why Section 3.6's measured comparison is reported as a separate, second kind of check rather
than folded into this one.

One result in Section 3.3 runs against a simple intuition and is stated here exactly as measured, with
no causal account offered. Under the main scenario, interior lighting and interior equipment both fall
very slightly from 2022 to 2030, lighting by 0.0157 percent and equipment by 0.0066 percent, both
changes excluding zero, at the same time as the at-home share and the midday share both rise. This
paper does not claim that more time spent at home produces more plug load; on this rebuild, these two
meters move in the opposite direction from that intuition, and that is reported here as the result.

The scenario spread in Section 3.2 rests on an open question this paper's own material does not
settle: what happens to work from home after 2022 (Section 1.3). In Canada the share of workers
mostly working from home fell from 41.1 percent in April 2020 to 18.7 percent in May 2024
[CITATION NEEDED: StatCan Daily, telework share]. If that fall continued after 2022, the
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
rebuild the same generator, the same held-out-year evaluation, and the same paired stock-scale design
for its own housing stock; only the resulting magnitudes would be expected to differ. Section 5 states
the scope and data limitations that bound this study; nothing above should be read as contradicting
that section.

---

## Number trace table

| Value as written | Results subsection |
|---|---|
| 0.1209 percent (main-scenario whole-building electricity change) | 3.3 |
| Full-reversion, partial-persistence, standardized-reversion scenario comparison | 3.2 |
| 0.73 percentage points (midday share change, cluster-aware) | 3.4 |
| 0.49 percentage points (load factor change) | 3.4 |
| 47.207 to 46.332 kW (peak demand, point values) | 3.4 |
| 7.852 to 7.768 kW (evening ramp, point values) | 3.4 |
| 0.00243 vs 0.00174 (midday share interval width, about 40 percent wider) | 3.8 |
| 0.00161 vs 0.00165 (load factor interval width, about 2 percent narrower) | 3.8 |
| 8,225.56 vs 8,951.40 kWh, difference 725.84 kWh (full model vs average-profile) | 3.5 |
| 3.493 h vs 0.084 h (2022); 3.255 h vs 0.053 h (2030) (household peak-hour circular standard deviation) | 3.5 |
| 4 candidates clear all selection checks; 2 of 21 threshold scenarios flip, 19 of 21 unchanged | 3.8 |
| 0.4680 vs 0.4305 (load factor), 0.3787 vs 0.3513 (midday share), 2.1367 vs 2.3231 (peak-to-average), 17.0 vs 18.69 (peak hour) | 3.6 |
| 48 of 48 cells pass, band plus or minus 15 percent | 3.3 |
| 0.0157 percent (lighting fall), 0.0066 percent (equipment fall) | 3.3 |
| 41.1 percent (April 2020), 18.7 percent (May 2024), Canada telework share | Not a Results number; carried from `dr_2J-11_VETTING.md` per the task doc's instruction (point 7), cited `[CITATION NEEDED: StatCan Daily, telework share]` |

## Reviewer items closed

- **M1** (compare the method against an average-profile arm; Discussion should say what the individual
  model adds) -- CLOSED for the Discussion portion. Paragraph 4 ("Section 3.5 isolates what the
  household-level model... adds").
- **D1** (show exactly which results need the household-level random model, not just averages) --
  CLOSED. Same paragraph: the annual total is close under both methods, the peak-timing spread is not.
- **D12** (explain why modelling individual behaviour matters even for whole-stock, aggregate results)
  -- CLOSED. Same paragraph, closing sentence, plus the model-selection paragraph (paragraph 5).
- **Q11** (Discussion cites Table 5 for percentage figures it does not contain) -- CLOSED by
  construction: this draft never names or cites a Table 5, and no percentage figure in it is attributed
  to that table; the archived Table 5 (EUI values) has no rebuilt source and is not used anywhere in
  this manuscript per `draft_S3_results.md`'s own `[NUMBER NEEDED: EUI]` placeholder.

## CITATION NEEDED list

1. Paragraph 3: source on why residential load timing, not only annual energy, matters for grid peak
   demand, the evening ramp and demand response.
2. Paragraph 3: source establishing 2030 as a recognized grid- or climate-planning horizon.
3. Paragraph 8: StatCan Daily reference for the post-2022 Canadian telework-share decline (41.1 percent
   April 2020 to 18.7 percent May 2024), per plan log (dt)/(ds); the author supplies this.

Total: 3. Identical in substance to the three items already flagged in `draft_S1_introduction.md`
(items 1 and 2 reuse the same underlying claim as that draft's items 1 and 2; item 3 reuses that
draft's item 3), since the same two claims and the same evidence gap recur in the Discussion.

## Open for the manager

1. Whether the two grid-planning `[CITATION NEEDED]` tags in this draft and the two in
   `draft_S1_introduction.md` should be filled with the same source in both places once the author
   supplies one, or whether the Discussion needs its own, more specific reference (e.g., on
   demand-response or distribution planning specifically, rather than the general timing-matters claim
   used in the Introduction).
2. Whether the model-selection robustness paragraph (four candidates, threshold sensitivity) belongs in
   the Discussion at all, or would fit better as a shorter pointer to Section 3.8/the Supplementary
   Information; it is included here because Section 1.5's first scientific contribution names the model
   choice explicitly and no other paragraph in this draft answers that contribution, but it is the
   paragraph in this draft closest to restating Results rather than discussing it.
3. Whether "the standardized-reversion variant... may be closer to what actually occurs than the main
   scenario is" (paragraph 8) is a claim the manager wants kept; it is a plain reading of the vetted
   post-2022 decline direction against the four tested scenarios, not a new number, but it is the one
   sentence in this draft that ranks the scenarios by plausibility rather than only reporting them side
   by side.

## WHAT I DID NOT VERIFY

- Did not open any T-numbered `impl/` file, CSV, or cluster output directly; every number above is
  copied from `draft_S3_results.md`'s own prose or its Number trace table, not re-derived from a raw
  file.
- Did not re-read `dr_2J-11_VETTING.md` in full; the two telework-share figures (41.1 percent, 18.7
  percent) are copied exactly as given in this task doc's point 7, which the task doc states are the
  only figures that source confirmed.
- Did not read `manuscript/prep/response_map.md` beyond the rows already identified by the manager's
  own grep pass recorded in this session; did not re-grep the file for additional rows whose "Where in
  new manuscript" column might implicitly cover the Discussion without naming it (for example, a row
  targeting "Throughout" with no explicit Discussion mention).
- Did not check this draft's wording against `draft_S7_limitations.md` sentence by sentence for
  consistency beyond the point-7 (work-from-home decline) and point-2 (grid-timing) claims that this
  task doc specifically flagged; a full cross-section consistency pass was out of scope.
- Did not verify Applied Energy's own house-style rules for a Discussion section (length norms, heading
  conventions) beyond the plain-language and no-symbol rules given in the task doc.
- Word count reported in the final summary is a plain word count of this file's body text (excluding
  the trailer sections below the horizontal rule), not a typeset or submission-system count.
