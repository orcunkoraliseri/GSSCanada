# 3J improvement plan - execution doc (started 2026-09-22)

This is the working state for EXECUTING the plan
`writing/submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md` (read its Sections 5, 7, 7a).
Every agent reads THIS file first, then its own work-package section below, and writes its result to
its own implementation doc in `writing/implementation/IMP/` (named in each section). Agents never edit
the plan, `Prompts/RESUME.md`, the Progress Log (`3rdJ_paper_TASKS.md`), the board, or memory - the
manager consolidates.

Author grant (2026-09-22): all decisions answered, "do not wait my confirmation, go to the end".
Author answers are in plan Section 7 ("Author answers") and 7a. Do not ask the author anything.

## Standing rules (binding on every agent)

- Reference bands, gate verdicts and every published measured number stay FROZEN. New evidence sits
  beside them; it never re-scores them.
- The frozen arm the paper reports is described in `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`:
  cells `Leg3_4-split/Step8_docs/campaign_local_deliverable/<scenario>__<Tall|SuperTall>__<MTL|CLG>/`
  (each has `channel_hourly.csv`, `hourly_meters.csv`, `manifest.json`, `injected_resized.idf`),
  aggregate `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/` (5 tables), scorecard
  `Leg3_4-split/Step9_docs/outputs_step9_deliverable/`. 🔴 NEVER use `outputs_step8/agg/` or
  `outputs_step9/` (superseded arm; `DEFAULT_AGG` in the Step-9 script points at the wrong one).
- Re-derive every number from its file; never from a log or a doc. Name file + column for each number.
- A check must be seen failing before it is trusted (write the negative control first).
- Local Python: `py -3` only; prefix `PYTHONIOENCODING=utf-8`; write scripts to a file and run the
  file (one-liners return empty in Git Bash). No local python named `python`.
- Speed cluster (`o_iseri@speed.encs.concordia.ca`, key ssh works): `sbatch` ONLY, `-t 7-00:00:00`,
  NEVER python/energyplus/srun on the login node, tcsh login shell (`2>/dev/null` inside ssh string
  fails). Account cap is 64 CPUs: `histnu` array owns 32 - NEVER touch, cancel or resize it. 3J and 1J
  share the other 32. Before every submission run `squeue -u o_iseri` and count non-histnu CPUs;
  3J total (running + pending) must stay <= 32 minus live 1J CPUs. Submit and end your turn; do not
  poll in a loop.
- Manuscript prose: "limitation", never "failure" (gate verdicts stay FAIL in tables); journal, not
  report (no meta notes, no internal code names in prose); never create images (plots from frozen
  data are fine); deep research is external (write prompts only, never run searches for citations).
- Reply to the manager in <= 250 words: what was done, the numbers, file paths, anything anomalous.

## Work packages and status

| ID | What | Owner | Status | Output doc |
|---|---|---|---|---|
| P10 | 2030 level check (does 3J share 2J's raking defect?) | agent | DONE: DEFECT (vetted) | `IMP/P10_2030_level_check.md` |
| P10R | Fix: re-rake by labour-force status, rebuild 2022 + 2030 products on one frame, add the lights/plug standby floor, re-run 52 cells as a new sibling arm | agents + manager | phase A running | `IMP/P10R_fix.md` |
| P3 | Code-schedule (uninjected) vs injected comparison | agent | DONE (vetted; D3 re-ruled, see log) | `IMP/P3_code_schedule_comparison.md` |
| P5+P11 | Sampling procedure from code; rule/checkpoint timing from the record | agent | DONE (vetted) | `IMP/P5_sampling.md`, `IMP/P11_rule_timing.md` |
| PROMPTS | Deep-research prompts P6, P7, P8, V1, V2 | agent | DONE (V11-V14; author runs them) | `deepResearch_Resources/V<NN>_3J_*.md` + `IMP/prompts_index.md` |
| V3 | V3b plumbing check then V3a seed replicates on Speed (V3a waits for P10R products) | agent + Speed | V3b submitted (1342424/26/27) | `IMP/V3_design_and_runs.md` |
| P9a | Number sheet, first pass | agent | DONE (vetted); second pass after P10R | `IMP/P9_number_sheet.md` |
| V4 | Second tower model design note, then runs | agent | after V3b | `IMP/V4_design.md` |
| V3c | Fairer code control (dwelling occupancy schedule for apartments and guest rooms), 4 runs | agent + Speed | submitted (1342434) | `IMP/V3c_fair_control.md` |
| REWRITE | P2 -> P1 -> P4 -> P12 -> P13 on the chapter sources, then rebuild | manager + agents | stage 1 DONE (`writing/chapters_v2/`, 143 ⟦P10R⟧ markers); stage 2 numbers pass after P10R | `IMP/rewrite_log.md` |
| P14 | Journal package, cover letter, audit prompt | agent | last | `IMP/P14_package.md` |

## P10 - 2030 level check

Aim, steps, expected, test: plan Section 5 "P10". Context already found by the manager:
- 2J's defect (2J plan `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md`
  WP1): 2030 raking target built from a PRE-relink 2022 reference while the 2022 schedules came from
  the POST-relink frame, so the 2022 -> 2030 residential at-home step was +8.3 pp instead of the
  intended +1.5 pp.
