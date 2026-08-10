# CLAUDE.md

> # 🔴🔴 ABSOLUTE TOP RULE — READ FIRST, NO EXCEPTIONS 🔴🔴
> **NEVER run a blocking/interactive `srun` (or any python/computation) on the Speed login node (`speed-submit2`). ALWAYS use `sbatch` — fire-and-forget — and read the output file afterward.**
>
> A blocking `srun ... | tee` leaves its srun client + `tee` + `tcsh` wrapper alive on the login node for the WHOLE queue wait (hours when saturated). The admin monitor flags this as compute-on-login. **This has been flagged THREE times. One more = account suspension = ALL job progress lost. There is no apology that fixes a ban.**
>
> Correct pattern (the ONLY way to run cluster compute):
> `sbatch -p ps --mem=16G -t 00:30:00 --wrap "cd <dir> && /path/python script.py args > out.txt"`
> → returns a job id instantly, leaves NOTHING on the login node. Read `out.txt` later with `tail`/`cat`.
> Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. NOTHING else. (Full detail in the Speed HPC Cluster section below.)

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

### Session hygiene — fresh employee sessions, not long resumes
Do not repeatedly resume the same employee agent session across multiple tasks or sub-investigations. Resuming re-sends the ENTIRE accumulated transcript as context every time — on a long-lived thread (large file reads, multi-MB logs/CSVs/IDFs) this burns a large amount of tokens per resume.

- For each new task, write (or update) an **implementation-plan / task doc** — `.claude/tasks.md`, a task doc under `eSim_docs_*/`, or a dedicated status/TASKS doc — that captures the decisions and state the next session needs.
- Then spawn a **fresh** employee session for that task and point it at the doc for context, instead of resuming the old thread.
- Treat the written doc, not the agent's own conversational memory, as the source of truth for handoff context.
- Only resume an existing agent thread when no written tracking doc exists yet to hand a fresh agent instead.

### Cost rule — cheap models for cheap work (HARD RULE)
Monitoring/`squeue`/`sacct`/`scancel` polling loops and any other mechanical, repetitive, or low-reasoning job (status checks, file existence/size peeks, log tails, simple scp uploads, waiting on jobs) are **cheap-model duties — use Haiku or Sonnet, never Opus.**

- Background/sub-agents **silently inherit the parent's model (Opus) when no model is set.** A poll loop spawned without an explicit model becomes a *second full Opus* burning premium budget to ask "done yet?". ALWAYS pass `model: haiku` (or `sonnet`) on the Agent tool for these.
- Better still: **do not run live poll loops at all.** SLURM finishing does not need watching. The employee/user relays the job numbers; the manager (Opus) only acts on terminal results.
- **Minimum monitoring frequency = 30 minutes.** When a job/task genuinely must be polled, space checks at least 30 min apart — never poll continuously or simultaneously. One status check, then wait ≥30 min before the next.
- **Never scan big files yourself — delegate to a cheap-model employee.** Reading/scanning/parsing large files (big `.csv`, multi-MB logs, large data dumps, the augmented diaries ~500 MB, etc.) must be handed to a Haiku/Sonnet employee, never done in the manager's own context (it overflows context and burns Opus tokens). The manager writes the analysis script + says what to extract; the employee runs it and returns only the small result table.
- Reserve Opus for what actually needs it: planning, debugging, analysis, writing prompts. If a task is a `while`-loop of the same command, it is not an Opus task.

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

## Deep research is EXTERNAL — author the prompt, never run the search (HARD RULE)

**The assistant does not perform deep research.** Literature searches, citation and DOI verification,
reference-band derivation and any other "go read the sources and come back with numbers" task are run
by the user in an **external deep-research tool (Gemini Antigravity)**, not in this session and not by
sub-agents.

The assistant's job is to **write the prompt document** that gets pasted into that tool, and later to
read, verify and act on the report that comes back.

- **Do not spawn research agents.** No `Agent` calls to search the web for sources, verify DOIs, chase
  report numbers, or compile reference tables. If a task needs external evidence, the deliverable is a
  prompt file, not an answer.
- **Where prompts and results live:** `3J_docs_occ_nTemp/deepResearch_Resources/`. Prompts and their
  results sit in the **same directory**.
  - `00_MASTER_BRIEF_V2.md` — shared context, pasted ahead of every prompt
  - `_RESPONSE_TEMPLATE.md` — the response schema (Sections A to H) the external tool must follow
  - `V<NN>_<topic>.md` — one prompt per topic
  - `RV<NN>_<topic>.md` — the returned report for that prompt
- **Prompt house style** (modelled on `idf_reader/docs_ACTIVE/LMN-1983/DeepResearch/NUs/`):
  `# V<NN>. Title`, then a pointer line to the master brief and response template, then
  `## Why we are asking` (the concrete situation that makes this worth asking),
  `## What we need` (numbered, specific, each item answerable),
  `## Named leads` (real institutions, databases and document families to try), and
  `## Deliverable` (what the answer's key section must contain, including what to write if the
  evidence does not settle it).
