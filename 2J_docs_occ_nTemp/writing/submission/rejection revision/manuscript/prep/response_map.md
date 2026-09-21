# Response map: every reviewer request vs plan status

Updated 2026-09-21 by T89 against the revised manuscript.

Originally built 2026-09-15 by T33 (WP10 prep). Source: `00_REVISION_PLAN.md` section 2 (the request
table) and section 3 WP10 (the new structure), plus section 5 items 10 to 39 and the plan log entries
from (ec) onward. This pass re-checked every row against the current files
`manuscript/2J_manuscript_AE_revised.md` (1,154 lines) and `manuscript/2J_SI_AE_revised.md` (497
lines), using grep and a full read of both, not against the old task-doc notes. Paraphrases below are
in plain words; no reviewer sentence is copied. Status values: DONE (quote the section, figure or table
where it lands), PARTIAL (say what is missing), WAITING ON AUTHOR (only the three author-owed items:
companion paper status, and the two `[NUMBER FROM RESULTS]` placeholders in Section 1.5), or DECLINED
(a pre-registered rule says we do not run this).

Columns: ID, plain paraphrase, class (A text / B re-derive a number / C new computation / D narrow a
claim / E rebuttal), what we change, where it lands in the new manuscript, which task(s) supply the
evidence, status, note.

