# T39 — Thread dr_2J-12 CARRIED findings into the response map

Task doc and implementation state in one file. Written by the manager 2026-09-16 (plan log (bf) follow-up).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster, no python on Speed.**

Status:     DONE

## Aim
The whole-paper review round (`dr_2J-12`, both Gemini and Fable versions) is closed and vetted
(`deepResearch/dr_2J-12_VETTING.md`). Six quiet fixes plus one new unassigned finding came out of that
vetting and are already written into `00_REVISION_PLAN.md` §5 items 10-15 and the "New, currently
unassigned work" paragraph right after item 15 (lines 482-514). None of these are reviewer requests, so
none of them are rows in `manuscript/prep/response_map.md` yet. Your job is to add them so WP10 (the
manuscript rewrite) does not lose track of them, the same way T33 built the original 42 rows.

## Inputs (read these; do not edit them except response_map.md itself)
- `../00_REVISION_PLAN.md` §5 (lines 470-515) — the six items (10-15) and the new confound/WFH-attribution
  item. Read the exact wording; do not paraphrase from memory.
- `deepResearch/dr_2J-12_VETTING.md` — the source vetting doc each item cites; skim only, to confirm the
  item numbers/labels match (e.g. "Fable M4", "Fable M9", "Fable 4.18").
- `manuscript/prep/response_map.md` — the file you are adding to. Read it in full first (it is short,
  83 lines); match its existing column structure and "Coverage check" convention exactly.
- `manuscript/draft_S7_limitations.md` — read it before deciding item wording lands there, since the new
  confound paragraph and possibly some of items 10-15 may belong in a section that already has a draft.

## What to add
1. A new section in `response_map.md`, after the Reviewer 3 table and before "## Manager check", titled
   `## Quiet fixes and new items (not reviewer-raised, dr_2J-12 vetted)`. Same column structure as the
   existing tables: `ID` (use Q10-Q15 for plan items 10-15, and `Q16` for the new confound/WFH-attribution
   item) · `Plain paraphrase` (max 20 words, describe the fix, not the finding — e.g. "Table 1's Motuzienė
   row wrongly checks 'forecast to future year'; fix the checkmark or soften the citation.") · `Class` (A
   text fix in every case except Q16 which is A + D, since it needs a limitations paragraph AND a change to
   the abstract/highlights framing) · `What we change` · `Where in new manuscript` (use the plan's own
   wording: Q10 = Introduction Table 1, Q11 = Discussion, Q12 = §7/Limitations (old numbering; new
   manuscript has this as the Limitations section, check `draft_S7_limitations.md`'s actual title), Q13 =
   Conclusion + Results §5.2/Table 5, Q14 = Results (SHEU comparison wording), Q15 = one-line author check,
   no manuscript text change until answered, Q16 = Limitations (confound paragraph) AND Abstract/Highlights/
   Fig. 6 caption AND WP1's provisional-framing fix per the plan's own instruction) · `Evidence task(s)`
   (write `dr_2J-12_VETTING.md`, there is no Tnn task for these) · `Status` (WAITING for all seven, since
   none of Introduction, Discussion, Conclusion, or Abstract are drafted yet — check this against the
   `manuscript/` folder listing before writing WAITING; if any target section already has a draft file,
   check whether the fix is actually applied there yet and set DONE or RUNNING accordingly) · `Note` (one
   short line; for Q15 note it is an author decision, not a text fix, until answered).
2. Update the "## Coverage check" line to say `49 rows above` (42 + 7) and add one sentence: "plus 7 quiet
   fixes from dr_2J-12 (Q10-Q16), not reviewer-raised, listed separately above."
3. If, on reading `draft_S7_limitations.md`, any of Q12, Q16 (or others) are already substantively covered
   by its current text, set that row's Status to DONE or RUNNING (not WAITING) and say exactly which
   paragraph/line covers it in the Note column. Do not edit `draft_S7_limitations.md` itself in this task —
   only report what you find in response_map.md.

## Rules
- Never edit `00_REVISION_PLAN.md`, `dr_2J-12_VETTING.md`, or the archive.
- No em dashes and no en dashes in anything you write.
- Do not write manuscript prose into the drafts. This task only updates `response_map.md`.
- Write "NOT VERIFIED" rather than guess a status; re-derive Status from what's actually on disk (the
  `manuscript/` folder listing and file contents), not from what the plan or any other doc claims.
- Append to Ledger/Verified/Decisions/Next below as you go; end the turn when response_map.md is updated
  and this doc is filled in. Do not resume a different task doc.

## Ledger
- No cluster jobs, no python. Local reading and writing only, as required.
- Read `00_REVISION_PLAN.md:460-518` (full §5 plus the "New, currently unassigned work" paragraph) for
  the exact wording of plan items 10-15 and the confound/WFH-attribution item.
- Read `deepResearch/dr_2J-12_VETTING.md` in full (247 lines) to confirm item labels/numbers match the
  plan (Gemini item 9 = Motuzienė/Q10, Fable M4 = Q11, Fable M9 = Q12, Fable M1 = Q13, Fable 4.6 = Q14,
  Fable 4.18 = Q15, Gemini item 8 + Fable S2/4.3 + Fable S8/4.1 = Q16).
