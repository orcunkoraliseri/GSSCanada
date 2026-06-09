# Step 9 — Activity-Driven Equipment & Lighting Schedules (light version)
### Using the predicted hourly *activities* to shape plug-load & lighting demand, anchored to NRCan SHEU 2019

> ⚠️ **UNDER REVISION — 4-hour schedule-injection bug found 2026-06-08.** `07_aug_to_bem.py` wrote the 4 AM-origin GSS diary slots straight to EnergyPlus `Hour` (slot @ 04:00 → Hour 0) instead of rotating to real clock (slot @ 04:00 → Hour 4). All occupancy / metabolic / equipment / lighting schedules were injected **4 h early** vs the weather. **The headline −4 h equipment peak-shift reported below is an artifact of this bug, not behaviour**, and the "sleep-hour" WARN is really morning activity. Bug fixed; **full cluster re-simulation in progress (initiated 2026-06-08)** — every timing / peak-hour result here is pending corrected re-runs. The SHEU annual calibration (48/48) is phase-invariant and stands. SI fixes from the investigation: **R1** (lighting = binary occupied-&-awake, no daylight gate) + **R4** (gross 3700 / net 3252) valid; **R2/R3** (offset-is-benign) rejected. Details: `Step9_docs/investigation/step9_investigation.md`.

> **Status: APPROVED — supplementary analysis (SI/Appendix) in this 2nd-journal paper.** Decision by
> user 2026-06-02. Both deep-research inputs are now **RESOLVED** (see *Resolved Inputs*; numbers folded
> into §9.2–§9.5), and the 1-cell prototype **PASSED** (`Step9_docs/prototype/PROTOTYPE_VERDICT.md`: equipment &
> lighting calibrated to <0.5% of SHEU; +35.4% sharper 2022→2030 peak differential vs presence-only).
> **This doc is the source of truth for the build. Implementation is deferred** — docs-only for now;
> the build runs after Step 8, reusing its sampled households (see *Build Plan*).

---

## EXECUTION CHECKLIST (live — update on each completion)

- [x] **Spike returns** — GO 2026-06-03. `nrel/energyplus:24.2.0` SIF on Speed; E+ 24.2.0-94a887817b; all 9 end-use meters <0.006% diff vs local (max 0.0055%). See `Step9_docs/cluster_container_spike.md`.
- [x] **Code build returns** — 4 red flags fixed (RF1+RF2 in code; RF3/RF4 structural); wiring in; Step 8 outputs byte-identical. Static validation ALL PASS (2026-06-03).
- [x] **Step 9 cluster run prompt** — run both halves (baseline + activity) on the 3-cell/n=20 sample on Speed for a clean paired Δ. COMPLETE 2026-06-05. Root causes fixed: (1) 17-col activity CSV (Equip_Design_W) never uploaded — resolved by running 07_aug_to_bem.py; (2) fridge schedule changed to Schedule:Compact (always 1.0) for E+24.2 compatibility + precheck parseability; (3) validate column bug fixed (activity uses InteriorEquipment/InteriorLights, not zone-level which extracts as 0 after S9 neutralization). Precheck PASS all 3 cells. Array 950562: 239/240 (1 warmup-convergence fail, MidRise/HH1865/2030). Validate job 950833: ALL 6 GATES PASS.
- [x] **Validate** — SHEU ±15% gate: 6/6 PASS. HighRise −0.1%/−0.1%, MidRise +0.3%/−5.6%, SingleD +0.0%/+0.0%. Sleep check: PASS (HighRise, MidRise 2030, SingleD — WARN on MidRise 2022 and SingleD which retain small baseload). Results in `/speed-scratch/o_iseri/step9_run/cluster_run_results.csv`. COMPLETE 2026-06-05.
- [x] **Step 8 finishes** → **S9-A scripts built 2026-06-05** (24-cell/n=50 full-grid scripts ready; upload to cluster + sbatch to launch).
- [x] **Plots** — DONE. figS1–S5 (`Step9_docs/figures/`) + figS6–S8 (normalized, `outputs_step9/`) + figV1 default-vs-Step9 (`outputs_step9/`). All 9 SI figures present on disk.
- [x] **Write-up** for the supplementary (SI/Appendix) section — DONE 2026-06-08. `Step9_docs/si_appendix_step9.md` rewritten submission-ready: full Method (§S4: two-tier split, shipped activity→end-use weight matrix, EFF co-presence, SHEU calibration + apartment-split derivation, lighting, neutralize-and-inject + multi-unit fridge correction), validation grid + gates (§S4.8), diurnal load shape + per-cell peak-shift tables (§S5), limitations (§S6), references. Numbers reconciled to the programmatic validator (equip max \|dev\| 2.5%, light 2.3%, sleep WARN 28/48, light shift −2..−5h).

---

## GOAL

Steps 4–7 predict, for every household, a **30-min time-series of activities** (`act30`, 14
categories), **presence** (`hom30`), and **co-presence**. Today only *presence* and *activity-as-
metabolic-heat* reach the BEM. Step 9 uses the **activities themselves** to shape the **lighting**
and **equipment (plug-load)** demand, so the daily electricity curve reflects *what people are
doing*, not just *whether they're home* — then keeps the yearly totals honest by anchoring to the
NRCan **Survey of Household Energy Use (SHEU) 2019**.

