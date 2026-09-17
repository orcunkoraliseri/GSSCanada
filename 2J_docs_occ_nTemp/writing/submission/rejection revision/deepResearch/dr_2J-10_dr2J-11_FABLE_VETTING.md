# Vetting of dr_2J-10 and dr_2J-11 (Fable, no-search, close-reading returns)

Vetted: 2026-09-16. Method: same as `dr_2J-12_VETTING.md`, adapted for no-search Fable returns (no
DOIs, no external sources, no journal-policy quotes to check). What was done instead: a quote-by-quote
check of every citation against the archived manuscript, re-derivation of every checkable arithmetic or
definitional claim, and a check of the revision plan and the four partial redrafts to sort each report's
top-5 critique items into already-known versus genuinely new. No em dashes or en dashes.

## 0. What text was reviewed

Both returns were run against `writing/submission/archive/2J_manuscript_submission.md` (the submitted,
already-rejected manuscript, 654 lines), the same basis as the `dr_2J-12` Fable run. Both returns state
this themselves and both are correct: the four partial redrafts in `rejection revision/manuscript/`
(`draft_S2_framework.md`, `draft_S7_limitations.md`, `draft_SI_model_selection.md`,
`draft_SI_schedule_completion.md`) do not touch the Introduction, Table 1, or the front matter that
`dr_2J-10` and `dr_2J-11` audit. `dr_2J-11` additionally reads `draft_S2_framework.md` section 2.7 and
`draft_S7_limitations.md` in a separate closing note, kept apart from its main seven sections; that note
was independently re-checked in this pass (section 5 below), not just trusted.