- 3J's "10.51 pp" (Table 6 row "Step 6") is explained in
  `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.md` ~lines 510-600 (entry
  2026-07-30 "Lot A fix") as a population-pooled comparison with a composition shift (weekday employed
  share 94.27 % in the anchor vs 49.87 % in the 2030 frame); metric of record there is -1.91 pp (old
  file) / -0.92 pp (fixed `_v2`). Re-derive, do not trust.
- Questions to answer from files: (1) which 2030 diary file did the Step-7 injector read for the
  frozen B_central / B_cons / B_opt / sens_* cells (pre-fix `_C` md5 7c105ef3 or post-fix `_v2`)?
  Read Step-7 code + cell `manifest.json`s. (2) Which 2022 frame did Y2022 cells use for residential
  and office, and which 2022 frame did the 2030 raking target use (`IS_SYNTHETIC` filter; pre- vs
  post-relink)? (3) Weekday at-home (residential) and at-work (office) shares by hour, 2022 vs 2030
  central, from the schedule products actually injected (and from `channel_hourly.csv` people
  columns of Y2022 vs B_central cells as a cross-check). (4) Is the 2022 -> 2030 step the intended
  scenario change or an artefact of mismatched frames? Reproduce the 10.51 first.
- Verdict must be one of: HARMLESS (explain), DEFECT (size it, list every paper number affected),
  or MIXED. If DEFECT: do not fix; write the re-rake + re-run design (what files, how many cells,
  CPU-hours) for the manager.

## P3 - code-schedule comparison

Aim, steps, expected, test: plan Section 5 "P3". The uninjected code-schedule control is scenario
`Default_NECB` (4 cells). Compute for each of the 4 building-city cells, for Default_NECB, Y2022 and
B_central: per-channel peak hour (circular mean and argmax, weekday), whole-building peak hour,
coincidence factor (peak of sum / sum of channel peaks), weekday day/night ratio (define day as
08-18 h, state it), per-channel EUI (both floor-area bases the paper uses). Controls first: reproduce
the published injected values (coincidence-factor median 0.941 and the four channel peak hours
12.1 / 11.9 / 12.3 / 18.9 h and whole building ~15 h quoted in the manuscript §5.3 /
`writing/fullSet/readySubmission.md`) from `agg_peak.csv` / `step9_loadshape_peaks.csv`, and show
your reader FAILS on a deliberately wrong input. Then report the comparison table and one plain
verdict: does the survey-driven model change the timing versus code schedules (by how much), or not?
Also produce the data for one figure (CSV) and a matplotlib script + PNG/PDF at 600 dpi in
`writing/figures/` named `fig_codeschedule_vs_survey.*` (plots from frozen data are allowed; no
generated imagery). Also produce a per-channel hourly presence CSV (the four channels, by hour, per
survey cycle 2005/2010/2015/2022 and 2030 central) for the new occupancy figure, if the cell files
carry it (people / occupancy columns), plus its plot `fig_presence_by_channel.*`.

## P5 + P11

P5 steps 1-2 and P11 steps 1 and 3 (plan Section 5). P5: from the code (Step 5/6/7 scripts), state
exactly what is drawn per cell: which households/workers/customers, how many, which seed(s), one
realisation or several, whether Tall and SuperTall and MTL/CLG share the same draw. Quote `file:line`.
Also list which random elements could be re-seeded cheaply for V3a (write to `IMP/P5_sampling.md`
§"Seed handles"). P11: from the 3J record (V2-B3, Step-9 gate doc, Progress Logs, `step9_gates.json`)
give the dated order: when the retail median-in-band rule was fixed vs when retail numbers first
existed; how the shipped checkpoint was chosen and the 0.0218 Retail-F1 difference. Quote file +
line + date for every claim.

