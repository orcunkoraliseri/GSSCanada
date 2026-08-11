# RESUME - THE 3J director prompt. Start every session here.

**Last updated: 2026-08-11, "Table 4 to the appendix, Limitations merged into Discussion" round.**

> 🔴 **THIS FILE IS THE FIXED ADDRESS OF THE 3J HANDOFF. There is no second one.**
> Instruction from the author, 2026-08-09: *"je veux seulement cet prompt RESUME.md, comme un prompt
> de directeur"* - one file, this path, updated in place every round.
>
> - **Never create a successor file beside it.** Copy the predecessor into `archive/` under a
>   `.<date>_pre_<round>.md` name, then **edit this file**. The address never moves.
> - **Never leave it lagging.** It is updated in the same response as the state change it describes,
>   like the Progress Log. A handoff that lags is worse than none, because it is trusted.
> - **History.** Until 2026-08-09 the handoff lived at
>   `3rdJ_employee_N6_figure_renumbering_2026-08-08.md`, and this file was a short pointer at it. The
>   author consolidated the two. That file is now
>   `archive/3rdJ_manager_prompt_2026-08-09_generated_images.MERGED_INTO_RESUME.md`; every earlier
>   handoff is in `archive/` beside it, most recent first:
>   `3rdJ_manager_prompt_2026-08-09_ledger.SUPERSEDED_by_generated_images_round.md`,
>   `3rdJ_manager_prompt_2026-08-09_round2.SUPERSEDED_by_full_ledger_round.md`,
>   `3rdJ_manager_prompt_2026-08-09.SUPERSEDED_by_docx_cleanup_round.md`,
>   `3rdJ_manager_prompt_2026-08-08.SUPERSEDED_by_2026-08-09_decisions_and_docx_round.md`,
>   `3rdJ_manager_prompt_2026-08-08_submission_round.SUPERSEDED_by_figure_dpi_round.md`,
>   `3rdJ_manager_prompt_2026-08-08.SUPERSEDED_pre_RV09_RV10.md`,
>   `3rdJ_paper_manager_prompt_2026-08-07_review_round.md`.
> - The old contents of this file - the Leg-2 two-channel simulation runbook, with the v24.2
>   `Zone_or_ZoneList_Name` office-WFH bug write-up - are at
>   `archive/RESUME.2026-08-09_pre_rewrite_leg2_runbook.md`. That campaign is finished and superseded
>   by Leg-3. **Nothing in it should be executed.**

---

## Contents