## Reviewer 1

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| M1 | Compare our method against simple fixed schedules and average occupancy profiles. | C | Add two new simulation arms (fixed-schedule, average-profile) on the same households. | Both arms defined in Section 2.12; the average-profile arm is compared and reported in Section 3.5, Figure 7 and Section 4 Discussion. | T22, T30, T77 | PARTIAL | Section 3.5 states plainly that the fixed-schedule arm "is not part of this comparison, since it is not a home-for-home comparison." Only the average-profile arm reached the Results; the fixed-schedule arm stays a Methods definition only. |
| M2a | Give one short diagram of the whole workflow. | A | New workflow figure, prompt only, author generates the image. | Figure 1, opening Section 2. | T76 | DONE | Ten-box, three-row diagram accepted by the author; `Figure_01_workflow.png` is the file cited. |
| M2b | Spell out the math behind the main models and metrics. | A | Add an equations block. | Section 2 (Equations 1 to 18) and the Symbol list at the end of Section 2. | T78 to T81 | DONE | |
| M2c | Some passages in the middle read like results and should move. | A | Move gate scores and JS (similarity) scores out of the methods sections. | Model-selection scores now sit in Section 3.8 (Results) and SI Sections S1 and S2, not in Section 2. | this task, WP10 | DONE | |
| M2d | Explain how the 50-household samples are drawn and show that is enough. | B + C | Write the sampling method in words; add a subsampling curve; run one larger check. | Sampling procedure in Section 2.8; sample-size check in Section 3.7 with SI Figure S1. | T05, T28, T75 | DONE | |
| M3 | Simulated energy differs a lot from the SHEU reference; show the conclusions still hold. | B + C(optional) + D | Measure the gap end-use by end-use; stop calling the match "plausible". | SHEU fitted-target check in Section 2.6 and Section 3.3 (48 of 48 cells pass); EUI levels reported in Section 3.3; no gap language or "plausible" wording remains anywhere. | T07, T87 | PARTIAL | The SHEU band check now passes cleanly on the rebuilt data, which was the reviewer's original complaint on the old data. What is still missing: the plan's item 24 ruling (state plainly that no measured end-use split exists and the gap cannot be assigned to one end use) has not been written into the manuscript text anywhere. Optional envelope check (T31) stays DECLINED by the pre-registered rule (plan log (aq)): the window-rating input value is not published anywhere. |
| M4 | Add more plots (occupancy, energy, load shape, peak, load factor) and cut repeated text. | A + B | New plots from data already computed; shorten prose. | Figures 2 to 8 now cover occupancy by hour, annual energy by end use, load shape, peak/load-factor/ramp, the end-use heatmap, the average-profile comparison and the measured check. | T71, T73, T76, T77 | DONE | |
| M5 | Fig. 5's occupancy rise from 2022 to 2030 needs checking; test other work-from-home paths. | C | Fix the 2030 numbers, then run more than one future path. | Section 3.2 (three named 2030 scenarios plus one standardized variant). | T20, T26, T29, T32 | DONE | |
| D1 | Show exactly which results need the household-level random model, not just averages. | C (via M1) + A | Answer using the M1 comparison. | Section 3.5 and Section 4 Discussion: the average-profile arm keeps the same calibrated design power but assigns everyone the same schedule, and household-level peak-timing diversity collapses almost to zero as a direct result. | T30, T77 | DONE | Answered by the average-profile arm specifically; does not need the fixed-schedule arm. |
| D2 | Add our own earlier published work to the comparison table, not just other groups'. | A | Add rows for our prior papers to Table 1. | Table 1, last data row ("Authors' own prior line"); Section 1.2 and 1.4 discuss it in prose. | T78 | WAITING ON AUTHOR | Table row is written and referenced in prose. The only piece left open is the companion journal paper's publication status, shown in Table 1 as `[STATUS TO CONFIRM BY AUTHOR]` and in Section 1.4 as "under review" plainly. One of the three author-owed items. |
| D3 | Define the model name "C-VAE" the first time it is used, not later. | A | Move the definition earlier. | Section 1.4, first sentence that uses the term. | T78 | DONE | |
| D4 | Explain the phrase "activity and end-use resolved" as soon as it appears. | A | Add a one-line definition. | Table 1 footnote d, attached to the C4 column where the phrase first appears. | T78 | DONE | |
| D5 | State more clearly how our method differs from the Chen et al. (2022) study. | A | Add one explicit comparison paragraph. | Section 1.2 (closest precedent) and Section 4 Discussion (the one axis of difference, C3). | T78, T82 | DONE | |
| D6 | Explain why the timing of energy use matters, and why 2030 is the target year. | A | Add a motivation paragraph. | Section 1.1, closing paragraph (grid timing, cites Denholm et al. 2015; 2030 planning horizon, cites IEA 2021). | dr_2J-14, dr_2J-15, T88 | DONE | |
| D7 | Rewrite the contributions as clear scientific and practical statements. | A | Rewrite the contributions paragraph. | Section 1.5: three scientific contributions, then two practical contributions, each a plain claim. | T78 | WAITING ON AUTHOR | The paragraph itself is rewritten and reads as intended, but it still carries two `[NUMBER FROM RESULTS]` placeholders (architectures searched; total simulation runs), two of the three author-owed items. |
| D8 | Add a table showing which dataset feeds which part of the framework. | A | New dataset-role table. | Table 2, opening Section 2. | T78 | DONE | |
| D9 | Move the EnergyPlus simulation description out of the datasets section. | A | Relocate that text. | Simulation mechanics now sit in Sections 2.8 and 2.9, not in the Table 2 dataset list. | T78 | DONE | |
| D10 | Rename the modelling section to something like "proposed modelling and simulation framework". | A | Retitle Section 3 as Section 2. | Section 2 title is exactly "Proposed modelling and simulation framework." | T78 | DONE | |
| D11 | Add formal definitions for the key modelling and aggregation steps. | A | Same work as M2b. | Section 2 (Equations 1 to 18). | T78 to T81 | DONE | |
| D12 | Explain why modelling individual behaviour matters even for whole-stock (aggregate) results. | C (via M1) + A | Same evidence as M1, plus the existing household-level peak finding. | Section 3.5 and Section 4 Discussion. | T30, T77 | DONE | |
| D13 | Discuss that more at-home energy may mean less office energy, which we do not model. | A | Add one limitation paragraph on this system boundary. | Section 5, "Only home energy is inside the system boundary." | manager 2026-09-21 | DONE | Stated as a scope limitation; needs no outside source because it claims only what the study does not model. |
| D14 | Merge two sections that describe the same thing twice. | A | Merge the repeated schedule-integration description. | Section 2 is now 2.1 to 2.12 with no duplicate schedule-integration passage found on a full read. | this task, WP10 | DONE | |
| D15 | Add more figures and tables; there is too much text for too few visuals. | A + B | Same work as M4. | Figures 2 to 8, Table 1, Table 2, SI Figures S1 and S2. | T71, T73, T76, T77 | DONE | |
| D16 | Re-check every number in the occupancy-change section against what the figure shows. | B | Re-derive each number from the current files. | Section 3.1 (corrected occupancy numbers, consistent with Abstract, Highlights and Conclusion). | T01, T11, T12, T18, T20 | DONE | Root cause (four-cycle diary mix instead of only 2022 diaries) is fixed in the household-frame rebuild. |
| D17 | Same as M5: test alternative 2030 work-from-home paths, not only one trend. | C | Same work as M5. | Section 3.2. | T20, T26, T29, T32 | DONE | |
| D18 | Fig. 6c shows little difference; break it down by end use and time of day. | B | New end-use-by-hour breakdown from existing simulation output. | Figure 6, the end-use by hour percent-change heatmap. | T71 | DONE | |
| D19 | Make the load-shape, ramping, peak, and load-factor results more prominent; that is the real contribution. | A + B | Lead the Results with these metrics; add a ramp metric already in the paper's own code. | Section 2.10 now defines the evening ramp (14:00 to 17:00 increase, yearly mean); Section 3.4 reports peak, load factor, midday share and ramp with Figures 4 and 5. | T71 | PARTIAL | Ramp wording mismatch fixed 2026-09-21. Results still opens with occupancy (3.1) and scenarios (3.2) before load shape (3.4). |
| D20 | Fig. 7 is too small and packed with information; split it into separate panels. | A | Split one figure into several. | Figure 7 exists (full model versus average-profile arm). | T77 | PARTIAL | Whether it reads clearly at print size is a visual check this task cannot make from text alone. Same treatment the plan already gives Figure 1 (plan item 23): the author's own eye is needed before submission. |

