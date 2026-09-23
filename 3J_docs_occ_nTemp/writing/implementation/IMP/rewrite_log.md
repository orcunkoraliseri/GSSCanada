# REWRITE stage 1 - log (chapters_v2)

Status: DONE, stage 1 (2026-09-22). Numbers pass waits for P10R.
Task: execution doc §REWRITE; plan §2-5, §7. Old sources (`writing/chapters/`, `writing/fullSet/`, `writing/tables/`) were not edited. No docx built. No images created.

## Files written (`writing/chapters_v2/`)

00_FrontMatter (title unchanged, authors, abstract, keywords, highlights) · 01_Introduction (1.1-1.4) · 02_Framework (2.1-2.6, Tables 1-2, Eqs. 1-2) · 03_Results (3.1-3.4, Tables 3-4) · 04_Discussion · 05_Limitations · 06_Conclusion · 07_Nomenclature · 08_AppendixA_Table1 (Table A.1) · 09_AppendixB_Equations (B.1-B.8) · 10_Declarations (CRediT, competing interest, funding, data, generative AI, ethics, acknowledgements) · 11_References · SI_additions.

## Measured on the new files (scratchpad `check.py`: HTML comments, equations, tables, headings and captions stripped)

- Abstract 234 words. Main text (sections 1-6) 5,620 words. Limitations 272 words.
- Highlights: 75, 76, 80, 80, 76 characters.
- Prose sentences: mean 16.3 words; none over 40 in sections 1-6 (longest 38, framework §2.6); 4 sentences over 30.
- Em or en dashes in prose: 0.
- Markers `⟦P10R:old⟧`: 143 (front matter 4, intro 2, results 123, discussion 7, limitations 2, conclusion 5).
- Banned-term scan (forecast, gate, uninjected, AT_*, Tag-2, side-track, cell, frozen, deliverable, Step, Leg, Chapter, occPRE/occACT, CYCLE_YEAR, val_score, SLAW, GSSP, TMYx, Retail Retail): no hits in sections 1-6 prose. "forecast" remains only in the 2J reference title. PCGrad appears only inside a [REF NEEDED] placeholder.

## Marker policy (as applied)

- Manager update received mid-task (lighting and plug loads now keep the prototype standby floor in the rebuild). Therefore EVERY injected-simulation number is marked, including 2005/2010/2015 energy, all survey-side P3 values, all scenario-lever values, all Table 4 ranges, medians and counts, and directional words that depend on them (for example ⟦P10R:rises slightly⟧, ⟦P10R:below⟧).
- Plain (not marked): code-schedule control numbers (85.36, 91.74, 0.930, 14.62, 7.21, 9.27, 1.03, 3.78, 260.23, 120.12, 12.02, 12.46, 18.32, 11.98, 0.963, 2.94, 3.14 occupants per 100 m2, peak hours 9 and 15 h), reference-range definitions, design values (levers, thresholds, loss weights, floor areas), and the 07:00 January code-side peak.
- 2005/2010/2015 presence values are marked although their people schedules should not change (P10: Y2005/10/15 products unaffected; the wiring fix touches lights and plug loads, not people). Expect them to come back unchanged.
- Lead point (2) is phrased without a committed size or direction: "change by ⟦P10R:-16 to -20⟧ %", "their day-to-night contrast changes with them".

## What moved where

