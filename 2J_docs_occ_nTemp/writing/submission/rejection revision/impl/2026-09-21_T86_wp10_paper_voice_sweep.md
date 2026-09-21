# T86 — WP10: remove project-process ("notebook") wording from the manuscript — implementation state

Task doc:   this file. Author instruction 2026-09-21: "do not mention WP (work packages) in the manuscript,
            this is a paper, not a notebook." Plan log (ec).
Status:     DONE
Agent:      fresh Sonnet employee, text only. No cluster, no web, no python except the pandoc checks below.

## Goal
`../manuscript/2J_manuscript_AE_revised.md` must read like a journal paper. Remove wording that describes
how the project was run rather than what the study did.

## What counts as notebook wording (rewrite or delete)
- Work packages, task IDs (T-numbers), gate IDs, plan items, "ruling", "manager", "assembly", "task doc".
- Drafting talk: "this draft", "read for this draft", "the writer", "marked for the author", "removed
  before submission", "accepted comparison table", "the number sheet".
- Build history: "the rebuild", "rebuilt runs", "previously published (and now superseded) campaign",
  "earlier build", "corrected version of the script", "the original, uncorrected version of the same
  script", "arithmetic error in the script". Rewrite as what the study did, e.g. "the simulations",
  "in this study". Where a sentence exists only to tell the history of a bug fix, delete that sentence.
- Script names, file paths, code identifiers in prose.

## Must NOT change
- Any number, interval, citation, or claim. Rewording only.
- These author placeholders stay exactly as they are: every `[CITATION NEEDED: ...]`, `[NUMBER FROM
  RESULTS]`, `[STATUS TO CONFIRM BY AUTHOR]`, `[NUMBER NEEDED: EUI]`.
- The title line, equations, tables, figure lines (`![](...)`), captions already fixed by the manager.
- "not a forecast"-style negations and "limitation" wording. Never write the word "failure" in prose.
- No em dashes or en dashes anywhere you write (the title is exempt).
- Do not quote "1.0-3.3" percent anywhere.

## Steps
1. `grep -n -i -E "rebuil|draft|superseded|script|uncorrected|task|WP[0-9]|\bT[0-9]{2}\b|ruling|writer|
   number sheet|assembly|earlier build|accepted" ../manuscript/2J_manuscript_AE_revised.md` and read each
   hit in context. Section 5 (Limitations) may keep a plain statement of a limitation, without history.
2. Edit each hit. Keep changes minimal.
3. Re-run the grep; record remaining hits and why each stays.
4. Append one line per edit to `../manuscript/prep/assembly_log.md` under `## T86 paper-voice sweep`
   (line, before, after).
5. Do NOT rebuild the Word file; the manager does that.

## Ledger
(no cluster jobs)

## Verified
- Ran the step-1 grep against `../manuscript/2J_manuscript_AE_revised.md` before and after editing.
  Before: 30 hits across the listed patterns. After: 6 hits, all confirmed false positives (substring
  matches: "manuscript" contains "script", "descriptive"/"description" contain "script") plus one
  deliberate stay (line 967, "could rebuild the same generator..." -- a forward-looking replicability
  claim about other countries, not this project's own build history).
- 12 edits made, one paragraph in Section 3.3 (SHEU check) had its bug-fix-history sentence (the
  original 12-of-48 figure and the arithmetic-error explanation) deleted outright per the task doc's
  "delete that sentence" rule; every other edit is a minimal reword.
- Checked no `failure` and no "1.0-3.3" string exist anywhere in the file (grep, zero hits).
- Checked no em dash / en dash characters were introduced by my edits (grep for U+2013/U+2014 in the
  manuscript and the assembly log; all hits pre-date this task -- title line, reference list page
  ranges, and one pre-existing instruction line in the assembly log that quotes the dash characters
  literally).
- All four author placeholders (`[CITATION NEEDED: ...]`, `[NUMBER FROM RESULTS]`,
  `[STATUS TO CONFIRM BY AUTHOR]`, `[NUMBER NEEDED: EUI]`) still present verbatim; `[NUMBER NEEDED:
  EUI]` sits inside the paragraph I edited (Section 3.3) and was left untouched.
- Appended one entry per edit, plus the remaining-hits explanation, to
  `../manuscript/prep/assembly_log.md` under `## T86 paper-voice sweep`.

## Decisions
- Treated "manuscript" and "descriptive"/"description" grep hits as false positives (they only match
  because the search pattern `script` is a substring of those ordinary words); left them unedited.
- Section 5 (Limitations) paragraph on unmatched before/after schedules: kept as a plain limitation
  statement (household-pool difference, 16,326 vs 16,208, a 320-household gap) per the task doc's
  explicit Section 5 allowance, but removed "rebuilt"/"rebuild"/"earlier build"/"originally submitted
  results" wording in favour of "used here" / "current pool" / "earlier version".
- Line 967 ("could rebuild the same generator...") left unchanged: it is a claim about what another
  country's researchers could do to replicate the method (Section 4, generalizability paragraph), not
  a description of how this project itself was run, so it falls outside the task's "how the project
  was run" scope. Flagged explicitly in the assembly log for the manager to overrule if a stricter
  reading is wanted.
- Section 1.2 companion-line sentence: shortened "its publication status is unconfirmed and marked for
  the author" to "its publication status is unconfirmed" -- dropped the drafting-talk clause only; the
  actual `[STATUS TO CONFIRM BY AUTHOR]` placeholder earlier in the same table row (line 88) is
  untouched, so the author-facing flag is not lost.

## Next
- Manager: rebuild the Word file from this manuscript (not done here, per task doc step 5).
- Manager/author: rule on the one flagged stay-as-is item (line 967, "could rebuild the same
  generator...") if a stricter voice sweep is wanted there too.

## WHAT I DID NOT VERIFY
- Did not re-read the SI file (`2J_SI_AE_revised.md`) or any other manuscript file; task doc named only
  the AE-revised main manuscript.
- Did not rebuild or open the `.docx` output; step 5 explicitly says not to.
- Did not check whether "the project's standard 50-household sample" (Section 3.7, not matched by the
  step-1 grep list) counts as notebook wording; left untouched since it falls outside the specified
  grep and the task doc's explicit "What counts" list does not name "project" as a term to rewrite.
