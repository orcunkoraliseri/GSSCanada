# P14 — Energy and Buildings submission package checklist (2026-09-23)

Status: checked 2026-09-23 against the files on disk. The rewrite (P2-P13) was in progress at the time,
so rows marked "rewrite" describe the PRE-rewrite manuscript (`4J_manuscript_submission.md`, dated
2026-09-17) and must be re-checked when the rewrite lands. Journal rules: `P14_journal_guide_EandB_2026-09-23.md`
(guide text `writing/resources/E_and_B_guide_for_authors_2026-09-23.txt`). No figure was regenerated or edited.

Paths below are relative to `4J_docs_occ/writing/submission/` unless they start with `4J_docs_occ/`.

## Summary: what is missing before upload

1. Manuscript: continuous line numbers are not in the build (no `lnNumType` in `extra/build_scripts/ref_submit.docx`,
   `ref_submit_single.docx` or the current docx). Manager.
2. Manuscript: Table 3 interval column waits on P5 (`[P5]` markers). Manager.
3. Graphical abstract: the new one does not exist yet. Author, from `IMP/prep/graphical_abstract_prompt.md`.
4. Figures: all seven are PNG only, nominal 100-300 dpi; charts need 1000 dpi or vector. Five carry the
   drawn word "Britain"; Figure 6 carries the withdrawn "six hours" span. Manager (re-export from the
   existing scripts after edits the manager approves).
5. Highlights: `4J_highlights.md` does not exist yet (rewrite writing it); an editable .docx with
   "highlights" in the file name is needed. Rewrite, then manager.
6. Data statement: Option C wants a repository deposit and citation; no deposit exists yet. Author
   (deposit, D4), manager (prepare the deposit bundle).
7. Generative AI declaration: absent from the current manuscript. Rewrite drafts; author confirms tools.
8. Declarations tool (competing interests Word file): filled only at submission. Author.
9. Cover letter: suggested reviewers and date are placeholders. Author.

## Per item

