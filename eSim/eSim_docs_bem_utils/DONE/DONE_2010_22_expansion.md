# Implementation Plan: Adding 2010 and 2022 Variations to Comparative Simulations

## Context

The comparative simulation menu (Options 3, 4, 6, 7) in `run_bem.py` currently
runs four fixed scenarios: **2025**, **2015**, **2005**, and **Default**. The
underlying schedule databases have been expanded with two new census/GSS years —
**2010** and **2022** — and the matching CSVs already exist alongside the others
in `BEM_Setup/`:

```
BEM_Setup/BEM_Schedules_2005.csv
BEM_Setup/BEM_Schedules_2010.csv   <-- new
BEM_Setup/BEM_Schedules_2015.csv
BEM_Setup/BEM_Schedules_2022.csv   <-- new
BEM_Setup/BEM_Schedules_2025.csv
```

The goal of this plan is to wire those two new years into Options 3, 4, 6, 7 so
that every comparative run produces **six** scenarios in chronological order:
`2005 → 2010 → 2015 → 2022 → 2025 → Default`.

> **Filename note:** the user requested a file named `2010/22_expansion.md`. The
> `/` character is invalid in Windows filenames, so this document is saved as
> `2010_22_expansion.md` in the same target directory.

---

## File Inventory (current 2025/2015/2005/Default touchpoints)

| File                                    | Lines / Areas to update                                       | Reason                                              |
|----------------------------------------|---------------------------------------------------------------|-----------------------------------------------------|
| `eSim_bem_utils/main.py`               | 651–696 (Option 3), 1456–1535 (Option 4), 1066–1174 (Option 6), 1859–1935 (Option 7), 2192–2196 (menu strings) | Add 2010 + 2022 to schedule dicts and scenario lists |
| `eSim_bem_utils/plotting.py`           | 488 (`plot_comparative_eui` palette), 727–730 (`plot_comparative_timeseries_subplots`), 848–853 (`plot_kfold_comparative_eui`), 957–962 (`plot_kfold_timeseries`) | Bar charts and time-series plots only have 4 colors today |
| `eSim_bem_utils/reporting.py`          | 523, 536 (hard-coded `['2025', '2015', '2005']` loops)        | Heating / Cooling summary ignores any year not in this list |
| `eSim_docs_bem_utils/comparative_simulation_plan.md` | Title and scenario bullets                          | Doc currently describes only 3 schedule years        |

No changes are needed in `integration.py`, `simulation.py`, `idf_optimizer.py`,
or `neighbourhood.py` — they are scenario-agnostic and operate on whichever
schedule dictionary is handed in.

---

## Design Decisions

1. **Single source of truth.** Define the comparative year list once at the top
   of `main.py` (next to the existing `BEM_SETUP_DIR` constants) so Options 3,
   4, 6, and 7 all read from the same tuple. This avoids the historical drift
   where each function maintains its own `schedule_files` dict.

   ```python
   # main.py — near the BEM_SETUP_DIR block
   COMPARATIVE_YEARS = ('2005', '2010', '2015', '2022', '2025')
   COMPARATIVE_SCENARIOS = COMPARATIVE_YEARS + ('Default',)
   ```

2. **Chronological ordering.** Plots read better when the timeline reads
   left-to-right, so the bar/legend order is `2005 → 2010 → 2015 → 2022 → 2025
   → Default`. Keep the tuple ordered explicitly — do not sort dict keys.

3. **Color palette.** With six scenarios, the existing 4-color blue→red gradient
   is too short. Extend it to a 6-step gradient that still cleanly visually
   separates "older" from "newer" and keeps **Default** as the warm anchor:

   ```python
   SCENARIO_COLORS = {
       '2005':    '#A6F956',  # light green
       '2010':    '#00B050',  # dark green
       '2015':    '#0758FF',  # blue
       '2022':    '#041991',  # navy
       '2025':    '#7A00B0',  # purple
       'Default': '#8A1100',  # red
   }
   ```

   Centralize this dict in `plotting.py` (top of file, near `END_USE_LABELS`)
   and import it from the four plotting helpers so the palette is defined once.
   The current `plot_comparative_eui` uses a list and indexes by position; that
   call site needs to switch to a `dict.get()` lookup to stay aligned with the
   other three helpers.

