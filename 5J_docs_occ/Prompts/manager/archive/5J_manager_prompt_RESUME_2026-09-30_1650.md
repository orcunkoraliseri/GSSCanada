# 5J manager prompt: RESUME the occupancy-aware surrogate paper (paste the whole file into a new session)

First written 2026-09-28 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6
and §7 change only when a rule or a design changes. Edit in place; never fork a copy.
Last updated: **2026-09-30 ~16:45 EDT: D2-8 multi-zone design written, builder task running, author asked A+B. Before: ~15:50 EDT: weather + design + pilot report verified; campaign held on D2-8 (author: whole-building box). Before that, ~15:30 local: pilot array failed at once (EnergyPlus `in.idf` link clash on Linux), fixed,
50/50 runs DONE on Speed (1403962 + 1403963); weather download DONE (78/78); author ruled ALL compute on Speed, nothing
on the local CPU (§3); two employees running on Speed: weather batch 2b and pilot part 2 report. Start at §5 item 0.**

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
    **15:38: 43 zips; about 25 min per month on CDS; Seville 5/13, Manchester and Milan 0 → complete
    about 2026-09-30 morning.** **18:56 (session closed): 50 zips, PID 19328 alive, Seville 11/13, Manchester
    and Milan folders not yet created.** **21:18 check: 54 zips, PID alive, Seville 13/13 done, Manchester 2/13,
    Milan 0 → about 10 h left, done about 2026-09-30 07:30. **21:10: Seville (batch 2a) converted, checked, scored
    (RMSE 2.30 °C; July 29.52, Jan 10.66 re-derived by the manager; md5 b7d60181…). Batch 2b = Manchester + Milan.**
    **21:35 check: CDS has slowed to about 40 min per zip (Manchester zips at 20:35 and 21:17; log shows the 2014-02
    request ACCEPTED, waiting). PID alive. 24 zips left → done about 2026-09-30 afternoon, not morning.** Do nothing
    to the download; never start a second one.
  * **Weather batch 1 DONE and checked 2026-09-29 ~15:40:** Valencia 2010, Birmingham 2014 and Turin 2014
    are in `_5J_data/surrogate/weather/epw/`. The checker is `tools/5thJ_check_epw.py`, seen failing 3×; the
    real run passed 3 of 3. RMSE against TABULA, in °C: Valencia 1.62, Birmingham 1.18, Turin 2.96, Madrid
    4.73, London 1.61, Bologna 3.67 (`epw/weather_score_5J.json`). Manager re-derived Valencia 1.621 and Turin
    July -4.30 °C against its station file. Turin's summer cold is mostly the real 2014 year: Bologna ERA5 2014
    is also -3.4 °C in July. Turin is kept. The half-cell (0.125°) LOCATION tolerance is accepted.
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
  * **act2 rule `prefix2_major` DONE and checked 2026-09-29 ~15:50** (now the default; state
    `Step2_docs/impl/2026-09-29_wp1_act2.md`, "Verified (manager)"; trigger md5 f02f52d1…; check
    `tools/5thJ_check_act2.py`, seen failing). `prefix2` and `--no-act2` still md5-equal to `wp1_test`. Prefix 33
    → ironing (332) in Spain (118,790 vs 22,780 min) and Italy (24,540 vs 5,610); manager re-derived both from the
    full pools. H1 now heating 10,747, cooling 4,831, appliances 2,372 kWh. Stock appliance mean unchanged
    (CREST calibration to published cycles), so act2 moves timing, not totals. UK not run (author script later).
  * **Open for the pilot:** about 195 kWh/m² heating and 88 kWh/m² cooling on the 55 m² old house look
    high; cooling is supply total (includes latent). Compare with the TABULA ES.ME reference need and
    choose sensible or total cooling (write the choice in 2F).
  * **Design tables DONE and verified 2026-09-29 ~21:38** (state `Step2_docs/impl/2026-09-29_wp1_design.md`,
    "Verified (manager)" + "Manager rulings"; outputs `Step2_docs/outputs_step2/`): buildings 120 (40 per country,
    10 per class, same 40 on the 3 climates; infiltration [0.3, 1.0] ach + north axis, Latin hypercube, seed 5),
    households es 60 + it 60 (size-stratified; v1 unweighted), climates 9 (Manchester, Milan pending), pilot 50
    rows (Madrid 2010, 5 buildings × 10 households: 40 single + 2 inputs × 5 replicates). Checker
    `tools/5thJ_check_design.py` PASS=44 (manager re-ran), seen failing. UK household script
    `tools/5thJ_design_households_uk.py` written, never run (author runs it).
  * **Households v2: DONE + verified 2026-09-29 ~21:48** (state `Step2_docs/impl/2026-09-29_wp1_households_v2.md`,
    "Verified (manager)" + "Manager rulings"). Weighted draw (seed 5, v1 strata counts kept; v1 tables kept in
    `outputs_step2/v1_unweighted/`); **ruling: household weight = person weight of the lowest-pid member in BOTH
    countries** (Italy has no household weight; Spain's `FACTOR_hogar` sits in raw DHOGAR, not used, sensitivity
    only). Checker PASS=46 (manager re-ran). Trigger md5 075fdd73…: `--hids FILE` (unknown hid -> exit 1 before any
    output), writes `<out>/presence/` (default run: 100/100 = shipped); default run md5-equal to `wp1_guard`.
    `wp1_hids/es_60/` = the 60 Spanish households (mean electricity 2307.2 vs 2322.8 default); pilot hids in
    `outputs_step2/pilot_hids_es.csv`. Later: `5thJ_idf._household` must read `<out>/presence/`.
  * **Pilot part 1: DONE + verified 2026-09-29 ~21:53** (state `Step2_docs/impl/2026-09-30_wp1_pilot.md`): 42 portable
    inputs (50 runs), relative = absolute gate PASS + seen failing; Speed copy md5 127/127 equal; 43 T free.
    **Check job 1401744 (running), array 1401745 (1-50%8, afterok) PENDING** in `/speed-scratch/o_iseri/5J/pilot/`.
    B16 test input: heating 23.8, cooling 12.0 MWh/yr, checked per m2 in part 2.
    **22:05: check job still RUNNING (14 min): md5 done (127 equal), `lfs` not found, now in `du -sh
    /speed-scratch/o_iseri` over ~9 TB, which is slow; the version check and the array release come after it.**
    Not a fault, only a delay (the array would wait on the CPU cap anyway). Lesson for the campaign check job:
    no `du` over the whole scratch tree; `du -sb` of the 5J folder only.
  * Still open in Step 2: weather batch 2b, pilot (running), pilot part 2 (report, campaign size). The 4J box took about 2 s of core
    time per run, so CPU is not the limit.