| Old place | New place |
|---|---|
| Ch00 Abstract (labelled Context/Gap/Aim...) | 00 Abstract, plain prose, D3 lead |
| Ch00 Declarations, Author info | 10_Declarations (end), 00 (authors only) |
| Ch01 §1.1-1.3 | 01 §1.1-1.3 (shortened; meta sentences cut) |
| Ch01 §1.4 prior line | folded into 01 §1.2 (one paragraph) |
| Ch01 §1.5 four advances + aim | 01 §1.4, three scientific + two practical contributions |
| Table 1 (novelty) | Appendix A, Table A.1; axis "Forecast to a future year" renamed "Future-year scenario"; criteria text shortened |
| Ch02 §2.1-2.3, Ch03 §3.1, Table 2 | 02 §2.1 + Table 1 (data/channel role) |
| Ch03 §3.2 model, §3.4 hotel | 02 §2.2 (Eq. 1 hotel multiplier in text) |
| Ch03 §3.4 levers, Ch04 §4.3 levers | 02 §2.3 |
| Ch03 §3.5, §3.6 | 02 §2.4 (plus P5 sampling paragraph) |
| Ch02 §2.4-2.5, Ch04 §4.1-4.3, Table 3 | 02 §2.5 + Table 2; M-1 control description |
| Ch04 §4.4 probes | 02 §2.5 one sentence each; history to SI S.2 |
| metric definitions + P3 method | 02 §2.6, fitted vs independent split, Eq. 2 (CF) |
| Ch05 §5.1 | 03 §3.1 with new Figure 5 (presence) |
| Ch05 §5.3 | replaced by 03 §3.2 (code vs 2022 survey cycle, Table 3, Figure 7) |
| Ch05 §5.4 | 03 §3.3 |
| Ch05 §5.2 + Table 5 | 03 §3.4 + Table 4 |
| Ch06 | 04 Discussion, rewritten around P3 |
| Table 7 (SI) | 05 Limitations (summary) + SI Table S2 |
| Ch08 | 06 Conclusion |
| Ch03 checkpoint story | SI S.1 |
| Ch03 §3.5 wiring story, Ch04 §4.4 stale-output story | SI S.2 |
| Ch05 §5.2 retail rule margin (0.15 %) | SI S.3 |
| Table 6 | SI Table S4 (rewritten, 10.51 sentence removed) |
| Table 4 | SI Table S1 |
| Figures 2, 4, 9, 10 | SI Figures S4, S5, S6, S7 |
| Figures S1, S2 (were in main text) | SI only |

Figure map (new main-text number -> file): 1 `Figure_01_pipeline_4split.png`; 2 `Figure_03_three_head_transformer.png`; 3 `Figure_05_hotel_sidetrack.png`; 4 `Figure_06_tag2_dispatch.png`; 5 `fig_presence_by_channel.png`; 6 `Figure_07_longitudinal_4ch.png`; 7 `fig_codeschedule_vs_survey.png`; 8 `Figure_11_scenario_4ch.png`; 9 `Figure_08_eui_4ch.png`. Tables: 1 channels/data (new), 2 simulation domain, 3 code vs survey (new, from P3), 4 EUI vs reference ranges, A.1 novelty.

## Figures whose data will change after P10R (re-plot from the new arm)

Figure 5 (presence; 2022 and 2030 curves, and all survey curves if people change), Figure 6 (all survey years, because of the wiring fix), Figure 7 (all survey curves and CF panel), Figure 8 (scenarios), Figure 9 (EUI vs ranges), SI Figures S6 and S7, the graphical abstract (also shows the old four-peak lead), and the P3 CSVs behind Table 3. Figures 1-4 and S1-S5 are unaffected.

## Deleted claims, and why

