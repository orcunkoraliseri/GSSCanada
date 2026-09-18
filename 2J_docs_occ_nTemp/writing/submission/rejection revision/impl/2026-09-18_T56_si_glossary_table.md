# T56 — write the one SI glossary table the review asked for (plan §5 item 28) — implementation state

Task doc:   this file.
Opened by:  manager, 2026-09-18, plan §5 item 28 (Progress Log (cb)).
Status:     DONE 2026-09-18. Employee: fresh Sonnet.
Scope:      **Writing only. No cluster, no jobs, no numbers re-derived, no images.**

## Why this exists
Plan §7, WP10 spec, carries two separate requirements from reviewer R2-1:
- **"Move to SI"** — the J3 architecture detail goes into the supplementary information.
- **"Plain terms"** — **replace OR gloss** every self-defined label, and **keep one short glossary table in
  the SI.**

The second half has never been delivered. A search of the tables tree and the revision manuscript folder for
"glossar" returns nothing. A one-term gloss was added under the shipped-model line of
`writing/submission/tables/SI/Table_B1_B2.md` on 2026-09-17, and **that is not this deliverable** — it covers
`J3` alone. **`J3` stays in that model-card table, glossed; do not delete the label.** Entry (ca) of the
Progress Log stated the rule as "this label never appears in prose"; that was wrong and is already corrected
in the log. The rule is replace-**or**-gloss.

## What to write
One new file: `writing/submission/tables/SI/Table_SI_glossary.md`.

- A short heading, one or two sentences of caption saying what the table is for, then **one table** with the
  columns: **Term as it appears | Plain-English meaning | Where it is used in the paper**.
- **One row per term that survives into the new text.** A term that WP10 has decided to replace everywhere
  (for example "forecast" → "scenario-based projection") does **not** earn a glossary row; the glossary is for
  terms a reader will still meet. State that rule in the caption so a later editor does not pad the table.
- **Plain-English meaning** is a full sentence a non-specialist reads once and understands. No second
  self-defined label inside the gloss. No maths.
- Keep it short. The review asked for "one short glossary table", so aim for roughly 8 to 14 rows, not 30.

## Your source, and its limits
`manuscript/prep/jargon_inventory.md` (built by T33) is the starting list: every term, its line count, its
line numbers in the archived manuscript, and a **SUGGESTED** plain replacement. Treat those suggestions as
suggestions — you are writing the final wording.

**Two limits you must respect:**
1. The line numbers in that inventory are from `submission/archive/2J_manuscript_submission.md`, the **frozen
   submitted file**. **Never edit anything under `submission/archive/`.** Read it only, and only in chunks —
   never the whole file into context.
2. The inventory's own "WHAT I DID NOT VERIFY" says the SI figure captions were not scanned. If you rely on a
   count, say where it came from and whether you re-checked it.

Also read, because they are the drafts the glossary must agree with:
`manuscript/draft_S2_framework.md`, `manuscript/draft_SI_model_selection.md`,
`manuscript/draft_SI_schedule_completion.md`, `manuscript/draft_S7_limitations.md`, and
`writing/submission/tables/SI/Table_B1_B2.md` (so the `J3` gloss you write matches the one already shipped
there rather than contradicting it).

## Decisions that are already taken — do not reopen them
- `J3` **stays** in the SI model card with its gloss. It also earns a glossary row.
- "forecast" is replaced throughout by "scenario-based projection" (R2-3, accepted). No glossary row.
- The paper says **limitation**, never **failure**. Gate verdicts keep the word FAIL only inside SI scorecards.
- The internal step numbers ("Step-8", "Step-9") are dropped from prose in favour of naming the action. Decide
  and record whether they still deserve a glossary row, given that a reader of the SI scorecards will still
  meet them.

## Checks before you call it done
- Every row's term is one a reader actually meets in the new text or the SI. Say, per row, where.
- No gloss contains another self-defined label.
- No number appears in the table that has not been re-derived elsewhere — the glossary is definitions only.
  If you find yourself wanting to put a number in, leave it out.
- Re-read the caption as a tired non-native English reader. If a row needs a second read, rewrite it.

## Deliverables
1. `writing/submission/tables/SI/Table_SI_glossary.md` — the table.
2. This file filled in: what you wrote, which terms you kept, **which terms you deliberately left out and
   why** (that list is as important as the table), and what you could not check.
3. One line appended to the plan's §9 closure notes is **not** yours to write — the manager does that.

## Ledger
- No cluster jobs. Wrote one new file, `writing/submission/tables/SI/Table_SI_glossary.md` (12 rows),
  2026-09-18. Note: that path resolves under `2J_docs_occ_nTemp/writing/submission/tables/SI/`, the
  same directory that already holds `Table_B1_B2.md`, `Table_A1_A2_A3.md`, `Table_C1_C2.md` and
  `Appendix_D_deviations.md` — not nested inside the `rejection revision` folder (which holds only the
  `manuscript/` drafts and `impl/` task docs, no `writing/` subfolder of its own).

