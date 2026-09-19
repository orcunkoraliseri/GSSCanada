# Vetting RT34: Canadian Open Data Inventory for Occupancy

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Item 1, the inventory, is mostly dropped.** About 18 of 24 named Canadian sources have no row and no NOT
   FOUND line. These include:
   - IESO, BC Hydro, Hydro Ottawa and Green Button;
   - the Canadian Housing Survey and the Research Data Centre items;
   - STM and TTC ridership;
   - Borealis, FRDR and CRDCN.
2. **Five of nine URLs are 404** (EnerGuide, Hydro-Quebec, the Montreal 3D model, ARTM, HUE). The HUE dataset has
   22 houses, not 42. The EnerGuide "over 1 million audit files" is unconfirmed; the open file is aggregated by
   postal area (FSA), not by dwelling.
3. **Item 3 is mostly off target.** 2 of 3 rows are not Canadian studies: Ferrando is a review, and Berres is
   Chattanooga traffic sensors. The report also discusses Quebec Law 25, which the prompt put out of scope. No
   card carries 9 of the 13 required columns.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:**
   - The Labour Force Survey public file (71M0001X) is monthly, from 1976 to now, and still updated.
   - Montreal by-law 21-042 covers buildings of 2,000 m2 or more, or 25 or more homes.
   - Ontario's energy reporting rule (O. Reg. 506/18) covers buildings of 50,000 sq ft or more.
   - The real EnerGuide open-data page is under the Open Government Licence - Canada.
   - Toronto pedestrian volumes are under the Open Government Licence - Toronto.
   - HUE is on Harvard Dataverse (10.7910/DVN/N3HGRN).
   - The real Hydro-Quebec demand dataset slug is `demande-electricite-quebec`; its 15-minute update was seen only
     in a search snippet.

**What this means for the Canadian inventory form (A14):** open. The Canadian public sources that reach dwelling
occupancy are few, and the report did not search most of the named ones. The disclosure by-laws cover large
buildings only, so they validate energy, not homes' occupancy.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 3 (match 2, wrong author lists 1, not resolved 0); use claims 3 (supported 1,
not in abstract 0, contradicted 1, no abstract 1); URLs 9 (opened 4); quoted strings 3 (found 3);
numeric facts 7 (confirmed 2, contradicted 1, not confirmed 4); prompt items approx. 24 named sources
(answered 9, answered as not found 1, dropped approx. 18); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (80 chars) | Title match | CrossRef authors | Report authors | Year | Container | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.buildenv.2024.111713 | 200 | Developing a residential occupancy schedule generator based on smart thermostat data | match | Doma, Prajapati, Ouf | Doma, Prajapati, & Ouf | 2024=2024 | Building and Environment = Build. Environ. | MATCH (but see note) |
| D2 | 10.1016/j.scs.2020.102408 | 200 | Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches | match | Ferrando, Causone, Hong, Chen | Ferrando, Causone, Hong, & Chen | 2020=2020 | Sustainable Cities and Society = Sustain. Cities Soc. | MATCH |
| D3 | 10.26868/25222708.2021.30744 | 200 | Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of traffic sensors | match | Berres, Bass, R New, Im, Urban, Sanyal (6 authors) | Berres, Im, & Sanyal (3 authors) | 2021=2021 | Building Simulation Conference Proceedings = Build. Simul. Conf. | AUTHOR MISMATCH |

Note on D1: CrossRef gives volume 261; the report's Section H reference states volume 259. This is a
factual error in the reference list, not covered by the author/title/year checks above.

Note on D3: three of six CrossRef-listed co-authors (Bass, R New, Urban) are silently dropped from
the report's author lists in both Table C1 and Section H. Count of wrong author lists: 1 of 3.

---

## 2. Use claims

