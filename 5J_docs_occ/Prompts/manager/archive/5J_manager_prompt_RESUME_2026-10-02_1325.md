# 5J manager prompt: RESUME the occupancy-aware surrogate paper (paste the whole file into a new session)

First written 2026-09-28 by the outgoing manager session. **Kept current: after every step the manager
rewrites §4 ("State now") and §5 ("Do this next"), and updates the "Last updated" line.** §1, §2, §3, §6
and §7 change only when a rule or a design changes. Edit in place; never fork a copy.
Last updated: **2026-10-02 12:25 EDT (OpenUBEM replied: about 158 Bologna models will be rebuilt as `_win_2026-10-06`, do NOT freeze the Bologna split or seal A2 on 10-05; 12 `_whole` buildings stay excluded; see §5 item PEER-REPLY-1002. Madrid array 3,536 done at 11:15, no failures. Start at §5 item START-HERE-1002 and read PEER-REPLY-1002 first.)** Older "Last updated" history (23:20 and earlier stamps): `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-10-02_pre_newsession.md`. Older §4/§5 detail: `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-10-01_0817.md`; the 14:42 version (§5 items v0-v3, 0-old) is `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-10-01_1916.md`.

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
  🟡 **AMENDMENT (author, 2026-10-01 ~13:00): "if it is avaialble use half of the local resources from the desktop".** Up to
  10 of 20 CPUs and ~31 GB RAM on the desktop (`py -3.13`, numpy 2.3.5) when Speed is blocked (account cap 64 CPUs shared with
  other projects). Spain/Italy copies only, run tree under `GSSCanada\_local_runs/5J_*`, path constants patched in copies, the
  Speed tree stays the master (sync results back). Never touch the author's own local jobs.
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

**CURRENT STATE (2026-10-02 11:15 EDT; this block is newer than the Step bullets below; the §5 START-HERE item is the order of work).**

  * Steps 1-7 CLOSED; Step 8 (writing) is a draft waiting on author items; Step 9 (Model A, EnergyPlus campaign on OpenUBEM windowed IDFs) is the live work.
  * Madrid: base is `_win_2026-10-05` (delivered 10-01 21:12; our md5 check clean). The running array 1409235 still runs the OLD `_win_2026-10-03` base (8,616 rows planned, throttle 32); 3,536 tasks done at 11:15, 0 failed, about 230 rows/h, estimated end 3 Oct morning. Check 1409266 waits on it. Afterwards: void the 171 changed stems' old results and re-run 1,458 rows on win5 (smoke 1409919 of the staged code was 15/15 clean). Amendment A1 (sealed) covers this.
  * Bologna: base `_win_2026-10-05` (delivered 10-01 22:55; md5 clean). Task 9p DONE: 12 buildings unrunnable (one `_whole` zone per floor), 38 sliver buildings (run as delivered), 3 buildings held out for tiny flats. Provisional plan 9,435 rows (md5 c6de7168...), lists dev 818 / val 176 / test 173. Amendment A2 NOT written, and now must wait for `_win_2026-10-06` (peer reply 10-02, see §5 PEER-REPLY-1002; the numbers in this bullet are for 10-05 and will change for the rebuilt homes). The author said 'of course tell it': message to OpenUBEM written 10-02 ~07:20 (file in `messages_GSSCanada/`, no reply at 11:15). OpenUBEM runs their own Bologna jobs 10-02 ~08:00 to 3 Oct ~01:00 on the same 64-CPU account cap.
  * Open for the author (one decision max per reply, do not nag): FINDING 5J-3 ruling (UKDS), T46 search, Li 2021 full text, ASHRAE G14 2014 edition, lighting, venue (O-6), UK line.
  * Owed housekeeping: Progress Log entry for 10-02 in `Step9_docs/5thJ_09_modelA.md`, memory line, board republish (live page v80; read + diff first).

