# V08. Six competitor-positioning axes we cannot characterise, and two dataset catalogue identifiers

Read `00_MASTER_BRIEF_V2.md` first for shared context, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H).

---

## Why we are asking

Our manuscript opens with a competitor-positioning matrix (Table 1) that places three named prior
works against seven axes and shows which cell none of them occupies. The claim the whole paper rests
on is that **no published work combines a time-use-survey-driven, multi-channel, forecast-to-a-future-
year occupancy model inside a single mixed-use building**. That claim is only as strong as the matrix
under it.

Eight cells in the manuscript currently read `n/r`, our marker for "the sources we are permitted to
cite do not state this". Six are in that matrix. We will not fill them by inference, and we will not
soften the claim to avoid them. We want them settled from the primary papers.

The specific problem is that our own prior deep-research report (`dr_L3-10`) characterises these
studies on a **different set of axes** than our matrix uses, so several of our cells are simply not
addressed by it. For example, `dr_L3-10` states that Doma and Ouf's occupancy source is "mobile
positioning data (SafeGraph snapshots)" and separately that the study is not longitudinal, but
neither statement tells us whether the model resolves occupancy **within a day**. Those are different
questions and we have been careful not to conflate them.

Two further cells are ordinary bibliographic work: we cite two statistical products by name but
cannot state their catalogue identifiers, and a reference list that names a dataset without an
identifier is not reproducible.

**A "NOT FOUND" verdict is a completely acceptable answer here**, and for the matrix it is the
answer we will publish. What is not acceptable is a plausible characterisation that turns out not to
be in the paper.

---

## What we need

### Part 1. Doma and Ouf, three axes

The study, as we understand it from `dr_L3-10`: a district-scale mixed-use energy-modelling study
using SafeGraph mobile-positioning snapshots for occupancy, 2019 to 2021, covering office, retail
and residential uses. Please identify the correct paper or papers (2023 and/or 2024, the same author
pair), open them, and answer:

1. **Time-series occupancy.** Does the occupancy input resolve variation **within a day**, that is a
   sub-daily or hourly profile, as opposed to a single occupancy level per building per period?
   Quote the sentence or describe the figure that settles it. We are asking about within-day temporal
   resolution, *not* about whether the study is longitudinal across years. If the paper uses
   different sub-daily resolution for different uses, say so per use.
2. **Calibrated behavioural model.** Is the occupancy model **calibrated against measured data**, and
   if so against what and at what resolution? We distinguish three cases and want to know which
   applies: (a) an occupancy model calibrated against measured occupancy, (b) an energy model
   calibrated against measured energy with occupancy left uncalibrated, (c) no calibration reported.
3. **Stock-scale.** Does the study model a **building stock**, and if so how many buildings? We are
   deliberately treating "district scale" as a distinct and weaker claim than "stock scale", so a
   building count, a floor-area total, or an explicit statement of the modelled extent is what
   settles this. If the paper says "district" without a count, that is itself the finding.

### Part 2. Buttitta and Finn (2020), three axes

The study, as we understand it: an Irish Time Use Survey driven residential occupancy study using
multi-unit residential building archetypes. Please identify it, open it, and answer:

4. **Calibrated behavioural model.** Same three-way distinction as item 2 above. Which applies, and
   against what measured data?
5. **Activity or end-use resolved.** Does the model distinguish **what occupants are doing** (an
   activity or end-use breakdown such as cooking, appliance use, hot water, lighting), or does it
   produce presence or occupancy count only? Name the activities or end uses if it does.
6. **Stock-scale.** Does it model a **stock** of dwellings, and if so how many, or does it model a
   small number of archetype buildings? A dwelling count or an explicit statement of extent settles
   it. "Archetypes" alone does not tell us the scale the archetypes represent.

### Part 3. Two dataset catalogue identifiers

7. **Institut de la statistique du Quebec (ISQ), monthly hotel-occupancy statistics.** We need the
   **exact table or product identifier** for the series of monthly hotel-establishment occupancy
   rates by region, in the form ISQ itself uses for citation, plus a stable URL and the licence.
   Note for context: we have separately established that this product is served through a Power BI
   front end with no download endpoint we could reach. We are asking for the **citable identifier**,
   which is a different question from retrievability, and it is fine if the answer is that ISQ
   publishes it only as a named web table with no catalogue number.
