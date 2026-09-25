# V4 - second tower model: design note (no simulation)

Task doc:  `writing/implementation/3J_IMP_execution_2026-09-22.md` row "V4" (line 49: "Second tower model
           design note, then runs", owner agent, status "after V3b", output `IMP/V4_design.md`); plan
           `writing/submission/IMP/3J_improvement_plan_from_2J_lessons_2026-09-22.md` Section 7a, row V4:
           "Design note first (which model, which cells, what counts as 'same result'); author approves
           the design before any run."
Status:    DESIGN ONLY. No simulation run for this task. V3b is closed (see
           `IMP/V3_design_and_runs.md` Section 10) so the execution doc's "after V3b" gate is met, but the
           model question below (Section 2) is open and blocks submission regardless.
Written:   2026-09-24, after V3b's result was recorded. Zero EnergyPlus, zero heavy process run for this
           note; only file reads and `find`/`grep` over the local repo and single-file `cat`/`ls`/`grep`
           over ssh on the cluster login node.

---

## 1. Aim

3J's headline timing claim (peak hours, coincidence factor, day/night contrast) is measured on exactly
two building geometries, the PNNL Tall and SuperTall mixed-use prototypes
(`writing/submission/3J_manuscript_submission.md:188,484-486`: floor areas 72,623.1 m2 Tall,
135,857.6 m2 SuperTall). P3 already found that on these two prototypes the timing result "does not
survive against code schedules" (`IMP/P3_code_schedule_comparison.md` Verdict: "the timing result as
currently framed... does not survive"; D3 ruling, `3J_IMP_execution_2026-09-22.md:209-212`). V4's job is
to check whether that finding (survive or not survive) is a property of the injection method, or a
property of these two specific tower geometries, by repeating the same code-vs-survey timing comparison
on a **different** mixed-use building model. This is a validation track (plan Section 7a), not a new
result to publish on its own: the frozen reference bands and gate verdicts stay exactly as they are
(`3J_IMP_execution_2026-09-22.md:15-16`); V4's output sits beside them and never re-scores them.

## 2. What model (OPEN - blocks everything below)

**NOT FOUND: no third Tag-2-routable mixed-use tower prototype IDF exists in this repo, as far as this
session could find.** Evidence:

- The only mixed-use tower IDF confirmed usable by the injector is the PNNL `TallBuilding_90.1-2019`
  family that already underlies both Tall and SuperTall
  (`Leg3_4-split/prompt-manager/previous/2026-07-24_manager_step8_arming.md:20-24`: "le recensement a
  confirmé que `TallBuilding_90.1-2019_..._v221.idf` EST la tour mixte Tag-2-routable... Résidentiel 30,
  Bureau 33, Commerce 9, Hôtel 25, Service/MEP 63; 164 Spaces (SuperTall 256)"). Tall and SuperTall are
  two sizes of this same family, not two independent models.
- The earlier record for the same repo states plainly that no second mixed-use IDF was found by a
  targeted search: `Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split_val.md:130` - "No
  Tag-2-routable mixed-use prototype IDF (HighriseApartment tower + Office + Retail + LargeHotel Spaces
  in one building) exists anywhere in this repo (confirmed by `--audit`: searched `0_BEM_Setup/`,
  `BEM_Setup/Buildings/`, `2J_docs_occ_nTemp/BEM_setup/`)."
- This session's own search (`find . -iname "*.idf"` across the repo root, excluding the frozen 3J
  campaign tree) found only single-use residential prototypes reused from 2J
  (`2J_docs_occ_nTemp/BEM_setup/Buildings_{MTL,CLG}*/ASHRAE901_Apartment{HighRise,MidRise}...idf`,
  `ASHRAE_HighRise_ST{15,20}_Geometric...idf`, `AttachedHouse...idf`, `DetachedHouse...idf`) - none of
  these carry office, retail or hotel Spaces, so none is Tag-2-routable for all four channels the way
  Tall/SuperTall are.

Three ways to close this, none decided here (see Open Questions, Section 7):

1. Acquire a genuinely different PNNL/DOE mixed-use commercial prototype from outside this repo (a new
   external input - out of scope for a design note, and it is new data acquisition, not a re-read of an
   existing file, so it needs the author's explicit go before anyone downloads or wires one in).
2. Redefine "second tower model" as a structural variant of the existing family (for example, a
   different HVAC template or code vintage applied to the same Tall or SuperTall geometry) - cheaper, but
   it tests a narrower question (does the timing finding survive a different plant, not a different
   building) and should be named honestly as that if chosen.
3. Treat Tall vs SuperTall themselves as the two "models" already validated against this exact question -
   P3 already ran the code-vs-survey timing comparison on both and found the same non-survival result on
   both (`IMP/P3_code_schedule_comparison.md`, all 4 cells), which is some evidence the finding is not
   tied to one specific geometry, but it is not a new model in the sense the plan asks for.

Everything below (cells, compute) is written assuming option 1 or 2 (a genuinely new IDF becomes
available); it cannot be finalised until Section 2 is resolved.

## 3. Which cells (conditional on Section 2)

If a new mixed-use IDF becomes available, mirror the existing 3J cross-product exactly, so results are
directly comparable to P3/V3b: the same two cities and climate zones already used throughout
(`writing/submission/3J_manuscript_submission.md:575-576`: Montreal Z6/Z6A, Calgary Z7A, TMYx one file
per city), the same two scenarios already run for V3b (Default_NECB code-schedule control, and one
survey-driven scenario - Y2022 rather than B_central 2030, to avoid re-opening the P10R dependency that
P3 already flagged, `IMP/P3_code_schedule_comparison.md` "P10 dependency" section), one realisation per
cell (matching the frozen campaign's own design, `IMP/P5_sampling.md`). That is 1 building x 2 cities x
2 scenarios = 4 cells minimum, the same size as the V3b design. **NOT FOUND: whether a new prototype
IDF would even support two Canadian climate files without rebuild work** - this depends on the specific
IDF chosen in Section 2 and cannot be answered yet.

## 4. What is compared, and the pre-registered pass/fail bands

**What is compared.** Reuse the exact P3 metric set and file conventions, so V4's numbers land in the
same table as P3's (`IMP/P3_code_schedule_comparison.md` "Definitions and provenance" table, metrics
computed by `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py`): per-channel weekday energy
peak hour (circular mean argmax, script line ~L215), whole-building peak hour (published circular mean,
`agg_peak.csv` `peak_hour_circular`), coincidence factor (`agg_peak.csv` `coincidence_factor`, 6-channel
basis, script L452-455), midday/night and day/night energy ratios (script L347-348), and channel EUI on
both bases (`step9_eui_by_channel.csv`). Code-schedule arm vs survey-driven arm, same as P3's Default_NECB
vs Y2022/B_central comparison.

**Pre-registered bands (written here, before any V4 run - this note IS the pre-registration event for
V4, so "source" below means where each numeric choice comes from, not a prior V4 result):**

1. **Plumbing precondition (reused verbatim from V3b, same source, same numbers).** Before any V4 timing
   number is trusted, the same three checks V3b ran must be repeated on the new model: static N-vs-R
   identity check (`IMP/V3_design_and_runs.md` Section 3.2), a noise floor from two identical repeat runs
   that must be <= TOL/10 (Section 3.3: TOL_ANN 1e-6, TOL_HOURLY 1e-4, so noise <= 1e-7 ann / 1e-5
   hourly), and a negative control that must FIRE (Section 5, below). **V3b's own result is the direct
   precedent for why this precondition cannot be skipped**: SuperTall_MTL's gate read a clean PASS
   (0/0) but was still ruled NOT_EVALUABLE because its noise floor failed
   (`IMP/V3_design_and_runs.md` Section 10.1-10.2) - a new building model gets no exemption from the same
   rule.
2. **"Same result" band for the timing question (PROPOSED here, sourced from the V3a/P5 reading rule).**
   A timing effect (peak-hour shift, coincidence-factor change) on the new model counts as replicating
   P3's finding only if it has the **same sign** as the corresponding P3 value
   (`IMP/P3_code_schedule_comparison.md` comparison table) **and** its magnitude exceeds run-to-run noise,
   using the same threshold already pre-registered for reading small effects on this project: "a
   published... difference is 'larger than draw noise' only if |delta| > 2 x SD(delta across seeds)"
   (`IMP/V3_design_and_runs.md` Section 4, "Pre-registered report" bullet, itself the design for V3a). A
   new model that shows the opposite sign, or a same-sign effect smaller than 2xSD, counts as NOT
   replicating; a new model with no seed-noise estimate available yet cannot be scored on this band at
   all (**NOT_EVALUABLE**, not PASS, by the same rule V3b used - see point 1). This band did not exist
   before this note; it is written down now, before any V4 number exists, per the project's own rule
   that a check must be pre-registered before it is trusted.
3. **EUI-gate independence (reused from P4/the frozen bands).** The new model's own EUI, if it is
   simulated, is compared against the existing frozen reference bands only for context, never used to
   re-score them (`3J_IMP_execution_2026-09-22.md:15-16`); no new EUI band is defined here.

## 5. Negative control that must be seen firing

Reuse V3b's exact design: shift the office weekday schedule +3 h in the new model's own code-schedule
arm and confirm the checker's control comparison FIRES (`IMP/V3_design_and_runs.md` Section 3.1 "X vs
R", Section 3.6 smoke test). V3b's own result is the standing evidence this control works when run for
real: FIRED in 4/4 cells, annual margin 7.2%-10.5%, hourly margin 1.0 (100%), against a tolerance of
1e-6 ann / 1e-4 hourly (`IMP/V3_design_and_runs.md` Section 10.3) - a margin of four to five orders of
magnitude. The same script (`scripts/V3/v3_office_necb_shift3h.csv`-style fixture) should be reused
rather than a new one written, so the control is known-good before it is pointed at an unfamiliar model.

## 6. Compute estimate

**Runs will be LOCAL, not on Speed** (author ruling 2026-09-24, `Prompts/RESUME.md:3,6-20`, read-only:
"the whole arm... is now LOCAL"), capped at 10 workers, with a RAM watchdog of the same design as
`IMP/scripts/p10r_mem_watchdog.ps1` (threshold 80%, kills the campaign's own driver and worker processes
first, two consecutive over-threshold samples, `p10r_mem_watchdog.ps1:1-30`) - a V4 run would need its
own copy of this script matching its own process/command-line pattern (the existing one only matches
`campaign_local_P10R`/`p10r_local_campaign`, `p10r_mem_watchdog.ps1:19-22`), not a shared instance.

**V4 must NOT start until the P10R campaign now running has finished.** Confirmed still in progress at
the time of writing: `Leg3_4-split/Step8_docs/campaign_local_P10R/` holds 32 cell folders (of 56) and the
driver log's last line is `[run] Default_NECB__SuperTall__MTL attempt=1`
(`Leg3_4-split/Step8_docs/campaign_local_P10R/_logs/driver_stdout_relaunch2.txt`, tail, read-only, not
modified) - it has not reached `[done]` for all 56 cells. `Prompts/RESUME.md:9` records EnergyPlus using
9.4 of 20 cores at 10 workers with RAM around half; V4 sharing the same box before that finishes would
risk the RAM ceiling this watchdog exists to protect.

**Runtime, once a model is known.** No runtime figure exists for a model that has not been chosen
(Section 2), so this is an extrapolation from the two towers already timed, not a measurement:
local win32, 6 workers, per-cell EnergyPlus time was 7.9-9.1 min (Tall) and 15.4-19.0 min (SuperTall)
(`IMP/V3_design_and_runs.md` Section 1, "Per-cell run time"); Speed's arm-H timings for the same two
towers ran 24 min to 1 h 14 min per cell on 1 CPU. If the new model is comparable in size to Tall or
SuperTall and the design in Section 3 holds (4 cells, single realisation, plus the plumbing precondition
of Section 4 point 1 which needs 2 extra "N/R/U/U2/X"-style repeat arms per cell as in V3b, i.e. up to
20 tasks for 4 cells): budget roughly 20 tasks x 15-45 min = 5-15 CPU-hours, well inside 10 local workers
in under 2 hours wall time. **This is a placeholder, not a commitment** - a genuinely larger or smaller
building would move it proportionally, and it cannot be firmed up until Section 2 is resolved.

## 7. Open questions for the author (max 3)

1. **Which second model?** Section 2's three options (acquire a new external PNNL mixed-use prototype;
   redefine "second model" as a structural variant of Tall/SuperTall; or treat Tall vs SuperTall as the
   two models already tested by P3). Each answers a different question and none is free to assume.
2. **Scenario year.** Should V4 use Y2022 only (avoids the still-open P10R/2030 dependency,
   `IMP/P3_code_schedule_comparison.md` "P10 dependency"), or wait for P10R's rebuilt 2030 products so
   both years can be reported together?
3. **Depth of the plumbing precondition.** Does V4 need its own full V3b-style N/R/U/U2/X repeat design
   (Section 4 point 1) before its timing numbers can be trusted, or is the static identity check (Section
   3.2 of V3_design_and_runs.md) alone acceptable for a second-model validation track that is explicitly
   "never gated" against the paper's frozen bands?

## 8. What I did not verify

- Whether any PNNL/DOE mixed-use prototype beyond Tall/SuperTall exists publicly and could be acquired;
  this note only checked what already exists in this repo.
- The new model's floor area, Space count, HVAC template, or climate-file compatibility - all depend on
  Section 2, which is unresolved.
- The exact wall-clock state of the P10R campaign at the moment V4 would actually be allowed to
  start (Section 6's cell count was read once, at write time, not polled).
- Whether 2 repeat runs (U, U2) are enough to estimate the noise floor on a new model, given that V3b's
  own SuperTall_MTL cell needed exactly this check to fail before its noise problem was visible
  (`IMP/V3_design_and_runs.md` Section 10.1-10.2) - the same could happen on an unfamiliar model and is
  not something a design note can rule out in advance.

## 9. Author ruling (2026-09-25)
Option chosen: **Tall vs SuperTall are the two models already tested** (no new model, no new runs). V4 closes
as a limitation sentence in the paper (single mixed-use tower family; the two heights are the only structural
contrast tested). Questions 2 and 3 of section 7 fall away with this choice.