- Read `manuscript/prep/response_map.md` in full (83 lines) before editing, to match its exact column
  structure and "Coverage check" convention.
- Ran `ls` on `manuscript/` and `manuscript/prep/`: four draft files exist (`draft_S2_framework.md`,
  `draft_S7_limitations.md`, `draft_SI_model_selection.md`, `draft_SI_schedule_completion.md`) plus the
  three `prep/` files. No Introduction, Discussion, Results, Conclusion, or Abstract/Highlights draft
  exists anywhere in `manuscript/`.
- Read `manuscript/draft_S7_limitations.md` in full (136 lines, the file whose target section, S7
  Limitations, is Q12's and part of Q16's landing spot).
- Grepped (case-insensitive) `manuscript/` for `lighting|daylight|R1|CATI|COLLECT_MODE|collection.mode|
  confound|Motuzien|Table 5|forecast` and read every hit's surrounding context in the four draft files.
- Edited `manuscript/prep/response_map.md`: added the new `## Quiet fixes and new items (not
  reviewer-raised, dr_2J-12 vetted)` section (7 rows, Q10-Q16) between the Reviewer 3 table and
  `## Manager check`, and rewrote the `## Coverage check` line to `49 rows above (42 + 7)` with the
  required one-sentence addition. No other file was edited.

## Verified
- `draft_S7_limitations.md` (Q12's target) does not contain the words "lighting", "daylight", or "R1"
  anywhere in the file; the promised §3.6-to-§7 cross-reference fix is not applied there. Set Q12 to
  WAITING, not DONE/RUNNING.
- `draft_S7_limitations.md` does not contain "CATI", "EQ", "collection mode", or "COLLECT_MODE"
  anywhere; the survey-mode confound paragraph Q16 needs is not present. The file's own "before-and-
  after schedules are not matched household by household" paragraph is about a different thing (the
  T21 household-pool rebuild), not the collection-mode confound. Set Q16 to WAITING.
- `draft_SI_model_selection.md:19` lists "survey collection mode" only as one of 90 input variables fed
  to the generative model's encoder; it is not a discussion of the CATI-to-EQ confound and does not
  satisfy any part of Q16. Confirmed by reading the surrounding context (lines 1-35).
- No file anywhere under `manuscript/` mentions "Motuzienė" (Q10), cites "Table 5" for percentage
  increments in a Discussion context (Q11), states the Conclusion-vs-Table-5 EUI wording (Q13), softens
  the SHEU "validates the model" wording (Q14), or addresses the 3x cohort-size coincidence (Q15).
  Confirmed these target sections (Introduction, Discussion, Conclusion, Results, author-check) simply
  do not exist yet as draft files, so there was nothing further to check for those five.
- Response map now has 49 rows total: the original 42 (28 + 7 + 7, unchanged) plus the 7 new Q10-Q16
  rows in the new section.

## Decisions
- None of Q10-Q16 were set to DONE or RUNNING; all seven are WAITING, matching the task doc's default,
  because the actual read of every existing draft file found none of the seven fixes applied anywhere.
- Q16 mapped to a single row rather than split, since the plan's own text treats the confound paragraph
  and the abstract/highlights/Fig. 6 narrowing as one assignment (to WP1 + WP10), matching the "Where in
  new manuscript" instruction to list all of Limitations, Abstract/Highlights/Fig. 6 caption, and WP1's
  provisional-framing fix together in one cell.
- Used `dr_2J-12_VETTING.md` as the sole Evidence task cell for all seven rows, as instructed (no Tnn
  task exists for these).

## Next
- WP10 drafting: when Introduction, Discussion, Results, and Conclusion get draft files, re-check Q10,
  Q11, Q13, Q14 against them (same grep-and-read method used here for Q12/Q16).
- When the abstract/highlights get drafted or `draft_S7_limitations.md` is revised, re-check whether the
  Q16 confound paragraph and the WFH-attribution narrowing have been added; flip Status accordingly.
- Q15 stays a one-line author question; no manuscript text change is owed until the author answers.

## WHAT I DID NOT VERIFY
- Whether `draft_S2_framework.md` or `draft_SI_schedule_completion.md` contain anything relevant to
  Q10, Q11, Q13, Q14, or Q15: read only the grep hits in those two files (none matched the Q10-Q15
  keywords beyond the generic "forecast"/"lighting" mentions already in their own established context,
  which is unrelated to these seven items) rather than reading both files start to finish; the task's
  scope was `draft_S7_limitations.md` specifically, so this is a narrower check than a full read.
- Whether the plan's own item numbering (10-15) could shift if `00_REVISION_PLAN.md` is edited later;
  took the plan text exactly as read on 2026-09-16 at the line ranges cited above.
- Did not check `writing/submission/archive/` or the vetting doc's own line numbers beyond what was
  needed to confirm the item-label mapping; did not re-verify the vetting doc's underlying Crossref or
  quote checks, since that is the vetting doc's own job, not this task's.
