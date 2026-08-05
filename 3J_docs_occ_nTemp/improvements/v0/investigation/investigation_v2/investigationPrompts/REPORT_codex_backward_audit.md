# Independent backward audit — 3J Leg-3 — CODEX

**Date:** 2026-08-04 · **Auditor:** Codex · **Basis:** code and artefacts

**Blindness declaration:** inside `improvements/investigation/` I opened only my own prompt. I did not open the prior audit, its README, `deepResearch Prompts/`, or the other auditor's prompt or report. Contaminated passages encountered: none. Findings below were reached independently of any prior audit.

## Method, and its limits

I read both Leg-3 entry documents before inspecting the Python, CSV, IDF, TXT and HTML artefacts in Steps 1–9; I did not read any other item below `improvements/investigation/`. I inspected the Step-4 training/inference/raking/validator code, Step-5 aggregation, Step-7 schedule conversion and gates, the mixed-use injector, Step-8 aggregation, a Step-9 injected IDF, and the submitted 2J manuscript. I streamed the 2022 Step-7 CSV and re-derived its schedule counts; I re-summed the 56 rows of `agg_meta.csv`. I did not run EnergyPlus, retrain, submit jobs, read raw GSS microdata, or open third-party sources. Therefore this is a code-and-artefact audit, not an independent survey or physical-model validation.

## Verdict, up front

The delivered artefacts do demonstrate several real protections: the post-projection three-channel mutex is rechecked, the IDF does receive per-space residential `People` objects, and the current Step-8 area table closes. But the residential mechanism described in the submitted manuscript is not the one that is executed: the claimed household maximum is computed and then bypassed, while the BEM uses the mean of separately assigned member diaries times household size. In Leg 3, key claims of rare-head and legacy-head validation are also not established by the reported gates: retail PR-AUC/F1 is teacher-forced, the regression gate is explicitly a non-row-matched distributional proxy, and a supposed diurnal gate cannot fail for any numeric out-of-band result. These are evidence problems, not assertions that every resulting energy number is wrong.

| | Finding | Severity | Step | Reaches the submitted 2J paper? |
|---|---|---|---|---|
| C-1 | Submitted paper says household occupancy is a per-slot maximum; shipped converter uses a per-member mean instead | High | 5, 7, injection | yes |
| C-2 | Legacy-head regression PASS is a distributional proxy, not the stated frozen, row-matched comparison | Med | 4 | no |
| C-3 | Retail diurnal “gate” cannot FAIL on a numeric out-of-band result | Med | 4 | no |
| C-4 | Retail PR-AUC/F1 measures teacher-forced reconstruction, not the generated/raked artefact sent downstream | Med | 4 | no |
| C-5 | Canonical Step-4 output has only a single-seed scorecard and lacks checkpoint/raking provenance needed to reproduce its lineage | Med | 4 | no |

## Findings

### C-1 — household-max semantics claimed by the submitted paper are bypassed

**The evidence.** Step 5 computes `HH_hom30_*` as a maximum over `SIM_HH_ID` at `Step5_docs/3rdJ_05_censusLinkage_4split.py:1027-1045`. Step 7, however, groups the original `hom30_*` fields and takes their mean (`.../Step7_docs/3rdJ_07_aug_to_bem_4split.py:304-314`); it does not reference `HH_hom30_*`. It then writes that fractional mean as `Occupancy_Schedule` (`:321-343`). The Step-7 residential gate tests only range, non-negative metabolic rate and day-type coverage (`:859-870`), not equivalence to the Step-5 maximum.

I streamed `outputs_step7/BEM_Schedules_4split_2022.csv`: 1,109,520 rows; 785,616 rows had `HHSIZE > 1`; 94,293 of those (12.002%) had a strictly fractional occupancy schedule. Examples include HH 40742 at weekday hour 17 = 0.5 and HH 40749 at weekday hour 6 = 0.75. The command was a read-only `Import-Csv` stream counting `0 < Occupancy_Schedule < 1` conditional on `HHSIZE > 1`. The injected IDF then attaches such a schedule to a full headcount: `.../finding9_verify/Y2022__Tall__MTL/injected.idf:90452-90462` shows `MXU_Residential_Occ_HH76197` with `Number of People = 4`.

The submitted manuscript instead says that agents are aggregated using the per-slot maximum (`2J_docs_occ_nTemp/writing/fullSet/readySubmission.md:211`) and calls the result a household occupancy schedule (`:229-235`).

