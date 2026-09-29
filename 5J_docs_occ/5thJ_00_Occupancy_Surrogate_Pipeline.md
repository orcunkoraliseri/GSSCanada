# An Occupancy-Aware Surrogate for EnergyPlus
### HETUS diaries (Spain, UK, Italy) -> schedules -> paired EnergyPlus campaign -> learned surrogate scored on the occupancy effect
#### Paper 5 of the series — the build checklist

Written 2026-09-28. **This is the checklist to create the project, and its Progress Log is the
state.** The one-page picture is `5thJ_00_Occupancy_Surrogate_Pipeline_Overview.md`; the board is
`5thJ_CHECKLIST.html`. Tick a box only when the artefact exists on disk and was re-derived by the
manager, never on an employee's word. Edit in place; never fork a copy.

Legend: `[x]` done and reviewed · `[~]` exists but part void · `[ ]` not started · 🔴 read first.

---

## AIM
Train a fast stand-in for EnergyPlus that predicts hourly heating, cooling and electricity from an
occupancy sequence, a building description and the weather, using a paired campaign in which only
the occupancy varies. Score it on the load **and** on the occupancy effect (the difference between two
households in the same building), with an occupancy-blind control that must fail. Research questions
RQ1 to RQ4 are in the Overview.

## WHY THIS PAPER, STATED SO IT CAN BE ATTACKED
* **"EnergyPlus is fast enough for one building."** True. The surrogate is for the stock: 100,000
  occupancy draws over a district (RQ4), which EnergyPlus cannot do in the time we have.
* **"A surrogate of EnergyPlus is already known."** Yes (Li, Bae and Im 2021; Pan et al. 2024; Govindarajan et
  al. 2025; none takes occupancy as an input, as far as read).
* **"Scoring a surrogate on differences is known."** Yes: Park and Park 2023 (retrofit savings). It is cited as
  the source; the new part is the occupancy version with a blind control.
  Our test is whether it keeps the **occupancy effect**, which is small next to the load; the blind
  control shows that a high load score alone proves nothing.
* **"The truth is a simulation."** Yes, and the paper says so. The claim is fidelity to EnergyPlus,
  not to meters.
* **"Someone coupled stochastic occupancy to EnergyPlus already."** He et al. 2015 and Dabirian et al.
  2024 did; both run EnergyPlus directly and train no surrogate (read at source 2026-09-28,
  `Resources/nearest_work/NEAREST_WORK.md`). He et al. show that one house gives different demand under
  five occupancy profiles but never score that difference; they are cited as the paired-design precedent.

## 🔴 LESSONS CARRIED FROM 1J TO 4J (read before building anything)
Collected 2026-09-28 by a read-only sonnet sweep of the four journals and the lessons memory; the
passages were read, the numbers not re-derived. Each line: the lesson, then what 5J does.

1. **Clock origin.** 4J diaries start at 04:00 (Spain 06:00); EnergyPlus reads from midnight, so all
   13,108 4J Step 8 runs were 4 h early. 5J: `rotate_to_midnight()` once per year, origin stamped in
   every run manifest (`4J_docs_occ/tools/4thJ_step7_schedules.py:120`; `Step8_docs/4thJ_08_bemSimulation.md:1530-1545`).
2. **🔴 Same input, different output.** In 4J, identical IDF, weather and binary gave up to 8 heating
   values over 10 replicates on OpenUBEM real-geometry cells; fold aggregates held. 5J: replicate runs
   in the campaign set a **truth noise floor**; no effect or surrogate error is scored below it
   (`4J_docs_occ/messages_OpenUBEM/2026-08-28_4J_to_OpenUBEM_FINDING181_arms_1_2_3_results.md:40-130`).
3. **Heating effect is tiny.** 4J annual heating effect was under 0.5 %, below the between-diary
   spread; peaks and timing moved more, and the sign flipped in Italy. 5J: score per end use; expect
   the claim to live in electricity and peaks; heating may be NOT_EVALUABLE, and that is reported
   (`4J_docs_occ/writing/4thJ_crossStep_analysis.md:119-160`).
4. **Only geometry-ordered effects survived** (apartment block > multi-family > terraced). 5J: score
   the occupancy effect per dwelling class; never pool (`Step8_docs/4thJ_08_bemSimulation.md:1570-1585`).
5. **Right level for each statistic.** A population statistic scored per dwelling gave 320 false
   FAILs. 5J: each metric states its level (run, pair, population) (`4thJ_08_bemSimulation.md:1594-1598`).
