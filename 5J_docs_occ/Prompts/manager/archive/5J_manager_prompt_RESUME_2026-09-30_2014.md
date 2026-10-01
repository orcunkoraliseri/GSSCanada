# 5J manager prompt: RESUME the occupancy-aware surrogate paper (paste the whole file into a new session)

First written 2026-09-28 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6
and §7 change only when a rule or a design changes. Edit in place; never fork a copy.
Last updated: **2026-09-30 19:57 EDT: Step 4 verified except the freeze: scorer re-derived by the manager (two cells, own code, equal); effect-good stand-in passes every gate; the 10 %-noise stand-in passes the load band but fails the occupancy-effect gate on heating/cooling (kept as a result); planted faults all caught; perturbation table being filled by a fresh employee; freeze waits on the ASHRAE Guideline 14 page. Before (18:58): Step 3 CLOSED for Spain + Italy (verified, splits sealed); Step 4 employee RUNNING; ASHRAE G14 page needed from the author before the freeze. Before (18:33): arrays FINISHED (31/31 COMPLETED, 0 failed files); part 2 employee RUNNING (integrity, resume check, splits). Before (16:51): Spain + Italy campaign RUNNING on Speed (6 arrays, 30 CPUs, 9,269 runs; 1,158 done, 0 failed at 16:51); part 2 task written, launch when arrays finish. Before (16:39): Step 2 CLOSED for Spain + Italy (design FROZEN); Step 3 part 1 employee RUNNING (campaign tool, smoke, preflight, 6 arrays). Before (16:31): households DONE + verified; campaign design DONE + verified with one placement defect; fix employee RUNNING (START HERE item 0). Before (16:16): multi-zone re-pilot DONE + verified; O-3 RULED (P = 3, split-pure household pools, no cut); two Step 2 closure employees RUNNING on Speed (Italy households + averages; campaign design). Before (~16:02): builder DONE + verified (15:58); multi-zone re-pilot employee RUNNING on Speed (task `Step2_docs/impl/2026-09-30_wp1_mz_repilot_TASK.md`); lighting question sent to the author. Before: D2-8 multi-zone RULED and designed; builder employee RUNNING on
Speed; author ruled A (every flat tested), B (4 targets), and "all possible outputs". Campaign HELD until the
multi-zone re-pilot. Start at §5 item 0.** (Stamps 16:00-17:00 written earlier today were ahead of the clock;
corrected in the Progress Log.)

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
  🔴 **This includes scripts you or an employee launch:** a script that reads a pooled file and skips UK lines
  still opens it (FINDING 5J-1, 2026-09-29: the 4J corpus `4J_step3_corpus.jsonl` holds es/uk/it and the Step 9
  trigger reads all of it). 5J reads only Spain+Italy copies made by the author.
  🔴 **No repo-wide or folder-wide search, and no wildcard that could match a UK file** (FINDING 5J-2: an employee's
  stray grep over *.csv/*.json could reach about 1,800 UK-named 4J outputs). Every task doc names its files in
  full and repeats this line. Spain/Italy episode files (`episodes_spain.parquet`, `episodes_italy.parquet`) are
  not UK data and may be read by name.
  Check the time with `date` before writing a stamp (on 09-29 the manager wrote estimated stamps up to 1.5 h
  ahead; corrected).
  UK counts and checks are run by the author or by a batch job; how UK aggregate results reach you is
  open decision O-7. UK-derived outputs and weights are never released publicly (clause 4).
* 🔴 **ALL compute on Speed, NOTHING on the local CPU (author, 2026-09-30, four messages):** "use speed cluster
  resources", "do not use local cpu resources". Even light work (EPW conversion, checkers, report scripts) goes in
  an sbatch job (python `/speed-scratch/o_iseri/envs/step4/bin/python -u`). Locally: edit files, ssh/scp, ls, read
  small files only. The author's own python/EnergyPlus jobs run on the local box; never touch them. Every task doc
  says "Speed, sbatch", never "Local only" (older task docs carry an AMENDMENT section).
* **Speed:** `sbatch` only, `-t 7-00:00:00`, `--exclude=antenna1`, never python or `srun` on the login
  node. Login shell is tcsh: wrap ssh commands as `ssh ... "bash -c '...'"`. Ask CPUs slightly under the agreed share (O-5). Disk: scratch was 9.3 T of 10 T on 2026-09-25;
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

* 🔴 **Buildings are multi-zone (author, 2026-09-30, D2-8):** floors + thermal zones, at least one zone per dwelling
  per floor; never one zone per building. Check the builder before any building enters a pilot or campaign.

## §4. State now (rewrite after every step)

* **Step 0:** subject ruled (B4); O-1 licences closed (all three countries stay); O-2 novelty **closed
  2026-09-28** by the author on the Li 2021 abstract (full-text re-check and one logged P1/P4 search owed
  at Step 8). Open: O-3 campaign size (pilot), O-4 input window, O-5 CPU share with 1J, O-6 venue, O-7 UK
  aggregate results.
* **Step 1 (WP0 inventory): DONE 2026-09-28 night except the UK line** (author runs one line from the
  Step 1 spec, section A, and pastes the output into the impl doc). Inventory
  `Step1_docs/outputs_step1/wp0_inventory.md`; manager re-derivation and gates 1.3 and 3.1 in
  `Step1_docs/impl/2026-09-28_wp0_inventory.md`, "Verified (manager)".
* **Step 2: IN PROGRESS. Done and verified (details in the state files under `Step2_docs/impl/` and the Progress Log):**
  * **Climates (D2-1 RULED 09-29):** 9 EPWs, 3 per country (Madrid, Valencia, Seville 2010; London, Birmingham,
    Manchester 2014; Bologna, Turin, Milan 2014), all converted, checked and scored (`weather_score_5J.json`;
    Manchester RMSE 1.138, Milan 3.165). Download finished 78/78. climates.csv refreshed on Speed 09-30 (all 9 ok;
    checker 46/0/0); `tools/5thJ_design_tables.py` now takes `--data`/`--openubem` (prints `PATCH read_roots OK`).
  * **Wrapper `tools/5thJ_idf.py`** (single-zone, 8 printed patches; D2-2 20/26 °C, D2-7 People + appliances,
    fixed gain zeroed), act2 rule `prefix2_major`, corpus guard (Spain+Italy copy only), design tables (120
    buildings, es 60 + it 60 weighted households, 50-row pilot list), households v2: all DONE + verified 09-29.
  * **Pilot (single-zone) DONE 09-30:** 50/50 Madrid runs on Speed (arrays 1403962 + 1403963), report
    `outputs_step2/pilot_report.md` ACCEPTED as a measurement (checker 14/1/3/10/0; median 2 s). Found: 4.3 must
    count absent = presence 0 (then 38/38 pass); 4.2a cooling in winter = 3 h of solar gain, fine; electricity is a
    pass-through (same value on four buildings). O-5 = 30 CPUs.
  * 🔴 **D2-8 RULED (author, 09-30): floors + thermal zones, never one zone per building** (memory
    `feedback_multizone_per_building.md`). The 4J Step 8 box is the WHOLE building, so the single-zone pilot
    numbers do not carry over; the old O-3 ruling (22,160 runs) is VOID until the re-pilot. Builder study (3J +
    4J Step 10, code only): neither usable as is; design `Step2_docs/impl/2026-09-30_d2-8_multizone_design.md`:
    keep 4J `derive(row)`, n_Storey floors, k dwellings per floor (SFH/TH k=1, one zone per floor; MFH/AB from
    TABULA's dwelling count, else manager rules), paired floors and party walls, same glazing and total capacity,
    interior R 0.35/0.50 ASSUMED, collapse-mode carry-over gate.
  * **A RULED: every flat is tested** (each dwelling its own design household and its own training row; pairing by
    fixed neighbours dropped). **B RULED: four targets per dwelling** = heating, cooling, equipment electricity,
    total electricity (= equipment + heating/COP + cooling/COP, COP 3.0 ASSUMED, author may change).
    **Outputs: "all possible"** (author): per zone hourly loads (total/sensible/latent), equipment and lighting
    electricity, people/infiltration/window gains and losses, temperatures, humidity, unmet hours; end-use meters;
    annual tables. No Lights object is invented; if 4J has no lighting schedule, ask the author.
  * **DONE + verified 15:58: multi-zone builder employee** (task `Step2_docs/impl/2026-09-30_wp1_multizone_builder_TASK.md` incl.
    AMENDMENT on outputs; state `..._wp1_multizone_builder.md`; Speed folder `/speed-scratch/o_iseri/5J/multizone/`):
    Part A TABULA dwelling count, Part B `tools/5thJ_idf_mz.py`, Part C area gates + EnergyPlus runs + carry-over
    + seen failing + run seconds and disk per run.
  * **DONE + verified 16:14: multi-zone re-pilot** (36 Madrid runs, every flat its own household; state
    `..._wp1_mz_repilot.md` "Verified (manager)"): all clean, checker 10/0/0/0 exit 0, four planted defects caught,
    replicates identical, 4-25 s per run; mass fix + k from TABULA in the builder. Manager's own Speed job (1404122)
    matched one flat's heating/cooling/equipment to its zone columns. Madrid cooling per m2 high: noted, check later.
  * **O-3 RULED 16:16 (manager, Progress Log):** SFH/TH all 60 households per building; MFH/AB every flat tested,
    P = 3, each run filled from ONE household pool (dev/val/test) so households never cross splits; same placement
    in a country's 3 climates; B0 = one average-household run per building and climate; 10 inputs x 10 replicates
    per country. About 14,200 runs for 9 climates, under 1 hour at 30 CPUs, about 22 GB; no cut.
  * **Step 2 CLOSED for Spain + Italy (16:38).** Households DONE + verified 16:28 (inputs in
    `/speed-scratch/o_iseri/5J/households/inputs/`, incl. `es_avg`, `it_avg`); campaign design DONE + verified, the
    distinct-flat defect FIXED + verified 16:37 (manager job 1404143: 0 below the bar). FROZEN design
    `Step2_docs/outputs_step2/campaign_design.md` md5 2594867b0fe6cf24191c00e0c83d91a7: Spain 4,768 + Italy 4,501 runs,
    about 18 CPU-hours; table/split md5s in the Progress Log 16:38. UK households wait on the author.
* **Step 3 CLOSED for Spain + Italy (18:56).** 9,269 runs (16:49-18:33, 0 failed); integrity 12 checks PASS, 4
  planted defects caught; resume check done; replicates identical; 12 split lists sealed read-only (md5s in the
  checklist Step 3 box and `Step3_docs/impl/2026-09-30_wp2_campaign_part2.md`); loader refuses test lists until
  `gates_frozen.md5` exists. Manager job 1404279 re-derived md5, annual numbers, split counts, refusal. 15.4 GB.
  INFO: one EnergyPlus wet-bulb warning per Madrid/Turin run (weather rows plausible): limitation, no rerun.
* **Step 4 VERIFIED except the freeze (19:57).** Scorer `tools/speed/5thJ_04_scorer.py` (md5 16d828f5...), definitions
  `Step4_docs/outputs_step4/gates_frozen.md` (md5 9134ae2a... in job 1404397; ASHRAE band still marked PENDING). Validation
  pairs Spain + Italy 33,474. Manager re-derived with own code (jobs 1404325, 1404408): Italy AB and Spain MFH R², sign,
  pair counts equal to the scorer; 14 scorer open logs, 0 locked runs. Effect-good stand-in: 112 PASS, 0 FAIL (val 2.0).
  The 10 %-noise "ASHRAE-good" stand-in passes the load band 32/32 but fails the occupancy-effect gate on 15 of 16
  heating/cooling cells: kept as a RESULT (paper premise), no gate relaxed; risk for Step 5 written in the Progress Log.
  Every planted fault caught (deleted run, training mean, building mean, 2 h shift, control, planted high floor -> 32
  NOT_EVALUABLE exit 2, planted crash -> exit 1); null 99.98 % of 6,400. Perturbation table: docs-only employee
  (task `Step4_docs/impl/2026-09-30_freeze_fix1b_TASK.md`). 🔴 Freeze waits on the author's ASHRAE Guideline 14 page.
* 🔴 **FINDING 5J-1** (09-29, trigger read the pooled 4J corpus; FIXED: copy + guard) and **FINDING 5J-2** (09-29,
  stray repo-wide grep; rule in §3). Reporting either to UKDS is the author's call; told once, nothing drafted.
* **Steps 5 to 8:** specs and validation plans written 2026-09-28; nothing run.
* **Board:** v25 = this update (09-30 19:57 EDT). Live page is the master: read + diff before any republish.

## §5. Do this next (rewrite after every step)

0. **START HERE (2026-09-30 19:57 EDT).** Step 4 is verified except the freeze (state `Step4_docs/impl/2026-09-30_freeze.md`,
   `..._freeze_fix1.md`). If the docs-only employee (fix 1b) has not reported: read `outputs_step4/perturbations.md`; if
   it is still a skeleton, spawn a fresh employee from `impl/2026-09-30_freeze_fix1b_TASK.md`. Then wait for the author's
   ASHRAE Guideline 14 page; with it: write the page into `gates_frozen.md` (remove the PENDING marker), rerun the
   misc2 job (gate 1.1 must PASS), md5 of `gates_frozen.md` + scorer into `/speed-scratch/o_iseri/5J/gates_frozen.md5`
   and the checklist Step 4 box (inside a Speed job), show the test reader opens after the freeze (val 4.2).
   Lighting: still asked (not blocking).
1. Step 5 (baselines and surrogate, GPU): write its task only after the freeze. O-4 input window is DRAFT (7 days
   in, 24 h out, per flat): rule it before Step 5. UK arrays wait on the author's UK household script
   (`tools/5thJ_design_households_uk.py`) and the UKDS 5J line.
2. After every step: Progress Log entry, this §4/§5, memory line, board (read + diff live page, syntax check,
   republish). Run `date` before every stamp. The previous version of this file is in
   `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-09-30_1957.md` (older §5 items, for the record).
## §6. Lessons carried (full list in the checklist, 16 items)

Clock origin (4J diaries start 04:00, Spain 06:00: rotate to midnight); same input can give different
EnergyPlus output (noise floor from replicates); heating effect tiny (expect the claim in electricity and
peaks); only geometry-ordered effects survived (score per dwelling class); right level per statistic;
exit 0 is not proof; cache keys on every input; one working directory per run; right meters; preflight
with pinned inputs; `--exclude=antenna1`; weather moves more than occupancy; laundry lives in secondary
activity; leakage from country-only fields; bootstrap by building and household; gates seen failing.

## §7. Open decisions (one line each; the full text is in the Overview)

O-3 campaign size RULED 09-30 16:16 + design FROZEN 16:38 (Spain 4,768 + Italy 4,501 runs) · O-4 input window (DRAFT 7 days in, 24 h
out; per dwelling now) · O-5 CPU share RULED 09-30: 30 CPUs · O-6 venue (after RQ1 and RQ2) · O-7 how UK aggregate
gate results reach the manager (recommend: the author asks UKDS for written permission) · k dwellings per floor
for MFH/AB (TABULA count, else manager) · COP 3.0 ASSUMED (author may change) · lighting schedule (ask if absent).