For the cross-check against the plan (task step 3), `00_REVISION_PLAN.md` (1312 lines) was read in full
via a targeted sweep: the reviewer-triage tables (lines 1 to 200), the work-package summaries and the
"weaknesses the reviewers did not raise" list (lines 460 to 529), and the manager's log entries
commissioning and receiving both Fable returns (lines 1230 to 1320), plus a keyword grep across the whole
file for every term either report's top-5 items turn on (novelty, Table 1, C-VAE, persistence, WFH,
system boundary, office, commercial, calibration provenance, scenario, Chen et al., matrix). Of the four
redrafts, only `draft_S2_framework.md` and `draft_S7_limitations.md` were read in full; the two SI drafts
(model selection, schedule completion) were not opened, because neither report's top-5 items touch model
selection thresholds or weekend-completion mechanics, so nothing in this vetting pass depends on them
(recorded in the task doc's WHAT I DID NOT VERIFY, not silently skipped).

## 1. Quote verification (README step 6 style: open the source, find the exact sentence)

Both reports declare up front that they replace the manuscript's em dashes, en dashes, and arrows with
commas or the word "to" inside quotations, and that section/paragraph pointers count prose paragraphs
from the top of the named subsection. Every spot-check below applies that same conversion before
comparing; a quote is marked MATCH when it is verbatim once dashes and arrows are converted back, or when
italics are dropped, and FAIL only if the wording, a number, or the section pointer is actually wrong.

**dr_2J-10 (novelty matrix), 21 quotes spot-checked, 21 MATCH, 0 FAIL:**

| # | Quote (as given in the report) | Manuscript location | Result |
|---|---|---|---|
| 1 | "The open cell that none occupies is a calibrated behavioural occupancy series forecast to 2030 through the work-from-home (WFH) break and carried into stock-scale paired building-energy simulation of the resulting load shape." | line 71 | MATCH |
| 2 | "The open cell that none occupies, and that this study fills, is the simultaneous combination of a calibrated behavioural occupancy forecast carried through the COVID/WFH structural break with stock-scale paired BEM simulation of the resulting load shape." | line 92 | MATCH |
| 3 | "The six-dimension gap matrix of section 1.2 (Table 1) identified an open cell that no prior study occupies" | line 435 | MATCH |
| 4 | "Chen et al. (2022) is the strongest competitor, stock-scale, calibrated, activity-resolved, and load-shape-focused, but retrospective: it does not forecast to a future year." | line 92 | MATCH |
| 5 | "Yin et al. (2024) tracks the very premise this paper builds on, long-term (2001 to 2021) change in time-use behaviour, but stops at statistical analysis: it neither forecasts forward nor runs building-energy simulation" | line 92 | MATCH |
| 6 | "Jalilian and Kamel (2025) forecasts at stock scale to a future year yet holds occupancy static at pre-pandemic schedules." | line 92 | MATCH |
| 7 | "The authors' own prior C-VAE work...would satisfy most of these columns; its delta against the present paper is not a matter of these six binary axes but of the four pipeline-stage advances set out in section 1.4 and section 1.5." | line 90 | MATCH |
| 8 | "five period-specific occupancy datasets (2005, 2010, 2015, 2022, and a synthetic 2025)" | line 107 | MATCH |
| 9 | "a journal treatment across six Montreal neighbourhood-unit typologies in climate Zone 6A over 2005 to 2025" | line 105 | MATCH |
| 10 | "A 2025 hindcast is replaced by a 2030 forecast carried through the structural break" | line 117 | MATCH |
| 11 | "N = 50 household IDs are sampled once" (per cell); "144,507-household building energy model (BEM) frame" | lines 318, 170 | MATCH |
| 12 | "this magnitude is provisional pending a calibration-provenance check described in section 7" | line 368 | MATCH |
| 13 | "the specific magnitude of the 2022 to 2030 step reported in section 5.1 (+2.2 to +3.9 percentage points)...should be treated as provisional pending a recalibration...against the current, post-relink household frame" | line 461 | MATCH |
| 14 | "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one" (cited as section 7 para 8) | line 467; paragraph count confirmed correct | MATCH |
| 15 | Reference-list titles for Reinhart and Cerezo Davila (2016) and Motuziene et al. (2022) | lines 565, 547 | MATCH |
| 16 | "already shown to support residential energy modelling in the United States (Chiou et al. 2011)" | line 122 | MATCH |
| 17 | "it is not itself a novel load-modelling contribution but an application of established methods to the pipeline's output representation" | line 266 | MATCH |
| 18 | "Presence-filtered default end uses are replaced by a SHEU-calibrated, activity-resolved bottom-up end-use model" | line 116 | MATCH |
| 19 | "This design follows the paired stock-scale simulation rationale articulated by Chen et al. (2022)" | line 320 | MATCH |
| 20 | "deliberately does not re-claim as novel, is the premise that survey-grounded time-series occupancy can be built for Canadian building energy models at all" | line 107 | MATCH |
| 21 | "these results establish that time-varying, survey-grounded occupancy schedules are feasible at building-stock scale" | line 487 | MATCH |

Table 1's nine competitor rows were also checked cell by cell against the manuscript's own table (lines
79 to 87): every check mark and cross the report relies on (Chiou, Widen and Wackelgard, Reinhart and
Cerezo Davila, Fischer, Motuziene, Chen, Osman, Yin, Jalilian) matches the source table exactly.

**dr_2J-11 (WFH trajectory), 19 quotes spot-checked, 19 MATCH, 0 FAIL:**

| # | Quote (as given in the report) | Manuscript location | Result |
|---|---|---|---|
| 1 | Central claim, section 3.4 para 4, full sentence on the 2030 forecast as a single high-persistence scenario | line 241 | MATCH |
| 2 | "Work-from-home has settled at roughly four times its pre-pandemic prevalence, about 20% of full workdays after the pandemic against 5% before...and shows every sign of persisting at a new hybrid-work equilibrium" | line 99 | MATCH |
| 3 | "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one; this is framed explicitly as the high-persistence upper bound rather than a central estimate" | line 467 | MATCH |
| 4 | "The 2022 jump...survives standardization...the weekday at-home break at the 2015 to 2022 transition settles at +5.2 pp" | line 370 | MATCH |
| 5 | Standardized series "64.2 / 64.2 / 63.3%" | line 370 | MATCH |
| 6 | "the 2022 to 2030 at-home gap as currently plotted is inflated...should be treated as provisional" | line 461 | MATCH |
| 7 | Highlights: "2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test." | line 24 | MATCH |
| 8 | "achieves a weekday JS divergence of 0.0619, a clear PASS against the < 0.20 True-Future-Test gate" | line 241 | MATCH |
| 9 | "independently corroborated by the Step-6 calibration validation" | line 461 | MATCH |
| 10 | "This captures the demographic virtual drift in P(demographics) between 2022 and 2030 without modifying the conditional behavioural model" | line 239 | MATCH |
| 11 | Fig. 6 caption: "Diurnal load-shape reshaping under work-from-home." | line 414 | MATCH |
| 12 | "the behavioural break reshapes the residential load curve structurally" | line 473 | MATCH |
| 13 | "The midday energy share increases by +0.367 percentage points (95% CI [+0.208, +0.526])...The load factor...increases by +0.0117 (95% CI [+0.0085, +0.0150])" | line 407 | MATCH |
| 14 | "The paper's primary inferential targets (section 5.3), the 2022 to 2030 load-shape metrics, are fully within-panel" | line 320 | MATCH |
| 15 | "load factor increment approximately +0.009 at that cycle" | line 409 | MATCH |
| 16 | "the 2030 weekday at-home mean of 78.48% against a target of 78.44%" | line 310 | MATCH |
| 17 | Abstract: "Weekday at-home occupancy breaks +5.2 percentage points (pp) at COVID and persists to 2030 (+2.2 to +3.9 pp)" | line 10 | MATCH |
| 18 | Section 6: "(+1.4 to +2.6% across the break, +0.6 to +1.2% to 2030; Table 5)" | line 435 | MATCH (and Table 5, lines 391-398, genuinely has no percentage-increment column, confirming the pointer mismatch the report claims) |
| 19 | "the order of the ~+12% structural increase in residential in-home energy demand documented for the Canadian context" | line 439 | MATCH, confirmed uncited in the manuscript's own text |

No fabricated quote, invented section reference, or misquoted number was found in either report across
the 40 spot-checks. Both reports' stated quotation convention (dashes and arrows replaced) accounts for
every surface difference found; no quote was paraphrased and presented as verbatim.

## 2. Arithmetic and consistency verification

- **dr_2J-10, SC8 (stock-scale N=50 arithmetic).** The report computes 4 archetypes x 6 cities x 50
  households/cell = 1,200 simulated households per cycle-year, against the manuscript's own
  "thousands of dwellings" standard for the stock-scale tradition (section 1.2 para 1). Re-derived
  independently: 4 x 6 = 24 cells, 24 x 50 = 1,200. Correct arithmetic. The comparison to "thousands"
  is a judgement call, not itself an arithmetic claim, and is reported as UNCERTAIN by the return itself.

- **dr_2J-11, Finding 5.1 (two incompatible readings of "+2.2 to +3.9 pp").** Re-derived both readings
  from the manuscript's own numbers. Reading A (level above pre-pandemic, the reading used in the
  Abstract, section 3.4, section 5.1, and Conclusion item 2): compare +2.2 to +3.9 pp against the
  2022 standardized level of +5.2 pp (line 370). Since 3.9 < 5.2, the 2030 level is below the 2022
  level under this reading, which is inconsistent with "persists," "extends rather than reverses" (line
  409), and "upper bound." Reading B (the 2022-to-2030 step, the reading used once, in section 7 para
  5, line 461): 2030 level = 5.2 + 2.2 = 7.4 pp to 5.2 + 3.9 = 9.1 pp above pre-pandemic. Both additions
  check out arithmetically. The report's conclusion, that the two readings cannot both be true and the
  text does not say which is meant, is a correct derivation from the manuscript's own stated numbers,
  not an invented tension.

