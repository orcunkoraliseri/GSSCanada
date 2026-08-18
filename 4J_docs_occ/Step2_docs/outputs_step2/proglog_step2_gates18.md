# Progress Log fragment — Step 2, eighteen-gate battery (2026-08-17)

*Fragment only — for the manager to merge into `4thJ_02_harmonisation.md` /
`4thJ_02_harmonisation_val.md`. Not itself a Progress Log entry.*

## What ran

The full eighteen-gate battery (`tools/4thJ_gates_step2.py --perturbation all`) ran over the real,
already-accepted `harmonised.parquet` (2,024,068 rows, 3 countries: ES/UK/IT) — 22 sweeps (1 baseline
+ 21 perturbations), 18 gates each. This was **a local run on the author's own Windows desktop**, not
a Speed HPC job: the machine already had all required inputs (crosswalks, Step 1 episodes/codebooks,
`filter_report.md`) and a working local `pandas`/`numpy` environment, and the job ran in well under a
minute of compute. It was **not** a submission governed by the Speed cluster rules.

Caveat on record: the first attempt at this same run, launched the same way, **died mid-battery when
the employee agent's session ended** — the local background process does not survive its agent. It
stopped after 10 of 22 sweeps (`gates18_run_20260817/full_sweep_report.txt`, truncated, kept as
evidence, not used for any number below). The manager re-launched the identical command from the
manager's own shell (which survives across turns) into a fresh output directory,
`gates18_run_20260817b/`, which completed all 22 sweeps and is the authoritative artefact for
everything below. The lesson recorded for future full-table batteries: **a `sbatch` job on Speed would
have survived the session where the local run did not** — prefer Speed for anything of this size going
forward.

## Baseline verdict per gate

18 gates scored per sweep, every sweep, all 22 sweeps (confirmed by direct count — no sweep silently
scored 17). At baseline: **17 scored gates** (`G2.10` excluded), **16 PASS, 1 FAIL**.

| Gate | Baseline | Note |
|---|---|---|
| G2.1–G2.9 | PASS | |
| G2.10 | NOT CHECKED | no published national time-use table held by the project; excluded from the scored tally (never a pass) |
| G2.11–G2.17 | PASS | |
| G2.18 | **FAIL** | sub-clause (a) only — see Finding 1 |

## The 21 perturbations — did each fell its named gate

20 of the 21 perturbations carry a named target gate; `null` is the no-op control (confirmed: moved
nothing).

| Perturbation | Target gate | Result |
|---|---|---|
| null | (control) | moved nothing — confirmed |
| del_activity_row | G2.1 | FIRED |
| strip_citation | G2.2 | FIRED |
| scale_duration | G2.3 | FIRED (see Finding 2 — also felled G2.4) |
| round_duration | G2.4 | FIRED |
| add_one_to_many | G2.5 | FIRED |
| empty_outdoor | G2.6 | FIRED |
| drop_spain_age | G2.7 | FIRED |
| zero_missing_flag | G2.8 | FIRED |
| pool_modal_code | G2.9 | FIRED |
| shift_sleep_budget | G2.10 | DID NOT FIRE — expected: G2.10 is never scored (NOT CHECKED at baseline and under perturbation alike) |
| remap_spain_transport | G2.11 | FIRED |
| wrong_rotation | G2.12 | FIRED |
| italy_catcon_swap | G2.13 | FIRED |
| spain_cop_bool | G2.14 | FIRED |
| spain_secondary_repoint | G2.15 | FIRED |
| uk_group1_carry | G2.16 | FIRED |
| null_strat_econ_status | G2.17 | FIRED |
| strat_day_type_wrong_grain | G2.17 | FIRED |
| italy_hh_type_prefix | G2.18 | FIRED (whole-gate; see M-7 sub-clause note below) |
| italy_age_band_split | G2.18 | FIRED (whole-gate; see M-7 sub-clause note below) |

19 of 20 named mappings FIRED as designed. The one non-firer (`shift_sleep_budget -> G2.10`) is
expected by construction, since G2.10 can never score PASS or FAIL.

## M-7 sub-clause attribution — G2.17 / G2.18

Because `G2.18` already reads FAIL at baseline (see Finding 1), whole-gate PASS/FAIL cannot tell
whether the two perturbations that target `G2.18` actually fired their own specific defect. The
battery's field-level `subclause_counter()` mechanism (acceptance test 2b) is what's authoritative
here — counter value at baseline vs. under the targeting perturbation:

