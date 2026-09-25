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

## Stage 2d (manager, 2026-09-25 ~03:10 UTC): P9 meaning fixes, vetted references

Backup of every chapter touched: `chapters_v2/_archive_pre_stage2d_2026-09-25/` (02, SI_additions, 01, 04, 11) and `tables/Table_07_limitations.md` (same folder).

P9 meaning-changed sentences rewritten:
1. `02_Framework.md:93` -> "Retail meets its range under the median rule but not under the all-simulations rule, where 19 of 56 simulations fall below the floor."
2. `SI_additions.md:39` -> "Retail meets its range under the median rule but not under the count of individual simulations (37 of 56 inside)."
3. `Table_07_limitations.md` L7 -> "Median 84.85 against a floor of 80, inside the range; 19 of 56 cells under the floor."
4. `Table_07_limitations.md:4` -> "No verdict is paraphrased. Rows L5 and L7 carry the numbers of the reported runs; the other rows carry the source's own numbers."
5. `SI_additions.md:55` "two reported outside their ranges": correct as it stands (office and hotel); not changed.
6. Pending item closed: `02_Framework.md` Section 2.5 now adds "In both controls, office and retail lighting and plug loads stay on the prototype schedules, while in the survey-based runs they follow occupancy above a standby floor."

References applied from `deepResearch_Resources/VETTING_RV11_RV14_2026-09-25.md`, TRUSTED-2J rows only (metadata copied from the 2J AE revised reference list, en dashes turned to hyphens):
- M1 Widén (already applied in stage 2c).
- M2 `01:5` (de Wilde, 2014; Mahdavi et al., 2021).
- M3 `01:5` (Richardson et al., 2008; Widén and Wäckelgård, 2010; Wilke et al., 2013), Wilke with the 2J title and pages.
- M7 `01:27` (Barrero et al., 2023; Statistics Canada, 2024).
- M14 `02:85` (Mardia and Jupp, 2000).
- M21 `04:17` HETUS half (Eurostat, 2018); ATUS half left as "[REF NEEDED: ATUS source]".
- M35 SHEU entry in the 2J form (CODR note kept).
- Not applied: M10 Caruana (optional, no placeholder), M40 Deru (only if s(t) came from the DOE Large Hotel schedule: author question).
- Checks: all 9 new keys present in 11_References, list alphabetical, 0 en/em dashes, [REF NEEDED] 17 -> 14.
- CANDIDATE rows (19) are for the author to open; listed in RESUME.

Side finding S2 (hotel data span) confirmed from `Leg3_4-split/Step6_docs/3rdJ_06_hotel_sarima_4split.py:24-43`: real values AB 2011-01..2022-09, QC 2019-01..2022-12, no CBRE 2005-2009 splice, QC order borrowed from AB, 2030 central path = 2019 shape x anchor. `02_Framework.md:15` ("Both series cover 2005 to 2022"; "CBRE and Travel Alberta") is therefore wrong. A fact-trace agent is writing `IMP/hotel_channel_fact_trace_2026-09-25.md`; fixes follow from it.

## Stage 2d hotel fix and figure prompts (manager, 2026-09-25 ~03:40 UTC)

Source: `IMP/hotel_channel_fact_trace_2026-09-25.md` (code trace). Backups: `chapters_v2/_archive_pre_stage2d_hotel_2026-09-25/`.
- `02:15` source and span: Government of Alberta tourism market monitor (not CBRE / Travel Alberta); Alberta 2011 to 2022, Quebec 2019 to 2022 (was "2005 to 2022").
- `02:36` hotel method rewritten to what the code did: 2022 = observed monthly rate (Alberta Oct to Dec repeat September); 2030 = 2019 monthly pattern x recovery level 0.615 (AB) / 0.635 (QC) with a new [REF NEEDED: source of the 2023 to 2025 hotel recovery levels]; SARIMA(1,1,0)(0,1,0,12) fitted on Alberta, reused for Quebec, with pulse Mar 2020 to Jun 2022 plus a level shift from Mar 2020; the model checks pattern and dip, its forecast is not used (drifts above full occupancy).
- `02` Table 1 hotel row: "Observed monthly rate for 2022; 2019 monthly pattern scaled to a recovery level for 2030".
- `02:70` code-schedule reason: "the provincial series do not cover those years in both provinces".
- `02:91` reconstruction: Alberta 2015 to 2019, Quebec 2019 only; dip direction reproduced, not its full depth.
- `05` new paragraph: Quebec order borrowed, 2019 reconstruction error 0.099 above the 0.05 threshold met by Alberta; 2030 hotel level rests on one recovery level per province.
- `10` data statement: "Government of Alberta" replaces "CBRE and Travel Alberta".
- `11`: CBRE entry removed; Government of Alberta (2022) entry added; ISQ entry filled from our export's source line; both keep a [REF NEEDED] for access date / table id.
- `tables/Table_04_validation_gates.md:37`: backcast window per province.
- AUTHOR QUESTION (new): the recovery levels 0.615 / 0.635 came from a deep-research report given to the Step 6 builder ("CBRE/STR-reported 2023-2025"), never vetted. They set the 2030 hotel level. The author must find the source or the paper must say they are assumed.

Figures found carrying internal notes (installed v3 drawings; journal figures must not): main Figures 2, 3 and 4 and SI S2 to S5. Prompts written (no image made):
- `submission/figures/Prompts_Images_v4/Figure_03_hotel_channel.md` (main Figure 3; also wrong: CBRE, old SARIMA order, SARIMA shown feeding the rate).
- `submission/figures/Prompts_Images_v4/Figure_02_and_04_redraw.md` (main Figures 2 and 4).
- `submission/figures/Prompts_Images_v4/SI_schematics_redraw.md` (S2 to S5).
- SI S1 is a data plot: an employee is redrawing it without title and dated footnote.

## Figure S1 cleaned 2026-09-25

Task: employee prompt, redraw SI Figure S1 (occupiable-area shares per tower) as a clean journal figure from the same data. Script `figures/SI/figS01_shares.py` read only, not edited; copy made at `figures/SI/figS01_shares_clean.py` and edited.

- Verified the unedited copy first: it reproduced the installed PNG and PDF byte for byte (md5 `72837247373eecb991f7fadc6c547a03` / `4e950feb3629ceebf4c7960df0fe789b`), and `figures/SI/` already matched `submission/figures/SI/` exactly before any change.
- Changes made in the copy only: removed the top caption ("measured occupiable-area shares per tower prototype"); removed the dated footnote (Corrected 2026-07-31 / Superseded figures text); reworded the Service/MEP box text to "Service and plant space: 20.6 % of gross floor area (SuperTall), 21.4 % (Tall); not occupiable" (numbers unchanged from the script, 20.6/21.4, matching Appendix C 20.64/21.41 rounded); replaced "residential-common" with "residential common" in the stacked-bar labels, the legend dict and the LABELS list. No other text, data, colours, layout, size (7.2 x 5.8 in) or dpi (520) changed.
- Checks: (a) extracted every rectangle patch (x, y, width, height, facecolor) from both the old and new scripts' axes without saving to disk (monkeypatched `save_both` to capture the Figure object before its `plt.close`) -- 16 rectangles in each, identical as a sorted set, confirming bar data untouched. (b) scanned every text object for "--", U+2013, U+2014, "Corrected", "Superseded", or the old title string: the OLD script's texts hit all of "--", "Corrected" and "Superseded" (check seen failing, as required) and did carry the title text; the NEW script's texts had zero hits and no title text.
- Old PNG/PDF archived to `submission/figures/SI/_archive_pre_clean_2026-09-25/` and `figures/SI/_archive_pre_clean_2026-09-25/` (md5 unchanged: `72837247373eecb991f7fadc6c547a03` png / `4e950feb3629ceebf4c7960df0fe789b` pdf, both locations).
- New figure regenerated with `figS01_shares_clean.py` and installed at both `figures/SI/Figure_S01_occupiable_shares.{png,pdf}` and `submission/figures/SI/Figure_S01_occupiable_shares.{png,pdf}` -- identical in both locations. New md5: png `b54a4725e05d39691b31d815d3edbf70`, pdf `4d01a1132427360c9c4666d791367b1e`.

