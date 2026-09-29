# 5J — Kickoff Note

Written 2026-09-19, after `D-5J-1` was ruled. Short note only — no methodology is scoped yet. Edit in
place as the paper takes shape; this is not a plan document.

## Update 2026-09-22 — A9 moved to the NSERC proposal; 5J subject reopened

* The author is preparing an NSERC proposal on a subject close to A9. **A9 is therefore reserved for
  that proposal and is no longer the 5J subject.** A9's record below is kept as it stood (it is still
  the best-evidenced angle and the NSERC proposal can draw on it). The A12 companion is unaffected.
* The author asked for a replacement that leans on growing LLM capacity while staying in climate,
  building energy and occupancy, with more originality.
* **Manager proposal (not yet ruled, `D-5J-2`):** A7 in a climate form. An open-weight LLM reads
  Canadian municipal building-permit text (Montreal, Toronto) and recovers each building's retrofit
  and cooling state (heat pump, air conditioning, insulation, windows), gives a set of possible
  answers or abstains when the text is thin, with conformal coverage per archetype. That uncertain
  stock feeds a Canadian building model with GSS occupancy, to show how much the unknown retrofit and
  cooling state changes demand and indoor conditions for the people actually at home. This puts
  occupancy and simulation back into A7, answering its "leaves the series spine" objection
  (`DECISION_5J_angle.md` A7), and keeps it distinct from A9 (no outage survival outcome).
* Why A7: the highest-scoring LLM-centred angle left after the strikes (24.5, `RT12`), four logged
  searches found nothing with abstention, no input blocker (`RT10`). Generator-based LLM ideas (A3,
  A13) stay out: 4J showed the fine-tuned generator losing to a raked donor pool.
* **Ruling 2026-09-22: `D-5J-2` ruled (a) by the author** — the permit-reading A7 climate form is
  the 5J subject, and the permit files are checked first (item 1 below). Result goes in the section
  "Permit file check" at the end of this note.
* **Deep research prompts written 2026-09-22 (author's request):** `DeepResearch/T39` (Canadian
  permit files, all large cities), `T40` (truth on heat pumps, AC, insulation, windows: EnerGuide,
  rebates, HES), `T41` (other record texts, and US permit sets with public truth for benchmarking).
  Brief gained section 10 (the A7 climate form, roles `L1` to `L4`, the record-source card, rules
  learned from the failed rounds: log written at fetch time, tag on every factual sentence, no
  self-grades). README wave 8 and rows added. Folder now 160 entries; at intake expect 2 files per
  report (`RT<NN>_<slug>.md`, `RT<NN>_pages.log`), then one fresh sonnet checker each.
* **Intake 2026-09-22: all three returned (one Gemini session, not three) and all three are FAILED
  ROUND;** routes kept, verdicts in `DeepResearch/VETTING_RT39.md`, `_RT40.md`, `_RT41.md`. Ruling
  and effect on the subject: section "Deep research intake (T39 to T41)" at the end of this note.
* **Unchecked before it is committed to:** (1) whether the permit files actually describe the work
  in text (the `RT17` round-2 Montreal row was invented, so data readiness is not verified) — a
  cheap agent can open the two open-data files; (2) openness of the climate form, which is a new
  wording no search has tested — needs one external Gemini prompt; (3) permit-to-truth labels to
  score the model against.

## Subject, settled

**A9 — passive survivability under power failure, with occupants.** How many hours a neighbourhood
stays inside a habitable indoor band after supply is lost, winter and summer, with uncertainty, and
with occupancy that says who is actually inside.

**A12 — privacy-utility and release protocol**, written in parallel as a short companion paper, built
from 4J's pre-registered membership-inference audit and the partial release that followed it. It
cannot lead: nobody has yet searched whether a protocol like this already exists (`DECISION_5J_angle.md`
S4/S5).

## Why A9

The only surviving angle whose openness was tested by searches that were re-run and independently
confirmed, fits assets already on hand, and has no input blocker (`RT12`, `RT10`). Full reasoning,
scores and strikes: `DeepResearch/DECISION_5J_angle.md`.

## The one condition, checked and cleared

Hobson and Brideau 2026 (ASHRAE, `10.63044/w26hob04`) was A9's nearest neighbour with unknown scope.
Read 2026-09-19: it is a summer-heatwave KPI study with occupancy fixed to NECB 2020's single schedule,
unchanged even during its outage run — never winter, never dynamic or demographic. A9's openness claim
survives; the ruling is not reopened.

## What is NOT yet decided (open for whenever this resumes)

* Methodology: BEM archetype(s), which weather-morphing tool (a real, MIT-licensed package at v2.2.0
  is pinned per `RT12` Q1 — repairs the dead-repository blocker `RT10` had flagged), how occupancy
  varies dynamically by household composition, which KPIs, winter vs. summer vs. both.