| # | Row | Claim text | Abstract source | Abstract words (quoted) | Verdict |
|---|---|---|---|---|---|
| U1 | L01 Doma et al. (2024) | "Built residential Markov occupancy schedule generator from ecobee smart thermostat motion logs and compared against GSS" | OpenAlex | "...develop a rule-based framework that addresses the limitations of relying on motion-detection data..." / "...validated by comparing them with residential occupancy profiles generated from the Canadian Time Use Survey (TUS)." | CONTRADICTED on method: abstract says rule-based, not Markov. Dataset claim (ecobee, 8,000+ Canadian homes, comparison against a Canadian time-use survey) is SUPPORTED. |
| U2 | L02 Ferrando et al. (2020) | "Reviewed bottom-up physics-based UBEM tools, identifying data integration gaps across North American and European stocks" | OpenAlex and CrossRef | no abstract text returned by either source | NO ABSTRACT |
| U3 | L03 Berres et al. (2021) | "Generated traffic-driven building occupancy schedules for UBEM using travel surveys and traffic count sensors" | OpenAlex | "We construct traffic-based occupancy schedules which are more responsive to changes in mobility patterns, and which can realistically estimate occupant arrivals, departures, and counts in individual buildings." | SUPPORTED for traffic-sensor-based schedules; the phrase "travel surveys" as an input does not appear in the retrieved abstract text (NOT IN ABSTRACT for that specific sub-claim). |

---

## 3. URLs and quotes

| # | Row | URL | HTTP status (curl + urllib, both agree) | Notes |
|---|---|---|---|---|
| L1 | StatCan LFS PUMF | https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X | 200 | Page confirms catalogue number 71M0001X = "Labour Force Survey: Public Use Microdata File". No licence text of any kind found on the page (searched case-insensitive for "licen[cs]e"); "Statistics Canada Open Licence" is PAGE NOT READABLE for that specific claim (page simply does not carry licence text). Temporal claim "2020-2024" is wrong: page lists monthly files from 1976 to August 2026, ongoing. |
| L2 | NRCan EnerGuide | https://open.canada.ca/data/en/dataset/4c554907-789a-4131-ab10-6395b0b42fa0 | 404 | Dataset does not exist at this ID. The real, current EnerGuide Rating System Open Data page is `https://open.canada.ca/data/en/dataset/0a7619fd-2ffe-44b5-9027-3dfcec0866fd`; fetched that page (200) as a substitute check: it does carry "Open Government Licence - Canada" (FOUND, matches the report's licence claim), but describes data aggregated to Forward Sortation Area (first 3 postal-code digits), not per-dwelling "audit files". |
| L3 | Hydro-Quebec hourly demand | https://www.donneesquebec.ca/recherche/dataset/demande-d-electricite-au-quebec | 404 | Wrong slug. Real dataset slug is `demande-electricite-quebec` (no "d-" / "au-"). Real dataset (per search snippet, not directly fetched) updates every 15 minutes, not "hourly" as the report states. |
| L4 | Ville de Montreal 3D model | https://donnees.montreal.ca/dataset/maquette-numerique-de-la-ville-de-montreal | 404 | No dataset with this slug found. Real Montreal 3D building datasets use names like "batiment-3d-2016-maquette-citygml-lod2-avec-textures2" or borough-specific slugs; none matches the report's URL. |
| L5 | Toronto pedestrian volumes | https://open.toronto.ca/dataset/pedestrian-volumes-at-intersections-data/ | 200 | Page text contains "Open Government Licence - Toronto" verbatim (FOUND, matches report). |
| L6 | ARTM EOD | https://www.artm.quebec/enquetes-mobilite/ | 404 | Page does not exist. Real ARTM OD-survey pages are at different paths (e.g. `/planification/enqueteod/`). Search results describe access via an ARTM "Mobility Data Portal" with three access tiers (government, university, researcher); no mention of CIQSS found in that description, contrary to the report's "Academic data agreement via CIQSS" claim. |
| L7 | U of T TTS | https://dmg.utoronto.ca/transportation-tomorrow-survey/ | 200 | Page opens but is a navigation-only landing page with no body text. Searched case-insensitive for "Concordia", "eligib", "university", "access": none found. The report's quoted-in-substance claim "Concordia eligible" is NOT FOUND on this page. |
| L8 | UBC HUE GitHub | https://github.com/intelligent-systems-lab/HUE | 404 | Organisation/repo does not exist. The real HUE dataset code repository is `github.com/smakonin/HUE.dataset`; the data itself is hosted on Harvard Dataverse (DOI 10.7910/DVN/N3HGRN), not distributed directly via GitHub as the report implies. |
| L9 | ecobee DYD | https://www.ecobee.com/en-ca/donate-your-data/ | 200 | Page opens and matches the report's general characterisation: a researcher-application flow ("Are you a scientist or researcher working to improve energy use, building science, or public health? We want to help.", "What is your research about?"). No pricing/fee text found either way, so "Free for approved university projects" is not confirmed or contradicted by the page. |

