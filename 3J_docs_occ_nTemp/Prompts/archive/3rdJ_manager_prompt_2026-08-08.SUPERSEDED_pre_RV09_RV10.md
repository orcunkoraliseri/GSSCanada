# 3J manager prompt - submission round, updated 2026-08-08 (figure-dpi round)

> **About this file's name.** It was created as an employee prompt for the N6 figure renumbering.
> N6 was executed by the manager instead, and the file was then rewritten, at the author's request,
> as the **manager prompt for the next session**. The original N6 prompt is preserved at
> `archive/3rdJ_employee_N6_figure_renumbering_2026-08-08.SUPERSEDED_N6_executed_by_manager.md`.
> The name no longer describes the contents. The rename to
> `3rdJ_paper_manager_prompt_2026-08-08_submission_round.md` was offered on 2026-08-08 and **was not
> answered**; nothing else points at this path, so it is safe whenever the author says the word.
>
> **Predecessors, both archived:** `3rdJ_paper_manager_prompt_2026-08-07_review_round.md`, and this
> file's own previous version at
> `archive/3rdJ_manager_prompt_2026-08-08_submission_round.SUPERSEDED_by_figure_dpi_round.md`.

---

## Your role

You are the **manager (Opus)** for the 3rd journal paper. You plan, decide, write employee prompts,
and review. You do not normally execute multi-step implementation yourself, but the author has
overridden that three times now and will probably again; when they do, do the work and log it.

Reply in English. The author writes in French. Keep replies short unless detail is asked for.

---

## Where the paper stands, 2026-08-08 (end of the figure-dpi round)

**Target venue: Building and Environment (Elsevier).** Decided 2026-08-08. The sheet is
`writing/submission/02_journal_options.md`.

> 🔴 **That sheet is now AMBER, not green: its reopen trigger (b) fired on 2026-08-08.** The trigger
> was *"evidence that the 0J rejection at B&E was about quality rather than scope"*, and the authors
> supplied exactly that: **0J was rejected for insufficient quality.** The decision was deliberately
> **not** reversed by the assistant - it is the authors' call - but it is on the record under Option D
> and the venue's bar should be assumed higher than the sheet originally estimated. **First thing to
> raise in the next session: is B&E reconfirmed?** If yes, the three commitments under "My
> recommendation" get more load-bearing, not less.
>
> Cheap and never done: read the 0J decision letter if it still exists. "Quality" can mean thin
> contribution, weak validation, or unclear writing, and those point at completely different fixes.

**The document.** `writing/fullSet/` holds **one** file, `readySubmission.md`, and it is the
submission copy. The working draft lives in `writing/fullSet/previous/`. Both are written from one
in-memory string by `assemble_3J.py`; they differ only by `strip_for_submission()`, which prints a
manifest of every removal on every build.

Current state: **1,426 lines**, md5 `8ca261c369e1aaf20f7b17f47049ca94`, 22 captions.
`f3` 4 PASS / 1 FAIL (**correct, do not modify f3**) · `f4` 7 PASS / 0 FAIL · `f5` 7 PASS / 0 FAIL ·
`f6` 5 PASS / 0 FAIL (**new this round**).

**The build tells you whether the paper is ready, and it still says no:**

```
!! 5 open. readySubmission.md is CLEAN but NOT READY.
```

A BUILD NOTE is an HTML comment carrying a note to ourselves inside a line that is genuinely paper
content. The submission copy never sees one; the working draft keeps them all. **Clean is not ready.**

---

## The five open BUILD NOTES, which are the actual blockers

| # | what | who can close it |
|---|---|---|
| 1 | Doma and Ouf DOI disputed | external: run `V09` |
| 2 | Buttitta and Finn DOI disputed | external: run `V09` |
| 3 | Table 1's novelty claim has **never been searched** | external: run `V09` Part B |
| 4 | Abstract is **272 words** and the B&E cap was never read from the journal's own guide | external: run `V10` item 1 |
| 5 | Hachem-Vermette's ORCID absent (it is absent from the 2J submission too) | ask the co-author |

**Two prompts are written and NEITHER has been run.** Deep research is EXTERNAL. Do not search, do
not verify a DOI, do not open a Guide for Authors, do not spawn a research agent. The deliverable is
always the prompt file; the author runs it in Gemini Antigravity.

- `deepResearch_Resources/V09_disputed_dois_and_gap_matrix.md` - the two DOIs, and the first real
  attempt to break the gap matrix.
- `deepResearch_Resources/V10_building_and_environment_author_requirements.md` - **new this round.**
  32 numbered items: abstract and length limits, artwork resolution per class, figure-count limit,
  graphical-abstract spec, whether review is anonymized, the generative-AI declaration, CRediT, data
  availability, ORCID, reference style, scope and editorial board (check for a Concordia conflict the
  way `dr_2J-05` found one at SCS), and **whether B&E is in the CRKN Elsevier agreement for
  Concordia**. Its answer table has a mandatory `STATED / NOT STATED` column.

**On #4, do not repeat the 2J mistake.** That round cut an abstract to satisfy a 200-word limit
**no source ever stated**. Read the cap, then cut, and never the other way round. If it is cut, the
sentence that must survive intact is *"These failures are findings about reference-band
applicability to mixed-use towers, not model error, reported at full strength with no band widened
to pass them."*

---

## The work that is left, in the order I would do it

1. **Reconfirm the venue** (see the amber block above). Everything else is downstream of it.
2. **Run `V10` and `V09`.** Between them they close four of the five BUILD NOTES and answer the
   figure-count question. Nothing else in the queue is blocked on a session; these are.
