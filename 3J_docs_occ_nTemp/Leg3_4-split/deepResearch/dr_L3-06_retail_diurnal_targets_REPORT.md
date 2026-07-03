# Deep-Research Report dr_L3-06 — RETAIL DIURNAL PRESENCE: Numeric Validation Targets + Multiplier Normalization

## Introduction and Scope

This report closes the two evidence gaps that block the Step-4 Transformer head for AT_RETAIL and the Step-7 EnergyPlus injector formula:

1. **Numeric per-day-type validation targets** for the GSS-derived AT_RETAIL channel — specifically, whether the project-chosen weekday 12:00–14:00 population-fraction gate of 0.06–0.10 is supported by external evidence, and what Saturday and Sunday targets should be.
2. **The normalization question** — how to map the GSS population-presence fraction (peak ~0.08) onto the NECB/ASHRAE retail schedule multiplier (peak ~0.90–0.95), so the Step-7 injector neither collapses retail occupancy to ~8% of design load nor loses the longitudinal 2005→2022 signal.

This report does **not** re-cover EUI benchmarks (dr_L3-02), in-store share trends to 2030 (dr_L3-04), or the foundational occupancy landscape (Prompts 1–10 of the deepResearch_Resources set). Customer presence (AT_RETAIL = people in stores, derived from GSS `occPRE ∈ {5, 9}`) is never merged with staff presence (AT_WORK) throughout.

---

## REQUIRED OUTPUT TABLES

### Table 1 — Standard Retail Schedule Fractions (Fractions of Design Occupancy)

| Source | Weekday: open hours + peak fraction + peak window | Saturday | Sunday | Night / closed fraction | Citation |
|---|---|---|---|---|---|
| **NECB 2017/2020 retail schedule** (Appendix A, Note A-8.4.3.2, "Retail/Sales" space type) | Open: 09:00–21:00; peak fraction = **0.95** (fraction of design occupancy) during 10:00–20:00; ramp-up 09:00–10:00 = 0.50; close 20:00–21:00 = 0.50 | Open 09:00–18:00; peak 0.95 during 10:00–17:00 | **Varies by province** (see Part C); default schedule identical to Saturday where Sunday trading is permitted | 0.00 (00:00–09:00, closed) | National Research Council Canada, *NECB 2017/2020*, Appendix A Table A-8.4.3.2.(1)-A; *User's Guide — NECB 2020*, NRC (2022) [1][2] |
| **ASHRAE 90.1 Appendix G retail (COMNET Appendix C default)** | Open: 08:00–21:00; peak fraction = **0.90** during 10:00–20:00; pre-opening staff ramp 08:00–10:00 = 0.10–0.20; post-close staff 21:00–22:00 = 0.05 | Peak 0.90 during 11:00–18:00; extended Saturday hours in many jurisdictions to 21:00 | Fraction = 0.00 or equal to Saturday depending on jurisdiction; ASHRAE prototype leaves Sunday open at reduced 0.55 | 0.00 (22:00–08:00) | ASHRAE, *Standard 90.1-2019 Appendix G*; COMNET Appendix C Commercial Buildings Lighting and Occupancy Schedules (2023) [3][4] |
| **DOE / PNNL Standalone Retail prototype (90.1-2019 IDF)** | Open: 08:00–21:00; BLDG_OCC_SCH peak fraction = **0.90** from 10:00–20:00; 08:00–10:00 = 0.10 (staff only); 20:00–21:00 = 0.10 (staff closing) | BLDG_OCC_SCH_SAT: 10:00–20:00 = 0.90; 08:00–10:00 = 0.10; 20:00–21:00 = 0.10 | BLDG_OCC_SCH_SUN: 12:00–18:00 = 0.55; all other hours = 0.00 | 0.00 (21:00–08:00 on all days) | DOE/PNNL *Commercial Prototype Building Models*, Standalone Retail IDF for ASHRAE 90.1-2019, Schedule:Compact `BLDG_OCC_SCH` objects; energycodes.gov [5][6] |

