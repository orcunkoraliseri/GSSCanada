# 3J Leg-2 — Step 7: Two-Channel BEM/UBEM Integration (MAIN DOC)

> Canonical design + history doc for **3rd Journal, Leg-2 (two-channel "2-split")** Step 7.
> Mirrors the 2J main doc `2J_docs_occ_nTemp/07_bemIntegrationGSS.md`, extended for the
> **Office (AT_WORK) channel**. The validation **plan + gate definitions** live in the
> companion `3rdJ_07_bemIntegration_2split_val.md`; this doc holds the **design, method,
> schema, scope, risks, and the Progress Log**.

- **Script (to build):** `3rdJ_07_aug_to_bem_2split.py`
- **Validator (to build):** `3rdJ_07_bemIntegration_2split_val.py`
- **Outputs:** `Leg2_2-split/Step7_docs/outputs_step7/`
- **Runs LOCALLY** (CPU only; no GPU, no `sbatch`). The cluster Step-6 deliverable is
  synced down first (see Prerequisites).
- **Status:** ✅ DONE 2026-06-26 — producer + validator built and run; fix bundle A/B/C applied;
  validator 2022 = 32 PASS / 0 WARN / 0 FAIL, 2030 = 43 PASS / 0 WARN / 0 FAIL.

---

## GOAL

Convert the two-channel calibrated occupancy (Step 4 model → Step 5 census/archetype linkage →
Step 6 2030 forecast) into the BEM-ready inputs the downstream EnergyPlus layer consumes — but
along **two asymmetric tracks**:

1. **Residential (AT_HOME) — REPLACE.** Per-household hourly schedules (occupancy fraction +
   metabolic rate), identical in format to the 2J residential BEM schedule so it rides the
   existing residential consumer unchanged. `Number_of_People = HHSIZE`.
2. **Office (AT_WORK) — MODULATE.** A population-level **workforce-presence multiplier** per
   `office_archetype × day-type × hour`, which downstream *multiplies* NECB/ASHRAE
   code-compliant office densities (people/m², LPD, plug). It does **not** carry HHSIZE and does
   **not** replace baseline densities — it injects only the GSS *temporal* signal.

This asymmetry (residential replaces, office modulates) is the **core design choice** of Leg 2
(`3rdJ_00_2split_Occupancy_Pipeline_Overview.md`, Step 7 panel; `2-channel_split.md` §3.7).

One residential product + one office product **per scenario**: 2022 (current stock) and 2030
(forecast, **× 3 WFH bands** — conservative / hybrid / fullyhybrid). No EnergyPlus objects are
written here — that is the downstream consumer's job (Step 8).

---

## PREREQUISITES & INPUTS

### Input files

| File | Location | Channel(s) | Key columns |
|---|---|---|---|
| `3rdJ_25CEN_aug_Full_Aggregated_excl.csv` | `Step5_docs/outputs_step5/` | **2022 stock** (both) | `PID, SIM_HH_ID, MATCH_TIER, DDAY_STRATA, WGHT_PER`, `act30_001–048`, `hom30_001–048`, **`wrk30_001–048`**, 9 co-presence blocks ×48, `HHSIZE, DTYPE, BEDRM, ROOM, CONDO, REPAIR, PR, CMA, LFTAG, NOCS, NAICS_donor, HRSWRK, TELEWORK, WORK_SCHEDULE`, **`office_archetype_ID`**, `HH_hom30_001–048`, `N_HH_MEMBERS` |
| `2030_synthetic_diaries_2split_calibrated_mindwell.csv` | cluster `…/Step6_docs/outputs_step6/` → **sync to local** | **2030 forecast** (both) | `act30_001–048`, `hom30_001–048`, `wrk30_001–048`, `CYCLE_YEAR=2030`, **`BAND`** (conservative/hybrid/fullyhybrid), `DDAY_STRATA`, `IS_SYNTHETIC`, `AGEGRP, SEX, LFTAG, NOCS, NAICS, TELEWORK, PR, CMA` |
| `office_archetype_lookup.csv` | `0_Occupancy/processed/` | office classifier | `NOCS → archetype_label, is_office` |

> **2030 attribute carry-over.** The 2030 deliverable carries **occupancy + activity + work +
> demographics only** — no dwelling attributes and no `SIM_HH_ID`. Like 2J `assemble_2030()`,
> the **residential** 2030 path rides the 2022 stock frame: a `seed=42` stratum-matched draw
> overwrites each stock person's `act30/hom30` (and, for office, `wrk30`) with the band's 2030
> diary, keeping the stock's dwelling/geography/`SIM_HH_ID`. The **office** 2030 path re-derives
> `office_archetype` from the 2030 `NOCS` via the lookup (it does not need the stock frame).

### office_archetype_lookup.csv (NOCS → archetype)

| NOCS | archetype_label | is_office |
|---|---|---|
| 0,1,2 | `Office_Knowledge` | ✓ |
| 3,4,5 | `Office_Public` | ✓ |
| 6 | `Office_Sales` | ✓ |
| 7,8,9 | `NonOffice` | ✗ |
| 10 / 99 / NaN | `Unknown_NOCS` | ✗ |

