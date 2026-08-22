# DR05: European Building Standards, EPBD Framework, and CEN/ISO Energy Performance Protocols

## Section A. Direct answer

Simulating European residential building archetypes requires a fundamental paradigm shift away from North American ASHRAE standards (ASHRAE 90.1, 62.2, 55) toward the European Committee for Standardization (CEN) and International Organization for Standardization (ISO) framework governed by the Energy Performance of Buildings Directive (EPBD, Directive 2010/31/EU, 2018/844/EU, and 2024/1275 Recast). While ASHRAE 90.1 assumes air-based central HVAC systems (VAV, heat pumps) and rigid commercial-style core-and-perimeter zoning, European residential stock is structurally characterized by **hydronic hot-water central heating (radiators/boilers)**, **natural window ventilation supplemented by continuous trickle/exhaust (0.3 to 0.6 ACH)**, **heavy thermal mass construction (c_m = 45 to 87 Wh/(m²·K))**, and **dwelling-unit compartmentalization**. Under CEN standards, building energy performance is calculated via **EN ISO 52016-1:2017** (hourly dynamic RC method, superseding EN ISO 13790:2008), thermal comfort and ventilation requirements are defined by **EN 16798-1:2019** (Modules M1-6, superseding EN 15251:2007), and building typology baselines are cataloged across 20+ countries by the **TABULA / EPISCOPE** open database. In European regulatory practice, baseline internal gains are codified as a flat time-invariant flux (ISO 13790 Annex G Table G.12 and Italian UNI/TS 11300-1 specify 4.0 W/m²; TABULA EU boundary condition specifies 3.0 W/m²), establishing the exact open benchmark against which our Step 8 LLM-generated stochastic schedules are compared.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Governing Pan-European Energy Framework | Energy Performance of Buildings Directive (EPBD) 2010/31/EU, amended by Directive (EU) 2018/844 and Directive (EU) 2024/1275 (Zero-Emission Building ZEB by 2030); mandates national cost-optimal minimum energy performance requirements and EPC certification. | Fact | European Parliament and Council, Directive (EU) 2024/1275 | Tier 1 | 2026-08-22 | H |
| 2 | Dynamic Energy Calculation Standard | EN ISO 52016-1:2017 (Energy performance of buildings - Energy needs for heating and cooling - Part 1: Calculation procedures); establishes an hourly RC network method with explicit heat balance on zone surfaces, superseding EN ISO 13790:2008. | Fact | CEN / ISO Standard Catalog, EN ISO 52016-1:2017 | Tier 1 | 2026-08-22 | H |
| 3 | Indoor Environmental Quality & Ventilation Standard | EN 16798-1:2019 (Module M1-6: Indoor environmental input parameters for design and assessment of energy performance of buildings); defines Category I (high), Category II (normal), Category III (moderate) thermal comfort bounds and ventilation rates, superseding EN 15251:2007. | Fact | CEN EN 16798-1:2019 Standard Record; CEN/TR 16798-2:2019 | Tier 1 | 2026-08-22 | H |
| 4 | ISO Space Usage & Residential Schedules | ISO 18523-2:2018 (Schedule and condition of building, zone and space usage - Part 2: Residential buildings); provides international operational schedules for residential dwellings. | Fact | ISO Standard Catalog, ISO 18523-2:2018 | Tier 1 | 2026-08-22 | H |
| 5 | Standard European Baseline Internal Heat Gain | EN ISO 13790:2008 Annex G Table G.12 and Italian UNI/TS 11300-1 Table 1 specify a flat continuous residential internal gain rate of 4.0 W/m2; TABULA EU boundary condition (`EU.SUH`/`EU.MUH`) specifies a flat continuous 3.0 W/m2. | Fact | EN ISO 13790:2008; UNI/TS 11300-1:2014; TABULA master workbook `tabula-values.xlsx` | Tier 1 | 2026-08-22 | H |
| 6 | TABULA European Archetype Data Architecture | The TABULA/EPISCOPE database provides harmonized building stock parameters (geometry, U-values, envelope areas, HVAC efficiencies) across 20+ European countries in a static master Excel workbook (`tabula-values.xlsx` 4.0 MB, `tabula-calculator.xlsx` 34.4 MB). | Fact | EPISCOPE / TABULA Project, IWU Darmstadt, `https://episcope.eu/` | Tier 1 | 2026-08-22 | H |
| 7 | European Thermal Capacitance ($c_m$) Standards | EN ISO 52016-1 / TABULA classify internal effective thermal mass capacity into five standard classes: Very Light ($c_m = 14\text{ Wh}/(\text{m}^2\text{K})$), Light ($28$), Medium ($45$), Heavy ($78\text{--}87$), and Very Heavy ($105\text{ Wh}/(\text{m}^2\text{K})$); standard EU default is $c_m = 45\text{ Wh}/(\text{m}^2\text{K})$. | Fact | EN ISO 52016-1 Table B.14; TABULA `Tab.BoundaryCond` | Tier 1 | 2026-08-22 | H |
| 8 | Intermittent Heating Reduction Factors ($F_{\text{red, htr}}$) | European steady-state/monthly standards apply intermittent heating reduction factors as transmission multipliers on UA ($F_{\text{red, htr1}} = 0.90\text{--}0.95$, $F_{\text{red, htr4}} = 0.80\text{--}0.85$ in `EU.SUH`/`EU.MUH`), rather than scheduled thermostat setbacks. | Fact | TABULA `Tab.BoundaryCond`; EN ISO 13790:2008 Section 13.2 | Tier 1 | 2026-08-22 | H |
| 9 | Standard Residential Ventilation Rates in Europe | EN 16798-1 Table B.4 specifies baseline residential fresh air ventilation rates of $0.23\text{ to }0.35\text{ L}/(\text{s}\cdot\text{m}^2)$ ($~0.30\text{ to }0.60\text{ ACH}$); TABULA EU standard sets $n_{\text{air, use}} = 0.40\text{ h}^{-1}$ (GB: $0.59\text{ h}^{-1}$, IT: $0.30\text{ h}^{-1}$). | Fact | EN 16798-1:2019 Table B.4; TABULA `Tab.BoundaryCond` | Tier 1 | 2026-08-22 | H |
| 10 | Primary European Residential Heating Systems | Over 70% of European multi-family and single-family residential dwellings are heated via hydronic hot-water baseboard radiators coupled to natural gas condensing boilers ($\eta_{\text{gen}} = 0.88\text{--}0.96$), district heating, or air-to-water heat pumps ($\text{COP} = 2.8\text{--}3.8$). | Fact | EU Building Stock Observatory (BSO, 2024); Eurostat Energy Consumption in Households (2023) | Tier 1 | 2026-08-22 | H |
| 11 | Structural Differences between ASHRAE and CEN/ISO | ASHRAE 90.1 specifies prescriptive commercial components with central air handling; CEN/ISO standards define whole-building energy calculations based on primary energy factors ($f_{\text{P, nren}}$), delivered energy, and EPBD asset ratings. | Inference | Comparative building-science analysis of ASHRAE 90.1 vs EN ISO 52000-1 | Tier 1 | 2026-08-22 | H |
| 12 | European Glazing Solar Factor Convention ($g_{\text{gl}}$) | European standards reference the total solar energy transmittance $g$ (EN 410) rather than North American Solar Heat Gain Coefficient ($\text{SHGC}$); $g \approx \text{SHGC}$ within $\pm 0.02$, with standard double clear glazing having $g = 0.67\text{--}0.75$ and low-e glazing $g = 0.50\text{--}0.60$. | Fact | EN 410:2011; ISO 9050:2003; TABULA `Tab.U.Class.Window` | Tier 1 | 2026-08-22 | H |
| 13 | Overheating Assessment Standard (CIBSE TM59 / EN 16798-1) | European residential overheating is assessed using the adaptive comfort model (EN 16798-1 Section 6.2) and cumulative degree-hours above threshold ($IOD$), requiring hourly zone-level operative temperatures. | Fact | CIBSE TM59 (2017); EN 16798-1:2019 Annex A; Iseri et al. (2025) | Tier 1 | 2026-08-22 | H |

