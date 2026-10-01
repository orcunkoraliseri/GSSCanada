# 1J resubmission — what only the author can do

Rewritten 2026-09-30 by the manager session (plan log (bo)). All analysis, writing and file building is done.
**Folder (2026-09-30):** `manuscript/` holds only the five files to upload; sources are in `manuscript/resources/`, backups in `manuscript/archive/`. Submission page: https://rp.tandfonline.com/submission/flow?submissionId=266775447&step=1
The earlier version of this list is in the plan log; items 1-4 of it are closed (references vetted, funding line set,
Figure 4 checked, tracked file made by the manager).

**Read this first: the hindcast result.** The projection did NOT beat carrying the 2016 census forward: it was closer to
the 2021 Census on 7 of 24 variables (the pre-set rule needed at least 13). As the rule said before the test, the paper
drops the claim that the projection forecasts better than carry-forward and reports the count. The 2025 cohort is now
described as a scenario close to the 2021 population (Abstract, Section 4.2 + Table 9, Section 5.2, Conclusion,
Appendix A, cover letter, Comment 4 answer). Please read those passages; the title still says "hindcast-tested", which
remains true.

1. **Cover letter:** DONE 2026-09-30 — dated September 30, 2026 and `1J_cover_letter_R1.docx` rebuilt (0 markers left).
   Read it once; if you upload on another day, change the first line of `resources/1J_cover_letter_R1.md` and run `pandoc resources/1J_cover_letter_R1.md -o 1J_cover_letter_R1.docx` from `manuscript/`.
2. **Final read** of `manuscript/1J_manuscript_R1.docx` (clean) and `1J_manuscript_R1_tracked_anonymous.docx` (Word
   compare against the submitted file, 883 changes).
3. **Upload** on the JBPS resubmission page (the page asks for two manuscript copies, see `manuscript/guide/`):
   - "Manuscript - with author details": `1J_manuscript_R1.docx`
   - "Manuscript - anonymous": `1J_manuscript_R1_anonymous.docx` (author block, CRediT and funding text removed; the two
     self-citations read "Anonymised for review."; build `py resources/build_R1.py --final --anon`)
   - Supporting file: `1J_manuscript_R1_tracked_anonymous.docx` (track changes vs. the submitted version, names removed;
     the version with names is in `archive/`)
   - `1J_response_to_reviewers_R1.docx` (checked: no author names) and `1J_cover_letter_R1.docx`
   - "Respond to comments" box, paste: "Our point-by-point response to every reviewer comment is uploaded as the file
     1J_response_to_reviewers_R1.docx. Each answer gives the section where the manuscript was changed; all changes are
     marked in 1J_manuscript_R1_tracked_anonymous.docx."
   - Delete the old files from the submission system.
4. **Upload page fields** (from `manuscript/guide/Manuscript Submission - abstract 3.pdf`, 2026-09-30):
   - Abstract box (must be under 150 words): paste the manuscript abstract, now 147 words (also in both .docx):
     Occupancy schedules for building performance simulation are usually fitted to one survey year and treated as fixed. This study builds household presence, activity and metabolic schedules for Canada from four General Social Survey time-use cycles (2005–2022) linked to the Census, and projects the household population to 2025 with a conditional variational autoencoder and a cluster-based drift model. In a hindcast against the held-out 2021 Census, the projection beat carrying the 2016 population forward on only 7 of 24 variables, missing the pre-set pass rule, so the 2025 cohort is used as a scenario, not a forecast. Households were at home 15.6–16.2 h per weekday in 2005–2015 and 17.9 h in 2022. Against a standard apartment schedule, the survey-based schedules raised simulated heating by 6–16 % and lowered cooling by 1–9 % in three Montreal house neighbourhoods, and changed both by under 7 % in three apartment neighbourhoods.
   - Word count box: 10924 (Word's count of the whole file, same basis as the 9112/9119 of the first submission;
     main text without tables, figures, equations and references = 6589). The journal's own limit could not be fetched
     (site blocks scripts) — check it on the journal page if in doubt.
   - AI checkbox: the declaration now names Claude Opus 5.5 (Anthropic) and Gemini 3 Pro Deep Research (Google), as you chose.
   - Published material: No (the eSim 2026 paper is cited, nothing reused — your answer). Human participants: No
     (public-use survey files). Data set: No.
5. Optional: run `IMP/deepResearch/dr_1J-07` and `dr_1J-08` (missing-age handling) — not needed for resubmission.
6. Decide about the shared code: `eSim/eSim_bem_utils/plotting.py` `calculate_eui()` still has the peak-demand defect fixed in 2J in
   August. The 1J numbers are now extracted by a separate corrected script; the shared file is untouched until you say so.
7. Delete when convenient (approval needed): `/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_5/NUS_RC4.BROKEN_draw23_20260928`
   and the stray `/speed-scratch/o_iseri/1J_rerun/wp14_probe.py`.
8. **Not 1J, found while checking references:** the paper Iseri, Dino, Kalkan (2026), Energy and Buildings 357, 117155 is listed
   with "Kalkan, S." in the submitted 2J and with "Kalkan, B." in the 4J manuscript. Check the publisher record and fix 4J before its upload.