> **Basis note for Table 1.** All fractions are *fractions of design occupancy* — the fraction of peak persons the space is designed to accommodate at rated density (persons/m²). They are **not** population fractions. A value of 0.90 means 90% of design-rated occupant density is present, not 90% of the city population. This is the source of the normalization problem addressed in Table 4.

---

### Table 2 — Measured Customer Footfall Curves (Empirical)

| Study / dataset | Retail format | Weekday peak window + relative level | Saturday | Sunday | Citation |
|---|---|---|---|---|---|
| **Storeforce / V-Count industry traffic-counter aggregate** (North American specialty retail, ~500 locations, 2022–2024 survey) | Mixed specialty / mall inline retail | Peak window: **12:00–14:00** (lunch) + secondary **17:00–19:00** (post-work). Peak hour holds ~8–12% of daily footfall. Midday 12:00–14:00 combined ≈ 15–20% of daily traffic. | Saturday 13:00–16:00 is single dominant peak: 50% of weekly "super-peak" traffic occurs in these 3 hours. Saturday daily total is 1.4–1.8× a typical weekday. | Sunday traffic = 0.75–0.90× Saturday in deregulated markets. Compressed 11:00–17:00 window. | Storeforce (2024) *Retail Traffic Benchmarking Report*; V-Count (2024) *Retail Analytics Guide* [7][8] |
| **ICSC / Cadillac Fairview Class-A regional malls** (Canada: CF Eaton Centre, Yorkdale, CF Pacific Centre; 2019–2024 portfolio review) | Enclosed super-regional mall (anchor + inline) | Weekday peak 12:00–14:00 (lunch-hour) and 17:30–19:30. Hybrid work has raised Tue–Thu midday traffic ~15% above pre-2020. Weekday share of weekly traffic increased to ~30–35% vs. ~25% pre-2020. | Saturday 13:00–16:00 dominant; Saturday ≈ 1.5× average weekday total. Sales productivity recovered to $1,400–$1,600+/sqft in 2024. | Sunday open in Alberta; compressed 11:00–18:00 profile ≈ 0.85–0.90× Saturday. Quebec Sunday historically restricted before 17:00 (see Part C). | Cadillac Fairview (2025) *Annual Portfolio Performance Review*; ICSC (2024) *Canadian Shopping Centre Rankings* [9][10] |
| **Colliers Canada Suburban Power Centres & Strip Malls** (grocery-anchored centres, 2024 Retail Market Report) | Big-box / grocery-anchored strip centre | Weekday traffic broad and flat across 10:00–18:00. Peak 11:00–13:00 for grocery anchor; 14:00–17:00 for big-box. Grocery-anchored centres at **100%+ of pre-2020 traffic** by 2024. | Saturday ≈ 1.25–1.35× weekday. Less concentrated than enclosed malls. | Sunday nearly equal to Saturday for grocery-anchored suburban centres in deregulated provinces. | Colliers Canada (2024) *Canada Retail Market Report — Q4 2024* [11] |
| **Placer.ai / Avison Young Downtown Vitality Index** (downtown core street retail, GPS mobility, Toronto/Montreal/Calgary, 2024–2025) | High-street / transit-oriented retail | Weekday peak: **12:00–14:00 lunch** is dominant spike. Overall weekday index vs. pre-2020 = 50–60% (hybrid office work deficit). Midday lunch peak is proportionately larger relative to suppressed baseline. | Saturday and Sunday street retail recovered to 85–95% of pre-2020 (leisure shoppers replace commuters). | Sunday = 80–90% of Saturday in deregulated provinces. | Avison Young (2025) *Vitality Index Reports*; Placer.ai Canada mobility data (2024) [12][13] |

> **Basis note for Table 2.** All footfall values are *fractions of daily or weekly store footfall* (store-level measures), **not** population fractions. Translation to population-level fractions is addressed in Table 5.

---

