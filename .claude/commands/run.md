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
   - For EACH task in tasks.md, emit a `verify:` line containing the
     literal shell/python command(s) that prove the task is done.
     Examples (not prose, actual runnable lines):
       verify: bash -n Speed_Cluster/foo.sh
       verify: python -m py_compile path/to/foo.py
       verify: python path/to/foo.py --help >/dev/null
       verify: diff <(bash config_to_env.sh configs/F8.yaml) expected_F8.env
     If a task has no programmatically checkable output (pure docs edit),
     write `verify: manual` and one sentence describing what reviewer reads.
     Reviewer B runs these commands verbatim — no interpretation.

2. REVIEWER MODE A (claude-opus-4-7)
   - Read only files within declared session scope
   - Check tasks.md and all task documents
   - If APPROVED → continue immediately
   - If NEEDS_REVISION → fix silently and re-review once
   - If still NEEDS_REVISION → fix again silently
   - If BLOCKED → stop and report to user, explain why

3. BUILDER (claude-sonnet-4-6)
   - Load only skills declared in tasks.md
   - At session start, also load ext_python-pro + thematic ext_*
     declared in tasks.md (persona-merge, see planner.md)
   - Read only files within declared session scope
   - Execute all tasks sequentially without pausing
   - After each task: smoke-test what was just written BEFORE marking [x]:
       - any .sh file written/edited:  bash -n <file>
       - any .py file written/edited:  python -m py_compile <file>
       - any .py with argparse:        python <file> --help >/dev/null
       - any .py loader/translator:    run it once on a real input;
                                       diff stdout against an expected fixture
                                       written in the same task
       - any .yaml file written:       python -c "import yaml; yaml.safe_load(open('<file>'))"
     Failed smoke-test = task NOT marked [x]; log error in progress.md and
     fix before continuing. Do not defer smoke to reviewer.
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
   - For each task: EXECUTE the `verify:` command from tasks.md verbatim
     via Bash. PASS only if the command exits 0 (or, for `verify: manual`,
     after reading the named artefact and confirming it matches the task spec).
     Visual-only review without running the verify command = automatic NEEDS_FIX.
   - Per-task verdict: PASS | NEEDS_FIX
   - If all PASS → update state.md COMPLETE, stop, show summary
   - If NEEDS_FIX → send builder to fix failed tasks only,
     then reporter, then reviewer MODE B again

6. Repeat build → report → review until all tasks PASS or 
   a task FAILS twice on the same issue

7. ARCHIVE (end of pipeline only — runs once after final REVIEWER B = APPROVED)
   - Reporter creates eSim_docs_archive/<YYYY-MM-DD>_<goal-slug>/
   - Reporter copies .claude/tasks.md, .claude/progress.md, .claude/state.md
     into that folder (no rename — preserves filenames for grep)
   - <goal-slug>: first 30 chars of goal, lowercased, non-alphanum → dash
   - Next /run starts with clean working state files
   - If REVIEWER B never APPROVES (BLOCKED or repeated FAIL), no archive
     is written — failed sessions are not archived

Interrupt me ONLY if:
- Reviewer returns BLOCKED (needs a decision only I can make)
- Any task FAILS twice on the same task
- A task requires writing outside declared session scope

On completion show me:
## Session Complete
- Goal: ...
- Status: COMPLETE | BLOCKED
- Reviewer A: APPROVED | NEEDS_REVISION (N revisions)
- Reviewer B: APPROVED (loop N) | NEEDS_FIX (M fix cycles)
- Skills loaded: (list)
- Session scope: (read/write paths used)
- Tasks completed: (list with commit strings)
- Documents created or updated: (list with paths)
- Footprint: (total files read / written across all tasks, from reporter logs)
- Tokens saved by scope limiting: (estimate based on files skipped)
