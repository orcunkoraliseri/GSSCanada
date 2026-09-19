# Vetting RT25: Day and night population grids

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Both deciding answers are unsupported.** Item 3's only validation number (Leyk et al. 2019,
   "25 to 50 %" error for daytime grids) has no basis in that paper, which is a review (U3). Item 4's
   building-energy claim (Banfi et al. 2024 on floor-area multipliers versus grids) is not what
   that paper's abstract says (U6).
2. **The only Canadian source is wrong.** The table cited as the Canadian commuting-flow table is a
   job-permanency table (N4).
3. **Two author lists carry invented co-authors** (Batista e Silva 2020, Banfi 2024), the same defect class as
   RT19. No licence is quoted, and "CC BY" appears on neither page given. Six of 13 card columns are
   missing from every row.
4. **Batch finding.** The tool opened no web page; two of the pages it marks "checked" are
   JavaScript shells with no readable text.
5. **What survives, checked here:** the European day and night grid (ENACT-POP) is at 1 km
   (its reference year is not confirmed); the WorldPop method gives about 100 m grids (Stevens et al.
   2015); Leyk et al. 2019 is a real review of gridded population products.

**What this means for the day-night grid form (A14):** still open. No error figure and no
building-energy use survive, so this report neither closes nor narrows the form.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 4 (match 4, wrong author lists 2, not resolved 0); use claims 7 (supported 1,
not in abstract 6, contradicted 0); URLs 5 opened (5 opened, of which 2 readable text / 3 not
readable as static HTML); quoted strings 0 (the report contains no double-quoted excerpts
attributed to a fetched page, so none to check); numeric facts 8 (confirmed 2, contradicted 1,
not confirmed 5); prompt items 9 (dropped 0, but Section F is missing 6 of the 13 mandatory
data-source-card columns); dashes em 0, en 0.

## 1. DOIs

| # | DOI | HTTP status (CrossRef) | Report title vs CrossRef title | Report author list vs CrossRef | Year | Container | Verdict |
|---|---|---|---|---|---|---|---|
| D1 | 10.1038/s41467-020-18344-5 | 200, resolved | Match: "Uncovering temporal changes in Europe's population density patterns using a data fusion approach" | Report (Section H): Batista e Silva, Poelman, Vandecasteele, Lavalle, Schiavina. CrossRef actual: Batista e Silva, Freire, Schiavina, Rosina, Marin-Herrera, Ziemba, Craglia, Koomen, Lavalle. "Poelman" and "Vandecasteele" do not appear in the CrossRef author list at all; "Freire", "Rosina", "Marin-Herrera", "Ziemba", "Craglia", "Koomen" are dropped. | 2020, matches | Nature Communications, vol 11, p 4631: matches | AUTHOR MISMATCH |
| D2 | 10.5194/essd-11-1385-2019 | 200, resolved | Match: "The spatial allocation of population: a review of large-scale gridded population data products and their fitness for use" | Report gives "Leyk, Gaughan, Adamo, de Sherbinin, Balk, Freire, ... & MacManus" (2019). CrossRef actual 17-author list: Leyk, Gaughan, Adamo, de Sherbinin, Balk, Freire, Rose, Stevens, Blankespoor, Frye, Comenetz, Sorichetta, MacManus, Pistolesi, Levy, Tatem, Pesaresi. Every named author in the report is a real co-author; the ellipsis correctly drops the middle names, though MacManus is not actually the last author (Pesaresi is). | 2019, matches | Earth System Science Data, vol 11, p 1385-1409: matches | MATCH |
| D3 | 10.3390/en17174400 | 200, resolved | Match: "Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges" | Report (Section H): Banfi, Fabrizio, Causone. CrossRef actual: Banfi, Ferrando, Li, Shi, Causone. "Fabrizio" does not appear in the CrossRef author list at all; "Ferrando", "Li", "Shi" are dropped. | 2024, matches | Energies, vol 17, p 4400: matches | AUTHOR MISMATCH |
| D4 | 10.1371/journal.pone.0107042 | 200, resolved | Match: "Disaggregating Census Data for Population Mapping Using Random Forests with Remotely-Sensed and Ancillary Data" | Report (Section H): Stevens, Gaughan, Linard, Tatem (2015). CrossRef actual: Stevens, Gaughan, Linard, Tatem. Exact match. | 2015, matches | PLOS ONE, vol 10, p e0107042: matches | MATCH |

Count of wrong author lists: 2 of 4 (D1, D3). Both wrong lists contain at least one invented
co-author name not present in CrossRef ("Poelman", "Vandecasteele" for D1; "Fabrizio" for D3) and
drop several real co-authors.

## 2. Use claims

Abstracts rebuilt from OpenAlex `abstract_inverted_index` for all four DOIs; all four had an
abstract.

