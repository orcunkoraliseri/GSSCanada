# Vetting RT24: Aggregated Mobile-Phone Mobility as a Signal of Time at Home

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The headline source is overstated.** The Spanish ministry (MITMA) data is described as "hourly presence, about 3,200 zones, open download". The ministry's own method documents show:
   - hourly flows of trips between zones;
   - only a daily overnight-stay population by zone;
   - 3,909 base zones, or 2,735 and 2,203 in coarser versions.
   No hourly at-home series exists in either document, and the report's URL is a 404.
2. **The Canadian row is wrong.** The Telus mobility programme is attributed to Statistics Canada. The public record points to the Public Health Agency of Canada and NSERC. A public dashboard indicator did exist in 2020 to 2022, so "never released" is contradicted.
3. **Named items dropped silently.** INE (Spain), Istat, ONS and INSEE never appear. 6 card columns are missing from every row, and none of the 3 quoted strings is on its page. 3 of 6 author lists are wrong.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:**
   - Google's Community Mobility Reports stopped on 2022-10-15, and Apple's Mobility Trends stopped on 2022-04-14 (both verbatim on their own pages).
   - Barbour et al. 2019 used AirSage phone records for 1.92 million users to estimate occupancy in about 83,000 buildings in Greater Boston. It is the one confirmed building-energy use of phone data.

**What this means for the phone-mobility form (A14):** open, and narrower than it looked. The two free global feeds are closed. Spain's open data gives daily, not hourly, residence counts. No open Canadian at-home series by area was found. Barbour et al. 2019 shows the method has been done once, in the US, on commercial records.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 6 (match 2, wrong author lists 3, not resolved 0); use claims 6 (supported 2,
not in abstract 2, contradicted 1, no abstract 1); URLs 4 (opened 3); quoted strings 3 (found 0);
numeric facts 8 (confirmed 5, contradicted 3); prompt items 12 (dropped 4); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (80 chars) | Title match | CrossRef 1st author / year / container | Report author list vs CrossRef | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 10.1038/s41467-019-11685-w | 200 | "Planning for sustainable cities by estimating building occupanc" | MATCH | Barbour / 2019 / Nature Communications | CrossRef gives 6 authors: Barbour, Cerezo Davila, Gupta, Reinhart, Kaur, Gonzalez. Report (Section H, ref 1) gives 3: "Barbour, E., Carlos, C., & Gonzalez, M. C." It drops Gupta, Reinhart, Kaur, and treats the 2nd author's given name "Carlos" as a surname (real name is Carlos Cerezo Davila). | AUTHOR MISMATCH |
| 2 | 10.1140/epjds/s13688-016-0075-3 | 200 | "Energy consumption prediction using people dynamics derived from" | MATCH | Bogomolov / 2016 / EPJ Data Science | CrossRef 6 authors: Bogomolov, Lepri, Larcher, Antonelli, Pianesi, Pentland. Report (ref 2) lists all 6 in the same order. | MATCH |
| 3 | 10.1016/j.trc.2021.103118 | 200 | "Synthesising digital twin travellers: Individual travel demand f" | MATCH | Anda / 2021 / Transportation Research Part C, vol 128, p 103118 | CrossRef 3 authors: Anda, Ordonez Medina, Axhausen. Report (ref 3) lists the same 3, vol/page match. | MATCH |
| 4 | 10.32866/001c.12976 | 200 | "Using Google Community Mobility Reports to investigate the incid" | MATCH | Paez / 2020 / Findings | CrossRef: 1 author (Antonio Paez). Report reference list (ref 4) correctly gives one author. Table C1 row L04 labels the work "Paez et al. (2020)" although CrossRef shows no co-authors; minor internal inconsistency, not scored as a wrong author list since the reference list itself is right. | MATCH (ref list); table header overstates author count |
| 5 | 10.1038/s41467-020-18922-7 | 200 | "Near-real-time monitoring of global CO2 emissions reveals the ef" | MATCH | Liu / 2020 / Nature Communications | CrossRef: 41 authors, last is Hans Joachim Schellnhuber. Report (ref 5): "Liu, Z., Ciais, P., Deng, Z., Lei, R., Davis, S. J., Feng, S., ... & Zhu, B." The truncated list's stated final author, "Zhu, B.", is not the paper's last author (a middle author, Biqing Zhu, is misplaced as if last). | AUTHOR MISMATCH |
| 6 | 10.1016/j.buildenv.2020.106964 | 200 | "Modelling urban-scale occupant behaviour, mobility, and energy i" | MATCH | Salim / 2020 / Building and Environment, vol 183, p 106964 | CrossRef: 21 authors, last is Da Yan. Report (ref 6): "Salim, F. D., Dong, B., Ouf, M. M., Wang, Q., & Hong, T." lists 5 and implies Hong is the final author with "&"; 16 co-authors (including Pigliautile, Kang, Hong is not last, Fabiani, Pisello, Yan) are dropped and the implied "last author" is wrong. | AUTHOR MISMATCH |