- **dr_2J-11, Finding 5.7 (Table 5 pointer mismatch).** Table 5 (manuscript lines 391-398) columns are
  Archetype, SHEU dwelling type, Simulated EUI 2022, Simulated EUI 2030, SHEU national central, SHEU
  band, Within band 2022, Within band 2030. No percentage-increment column exists. Section 6 cites
  "(+1.4 to +2.6% across the break, +0.6 to +1.2% to 2030; Table 5)" (line 435) for numbers that in fact
  come from the paired-run computation in section 5.2, not from Table 5. Confirmed as stated.

## 3. Known-versus-new cross-check against the plan and the drafts

Both reports' own drafts note (`dr_2J-10` implicitly, `dr_2J-11` explicitly at its end) that none of the
four partial redrafts touch the material they audit, except `draft_S2_framework.md` section 2.7 and
`draft_S7_limitations.md` for `dr_2J-11`'s WFH-scenario item. The table below classifies each report's
top-5 ranked critique item against `00_REVISION_PLAN.md`'s reviewer-triage tables (section 2), its
work-package list (section 3), and its "weaknesses the reviewers did not raise" list (section 5), read in
full for this pass.

**dr_2J-10 (novelty matrix), top 5:**

| Item | Known or new | Where it already lives in the plan |
|---|---|---|
| R1: novelty vs. the authors' own prior work asserted by exclusion, not shown | KNOWN | Reviewer 1 item D2 ("if the authors' previous published studies are excluded, they should also be included"), assigned WP10; plan section 5 item 8 (Table 1 matrix never tested by a systematic search, WP12.3a). Fable's mechanism (section 1.2 para 2 concedes the predecessor "would satisfy most" columns) sharpens the reviewer's complaint but is not new information. |
| R2: no stated column criteria; Chiou scored X and Yin scored check-mark on "Calibrated behavioural model" with no consistent rule | NEW | Not found anywhere in the plan's reviewer-triage tables or the section 5 quiet-fix list. The plan's item 8 is about testing the matrix against an external search, not the matrix's own internal scoring consistency. Actionable new input for WP10's Table 1 rewrite. |
| R3: the one column separating the paper from Chen et al. is a single feature, and the design is Chen's | KNOWN | Reviewer 1 item D5 ("differences from Chen et al. (2022) should be described more explicitly"), assigned WP10 ("one explicit paragraph"). |
| R4: the distinguishing column is the result the paper itself calls provisional and single-scenario | KNOWN facts, new synthesis | The provisional 2022-to-2030 number is WP1's critical-path job; the single-scenario framing is WP2's job. Both already the top of the plan's work-package list. The specific link Fable draws (the ONE feature that makes the paper novel over Chen is not yet earned) is not stated this way anywhere in the plan and is useful framing for WP10's Discussion rewrite once WP1/WP2 land. |
| R5: disclaimed premise as the abstract/conclusion's closing sentence; a review paper and an office study sit in the matrix | PARTIALLY KNOWN | The Motuzieno half (office study scored "Forecast to future year") is already CARRIED from `dr_2J-12` (plan section 5 item 10, line 482). The Reinhart-is-a-review-paper half and the disclaimed-premise-as-closing-sentence tension (the report's M5) are not in the plan; NEW. |

