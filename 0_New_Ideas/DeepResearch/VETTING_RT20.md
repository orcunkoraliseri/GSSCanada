# Vetting RT20: smart_thermostat_presence_data (round 2)

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-19).

Rule applied to all six round-2 reports: a row survives only if this checker confirmed it at its
source; a row that is contradicted, or whose quote or fact has no log line, is struck. A log line
written after the text was composed does not count as reading; only the checker's own re-fetch does.

1. **Kept:**
   - All six DOI rows (section 1): Doma, Prajapati, Ouf 2024; Jung, Wang, Hong, Jazizadeh 2023;
     Huchuk, Sanner, O'Brien 2019; Pritoni, Woolley, Modera 2016; Stopps, Touchie 2019; Pang et al.
     2025. Rows 3, 4 and 6 are identity only (no abstract, U3, U4, U6).
   - Doma et al. 2024: over 8,000 Canadian homes, 3 % difference in daily occupied hours against the
     Canadian time-use survey (U1, key numbers 1 and 2).
   - Jung et al. 2023: 104,693 thermostats, 91,747 in the US, 48 countries; house-type counts with
     49,593 detached, about 62 % of classified homes; the vendor definitions of motion and "Smart
     home"; the "Sleep" schedule filling night-time false vacancy (U2, U7 to U9, quotes 1 to 5 and 9).
   - Card 1 access route: the ecobee "Are you a scientist or researcher" text is on the live page
     (quote 6). Nothing else in card 1's access and licence cells survives (see struck).
   - Cards 2 and 3: Google Nest and Resideo have no bulk research programme on their developer
     portals, kept as NOT FOUND (section 11).
   - Card 4: the Hydro-Québec demand-response file, CC BY-NC 4.0, 64,605 rows, no presence or motion
     field. Its quoted field list is **truncated** (6 of 12 items, quote 7); the full list is in the
     VETTING_RT23 addendum. Same file as RT23's LCPR.
   - Card 6: Dryad 0 hits and Figshare 0 relevant hits (key numbers 7, 8); Zenodo blocked with 403.
2. **Struck:**
   - The "403 Forbidden" on Concordia Spectrum and the "Cloudflare 403" on ScienceDirect (defects 1
     and 2): the log shows HTTP 200 and a timeout, and no ScienceDirect fetch at all.
   - The `COULD NOT OPEN` answer to the Doma question (defect 3). Answered instead by VETTING_RT32's
     kept row: hourly in aggregate, no split by household or dwelling type, arrival and departure
     times left to future work.
   - Card 1's licence and redistribution cell (key number 10, defect 5). The brief's hard constraint
     asked for it quoted from the programme's page; no such text is there.
   - Section G's claim that ecobee holds only floor area, age and storeys (section 11, defect 4):
     contradicted by Jung et al. 2023 Table 1, which lists "Number of occupants", entered by the user.
   - Card 5 (Texas): "Mueller community" and "over 10,000 enrolled homes" (no page behind either,
     section 7). Card 6's "Open web search" access cell (line 153). NREL OEDI "0 submissions" (not
     verifiable). "Split incentive" (no log line). "No study reweighted DYD to census marginals" (no
     query logged, section 11).
3. **Not answered:** the named leads (NRCan, the two journals, BuildSys, e-Energy) have no heading
   and no search (section 10). Sarran et al. 2021 is correct in CrossRef but was never made a row.
4. **Runner rules.** Written directly, not by a script. One log line (the Hydro-Québec zip) came 11
   seconds after the text was composed; it supports only the URL cell, which this check re-fetched.
   No dashes, no gate proposal, no named individual, no self-written verdict.

