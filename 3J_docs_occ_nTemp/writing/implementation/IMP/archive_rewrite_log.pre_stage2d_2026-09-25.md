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

## Author rulings 2026-09-25 (apply in stage 2)
- Write like the 2J AE revision (layout + back matter; see `P14_package.md` section 6 top). Open item 8 (funding) CLOSED: "through a Discovery Grant" as 2J.
- AI declaration: Gemini drew Figures 1 to 4 (2J sentence form). Comment 11 CLOSED.
- Open item 5 / comment 8 (Table A.1): SPLIT the prior-line row as 2J does. CLOSED.
- Open item 6 (self-citations): follow the 2J revision's handling of 1J/2J status. 
- V4: Tall vs SuperTall as the two models; add one limitation sentence.

## Stage 2b (2026-09-25): P10R numbers pass

Script `IMP/scripts/p10r_marker_values.py` (one metric function per marker, run on the frozen arm and on P10R; read only on both). Table `IMP/data/P10R/P10R_marker_table.csv` (marker rows + code-column controls + negative controls); console `IMP/data/P10R/P10R_marker_table.out` (dry run) and `P10R_marker_table_apply.out` (apply run). Backup of 00 to 06 before any edit: `chapters_v2/_archive_pre_stage2b_2026-09-25/` (7 files, md5-identical, non-empty). The apply step refuses to run if a chapter differs from its backup, and rewrites only the marker spans (line counts and CRLF endings unchanged).

### Counts (143 markers)

| file | substituted | not reproduced (left) | claim no longer holds (left) |
|---|---|---|---|
| 00_FrontMatter | 4 | 0 | 0 |
| 01_Introduction | 2 | 0 | 0 |
| 03_Results | 121 | 2 | 0 |
| 04_Discussion | 6 | 0 | 1 |
| 05_Limitations | 2 | 0 | 0 |
| 06_Conclusion | 4 | 0 | 1 |
| total | 139 | 2 | 2 |

Remaining `⟦P10R` after apply (grep): 00:0, 01:0, 03:2 (lines 58, 87), 04:1 (line 9), 05:0, 06:1 (line 5). Stray brackets: open = close = marker count in every file, none elsewhere.

### Control

- Substitution only where the OLD formatted value equals the printed text. 136 reproduce by direct rounding; 1 by 3 dp then half-up double rounding (Table 3 retail ratio 47.0547 -> 47.06); 3 by the printed 1-dp value rounded half-up (abstract, Discussion and Conclusion retail "-12 to -15" = -14.48 -> -14.5 -> -15). Claim markers (text) reproduce if the claim holds on the old arm; they are substituted only if it also holds on P10R.
- Positive control: the Table 3 code-schedule column (not markers: 9, 12.02, 7.21, 85.36, 15, 12.46, 9.27, 91.74, 15, 18.32, 1.03, 260.23, 9, 11.98, 3.78, 120.12, 14.62, 0.930, 0.963, 2.94), code office presence 3.14 and the code hotel night-over-midday count (2 of 4): 44/44 reproduce on BOTH arms (Default_NECB injects nothing).
- Negative controls, 12/12 do NOT reproduce, as required: office 2022 EUI from Y2015 (71.29 vs 70.20); Table 3 office ratio on retail (47.05 vs 11.41); residential night over 00-06 (2.1 to 2.2 vs 2.2 to 2.3); office single lever from the B_cons bundle (+1.47 to +2.20 vs +1.67 to +2.45); residential with sens_office_cons and _opt pooled (-0.08 to +0.29 vs +0.06 to +0.29); hotel share from area share (20.25 vs 44.47); office vs code on B_central (-17.0 to -22.7 vs -15.6 to -20.2); retail in-range count from the P10R arm (37/56 vs 12/56); CF6 from B_central (0.941 vs 0.940); hotel occupant peak from code (15:00 vs 22:00); abstract retail 0-dp range from office with all three rounders (-16 to -20 vs -12 to -15); residential range from B_central only (-1.1 to -1.9 vs -1.0 to -1.9).
- Definitions fixed by reproduction (recorded in the CSV): presence = weekday people per 100 m2, hours 09-16 (day) and 00-05 (night), median of 4 models; occupant peak = median of per-model argmax; Section 3.2 = Y2022 vs Default_NECB per model; single-lever ranges = sens_* cells vs B_central (energy_pct_vs_Bcentral); "Residential moves by ... under the office variants" reproduces with sens_office_cons ONLY (pooling sens_office_opt gives -0.08 to +0.29); bundles = B_cons and B_opt pooled; "less than" bounds = max rounded UP at the print dp.