**dr_2J-11 (WFH trajectory), top 5:**

| Item | Known or new | Where it already lives in the plan |
|---|---|---|
| 1: the WFH effect is never measured with an interval; the CI-bearing leg holds WFH fixed | KNOWN | Already CARRIED from `dr_2J-12` and explicitly named there as "the single most load-bearing finding," assigned WP1 + WP10 (plan lines 509-514). `dr_2J-11` independently re-derives the same conclusion from the scenario definition itself (a different route than `dr_2J-12`'s panel-change route), which is real corroboration, not a new finding. |
| 2: one 2030 number, two incompatible definitions | NEW | Not present under any plan item found in this pass. A genuine internal contradiction that should be resolved as part of WP1's recalibration and needs an explicit editorial decision on which definition (level vs. step) the rebuilt number will report. |
| 3: a single one-sided scenario, promised bounded, never bounded | KNOWN | This is WP2's entire stated purpose (plan lines 168-193); also Reviewer 3 items R3-2 and R3-4 (lines 117, 119) and Reviewer 1 items M5/D17 (lines 78, 95). |
| 4: the system boundary (home vs. office energy) is never declared | KNOWN | Reviewer 1 item D13 (line 91) already assigned "one limitation paragraph," and the rewrite plan already names the fix directly (line 367: "New system-boundary paragraph: more home occupancy may mean less office energy, not modelled (R1-D13)"), assigned WP10/WP12. `dr_2J-11`'s contribution is confirming the paragraph still does not exist in either the submitted text or the current S7 redraft, which is useful process confirmation, not a new finding. |
| 5: the provisional/inflated input feeds every 2030 result without the caveat travelling | KNOWN | Essentially the same finding already CARRIED from `dr_2J-12`'s vetting ("the fix must also reach the abstract and highlights, not just section 7"). |

## 4. Positive-control-style sanity check (task step 4)

`dr_2J-11` Finding 5.6 explicitly states it overlaps with a `dr_2J-12` finding: "This is the same point
as S7 and was also raised by the `dr_2J-12` return; it is repeated here because it is where the scenario
definition and the reported figures collide." Checked against `dr_2J-12_VETTING.md` section 6 CARRIED
list: "The CI-bearing shape deltas measure 2022-to-2030, not the WFH break itself (Fable S8, finding 4.1,
critique item 1)." Confirmed as the same mechanism, correctly self-identified. PASS.