**What this means for the thermostat-presence form (A14, role R1 generate):** narrowed. Building
occupancy schedules from ecobee thermostats already exist for Canada (Doma et al. 2024, 8,000 homes,
checked against the time-use survey) and for the US (Jung et al. 2023), so the bare form is done.
The open part matches the diary-bias form's: splits by household and dwelling type, arrival and
departure times, and matching the thermostat homes to the Canadian population. The "Number of
occupants" field makes a household-size match possible; whether anyone has reweighted the data to the
census is unassessed. Access: ecobee has a researcher route, but its licence terms are unread; the
author reads the agreement before relying on it. Selection bias toward detached homes (62 %) is
measured in the US sample only.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 6 (MATCH 6, author mismatch 0, other mismatch 0, not resolved 0); use claims 10
(supported 6, not in abstract 0, contradicted 0, no abstract 4); URLs in report 9 (in log 9, not in
log 0; fetched 9, content confirmed 7, partially confirmed 2); log excerpts re-checked 18 (found 15,
not found 0, unreachable/JS-rendered 3); quoted strings 10 (found 9, not found 0, no log line 1);
unlogged-source claims 1 strict (plus 2 borderline, see section 7); log lines after compose time 1;
key numbers 10 (confirmed 8, contradicted 0, not confirmed 2); prompt items 12 (carded 10, partial 1,
not answered despite being reachable 1); dashes em 0, en 0.

## 1. DOIs (6 unique)

Every DOI in the report resolves, and CrossRef's title, full author list, year, volume and page match
the report's table row exactly. No invented, split, dropped or merged author names found (contrast
with round 1, where 6 of 9 rows had wrong author lists).

| # | DOI | HTTP | CrossRef title (80 ch) | CrossRef authors | Report authors | Year | Vol | Page | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10.1016/j.buildenv.2024.111713 | 200 | Developing a residential occupancy schedule generator based on smart thermostat | Doma, Prajapati, Ouf (3) | Doma, Prajapati, Ouf | 2024 | 261 | 111713 | MATCH |
| 2 | 10.1016/j.buildenv.2023.110628 | 200 | Smart thermostat data-driven U.S. residential occupancy schedules and developmen | Jung, Wang, Hong, Jazizadeh (4) | Jung, Wang, Hong, Jazizadeh | 2023 | 243 | 110628 | MATCH |
| 3 | 10.1016/j.buildenv.2019.106177 | 200 | Comparison of machine learning models for occupancy prediction in residential b | Huchuk, Sanner, O'Brien (3) | Huchuk, Sanner, O'Brien | 2019 | 160 | 106177 | MATCH |
| 4 | 10.1016/j.enbuild.2016.05.024 | 200 | Do occupancy-responsive learning thermostats save energy? A field study in univ | Pritoni, Woolley, Modera (3) | Pritoni, Woolley, Modera | 2016 | 127 | 469-478 | MATCH |
| 5 | 10.1088/1757-899X/609/6/062013 | 200 | Reduction of HVAC system runtime due to occupancy-controlled smart thermostats | Stopps, Touchie (2) | Stopps, Touchie | 2019 | 609 | 062013 | MATCH |
| 6 | 10.1016/j.enbuild.2024.115161 | 200 | Long-Term field testing of the accuracy and HVAC energy savings potential of oc | Pang, Guo, O'Neill, Smith-Cortez, Yang, Liu, Dong (7) | Pang, Guo, O'Neill, Smith-Cortez, Yang, Liu, Dong | 2025 (CrossRef `published-print`) | 328 | 115161 | MATCH |

Row 6 note: the DOI string embeds "2024" (the year the article record was created online,
2024-12-09) but CrossRef's `published-print`/`issued` date is 2025-02; the report's "2025" citation
matches CrossRef's citable year, not the DOI substring. Not a mismatch.

One additional DOI is used in prose (Card 5, "Sarran et al. (2021, Energy Policy 153, 112290)") but
is never placed in a DOI table row and never appears in the Section H reference list, so it is
outside the scope of the corrections block's "every DOI in every table row" rule. CrossRef confirms
it: title "A data-driven study of thermostat overrides during demand response events", authors
Sarran, Gunay, O'Brien, Hviid, Rode (5), vol 153, page 112290 — consistent with the report's one-line
mention, but not admitted as a proper row per the corrections block's own rule.

## 2. Use claims