## PROMPTS

Write the deep-research prompts the author will run in Gemini (never run them). House format: copy
the structure of an existing prompt in `deepResearch_Resources/` (read two recent ones first, and the
2J equation-sources prompt `dr_2J-17` if found under `2J_docs_occ_nTemp`). Number them with the next
free V<NN> in `3J_docs_occ_nTemp/deepResearch_Resources/`. One prompt each for:
P6 (standard source for each equation, list from plan Section 2 row M2b), P7 (literature + break
Table 1 + closest competitor + fill the five "not reported" references + motivation for why timing
matters), P8+V2 (measured hourly occupancy/load data per use type, Canada or comparable; must be
independent of GSS and of the hotel SARIMA inputs), V1 (measured annual EUI for Canadian buildings by
use type - Montreal large-building disclosure, Toronto/Calgary benchmarking, ENERGY STAR Portfolio
Manager Canada medians, NRCan survey tables; must report which splits by use and access conditions).
Every prompt demands URLs/DOIs and says fabricated citations are expected to be checked. Also write
`IMP/prompts_index.md` listing them and what each unblocks.

## V3 - plumbing check (V3b) and seed replicates (V3a)

Aim: plan Section 7a. Steps:
1. Feasibility on Speed: is EnergyPlus 24.2.0 available (module or a container already used by 1J or
   2J - look in `1J_docs_occ/` and `2J_docs_occ_nTemp/` sbatch scripts and on Speed `ls` of their
   dirs, no find -R)? Does the Step-7 injector + Step-9H resize cell script run on Linux? Measure the
   per-cell run time from the local deliverable logs.
2. V3b design, written BEFORE any run: take the code (NECB) schedules the Default_NECB cells use, send
   them through the SAME injection path as the survey channels (the Step-7 injector, REPLACE mode),
   and compare with the uninjected Default_NECB run on the SAME platform. Pre-register the tolerance
   (e.g. annual site energy |rel diff| <= 1e-6 and hourly channel energy max |rel diff| <= 1e-4 -
   justify from a same-platform rerun of the uninjected cell, which measures platform/run noise).
   Negative control: a deliberately wrong schedule (e.g. office schedule shifted by 3 h) must FAIL.
   Also run the uninjected Default_NECB on Speed and compare to the local win32 deliverable to measure
   the cross-platform difference (report it; it is not a gate).
3. Submit V3b as ONE sbatch array (the 4 building-city cells x {uninjected, NECB-through-injector,
   negative control} = 12 tasks, 1 CPU each), after checking CPUs. Record job IDs.
4. V3a design (depends on P5's seed handles - read `IMP/P5_sampling.md` when it exists; if not yet
   written, derive the seed handles yourself from the Step 6/7 code): fastest design inside the CPU
   budget: target B_central + Y2022 for all 4 building-city cells x 5 seeds (40 runs) if one wave fits;
   otherwise one cell per city and tower. Pre-register what is reported (run-to-run SD and range of
   each published metric: channel EUI, peak hours, coincidence factor, scenario deltas). Submit as an
   array after V3b's jobs are in, with `--dependency=afterany:<V3b job>` if CPUs are short.
5. Write `IMP/V3_design_and_runs.md`: design, tolerance, commands, job IDs, log paths, and the exact
   check the next agent runs when jobs finish. Do NOT wait for jobs.

## P10R - fix the frame defect (Option R of `IMP/P10_2030_level_check.md` §7)

Manager ruling 2026-09-22: Option R (fix and re-run). Basis: author D1 "fix first" and the standing
grant "do not wait, go to the end"; the author also said compute is available. The frozen arm stays
untouched; the fix is a NEW SIBLING ARM, every new file beside the old one, never overwriting.
Author decision inside step 1 ("add a weekday HOME target?"): NO. Only the labour-force
stratification is added (the minimal change that removes the defect); the remaining same-frame
2030 weekday home dip (decoder residual, P10 §5) is reported as a limitation.

