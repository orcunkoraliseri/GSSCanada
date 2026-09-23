# P14 — Energy and Buildings Guide for Authors, read 2026-09-23

Source: the author's browser save,
`writing/resources/Guide for authors - Energy and Buildings - ISSN 0378-7788 _ ScienceDirect.com by Elsevier.pdf`
(41 pages, printed 2026-09-23 08:19). Text copy: `writing/resources/E_and_B_guide_for_authors_2026-09-23.txt`
(line numbers below refer to it).

## Rules that change the 4J plan

| Rule | Guide line | 4J today | Action |
|---|---|---|---|
| Original papers "preferably no more than 20 double line spaced manuscript pages including tables and illustrations" | 229-231 | ~17,100 words, 8 figures, ~8 tables | Soft limit ("preferably"). 20 double-spaced pages is roughly 5,000-6,000 words with no figures, so even the D5 target (9,000-10,000) is above it. Author asked (see below). Move tables and figures that are not load-bearing to the supplement either way |
| Abstract at most 250 words | 743 | 517 words, labelled parts | Rewrite (P13), no labels, no undefined abbreviations (759) |
| Keywords 1 to 7, avoid multi-word "and/of" keywords | 764-765 | check | P13 |
| Highlights required, 3 to 5 bullets, at most 85 characters each, SEPARATE file with "highlights" in the file name | 771-781 | in the manuscript | Separate file at P14 |
| Graphical abstract REQUIRED, separate file (TIFF, EPS, PDF or MS Office) | 787-800 | embedded PNG | Separate upload; image is the author's (never-create-images rule) |
| Figures as separate files; photos/halftones at least 300 dpi, line art at least 1000 dpi | 842-893 | not checked | Check every figure file (P14) |
| AI may make data plots from data; must not alter primary data images; AI use in images disclosed in the caption and in the declaration | 905-929 | figures are script plots from frozen data plus author-made schematics | Caption disclosure only if an AI tool made an image |
| Math as editable text, displayed equations numbered consecutively; appendix equations Eq. (A.1) | 806-819, 1140 | only 2 displayed | Fits P6 (equations in text + Appendix B) |
| Tables editable, captions, notes below, no vertical rules or shading, use sparingly | 823-837 | markdown tables | Check at rebuild |
| Declaration of generative AI use: new section at the END of the manuscript, title "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process" | 457-505 | missing | Add (P13); author confirms the wording |
| Competing interests via the declarations tool (Word file uploaded) | 397-435 | text only | Author fills the tool at submission |
| Funding in the standard sentence form | 437-455 | "Voltage-Age Seed fund" spelling | One spelling across papers (P12) |
| CRediT statement required | 1097-1134 | present | Keep |
| Research data: Option C, deposit data in a repository and cite it, OR state why it cannot be shared; data statement required | 993-1010 | check | HETUS/UKTUS microdata cannot be redistributed: statement says so; deposit what can be (code, frozen pre-registration and hash, generated diaries if privacy audit allows). Ties to D4 deposit |
| Continuous line numbers | 1064 | no | Build script option (P13) |
| Numbered sections 1.1, 1.1.1; abstract not numbered | 1069-1078 | H1 then H3, no H2 | Fix heading levels at rebuild |
| Acknowledgements directly before the reference list | 1086-1092 | front matter | Move (P13) |
| References: any consistent style at submission; must include DOIs where available; every reference must be real | 1146-1178 | author-year, DOIs | OK as is; journal applies numbered style at proof |
| Sex and/or gender dimensions addressed in the article or declared as a limitation | 587 | sex is a stratum, not discussed | One sentence (P13) |
| Single anonymized review | 263 | author names on file | OK |
| Word, single column, editable source | 687-690 | docx via build script | OK |

## Waiting on the author

Length: the guide prefers about 20 double-spaced pages including tables and figures. D5 (9,000-10,000
words) was set before the guide was read. Recommendation recorded in RESUME.

## 2026-09-23 (manager): layout step added to the build
`tools/4thJ_docx_eb_layout.py` (new) sets double spacing on body-text styles (BodyText, FirstParagraph,
Abstract, Bibliography; tables unchanged) and adds continuous line numbers (`w:lnNumType`, placed in
schema order inside `w:sectPr`). Wired into `tools/4thJ_build_submission_docx.sh` (default on; `EB_LAYOUT=0`
skips; backup `tools/previous/4thJ_build_submission_docx.sh.pre_EBlayout_20260923`). Tested on a copy of the
current docx: Word opens it, line numbering active, 72 pages at double spacing; and a dry-run build of the
archived manuscript: 4 style patches + 1 section patch printed, captions 8, superscript PASS.
