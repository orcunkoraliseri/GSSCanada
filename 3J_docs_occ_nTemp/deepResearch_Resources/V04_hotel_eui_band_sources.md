# V04. Hotel as-modelled EUI band for Canadian climate zones 6 and 7

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections required. **Section F is the deliverable.**

## Why we are asking

The gate `S9-EUI-hotel` uses a band with a ceiling of **300 kWh/m2.yr**. Two things about it are now
established, and they point in opposite directions.

**The number itself is properly sourced.** It traces to a local reference table,
`BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv`, which gives DOE
prototype Large Hotel at **302.2 kWh/m2.yr** for climate zone 7 (Duluth, paired with Calgary) and
286.4 for zone 6A (Minneapolis, paired with Montreal). Those are real values in a real file, at the
right climate zones.

**The justification written around it is not.** The report that defines the band,
`Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md`, states that the ceiling is anchored on
ASHRAE 90.1-2016 and 90.1-2019 prototypes, when the figure it actually uses is the **90.1-2004**
baseline row. Its supporting citations do not hold:

* `PNNL-28543`, cited as the 90.1-2019 savings analysis, is in reality "PNNL's Intermediate
  Characterization Summary for the MP-1 Experiment", a nuclear-materials report.
* `PNNL-26343`, cited for the 90.1-2016 rows, does not resolve at all.
* A CanmetENERGY 2020 archetype study is cited with a URL that returns 404, and the study could not be
  located.
* Its Table 2 lists 441 to 521 kWh/m2.yr for Large Hotel under modern codes, which is **higher** than
  the 2004 baseline. That is backwards: a stricter code lowers EUI. The correctly identified PNNL
  90.1-2019 analysis gives Large Hotel about 239 kWh/m2.yr as a US national average, below the 2004
  figure as expected.

So we have a defensible number resting on an indefensible argument, and a band built from a 2004-code
reference being applied to a 2019-code building.

## What we need

1. **Re-source the ceiling properly.** What is the as-modelled all-fuel site EUI of a code-compliant
   Large Hotel and Small Hotel in climate zones 6A and 7, under ASHRAE 90.1-2004, 2016 and 2019, and
   under NECB 2017 or 2020? Cite each figure to a document you opened. Prompt `V01` covers the DOE
   prototype matrix in general; **here we want the hotel rows specifically, plus the Canadian
   equivalents**, and you should say where your numbers agree or disagree with `V01`.

2. **Kill or confirm the 441 to 521 figures.** Establish whether any published source gives Large Hotel
   EUI in that range for CZ6A or CZ7 under 90.1-2016 or 90.1-2019. If none does, say so plainly, since
   those rows are currently in a document we cite.

3. **A Canadian hotel reference.** Is there a NECB-compliant Canadian hotel or lodging archetype with
   published as-modelled energy performance? Try CanmetENERGY BTAP archetypes, NRC, and NRCan. If a
   CanmetENERGY 2020 archetype study exists at all, find it; if it does not, record `NOT FOUND` with
   the search terms, because the same missing source also blocks our office band (prompt `V02`).

4. **Domestic hot water share.** Hotels are DHW-dominated in a way offices are not, and our own hotel
   DHW modelling has been through several corrections. Where a source gives an end-use breakdown for a
   hotel prototype in a cold climate, capture the **DHW share and absolute DHW EUI** separately. State
   the service hot water temperature and the mains temperature assumption if given, since those drive
   the delivered energy.

5. **Full-service against limited-service.** Large Hotel and Small Hotel prototypes differ
   substantially, and so do full-service and limited-service real buildings. Say which subtype each
   figure describes, and which one best matches a hotel occupying part of a mixed-use tower.

6. **The stacked-tower caveat.** Our hotel is a set of floors inside a mixed-use tower, not a standalone
   building. A standalone prototype carries its own envelope, roof, ground contact and service core,
   which a stacked block does not. Say whether any source addresses partial-building or
   floor-block EUI, and in which direction the standalone comparison biases.

7. **Empirical figures, separately labelled.** NRCan hotel benchmarking snapshots, CBECS lodging tables.
   Context only, never band inputs, and clearly separated from as-modelled values.

## Named leads

US DOE Building Energy Codes Program prototype building models, Large Hotel and Small Hotel, per
climate zone and per vintage; PNNL "Energy Savings Analysis: ANSI/ASHRAE/IES Standard 90.1" reports for
2016 and 2019, with their appendices; OSTI; CanmetENERGY BTAP and `btap_batch` archetype result sets;
National Research Council Canada NECB documentation; NRCan Energy Benchmarking data snapshots for
hotels; US EIA CBECS lodging tables; peer-reviewed work on hotel energy modelling in cold climates and
on hotel occupancy elasticity.

**Open documents before citing them.** This prompt exists because a report number was cited without the
document behind it ever being opened, and it turned out to be about nuclear materials.

## Deliverable

Section B must give hotel EUI rows with prototype, subtype, vintage, climate zone, fuel scope and area
basis on every row. Section F must state the as-modelled site EUI range a code-compliant hotel in CZ6A
and CZ7 should show under a **modern** code, with a tolerance and a statement of what counts as a
failure rather than a difference, and with the floor and the ceiling **cited separately**.

Section G must record, explicitly: whether the 441 to 521 figures can be sourced anywhere, and whether
a CanmetENERGY Canadian archetype study exists.

Note that our current ceiling of 300 may well survive this. We are not asking you to move it. We are
asking you to give it an argument that holds, or to tell us it cannot have one.
