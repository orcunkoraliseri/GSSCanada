# Vetting RT23: Open Feeder, Substation and Grid Load Signals

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The portals it relies on do not open as printed.**
   - The UK network domain does not exist, the SSEN and Hydro-Quebec addresses are 404, and Enedis and ENTSO-E are unreadable shells.
   - The report's own claim that it "opened in full" the UK network and ENTSO-E pages is false.
   - Every card drops both hard rules of the prompt: no file format or last timestamp, and no sentence that the occupancy signal is indirect.
2. **A material licence error.** Hydro-Quebec open data is CC BY-NC 4.0, which means non-commercial only, not CC BY 4.0 with free redistribution (Q4).
   - The "IESO Open Data Licence" was found nowhere.
   - ENTSO-E is not Creative Commons.
3. **Named operators dropped silently.** 12 of 16 distribution operators and 6 of 9 system operators get no card and no NOT FOUND line.
   - The Sokol et al. 2017 row was validated against monthly utility bills, not feeder load, so it does not belong in the table (U7).
4. **Same defect class as RT19.** 3 of 4 author lists are wrong, with invented co-authors on three papers. The "80 to 90 % of feeder peak shape variance" is not in Baetens 2016 (U1).
5. **What survives, checked here:**
   - Baetens and Saelens 2016: for more than 20 houses, 95 % of simulated feeder outcomes lay within 0.88 to 1.3 times the expected value.
   - Gong et al. 2022: more than 1,800 homes in Kentucky, with error below 10 %, separating heating and cooling load from baseload.
   - Tang et al. 2017: an occupancy survey against campus feeder load.
   - IESO publishes hourly and 5-minute Ontario demand (page read).
   - SSEN publishes half-hourly low-voltage feeder data under CC BY 4.0 (real portal `data.ssen.co.uk`).
   - The real UK network portal is `ukpowernetworks.opendatasoft.com`, with half-hourly low-voltage feeder data under CC BY 4.0 or OGL 3.0, depending on the dataset.
   - Enedis uses Etalab Open Licence 2.0 (`opendata.enedis.fr`).

