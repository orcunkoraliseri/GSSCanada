# 5J manager prompt: RESUME the occupancy-aware surrogate paper (paste the whole file into a new session)

First written 2026-09-28 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6
and §7 change only when a rule or a design changes. Edit in place; never fork a copy.
Last updated: **2026-10-01 04:17 EDT: Step 6 CLOSED (one scoring done + re-derived; occupancy effect right in 31/32, 31/32, 26/28 test cells, load accuracy 21/14/14 of 32, control never passes, claims hold 11/12; seed and new-country limits); next Step 7 design. Before (02:53): Step 5 CLOSED (C fails 32/32 = G5J.4 PASS; seed spread 30/22/13 -> seeds 2-3 also reported on test); Step 6 B0 reported analyses locked (v2), scorer test mode locked, test predictions RUNNING. Before (01:01): Step 5 winner S3 pinned + verified (validation: household effect right in 30/32 groups, load accuracy 19/32); B1 verified; AMENDMENT 3 (B1 clipped at 0; winner unchanged under it); part E (control, seeds, one-country) RUNNING. Before (23:24): grid re-run DONE (16/16; best validation loss 0.110; S0 went 0.465 -> 0.159 with the clip); part D winner chain RUNNING (shortlist S2 S3 S1 S11 S9 S13 = manager list); B1 predicting validation; Step 6 claim rule written before any test result (6D); household days come from one shared generated pool (stated limit, not a leak). Before (21:24): S validation gap explained = network extrapolation on one new building with impossible static inputs (es_B40, TABULA V_C 20 m per m2, z 47); no window bug (own check exact); rules AMENDMENT 2 sealed 21:19 (static z clipped to development range; B1 unchanged); old grid VOID; fix employee DONE, smoke 1404630 all PASS, manager re-derived the clip (equal); grid re-run RUNNING (array 1404631, %4); B1 still tuning; stale "three country-out folds" text fixed in Step 5/6 docs. Before (20:49): slow GPU training fixed (cudnn deterministic off; probe job); new smoke PASS; 16-config grid RUNNING (array 1404570, each config <1 GPU-h); first two configs stop at epoch 1 with validation loss ~10x B1 -> manager diagnostic job 1404577 RUNNING (bug vs real gap); B1 still training; Step 6 part B task written; 3J/4J setup review written (`Prompts/manager/2026-09-30_setup_check_3J_4J.md`). Before (20:21): Step 5 part A DONE + verified (feature store); rules AMENDMENT 1 (val 1.3 checked per validation block; B0 from b0_dev on development buildings); parts B (B1 trees) and C (TCN + Transformer smoke + grid) employees RUNNING; parts D and E task docs written. Before (20:10): Step 4 CLOSED, gates FROZEN 20:04 (ASHRAE page found by the manager under the author's go-ahead: Guideline 14-2002 cl. 5.3.2.4 f, p. 18); Step 5 rules written before training (O-4 ruled); Step 5 part A employee RUNNING (feature store + B0). Before (19:57): Step 4 verified except the freeze: scorer re-derived by the manager (two cells, own code, equal); effect-good stand-in passes every gate; the 10 %-noise stand-in passes the load band but fails the occupancy-effect gate on heating/cooling (kept as a result); planted faults all caught; perturbation table being filled by a fresh employee; freeze waits on the ASHRAE Guideline 14 page. Before (18:58): Step 3 CLOSED for Spain + Italy (verified, splits sealed); Step 4 employee RUNNING; ASHRAE G14 page needed from the author before the freeze. Before (18:33): arrays FINISHED (31/31 COMPLETED, 0 failed files); part 2 employee RUNNING (integrity, resume check, splits). Before (16:51): Spain + Italy campaign RUNNING on Speed (6 arrays, 30 CPUs, 9,269 runs; 1,158 done, 0 failed at 16:51); part 2 task written, launch when arrays finish. Before (16:39): Step 2 CLOSED for Spain + Italy (design FROZEN); Step 3 part 1 employee RUNNING (campaign tool, smoke, preflight, 6 arrays). Before (16:31): households DONE + verified; campaign design DONE + verified with one placement defect; fix employee RUNNING (START HERE item 0). Before (16:16): multi-zone re-pilot DONE + verified; O-3 RULED (P = 3, split-pure household pools, no cut); two Step 2 closure employees RUNNING on Speed (Italy households + averages; campaign design). Before (~16:02): builder DONE + verified (15:58); multi-zone re-pilot employee RUNNING on Speed (task `Step2_docs/impl/2026-09-30_wp1_mz_repilot_TASK.md`); lighting question sent to the author. Before: D2-8 multi-zone RULED and designed; builder employee RUNNING on
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
* **🟢 Step 4 CLOSED, gates FROZEN (20:04, job 1404499).** ASHRAE source found by the manager under the author's go-ahead (Guideline
  14-2002 clause 5.3.2.4 f, p. 18, read verbatim; author to confirm the 2014 edition). Lock `/speed-scratch/o_iseri/5J/gates_frozen.md5`
  (gates_frozen.md 5a0dae85..., scorer 84d1dafa..., split_loader 9aad66d5...); gate 1.1 PASS (was FAIL), 1.2 PASS; test lists refused
  before and open after (val 4.2). Scorer still refuses test runs (Step 6 adds a test mode). Step 4 results: effect-good stand-in 112
  PASS / 0 FAIL; the 10 %-noise stand-in passes the load band 32/32 but fails the occupancy-effect gate on 15/16 heating/cooling cells
  (a RESULT, paper premise); every planted fault caught; null 99.98 %. Table `Step4_docs/outputs_step4/perturbations.md`.
