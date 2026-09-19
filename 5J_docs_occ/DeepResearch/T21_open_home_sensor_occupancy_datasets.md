# T21. Open datasets with measured occupancy in homes: the registry

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

A small number of research projects instrumented real homes and published the data: motion, door,
CO2, room presence, sometimes a ground-truth occupancy log kept by the residents. These are the only
places where residential presence was **measured** rather than recalled in a diary. We need one
registry of them, with what each actually contains, so we can judge whether any is large enough,
long enough and diverse enough to score a time-use generator against (`R3`), and which country each
could validate.

## What we need

### Item 1. The registry

One data-source card (brief section 9) per dataset, plus: number of homes; household composition
known or not; duration per home; sensors; whether a **ground-truth presence label** exists and how it
was collected (resident log, camera, annotation, inferred); room-level or dwelling-level; resolution.
Search at least these, and add any others you find:

ECO (Switzerland), REFIT (UK), IDEAL (UK), SPHERE (UK), UK-DALE (UK), HUE (British Columbia), Smart*
and UMass Smart Home (US), CASAS (US), ARAS (Turkey), Pecan Street Dataport (US), the ASHRAE Global
Occupant Behavior Database, the IEA EBC Annex 79 occupant datasets, LBNL occupancy datasets, the
Building Data Genome projects (say whether any residential), any Canadian instrumented-home dataset
(for example university test houses or utility pilots), and any European Horizon project that
released household sensor data.

### Item 2. Fitness to score a population

For each dataset with ground-truth presence: could it score a **population** of generated schedules
(many homes, many days, known demographics), or only one household? Give the count of home-days with
presence labels. Rank nothing; state the counts.

### Item 3. Studies that already did it

Works that compared measured home presence from any of these datasets with schedules from a time-use
survey, a standard schedule (ASHRAE, NECB, ISO 17772, SIA 2024) or a stochastic occupancy model.
Section C rows with the metric and the size of the difference.

### Item 4. Coverage gaps

Which countries have no open instrumented-home dataset with presence labels? State plainly whether
Canada, Spain and Italy have one.

## Named leads

*Scientific Data*, *Data in Brief*, *Energy and Buildings*; BuildSys, e-Energy, UbiComp proceedings;
UK Data Service; Edinburgh DataShare; Zenodo; Dryad; Figshare; NREL OEDI; Pecan Street Dataport
access pages; ASHRAE OB database portal.

## Hard constraints specific to this prompt

* A dataset without a ground-truth or derivable presence signal is listed, marked `NO PRESENCE
  SIGNAL`, and not described as occupancy data.
* Home counts and durations are taken from the dataset's own documentation, quoted, with the date.
* Access for a Canadian university researcher is quoted per dataset; academic-only and
  non-commercial clauses are quoted, not summarised.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: how many open datasets carry measured residential presence for more than
twenty homes, and which countries they cover.

**Section F** is the registry (item 1) with the home-day counts (item 2). **Section C** is item 3.
**Section D** assesses "a multi-dataset presence benchmark for time-use occupancy generators" as a
form of `A14`. **Section G** carries item 4 and your negative controls.
