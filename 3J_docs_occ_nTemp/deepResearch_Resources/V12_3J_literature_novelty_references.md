# V12. Literature, novelty check, motivation and reference repair for the 3J manuscript

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H). This prompt unblocks plan item P7.

---

## Why we are asking

The manuscript ("From One Channel to Four", targeted at Building and Environment) has 18 references,
of which 4 are the authors' own work or standards bodies and 5 read literally "not reported" in place
of a report number, edition or table identifier. The companion paper (2J) was rejected once already by
this journal for "insufficient quality", and a thin, partly-unverifiable reference list is exactly what
that verdict looks like. The revised, resubmitted 2J now carries 48 references. Two of 3J's existing
competitor citations (Doma and Ouf, and Buttitta and Finn) already had disputed DOIs resolved in a
separate prompt (`V09`, vetted); do not re-open those two, use the vetted forms.

Table 1 of the manuscript claims an unoccupied cell in the literature: no published study combines a
time-use-survey-driven, multi-channel, calibrated behavioural occupancy model, forecast to a future
year, inside one mixed-use building. That claim currently rests on the same three studies scored in
Table 1, and no search was ever run to look for a fourth. An empty competitor list is evidence of no
search far more often than it is evidence of no competitor (the same lesson `V09` already applied once
to this project); this prompt applies it again, on the full literature question rather than two DOIs.

---

## What we need

**Part A. Try to break Table 1, and name the closest competitor.**

1. Search, 2015 to 2026, for any published study that generates two or more occupancy channels for
   functionally different uses (residential, office, retail, hospitality/hotel, or similar), driven at
   least in part by a time-use survey (HETUS, ATUS, MTUS, a national GSS/time-use-diary source, or
   equivalent), and applies the result to a mixed-use building or a stacked-use energy model.
2. Do the same for the narrower, more dangerous case: any survey-driven occupancy model carried forward
   to a future year (a forecast or scenario horizon) for more than one use.
3. Report explicitly on hotel and retail occupancy specifically, since those are the two channels this
   study adds over its own prior single-channel work. Any published study that models guest-room or
   retail-customer presence for building energy simulation from a population-level source is relevant
   even if single-channel.
4. Search specifically for multi-task or Transformer-based occupancy generators (sequence models with
   more than one output head, jointly trained) applied to building occupancy or activity scheduling, not
   only in energy modelling; report the closest matches even from adjacent domains (mobility, activity
   recognition) if they generate calibrated multi-channel time series.
5. For every candidate found, including partial matches, report the axes it does and does not satisfy,
   using Table 1's eight axes as given below, and give the DOI or stable link for each.
6. State how many searches you ran, in which databases, and with which query strings. A report that
   lists no competitor without listing its queries is not usable, because it cannot be distinguished
   from a search that was never run.
7. If you find a genuine competitor for the unoccupied cell, say so directly in one sentence at the top
   of Section A. A finding that the novelty claim is weaker than stated is a successful result of this
   prompt, not a failure of it. Do not soften it and do not bury it.

**Table 1's eight axes**, for scoring every candidate: time-series occupancy; time-use-survey-driven;
multi-channel (more than one use); calibrated behavioural model (parameters estimated from observed
microdata on the population modelled, not a standard schedule or a single building's sensor/positioning
trace); forecast to a future year; mixed-use single building (uses stacked or co-located inside one
building/plant, not modelled as separate buildings in a district); activity/end-use resolved; stock-scale
(represents a building population, not a named small set of buildings).

**Part B. Motivation literature: why the timing result matters.**

