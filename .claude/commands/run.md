The message I just typed after /run IS the goal.
Do not ask me anything. Do not confirm. Just execute.

Full autonomous agent loop:

1. PLANNER (claude-opus-4-7)
   - Read goal
   - Select minimum skills needed from .claude/skills/
   - Declare session path scope (read/write/off-limits)
   - Create tasks.md with skills list and scope at the top
   - Create task documents in correct eSim_docs_*/ folder
   - Load only selected skills

2. REVIEWER MODE A (claude-opus-4-7)
   - Read only files within declared session scope
   - Check tasks.md and all task documents
   - If APPROVED → continue immediately
   - If NEEDS_REVISION → fix silently and re-review once
   - If still NEEDS_REVISION → fix again silently
   - If BLOCKED → stop and report to user, explain why

3. BUILDER (claude-sonnet-4-6)
   - Load only skills declared in tasks.md
   - Read only files within declared session scope
   - Execute all tasks sequentially without pausing
   - After each task: mark [x] in tasks.md, append to progress.md
   - If a task requires reading outside session scope:
     log SCOPE_BREACH in progress.md and skip that file

4. REPORTER (claude-opus-4-7)
   - Load only: sequential-thinking.md, report-generation.md
   - Read only: progress.md, task documents, state.md
   - Append Progress Log chapter to each completed task document
   - Never delete or overwrite existing content
   - Update state.md with loop count and status

5. REVIEWER MODE B (claude-opus-4-7)
   - Read only files listed in progress.md as modified
   - Do not crawl entire project
   - Per-task verdict: PASS | NEEDS_FIX
   - If all PASS → update state.md COMPLETE, stop, show summary
   - If NEEDS_FIX → send builder to fix failed tasks only,
     then reporter, then reviewer MODE B again

6. Repeat build → report → review until all tasks PASS or 
   a task FAILS twice on the same issue

Interrupt me ONLY if:
- Reviewer returns BLOCKED (needs a decision only I can make)
- Any task FAILS twice on the same task
- A task requires writing outside declared session scope

On completion show me:
## Session Complete
- Goal: ...
- Status: COMPLETE | BLOCKED
- Skills loaded: (list)
- Session scope: (read/write paths used)
- Tasks completed: (list with commit strings)
- Documents created or updated: (list with paths)
- Tokens saved by scope limiting: (estimate based on files skipped)