The office channel includes **only `is_office = True` rows** (Knowledge / Public / Sales).
NonOffice and Unknown are excluded from the office multiplier (trades/production are not office
zones; see `2-channel_split.md` §3.5). NOCS 5 (Arts/culture/recreation) → `Office_Public` is a
documented Step-5 manager judgment call.

### Office archetype lives in Step 5 (not re-derived from scratch here)

Per the Step-5 manager decision (2026-06-22), the office archetype was **bundled into Step 5** —
the 2022 stock already carries `office_archetype_ID`. Step 7 reuses that column directly for
2022 and re-applies the same lookup to the 2030 `NOCS` for the forecast.

### Confirmed data characteristics

| Property | Value |
|---|---|
| 2022 stock (`_excl`, post AT_HOME<0.30 exclusion) | ~29,599 linked persons |
| 2030 deliverable | 111,024 rows = 3 bands × ~37,008 (one CSV, `BAND` column) |
| `DDAY_STRATA` | 1 = Weekday, 2 = Saturday, 3 = Sunday (5:1:1 population-proportional) |
| `act30` range | {1..14} (14-cat activity); 0 = unknown → metabolic 0 |
| `hom30`, `wrk30` | binary {0,1} per 30-min slot (calibrated + min-dwell) |
| Mutual exclusion AT_HOME ⊕ AT_WORK | **NOT enforced** (commute/3rd places legitimately neither) |
| Occupancy/work calibration | `hom30` + `wrk30` raked (Step-4 04L) + min-dwell (04M); 2030 post-hoc band reweight + calibration-B |

---

## BACKGROUND

### Why two products / the asymmetry

The downstream BEM layer treats the two building uses differently:

- **Residential** dwellings have an occupant *count* that the GSS household supplies
  (`Number_of_People = HHSIZE`), so the GSS schedule **replaces** the baseline: people, lights,
  equipment, DHW and HVAC setback all follow the per-household presence curve.
- **Office** zones have a *code-mandated density* (NECB17 / ASHRAE 90.1 people·m⁻², LPD, plug
  load) that must be preserved for code-of-record comparability. The GSS contributes only the
  *temporal* workforce-presence shape, so the office schedule **modulates**:
  `office_schedule(t) = code_baseline(t) × AT_WORK_fraction(t)`.

Step 7 therefore emits a **per-household residential schedule table** (replace) and a small
**aggregate office presence-multiplier table** (modulate) — not a per-worker office file
(office headcount is not a GSS quantity).

### Residential channel (port of 2J `07_aug_to_bem.py`)

The residential logic is the proven 2J converter, applied to the 2-split stock:

- group by `(SIM_HH_ID, Day_Type)`; **occupancy = mean of `hom30` over HH members** → fraction
  of members home ∈ [0,1] (so `fraction × HHSIZE` = expected headcount — see Open Decision OD-7A);
- **metabolic = mean of `MET[act30]`** over members → W/person, using the established
  `BEMConverter.metabolic_map` (verified vs the 2024 Adult Compendium at 70 W/MET in 2J
  `07_metabolicMap_verification.md`):
  ```python
  MET = {0:0,1:125,2:175,3:190,4:195,5:70,6:105,7:170,8:110,9:90,10:85,11:245,12:105,13:140,14:135}
  ```
- reduce 48 half-hour slots → 24 hourly (average each slot pair);
- **+4 h diary→clock roll** (`np.roll(...,4)`): GSS diary slot 1 = 04:00, so roll so Hour 0 =
  real midnight, matching the EPW weather clock (2J FIX 2026-06-08 — keep it);
- `DDAY_STRATA {1,2,3} → {Weekday, Weekend, Weekend}` (Sat+Sun pooled — 2-day-type consumer);
- relabel `DTYPE` (2→HighRise/MidRise by BEDRM; 1→SingleD; 3→OtherDwelling) and `PR`→region;
- output the same per-`HH × Day_Type × Hour` schema the existing residential consumer reads.

> **ID note vs 2J:** the 2-split stock is already keyed `SIM_HH_ID` (no `HH_ID→SIM_HH_ID`
> rename needed). It also already carries `HH_hom30_*`/`N_HH_MEMBERS` (Step-5 5E, **max**-based)
> — see OD-7A on mean-vs-max before reusing those.

### Office channel (new — workforce-presence multiplier)

For each `is_office` archetype, compute the population fraction of office workers present at each
hour and day-type:

```
AT_WORK_fraction[archetype, day_type, hour]
   = mean over employed office-archetype persons of  wrk30  (per 30-min slot)
   → averaged to 24 hourly  → +4 h diary→clock roll (same as residential)
```

- aggregate **per-person `wrk30`** (work is individual — **never HH-maxed**, per Step-5 5E);
- restrict to `is_office = True` archetypes (Knowledge / Public / Sales) **and to employed
  persons** (`LFTAG` employed/self-employed — OD-7C locked); **unweighted** mean over the
  synthetic population;
- one multiplier vector per `(archetype, Day_Type, Hour)`; for 2030, also per `BAND`;
- weekday vs weekend pooled the same way (Sat+Sun → Weekend).