4. **Bar width math.** All four plotting helpers use a fixed `width = 0.2`
   which works for 4 bars per category but will overflow with 6. Compute width
   from the number of scenarios so the group still fits inside one x-tick:

   ```python
   bar_width = 0.8 / len(scenarios)   # 0.8 = total group width
   ```

   Apply this to `plot_comparative_eui`, `plot_kfold_comparative_eui`. The two
   time-series helpers use line plots (not bars), so only the color dict needs
   updating there.

5. **Reporting summary loop.** `reporting.py` lines 523/536 hard-code
   `['2025', '2015', '2005']`. Replace with `[s for s in self.scenarios if s !=
   'Default']` so the heating/cooling summary auto-includes 2010 and 2022 as
   they appear.

6. **Total simulation count messages.** Options 4 and 7 print
   `"1 Default + iter_count × 3"`. Update the literal `3` to
   `len(COMPARATIVE_YEARS)` (= 5) so the message stays accurate.

---

## Tasks

Each task follows the project's CLAUDE.md task-list format.

### Task 1 — Introduce a single source of truth for the scenario list

- **Aim:** Eliminate four duplicated `schedule_files` dicts and have one place
  to add/remove a comparative year in the future.
- **What to do:** Add two module-level constants in `main.py`
  (`COMPARATIVE_YEARS`, `COMPARATIVE_SCENARIOS`) and a small helper that builds
  the `{year: csv_path}` dict on demand.
- **How to do it:**
  1. Open `eSim_bem_utils/main.py` at lines 21–28 (the BEM_SETUP_DIR block).
  2. Append:
     ```python
     # Comparative simulation scenario configuration
     # Order matters for plot legends (left-to-right chronological).
     COMPARATIVE_YEARS = ('2005', '2010', '2015', '2022', '2025')
     COMPARATIVE_SCENARIOS = COMPARATIVE_YEARS + ('Default',)

     def _build_schedule_file_map() -> dict:
         """Return {year: BEM_Schedules_<year>.csv path} for all comparative years."""
         return {
             year: os.path.join(BEM_SETUP_DIR, f"BEM_Schedules_{year}.csv")
             for year in COMPARATIVE_YEARS
         }
     ```
  3. No removals yet — Tasks 2–5 will switch each option over to use this map.
- **Why:** Today, the same dict is hand-typed in four functions. The next time
  a year is added we want to touch one place, not four.
- **Impact on:** `main.py` only.
- **Steps / sub-steps:** Edit one block in `main.py`.
- **Expected result:** Module imports cleanly; constants are visible to every
  option function.
- **How to test:** Run `python -c "from eSim_bem_utils.main import COMPARATIVE_YEARS; print(COMPARATIVE_YEARS)"`
  from the project root and confirm it prints the 5 years in order.

---

### Task 2 — Update Option 3 (single-building comparative)

- **Aim:** Make `option_comparative_simulation()` run six scenarios.
- **What to do:** Replace the inline `schedule_files` dict, the `scenarios`
  list, and the human-readable description block with references to the new
  constants.
- **How to do it:**
  1. In `main.py`, edit the description prints at lines 583–587 to:
     ```python
     print("This will run 6 simulations for a randomly selected household:")
     for year in COMPARATIVE_YEARS:
         print(f"  - {year} Schedules")
     print("  - Default (No schedule injection)")
     ```
  2. Replace lines 651–655 with:
     ```python
     schedule_files = _build_schedule_file_map()
     ```
  3. Replace line 696 (`scenarios = ['2025', '2015', '2005', 'Default']`) with:
     ```python
     scenarios = list(COMPARATIVE_SCENARIOS)
     ```
  4. Leave the rest of the function untouched — the `for scenario in scenarios`
     loop and the `if scenario == 'Default' / elif scenario in all_schedules`
     branches already work for any number of years.
- **Why:** This is the simplest of the four options and validates the pattern
  before applying it elsewhere.
- **Impact on:** Option 3 only. Output now produces six scenario subdirectories
  under `SimResults/Comparative_HHxp_*/` and feeds six entries into
  `plot_comparative_eui` / `plot_comparative_timeseries_subplots`.
