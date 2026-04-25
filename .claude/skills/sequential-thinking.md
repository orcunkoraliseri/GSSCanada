---
name: sequential-thinking
description: Reason step-by-step before acting. Decompose research/engineering problems explicitly, surface assumptions, and avoid jumping to code.
scope: planner, reviewer, reporter
---

# Sequential Thinking

Before producing any task list, plan, review verdict, or interpretation, walk through the problem in explicit ordered steps. Do not skip to the answer.

## Required reasoning structure

For every non-trivial input:

1. **Restate the goal in one sentence.** What does success look like, concretely? If you cannot do this, stop and ask.
2. **List inputs and constraints.** What files, datasets, or prior decisions does this depend on? What is fixed (Census/GSS schema, EnergyPlus 8760 hourly contract, `occ_config.py` paths)? What is variable?
3. **Enumerate unknowns.** What do you not yet know? Mark each unknown as either: (a) resolvable by reading code/data, (b) needs user clarification, (c) deferrable.
4. **Identify risks specific to this project.** Common risks in eSim:
   - Schedule length drift (≠ 8760)
   - Index misalignment in pandas joins between Census PUMF and GSS time-use
   - Hardcoded paths bypassing `occ_config.py` / `eSim_bem_utils/config.py`
   - Silent demographic-mapping changes affecting publishable results
   - Missed `idf.save()` after eppy mutation
5. **Sketch 2–3 candidate approaches.** Briefly. Pick one with a stated reason.
6. **Only then produce the output** (task list, verdict, report chapter).

## Anti-patterns to avoid

- "Looks fine" verdicts with no per-criterion reasoning.
- Plans that bundle multiple concerns into one task ("refactor and validate and re-run").
- Reporting that restates the aim instead of interpreting the result.
- Hidden assumptions (e.g., assuming GSS year alignment without naming the years).

## Output discipline

When the reasoning is internal, keep the user-facing output crisp. The thinking exists to make the answer correct, not to fill the response.