**Why it matters.** The executed quantity is expected members at home, under independently assigned member diaries: `HHSIZE × mean(member AT_HOME)`. It is not the binary “any member present” quantity described in the paper and not the `HH_hom30` quantity computed in Step 5. Either definition can be defensible, but they yield different schedules and internal gains. The submitted methods statement is false as written; its energy and timing claims are not evidence for the maximum-based mechanism it describes.

**Magnitude, honestly.** The semantic discrepancy affects 12.002% of multi-person hourly schedule records in the measured 2022 product; its energy effect is unknown here because no paired mean-versus-max EnergyPlus comparison was run. The difference may be small in stock aggregate or material for diversity/peak claims; this audit does not infer either.

**Falsifier.** For the exact 2022 input, compare Step-7 `Occupancy_Schedule` against both `mean(hom30_*)` and `mean(HH_hom30_*)` by `(SIM_HH_ID, Day_Type, Hour)`. If it equals the latter (after the documented half-hour/hour and clock transforms), this finding is false.

**Recommended action.** Before relying on the submitted paper, correct the manuscript to describe the executed expected-members-at-home model, or change and revalidate the converter to use the household maximum. Also add a unit test that makes an `HH_hom30`/`hom30` divergence and requires the intended one. Cost: low for the reconciliation/test; high if resimulation or manuscript correction after submission is required.

### C-2 — REG-1/REG-2 cannot establish the stated legacy-head non-regression claim

**The evidence.** The validator itself says the common frozen validation split and respondent identities are not persisted (`Step4_docs/3rdJ_04_augmentationGSS_4split_val.py:1749-1755`). It consequently compares the current synthetic distribution to the Leg-2 synthetic distribution (`:1755-1762`), not the same held-out observations scored by both checkpoints. The reported PASS labels disclose the same limitation: `outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/step4_validation_report.txt:140-141` calls both results “PROXY: cross-leg synthetic-vs-synthetic, not row-matched frozen split.”

**Why it matters.** Equal marginals/mean curves do not establish unchanged conditional behaviour for the same respondent strata, nor do they prove the old model heads survived the added retail head. A model could regress sharply on a subgroup while retaining nearly identical aggregate distributions.

**Magnitude, honestly.** This does not prove regression. It proves the advertised regression evidence is insufficient. The unmeasured upper bound is all conditional/head-level degradation that preserves the compared marginals.

**Falsifier.** Persist the validation respondent IDs and evaluate the exact Leg-2 and Leg-3 checkpoints on that same frozen input, reporting the pre-specified per-head differences. A verified row-matched result within the stated bar kills this finding.

**Recommended action.** Reclassify existing REG-1/2 PASS values as proxy/diagnostic, save a versioned validation manifest and checkpoint hashes, and add a real row-matched regression gate. Cost: low for artefact persistence; medium for rerunning inference.

### C-3 — RW6 is severity-vacuous for numeric results

**The evidence.** `_grade_band` is called with `hard=False` (`Step4_docs/3rdJ_04_augmentationGSS_4split_val.py:1293-1297`). Under that condition, an out-of-band non-NaN value returns `warn` even if it is arbitrarily far outside the band (`:1267-1285`). The implementation comments explicitly say no FAIL column applies (`:1268-1275`). Thus, for example, a weekday rate of 0.0000 or 1.0000 becomes WARN, not FAIL. The current canonical report records the 0.0453 weekday value against a 0.06–0.10 target as WARN in every cycle (`.../step4_validation_report.txt:8-19`).

**Why it matters.** This is not a validation gate with a failure mode for numeric target violations; it is a warning reporter. Counting its in-band entries as evidence while making every numeric breach non-blocking conceals whether the physical retail target is a requirement or merely contextual.

**Magnitude, honestly.** The current measured shortfall is 1.47 percentage points (0.0453 versus the 0.0600 lower bound), or 24.5% below that lower bound. The code permits a 100% rate with the same WARN severity, so the gate supplies no finite exclusion bound.

**Falsifier.** Show a project decision, pre-dating the evaluated artefact, that RW6 is intentionally informational/WARN-only and is never presented as a validation PASS in paper or scorecard. Alternatively, make a known extreme fixture produce a blocking result. Either makes the stated criticism inapplicable.