- **Steps:**
  1. Edit description block (lines 583–587).
  2. Replace `schedule_files` dict (lines 651–655).
  3. Replace `scenarios` literal (line 696).
- **Expected result:** Selecting Option 3 prepares six IDFs, runs six EnergyPlus
  jobs in parallel, and emits the comparative bar chart and time-series plot.
- **How to test:** Run `python run_bem.py`, choose `3`, pick a fast Toronto IDF
  + EPW + dwelling type, confirm in console that all 6 scenarios run and that
  `SimResults_Plotting/Comparative_Summary_HH_*.png` shows 6 bars per end-use
  category in the legend.

---

### Task 3 — Update Option 4 (Monte Carlo single-building)

- **Aim:** Same expansion for `option_kfold_comparative_simulation()`.
- **What to do:** Replace `schedule_files`, `year_scenarios`, `scenarios` and
  fix the `total_sims` math so the user-facing count stays correct.
- **How to do it:**
  1. Replace lines 1465–1469 with:
     ```python
     schedule_files = _build_schedule_file_map()
     ```
  2. Replace lines 1534–1535 with:
     ```python
     year_scenarios = list(COMPARATIVE_YEARS)
     scenarios = list(COMPARATIVE_SCENARIOS)
     ```
  3. Update the print message at lines 1456–1458 to use
     `len(COMPARATIVE_YEARS)` instead of the hard-coded `3`:
     ```python
     total_sims = 1 + iter_count * len(COMPARATIVE_YEARS)
     print(f"\nThis will run 1 Default + {iter_count} iterations × "
           f"{len(COMPARATIVE_YEARS)} year scenarios = {total_sims} total simulations.")
     ```
  4. The Monte Carlo loop body (`for scenario in year_scenarios`) and the
     `all_eui_results = {s: [] for s in scenarios}` initializer already
     generalize cleanly — no further edits needed.
- **Why:** Option 4 is functionally Option 3 in a Monte Carlo wrapper. Same
  scenario expansion, plus the user-facing simulation count message must stay
  accurate.
- **Impact on:** Option 4. Aggregated CSV (`aggregated_eui.csv`) and Monte Carlo
  bar chart (`MonteCarlo_Comparative_EUI_*.png`) now have 6 mean/std columns.
  `reporting.py` is invoked here too — Task 6 covers it.
- **Steps:**
  1. Replace `schedule_files` dict.
  2. Replace `year_scenarios` / `scenarios`.
  3. Update `total_sims` message.
- **Expected result:** With `iter_count=2`, the console prints
  `"1 Default + 2 iterations × 5 year scenarios = 11 total simulations."` and
  produces 11 EnergyPlus runs.
- **How to test:** Run Option 4 with `iter_count=1` (smallest valid) on a fast
  IDF; verify `aggregated_eui.csv` has columns
  `2005_mean,2005_std,2010_mean,2010_std,2015_mean,2015_std,2022_mean,2022_std,2025_mean,2025_std,Default_mean,Default_std`.

---

### Task 4 — Update Option 6 (comparative neighbourhood)

- **Aim:** Same expansion for `option_comparative_neighbourhood_simulation()`.
- **What to do:** Replace `schedule_files`, `scenarios`, and the description.
- **How to do it:**
  1. Edit description prints at lines 1066–1071:
     ```python
     print("This will run parallel simulations for a neighbourhood:")
     for year in COMPARATIVE_YEARS:
         print(f"  - {year} Schedules")
     print("  - Default (No schedule injection)")
     ```
  2. Replace lines 1111–1115 with:
     ```python
     schedule_files = _build_schedule_file_map()
     ```
  3. Replace line 1174 (`scenarios = ['2025', '2015', '2005', 'Default']`) with:
     ```python
     scenarios = list(COMPARATIVE_SCENARIOS)
     ```
  4. The household-matching loop already iterates `for scenario in year_scenarios`
     — but in this function the analogous variable is just inside the loop. The
     existing `if scenario == 'Default' / elif scenario in all_schedules` flow
     handles new years transparently.
- **Why:** Neighbourhood comparative is the multi-building counterpart of
  Option 3. Same data structure, same scenario expansion.
