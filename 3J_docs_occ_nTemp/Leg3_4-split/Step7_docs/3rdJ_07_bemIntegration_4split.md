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

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-07-23 | Fork bases verified | PASS | `integration.py` MD5 `6a92268be1f8dc3301df3bec80d6dd2e` matches spec exactly (post-multizone-fix). `office_integration.py` (Step8_docs top level, 2026-07-02) confirmed live/non-archived. `3rdJ_07_aug_to_bem_2split.py` post-2026-07-18 confirmed (predecessor `.20260718_preD2030harden` present alongside for provenance). |
| 2026-07-23 | `--audit` | PASS | 2022 stock 29,502 rows/23,115 HH; 2030 `_C` 111,024 rows, BAND={conservative,fullyhybrid,hybrid}. **H6 PASS**: 2030 `_C` MD5 = `7c105ef331b37107d5b605c95028c3ba` (exact match to spec). **H8 PASS**: 0 mutex conflicts in both raw sources. Retail lever files + hotel inputs all present. FLAGGED: historical 2005/2010/2015 retail cycles NOT present locally — deferred to Step-8A-style generation (out of Step-7's execution order per runbook; Leg-2 precedent builds historical residential/office at Step 8A, not Step 7). FLAGGED: **no Tag-2-routable mixed-use prototype IDF exists anywhere in this repo** (checked `0_BEM_Setup/` — HPXML templates only; `BEM_Setup/Buildings/` — TallBuilding/SuperTallBuilding 90.1-2019 office + SF/Detached house only, v221; `2J_docs_occ_nTemp/BEM_setup/` — ApartmentHighRise/MidRise only). **W-section PENDING.** |
| 2026-07-23 | Built `3rdJ_07_aug_to_bem_4split.py` | DONE | Forked from Leg-2 2split builder; extended `complete_day_types`/`assemble_2030` to carry `ret30`; added `build_retail_product_2022/2030`, `build_hotel_product`, H1–H9 asserts, `_check_h5_monotonicity`. CLI: `--audit`, `--year 2022`, `--year 2030 --bundle {cons,central,opt} [--sens {office,retail,hotel}]`. |
| 2026-07-23 | `--year 2022` build | PASS | Products: `BEM_Schedules_4split_2022.csv` (1,109,520 rows / 23,115 HH), `office_presence_multiplier_2022.csv` (144 rows), `retail_presence_multiplier_2022.csv` (288 rows), `hotel_schedule_multiplier_2022.csv` (2,304 rows). All product-side gates (H1–H4, H7, H8, H9) PASS. |
| 2026-07-23 | `--year 2030 --bundle {cons,central,opt}` build | PASS | 3 aligned-bundle passes built residential+retail+hotel per bundle (cons→conservative/shift/low, central→hybrid/plateau/central, opt→fullyhybrid/renaissance/high) + refreshed the single all-bands `office_presence_multiplier_2030.csv` (432 rows) each pass. Row counts: residential 1,109,520/bundle; retail 288/bundle; hotel 2,304/bundle. **H5 monotonicity PASS all 3 channels**: residential WD 9-17h home-occ cons=0.4987<central=0.5373<opt=0.5616; retail lever cons=0.90<central=0.97<opt=1.05 exact; hotel mean monthly_rate cons=0.5688<central=0.6250<opt=0.6626. |
| 2026-07-23 | `--sens {office,retail,hotel}` off-diagonal builds | PASS (idempotency confirmed) | Ran all 3 `--sens` calls per the execution order. **F-section MD5 insulation CONFIRMED empirically**: `--sens office` regenerated `BEM_Schedules_4split_2030_{cons,opt}.csv` byte-identical to the aligned-bundle build (MD5 `0dcfbe40…`/`8112f64c…` unchanged) while retail/hotel files' mtimes were untouched; `--sens retail` regenerated `retail_presence_multiplier_2030_{cons,opt}.csv` byte-identical (MD5 `f47de539…`/`337ac1b5…`) with residential/office/hotel untouched; `--sens hotel` regenerated `hotel_schedule_multiplier_2030_{cons,opt}.csv` byte-identical (MD5 `d6e834ba…`/`e0ab6c86…`) with the other 3 channels untouched. **Zero cross-channel leakage — the 3 axes are genuinely independent by construction** (retail lever files and hotel forecast files have no BAND/office-axis column at all; residential/office depend only on the office BAND). |
| 2026-07-23 | **Realized scenario matrix** | 9 configs → full 3×3×3 resolution | 3 office-axis states (conservative/hybrid/fullyhybrid, shared by residential+office) + 3 retail-axis states (shift/plateau/renaissance) + 3 hotel-axis states (low/central/high) = 9 distinct channel-builds via exactly 3 `--bundle` CLI calls (axes are orthogonal, confirmed above) + 3 confirmatory `--sens` idempotency reruns. Step 8 composes any of the 27 combinations by picking the residential+office file for its office-axis value, the retail file for its retail-axis value, and the hotel file for its hotel-axis value — no 27-way rebuild needed. |
| 2026-07-23 | FLAGGED open item: NECB retail baseline proxy | DOCUMENTED, not fabricated | No hour-by-hour NECB Table A-8.4.3.2.(1)-A retail occupancy table exists anywhere in this repo (confirmed by repo-wide search via research subagent + direct grep). `staff_shoulder_flag` (H3/R5) computed against a documented PROXY reconstructed from the real `RetailStandalone BLDG_OCC_SCH_2010` `Schedule:Day:Interval` objects in `BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf` (ASHRAE 90.1-2019/DOE-PNNL retail-standalone prototype, raw peak 0.80), rescaled ×(0.95/0.80) to match the dr_L3-06 0.95-peak assumption. **Must be reconciled against whichever real mixed-use IDF Step 8 eventually selects** — this is exactly why W is PENDING, not a silent FAIL. |
| 2026-07-23 | FLAGGED open item: 2022 retail PR split | DOCUMENTED, not fabricated | Leg-3 Step-5 2022 stock's `PR` column is region-remapped 1–6 (Prairies=4 merges AB/MB/SK); raw province codes are not retained in any Step-5 output. 2022 retail product uses PR=2 (Quebec, exact) for "QC" and PR=4 (Prairies, AB+MB+SK) as a documented PROXY for "AB". The 2030 retail lever files do NOT have this problem — their source diary pool retains raw GSS province codes (confirmed PR_GROUP=QC/AB split directly, verified in the lever CSVs). |
| 2026-07-23 | FLAGGED open item: 2022 hotel AB Q4 gap | DOCUMENTED, carry-forward-filled | `0_Occupancy/processed/hotel_multiplier_lookup.csv` has AB 2022 rows for months 1–9 only (months 10–12 missing; QC 2022 is complete). Filled via carry-forward from September; 3 (PR,MONTH) cells flagged `rate_filled=1` in the 2022 hotel product. Surfaced honestly as a WARN in validator H.2/H.2b, not hidden. |
| 2026-07-23 | Built `eSim_bem_utils/commercial_integration.py` | DONE, untested against real IDF | `inject_mixed_use()` implemented: Tag-2 exact-match dispatch (8 channel classes per the routing table), `modulate_baseline()` (2-day-type office / 3-day-type retail), `modulate_baseline_monthly()` (hotel, 12 monthly blocks in 1 annual `Schedule:Compact`), v24.2 field names only (`Number_of_People_Schedule_Name` for People — the exact Leg-2 hard-wiring-gate lesson), fall-back guarantee (W5) per missing channel, `assert_wiring()` (W2) ready. Pure-Python logic (Tag-2 dispatch, CSV loaders, Schedule:Compact field builders) smoke-tested successfully against the actual Step-7 products (office/retail/hotel series load and build correct field counts: office 24+24, retail 48×3, hotel 12×48×2). **Cannot be dry-run tested against a real IDF** — none exists in this repo (see `--audit` finding above). |
| 2026-07-23 | Built `3rdJ_07_bemIntegration_4split_val.py` | DONE | Sections A–G (ported/extended) + R (8 gates) + H (6 gates) + M (4 gates) + W (6 gates, PENDING) + F (insulation + WFH direction) + G. Ran `--all` (2022 + 3×2030 bundles) → 4 HTML reports in `outputs_step7/`. One validator strictness bug found and fixed during this run: M2/R3 "±1 slot" tolerance (val doc spec) was implemented as a stricter hour-only window, producing 2 false-positive FAILs on the 2030 scenarios; widened to the correct tolerance (11–15h WD / 12–17h Sat) and re-ran — those 2 FAILs cleared legitimately (not gate-relaxed; the fix made the implementation match the already-written spec, verified against the actual val.md wording). |
| 2026-07-23 | **Full validator scorecard** | 2022: 42P/10W/1F · 2030_cons: 52P/7W/1F · 2030_central: 52P/7W/1F · 2030_opt: 52P/7W/1F | See `_val.md` Progress Log for the gate-by-gate table and the 2 FAIL dispositions (retained, not relaxed). |
| 2026-07-23 | Office product MD5 vs Leg-2 (insulation check) | INFO, expected DIFFERENT | `office_presence_multiplier_2022.csv`: Leg-2 MD5 `1af6e0cf…` vs Leg-3 MD5 `ff0fc987…` — differ, as expected: Leg-3's Step-5 pool is 23,115 HH vs Leg-2's 23,150 HH (a different frame, not a bug). No unexplained divergence found. |
| 2026-07-23 | **Step 7 status** | NOT FULLY CLOSED — 2 documented FAILs open, W-section PENDING | Per non-closure discipline: "Step 7 NOT done until 0 FAIL (or documented WARN/INFO)." The 2 remaining FAILs (M2 2022 retail late-peak; E.3 Office_Sales band non-monotonicity) are investigated, evidence-backed, and NOT gate-relaxed — see `_val.md` Progress Log for full disposition. W-section is PENDING (not FAIL) pending a mixed-use prototype IDF that does not yet exist in this repo — this blocks Step 8 per the hard wiring gate until resolved. Returned to manager for a go/no-go decision on these 2 open items before Step 8. |
| 2026-07-23 | **MANAGER REVIEW — Step-7 PRODUCT phase ACCEPTED (products + injector + validator complete); W-section DEFERRED to Step-8 IDF setup** | ACCEPTED w/ 2 documented FAILs; W deferred (user-gated) | Manager (Opus) independently re-verified employee claims from the artifacts, not the log. **(1) M.2 FAIL confirmed genuine, accept-as-documented**: `retail_presence_multiplier_2022.csv` QC weekday `at_retail_fraction` peaks at slot 34 / Hour 16 (0.0357) — a real after-work-shopping curve. Roll is CORRECT, not a +4h mis-roll: QC Saturday & Sunday peak at Hour 13 (midday), exactly where retail should peak; a +4h mis-roll would displace the Sat peak to 17h. Gate-window-too-narrow candidate, no re-run. **(2) E.3 FAIL confirmed genuine, accept-as-documented**: `office_presence_multiplier_2030.csv` Office_Sales weekday peak cons=0.5100 < hybrid=0.5174 (violation +0.0074) > fullyhybrid=0.3930 on n=201; Knowledge & Public cleanly monotone. Small-cell noise on the smallest archetype (same class Leg-2 documented). **(3) F-section separability CONFIRMED — structural + empirical**: retail lever files & hotel forecast files carry NO office-BAND column; residential/office depend only on office BAND → 3 axes orthogonal by construction. Manager verified file structures directly (office product carries BAND col; retail/hotel are per-lever/per-band). MD5 pairs logged above corroborate. **9 configs → 27 analytic cells VALID.** Neither FAIL contaminates the deliverable; no re-run needed (Step-5/Step-6 disposition precedent). **Product phase = usable by Step 8.** The ONE genuine blocker is **W-section wiring** (no Tag-2-routable prototype IDF exists) — reclassified as a **Step-8 IDF-setup task + user-gated design decision** (per-archetype UBEM composition [recommended, matches the proven separability design] vs single mixed-use building), NOT a Step-7 product defect. Step 8 NOT launched (user go pending). See [[project_3j_leg3_step7_status]]. |
