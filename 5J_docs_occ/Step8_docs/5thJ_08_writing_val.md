# Validation plan — Step 8 (writing)

### 5J occupancy-aware surrogate. Main doc: `5thJ_08_writing.md`

Written 2026-09-28.

---

## Section 1 — Claims

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 1.1 | Every number in the text found in a frozen output file (script lists number, file, row) | all | FAIL |
| 1.2 | Every verdict word (pass, fail, not evaluable) matches the Step 6 SUMMARY | all | FAIL |
| 1.3 | "first" or "to our knowledge" appears only with the logged P1/P4 search on disk | yes | FAIL |
| 1.4 | None of the three "not claimed" phrases appears as a claim | 0 | FAIL |

## Section 2 — Citations

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 2.1 | Every cited work opened (full or abstract, stated in the nearest-work table) | all | FAIL |
| 2.2 | Authors, year, venue, pages match the CrossRef record | all | FAIL |
| 2.3 | Licence credits for INE, ISTAT, UKDS present in the required wording | 3/3 | FAIL |

## Section 3 — Style rules

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 3.1 | No LLM or tool name outside the AI declaration (grep) | 0 | FAIL |
| 3.2 | No process or meta notes in captions or prose ("not comparable", "stated here", history) | 0 | FAIL |
| 3.3 | Limitations say limitation, never failure (gate verdicts keep FAIL) | yes | FAIL |
| 3.4 | Every figure is a script plot from frozen data or an author-made image from a prompt | yes | FAIL |

## Section 4 — Data statement

| Gate | Check | Pass | Severity |
|---|---|---|---|
| 4.1 | No UK-derived output or weight in any released file list | 0 | FAIL |

## Section 5 — Seen failing

* 3.1: plant a tool name in a scratch copy of the manuscript; the grep must hit.
* 1.1: change one number in a scratch copy; the number check must FAIL.
