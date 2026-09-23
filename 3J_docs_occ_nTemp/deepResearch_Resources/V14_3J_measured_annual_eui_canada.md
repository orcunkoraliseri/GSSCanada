# V14. Measured annual energy intensity for Canadian buildings, by use type

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H). This prompt unblocks plan item V1.

---

## Why we are asking

Three of the manuscript's four channel-level energy-use-intensity (EUI) gates fail against reference
bands that were built for single-use building stock, not for a mixed-use, stacked tower: the office
channel fails hardest (all 56 campaign cells below a 100 kWh/m2.yr floor, and the uninjected, no-occupancy
control also fails at 85.45), the hotel channel splits into two prototype clusters straddling its
300 kWh/m2.yr ceiling, and the retail channel's median sits 5.47% below its 80 kWh/m2.yr floor. The
manuscript's position is that these are findings about band applicability to mixed-use towers, not
model error, and it never widens a band to pass. That position is more defensible if the same channels
are also checked, separately, against real measured Canadian buildings, independent of the as-modelled
reference bands already in the gate set. This is track V1 of the author-approved validation plan: reading
only, no simulation, and the frozen gate verdicts are never re-scored by anything this prompt returns.

---

## What we need

For each of the four channels (residential, office, retail, hotel/hospitality), and separately for
mixed-use buildings as a category if it is reported at all, find publicly documented **measured**
(metered or billed, not simulated or code-modelled) annual energy-use-intensity data for Canadian
buildings, split by use type wherever the source allows it.

1. **Montreal's large-building energy and water disclosure open data** (the municipal by-law requiring
   large buildings to report annual energy and water use): confirm it exists, give the exact open-data
   portal URL, the years covered, whether it reports by building-use category (and which categories),
   the floor-area basis used (state whether it is gross floor area, and whether any conditioned-area
   adjustment is possible), and whether mixed-use buildings are reported as a single record or
   disaggregated by use inside the building.
2. **Toronto's and Calgary's building energy/water benchmarking open data** (municipal disclosure or
   benchmarking programs, if either or both cities operate one): same questions as item 1 for each city
   found to have one; if a city has no such program, say so.
3. **ENERGY STAR Portfolio Manager Canadian medians**: whether Canadian building median EUI figures by
   property type are published (not the US medians), where, for which property types, on what area
   basis, and for what most recent year.
