# Vetting RT33: The Work-from-Home Shift as Recorded by Open Data Other than Time-Use Surveys

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Its one quoted Statistics Canada sentence was found nowhere.** "21.4 % in early 2024" from a "May 2024" Daily
   matches no release (Q2, N2). The real releases say about 20 % in November 2023 (Daily 2024-01-18, from the Labour
   Force Survey) and 21 % in July 2023 (the 2022 time-use survey highlights, Daily 2024-06-05).
2. **Wrong variable, wrong numbers.** The telework variable given, `COWMAIN`, is "class of worker", not work location
   (N4). The Madrid survey had 256 households, not 920 (N5). A 2021 paper is cited for a 2023 figure (N7). The Google
   paper works by state, not county (L03).
3. **Item 1 is mostly dropped.** Spain, Italy and the UK get no card of their own. There is no smart-meter, utility or
   thermostat row. Four named leads were never used (SWAA, the ONS survey, Hydro-Quebec, IESO). About 7 of the 13 card
   columns are missing.
4. **Batch finding.** The tool opened no web page. The transit and office percentages are not on the pages it gave.
5. **What survives, checked here:**
   - The Labour Force Survey public file (catalogue 71M0001X).
   - Working from home peaked at about 40 % in April 2020 and was about 20 % by November 2023.
   - Google's Community Mobility Reports stopped updating on 2022-10-15.
   - Eurostat table `lfsa_ehomp` gives the EU home-working share.
   - Liu et al. 2020 and Paez 2020 are real and correctly titled.

**What this means for the post-2020 work-from-home form (A14, role R4):** open. No study was found that uses these
signals to build post-2020 occupancy schedules or to correct pre-2020 ones. Only two national trajectory numbers
survive.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 2, wrong author lists 2, not resolved 0); use claims 4 (supported 0,
not in abstract 1, contradicted 2, no abstract 1); URLs 5 (opened 5); quoted strings 2 (found 1);
numeric facts 8 (confirmed 4, contradicted 4); prompt items 4 (dropped 1, with several sub-asks
silently absent inside item 1); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | HTTP status | CrossRef title (80 char) | Title match | CrossRef 1st author / year / container | Report states | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.enpol.2020.111964 | 200 | Electricity demand during pandemic times: The case of the COVID-19 in Spain | Match | Santiago, I. / 2021 / Energy Policy, vol 148, art 111964 | Santiago, I., Moreno-Munoz, A., Quintero-Jimenez, P., Garcia-Torres, F., Gonzalez-Redondo, M.J. (2021), Energy Policy, 148, 111964 (5 authors, same order) | MATCH |
| D2 | 10.1038/s41467-020-18922-7 | 200 | Near-real-time monitoring of global CO2 emissions reveals the effects of the COVID-19 pandemic | Match | Liu, Z. (first) / 2020 / Nature Communications, vol 11, art 5172. Full author list has 44 names, last author Schellnhuber, H.J. | Report: "Liu, Z., Ciais, P., Deng, Z., Lei, R., Davis, S. J., Feng, S., ... & Zhu, B." The final author printed is "Zhu, B." (Biqing Zhu), who is actually author #10 of 44 in CrossRef, not the last. Real last author (Schellnhuber, H.J.) is omitted. | AUTHOR MISMATCH |
| D3 | 10.32866/001c.12976 | 200 | Using Google Community Mobility Reports to investigate the incidence of COVID-19 in the United States | Match | Paez, A. (sole author) / 2020 / Findings | Paez, A. (2020), Findings, 12976 | MATCH |
| D4 | 10.1016/j.scs.2021.103262 | 200 | Adequacy of telework spaces in homes during the lockdown in Madrid, according to socioeconomic factors and home features | Match | Cuerdo-Vilches, T. (first) / 2021 / Sustainable Cities and Society, vol 75, art 103262. CrossRef lists 4 authors: Cuerdo-Vilches, Navas-Martin, March, Oteiza | Report: "Cuerdo-Vilches, T., Navas-Martin, M. A., & Oteiza, I." Third author Sebastia March is missing entirely (dropped, not "et al."-truncated). | AUTHOR MISMATCH |

Count of author lists wrong: 2 of 4 (D2, D4). Both errors are omission/truncation errors that change
who the reader is told wrote the paper, not typos.

---

## 2. Use claims

Table C1 supplies one "what it did" / "signals compared" use claim per row (L01-L04). Abstracts
rebuilt from OpenAlex `abstract_inverted_index` (D2, D3, D4); D1 (Santiago) has no abstract in
OpenAlex or CrossRef.

