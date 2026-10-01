# TASK (employee, Sonnet): 5J Step 8 part A: first full manuscript draft from the recorded results

Written 2026-10-01 05:55 EDT by the 5J manager (`date` before every stamp you write). This is a DRAFT for the author; it is written
only from recorded results. Nothing is computed in this task (no Speed job, no local compute). State file: create
`Step8_docs/impl/2026-10-01_wp6_draft.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Read first (in this order; only these files)
1. Style and structure model (sole author, no grant, same journal family): `4J_docs_occ/writing/submission/4J_manuscript_submission.md`
   (copy its section layout, its declaration wording for a SOLE author with NO funding, its Nomenclature and Appendix A
   positioning-table form, its sentence style). Use it for FORM only: do not copy any 4J number or claim.
2. 5J results (the ONLY sources of numbers): `5J_docs_occ/5thJ_00_Occupancy_Surrogate_Pipeline_Overview.md`,
   `5thJ_00_Occupancy_Surrogate_Pipeline.md` (Progress Log), `Step2_docs/outputs_step2/campaign_design.md`,
   `Step4_docs/outputs_step4/gates_frozen.md`, `Step5_docs/outputs_step5/step5_rules.md`, `Step5_docs/outputs_step5/winner.md`,
   `Step5_docs/outputs_step5/models.md`, `Step6_docs/5thJ_06_sealedScoring.md` (esp. 6D), `Step6_docs/outputs_step6/RESULTS.md`,
   `Step6_docs/outputs_step6/claims.txt`, `Step6_docs/outputs_step6/reported_S_*.txt`, `Step7_docs/impl/2026-10-01_step7_design.md`,
   `Resources/nearest_work/NEAREST_WORK.md`, `Prompts/deepResearch/VETTING_RT45.md`, `Step8_docs/5thJ_08_writing.md` and `_val.md`.

## Hard rules
* 🔴 UK: this paper reports Spain and Italy only; UK is mentioned once, as data not used in this study. No UK number anywhere.
* 🔴 Every number in the draft is copied from one of the files above, and the state file lists, for every number, the file and
  line it came from (a "number ledger" table). No rounding beyond what the source prints, except percentages to whole numbers.
  No number from Step 7 exists yet: Section "District demonstration" is written as METHOD only, with one bracketed line
  `[Step 7 results pending]` per paragraph that needs them (this marker is allowed in this draft only).
* 🔴 No word "first", "novel", "to our knowledge", "for the first time" or "unprecedented" (the logged novelty search is not done).
  Contributions are stated as what was done and found.
* No LLM or tool name anywhere except the AI declaration (and there: Claude for analysis code and drafting assistance and
  Gemini for literature search reports, both "checked by the author against the source records"; keep 4J's wording form).
* Journal, not report: no process history ("we first tried", "amendment 2 was written at 21:19"), no internal IDs (job numbers,
  G5J codes become plain names: "load accuracy", "occupancy effect", "blind control", "peak timing", "new country"), no
  meta notes. Rule changes made before the test scoring ARE stated once in Methods as design facts (e.g. "static inputs were
  clipped to the training range", "the tree baseline's outputs were clipped at zero"), without times.
* Limitations are written as limitations (never "failure"); verdicts are reported as the scorer printed them.
* Length: main text about 7,500 to 8,500 words, excluding references, tables and back matter.

## Content plan (sections; follow it)
* Title (one line, finding-led), Abstract (<= 200 words, with the three headline numbers: occupancy effect right in 31/32,
  31/32, 26/28 test cells; load accuracy in 21/14/14 of 32; blind control 0), 5 Highlights (finding-led, each <= 85 characters),
  Keywords.
* 1 Introduction: why stock models need many occupancy samples; surrogates are fast but scored on load, not on the difference
  occupancy makes; the paired design (He et al. 2015) and difference scoring (Park and Park 2023) as the sources; aim and
  four contributions (as findings).
* 2 Methods: 2.1 data (HETUS Spain 2010 and Italy 2014 diaries, generated household-years from the 4J pipeline, the shared
  generated-day pool stated plainly); 2.2 buildings (TABULA archetypes, multi-zone floors and flats, every flat its own
  household, EnergyPlus 23.1, heating 20 C, cooling 26 C, ideal loads, COP 3.0 for total electricity as an assumption);
  2.3 campaign and splits (9,269 runs; new households, new buildings, both new; sealed before training); 2.4 models (B0 average
  household, B1 boosted trees, S temporal convolution / transformer grid, blind control C, seeds, one-country trainings);
  2.5 scoring (load accuracy against ASHRAE Guideline 14 hourly bands; occupancy effect = R² of the hourly pair difference,
  annual sign agreement, skill over B1 with a two-way cluster bootstrap; peak hour; claim rule fixed before the test scoring);
  2.6 district demonstration (Step 7 design: archetype twins of 100 real Madrid buildings, household pool, draws, EnergyPlus
  check, timing) as method only.
* 3 Results: 3.1 model selection on validation (one paragraph; seed spread); 3.2 load accuracy on test; 3.3 occupancy effect on
  test (the key result, with the claim table: holds 11 of 12); 3.4 blind control; 3.5 peaks and presence-heating timing (as a
  like-for-like check); 3.6 size versus timing (73-98 % of the annual pair effect explained by size and appliance level);
  3.7 new country; 3.8 district demonstration `[Step 7 results pending]`.
* 4 Discussion (difference right, level weak; why the baseline differs; what the seed spread means for practice; what the
  shared day pool means for "new household").
* 5 Limitations (bold-led, one paragraph each: archetypes not real geometry; generated days from one pool; one weather year per
  city; seed dependence; Spain and Italy only; ideal loads and fixed setpoints; the TABULA volume inconsistency of one archetype;
  district twins larger than the real buildings).
* 6 Conclusion (numbered findings, as in 4J). Nomenclature. Appendix A positioning table from NEAREST_WORK.md (rows as there).
* Back matter in 4J order for a sole author with no funding. Data availability: Spain- and Italy-derived campaign outputs and
  model weights can be shared under the source licences; code released; UK data not used.
* References: only works named in NEAREST_WORK.md, VETTING_RT45.md, the Overview and the 4J manuscript's reference list where
  the same work is cited for the same point; every entry with DOI as in those files. No new reference.

## Figures and tables (placeholders only; the manager draws figures from frozen data later)
Figure 1 design (image prompt exists), Figure 2 load accuracy, Figure 3 occupancy effect S vs C (key figure), Figure 4 peaks and
timing, Figure 5 district spread. Tables: Table 1 campaign and splits; Table 2 test verdict counts per model and list (from
RESULTS.md); Table 3 claim table (claims.txt rows for S). Captions say what is shown, never what is missing.

## Outputs
`5J_docs_occ/writing/5J_manuscript_draft.md`, `5J_docs_occ/writing/5J_highlights.md`, `5J_docs_occ/writing/AUTHOR_TODO_5J.md`
(what only the author can do: novelty search T46, Li 2021 full text, ASHRAE 2014 edition check, venue, lighting decision,
Step 7 numbers, figure approval), and the state file with the number ledger.

## Report back (short, plain)
Word count; sections written; count of numbers in the ledger; open items; status.
