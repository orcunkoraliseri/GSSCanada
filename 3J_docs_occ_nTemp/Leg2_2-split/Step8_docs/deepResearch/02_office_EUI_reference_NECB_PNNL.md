# Deep-research prompt — OFFICE reference/as-modelled EUI: NECB 2020 + ASHRAE 90.1 large-office + DOE/PNNL Tall & SuperTall prototype expected EUIs

## Role
You are a building-energy-code and prototype-model research analyst. Produce a rigorous, citation-anchored reference note on the **expected (as-modelled) energy-use intensity of large / high-rise office buildings** under Canadian and reference North-American energy codes, formatted so a simulation team can adopt the numbers as a *code-reference* plausibility band.

## Objective
Deliver expected office **EUI (kWh/m²·yr and GJ/m²·yr)** from **code-compliant reference models** — NECB 2020, ASHRAE 90.1 (recent cycles), and the **DOE/PNNL commercial prototype building models** — for large/high-rise office buildings in cold Canadian climate zones. This is the "as-modelled reference" half of the office plausibility gate; the empirical (SCIEU/CEUD) half is covered by the companion prompt `01_...`.

## Context (why this exact source matters)
Our EnergyPlus office runs use the **DOE/PNNL commercial prototype "Tall" and "SuperTall" office building IDFs** (transitioned v22.1 → v24.2), simulated across six Canadian climate-zone cities: Toronto (5A), Kelowna (5B), Vancouver (5C), Montréal (6A), Calgary (6B), Winnipeg (7A) — i.e. NECB/ASHRAE cold zones ~6–7. Because these IDFs *are* the PNNL prototypes, the **published expected EUI of those very prototypes** is the strongest, most direct reference band. Simulated EUI = annual **site (secondary) energy ÷ conditioned floor area**.

## Required findings (answer each explicitly; mark any unavailable cell `NOT FOUND`)
1. **DOE/PNNL commercial prototype office models — PRIMARY.** For the large-office / high-rise-office prototypes (and specifically any "Tall" and "Super Tall" / high-rise office prototypes in the ASHRAE 90.1 prototype set), report the **published annual EUI** (site and, if given, source) in kWh/m²·yr and kBtu/ft²·yr, for the coldest available US climate-zone analogues to Canadian **CZ 6 and CZ 7** (e.g. 6A/6B/7). Give the exact prototype name, 90.1 code edition/year, climate zone, and the results-table/URL. Convert kBtu/ft² → kWh/m² (1 kBtu/ft² = 3.15459 kWh/m²) and show the arithmetic.
2. **NECB 2020 reference-building office EUI.** Find published or NRCan-reported expected EUI for NECB-2020-compliant office buildings in Canadian climate zones 6/7 (or the NECB reference-building performance path implied intensity). Give table/figure, zone, and value in kWh/m²·yr.
3. **ASHRAE 90.1 large-office EUI trajectory.** Report the large-office prototype whole-building EUI under recent 90.1 editions (e.g. 90.1-2013 / -2016 / -2019) for cold zones, to bracket how code vintage moves the number.
4. **End-use breakdown.** For the reference large office, give the approximate end-use split (heating / cooling / interior lights / interior equipment / fans / DHW) as % of site energy — so we can sanity-check that our occupancy-coupled lights+equipment share is plausible.
5. **Electricity vs gas.** State the fuel split assumed in the reference model (electric lights/equipment/cooling/fans; heating fuel gas or electric) for cold Canadian zones, and the resulting electricity-only EUI if published.
6. **Floor-area & energy basis.** Confirm each source's floor-area basis (gross vs conditioned) and site vs source energy, so the band reconciles with a **conditioned-area, site-energy** simulation result.
7. **Recommended reference band.** Synthesize a single recommended **as-modelled office EUI band in kWh/m²·yr** (central value + outer range) for CZ 6 and CZ 7, on a conditioned-floor-area / site-energy basis, ready to encode as a numeric gate.

## Output format (mirror the residential note exactly)
Sections in this order: **TL;DR** (bold band numbers) → **Key Findings** → **Details** (numbered tables: PNNL prototype EUIs by zone/code, NECB 2020 reference, 90.1 vintage trajectory, end-use split; show all unit conversions) → **Interpretation for simulation plausibility bands** → **Recommendations** → **Caveats** → **Sources** (exact document/table titles, code editions, and working URLs — e.g. energycodes.gov commercial prototype results, ASHRAE 90.1, NRCan NECB pages).

## Quality rules
- Cite only **named documents/tables/prototype result sets** with verbatim values; never invent a number.
- Give EUI in **kWh/m²·yr** for every value (plus the native unit + conversion shown: 1 kBtu/ft² = 3.15459 kWh/m²; 1 GJ = 277.78 kWh).
- Keep **site (secondary)** distinct from source/primary energy.
- Mark every unavailable cell `NOT FOUND`.
- State floor-area basis and code vintage on every table.
- The final recommended band must be a **directly encodable numeric threshold** (central kWh/m²·yr + outer range) for CZ 6 and CZ 7.

## Deliverable
A single markdown file named `Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL prototypes) — As-Modelled Bands.md`, saved in this `deepResearch/` folder.
