# T23 — Audit: did published runs silently use fallback standard schedules? — implementation state

Task doc:   this file. Trigger: T19 Decisions (`2026-09-15_T19_wp3_static_arm_build_smoke.md`, FINDING on
`idf_optimizer.py:625`): `load_standard_residential_schedules()` looks for `schedule.json` two directory
levels up from `idf_optimizer.py` (the `Step8_docs` level), but the file lives at the repo root
`0_BEM_Setup/Templates/schedule.json`. With `verbose=False` it silently returns `_get_fallback_schedules()`.
Status:     DONE

## Why it matters (manager)
If any published 2J number (Step 8 single-building campaign, Step 9 neighbourhood "Default" arm via
`integration.inject_neighbourhood_default_schedules`, or any equipment/lighting/DHW shape) came from this
function, it used a hardcoded approximation, not the DOE MidRise profile the manuscript describes. Read-only
audit; no fix, no reruns in this task.

## Questions (answer each with file:line evidence)
- Q1 Every call site of `load_standard_residential_schedules` and `_get_fallback_schedules` in the 2J code
  actually used for the published runs (`2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/`, Step 9 code,
  `run_bem.py`, `run_paired_mc.py`, and any `eSim_bem_utils/` copy they import). Which arguments, which
  `verbose`.
- Q2 For each call site: which published output depends on it (which arm, which figure/table if the step
  docs say), and from which directory the published runs executed (step docs / logs). Does
  `schedule.json` exist at the two-levels-up path in THAT layout? (`Glob`/`ls` locally only.)
- Q3 Side by side, fallback values vs real `schedule.json` MidRise values: occupancy, equipment, lighting,
  weekday and weekend, 24 hours each; report max abs difference per series. Read both from source/JSON
  (small files); do not run anything.
- Q4 Any surviving published run log (Step 8/9 outputs, local) that contains the string
  "schedule.json not found" or evidence of which path was taken. Use `Grep` with a file glob on log/out
  files; never open multi-MB files whole.
- Q5 Verdict in one line per published arm: AFFECTED / NOT AFFECTED / UNKNOWN, and why.

## Brief (employee, Sonnet)
Local read-only. No edits to any existing file. No Speed jobs. No python runs on large files. Write answers
under Verified as you go; end with Status DONE. Guard context: `Grep` before `Read`, read ranges not whole
big files.

## Ledger

## Verified

**Q1 — call sites (live code only; `archive/integration.20260603.py` and `.20260604.py` are superseded,
excluded).** All three live calls are in `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py`:
- `integration.py:1360` — `idf_optimizer.load_standard_residential_schedules(verbose=False)`, inside
  `inject_schedules()` (single-building, per-household path; function spans `integration.py:1269-1989`).
  `verbose` is hardcoded `False` at this call — the file-not-found warning is unconditionally suppressed.
- `integration.py:2045` — `idf_optimizer.load_standard_residential_schedules(verbose=verbose)`, inside
  `inject_neighbourhood_schedules()` (`integration.py:1989-2320`, default param `verbose: bool = True`
  at `integration.py:1997`, but the effective value depends on the caller).
- `integration.py:2351` — `idf_optimizer.load_standard_residential_schedules(verbose=verbose)`, inside
  `inject_neighbourhood_default_schedules()` (`integration.py:2320-...`, default param
  `verbose: bool = True` at `integration.py:2325`) — this is the Step 9 "Default" arm named in the task.
- No `_get_fallback_schedules()` call sites outside `idf_optimizer.py` itself (`idf_optimizer.py:632,645`,
  both inside `load_standard_residential_schedules`) — nothing calls the fallback function directly.
- Callers of `inject_neighbourhood_default_schedules` (both pass through to the `verbose=verbose`
  call above): `main.py:1320` — `verbose=True`, batch/6-scenario flow, `scenario == 'Default'` branch
  (`main.py:1315-1320`); `main.py:2282` — `verbose=False`, second neighbourhood-comparison flow
  (`main.py:2272-2282`, output literally named `Scenario_Default.idf` under a `Default/` subdir). Both
  produce the Step 9 "Default" arm.