| # | Claim (location) | Check | Verdict |
|---|---|---|---|
| U1 | Doma et al. 2024: OSG package validated against Canadian TUS, quote block (Sec. C row 1) | OpenAlex abstract: "The package takes advantage of the Donate Your Data (DYD) dataset by Ecobee to develop a rule-based framework that addresses the limitations of relying on motion-detection data to represent the whole-building occupancy. The framework was applied to over 8,000 Canadian households as a case study." | SUPPORTED, quote verbatim |
| U2 | Jung et al. 2023: K-means clustering, day/house-type/state, ROSS, "over 90,000" quote (Sec. C row 2) | Full text (eScholarship PDF, p.1): "Over 90,000 residential occupancy schedules were estimated from the ecobee Donate Your Data dataset... This study further investigated the impacts of three parameters (day, house type, and state)..." | SUPPORTED, quote verbatim |
| U3 | Huchuk et al. 2019: ML models, Random Forest matching/outperforming, >10,000 thermostats (Sec. C row 3) | CrossRef and OpenAlex both return no abstract for this DOI | NO ABSTRACT |
| U4 | Pritoni et al. 2016: field study, university residence halls, energy savings (Sec. C row 4) | CrossRef and OpenAlex both return no abstract | NO ABSTRACT |
| U5 | Stopps & Touchie 2019: HVAC runtime reductions, Toronto MURB suites, remote occupancy sensors (Sec. C row 5) | OpenAlex abstract: "Field data were collected from 56 thermostats installed in two condominium buildings located in Toronto, Canada... an average reduction in suite HVAC system runtime of 17% was found." | SUPPORTED |
| U6 | Pang et al. 2025: long-term field test, false negative errors, single-family home (Sec. C row 6, Sec. B row 14, Sec. G item 3) | CrossRef and OpenAlex both return no abstract | NO ABSTRACT |
| U7 | ecobee DYD scale, "104,693... 91,747 US... 48 countries" (Sec. B row 2) | Jung et al. full text p.6: "A total of 104,693 ecobee thermostats data were shared with the authors. The majority of the data (91,747 ecobee thermostats) were collected in the U.S. (a total of 48 countries included)" | SUPPORTED, verbatim numbers |
| U8 | Single-family bias, "49,593 detached... 3,060 apartments... 3,252 condominiums" (Sec. B row 13, Sec. G item 4) | Jung et al. full text p.6: "Apartment (3,060), condominium (3,252), detached (49,593), loft (350), multiplex (1,325), rowhouse (3,214), semi-detached (965), and townhouse (6,231)" | SUPPORTED, verbatim numbers |
| U9 | "Sleep" schedule used to override night-time false vacancy (Sec. G item 3, attributed to Jung et al. 2023) | Jung et al. full text: motion feature "known for having false negative cases (reporting vacancy while the house is occupied)"; later text relies on the user-set "Sleep" schedule to fill in nocturnal occupancy | SUPPORTED |
| U10 | Sarran et al. 2021: "evaluated thermostat overrides during demand response" (Card 5) | CrossRef/OpenAlex title "A data-driven study of thermostat overrides during demand response events"; no abstract available at either source | NO ABSTRACT (title-level match only, no full check possible) |

## 3. Study type (Section C)

All 6 Section C rows are tagged `[results]`. Checked against abstract/full text: all six are indeed
empirical/results papers (field studies or data-driven analyses), none is a protocol or review. No
mismatch found.

## 4. URLs

9 unique URLs appear in the report body. All 9 have a matching log line (in log: 9/9, none missing).