### Not reproduced (markers left in place)

- `03_Results.md:58` "-1.0 to -1.9" (residential vs code). Tried: Y2022 CFA -1.0 to -1.6; Y2022 GFA-share -1.1 to -1.7; B_central -1.1 to -1.9; all survey scenarios -0.9 to -1.9. Only Y2022 + B_central pooled gives -1.0 to -1.9, but that pooling does not reproduce the office and retail ranges in the same paragraph, so it is not the paper's definition. The P10R value on the Y2022 definition would be -0.8 to -1.4.
- `03_Results.md:87` "17" (office heating share). All-56 median 31.7 % (old) / 22.0 % (P10R); mean 31.4; pooled 31.8; heating + fans + pumps + heat recovery 45.2. Only the 4 code-schedule models give 16.6 -> 17 (same on both arms). The number was measured on an earlier arm (V2-B1, 2026-08-04). Author to decide the scope.

### Claims that no longer hold (markers left in place, author to rewrite)

- `04_Discussion.md:9` "The code schedules overstate the energy of office and retail tenants and flatten their daily profile." Overstate still holds (all 4 models, both uses); flatten does not: survey midday-to-night ratios are now BELOW code (office 5.37 vs 7.21, retail 7.75 vs 9.27), so the survey profiles are the flatter ones.
- `06_Conclusion.md:5` "Residential and hotel energy barely move". Test used: every absolute change vs code below 2.0 % (smallest round bound over the old printed maximum, 1.9). Residential max 1.37 % (holds); hotel is now +1.10 to +2.13 % in all 4 models (was -0.57 to +0.33). Judgement call for the author.

### Sentences whose meaning changed (number substituted, wording NOT changed)

1. `03_Results.md:13` retail 2022 vs 2005 +2.36 % -> -4.40 % (four-model range +0.13 to +4.69 -> -4.52 to -4.29): retail now falls in 2022 in every model.
2. `05_Limitations.md:11` "the 2022 retail rise" -> "fall" (direction word substituted, same cause as 1).
3. `03_Results.md:66` residential under the office variants +0.06 to +0.29 % -> -0.29 to -0.07 %: sign flips (known). Also "hotel by 0.00 to 0.00 %" and "office shifts by -0.01 to 0.00 %" now print as zero ranges.
4. `03_Results.md:56` "Their weekday midday-to-night ratios move from 7.2 to 5.4 and from 9.3 to 7.8": the survey contrast is now LOWER than code (was 11.4 and 47.1, higher). Table 3 rows 31 and 35 (5.37, 7.75) say the same. Night load rose most (P10 level check: office night kW x2.3, retail x4.2).
5. `03_Results.md:81` Table 4 retail 12/56 -> 37/56; the (unmarked) verdict cell still reads "FAIL (median rule)" but the P10R gate is PASS (median 84.85 inside 80 to 155). Office stays 0/56, FAIL.
6. `03_Results.md:91` "Retail falls short of its floor. The median ... is 84.85 kWh/m2/yr, -6.07 % below the floor of 80. 37 simulations lie inside the range and 19 lie below it, so retail also does not meet its range on a count of individual simulations": the median is now above the floor and inside the range; the whole paragraph reads wrong.
7. `04_Discussion.md:15` "The retail median falls above its floor, while the code-schedule control falls inside" (direction word "below" -> "above"): both now inside, the contrast is gone.
8. `05_Limitations.md:7` "retail does not meet its range under the all-simulations rule as well": still true for the all-simulations rule (37/56), but "as well" now implies the median rule is also not met, and it is met.
9. `06_Conclusion.md:7` (unmarked) "the retail verdict follows from the survey-based customer schedule": retail now meets its range; not a marker, not edited.
10. `00_FrontMatter.md:13`, `04_Discussion.md:9`, `06_Conclusion.md:5` retail "-12 to -15" -> "-9 to -9" (P10R range -8.9 to -9.4 rounds to one number at 0 dp); office "-16 to -20" -> "-7 to -10"; `01_Introduction.md:35` "12 to 20" -> "7 to 10". The code-vs-survey energy effect roughly halves.
11. `03_Results.md:58` "Hotel intensity changes by less than 2.2 %" (was 0.6): the hotel change is now positive in all 4 models, +1.1 to +2.1 %.
12. `03_Results.md:11` office presence "1.80 in 2022 and 1.80 in the central 2030 scenario" (was 2.13 and 1.66): 2030 no longer below 2022 at two decimals.
13. `03_Results.md:52` residents' occupant peak "midnight" -> "01:00"; Table 3 office occupant peak 10 -> 12, retail 14.5 -> 15.5. No reversal, noted for the figure text.