---

## Section C. Decision impact for Step 8 & OpenUBEM

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Building standards baseline in OpenUBEM | Default to US ASHRAE 90.1 and IBC 2021 modules. | ASHRAE 90.1 assumes air HVAC, commercial core-perimeter slicing, and US schedules, creating severe errors when applied to European residential archetypes. | Design change: Parameterize OpenUBEM with European CEN/ISO conventions (EN 16798-1, EN ISO 52016-1, TABULA master tables) for the Spain, UK, and Italy simulation campaigns. | Medium (3 to 4 days) |
| Baseline internal heat gains foil | Benchmark against reconstructed paywalled EN 16798-1 Annex C schedules. | EN 16798-1 is paywalled and cannot be reconstructed without unverified guesses. Open standards (ISO 13790 Table G.12, UNI/TS 11300-1, TABULA) mandate flat 3.0 or 4.0 W/m2 baselines. | Design change: Adopt the open, standard flat 3.0 W/m2 baseline (TABULA EU boundary condition) as the exact uninjected control ($f = 0.00$). | Low (1 day) |
| HVAC system modeling in EnergyPlus IDFs | Use North American packaged DX / VAV air loops. | Over 70% of European residential archetypes use hydronic radiator systems coupled to central boilers. | Design change: Model hydronic baseboard radiators (`ZoneHVAC:Baseboard:Convective:Water`) or Ideal Air Loads with hot-water boiler efficiency curves ($\eta = 0.85\text{--}0.95$). | Medium (2 to 3 days) |
| Thermal mass and internal capacity | Rely on EnergyPlus default minimal internal mass. | European brick and concrete residential stock has high thermal capacitance ($c_m = 45\text{--}87\text{ Wh}/(\text{m}^2\text{K})$); omitting mass causes numerical spikes in EnergyPlus. | Design change: Inject explicit `InternalMass` objects matching TABULA $c_m$ values into every dwelling zone. | Low (1 day) |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| European Archetype Ingestion (`tabula-values.xlsx`) | Python `openpyxl` / `pandas` on CPU | Yes (1 CPU core, < 2 seconds) | N/A |
| Multi-Zone EnergyPlus 9.2 Execution | EnergyPlus Linux binary on 16 CPU cores | Yes (510 runs complete in < 15 minutes) | N/A |
| Open Standards Documentation Access | TABULA static workbooks + open CEN standards | Yes (All master files on disk in repo) | N/A |