Opened (200): 4 of 9 (L1, L5, L7, L9). Not opened (404): 5 of 9 (L2, L3, L4, L6, L8).

Quoted strings attributed to a page: only the three CrossRef titles in Section H (checked in Section 1
above; all 3 FOUND verbatim against CrossRef). No licence, eligibility or redistribution text
anywhere in the report is presented in double quotes, despite brief section 9's requirement that such
terms be quoted rather than summarised (see Section 5).

---

## 4. Key numeric facts

| # | Fact | Report value | Check | Verdict |
|---|---|---|---|---|
| N1 | ecobee DYD household count | "over 8,000 Canadian homes" | OpenAlex abstract of Doma et al. (2024): "applied to over 8,000 Canadian households" | CONFIRMED |
| N2 | HUE household count | "42 Canadian homes" | Web search of the HUE dataset's own description: "There are currently twenty-two houses contained within the dataset" | CONTRADICTED (22, not 42) |
| N3 | NRCan EnerGuide scale | "over 1 million Canadian home audit files" | Fetched the real open.canada.ca EnerGuide page (correct ID, found by search): no "million" figure anywhere on the page; page describes FSA-level aggregated data, not per-dwelling audit files | NOT CONFIRMED (tried: full-text search of the real dataset landing page) |
| N4 | Montreal By-law 21-042 threshold | ">2,000 m2" | montreal.ca and press coverage of Règlement 21-042: "buildings of 2,000 m2 (21,528 sq ft) or more OR 25 housing units or more" | CONFIRMED |
| N5 | Ontario EWRB threshold | ">50,000 sq ft" | ontario.ca / CanLII O. Reg. 506/18 coverage: "prescribed buildings 50,000 square feet and larger" | CONFIRMED |
| N6 | Smart meter penetration Quebec/Ontario | "over 95%" | not checked against a primary utility or regulator source | NOT CONFIRMED (tried: none attempted beyond the report's own claim, time-boxed out) |
| N7 | Combined ARTM + TTS household sample | "more than 230,000 households" | not checked against ARTM/TTS official sample-size documentation | NOT CONFIRMED (tried: general web search only surfaced survey history/access-tier text, not sample sizes) |

---

## 5. Completeness

### Against the T34 prompt's Item 1 named sub-categories (approx. 24 distinct named sources)

| Group (T prompt) | Named items | Status |
|---|---|---|
| 1. Statistics Canada | LFS PUMF | ANSWERED |
| | Canadian Housing Survey | DROPPED |
| | experimental statistics | DROPPED |
| | Research Data Centre items (named) | DROPPED |
| 2. NRCan / CanmetENERGY | EnerGuide | ANSWERED (but see N3, wrong URL and unverified scale) |
| | Canadian Housing Stock model inputs | DROPPED |
| | metered sets | DROPPED |
| 3. Utilities / system operators | Hydro-Quebec open data | ANSWERED (wrong URL, see L3) |
| | IESO | DROPPED (zero mentions anywhere in the report) |
| | Toronto Hydro | ANSWERED AS NOT FOUND (only in Section G prose, no Section F row) |
| | Hydro Ottawa | DROPPED |
| | BC Hydro | DROPPED |
| | Green Button (Ontario) | DROPPED |
| 4. Municipal portals | Ville de Montreal 3D model | ANSWERED (wrong URL, see L4) |
| | Toronto pedestrian volumes | ANSWERED |
| | cycling counters | DROPPED |
| | permits | DROPPED |
| | population by small area | DROPPED |
| | municipal building-occupancy data | DROPPED |
| | Montreal / Toronto building-energy disclosure | ANSWERED but as narrative prose in Section B, not as Section F rows with a URL, and not quoted verbatim (see Item 2 below) |
| 5. Transport agencies | ARTM EOD | ANSWERED (wrong URL, see L6) |
| | DMG TTS | ANSWERED |
| | STM ridership | DROPPED |
| | TTC ridership | DROPPED |
| 6. University / consortium holdings | ecobee DYD (instrumented-home) | ANSWERED |
| | HUE (metered set) | ANSWERED (wrong URL, see L8) |
| | Borealis | DROPPED |
| | FRDR | DROPPED |
| | CRDCN | DROPPED |

Answered: 9. Answered as not found: 1 (Toronto Hydro, prose only). Dropped silently (no row, no
"NOT FOUND" statement, no mention anywhere in the text): 18 of 24, including three of the four named
utilities besides Hydro-Quebec (IESO, BC Hydro, Hydro Ottawa, plus Green Button Ontario), all three
named research-data consortia (Borealis, FRDR, CRDCN), and both named municipal transit agencies
(STM, TTC).

### Item 2 (ground truth for Canadian UBEM)

T34 says "Quote the disclosure rules." Table B1 rows 3 and 4 paraphrase the Montreal by-law and the
Ontario EWRB regulation; neither is given as a direct quotation from the regulation text. ANSWERED,
but not to the letter of the instruction.

### Item 3 (Canadian occupancy studies using non-survey data)

T34 asks for "works that used any Canadian non-survey source for residential or urban occupancy."
Of the three rows in Table C1: only L01 (Doma et al., ecobee, Canadian homes) is actually a Canadian
occupancy study. L02 (Ferrando et al.) is a general UBEM tools review with no Canadian data or focus.
L03 (Berres et al.) is a Chattanooga, Tennessee study with no Canadian data. 2 of 3 Section C rows do
not answer the question the item asked; they answer a broader "UBEM occupancy schedule work"
question instead.

### Section F data-source card (brief section 9)

Required columns beyond the report's own template: source name and custodian; country and geography;
years covered and whether still updated; unit; the occupancy variable actually contained (quoted);
temporal resolution; spatial resolution; sample size; roles R1-R4; access route and eligibility for a
Canadian researcher (quoted, dated); licence and whether derived schedules may be redistributed
(quoted); known selection bias; one verified use example or NONE FOUND.

Table F1 in RT34 carries only: custodian and organisation, dataset name, geographic coverage,
temporal span and resolution, access route and licensing (paraphrased, not quoted), URL. Missing
entirely from every row: unit; the occupancy variable quoted from documentation; spatial resolution
as its own field; sample size as its own field; roles R1 to R4; eligibility quoted with a date;
redistribution rights quoted; known selection bias; and a verified use example or NONE FOUND. 9 of
13 required card columns are missing from all 9 rows.

### Out-of-scope content

T34's hard constraints state "Quebec Law 25 and federal privacy rules are out of scope here; T36
covers them." Section G nonetheless raises "provincial privacy legislation (e.g. Quebec Law 25)" as
the reason utilities withhold data. This is the exact topic the prompt says is out of scope for T34.

---

## 6. Dashes

Counted with `py` over the raw report file: em dash (U+2014) count = 0. En dash (U+2013) count = 0.

---

## 7. Rules

- Named individual connected to a fellowship programme: none found in the report text (checked for
  "fellowship", named professors, etc.; the only named individual, "Liam O'Brien, Associate Professor
  at Carleton University", appears solely inside the fetched ecobee web page during this vetting, not
  inside the RT34 report itself).
- Proposal to change the 4J gate: none found.
- Claim that the report was vetted or accepted: none found (Section G explicitly states "I confirmed"
  self-checks, but does not claim external vetting or acceptance).
- Out-of-scope Law 25 mention: see Section 5 above; flagged as a hard-constraint violation, not a
  fellowship/gate/vetted-claim issue.

---

Checked items, tools used: `py` scripts against `api.crossref.org` and `api.openalex.org` (DOIs,
abstracts), `curl` and Python `urllib` (URL status, cross-checked and in agreement on all 9 URLs),
`WebSearch` to locate the real page for four 404s and to check four numeric facts against primary or
near-primary sources.