1. "Coincidence factor below 1 in all four cells: use diversity flattens the peak" (abstract, highlight 2, §1.5, §5.3, §6, §7). D3 ruling: CF <= 1 is arithmetic, and the code tower has CF 0.930, lower than the survey tower.
2. "Four peaks at four different hours" credited to the survey model; "A single-channel schedule cannot carry a difference between populations" (§6); "same attenuation effect as household diversity" (§5.3). D3: the code schedules already stagger the uses.
3. §5.3 2030-central peak hours and kW levels (11.90/12.04/12.37/18.91 h, 14.95 h, 72.03/2.11 kW etc.). Replaced by the code-vs-2022 comparison; old Figures 9-10 go to SI. The P9 corrections for this block (office weekday range 11.88-11.93, building 14.10-15.69, retail night 2.10 kW, 0.941/0.851 are 2030-central 4-simulation values) apply if any of it is restored.
4. "decided in advance of the numbers" (§5.2, §7). Reworded per P5+P11 (a) in §2.6 and Limitations.
5. §6 reproducibility paragraph on the 2J extraction defects (plan §3 item 6).
6. §1.3 "a decline this study's own deep-research check found to be internationally normal". Unsourced.
7. §2.3 "No StatCan table of monthly hotel-occupancy rates exists (a data-availability check run for this study)". Unsourced.
8. Table 6 "2030 work presence sits 10.51 percentage points below observed 2022" (P10: wrong as written).
9. Table 7 L6 "Wrong in sign and order in 56 of 56 cells..." (no source in the reported arm; merge note in SI_additions).
10. "Two candidate mechanisms ... refuted in 56 of 56 cells": the "56 of 56" is dropped; the 17 % heating share and rebasing sentences are kept, marked, and flagged (P9 rows 58, 99: no source file in the reported arm).
11. Old §3.6 retail end-use claims: lighting and HVAC follow opening hours; plug load follows the staff schedule and stays on the NECB baseline; customer presence modulates only occupant gain; minimum lighting floors. Replaced by "lighting and plug loads follow occupancy above the prototype's standby floor" (manager wiring statement; `eSim/eSim_bem_utils/commercial_integration.py:384-400, 2160-2186` shows the floor formula and says only LIGHTS diversity has a retail open-hours option, off by default). Not confirmed in code for the old claims, so deleted.
12. "without distorting the individual channel marginals" (exclusivity step). No evidence cited.
13. Contributions "a validation stance" and "the experimental design" (plan R1-D7).
14. Table 3 note "The two models per prototype differ by 36 bytes, the climate tag alone" (P9 alarming 5: the design-day block also differs). Now "share geometry and differ in climate location and design-day sizing data".
15. Table 3 note on the Calgary weather file labelled 6B in the prior study and 7A here. Dropped from the main text; author may restore in SI.
16. Restaurant fifth-channel paragraph (§3.1). Out-of-scope note.
17. Meta sentences: §5 opening structure announcement; "every measured value ... frozen deliverable"; six of seven "no band moved" repeats (one kept in §2.6, plus "verdicts are reported as scored"); "Three things are stated rather than smoothed over"; "This is the gap the present study addresses: not ... but ..."; Hotel "must be read as such".
18. Old keywords "Joint multi-task transformer" and "Energy use intensity band" replaced by "Occupancy schedule" and "Energy use intensity".
19. "Retail Retail" archetype name (now "one retail space type").

## Open items

1. P10R numbers pass: substitute all 143 markers from the new arm; re-derive the §3.1 presence values with scratchpad `pres.py` logic (WD, median of 4 models of `people_per_100m2`, day = hours 9-16, night = hours 0-5) on the new `fig_presence_by_channel_data.csv`.
2. §2.3 paragraph describes the re-raked 2030 construction ("within each labour-force group"). Confirm against P10R phase C.
3. Wiring: Table 4 verdict column keeps the frozen FAIL/INFO verdicts. The old unfloored wiring lowered office EUI by about 20 % (injector comment, `commercial_integration.py:390-393`), so the new arm could change office and retail counts, and possibly verdicts. Manager decides how the paper reports frozen verdicts beside new-arm numbers.
4. V3c: one sentence in §4 (Discussion, control paragraph) and the comment in §2.5 wait for the dwelling-schedule control result.
5. Table A.1 own row merges 1J, 2J and eSim 2026 and keeps the old scoring; the revised 2J scores its own prior line (1J + eSim) present on time-series and calibration only, absent on future-year scenario and activity, partial on stock scale (P12 §1). Author picks: split the row or rescore.
6. Self-citations: 1J and 2J cited as "in preparation a/b" (both rejected, not yet resubmitted). eSim 2026 uses 2J's title form "Longitudinal analysis of occupancy-driven energy demand in Canadian residential buildings (2005-2025)". Author confirms; 1J title may change in its revision.
7. Generative-AI declaration: tool names and purposes are placeholders (Elsevier wording).
8. Funding: 2J says "through a Discovery Grant"; 3J text says only NSERC. Author confirms.
9. Confirm the reference ranges are independent of the SCIEU calibration target (§2.6 says they are the independent check).
10. Confirm the exclusivity rule (Eq. B.4) normalisation against the decode code.
11. Hotel coverage: §2.1 says both series cover 2005-2022, while §2.5 says the Quebec series lacks matching coverage for 2005-2015 (old text had the same tension). Resolve.
12. Context-range central values 280 (retail) and 350 (hotel) are not in the deliverable (P9 rows 67-68); kept as in old Table 5.
13. Hotel 2022 change "+0.09 %" does not reproduce (P9: 0.12 %); marked, re-derive.
14. Figure 1 is still the report-style "Steps 1-9" pipeline; plan R1-M2a asks for a simple redraw. An image prompt is needed (author generates; no image made here).
15. Assembler for `chapters_v2` does not exist yet; the SI merge follows `SI_additions.md` (numbering table, S.1-S.3, Table S4, merge notes).
16. Limitations are 272 words (target about 250); trim in the P13 writing pass if needed.

