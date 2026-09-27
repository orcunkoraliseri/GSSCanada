# Permit-Reading Retrofit and Cooling State for an Occupied Building Stock
### Montreal permits (French) and Toronto permits (English) -> abstaining reader -> stock state -> paired EnergyPlus with GSS occupancy
#### Paper 5 of the series — the build checklist

Written 2026-09-26. **This is the checklist to create the project.** The one-page picture is
`5thJ_00_Permit_Reading_Pipeline_Overview.md`; the design and its Progress Log are
`5thJ_01_Methods_Design.md` (the state). Tick a box only when the artefact exists on disk and was
re-derived by the manager, never on an employee's word. Edit in place; never fork a copy.

Legend: `[x]` done and reviewed · `[~]` exists but part void · `[ ]` not started · 🔴 read first.

---

## AIM
Read retrofit and cooling state (windows, insulation, heat pump, air conditioning, heating change)
from short permit text with a language model that abstains when the text is too thin, turn it into a
per-building probability, and carry that uncertainty through paired EnergyPlus runs driven by GSS
occupancy. See the Overview for research questions RQ1 to RQ4.

## STEP 0 — DECISIONS AND ROLES
- [x] Subject ruled: D-5J-2 (a), A7 climate form (LLM reads permit text for retrofit and cooling state, with abstention, feeds stock model + GSS occupancy).
- [x] Design v1 written: `5thJ_01_Methods_Design.md` (sections 1 to 10).
- [x] D-5J-3 ruled 2026-09-26: (a), author labels ~2,600 texts, colleague labels 400 blind. Recorded in design doc section 9.
- [ ] Colleague for the 400 agreement texts named (needed if D-5J-3 = (a)).
- [ ] Venue left open until RQ1 results exist (O-6).

## STEP 1 — WP0: FREEZE AND INVENTORY (sonnet employees; data in `GSSCanada\_5J_data\`, outside the repo)
Task doc `impl/2026-09-22_wp0_task.md`.

**1A. Permits and roll** (`impl/2026-09-22_wp0A_permits_roll.md`)
- [x] Montreal permits downloaded, row count and checksum written (514,439 roll rows, sha prefix 7e3f834c).
- [x] Toronto permits: 1,083,669 unique, 729,339 residential, 101,611 "HVAC -" texts. Licence: Open Data Licence - City of Toronto (O-2 closed).
- [x] Permits joined to assessment roll by address: 410,123 of 420,572 (97.5 %).
- [x] 🔴 Trap fixed: roll year 9999 = placeholder (19,990 rows) and years < 1800 = vintage unknown, fall back to the borough mix.
- [x] 🔴 Trap fixed: 16,098 joins (3.9 %) have candidates in different vintage bands, carry a mixture weighted by dwelling count.