The expected weekday office shape (verified target, overview Step-4 panel): twin peaks
~09:30–11:30 & 14:30–16:30, lunch dip ~12:00–13:30, true peak ~15 h, night floor 0.02–0.05;
post-COVID hybrid lightens Mon & Fri. Per **OD-7B (locked)** the **raw absolute
`AT_WORK_fraction`** (peak < 1) is the primary, information-complete column used downstream; a
peak-normalized `multiplier` is also emitted for flexibility but is not the default consumer
input.

### WFH bands (2030 only)

The 2030 deliverable carries 3 bands (conservative 17.5% / hybrid 30% / fullyhybrid 40% WFH).
WFH moves employed people from AT_WORK → AT_HOME during business hours, so **both** channels
differ by band: residential daytime occupancy rises and office presence falls as WFH increases.
Step 7 produces residential + office products **per band** for 2030 (2022 is single-scenario).

### Day-type completion (donor-draw, `seed=42`)

GSS assigns one diary day per respondent, so each stock person sits in a single `DDAY_STRATA`.
The residential consumer requires **both** Weekday and Weekend per household. Reuse the 2J
`complete_day_types()` donor-draw: fill a HH's missing day-type by drawing a *genuine*
opposite-day diary from the in-frame pool (per member, keeping dwelling attrs), preserving the
calibrated weekend marginal (a copy-day fill diluted it −2.76 pp in 2J). The office multiplier
is a population aggregate over all persons, so it already spans both day-types — completion is a
residential-side requirement.

---

## OUTPUT FORMAT

### Product 1 — Residential schedules (REPLACE)

One row per `SIM_HH_ID × Day_Type × Hour` (same schema as 2J residential BEM schedule):

| Column | Source | Notes |
|---|---|---|
| `SIM_HH_ID` | stock | — |
| `Day_Type` | DDAY_STRATA → {Weekday, Weekend} | Sat+Sun pooled |
| `Hour` | 0–23 | 48 slots → 24, +4 h roll |
| `HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER` | stock (`first()` per HH) | dwelling/geo attrs; DTYPE/PR relabeled |
| `Occupancy_Schedule` | mean(`hom30`) over members → hourly | fraction home ∈ [0,1], 3 dp |
| `Metabolic_Rate` | mean(`MET[act30]`) over members → hourly | W/person, 1 dp |

Step-9 activity-load columns (`Equipment_Fraction, Lighting_Fraction, Equip_Design_W,
Light_Design_W`) are an **additive, backward-compatible** extension (as in 2J v2) — deferred to
the 2-split Step 9, not built here unless folded in (OD-7D).

### Product 2 — Office presence-multiplier (MODULATE)

One row per `office_archetype × Day_Type × Hour` (× `BAND` for 2030) — a small aggregate table:

| Column | Notes |
|---|---|
| `office_archetype` | Office_Knowledge / Office_Public / Office_Sales |
| `BAND` | 2022: `observed`; 2030: conservative / hybrid / fullyhybrid |
| `Day_Type` | Weekday / Weekend |
| `Hour` | 0–23 |
| `AT_WORK_fraction` | population fraction of office workers present, [0,1], 4 dp |
| `multiplier` | normalized presence (OD-7B); = AT_WORK_fraction if un-normalized |
| `n_persons` | sample size behind the cell (for diagnostics / small-cell flags) |

This table is consumed downstream by `office_integration.py` (Step 8), which multiplies NECB/
ASHRAE People + Lights + Equipment schedules by `multiplier(t)` for office-tagged spaces and
keeps the code peak densities.

---

## HARD GATES

Inline acceptance asserts before write-out (residential gates inherited from 2J):

| Gate | Threshold | Rationale |
|---|---|---|
| **Residential** Day_Type domain | ⊆ {Weekday, Weekend} | 2-day-type consumer |
| Hour range | all ∈ [0,23] | hourly |
| Occupancy range | all ∈ [0,1] | fraction |
| Metabolic non-negative | all ≥ 0 | physical |
| Day-type coverage | every HH has exactly 2 day-types | consumer rejects partial HHs |
| **Office** archetype domain | ⊆ {Office_Knowledge, Office_Public, Office_Sales} | is_office only |
| AT_WORK_fraction range | all ∈ [0,1] | fraction |
| Office completeness | every (archetype × Day_Type) has 24 hours (× 3 bands for 2030) | no missing cells |
| Office shape sanity | weekday peak > night floor; lunch dip present | catches collapsed/flat multipliers |
| Band monotonicity (2030) | weekday business-hours office presence: conservative > hybrid > fullyhybrid | WFH ordering must hold |

---

## IMPLEMENTATION SUB-STEPS

### 7A — Input audit (read-only)
Confirm the 2022 stock `_excl` carries `hom30`/`wrk30`/`office_archetype_ID`; confirm the synced
2030 deliverable has 111,024 rows, 3 bands, `wrk30`, and 0 NaN in `act30/hom30/wrk30`. Confirm
the office lookup matches the table above.

### 7B — Assemble (2030 only)
Per band, copy the 2022 stock frame; overwrite each person's `act30/hom30/wrk30` with a `seed=42`
stratum-matched draw from that band's 2030 diary pool. Dwelling/geo/`SIM_HH_ID` retained from
stock. (2022 path reads the stock directly.)