| URL | In log? | Fetched now | HTTP now | Claimed content on page? |
|---|---|---|---|---|
| https://www.ecobee.com/en-ca/donate-your-data/ | yes (lines 11,12,14) | yes | 200 | Access-route quote CONFIRMED verbatim; licence/redistribution claim NOT on page (see section 9) |
| https://developer.honeywellhome.com/ | yes (line 38) | yes | 200 | CONFIRMED: no "research"/"academic"/"dataset" text anywhere on page |
| https://developers.google.com/nest/device-access | yes (line 39) | yes | 200 | CONFIRMED: no "research"/"academic"/"dataset" text anywhere on page |
| https://www.pecanstreet.org/dataport/ | yes (line 40) | yes | 200 | Research/paid-access framing CONFIRMED; "Mueller community" detail NOT on this page |
| https://donnees.hydroquebec.com/api/v2/catalog/datasets?search=thermostat | yes (lines 29,30) | yes | 200 | CONFIRMED: field list, licence "CC BY-NC 4.0", 64,605 records all match |
| https://donnees.solutions.hydroquebec.com/.../do_LCPR_fr.csv.zip | yes (line 50) | yes | 200 | CONFIRMED reachable, binary zip |
| https://escholarship.org/content/qt4wd5w010/qt4wd5w010.pdf | yes (lines 24-27) | yes | 200, 2,259,137 bytes (byte-identical to log) | CONFIRMED: every quoted number and vendor-definition string traced to this PDF |
| https://data.openei.org/submissions?q=thermostat | yes (lines 35,36) | yes | 200 | NOT CONFIRMED: page is a JavaScript app; the results table is populated by client-side code, so the static HTML (matching the logged excerpt) never shows a result count either way. The report's "0 submissions" cannot be verified or refuted from this page. |
| https://austinenergy.com/powerpartner | yes (line 42, logged as ERR) | yes | now 200 (173 KB) via this session's fetch | Log-consistent: the report's own attempt failed (ERR), which the report accurately states. A later, independent fetch in this check succeeded, meaning the failure was transient/environment-specific, not a broken URL. |

## 5. Log excerpt re-check (18 lines checked, spread across the full 22:48:20-22:56:22 span)

| Line | Time | URL | Re-fetch result | Excerpt match |
|---|---|---|---|---|
| 1 | 22:48:20 | api.crossref.org (Doma DOI) | 200, same JSON preamble | FOUND |
| 4 | 22:48:39 | doi.org/10.1016/j.buildenv.2024.111713 | 200, "Redirecting" | FOUND |
| 7 | 22:48:50 | api.elsevier.com/content/article/PII:... | 400, "INVALID_INPUT..." | FOUND (confirms this call failed with 400, not 403) |
| 9 | 22:49:43 | spectrum.library.concordia.ca/996045/ | 200, same title text | FOUND |
| 10 | 22:50:05 | spectrum.library.concordia.ca/996045/ (retry) | log says ERR/timeout | reproducible pattern: intermittent, but a later fetch (this check) got 200 with full content, including a PDF (see section 9) |
| 11 | 22:50:24 | ecobee.com/en-ca/donate-your-data/ | 200, same nav text (after stripping `<script>`/`<style>`, matches exactly) | FOUND |
| 24 | 22:51:38 | escholarship.org/.../qt4wd5w010.pdf | 200, byte-identical (2,259,137 bytes) | FOUND |
| 28 | 22:52:57 | d3m.mie.utoronto.ca/publications/ | 200, same text | FOUND |
| 29 | 22:53:39 | donnees.hydroquebec.com catalog API | 200, same JSON | FOUND |
| 33 | 22:54:00 | api.figshare.com articles search | 200, same 5 items (all irrelevant to the topic) | FOUND |
| 35 | 22:54:06 | data.openei.org/submissions | 200, same shell text | FOUND (but is a JS shell, see section 4) |
| 38 | 22:54:18 | developer.honeywellhome.com | 200, same text | FOUND |
| 39 | 22:54:22 | developers.google.com/nest/device-access | 200, same text | FOUND |
| 40 | 22:54:26 | pecanstreet.org/dataport/ | 200, same text | FOUND |
| 41-42 | 22:54:39-48 | austinenergy.com (2 URLs) | log: ERR (DNS failure) both times | UNREACHABLE at the time logged; one of the two now resolves (see section 4) |
| 50 | 22:56:22 | donnees.solutions.hydroquebec.com .../do_LCPR_fr.csv.zip | 200, same byte count (2,535,975 bytes) | FOUND |

