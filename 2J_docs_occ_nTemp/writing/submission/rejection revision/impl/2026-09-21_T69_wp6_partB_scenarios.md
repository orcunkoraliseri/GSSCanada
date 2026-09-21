# T69 -- WP6 Part B: end use x hour decomposition on the three scenario arms

You are a Sonnet employee on the 2J Applied Energy resubmission. Cluster-only. Read
`CLAUDE.md` at the repo root first (top rule: `sbatch` only, never a blocking `srun` or bare
python on the login node). Submit your job(s), write state to the IMPL doc, **end your turn** --
do not wait or poll. Collection is the manager's job.

## 0. Why this task exists

WP6 Part A (`T68`) decomposed end use x hour for the MAIN 2022-to-2030 rebuild and was ACCEPTED
(`impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md`, plan log (de)). Part B does the same for
the three scenario arms the paper also reports (checklist B4/B4b/B6): the reviewer wants to see how
the load shape differs depending on how much of the 2020-22 work-from-home shift persists to 2030.
Per plan §4 ("Phase 3: WP6 on corrected 2030 + scenarios"), this is the last piece WP6 owes before
WP11 (figures) can use its output.

## 1. Inputs -- read-only, never edit any of these

- `T21/out/step8/<cell>/sample_NNN_HHxxxxx/2022/hourly_meters.csv` -- the common 2022 baseline,
  full 1,200 households (24 cells x 50), same tree T68 already used.
