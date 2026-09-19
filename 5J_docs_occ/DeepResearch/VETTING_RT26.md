# Vetting RT26: household_travel_surveys

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The answer to the question rests on a false claim.** The only building-energy prior work given
   for travel surveys (Berres et al. 2021) is a traffic-sensor paper, by its own title and abstract
   (U1, N8). A second use claim is also contradicted (Gerike et al. 2015 covers Germany only, U2).
2. **Same defect class as RT19.** 2 of 4 author lists are wrong (one co-author invented), and the
   report's own line "All DOIs have been verified" is false.
3. **Item 1 is half dropped.** 9 of 16 named surveys are silently absent, and 7 of about 13
   data-source card columns are missing from every row, so no row is a usable card.
4. **Batch finding.** The tool opened no web page for this report (its own log). The German access URL
   now serves a casino page; the "via CIQSS" access route for the Montreal survey was found nowhere.
5. **What survives, checked here:** the Montreal survey's 2018 sample of about 73,000 households
   (but 158 municipalities, not 82); the Toronto survey's 2016 sample of about 163,000 interviews; the
   US national survey 2017 sample of 129,696 households (the 2022 edition is only 7,893); the ARTM data
   portal with a researcher access level; McKenna et al. 2015 is correct and uses UK time-use data.

**What this means for the travel-survey form (A14):** still open, not "taken". No building-energy
work using a household travel survey for occupancy was found, but this report did not search well
enough to call that a gap. The zero-trip share (15 to 20 %) is unsourced and may not be quoted.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 2, wrong author lists 2, not resolved 0); use claims 4 (supported 1,
not in abstract 1, contradicted 2); URLs 3 (opened 3); quoted strings 0 (found 0); numeric facts 8
(confirmed 3, contradicted 3, not confirmed 2); prompt items 4 top-level (dropped 0 at top level, but
9 of 15 named surveys in item 1 silently absent, see section 5); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (80 chars) | Title match | CrossRef 1st author / year / container | Report states | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | 10.26868/25222708.2021.30744 | 200 | "Generating traffic-based building occupancy schedules in Chattanooga, Tenness..." | Yes | Berres (Andy Berres); 2021; Building Simulation Conference Proceedings. Full author list: Berres, Bass, R New (Joshua New), Im, Urban, Sanyal (6 authors) | "Berres, A., Im, P., & Sanyal, J. (2021)" (3 of 6 authors; Bass, New, Urban dropped) | AUTHOR MISMATCH |
| D2 | 10.1016/j.tra.2015.03.030 | 200 | "Time use in travel surveys and time use surveys [dash] Two sides of the same coin?" | Yes | Gerike; 2015; Transportation Research Part A. Full author list: Gerike, Gehlert, Leisch (3 authors) | "Gerike, R., Gehlert, T., & Schulz, F. (2015)" (3rd author invented: "Schulz" is not an author; real 3rd author is Leisch) | AUTHOR MISMATCH |
| D3 | 10.1016/j.enbuild.2015.03.013 | 200 | "Four-state domestic building occupancy model for energy demand simulations" | Yes | McKenna; 2015; Energy and Buildings, vol 96, pp 30-39 | "McKenna, Krawczynski, Thomson (2015)... Energy and Buildings, 96, 30-39" | MATCH |
| D4 | 10.1016/j.tra.2015.12.001 | 200 | "Help or hindrance? The travel, energy and carbon impacts of highly automated vehicles" | Yes | Wadud; 2016; Transportation Research Part A, vol 86, pp 1-18 | "Wadud, MacKenzie, Leiby (2016)... 86, 1-18" | MATCH |

Author lists wrong: 2 of 4 (D1, D2). Both errors are the same class as the prior wave (dropped/invented
co-authors), not typos.

A fifth citation, "Hubert et al. (2008)", appears in Section G prose with no DOI, no entry in Section H
references, and no CrossRef/OpenAlex lookup performed. It cannot be checked and is not admitted to any
table under the brief's own rule (section 9, extra hard rule 1: a row without a resolving identifier is
not admitted to Sections C or F); it should not have been used to support a claim in Section G either.

---

## 2. Use claims

