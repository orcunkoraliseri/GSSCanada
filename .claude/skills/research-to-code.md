---
name: research-to-code
description: Translate research artifacts (papers, equations, datasets) into eSim code without losing scientific intent.
scope: planner, builder, reporter
---

# Research-to-Code Translation

eSim is a research codebase. Translation from a paper or methodology note into working code is a recurring task. Done badly it silently changes results.

## Before writing code

1. **Locate the source of truth.** Cite the exact paper section, equation number, or methodology note. If the source is internal (`eSim_writing/`, prior chat, a notebook), name the file and section.
2. **Extract the contract.** What is the input shape and units? What is the output shape and units? What is the time resolution? For schedules, is the convention "value at start of interval" or "average over interval"?
3. **Check existing implementations.** Grep `eSim_occ_utils/` and `eSim_bem_utils/` for prior implementations of the same idea. Reuse over re-implement.
4. **Note the validation reference.** What number, distribution, or figure should the result reproduce? If the paper reports a metric (e.g., mean weekday occupancy = 0.62), record that as the test target.

## While writing code

- Keep variable names close to the paper's notation when possible (`p_home`, `lambda_arr`, `Q_int`). Add a short docstring linking name → paper symbol.
- Comment only the **why** that a future reader cannot infer: a non-obvious assumption, a deviation from the paper, a workaround for a data quirk.
- If a paper's equation has implicit assumptions (e.g., closed populations, stationarity), state them at the top of the function.
- For demographic mappings, pull from the existing mapping module — never re-encode categorical schemes inline.

## After writing code

- Reproduce the paper's reference number with a small test fixture. If you cannot, stop and report the gap before integrating.
- Record the deviation (data year, region, population subset) if your number differs from the paper. The reporter agent will surface this.
- If the change could affect publishable results, the task progress log must say so explicitly — even if the magnitude is small.

## Common pitfalls in this codebase

- **Time-zone drift** between GSS diary minutes (local time) and EnergyPlus weather files (TMY local time, no DST). Always state which clock you are on.
- **5-min → 30-min → hourly downsampling** can be sum, mean, or first-of-bin. The choice matters for occupancy vs. internal gains. Use the convention already established in `*_occToBEM.py`; do not invent a new one.
- **Person-units vs. household-units** — many GSS variables are per-respondent; many Census variables are per-household. Joining without resolving the unit is the most common source of silent bugs.