**Why this sharpens the paper's novelty.** Step 8's contribution is "predicted occupancy
time-series → load shape & peak timing." Step 9 deepens it to "predicted **activity** time-series →
**end-use-resolved** load shape" (cooking, laundry, entertainment, home-office), which is a stronger,
more behaviourally grounded claim about *when* and *which* loads move 2022→2030.

---

## THE GAP (what the engine does now)

`integration.py` (the Step-8 engine) currently sets internal loads like this:
- **People / metabolic:** driven by occupancy + activity (the `Metabolic_Rate` we already compute).
- **Lighting:** *Daylight-Threshold (gatekeeper)* — on when present + dark, off in daylight.
- **Equipment / DHW:** *Presence Filter* — a coarse **min/max toggle** by presence only.

So equipment is essentially "someone home → plug load high; empty → low." The rich **activity**
signal (cooking vs sleeping vs watching TV) is **not** used for plug loads or lighting. Step 9 fills
that gap.

---

## WHAT WE ADAPT FROM THE LITERATURE (and what we skip)

This is **not** a new method — it's a *simplified adaptation* of established activity-based
bottom-up load modelling. Full reports + citations in `Step9_docs/deepResearch/`.

**We adopt (and cite):**
- **Activity → appliance crosswalk** and the **two-tier (baseload vs activity-driven) split** —
  Richardson, Thomson, Infield & Clifford (2010); McKenna & Thomson (2016, CREST).
- **Calibrate to national annual totals with a per-end-use scalar** — Richardson (2010);
  Armstrong et al. (2009, NRC); the **2023 Canadian** stochastic generator (*Building & Environment*).
- **Non-linear co-presence** (shared vs personal devices) — Richardson (2008/2010); Widén & Wäckelgård (2010).
- **Anchor values** — NRCan **SHEU 2019** + the Comprehensive Energy Use Database; Hydro-Québec splits.

