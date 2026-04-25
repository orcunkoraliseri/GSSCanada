The message I just typed after `/run` IS the goal. Do not ask me anything.

Execute the full agent loop autonomously:

1. **Planner** — read full project structure and `.claude/state.md`, create `.claude/tasks.md` and one task document per task in the correct `eSim_docs_*/` folder for this goal.
2. **Reviewer MODE A** — review the plan.
   - If `APPROVED` → continue.
   - If `NEEDS_REVISION` → silently send the planner back to fix the flagged tasks, then re-review. Repeat until `APPROVED`.
   - If `BLOCKED` → stop and tell me why.
3. **Builder** — execute all unchecked tasks without pausing.
4. **Reporter** — append a Progress Log chapter to each completed task document.
5. **Reviewer MODE B** — review execution.
   - If all `PASS` → reporter updates `.claude/state.md` to `Status: COMPLETE` and the loop ends.
   - If any `NEEDS_FIX` → send the **builder back to those tasks only**, then reporter again, then reviewer again.
   - If any `FAIL` → see interrupt rules below.
6. Repeat from step 5 until clean.

## Interrupt only if

- Reviewer returns `BLOCKED` (decision only the user can make — missing data, ambiguous research intent, conflicting prior decisions).
- A task requires writing outside its agent's `allowedPaths`.
- A builder task `FAILED` twice on the same task across the same goal.

Otherwise run to completion silently. When done, show me:
- The final `.claude/state.md` content.
- The list of task documents created (path + title) for this loop.

## Hard rules during the loop

- Honor every constraint in `CLAUDE.md` (Task and Commit Format, protected ML files, schedule contracts, no hardcoded paths, joblib loky, cluster login is submission-only).
- Reporter is append-only on task documents. State.md is the only file the reporter overwrites.
- Reviewer is read-only — never let it edit.
- The builder never submits sbatch jobs; it produces the script and the literal command for the user.