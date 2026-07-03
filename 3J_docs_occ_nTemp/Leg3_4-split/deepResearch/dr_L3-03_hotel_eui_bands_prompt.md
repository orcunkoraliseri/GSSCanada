# Deep-Research Prompt dr_L3-03 — HOTEL EUI PLAUSIBILITY BANDS for Canada (empirical + as-modelled)

> SCOPE GUARD — READ FIRST. This is the **hotel energy-benchmark** task of the Leg-3 set. Its job is to
> produce two defensible EUI bands (kWh/m²/yr) for validating simulated hotel floors: an **AS-MODELLED
> band** from code prototypes (= PASS criterion) and an **EMPIRICAL band** from Canadian survey data
> (= INFO criterion) — plus the occupancy-elasticity evidence unique to hotels. Do NOT cover retail
> (that is `dr_L3-02`), do NOT research hotel occupancy *data sources* (that is `dr_L3-01`), and do NOT
> derive diurnal guest-room shapes (that is `dr_L3-05`). See `00_deep_research_prompts_Leg3.md` for
> shared facts and conventions.

---

## What this document is

A benchmark-band brief. We simulate the **hotel floors** (LargeHotel-style guest rooms + amenity
spaces: Banquet / Cafe / Kitchen / Lobby / Laundry) of PNNL Tall / SuperTall mixed-use prototypes
(NECB 2017, climate zones 6A Montreal and 7A Calgary) in EnergyPlus. Guest-room schedules are modulated
by `s(t) × StatCan monthly occupancy rate`; amenity zones stay on NECB baseline in v1. The validator
needs numeric bands to judge the simulated hotel EUI, in the same two-band structure proven in Leg 2.

> **Anchor — the Leg-2 office gate this prompt must replicate for hotels (pre-filled, project-internal).**
> For the office channel we locked: as-modelled band **(central 135, low 100, high 200) kWh/m²/yr**
> from NECB/DOE-PNNL office prototypes in cold climates = **PASS criterion**; empirical band
> **(central 230, low 170, high 360) kWh/m²/yr** from NRCan SCIEU = **INFO criterion**. The simulated
> office median (180) fell inside the as-modelled band → PASS. Your deliverable is the hotel analogue
> of exactly this structure.

## Role

Building-energy benchmarking analyst with hospitality-sector depth. Ground the empirical side in NRCan
SCIEU / CEUD accommodation-sector figures; ground the as-modelled side in US DOE / PNNL Large Hotel and
Small Hotel prototype results (ASHRAE 90.1 vintages, cold climate zones 6/7) and any NECB 2017/2020
hotel archetype studies for Canada; use US CBECS lodging distributions as cross-check context; add the
hotel-specific literature on energy-vs-occupancy elasticity (energy per occupied room, fixed base
load). Keep survey-empirical and prototype-simulated numbers strictly separate.

## Why this matters (so you scope correctly)

The hotel channel is the only one whose *validation* couples to an external data series: if the
simulated EUI responds too strongly (or not at all) to the monthly occupancy multiplier, the gate must
distinguish "wrong band" from "wrong elasticity". Hotels are famous for a large presence-independent
load share (DHW, laundry, kitchen, corridor conditioning, 24/7 lobby) — measured elasticities say how
much annual EUI *should* move when occupancy swings, which is exactly what our scenario runs vary. A
band without the elasticity context would let a flat, non-responding simulation pass — the precise
failure mode (silently unmodulated schedules) that burned the Leg-2 office channel.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Empirical Canadian accommodation EUI (SCIEU / CEUD)

| Source + survey year | Building class definition ("accommodation", "accommodation & food services", lodging) | Median EUI (kWh/m²/yr) | Spread (quartiles / range) | Fuel coverage | Known biases (motels vs full-service urban hotels, vintage) | Citation |
|---|---|---|---|---|---|---|
| NRCan SCIEU (latest) |  |  |  |  |  |  |
| NRCan SCIEU (earlier waves, if published) |  |  |  |  |  |  |
| NRCan CEUD (accommodation) |  |  |  |  |  |  |

### Table 2 — As-modelled hotel EUI (prototypes / archetypes, cold climate)

| Prototype / study | Code vintage | Climate zone | EUI (kWh/m²/yr) | Fuel coverage | Citation |
|---|---|---|---|---|---|
| DOE-PNNL Large Hotel |  | CZ 6 |  |  |  |
| DOE-PNNL Large Hotel |  | CZ 7 |  |  |  |
| DOE-PNNL Small Hotel |  | CZ 6/7 |  |  |  |
| NECB 2017/2020 hotel archetype study (Canada) |  |  |  |  |  |
| (any other cold-climate hotel simulation study) |  |  |  |  |  |

### Table 3 — US context for cross-checking (CBECS lodging)

| CBECS year | Category | Median / mean EUI (converted to kWh/m²/yr) | US-vs-Canada caveats | Citation |
|---|---|---|---|---|
|  |  |  |  |  |

### Table 4 — Hotel end-use split and occupancy elasticity (the hotel-specific part)

| Quantity | Value | Source |
|---|---|---|
| DHW share of hotel EUI (%) |  |  |
| Guest-room vs amenity/back-of-house EUI split |  |  |
| Fixed (presence-independent) share of total load (%) |  |  |
| Measured elasticity: % energy change per 10 pp occupancy change (or energy per occupied room) |  |  |
| COVID natural experiment: reported hotel energy drop at collapsed occupancy (2020) |  |  |

### Table 5 — RECOMMENDED VALIDATOR BANDS (the deliverable)

| Band | Low | Central | High | Role in validator | Justification (one paragraph each, below the table) |
|---|---|---|---|---|---|
| Hotel **as-modelled** (prototype, CZ 6/7) |  |  |  | **PASS criterion** |  |
| Hotel **empirical** (SCIEU/CEUD) |  |  |  | **INFO criterion** |  |
| Occupancy-response check (expected EUI swing across our occupancy scenarios) |  |  |  | **differentiation gate support** |  |

---

## Part C — Synthesis (bands + elasticity verdict + caveat list)

Give: (1) the two EUI bands restated with justifications; (2) an **elasticity verdict**: for a monthly
occupancy multiplier swinging between the observed QC/AB extremes (COVID trough → pre-COVID peak), what
annual-EUI response range is defensible for guest-room-modulated-only simulation (amenities on
baseline) — this feeds the scenario-differentiation gate; (3) the **caveat list** for the validator
documentation — floor-area basis, fuel coverage, amenity inclusion, occupancy-normalization
(EUI per m² vs per occupied room-night), mixed-use podium hotel vs standalone prototype; (4) whether
Small Hotel or Large Hotel prototype is the better as-modelled anchor for hotel floors embedded in a
tall mixed-use tower, and why.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Every EUI given in kWh/m²/yr with fuel coverage stated; show conversions from kBtu/ft² or GJ/m².
4. **"Confidence and caveats":** which band bound or elasticity number is least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Never mix survey-empirical and prototype-simulated numbers in one band.**
- **The elasticity row is mandatory** — a band answer without occupancy-response evidence does not
  close this prompt.
- **State fuel coverage for every number.**
- **No fabricated precision;** flag GAPs (e.g., if SCIEU has no clean accommodation-only class, say so
  and propose the nearest defensible proxy).
- **Stay on topic** — energy benchmarks and elasticity only; no occupancy data sources, no diurnal
  shapes.
