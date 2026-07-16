# 3rd Journal — Step 8 — EMPLOYEE BUILD PROMPT

> Manager-authored handoff, 2026-06-28. The user delivers this to a fresh employee (Sonnet) session. Paste from the line below.

---

**You are the employee. Execute the task below and append a `Progress Log` entry to `3rdJ_08_simulation_2split.md` on completion.** Stay within scope; flag any blocker back to the user (who relays to the manager). Do not expand scope or invent pipeline steps.

## Mission

Build the **Step 8 two-channel EnergyPlus simulation** for the 3J Leg-2 pipeline: residential (REPLACE, paired Monte-Carlo) + office (MODULATE, deterministic), across **7 scenarios** (2005 / 2010 / 2015 / 2022 / 2030-conservative / 2030-hybrid / 2030-fullyhybrid). You write and locally smoke-test the code, bundle the cluster upload, and hand back the exact `sbatch` commands. **You do NOT submit cluster jobs — the user runs every `sbatch`.**

## Read first (do not skip)

1. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split.md` — the design doc. Every decision is locked there (§0 table). This prompt is the execution layer; the design doc is the source of truth.
2. `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_val.md` — the validation spec you build the validator against.
3. J2 sources to port (`2J_docs_occ_nTemp/Step8_docs/`): `08_gen_cycle_schedules.py`, `run_paired_mc.py`, `eSim_bem_utils_2J/` (`integration.py`, `simulation.py`, `schedule_generator.py`, `config.py`, `run_batch_hpc.py`), `step8_val_v2.py`, `08_simulation_plots.py`.

## Locked scope (do not re-litigate)

- **7 scenarios, both channels.** Historical (2005/2010/2015) schedules do NOT exist yet → sub-step 8A generates them first.
- **Full coupling:** People + Lights + Equipment occupancy-coupled in BOTH channels. Office Lights `L=max(Lmin,η·O·D)` (`Lmin=0.15, η=1.0, D=1.0` unless the IDF has `Daylighting:Controls`); office Equipment `P=Pbase+(1−Pbase)·O` (`Pbase=0.20`). HVAC/DHW stay at code baseline. Code peak densities (people/m², LPD, plug) are NEVER modified — only temporal shape.
- **Office:** 3 archetype schedules (Knowledge/Public/Sales) × 2 envelopes (Tall/SuperTall) × 6 CZ × 7 scen = **252 deterministic runs**.
- **Residential:** 4 arch × 6 CZ × 7 scen × N=50 paired = **8,400 runs**.
- `Interpolate to Timestep = No` on all injected schedules.

## Tasks (ordered)

### 8C.0 — Office IDF version transition (do early; gates 8C)
- Transition the 4 office IDFs `BEM_Setup/Buildings/CAN_{CLG,MTL}/{Tall,SuperTall}Building_…_v221.idf` from **EnergyPlus v22.1 → v24.2** (same transition chain J2 ran for the residential stock; run the E+ transition utilities via the SIF on the cluster, or document the local transition path).
- Audit zone tagging for Tag-2 routing (apartment / office / hotel-retail / MEP) and report which zones are office-tagged.
- Report whether the prototypes contain `Daylighting:Controls` (decides D(t) handling per design §5). Flag back; do not guess.

### 8A — Historical schedule generation (gates the whole campaign)
- Port `08_gen_cycle_schedules.py` onto the 3J two-channel machinery: load the locked Step-4 model (`Step4_docs/outputs_step4/checkpoints/best_model.pt`), generate per-cycle augmented diaries for 2005/2010/2015 (both heads), apply the locked 04L/04M calibration, run the Step-7 `3rdJ_07_aug_to_bem_2split.py` path per cycle.
- **Deliverables** → `Step8_docs/outputs_step8/historical_schedules/`: `BEM_Schedules_2split_{2005,2010,2015}.csv` (13-col) + `office_presence_multiplier_{2005,2010,2015}.csv` (7-col). Byte-identical headers to the 2022 files.
- Must pass val **§0** (schema, row counts, calibration, longitudinal continuity, no NaN) before launching any EnergyPlus run.

### 8B — Residential campaign
- Create `eSim_bem_utils_3J/` as a versioned copy of `eSim_bem_utils_2J/` (OD-8J). All Step-8 edits go in the 3J copy; never touch the 2J copy.
- Adapt `run_paired_mc.py`: 7 scenario labels, `STEP8_BUILDINGS_DIR → 2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`, 3J stock (`BEM_Schedules_2split_*.csv`, 23,211 HH). Add the Lights/Equipment occupancy-coupling (design §4a). Resume-on-restart.
- Run the **OD-8F pool-size audit** first: for each (DTYPE × PR) cell confirm ≥ 50 HH; any cell < 50 → document + with-replacement sampling (never silently drop).

### 8C — Office campaign
- Build `office_integration.py` per design §5 (People + Lights + Equipment `Schedule:Compact`; density preserved; Tag-2 zone gate). Build an `office_runner.py` that produces the modified IDF → runs E+ once via the SIF → parses `hourly_meters.csv`.

### 8D / 8E — Aggregation + validation
- Port `08_simulation_plots.py` for the rollups/figures (design §8).
- Build `3rdJ_08_simulation_2split_val.py` implementing every gate in the val spec → `outputs_step8/step8_validation_report.html`. Report the PASS/WARN/INFO/FAIL tally.

## Cluster hard rules (account-suspension risk — NON-NEGOTIABLE)

1. **`sbatch` ONLY.** No `srun`, no bare `python`/`python3` on the login node `speed-submit2` — not even one-liners. (Flagged 3×; one more = suspension = all progress lost.)
2. Every job `-t 7-00:00:00` (7-day) minimum walltime.
3. Login shell is `tcsh`: single-line commands, no `\` continuation, no `2>&1` (use `>&` or omit).
4. EnergyPlus 24.2 via the SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`; cluster python `/speed-scratch/o_iseri/envs/step4/bin/python`.
5. **Module precheck before any handoff:** scan every script's imports and confirm `eppy`, `pandas`, `numpy`, `torch`, `joblib`, `yaml` (and anything else used) exist in the cluster env at `/speed-scratch/o_iseri/envs/step4/`. If any is missing, add an install/precheck line to the wrapper — do not assume.