4. **Natural Resources Canada survey tables**, specifically the Survey of Commercial and Institutional
   Energy Use (SCIEU) and any published summary tables giving EUI by building activity type (office,
   retail, accommodation/hotel, multi-unit residential), the most recent year available, and the area
   basis. Cross-check this against the SCIEU identifier this project needs for its own reference list
   (a separate prompt, `V12`, is also chasing the exact SCIEU year/table identifier; if you find it here,
   report it, but do not treat that as this prompt's main deliverable).
5. Any other Canadian source with measured, metered annual EUI split by use type: CMHC data on
   multi-unit residential energy use; a province-level or utility-level open-data energy-disclosure
   program beyond Montreal/Toronto/Calgary; a published Canadian building-stock energy-benchmarking
   study (peer-reviewed or a national-lab/consultancy report) that reports median or distributional EUI
   by use type for office, retail and hotel/accommodation buildings specifically.
6. For hotel/accommodation specifically: search for a Canadian- or cold-climate-specific measured EUI
   benchmark distinct from the DOE/PNNL prototype-derived band already in the manuscript (the manuscript
   currently anchors its 300 kWh/m2.yr hotel ceiling on a US DOE/PNNL Large Hotel prototype value, not a
   measured Canadian figure); report anything that would let this study compare its measured hotel
   simulation output against an actually metered Canadian or cold-climate hotel population, not another
   prototype model.
7. For each dataset or table found, report explicitly: the floor-area basis (gross floor area, rentable
   area, conditioned area; state which, and flag if the source does not say); whether the figure is
   all-fuel site energy or electricity-only, or if it also reports source/primary energy; the building-
   use category definitions used (do they match, roughly, residential/office/retail/hotel, or do they
   split differently, for example combining retail with other commercial); the most recent year of data;
   sample size if reported (number of buildings behind a median); and how the data is accessed (open
   download, API, registration, or restricted).

---

## Named leads

Ville de Montreal open-data portal (donnees.montreal.ca) for the large-building energy and water
disclosure by-law; City of Toronto Better Buildings / building energy and water benchmarking open data;
City of Calgary building benchmarking or energy-disclosure open data, if it exists (check explicitly;
Calgary is one of this study's two simulated cities); ENERGY STAR Portfolio Manager Canada (US EPA/NRCan
joint program) technical documentation and published Canadian benchmark reports; Natural Resources
Canada's Office of Energy Efficiency, Survey of Commercial and Institutional Energy Use (SCIEU) tables
and any published SCIEU summary report; Natural Resources Canada Survey of Household Energy Use (SHEU),
already cited in the manuscript for residential, checked here only for whether it splits multi-unit
residential comparably; CMHC Canadian Housing Statistics Program; National Research Council Canada
building-stock studies; any Canadian building-energy-benchmarking peer-reviewed literature (Building and
Environment, Energy and Buildings, Journal of Building Engineering) reporting measured EUI distributions
by use type.

---

## Deliverable

Section A of your answer must contain a table with columns:

`Channel | Data source | Geography | Years | EUI figure(s) reported (kWh/m2.yr, converted if needed,
show arithmetic) | Floor-area basis | Fuel scope (all-fuel/electricity-only) | Sample size | Access |
DOI or URL | Tier`

At least one row per channel (residential, office, retail, hotel), and, where available, a mixed-use
row. Where nothing measured and public exists for a channel, say so explicitly with the search queries
that found nothing, rather than omitting the row.

Then:

1. Section F of the response template, filled in per channel where a usable figure was found: target
   quantity, our model's measured value (given below), the external measured value, and the tolerance
   you would accept before calling it a genuine mismatch versus a difference already explained by
   area-basis or fuel-scope mismatch.
2. One paragraph stating plainly whether any of the found measured Canadian figures would, on their own
   evidence, support widening or narrowing any of the three failing as-modelled bands (office 100/135/200,
   hotel 180/240/300, retail 80/110/155 kWh/m2.yr, low/central/high), while making clear that this
   study's frozen gate verdicts are not to be changed by this prompt regardless of the answer; the
   question is only whether external measured evidence agrees or disagrees with the existing bands.

**Our model's current measured values, for Section F and for your own sanity check** (already
published, frozen CFA-basis medians across all 56 campaign cells, must not be altered by this prompt):
Office 71.02 kWh/m2/yr (range 61.72-90.21; uninjected control 85.45); Retail 75.63 kWh/m2/yr (range
63.63-96.84); Hotel 260.54 kWh/m2/yr (range 203.33-318.42); Residential 119.10 kWh/m2/yr (range
111.57-128.77).

Rules restated, because every previous round in this project needed them:

- A dataset or table is not evidence until it has been opened. Report what you opened.
- Give URL or DOI for every item. Items without a working link are discarded.
- `NOT FOUND` beats an invented number, an invented year, or an invented sample size.
- Never propose relaxing a reference band or a gate verdict because this project's model fails it. That
  decision belongs to the authors alone and is out of scope for this prompt entirely.
- Keep as-modelled (the manuscript's own bands) and empirical (this prompt's findings) figures strictly
  separate; do not blend a measured Canadian figure into an as-modelled band number.
- Fabricated citations are expected in Gemini's returned reports and will be checked, one by one, before
  anything is quoted in the manuscript.
- No em dashes and no en dashes anywhere in the returned text.

Save the return as `RV14_3J_measured_annual_eui_canada.md` in this same folder.
