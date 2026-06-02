# Step 8 — BEM Simulation: Implementation Plan
### Time-Series Occupancy → EnergyPlus: the 2022 → 2030 residential energy shift
#### GSS Occupancy Pipeline — Detailed Implementation Specification

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

### Sub-step 8C — Runner extension
Add **2030** to `run_bem.py` / `main.py` `COMPARATIVE_YEARS` (currently `2005…2025`) and point
2022 at the calibrated file. Versioned copy under our pipeline (do **not** edit conference/journal-1
code in place — copy + adapt).

### Sub-step 8D — Paired-MC batch
For each (archetype × CZ): sample 50 HH IDs (seed 42), run each across 5 years → 8760 series.
Persist raw E+ outputs + parsed time-series.

### Sub-step 8E — Aggregation + metrics
Compute the load-shape metrics, peak timing, stock-weighted ensemble, paired Δ(year) per HH.

### Sub-step 8F — Validation report
`08_simulation_val.py` → `outputs_step8/step8_validation_report.html` (see `08_simulation_val.md`).

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
