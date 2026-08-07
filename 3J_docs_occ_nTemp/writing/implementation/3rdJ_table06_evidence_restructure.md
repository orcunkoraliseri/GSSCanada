# Table 6 - move the evidence apparatus to the SI (task spec)

**Created:** 2026-08-06 · **Status:** SPEC WRITTEN, not yet executed
**Follows from:** the user's decision that the submission copy must be a plain paper with no notes
added during the build process.

---

## The problem, stated exactly

The submission strip in `assemble_3J.py` removed 448 lines of build apparatus. **Table 6 is what
survived it, and deliberately so.** Its `Evidence` column is nine cells of repository paths, md5
hashes, SLURM job numbers, French-language quotations from internal implementation docs, and the
phrases "in this task" and "per the standing hard rule".

It was not stripped automatically for one reason: **Table 6 is where the paper is honest about its
additive claim.** The evidence column is what stops "additive by construction" from being an
unsupported assertion. A blind strip would have deleted the caveat and left the claim, which is the
worst possible outcome and the exact failure the manual-strip decision was taken to avoid.

So the fix is not deletion. It is **relocation with compression**.

## Aim

Table 6 in the main text states the verdict and the basis in a form a reviewer can read. The full
evidence trail moves to a new SI table, where repository-level detail belongs and where nothing is
lost.

## Steps

1. **Archive first.** Copy `writing/tables/Table_06_leg2_leg3_delta.md` to
   `writing/tables/archive/Table_06_leg2_leg3_delta.2026-08-06_pre_evidence_relocation.md`.
2. **Create `writing/tables/SI/Table_B2_crossleg_evidence.md`.** It carries the **current Evidence
   column verbatim**, one row per pipeline step, unchanged, including every md5, path, job number
   and quotation. This is a copy operation. **Change nothing in the text you move.**
3. **Rewrite Table 6's Evidence column** as a short `Basis` column, one or two sentences per row,
   written for a reader outside this project. Each cell must state:
   - **what was compared** (for example "the four prototype IDF files as read by both campaigns"),
   - **what was found** (for example "byte-identical"), and
   - a pointer `See SI Table B2` for the detail.
   No file path, no md5, no job number, no French, and never the phrases "in this task", "this
   task", "the standing hard rule", "per the hard rule".
4. **Preserve every verdict exactly.** The `Bit-identical?` column is not touched. Five rows read
   `n/r` (Steps 1, 2, 3, 5, 8), three read `No` (Steps 4, 6, 9), one reads
   `Yes, for the base prototype geometry only` (Step 7). **If your rewrite changes a verdict, you
   have made an error, not an improvement.**
5. **Preserve the Step 9 comparability caveat.** That row carries an unresolved question about
   whether Leg-2's 172.7 figure is electricity-only while Leg-3's is all-fuel, so the two may not
   share a basis. That caveat must survive into the main-text `Basis` cell in plain language, not
   only into the SI. It is a limitation of the comparison itself, and burying it would be the same
   mistake as stripping the column.
6. **Add the SI placeholder.** Whichever chapter or SI section currently carries
   `Table_B1_improvement_rounds.md`, add the matching line for the new table in the same style:
   `**Table B2.** *(insert `Table_B2_crossleg_evidence.md` here)*` with its caption.
7. Rebuild: `PYTHONIOENCODING=utf-8 py -3 writing/fullSet/assemble_3J.py` and confirm Table B2 is
   inlined at a placeholder, not appended to the leftovers appendix.

## Expected result

- Main-text Table 6: 9 rows, columns `Pipeline step | Leg-2 artefact | Leg-3 change | Bit-identical? |
  Basis`, readable by someone who has never seen this repository.
- SI Table B2: the full evidence trail, nothing lost.
- Every verdict identical to before.

## Test method

Do all four, and paste the output of each:

1. **Verdict invariance.** Extract the `Bit-identical?` column from the archived copy and from the
   rewritten table and diff them. The diff must be empty. This is the load-bearing check.
2. **Apparatus absence in the main table.** Grep the rewritten Table 6 for: `md5`, a 32-hex string,
   `.py`, `.md`, `Leg2_2-split/`, `Leg3_4-split/`, `in this task`, `standing hard rule`, `job `.
   Zero hits. Grep the new SI table for the same and expect **many** hits, which confirms the content
   moved rather than vanished.
3. **Nothing lost.** Every 32-hex md5 present in the archived copy must be present in SI Table B2.
   Count them in both and compare the counts, and list any that are in one and not the other.
4. **`py -3 writing/implementation/f4_prose_rules_check.py`** must stay at 6 PASS / 0 FAIL, and
   `assemble_3J.py` must still print `readySubmission.md ... OK` with no MISMATCH.

## Hard rules

- No em dashes, no en dashes.
- No number changes. No band moves. No gate verdict changes.
- Do not touch any file other than the two tables, the one chapter or SI file gaining the
  placeholder, and the archive copy.
- `py -3` only. Never count lines with PowerShell; use `wc -l`.
- Corrections are additive: archive before editing, never delete a caveat.