## Reviewer 2

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| R2-1 | The paper reads like an internal technical report; move QA and debugging detail to supplementary material, use plainer terms. | A | Move QA/debug content to SI; replace self-defined labels with plain words. | SI Table S3 (glossary); main text checked clean of the internal labels. | this task, T56, T86 | DONE | Grepped the main manuscript for the literal strings "J3", "True-Future-Test", "FailSafe", "occACT", "DDAY_STRATA", "COLLECT_MODE" and "Tier-1": zero hits. |
| R2-2 | Check the simulated hourly profiles against real measured household or area electricity data for a recent year. | C + external data | Compare against measured Ontario/Toronto hourly data. | Section 3.6 and Figure 8 (twelve period-and-day-type groups, Toronto and Ontario, 2022). | T02, T09, T15, T73 | DONE | Stated plainly as "a check on the simulated shape, not a validation of the model as a whole." |
| R2-3 | Reconsider calling this a "forecast"; call it a scenario-based projection throughout. | A (accepted) | Replace "forecast" with "scenario-based projection" in title, abstract, and text. | Body text: three negated uses only ("not a forecast," Section 2.7 and Section 5 twice). Title still reads "Forecasting..." | T86 | PARTIAL | The title was deliberately NOT changed. Plan log (dz) records this as the author's own ruling, kept as an approved exception with the reviewer risk flagged once. This is a standing author decision, not an unfinished task. |
| R2-4 | Rewrite the abstract in plain sentences, without symbols like +, plus/minus, approx, or delta. | A | Prose abstract. | Abstract. No +, plus/minus, approx or delta symbol found; every value is spelled out in words. | T83 | DONE | |
| R2-5 | Delete the paragraph that describes how the introduction itself is organized. | A | Delete that paragraph. | Introduction (Sections 1.1 to 1.5). No such paragraph exists on a full read. | T78 | DONE | |
| R2-6 | The SHEU agreement mainly shows the model was tuned to match it, not independent proof it is right. | A + D | Stop naming this "calibration closure"; do not call it independent validation. | Section 2.6, Section 3.3 and Section 4 all call it a "fitted-target check," and Section 4 states plainly it is "not an independent validation." | T07 | DONE | Grepped for "calibration closure" and "credibility anchor": zero hits in the current manuscript. |
| R2-7 | Figures 6 and 7 are too small and hard to read. | A | Split/enlarge figures. | Figures 6 and 7 both exist in the current manuscript. | T71, T77 | PARTIAL | Same item as D20; legibility at print size is a visual check, not verifiable from the text alone. |

