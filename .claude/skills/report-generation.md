---
name: report-generation
description: How the reporter agent appends Progress Log chapters to task documents and updates state.md — append-only.
scope: reporter
---

# Report Generation

The reporter is the project's institutional memory. Its only job is to **append** results, interpretation, and recommendations to existing task documents — never delete, overwrite, or reformat.

## Hard rules

- **Append-only.** If the Progress Log section already exists in a doc, add a new dated sub-entry under it. Never replace a previous sub-entry.
- **No edits to Aim / Steps / Expected Result / Test Method.** Those are the planner's record of what was intended.
- **Refer, don't restate.** Don't paste the aim back in the Progress Log; the reader has the doc above.
- **Cite specifics.** Filenames, line counts, exact metrics, exact commit type.

## Per-task append template

```
---

## Progress Log

### Session: <YYYY-MM-DD> | Loop: <N>
**Status:** DONE | FAILED | PARTIAL
**Commit:** [type]: brief description

### Results
<What the builder produced. Concrete: file paths, row counts, metric values, test outcomes.>

### Interpretation
<Research-level commentary. Did the result match the aim? Are the occupancy
schedules behaviorally realistic (e.g., morning/evening peaks for residential
dwellings, sleep period 23:00–06:00)? Do EnergyPlus outputs fall within
expected energy ranges for Canadian housing (rough EUI bands by archetype)?
What patterns are worth a follow-up?>

### Issues and Technical Debt
<Failures, partial completions, hardcoded values discovered, deferred edge
cases, suspicious silent assumptions. If none: "None noted.">

### Recommended Next Step
<One sentence. Names a concrete next task or check.>
```

## When the section already exists

Add a new `### Session: <date> | Loop: <N>` block under the existing `## Progress Log` heading. Do not touch prior `### Session:` blocks.

## state.md update

After all task docs are updated, overwrite `.claude/state.md` with:

```
## Project: eSim OpenUBEM-Occupancy
## Last updated: <YYYY-MM-DD>
## Loop: <N>
## Status: IN_PROGRESS | COMPLETE | BLOCKED
## Last session goal: <one sentence>
## Last session result: <one sentence — what shipped>
## Next recommended action: <one sentence — usually the next /plan goal or the next builder task>
```

`state.md` is the only file the reporter overwrites in full. Everything else is append-only.

## Interpretation discipline

The reporter's value is interpretation, not summarization. A reader who only reads the Progress Log should understand:
- whether the result is trustworthy,
- whether it advances the research goal,
- what the next decision point is.

If the reporter cannot answer those three, the report is incomplete — go read the modified files and the test output, then write again.

## Reporter never

- Modifies code.
- Modifies the aim or steps of a task.
- Compresses or rewrites prior session entries.
- Invents results not present in `progress.md` or the modified files.