* 🔴 **FINDING 5J-1** (09-29, trigger read the pooled 4J corpus; FIXED: copy + guard) and **FINDING 5J-2** (09-29,
  stray repo-wide grep; rule in §3). Reporting either to UKDS is the author's call; told once, nothing drafted.
* **Step 5 STARTED (20:08).** Rules written BEFORE training: `Step5_docs/outputs_step5/step5_rules.md` (md5 by job 1404502 into
  `/speed-scratch/o_iseri/5J/train/step5_rules.md5`): O-4 RULED (inputs = what EnergyPlus gets: presence, appliance, members, design
  level, neighbour flats above/below/same floor, weather, calendar, static building vector; no activity shares; 168 h + 24 h window);
  total electricity computed (COP 3.0), not learned; B1 = sklearn boosted trees (no lightgbm on Speed); S = TCN + Transformer, 8
  configs each on A100 20 GB slices; winner by the frozen scorer (most G5J.3 PASS cells); never a loco list (holds test runs).
  Part A DONE + VERIFIED 20:19 (store `/speed-scratch/o_iseri/5J/train/store/`: dev 15,096 flat rows, val 7,617, val pairs 33,474;
  manager own-code job 1404522: 3 rows equal raw files). Rules AMENDMENT 1 (20:18, before any result; `train/step5_rules_amend1.md`):
  val 1.3 per validation block (the frozen list holds development households on NEW buildings by design: es 396 / it 297 runs);
  B0 from `b0_dev` for development buildings. B0 + score RUNNING (1404520/1404521). Part B (B1) and part C (S smoke + grid)
  employees RUNNING (state `Step5_docs/impl/2026-09-30_wp3_b1.md`, `..._wp3_s.md`).
* **Step 5 at 21:24 EDT.** Manager diagnostic (CPU job 1404617; GPU one 1404577 cancelled unrun): validation windows in
  development buildings score like development; the error sits on new buildings out of the static range, above all es_B40
  (V_C 151,909.56 m3 for 7,507.5 m2; builder never reads V_C, so EnergyPlus loads are fine). Rules AMENDMENT 2 (md5 65e54b5c...,
  `train/step5_rules_amend2.md`): static z clipped to the development [min, max]; same 16 configs re-run from scratch. Grid
  1404570 cancelled 21:18, outputs moved to `ckpt/S_void_1404570` (never used). Clip employee DONE (state
  `Step5_docs/impl/2026-09-30_wp3_s_clip.md`, MANAGER VERIFIED 21:23: smoke 1404630 all PASS, own bounds equal, only es_B40
  clipped). Grid re-run array 1404631 (0-15 %4) RUNNING since 21:22; expect ~2-3 h. B1 1404525 RUNNING (heating trial 16 at
  21:12), scorer 1404526 waits. Part E and Step 6 part A task docs carry an AMENDMENT 2 note (clip with the checkpoint's stats;
  country-out stats from the training country only).
