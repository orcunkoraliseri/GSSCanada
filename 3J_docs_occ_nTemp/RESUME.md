# RESUME — Opus Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Opus session to continue.**
Last updated: 2026-07-01 (Step 8 VALIDATED end-to-end, both channels; §8D aggregation DONE;
Step-9 office EUI benchmark gate DONE & PASSING — scorecard 46/1/13/0. Next = paper reporting).
First read CLAUDE.md and memory/MEMORY.md (esp. `project_step8_2split_status.md`,
`project_step8_2split_8D_design.md`), then resume as if no break happened.

---

## 0. Who you are

You are the **MANAGER (Opus)** in a two-agent workflow for the GSSCanada occupancy
modeling research (3rd journal = **"3J"**, Leg-2 = **"2-split"** = two-channel
AT_HOME + AT_WORK joint occupancy model).

- **You plan / debug / judge / write builder prompts. You do NOT execute, submit cluster
  jobs, or run live poll loops.** The employee handles execution + relays results; you act
  only on terminal outcomes.
- **Cheap Haiku/Sonnet "employees" do ALL execution** — scp, sbatch, log peeks, monitoring,
  retrieval, large-file scans. ALWAYS set `model:` on every Agent call (bg agents silently
  inherit Opus). Prefer a silent background `Monitor` bash poll loop over an agent watcher for
  waiting on a job (zero model tokens while polling); min ~30-min spacing; no live poll loops
  in Opus.
- You are "both manager and sometimes employer": if the user hands you a current runbook AND
  confirms, you may execute that one cycle. Default is plan/debug only.
- Communication: casual, ≤100 words unless detail requested. End with the literal command to
  run. Resolve clarifying questions BEFORE printing a builder prompt.

## 1. HARD RULES (never violate — account-suspension risk)

1. **NEVER** run a blocking/interactive `srun` (or any python/computation) on the Speed
   **login node** `speed-submit2`. ALWAYS `sbatch` (fire-and-forget), then read the output
   file. Flagged 3× — one more = suspension = all progress lost.
