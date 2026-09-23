# V13. Independent measured hourly presence or load data, per use type

Paste `00_MASTER_BRIEF_V2.md` ahead of this prompt, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H). This prompt unblocks plan items P8 and V2.

---

## Why we are asking

The manuscript reports, per channel, a weekday load shape, a circular-mean peak hour, and a
whole-building coincidence factor across four occupant populations (residential, office, retail,
hotel) sharing one stacked tower. None of it is checked against anything measured; it is checked only
against the survey the model was trained on and against code-default schedules. A 2J reviewer already
asked for exactly this ("external validation of the hourly profile against measured data"), and 3J has
not answered it for any of its four channels.

**The independence requirement is the whole point of this prompt.** Two data sources are already inside
this pipeline and must not be offered back as if they were independent evidence:
1. The Canadian General Social Survey (GSS) Time-Use microdata (2005, 2010, 2015, 2022), which is what
   the residential, office and retail channels were generated and fitted from.
2. The Institut de la statistique du Quebec (ISQ) and CBRE/Travel Alberta monthly hotel-occupancy-rate
   series, which is what the hotel SARIMA side-track was fit to.

A dataset built from either of those, or from a source that itself draws on them, is not usable here.
We need presence or load data measured by an independent instrument (a utility meter, a building
management system, a WiFi/badge/sensor occupancy count, a separate national time-use or travel survey,
a separate hotel/hospitality industry panel not sourced from ISQ or CBRE, or a published load-research
study) for one or more of: residential, office, retail, hotel, or a mixed-use building as a whole.

---

## What we need

1. For each of the four use types (residential, office, retail, hotel/hospitality) and, separately, for
   mixed-use buildings as a whole, find publicly documented measured hourly (or sub-hourly, or at worst
   daily-profile) presence or load data for Canada, or, if none exists for Canada, for a climate and
   building-stock context genuinely comparable (similar heating-dominated climate, similar code
   vintage; a Nordic, northern-US or similar cold-climate source is preferable to a source from a warm
   or Mediterranean climate).
2. For each candidate dataset, state explicitly: what is measured (presence/occupancy count, or energy
   load, and if load, which end use); the source instrument or method (utility smart-meter, BMS,
   sensor, survey diary, industry panel); the geographic and building-stock coverage; the years covered;
   the time resolution (state whether an hourly weekday profile can actually be extracted, or whether
   the finest public resolution is monthly or daily); how it is accessed (open dataset with a direct
   download link, an application/registration process, or a paywalled or restricted product); and the
   licence or terms of use for reuse in a published figure.
3. State explicitly, dataset by dataset, whether it is independent of the GSS Time-Use survey and of
   the ISQ/CBRE hotel series named above, or whether it in fact draws on either (for example, some
   commercial hotel-occupancy panels resell government tourism-statistics tables; check the panel's own
   methodology page for this before listing it as independent).
4. Prioritize, in this order: (a) open datasets with a documented licence permitting reuse in a figure;
   (b) datasets requiring a data-use agreement or academic registration but genuinely obtainable; (c)
   datasets described in a published paper's methodology section, where the paper itself, not the raw
   data, is what we could cite and compare against; (d) commercial or paywalled products, flagged as
   such, listed only if nothing in (a)-(c) exists for that channel.
5. If nothing usable exists for a given channel, after a real search (report the queries, per rule
   below), say so plainly rather than stretching a partial match. A clean "nothing found, independent
   and public, for this channel" is a valid and useful answer.

---

## Named leads

Canada-specific: Statistics Canada's Survey of Household Energy Use (SHEU) end-use tables (state
whether any sub-annual/hourly disaggregation exists beyond the annual totals this project already
uses); Natural Resources Canada's Survey of Commercial and Institutional Energy Use (SCIEU); provincial
utility open-data or load-research programs (Hydro-Quebec, Hydro One / IESO Ontario, BC Hydro, ENMAX or
Calgary-area utility open data) for residential and commercial hourly load-research panels; CMHC or
municipal building-benchmarking open portals with sub-annual detail if any exists; university or NRC
building-instrumentation datasets (CanmetENERGY, Concordia's own published instrumented-building
studies) if independent of this project's authors' prior work.