## Verified
- Read `manuscript/prep/jargon_inventory.md` in full (source list, 47 lines).
- Read the four named drafts in full: `manuscript/draft_S2_framework.md` (417 lines),
  `manuscript/draft_SI_model_selection.md`, `manuscript/draft_SI_schedule_completion.md`,
  `manuscript/draft_S7_limitations.md`.
- Read `writing/submission/tables/SI/Table_B1_B2.md` in full (136 lines) — confirmed the shipped `J3`
  gloss already there and matched this table's `J3` row to it rather than contradicting it.
- Beyond the task doc's named list, grepped (not read whole) two more files in the same SI folder,
  `Table_C1_C2.md` and `Appendix_D_deviations.md`, plus `Table_A1_A2_A3.md`, to answer the task's own
  check "say, per row, where" a reader meets each term — the four named drafts alone do not use most of
  these coined labels any more (they were already rewritten in plain words there), but the two
  scorecard tables still do, extensively. This is why the "Where used" column of several rows cites
  Table C1 / Table C2 / Appendix D rather than the four drafts.
- Confirmed by grep (not found) that "frozen frame", "paired frozen-frame", "C-VAE" and "MDLM"/"SEDD"
  do not appear anywhere in the four named drafts.

## Decisions
- **Step-8 / Step-9 (task doc asked me to decide and record this one).** They earn a glossary row.
  Reason: although the four working drafts have already dropped the step numbers from prose, the raw
  labels "Step-8" and "Step-9" are still written, repeatedly, inside `Appendix_D_deviations.md` (a live
  shipped SI file, not an archived or working document), so a reader of the SI as it stands today will
  still meet them.
- Scope expansion beyond the task doc's named source files: the task doc names only the four drafts
  plus `Table_B1_B2.md` as what the glossary "must agree with." Checking only those five files would
  have produced a glossary that omits several terms (Tier 1-4, FailSafe, True-Future-Test, occACT,
  DRIFT_MATRIX) a reader of the actual SI folder still meets today, because those terms live in two
  other shipped SI tables (`Table_C1_C2.md`, `Appendix_D_deviations.md`) that have not yet been through
  WP10's plain-language pass. I read those two tables (grep, not whole-file) and included the terms
  they still use, since the task's own instruction is "the glossary is for terms a reader still meets,"
  and a reader of the SI folder meets these. Recorded as a note inside the new file itself so this is
  not silently assumed.
- Combined "PASS / WARN / INFO / FAIL" into one row rather than four, since all four are one family of
  verdict labels used identically across every scorecard; four separate one-word rows would not read as
  "one short glossary table."
- Combined "Tier 1 / Tier 2 / Tier 3 / Tier 4" into one row for the same reason; the four tiers are one
  fallback mechanism, not four unrelated terms.
- Kept "J3" and "calibrated J3" as a single row (the jargon inventory lists them as two separate lines
  with the same gloss); a second row for the same label would not match the "term a reader still meets"
  test — they are the same word.
- No row for "gate" was drawn purely from the four drafts' own prose, which has already replaced the
  word with "check"/"band"/"ceiling" throughout; the row exists because the word still appears, heavily,
  in the shipped scorecard tables, and cites those tables, not the drafts, as "where used."

## Terms deliberately left out
(Full one-line reasons are written into the glossary file itself, under "Terms considered and
deliberately left out," so they travel with the deliverable. Summary:)
- **forecast** — already replaced everywhere by "scenario-based projection" (R2-3, accepted); no row.
- **calibrated J3** — same label as J3; not a second row.
- **paired frozen-frame / frozen frame** — fully replaced by plain language; not found anywhere in the
  five named files or the two extra SI tables checked.
- **MDLM, SEDD** — each appears once, already glossed in place in Table B1's own text; SI-only per the
  existing decision; not worth a row at this table's length.
- **calibration closure** — the literal phrase was never written anywhere (0 hits, confirmed again by
  this task); it is a framing problem fixed by rewording, not a term to define.
- **hindcast** — ordinary English, not project jargon; already decided, no change.
- **G3, W_2005** — one-off internal shorthand seen once each in a single Table C1/C2 footnote; not on
  the original jargon-inventory list and too minor to add at this table's target length.

## Next
- The glossary itself needs no further work from this task's side.
- Flagged inside the new file for the collector/manager: `Table_C1_C2.md` and
  `Appendix_D_deviations.md` (both in `writing/submission/tables/SI/`) still carry the raw, un-glossed
  forms of Tier 1-4, FailSafe, True-Future-Test, occACT, Step-8, Step-9, DRIFT_MATRIX_1522 and the
  PASS/WARN/INFO/FAIL verdicts throughout their own prose and cells. They have not been through the same
  plain-language pass WP10 already applied to the four drafts and to `Table_B1_B2.md`. This glossary
  table matches what a reader of those two files meets today; if WP10 later rewrites those two tables
  the same way it rewrote the four drafts, several of this glossary's rows (Tier 1-4, FailSafe, occACT,
  DRIFT_MATRIX, Step-8/9) may then need their "Where it is used" column updated or, if the label is
  dropped outright, the whole row removed.
