# 3J Leg-3 — Step 7: Four-Channel BEM/UBEM Integration (MAIN DOC)
### `office_integration.py` → `commercial_integration.py::inject_mixed_use()` — one Tag-2 dispatch, four channels; MODULATE not REPLACE for every commercial channel — runs LOCALLY (product build) + injection at Step-8 time

---

## GOAL

Generalize the Leg-2 injection asymmetry to four channels and build the per-channel schedule **products** Step 8 consumes:

| Channel | Injection | Formula | People count |
|---|---|---|---|
| Residential (✅ Leg 1/2) | **REPLACE** | `schedule(t) = presence(t)·default(t) + (1−presence(t))·baseload` | `Number_of_People = HHSIZE` |
| Office (✅ Leg 2) | **MODULATE** | `necb_office_baseline × AT_WORK_fraction(t)` | NECB density 25.0 m²/person — never HHSIZE |
| Retail (⚠️ Leg 3) | **MODULATE** | People: `0.95 × shape_c_d(t)` in customer hours (peak-normalized, dr_L3-06); staff-only shoulder slots (baseline ≤ 0.10) keep the code schedule unmodified | NECB retail density ~3.7 m²/person — **never scaled** |
| Hotel guest rooms (⚠️ Leg 3, non-GSS) | **MODULATE, monthly** | `necb_hotel_guestroom_baseline × hotel_multiplier(t, month, PR)` | NECB hotel density — never scaled |

> **✅ Retail normalization (RESOLVED 2026-07-02, dr_L3-06 / OD-11).** Raw-fraction injection is REJECTED (unanimous in the TUS-to-BEM literature — Richardson et al. 2010; IEA Annex 66/Haldi et al. 2017; Reinhart & Cerezo Davila 2016; it would collapse retail to ~8 % of design load). The injector formula is
> `retail_schedule_multiplier(t,c,d) = 0.95 × [at_retail_fraction_c_d(t) / max_t(at_retail_fraction_c_d(t))]`
> where 0.95 = NECB 2017/2020 retail/sales peak fraction (Table A-8.4.3.2.(1)-A). The 2005→2022 level drift (~2.3 % → ~2.1 %) is **deliberately routed to the Step-6B lever** (applied BEFORE this normalization), not absorbed here — clean amplitude sensitivity.

## PREREQUISITES & INPUTS

| Input | Path | Notes |
|---|---|---|
| Residential aggregated stock (2022) | Leg-3 `Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated[_excl].csv` | frame counts from the Leg-3 Step-5 record — never assume Leg-2's 23,150 |
| 2030 diaries | Leg-3 `Step6_docs/outputs_step6/2030_synthetic_diaries_4split_calibrated_mindwell_C.csv` | **the `_C` file is the only valid 2030 source** (Leg-2 hard-learned); the builder must hard-fail on a non-`_C` default |
| Office archetype lookup | `0_Occupancy/processed/office_archetype_lookup.csv` | reused |
| Retail lever files | `Step6_docs/outputs_step6/at_retail_fraction_2030_*.csv` | per band (+ QC-Sunday variant) |
| Hotel multipliers | `0_Occupancy/forecasts/hotel_multiplier_2030.csv`, `0_Occupancy/processed/hotel_multiplier_lookup.csv` | per month × PR × band |
| Historical cycles | Step-8A-style generation for 2005/2010/2015 retail fractions | per cycle × day-type |

## OUTPUT PRODUCTS (all under `outputs_step7/`)

1. **Product 1 — residential** `BEM_Schedules_4split_{2022,2030_<band>}.csv` (13-col, verbatim Leg-2 schema).
2. **Product 2 — office** `office_presence_multiplier_{2022,2030}.csv` (7-col, verbatim Leg-2 schema).
3. **Product 3 — retail (NEW)** `retail_presence_multiplier_{cycle|2030_<band>}.csv`:
   `Day_Type ∈ {Weekday, Saturday, Sunday}, PR ∈ {QC, AB}, Hour 0–23 (30-min slots ×2 → 48 rows/day-type), at_retail_fraction, shape (peak-normalized), multiplier (= 0.95 × shape), staff_shoulder_flag`
   — per-cycle × day-type peak normalization computed here; Sunday differs by PR (regulated QC vs deregulated AB).
4. **Product 4 — hotel (NEW)** `hotel_schedule_multiplier_{2022,2030_<band>}.csv`:
   `PR, MONTH 1–12, Day_Type ∈ {Weekday, Weekend}, slot 1–48, s_t, monthly_rate, multiplier (= s_t × monthly_rate)`
   — s(t) from the dr_L3-05 table (plateau 1.00 22:00–06:00, trough 0.200 wd / 0.308 we); holiday = weekend (limitation, recorded).

