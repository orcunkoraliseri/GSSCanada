---
name: task-decomposition
description: Break a research/engineering goal into atomic, testable, sequenced tasks suitable for the eSim multi-agent loop.
scope: planner
---

# Task Decomposition

Convert a user goal into a numbered task list where each task is atomic, testable, and routed to the correct `eSim_docs_*` folder.

## Atomicity rules

A task is atomic when:
- It produces **one** observable artifact (a file, a metric, a passing test, a committed change).
- It can be reviewed in isolation by the reviewer agent.
- A single commit can describe it, with one of the allowed types: `[data] [ml] [pipeline] [bem] [fix] [docs]`.

If a candidate task needs the word "and" in its title, split it.

## Sizing heuristics

Target each task to be ~30–90 minutes of builder work. Concretely for eSim:

- One pipeline-stage edit (e.g., `*_alignment.py` change) → one task.
- One IDF schedule injection routine → one task.
- One validation figure or report table → one task.
- A C-VAE training run → one task (artifact: trained model + metrics file).
- A Calcul Québec batch submission → one task (artifact: sbatch command + expected output paths).

Do **not** combine code change + simulation rerun + figure regeneration in one task. They are three.

## Sequencing and dependencies

- Order tasks so each one's inputs exist when it starts.
- Make dependencies explicit in the task body ("Depends on: T03 output `aligned_2022.parquet`").
- If two tasks are truly independent, mark them so the builder can interleave or the reviewer can parallelize review.

## Routing checklist

Before assigning a task to a docs folder, ask:
- Does it touch GSS/Census ingestion, profile matching, C-VAE, or schedule generation? → `eSim_docs_occ_utils/`
- Does it touch IDFs, eppy/geomeppy, EnergyPlus runs, schedule injection? → `eSim_docs_bem_utils/`
- Does it touch HPC submission, batching, Calcul Québec, Speed cluster? → `eSim_docs_cloudSims/`
- Does it touch neighborhood-scale geometry or aggregation across buildings? → `eSim_docs_ubem_utils/`
- Does it produce a figure, table, validation result, or paper section? → `eSim_docs_report/`

A task that genuinely spans two folders is usually two tasks.

## Acceptance criteria

Every task must specify:
- **Expected Result**: a concrete artifact name or measurable metric.
- **Test Method**: the exact command or check that proves the task is done.

If you cannot write the Test Method, the task is not ready — either gather more context or split it.