1. [Your role](#your-role)
2. [Where the paper stands, 2026-08-09](#where-the-paper-stands-2026-08-09)
3. [The document, and how to rebuild it](#the-document-and-how-to-rebuild-it)
4. [The figures, and who owns them](#the-figures-and-who-owns-them)
5. [Everything completed, round by round](#everything-completed-round-by-round)
6. [Open BUILD NOTE 1 of 3: Table A2 ships unlabelled and uncited](#open-build-note-1-of-3-table-a2-ships-unlabelled-and-uncited)
7. [Open BUILD NOTE 2 of 3: two references have never been opened](#open-build-note-2-of-3-two-references-have-never-been-opened)
8. [Open BUILD NOTE 3 of 3: the generated-image defects](#open-build-note-3-of-3-the-generated-image-defects)
9. [What is settled, so nobody reopens it](#what-is-settled-so-nobody-reopens-it)
10. [The work that is left, in the order I would do it](#the-work-that-is-left-in-the-order-i-would-do-it)
11. [Refusals still standing](#-refusals-still-standing-the-first-one-costs-money-if-it-is-forgotten)
12. [Standing hazards](#standing-hazards-and-every-one-of-them-has-already-bitten-this-project)
13. [Hard rules for this phase](#hard-rules-for-this-phase)
14. [The closure ritual, every round, unprompted](#the-closure-ritual-every-round-unprompted)

---

## Your role

You are the **director / manager (Opus)** for the 3rd journal paper. You plan, decide, write employee
prompts, and review. You do not normally execute multi-step implementation yourself, but the author
has overridden that six times now and will probably again; when they do, do the work and log it.

Reply in English. The author writes in French. Keep replies short unless detail is asked for.

**In five lines, for the impatient:**

- The 3J paper is **written, built, rendered and gate-clean**. It is **not submitted**.
- Venue: **Building and Environment (Elsevier)**, reconfirmed 2026-08-09, which made three
  commitments binding.
- **This is a WRITING phase. Zero simulation.** No `sbatch`, no cells, no re-runs.
- **Zero open BUILD NOTES.** The build prints the count on every run; it reads `none` as of 2026-08-11.
- 2J was submitted to Building Simulation on 2026-08-07 and is frozen pending its decision letter.

---

## Where the paper stands, 2026-08-11

**Target venue: Building and Environment (Elsevier). RECONFIRMED by the authors 2026-08-09.** The
sheet `writing/submission/02_journal_options.md` is **green again**. Reopen trigger (b) fired on
2026-08-08 (0J was rejected at B&E for insufficient quality, not scope); the trigger was put back in
front of the authors with the bar restated and the venue was chosen again, recorded in a
`RECONFIRMED BY THE AUTHORS - 2026-08-09` block under Option D.

> **What reconfirmation cost, and it is binding now, not advisory.** The amber block said that if the
> venue were reconfirmed the three commitments under "My recommendation" become more load-bearing.
> They are therefore fixed: (1) the **uninjected-control** result leads the cover letter's first
> paragraph - it is what separates "three of four EUI gates failed" from a desk reject, because the
> office band fails on a model with no occupancy injection at all; (2) the **abstract** opens on the
> behavioural claim, not the pipeline; (3) the **§1 and §6.1 pass** under Option D stands.
>
> Still cheap and still never done: read the 0J decision letter if it exists. "Quality" can mean thin
> contribution, weak validation, or unclear writing, and those point at different fixes. Reconfirming
> the venue decided that the answer is not needed *before* submitting, not that it does not matter.

**Numbers, all re-derived at the last build:**

| | |
|---|---|
| `readySubmission.md` | **1,086 lines**, 23 caption labels + the graphical abstract |
| `3J_manuscript_submission.docx` | **5,744,124 bytes** · 23 captions · **15 images** · 14 tables · **14,359 words** · **single** spaced |
| equations | **6 native Word (OMML)**, 3 of them displayed. Formulas are no longer code blocks |
| lists in the document | **5**, and all five are the Highlights. Everything else is prose |
| `f3` asset provenance | **3 PASS / 2 FAIL** - the figure registry is stale since the 2026-08-11 replot, see below. **Do not modify `f3` itself** |
| `f4` prose rules | 7 PASS / 0 FAIL (31 files, 22 exhibits) |
| `f5` figures | not run this round - it is NOT read-only, see below |
| `f6` replot equivalence | 5 PASS / 0 FAIL as of 2026-08-09 |
| open BUILD NOTES | **0** |

🔴 **`f3`'s two FAILs are asset bookkeeping, not a manuscript defect, and they are real.** C2 lists
figures present in the submission tree that are not in the registry, and C4 reports
`figures_hires/fig_diurnal_4ch.png` disagreeing with its registered hash. Both date from the
2026-08-11 figure replot, which did not update the registry. Fix the REGISTRY, never the gate.

**House rules for exhibits, set by the author 2026-08-11 and now enforced by the build:**
a figure caption goes **below** the figure, a table caption goes **above** the table, every caption is
**about five words** on **one line**, and **bold is not used inside a paragraph** - the only bold left
in the document is the 24 `**Figure N.**` / `**Table N.**` labels, which the assembler, the loss check
and `f4`'s C7 all key on. The build prints `captions that wrapped onto a second line`; it must stay 0,
because a wrapped caption used to be split in half by its own figure.

**House rules for the PROSE, set by the author 2026-08-11 in the same day's second message. It is a
paper, not a report, and every one of these is countable in the built file:**

- **One serif font.** Times New Roman everywhere. `ref_submit_single.docx` pins the four heading styles
  and `VerbatimChar`; the sources carry **no inline code spans at all**. An identifier in backticks
  reads as code however it is typeset, so both halves are needed. Installed file: 0 explicit non-Times
  runs, 0 Consolas.
- **Formulas are Word equations.** Written as TeX in the sources, converted by pandoc to native OMML.
  Count `<m:oMath>` in the installed file; a formula that shipped as text or as a picture counts zero.
- **No build dates, no repository paths, no "Footnotes" sections** in reader-facing text. Currently
  0 / 0 / 0.
- **No bullets and no numbered lists**, except the five Highlights, which Elsevier requires as a list.
- **No exhibit inside Discussion or Conclusion.** Table 4 and Table 7 live in the supplementary
  material and are cited from the body.
- **There is no Limitations chapter.** It was merged into Chapter 6 on 2026-08-11 and the chapter was
  cut by 49 %, 2,656 to 1,367 words. The Conclusion is now Chapter 7. Continuous prose, no
  subsections, no L-numbers.
- **Table numbering is not in first-citation order** (main text 1, 2, 6, 3, 5; appendix 4, 7, A1, A2).
  Pre-existing, flagged to the author, renumbering not done unasked.
- **The appendix carries tables, not essays.** No explanatory blocks around an SI table.

🔴 **Before cutting any block, find the surviving home of every number in it.** The disclosures that
were deleted from the SI model card this round are all stated in Chapter 3 prose; that was checked
disclosure by disclosure, not assumed. A cut that loses a measurement is a defect, not a shortening.

⚠ **The `f5` paragraph below describes the state as of 2026-08-09, when the shipped art was
author-generated. The 2026-08-11 replot put the script-drawn figures back, which may have changed both
arms; `f5` has not been run since, so its current verdict is UNKNOWN rather than 5 PASS / 2 FAIL.
Snapshot the figure tree's md5s before running it - see the read-only warning underneath.**

🔴 **`f5`'s two FAILs are the correct answer and must not be "fixed".** C1 fails because the vector
PDFs for the swapped figures were deliberately removed rather than left disagreeing with the new
PNGs. C2 fails because the plotting scripts no longer reproduce the shipped artwork - they cannot,
the artwork is no longer theirs. Both are true statements about a decision the authors took.

🔴 **`f5` is also NOT read-only. Its C2 arm re-runs every figure script, and those scripts write to
the real output paths.** Running it after installing an image silently reverts the install in
`writing/figures/` and regenerates the deleted PDFs. Its `md5 changed on re-run (b3eea0a9 ->
d09d7b8d)` line was the gate reporting **its own write**, not a determinism finding. Re-install and
re-verify after running it. `f6` was checked the same way, snapshotting the figure tree's md5s before
and after, and is genuinely read-only.

---

## The document, and how to rebuild it

`writing/fullSet/` holds **one** file, `readySubmission.md`, the submission copy. The working draft
lives in `writing/fullSet/previous/`. Both are written from one in-memory string by `assemble_3J.py`;
they differ only by `strip_for_submission()`, which prints a manifest of every removal on every build.

```
writing/submission/
  3J_manuscript_submission.md     <- readySubmission.md, figure paths rebased ../figures/ -> figures/
  3J_manuscript_submission.docx   <- 5.76 MB, 24 captions, 15 images, 14 tables, SINGLE spaced
  figures/  figures/SI/           <- the 15 shipped PNG (+ vector PDF for figures 7-11 only)
  figures/Prompts_Images/         <- 15 image-generation prompts + README
  figures/archive/                <- superseded matplotlib art · jpg duplicates · the 3 refused figures
  tables/   tables/SI/
  extra/build_scripts/            <- ref_submit.docx, ref_submit_single.docx, post.py, submit_check.py
```

Rebuild it with, from `3J_docs_occ_nTemp/`:

```
py -3 writing/fullSet/assemble_3J.py
cd writing/submission
sed 's|\.\./figures/|figures/|g' ../fullSet/readySubmission.md > 3J_manuscript_submission.md
pandoc 3J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 3J_manuscript_submission.docx
```

🔴 **The reference doc changed on 2026-08-09 and the old one still exists.** `ref_submit.docx` is 2J's,
untouched, **double** spaced (`w:line="480"`). `ref_submit_single.docx` is the derived copy at
`w:line="240"`, **single**, which is what the authors asked for and what the recipe above uses. Both
carry 12 pt Times, black headings, justified body, centred 10 pt captions; `post.py` sets table text to
10 pt single-spaced. Note that **Elsevier asks for double-spaced manuscripts at submission**, so if the
desk check bounces it, the fix is swapping one filename on the pandoc line.

**Verify the INSTALLED docx, never the build output** - in the 2J round a table column had silently
vanished from the shipped file. The check that matters is md5 of every part in `word/media/` against
the files on disk. **No blinded build is needed**: review is single-anonymized (RV10 item 14).

**The build tells you whether the paper is ready:**

```
UNRESOLVED BUILD NOTES -- each one blocks submission:
  none. Nothing in the manuscript is waiting on an external answer.
```

An answered note is rewritten in place as `BUILD NOTE RESOLVED <date> by <what>`. It keeps the words
"BUILD NOTE" on purpose, so the strip and the residue check still catch it, and it stops counting as
blocking. **Deleting the note would delete the reason.** **Clean is not ready.**

---

## The figures, and who owns them

**All 15 images in the `.md` are present in the `.docx`, verified byte-identical by md5 against
`word/media/` on 2026-08-09.** This is the current, correct state of the artwork:

| figure | file | px | origin |
|---|---|---|---|
| graphical abstract | `graphicalAbstract.png` | 1376 x 768 | **author-generated** |
| 1 to 6 | `Figure_01..06_*.png` | 1376 x 768 | **author-generated** |
| S1 | `SI/Figure_S01_occupiable_shares.png` | 1200 x 896 | **author-generated** - 🔴 defective, see BUILD NOTE 3 |
| S2 | `SI/Figure_S02_scenario_levers.png` | 1376 x 768 | **author-generated** |
| S3 | `SI/Figure_S03_leg2_pipeline.png` | 1376 x 768 | **author-generated**, clean |
| **7 to 11** | `Figure_07..11_*.png` | 4622 to 6597 | 🔴 **matplotlib, 600 dpi + vector PDF. These are the measured results. They were NOT replaced and must not be, absent a decision** |

The generated images are about **184 dpi** at the 190 mm page width, against Elsevier's **500** for
combination art; the files they replaced were 5400 to 6600 px. Figures 1-6, S1, S2 and S3 now have
**no vector PDF**. That, and three visible rendering defects, is BUILD NOTE 3.

**Every one of the 15 has a prompt** at `writing/submission/figures/Prompts_Images/`. The six that
carry measured numbers - 7, 8, 9, 10, 11, S1 - have prompts that **embed the actual series in a
table**, from the frozen deliverable, with file, column and source line named. Figure 9's series needs
`metric == "energy_W"` (Step-9 script `:331`); without that filter every channel returns 48 rows and
the plotting code's `len(y) != 24` guard silently skips it.

---

## Everything completed, round by round

The full detail is in `writing/implementation/3rdJ_paper_TASKS.md`, one Progress Log entry per line
below. This table exists so a fresh session knows what is **done and closed** without reading 1,862
lines. The third column is what the round found that was not what it was sent to do - that column is
the reason the ledger is worth keeping.

### Build phase - 2026-08-06, tasks T1 to T12

| # | What was delivered | What it also found |
|---|---|---|
| T1 | Step-1 asset verification: every figure, table and number traced to a frozen artefact | - |
| T2 | Bucket C - the 7 existing figures relocated into the paper tree | one C2 mismatch, explained not patched |
| T3 | Bucket B - Tables 2, 3, 6 | 🔴 **Table 6 changed what the paper is allowed to claim** |
| T4 | Bucket B - Tables 4, 5 | an arithmetic error, caught at review |
| T5 | Bucket B - Tables 1, 7 | the limitations count is a known ID collision |
| T6 | Bucket B - SI tables A1-A2, B1, Appendix C | B1 is clean |
| T7 | Bucket A - the 8 schematic prompts | - |
| T8 | Bucket D - Chapters 2, 3, 4 | a new check, plus a Methods disclosure that had to be added |
| T9 | Bucket D - Chapter 5, Results | §5.1 gained a caveat it needed |
| T10 | Bucket D - Chapters 1, 6, 7, 8 + Front Matter | two manager corrections |
| T11 | Assembly | **the 2J divergence is now structurally impossible**, not merely avoided |
| T12 | Final build report and closure | - |

### Round 2 - 2026-08-06 night into 2026-08-07

| # | What was delivered | What it also found |
|---|---|---|
| R3 | the submission strip, `strip_for_submission()` | 🔴 **the transform's own guard caught it lying** |
| R2 | schematics - direction decided, build delegated | - |
| R4 | the first deep-research prompt | - |
| R1 | the first end-to-end read of the whole paper | it justified itself immediately |
| #17 | - | 🔴 **the strip deleted real content and no check noticed** - this is why the loss check exists |
| #18 | RV07 and RV08 returned, vetted offline | - |
| #19 | schematics built | 🔴 **one schematic contradicted Table 6** |

### Submission phase - 2026-08-08

| # | What was delivered | What it also found |
|---|---|---|
| #1 | N6 figure renumbering + the `fullSet/` single-document layout | - |
| #2 | SI Tables B1 and C1 cut from the paper (kept on disk - `f5` reads them) | - |
| #3 | **target journal decided: Building and Environment** | - |
| #4 | 13 uncited figures cited, apparatus out of the paper, the B&E framing pass | 🔴 **a Manager-notes block was partly INSIDE the submitted paper**; the DOI banner removed without hiding the problem; Table 6 restructured; **an identifier sweep that had to be reverted** |
| #5 | figures re-rendered at 600 dpi + vector PDF; the B&E requirements prompt | 🔴 **`DEFAULT_AGG` pointed at the superseded arm** - 1 of 5 figures reproduced, 16 `verdict_asmodelled` cells moved. A reopen trigger fired, and it had been written before the fact |
| #6 | RV09 and RV10 returned, vetted, applied | **BUILD NOTES 5 open to 1 open**; a second compliance failure found by checking rather than by being told; one finding **reversed work done two hours earlier** |

### Decision and rendering phase - 2026-08-09

| # | What was delivered | What it also found |
|---|---|---|
| #1 | the three authorial decisions taken; last RV09/RV10 note closed; **the submission `.docx` built** | 🔴 the calibration dispute was settled by a fact **inside RV09 all along**; **Table A2 ships unlabelled** - back to 1 open |
| #2 | the `.docx` made to read like a paper: no thematic breaks, no report notes, single spacing, one bulleted `# References` chapter, 2J cross-cited, image prompts collected | 🔴 **2J was missing from its own successor**; **nine sources were cited with no entry anywhere**; **two of them had never been opened** - back to 2 open |
| #3 | the handoff rebuilt as a full ledger with a table of contents | a dash check reported **281 matches on a file containing zero**, and exited 0 |
| #4 | author-generated images installed; the never-create-images rule written into `CLAUDE.md` and `README.md`; prompts written for all six remaining figures | 🔴 **`f5` reverted the install while checking it**; **C6 passed on a figure whose shipped PNG reads `4.0.1`**; **three generated results figures came back fabricated and were refused** - 3 open |
| #5 | the handoff and this file merged into one director prompt at this path; the 15 installed images re-verified inside the shipped `.docx` | - |

### What the 2026-08-09 round 2 changed, in detail

**No thematic breaks in the submission copy.** Word was showing 60 objects named "Horizontal Line";
they are markdown `---` rules, which pandoc emits as **VML rectangles** (`<v:rect>`). No style setting
could remove them - they are drawings, not text. `strip_for_submission()` now drops every rule, **last,
after the residue and loss checks**, because the section-drop loop uses `---` as a terminator and the
residue check tests for two rules in a row. Built file: 0 `<v:rect>`.

**No report-style notes in the paper.** Six went: the `n/r` legend, `(5 bullets, each <=85
characters.)`, the front-matter note, the Table 1 differentiation note, and two "verify against the
master bibliography" asides. Three became `<!-- APPARATUS NOTE ... -->` comments and the strip grew one
new named rule that removes **every** HTML comment that is not already a BUILD NOTE. Deleting them
would have deleted the reason.

**`MARK_SUB` is now `not reported`, not `n/r`.** The legend was solved by making the legend
unnecessary. The marker is still fully visible; only the blockquote that declared the symbol went.

**One `# References` chapter at the end**, bulleted, alphabetised, after the Conclusion and before the
Supplementary material. Chapter 08 was split into `Chapter_08_Conclusion.md` /
`Chapter_09_References.md` / `Chapter_10_Supplementary.md`. Nine sources that were cited with no entry
anywhere are now entered, and the Statistics Canada / NECB / EnergyPlus entries were replaced with 2J's
already-vetted forms so the two papers agree.

**2J is cross-cited.** §1.4 describes 2J's abstract almost word for word while citing the JBPS paper
and the eSim companion instead. 2J is now `Iseri and Hachem-Vermette (under review b)` and is cited at
§1.4, §2.1, §3.6, §7.F and the reference list; the JBPS entry became `under review a`.

---

## Open BUILD NOTE 1 of 3: Table A2 ships unlabelled and uncited

This is a build-mechanism defect, not a content one, and it was found while verifying the .docx.

> `writing/tables/SI/Table_A1_A2.md` carries **two** tables under two `# ` headings.
> `Chapter_10_Supplementary.md:3` has **one** placeholder for the file, and `assemble_3J.py`'s
> `inline_table()` strips every `^# ` line. A1's label is supplied by the placeholder; **A2's is
> deleted.** The AT_RETAIL codebook ships as an unlabelled continuation of the model card, under no
> number, and **no chapter cites "Table A2" anywhere.** In the built docx: "Table A1" 3 times,
> "Table A2" and "AT_RETAIL codebook" zero, while A2's body ships in full.
>
> 🔴 **`f4`'s C7 is structurally blind to it.** C7 checks that every caption it FINDS is cited in
> prose, so it reports 22/22 while a 23rd exhibit rides along unnumbered - the caption was destroyed
> before C7 ever saw the document.
>
> **Two options, and the choice is editorial, which is why it was not patched.**
> **(a, recommended)** A2 is its own SI table: split the file into `Table_A1_model_card.md` and
> `Table_A2_retail_codebook.md`, add a `**Table A2.**` placeholder and caption, and cite it once in
> prose - the natural site is **§3** where the AT_RETAIL rule is defined, or **§2** with the GSS
> cycles, **not §8**. The codebook is about the DATA and the model card is about the MODEL, and a
> reader sent to a model card will not look there for a variable crosswalk.
> **(b)** A2 is part of the model card: fold it in as `### A1.6 - AT_RETAIL codebook per GSS cycle`,
> which needs no new citation because A1 is already cited, and drop the "Table A2" name.
>
> Re-run `f4` afterwards and **expect the exhibit count to move off 22**. If it does not, the fix did
> not take.

---

## Open BUILD NOTE 2 of 3: two references have never been opened

`Kurin et al. 2022` and `Menon et al. 2020` have been cited by name in the SI architecture table since
it was written, and until 2026-08-09 **neither had a reference entry anywhere in the paper**. They are
now entered in `Chapter_09_References.md`.

> Both forms come from the deep-research report family in which **roughly half of all citations have
> been found fabricated**, and neither has been opened through Crossref or a publisher page. The Kurin
> entry is `dr_L3-13` reference 5 **minus** two fields that were self-evidently placeholders in that
> report and were deliberately not carried: a page range `35, 1234-1246` and an OpenReview URL
> `id=e-58pB58p`. The Menon entry is `dr_L3-08` reference 9 verbatim.
>
> **What closes it:** open both and confirm author list, venue and year. That is a deep-research task,
> so it is a `V<NN>` prompt for the author to run externally - **do not search from this session.**

---

## Open BUILD NOTE 3 of 3: the generated-image defects

Recorded on Figure S1's caption in `Chapter_04_ExperimentalDesign.md`. The authors were shown all of
this with the numbers and chose to install anyway (*"juste utiliser ces images, vas-y"*), so it is
recorded, not argued. Regenerating at 4000 px or more would close all four at once.

> 1. 🔴 **Figure S1 is a data figure and its artwork is fabricated.** One bar reads `4.0.1`, which is
>    not a share; the other `0.37`; there is no axis; the footnote reads *"Mechanical, etelorgical
>    ancr of coherotyl electrical and plumbingnoing"*. The caption still says "Measured
>    occupiable-area share", so caption and artwork disagree.
> 2. **Figure 4**'s lower "raw / after projection" panel renders as two empty boxes.
> 3. **Figure 6**'s "Hard Wiring Gate" box renders two blank grey bars where its labels should be.
> 4. **Every generated image is 1376 x 768 px**, about **184 dpi** at the 190 mm page width, against
>    Elsevier's **500 dpi** for combination art. The files replaced were 5400 to 6600 px.
> 5. Figures 1-6, S1, S2 and S3 now have **no vector PDF**; the stale matplotlib PDFs were archived
>    rather than left disagreeing with the new PNGs.

**Revert path:** `writing/submission/figures/archive/superseded_matplotlib/` and
`writing/figures/archive_matplotlib_2026-08-09/`, two independent copies. Copy back and rebuild.

### 🔴 And three generated RESULTS figures were refused

Figures 7, 8 and 9 were generated from the data-carrying prompts and **came back with invented
numbers**. They are quarantined at
`writing/submission/figures/archive/generated_NOT_INSTALLED_data_figures/` and were **not** installed.

| | the frozen deliverable says | the generated image drew |
|---|---|---|
| **Fig 8** office | box 65.4 to 74.8, **max 90.21, entirely below the 100.0 floor** | box about 210 to 367 sitting **inside** a band drawn 168 to 410 |
| **Fig 8** bands | office 100/135/200, retail 80/110/155, hotel 180/240/300 - all different | **one identical band** behind all three |
| **Fig 8** retail | median **75.63, below its 80.0 floor** | median about 240, inside |
| **Fig 7** energy | every value within **plus or minus 2.4%** | a fan from **-34% to +14%** |
| **Fig 9** winter | total peaks about **4200 kW at hour 7** | about **330 kW**, peaking at 18 |

**Figure 8 reverses three of the paper's four headline gate verdicts.** It shows office and hotel
comfortably inside bands the paper reports them failing, which contradicts the abstract, section 5 and
the cover letter's first paragraph. That is why it was not installed on the strength of the earlier
instruction: it is not a rendering defect, it is a different result.

**Figures 10 and 11 needed nothing.** The files supplied for them are byte-identical to the plots
already shipped (md5 `ae4d14cc` and `6f4a6703`), so those two are still the correct 600 dpi figures.

**Figure S3 WAS installed** - it is a schematic, it is clean and correct, and it carries no number.

---

## What is settled, so nobody reopens it

**The calibrated-behavioural-model dispute is CLOSED, and the fact that closed it was inside RV09.**
RV09 marked THIS STUDY "No" on that axis against Table 1's tick. Reading the **column** instead of the
cell settles it: **RV09 marks all TEN rows of its own matrix "No"**, including Widén and Wäckelgård
and Yamaguchi, which it separately certifies as time-use-survey-driven, and its parenthetical for this
study is "gate-tested control" - validation, not a denial that the model is fit to microdata. A column
with zero variance across ten studies cannot un-tick this study specifically. Recorded, not adopted.

Two things fell out of that, and the second is the one worth remembering:

- The novelty claim **never rested on that axis**. It rests on four: time-use-survey-driven,
  multi-channel, forecast to a future year, mixed-use single building.
- 🔴 **One of those four was not a column in Table 1.** *Time-use-survey-driven* was missing from a
  seven-axis matrix, so the table did not score the axis the claim most depends on. **Added.** The
  matrix is now eight axes; §1.2's "six positioning axes" and the caption's "Seven-column" are
  corrected to eight.

Also closed: **Table A1's `Confirmed against` column** is retitled **`Source in the project
repository`** in all three sub-tables, with a paragraph above declaring the convention (internal
paths, not expected to resolve, printed so every number is attributable to a place in the build).
The five `⚠ check source` cells in Table 1 are settled from RV09 full-text readings; markers went
22 to 14. **Not adopted from RV09**, and named in Table 1's Sources so nobody re-imports them: its
calibration column, and its *activity/end-use* verdict for Doma, which contradicts `dr_L3-10` on a
cell `dr_L3-10` does state.

Closed in earlier rounds, do not redo: figure resolution (600 dpi + vector PDF; combination art needs
**500**, and the 300 dpi intermediate was itself wrong), keywords 13 to 6, **no abstract cap** (272
stays), single-anonymized review, both disputed DOIs, the SI cuts of B1 and C1, the target venue, the
figure renumbering, and the whole 2026-08-09 docx cleanup listed in the ledger above.

---

## The work that is left, in the order I would do it

| # | Item | Whose call | Blocking? |
|---|---|---|---|
| 0 | **Decide on the three refused results figures** (BUILD NOTE 3). Either accept the shipped 600 dpi plots as final, or regenerate 7, 8 and 9 with the data prompts and have them checked against the tables again. **Figure 8 as generated contradicts the paper's own abstract** | authors | **yes, if they are to change** |
| 1 | **Settle the Table A2 label** (BUILD NOTE 1). Then rebuild the .md and the .docx and re-run `f4`, expecting the exhibit count to move off 22 | authors choose (a) or (b); execution is mine | **yes** |
| 2 | **Author a `V<NN>` prompt for Kurin and Menon** (BUILD NOTE 2). Two entries, four fields each. The prompt is mine, the search is the author's, run externally | mine to write | **yes** |
| 3 | **Fill the cover letter's placeholders** - handling editor's name, submission date - in `writing/submission/Title_Page_and_Cover_Letter.md`, then render it to .docx the same way. 2J shipped the title page and cover letter as **one** document | authors supply, I render | yes, for submission |
| 4 | **Check the three binding commitments are actually in the cover letter and abstract.** Reconfirming B&E is what made them binding. Check, do not assume | mine | yes, for submission |
| 5 | **The generative-AI declaration.** RV10 item 18 gives Elsevier's prescribed wording; it goes in a dedicated section before the references, required only if such a tool assisted drafting. Whether one did is the authors' statement to make, so nothing was written | authors | yes, for submission |
| 6 | **§1.4's "Leg-1, published as the second journal in this line (2J)"** reads as though Leg-1 and 2J are the same paper. The citations are right either way, so this is wording, not correctness | authors | no |
| 7 | **Table A1's `Source in the project repository` column** is the last report-like element left in the paper. Kept because the authors chose it. It goes on one word | authors | no |
| 8 | **Deferred and still deferred:** N7 (`f3`'s C2 failure list - **do not relax C2**; the 10 entries are the paper-authored schematics and the fix is scope, not threshold) and N8 (`f5`'s C4 converse gap) | mine, when asked | no |
| 9 | **Read the 0J decision letter** if it exists. Cheap, never done, and it tells you which kind of "insufficient quality" B&E meant | authors | no |

---

### 🔴 Refusals still standing. The first one costs money if it is forgotten.

1. **Do NOT tick Gold open access** on RV10's CRKN claim that B&E carries a 100 percent APC waiver for
   Concordia authors. **Same shape as the claim that was wrong for 2J and Springer.** It blocks
   nothing (subscription publishing is free either way) but the list APC is **$3,690 USD** and the tick
   is irreversible. Confirm on Concordia Library's own page first.
2. **The Concordia editor conflict is UNANSWERED, not cleared.** RV10 item 29 named two
   Editors-in-Chief and never listed the subject editors, which is what was asked. An unlisted board
   is not an empty board, and this author line already found such a conflict at another venue.
3. **RV09 reference 5 (Yamaguchi 2017)** states one title and reports a different one as its Crossref
   return. It does not enter Table 1 and fails the cell on two axes under either title, so it blocks
   nothing, but the row is unverified. If exactly one row of RV09 Part B is opened by hand, open it.

Read `deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md` before using either report.

---

## Standing hazards, and every one of them has already bitten this project

- **A gate must be seen failing before it is trusted.** C7 was watched failing on 13 exhibits before a
  single citation was added. `f6`'s C1 was watched failing on 4 of 5 figures before it was believed.
  Write the check first, always.
- 🔴 **A check that REGENERATES its input is not read-only.** `f5`'s C2 arm re-runs the figure scripts,
  which write to the real paths, and it silently reverted a figure install. Snapshot md5s before and
  after any gate whose write behaviour is unaudited.
- 🔴 **A check that validates the GENERATOR is blind to a substituted artefact.** `f5`'s C6 certified
  Figure S1's arithmetic - from the plotting script - while the shipped PNG said `4.0.1`. Ask of every
  check: if someone swapped the output file, would this notice?
- 🔴 **A pattern that does not compile as intended does not error, it matches something else.** A dash
  check written as `grep -c [—–]'` reported **281 matches on a file containing zero**, and exited 0.
- 🔴 **Two signals removed in one edit are not two decisions.** `CONTENT_RESUMES` was narrowed on
  2026-08-08 because a bare table row let an apparatus section leak; `![` was dropped in the same edit,
  though a figure never appears inside an apparatus block. On 2026-08-11 that cost a figure: the
  section drop ran past Figure S3's image and stopped at its caption, and the submission copy shipped
  a caption with nothing above it. **The loss check counts CAPTIONS, so it was structurally blind** -
  the caption is exactly what survived. The assembler now counts IMAGES too, and the build prints
  `captions N, images M`. When you narrow a pattern, narrow one thing.
- 🔴 **A check that counts what it FINDS cannot see what was destroyed before it looked.** `f4`'s C7
  verifies every caption is cited and passed 22/22 while Table A2 shipped with no caption at all. When
  a check enumerates from the artefact, ask what the artefact would look like if an item had been
  deleted upstream - and get the count from an independent source.
- 🔴 **Read the whole COLUMN before believing a cell.** RV09's "No" on our calibration axis looked like
  a finding about us; it was a column that reads No for all ten studies. One cell is an assertion, the
  distribution is the evidence.
- 🔴 **A default inside a pipeline script is not provenance.**
  `3rdJ_09_activityDrivenLoads_4split.py:63` `DEFAULT_AGG` points at `outputs_step8/agg`, the
  **superseded** arm; the canonical deliverable came from `outputs_step8/agg_deliverable`. Rendering on
  the default reproduced 1 of 5 figures and moved **16 `verdict_asmodelled` cells**. Check defaults
  against `V2-G1_FROZEN_DELIVERABLE.md` before re-running anything.
- 🔴 **A similarity check on a plot is nearly blind.** Downsample-and-compare passed on figures built
  from the wrong arm: layout, palette and axis labels are identical no matter what the bars say.
  Re-render at the ORIGINAL resolution and demand byte-identity.
- **Verify the INSTALLED file, not the build output.** In 2J a table column had silently vanished from
  the shipped docx.
- 🔴 **Something the reader sees may not be text at all.** Sixty "Horizontal Line" objects in Word were
  markdown `---` rules rendered as VML rectangles. Every attempt to fix that in a style or a font would
  have failed, because the thing on the page was a drawing. Before treating a rendering complaint as a
  formatting problem, find the object in `word/document.xml` and see what it actually is.
- 🔴 **Write the justification, then test it before it hardens.** A comment in `assemble_3J.py` claimed
  a second bug - a paragraph rendering as a setext H2 - on a correct reading of CommonMark and a wrong
  reading of *pandoc*, which takes setext only from a single-line header. Running the fragment through
  pandoc killed it in one command. A plausible mechanism written into a code comment becomes fact for
  the next reader.
- **Removing the pointer does not remove the thing** when the list is built by DIFFING. Deleting a
  table's placeholder relocates it, in full, into the leftovers appendix. Cutting from the submission
  is `EXCLUDED_TABLES` in `assemble_3J.py`, by name, printed on build. And **cutting from the
  submission is not deleting the artefact**: `Appendix_C_corrections.md` stays on disk because `f5`'s
  C4 and C6 arms read it.
- **A cross-reference that names a SECTION must be re-derived, never remapped.**
- **Dropping a section's heading is not dropping the section**, and the converse also holds - see the
  Table A2 note above. A residue check that looks for the heading is blind both ways.
- **A blind token map across files will corrupt something.** The identifier sweep rewrote 58
  occurrences, garbled prose, and broke file paths inside Sources blocks. Reverted, redone site by site.
- **A check whose meaning flips with its own mode is not a check.** Pin the arm, not the mode.
- **Verify a logged number against the artefact's own columns**, even one that hits a target exactly.
  Do not trust a Progress Log claim, including mine.
- **Residue check and loss check are different checks.** Keep both.
- **Read the gate's own doc before proposing any threshold change.** A basis change that turns FAIL
  into WARN is a band change in disguise. Prefer purely additive fixes.
- **Never count lines with PowerShell** `Measure-Object -Line`; use `wc -l`. `py -3` is the only
  working Python invocation, and prefix it with `PYTHONIOENCODING=utf-8` when a script prints anything
  outside cp1252. **Do not use a bash heredoc for prose containing apostrophes** - it broke a round;
  write the text to a file and `cat` it. `py -3 -c "..."` one-liners have returned empty output in Git
  Bash: write the probe to the scratchpad and run the file.

---

## Hard rules for this phase

- **This is a writing phase. Zero simulation.** No `sbatch`, no cells, no re-runs. Re-rendering a
  figure from frozen aggregates is not simulation, but it is authorisation-gated: say so first.
- **NEVER** run a blocking `srun`, or any Python, on the Speed login node `speed-submit2`. Always
  `sbatch`, always `-t 7-00:00:00`. Flagged three times; one more is account suspension. Irrelevant
  during a writing phase, and that is exactly when it gets forgotten.
- **No band moves, no gate verdict changes, no measured number changes.** The three failing EUI gates
  stay failing; that is the paper's contribution.
- **Archive the predecessor before editing.** Corrections are additive. Guard the copy with
  `[ -s "$BK" ]` in the same command before truncating anything.
- **A reported grep result is not a check.** Read exit codes, and check the pattern compiled.
- **Do not modify `f3`.** Its 4 PASS / 1 FAIL is the correct answer.
- **The assistant NEVER creates images.** Author instruction 2026-08-09, now a hard-rule section in
  `GSSCanada-main/CLAUDE.md` and a bullet in `README.md`. Write the prompt; the author generates; you
  install, verify against the INSTALLED file, and report every defect. **Plotting is not drawing** - a
  matplotlib figure rendered from a frozen aggregate is computation and stays yours. 🔴 **A prompt for
  a figure that carries measured numbers must carry those numbers**, in a table, from the frozen
  deliverable, with file, column and source line named.
- **Deep research is external.** Author the prompt; never run the search. Roughly half the citations
  in the returned reports have been fabricated.
- **Never edit a built artefact by hand.** Every change goes into the sources or the build, and is then
  verified against the installed file.
- **Reply in English.** The author writes in French.

---

## The closure ritual, every round, unprompted

Three artefacts plus memory, in the same response, without being asked:

1. **Progress Log** appended to `writing/implementation/3rdJ_paper_TASKS.md`.
2. **THIS file**, at this exact path - `3J_docs_occ_nTemp/Prompts/RESUME.md` - **edited in place**,
   with the predecessor copied to `archive/` first. Not a new file beside it.
3. **The board republished** at its fixed URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>
4. **Memory** updated (`project_3j_paper_writing.md`, and `feedback_gates_must_be_seen_failing.md` if
   a new failure class was found).
