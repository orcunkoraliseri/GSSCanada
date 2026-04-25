Use the **builder** agent.

Read `.claude/tasks.md` and the linked task documents. Execute every unchecked `[ ]` task in order.

For each task:
1. Apply `@python-best-practices`, `@data-pipeline`, `@test-writing`, `@bash-automation` as relevant.
2. Implement the task. Run the Test Method.
3. Mark `[x]` in `.claude/tasks.md`.
4. Append a per-task block to `.claude/progress.md` per `@progress-tracking`.
5. Continue immediately to the next task.

Do not pause for confirmation. Honor all hard constraints in `agents/builder.md` (8760 schedules, `idf.save()`, no hardcoded paths, joblib loky, protected ML files untouched, `0_Occupancy/DataSources_*` read-only).

If a task would write outside `allowedPaths`, log `Status: BLOCKED` and move on.