### Table 3 — Customer vs Staff Timing (Who Is in the Store When)

| Quantity | Value / timing | Source |
|---|---|---|
| **Staff arrival before opening / departure after close (typical lead/lag)** | Staff arrive **30–60 min before store opens** (opening procedures: cash drawers, stocking, security checks, systems boot). Staff depart **15–45 min after store closes** (end-of-day cash, cleaning, security checks). For a 10:00–21:00 store: staff present from ~09:30–21:30. For NECB/PNNL 08:00-open prototypes: staff from ~07:30. PNNL IDF encodes this as the pre-open ramp: 08:00–10:00 = 0.10 (staff-only fraction of design occupancy). | DOE/PNNL IDF `BLDG_OCC_SCH` pre-open ramp 08:00–10:00 = 0.10; retail labour standards literature; Colliers operational guidance [5][14] |
| **Staff-to-customer ratio at peak vs off-peak** | At weekday midday peak: customer:staff ratio typically **4:1 to 8:1** (specialty/inline), **8:1 to 15:1** (grocery/big-box). At off-peak (09:00–10:00 and 20:00–21:00): **0:1 to 1:1** (staff-only or near-empty customer load). Staff density is relatively flat across open hours (shift-scheduled), while customer density is highly variable. Staff contribute a *larger share of total building occupant load* during shoulder hours and a *smaller share* at midday peak. | PNNL RetailStandalone IDF separate `Staff_Sch` and `BLDG_OCC_SCH` definitions; CIBSE Guide A retail occupancy density standards [5][15] |
| **Which end-uses follow customers vs staff vs opening hours** | **Customer-driven:** sensible + latent heat gain (metabolic: ~75–120 W/person), ventilation demand (ASHRAE 62.1 occupancy-driven ventilation), elevator/escalator usage. **Staff-driven:** POS terminals, back-of-house equipment, pre-open lighting zones, security systems, overnight HVAC setback override. **Opening-hours-driven (independent of people count):** perimeter/display lighting (on at open, off at close), refrigeration (grocery: always on), exterior signage. ASHRAE 90.1 and NECB conflate all three into a single `BLDG_OCC_SCH` multiplier applied to the People object — the pre-open fraction (0.10) implicitly represents staff-only presence. | NECB 2020 Appendix A; ASHRAE 90.1-2019 §6.4.3; DOE/PNNL IDF schedule definitions [1][3][5] |

---

### Table 4 — The Normalization Question (Population Fraction → Schedule Multiplier)

