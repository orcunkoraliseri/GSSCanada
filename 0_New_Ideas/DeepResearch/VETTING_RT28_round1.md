# Vetting RT28: High-Frequency Surveys with Presence and Work-from-Home Variables

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **The quoted survey questions, the heart of Item 1, are mostly wrong.**
   - `COWMAIN` is class of worker.
   - RECS `HEATHOME` is about heating.
   - The EU variable is `HOMEWORK`, not `HOMEWK`.
   - The SHEU question and its variable `OCCWEEK` were rewritten.
   - Census `DEPART` is not found.
   Six of 10 quotes are not on the pages.
2. **All three use claims are contradicted.**
   - Santiago et al. 2021: national demand fell by 13.49 %; there is no "15 to 22 % residential increase".
   - Cuerdo-Vilches: 256 households, not 920.
   - Bianchi et al.: the data are metered consumption, and the author list has an invented name.
3. **Named surveys dropped silently.** EWCS, EU-SILC, Understanding Society, the Canadian Housing Survey, the Canadian Internet Use Survey and ATUS never appear. The report also presents Census PUMF and SHEU as new sources, though the brief says we already hold them.
4. **Batch finding.** The tool opened no web page for this report.
5. **What survives, checked here on the official pages:**
   - US ACS person file: `JWDP` "Time of departure for work - hour and minute", `JWMNP` "Travel time to work", and `JWTRNS` with code 11 "Worked from home".
   - RECS 2020: `TEMPHOME`, `TEMPGONE` and `TEMPNITE` are setpoints for "when someone is home during the day", "when no one is inside" and "at night". The presence variable is `ATHOME` ("How many weekdays is someone at home most or all of the day?").
   - EU-LFS `HOMEWORK`: "Working at home for the main job", coded mainly, sometimes or never.
   - SHEU 2019, question F17: "In 2019, on an average weekday, was there someone at home all day?" SHEU is already held.
   - The Labour Force Survey added a work-from-home supplement in April 2020.

**What this means for the between-wave survey form (A14, role R2 constrain):** open, with real handles. The pointers above are exact, verified presence and telework questions that can constrain a schedule between time-use waves. The SHEU F17 and RECS `ATHOME` pair is the closest Canadian and US match.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 3 (match 1, wrong author lists 2, not resolved 0); use claims 3 (supported 0,
not in abstract 0, contradicted 3); URLs 3 (opened 3); quoted strings 10 (found 4, not found 6);
numeric facts 8 (confirmed 1, contradicted 7); prompt items 16 named leads (fully answered with a
card 7, silently dropped 7, named in prose only and not carded 2); dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (80 ch) | Title match | CrossRef 1st author, year, container | Report states | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | 10.1016/j.enpol.2020.111964 | 200 | "Electricity demand during pandemic times: The case of the C" | Yes | Santiago, 2021, Energy Policy, vol 148, p111964 | Santiago et al 2021, Energy Policy, matches author order (Santiago, Moreno-Munoz, Quintero-Jimenez, Garcia-Torres, Gonzalez-Redondo) exactly, year, venue, volume, page all match | MATCH |
| D2 | 10.1016/j.scs.2021.103262 | 200 | "Adequacy of telework spaces in homes during the lockdown in" | Yes | Cuerdo-Vilches, 2021, Sustainable Cities and Society, vol 75, p103262 | Report author list "Cuerdo-Vilches, Navas-Martin, Oteiza" is missing a fourth author, Sebastia March, who is on CrossRef. Year, venue, volume, page match | AUTHOR MISMATCH (1 co-author dropped) |
| D3 | 10.1016/j.apenergy.2020.115470 | 200 | "Modeling occupancy-driven building loads for large and dive" | Yes | Bianchi, 2020, Applied Energy, vol 276, p115470 | Report author list "Bianchi, Long, Goldwasser" invents a co-author "N. Long" who is not on CrossRef, and drops three real co-authors (Zhang, Parker, Horsey). Year, venue, volume, page match | AUTHOR MISMATCH (1 invented author, 3 real co-authors dropped) |

Author lists wrong: 2 of 3 (D2, D3). D3 is the more serious case: a named person, "N. Long", does
not appear on the paper at all.

---

## 2. Use claims (Section C, Table C1)