## Reviewer 3

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| R3-1 | Redo the 2030 numbers on the corrected household data and update every affected figure, interval, and conclusion. | C, critical path | Rebuild the 2022 stock, rebuild 2030 on top of it, rerun the full simulation campaign. | Whole manuscript: Abstract, Results, Discussion and Conclusion all read from the rebuilt tree. | T18, T18b, T18c, T20, T21, T87 | DONE | |
| R3-2 | Run at least two 2030 paths (workers mostly stay home vs. partly return), or use much more careful wording. | C | Build three scenarios (stay-home, partial return, full return) on the rebuilt stock. | Section 3.2, in the main Results body. | T26, T29, T32 | DONE | |
| R3-3 | Be careful to say "change linked to the pandemic/remote work" rather than claiming it was directly caused by them. | A + D | Replace causal wording; add one limitation naming other changes over the same period. | Section 1.3 ("a change associated with the pandemic"); Section 5 Limitations, collection-mode paragraph, separates correlation from causation explicitly. | T82 | DONE | |
| R3-4 | Add at least a rough range of outcomes in the main results, not only at the end. | C | Same work as R3-2. | Section 3.2, main Results body, not confined to Limitations. | T26, T29, T32 | DONE | |
| R3-5 | Separate "the model matches its own tuning target" from "independent evidence the model is plausible", clearly labelled. | A + C | Split into two labelled parts. | Section 3.3 (fitted-target SHEU check) and Section 3.6 (independent measured check) are two clearly separate, distinctly titled subsections. | T02, T09, T15, T07 | DONE | |
| R3-6 | Explain how the confidence intervals were built, and whether household clustering (same city/archetype) was accounted for. | B | Document the interval method; note it does not yet account for city/archetype clustering. | Section 2.11 (paired interval method, states plainly it treats households as independent); Section 3.8 and SI Section S10 (clustering-aware bootstrap compared against the plain interval). | T03, T67 | DONE | |
| R3-7 | Explain where the specific pass/fail thresholds come from, whether fixed before comparing models, and whether the choice changes under slightly different thresholds. | B (+ D if fixed after the fact) | Trace the thresholds; re-rank the stored trial scores under shifted thresholds. | Section 3.8 and SI Section S2. | T04 | DONE | Wording used exactly as required: "chosen among four passing candidates," not "the only one that passed." |

## Quiet fixes and new items (not reviewer-raised, dr_2J-12 vetted)