- No number in this table needs re-derivation; every number quoted (the 0% FailSafe rate) is already
  published in the source SI tables cited, not computed by this task.

## Manager ruling, 2026-09-18 (plan log entry (cj))

**ACCEPTED with two wording corrections made by the manager, not by the employee.**

Checked against the three acceptance conditions written into §3 of the prompt file before dispatch:
1. *Every row names where a reader meets the term* — yes, all 12 rows carry a "Where it is used" citation.
2. *No gloss contains a second self-defined label* — yes, re-read row by row.
3. *The terms deliberately left out, with a reason each* — yes, seven of them, and they are written into
   the deliverable file itself rather than only into this doc, which is the right place for them.

Row count is 12, inside the 8-14 target. **The row count must not grow**; the review asked for one *short*
table.

**The one substantive claim in the table was re-derived, not taken on trust.** The `FailSafe` row asserts the
last-resort tier was never triggered. Source found and quoted: `Table_C1_C2.md:22`
(`FailSafe tier share | 0% | PASS`) and `Appendix_D_deviations.md:83,85`
("FailSafe = 0% (all 286,537 Census agents matched in Tier 1-3)"). The claim is sourced. **The unit was
wrong, though**: both the `Tier 1/2/3/4` row and the `FailSafe` row said **household** where the source says
**Census agent**, i.e. a person. Tier matching is person-to-diary; 286,537 agents live in 144,507 households,
so the two are not interchangeable and a reviewer who checks Appendix D against the glossary would find the
mismatch. Both rows corrected in place to "person". **Lesson, consistent with (ce): a gloss inherits the
unit of the thing it glosses, and a plain-English rewrite is exactly where a unit quietly changes.**

**The employee's scope expansion is upheld.** It read two SI files the brief did not name
(`Table_C1_C2.md`, `Appendix_D_deviations.md`) because the brief's own test is "a term a reader still meets",
and a reader of today's SI folder meets Tier 1-4, FailSafe, occACT, Step-8/9 and DRIFT_MATRIX there. Without
that expansion the table would have been a glossary of the four rewritten drafts, which need no glossary.
Recording the expansion inside the deliverable rather than assuming it silently is the behaviour wanted.

**New carry-in for WP10/Step 13, recorded here and in the plan, not acted on now:** `Table_C1_C2.md` and
`Appendix_D_deviations.md` have **not** had the plain-language pass that the four drafts and
`Table_B1_B2.md` had. That is not a defect in this table — the glossary is written to match the SI as it
actually ships today. But WP10 must decide one of two things and cannot leave it open: either those two
tables keep their raw labels (and this glossary carries them, unchanged), **or** they are rewritten too, in
which case the "Where it is used" column of the Tier, FailSafe, occACT, Step-8/9 and DRIFT_MATRIX rows is
stale and those rows are removed or re-pointed. **Whichever is chosen, glossary and tables are re-read
against each other once, in the same sitting.**

Not verified by the manager either: the `C-VAE` row's claim that the term survives in the main text rests on
`jargon_inventory.md`'s count of 3 lines, not on a re-read of that section; WP10 confirms it when it rewrites
the Introduction. If `C-VAE` turns out to be replaced everywhere, its row goes.

## WHAT I DID NOT VERIFY
- Did not open `Table_A1_A2_A3.md` in full, only grepped it for the term list (one hit, a file-path
  citation containing "Step-9", not a reader-facing use) — did not read it end to end for other possible
  jargon beyond the audited list, since the task doc scoped source-checking to the jargon inventory's
  own terms, not a fresh audit of every SI file.
- Did not check the archived, frozen submission (`submission/archive/2J_manuscript_submission.md`)
  beyond what `jargon_inventory.md` already reports; per the hard rule, that file was not opened at all
  in this task, only its line numbers as already tabulated in the inventory were relied on.
- Did not verify whether "C-VAE" is actually still present in whichever main-text section carries the
  Introduction/Methods (not among the four drafts this task was given); relied on the jargon inventory's
  own count (3 lines) and the standing decision (R1-D3, define at first use) rather than re-reading that
  section, which was outside this task's named source list.
- Did not check the SI Appendix figure captions for further occurrences of any term; the source
  inventory itself already flags this as unchecked, and this task did not extend that check.
- Did not confirm whether `Table_C1_C2.md` and `Appendix_D_deviations.md` are themselves scheduled for
  a WP10 rewrite (and therefore whether the "Where used" citations to them are durable) — flagged above
  as a question for the manager, not resolved here.
