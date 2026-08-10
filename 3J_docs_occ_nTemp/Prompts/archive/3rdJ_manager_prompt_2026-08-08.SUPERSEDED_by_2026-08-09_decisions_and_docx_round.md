# 3J manager prompt - THE standing handoff, last updated 2026-08-08 (figure-dpi round)

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
> **Predecessors, all archived:** `3rdJ_paper_manager_prompt_2026-08-07_review_round.md`, and this
> file's own previous versions at
> `archive/3rdJ_manager_prompt_2026-08-08_submission_round.SUPERSEDED_by_figure_dpi_round.md` and
> `archive/3rdJ_manager_prompt_2026-08-08.SUPERSEDED_pre_RV09_RV10.md`.

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

Current state: **1,426 lines**, 22 captions. `f3` 4 PASS / 1 FAIL (**correct, do not modify f3**) ·
`f4` 7 PASS / 0 FAIL · `f5` 7 PASS / 0 FAIL · `f6` 5 PASS / 0 FAIL (**new 2026-08-08**). Every
figure is 300 dpi or 600 dpi and every one has a vector PDF.

**The build tells you whether the paper is ready, and it still says no:**

```
!! 1 open. readySubmission.md is CLEAN but NOT READY.
```

An answered note is rewritten in place as `BUILD NOTE RESOLVED <date> by <what>`. It keeps the words
"BUILD NOTE" on purpose, so the strip and the residue check still catch it, and it stops counting as
blocking. **Deleting the note would delete the reason.**

A BUILD NOTE is an HTML comment carrying a note to ourselves inside a line that is genuinely paper
content. The submission copy never sees one; the working draft keeps them all. **Clean is not ready.**

---

## The ONE open BUILD NOTE, which is the actual blocker

Five were open at the start of 2026-08-08. `RV09` and `RV10` came back the same day, were vetted
against the artefacts, and closed four of them. What is left is one, and it is a claim question, not
a lookup:

> **`RV09`'s competitor matrix marks THIS STUDY "No" on the *calibrated behavioural model* axis,
> while `Table_01_gap_matrix.md` marks the same axis for the same study with a tick.** The report did
> not flag the disagreement. It matters because the unoccupied cell Table 1 claims is defined partly
> by that axis: if the axis reads No for us, the cell is not ours either, and the novelty sentence
> has to be rebuilt on the four axes that are NOT in dispute (time-use-survey-driven, multi-channel,
> forecast to a future year, mixed-use single building), all four of which `RV09` does support.
>
> **Decide what "calibrated" means in this paper, then make Table 1 and the text agree.** That is a
> claim change and it belongs to the authors, which is why it was left open rather than resolved.

**Read `deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md` before using either report.** Neither
was accepted wholesale. Three things in it are refusals, not findings, and the first will cost money
if it is forgotten:

1. **Do NOT tick Gold open access on `RV10`'s CRKN claim.** It says B&E carries a 100 percent APC
   waiver for Concordia authors. That is the same shape of claim that was wrong for 2J and Springer.
   It blocks nothing, since subscription publishing is free either way, but the list APC is
   **$3,690 USD** and ticking the box is irreversible. Confirm on Concordia Library's own page.
2. **The Concordia editor conflict is UNANSWERED, not cleared.** `RV10` item 29 named two
   Editors-in-Chief and never listed the subject editors, which is what was asked. An unlisted board
   is not an empty board, and this author line already found such a conflict at another venue.
3. **`RV09` reference 5 (Yamaguchi 2017) contradicts itself** - one title stated, a different one
   reported as the Crossref return - and it is the closest competitor row in the whole matrix. If
   exactly one row of Part B gets opened by hand, open that one.

Also unanswered and cheap: the **generative-AI declaration** (`RV10` item 18). Elsevier prescribes
the wording and it goes before the references, required only if such a tool assisted drafting.
Whether one did is the authors' statement to make, so nothing was written.

**What the reports settled, so nobody re-opens it:** there is **no abstract word cap** (272 stays,
uncut), **no figure-count limit**, review is **single-anonymized** (no blinded build), keywords cap
at **6** (were 13, now 6), highlights cap at **85 characters** (already compliant), and both disputed
DOIs are corrected.

## The work that is left, in the order I would do it

1. **Reconfirm the venue** (see the amber block above). Everything else is downstream of it.
2. **Settle the calibrated-behavioural-model axis** (the one open BUILD NOTE above), then make
   Table 1 and the §1.2 novelty sentence agree with whatever is decided. While Table 1 is open,
   `RV09` also supplies verdicts for the five `check source` cells it currently carries.
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

**Closed, do not redo:** figure resolution. Figures 7 to 11 were 140 dpi and are now **600 dpi with
a vector PDF each**, re-rendered from the canonical aggregates and verified byte-identical to the
shipped figures at the original dpi. The 140 dpi copies are archived beside them. Note the 300 dpi
intermediate was itself wrong: **combination art needs 500**, and 300 was assumed before `RV10` was
read. Keywords (13 to 6), the abstract cap (there is none), the review model (single-anonymized) and
both DOIs are also closed.

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
2. **THIS manager prompt**, at this exact path -
   `3J_docs_occ_nTemp/Prompts/3rdJ_employee_N6_figure_renumbering_2026-08-08.md` - **edited in
   place**, with the predecessor copied to `archive/` first. Not a new file beside it. The author
   made this explicit on 2026-08-08; see the block at the top.
3. **The board republished** at its fixed URL:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>
4. **Memory** updated (`project_3j_paper_writing.md`, and
   `feedback_gates_must_be_seen_failing.md` if a new failure class was found).