* **Step 5 at 20:49 EDT (history).** B0 scored + verified (20:23). Part C: smoke 1404529 showed 1.3 s/step; manager probe 1404560 found
  the cause (cudnn deterministic=True: TCN 30x slower); `s5_train.py` seed_all now deterministic=False, benchmark=True (operational,
  logged in `..._wp3_s.md`); new smoke 1404569 all CHECK PASS (reload 4 dp equal), 0.31-0.95 GPU-h per config; grid array 1404570
  RUNNING (0-15 %8). ⚠️ S0 and S1 early-stopped with best epoch 1: val_sum 0.46 / 0.51 while train loss 0.10, i.e. per target
  ~0.15 standardised MSE vs B1's ~0.016 on heating -> manager diagnostic 1404577 (`/speed-scratch/o_iseri/5J/mgr/mgr_diag_s_<id>.out`:
  static z ranges dev vs val, per-target MSE dev vs val, per validation block, own-presence check on val rows). Part B (B1,
  1404525) RUNNING (trial 6 of heating at 20:47), scorer 1404526 waits.
* **Steps 6 to 8:** specs and validation plans written 2026-09-28. Step 6 part A task (`Step6_docs/impl/2026-09-30_wp4_predict_TASK.md`)
  and part B task (the ONE scoring job, `..._wp4_scoring_TASK.md`, 20:47) written. 3J/4J setup review (author asked 20:45):
  `Prompts/manager/2026-09-30_setup_check_3J_4J.md` (Sonnet reviewer, docs only, no UK file): top points = most test cells hold one
  building so the building bootstrap adds little (frozen; state in the paper); level vs timing not separated (suggest a
  timing-only control REPORTED in Step 6, not gated); Step 7 must not compare against the heating-only 4J Step 10 builder; Step 5/6
  docs still say three one-country folds, rules say two (fix wording). Not yet checked by the manager.
* **Board:** v33 = this update (10-01 04:17 EDT). Live page is the master: read + diff before any republish.

## §5. Do this next (rewrite after every step)

0. **START HERE (2026-10-01 04:17 EDT).** 🟢 Step 6 CLOSED 04:16 (ONE scoring job 1405205; results
   `Step6_docs/outputs_step6/RESULTS.md`; manager re-derived, job 1405218). S: G5J.3 31/32, 31/32, 26/28 (+4 NE); G5J.2 21/14/14
   of 32; C never passes; 6D claims hold 11/12 (heating on both-new = partly); seeds 2/3 much worse (claim = pinned model);
   new country Spain->Italy fails, Italy->Spain partly. NEXT = Step 7 (`Step7_docs/5thJ_07_speedDistrict.md`, all items DRAFT):
   write the Step 7 design ruling first (district = ES-MAD-BERRUGUETE from 4J Step 10; recommended: the 7C EnergyPlus check uses
   the 5J multi-zone builder `tools/5thJ_idf_mz.py` on each real dwelling mapped to its 5J archetype vector, so surrogate error
   is not mixed with builder error (3J/4J review issue 4); the 4J real-geometry runs only as a reported side line; household
   pool = campaign households + a larger built pool, in/out-of-range counted), then employee tasks (mapping, draws, EP check,
   speed). 🔴 7E: copy Spain+Italy checkpoints off Speed with md5s before ~31 Oct. Then Step 8 (writing).