`dr_2J-10` does **not** make an equivalent self-identified overlap claim anywhere in its own text. Its
own "M6" finding is about the end-use layer being called an "advance" in section 1.5 and "not itself a
novel...contribution" in section 3.6, which has nothing to do with the Conclusion-item-1/Table-5
contradiction. The task doc that commissioned this vetting states, under its own step 4, that "dr_2J-10
M6 and dr_2J-11 Finding 5.6 both note overlap with prior dr_2J-12 findings (the Conclusion-item-1/
Table-5 contradiction...)." That description does not match `dr_2J-10`'s actual text: the
Conclusion-item-1/Table-5 contradiction and the lighting/daylight-gate and Table-5-miscitation findings
are labelled M1, M4, and M9 in `dr_2J-12`'s own Fable report (see `dr_2J-12_VETTING.md` section 1), not
in `dr_2J-10`. This looks like a mislabeling in the task doc, most likely a mix-up between `dr_2J-10`'s
own finding numbers and `dr_2J-12` Fable's finding numbers, both of which use an "M#" convention for
internal mismatches. It is not a fabrication in `dr_2J-10` itself: `dr_2J-10` simply never claims this
overlap. Recorded here so the overlap is not repeated to the author as something `dr_2J-10` itself says.

## 5. Independent re-check of dr_2J-11's own redraft cross-check note

`dr_2J-11` closes with a note (not mixed into its main sections) making three claims about
`draft_S2_framework.md` and `draft_S7_limitations.md`. Each was independently re-read against the current
drafts in this pass, not trusted from the return:

1. "`draft_S2_framework.md` section 2.7 now defines three persistence scenarios, lambda in
   {1, 0.5, 0}...and states 'This is a scenario-based projection of a stated persistence assumption, not
   a forecast'." Confirmed: `draft_S2_framework.md` lines 224-242 define exactly this, with the quoted
   sentence appearing verbatim at lines 241-242. MATCH.
2. "`draft_S7_limitations.md` states 'The 2030 results are a scenario, not a forecast.' and disclaims any
   uncertainty range. It still contains no residential-only or office/commercial boundary sentence."
   Confirmed: the quoted sentence is the bolded lead of the sixth limitation, line 57; "No uncertainty
   range, no policy change, and no alternative trajectory..." follows at lines 61-62; the full 135-line
   draft was read and contains no mention of office, commercial, or a system-boundary scope sentence.
   MATCH.
3. The "new tension" claim: the redraft's 2030 target adds "8 times a linear trend fitted to real
   respondents from 2005, 2010 and 2015" to the 2022 stock rate (matching Eq. 10 in `draft_S2_framework.md`,
   lines 228-233, and the parallel sentence in `draft_S7_limitations.md` line 59), while the submitted
   manuscript's own section 5.1 argues the 2005-2015 drift is compositional, not behavioural, once
   standardized (line 370, the 64.2/64.2/63.3% series already quote-verified above). Confirmed as a real
   tension: the redraft's primary 2030 formula uses the raw (non-standardized) 2005-2015 trend as the
   slope term, with the standardized version offered only "as a sensitivity check" (`draft_S2_framework.md`
   lines 236-239), which is the same distinction the submitted text uses to argue the earlier trend is not
   behavioural. `dr_2J-11`'s suggestion that the standardized version should probably be the primary,
   not the sensitivity, is a reasonable editorial recommendation, correctly flagged as UNCERTAIN by the
   report itself rather than asserted as fact.

All three of `dr_2J-11`'s own cross-check claims about the drafts are verified accurate in this pass.

## 6. CARRIED versus lower-confidence framing, and final verdicts

**CARRIED (verified against the manuscript, arithmetic re-derived, or independently confirmed against
the drafts in this pass):**

