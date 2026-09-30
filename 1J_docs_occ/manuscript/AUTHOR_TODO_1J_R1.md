# 1J resubmission — what only the author can do

Written 2026-09-29 by the manager session. Everything else is done or running (see `IMP/00_REVISION_PLAN.md`, latest entry).

1. **Run the reference check.** Paste `IMP/deepResearch/dr_1J-09_reference_check_prompt.md` into Gemini; save the answer next to it as
   `dr_1J-09_reference_check_results.md`. The manager vets it and fills the `[[TITLE]]` / `CHECK` items in
   `manuscript/R1_references.md`. The final build refuses to run while any CHECK or `[[...]]` remains.
   Highest priority inside it: open **Dias dos Santos, Moghadasi and Paez (2025)** yourself — it may be the closest Canadian precedent.
2. **Confirm one fact:** the funding line for 1J (the draft copies the 2J one: NSERC Discovery Grant + Volt-Age Seed Fund,
   plus the 2J sentence that the funders had no role). Settled on 2026-09-29 (bm): the buildings (Section 3.6, from the IDFs);
   the eSim conference paper is cited as presented at eSim 2026, exactly as the submitted 2J and 3J papers cite it
   (`iseri2026esim`), with one sentence in Section 1.3; the 2J companion is cited as submitted to Energy and Buildings.
2b. **Cover letter:** `manuscript/1J_cover_letter_R1.md` (modelled on the 2J one): add the upload date; read it once.
   Titles/authors of Osman 2023 and Chen 2022 and the Yin 2024 link were taken from the submitted 2J reference list, so
   dr_1J-09 only needs to confirm the claims for those three.
3. Figure 4 (matching workflow) checked by the manager: it shows no percentages, so it stays as is.
4. **Tracked-changes file:** open `manuscript/submission_Occ_NUsJournal.docx` in Word, Review > Compare > Revised document =
   `manuscript/1J_manuscript_R1.docx`, save as `1J_manuscript_R1_tracked.docx`. (Word's compare gives the "changes highlighted" file
   the journal asks for.)
5. **Upload** on the JBPS resubmission page: clean .docx, tracked .docx, response letter (no author names), figures if asked;
   delete the old files from the submission system.
6. Optional: run `IMP/deepResearch/dr_1J-07` and `dr_1J-08` (missing-age handling) — not needed for resubmission.
7. Decide about the shared code: `eSim/eSim_bem_utils/plotting.py` `calculate_eui()` still has the peak-demand defect fixed in 2J in
   August. The 1J numbers are now extracted by a separate corrected script; the shared file is untouched until you say so.
8. Delete when convenient (approval needed): `/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_5/NUS_RC4.BROKEN_draw23_20260928`
   and the stray `/speed-scratch/o_iseri/1J_rerun/wp14_probe.py`.
9. **Not 1J, found while checking references:** the paper Iseri, Dino, Kalkan (2026), Energy and Buildings 357, 117155 is listed
   with "Kalkan, S." in the submitted 2J and with "Kalkan, B." in the 4J manuscript. Check the publisher record and fix 4J before its upload.
