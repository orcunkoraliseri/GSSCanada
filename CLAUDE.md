# CLAUDE.md

> # 🔴 TOP RULE — Speed cluster
> **NEVER run blocking `srun` or any python on the login node (`speed-submit2`). ALWAYS `sbatch` — fire-and-forget — then read the output file.**
> Flagged THREE times already. One more = account suspension = all job progress lost.
> Only pattern allowed: `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd <dir> && /path/python script.py args > out.txt"`
> Allowed on login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Nothing else.

## 🔴 Communication — READ THIS FIRST, IT OVERRIDES EVERYTHING

The user cannot follow long or complex answers. Reply in **English** (the user may write in French).

**Every reply uses this shape — nothing else:**

```
• <What is done / what happened — one plain sentence.>

  - <fact 1>
  - <fact 2>
  - <fact 3>        (3–5 bullets max, one short line each)

  Evidence: <path>, <path:line>.

  Next: <the next action, 3–4 words>
```

Good example (copy this style):

```
• EU-02 is finished. NS-02 is now MET for all four selected neighbourhoods.

  - Four live manifest sets created and audited.
  - Bologna reconciliation completed.
  - Final gate audit passed for all four sites.
  - Focused regression suite: 67 passed.

  Evidence: outputs/eu_evidence/X-11/eu02_ns02_gate_audit.json, docs/MVP_european_locations.md:679.

  Next: EU-04 geometry.
```

**Rules:**

1. **Max ~80 words.** One sentence per bullet. If it does not fit, it goes in the doc on disk, not in the reply.
2. **No tables, no headers, no numbered re-derivations, no 🔴/🟢 flags, no bold-everywhere** in chat replies.
3. **No narration.** Do not explain what you checked, how you checked it, what disagreed with what, or how the closure ritual went. State the result only.
4. **No side findings in chat.** New FINDINGs, caveats, "never quote this as…", warnings — write them in the doc, then mention in ONE bullet: "- New finding recorded: FINDING NN (see doc)."
5. **One decision max.** If the user must decide, end with one line: "Waiting on you: D-XX — recommend (a)." No option lists.
6. **No preamble, no recap.** Don't restate the question, don't narrate the plan, don't summarize what you just said.
7. **NEVER create anything not explicitly requested.** No new files, docs, scripts, reports, boards, logs, or "helpful extras". If something extra seems needed, ask in one sentence first.
8. **Every reply ends with `Next:` and the next action in 3–4 words.** Never a sentence, never a paragraph — a short
   noun phrase ("Next: EU-04 geometry.", "Next: nothing owed.", "Next: waiting on D-EU-31."). It is mandatory on
   every reply, including short answers and questions.
9. Details only if asked ("Want details?").

Bad example (never do this): a 400-word reply with a table, three numbered re-derivations, two new FINDINGs explained in full, a closure-ritual walkthrough, and three decisions at the end. The user cannot read that.

## Project

Builds residential occupancy schedules for EnergyPlus from StatCan Census + GSS time-use data; ML path for synthetic populations. Python 3.9+, macOS/Windows. Use the repo's existing environment; run scripts one at a time.

## Directories

- `0_Occupancy/` — Census/GSS inputs, outputs, model artifacts
- `0_BEM_Setup/` — IDFs, weather, sim results
- `eSim_occ_utils/` — occupancy pipeline (`occ_config.py`)
- `eSim_bem_utils/` — BEM integration (`config.py`)
- `eSim_docs_occ_utils/`, `eSim_docs_bem_utils/` — workflow docs
- `eSim_tests/` — tests

## Pipelines

Census flow: `*_alignment.py` → `*_ProfileMatcher.py` → `*_HH_aggregation.py` → `*_occToBEM.py` → `*_main.py`. Schedules: 5-min source → 30-min/hourly for EnergyPlus.

ML: `eSim_occ_utils/25CEN22GSS_classification/` — `run_step1.py` (preprocess/train/forecast), `run_step2.py` (assembly/matching), `run_step3.py` (occ→BEM).

🔴 Do NOT modify unless explicitly told: `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py` (all in `25CEN22GSS_classification/`).

## Working Rules

- Read files before editing. Smallest practical change. No invented pipeline steps, files, or datasets.
- Census/GSS inputs are research data — no silent cleaning or format changes.
- If a change could alter publishable results, say so in one sentence.
- Cite code as `file:line`.
- Validation: narrowest meaningful check (schema/row counts for data edits; schedule shape/resolution for BEM edits). If unverified, say what wasn't.

## Agent roles

Two-agent workflow: **Manager** (Opus — plans, debugs, writes employee prompts, does not implement) and **Employee** (Sonnet — executes one prompted task, appends a Progress Log entry). Identify your role from the prompt; ask if unclear and it matters.

- Spawn **fresh** employee sessions per task, handed off via a written task doc — never resume long threads (token burn).
- **Cheap models for cheap work:** polling, file peeks, log tails, big-file scans → Haiku/Sonnet employee, never Opus. Always pass an explicit model to sub-agents. Poll ≥30 min apart, or not at all — SLURM doesn't need watching.
- Never scan big files (multi-MB logs/CSVs) in the manager's context — delegate.

## 🔴 NO PARKING — state lives on disk, never in an agent's context (hard rule)

*"ne laisse pas parker, pour chaque fois demarrer la nouvelle agent"* (author, 2026-08-17), after one
employee reached **359.7k context** across a 43-minute run — 358k of it cache re-reads — by submitting
jobs and then waiting five times for work that was already finished.