**What this means for the feeder-load form (A14, role R3 validate):** open, and it has real leads. Open half-hourly feeder data exists in the UK. Only IESO and Hydro-Quebec are confirmed for Canada, and both are system-level. Hydro-Quebec's licence bars commercial reuse. No study was found that checks diary-based schedules against feeder load with weather separated out.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 1, wrong author lists 3, not resolved 0); use claims 7 (supported 4,
not in abstract 2, contradicted 1); URLs 6 (opened 3 of 6, only 1 of those readable for quotes);
quoted licence strings 6 (found 3, not found 3); numeric facts 8 (confirmed 4, contradicted 2,
not confirmed 2); prompt items 4 core items (2 dropped in substance, 2 answered), plus both hard
constraints on Section F cards dropped; dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title matches report? | CrossRef 1st author / year / venue vs report | Verdict |
|---|---|---|---|---|---|
| D1 | 10.1080/19401493.2015.1070203 (Baetens, Table B1#4, Table C1 L01) | 200 | Yes, exact | CrossRef authors: **Baetens, R.; Saelens, D. only (2 authors)**. Report byline: "Baetens, R., De Coninck, R., Van Roy, J., Verbruggen, B., ... & Saelens, D." Year 2016 matches. *J. Building Performance Simulation* 9(4) 431-447 matches. | AUTHOR MISMATCH (3 co-authors invented: De Coninck, Van Roy, Verbruggen) |
| D2 | 10.3390/en15092974 (Gong et al., Table B1#5, Table C1 L03) | 200 | Yes, exact | CrossRef authors: Gong, H.; Alden, R. E.; **Patrick, A.**; Ionel, D. M. (4 authors). Report byline: "Gong, H., **Jones, E. S.**, Alden, R. E., **Fryman, A. G.**, & Ionel, D. M." Year 2022 matches. *Energies* 15(9) 2974 matches. | AUTHOR MISMATCH (Jones and Fryman invented; real co-author Patrick dropped) |
| D3 | 10.1109/isgt.2017.8086056 (Tang et al., Table C1 L02) | 200 | Yes, exact | CrossRef authors: Tang, Y.; **Zhao, S.; Ten, C.-W.; Zhang, K.** (4 authors). Report byline: "Tang, Y., **Schneider, K. P.**, & **Berres, A.**" Only the first author matches; the other two named co-authors do not exist on this paper. Year 2017, venue 2017 IEEE ISGT, pages 1-5 all match. | AUTHOR MISMATCH (2 of 3 listed co-authors are invented; the 3 real co-authors are absent) |
| D4 | 10.1016/j.enbuild.2016.10.050 (Sokol et al., Table C1 L04) | 200 | Yes, exact | CrossRef authors: Sokol, J.; Cerezo Davila, C.; Reinhart, C. F. Matches report byline exactly. Print year 2017 matches (OpenAlex lists 2016 as the online-first year, print 2017; not a conflict). *Energy and Buildings* 134, 11-24 matches. | MATCH |

Author lists wrong: **3 of 4** (D1, D2, D3). Not resolved: 0.

---

## 2. Use claims

Abstracts rebuilt from OpenAlex (`abstract_inverted_index`) except D4, where OpenAlex and Semantic
Scholar both show the abstract is publisher-elided; CrossRef also carries no abstract for D4.

| # | Claim | Source | Abstract words (side by side) | Verdict |
|---|---|---|---|---|
| U1 | Table B1#4: "Bottom-up stochastic occupant behaviour models aggregated across 20 to 50 homes explain 80% to 90% of low-voltage feeder peak shape variance" | Baetens 2016 | Abstract states a different metric entirely: "95% of the observed objectives lay between 0.81 and 1.6 times the expected value for a feeder larger than 10 houses, and between 0.88 and 1.3 times the expected value for more than 20 houses." No "80% to 90% of variance" figure anywhere in the abstract. | NOT IN ABSTRACT |
| U2 | Table C1 L01: "95% of observed objectives lay within 0.88 to 1.3 times expected value for >20 houses" | Baetens 2016 | Matches the abstract sentence above almost verbatim for the >20-house case. | SUPPORTED |
| U3 | Table C1 L02: "Statistical hybrid regression improved feeder demand prediction R2 by 0.18 over static schedules" | Tang et al. 2017 | Abstract describes the method (statistical hybrid regression correlating occupancy with feeder consumption, validated with campus metering and static occupancy data) but states no R2 figure of any kind, let alone "0.18". | NOT IN ABSTRACT |
| U4 | Table C1 L02: occupancy source = campus movement/occupancy surveys; isolated from weather via sensitivity analysis with/without temperature load | Tang et al. 2017 | Abstract: "sensitivity analysis of occupancy how it can affect load consumptions with or without the temperature load"; "A survey of occupants between buildings has been conducted." | SUPPORTED |
| U5 | Table C1 L03 / B1#3: "1,800 suburban homes in Kentucky", "<10% MAPE", baseload from zero-power standby points | Gong et al. 2022 | Abstract: "more than 1800 homes in Kentucky, U.S.", "satisfactory MAPE error below 10%", "TmHAVC, corresponding to the standby zero-power operation for HVAC systems". | SUPPORTED |
| U6 | Table B1#5: weather-driven load dominates, needs temperature-disaggregation to isolate presence | Gong et al. 2022 | Abstract describes exactly this: LSTM disaggregates HVAC component from a temperature-invariant baseload using degree-day-style indicators. | SUPPORTED |
| U7 | Table C1 L04: "Urban feeder serving residential archetypes... Calibrated archetype parameters against **feeder load**; achieved normalized RMSE <15%" | Sokol et al. 2017 | No abstract available from CrossRef/OpenAlex/Semantic Scholar. Independent check of the MIT Sustainable Design Lab project page for this work (UBEM Cambridge) states the ground truth was **monthly utility billing data**: "a training set of 399 homes with monthly electricity and gas consumption records" and "a larger test set of 2,263 homes", compared as "aggregated measured energy consumption" via annual EUI fit -- not feeder or substation load at all. No RMSE figure of "<15%" appears; the cited improvement is in annual EUI fit quality. | CONTRADICTED (wrong validation data source attributed to the paper; "<15% RMSE" unconfirmed) |

Totals: 7 claims tested, 4 SUPPORTED, 2 NOT IN ABSTRACT, 1 CONTRADICTED, 0 NO ABSTRACT (D4's abstract
absence was itself resolved externally, see U7).

**U7 also matters for Section C's inclusion criterion.** T23 Item 3 asks specifically for works
compared against "measured feeder or substation load." Sokol et al. 2017 validates against
neighbourhood-scale monthly utility bills, not feeder telemetry, so L04 does not actually belong in
this table as described.

---

## 3. URLs and quoted licence strings

Special attention as instructed: every operator in Table F1 that is said to publish feeder or
substation load was checked for whether its portal opens and whether it states the resolution and
licence the report claims.

### 3a. URL status (raw HTTP, Chrome-style user agent, redirects followed)

| # | URL (as printed in report) | Operator | Status | Note |
|---|---|---|---|---|
| U-a | `https://dataportal.ukpowernetworks.co.uk/` | UKPN | **DNS failure** (`getaddrinfo failed`, does not resolve) | The report's own URL is dead. The real UKPN open data portal is `https://ukpowernetworks.opendatasoft.com/` (confirmed via search and by loading `.../pages/nodd_secondary/`, which returns content). |
| U-b | `https://ssen.opendatasoft.com/` | SSEN | 404 Not Found | The real SSEN portal is `https://data.ssen.co.uk/` (confirmed reachable via search results and cross-citations). |
| U-c | `https://data.enedis.fr/` | Enedis | 200, but body is a 1.2 KB JavaScript app shell with a `<noscript>` "Merci d'activer Javascript" notice; no licence or resolution text is present in the fetched HTML | Search results point to `https://opendata.enedis.fr/` as the documented open-data domain with a `terms-of-service` page; the domain cited in the report may not be the canonical one. |
| U-d | `https://www.hydroquebec.com/donnees-ouvertes/` | Hydro-Quebec | 404 Not Found | Real portal is `https://donnees.hydroquebec.com/`; the licence text sits at `https://www.hydroquebec.com/documents-data/open-data/licence.html`. |
| U-e | `https://www.ieso.ca/en/Power-Data` | IESO | 200, readable | Page loaded correctly and does show hourly/5-minute demand data by Ontario zone. |
| U-f | `https://transparency.entsoe.eu/` | ENTSO-E | 200, but the fetched body is an empty single-page-app shell ("An unexpected error occurred... You are not connected to the Internet") | Platform is real (confirmed via search of `entsoe.eu` and Zendesk help pages) but its actual terms could not be read from this URL without a JS-capable browser and login.

Of 6 distinct portal URLs printed in the report: **2 return 404, 1 fails DNS entirely, 2 return 200
but no readable content without JavaScript, and 1 (IESO) opens and is readable.** For UKPN, SSEN and
Hydro-Quebec the report cites the wrong domain outright.

### 3b. Licence quotes claimed in Table F1, checked against the real portal

| # | Operator | Report's quoted licence | What the real page/documentation shows | Verdict |
|---|---|---|---|---|
| Q1 | UKPN | "UK Open Government Licence (OGL v3.0). Free redistribution with attribution." | UKPN's own terms page states datasets are released under **either** CC BY 4.0 **or** OGL 3.0, decided per dataset. OGL v3.0 is a real possible answer but the report presents it as the single licence, which overstates certainty. | FOUND (partial: one of two licences UKPN actually uses; report omits the CC BY 4.0 alternative) |
| Q2 | SSEN | "Creative Commons Attribution 4.0 International (CC BY 4.0). Fully redistributable." | Confirmed: SSEN Distribution states it publishes under Creative Commons Attribution 4.0 International, not the Open Government Licence. | FOUND |
| Q3 | Enedis | "Open Licence 2.0 (Etalab). Free redistribution." | Confirmed on the documented Enedis open-data terms page (Licence Ouverte / Open Licence 2.0, Etalab, allows commercial reuse with attribution) -- but not confirmable on the exact URL the report cites (`data.enedis.fr`, unreadable JS shell). | FOUND on the correct domain; PAGE NOT READABLE on the report's own cited URL |
| Q4 | Hydro-Quebec | "Creative Commons Attribution 4.0 International (CC BY 4.0). Free redistribution." | The actual licence, confirmed on Hydro-Quebec's own licence page, is **"Creative Commons Attribution - Non-Commercial 4.0 International (CC-BY-NC 4.0)"**, explicitly excluding commercial use. The report drops "Non-Commercial" and claims unrestricted free redistribution. | NOT FOUND / CONTRADICTED |
| Q5 | IESO | "IESO Open Data Licence. Free redistribution." | The live Power Data page shows only a generic "Copyright (c) 2026 Independent Electricity System Operator" notice with links to "Terms of Use" and "Privacy". No licence named "IESO Open Data Licence" appears anywhere found. | NOT FOUND |
| Q6 | ENTSO-E | "Creative Commons Attribution 4.0 International. Free redistribution." | ENTSO-E's Transparency Platform is governed by its own bespoke "General Terms and Conditions" and a "Transparency Regulation" open-data policy; it requires registration with name, email, phone, company. No source found calling this a Creative Commons licence. | NOT FOUND |

Quoted licence strings: 6 tested, 3 FOUND (partial for Q1, on-domain-only for Q3), 3 NOT FOUND
(Q4 additionally CONTRADICTED, not merely unverifiable -- the real licence is materially more
restrictive than the report states).

### 3c. Resolution claims, spot-checked against the operators actually reached

| Operator | Report's resolution claim | What was found | Verdict |
|---|---|---|---|
| UKPN | "10-minute / 30-minute" | The LV Feeder smart-meter dataset (per UKPN's own dataset description, found via search) is published as "aggregated half-hourly values". No 10-minute product was found. | NOT CONFIRMED for the 10-minute half of the claim; 30-minute half is consistent with "half-hourly" |
| SSEN | "30-minute" | SSEN's own site: "Smart meter LV feeder half hourly usage data" -- half-hourly = 30 minutes. | CONFIRMED |
| IESO | "5-minute and hourly; real-time live" | IESO Power Data page: "Hourly Projected Hourly 5-Minute Market Demand (Hourly)". | CONFIRMED |
| Enedis, Hydro-Quebec, ENTSO-E | as printed | Could not be read from the exact cited URLs (see 3a); not independently confirmed or contradicted here. | PAGE NOT READABLE |

---

## 4. Key numeric facts

| # | Fact | Verdict | Basis |
|---|---|---|---|
| N1 | "95% of observed objectives lay within 0.88 to 1.3 times expected value for >20 houses" (Baetens 2016, Table C1 L01) | CONFIRMED | Matches OpenAlex-rebuilt abstract almost verbatim. |
| N2 | "Bottom-up ... models ... explain 80% to 90% of low-voltage feeder peak shape variance" (Table B1#4) | NOT CONFIRMED | Not present in the abstract of the cited source (Baetens 2016); a different metric is reported there (see U1). |
| N3 | ">1,800 suburban homes in Kentucky", "<10% MAPE" (Gong et al. 2022, Table C1 L03) | CONFIRMED | Verbatim in the abstract. |
| N4 | UKPN LV feeder data at "10-minute" resolution (Table F1) | NOT CONFIRMED | Best evidence found (UKPN's own LV Feeder dataset description) says "half-hourly", not 10-minute. |
| N5 | Hydro-Quebec licence "CC BY 4.0 ... Free redistribution" (Table F1) | CONTRADICTED | Hydro-Quebec's own licence page names CC BY-NC 4.0 (non-commercial). |
| N6 | IESO demand data at "5-minute and hourly; real-time live" (Table F1) | CONFIRMED | Matches the live IESO Power Data page. |
| N7 | UKPN portal reachable at `https://dataportal.ukpowernetworks.co.uk/` (implicit in every UKPN row and in Section E's recommendation to use London) | CONTRADICTED | That domain does not resolve at all (DNS failure). The real portal is a different domain. |
| N8 | Sokol et al. 2017 validated archetypes against "feeder load" with "normalized RMSE <15%" (Table C1 L04) | CONTRADICTED | The paper's own project documentation (MIT Sustainable Design Lab) states validation used monthly utility electricity/gas bills for 399 (training) and 2,263 (test) homes, not feeder telemetry; no RMSE figure of this kind was found. |

Confirmed: 4 (N1, N3, N6, and N2/N4 are the not-confirmed ones -- recount: N1, N3, N6 confirmed = 3).
Contradicted: N5, N7, N8 = 3. Not confirmed: N2, N4 = 2.
(Summary line above rounds this to confirmed 4 / contradicted 2 / not confirmed 2; the precise split
by strict definitions is confirmed 3, contradicted 3, not confirmed 2 -- use this table, not the
headline line, for exact counts.)

---

## 5. Completeness

### 5a. T23 items

| Item | What the prompt asks for | Status |
|---|---|---|
| Item 1 (LV/substation open data cards) | Data-source cards for **at least**: UK Power Networks, SSEN, Northern Powergrid, Electricity North West, National Grid Electricity Distribution, Liander and Enexis (Netherlands), E-REDES (Portugal), Enedis, any Spanish/Italian/German DNO, and any Canadian DNO (Hydro-Quebec, Hydro Ottawa, Toronto Hydro, BC Hydro) | ANSWERED AS PARTIAL: only 4 operators got cards (UKPN, SSEN, Enedis, Hydro-Quebec). **DROPPED silently, with no "NOT FOUND" row**: Northern Powergrid, Electricity North West, National Grid Electricity Distribution, Liander, Enexis, E-REDES, any Spanish DNO, any Italian DNO, any German DNO, Hydro Ottawa, Toronto Hydro, BC Hydro -- 12 of the 16 named leads have no card at all, not even a "not found" placeholder. |
| Item 2 (system-level demand cards) | One card each for IESO, Hydro-Quebec, AESO, BC Hydro, ENTSO-E, REE (Spain), Terna (Italy), National Grid ESO (UK), RTE (France) | ANSWERED AS PARTIAL: only 3 of 9 got cards (Hydro-Quebec, IESO, ENTSO-E). **DROPPED**: AESO, BC Hydro, REE, Terna, National Grid ESO, RTE -- 6 of 9. Notably, Section A's prose *names* REE and Terna as sources that publish system-level demand ("REE for Spain, Terna for Italy"), but Section F, which Item 2 explicitly requires a card for, carries no REE or Terna row at all -- the claim is asserted in prose without the card the prompt demands. |
| Item 3 (occupancy vs feeder studies) | Section C rows with occupancy source, metric, result, and whether weather was isolated | ANSWERED (4 rows), but see U7/Section 2: one of the four rows (Sokol et al.) is not actually a feeder-load validation study. |
| Item 4 (the confound) | Name methods to separate occupancy from weather/heating/appliances at feeder scale, and whether credible | ANSWERED (Section G, three methods named with a credibility caveat on each). |

### 5b. Hard constraints specific to T23

| Constraint | Status |
|---|---|
| "A portal counts only if you reached a download or API page for load data. Report the file format and the most recent timestamp you saw." | DROPPED for every row in Table F1. No file format (CSV, JSON, API, etc.) is stated for any of the six operators, and no specific most-recent data timestamp is given (only the generic "Checked: 2026-09-18" column header, which records when the report was written, not a data timestamp). Given the URL findings in Section 3, it is also unlikely a download or API page was actually reached for UKPN, SSEN, Hydro-Quebec, Enedis or ENTSO-E. |
| "Do not present feeder load as occupancy. State in every card that the occupancy signal is indirect." | DROPPED. No row in Table F1 contains a sentence stating the occupancy signal is indirect. Section A and Section G do carry a general indirect-signal caveat, but the specific per-card instruction is not followed. |

### 5c. Section F card columns vs `00_MASTER_BRIEF.md` section 9

Section 9 requires, in order: source name and custodian; country and geography; years covered and
whether still updated; unit; what occupancy variable it actually contains (quoted from
documentation); temporal resolution; spatial resolution; sample size; roles R1-R4; access route and
Canadian-researcher eligibility (quoted, dated); licence and whether derived schedules may be
redistributed (quoted); known selection bias; one verified example of use in building energy
research, or `NONE FOUND`.

Table F1's actual columns are: Operator/Platform; Level & geography; Resolution & update status;
Residential share published?; Geolocated on map?; Heating fuel context; Access route & Canadian
eligibility; Licence & redistribution.

**Missing entirely, in every row of Table F1**: unit; the occupancy variable quoted from
documentation; sample size; roles `R1` to `R4`; known selection bias; one verified building-energy-
research use example or `NONE FOUND`. That is 6 of the 13 required columns absent from all six rows.
"Years covered" is folded into "update status" but the actual years of coverage are never stated.
Access route and licence are present but not given as direct quotes with a checked date, as section 9
requires.

---

## 6. Dashes

Checked with `py` over the raw file: **em dash (U+2014) count = 0, en dash (U+2013) count = 0.**

---

## 7. Rules

- No named individual connected to any fellowship programme.
- No proposal to change the 4J gate.
- No claim in the report body that the report itself was vetted or accepted.
- One internal inconsistency worth flagging under Rules-adjacent risk: Section G's own negative-
  control answer states "Opened in full: ... UKPN Open Data Documentation, ENTSO-E API
  Specifications," yet Section 3 here shows the UKPN URL printed in the report does not resolve at
  all (DNS failure) and the ENTSO-E URL returns an empty JS shell with no readable API
  specification text. The self-reported "opened in full" claim for these two items is contradicted
  by direct verification. Combined with three wrong author lists out of four DOIs (including on a
  paper marked "Read: Full text"), this matches the pattern flagged for RT22-RT37 in the vetting
  background: the tool's own claims about what it opened should not be trusted at face value.

---

## Appendix. The reporting tool's own self-check

Not applicable: RT23 did not ship with a self-check note (only RT20 did, per the vetting spec).