**(Older Step bullets follow; where they disagree with the block above, the block wins.)**

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
* **🟢 Step 5 CLOSED (10-01 02:52).** Rules `Step5_docs/outputs_step5/step5_rules.md` + AMENDMENTS 1-3 (md5 5e937d09...; 2 = static
  inputs clipped to the development range, 3 = tree baseline clipped at 0). Winner **S3** (TCN 64 large), pinned
  `train/winner/pinned/best.pt` md5 78271da9...; records `winner.md`, `models.md`. Validation: occupancy effect 30/32, load 19/32.
  Blind control C fails 32/32 (good). Seeds 2/3 much worse (30/22/13). Checkpoints copied off Speed (24/24 md5 OK,
  `GSSCanada\_5J_data\surrogate\checkpoints\`).
* **🟢 Step 6 CLOSED (10-01 04:16).** ONE scoring job 1405205; `Step6_docs/outputs_step6/RESULTS.md` (corrected 06:07). Test: occupancy
  effect right in 31/32, 31/32, 26/28 cells; load accuracy 21/14/14 of 32; control never passes; claims hold 11/12 (heating on
  both-new = partly); seeds 2/3 much worse (claim = the pinned model); Spain->Italy fails (0-3/16), Italy->Spain partly (9-10/16);
  size + appliance level explain EP 73-98 % / S 79-98 % of the annual pair effect. Post-scoring rule (spec log 05:04): figure-data
  jobs may read test truth, log every open, write md5s, no verdict.
* **🟢 Step 7 CLOSED (10-01 13:15).** Design `Step7_docs/impl/2026-10-01_step7_design.md` (twins of 100 real Madrid buildings:
  2,034 twin dwellings vs 1,173 real; 560-household pool; N = 1,000 draws). State `Step7_docs/impl/2026-10-01_wp5_district.md`
  (last entry = VERIFIED). Outputs `Step7_docs/outputs_step7/` (district_spread.csv md5 62209987...). EnergyPlus check 2,000 runs
  over 20 draws; heating median CV(RMSE) 38.6 %, pooled NMBE +10.2 % (in range 27.1 % / -7.6 %, out of range 165 % / +58 %);
  district totals r 0.97-0.9999; S 61x EnergyPlus on a GPU slice, 1.2x on one CPU core. Spread: annual heating 12,728 MWh
  (12,697-12,760). Writer check (20/20 draws) and manager recount (112 rows, worst 5e-6) ran on the DESKTOP (Speed cap held by
  other projects; author allowed half the desktop); the three queued Speed copies were cancelled. Recount corrected the settling
  sentence (medians within 0.1 % from 100 draws; width from 500 draws within 6 % of its 1,000-draw value). Gate 1.4 WARN 3/8.
* **Step 8 (writing) STARTED.** Draft `writing/5J_manuscript_draft.md` (UK sentences are FINDING 5J-3 markers), highlights
  `writing/5J_highlights.md`, author list `writing/AUTHOR_TODO_5J.md` (item 0 = FINDING 5J-3), number ledger (94 rows)
  `Step8_docs/impl/2026-10-01_wp6_draft.md`: manager ledger pass DONE 08:23 (all equal to sources; Milan 3.165 -> 3.17).
  District text MERGED 08:28 (state `Step8_docs/impl/2026-10-01_wp6_s38.md`, manager note; backup
  `writing/archive/5J_manuscript_draft_pre_s38_merge_2026-10-01.md`): Abstract (200 words), 1.3, 2.6, 3.8 + Table 5, 4.5,
  Limitations (twin direction 2,034 vs 1,173), Conclusion 7. 3.8 spread numbers FILLED 12:25 and settling sentence corrected
  13:15 (state `Step8_docs/impl/2026-10-01_wp6_s38.md`). Figures 2-5 drawn (`figures/`, `writing/figures/`); Figure 5 DONE 13:15
  (all read-back checks pass; top row given its own x axis because the shared axis squeezed the histogram; caption checked;
  state `Step8_docs/impl/2026-10-01_wp6_fig5.md`). No draft section is waiting on data any more.
  Rule check DONE + verified 13:52 (`tools/5thJ_valpass.py`, state `Step8_docs/impl/2026-10-01_wp6_valpass.md`): 0 unmatched
  numbers, 0 citation orphans, no tool names, 11 small counts traced by hand; 4 lines fixed (draft md5 09c7bc0d...). Author prompts
  written 13:47: Figure 1, graphical abstract section 10, T47 references; overview page `5J_paper_overview.html`.
* 🔴 **FINDING 5J-3 (10-01 06:08, Progress Log):** the generated-day pools (`generated_leg5_es/it_constrained.jsonl`) are very probably
  the 4J Leg-5 LOCO generations, made by models fine-tuned on UK diaries (the Spain pool by the UK+Italy model). Author ruling
  needed; recommend writing to UKDS and keeping every 5J output private. No new generation; no data-release promise in the paper.
* **Step 9 (Model A) IN PROGRESS** (design + log `Step9_docs/5thJ_09_modelA.md`, read its LAST entries; rules DRAFT
  `Step9_docs/outputs_step9/step9_rules.md`, not sealed). Base = OpenUBEM windowed IDFs `_win_2026-10-03` (local
  `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_win_2026-10-03/`, Speed
  `/speed-scratch/o_iseri/fleets/EU11_<D>_win_2026-10-03`; tools switch with `MODELA_VINTAGE=win_2026-10-03`; open only the two
  district folders by full name, never list `EU-11/`).
  * Ruled: D9-3 pilot settings (ideal loads 20/26 C, People + appliances from Schedule:File) + one default-schedule run per
    building; D9-5 windows as delivered; D9-6 fix at source; tiny-flat hold-out (any flat < 15 m2 -> building out; author 17:39);
    **D9-4 (author 18:55) "follow openUBEM settings for buildings" = NO fast setting** (shading PolygonClipping daily, sizing
    Yes/Yes/Yes, delivered timestep; fast-setting check G-c7 PASSED but is not adopted); **"keep going handle simulations" =
    full plan, every building, no sampling** (manager reading, in R10).
  * Plan after hold-out: 18,021 runs (Madrid 9,201, Bologna 8,820); per building dev 9 / val 6 / test 6 incl. B0 + default;
    about 5,800-6,800 CPU-h = about 7.6-8.8 days at 32 CPUs; disk about 49 GB (0.229 MB per flat-year).
  * Splits sealed in R1 (building seed 9102, household seed 9101; md5s in R1). 10-04 rules written BEFORE any run (R1 a-d):
    Madrid split sealed on 10-03, a changed building keeps its split and its 10-03 runs are void and re-run; Madrid hold-out
    re-read on 10-04; Bologna split + hold-out derived on 10-04 by dated amendment before any Bologna run; every run stores its
    source IDF md5 and is reused only if it matches.
  * Closed checks: 9i writer gates on 10-02 (aggregator 1407560), 9j final-base walls by EnergyPlus (sample 1407674), store code
    accepted (9g). **Open 9k** (`impl/2026-10-01_wp9k_final_base_check.md`): writer gates on win3 (array 1407876, 22/38 done at
    19:15), aggregator 1407909 + store re-test 1407961 pending on it; degenerate-surface count (estimate about 75 Madrid / 20
    Bologna buildings; EnergyPlus counts come from each building's first campaign run; decision deferred).
  * **9l campaign runner** (`impl/2026-10-01_wp9l_campaign_madrid.md`, manager read 19:10 appended): code in Speed
    `/speed-scratch/o_iseri/5J/modelA/campaign/root/5J_docs_occ/tools/` (`a9_campaign_task.sh/.py`, check, prep); plan
    `manifests/plan_ES-MAD-BERRUGUETE.csv` 9,201 rows md5 f627f60d...; B0 = mean of 60 dev households (pilot rule, seed 9106).
    Smoke 1408110 (36 runs, 5 buildings incl. triangle 1271cddbf6bd1e8a): first 9 runs CLEAN at 19:15 (about 3.5 min each for a
    2-flat building, default-mode paths work, G-c3 exact, purity 0); check 1408112 -> re-submission 1408134 (expect all SKIP) ->
    check 2 1408136 queued.
  * OpenUBEM (peer `openubem-cc`, 18:56 + 19:13, claims): flat count follows floor area; Madrid changes only sliver/shared-record
    buildings; Bologna almost all; they send 10-04 paths + md5, Madrid changed-stem list, old/new count table; earliest 2 Oct.
* **Campaign (20:19):** 9k CLOSED (final base passes every writer gate), 9m ACCEPTED (skip key = 4 writer + 7 household code files actually loaded), smoke ACCEPTED (21/36 clean; not clean = triangle + 77-flat 394922138a6b5928, both degenerate), check control fixed (expected clean 4). Seal 1409233: 18/18 md5 OK, control FIRED, 38 files in `/speed-scratch/o_iseri/5J/modelA/step9_rules.md5`. Array 1409235 (index ranges = plan minus degenerate rows; deferred ranges in the 20:18 log entry are recomputable from `wp9k/degenerate_win3.csv` + the plan), check 1409266.
* **Board:** v80 (10-01 20:32 EDT; session closed, 9n helper to restart; before that v79 20:29; first 45 Madrid runs clean; Madrid campaign running; first 10 smoke runs clean; expect items=66 done=52 prog=5 todo=9). Routine: `Artifact read
  path=index.html` (or the local file if the manager published last), `diff --strip-trailing-cr`, back up `board_pre_vNN.html`,
  edit script, `node --check` + `node board_smoke.js board_v16.js`, publish with the url. Live page is the master.

## §5. Do this next (rewrite after every step)

PEER-REPLY-1002. **(2026-10-02 12:25 EDT, live message from `openubem-cc`, answers our three-differences note; READ BEFORE START-HERE-1002 item 4).**
   * **Do NOT freeze the Bologna split and do NOT seal A2 on the 10-05 files.** About 158 Bologna models (148 lost more than 5 % floor area vs 10-03) will be rebuilt into a new folder `IT-BOL-GALVANI2_win_2026-10-06`; they will send the stem list, paths and md5s. All other Bologna stems stay byte-identical to 10-05, so runs on unaffected stems stay valid. Cause (their FINDING 289, being traced): the flat-count rebuild merged the storeys of one flat into one tall zone with a single floor (example 0177dae25178d27e: 5 zones on 4 storeys in 10-03, 1 zone 0-12 m in 10-05). This is the 'fewer storeys' point from our note.
   * The 12 `_whole` buildings are INTENDED and are in their own exclusion list (`undivided_excluded_2026-10-05.csv`): keep them out (our plan already does). Slivers: no action. Tiny flats: they measure 5 such zones in 2 homes; our third building 97d478bc56840531 has a zero-floor zone `_F0_dwelling_3` (lost in the 10-04 flat-count rebuild; floor exists in 10-03); a defect on their side, expected to be fixed in the 10-06 rebuild if the home is among the affected ones. Our tiny-flat hold-out stands (3 buildings).
   * Order now: (a) wait for their 10-06 note; then md5-check ourselves, re-derive the Bologna split + hold-out on the final base (task 9p repeated for the changed stems only; sealed rule: a changed building keeps its split) and seal A2 on it; (b) Madrid first: when the array ends do the 1,458-row win5 resubmission as planned, and START NO Bologna array until A2 is sealed on the 10-06 base.
   * 🔴 **Open risk to measure (our own check, Speed sbatch, fresh Sonnet employee, Madrid win5 only):** the same flat-count rebuild gave Madrid 113 `flat_count` changed stems in 10-05. Compare per-building total floor area and storey count, win3 vs win5, for those stems BEFORE the 1,458-row win5 resubmission is submitted. Peer said Bologna only; Madrid is unconfirmed. If any Madrid stem lost floor area, ask the peer (message file in `messages_GSSCanada/`, Madrid campaign inputs only, no UK content) and hold those stems back.
   * No reply file or acknowledgement was sent by the manager (nothing was requested of us except waiting). Peer note itself was live only; this item is the record.
START-HERE-1002. **(2026-10-02 11:15 EDT; a new session starts here; items below it are history, the newest ones win).** Run `date` first. Nothing is due before the Madrid array ends (about 3 Oct morning), so a new session mostly checks and waits.
   1. Check (tcsh-safe, from the desktop): `ssh speed "bash -c 'sacct -j 1409235 -X -n -o State | sort | uniq -c; sacct -j 1409266 -X -n -o JobID,State'"`. Failed tasks: read the head of `campaign/logs/t_1409235_<n>.out`, resubmit only those indices. Never raise `%32`.
   2. Read OpenUBEM's reply: list `OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/` by name, open only files dated 2026-10-02 or later that are not our own message (peer `openubem-cc` also sends live messages). Wanted: the answer on the 12 `_whole` buildings and the zero-floor flat; their Bologna 10-05 collected note (expected about 3 Oct 01:00 EDT).
   3. When the Madrid array ends and check 1409266 reads clean (ROWS done 8,616, TASK_ERROR 0, PURITY 0, GC3 0, SRC 0, CONTROL FIRED, NOT_CLEAN by name): follow item c0000 below: move the void win3 results (`impl/wp9o_win5/void_results_win3.txt`) to `campaign/results_void_win3/`, submit the 1,458-row win5 resubmission (rows 16-1458) and its check.
   4. (SUPERSEDED by PEER-REPLY-1002: wait for the 10-06 rebuild before sealing A2; text below is the old plan.) Seal amendment A2 in `outputs_step9/step9_rules.md` BEFORE any Bologna run, as in item c0000000 item 1 (every md5 is in `Step9_docs/impl/2026-10-01_wp9p_rebase_bologna_win5.md`, its Next item 1). If OpenUBEM says the 12 `_whole` buildings are a defect they will fix, wait for the fix (a changed building voids its Bologna runs) and tell the author; if no reply by the time the CPU cap frees, seal A2 with the 12 excluded and go. Then: prep line, 3-row memory probe of the largest building, array `--array=1-9435%32` with dependency, check (c0000000 item 3).
   5. After each step: Progress Log entry, this file (§4 CURRENT STATE and this item), memory line, board v81 (read + diff the live page first). Reply to the author in the fixed short shape, English, plain words.
   Do NOT: open UK data or outputs, run compute on the login node, use wildcard searches that could match UK files, create images, or write to OpenUBEM about anything beyond the Bologna/Madrid campaign inputs without telling the author.
0. **START HERE (2026-10-01 20:19 EDT): Madrid campaign running.** Run `date` first. Steps a-e of the 19:16 list are DONE
   (9k read, smoke read, 9m key, seal, submit; see the log entries 19:30-20:18 and the manager reads in the 9k / 9l / 9m state files).
   a. **Daily:** `sacct -j 1409235 -X -n -o State | sort | uniq -c` (tcsh; no `$()`); read progress from sacct only (no wildcard
      listing of results/). Failed tasks: head of `campaign/logs/t_1409235_<n>.out`; resubmit only those indices
      (skip rule reuses the rest). 5J stays at 32 CPUs (`%32`); never raise it while OpenUBEM uses 32.
   b. **When the array ends:** read `campaign/logs/check_1409266.out`: ROWS done = 8,616, TASK_ERROR 0, PURITY 0, GC3 0, SRC 0,
      CONTROL planted_faults FIRED, every NOT_CLEAN by name (expected none, since degenerate buildings are deferred; any other
      not-clean run = new finding). Manager read in the 9l state file, log entry, board.
   c0000000000. **PEER NOTE 2026-10-02 07:10 EDT (openubem-cc, live message, info only):** their Madrid 10-05 run is finished (1,171 of 1,172 homes; the one failure is a 21 m2 single-zone home whose heat balance diverges, theirs, not re-run). Their Bologna 10-05 run (same 1,179 IDFs we hold, no file changes) is queued on Speed, start about 08:00 EDT, finish about 01:00 EDT 3 Oct; they will send a note when collected. They wrote this before seeing our 07:20 message. Their Bologna jobs share the 64-CPU account cap with our Madrid array.
   c000000000. **UPDATE 2026-10-02 ~07:20 EDT: author said "of course tell it" -> message WRITTEN (not a reply to anything) at `OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-10-02_4J_to_OpenUBEM_bologna_win5_three_differences.md` (12 `_whole` buildings + question, 38 sliver buildings, 6 tiny flats in 3 buildings + question on the zero-floor zone). Bologna only, no UK content. A2 NOT sealed yet: wait for their reply on the 12 `_whole` buildings (the Bologna campaign cannot start before the Madrid array ends, about 3 Oct). If no reply by the time the cap frees, seal A2 as in c0000000 item 1 (12 excluded) and go. Replies land in the same folder; read only files dated 2026-10-02 or later.**
   c00000000. **UPDATE 2026-10-02 07:05 EDT (new session, morning order of c00000 DONE):** smoke 1409919 = 15/15 CLEAN (0 NOT_CLEAN; 9 rows of 394922138a6b5928, 6 of 1271cddbf6bd1e8a); throttle restored to 32 (job 1410129 COMPLETED, ArrayTaskThrottle=32). Madrid array 1409235 (task index = run row, not building): 2,587 done / 32 running / 1 pending range, 0 failed, about 240 rows/h, check 1409266 pending on it; est. end about 3 Oct. Nothing due until it ends. Still waiting on the author: Bologna A2 decisions (c0000000 items 1-2). Board not republished this step (v80 live).
   c0000000. **UPDATE 23:20: 9p (Bologna 10-05) DONE; manager read done, A2 NOT yet written on purpose (author decides first). State `Step9_docs/impl/2026-10-01_wp9p_rebase_bologna_win5.md` (its Next item 1 has every md5 for A2). Measured differences from the peer's Bologna message: 12 buildings with one `_whole` zone per floor (cannot run), 38 buildings with 52 slivers at our 0.01 m rule (peer says 0), 6 flats under 15 m2 in 3 buildings (peer says none; one has no floor surface). MORNING DECISIONS for the author: (1) tell OpenUBEM about those three (draft the message, they reply in OpenUBEM docs) or accept them; (2) then seal A2 (lists dev 818 / val 176 / test 173, hold-out 3, 12 excluded, 38 run as delivered, plan 9,435 rows md5 c6de7168...). Staged copy in `/speed-scratch/o_iseri/5J/modelA/campaign_bol5/` never executed: when the 32-CPU cap frees (Madrid array: 736 done / 31 running / 1 pending at 23:18, 768 building tasks, so it ends about 3 Oct, NOT 8 Oct) run helper's line 1 (prep), then the 3-row probe of the largest building for memory, then the array. Madrid 1,458-row resubmission goes first or second: manager decides with the helper's timing (whole queue 2.8-3.3 days at 32 CPUs).**
   c000000. **UPDATE 22:55: Bologna `_win_2026-10-05` ARRIVED (OpenUBEM peer message; our own md5 of all 1,179 IDFs = their list, 0 differences; 1,070 flat_count rebuilt + all shifted to a local origin; 0 degenerate by their claim). Task 9p (fresh Sonnet, background) re-measures it, copies it to Speed (new fleet folder), rebuilds static, DERIVES the Bologna split + hold-out on the new base (seed 9102), builds a provisional plan and writes the sbatch line; state file `Step9_docs/impl/2026-10-01_wp9p_rebase_bologna_win5.md`. FIRST in the morning: read it; if no 'state written to' line the employee died, send another fresh one. Then the manager read: seal the Bologna lists + hold-out by dated amendment A2 BEFORE any Bologna run; decide the order (Madrid resubmission 1,458 rows vs Bologna rows; the 32-CPU cap is full until about 8 Oct). Bologna has no live runs and no void results. Slip logged: one `ls` of EU-11/ piped to a count (no UK name read).**
   c00000. **UPDATE 21:58 (author asleep): smoke task 1 (the 77-flat building) came out CLEAN, so the staged code works. 14 smoke rows still run (done about 03:30 EDT). Job 1410129 restores the throttle to 32 by itself after the smoke (check its log `campaign_win5/logs/restore_throttle_1410129.out`; if missing or failed run the `scontrol` line of the next item by hand). Morning order: (1) `date`; sacct of 1409235 and 1409919; (2) read all 15 RESULT lines `grep RESULT campaign_win5/logs/t_1409919_*.out` (expect 15 CLEAN: 9 rows of 394922138a6b5928 and 6 of 1271cddbf6bd1e8a); (3) daily array check, resubmit only failed indices; (4) nothing else is due before the array ends; OpenUBEM Bologna 10-05 not before 2 Oct (their message), handle per items c000/c0000.**
   c0000. **UPDATE 21:32: 9o DONE and ACCEPTED; amendment A1 is in `outputs_step9/step9_rules.md`. Smoke of the staged `campaign_win5` code = array 1409919 (15 rows, `%1`, the two smoke buildings; live array throttle lowered to 31). FIRST: read `campaign_win5/logs/t_1409919_<n>.out` RESULT lines (expect 0 NOT_CLEAN for both buildings) and fix the staged code if it crashed (zone map / b0 path were untested). WHEN the live array 1409235 ends and its check 1409266 is read: move the void results (`impl/wp9o_win5/void_results_win3.txt`) to `campaign/results_void_win3/`, then submit the item-7 line of the 9o state (rows 16-1458; 1-15 are done by the smoke) and its check; store build later with TWO roots, one ledger (win5 plan, zone_map_win5, `static_win5`; test the two-root build on the desktop first). The throttle was lowered 32 -> 31 for the smoke: restore with `scontrol update JobId=1409235 ArrayTaskThrottle=32` once 1409919 is finished.**
   c000. **UPDATE 21:12: Madrid `_win_2026-10-05` ARRIVED and was md5-checked by us (171 changed = 113 flat_count + 58 degenerate; 1,001 identical). Task 9o is running (fresh Sonnet; state `Step9_docs/impl/2026-10-01_wp9o_rebase_win5.md`; it reports, never decides). First: read that state file; if it has a 'state written to' line, do the manager read: decide the split-list and hold-out differences (sealed lists never move a building), then after the live array 1409235 ends, move the 171 stems' old results to `results_void_win3/` and submit the new array it names. Bologna 10-05 NOT delivered yet (local-origin shift; not before 2 Oct). The note below that says 'wait for 10-05' now applies to Bologna only.**
   c00. **UPDATE 20:55: OpenUBEM's next delivery is `_win_2026-10-05` (not 10-04; log 20:55 has their reasons: EnergyPlus's own degenerate rule, sliver triangles kept, Bologna moved to a local origin). Read item c below with 10-05 wherever it says 10-04. Their counts (63 / 12 / 20 homes) are claims: re-derive against our 72-building list.**
   c. **When OpenUBEM sends 10-04** (asked 20:18 to remove degenerate surfaces too; ACCEPTED 20:21: vertices within 0.01 m merged,
      a surface with < 3 vertices deleted with its windows and its partner only if the partner is degenerate too; a pair whose
      partner is whole is left unchanged and listed `partner_not_degenerate`, so such buildings may keep one Severe line and stay
      not clean by rule R1 e; delivery = `changed_stems.txt` with a reason column (flat_count / degenerate / both),
      `md5_2026-10-04.txt`, `degenerate_2026-10-04.csv`; they first match our list stem by stem; log 20:21 + 20:22): md5 every Madrid IDF against 10-03 ourselves;
      changed buildings: void + re-run (R1 a, d): copy 10-04 to a NEW Speed fleet folder and build a 10-04 Madrid plan on it;
      unchanged buildings then SKIP (same src md5), changed ones re-run; re-read the hold-out; submit the 585 deferred degenerate-building runs
      (index ranges = plan rows whose stem is in `wp9k/degenerate_win3.csv`); still degenerate -> run as delivered, reported not clean.
      Then Bologna: split + hold-out by dated AMENDMENT (seed 9102), plan, `it` B0, run.
   d00. **UPDATE 20:48: 9n is DONE and ACCEPTED (log 20:48; helper line present; counts re-derived 13 stored / 8 refused, heating 10832.012). Skip d0 and d. Remaining for the store: after check 1409266 reads clean, copy the 4 code files and run the one sbatch line in the state file's Next section (no build while the array runs; CPU cap full).**
   d0. **(old) UPDATE 20:38:** a fresh Sonnet employee was launched 20:34 on the 9n task doc (partial `wp9n/smoke_copy/` kept; no `a9_store_pre9n.py` existed). First: read `Step9_docs/impl/2026-10-01_wp9n_store_campaign.md`; if it has a "state written to" line, do the manager read; if missing or the employee left no line, send a fresh one (see d).
   d. Store from campaign output: task 9n was dispatched 20:30 but the old session closed at 20:31 before its state file existed, so the helper STOPPED: first check `Step9_docs/impl/2026-10-01_wp9n_store_campaign.md` and the folder `Step9_docs/impl/wp9n/`; if the state file is missing or has no "state written to" line, send a FRESH agent with the same task doc `Step9_docs/impl/2026-10-01_wp9n_store_campaign_TASK.md` (tell it to keep any partial `wp9n/smoke_copy/` and `a9_store_pre9n.py` it finds, and never overwrite `a9_store_pre9n.py` if present), then read its state file. Later: noise floor (10 x 10), store build on Speed after the check (fix the store check `heating_column_unique_by_position` to the
      exact supply-air label first, 9k read), GPU training (window ends late October).
   e. After every step: log entry, this §4/§5, memory line, board.
0-old. **(2026-10-01 13:52 EDT).** Run `date` first. Steps 1-7 are CLOSED; Step 8 is the only open step.
   a. Draft rule check DONE + verified 13:52 (see §4). The manager has no draft task left that does not wait on the author.
   a1. 14:17: RT47 vetted MIXED (`Prompts/deepResearch/VETTING_RT47.md`), initials + 7 method sources added (draft md5 6ea62229...,
       rule check exit 0). Figure 1 (md5 ee3a295c...) and graphical abstract made by the author's tool and checked; fix lists in
       Figure 1 prompt section 9 and graphical abstract prompt section 10.5. T48 (UK licence research) written 14:03, not yet run.
   b. When the author answers: FINDING 5J-3 ruling -> fill the two UK bracket slots (draft L64, L400) and the data statement;
      T47 result (`Prompts/deepResearch/RT47_*`) -> vet with the 7 steps, fix reference fields, add method/context sources;
      T46 result -> 8A novelty sentences; Figure 1 image -> check against its prompt section 4 + caption, record md5;
      re-run `py -3.13 tools/5thJ_valpass.py --scratch <scratchpad dir>` after every draft change (gate 1.1 cannot catch a
      wrong integer below 100: trace new small counts by hand).
   c. 8C declarations and 8D venue wait on the author (below); 8A novelty waits on the T46 search and Li 2021.
   d. After each: this §4/§5, memory line, Progress Log, board (back up, read + diff live page, syntax check on Speed: extract the page script, scp to `/speed-scratch/o_iseri/5J/board/`, `sbatch --parsable board_check.sh`, read `check_<id>.out`; republish
      v38+; routine in memory `feedback_board_live_artifact_is_master.md`).
   Author items (cannot be done by the manager; keep as ONE decision in replies = FINDING 5J-3): FINDING 5J-3 ruling (UKDS);
   run `Prompts/deepResearch/T46_novelty_logged_search_P1_P4.md`; Li 2021 full text; ASHRAE G14 2014 edition; lighting; venue
   (O-6); UK line (Step 1).
1. UK arrays are ON HOLD (FINDING 5J-3) and wait on the author's UK household script (`tools/5thJ_design_households_uk.py`) and the UKDS 5J line. Author to check
   the ASHRAE 2014 edition clause (amendment only if it differs).
2. After every step: Progress Log entry, this §4/§5, memory line, board (read + diff live page, syntax check,
   republish). Run `date` before every stamp. The previous version of this file is in
   `Prompts/manager/archive/5J_manager_prompt_RESUME_2026-10-01_1315.md` (older §4/§5 items, for the record).
## §6. Lessons carried (full list in the checklist, 16 items)

Clock origin (4J diaries start 04:00, Spain 06:00: rotate to midnight); same input can give different
EnergyPlus output (noise floor from replicates); heating effect tiny (expect the claim in electricity and
peaks); only geometry-ordered effects survived (score per dwelling class); right level per statistic;
exit 0 is not proof; cache keys on every input; one working directory per run; right meters; preflight
with pinned inputs; `--exclude=antenna1`; weather moves more than occupancy; laundry lives in secondary
activity; leakage from country-only fields; bootstrap by building and household; gates seen failing.

## §7. Open decisions (one line each; the full text is in the Overview)

O-3 campaign size RULED 09-30 16:16 + design FROZEN 16:38 (Spain 4,768 + Italy 4,501 runs) · O-4 input window RULED 09-30 20:10 (168 h + 24 h, per flat, EnergyPlus inputs only; `Step5_docs/outputs_step5/step5_rules.md`)
· O-5 CPU share RULED 09-30: 30 CPUs; RE-RULED 2026-10-01 16:48: 5J up to 32 Speed CPUs, OpenUBEM up to 32, at the same time (same account), desktop up to 10 if needed · O-6 venue (after RQ1 and RQ2) · O-7 how UK aggregate
gate results reach the manager (recommend: the author asks UKDS for written permission) · k dwellings per floor
for MFH/AB (TABULA count, else manager) · COP 3.0 ASSUMED (author may change) · lighting schedule (ask if absent).
