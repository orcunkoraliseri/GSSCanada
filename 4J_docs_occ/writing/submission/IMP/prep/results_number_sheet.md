# Results number sheet (P9)

Built 2026-09-23 by a read-only audit task, copying the shape of the 2J precedent
`2J_docs_occ_nTemp/writing/submission/rejection revision/manuscript/prep/results_number_sheet.md`.
Companion documents checked: `writing/submission/4J_manuscript_submission.md` (MS) and
`writing/submission/4J_supplementary_material.md` (SM). No repository file was edited by this task
except this one (newly created).

This is the "before the rewrite" run named in the improvement plan
(`writing/submission/IMP/4J_improvement_plan_from_2J_lessons_2026-09-22.md`, item P9): "Run before the
rewrite and after it; the two must match except where P3, P5 or P10 add numbers." A second pass is owed
once P3/P5/P10 land.

A prior forensic audit exists at `writing/IMP/RIMP_02_2026-09-14.md` (2026-09-14, Fable). Cross-checking
its findings against the CURRENT manuscript text shows most of its major defects (steering-arm-not-measured
claim, missing Table 3/4 numbering, 2,048- vs 1,280-token window, pre- vs post-rotation chaining numbers,
"four" vs "two" citation-network checks, wrong campaign attribution for the 840 Madrid cells, "three to
nine times the band" vs the table's own 3.3-8.6) have already been repaired in the version read for this
sheet. Where a RIMP-02 finding is confirmed still open, it is folded into the rows below rather than
duplicated.

## SUMMARY

| Status | Rows |
|---|---|
| Total quantitative-claim rows checked | 116 |
| MATCH | 95 |
| ROUNDING | 13 |
| MISMATCH | 8 |
| NO SOURCE FOUND | 0 |

### Every MISMATCH, with the proposed correct value and source

1. **Table 7 peak powers (§5.8, MS:827-833).** MS says Spain 14:00/518 W, Italy 18:00/395 W, Britain
   20:00/422 W. Hours are right; powers are wrong. Primary source `Step9_docs/outputs_step9/agg_diurnal.csv`
   gives Spain 14:00/**502.88 W**, Italy 18:00/**403.52 W**, Britain 20:00/**416.13 W** (rounded 503/404/416,
   matching the project's own secondary check `writing/4thJ_crossStep_analysis.md:107-108`). No file anywhere
   holds 518/395/422 together. **Fix: replace the three power values with 502.9 / 403.5 / 416.1 W** (or the
   rounded 503/404/416 already used in the cross-step analysis and confirmed by a separate agent trace to
   equal Table 7's caption cross-check in RIMP-02, D.6).
2. **Observed-stock cell counts (§4.4, §7.10, SM S4).** MS says 35,290 cells total (Madrid 11,510 / Bologna
   11,710 / London 12,070). The campaign's own FINAL scored progress-log entry
   (`Step10_docs/4thJ_10_nocoreRealStock_val.md:128`, dated 2026-09-16, "THE SUITE IS SCORED IN FULL") gives
   **35,090 real completed cells (es/Madrid 11,340 / uk/London 12,070 / it/Bologna 11,680)**. The manuscript's
   35,290/11,510/11,710 figures trace instead to an earlier 2026-09-08 PREFLIGHT/planned document
   (`Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:1591,1822`, and `Prompts/RESUME.md:85`),
   which was never updated to the campaign's final count. London (12,070) happens to be identical in both.
   **Fix: use 35,090 (Madrid 11,340 / Bologna 11,680 / London 12,070)** everywhere the total or per-district
   split is quoted, or state explicitly that the number is a planned/preflight figure if that is what is meant.
3. **Training wall time (§3.3 MS:287-288, SM:147).** "Wall time is approximately ten to twelve hours per
   fold." Spain 11:00:05 and Britain 10:04:33 are inside that range
   (`Step4_docs/outputs_step4/proglog_step4_gates.md:3270` and `Step4_docs/investigation/2026-08-23_G4.1_G4.3_G4.6_G4.12_four_gates_never_passed.md:488-489`),
   but Italy measured **07:28:06** (`...four_gates_never_passed.md:370`), below the stated floor. **Fix: state
   the true range, "approximately 7.5 to 11 hours per fold," or report per-fold wall times.**
4. **Fictional-country amplitude noise floor (§5.4, MS:741-745).** "A sampling-noise probe ... returns a
   seed-alone spread of 0.529, 0.658 and 0.385 on the within-stratum variance ratio, which is wider than the
   entire 0.45-wide acceptance band" — stated for all three folds. Source
   (`Step4_docs/outputs_step4/proglog_step4_gates.md:3334-3344`) only supports this for Spain (0.529) and
   Britain (0.658); Italy's 0.385 is narrower than the 0.45 band, and the source text itself limits the "wider
   than the band" statement to es/uk. **Fix: "wider than the band in Spain and Britain (0.529, 0.658); narrower
   in Italy (0.385)."**
5. **Unconstrained-generation batch size (§3.5/§4.2, SM S4).** "5,200 unconstrained diaries per fold" was true
   when generated (`Step7_docs/4thJ_07_constrainedGeneration.md:1717-1721`, verified by line count at the
   time), but the on-disk files `generated_leg5_{es,uk,it}_nogrammar.jsonl` were later overwritten by a larger
   rejection-sampling batch for a different gate (75,531/16,795/48,809 lines now), with no backup of the
   original 5,200-line files retained. The claim is not currently reproducible from the primary artefact.
   **Fix: either restore/label a frozen 5,200-line snapshot for the decoding-neutrality comparison, or state in
   the text that the on-disk unconstrained batch has since been superseded for a later gate and point to where
   the original count was verified (dated impl entry above).**

None of the ten mismatches change the headline result (the transfer bar is not met, 1.1-3.9x, nine of nine
cells) — that number and its underlying Table 3 are a clean MATCH to the primary source.

---

## R1 — Abstract, Highlights, headline claims

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| HDR-1 | "misses ... by factors of 1.1 to 3.9" (Abstract, Highlights, §1.5, §5.1, §6.1, §6.7, §8) | 1.1-3.9 | `Step6_docs/outputs_step6/g61_leg5_scored.json` (model_mae/null_mae per cell, recomputed) | min 1.1461 (uk Y_GE65), max 3.9119 (es Y45-64) | MATCH |
| HDR-2 | "closest miss 2.70 minutes per day" | 2.70 | `g61_leg5_scored.json` .folds.uk.bands["Y_GE65"].margin | -2.698 | ROUNDING |
| HDR-3 | "73,254 diaries, 2,024,068 episodes" (Abstract) | as stated | `Step2_docs/4thJ_02_harmonisation.md:1360-1366,1720,1946` | identical | MATCH |
| HDR-4 | "1.5 to 7.3 billion parameters" / "4.7-fold larger backbone moves mean absolute error from 42.05 to 43.14" (Abstract) | 42.05->43.14, 4.7x | `Step6_docs/4thJ_06_transfer.md:2898,2972` | identical; note 7.30/1.48=4.93, not 4.7 (source's own rounding, inherited) | MATCH (to source) |
| HDR-5 | "training all 7,377,965,056 parameters instead of the adapter's 79,953,920" | as stated | `Step4_docs/outputs_step4/proglog_step4_gates.md:3468-3478` | identical | MATCH |
| HDR-6 | "pooled slopes of 0.40 to 0.53 against a floor of 0.80" (Abstract, Highlights) | 0.40-0.53 | `Step6_docs/outputs_step6/g67_leg5_{es,uk,it}.json` pooled_slope | 0.4153/0.5329/0.4049 | MATCH |
| HDR-7 | "steering arm ... R-squared 0.99 in every fold" (Abstract) | 0.99 | same files, `r2` | 0.9897/0.9914/0.9941 | ROUNDING |
| HDR-8 | "peak six hours apart, at 14:00 in Spain, 18:00 in Italy and 20:00 in Britain" (Abstract, §5.8, §6.5, §8) | hours only | `Step9_docs/outputs_step9/agg_diurnal.csv` | 14:00/18:00/20:00 confirmed; POWERS attached to this claim (Table 7) are a separate mismatch, see summary #1 | MATCH (hours only) |
| HDR-9 | "92x trainable parameters" (Highlights) | 92x | 79,953,920 -> 7,377,965,056 | 7,377,965,056/79,953,920 = 92.31 | MATCH |
| HDR-10 | "at most 85 characters" is a style rule, not a number claim — skipped | -- | -- | -- | n/a |

## R2 — Table 3 (§5.1): time-budget MAE, nine cells

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| TB3-1 | Spain Y25-44 model/null/margin | 36.81/9.94/-26.9 | `g61_leg5_scored.json` .folds.es.bands["Y25-44"] | 36.8132/9.9348/-26.8784 | ROUNDING |
| TB3-2 | Spain Y45-64 | 34.52/8.82/-25.7 | .folds.es.bands["Y45-64"] | 34.5182/8.8238/-25.6944 | ROUNDING |
| TB3-3 | Spain Y_GE65 | 44.32/11.81/-32.5 | .folds.es.bands["Y_GE65"] | 44.3204/11.8136/-32.5068 | ROUNDING |
| TB3-4 | Britain Y25-44 | 58.91/21.79/-37.1 | .folds.uk.bands["Y25-44"] | 58.9046/21.7916/-37.113 | ROUNDING |
| TB3-5 | Britain Y45-64 | 60.44/19.21/-41.2 | .folds.uk.bands["Y45-64"] | 60.4441/19.2128/-41.2313 | ROUNDING |
| TB3-6 | Britain Y_GE65 | 21.24/18.54/-2.70 | .folds.uk.bands["Y_GE65"] | 21.2357/18.5377/-2.698 | ROUNDING |
| TB3-7 | Italy Y25-44 | 62.24/19.51/-42.7 | .folds.it.bands["Y25-44"] | 62.2415/19.5076/-42.7338 | ROUNDING |
| TB3-8 | Italy Y45-64 | 33.95/13.85/-20.1 | .folds.it.bands["Y45-64"] | 33.9465/13.8522/-20.0943 | ROUNDING |
| TB3-9 | Italy Y_GE65 | 35.84/15.51/-20.3 | .folds.it.bands["Y_GE65"] | 35.8421/15.507/-20.335 | ROUNDING |
| TB3-10 | "by factors of 2.3 to 3.9 in eight of the nine cells and by a factor of 1.15 in the ninth" | 2.3-3.9, 1.15 | recomputed model_mae/null_mae | eight cells 2.3114-3.9119; ninth (uk Y_GE65) 1.1461 | MATCH |
| TB3-11 | "already about five times worse ... between three and four times worse again" (MS:632-633) | ~5x, 3-4x | recomputed: own-corpus MAE (T6 below) vs null MAE ~4.4-6.4x; null vs model 1.15-3.9x per TB3-10 | Overstates the low end: the model-vs-null ratio spans 1.15-3.9x, not uniformly "three to four" | ROUNDING/imprecise but not a hard MISMATCH — see note |
| TB3-12 | "Measured, it is the weakest of the three [nulls] in six of nine cells" | 6/9 | `Step6_docs/outputs_step6/g62_g63_leg5_scored.json` vs Table 3 raked values (recomputed ordering) | reverses in ES Y25-44, IT Y25-44, IT Y_GE65, UK all three = 6/9 | MATCH |

Note on TB3-11: the sentence is a descriptive gloss, not a table entry; recomputing the model/null ratio
gives 1.15-3.9x, so "between three and four times worse again" undersells the low end (closest miss is
only 1.15x, not 3x). Not counted in the MISMATCH tally because it is prose commentary rather than a
distinct sourced number, but flagged for the rewrite (P9 second pass).

## R3 — Table 4 (§5.2) and the transfer design (§3.5, §3.6, §4.1-4.3)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| T1a | Budget agreement FAIL | 9/9 | `g64_leg5_generated.json` board.FAIL | 9 | MATCH |
| T1b | Frozen limitation criteria FAIL | 9/9 | `g65_g69_leg5.json:4` | 9 | MATCH |
| T1c | Held-in regression FAIL | 6/6 | `g66_leg5_generated.json` board.FAIL | 6 | MATCH |
| T1d | Fictional country FAIL | 3/3 | `g67_leg5_{es,uk,it}.json:68` | 3/3 | MATCH |
| T1e | Joint structure FAIL, all folds/bases | FAIL all | `g68_model_leg5_*_{none,weight_dia_cal}.json` | 6/6 false | MATCH |
| T1f | Country discrimination FAIL | 9/9 | `g65_g69_leg5.json:5` | 9 | MATCH |
| T2 | Held-in regression corrected: pilot 5/6 -> reported 2/6; real-corpus arm 3/3 | 5/6->2/6, 3/3 | `g66_leg4_generated.json` (pilot clause2), `g66_corpus_calibration.json` | 2/6 (leg5); 3/3 | MATCH |
| T3 | Italy youngest band discrimination margin | -0.4555 | `g65_g69_corpus_calibration.json:527` | -0.45549729 | MATCH |
| T4 | 5,200 unconstrained diaries per fold | 5,200 | `Step7_docs/outputs_step7/generated_leg5_*_nogrammar.jsonl` | true at generation time; files since overwritten (75,531/16,795/48,809 lines) | MISMATCH (provenance, see summary #5) |
| T5 | Single-donor-country populations, six in all | 6 | `Step6_docs/outputs_step6/secondary_nulls.json` | 6 objects | MATCH |
| T6 | Spain's own real corpus errors "1.86 to 2.00 minutes per day" | 1.86-2.00 | `g65_g69_corpus_calibration.json` es mae | Y_GE65 1.8603, Y45-64 1.9361, Y25-44 1.9962 | MATCH |
| T7 | Markov comparator: 0.264 vs band 1.50; dwell 119.6 vs band 10.0 | 0.264/119.6 | `Step6_docs/outputs_step6/markov_comparator_it.json:8,10` | transitions_abs_err 0.26411; dwell_w1_max 119.5645 | MATCH (119.6 is ROUNDING of 119.5645) |
| T8 | "Hour-support constancy" built, self-tested, never scored on model output | as stated | `Step6_docs/4thJ_06_transfer_val.md:85-120` (G6.14) | self-tested 9/9, never applied to model output | MATCH |
| T9 | Generation: 5,200 constrained per fold | 5,200 | `Step7_docs/outputs_step7/generated_leg5_*_constrained.jsonl` (wc -l) | 5,200 each | MATCH |
| T10 | 3,600 held-in (600x6) | 3,600 | `Step7_docs/outputs_step7/generated_leg5_*_g66{es,it,uk}.jsonl` (wc -l) | 600x6=3,600 | MATCH |
| T11 | 9,000 fictional-country (600x5x3) | 9,000 | `Step7_docs/outputs_step7/generated_leg5_*_g67t0{0-4}.jsonl` (wc -l) | 600x15=9,000 | MATCH |
| T12 | "durations ... running total takes exactly 145 distinct values" | 145 | `Step7_docs/4thJ_07_constrainedGeneration.md:45` | 145 (0..1440 step 10) | MATCH |
| T13 | Day-chaining: peak moves 0.028-0.289% vs 25% trigger (§3.6, §6.5, §7.5) | 0.028-0.289% | `Step8_docs/outputs_step8/chaining_step8.json` G7.18 measured_peak_spread_pct (post-rotation, re-measured) | 0.0285/0.1936/0.2892 | MATCH (0.0285 rounds to 0.028) |

## R4 — Datasets and Harmonisation (§2, §3.1)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| D1 | Table 2 diaries/episodes: ES 19,295/430,754; UK 16,533/587,632; IT 41,229/1,077,657 | as stated | `Step1_docs/outputs_step1/parse_report_{spain,uk,italy}.txt` | identical | MATCH |
| D2 | "8,259 of 8,274 gave both" (UK diary days) | 8,259/8,274 | `Step1_docs/outputs_step1/parse_report_uk.txt` | 8,259 gave 2, 15 gave 1; 8,259+15=8,274 | MATCH |
| D3 | Harmonisation totals: 2,024,068 episodes / 73,254 diaries, down from 2,096,043 / 77,057 | as stated | `Step2_docs/4thJ_02_harmonisation.md:1360-1366,1720,1946`, `_val.md:777-783` | identical; 2,096,043-90,890+18,915=2,024,068 | MATCH |
| D4 | "90,890 removed below age-11 floor, net of 18,915 splits" | 90,890/18,915 | same lines | identical (doc notes a x2 row-flag subtlety, does not change the reported figures) | MATCH |
| D5 | "eighteen registered checks, seventeen scored, sixteen passed" | 18/17/16 | `Step2_docs/outputs_step2/proglog_step2_gates18.md:28` | "17 scored (G2.10 excluded), 16 PASS, 1 FAIL" | MATCH |
| D6 | SM S1.1 Acquisition: "Spain 15 PASS; Italy 1 FAIL; Britain 1 FAIL" of 16 | as stated | `Step1_docs/4thJ_01_corpusAcquisition.md:972,976,1121-1130` (final merged state) | Spain 15/15; Italy 12/1 FAIL; UK 13/1 FAIL | MATCH (only the final merged-manifest round matches; superseded early per-country gate_report txts show 2 FAILs each — flag for anyone re-deriving from the wrong snapshot) |
| D7 | Token lengths 256/632/1178 vs band 300/700/1200 | as stated | `Step3_docs/4thJ_03_serialisation_val.md:588,967` | 256.0/632.0/1178 exact | MATCH |
| D8 | "1,280-token training window" | 1,280 | `Step4_docs/outputs_step4/leg5_ceiling_fold_es/run_manifest_leg5_ceiling_fold_es.json` max_len | 1280 | MATCH |
| D9 | "All 73,254 diaries serialise, no rows/diaries dropped" | as stated | `Step3_docs/4thJ_03_serialisation.md:392-394` | "73,254/73,254 exact, 0 dropped" | MATCH |
| D10 | "Nineteen of twenty registered checks pass at baseline ... 21 perturbations felled the check they named" | 19/20, 21/21 | `Step3_docs/4thJ_03_serialisation_val.md:10,761-762,977` | identical | MATCH |
| D11 | "551 British diaries ... household type ... unknown"; "3.48 per cent of that fold" (§3.2, §7.3) | 551, 3.48% | `Step3_docs/4thJ_03_serialisation_val.md:1079,1090` | 551/15,854 = 3.4753% (source states "3.5%" to 1dp) | ROUNDING (3.475% -> 3.48 vs source's own 3.5) |
| D12 | "dropping the cell moves whole-fold mean absolute error by 0.158 minutes per day" (§7.3) | 0.158 | `Step6_docs/4thJ_06_transfer.md:3629` / `Step6_docs/impl/2026-08-26_g68-...md:188` | +0.158 min/day | MATCH |
| D13 | Age floors: Spain 10, Britain 8, Italy 3 (proxy 3-10) | as stated | `Step1_docs/outputs_step1/codebook_facts_{italy,uk}.md` | UK "8"; Italy "3 ... proxy 3-10" | MATCH |
| D14 | "158 three-digit activity codes, four location classes, six co-presence flags" (§3.1) | 158/4/6 | `Step2_docs/4thJ_02_harmonisation.md:1173`; `crosswalk_location.csv` (4 classes); `crosswalk_copresence.csv` (6 flags) | 158/4/6 | MATCH |
| D15 | "reduced to these six fields from an original nine" (§3.2) | 6 from 9 | `Step3_docs/4thJ_03_serialisation.md:372-373,557-558` | season dropped (D-S2-19), then mode+scheme dropped (D-S3-11): 9->8->6 | MATCH |
| D16 | "only Y25-44, Y45-64, Y_GE65 usable" (3 of 8 age bands) (§2.2) | 3/8 | `Step5_docs/4thJ_05_populationLinkage.md:372,475` | consistent (2 of 8 bands must be assigned rather than fitted) | MATCH |
| D17 | "44 candidates" weather stations; "5 to 11 per cent of heating demand"; "two thousandths of a kelvin" (§2.3, §3.7) | 44, 5-11%, 0.002K | `Step8_docs/docs/2026-08-25_D-S8-4_weather-basis-and-station-selection.md:127-138,183,269` | 44 candidates; 5-11%; UK margin 0.002K | MATCH |

## R5 — Model, training and populations (§3.3, §3.4, SM S1.2-S1.3, S2, S3)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| M1 | Backbones: 7.30B reported, 1.48B pilot, 7B comparison family | as stated | `Step4_docs/4thJ_04_finetuneLLM.md:37-38` | identical | MATCH |
| M2 | Adapter: rank 32, alpha 64, dropout 0.05, rsLoRA, 7 target modules, 79,953,920 params, 1.0837% | as stated | `tools/4thJ_step4_thresholds.py:93-98`; `proglog_step4_gates.md:3471` | identical | MATCH |
| M3 | Full fine-tune parameter count 7,377,965,056 | as stated | `leg5_ceiling_fold_es/run_manifest...CORRECTION.json`; `proglog:3471` | identical | MATCH |
| M4 | Training config: 3 epochs, lr 1e-4, batch 2, grad_accum 8, seq_len 1280, bf16, AdamW, 1 seed, 1 A100 | as stated | `run_manifest_leg5_ceiling_fold_es.json` | identical | MATCH |
| M5 | "Wall time approximately ten to twelve hours per fold" | 10-12h | `proglog_step4_gates.md:3270`; `Step4_docs/investigation/2026-08-23_...four_gates_never_passed.md:370,488-489` | es 11:00:05, uk 10:04:33, **it 07:28:06** | MISMATCH (Italy below range, see summary #3) |
| M6 | "100,000 persons"; IPF "below 1e-13" | 100,000 / 1e-13 | `tools/4thJ_step5_synthesise.py:209,223`; population CSVs (100,000 rows each) | identical | MATCH |
| M7 | "Spain's population is fitted on five of the seven economic-status categories" | 5/7 | `Step5_docs/4thJ_05_populationLinkage.md:1069,1442,922-957` | homemaker folded into other_inactive | MATCH |
| M8 | Temperatures 1.30/1.10/1.20 (es/uk/it) | as stated | `Step5_docs/outputs_step5/temperature_calibration.md` T_chosen | 1.30/1.10/1.20 | MATCH |
| M9 | "34 of 36 gate-fold verdicts pass"; FAIL Spain 0.51, Britain 0.99, PASS Italy 1.29 | 34/36; 0.51/0.99/1.29 | `Step5_docs/outputs_step5/temperature_calibration.md:480,488-494` | identical | MATCH |
| M10 | SM S1.2: variance-ratio FAIL 3/3; shuffled-prefix CE FAIL 7/7, 0.068-0.106; merge drift FAIL 4/4, 3.2e-4 to 7.3e-4; within-stratum shuffle 0.002-0.0069, 55-64% unchanged | as stated | `Step4_docs/investigation/2026-08-23_...four_gates_never_passed.md` (multiple line refs); `proglog_step4_gates.md` | all values reproduce exactly | MATCH |
| M11 | S1.6: seed-alone spread 0.529/0.658/0.385 | as stated | `proglog_step4_gates.md:3338-3340,3522` | identical (same source as HDR/P6 below) | MATCH |
| M12 | S1.6: "84 to 1,062 times the untrained baseline's conditioning response" | 84x-1062x | `...four_gates_never_passed.md:313-326,513` | leg4-es 84x, leg5-es 1062x (same-run pairs, not a naive cross min/max) | MATCH |
| M13 | S1.6: "merged/unmerged differ in 39 to 46 of 48 cases, 81 to 96 per cent" | 39-46/48 | `...four_gates_never_passed.md:344-347` | 39/48=81.25%, 46/48=95.8% | MATCH |
| M14 | Table 5 row 2: training loss "0.508305 against 0.513494 at epoch 2" | as stated | `proglog_step4_gates.md:3468-3470` | identical | MATCH |
| M15 | Table 5 row 3: alternative family "24 per cent more wall time, 16 per cent more memory" | 24%/16% | `Step4_docs/4thJ_04_finetuneLLM.md:542,557` | VRAM 19.98->23.14 GiB (+15.8%~16%, OK); wall 37,211->45,339s (+21.8%, not 24% — source's own inherited rounding) | MATCH (to source's stated text; source's own arithmetic gives 21.8%, flagged) |
| M16 | S3 prefix: country 3, age 8, sex 2, hh-type 6/5-raked, econ 7/5-raked(ES), day-type 3, exogenous 5/7,1/7,1/7 | as stated | `Step5_docs/outputs_step5/marginals_es.csv`; `Step5_docs/4thJ_05_populationLinkage.md:147,1344` | identical | MATCH |
| M17 | phi_int reference internal gain = 3.0 W/m² in every fold (§3.7) | 3.0 | `Step8_docs/4thJ_08_bemSimulation.md:468,536,559,1452`; `tools/4thJ_step8_injected.py:437` | 3.0 W/m² throughout | MATCH |
| M18 | f-level sweep {0.00, 0.15, 0.30, 0.50, 1.00} (§3.7) | as stated | `tools/4thJ_step8_aggregate.py:74` PREREG_GRID; `tools/4thJ_step8_injected.py:13` | identical | MATCH |

## R6 — Capacity, amplitude and privacy (§5.3, §5.4, §5.6, SM S1.5-S1.6)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| P1 | Table 5 row 1: 1.48B->7.30B (4.7x), mean error 42.05->43.14, 4 better/5 worse | as stated | `Step6_docs/4thJ_06_transfer.md:2898,2972` | identical (source's own "4.7x" vs a recomputed 4.93x — inherited, not introduced by MS) | MATCH |
| P2 | §5.4 pilot 1.48B: direction R2 0.8455/0.9808/0.9836; amplitude 0.2666/0.4612/0.3785 | as stated | `Step6_docs/4thJ_06_transfer.md:2539-2541` | identical | MATCH |
| P3 | §5.4 reported 7B: direction R2 0.9897/0.9914/0.9941; amplitude 0.4153/0.5329/0.4049 | as stated | `Step6_docs/outputs_step6/g67_leg5_{es,uk,it}.json` r2/pooled_slope | identical | MATCH |
| P4 | §5.4: "seed-alone spread ... wider than the entire 0.45-wide acceptance band" (all three folds) | wider (all 3) | `proglog_step4_gates.md:3334-3344` | es 0.529, uk 0.658 (both wider); it 0.385 (NARROWER than 0.45) | MISMATCH (see summary #4) |
| P5 | §5.6: MIA AUC 0.6645/ceiling 0.65, z=1.70; untuned floor 0.4886; reference-based 0.5594/0.75; prefix extraction 0/103 | as stated | `Step6_docs/outputs_step6/privacy_audit.md:19,59-65,105`; `privacy_mia_leg5_it.json`; `4J_step6_mia_1286976.out:101-106` | identical | MATCH |
| P6 | §5.6: distance-to-closest-record: PASS Spain/Italy, FAIL Britain (0.4236 vs [0.4028,0.4167]) | as stated | `Step6_docs/outputs_step6/g613_leg5_dcr.json` uk block | verbatim | MATCH |
| P7 | §5.6: perplexity gap 0.0570/0.05 ceiling; permuted-adapter 0.0511; memorisation ceiling 0.6496, -0.0149 headroom, +0.102 with capacity | as stated | `privacy_mia_leg5_it.json`; `privacy_audit.md:106,115-116,121,154` | identical | MATCH |
| P8 | SM S1.5 table (restates P5-P7) | as stated | `privacy_audit.md` sections 2,4,8 | identical | MATCH |

## R7 — Joint structure, constrained decoding, appliance mapping (§3.6, §3.9, §5.5, §5.7, §5.9)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| J1 | Table 6 dwell-time Wasserstein: band 10.0, 50.13-66.57, x5.0-6.7 | as stated | `Step6_docs/outputs_step6/g68_model_leg5_{es,it,uk}_{none,weight_dia_cal}.json` summary.dwell_w1_max | min 50.1299 (it), max 66.5661 (uk) | MATCH |
| J2 | Table 6 transition TV: band 0.050, 0.1623-0.2344, x3.3-4.7 | as stated | same files, summary.transition_tvd | min 0.16228 (uk), max 0.23439 (it) | MATCH |
| J3 | Table 6 diurnal JSD: band 0.015, 0.0690-0.1189, x4.6-7.9 | as stated | same files, summary.diurnal_jsd_mean | min 0.06899 (es), max 0.11886 (it) | MATCH |
| J4 | Table 6 time-budget: band 8.0, 38.26-68.67, x4.8-8.6 | as stated | same files, summary.budget_err_max_min | min 38.2597 (it), max 68.6685 (es) | MATCH |
| J5 | "all four miss their band in every fold, at between 3.3 and 8.6 times the band" (§5.5, Fig.5) | 3.3-8.6 | recomputed from J1-J4 | 3.3 (J2 min) to 8.6 (J4 max) | MATCH |
| J6 | "a second real Italian sample misses 65 of 68 attribute-pair cells" | 65/68 | `Step6_docs/4thJ_06_transfer_val.md:44,330` | verbatim | MATCH |
| J7 | Markov comparator (also T7 above): 0.264/1.50; 119.6/10.0 | 0.264/119.6 | `markov_comparator_it.json:8,10` | identical | MATCH |
| J8 | §5.7: unmasked validity 6.88%/30.96%/10.65% vs 99.90% requirement | as stated | `Step7_docs/4thJ_07_constrainedGeneration.md:1730,1823-1825` | 358/1610/554 of 5,200 | MATCH |
| J9 | §5.7: "Between 69 and 93 per cent ... required the mask to intervene" | 69-93% | `Step7_docs/outputs_step7/firing_rate_by_stratum_summary.json` population_firing_rate | es 93.16%, uk 69.84%, it 89.62% | MATCH |
| J10 | §5.7: 5,169/5,066/5,065 valid of 5,200; worst stratum -101.02/-29.60/-48.87 vs +-5.0 | as stated | `Step7_docs/4thJ_07_constrainedGeneration_val.md:347,349` | identical | MATCH |
| J11 | §3.9: mapping 192 rows/141 codes, 43 validated, 54 electricity, 7 hot-water, 131 no-load | as stated | `Step9_docs/outputs_step9/mapping_provenance.md:50-58` | identical (43 is of the 192 rows, not of the 141 codes — MS phrasing is ambiguous but not wrong) | MATCH |
| J12 | §3.9: secondary activity 29.816%/26.308%/29 codes | as stated | `Step9_docs/4thJ_09_enduseLoads.md:100,669` | identical | MATCH |
| J13 | §5.9: laundry minutes 2,462/1,589/781 vs 27,036; ratios 0.776/0.179/0.092; R2 0.2967/0.4106/0.0346 vs 0.85 | as stated | `Step9_docs/4thJ_09_enduseLoads.md:707-708,773` | identical | MATCH |
| J14 | §5.9 stock scale: 7,602 London/29,902 Bologna; R2 0.4347/0.0781; "77 per cent laundry at 11:00"; suppression 80-90% | as stated | `Step11_docs/4thJ_11_stockEndUseLoads.md:70-71,335,337,787-799`; `outputs_step11/g11_6_18/gates_step11_full.json` | identical | MATCH |
| J15 | Table 7 (§5.8): Spain peak hour/power | 14:00 / 518 W | `Step9_docs/outputs_step9/agg_diurnal.csv` fold=es, max elec_w_per_dwelling | hour 14.0 / 502.8777 W | MISMATCH (hour right, power +15.1 W / +3.0%) |
| J16 | Table 7: Italy peak hour/power | 18:00 / 395 W | `agg_diurnal.csv` fold=it | hour 18.0 / 403.5225 W | MISMATCH (hour right, power -8.5 W / -2.1%) |
| J17 | Table 7: Britain peak hour/power | 20:00 / 422 W | `agg_diurnal.csv` fold=uk | hour 20.0 / 416.1349 W | MISMATCH (hour right, power +5.9 W / +1.4%) |

No file on disk holds 518/395/422 together; the project's own secondary check
(`writing/4thJ_crossStep_analysis.md:107-108`) gives the correctly rounded 503/404/416 W instead. See
summary item 1.

## R8 — BEM, heating, hot water, stock (§2.3, §2.4, §3.7, §3.8, §4.3, §4.4, §5.10, §5.11, SM S4)

| ID | Manuscript quote | MS value | Source | Source value | Status |
|---|---|---|---|---|---|
| B1 | "88 archetypes: 24 Spain, 32 Britain, 32 Italy" | 88=24+32+32 | `Step8_docs/outputs_step8/archetype_idf_manifest.csv` | es 24, uk 32, it 32 | MATCH |
| B2 | "13,108 simulations ... applied occupancy four hours early ... all 13,108 re-executed" (§3.8) | 13,108 | `Step8_docs/4thJ_08_bemSimulation.md` FINDING 141 entry | "all 13,108 runs above ... RE-RUN" | MATCH |
| B3 | SM S4 composition: 4,048 + 9,000 + 60 = 13,108 | as stated | `4thJ_08_bemSimulation.md` (440 scenario-cells/4,048 runs); `chaining_step8.json` (3x6x5x100=9,000); `calendar_probe_step8.json` (3x(10+10)=60) | 4,048+9,000+60=13,108 | MATCH |
| B4 | "the multiplier had been written to six decimal places ... within four parts in ten million" (§3.7) | %.6f, 4e-7 | `4thJ_08_bemSimulation.md:209` FINDING 132 | "false by 4.01e-07 relative" | MATCH |
| B5 | Table 8: peak +2.7145/+0.0393/-0.6332; spread 4.9837/2.3797/1.5959; ratio 0.54/0.02/0.40; annual median -1.5100/-0.3605/-0.4178 | as stated | `Step8_docs/outputs_step8/agg_by_fold.csv` f=1.00 rows; `4thJ_08_bemSimulation.md:239,1568` | identical | MATCH |
| B6 | "apartment buildings largest everywhere at +3.46, +1.04 and +0.50 per cent" | 3.46/1.04/0.50 | `Step8_docs/outputs_step8/agg_by_class.csv` cls=AB, f=1.00 | 3.4617/1.0421/0.5002 | ROUNDING |
| B7 | "hourly peak by up to 7.92 per cent and the peak hour by up to 41 hours" (core-era 410-cell campaign) | 7.92%/41h | `Step10_docs/impl/2026-08-28_EU-09-EU-10-scored-over-the-149.md:141-146` FINDING 184 | it hourly peak +7.92%; peak-hour shift up to 41h | MATCH (figures trace to the 149-cell certified subset of the 410-cell record, not a fresh re-derivation over all 410 — same basis the manuscript already uses for that campaign) |
| B8 | "+136.6% Spain, -29.6% Britain, -36.7% Italy"; "539-hour ... 2,901 hours" (§5.11) | as stated | `Step8_docs/4thJ_08_bemSimulation.md:1276,1287-1288` FINDING 121 | identical | MATCH |
| B9 | §5.10: hot-water 100.16/117.65/91.06 L/person/day vs band 30-50 | as stated | `Step9_docs/4thJ_09_enduseLoads_val.md:226` G9.7 | identical | MATCH |
| B10 | §5.10: "reduces to 200 divided by household size, within 0.0005 over all 300 rows" | as stated | `Step9_docs/4thJ_09_enduseLoads.md:701` | identical | MATCH |
| B11 | §5.10: replacement check passes 200.79/201.01/199.47; stock 202.41/200.35; doubled-draw ~401 | as stated | `Step9_docs/4thJ_09_enduseLoads_val.md:227` G9.15; `Step11_docs/4thJ_11_stockEndUseLoads.md:815` G11.18 | 200.79/201.01/199.47; uk 202.41, it 200.35; doubled draws 401.58/402.03/398.93 | MATCH |
| B12 | §3.9 Jordan & Vajen model: 1/6/140/40 L, portions 0.14/0.36/0.10/0.40, sum 200.0 | as stated | `Step9_docs/docs/2026-08-25_items-9.1-9.5_the-mapping-the-trigger-and-the-campaign.md:118` | identical | MATCH |
| B13 | §4.4: 7,602 flats/1,200 London buildings; 29,902 flats/1,126 Bologna buildings; 49 excluded | as stated | `Step11_docs/4thJ_11_stockEndUseLoads.md:768-772` | identical (42 IT + 7 UK = 49) | MATCH |
| B14 | §2.4: "3,529 buildings, 31,591 dwellings" (three-district total) | 3,529/31,591 | `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:1573,1591` | identical | MATCH (this is the same 2026-09-08 preflight source that also carries the now-superseded 35,290 cell total — see summary #2) |
| B15a | Total observed-stock cells (§4.4, §7.10, SM S4) | 35,290 | `Step10_docs/4thJ_10_nocoreRealStock_val.md:128` (final, 2026-09-16) | 35,090 completed | MISMATCH (+200; see summary #2) |
| B15b | Cell counts by district (Madrid/Bologna/London) | 11,510/11,710/12,070 | `Prompts/RESUME.md:85`; `writing/IMP/SCOPE_madrid_stock_run_2026-09-14.md` (planned) vs `Step10_docs/4thJ_10_nocoreRealStock_val.md:128` (final) | planned 11,510/11,710/12,070; final completed 11,340/12,070/11,680 | MISMATCH (Madrid +170, Bologna +30, London exact) |
| B16 | "840 cells that did not complete, across 84 buildings in Madrid" (§7.10), now correctly attributed to the LARGER (35,290/35,090) campaign | 840/84 | `Step10_docs/impl/C2_ES_failure_progress_log.csv` | 84 distinct building_id rows, sum(n_failed_cells)=840 | MATCH (exact; also confirms the RIMP-02 2026-09-14 finding that this used to be mis-attributed to the smaller 410-cell campaign has since been fixed) |
| B17 | "410 cells" earlier core-era campaign (§4.4, §5.11, SM S4) | 410 | `Step10_docs/outputs_step10/realstock_campaign/campaign_summary.json` | n_cells 410, n_buildings 41 | MATCH |

---

## Notes for the rewrite (P9 second pass, after P3/P5/P10)

- Fix the five MISMATCH items in the summary above; re-run this sheet afterward and diff it against this
  version, per the improvement plan's own instruction that "the two must match except where P3, P5 or P10
  add numbers."
- TB3-11 (the "three to four times worse again" gloss) is imprecise rather than wrong; tighten the wording
  or drop the specific multiplier since Table 3 already carries the exact range.
- Where this sheet notes "MATCH to source's stated text" with a flagged internal arithmetic inconsistency in
  that source (HDR-4/M15's 4.7x/24% figures), the manuscript is not at fault, but a rewrite pass could quote
  the recomputed figures (4.93x, 21.8%) instead, or note the discrepancy is inherited.
- D6's caveat (superseded early per-country gate-report snapshots) is a note for future audits, not a
  manuscript defect: the manuscript's own numbers already match the correct, final source.