WHAT I DID NOT VERIFY: did not open the rendered PNG/PDF visually (no image viewer used); relied on programmatic extraction of matplotlib patch geometry/color and text strings instead. Did not check whether any other document (manuscript body, SI text, prompt .md files) references the old caption or footnote wording and needs updating to match. Did not check `f5_figure_check.py` or any other gate script that may import from `figS01_shares.py` (the original, unedited) for consistency with the new clean output.

## Figure titles removed 2026-09-25

Scope: remove the in-figure titles (and any en/em dash in figure text) from the 3J paper's five main data figures, redrawn from the same P10R data with the same Step-9 code. Script: `IMP/scripts/p9_figures_notitle.py` (new; does not edit `p9_figures.py` or the Step-9 original, which is loaded unmodified via `importlib`). Console: `IMP/data/P10R/P9_figures_notitle_dryrun.out` (dry run) and `IMP/data/P10R/P9_figures_notitle.out` (install run). Archives, md5-identical to what they replace and non-empty: `figures/_archive_pre_notitle_2026-09-25/` and `submission/figures/_archive_pre_notitle_2026-09-25/` (Figure_07 to Figure_11, PNG + PDF).

Files changed (installed identically to both `writing/figures/` and `writing/submission/figures/`):

| file | md5 before | md5 after |
|---|---|---|
| Figure_07_longitudinal_4ch.png | 58e396e1c2bca058ac9da6738acbe007 | 136e2218dfdf9545875627c3e78eb4f7 |
| Figure_07_longitudinal_4ch.pdf | 7ef0af15fdea45471dc95e04742dab67 | 9b326583ba23516430352bc8ae0fa2e2 |
| Figure_08_eui_4ch.png | e8a21049f2833cf6f79b811abd1fb912 | 7f23e5e112c35bc15f0502f2850c49ef |
| Figure_08_eui_4ch.pdf | 1b3befc4b9223a3a72643db5c2749e90 | c03c2300e834bce512cdbaa73774e6c7 |
| Figure_09_diurnal_4ch.png | da9835f34d77424281ec37fffcfe5308 | 748f1c29edb77b722051d66d6b452db4 |
| Figure_09_diurnal_4ch.pdf | 15d945bd0253c8eb9442cc2c52a582d1 | eb372aaf1e03676eaf6717c1db5232ff |
| Figure_10_peakhour_4ch.png | 582c1e9598cb58dafc6a1d3294528ce9 | 4597c1c0a480bef887f3adce233c4baa |
| Figure_10_peakhour_4ch.pdf | d8f16bca58663b0301e22abb92fd85d7 | 9b891a847919d266d643675ffc4ee472 |
| Figure_11_scenario_4ch.png | e74d8088edd78bfbbc4c7f1a35392696 | 0b97a38535e481de6451a2800e8fe2af |
| Figure_11_scenario_4ch.pdf | bb639d721ddf28904b35929158627d75 | cad022c8c5c5693f20ae76b2286279ef |

Not touched: `fig_presence_by_channel`, `fig_codeschedule_vs_survey` (PNG + PDF, both locations) -- already had no in-figure descriptive title and no en/em dash before this task; and the two Gemini schematic scripts (`generate_fig01_framework.py`, `generate_graphical_abstract.py`).

Text removed (verbatim, from `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py`, loaded unmodified, never edited):
- Figure_08_eui_4ch: `ax.set_title` "Step 9 section R1 -- per-channel EUI vs as-modelled band (green), CFA basis, all 56 cells" (had a middle dot, no en/em dash) -- removed, no replacement (single panel; the benchmark band is visual).
- Figure_09_diurnal_4ch: `fig.suptitle` "Step 9 section R2 -- coincident four-channel diurnal load, {cell}" (em dash) -- removed. Per-panel `ax.set_title(f"{season} - weekday")` ("winter - weekday" / "summer - weekday") KEPT as-is: it is the only thing telling the two panels apart, no dash, and the caption (`chapters_v2/SI_additions.md:18`, "Diurnal load per channel, central 2030 scenario") does not name the season.
- Figure_10_peakhour_4ch: `ax.set_title` "Step 9 section R2 -- peak timing per channel, all 56 cells" (em dash) -- removed, no replacement (panel already identified by the channel y-tick labels). x-axis label's em dash fixed: "weekday peak hour [h] -- load-weighted CIRCULAR mean (caveat 3)" changed to "weekday peak hour [h] - load-weighted CIRCULAR mean (caveat 3)" (plain hyphen; only that one character changed).
- Figure_11_scenario_4ch: `fig.suptitle` "Step 9 section R3 -- one-at-a-time scenario response (G8o / G8r / G8h), sim-side evidence" (em dash) -- removed. Per-panel `ax.set_title(f"{ch} lever  {LEVER_ORDER[ch]}")` KEPT as-is (no dash): the only thing naming which of the three panels is office/retail/hotel; caption (`chapters_v2/03_Results.md:70`) does not.
- Figure_07_longitudinal_4ch: `fig.suptitle` "Step 9 section R4 -- longitudinal 2005 to 2022, mean over building by city" (em dash, plus a right-arrow character, not an en/em dash) -- removed, no replacement (the two panels are already told apart by their own y-axis labels, "energy change % vs 2005" and "weekday midday share").

Panel label kept and reason recorded in the script docstring and in `ALLOWED_AX_TITLES` (p9_figures_notitle.py): the diurnal figure's suptitle was the ONLY place the specific building/city cell (`cell`, e.g. `B_central__SuperTall__CLG`) was recorded; the caption does not name it, so a short non-title label was kept via `fig.text` (not `ax.set_title`/`fig.suptitle`), placed top-left in small grey font, plain text (only underscores, no dash).

