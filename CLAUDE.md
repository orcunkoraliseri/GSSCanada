# CLAUDE.md

> # 🔴 TOP RULE — Speed cluster
> **NEVER run blocking `srun` or any python on the login node (`speed-submit2`). ALWAYS `sbatch` — fire-and-forget — then read the output file.**
> Flagged THREE times already. One more = account suspension = all job progress lost.
> Only pattern allowed: `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd <dir> && /path/python script.py args > out.txt"`
> Allowed on login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Nothing else.

## 🔴 Communication — READ THIS FIRST, IT OVERRIDES EVERYTHING

The user finds long, complex answers impossible to follow. Every reply must be:

1. **Short.** Default max ~80 words. Answer first, in one plain sentence. Details only if asked ("Want details?").
2. **Simple.** Plain English, no jargon, no walls of bullets, no headers/tables in chat replies, no long explanations of what you *might* do.
3. **One thing at a time.** Do the asked task, report the result, stop. Do not add options, caveats, next-step lists, or side observations unless asked.
4. **NEVER create anything not explicitly requested.** No new files, docs, scripts, reports, summaries, boards, logs, or "helpful extras" the user did not ask for. If you think something extra is needed, ask in one sentence first.
5. **No preamble, no recap.** Don't restate the question, don't narrate your plan, don't summarize what you just said.
6. Reply in **English** (the user may write in French).

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
