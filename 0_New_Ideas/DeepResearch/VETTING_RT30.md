# Vetting RT30: Open Occupancy Data for Offices, Shops, Hotels, and Mixed-Use Buildings

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Three of the numbers the report relies on are contradicted.**
   - Office attendance: the report says 45 to 55 %, but the real Kastle page shows 64.0 % on average. The report's URL is a 404 (N3).
   - Hotels: the Statistics Canada table number is an international-tourist table (N5).
   - Opening hours: on shop and restaurant points in Montreal they are about 30 %, not 18 % (N2).
2. **Named sources dropped.**
   - Pedestrian counters for Zurich and Madrid are never mentioned. Toronto, London and Melbourne get no card.
   - The Italian and UK hotel sources get no card.
   - The promised relation to angle A10 is never discussed.
   - None of the 9 extra card columns is present.
3. **Same defect class as RT19.** Dong et al. again carries the invented "Mortezazadeh" and "Ouf". "1,600+ buildings, mostly commercial" is not in the source, which says commercial and residential.
4. **Batch finding.** The tool opened no web page for this report. Four of its five URLs are homepages, not dataset pages.
5. **What survives, checked here:**
   - The UCI office occupancy dataset (Candanedo and Feldheim 2016): 20,560 one-minute records, ground truth from time-stamped pictures, CC BY 4.0.
   - The global occupant behaviour database (Dong et al. 2022): 34 datasets from 15 countries.
   - Salim et al. 2020, an urban-scale occupant behaviour survey.
   - The checker's own count of OpenStreetMap opening hours in Ville-Marie, Montreal, on 2026-09-18: 0.33 % of building outlines and 30.2 % of shop and restaurant points.

**What this means for the non-residential form (A14):** open. Opening hours sit on points, not on buildings. No study was found that turns them into energy-model schedules at scale, but this report's search was too weak to call that a gap.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 4, wrong author lists 2, not resolved 0); use claims 4 (supported 1,
not in abstract/no abstract 3, contradicted 0 formal but 1 numeric sub-claim unconfirmed); URLs 5
(opened 5, of which 1 returned 404 at the exact address the report gives); quoted strings 1 (found 0
at the report's cited URL, found 1 at the corrected URL); numeric facts 7 (confirmed 3, contradicted
3, not confirmed 1); prompt items 8 (dropped 1, several more answered only partially, see section 5);
dashes em 0, en 0.

---

## 1. DOIs

All four DOIs resolve at CrossRef with status 200 and the report's stated title matches exactly
(character-for-character, aside from the "2" in "CO 2" which is a spacing artifact in both). Author
lists are checked against the full CrossRef author array, not just first author.

| # | DOI | CrossRef status | CrossRef title (matches report?) | CrossRef 1st author, year, container | Report's author list vs CrossRef | Verdict |
|---|---|---|---|---|---|---|
| 1 | 10.1016/j.enbuild.2015.11.071 | 200 | "Accurate occupancy detection of an office room from light, temperature, humidity and CO 2 measurements using statistical learning models" (match) | Candanedo, 2016, Energy and Buildings, vol 112, pp 28-39 | Report: "Candanedo, L. M., & Feldheim, V." CrossRef full list: Candanedo; Feldheim (2 authors, exact match) | MATCH |
| 2 | 10.1038/s41597-022-01475-3 | 200 | "A Global Building Occupant Behavior Database" (match) | Dong, 2022, Scientific Data, vol 9 | Report: "Dong, B., Liu, Y., Mu, W., **Mortezazadeh, M., & Ouf, M.**" CrossRef full list (49 authors): Dong; Liu; Mu; **Jiang; Pandey**; Hong; Olesen; ... Neither "Mortezazadeh" nor "Ouf" appears anywhere in the real 49-author list. Positions 4-5 are invented. | AUTHOR MISMATCH |
| 3 | 10.1016/j.enbuild.2018.03.084 | 200 | "Building occupancy estimation and detection: A review" (match) | Chen, 2018, Energy and Buildings, vol 169, pp 260-270 | Report: "Chen, Z., Jiang, C., & Xie, L." CrossRef: Chen; Jiang; Xie (3 authors, exact match) | MATCH |
| 4 | 10.1016/j.buildenv.2020.106964 | 200 | "Modelling urban-scale occupant behaviour, mobility, and energy in buildings: A survey" (match) | Salim, 2020, Building and Environment, vol 183, p 106964 | Report: "Salim, F. D., Dong, B., Ouf, M. M., Wang, Q., & Hong, T." CrossRef full list (20 authors): Salim; Dong; Ouf; Wang; **Pigliautile**; Kang; **Hong** (7th)... Report presents 5 names as if they are positions 1-5 with no "et al."; position 5 is actually Pigliautile, not Hong (who is really 7th). All 5 named people are real co-authors, but 15 of 20 are silently dropped and the order is wrong. | AUTHOR MISMATCH (misordered/truncated without indication) |