0-prev4. **(2026-10-01 02:53 EDT, DONE 04:16.)** 🟢 Step 5 CLOSED (02:52; Progress Log + `Step5_docs/outputs_step5/models.md` +
   `winner.md`). Step 6 IN PROGRESS:
   * Part B0 (reported analyses) DONE + VERIFIED: locked `freeze/s6_reported_v2.py` md5 3a0749b1... (v1 `freeze/s6_reported.py`
     is VOID: wrong lag sign); state `Step6_docs/impl/2026-10-01_wp4_reported.md`.
   * Part A (state `Step6_docs/impl/2026-09-30_wp4_predict.md`): scorer test mode locked 02:16 (`freeze/5thJ_04_scorer_t.py`
     md5 4d15df70..., `gates_frozen_amend1.md5`; diff = intended lines only, byte-equal without --test: manager read job
     1405152); test store built; predictions RUNNING (B0 1405157, B1+B1_loco_es 1405159, B1_loco_it 1405160, GPU array 1405161
     = S, C, S_seed2, S_seed3, S_loco_es, S_loco_it), final check 1405162. NEXT: read 1405162; verify (one test flat's S
     prediction recomputed from the pinned checkpoint + test drivers with own code in a GPU/CPU job; open logs: no test truth;
     counts); then launch part B (`Step6_docs/impl/2026-09-30_wp4_scoring_TASK.md`; it now has 24 scorer calls + 3 calls of
     s6_reported_v2 --test; the startup script must also check s6_reported_v2.md5 and the S_seed2/3 + all checkpoint md5s
     against `test/ckpt_md5_snapshot.tsv` and the Step 5 records). After scoring: manager re-derives 3 numbers, claims.txt by
     6D, Progress Log, then Step 7.
0-prev3. **(2026-10-01 01:01 EDT, DONE 02:52.)** Step 5 part D DONE + VERIFIED: winner **S3** (TCN 64 large λ1), validation G5J.3
   30/32, G5J.2 19/32 (load accuracy fails mostly in Italian MFH/AB = RESULT), skill over B1 excludes 0 in 30/32; pinned
   (`train/winner/pinned/best.pt`, md5 78271da9...); record `Step5_docs/outputs_step5/winner.md`. B1 verified (own code equal).
   Rules AMENDMENT 3 (sealed 00:31:58, md5 5e937d09...): B1 clipped at 0 from now on (S/C already were); sensitivity: winner
   unchanged. Part E employee RUNNING (launched 01:00; state `Step5_docs/impl/2026-09-30_wp3_control.md`): C seeds 1-3, S3 seeds
   2-3, S_loco_es/it, B1_loco_es/it, validation scoring vs `pred/B1_clip0`. When it reports: verify (3 donor rows from the md5
   rule, C config diff, one G5J.3 cell of C with own code, seed spread), close Step 5 (Progress Log, models.md), then Step 6
   part A (`Step6_docs/impl/2026-09-30_wp4_predict_TASK.md`, has AMENDMENT 2/3 notes), verify, part B (ONE scoring job).
