# EMPLOYEE PROMPT v2 — Step 8 Apartment Cooling Fix, INJECTOR-LEVEL + Local Smoke (3J Leg-2)

> Paste-ready. Manager-authored 2026-07-08. Supersedes the v1 prompt (archived at
> `Step8_docs/archive/step8_coolfix_employee_prompt.20260707_v1_idfPatch.md` — do NOT execute it).
> Execute top-to-bottom; the session-boundary protocol tells you where to stop and report.

---

**You are the employee. Execute the task below and append a Progress Log entry on completion**
(to BOTH `investigation/step8_coolfix_implementation_plan.md` and
`investigation/step8_resid_heating_cooling_dominance_investigation.md`).

## Context (read these first, in this order)

All paths relative to `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\` locally and to
`/speed-scratch/o_iseri/step8_2split/upload/...` on the cluster. Phases A–C (code fix, static
verify, 4-run smoke) run **locally** (the queue is saturated; the smoke is explicitly a local
job per the user). On a smoke PASS you continue in the SAME session into Phase D — upload +
full 4,200-run cluster array submission — then stop.

1. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_coolfix_implementation_plan.md`
   — THE runbook, especially the **"Fix v2 — injector-level seasonal cooling override"** section.
   This prompt operationalizes that section; if this prompt and the plan disagree, flag it, don't guess.
2. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`
   — the confirmed diagnosis. §9 explains why fix v1 (patching the static IDF templates) failed:
   `inject_setpoint_schedules()` in `eSim_bem_utils_3J/integration.py` collapses ANY static
   schedule to one flat year-round constant, so the seasonal template patch never reached the sim.
   The fix must live in the injector itself.

**Scope guard:** you edit exactly ONE code file — `Step8_docs/eSim_bem_utils_3J/integration.py`
— plus one small new verify script. Do NOT touch: `main.py`, `3rdJ_08B_run_paired_mc.py`, the
validator (gate 4.9 already added), any IDF template (the `Buildings_MTL_v242_3Jfix/` dir from v1
stays as-is — inert but intentionally kept), the house archetypes, the office channel, heating
setpoints, or internal-load densities. Do NOT git-commit anything (user owns git).

**Local-run guard:** the smoke is 4 EnergyPlus runs (~3 min each) — light and safe, but run them
attended in the foreground, sequentially, never in parallel; this box cannot be rebooted remotely
if it wedges.

## Phase A — injector code change (locally)

1. Archive predecessor: copy `Step8_docs/eSim_bem_utils_3J/integration.py` →
   `Step8_docs/eSim_bem_utils_3J/archive/integration.20260708_preCoolfixInjector.py`.
2. Edit `integration.py` — three pieces, nothing else:

   **(a) Module-level config**, near the other top-of-file constants, with a comment citing the
   plan's Fix-v2 section:
   ```python
   # CoolFix v2 (step8_coolfix_implementation_plan.md "Fix v2"): seasonal cooling-setpoint
   # relief for the two ASHRAE-90.1 apartment prototypes whose native schedule holds 24.0C
   # year-round (winter internal-gain cooling artifact; investigation doc §2/§8/§9).
   COOLFIX_ARCH_SUBSTRINGS = ('APARTMENTMIDRISE', 'APARTMENTHIGHRISE')
   COOLFIX_WINTER_COOL_SP = 28.0   # variant 1a; 1b fallback = 40.0 (winter lockout)
   COOLFIX_WINTER_MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'Oct', 'Nov', 'Dec')
   ```

   **(b) `inject_setpoint_schedules()` (~line 1112):** add optional param
   `cooling_seasonal_override: dict = None` (pass the config as e.g.
   `{'winter_sp': 28.0, 'winter_months': (...)}`).
   - When `None`: behavior byte-identical to today — do not restructure any existing code.
   - When set AND `use_schedule_file` is truthy: `raise ValueError` with a clear message
     (the campaign uses the Schedule:Compact path; the fix must fail loudly, never drop silently).
   - When set (Compact path): build the **cooling** schedule via the EXISTING helper
     `create_monthly_compact_schedule(new_cool_name, 'Temperature', monthly)` instead of
     `_compact_setpoint`, where `monthly` maps all 12 month abbreviations to
     `{'Weekday': [...], 'Weekend': [...]}` lists of `{'hour': h, 'value': v}` dicts:
     - **Winter months** (`winter_months`): `v = max(winter_sp, cooling_setback)` (= 28.0) for
       all 24 hours, both day types. Flat on purpose — the 27.0 absence setback must never sit
       BELOW the seasonal relief value (that would command MORE cooling when absent).
     - **All other months (May–Sep):** exactly today's values — the `wd_cool` / `we_cool` lists
       already computed by `_build_setpoint_schedule()` (active 24.0 occupied / 27.0 absent),
       just wrapped into the `{'hour','value'}` dict format.
     - The **heating** schedule build is untouched (still `_compact_setpoint`).
     - Keep the existing remove-stale-schedules re-run-safety block working for the new object.
   - Note on autosizing: `create_monthly_compact_schedule` already assigns
     `SummerDesignDay WinterDesignDay` the Weekday pattern of the containing month, so the July
     summer design day keeps today's 24.0/27.0 pattern → cooling autosizing unchanged. Do NOT
     add any design-day special-casing.

   **(c) `inject_schedules()`, right before the `inject_setpoint_schedules(...)` call
   (~line 1996):** build the override from the filename gate and pass it through:
   ```python
   _fname = os.path.basename(idf_path).upper()
   cooling_seasonal_override = None
   if any(s in _fname for s in COOLFIX_ARCH_SUBSTRINGS):
       cooling_seasonal_override = {'winter_sp': COOLFIX_WINTER_COOL_SP,
                                    'winter_months': COOLFIX_WINTER_MONTHS}
       print(f"  [CoolFix] seasonal cooling override active "
             f"(winter SP {COOLFIX_WINTER_COOL_SP}C, months {','.join(COOLFIX_WINTER_MONTHS)})", flush=True)
   ```
   and add `cooling_seasonal_override=cooling_seasonal_override` to the call. Filename gating is
   deliberate — every path that injects into an apartment IDF (campaign, smoke, one-offs) gets
   the fix uniformly with zero changes outside this file.
3. `py -m py_compile Step8_docs/eSim_bem_utils_3J/integration.py` must pass.

## Phase B — static injection verification (locally, BEFORE any simulation)

This is the check that would have caught v1 without burning a single sim. Write
`Step8_docs/investigation/verify_coolfix_injection.py`:

4. The script imports `integration` (3J), loads one real household schedule the same way the
   campaign does (via `integration.load_schedules` on the existing local
   `BEM_Schedules_2split_*.csv` inputs — mirror how `main.py` / the smoke path resolves them),
   then calls `integration.inject_schedules()` twice into a scratch dir
   (`Step8_docs/outputs_step8/coolfix_verify/`):
   - once with the **MidRise** template from `Buildings_MTL_v242_3Jfix/` (+ the Winnipeg EPW),
   - once with the **DetachedHouse** template (no-op control).
5. It then parses both generated IDFs and asserts, printing PASS/FAIL per check:
   - MidRise `CoolSP_HH_*`: is a `Schedule:Compact` with **per-month `Through:` blocks**; every
     winter-month block (Jan–Apr, Oct–Dec) is 28.0 for all hours/day-types; every summer-month
     block (May–Sep) contains only 24.0/27.0; the `[CoolFix]` line appeared in stdout.
   - MidRise `HeatSP_HH_*`: single `Through: 12/31` block, values unchanged vs the archived-code
     behavior (22.x/18.0 pattern).
   - DetachedHouse `CoolSP_HH_*`: still the flat single-block form (24-ish/27.0) — no-op proof
     for non-gated archetypes.
6. If any assertion fails → fix Phase A and re-run. Do not proceed to Phase C on a FAIL.

## Phase C — local 4-run smoke + gate (locally)

7. Fresh out-dir: `Step8_docs/outputs_step8/campaign_smoke_v2/` — do NOT reuse or mix with the
   failed v1 smoke outputs (`campaign_smoke/`). Leave v1 outputs in place for provenance.
8. Run the same runner as the v1 local smoke (`3rdJ_08B_run_paired_mc.py`, local Python env,
   EnergyPlus 24.2 at `C:\EnergyPlusV24-2-0`), two sequential invocations, attended:
   `--arch MidRise --city Winnipeg_7A --scenario 2022 --n 2 --seed 42 --mode standard
   --out-dir <campaign_smoke_v2>` then the same with `--arch HighRise`. (4 runs total, ~3 min
   each.) Before trusting results, spot-grep one generated `in.idf` per archetype for the
   monthly `CoolSP_HH_*` blocks (same criteria as Phase B) and check each run's `eplusout.err`
   / console for E+ Severe/Fatal (a malformed Schedule:Compact fatals out).
9. Run `investigation/probe_winter_cooling.py` with `STEP8_CAMP_DIR` pointed at
   `campaign_smoke_v2`.
10. **Smoke gate (all three):**
    - DJF cooling per archetype **< 10% of pre-fix** (pre-fix DJF baselines from
      investigation §8.1: MidRise 16,474 kWh, HighRise 34,126 kWh);
    - annual heating clearly **up** vs pre-fix (MidRise 9,740 / HighRise 71,636 kWh §8.1);
    - no E+ Severe/Fatal in any of the 4 runs.
    - **PASS →** continue DIRECTLY into Phase D (no user check-in needed — the full-run GO is
      pre-authorized on a smoke PASS). **FAIL →** apply fallback **1b ONCE without asking**: set
      `COOLFIX_WINTER_COOL_SP = 40.0`, redo Phase B + Phase C; if 1b passes, continue to Phase D.
      If 1b also fails → STOP and report (manager must re-diagnose; do not iterate further, do
      NOT proceed to Phase D).

## Phase D — cluster subset re-sim (pre-authorized on smoke PASS; same session)

## 🔴 Cluster hard rules (account-suspension risk — no exceptions)

- NEVER run python or any compute on the login node (`speed-submit2`). NEVER blocking `srun`.
  Everything computational goes through `sbatch` (fire-and-forget, read the log file later).
- Allowed on login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, mkdir,
  module load`, single-file `tail/head/grep/wc -l/cat`.