No excerpt failed to match a fetched page. The log is internally consistent with what the pages
actually contain.

## 6. Quoted strings (10 sourced quotes found in the report text)

| # | Quoted string (location) | Attributed to | Log line | On that page? |
|---|---|---|---|---|
| 1 | "Smart home is when... two hours." (Table B row 7) | Jung et al. 2023, Table 2 | line 24-27 (PDF) | FOUND, verbatim |
| 2 | "The package takes advantage of the Donate Your Data (DYD)... case study." (Sec. C row 1) | Doma et al. 2024 abstract | line 3 (OpenAlex) | FOUND, verbatim |
| 3 | "Over 90,000 residential occupancy schedules were estimated..." (Sec. C row 2) | Jung et al. 2023 full text | line 24-27 (PDF) | FOUND, verbatim |
| 4 | "Motion data sensed by the Passive InfraRed (PIR) sensors..." (Card 1) | Jung et al. 2023, Table 2 | line 24-27 (PDF) | FOUND, verbatim |
| 5 | "Smart home is when... two hours." (Card 1, repeat of #1) | Jung et al. 2023, Table 2 | line 24-27 (PDF) | FOUND, verbatim |
| 6 | "Are you a scientist or researcher... available to the public?" (Card 1, access route) | ecobee DYD page | line 11 | FOUND, verbatim (confirmed by this check's own re-fetch) |
| 7 | "Hourly consumption per substation, Average inside temperature... Presence of demand response events" (Card 4) | Hydro-Quebec catalog metadata | line 29,30 | FOUND, but a TRUNCATED quote: the source's bulleted list has 12 items (also Calendar data, Air temperature, Wind speed, Solar radiance, Relative humidity, Snow precipitation); the report reproduces only the first 6, presented as if the list ends there, with no ellipsis |
| 8 | "CC BY-NC 4.0" (Card 4 licence) | Hydro-Quebec catalog metadata | line 29,30 | FOUND, verbatim (`license` field) |
| 9 | "Sleep" (Sec. G item 3) | Jung et al. 2023, Table 2 "Schedule" feature | line 24-27 (PDF) | FOUND (the source names a "Sleep" schedule state) |
| 10 | "split incentive" (Sec. G item 4) | not attributed to any URL or DOI | none | NO LOG LINE |

## 7. Unlogged sources

Strict match to the check's definition (source is literally "open web search", "search", or a URL
absent from the log):

- Line 153 (Card 6, access route cell): "Access route and eligibility for a researcher at a Canadian
  university: **Open web search**; date checked 2026-09-18." This is the one explicit "open web
  search" citation in the report.

Two borderline cases, cited to a logged URL but stating content that page does not carry:

- Card 5 (line 137): "Known selection bias: Pecan Street sample is concentrated in Mueller community,
  Austin TX (high-income, solar/EV adopters)." Attributed implicitly to the logged
  pecanstreet.org/dataport/ page (line 40), but "Mueller" does not appear anywhere on that page as
  fetched (by the tool or by this check).
- Card 5 (line 133): "Austin Energy Power Partner enrolled homes (>10,000)." Both Austin Energy URLs
  in the log returned `ERR` (lines 41, 42); no page behind this figure ever loaded.
- Card 1 (line 64): the licence/redistribution sentence is presented as fact with no quote marks,
  attributed to the ecobee DYD page, but no licence, redistribution or agreement text of any kind is
  on that page (see section 9).

## 8. Timing

Log: 50 lines, first `2026-09-18T22:48:20`, last `2026-09-18T22:56:22` (span 8 min 2 s). Maximum
lines in any 60-second window: 13, starting at `22:54:16` (a burst of repository/vendor-portal
fetches, all distinct URLs, not repeats). Report text composed `22:56:11`; report file written
`22:56:47`.

Log lines timestamped after the compose time (`22:56:11`): **1**.
- `22:56:22` `https://donnees.solutions.hydroquebec.com/donnees-ouvertes/data/zip/do_LCPR_fr.csv.zip`
  (the raw Hydro-Quebec data file). This page was opened 11 seconds after the report text was
  composed, and 25 seconds before the report file was written. It supports only the "Direct URL" and
  "Confirmed reachable" cells of Card 4, both of which merely restate the URL and its status, not a
  quote or number that could have been affected by opening it late.

By contrast with round 1 ("sixteen reports in about nine minutes without opening a page"), this
report's 50 log lines are spread across 8 minutes and almost all precede the compose time.

## 9. Key numbers

| # | Number | Verdict | Source checked |
|---|---|---|---|
| 1 | Over 8,000 Canadian households (Doma et al. 2024) | CONFIRMED | OpenAlex abstract |
| 2 | 3% difference in aggregated daily occupied hours (Doma et al. 2024) | CONFIRMED | OpenAlex abstract; also Doma's PhD thesis (Concordia Spectrum, eprint 996045, p.44): "The TUS reported the mean daily occupied percentage in Canadian households as 71%, while the generated profiles by the OSG package reported it at 68%" |
| 3 | 104,693 total ecobee thermostats / 91,747 in the US / 48 countries (Jung et al. 2023) | CONFIRMED | Full text p.6, verbatim |
| 4 | 49,593 detached homes of ~80,000 classified dwellings, "over 60%" (Jung et al. 2023) | CONFIRMED | Full text p.6: named house-type counts sum to 67,990 (79,611 including the excluded "other" category); 49,593/79,611 = 62.3%, consistent with "over 60%" and "~80,000" |
| 5 | 64,605 records, Hydro-Quebec demand-response dataset | CONFIRMED | Catalog API `records_count: 64605` |
| 6 | Licence "CC BY-NC 4.0", Hydro-Quebec dataset | CONFIRMED | Catalog API `license: "CC BY-NC 4.0"` |
| 7 | Dryad search "0 hits" | CONFIRMED | Re-run query: `{"count": 0, "total": 0}` |
| 8 | Figshare search "0 relevant hits" | CONFIRMED as worded | Re-run query returns 5 items, none topically relevant (a calibration paper, a Twitter dataset, a health-workforce model, a mouse-imaging dataset, an earthquake dataset); report correctly says "0 relevant", not "0 total" |
| 9 | NREL OEDI "0 submissions" | NOT CONFIRMED | The submissions page is a JavaScript single-page app; the results table is not present in the static HTML either now or as logged, so this count cannot be verified or refuted from the page itself |
| 10 | ecobee DYD licence: "Proprietary research agreement; raw microdata cannot be redistributed; derived aggregate schedules... may be published open access" | NOT CONFIRMED | No licence, redistribution, fee, turnaround or agreement text of any kind appears anywhere on the logged/re-fetched ecobee DYD page |

## 10. Prompt items (including the corrections block)

| Item | Status |
|---|---|
| 1.1 ecobee DYD, full card | CARDED (Card 1) |
| 1.2 Google Nest | CARDED (Card 2, `NOT FOUND`, logged) |
| 1.2 Honeywell Resideo (corrections: "gets its own card") | CARDED (Card 3, `NOT FOUND`, logged) |
| 1.3 Quebec demand-response programme (corrections: "card or NOT FOUND") | CARDED (Card 4) |
| 1.3 Texas demand-response programme (corrections: "card or NOT FOUND") | CARDED (Card 5) |
| 1.4 Zenodo, Dryad, Figshare, NREL OEDI (corrections: "each searched with the query logged") | CARDED (Card 6, all four queries logged) |
| Item 2 (2016-2026 works using thermostat data) | CARDED (Section C, 6 rows) |
| Item 3 (what the sensor misses) | CARDED (Section G item 3) |
| Item 4 (selection bias) | CARDED, but with a factual gap: see section 9 row 10 and below |
| Corrections item 2 (does Doma et al. 2024 go beyond total daily occupied hours?) | Report answers `COULD NOT OPEN`. This is not accurate: the underlying study text is reachable. Doma's PhD thesis (Spectrum eprint 996045), which reproduces this exact paper as Chapter 3 ("OCCUPANCY SCHEDULE GENERATOR (OSG) FOR RESIDENTIAL BUILDINGS BASED ON SMART THERMOSTAT DATASET", citing Building and Environment 261, 111713 by name on its reference-list page), opened at HTTP 200 in this check, including its PDF. Chapter 3 (thesis p.41-42) states the comparison uses "the Mann-Whitney U (MWU) test... to investigate the difference in the hourly occupancy probabilities estimated by the developed OSG package and the Canadian TUS" — an hourly-profile comparison, not only a single daily total. The thesis's own Conclusion (p.49-50) states: "future works will focus on updating the developed package to add descriptive analysis to the generated occupancy profiles, such as daily arrival and departure times" and "while socio-demographic information regarding occupants is not available in the DYD dataset, future work can look into integrating the DYD dataset with other data sources" — i.e., breakdowns by household/dwelling type and first-departure/last-return times are explicitly named as **not done**, reserved for future work. |
| Item 1's household-metadata sub-ask (floor area, age of home, **number of occupants**, province or postal region) | PARTIAL: Card 1 covers geography ("City and province/state"); floor area and age of home are named only once, in Section G's selection-bias paragraph, not in Card 1 itself; "number of occupants" is never mentioned anywhere in the report, despite being field #11 in the metadata table of the one source (Jung et al. 2023, full text, Table 1) that the report says it read in full |
| Named leads: NRCan, *Journal of Building Performance Simulation*, *Applied Energy*, BuildSys, e-Energy | Not mentioned anywhere in the report; no heading, no `NOT FOUND`, no search logged for any of them |

## 11. Negative claims

| Claim | Log support |
|---|---|
| "Honeywell Resideo and Google Nest maintain no academic research donation programs" | Supported by fetches of both developer portals (lines 38, 39), reproduced in this check: neither page contains "research", "academic" or "dataset" text |
| Hydro-Quebec dataset "zero household-level presence or motion variables" | Supported by the catalog API field list (lines 29, 30): no motion/occupancy field present |
| "Zero open microdata sets on Dryad (0 hits)" | Query logged (line 32), count 0 confirmed by re-run |
| Figshare "0 relevant hits" | Query logged (line 33), confirmed |
| Zenodo "blocked automated search with HTTP 403" | Logged (lines 31, 37), confirmed reproducible |
| NREL OEDI "0 submissions" | Query logged (lines 34, 35, 36) but the results table is client-side rendered; no static count is visible in the logged or re-fetched page (see section 9) |
| "No identified study has successfully reweighted the full ecobee DYD dataset to national census marginals" | NONE LOGGED: the only related search in the log is a generic OpenAlex query `search=ecobee occupancy` (line 43, 156 hits); no query targeting "reweight", "raking" or "census" terms appears in the log |
| "Number of occupants" is not part of ecobee's collected metadata (implied by Sec. G item 4's claim that only floor area/age/storeys are available) | CONTRADICTED by the report's own full-text source: Jung et al. 2023 Table 1, field 11, is literally "Number of occupants... inputted by the user" |

