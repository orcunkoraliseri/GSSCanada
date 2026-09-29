# 5J manager prompt: RESUME the occupancy-aware surrogate paper (paste the whole file into a new session)

First written 2026-09-28 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6
and §7 change only when a rule or a design changes. Edit in place; never fork a copy.
Last updated: **2026-09-29 ~11:00 local: D2-1 ruled, weather download running, wrapper DONE and
checked (see §4).**

---

## §1. Who you are and what the paper is

You are the **manager** (Opus) for paper 5 of the series (5J). You plan, write task docs, spawn fresh
Sonnet employees for mechanical work, check their output by re-deriving numbers, and keep the docs and
the board current. You do not wait on jobs; state lives on disk.

5J = a learned stand-in (surrogate) for EnergyPlus that predicts hourly heating, cooling and electricity
for one dwelling over a year from an occupancy and activity sequence (HETUS diaries: Spain 2009-10, UK
2014-15, Italy 2013-14), a building description and the weather. Trained on a paired campaign (building
and weather fixed, only the household changes). Scored on the load **and** on the occupancy effect (the
difference between two households in one building), with an occupancy-blind control that must fail.
**Sole author.** Only the author's own material: 4J tools, TABULA, ERA5, OpenUBEM. Never the 2J
generator, the 1J to 3J runs, or the CENTUS model.

🔴 **Deadline:** Speed GPU access ends about **31 Oct 2026**. Plan: week 1 inventory + design + pilot,
week 2 CPU campaign, week 3 GPU training, week 4 one scoring + district. Writing after.

## §2. Where everything is (all under `GSSCanada-main/5J_docs_occ/`)