- **Impact on:** Option 6. Six neighbourhood IDFs now generated per run; six
  series on the comparative plots.
- **Steps:**
  1. Edit description block.
  2. Replace `schedule_files` dict.
  3. Replace `scenarios` literal.
- **Expected result:** Six prepared neighbourhood IDFs under
  `SimResults/Neighbourhood_Comparative_*/` and a 6-bar comparative plot.
- **How to test:** Run Option 6 with the smallest neighbourhood IDF available;
  watch console for "Loaded N households" lines for **all five** years.

---

### Task 5 — Update Option 7 (Monte Carlo neighbourhood)

- **Aim:** Same expansion for `option_batch_comparative_neighbourhood_simulation()`.
- **What to do:** Replace `schedule_files`, `year_scenarios`, `scenarios`, and
  fix the simulation-count message.
- **How to do it:**
  1. Update message at lines 1859–1860:
     ```python
     total_sims = iter_count * len(COMPARATIVE_YEARS) + 1
     print(f"\nThis will run 1 Default + ({iter_count} iterations × "
           f"{len(COMPARATIVE_YEARS)} scenarios) = {total_sims} total simulations.")
     ```
  2. Replace lines 1867–1871 with:
     ```python
     schedule_files = _build_schedule_file_map()
     ```
  3. Replace lines 1934–1935 with:
     ```python
     year_scenarios = list(COMPARATIVE_YEARS)
     scenarios = list(COMPARATIVE_SCENARIOS)
     ```
- **Why:** Final option that hard-codes the year list. Same fix pattern as
  Option 4 but at the neighbourhood scale.
- **Impact on:** Option 7. Aggregated CSV gains 2010/2022 columns; plots gain
  two more series.
- **Steps:**
  1. Update count message.
  2. Replace `schedule_files` dict.
  3. Replace `year_scenarios` / `scenarios` literals.
- **Expected result:** With `iter_count=1`, console prints
  `"1 Default + (1 iterations × 5 scenarios) = 6 total simulations."`.
- **How to test:** Run Option 7 with `iter_count=1` on the smallest neighbourhood
  IDF; verify all six scenarios appear in the output directory tree
  (`Default/`, `iter_1/2005/`, `iter_1/2010/`, …, `iter_1/2025/`).

---

### Task 6 — Update `reporting.py` heating / cooling summary loop

- **Aim:** Stop the auto-generated CSV report from silently dropping 2010 and
  2022 from the "Summary of Key Findings" section.
- **What to do:** Replace the two hard-coded `['2025', '2015', '2005']` literals
  with a derived list of all non-Default scenarios.
- **How to do it:**
  1. Open `eSim_bem_utils/reporting.py`.
  2. At line 523, replace:
     ```python
     for scenario in ['2025', '2015', '2005']:
     ```
     with:
     ```python
     for scenario in [s for s in self.scenarios if s != 'Default']:
     ```
  3. Repeat the same replacement at line 536 (cooling section).
- **Why:** `self.scenarios` is already the set of scenarios actually run, so it
  naturally includes whatever years Options 3/4/6/7 hand it. Two literal lists
  are the only obstacle to that working today.
- **Impact on:** `MonteCarlo_*` report CSV summary. Section 1 (Heating) and
  Section 2 (Cooling) will now list all 5 year scenarios versus Default.
- **Steps:** Two one-line edits.
- **Expected result:** After running Option 4, open the generated report CSV
  and confirm both summary sections show entries for 2005, 2010, 2015, 2022,
  and 2025 (not just three).
- **How to test:** Run Option 4 with `iter_count=1`, open the resulting
  `MonteCarlo_Report_*.csv` in the batch dir, verify sections 1 and 2 list five
  year scenarios each.

---

### Task 7 — Extend the plotting palette and bar-width math

- **Aim:** Make the four comparative plots render six scenarios cleanly.
- **What to do:** Add a single `SCENARIO_COLORS` dict at module scope in
  `plotting.py`, switch all four helpers to read from it, and replace the fixed
  `width = 0.2` in the bar plots with `0.8 / len(scenarios)`.