- **Rules to restate inside every prompt:** a citation is not evidence until opened; verify DOIs via
  `https://api.crossref.org/works/<DOI>` and report numbers by opening the PDF; `NOT FOUND` beats an
  invented number; never propose relaxing a band because our model fails it; keep as-modelled and
  empirical figures strictly separate; no em dashes or en dashes in the returned text.


## The assistant NEVER creates images — it writes the prompt (HARD RULE)

**Instruction from the author, 2026-08-09: *"tu ne jamais creer des images."*** The assistant does not
generate, draw, synthesise or render any figure, schematic, diagram, icon or graphical abstract that
will appear in a paper. This is the same division of labour as the deep-research rule above: **the
assistant's deliverable is a prompt document, not the artefact.**

- **What the assistant produces:** a prompt file under
  `<paper>_docs_*/writing/submission/figures/Prompts_Images/`, one `.md` per image, written so that
  someone else can generate the image from it without asking a follow-up question.
- **What the author produces:** the image itself, in their own image tool, saved next to the prompt.
- **What the assistant then does:** install it, verify it is byte-identical inside the shipped
  document, and report every defect it can see in the rendered artwork.

**This does not apply to plots computed from data.** Matplotlib figures rendered by a script from a
frozen aggregate are *computation*, not image creation, and remain the assistant's job. The line is
between **drawing** something and **plotting** something.

🔴 **A prompt for a figure that carries measured numbers must carry those numbers.** Figures 7 to 11
of the 3J paper are the paper's results. A prompt that describes such a figure in words invites an
image generator to invent the values, and it will: the 2026-08-09 round shipped a generated Figure S1
labelling a share as `4.0.1` with a garbled footnote, while the gate that checks that figure's
arithmetic still passed, because it reads the plotting script and not the PNG. So for any data
figure, the prompt must state the **actual series, in a table, taken from the frozen deliverable**,
and must say that no value may be altered, rounded or added.

**Verification is not optional and is not read-only.** After installing any supplied image, verify it
against the *installed* document, and remember that a gate which re-runs a figure script **writes to
the real output path** and will silently revert the install (`f5`'s C2 arm did exactly that). Snapshot
md5s before and after any gate whose write behaviour is unaudited.

## Speed HPC Cluster

- Host: `o_iseri@speed.encs.concordia.ca`; login node `speed-submit2` is for job submissions only — do not run any computation, builds, or interactive workloads on it (admin warning: "this node is for job submissions only: no compute").
- **🔴 HARD RULE #1 (account-suspension risk — flagged THREE times; if banned, ALL job progress is lost): NEVER run a blocking/interactive `srun` from the login node. ALWAYS use `sbatch`.** A blocking `srun ... | tee ...` sends the python to a compute node (fine) BUT leaves the **srun client + the `tcsh -c` wrapper + `tee` alive on the login node (`speed-submit2`) for the ENTIRE queue wait** — hours when the pool is saturated (`AssocGrpCpuLimit`). The admin's monitor flags those lingering login-node processes as "computational workload on speed-submit" (incidents: 2026-06-10, and again 2026-06-18 via the `3rdJ_04P` probe). To run anything and get its output: submit with `sbatch` (a `.sh` wrapper, or `sbatch -p ps --mem=16G -t 00:30:00 --wrap "cd … && /path/python script.py args > out.txt"`) — it returns a job id instantly and leaves NOTHING on the login node — then read `out.txt` later with a single-file `tail`/`cat`. Do **not** wait/block on a job; SLURM finishing does not need watching.
- **🔴 HARD RULE #2 (admin warning 2026-06-10, repeat offence = account suspension): NO bare `python`/`python3` on the login node — ever.** This includes "quick" verification one-liners (`python3 -c`, `python - <<EOF`, glob/line-count scans over result dirs). Every check that runs Python or touches many files MUST go through the scheduler via **`sbatch`** (NOT blocking `srun` — see Rule #1). Allowed directly on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, and single-file peeks (`tail`/`head`/`grep`/`wc -l`/`cat` on ONE log or csv). Anything iterating over directories or importing pandas/numpy/torch/eppy → `sbatch`, no exceptions.
- **🔴 HARD RULE #3 (walltime — the user does NOT want to see TIMEOUT / time-limit errors, EVER): EVERY job submission MUST request a minimum 1-week walltime — `-t 7-00:00:00` (= `168:00:00`). NEVER use 1h / 1day / 48h caps again.** This applies to ALL jobs regardless of expected runtime — even minute-long diagnostic probes — so nothing is ever killed by walltime. Pad generously; a job that finishes early releases its allocation, so an over-long cap costs nothing. If a partition's `MaxTime` is below 7 days, request that partition's maximum instead (check `scontrol show partition <p>`); never silently fall back to a short cap. (Raised from the prior 48h floor on 2026-06-24 after a 1h diagnostic cap killed control job 987005 with empty output.)
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