**Recommended action.** Rename RW6 to an informational diagnostic or specify a real FAIL rule before using it as validation evidence. Do not widen the band. Cost: low code/document change; medium if failed results require an explanatory analysis.

### C-4 — rare-retail discrimination is not measured on the delivered generated schedule

**The evidence.** The trainer describes its PR-AUC/F1 as “teacher-forced retail” while its distribution gaps are AR-generated (`Step4_docs/3rdJ_04D_train_4split.py:356-359`); the code calculates the former from observed held-out inputs (`:470-497`). The validator labels RW1/RW2 as teacher-forced values read from the training log (`Step4_docs/3rdJ_04_augmentationGSS_4split_val.py:1149-1157`), while the canonical report gives 0.5190 and 0.3794 (`.../step4_validation_report.txt:100-101`). The same report shows post-hoc raking fidelity (not unassisted model discrimination) at 0.09–0.22 pp by cycle/stratum (`:87-98`). The shipped pool is therefore a generated, projected, and raked artefact, not the teacher-forced prediction used for RW1/RW2.

**Why it matters.** Teacher forcing conditions on the actual preceding sequence and tests reconstruction. The BEM receives free-running outputs after post-processing. Strong teacher-forced PR-AUC/F1 does not establish rare-event detection or calibration for the actual delivered process.

**Magnitude, honestly.** No free-running PR-AUC/F1 is available in the inspected artefacts, so the performance gap is unbounded by this audit. Aggregate controls still show the retail channel is nonzero and its marginal curves are close; this finding is about individual/conditional predictive evidence, not a claim that the retail marginal is wrong.

**Falsifier.** On the persisted held-out IDs, score free-running decoded retail slots against their labels before raking, and report PR-AUC/F1 with the exact deployed thresholds; optionally report the post-rake distribution separately. If both clear the pre-specified bars, this finding is resolved.

**Recommended action.** Split the scorecard into teacher-forced diagnostic, free-running model gate, and post-rake marginal calibration; do not use one in place of another. Cost: medium inference/evaluation run, no training required.

### C-5 — the canonical Step-4 artefact is not reproducibly linked to its claimed model selection

**The evidence.** The canonical directory `Step4_docs/outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/` contains the 418,622,542-byte CSV, HTML/TXT reports and `W3_EFFICACY.txt`, but no model checkpoint or `rake3ch_provenance.json`; its output filename itself identifies only seed 3. The canonical report acknowledges no seed summary and a pending five-seed sweep (`.../step4_validation_report.txt:25`). The validator regards the multi-seed table as optional/secondary (`Step4_docs/3rdJ_04_augmentationGSS_4split_val.py:1938-1953`). The raking program expects to read a winning checkpoint and writes a provenance file (`Step4_docs/3rdJ_04L_joint_rake_4split.py:510-520,820-887`), but that linkage artefact is absent from the canonical directory inspected.

**Why it matters.** A reader cannot establish which checkpoint generated the pool, whether it was selected from multiple seeds, or reproduce the subsequent rake. This blocks an audit of the “model performance” claim even when the final CSV's marginals are good.

**Magnitude, honestly.** This is a reproducibility and evidence failure, not evidence that seed 3 is a bad model. The uncertainty across seeds and checkpoints is unmeasured in the canonical record.

**Falsifier.** Supply a manifest for this exact CSV containing SHA-256 values for input tensors, checkpoint, inference code, rake code/configuration and output, plus a completed candidate-seed score table that identifies seed 3 as the chosen model. Matching hashes and a complete table resolve it.

**Recommended action.** Treat the CSV as non-publishable model evidence until it has an immutable run manifest and seed-selection record. Cost: low if retained artefacts exist; medium/high if the run must be reproduced.

## What is NOT wrong

- The post-projection occupancy mutex is a real, falsifiable check. The canonical report recomputes `0/6,149,856` slots with more than one active home/work/retail channel (`Step4_docs/outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/step4_validation_report.txt:128-129`). A fixture with two active final flags would fail it; Step 7 also aborts on pre-BEM conflicts (`Step7_docs/3rdJ_07_aug_to_bem_4split.py:273-281`).
- Residential injection is not silently routed through the wrong EnergyPlus field in the inspected IDF: the `People` object explicitly references `MXU_Residential_Occ_HH76197` in its Number-of-People schedule field and has an absolute count of four (`Step9_docs/outputs_step9/finding9_verify/Y2022__Tall__MTL/injected.idf:90452-90462`).
- The current Step-8 area artefact closes under its own stated convention. I re-summed the six channel areas in all 56 `agg_meta.csv` rows: zero non-closing cells and a maximum absolute residual of `1.46e-11 m²`; the first SuperTall row records `135857.59426106038 m²` (`Step8_docs/outputs_step8/agg/agg_meta.csv:2`) and Tall records `72623.06993958 m²` (`:4`). This says nothing about external representativeness, but the artefact is internally arithmetically consistent.