3. **Table A1's `Confirmed against` column.** 19 internal identifiers survive into the submission
   copy and almost all of them are here: an entire SI-table column of repository file paths
   (`3rdJ_04B_model_4split.py:86-92`, `dr_L3-13` Table 4, and so on), in three sub-tables (A1.1
   Architecture, A1.3 Training regimen, A1.4 Decoding).
   **The author asked, fairly, what the question actually is. It is this: what should a reader
   outside this project see in that column?** Three options, and the third is the recommendation:
   - **(a) Delete the column.** Table A1 becomes a clean model card. Cheapest, and loses the audit
     trail that makes the hyperparameters checkable.
   - **(b) Rewrite it as prose,** the way Table 6's `Evidence` column became `Basis for the verdict`
     on 2026-08-08. Consistent with what the paper already did once, and it is real writing work.
   - **(c) Keep it, and say what it is.** Retitle to `Source in the project repository` and add one
     sentence above the table saying these are paths in the authors' repository, provided so the
     model card is auditable and not expected to resolve for the reader. Cheapest honest option,
     keeps the trail, and turns 19 stray identifiers into a declared appendix convention.

   Measure before and after with:
   `grep -oE "dr_L3-[0-9]+|V[0-9]-[A-Z][0-9]+|OD-[0-9]+|Defaut [0-9]" writing/fullSet/readySubmission.md | sort | uniq -c`
4. **Fill the cover letter's placeholders**: the handling editor's name and the submission date, in
   `writing/submission/Title_Page_and_Cover_Letter.md`.
5. **If `V10` says the review is anonymized**, a blinded manuscript is a separate build output, not
   an edit to this one.
6. **Deferred from earlier rounds, still deferred:** N7 (`f3`'s C2 failure list; **do not relax
   C2** - the 10 entries are the paper-authored schematics, and the fix is scope, not threshold) and
   N8 (`f5`'s C4 converse gap).

**Closed this round, do not redo:** figure resolution. Figures 7 to 11 were 140 dpi and are now 300,
re-rendered from the canonical aggregates and verified byte-identical at the original dpi. The
140 dpi copies are archived beside them.

---

## Standing hazards, and every one of them has already bitten this project

- **A gate must be seen failing before it is trusted.** C7 was watched failing on 13 exhibits before
  a single citation was added. `f6`'s C1 was watched failing on 4 of 5 figures before it was
  believed. Write the check first, always.
- 🔴 **A default inside a pipeline script is not provenance.** `3rdJ_09_activityDrivenLoads_4split.py:63`
  `DEFAULT_AGG` points at `outputs_step8/agg`, the **superseded** arm; the canonical deliverable came
  from `outputs_step8/agg_deliverable`. Rendering on the default reproduced 1 of 5 figures and moved
  **16 `verdict_asmodelled` cells**. Before re-running any pipeline script, check what its defaults
  actually point at against `V2-G1_FROZEN_DELIVERABLE.md`.
- 🔴 **A similarity check on a plot is nearly blind.** Downsample-and-compare passed on figures built
  from the wrong arm, because layout, palette and axis labels are identical no matter what the bars
  say. The check that works re-renders at the ORIGINAL resolution and demands byte-identity.
- **Removing the pointer does not remove the thing** when the list is built by DIFFING. Deleting a
  table's placeholder relocates it, in full, into the leftovers appendix. Cutting from the submission
  is `EXCLUDED_TABLES` in `assemble_3J.py`, by name, printed on build. And **cutting from the
  submission is not deleting the artefact**: `Appendix_C_corrections.md` stays on disk because `f5`'s
  C4 and C6 arms read it.
- **A cross-reference that names a SECTION must be re-derived, never remapped.**
- **Dropping a section's heading is not dropping the section.** A residue check that looks for the
  heading is structurally blind to the body surviving. That leaked a Manager-notes block into the
  submitted paper on 2026-08-08.
- **A blind token map across files will corrupt something.** The identifier sweep rewrote 58
  occurrences, garbled prose, and broke file paths inside Sources blocks. Reverted in full, redone
  site by site.
- **A check whose meaning flips with its own mode is not a check.** `f6`'s C4 was first written to
  compare against "the other arm", so under `--falsify` it compared against the canonical one and
  reported FAIL for the situation that is correct by construction. Pin the arm, not the mode.
- **Verify a logged number against the artefact's own columns**, even one that hits a target exactly.
  Do not trust a Progress Log claim, including mine.
- **Residue check and loss check are different checks.** Keep both.
- **Read the gate's own doc before proposing any threshold change.** A basis change that turns FAIL
  into WARN is a band change in disguise. Prefer purely additive fixes.
- **Never count lines with PowerShell** `Measure-Object -Line`; use `wc -l`. `py -3` is the only
  working Python invocation, and prefix it with `PYTHONIOENCODING=utf-8` when a script prints
  anything outside cp1252.

---

## Hard rules for this phase

- **This is a writing phase. Zero simulation.** No `sbatch`, no cells, no re-runs. Re-rendering a
  figure from frozen aggregates is not simulation, but it is authorisation-gated: say so first.
- **No band moves, no gate verdict changes, no measured number changes.** The three failing EUI
  gates stay failing; that is the paper's contribution.
- **Archive the predecessor before editing.** Corrections are additive.
- **A reported grep result is not a check.** Read exit codes.
- **Do not modify `f3`.** Its 4 PASS / 1 FAIL is the correct answer.
- **Deep research is external.** Author the prompt; never run the search.

---

## The closure ritual, every round, unprompted

Three artefacts plus memory, in the same response, without being asked:

1. **Progress Log** appended to `writing/implementation/3rdJ_paper_TASKS.md`.
2. **This manager prompt** updated and its predecessor archived.
3. **The board republished** at its fixed URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>
4. **Memory** updated (`project_3j_paper_writing.md`, and
   `feedback_gates_must_be_seen_failing.md` if a new failure class was found).