6. **Exit 0 is not proof.** 2J never wired the work-from-home schedule into the IDF; 3J scenarios were
   byte-identical over 56 cells; a 4J rerun was bit-identical because a helper skipped `build()`. 5J:
   check that outputs **differ** between households, and every patch prints a line that is checked.
7. **Cache keys and resume.** 3J F8 and a 4J cache were keyed on too few inputs. 5J: key on every
   input by hash; prove MISS, HIT, and key-moves-on-change; resume check moves outputs away.
8. **One working directory per run.** ReadVarsESO files collided between workers in 4J. 5J:
   `cwd=run_dir`; a fallback that only warns is a crash (`Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:556,833`).
9. **Right meters.** 2J counted heat-recovery transfer as cooling. 5J: targets read from the right
   meters, and plausibility checked before targets are frozen (`2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md:281-286`).
10. **Preflight, pinned inputs, geometry failures.** 4J Madrid lost 84 buildings to geometry faults.
    5J: one preflight with inputs pinned by hash; a failing building is dropped for the whole pair.
11. **Speed.** Ask slightly under the CPU cap (`AssocGrpCpuLimit`); node antenna1 truncated outputs in
    1J, so `--exclude=antenna1`; per-task size or md5 check; disk preflight; raw EnergyPlus output
    deleted once hourly series are extracted (`1J_docs_occ/Prompts/1J_manager_prompt_RESUME.md:11-18,47`).
12. **Weather moves more than occupancy** (station alone 5 to 11 % in 4J). 5J: weather is part of the
    frozen frame; never compare absolute loads across weather bases.
13. **Laundry lives in secondary activity** (26 % of diary minutes). 5J: electricity schedules use
    secondary activity too; a mean-scale check fails when a load is doubled (`4thJ_crossStep_analysis.md:189-239`).
14. **Leakage.** Fields only one country records leak country identity. 5J: identical encodings across
    countries; split unit = household and building, never run.
15. **Bootstrap by cluster** (building, household), never by hour or run; simulate the null under the
    real sampling design; when a sign contradicts the mechanism, suspect the method first.
16. **Gates.** Three outcomes (did not run / ran, did not fire / fired) in the SUMMARY and the exit
    code; an empty population is NOT_EVALUABLE; a band is used only after its source is opened; a gate
    is retired only after a replacement detector exists.

