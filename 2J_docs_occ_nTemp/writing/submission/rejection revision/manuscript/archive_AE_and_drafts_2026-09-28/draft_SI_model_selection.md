# SI Section: Generative Model, Selection, and Diary Validation

Draft written by T36 (WP10), 2026-09-15. Moves detail out of the main text per reviewer 2 point 1
and reviewer 1 M2c. Numbers were re-read from source files, not copied from the archived manuscript;
the number trace table at the end lists every value with its source and whether it matches the
archived text.

---

## S.1 Generative model architecture

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

The model has about 29.25 million parameters and an internal width of 384. This separation of "what
the person is doing" from "whether they are home and with whom" is what let this model pass every
check described below, while several competing designs that mixed the two signals did not.
The architecture is summarized in SI Table B1 (already in the supplementary tables).

## S.2 Model selection search

**How many candidates.** Over 40 candidate model designs were tried in a staged search: first
trained on a small 2% slice of the data, then 20%, then the full data, so that clearly weak designs
could be dropped early without spending full training time on them. The candidates covered several
different families: simple statistical (Markov chain) models, autoregressive sequence models,
variational autoencoders, GAN-style models, cross-attention architectures, and masked
discrete-diffusion models.

**The four checks used to keep or reject a candidate.** A candidate had to pass all four of these to
be considered:
- How different the generated mix of activities is from the real mix (a distributional distance
  measure, "activity JS", capped at 0.05).
- How far off the generated at-home percentage is from observed data (an error measure in
  percentage points, capped at 5.3 pp).
- How far off the worst single co-presence channel is (capped at 5.0 percentage points).
- A single combined score blending several of the above (capped just under 1.045).

**Where the four checks came from.** All four thresholds were inherited from an earlier baseline
model run rather than derived independently. Two of the four (the combined-score cap of 1.045 and
the at-home error cap of 5.3 pp) are set exactly equal to that earlier baseline model's own observed
scores, not to an independent target. The activity-distance cap (0.05) is asserted alongside the
other three with no independent justification found in any project document. The co-presence cap was
tightened during the same revision from 10 percentage points to 5 percentage points, with no reason
recorded for the change. None of the four thresholds has a documented independent basis (for example
a survey sampling-error floor); this is reported here as a limitation of the selection procedure, not
as an error in the chosen model. See the number trace table for exact citations.

**Which candidates passed.** The project's own working notes describe the chosen model as the only design to pass all four checks. A re-check of the four published thresholds against
the individually reported scores of every candidate shows this is not quite right: three other
candidates (each a variant of the chosen model with parts of its head design changed) also clear all four
published thresholds when the thresholds are applied literally. The working notes had actually scored
those variants against a stricter, unpublished bar (beating the chosen model's own combined score, plus an
additional check not among the published four), which is why they read as failing in the notes even
though they clear the published thresholds. This does not change which model was chosen: among the
four candidates that pass the four published checks, the chosen model still has the best (lowest)
combined score, so the choice stands. What changes is only the sentence describing why: the model is
described as "the candidate with the best combined score among those that cleared all four checks,"
not as "the only candidate to clear all four checks."