| # | Item (guide line) | Exists? | Path | What is missing | Who |
|---|---|---|---|---|---|
| 1 | Manuscript, editable Word, single column (687-690) | Yes (pre-rewrite) | `4J_manuscript_submission.md`, `4J_manuscript_submission.docx` (2026-09-17) | Rebuild from the rewritten .md with pandoc + `extra/build_scripts/ref_submit.docx` + `post.py` | Manager |
| 1a | Continuous line numbers (1064) | No | build: `extra/build_scripts/` | Add line numbering (section property `w:lnNumType`, restart continuous) to the reference doc or to `post.py`; confirm in the built docx | Manager |
| 1b | Title page: title, author, full affiliation with country, corresponding author with e-mail (guide "Title page") | Yes (pre-rewrite, "Author Information") | `4J_manuscript_submission.md` lines 19-27 | Title must become the D2 title; keep author block and corresponding-author e-mail on the title page | Rewrite |
| 1c | Abstract at most 250 words, no labels, no undefined abbreviations (743, 759) | No (pre-rewrite: 517 words, labelled) | manuscript | Rewrite target | Rewrite |
| 1d | Keywords 1-7 (764-765) | Yes (6) | manuscript | Re-check after rewrite | Rewrite |
| 1e | Numbered sections 1, 1.1 (1069-1078) | No (H1 then H3) | manuscript | Rewrite target | Rewrite |
| 1f | Equations editable and numbered; appendix Eq. (A.1) (806-819, 1140) | Partly | manuscript | Appendix B equations in rewrite | Rewrite |
| 1g | Tables editable, captions, notes below, no vertical rules or shading (823-837) | Markdown tables | manuscript | Check in the built docx | Manager |
| 1h | Table 3 intervals | No | `IMP/impl/P5_intervals_table3.md` | P5 job output; fill `[P5]` cells and the marked sentence in 2.6 | Manager |
| 1i | Length, about 7,500 words main text (D5; guide prefers about 20 double-spaced pages, 229-231) | No (pre-rewrite about 17,100 words) | manuscript | Rewrite target; word count per section in the brief log | Rewrite |
| 1j | Sex/gender sentence (587) | No | manuscript | One sentence | Rewrite |
| 2 | Highlights: 3-5 bullets, at most 85 characters each, separate editable file with "highlights" in the name (771-781) | No | target `4J_highlights.md` | File (being written); then build `4J_highlights.docx`; count characters per bullet; remove the in-manuscript Highlights section | Rewrite, then manager |
| 3 | Graphical abstract, separate file, at least 531 x 1328 px (h x w), readable at 5 x 13 cm, TIFF/EPS/PDF/MS Office (787-800) | Old one only | `figures/HETUS_LLM_CrossNational_Pipeline.png` (3937 x 1525 px, nominal 125 dpi), embedded in the manuscript at line 41 | New image from `IMP/prep/graphical_abstract_prompt.md` as PDF + TIFF; old one removed from the manuscript body | Author (image), manager (removal) |
| 4 | Figures as separate files, logical names Figure_1 ... (842-893) | PNG files exist; not named Figure_N | `figures/` | Upload copies named `Figure_1` to `Figure_7` in an upload folder (2J precedent: `2J_docs_occ_nTemp/.../manuscript/AE_upload/Figure_N.pdf`) | Manager |
| 4a | Resolution: charts and line drawings 1000 dpi (min width 3543 px single column, 7480 px full page) or vector EPS/PDF with fonts embedded; photos 300 dpi | No | see figure table | All seven are PNG; none reaches 7480 px; nominal dpi tags 100-300. Re-export each from its script as vector PDF | Manager |
| 4b | Figure content matches the rewritten text | No | see figure table | "Britain" in drawn labels (Figures 2, 3, 4, 6, 7); Figure 6 "six hours" span (withdrawn under P3 branch 2) | Manager |
| 4c | AI use in images disclosed in caption and declaration (905-929) | n/a so far | captions | Only if an AI tool made or altered an image (for example the graphical abstract) | Author |
| 5 | Supplementary material, cited in text, with caption, submitted with the manuscript (guide "Supplementary material") | Yes (pre-rewrite) | `4J_supplementary_material.md` | Companion title still the old one; being updated by the rewrite; build to .docx or .pdf for upload | Rewrite, then manager |
| 6 | CRediT statement (1097-1134) | Yes | manuscript line 37 | Move to the end-of-manuscript declarations block | Rewrite |
| 6a | Competing interests: text plus declarations tool Word file (397-435) | Text yes; tool file no | manuscript line 35 | Fill the Elsevier declarations tool at submission, upload the .docx | Author |
| 6b | Funding in the standard sentence form (437-455) | Yes, wrong spelling | manuscript line 31 ("Voltage-Age Seed fund") | "Volt-Age Seed Fund" (as in revised 2J), standard form, sponsor role sentence | Rewrite |
| 6c | Acknowledgements directly before References (1086-1092) | No (in front matter) | manuscript | Move | Rewrite |
| 7 | Data statement; Option C: deposit and cite, or state why not (993-1010) | Statement yes; deposit no | manuscript line 33 | Deposit code and the frozen pre-registration with its hash (`4J_docs_occ/Step6_docs/outputs_step6/prereg.md` + `.md5`, addenda `prereg_addendum_01.md`, `_02.md` + `.md5`); cite the repository DOI; state that HETUS/UKTUS microdata cannot be redistributed. Current text says "on reasonable request": replace with the deposit citation | Author (deposit), manager (bundle), rewrite (wording) |
| 8 | Declaration of generative AI and AI-assisted technologies in the manuscript preparation process, new section before References (457-505) | No | manuscript | Draft in rewrite; author names each tool and purpose | Rewrite, then author |
| 9 | Cover letter | Yes (new) | `4J_cover_letter.md` | Date; suggested reviewers `[author to add]`; convert to .docx at upload | Author |
| 10 | Pre-registration deposit (D4), "registered internally before training (hash-locked, 2026-08-18) and deposited at submission" | No | files as in row 7 | Deposit on a public registry at submission; add the link to the manuscript and data statement | Author |
| 11 | References consistent, DOIs where available, all real (1146-1178) | Yes (author-year, DOIs) | manuscript | External audit (`IMP/prep/external_audit_prompt.md`) flags any it cannot verify | Author (runs audit), manager (fixes) |

## Figures referenced by the manuscript (pre-rewrite)

Read with `file` and the PNG `pHYs` chunk (pixels per metre converted to dpi). "Width at 1000 dpi" is the
largest print width at which the PNG meets the line-art rule.