| ID | Plain paraphrase | Class | What we change | Where in new manuscript | Evidence task(s) | Status | Note |
|---|---|---|---|---|---|---|---|
| Q10 | Table 1's Motuzienė row wrongly checks "forecast to future year"; fix the checkmark or soften the citation. | A | Remove or adjust the "Forecast to future year" checkmark for Motuzienė et al. (2022) in Table 1, or soften the section 1.3 citation wording. | Table 1, C3 column now "cross (footnote c)"; footnote c explains why. | dr_2J-12_VETTING.md | DONE | |
| Q11 | Discussion cites Table 5 for percentage figures it doesn't contain; fix the citation or remove the claim. | A | Remove or correct the Table 5 citation in the Discussion for annual-electricity percentage increments. | Table 5 no longer exists anywhere in the rebuilt manuscript; no percentage claim is attributed to a "Table 5" anywhere. | dr_2J-12_VETTING.md | DONE | Resolved by the WP10 restructuring rather than by a targeted citation fix; the table that carried the wrong citation is gone. |
| Q12 | Section 3.6 promises a lighting daylight-gate discussion in section 7 that section 7 never gives. | A | Add the promised sentence on the lighting daylight-gate simplification to the Limitations section, or remove the forward reference. | Neither the forward-reference sentence nor any lighting/daylight discussion exists anywhere in the current manuscript (grepped "daylight", "lighting.*gate", "R1"). | dr_2J-12_VETTING.md | DONE | The unmet promise and the promise sentence itself are both gone; treated as resolved rather than reopened, since nothing forward-references an unwritten section any more. |
| Q13 | Conclusion says EUI is consistent with SHEU ranges; Results say all four archetypes are below range. | A | Change the Conclusion wording so it agrees with Results. | Table 5 and the "consistent with SHEU ranges" language are both gone from the Conclusion on a full read. | dr_2J-12_VETTING.md | DONE | Resolved by restructuring; the contradiction cannot recur because the sentence it lived in is gone. |
| Q14 | SHEU agreement is a scalar fitted to its own target; soften "validates the model" wording. | A | Replace "validates the model" / "credibility anchor" language. | Same evidence as R2-6. | dr_2J-12_VETTING.md | DONE | |
| Q15 | 2030 cohort size equals exactly 3x the 2022 diary count; ask author if deliberate. | A | One-line author check of whether the 3x relationship is deliberate or a coincidence. | Not addressed; the old counts (37,008 households, 12,336 diaries) no longer appear anywhere. | dr_2J-12_VETTING.md | PARTIAL | The household-frame rebuild changed the underlying numbers (stock frame is now 144,465 households); the deliberate-versus-coincidence question was never re-asked on the current numbers, so it is open on a different set of figures than when it was raised. |
| Q16 | Survey mode change lands on the same cycle as COVID; add a confound limitations paragraph and narrow WFH-attribution claims. | A + D | Add a limitations paragraph disclosing the collection-mode confound; narrow the abstract/highlights/Figure 6 caption. | Section 5 Limitations, final numbered paragraph before the "three further limitations" close, states the confound explicitly; Abstract, Highlights and the Figure 6 caption do not attribute the CI-bearing shape deltas to the WFH break specifically. | dr_2J-12_VETTING.md, T82, T83 | DONE | |
| Q17 | Table 1's novelty-matrix columns have no stated scoring criteria anywhere, and Chiou et al. (2011) and Yin et al. (2024) are scored inconsistently on "Calibrated behavioural model". | A | Add explicit scoring criteria for each Table 1 column; correct the Chiou and Yin crosses/checks. | Table 1 footnote b names both corrections directly (Chiou scored absent with reasoning, Yin scored present with reasoning). | dr_2J-10_dr2J-11_FABLE_VETTING.md (R2/M3) | DONE | |
| Q18 | The manuscript's own "+2.2 to +3.9 pp" 2030 figure is defined two incompatible ways. | A + D | Make an explicit editorial decision on which definition the rebuilt 2030 number reports, then use it consistently. | The old figure and both of its readings are gone; the rebuilt manuscript uses one consistent set of numbers throughout (4.73 pp 2022 break, 7.67 pp standardized, and per-scenario 2030 steps of 1.49, negative 0.85 and negative 3.21 pp). | dr_2J-10_dr2J-11_FABLE_VETTING.md (Finding 5.1) | DONE | Resolved by the rebuild rather than by picking between the two old readings; the ambiguity cannot recur because the old figure is gone. |
| Q19 | Table 1's real gap against Chen et al. (2022) is narrower than the prose implies; separately, the deep-research report's own internal table undercounts some rows. | A | Name column C3 explicitly as the one axis separating this paper from Chen et al. (2022). | Table 1 footnote c and Section 4 Discussion both name C3 as the one axis of difference. | dr_2J-10_VETTING.md section 7 | DONE | The report's own internal Table B undercount is informational for anyone quoting that outside report; nothing in this manuscript quotes it, so no manuscript-facing fix was needed for that half. |
| Q20 | The manuscript's 2030 scenario assumes work-from-home "persists with probability one," but the real trend since 2022 is a continued decline. | A + D | Ground the reversion scenario in the observed post-2022 decline instead of an arbitrary bracket. | Section 4 Discussion cites the post-2022 decline directly (Statistics Canada 2024b: 18.7 percent in May 2024, down 1.4 points from 2023 and 3.7 from 2022) and reframes the scenarios as "a range of outcomes, not... a central estimate." | dr_2J-11_VETTING.md, T88 | DONE | The old "7.1 percent" 2016 figure, flagged as unmatched to its cited source, does not appear anywhere in the current manuscript. |
| Q21 | Reference list: Motuzienė et al. (2022) is cited with volume 76; the real volume is 77. | A | Fix the printed volume number. | Reference list now reads volume 77. | plan section 5 item 20 | DONE | Fixed 2026-09-21. |
| Q22 | Reference list: Jalilian & Kamel (2025) is cited with a truncated title, missing its subtitle. | A | Restore the full published title. | Reference list now carries the full title with its Nassau County subtitle. | plan section 5 item 21 | DONE | Fixed 2026-09-21. |

## Carried findings (plan section 5, items 10 to 19)