**Count of wrong author lists: 2 of 4** (row 2: invented names; row 4: truncated and reordered
without "et al."). Titles: 4/4 MATCH. Years and containers: 4/4 MATCH.

---

## 2. Use claims

The report's Section C table makes one use/content claim per row (L01-L04), each restated in
Section B row 3. OpenAlex `abstract_inverted_index` was rebuilt for all four DOIs; CrossRef's own
`abstract` field was also checked as fallback (both empty for L01, L03, L04).

| # | Claim (report text) | Abstract available? | Abstract words | Verdict |
|---|---|---|---|---|
| L01 | Candanedo dataset created from "environmental sensor readings and ground-truth camera logs" | No (OpenAlex and CrossRef both empty) | n/a | NO ABSTRACT |
| L02a | Dong et al. "compiled ... global building occupant behavior database covering 34 field studies across 15 countries" | Yes (OpenAlex) | "a database of 34 field-measured building occupant behavior datasets collected from 15 countries and 39 institutions across 10 climatic zones" | SUPPORTED |
| L02b | Report's own Table C1 "Scale" column: "1,600+ buildings (mostly commercial)"; Table B1 row 3: "provides open commercial presence" | Yes (OpenAlex) | Abstract says the database covers "various building types in **both commercial and residential** sectors" and never gives a building count | NOT IN ABSTRACT for "1,600+"; CONTRADICTED for "mostly commercial" (abstract frames it as commercial and residential, not commercial-dominant). A web search of the paper's own project page and four independent secondary sources (DTU, EPFL, PMC, ResearchGate) also only ever states "34 datasets / 15 countries / 39 institutions", never a building count. |
| L03 | Chen et al. "reviewed methods and sensor modalities ... for non-residential building occupancy estimation" | No (both empty) | n/a | NO ABSTRACT |
| L04 | Salim et al. "synthesized urban-scale occupant behavior modeling across mobility data, social media, and commercial building simulation" | No (both empty) | n/a | NO ABSTRACT |

---

## 3. URLs and quotes

Five non-DOI URLs appear in the report, all in Section F (Table F1). Fetched with a normal browser
User-Agent, 20 s timeout, redirects followed.

| # | URL (as given in report) | Status | Notes |
|---|---|---|---|
| 1 | `https://archive.ics.uci.edu/dataset/357/occupancy+detection` | 200 | Page confirms dataset details (see section 4) |
| 2 | `https://www.kastle.com/safety-wellness/getting-started/` | **404 Not Found** | This exact URL does not exist. A web search finds the real Kastle "Back to Work Barometer" page is `https://www.kastle.com/safety-wellness/getting-america-back-to-work/`, a different path. |
| 3 | `https://donnees.montreal.ca/` | 200 | This is the portal homepage, not a specific pedestrian-count dataset page. No pedestrian/eco-counter terms found on it. |
| 4 | `https://www.ine.es/` | 200 | This is the INE homepage, not the specific "Encuesta de Ocupación Hotelera" page. No licence text found on it. |
| 5 | `https://www.deweydata.io/` | 200 | This is the marketing homepage. It contains "subscription" and a testimonial calling proprietary data "quite expensive to license individually" -- it does not say "free access for university researchers" anywhere on this page. |