- No `eSim_bem_utils/` (non-`_2J`) copy is imported by the published-run entry points: `run_bem.py:22`
  and `run_paired_mc.py:25-26` both import from `eSim_bem_utils_2J` only
  (`sys.path.insert(0, dirname(__file__))` then `from eSim_bem_utils_2J.main import ...`). A separate
  `eSim/eSim_bem_utils/` tree exists at the repo root but nothing under `2J_docs_occ_nTemp` imports it.
- Critically: `verbose` never changes whether the fallback fires — `idf_optimizer.py:628-632` returns
  `_get_fallback_schedules()` whenever `os.path.exists(schedule_json_path)` is `False`, unconditionally;
  `verbose` only gates the one `print()` warning at `idf_optimizer.py:629-630`. So the `verbose=False`
  call sites are silently affected in exactly the same way as the `verbose=True` ones.

**Q2 — which output, which directory, does the file exist there.**
- `base_dir` is computed from `idf_optimizer.py`'s own `__file__`
  (`os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`, `idf_optimizer.py:625`) — independent
  of which script imports it or its cwd. For the live tree this resolves to
  `.../2J_docs_occ_nTemp/Step8_docs`, so the lookup path is always
  `.../2J_docs_occ_nTemp/Step8_docs/0_BEM_Setup/Templates/schedule.json`.
- Confirmed locally: no such nested path exists anywhere under `2J_docs_occ_nTemp` — `find ... -iname
  "schedule*.json"` over the whole repo returns only `0_BEM_Setup/Templates/schedule.json` and
  `schedule_sf.json` at the **repo root** (`GSSCanada-main/0_BEM_Setup/Templates/`), plus a
  `BEM_Setup/Templates/schedule_sf.json` — never a copy nested inside `2J_docs_occ_nTemp/Step8_docs/`.
- Published Step 8 runs executed with `cd /speed-scratch/o_iseri/GSSCanada/GSSCanada-main/
  2J_docs_occ_nTemp/Step8_docs && sbatch step8_smoke.sh` etc. (`Step8_docs/cluster_rerun.md:93,102,109`)
  — i.e. the cluster tree mirrors the same `GSSCanada-main/2J_docs_occ_nTemp/Step8_docs/...` layout as
  local, so `idf_optimizer.py`'s 2-up path resolves the same broken way there (no cluster access to
  re-check the cluster copy directly per task rules; inferred from identical relative layout, consistent
  with T19's own finding that this bug is layout-inherent, not staging-path-dependent).
- Output dependency, single-building (Step 8): `standard_schedules` (from the `1360` call) feeds
  `idf_optimizer.scale_water_use_peak_flow(idf, standard_schedules, verbose=True)`
  (`integration.py:1461`) — DHW peak-flow scaling for every single-building run — and supplies the
  `PresenceFilter` reference curves `std_weekday`/`std_weekend` per `std_key` in
  `integration.py:1732-1733` for LIGHTS/ELECTRICEQUIPMENT/GASEQUIPMENT/WATERUSE:EQUIPMENT whenever the
  Step-9-consolidation carrier is not active for that object type (`integration.py:1724-1727`).