**We skip (this is the "light" part, and it's in our favour):**
- The papers **generate** activities stochastically (Markov chains) and **roll dice** for each
  appliance switch-on. **We already predict the activities** (J3 model, calibrated, forecast to 2030),
  so we use them **directly as a deterministic shape** — no Markov chain, no switch-on probabilities.
- Citable framing: *"We adapt the Richardson/CREST activity-to-load mapping and NRCan calibration,
  driven by our predicted activity time-series in place of a synthetically generated one."*

---

## INPUTS

| Input | Source | Role |
|---|---|---|
| `act30` (14 categories, 30-min) | Step 4 aug / Step 7 | the activity shape (what drives the bend) |
| `hom30` presence + co-presence | Step 4 aug / Step 7 | active-occupancy + shared/personal scaling |
| `BEM_Schedules_{year}.csv` | Step 7 | per-HH hourly frame we extend |
| Archetype IDF default Lights/Equipment | `Buildings_MTL_v242/` | the schedules we bend (don't rebuild) |
| SHEU 2019 end-use & appliance kWh (region × dwelling) | NRCan | the annual anchor — **RESOLVED (DR-1)**, see §9.4 |
| Activity→appliance weights + co-presence form | CREST / 2023 CA generator | the bend magnitudes — **RESOLVED (DR-2)**, see §9.2–9.3 |

The 14 activity labels (from `02_harmonizeGSS.py` `ACT_LABELS`): 1 Work · 2 Household work &
maintenance · 3 Caregiving · 4 Purchasing · 5 Sleep · 6 Eating & drinking · 7 Personal care ·
8 Education · 9 Socializing · 10 Passive leisure · 11 Active leisure · 12 Community/volunteer ·
13 Travel · 14 Misc. (0 = away/missing.)

---

## METHOD — light version (easy walk-through)

**Core idea:** split each home's electricity into a flat *always-on* part and a *behaviour* part;
shape the behaviour part with the activity diary; then scale the year to match SHEU.

### 9.1 — Two buckets (the two-tier split)
- **Always-on baseload** (fridge, freezer, internet/networking, standby): a **flat** schedule, 24/7,
  **never** modulated by activity. (It is ~half the appliance load — must not be zeroed when the home
  is empty/asleep.) Sized to the SHEU fridge/freezer/standby anchors.
- **Activity-driven** (cooking, laundry, dishwasher, TV/entertainment, computer/home-office,
  personal care): this is the part we bend.

### 9.2 — Activity → end-use crosswalk (the bend rule)
For each 30-min slot, each member's activity adds weight to the relevant end use:

| Activity | Drives (activity-driven end use) | Presence | Scaling |
|---|---|---|---|
| 1 Work | Computer / home-office, task light | home if telework, else away | per-person |
| 2 Household work & maint. | Laundry (washer/dryer), dishwasher, vacuum, cooking prep | home | sub-linear |
| 3 Caregiving | Lighting + minor plugs (+ incidental laundry/cooking) | home | sub-linear |
| 4 Purchasing | — (baseload only) | **away** | — |
| 5 Sleep | — (baseload only) | home, inactive | — |
| 6 Eating & drinking | Cooking (range/oven/microwave/kettle), dishwasher | home | sub-linear |
| 7 Personal care | Hot water (DHW), hair dryer, bathroom light | home | per-person |
| 8 Education | Computer / laptop, task light | home if studying-at-home | per-person |
| 9 Socializing | TV / entertainment, lighting | home | shared |
| 10 Passive leisure | TV / entertainment, computer | home | shared |
| 11 Active leisure | minor / none (indoor) or away (outdoor) | mixed | low |
| 12 Community/volunteer | — (baseload only) | **away** | — |
| 13 Travel | — (baseload only) | **away** | — |
| 14 Misc | small plugs + lighting | home (assume) | low |

**Weights RESOLVED (DR-2 — `Step9_docs/deepResearch/Activity-Based Load Modeling Numbers.md`).** The deterministic
activity→end-use weight matrix (the *expected* load intensity each activity drives — no Markov, no dice):

| Code | Activity | Cook | Dishw | Washer | Dryer | TV/Ent | PC/Office | Care+DHW | Light |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Work (home) | 0.05 | 0 | 0 | 0 | 0 | 0.90 | 0.05 | 1.0 |
| 2 | Household work | 0.10 | 0.20 | 0.30 | 0.20 | 0 | 0 | 0.20 | 1.0 |
| 3 | Caregiving | 0.10 | 0 | 0 | 0 | 0.30 | 0 | 0.10 | 1.0 |
| 4 | Purchasing (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | Sleep | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | Eating & drinking | 0.85 | 0.15 | 0 | 0 | 0 | 0 | 0 | 1.0 |
| 7 | Personal care | 0 | 0 | 0 | 0 | 0 | 0 | 0.90 | 1.0 |
| 8 | Education (home) | 0.05 | 0 | 0 | 0 | 0 | 0.85 | 0 | 1.0 |
| 9 | Socializing | 0.15 | 0 | 0 | 0 | 0.40 | 0 | 0 | 1.0 |
| 10 | Passive leisure | 0 | 0 | 0 | 0 | 0.85 | 0.15 | 0 | 1.0 |
| 11 | Active leisure | 0 | 0 | 0 | 0 | 0.20 | 0 | 0.20 | 1.0 |
| 12 | Community (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 13 | Travel (away) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 14 | Misc (home) | 0 | 0 | 0.10 | 0 | 0.10 | 0.10 | 0 | 1.0 |

Lighting weight = 1.0 for every active home state, then modulated by the daylight override (§9.5).
**Within-activity sub-splits** (fracture a broad GSS code into appliances): Code 2 → washer 0.35 / dryer
0.25 / dishwasher 0.20 / cleaning 0.20; Code 6 → range 0.45 / microwave 0.35 / small-appliance 0.20
(06–10h → small 0.50 / micro 0.40; 16–20h → range 0.70); Code 10 → TV 0.65 / PC 0.20 / laptop 0.15.
**Appliance active power (W), DR-2:** range 3000 / microwave 1500 / kettle 1200 / dishwasher 930 /
washer 470 / dryer 2100 / TV 100 / desktop 150 / laptop 45; sub-30-min loads prorated `P_rated × (D/30)`,
dishwasher cycles >30 min queue forward. *(The prototype `Step9_docs/prototype/activity_loads.py` used a simplified aggregated
subset — e.g. one ~930 W "cooking" bucket — which the per-end-use SHEU scalar re-levels regardless.)*

### 9.3 — Co-presence scaling
- **Shared devices** (TV, room lighting, cooking, dishwasher): active if **≥1** member does the
  activity; **does not multiply** with more people (sub-linear / "first occupant").
- **Personal devices** (laptop, hair dryer, personal hot-water): scale **≈ linearly** with the
  number of members doing it. We have co-presence, so we apply this directly.

**Effective-occupancy (EFF) RESOLVED (DR-2):** shared devices use a sub-linear factor of the number of
members doing the activity — **EFF(N) = 1.0 / 1.4 / 1.7 / 1.9 / 2.0** for N = 1 / 2 / 3 / 4 / ≥5;
personal devices scale **linearly (= N)**. Shared set = {cooking, dishwasher, washer, dryer, TV};
personal = {PC, hair-dryer, personal DHW}. (Prototype `Step9_docs/prototype/activity_loads.py` implements exactly this.)

### 9.4 — Anchor to SHEU (the one calibration scalar)
For each end use *e*: build its raw activity-shaped annual profile, then compute one correction
scalar `f_e = SHEU_target_e(region, dwelling) / simulated_annual_e`, and apply it so the **shape
comes from behaviour and the yearly total comes from SHEU**. Baseload is held fixed; the
activity-driven categories absorb the remaining target. (Exactly Richardson's per-appliance scalar.)

**Anchors RESOLVED (DR-1 — `Step9_docs/deepResearch/Calibration Dataset … (per household).md`).**
*Hard [Published] targets — total household electricity intensity (kWh/hh·yr), calibrate to within ±10%:*
Quebec 17,750 · Atlantic 13,333 · Prairies (MB/SK) 11,083 · BC 8,861 · Ontario 8,278 · Alberta 6,722
(Canada 11,055). *By dwelling [Published total]:* single detached 12,694 (lighting 1,262, appliances
≈3,700) · attached ≈10,750 · low-rise apt 7,417 · high-rise apt 6,583.
*Baseload held flat ≈1,000–1,200 kWh/hh·yr:* fridge 448 kWh/51 W · freezer 343/39 W · standby ≈400–430/
45–49 W. *Appliance UEC [Published, CEUD T16]:* fridge 448 · freezer 343 · dishwasher 73 · washer 35 ·
dryer 790 · range 546 · other electronics ≈1,400.
**Derived vs published (important):** SHEU publishes only the *totals*; per-end-use splits are
**derived** (model-grade). For all-electric **Quebec** homes use the Hydro-Québec split directly —
54% heat+AC / 20% DHW / 18% appliances+electronics / 5% lighting / 3% other — and disaggregate with
province-specific heating-fuel logic, not one national split.

### 9.5 — Lighting
`lighting(t) = active_occupancy(t) × daylight_gate(t)`, scaled to the SHEU lighting total. The engine
already does the daylight gate — we add the active-occupancy shape and the SHEU scale, and reconcile
with EnergyPlus `Daylighting:Controls` to avoid double-counting.

SHEU lighting anchors (kWh/hh·yr, DR-1): national 1,053 · single detached 1,262 · apartment 736 (falling
with LED adoption). The prototype confirmed the IDF's daylight-only default badly under-counts (≈151 kWh
for Montreal SingleD vs the 1,262 SHEU anchor) — so the SHEU scale is essential, not optional.

### 9.6 — Inject into EnergyPlus
The bent **Lights** and **ElectricEquipment** schedules go in exactly where Step 8 already injects
occupancy + metabolic. (Optional later: route personal-care / dishwashing / laundry to
`WaterUse:Equipment` for activity-driven DHW.)

---

## INTEGRATION POINT

- **Step-7 converter (`07_aug_to_bem.py`)**: extend to also emit, per HH × hour × day-type, an
  `Equipment_Fraction` and `Lighting_Fraction` (activity-driven, two-tier, normalized) alongside the
  existing `Occupancy_Schedule` + `Metabolic_Rate`.
- **Step-8 engine (`eSim_bem_utils_2J/integration.py`)**: consume those fractions for the `Lights` /
  `ElectricEquipment` objects instead of the current daylight/presence-toggle defaults.
- **Calibration** (`f_e`) applied per region × dwelling at converter time. No change to the
  do-not-modify ML files.

---

## HARD GATES

| Gate | Threshold |
|---|---|
| Annual end-use total vs SHEU | each activity-driven end use within **±10%** of its SHEU anchor |
| Baseload integrity | fridge/freezer/standby **never** zeroed (flat 24/7) |
| No double-count | `Electricity:Facility` not summed with its own components; metabolic ≠ equipment |
| Load-shape sanity | diurnal curve has plausible morning/evening structure; cooking peaks at meal times |
| Lighting–daylight | no double-count with `Daylighting:Controls` |

---

## RISKS / CAVEATS (all manageable, document in Methods)

- **30-min resolution flattens appliance peaks** (a 3-min microwave spike → a low sustained load).
  Fine for our **load-shape** focus; **not** valid for instantaneous appliance peak-kW. State it.
- **Seasonality:** time-use under-captures "people stay in more in winter." Heating dominates and we
  have multiple cycles, so likely minor; optional seasonal factor (Fischer) if validation demands it.
- **Crosswalk assumptions:** activity→appliance mapping is judgement-based; the SHEU scalar bounds the
  error in *total*, but the *split between* end uses carries assumption risk — document the crosswalk.
- **Derived anchors:** the Quebec per-appliance numbers in the research are *derived* (province total
  × Hydro-Québec %), not directly published — verify against the SHEU tables (DR-1).
- **Co-presence cooking/TV** must be sub-linear or the model over-predicts multi-person homes.

---

## RESOLVED INPUTS (both deep-research gaps closed)

Both inputs that were open at design time are now answered; full reports in `Step9_docs/deepResearch/`,
the prompts that produced them in `Step9_docs/prompts/`:
1. **DR-1 — SHEU regional/dwelling anchors** → `Step9_docs/deepResearch/Calibration Dataset Canadian Residential
   Electricity End-Use, Appliance & Baseload Consumption (per household).md` (prompt:
   `Step9_docs/prompts/DR_prompt_SHEU_regional_anchors.md`). Numbers folded into **§9.4**.
2. **DR-2 — Activity→appliance weights + co-presence + seasonality + validation** →
   `Step9_docs/deepResearch/Activity-Based Load Modeling Numbers.md` (+ `.pdf`; prompt:
   `Step9_docs/prompts/DR_prompt_activity_appliance_mapping.md`). Numbers folded into **§9.2–§9.3**.
   - **Seasonality decision:** apply a small cosine factor on **cooking + DHW only**,
     `W_base × (1 + 0.15·cos(2π(d−15)/365))` (peak mid-January); leave other end uses unscaled
     (heating dominates the seasonal swing and is handled by the thermal model).
   - **Validation datasets:** Saldanha & Beausoleil-Morrison (2012, 12 Canadian houses, 1-min) and
     Johnson & Beausoleil-Morrison (2017, 23 houses) — for load-**shape** (not appliance-peak) validation.

**Scope decision (user, 2026-06-02): GO** — fold light Step 9 into *this* paper as supplementary analysis.

---

## BUILD PLAN (light Step 9) — implementation, deferred until after Step 8

**Aim.** Activity-driven equipment + lighting across the **6 climate-zone cities × 4 archetypes** grid,
**2022 + 2030**, **paired against the presence-only Step-8 baseline on the SAME sampled households**,
SHEU-calibrated — yielding the supplementary, end-use-resolved load-shape results.

**Steps.**
1. **Fix the 4 prototype red flags FIRST** (`Step9_docs/prototype/PROTOTYPE_VERDICT.md`):
   (a) **dishwasher-queue de-bounce** — per-trigger cooldown so consecutive eating slots don't re-fire
   the 3-slot queue (the suspected cause of the h7 morning-peak artifact);
   (b) **fridge/baseload double-zero** — keep the IDF `refrigerator1` and subtract its kWh from the
   STEP9 baseload target (don't zero it *and* add a flat ~130 W);
   (c) **kWh-comparable baseline** — calibrate the presence-only baseline to the same annual total so
   shape *and* total are comparable;
   (d) **N ≥ 20** per cell (prototype n=5 gave high peak-hour variance, esp. lighting).
2. **Promote** `Step9_docs/prototype/activity_loads.py` into the Step-7 converter `07_aug_to_bem.py`: emit, per
   HH × hour × day-type, an `Equipment_Fraction` + `Lighting_Fraction` (two-tier, normalized) alongside
   the existing occupancy + metabolic outputs.
3. **Modify** `eSim_bem_utils_2J/integration.py` to consume those fractions for `Lights` /
   `ElectricEquipment` instead of the daylight/presence-toggle defaults. (Versioned engine copy only;
   conference `eSim_bem_utils/` untouched; no change to the do-not-modify ML files.)
4. **Run** on Step-8's exact sampled households (same per-cell SHA-256 seed) so the activity-vs-presence
   comparison is a clean within-HH paired Δ — reuse the Step-8 frame, do not re-sample.
5. **Aggregate + plot:** activity-vs-presence diurnal, equipment/lighting peak-hour shift, and the
   2022→2030 differential resolved by end use.

**Expected result.** Per region × dwelling, annual equipment & lighting within **±10%** of the SHEU
anchor (prototype hit <0.5%); physically-sane diurnal (zero during sleep/away); the 2022→2030
differential **sharper than presence-only** (the novelty) — **with the h7 morning-peak artifact resolved
or explained** after the dishwasher de-bounce.

**Test method.** ±10% calibration gate vs SHEU; paired same-HH comparison vs the Step-8 presence-only
baseline; sleep/away zero-check; regression against the prototype cell (SingleD × Montreal_6A) to confirm
the refactor doesn't change behaviour; load-shape cross-check vs the Canadian measured-load datasets
(Saldanha & Beausoleil-Morrison) from DR-2.

**Sequencing.** Runs **after** Step 8 (avoids RAM/compute contention on the same box, and lets Step 9
reuse Step 8's frozen household sample). Documentation now; code on the user's go.

---

## REFERENCES (full list in `Step9_docs/deepResearch/`)

- Richardson, Thomson, Infield & Clifford (2010), *Domestic electricity use: a high-resolution energy
  demand model*, Energy & Buildings 42(10). DOI:10.1016/j.enbuild.2010.05.023.
- Richardson, Thomson, Infield & Delahunty (2009), *Domestic lighting…*, Energy & Buildings 41(7).
- Widén & Wäckelgård (2010), *A high-resolution stochastic model…*, Applied Energy 87(6).
- McKenna & Thomson (2016), *High-resolution stochastic integrated thermal–electrical… (CREST)*, Applied Energy 165.
- Armstrong, Swinton, Ribberink, Beausoleil-Morrison & Millette (2009), *Synthetically derived profiles…
  Canadian housing*, J. Building Performance Simulation 2(1).
- *Stochastic bottom-up load profile generator for Canadian households' electricity demand* (2023),
  Building & Environment. DOI:10.1016/j.buildenv.2023.110466. *(verify author list)*

---

## Progress Log

### 2026-06-03 — Step 9 Code Build (local, no E+)

**Status: COMPLETE (static validation). Deferred items listed below.**

**Files changed**

| File | Action | Archive |
|------|--------|---------|
| `2J_docs_occ_nTemp/activity_loads.py` | NEW (production module, RF1+RF2 fixed) | — |
| `2J_docs_occ_nTemp/07_aug_to_bem.py` | EXTENDED (+4 Step-9 columns, `_compute_hh_activity_fracs`) | `archive/07_aug_to_bem.20260603.py` |
| `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py` | EXTENDED (Step-9 branch in `load_schedules` + `inject_schedules`) | `archive/integration.20260603.py` |
| `2J_docs_occ_nTemp/step9_static_validation.py` | NEW (validation script, no E+) | — |

**RF1 — Dishwasher de-bounce (FIXED)**
Added `dw_cooldown` counter to `activity_loads.compute_48slot_loads()`. Trigger is now gated
by `dw_queue == 0 and dw_cooldown == 0`. After the 3-slot run completes, `dw_cooldown = 6`
(3-hour gap) prevents re-trigger. Regression check on an all-eating (act=6, 48 slots) 1-person
household: 18 active dishwasher slots (6 cycles × 3 slots, cycle period = 9 slots = 4.5h).
Prototype behavior was 48 slots (every slot). STATIC CHECK: PASS.

**RF2 — Fridge/baseload double-zero (FIXED)**
Added `FRIDGE_KWH_IDF = 448.0` (SHEU 2019 single-detached fridge UEC, DR-1 Table C) and
`SHEU_EQUIP_KWH_NET = 3700 - 448 = 3252 kWh`. `calibrate_schedules()` now targets the net
3252 kWh so the IDF's always-on `refrigerator1` and the STEP9 `BASELOAD_W` (130 W) do not
double-count fridge electricity. Arithmetic verified: `SHEU_EQUIP_KWH_NET = 3252.0`. STATIC CHECK: PASS.

**RF3 — N ≥ 20 (STRUCTURAL — no code change required)**
`_compute_hh_activity_fracs()` loops over the full aug CSV groupby (all 144,507 HHs), so any
sample size is supported. The n=5 prototype instability was purely a sample-size limitation;
n ≥ 20 will be enforced at the cluster run step.

**RF4 — kWh-comparable baseline (STRUCTURAL — deferred to cluster run)**
The code is wired correctly (STEP9 fracs + SHEU-calibrated DesignLevel). Making the
presence-only baseline kWh-comparable requires zeroing `gas_mels1` and `IECC_Adj1` in the
baseline IDF — that is an E+ run-time operation, deferred to the cluster Step 9 script.

**Pipeline wiring**

`07_aug_to_bem.py` now emits four new columns per HH × day-type × hour:
- `Equipment_Fraction` (0–1, normalized to peak, SHEU_NET-calibrated)
- `Lighting_Fraction` (0–1, raw occupancy-gated fraction)
- `Equip_Design_W` (W, per-HH DesignLevel for ElectricEquipment IDF object)
- `Light_Design_W` (W, per-HH Lighting_Level for Lights IDF object)

All 13 original columns unchanged; existing `Occupancy_Schedule` and `Metabolic_Rate`
logic is byte-identical. Constants-diff (MET, PR_LBL, DAYTYPE) confirmed identical to archived predecessor.

`eSim_bem_utils_2J/integration.py` changes (additive, backward-compatible):
- `load_schedules()`: parses `Equipment_Fraction`, `Lighting_Fraction` into each hour entry;
  reads `Equip_Design_W`, `Light_Design_W` into `metadata`. Old CSVs without these columns
  fall back to 0.0 (Step 9 path stays inactive for Step 8 runs).
- `inject_schedules()`: extracts `_s9_equip_data`, `_s9_light_data` at entry. For `LIGHTS`:
  if `light_design_w > 0`, uses activity fracs (same fraction all months) + updates
  `Lighting_Level`. For `ELECTRICEQUIPMENT`: if `equip_design_w > 0`, uses activity fracs +
  updates `Design_Level`. `GASEQUIPMENT` and `WATERUSE:EQUIPMENT` are unchanged (presence-filter path).
  When new columns absent (old CSV), all three objects use the pre-existing logic unchanged.

**Static validation results** (`step9_static_validation.py`)

| Check | Result |
|-------|--------|
| RF1 de-bounce: 18 DW slots on all-eating day (was 48) | PASS |
| RF2 arithmetic: SHEU_NET = 3700 − 448 = 3252 kWh | PASS |
| Calibration scalar: equip_scale = NET/raw (verified exact) | PASS |
| Sleep/Away: light_frac = 0, equip_W = BASELOAD_W = 130 W | PASS |
| Output schema: required keys, 24h arrays, fracs ∈ [0,1] | PASS |
| `07_aug_to_bem.py` import + OUT_COLS (17 cols, 4 new) | PASS |

**Deferred to cluster run**

- Paired E+ kWh comparison (activity vs presence-only baseline)
- ±15% SHEU calibration gate at E+ output level
- 2022→2030 differential on n ≥ 20 per cell
- `gas_mels1`/`IECC_Adj1` zeroing on baseline IDFs for apples-to-apples kWh comparison
- `Lighting_Level` / `Design_Level` update verified in IDF output (best-effort in inject_schedules; confirmed once E+ run completes)
- Per-region × per-dwelling SHEU calibration targets (all HHs use SingleD 3252/1262 kWh for now)
- NRCan, **SHEU 2019** + Comprehensive Energy Use Database; Hydro-Québec end-use breakdown.
- Validation: Saldanha & Beausoleil-Morrison (2012), Energy & Buildings 49; Johnson & Beausoleil-Morrison (2017).

---

## Progress Log

| Date | Item | Result | Notes |
|---|---|---|---|
| 2026-06-02 | Step 9 light-version design drafted | ✅ DESIGN | Activity-driven equipment + lighting via two-tier split (flat baseload + activity-bent), co-presence scaling, single SHEU calibration scalar per region×dwelling; injected where Step 8 already injects occupancy/metabolic. Adapts Richardson/CREST + Armstrong/2023-CA + SHEU 2019; **skips the stochastic Markov/switch-on machinery because activities are already predicted.** Status = candidate; 2 open inputs sent to deep research (DR-1 SHEU anchors, DR-2 activity weights + co-presence). Scope decision (this paper vs future work) pending. |

| 2026-06-02 | Step 9 prototype — 1-cell run | ✅ COMPLETE | Cell: SingleD × Montreal_6A. HH IDs: 37870 (n=4), 111596 (n=3), 77720 (n=2), 36140 (n=1), 90994 (n=2). n=5, seed=42. 2022+2030. All 20 E+ runs Completed Successfully. STEP 0 HARD CHECK PASSED (act codes 1–14, no code 0, sleep fraction at 02:00 = 68.7%). Calibration: equipment 3693–3705 kWh/yr (+/-0.3%), lighting 1257–1263 kWh/yr (+/-0.4%) — both well within +/-15% gates. Equipment peak: activity h7 (7am) vs baseline h18 (6pm) — 11-hour shift; 2022->2030 +35.4% in activity vs +0.4% in baseline. Lighting: activity model 8.3x higher annual energy (SHEU-anchored 1262 kWh vs baseline 151 kWh from daylight-gated IDF default). Caveats: dishwasher-queue de-bounce needed; n=5 lighting peak hour high-variance; baseline not kWh-comparable. RECOMMENDATION: fold into paper as supplementary analysis (Appendix/SI). Files: Step9_docs/prototype/activity_loads.py, run_prototype.py, figures/diurnal_comparison.png + diurnal_data.csv, PROTOTYPE_VERDICT.md. |

| 2026-06-02 | Step 9 scope decision + doc formalized | ✅ GO (supplementary) | User approved folding light Step 9 into this paper as supplementary analysis. Doc brought up to date: status → APPROVED; both DR inputs marked RESOLVED with numbers folded into §9.2–§9.5 (DR-2 weight matrix + within-activity sub-splits + EFF co-presence; DR-1 SHEU provincial/dwelling anchors + flat baseload + Hydro-Québec split; seasonality = ±15% cosine on cooking+DHW only). Added a BUILD PLAN (aim/steps/expected/test) that fixes the 4 prototype red flags FIRST (dishwasher de-bounce, fridge double-zero, kWh-comparable baseline, N≥20), then promotes activity_loads.py into 07_aug_to_bem.py + integration.py, runs on Step-8's HH sample, validates vs Saldanha/B-M. **Implementation deferred — docs only; build runs after Step 8.** No code or 00–08 pipeline docs touched. |

| 2026-06-03 | Step 9 cluster run — Phase 0 RECON + apartment SHEU targets | ✅ IN PROGRESS | Phase 0 complete. Three cells from _bigtest: SingleD×Winnipeg_7A, HighRise×Montreal_6A, MidRise×Toronto_5A (n=20, seed=42, 2022+2030). Architecture: TWO-STAGE (Stage A: Python/eppy → IDFs in sbatch; Stage B: SLURM array 240 tasks; Stage C: validate). RF4 baseline: `07_aug_to_bem.py` `_CLASSIC_BAK` mechanism preserves 13-col baseline; 17-col activity CSVs generated on cluster. **Deviation D1 (documented in cluster_run.md):** per-DTYPE SHEU targets added — HighRise (1474/736 kWh), MidRise (1718/736 kWh), both derived by scaling SingleD appliance ratio (29.2%) to SHEU dwelling totals. `activity_loads.py` updated (`SHEU_BY_DTYPE` + `dtype` param to `calibrate_schedules`); `07_aug_to_bem.py` updated (passes per-HH `dtype_label` to calibrate). Predecessors archived: `archive/activity_loads.20260603.py`, `archive/07_aug_to_bem.20260603b.py`. Cluster scripts created in `Step9_docs/step9_cluster/`; `cluster_run.md` skeleton written. Phases 1–5 pending cluster execution. |

| 2026-06-04 | Step 9 cluster run — ALL PHASES COMPLETE; calibration FAIL | ❌ CALIBRATION FAIL (data exists, 240 runs) | **Phase 4 COMPLETE (job 948810):** 240/240 hourly_meters.csv, 0 FAIL logs. **Phase 5 validate FAIL (job 949086):** all 6 SHEU ±15% gates fail. Fixed validate.py: `3.6e9`→`3.6e6`, `/N_HH`, zone-level meters (`Zone Electric Equipment`/`Zone Lights Electricity Energy`). **Results (n=20 avg):** SingleD equip +63–74% over target (3252 kWh); HighRise equip -45–48% under (1474); MidRise equip -54–63% under (1718). All cells lighting overshoot +32–61%. **Root cause:** `inject_schedules` activity path — likely adds new equipment objects alongside existing IDF defaults (double-count for SingleD) or uses IDF Design_Level not calibrated Equip_Design_W (undershoot for apartments). **Investigation target:** `integration.py` activity injection path, then fix `07_aug_to_bem.py` calibration if needed, re-run A2+array. Data preserved in `/speed-scratch/o_iseri/step9_run/`. |

| 2026-06-04 | Step 9 precheck — stale IDF + fridge calibration bugs found and fixed | 🔧 PATCH 2 (A2 regen 949237 running) | **Bug 1 — stale IDF:** `step9_precheck.sh` used `find … | head -1` which returned Jun-3 IDFs (old HH IDs) instead of job-949144 IDFs. Fixed: precheck now reads `step9_manifest.csv` via `awk` to get the canonical IDF path. **Bug 2 — SF fridge overcounts:** SF archetype `refrigerator1` is 91.1 W with "Refrigerator" schedule → 668.7 kWh/yr; SHEU assumes 448 kWh. Keeping it untouched puts SingleD equipment +5.8% over the ±5% precheck gate. Fix: when named fridge found, override it to 51.14 W "Always On Discrete" (→ 448 kWh/yr) rather than keeping untouched. HighRise/MidRise PASS (no named fridge; inject STEP9_Fridge baseload). A2 regen 949237 running; precheck resubmit pending. |

| 2026-06-04 | Step 9 inject path — root cause confirmed + fix shipped | 🔧 FIX BUILT (pending cluster validation) | **Root cause (two-faced bug in `integration.py`):** (1) **SF IDFs:** `cache_key + continue` at lines 1509–1512 assigned the activity schedule to ALL ElectricEquipment/Lights objects but only overrode `Design_Level`/`Lighting_Level` on the first one → subsequent objects kept original IDF watts AND got the activity schedule → double-count (equip +63–74%, light +32–61%). (2) **NECB apartment IDFs:** `obj.Design_Level = _s9_equip_dw` is a no-op when `Design_Level_Calculation_Method = Watts/Area` → E+ used the NECB W/m² density, ignoring the calibrated value (equip −45–63% of target). **Fix (`integration.py` — neutralize-and-inject-carrier, lines 1497–1670):** Step 9 consolidation block runs BEFORE the `load_targets` loop: (a) Equipment — keep named fridge (name contains 'refrigerator' or schedule == 'Refrigerator') untouched; neutralize all other ELECTRICEQUIPMENT in the occupancy zone (Design_Level=0, Watts_per_Zone_Floor_Area=0, method=EquipmentLevel); inject one `STEP9_Equip_<hh>` carrier (EquipmentLevel, Design_Level=equip_design_W, activity schedule). If no named fridge found (NECB lump), inject `STEP9_Fridge_<hh>` with 51.14 W always-on (=448 kWh/yr) so SHEU net target is additive-correct. (b) Lighting — neutralize all LIGHTS in occupancy zone (Lighting_Level=0, Watts_per_Zone_Floor_Area=0, method=LightingLevel); inject one `STEP9_Lights_<hh>` carrier. Two loop guards at top of `load_targets` loop skip ELECTRICEQUIPMENT and LIGHTS when Step 9 is active — Step 8 path is byte-identical (block only entered when `_s9_equip_dw > 0`). Multi-zone apartment flag: warns if >1 People zone found; uses first zone and flags for Phase 5 meter verification. **Predecessor archived:** `archive/integration.20260604.py`. **New cluster scripts:** `step9_audit_idf.sh` (dumps IDF objects from old run to document bug), `step9_precheck.sh` (analytic pre-check on 3 cells, ±5% tolerance, zero leaks). **`precheck_calibration.py` updated** to recognize 'Always On Discrete' (E+ built-in schedule) as 1.0 for frac-hour calculation. **Validation pending:** audit → A2 regen → precheck (±5%) → smoke → full array → Phase 5 (±15% all 6 gates). |
| 2026-06-05 | Step 9 cluster run — 3-cell/n=20 validation COMPLETE | ✅ 6/6 GATES PASS | **Inject fix VALIDATED end-to-end.** Precheck PASS all 3 cells. Array **950562**: 239/240 hourly_meters (1 warmup-convergence fail — MidRise/HH1865/2030). Validate job **950833**: all 6 SHEU ±15% gates PASS — HighRise −0.1%/−0.1%, MidRise +0.3%/−5.6%, SingleD +0.0%/+0.0%; sleep-check PASS (WARN on MidRise-2022 + SingleD residual baseload). Three root causes fixed: (1) 17-col activity CSV (`Equip_Design_W`) never uploaded → ran `07_aug_to_bem.py`; (2) fridge → `Schedule:Compact` (always 1.0) for E+24.2 compat + precheck parseability; (3) validate column bug — activity reads `InteriorEquipment`/`InteriorLights` (zone-level extracts 0 after S9 neutralization). Results: `/speed-scratch/o_iseri/step9_run/cluster_run_results.csv`. **Next (after Step 8 closes): full 24-cell/n=50 grid + plots + SI write-up.** |

| 2026-06-05 | S9-A — full 24-cell/n=50 scripts built | 🔧 SCRIPTS READY — awaiting upload + sbatch | **OtherDwelling audit complete.** `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` has 7 named refrigerators (`refrigerator_unit1–7`, 91.06 W each, `EquipmentLevel`, schedule `Refrigerator`) across 7 unit zones — takes the **named-fridge calibration path** (same as SingleD). *(Count corrected 2026-06-06: direct IDF inspection found 7, not 5; the earlier "5" came from a template IDF. D8 correction updated accordingly below.)* SHEU targets already in `activity_loads.SHEU_BY_DTYPE` (`OtherDwelling: (2691.0, 1100.0)`); no code edits needed. **Multi-unit fridge correction (D8):** building-level `InteriorEquipment:Electricity` captures 7 fridges; `step9_validate_full.py` subtracts 6 × 448 kWh = 2,688 kWh from activity reading for OtherDwelling cells before the ±15% gate. Precheck (occupancy-zone only) is unaffected. **6 new cluster scripts:** `step9_idf_gen_full.py` (24 cells × n=50); `step9_a_generate_full.sh` (A1+A2-1+A2-2 folded in one job); `step9_precheck_full.sh` (4 archetypes, incl. OtherDwelling); `step9_b_array_full.sh` (48-task array, 4-parallel E+ per task, 100 IDFs/task); `step9_validate_full.py` (24-cell CELL_DTYPE + D8 correction); `step9_c_validate_full.sh`. `cluster_run.md` updated: D7 (OtherDwelling SHEU + fridge audit) + D8 (validate correction) + full-grid Phase Status table. **Next:** upload scripts → sbatch `step9_a_generate_full.sh` (Stage A: ~2h) → precheck (4 cells) → smoke → sbatch `step9_b_array_full.sh` (48 tasks, 9,600 E+ runs) → sbatch `step9_c_validate_full.sh`. |