## REF NEEDED placeholders (for the literature prompt; never invent)

1. Review on occupant behaviour and the performance gap (§1.1).
2. Two or three representative single-use occupancy models: Markov, survival, time-use (§1.1).
3. Mixed-use load diversity and plant sizing / grid peak (§1.1).
4. PCGrad gradient projection (§2.2).
5. Seasonal ARIMA, Box-Jenkins (§2.2).
6. Circular statistics for the mean hour (§2.6).
7. Standard definition of the coincidence factor (§2.6).
8. Occupancy diversity and peak demand in large or mixed-use buildings (§4).
9. Measured energy by use for Canadian mixed-use or high-rise buildings (§4).
10. American Time Use Survey and Harmonised European Time Use Survey (§4).
11. Class-weighted cross-entropy and logit adjustment (Appendix B).
12. One-line scoring criterion per Table A.1 axis (Appendix A).
13. ASHRAE Guideline 14 edition; CBRE/Travel Alberta identifier; ISQ table identifier; SCIEU year and table; PNNL prototype release (References, carried from the old list).

## Stage 2a (2026-09-23): prose wording + author comments

Task: mechanical employee task, "fail" wording in prose + HTML author comments. Backup made at `chapters_v2/_archive_pre_stage2a/` (all 13 files copied, all non-empty, verified before editing).

### Task A - "fail" wording in prose (old -> new, one line each)

1. `01_Introduction.md:33` - "single-use intensity ranges fail to judge the uses" -> "single-use intensity ranges cannot judge the uses"
2. `02_Framework.md:93` - "scored as passed or failed" -> "scored as met or not met"
3. `02_Framework.md:93` - "Retail fails under either rule." -> "Retail does not meet its range under either rule."
4. `03_Results.md:89` - "P10R:28 failing simulations" -> "P10R:28 simulations outside the range" (marker number unchanged)
5. `03_Results.md:91` - "retail also fails a count of individual simulations" -> "retail also does not meet its range on a count of individual simulations"
6. `04_Discussion.md:15` - "The office range fails even for the unmodified code-schedule tower." -> "The office range is not met even for the unmodified code-schedule tower."
7. `05_Limitations.md:7` - marker text only: P10R:fails -> P10R:does not meet its range
8. `SI_additions.md:25` - "discard every checkpoint that failed a hard check" -> "discard every checkpoint that did not pass a hard check"
9. `SI_additions.md:35` - "office output failed to differ from an unmodulated run" -> "office output did not differ from an unmodulated run"
10. `SI_additions.md:41` - "Retail fails under both rules." -> "Retail does not meet its range under both rules."
11. `SI_additions.md:57` (Table S4 cell) - "three reported failing (Table 4)" -> "three reported outside their ranges (Table 4)"