| # | Claim | Where | Abstract words | Verdict |
|---|---|---|---|---|
| U1 | Batista e Silva 2020 built ENACT-POP using "census, commuting, and tourism data" (Table C1 L01) / "night-time census counts, regional commuting statistics ... school enrolment ... tourism statistics" (Section G) | Table C1, Section G | Abstract: "a multi-layered dasymetric approach that combines official statistics with geospatial data from emerging sources ... at 1 km2 resolution." No input source is named. | NOT IN ABSTRACT |
| U2 | Leyk et al. 2019 "systematically reviewed and compared global gridded population datasets (GHSL, LandScan, WorldPop, GPW)" | Table C1 L02 | Abstract: "presents, compares and discusses a set of large-scale (global and continental) gridded datasets representing population counts or densities." No product is named. | NOT IN ABSTRACT |
| U3 | Leyk et al. 2019 "showed daytime grids exhibit mean absolute percentage errors of 25% to 50% when validated against local micro-censuses or mobile tracking data" (Table B1 row 6, the report's answer to Item 3, validation) | Table B1 #6 | Abstract describes the paper as a review/comparison through a "fitness for use" lens; it states the products "have never been systematically reviewed and compared" before this paper, and does not mention daytime grids, validation against micro-censuses or mobile data, or any error percentage. | NOT IN ABSTRACT (flag: this is the report's sole cited validation number for Item 3 and the abstract gives no basis for it) |
| U4 | Stevens et al. 2015 "developed WorldPop random forest dasymetric mapping framework ... census counts, satellite imagery, road networks" at "100m grids" | Table C1 L03 | Abstract: "a new semi-automated dasymetric modeling approach ... 'Random Forest' estimation technique ... gridded prediction of population density at ~100 m spatial resolution ... case study ... Vietnam, Cambodia, and Kenya." | SUPPORTED |
| U5 | Banfi et al. 2024 "surveyed state of the art in occupant behavior integration within urban building energy modeling ... CityBES, CEA, AutoBEM" | Table C1 L04 | Abstract: "conducting a thorough literature review to examine existing OB modelling techniques ... assessed the flexibility of available UBEM tools." No tool is named. | NOT IN ABSTRACT |
| U6 | Banfi et al. 2024 shows "UBEM frameworks (City Energy Analyst, AutoBEM) rely on building-by-building gross floor area multipliers rather than gridded population rasters to assign occupant headcount" | Table B1 row 7 | Abstract: "current UBEM practices primarily rely on static occupant profiles, due to limitations in the software itself." This is a claim about static vs dynamic occupant-behaviour profiles, not about floor-area multipliers versus gridded population rasters. | NOT IN ABSTRACT |
| U7 | ENACT-POP reference year is 2011, "no post-2020 update released" | Table B1 row 1 | Abstract gives no reference year and no update history. | NOT IN ABSTRACT |

## 3. URLs and quotes

| # | URL / identifier as given in report | Fetch result | Content check |
|---|---|---|---|
| W1 | JRC ENACT-POP dataset, `https://data.jrc.ec.europa.eu/dataset/4b17f8b9-4a4b-4f9e-a89e-4e4c9e4c1122` | HTTP 200 | PAGE NOT READABLE: the response is a Blazor single-page-app shell (20 KB, contains only the generic app chrome and a stock "An unhandled error has occurred" template that is present on every page of this app, not dataset content). No dataset title, resolution, year or licence text is present in the fetched HTML, so none of Table F1's claims for this row could be checked against the page. |
| W2 | JRC GHSL portal, `https://ghsl.jrc.ec.europa.eu/` | HTTP 200, redirects to `https://human-settlement.emergency.copernicus.eu/` | Readable static HTML (15.8 KB, real title "Global Human Settlement - GHSL Homepage"). Searched (case-insensitive) for "CC BY": NOT FOUND on this page. The report's claimed licence ("CC BY 4.0") is not on the page that was actually given. |
| W3 | WorldPop, `https://www.worldpop.org/` | HTTP 200 | Readable static HTML (272 KB, real title "Open Spatial Demographic Data and Research - WorldPop"). Searched for "CC BY": NOT FOUND on this homepage (the licence text, if any, lives on a specific dataset page, not the one given). |
| W4 | ORNL LandScan portal, `https://landscan.ornl.gov/` (named as a lead, no specific licence page given) | HTTP 200 | PAGE NOT READABLE: JavaScript single-page-app shell (672 bytes), contains no text content at all (`<div id="root"></div>`). The report's claim that free academic LandScan access is "restricted to US institutions" could not be checked against any page the report or I could open. |
| W5 | Statistics Canada, Table 98-10-0453-01 (named as the "Commuting Flow Tables" source, Table F1 last row) | HTTP 200, `https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810045301` | Readable static HTML. Page title: "Job permanency by highest level of education, occupation major group, employment income statistics, age and gender: Canada, provinces and territories, census metropolitan areas and census agglomerations with parts." This table has nothing to do with commuting flows or daytime population. CONTRADICTED. |