8. **CBRE and Travel Alberta hotel-occupancy reporting for Alberta.** We cite "CBRE National Market
   Report archives" for the 2005 to 2009 span and Alberta hotel occupancy and average-daily-rate
   series generally. We need the **exact report title, publisher and any series or catalogue
   identifier** as they should appear in a reference list, distinguishing clearly between: the CBRE
   product, the Travel Alberta or Government of Alberta product, and the *Alberta Tourism Market
   Monitor* open-data series we already use (source tag `ABMKTMONITOR`, `open.alberta.ca`, Open
   Government Licence). If our 2005 to 2009 span in fact comes from a different product than the one
   we have named, say so plainly. That would be a citation error on our side and we want to know.

---

## Named leads

- **Doma and Ouf**: Concordia University and University of Calgary author affiliations; *Energy and
  Buildings*, *Building and Environment*, *Journal of Building Performance Simulation*, *Sustainable
  Cities and Society*; the SafeGraph Places / Patterns literature; ASHRAE and IBPSA conference
  proceedings 2022 to 2024.
- **Buttitta and Finn**: University College Dublin; *Energy and Buildings*, *Applied Energy*,
  *Energies*; the Irish Time Use Survey (Central Statistics Office Ireland); the IEA EBC Annex 66 and
  Annex 79 occupant-behaviour literature, where this work is frequently cited.
- **ISQ**: `statistique.quebec.ca`, Banque de donnees des statistiques officielles (BDSO), the
  *Tourisme et loisir* subject area, and the *taux d'occupation des etablissements d'hebergement*
  series; also Tourisme Quebec and the *Bulletin touristique*.
- **CBRE and Alberta**: CBRE Hotels *Canadian Hotel Market Report* / *Trends in the Canadian Hotel
  Industry*; STR (Smith Travel Research) Canada, which supplies much of the underlying data;
  Travel Alberta; Government of Alberta *Alberta Tourism Market Monitor* on `open.alberta.ca`;
  Destination Canada research archives.

---

## Rules that apply to this prompt, restated

- **A citation is not evidence until the document has been opened.** For every one of items 1 to 6,
  we need a quotation or a specific figure or table reference from inside the paper, not a
  characterisation drawn from an abstract, a citing paper, or a database record.
- **Verify every DOI** via `https://api.crossref.org/works/<DOI>` and report the verification result.
  Report the year, venue and author list exactly as Crossref returns them.
- **`NOT FOUND` beats an invented answer**, and for items 1 to 6 a `NOT FOUND` is a publishable
  result: those cells stay marked as unreported in our table. Do not resolve an ambiguous cell to
  whichever value seems more likely.
- **Do not propose relaxing any band or threshold of ours**, and do not comment on our failing gates.
  This prompt asks nothing about energy-use intensity.
- **Keep as-modelled and empirical figures strictly separate** if any arise.
- **No em dashes and no en dashes** anywhere in the returned text. Use plain hyphens.
- If you find that we have **mis-identified a study** (wrong paper, wrong year, wrong author pair),
  say so first and loudly, before answering the axes. That is a more important finding than any
  individual cell.

---

## Deliverable

Section A must open with a **table of the eight items**, numbered 1 to 8 as above, each with one of
exactly three verdicts: **SETTLED** (with the value), **NOT FOUND** (with what was searched and why
it is absent), or **OUR ERROR** (we described the source incorrectly, with the correction).

Section B must give, for each SETTLED item, the quotation or figure or table reference that settles
it, with page or section, plus the full citation and its Crossref verification result.

Section G must state explicitly whether any of items 1 to 6 came out in a way that **weakens our
positioning claim**, that is: whether any of the three prior works turns out to occupy an axis we
have marked as unoccupied, and in particular whether any of them turns out to be mixed-use inside a
single building, or to forecast to a future year. If so, say it plainly and first. We would rather
rewrite the claim than defend a wrong one.
