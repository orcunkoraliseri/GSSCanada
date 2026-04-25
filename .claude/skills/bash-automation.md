---
name: bash-automation
description: Shell discipline for eSim — single-line commands, explicit local-vs-cluster labels, sbatch handoff.
scope: builder
---

# Bash Automation (eSim)

This project runs across three shells: macOS bash (primary), Windows PowerShell (secondary), and Speed cluster bash (HPC). Commands must be portable enough to be copy-pasted between them, or clearly labeled when they are not.

## Core rules (project-wide)

1. **One command per line.** No multi-line scripts in chat — PowerShell wraps long paths and breaks them.
2. **Always label the target shell** when giving a command to the user:
   - `# locally` — runs on the user's macOS or Windows machine
   - `# on the cluster` — runs on Speed (`speed-submit2`, login node, **submission only**)
3. **Prefer `cd` first.** `cd <project_dir>; command short.py` is more robust than passing a long absolute path on Windows.
4. **`scp` per file, per line.** Never brace-expand. Never combine sources.
5. **Bundle uploads.** When syncing edits to the cluster, do one recursive `scp` at the end of an edit cycle — not file-by-file mid-cycle.

## Cluster submission protocol

- The login node `speed-submit2` is for `sbatch` submission only. Do **not** run computation there.
- The builder agent does **not** submit jobs. It produces:
  - the sbatch script (committed under the relevant docs folder or `submit_*.sh`),
  - the literal sbatch command on its own line,
  - the expected output paths.
- The user runs the sbatch command. The builder must never claim a job is submitted.

Example handoff (correct):
```
# on the cluster
sbatch submit_array_tuned.sh
```

Example handoff (wrong — never write this):
```
[builder]: Job submitted as 12345.
```

## Long-running locals

- Long simulations or batch processes run locally should be launched in the foreground from a dedicated terminal, not backgrounded by the agent. Document the command in the task doc; let the user start it.
- For status checks, prefer existing helpers (`check_progress.sh`, `check_hpc_progress.py`) over ad-hoc one-liners.

## Output discipline

- Capture stdout/stderr to a file with a date-stamped name. Do not rely on terminal scrollback as a record.
- Do not pipe through `cat` for the agent's own use — read files directly with the Read tool.

## What the builder must give the user at end of message

End every builder turn that needs human action with the literal command(s) to run, on their own line, labeled `# locally` or `# on the cluster`. Never write "when X finishes, do Y" without giving Y as a runnable command.
