# VETTING RT05 climate_change_heat_and_ubem

VERDICT: ACCEPTED (manager, 2026-09-07). Ten of ten DOIs match; the malformed prefix in C6 is a typographical variant of the H6 DOI that resolves. No own-work claims beyond the brief. Minor strikes: the ClimateData.ca Design Value Explorer path (F1 row 2) returns 404, keep the portal root as the route; pyepwmorph version and repository disagree with RT10 (2.0.0 at justinfmccarty here, 2.0.1 at intelligent-environments-lab there, the latter 404), so the package is accepted and its version and home are not. Accepted: F1 weather artefacts and licences (PCIC, C3S, and the closed status of CCWorldWeatherGen, Meteonorm, WeatherShift); F2 vulnerability indices lacking indoor terms; B10 and G NOT FOUND for dwelling-level indoor validation; G NOT FOUND for heat-responsive presence; E's engine additions as a design list. Angles: static-archetype overheating taken; A2 open only with the presence module; A4's peak claim depends on an AC-uptake assumption (D row 2).

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (10 unique, 10 MATCH, 0 MISMATCH, 0 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claimed title (Section H, first 90 chars) | Verdict |
|---|---|---|---|---|
| 10.1191/0143624405bt112oa | 200 | Constructing design weather data for future climates | Constructing design weather data for future climates | MATCH |
| 10.1016/j.enbuild.2008.06.005 | 200 | Climate change future proofing of buildings - Generation and assessment of building simu | Climate change future proofing of buildings-Generation and assessment of building simulation | MATCH |
| 10.1016/j.renene.2012.12.049 | 200 | Transforming existing weather data for worldwide locations to enable energy and building pe | Transforming existing weather data for worldwide locations to enable energy and building per | MATCH |
| 10.1016/j.buildenv.2016.01.010 | 200 | Mapping indoor overheating and air pollution risk modification across Great Britain: A model | Mapping indoor overheating and air pollution risk modification across Great Britain: A modell | MATCH |
| 10.1016/j.buildenv.2011.12.003 | 200 | Building characteristics as determinants of propensity to high indoor summer temperatures in | Building characteristics as determinants of propensity to high indoor summer temperatures in | MATCH |
| 10.1080/09613218.2016.1222190 | 200 | Overheating in vulnerable and non-vulnerable households | Overheating in vulnerable and non-vulnerable households | MATCH |
| 10.1016/j.buildenv.2017.06.031 | 200 | The impact of climate change on the overheating risk in dwellings - A Dutch case study | The impact of climate change on the overheating risk in dwellings-A Dutch case study | MATCH |
| 10.3390/data4020072 | 200 | Climate Data to Undertake Hygrothermal and Whole Building Simulations Under Projected Climat | Climate Data to Undertake Hygrothermal and Whole Building Simulations Under Projected Climate | MATCH |
| 10.1016/j.enbuild.2020.109935 | 200 | Future heating and cooling degree days for Belgium under a high-end climate change scenario | Future heating and cooling degree days for Belgium under a high-end climate change scenario | MATCH |
| 10.1016/j.enbuild.2017.02.049 | 200 | Monitoring summer indoor overheating in the London housing stock | Monitoring summer indoor overheating in the London housing stock | MATCH |

Years: all 10 CrossRef `issued` years match the years stated in the report's Section C/H (2005, 2008, 2013, 2016, 2012, 2016, 2017, 2019, 2020, 2017 respectively).

**Extra identity finding (not counted in the 10 above, found by manual read, not the regex):** Section C row C6 (line 34) prints the DOI as `` 10.80/09613218.2016.1222190 `` (malformed prefix, only 2 digits after "10."). This does not match the task's DOI regex (`10\.[0-9]{4,9}/...` requires 4-9 digits) so it is not one of the 10 above. Checked anyway: `curl` on `https://api.crossref.org/works/10.80/09613218.2016.1222190` returns HTTP 404 (NOT RESOLVED). Section H, line 115, gives the same reference as `` 10.1080/09613218.2016.1222190 `` (which resolves, see row above). The two strings for the same Vellei et al. (2017) reference disagree between Section C and Section H.

## 2. Dashes

em: 0  en: 0

## 3. URLs (12 checked of 12)

| URL | HTTP status |
|---|---|
| https://services.pacificclimate.org/demo/wx-files/app/ | 200 |
| https://climatedata.ca/explore/variable/dve/ | 404 |
| https://cds.climate.copernicus.eu/datasets/sis-energy-derived-projections | 200 |
| https://pypi.org/project/pyepwmorph/ | 200 |
| https://energy.soton.ac.uk/ccworldweathergen/ | 200 |
| https://meteonorm.com/ | 200 |
| https://santemontreal.qc.ca/professionnels/drsp/sujets-a-z/chaleur/ | 200 |
| https://www.toronto.ca/city-government/data-research-maps/open-data/ | 200 |
| https://www.atsdr.cdc.gov/placeandhealth/svi/index.html | 404 (403 when retried with a browser User-Agent) |
| https://www.canada.ca/en/health-canada/services/climate-change-health/extreme-heat.html | 200 |
| https://cds.climate.copernicus.eu/ | 200 |
| https://github.com/justinfmccarty/pyepwmorph | 200 |

## 4. OpenAlex counts

NONE QUOTED. The file contains no `openalex` string, no API URL, and no query construction.

## 5. Provenance columns

Section C landscape table (10 rows, C1-C10): column "Read: full / abstract / none" present, filled in all 10/10 rows. Every filled value is the identical string "Full" (no row uses "abstract" or "none").

Section D gap-and-fit table (2 rows, A2/A4): no "date checked" or "read" style provenance column exists in this table (0/2, column absent, not merely empty).

Section F artefact tables: Part 1 (7 rows) has a "Date checked" column, filled 7/7, every value the identical string "2026-09-07". Part 2 (4 rows) has a "Date checked" column, filled 4/4, every value the identical string "2026-09-07".

Totals: 21 of 21 rows that have a provenance column carry a non-empty value; all values within each table are identical across rows (no per-row differentiation); Section D has no such column at all.

## 6. Own-work claims beyond the brief

NONE. Section A/E state design recommendations ("our simulation engine requires three modular additions", "We must not promise or claim that our engine predicts exact indoor temperatures...") without asserting a specific invented number or result for the author's engine, CENTUS, OpenUBEM, or papers 1J-4J. No sentence states a fabricated result, metric value, or fact about "our" work beyond what the master brief (`00_MASTER_BRIEF.md`, e.g. lines 55-69, 162) already supplies (four European districts, Montreal/Toronto Canadian stubs, the master brief's own instruction "Do not state, estimate or reproduce any result of our models or our engine" is not violated).
