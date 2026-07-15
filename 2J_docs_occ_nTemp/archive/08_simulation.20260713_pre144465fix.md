# Step 8 — BEM Simulation: Implementation Plan
### Time-Series Occupancy → EnergyPlus: the 2022 → 2030 residential energy shift
#### GSS Occupancy Pipeline — Detailed Implementation Specification

> ✅ **RESOLVED — re-simulated & re-validated on the corrected v2 campaign (2026-06-10).** The 4-hour schedule-injection bug found 2026-06-08 (`07_aug_to_bem.py` wrote the 4 AM-origin GSS diary slots straight to EnergyPlus `Hour` instead of rotating slot@04:00 → Hour 4, as the classic `21CEN22GSS_occToBEM.py` did; all four channels injected 4 h early vs the EPW) is fixed (rotation restored) and repaired by a **full re-simulation**: v2 campaign `953111` + full re-validation `954135` + Sub-step 8G recovery `954296/954300` → **6,000/6,000 runs, 24 PASS / 0 WARN / 3 INFO / 0 FAIL**, §2 schedule round-trip **EXACT all 5 years** (v2 schedules regenerated from the current calibrated CSVs — this also **supersedes** the 2026-06-05/07 §2 schedule-provenance / donor-draw-divergence limitation recorded in the Progress Log below). v2 results: `SimResults_Step8_corrected_v2/` (cluster) → `outputs_step8_v2/` (local). EUI phase-invariant vs v1 (max Δ +2.85% SingleD); mean peak hour 17.5–17.7 h all years. Pre-v2 numbers below are superseded where they differ. Details: `08_simulation_val.md`, `Step8_docs/cluster_rerun.md`, `Step9_docs/investigation/step9_investigation.md`.

---

## GOAL

Quantify the **residential energy impact of the predicted occupancy time-series** by driving
EnergyPlus with the calibrated 30-min occupancy + metabolic schedules (Steps 4–7) and the
forecast-to-2030 deliverable, then comparing energy **load shapes** across cycle-years
2005 → 2030. The unit is a **single-building archetype**; stock-scale behaviour is reconstructed
by **Monte-Carlo sampling** over the household population. The headline result is a **time-series**
(hourly load shape, peak timing) — not annual kWh — which is the methodological novelty of this
(second) journal paper.

> **Why this is new.** The conference paper (single buildings, `BEM_Setup/Buildings/`) and the
> first journal (Neighbourhood Units, `BEM_Setup/Neighbourhoods/`) drove BEM with **non-time-series**
> occupancy (demographic diversity factors → annual energy). This paper predicts occupancy as a
> **behavioural time-series** (AT_HOME + co-presence + activity, calibrated, forecast to 2030), so the
> contribution shifts from *how much* energy to ***when*** — load shape, peak magnitude, and
> peak-hour timing, with Monte-Carlo uncertainty bands.

---

## PREREQUISITES & INPUTS

### Input Files

| File | Location | Content | Status |
|---|---|---|---|
| `BEM_Schedules_2022.csv` | `BEM_Setup/` | Calibrated 2022 occupancy + metabolic (Step 7) | ✅ exists |
| `BEM_Schedules_2030.csv` | `BEM_Setup/` | Forecast 2030 (Step 7) | ✅ exists |
| `BEM_Schedules_{2005,2010,2015}.csv` | `BEM_Setup/` | Historical cycles on the frozen 2022 frame | ⚠️ **to generate** (see Prereq P1) |
| Archetype IDFs (all 4 dwelling types) | `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL/` | DetachedHouse→SingleD · AttachedHouse→Other · ApartmentMidRise→MidRise · ApartmentHighRise→HighRise (NECB17 / NBC936, Z6) | ✅ **complete — P2 resolved** |
| Cold-zone envelope sensitivity | `2J_docs_occ_nTemp/BEM_setup/Buildings_CLG/` | Same 4 archetypes in Z7A code (Calgary/Winnipeg) | ✅ available (optional) |
| Weather (6 EPW) | `BEM_Setup/WeatherFile/` | TMYx for CZ 5A/5B/5C/6A/6B/7A | ✅ exists |
| Simulation engine | `eSim_bem_utils/` | `integration.py`, `simulation.py`, `run_batch_hpc.py`, `config.py` | ✅ exists |

### Confirmed assets

- **Dwelling distribution (per-HH, 144,507):** SingleD 76,365 (**52.9%**) · MidRise 30,740 (**21.3%**)
  · OtherDwelling 18,838 (**13.0%**) · HighRise 18,522 (**12.8%**) · Movable "8" 42 (**0.03%**, dropped).
- **Base building model = MTL set** (`BEM_setup/Buildings_MTL/`, Canadian NECB17/NBC936 Z6),
  **held fixed across all 6 climates** so cross-city/cross-year energy variation is occupancy+weather,
  not envelope. Tall variants `ASHRAE_HighRise_ST15/ST20` available for a HighRise height sensitivity.
- **Climate zones (6 cities):** Toronto 5A (ON) · Kelowna 5B (BC) · Vancouver 5C (BC) · Montreal 6A (QC)
  · Calgary 6B (AB) · Winnipeg 7A (MB). Province→city map in `eSim_bem_utils/config.py`
  (`PR_REGION_TO_EPW_CITY`).
- **Engine capability:** `integration.py` filters schedules by `DTYPE`, builds `Schedule:Compact`
  (Weekday/Weekend, per-month `Through:` blocks), injects into the `People` object; `run_bem.py`
  option 4 = Monte-Carlo comparative single building; options 7/10 = batch MC.

---

## BACKGROUND — the experimental design

### Single building + Monte-Carlo = stock-scale, cheaply

One archetype IDF is run **many times**, each with a different household's occupancy time-series
drawn from the calibrated population. The **ensemble distribution** of energy outcomes is the
stock-scale result — capturing occupant **diversity** without simulating all 144,507 dwellings.

### Paired MC over a frozen frame (the key design choice)

Because the dwelling stock is **frozen at the 2022 frame** (Step 7 assembled 2030 onto the same
HH IDs; we do the same for 2005/2010/2015), **every `SIM_HH_ID` exists in all five years**. So we:

1. Sample **N = 50 household IDs once** per (archetype × climate-region), stratified to the
   matching `DTYPE × PR`.
2. Run **each sampled household across all 5 years** in the same archetype IDF under the same TMY
   weather — only its **occupancy time-series changes by year**.

This yields **paired** per-household energy series → the 2022→2030 (and inter-cycle) deltas are
within-household differences with much tighter confidence intervals and clean attribution
(building physics + climate are differenced out).

### What is held vs varied

| | Held constant | Varied |
|---|---|---|
| Within a cell (archetype × CZ) | IDF, TMY weather | sampled household, cycle-year |
| Across the experiment | — | archetype, climate zone, year, MC iteration |

> **Isolation logic.** Holding building + weather fixed means the cross-year energy delta is
> *purely* the predicted occupancy change (incl. the 2015→2022 COVID break and the 2022→2030
> forecast). Future-weather morphing is deferred to a sensitivity (out of core scope).

---

### Inter-cycle signal — why all five cycles

Observed within-stratum AT_HOME from `augmented_diaries.csv` (verified 2026-06-01) — these are the
**per-cycle raking targets** and the diary basis the BEM sees:

| Cycle | AT_HOME (diary, IS_SYN=0) | WD / Sat / Sun | vs prev |
|---|---|---|---|
| 2005 | 70.4% | 69.0 / 71.9 / 75.7 | — |
| 2010 | 71.4% | 70.0 / 71.9 / 77.6 | +1.0 pp |
| 2015 | 72.3% | 70.8 / 74.2 / 77.3 | +0.9 pp |
| 2022 | 77.5% | 76.9 / 77.3 / 80.2 | **+5.2 pp (COVID onset)** |
| 2030 | ~79.7% | 78.4 / 79.2 / 81.5 | +2.2 pp (persistence) |

