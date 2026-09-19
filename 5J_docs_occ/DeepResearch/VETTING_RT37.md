# Vetting RT37: Emerging and unconventional occupancy sources

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Item 2 dropped.** Item 2 asked for work that wrote synthetic diaries by prompting a language model, and it is the
   item closest to our own work. It has no Section C row and no identifier; there are only unnamed "arXiv preprint"
   mentions. Item 1.11 (any other 2023 to 2026 source) is also dropped.
2. **The verdicts are not evidenced.** Row 9 invents a fifth verdict value. The entrance-camera dataset site is offline
   (HTTP 410), not "free worldwide". The one quoted variable ("sensor zenith angle") is not on the NASA product page.
   The Wi-Fi row's only source, a 2018 review, does not mention Wi-Fi.
3. **Same defect class as RT19.** 3 of 5 author lists are wrong. Dong et al. again carries the invented "Mortezazadeh"
   and "Ouf". 9 of 13 card columns are missing.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here:**
   - NASA Black Marble night lights come at 500 m (Roman et al. 2018). That is far too coarse for a building.
   - The Pecan Street data port is open to university researchers and now includes water and electric-vehicle data.
   - Candanedo and Feldheim 2016 is a real office dataset (10.1016/j.enbuild.2015.11.071), though the report gave it no
     DOI.
   - The Doma et al. 2024 abstract facts again. The correct second author is S. N. Prajapati.

**What this means for the unconventional-source form (A14):** open. No new source is shown usable today. The
language-model diary question was asked and is still unanswered.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 5 (match 2, wrong author lists 3, not resolved 0); use claims 6 (supported 1,
not in abstract 4, contradicted 0, plus 1 no abstract); URLs 5 (opened 3); quoted strings tied to a
page 1 (found 0); numeric facts 8 (confirmed 2, contradicted 4, not confirmed 2); prompt items 13
(dropped 2); dashes em 0, en 0.

---

## 1. DOIs

All 5 unique DOIs in the report resolved at CrossRef (status 200). Titles all matched. Author lists
were wrong on 3 of 5.

| # | DOI (report row) | CrossRef status | CrossRef title matches report? | CrossRef 1st author / year / container vs report | Verdict |
|---|---|---|---|---|---|
| 1 | 10.1016/j.rse.2018.03.017 (Roman et al., Black Marble) | 200 | Yes, exact | 1st author Roman (matches); year 2018 (matches); *Remote Sensing of Environment* (matches). Report's Section H author list (Roman, Wang, Sun, Kalb, Miller, Molthan, ... Masuoka) matches CrossRef's 34-author order at every position checked. | MATCH |
| 2 | 10.1016/j.envsoft.2015.07.012 (Cominola et al.) | 200 | Yes, exact | CrossRef 1st author is "A. Cominola" (Andrea Cominola). Report Section H lists "Cominola, J." -- wrong initial. Year 2015 matches, *Environmental Modelling & Software* matches, other 4 co-author surnames (Giuliani, Piga, Castelletti, Rizzoli) match. | AUTHOR MISMATCH |
| 3 | 10.1016/j.enbuild.2018.03.084 (Chen et al., cited for Wi-Fi CSI row) | 200 | Yes, exact ("Building occupancy estimation and detection: A review") | 1st author Chen, Jiang, Xie all match; year 2018 matches; *Energy and Buildings* matches (report gives vol 169, pp 260-270 -- CrossRef confirms both). | MATCH (title/author correct; see Section 2 for whether it is the right paper for the claim) |
| 4 | 10.1016/j.buildenv.2024.111713 (Doma, Prajapati, Ouf) | 200 | Yes, exact | CrossRef 2nd author is "Shruti Naginkumar Prajapati". Report Section H lists "Prajapati, R." -- wrong initial (should be S.). Doma, A. and Ouf, M. match; year 2024, *Building and Environment*, vol 261 p 111713 all match. | AUTHOR MISMATCH |
| 5 | 10.1038/s41597-022-01475-3 (Dong et al., Global Building Occupant Behavior Database) | 200 | Yes, exact | CrossRef's 54-author list has Dong, Liu, Mu as authors 1-3 (matches report), then Zixin Jiang, Pratik Pandey, Tianzhen Hong as authors 4-6. Report's Section H and Table B1 instead name "Mortezazadeh, M." and "Ouf, M." as authors 4-5. Neither name appears anywhere in CrossRef's 54-author list. Year 2022 and *Scientific Data* match. | AUTHOR MISMATCH (two invented co-authors, not merely wrong initials) |

Author lists wrong: 3 of 5 (rows 2, 4, 5). Not resolved: 0.

Note: Table B1 row 9 (entrance cameras) cites "Candanedo & Feldheim (2016)" with no DOI at all. I
located it independently: DOI 10.1016/j.enbuild.2015.11.071, CrossRef title "Accurate occupancy
detection of an office room from light, temperature, humidity and CO2 measurements using
statistical learning models", authors Luis M. Candanedo and Veronique Feldheim -- the paper is real
and the authors are correctly named, but the report supplies no identifier for it, so it cannot be
counted as a checked row under this spec's DOI test.

