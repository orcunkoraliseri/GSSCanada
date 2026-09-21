# T91 — find the two Introduction counts — implementation state

Task doc:   this file. Plan log (em).
Status:     DONE
Agent:      fresh Sonnet employee. Local reading and grep only. Cluster: `ls`, `wc -l`, `cat` of small
            files ONLY on the login node (no python, no loops over big trees; sbatch only if you must
            count, then end the turn with the JobID written here). No web.

## Goal
Manuscript Section 1.5 (`../manuscript/2J_manuscript_AE_revised.md`, lines ~158 and ~162) has two
`[NUMBER FROM RESULTS]` placeholders:
1. "([N] architectures searched)": how many generative-model architectures were compared in the
   architecture search that chose the final model.
2. "(50 households per panel, [N] simulation runs)": the total number of building energy simulations
   behind the results REPORTED in this paper (the rebuilt 2022 and 2030 runs and the arms the Results
   actually use), not every run ever made.

## Where to look
- (1): the architecture search record. Start at `C:\Users\o_iseri\.claude\projects\C--Users-o-iseri-Desktop-GSSCanada\memory\` files named `project_step4_*` in `archive/`, `feedback_step4_ml.md`, and the step-4 working doc `step4_training_v4.md` it names; also the SI (`../manuscript/2J_SI_AE_revised.md`) model-card section. Count only architectures actually trained and scored, and say which list you counted.
- (2): `2026-09-21_T79_wp10_results_number_sheet.md`, `../manuscript/prep/results_number_sheet.md`, `2026-09-15_T26_wp2_scenario_builds.md`, `2026-09-15_T30_wp3_average_profile_arm.md`, `2026-09-21_T87_eui_collector.md` (300 simulations per archetype and year), and the Methods/Results text. Build the count as an explicit product (households x archetypes x cities x years x arms) and cross-check it against at least one delivered-run count on disk (for example a delivered total like 1,200 or 2,400 households per arm).

## Rules
- Do NOT edit the manuscript. Write both numbers, the arithmetic, and the source line for each here.
- If a number cannot be sourced, write NOT FOUND and why; never guess.
- No em or en dashes.

## Output
Fill Verified / Decisions / Next / WHAT I DID NOT VERIFY, set Status DONE, end the turn.

## Ledger
No cluster jobs run. Local reading and grep only (memory files, project docs under
`2J_docs_occ_nTemp/step4_Speed_Cluster/step4_Speed-Cluster_docs/`, and the `writing/submission/rejection
revision/impl/` and `manuscript/` trees). No login-node commands were needed.

## Verified

### Placeholder 1: "([N] architectures searched)"
No single exact integer is stated anywhere as the final answer; three independent project documents
agree on a floor, not an exact count:
- `2J_SI_AE_revised.md:152` and `manuscript/draft_SI_model_selection.md:36`: "Over 40 candidate model
  designs were tried in a staged search" (2% then 20% then full data).
- `manuscript/draft_SI_model_selection.md:155`: number-trace row "Over 40 trials in the search", sourced
  to `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md:3` and `:270` ("across
  40+ trials" / "40+ trials of topology search"), both read directly and confirmed verbatim.
- I also counted the one list in the project that enumerates every trained-and-scored design with its
  own score: `step4_Speed_Cluster/step4_Speed-Cluster_docs/comparision.md`. Table 1 ("Full Data
  Training") lists 48 distinct named architectures, each with a logged `val_score` (rows J5_C through
  J3_CLEAN, lines 11-58, all scored, none blank). Table 2 ("Sample Data Training") adds 7 more distinct
  names trained and scored only at the 10% sample stage (MDLM_D3, MDLM_E3, MDLM_F0-F4; lines 66-72, all
  have a logged `val_score`) plus MDLM_F8 and PP_H0-H5, which the table itself marks "diag only, no
  log" / "diagnostics only, no training logs" (lines 73-74) so I excluded those (not scored). Full-list
  total: 48 + 7 = 55 distinct architectures actually trained and scored, across all stages of the search.

### Placeholder 2: "(50 households per panel, [N] simulation runs)"
"50 households per panel" was already filled by an earlier task (T84, `manuscript/prep/assembly_log.md`
item 4) from "24 cells (4 archetypes x 6 cities), 50 households per cell"
(`2J_manuscript_AE_revised.md:202,425,686`). I built the simulation-run count as a product and
cross-checked it against delivered household counts read directly from `impl/2026-09-21_T79_wp10_
results_number_sheet.md` Verified section:
- Base paired 2022-2030 rebuild (Step 8, the "paired, within-household" design the same sentence
  describes): 24 cells x 50 households x 2 years = **2,400** runs.
  Source: `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:12` ("Step 8: 24 cells x 50 households x
  {2022, 2030} = 2,400") and line 499 ("Go given for T21 phase B... Step 8 2,400"); independently
  confirmed by `manuscript/prep/results_number_sheet.md:153` ("T21: 2,400 household-years = 24 cells x
  2 years x 50 households") which explicitly states the archived abstract's old "6,000 paired
  EnergyPlus runs (2005-2030)" figure has NO rebuilt equivalent and the rebuild scope is 2022/2030 only.
- The manuscript states the paired design was run under "four stated 2030 scenarios"
  (`2J_manuscript_AE_revised.md:10`). Three of the four are ADDITIONAL 2030-only runs beyond the base
  pair above (the fourth, S-Full/lambda=1.0, is the same T20 "main" 2030 build already inside the 2,400
  above, per `impl/2026-09-15_T26_wp2_scenario_builds.md:88` "task 0 = lambda 1.0 (S-Persist, runs vs
  T20 main)"): S-Partial 1,200, S-None 1,198, S-Revert-std 1,199 delivered households, each 24 cells x
  50 (2030 only). Source: `impl/2026-09-21_T79_wp10_results_number_sheet.md:68-69` Verified section,
  read directly ("household counts (S-Full 1200/S-None 1198/S-Partial 1200/S-Revert-std 1199...) ...
  re-read from their own run_meta.json/controls.json").
- Sum used in the Results for this paired-attribution design: 2,400 + 1,200 + 1,198 + 1,199 = **5,997**.

Explicitly EXCLUDED from this count (they belong to the paragraph's OTHER two numbers, already filled,
not this placeholder):
- Step 9 (24 cells x 50 x 2 years x {baseline, activity} = 4,800 E+ runs; source:
  `impl/2026-09-15_T25_step9_run_machinery.md:40` and `2J_manuscript_AE_revised.md:499`) is what backs
  the SHEU 48-of-48-cells number, which is the SAME paragraph's next, already-filled placeholder
  ("48 of 48 cells within the plus or minus 15 percent band").
- T30's average-profile arm (24 cells x 50 x 2 years = 2,400 E+ runs; source:
  `impl/2026-09-15_T30_wp3_average_profile_arm.md:19` "24 cells x 50 x 2 = 2,400 runs") backs the
  "full model vs average-profile arm" / Figure 6 comparison, which is the paragraph's practical
  contribution 5 (diurnal load-shape metrics), not contribution 3.

## Decisions
- Placeholder 1: reporting the well-sourced range, not a single guessed integer. The project's own
  accepted SI/manuscript text already commits to "over 40" (safe, zero new risk, matches
  `2J_SI_AE_revised.md:152` verbatim). My own recount of the one complete trial log gives a more precise
  55 (or 48 if only the full-data stage counts, excluding 7 sample-stage-only trials) -- both are
  consistent with "over 40" but I did not find one document that names 55, 48, or any other single
  integer as THE authoritative count, so I am not overriding "over 40" with my own tally without a
  ruling. Recommend the manuscript either keep the existing SI wording "over 40" (change "[NUMBER FROM
  RESULTS] architectures searched" to "over 40 architectures searched") or use 55 if an exact count is
  required, citing `comparision.md` Tables 1-2 as the source list.
- Placeholder 2: reporting 5,997 as a number I built (product + cross-check), not one I found
  pre-stated anywhere as a single total -- no document states "5,997" or any other single grand total
  for "simulation runs" behind this specific sentence. The three components (2,400 / 1,200 / 1,198 /
  1,199) are each independently sourced and were each re-read from their own run_meta.json per T79's
  Verified section, so the arithmetic is solid; the SCOPE decision (which arms belong to "this"
  placeholder vs. the paragraph's other two, already-filled placeholders) is my own judgment call, laid
  out above with reasons, not something any single document states outright.

## Next
Author/manager decides: (a) which of the two candidate numbers for architectures searched ("over 40" vs
55) to place in the manuscript, and (b) whether 5,997 is the intended scope for simulation runs, or
whether the paragraph's "N simulation runs" was meant to cover the whole campaign (in which case add
Step 9's 4,800 and T30's 2,400 for a grand total of 13,197 -- also computed here, all components
sourced above, just not the reading I judged most consistent with the sentence's own wording). Do not
edit the manuscript from this task; T91 is read/count only.

## WHAT I DID NOT VERIFY
- Did not open or scan any multi-MB file (all reads were of small `.md` docs and their already-quoted
  numbers); did not re-run or re-derive any of T21/T25/T26/T30/T79's own arithmetic from raw CSVs, only
  re-read their stated, already-verified figures.
- Did not check whether comparision.md's Table 1/Table 2 (undated) reflects every phase of the search
  (it appears to post-date the "40+" note in `04_augmentationGSS_IMP_2.md`, since it includes the later
  J6 family and 8B-2/8B-3 B2-series rows that file's "40+" line predates) -- did not find a later
  document that reconciles "40+" with my recount of 55; flagged as an open reconciliation, not resolved.
- Did not verify whether the four 2030 scenario arms (S-Full/S-Partial/S-None/S-Revert-std) are the
  COMPLETE set the Results actually use for every figure that touches 2030, versus only some of R1-R9 in
  `results_number_sheet.md` -- read the sheet's own Verified section for the household counts but did not
  re-read all nine R1-R9 rows individually to confirm every 2030 number in the paper traces to exactly
  these four arms and no others.
- Did not check `manuscript/draft_S0_abstract_highlights.md` or `draft_S1_introduction.md` beyond the
  grep hits already quoted, for any other place these two placeholders (or a resolved version of them)
  might already exist.