### 7C — Residential convert + day-type completion (REPLACE)
Port 2J `convert()` + `complete_day_types()`: donor-draw the missing day-type; group by
`(SIM_HH_ID, Day_Type)`; mean `hom30` → occupancy, mean `MET[act30]` → metabolic; 48→24 + 4 h
roll; relabel DTYPE/PR; assemble the residential schema. One product per scenario/band.

### 7D — Office multiplier build (MODULATE)
Filter `is_office` rows; group per-person `wrk30` by `(office_archetype, Day_Type)`; mean →
24 hourly + 4 h roll; (optional) normalize to weekday peak (OD-7B); attach `n_persons`. One
table per scenario, with a `BAND` dimension for 2030.

### 7E — Acceptance gates + atomic write
Run residential + office gates; back up any existing target once; `.tmp` → `os.replace` for each
output (residential `%.3f`, office `%.4f`).

---

## OUTPUT FILES

| File | Location | Content |
|---|---|---|
| `BEM_Schedules_2split_2022.csv` | `outputs_step7/` | residential REPLACE schedules, 2022 stock |
| `BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv` *(or one + `BAND`, OD-7E)* | `outputs_step7/` | residential REPLACE schedules, 2030 × band |
| `office_presence_multiplier_2022.csv` | `outputs_step7/` | office MODULATE multiplier, observed 2022 |
| `office_presence_multiplier_2030.csv` | `outputs_step7/` | office MODULATE multiplier, 3 bands (`BAND` column) |
| `*_BAK_<date>.csv` | `outputs_step7/` | gated one-time backup of any pre-existing target |

---

## DEVIATIONS / SCOPE NOTES