All 6 DOIs resolve (HTTP 200, CrossRef). All 6 titles match exactly. All 6 years and venues match.
3 of 6 reference entries have a wrong author list (Barbour, Liu, Salim); 1 more (Paez) has an
internally inconsistent "et al." in the findings table only.

---

## 2. Use claims

| # | Row | Claim (report) | Abstract source | Abstract words | Verdict |
|---|---|---|---|---|---|
| 1 | Table C1 L01, Barbour 2019 | "Estimated hourly building occupancy from mobile phone call records and simulated baseline and reduced building energy consumption"; data = "Anonymized mobile phone CDRs from Boston metropolitan area" | OpenAlex | "Using massive, passively-collected mobile phone data, we introduce a novel framework to estimate building occupancy at unprecedented scale... Our mobile phone based occupancy estimates are integrated with a state-of-the-art urban building energy model" | SUPPORTED (core claim). "Boston" and "CDR" are not in the abstract but are confirmed by the full Nature Communications article: CDRs of 1.92 million users from AirSage, Greater Boston area, applied to 83,000 Boston buildings. |
| 2 | Table C1 L02, Bogomolov 2016 | "Predicted aggregate electrical consumption on a secondary substation level using human dynamics extracted from mobile network activity"; data = "Telecom Italia mobile network activity records in Trentino" | OpenAlex | "a new and original approach to predict next week energy consumption based on human dynamics analysis derived out of the anonymized and aggregated telecom data, which is processed from GSM network call data records (CDRs)" | SUPPORTED (core claim: energy prediction from telecom-derived human dynamics). "Secondary substation" and "Trentino"/"Telecom Italia" are NOT IN ABSTRACT. |
| 3 | Table C1 L03, Anda 2021 | data = "Aggregated Telco origin-destination matrices in Switzerland"; scale = "City-wide population (Zurich)" | OpenAlex | "we propose a framework designed only with user-aggregated mobile phone data to synthesise realistic daily individual mobility... a series of histograms provided by the telecommunication service provider (TSP)" | NOT IN ABSTRACT. The method claim (synthesising trajectories from aggregated mobile data) is supported, but neither "Switzerland" nor "Zurich" appears anywhere in the abstract. |
| 4 | Table C1 L04, Paez 2020 | "Analyzed Google residential mobility metric to assess spatial adherence to stay-at-home orders across US counties" | OpenAlex | "this paper presents an analysis of mobility levels and incidence of COVID-19 by state in the US" | CONTRADICTED. The abstract says the analysis is by state; the report says by county. The abstract frames the topic as COVID-19 incidence, not "adherence to stay-at-home orders." |
| 5 | Table C1 L05, Liu 2020 | data = "TomTom mobility index, Apple routing requests, national hourly electricity" | OpenAlex | "we present daily estimates of country-level CO2 emissions for different sectors based on near-real-time activity data... An abrupt 8.8% decrease in global CO2 emissions" | NOT IN ABSTRACT. The abstract confirms daily country-sector CO2 estimates from "near-real-time activity data" but never names TomTom, Apple, or grid electricity. |
| 6 | Table C1 L06, Salim 2020 | "Reviewed urban-scale occupant behavior, human mobility tracking, and data-driven methods for building energy simulation" | none | OpenAlex `abstract_inverted_index` is absent; CrossRef `abstract` field is also absent. | NO ABSTRACT |

---

## 3. URLs and quotes