- **How to do it:**
  1. Open `eSim_bem_utils/plotting.py`. Just under `END_USE_LABELS` (or wherever
     module constants live), add:
     ```python
     # Comparative scenario palette — keep keys aligned with main.COMPARATIVE_SCENARIOS
     SCENARIO_COLORS = {
         '2005':    '#A6F956',
         '2010':    '#00B050',
         '2015':    '#0758FF',
         '2022':    '#041991',
         '2025':    '#7A00B0',
         'Default': '#8A1100',
     }
     ```
  2. **`plot_comparative_eui` (line 453):**
     - Delete line 488: `scenario_colors = ['#041991', '#0758FF', '#A6F956', '#8A1100']`
     - Change line 493 from `width = 0.2` to:
       ```python
       width = 0.8 / max(len(scenario_names), 1)
       ```
     - Change the `bars = ax.bar(...)` color argument (around line 504) from
       `color=scenario_colors[i % len(scenario_colors)]` to
       `color=SCENARIO_COLORS.get(scenario_name, '#666666')`.
  3. **`plot_comparative_timeseries_subplots` (line 673):**
     - Replace the local dict at lines 727–730 with `scenario_colors = SCENARIO_COLORS`.
       (Or delete the dict and read `SCENARIO_COLORS.get(...)` directly.)
     - No bar-width changes — this plot is line-based.
  4. **`plot_kfold_comparative_eui` (line 818):**
     - Replace the local dict at lines 848–853 with `scenario_colors = SCENARIO_COLORS`.
     - Change `bar_width = 0.2` (line 857) to:
       ```python
       bar_width = 0.8 / max(n_scenarios, 1)
       ```
  5. **`plot_kfold_timeseries` (line 900):**
     - Replace the local dict at lines 957–962 with `scenario_colors = SCENARIO_COLORS`.
     - No bar-width changes — line-based plot.
- **Why:** The current 4-color palette runs out at 5+ scenarios. The current
  bar widths overflow each x-tick group when more than 4 bars are present. Both
  problems must be fixed for the plots to remain readable.
- **Impact on:** `plot_comparative_eui`, `plot_comparative_timeseries_subplots`,
  `plot_kfold_comparative_eui`, `plot_kfold_timeseries`. All consumers of these
  functions (Options 3, 4, 6, 7) get the new palette automatically.
- **Steps:**
  1. Add `SCENARIO_COLORS` constant.
  2. Update bar plotter `plot_comparative_eui`.
  3. Update line plotter `plot_comparative_timeseries_subplots`.
  4. Update bar plotter `plot_kfold_comparative_eui`.
  5. Update line plotter `plot_kfold_timeseries`.
- **Expected result:** All four comparative plots show six distinct, ordered,
  non-overlapping series.
- **How to test:** After Tasks 2 and 7 are done, run Option 3 once and visually
  inspect `Comparative_Summary_HH_*.png`: six bars per category, legend reads
  2005 → 2010 → 2015 → 2022 → 2025 → Default, no overlap.

---

### Task 8 — Refresh the menu strings and existing doc

- **Aim:** Keep the menu printout and the existing `comparative_simulation_plan.md`
  doc consistent with the new scenario set.
- **What to do:** Edit the four menu lines in `main_menu()` and add a one-line
  note to the existing comparative doc.
- **How to do it:**
  1. In `main.py`, lines 2192–2196, change the four scenario annotations from
     `(2025/2015/2005/Default)` to `(2005/2010/2015/2022/2025/Default)`.
  2. In `eSim_docs_bem_utils/comparative_simulation_plan.md`, update the "Goal"
     bullet list at the top so it lists all five years; add a single sentence
     pointing readers to this document (`2010_22_expansion.md`) for the
     expansion history.
- **Why:** A user reading the menu should immediately see the new years; a
  developer reading the existing comparative plan should not be misled by stale
  scenario lists.
- **Impact on:** User-visible menu and one Markdown doc.
- **Steps:** Two text edits.
- **Expected result:** Running `python run_bem.py` shows the updated scenario
  annotations in the menu.
- **How to test:** Launch the menu, visually verify lines 3, 4, 6, 7.

---

## Verification Checklist (run after all tasks complete)