- Output dependency, Step 9 neighbourhood "Default" arm: `inject_neighbourhood_default_schedules` uses
  `standard_schedules` **directly as the injected profile** — `default_light_weekday/weekend`,
  `default_equip_weekday/weekend`, `default_occ_weekday/weekend`, `default_water_weekday/weekend`,
  `default_activity` are all read straight from the dict (`integration.py:2354-2367`) with no further
  transformation. The docstring explicitly claims "DOE MidRise Apartment schedules... OpenStudio
  Standards Gem... ASHRAE 90.1" (`integration.py:2331-2338`). Referenced in
  `Step9_docs/si_appendix_step9.md:357` as "Fig S9 — Default vs activity-driven equipment demand" and
  the "presence-only baseline" arm of the 4-archetype x 6-climate-zone x 2-year x 2-arm validation grid
  (`si_appendix_step9.md:165-193`, Table S4.3 SHEU gates evaluated on the *activity* arm only, not the
  Default/baseline arm — the SHEU ±15% gate does not check the Default arm's shape).
- `inject_neighbourhood_schedules` (`2045` call, non-default neighbourhood-matched arm) uses
  `standard_schedules` for the same lighting/equipment/DHW/occupancy defaults comment
  ("Use Standardized Residential Schedules for all defaults... ensures consistency with Option 3",
  `integration.py:2038-2061`) before per-household schedules from `schedules_list` override them.

**Q3 — fallback vs real `schedule.json`, side by side.** Read `_get_fallback_schedules()`
(`idf_optimizer.py:734-767`) and `0_BEM_Setup/Templates/schedule.json` (repo root, 2258 bytes, read
whole). The real file's `"ApartmentMidRise ..._SCH"` entries each carry a single `"...Default"`
day-schedule (no separate Weekday/Weekend identifiers) — so `load_standard_residential_schedules()`'s
own Default-branch logic (`idf_optimizer.py:700-705`) sets `Weekday == Weekend` from that one array,
exactly mirroring the fallback's `'Weekend': x.copy()` of the same weekday array (`idf_optimizer.py:763-
766`). Compared value-for-value (24 hourly values each):
  - occupancy: fallback `[1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.85,0.39,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.30,
    0.52,0.87,0.87,0.87,1.0,1.0,1.0]` vs JSON `OCC_APT_SCH` `values` (`schedule.json:9`) — **identical**,
    max abs diff = 0.0.
  - equipment: fallback `[0.45,0.41,0.39,0.38,0.38,0.43,0.54,0.65,0.66,0.67,0.69,0.70,0.69,0.66,0.65,0.68,
    0.80,1.00,1.00,0.93,0.89,0.85,0.71,0.58]` vs JSON `EQP_APT_SCH` `values` (`schedule.json:18`) —
    **identical**, max abs diff = 0.0.
  - lighting: fallback `[0.01,0.01,0.01,0.01,0.03,0.07,0.08,0.07,0.03,0.02,0.02,0.02,0.02,0.02,0.02,0.04,
    0.08,0.11,0.15,0.18,0.18,0.12,0.07,0.03]` vs JSON `LTG_APT_SCH` `values` (`schedule.json:27`) —
    **identical**, max abs diff = 0.0.
  - dhw (not in Q3's named list but load-bearing for the DHW-scaling dependency above): fallback
    `[0.08,0.04,0.02,0.02,0.04,0.27,0.94,1.00,0.96,0.84,0.76,0.61,0.53,0.47,0.41,0.47,0.55,0.73,0.86,0.82,
    0.75,0.61,0.53,0.29]` vs JSON `APT_DHW_SCH` `values` (`schedule.json:36`) — **identical**, max abs
    diff = 0.0.
  - activity: fallback `95.0` (`idf_optimizer.py:767`) vs JSON `Activity Schedule` `values` = `[95.0]`
    (`schedule.json:45`) — identical.
  - Weekday and Weekend are identical to each other in BOTH sources for every series (fallback by
    explicit `.copy()`; real JSON because its only day-schedule identifier is `"...Default"`, which the
    loader applies to both — `idf_optimizer.py:700-705`).
  - **The hardcoded fallback numbers are byte-for-byte the same numbers as the real
    `schedule.json` Default profile.** This is a code-path bug (wrong function executed, wrong file
    silently skipped, no real file I/O happened) but NOT a numeric-content bug for these four series —
    whichever branch ran, the same 24 values were injected.

**Q4 — log search.** `Grep` for `schedule\.json not found|not found at|Warning:.*schedule\.json|Loaded
DOE MidRise|Using DOE MidRise Apartment standard schedules` across every `*.log`/`*.out`/`*.txt` under
`2J_docs_occ_nTemp/` (recursive) returns **no matches**. Checked file sizes first (all ≤ 386,881 bytes,
none multi-MB): `Step8_docs/campaign_N50_err.log` (0 B), `campaign_N50_run.log` (1.6 KB),
`r2b_wfh_delta/r2b_run.log` (16.9 KB), `step8_rebuild_agg.log` (5.5 KB), `step8_validation_run.log`
(4.8 KB), `_bigtest/_logs/*.log`, `_gen_all.log` (3.9 KB); `Step9_docs/s9_warmup60_951832.out` (386.9 KB),
`step9_cluster/step9_loadshape_aggregate.log` (4.9 KB), `step9_cluster/step9_validate_full.log`
(9.4 KB), `step9_relaunch.log` (0.9 KB), `step9_val_run.log` (2.6 KB). No surviving local log records
which branch (real file vs fallback) was taken on any run — consistent with `verbose=False` at the
Step 8 single-building call site (`integration.py:1360`) and with the "Using DOE MidRise..." message
(`integration.py:2064`, unconditional print inside `inject_neighbourhood_schedules` when `verbose=True`)
never appearing, meaning either that call ran with effective `verbose=False` or its stdout was not
captured into any of these files.

**Q5 — verdict per published arm.**
- Step 8 single-building campaign (`inject_schedules`, DHW scaling + PresenceFilter defaults):
  **AFFECTED (code path), NOT AFFECTED (numeric outcome)** — fallback fired silently (file missing at
  the buggy 2-up path), but its occupancy/equipment/lighting/DHW values are numerically identical to
  the real `schedule.json` Default profile, so the injected numbers match what the real file would have
  produced.
- Step 9 neighbourhood "Default" arm (`inject_neighbourhood_default_schedules`, `Scenario_Default.idf`,
  Fig S9 / si_appendix_step9.md baseline comparisons): **AFFECTED (code path), NOT AFFECTED (numeric
  outcome)** — same reasoning; docstring's DOE-MidRise/OpenStudio/ASHRAE provenance claim was not
  actually read from disk, but the values used equal the ones that file contains.
- Step 9 neighbourhood-matched arm (`inject_neighbourhood_schedules`, non-Default scenarios): **AFFECTED
  (code path) for the default-fill values only, NOT AFFECTED (numeric outcome)** — same fallback dict
  feeds the lighting/equipment/DHW/occupancy defaults before per-household overrides; per-household
  schedule data itself (from GSS-derived CSVs) is untouched by this bug.
- No arm is numerically wrong from this bug for the four compared series (occupancy, equipment,
  lighting, DHW); the bug is real (wrong code path, unconditionally suppressed warning, no actual file
  read) but has zero measured effect on these four series' values because the fallback constants were
  copied from the same source file.

## Decisions

## Next
Employee: Q1-Q5. Manager: if any published arm is AFFECTED → add to revision plan as a correction item and
decide rerun scope; the T22 static arm already uses the real `schedule.json`.

## WHAT I DID NOT VERIFY
- Did not check the cluster's actual on-disk copy of `2J_docs_occ_nTemp/Step8_docs/0_BEM_Setup/` (no
  cluster access allowed this task) — inferred it does not exist there from the identical local repo
  layout and T19's own finding; not a direct read.
- Did not verify `schedule_sf.json` (`baseline='sf_detached'`) call sites or values — Q1-Q5 scope is the
  `midrise` baseline / `schedule.json` used by the published arms; `sf_detached` is documented in
  `load_standard_residential_schedules()`'s docstring as "robustness check only; does not affect
  production runs unless explicitly passed" (`idf_optimizer.py:582-585`) and no call site in the live
  `integration.py`/`main.py` passes `baseline='sf_detached'`.
- Did not trace every downstream consumer of the DHW-scaled/PresenceFilter values (e.g. exact per-hour
  contribution to final annual kWh in each published table/figure) — confirmed the dependency exists and
  the two named 24-value inputs are numerically identical to the real file, which is sufficient to settle
  Q3-Q5 without re-deriving full downstream aggregates.
- Did not open or run any script; no cluster job submitted; no existing file edited other than this doc.
