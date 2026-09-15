# T08 — WP12.1: crosswalk leaf-code counts — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` §3 WP12 item 1, §10 Wave 2
Status:     DONE (re-derived from disk; two gaps unresolved, author decision owed)

## Task

**Why.** The activity crosswalk spreadsheet gives leaf-code counts 182 / 265 / 64 / 123, the paper
gives 182 / 264 / 64 / 121. We must know which mapping the pipeline actually used.

**Reading only. No compute, no Speed, no edits to pipeline or archive files.**

**Steps.**
1. Find the crosswalk spreadsheet(s) and the paper sentence/table stating the counts
   (`writing/submission/archive/2J_manuscript_submission.md` and its SI, grep only). Record what the
   four counts refer to (which survey cycles or code families).
2. Find the code that loads the crosswalk (grep the 2J pipeline for the spreadsheet file name and for
   sheet or column names). Record `file:line` and which file/sheet/version it reads.
3. Count leaf codes in the file the code reads, the same way the paper counts them (state how).
   Local python is `py -3`. Scratch scripts go in `T08_scripts/`.
4. For each mismatch (265 vs 264, 123 vs 121): name the exact extra rows, and say whether the pipeline
   consumes them (for example: header row, duplicate, code with no diary occurrences, dropped by a
   filter at `file:line`).
5. Write the result in Verified. Proposed fix in Next: either "paper counts right, spreadsheet has N
   unused rows (listed)" or "paper counts wrong, correct values are …". The author decides; do not
   edit the manuscript.

**Test.** Every count re-derived from a file on disk with the counting rule written down.

**Employee rules.** Plan §10 rules 5–6 apply. Never read a multi-MB file into context.

## Ledger
(no cluster jobs expected)

## Verified

**Step 1 — paper sentence + SI table.**
- Manuscript sentence (`writing/submission/archive/2J_manuscript_submission.md:194`): "the mapping covers
  182, 264, 64, and 121 raw codes for the 2005, 2010, 2015, and 2022 cycles respectively... 0.00%
  unmapped episodes in every cycle (SI Table B2)."
- SI (`writing/submission/archive/submissionDocs/Supplementary_Material/Supplementary_Material.md:266-271`,
  Table B2): same four numbers, 2005=182, 2010=264, 2015=64, 2022=121, "Zero disambiguation conflicts".
- Counts refer to raw GSS episode-activity codes (one GSS diary cycle per codebook sheet) mapped to the
  paper's 14-category `occACT` scheme.

**Step 2 — code that loads the crosswalk.**
`2J_docs_occ_nTemp/02_harmonizeGSS.py`:
- `ACTIVITY_EXCEL` (line 345): `references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`
- `ACT_SHEET_MAP` (347-352): sheets `2005codebook`/`2010codebook`/`2015codebook`/`2022codebook`.
- `build_activity_crosswalks()` (372-391): `openpyxl.load_workbook(..., data_only=True)`, iterates
  `ws.iter_rows(min_row=2, ...)` (row 1 = header, skipped), keeps a row only if col A (category) and
  col B (raw code) are both non-None and col A is not a string; builds `lookup[raw_code] = category`.
  For cycle 2010 only, it ALSO inserts `lookup[int(raw_code)] = category` (line 389) — a second key for
  every decimal-coded row (e.g. `80.1` also aliases to `80`).
- `apply_activity_crosswalk()` (394-428) is where this dict is actually applied to the diary rows via
  `raw_col = "ACTCODE"` (2005/2010) or `"TUI_01"` (2015/2022), plus explicit sentinel overrides
  (995→10 for 2005/2010, 95→14 for 2015, 9999→14 for 2022) applied on top of the crosswalk map.

**Step 3 — re-derived counts (script `T08_scripts/count_crosswalk.py`, `py -3`, local, no Speed).**
Counting rule = same loop the pipeline uses: rows `min_row=2..ws.max_row` of each codebook sheet,
kept iff col A and col B both non-None and col A is not text (identical to `build_activity_crosswalks`
lines 380-390). Ran against the actual file the code reads
(`references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`, workbook sheets
confirmed = exactly `2005codebook/2010codebook/2015codebook/2022codebook`).

| cycle | raw rows in file (kept by pipeline filter) | duplicates found | final crosswalk-dict keys pipeline builds |
|---|---|---|---|
| 2005 | 183 | 0 | 183 |
| 2010 | 266 | 0 (pre float/int expansion) | 308 (float+int alias keys from 125 decimal-coded rows) |
| 2015 | 64  | 0 | 64 |
| 2022 | 123 | 0 | 123 |

**Step 4 — mismatches, named rows, pipeline consumption.**
- **2005 (paper 182, task-doc "spreadsheet" 182 — no listed mismatch, but the raw file is NOT 182):**
  file has 183 rows. Row 2 of `2005codebook` = `(cat=1, code=2, "Work-related")` — a single-digit code,
  out of family with every other 2005 code (all 2–3 digits, 11...995). It is the category-level label
  duplicated as if it were a leaf row. Excluding it gives 182, matching both cited figures. The pipeline
  filter (lines 380-390) does **not** exclude it — `lookup[2] = 1` is written like any other row, so the
  runtime crosswalk table actually has 183 keys, not 182.
