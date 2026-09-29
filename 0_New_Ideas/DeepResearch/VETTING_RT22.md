# Vetting RT22: smart_meter_inferred_occupancy

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The central answer is unsupported.** The accuracy bands by meter resolution in Section A (80 to
   92 %, 70 to 78 %, below 65 %) appear in none of the five cited papers (N1 to N3). Only 1 of 10 use
   claims is supported (U1).
2. **Same defect class as RT19.** 3 of 5 author lists are wrong. Chen et al. 2015 carries two
   invented names, and McKenna and Thomson 2016 has an invented third author. None of the 5 quoted
   variable strings is on its page. The London licence is Creative Commons Attribution, not OGL.
3. **The Canadian part of Item 2 is missing.** The Ontario and Quebec utility data get one prose line,
   with no card, URL or licence. The "8 to 15 % more daytime base load after 2020" figure has no source.
4. **Batch finding.** The tool opened no web page. The Irish trial page is a 404, and the UK smart
   energy research lab page returns a 403.
5. **What survives, checked here:**
   - Jin, Jia and Spanos 2017: about 78 to 93 % presence accuracy for homes.
   - Kleiminger et al. 2013: above 80 %, from 5 households over about 8 months.
   - Low Carbon London: 5,567 households, under a Creative Commons Attribution licence.
   - Chen et al. 2015: a countermeasure against occupancy detection.

**What this means for the smart-meter form (A14):** open. How accuracy falls as meter resolution
drops remains unmeasured by any source that survived. The "no study compares meter presence with a
time-use survey" claim is plausible, but this report's search was too weak to rest a gap on it.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 5 (match 2, wrong author lists 3, not resolved 0); use claims 10 (supported 1,
not in abstract 7, contradicted 0, no abstract 2); URLs 5 (opened 3); quoted strings 5 (found 0);
numeric facts 8 (confirmed 2, contradicted 0); prompt items 4 (dropped 0); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | Report cite | CrossRef status | CrossRef title | Title match | CrossRef authors | Report authors | Author verdict | Year/venue/pages |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 10.1109/tmc.2017.2684806 | Jin, Jia, Spanos 2017, IEEE TMC | 200 | Virtual Occupancy Sensing: Using Smart Meters to Indicate Your Presence | MATCH | Ming Jin; Ruoxi Jia; Costas J. Spanos | Jin, M.; Jia, R.; Spanos, C. J. | MATCH (3/3 authors, order matches) | 2017, IEEE Trans. Mobile Computing 16(11):3264-3277, all match |
| D2 | 10.1016/j.enbuild.2018.11.025 | Razavi, Gharippour, Fleury 2019, Energy Build. | 200 | Occupancy detection of residential buildings using smart meter data: A large-scale study | MATCH | Rouzbeh Razavi; Amin Gharipour; Martin Fleury; Ikpe Justice Akpan (4 authors) | Razavi, R.; Gharippour, A.; Fleury, M. (3 authors) | AUTHOR MISMATCH: 4th co-author Ikpe Justice Akpan dropped; "Gharippour" misspelled (actual: Gharipour) | 2019, Energy and Buildings 183:195-208, match |
| D3 | 10.1145/2528282.2528295 | Kleiminger, Beckel, Staake, Santini 2013, BuildSys | 200 | Occupancy Detection from Electricity Consumption Data | MATCH | Wilhelm Kleiminger; Christian Beckel; Thorsten Staake; Silvia Santini | Kleiminger, W.; Beckel, C.; Staake, T.; Santini, S. | MATCH (4/4 authors) | 2013, Proc. 5th ACM BuildSys, pp. 1-8, match |
| D4 | 10.1109/tsg.2015.2402224 | Chen, Barker, Subbiah, Irwin, Shenoy 2015, IEEE TSG | 200 | Preventing Occupancy Detection From Smart Meters | MATCH | Dong Chen; Sandeep Kalra; David Irwin; Prashant Shenoy; Jeannie Albrecht (5 authors) | Chen, D.; Barker, S.; Subbiah, A.; Irwin, D.; Shenoy, P. | AUTHOR MISMATCH: "Barker, S." and "Subbiah, A." are not on the paper (invented); real co-authors "Kalra, S." and "Albrecht, J." are missing | 2015, IEEE Trans. Smart Grid 6(5):2426-2434, match |
| D5 | 10.1016/j.apenergy.2015.12.089 | McKenna, Krawczynski, Thomson 2016, Appl. Energy | 200 | High-resolution stochastic integrated thermal-electrical domestic demand model | MATCH | Eoghan McKenna; Murray Thomson (2 authors only) | McKenna, E.; Krawczynski, M.; Thomson, M. | AUTHOR MISMATCH: "Krawczynski, M." is invented; paper has only 2 authors | 2016, Applied Energy 165:445-461, match |

