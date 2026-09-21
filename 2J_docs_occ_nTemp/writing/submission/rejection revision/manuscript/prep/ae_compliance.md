# Applied Energy submission compliance check

Task doc: `../../impl/2026-09-21_T90_wp13_ae_compliance.md`
Date attempted: 2026-09-21

## Step 1 result: NOT OPENABLE

The live Applied Energy Guide for Authors could not be opened. Every URL tried returned
HTTP 403 Forbidden (Elsevier and ScienceDirect appear to block this tool's automated
fetch), except one, which followed a dead redirect to a generic ScienceDirect journal
browse page (the slug does not resolve there). A control fetch of a neutral, unrelated
page (example.com) succeeded normally, so the fetch tool itself works; the block is
specific to elsevier.com and sciencedirect.com.

URLs tried, and result:
1. `https://www.elsevier.com/journals/applied-energy/0306-2619/guide-for-authors`
   -> 301 redirect to `https://www.sciencedirect.com/science/journal/03062619/publish/guide-for-authors`
2. `https://www.sciencedirect.com/science/journal/03062619/publish/guide-for-authors`
   -> HTTP 403 Forbidden
3. `https://www.sciencedirect.com/journal/applied-energy/publish/guide-for-authors`
   -> HTTP 403 Forbidden
4. `https://www.sciencedirect.com/journal/applied-energy/about/author-guidelines`
   -> HTTP 403 Forbidden
5. `https://www.journals.elsevier.com/applied-energy/guide-for-authors`
   -> 302 redirect to `https://www.sciencedirect.com/browse/journals-and-books` (dead: not the guide)
6. `https://www.elsevier.com/journals/applied-energy/0306-2619`
   -> 301 redirect to `https://www.sciencedirect.com/science/journal/03062619`
7. `https://www.sciencedirect.com/science/journal/03062619`
   -> HTTP 403 Forbidden
8. `https://sciencedirect.com/journal/applied-energy/publish/guide-for-authors`
   -> HTTP 403 Forbidden

Control: `https://www.example.com` fetched successfully (confirms the fetch tool is
working; the 403s are specific to the Elsevier / ScienceDirect domains).

Per the task doc, requirements are never filled from memory. No requirement in the table
below, and no MEETS / DOES NOT MEET verdict, may be produced until the guide is opened by
some other means (for example, the author opening it in a normal browser session and
saving the page or pasting its text, or a manual browser check outside this tool's
sandbox).

## Step 2: requirement table

Not produced. Blocked by step 1 (NOT OPENABLE). No row below is filled from memory;
this table is a placeholder listing only the requirement categories the task doc names,
each marked NOT CHECKABLE until the guide text is obtained.

| Requirement (from task doc list) | Guide wording | Manuscript measurement | Verdict |
|---|---|---|---|
| Article type and length/word limit | not read | not measured | NOT CHECKABLE |
| Abstract length | not read | not measured | NOT CHECKABLE |
| Highlights (number, characters) | not read | n/a (author-owed, not yet written) | NOT CHECKABLE |
| Keywords | not read | not measured | NOT CHECKABLE |
| Graphical abstract | not read | not checked | NOT CHECKABLE |
| Section structure | not read | not checked | NOT CHECKABLE |
| Nomenclature | not read | not checked | NOT CHECKABLE |
| Figure format and resolution | not read | not checked | NOT CHECKABLE |
| Table format | not read | not checked | NOT CHECKABLE |
| Reference style | not read | not checked | NOT CHECKABLE |
| Data availability statement | not read | not checked | NOT CHECKABLE |
| Declaration of competing interest | not read | not checked | NOT CHECKABLE |
| CRediT author statement | not read | not checked | NOT CHECKABLE |
| Generative AI declaration | not read | not checked | NOT CHECKABLE |
| Funding | not read | not checked | NOT CHECKABLE |
| Cover letter | not read | n/a (not yet written) | NOT CHECKABLE |
| Response to reviewers / transfer notes | not read | not checked | NOT CHECKABLE |
| Peer review type (single/double blind) | not read | relevant to whether `submit_check.py`'s master/blinded pair applies (plan `00_REVISION_PLAN.md` line 433) | NOT CHECKABLE |
| Anything else stated | not read | not checked | NOT CHECKABLE |

## Step 3: what the author must supply

Not determined from the guide (step 1 blocked). From the task inputs already on file,
these are known to be author-owed regardless of the guide's exact wording (from plan log
entries (ee)-(eg) and the manuscript's own placeholders):
- Funding statement content (grant numbers, if any).
- CRediT author roles per author.
- Declaration of competing interest (names/relationships, if any).
- Cover letter text.
- Highlights (not yet drafted, per task doc step 4 the employee may not write these).
- Any journal-specific author information (ORCID, affiliations) not already in the
  manuscript metadata.

## `submit_check.py` note

Read only, not run (task doc step: run only if it needs no edits and says what it
checks). The script (`../../../extra/build_scripts/submit_check.py`) takes two file
arguments, `MASTER` and `BLINDED`, and checks formatting invariants (paragraph/image/
table counts, "Figure N" residue, caption forms, reference comma style, default font/
size, double spacing, page-number footer, absence of line numbers, table text size, and
a 9-probe blinding-residue scan comparing an unblinded master against a blinded copy).
This script assumes a **double-blind** submission (it expects a separate blinded file
with author names/affiliations/funding/ORCID stripped). The plan
(`00_REVISION_PLAN.md` line 433) already flags this: "apply its format (blinding only if
double-blind; the 16/6-line master/blinded invariant applies only then)". Whether Applied
Energy uses single-blind or double-blind review is one of the guide items that could not
be read (see table row "Peer review type" above), so **whether this script is the right
gate for Applied Energy cannot yet be decided.** Only one manuscript docx exists in
`../` (`2J_manuscript_AE_revised.docx`); no blinded copy exists yet, so the script cannot
be run as-is regardless.

## Status
NOT OPENABLE at step 1. No further steps performed per task doc instruction.