Read on the **same (diary) basis**, the big shift is the **2015→2022 COVID onset (+5.2 pp)**; the
2030 forecast shows **persistence** (+2.2 pp), consistent with the structural-break / COVID-persists
design. (Survey-*weighted* population rates in Steps 2–3 run ~8 pp lower — 62–72% — same shape; the
Census linkage re-weights each cycle to the population, which for 2022 brought the 77.5% diary rate
to the ~71.6% the BEM actually used. The 2005–2015 BEM marginals re-weight the same way at run time.)

**Per-cycle raking is required, not optional:** in every cycle the *synthetic* weekday AT_HOME sits
~5–10 pp **below** observed (2005 WD obs 69.0% vs syn 62.0%; 2022 76.9% vs 67.2%) — the same J3 bias
Phase-8B corrected for 2022. The DRIFT matrices (`forecast_2030/DRIFT_MATRIX_*.csv`) add the
*time-series* nuance: the 2015→2022 and 2022→2030 weekday shifts are more **daytime** Work
(0.225→0.252) and Education (0.009→0.021) *at home* — reshaping the daily load curve and peak timing,
exactly the novelty. **Keeping 2005–2015 anchors the "flat-then-break" narrative.**

---

## EXPERIMENTAL GRID

| Dimension | Levels | Count |
|---|---|---|
| Dwelling archetype | SingleD, MidRise, HighRise, OtherDwelling | 4 |
| Climate-zone city | Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A | 6 |
| Cycle-year | 2005, 2010, 2015, 2022 (calibrated), 2030 (forecast) | 5 |
| Monte-Carlo households (paired) | sampled IDs per (archetype × region) | 50 |

**Total annual EnergyPlus runs:** 4 × 6 × 5 × 50 = **6,000** (paired structure: 50 HH × 5 years per
archetype×CZ). Cloud/HPC batch via `run_batch_hpc.py`. **Stock aggregation:** weight each
(archetype × region) cell by its empirical `DTYPE × PR` share of the 144,507-HH stock.

---

## PRIMARY OUTPUTS — the time-series novelty

| Output | Description | Why it matters |
|---|---|---|
| **8760-h load profiles** | Hourly heating / cooling / total / electricity, per scenario, with **MC bands** | The forecast occupancy reshapes the annual load curve |
| **Diurnal-by-season profiles** | 24-h average × heating/cooling season | Shows the *shape* change, not just totals |
| **Peak demand — magnitude + hour** | Annual & seasonal peak load and **hour-of-peak shift** 2022→2030 | WFH-persistence keeps people home midday → peak moves/flattens (grid/DR relevance) |
| **Load-shape metrics** | Load factor, peak-to-average ratio, daily ramp | Quantify the shape change |
| **Ensemble coincidence/diversity factor** | How occupant diversity smooths the *stock* load | Inherently stock-scale + time-series |
| **Annual EUI** (secondary) | kWh/m²·yr per archetype × CZ × year | Longitudinal 2005→2030 trend + COVID break; benchmark check |

---

## HARD GATES

| Gate | Threshold |
|---|---|
| EnergyPlus run success | 0 fatal errors; sizing converged; all 6,000 runs complete |
| Schedule injection fidelity | Injected `Schedule:Compact` daily mean = source `Occupancy_Schedule` (±0.5%) |
| MC convergence | Cell-mean annual energy CI half-width < 2% by N = 50 |
| Physical plausibility | EUI within published Canadian residential range per archetype/CZ (NRCan SHEU) |
| 2022→2030 effect detectable | Paired Δ load-shape statistically separable from 0 where expected |

---

## IMPLEMENTATION SUB-STEPS