## SCENARIO MATRIX (2030)

The three per-channel levers (office WFH × retail in-store × hotel SARIMA) would cross to 27 combinations. **Recommended default (execution-time confirm): 3 aligned bundles + baseline** —
`B-cons = {WFH conservative, retail 0.90, hotel 0.92/tilt}`, `B-central = {hybrid, 0.97, 1.00}`, `B-opt = {fullyhybrid, 1.05, 1.05/tilt}` — plus one-at-a-time sensitivity re-runs per channel off B-central (6 extra product sets, cheap: products are CSVs). The full 27-cross remains a re-run option, not a default. Record the chosen matrix in the Progress Log before Step 8 consumes it.

## TAG-2 ROUTING TABLE (verbatim spec §4 — dispatch is exact `Tag 2 == "<literal>"`, not substring)

| Tag 2 (verbatim from IDF) | Channel | Injection |
|---|---|---|
| `HighriseApartment Apartment` | Residential | per-household TUS, `Number_of_People = HHSIZE` |
| `HighriseApartment Corridor`, `HighriseApartment Office` | Residential (common) | residential multiplier on Lights only |
| `OpenOffice`, `ClosedOffice` | Office | NECB baseline × `AT_WORK_fraction(t)` |
| `Conference`, `Classroom`, `Dining`, `Restroom` | Office (support) | same as Office |
| `Retail Retail`, `Retail Back_Space`, `Retail Point_of_Sale`, `Retail Entry` | Retail | `0.95 × shape_c_d(t)`; staff-only slots keep baseline |
| `LargeHotel GuestRoom5`, `GuestRoom6`, `GuestRoom7` | Hotel | NECB baseline × `hotel_multiplier(t, month, PR)` |
| `LargeHotel Banquet`, `Cafe`, `Kitchen`, `Lobby`, `Laundry`, `Storage`, `Corridor`, `Retail` | Hotel (support) | NECB baseline only (v1 — OD-6: revisit only if the Step-8 hotel EUI gate fails) |
| `Corridor`, `Storage`, `Elec/MechRoom`, `Elevator Shaft`, `Elevator Lobby`, `Plenum Space Type`, `Main Electrical`, `Main Mechanical`, `Elevator Machine Room` | Service / MEP | NECB baseline, **no modulation** |

> `HighriseApartment Office` (1 Space per prototype) is intentionally **Residential** — it serves the apartment block. `Resi_bot_Office ZN` zones stay BASELINE (Leg-2 documented decision).

## SLOT-ORIGIN DISCIPLINE (the +4h roll — 2J/Leg-2 lesson, encode once)

All GSS-derived 48-slot arrays are **04:00-origin** (slot 1 = 04:00). Every product conversion to clock time applies the diary→clock roll exactly as `3rdJ_07_aug_to_bem_2split.py:156-157/:307` does (`np.roll(..., +4h)`), for **residential, office AND the new retail product**. The **hotel s(t) table is already clock-indexed** (dr_L3-05 publishes it 00:00–23:30) — it gets **NO roll**; the builder asserts this by checking the overnight plateau lands at 22:00–06:00 in the emitted product. A mis-rolled channel shows up as a peak at an absurd clock hour — the 2J "00h peak" was exactly this class of bug (a validator clock-label offset); the R-section clock-window gates in the val doc are the tripwire.

## PORT BASES (fork from the FIXED Leg-2 files, not their archived predecessors)

| Leg-3 file | Fork base | Why this version |
|---|---|---|
| `3rdJ_07_aug_to_bem_4split.py` | `3rdJ_07_aug_to_bem_2split.py` **post-2026-07-18** (D2030 default hardened to `_C`; predecessor `.20260718_preD2030harden` is the WRONG base) | the non-`_C` default footgun is closed in this version |
| `commercial_integration.py` residential branch | `eSim_bem_utils_3J/integration.py` **post-multizone-fix** (md5 `6a92268be1f8dc3301df3bec80d6dd2e`; predecessor `integration.20260715_preMultizoneFix.py` is the WRONG base) | per-zone carrier replication for multi-zone residential (the tower apartment zones ARE multi-zone) |
| office branch | `office_integration.py` post-2026-07-02 (zone-field + People-field fixes in) | v24.2 field names |

## IMPLEMENTATION — `eSim_bem_utils/commercial_integration.py`

