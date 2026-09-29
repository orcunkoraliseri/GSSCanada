# 2J against the Energy and Buildings Guide for Authors, 2026-09-28

Guide text: `4J_docs_occ/writing/resources/E_and_B_guide_for_authors_2026-09-23.txt` (author's browser save,
read for 4J on 2026-09-23; line numbers refer to it). Venue approved by the supervisor on 2026-09-28
("I agree for Energy and Buildings"), with a request for a more energy/engineering title.

| Rule (guide line) | 2J state | Action taken |
|---|---|---|
| Title concise, informative (716-719) | old "From 'How Much' to 'When' ..." | New title chosen by the author 2026-09-28: "Residential electricity load shape under changing occupancy: household-level schedules and stock-scale building energy simulation for Canada, 2005–2030" (manuscript, title page, cover letter) |
| Title page: authors, affiliation with country, corresponding e-mail (714-731); single anonymized review (263) | title page was only in the cover-letter file | Author block added under the title in the manuscript; upload cover letter now holds the letter only |
| Original paper "preferably" at most 20 double-spaced pages incl. tables and figures (229-231) | about 13,800 words in the docx (with references and appendices), 12 figures | NOT changed. Soft limit ("preferably"); supervisor wants submission now. If the editor asks, first move Appendix B to the SI (as 4J did) |
| Abstract at most 250 words (743) | 240 words | none |
| Keywords 1 to 7, avoid "and"/"of" (764-765) | 7, none use "and"/"of" | none |
| Highlights 3 to 5, at most 85 characters, separate file with "highlights" in the name (771-781) | 5 bullets, 78-85 characters | `EB_upload/2J_highlights.docx` |
| Graphical abstract REQUIRED, separate file, at least 531 x 1328 px (787-800) | none (the August image shows the retired pipeline) | Prompt `submission/figures/Prompts_Images/Graphical_abstract_EB_prompt.md`; AUTHOR makes the image |
| AI-made images disclosed in each caption and in the AI declaration (905-929) | Figures 1-5 captions say "Drawn with Gemini (Google) from the authors' specification"; declaration names Figures 1 to 5 | 2026-09-28 (fc): caption notes REMOVED on the author's order (no LLM name anywhere except the AI declaration, whatever the guide says); the declaration still names Figures 1 to 5 |
| AI declaration section before References, fixed title (457-505) | present, exact title | none |
| Funding in standard form, funder role (437-455) | NSERC Discovery Grant + Volt-Age Seed Fund, with the funders-had-no-role sentence | none |
| Competing interests via declarations tool (397-435) | text present | AUTHOR fills the tool at submission and uploads its Word file |
| CRediT (1097-1134) | present | none |
| Data: Option C, deposit or state why not (993-1010) | statement: StatCan licence forbids redistribution; IESO public; derived data on request | none |
| Continuous line numbers (1064) | absent before | `eb_layout.py` in the build (line numbers + double spacing) |
| Numbered sections, abstract unnumbered (1069-1078) | yes | none |
| Acknowledgements directly before References (1086-1092) | yes | none |
| References: any consistent style at submission, DOIs (1146-1178) | author-year with DOIs | none |
| Sex/gender (587) | sentence in Section 2.2 | none |
| Figures as separate files | PDFs 1-12 | copied to `EB_upload/` |

Build: `py impl/T94_scripts/build_main_docx.py` (now reads `2J_manuscript_EB.md`, runs `post.py` = the 3J
version with centred captions, content-sized table columns and 16 pt title, then `eb_layout.py`).
SI: pandoc `2J_SI_EB.md` with `ref_submit.docx`, `--columns=10`, then `post.py`.
Cover letter: pandoc of the letter part of `2J_title_page_and_cover_letter_EB.md`, then `post.py`.
