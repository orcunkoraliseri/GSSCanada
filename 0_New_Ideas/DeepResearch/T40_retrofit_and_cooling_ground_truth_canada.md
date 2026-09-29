# T40. What can check the model: truth on heat pumps, air conditioning and retrofits in Canadian homes

Paste `00_MASTER_BRIEF.md` first (read its section 10), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. Run alone. Written 2026-09-22. Your files are
`RT40_retrofit_and_cooling_ground_truth_canada.md` and `RT40_pages.log`.

## Why we are asking

A model that reads permit text is only worth publishing if its answers can be scored against
something true. We need sources that say, per building or per dwelling (role `L2`), or as counts by
area and year (role `L3`), which Canadian homes have a heat pump, air conditioning, added insulation
or new windows, and whether any of them can be joined to an address (role `L4`).

## What we need

### Item 1. Per-dwelling truth (role `L2`)

One record-source card (brief section 10) for each of these, or a `NOT FOUND` line with URLs tried:
* NRCan EnerGuide home evaluations and the database behind them (pre- and post-retrofit audits),
  including any access route for university researchers;
* Canada Greener Homes Grant and Canada Greener Homes Loan: any public or researcher-accessible data;
* Canada Greener Homes Affordability Program and the Oil to Heat Pump Affordability program;
* Quebec: Rénoclimat, LogisVert (Hydro-Québec), Chauffez vert, and Hydro-Québec's own program data;
* Ontario: Home Renovation Savings, Enbridge Home Efficiency Rebate Plus, Toronto's Home Energy Loan
  Program (HELP), IESO program data;
* British Columbia (CleanBC Better Homes), Alberta, Nova Scotia (Efficiency Nova Scotia), Manitoba
  (Efficiency Manitoba);
* any municipal or utility heat-pump rebate list published by address or by postal area.

For each, quote what is released (per address, per postal area, per city, or only totals), and the
terms for linking it to other records.

### Item 2. Aggregate checks (role `L3`)

Cards for the Statistics Canada Households and Environment Survey (air conditioning and heating
equipment by city or province, every cycle available), the Survey of Household Spending equipment
tables, the census questions on heating if any, CMHC data, and NRCan's Comprehensive Energy Use
Database tables on residential equipment stocks. We already hold NRCan SHEU 2019 (brief section 9), so
list it only if a newer cycle exists. Give, for each: the smallest geography, the years, and the exact
table identifier from a logged page.

### Item 3. Scoring a record-reading model against truth

Studies that scored an automated reading of building records (permits, audits, listings, assessment
data) against audit, rebate or survey truth, in any country. Section C rows with: the record type, the
truth source, how records were joined to truth, the sample size, and the reported agreement.
`TITLE ONLY` where no abstract or text was logged.

## Named leads

natural-resources.canada.ca, open.canada.ca, www150.statcan.gc.ca, hydroquebec.com,
transitionenergetique.gouv.qc.ca, toronto.ca, enbridgegas.com, ieso.ca, betterhomesbc.ca,
efficiencyns.ca; OpenAlex queries on "EnerGuide", "heat pump adoption" with "Canada", "building
permit" with "validation" or "ground truth".

## Hard constraints specific to this prompt

* "Available to researchers" is written only if a logged page says so; quote the sentence. A program
  that publishes only a press release with totals is `L3` at best.
* Never suggest obtaining per-person or per-household records against their terms, or re-identifying
  anyone. If a source is closed, say so and stop.
* Copy every table identifier and every number exactly from a logged page.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: is there any Canadian source that gives per-building truth on heat pumps,
air conditioning or insulation that a university researcher can obtain and join to an address, and
under what terms. **Section F** is items 1 and 2. **Section C** is item 3. **Section D** says, as
`[INFERENCE]`, which truth source would score a Montreal or Toronto model best, and its main bias.
**Section G** carries the `NOT FOUND` lines, the closed sources, and your negative controls.