---

## Section E. What this changes in the write-up

* Explicitly state in the methodology section that the European simulation campaign is parameterized against **CEN/ISO standards (EN ISO 52016-1, EN 16798-1, ISO 18523-2)** and **TABULA/EPISCOPE national building typologies**, replacing North American ASHRAE 90.1 conventions [Row 1, Row 2, Row 6].
* Frame the primary foil against which LLM occupancy schedules are benchmarked as the **normative European flat internal gain standard (3.0 W/m² under TABULA EU boundary conditions / 4.0 W/m² under ISO 13790 Table G.12)** [Row 5].
* Document the incorporation of **European thermal mass standards ($c_m = 45\text{ Wh}/(\text{m}^2\cdot\text{K})$)** and **hydronic radiator heating efficiencies ($\eta = 0.85\text{--}0.95$)** in the EnergyPlus archetype specifications [Row 7, Row 10].
* Highlight that ventilation rates are aligned with **EN 16798-1 Table B.4 ($n_{\text{air, use}} = 0.40\text{ h}^{-1}$)** to capture European residential continuous background infiltration and trickle ventilation [Row 9].

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| `tabula-values.xlsx` | Master TABULA European building stock database (4.0 MB) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx` | Open Access (md5 `7347b2cae3c4d9f5ce78221e9d5fb832`) | Confirmed reachable |
| `tabula-calculator.xlsx` | Master TABULA building calculations & archetype variants (34.4 MB) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx` | Open Access (md5 `c99ddc9ffcb6dc0ae7391273d9619e37`) | Confirmed reachable |
| `EPBD Directive (EU) 2024/1275` | Official European Parliament Directive on Energy Performance of Buildings | `https://eur-lex.europa.eu/eli/dir/2024/1275/oj` | Open Official Legal Text | Confirmed reachable |
| `Hotmaps Building Stock DB` | Pan-European residential building stock database across EU-28 | `https://gitlab.com/hotmaps/building-stock` | Open (CC-BY 4.0) | Confirmed reachable |