- `T29/out/lambda_0.0/<cell>/sample_NNN_HHxxxxx/2030/hourly_meters.csv` -- work-from-home fully
  reverts by 2030 ("S-None" in the paper's naming). **2030 only, no 2022 subfolder** -- confirmed by
  directory listing before writing this doc.
- `T29/out/lambda_0.5/<cell>/sample_NNN_HHxxxxx/2030/hourly_meters.csv` -- half the shift persists
  ("S-Partial"). 2030 only.
- `T32/step8_std/out/<cell>/sample_NNN_HHxxxxx/2030/hourly_meters.csv` -- **note the path**: T32's
  household hourly files live under `T32/step8_std/out/`, NOT `T32/out/` (that folder holds only
  aggregate CSVs and an HTML report -- checked before writing this doc). This is the
  population-mix-held-fixed scenario (checklist B4b), a different scenario dimension from the two
  lambda arms above, not a third lambda value. Label it `S-Revert-std` everywhere, never grouped
  under a lambda number.
- `T66/scripts/step9_validate_full_corrected.py` -- read-only, for `T66_CELL_EQUIP_DIVISOR` and
  `T66_CELL_LIGHT_DIVISOR` (unchanged from T68, do not re-derive).
- `T67/T67_scripts/cell_cluster_bootstrap.py` and `T68/T68_scripts/enduse_hour_corrected.py` --
  read-only references for the two functions you are reusing (see Ruling 2 below).

**Do not use** `T29/out/t29_p3_deltas.csv` or `T32/out/std/t32_metrics_std.csv` /
`t32_metrics_primary.csv` as a source of trusted numbers for anything in this task. The T29 file's
own `n_paired_households=1200` for a scenario known to deliver only 1,198 is exactly the
not-on-common-basis problem plan item 30 already ruled un-quotable -- it is background only, never a
validation target.

## 2. What T21's 2022 tree and each scenario's 2030 tree do NOT share automatically

**Confirmed by directory listing before this task went out:** `T29/out/lambda_0.0/` has 1,198
household-year folders (2 short of 1,200 -- `OtherDwelling__Vancouver_5C` sample 9 and one other
cell), `T29/out/lambda_0.5/` has the full 1,200, and T32's `step8_std/out/` is expected to be short
by the one household plan item 33 names (`OtherDwelling__Vancouver_5C` sample 9 again) -- **you must
verify T32's actual count yourself**, do not assume it matches the number in this paragraph.

## 3. Rulings -- fixed by the manager, not yours to redecide

1. **Household basis, two-tier.** For each scenario arm on its own, build its 2022-to-2030(scenario)
   change table using every household actually present in BOTH that scenario's 2030 folder AND
   `T21`'s 2022 folder for the same `<cell>/sample_NNN_HHxxxxx>` name -- determined by discovery, never
   assumed to be 1,200. A household present in the scenario's 2030 output but absent from T21's 2022
   tree (should not happen, since all scenarios are drawn from the rebuilt population, but check, do
   not assume) is excluded and logged by name. **Separately**, for any table or number that compares
   ACROSS scenario arms (e.g. "how does the midday load shape differ between S-None, S-Partial,
   S-Revert-std and the main 2030"), restrict to the households common to **every** arm being
   compared in that specific table, and print the exact household count used, per arm, next to the
   number. Do not produce a cross-scenario number on any other basis.
2. **Script reuse, not a rewrite.** Copy (never edit) `T68_scripts/enduse_hour_corrected.py` into a
   new `T69_scripts/` folder. Reuse its per-household meter-processing function, its divisor logic,
   its `safe_pct_change`, its zero-2022-denominator exclusion, its closure identity, and its
   `stock_weighted_cluster_bootstrap` (T68's ACCEPTED, verified-genuine cluster bootstrap -- read
   `impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md`'s Manager collection section for why it was
   accepted) exactly as they stand. What must change is **discovery**: T68's `discover_runs()`
   expects one root with both `2022/` and `2030/` under every household folder. These three scenario
   trees are 2030-only, so write a new discovery function that, for a given scenario root, finds
   every delivered `2030/hourly_meters.csv`, then looks up the SAME `<cell>/sample_NNN_HHxxxxx>` path
   under `T21/out/step8/.../2022/hourly_meters.csv` for its paired baseline. Log every miss.
3. **Divisor tables, quotable-core rule (relative quantities only for fan/facility/thermal meters),
   percent-change-denominated CI, and the T28/T60 `excludes_zero` rule are unchanged from Part A.**
   Read plan log (dd)/(de) if any of this is unclear before writing code.
4. **C2's seen-working control needs its own new reference per arm** -- T67's `agg_annual.csv` and
   T29's `p3_deltas.csv` do not cover these metrics on this basis (T29's file is explicitly
   not-to-be-trusted per §2 above). For **each of the three scenario trees**, hand-compute annual kWh
   and peak kW for one real household (pick the first delivered sample in `SingleD__Toronto_5A` in
   each tree) directly from its `hourly_meters.csv`, and match your script's own output for that same
   household to at least 6 significant figures. C1 (clock-shift) and C3/C4 (divisor invariance and
   sanity) reuse T68's exact method, run once per scenario arm.
5. **Label S-Revert-std distinctly.** It is the population-mix-held-fixed scenario (checklist B4b),
   not a third work-from-home persistence level. Never print it in a column or chart series that
   implies it sits on the same lambda axis as S-None/S-Partial.
6. **Output schema matches T68's `enduse_change_2022_2030.csv` exactly**, plus a `scenario` column
   (`S-None`, `S-Partial`, `S-Revert-std`), so one file can be read by all three arms together and, if
   the manager wants it later, concatenated with T68's own file (which is implicitly `scenario =
   S-Full`, the main 2030 rebuild) for a single WP11 figure input. Do not concatenate it yourself --
   that is a manager decision at collection, not yours.

## 4. Deliverables (mirror T68's structure)

Per scenario arm, under `T69/out/<scenario_name>/`:
`enduse_annual.csv`, `enduse_hourly_profile.csv`, `grid_metrics.csv`, `closure.csv`,
`enduse_change_2022_2030.csv` (this arm's own household basis), `controls.json`, `run_meta.json`
(must include `controls_all_fired`, `n_households_year_read_ok`/`skipped`, the divisor tables used,
the zero-2022-denominator counts, and an `undelivered_csv_sweep` that actually reads any
`undelivered.csv` under that scenario's tree, per item 31's fix already applied in T68).

One additional file, `T69/out/cross_scenario_common_basis.csv`: the household-count table required by
Ruling 1's second sentence -- for every pairwise and four-way combination of {S-Full (T68, for
reference only, do not recompute it), S-None, S-Partial, S-Revert-std} that a manuscript figure might
plausibly need, the exact household count in the intersection.

Job(s): reuse T68's resource shape (`-p ps -c 8 --mem=32G -t 7-00:00:00`) via `sbatch --wrap`. One
job covering all three arms sequentially is fine (T68's whole real run took under 90 seconds); do
not over-provision. Log at `T69/logs/t69_run.out`.

## 5. Implementation doc

Create `impl/2026-09-21_T69_wp6_partB_scenarios_IMPL.md` before submitting, same skeleton as T68's
(Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), and write the JobID(s) to it the
moment `sbatch` returns. End your turn immediately after. Do not read any output file after
submission -- that is the manager's job, in this same fixed order every time: `run_meta.json`'s
`controls_all_fired` first, then `controls.json`, then results.