## 12. Our own work

One row references project assets (Section D, A14 row): "Canadian GSS time-use pipeline (1J, 2J),
OpenUBEM dwelling-level archetypes, validation discipline." This names assets by category only; it
states no result, number, accuracy figure or outcome belonging to the project's own papers or engine.
Consistent with brief section 3's description; no invented figure found.

## 13. Rule breaches

- Em dashes (U+2014): 0 in report, 0 in log. En dashes (U+2013): 0 in report, 0 in log.
- No named individual is connected to a fellowship programme anywhere in the report.
- No proposal to change the 4J pre-registered gate, null or threshold appears.
- No self-grading language ("ACCEPTED", "VERDICT", or similar) appears in the report file itself
  (contrast with round 1, where the tool wrote its own `VERDICT: ACCEPTED` inside a forbidden second
  file). This report contains only one file, as instructed.

## 14. The five most serious defects found (facts, one line each, no verdict words)

1. The report states twice (Section B row 5, and the "Answers to Mandatory Questions" section) that
   Concordia Spectrum eprint 996045 returned "403 Forbidden." The log records no 403 for this eprint
   anywhere: line 9 shows the same URL returning HTTP 200 with readable content, and line 10 shows a
   connection **timeout** on a retry (`ERR: urlopen error timed out`), not a 403. This check's own
   re-fetch of both the record page and its PDF (a related document, Aya Doma's PhD thesis, which
   reproduces the Building and Environment 2024 paper as Chapter 3) returned HTTP 200 in both cases.
