Use the **reviewer** agent in **MODE A** (plan review).

Read `.claude/tasks.md` and every linked task document in `eSim_docs_*/`.

Verify, per the `@code-review` skill plan-mode checklist:
- Each task follows the CLAUDE.md template (Aim / Steps / Expected Result / Test Method).
- Each task is atomic, testable, and correctly sequenced.
- Dependencies are explicit.
- Acceptance criteria are measurable.
- Commit type is one of `[data] [ml] [pipeline] [bem] [fix] [docs]`.
- Routing folder matches the task's scope.

Output to terminal only. No file writes. Per-task line:
`<TASK_ID> | OK | REVISE — <reason>`

End with overall:
`VERDICT: APPROVED | NEEDS_REVISION | BLOCKED`