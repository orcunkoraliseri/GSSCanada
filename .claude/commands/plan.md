Use the **planner** agent.

Read the full project structure (`eSim_occ_utils/`, `eSim_bem_utils/`, `eSim_docs_*/`), the existing `CLAUDE.md`, and `.claude/state.md` first.

Then create:
- `.claude/tasks.md` — session checklist with `## Session: <date>`, `## Goal: <user goal>`, `## Loop: <N>`, and a numbered task list.
- One task document per task in the correct `eSim_docs_*/` folder, named `<TASK_ID>_<short-title>.md`, using the CLAUDE.md template (Aim / Steps / Expected Result / Test Method).

Apply the `@sequential-thinking` and `@task-decomposition` skills. Increment the loop counter in `.claude/state.md`. Do not modify source code.

The goal for this planning session is what I type after `/plan`.