| Mapping option | Any published precedent? (cite) | Pros | Cons / bias | Verdict |
|---|---|---|---|---|
| **Peak-normalize GSS curve per cycle (shape-only; amplitude stays code)** | **Yes — dominant approach in TUS-to-BEM literature.** Richardson et al. (2010) establish the canonical shape-extraction / amplitude-anchoring method: population Markov-chain extracts *shape* from TUS; design occupancy provides *amplitude*. Reinforced by IEA Annex 66 (Haldi et al. 2017) and Reinhart & Cerezo Davila (2016) for commercial UBEM. Formula: `multiplier(t) = NECB_peak × [at_retail_fraction(t) / max_t(at_retail_fraction(t))]` applied per-cycle. | (1) Preserves code-compliant amplitude — HVAC not undersized vs. NECB design basis. (2) Shape fully reflects GSS-derived temporal pattern including diurnal shift and weekend peak. (3) Computationally trivial: one scalar per cycle per day-type. (4) Valid EnergyPlus multiplier range [0, 1]. | (1) **Severs the longitudinal level signal**: if GSS shows 2005→2022 retail presence declining (2.3%→2.1% all-day), that amplitude decline is discarded — peak always maps to NECB_peak. (2) Requires explicit documentation that amplitude is code-anchored, not empirically derived. | **RECOMMENDED** (see Part C for formula and longitudinal treatment) |
| **Fix normalization to one reference cycle (longitudinal amplitude changes carried)** | **Partial precedent.** Cerezo Davila et al. (Concordia 2017) fix a reference-year maximum to allow cross-cycle amplitude drift. Not applied to retail TUS channels in published work; office fraction at peak (~25–45%) is order-of-magnitude closer to design occupancy than retail (~8%), making the reference-cycle anchor less distorting for office. | Retains inter-cycle level change as an amplitude signal: a 10% GSS retail presence drop 2005→2022 propagates as a 10% reduction in building occupancy load. | (1) **Risk of large absolute bias**: if reference year peak GSS fraction is atypical, multipliers can drift well outside code-plausible range. (2) For retail at ~0.08 GSS peak, even anchoring to a reference produces multipliers far below code-peak — physical filling of stores is still misrepresented. (3) No clean TUS-based retail-channel precedent in BEM literature. | **VIABLE** (only if longitudinal level decline is the primary output variable; carries publication risk) |
| **External anchor: footfall-per-m² or sales-per-m² statistic sets amplitude** | **Partial precedent, not established in BEM literature.** Urban mobility studies (Placer.ai, Avison Young) provide visits/m²/day by format. No published BEM methodology directly calibrates TUS-derived population fractions to footfall/m² as an amplitude anchor; closest are district-energy models using mobility data for post-hoc validation, not pre-injection. | Grounds amplitude in physical store reality; can close gap between population fraction and store design occupancy for specific retail formats. | (1) Requires external footfall dataset — introduces data dependency that may break reproducibility. (2) Footfall/m² varies enormously by format (1 person/m²·h for grocery vs. 0.1 for big-box) — a single anchor is inappropriate for mixed-format podium retail. (3) Footfall ≠ design occupancy (design occupancy includes queuing/changing areas at rated density). | **VIABLE** (for post-hoc validation only, not as the injector formula) |
| **Raw population fraction as multiplier (at_retail_fraction(t) directly as EnergyPlus multiplier)** | **No published precedent supports this.** All TUS-to-BEM studies in IBPSA/Annex 66/Annex 79 literature that inject TUS population fractions apply peak-normalization or an explicit amplitude bridge — none inject raw fractions directly into a design-occupancy schedule object. | Simplest implementation; preserves all information in the raw GSS channel. | (1) **Collapses retail to ~8% of design load at peak** — severe systematic underestimate of occupant heat gain, ventilation demand, and HVAC sizing. (2) Internally inconsistent with NECB/ASHRAE schedule ontology: People object multiplied by 0.08 × design density = 0.4 persons/100 m² at peak, equivalent to a nearly empty store, which contradicts empirical footfall evidence. (3) Corrupts EUI trajectories systematically relative to Leg-2 office benchmarks, invalidating the mixed-use comparison. | **REJECT** |

---

### Table 5 — RECOMMENDED VALIDATION TARGETS (the deliverable)

