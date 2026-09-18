# S7. Limitations

This work has eleven limitations. The first eight bear directly on the results reported above; the
last three are disclosed here although no reviewer raised them. Each is stated in plain terms,
together with what it does and does not affect.

**Scope.** The study covers six Canadian cities (Toronto, Kelowna, Vancouver, Montreal, Calgary and
Winnipeg) and four dwelling types (single-detached houses, other low-rise houses, mid-rise apartments
and high-rise apartments), built from one country's time-use survey (Canada's General Social Survey).
No other country's time-use data is used, and the six cities do not represent every Canadian climate.
The check against real-world data is a comparison to measured residential electricity load shapes for
Toronto and the province of Ontario, over shoulder-season weekdays only; it is not a whole-building
energy measurement (it excludes natural gas heating and is not available for the other five cities or
for winter and summer conditions), so it should be read as a shape check, not a full energy validation.

**The before-and-after schedules are not matched household by household.** The chosen model of
occupant behaviour was rebuilt on diaries drawn only from the most recent survey year, replacing an
earlier build that mixed in older survey years. This rebuild changes which households pass the
simulation engine's own data-quality check, so the pool of households actually simulated is not the
same pool as in the originally submitted results: for one representative city-and-type cell (single-
detached houses in the Montreal region), the rebuilt pool holds 16,326 paired households against 16,208
in the original, a difference of 320 households, and the same random seed therefore draws a different
sample of households in the two versions. Comparing the two versions is a like-for-like comparison of
model versions, not a household-paired before/after study, and the paper states this plainly wherever
the two are placed side by side.

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

**Weekend behaviour is harder to reproduce than weekday behaviour.** The project fixed one
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
and the exact same person-to-diary assignments as the chosen 2022 stock; only each household's
probability of being home in a given time slot is shifted, by an amount equal to eight times a linear
trend fitted to real respondents from 2005, 2010 and 2015 (the years before the survey was disrupted),
clipped to stay between 0% and 100%. No uncertainty range, no policy change, and no alternative
trajectory for remote work or household composition is built into this projection: it extends one
historical trend forward by a fixed amount on a fixed population. The paper's scenario range (partial
and full versions of this same shift) should be read as bounding one assumption about how far a
pre-existing trend continues, not as a probabilistic forecast of 2030 occupancy.

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
scenarios above (which extend a trend fitted partly across this same 2015-to-2022 boundary), carries an
amount of survey-design effect that this study cannot measure or remove.

**Three further limitations, not raised by reviewers but disclosed here.** First, the 2030 schedules
use the same typical-year weather file as 2022, not a projected future-climate weather file, so the
results isolate the effect of behaviour change from the effect of a changing climate. Second, matching
census households to survey diaries assumes that, once the matching characteristics are accounted for,
the diary is otherwise assigned independently of anything not captured by those characteristics; this
assumption cannot be tested directly with the data used here. Third, the metabolic heat given off by
occupants is taken from a standard per-person value and is not independently calibrated against
measured internal gains in this study.

---

## Claim trace table