**1B. Area truth and model inventory** (`impl/2026-09-22_wp0B_areatruth_models.md`)
- [x] StatCan 38-10-0019-01 (AC) and 38-10-0286-01 (heating) rows pulled for Montreal and Toronto.
- [x] 2J model inventory: all four models have a gas furnace and DX cooling (O-4 mostly closed).
- [x] EnerGuide download complete: 21 files, `download_log.txt` ends ALL_DONE.
- [x] **B2 EnerGuide redo** (done 2026-09-26, reviewed): rows per Montreal H-FSA, FSAs with ≥ 30 homes, heat pump / AC / insulation columns. The first counts are VOID (read half-downloaded files). B2 never wrote its section; relaunch ONE fresh sonnet employee on task-doc section "Employee B2".
- [x] Manager re-derived numbers (one file size vs `download_log.txt`, count of Montreal FSAs with ≥ 30 houses, one FSA's heat-pump share); watch for strings counted as "has AC" that mean "none".
- [x] O-3 closed in the design doc (109 H and 91 M FSAs with >= 30 houses); Progress Log entry written; B impl Status set to DONE.

## STEP 2 — WP1: LABELS AND SAMPLING
- [~] `5thJ_02_Label_Spec.md` DRAFT v1 written 2026-09-26 (author to read; Toronto examples still to be replaced by real rows): rule, French and English positive and negative examples for each of W, I, HP, AC, F, plus reset events N and D; the "cannot tell" rule.
- [~] Known traps in the spec: "isolation" for sound or fire separation is not I; "même ouverture" window work is W; Toronto boilerplate is not F.
- [x] Sampling frame built (sonnet, reviewed 2026-09-26): residential permits only; strata = keyword hit group × decade × building type; rare groups (HP, AC, I) oversampled; inclusion probabilities stored. 42 strata got no draw (0.2 % Montreal, 1.4 % Toronto permits): limitation.
- [x] WP0 rules applied: the extra Toronto "Residential"/"House" rows count as residential (2,386, not 2,394); the roll is not joined yet, only `source_id` is carried, so the roll-year and mixture rules apply at WP4.
- [x] Sizes drawn: Montreal 2,000 (dev 400, calibration 800, test 800); Toronto 600 (calibration 300, test 300). Manager re-derived counts, quotas, weights, blind sheet.
- [x] Test sets sealed: `_5J_data\wp1\sealed\test_manifest_SEALED.csv`, sha256 d5f66eb3..., read-only; nothing opens it before Step 3.
- [ ] Labelling done by the author (~2,600 texts, 10 to 12 hours), yes / no / cannot tell per label.
- [ ] 400 texts labelled twice, blind; Cohen's kappa per label; any label under 0.6 merged or dropped before any model is scored (G5J.1).

## STEP 3 — FREEZE THE GATES (before any test row is scored)
- [ ] Section 7 thresholds turned from DRAFT to frozen, checksum written in the design doc.
- [ ] Perturbation table written: one named perturbation breaks exactly one gate.
- [ ] 🔴 Each gate seen failing on its perturbation (G5J.1 shuffled labels, G5J.2 copy of keyword rule, G5J.3 shuffled calibration labels, G5J.5 alpha 0.01, G5J.6 uniform 50 % prior).
- [ ] What the exit code and the SUMMARY line mean is written down: NOT_EVALUABLE is not PASS.

## STEP 4 — WP2: FOUR READERS (RQ1)
- [ ] Reader 1: keyword rule, French and English stems, negation and trap list from the label spec.
- [ ] Reader 2: Gunay-style association rules, re-implemented from the paper's description.
- [ ] Reader 3: small fine-tuned encoder (multilingual or French-first), or few-shot only if sizes do not allow training.
- [ ] Reader 4: open-weight instruction model on one A100 80 GB, constrained JSON output, per-label probabilities from answer-token log-probabilities.
- [ ] Two or three model families tried on the dev split only; winner pinned (name, revision hash) before the test set is opened.
- [ ] All readers scored on the same sealed Montreal test rows, re-weighted by inclusion probability.
- [ ] G5J.2 read: LLM beats best of readers 1 to 3 by 0.05 macro-F1 with bootstrap interval excluding 0, else reported as a tie.

## STEP 5 — WP3: ABSTENTION WITH STATED COVERAGE (RQ2)
- [ ] Split conformal per label, nonconformity = 1 minus probability of the true answer, alpha 0.10; output {yes}, {no} or {yes, no} (= abstain).
- [ ] Mondrian versions by building type, decade and borough group.
- [ ] G5J.3 coverage in [0.87, 0.93], overall and per group with ≥ 50 test rows.
- [ ] Shift tests: Montreal calibration on Toronto unchanged (expected to break, reported as such), then recalibrated on the 300 Toronto calibration rows; before 2010 vs 2010 and later (G5J.4, report only).
- [ ] G5J.5 abstention ≤ 40 % on W; abstention and set size reported for every label; accuracy-coverage curve against plain thresholding.

## STEP 6 — WP4: PERMIT EVENTS -> BUILDING STATE (RQ3)
- [ ] Building history built: ordered permits to 2022, N or D resets.
- [ ] Prior π(e, FSA) from EnerGuide scaled to the StatCan city share; vintage from the roll.
- [ ] Detection rate d(e, city): near zero for HP and AC in Montreal by rule; estimated for W and I from read counts vs area shares.
- [ ] P(upgraded | nothing read) = π(1 − d) / (1 − π d) implemented and unit-checked.
- [ ] G5J.6 area check: 90 % interval holds the EnerGuide share in ≥ 80 % of Montreal FSAs with ≥ 30 audited homes and the StatCan city share for AC and heat pump.

## STEP 7 — WP5: ENERGYPLUS CAMPAIGN (RQ4)
- [ ] O-1 closed: envelope U-values and air-tightness by vintage (before 1960, 1960 to 1989, 1990 and later); external deep research prompt written and run by the author only if the author agrees.
- [ ] Baseboard-electric and cold-climate heat-pump variants built (standard EnergyPlus objects); AC off = cooling coil switched off; one test run per variant.
- [ ] Vintage levels set by replacing insulation values inside existing constructions; air-tightness through the airflow-network leakage areas.
- [ ] About 24 state combinations listed after impossible ones are removed.
- [ ] 50 GSS 2022 household draws per archetype through the 2J pipeline, matched to the Montreal mix from Census PUMF.
- [ ] Campaign submitted on Speed (`sbatch` only, within the 32-CPU cap, 7-day walltime): ~4 × 3 × 24 × 50 × 2 ≈ 29,000 paired runs; job IDs written to an impl doc.
- [ ] G5J.7 base-stock band checked (report only).

## STEP 8 — WP6: PROPAGATION AND SPLIT (RQ4)
- [ ] Per run: annual heating and cooling, winter and summer peak hour, occupied-hour hours above 26 °C and 28 °C for homes without AC.
- [ ] 1,000 stock draws from the WP4 probabilities; median and 90 % interval for Montreal and per borough.
- [ ] Two-factor random-effects split (state draws × occupancy draws, paired): shares for unknown state, occupancy, interaction.
- [ ] Counterfactual: (a) prior only, (b) keyword reader, (c) LLM reader with abstention; the narrowing (a) to (c) is the value of reading the text.

## STEP 9 — WRITING
- [ ] Nearest-work rows re-checked at source; O-5 papers (Pauling 2026, Jiang 2025) read.
- [ ] Figures: only data plots computed by script from frozen data; image prompts for any drawing (never draw).
- [ ] Manuscript written in the 2J AE style; limitations written as limitations, gate verdicts stay as recorded.
- [ ] Venue chosen (O-6); cover letter; AI, funding, CRediT and acknowledgements copied from the 2J AE revision.

---

## VALIDATION PLAN
Gates G5J.1 to G5J.7 in the Overview and design doc section 7. No test row is scored before Step 3 is
ticked. A gate counts only after it has been seen failing.

## KEY DESIGN DECISIONS
See the Overview table. Long-lived decisions go in the design doc; per-task state goes in
`impl/<YYYY-MM-DD>_<task-slug>.md`, one file per task, ledger append-only.

## OPEN DECISIONS
D-5J-3 (who labels), O-1 (envelope values), O-3 (EnerGuide counts, B2), O-5, O-6.

## LIMITATIONS
Pointer to design doc sections 3 to 6; see the Overview.

## PROGRESS LOG (append-only)
- 2026-09-26 (manager): checklist and Overview created on the author's request. State found: WP0-A
  done; WP0-B partly void (B2 never wrote its section, no leftover process); D-5J-3 open.
- 2026-09-26 (manager): D-5J-3 ruled (a). Label spec v1 written. Keyword count found HP and AC do appear in Montreal permit text (new builds, contractor add-ons); WP4 estimates d from data for those, near zero only for retrofits. B2 relaunched (background). Artifact and manager prompt updated.
- 2026-09-26 (manager): B2 reviewed and DONE; O-3 closed. Step 1 (WP0) is complete.
- 2026-09-26 (manager): WP1 sampling frame built and reviewed (2,600 texts, sealed test file, blind sheets). Author reads the label spec and starts labelling next.