Not touched (exceptions): `03_Results.md:80,81,82` Table 4 verdict cells FAIL / FAIL (median rule) - kept as scored verdicts. No numbers were changed anywhere.

Counts: P10R markers before = 143, after = 143 (unchanged). grep -i "fail" hits before = 13 lines, after = 3 lines (only the three Table 4 verdict cells remain).

### Task B - HTML author comments (verbatim, file:line, classification)

1. `00_FrontMatter.md:27` - "Graphical abstract and highlights are uploaded as separate files at submission (Elsevier order). The existing graphicalAbstract.png still shows the old lead (four peak hours); see rewrite_log.md open items." -> OPEN (graphical abstract file needs an updated lead; deleted from chapter).
2. `02_Framework.md:46` - "P10R: this paragraph describes the re-raked construction (labour-force stratification). Confirm wording against P10R phase C before the numbers pass." -> OPEN (deleted from chapter).
3. `02_Framework.md:60` - "Describes the P10R rebuild wiring (manager, 2026-09-22). The published arm had lights and plug loads on bare occupancy with no floor." -> ALREADY ANSWERED by the surrounding sentence, which already states the current (floored) wiring; deleted.
4. `02_Framework.md:79` - "V3c (fairer control with apartments and guest rooms on the NECB dwelling-unit schedule) is pending; its result decides one sentence in Section 3.2." -> OPEN (deleted from chapter).
5. `02_Framework.md:93` - "Confirm that the reference ranges are independent of the SCIEU calibration target." -> OPEN (deleted from chapter).
6. `03_Results.md:87` - "The heating share and the rebasing claim have no source file in the reported arm (P9 rows 58, 99); re-derive on the new arm or delete." -> OPEN (deleted from chapter).
7. `04_Discussion.md:13` - "V3c pending: one sentence here states whether the hotel and residential presence contrast survives against that control." -> OPEN, same V3c item as #4 (deleted from chapter).
8. `08_AppendixA_Table1.md:15` - "P12: the revised 2J scores its own prior line (1J + eSim 2026) present on time-series and calibration only, absent on future-year scenario and activity/end-use, partial on stock scale and load shape. The row above merges 1J, 2J and eSim 2026 and is scored as the old 3J Table 1 did. Author to decide: split the row (1J+eSim scored as in 2J Appendix A; 2J separately) or keep merged. Listed as an open item in rewrite_log.md." -> OPEN, explicit author decision (deleted from chapter).
9. `09_AppendixB_Equations.md:23` - "Confirm the exact normalisation against the decode code before the numbers pass (the old text says 'threshold-normalized argmax')." -> OPEN (deleted from chapter).
10. `10_Declarations.md:11` - "2J names the NSERC award as a Discovery Grant; confirm the same wording applies to 3J." -> OPEN (deleted from chapter).
11. `10_Declarations.md:21` - "Elsevier standard wording. For reference, 2J states: Claude (Anthropic) to improve grammar and readability; Gemini (Google) to prepare literature research reports and to draw the schematic diagrams from the authors' specifications. Author confirms the 3J tools and figure list." -> OPEN (deleted from chapter; the [TOOL NAME / SERVICE, to be confirmed by the authors] placeholder text is untouched, not inside a comment).
12. `SI_additions.md:21` - "MERGE NOTE: Table S2, row L6: the entry 'Wrong in sign and order in 56 of 56 cells. Exposure takes 2 values across the campaign, not 56.' is deleted. The measurement it states was not computed in the reported runs. The row keeps its limitation statement with the bounding measurement 'Not evaluated in the reported runs.' Row L4 uses 85.36 kWh/m2/yr in place of 85.45." -> OPEN. Table S2 itself is old Table 7 in `writing/tables/Table_07_limitations.md`, not in this file, so the edit it describes is not yet visible anywhere in chapters_v2; deleted from chapter, listed below so the merge step is not lost.
13. `SI_additions.md:41` - "P11: the 0.15 % margin comes from the project decision log, not from the reported arm (P9 row 64)." -> OPEN (provenance note, not stated in surrounding prose; deleted from chapter).
14. `SI_additions.md:59` - "MERGE NOTE: The row '2030 scenarios and hotel model' no longer carries the sentence '2030 work presence sits 10.51 percentage points below observed 2022'. That figure compared a synthetic 2030 pool with a mainly employed 2022 anchor and does not measure the injected schedules." -> ALREADY ANSWERED: Table S4's "2030 scenarios and hotel model" row, immediately above, does not carry that sentence; deleted.