Reusable 4J tools (all in `4J_docs_occ/tools/`, the author's own sole-author work):
`4thJ_step7_schedules.py` (diary to `Schedule:File`, `rotate_to_midnight`, `household_year`),
`4thJ_step7_indoor.py`, `4thJ_step8_tabula.py` (TABULA parameters es, uk, it), `4thJ_step8_idf.py`
(archetype IDFs, 88 built, 0 severe), `4thJ_step8_weather.py`, `4thJ_step10_weather_year.py`,
`4thJ_step8_chaining.py`, `4thJ_step8_scenario.py` (cache key), `4thJ_step9_mapping.py`
(activity to appliance), `4thJ_step10_paired.py`, `4thJ_step10_nocore_campaign.py` and
`4thJ_step10_nocore_preflight.py` (campaign runner and guard), `4thJ_step10_eu08_driver.py`.

## STEP 0 — DECISIONS, LICENCES, NOVELTY (week 1: 29 Sep to 4 Oct 2026)
- [x] Subject ruled: D-5J-6 = form B4, occupancy-aware simulation surrogate (author, 2026-09-28).
- [x] Sole author; no co-authored input (no 2J generator, no 1J to 3J runs, no CENTUS model).
- [x] Old 5J folder renamed `0_New_Ideas` (all ideas kept); this folder created fresh.
- [x] 🔴 O-1: HETUS agreement for each country read (Spain, UK, Italy); a country whose terms do not allow a new paper is dropped and the drop recorded.
  - 2026-09-28 read. **Spain (INE): OK.** Open download, CC BY 4.0; derived and commercial use allowed; cite "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es"; do not suggest INE endorsement.
  - **Italy (ISTAT): OK.** The held file is the public-use file ("File ad uso pubblico", `uso_tempo_2013_IT.zip`, `!Leggimi.html`), not a per-project research file, so it is not tied to paper 1; ISTAT content is CC BY 4.0 (legal notice) unless stated otherwise; cite the source and say changes were made. The conditions accepted at download were not saved on disk: re-read them once on the mIcro.STAT page.
  - 🔴 **UK (UKDS SN 8128, EUL v16.00, 25 Feb 2026): usable, but three actions first.** (a) Clause 2: use only for the purposes declared in the registered Project Information; 5J is a new purpose, so **add a 5J project in the UKDS account and attach SN 8128** (or get permission) before any UK run. (b) Clause 4: no access to the data or any derived dataset, synthetic ones included, except to registered users, so **UK-derived schedules, campaign outputs and surrogate weights are not released publicly**. (c) 🔴 Clause 5: **no online data tools, generative AI included, "in connection with" the data without written permission from UKDS**: the assistant never opens UK diary rows or UK-derived files; code is written against the data dictionary and run by the author or a batch job. Also: clause 11 cite Sullivan and Gershuny (2023) and acknowledge; clause 12 send UKDS the paper's bibliographic details; clause 18 destroy copies and derived datasets at the end of the access period.
  - Decision for the author: keep the UK (after registering the 5J project) or run 5J on Spain and Italy only. Recommend keep, register today.
  - ✅ **RULED 2026-09-28 by the author: the UK stays in ("UK is okay as far as i know").** Not verified by the manager: the wording of the Project Information in the author's UKDS account (clause 2). Clauses 4 and 5 hold whatever that wording says: no public release of UK-derived outputs or weights, and the assistant never opens UK data rows or UK-derived files.
- [x] O-2: He et al. 2015 (BS2015, `10.26868/25222708.2015.2655`) and Dabirian et al. 2024 (`10.1007/978-981-97-8309-0_1`) read at source, neither trains a surrogate; Li, Bae and Im 2021 (`10.2172/1817464`) abstract read only (osti.gov unreachable; sensor-fault surrogate, 107 inputs not listed, low risk); nearest-work table `Resources/nearest_work/NEAREST_WORK.md` (6 rows). Outside search RT45 vetted 2026-09-28 (`Prompts/deepResearch/VETTING_RT45.md`: mixed; Park and Park 2023 kept as the difference-score precedent). ✅ **CLOSED 2026-09-28 by the author** ("yes please"): Li 2021 accepted at abstract level; full-text re-check at Step 8. Still owed before the manuscript says "first": one logged search for P1 and P4 (Step 8).
- [ ] O-5: Speed CPU share agreed while 1J draws finish; `squeue` read before the first submission.
- [ ] Venue left open until RQ1 and RQ2 results exist (O-6).

## STEP 1 — WP0: INVENTORY OF WHAT 4J ALREADY BUILT (sonnet employee, read-only)
Spec `Step1_docs/5thJ_01_wp0Inventory.md`; validation `Step1_docs/5thJ_01_wp0Inventory_val.md`.
Task doc `impl/<date>_wp0_inventory.md`. Data outside the repo, in `GSSCanada\_5J_data\` (new
subfolder `surrogate\`; the old permit data there stays untouched).
- [x] HETUS files located, row counts and checksums written (Spain, Italy: all equal the 4J records). **UK: WAITING ON AUTHOR** (one line in the Step 1 spec; UKDS clause 5).
- [x] 4J diary-to-schedule path located: presence, activity-driven equipment and lighting, hot water (Step 9), and the day-to-year chaining rule as ruled in 4J (independent, seed 1); schedule time origin checked (all diaries harmonised to 04:00, `rotate_to_midnight` cyclic over the year). 4J ignores secondary activity (Step 2 adds it).
- [x] 4J TABULA archetype IDF builder located (88 archetypes: es 24, uk 32, it 32); it takes one TABULA-derived dict, is heating only and writes no meters (Step 2, 2F).
- [x] 4J ERA5 weather files located: Madrid 2009/2010, London 2014/2015, Bologna 2013/2014 only; Step 8 used TMYx typical years for Valencia, Birmingham, Torino (Step 2, 2F).
- [x] OpenUBEM campaign entry point located; EnergyPlus 23.1.0-87ed9199d4 (local and Speed); Step 8 IDFs declare 24.2 (Step 2, 2F).
- [x] Manager re-derives one number from each item (2026-09-28 night: all five equal; gates 1.3 and 3.1 pass and were seen failing; `Step1_docs/impl/2026-09-28_wp0_inventory.md`).

## STEP 2 — WP1: CAMPAIGN DESIGN AND PILOT (week 1)
Spec `Step2_docs/5thJ_02_campaignDesignPilot.md`; validation `Step2_docs/5thJ_02_campaignDesignPilot_val.md`.
- [ ] Climates chosen: about three per country (DRAFT list; ERA5 actual years).
- [ ] Building variants: Latin hypercube over insulation, glazing share, air-tightness, floor area and orientation, inside TABULA ranges; about 40 per country and climate (DRAFT).
- [ ] Households: about 60 diary households per building (DRAFT), drawn with survey weights; the **same households on every building of a country**, so every pair is a clean occupancy contrast.
- [ ] Output variables fixed: hourly heating, cooling and electricity per dwelling, from the right meters (lesson 9); annual sums checked against the hourly sums.
- [ ] Replicate runs planned (same input run several times, lesson 2) to set the truth noise floor.
- [ ] Electricity schedules include secondary activity (lesson 13); clock rotated to midnight (lesson 1).
- [ ] Pilot: 50 runs on Speed (`sbatch`, 7-day walltime); time per run and output size measured and written.
- [ ] Campaign size set from the pilot (DRAFT ~21,600 runs), inside the CPU share and the disk quota; plan count written before submission.

## STEP 3 — WP2: FULL CAMPAIGN ON SPEED (CPU, week 2: 5 to 11 Oct)
Spec `Step3_docs/5thJ_03_fullCampaign.md`; validation `Step3_docs/5thJ_03_fullCampaign_val.md`.
- [ ] `sbatch` arrays submitted, job IDs in `impl/<date>_wp2_campaign.md` (ledger append-only).
- [ ] G5J.1: every planned run present, "EnergyPlus Completed Successfully", 0 severe errors, output rows = 8,760; a run that exited 0 but wrote nothing is caught.
- [ ] Resume check tested: outputs moved away, plan count seen to drop.
- [ ] Outputs seen to differ between households on the same building (lesson 6); one working directory per run (lesson 8); `--exclude=antenna1`, disk preflight, raw output deleted after extraction (lesson 11).
- [ ] Splits written and **sealed** (read-only, checksum in this doc): development, validation, test-new-households, test-new-buildings, test-new-country (leave one country out). Households and buildings never cross splits.
- [ ] No model sees a test file before Step 4 is ticked.

## STEP 4 — FREEZE THE GATES (before any test row is scored)
Spec `Step4_docs/5thJ_04_freezeGates.md`; validation `Step4_docs/5thJ_04_freezeGates_val.md`.
- [ ] Overview gate thresholds turned from DRAFT to frozen; checksum written here.
- [ ] Perturbation table: one named perturbation breaks exactly one gate.
- [ ] 🔴 Each gate seen failing: G5J.1 (delete one run's output), G5J.2 (predict the training mean), G5J.3 (shuffle occupancy = control C), G5J.5 (shift predictions by 2 h).
- [ ] What the exit code and the SUMMARY line mean is written down; a crashed section is NOT_EVALUABLE, never PASS.
- [ ] Noise floor for G5J.3 set from the replicate runs (same input, lesson 2); any end use whose occupancy effect sits below it is NOT_EVALUABLE for G5J.3, reported per dwelling class (lessons 3, 4).

## STEP 5 — WP3: BASELINES AND SURROGATE (GPU, week 3: 12 to 18 Oct)
Spec `Step5_docs/5thJ_05_surrogateTraining.md`; validation `Step5_docs/5thJ_05_surrogateTraining_val.md`.
- [ ] B0: average-schedule baseline (predicted occupancy effect = 0).
- [ ] B1: gradient-boosted trees on hourly features (current and lagged occupancy, weather, building), CPU.
- [ ] S: sequence model (two families tried, for example temporal convolution and Transformer encoder), 7-day history in, next 24 h out (O-4), on one A100; chosen on the validation split only; winner pinned (code hash, seed, checkpoint checksum).
- [ ] C: model S retrained with occupancy shuffled across runs (the blind control).
- [ ] Training logs, loss curves and GPU hours written to the impl doc.

## STEP 6 — WP4: ONE SCORING OF THE SEALED TEST SETS (RQ1 to RQ3, week 4: 19 to 25 Oct)
Spec `Step6_docs/5thJ_06_sealedScoring.md`; validation `Step6_docs/5thJ_06_sealedScoring_val.md`.
- [ ] G5J.2 load accuracy on new households and new buildings, per target.
- [ ] G5J.3 occupancy effect on paired differences; bootstrap resamples **households and buildings as clusters**, not hours.
- [ ] G5J.4 control C fails G5J.3; if not, G5J.3 is withdrawn and the paper says so.
- [ ] G5J.5 daily peak hour; thermal-mass lag read from cross-correlation of presence and heating.
- [ ] G5J.6 leave-one-country-out scores reported.
- [ ] Every number re-derived by the manager from the scored files.

## STEP 7 — WP5: WHAT THE SPEED BUYS (RQ4, week 4)
Spec `Step7_docs/5thJ_07_speedDistrict.md`; validation `Step7_docs/5thJ_07_speedDistrict_val.md`.
- [ ] One European district from OpenUBEM chosen (dwelling-level, no-core rule).
- [ ] 100,000 occupancy draws run by the surrogate; district demand spread (median and 90 % interval).
- [ ] EnergyPlus run on a random subsample of the same draws; surrogate error there reported.
- [ ] G5J.7 time per dwelling-year, surrogate against EnergyPlus on the same node.
- [ ] 🔴 GPU work finished and checkpoints copied off Speed before access ends (about 31 Oct 2026).

## STEP 8 — WRITING (after the GPU window; no GPU needed)
Spec `Step8_docs/5thJ_08_writing.md`; validation `Step8_docs/5thJ_08_writing_val.md`.
- [ ] Nearest-work rows re-checked at source, including Li, Bae and Im 2021 in full (its 107 inputs), and one logged search (queries saved) for P1 (occupancy sequence as surrogate input) and P4 (time-use diaries feeding a learned energy model) before the word "first" is written.
- [ ] Figures: only data plots computed by script from frozen data; image prompts for any drawing (never draw).
- [ ] Manuscript in the 2J AE style; limitations written as limitations; gate verdicts stay as recorded; no LLM or tool name outside the AI declaration.
- [ ] Venue chosen (O-6); declarations for a sole author (no grant unless one applies).

---

## VALIDATION PLAN
Gates G5J.1 to G5J.7 in the Overview. No test row is scored before Step 4 is ticked. A gate counts
only after it has been seen failing.

## KEY DESIGN DECISIONS
See the Overview table. Long-lived decisions go in this doc; per-task state goes in
`impl/<YYYY-MM-DD>_<task-slug>.md`, one file per task, ledger append-only.

## OPEN DECISIONS
O-1 (HETUS licences, closed), O-2 (novelty, closed), O-3 (campaign size), O-4 (input window),
O-5 (CPU share), O-6 (venue), O-7 (how UK aggregate results reach the manager).

## LIMITATIONS
Pointer to the Overview; new ones are added to the Progress Log as they arise.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): subject ruled B4 by the author; old folder renamed `0_New_Ideas`; this
  checklist, the Overview and the board created on the author's request. Nothing submitted, nothing
  running. Next: Step 0 (licences O-1, novelty O-2).
- 2026-09-28 (manager): 16 lessons from 1J to 4J added (sonnet sweep, passages read, numbers not
  re-derived); campaign now carries replicate runs for a truth noise floor, and G5J.3 is scored per
  end use and per dwelling class.

**2026-09-28 (board published).** `5thJ_CHECKLIST.html` published as the 5J board:
https://claude.ai/artifact/Po6gPXs5daYghKhRK3bNzH (Version 1; script syntax-checked before publish; 50 items, 3 done).
Republish the same file after every step; read the live page first.

**2026-09-28 (O-1 licences read).** Spain and Italy allow the new paper under open licences (CC BY 4.0). The UK allows it
only after a 5J project is registered in the UKDS account; UK-derived outputs and weights stay private, and no online AI
tool may touch UK data without written UKDS permission (EUL v16.00 clauses 2, 4, 5). Sources: UKDS EUL PDF
(`ukdataservice.ac.uk/app/uploads/cd137-enduserlicence.pdf`, read in full), `ldJson_8128.json` in
`_local_runs/4J/raw/uk/unpacked/UK-TUS/` ("Commercial use ... requires approval"), INE legal notice
(`ine.es/dyngs/AYU/index.htm?cid=125`), ISTAT legal notice (`istat.it/en/legal-notice/`), `!Leggimi.html` in the Italy zip.
Not verified: the exact ISTAT download conditions page; the end date of the author's current UKDS access period.
O-1 stays open until the author registers the UK project or drops the UK.

**2026-09-28 (O-1 closed by the author; 4J records checked).** The author ruled that the UK stays in; all three countries
go forward. Carried rules: UK-derived outputs and weights are never released publicly; the assistant never opens UK data
rows or UK-derived files (EUL clause 5); cite and acknowledge each source; send UKDS the paper's details after publication.
4J records read (`4J_docs_occ/Step1_docs/4thJ_01_corpusAcquisition.md:64-67`, `outputs_step1/acquisition_manifest_uk.json`):
(1) UK SN 8128 was downloaded by the author in person on 2026-08-14 under the EUL, for the 4J project; 4J recorded the
licence name only and never read the terms (`licence_note`). (2) Italy was "HELD already from paper 1" and hand-delivered;
the file itself is ISTAT's free public-use file, so for a sole-author paper the author should download it again in their
own name from ISTAT and compare the md5 with the held copy (cheap; removes any link to the co-authored paper).
(3) 🔴 In 4J, assistant employee sessions unpacked, hashed and parsed the UK files directly (Step 1, 2026-08-15). EUL
v16.00 (25 Feb 2026) clause 5 bans online AI tools in connection with the data without UKDS written permission. This is
flagged to the author for 4J; it is not a 5J step and nothing in 4J was changed.
Next: O-2 (nearest work read at source).

**2026-09-28 (graphical abstract draft reviewed).** The author's outside tool built a draft from
`Prompts/5thJ_graphical_abstract_prompt.md`: a plotting-script version (`figures/5J_graphical_abstract.{pdf,png,tiff}`,
script `figures/scripts/generate_5J_graphical_abstract.py`, byte-identical copy in `../tools/`) and an image-generator
render (`figures/5J_graphical_abstract_gemini.jpg`). All four image files are also copied into `Prompts/` (about 23 MB of
duplicates). Review by eye, against sections 3 to 6 of the brief:
Plotted version = usable design-stage draft. Size 2656 x 1062 (meets the 1062 x 2656 aim); words match the permitted list;
Panel C is the empty frame the brief asks for; no invented numbers. To fix: (a) the five day strips and five load curves
are unevenly spaced (big gap before the fifth); (b) the arrows are only arrowheads, no lines run into or out of the house;
(c) the crossed-out strip uses red, which is not in the palette (use mid grey); (d) smallest text is 7 pt, brief prefers 8;
(e) panel widths about 29 / 37 / 33 % vs the brief's 35 / 30 / 35; (f) some gaps are near touching (reported minimum
0.53 pt).
Image-generator version = not usable as is. It repeats "Time-use diaries: Spain, Italy, UK" and "Only occupancy changes"
(extra words, section 8 rule); its canvas is about 1.8 : 1, not 2.5 : 1, and leaves no room for Panel C; it is a JPEG,
not vector. If any part of it is used, the tool must be named in the AI declaration only.
Nothing deleted. Whether to remove the duplicate copies in `Prompts/` and `../tools/` is the author's call.
Next: O-2 (nearest work read at source).

**2026-09-28 (duplicates removed; fix list written).** On the author's request: the four image copies in `Prompts/` and
the script copy in `../tools/` were deleted after `cmp` showed them byte-identical to the originals in `figures/`. The
drawing fixes are written as a prompt (brief section 9: even spacing, visible arrows, grey cross instead of red, 8 pt
text, panel widths 35/30/35); the assistant does not edit or run the drawing script itself (never-create-images rule).
Next: author runs the section 9 fix; then O-2.

**2026-09-28 (graphical abstract draft 2, fixes applied by the assistant at the author's request).** The author asked the
assistant to run the section 9 fixes itself ("of course lets go run"), a one-off exception to the never-create-images
rule for this plotting script only. Draft-1 script kept at the session scratchpad (`generate_5J_graphical_abstract_draft1.py`).
Changes in `figures/scripts/generate_5J_graphical_abstract.py`: five equally spaced rows (strips and curves); arrows drawn
above shapes with no shrink, fanning into and out of the house walls; cross over the shuffled strip now mid grey
#64748B (no red); all text 8.0 pt, titles and bottom line 8.3 pt; the Panel C y-axis label moved above the frame
(horizontal); outputs now written to `figures/` only (no copies to `Prompts/` or `../tools/`).
Run output (read, not assumed): 24 text items all on the permitted list; smallest font 8.00 pt; clearance check 0
problems, smallest gap 1.01 pt, covering 24 texts, 16 lines, 17 arrows, 156 other shapes; image 2656 x 1062.
Check seen failing: two planted overlapping labels produced 8 problems (caught).
Deviation from the brief: panel widths are 31 / 40 / 30 %, not 35 / 30 / 35, because Panel B's one row of tag, box and
tag needs about 39 % of the width at 8 pt. The author may prefer 7.5 pt to get closer to the brief's split.
Next: O-2 (nearest work read at source).

**2026-09-28 (O-2, nearest work downloaded, 1 of 3).** Saved to `Resources/nearest_work/`:
`He2015_BS2015_2655.pdf` (IBPSA proceedings, open, 8 pages; title checked: "Coupling a stochastic occupancy model to
EnergyPlus to predict hourly thermal demand of a neighbourhood"). Not downloaded: Li, Bae and Im 2021 (ORNL report,
"Surrogate Model of Flexible Research Platform EnergyPlus Models to Enable Sensitivity Analysis"): its only copy is on
osti.gov, which does not connect from this machine (timed out in curl and PowerShell); Dabirian, Alamatsaz and Eicker 2024
(Springer chapter, "Enhancing Urban Building Energy Simulations: Advanced Evaluation of Stochastic Occupancy Models with
Real Occupancy Data"): closed access, no open copy found. Author to save both into the same folder (browser; Concordia
library for the Springer chapter). Nothing read yet.
Next: author saves two PDFs; then read all three.

**2026-09-28 (O-2, two of three read; outside search T45 written).** The author supplied the IBPC 2024 volume
(`Resources/nearest_work/Dabirian2024_book_978-981-97-8309-0.pdf`, chapter on PDF pages 19-28) and could not open the
ORNL report in the browser either. Both available works read in full: **neither trains a surrogate.** He et al. 2015
run EnergyPlus directly with Markov-model heating hours (heating only; one house under five occupancy profiles gives
different demand, shown but never scored; the paired-design precedent to cite). Dabirian et al. 2024 learn an office
occupancy generator from campus electricity (k-means plus Gaussian mixture) and score occupancy counts, not energy.
Li, Bae and Im 2021 stay unread; the earlier RT43 row for it gave wrong authors (Han Li, Seungjae Lee), so its
"fixed schedules only" is not evidence. Table: `Resources/nearest_work/NEAREST_WORK.md`. Stale lines corrected in the
Overview (known neighbours, O-2) and in this file ("R2 0.99 ... Li 2021" removed: never read). On the author's request
("if needed create deep research prompts"): `Prompts/deepResearch/` holds `00_MASTER_BRIEF_5J.md`,
`_RESPONSE_TEMPLATE.md` (copied from the New Ideas series, path changed) and `T45_occupancy_aware_surrogate_prior_work.md`
(five parts of the claim P1 to P5; K1 and K2 are controls we hold in full; K3 asks for a file link to Li 2021 and its
input list quoted). Nothing running.
Next: author runs T45; manager vets RT45.

**2026-09-28 (O-2, outside search RT45 vetted: mixed).** The report (`Prompts/deepResearch/RT45_*`) came back
the same evening; vetting in `Prompts/deepResearch/VETTING_RT45.md`. Both controls pass: its He 2015 and Dabirian
2024 descriptions match our full texts. All 12 DOIs are real, with matching titles and authors. Kept after checking
at source: Park and Park 2023 (JBPS, abstract: low-RMSE surrogates "failed to adequately predict the causal
relationships", i.e. retrofit savings), **the precedent for our difference score**, so the claim becomes its
occupancy version with a blind control; Pan et al. 2024 (full text, eScholarship copy saved to `Resources/nearest_work/`:
"the weather variables were the features") and Govindarajan et al. 2025 (abstract: 23 variables, occupancy not named)
as hourly stock-scale surrogates with no occupancy input. Li, Bae and Im 2021 abstract now read (OpenAlex carries the
OSTI abstract): sensor-fault surrogate of one ORNL test building, "107 input variables" not listed, 4,000 runs; risk
low, input list unread. Rejected: every "nobody has / never" verdict (the page log has 20 lines and not one search
query), "opened in full" for three papers seen only as registry records, two wrong citation fields (Barnes pages,
Pan volume), two dead or walled Section F links. Nearest-work table now 6 rows; Overview neighbours and O-2 updated.
Not verified: CityTFT 2025 (title only), the Vosoughkhosravi review (unread; the report's P4 "never" rests on it).
Nothing running.
Next: author decides O-2 closure; then Step 1 (WP0 inventory).

**2026-09-28 night (O-2 closed; step docs and handover written; Step 1 inventory done).**
The author closed O-2 on the Li 2021 abstract ("yes please"; full-text re-check and one logged P1/P4
search owed at Step 8) and said no confirmation is needed for planned steps. Written: spec and validation
plan for every step (`Step1_docs/` to `Step8_docs/`, each `5thJ_0N_<name>.md` + `_val.md`), and the
handover `Prompts/manager/5J_manager_prompt_RESUME.md`. New open decision O-7 (how UK aggregate gate
results reach the manager). Step 1: a Sonnet employee wrote `Step1_docs/outputs_step1/wp0_inventory.md`
and `.json` (65 facts, 13 4J findings, 9 flags); Spain and Italy raw md5s, line counts and episode rows
(430,754 and 1,077,657) all equal the 4J records. Manager re-derived one number per item (DIARIO1 19,295
lines; schedule 8,760 hours, day 1 = 20.67 h present; ES01 IDF window U 5.35 = manifest, Version 24.2, no
meters; Madrid 2010 EPW header ERA5; Madrid run err file EnergyPlus 23.1.0-87ed9199d4): all equal.
Gates 1.3 (md = json, 67 paths) and 3.1 (no UK file opened: employee transcript grepped, only two
`ls -l`) PASS, each seen failing on a planted line. UK line WAITING ON AUTHOR. The inventory changes the
Step 2 draft (Step 2 doc, new 2F): only one ERA5 city per country (D2-1, author); the 4J box builder is
heating only with no meters (D2-2); IDFs say 24.2 but only 23.1 is installed (D2-3); 4J ignores secondary
activity (D2-4); Speed episode copies differ from local (D2-5); Speed EPW location unknown (D2-6). The
4J box took about 2 s of core time per run, so CPU is not the limit. `squeue`: 1J holds 5 CPUs plus two
waiting 1-CPU scorers. Step 7 doc: district `ES-MAD-BERRUGUETE` paths filled in. Nothing submitted.
Next: author answers D2-1 (climates) and runs the UK md5 line; then Step 2 design tables and pilot tools.

**2026-09-28 late night (D2-1 climates checked; cities recommended).**
At the author's request the manager read the OpenUBEM `europeanLocations` docs (weather research DR08 §5,
the ERA5 scripts and registry) and the 4J station scores. The ERA5 download and EPW conversion work for
any city; 5J needs its own copy of two OpenUBEM scripts because they allow one city per country, take
elevation per country and fetch two years. Download time measured on the OpenUBEM files: about 6 min per
month file (Madrid) up to 18 h for 26 files (Bologna), so six city-years take about 8 h to 2 days, locally.
The 4J buildings cover one TABULA region per country (`ES.ME`, `GB.ENG`, `IT.MidClim`), so Edinburgh, Rome
and Palermo are dropped from the 2A draft. 4J's 44-station score shows Madrid (3.57) and Bologna (2.82) fit
TABULA's climate poorly. Recommended: Spain Valencia + Seville, UK Birmingham + Manchester, Italy Turin +
Milan (best-fit station plus one large city each); fallbacks Barcelona, Leeds. Written in the Step 2 doc
2F ("Checked"), the Overview D2-1 bullet, the handover prompt and the board. Nothing downloaded; nothing
submitted.
Next: author says yes to the six cities (D2-1); the manager then writes the download task first.

**2026-09-29 morning (D2-1 RULED: six ERA5 cities; weather download task started).**
Author answered "lets go" to "yes to these six cities": D2-1 = (a), Valencia, Seville, Birmingham,
Manchester, Turin, Milan (Step 2 doc 2F, "RULED 2026-09-29"). Download order Valencia, Birmingham, Turin,
then Seville, Manchester, Milan. Task doc `Step2_docs/impl/2026-09-29_wp1_weather_TASK.md` (5J copies of
the two OpenUBEM scripts in `5J_docs_occ/tools/`, per-site keys and elevations, one year, own registry;
download local and detached); state `Step2_docs/impl/2026-09-29_wp1_weather.md`. No other python was
running before the start (one CDS job at a time). Nothing submitted to Speed.
Next: employee report checked; then the building-wrapper task doc (D2-2 to D2-4).

**2026-09-29 ~11:00 (building wrapper built; four Spain test runs pass; weather download running).**
Wrapper `tools/5thJ_idf.py` (8 printed patches: version 23.1, dual setpoint 20/26 °C, hourly heating,
cooling and appliance-electricity outputs, infiltration and north axis as arguments, fixed 4J gain set to
zero, People and appliance objects per household) and trigger copy `tools/5thJ_step9_trigger_act2.py`
(secondary activity; `--no-act2` reproduces the 4J Step 9 files byte for byte). Four local Madrid runs on
`ES.ME.SFH.01.Gen.ReEx.001`: all complete, 0 severe; two households differ in all three targets; the
replicate is identical; secondary activity raises appliance electricity about 5 %. Manager re-derived
H1: heating 10,752, cooling 4,841, appliances 2,388 kWh (peak W × schedule sum = EnergyPlus). Patch
checker seen failing twice, passing once. Manager settled the act2 code-length question (2F, D2-4
detail). Open for the pilot: heat and cooling per m² look high; sensible vs total cooling to decide.
Weather: download PID 19328 running since 10:17; first zip in. Nothing submitted to Speed.
Next: implement act2 rule `prefix2_major`; design tables task; convert weather as zips land.