8. Find published sources for why the *timing* of peak demand across co-located uses matters for plant
   sizing, a shared central plant, and district- or grid-level peak demand in a mixed-use or multi-use
   building context, to support one motivation paragraph (2J reviewer request: "why does *when*
   matter"). Diversity/coincidence-factor literature in HVAC central-plant sizing is the primary target;
   grid- or district-level peak-coincidence literature is the secondary target.
9. Find a source for the general claim that occupancy diversity across building uses or zones lowers
   the coincident (whole-building or whole-district) peak relative to the sum of individual peaks, to
   support (not replace) this study's own measured coincidence-factor result.

**Part C. Source the two §1.3 claims currently unsourced.**

10. A source for the claim that a decline in retail/in-person shopping time (attributed in the text to
    e-commerce) is "internationally normal in direction and comparable in magnitude" across the United
    States, the United Kingdom and the European Union, over roughly 2005-2022. Time-use-survey-based
    retail/shopping-time trend studies are the primary target.
11. A source for the persistence of hybrid and work-from-home arrangements pulling down office presence,
    post-2022, distinct from the pure pandemic-collapse literature (which this project already has via
    its own prior work). Prefer sources published 2023-2026 describing a stabilized, not transient,
    post-pandemic hybrid-work level.

**Part D. Re-verify every existing reference, and fill the five "not reported" entries.**

12. For each of the 18 references currently in the manuscript (list given below in Named leads), verify
    via Crossref (or the issuing body's own catalogue for non-DOI sources) that the title, volume, pages
    and year are correct as printed. Report any mismatch.
13. Fill these five specific gaps, each currently printed as "not reported" in the manuscript:
    (a) the exact edition of ASHRAE Guideline 14, *Measurement of Energy, Demand and Water Savings*;
    (b) the exact CBRE Limited / Travel Alberta report or catalogue identifier for the Alberta
        hotel-occupancy and average-daily-rate series used, including the CBRE National Market Report
        archives covering 2005-2009;
    (c) the exact Institut de la statistique du Quebec (ISQ) table or catalogue identifier for the
        monthly Quebec hotel-occupancy statistics used;
    (d) the survey year and table identifier for Natural Resources Canada's Survey of Commercial and
        Institutional Energy Use (SCIEU), used to calibrate activity-driven end-use loads;
    (e) the exact release and version identifier for the U.S. Department of Energy / Pacific Northwest
        National Laboratory Commercial Prototype Building Models, specifically the Tall and SuperTall
        mixed-use prototypes.

---

## Named leads

Existing 18 references (verify all; see Part D): ASHRAE (2019) 90.1-2019; ASHRAE Guideline 14 (edition
unknown); Buttitta and Finn (2020), Energy and Buildings 206, 109577; CBRE/Travel Alberta series
(identifier unknown); Doma and Ouf (2023), Building Simulation 2023 proceedings; Doma, Padsala, Ouf and
Eicker (2024), Applied Energy 375, 124081; Institut de la statistique du Quebec series (identifier
unknown); Iseri and Hachem-Vermette (2026, and two "under review" companion papers); National Research
Council Canada (2017) NECB 2017; Natural Resources Canada (2019) SHEU 2019; Natural Resources Canada
SCIEU (year unknown); Statistics Canada (2021) Census PUMF; Statistics Canada (2022) GSS Time Use PUMF;
U.S. DOE (2024) EnergyPlus 24.2.0; U.S. DOE/PNNL Commercial Prototype Building Models (release unknown);
Widen and Wackelgard (2010), Energy and Buildings 42(5), 706-714.

Databases and venues: Crossref REST API; Scopus and Web of Science; Google Scholar citation-chain walks
both forward and backward from Doma and Ouf (2023, 2024), Buttitta and Finn (2020), and Widen and
Wackelgard (2010); IBPSA proceedings (Building Simulation conference series and national affiliates
eSim, BSO, SimBuild); *Energy and Buildings*, *Building and Environment*, *Applied Energy*, *Journal of
Building Performance Simulation*, *Building Simulation*, *Journal of Building Engineering*; IEA EBC
Annex 66 and Annex 79 occupant-behaviour output; HETUS and American Time Use Survey methodological
literature for building-energy applications; ASHRAE Handbook of Fundamentals (central-plant sizing,
load diversity); NRCan, ISQ and CBRE publication catalogues directly, for Part D items (b)-(d).

---

## Deliverable

Section A of your answer must contain:

1. One sentence up front stating whether Table 1's novelty claim survives the search or not.
2. A competitor table, one row per candidate found in Part A: `study | DOI/link | time-series
   occupancy | time-use-survey-driven | multi-channel | calibrated behavioural | forecast to future
   year | mixed-use single building | activity/end-use resolved | stock-scale | how verified`.
3. A search log: databases queried, exact query strings, result counts per query. Mandatory.
4. A short reference table for Part B and C: `claim | source | what it supports | Tier | link`.
5. A table for Part D: `reference | verified as printed (yes/no/mismatch, state it) | the five gap-fill
   items each with its recovered identifier and source URL`.
6. Target roughly 35-50 vetted candidate references across Parts A-D combined; report the actual count
   reached and why if it falls short.

Rules restated, because every previous round in this project needed them:

- A citation is not evidence until it has been opened. Report what you opened.
- Give URL or DOI for every item. Items without a working link are discarded.
- `NOT FOUND` beats an invented number, an invented volume, or an invented author list. Roughly half of
  the citations returned by external research in this project's earlier rounds turned out to be
  fabricated, and every one was internally consistent and plausible-looking; fabricated citations are
  expected here too and every one will be checked before it is quoted in the manuscript.
- Never propose relaxing a reference band or a gate verdict because this project's model fails it. Out
  of scope for this prompt entirely.
- Keep as-modelled and empirical figures strictly separate.
- No em dashes and no en dashes anywhere in the returned text.

Save the return as `RV12_3J_literature_novelty_references.md` in this same folder.
