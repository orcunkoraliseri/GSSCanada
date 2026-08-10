# 3J manager prompt - THE standing handoff, last updated 2026-08-09 (decisions + .docx round)

> 🔴 **THIS PATH IS THE FIXED ADDRESS OF THE 3J MANAGER HANDOFF.** Instruction from the author,
> 2026-08-08: *"mettre a jour ce prompt ... chaque fois"* - update **this file**, every round, in
> place. A new session is opened by reading this path and nothing else, so:
>
> - **Never create a successor file next to it.** The predecessor gets copied into `archive/` under a
>   `SUPERSEDED_by_<round>` name, and then **this file is edited**. The address never moves.
> - **Never leave it lagging.** It is updated in the same response as the state change it describes,
>   like the Progress Log. A handoff that lags is worse than none, because it is trusted.
> - **The rename question is closed.** The author pointed at this path deliberately, so the path is
>   now load-bearing and stays as it is, misleading name and all. This block is what the name would
>   have said. (For the record: the file began as the employee prompt for the N6 figure renumbering,
>   N6 was executed by the manager instead, and the original is preserved at
>   `archive/3rdJ_employee_N6_figure_renumbering_2026-08-08.SUPERSEDED_N6_executed_by_manager.md`.)
>
> **Predecessors, all archived**, most recent first:
> `archive/3rdJ_manager_prompt_2026-08-08.SUPERSEDED_by_2026-08-09_decisions_and_docx_round.md`,
> `archive/3rdJ_manager_prompt_2026-08-08_submission_round.SUPERSEDED_by_figure_dpi_round.md`,
> `archive/3rdJ_manager_prompt_2026-08-08.SUPERSEDED_pre_RV09_RV10.md`,
> `3rdJ_paper_manager_prompt_2026-08-07_review_round.md`.

---

## Your role

You are the **manager (Opus)** for the 3rd journal paper. You plan, decide, write employee prompts,
and review. You do not normally execute multi-step implementation yourself, but the author has
overridden that four times now and will probably again; when they do, do the work and log it.

Reply in English. The author writes in French. Keep replies short unless detail is asked for.

---

## Where the paper stands, 2026-08-09 (end of the decisions + .docx round)

**Target venue: Building and Environment (Elsevier). RECONFIRMED by the authors 2026-08-09.** The
sheet `writing/submission/02_journal_options.md` is **green again**. Reopen trigger (b) fired on
2026-08-08 (0J was rejected at B&E for insufficient quality, not scope); the trigger was put back in
front of the authors with the bar restated and the venue was chosen again, which is recorded in a
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

**The document.** `writing/fullSet/` holds **one** file, `readySubmission.md`, the submission copy.
The working draft lives in `writing/fullSet/previous/`. Both are written from one in-memory string by
`assemble_3J.py`; they differ only by `strip_for_submission()`, which prints a manifest of every
removal on every build.

Current state: **1,467 lines**, 22 captions. `f3` 4 PASS / 1 FAIL (**correct, do not modify f3**) ·
`f4` 7 PASS / 0 FAIL · `f5` 7 PASS / 0 FAIL · `f6` 5 PASS / 0 FAIL. Every figure is 300 or 600 dpi
with a vector PDF.

**There is now a rendered submission package**, and it did not exist before this round:

```
writing/submission/
  3J_manuscript_submission.md     <- readySubmission.md, figure paths rebased ../figures/ -> figures/
  3J_manuscript_submission.docx   <- 15.1 MB, 22 captions, 15 images, 14 tables
  figures/  figures/SI/           <- 12 PNG + 11 vector PDF, plus the 3 SI figures
  tables/   tables/SI/
  extra/build_scripts/            <- ref_submit.docx, post.py, submit_check.py, copied from 2J
```

Rebuild it with, from `3J_docs_occ_nTemp/`:

```
py -3 writing/fullSet/assemble_3J.py
cd writing/submission
sed 's|\.\./figures/|figures/|g' ../fullSet/readySubmission.md > 3J_manuscript_submission.md
pandoc 3J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 3J_manuscript_submission.docx
```

`ref_submit.docx` carries 12 pt Times, double spacing, black headings, justified body, centred 10 pt
captions. `post.py` sets table text to 10 pt single-spaced. **Verify the INSTALLED docx, never the
build output** - in the 2J round a table column had silently vanished from the shipped file.
**No blinded build is needed**: review is single-anonymized (RV10 item 14).

**The build tells you whether the paper is ready. It reached zero for the first time this round, then
went back to one:**

```
!! 1 open. readySubmission.md is CLEAN but NOT READY.
```

An answered note is rewritten in place as `BUILD NOTE RESOLVED <date> by <what>`. It keeps the words
"BUILD NOTE" on purpose, so the strip and the residue check still catch it, and it stops counting as
blocking. **Deleting the note would delete the reason.** **Clean is not ready.**

---

## The ONE open BUILD NOTE: Table A2 ships unlabelled and uncited

This is a build-mechanism defect, not a content one, and it was found while verifying the .docx.

> `writing/tables/SI/Table_A1_A2.md` carries **two** tables under two `# ` headings.
> `Chapter_08_Conclusion.md:13` has **one** placeholder for the file, and `assemble_3J.py`'s
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

## What this round settled, so nobody reopens it

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
stays), single-anonymized review, both disputed DOIs.

---

## The work that is left, in the order I would do it

1. **Settle the Table A2 label** (the one BUILD NOTE above). Then rebuild the .md, the .docx, and
   re-run `f4`.
2. **Fill the cover letter's placeholders**: handling editor's name and submission date, in
   `writing/submission/Title_Page_and_Cover_Letter.md`. Render it to .docx the same way, and note
   that 2J shipped the title page and cover letter as **one** document.
3. **Write the three binding commitments into the cover letter and abstract** if they are not already
   there - reconfirming B&E is what made them binding. Check, do not assume.
4. **The generative-AI declaration.** RV10 item 18 gives Elsevier's prescribed wording; it goes in a
   dedicated section before the references, required only if such a tool assisted drafting. Whether
   one did is the authors' statement to make, so nothing was written.
5. **Deferred from earlier rounds, still deferred:** N7 (`f3`'s C2 failure list; **do not relax C2** -
   the 10 entries are the paper-authored schematics, and the fix is scope, not threshold) and N8
   (`f5`'s C4 converse gap).

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
  outside cp1252. **Do not use a bash heredoc for prose containing apostrophes** - it broke this round;
  write the text to a file and `cat` it.

---

## Hard rules for this phase

- **This is a writing phase. Zero simulation.** No `sbatch`, no cells, no re-runs. Re-rendering a
  figure from frozen aggregates is not simulation, but it is authorisation-gated: say so first.
- **No band moves, no gate verdict changes, no measured number changes.** The three failing EUI gates
  stay failing; that is the paper's contribution.
- **Archive the predecessor before editing.** Corrections are additive.
- **A reported grep result is not a check.** Read exit codes.
- **Do not modify `f3`.** Its 4 PASS / 1 FAIL is the correct answer.
- **Deep research is external.** Author the prompt; never run the search.

---

## The closure ritual, every round, unprompted

Three artefacts plus memory, in the same response, without being asked:

1. **Progress Log** appended to `writing/implementation/3rdJ_paper_TASKS.md`.
2. **THIS manager prompt**, at this exact path -
   `3J_docs_occ_nTemp/Prompts/3rdJ_employee_N6_figure_renumbering_2026-08-08.md` - **edited in
   place**, with the predecessor copied to `archive/` first. Not a new file beside it.
3. **The board republished** at its fixed URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>
4. **Memory** updated (`project_3j_paper_writing.md`, and `feedback_gates_must_be_seen_failing.md` if
   a new failure class was found).