- **2010 (spreadsheet 265, paper 264 — gap of 1):** file has 266 rows. Row 265 of `2010codebook` =
  `(cat=1, code=2, "Work-related")` — the identical stray label row, spliced out of numeric sequence
  (between code 995 at row 264 and code 712 at row 266; confirmed no other row with code <10 exists in
  this sheet). Removing it gives 265, which matches the task doc's cited "spreadsheet" figure exactly.
  The pipeline does not filter it out either (`lookup[2.0] = 1`, plus the 2010-only int-alias branch
  also writes `lookup[2] = 1`). **Residual gap: 265 (after removing the one confirmed duplicate) vs
  paper's 264 — still 1 code unexplained.** No second duplicate, header, or sentinel row found: scanned
  all 266 rows for codes <10 (only the one found), for exact duplicate raw codes (none), and for
  int-truncation collisions from the decimal-alias logic (5 found — `810.9`,`862.1`,`862.2`,`951.1`,
  `951.3` — but these affect the *dict key count* [308], not the *row count* used for the paper's prose
  figure, and none of them removes a row).
- **2022 (spreadsheet 123, paper 121 — gap of 2):** file has 123 rows, all unique codes, no rows with
  code <10, no duplicate raw codes. Sentinel-looking codes present and legitimately part of the table:
  `999` ("Civic or religious activities, not stated" → cat 12) and `9999` ("Uncodable/Unknown activity"
  → cat 14, also re-asserted by the explicit override at `02_harmonizeGSS.py:425`, which is redundant
  with — not a replacement for — the crosswalk-table entry). **No row-level explanation found for the
  2-code gap.** The pipeline's filter consumes all 123 rows into the crosswalk dict unmodified.
- File-system check: the Excel workbook's mtime (2026-04-02) predates the archived manuscript's mtime
  (2026-08-13) by over four months, so the spreadsheet was not edited after the paper text was drafted —
  the 264/121 figures were not superseded by a later spreadsheet revision; they simply don't match the
  file that exists today and that the pipeline points at.

## Decisions
- Counted "leaf codes" the same way the paper's prose does: raw (category, raw-code) rows per codebook
  sheet, header row excluded, no assumption about diary occurrence (not checked — see below).
- Treated the single-digit `code=2 "Work-related"` row found identically in both the 2005 and 2010
  sheets as a duplicate/mislabeled category-header row, not a genuine leaf code, because (a) it is the
  only code under 10 in either sheet, (b) in 2010 it sits completely out of numeric sequence, and (c) its
  own text label ("Work-related") matches the *category name*, not an activity, unlike every other row.
  This is inference from spreadsheet structure only — not confirmed against StatCan's codebook PDF or
  against real diary data.

## Next
**Manager 2026-09-15 — one untested explanation before asking the author.** The paper may have counted
codes that OCCUR in the diary episodes, not rows in the codebook sheet. Test: distinct `ACTCODE`
(2005/2010) and `TUI_01` (2015/2022) values in the raw episode files the pipeline reads, and which
codebook codes never occur (expected: 2010 misses 1 besides the stray `2`, 2022 misses 2). Small
follow-up task, run as a Speed job (all compute goes to Speed). If it
explains both gaps, the paper is right and the SI note says "codes observed in the diaries".
Earlier collector note: Author decision owed on two things this task could not settle by reading alone:
1. **2005/2010 duplicate row**: confirm (or have someone confirm from the StatCan codebook) that raw
   code `2` never occurs in real `ACTCODE` diary data for 2005/2010. If confirmed, the paper's 182/264
   undercounts the *pipeline's actual crosswalk table* by 1 in 2010 (dict really has 265 usable codes
   after removing the duplicate, not 264) and its 183-row 2005 sheet by 1 (183, not 182, though the
   duplicate is harmless there too, going into the 182 count either way once excluded).
2. **2010 (265 vs 264) and 2022 (123 vs 121) residual gaps**: not explained by any row structure found
   in the current spreadsheet — no further duplicates, header rows, or filtered-out rows exist. Options
   for the author: (a) paper counts are simply wrong, correct values are 182/265/64/123 (what the
   pipeline reads today, after excluding the one confirmed 2005/2010 duplicate); or (b) the 264/121
   figures came from an older/different version of the spreadsheet no longer on disk, in which case the
   author needs to locate that version — this task did not search version history or backups.
Do not edit the manuscript; this doc only records the re-derivation for the author to act on.

## WHAT I DID NOT VERIFY
- Whether raw code `2` (the stray "Work-related" row in 2005/2010) ever actually occurs in real
  `ACTCODE` diary episodes — would require reading GSS microdata, out of scope ("reading only, no
  compute" — and the task doc restricts this task to the crosswalk file itself).
- Whether the pipeline's actual harmonized output (`occACT`) for 2005/2010 was ever materially affected
  by the stray row (i.e. whether any respondent-episode got mapped through `raw_code=2`) — not checked;
  would need the merged/harmonized GSS output, not opened here.
- Where the paper's specific 264 (2010) and 121 (2022) figures came from if not this spreadsheet — did
  not search git/version history, `.bak` files, or older spreadsheet copies for a prior version that
  might literally have 264/121 rows.
- Did not open the StatCan GSS codebook PDFs (if any exist in the repo) to independently confirm code
  `2`'s status as a category header rather than a leaf code — conclusion rests on spreadsheet structure
  (digit-length pattern, out-of-sequence position, label text) only.
- Did not check `2015codebook` or `2022codebook` sheets for XML-level hidden rows/filtered rows beyond
  what `openpyxl` with `data_only=True` exposes (e.g. no check for hidden rows, grouped rows, or rows
  outside `ws.dimensions` that Excel might still store).