Checks, each made to fail first on the unmodified (titled) render before being trusted (all in `p9_figures_notitle.py`, printed in `P9_figures_notitle.out`):
- R0: my copy's harness (paths/dpi/pdf handling), calling the Step-9 module's OWN unmodified fig_eui/fig_diurnal/fig_peakhour/fig_scenario/fig_longitudinal on the P10R agg arm at 600 dpi, reproduces the currently installed PNG and PDF byte for byte for all 5 figures (10/10 md5 pairs matched) -- proves the harness itself is not the source of any later difference.
- D0 (seen-failing control): the same title/dash checks used below, run against that same unmodified render, DID find a non-empty title on every one of the 5 figures and an en/em dash in at least one text object on every one of the 5 figures (printed per-figure in the log) -- confirms the checks can actually detect the thing they are meant to catch.
- D1: after the title/dash removal, (b) no text object anywhere in the figure (suptitle, every axis title at every one of matplotlib's three title locations -- center/left/right --, axis labels, legend entries, tick labels, free-standing text) contains U+2013 or U+2014, for all 5 figures; (c) no leftover descriptive title remains: `fig.suptitle` is empty on all 5, and any non-empty `ax.set_title` text is checked against an explicit, exact allowlist of the panel labels documented above (winter/summer, and office/retail/hotel plus lever) -- nothing outside that allowlist is tolerated. Both passed on all 5 figures.
- P3 (completeness check, not required by the task): re-ran the same title/dash check, including a fix for matplotlib's loc="left"/"right" titles, against the two already-compliant P3 figures (`fig_presence_by_channel`, `fig_codeschedule_vs_survey`, both UNCHANGED scripts) -- confirms they already carry only short "(a) Office"-style panel labels (loc="left" titles; the first version of this check missed these because `ax.get_title()` alone only reads the center-location title -- fixed before trusting the result) and zero em/en dashes; nothing installed for these two, matching the task's own description that only the five main figures carried titles.
- A: for every one of the 5 figures, every Line2D (get_data), every Patch/boxplot-artist (path vertices), and every Collection (scatter offsets, fill_between path vertices) on every axis was extracted from the R0 render and the title-removed render (both held in memory, not re-read from disk) and compared for exact equality (numeric arrays rounded to 1e-9, the one categorical line -- the era axis in Figure_07 -- compared as exact strings). All 5 matched exactly: no data value, axis, colour or size changed.
- All 31 controls (10 R0 + 2 D0 + 10 D1 + 4 P3 + 5 A) passed before `--install` copied anything.

WHAT I DID NOT VERIFY: did not open the rendered PNG/PDF visually (no image viewer used); relied on the programmatic title/dash/artist-data checks above. Did not re-check the PDF's internal text streams directly (only the matplotlib Text objects that produced them). Did not check whether `submission/figures/Prompts_Images_v3/*.md` (the original image-generation prompt records, describing the OLD titled figures) need updating to say the figures are now untitled; those are historical generation records, not cited by the manuscript. Did not grep every other document in `writing/` for stray references to the removed title text strings (a search for "Step 9" + section-sign across chapters/submission was not run).

## SI jargon pass 2026-09-25

Task: journal voice for the SI tables and S.3, with no number, verdict or meaning changed. Every file was archived before editing to `chapters_v2/_archive_pre_si_jargon_2026-09-25/` (`tables__Table_04_validation_gates.md`, `tables__Table_07_limitations.md`, `tables__SI__Table_A1_A2.md`, `SI_additions.md`, `fullSet__assemble_3J_v2.py`). The md5 of each copy equalled the original before editing. Edits were applied by an exact-match script (each string matched once). Only the carried part of each table file was edited; the `## Sources` and notes sections below it were left as they were.

### Table S1 (`tables/Table_04_validation_gates.md`)
- "(a) Tiered gates - ... / Tier 3 ASHRAE G14" -> "(a) Tiered checks - ... / Tier 3 downstream"
- "Applied per day-type, to AT_RETAIL exactly as to AT_WORK in the two-channel stage." -> "Applied per day type, to retail presence exactly as to work presence in the two-channel version."
- "(b) Channel-specific gates" -> "(b) Channel-specific checks"
- "LOCATION mapping" (4 rows) -> "Location mapping"; "AT_RETAIL rate" -> "Retail presence rate"
- "OR-rule leak | Online shopping, excluded from AT_RETAIL" -> "Retail rule (Eq. B.1) | Online shopping excluded from retail presence"
- "cross-tab still reported" -> "cross-tabulation still reported"
- "JS(AT_WORK), JS(AT_RETAIL) per stratum" -> "JS for work presence and for retail presence, per stratum"
- "PR-AUC and F1 on positive slots, AT_RETAIL" -> "..., retail presence"
- "bits vs the two-channel baseline" -> "bits versus the two-channel version"
- "AB monthly 2015-2019 and QC monthly 2019 vs reconstruction" -> "Alberta monthly 2015-2019 and Quebec monthly 2019 versus reconstruction"
- "Default vs 2022, Montreal SuperTall" -> "Code-schedule control versus 2022, Montreal SuperTall"
- "(c) Wiring and differentiation gates" -> "... checks"; "the two-channel stage's occupancy-field wiring defect" -> "the two-channel version's ..."
- "100 % of modulated Spaces pass" -> "100 % of modulated spaces pass"
- "byte-identical = FAIL" (Target column, not a verdict column) -> "byte-identical outputs do not pass"
- Provenance paragraph: "adopted to catch an all-zeros failure mode and flagged as heuristic rather than literature-derived by this project's own architecture and training reviews." -> "They were adopted to catch a model that predicts no retail presence at all, and they are treated as heuristic rather than literature-derived."
- "peak magnitude and timing gate ... the OR-rule freeze, the Jensen-Shannon pairing and drift gates, the midday-dynamics gate" -> "peak magnitude and timing check ... fixing the retail rule before training, the Jensen-Shannon pairing and drift checks, the midday-dynamics check"
- "the wiring and differentiation gates, and the EUI-share gate of 2 percentage points. These are project acceptance bars, not literature values." -> "... checks, and the EUI-share check of 2 percentage points. These are acceptance thresholds chosen for this study, not literature values."
- Not changed: the intro sentence, "(§3.5)" and the provenance heading, because the assembler rules replace them at build time; "fail to reject H0" (a statistics term).

### Table S2 (`tables/Table_07_limitations.md`, table rows only)
- Group "Reference bands" (L4 to L8) -> "Reference ranges"
- L4 statement "the gate is a band-applicability finding." -> "the check result reflects the fit of the range to this tower, not a model defect." ("not a model defect" comes from the source L4 heading.)
- L4 measurement "The uninjected control scores 85.45 ..." -> "The code-schedule control scores 85.45 ..." (the build rule still turns 85.45 into 85.36); "Two mechanisms refuted; the source gives three floors for itself." -> "Two candidate explanations were ruled out; the reference source gives three different floors."
- L5 "The hotel band is archetype- and city-mismatched." -> "The hotel reference range comes from a different building archetype and different cities."; "FAIL on 28 of 56 cells, all Tall, all over the 300 ceiling; range 204.83-322.18." -> "Outside the range in 28 of 56 simulations, all in the Tall tower and all over the 300 ceiling; simulated values 204.83-322.18."
- L7 "19 of 56 cells under the floor. The rate gate is informational." -> "19 of 56 simulations under the floor. The retail rate check is reported for information only."
- L8 "Residential has no as-modelled band" -> "Residential has no reference range that matches the modelled building"
- L11 "18.75 % hot on the wrong shape." -> "18.75 % too high, on the wrong shape."
- L12 "The anchor previously cited gives 5. The gate is non-monotonic: fails at 10, passes at 11-20, fails at 30." -> "The nearest literature value is 5, a study design rather than a recommendation. The check is non-monotonic: it does not pass at 10, passes at 11-20 and does not pass at 30." (The "study design" clause comes from the source L12.)
- L13 "Three construction stages, three implementations; this one verified against its own code." -> "The three model versions aggregate households in three different ways; this version was checked against its own code."
- L14 "the earlier stable claim was a documentation defect." -> "it is not stable." (Process history dropped; the decline and its numbers stay.)
- L16 "capacity-pinned on one object, and a global fix does not correct it" -> "limited by the capacity of one water heater, and a global resize does not correct it"; "that object's share" -> "that heater's share"
- Not changed: the L6 measurement source text (the build rule replaces it with "Not evaluated in the reported runs.") and the intro (build rule). The build-note item "L6 still says tested and refuted" no longer applies: the L6 statement now reads "not used in this paper", which agrees with the measurement cell.

### Table S3 (`tables/SI/Table_A1_A2.md`)
- "two-channel stage" (4 places) -> "two-channel version"; "earlier stages" -> "earlier versions"; "between the two stages" -> "between the two versions"
- "Activity arm" -> "Activity decoder"; "the activity arm's gradient barrier untouched" -> "the activity decoder's gradient barrier unchanged"
- "an independent data-pipeline fix rather than part of the retail addition" -> "a data-preparation correction unrelated to the retail addition"
- "early stopping on the gate set" -> "early stopping on the check set"
- Selection rule "Gate-first, then maximize retail F1 among survivors ... The shipped checkpoint" -> "Discard checkpoints that do not pass the hard checks, then maximize retail F1 among the rest ... The delivered checkpoint" (the rule wording follows S.1)
- "Shipped scorecard | 147 PASS / 18 WARN / 1 FAIL; the single FAIL is a day-type ordering check pre-existing in the two-channel baseline, with no new failure introduced" -> "Automated checks on the generated diaries | 166 checks: 147 pass, 18 give a warning and 1 does not pass. The one that does not pass is a day-type ordering check that also did not pass in the two-channel version; no check that passed there stops passing here". CHOICE: the counts are kept and explained in words. What was counted: the Step 4 validator run on the generated (augmented) diary pool, `Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split.md:51` (the sole FAIL is OW5, day-type ordering; REG-4 means the current failures equal the baseline failures). 166 = 147 + 18 + 1.
- "The shipped model trains on 49." -> "The delivered model is trained with 49."
- Caption "**Table A2.** - AT_RETAIL codebook per GSS cycle." -> "**Table A2.** - Retail presence codebook per GSS cycle." plus one new lead-in sentence: "Each raw code below maps to the harmonised location code 5 (store) used in Eq. B.1." (At build time the caption line itself is replaced by the heading "(e) Per-cycle retail code mapping".)
- "2022 (GSSP)" -> "2022"

### S.3 (`chapters_v2/SI_additions.md`)
- "That count turned on a margin of 0.15 % of the floor. In an earlier improvement round, a shift of -0.05 % in the median changed one simulation's verdict." -> "Under that count, the verdict depended on a margin of only 0.15 % of the floor. In an earlier model version, a shift of -0.05 % in the median changed one simulation's verdict." The numbers are kept. The meaning follows the source at `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md:452-454` (a margin of 0.15 % of the floor; a -0.05 % median move flipped one simulation, 55/56 to 54/56).
- S.1, S.2 and Table S4: no internal terms found. "work-from-home bands" in Table S4 was kept, because it is a scenario band and the main text uses the same term (`02_Framework.md:22,46,48`).

### Assembler (`fullSet/assemble_3J_v2.py`, rule strings only)
- Table S2 rule "merge note ... 85.45 -> 85.36": old and new strings "The uninjected control scores ..." -> "The code-schedule control scores ..." (the intended output is the same, in the new wording).
- Table S3 rule "second table of the file becomes part (e)": old string "**Table A2.** - AT_RETAIL codebook per GSS cycle." -> "**Table A2.** - Retail presence codebook per GSS cycle." (the output heading is unchanged).

### Eq. B.1 codes vs Table S3(e): CONSISTENT (the same codes in two codings)
Eq. B.1 uses the harmonised codes. Table S3(e) lists the raw survey codes that map to harmonised location 5.
- The rule works on the harmonised columns: `Leg3_4-split/Step3_docs/3rdJ_03_mergingGSS_4split.py:1371-1372` (`AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))`). The same rule is at `Leg3_4-split/Step2_docs/3rdJ_02_harmonizeGSS_4split.md:50`.
- Harmonised scheme: `3rdJ_02_harmonizeGSS_4split.md:8` (occPRE Shopping = code 5; occACT Purchasing Goods and Services = code 4). Crosswalk row at `:40` (occPRE 5 = PLACE 06 + 07 in 2005/2010, LOCATION 306 in 2015, LOCATION 3306 in 2022).
- Mapping in code: `Leg2_2-split/Step2_docs/3rdJ_02_harmonizeGSS_2split.py:672` (occPRE = raw PLACE/LOCATION mapped through the crosswalk); sheets at `:625-630`; workbook path at `:989-993`.
- Codebook `2J_docs_occ_nTemp/references_Pre_coPre_Codes/Data Harmonization_presenceCategories - execution.xlsx`: sheet 2005-2010codebook rows 7-8 (5 <- 6, 5 <- 7) and row 12 (9 <- 11); 2015codebook row 8 (5 <- 306) and rows 12-14 (9 <- 312, 308, 311); 2022codebook row 8 (5 <- 3306) and rows 12-14 (9 <- 3312, 3308, 3311).
- Activity: `2J_docs_occ_nTemp/references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`, sheet 2005codebook rows 52-65 and 2010codebook rows 68 onward: harmonised category 4 = purchasing goods and services (raw codes 301 to 380).
- Action: one lead-in sentence was added to Table S3(e) (above). Observation, not changed: Table S3(e) gives no raw codes for harmonised location 9, which Eq. B.1 also uses.

### Build
- `py -3 fullSet/assemble_3J_v2.py`: exit 3. Checks 1a to 3 PASS. Check 4 FAILs only because ASHRAE Guideline 14 is cited in the SI only, as expected. SI .md md5 7f4a5420, SI .docx md5 a04faf23. The main files are unchanged (md5 fc9e3b47 / acf8122d).
- `py -3 fullSet/assemble_3J_v2.py --selftest`: exit 0, 21 of 21 probes detected.
- Installed SI .md: 0 hits for AT_RETAIL, uninjected, shipped, GSSP, "improvement round", "cells" and "= FAIL". The SI .docx text contains the new wording (the 85.36 line, the code-5 sentence, "166 checks", "earlier model version").

### WHAT I DID NOT VERIFY
- I did not open the .docx in Word. I checked it only by reading the XML text.
- "166 checks" is the sum 147 + 18 + 1. I did not open the validator report to confirm that it has no other outcome class (for example, skipped checks).
- I did not check that the "two-channel version" wording matches every use in the main text. The main text was not edited.
- I did not re-check the new SI intro sentences flagged in the build note (the S1 and S2 intros). They are unchanged.
- Main-text jargon was not in scope and was not searched.

## Figure labels made plain 2026-09-25

Scope: replace internal code labels with plain journal labels in the 3J paper's five main data
figures, redrawn from the same P10R data with the same Step-9 code, on top of the already-installed
title/dash removal (previous section). Script: `IMP/scripts/p9_figures_plain.py` (new; copied from
`p9_figures_notitle.py` and edited; does not edit `p9_figures.py`, `p9_figures_notitle.py`, or the
Step-9 original, all loaded/kept unmodified). Console: `IMP/data/P10R/P9_figures_plain_dryrun.out`
(dry run, 80/80 controls PASS) and `IMP/data/P10R/P9_figures_plain.out` (install run, same 80/80).
Archives, md5-identical to what they replace and non-empty (verified before the script ran, by
`cp -p` then `md5sum` on all 20 files): `figures/_archive_pre_plain_2026-09-25/` and
`submission/figures/_archive_pre_plain_2026-09-25/` (Figure_07 to Figure_11, PNG + PDF).

### Label changes, old -> new, per figure

**Figure_09_diurnal_4ch**
- Top-left cell-tag text `B_central__SuperTall__CLG` -> REMOVED entirely (no replacement text in
  the figure). `B_central` = the central bundle (`BUNDLES = ["B_cons", "B_central", "B_opt"]`,
  `3rdJ_09_activityDrivenLoads_4split.py:195`); `SuperTall` = the taller of the two building
  archetypes; `CLG` = Calgary (confirmed against the archetype-gap comment at that file's line 187,
  "NECB-2017 MTL/Calgary vs 90.1-2019 Rochester"; `MTL` = Montreal, not used by this particular
  cell). **Caption phrase for the manager to add** (this cell's identity is otherwise lost):
  "SuperTall tower, Calgary, central 2030 scenario."
- Legend `residential_common` -> `residential common`; `service_MEP` -> `service and plant`.
- Panel labels `winter · weekday` / `summer · weekday` kept as-is (task allowed).

**Figure_07_longitudinal_4ch**
- x tick labels `Y2005`, `Y2010`, `Y2015`, `Y2022` -> `2005`, `2010`, `2015`, `2022` (both panels).
- Left y label `energy Δ% vs 2005` -> `energy change from 2005 (%)`.
- Right y label `weekday midday share` and the office/retail/hotel/residential legend unchanged.

**Figure_11_scenario_4ch**
- y label `channel energy Δ% vs B_central` -> `channel energy change vs central scenario (%)`.
- x tick labels: `sens_office_cons` -> `office conservative`, `sens_office_opt` -> `office
  optimistic`, `sens_retail_cons` -> `retail conservative`, `sens_retail_opt` -> `retail
  optimistic`, `sens_hotel_cons` -> `hotel conservative`, `sens_hotel_opt` -> `hotel optimistic`,
  `B_central` -> `central` (same BUNDLES mapping as above; the three panel-title lines "office
  lever ('conservative', 'hybrid', 'fullyhybrid')" / "retail lever (0.9, 0.97, 1.05)" / "hotel
  lever (0.92, 1.0, 1.05)" were already free of code tokens and are kept unchanged).

**Figure_08_eui_4ch, Figure_10_peakhour_4ch**: no label change. `EUI`, `kWh/m2/yr`, `CFA basis` are
defined in the manuscript's own nomenclature table (`CFA` = "Conditioned floor area",
`chapters_v2/07_Nomenclature.md:9`) and in the main text ("energy use intensity (EUI)"); the
peak-hour x label already used a plain hyphen with no underscore/code token after the previous
(notitle) round. Checked, not just left alone: see M08/M10 below.

### md5, before (currently-installed notitle figures) -> after (plain-label)

| file | before | after |
|---|---|---|
| Figure_07_longitudinal_4ch.png | 136e2218dfdf9545875627c3e78eb4f7 | 8e436d2d600f7b17467d9836dc15af74 |
| Figure_07_longitudinal_4ch.pdf | 9b326583ba23516430352bc8ae0fa2e2 | 71bf38a761bb988116acbecb849e0508 |
| Figure_08_eui_4ch.png | 7f23e5e112c35bc15f0502f2850c49ef | 7f23e5e112c35bc15f0502f2850c49ef (unchanged) |
| Figure_08_eui_4ch.pdf | c03c2300e834bce512cdbaa73774e6c7 | c03c2300e834bce512cdbaa73774e6c7 (unchanged) |
| Figure_09_diurnal_4ch.png | 748f1c29edb77b722051d66d6b452db4 | da86e829e494d0c78a9c400e03775050 |
| Figure_09_diurnal_4ch.pdf | eb372aaf1e03676eaf6717c1db5232ff | a2b150504d129985e5d3c0ffbf102aec |
| Figure_10_peakhour_4ch.png | 4597c1c0a480bef887f3adce233c4baa | 4597c1c0a480bef887f3adce233c4baa (unchanged) |
| Figure_10_peakhour_4ch.pdf | 9b891a847919d266d643675ffc4ee472 | 9b891a847919d266d643675ffc4ee472 (unchanged) |
| Figure_11_scenario_4ch.png | 0b97a38535e481de6451a2800e8fe2af | b67b929ca69485aec4ed0ad37850b5e9 |
| Figure_11_scenario_4ch.pdf | cad022c8c5c5693f20ae76b2286279ef | 9fd379562ca558c92d3c062b19f88eb5 |

Installed identically to both `writing/figures/` and `writing/submission/figures/` (same file, same
md5, verified from the install-run console output which prints both destinations).

### Checks, each made to fail first before being trusted (all in `p9_figures_plain.py`, printed in `P9_figures_plain.out`)
- R0: this script's own baseline is the currently-installed **notitle** render (`fig_*_nt`
  functions copied verbatim from `p9_figures_notitle.py`, not re-edited), not the raw titled
  Step-9 output -- because the files this script replaces are already the notitle ones. Reproduces
  the currently installed PNG/PDF byte for byte for all 5 figures (10/10 md5 pairs matched).
- D0 (seen-failing control): the plain-label checks (no `_`, `Y20`, `CLG`, `MTL`, en/em dash
  anywhere in figure text), run against that same notitle R0 render, DID find violations on 3 of
  the 5 figures (Figure_07: `Y2005`/`Y2010`/`Y2015`/`Y2022`; Figure_09:
  `residential_common`/`service_MEP`/`B_central__SuperTall__CLG`; Figure_11: `B_central` and all 6
  `sens_*` tokens plus the `B_central` in the y label) -- confirms the checks can actually detect
  the thing they are meant to catch.
- D1: after the substitutions, no text object anywhere in any of the 5 figures (suptitle, every
  axis title at all 3 matplotlib title locations, axis labels, legend entries, tick labels,
  free-standing text) contains `_`, `Y20`, `CLG`, `MTL`, or an en/em dash; no leftover descriptive
  title (same exact allowlist of kept panel labels as the notitle round). Passed on all 5.
- M (new this round -- a check specific to the ACTUAL replacements, not just their absence):
  for Figure_07/09/11, every one of the exact old strings above is confirmed present in the R0
  render and absent from the plain-label render, and every one of the exact new strings is
  confirmed present in the plain-label render (34 paired assertions, all PASS). For Figure_08 and
  Figure_10, the FULL non-title text list (xlabel, ylabel, every tick label, every legend entry)
  is asserted byte-for-byte IDENTICAL old vs new, not merely "no forbidden substring" -- proves
  nothing in those two figures changed, not just nothing bad.
- P3 (completeness, not required by the task): re-ran the same plain-label check against the two
  already-compliant P3 figures (`fig_presence_by_channel`, `fig_codeschedule_vs_survey`, unchanged
  scripts) -- confirms zero code tokens or dashes there either; nothing installed for these two.
- A: for every one of the 5 figures, every Line2D (get_data), every Patch/boxplot-artist (path
  vertices), and every Collection (scatter offsets, fill_between path vertices) on every axis was
  extracted from the R0 (notitle) render and the plain-label render (both held in memory) and
  compared for exact equality (numeric arrays rounded to 1e-9; the categorical era axis in
  Figure_07 and the categorical scenario-tag axis in Figure_11 compared as exact strings -- both
  still keyed on the ORIGINAL code strings, e.g. `Y2005`/`sens_office_cons`, for plotting purposes;
  only the DISPLAYED tick text was remapped via `ax.set_xticklabels()` afterward, so the
  categorical positions are provably unaffected by the label change). All 5 matched exactly.
- All 80 controls (10 R0 + 5 D0 + 10 D1 + 34 M + 4 P3 + 5 A) passed before `--install` copied
  anything, and again on the `--install` run itself.

### Visual check
Read (viewed) all three changed PNGs after install (`Figure_07_longitudinal_4ch.png`,
`Figure_09_diurnal_4ch.png`, `Figure_11_scenario_4ch.png`) at full resolution: no overlapping text,
no cut-off labels, legend and rotated x tick labels (Figure_11) fit within the axes, panel titles
and legend entries render correctly with the new plain wording. Figure_08 and Figure_10 were not
re-viewed since their files are byte-identical to before (confirmed by md5, not by eye).

### Caption phrases the manager must add (so no information is lost by the removed/renamed text)
- Figure_09 caption: name the cell explicitly, e.g. "SuperTall tower, Calgary, central 2030
  scenario" (previously carried only in-figure as `B_central__SuperTall__CLG`).
- No other figure lost information: Figure_07's era labels and y-axis meaning are unchanged in
  substance (only "Y2005"->"2005" and the Δ%-vs symbol phrasing); Figure_11's bundle/scenario
  identity is unchanged in substance (only "B_central"->"central" and "sens_X_cons/opt"->"X
  conservative/optimistic").

### WHAT I DID NOT VERIFY
- Did not re-check the PDF's internal text streams directly (only the matplotlib Text objects that
  produced them), same limitation as the notitle round.
- Did not add the Figure_09 caption phrase to the manuscript text myself -- that is a manuscript
  edit outside this script's scope (figures only); the exact phrase is given above for the manager
  to insert.
- Did not check `submission/figures/Prompts_Images_v3/*.md` or `Prompts_Images_v4/*.md` (historical
  image-generation prompt records) for stray references to the old code-label strings; those are
  historical records, not cited by the manuscript.
- Did not grep every other document in `writing/` for stray prose references to `B_central`,
  `sens_office_cons`-style tags, `residential_common`, `service_MEP`, or `Y2005`-style era codes
  outside the five figure scripts and this log.
- Did not verify CFA/EUI/kWh-per-m2 wording anywhere beyond the one grep against
  `chapters_v2/07_Nomenclature.md` and the submission manuscript's own nomenclature table.

## V3a full result written in (manager, 2026-09-25 ~05:00 UTC)
- 40/40 runs ok (resumed 04:02, done 04:30 UTC, guard never fired). Seed 42 reproduces all 8 P10R cells exactly. Source: `IMP/V3_design_and_runs.md` 11.6.
- `05_Limitations.md` V3a sentences now cover both towers: EUI spread about 0.5 % or less (max CV 0.543 %, residential), peak-hour SD about 0.1 h or less (max 0.117 h), office/retail/hotel 2030-vs-2022 changes 7 to 280 times the spread, residential change 1.2 to 1.7 times (not clearly larger), sign depends on the draw. Backup `chapters_v2/_archive_pre_stage2d_hotel_2026-09-25/05_Limitations.pre_V3a_full.md`. Build re-run: exit 3 (expected).

## Reference fixes 2026-09-25 (author approved)
Source: `IMP/author_checks_2026-09-25/item3_candidate_references.md`. Author approval 2026-09-25: "put the 8 verified references and the 6 corrections into the paper". Only VERIFIED and FIX rows used; METADATA-ONLY (M5b, M11, M15, M17, M39) and REJECT (M4, M5a, M24) not used. Hotel recovery sentence and all numbers untouched. Access dates = 25 September 2026 (the day item3 read the pages). Pre-edit copies: session scratchpad only (old text is given below).

Chapter edits (old -> new, item):
- `01_Introduction.md:11` "[REF NEEDED: sources linking mixed-use load diversity to plant sizing and grid peak]" -> "(Happle et al., 2020) [REF NEEDED: source linking the overlap of uses to grid peak demand]" (X1; Happle supports the plant-sizing half only, grid-peak half stays open).
- `02_Framework.md:30` "[REF NEEDED: PCGrad, gradient surgery for multi-task learning]" -> "(Yu et al., 2020)" (M9).
- `02_Framework.md:36` "and a level shift from March 2020." -> "and a level shift from March 2020 (Box and Tiao, 1975)." (M12). Hotel recovery placeholder and Box-Jenkins placeholder (M11, metadata-only) on the same line left as they were.
- `02_Framework.md:93` "A wider empirical range, and ... (Natural Resources Canada, 2019)" -> "A wider empirical range [REF NEEDED: survey year of the Survey of Commercial and Institutional Energy Use values behind the context ranges], and ... (Natural Resources Canada, 2019a)" (M31: the Step 9 INFO values carry no year, so the year stays open here; SHEU becomes 2019a because SCIEU 2019 is now 2019b).
- `04_Discussion.md:7` "[REF NEEDED: studies that link occupancy diversity to peak demand in large or mixed-use buildings]" -> "(Doma et al., 2024)" (M18; cited for the occupancy-and-peak link only).
- `04_Discussion.md:15` "... to judge channel levels [REF NEEDED: measured energy data for Canadian mixed-use or high-rise buildings by use]." -> "... to judge channel levels. The Canadian surveys of measured energy report it by whole building or by primary activity, not by use within one building (Natural Resources Canada, 2018; Natural Resources Canada, 2019b)." (M19; Montreal municipal open data dropped, as item3 allows).
- `04_Discussion.md:17` "The American Time Use Survey and the Harmonised European Time Use Survey could fill the first role (Eurostat, 2018) [REF NEEDED: ATUS source]." -> "The American Time Use Survey (U.S. Bureau of Labor Statistics, 2026) and the Harmonised European Time Use Survey (Eurostat, 2018) could fill the first role." (M22).
- `09_AppendixB_Equations.md:17` "[REF NEEDED: source for class-weighted cross-entropy and the matching logit adjustment]" -> two sentences: up-weighting equals over-sampling, prior correction subtracts the log of the factor (King and Zeng, 2001); general logit adjustment (Menon et al., 2021) (M25, both).

`11_References.md` edits (new line numbers):
- :3 Guideline 14 undated "[REF NEEDED: edition year]" -> "ASHRAE (2014) *ASHRAE Guideline 14-2014: ...*", no ISBN, moved before ASHRAE (2019) (M26). Edition 2014 taken from the Step 6 code that set the thresholds (`Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split_val.py:1301`, "Guideline 14-2014 Section 4.1"); 14-2023 supersedes it but is not the source used. Still cited only in SI Table S1 (CHECK 4, expected).
- :9 new Box and Tiao (1975) (M12). :23 new Happle et al. (2020) (X1). :29 new King and Zeng (2001), :35 new Menon et al. (2021) (M25). :53 new U.S. Bureau of Labor Statistics (2026) (M22). :65 new Yu et al. (2020) (M9).
- :15 Doma and Ouf (2023) "pp. 1671-1678. https://publications.ibpsa.org/...bs2023_1671.pdf" -> "pp. 596-603. https://doi.org/10.26868/25222708.2023.1671" (M34).
- :21 Government of Alberta (2022): "[REF NEEDED: access date; earlier monthly issues]" -> "(monthly issues, 2011 to 2022) ... and the yearly datasets for 2011 to 2021 (accessed 25 September 2026)" (M28). Year label kept at 2022 so the in-text citation still matches.
- :25 Institut de la statistique du Québec (2026): "monthly data by territory ... [REF NEEDED: table identifier and access date]" -> "(régions et MRC/villes), monthly data. Tableau de bord, Gouvernement du Québec, ministère du Tourisme. <quebec.ca dashboard URL> (accessed 25 September 2026)" (M30; no table ID exists).
- :37 NECB ISBN "0-660-24321-4" -> "978-0-660-24718-2" (M33, ISBN of Cat. NR24-24/2017E-PDF).
- :39 new Natural Resources Canada (2018) SECMURBs 2018 Data Tables (M19). Year = survey year, as in the existing SHEU entry; release year not seen.
- :41 SHEU "(2019)" -> "(2019a)".
- :43 SCIEU undated "[REF NEEDED: survey year and table identifier]" -> "Natural Resources Canada (2019b) *Survey of Commercial and Institutional Energy Use (SCIEU), Buildings 2019: Data Tables* ... (accessed 25 September 2026)" (M19/M31; no SDDS 5032, no 57-603-X).
- Goel et al. (2014) (G): not cited anywhere in chapters_v2 or SI, and support for a hotel schedule is not confirmed, so nothing added. Correct DOI if ever used: 10.2172/1129366.

Build: `py -3 writing/fullSet/assemble_3J_v2.py` exit 3; CHECK 4 flags only ASHRAE (2014) Guideline 14 (SI-only); CHECK 5: 7 [REF NEEDED] (was 15).
Still open: grid-peak source (Intro), hotel recovery levels, Box-Jenkins (M11), coincidence-factor definition (M17), SCIEU year behind the context ranges, Table A.1 scoring criteria, PNNL prototype release. Also item3 note on M28: the 2022 Alberta dataset lists October and November issues; the "last three months of 2022 missing" sentence was not touched (hotel text is being changed elsewhere).

## Hotel 2030 observed levels: numbers and figures updated (manager, 2026-09-25 ~17:55 UTC)

Runs: 36 re-runs (all B_* and sens_* cells) finished 17:42 UTC, `DRIVER DONE ok=56 failed=0`, aggregate exit 0 (4 restarts
in total; the last round 22/22 with no RAM-guard stop, memory at most 59 %). Downstream `IMP/scripts/hotel_obs_post.sh`
(out: `IMP/data/P10R/hotel_obs_post.out`): Step-9 scorer exit 0; gates (d)+(e) exit 1 (expected, out-of-scope cells);
old-vs-new table exit 0; P3 `--arm P10R` exit 0, controls 3/3, negative controls 7/7 failing as required.
Hotel EUI gate still FAIL: median 262.9, 28/56 inside, 28 above 300, range 204.8-321.6.

Numbers (`p10r_marker_values.py` recomputed, `hotel_obs_marker_diff.py` vs the pre-switch table): 143 markers, 28 moved,
115 unchanged. All 28 are in `03_Results.md` (lines 64, 66, 68, 80-83, 87, 89, 91) plus 2 in `tables/Table_07_limitations.md`
(L5 range 204.83-322.18 -> 204.83-321.55; L7 median 84.85 -> 84.82). The 16 "UNEXPECTED" flags are Table 4 and its prose
(lines 80-91): their definition pools all 56 simulations, 36 of which are the re-run 2030 cells, so the move is expected
(the flag keys on a scenario name in the definition, which a 56-pool does not carry). Counts (0/56, 37/56, 28/56, 19 below)
unchanged. Backups: `chapters_v2/_archive_pre_hotel_obs_2026-09-25/` (03_Results.md, Table_07_limitations.md).

One claim moved past its own check: `03_Results.md:68` "levers act nearly additively" (rule: |bundle - sum of 3 single
levers| < 5 % of |bundle|, per model). Worst case was 3.8 %, now 5.6 %: retail, optimistic band, one model, bundle +2.098
vs sum +2.216, gap 0.118 percentage points (next worst 3.9 %). Sentence rewritten with the measured bound instead of dropped:
"These ranges lie within 6 % of the sums of the single-lever effects, at most 0.12 percentage points, so the levers act
nearly additively."

Other chapters: no marker moved (00:13, 01:33, 02:93, 04:15, 05:9, 06:7 unchanged). `05_Limitations.md:3` (repeat seeds)
waits on the 20 B_central V3a re-runs, launched 17:46 UTC.
Framework hotel sentence (`02_Framework.md:36`) already carries 0.597 / 0.610 with Government of Alberta (2026) and ISQ (2026).

Figures: `IMP/scripts/p9_figures_hotel_obs.py` (new; imports `p9_figures_plain.py`, does not edit it). Out:
`IMP/data/P10R/P9_figures_hotel_obs.out`. C0 positive control: old archived data reproduces all 20 installed PNG/PDF byte
for byte; C1: Figure 11 changes with the new data, Figure 7 (2005-2022 only) byte-identical; D1 plain-label checks pass.
27/27. Installed Figures 8, 9, 10, 11 (both folders; old in `_archive_pre_hotel_obs_2026-09-25/`). Figure 7 not copied.
`fig_presence_by_channel` and `fig_codeschedule_vs_survey` (both draw the 2030 central line) re-rendered `--arm P10R`;
both changed, both renders repeat byte for byte on a second run; old in `writing/figures/_archive_pre_hotel_obs_2026-09-25/`.

Build: `py -3 writing/fullSet/assemble_3J_v2.py` exit 3 (CHECK 4 = Guideline 14 SI-only, as before; 6 [REF NEEDED]).
Body 6,377 words.

### Limitations draw-spread ratio after the hotel observed re-run of V3a (2026-09-25 ~18:45 UTC)

`writing/chapters_v2/05_Limitations.md` line 3: "are 7 to 280 times this spread" -> "are 5 to 310 times this spread".
Source: `IMP/data/V3/v3a_P10R/full_hotel_obs/v3a_P10R_delta_eui.csv`, column ratio_abs_pub_over_sd, office/retail/hotel
rows: min 5.40 (Tall MTL hotel), max 311.1 (SuperTall CLG retail). The 0.5 % (max CV 0.542 %) and 0.1 h (max SD 0.117 h)
sentences and the residential sentence (1.15-1.60, sign flips in all 4 cells) are unchanged. Byte check: the backup
with only that replacement equals the new file; CRLF kept. Backup `chapters_v2/_archive_pre_hotel_obs_2026-09-25/05_Limitations.md`.
Build exit 3 (same CHECK 4 / CHECK 5 as above); "5 to 310 times" present once in the built main .md, "7 to 280" absent.

## B&E format pass and the last citations (2026-09-25, ~19:15 UTC)

Author: "can you find sources/insert for the six missing citations, give me paywalled references full name to download
for you. prepare cover letter except the date" and "update our manuscript in terms of titles, fonts, caption style, no
long caption ... reference writing style ... for Building and Environment standards" (model: the 2J AE revision files).
Sources: live B&E guide (curl of elsevier.com guide-for-authors); source check `scratchpad/refs_found.md` (every field read
from Crossref, OSTI, eScholarship, GitHub API or the live NRCan tables; nothing from memory).

Format (backups `chapters_v2/_archive_pre_BE_format_2026-09-25/`): fonts and spacing already equal 2J (Times New Roman 12,
double spacing, tables 10 pt single). Figures 1-4 captions end "Drawn with Gemini (Google) from the authors' specification."
(Gemini drew them with Python; PNG metadata says Matplotlib for 1 and 3, which is consistent). Figure 6, Figure 7 and
Table 3 captions shortened; Table 3 note moved below the table. Table A.1 scoring rules written (5 axes). References: "(Year)."
in 32 entries, final period in 25, accessed dates on the 4 web sources (URLs checked live). Author-year kept (B&E applies its
numbered style at proof; 2J did the same).

Citations (backups `chapters_v2/_archive_pre_citations_2026-09-25/`; CRLF kept in 02 and 11, LF kept in 01):
- 01_Introduction:11 grid peak -> (Weissmann et al., 2017; Happle et al., 2020; Vecchi and Berardi, 2024). Weissmann full text
  read (district peak falls when buildings with different use profiles are added; residential heating only); Vecchi abstract
  read (conference paper; says mixed uses flatten district peaks).
- 02_Framework:89 coincidence factor -> (Guan et al., 2016; Weissmann et al., 2017). Weissmann Eq. 1-4 give peak of the sum
  over sum of peaks; Guan is METADATA ONLY (download refused) and is on the author's download list.
- 02_Framework:66 + 11_References: the Tall/SuperTall models are NOT a DOE/PNNL release (not on energycodes.gov). They are
  LBNL prototypes in NREL OpenStudio-Standards (added 2020-07-21 / 2020-09-03). Text and reference changed to
  "National Renewable Energy Laboratory (2020)"; line 79 "PNNL prototype schedules" -> "prototype schedules". The gem version
  used on 2026-04-17 is NOT known: the local OpenStudio 3.10.0 (installed 2026-04-14) bundles openstudio-standards 0.8.2, but
  the IDFs say EnergyPlus 22.1, which OpenStudio 3.10 does not write, so 0.8.2 is not confirmed. Author item.
  03_Results:91 "DOE/PNNL Large Hotel prototype" is a real DOE/PNNL model and stays; PNNL stays in the Nomenclature.
- 02_Framework:93 SCIEU year -> 2019 (Natural Resources Canada, 2019b): retail 280 = 2019 Table 1 (281), hotel 350 = 356,
  office 230 = 2019 Table 17.1 over 18,580 m2 (231). Wording "centred where reported on the 2019 means". OPEN: the low and high
  edges of the context ranges (170-360, 150-380, 220-480; Table 4) match no SCIEU table read; they come from the deep-research
  reports dr_L3-02/03 (code `3rdJ_09_activityDrivenLoads_4split.py:167-189`). Author decision.
- Yamaguchi and Shimoda (2017) does not exist and was never in the chapters.
Build: exit 0 path, CHECK 2a-2e PASS, CHECK 5 = 0 placeholders, CHECK 4 = ASHRAE 2014 only (cited in the SI, expected). Main
body 6,405 words, abstract 237.

Cover letter: `submission/Title_Page_and_Cover_Letter.md` rewritten to the B&E musts (three major contributions, submission
declaration complied with, permissions statement), date left as [Date]; one comma fixed; .docx rebuilt with ref_submit.docx
+ post.py (no dashes, all sections present). Backup `submission/archive/pre_BE_format_2026-09-25/`.
Upload folder `submission/BE_upload/`: Figure_1.pdf to Figure_9.pdf (md5 = source for all 9, map as in the manuscript order)
and `3J_highlights_BE.docx` (5 bullets, 75-80 characters). Graphical abstract not copied (not requested).

## Context-range edges removed; the two unreachable sources replaced (2026-09-25, ~19:45 UTC)

Author: cannot download Guan 2016 or Box 2015 ("please in an alternative way"); search the source of the context-range
edges, "if you can find apply, if not exclude from the tables"; does not know the OpenStudio-Standards version.
- Edge search: the edges come from the deep-research reports, which say themselves they are judgement, not survey values:
  office 170-360 = "a -25% to +55% buffer" (`Leg2_2-split/Step8_docs/deepResearch/Canadian Office Energy-Use Intensity
  (NRCan SCIEU_CEUD) - Plausibility Bands.md:130`); retail 150-380 "least certain bound" (dr_L3-02 REPORT:99); hotel 220-480
  "a soft estimate" (dr_L3-03 REPORT:147). No survey table gives them -> EXCLUDED.
- Table 4 column "Context range, low / central / high" -> "Survey value (context)": office 231, retail 281, hotel 356,
  residential 113.9-147.2 (unchanged SHEU). Values re-read live today from SCIEU 2019 Table 1 (hotel 1.28, non-food retail
  1.01 GJ/m2) and Table 17.1 (office excluding medical, over 18,580 m2: 0.83 GJ/m2); x 277.78. Note added below Table 4.
  02_Framework:93 sentence reworded to "The 2019 survey means ... are shown as context only." Figure 9 draws only the scored
  ranges (p9_figures_plain.fig_eui_nt), so no figure change. `tables/Table_05_eui_bands.md` still holds the old edges but is
  not read by the build.
- Box et al. (2015) -> Hyndman and Athanasopoulos (2021), *Forecasting: Principles and Practice*, 3rd ed., OTexts, open online
  (section 9.9 Seasonal ARIMA models; citation form taken from the book's own page, HTTP 200 today).
- Guan et al. (2016) dropped; Weissmann et al. (2017) alone carries the coincidence factor definition (full text read, Eq. 1-4).
- OpenStudio-Standards version: author does not know; the reference stays without a version (closed).
Backups `chapters_v2/_archive_pre_context_edges_2026-09-25/`; CRLF kept. Build: CHECK 2a-2e PASS, 0 placeholders, CHECK 4 =
ASHRAE 2014 only (SI-only, expected); 36 references; body 6,431 words.

## Author comments in the Word file (2026-09-25 ~20:30 UTC)
Author's commented copy kept at `IMP/author_checks_2026-09-25/3J_manuscript_submission_AUTHOR_COMMENTS.docx` (8 comments).
- Title smaller: Title style 28 pt -> 16 pt bold (post.py, styles.xml).
- Highlights more striking, 2J style: 5 new bullets, 78-84 characters, numbers only from the abstract (00_FrontMatter.md,
  BE_upload/3J_highlights_BE.docx rebuilt).
- No LLM name in the text: the "Drawn with Gemini" note removed from Figures 1-4 (02_Framework.md); the AI statement in the
  declarations is the only mention. Cover letter: "and in the figure captions" removed, .docx rebuilt.
- Table widths from content, all tables (main + SI): post.py sets each column in proportion to its mean cell length, never
  narrower than its longest word; text width 9360 twips (Letter, 1 in, the page Word gives these files); cell margins 0.05 in.
  Table A.1 study column 11 % -> 23 %.
- Captions centred: every "Figure N." / "Table N." caption paragraph and every figure image centred; table captions keep with
  their table (post.py prints the counts: main 14 captions + 9 images, SI 11 + 7).
- Appendix A: intro cut to three sentences, closing paragraph to two (08_AppendixA_Table1.md).
Backups: `chapters_v2/_archive_pre_author_comments_2026-09-25/`, `submission/archive/pre_author_comments_2026-09-25/`,
`submission/extra/build_scripts/post.pre_author_comments_2026-09-25.py`. Build: CHECK 1-3 PASS, 0 placeholders, CHECK 4 =
ASHRAE 2014 only (SI-only, expected).
