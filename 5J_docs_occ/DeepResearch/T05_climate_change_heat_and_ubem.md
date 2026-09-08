# T05. Climate change, heat and UBEM: future weather files, overheating at stock scale, and whether anyone couples occupancy to heat exposure

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`.

## Why we are asking

Our engine simulates historical or actual-year weather only. It has an unvalidated outdoor
thermal-comfort module and no future-weather path. Angles `A2` and `A4` in the master brief need
future or extreme weather, indoor overheating metrics, and, ideally, occupancy that knows a heat wave
is happening. We need to know what the literature and the data providers already offer, under which
licences, and where the open question is: in the weather files, in the building physics, or in the
occupants.

## What we need

### Item 1. Future and extreme weather for building simulation, as artefacts

For each method or product that produces hourly weather files for future climate or for extreme
events, one Section F row: the method (morphing, dynamical downscaling, stochastic generator, Urban
Weather Generator microclimate adjustment, reanalysis-based extreme-year selection); the climate
model ensemble and scenario it rests on (CMIP6 SSPs, CORDEX, national services); the geographic cover;
the output format (EPW or other); the **licence and whether the files may be redistributed with a
paper**; the URL opened; the date checked. Include at least: the morphing tools descended from
Belcher et al., the Future Weather Generator, WeatherShift, Meteonorm future, the Canadian future
weather files from PCIC, ECCC and NRC, the EU Copernicus C3S building-sector datasets, the ISO 15927
and ASHRAE extreme-year selection methods, and any 2024 to 2026 ML-based weather generator with
released code.

For Canada specifically: which future weather files exist for Montreal and Toronto, from whom, at
which scenarios, and whether the NECB or the National Building Code now references them.

### Item 2. Overheating and indoor heat exposure at district or stock scale

1. Which metrics are used in UBEM-scale overheating studies: degree-hours over a threshold, CIBSE
   TM59 and TM52, EN 16798-1 categories, indoor overheating degree, heat index and WBGT indoors,
   UTCI outdoors. For each, who used it at stock scale, and with what validation.
2. Which UBEM-scale studies simulated indoor temperatures under future or extreme weather for real
   districts, with what occupancy assumption. Report the occupancy assumption in its own column,
   because that is the gap we suspect.
3. Whether any study validated simulated indoor overheating against measured indoor temperatures at
   more than a handful of dwellings. If `NOT FOUND`, say so; that limits every paper in the cluster,
   ours included.

### Item 3. Occupants during heat

1. Empirical evidence on how presence, activity, window opening, shading, fan and air-conditioner use
   change during heat waves, from surveys, sensors or time-use data. Population-scale sources are
   what we need; single-building studies count only as context.
2. Any model in which occupant **presence** during heat is estimated from time-use or mobility data
   and used in exposure or energy simulation. This is the same hinge as `T04` item 4, asked from the
   climate side; the two answers will be compared.
3. Heat-vulnerability indices used by cities and health agencies: which of them include a
   time-at-home or indoor-exposure component, and how it is estimated.

### Item 4. Cooling demand, adaptation and the energy side

What has UBEM-scale work concluded about cooling demand growth, peak load shifts and passive versus
active adaptation under future climate for European and Canadian cities? Report only studies with a
stated climate scenario and a stated occupancy assumption. Note where the conclusions depend on an
assumed air-conditioning uptake that the study did not model.

### Item 5. The engine gap

Given the master brief's description of our engine (section 3, item 3), list what would have to be
added for `A2` or `A4`: a future-weather ingest, an overheating metric, an occupant response rule, a
morphing step. For each, whether an open-source implementation exists that we could adopt, at which
version, under which licence, checked when.

## Named leads

Copernicus C3S Climate Data Store; CORDEX and EURO-CORDEX; PCIC and ECCC future weather files; NRC
Canada's climate-resilient buildings programme; the CIBSE TM59 and TM52 documents; EN 16798-1; the
IEA EBC Annex 80 on resilient cooling; *Building and Environment*, *Energy and Buildings*, *Sustainable
Cities and Society*, *Urban Climate*, *Environmental Research Letters*; the WHO and Health Canada heat
guidance; the Lancet Countdown indicators.

## Hard constraints specific to this prompt

* Every dataset carries its licence text or a `LICENCE NOT FOUND`, and the date checked. We will not
  build on a file we cannot redistribute.
* Every occupancy assumption in item 2 is quoted from the paper, not inferred.
* Do not confirm that a Canadian future weather product exists because the prompt named it. Report
  what is downloadable now.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers in its first two sentences: whether any UBEM-scale overheating study used
occupancy that responds to heat; and whether redistributable future weather files exist for our four
European districts and for Montreal and Toronto.

**Section C** is the overheating-at-scale table from item 2 with the occupancy column.

**Section E** is the engine gap from item 5.

**Section F** is the weather-artefact table from item 1 and the vulnerability-index table from
item 3.3.

**Section G** carries the validation finding from item 2.3 and your negative controls.