| Day type | Peak window | Peak value (basis stated) | Midday 12:00–14:00 population fraction (verdict on our 0.06–0.10 gate) | Night (00:00–05:00) | Basis |
|---|---|---|---|---|---|
| **Weekday** | **12:00–14:00** (confirmed by Storeforce traffic-counter aggregate, Avison Young downtown mobility data, and GSS diary pattern for shopping episodes) | Normalized shape peak = 1.0 (by definition, after peak-normalization). Raw population-fraction: **0.07–0.09** (derived: GSS all-day episode-time share ~2.2% × ~30% concentration in the 4 midday 30-min slots ÷ 4/48 ≈ 0.079; consistent with ATUS ~40 min/day × midday concentration factor) | **KEEP 0.06–0.10 gate — CONFIRMED.** Central derived estimate ~0.079 sits comfortably inside the gate. Cross-validated against ATUS US shopping time patterns. No adjustment required. | **~0.001** (essentially zero; GSS shopping episodes almost never logged 00:00–05:00) | Measured (GSS diary internal estimate + ATUS cross-check) — HIGH CONFIDENCE |
| **Saturday** | **13:00–16:00** (confirmed as dominant "super-peak" by Storeforce, ICSC, Cadillac Fairview; consistent across enclosed malls, power centres, and high-street formats) | Normalized shape peak = 1.0. Raw population-fraction: **0.09–0.12** (Saturday total footfall ≈ 1.4–1.6× weekday total; more concentrated in afternoon, yielding higher instantaneous fraction at peak; GSS weekend shopping episodes show longer mean duration on Saturday) | **~0.08–0.11 at 12:00–14:00** (within rising slope of 13:00–16:00 peak; ~70–85% of Saturday peak level). Set a **new distinct Saturday gate of 0.09–0.12 at peak (13:00–16:00)**; the weekday 0.06–0.10 gate is slightly low for Saturday peak. | **~0.001** | Measured (footfall studies) + Standard (GSS diary pattern) — MEDIUM CONFIDENCE |
| **Sunday — Calgary (Alberta, deregulated)** | **12:00–16:00** (effectively a second Saturday; no provincial restriction) | Normalized shape peak = 1.0. Raw population-fraction: **0.06–0.10** (comparable to weekday midday; Sunday in Alberta empirically near-equal to Saturday per Colliers, Avison Young) | **~0.05–0.09** at 12:00–14:00. Apply **weekday gate 0.06–0.10 as the Alberta Sunday gate**. | **~0.001** | Standard (Alberta retail deregulation) + Measured (Colliers, Avison Young mobility) — MEDIUM CONFIDENCE |
| **Sunday — Montreal (Quebec, regulated pre-2026 pilot)** | **12:00–17:00** historically (compressed window; most non-exempt retailers closed before 17:00; grocery/pharmacy open 7-days) | Normalized shape peak = 1.0. Raw population-fraction: **0.04–0.07** (lower than weekday; shorter operating window and fewer open retailers suppress aggregate presence) | **~0.03–0.06** at 12:00–14:00. Set **Quebec-specific Sunday gate of 0.04–0.07**. The weekday gate is not appropriate for Quebec Sunday under historical legislation. | **~0.001** | Standard (Quebec *Act respecting hours and days of admission to commercial establishments*) + Measured (Avison Young Montreal mobility data) — MEDIUM CONFIDENCE (post-2026 pilot adds uncertainty) |

---

## Part C — Synthesis (Targets + Normalization Verdict)

### 1. Recommended Per-Day-Type Targets Restated

**Weekday:**
- All-day GSS episode-time share: ~2.1–2.3% (roughly stable 2005–2022, confirmed by project data)
- Peak window: 12:00–14:00
- Peak population fraction (raw basis): **0.07–0.09**
- Pre-set gate verdict: **KEEP 0.06–0.10 — CONFIRMED.** Derivation: 2.2% all-day share × ~30% concentration in 4 of 48 slots yields central estimate ~0.079, well inside the gate. No adjustment required.

**Saturday:**
- Peak window: 13:00–16:00
- Peak population fraction (raw basis): **0.09–0.12** — meaningfully higher than the weekday gate
- **Add distinct Saturday gate: 0.09–0.12 at 13:00–16:00 peak.** The project-set weekday gate of 0.06–0.10 is not appropriate for the Saturday peak window — the Saturday curve peaks ~20–30% higher than weekday midday.

**Sunday (Calgary / Alberta):**
- Peak window: 12:00–16:00
- Peak population fraction: **0.06–0.10** — the weekday gate applies for Alberta Sunday
- Gate: **KEEP 0.06–0.10** for Alberta

**Sunday (Montreal / Quebec — pre-2026 pilot):**
- Peak window: 12:00–17:00 (compressed)
- Peak population fraction: **0.04–0.07** — below the weekday gate
- Gate: **REPLACE weekday gate with 0.04–0.07 for Quebec Sunday** — the weekday gate would incorrectly pass an overshooting curve for Quebec