| # | Check                                                               | How                                                  |
|---|----------------------------------------------------------------------|------------------------------------------------------|
| 1 | All 5 schedule CSVs are loadable and produce non-empty households   | Run Option 3 once; watch console for "Loaded N HHs"  |
| 2 | Option 3 produces 6 scenario subdirs                                | `ls SimResults/Comparative_HH*p_*/` → 6 entries      |
| 3 | Option 4 produces correct simulation count                          | Console prints `1 Default + K × 5 = ...`             |
| 4 | Option 6 runs 6 neighbourhood scenarios                             | `ls SimResults/Neighbourhood_Comparative_*/` → 6     |
| 5 | Option 7 produces correct simulation count                          | Console prints `1 Default + (K × 5) = ...`           |
| 6 | Comparative bar chart has 6 bars per end-use                        | Open `Comparative_Summary_HH_*.png`                  |
| 7 | Time-series plot has 6 lines per subplot                            | Open `Comparative_TimeSeries_HH_*.png`               |
| 8 | Aggregated CSV (Option 4) has 12 mean/std columns                   | Open `aggregated_eui.csv`                            |
| 9 | Reporting summary lists all 5 years                                 | Open `MonteCarlo_Report_*.csv`, check sections 1/2   |
| 10| Menu printout shows updated scenario annotations                    | `python run_bem.py`                                  |

---

## Risks & Things to Watch

1. **Households missing in some years.** Options 3/4 use `find_best_match_household`
   keyed on hhsize. If `BEM_Schedules_2010.csv` or `_2022.csv` happen to be
   sparse for an unusual dwelling type / region combo, the existing fallback
   (random pick) will trigger. This isn't a regression — it's the same behavior
   that already exists for 2005/2015/2025 — but worth noting in case the user
   sees more "Warning: No N-person HH found" lines after the change.

2. **Simulation runtime grows ~50%.** Going from 4 → 6 scenarios per run scales
   linearly. For Option 4/7 with `iter_count=5`, that's `1 + 5×5 = 26` runs
   instead of `1 + 5×3 = 16`. Worth flagging when the user kicks off the first
   end-to-end test.

3. **Plot legibility at 6 series.** The 0.8/N bar-width formula keeps groups
   inside one x-tick, but with many end-use categories the figure may need a
   wider `figsize`. If reviewers complain, bump `figsize=(16, 8)` to
   `figsize=(20, 8)` in `plot_comparative_eui` and `plot_kfold_comparative_eui`.

4. **Reporting.py implicit ordering.** `self.scenarios = list(results.keys())`
   on line 39 inherits whatever order Options 3/4/6/7 pass in. The Task 1
   tuple is already in chronological order, so the report sections will list
   years correctly without needing a sort.

---

## Order of Implementation

Tasks **must** be done in this order — earlier tasks set up the constants and
palette that later tasks consume:

1. **Task 1** — add `COMPARATIVE_YEARS` / `COMPARATIVE_SCENARIOS` constants and
   `_build_schedule_file_map()` helper.
2. **Task 7** — extend plotting palette and bar widths (so the visual output is
   ready before any scenario actually runs through them).
3. **Task 2** — Option 3 (smallest blast radius, easiest to verify end-to-end).
4. **Task 3** — Option 4.
5. **Task 4** — Option 6.
6. **Task 5** — Option 7.
7. **Task 6** — `reporting.py` summary loop fix.
8. **Task 8** — menu strings and doc refresh.

After step 3, Option 3 should already produce six-bar plots correctly. Treat
that as the smoke test before continuing with the remaining options.

---

## Progress Log

### 2026-04-06 — Implementation complete + Option 3 smoke test

**Status:** All eight tasks merged. Code-level verification passed (constants
present, four plotting helpers reading from `SCENARIO_COLORS`, no leftover
hard-coded year literals in `main.py` or `reporting.py`, menu strings updated).

**Smoke test run:** Option 3 — Comparative single-building, household 5203
(1-person), batch `Comparative_HH1p_1775505815`.

- 6 / 6 scenarios completed successfully (2005, 2010, 2015, 2022, 2025, Default)
- Total wall-clock time: **29.6 s** (parallel, 6 workers, ~28 s per scenario)
- Output dirs: `BEM_Setup/SimResults/Comparative_HH1p_1775505815/{2005,2010,2015,2022,2025,Default}/`
- Schedule exports present for all 5 year scenarios under
  `BEM_Setup/SimResults_Schedules/Comparative_HH1p_1775505815/`