**The failure mode.** An employee submits `sbatch`, spawns a background poll, and stops. Every wake
re-sends its whole transcript, produces nothing, and grows the transcript again. The transcript file
hit 1.9 MB. **Waiting is the most expensive thing an agent can do.**

**The four rules — they bind employees and manager alike:**

1. **An employee never waits.** Submit the job, write the JobID to its implementation doc, **end the
   turn** with "job N submitted, state written to `<path>`". No background polls, no `sleep`, no
   "I'll wait for the notification", no no-op `Bash true` to hold the turn open. Polling is the
   **manager's** job and the manager's alone.
2. **One agent, one task, one turn.** Never `SendMessage` a finished employee back to life to
   continue work — resuming replays the entire transcript. **Spawn a new agent** with a fresh
   context, handed the task doc and the implementation doc. A completed employee is done forever.
3. **Write state before you stop, not after you finish.** Anything the next agent needs — JobIDs and
   their exit codes, output paths, row and column counts actually read, decisions taken, what failed
   and whether a re-run superseded it — goes into the **implementation doc on disk** as it happens.
   Nothing of value may exist only in an agent's context. If an agent dies mid-task, the doc is the
   only thing that survives, and the replacement agent must be able to resume from it cold.
4. **Guard the context.** Never read a multi-MB file into context — use `wc -l`, `grep -n`,
   `tail -c N`, `head`. If an employee passes roughly **150k tokens**, it stops, writes state, and
   says "handoff needed" rather than pushing on.

**Implementation docs.** Long-lived decisions go in the step's own working doc (e.g.
`4J_docs_occ/Step2_docs/4thJ_02_harmonisation.md`). Per-task execution state gets its own file,
created when a task starts and named for the task, not the agent:
`<Step>_docs/impl/<YYYY-MM-DD>_<task-slug>.md`. Minimum contents:

```
# <task> — implementation state
Task doc:   <path to the employee prompt>
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per cluster job: JobID · what · state · exit · output path
## Verified      <- numbers actually read, with where they were read from
## Decisions     <- anything the task doc did not decide, and what was assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

The ledger is append-only. **A failed job is never dropped from it** — it stays with the line that
supersedes it, or the gap gets repaired.

## 🔴 Deep research is EXTERNAL (hard rule)

The assistant never searches literature, verifies citations/DOIs, or spawns research agents. Deliverable = a prompt file the user runs in Gemini Antigravity. Prompts + results live in `3J_docs_occ_nTemp/deepResearch_Resources/` (`V<NN>_*.md` prompts, `RV<NN>_*.md` reports, `00_MASTER_BRIEF_V2.md`, `_RESPONSE_TEMPLATE.md`). Every prompt restates: open sources before citing; verify DOIs via crossref; `NOT FOUND` beats an invented number; never relax a band because our model fails it; no em/en dashes.

## 🔴 NEVER create images (hard rule)

*"tu ne jamais creer des images"* (author, 2026-08-09). No generating/drawing figures, schematics, diagrams, or graphical abstracts. Deliverable = a prompt file under `<paper>_docs_*/writing/submission/figures/Prompts_Images/`; the author generates the image. After install: verify against the *installed* document; snapshot md5s around any gate that re-runs figure scripts (they write to real paths).

**Exception:** matplotlib plots computed by a script from frozen data are allowed — plotting ≠ drawing. Any prompt for a data figure must include the actual measured series in a table, with "no value may be altered".

## Speed HPC (detail)

- Host `o_iseri@speed.encs.concordia.ca`. Login node = submissions only.
- Rule #1: no blocking `srun` (leaves client+tee alive on login node for the whole queue wait → flagged).
- Rule #2: no bare `python`/`python3` on login node, ever — including one-liners. Anything iterating dirs or importing pandas/numpy/torch → `sbatch`.
- Rule #3: **every job requests ≥7-day walltime** (`-t 7-00:00:00`), even 1-minute probes. If partition MaxTime < 7d, use its max.
- Cluster commands: single line, labeled "locally" or "on the cluster".

## Tasks & Commits

Task notes: aim / steps / expected result / test method. Completed docs get a `Progress Log` (append-only — never delete or reformat existing entries).
Commits: `[type]: Brief description` — types `[data]` `[ml]` `[pipeline]` `[bem]` `[fix]` `[docs]`.

## Multi-Agent Loop (when /run or /plan is used)

| Agent | Model | Permissions | Writes |
|---|---|---|---|
| planner | opus | plan mode | `.claude/tasks.md`, `eSim_docs_*/` |
| reviewer | opus | read only | terminal only |
| builder | sonnet | bypassPermissions | src, `.claude/progress.md` |
| reporter | opus | plan mode | `eSim_docs_*/` (append only) |

Loop: `/plan` → `/review-plan` → `/build` → `/report` → `/review-execution` → repeat `/build` until DONE → final `/report` sets `state.md` COMPLETE. `/run <goal>` runs it autonomously; interrupts only on BLOCKED, out-of-path writes, or double failure.

Doc routing: `eSim_docs_occ_utils/` (occupancy/GSS), `eSim_docs_bem_utils/` (EnergyPlus/IDF), `eSim_docs_cloudSims/` (HPC), `eSim_docs_ubem_utils/` (urban), `eSim_docs_report/` (analysis/figures/paper).

State files: `.claude/tasks.md` (planner), `.claude/progress.md` (builder appends), `.claude/state.md` (reporter overwrites).

**After task completion:** archive any `.bak` files in a separate archive folder.
