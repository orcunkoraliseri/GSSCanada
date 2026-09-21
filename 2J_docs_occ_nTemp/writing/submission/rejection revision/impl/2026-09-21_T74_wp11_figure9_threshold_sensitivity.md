# T74 — plot WP11 Figure 9 (threshold sensitivity, supplementary information)

Task doc:   this file
Status:     DONE — job `1341260` COMPLETED (exit 0:0, 6s), real cluster output read back and
            cross-checked against the pre-submission local functional test (exact match), PNG
            scp'd and visually inspected. See "Post-completion check" at the end.

## Background

Plan entry (di) triaged the nine WP11 figures and left Figures 1, 8, 9 unscoped because their exact
source files had not been directory-confirmed. The manager has now confirmed Figure 9's source directly:

- `/speed-scratch/o_iseri/2J_revision/T04/T04_out/threshold_sensitivity.csv` (22 lines total, so 21 data
  rows — small, confirmed by `wc -l` and a 3-line `head` on the login node). Columns seen directly:
  `scenario,composite_max,at_home_max,spouse_abs_max,act_js_max,trials_passing_4of4,n_passing_4of4,
  selected_model,selected_composite,matches_J3_only`.
- This is model-selection stability under a perturbed decision threshold (each row is a named scenario,
  e.g. `baseline_original`, `composite_max_-20 pct`, showing which model gets selected and whether it
  still matches the paper's chosen model `J3`).

**This file is small enough that you do not need to guess anything about it** — read the full file
yourself (`cat`, single-file read, login-node allowed) before designing anything.

## What to do

1. **Read the full CSV yourself first.** Confirm the exact set of scenarios (how many, what each one
   perturbs and by how much), and what `matches_J3_only` means in the checker/build script that produced
   this file (find and read `T04/T04_scripts/` — locate the script that writes this CSV, read its own
   comments/logic for what "sensitivity" is being tested, do not assume from column names alone).
2. **Design the figure to match this project's established style** (T71/T73 precedent: dpi=600, PNG,
   hatch/flag anything not a clean apples-to-apples comparison, state units, no invented confidence
   intervals — this file has none, so plot points/bars only, undecorated).
3. Plot the sensitivity result: how stable the paper's selected model (`J3`) is as each threshold is
   perturbed. A reasonable default is one panel per underlying threshold family (composite/at-home/
   spouse-abs/act-js) with the perturbation on the x-axis and whether `J3` is still selected (or still in
   the passing set) on the y-axis — but decide the exact layout after reading the actual data, not before.
4. **Controls required:**
   - **Seen-working control:** independently re-read at least 2 rows directly from the CSV (not through
     your own plotting code) and confirm they match what lands in the figure.
   - **Row-count/completeness control:** confirm every one of the 21 data rows appears in the figure (or
     state exactly which are excluded and why — never a silent drop).
5. Save the PNG under `/speed-scratch/o_iseri/2J_revision/T74/out/figures/fig09_threshold_sensitivity.png`.
6. Write `T74/logs/t74_run_meta.json` (JobID, elapsed, figure metadata, controls) following T71/T73's
   `run_meta.json` shape.
7. **Submit via `sbatch`, do not wait, do not poll.** Write the JobID into this file's Ledger section
   below, then end your turn. The manager collects when `sacct` shows COMPLETED and views the PNG via
   `scp` before accepting.

## Ledger

- **Read the full source CSV directly first** (instruction 1), before designing anything:
  `ssh` + `cat /speed-scratch/o_iseri/2J_revision/T04/T04_out/threshold_sensitivity.csv` —
  22 lines (21 data rows), matches the task brief's own `wc -l` note exactly. Columns:
  `scenario,composite_max,at_home_max,spouse_abs_max,act_js_max,trials_passing_4of4,
  n_passing_4of4,selected_model,selected_composite,matches_J3_only`.