- Plots generated:
  - `Comparative_HH_5203_<scenario>.png` × 6 (per-scenario end-use breakdown)
  - `Comparative_Summary_HH_5203_1775505851.png` (6-bar grouped chart)
  - `Comparative_TimeSeries_HH_5203_1775505852.png` (6-line subplots)

**EUI results (extracted from `eplusout.sql` → Site and Source Energy table):**

| Scenario | Total Site EUI (MJ/m²) | Total Site EUI (kWh/m²) | Δ vs Default |
|---------:|----------------------:|------------------------:|-------------:|
| 2005     | 13.64                 | 3.79                    | +0.0 %       |
| 2010     | 13.69                 | 3.80                    | +0.4 %       |
| 2015     | 13.10                 | 3.64                    | **−4.0 %**   |
| 2022     | 13.71                 | 3.81                    | +0.5 %       |
| 2025     | 13.70                 | 3.81                    | +0.4 %       |
| Default  | 13.64                 | 3.79                    | baseline     |

**End-use breakdown (GJ/year, raw from SQL):**

| Scenario | Cool (E) | Lights (E) | Equip (E) | Heat (Gas) | DHW (Gas) | Equip (Gas) |
|---------:|---------:|-----------:|----------:|-----------:|----------:|------------:|
| 2005     | 4.84     | 0.24       | 5.98      | 48.41      | 3.16      | 1.86        |
| 2010     | 4.81     | 0.24       | 5.98      | 48.35      | 3.16      | 1.86        |
| 2015     | 4.81     | 0.24       | 5.98      | 48.51      | 3.16      | 1.86        |
| 2022     | 4.84     | 0.24       | 5.98      | 48.59      | 3.16      | 1.86        |
| 2025     | 4.82     | 0.24       | 5.98      | 48.38      | 3.16      | 1.86        |
| Default  | 4.94     | 0.24       | 5.98      | 47.79      | 3.16      | 1.86        |

> Reported building area = 5,154 m². That number is the EnergyPlus
> "Total Building Area" — much larger than a single dwelling, so the per-m²
> EUI looks small. The selected IDF appears to be a multi-zone building or one
> with a large unconditioned envelope. Consider re-running on a smaller
> single-family IDF for a more recognisable EUI scale before publishing.

**Observations / things to investigate:**

1. **Year scenarios cluster tightly (2005/2010/2022/2025 all within ±0.5 % of
   Default).** This is consistent with the building being heating-dominated and
   most schedule sensitivity living in heating gas demand, which barely shifted.
2. **2015 is the visible outlier (−4 %).** Lower heating gas relative to the
   other years (48.51 GJ — actually similar to neighbours, so the EUI delta
   comes from a small difference somewhere else worth tracing). Worth comparing
   against the per-scenario breakdown plots before drawing conclusions.
3. **Lights, Equipment (Elec), Equipment (Gas), and DHW are byte-identical
   across all 6 scenarios.** That means the schedule injection is currently
   only moving People-related loads (and downstream heating/cooling), not
   Lights/Equipment/DHW. If the longitudinal narrative depends on showing how
   modern lighting/appliance use patterns differ from 2005, this needs digging
   in `integration.inject_schedules` — those end uses should be variable across
   years.
4. **Cooling moves only ~0.13 GJ across scenarios.** Toronto-style climate, so
   cooling is small to begin with; not necessarily a bug, but flag for
   sensitivity discussion in the eSim paper.

**Next steps:**

- Run Option 4 (Monte Carlo single-building) with `iter_count=1` to confirm
  the 11-simulation count message and the aggregated CSV structure.
- Run Option 6 / Option 7 on the smallest neighbourhood IDF available.
- Investigate why Lights/Equipment/DHW end uses are flat across schedule years
  — if intentional, document it; if a bug, file a follow-up.
- Re-run Option 3 on a smaller single-family IDF to get a more conventional
  EUI magnitude (~100–200 kWh/m²) before generating publication plots.
