# T10. What can actually be opened and run: data, licences and compute for the shortlisted angles

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, E, F, G, H used. Run in wave 2, after `T02`, for the **three angles it ranked highest**.
If `RT02` is not yet available, answer for `A2`, `A3` and `A9`.

## Why we are asking

Every earlier research round of this project produced angles that were open in the literature and
then stalled on a file we could not download, a licence that forbade redistribution, or a compute
size we did not have. This prompt asks, for the three shortlisted angles only, **what can be opened
today**, from a Canadian university, without commercial budget, and what the paper could therefore
release. It was written after a session in which a landing page returning HTTP 200 was mistaken for
reachable data.

## What we need

### Item 1. Every input each angle needs, as a retrievable artefact

For each of the three angles, list every dataset, weather file, archetype library, standard, code
library and benchmark it would need. One Section F row each with: what it is; who publishes it; the
exact URL you opened; whether the file itself downloaded or only a landing page loaded; format and
size; licence text or `LICENCE NOT FOUND`; whether derived outputs may be published; whether the raw
file may be redistributed; eligibility for a Canadian-based researcher; date checked.

For Canada specifically, if `A8` or `A9` is shortlisted: building footprints and heights for Montreal
and Toronto (municipal open data, Microsoft and Google footprints, StatCan), assessment rolls, the
NECB archetype sources, Ontario and Quebec energy disclosure data, Hydro-Québec and IESO load data,
Canadian future and extreme weather files, and the standards that define a habitable indoor band.

For Europe, if `A2` or `A4` is shortlisted: future weather for Madrid, Lyon, London and Bologna;
demographic projections at the resolution of a district (Eurostat EUROPOP and national institutes);
EPC registers and their bulk-download terms; measured indoor-temperature datasets for validation.

### Item 2. What we could release

For each angle: given the licences in item 1, which of the paper's outputs could ship (code,
synthetic populations, simulated results per building, weather files, archetype tables, the model),
and which could not. Compare against the data-availability policies of *Energy and Buildings*,
*Building and Environment* and *Applied Energy*, quoted with the date checked.

### Item 3. Compute

For each angle, estimate the compute shape: number of EnergyPlus runs, model training hours, agent
inference calls. State the assumption behind each number as `INFERENCE`. Then say whether it fits one
SLURM node with a seven-day walltime and an 80 GB GPU, or needs a multi-node reservation we do not
have. If an angle needs API calls to a hosted model, say so plainly; that angle is then infeasible as
designed.

### Item 4. Open-source components we would adopt

For every engine addition the shortlisted angles need (future-weather morphing, overheating metrics,
conformal prediction, agent frameworks, population synthesis, outage simulation in EnergyPlus), the
open-source library that does it, its version and licence, its last release date, and whether it is
maintained. `NOT FOUND` where none exists, because then it is our work.

### Item 5. The blocker, per angle

Name the single hardest dependency for each angle: the one that, if it fails, stops the paper. Say
how long it takes to find out (a download, an email, a data agreement, an eligibility ruling) and what
the fallback is. Never propose paying for the fallback.

## Named leads

Copernicus Climate Data Store; PCIC, ECCC and NRC Canada climate data; Statistics Canada, Ville de
Montréal and City of Toronto open data portals; Ontario Energy and Water Reporting and Benchmarking;
Hydro-Québec open data; IESO data directory; Eurostat and national demographic projections; the
Ordnance Survey, Catastro, IGN and ISTAT portals; EPC open registers for England, Comunidad de Madrid,
ADEME and Emilia-Romagna; PyPI and GitHub for library versions; the journals' author-guideline pages.

## Hard constraints specific to this prompt

* **List every URL you actually opened, separated from URLs you named but did not open.** This is the
  first mandatory negative control.
* A landing page is not a download. Say which it was.
* Do not reconstruct a table from a paywalled or login-gated source.
* Do not recommend buying data, weather files or cloud compute.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first sentence which of the three angles has every input reachable today,
and in its second which one has a blocker with no free fallback.

**Section B** is the compute table from item 3 and the release table from item 2.

**Section E** is the blocker analysis from item 5.

**Section F** is the artefact table from item 1 and the component table from item 4.

**Section G** carries the opened-versus-named URL lists and your other negative controls.