- `dr_2J-10`: the two-basis novelty argument (M1), the predecessor's three inconsistent characterizations
  of what its "2025" was (M2), the Chiou/Yin column-scoring inconsistency (M3, R2), the Table 1 caption
  vs. section 6 scope disagreement (M7), the review-paper/office-study category mismatch (S4), and the
  provisional/single-scenario status of the one distinguishing column (SC9, R4). All quote-verified.
- `dr_2J-11`: the scenario-definition-implies-no-WFH-change-after-2022 argument (S7, item 1), the two
  incompatible definitions of "+2.2 to +3.9 pp" (Finding 5.1, arithmetic re-derived), the never-delivered
  sensitivity bound (S4, item 3), the system-boundary NOT FOUND result (section 4, item 4, and confirmed
  absent from the S7 redraft in section 5 above), and the Table 5 pointer mismatch (Finding 5.7,
  re-derived). All quote-verified.

**Lower-confidence framing (the report's own synthesis or severity judgement, not a quote-checkable
fact; safe to use as argument, not to be quoted to the author or a reviewer as an established fact):**

- `dr_2J-10` section 4's claim that the prose novelty claim is "unfalsifiable by construction" is the
  report's own interpretive judgement about what a hypothetical competitor could or could not satisfy; it
  follows reasonably from the quoted text but is not itself a quote.
- Both reports' severity labels ("would-reject," "would-request-major-revision," "minor") on their
  ranked items are editorial judgement calls, consistent with the reasoning given but not independently
  checkable the way a quote or an arithmetic claim is.
- `dr_2J-11` Finding 5.4 (the 78.44% target reads as a raked input rather than a forecast output) is
  explicitly self-flagged UNCERTAIN by the report; carry it as a flagged possibility, not as fact.

**Verdicts:**

- **dr_2J-10 (novelty matrix): SURVIVES VETTING.** All 21 spot-checked quotes and every Table 1 cell
  match the archived manuscript exactly; the stock-scale arithmetic is correct; three of five top-ranked
  items are already known and assigned to existing work packages (WP1, WP2, WP10, WP12.3a), one is
  partially known (the Motuzieno half of R5, already CARRIED from `dr_2J-12`), and one (R2, the
  criteria-free matrix with an internally inconsistent Chiou/Yin cell) is genuinely new and actionable.
- **dr_2J-11 (WFH trajectory): SURVIVES VETTING.** All 19 spot-checked quotes match exactly; both
  arithmetic re-derivations (Finding 5.1's two readings, Finding 5.7's Table 5 mismatch) check out; its
  self-cross-check against the two live drafts is independently confirmed accurate in every particular;
  its headline item is corroboration (by a different route) of `dr_2J-12`'s single most load-bearing
  finding, already on the WP1 + WP10 critical path; and it surfaces one genuinely new, actionable
  contradiction (Finding 5.1) that needs an explicit editorial decision before WP1's rebuilt 2030 numbers
  are reported.

## 7. What this vetting did not check

- Neither report's characterization of any external study (the nine Table 1 competitors, Barrero et al.,
  Guo et al., Cicala) was checked against that study's actual content; both reports flag this themselves
  as OUTSIDE MY SCOPE, and it remains outside this vetting pass too, since no DOI or external source is
  involved (that is the paired Gemini returns' job, still owed by the author).
- Neither report's severity labels, nor `dr_2J-10` section 4's "unfalsifiable by construction" framing,
  were independently re-argued; they were checked only for whether the quotes underneath them are real,
  not for whether the label itself is the correct one a reviewer would apply.
- The two SI redrafts (`draft_SI_model_selection.md`, `draft_SI_schedule_completion.md`) were not opened
  in this pass, since neither report's top-5 items intersect with model-selection thresholds or
  weekend-schedule completion; if a later task finds an item that does touch those drafts, they still
  need their own check.
- Figures, SI tables, and the companion C-VAE manuscript were not available as text in this session
  either, the same gap both reports themselves disclose.
- The remaining Fable findings not named in either report's top 5 or explicitly cited above (the
  bulk of `dr_2J-10`'s sections 3 and 5, `dr_2J-11`'s remaining sub-claims S1/S2/S8) were read in full but
  not individually re-verified quote by quote in this pass; a full read found nothing inconsistent with
  the manuscript text already checked, but "not individually re-verified" should be read literally.
