# CONTINUATION — Fix v3: metric re-base (same session; your v2 smoke FAIL is the input)

You are the **employee**, continuing in this same session. Your two smoke FAILs (1a/1b) were the
decisive experiment: the manager root-caused the anomaly from your preserved outputs
(investigation **§11** — read it now, plus the new **"Fix v3"** section of
`step8_coolfix_implementation_plan.md`; both in `Step8_docs/investigation/`).

**TL;DR of the diagnosis:** the winter "cooling" was never mechanical. `Cooling:EnergyTransfer`
sums `Zone Air System Sensible Cooling Energy` (proven in your runs' `eplusout.mtd`), and every
apartment unit has a thermostat-independent `ZoneHVAC:EnergyRecoveryVentilator` (24 MidRise / 46
HighRise) whose post-heat-recovery supply air is below room temperature all winter — metered as
"cooling" at zero electricity. Your 24/28/40°C insensitivity is exactly what that predicts. The
model is fine; the **metric** is wrong. Fix v3 changes aggregation + validation only.
**NO re-simulation — the existing 25,200 campaign runs stay valid.**

Execute Phases V3-A → V3-D below, then STOP after the chained sbatch submission and report.
Append a Progress Log row to `step8_coolfix_implementation_plan.md` when you stop.

---

## 🔴 Cluster hard rules (unchanged, account-suspension risk — flagged 3×, one more = ban)

- NEVER a blocking `srun` or bare `python` on the login node (`speed-submit2`). `sbatch` only,
  fire-and-forget. NO polling — submit and stop.
- EVERY job: `-t 7-00:00:00` walltime, no exceptions.
- Allowed on the login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, mkdir,
  module load`, single-file `tail/head/grep/wc -l/cat`. Nothing else.
- Single-line commands; label every command "locally" or "on the cluster".

---

## Phase V3-A — revert the v2 injector override (local)

The override's premise is falsified AND it perturbs real results (your 1a→1b annual cooling
electricity moved 136.12 → 118.48 GJ — shoulder-season compressor lockout). It must not survive.

1. Locally: archive the current `eSim_bem_utils_3J/integration.py` →
   `eSim_bem_utils_3J/archive/integration.20260708_coolfixInjector_v2_falsified.py` (keep for provenance).
2. Locally: restore `eSim_bem_utils_3J/integration.py` from
   `eSim_bem_utils_3J/archive/integration.20260708_preCoolfixInjector.py` (your Phase-A archive).
3. Verify all three, report results:
   - `py_compile` passes;
   - `cooling_seasonal_override` / `COOLFIX_` appear **0 times** in the restored file;
   - restored file is byte-identical (SHA-256) to the pre-fix archive.

Do NOT touch `Buildings_MTL_v242_3Jfix/`, `main.py`, or anything in 2J. Gate 4.9 is re-based in
V3-D, not removed. You never uploaded the v2 integration.py to the cluster — confirm that remains
true (nothing to clean up remotely).

## Phase V3-B — retention spot-check (on the cluster, one command)

4. On the cluster: `ls` the first sample's 2022 dir of the MidRise Winnipeg campaign cell, e.g.
   single-line: `ls /speed-scratch/o_iseri/step8_2split/campaign/MidRise__Winnipeg_7A/` then one
   more `ls` into its first `sample_*/2022/`. Confirm **`eplusout.sql`** is present (expected —
   the runner persists it by design; `eplustbl.csv` bonus but not required).
5. **If `eplusout.sql` is missing: STOP and report** — fallback (subset re-sim with added
   `Output:Meter`) is a separate manager decision. Otherwise continue.

## Phase V3-C — End-Uses extractor (author locally, run on cluster via sbatch)

6. Locally: write `investigation/extract_enduse_annual.py`. **Stdlib only** (os, glob, csv, re,
   sqlite3) — no pandas, so any cluster python module works. Behavior:
   - Walk `<campaign>/<cell>/sample_*/<year>/eplusout.sql` (campaign root from env
     `STEP8_CAMP_DIR`, default `/speed-scratch/o_iseri/step8_2split/campaign`).
   - Per sql, run exactly this (query verified locally against your v2 smoke sql):
     ```sql
     SELECT RowName, ColumnName, Value FROM TabularDataWithStrings
     WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
       AND TableName='End Uses' AND RowName IN ('Heating','Cooling')
     ```
     Values are strings with padding (e.g. `'      136.12'`), units GJ — `float(value.strip())`.
   - One output row per run: `cell, arch, city, cz, scenario, sample, hh_id, heating_gas_GJ,
     heating_elec_GJ, heating_district_GJ, cooling_elec_GJ, cooling_gas_GJ, cooling_district_GJ`
     (arch/city from the cell dir name `ARCH__City_CZ`, cz = city suffix; sample/hh_id from
     `sample_NNN_HHxxxxx`; district = sum of the three District columns).
   - Skip-and-log unreadable sql files; final tally line `dirs=N parsed=N skipped=N`.
   - Write `agg_enduse_annual.csv` into the same directory the 8D agg tables live in (where
     `agg_annual.csv` lands — you know the path from the 8D runs).
7. Locally: dry-run the extractor against the local smoke tree
   (`STEP8_CAMP_DIR=outputs_step8/campaign_smoke_v2`) — expect 4 rows, MidRise sample_001 2022
   showing `cooling_elec_GJ=136.12`, `heating_gas_GJ=78.34`. Gate: exact match. FAIL → fix before
   any upload.
8. scp the script up (label: locally), then on the cluster submit single-line fire-and-forget:
   `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd <Step8 dir> && <cluster python> investigation/extract_enduse_annual.py > extract_enduse_annual.out 2>&1"`
   (reuse the python path/module pattern from your previous run scripts). Note the job ID.

## Phase V3-D — validator re-base (edit locally, upload, chained submit)

9. Locally: archive `3rdJ_08_simulation_2split_val.py` →
   `archive/3rdJ_08_simulation_2split_val.20260708_preV3metric.py`, then two changes:
   - **Gate 4.9-heat-dominance**: source = `agg_enduse_annual.csv`; ratio =
     `cooling_elec / (heating_gas + heating_elec + heating_district)` (site GJ), per archetype ×
     CZ 6A/6B/7A. Thresholds unchanged (FAIL > 2.0 in 7A; WARN > 1.25 in 6A/6B/7A). Update the
     gate's printed label to say "end-use energy" so the metric is self-documenting.
   - **§4 report**: add an end-use table (heating fuel vs cooling electricity, archetype × CZ,
     from the new csv) and relabel the existing ET-based §4 rows as
     "air-system delivered sensible energy (incl. ventilation air)". Touch nothing else.
   - `py_compile`; do NOT regenerate the report locally.
10. scp the edited validator up (locally), then on the cluster submit the validator chained to the
    extractor, single-line: `sbatch --dependency=afterok:<extractor job id> -p ps --mem=16G -t 7-00:00:00 --wrap "cd <Step8 dir> && <cluster python> 3rdJ_08_simulation_2split_val.py <usual args> > step8_val_v3.out 2>&1"`
    (reuse the exact invocation pattern from the 8E re-val job 1062194 era scripts). Note the job ID.

## STOP + report

11. STOP here. No polling. Append a Progress Log row to `step8_coolfix_implementation_plan.md`
    (revert verification results, dry-run gate result, both job IDs, chained dependency stated),
    and report to the user: Phase results, the two job IDs, and that next session (after the user
    relays completion) = scp `agg_enduse_annual.csv` + regenerated report down, check gate 4.9
    (expected: **WARN ~1.7× in 7A, not FAIL** — prototype characteristic, paper-framing note),
    then docs refresh.

**Expected end state of this session:** injector reverted and verified locally; extractor
dry-run-passed locally and submitted on the cluster; re-based validator uploaded and queued behind
it; no re-simulation anywhere; 2J untouched.
