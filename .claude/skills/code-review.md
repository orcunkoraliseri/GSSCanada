---
name: code-review
description: Structured review checklist for eSim source and plan documents. Read-only, terminal output only.
scope: reviewer
---

# Code Review (eSim)

Reviewer is **read-only**. Output a structured verdict to the terminal. Never edit files, never propose patches as edits — describe the fix in prose with file:line references.

## Verdict format

For each task or file reviewed:

```
<TASK_ID> | <verdict> | <one-line summary>
  - finding 1 (path:line)
  - finding 2 (path:line)
```

Verdicts:
- **PASS** — meets the stated expected result, no issues.
- **NEEDS_FIX** — meets intent but has specific defects to address.
- **FAIL** — does not meet the expected result.
- **REVISE** (plan-mode only) — task as written is not atomic, testable, or correctly routed.

End with overall: `VERDICT: APPROVED | NEEDS_REVISION | BLOCKED`.

## Review checklist — execution mode (MODE B)

Run this list against each completed task. Cite a file:line on every finding.

### Correctness
- [ ] The diff matches the task's stated Expected Result.
- [ ] The Test Method passes (or is documented as run).
- [ ] No silent behavior change in unrelated functions.

### eSim-specific contracts
- [ ] EnergyPlus schedule arrays are exactly length 8760 (or 17520 for 30-min, 105120 for 5-min).
- [ ] Every eppy IDF mutation is followed by `idf.save()`.
- [ ] No raw GSS/Census microdata rows in any log, print, or file output.
- [ ] No hardcoded data, IDF, weather, or EnergyPlus binary paths — all via `occ_config.py` or `eSim_bem_utils/config.py`.
- [ ] `0_Occupancy/DataSources_*` is untouched.
- [ ] Files protected by CLAUDE.md (the three `25CEN22GSS_classification` ML files) are unmodified unless the task explicitly authorized it.

### Pandas / numpy
- [ ] No silent index misalignment on merges (joins use `validate=`, or row counts are asserted).
- [ ] No `inplace=True`.
- [ ] DataFrame schema is preserved (or schema change is the explicit point of the task).

### Concurrency
- [ ] All parallel work uses joblib with `backend="loky"`.
- [ ] `n_jobs` is parameterizable for cluster runs (not hardcoded to `-1`).

### Reproducibility
- [ ] Random seeds set where relevant (numpy, torch/tf, sklearn).
- [ ] Output directory names include a date or run-id token, not "tmp" / "test".

### Style / hygiene
- [ ] No dead code, no commented-out blocks.
- [ ] Imports clean (no unused, sorted by group).
- [ ] Docstrings on public functions describe inputs, outputs, and side effects.

## Review checklist — plan mode (MODE A)

For each task in `.claude/tasks.md` and its linked doc:

- [ ] Doc follows the required template (Aim / Steps / Expected Result / Test Method).
- [ ] Task is atomic (no "and" in the title; one artifact).
- [ ] Expected Result is concrete and measurable.
- [ ] Test Method is executable (named command, named file to inspect, or named metric threshold).
- [ ] Commit type is one of `[data] [ml] [pipeline] [bem] [fix] [docs]`.
- [ ] Routing folder matches content (see `task-decomposition` skill).
- [ ] Dependencies listed if any.

## Tone

Be specific and terse. "FAIL: schedule length 8736 ≠ 8760 at `eSim_bem_utils/inject.py:142`" beats "the schedule looks wrong."