| Manuscript label | File | Exists? | Pixels (w x h) | Nominal dpi | Width at 1000 dpi | Script | Content issue |
|---|---|---|---|---|---|---|---|
| Graphical abstract | `figures/HETUS_LLM_CrossNational_Pipeline.png` | Yes | 3937 x 1525 | 125 | 10.0 cm | `figures/scripts/generate_graphical_abstract.py` | To be replaced (item 3); must not stay in the manuscript body |
| Figure 1 | `figures/HETUS_LLM_Pipeline_Steps.png` | Yes | 4440 x 1620 | 100 | 11.3 cm | `figures/scripts/generate_fig01_pipeline.py` | none found by label search |
| Figure 2 | `figures/Figure_02_loco_design.png` | Yes | 3850 x 1277 | 175 | 9.8 cm | `figures/scripts/generate_fig02_loco.py` | "Britain" x2 in drawn text |
| Figure 3 | `figures/Figure_03_nine_cells.png` | Yes | 3600 x 2160 | 300 | 9.1 cm | `figures/scripts/generate_fig03.py` | "Britain held out" labels |
| Figure 4 | `figures/Figure_04_amplitude_slope.png` | Yes | 3600 x 2160 | 300 | 9.1 cm | `figures/scripts/generate_fig04.py` | "Britain held out" labels |
| Figure 5 | `figures/Figure_05_joint_structure.png` | Yes | 3600 x 2100 | 300 | 9.1 cm | `figures/scripts/generate_fig05.py` | none found by label search |
| Figure 6 | `figures/Figure_06_appliance_peaks.png` | Yes | 3600 x 2160 | 300 | 9.1 cm | `figures/scripts/generate_fig06.py` | "six hours" span annotation (withdrawn claim); generated series only, while Table 7 becomes three sources; "Britain" legend and label. Watt labels (503, 416) match the data |
| Figure 7 | `figures/Figure_07_heating_null.png` | Yes | 3600 x 2550 | 300 | 9.1 cm | `figures/scripts/generate_fig07.py` | "Britain" country label |

All eight files exist. All are wide enough for a single column (3543 px) at 1000 dpi; none is wide enough
for a full page (7480 px). The rewrite may move non-load-bearing figures to the SI: re-run this table on
the final figure list.

Figure fix route (manager, not done here): edit the label strings in the scripts ("Britain" to "UK";
Figure 6 to the P3 result or to the SI as the rewrite decides), re-export as vector PDF with embedded
fonts, snapshot md5s of the PNGs first (scripts write to real paths), and copy to an upload folder as
`Figure_1.pdf` ... `Figure_7.pdf`. The data figures are script plots from frozen data, which the guide
allows (905-929).

## Next

Manager: after the rewrite lands, re-check rows marked Rewrite, add line numbering to the build, fix and
re-export the figures, build highlights/SI/cover-letter .docx files, fill `[P5]`. Author: graphical
abstract, repository deposit, declarations tool, suggested reviewers, generative AI tool names.

## Manager vet (2026-09-23)
- Item 1 / row 1a is now DONE: `tools/4thJ_docx_eb_layout.py` runs inside `tools/4thJ_build_submission_docx.sh`
  (double spacing + continuous line numbers, schema-ordered `w:lnNumType`); tested on the pre-rewrite docx,
  Word opened it, 72 pages, numbering on. See `P14_journal_guide_EandB_2026-09-23.md` note.
- Cover letter 426 words (file), no email address, no banned wording. Graphical-abstract and audit prompts
  ban "Britain", "six hours", "2 to 6", 518/395/422. Accepted.
- Item 4 (figures): delegated to a figure-fix agent (labels to "UK", Figure 6 to the P3 three-source result,
  vector PDF + 1000 dpi PNG export); outcome logged below when done.

## Figure fix (agent, 2026-09-23)

**Archive (step 1):** every script to be edited and every PNG it writes were copied to
`figures/previous/` (and `figures/previous/Prompts_Images/` for the alias copies) with suffix
`.pre_UKfix_20260923` before any edit; each copy checked non-empty (`[ -s ]`), all passed.

md5 before -> after (figures/ copy; the two Prompts_Images copies of each figure are byte-identical
to the figures/ copy, both before and after):
| File | md5 before | md5 after |
|---|---|---|
| Figure_02_loco_design.png | 84d64dafed1c382d68bf7103ab4dff27 | 1405cf0d42a94cbe2ed580da6f612ec7 |
| Figure_03_nine_cells.png | 2968a08aa5ef4766a25a0d46245d6fba | bf49020cbcdfd8cf89648f5d2d051855 |
| Figure_04_amplitude_slope.png | a78cc584865467ba3b6ebdca538f5aee | 9a9621dbfb310b8b4447679f003fd305 |
| Figure_06_appliance_peaks.png | e520c555ce1e8cd62256fe190f5b8567 | d57116b2f30748aeb8c70b5357365c32 |
| Figure_07_heating_null.png | d82f383195e2d2273ce61bbbe563a459 | eaf8cb2a04fe4d157b5fabcd228ae915 |

