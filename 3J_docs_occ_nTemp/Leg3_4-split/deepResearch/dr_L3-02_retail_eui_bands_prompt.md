# Deep-Research Prompt dr_L3-02 — RETAIL EUI PLAUSIBILITY BANDS for Canada (empirical + as-modelled)

> SCOPE GUARD — READ FIRST. This is the **retail energy-benchmark** task of the Leg-3 set. Its job is
> to produce two defensible EUI bands (kWh/m²/yr) for validating simulated retail zones: an
> **AS-MODELLED band** from code prototypes (= PASS criterion) and an **EMPIRICAL band** from Canadian
> survey data (= INFO criterion). Do NOT cover hotels (that is `dr_L3-03`), do NOT research retail
> occupancy patterns or footfall (already covered by the foundational Prompt-7 report in
> `deepResearch_Resources/`), and do NOT forecast retail trends (that is `dr_L3-04`). See
> `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A benchmark-band brief. We simulate the **retail podium zones** of PNNL Tall / SuperTall mixed-use
prototype buildings (NECB 2017, climate zones 6A Montreal and 7A Calgary) in EnergyPlus, with occupancy
schedules modulated by a GSS-derived customer-presence multiplier. The validator needs numeric bands to
judge the simulated retail EUI. Surveyed building stock and code-minimum prototypes differ
systematically, so we always carry **both** bands and give them different roles.

> **Anchor — the Leg-2 office gate this prompt must replicate for retail (pre-filled, project-internal).**
> For the office channel we locked: as-modelled band **(central 135, low 100, high 200) kWh/m²/yr**
> from NECB/DOE-PNNL office prototypes in cold climates = **PASS criterion**; empirical band
> **(central 230, low 170, high 360) kWh/m²/yr** from NRCan SCIEU = **INFO criterion**. The simulated
> office median (180) fell inside the as-modelled band → PASS. Your deliverable is the retail analogue
> of exactly this structure.

## Role

Building-energy benchmarking analyst. Ground the empirical side in NRCan's Survey of Commercial and
Institutional Energy Use (SCIEU) and the Comprehensive Energy Use Database (CEUD); ground the
as-modelled side in the US DOE / PNNL commercial prototype results (Standalone Retail, Strip Mall,
ASHRAE 90.1 vintages, cold climate zones 6/7) and any NECB 2017/2020 retail archetype studies for
Canada; use US CBECS mercantile distributions only as cross-check context. Keep survey-empirical and
prototype-simulated numbers strictly separate.

## Why this matters (so you scope correctly)

The Leg-2 office validation initially confused these two bases and produced a false alarm (a simulated
prototype judged against surveyed-stock EUI looks implausibly low). The two-band structure — prototype
band as the pass criterion, survey band as information — resolved it. Retail adds a sharper version of
the same trap: surveyed "retail" includes grocery stores whose refrigeration load inflates EUI far
above a non-food podium retail zone, and our retail zones are *inside a tall building* (shared HVAC,
no roof/ground exposure) while the prototypes are standalone boxes. Getting the bands and their caveats
right up front prevents weeks of chasing a "failed" gate that was actually a basis mismatch.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Empirical Canadian retail EUI (SCIEU / CEUD)

| Source + survey year | Building class definition ("retail trade", "mercantile", etc.) | Median EUI (kWh/m²/yr) | Spread (quartiles / range) | Fuel coverage (electricity-only vs all-fuels) | Known biases (vintage mix, mall vs standalone, grocery share) | Citation |
|---|---|---|---|---|---|---|
| NRCan SCIEU (latest) |  |  |  |  |  |  |
| NRCan SCIEU (earlier waves, if published) |  |  |  |  |  |  |
| NRCan CEUD (commercial/institutional, retail) |  |  |  |  |  |  |

### Table 2 — As-modelled retail EUI (prototypes / archetypes, cold climate)

| Prototype / study | Code vintage | Climate zone | EUI (kWh/m²/yr) | Fuel coverage | Citation |
|---|---|---|---|---|---|
| DOE-PNNL Standalone Retail |  | CZ 6 |  |  |  |
| DOE-PNNL Standalone Retail |  | CZ 7 |  |  |  |
| DOE-PNNL Strip Mall |  | CZ 6/7 |  |  |  |
| NECB 2017/2020 retail archetype study (Canada) |  |  |  |  |  |
| (any other cold-climate retail simulation study) |  |  |  |  |  |

### Table 3 — US context for cross-checking (CBECS mercantile)

| CBECS year | Category | Median / mean EUI (converted to kWh/m²/yr) | US-vs-Canada caveats (climate, fuel mix, stock) | Citation |
|---|---|---|---|---|
|  |  |  |  |  |

### Table 4 — Retail end-use split (how much EUI is occupancy-modulatable)

| End use | Share of retail EUI (%) | Follows occupancy / opening hours / fixed? | Source |
|---|---|---|---|
| Lighting |  |  |  |
| HVAC (heating + cooling + fans) |  |  |  |
| Refrigeration (grocery only) |  |  |  |
| Plug / equipment |  |  |  |
| DHW / other |  |  |  |

### Table 5 — RECOMMENDED VALIDATOR BANDS (the deliverable)

| Band | Low | Central | High | Role in validator | Justification (one paragraph each, below the table) |
|---|---|---|---|---|---|
| Retail **as-modelled** (prototype, CZ 6/7) |  |  |  | **PASS criterion** |  |
| Retail **empirical** (SCIEU/CEUD) |  |  |  | **INFO criterion** |  |

---

## Part C — Synthesis (bands + caveat list)

Give: (1) the two bands from Table 5 restated with their justifications; (2) an explicit **caveat
list** for the validator documentation — at minimum: floor-area basis (gross vs conditioned), fuel
coverage, whether common areas are included, the grocery-refrigeration skew in survey data, and the
**podium-retail vs standalone-prototype mismatch** (our zones share HVAC and envelope with a tall
building — state the expected direction of bias); (3) a recommendation on whether grocery-class sources
should be excluded from the empirical band entirely, given our podium retail is non-food by prototype
definition.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Every EUI given in kWh/m²/yr with fuel coverage stated in the same cell or column; show the
   conversion when a source publishes in other units (kBtu/ft², GJ/m²).
4. **"Confidence and caveats":** which band bound is least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Never mix survey-empirical and prototype-simulated numbers in one band** — the two-band separation
  is the entire point.
- **State fuel coverage for every number** (electricity-only vs all-fuels changes retail EUI hugely).
- **No fabricated precision;** flag GAPs (e.g., if SCIEU does not publish a retail-class median, say so
  and propose the nearest defensible proxy).
- **Stay on topic** — energy benchmarks only; no occupancy schedules, no trend forecasting.
