# Step 8D — Office EUI benchmark deep-research prompts

**Purpose.** The two-channel Step-8 validation scorecard (`3rdJ_08_simulation_2split_val.py`) has a §4 *physical-plausibility* gate that benchmarks each simulated cell's annual EUI (kWh/m²·yr) against authoritative reference bands. The **residential** channel already has a numeric band source — the 2J deep-research doc *"Canadian Residential Energy-Use Intensity by Dwelling Type (NRCan) — Plausibility Bands"* (in `2J_docs_occ_nTemp/writing/deepResearch/`), which our 4 residential archetypes (SingleD / OtherDwelling / MidRise / HighRise) reuse directly.

The **office** channel has **no numeric benchmark anywhere in the codebase** — `..._val.md §4.2` is only qualitative ("within NRCan SCIEU commercial bands / NECB reference-schedule implied EUI"). These prompts source that gap so §4.2 can become a real numeric gate.

**What the office campaign is (context for the researcher).** 3 office schedule archetypes (Knowledge / Public / Sales) × 2 envelopes (Tall, SuperTall — DOE/PNNL commercial *prototype* high-rise office IDFs, transitioned v22.1→v24.2) × 6 Canadian climate-zone cities (Toronto 5A, Kelowna 5B, Vancouver 5C, Montréal 6A, Calgary 6B, Winnipeg 7A) × 7 scenarios = 252 EnergyPlus runs. EUI denominator in our results = **conditioned floor area** from `eplusout.sql` (`calculate_eui`).

**The two prompts (run each as a separate deep-research pass):**
- `01_office_EUI_empirical_SCIEU_CEUD.md` — the *measured Canadian stock* band (NRCan SCIEU + CEUD commercial/office tables), regional where available.
- `02_office_EUI_reference_NECB_PNNL.md` — the *as-modelled code/prototype* band (NECB 2020 / ASHRAE 90.1 large-office + DOE/PNNL Tall & SuperTall prototype published EUIs).

Together they bracket the §4.2 office gate: empirical = "does our number resemble real Canadian offices?"; prototype = "does our number resemble the reference model these exact IDFs derive from?"

**Deliverable per prompt:** a markdown doc mirroring the residential one — verbatim source-table values, both GJ/m² and kWh/m² (1 GJ = 277.78 kWh), site (secondary) not source energy, explicit floor-area basis, regional/CZ bands, every unavailable cell marked `NOT FOUND`, working source URLs, and a final **recommended numeric plausibility band (central value + outer range, kWh/m²·yr)** ready to encode as a gate threshold. Save outputs back into this folder.