| # | Claim (row) | Claim text | Abstract source | Abstract words | Verdict |
|---|---|---|---|---|---|
| U1 | Section A + Table C1 L01, Berres et al. (2021) | "travel surveys have been successfully leveraged to generate synthetic urban occupancy schedules, notably by Berres et al. (2021)"; Table C1 "Data used: Traffic counts, regional travel demand model, NHTS" | OpenAlex (full, 617 chars) | "We construct traffic-based occupancy schedules which are more responsive to changes in mobility patterns... estimate occupant arrivals, departures, and counts." No mention anywhere of a household travel survey, NHTS, or travel-diary microdata; the paper is about a grid of traffic sensors (also stated in the paper's own title). | CONTRADICTED |
| U2 | Table C1 L02, Gerike et al. (2015) | "Compared travel behavior and time use between national travel surveys and time use surveys across Germany, Austria, and Switzerland" | OpenAlex (full, 1976 chars) | "The analyses are based on the German National Travel Survey and the German National Time Use Survey from 2002." Only Germany; Austria and Switzerland are not mentioned anywhere in the abstract. | CONTRADICTED |
| U3 | Table C1 L03, McKenna et al. (2015) | "UK Time Use Survey microdata" | OpenAlex (full) | "The model is constructed from and verified against UK time-use survey data" | SUPPORTED |
| U4 | Table C1 L04, Wadud et al. (2016) | "Analyzed travel survey data to evaluate energy and carbon trade-offs of travel activity shifts"; Data used: "US National Household Travel Survey (NHTS)" | OpenAlex (full, 1746 chars) | Abstract describes a "coherent energy decomposition framework," a literature review, and the authors' "own estimates using engineering and economic analysis." No mention of NHTS, a travel survey, or travel-survey data anywhere. | NOT IN ABSTRACT |

Central finding for this assignment: U1 is the report's only cited building-energy example of occupancy
derived from a travel survey (it is what Section A's direct answer rests on), and it is the one flagged
in the task instructions to check. The Berres et al. (2021) abstract, and its own title, describe a
**traffic-sensor** paper, not a household-travel-survey paper. No NHTS, EOD, TTS, or any named travel
survey appears in its abstract.

---

## 3. URLs and quotes

| # | URL | Fetch status | Final URL | Content matches claimed use | Quoted strings tied to it | Verdict |
|---|---|---|---|---|---|---|
| W1 | https://nhts.ornl.gov/ | 200 | same | Yes, real NHTS site | none attributed | FOUND (page real; no quote to check) |
| W2 | https://beta.ukdataservice.ac.uk/ | 301 -> 200 | https://ukdataservice.ac.uk/ | Yes, real UK Data Service site | none attributed | FOUND (page real; no quote to check) |
| W3 | https://www.clearingstelle-verkehr.de/ | 200 | https://clearingstelle-verkehr.de/ | **No.** Page title: "Casino ohne OASIS - Online Casinos Deutschland im Anbietercheck." The entire page is an online-casino comparison site in German; it contains no reference to MiD, BMDV, transport, or academic data licensing anywhere. | Report states this URL is the "Clearingstelle Verkehr portal" with "Free academic use license upon application" | PAGE NOT READABLE for the claimed content (page loads, but is unrelated; the licence claim cannot be checked against it and the URL does not support the stated access route) |

No double-quoted strings in Table F1 are explicitly attributed to a specific fetched page (the "Access
conditions" column is paraphrase/assertion throughout, not quotation), so there is nothing to search for
FOUND/NOT FOUND under the letter of check 3; the one quote-like claim (MiD licence terms on the
Clearingstelle Verkehr URL) fails because the page is not what the report says it is.

---

## 4. Key numeric facts

| # | Fact | Report states | What I checked | Result | Verdict |
|---|---|---|---|---|---|
| N1 | ARTM EOD 2018 household count | "approx. 73,000 households" | ARTM's own site (artm.quebec, "Des nouvelles de l'enquete Origine-Destination 2018"): "73 000 menages" | Matches | CONFIRMED |
| N2 | ARTM EOD 2018 municipality count | "82 municipalities" (Table F1) | Same ARTM page: "158 municipalites" | Report's figure (82) does not match the source's figure (158) | CONTRADICTED |
| N3 | TTS 2016 household count | "approx. 162,000 households" | DMG's own TTS Introduction page: "approximately 163,000 completed interviews" | Close (162k vs 163k), within rounding | CONFIRMED |
| N4 | NHTS 2017 household count | "~129,000 households" | FHWA/NHTS documentation (web search of primary NHTS materials): 129,696 households (26,099 national sample + 13 add-on areas) | Matches | CONFIRMED |
| N5 | NHTS 2017/2022 combined "over 260,000 completed household travel diaries" | Table B1 row 6, merges both editions into one PUMF claim | 2017: 129,696 households (264,000 is the persons count, per the report's own Table F1). 2022 edition: only 7,893 households, an address-based sample, an order of magnitude smaller, not mentioned anywhere in the report | The 260,000 figure appears to conflate 2017 PERSONS with "household travel diaries," and silently omits that the 2022 edition is far smaller, not "similar scale" | CONTRADICTED (unit conflation; material fact omitted) |
| N6 | Zero-trip respondent share, EOD and TTS | "approximately 15% to 20%" (Section E) / "approximately 18%" (Section G) | No primary EOD or TTS documentation page was opened or cited for this figure; it is asserted with no source | Not checked against any traceable document | NOT CONFIRMED (unsourced) |
| N7 | Montreal EOD access route: "via ARTM academic data agreements and CIQSS" | Table B1 row 1, Table F1 | ARTM's own portal (donnees.artm.quebec, "Portail donnees mobilite") describes a tiered access system with Level 2 for university researchers/professors, run directly by ARTM. No page found (ARTM site, CIQSS site, or web search) stating that CIQSS distributes EOD microdata | The specific claim that CIQSS is an access route for this survey was not found anywhere; access as documented runs through ARTM's own portal | NOT CONFIRMED |
| N8 | Berres et al. (2021) "successfully leveraged" a travel survey for occupancy schedules | Section A | Abstract (checked in full, see section 2, U1) | Abstract describes traffic sensors and mobility patterns, not a travel survey | CONTRADICTED |

---

## 5. Completeness

### Top-level T26 prompt items

| Item | Asks for | Status |
|---|---|---|
| Item 1 (surveys) | Data-source cards for named Canadian, US, and European surveys | ANSWERED, but incomplete: see survey-by-survey table below |
| Item 2 (presence from trips) | Section C rows: method, handling of zero-trip people, comparison with time-use survey for the same place/year | ANSWERED AS NOT FOUND in substance: the four Section C rows do not state a per-study zero-trip handling method or a same-place/same-year time-use comparison; that material appears only as generic prose in Section G, not tied to any specific study |
| Item 3 (travel survey vs time-use survey) | Studies comparing time out of home or trip counts, direction and size of the difference, quoted | ANSWERED (Gerike et al. 2015 quoted with a direction and size), but the report's own restatement of that study's scope (Germany/Austria/Switzerland) is CONTRADICTED by the study's abstract (see U2); the second cited source, Hubert et al. (2008), is unverifiable (no DOI, not in Section H) |
| Item 4 (building energy use) | Section C rows for works using travel surveys for occupancy in building energy | ANSWERED, but its sole example (Berres et al. 2021) is CONTRADICTED (see U1); on the evidence gathered here the honest answer to Item 4 is closer to NOT FOUND |

### Item 1 survey-by-survey check (named leads in the T prompt)

| Named survey | In Table F1? |
|---|---|
| Enquete Origine-Destination (Montreal, ARTM) | Present |
| Transportation Tomorrow Survey (Toronto/GTHA, DMG) | Present |
| Quebec City regional survey | DROPPED (silently absent) |
| Ottawa-Gatineau TRANS | DROPPED (silently absent) |
| Calgary regional survey | DROPPED (silently absent) |
| Metro Vancouver regional survey | DROPPED (silently absent) |
| NHTS (US) | Present |
| Large open US regional survey | DROPPED (silently absent) |
| UK National Travel Survey | Present |
| Germany Mobilitat in Deutschland (MiD) | Present |
| France Enquete Mobilite des Personnes | Present |
| Ile-de-France Enquete Globale Transport | DROPPED (silently absent) |
| Switzerland Mobility and Transport Microcensus | DROPPED (silently absent) |
| Netherlands ODiN | Present |
| Spain (national or Madrid regional) | DROPPED (silently absent) |
| Italy (national or Bologna regional) | DROPPED (silently absent) |

9 of 16 named surveys are silently absent from Table F1, with no NOT FOUND statement anywhere in the
report acknowledging the gap.

### Data-source card columns (brief section 9) vs Table F1

Table F1 uses 6 columns: survey name and custodian; geography and coverage; sample size and recent
editions; data format and trip timing; at-home work captured; access conditions and eligibility.

Required by brief section 9 and missing from every row of Table F1:
- unit (person, household, dwelling, device, grid cell, area)
- the occupancy variable actually contained, quoted from documentation
- spatial resolution of the home location in the public file (only discussed generically in Section G
  prose, not per row, and Item 1 explicitly asks for this per survey)
- roles R1 to R4 per source
- licence and whether derived schedules may be redistributed, quoted
- known selection bias, per source
- one verified example of use in building energy research, or NONE FOUND, per row

7 of the roughly 13 required data-source card columns are missing from every row.

---

## 6. Dashes

Checked with `py`, counting U+2014 (em dash) and U+2013 (en dash) across the full report text.

Em dash count: 0
En dash count: 0

---

## 7. Rules

- Named individual connected to a fellowship programme: none found.
- Proposal to change the 4J gate: none found.
- Claim that the report was vetted or accepted: none found as an external claim. Section G item 4 states
  "No. All DOIs have been verified against `api.crossref.org`," which is a self-verification claim; this
  vetting note's own DOI check (section 1) contradicts it in part, since 2 of the 4 DOIs resolve to
  author lists different from what the report states even though the DOIs themselves resolve correctly.

---

Checked items summary: DOIs 4, use claims 4, URLs 3, numeric facts 8, dashes em 0 en 0.
