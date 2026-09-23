# Applied Energy guide check (2026-09-22, second pass (ey))

Source: the official Guide for Authors, opened 2026-09-22 through the Concordia library connection.
Saved copies: `impl/AE_guide_for_authors_2026-09-22.html` and `.txt` (line numbers below refer to the .txt).
A third-party summary site (manusights) gave different limits (200-word abstract, 4 to 6 keywords,
numbered references required). Those limits are WRONG against the official page and were not used.
No Gemini prompt was needed.

| Requirement (guide line) | Official rule | Our paper | Status |
|---|---|---|---|
| File format (300-306) | editable .docx, single column, no strikethrough/underline | pandoc .docx, single column | met |
| Abstract (320-329) | at most 250 words; no references; define abbreviations | 240 words, no references, no abbreviations | met |
| Keywords (330-332) | 1 to 7; avoid multi-word keywords with "and"/"of" | 7; "peak demand and load factor" changed to "load factor" in (ey) | met |
| Highlights (333-338) | 3 to 5 bullets, at most 85 characters each, separate file with "highlights" in its name | 5 bullets (78 to 85 characters); `AE_upload/2J_highlights_AE.docx` | met |
| Graphical abstract (339-347) | encouraged, not required | none | optional, not made |
| Peer review (139) | single anonymized | author names may appear | met |
| Title page (313-319) | title, names, lower-case letter affiliations, full postal address, corresponding e-mail | `2J_title_page_and_cover_letter_AE.md` | met |
| Math (348-354) | editable; solidus for small inline fractions; exp for powers of e; numbered in order | two inline fractions changed to solidus in (ey); display equations (1)-(6), appendix (B.1)-(B.12) | met |
| Tables (355-363) | editable, cited, numbered, caption, notes below, no vertical rules or shading | 2 tables in text + Table A.1; docx has no borders or shading | met |
| Figures (364-399) | separate files, logical names; charts preferably vector (EPS/PDF) | `AE_upload/Figure_1.pdf` to `Figure_12.pdf`; Figures 6-12 are vector PDFs from the same plot script (PNGs byte-identical to the docx copies) | met; upload each |
| AI in figures (400-406) | explanatory diagrams allowed; say so in each caption and in the AI statement | Figures 1 to 5 captions say "Drawn with Gemini (Google) from the authors' specification." | met |
| Sections (455-460) | numbered sections 1.1, 1.1.1; abstract unnumbered; cross-references by number | sections 1-6 numbered; references by section number | met |
| Appendices (494-497) | A, B; Eq. (B.1); Table A.1 | "Table A1" changed to "Table A.1" in (ey); Eqs. B.1-B.12 | met |
| CRediT (476-481) | required | section before References | met |
| Competing interests (186-201) | declare; also fill the Elsevier declarations tool at submission | section before References | text met; tool at upload (author) |
| Funding (202-208) | standard form; state sponsor role; program detail not needed | NSERC (Discovery Grant) and Volt-Age Seed Fund, Concordia University; funders' role stated; grant number not needed (author, 2026-09-22) | met |
| Generative AI (209-225) | own section before References, set wording | Claude (grammar), Gemini (research reports, Figures 1 to 5) | met |
| Sex and gender (251-262) | define how sex/gender were used, or state as a limitation | Section 2.2: 2005-2015 cycles record sex; 2022 cycle and 2021 census record gender (men+, women+); joined into one two-category variable, conditioning and matching only | met (added in (ey)) |
| Acknowledgements (473-475) | directly before References, not on title page | last section before References | met |
| Data statement (424-435) | deposit data, or explain why not | Statistics Canada licence stops redistribution; derived data and scripts on request | met |
| References (498-511) | real sources, complete (authors, volume, pages), DOIs where available; any consistent style at submission | author-year, all authors listed; (ey) filled in full author lists for Elsayed 2023, Herrmann 2024, Mahdavi 2021 (Crossref) and the volume of Iseri 2026 (357) | met; numbered style applied by the journal at proof |
| Article length | no limit stated | not applicable | met |

Open for the author only: fill the Elsevier declarations tool; upload the highlights file and the twelve
figure files from `manuscript/AE_upload/`; optional: say if the PI wants NRC named as the source of the
Volt-Age funds (the offer letter says "NRC (Volt-Age)"; the earlier papers name only the Volt-Age Seed Fund).
