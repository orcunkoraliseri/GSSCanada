# V3c results -- F (fair, residential-shaped control) vs U (frozen Default_NECB control)

Companion to `writing/implementation/IMP/V3c_fair_control.md` (sections 1-9 there are append-only,
not touched here). This doc is the post-processing + comparison the doc's section 8 asked for.
Local run, 2026-09-24, author ruling that day allows local work instead of a Speed sbatch step
because the cluster queue is full.

## 1. Cluster run status (array 1342434)

`sacct -j 1342434 --format=JobID,State,ExitCode,Elapsed -X` (ran and fired: all 4 completed clean):

| Task | State | ExitCode | Elapsed |
|---|---|---|---|
| 1342434_0 | COMPLETED | 0:0 | 00:13:50 |
| 1342434_1 | COMPLETED | 0:0 | 00:14:21 |
| 1342434_2 | COMPLETED | 0:0 | 00:26:01 |
| 1342434_3 | COMPLETED | 0:0 | 00:32:53 |

Each `runs/V3c/F__Default_NECB__<b>__<c>/manifest.json`: `"status": "ok"`, `build_F` =
`objects_changed: 4, objects_added: 1, repointed: {apartment: 1, hotel: 3}` on all 4 cells --
matches the doc's own self-check exactly.

## 2. Copy to local disk (change from section 6: local aggregation, not sbatch)

Cluster side size check (`du -sh`): 906M total (`SuperTall__CLG` 275M, `SuperTall__MTL` 275M,
`Tall__CLG` 179M, `Tall__MTL` 179M). C: had 594 GB free, RAM at 54.6% before the copy -- both
inside the guard. `scp -r`, one cell at a time, to
`C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/3J_V3c/runs/V3c/`. Local sizes matched (274M/274M/
178M/178M, the ~1M difference is block-size rounding, not a partial copy).

## 3. Local Step-8E aggregation