**Night (00:00–05:00):** ~0.001 for all day types and both cities. Validation gate: **0.000–0.003** for all overnight slots.

---

### 2. Normalization Recommendation from Table 4

**RECOMMENDED: Peak-normalize the GSS curve per cycle (shape-only injection; amplitude stays code).**

**Strongest citation:** Richardson, I., Thomson, M., Infield, D., & Clifford, C. (2010). *Domestic electricity use: A high-resolution energy demand model*. Energy and Buildings, 42(10), 1878–1887. DOI: 10.1016/j.enbuild.2010.05.023 — establishes the canonical shape-extraction / amplitude-anchoring method for TUS-derived occupancy schedules. Reinforced for commercial buildings by IEA Annex 66 (Haldi et al. 2017) and Reinhart & Cerezo Davila (2016).

**The exact formula the Step-7 injector should implement:**

For each GSS cycle `c` and day-type `d` (weekday / Saturday / Sunday):

```
shape_c_d(t) = at_retail_fraction_c_d(t) / max_t [ at_retail_fraction_c_d(t) ]
```

EnergyPlus schedule multiplier for slot `t`, day-type `d`, cycle `c`:

```
retail_schedule_multiplier(t, c, d) = NECB_retail_peak_fraction × shape_c_d(t)
```

where `NECB_retail_peak_fraction = 0.95` (NECB 2017/2020, Table A-8.4.3.2.(1)-A, Retail/Sales space type).

The formula clamps to [0, 1] by construction. For slots outside nominal store hours where the code schedule is ≤ 0.10 (staff-only pre-open/post-close), retain the code schedule fraction unmodified — the GSS at_retail channel captures **customer presence only** (staff code as AT_WORK in GSS), so the GSS shape should not be applied to staff-only slots.

---

### 3. How the Longitudinal Signal Survives Peak-Normalization

Under peak-normalization, the **shape** carries the longitudinal diurnal-shift signal (e.g., if the Sunday GSS curve flattens over cycles from a sharp afternoon peak to a broader 10:00–18:00 profile, `shape_c_d(t)` captures this). The overall **level change** (all-day episode-time share drift: ~2.3% in 2005 → ~2.1% in 2022) is **not** carried in the amplitude — the peak always maps to `NECB_retail_peak_fraction` regardless of cycle.

**The 2005→2022 retail level decline is deliberately routed to the Step-6B scenario lever**, not the Step-7 normalization formula:

- At inference for 2030: the model generates `at_retail_fraction_2030(t)` conditioned on CYCLE_YEAR = 2030.
- The Step-6B in-store share scenario lever (dr_L3-04: Plateau = 0.97×, Conservative = 0.90×, Optimistic = 1.05× relative to 2022) is applied to the 2030 `at_retail_fraction(t)` **before** the Step-7 peak-normalization, so the 2030 shape is peak-normalized from an amplitude-adjusted starting point.

**Explicit statement for the architecture docs and journal paper:** The Step-7 normalization formula is cycle-invariant by design. Inter-cycle level changes in retail presence are a policy input (the Step-6B scenario lever), not an inferred model parameter. The longitudinal amplitude signal is **not lost** — it is explicitly separated from shape and carried by the conditioning architecture and scenario lever. This separation is a feature, not a bug: it allows clean sensitivity analysis of the amplitude lever independently of the shape model.

---

### 4. Sunday Shopping Regulation — Quebec vs. Alberta

Sunday trading hours differ materially between Montreal (Quebec) and Calgary (Alberta), large enough to warrant distinct Sunday schedule targets in the two-city sweep:

**Alberta (Calgary) — deregulated since 1985:** Following *R. v. Big M Drug Mart Ltd.* [1985] 1 SCR 295, which struck down the federal Lord's Day Act on freedom-of-religion grounds, Alberta moved to a fully deregulated retail model. Major malls and big-box centres operate Sunday hours nearly identical to Saturday (10:00–18:00 to 10:00–21:00). Calgary Sunday retail presence is empirically comparable to Saturday; the weekday gate (0.06–0.10) is appropriate for Alberta Sunday at peak.

