# dr_2J-10 (Fable version) results: close-reading audit of our own novelty argument, no external search

**Run:** 2026-09-16, Claude Fable 5.1 inside Claude Code, no web access.
**Text reviewed:** `writing/submission/archive/2J_manuscript_submission.md` (the submitted manuscript, 653 lines). This is the only complete manuscript on disk; the four partial redrafts in `rejection revision/manuscript/` (S2 framework, S7 limitations, two SI drafts) do not touch the Introduction or Table 1 and were not substituted in. Findings describe the submitted text. Table 1 was read as Markdown; the figure images and the companion C-VAE manuscript were not available and were not read.
**Column labels:** the prompt's context defines C1 to C6 with wording that differs from the manuscript's own column headings (for example C2 "behaviour model grounded in survey data" versus the manuscript's "Calibrated behavioural model"; C3 "future year or scenario across the COVID break" versus the manuscript's "Forecast to future year"). This audit judges the manuscript on its OWN headings, and flags where the prose and the headings diverge.
**Quotation convention:** the manuscript uses em and en dashes and arrows. Inside quotations, dashes are replaced by commas and "2015→2022" is written "2015 to 2022" so this report contains no em or en dashes. Section pointers use the manuscript's numbering; "para N" counts prose paragraphs from the top of the named subsection, ignoring captions and tables.
**Status:** UNVETTED deep-research return. Goes through the 7-step vetting before anything is acted on. Nothing here was checked against any competitor paper; every characterization of a competitor is taken as the manuscript states it.

---

## 1. Verdict