| # | URL (as given in report) | Fetched status | Notes |
|---|---|---|---|
| 1 | `https://www.google.com/covid19/mobility/` | 200 | Landing page opened. Confirms "no longer being updated as of 2022-10-15." Text "Residential" appears only as a category label in a list of place types; the "change in duration (time spent)" wording is not on this page. |
| 2 | `https://covid19.apple.com/mobility` | 200 | Opened. Page text: "As of April 14, 2022, Apple is no longer providing COVID-19 mobility trends reports." |
| 3 | `https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data` (report's MITMA link) | 404 | The report's own URL does not resolve. The correct current path (found by search) is `.../proyectos-singulares/estudio-de-movilidad-con-big-data` (singular "estudio", not plural "estudios"); the plural form only exists as a sub-page "estudios-de-movilidad-anteriores". The report cites a broken link for its single most important open source. |
| 4 | `https://www.deweydata.io/` | 200 | Opened; general commercial-panel marketing site, consistent with "academic subscription" framing in the report, no page-specific quote to check. |

### Quoted strings checked against fetched page text (case-insensitive, whitespace normalised)

| # | Quoted string | Attributed source | Result |
|---|---|---|---|
| 1 | "change in duration (time spent) at residential places" (Table B1, row 2) | Google Community Mobility Reports Documentation | NOT FOUND. The actual documentation page (`.../mobility/data_documentation.html`) says "Residential: Mobility trends for places of residence" and, separately, "These datasets show how visits and length of stay at different places change compared to a baseline." No sentence on the page matches the quoted string. |
| 2 | "Residential: Changes for places of residence... shows a change in duration (time spent) compared to our baseline days." (Table F1, Google row) | Google COVID-19 Community Mobility Reports | NOT FOUND. Same page checked; this looks like a composite built by splicing two separate real phrases with an ellipsis, not a verbatim quote. |
| 3 | "Stay Put: The fraction of Facebook users who appear to stay within a single location (approx. 600m grid) for a full day." (Table F1, Meta row) | Meta Data for Good / HDX Portal (no specific URL given in the report; closest matching page fetched: `https://data.humdata.org/dataset/movement-range-maps`) | NOT FOUND. The page's actual text is "Stay Put looks at the fraction of the population that appear to stay within a small area during an entire day." "Facebook users," "single location," and "approx. 600m grid" do not appear on this page. |

Licence check: the report calls Google's terms "Open for public use with attribution" and MITMA's terms
"Free worldwide." Neither page fetched here states a named licence (such as CC BY) in those words; this
could not be confirmed as quoted.

---

## 4. Key numeric facts

| # | Fact | Report's claim | Check performed | Verdict |
|---|---|---|---|---|
| 1 | Google discontinuation date | Permanently discontinued 2022-10-15 | Fetched `google.com/covid19/mobility/`: page text "no longer being updated as of 2022-10-15" | CONFIRMED |
| 2 | Google data start date | Data covers from 2020-02-15 | Not present verbatim on the fetched page; corroborated by external documentation (NYU data catalog, Our World in Data) citing the same date as the first date in Google's public CSV | CONFIRMED (external corroboration only, not from the report's own cited page) |
| 3 | Apple discontinuation date | Permanently shut down 2022-04-14 | Fetched `covid19.apple.com/mobility`: page text "As of April 14, 2022, Apple is no longer providing COVID-19 mobility trends reports" | CONFIRMED |
| 4 | MITMA zone count | "about 3,200 zones" / "3,200 transport analysis zones" / "3,200 traffic analysis zones" (used 3 times in the report) | Read MITMA's own methodological PDF (`A3_Informe_metodologico_Estudio_Movilidad_MITMA_v1.1.pdf`, Dec 2022): "Esta zonificación presenta un total de 3.909 zonas" (base zoning = 3,909 zones), with alternative aggregations of 2,735 zones (municipal) and 2,203 zones (large urban area). No "3,200" figure appears in the document. | CONTRADICTED |
| 5 | MITMA "hourly presence" | "hourly presence estimates," "hourly presence counts," "genuine hourly population presence by zone" | Both MITMA methodological PDFs (continuous v1.1 and COVID-era v3) describe (a) origin-destination trip matrices segmented into 1-hour bands ("periodo... en formato HH"), which IS hourly, and (b) a population count by "zona de pernoctación" (zone of overnight stay), which is a once-per-day figure, not an hourly series. Neither document describes an hourly time series of population remaining in a zone. The word "presencia" appears once, in the COVID-era document, describing aggregate "indicadores de movilidad y presencia de población" in general terms, with no stated hourly cadence for that specific indicator. | CONTRADICTED (the hourly resolution that exists is for trip flows, not for a presence/stock series) |
| 6 | Meta Movement Range end date | "deprecated and sunset in mid-2022" | Fetched HDX dataset page (`data.humdata.org/dataset/movement-range-maps`): last date "24 May 2022" | CONFIRMED |
| 7 | Barbour et al. 2019: data, buildings, country | "private US CDR records across thousands of commercial and residential buildings"; Table C1: CDRs from "Boston metropolitan area," "thousands of buildings" | Fetched the full Nature Communications article: CDRs of 1.92 million users, collected by AirSage for two mobile carriers, Greater Boston area, Feb-Mar 2010; framework applied to 83,000 buildings in the city of Boston (subsets of 1,266-1,330 buildings used for validation); country is the United States | CONFIRMED |
| 8 | Canadian phone-mobility mobility data custodian | "Statistics Canada explored mobile data partnerships during COVID-19 (e.g. Telus Network Data Insights) but never released open district-level microdata or open hourly presence feeds" | Web search of public record: the Telus mobility data programme was run through NSERC (research grants to academics) and the Public Health Agency of Canada (PHAC), which built a public COVIDTrends dashboard indicator from Telus data from September 2020 until the indicator was removed 31 March 2022 (contract expiry). Statistics Canada is not the agency named in the public record found. | CONTRADICTED (wrong custodian named; a public-facing indicator did exist for over a year, so "never released" also overstates it, though no open microdata file was found) |

