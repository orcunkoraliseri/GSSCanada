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

---

## Number trace table

| Value as written | Results subsection |
|---|---|
| 0.1209 percent, rounded to 0.12 percent (main-scenario whole-building electricity change) | 3.3 |
| 0.73 percentage points (midday share change, cluster-aware) | 3.4 |
| 0.49 percentage points (load factor change) | 3.4 |
| Full-reversion scenario: small real fall in annual electricity (0.1225 percent) | 3.2 |
| Partial-persistence scenario: no detectable change (0.0117 percent, interval contains zero) | 3.2 |
| Standardized-reversion variant: largest change of the three (0.4408 percent) | 3.2 |
| Full model vs average-profile method: close annual totals (8,225.56 vs 8,951.40 kWh, one illustrative cell), very different household peak-timing spread (3.493 h vs 0.084 h, 2022) | 3.5 |
| Simulated vs measured Toronto/Ontario 2022: peak hour 17.0 vs 18.69, peak-to-average 2.1367 vs 2.3231 | 3.6 |

## Reviewer items closed

- **Q13** (Conclusion says EUI is consistent with SHEU ranges, contradicting Results) -- CLOSED for the
  Conclusion portion by removal, not reconciliation: no energy-use-intensity figure exists in this
  rebuild (`draft_S3_results.md` carries only `[NUMBER NEEDED: EUI]`), so this draft makes no EUI claim
  and no "consistent with" wording anywhere. The Results-section half of this row is not this task's
  responsibility and is unchanged from `draft_S3_results.md`'s own handling.
- **Q18** (the manuscript's "+2.2 to +3.9 pp" figure is defined two incompatible ways) -- CLOSED for
  the Conclusion portion: that figure, and any pre-pandemic-to-2030 percentage-point figure, is retired
  per plan log (ds) and does not appear anywhere in this draft. Every percentage-point figure quoted
  here (0.73, 0.49) is a single, already-disambiguated 2022-to-2030 change taken directly from Results,
  not a level above a pre-pandemic baseline. The Abstract and Results portions of this row are out of
  this task's scope.
- **R3-1** (update every affected figure, interval and conclusion on the corrected household data) --
  CLOSED for the Conclusion portion: every number in this draft's five findings traces to the rebuilt
  Results sheet (Sections 3.2 to 3.6 of `draft_S3_results.md`, entry (du)), none to the archive. The
  Results and Abstract portions of this row are handled elsewhere (T81/(du) for Results; the Abstract is
  not part of this task).

## CITATION NEEDED list

None. This draft states no outside claim; every sentence either restates a Results number in plain
words or is a scope statement about what the paper itself did.

## Open for the manager

1. Pre-pandemic at-home levels (2005, 2010, 2015 cycles) and the size of the 2015-to-2022 break are not
   included in this Conclusion. `draft_S3_results.md` Section 3.1 still carries two `[NUMBER FROM T80]`
   placeholders for these figures, and T80 (job 1341375, per plan log (du)) had not been collected as of
   this task. The task doc allows omitting them ("only if you need them at all"); this draft judged the
   five findings above complete without them and left them out rather than wait on T80. If the manager
   wants a sixth finding on the pre-pandemic-to-2022 break once T80 lands, it would need its own sentence
   here, added after the fact.
2. The practical-message paragraph (paragraph after the five findings) is this task's own synthesis of
   "annual demand changes little, timing changes more, plan accordingly" from the findings above; it is
   not a quoted Results sentence. Flagging it as the one paragraph in this draft closest to
   interpretation rather than restatement, for the manager to check against the Discussion's own framing
   for consistency.
3. The three future-work items are matched to Section 5's limitations by this task's own reading
   (typical-year weather, the partial scope of the measured check, and the citation-needed post-2022
   work-from-home trend from the Discussion draft). If the manager wants a future-work item on the
   before-and-after household pool mismatch, the metabolic heat channel, or the collection-mode
   confound instead of or in addition to these three, that is a manager-level choice among Section 5's
   eleven limitations, not decided here.

## WHAT I DID NOT VERIFY

- Did not open any T-numbered `impl/` file, CSV, or cluster output directly; every number above is
  copied from `draft_S3_results.md`'s own prose or its Number trace table, not re-derived from a raw
  file.
- Did not check whether T80 (job 1341375) has finished or what values it produced; this draft does not
  use any T80 number, per the "only if you need them at all" allowance, so this was not chased further.
- Did not read `manuscript/prep/response_map.md` beyond the rows already identified by the manager's
  own grep pass recorded in this session.
- Did not check this draft's wording against `draft_S7_limitations.md` sentence by sentence for
  consistency beyond matching three future-work items to three named limitations; a full cross-section
  consistency pass was out of scope.
- Did not verify Applied Energy's own house-style rules for a Conclusion section beyond the
  plain-language, no-symbol and word-count rules given in the task doc.
- Word count reported in the final summary is a plain word count of this file's body text (excluding
  the trailer sections below the horizontal rule), not a typeset or submission-system count.
