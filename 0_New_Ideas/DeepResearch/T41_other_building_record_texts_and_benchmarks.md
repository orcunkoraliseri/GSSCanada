# T41. Other building records a model could read, and outside-Canada permit sets to benchmark on

Paste `00_MASTER_BRIEF.md` first (read its section 10), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. Run alone. Written 2026-09-22. Your files are
`RT41_other_building_record_texts_and_benchmarks.md` and `RT41_pages.log`.

## Why we are asking

Permits show only work that needed a permit. Other public records may fill the gaps (role `L1`) or
give the join key (role `L4`). Separately, a method is easier to trust if it is also tried on a city
where per-building truth is already public; some US cities publish both permit text and building
energy or equipment data. We need both lists.

## What we need

### Item 1. Other Canadian record texts

One record-source card (brief section 10) for each, or a `NOT FOUND` line with URLs tried:
* property assessment rolls and their building descriptions: Montreal's rôle d'évaluation foncière,
  Quebec's other municipal rolls, Ontario's MPAC, BC Assessment, Alberta municipal assessment data;
* building energy and water benchmarking disclosure: Ontario's Energy and Water Reporting and
  Benchmarking (EWRB), Toronto, Montreal's by-law on greenhouse gas disclosure for large buildings,
  Vancouver, Calgary, Edmonton; say which ones cover multi-unit residential buildings;
* municipal 311 or service-request records that mention heating or cooling (for example "no heat" or
  "no air conditioning" complaints) by address or area;
* rental or sale listing text (Centris, realtor.ca, Kijiji, Rentals.ca and similar): quote their terms
  on automated collection and reuse; do not propose collecting them against those terms.

### Item 2. Outside-Canada permit sets with public truth, for benchmarking only

Cards for US or other cities that publish both residential permit free text and a per-building truth
source on heating, cooling or retrofits: at least New York City, Chicago, Boston, Seattle, San
Francisco, Los Angeles, Austin, Denver, Washington DC, Philadelphia, Minneapolis. For each, name both
files, the join key between them, and the years they overlap.

### Item 3. Language models reading any of these records

Studies that used a language model or text classifier on assessment, benchmarking, listing, 311 or
permit text to infer building equipment or energy features. Section C rows with: the record type,
the city, the model, what was extracted, whether the model could abstain or give a set of answers,
and the reported accuracy. `TITLE ONLY` where no abstract or text was logged.

## Named leads

Municipal and provincial open-data portals; mpac.ca, bcassessment.ca; ontario.ca (EWRB); NYC Open
Data (DOB permits, Local Law 84 and 97 data), data.cityofchicago.org, data.boston.gov,
data.seattle.gov, datasf.org, data.lacity.org, data.austintexas.gov; OpenAlex and arXiv queries on
"building permit" with "language model", "text classification", "heat pump", "retrofit".

## Hard constraints specific to this prompt

* Terms of service and licences are quoted from a logged page, never summarised. If terms forbid
  automated collection, the card says so and the source is marked `not usable`.
* Item 2 sources are for method benchmarking only; do not present them as Canadian evidence.
* A study row about language models counts only if its abstract or text is logged.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which non-permit Canadian records carry free text or equipment fields
usable as `L1` or `L4`, and which non-Canadian city has permit text plus public per-building truth that
overlap in years. **Section F** is items 1 and 2. **Section C** is item 3. **Section D** says, as
`[INFERENCE]`, which one extra Canadian source would most reduce the "no permit needed" blind spot.
**Section G** carries the `NOT FOUND` lines, the sources marked `not usable`, and your negative controls.