* A12's own openness has never been searched (only asserted from a fact we pasted ourselves).
* No angle-by-programme fit table exists anywhere in the series (`RT09` failed both rounds). Two
  survivable facts: NSERC closes 17 October and requires the work to be significantly distinct from
  the doctoral thesis; every 2026 fellowship deadline precedes any possible 5J preprint, so 5J serves
  the 2027 cycle — the subject was chosen on the science, not to fit a 2026 deadline.

## Pointers

* `DeepResearch/DECISION_5J_angle.md` — the ruling and its reasoning.
* `DeepResearch/VETTING_RT12.md` — the ranking report's verdict and six strikes.
* `5J_IDEAS_from_DeepResearch.md` — the fuller synthesis behind A9/A12.
* `PROMPTS/New_ideas_Manager_Prompt.md` — the subject-selection series' full log, if the history behind
  the ruling is ever needed again.

## Permit file check (2026-09-22, sonnet agent)

Mechanical data check only. Files downloaded to
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\a46a4e76-5714-4aae-a52a-ccc10cea537b\scratchpad\permits\`
(temp folder, not in the project; the manager or a later agent should re-download if the files are
needed again).

### Montreal: Permis de construction, transformation et demolition

* Page: https://donnees.montreal.ca/dataset/permis-construction, HTTP 200.
* Licence quoted on the site's licence page (donnees.montreal.ca/pages/licence-d-utilisation):
  "Creative Commons Attribution 4.0 International".
* Update frequency shown on page: "Hebdomadaire" (weekly).
* Date range in the file (date_emission column): 1990-01-03 to 2026-09-14.
* File downloaded: CSV, main resource, 185,762,564 bytes (about 177 MB as shown on the page).
  Direct link: https://donnees.montreal.ca/dataset/d90eaf1b-2de8-43f0-923a-27a620ecdf41/resource/5232a72d-235a-48eb-ae20-bb9d501300ad/download/permis-construction.csv
  (the portal returns HTTP 403 "RBAC: access denied" to a plain curl request with no User-Agent
  header; adding a browser User-Agent and Referer header fixed it).
* Total rows read: 560,309 (the portal's own summary text elsewhere says "about 524,000"; the file is
  larger now, consistent with weekly updates since that number was written).
* Columns: no_demande, id_permis, date_debut, date_emission, emplacement, arrondissement,
  code_type_base_demande, description_type_demande, description_type_batiment,
  description_categorie_batiment, nature_travaux, nb_logements, longitude, latitude, loc_x, loc_y.
* Free-text description column: nature_travaux. Median length 97 characters, 90th percentile 222
  characters, 0 percent of rows empty.
* Residential vs other use: description_type_batiment. Values are messy across decades (mixed
  casing: "Residentiel", "Habitation", "habitation", "HABITATION", "Residentiel-Mixte", etc). Counting
  any value containing "resident" or "habitation" (case and accent insensitive) as residential gives
  420,572 residential rows out of 560,309 (75.1 percent).
* Structured work-type column: description_type_demande (top values by row count): Transformation
  246,311; Transformation combinee 36,146; Construction 28,946; Renovation 14,085; CA - Certificat
  d'autorisation 11,981; Abattage d'arbre 10,577; PL - Plomberie 10,551; Travaux exterieurs 10,050;
  CA- Abattage d'arbre 9,373; Demolition 9,072; Travaux interieurs 8,350; Piscine 6,077; T1:Transformation
  ext/PA/PIIA 5,621; CO - Construction 5,590; MI Modifications Interieures 5,160. This column names the
  permit category (construction, transformation, demolition, tree removal, plumbing, etc), not the
  equipment worked on, so it does not by itself say heat pump/AC/insulation/windows.
* Keyword hits, counted inside the 420,572 residential rows, case and accent insensitive, on
  nature_travaux (a row can match more than one group):
  - heat pump: 2,643
  - air conditioning: 750
  - insulation: 3,605
  - windows: 65,730
  - HVAC general: 482
* Address/identifier: emplacement (free-text street address) present on 100 percent of rows.
  longitude/latitude present on 96.8 percent of rows (542,275 of 560,309); these could link to a
  building footprint directly. arrondissement (borough) is also always present.
* 10 example residential rows matching at least one keyword group (nature_travaux, verbatim, commas
  in the source are literal comma-separated line fragments from the original field):
  1. "RENOVATION EXTERIEUR D'UNE RESIDEN-, CE UNIFAMILIALE., CHANGER LE BARDEAUX D'ASPHALTE., CHANGER LES FENETRES, SANS EN, AJOUTE."
  2. "RENOVATION INTERIEURE D'UNE RESI-, DENCE., CONVERTIR GARAGE EN CHAMBRE A COU-, CHER, MODIFIER PORTE DE GARAGE POUR, MUR AVEC FENETRES ET INSTALLER UNE"
  3. "RENOVATIONS EXTERIEURES SUR MAISON, EN RANGEE., CHANGER TROIS FENETRES ET LA PORTE, D'ENTREE, MEMES OUVERTURES ET MEMES, DIMENSIONS."
  4. "RENOVATIONS EXTERIEURES D'UNE RESI-, DENCE EXISTANTES., REMPLACEMENT DE DEUX FENETRES ET, D'UNE PORTE.REMPLACEMENT DU PAREMENT EXTERIEURE DU MUR ARRIERE POUR"
  5. "RENOVATION EXTERIEUR D'UNE RESIDEN-, CE EXISTANTE., DOIT ETRE CONFORME AU C.N.B. 1990, ET AUX REGLEMENTS MUNICIPAUX., CHANGER TOUTES LES FENETRES DE LA"
  6. "RENOVATIONS EXTERIEURES SUR RESI-, DENCE EXISTANTE., INSTALLATION DE CORNICHES AU DESSUS, DE CERTAINES FENETRES DU R-D-C., CHANGER FENETRE STANDARD MUR AVANT"
  7. "RENOVATIONS EXTERIEURES SUR RESI-, DENCE EXISTANTE., CHANGER 6 FENETRES ET LA PORTE, PATIO [MEMES DIMENSIONS ET MEMES, OUVERTURES]."
  8. "RENOVATION EXTERIEUR D'UNE RESIDEN-, CE EXISTANTE., CHNAGER TROIS FENETRES ET UNE PORTE, D'ENTREE. DE MEME DIMENSIONS., DOIT ETRE CONFORME AU C.N.B. 1990"
  9. "EXPIRATION DU PERMIS 22 AOUT 1994., RENOVATION INTERIEUR D'UNE RESI-, DENCE UNIFAMILIALE EXISTANTE., CHANGER 4 FENETRES ET LES DEUX, PORTES D'ENTREE."
  10. "RENOVATION EXTERIEUR D'UNE RESIDEN-, CE UNIFAMILIALE EXISTANTE, CHANGER SIX FENETRES ET LA PORTE, D'ENTREE., DOIT ETRE CONFORME AU C.N.B. 1990"
* 5 random residential rows matching no keyword group:
  1. "AGRANDISSEMENT / EN COUR ARRIERE 13' X 23'"
  2. "EN FACADE; ELARGIR L'ESCALIER ET LE BALCON AU REZ-DE-CHAUSSEE POUR L'INSTALLATION D'UN SIEGE ESCALIER B.07 DE SAVARIA (LARGEUR LIBRE DANS L'ESCALIER DE 900 MM)"
  3. "RECONSTRUCTION DE QUATRES BALCONS ARRIERE"
  4. "EN COUR ARRIERE, INSTALLER UNE PISCINE HORS-TERRE OVALE DE 12' X 18' ACCESSIBLE PAR UNE ECHELLE SECURITAIRE."
  5. "AMENAGEMENT DE L'ENTREE DE GARAGE - GENEVIEVE TURCOTTE"

Note: this file's nature_travaux text is written by permit clerks in short fragments, often about
exterior/renovation work in general terms; the window and heat-pump keyword hits above mostly come
from lines that explicitly say "changer les fenetres" (window replacement) or similar. Heat pump and
air conditioning terms are comparatively rare (2,643 and 750 hits respectively out of 420,572
residential rows).

### Toronto: Building Permits - Active Permits

* Page: https://open.toronto.ca/dataset/building-permits-active-permits/, HTTP 200. The page's HTML
  contains the word "Retired" in what looks like standard portal filter chrome ("show retired
  datasets"), not a status label on this specific dataset; the CKAN API record for it shows
  last-modified timestamps from today (2026-09-22) and a refresh_rate of "Daily", so it is being kept
  current.
* Licence: CKAN package record reports id "notspecified", title "License not specified". The portal's
  general licence, shown elsewhere on open.toronto.ca, is "Open Government Licence - Toronto"; this
  specific dataset's own licence field is blank.
* Update frequency: "Daily" (CKAN API field refresh_rate).
* Date range in the file (APPLICATION_DATE column): 1983-02-01 to 2026-09-20 (ISSUED_DATE column:
  1985-12-25 to 2026-09-20). The dataset notes data before 1999-10-01 may be incomplete.
* File downloaded: CSV, 69,180,903 bytes.
  Direct link: https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/108c2bd1-6945-46f6-af92-02f5658ee7f7/resource/dfce3b7b-4f17-4a9d-9155-5e390a5ffa97/download/building-permits-active-permits.csv
* Total rows read: 204,592 (matches the CKAN API's own stated record count).
* Columns: _id, PERMIT_NUM, REVISION_NUM, PERMIT_TYPE, STRUCTURE_TYPE, WORK, STREET_NUM, STREET_NAME,
  STREET_TYPE, STREET_DIRECTION, POSTAL, GEO_ID, WARD_GRID, APPLICATION_DATE, ISSUED_DATE,
  COMPLETED_DATE, STATUS, DESCRIPTION, CURRENT_USE, PROPOSED_USE, DWELLING_UNITS_CREATED,
  DWELLING_UNITS_LOST, EST_CONST_COST, ASSEMBLY, INSTITUTIONAL, RESIDENTIAL,
  BUSINESS_AND_PERSONAL_SERVICES, MERCANTILE, INDUSTRIAL, INTERIOR_ALTERATIONS, DEMOLITION,
  BUILDER_NAME.
* Free-text description column: DESCRIPTION. Median length 94 characters, 90th percentile 212
  characters, 0.11 percent of rows empty.
* Residential vs other use, two candidate columns exist:
  - STRUCTURE_TYPE (a category like "SFD - Detached", "Apartment Building", "Office"). Counting rows
    whose STRUCTURE_TYPE names a residential building type (SFD, apartment building, multiple unit
    building, townhouse, duplex/triplex, 2/3+ unit detached or semi, laneway suite, converted house,
    row house; excluding rows explicitly labelled "Multiple Use/Non Residential" or "Mixed Use/Res w
    Non Res") gives 137,585 residential rows out of 204,592 (67.3 percent). This was used as the
    residential set for the keyword counts below because a large share of permits are filed as
    separate mechanical/plumbing sub-permits tied to a residential structure.
  - RESIDENTIAL (a numeric column, floor area in square metres attributed to residential use per
    permit; 0 or blank for most sub-permits). Counting rows where this value is greater than 0 gives
    only 28,263 rows (13.8 percent) because the area breakdown is mostly filled in only on the main
    building permit, not on its linked mechanical/plumbing/drain permits.
* Structured work-type column: WORK (top values by row count): Building Permit Related(PS) 38,589;
  Building Permit Related(MS) 34,232; Interior Alterations 27,872; Multiple Projects 20,751; New
  Building 15,838; Building Permit Related (DR) 10,664; Addition(s) 6,499; Other(BA) 3,533; Backflow
  Prevention Devices (Water only) 2,314; Other(SR) 2,222; Demolition 2,178; Back Water Valve (Sewer
  only) 2,132; Garage 2,131; New Laneway/Rear Yard Suite 1,686; Other(PS) 1,646. PERMIT_TYPE has
  labels like "Mechanical(MS)" and "Plumbing(PS)" that flag HVAC/plumbing sub-permits but not the
  specific equipment; neither column has explicit codes for heat pump, AC, insulation or windows.
* Keyword hits, counted inside the 137,585 residential rows (STRUCTURE_TYPE definition), case
  insensitive, on DESCRIPTION:
  - heat pump: 139
  - air conditioning: 187
  - insulation: 659
  - windows: 4,485
  - HVAC general: 22,907 (this group includes "mechanical", "furnace", "heating"; it is inflated by
    DESCRIPTION text that literally starts with "HVAC -" for every Mechanical(MS) sub-permit, not by
    equipment-specific detail)
* Address/identifier: STREET_NAME present on 99.98 percent of rows; STREET_NUM, POSTAL and GEO_ID
  (a numeric property/parcel identifier) are also columns and could link to a building footprint;
  their fill rate was not separately checked.
* 10 example residential rows matching at least one keyword group (DESCRIPTION, verbatim):
  1. "REV 01 - HVAC - Proposal to finish basement. HVAC - Proposal to construct a new 2 storey single family dwelling and demolish the existing 2 storey single family dwelling"
  2. "HVAC - Proposed 3-storey semi-detached house"
  3. "HVAC - Proposal for a 3 storey addition at the front and interior alterations in the existing semi-detached single family dwelling."
  4. "HVAC - Proposal to demo existing house to construct a new 2 storey duplex."
  5. "HVAC - To demolish existing dwelling and construct a new two storey dwelling"
  6. "HVAC - Proposal for a new SFD-Detached."
  7. "HVAC - Proposal for a 2 level rear addition with an attached deck, interior structural and layout alterations and cosmetic interior alterations."
  8. "HVAC - CONSTRUCTION OF A NEW 2-STOREY MASONRY SFD"
  9. "HVAC - Proposal to construct a new three-storey detached dwelling with an integral garage, a rear deck, a rear basement walkout, a front and rear second storey balcony and a rear third storey balcony."
  10. "REVISION#1: FRONT BAY WINDOW Proposal to construct a new 2 storey single family dwelling with a front porch and rear deck."
* 5 random residential rows matching no keyword group:
  1. "Proposed front & rear one storey addition, interior alterations to existing ground floor, basement underpinning, & new roof over one storey portion."
  2. "Plumbing - proposal to underpin and finish part of the basement"
  3. "Interior renovations - demolition of interior walls, exterior wall finish, enlargement of rear door opening,"
  4. "proposal for adding of 5m2 portico on existing front porch"
  5. "Proposal to install a back water valve and sump pump."

Note: most of the 10 "matched" examples above are generic "HVAC - [main permit description repeated]"
text from the linked Mechanical sub-permit, not a description of what equipment is being installed.
Very few DESCRIPTION strings name a heat pump or AC unit specifically; the keyword counts for heat
pump and AC (139 and 187) are much smaller than the general HVAC bucket (22,907), which is dominated
by this boilerplate "HVAC -" prefix rather than genuine equipment detail.

### Toronto: Building Permits - Cleared Permits (two resources, since 2017 and 2000-2016)

* Page: https://open.toronto.ca/dataset/building-permits-cleared-permits/, HTTP 200. Same CKAN
  licence field as the active-permits dataset: "License not specified" (id notspecified).
* Update frequency: "Daily" (CKAN API refresh_rate), for the "since 2017" resource. The "2000 to
  2016" resource is a static historical export, last modified 2025-07-08.
* Columns (both resources): same set as Active Permits, except the 2000-2016 resource has no _id and
  no BUILDER_NAME column.

**Resource: Cleared Building Permits since 2017**
* File downloaded: CSV, 148,478,326 bytes.
  Direct link: https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9e42a85b-180f-4dc5-b0d7-d46661a6c0ec/resource/b41c3e9e-4d2d-4b09-a789-9569d8da407c/download/cleared-building-permits-since-2017.csv
* Total rows read: 438,965.
* Date range (ISSUED_DATE): 1979-11-27 to 2026-09-17 (some older permits are recorded here even
  though the resource name says "since 2017"; likely re-issued or long-open older permits).
* Free-text description column: DESCRIPTION. Median length 92 characters, 90th percentile 202
  characters, 0.14 percent of rows empty.
* Residential rows by the same STRUCTURE_TYPE rule as Active Permits: 306,116 of 438,965 (69.7
  percent). By the RESIDENTIAL floor-area column instead: 39,702 (9.0 percent).
* Keyword hits inside the 306,116 residential rows, on DESCRIPTION:
  - heat pump: 118
  - air conditioning: 269
  - insulation: 1,363
  - windows: 9,118
  - HVAC general: 51,271
* Address: STREET_NAME present on 100 percent of rows.
* 10 example residential rows matching at least one keyword group:
  1. "Drain - interior alterations to basement & main floor, replace windows"
  2. "Drain - Interior alterations throughout dwelling, layout changes and window alteration in rear of dwelling"
  3. "Drain - Proposal for multiple projects to an existing 3 storey SFD-detched dwelling. Scope of work includes interior alterations, enlarge window openings, fill in window openings and rempove dormer roof."
  4. "Drain - Proposal for multiple projects to an existing SFD-semi dwelling Scope of work includes underpinning, new basement window and interior alterations on the 2nd floor. Basement to remain unfinished."
  5. "Drain - Proposal to construct a new 2-storey detached house with integral garage and install plumbing fixtures, underground services, and install HVAC system."
  6. "Drain - Proposal to construct a new 2-storey detached house with integral garage and install plumbing fixtures, underground services, and install HVAC system." (duplicate entry, two separate permit rows with identical text)
  7. "Drain - Addition of secondary suite in the basement and window enlargement"
  8. "Drain - Proposed second unit dwelling in basement- two(2) enlarged windows including one(1) egress window in basement-two(2) new windows including one(1) egress window in basement"
  9. "Drain - Proposal for interior alterations of two storey house with new basement slab floor, underpinning and new windows and exterior doors."
  10. "Drain - Proposal for interior alterations of basement and ground floor, new rear covered deck and window replacement"
* 5 random residential rows matching no keyword group:
  1. "EXT. ALTERATIONS TO TOWN HOUSE"
  2. "Plumbing - Proposal for underpinning of existing four unit detached dwelling."
  3. "Plumbing - Construct a new two storey dwelling (351.31m2) with attached garage and finished basement (151.7m2)"
  4. "Proposed Back Water Valve (Sewer only)"
  5. "Proposal for in-suite replacement of kitec piping."

**Resource: Cleared Permits 2000 to 2016**
* File downloaded: CSV, 155,623,064 bytes.
  Direct link: https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9e42a85b-180f-4dc5-b0d7-d46661a6c0ec/resource/c647bdae-0127-425e-86e6-2d88ff0e2adf/download/export_202507081211.csv
* Total rows read: 448,093.
* Date range (ISSUED_DATE): 1973-06-07 to 2016-12-29.
* Free-text description column: DESCRIPTION. Median length 76 characters, 90th percentile 166
  characters, 0.39 percent of rows empty (both shorter than the newer resource, consistent with
  older, terser clerk notes).
* Residential rows by the STRUCTURE_TYPE rule: 291,104 of 448,093 (65.0 percent). By the RESIDENTIAL
  floor-area column: 53,331 (11.9 percent).
* Keyword hits inside the 291,104 residential rows, on DESCRIPTION:
  - heat pump: 14
  - air conditioning: 553
  - insulation: 599
  - windows: 4,647
  - HVAC general: 51,207
* Address: STREET_NAME present on 99.99 percent of rows.
* 10 example residential rows matching at least one keyword group:
  1. "REVISE FROM ONE FURNACE TO TWO FURNACE HVAC FOR NEW SFD BUILDING PERMIT NUMBER 114459"
  2. "Install HVAC system to 2nd. & 3rd. fls. refer to appln. # 112891."
  3. "INSTALL HVAC TO A NEW SINGLE FAMILY DWELLING."
  4. "Install high efficiency gas furnace with air conditioning complete with ductwork. cost incl. 118937"
  5. "alter plans approved under #00-119162 by altering window openings and relocating fire shutters on south elevation."
  6. "HVAC to New Single Family Dwelling Refer: B90068"
  7. "Installl and Suplly HVAC system and related Duct Work throughout the Building See BP: 428-754 - Cost Includeed."
  8. "HVAC ORIG PERMIT 99-104355"
  9. "Addition to Single Family Dwelling. HVAC & PLBG. Included."
  10. "Install HVAC system including duct work and 2 new gas furnaces. Cost included in appln. # 119840."
* 5 random residential rows matching no keyword group:
  1. "Backflow Prevention Devices to be installed in a Apartment Building."
  2. "NEW SINGLE FAMILY DWELLING & DEMO"
  3. "Plumbing - SECOND UNIT IN BASEMENT - Second Suite (New)"
  4. "New SFD including Demo"
  5. "Construct platform at front with roof above, alter front elevation and apply new layer of face brick."

Note: only this older resource shows "air conditioning complete with ductwork" as a concrete
equipment-level phrase (example 4 above); most heat pump/AC hits across both Toronto files are
boilerplate "HVAC -" prefixes on sub-permits, not equipment-specific text like the phrase itself.

### Summary across both cities

* Both cities' description fields are real free text (not blank, not codes), with a median length
  around 75 to 100 characters and a 90th percentile around 165 to 220 characters, so there is text
  for a model to read, but it is short (often one sentence or a clerk's fragment list).
* Neither city has a structured column that names heat pump, air conditioning, insulation or window
  work directly; the closest structured columns (description_type_demande in Montreal, WORK and
  PERMIT_TYPE in Toronto) only say the permit category (renovation, mechanical, plumbing, new
  building), not the equipment.
* Window-replacement language is the best-covered keyword group in both cities (65,730 Montreal
  residential rows; 4,485 to 9,118 per Toronto resource). Heat pump and air conditioning language is
  rare in both cities (a few hundred to a few thousand rows each, out of hundreds of thousands of
  residential rows). Toronto's "HVAC general" count is dominated by a literal "HVAC -" text prefix
  Toronto's system stamps on every mechanical sub-permit, not by equipment-specific detail, so it
  overstates how often a model could actually identify heat pump/AC from that group.

### WHAT I DID NOT VERIFY

* Did not check whether Montreal's older rows (pre-2000, "Permis ancien systeme" category) differ
  systematically in text quality or length from newer rows; the median/p90 figures are computed over
  the whole file.
* Did not check the fill rate of Toronto's STREET_NUM, POSTAL or GEO_ID columns, only STREET_NAME.
* Did not verify whether Toronto's GEO_ID or Montreal's longitude/latitude actually align with any
  specific building-footprint dataset (for example Microsoft/Overture footprints); only noted that a
  coordinate or address field exists.
* Did not de-duplicate rows across the Toronto "cleared since 2017" and "cleared 2000-2016" resources
  or against the "active permits" resource; a single physical permit can appear in more than one of
  the three Toronto files as it moves through its lifecycle (application, issue, clearance), so the
  three Toronto row counts are not simply additive.
* Did not check Montreal's GeoJSON or SHP resources, or the Toronto XML/JSON resources; only the main
  CSV resource was downloaded and read for each dataset.
* Did not inspect the Montreal "Statistiques sur les permis" secondary CSV resource.
* Keyword matching is plain substring search on lowercased, accent-stripped text (no stemming beyond
  the literal word stems given in the task, no negation handling, e.g. "no insulation planned" would
  still count as a hit); counts above are literal string-match counts, not a claim about what an LLM
  would actually extract.
* The residential/non-residential split for Toronto is a rule built from the STRUCTURE_TYPE value
  list observed in the active-permits file and applied to all three files; did not exhaustively check
  every distinct STRUCTURE_TYPE value in the two cleared-permits files for residential-sounding
  categories that were missed.
* Did not confirm the meaning of the "Retired" text found on the active-permits HTML page; treated it
  as portal UI chrome based on the CKAN API showing the record as live and updated today, but did not
  trace the page's JavaScript/CSS to be certain.
* Did not check licence terms in detail beyond the name/label shown on each page.

VERDICT (manager, 2026-09-22): **TEXT EXISTS; SUBJECT SURVIVES BUT NARROWS.**
* Item (1) of "Unchecked" is answered: both cities publish real free text on every row, open to
  download, decades deep, with an address on every row and coordinates on 96.8 % of Montreal rows.
  Montreal is CC BY 4.0. Toronto's own licence field is blank; the portal-wide Open Government
  Licence - Toronto must be confirmed as applying before any derived label is released.
* The text is short (median about 75 to 100 characters) and names heat pumps and air conditioning
  rarely: about 0.6 % and 0.2 % of Montreal residential rows, and well under 0.5 % in every Toronto
  file. Windows are common in Montreal (about 16 %), insulation less so. So the permit text can carry
  windows and envelope work; it cannot on its own carry the cooling half of the subject.
* Probable reason, to be settled by `T39` item 1 (not assumed here): many heat-pump and
  air-conditioning installs may need no building permit, so absence from the file means "unknown",
  not "none". This makes abstention the core of the method rather than a feature, and makes a truth
  source (`T40`) the deciding input: **if `T40` finds no per-building or area truth on cooling, the
  cooling half is dropped and the paper narrows to envelope retrofit state.**
* Two design facts for later: Toronto's "HVAC -" prefix on every mechanical sub-permit is boilerplate
  and must be stripped before any count or model input; and the three Toronto files overlap, so rows
  are de-duplicated by permit number before use. Any LLM result must beat a plain keyword baseline on
  the same rows, since window work is already keyword-findable.
* Counts above are substring matches by the checker (no negation handling, French "isolation" also
  covers acoustic and fire separation); none is quotable as a result.

## Deep research intake (T39 to T41), 2026-09-22

All three reports ran in one Gemini session and all three are **FAILED ROUND**: fabricated or
misplaced tags well past the brief's limit of five, invented "verbatim" examples, and (T41) invented
authors on a real DOI. Only rows a fresh sonnet checker confirmed at source are kept. Verdicts:
`DeepResearch/VETTING_RT39.md`, `VETTING_RT40.md`, `VETTING_RT41.md`.

What is now known at source:
* **Permits and cooling (T39).** Montreal's own page says no permit is needed to install a heat pump
  or air conditioner, permanent or removable. Toronto's page says furnace or boiler replacement in a
  house, additional cooling, insulation, and same-opening window replacement in detached,
  semi-detached or row houses need no permit. This settles the "probable reason" in the permit-file
  verdict: a missing permit means unknown, never none.
* **Truth (T40).** No open Canadian file gives heat pump, AC or insulation state per address. The
  EnerGuide open package gives one row per evaluated home with heat pump, AC, furnace and insulation
  columns, at FSA level (first three postal characters), OGL-Canada, 2004 to 2026. StatCan
  38-10-0019-01 (air conditioners) and 38-10-0286-01 (primary heating) give Montreal and Toronto
  shares, 2013 to 2023. EnerGuide homes chose to be audited, so their shares are biased
  [INFERENCE].
* **Other records and benchmarks (T41).** Listing sites are not usable (terms forbid collection).
  Montreal's assessment roll is an open join key (CC BY). New York City (permits plus Local Law 84,
  from 2011) and Chicago (permits plus benchmarking, from 2014) are confirmed outside benchmarks.
* **Prior work.** Gunay et al. 2023 (Building and Environment) mined free-text permit fields in seven
  Canadian cities, over 240,000 entries, for dwelling type, floor area and foundation, with
  association rules. Zhang, Hong, Luo 2020 (SimBuild) ran BERT on San Francisco permits to label work
  type (multi-label, 71 to 84 % by class). Neither reads equipment or retrofit state, uses a language
  model with abstention, or reads French.

VERDICT (manager, 2026-09-22): **SUBJECT HOLDS; COOLING KEPT AT AREA LEVEL; NARROWER NOVELTY.**
* By the rule written in the permit-file verdict, the cooling half is dropped only if no per-building
  or area truth exists. Area truth exists (EnerGuide FSA shares, StatCan CMA tables), so **cooling is
  kept, scored per FSA and per city, not per dwelling.** Permit text is not the main cooling input,
  since no permit is needed; the area shares set the prior and the permit reading updates it where a
  larger job mentions the equipment.
* The per-dwelling reading is scored on envelope and equipment work that does appear in permits
  (windows in Montreal above all), against hand labels on a sample, and against a keyword rule and a
  Gunay-style association-rule baseline. Any claim of novelty rests on four things the prior work did
  not do: retrofit and cooling state, a language model, a set of answers or abstention with stated
  coverage, and French text [INFERENCE].
* Held-out city test: other Canadian cities with a live free-text field (Vancouver, Edmonton, Quebec
  City, Hamilton, Halifax, others) are candidates, each to be measured by us before use; the
  reports' row counts are not quotable. New York City is the outside benchmark with per-building truth.
* Still unchecked: openness of the climate form as worded (no search yet tests "language model plus
  abstention on permit text for retrofit state"); Toronto's licence ("License not specified" on the
  dataset); the EnerGuide file itself, to be opened and counted by us before any design depends on it.
* 2026-09-22 (author's request): the openness search is written as `DeepResearch/T42` (four parts:
  model reads records for retrofit state, abstention with coverage, French text, feeds an energy
  model; Gunay 2023 and Zhang 2020 are its positive controls). Brief section 10 now covers `T39` to
  `T42`. Run alone in a fresh session; at intake one fresh sonnet checker. Folder 170 entries.

INTAKE T42 (manager, 2026-09-22): **FAILED ROUND, OPENNESS HOLDS AS FAR AS SEARCHED.**
* The report (`DeepResearch/VETTING_RT42.md`) gave two accuracy figures its sources do not contain
  and marked unfetched pages as reachable, so it is not admitted as a table.
* Kept at source: both known works were found by real searches. Gunay 2023 handles Montreal French
  with hard-coded keywords, not a language model, and extracts no equipment. Zhang 2020 has no
  abstention and no French. The nearest abstention work, Borrotti 2024 (Energies), applies conformal
  prediction to simulated loads, not to text. Geske and Voelker 2025 carry refurbishment-state
  uncertainty through an urban model in Germany.
* The four-part combination is unclaimed as far as these searches reach [INFERENCE]. Not yet read:
  Wu et al. 2026 Geo2UBEM (SSRN 10.2139/ssrn.7333555, language-model agents inferring urban model
  inputs), Pauling 2026 (SSRN), Jiang et al. 2025 (Energy). Geo2UBEM is the one that could take the
  "language model fills urban model inputs" part; read it before any novelty sentence is written.
* Novelty wording: retrofit and cooling state from French record text, with abstention at stated
  coverage, carried as uncertainty into a stock model with time-use occupancy.

### GEO2UBEM READ (manager, 2026-09-22): DOES NOT TAKE OUR PART, OPENNESS HOLDS

Full text read from the author's copy, `resources/Wu2026_Geo2UBEM_ssrn-7333555.pdf` (24 pages,
preprint, not peer reviewed).
* What it does: street images and GIS give the building shape; a three-agent language model loop
  (Claude Sonnet 4.6) reads simulation results and a national benchmark (CBECS 2018 medians) and
  sets search bounds for seven non-geometric inputs (equipment, lighting, occupant density,
  infiltration, wall U, window U, SHGC). Six Purdue campus buildings, commercial only, pages 6 to 10.
* What it does not do: it reads no record text, infers no retrofit, heat pump or cooling state, has
  no abstention with stated coverage (only a confidence below 0.7 sends a building to human review),
  no French, no housing, and uses DOE reference schedules, not time-use occupancy.
* Nearest overlap: its future work (limitation 6) says a language model "would infer use class from
  street-level imagery, GIS attributes, and permit records". Use class only, and not done.
* Effect: cite it as the nearest language-model-for-urban-model work. The novelty wording above
  stands. Still unread and lower priority: Pauling 2026 (SSRN), Jiang et al. 2025 (Energy).

## Methods design started (2026-09-22)

The working doc is now `5thJ_01_Methods_Design.md` (design v1, gates DRAFT, one author decision
D-5J-3 on who writes the labels). This note stays the subject record; state lives in that doc's
Progress Log.
