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
- 2026-09-25 00:03 UTC (09-24 evening local): AUTHOR RULING, Speed full: run P10R LOCALLY on half the CPUs. Replaces the 09-23 "Speed only" ruling for P10R; whole arm now local (9 ok from 09-23 + 47). Launched `p10r_local_campaign.py --workers 10` (stdout `campaign_local_P10R/_logs/driver_stdout_relaunch2.txt`) + RAM guard `IMP/scripts/p10r_mem_watchdog.ps1 -Threshold 80` (kills only this campaign's processes; seen firing on a dummy at threshold 1, dry and real; quiet at 99). At launch: 10 EnergyPlus running, RAM 49.6% used, C: 599 GB free. Nothing submitted on Speed.
- 2026-09-25 00:15 UTC (manager): CPU check on the local P10R run: EnergyPlus uses 9.4 of 20 cores (10 workers, half), other programs ~6 cores, RAM 54%. Author asked to run parallel work: two sonnet employees started (no EnergyPlus, one light process each, frozen arm and campaign_local_P10R untouched): (1) V3b result + cross-platform tolerance into `IMP/V3_design_and_runs.md` section 10, then `IMP/V4_design.md`; (2) V3c post-processing done LOCALLY (cluster full) into `IMP/V3c_results.md` + `IMP/data/V3c/`, cells copied to `_local_runs/3J_V3c/`. Board v13.

### 2026-09-25 00:22 UTC - V3c post-processed (local), verified
- Sonnet employee aece841612e789248 wrote `IMP/V3c_results.md` (170 lines), `IMP/scripts/v3c_compare.py`, `IMP/data/V3c/`.
- Manager re-read `data/V3c/v3c_comparison_summary.csv`: _BUILDING peak hour F 14.648 vs U 14.621 (+0.03 h), CF 0.9294 vs 0.9301 (-0.0007); hotel weekday night people F 479.1 vs U 3.15; residential F 667.1 vs U 3.67. Survey arms (frozen deliverable, Y2022 / B_central) hotel 302.8 / 331.5, residential 408.6 / 390.6. Matches the report.
- Gates: gate 1 (U vs U) ran, did not fire (0 diff); gate 2 (altered U) ran and fired (448.67, localized). Both as designed.
- Verdict (limitation wording): the hotel/residential night-presence contrast in P3 is mostly a property of the NECB-A control schedule. Feeds REWRITE stage 2 (P3 paragraph) and the P10R P3 re-run.
- P10R local: 27/56 ok at 00:19 UTC (18 new, 0 failed), RAM 51%. Board v14.

### 2026-09-25 00:26 UTC - V3b write-up + V4 design note (sonnet a9f96c6e1d2846107), verified
- `IMP/V3_design_and_runs.md` section 10 added (lines 262-415). Manager re-read the table against the doc's own sources: Tall_MTL / Tall_CLG / SuperTall_CLG PASS, SuperTall_MTL NOT_EVALUABLE (noise U2 vs U ann 2.126e-4, hr 0.5376); control fired 4/4 (ann 0.072-0.105). Overall exit 2 = NOT_EVALUABLE, as recorded 09-23.
- New: SuperTall_MTL U and U2 ran on different nodes and differ by 293,961 EnergyPlus warnings; Tall_MTL also crossed nodes and matched exactly, so node alone does not explain it. Open item V3-O1 (repeat pinned to one node), not run.
- Tolerance recorded (1e-6 ann / 1e-4 hr, noise <= TOL/10); same-platform basis; cross-platform rows stay "reported".
- Sign check (class 60, method first): effect_table computes 100*(A-B)/|B| with A=U, B=R (`scripts/V3/v3_check.py:107,152`), so + means U above R. P-b4 predicted U below R (code floors). Measured U above R in every lights/equip column (office_equip +65.56% identical in 4 cells). Formula sign is right; the mechanism is not yet explained. Open item V3-O2; do NOT carry into prose until explained. Likely links to P10 (frozen arm's schedule base), check when P10R numbers land.
- Process slip: the employee ran one `python3 -c` JSON read on the Speed login node (rule: never). Logged in section 10.6; no compute; repeat with grep. Recorded here as a rule breach.
- `IMP/V4_design.md` (185 lines): no second mixed-use tower IDF in the repo; 3 options + 3 author questions (section 7). V4 parked on the author; it does not block P10R, stage 2 rewrite or submission.
- 01:01 UTC: P10R 33/56 ok (9 kept + 24 new, counted with date filter), 10 running, 0 failed, RAM 58%. The 00:22 entry's '27/56 (18 new)' was wrong: whole-log grep counted 8 old ok lines; true was 19/56. Board v16 corrects it.

- **2026-09-25 01:08 UTC:** 38/56 P10R ok (9 + 29 new, date-filtered count), 0 failed, RAM 61.5%. RESUME.md updated in place (archived first to `Prompts/archive/RESUME.2026-09-25_pre_0108utc_status.md`): new top STATUS box with live state, the B_central__Tall__MTL fix, the ordered pipeline, V3-O2. Board v17.

### 2026-09-25 02:10 UTC - P10R campaign complete, aggregated, scored, gates (d)+(e)
- Driver b3vr4knyg: `DRIVER DONE ok=56 failed=0` (47 new + 9 kept); guard never fired (peak logged 63.2%, exited 0 when idle). First aggregate exit=1: `B_central__Tall__MTL` had no `run/eplusout.sql` and `_run1_B_central__Tall__MTL` was counted as a 57th cell. Both MOVED (not deleted) to `Leg3_4-split/Step8_docs/_archive_P10R_local_2026-09-25/`; rerun `--workers 1` (guard on): `DRIVER DONE ok=56 failed=0`, aggregate `56 / 56`, attribution closes on every cell; `agg_meta` 56 rows, 56 closed.
- Scorer drift check (class 58/59 spirit): current Step-9 scorer md5 cc2d1a9b != frozen registry e4283d83. Re-scored the FROZEN agg_deliverable into `Step9_docs/outputs_step9_P10R/_control_frozen_rescore_2026-09-25/`: loadshape + scenario tables byte-identical; eui/longitudinal/gates differ ONLY in the `band_src` text (V3-H3 note); every number and every verdict equal. So old-vs-new comparisons with the current scorer are fair.
- Step-9 on agg_P10R -> `Step9_docs/outputs_step9_P10R/` (exit 0): scorecard 18 PASS / 0 WARN / 2 FAIL / 10 INFO (frozen: 17/3/10). S9-EUI-retail FAIL -> PASS. Office median 79.5 (frozen 71.0), range 70.9-90.2, still 0/56 in band. Hotel median 263.1 (260.5), 28/56 in band, range 204.8-322.2.
- Gates (d)+(e) over all 56 (`IMP/scripts/p10r_gates_C_de_56.out/.json`): both FAIL as run, exit 1. Cause is scope, not defect: (d) BAD only on the 12 Y2005/Y2010/Y2015 cells (36 BAD lines = 12 x 3 channels), which by design read the unchanged cycle products (P10 §6 "Not affected"); independently their INPUTS_HASH_DETAIL equals the frozen arm's cell-for-cell (12 identical, 0 differ). All 44 rebuilt/other cells ok. (e) FAIL only on the 4 Default_NECB cells (0 office MXU objects: the code-schedule control injects nothing); 52/52 injected cells PASS (office Load floors lights 0.0453, equip 0.2). Gate code and bands NOT changed; the as-run verdict stays FAIL and is recorded with this scope reading.
- P3 script: `--arm P10R` option added (backup `IMP/scripts/_archive_p3_code_schedule_comparison.pre_arm_2026-09-25.py`); default mode unchanged in intent, still to be regression-checked against its own frozen outputs.

- **2026-09-25 ~03:00 UTC:** image prompts written for the author (no image made): `writing/submission/figures/Prompts_Images_v4/Figure_01_framework_simple.md` (10 boxes, 3 rows, 2J style; drop-in name Figure_01_pipeline_4split.png) and `.../Prompts_Images_v4/graphicalAbstract.md` (new lead, no numbers). Figures 2-4 (transformer, hotel side-track, dispatch) already exist at 5700-6000 px long edge, no regeneration needed.

### 2026-09-25 ~03:00 UTC - Stage 2c done; images and research reports received; three helpers running
- Stage 2b agent finished (139/143 swapped with the reproduce-old control; 12/12 negative controls did not reproduce). Manager fixed the 4 leftovers and the meaning-changed sentences, wrote V3c and V4 into the text, back matter in 2J form, Table A.1 split, self-citations as 2J, Widén reference. Detail: `IMP/rewrite_log.md` "Stage 2c". Checked: zero markers, zero en/em dashes.
- Author images: Figure 1 checked by eye, OK and installed. Graphical abstract has a stray diagonal line and the old hotel top chart; prompt updated, author to regenerate.
- Author reports RV11-RV14 received; vetting agent started (offline). P9 second-pass agent started. V3a: 10/40 done, 0 failed, 10 running (driver.log 02:50 UTC).
- Board v21. RESUME top box updated (archive `Prompts/archive/RESUME.2026-09-25_pre_0300utc_stage2c.md`).

### 2026-09-25 03:30 UTC - V3a (seed replicates) running LOCALLY on the P10R arm: interim state
- V3 code switched to P10R (backups `*.pre_P10R_2026-09-25.bak` in `IMP/scripts/V3/`): products = `outputs_step7_P10R` (md5s = P10R manifests = registry, checked on disk), standby floor ON, static reference = `campaign_local_P10R/<cell>/injected_resized.idf`.
- Static pre-check (no simulation), 4 cells: seed-42 rebuild of Y2022 and B_central = P10R IDF object for object (0/0, 8 of 8). Controls fired: seed 101 differs (27 or 41 PEOPLE objects), standby floor OFF differs (25 LIGHTS/EQUIPMENT objects). `IMP/data/V3/v3a_P10R/precheck/`.
- Runs: driver `IMP/scripts/V3/v3a_local_driver.py`, 10 at once, root `Leg3_4-split/Step8_docs/campaign_local_P10R_V3a/`. 25/40 ok by 03:26 UTC. At 03:26 the RAM guard FIRED (84.2% on 2 samples) and killed the driver and the 10 live runs. Cause: another project's job (OpenUBEM `fleet06c_harvest_2026-09-24.py`, 12 python workers, started 03:21 UTC) took the RAM; RAM stayed 75% after V3a was gone. That job was not touched. The 15 unfinished tasks (10 killed, 5 never started) are rerun by the same driver command once RAM allows; ok tasks are skipped.

### 2026-09-25 03:45 UTC - V3a stopped by the RAM guard at 25/40; partial result written
- Guard FIRED 03:26:31 UTC (84.2% RAM on 2 samples), killed the V3a driver + 10 live runs. Cause: another session's OpenUBEM `fleet06c_harvest_2026-09-24.py` (12 workers, started 03:21 UTC), not V3a. Per manager: NOT relaunched.
- Finished ok 25 (tasks 0-5, 10-19, 30-38); killed 10 (6-9, 20-24, 39); never started 5 (25-29). Resume command (only the 15) and the post-run steps: `IMP/V3_design_and_runs.md` section 11.3.
- Seed 42 reproduces the published P10R cells exactly (0 difference, hourly and aggregate) in the 6 finished cells; B_central Tall MTL/CLG not run.
- PARTIAL noise verdict (SuperTall only, 5 pairs MTL, 4 pairs CLG): office, retail, hotel, service_MEP 2030-vs-2022 EUI changes are far larger than draw noise; residential is NOT (sign flips across seeds, both cities); residential_common NOT in MTL, yes in CLG. Tall tower not yet measurable. Section 11.4; data `IMP/data/V3/v3a_P10R/partial_2026-09-25/`.

### 2026-09-25 ~04:00 UTC - Word files built, hotel description corrected, V3a paused (manager)
- P9 second pass merged (6 numbers, 5 meaning fixes); 2.5 control sentence added; 9 TRUSTED-2J references in; REF NEEDED now 15.
- Hotel channel text corrected to the code (fact trace `IMP/hotel_channel_fact_trace_2026-09-25.md`): source Government of Alberta monitor, spans AB 2011-2022 / QC 2019-2022, 2022 observed rate, 2030 = 2019 shape x recovery level (source of 0.615/0.635 unvetted: author question), SARIMA(1,1,0)(0,1,0,12) as a check only; Limitations paragraph added.
- New build script `fullSet/assemble_3J_v2.py` (exit 3 expected: Guideline 14 SI-only); both .docx built and checked on the installed files; title page + cover letter rebuilt in 2J AE form.
- Figures: data figures without titles and code labels; S1 cleaned; main Figures 2-4 and SI S2-S5 are old drafts with internal notes -> Gemini prompts written in `submission/figures/Prompts_Images_v4/`.
- V3a: 25/40 ok, stopped 03:26 UTC by the RAM guard (another session's OpenUBEM job). Partial spread written into Limitations. Waiter restarts the 15 unfinished tasks when memory is free (RESUME top box).

### 2026-09-25 ~04:45 UTC - V3a FULL result, all 40 of 40 confirmed ok
- Confirmed from every run's manifest (not just the driver log): all 40 tasks `status=ok`, `ep_return_code=0`. Full aggregation and checker rerun on all 5 seeds x 8 cells, both exit 0. Seed-42 now reproduces all 8 published P10R cells exactly (worst annual and hourly difference 0.0; 0 unmatched rows, 0 max difference in every aggregate table), including the two Tall B_central cells the partial result could not check. Largest seed-to-seed EUI spread 0.543% (B_central Tall MTL, residential); largest peak-hour spread 0.117 h (Y2022 Tall CLG, residential_common). In all four tower-city cells, the published 2022-to-2030 change in office/retail/hotel is 7.1x to 282x the draw noise (a real signal); the residential change is not (1.2x-1.7x, below the 2x bar, sign flips across seeds in every cell). Full detail `IMP/V3_design_and_runs.md` section 11.6. `--slim` SQL-shrink not run (not asked for this task; run folders and full SQLs left untouched).

### 2026-09-25 15:10 UTC - author rulings: references in, hotel 2030 levels switched to observed (36 re-runs)
- Author: "yes to both". (1) 8 verified + 6 fixed references applied by a background agent (log: `IMP/rewrite_log.md`
  "Reference fixes 2026-09-25 (author approved)"). (2) Hotel 2030 recovery levels AB 0.615 -> 0.597, QC 0.635 -> 0.610
  (observed 2023-2025 means; `IMP/author_checks_2026-09-25/item2_hotel_recovery_levels.md` section 8).
- Archive before the switch: `Leg3_4-split/_archive_pre_hotel_obs_2026-09-25/` (55 files).
- Control seen both ways: `IMP/scripts/hotel_obs_rebuild.py --control` = PASS on the old forecast (3/3 frozen md5s
  reproduced), FAIL after the anchor edit. `--write` -> new 2030 hotel CSVs in outputs_step7_P10R. lookup + s(t) md5 unchanged;
  3rdJ_06 gate scorecard identical to the archived one (2 old QC FAIL rows).
- P10R Step-7 script patched: the 2030 hotel products are built from the forecast, no longer byte-copied (2022 still copied).
- Trap: `p10r_local_campaign.py cell_ok()` ignores INPUTS_HASH. `IMP/scripts/hotel_obs_stale_cells.py`: 36 stale, 20 unchanged
  (as designed: all B_* and sens_* read the 2030 hotel CSVs). 36 moved to `Step8_docs/_archive_pre_hotel_obs_2026-09-25_cells/`.
- Driver relaunched 15:06 UTC, 10 workers, RAM guard 80 %. Dry-run plan: 20 kept, 36 to run.
- Gemini v5 figures (Figure 5 hotel, S5, graphical abstract) checked and accepted; Word files rebuilt (exit 3).

### 2026-09-25 ~17:55 UTC - hotel 2030 re-runs done (56/56 ok), numbers and figures updated, V3a 2030 re-runs started
- 36 re-runs done 17:42 UTC, aggregate exit 0. Post chain `IMP/scripts/hotel_obs_post.sh` all as expected.
- 28 of 143 printed numbers moved, all in Results + Table S2; one claim (additivity) re-worded to its measured bound
  (5.6 %, 0.12 points). Detail: `IMP/rewrite_log.md` section "Hotel 2030 observed levels: numbers and figures updated".
- Figures 5, 7, 8, 9, 10, 11 redrawn (checks 27/27); Word files rebuilt, exit 3 as expected.
- V3a: the 20 B_central repeat-seed cells re-run (the old ones were moved to `campaign_local_P10R_V3a/../_archive_pre_hotel_obs_2026-09-25_V3a`
  earlier; the pinned 2030 hotel md5 in `V3/v3_lib.py` is 30071672, matches disk). Launched 17:46 UTC, 8 at once,
  RAM guard 88 % (same watchdog process). Then: `v3a_local_aggregate.py` -> `v3_check.py v3a` -> `v3a_report_P10R.py`
  -> `05_Limitations.md:3` if its numbers move -> rebuild.
- V3a re-run done: driver `done ok=20 failed=0` 18:37:20 UTC; 40/40 manifests ok; new hotel md5 in 20/20 B_central and 0/20 Y2022
  manifests. Aggregate `outputs_step8/agg_V3a_P10R_hotel_obs` (5 seeds x 8/8 cells, residual 0), `v3_check.py v3a` exit 0,
  report `IMP/data/V3/v3a_P10R/full_hotel_obs/`: seed 42 = agg_P10R exactly (8/8, worst 0.0). Ratio office/retail/hotel
  5.4-311 (was 7.1-282), CV and peak SD unchanged, residential verdict unchanged. `05_Limitations.md:3` "7 to 280" ->
  "5 to 310". Rebuilt, exit 3 as expected. Watchdog ended on its own. Board v40. Detail: `IMP/V3_design_and_runs.md` 11.8-11.9.
  **No machine work left; author items only (see RESUME top box).**

- 2026-09-25 ~19:15 UTC: B&E format pass + last citations done. 0 [REF NEEDED] left; Tall/SuperTall source corrected to NREL
  OpenStudio-Standards (LBNL, 2020), not DOE/PNNL; SCIEU year = 2019; cover letter done except the date (.docx rebuilt);
  `submission/BE_upload/` = Figure_1..9.pdf + 3J_highlights_BE.docx. Author items: download Guan 2016 and Box 2015; gem version;
  source of the context-range edges. Detail: `IMP/rewrite_log.md` "B&E format pass and the last citations".
- 2026-09-25 ~19:45 UTC: context-range edges had no source (deep-research buffers) -> removed from Table 4, SCIEU 2019 survey
  values shown instead; Box 2015 -> Hyndman & Athanasopoulos 2021 (open); Guan 2016 dropped. No download left for the author.
  Rebuilt, checks as expected. Author items: cover-letter date, final read, submit.
- 2026-09-25 ~20:30 UTC: author's 8 Word comments fixed (smaller title, new highlights, Gemini notes out of captions,
  content-based table widths, centred captions, shorter Appendix A). Rebuilt; checks as expected. Board v44 (tasks ticked).
  Author items: cover-letter date, final read, submit.
