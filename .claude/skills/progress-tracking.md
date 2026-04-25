---
name: progress-tracking
description: How the builder records work in .claude/progress.md and updates .claude/tasks.md.
scope: builder
---

# Progress Tracking

The builder is the only agent that writes to `.claude/progress.md`. Reporter reads it and propagates results into the task documents.

## Per-task workflow

For each task the builder completes (or fails on):

1. Do the work.
2. Run the Test Method specified in the task doc.
3. Mark the task `[x]` in `.claude/tasks.md` (or leave `[ ]` and annotate if FAILED/PARTIAL).
4. Append a block to `.claude/progress.md` using the format below.
5. Move to the next task immediately. Do not pause for confirmation.

## Append format (exact)

```
## <TASK_ID> — <ISO datetime, e.g. 2026-04-25T14:32:00>
Status: DONE | FAILED | PARTIAL
Commit: [type]: brief description
Files modified:
  - path/to/file_a.py
  - path/to/file_b.py
Tests: PASS | FAIL | SKIPPED
Notes: <what was done, edge cases, deviations from plan, blockers>
```

Required fields:
- **Status** — one of the three values, no others.
- **Commit** — must use one of the allowed types: `[data] [ml] [pipeline] [bem] [fix] [docs]`. The brief description should be commit-message-quality (≤72 chars).
- **Files modified** — full repo-relative paths, one per line. If none, write `Files modified: (none)`.
- **Tests** — what the Test Method returned. `SKIPPED` requires a one-sentence reason in Notes.
- **Notes** — short paragraph or bullets. Mention anything the reviewer/reporter will need: silent assumptions made, data subsets used, hardcoded fallbacks introduced (which should generally not happen — see `python-best-practices`).

## When a task is BLOCKED

If completing a task would require writing outside the agent's `allowedPaths`, or requires data the user has not provided, or depends on an upstream task that is still pending:

```
## <TASK_ID> — <ISO datetime>
Status: BLOCKED
Commit: (none)
Files modified: (none)
Tests: SKIPPED
Notes: BLOCKED — <one-sentence reason>. Need: <what would unblock>.
```

Do not attempt the write. Do not modify out-of-scope files. Move to the next task.

## What goes in tasks.md vs. progress.md

- `tasks.md` is a checklist. Update only the `[ ]` → `[x]` toggle and (optionally) a one-word status flag at end of line.
- `progress.md` is the durable record. Reporter reads from here.

Never reformat or compress prior `progress.md` entries. Append-only.