| Row | Claim text (report) | Abstract words (rebuilt) | Verdict |
|---|---|---|---|
| L01 Santiago | "Analyzed Spanish national electricity demand and diurnal load shapes during COVID lockdown using mobility data"; signals "Red Electrica hourly load + Google mobility reports" | No abstract available from OpenAlex or CrossRef | NO ABSTRACT |
| L02 Liu et al. | "Monitored real-time changes in global sector-specific energy and CO2 emissions using mobility and power telemetry"; signals "TomTom traffic, Apple mobility, national grid feeds" | "...daily estimates of country-level CO2 emissions for different sectors based on near-real-time activity data... abrupt 8.8% decrease in global CO2 emissions..." No mention of TomTom or Apple by name anywhere in the abstract. | NOT IN ABSTRACT (the named data sources are not in the abstract; the general "mobility/telemetry" framing is roughly consistent) |
| L03 Paez | "Investigated Google residential mobility metrics and stay-at-home order compliance across US counties"; Scale column states "National US (county scale)" | "...GCMR... measure changes in mobility with respect to a baseline... using data from the New York Times on COVID-19 cases and GCMR, this paper presents an analysis of mobility levels and incidence of COVID-19 by state in the US." Abstract explicitly says analysis is **by state**, not by county. No "stay-at-home order compliance" language. | CONTRADICTED (scale: report says county, abstract says state) |
| L04 Cuerdo-Vilches | "Surveyed residential telework adaptation, domestic energy use, and indoor comfort in Madrid homes during lockdown"; "Domestic survey questionnaires (920 homes)" | "...an online survey... The data obtained on workspace perception and its adequacy were studied in Madrid... for a sample of 256 households with people teleworking or studying." No mention of "energy use" or "indoor comfort" in the abstract; the topic is workspace adequacy, not energy or comfort. | CONTRADICTED (920 homes vs abstract's 256 households; energy/comfort framing not supported) |

---

## 3. URLs and quotes

| # | URL (as in report) | Fetched status | What it is | Verdict |
|---|---|---|---|---|
| U1 | https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X | 200 | Confirmed: "Labour Force Survey: Public Use Microdata File," monthly, LFS PUMF | Opens; matches description |
| U2 | https://www.google.com/covid19/mobility/ | 200 | Confirmed discontinuation text: "The Community Mobility Reports are no longer being updated as of 2022-10-15." | Opens; quoted date (2022-10-15) matches report's Table B1 shutdown date exactly |
| U3 | https://www.stm.info/ | 200 | Generic bilingual transit portal homepage (trip planner, fares, service status). No ridership recovery percentages or annual activity report content on this page. | Opens, but the specific 80-82% recovery figure attributed to it is not on this page (report cites "Annual Activity Reports," a different, unlinked document) |
| U4 | https://www.ttc.ca/ | 200 | Generic transit portal homepage (service status, CEO's Report link exists). No ridership recovery percentage on the page itself. | Opens, but the specific 75-80% figure is not on this page (report cites "CEO Monthly Reports," a different, unlinked document) |
| U5 | https://www.kastle.com/ | 200 | Homepage nav lists "Occupancy Barometer" / "Peak Day Hybrid Index," no percentage figures on the page itself | Opens; topic confirmed, but the specific 51.2% figure is not on this page |

Quoted strings attributed to a specific page or source, checked verbatim (whitespace-normalised):

| # | Quoted string | Attributed source | Found on source checked | Verdict |
|---|---|---|---|---|
| Q1 | "The Community Mobility Reports are no longer being updated as of 2022-10-15" (paraphrased in report as "permanent shutdown on 2022-10-15") | Google COVID-19 Community Mobility Reports page | Yes, near-verbatim on the page fetched | FOUND |
| Q2 | "The proportion of workers who usually work most of their hours from home was 21.4 % in early 2024, down from 40 % in April 2020 but nearly triple the 2016 pre-pandemic level (7.1 %)." attributed to "Statistics Canada, The Daily (May 2024)" | Not linked in the report; closest matching StatCan Daily article found by search/fetch is "Working from home in Canada," dated **2024-01-18**, not May 2024 | That article states: "the percentage of Canadians working most of their hours from home during the LFS reference week decreased to about **20% in November 2023**" (not 21.4%, not "early 2024"); "rising to about **40% in April 2020**" (this part matches); "about **7%** of Canadians worked most of the time from home in May 2016" (report says 7.1%, close but not exact, and not phrased as "nearly triple"). No StatCan Daily article titled or dated May 2024 carrying this exact sentence was found. | NOT FOUND (wrong date attributed, wrong headline number, wording does not match any located StatCan release) |

Licence check: report's Table F1 states "Free worldwide" for every row and never quotes a licence
string, as brief section 9 rule 4 requires ("Free for researchers on application" is `application`,
not `open`; terms of service quoted, not summarised). No licence text is quoted anywhere in Section F,
so this cannot be checked against a page; it is asserted, not shown.

---

## 4. Key numeric facts

| # | Fact | Report states | Check | Verdict |
|---|---|---|---|---|
| N1 | LFS telework 2020 peak | ~40% in April 2020 | Confirmed by StatCan "Working from home in Canada" (2024-01-18): "rising to about 40% in April 2020" | CONFIRMED |
| N2 | LFS telework "21.4% in early 2024" per "Daily (May 2024)" | 21.4%, sourced to a May 2024 Daily | No such figure or dated release found; the two real StatCan Daily releases located give 20% (Nov 2023, LFS-based, dated 2024-01-18) and 21% (July 2023, from the 2022 Time Use Survey highlights, dated 2024-06-05) | CONTRADICTED (number and date both unmatched) |
| N3 | Google Mobility discontinuation date | 2022-10-15 | Confirmed verbatim on google.com/covid19/mobility/ | CONFIRMED |
| N4 | LFS PUMF variable for telework named `TELEWORK` / `COWMAIN` | "`TELEWORK` / `COWMAIN`: % of workers working mainly from home, hybrid, or on-site" | `COWMAIN` is documented (ILO microdata catalogue, StatCan guide) as "Class of worker, main job" i.e. paid employee vs self-employed vs public/private, unrelated to work location or telework | CONTRADICTED (COWMAIN is the wrong variable) |
| N5 | Cuerdo-Vilches survey sample size | "920 homes" | Abstract (OpenAlex): "a sample of 256 households" | CONTRADICTED |
| N6 | Kastle office occupancy mid-2024 | 51.2% of baseline | Kastle's own reported figure: occupancy rose to 51.6% by December 2024 after a year of gains; a mid-2024 value in the high-40s/low-50s is plausible but the exact 51.2% figure was not independently located | NOT CONFIRMED (plausible, not verified to the decimal) |
| N7 | Santiago et al. "net structural increase (2023)" of +3% to +5% | Attributed (same table row) to Santiago et al. (2021) | Santiago et al. was published in 2021 (Energy Policy vol 148) and, per its own DOI record and the paper's known scope, analyses the 2020 lockdown period; a 2021 paper cannot report a 2023 data point | CONTRADICTED (temporally impossible attribution) |
| N8 | Eurostat table code `lfsa_ehomp` exists and covers home-working share | "table `lfsa_ehomp`" | Confirmed: Eurostat databrowser lists `lfsa_ehomp`, "Employed persons working from home... as a percentage of total employment," EU Labour Force Survey based | CONFIRMED |

4 of 8 numeric facts confirmed; 4 of 8 contradicted (one of the four, N6, is downgraded to "not
confirmed" in the summary line count above because it is plausible rather than falsified; N2, N4, N5,
N7 are the four counted as CONTRADICTED).

---

## 5. Completeness

T33 prompt items:

| Item | Ask | Verdict | Note |
|---|---|---|---|
| Item 1 | Canada first, then Spain, Italy, UK: one data-source card per open signal (LFS telework, Google mobility, smart-meter/utility, thermostat occupancy, transit ridership, office attendance) | ANSWERED, but materially incomplete / silently dropped sub-asks | Spain, Italy and UK each get **no country-specific card**; only an EU27-aggregate Eurostat row mentions them collectively. UK's named lead (ONS opinions and lifestyle survey) is never mentioned. No Canadian smart-meter/utility row (Hydro-Quebec, IESO, both named leads) and no thermostat-based occupancy row for any country, though the prompt explicitly asks for both categories. |
| Item 2 | Trajectories per signal, quoted, sourced | ANSWERED | Table B1; see Sections 3-4 above for quote/number accuracy problems within it |
| Item 3 | Studies comparing 2+ signals, or a signal vs a time-use survey | ANSWERED (thin) | Only L01 (Santiago, comparing Red Electrica load and Google mobility) clearly compares two signals; none compares a signal against a time-use survey |
| Item 4 | Works using these signals to build post-2020 occupancy scenarios or correct pre-2020 schedules | ANSWERED AS NOT FOUND (implicitly, not stated in prose) | Table C1's own "What it did NOT do" column shows none of L01-L04 does this (e.g. L01: "Did not construct bottom-up building-by-building UBEM schedules"); Section A also states no such comparison exists, but the report never states in Section C or G that Item 4 itself returned no hits |

Named leads from the T prompt not used anywhere in the report: WFH Research (SWAA, US methodological
comparator), ONS opinions and lifestyle survey (UK), Hydro-Quebec, IESO.

Section F data-source card columns required by brief section 9, checked against Table F1's five
columns (signal & custodian; geography & coverage; frequency & temporal span; metric & units; access
conditions & Canadian eligibility):

Missing entirely from every row: unit (person/household/dwelling/device/grid cell/area, as a distinct
field), the occupancy variable quoted from the source's own documentation (the one variable name given,
`COWMAIN`, is wrong, see N4), spatial resolution, sample size, roles `R1` to `R4`, licence text and
whether derived schedules may be redistributed (quoted), known selection bias, and one verified example
of use in building energy research or `NONE FOUND`. Of the 13 columns brief section 9 lists, roughly 7
are absent from every Table F1 row.

---

## 6. Dashes

Counted with `py` over the report file: em dash (U+2014) = 0. en dash (U+2013) = 0.

---

## 7. Rules

- Named individual connected to a fellowship programme: none found.
- Proposal to change the 4J gate: none found.
- Claim that the report itself was vetted or accepted: none found (Section G explicitly defers
  vetting, consistent with brief section 9 rule 7).