| # | Claim | Plain sentence carrying it | Source (file:line) | Matches source | Notes |
|---|-------|------------------------------|---------------------|-----------------|-------|
| 1a | Six cities, four archetypes | "six Canadian cities ... and four dwelling types" | `writing/Prompts/2J_manager_prompt_RESUME_AE_resubmission.md:59-61` | Yes | Archetypes SingleD, OtherDwelling, MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B, Winnipeg_7A |
| 1b | One country's time-use survey; measured check is partial (Toronto/Ontario electricity, shoulder weekdays only) | "one country's time-use survey ... a shape check, not a full energy validation" | `impl/2026-09-15_T09_wp5_sim_vs_measured_toronto.md:11-13,38-41,150,182-186` | Yes | T09 confirms Electricity:Facility only, Toronto + Ontario, shoulder-weekday n_days=82 |
| 2 | Rebuilt pool 16,326 vs published 16,208, difference 320 households, one cell | "the rebuilt pool holds 16,326 paired households against 16,208 in the original, a difference of 320 households" | `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438` | Yes | Matches task doc's numbers exactly; also plan log `00_REVISION_PLAN.md:958-968` entry (ak) |
| 3 | One envelope only; window U/SHGC for dominant glazing type not found; WP7.3 not run | "only one building envelope is used ... existing-stock envelope variant was not built" | `impl/2026-09-15_T31_wp7_existing_stock_envelope.md:408-412,417` | Yes | Dominant glazing = Swan code 200, double glazed clear 13mm air, 74.0% of single-detached window area; also plan log `00_REVISION_PLAN.md:1004-1010` entry (aq) |
| 4 | Validator check 3.5: 75.04% vs 72.3% anchor, band 2pp, FAIL, real weighted 2022 donors at 72.31% | "the chosen 2022 housing stock scores 75.04% against a 72.3% anchor, a gap of 2.74 points" | `impl/2026-09-15_T18c_wp1_frame_v2.md:56-58,61` | Yes | Task doc omitted the 2.74pp delta figure; added here from source. Also plan log `00_REVISION_PLAN.md:879-886` entry (aa) |
| 5 | Weekend ceiling 0.10, weekday 0.0619/0.0630 pass, weekend 0.1817/0.1843 (held-out) and 0.1637/0.1618 (backcast) fail, observed-only weekend 0.036/0.040, synthesized 0.138-0.175, up-weighting moved score ~0.005, 0.20 ceiling disclosed but unused | "Saturday and Sunday do not meet this ceiling ... moved this gap by only about 0.005" | `manuscript/draft_SI_model_selection.md:95-128` | Yes | Matches task doc's numbers exactly (0.036/0.040 vs 0.138-0.175, ~0.005 movement) |
| 6 | 2030 = same stock persons/diaries, target = clamp(stock_rate + 8*pre_slope, 0, 1), pre_slope from real 2005/2010/2015 respondents, no uncertainty range built in | "only each household's probability of being home ... is shifted, by an amount equal to eight times a linear trend" | `impl/2026-09-15_WP1_step2_retargeting_spec.md` (Section 3, "Chosen design (D1, delta on the stock)") and `impl/2026-09-15_T20_wp1_d1_2030_build.md:9-18` | Yes | Formula identical in both files: `target[s,t] = clamp(stock_rate[s,t] + 8 x pre_slope[s,t], 0, 1)` |
| 8 | Saturday and Sunday pooled into one weekend pattern at the building-model interface; the day-type map is `{1,2,3} -> {Weekday, Weekend, Weekend}` | "Saturday and Sunday are pooled into that single weekend pattern" | `2J_docs_occ_nTemp/07_aug_to_bem.py:34`; `2J_docs_occ_nTemp/07_bemIntegrationGSS.md:60-68`; plan `00_REVISION_PLAN.md:481` (S5, item 5) | Yes | Added by the manager 2026-09-15 (log (bc)) after the SI schedule-completion draft settled it. The size of the lost difference is PENDING on the rebuilt runs, so no number is quoted here. |
| 9 | GSS diary collection moved from telephone interview (CATI) to a self-administered electronic questionnaire (EQ) starting with the 2022 cycle, the same cycle that carries the pandemic/WFH at-home shift; `COLLECT_MODE` is 0 for 2005/2010/2015 and 1 only for 2022, so mode and behaviour cannot be separated in this design and neither a mode effect nor its absence can be shown from these data | "This change in collection method lands on exactly the one survey year, 2022 ... the two changes cannot be told apart with these data" | `00_REVISION_PLAN.md:550-558` (§5, "New, currently unassigned work"); `deepResearch/dr_2J-12_VETTING.md:127-132,195-197` | Yes | New limitation added this task (T43); not re-derived, taken from dr_2J-12's already quote-checked/Crossref-corroborated finding per the task's instruction; classified here as reviewer-adjacent (R3-3 asks to "list other concurrent changes as a limitation") rather than in the reviewer-unraised group below, a judgement call recorded in the implementation doc |
| 7a | TMY (typical-year) weather, not future weather, used for 2030 | "the 2030 schedules use the same typical-year weather file as 2022" | `00_REVISION_PLAN.md:472` (S5, item 1) | Yes | Found under S5 "Weaknesses the reviewers did not raise", not literally under a S9 checkbox; recorded per task item 7 instruction |
| 7b | Census-GSS match rests on conditional independence | "matching census households to survey diaries assumes ... independently of anything not captured by those characteristics" | `00_REVISION_PLAN.md:474` (S5, item 3) | Yes | Same S5 list as 7a |
| 7c | Metabolic heat channel not independently calibrated | "the metabolic heat given off by occupants ... is not independently calibrated" | `00_REVISION_PLAN.md:475` (S5, item 4) | Yes | Same S5 list as 7a |
| 7d | One climate-zone envelope for all six cities (Atlantic households on Montreal weather file) | Folded into the envelope paragraph as "every simulated building uses the current building-code envelope regardless of its true vintage" (scope of "one envelope" widened) | `00_REVISION_PLAN.md:473` (S5, item 2) | Partial | S5 item 2 is about one climate-zone envelope across all cities; the main-text paragraph focuses on the vintage (existing-stock) envelope per the task's limitation #2. Both share the same root cause (T31 closed without runs); not given a separate sentence to avoid diluting the primary claim. Flagged in WHAT I DID NOT VERIFY. |