0-prev2. **(2026-09-30 23:24 EDT, DONE 01:00.)** Grid 1404631 DONE (16/16 exit 0; manager read the logs; best S11 0.110). Part D
   chain RUNNING (state `Step5_docs/impl/2026-09-30_wp3_winner.md`): shortlist 1404807 DONE = S2, S3, S1, S11, S9, S13 (equals
   the manager's own list); predictions 1404808 (GPU) running; scorers 1404809 wait on B and on the B1 scorer 1404526; winner
   1404810, reload+pin 1404811, cleanup 1404812. B1 1404525 is PREDICTING validation (313/1980 at 23:16, slow; hours). If
   1404525 or 1404526 fails, cancel 1404809-1404812. When B1 + 1404526 finish: verify B1 (one flat recomputed from the saved
   model with own code, one G5J.2 cell, the total-electricity rule). When the chain finishes: verify the winner (R7.3 from the
   6 score files with own code, one G5J.3 cell from predictions + truth, reload loss; STATIC_CLIP lines present), then launch
   part E (`..._wp3_control_TASK.md`, has an AMENDMENT 2 note), verify, close Step 5, then Step 6 A, B. Step 6 spec now has
   section 6D (claim rule, written 21:25 before any test result; household-day sharing; weekday note). If S stays worse than
   B1, that is a RESULT. Items 0a/0b below are history.
0-prev. **(2026-09-30 21:24 EDT, DONE 23:24.)** Grid re-run 1404631 and B1 1404525 RUNNING; then part D.
0a. **(2026-09-30 20:49 EDT, DONE 21:23: bug found = static extrapolation, AMENDMENT 2.)** First read diagnostic 1404577. If it shows a BUG (e.g. validation windows or static
   inputs built wrong, new-building static z far outside the development range): fix in a fresh employee task, re-smoke, cancel
   and resubmit the grid (no result is final before the winner). If it shows a REAL gap (S worse than B1 on new buildings): the
   grid stays; record it (a RESULT, not a defect); the rules fix the grid, no new configs. Then read B1 (1404525/1404526) and
   verify; then part D when the grid has finished; then part E; close Step 5; then Step 6 A, B. Older item 0 (20:21) below.
0b. **(2026-09-30 20:21 EDT).** Step 5 rules: `Step5_docs/outputs_step5/step5_rules.md` + AMENDMENT 1 (never edit;
   amendments only, each locked on Speed with a prefix-unchanged check like job 1404523). Part A DONE + verified. RUNNING now:
   B0 + its score (1404520/1404521: read `train/logs/s5_b0_1404520.out` and `train/score` tag B0; expect G5J.3 FAIL on every cell;
   re-derive one B0 G5J.2 cell with own code), part B employee (B1, state `Step5_docs/impl/2026-09-30_wp3_b1.md`), part C employee
   (S smoke + 16-config grid, state `..._wp3_s.md`). When each reports: verify with own code (B1 one flat recomputed from the saved
   model; S one smoke window rebuilt from raw files, reload loss, 16 configs differ only in the 4 factors). When the grid has
   finished: launch part D (task `Step5_docs/impl/2026-09-30_wp3_winner_TASK.md`: shortlist 3+3, predict, score, winner by R7,
   reload check, pin); verify; then part E (task `..._wp3_control_TASK.md`: blind control C, seeds 1-3, one-country trainings);
   verify; close Step 5; then Step 6 (needs a test mode for the scorer: a dated amendment to the freeze, never an edit). GPU: `-p ps
   --gres=gpu:nvidia_a100_2g.20gb:1`, at most 30 CPUs for 5J in total. Lighting: still asked (not blocking).
1. UK arrays wait on the author's UK household script (`tools/5thJ_design_households_uk.py`) and the UKDS 5J line. Author to check
   the ASHRAE 2014 edition clause (amendment only if it differs).
2. After every step: Progress Log entry, this §4/§5, memory line, board (read + diff live page, syntax check,
   republish). Run `date` before every stamp. The previous version of this file is in
   `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-10-01_0416.md` (older §5 items, for the record).
## §6. Lessons carried (full list in the checklist, 16 items)

Clock origin (4J diaries start 04:00, Spain 06:00: rotate to midnight); same input can give different
EnergyPlus output (noise floor from replicates); heating effect tiny (expect the claim in electricity and
peaks); only geometry-ordered effects survived (score per dwelling class); right level per statistic;
exit 0 is not proof; cache keys on every input; one working directory per run; right meters; preflight
with pinned inputs; `--exclude=antenna1`; weather moves more than occupancy; laundry lives in secondary
activity; leakage from country-only fields; bootstrap by building and household; gates seen failing.

## §7. Open decisions (one line each; the full text is in the Overview)

O-3 campaign size RULED 09-30 16:16 + design FROZEN 16:38 (Spain 4,768 + Italy 4,501 runs) · O-4 input window RULED 09-30 20:10 (168 h + 24 h, per flat, EnergyPlus inputs only; `Step5_docs/outputs_step5/step5_rules.md`)
· O-5 CPU share RULED 09-30: 30 CPUs · O-6 venue (after RQ1 and RQ2) · O-7 how UK aggregate
gate results reach the manager (recommend: the author asks UKDS for written permission) · k dwellings per floor
for MFH/AB (TABULA count, else manager) · COP 3.0 ASSUMED (author may change) · lighting schedule (ask if absent).