| Row | Claim (what it says the paper did / data used) | Abstract source | Abstract words | Verdict |
|---|---|---|---|---|
| L01 Santiago 2021 | "Analyzed Spanish national electricity demand changes during COVID lockdown and linked them to household telework shifts"; "Data used: Spanish Red Electrica hourly load, mobility indices"; and (Table B1 #6, same paper) "increased Spanish residential electricity consumption by 15% to 22%" | No OpenAlex abstract, no CrossRef abstract field. Verified instead from the PMC full-text mirror (PMC7553070) | Paper reports a **13.49% decrease** in national demand (24 Feb to 30 Apr 2020 vs 5-yr average) from REE grid data recorded every 10 minutes (144 measurements/day, not "hourly"); the only residential example given is one household with 6.74% higher demand. No mention of "mobility indices" was found. Paper does not report any 15-22% residential increase anywhere found | CONTRADICTED (the 15-22% number does not exist in the source; "hourly" and "mobility indices" not confirmed either; NO ABSTRACT via the two prescribed sources) |
| L02 Cuerdo-Vilches 2021 | "Surveyed domestic telework conditions and indoor environmental quality across Madrid households during lockdown"; "Data used: Questionnaire survey in Madrid (920 respondents)" | OpenAlex abstract_inverted_index rebuilt successfully | "an online survey ... for a sample of **256 households** with people teleworking or studying" in Madrid, stratified by gender and income; content is workspace adequacy/perception (space, furniture, lighting, digital resources), not indoor environmental quality as a measured construct | CONTRADICTED (920 vs the abstract's 256; "indoor environmental quality" is not the abstract's framing) |
| L03 Bianchi 2020 | "Modeled occupancy-driven building loads for stock simulation using parametric schedules conditioned on demographic inputs"; "Data used: Survey microdata, DOE prototype models"; "Scale: Urban stock" | No OpenAlex abstract, no CrossRef abstract field. Verified instead from the OSTI mirror (osti.gov/servlets/purl/1660214) | "Occupancy is estimated by the extrapolation of operation times directly from **metered electric consumption data**." Tested on "25,000 commercial buildings in Los Angeles, California." No mention of survey microdata or demographic-input conditioning was found | CONTRADICTED (data source is metered consumption data, not survey microdata; scale is a named city, 25,000 buildings, not generic "Urban stock") |

All 3 use claims contradicted by the source once actually read. This also weakens Section D's premise:
L03 is the report's own evidence that a non-time-use, non-survey (metered) data stream already does
what A14 proposes; the report frames it only as a schedule-modeling paper.

---

## 3. URLs and quotes

### 3a. URLs opened

| URL (Section F) | Status | Notes |
|---|---|---|
| https://www150.statcan.gc.ca/n1/en/catalogue/71M0001X | 200 | LFS PUMF catalogue landing page. No data dictionary or variable list is shown on the page itself; it points to a downloadable zip. Guide to the LFS (71-543-G, 2025) and its questionnaire appendix were also opened; neither mentions work-from-home |
| https://www.eia.gov/consumption/residential/data/2020/ | 200 | RECS 2020 microdata landing page; links to codebook and questionnaire forms (EIA-457A etc.) |
| https://www.census.gov/programs-surveys/acs | 200 | ACS program landing page |

3 of 3 URLs opened (200). Two more sources cited in Section F (SHEU, EU-LFS, EHS) carry **no URL at
all** in the "Source" column, only a document name, so they could not be checked this way; they were
instead traced through search (see 3b).

### 3b. Quoted survey question wording, tested against the actual official page (extra-care item)

| # | Report's quote (variable, wording) | Official page found and opened | What the official page actually says | Verdict |
|---|---|---|---|---|
| Q1 | LFS `COWMAIN` / `TELEWORK`: "Did this person work mainly from home, outside the home, or a combination of both during the reference week?" | Guide to the Labour Force Survey 2025 (71-543-G) and its questionnaire Appendix B (2006-2020 archived version); LFS catalogue page 71M0001X | `COWMAIN` is documented (via a separate search) as **"Class of worker, main job"**, unrelated to work location. The archived questionnaire text has no work-location question at all (StatCan added a WFH supplement only from April 2020). No page seen states this quoted sentence or a variable called `TELEWORK` | NOT FOUND. The variable/question pairing is wrong: `COWMAIN` is not a telework variable |
| Q2 | Census `POWST`: "Place of work status (Worked at home, No fixed workplace, Worked at specified location)" | Statistics Canada Census 2021 Dictionary, "Place of work status" (pop110) | Official categories: "Worked at home (including farms)", "**Worked outside Canada**", "No fixed workplace address", "Worked at the address specified (Usual workplace address)". The report drops the "Worked outside Canada" category and paraphrases the other two; the code `POWST` itself is not shown on this page | NOT FOUND (paraphrase, one category silently dropped) |
| Q3 | Census `DEPART`: "Time leaving for work" | Census 2021 Dictionary "Location of workplace" (pop132) has no such entry; StatCan table titles confirm a "time leaving for work" dimension exists (question 53a) | The concept exists in 2021 Census output, but no page opened shows a variable coded `DEPART` or this exact quoted sentence as a question | NOT FOUND (concept plausible, quote and variable code unconfirmed on any page opened) |
| Q4 | SHEU `OCCWEEK`: "Is someone usually at home during the day on weekdays?" | statcan.gc.ca instrument page for the Households and the Environment Survey: Energy Use, 2019 (instrument 3881_Q2_V7) | The actual question, **F17**: "In 2019, on an average weekday, **was there someone at home all day**?" (Yes / No / Don't know). No variable called `OCCWEEK` appears on the page | NOT FOUND (wording rewritten, variable name unconfirmed) |
| Q5 | RECS `HEATHOME`: "Is your home typically occupied during weekday daytime hours?" | 2020 RECS Household Questionnaire, Form EIA-457A (PDF, text-extracted, 110 pages) | `HEATHOME` is: **"Is your home heated during the winter?"** (a heating-equipment question, asked of all respondents). The actual weekday-presence question is a different variable, `ATHOME`: **"How many weekdays is someone at home most or all of the day?"** | NOT FOUND. This is a wrong variable: the report's quoted presence question is attached to the wrong variable name |
| Q6 | RECS `TEMPHOME`, `TEMPGONE`, `TEMPNITE` (temperature setpoints) | Same 2020 RECS questionnaire PDF | Confirmed at the thermostat section: "When someone is home during the day? [TEMPHOME]", "When no one is inside your home during the day? [TEMPGONE]", "Inside your home at night? [TEMPNITE]" | FOUND |
| Q7 | ACS `JWDP`: "Time of departure for work" | 2024 ACS PUMS Data Dictionary (Census Bureau, PDF, text-extracted) | "Time of departure for work - hour and minute" | FOUND (report's quote is a shortened but accurate version of the real label) |
| Q8 | ACS `JWMNP`: "Travel time to work" | Same dictionary | "Travel time to work" | FOUND (exact) |
| Q9 | ACS `JWTRNS`: "Means of transportation to work (including Worked from home)" | Same dictionary | "Means of transportation to work"; code 11 = "Worked from home" | FOUND (label and category both confirmed) |
| Q10 | EU-LFS `HOMEWK`: "Person working from home (1=Usually, 2=Sometimes, 3=Never)" | EU-LFS Explanatory Notes from Q1 2021 onwards (Eurostat, PDF, text-extracted, 261 pages) | The variable is named **`HOMEWORK`**, not `HOMEWK`. Label: "Working at home for the main job". Codes: "1 Person mainly works at home / 2 Person sometimes works at home / 3 Person never works at home" | NOT FOUND (wrong variable name; codes paraphrased, "mainly" rewritten as "usually") |

Found 4 of 10 (Q6, Q7, Q8, Q9, all in RECS thermostat and ACS commuting rows). Not found 6 of 10,
including every quote attributed to LFS, Census, SHEU and EU-LFS. Two of the six (Q1 and Q5) pair
the quoted question to a **demonstrably wrong variable name** that is documented on an official page
as meaning something else entirely (`COWMAIN` = class of worker; `HEATHOME` = whether the home has
heat at all).

Licence statements: none of Section F's "Access conditions" cells were tested against a licence page
directly (out of scope given the time spent above); flagged for the manager as unchecked.

---

## 4. Key numeric facts

| # | Fact | Report states | Tried | Verdict |
|---|---|---|---|---|
| N1 | LFS started tracking telework | "post-2020 files track telework mode" | StatCan Daily article search: LFS added a WFH supplement in April 2020 | CONFIRMED |
| N2 | Santiago 2021 residential consumption change from telework | "increased ... by 15% to 22%" | PMC full text of the paper | CONTRADICTED (national demand -13.49%; the paper's one household example is +6.74%, not 15-22%) |
| N3 | Cuerdo-Vilches 2021 sample size | "920 respondents" | OpenAlex abstract | CONTRADICTED (256 households) |
| N4 | RECS `HEATHOME` meaning | "Is your home typically occupied during weekday daytime hours?" | RECS 2020 questionnaire PDF, form EIA-457A | CONTRADICTED (it is a heating-equipment question; the real presence variable is `ATHOME`) |
| N5 | EU-LFS variable name for home-working | `HOMEWK` | EU-LFS Explanatory Notes PDF | CONTRADICTED (real name is `HOMEWORK`) |
| N6 | Bianchi 2020 data source | "Survey microdata, DOE prototype models" | OSTI abstract mirror | CONTRADICTED (metered electric consumption data) |
| N7 | SHEU 2019 presence question wording | "Is someone usually at home during the day on weekdays?" | StatCan survey instrument page (3881_Q2_V7) | CONTRADICTED (actual Q F17: "was there someone at home all day") |
| N8 | LFS variable pairing for telework | `COWMAIN` / `TELEWORK` | LFS Guide 2025 and archived questionnaire | CONTRADICTED (`COWMAIN` = class of worker, main job; no page found names a `TELEWORK` variable) |

1 confirmed, 7 contradicted.

---

## 5. Completeness

T28 Item 1 named leads and their status in the report:

| Country | Named lead | Status |
|---|---|---|
| Canada | Labour Force Survey PUMF | ANSWERED (Section F, quote not found, see check 3b Q1) |
| Canada | Census of Population PUMF | ANSWERED (Section F, quote not found, see check 3b Q2/Q3) |
| Canada | Survey of Household Energy Use | ANSWERED (Section F, quote not found, see check 3b Q4) |
| Canada | Canadian Housing Survey | DROPPED (no mention anywhere in the report) |
| Canada | Canadian Internet Use Survey | DROPPED (no mention anywhere) |
| Canada | Any COVID-era StatCan telework survey | DROPPED as a named, separate source (only folded loosely into the LFS row) |
| US | Residential Energy Consumption Survey | ANSWERED (Section F, mixed: temp variables found, `HEATHOME` wrong, see 3b Q5/Q6) |
| US | American Community Survey PUMS | ANSWERED (Section F, quotes found, see 3b Q7-Q9) |
| US | ATUS well-being / leave modules | DROPPED (no mention anywhere, not even "not found") |
| Europe | EU Labour Force Survey | ANSWERED (Section F, wrong variable name, see 3b Q10) |
| Europe | European Working Conditions Survey (EWCS) | DROPPED (no mention anywhere in the report) |
| Europe | EU-SILC | DROPPED (no mention anywhere) |
| Europe | UK English Housing Survey | ANSWERED (Section F row present, but no question quoted at all, only a generic description; violates the brief's hard rule 1, "a paraphrase is not admitted") |
| Europe | Understanding Society | DROPPED (no mention anywhere) |
| Europe | Spain Encuesta de Poblacion Activa | Named in Section A prose only ("Spanish Encuesta de Población Activa"); no Section F card, no quoted question | NOT CARDED |
| Europe | Italy Rilevazione sulle Forze di Lavoro | Named in Section A prose only; no Section F card, no quoted question | NOT CARDED |

Of 16 named leads: 7 answered with a full Section F card (though 6 of those 7 cards carry an
unverified or wrong quote, see check 3b), 7 silently dropped, 2 named only in prose and never carried
into the required card format.

Item 2 (use in building energy, Section C): ANSWERED, 3 rows, but all 3 contradicted on inspection
(check 2).

Item 3 (consistency with time-use surveys, Section G): ANSWERED narratively ("LFS reports
approximately 5% to 10% higher telework prevalence than single-day time-use diaries") but with **no
named study or citation** behind the number; not testable against a source and no DOI or page is
offered for it.

Section F column completeness against brief section 9's data-source card: the brief requires, per
row, custodian, country/geography, years covered and whether still updated, unit, quoted occupancy
variable, temporal resolution, spatial resolution, sample size, roles R1-R4, access route with
eligibility (quoted, dated), licence and redistribution (quoted), known selection bias, and one
verified use-in-building-energy example or `NONE FOUND`. RT28's Section F table (5 columns: survey
name/custodian, periodicity/edition, variable+wording, microdata public, access conditions) carries
**none** of: country/geography as its own column, unit, temporal resolution, spatial resolution,
sample size, R1-R4 roles, licence/redistribution text, selection bias, or a use-in-building-energy
example per row. This is the largest completeness gap in the report.

---

## 6. Dashes

Count via `py`: em dash (U+2014) = 0, en dash (U+2013) = 0.

---

## 7. Rules

- No named individual connected to a fellowship programme was found.
- No proposal to change the 4J gate was found.
- No claim that the report was vetted or accepted was found; Section G explicitly defers vetting to
  "someone else", consistent with brief section 9 rule 7.
- The brief's rule for T19-T38 ("we already hold ... Census PUMF, NRCan SHEU 2019 ... report only
  presence-relevant variables we may not have used, and say so") is not followed: the report cards
  Census PUMF and SHEU as if new, with no statement of what was already held versus newly reported.

---

## Appendix. Notes on method

DOIs checked via `https://api.crossref.org/works/<DOI>`. Abstracts attempted via
`https://api.openalex.org/works/doi:<DOI>` (2 of 3 returned no `abstract_inverted_index`) and via
CrossRef's `abstract` field (0 of 3 present); for the 2 papers with no abstract in either source, the
claim was instead checked against a full-text mirror found by search (PMC for Santiago 2021, OSTI for
Bianchi 2020), noted in each row rather than silently substituted. Official pages for quoted survey
wording were located by web search and opened directly; where a PDF returned unreadable binary via
the fetch tool, the PDF was downloaded and its text extracted locally with `pypdf` before searching it
(RECS 2020 questionnaire, ACS 2024 PUMS data dictionary, EU-LFS Explanatory Notes) so that "not found"
verdicts above reflect an actual text search of the source, not a failed fetch.
