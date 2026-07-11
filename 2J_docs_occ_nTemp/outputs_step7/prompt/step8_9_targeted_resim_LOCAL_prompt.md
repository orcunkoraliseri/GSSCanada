# 2J — Targeted **LOCAL** re-simulation of Step-8 + Step-9 (2022 & 2030 only) — new-session execution prompt

> Paste into a fresh session. Speed cluster is busy ~2 weeks → **run everything LOCALLY**, no waiting.
> Written 2026-07-10 by the director session, after two read-only investigations pinned the exact recipe + gotchas.

---

## ROLE & ENVIRONMENT
You are the **executor** for a LOCAL EnergyPlus re-simulation of the 2J pipeline. Local Windows box: use the
**`py`** launcher (NOT `python`). EnergyPlus is installed at **`C:\EnergyPlusV24-2-0\energyplus.exe`**
(auto-detected by `eSim_bem_utils_2J/config.py:8-14`). **Speed-cluster login-node rules do NOT apply to local
runs.** These are 600 MB+ CSVs and thousands of E+ runs → **never load a whole schedule CSV into your chat
context** (delegate any scan/count to a small script that prints only the tiny result); run E+ in **background,
batched by cell**; use the parallel workers + memory watchdog already in `run_campaign_local.py`. Working root:
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`.

## WHY (context)
The 2026-07-09 Steps 4–7 refresh **materially changed the 2022/2030 BEM schedules** — not just −42 HH:
**1.2 % gross ID churn** (909 out / 867 in via the region-tier relink) **and act30 is now joint-raked**
(previously un-raked). The existing EnergyPlus campaigns — **Step-8** (Jun-8, cluster job 953111, 24 PASS) and
**Step-9** (Jun-10, 48 PASS) — ran on the **OLD** schedules and are stale for 2022/2030. **Historical years
2005/2010/2015 stay as-is** (targeted scope, user-approved). Frame is now **144,465 HH** (2022==2030 IDs);
2005/2010/2015 still carry 144,507.

Refreshed schedule files (at `GSSCanada-main\BEM_Setup\`, Jul-9): `BEM_Schedules_{2022,2030}.csv` (17-col
"activity") + `BEM_Schedules_{2022,2030}_baseline.csv` (13-col "baseline").

---

## TASK 0 — (cheap, do FIRST) correct the now-STALE "act30 un-calibrated" statements
**Verified fact:** act30 IS now **joint-raked / calibrated** (`05_postlink_rake.py --joint`, added 2026-07-09;
downstream aggregate→bem→exclusion rebuild produced the 285,367-row `_excl` file; live per-stratum act30 gaps
0.59–1.17 pp vs ~12.3 pp pre-rake). So Metabolic_Rate **and** the Step-9 Equipment/Lighting fractions in the
current 2022/2030 BEM are **calibrated**, not raw. Fix these stale statements, then regenerate:
- `2J_docs_occ_nTemp/07_bemIntegrationGSS.md:47` ("Activity calibration | act30 **un-raked**") and **:226**
  (Risk Register "Metabolic channel un-calibrated — act30 was never raked") → reword to joint-raked/calibrated.
- `2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py` §4.4 (~L439-441: "(act30 un-calibrated)", "informational
  (un-raked)") **and** the deviations panel (~L792-796, L823-826) → reword to "act30 joint-raked (calibrated)".
- Archive the validator predecessor, then regenerate both Step-7 reports: `py 07_bemIntegrationGSS_val.py`
  (→ `outputs_step7/step7_validation_report_{2022,2030}_v2.html`). Confirm §4.4/deviations now read "calibrated".
- Update memory `project_2j_step7_improvements.md` (the "un-calibrated by design" line is wrong).

## TASK 1 — Step-8 local re-sim (2022 + 2030)
Driver: `Step8_docs/run_paired_mc.py` → `eSim_bem_utils_2J/main.py:run_step8_paired_mc` (one process = one
archetype×city cell). **`--years 2022,2030` is supported** (`run_paired_mc.py:42-43,60`). Cells = 4 archetypes ×
6 cities (`STEP8_ARCHETYPES`/`STEP8_CITIES`, `main.py:81-97`). Count = **24 × 50 × 2 = 2,400 E+ runs**. Outputs →
`BEM_Setup\SimResults_Step8\campaign_N50\<arch>__<city>\sample_XXX_HHnnnn\{2022,2030}\`.

**⚠️ PAIRED-SAMPLING GOTCHA (decide before running).** Restricting `--years 2022,2030` builds the HH pool from
the **2022∩2030** intersection (144,465) — a different/larger/differently-ordered set than the original 5-year
(144,507) intersection — so `rng.sample()` (main.py:2039, seed keyed on cell only) draws a **different 50 HH per
cell** than the existing `sample_XXX/{2005,2010,2015}` dirs → **breaks the paired within-household Δ** against the
retained historical years. Two ways forward — pick with the user:
- **P1 (pragmatic, recommended for "targeted"):** fresh `--n 50 --years 2022,2030` sampling; treat **2022-vs-2030
  as internally paired** (this IS the paper's forward-looking WFH/2030 delta). Historical years become non-paired
  trend context. No code change.
- **P2 (rigorous):** re-sim the **same 50 HH per cell** as the existing campaign (each cell has
  `cell_manifest.csv` with the original `sim_hh_id`s) so new 2022/2030 drop-in-replace and stay paired with the
  retained 2005/2010/2015. Requires **adding a fixed-HH-list mode** to `run_paired_mc.py` (not currently
  supported — only fresh `--n/--seed`) + handling the ~0.6 % of manifest HH now absent from the 144,465 frame
  (drop or substitute). More work; needed only if the paper pairs 2022/2030 against 2005-2015.

**Local invocation.** `run_campaign_local.py` (parallel, cores-2 workers, mem watchdog) has **no `--years`
flag** (argparse L143-163). Either (a) add a `--years` pass-through to it, or (b) loop `run_paired_mc.py` over the
24 cells:
```
py Step8_docs/run_paired_mc.py --archetype <ARCH> --city <CITY> --n 50 --seed 42 --sim-mode standard --years 2022,2030
```
Run in background, batch by cells, watch memory. (Cluster fallback if it frees up: `step8_array_v2.sh` +
`--years 2022,2030` added and `EXPECTED=100` instead of 250 — but we're going local.)

## TASK 2 — Step-9 local re-sim (FULL, 2022 + 2030)
Step 9 (activity-driven internal gains, baseline vs activity arms) is **already 2022/2030-only** — the entire
existing **4,800-run** dataset (24 cells × 50 × 2 yr × 2 arms) is stale → **full local re-run**.
**⚠️ No local Step-9 driver exists** (cluster used `Step9_docs/step9_cluster/step9_idf_gen_full.py` +
Singularity). Build a thin local wrapper reusing the `eSim_bem_utils_2J` engine via `run_paired_mc.py --sched-dir`
pointed **twice**: once at the 17-col **activity** files (`BEM_Schedules_{2022,2030}.csv`) and once at the 13-col
**baseline** (`BEM_Schedules_{2022,2030}_baseline.csv`). Produce the output artefacts the Step-9 validators expect
(`cluster_run_results.csv`, `peak_shift_summary.csv`, `loadshape_profiles.csv`, `peak_hours.csv`). Investigate the
step9 scripts first to match their expected layout.

## TASK 3 — re-aggregate + re-validate
- **Step-8:** `py Step8_docs/08_simulation_plots.py --rebuild-agg --figs all` (hardcodes 5 years L68 — correctly
  mixes the refreshed 2022/2030 cells with the untouched historical dirs), then `py 08_simulation_val.py`
  (derives years dynamically L1166; `HISTORIC_YEARS` vs `PROVENANCE_YEARS` gate logic already present — no year
  edits needed).
- **Step-9:** `step9_cluster/step9_validate_full.py`, `step9_loadshape_aggregate.py`, `09_activityDrivenLoads_val.py`
  (all 2022/2030-aware; no year edits).

## TASK 4 — propagate the frame + un-stale downstream docs (**after** the sims land)
Only once the re-simmed numbers are in (so the paper's frame matches its results), sweep **144,507 → 144,465**
across: `08_simulation.md`, `09_activityDrivenLoads.md`, the `00_*` overview docs, the now-false comment
`eSim_bem_utils_2J/main.py:66-72` ("share the SAME 144,507 SIM_HH_IDs"), and the manuscript under `writing/`
(incl. the explicit "Number hygiene: 144,507 households" line in `2nd_Occ_Journal_Skeleton.md:358`).

---

## HOUSE RULES
Local `py` launcher; **never** load 600 MB CSVs into chat context (script → small output); archive predecessors
before overwriting; smallest practical change; **call out any publishable-results change**; re-derive numbers
from artefacts (don't transcribe logged before/after); local E+ runs are exempt from Speed login-node rules.

## KEY FILES
- Step-8: `Step8_docs/run_paired_mc.py`, `eSim_bem_utils_2J/main.py`, `Step8_docs/run_campaign_local.py`,
  `Step8_docs/08_simulation_plots.py`, `08_simulation_val.py`, per-cell `cell_manifest.csv`
- Step-9: `Step9_docs/step9_cluster/step9_idf_gen_full.py`, `step9_validate_full.py`, `09_activityDrivenLoads_val.py`
- Schedules: `GSSCanada-main/BEM_Setup/BEM_Schedules_{2022,2030}.csv` (+ `_baseline.csv`)
- act30 rake: `05_postlink_rake.py` (`--joint`)
- Prior handoff (Step-7 close-out): `outputs_step7/prompt/step7_handoff_prompt.md`