**HAS A STRUCTURAL PROBLEM.** The manuscript runs two novelty claims on two different bases (a six-column "open cell" against external studies, and four pipeline-stage advances against the authors' own prior work), and it concedes in its own words that the six-column basis does not separate this paper from that prior work, so the "open cell that none occupies" is open only because the one study the text says would fill most of it was excluded from the table by fiat.

---

## 2. Argument map

**Novelty claim, quoted (§1.2 para 1, last sentence):** "The open cell that none occupies is a calibrated behavioural occupancy series forecast to 2030 through the work-from-home (WFH) break and carried into stock-scale paired building-energy simulation of the resulting load shape."

Restated §1.2 para 3, last sentence: "The open cell that none occupies, and that this study fills, is the simultaneous combination of a calibrated behavioural occupancy forecast carried through the COVID/WFH structural break with stock-scale paired BEM simulation of the resulting load shape." Restated §6 para 1: "The six-dimension gap matrix of §1.2 (Table 1) identified an open cell that no prior study occupies".

Sub-claims that must hold, each with the supporting text and a call on the text's own terms.

**SC1. The six columns are defined so that a reader can check a ✓ or ✗.** INSUFFICIENT.
The only definitions are the six column headings of Table 1: "Time-series occupancy", "Calibrated behavioural model", "Forecast to future year", "Activity & end-use resolved", "Stock-scale", "Load-shape & peak focus". No sentence anywhere states what earns a ✓ in any column. The prose applies the labels only once, to Chen: "stock-scale, calibrated, activity-resolved, and load-shape-focused" (§1.2 para 3). Without criteria, the ✗ entries cannot be audited from the text, and the internal consistency problems in Section 3 below follow directly.

**SC2. No external competitor fills all six columns.** INSUFFICIENT for six of nine rows.
Table 1 shows at least one ✗ in every competitor row. The prose supports the ✗ for exactly three rows: Chen ("but retrospective: it does not forecast to a future year", §1.2 para 3), Yin ("it neither forecasts forward nor runs building-energy simulation", §1.2 para 3), and Jalilian and Kamel ("holds occupancy static at pre-pandemic schedules", §1.2 para 3). For Chiou, Widén and Wäckelgård, Reinhart and Cerezo Davila, Fischer, Motuzienė and Osman, the only support is the table cell itself. Whether those cells are factually right is OUTSIDE MY SCOPE; on the text's own terms they are asserted, not argued.

**SC3. Chen et al. (2022) lacks the forecast column and only that column.** SUFFICIENT on the text's own terms.
"Chen et al. (2022) is the strongest competitor, stock-scale, calibrated, activity-resolved, and load-shape-focused, but retrospective: it does not forecast to a future year." (§1.2 para 3). The table row (✓ ✓ ✗ ✓ ✓ ✓) matches the sentence. Whether Chen actually lacks a future year is OUTSIDE MY SCOPE.

**SC4. Yin et al. (2024) stops at statistical analysis.** SUFFICIENT for the ✗ cells, UNCERTAIN for the ✓ cells.
"Yin et al. (2024) tracks the very premise this paper builds on, long-term (2001 to 2021) change in time-use behaviour, but stops at statistical analysis: it neither forecasts forward nor runs building-energy simulation" (§1.2 para 3). The three ✗ (forecast, activity and end-use, load-shape) follow from "neither forecasts forward nor runs building-energy simulation". The two ✓ (time-series occupancy, calibrated behavioural model) are not supported by any sentence; see mismatch M3 in Section 3.

**SC5. Jalilian and Kamel (2025) holds occupancy static.** SUFFICIENT on the text's own terms.
"Jalilian and Kamel (2025) forecasts at stock scale to a future year yet holds occupancy static at pre-pandemic schedules." (§1.2 para 3). Table row (✗ ✗ ✓ ✗ ✓ ✗) matches.

**SC6. The authors' own prior work does not occupy the cell.** INSUFFICIENT, and this is the load-bearing gap.
The text says the opposite of what the claim needs: "The authors' own prior C-VAE work (a companion manuscript by the same authors, currently under review; Iseri and Hachem-Vermette 2026) would satisfy most of these columns; its delta against the present paper is not a matter of these six binary axes but of the four pipeline-stage advances set out in §1.4 and §1.5." (§1.2 para 2). The text never says WHICH column the prior work misses. §1.4 para 2 describes the predecessor as spanning "2005, 2010, 2015, 2022, and a synthetic 2025", across "six Montréal neighbourhood-unit typologies", delivering "a first default-referenced reading of peak cooling timing", which on the manuscript's own description touches the time-series, behavioural-model, future-year, multi-archetype and peak-timing columns. The claim "no prior study occupies" (§6 para 1) therefore rests on the sentence "The matrix scores external competitors only." (§1.2 para 2), which is a scoping decision, not evidence.

**SC7. "Forecast to 2030 through the WFH break" is a capability the table scores.** INSUFFICIENT.
The table column is "Forecast to future year". The prose claim adds "through the work-from-home (WFH) break" (§1.2 para 1) and "carried through the COVID/WFH structural break" (§1.2 para 3). Two competitors hold ✓ in the forecast column (Motuzienė; Jalilian and Kamel), so the qualifier "through the break" is doing exclusionary work that the table does not show. The same is true of "paired": "stock-scale paired building-energy simulation" (§1.2 para 1) is part of the claim, but no column scores pairing.

**SC8. This study earns ✓ in "Stock-scale" by the standard the prose sets.** UNCERTAIN on the text's own terms.
§1.2 para 1 defines the second tradition as running "stock- and urban-scale energy engines across thousands of dwellings". §4.3 para 1 states "N = 50 household IDs are sampled once" per archetype-by-city cell, giving 4 × 6 × 50 = 1,200 simulated households per cycle-year, drawn from a "144,507-household building energy model (BEM) frame" (§2.2). Whether a 50-per-cell Monte-Carlo sample of a stock frame meets the "thousands of dwellings" standard the prose itself uses for the stock-scale tradition is not argued anywhere.

**SC9. This study earns ✓ in "Forecast to future year" with a forecast the paper stands behind.** SUFFICIENT for the binary cell, but the text undercuts the substance.
The 2030 forecast exists (§3.4). But the manuscript itself writes: "this magnitude is provisional pending a calibration-provenance check described in §7" (§5.1 para 1), and "the specific magnitude of the 2022 to 2030 step reported in §5.1 (+2.2 to +3.9 percentage points) and visualized in Fig. 5 should be treated as provisional pending a recalibration of the 2030 occupancy forecast against the current, post-relink household frame" (§7 para 5), and "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one" (§7 para 8). The one column that separates this paper from its strongest competitor is the one the paper itself marks provisional and single-scenario.

---

## 3. Internal consistency mismatches

**M1. Two novelty claims on two bases, and the text says the matrix basis does not separate the paper from its predecessor.**
Side A (§1.2 para 1): "The open cell that none occupies is a calibrated behavioural occupancy series forecast to 2030 through the work-from-home (WFH) break and carried into stock-scale paired building-energy simulation of the resulting load shape."
Side B (§1.2 para 2): "The authors' own prior C-VAE work ... would satisfy most of these columns; its delta against the present paper is not a matter of these six binary axes but of the four pipeline-stage advances set out in §1.4 and §1.5."
Side C (§6 para 1): "an open cell that no prior study occupies".
"No prior study" in §6 is wider than "external competitors only" in §1.2 para 2. Read together, the matrix novelty holds against outsiders while the real delta is against the authors' own work on a different basis, and the text does not say which of the six columns the predecessor misses.

**M2. What the predecessor's 2025 was: forecast, hindcast, or synthetic present.**
Side A (§1.4 para 1): "a journal treatment across six Montréal neighbourhood-unit typologies in climate Zone 6A over 2005 to 2025".
Side B (§1.4 para 2): "five period-specific occupancy datasets (2005, 2010, 2015, 2022, and a synthetic 2025)" and "rather than stopping at a synthetic present-day cycle".
Side C (§1.5 item 3): "A 2025 hindcast is replaced by a 2030 forecast carried through the structural break".
A "hindcast", a "synthetic present-day cycle" and a series "over 2005 to 2025" are three different things. This matters for SC6: if the predecessor projected 2025 from a dataset that already included 2022, it already crossed the break, and the "Forecast to future year" column would not separate the two papers.

**M3. Column 2, "Calibrated behavioural model", is applied on different criteria to Chiou and to Yin.**
Chiou et al. (2011): Table 1 gives ✗ in column 2. Yet §1.5 para 3 cites the same study as evidence that the American Time Use Survey has been "already shown to support residential energy modelling in the United States (Chiou et al. 2011)", and the reference list title reads "A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method". On the manuscript's own description, Chiou is survey-grounded.
Yin et al. (2024): Table 1 gives ✓ in column 2, while §1.2 para 3 says the study "stops at statistical analysis" and runs no model that reaches energy.
If "calibrated behavioural model" means survey-grounded, Chiou's ✗ is inconsistent with §1.5; if it means calibrated in the raking sense this paper uses (§3.2, §3.5), Yin's ✓ is unsupported. Either reading leaves one row inconsistent. Which is factually right is OUTSIDE MY SCOPE.

**M4. Column 1, "Time-series occupancy", is used in two senses.**
§1.4 para 1 uses "time-series occupancy" for intraday schedules fed to building energy models: "survey-grounded, time-series occupancy can be generated for Canadian building energy models". Table 1 gives Yin ✓ in that column while §1.2 para 3 describes Yin as documenting "long-term (2001 to 2021) change in time-use behaviour", a multi-year series. The column heading does not say which sense is scored. UNCERTAIN which sense Yin's ✓ is meant in.

**M5. The premise the paper says it does not re-claim is the sentence the abstract and conclusion end on.**
Side A (§1.4 para 2): "What this paper carries over, and deliberately does not re-claim as novel, is the premise that survey-grounded time-series occupancy can be built for Canadian building energy models at all". Also §1.4 para 1: "treating its core premise, time-series GSS occupancy in Canadian BEM, as established rather than novel."
Side B (Abstract, last sentence): "Time-varying, survey-grounded schedules are therefore feasible at stock scale and materially change the ramping- and demand-response-relevant load metrics that static schedules cannot see."
Side C (§8 final para): "Taken together, these results establish that time-varying, survey-grounded occupancy schedules are feasible at building-stock scale".
The word "at stock scale" may be the intended distinction from the predecessor's six-typology, one-zone domain, but no sentence draws that distinction, so the closing claim reads as the disclaimed premise.

**M6. The end-use layer is an "advance" in §1.5 and "not itself a novel ... contribution" in §3.6.**
Side A (§1.5 item 2): "Loads. Presence-filtered default end uses are replaced by a SHEU-calibrated, activity-resolved bottom-up end-use model".
Side B (§3.6 para 1): "it is not itself a novel load-modelling contribution but an application of established methods to the pipeline's output representation".
These can both be true (an advance over the authors' own prior line, not a field novelty), but the Introduction does not say so, and Table 1 scores the same layer as one of the six capability columns.

**M7. Table 1's title and the §6 restatement disagree on scope.**
Table 1 caption: "Six-dimension capability matrix: external competitors versus this study." §1.2 para 2: "The matrix scores external competitors only." §6 para 1: "an open cell that no prior study occupies". "No prior study" includes the authors' own prior work, which the matrix excludes.

---

## 4. Circularity and overclaiming finding

**Judgment: the matrix is partly circular, and the prose claim is more circular than the table.**

Reasoning, in three steps.

1. **The table is a conjunction of six binary features, and the paper's separation from the strongest row is one feature.** By the manuscript's own scoring, Chen et al. (2022) holds five of six; the only difference is "Forecast to future year". The manuscript also states that its attribution design "follows the paired stock-scale simulation rationale articulated by Chen et al. (2022)" (§4.3 para 2) and calls Chen "the closest methodological precedent to the present work" (§1.2 para 1). So the matrix-based novelty, as written, is: Chen's design plus a forecast year. A conjunction of six features will almost always be unique to the paper that chose the six; the question a reviewer asks is whether the one distinguishing feature is itself a contribution or an application, and the text does not argue that.

2. **The prose claim adds criteria that the table does not score, which makes it narrower than the table and harder to falsify.** The prose cell is "forecast to 2030 through the work-from-home (WFH) break and carried into stock-scale paired building-energy simulation" (§1.2 para 1). "Through the WFH break" and "paired" are not columns. A competitor that scored ✓ on all six columns could still be excluded by the prose on those two qualifiers. That is the shape of an unfalsifiable-by-construction claim. Conversely, the table without the qualifiers is falsifiable: any study with a post-2022 forecast and Chen's other five features would fill it. The manuscript should be read as making the table's claim, not the prose's, and as written the two are not the same claim.

3. **The exclusion of the authors' own prior work is the single decision that keeps the cell open.** §1.2 para 2 concedes the predecessor "would satisfy most of these columns". If it satisfies five, the matrix separates the present paper from its own predecessor by at most one column, the same margin as against Chen. The manuscript then relocates the novelty to "four pipeline-stage advances" (§1.5), each of which is an improvement in degree (a better generator, a calibrated load layer, a longer horizon, a paired design) rather than a new capability. That relocation is honest, but it means the six-column matrix is not where the paper's novelty lives, and the Discussion's opening sentence (§6 para 1) treats it as if it were.

Overclaiming, specifically: "The open cell that none occupies" (§1.2 para 1 and para 3) and "an open cell that no prior study occupies" (§6 para 1) are stated as facts about the literature. On the text's own terms they are facts about nine chosen rows plus a scoping rule. "of which the Canadian result is the first full demonstration" (§1.5 para 3) is a further "first" that no column or sentence supports.

---

## 5. Structure and clarity issues

**S1. The claim is asserted before its evidence, twice.** §1.2 para 1 states "The open cell that none occupies is ..." before Table 1 appears and before para 3 gives the only per-study reasoning; para 3 then restates the same claim in almost the same words: "The open cell that none occupies, and that this study fills, is ...". The reader meets the conclusion, then the table, then the argument, then the conclusion again.

**S2. "Closest methodological precedent" concedes what "open cell" denies.** §1.2 para 1: "the paired stock-scale simulation design of Chen et al. (2022) the closest methodological precedent to the present work"; same paragraph: "The open cell that none occupies". §6 para 2 repeats both: "the closest methodological precedent supplies a paired stock-scale simulation design but applies it retrospectively". Technically consistent (Chen misses one column), but "closest precedent" plus §4.3's "follows the paired stock-scale simulation rationale articulated by Chen et al." tells the reader the design is borrowed, while "open cell" and "none occupies" tell the reader the space was empty. The two framings are not reconciled in the text.

**S3. The table's competitor rows are never introduced by name before they are scored.** Chiou, Widén and Wäckelgård, Fischer, Motuzienė, Osman are scored in Table 1 with no sentence in §1.2 describing what they did; Widén and Osman are only cited in the "first tradition" list of §1.2 para 1, Chiou only in §1.5 para 3, Motuzienė only in §1.3. A reader cannot check a row against a description that does not exist.

**S4. A review paper and an office-building study sit in a capability matrix about residential load shape.** The reference list entry for Reinhart and Cerezo Davila (2016) is titled "Urban building energy modeling, A review of a nascent field"; the entry for Motuzienė et al. (2022) is titled "Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic". Scoring a review on six capabilities, and an office study in a matrix whose open cell is "the residential load shape" (§1.2 para 1 refers to "residential" throughout), is a category mismatch visible from the manuscript's own reference list. Whether either paper's content fits the cells is OUTSIDE MY SCOPE.

**S5. The §1.4 "does not re-claim" statement and the four advances leave the reader with two different answers to "what is new".** §1.4 para 2 ends: "what is new is every stage of the pipeline that turns that premise into a forecast load shape." §1.2 para 3 ends: what is new is "the simultaneous combination" of six features. The Introduction does not say whether the second is the reason the first matters, or an independent claim.

**S6. The "first full demonstration" sentence introduces a transferability novelty that no other section carries.** §1.5 para 3: "The study is accordingly presented as a transferable method for forecasting stock-scale load shape from behavioural microdata, of which the Canadian result is the first full demonstration." No column scores transferability, and the Conclusion's version ("the method that produces them is not" Canadian, §8 final para) states portability without the word "first".

---

## 6. Ranked reviewer critique (top 5)

**R1. Novelty against the authors' own prior work is asserted by exclusion, not shown.** Severity: would-request-major-revision.
§1.2 para 2: "The authors' own prior C-VAE work ... would satisfy most of these columns; its delta against the present paper is not a matter of these six binary axes". A reviewer reads this as the authors conceding that the headline gap matrix does not distinguish the submission from a manuscript by the same authors currently under review, and will ask which column it misses and why the answer is not "none". Combined with M2 (was the predecessor's 2025 a forecast, a hindcast, or a synthetic present?), this is the most likely trigger for "novelty not established" or "salami" concerns.

**R2. The matrix has no stated criteria and six of nine rows have no supporting sentence.** Severity: would-request-major-revision.
Table 1 headings only; §1.2 para 3 argues three rows. The Chiou versus Yin application of "Calibrated behavioural model" (M3) is the visible symptom: the same column is ✗ for a study §1.5 describes as time-use-survey-based and ✓ for a study §1.2 describes as statistical analysis. A reviewer who spots one inconsistent cell distrusts the table.

**R3. The distinguishing column against the strongest competitor is a single feature, and the paper adopts that competitor's design.** Severity: would-request-major-revision.
§1.2 para 3: "Chen et al. (2022) is the strongest competitor ... but retrospective: it does not forecast to a future year." §4.3 para 2: "This design follows the paired stock-scale simulation rationale articulated by Chen et al. (2022)". A reviewer will frame the contribution as "Chen plus a forecast year" and ask whether adding a projected year to an existing design is a contribution or an application. The prose's extra qualifiers ("through the WFH break", "paired") do not help, because they are not scored (Section 4, step 2).

**R4. The feature that fills the cell is the result the paper marks provisional and single-scenario.** Severity: would-request-major-revision, minor if §7 para 5's recalibration is done before resubmission.
§5.1 para 1: "this magnitude is provisional pending a calibration-provenance check described in §7". §7 para 8: "the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one". The novelty rests on a 2030 forecast through the break; the paper's own text says the 2030 occupancy level was raked against a superseded reference population and represents an upper bound. A reviewer will ask whether the column is earned.

**R5. The disclaimed premise is the sentence the abstract and conclusion end on; and the matrix includes a review paper and an office study.** Severity: minor.
§1.4 para 2: "deliberately does not re-claim as novel, is the premise that survey-grounded time-series occupancy can be built for Canadian building energy models at all"; §8 final para: "these results establish that time-varying, survey-grounded occupancy schedules are feasible at building-stock scale". Plus S4 (Reinhart and Cerezo Davila is a review by its own title; Motuzienė is about office buildings by its own title). Each is small; together they signal that the novelty section was assembled rather than argued.

---

## 7. What is OUTSIDE MY SCOPE

- I did not open or recall the content of any of the nine competitor studies in Table 1; every ✓ and ✗ is judged only against what the manuscript itself says about that study.
- I did not read the authors' companion C-VAE manuscript (Iseri and Hachem-Vermette 2026), so I cannot say which of the six columns it fills; I only note that the submission says "most".
- I cannot say whether any published study fills all six columns; that is the Gemini version's task.
- I did not assess Barsanti, Yilmaz and Binder (2024), which the Gemini prompt names but the manuscript does not.
- I cannot say whether Chiou et al. (2011) uses a calibrated model, whether Yin et al. (2024) reports intraday series, or whether Motuzienė et al. (2022) forecasts a future year; I only note that the manuscript's own descriptions of those studies sit uneasily with the cells it assigns them.
- I did not check whether "stock-scale" has an accepted threshold in the field; I only note the manuscript's own phrase "thousands of dwellings" against its own N = 50 per cell.
- I did not evaluate the prompt's context sentence that the paper compares "against measured hourly utility data"; the submitted text contains no such comparison, and I treat that as a description of the planned revision, not of this manuscript.