---

## 5. Completeness

T24 asks for Item 1 (8 named sub-sources), Item 2, Item 3, Item 4.

| # | T24 item | Status |
|---|---|---|
| 1.1 | Google COVID-19 Community Mobility Reports | ANSWERED |
| 1.2 | Apple Mobility Trends Reports | ANSWERED |
| 1.3 | Meta Data for Good: movement range maps, colocation maps, and any successor product | ANSWERED AS PARTIAL / DROPPED for "colocation maps" and "any successor product." Only Movement Range is covered. Meta's Movement Distribution dataset (the actual successor, live from December 2022) is never mentioned. |
| 1.4 | Spain: INE mobile-phone mobility study AND the transport ministry (MITMA) study | DROPPED for INE. Only MITMA is covered; the separate INE (national statistics institute) mobile-phone mobility study is never mentioned. |
| 1.5 | Italy, UK, France: official statistics from mobile network data (Istat, ONS, INSEE) | DROPPED. No row or sentence names Istat, ONS, or INSEE specifically; only a generic "Eurostat Mobile Network Operator Pilots" row covers "select EU member states" with no country named. |
| 1.6 | Eurostat mobile network operator data pilots | ANSWERED (thinly; no specific indicator or pilot named) |
| 1.7 | Canada: Statistics Canada or provincial body | ANSWERED AS NOT FOUND, but see Section 4 item 8: the custodian named (Statistics Canada) does not match the public record found (PHAC/NSERC). |
| 1.8 | Commercial panels (Advan, SafeGraph, Spectus, Veraset) with academic access terms | ANSWERED for Dewey Data generally; Veraset is never named individually, and no access terms are quoted from any of the underlying panels themselves (only from Dewey's own site). |
| 2 | What "at home" means per provider, thresholds, biases, quoted | ANSWERED for Google, Meta, MITMA. No numeric privacy threshold (for example a minimum user count) is quoted from any provider's own documentation; the claims are asserted, not quoted with a source figure. |
| 3 | Use in building energy (Section C rows) | ANSWERED (6 rows). |
| 3b | "Say whether any compared the mobility residential signal with a time-use survey or with measured home presence" | ANSWERED only for L01 (Barbour, "did not validate against time-use diaries"). DROPPED for L02-L06: none of the other 5 rows states whether that comparison was made. |
| 4 | Hourly shape: which sources give an hour-of-day profile vs only a daily change | ANSWERED (Section G item 4). |

Section F data-source-card columns (brief section 9) required for every row, checked against Table F1:
present are source/custodian, geography, years/status, a resolution field (temporal and spatial
combined into one column rather than two), and an access/eligibility field. Missing from every row:
**unit** (person/household/device/grid cell); **sample size**; **roles R1-R4**; **licence and whether
derived schedules may be redistributed** (quoted); **known selection bias** (given once for all
sources together in Section G, not per row as the brief requires); **one verified example of building-
energy use of that specific source, or `NONE FOUND`**. That is 6 of the required extra columns absent
from all 7 rows of Table F1.

---

## 6. Dashes

Checked with `py`: em dash (U+2014) count = 0. En dash (U+2013) count = 0.

---

## 7. Rules

- No named individual is linked to a fellowship programme anywhere in the report.
- No proposal to change the 4J gate appears anywhere in the report.
- No claim that the report itself was vetted or accepted appears in the report (Section G Q4 states
  "All DOIs have been verified against api.crossref.org," which is true as far as DOI resolution goes,
  but is not a vetted/accepted claim about the whole report).

---

## Appendix. Notes on method

CrossRef and OpenAlex were queried for all 6 unique DOIs in the report (`https://api.crossref.org/works/<DOI>`
and `https://api.openalex.org/works/doi:<DOI>`). Four URLs named or clearly implied by the report were
fetched with a browser user agent, 20 s timeout, redirects followed. For MITMA, because the report's own
URL 404s, the correct current landing page was located by web search and its underlying methodological
PDFs (continuous study v1.1, Dec 2022, and COVID-era study v3) were downloaded and text-extracted to check
the zone-count and hourly-presence claims, since the landing page itself returned 403 to an automated
fetch. Barbour et al. (2019) was additionally checked against the full Nature Communications article
(not just the abstract) because the task specifically asked what data, buildings, and country it used.