2. **NO bare `python`/`python3` on the login node — ever** (incl. one-liners). Allowed on
   login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, ssh, module load`,
   single-file `tail/head/grep/wc -l/cat`. Anything importing pandas/numpy/torch/eppy or
   iterating dirs → `sbatch`.
3. **EVERY job submission MUST request `-t 7-00:00:00`** (1-week min). Speed ps/pg MaxTime =
   7 days. A 1h cap once killed control job 987005 with empty output.
4. Speed login shell is **tcsh**: no `2>&1` (use `>` only; SLURM captures stderr to
   `--output`); one short line per command, no `\` continuation.
5. **Label every command "locally" or "on the cluster."**
6. **Bundle uploads** — one upload cycle; never file-by-file across cycles. Never upload the
   whole `GSSCanada-main/` dir; only named files/dirs.
7. Before any `sbatch` handoff, scan script imports — ensure eppy/pandas/numpy/torch/etc.
   exist in the cluster env (`envs/step4`); add a precheck line if unsure.
8. Archive predecessor (`cp` to `archive/`) before any edit. Update progress logs
   **live/incrementally**, not batched.
9. **Full audit, no patches**: when one cluster cycle reveals a bug, audit the whole chain and
   ship ONE fix bundle.

## 2. Cluster facts (Speed @ Concordia)

- host: `o_iseri@speed.encs.concordia.ca` (passwordless ssh/scp from this Windows box via Git
  Bash); login node = submission only; GPU partition = `pg`, CPU = `ps`.
- python: `/speed-scratch/o_iseri/envs/step4/bin/python`
- EnergyPlus 24.2 SIF: `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`
- Step-8 scratch dir: `/speed-scratch/o_iseri/step8_2split/` — upload tree under `upload/`,
  logs `logs/`, residential output `campaign/`, office output `office/`, agg tables
  `upload/…/Step8_docs/outputs_step8/agg/`.
- Step-4 base ckpt (LOCKED): `…/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt`

---

## 3. WHERE WE ARE — Steps 1–7 DONE; Step 8 VALIDATED end-to-end (both channels); §8D DONE

**Steps 5/6/7 closed** (memory `project_step{5,6,7}_2split_status`). Step-7 deliverables in
`Leg2_2-split/Step7_docs/outputs_step7/`: residential `BEM_Schedules_2split_{2022,2030_*}.csv`
(REPLACE) + office `office_presence_multiplier_{2022,2030}.csv` (MODULATE).

**Step 8 = two-channel EnergyPlus simulation — COMPLETE & VALIDATED.** All in
`Leg2_2-split/Step8_docs/`. Scope (locked): 7 scenarios both channels
(`2005 2010 2015 2022 2030-conservative 2030-hybrid 2030-fullyhybrid`); full coupling
People+Lights+Equipment; HVAC/DHW code baseline; peak densities never modified.
- **Residential campaign (job 1029756): DRAINED CLEAN** — 8,400 cells (4 arch × 6 CZ × 7 scen
  × N=50 paired MC), 168/168 tasks ok, 0 errors. Symlink/bind bug resolved (`--bind
  /nfs/speed-scratch`).
- **Office campaign (job 1048238): DRAINED CLEAN** — 252 deterministic runs (3 arch ×
  Tall/SuperTall × 6 CZ × 7 scen).
- **§8E validation scorecard (job 1053668):** 27 PASS / 0 WARN / 13 INFO / 0 FAIL. Plotted
  re-run (job 1053902) confirmed the "no-plots" bug fixed (5 embedded charts).
- **§8D aggregation + validation refresh (job 1053986): COMPLETE 2026-07-01** (COMPLETED, exit
  0, Elapsed 01:52:25). Two-pass "summarize-on-read": `3rdJ_08_simulation_2split_agg.py`
  streamed all 8,652 runs (8,400 resid + 252 office) → `outputs_step8/agg/{agg_diurnal(1.28M
  rows),agg_annual,agg_meta,agg_peak(8,652 each)}.csv`; then `3rdJ_08_simulation_2split_val.py`
  re-ran with §4/§5/§7 (+§6.1/6.4–6.7) now reading real agg tables. **Scorecard 45 PASS / 1 WARN
  / 13 INFO / 0 FAIL; 8 embedded charts.** HTML pulled local:
  `Leg2_2-split/Step8_docs/outputs_step8/step8_validation_report.html` (717,173 bytes).
  - **The one WARN (non-blocking, expected):** SingleD median EUI 213 kWh/m² outside SHEU band
    [131–186] — pre-documented basis mismatch (our EUI = site energy ÷ *conditioned* area incl.
    basement; SHEU = heated area *excl.* basement, so conditioned-basis SingleD reads high).
    Other 3 archetypes in-band.
- **Step-9 office EUI benchmark gate (job 1054800): DONE & PASSING 2026-07-01** (COMPLETED, exit
  0, Elapsed 00:08:35 — fast Pass-2 re-validate, agg tables reused). Both office deepResearch
  prompts landed and are encoded in `3rdJ_08_simulation_2split_val.py`: `OFFICE_EUI_BAND =
  (135,100,200)` kWh/m² (as-modelled NECB2020/90.1-2019 DOE-PNNL Tall/SuperTall prototype — our
  IDFs ARE these; the pass criterion) + `OFFICE_EUI_EMPIRICAL = (230,170,360)` (SCIEU/CEUD measured
  stock, INFO context only). Result: **§4.3-office median office EUI 180 kWh/m² PASS** (in-band,
  per-arch range 160–216); §4.4 empirical INFO. **Scorecard flipped 45→46 PASS / 1 WARN / 13 INFO
  / 0 FAIL** (the office §4.3 INFO→PASS). Refreshed HTML 724,540 bytes, 8 charts (office EUI panel
  now bars+band), pulled local byte-identical. This closes the office half of 3J Step 9 (the
  mechanical half — Lights/Equipment × AT_WORK presence — was already in Step 8 via OD-8B).

Key files: `3rdJ_08_simulation_2split.md` (design + live Progress Log — canonical),
`…_val.md` (validation spec), `3rdJ_08_simulation_2split_agg.py` (NEW §8D aggregator),
`3rdJ_08_simulation_2split_val.py` (validator, §8D-extended), `run_aggregation.sh`,
`eSim_bem_utils_3J/` (engine, `plotting.calculate_eui`).

## 4. WHAT'S DONE — full pipeline through Step 8

Steps 1–7 closed; Step 8 built, corrective-cycled, both campaigns drained clean, validated
end-to-end (§8E scorecard + §8D EUI/load-shape rollup). Two-channel campaign is now a complete,
validated dataset ready to write up. The 13 INFO gates are mostly office-side reported metrics
(no numeric benchmark band encoded yet) + a few informational cross-channel notes — none are
blockers.

## 5. WHAT'S NEXT — paper reporting

The dataset + all gates are closed. One thread remains:

1. ~~**Office EUI numeric gate.**~~ **DONE 2026-07-01** (job 1054800). Both deepResearch prompts
   landed; office band encoded (`OFFICE_EUI_BAND=(135,100,200)` as-modelled PNNL = pass criterion;
   `OFFICE_EUI_EMPIRICAL=(230,170,360)` SCIEU = INFO). §4.3-office median EUI 180 kWh/m² PASSES.
   Scorecard 46/1/13/0. Office half of Step 9 closed.

2. **Paper reporting (the live thread).** Step 8/9 is the results backbone (load shapes, peak-hour
   timing, the 2015→2022 COVID break, the 2030 WFH-band energy spread, office vs NECB-prototype
   EUI). Begin drafting the 3J results/methods sections from the validated campaign + the 8 report
   charts. (2J submission copy `readySubmission.md` is the style reference — see memory
   `project_2j_paper_writing`.) One paper caveat worth a sentence: the top office archetype EUI
   (216) pokes just above the 200 prototype ceiling; the gate is on the median (180, in-band) so
   it's non-blocking, but note it.

**Suggested opening line to the user:** "Step 8/9 is fully closed — both channels drained clean,
§8D aggregation done, and the office EUI gate now PASSES (median 180 kWh/m² inside the NECB-PNNL
band). Scorecard 46/1/13/0, 8 charts, only the expected SingleD-basis WARN. Want to start drafting
the 3J results section?"