Totals: 14 comments found, 14 deleted from chapters, 2 already answered by surrounding text, 12 open questions.

### Open questions for manager/author

- Graphical abstract PNG still shows the old four-peak-hour lead; needs regeneration to match the current lead (image prompt only, per project rule; `00_FrontMatter.md`).
- Confirm §2.3 re-raking paragraph wording against P10R phase C before numbers pass (`02_Framework.md` §2.3).
- V3c (fairer code-schedule control, apartments/guest rooms on NECB dwelling-unit schedule) is still pending; its result decides one sentence each in §2.5 and §4 (`02_Framework.md` §2.5, `04_Discussion.md` §4).
- Confirm the reference intensity ranges are independent of the SCIEU calibration target (`02_Framework.md` §2.6).
- The office heating-share (17%) and rebasing claim have no source file in the reported arm (P9 rows 58, 99); re-derive on the new arm or delete (`03_Results.md` §3.4).
- Table A.1: author to decide whether to split the "authors' prior residential line" row (1J+eSim scored as in 2J Appendix A; 2J separately) or keep it merged (`08_AppendixA_Table1.md`).
- Confirm the exclusivity-step normalisation wording against the decode code before numbers pass; old text said "threshold-normalized argmax" (`09_AppendixB_Equations.md`).
- Confirm the NSERC funding wording (Discovery Grant, as in 2J) applies to 3J (`10_Declarations.md`, Funding).
- Confirm the AI-use declaration: fill in the tool/service and reason (2J used Claude for grammar/readability and Gemini for literature reports and schematic diagrams) (`10_Declarations.md`, generative AI declaration).
- SI merge: when Table S2 (`writing/tables/Table_07_limitations.md`) is folded in, delete row L6's measured claim and keep only "Not evaluated in the reported runs"; use 85.36 kWh/m2/yr in row L4, not 85.45.
- Confirm the retail scoring margin (0.15 % of the floor) traces to the project decision log and not to the reported arm (P9 row 64) (`SI_additions.md` §S.3).

### Task C - verify

- grep -i "fail" after edits: 3 hits, all Table 4 verdict cells (`03_Results.md:80,81,82`, FAIL / FAIL (median rule) / FAIL) - allowed exception, gate verdicts stay as scored.
- grep "<!--" after edits: 0 hits across chapters_v2/*.md.
- Word count, `03_Results.md`: 2,041 -> 2,020 words (-21).
- Word count, `04_Discussion.md`: 720 -> 703 words (-17).
- P10R marker count: 143 before, 143 after (unchanged).

### WHAT I DID NOT VERIFY

- Did not re-run the scratchpad check.py sentence-length / banned-term scan from stage 1; only grep-based checks above were run.
- Did not check `writing/fullSet/` or `writing/tables/` (old sources) for matching "fail" wording or comments; task scope was chapters_v2/*.md only.
- Did not verify that the SI merge notes (items 12 and 14 above) match the current content of `writing/tables/Table_07_limitations.md`; that file was not opened.
- Did not rebuild the docx or check pagination/word-count against any journal limit.
- Did not judge whether the wording substitutions ("does not meet its range", "cannot judge", "outside the range") read well in full-paragraph context beyond the sentence edited; only the target sentence was checked against the rest of that sentence.