* 🔴 **FINDING 5J-1 (2026-09-29 ~16:05): the Spain/Italy trigger runs read the pooled 4J corpus, which holds UK
    rows** (skipped in-process, nothing printed or written; the rule is broken as written). Waiting on the author:
    (1) run the one-line Spain+Italy copy (exact command in §5 item 2b; sent to the author 2026-09-29 ~16:15);
    (2) whether anything needs reporting to UKDS (author's call; never draft or send anything without being asked).
    **No 5J run that loads the corpus until the copy exists.** At session close (18:56) `_5J_data/surrogate/inputs/`
    was still EMPTY: the author had not run the copy and had not answered (2).
    **21:20: author MADE the copy** (`inputs/4J_step3_corpus_es_it.jsonl`, 57,400 lines, es 19,140, it 38,260,
    uk 0 = 4J Step 3's own counts; md5 1a516344…). **21:30: corpus-guard employee RUNNING** (task
    `Step2_docs/impl/2026-09-29_wp1_corpus_guard_TASK.md`, state `..._wp1_corpus_guard.md`, outputs `wp1_guard/`).
    (2) UKDS reporting: still the author's call, not asked again.
    **FIXED + verified 2026-09-29 ~21:37:** trigger md5 c642cda4…, `--corpus` default = the copy, guard refuses the
    pooled file by name/location before opening (manager re-ran: exit 3 twice); Spain and Italy outputs md5-equal to
    act2 (state `Step2_docs/impl/2026-09-29_wp1_corpus_guard.md`, "Verified (manager)"). Limit: a renamed copy of
    the pooled file elsewhere would pass the name check.
* 🔴 **FINDING 5J-2 (2026-09-29 ~21:40):** the design employee started a repo-wide grep (`n_air_use`, *.csv/*.json/
    *.py) and killed it at once, nothing printed; about 1,800 UK-named csv/json 4J outputs were in its reach. Same
    class as 5J-1. Fix = §3 rule (no repo-wide search). Reporting 5J-1/5J-2 to UKDS: author's call; tell the author
    once, in one bullet, do not draft anything.
* **Steps 3 to 8:** specs and validation plans written 2026-09-28; nothing run. Nothing submitted to
  Speed for 5J.
* **1J** on 2026-09-28 night: one 5-CPU draw task running (`1400935_19`), two 1-CPU scorers waiting.
* **Board v15 published 2026-09-29 ~21:55** (pilot queued on Speed). Next board = v16.
* Board v14 published 2026-09-29 ~21:48 (households weighted + chosen households run exactly; pilot being built). Next board = v15.
* Board v13 published 2026-09-29 ~21:50 (script locked to the copy; design tables done; weather slower). Next board = v14.
* Board v12 published 2026-09-29 ~21:15 (UK bullet now amber: copy made, script being locked; Seville ready).
* Board v11 published 2026-09-29 ~16:10 (v10 at ~15:55: "Secondary activity" -> done; v11: red "Waiting on you: UK-file issue" bullet + stamp). 13 done, 3 in progress, 36 not started. Next board = v12.

## §5. Do this next (rewrite after every step)

0. **Where we are (2026-09-30 ~15:50 EDT) — START HERE:** weather batch 2b, the climates.csv refresh and the pilot
   report are DONE and verified (Progress Log entry 15:50; pilot state file last section). O-5 = 30 CPUs; O-3 =
   22,160 runs, no cut. 🔴 Campaign HELD on **D2-8, RULED 16:00: floors + thermal zones, never one zone per building; design written 16:45 (`Step2_docs/impl/2026-09-30_d2-8_multizone_design.md`), employee building `tools/5thJ_idf_mz.py` (task `..._wp1_multizone_builder_TASK.md`); A RULED every flat tested, B RULED 4 targets (heat, cool, equipment, total elec with COP 3.0 ASSUMED); then design tables + pilot rebuild**: the 4J box is the whole building, so MFH/AB put one
   household in a 4-9 storey block (and per-m2 uses one plate); electricity is a pass-through (appliance level x
   schedule). Once the author rules: an employee patches `tools/5thJ_idf.py` (build from a modified `derive` dict,
   never edit 4J; prints `PATCH ... OK`), re-runs the 50-run pilot on Speed (arrays like 1403962/3), checker with
   4.3 absent = presence 0 and per-m2 on the right area; then the campaign task doc (Speed, 30 CPUs, check job with
   ONE real EnergyPlus run, Spain+Italy arrays first; UK arrays wait on the author's UK household script and the
   UKDS project line). Board v16 + memory line still to do.
   **Previous item 0 (2026-09-30 ~15:30):** pilot runs 50/50 DONE on Speed (arrays 1403962 + 1403963 after the
   `in.idf` fix; failed 1401745 kept in `pilot/failed_1401745/`; state `Step2_docs/impl/2026-09-30_wp1_pilot.md` last
   section). Weather 78/78 zips, Manchester + Milan EPWs converted (15:14, before the Speed-only ruling). Two
   employees RUNNING on Speed: (a) weather batch 2b checks + scoring + climates.csv refresh (task
   `2026-09-30_wp1_weather_convert_batch2b_TASK.md`, AMENDMENT section; Speed folder `5J/weather_batch2b/`);
   (b) pilot part 2 report (task `2026-09-30_wp1_pilot_report_TASK.md`, AMENDMENT; Speed folder `5J/pilot/report/`).
   When they report: re-derive one number each (one RMSE; one run's annual electricity + median seconds), then rule
   O-3 campaign size and O-5 CPU share, write the campaign task doc (Speed, with ONE real EnergyPlus run in the check
   job), board v16, memory line. Old item 0 kept below for the record.
   **Old item 0 (2026-09-29 ~21:54):** pilot part 1 DONE and verified; array 1401745 queued (account at
   its 64-CPU cap; 1J scorers expected to end tonight). First: `sacct -j 1401744,1401745 -X
   --format=JobID,State,ExitCode,Elapsed` (on the cluster, login node, fine). If the check job FAILED the array
   never starts (DependencyNeverSatisfied): read `check_1401744.out`, fix, resubmit both. If 1401744 is STILL
   running in `du` next morning: `scancel 1401744` (5J's own job; the array then drops), resubmit the check with
   `du -sb /speed-scratch/o_iseri/5J` instead of the whole tree, then resubmit the array with afterok on it; write
   both new JobIDs in the pilot state file Ledger. Once `sacct` shows the pilot array finished, launch a fresh employee on the pilot part 2 task doc,
   READY: `Step2_docs/impl/2026-09-30_wp1_pilot_report_TASK.md` (copy results back, gates 2.1-5.3 of the val doc,
   seen failing, `outputs_step2/pilot_report.md`); then the manager rules O-3 campaign size and the O-5 share.
   Check the time with `date` before stamping anything.
1. Read the last Progress Log entry of the checklist, the Step 2 doc 2F, and the state files
   `Step2_docs/impl/2026-09-29_wp1_weather.md`, `2026-09-29_wp1_wrapper.md` and `2026-09-29_wp1_act2.md`.
2. **act2 rule: DONE** (2026-09-29 ~15:50). Nothing to do; `prefix2_major` is the default for every 5J run.
2b. **Corpus copy + guard: DONE and verified 2026-09-29** (kept below for the record). When `_5J_data/surrogate/inputs/4J_step3_corpus_es_it.jsonl`
   exists: check it has 0 lines with `"country": "uk"` (grep -c on the COPY only; never on the pooled file), md5 it,
   then an employee adds an additive `--corpus` argument to `tools/5thJ_step9_trigger_act2.py` (default = the copy),
   a guard that exits on the pooled 4J path, and shows Spain `prefix2_major` outputs md5-equal to
   `wp1_act2/step9_major/`. Only then design tables (item 4) and the pilot.
   The command the author runs in their OWN terminal (never run by an AI tool, it reads the pooled file):
   `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe -c "import json; src=r'C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step3_docs\outputs_step3\4J_step3_corpus.jsonl'; dst=r'C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl'; o=open(dst,'w',encoding='utf-8',newline=''); [o.write(l) for l in open(src,encoding='utf-8',newline='') if l.strip() and json.loads(l)['country']!='uk']; o.close()"`
   The corpus-guard employee must also check the trigger has no OTHER path that reads a pooled 4J file (grep the
   trigger and the 4J modules it imports for `outputs_step3`, `corpus`, `pool`), and list any in its state file.
3. **Weather batch 2b (Seville already done as 2a, task `..._weather_convert_seville_TASK.md`):** count zips (`ls _5J_data/surrogate/weather/raw/*/*.zip | wc -l`, target 78) and check
   PID 19328 is alive; never start a second download (at ~40 min per zip, expect 78 about 2026-09-30 afternoon).
   After batch 2b, rerun `tools/5thJ_design_tables.py` so climates.csv gets the two md5s (other tables must stay
   md5-equal; show it) and re-run the checker. When uk_manchester and it_milan have 13 zips
   each, a fresh employee runs batch 2b (copy the Seville task, two sites). The task is the same as `Step2_docs/impl/2026-09-29_wp1_weather_convert_TASK.md`
   with those three `--site` values. The checker already exists, so rerun only its failing gate (8,759 rows) and add
   the results to `weather_score_5J.json`. Re-derive one RMSE yourself.
4. **Design tables: DONE and verified 2026-09-29 ~21:38** (see §4); households v2 running (item 0). Author still
   runs the UK household script (`tools/5thJ_design_households_uk.py`, after v2 adds weights) when convenient; not
   needed for the Spain pilot. Original plan text: (`Step2_docs/impl/<date>_wp1_design_TASK.md`): buildings.csv
   (Latin hypercube inside TABULA ranges per class; include infiltration and north axis), households.csv
   (Spain and Italy drawn with survey weights by household size; **UK: the employee writes a script
   only; the author runs it; nobody opens its output**), climates.csv (nine cities), seeds and md5s.
5. Then D2-5/D2-6 (copy inputs and EPWs to `/speed-scratch/o_iseri/5J/`, md5 both sides; disk preflight
   job), write the CPU share in the Progress Log (O-5, read `squeue` first), then the 50-run Spain pilot
   (`sbatch`, `-t 7-00:00:00`, `--exclude=antenna1`).
   **Pilot part 1 RUNNING since ~21:47 (was: task doc READY): `Step2_docs/impl/2026-09-30_wp1_pilot_TASK.md`** (build 50 portable
   inputs, relative-path gate, copy to Speed, md5 + disk preflight job, array 1-50%8). Launch a fresh employee on it
   right after households v2 is verified. O-5 read 2026-09-29 ~21:37 (Progress Log): account at its 64-CPU cap
   (1J WP4 40 + openubem arrays 24); pilot asks 8 CPUs and queues. Pilot part 2 task doc READY:
   `Step2_docs/impl/2026-09-30_wp1_pilot_report_TASK.md`.
   The Spain pilot does not need Manchester/Milan: once households v2 is verified, D2-5/D2-6 and the pilot can go
   (pilot inputs: Madrid 2010 EPW, the 5 pilot buildings, `outputs_step2/pilot_hids_es.csv`, the copy, 4J pools).
6. After every step: Progress Log entry, republish the board (v16 next: read + diff live page,
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