## Gate assessment

| Gate examined | Can it fail? | Independent reference? | Quantity survives downstream? | Assessment |
|---|---|---|---|---|
| Step-7 residential schema/range | Yes, for malformed/range/missing-day-type input | No semantic reference to HH maximum | Yes, values are injected | Sound schema guard; does not test claimed household semantics (C-1). |
| ISR final / Step-7 mutex | Yes, any final overlap | Direct final schedule values | Yes, those flags feed schedules | Sound and meaningful. |
| RW1/RW2 PR-AUC/F1 | Yes, on training-log values | Held-out labels, but teacher-forced | No: score is not on deployed free-running/raked schedule | Meaningful reconstruction diagnostic, insufficient delivery gate (C-4). |
| RW6 retail bands | Not for a numeric out-of-band value | Target is external/project specification | Retail schedule survives | WARN-only diagnostic mislabeled/used as a gate (C-3). |
| REG-1/2 old heads | Yes, aggregate synthetic distributions can diverge | Not row-matched and both outputs are synthetic | Only indirectly | Proxy detects gross marginal drift, not claimed checkpoint regression (C-2). |
| Step-8 area closure | Yes, non-closing area arithmetic can fail | Parsed areas / total in artefact | Yes, it is the EUI denominator | Internally sound for the declared area convention. |

## Numbers that did not reconcile

| Quantity | Claimed | Measured / re-derived | Verdict |
|---|---:|---:|---|
| Household aggregation | Per-slot `max(AT_HOME)` in submitted manuscript (`readySubmission.md:211`) | Step-7 uses `mean(hom30)` (`3rdJ_07_aug_to_bem_4split.py:309`); 94,293/785,616 multi-person schedule rows are fractional | Does not reconcile; C-1. |
| Retail weekday target | 0.0600–0.1000 | 0.0453 in each reported cycle (`step4_validation_report.txt:8,11,14,17`) | Below target; WARN, never FAIL (C-3). |
| Retail PR-AUC / F1 | PASS 0.5190 / 0.3794 | Those are teacher-forced training-log values (`3rdJ_04_augmentationGSS_4split_val.py:1149-1157`) | Value reconciles; interpretation does not (C-4). |
| Multi-seed evidence | A selection workflow is implied | Canonical report explicitly says no seed summary (`step4_validation_report.txt:25`) | Not established (C-5). |
| Step-8 gross area closure | Channel areas should sum to total | All 56 rows closed; max residual `1.46e-11 m²` | Reconciles. |

## Open questions I could not settle

- The EnergyPlus magnitude and load-shape consequence of mean-member versus household-max occupancy needs a paired resimulation; no such result was inspected.
- I did not verify raw GSS coding, Census household construction, external hotel series, or cited standards; those claims remain unverified here.
- The actual held-out respondent IDs, the production checkpoint, and model/rake run manifests were unavailable in the canonical Step-4 directory; without them, free-running predictive and exact regression claims cannot be independently calculated.
- I did not inspect every Step-1–9 gate or any large EnergyPlus SQL output, so this report does not certify their correctness.

## Recommended order of work

1. Create and run a small deterministic C-1 fixture/test comparing mean and max aggregation, then reconcile the submitted manuscript with the actual method. **Cost:** hours; highest evidence per effort.
2. Change RW6’s label/severity to match its intended decision role, or add a real pre-specified failure condition. **Cost:** hours.
3. Emit immutable Step-4 manifests: seed table, checkpoint/input/code hashes, decode thresholds and rake provenance. **Cost:** hours if artefacts remain.
4. Run free-running held-out retail PR-AUC/F1 and a row-matched Leg-2/Leg-3 regression comparison using persisted IDs. **Cost:** a moderate local/GPU inference job; no retraining required.
5. Only after steps 1–4, run paired mean-versus-max BEM simulations to bound C-1’s energy effect. **Cost:** substantial simulation time.