- EVERY job requests `-t 7-00:00:00` walltime. Every cluster command is a single line.
- Do NOT poll job status. Submit, report the job ID, stop.
- Label every command you show as "locally" or "on the cluster".

11. Upload (locally): scp the edited `integration.py` (and `verify_coolfix_injection.py` for
    provenance) to the matching paths under
    `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/`.
    If variant 1b ended up live, the uploaded file must be the 1b version — state which variant
    was uploaded in your report.
12. Preserve pre-fix outputs (on the cluster, single line — rename, don't delete):
    `mkdir -p /speed-scratch/o_iseri/step8_2split/campaign_precoolfix && mv /speed-scratch/o_iseri/step8_2split/campaign/MidRise__* /speed-scratch/o_iseri/step8_2split/campaign/HighRise__* /speed-scratch/o_iseri/step8_2split/campaign_precoolfix/`
13. Write locally + scp up `run_residential_array_coolfix.sh`: copy of `run_residential_array.sh`
    with `#SBATCH --array=84-167` (MidRise = 84–125, HighRise = 126–167 per the cell-idx decode
    `arch_idx = idx // 42`) and job name `3J_8B_coolfix`. NOTHING else changes (seed 42 preserves
    the paired HH sampling; keep the E+ SIF `EPWRAP` scaffolding intact).
14. Submit (on the cluster): `sbatch .../Step8_docs/run_residential_array_coolfix.sh`.
    84 tasks × 50 sims = 4,200 runs; queue may be saturated (`AssocGrpCpuLimit`) — fire-and-forget,
    expect days, no polling.

## STOP — report (session boundary)

15. **STOP here.** Report: what changed in `integration.py` (with line refs), Phase-B check
    results, the smoke before/after table (DJF + annual heat/cool per archetype vs §8.1), the
    gate verdict, which variant (1a or 1b) is live, and the array job ID. Append dated Progress
    Log entries to BOTH docs (step 0 of this prompt). Downstream refresh (8D `--rebuild` → 8E →
    Step-9 → campaign-scale probe → docs) follows the v1 runbook Phases 6–7 in
    `step8_coolfix_implementation_plan.md` in a LATER session, once the user relays that the
    array finished.

## Blockers

Anything ambiguous, any FAIL outside the rules above, any file that doesn't match what this
prompt says it contains (e.g. `create_monthly_compact_schedule` signature differs, the schedule
CSVs can't be located the way `main.py` finds them) → stop and flag to the user for the manager.
Do not improvise around a mismatch.