Extend `inject_office_schedules()` → **`inject_mixed_use(idf, channels, building_meta)`** (skeleton = spec §5): four Tag-2 sets + `modulate_baseline()` / `modulate_baseline_monthly()` dispatch. `modulate_baseline()` rewrites the referenced `Schedule:Compact`/`Schedule:File` as `new(t) = baseline(t) × multiplier(t)`, densities untouched. **Fall-back guarantee:** a channel with missing data reverts its Spaces to NECB baseline — the rest still produces valid output (spec §9).

- **v24.2 field names only**: zone references via `Zone_or_ZoneList_or_Space_or_SpaceList_Name` (the Leg-2 zone-field bug), People schedule via **`Number_of_People_Schedule_Name`** (the Leg-2 People-field bug).
- **Interpolate-to-Timestep = `No`** — inherited Leg-2 value (OD-8H), applied uniformly to retail + hotel schedules (**OD-8 of the pipeline: recorded here as required**).
- Hotel monthly mechanics: emit 12 monthly blocks in one annual `Schedule:Compact` (Through: fields) per guest-room Space — one IDF per scenario, not 12.

> **🔴 HARD WIRING GATE (Leg-2 lesson, 2026-07-02 — mandatory, at injection time, before any simulation is queued).** In Leg 2 the office injector wrote the presence multiplier to `Schedule_Name` instead of `Number_of_People_Schedule_Name` (`office_integration.py:254`); EnergyPlus accepted the IDF silently and **all 7 office scenarios simulated byte-identical**. `commercial_integration.py` therefore ships with a post-injection assertion, per Space: *every schedule the injector claims to have modulated is actually referenced by the correct IDF field* (People / Lights / ElectricEquipment named fields), **and** the modulated series differs from baseline wherever multiplier ≠ 1. Assertion failure = abort, no sbatch.

## HARD GATES (product-side, enforced by the builder before write)

| # | Gate | Target |
|---|---|---|
| H1 | Day_Type domain per product | exact sets above |
| H2 | Multiplier ranges | office fraction ∈ [0,1]; retail multiplier ∈ [0, 0.95], peak = 0.95 exactly per cycle × day-type; hotel multiplier ∈ (0, 1] |
| H3 | Staff-shoulder preservation | slots with baseline ≤ 0.10 carry `staff_shoulder_flag=1` and multiplier = baseline (unmodified) |
| H4 | Hotel monthly variation | 12 distinct monthly amplitudes per PR; s(t) plateau/trough exact (1.000 / 0.200 / 0.308) |
| H5 | Band monotonicity | office cons > hyb > fully (presence); retail 0.90 < 0.97 < 1.05 (mass ratios exact); hotel low < central < high |
| H6 | 2030 source | `_C` file only; hard-fail otherwise |
| H7 | Atomic write + `_BAK_<date>` backups | as Leg 2 |
| H8 | **Input-mutex hard gate (the Leg-2 mutex-bug lesson):** 0 slots with more than one of {hom30, wrk30, ret30} = 1 in the consumed diaries (2022 stock AND 2030 `_C`), asserted **before** any product is built | 0 conflicts — FAIL aborts the build. Leg-2's Step-7 validator had **no** mutex check, which is exactly how 4,280 impossible `hom30∧wrk30` cells (calibration-C weekend min-dwell re-raising hom30 over wrk30) sailed into a full simulation cascade and forced a 72-task re-sim |
| H9 | Clock-origin assertions: retail product peak lands in its clock window post-roll; hotel plateau at 22:00–06:00 (no roll applied) | per H8-style abort |

## CONNECTION TO DOWNSTREAM

Step 8 consumes the four products + `inject_mixed_use()`; Step 9 reads the Step-8 agg tables. The Leg-2 residential/office products remain valid — Leg-3 regenerates them from Leg-3 sources for provenance coherence, and MD5-compares the office product against Leg-2's as an insulation check (expected near-identical if upstream unchanged; any diff must be explainable by the Leg-3 pool delta).

## SCRIPT EXECUTION ORDER (planned)

```
py -3 -X utf8 3rdJ_07_aug_to_bem_4split.py --audit
py -3 -X utf8 3rdJ_07_aug_to_bem_4split.py --year 2022
py -3 -X utf8 3rdJ_07_aug_to_bem_4split.py --year 2030 --bundle {cons,central,opt} [--sens <channel>]
py -3 -X utf8 3rdJ_07_bemIntegration_4split_val.py
```

## Progress Log

*(append entries below — `| Date | Task | Result | Notes |`)*
