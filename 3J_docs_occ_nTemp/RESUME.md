# RESUME — Opus Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Opus session to continue.**
Last updated: **2026-07-02 — 🔴 OFFICE WFH BUG FOUND + FIXED, RE-SIM IN FLIGHT.** While finishing
Step 9 we discovered the office channel was simulated WITHOUT working WFH modulation: all 7
scenarios byte-identical in every metric (peak/occ/shape/energy). Root cause (confirmed, NOT stale
cache): `office_integration.py` read the pre-v24.2 zone field `Zone_or_ZoneList_Name`, but E+ v24.2
renamed it → every zone read as "" → all tagged 'skip' (`n_office_zones=0`) → the band-specific
OFC_* schedules were appended but never wired to a zone → E+ ran the prototype `NECB-A-Occupancy`
for all scenarios. FIXED (added `_get_zone_name` v24.2-robust helper + corrected the PEOPLE
`Number_of_People_Schedule_Name` field); SMOKE-VALIDATED (job 1057831: n_office_zones=6,
HOURLY_DIFFER, People wired to OFC_People). **Re-sim array job 1058490 (`run_office_resim.sh`,
0-251, `--no-skip`) launched, PENDING on AssocGrpCpuLimit; Sonnet drain-watch running.** So the
prior "Step 8 VALIDATED 46/1/13/0" and "Step 9 ~80% done, re-source from peak/shape" are SUPERSEDED
for the office half — see §6. (Residential unaffected: scenario response varies correctly.)
First read CLAUDE.md and memory/MEMORY.md (esp. `project_step8_office_wfh_bug.md`,
`project_step9_2split_status.md`), then resume as if no break happened.

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

**Suggested opening line to the user:** "Step 8 is fully closed and the unified Step 9 (both
channels) is built — job 1055064 just needs its outputs collected + the two pipeline docs reframed
(see below). Want me to finish Step 9 first, then start the 3J results section?"

---

## 6. 🔴 DO THIS FIRST — office re-sim (job 1058490) → re-agg → finish Step 9

> **⚠️ THE OLD PLAN BELOW IS SUPERSEDED.** It assumed office annual metrics were merely
> "degenerate" and the WFH signal lived in peak/shape — WRONG. A 2026-07-02 probe found the office
> channel was simulated with **NO working WFH modulation at all** (E+ v24.2 zone-field rename bug;
> full detail in `memory/project_step8_office_wfh_bug.md`).

**STATE:** office bug FIXED in `Step8_docs/office_integration.py` (v24.2 zone field via new
`_get_zone_name` helper + corrected PEOPLE `Number_of_People_Schedule_Name`); smoke-validated
(job 1057831: n_office_zones 0→6, HOURLY_DIFFER, People wired to OFC_People). Re-sim **array
1058490** (`Step8_docs/run_office_resim.sh`, `--array=0-251`, `--no-skip`) IN FLIGHT — overwrites
`/speed-scratch/o_iseri/step8_2split/office`; PENDING on AssocGrpCpuLimit; Sonnet drain-watch
running (25-min poll). Residential untouched.

**WHEN 1058490 DRAINS CLEAN** (sacct: 252 COMPLETED; 252 `hourly_meters.csv`; spot-check
`Office_Knowledge__SuperTall__6A` 2022 vs 2030-fullyhybrid = DIFFER):
1. **Re-aggregate §8D** — `sbatch Step8_docs/run_aggregation.sh` (`3rdJ_08_simulation_2split_agg.py`)
   → fresh `outputs_step8/agg/{agg_annual,agg_peak,agg_diurnal,agg_meta}.csv`. Office now varies by
   scenario in peak/occ/diurnal (annual energy stays ~flat = HVAC-dominated — expected, fine).
2. **Refresh §8E scorecard** — re-run `3rdJ_08_simulation_2split_val.py`; office scenario gates
   (§6.3/§7.2) now pass on REAL sim outputs not inputs; confirm no regressions.
3. **Finish Step 9** — edit `Step9_docs/3rdJ_09_activityDrivenLoads_2split.py`
   `build_scenario`/`build_longitudinal`: office rows from `agg_peak` (`peak_kW_annual`,
   `mean_peak_hour`) + `agg_diurnal` (`office_occ` mid-day) — user chose **ALL THREE metrics**;
   redraw `fig_scenario_both` office panel. Residential rows already correct. `sbatch run_step9.sh`,
   collect. Update doc §R3/R4 + §5 ledger + §8 caveats (drop "degenerate/pending" → real signal).
4. **Reframe the 2 pipeline docs** (archive predecessors first): the STEP-9 boxes in
   `3rdJ_00_2split_Occupancy_Pipeline_Overview.md` + `3rdJ_00_2split_Occupancy_Pipeline.md`
   "office-only" → "both channels".
5. Update `memory/project_step8_office_wfh_bug.md` + `project_step9_2split_status.md` + this RESUME to DONE.
6. **THEN paper reporting** (2J `readySubmission.md` = style ref).

---

### Background — why Step 9 is bi-channel (still valid)