No double-quoted strings in the report are attributed to a specific fetched page (the access-terms
and licence cells in Table F1 are paraphrased, e.g. "Free worldwide", "Open Licence", not quoted
verbatim from a source), so there is nothing to search for under check 3's quote rule; this itself
is a completeness gap against brief section 9, which requires the licence and eligibility text to
be quoted.

## 4. Key numeric facts

| # | Fact | Verdict | What I tried |
|---|---|---|---|
| N1 | ENACT-POP grid resolution is 1 km2 | CONFIRMED | OpenAlex abstract of D1: "at 1 km2 resolution." |
| N2 | ENACT-POP reference year is 2011, no post-2020 update | NOT CONFIRMED | Abstract has no year; the report's own linked dataset page (W1) is not readable; could not confirm from any source actually opened. |
| N3 | Leyk et al. 2019 found daytime-grid MAPE of 25% to 50% against micro-censuses/mobile data | NOT CONFIRMED (see U3) | Abstract describes a review/comparison paper with no validation-error result reported at all. |
| N4 | Statistics Canada "Commuting Flow Tables" = Table 98-10-0453-01 | CONTRADICTED | Fetched the table's own page (W5); its actual subject is job permanency and employment income, not commuting flows. |
| N5 | LandScan Global academic access is free only to US institutions (East View Geospatial) | NOT CONFIRMED | landscan.ornl.gov (W4) not readable; no East View URL given in the report to check directly. |
| N6 | LandScan HD is restricted to US government/approved researchers, "no retrievable file" for Canada | NOT CONFIRMED | Same as N5; no page opened states this. |
| N7 | WorldPop / Stevens et al. 2015 method resolves population to approximately 100 m grids using Random Forest | CONFIRMED | OpenAlex abstract of D4: "~100 m spatial resolution", "Random Forest" estimation technique. |
| N8 | Banfi et al. 2024 shows UBEM tools use floor-area multipliers rather than gridded rasters | NOT CONFIRMED (see U6) | Abstract frames the finding as static vs dynamic occupant-behaviour profiles, a different claim. |

## 5. Completeness

### T25 prompt items

| Item | Status |
|---|---|
| Item 1: products / data-source cards | ANSWERED (Table F1), but see column gap below |
| Item 2: how day population is modelled (inputs, activity classes, residential separation) | ANSWERED (Section G) |
| Item 3: validation of products (error metric and value) | ANSWERED, but the sole number given (Leyk et al. MAPE 25-50%) is not supported by that paper's abstract (see U3/N3) |
| Item 4: use in building energy | ANSWERED (Table C1 L04, Table B1 row 7), but the Banfi finding is not supported by that paper's abstract as stated (see U6/N8) |
| Section A direct answer | ANSWERED |
| Section D, A14 gap assessment | ANSWERED |
| Hard constraint: grid size and reference year for every product, do not call a 2011-based product current | ANSWERED and respected (report explicitly flags ENACT-POP as frozen at 2011, not current) |
| Hard constraint: say when residential daytime population is not separated | ANSWERED (Table F1 "Residential daytime separated?" column, filled for every row) |
| No em/en dashes | RESPECTED (0 of each, see section 6) |

Nothing was silently dropped at the item level.

### Section F vs brief section 9 mandatory data-source card columns

Brief section 9 requires, for every Section F row (T19-T38): source name and custodian; country and
geography; years covered and whether still updated; unit (person/household/dwelling/device/grid
cell/area); what occupancy variable it actually contains, quoted from documentation; temporal
resolution; spatial resolution; sample size; roles R1-R4; access route and eligibility for a
Canadian-university researcher, quoted with date checked; licence and whether derived schedules may
be redistributed, quoted; known selection bias; one verified example of use in building energy
research or NONE FOUND.

Table F1 has 6 columns: dataset name and custodian; geographic coverage; reference year and grid
resolution (spatial resolution and one year merged into one cell, no separate temporal-resolution
or still-updated field); day/night definitions; residential daytime separation; access terms and
Canadian eligibility (paraphrased, not quoted).

Missing entirely from every Table F1 row: unit; temporal resolution as its own field; sample size;
roles R1-R4; known selection bias; one verified building-energy use example or NONE FOUND per row
(building-energy use is discussed separately in Section C/B1 instead of per-product in Section F).
Present but not quoted verbatim as the brief requires: access/eligibility text, licence and
redistribution terms. This is 6 of 13 required columns entirely absent, which is the wave's largest
completeness gap found so far in this row.

## 6. Dashes

U+2014 (em dash): 0
U+2013 (en dash): 0
(counted with `py` over the report file)

## 7. Rules

No named individual connected to a fellowship programme. No proposal to change the 4J gate. The
report carries no self-verdict and does not claim to have been vetted or accepted, consistent with
brief section 9 rule 7.