| Item | Plain paraphrase | Where the manuscript now handles it | Status |
|---|---|---|---|
| 10 | Table 1 wrongly credits Motuzienė et al. (2022) with a future-year forecast; it is a short-horizon pandemic study. | Table 1, C3 column and footnote c, explicitly corrected. | DONE |
| 11 | The Discussion cites "Table 5" for percentages that table never held. | Table 5 no longer exists in the rebuilt manuscript. | DONE |
| 12 | Section 3.6 promises a lighting daylight-gate discussion that the Limitations section never delivers. | Neither the promise nor the gap exists in the current text. | DONE |
| 13 | The Conclusion says EUI is "consistent with" SHEU ranges while Results say all four archetypes sit below range, a same-document contradiction. | The contradictory sentence and the table it referred to are both gone from the Conclusion. | DONE |
| 14 | The SHEU agreement is a scalar fitted to its own target, then checked against it, so calling it "validation" is circular. | Section 2.6, 3.3 and 4 call it a fitted-target check, explicitly not an independent validation. | DONE |
| 15 | The 2030 cohort size equals exactly three times the 2022 valid-diary count; unclear if that is a deliberate oversample or a coincidence. | Not addressed with the current stock numbers; the old counts this question was built on (37,008 and 12,336) no longer appear anywhere in the rebuilt manuscript. | OPEN |
| 16 | Table 1's six columns have no stated scoring criteria, and Chiou et al. (2011) and Yin et al. (2024) are scored inconsistently. | Table 1 footnote b states the criteria and corrects both rows. | DONE |
| 17 | The manuscript's own 2030 shift figure is defined two incompatible ways (a level versus a step). | Resolved by the rebuild: one consistent set of numbers is used everywhere now, and the old figure with its two readings is gone. | DONE |
| 18 | Table 1's real gap against Chen et al. (2022) is narrower than the prose implies (missing only one column, C3). | Table 1 footnote c and Section 4 Discussion name C3 explicitly as the one axis of difference. | DONE |
| 19 | The manuscript's scenario assumes work-from-home holds at its pandemic level forever, but the real trend since 2022 is a continued decline. | Section 4 Discussion grounds the scenario range in the observed post-2022 decline and frames the scenarios as a range of outcomes, not a single predicted path. | DONE |

## Manager check (plan log (at), historical, 2026-09-15)

Counts re-measured by the manager on the earlier draft: "forecast" 33 lines case-insensitive, "gate(s)"
19 lines as a whole word, "calibration closure" 0. Superseded by the T89 counts below.

## T89 check (2026-09-21, current manuscript)

Counts re-measured directly against `manuscript/2J_manuscript_AE_revised.md`: "forecast" case-insensitive,
4 lines (the title, plus three negated uses, "not a forecast," in Section 2.7 and Section 5 twice);
"calibration closure" and "credibility anchor," 0 each; no em or en dash anywhere in the running text
(only the title and reference page ranges, an accepted exception per plan log (dz)); "1.0 to 3.3" percent
in either direction, 0. The SI file (`manuscript/2J_SI_AE_revised.md`) has 0 uses of "forecast."

## Coverage check

55 rows above (42 + 13): Reviewer 1: 28, Reviewer 2: 7, Reviewer 3: 7, matching the plan's count in section 2,
plus 13 quiet fixes not reviewer-raised, listed separately above: Q10-Q16 (7, from `dr_2J-12`), and
Q17-Q22 (6, added by T42: Q17-Q19 from `dr_2J-10`/`dr_2J-11` Fable and Gemini vetting, Q20 from `dr_2J-11`
Gemini vetting, Q21-Q22 from the 2026-09-17 independent reference re-verification, plan section 5 items 16-21).
Plus 10 carried-finding rows for plan section 5 items 10 to 19, added by this task (T89).

Row-count tally after this pass (55 original rows): DONE 43, PARTIAL 10, WAITING ON AUTHOR 2, DECLINED 0.
Carried-findings rows (10, items 10 to 19): DONE 9, OPEN 1.

## WHAT I DID NOT VERIFY
- Figure legibility and panel layout at print size (rows D20, R2-7): this is a visual check and this
  task is text only. The plan already treats this kind of check as the author's own eye (plan item 23),
  and that same treatment is used here rather than guessing.
- Whether the `.docx` builds match the `.md` source read for this task; only the Markdown source files
  were read.
- DOI or citation accuracy beyond what earlier vetting already recorded in the plan; deep research and
  citation checking are outside this task's scope.
- The individual `impl/*.md` Status lines for every task named in the Evidence task(s) column; this task
  read the manuscript and plan directly rather than re-opening every task doc, since the manuscript text
  itself is the source of truth this task was asked to check rows against.
- Whether the three WAITING ON AUTHOR items (companion paper status; the two `[NUMBER FROM RESULTS]`
  placeholders in Section 1.5) have been answered since this read; they were open at read time.