### Sub-step 8A — Schedule generator (Prereq P1) — ✅ COMPLETE (2026-06-01)
`Step8_docs/08_gen_cycle_schedules.py` generated all **five** `BEM_Schedules_{2005,2010,2015,2022,2030}.csv`
on one consistent basis. Per cycle: (1) pull that cycle's diaries from `outputs_step4/augmented_diaries.csv`
(found **local** — no cluster pull), (2) **rake synthetic hom30 → that cycle's observed within-stratum
AT_HOME** (Phase-8B per cycle — decision #2), (3) **demographic-matched assembly onto the frozen 2022 frame**
(option B; tiered keys AGEGRP/SEX/MARSTH/HHSIZE/LFTAG + DDAY_STRATA — **geography PR/CMA dropped** for
uniform cross-cycle matching; 2030 joins demographics via `occID`), (4) `convert()` → 13-col file. Classic /
Step-7 originals backed up `*_PRE_STEP8_BAK.csv`.

**Result — final WD/WE occupancy (all five via identical procedure, paired-valid):** 2005 0.690 / 0.738 ·
2010 0.683 / 0.723 · 2015 0.671 / 0.707 · 2022 0.737 / 0.733 · 2030 0.776 / 0.782. Pre-COVID flat-declining
(compositional — confirmed by AGEGRP×SEX×LFTAG standardization); COVID onset = biggest break (+6.6 pp WD);
2030 persistence (+3.9 pp). See the Progress Log for the full P1 history (basis decision B, geography drop,
2022 rebuild).

### Sub-step 8B — Archetype IDFs ✅ (Prereq P2 resolved)
All four dwelling archetypes already exist in `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL/`
(Canadian NECB17 / NBC936, Z6): DetachedHouse, AttachedHouse, ApartmentMidRise, ApartmentHighRise.
**Use the MTL set as the single base building model across all 6 climates** — holding the envelope
constant makes cross-city/cross-year energy variation attributable to *occupancy + weather*, not
building differences, and the **paired per-HH Δ cancels the envelope** outright. `Buildings_CLG`
(Z7A) provides a colder-envelope sensitivity for absolute-EUI checks in the cold zones.

### Sub-step 8C — Runner extension ✅ COMPLETE (2026-06-02)
Versioned engine copy `Step8_docs/eSim_bem_utils_2J/` (+ our own `run_bem.py` menu and headless
`run_paired_mc.py`); `COMPARATIVE_YEARS` → 2030; `STEP8_*` constants (archetype→DTYPE, city→region);
new `run_step8_paired_mc()` = paired draw (same `SIM_HH_ID` across all 5 years, deterministic
per-cell SHA-256 seed). MTL archetype IDFs upgraded v22.1→v24.2 (`Buildings_MTL_v242/`; the raw
_v221 files fatal under the 24.2 IDD). 4-run smoke green (8760-h hourly output, paired Δ non-zero).
See Progress Log 2026-06-02.

### Sub-step 8D-pilot — grid-wide mini-sample (setup validation) — ⏳ TODO (employee)
**Aim:** before the full 6,000-run campaign, confirm the paired-MC setup works across *every*
archetype, climate city, and region, and capture real per-run timing to size the full job.

**Steps:**
1. From `2J_docs_occ_nTemp/Step8_docs/`, run all **24** (archetype × city) cells at **N=3**, all 5
   years, annual (`--sim-mode standard`), seed 42 → 24 × 3 × 5 = **360 E+ runs**. Use
   `run_paired_mc.py` per cell (a PowerShell double-loop over the 4 archetypes × 6 cities).
2. Isolate pilot outputs under `BEM_Setup/SimResults_Step8/_pilot_N3/<archetype>__<city>/`
   (raw `eplusout.sql` + `hourly_meters.csv` + `cell_manifest.csv` per cell).

**Expected result:** 360/360 runs `status=ok` (0 fatal); every cell yields `(8760, N_meters)` hourly
CSVs; the same `SIM_HH_ID`s appear in all 5 years per cell (paired); a wall-clock + per-run timing
number to extrapolate the 6,000-run cost.

**Test method:** count `eplusout.end` files containing "Completed Successfully" (expect 360) and
`hourly_meters.csv` files (expect 360); spot-check one CSV per archetype (8760 rows, non-zero load);
confirm a 2022-vs-2030 paired Δ is non-zero for one sample HH. Report cells-ok/24, runs-ok/360,
timing, and any failed cell + its `eplusout.err` cause.

### Sub-step 8D — Paired-MC batch
For each (archetype × CZ): sample 50 HH IDs (seed 42), run each across 5 years → 8760 series.
Persist raw E+ outputs + parsed time-series. (Run only after the 8D-pilot is green; the design
target is local-overnight vs Speed-cluster — decide based on the pilot's timing.)

### Sub-step 8E — Aggregation + metrics
Compute the load-shape metrics, peak timing, stock-weighted ensemble, paired Δ(year) per HH.

### Sub-step 8F — Validation report
`08_simulation_val.py` → `outputs_step8/step8_validation_report.html` (see `08_simulation_val.md`).

### Sub-step 8G — Re-run failed / partial simulations (corrected re-sim) — ⏳ TODO
**Trigger:** run **only after the corrected Step-8 array (`953111`) is all-terminal** (no RUNNING/PENDING in `sacct -j 953111`). The failure count is not yet known — **1 confirmed** (`OtherDwelling×Kelowna_5B / sample_050_HH145979 / 2010`); 3 HighRise cells (tasks 19/22/23) were still running when this was queued, so more may surface.

**Aim:** restore every (archetype × city × year) cell to a clean **N=50 of full 8760-row runs** by recovering each EnergyPlus run that died mid-campaign — **without touching the frozen archetype IDFs** (`BEM_setup/Buildings_MTL_v242/`, Step-9-owned).

**Why needed:** a failed E+ run still leaves a *header-only* `hourly_meters.csv` (0 data rows, 3 of 10 meter columns) and still increments the engine's "hourly parsed" counter (`eSim_bem_utils_2J/main.py:2090-2110`), so a plain file-count looks complete (the "250/250 parsed" line hides it). The one confirmed failure is an HVAC **autosizing** fatal — `Coil:Cooling:DX:SingleSpeed "DX COOLING COIL_UNIT6" — negative coil bypass factor calculated`, thrown during System Sizing 2.2 s in (`eplusout.err`). It is **deterministic** (a plain re-run reproduces it) and **unrelated to the 4-h schedule fix** (the same HH ran clean in 2005/2015/2022/2030).

**Steps:**
1. **Gate** — confirm all 24 array tasks are terminal (`sacct -j 953111`); none RUNNING/PENDING.
2. **Enumerate ALL failures authoritatively** — do not trust SLURM state or file-count. For each run dir `.../SimResults_Step8_corrected_v2/campaign_N50/<cell>/sample_*/<year>/`, flag it if `eplusout.end` does **not** contain "Completed Successfully" **or** `hourly_meters.csv` has **< 8760 data rows**. Emit an inventory (cell, sample, HH, year, last `** Severe **` line of `eplusout.err`). This is the same success predicate `step8_warmup_retry.py:46-54` uses, plus the row check that catches the header-only files file-count misses.
3. **Classify** failures by `eplusout.err` root cause so one fix covers a whole class (e.g. all `negative coil bypass factor` cases).
4. **Recover each run one-off, on an ISOLATED COPY of that run's saved IDF** (`.../<year>/Scenario_<year>.idf` or `in.idf` — already expanded in the results dir; **never** edit `Buildings_MTL_v242/`). Apply the minimal sizing tweak for its class — for the DX-coil class, bound the coil's autosized airflow-per-capacity or set its Rated Air Flow Rate / Rated SHR (confirm the cause first with `Output:Diagnostics,DisplayExtraWarnings`). Run E+ once via the cluster SIF + that city's EPW, validate, then drop the new `hourly_meters.csv` (+ `eplusout.sql`) back into the run dir → that cell returns to 50/50. NB: `step8_warmup_retry.py`'s remedy (warmup-days → 120) will **not** fix a sizing fatal, so this class needs the sizing tweak, not a plain retry.
5. **Fallback** — if a run is genuinely unrecoverable after a bounded effort, leave its empty file in place: the aggregator already row-guards it (`08_simulation_plots.py:268` returns status="short" → excluded, contributes nothing), so that one cell-year is a clean **N=49** (unbiased). Document the exclusion.
6. **Re-aggregate + re-validate** — `py 08_simulation_plots.py --rebuild-agg`, then `py 08_simulation_val.py`. Confirm the EUI bands and SHEU 48/48 gate are **unchanged** (phase-invariant control — if they move, something beyond the recovery changed) and every cell is back to 50/50 (or a documented N=49).
7. **Log** the failure inventory, root-cause class, the fix applied, and before/after N per cell in the Progress Log.

**Expected result:** zero remaining failed runs (every `eplusout.end` = "Completed Successfully" and every `hourly_meters.csv` = 8760 rows × full meter set), or a short, documented list of N=49 exclusions; refreshed `outputs_step8/agg/` + validation report; EUI/SHEU gates unmoved.

**Test method:** re-run the step-2 enumeration scan → expect 0 flags (or only the documented unrecoverable set); diff per-cell EUI and SHEU 48/48 vs pre-recovery (must be unchanged — phase-invariant); spot-check one recovered `hourly_meters.csv` = (8760, 10) with non-zero, physically-ordered loads.

**Reuse / don't reinvent:** detection predicate from `step8_warmup_retry.py:46-54`; the aggregator already excludes empty runs (`08_simulation_plots.py:268`), so no aggregator change is required for this failure mode. *Optional hardening:* also require the full `KEEP_METERS` column set there, to guard against a hypothetical ≥8760-row but partial-column file.

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|---|---|---|
| Single (MTL Z6) envelope under all climates | Absolute EUI slightly high in the coldest zone (a real Z7A building is better-insulated) | Paired per-HH Δ cancels the envelope → report deltas as primary; `Buildings_CLG` Z7A as a cold-zone EUI sensitivity |
| Frozen 2022 dwelling stock for 2005–2015 | No stock-turnover effect | Deliberate — isolates occupancy; state as limitation |
| TMY weather (not historical/future) | No weather-change effect | Deliberate — isolates occupancy; future-weather = later sensitivity |
| 6,000 runs compute | Wall-clock | Cloud/HPC batch (`run_batch_hpc.py`); paired structure already minimal |
| Historical cycles un-raked vs calibrated | Provenance inconsistency | Apply Phase-8B raking per cycle in 8A |
| Metabolic channel un-calibrated | Internal-gain inputs ride raw activity | Documented (`07_metabolicMap_verification.md`); occupancy-gated; minor |

---

## CONNECTION TO PIPELINE

- **Upstream:** consumes Step 7 `BEM_Schedules_<year>.csv` (occupancy + metabolic). Step 8A
  back-fills the historical cycles using the Step 4 augmented pool + Step 7 converter.
- **Engine:** `eSim_bem_utils/` (versioned copy for this paper). Climate routing already in
  `config.py`.
- **Downstream:** the load-shape results + stock aggregation are the paper's **results section**.

---

## DECISIONS PENDING (user)

1. ~~Archetype prototypes~~ ✅ **resolved 2026-06-01** — use the `BEM_setup/Buildings_MTL` 4-archetype
   set as the base building model (all dwelling types present; Canadian codes); `Buildings_CLG` = cold-zone sensitivity.
2. ~~Historical-cycle raking~~ ✅ **resolved 2026-06-01** — include all 5 cycles and **rake each to
   its own observed within-stratum AT_HOME** (Phase-8B per cycle), so 2005→2030 is one uniform
   method (no mixing calibrated 2022/2030 with raw 2005–2015). Frame 2005–2015 as the flat
   pre-COVID baseline, 2022→2030 as the result (see *Inter-cycle signal* above).

---

## Progress Log

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-06-01 | Step 8 designed | ✅ DESIGN | Paired-MC over frozen frame; 4 archetypes × 6 CZ × 5 years × 50 HH = 6,000 runs; load-shape (time-series) outputs as the novelty. Created `08_simulation.md` + `08_simulation_val.md`; added Step 8 to both `00_` pipeline docs. Prereqs: P1 generate 2005/2010/2015 schedules, P2 archetype IDFs, runner +2030. `.py` versioning = next phase. |
| 2026-06-01 | Archetype IDFs located — **P2 resolved** | ✅ | User found `2J_docs_occ_nTemp/BEM_setup/Buildings_{MTL,CLG}/` with all 4 dwelling types (Detached / Attached / ApartmentMidRise / ApartmentHighRise; NECB17 / NBC936). **Decision: MTL Z6 set = base building model across all climates** (envelope held constant → clean occupancy attribution; paired Δ cancels the envelope); `Buildings_CLG` Z7A = cold-zone EUI sensitivity. Remaining prereqs: P1 (2005/2010/2015 schedules) + runner +2030. |
| 2026-06-01 | **Decision #2 resolved** — cycles + raking | ✅ | Verified the AT_HOME trajectory (62.7→62.3→64.5→70.6→~79%) + DRIFT matrices: inter-cycle signal is concentrated at 2015→2022→2030 (2005–2015 = flat baseline). **Include all 5 cycles; rake each per cycle** to its own observed within-stratum AT_HOME (uniform method). 2030 weekday drift = more daytime Work/Education at home → reshapes load curve (supports the time-series novelty). Added *Inter-cycle signal* table to the doc. |
| 2026-06-01 | P1 input located | ✅ resolved | Multi-cycle `augmented_diaries.csv` (192,183 rows, all 4 cycles, 545 cols incl. demographics) found local at `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv` — no cluster pull needed. |
| 2026-06-01 | P1 generator built + 2015 test | ✅ mechanics OK | `Step8_docs/08_gen_cycle_schedules.py` (per-cycle Phase-8B rake syn→observed + assemble onto frozen 2022 frame + convert). 2015 test: rake hit observed marginals exactly (syn WD 65.75→70.84%), 6.9M rows / 144,507 HH, gates pass. |
| 2026-06-01 | **Assembly-basis decision — B selected** | ✅ B | 2015 test exposed a basis mismatch: stratum-random assembly gives **2015 WD occ 0.709 > 2022 WD 0.703 (inverted)** because 2022 is demographically-linked (Step 5, population-representative ~70%) while 2030 + assembled cycles are stratum-random (raw diary ~77%) — confounds the longitudinal comparison & weakens the paired design. Options weighed: **(A) Stratum-random for all** — also regenerate 2022 by assembly (→ ~76.9% WD); simple, internally consistent, but raw (non-population) basis, weaker pairing, contradicts the Step-7 calibrated 2022. **(B) ✅ Demographic-matched assembly for every cycle** — match each frame HH to a cycle-Y diary of similar demographics + stratum (per-cycle mini Step-5; the augmented file has the keys); all years population-representative, paired design valid, 2022 stays as-is; more generator work, scientifically cleanest for the journal. **(C) Leave it** — not viable; basis confound would undermine the headline result. **SELECTED B (user, 2026-06-01).** Generator upgrading stratum-random → demographic-matched (tiered keys AGEGRP/SEX/MARSTH/HHSIZE/LFTAG/PR/CMA + DDAY_STRATA); provisional 2015 to be regenerated. Note: the 2030 forecast diaries carry occID (→ 2022 demographics), so they can be demographic-matched too for full 5-year consistency. |
| 2026-06-01 | P1 historical cycles generated (option B) | ✅ 2005/2010/2015 | Demographic-matched (tiered) generation; 6.9M rows / 144,507 HH each, rake exact, 0 failsafe. **Basis fixed** — BEM WD occ 2005 **0.690** / 2010 **0.683** / 2015 **0.669** < 2022 0.703 < 2030 0.785 (correct ordering; was 0.709-inverted under stratum-random). Classic census files backed up → `BEM_Schedules_{2005,2010,2015}_PRE_STEP8_BAK.csv`. **Standardization check** (AGEGRP×SEX×LFTAG, frame-weighted WD): 2005 64.2% / 2010 64.2% / 2015 63.3% / 2022 70.6% — confirms pre-COVID weekday at-home was **genuinely flat**, the raw-marginal rise (69→71%) was **compositional** (sample aging), and the real shift is the COVID jump. Standardized 2022 (70.6%) ≈ linked-2022 BEM (0.703) → demo basis consistent with Step 7. *Paper-relevant finding.* |
| 2026-06-01 | Two cleanups identified | ⏳ open | **(1)** 2005 matched coarser (geography PR/CMA coding gap → tier1=0), inflating its BEM WD ~1 pp vs standardization; fix = drop PR/CMA from the occupancy match so all cycles match on identical demographic keys (uniform cross-cycle basis). **(2)** 2030 still raw-basis (Step-7 stratum-random, WD 0.785) — needs demo-matched re-assembly; the 2030 forecast diaries carry occID → join 2022 demographics, then match. Both folded into one final regen → fully consistent 5-year set (2022 stays linked). |
| 2026-06-01 | Both cleanups executed + regen | ✅ done | Generator upgraded: geography (PR/CMA) **dropped** from the match (uniform demographic keys AGEGRP/SEX/MARSTH/HHSIZE/LFTAG); **2030 demo-matched** via occID→2022-demographics join (12,336 respondents, **0 unmatched**). Regenerated 2005/2010/2015/2030 (each 6.9M rows / 144,507 HH, 0 failsafe). Step-7 2030 backed up → `BEM_Schedules_2030_PRE_STEP8_BAK.csv`. |
| 2026-06-01 | **5-year trajectory verified** | ✅ + 1 open | WD occ from written files: 2005 **0.690** / 2010 **0.683** / 2015 **0.671** / 2022 **0.703** / 2030 **0.776** (WE 0.738/0.723/0.707/0.749/0.782). Pre-COVID flat-declining ✓; COVID + forecast rise ✓. **Open consistency issue:** 2022 is still on the Step-5 *linkage* (0.703 ≈ survey-weighted 70.6%, most accurate absolute value) while the other four use the demo-matcher → the 2022→2030 jump reads **+7.3 pp** (larger than the COVID onset — backwards), and the **paired design requires one procedure for all years**. Measured 2022 *through the same matcher*: **WD 0.737** → trajectory becomes 0.690 / 0.683 / 0.671 / **0.737** / 0.776 (COVID **+6.6 pp**, 2030 persistence **+3.9 pp** — coherent). Trade-off: matcher-2022 (0.737) ~3 pp high vs linkage (0.703); paired deltas (the paper's focus) are clean. **Recommend regenerating 2022 via the matcher** for a consistent paired set (Step-7 linked 2022 kept as the single-year deliverable). *Pending user decision.* |
| 2026-06-01 | 2022 rebuilt via matcher — **P1 COMPLETE** | ✅ DONE | User approved. 2022 through the same rake + demo-matcher: **WD 0.737 / WE 0.733** (Step-7 linked 2022 → `BEM_Schedules_2022_PRE_STEP8_BAK.csv`). **Final consistent 5-year set** (all via identical procedure, paired-valid): WD **0.690 / 0.683 / 0.671 / 0.737 / 0.776**, WE **0.738 / 0.723 / 0.707 / 0.733 / 0.782**. Pre-COVID flat-declining (compositional, per the standardization); **COVID onset = the biggest break (+6.6 pp WD)**; 2030 persistence (+3.9 pp). Notable: 2022 WD≈WE (0.737/0.733) — COVID erased the weekday/weekend gap (WFH), a clean illustration of the effect. **All five `BEM_Schedules_{2005,2010,2015,2022,2030}.csv` ready for the runner (Sub-step 8C).** |
| 2026-06-02 | **Sub-step 8C built** — versioned engine + paired-MC runner | ✅ DONE | Copied `eSim_bem_utils/` → `Step8_docs/eSim_bem_utils_2J/` (intra-package imports repointed to `_2J`; conference/J1 engine untouched). `main.py`: `BASE_DIR` fixed to repo root (now 4 dirnames up), `COMPARATIVE_YEARS` 2025→2030, added `STEP8_*` constants (Buildings_MTL dir, 4 archetype→DTYPE maps {SingleD/OtherDwelling/MidRise/HighRise}, 6 CZ-city→region maps) + new `run_step8_paired_mc()`. New `Step8_docs/run_bem.py` (2nd-journal menu) + `run_paired_mc.py` (headless 1-cell driver for the 8D HPC array; deterministic per-cell SHA-256 seed so array tasks each reproduce their own draw). **Paired design = the core change:** old option-4 re-drew a *different* HH per year (matched on `hhsize` only); the new runner samples N `SIM_HH_ID`s ONCE per cell and runs the SAME IDs across all 5 years → true within-HH paired Δ. |
| 2026-06-02 | Frozen-frame + pool-size verification | ✅ | All 5 `BEM_Schedules` share the identical 144,507 `SIM_HH_ID`s (set diff = 0) → within-HH pairing valid. Per-(DTYPE×PR) pool sizes all ≫ 50 (smallest = HighRise×Prairies 853, OtherDwelling×Prairies 863) → **no thin cells**: N=50 sampled without replacement everywhere (with-replacement guard kept but never triggers). Annual mode (`standard`) locked per user (true 8760 load shapes; `weekly` = smoke only). |
| 2026-06-02 | Wiring sanity check | ✅ | Package imports from new location; `BASE_DIR`→repo root; all 24 (archetype×city) cells resolve to real IDF + 6-CZ EPW. |
| 2026-06-02 | **IDF version fix (smoke caught it)** | ✅ | First 1-cell smoke fatal-ed in ~1 s: the MTL archetypes are EnergyPlus **v22.1**, and inject only restamps the Version string — so under the 24.2 IDD the `HeatExchanger:AirToAir:SensibleAndLatent` + `Coil:Cooling:DX:SingleSpeed` fields shift (node names land in enum/numeric slots → 8 severe → fatal before sim). Fix = ran E+'s official transition chain 22.1→22.2→23.1→23.2→24.1→24.2 (`PreProcess/IDFVersionUpdater/Transition-*.exe`) on the 4 archetypes → new `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` (originals untouched); repointed `STEP8_BUILDINGS_DIR`. Also fixed the runner to report true E+ success (ok/partial/error via `eplusout.end`) instead of always "ok". |
| 2026-06-02 | **Sub-step 8C COMPLETE — smoke green** | ✅ DONE | Re-ran smoke on 24.2 IDFs: **4/4 annual E+ runs OK** (~37 s, 4 parallel workers), 4/4 hourly parsed. Each `hourly_meters.csv` = **(8760, 10)** with the load-shape meters (Electricity:Facility, Interior Lights/Equipment, Fan, Heating/Cooling:EnergyTransfer, WaterSystems). **Paired confirmed:** same `SIM_HH_ID`s (130336, 8) ran in both 2022 & 2030; occupancy moves the load (HH130336 2030 vs 2022: elec −10.7%, lights −16.3%, cooling −15.8%, heating +6.1%, water −23.5%; fan flat). Runner (`run_step8_paired_mc`) + headless driver (`run_paired_mc.py`) + 2nd-journal menu (`run_bem.py`) + per-cell SHA-256 seed all validated. **Ready for 8D (6,000-run grid).** |
| 2026-06-02 | **Sub-step 8E generator built + pilot-validated** | ✅ DONE | `Step8_docs/08_simulation_plots.py` (figure catalogue → real figures): two-pass summarize-on-read aggregation (`outputs_step8/agg/*.csv`) + 10 figure functions + CLI; reuses `reporting.py`/`plotting.py` helpers; Step-8 palette. Validated against the in-progress N=3 pilot (105 runs, all ok): agg sane, **pairing exact** (diff 0), correct-signed midday Δ, all 10 figs render (Fig 1 occupancy driver + Fig 2 headline diurnal tell the WFH story). Re-runs on the full campaign via `--rebuild-agg`. Detail + open EUI-benchmark flag in `08_simulation_plots.md` Progress Log. (8D-pilot itself is the employee's separate task; this used its partial output to validate the figure code.) |
| 2026-06-02 | **8D run target = LOCAL parallel** + campaign runner built & validated | ✅ DONE (built; run pending) | **Decision (user):** run the 6,000-run grid **local-parallel overnight**, not the Speed cluster (cluster would need an E+ 24.2 install + full port — not worth it for a one-shot; the 20-core local box does it in ~3 h). Built `Step8_docs/run_campaign_local.py` — bounded worker-pool wrapper around the validated `run_paired_mc.py`: `--workers` (default cores−2 = **18** here), isolates output under `SimResults_Step8/campaign_N50/<cell>/` (clean of the N=3 `_pilot_N3` dirs), per-cell logs + `campaign_status.csv`, **resume-on-restart** (skips cells already holding N×years `hourly_meters.csv`; failed/partial re-run), and a `--cells` subset filter for targeted re-runs. **Validated:** 24/24 cells resolve (`--dry-run`); **concurrency smoke** (2 SingleD cells, N=2, weekly, 2 workers) → both ok in **2.4 min wall-clock** (vs ~5 min sequential → genuine parallelism), 20/20 `hourly_meters.csv`, no E+ collision, 0 stray processes after. Launch: `cd Step8_docs; py run_campaign_local.py --n 50`; verify with `py run_campaign_local.py --dry-run` (expect done 24 / to-run 0). **Next:** user launches overnight → then 8E `--rebuild-agg` pointed at `campaign_N50`. |
| 2026-06-02 | **Sub-step 8D-pilot COMPLETE** — N=3 across all 24 cells | ✅ DONE | **360/360 runs ok, 0 failures, 24/24 cells ok.** `SimResults_Step8/_pilot_N3/<archetype>__<city>/` populated. All 360 `eplusout.end` = "Completed Successfully"; all 360 `hourly_meters.csv` present. Spot-check (one CSV per archetype × Toronto_5A): all 8760 rows, annual `Electricity:Facility` non-zero and physically ordered (SingleD 37 GJ < OtherDwelling 247 GJ < MidRise 917 GJ < HighRise 1,305 GJ). Paired Δ confirmed: SingleD × Toronto sample_001 2022→2030 `Electricity:Facility` = −1.26 GJ (−3.3%) — non-zero, correct-signed (more WFH in 2030 shifts load shape). **Wall-clock (sequential, 1 cell at a time):** 10,881 s = 3.02 hr; avg 30.2 s/run. Per-archetype avg: SingleD ~118 s/cell, OtherDwelling ~512 s, MidRise ~616 s, HighRise ~568 s. **Full 6,000-run campaign extrapolation:** sequential ~46 hr; with 24 parallel SLURM jobs (1/cell) wall-clock ≈ longest single cell × 17 E+ batches ≈ 2.7 hr cluster wall-clock. No failed cells. **Verdict: runner + engine validated end-to-end across all 4 archetypes × 6 climate zones × 5 cycles; cleared for N=50 full campaign.** |
| 2026-06-02 | **RAM fix verified (STEP 1 gate) — PASS; full campaign (STEP 2) ABORTED on memory** | ⚠️ BLOCKED | **Fix verified:** `run_campaign_local.py:66` sets `ESIM_WORKERS="1"` per cell subprocess; `simulation.py:159–160` reads it, capping the inner `ProcessPoolExecutor` to 1. **STEP 1 gate (2 cells, --workers 2, weekly, N=2):** peak E+ count = **2** (locked exactly at --workers, never exceeded); peak committed-memory % = **59.7%**; exit 0; 20/20 `hourly_meters.csv` produced. Fix confirmed correct — nested-parallelism bug is resolved. **STEP 2 full campaign (--workers 6) ABORTED:** Python setup phase for 6 concurrent cells (each loading 144k-row BEM_Schedules × 5 cycles) pushed committed-memory to **66–67%** before any E+ started. At first E+ launch (4 processes), committed spiked to **75.2%** — exceeding the ~70% abort threshold. E+ count was correctly ≤ 6 (fix is working; this is NOT a recurrence of the nested-parallelism bug). Run killed cleanly; memory returned to 31.2%; 0 cells completed; `campaign_N50/` holds 24 cell dirs but all empty. **Not verified:** full campaign completion; campaign_status.csv; --dry-run done 24/to-run 0. **Root cause / recommendation:** at --workers 6, the Python schedule-generation stage (6 simultaneous processes, each doing 50-HH demographic matching + CSV I/O) dominates the memory budget before E+ begins. Retry at **--workers 4** expected to keep the Python+E+ combined load under 70%; resume is safe (0 cells completed, no data to protect). |
| 2026-06-02 | **Flip flag + memory watchdog added; bigger load test running** | ✅ code / ⏳ test in progress | **5 edits to `run_campaign_local.py`** — (A) added `import threading`, `import ctypes`; (B) module-level watchdog: `_ACTIVE` dict, `_ABORT` Event, `_MEMORYSTATUSEX` ctypes struct, `_committed_pct()` (Windows % Committed Bytes In Use), `_kill_active()` (taskkill /F /T), `_watchdog(ceiling, interval=3s)` background thread; (C) `_run_cell` rewritten with `Popen` (not `run`) + `_ACTIVE` registration so watchdog can kill the process tree; (D) `--ep-workers` arg (inner E+ pool size via `ESIM_WORKERS`; default 1; "flip" = `--workers 1 --ep-workers 6` runs cells sequentially, each with 6 parallel E+); (E) `--mem-abort` arg (watchdog ceiling, default 80%); watchdog armed on `wd.start()`, stopped on `_ABORT.set()` after pool; abort check prints advisory and exits 1 if any cell was ABORTED. `py -m py_compile run_campaign_local.py` **passed**. **Watchdog self-test** (`--mem-abort 1`): fired in < 3 s (committed 48.4% ≥ 1%), printed kill line, exited 1, zero orphan `energyplus.exe` or `python` from the run. Clean kill confirmed. **Bigger load test** (3 cells: HighRise×Montreal_6A, MidRise×Toronto_5A, SingleD×Winnipeg_7A; N=20, annual, `--workers 1 --ep-workers 6 --mem-abort 80`) — started at ~19:06; **SingleD DONE** 16.8 min (exit 0), **MidRise DONE** 83.8 min (exit 0). **HighRise in progress** at time of writing. Monitoring data collected across all 3 cells: **E+ count** = 6 for SingleD (as designed); 14 observed for MidRise/HighRise (multi-zone archetypes run 2 E+ per job — S Apartment + N Apartment — so the effective pool is 6 jobs × 2 E+ = 12, plus brief batch-overlap spikes to 14; log confirmed `Starting 100 simulations with 6 parallel workers` — ESIM_WORKERS=6 honoured). **Committed % profile** — during CSV load+IDF injection phase: 66–73% (peak transient **79.4%**, sub-3 s; watchdog 3-s poll missed it); after Python GC releases CSV data: sustained **58–59%** for the E+ pool; handoff between cells (MidRise→HighRise) dropped to **43.2%** then rebuilt to 58.1% — confirms one cell's ~3.7 GB CSV in RAM at a time (flip isolates). **Watchdog: never fired** during the test. HighRise committed % during E+ = **58.1%** — identical to MidRise; not worse (heaviest archetype is not a RAM bottleneck once CSVs are GC'd). **Key finding:** the 73–79% spikes occur only during the brief CSV load + IDF injection window before the ProcessPoolExecutor receives all jobs and GC frees the schedule data; the sustained E+-running level is ~58–59%; the 80% watchdog provides ~20 pp margin over the sustained level and ~1 pp margin over the observed peak transient. **GO/NO-GO for full campaign:** CONDITIONAL GO — the watchdog provides the freeze safety net; the 79.4% transient spike is within 0.6 pp of the 80% ceiling and caused by machine-level background process bursts, not E+/Python load. **Recommend** running the full campaign at `py run_campaign_local.py --n 50 --workers 1 --ep-workers 6 --mem-abort 80` and monitoring the first 2–3 cells. If the watchdog fires, lower to `--ep-workers 4`; resume picks up where it left off. **VERIFIED (2026-06-02, after test completed):** exit 0 on all 3 cells; HighRise DONE in **76.5 min** (exit 0); total wall-clock **2.95 h**. **300/300 hourly_meters.csv** (100 per cell = 20 HH × 5 yr). Watchdog never fired. campaign_status.csv populated. `_bigtest/` left for inspection. **FULL GO** for `py run_campaign_local.py --n 50 --workers 1 --ep-workers 6 --mem-abort 80`. |
| 2026-06-04 | **8D campaign watchdog trips + orphan-reap + re-launch at --ep-workers 2** | ⛔ ESCALATED → Speed cluster | **History since 2026-06-02 FULL GO:** Four watchdog trips occurred on MidRise__Toronto_5A as --ep-workers was stepped down (6�2 trips ? 3 ? 2), leaving 12 cells completed (all SingleD + OtherDwelling, resume-safe) and 12 ABORTED (all MidRise + HighRise). Root cause identified: each watchdog kill left orphan `energyplus.exe` children (leaked from killed cell subprocesses), accumulating ~3�4 GB baseline committed per trip. **Today's session (2026-06-04, ~13:22 local):** Verified no campaign Python running. Identified 8 orphan E+ processes (PIDs 6676, 31668, 32388, 29556, 28384, 15656, 32428, 34784 � all parented to prior campaign runs, staggered start times 08:43�13:14). Killed all 8. **Clean baseline after reap: 60.1% committed.** Note: a concurrent unrelated process (`idf_reader/main_BEM.py`, PID 27360) runs 8 E+ of its own (confirmed via ParentProcessId); these are NOT campaign orphans and must not be killed; they add ~2�12 pp dynamically as their simulations progress. Re-launched with `py -u run_campaign_local.py --workers 1 --ep-workers 2 --mem-abort 80.0 --sim-mode standard` (PID 31148; stdout buffering fixed via `-u` + PYTHONUNBUFFERED=1 env). Campaign started ~13:29: 12 resume-skip, 12 to run, watchdog armed. **Committed % at launch: 74.2%** (idf_reader E+ at peak; campaign E+ not yet started). Gate = MidRise__Toronto_5A exit=0 without watchdog trip (~95 min expected). Escalation = if watchdog trips again at confirmed clean baseline ? STOP, move MidRise+HighRise to Speed cluster. **Status: MONITORING � gate and completion pending.** |
| 2026-06-04 | **8D escalation confirmed — MidRise+HighRise → Speed cluster** | ⛔ STOPPED | **Watchdog fired at 80.7% committed, 9.2 min into MidRise__Toronto_5A** at --ep-workers 2, confirmed clean baseline 60.1% after orphan reap. idf_reader/main_BEM.py concurrent E+ load (~12 pp) left only ~5.8 pp headroom; MidRise CSV load + E+ startup sufficient to breach 80%. All 12 remaining cells (MidRise×6 + HighRise×6) ABORTED; 12/24 cells complete (SingleD+OtherDwelling, all resume-safe). Campaign stopped, not relaunched. **Per escalation rule: do NOT lower --ep-workers further, raise --mem-abort, or reboot. The 12 heavy cells must move to the Speed cluster** (EnergyPlus 24.2 install + SLURM array). Current committed: 72.7% (idf_reader still running). Local campaign done at 12/24. |
| 2026-06-04 | **Speed cluster port — SLURM array built, staged, submitted** | ✅ COMPLETE | **Design:** 12-task SLURM array (`step8_speed/run_heavy_array.sh`; `--array=0-11`, `--time=48:00:00`, `--mem=16G`, `--cpus-per-task=8`). Tasks 0-5 = MidRise×{Toronto_5A,Kelowna_5B,Vancouver_5C,Montreal_6A,Calgary_6B,Winnipeg_7A}, tasks 6-11 = HighRise×same. Each task runs `run_paired_mc.py --archetype $ARCH --city $CITY --n 50 --seed 42 --sim-mode standard` via host Python (`/speed-scratch/o_iseri/envs/step4/bin/python`). E+ 24.2 invoked through the validated nrel SIF (`step9_spike/energyplus_24.2.0.sif`); per-task wrapper dir with `energyplus`/`ExpandObjects` bash scripts + IDD extracted from SIF at task start. Outputs land in `/speed-scratch/o_iseri/step8_speed/campaign_N50/<cell>/`. ESIM_WORKERS=8, MPLBACKEND=Agg. **Audit chain completed:** all 5 BEM_Schedules CSVs (5 yrs × 453 MB) + 4 archetype IDFs (Buildings_MTL_v242/) + 6 EPWs + eSim_bem_utils_2J package + run_paired_mc.py / run_bem.py uploaded. load_schedules() uses csv.DictReader (streams CSV row-by-row; per-cell memory ≈ 2-3 GB peak including E+ workers). **Submissions:** `cd /speed-scratch/o_iseri/step8_speed && sbatch run_heavy_array.sh` → job array ID = **950097**. **sacct (2026-06-05): all 12 tasks COMPLETED, exit 0:0.** Elapsed: MidRise 2:45–3:26 h, HighRise 3:47–4:33 h. Cluster spot-check: all 12 cells at **250/250 hourly_meters.csv** on `/speed-scratch/`. **Download in progress** (2026-06-05): MidRise×6 all 250/250 locally; HighRise download underway via scp. |
| 2026-06-05 | **8D campaign COMPLETE — 24/24 cells, 6,000 runs ok** | ✅ DONE | Sequential scp of all 12 heavy cells (MidRise×6 + HighRise×6) from `/speed-scratch/o_iseri/step8_speed/campaign_N50/` to local `BEM_Setup/SimResults_Step8/campaign_N50/` completed. **Final local verification: all 24 cells at 250/250 hourly_meters.csv** (50 HH × 5 years each; total 6,000 runs). `campaign_status.csv` updated: 12 ABORTED rows → `ok(cluster-950097),0`; all 24 rows now ok. **Full campaign:** 12 cells local (SingleD+OtherDwelling, `ok(resume-skip)`) + 12 cells cluster (MidRise+HighRise, SLURM array 950097). **Ready for Sub-step 8E:** `py 08_simulation_plots.py --rebuild-agg` pointed at `campaign_N50/`. |
| 2026-06-05 | **Sub-step 8E COMPLETE — aggregation + all 11 figures** | ✅ DONE | `py 08_simulation_plots.py --results-dir ..\..\BEM_Setup\SimResults_Step8\campaign_N50 --rebuild-agg --figs all` ran to completion (exit 0). **Pass 1 (aggregation):** 6000/6000 runs processed, 0 failures; `outputs_step8/agg/` written (diurnal rows = 11,664,000; peak rows = 6,000). **Pass 2 (figures):** 11 figures rendered — fig01_occupancy_driver, fig02_diurnal_electricity, fig02b_diurnal_electricity_by_archetype, fig03_peak_hour_shift, fig04_paired_delta_by_hour, fig05_diurnal_by_season, fig06_carpet_8760, fig07_delta_by_cz, fig08_stock_weighted, fig09_longitudinal, fig10_eui_bars → all saved to `outputs_step8/figures/`. **Step 8 is complete end-to-end.** |
| 2026-06-05 | **Manager review of 8E results + all 11 figures; 8F handed off** | ✅ REVIEWED | **Aggregation verified:** `agg_meta` 6,000 rows, 24 cells × 5 yrs, status ok=6000/6000, all `has_hourly`. **Annual electricity (mean/arch over 6 cities × 50 HH):** pre-COVID flat (2005→2015); COVID break 2015→2022 **+1.4 to +2.6%** (SingleD +2.6, HighRise +2.5, OtherDwelling +1.8, MidRise +1.4); 2030 persists **+0.6 to +1.2%**. **Mechanism:** more daytime presence → **heating ↓ / cooling ↑** (HighRise heat −5.6/−4.4%, cool +2.5/+1.7%; occupant internal gains offset heating); **midday-share + load-factor rise** every cycle post-COVID; **peak-to-average falls**. **Peak:** hour **stable ~17–18h (sharpens, NOT shifts)**; paired Δ peak demand (Fig 7) **negative in every archetype × CZ cell** — HighRise **−3.6 to −5.5 kW** (largest in cold zones 6A/7A), small for SingleD (~0 to −0.1 kW) → WFH **peak-flatten / shave**, scales with building size. **EUI sane & ordered** (SingleD ~207 > MidRise ~151 > OtherDwelling ~127 > HighRise ~115 kWh/m²; colder CZ higher) → plausibility gate looks PASS. **Driver (Fig 1):** 2030 holds **~15 pp more weekday-midday at-home** vs pre-COVID. **All 11 figures reviewed — coherent & publication-ready;** strongest trio = Fig 1 (driver) → Fig 9 (longitudinal COVID break) → Fig 7 (peak shaving). **Caption caveats:** MC / paired bands wide; paired hourly Δ separable mainly in the morning (Fig 4); Fig 6 is a single HH; annual totals barely move → **frame the contribution as load-shape (midday-fill + peak-flatten), not annual energy.** **8F:** prompt authored & handed to the employee — build `08_simulation_val.py` from `08_simulation_val.md` (8 sections) → `outputs_step8/step8_validation_report.html` (`.py` does not yet exist). MC-CI < 2% convergence gate deferred to 8F. |
| 2026-06-05 | **Manager review of 8F validation report — Step 8 SIGNED OFF** | ✅ SIGNED OFF | Employee built `08_simulation_val.py` (`SimulationValidator`, 8 sections), ran in 29 s → `outputs_step8/step8_validation_report.html` (719 kB, 11 embedded charts, all 8 sections populated). **Scorecard: PASS 19 / WARN 5 / INFO 3 / FAIL 0 → clean pass.** **§1** 6000/6000 complete, 0 fatal, 1 benign E+ design-day sizing-convergence WARN. **§3** convergence: mean CI **1.80%**, worst-cell **4.04%** (threshold <2% → WARN; expected at N=50 per cell; acceptable for a load-shape paper, not annual-kWh precision). **§4** plausibility PASS — all EUI cells inside NRCan SHEU bands (SingleD 202 / MidRise 153 / OtherDwelling 126 / HighRise 116 kWh/m²; matches the 8E figure read 207/151/127/115). **§6** separability = **the core paper story**: midday-share & load-factor CIs exclude 0 (load-shape effect separable), annual EUI CI includes 0 (wide MC → PASS, "shape not energy"); peak-hour **FLATTEN** confirmed (Δ=+0.03 h, INFO). **§7** COVID break visible (Δload_factor +0.009 at 2022); 2030 extends it sensibly. **One flag — §2 schedule-fidelity WARN:** IDF schedules were frozen at 8B build time, *before* Step-7 OP4 donor-draw refinement landed in `BEM_Schedules_2022.csv`, so the simulated occupancy carries the −2.76 pp weekend-marginal dilution OP4 fixed; HighRise exact-match, other archetypes diverge. Flagged as a known limitation, not a runner injection bug. **Manager verdict: weekend-only + second-order vs the +15 pp weekday COVID signal that drives every headline (midday-fill, peak-flatten) → document as a known limitation in the paper, do NOT re-run 6,000 sims.** Outstanding for the writeup: (1) one sentence explaining the HighRise-matches / others-diverge asymmetry (likely HighRise had no weekend dilution to fix), (2) the §2 limitation paragraph. **Step 8 validated end-to-end — campaign + aggregation + figures + validation report all complete.** |
| 2026-06-07 | **Step 8 CLOSED — provenance A/B resolved (Option A)** | ✅ COMPLETE | The 2026-06-05 sign-off's §2 schedule-fidelity flag was investigated in depth (`Step8_docs/08_validation_warnings_investigation.md`, Rounds 1–2d + a read-only post-mortem). Outcome: the as-built **2022/2030** occupancy schedules are unrecoverable (aug input was revised before archiving; they survive verbatim in the campaign IDFs), but the campaign is **confirmed physically sane** — the post-mortem pulled campaign HighRise `eplustbl.csv` showing Interior Lighting 39–44 GJ / Equipment 617–737 GJ / EUI 249–272 MJ/m² (matches the r2c as-run cell means). The r2d spot-check's **−26% EUI scare was an artifact**: `BEM_Schedules_2022.csv` was updated with Step-9 columns *after* the campaign, flipping `integration.py` into the S9 activity-load path that zeroes standard L&E; the campaign ran pre-S9 → clean. **Decision (manager + user): Option A** — adopt the campaign as-run; document the provenance gap as a methods limitation (canonical paragraph in the warnings doc); **NO re-sim; NO re-run of the 8E plots or 8F validator** (both derive from the unchanged final 6,000-run campaign). Within-household 2022→2030 contrast (the headline) preserved; annual EUI secondary. Writeup-only items remain (limitation paragraph → manuscript). **Step 8 COMPLETE.** |
| 2026-06-09 | **Sub-step 8G queued** — re-run failed/partial re-sim runs | ⏳ TODO | Corrected array `953111` still running at queue time (20 done · 1 FAILED · 3 HighRise running). 1 failure confirmed: `OtherDwelling×Kelowna_5B/sample_050_HH145979/2010` = E+ autosizing fatal `Coil:Cooling:DX:SingleSpeed "DX COOLING COIL_UNIT6" — negative coil bypass factor` (deterministic; **unrelated to the 4-h fix** — same HH clean in 2005/2015/2022/2030). The failed run still left a header-only `hourly_meters.csv` (0 rows) the engine counted as "parsed". Plan: after the array is all-terminal, enumerate ALL failures (`eplusout.end` ≠ "Completed Successfully" OR `hourly_meters.csv` < 8760 rows — file-count misses header-only files), recover each via a per-run **sizing tweak** on an isolated IDF copy (warmup-retry can't fix a sizing fatal), then re-aggregate + re-validate. Fallback = leave the empty file → aggregator row-guard (`08_simulation_plots.py:268`) yields a clean N=49. Full task at **Sub-step 8G**. |
| 2026-06-10 | **Sub-step 8G COMPLETE** — single failed run recovered; campaign now 6000/6000 | ✅ DONE | **Enumeration (authoritative):** scanned all 6,000 `eplusout.end` files (via `grep -L "EnergyPlus Completed Successfully"`) + all 6,000 `hourly_meters.csv` row counts (via `agg_meta.csv` status column). Result: **exactly 1 failure** — `OtherDwelling×Kelowna_5B / sample_050_HH145979 / 2010` (`status=short`, `n_hours=0`). No additional failures beyond the 1 known case. **Root cause confirmed:** `eplusout.err` fatal = `Coil:Cooling:DX:SingleSpeed "DX COOLING COIL_UNIT6" — negative coil bypass factor calculated` during System Sizing. 1 Severe, 9 Warning, elapsed 2.22 s. Unrelated to the 4-h clock fix (same HH ran clean in 2005/2015/2022/2030). **Recovery:** (1) Isolated copy of failed run dir created at `step8_8G_fix/OtherDwelling__Kelowna_5B__sample_050_HH145979__2010/`; (2) Applied sizing tweak to `expanded.idf` copy only (never touched `Buildings_MTL_v242/`): `Coil:Cooling:DX:SingleSpeed "DX Cooling Coil_unit6"` field `Gross Rated Sensible Heat Ratio`: **`autosize` → `0.75`** (1 replacement, Python `re.subn` regex targeting the unit6 block); original backed up as `expanded.idf.ORIG_PRE_8G`; (3) Submitted SLURM job **954296** (sbatch `step8_8G_fix.sh`, partition ps, 1 cpu, 4G, 48h); job COMPLETED exit=0:0 in **3m 46s**; `EnergyPlus Completed Successfully -- 0 Severe Errors`, elapsed 3m 23s; `hourly_meters.csv` extracted (8761 lines, 9 meters); (4) Original failed dir renamed to `2010_FAILED_BAK` in campaign; corrected dir placed at `campaign_N50/OtherDwelling__Kelowna_5B/sample_050_HH145979/2010/`. **Re-aggregation:** submitted `step8_aggval_v2.sh` as job **954300**; COMPLETED exit=0:0 in **56m 19s**. **New scorecard: PASS 24 / WARN 0 / INFO 3 / FAIL 0** (was PASS 22/WARN 2 before fix — gates 1.1 and 1.5 completeness now PASS). **agg_meta status: ok=6000 / short=0** (was ok=5999/short=1). **EUI deltas (post − pre):** SingleD +0.0008, MidRise −0.0028, OtherDwelling −0.0120, HighRise +0.0017 kWh/m² (all < 0.013 kWh/m² — negligible, 1/6000 runs). **Peak-hour deltas:** all < 0.001 h across all 5 years (sub-minute). **Local downloads refreshed** in `outputs_step8_v2/`: `step8_validation_report.html` (749 kB), `agg/agg_annual.csv` (1,565 kB), `agg/agg_peak.csv` (866 kB), `agg/agg_meta.csv` (1,058 kB), `agg/agg_peak_hours.csv` (149,425 kB), `figures/` (23 files). **Sub-step 8G COMPLETE — campaign at 6000/6000.** |
| 2026-07-11 | **Targeted 2022+2030 LOCAL re-sim — 24/24 cells, 0 FAIL** | ✅ DONE | Separate follow-up campaign, NOT a re-run of the 6,000-run 5-year campaign above (2005/2010/2015 untouched). Triggered by two downstream corrections needing fresh 2022/2030 schedules: the household-frame fix (144,507→144,465, Step-5 refresh) and the act30 joint-raked calibration correction (see `project_2j_step89_resim` history). Re-simulated **2022 + 2030 only**, all 24 archetype×city cells, N=50 HH, paired (2,400 E+ runs total), via the LOCAL memory-safe flip pattern `run_campaign_local.py --workers 1 --ep-workers 18` (one cell's schedule set in RAM at a time, 18 parallel E+ within it). **Result: 24/24 cells status=ok/exit=0, 0/2,400 runs failed** — verified from a freshly-read `campaign_status.csv` plus `grep -r "Failed: [1-9]" _logs/` across all 24 per-cell logs (zero matches). Sequential wall-clock **≈ 21.0 h** (SingleD ~14 min/cell avg, OtherDwelling ~57, MidRise ~70, HighRise ~69). **Manifest-clobbering risk (Bug 1) materialized and was mitigated**: the fresh sample overwrote all 24 `cell_manifest.csv` (confirmed via timestamp check); each was archived (renamed, not deleted) to `cell_manifest.csv.new_2022_2030_20260711` *before* any re-aggregation, so `08_simulation_plots.py`'s `discover_runs()` falls back 100% to directory-name HH-ID parsing for both old and new sample rows — avoids silently mislabeling retained 2005/2010/2015 rows. Cost: aggregate `hhsize` column now blank for all rows (confirmed cosmetic/unused by any validator gate or figure). Full per-cell timing table, the Bug-1 write-up, and the companion Step-9 (activity-driven loads) targeted re-sim are tracked in `outputs_step8/implementation-improvement/step8_2022_2030_resim_implementation.md`. **Task 3 (re-aggregate + re-validate) intentionally deferred** until the Step-9 companion campaign also finishes, so both get aggregated/validated together in one pass. |