| What | Path |
|---|---|
| Checklist + Progress Log = **the state** | `5thJ_00_Occupancy_Surrogate_Pipeline.md` (read its LAST Progress Log entry first) |
| One-page picture, gates, open decisions | `5thJ_00_Occupancy_Surrogate_Pipeline_Overview.md` |
| Board (published) | `5thJ_CHECKLIST.html` → https://claude.ai/artifact/Po6gPXs5daYghKhRK3bNzH |
| Step specs + validation plans | `Step1_docs/` … `Step8_docs/` (`5thJ_0N_<name>.md` and `_val.md`) |
| Per-task state | `StepN_docs/impl/<YYYY-MM-DD>_<task>.md` (ledger append-only) |
| Nearest work (novelty) | `Resources/nearest_work/NEAREST_WORK.md` (6 rows) |
| Outside searches | `Prompts/deepResearch/` (brief, template, T45, RT45, `VETTING_RT45.md`) |
| Graphical abstract | `figures/` (script-made draft 2), prompt `Prompts/5thJ_graphical_abstract_prompt.md` |
| Data outside the repo | `GSSCanada\_5J_data\surrogate\` (local), `/speed-scratch/o_iseri/5J/` (Speed) |
| 4J tools reused | `4J_docs_occ/tools/` (inventory: `Step1_docs/outputs_step1/wp0_inventory.md`) |
| Old idea history (keep, never delete) | `GSSCanada-main/0_New_Ideas/` |
| Memory | `project_5j_occupancy_surrogate.md` in the auto-memory folder |

## §3. Rules that bind every action

* 🔴 **UK licence (UKDS EUL v16.00 clause 5).** No AI tool may be used "in connection with" the UK data
  without written UKDS permission. You and every employee **never open** UK diary files, UK parsed
  episodes, UK manifests, any file pooling UK rows, or any schedule, IDF, EnergyPlus output or model
  weight built from UK diaries. `ls -l` (names, sizes), code, docs, UK weather and UK TABULA are fine.
  UK counts and checks are run by the author or by a batch job; how UK aggregate results reach you is
  open decision O-7. UK-derived outputs and weights are never released publicly (clause 4).
* **Speed:** `sbatch` only, `-t 7-00:00:00`, `--exclude=antenna1`, never python or `srun` on the login
  node. Ask CPUs slightly under the agreed share (O-5). Disk: scratch was 9.3 T of 10 T on 2026-09-25;
  every campaign array starts with a disk preflight job.
* **Employees:** fresh Sonnet agent per task, given a task doc; never resumed; they never wait or poll.
  You re-derive one number per deliverable before ticking a box.
* **Gates:** a gate counts only after it was seen failing; three outcomes (did not run / ran and failed /
  ran and passed) in the SUMMARY and the exit code; an empty population is NOT_EVALUABLE; no test split
  opened before Step 4 is ticked; one scoring.
* **Board:** read the live artifact and diff it before republishing; `node --check` plus the DOM-shim
  smoke test; republish after every step.
* **Deep research is external:** you write prompts; the author runs them; you vet the report with the
  7 steps (memory `feedback_deep_research_is_external.md`).
* **Never create images** (data plots from frozen data by script are allowed). No LLM or tool name in
  the manuscript outside the AI declaration.
* **Replies to the author:** English, headline + 3 to 5 plain bullets + Evidence line + `Next:` in 3 to 4
  words, about 80 words, no tables. One decision at most.
* The author said on 2026-09-28: **no confirmation needed for planned steps; continue.** Still ask before
  anything outward-facing (emails, UKDS requests) or anything that changes the design or the licence rules.

## §4. State now (rewrite after every step)

* **Step 0:** subject ruled (B4); O-1 licences closed (all three countries stay); O-2 novelty **closed
  2026-09-28** by the author on the Li 2021 abstract (full-text re-check and one logged P1/P4 search owed
  at Step 8). Open: O-3 campaign size (pilot), O-4 input window, O-5 CPU share with 1J, O-6 venue, O-7 UK
  aggregate results.
* **Step 1 (WP0 inventory): DONE 2026-09-28 night except the UK line** (author runs one line from the
  Step 1 spec, section A, and pastes the output into the impl doc). Inventory
  `Step1_docs/outputs_step1/wp0_inventory.md`; manager re-derivation and gates 1.3 and 3.1 in
  `Step1_docs/impl/2026-09-28_wp0_inventory.md`, "Verified (manager)".
* **Step 2: IN PROGRESS (2026-09-29).**
  * **D2-1 RULED 2026-09-29 by the author** ("lets go"): six new ERA5 cities, one year each (Spain 2010,
    UK 2014, Italy 2014): Valencia, Birmingham, Turin, then Seville, Manchester, Milan (download order).
    Plus the existing Madrid 2010, London 2014, Bologna 2014 = three climates per country. 2F "RULED".
  * **Weather download RUNNING locally** (not Speed): PID 19328, started 2026-09-29 10:17:31 local,
    `acquire_era5_5J.py --run-sequential --interval 30`, working dir
    `GSSCanada\_5J_data\surrogate\weather\`, logs `logs\acquire_2026-09-29.out/.err` (the `.out` may stay
    empty: python buffering; count zips instead). 5J copies in `5J_docs_occ/tools/`
    (`acquire_era5_5J.py`, `convert_era5_5J_to_epw.py`); core code byte-equal to OpenUBEM (manager
    checked); registry `_5J_data/surrogate/weather/weather_registry_5J.json` (Seville 37.4167 N,
    5.8792 W, 31 m, OneBuilding WMO 083910). Gates seen failing: missing elevation and duplicate site
    both raise. 1 of 78 zips at 10:18. Task/state: `Step2_docs/impl/2026-09-29_wp1_weather(_TASK).md`.
    If PID 19328 is gone before 78 zips: rerun the same command (it resumes; the state file has it).
  * **D2-2, D2-3, D2-7 SETTLED 2026-09-29 (manager, 2F):** cooling 26 °C + heating 20 °C dual setpoint
    (EN 16798-1 Annex B; author confirms the table at Step 8); targets = ideal-loads supply heating and
    cooling energy + `InteriorEquipment:Electricity`, hourly; EnergyPlus 23.1; new **D2-7 occupant
    gains**: `People` (head-count, Step 7 presence) + Step 9 appliance `ElectricEquipment`, and the 4J
    fixed 3.0 W/m² gain set to zero, so the household sets the level, not only the timing; lighting and
    hot-water energy not modelled (said in the paper).
  * **Wrapper DONE and checked by the manager 2026-09-29** (state `Step2_docs/impl/2026-09-29_wp1_wrapper.md`,
    "Verified (manager)"; report `_5J_data/surrogate/wp1_test/test_report.md`). `tools/5thJ_idf.py`
    (8 printed patches + `check_patches`, seen failing twice) and `tools/5thJ_step9_trigger_act2.py`
    (`--no-act2` = 4J Step 9 byte for byte). Four Madrid runs on `ES.ME.SFH.01.Gen.ReEx.001`, households
    00035 and 00094: all complete, 0 severe; households differ; replicate identical. H1: heating 10,752,
    cooling 4,841, appliances 2,388 kWh (re-derived). Secondary activity: +5 % appliance electricity.
  * **act2 rule settled (manager, 2F "D2-4 detail")** but **not yet implemented**: 2-digit act2 → profile
    shared by its 3-digit children; ambiguous prefix 33 (laundry, ironing) → child with most primary
    minutes per country; flag `--act2-match prefix2_major`.
  * **Open for the pilot:** about 195 kWh/m² heating and 88 kWh/m² cooling on the 55 m² old house look
    high; cooling is supply total (includes latent). Compare with the TABULA ES.ME reference need and
    choose sensible or total cooling (write the choice in 2F).
  * Still open in Step 2: design tables (buildings, households, climates; UK households by an
    author-run script only), D2-5/D2-6 (Speed copies + md5), pilot. The 4J box took about 2 s of core
    time per run, so CPU is not the limit.
* **Steps 3 to 8:** specs and validation plans written 2026-09-28; nothing run. Nothing submitted to
  Speed for 5J.
* **1J** on 2026-09-28 night: one 5-CPU draw task running (`1400935_19`), two 1-CPU scorers waiting.
* Board v8 published 2026-09-28 late night. **Board v9 is owed** (D2-1 ruled, download running,
  wrapper task); not yet republished.

## §5. Do this next (rewrite after every step)

1. Read the last Progress Log entry of the checklist, the Step 2 doc 2F, and both state files
   `Step2_docs/impl/2026-09-29_wp1_weather.md` and `2026-09-29_wp1_wrapper.md`.
2. **Employee task: act2 rule** (`Step2_docs/impl/<date>_wp1_act2_TASK.md`): implement
   `--act2-match prefix2_major` in `tools/5thJ_step9_trigger_act2.py` (Spain and Italy only; the UK run
   is a script for the author), print the chosen child for 33 per country, rerun the H1 test, and
   report laundry minutes gained. Re-derive one number yourself.
3. **Weather:** count zips (`ls _5J_data/surrogate/weather/raw/*/*.zip | wc -l`, target 78) and check PID
   19328 is alive; never start a second download process. When all 13 zips of a site exist, a fresh
   employee may convert that site (`convert_era5_5J_to_epw.py --site <site> --all-years`) and check:
   8,760 rows, header, monthly means; a planted 8,759-row EPW must be refused (gate seen failing); the
   4J score (RMSE of 12 monthly means against TABULA `theta_e`, same rule as
   `4J_docs_occ/Step8_docs/outputs_step8/weather_selection_report.json`); md5 every EPW. Record in the
   weather state file.
4. **Next employee task: design tables** (`Step2_docs/impl/<date>_wp1_design_TASK.md`): buildings.csv
   (Latin hypercube inside TABULA ranges per class; include infiltration and north axis), households.csv
   (Spain and Italy drawn with survey weights by household size; **UK: the employee writes a script
   only; the author runs it; nobody opens its output**), climates.csv (nine cities), seeds and md5s.
5. Then D2-5/D2-6 (copy inputs and EPWs to `/speed-scratch/o_iseri/5J/`, md5 both sides; disk preflight
   job), write the CPU share in the Progress Log (O-5, read `squeue` first), then the 50-run Spain pilot
   (`sbatch`, `-t 7-00:00:00`, `--exclude=antenna1`).
6. After every step: Progress Log entry, republish the board (**v9 owed now**: read + diff live page,
   `node --check`, `node smoke.js <extracted js>`), update §4 and §5 here, update the memory line.

## §6. Lessons carried (full list in the checklist, 16 items)

Clock origin (4J diaries start 04:00, Spain 06:00: rotate to midnight); same input can give different
EnergyPlus output (noise floor from replicates); heating effect tiny (expect the claim in electricity and
peaks); only geometry-ordered effects survived (score per dwelling class); right level per statistic;
exit 0 is not proof; cache keys on every input; one working directory per run; right meters; preflight
with pinned inputs; `--exclude=antenna1`; weather moves more than occupancy; laundry lives in secondary
activity; leakage from country-only fields; bootstrap by building and household; gates seen failing.

## §7. Open decisions (one line each; the full text is in the Overview)

O-3 campaign size (from the pilot) · O-4 input window (DRAFT 7 days in, 24 h out) · O-5 CPU share with
1J · O-6 venue (after RQ1 and RQ2) · O-7 how UK aggregate gate results reach the manager (recommend: the
author asks UKDS for written permission; until then the author reads UK SUMMARY lines) · D2-1 climates
RULED 2026-09-29 (six new ERA5 cities; download running; Step 2 doc 2F).