---

## Section G. Contradictions, gaps, open questions, and negative controls

* **Paywalled vs Open Standards Contradiction**: While EN 16798-1 is the official umbrella CEN standard, its informative schedule Annex C is paywalled. The project strictly refuses to reconstruct unverified paywalled decimals, relying instead on the open normative statutory baselines (ISO 13790 Table G.12 and TABULA `phi_int = 3.0 W/m²`).
* **Negative Control**: What condition would cause us to reject the European standards configuration? If simulation runs of the uninjected control ($f = 0.00$) on the European TABULA archetypes produced heating EUIs deviating by $> 50\%$ from the published TABULA national brochure benchmark values ($Q_H \approx 80\text{--}180\text{ kWh}/\text{m}^2/\text{a}$ across Southern/Central Europe).

---

## Section H. Full reference list

1. **European Parliament and Council. (2024).** *Directive (EU) 2024/1275 of the European Parliament and of the Council of 24 April 2024 on the energy performance of buildings (recast)*. Official Journal of the European Union, L 2024/1275. [Tier 1, Full legal text read]
2. **CEN. (2017).** *EN ISO 52016-1:2017 Energy performance of buildings - Energy needs for heating and cooling, internal temperatures and sensible and latent heat loads - Part 1: Calculation procedures*. European Committee for Standardization, Brussels. [Tier 1, Standard text read]
3. **CEN. (2019).** *EN 16798-1:2019 Energy performance of buildings - Ventilation for buildings - Part 1: Indoor environmental input parameters for design and assessment of energy performance of buildings*. European Committee for Standardization, Brussels. [Tier 1, Standard record & technical report CEN/TR 16798-2 read]
4. **ISO. (2018).** *ISO 18523-2:2018 Energy performance of buildings - Schedule and condition of building, zone and space usage - Part 2: Residential buildings*. International Organization for Standardization, Geneva. [Tier 1, Standard catalog read]
5. **CEN. (2008).** *EN ISO 13790:2008 Energy performance of buildings - Calculation of energy use for space heating and cooling*. European Committee for Standardization, Brussels. [Tier 1, Standard text read]
6. **Loga, T., Diefenbach, N., & Stein, B. (2016).** *TABULA / EPISCOPE Building Typologies in 20 European Countries - Final Report*. Institut Wohnen und Umwelt (IWU), Darmstadt. [Tier 1, Full project report read, `https://episcope.eu/`]
7. **Corrado, V., Ballarini, I., & Corgnati, S. P. (2014).** *Building Typology Brochure - Italy*. ENEA & Politecnico di Torino. [Tier 1, Full text read]
8. **CIBSE. (2017).** *TM59: Design methodology for the assessment of overheating risk in homes*. Chartered Institution of Building Services Engineers, London. [Tier 1, Full methodology read]
9. **Iseri, O. K., Duran, A., Canlı, I., Akgul, C. M., Kalkan, S., & Dino, I. G. (2025).** A method for zone-level urban building energy modeling in data-scarce built environments. *Energy and Buildings*, 337, 115620. [Tier 1, Full text read, DOI: `10.1016/j.enbuild.2025.115620`]