Claims that still hold on P10R (text kept, brackets removed): hotel verdict splits by prototype (all 28 out-of-range are Tall above 300; SuperTall 204.83 to 221.86, Tall 304.41 to 322.18, the gap contains the ceiling); annual building maximum at 07:00 in January in every code and Y2022 model; CF change positive (+0.005 to +0.012), so "raise/rises slightly" holds; bundles additive (worst per-model gap 3.8 % of the bundle, old 1.9 %); Service/MEP rebasing lowers office EUI in 56/56; hotel night energy above midday in all four Y2022 models.

### WHAT I DID NOT VERIFY

- Did not rewrite any sentence; the 13 items above and the 4 left markers need author or manager wording.
- Did not touch 02_Framework, 07 to 11, SI_additions, figures, captions or `writing/tables/`; numbers there (and figure images) still come from the frozen arm.
- The "barely move" threshold (2.0 %) and the additivity threshold (5 % of the bundle) are my choices, stated above; they are not from the paper.
- Did not check whether prose outside markers (for example 03:13 "do not move together", or 03:9 "much lower" with residential 2022 daytime presence now 1.26) still reads right beyond the items listed.
- New values use direct rounding of the exact value; no double rounding was applied to P10R numbers.

## Stage 2c (2026-09-25): meaning pass, V3c/V4 sentences, back matter (manager)

Backups: `chapters_v2/_archive_pre_stage2c_2026-09-25/` (00, 01, 03, 04, 05, 06, 08, 10, 11 before first touch) and `_archive_pre_stage2c_v3c_2026-09-25/` (00, 02, 04, 05, 06 before the V3c edit). Scripts in the session scratchpad (`stage2c_meaning.py`, `stage2c_v3c_v4.py`, `decl_2j.py`, `selfcite_tableA1.py`); each asserts one match per edit and writes nothing on a miss. Zero markers left; zero en/em dashes.