Names (new, sibling): Step-6 `..._C_v3.csv`; Step-7 products in `Leg3_4-split/Step7_docs/outputs_step7_P10R/`;
cells in `Leg3_4-split/Step8_docs/campaign_local_P10R/`; aggregate `Leg3_4-split/Step8_docs/outputs_step8/agg_P10R/`;
scorecard `Leg3_4-split/Step9_docs/outputs_step9_P10R/`. Scripts: copy to `*_P10R.py` beside the
original (never edit a script the frozen arm was produced by; the `eSim_*` protected files are never touched).

Phase A (agent): gates written and seen failing first (P10 §7 item 5 a-d); re-rake -> `_C_v3`;
re-assemble Y2022 (2022 real rows, `demo_assemble`), 2030 residential x3 (`demo_assemble_2030`),
2030 office (`build_office_2030_product` from `_C_v3`), 2030 retail x3 (current FINDING-7 path from
`_C_v3`); hotel products unchanged; run the Step-6 and Step-7 validators; build ONE cell
(B_central__Tall__MTL) end to end locally and time it, check its manifest names the new md5s;
write the exact command that runs the other 39 cells locally (same win32 EnergyPlus as the frozen
arm, for comparability) and END. Phase B (manager): launch the 39 cells in the background.
Phase C (agent): aggregate (pass the new aggregate path explicitly, never `DEFAULT_AGG`), Step-9
scorer into the new scorecard dir, carry-over of the 16 unchanged cells by copy, old-vs-new table
for every paper number P10 §6 lists.

## P9a, V4, REWRITE, P14

Filled in by the manager when their inputs land.

## Progress log (manager only, newest last)

- 2026-09-22: doc created; agents launched for P10, P3, P5+P11, PROMPTS, V3. Speed check at launch:
  0 1J jobs, histnu ~32 x 1 CPU running, account cap cpu=64.
- 2026-09-22: PROMPTS done. V11 (equation sources), V12 (literature, novelty, 18 refs + 5 gaps),
  V13 (measured hourly occupancy/load, independent of GSS and hotel inputs), V14 (measured annual
  EUI Canada) in `deepResearch_Resources/`; index `IMP/prompts_index.md`. Manager check: 4 files
  present (129-181 lines); 2 long dashes in V14 lines 60/106 replaced. Author runs them in Gemini.
- 2026-09-22: P5+P11 done (`IMP/P5_sampling.md`, `IMP/P11_rule_timing.md`). Manager spot-check
  PASSED on: `RESIDENTIAL_SEED = 42` at `Step8_docs/3rdJ_08D_campaign_cells.py:168`;
  `improvements/v2/3rdJ_L3_v2_implementation.md:1892,1924-1928` (rule chosen "with our numbers
  already known", 2026-08-04 night) and `:3477` (pre-registration 2026-08-05 before deliverable
  numbers). REWRITE items carried: (a) §5.2 sentence "decided in advance of the numbers"
  (`readySubmission.md:662`) is only half true -> reword: rule fixed after an earlier run's numbers
  were seen, written down before the reported runs; retail fails under either rule. (b) Montreal and
  Calgary cells of the same scenario/tower use the SAME household draw (Tall 27, SuperTall 41) and
  the same office draw; only retail/hotel differ by province -> city differences are climate +
  retail/hotel inputs, not sampling; say so in Methods and Limitations. (c) V3a seed handle =
  `RESIDENTIAL_SEED` (Step 8 + EnergyPlus only).