RAM re-checked at 49.9% right before the run (still under the 70% stop line). One process
(default `--jobs 1`), from repo root:
```
PYTHONPATH=C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/eSim PYTHONIOENCODING=utf-8 py -3 \
  Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py \
  --campaign-dir C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/3J_V3c/runs/V3c \
  --outdir writing/implementation/IMP/data/V3c/agg_V3c_F \
  --eplus-idd C:/EnergyPlusV24-2-0/Energy+.idd --idf-name injected_resized.idf
```
All 4 cells `[ok]`, attribution residual 0.000000% on every cell. `eSim` was at
`GSSCanada-main/eSim` (found by `find`, matched the doc's guess). Output:
`IMP/data/V3c/agg_V3c_F/agg_{peak,diurnal,meta,annual_by_channel,annual}.csv`. `cell_tag` values
came out `Default_NECB__<building>__<city>` -- identical strings to U's `agg_deliverable` cell
tags (both arms are the `Default_NECB` build; only the schedule pointer differs), so F and U rows
were matched on this shared cell_tag rather than needing a rename.

Resolves two of the doc's section-9 open items: `agg_diurnal.csv` carries only `metric in
{"energy_W","people"}` -- no `people_frac`-style normalized column exists, in either F's own
output or U's frozen `agg_deliverable` (checked both). `agg_annual_by_channel.csv` likewise
carries only `eui_CFA_kWh_m2`, no GFA-share column, in both places -- the GFA-share basis needs
the Step-9 scorer, which was not run for arm F (out of scope here; noted, not assumed away).

## 4. Comparison script

New script `writing/implementation/IMP/scripts/v3c_compare.py`. Imports `circ`, `resultant`,
`load`, `wd_profile` from `p3_code_schedule_comparison.py` by path (`importlib`) rather than
reimplementing the peak-hour / coincidence-factor math. Reads U straight from the frozen
`Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_*.csv` (read-only, not re-aggregated),
filtered to the 4 `Default_NECB__*` cell tags; reads F from `IMP/data/V3c/agg_V3c_F`. `--agg-f`
and `--agg-u` are overridable so the same script serves the gate tests in section 5.

Outputs (arm column U/F, `writing/implementation/IMP/data/V3c/`):
- `v3c_presence_by_hour.csv` -- weekday people-count by hour, per channel (office/retail/hotel/
  residential), per cell, both arms.
- `v3c_per_cell_metrics.csv` -- per cell: whole-building peak hour + coincidence factor
  (`_BUILDING` row), and per channel: weekday energy peak hour, weekday occupancy peak hour,
  weekday night/midday mean people, channel EUI (CFA basis).
- `v3c_comparison_summary.csv` -- median over the 4 cells, per channel x arm (the P3-summary
  shape asked for).
- `v3c_comparison_diff.csv` -- F minus U, one row per channel (circular diff in hours for the
  two peak-hour columns, plain diff elsewhere).

## 5. Gates seen failing (ran, and fired/did not fire as expected)

**Gate 1 -- U vs U (did not fire, correctly):** `v3c_compare.py --agg-f <agg_deliverable> --agg-u
<agg_deliverable>` (same directory both arms). Result: `MAX_ABS_DIFF_ACROSS_ALL_NUMERIC_COLUMNS =
0.000000`, every cell of `v3c_comparison_diff_UvU.csv` is exactly 0 or NaN (NaN only where a
metric legitimately does not apply to `_BUILDING`, e.g. EUI). PASS.

**Gate 2 -- deliberately altered copy (ran and fired, correctly):** copied U's own
`agg_{peak,diurnal,meta,annual_by_channel}.csv` to `IMP/data/V3c/agg_U_altered/`, doubled the
`hotel` / weekday / `people` rows in `agg_diurnal.csv` only (384 rows), ran
`v3c_compare.py --agg-f agg_U_altered --agg-u agg_deliverable`. Result:
`MAX_ABS_DIFF_ACROSS_ALL_NUMERIC_COLUMNS = 448.673702`, and the nonzero cells in
`v3c_comparison_diff_CLEANALT.csv` are exactly `hotel` `wd_night_people` (+3.148) and
`wd_midday_people` (+448.674) -- every other channel and column stayed at 0. The checker fires,
and fires only where the data was actually changed. PASS.

(A second, less clean version of this test used the real F data doubled instead of a plain copy
of U -- also fired, `MAX_ABS_DIFF = 955.07` -- kept in `data/V3c/selftest/*_ALTERED.csv` for the
record, but the clean U-vs-altered-U version above is the one to cite: it isolates the injected
change from the real F-vs-U effect being measured.)

## 6. F vs U -- the real comparison

Medians over the 4 cells (Tall/SuperTall x MTL/CLG), full tables in `v3c_comparison_summary.csv`
/ `v3c_comparison_diff.csv` / `v3c_per_cell_metrics.csv`. For context, the frozen `agg_deliverable`
also gives the two survey-driven arms' numbers (Y2022, B_central; read-only, same tables P3
already used) -- pulled here only to answer the one-sentence verdict, not re-derived.

**Whole building** (barely moves -- expected, only 4 PEOPLE objects out of a full campus IDF
changed):
- Peak hour: U 14.62 h, F 14.65 h (diff +0.028 h, about 1.7 minutes).
- Coincidence factor: U 0.9301, F 0.9294 (diff -0.0007).

**Hotel channel, weekday people presence** (this is the one that matters for the verdict):
| Arm/scenario | night mean (people) | midday mean (people) | weekday peak hour |
|---|---|---|---|
| U (Default_NECB, unfair control) | 3.15 | 448.67 | 12.22 (midday) |
| F (Default_NECB, fair control) | 479.11 | 235.97 | 23.35 (night) |
| Y2022 (survey-driven) | 302.77 | 142.76 | 23.21 (night) |
| B_central (survey-driven) | 331.46 | 148.88 | 23.28 (night) |

**Residential channel, weekday people presence:**
| Arm/scenario | night mean (people) | midday mean (people) | weekday peak hour |
|---|---|---|---|
| U (Default_NECB, unfair control) | 3.67 | 518.88 | 12.21 (midday) |
| F (Default_NECB, fair control) | 667.13 | 222.38 | 23.59 (night) |
| Y2022 (survey-driven) | 408.59 | 131.15 | 11.62 (broad/bimodal profile) |
| B_central (survey-driven) | 390.61 | 187.75 | 0.92 (near-midnight) |

Secondary effect (people gains shift the internal-gain timing slightly): channel EUI (CFA basis)
moves by -3.92 kWh/m2 (hotel) and -3.82 kWh/m2 (residential), +0.91 (office) and +0.59 (retail);
weekday energy (not occupancy) peak hour shifts by only -0.02 to -0.05 h per channel.

**One-sentence verdict:** once the code control's own apartment and hotel-guest-room occupancy
is switched from the office-shaped NECB-A schedule to the residential-shaped NECB-G (dwelling-
unit) schedule, the control (F) itself swings to a night-heavy presence pattern for both channels
-- as large as, and for these four cells somewhat larger than, the survey-driven arms' night
presence -- so the hotel/residential night-presence contrast that P3 reported between the code
control and the survey-driven arms is a limitation of the unfair NECB-A control, not a property
of the survey data, and it shrinks sharply (for these two channels, essentially disappears in
direction, though F overshoots the survey arms' magnitude) once the control is made fair.

## 7. Ledger

| When (2026-09-24) | Job/step | What | State | Output |
|---|---|---|---|---|
| verify | `sacct -j 1342434` | 4/4 tasks COMPLETED, 0:0 | ran and fired (all ok) | section 1 |
| verify | 4x `cat manifest.json` | status=ok, build_F objects_changed=4/added=1 on all 4 | ran and fired | section 1 |
| copy | `du -sh` + `scp -r` x4 | 906M cluster -> 906M-equiv local, RAM/disk checked before | done | `_local_runs/3J_V3c/runs/V3c/F__*` |
| aggregate | Step-8E, 1 process | 4/4 `[ok]`, attribution residual 0.0% | done | `IMP/data/V3c/agg_V3c_F/agg_*.csv` |
| compare | `v3c_compare.py` gate 1 (U vs U) | did not fire (0.000000 max diff) | PASS | `data/V3c/selftest/*_UvU.csv` |
| compare | `v3c_compare.py` gate 2 (altered U) | ran and fired (448.67 max diff, localized to the edit) | PASS | `data/V3c/selftest/*_CLEANALT.csv` |
| compare | `v3c_compare.py` (real F vs U) | ran and fired (real, expected differences) | done | `data/V3c/v3c_comparison_{summary,diff}.csv`, `v3c_per_cell_metrics.csv`, `v3c_presence_by_hour.csv` |

## 8. What I did not verify

- Did not re-run or touch Step-9 (`3rdJ_09_activityDrivenLoads_4split.py`) for arm F, so there is
  no GFA-share-basis EUI or `step9_loadshape_peaks.csv`-style table for F; the CFA-basis EUI from
  `agg_annual_by_channel.csv` is the only EUI comparison made here. It is at least the same basis
  for both arms, but I did not check it against the Step-9 GFA-share basis some published tables
  use.
- Did not check whether other, non-PEOPLE objects in the hotel/residential channels moved their
  own occupancy or plug/lighting schedules between the F build and the U build; `V3c_fair_control.md`
  section 4 says lights/equipment were left untouched by `v3c_build_F.py`, and I relied on that
  claim (backed by its own static-diff gate, section 4 of that doc) rather than re-diffing the
  IDFs myself here.
- Did not re-verify Y2022/B_central's own numbers (pulled read-only from the frozen
  `agg_deliverable` for context in section 6 only) -- those are P3's numbers, already controlled
  there; I did not re-run P3's own control/negative-control suite.
- Whole-building peak-hour and coincidence-factor gap between F and U (0.028 h, 0.0007) is small
  enough that I cannot rule out it being within run-to-run EnergyPlus solver noise rather than a
  real effect of the schedule change; not tested against a repeat run (none was done, one run per
  cell as designed).
- Did not clean up `IMP/data/V3c/agg_V3c_F_altered/`, `agg_U_altered/`, or `selftest/` -- kept as
  the on-disk record for section 5; small (CSV-only, no re-copied `.sql`/`.csv` run outputs), left
  in place rather than deleted.