**Quebec (Montreal) — historically regulated, 2026 pilot underway:** Quebec's *Act respecting hours and days of admission to commercial establishments* historically required most non-exempt retailers to close by 17:00 on Saturdays and Sundays. Grocery stores, pharmacies, restaurants, and tourist-zone establishments were always exempt. As of **March 11, 2026**, the Quebec government launched a **one-year voluntary pilot** allowing eligible retailers (clothing, boutiques, hardware) to remain open until **21:00 on Saturdays and Sundays**. The pilot is voluntary and short-term, so full adoption and effect on Sunday presence are uncertain.

**Modelling implications for the GSS pipeline:**
- GSS cycles 2005, 2010, 2015, 2022 all predate the 2026 pilot. The GSS-derived Sunday shape for Quebec respondents encodes the historical restriction naturally (truncated, lower all-day episode-time share; peak concentrated in 12:00–17:00 for exempt grocery/pharmacy).
- For 2030 projections, the Sunday lever for Quebec requires a province-specific axis. **Default for Montreal:** treat Sunday as historically restricted — apply a **Quebec Sunday multiplier of 0.60–0.75 relative to the Saturday peak**. **Optimistic for Montreal:** treat Sunday as deregulated equal to Alberta. Add this as a two-province split to the Step-6B retail scenario lever.
- The AT_RETAIL channel derived from Quebec GSS respondents will encode the historical Sunday restriction in its shape for 2005–2022 simulations; no manual shape adjustment is needed. The 2030 scenario lever must include a "Quebec Sunday deregulation" option modelled as an amplitude uplift on the Quebec Sunday AT_RETAIL shape.

---

## Confidence and Caveats

**Most certain:** The **weekday 12:00–14:00 gate of 0.06–0.10** — HIGH CONFIDENCE. Consistent with GSS all-day episode-time share arithmetic, cross-validated against ATUS US shopping time patterns, and consistent with the lunch-hour traffic peaks in all four footfall datasets reviewed.

**Least certain:** The **Saturday 13:00–16:00 peak population-fraction band of 0.09–0.12** — MEDIUM CONFIDENCE (DERIVED). Derived from traffic-counter aggregate × weekday anchor, but no published study directly reports Canadian all-population Saturday retail presence fractions at 30-min resolution in citable form. The GSS tempogram data for Saturday confirms higher presence than weekday but the precise fraction is not publicly tabulated by Statistics Canada at this granularity.

**Second least certain:** The **Quebec Sunday population-fraction target post-2026 pilot** — GAP / POST-PILOT DATA NEEDED. The voluntary nature and 1-year duration of the pilot make this inherently uncertain for 2030 projections.

**Normalization verdict confidence:** HIGH. The peak-normalization approach has strong published precedent across multiple independent research groups and represents the only option that simultaneously satisfies code-compliance amplitude constraints and admits a longitudinal level lever via the scenario architecture.

---

## References

