# T14. The scenario axis: future population, future weather and an evolving stock, combined, for districts to 2050

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Reads `T05` for the weather side; this prompt covers
the demographic and stock sides and the combination.

## Why we are asking

Our second paper forecast the Canadian residential load shape to 2030 by varying occupancy alone,
holding weather and stock frozen, and its conclusion names future weather and an evolving stock as the
next step. Our fourth paper had a forecasting design researched for it (shift-share decomposition of
observed change plus counterfactuals conditioned on official demographic and telework projections)
and ruled it out of scope. Angle `A4` picks that up: **occupancy, weather and stock all moving**, for
real districts, with the occupancy side demographically resolved. We need to know who has combined
the three, how, and what they found about which driver dominates.

## What we need

### Item 1. Studies that move more than one driver

Every 2018 to 2026 district-, city- or stock-scale energy study that projects to 2030 or beyond and
varies at least two of: climate, population and household structure, occupant behaviour or telework,
building stock (new construction, demolition, retrofit). For each, one Section C row plus columns
for which drivers moved, how each was projected, the horizon, the scenarios, and **which driver the
authors found dominant for demand and for peak**. Say in Section A how many moved all three and
whether any resolved occupancy demographically rather than by a fixed schedule.

### Item 2. Demographic and behavioural projections as inputs

1. Official demographic projections usable at district scale, or downscalable: Eurostat EUROPOP,
   national institutes for Spain, France, England, Italy, Statistics Canada and provincial agencies;
   what they project (age, household size and type, migration), at what geography, to what year,
   under what licence. Section F rows.
2. Telework and time-allocation projections: which official or peer-reviewed sources project the share
   of work done from home, hours worked, retirement age, school hours to 2030 or 2050, and how
   energy studies have used them.
3. Methods for turning a demographic projection into a synthetic population of households at district
   scale (spatial microsimulation, iterative proportional fitting, generative population synthesis,
   dynamic microsimulation such as LIAM2 or MicSim), with the study that used each for energy.

### Item 3. Stock evolution

How do UBEM and stock models represent new construction, demolition, renovation rates and standards to
2050? Cite the models with released methods (EU Building Stock Observatory scenarios, national
renovation-wave models, Canadian stock models used by NRCan or CMHC, city models). Report the
renovation-rate assumptions and their source, because that number usually decides the result.

### Item 4. The attribution question

When several drivers move, how do studies attribute the change in demand and peak to each? Report the
decomposition methods used (one-at-a-time freezing, Shapley or Sobol decomposition, shift-share,
Kaya-style identities, scenario differencing) and their known weaknesses when drivers interact, for
example heat waves and daytime presence. Say which method our frozen-frame campaign design (master
brief section 8) already implements and what it cannot attribute.

### Item 5. Forecast credibility with reviewers

Which projections in item 1 were later checked against what happened, and how far off were they? Is
there any published retrospective on building-stock or UBEM projections? If `NOT FOUND`, say so. Then
say what a reviewer in 2027 will require before accepting a 2050 district projection: uncertainty
bands, scenario spread, official-source conditioning, a hindcast.

### Item 6. Where the combination is open

State in one sentence what no study in item 1 did that `A4` would do, and then name the nearest study
that almost did it. If the sentence does not survive, say so in Section A.

## Named leads

Eurostat EUROPOP2023 and national projection pages; Statistics Canada population projections and
household projections; the EU Building Stock Observatory; the IEA and IPCC buildings-sector scenario
literature; *Energy and Buildings*, *Applied Energy*, *Energy Policy*, *Energy*, *Environmental
Research Letters*, *Building Simulation*; the International Microsimulation Association journal.

## Hard constraints specific to this prompt

* Every projection carries its issuing body, base year, horizon and licence, checked on the day.
* Every dominance claim in item 1 is the authors' own conclusion, quoted, not your reading of a figure.
* Do not present our second paper's forecast back to us.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first two sentences how many studies moved climate, population and stock
together at district scale, and whether any resolved occupancy demographically.

**Section C** is the multi-driver table from item 1.

**Section F** is the projection-source table from item 2.1 and the stock-model table from item 3.

**Section E** is items 4, 5 and 6.

**Section G** carries the renovation-rate assumptions collected in item 3, the retrospective finding
from item 5, and your negative controls.