2. The report states "full text behind Cloudflare 403 on ScienceDirect," but no ScienceDirect or
   `linkinghub.elsevier.com` URL appears anywhere in the log. The only related log lines are the
   `doi.org` redirect (line 4, HTTP 200) and a separate Elsevier API call (line 7, HTTP 400,
   `INVALID_INPUT`, a malformed request, not a Cloudflare block).
3. Because of defects 1-2, the report answers the corrections block's Item 2 question ("does the
   Doma et al. comparison go beyond total daily occupied hours?") with `COULD NOT OPEN`, when a
   reachable, readable source (the PhD thesis reproducing the same study) answers it directly: the
   comparison does reach hourly occupancy-probability profiles via a Mann-Whitney U test, but
   explicitly does **not** break out by household/dwelling type or by first departure/last return,
   naming both as future work.
4. Section G's selection-bias discussion states that only "floor area, age of home, number of
   storeys" are available as dwelling metadata and that "household-level demographic microdata... are
   not collected by ecobee," while the report's own full-text source (Jung et al. 2023, Table 1)
   lists "Number of occupants" as a collected metadata field; the report never mentions this field,
   despite the prompt explicitly asking for it.
5. Card 1's licence and redistribution statement for ecobee DYD ("Proprietary research agreement;
   raw microdata cannot be redistributed; derived aggregate schedules... may be published open
   access") is presented as fact but is not quoted, and no licence, redistribution, fee, turnaround or
   agreement text of any kind is on the logged or re-fetched ecobee DYD page, contrary to the
   prompt's hard constraint that "the eligibility and licence of DYD are quoted from the program's own
   page."