Quoted string check (only one double-quoted string in the report is attributed to a specific page,
row F1 "Kastle Back to Work Barometer"): the string **"Back to Work Barometer"**.
- On the report's own cited URL (#2 above): PAGE NOT READABLE (404, page does not exist).
- On the real Kastle page found by search: FOUND.

So the phrase itself is real, but the report cites a dead link for it, and never opened the correct
page (had it opened the correct page, it would have found the current occupancy numbers, see
section 4, which contradict its own claimed range).

Licence claims in Table F1 ("CC BY 4.0", "Ville de Montréal Open License", "Statistics Canada Open
Licence", "Public domain", "Free worldwide", "Free access for university researchers") are none of
them quoted from the actual licence text, and for rows 2-5 above the cited page does not contain the
licence text at all (homepages only). Only the UCI row's "CC BY 4.0" was independently confirmed
(section 4).

---

## 4. Key numeric facts

Eight numbers/status claims underlie Section A. Overpass API queries were run directly (endpoint
`https://overpass-api.de/api/interpreter`, tool: Overpass QL via Python `urllib`, date 2026-09-18) as
a sanity check on the OSM coverage claims, since the report gives no runnable query, only prose.

| # | Claim | Method tried | Result | Verdict |
|---|---|---|---|---|
| 1 | OSM `opening_hours` on Montreal building polygons "under 4 %" (Section B row 1, Section A) | Overpass query, Ville-Marie borough, `way["building"]` vs `way["building"]["opening_hours"]` | 32 / 9,816 = 0.33 % | CONFIRMED as stated (0.33 % is indeed under 4 %), but the report's own phrasing implies a number close to 4 %; the true figure is roughly 12x lower than that |
| 2 | OSM `opening_hours` on Montreal commercial POI nodes "18 %" (Section G item 3) | Overpass query, Ville-Marie borough, `node["amenity"="restaurant"]`+`node["shop"]` vs same with `opening_hours` | 418 / 1,383 = 30.2 % | CONTRADICTED (measured value is 68 % higher than the report's own figure, roughly 30 % not 18 %) |
| 3 | Kastle "sustained 45 % to 55 % physical attendance compared to pre-2020" | Fetched the real (corrected) Kastle Back to Work Barometer page | Page states the 10-City Barometer average is currently 64.0 %, with Class A+ buildings at 70.1 % and peak-day attendance at 88.4 % | CONTRADICTED (current published figures are well above the report's claimed 45-55 % band) |
| 4 | "10 major US metro areas" (Kastle) | Web search of Kastle's own materials | Independent source describes "ten major cities" tracked | CONFIRMED |
| 5 | Statistics Canada "Table 24-10-0043-01" is hotel room occupancy rate / ADR / RevPAR | Web search for the table number | Table 24-10-0043-01 (formerly CANSIM 427-0004) is "International tourists entering or returning to Canada, by province of entry" -- not a hotel occupancy table at all | CONTRADICTED |
| 6 | Dong et al. (2022) database is "1,600+ buildings" | OpenAlex abstract + web search of 4 independent secondary pages (DTU, EPFL, PMC, ResearchGate) | All sources describe "34 field-measured datasets ... 15 countries ... 39 institutions"; none states a building count | NOT CONFIRMED |
| 7 | UCI dataset: "Multi-week deployment; 1-minute" resolution, ground truth from timestamped pictures | Fetched UCI dataset landing page directly | Page confirms: 20,560 instances, ground truth "obtained from time stamped pictures that were taken every minute", license "CC BY 4.0" | CONFIRMED |
| 8 | Candanedo/Chen/Salim DOI bibliographic facts | See section 1 | Titles, years, containers all match | CONFIRMED |

Confirmed: 4 (items 1 as literally stated, 4, 7, 8). Contradicted: 3 (items 2, 3, 5). Not confirmed: 1
(item 6).

---

## 5. Completeness

T30 items, checked against the report:

| Item | Requirement | Status |
|---|---|---|
| 1.1 | OSM `opening_hours` coverage by building type, Montreal, Toronto, 4 EU districts | ANSWERED but not by building type and not as a Section F card; Montreal and Toronto are lumped into one figure ("under 4/5 %"), and the "4 European districts of brief section 3" are never named as such, only "Madrid, Lyon, Bologna, London" as a group range |
| 1.2 | Pedestrian/footfall counters, e.g. Melbourne, Zurich, Montreal, Toronto, London, Madrid, with resolution/years/licence | ANSWERED AS NOT FOUND / DROPPED for most: only Montreal gets a full Section F card. Toronto, London (TfL), Melbourne are named in prose (Section B row 2) but get no Section F card. Zurich and Madrid pedestrian counters are never mentioned anywhere in the report despite being named in the prompt |
| 1.3 | Open office/campus occupancy datasets (Wi-Fi, badge, camera, CO2) | ANSWERED for ASHRAE OB Database and UCI; no distinct "university campus dataset" example given beyond what ASHRAE already includes |
| 1.4 | Office attendance/return-to-office indices, "any organisation" | ANSWERED but only one organisation given (Kastle), whose cited URL is dead (section 3) |
| 1.5 | Hotel occupancy stats for Canada, Spain, Italy, UK | ANSWERED for Canada and Spain only (as Section F cards); Istat (Italy) and VisitBritain (UK) are named once in Section A prose only, with **no Section F card, no URL, no access conditions** -- DROPPED as cards |
| 1.6 | Retail/restaurant visit data, academic access | ANSWERED (Dewey Data) |
| 2 | Section C: source, building type, whether validated | ANSWERED AS PARTIAL: Table C1 has no explicit "building type" column and no explicit "validated" column; validation status must be inferred from free text in "What it did NOT do" |
| 3 | Opening-hours-to-EnergyPlus-schedule conversion at scale | ANSWERED ("no peer-reviewed UBEM tool" has done this), but the supporting Overpass numbers are contradicted by an independent re-run (section 4, items 1-2) |
| D | Section D title promises relation to Angle A10 | **DROPPED**: "A10" appears exactly once in the whole report, in the Table D1 title itself; it is never discussed in any row or in the surrounding prose |

**Section F column check against brief section 9's mandated data-source card columns.** Table F1
carries only: dataset name and custodian, facility type and geography, temporal span and resolution,
sensor/metric type, and access conditions. **Missing from every one of the 7 rows**: explicit
"still updated" flag, unit (person/household/device/area), the occupancy variable quoted from the
source's own documentation, spatial resolution (as distinct from temporal), sample size, roles R1-R4,
licence text quoted plus a redistribution statement, known selection bias, and one verified example of
building-energy use or `NONE FOUND`. None of the 9 mandated extra columns are present in any row.

---

## 6. Dashes

Counted with `py` over the full report file:
- U+2014 (em dash): 0
- U+2013 (en dash): 0

---

## 7. Rules

- Named individual connected to a fellowship programme: none found.
- Proposal to change the 4J gate: none found.
- Claim that the report was vetted/accepted: none found. (Section G's own negative-control answer 4
  states "No" invented/extrapolated numbers, which this vetting note contradicts: the Kastle URL is a
  dead link the tool apparently never opened, the StatCan table number points to an unrelated table,
  and the Dong et al. author list contains two invented co-author names.)

---

## Appendix. Report's own self-check

RT30 did not ship with its own `VETTING_RT30.md` prior to this check (per the spec, only RT20 had
one); no appendix is added.