**Why the chosen model was picked.** Passing was necessary but not sufficient among the four
qualifying candidates; the chosen model was picked because it had the lowest (best) combined score among them.
Some notable design choices did not clear the bar: one masked-diffusion candidate produced the single
best combined score of the entire search, but failed the activity-distance and at-home checks (its
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

## S.3 Diary validation on a held-out year

Two related checks assess whether the model's generated diaries for the most recent survey year
(2022) look like real 2022 behaviour.

**The ceiling.** Before either check was run, the project set one distributional distance ceiling of
0.10 for every day type: weekday, Saturday and Sunday. That is the ceiling we report against
throughout, for both checks.

**Held-out-year test.** The model, trained only through the second-most-recent survey year (2015),
was asked to generate diaries for the entirely unseen 2022 year. On weekdays the generated diaries
scored 0.0619, within the 0.10 ceiling.

**Backcast reconstruction.** Separately, the fully trained model (which has now seen 2022 data) was
asked to reconstruct 2022 diaries using the real 2022 respondent information. On weekdays this
scored 0.0630, also within the 0.10 ceiling.

**Weekends do not meet the ceiling.** On weekends both checks score well above 0.10: 0.1817
(Saturday) and 0.1843 (Sunday) in the held-out-year test, and 0.1637 and 0.1618 in the backcast. We
state this as a result, not as a pass. Two further points belong with it.

First, the ceiling was widened to 0.20 for weekends after these values were seen, and the weekend
results were then recorded as passing. We do not use the widened ceiling anywhere in this paper, and
no weekend result should be read as having met a pre-registered ceiling.

Second, the weekend gap is concentrated in one identifiable part of the evaluation set. That set
mixes two kinds of rows: diaries genuinely observed on that day type, and diaries the model had to
synthesize because the respondent reported a different day type. Scored on the genuinely observed
2022 weekend diaries alone, the distance is 0.036 (Saturday) and 0.040 (Sunday), well inside the
0.10 ceiling; the synthesized rows sit 0.138 to 0.175 from the observed distribution. Weekend
diaries are fewer and weekend behaviour is more varied, and raising the weekend training weight
twice moved the score by about 0.005, so the gap does not appear to be an optimisation shortfall.
We therefore treat the synthesized weekend days as a stated limitation of the diary completion step,
and weekend results are carried through the rest of the paper with that limitation attached.

## S.4 Post-hoc calibration (raking) cost

After the model generates diaries, a calibration step ("raking") is applied that nudges the
generated at-home percentages, slot by slot, to match their target values exactly. This step is
needed because the raw generated output, while close, is not perfectly calibrated to the target
at-home percentages. The cost of this adjustment is that roughly 1.8-2.1% of individual
slot-records end up with an activity label that no longer matches its own at-home flag (for example,
a slot still labelled "away" activity after being nudged to "at home"). This is treated as harmless
for the building energy model, because the energy model reads only the at-home flag to decide
occupancy; it does not read the activity label for that purpose.

---

## Number trace table

**Author decision, 2026-09-15.** Rows marked OLD CAMPAIGN or OLD BUILD below must be re-derived on the
rebuilt runs (T20, T21, T28, T30) before they may appear anywhere in the manuscript or SI. Any row the
rebuilt runs do not produce is dropped, not quoted from the old campaign. Old and rebuilt numbers are
never mixed in one table.

| Value | Meaning | Source file:line | Matches archived text | Notes |
|---|---|---|---|---|
| d_model = 384, ~29.25M params | Model width and size | `step4_Speed_Cluster/step4_Speed-Cluster_docs/step4_training_v4.md:86` ("Identical model: 29.25 M params"); d_model=384 also at `:308` | Yes | |
| d_cond = 90 | Conditioning vector size | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:203` ("Phase 7 showed d_cond=90 hurts", i.e. d_cond=90 is the Phase-2/current bundle); `writing/submission/tables/SI/Table_B1_B2.md:24` | Yes | Also cross-checked against existing SI Table B1 |
| Gradient-detach barrier between activity decoder and binary heads | Architecture feature | `step4_Speed_Cluster/step4_Speed-Cluster_docs/step4_training_v4.md:335` (".detach() barrier means binary-head gradients never reach the AR decoder") | Yes | |
| Over 40 trials in the search | Trial count | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:3` ("across 40+ trials") and `:270` | Yes | |
| Four gate thresholds: act JS <= 0.05, AT_HOME RMS <= 5.3 pp, co-presence gap <= 5.0 pp, composite < 1.045 | Selection checks | `step4_Speed_Cluster/step4_Speed-Cluster_docs/step4_training_v4.md:337-344` (gates table) | Yes | |
| J3 gate scores: act JS 0.0191, AT_HOME RMS 4.57 pp, Spouse gap -2.03 pp, composite 0.6355 | Chosen model's scores | `step4_Speed_Cluster/step4_Speed-Cluster_docs/step4_training_v4.md:341-344` | Yes | |
| MDLM best composite 0.559 (0.5592), AT_HOME RMS 7.81 pp | Best-composite failing candidate | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP.md:1210` ("MDLM_G1 0.5592 ... 7.81 ... 4.57") and `comparision.md:126` | Yes (archive rounds 0.5592 to 0.559) | |
| Cross-attention decoders collapse to 19-23 pp co-presence gap | Negative finding | `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:410` ("COP max gap ranges 19-23 pp") | Yes | |
| Threshold provenance: composite<1.045 and AT_HOME<=5.3pp equal the F1 baseline's own scores; act_JS<=0.05 has no independent rationale; Spouse gate tightened 10pp -> 5pp with no stated reason | Where the checks came from | `DONE_step4_training.md:806,130,480,842`; `DONE_step4_training_v2.md:24`; commit `de99c08f` (2026-04-28) | Not previously stated in archived text | From `impl/2026-09-15_T04_wp9_threshold_provenance.md` Verified section, re-derived via `git log -S` by that task; re-cited here, not re-run |
| At original thresholds, J3, J5_X1, J5_X2, J5_B all pass 4/4 | Candidates passing, literal thresholds | `impl/T04_out/threshold_sensitivity.csv` row 1 (`baseline_original`); cross-checked against `step4_training_v4.md:738-741` (J5_X2, J5_A, J5_B scores) and `:354-361` (J5_X1, J5_X1b scores) | No | Archive text (`archive/2J_manuscript_submission.md:208`) says "the sole model to clear all four gates"; this is wrong as literally checked. J3 keeps the lowest composite among the 4 passers, so the choice of J3 is unaffected. |
| Threshold-sensitivity: same 4-model set passes under +-10/20% on composite, Spouse, or act_JS alone; AT_HOME -20% (or all-together -20%) narrows to 1 passer (J5_X1) and flips the selection | 21-scenario sensitivity result | `impl/T04_out/threshold_sensitivity.csv` all 21 rows (rows 3-6, 8-18, 20-21 keep the 4-set; row 7 and row 19 flip to J5_X1 alone) | Not previously stated in archived text | Job 1328244, collected and byte-verified per `impl/2026-09-15_T04_wp9_threshold_provenance.md` |
| Held-out-year (True-Future-Test) weekday JS 0.0619, weekend 0.1817 (Sat) / 0.1843 (Sun); pre-registered ceiling 0.10 for every stratum, so both weekend values miss it (the scorecard's < 0.20 is the widened ceiling, applied after the fact) | Held-out-year test | `06_longitudinalForecastingGSS.md:655` ("TFT Phase 3 WD/Sat/Sun (2022 unseen) | < 0.20 | 0.0619 / 0.1817 / 0.1843 | PASS") | Weekday: yes. Weekend: archive text says "0.16-0.18" for weekend in general; this specific held-out-year run's Sunday value (0.1843) sits just above that stated range | The archive text's "0.16-0.18" appears to blend this run with the backcast run below rather than quoting one run precisely |
| Backcast weekday JS 0.0630 within the 0.10 ceiling; Sat 0.1637 and Sun 0.1618 above it (weekend ceiling widened to 0.20 after the result; not used) | Backcast reconstruction | `06_longitudinalForecastingGSS.md:782`; re-baseline at `:26,576,616` | Yes | Manager: the re-baseline happened after the weekend values were seen; S.3 now states this and does not rely on it |
| Observed-only rows: weekday 0.046, Sat 0.036, Sun 0.040 | Weekend-floor evidence | `06_longitudinalForecastingGSS.md:788-790` and `:804` | Yes (archive: "0.036-0.046") | |
| Synthetic-only rows sit 0.138-0.175 from observed | Weekend-floor evidence | `06_longitudinalForecastingGSS.md:805` (WD=0.175, Sat=0.147, Sun=0.138) | Yes (archive: "0.14-0.18") | |
| OLD 2030 BUILD, re-derive or drop: 35/35 checks passed (forecasting validation scorecard) | Overall forecasting scorecard | `outputs_step6/step6_validation_report.html:21` ("35/35 checks passed", generated 2026-07-10) | Yes | HTML report, read via grep only, not opened whole |
| Raking coherence cost ~1.8-2.1% of slot-records | Post-hoc calibration cost | `04_augmentationGSS.md:59` ("coherence cost ~1.8-2.1% of slot-records, BEM-harmless") | Yes | |
| ~192,183 diary-days (64,061 respondents x 3 day-types) | Augmented output size | `04_augmentationGSS.md:9` | Yes | |
| Donor-draw completion; earlier copy-day approach diluted weekend marginal by -2.76 pp | Schedule-completion method | `07_bemIntegrationGSS.md:93` and `:251` | Yes | Not part of the model-selection/diary-validation scope per se, but requested in si_move_list; kept out of S.1-S.4 prose since it belongs to a different SI subsection (schedule completion), see WHAT I DID NOT VERIFY |
| OLD CAMPAIGN, re-derive on rebuilt runs: End-use-layer validation scorecard PASS=6 WARN=1 INFO=3 FAIL=0 | Section-3.6 scorecard | `09_activityDrivenLoads_val.md:222` ("Console scorecard: PASS=6 WARN=1 INFO=3 FAIL=0") | Yes | |
| OLD CAMPAIGN, re-derive on rebuilt runs: 4,800 paired runs, of which 4,795 carried complete meter output (archived) vs. 4,790 completed / 10 absent (source) | End-use layer run completeness | `09_activityDrivenLoads_val.md:37` ("4,790 completed (10 absent)") | No, give both | Archive says 4,795; the source validation doc says 4,790. Flagged as a discrepancy, not corrected here. |
| OLD CAMPAIGN, re-derive on rebuilt runs: Campaign 6,000/6,000 runs; DX-coil fatal fixed by Gross Rated Sensible Heat Ratio autosize->0.75; EUI delta <= 0.013 kWh/m2/yr | Section-4.4 DX-coil fix | `Step8_docs/cluster_rerun.md:160,297-309,328,341` | Yes | |
| OLD CAMPAIGN, re-derive on rebuilt runs: Campaign verification scorecard 24 PASS / 0 WARN / 3 INFO / 0 FAIL (archived) | Section-4.4 scorecard | `Step8_docs/cluster_rerun.md:341` gives "24 PASS / 0 WARN / 0 FAIL" (no INFO count stated there); `Step8_docs/08_09_injection_bug_status.md:3` gives a different, later 8-section re-validation: "22 PASS / 2 WARN / 3 INFO / 0 FAIL" | No, give both | Two different validation passes exist in the source docs and neither exactly reproduces the archived "24 / 0 / 3". The 24-PASS/0-WARN half matches `cluster_rerun.md`; the "3 INFO" half matches a different, separate scorecard in `08_09_injection_bug_status.md`. NOT reconciled here; flagged for the collector. |
| OLD CAMPAIGN, re-derive on rebuilt runs: Schedule round-trip fidelity exact; mean peak hour 17.5-17.7 h; max archetype EUI change +2.85% | Section-4.4/4.2 timing results | `Step8_docs/08_09_injection_bug_status.md:3` ("round-trip EXACT all 5 years, peak hour 17.5-17.7 h, EUI phase-invariant vs v1 (max delta +2.85% SingleD)") | Yes | |
| OLD BUILD, re-derive on rebuilt 2022 and 2030 schedules: Schedule-integration validation: 2022 29 PASS / 0 WARN / 0 FAIL; 2030 28 PASS / 0 WARN / 0 FAIL | Section-4.2 scorecard | `07_bemIntegrationGSS_val.md:16-17` and `:199` | Yes | |

---

## Ledger
- No cluster jobs run by this task; all reading done locally against files already on disk (T04's
  Speed job 1328244 was run and collected by an earlier task, reused here read-only via
  `impl/T04_out/threshold_sensitivity.csv`).
- Read `archive/2J_manuscript_submission.md` lines 195-360 (offset/limit) for the exact archived
  wording and line numbers used above.
- Read `impl/2026-09-15_T04_wp9_threshold_provenance.md` in full (small file) for threshold
  provenance and the sensitivity-scenario summary.
- Read `impl/T04_out/threshold_sensitivity.csv` (22 lines) in full.
- Grepped (never opened whole) roughly 15 source docs under `2J_docs_occ_nTemp/` (excluding the
  `writing/` duplicate copies of the manuscript, which are not sources) for every quoted number:
  `step4_training_v4.md` (1232 lines, read only the cited ranges), `04_augmentationGSS_IMP.md`,
  `04_augmentationGSS_IMP_2.md`, `04_augmentationGSS.md`, `06_longitudinalForecastingGSS.md`
  (874 lines, read only the cited ranges), `07_bemIntegrationGSS.md`, `07_bemIntegrationGSS_val.md`,
  `09_activityDrivenLoads_val.md`, `Step8_docs/cluster_rerun.md`, `Step8_docs/08_09_injection_bug_status.md`,
  `outputs_step6/step6_validation_report.html` (grep only, HTML report not opened whole),
  `writing/submission/tables/SI/Table_B1_B2.md` (127 lines, read in full, cross-check only, not a
  primary source and not edited).

## Verified
See the number trace table above; every row that says "Yes" or "No, give both" was read directly
from the cited file:line during this task, not carried over from the archived manuscript or from
si_move_list.md's own paraphrase.

## Decisions
- Kept the "J3 was the only model to clear all four gates" correction in plain words (S.2) rather
  than silently keeping the archived "sole model" phrasing, because task doc rule 2 (T04) already
  established this as a required correction and the si_move_list's own item 2 asks for "the
  candidates that passed."
- Put the donor-draw / copy-day history row in the trace table (it was in si_move_list's "WP10 move
  list") but did not write prose for it in S.1-S.4, since it belongs to "schedule-completion method
  detail," a different SI subsection than model selection / diary validation, per si_move_list's own
  "Target" column. Not asked of the author; flagged here for whoever assembles the SI section order.
- Did not attempt to reconcile the two conflicting campaign-verification scorecards (24/0/0 vs
  22/2/3) found in `Step8_docs/cluster_rerun.md` vs `Step8_docs/08_09_injection_bug_status.md`; both
  are cited in the trace table as "No, give both" rather than picking one. This is a Step-8
  documentation gap, not something to be resolved by this SI-drafting task.
- Did not open `writing/submission/tables/SI/Table_B1_B2.md`'s own claim ("J3 is the only 4/4-gate
  model across 40+ trials," line 9 and 59) for correction; that file is an existing SI table, not the
  task's draft target, and the task doc says write only the one draft file. Flagged here so the
  collector updates Table_B1_B2.md to match the corrected S.2 wording.

## Next
Collector/manager to: (1) decide where the donor-draw history row lands (a separate SI subsection,
per si_move_list's own routing); (2) reconcile or explicitly flag-and-keep the two conflicting
Step-8 scorecards (24/0/0 vs 22/2/3) rather than silently picking the archived "24/0/3" hybrid;
(3) correct `Table_B1_B2.md` lines 9 and 59 ("sole 4/4-gate model") to match this draft's S.2
wording, since that table is referenced from the main text as "SI Table B1" and would otherwise
still assert the now-corrected claim; (4) confirm 4,795 vs 4,790 for the end-use-layer run count
before this draft is finalized into the manuscript's SI.

## WHAT I DID NOT VERIFY
- Did not verify the F-series (pre-J-series) threshold history beyond what T04 already recorded; did
  not re-run `git log -S` myself, relied on T04's citations (`DONE_step4_training.md:806,130,480,842`,
  `DONE_step4_training_v2.md:24`, commit `de99c08f`).
- Did not open `outputs_step6/step6_validation_report.html` as a full file (HTML, could be large);
  read only the grep-matched line and its immediate context for the "35/35 checks passed" figure.
  Did not check whether that report's underlying 35 individual checks match section 3.4's specific
  weekday/weekend/backcast numbers one-for-one, only that the overall tally is 35/35.
- Did not reconcile the 4,795 (archived) vs 4,790 (source) end-use-layer run-count discrepancy, or
  the 24/0/3 (archived) vs the two source scorecards (24/0/0 and 22/2/3) discrepancy; both are
  flagged in the trace table for the collector rather than resolved here.
- Did not independently re-derive the co-presence 19-23 pp figure or the MDLM composite/AT_HOME
  figures from raw diagnostics JSON; took the already-tabulated doc values at
  `04_augmentationGSS_IMP_2.md:410` and `04_augmentationGSS_IMP.md:1210` as the source, consistent
  with how T04 built its own trial roster.
- Did not check the SI Appendix (archived file lines 599+) for whether it already has a home section
  for this content that this draft should be merged into rather than appended as new; si_move_list's
  own "WHAT I DID NOT VERIFY" flagged the same open question and it remains open here.
- Did not verify the exact wording the main text will keep versus move to this SI section; this
  draft is the SI content only, not a proposed edit to the main-text paragraphs it is drawn from.

## Status: DONE
Draft exists at `manuscript/draft_SI_model_selection.md` (this file's sibling in the same folder).
All numbers in S.1-S.4 and the trace table are re-read from source per the task's hard rule; two
discrepancies (end-use-layer run count, campaign verification scorecard) are surfaced rather than
silently resolved. No cluster access used. Token budget not exceeded (~90k used this session).