- 4 markers the agent left: residential vs code now "-0.8 to -1.4" (2022 vs code, the definition that reproduces office/retail in the same paragraph; the printed -1.9 never reproduced); heating share now "about 17 % ... in the code-schedule models and 22 % across the 56 simulations" (both measured, both below 35 to 45); Discussion "flatten" reversed to "sharpen the contrast between their midday and night loads" (code ratios 7.2/9.3 vs survey 5.4/7.8); Conclusion "barely move" -> "change by about 2 % or less" (hotel +1.1 to +2.1, residential -0.8 to -1.4, P3_delta_vs_code.csv).
- Retail now meets its range by the median rule (Step-9 P10R gate S9-EUI-retail = PASS, 37/56 in, 19 below). Table 4 verdict cell -> "PASS (median rule)"; §3.4 retail paragraph, Discussion, Limitations and Conclusion reworded ("meets on the median, not in every simulation").
- "-9 to -9 %" -> "about -9 %" (front matter, Discussion, Conclusion). Cross-effect "0.00 to 0.00" -> "less than 0.01 %".
- V3c (result in `IMP/V3c_results.md` §6): the dwelling-unit control (NECB-G) also puts residents and guests in at night (weekday peak ~23:00); the night contrast is a property of the office-hours control. Sentences added in §2.5 (second control described), §4 control paragraph (contrast + timing holds: centroid 0.03 h, CF 0.001), §5, Abstract, Highlight 2 (now office presence), Conclusion. Graphical-abstract prompt top chart switched hotel -> office.
- V4: one limitation sentence (one tower family; Tall vs SuperTall the only structural contrast).
- Back matter 2J form: Discovery Grant (Funding + Acknowledgements); AI sentence = Claude (grammar/readability) + Gemini (research reports; Figures 1 to 4 and the graphical abstract); sources checked against publisher records.
- Table A.1 split as 2J: prior line (1J + eSim 2026) scored as 2J does (future-year ✗, activity ✗, stock-scale P); second companion manuscript (2J) on its own row.
- Self-citations as 2J: unpublished manuscripts named in text as "companion journal manuscript, under review", removed from References; eSim 2026 kept. AUTHOR CHECK AT SUBMISSION: 2J must be submitted to AE before 3J goes out, otherwise "under review" is untrue for it.
- Still on the old arm (next, P9 second pass): numbers in 02, appendices, SI, `writing/tables/`, and the figures.
- Reference fix (manager, 2026-09-25 ~02:55 UTC): `11_References.md` Widén and Wäckelgård (2010) entry "A Swedish time-use survey and its utility for building energy modeling", E&B 42(5) 706-714, doi 10.1016/j.enbuild.2009.11.010 replaced by the 2J Crossref-checked record (Applied Energy 87(6) 1880-1892, doi 10.1016/j.apenergy.2009.11.006). Flag came from RV12; the replacement comes from the trusted 2J list, not from RV12. Fits the Introduction sentence (time-use-survey residential model).
- Status fix (manager, ~03:10 UTC): "under review" -> "in revision" for both companion manuscripts (01:17 x2, 04:11, 08 Table A.1 x2). Source: `IMP/P12_consistency_facts.md` (2J declined by Building Simulation 2026-09-15, 1J declined by JBPS 2026-09-19 with invitation to resubmit; neither under review). Re-check at submission.
- V3-O2 cross-check (manager, ~03:20 UTC): read the P10R IDFs. Code control `Default_NECB__Tall__MTL/injected_resized.idf` keeps office lights on `OfficeLarge BLDG_LIGHT_SCH_2013` and equipment on `NECB-A-Electric-Equipment` (prototype load schedules); survey cell `B_central__Tall__MTL` puts them on `MXU_Office_Load_f045/f200_*` (occupancy-following with standby floor). So the §3.2 office/retail differences combine occupancy AND the load-schedule switch (F-V3-1). V3b U-vs-R (frozen contract, no floor) measured the switch alone with code occupancy as RAISING office lights/equipment (+23 %/+66 %), so the presence part alone is likely larger than -7 to -10 %; not measured on P10R, not quoted. Limitation sentence added to 05. PENDING after the P9 agent releases 02: one sentence in §2.5 control paragraph ("In the control, office and retail lighting and plug loads also stay on the prototype schedules"). V3-O2 (sign vs P-b4) stays an open item in V3 doc; no prose depends on it.

## P9 second pass (2026-09-25): numbers outside 00/01/03 to 06, tables, data figures

Scripts: `IMP/scripts/p9_second_pass.py` (numbers; imports the Stage 2b `p10r_marker_values.py` Arm class and metric functions, one function per number, run on both arms) and `IMP/scripts/p9_figures.py` (figures). Table `IMP/data/P10R/P9_second_pass_table.csv`; console `IMP/data/P10R/P9_second_pass.out` (dry run + apply run) and `IMP/data/P10R/P9_figures.out` (install run). Backups before any edit, md5-identical and non-empty: `chapters_v2/_archive_pre_P9_2026-09-25/` (SI_additions.md), `tables/_archive_pre_P9_2026-09-25/` (Table_07_limitations.md), `figures/_archive_pre_P9_2026-09-25/` (7 figures, PNG + PDF, and the two P3 figure scripts), `submission/figures/_archive_pre_P9_2026-09-25/` (Figures 07 to 11, PNG + PDF). 02_Framework.md was read only, not edited.

