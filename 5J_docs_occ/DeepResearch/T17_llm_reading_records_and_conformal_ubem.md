# T17. Language models reading building records with abstention, and conformal trust bounds on a UBEM: what exists, what was measured, and what the records actually contain

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Reads `T06` item 4 for the enrichment landscape.

## Why we are asking

Angle `A7` and one fellowship programme in the master brief (section 5) turn on two ideas that are
new to our work: a language model that reads renovation state or building attributes out of permit
archives, energy-certificate free text and cadastral records, **emits a prediction set and abstains
when the evidence is thin**; and **conformal prediction** attached to a UBEM so that a building never
metered carries a coverage guarantee by archetype. Both come from machine learning and both would be
applied to a stock model. We need to know how far each has already gone in the built environment, and
whether the records that would feed the first idea say what we hope they say.

## What we need

### Item 1. LLM extraction from building records

Every 2022 to 2026 work that applies a language model to permit records, energy-performance-certificate
text, cadastral or property descriptions, inspection reports or listing text to infer building
attributes (construction year, renovation state, envelope, heating system, use). One Section C row
each plus: language and country of the records; model and whether open-weight; supervised or
zero-shot; accuracy against a labelled ground truth, with the size of that ground truth; whether the
extraction fed a stock or energy model; whether abstention or uncertainty was reported. Say in
Section A how many reported abstention or calibrated uncertainty at all.

### Item 2. Selective prediction and prediction sets with LLMs

The current state of selective prediction, prediction sets and conformal methods **for language-model
outputs** on extraction and classification tasks: the methods (conformal prediction over label sets,
conformal factuality, self-consistency and verbalised confidence as scores, abstention thresholds),
the benchmarks they were tested on, the coverage they achieved, and the known failure modes
(calibration collapse under distribution shift, exchangeability violations). Cite the methodological
papers and the 2025 to 2026 surveys. Then say which methods work with an open-weight model on one GPU.

### Item 3. Conformal prediction in building energy and UBEM

Any 2020 to 2026 work that applied conformal prediction, or another distribution-free coverage
method, to building energy prediction, load forecasting or UBEM outputs. Per work: what was covered,
at what level, marginal or group-conditional, validated on what data. Report whether anyone has
attached coverage bounds to a **physics-based** UBEM's per-building outputs where meters exist for a
subset only. If `NOT FOUND`, that is the gap.

### Item 4. What the records contain

For Sweden, Spain, France, England, Italy and Canada (Quebec, Ontario): what building permit archives
and energy-certificate registers exist, whether they contain free text, whether renovation measures
are recorded as fields or only in text, bulk-access route and licence, languages, and any published
study on their completeness. Section F rows. This decides whether the first idea has data at all
outside the fellowship's host country.

### Item 5. Renovation state as a target

How do stock models currently estimate which buildings have been renovated and when: registers,
EPC before-and-after pairs, remote sensing, survey, assumption? What national renovation-rate
estimates exist for the six countries and how were they produced? Who has shown that mis-estimating
renovation state changes retrofit-priority rankings, and by how much?

### Item 6. The honest placement

State in one paragraph whether an LLM-with-abstention reader feeding a conformally bounded UBEM is
an open combination, a combination whose parts are each done, or a combination already published.
Name the nearest work for each part.

## Named leads

arXiv `cs.CL`, `cs.LG`, `stat.ML`; NeurIPS, ICML, ICLR, ACL, EMNLP for conformal and selective
prediction; *Automation in Construction*, *Advanced Engineering Informatics*, *Energy and Buildings*,
*Applied Energy*, *Building and Environment*; Boverket, the Swedish energy-declaration register,
Catastro and the Comunidad de Madrid certificate registry, ADEME DPE and the French permit database,
the English EPC open register and planning portals, the Emilia-Romagna certificate register, the Ville
de Montréal permit open data and Ontario municipal permit portals.

## Hard constraints specific to this prompt

* Every accuracy and coverage figure carries its test-set size and its source table.
* Every register carries its access route and licence, checked on the day.
* Do not name individuals connected to the fellowship programme or its host groups.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences how many building-record extraction works reported
abstention or calibrated uncertainty, and whether conformal bounds have been attached to a
physics-based UBEM.

**Section C** is the extraction table from item 1 and the conformal-in-energy table from item 3.

**Section F** is the register table from item 4.

**Section E** is items 2, 5 and 6.

**Section G** carries your negative controls.