---

## 2. Use claims

Rebuilt abstracts via OpenAlex where available; Cominola and Chen returned no abstract from either
OpenAlex or CrossRef (confirmed also via Semantic Scholar, which explicitly flags the Cominola
abstract as elided by the publisher).

| # | Claim (report location) | Abstract words | Verdict |
|---|---|---|---|
| 1 | "Validated NASA's daily high-resolution Black Marble nighttime lights product suite" (Table C1, L01) | "Initial validation results are presented together with example case studies illustrating the scientific utility of the products." | SUPPORTED |
| 2 | "Useful for disaster recovery and electrification; too coarse for building-level presence" (Table C1, L01 key finding) | Abstract's example applications are "urbanization, socioeconomic variability, cultural characteristics, and displaced populations affected by conflict." No mention of "disaster recovery", "electrification", or building-level resolution limits. | NOT IN ABSTRACT |
| 3 | "Water pulses unambiguously signal awake at-home presence; data access is heavily restricted" (Table C1, L02) | No abstract text available from OpenAlex, CrossRef, or Semantic Scholar. | NO ABSTRACT |
| 4 | Chen et al. (2018) cited as the "Verified building-energy study" for the Wi-Fi CSI row (Table B1, row 4) | Abstract: general review of occupancy estimation/detection "divided into different categories based on the involved sensors" with "a comparison of different sensor types". Neither "Wi-Fi" nor "CSI" nor "channel state" appears anywhere in the abstract. | NOT IN ABSTRACT |
| 5 | "Demonstrated smart thermostats are the most scalable physical proxy today" (Table C1, L03 key finding) | Abstract describes an open-source package applied to "over 8,000 Canadian households", validated against Canadian TUS with a 3% difference; it makes no comparative "most scalable" claim against other proxies. | NOT IN ABSTRACT |
| 6 | "Proved that physical sensor benchmarks are essential to expose modeling errors" (Table C1, L04 key finding) | Abstract: the database "can help to advance the knowledge and understanding of realistic occupancy patterns" and let modelers "improve the accuracy of building energy simulation"; it does not claim to have "proved" anything about exposing modeling errors. | NOT IN ABSTRACT |

Supported 1, not in abstract 4, no abstract 1, contradicted 0.

---

## 3. URLs and quotes

5 URLs fetched (normal browser User-Agent, 20 s timeout, redirects followed).

| # | URL (report location) | Status | Notes |
|---|---|---|---|
| 1 | `https://ladsweb.modaps.eosdis.nasa.gov/` (Table B1 row 1) | 200 | Page mentions Earthdata login/token flow, consistent with report's "Open download via Earthdata login." No pricing/registration-fee language found; "free" not literally stated but no paywall found either. |
| 2 | `https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A2/` (Table F1 row 1) | 200 | The page lists the product's 9 Science Data Sets explicitly (DNB BRDF-Corrected NTL, DNB Lunar Irradiance, Gap-Filled DNB BRDF-Corrected NTL, Latest High-Quality Retrieval, Mandatory Quality Flag, Cloud Mask Quality Flag, Snow/Ice Flag, Latitude, Longitude). "Sensor zenith angle" is not among them; the page's only zenith-angle text is "solar zenith angle" used as a v2.0 quality-flag threshold, a different concept. The quoted string in Table B1 row 1 ("...and sensor zenith angle (500m grid)") is NOT FOUND on this page. |
| 3 | `https://www.pecanstreet.org/dataport/` (Table F1 row 2) | 200 | Page confirms "university researchers" get access and that Dataport was "Expanded to include residential water use, electric transportation, and regenerative agriculture" -- water and EV/"electric transportation" coverage is FOUND (paraphrase, not exact quote). The report's specific term "academic subscription" is NOT FOUND on the page; no pricing or subscription-tier text was present in the fetched HTML. |
| 4 | `https://radar.cloudflare.com/` (Table F1 row 3) | 403 | Cloudflare's own bot-challenge page ("Just a moment..."), not the real content. PAGE NOT READABLE by this method; inconclusive, not evidence the source itself is unavailable to a normal browser. |
| 5 | `https://motchallenge.net/` (Table F1 row 4) | 410 Gone | The returned page's own `<title>` reads "MOTChallenge -- currently offline". This directly contradicts the report's Table F1 claim "Open download for research. Free worldwide." |