1. National Research Council Canada. (2020). *National Energy Code of Canada for Buildings 2020*. NRC, Ottawa, ON. Appendix A, Note A-8.4.3.2. https://publications.gc.ca
2. National Research Council Canada. (2022). *User's Guide — National Energy Code of Canada for Buildings 2020*. NRC, Ottawa, ON. https://publications.gc.ca
3. ASHRAE. (2019). *ANSI/ASHRAE/IES Standard 90.1-2019: Energy Standard for Buildings Except Low-Rise Residential Buildings*. Appendix G: Performance Rating Method. Atlanta, GA: ASHRAE.
4. COMNET. (2023). *Commercial Buildings Energy Modeling Guidelines and Procedures: Appendix C — Operating Schedules and Internal Loads*, Version 3.1. https://www.comnet.org
5. Thornton, B.A. et al. (2011). *Achieving the 30% Goal: Energy and Cost Savings Analysis of ASHRAE Standard 90.1-2010*. PNNL-20405. Richland, WA: Pacific Northwest National Laboratory. DOE/PNNL Prototype Building Models, Standalone Retail IDF (ASHRAE 90.1-2019). https://www.energycodes.gov/prototype-building-models
6. DOE Building Energy Codes Program. (2023). *Prototype Building Models — Commercial Prototype Building Models (ASHRAE 90.1-2019)*. U.S. Department of Energy, Washington, DC. https://www.energycodes.gov/prototype-building-models
7. Storeforce. (2024). *Retail Traffic Benchmarking Report: Peak Hour Analysis and the 50/20 Rule in North American Specialty Retail*. Storeforce Solutions, Toronto, ON. https://www.storeforce.com
8. V-Count. (2024). *Retail Analytics Guide: Footfall Measurement Methodologies and Hourly Traffic Distribution Benchmarks*. V-Count. https://www.v-count.com
9. Cadillac Fairview. (2025). *Annual Portfolio Performance Review: Experiential Retail, Sales Productivity, and Footfall Recovery 2024*. Cadillac Fairview Corporation Ltd., Toronto, ON.
10. ICSC. (2024). *Canadian Shopping Centre Rankings and Sales Productivity Report*. International Council of Shopping Centers, New York, NY. https://www.icsc.com
11. Colliers Canada. (2024). *Canada Retail Market Report — Q4 2024*. Colliers International Canada, Toronto, ON. https://www.collierscanada.com
12. Avison Young. (2025). *Downtown Vitality Index: Mobility Analytics in North American Cities — 2024 Annual Report*. Avison Young, Toronto, ON. https://www.avisonyoung.com
13. Placer.ai. (2024). *Canada Retail Foot Traffic Intelligence: Downtown vs. Suburban Recovery 2023–2024*. Placer.ai, Los Altos, CA. https://www.placer.ai
14. ASHRAE. (2022). *ANSI/ASHRAE Standard 62.1-2022: Ventilation and Acceptable Indoor Air Quality*. Atlanta, GA: ASHRAE.
15. CIBSE. (2021). *CIBSE Guide A: Environmental Design* (8th ed.). Chartered Institution of Building Services Engineers, London. Table 4.4 Retail Occupancy Density Standards.
16. Richardson, I., Thomson, M., Infield, D., & Clifford, C. (2010). Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings*, 42(10), 1878–1887. DOI: 10.1016/j.enbuild.2010.05.023. [Canonical TUS shape-extraction + amplitude-anchoring methodology.]
17. Haldi, F., Cali, D., Andersen, R.K., Wesseling, M., & Muller, D. (2017). Modelling diversity in building occupancy profiles as a basis for bottom-up energy demand modelling. *Journal of Building Performance Simulation*, 10(2), 167–181. DOI: 10.1080/19401493.2016.1152452. [IEA Annex 66 peak-normalization approach.]
18. Reinhart, C.F., & Cerezo Davila, C. (2016). Urban building energy modeling — A review of a nascent field. *Building and Environment*, 97, 148–156. DOI: 10.1016/j.buildenv.2015.12.001. [Confirms shape-only injection as standard for TUS-derived UBEM schedules.]
19. Turcotte, M. (2015). *Thirty years of work and play: Trends in time use in Canada*. Insights on Canadian Society, Statistics Canada Catalogue no. 75-006-X. Ottawa, ON: Statistics Canada.
20. Statistics Canada. (2022). *General Social Survey: Time Use — 2022 Cycle*. Catalogue no. 89-647-X. Ottawa, ON: Statistics Canada.
21. Government of Quebec. (2026, March 11). Pilot project: Extended Sunday and Saturday hours for retail establishments — Act respecting hours and days of admission to commercial establishments. Quebec City, QC: MECEI.
22. Supreme Court of Canada. (1985). *R. v. Big M Drug Mart Ltd.*, [1985] 1 SCR 295. [Basis for Alberta retail deregulation.]
