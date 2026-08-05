# V01. DOE-PNNL prototype site EUI by climate zone and code vintage

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections required. **Section F is the deliverable.**

## Why we are asking

Two of our validation bands were built from a local reference table,
`BEM_Setup/Reference-Validation/DOE_non-residential_simulation_results_canadian.csv`. We have opened it
and confirmed what it is: DOE prototype site EUI in kWh/m2.yr, cross-tabulated by climate zone, with
columns labelled `Minneapolis - Montreal (6A)` and `Duluth - Calgary (7)`. It is the **ASHRAE 90.1-2004
baseline** set.

The building we judge against those bands is **90.1-2019 / NECB 2017**. Codes tightened across the
2004, 2010, 2013, 2016 and 2019 cycles, so a 2019-code building should sit below a 2004-derived figure
by construction. If so, our office floor of 100 and our hotel ceiling of 300 are both mismatched to the
model on vintage, and every mechanism we have tested against those gates was testing the wrong thing.

We need the same prototypes, same climate zones, **across vintages**, so the size of that mismatch can
be measured rather than assumed. A prior attempt failed because the PNNL **summary** reports publish
only national averages weighted across all 19 US climate zones, which is useless to us: Canada is
entirely zones 6 and 7, and a national average that includes Miami and Phoenix pulls the number down.

## What we need

1. **The core matrix.** Site EUI, all-fuel, for the DOE/PNNL commercial prototype buildings, at
   **climate zone 6A and climate zone 7**, for ASHRAE **90.1-2004, 2010, 2013, 2016 and 2019**.
   Building types in priority order:
   * Large Office and Medium Office
   * Large Hotel and Small Hotel
   * Stand-Alone Retail and Strip Mall
   * Mid-Rise Apartment and High-Rise Apartment, if published
   Give the published value in its own units and the conversion to kWh/m2.yr, with the arithmetic
   shown. Where a cell of the matrix is not published, leave it blank and say what you searched.

2. **Go to the underlying results, not the summary PDFs.** The per-climate-zone numbers live in the
   prototype model result sets rather than the savings-analysis narrative. Look for the per-prototype,
   per-vintage, per-climate-zone **scorecards** and any downloadable results workbooks. If the
   scorecards give an end-use breakdown, capture **space heating** separately: our office shortfall is
   concentrated there, at about 17 percent of site energy against an expected 35 to 45 percent, and a
   prototype end-use split would let us test that directly.

3. **Anchor against our local file and report any disagreement.** Known values in our 90.1-2004 table,
   in kWh/m2.yr: Large Office 172.6 (6A) and 176.3 (7); Large Hotel 286.4 and 302.2; Small Hotel 230.9
   and 244.8; Stand-Alone Retail 109.8 and 110.7; Strip Mall 147.0 and 153.0. State whether the
   published 90.1-2004 figures you find agree with these. **A disagreement is a finding, not an
   inconvenience**, because our hotel ceiling of 300 comes directly from the 302.2 cell.

4. **The vintage trajectory itself.** Express each later vintage as a percentage change against the
   2004 baseline, per building type and per climate zone. This is the number that tells us how far a
   2004-derived band is displaced from a 2019-code building.

5. **The fuel-switching confound.** Some prototype revisions changed the baseline heating system, not
   only its efficiency. Where a vintage change involves a system or fuel change rather than a
   tightening of the same system, say so, because it breaks the simple monotonic reading of the
   trajectory.

6. **The Canada question.** The US-to-Canada city mapping in our table (Minneapolis for Montreal,
   Duluth for Calgary) is a convention we inherited. Say how good it is. Compare heating and cooling
   degree days for the paired cities, and state whether a US prototype at CZ6A is a fair stand-in for a
   Montreal building or whether it biases in a known direction.

## Named leads

US DOE Building Energy Codes Program prototype building models
(`energycodes.gov/prototype-building-models`) and its per-climate-zone scorecards and results
workbooks; the same programme's commercial prototype development pages; PNNL "Energy Savings Analysis:
ANSI/ASHRAE/IES Standard 90.1" reports for 2010, 2013, 2016 and 2019, **including their appendices**,
which sometimes carry the climate-zone breakdown the body omits; OSTI for the same reports; the
EnergyPlus example and prototype file sets distributed with the models; ASHRAE 90.1 Standard
committee documentation on baseline system changes between editions.

**Verify report numbers by opening the document.** We previously found `PNNL-28543` cited for the
90.1-2019 savings analysis; the actual `PNNL-28543` is a nuclear-materials characterization report, and
`PNNL-26343` does not resolve at all.

## Deliverable

Section B must carry the full matrix, one row per prototype x vintage x climate zone, with the basis
columns filled. Section F must give us, for **office** and for **hotel** separately, the as-modelled
site EUI a 90.1-2019 or NECB 2017 building in CZ6A and CZ7 should be expected to show, with a tolerance
and a statement of what would count as a failure rather than a difference.

If the per-climate-zone data is not publicly retrievable at all, say that in Section A's first sentence
and spend Section F on the closest defensible substitute plus the reason it is a substitute.