| Perturbation | Sub-clause | Baseline counter | Perturbed counter | Result |
|---|---|---|---|---|
| null_strat_econ_status | G2.17 (a) | 0 | 19 | FIRED |
| strat_day_type_wrong_grain | G2.17 (b) | 0 | 1 | FIRED |
| italy_hh_type_prefix | G2.18 (a) | 0 | 6 | FIRED |
| italy_age_band_split | G2.18 (b) | 0 | 1 | FIRED |

All four fired cleanly at the field level, independent of G2.18's pre-registered whole-gate FAIL.

## Coverage cross-tab

Acceptance test 4 builds the full 18-gate x 22-sweep cross-tab. Result: **coverage clause PASS** —
the list of gates that PASS at baseline and were never made to fall anywhere across the 21
perturbations is **empty (`[]`)**. Every gate that can PASS was demonstrated failing somewhere in the
sweep.

## Finding 1 — G2.18 FAILs at baseline (reported, not repaired)

Sub-clause (a): `leak_bands(declared-availability) = 0` but `escalations(prevalence, D-S2-19) = 3`.
**Zero leaks is the substantive result** — no band is emitted by exactly one country. The whole-gate
FAIL comes from the escalation clause alone.

The three escalations (derived by applying the escalation rule already on record — literal
"share > 10x smallest of the other two," no zero-filtering — to the `unknown`-band shares printed in
the baseline country x stratum cross-tab; not itself printed as a labelled list by the report):
- `strat_hh_type`, `unknown` share es=0.000% / uk=3.514% / it=0.000% — escalates once, on **UK**.
- `strat_econ_status`, `unknown` share es=0.000% / uk=0.519% / it=4.243% — escalates twice, on **UK**
  and **IT**.

1 + 2 = 3, matching the printed count exactly.

Whether an escalation driven by `unknown`'s own share should carry a whole-gate FAIL, or be reported
as a flagged note beside an otherwise-passing leak clause, is a band/threshold question — the
author's call, not the employee's or the manager's. Not repaired, not silenced, nothing moved.

## Finding 2 — Acceptance test 3 reports one clean violation

`scale_duration` (targeting `G2.3`) also felled `G2.4`, but `G2.4` is listed in `scale_duration`'s row
as "must stay clean." Test 3's own output: `"VIOLATION: scale_duration felled G2.4 (baseline=PASS,
perturbed=FAIL) but its row lists G2.4 as must-stay-clean"`, `clean violations = 1`.

This is the same entanglement as the standing limitation that **`G2.3` is not demonstrated
independently of `G2.4`** — previously a note, now visible as a hard, measured violation rather than
a note. Reported as found; no perturbation was added, removed, or adjusted to repair it (adding a row
to a pre-registered table is the author's call).

## Standing limitations restated

- **`G2.3` is still not demonstrated independently of `G2.4`.** `scale_duration` (G2.3's own
  perturbation) also moves G2.4 (Finding 2), so the two gates are not shown falling independently of
  one another in this battery.
- **`G2.10` remains `NOT CHECKED`.** No published national time-use table is held by the project; a
  re-tabulation of the project's own harmonised data would share an ancestor with the reference and
  cannot fail, so it is not substituted. `NOT CHECKED` is never a pass, and G2.10 is excluded from
  every scored tally in this report (17 of 18 gates scored, everywhere).

## WHAT I DID NOT VERIFY

- The three baseline `G2.18(a)` escalations (Finding 1) are not printed as a labelled per-stratum
  list anywhere in the report — the aggregate count (3) is printed; the per-stratum/per-country
  breakdown above is this agent's derivation from the printed `V2.j` cross-tab and the already-agreed
  escalation formula, not a number the runner itself emitted.
- The employee's earlier `Decision 4` note in the implementation doc quotes `strat_econ_status`
  `unknown` shares as "ES 0.0%, UK 6.3%, IT 13.5%"; the actual `_b` baseline report prints
  es=0.000%, uk=0.519%, it=4.243%. The discrepancy is not reconciled here — flagged for the
  author/manager. The numbers used above are the ones printed in the authoritative `_b` report.
- `crosswalk_strata.csv` was not opened directly to independently confirm the raw rows behind
  `G2.18(a)`'s `leak_bands`/`(b)`'s `it_conflicts` counters — only the runner's printed counts and
  the before/after deltas under the two targeting perturbations were read.
- The 21 x 18 = 378 individual gate cells across all perturbation sweep bodies were not each
  hand-re-verified line by line beyond what the coverage cross-tab (generated from the same run)
  already tabulates.
- `V2.k`'s reference numbers (446,547 / 567,381 / 1,010,140 episodes; 37,830 / 0 / 0 splits) were
  confirmed to match the report's printed numbers exactly, but were not independently re-derived from
  `harmonised.parquet` in this task.
