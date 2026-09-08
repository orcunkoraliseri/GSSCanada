# T06. UBEM in 2026: the open tools, the validation bar reviewers now apply, and where an engine with dwelling-level division and zero fitted parameters actually stands

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`.

## Why we are asking

Our engine is an open-source Python UBEM: OpenStreetMap ingest, rule-based archetype classification
with provenance on every column, per-building EnergyPlus models, dwelling-level division without a
core zone for European residential blocks, report-only validation gates, no fitted parameters. It is
validated on twelve US city-density cells and applied to four European districts. We think some of
that is unusual. We do not know which parts, because the UBEM tool literature is large and we have not
audited it since 2024. Angles `A1`, `A2`, `A4`, `A5`, `A8` and `A9` all ride on this engine, so its
standing matters to every one of them.

## What we need

### Item 1. The tool landscape

For each open-source or openly documented UBEM tool active in 2024 to 2026, one Section C row plus
columns for: ingest (OSM, CityGML, cadastre, LiDAR); archetype method (rule, ML, LLM); zoning
resolution (building, floor, dwelling, room); engine (EnergyPlus, Modelica, reduced-order, surrogate);
calibration (none, Bayesian, ML); provenance tracking; licence; last release date checked. Include at
least UBEM.io, CityBES, URBANopt, TEASER and AixLib, CEA, umi, CitySim, MUBES, eplusUBEM style
pipelines, the Cambridge and MIT stock models, any national stock model with released code, and
anything released in 2025 or 2026 that we have not named.

### Item 2. The validation bar

1. What do 2024 to 2026 UBEM papers in *Energy and Buildings*, *Applied Energy*, *Building and
   Environment*, *Sustainable Cities and Society* and *Building Simulation* report as validation:
   which metrics, against which measured data, at which aggregation. Give the distribution, not one
   example.
2. Whether the field accepts **zero-fitted-parameter** models that under-predict measured stock EUI by
   a known margin, or expects calibration. Cite the reviews and the editorials.
3. Whether any UBEM paper reports **run-to-run or cross-platform reproducibility** of its results. We
   have measured ours; we want to know if anyone else has.

### Item 3. Dwelling-level modelling

Which works divide residential buildings into dwellings for simulation, by what rule, validated how?
Include automatic floor-plan or layout generation for energy modelling if it reached simulation. Report
whether anyone has shown that dwelling-level division changes stock-scale conclusions relative to
one-zone-per-building or one-zone-per-floor, and by how much. If `NOT FOUND`, that is a result.

### Item 4. Archetype enrichment with language models and open records

Has any UBEM work used an LLM to extract building attributes from **text or tabular open records**
(EPC registers, cadastral descriptions, permit records, listing text), as opposed to images? What
accuracy, against what ground truth, at what scale. Report separately the image-based line of work
(street view, aerial) so we know the boundary; we will not create images but may read literature about
them. This item feeds angle `A7` and `T17`.

### Item 5. European and Canadian district data for validation

For the four countries of our European districts (Spain, France, England, Italy) and for Canada
(Quebec, Ontario): which **measured** building-level or district-level energy datasets are open enough
to validate a UBEM against, at which aggregation, under which licence, opened when. EPC registers,
smart-meter open datasets, utility disclosure programmes, municipal benchmarking. Section F rows.

### Item 6. Where we stand

From items 1 to 5, write a one-paragraph honest placement of our engine: which of its properties are
common, which are rare, which are absent from it that competitors have. Then say what a UBEM
methods paper about the engine alone would be judged as in 2027, and what it would need to add to be
more than a tool description.

## Named leads

The tool papers and repositories named in item 1; IBPSA Building Simulation 2025 and uSim
proceedings; the IEA EBC Annex 70 and Annex 89 outputs; *Energy and Buildings* review articles on UBEM
2023 to 2026; the CityGML and 3DCityDB communities; Ordnance Survey, Catastro, IGN, ISTAT and Statistics
Canada open data portals; utility open-data programmes in Ontario and Quebec.

## Hard constraints specific to this prompt

* Every tool's last release date and licence checked on the day, with URL.
* Item 2.1 is a distribution over many papers. Give the count and the range, with the query used.
* Do not describe our engine back to us in flattering terms. Item 6 is an audit.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences: whether dwelling-level division with provenance and
no fitted parameters is rare or common in released tools; and whether any UBEM paper reports
cross-platform reproducibility.

**Section C** is the tool landscape from item 1.

**Section D** maps our engine's properties against the field.

**Section E** is item 6.

**Section F** is the validation-data table from item 5.

**Section G** carries the dwelling-division finding from item 3, the validation-bar distribution from
item 2, and your negative controls.