**Context (why Step 9 was rebuilt today):** the user pushed back that residential and office must
get **equal importance / attention / evaluation** (equal ≠ identical parameters — each channel keeps
its own physics: resid = MC + SHEU + REPLACE; office = deterministic + NECB + MODULATE). The 3J
pipeline docs had scoped Step 9 as *office-only* (residential Step 9 = Leg-1 / 2J). We agreed to
build a **unified, bi-channel Step 9 at aggregate depth** (presence→Lights/Equipment coupling +
aggregate site-EUI calibration, each channel vs its own benchmark), because that's the depth where
parity is genuinely achievable (office has no per-end-use benchmark like SHEU → can't go
activity-resolved without becoming the hand-wavy channel; deep activity-resolved office = a Leg-3
candidate). No re-simulation — it reads the existing §8D agg tables.

**Built today (all in `Leg2_2-split/Step9_docs/`, uploaded to the cluster upload tree):**
- `3rdJ_09_activityDrivenLoads_2split.md` — the bi-channel method+results doc (has an explicit
  "equal-treatment ledger" table answering the parity ask).
- `3rdJ_09_activityDrivenLoads_2split.py` — analysis script: reads `Step8_docs/outputs_step8/agg/`
  (agg_annual/peak/diurnal/meta) → `outputs_step9/{step9_eui_by_channel,step9_loadshape_peaks,
  step9_scenario_response,step9_longitudinal}.csv` + `figures/fig_{eui,diurnal,peakhour,scenario}_both.png`
  + `step9_report.html`.
- `run_step9.sh` — SLURM (`-p ps`, `-t 7-00:00:00`, py_compile + dep fast-fail), log
  `logs/9_step9_<JOBID>.out`.

**Status: RAN + COLLECTED overnight (job 1055064 COMPLETED, exit 0, 41 s).** Outputs are LOCAL at
`Step9_docs/outputs_step9/` (4 CSVs + 4 figs + `step9_report.html`). The doc's §R1–R4 tables now hold
the REAL numbers. **Step 9 is ~80% done — one refinement pass remains before it's "DONE" and before
the pipeline-doc reframe.**

**What's solid (paper-ready):** both-channel EUI vs benchmark (resid SingleD 212.5 WARN=expected,
OtherDwelling 140.4 / MidRise 177.3 / HighRise 142.9 in-band; office 179.6 PASS); residential
scenario response (mid-day 0.252→0.273, energy +2.14% across WFH bands); residential COVID break;
office load-shape (mid-day hump 146 kW > night 57 kW, WE 48.5 < WD 146).

**🔴 THE ONE REFINEMENT TO DO FIRST (then Step 9 is done):** the office **scenario + longitudinal**
metrics are degenerate at the ANNUAL level — in `agg_annual` the office `occ_mean_persons` = 163.683
and annual energy ≈ 19,066 MWh are IDENTICAL across all 7 scenarios (that's the NECB design density +
an HVAC-dominated annual total, not the AT_WORK-modulated signal). The office WFH story is real but
lives in **peak / load shape** (§8E §6.3 already showed office 2030 WD peak 0.70→0.62→0.60). Also the
office **lights/equip end-use split** is absent from agg (residential-only). Both are documented in
the doc §8 caveats 4–5 + the §5 ledger (flagged, not hidden).

**Runbook to finish (small script edits + one 41 s re-run — NO re-simulation; hand mechanical bits to
a `model: sonnet` employee):**
1. **Decide the office scenario/longitudinal metric with the user** (paper-narrative call): feature
   office **peak kW** and/or **peak-hour** and/or **mid-day office_occ** across scenarios — since
   annual energy is ~flat (a legit finding: "WFH reshapes office peak/shape, not annual energy").
2. Edit `3rdJ_09_activityDrivenLoads_2split.py` `build_scenario`/`build_longitudinal` so the OFFICE
   rows come from `agg_peak` (`peak_kW_annual`, `mean_peak_hour`) and/or `agg_diurnal` (`office_occ`
   mid-day mean per scenario), not `agg_annual` energy. Re-draw `fig_scenario_both` office panel with
   the chosen metric. (Residential rows are correct — leave them.)
3. Archive predecessor `.py` → `Step9_docs/archive/`, re-upload the one file, `sbatch run_step9.sh`,
   collect (drain-watch or a Sonnet poll ≥30 min), scp `outputs_step9` local, confirm office scenario
   now shows a real signal.
4. Update the doc §R3/§R4 + ledger + caveats to reflect the fixed office metric; mark Step 9 DONE.
5. **THEN reframe the two pipeline docs** (archive predecessors to a sibling `archive/` first, per
   HARD RULE): `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline_Overview.md` (STEP 9 box, ~L112–117) +
   `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` (STEP 9, ~L223–226): "office-only" → "both
   channels: residential (SHEU) + office (NECB) activity-driven end-use loads + EUI calibration; deep
   activity-resolved residential = Leg-1 provenance, deep office = Leg-3 candidate." Keep the
   "Residential pipeline unchanged" spirit but make Step 9 explicitly bi-channel + equal-weight.
6. Update memory (`project_step9_2split_status.md`) + this RESUME.md to Step 9 DONE, then paper reporting.

**Then (the real next milestone): paper reporting.** Step 8/9 is the results backbone (load shapes,
peak-hour timing, 2015→2022 COVID break, 2030 WFH-band spread, both-channel EUI vs benchmark).
2J submission copy `readySubmission.md` is the style reference (memory `project_2j_paper_writing`).