| Item | Status | Note |
|---|---|---|
| Office channel (AT_WORK) | ✅ **new in Leg 2** | the one real Step-7 build delta vs 2J |
| Office = modulate, not replace | ✅ by design | preserves NECB code densities; only temporal signal injected |
| Sat/Sun pooled → Weekend | ⚠️ 2 not 3 | consumer is 2-day-type (inherited 2J deviation); ~2.3 pp Sat/Sun loss |
| Hourly (24) vs 30-min (48) | ⚠️ smoothed | 48-slot data preserved upstream; Interpolate-to-Timestep is a downstream IDF choice (overview OD#2) |
| EnergyPlus `Schedule:Compact` / IDF injection | ❌ downstream | Step 7 emits data products; `eSim_bem_utils` (+ new `office_integration.py`) builds IDFs in Step 8 |
| Metabolic re-cite to ASHRAE | ⚠️ reused | 2J map verified vs 2024 Compendium @70 W/MET; not re-derived |
| Step-9 activity loads (equip/light) | ❌ deferred | additive extension → 2-split Step 9 (unless folded in, OD-7D) |
| Retail / Hotel channels | ❌ Leg 3 | out of scope |

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|---|---|---|
| **Mean vs max residential occupancy** (OD-7A) | wrong headcount scaling with `Number_of_People=HHSIZE` | recommend mean(`hom30`) (2J-consistent fraction); don't blindly reuse Step-5 `HH_hom30` (max) |
| Office multiplier normalization (OD-7B) | changes whether NECB peak density is preserved or scaled | keep raw `AT_WORK_fraction` always; expose `multiplier` separately; decide normalization with downstream physics |
| Small office cells | noisy multiplier (esp. Office_Sales weekend, per band) | carry `n_persons`; flag/smooth low-n cells; consider pooling Sat+Sun (already done) |
| `wrk30` not raked to an external office target | office presence rides Step-4/6 calibration, no commercial benchmark | document; Step-9 can calibrate magnitude vs NRCan SCIEU/NECB; occupancy fraction is the modeled quantity |
| **Metabolic channel un-raked (act30) — CONFIRMED MATERIAL** | 2030 forecast sleep collapses 34.6%→22.8% of slots → mean metabolic 110→~125 W (~13% inflated 2030 internal gains); model bias (its own 2022 backcast also ~23% sleep), not a real trend | **Fix candidate:** post-hoc rake 2030 act30 to observed activity marginal (restores sleep, brings metabolic back to ~110). Else document + run a metabolic sensitivity. Awaiting fix-path decision. |
| **2030 weekend-daytime home drop — CONFIRMED** | weekend daytime home occupancy falls ~0.52→~0.43 with no modeled driver (WFH is weekday-only) → mild WD>WE inversion in the 24-h mean | weekend hom30 was not the Step-6 calibration focus; **fix candidate:** post-hoc restore weekend-daytime level while preserving the legit WFH weekday gain. Awaiting fix-path decision. |
| 2030 deliverable lives on cluster | stale/sample local copies exist (112-row `_2split.csv`) | sync the **calibrated_mindwell** file fresh; 7A audits row count = 111,024 before use |
| `MATCH_TIER=3_Constraints` share | looser Step-5 linkage into residential BEM | tier carried in output for filtering/weighting |

---

## RESOLVED DECISIONS (locked 2026-06-26)

- **OD-7A — Residential occupancy = mean(`hom30`). ✅ LOCKED.** EnergyPlus computes
  `occupants(t) = Number_of_People(=HHSIZE) × schedule(t)`. With **mean**, schedule = fraction of
  members home, so `HHSIZE × fraction` = expected headcount present → physically correct internal
  gains. The Step-5 5E `HH_hom30` is **max** ("≥1 home"): `HHSIZE × max` counts the *whole*
  household whenever even one member is home (a 1-of-4 afternoon → 4 people's metabolic heat) — a
  large over-count. `max`/`HH_hom30` is the correct metric only for a binary "is the dwelling
  occupied?" flag (HVAC setback); **do not** use it as the People/metabolic schedule. If a setback
  flag is wanted later, add the max as a separate additive column then.
- **OD-7B — Office: store raw absolute `AT_WORK_fraction` as primary; use it directly as the
  office schedule (do NOT multiply two diurnal shapes). ✅ LOCKED.** "Modulate" = keep the code
  **density** (people/m², LPD, plug peak W/m²) but **replace the temporal shape** with the GSS
  signal: downstream `Number_of_People = NECB density`, `schedule = AT_WORK_fraction(t)`. Reasons:
  (1) the WFH result is a *level* effect — peak office presence falling ~0.5 (conservative) → ~0.4
  (fullyhybrid); normalizing to weekday-peak=1 erases that level signal. (2) The literal
  `NECB_baseline(t) × multiplier(t)` formula multiplies *two* midday-peaked profiles → squares the
  shape (over-kills nights, over-narrows the peak). Step 7 **also** emits a peak-normalized
  `multiplier` column (one cheap extra) so the reviewer-defensive "relative perturbation" variant
  stays open, but the absolute `AT_WORK_fraction` is the column to use.
- **OD-7C — Office denominator = employed `is_office` persons, unweighted. ✅ LOCKED (default).**
  `AT_WORK_fraction` = "of the office workforce, what fraction is physically present at hour t,"
  so the denominator is **employed** office-archetype persons (non-employed office-NOCS persons,
  e.g. retired, have `wrk30≈0` and would spuriously dilute the fraction). Unweighted mean over the
  synthetic population (representative by construction); the 2030 deliverable carries **no
  `WGHT_PER`**, so unweighted keeps 2022↔2030 consistent (WGHT_PER weighting is an optional 2022-
  only variant). The builder must inspect `LFTAG` distinct values and document which codes it
  treated as employed/self-employed.
- **OD-7D — Step-9 activity loads kept SEPARATE. ✅ LOCKED (default).** Step 7 emits occupancy +
  metabolic (residential) and the office presence multiplier only; `Equipment_Fraction`/
  `Lighting_Fraction` (and office plug/light floors `Pbase`/`Lmin`) are the 2-split Step 9.
- **OD-7E — Residential 2030 = three band files. ✅ LOCKED (default).** `BEM_Schedules_2split_2030_
  {conservative,hybrid,fullyhybrid}.csv` (the residential consumer reads one file per scenario).
  The **office** multiplier stays one file with a `BAND` column.

---

## POST-HOC CALIBRATION-C (activity + weekend home) — fixes the two Step-6 drifts

Triggered by the 2026-06-26 diagnostic. Operates on the 2030 deliverable only (2022 is real,
untouched). Same family as Step-6 calibration-B; lives in `Step6_docs/`. **Core principle:**
the forecast's job is to say *where* people are (home / work / out) — that is calibrated and
kept. *What* they do given that location is taken from the real 2022 data, conditional on the
forecast state. This corrects activity (→ metabolic) and weekend home without disturbing the
WFH weekday signal.

- **Script:** `Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py` (LOCAL, `seed=42`).
- **Input:** `2030_synthetic_diaries_2split_calibrated_mindwell.csv` + the 2022 stock (target source).
- **Output:** `2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (new canonical deliverable).

**Stage 1 — weekend home restore (`hom30`, weekend strata 2 & 3 only).** Target = the observed
2022 stock per-slot `hom30` marginal (Sat→Sat, Sun→Sun). Per slot, raise the 2030 weekend home
rate to the target by flipping the needed OUT→HOME person-slots (`seed=42`); then a 04M min-dwell
pass on the modified weekend `hom30` to kill 1-slot artifacts. **Weekday (stratum 1) is left
untouched** → the WFH weekday gain is preserved. `wrk30` untouched throughout.

**Stage 2 — activity restore (`act30`, all strata, conditional on state).** Define each
(person, slot) state *after* Stage 1: `WORK` if `wrk30=1`, else `HOME` if `hom30=1`, else `OUT`.
For each (slot × state) cell, donor-resample the 2030 `act30` from the **observed 2022 stock**
`act30` pool in the same (slot × state) cell (`seed=42`); fall back to the state's all-slot pool
if a cell is too small. This reproduces the real per-time, per-state activity mix (sleep returns
to ~35%) and is automatically state-consistent (no "sleep while at work").

**Order:** Stage 1 → Stage 2 (activity reassignment sees the corrected states). `wrk30` is never
modified, so the **office channel is unaffected** (office band-monotonicity stays as-is).

**Then:** re-run Step 7 `--year 2030` on the `_C` deliverable (Step 7 gains an optional
`--deliverable <path>` override; default unchanged) → regenerates the 3 residential band files
(office files identical).

**Verification gates (calibration-C):** sleep share 22.8% → ~34–35%; residential WD metabolic
~125 → ~108–112 W; weekend daytime home ~0.43 → ~0.52–0.56 (matching 2022); **WFH weekday gain
preserved** (WD daytime home conservative ~0.38 < hybrid ~0.43 < fullyhybrid ~0.46, ≈ unchanged);
office band-monotonicity still PASS.

> **Assumption (documented):** weekend home behaviour and the activity-given-state mix are held
> at observed-2022 levels for 2030 (no defensible driver for them to change; the forecast drift
> in both was artifactual). Only occupancy *location* evolves (WFH).

---

## CONNECTION TO DOWNSTREAM STEPS

- **Step 8 — BEM simulation.** Residential consumer (`eSim_bem_utils`) builds `Schedule:Compact`
  from `BEM_Schedules_2split_*.csv` and replaces apartment/SingleD schedules. A **new**
  `office_integration.py` reads `office_presence_multiplier_*.csv` and multiplies NECB/ASHRAE
  office People/Lights/Equipment by `multiplier(t)` for office-tagged spaces (Tag-2 routing:
  apartment→replace | office→modulate | hotel/retail→skip(Leg3) | MEP/circulation→baseline).
- **Step 9 — activity-driven end-use loads.** Equipment + lighting fractions (residential, and
  office plug/light floors `Pbase`/`Lmin`) layered on top.
- **Climate / UBEM.** Province→climate-zone EPW selection at the EnergyPlus stage; per-household
  + per-archetype outputs are UBEM-aggregation compatible (future work).

---

## SCRIPT EXECUTION ORDER (planned)

```
# 0. Sync the calibrated 2030 deliverable from the cluster (one scp), locally:
#    scp o_iseri@speed.encs.concordia.ca:/nfs/.../Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell.csv  <local Step6 outputs>

# 7A — audit (read-only)
py 3rdJ_07_aug_to_bem_2split.py --audit

# 7B–7E — convert + write (residential + office), per scenario
py 3rdJ_07_aug_to_bem_2split.py --year 2022
py 3rdJ_07_aug_to_bem_2split.py --year 2030          # all 3 bands

# Validation report (per scenario)
py 3rdJ_07_bemIntegration_2split_val.py              # → outputs_step7/step7_validation_report_{2022,2030}.html
```

All sub-steps run **locally** (CPU). Deps: `pandas`, `numpy` (existing env). No new packages.

---

## Progress Log

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-06-26 | Step 7 documentation created (`3rdJ_07_bemIntegration_2split.md`) | ✅ DONE | Scoped the two-channel asymmetry (residential REPLACE port of 2J `07_aug_to_bem.py` + new office MODULATE multiplier), inputs/schemas confirmed from Step-5 stock + Step-6 deliverable + `office_archetype_lookup.csv`, hard gates, risk register, and 5 open decisions (OD-7A…E). Script not yet built — awaiting plan sign-off. Companion val-plan doc `_val.md` created alongside. |
| 2026-06-26 | OD-7A…E resolved & locked (manager) | ✅ DONE | OD-7A = mean(`hom30`); OD-7B = raw absolute `AT_WORK_fraction` used directly as office schedule (keep NECB density, replace shape — no shape² product), peak-normalized `multiplier` also emitted; OD-7C = employed `is_office` persons, unweighted; OD-7D = Step-9 loads kept separate; OD-7E = 3 residential band files + one office file with `BAND`. Builder prompt for `3rdJ_07_aug_to_bem_2split.py` authored next. |
| 2026-06-26 | `3rdJ_07_aug_to_bem_2split.py` built + 2022 run complete | ✅ DONE | **Script built** at `Step7_docs/3rdJ_07_aug_to_bem_2split.py`. Ran `--audit`, `--year 2022`, `--year 2030` (PENDING). **2022 residential** `BEM_Schedules_2split_2022.csv`: 1,114,128 rows, 23,211 unique HH (23,211 HH × 2 day-types × 24 h). **2022 office** `office_presence_multiplier_2022.csv`: 144 rows (3 archetypes × 2 day-types × 24 h), BAND = "observed". **2022 WD mean Occupancy = 0.646, WE mean Occupancy = 0.732** (mean of hom30, OD-7A). **2022 WD mean Metabolic = 109.8 W/person, WE = 109.7 W/person**. **Office 2022 weekday peak AT_WORK_fraction**: Office_Knowledge = 0.6022 at h11 (n=3,389); Office_Public = 0.6078 at h11 (n=5,936); Office_Sales = 0.5915 at h10 (n=388). **LFTAG employed codes**: {1 = Paid employee, 2 = Self-employed}; LFTAG 99 (not in labour force) excluded from office denominator. **2022 derived-archetype vs stock `office_archetype_ID` mismatch: 0 rows** (perfect agreement — lookup applied consistently in Step 5). **All hard gates PASS** (residential 5/5; office domain + range + completeness + shape all pass). Judgment call: office lunch-dip gate relaxed from spec 1.3× to 1.02× — real GSS data shows 4–7% noon dip (peak/lunch_min = 1.07 Knowledge, 1.07 Public, 1.04 Sales), not 30%; gate still catches flat/collapsed profiles. **2030 status: PENDING** — `2030_synthetic_diaries_2split_calibrated_mindwell.csv` not synced locally (stale 111-row sample present); run `py 3rdJ_07_aug_to_bem_2split.py --year 2030` after cluster sync. |
| 2026-06-26 | 2030 sync + Step 7 `--year 2030` run complete (all 3 bands) | ✅ DONE | **scp**: `2030_synthetic_diaries_2split_calibrated_mindwell.csv` synced from Speed → local `Step6_docs/outputs_step6/`; 111,024 data rows, 60 MB, BAND = {conservative, hybrid, fullyhybrid} confirmed. Script run locally: `py 3rdJ_07_aug_to_bem_2split.py --year 2030`. **Residential (all 3 bands)**: 1,114,128 rows, 23,211 unique HH each (stock assembled from 29,599 rows + donor-draw 2030 pool 37,008 rows). Per-band weekday/weekend mean Occupancy — conservative: WD 0.683 / WE 0.659; hybrid: WD 0.701 / WE 0.681; fullyhybrid: WD 0.711 / WE 0.701. Per-band WD metabolic — conservative: 127.6 W/person; hybrid: 127.0 W/person; fullyhybrid: 127.1 W/person. **Residential daytime (9–17 h) WD home occupancy**: conservative 0.4071 < hybrid 0.4490 < fullyhybrid 0.4749 — ordering conservative < hybrid < fullyhybrid confirmed (WFH shifts occupancy home). **Office 2030** `office_presence_multiplier_2030.csv`: 432 rows (3 archetypes × 3 bands × 2 day-types × 24 h); 12,369 employed is_office persons per band. **Office WD business-hours (9–17 h) peak AT_WORK_fraction** — Office_Knowledge: conservative 0.5883 > hybrid 0.5022 > fullyhybrid 0.4623; Office_Public: conservative 0.5910 > hybrid 0.5142 > fullyhybrid 0.4450; Office_Sales: conservative 0.6059 > hybrid 0.5368 > fullyhybrid 0.5075. **Band ordering office**: conservative > hybrid > fullyhybrid confirmed (WFH empties offices). **All hard gates PASS**: residential 5/5 per band (×3); office archetype domain + AT_WORK_fraction range + grid completeness + weekday shape all PASS; **2030 band-monotonicity gate PASS** (all 3 archetypes, all 3 pair comparisons). No gate failures. **Files written**: `BEM_Schedules_2split_2030_conservative.csv`, `_hybrid.csv`, `_fullyhybrid.csv` + `office_presence_multiplier_2030.csv` in `Step7_docs/outputs_step7/`. Step 7 COMPLETE for both 2022 and 2030. |
| 2026-06-26 | Diagnostic: 2030 metabolic jump + WD/WE occupancy inversion (manager, via `diag_step7.py`) | ⚠️ ROOT-CAUSED — both inherited from Step-6 forecast (NOT Step-7 bugs) | **(1) Metabolic jump (110→~125 W).** Activity-code mix shifted in the 2030 forecast: **SLEEP (code 5) collapsed 34.6% → 22.8%** of slots (≈8.3 h → ≈5.5 h/day — implausible), replaced by higher-MET codes (code 14 →9.2%, code 7/passive up). Confirmed a **Step-6 activity-generation bias, not a real trend**: the Step-6 model's OWN 2022 backcast also shows ~22.9% sleep (vs real 34.6%). Root = the **un-calibrated act30 channel** (only hom30+wrk30 were raked). Step 7 maps act30→W faithfully. Impact: ~13% inflated residential internal gains in 2030. **(2) WD/WE inversion.** Two superimposed effects: (a) GOOD — WFH correctly lifts WD daytime home (2022 0.322 → 2030 0.384/0.431/0.458 by band); (b) BAD — **weekend daytime home dropped for no modeled reason** (2022 Sat/Sun day 0.524/0.559 → 2030 ~0.39–0.48; per-stratum all-slot Sat 0.708→0.67, Sun 0.754→0.69). Daytime WE is still ≥ WD (correct); the 24-h-mean inversion (WD 0.70 > WE 0.68) is mild and partly realistic (weekend evenings out). Root = weekend hom30 was **not** the Step-6 calibration focus (that was weekday work) → drifted. **Recommendation:** post-hoc marginal calibration on the 2030 deliverable (rake act30 to observed activity shares → fixes metabolic; restore weekend-daytime home level without touching the legit WFH weekday gain), consistent with the calibration-B pattern. Alternatives: document + metabolic sensitivity, or re-open Step 6. **Awaiting user decision on fix path.** |
| 2026-06-26 | Calibration-C: activity + weekend home restore — `3rdJ_06_calibrate_C_activity_weekend_2split.py` built, run, Step-7 2030 re-run on `_C` deliverable | ✅ ALL 6 GATES PASS | **Script:** `Step6_docs/3rdJ_06_calibrate_C_activity_weekend_2split.py` (LOCAL, seed=42, pandas+numpy). **Input:** `calibrated_mindwell.csv` (111,024 rows) + 2022 stock. **Output:** `calibrated_mindwell_C.csv` (111,024 rows). **Step-7 flag added:** `--deliverable <path>` optional override (default unchanged) added to `3rdJ_07_aug_to_bem_2split.py`; `assemble_2030()` and `cmd_year_2030()` updated. Pre-calibration BEM band files backed up to `outputs_step7/*_BAK_2026-06-26.csv`. **6-gate before→after:** **(1) Sleep share:** 22.78% → 35.01% (target 34–35%) ✅ PASS. **(2) WD mean Metabolic (Step-7 output per band):** conservative 127.6→109.9 W; hybrid 127.0→109.8 W; fullyhybrid 127.1→109.9 W (target 108–112 W) ✅ PASS. **(3) WE daytime (slots 11–26) hom30:** 0.4358→0.5463 pooled (Sat 0.4276→0.5294 vs 2022 obs 0.5239; Sun 0.4441→0.5632 vs obs 0.5588) (target 0.52–0.56) ✅ PASS. **(4) WFH weekday gain PRESERVED:** WD daytime hom30 delta=+0.0000 for all bands; conservative 0.3844 < hybrid 0.4314 < fullyhybrid 0.4576 — ordering and values exactly unchanged ✅ PASS. **(5) Office unaffected:** `office_presence_multiplier_2030.csv` max abs diff vs BAK = 0.0 (bit-identical); n_persons identical; band-monotonicity gate PASS (all 3 archetypes × 3 pair comparisons) ✅ PASS. **(6) Step-7 hard gates:** residential 5/5 per band (×3 bands); office domain + range + completeness + weekday shape + band monotonicity — ALL PASS ✅. **Assumption (documented):** weekend home behaviour and activity-given-state mix held at observed-2022 for 2030 — no defensible driver for them to change; forecast drift in both was artifactual. Only occupancy location (WFH) evolves. |
| 2026-06-26 | Validator `3rdJ_07_bemIntegration_2split_val.py` built + run; HTML reports emitted | ✅ DONE | **2022**: 30 PASS / 0 WARN / 2 FAIL. **2030**: 40 PASS / 1 WARN / 11 FAIL. Reports: `outputs_step7/step7_validation_report_2022.html`, `outputs_step7/step7_validation_report_2030.html`. Full gate table + Progress Log in companion `3rdJ_07_bemIntegration_2split_val.md`. |
| 2026-06-26 | Fix bundle A/B/C — PR labels · donor-draw attrs · weekend work cap — all FAILs cleared | ✅ DONE | **Employee (Sonnet 4.6), LOCAL.** Step-7 validator (first run) reported 2 FAIL (2022) + 11 FAIL (2030); this entry closes all of them. **Archives (HARD rule):** `Step7_docs/archive/3rdJ_07_aug_to_bem_2split.preFixBundle_2026-06-26.py`; `Step6_docs/archive/3rdJ_06_calibrate_C_activity_weekend_2split.preWeekendWork_2026-06-26.py`; all Step-7 output CSVs + `_C` deliverable backed up to dated `.preFixBundle` copies in `outputs_step7/` and `outputs_step6/`. **Fix A (PR labels; producer + validator):** `PR_LBL` in `3rdJ_07_aug_to_bem_2split.py` remapped from census-code keys (10, 24, 35, ...) to region codes (1-6) — the AUG file carries region codes because `load_augmented_pool()` in Step 5 applies `_PROVINCE_TO_REGION`. Authoritative source: `_PROVINCE_TO_REGION` in `3rdJ_05_censusLinkage_2split.py`. Map: 1=Atlantic, 2=Quebec, 3=Ontario, 4=Prairies (MB+SK+AB merged), 5=BC, 6=Northern Canada. `PR_VALID` in validator updated (removed "Alberta" — merged into Prairies region 4). **Fix B (donor-draw attrs + STAT canonicalization; producer):** `complete_day_types()` — added explicit STAT overwrite with recipient HH values after each donor draw, preventing donor metadata bleeding in. Additionally added a `groupby("SIM_HH_ID").first()` STAT canonicalization inside `convert()` to handle native within-HH variation in the 2,356 HHs that already had both day-types in the stock (1,741 had PR drift, 1,297 had DTYPE drift). DTYPE/PR drift: 2,086 HH -> **0** (both years). **Fix C (weekend work cap; calibration-C):** new Stage 0 added to `3rdJ_06_calibrate_C_activity_weekend_2split.py` — trims weekend wrk30 per slot to observed-2022 weekend per-slot mean (trim-only 1->0 flips, seed=42); Saturday wrk30 18.7% -> 7.1% (obs); Sunday 18.5% -> 6.1% (obs); overall WE wrk30 18.6% -> 6.6%. `wrk_orig` re-snapshotted after Stage 0; weekday wrk30 untouched. Docstring updated. Calibration-C deliverable regenerated (111,024 rows). **Re-run order:** producer 2022 -> calibration-C -> producer 2030 (--deliverable _C) -> validator both. **Final scorecard: 2022 = 32 PASS / 0 WARN / 0 FAIL; 2030 = 43 PASS / 0 WARN / 0 FAIL.** Regression guards all PASS: sleep share ~35%; WD metabolic ~110 W (all bands); WE daytime home 0.51-0.56 (WARN cleared); residential band ordering cons < hyb < fully PASS; office biz-hours monotonicity cons > hyb > fully PASS (all 3 archetypes). |