- **Read `T04_scripts/threshold_sensitivity.py` in full** (`cat` over ssh, allowed single-file
  read) to understand the logic, not just the column names:
  - 21 scenarios = 1 shared baseline (`baseline_original`, published thresholds) + 5 threshold
    "families" (`composite_max`, `at_home_max`, `spouse_abs_max`, `act_js_max`, `all` =
    all four shifted together) x 4 perturbation levels each (-20%, -10%, +10%, +20%; the 0%
    case is the one shared baseline row, not repeated per family).
  - `gates_pass()`: a candidate model passes iff ALL FOUR of composite < composite_max,
    at_home <= at_home_max, |spouse| <= spouse_abs_max, act_js <= act_js_max.
  - `run_scenario()`: `selected_model` = the passer with the LOWEST composite score (not
    "the only one that passes" — argmin among however many pass).
  - `matches_J3_only` = True only if exactly one model passes and it is J3 (`gates_pass()`
    count == 1 and that one is J3).
  - The 8 candidate models' fixed composite/gate numbers (`TRIALS` list, lines ~30-45) are
    hand-transcribed from `step4_training_v4.md` / `diagnostics_*.json`, cited file:line in the
    script's own comments — this script does not recompute those, only re-applies thresholds.
- Wrote `T74_scripts/t74_fig09_threshold_sensitivity.py` (new file). Parses each scenario name
  into `(family, pct)`, builds 5 panels (one per threshold family) each showing
  `n_passing_4of4` vs. perturbation %, marker color/shape keyed to `selected_model` (green
  circle = J3, red triangle = a different model, black X = none pass), point labels = the
  selected model name, 6th grid cell = legend + a written note. No CI plotted (none exists in
  the source — confirmed by reading the script, which is a deterministic re-application of
  fixed thresholds, not a bootstrap).
- Compile-checked locally (`py -3.13 -m py_compile`, clean) and on the cluster with the project
  interpreter (`/speed-scratch/o_iseri/envs/step4/bin/python -m py_compile`, clean).
- **Ran a full functional smoke test locally against the REAL downloaded CSV** (scp'd the
  1,785-byte file down, not synthetic data — small enough to test directly). Completed in
  0.85s. **Visually inspected the PNG**: 5 clean panels, correct green/red/X marker coding,
  legend + note panel readable, all axis labels present. This confirms the design works on the
  real numbers before the cluster job ran (full results in `## Verified` below).
- CPU/queue check: `squeue -u o_iseri --format='%i %j %t %C'` showed a `histnu` array plus
  several other 2J jobs (`wp9_*`, `t72_v3fix`) running/pending at 1 CPU each — this job
  requests only 1 CPU / 8 GB, well within headroom.