**Figures 2, 3, 4, 7 (step 2):** drawn word "Britain" replaced with "UK" everywhere it appeared, keeping
grammar natural ("Britain held out" -> "UK held out"; "Britain's published census marginals" -> "the
UK's published census marginals"; "against Britain's published tables" -> "against the UK's published
tables"; the palette comment header too). `grep -rn Britain` on all five edited scripts now returns
nothing. No data value, colour, or dict key structure changed (dict keys were renamed consistently, e.g.
`generate_fig04.py`'s `steering_r2` key and the `folds_data` name it is looked up by both changed
together). The in-image titles "Figure 3: ...", "Figure 4: ...", "Figure 7: ..." (drawn via
`fig.suptitle`) were removed; the vacated top margin was given back to the panels
(`subplots_adjust`/`gridspec` `top=` raised) and nothing else was touched. Figure 2 had no in-image
"Figure 2:" title to remove.

**Figure 6 (step 3): rebuilt from data.** Old figure plotted only the generated diaries for 100
dwellings and carried a withdrawn "six-hour spread" claim. New figure: three panels side by side
(Spain, Italy, UK), sharing one y-axis, each with three hourly lines (generated, real diaries
unweighted, raked donor diaries), stock-mean electricity per dwelling in watts, hours 0-23. Colours by
source (Tol muted set): generated indigo `#332288` solid/circle, real rose `#CC6677` dashed/square,
raked donor teal `#44AA99` dash-dot/triangle -- line style and marker carry the distinction alongside
colour. Each line's peak hour is marked with a larger dot (black edge); no "six hours" text, no spread
arrow, no ranking annotation, no title text. Axis labels are plain words ("Hour of day", "Mean
electricity per dwelling (W)"). Data are read directly from
`Step9_docs/outputs_step9_P3/<source>/<country>/stock_series_<country>.csv` (hourly mean of
`electricity_w` across the year, divided by 100 dwellings) — the same files behind the P3 result table
in `P3_appliance_real_and_donor.md`.

**Reproduction check (step 3, required before trusting the figure):** all nine peaks (3 countries x 3
sources) reproduce the P3 result table exactly:
Spain generated 14:00 502.9 W, real 21:00 421.5 W, donor 19:00 408.5 W;
Italy generated 18:00 403.5 W, real 19:00 444.4 W, donor 21:00 396.5 W;
UK generated 20:00 416.1 W, real 18:00 427.2 W, donor 21:00 425.9 W.
Verified twice: once independently before touching the script (`py -3` one-off), and again inside
`generate_fig06.py` itself, which now raises `SystemExit` and refuses to save if any of the nine
peaks drifts from these values. Both checks PASSED. (First draft had a bug: the shared y-axis was
capped at 480, clipping the Spain-generated peak of 502.9 off the top of the panel; caught on visual
review of the rendered PNG and fixed by sizing the axis to the data's own maximum before the final
export.)

**Export (step 4):** all five scripts now set `pdf.fonttype`/`ps.fonttype` = 42 and save, for every PNG
path each script already wrote (figures/ copy and both Prompts_Images alias copies), a PNG at 1000 dpi
and a vector PDF next to it. All ran locally with `py -3` against frozen data/coordinates; no cluster
compute used. Resulting pixel sizes (figures/ copy):

| File | Pixels (w x h) | dpi (PNG tag) | PDF |
|---|---|---|---|
| Figure_02_loco_design.png | 22000 x 7300 | 1000 | Figure_02_loco_design.pdf (27.0 KB) |
| Figure_03_nine_cells.png | 12000 x 7200 | 1000 | Figure_03_nine_cells.pdf (22.6 KB) |
| Figure_04_amplitude_slope.png | 12000 x 7200 | 1000 | Figure_04_amplitude_slope.pdf (27.6 KB) |
| Figure_06_appliance_peaks.png | 13500 x 4600 | 1000 | Figure_06_appliance_peaks.pdf (27.9 KB) |
| Figure_07_heating_null.png | 12000 x 8500 | 1000 | Figure_07_heating_null.pdf (27.6 KB) |

**Verify (step 5):** each new PNG opened and read: all show "UK", none shows "Britain", Figure 6 shows
no "six hours" text. `grep -rn Britain` on the five edited scripts: 0 matches. `grep -n suptitle` on
the five: only Figure 2's (no title string; Figures 3/4/6/7 have no suptitle call left).

**Not done / out of scope for this pass:** Figure 5 and Figure 1 were not touched (not in this task's
list; Figure 5's palette comment still says "Britain" but no in-image label was ever found under that
name). The `4thJ_figureNN_*.md` spec files in `Prompts_Images/` and the pipeline/graphical-abstract
scripts were not edited. Upload-folder renaming to `Figure_1.pdf` ... `Figure_7.pdf` (P14 item 4) is
still open, as is the "Britain" -> "UK" pass over any figure spec `.md` files, since those are prompt
documents, not drawn images, and were outside this task's scope.