## What you do locally vs. what the user runs

- **You (local):** write all scripts; smoke-test on a tiny subset (e.g. 1 arch × 1 CZ × 2 scenarios × N=2 residential; 1 office archetype × 1 envelope × 1 CZ × 1 scenario) to prove the pipeline end-to-end produces a valid `hourly_meters.csv`; bundle the cluster upload into ONE `scp -r` per cycle; write the SLURM array wrappers (`run_residential_array.sh`, `run_office_array.sh`).
- **You hand back to the user (literal commands, one line each):** the single `scp -r` upload command, then the exact `sbatch …` submission commands for the residential and office arrays. The user runs them and relays job IDs/output.
- **You do NOT:** submit `sbatch` yourself, run any blocking `srun`, poll `squeue`/`sacct` in a loop, or run Python on the login node.

## Guardrails

- The residential REPLACE path must stay numerically faithful to J2; the office channel is purely additive. Do not alter any Leg-1/J2 residential result.
- Before editing any predecessor script, `cp` it to `Step8_docs/archive/<name>.<predecessor>_<date>.py` in the same change.
- Update the Step-8 Progress Log incrementally as sub-steps complete — do not batch at the end.
- Smallest practical change; preserve naming/workflow conventions; cite exact file:line when referencing code.

## Deliverables checklist

- [ ] 8C.0 office IDFs transitioned v22.1→v24.2 + zone-tag + daylighting report
- [ ] 8A historical schedules (6 CSVs) passing val §0
- [ ] `eSim_bem_utils_3J/` + adapted `run_paired_mc.py` (residential, full coupling)
- [ ] `office_integration.py` + `office_runner.py` (office, full coupling)
- [ ] OD-8F pool-size audit result
- [ ] SLURM wrappers + bundled upload command + `sbatch` commands for the user
- [ ] `3rdJ_08_simulation_2split_val.py` + smoke-test evidence
- [ ] `Progress Log` entry appended to `3rdJ_08_simulation_2split.md`

Flag any blocker (missing module, ambiguous zone tag, pool cell < 50, transition error, daylighting ambiguity) to the user before proceeding past it.