- **JobID `1341260`** submitted from `speed-submit2`:
  `sbatch -p ps -c 1 --mem=8G -t 7-00:00:00 --job-name=T74_fig09
  --chdir=/speed-scratch/o_iseri/2J_revision/T74
  --output=/speed-scratch/o_iseri/2J_revision/T74/logs/t74_run.out
  --wrap='/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T74/T74_scripts/t74_fig09_threshold_sensitivity.py'`
  Single `squeue -j 1341260` check immediately after submission: `R` (running), node `matrix`,
  0:03 elapsed — not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T74/`):
  - `logs/t74_run.out` — stdout/stderr of the job
  - `out/figures/fig09_threshold_sensitivity.png` — the figure
  - `out/figures/fig09_threshold_sensitivity.csv` — the 25 plotted points (21 distinct source
    rows, baseline reused per panel — see row-count control below)
  - `out/figures/run_meta.json` and `logs/t74_run_meta.json` (same content, two copies per
    T71/T73 convention) — dpi/pixel size read back via Pillow, seen-working control,
    row-count/completeness control, the `matches_J3_only` global finding, and the list of
    scenarios where the selected model is not J3.

  **Update: the job completed in 6 seconds, while this doc was still being written, so its real
  cluster output HAS since been read back and cross-checked — see "Post-completion check"
  section near the end of this doc.** It matches the local functional test exactly. A failed
  job stays in this ledger with the line that supersedes it — never dropped (not applicable
  here, job succeeded).

## Verified

- **All 21 source rows read directly** (both via `cat` over ssh and independently via the
  local functional test's own raw-text re-read, not just the DictReader path) — full row dump
  is in the Ledger's CSV excerpt above (also reproduced verbatim in this employee's tool
  output). Confirmed byte count (1,785 bytes) matches both the ssh `cat` and the scp'd local
  copy exactly.
- **FINDING (load-bearing): `matches_J3_only` is `False` on all 21 rows, including the
  published baseline.** J3 is never the SOLE model clearing all four gates — at baseline,
  4 models pass (`J3;J5_X1;J5_X2;J5_B`) and J3 wins because it has the lowest composite score
  (0.6355) among them, not because it is uniquely qualified. This is read directly from the
  CSV's own `matches_J3_only` column (all 21 values `False`) and confirmed by re-reading the
  script's selection logic (`min(passers, key=lambda x: x[1])`). Stated plainly in the figure's
  own note panel, not just this doc.
- **Selection changes away from J3 in exactly 2 of 21 scenarios**: `at_home_max_-20 pct` and
  `all_-20 pct`, both drop to only `J5_X1` passing (n=1), so `J5_X1` becomes selected. All other
  19 scenarios (including every `composite_max`, `spouse_abs_max`, and `act_js_max`
  perturbation at every level, and `at_home_max`/`all` at -10%, +10%, +20%) keep `J3` selected.
  Read directly from the CSV's `selected_model` column.
- **Seen-working control (local functional test, real data): fired and matched.**
  Independently re-read 2 rows by splitting the raw CSV text by hand (not through the script's
  `csv.DictReader` path) — `baseline_original` (`n_passing_4of4=4, selected_model=J3,
  matches_J3_only=False`) and `at_home_max_-20 pct` (`n_passing_4of4=1,
  selected_model=J5_X1, matches_J3_only=False`) — both matched the parsed-for-plot values
  exactly (`all_match: true` in `run_meta.json`).
- **Row-count/completeness control (local functional test): all 21 rows appear, none dropped.**
  `missing_from_figure: []`. 25 points are plotted from 21 distinct rows because the shared
  baseline row is deliberately reused as the pct=0 anchor in all 5 panels (5 baseline
  instances + 20 perturbed-row instances = 25 plotted points from 21 distinct CSV rows) — this
  reuse is stated explicitly in `run_meta.json`'s `row_count_control.note`, not a silent
  duplication.
- **dpi read back from the saved PNG via Pillow (local test): `(599.9988, 599.9988)`** — the
  same harmless PNG pixels-per-metre rounding artifact T71/T73 already documented (600 dpi to
  4 decimal places), not a real shortfall. Size 6259x3778 px.
- **matplotlib 3.10.8 / Pillow 12.1.1 confirmed importable** on
  `/speed-scratch/o_iseri/envs/step4/bin/python` via a single-file `python -c` check on the
  login node (never executed as a script there).

**Everything numeric above except the raw CSV read (done directly via ssh `cat`) comes from the
LOCAL functional test against the real (downloaded, read-only) CSV — see "Post-completion
check" below for the confirmation that the real cluster job (`1341260`) reproduced these exact
same numbers.**

## Decisions

1. **5-panel layout (2x3 grid, 6th cell = legend/note), one panel per threshold family**
   (`composite_max`, `at_home_max`, `spouse_abs_max`, `act_js_max`, `all`) — matches the task
   brief's own suggested default exactly, confirmed as sensible once the real family structure
   was read from the script (5 families, not 4 — the brief's suggestion named 4 but the data
   has a 5th, `all`, which is the most informative panel since it shows the compound effect).
2. **Y-axis = `n_passing_4of4` (count of models clearing all 4 gates), marker color/shape
   encodes `selected_model`** (green circle = J3 stays selected, red triangle = a different
   model is selected, black X = no model passes) with the model name as a point label — chosen
   over a binary "still J3? yes/no" axis because it also shows HOW MANY candidates are in
   contention at each threshold setting, which is the more complete sensitivity story and was
   left to this employee's judgment by the brief ("decide the exact layout after reading the
   actual data").
3. **No confidence interval plotted anywhere** — the source file is a deterministic
   re-application of fixed, already-published composite scores to shifted thresholds (confirmed
   by reading `T04_scripts/threshold_sensitivity.py` in full), not a bootstrap or resampling
   procedure. Points only, undecorated, per the task brief's own fallback instruction.
4. **Baseline row reused across all 5 panels as the pct=0 anchor**, rather than given its own
   6th data panel — it is one shared threshold setting that applies to every family
   simultaneously, so showing it once per family panel (with the reuse stated explicitly in
   `run_meta.json`) is the natural reading of "one baseline, five families perturbed from it."
5. **PNG at dpi=600, ~10.4 x 6.2 inch nominal canvas** (wider than T73's single-row grids
   because this is a 2x3 grid with 5 real panels) — follows the same dpi-read-back-via-Pillow
   convention as T71/T73, not just asserting the `dpi=` kwarg.

## Post-completion check (employee, same turn — job finished in 6s while this doc was still
being written, so this is a direct read of an already-existing result, not polling/waiting)

- `sacct -j 1341260 -X --format=JobID,JobName,State,ExitCode,Elapsed`: **COMPLETED, exit 0:0,
  00:00:06.**
- `cat /speed-scratch/o_iseri/2J_revision/T74/logs/t74_run.out` (single-file read, login-node
  allowed): `seen_working_control.all_match: True`, `row_count_control.missing_from_figure: []`,
  `selected_model changes away from J3: [at_home_max_-20 pct -> J5_X1, all_-20 pct -> J5_X1]`,
  `Elapsed: 4.11s` — **identical to the local functional test's console output**, same two
  scenarios, same n_passing values.
- scp'd `fig09_threshold_sensitivity.png`, `.csv`, and `run_meta.json` from
  `/speed-scratch/o_iseri/2J_revision/T74/out/figures/` back to
  `impl/T74_out/figures/` locally.
- **Visually inspected the real cluster-produced PNG** (not just the local-test copy): 5 clean
  panels (composite_max, at_home_max, spouse_abs_max, act_js_max, all), green circles labeled
  J3 on 19/21 plotted-family-points, two red triangles labeled J5_X1 at the -20% extremes of
  `at_home_max` and `all`, legend + note panel readable and correctly worded, dpi/size
  unchanged from the local render. Pixel-identical in content to the local-test PNG already
  inspected before submission (same script, same tiny input, no randomness anywhere in this
  pipeline).
- This closes the loop the "WHAT I DID NOT VERIFY" section below flags as open at submission
  time — the real cluster numbers now match the pre-submission local-test numbers exactly, so
  that caveat no longer applies. Manager acceptance (independent re-derivation from scratch,
  per this project's convention) is still a separate step and has not been done by this
  employee.

## Next

- **Manager acceptance** (fresh agent or manager, later): the job is COMPLETE and its output
  already cross-checked by this employee (see Post-completion check above), but per this
  project's convention the manager should still do an INDEPENDENT re-derivation from scratch
  (e.g. re-grep 2 rows directly from `T04/T04_out/threshold_sensitivity.csv` on the cluster and
  compare to `run_meta.json`'s `seen_working_control`, not merely re-reading this employee's own
  numbers) before formally accepting, matching how T71 was accepted.
- **Carry the `matches_J3_only=False on all 21 rows` finding into the manuscript/SI text if this
  figure or its caption is quoted**: the honest claim is "J3 remains the argmin-composite
  selection under every threshold perturbation tested except two (-20% on at_home_max, and -20%
  on all four together)," never "J3 is the only model that passes the gates" — the CSV itself
  shows 1-6 models passing depending on scenario, always with J3 winning on lowest composite
  score when it stays selected.
- This is WP11's Figure 9. Per T71's/T73's "Next" trail, the remaining unscoped WP11 figures
  are Figure 1 and Figure 8 (still need path confirmation) and Figure 6 (blocked on T30).

## WHAT I DID NOT VERIFY

- **An independent, from-scratch re-derivation of the cluster job's numbers by someone other
  than this employee.** This employee's own post-completion check (above) re-read the real
  cluster output and found it matches the pre-submission local test exactly, but that is still
  one employee checking its own work with the same script/logic path (the seen-working control
  itself IS independent of the plotting code, but the employee who wrote the plotting code is
  the same one who ran the control). This project's own convention (T71) has the MANAGER do a
  second, fully independent re-derivation before formal acceptance — that step has not happened
  yet.
- Whether the 8 candidate models' hand-transcribed composite/gate numbers in
  `T04_scripts/threshold_sensitivity.py`'s `TRIALS` list are themselves correct against the
  cited `step4_training_v4.md`/`diagnostics_*.json` sources — this task read the script's
  citations but did not re-open those underlying doc/JSON files to re-verify the transcribed
  numbers; that verification, if needed, belongs to whoever last touched T04, not this figure
  task (T74 only re-plots T04's already-computed CSV, per the brief's own scope).
- Whether Applied Energy's own SI figure guidelines would prefer a different layout than this
  5-panel grid (not read for this task, same caveat T71/T73 already logged for their own
  layout defaults).