## 15. What checks out (facts the manager could keep, each with its source)

- All 6 DOIs resolve and match CrossRef on title, full author list, year, volume and page (section 1).
- Doma et al. 2024: over 8,000 Canadian households, 3% difference in aggregated daily occupied hours
  vs. the Canadian TUS, exact wording confirmed in the OpenAlex abstract and independently in the
  underlying PhD thesis (71% vs 68%, Mann-Whitney U p>0.05) (sections 2, 9).
- Jung et al. 2023 scale and demographics (104,693 total thermostats, 91,747 US, 48 countries,
  house-type counts including 49,593 detached) are all verbatim from the full-text PDF this check
  independently downloaded and matched byte-for-byte to the log (sections 2, 9).
- The ecobee DYD access-route quote ("Are you a scientist or researcher...") is verbatim on the live
  page as of this check (section 6).
- Hydro-Quebec Card 4's field list, licence ("CC BY-NC 4.0") and 64,605-record count all match the
  live catalog API (sections 6, 9).
- Resideo and Google Nest cards' `NOT FOUND` for a bulk academic research programme is confirmed:
  neither developer portal mentions "research," "academic" or "dataset" access anywhere (sections 4,
  11).
- The Zenodo/Dryad/Figshare/NREL OEDI repository searches (corrections-block Item 1.4) are all
  present with logged query URLs, and Dryad's "0 hits" and Figshare's "0 relevant hits" both
  reproduce exactly on re-run (sections 9, 11).
- No em or en dashes, no named individuals tied to fellowships, no proposed change to the 4J gate, and
  no self-written verdict inside the report file (section 13).