Author lists wrong: 3 of 5 (D2, D4, D5). D4 also invents two full names that do not appear on the
paper at all (Barker, Subbiah), a fabrication rather than an omission.

---

## 2. Use claims

Verdicts per spec check 2: SUPPORTED / NOT IN ABSTRACT / CONTRADICTED / NO ABSTRACT.
Razavi et al. 2019 (D2) has no abstract in OpenAlex (`abstract_inverted_index` is null) and no
`abstract` field in CrossRef; all claims resourced to it are NO ABSTRACT.

| # | Claim (report location) | Cited to | Abstract words | Verdict |
|---|---|---|---|---|
| U1 | Table C1 L01: "78% to 93% binary accuracy across residential testbeds" | Jin 2017 | "accuracies of approximately 78 to 93 percent for residences and 90 percent for offices" | SUPPORTED |
| U2 | Table C1 L01: held-out transfer "Yes (models evaluated on unseen homes with 81% accuracy)" | Jin 2017 | Abstract says results are "nearly as accurate as models learned with sufficient data" for the no/limited-training-data case; no 81% figure anywhere in the abstract | NOT IN ABSTRACT |
| U3 | Table C1 L02: "73.4% accuracy (AUC 0.77)" | Razavi 2019 | no abstract available | NO ABSTRACT |
| U4 | Table F1 CER row, "Verified BEM use": Razavi 2019 used the CER dataset | Razavi 2019 | no abstract available | NO ABSTRACT |
| U5 | Table C1 L03: "F1 score of 0.81 to 0.85 on 1-minute data; drops to 0.71 on 15-minute data" | Kleiminger 2013 | "it is possible to achieve occupancy detection accuracies of more than 80%" (no F1 metric, no resolution breakdown, no 0.71 figure) | NOT IN ABSTRACT |
| U6 | Table C1 L03 ground truth: "Tablet-based manual entrance diary kept by residents" | Kleiminger 2013 | "ground-truth occupancy information for 5 households during a period of about 8 months" (5 households/8 months match report's "5 Swiss homes"; tablet/entrance-diary detail not stated) | NOT IN ABSTRACT |
| U7 | Table C1 L04: "87% to 92% true positive presence detection before privacy masking" | Chen 2015 | Abstract describes a countermeasure (water-heater "CHPr") to prevent occupancy detection; states detection "highly correlates with simple statistical metrics" but gives no 87-92% figure at all | NOT IN ABSTRACT |
| U8 | Table B1 row 5: refrigerator cycling / routers / standby loads mask nocturnal presence and cause daytime false positives | Chen 2015 | Abstract mentions "power's mean, variance, and range" as correlating with occupancy; no mention of refrigerators, routers, standby loads, sleep, or false positives | NOT IN ABSTRACT |
| U9 | Table F1 Low Carbon London row, "Verified BEM use": McKenna 2016 validated against measured LCL profiles | McKenna 2016 | "compares its output with three independent validation datasets" (unnamed); LCL is not named in the abstract | NOT IN ABSTRACT |
| U10 | Table F1 Pecan Street row, "Verified BEM use": Jin 2017 used Pecan Street / Dataport data | Jin 2017 | "data from both residential and commercial buildings" (no dataset name given) | NOT IN ABSTRACT |

1 of 10 use claims is supported by the cited abstract's own words. The two headline accuracy tables
(Section A's resolution-tiered accuracy bands, and every specific decimal figure in Table C1 except
the one 78-93% range) rest on numbers that do not appear in any of the five papers' abstracts.

---

## 3. URLs and quotes

Fetched with a browser user agent, 20 s timeout, redirects followed.

| URL (report row) | Status | Notes |
|---|---|---|
| ISSDA CER, `https://www.ucd.ie/issda/data/commissionforenergyregulationcer/` | 404 | page does not exist at this path |
| SERL access, `https://serl.ac.uk/researchers/access/` | 403 | Forbidden; the fetchable response is a generic website accessibility-statement page, not a SERL researcher-access page |
| London Datastore LCL, `https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households` | 200 | redirects to slug `...-vqm0d`; page loads |
| Pecan Street Dataport, `https://www.pecanstreet.org/dataport/` | 200 | page loads, but is a marketing landing page with no data specifications |
| Ausgrid, `https://www.ausgrid.com.au/` | 200 | this is the Ausgrid corporate homepage, not a Solar Home dataset page; no dataset content of any kind is on it |

Double-quoted "occupancy variable" strings (Table F1 column), searched case-insensitive/whitespace-normalised:

| Quote | Page | Result |
|---|---|---|
| "Half-hourly electricity consumption in kWh" | ISSDA CER | PAGE NOT READABLE (404) |
| "Half-hourly electrical energy consumption in kWh" | London Datastore | NOT FOUND (page says "energy consumption, in kWh (per half hour)", a different string) |
| "Half-hourly electricity and gas smart meter telemetry" | SERL | PAGE NOT READABLE (403) |
| "Whole-home and disaggregated circuit real power (W)" | Pecan Street | NOT FOUND |
| "Gross electricity consumption and solar PV generation in kWh" | Ausgrid | NOT FOUND |

Licence claims (not literally quoted in the report table, but stated as fact; checked against the
readable pages):

- London Datastore row states licence "UK Open Government Licence (OGL v2.0)". The page's own
  licence field reads "Creative Commons Attribution" ("licence creative commons attribution last
  update over 4 years ago maintainer uk power networks"). CONTRADICTED. The string "OGL" appears on
  the page only inside unrelated analytics/cookie JavaScript config, not as a licence name.
- Ausgrid row states "Creative Commons Attribution 4.0 International" for the Solar Home dataset.
  Not checkable: the cited URL is the Ausgrid homepage, which contains no mention of this dataset
  or any licence for it at all.
- Pecan Street row states "Dataport Academic Licence". The dataport page links to "Dataport Terms &
  Conditions" and "Dataport Terms of Service" without displaying their content; no licence name
  match possible on this page.
- ISSDA and SERL licence claims: PAGE NOT READABLE (404 / 403).

---

## 4. Key numeric facts

| # | Fact (Section A rests on it) | Attempt | Verdict |
|---|---|---|---|
| N1 | 80-92% accuracy at 1-second to 1-minute resolution | Checked against Jin 2017 (78-93% residential) and Kleiminger 2013 (>80%) abstracts; neither gives this exact band, and Razavi has no abstract | NOT CONFIRMED |
| N2 | 70-78% accuracy at 15-30 minute resolution | No abstract of the 5 cited papers states a resolution-tiered accuracy figure in this band | NOT CONFIRMED |
| N3 | Below 65% accuracy at 60-minute resolution | Same; no abstract states this | NOT CONFIRMED |
| N4 | CER trial: 4,225 households | ISSDA page (source cited) is 404; cannot check against the primary page | NOT CONFIRMED |
| N5 | Low Carbon London: 5,567 households | London Datastore page, quote: "Energy consumption readings for a sample of 5,567 London Households" | CONFIRMED |
| N6 | SERL: approx. 13,000 households | Cited URL (SERL access page) is 403; the page that does load at that address is an unrelated accessibility statement with no household count | NOT CONFIRMED |
| N7 | SERL legally closed to researchers outside the UK (Digital Economy Act 2017) | Cited URL is 403 / unreadable; cannot confirm the legal-eligibility text from the cited source | NOT CONFIRMED |
| N8 | Jin 2017: 78-93% binary accuracy | OpenAlex abstract: "accuracies of approximately 78 to 93 percent for residences and 90 percent for offices" | CONFIRMED |

2 of 8 confirmed. Both of the confirmed facts are simple headline numbers (household count, one
accuracy range); every resolution-tiered accuracy band in Section A, which is the report's central
"how accurate" answer, is unconfirmed from any opened source.

---

## 5. Completeness

T22 prompt items:

| Item | Requirement | Verdict |
|---|---|---|
| 1 | Inference methods & accuracy, Section C, best/typical accuracy and resolution of collapse | ANSWERED (Table C1, Section A), but see section 2/4 above: the resolution-collapse numbers are not confirmable from the cited abstracts |
| 2 | Data-source cards (brief section 9) for named datasets incl. CER, LCL, SERL, Pecan Street, Ausgrid, London Datastore household sets, Ontario/Quebec Green Button or utility releases, any Canadian utility dataset | PARTIALLY ANSWERED. CER, LCL, SERL, Pecan Street, Ausgrid each get a full Section F card. "Ontario and Quebec Green Button or utility research releases" and "any Canadian utility dataset available to university researchers" get only one prose bullet in Table B1 row 4 (no Section F card, no URL, no licence, no eligibility-with-date-checked line as brief section 9 requires) |
| 3 | Occupancy-relevant findings from meters; whether any compared meter-derived presence to a time-use survey | ANSWERED. Time-use comparison sub-question answered as "virtually absent" (ANSWERED AS NOT FOUND). Note: the "8% to 15% increase in daytime base load post-2020" claim cites no DOI, paper, or URL at all ("e.g. California and UK studies", unnamed) |
| 4 | Can meter data generate BEM schedules | ANSWERED AS NOT FOUND, with search description given |

No item is silently dropped, but item 2's Canadian-data sub-requirement is answered in a form (one
fact-table bullet) that does not meet the brief's own data-source card format.

Section F column check against `00_MASTER_BRIEF.md` section 9's required card columns: the report's
Table F1 uses 9 columns (dataset & custodian; country & geography; sample & duration; temporal
resolution; occupancy variable quoted; survey linkage; access & eligibility; licence &
redistribution; verified BEM use). Four columns required by brief section 9 are missing from every
row: **unit** (person/household/dwelling/device/grid cell/area), **spatial resolution** (distinct
from country/geography), **roles R1-R4**, and **known selection bias**. "Whether still updated" is
only implicit in free text ("2018 to present"), not a stated yes/no.

Named leads in the T22 prompt not mentioned anywhere in the report: NILMTK, e-Energy proceedings,
*Energy Informatics* journal.

---

## 6. Dashes

`py` count on the report file: em dashes (U+2014) = 0, en dashes (U+2013) = 0.

---

## 7. Rules

- No named individual connected to a fellowship programme.
- No proposal to change the 4J gate.
- No claim that this report itself was vetted or accepted (Section G item 4 answer states "All
  accuracy figures are quoted directly from the verified primary papers", which section 2 above
  shows is not supported for most of the specific figures, but this is not a claim of external
  vetting/acceptance).

---

## Findings this vetting rests on (concrete, for the manager)

- 3 of 5 DOI author lists are wrong (D2, D4, D5); D4 (Chen et al. 2015) invents two full author
  names, "Barker, S." and "Subbiah, A.", who are not on the paper.
- Of the report's own headline numbers in Section A (the resolution-tiered accuracy bands: 80-92% /
  70-78% / <65%), none is confirmable from any of the 5 cited papers' abstracts; only 2 of 8 checked
  numeric facts and 1 of 10 use claims are confirmed/supported.
- The Low Carbon London row states licence "UK Open Government Licence (OGL v2.0)"; the actual page
  states "Creative Commons Attribution". CONTRADICTED.
- The SERL URL cited for the "legally closed to researchers outside the UK" claim returns 403; a
  differently-rendered fetch of the same URL returns an unrelated website accessibility statement,
  not SERL access-policy content. The access-restriction claim is directionally plausible (SERL's
  UK-only Secure Research Service model is real) but is not confirmed from the cited source.
- The ISSDA CER page (source for the 4,225-household figure and the CER licence) is 404.
- Section F is missing 4 of the columns brief section 9 requires on every row: unit, spatial
  resolution, roles R1-R4, known selection bias.