Scope read: chapters_v2 02, 07, 08, 09, SI_additions; the table files the SI uses (Table_04_validation_gates.md = Table S1, Table_07_limitations.md = Table S2, tables/SI/Table_A1_A2.md = Table S3). Not used by the manuscript or SI, not edited (old main-text tables now inline in chapters_v2): Table_01, 02, 03, 05 (still carries frozen-arm numbers, superseded by 03 Table 4), 06, SI/Table_B1, SI/Appendix_C. Not in scope and still on the frozen arm: the assembled `fullSet/readySubmission_SI.md` and `submission/3J_supplementary_material.md` (their Table 7 copy updates when the SI is rebuilt).

### Counts

- Arm numbers: 14. Substituted 6 (5 change value, 1 same value): Table S2 row L5 hotel range 203.33-318.42 -> 204.83-322.18 and "28 of 56" (same); row L7 retail median 75.63 -> 84.85, "5.47 % below" -> "-6.07 % below", "44 of 56 cells under" -> "19 of 56"; SI_additions.md:55 "three reported outside their ranges" -> "two".
- Not reproduced, left as printed: 8 (list below).
- Constants, not arm: 563 numeric tokens on 260 lines (02: 45 lines, 07: 3, 08: 5, 09: 15, SI_additions: 16, Table_A1_A2: 45, Table_04: 40, Table_07: 91 incl. its provenance notes). 02, 07, 08, 09 hold no arm result.
- Negative controls 13/13 do not reproduce (wrong basis, wrong prototype, wrong scenario, wrong band limit, wrong gate set, wrong channels, new arm read as old). Positive controls 5/5: the same functions on P10R reproduce 03 Table 4 (hotel 204.83-322.18, retail 84.85, 19 below floor, 28 above ceiling) and the 18/2/10 scorecard (2 scored FAIL).
- Table_07 also got an additive note 6 at its end (below the provenance notes, not printed in the SI).

### Not reproduced (left as printed)

1. Table_07 L4 "85.45" (uninjected control office EUI): Default_NECB office CFA median is 85.36 on BOTH arms; mean 85.65, GFA-share 82.09. Source is V2-B1 (earlier arm). The SI merge note (Stage 2c item 12) already asks for 85.36.
2. and 3. Table_07 L6 "56 of 56" and "2 values": the stacked-channel test was not run on either arm (gate S9-EUI-EXPOSURE is INFO, "step9_envelope_exposure.csv not found", both arms). The merge note deletes the claim.
4. to 6. Table_07 L16 "-0.98", "26.7 %", "65.4 %": V2-B4 per-heater DHW diagnostic; no per-heater series in agg_* or step9_*.
7. SI_additions.md:39 "0.15 %": decision margin of an earlier run (V2-B3). Tried: smallest |retail - 80| / 80 over 56 simulations = 0.82 % (old) / 0.37 % (P10R).
8. SI_additions.md:39 "-0.05 %": median shift between two earlier runs (V2-E3); history.

### Sentences whose meaning changed (wording NOT changed; manager to rewrite)

1. `chapters_v2/02_Framework.md:93` "Retail does not meet its range under either rule." Now false: retail meets the median rule (gate PASS, median 84.85 inside 80 to 155) and does not meet the all-simulations rule (37/56).
2. `chapters_v2/SI_additions.md:39` "Retail does not meet its range under both rules." Same.
3. `tables/Table_07_limitations.md:14` (Table S2 L7) "Median 84.85 against a floor of 80, -6.07 % below, 19 of 56 cells under": the median is now above the floor; "-6.07 % below" reads wrong.
4. `chapters_v2/SI_additions.md:55` (Table S4) "two reported outside their ranges (Table 4)": office and hotel only; retail no longer counted.
5. `tables/Table_07_limitations.md:4` "No verdict is paraphrased and every number is the source's own.": L5 and L7 now carry P10R values, not the source document's.
Unchanged meaning: Table S2 L5 hotel still FAIL, 28/56, all Tall above 300; L4 control still below the 100 floor.

### Figures (regenerated from P10R, matplotlib from data)

