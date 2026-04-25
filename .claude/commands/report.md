Use the **reporter** agent.

Read `.claude/progress.md` and every task document referenced by entries in this loop.

For each completed task, append a Progress Log chapter to its task document using the template in `agents/reporter.md`:

```
## Progress Log
### Session: <date> | Loop: <N>
**Status:** ...
**Commit:** ...
### Results
### Interpretation
### Issues and Technical Debt
### Recommended Next Step
```

If a Progress Log section already exists, add a new `### Session:` block under it — never replace prior entries.

After all task docs are updated, overwrite `.claude/state.md` with the new state snapshot.

CRITICAL: append-only on task documents. Never delete or reformat existing content. Never modify code.