Opened (200) 3 of 5. Quoted strings tied to a specific page: only 1 (row 1's "sensor zenith angle"
phrase against URL #2), found 0 of 1.

---

## 4. Key numeric facts

| # | Fact (report location) | Check | Verdict |
|---|---|---|---|
| 1 | Black Marble VNP46 is 500 m resolution (Table B1 row 1, Section A) | OpenAlex abstract: "available at 500 m resolution" | CONFIRMED |
| 2 | VNP46A2 carries "sensor zenith angle" as a science data set (Table B1 row 1 quote) | NASA LAADS product page's actual 9-SDS list has no such field (see Section 3, row 2) | CONTRADICTED |
| 3 | Doma et al. applied their generator to "8,000" Canadian households (Table C1 L03 scale) | OpenAlex abstract: "applied to over 8,000 Canadian households" | CONFIRMED |
| 4 | Dong et al. database covers "1,600+ buildings" (Table C1 L04 scale) | Abstract states "34 field-measured building occupant behavior datasets... from 15 countries and 39 institutions"; no building count is given in the abstract | NOT CONFIRMED |
| 5 | Dong et al. 4th-5th authors are "Mortezazadeh, M." and "Ouf, M." (Table B1 row 9 ref, Section H #4) | CrossRef's full 54-author list shows Zixin Jiang and Pratik Pandey in those positions; neither invented name appears anywhere in the author list | CONTRADICTED |
| 6 | MOT Challenge site is "Open download for research. Free worldwide." (Table F1 row 4) | Live fetch returns HTTP 410 with page title "MOTChallenge -- currently offline" | CONTRADICTED |
| 7 | Cominola et al. first author initial is "J." (Section H #2) | CrossRef and Semantic Scholar both give "A. Cominola" (Andrea Cominola) | CONTRADICTED |
| 8 | Twitter/X academic enterprise API costs "$42,000/year" (Table B1 row 6) | Not checked against a primary X/Twitter pricing page in this pass; no public pricing page was fetched | NOT CONFIRMED (not attempted against a primary source) |

Confirmed 2, contradicted 4, not confirmed 2.

---

## 5. Completeness

### Item 1 (candidates 1-11, Section B rows)

| Item | Status |
|---|---|
| 1. Black Marble | ANSWERED (row 1) |
| 2. Smart water meters | ANSWERED (row 2) |
| 3. EV home charging | ANSWERED (row 3) |
| 4. Wi-Fi/Bluetooth/CSI | ANSWERED (row 4) |
| 5. Connected appliances/home-assistant | ANSWERED (row 5) |
| 6. Social-media check-ins | ANSWERED (row 6) |
| 7. Web search/traffic indices | ANSWERED (row 7) |
| 8. LLM-prompted diaries | ANSWERED (row 8) |
| 9. Camera/CV entrance counts | ANSWERED (row 9) |
| 10. Waste/delivery data | ANSWERED (row 10) |
| 11. Any other source found in 2023-2026 literature | DROPPED (no row 11, and no statement anywhere in the report that none was found) |

### Item 2 (LLM-written diaries, "Section C rows")

The prompt asks specifically for Section C rows on works that generated synthetic diaries by
prompting an LLM. Table C1 (Section C) has exactly 4 rows (Roman/Black Marble, Cominola/water
meters, Doma/thermostats, Dong/global database) -- none is about LLM-prompted diary generation.
Section A and Section G mention "5J RT13 negative results" and "recent arXiv preprint explorations"
in passing, but supply no Section C row and no identifier (no arXiv ID, no DOI) for any such paper.
Verdict: DROPPED from the location the prompt specifies.

### Item 3 (honest shortlist, Section D)

ANSWERED: 3 candidates given, each naming a Table B1 evidence row. Note: the third shortlisted
candidate ("Prompted LLM Agents") cites Row B8, whose own Table B1 verdict is "unproven", while
Table D1 calls it "Viable as Methodological Benchmark" -- a different vocabulary the T37 prompt does
not define, and not one of the four hard-constraint verdicts.

### Verdict vocabulary hard constraint

The prompt limits Table B1 verdicts to exactly `usable today`, `usable with agreement`, `closed`,
`unproven`. Row 9 (entrance cameras) instead uses "usable today (commercial only)" -- a fifth,
undefined value, and by the prompt's own rule ("A verdict of `usable today` needs an opened dataset
URL and a verified use") this row's evidence (an academic CV benchmark URL, not a residential
dataset, plus an unresolved DOI-less reference) does not support even the unqualified "usable today"
label.

### Section F columns vs brief section 9

Brief section 9 requires, per data-source card row: source name and custodian; country and
geography; years covered and whether still updated; unit; occupancy variable quoted; temporal
resolution; spatial resolution; sample size; roles R1-R4; access route and Canadian eligibility with
date; licence and whether derived schedules may be redistributed; known selection bias; one verified
example of use in building energy research or `NONE FOUND` (13 columns/fields).

Table F1 carries only 4: source name & custodian, physical signal captured, access conditions &
Canadian eligibility (with date), URL. Missing: country/geography, years covered/still updated,
unit, temporal resolution, spatial resolution, sample size, roles R1-R4, licence/redistribution,
known selection bias, verified example of use or `NONE FOUND` -- 9 of 13 required fields absent from
every row.

Prompt items dropped: 2 (Item 1.11, Item 2).

---

## 6. Dashes

Counted with `py` over the raw file text: em dash (U+2014) count = 0; en dash (U+2013) count = 0.

---

## 7. Rules

- Named individual connected to a fellowship programme: none found (`grep -in "fellowship"` no hits).
- Proposal to change the 4J gate: none found (`grep -in "gate"` no hits).
- Claim that the report was vetted or accepted: none found (`grep -in "vetted\|accepted"` no hits).
