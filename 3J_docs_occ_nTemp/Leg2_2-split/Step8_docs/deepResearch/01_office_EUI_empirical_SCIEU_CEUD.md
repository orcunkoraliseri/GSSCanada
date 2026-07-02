# Deep-research prompt — Canadian OFFICE energy-use intensity (empirical stock): NRCan SCIEU + CEUD plausibility bands

## Role
You are an energy-data research analyst. Produce a rigorous, citation-anchored reference note on the **energy-use intensity (EUI) of office buildings in Canada**, using authoritative NRCan sources, formatted so a building-energy-simulation team can adopt the numbers directly as physical-plausibility bands.

## Objective
Deliver numeric EUI plausibility bands (kWh/m²·yr, and GJ/m²·yr) for **office / commercial-office buildings in Canada**, ideally split by building size (large / high-rise office), by region/province or climate zone, and by energy basis (total all-fuels site energy **and** electricity-only). These bands will be used to gate EnergyPlus simulation results for large high-rise Canadian office prototypes.

## Context (what the bands must fit)
The simulation campaign models **large high-rise office prototypes** (DOE/PNNL "Tall" and "SuperTall" commercial office building models) across six Canadian climate-zone cities: Toronto (ASHRAE 5A / ON), Kelowna (5B / BC), Vancouver (5C / BC), Montréal (6A / QC), Calgary (6B / AB), Winnipeg (7A / MB). Simulated EUI is annual **site (secondary) energy ÷ conditioned floor area**. We therefore need **site-energy** (not source/primary) intensities, and a clear statement of each source's **floor-area basis** (gross vs conditioned/heated) so we can reconcile denominators.

## Required findings (answer each explicitly; mark any unavailable cell `NOT FOUND`)
1. **NRCan SCIEU (Survey of Commercial and Institutional Energy Use) — PRIMARY.** Find the most recent SCIEU cycle (state the reference year). Report office (or "office" activity-type) **energy intensity per floor area**:
   - total all-fuels intensity (GJ/m² and kWh/m²),
   - electricity-only intensity (GJ/m² and kWh/m²),
   - by region/province where SCIEU publishes it (Atlantic / Québec / Ontario / Prairies / Alberta / BC),
   - by building size class if available (SCIEU sometimes bins by floor-area size — report the large-building bin).
   Give the exact SCIEU **table number and title**, the reference year, and the verbatim anchor values.
2. **NRCan CEUD (Comprehensive Energy Use Database), Commercial/Institutional sector — CROSS-CHECK.** Report the office building-type EUI (secondary energy PJ, floor space M m², implied GJ/m² and kWh/m²) for the latest reference year, with exact table number/title and URL. Note its floor-area basis (typically total/gross floor space).
3. **Energy basis & floor-area basis** for each source: confirm site (secondary) vs source/primary; confirm gross vs conditioned/heated floor area. Flag where SCIEU and CEUD differ so the bands aren't naively mixed.
4. **Electricity share.** Report the typical electricity fraction of office site energy in Canada (helps interpret a model where lights+equipment+HVAC-fans are electric and heating may be gas).
5. **Regional spread.** Give the min–max office intensity across regions/provinces (total and electricity-only), noting Québec (electric heat) vs Alberta/Ontario (gas heat) drivers, mirroring how the residential note handled this.
6. **Data-quality flags.** Report NRCan quality flags (A/M/U or equivalent) on any office cells used, and treat suppressed/caution cells as soft.
7. **Recommended plausibility band.** Synthesize a single recommended office **EUI band in kWh/m²·yr**: a central value and an outer (regional) range for (a) total all-fuels and (b) electricity-only, explicitly stated on a **conditioned-floor-area basis** if possible (or state the offset needed to convert from gross).

## Output format (mirror the residential note exactly)
Sections in this order: **TL;DR** (bold band numbers) → **Key Findings** → **Details** (numbered tables: SCIEU primary, CEUD cross-check, regional ranges; show the GJ/m² → kWh/m² conversion arithmetic using 1 GJ = 277.78 kWh) → **Interpretation for simulation plausibility bands** → **Recommendations** → **Caveats** → **Sources** (exact table numbers, titles, catalogue, reference year, and working URLs — SCIEU data-table index, each cited table's page, CEUD commercial table pages).

## Quality rules
- Cite only **named NRCan tables** with verbatim values; never invent a number.
- Give **both** GJ/m² and kWh/m² for every intensity, with the conversion shown.
- Keep **site (secondary) energy** distinct from source/primary; do not benchmark against ENERGY STAR *source*-EUI.
- Mark every unavailable cell `NOT FOUND` (do not silently drop it).
- State the floor-area basis on every table.
- The final recommended band must be a **directly encodable numeric threshold** (central kWh/m²·yr + outer range), suitable for a ±band pass/fail gate.

## Deliverable
A single markdown file named `Canadian Office Energy-Use Intensity (NRCan SCIEU_CEUD) — Plausibility Bands.md`, saved in this `deepResearch/` folder.