## Ledger
- No cluster jobs run. Read-only local task: grepped and read `00_REVISION_PLAN.md`, `2J_manager_prompt_RESUME_AE_resubmission.md`, and six `impl/` task docs plus `manuscript/draft_SI_model_selection.md`, all under 600 lines each; no multi-MB file opened whole.

## Verified
- Plan log entries (aa) `00_REVISION_PLAN.md:879-886`, (ak) `:958-968`, (aq) `:1004-1010` read in full.
- Manager prompt §0 engine facts (archetypes/cities) read at `2J_manager_prompt_RESUME_AE_resubmission.md:59-61`.
- `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438` read: new paired pool 16,326, published paired pool 16,208, symmetric difference 320 (task doc's "16,326 vs 16,208, 320 households" confirmed exactly).
- `impl/2026-09-15_T31_wp7_existing_stock_envelope.md:408-412,417` read: window NOT FOUND, rule 8 fires, WP7.3 not run, one-envelope limitation stated in the doc's own words.
- `impl/2026-09-15_T18c_wp1_frame_v2.md:56-58,61` read: 75.04% vs 72.3%, delta 2.74pp (task doc did not state the delta; added here), band 2pp, FAIL; split figures 72.31% (weighted real donors), 74.31% (real unweighted), 75.95% (synthetic donors, n=126,072).
- `manuscript/draft_SI_model_selection.md:95-128` (Section S.3) read in full: all weekend numbers match the task doc's numbers exactly, including the ~0.005 up-weighting movement.
- `impl/2026-09-15_WP1_step2_retargeting_spec.md` read in full (94 lines): Section 3 "Chosen design (D1, delta on the stock)" gives the exact target formula.
- `impl/2026-09-15_T20_wp1_d1_2030_build.md:9-42` read: same formula confirmed independently in the build doc, status COLLECTED, N0-N3 PASS.
- `00_REVISION_PLAN.md:470-483` (Section S5, "Weaknesses the reviewers did not raise") read in full for the task's item 7 (additional decided limitations): used items 1, 3, 4 as separate sentences; item 2 folded into the envelope paragraph (see trace row 7d).
- `impl/2026-09-15_T09_wp5_sim_vs_measured_toronto.md:1-41,150,174-186` read for the scope paragraph's claim that the measured check is Toronto/Ontario electricity only, shoulder-season weekdays.
- Searched `00_REVISION_PLAN.md` for a literal plan-log entry "(ba)" (the task doc's header cites "plan log (ba)" as the entry that commissioned T37): not found by grep; the log runs through entry (az) at the point this session read it. Recorded as a discrepancy below, not corrected silently.

## Decisions (T43, 2026-09-17 addition)
- 2026-09-17, manager: plan §5 item 22 CLOSED by **option (b)**. The eleventh limitation's one
  outside-literature sentence is removed and replaced by what this project's own data supports: the
  `COLLECT_MODE` indicator is 0 for 2005/2010/2015 and 1 only for 2022, so the mode change and the
  pandemic shift are perfectly confounded and neither a mode effect nor its absence is demonstrable
  here. No citation is now owed, and none may be invented. The limitation still stands on its own
  evidence, which was the plan's stated reason for declaring option (b) sufficient. The table row for
  this limitation was softened in the same way; `dr_2J-12_VETTING.md:127-132,195-197` stays in the
  source column as the provenance of the finding, not as a citation in the prose.
- Added an eleventh limitation (the CATI-to-EQ survey collection-mode confound, `dr_2J-12` CARRIED item,
  plan `00_REVISION_PLAN.md:550-558`) as its own paragraph, placed after the "Saturday and Sunday are
  simulated as one day" paragraph and before the "Three further limitations" bundle. Opening-sentence
  count updated from "ten ... first seven" to "eleven ... first eight". Checked the existing ten for
  overlap: limitation 6 (2030 scenario) mentions "the years before the survey was disrupted" but never
  names the CATI-to-EQ mode change; no existing limitation states the mode change or the confound, so
  this is not a duplicate. Cross-referenced limitation 6 explicitly from the new paragraph ("the 2030
  scenarios above") instead of repeating its content. Classified the new item among the "first eight"
  (reviewer-adjacent) rather than the "last three, no reviewer raised them" group, because Reviewer 3's
  own request 3 in the plan ("list other concurrent changes as a limitation") is the closest existing
  reviewer hook for this item; this is a judgement call, not dictated by the task brief, and is flagged
  in the new implementation doc.

## Decisions
- Where the task doc's list (items 1-6) and the source files agreed exactly, no numbers were changed. The one number the task doc omitted (the 2.74pp delta on validator check 3.5) was added from the source per the "source wins, record both" rule; there is no disagreement, only an addition.
- Item 7 ("§9 closure boxes"): the literal §9 checklist (`00_REVISION_PLAN.md:565-580`) contains only meta-checklist rows (e.g. "WP2-WP9 done or explicitly declined"), not itemised limitations. The itemised list of additional, reviewer-unraised limitations lives instead in Section S5 (`:470-483`), which Section S10's Wave-5 audit prompt (`:658-659`) also treats as the standing limitations list. Used S5 as the source for item 7 rather than leaving it blank, and recorded this substitution here rather than silently treating S5 as "§9."
- Of S5's five items (TMY weather, one envelope for all cities, conditional independence, metabolic heat channel, weekend pooled into one day type), item 5 ("weekend pooled into one day type; hourly reporting") was not given its own sentence: it is a different claim from the already-covered synthesized-weekend limitation (item 3 in the task list) and would need its own source check beyond this task's scope; flagged below as not verified/not included, not silently merged.
- Item 2 of S5 (one climate-zone envelope for all six cities) was folded into the main envelope paragraph rather than given a separate paragraph, since both trace to the same T31 closure (no separate existing-stock envelope exists, so "one envelope" already covers "one envelope everywhere"). Recorded as a partial match in the trace table (row 7d) rather than a clean one-to-one.
- No `[VALUE PENDING]` placeholders were needed: every number used was already produced by a rebuilt-run source file (ruling (b) satisfied) or by the pre-rebuild plan/manager-prompt facts (city/archetype list, S5 items), which are not simulation-campaign numbers.

## Next
- None from this task's side; draft and trace table are complete. Manager to fold this section into the assembled manuscript and re-run the T-AUDIT provenance check against the same source files at final assembly (source lines given above make that check mechanical).

## WHAT I DID NOT VERIFY
- The task doc's header cites "manager. Written 2026-09-15 (plan log (ba))" as the entry commissioning T37; grep found no entry literally labelled "(ba)" in `00_REVISION_PLAN.md` (the log runs (aa) through (az) at read time). Did not chase this further since it does not change any limitation's content; noting it so the manager can check whether (ba) exists elsewhere (e.g. was written after this session started reading, or is a typo for a nearby letter).
- S5 item 5 ("weekend pooled into one day type; hourly reporting") was read but not traced to a further source or included in the draft; it may be a distinct, sixth reviewer-unraised limitation that still needs its own sentence and citation.
- Did not independently re-verify T18c's or T21's own upstream numbers (e.g. did not re-run the validator or the engine's schedule sanity check); took the task docs' own Verified/Ledger sections as the source, per this task's scope (local reading only, no cluster, no recomputation).
- Did not check whether `manuscript/draft_S7_limitations.md` conflicts in wording or numbers with any other already-drafted section (`draft_S2_framework.md`, `draft_SI_model_selection.md` outside S.3) since the task doc scopes this task to writing S7 only, not cross-section consistency.
- Did not verify current word/paragraph-count conventions for an Applied Energy limitations subsection (e.g. target length); wrote to the content the task specified, not to an external house-style length rule.