- 2026-09-22: P3 done (`IMP/P3_code_schedule_comparison.md`, figures `writing/figures/
  fig_codeschedule_vs_survey.*`, `fig_presence_by_channel.*`). Manager re-derivation from
  `agg_deliverable/agg_peak.csv` (`channel=="_BUILDING"`, `coincidence_factor`, `peak_hour_circular`,
  median of 4 cells): code 0.9301 / 14.621 h; Y2022 0.9402 / 14.848 h; B_central 0.9409 / 14.950 h -
  matches. Presence argmax from `agg_diurnal.csv` (all, WD, people): hotel 15 -> 22 h, office 9 -> 10 h
  in all 4 cells - matches. Figures viewed; fine.
  **Manager finding M-1 (control definition).** In the uninjected control
  (`Default_NECB__Tall__MTL/injected_resized.idf` PEOPLE objects) apartments ("HighriseApartment
  Apartment People") and hotel guest rooms ("LargeHotel GuestRoom5-7 People") use `NECB-A-Occupancy`,
  the NECB OFFICE occupancy schedule; retail uses `NECB-C`. Lighting keeps the PNNL prototype schedules
  (`ApartmentHighRise LTG_APT_SCH`, `HotelLarge BLDG_LIGHT_SCH_2013`). So the "code schedule" building
  puts residents and hotel guests on office hours; the presence reversal in P3 is partly a property of
  that control. The paper must describe the control exactly. Added validation run V3c (below).
  **D3 RULING (manager, under the author's pre-stated branch "otherwise revisit D3").** The timing
  result as framed (peak hours, coincidence factor) does NOT survive against code schedules: building
  centroid +0.16 to +0.29 h, coincidence factor 0.930 -> 0.940 (UP), annual peak 07:00 January in all
  cells under both. New lead for abstract/intro/results order: (1) survey-driven channels change WHO is
  in the tower and WHEN (hotel guests and residents at night; lower 2030 office presence); (2) that
  reaches energy only where lighting and equipment follow occupancy: office and retail intensity
  -16 to -20 % and -12 to -15 % (2022), weekday midday-to-night ratio office 7.2 -> 11.4, retail
  9.3 -> 47; (3) whole-building demand timing and coincidence stay where the prototype's plant start-up
  and lighting/equipment schedules put them - reported as a finding, and every sentence that credits
  the survey model with channel peak diversity or a coincidence factor below 1 is removed. Title stays
  (D2). Comparison stated on 2022 (does not depend on P10); 2030 column only after P10 clears.
  Manuscript number fixes for P9/REWRITE: office range 11.82 mixes all-days column (weekday min 11.88);
  building range -> 14.10-15.69; retail night 2.10 kW; control "85.45" is a constant in the Step-9 band
  text (`3rdJ_09_...py:164`) - frozen cells give median 85.36 -> use 85.36 (verdict unchanged); 0.941
  and 0.851 are 2030-central 4-cell values, say so.
- 2026-09-22: V3c ADDED (manager): fairer code control = Default_NECB with apartment and guest-room
  PEOPLE on the NECB dwelling-unit occupancy schedule instead of NECB-A, 4 cells, 1 CPU each, same
  Speed platform as V3b. Launch after the V3 agent reports (do not disturb it). Its result decides one
  sentence: whether the hotel/residential presence contrast survives against a residential-shaped code
  schedule.
- 2026-09-22: P9a + P1 + P12 done (`IMP/P9_number_sheet.md`, `IMP/P1_jargon_inventory.md`,
  `IMP/P12_consistency_facts.md`, `IMP/sentence_length_baseline.md`). 121 numbers: 76 match, 12
  mismatch, 15 not found, 18 band definitions. Manager spot-check PASSED on: (1) §5.4 retail
  "-2.42 % to -1.76 %" is the B_cons bundle, not `sens_retail_cons` (-2.10 to -1.59) -
  `step9_scenario_response.csv`, `energy_pct_vs_Bcentral`; (2) Table 7 L6 "56 of 56 wrong sign"
  has no source in the frozen arm: `outputs_step9_deliverable/step9_gates.json` S9-EUI-EXPOSURE says
  the exposure file was not found and "cannot be reported this run"; the only file is in the
  superseded `outputs_step9/` -> REWRITE drops L6's number or re-derives it on the reported arm.
  (3) 2J rejected by Building Simulation 2026-09-15 (not yet at Applied Energy), 1J rejected with
  resubmission invited by JBPS 2026-09-19 -> "under review" is stale for both. Also: eSim 2026
  conference title in 3J duplicates 1J's title; 2J cites it differently - REWRITE uses 2J's form.
  Funding spelling "Volt-Age". Hotel 2022 "+0.09 %" does not reproduce (0.12 %; agent value, not re-checked by manager).
- 2026-09-22: P10 done: DEFECT. Manager check PASSED on the code: `Step7_docs/3rdJ_07_aug_to_bem_4split.py`
  `cmd_year_2022` reads the full all-cycle stock with no cycle filter (:1057-1073, and the 08A
  docstring :119-126 records it); `assemble_2030` (:393-412) draws 2030 diaries within day type only,
  no demographic match. The Y2005/10/15 sibling products DO use cycle-real rows (08A :228), so Y2022 is
  the odd one out. Side finding carried: all 36 2030-family cells ran the office and retail 2030
  products from before the 2026-08-02 fixes. Table 6 "10.51 pp" sentence is wrong as written either way.
  RULING: Option R (see P10R section). V3 agent told to run V3b only and hold V3a for the P10R products.
- 2026-09-22: V3 agent done (`IMP/V3_design_and_runs.md`). Speed jobs: smoke 1342424 (running),
  V3b array 1342426 (pending, <= 2 CPUs because 1J holds 30), checker 1342427 (afterany). Speed has the
  exact EnergyPlus build the frozen arm used. V3a designed, refuses to run until P10R products exist.
  **F-V3-1, manager-verified:** the frozen arm ran the injector BEFORE its standby-floor fix: office,
  retail and hotel-room LIGHTS and ELECTRICEQUIPMENT carry the bare occupancy schedule. The injector's
  own notes call this a defect (`eSim/eSim_bem_utils/commercial_integration.py:384-400`, S9D-8: "office
  equipment energy fell 59 % and lighting 45 %... office EUI fell 20 % and retail 23.5 %").
  `improvements/v2/V2-E5_PREREGISTRATION.md`: the deliverable = base arm (pre-fix) + retail NECB-C + DHW
  resize; the fix (arm A, office 71.08 -> 80.03) was left out under the 2026-08-04 "stop running arms to
  move gates" direction; `audit_preG5.md:1511` still calls the fix "correct and still worth having".
  Manuscript §3.6 (`readySubmission.md:440-447`) claims floors are enforced - text does not match model.
  **RULING (manager, under D1 "fix first"):** P10R also carries the standby-floor fix; scope 40 -> 52
  cells (Y2005/10/15 re-run too; only Default_NECB carries over). Reason: it is a correctness fix the
  code itself documents, not a gate move; bands and verdict rules stay frozen, and the new verdicts are
  reported whatever they are. Consequence: P3's office/retail energy differences (the D3 lead point 2)
  were largely produced by this wiring and are re-measured on the new arm; lead point 2 is held open.
  P10R and REWRITE agents told by message.
- 2026-09-22: REWRITE stage 1 done (`writing/chapters_v2/` 13 files, `IMP/rewrite_log.md`). Manager
  check: 143 ⟦P10R⟧ markers; no long dashes; "forecast" only inside 2J's own cited title (kept);
  funding "Volt-Age". Carried to stage 2 (P13 pass): (i) prose still uses the verb "fails" about ranges
  (02_Framework:93, 03_Results:91, 04_Discussion:15, SI_additions:41) -> "does not meet"/"falls
  outside"; verdict columns keep FAIL; (ii) HTML comments (`<!-- -->`) are author notes and must be
  stripped or resolved before the build; (iii) how to show old frozen verdicts beside new numbers:
  RULING - the paper reports ONE arm, the new P10R arm, scored with the frozen bands and frozen rules;
  old verdicts are not shown in the paper (the SI states the arm change in one sentence: wiring and
  population-frame corrections before scoring); (iv) 13 [REF NEEDED] -> resolved only from the
  author's V12 Gemini result; (v) author-only: AI-declaration placeholder, NSERC grant wording.
- 2026-09-22: V3c submitted (`IMP/V3c_fair_control.md`): Speed array 1342434 (4 x 1 CPU; first try
  1342430 failed on a path bug, fixed). Apartments and guest rooms re-pointed to NECB-G (dwelling-unit)
  occupancy, values from repo tables; static diff check seen both ways (4 PEOPLE changes PASS; stray
  lights edit FIRED). Post-processing command is in the doc.
  **Disk:** local C: had 140 MB free during V3c, 9.27 GB at the manager's check. P10R campaign MOVED
  to Speed, all 56 cells (Default_NECB re-run too, one platform for the whole arm); local = one test
  cell only, raw E+ outputs pruned. P10R agent told by message; manager submits after a CPU check.
- 2026-09-22: P10R phase A done and vetted from `IMP/P10R_fix.md`: `_C_v3` (6ee73094); 10 products
  rebuilt, hotel byte-copied; gates (a) 0.3006 -> 0.4180, (b) employed weekend gaps +0.06/-0.13 pp
  (frozen -8.99/+6.48), (c) mutex, (d) manifest md5s, (e) standby floor - each seen failing on the
  frozen inputs first. Static control: live code with the frozen flag rebuilds the frozen IDF except one
  added report line. Test cell B_central Tall MTL: 398 s, deterministic; office 71.64 -> 80.20,
  retail 77.14 -> 87.27 (standby floor explains most; arm A moved office 71.08 -> 80.03).
  Phase B placement: Speed squeue at 18:55 - histnu ~32, 1J draws 30 CPUs (heavy tasks ~28 h each,
  arrays run for days), V3b 2 -> 3J has no free CPU for days. RULING: run the 56 cells LOCALLY
  (6.6 min/cell, hours not days) with a disk guard and slimmed `eplusout.sql` (C: had 5.9 GB free).
  Agent building the driver + slim-sql control. Stage tree also uploaded to
  `/speed-scratch/o_iseri/3J_P10R` (used later by V3a; P10R array NOT submitted on Speed).
- 2026-09-22 23:01 UTC: P10R local campaign LAUNCHED by the manager (background shell), 4 workers,
  disk guard 3 GB (C: 4.3 GB free at launch, 20 cores), driver `IMP/scripts/p10r_local_campaign.py`,
  logs `Leg3_4-split/Step8_docs/campaign_local_P10R/_logs/driver.log` + `driver_stdout.txt`. B-local
  vetted from the agent report: slim sql 161.7 -> 1.0 MB; full vs slim aggregation byte-identical (5
  tables); slim db missing ReportDataDictionary crashes the aggregator (control fired).
  KNOWN GAP: the kept test cell `B_central__Tall__MTL` has no `run/eplusout.sql` (deleted in phase A),
  so the driver's final aggregation will fail or skip it -> phase C first re-runs that one cell with the
  runner, slims it, then aggregates all 56 into `agg_P10R/`.
- 2026-09-22 23:38 UTC: P10R local campaign STOPPED (driver exit 120) - C: at 0 bytes free. About 8 of 56 cells ok before the stop. Cause is NOT 3J: C:/Users/o_iseri/AppData/Local/Temp/ubem_validation/fleet06b_local_2026-09-18 holds ~808 GB and ~13.4 GB was written under ubem_validation in the last 2 h (another project; not touched by 3J). 3J wrote 0.14 GB in that window. Author action needed: free disk / stop that writer. Relaunch = same command (driver skips ok cells, retries the rest).
- 2026-09-23 00:19 UTC: author freed disk (67.2 GB free). P10R local campaign RELAUNCHED, same command, 4 workers: 8 cells already ok and kept (+ test cell kept, still needs phase-C re-run), 47 to run. stdout -> campaign_local_P10R/_logs/driver_stdout_relaunch1.txt. At ~7.5 min per wave of 4 runs, about 1.5 h to finish.
- 2026-09-23 ~00:55 UTC: AUTHOR RULING: simulations run ONLY on Speed, never locally ("only continue with the cluster of speed"). Local driver + 4 EnergyPlus runs killed (0 left). Local campaign_local_P10R/ (8 ok cells) is kept only as a Speed-vs-local cross-check; the P10R arm = the Speed campaign, all 56 cells. Speed script updated (backup .bak_pre_slim): slims run/eplusout.sql after each ok cell (p10r_slim_sql.py uploaded, md5 51d6487d matches), --nice=10000 so histnu/1J always win a freed CPU; runner md5 f8916ef6 and commercial_integration.py md5 233932d7 on Speed = local. User cap is cpu=64 (sacctmgr). Submitted: test cell 0 = job 1342523; cells 1-55 = array 1342524 (%26), afterok on the test. Output: /speed-scratch/o_iseri/3J_P10R/campaign_P10R. Phase C: pull + aggregate from there.
- 2026-09-23 01:15 UTC: NEW improvement board (author asked, modelled on the 1J board): https://claude.ai/artifact/Fr1S2GUncWa3bC5QptgoKN . Source IMP/board/3J_improvement_board.html; state lives in its db doc board/progress (checks, sims bars, log) - update bars/log with ArtifactData update, republish only for layout. Older paper-tracker board 0e491191 is a separate lineage, left as is.
- 2026-09-23: P14 draft written (IMP/P14_package.md); waits on P10R numbers + author confirmations.
- 2026-09-23 00:40 UTC: P10R test 1342523 (and resubmit 1342533) FAILED in 7 s at the mirror check: speed script md5 stale in repo/mirror_md5.txt (the list the checker reads). Fixed list (63 lines: script 556bebd8, + p10r_slim_sql.py 51d6487d), uploaded to repo/ and 3J_P10R/. Chains 1342524/1342534 cancelled. Resubmitted: test 1342535 (RUNNING on speed-30, [mirror] OK, standby floor True) + cells 1-55 array 1342536 (afterok). Author closing the session; handoff = Prompts/RESUME.md top block.