North American / comparable-climate: ASHRAE Research Project databases on measured occupancy or
diversity/coincidence factors; U.S. Department of Energy commercial building datasets (CBECS microdata,
though it is annual not hourly; note this explicitly if it is the best available); the U.S. National
Renewable Energy Laboratory (NREL) End-Use Load Profiles (EULP) dataset, which does include synthetic
hourly load shapes for U.S. building stock by type, state whether it is measured, simulated, or a blend,
and whether it covers retail and hotel/hospitality as distinct types; American Time Use Survey (ATUS)
for a genuinely independent residential/workplace/shopping presence check (distinct from Canada's GSS);
published WiFi- or badge-based office-occupancy studies (a well-known strand exists post-2020 tracking
office reoccupancy, for example Kastle Systems' published back-to-office index, or university-published
occupancy-sensor studies) for the office channel specifically; published retail footfall or
customer-traffic panel data (for example industry footfall-analytics providers, if their methodology
page documents public or licensable hourly output) for the retail channel; hotel/hospitality industry
demand-curve studies (for example STR/CoStar hospitality analytics, checked for whether it resells
government tourism statistics or is an independent guest-level panel) for the hotel channel, checked
explicitly against the independence requirement above.

---

## Deliverable

Section A of your answer must contain, per channel (five rows minimum: residential, office, retail,
hotel, mixed-use whole-building), a table with columns:

`Channel | Dataset name | What is measured | Source/instrument | Coverage (geography, years) | Time
resolution (can an hourly weekday profile be extracted? yes/no/unclear) | Access (open/registration/
paywalled) | Licence for reuse | Independent of GSS and ISQ/CBRE? (yes/no/explain) | DOI or URL | Tier`

Then:

1. A one-paragraph recommendation, per channel, of the single best candidate (or "none usable found")
   for the comparison this paper needs: normalized weekday shape and peak hour, channel by channel.
2. A search log: databases and portals checked, exact query strings, result counts. Mandatory, for the
   same reason as every other prompt in this project: a channel reported as "nothing found" without a
   search log cannot be told apart from a search that was never run.
3. Section F of the response template, filled in for any channel where a usable dataset was found:
   target quantity (for example "office weekday peak hour"), our model's comparable output value (from
   the manuscript, quoted below), the expected value from the external source, and a tolerance you would
   accept before calling it a mismatch.

**Our model's current values, for Section F and for your own sanity check** (already published,
frozen, must not be altered by this prompt): weekday peak hour, circular mean, median across four
building-city cells, central 2030 scenario: Office 11.90 h, Residential 12.04 h, Retail 12.37 h, Hotel
18.91 h; whole-building peak 14.95 h; whole-building coincidence factor median 0.941 (low 0.851).
Weekday midday-to-night ratios: Retail near 34 to 1, Office near 11.8 to 1, Residential near 3.9 to 1,
Hotel inverted (night exceeds midday).

Rules restated, because every previous round in this project needed them:

- A dataset is not evidence until its methodology page has been opened and read. Report what you
  opened.
- Give URL or DOI for every item. Items without a working link are discarded.
- `NOT FOUND` beats a stretched match. A partial match (wrong climate, wrong resolution, wrong years) is
  fine to report, but must be labelled as partial, not silently presented as a fit.
- Fabricated citations are expected in Gemini's returned reports and will be checked, one by one, before
  anything is quoted in the manuscript.
- Never present a modelled or simulated profile as measured, and flag clearly anywhere a candidate
  dataset (such as NREL's EULP) is itself partly synthetic rather than directly metered.
- No em dashes and no en dashes anywhere in the returned text.

Save the return as `RV13_3J_measured_hourly_occupancy_and_load.md` in this same folder.
