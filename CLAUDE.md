# CLAUDE.md

## Communication Style

Talk like two friends chatting — casual, short, no jargon. Max 100 words per reply unless the user explicitly asks for a detailed or technical answer. No bullet-point walls, no lengthy explanations. If something needs more depth, ask first: "Want the full details?" Skip the preamble ("Great question!") and go straight to the point.

---

## eSim 2026: Occupancy Modeling

This repo builds residential occupancy schedules for EnergyPlus by aligning Statistics Canada Census data with GSS time-use data, with an ML-based path for newer synthetic populations.

## Environment

- Primary research context: macOS, with Windows use
- Python 3.9+
- Use the repo's existing environment before proposing new packages
- Run scripts manually, one at a time

Key deps: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `tqdm`, `eppy`, `scikit-learn`, `torch` or `tensorflow`

## Agent roles (manager vs. employee)
The user runs a two-agent workflow. Identify which role you are at the start of every session by reading the prompt:

- **Manager (Agent1, generally Opus)** — plans work, debugs, writes the prompts that spawn fresh employee sessions. Owns the task list and reviews the Progress Log; does not normally execute multi-step implementation itself. If the user is talking to you about *what to do*, *how to break it down*, or *what prompt to send to a Sonnet session*, you are the manager.
- **Employee (Agent2, generally Sonnet)** — executes a single task handed off via a manager-authored prompt, then appends a `Progress Log` entry under the relevant task doc. Stays within the scope of the prompt; flags blockers back to the user (who relays to the manager). If you were spawned with a focused task description and an expected deliverable, you are the employee.

When the user says "an agent" without qualifying, ask which role applies if the answer changes your behaviour. Manager prompts to employees should explicitly state: **"You are the employee. Execute the task below and append a Progress Log entry on completion."**

## Important Directories

- `0_Occupancy/`: Census/GSS inputs, processed outputs, model artifacts
- `0_BEM_Setup/`: IDFs, weather files, simulation results
- `eSim_occ_utils/`: occupancy pipeline, `occ_config.py`, optional `GSS_BASE_DIR`
- `eSim_bem_utils/`: BEM integration, `config.py`, optional `ENERGYPLUS_DIR`
- `eSim_docs_occ_utils/`, `eSim_docs_bem_utils/`: workflow docs
- `eSim_tests/`: tests and validation outputs

## Standard Pipeline

Typical Census-year flow:

1. `*_alignment.py`
2. `*_ProfileMatcher.py`
3. `*_HH_aggregation.py`
4. `*_occToBEM.py`
5. `*_main.py`

Meaning: align demographics, match profiles, aggregate households, convert to BEM schedules, then orchestrate the run.

Source schedules are usually 5-minute data, then converted to 30-minute or hourly outputs for EnergyPlus.

## ML Pipeline

Location: `eSim_occ_utils/25CEN22GSS_classification/`

- `run_step1.py`: preprocessing, training, forecasting, validation
- `run_step2.py`: household assembly, profile matching, aggregation
- `run_step3.py`: occupancy-to-BEM conversion

Do not modify these files unless explicitly instructed:

- `eSim_occ_utils/25CEN22GSS_classification/eSim_datapreprocessing.py`
- `eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead.py`
- `eSim_occ_utils/25CEN22GSS_classification/eSim_dynamicML_mHead_alignment.py`

## Working Rules

- Read relevant files before editing
- Preserve workflow, naming, and research assumptions unless asked to change them
- Make the smallest practical change
- Do not invent new pipeline steps, files, or datasets
- Be explicit about assumptions, risks, and validation gaps
- Use exact file references with line numbers when citing code

## Speed HPC Cluster

- Host: `o_iseri@speed.encs.concordia.ca`; login node `speed-submit2` is for job submissions only — do not run any computation, builds, or interactive workloads on it (admin warning: "this node is for job submissions only: no compute").
- **HARD RULE (admin warning 2026-06-10, repeat offence = account suspension): NO bare `python`/`python3` on the login node — ever.** This includes "quick" verification one-liners (`python3 -c`, `python - <<EOF`, glob/line-count scans over result dirs). Every check that runs Python or touches many files MUST be wrapped in the scheduler: `srun -p ps --mem=4G -t 00:30:00 python3 -c '...'` (or an sbatch script). Allowed directly on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `cd`, `ls`, `scp`, `module load`, and single-file peeks (`tail`/`head`/`grep`/`wc -l` on ONE log or csv). Anything iterating over directories or importing pandas/numpy/torch/eppy → srun, no exceptions.
- Always submit every cluster command as a single line (no line breaks), and when instructing the user, label each command explicitly as "locally" or "on the cluster".

## Research and BEM Guardrails

- Treat Census and GSS inputs as research data, not sample data
- Be cautious with demographic mappings, silent cleaning, or formatting changes
- Occupancy output changes can affect IDF inputs, simulation, and reporting
- If a change could alter publishable results, call that out clearly

## Validation

- Prefer the narrowest meaningful check
- For data-processing edits, verify schema, row counts, and sample outputs
- For BEM-facing edits, verify schedule shape, resolution, and compatibility
- If full execution is too expensive, state what was not verified

## Task and Commit Format

Task notes or plans should use:

- aim
- steps
- expected result
- test method

Completed task docs should add a `Progress Log`.

Commit format:

`[type]: Brief description`

Allowed types: `[data]`, `[ml]`, `[pipeline]`, `[bem]`, `[fix]`, `[docs]`

## Multi-Agent Workflow

### Agent Registry

| Agent    | Model             | Permissions         | Primary Write Target              |
|----------|-------------------|---------------------|-----------------------------------|
| planner  | claude-opus-4-7   | plan mode           | `.claude/tasks.md`, `eSim_docs_*/` |
| reviewer | claude-opus-4-7   | read only           | terminal output only              |
| builder  | claude-sonnet-4-6 | bypassPermissions   | src files, `.claude/progress.md`   |
| reporter | claude-opus-4-7   | plan mode           | `eSim_docs_*/` (append only)       |

### Loop Order

1. `/plan` → planner reads project, creates `tasks.md` + task docs in `eSim_docs_*/`.
2. `/review-plan` → reviewer MODE A approves or flags tasks before execution.
3. `/build` → builder executes tasks, appends to `progress.md`.
4. `/report` → reporter appends a Progress Log chapter to each task doc.
5. `/review-execution` → reviewer MODE B checks task docs + source files.
6. Repeat from `/build` until all tasks DONE.
7. Final `/report` → updates `state.md` to `COMPLETE`.

`/run <goal>` runs steps 1–7 autonomously without prompting; it interrupts only on BLOCKED, out-of-allowedPaths writes, or a task that fails twice.

### Task Document Routing

- `eSim_docs_occ_utils/`  → occupancy, GSS/Census, C-VAE, schedule generation
- `eSim_docs_bem_utils/`  → EnergyPlus, IDF, eppy/geomeppy, schedule injection
- `eSim_docs_cloudSims/`  → Calcul Québec / Speed cluster, HPC batch jobs
- `eSim_docs_ubem_utils/` → urban-scale geometry, neighborhood units, aggregation
- `eSim_docs_report/`     → validation, analysis, figures, paper sections

### Reporter Rule

Reporter ONLY appends. It never deletes or reformats existing document content. Each loop's results are permanently recorded as a new dated sub-entry. `.claude/state.md` is the only file the reporter overwrites in full.

### State Files

- `.claude/tasks.md`    — current session task list (planner writes)
- `.claude/progress.md` — execution log (builder appends per task)
- `.claude/state.md`    — loop counter and overall project status (reporter updates)