Controls (`P9_figures.out`, 63 PASS / 0 FAIL): the frozen arm re-rendered with the same code reproduces all 5 current Step-9 PNGs and both P3 figures (PNG and PDF) byte for byte; the P10R arm at 140 dpi reproduces the Step-9 P10R run's own figures; Step-9 tables rebuilt from agg_P10R equal outputs_step9_P10R (224/224/64 rows, max diff 6e-14, verdicts identical); the superseded agg arm does not reproduce any current PNG; 23 spot checks of figure data against 03 Tables 3 and 4 and text all match (office/retail/hotel/residential/building midday-to-night ratios 5.37/7.75/0.80/3.86/2.40, office peak 11.81, CF 0.939 and 0.930, occupant peaks 12/15.5/22/1, four Table 4 ranges, 37/56 and 28/56, retail -4.40 %, office -1.99 %, two lever ranges); 8 wrong reads (wrong hours, frozen data, wrong scenario, bundle for single lever, wrong basis, wrong channel) do not match.
The old Step-9 PDFs were NOT reproducible by the render tried (made by another route); the new PDFs are the same figure objects saved with bbox tight and no date metadata.

md5 before -> after (writing/figures; Figures 07 to 11 also in writing/submission/figures, identical md5):
- Figure_07_longitudinal_4ch.png 474314e9d455ef6acf237f94eea8f870 -> 58e396e1c2bca058ac9da6738acbe007; .pdf e6abcc64b7ac54ac1ec97678faef89fd -> 7ef0af15fdea45471dc95e04742dab67
- Figure_08_eui_4ch.png 15af64b6d1cf9bd3b42e6cfb131ed156 -> e8a21049f2833cf6f79b811abd1fb912; .pdf 91e8d0ac3224be333ed7e56c146424f2 -> 1b3befc4b9223a3a72643db5c2749e90
- Figure_09_diurnal_4ch.png (SI S6) 8588145b55d937eecd0c1e2aa977586b -> da9835f34d77424281ec37fffcfe5308; .pdf 519a80ca20659236693ccd6dbf0012f9 -> 15d945bd0253c8eb9442cc2c52a582d1
- Figure_10_peakhour_4ch.png (SI S7) ae4d14cc14beec07c7d05c7e80d8915a -> 582c1e9598cb58dafc6a1d3294528ce9; .pdf be8ddacf45167b6acddb734203bc6299 -> d8f16bca58663b0301e22abb92fd85d7
- Figure_11_scenario_4ch.png 6f4a6703147335bc714e52920f594c39 -> e74d8088edd78bfbbc4c7f1a35392696; .pdf 2aee904b4fd853e38dd269a727688e18 -> bb639d721ddf28904b35929158627d75
- fig_presence_by_channel.png 82abbebf4ace9b712a03bc4559946fc0 -> 8fc1a513b01493f1500314d3b4adf2f5; .pdf b5e4846af1f54cafd1386b8f2f99cdc3 -> 21dd419b2cb1287ada496d2bed5368df
- fig_codeschedule_vs_survey.png 447350908b199f6be7cb885b5bd8ead7 -> e31c2e3df401e110c690f8e18f2fe5bc; .pdf 886d963e22e3ea8531ba101b6cbf0f1d -> feffc05c062c2ebd84aeb00adca4622f
- `fig_presence_by_channel.py` and `fig_codeschedule_vs_survey.py` now take `--arm P10R|deliverable` (default P10R, reads `_P10R_figdata/`); run standalone they reproduce the installed md5.
- Not touched: Figure_01 to 06 schematics, graphicalAbstract, SI S1 (floor-area shares, geometry constants), S2 (lever values), S3 to S5 (schematics).

### Open for the manager

- The five Step-9 figures still carry internal titles drawn by the Step-9 code (for example "Step 9 §R1 ... all 56 cells", with an em dash) and lower-case channel labels. Unchanged by this pass (same code as the frozen figures); a journal-style replot is a separate task.
- Table S2 L4 (85.45) and L6 wait on the SI merge note; not edited here.
- `P9_number_sheet.md` has no status table, so no line was added there.

### WHAT I DID NOT VERIFY

- Did not rebuild the docx or the assembled SI; `fullSet/readySubmission_SI.md` and `submission/3J_supplementary_material.md` still show the frozen-arm Table 7.
- Did not re-run `p3_code_schedule_comparison.py --arm P10R`; the `_P10R_figdata` CSVs were used as written on 2026-09-24 22:07 and checked only against 03 Tables 3 and 4 (23 spot checks).
- Did not open the old Step-9 PDFs to see how they were made.
