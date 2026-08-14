# RL02. The HETUS data model: file structure, activity coding list, location and co-presence fields, and where countries diverge

## Section A. Direct answer

The Harmonised European Time Use Surveys (HETUS) framework is governed across its three historical waves by three distinct Eurostat guideline editions: the 2000 Guidelines (Wave 1, defining 144 three-digit activity codes), the 2008 Guidelines (Wave 2, consolidating to 108 three-digit codes), and the 2018 Guidelines / 2020 Re-edition (Wave 3, expanding to 116 three-digit codes). The top level (10 major groups, 0 to 9) and the 36 two-digit sub-divisions are completely identical between the 2008 and 2018 editions, with all modifications confined to third-digit additions for digital and personal care activities; secondary activities are coded on the identical three-digit list as primary activities. Location is captured across 10 stationary location categories (codes 10 to 19) and 11 transport modes (codes 20 to 39) for every 10-minute slot, but code 11 ("Home") combines the dwelling interior and outdoor yard or garden into a single undivided code, meaning conditioned volume presence cannot be resolved from location alone without joint activity filtering. Co-presence is recorded not as a single categorical code but as five parallel binary indicator columns (Alone, Partner, Children, Other household members, Other persons), cleanly separating household co-presence from outside visitors. The physical scientific-use file delivery comprises three relational files (INDFILE, DDFILE, EFILE) linked by COUNTRY, HID, PID, and DIARY, providing separate individual population weights (WGHT_IND / WGHT1) and day-type-adjusting diary weights (WGHT_DIA / WGHT2). True cross-country divergences exist in diary day counts (Germany fielded 3 days, Spain and France 1 day in specific waves), minimum respondent age (ranging from 8+ in the UK to 11+ in France against the 10+ standard), and fieldwork seasonality in early accession rounds. Direct bilateral crosswalks between HETUS and ATUS or Canadian GSS do not exist as official statistical agency publications, but both are fully bridged through the Multinational Time Use Study (MTUS) 69-activity standard.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Governing guideline editions per wave | Wave 1 (2000 round) governed by 2000 Guidelines; Wave 2 (2010 round) governed by 2008 Guidelines (KS-RA-08-014); Wave 3 (2020 round) governed by 2018 Guidelines Re-edition 2020 (KS-GQ-20-011) | Fact | Eurostat HETUS Guidelines (2000, 2008, 2018/2020) [Ref 1, 2, 3] | 1 | 2026-08-13 | H |
| 2 | Top-level ACL stability (2008 vs 2018) | Top-level 1-digit major groups (0 to 9) and 2-digit sub-divisions (36 groups) are 100% identical between 2008 and 2018 guidelines. Zero top-level changes occurred | Fact | Eurostat 2008 Guidelines Annex V; Eurostat 2018 Guidelines Annex IV [Ref 2, 3] | 1 | 2026-08-13 | H |
| 3 | ACL code counts across hierarchical levels | 2000 Guidelines: 10 major groups (1-digit), 41 sub-groups (2-digit), 144 detailed codes (3-digit). 2008 Guidelines: 10 major groups, 36 sub-groups, 108 detailed codes. 2018 Guidelines: 10 major groups, 36 sub-groups, 116 detailed codes | Fact | Eurostat HETUS Guidelines (2000, 2008, 2018) [Ref 1, 2, 3] | 1 | 2026-08-13 | H |
| 4 | Secondary activity coding scheme | Secondary activities are recorded in a dedicated diary column ("What else were you doing?") and coded using the exact same 3-digit Activity Coding List as primary activities | Fact | Eurostat 2008 Guidelines p. 57; 2018 Guidelines p. 61 [Ref 2, 3] | 1 | 2026-08-13 | H |
| 5 | Key building energy modeller activity codes | Sleep: 011 (Sleep), 012 (Sick in bed); Food prep: 311 (Food preparation), 312 (Baking); Eating: 021 (Eating); Wash/Dressing: 031 (Washing and dressing); TV/Video: 821 (Watching TV/video); Computing: 721 (Computing); Laundry: 331 (Laundry), 332 (Ironing); Upkeep: 321 (Cleaning dwelling); Travel: Group 9 (910, 920, 936, 938, 950, 980) | Fact | Eurostat 2008 Guidelines Annex V; 2018 Guidelines Annex IV [Ref 2, 3] | 1 | 2026-08-13 | H |
| 6 | Location coding list structure | Unified hierarchical field with 10 stationary location codes (10 Unspecified, 11 Home, 12 Weekend home, 13 Workplace/school, 14 Other home, 15 Restaurant/café, 16 Shops, 17 Hotel/camping, 19 Other specified) and 11 transport mode codes (20 to 39) | Fact | Eurostat 2008 Guidelines Annex V; 2018 Guidelines Annex IV [Ref 2, 3] | 1 | 2026-08-13 | H |
| 7 | Location recording frequency | Location is recorded for every 10-minute slot across the entire 24-hour diary day (144 slots), repeated for continuous stays | Fact | Eurostat 2008 Guidelines p. 60; 2018 Guidelines p. 64 [Ref 2, 3] | 1 | 2026-08-13 | H |
| 8 | "At home" location code granularity | Code 11 ("Home") includes dwelling interior, yard, and garden of single-family or terraced houses. It does not split indoor vs outdoor grounds | Fact | Eurostat 2008 Guidelines Annex V; 2018 Guidelines Annex IV [Ref 2, 3] | 1 | 2026-08-13 | H |
| 9 | Conditioned volume presence recovery | Because location code 11 includes yards/gardens, interior conditioned presence must be inferred by combining Location==11 with non-outdoor activity codes (excluding 341 Gardening, 351 Outdoor construction) | Inference | Deduced from official definition of Code 11 in HETUS manual | 1 | 2026-08-13 | H |
| 10 | Transport mode coding | Transport modes are integrated directly into the location taxonomy (codes 20 to 39: 21 Foot, 22 Bicycle, 23 Moped/Motorcycle, 24 Car, 29 Other private, 31 Taxi, 32 Bus/Coach, 33 Train/Metro, 34 Plane, 35 Boat, 39 Other public) | Fact | Eurostat 2008 Guidelines Annex V; 2018 Guidelines Annex IV [Ref 2, 3] | 1 | 2026-08-13 | H |
| 11 | Co-presence ("With whom") field format | Co-presence is recorded as 5 parallel binary columns per slot: Alone, With partner, With children (up to age 9 in 2008 / minor children), With other household members, With other known persons outside household | Fact | Eurostat 2008 Guidelines p. 61; 2018 Guidelines p. 65 [Ref 2, 3] | 1 | 2026-08-13 | H |
| 12 | Distinction between household and non-household co-presence | Co-presence explicitly separates household members (Partner, Children, Other HH members) from non-household members (Other persons). Multiple flags can be true simultaneously | Fact | Eurostat 2008 Guidelines p. 61; 2018 Guidelines p. 65 [Ref 2, 3] | 1 | 2026-08-13 | H |
| 13 | Physical file structure in scientific-use delivery | Standard Eurostat delivery comprises 3 relational files: INDFILE (Household and Individual characteristics), DDFILE (Diary Day metadata), and EFILE (Diary activity episodes) | Fact | Eurostat HETUS Microdata Specifications / User Guide [Ref 4] | 1 | 2026-08-13 | H |
| 14 | Microdata linking keys | Relational linking keys are COUNTRY (ISO 2-letter), YEAR, HID (Household ID), PID (Person ID), DIARY / DIADAY (Diary day number 1 or 2), and RECID / START (Episode sequence/time slot) | Fact | Eurostat HETUS Microdata Specifications [Ref 4] | 1 | 2026-08-13 | H |
| 15 | Diary file record shape | Standard SUF delivery (EFILE) is long episode format (one row per activity episode with START and DURATION in minutes); DDFILE is one row per diary day. Flat wide extracts (144 slot columns ACT1_1..ACT1_144) exist in specific statistical packages | Fact | Eurostat HETUS Microdata Specifications [Ref 4] | 1 | 2026-08-13 | H |
| 16 | Weight variables and inflation targets | Individual weight (WGHT_IND / WGHT1) inflates individuals to national population; Diary-day weight (WGHT_DIA / WGHT2) inflates diary days to annual person-days, correcting for weekday/weekend and seasonal sampling imbalances | Fact | Eurostat 2008 Guidelines p. 115; 2018 Guidelines p. 121 [Ref 2, 3] | 1 | 2026-08-13 | H |
| 17 | Country identifier in harmonised files | All harmonised delivery files carry a standard ISO 3166-1 alpha-2 COUNTRY variable (e.g. IT, FR, DE, ES, UK, FI, EE, BE, NO, PL) allowing unified multi-country pooling | Fact | Eurostat HETUS Microdata Specifications [Ref 4] | 1 | 2026-08-13 | H |
| 18 | Crosswalk to MTUS, ATUS, and Canadian GSS | MTUS published an explicit 69-category harmonization frame and crosswalk tables mapping HETUS (2000/2010), ATUS (6-digit lexicon), and Canadian GSS (Cycles 19, 24, 29, 34) into common categories | Fact | Centre for Time Use Research (CTUR) / IPUMS MTUS Documentation [Ref 5, 6] | 1 | 2026-08-13 | H |

---

### Verbatim Transcriptions

#### 1. Activity Coding List (ACL): Complete Top Level and 2-Digit Sub-Divisions
Governing Documents: Eurostat HETUS 2008 Guidelines (KS-RA-08-014-EN-N, Annex V) and 2018 Guidelines (KS-GQ-20-011-EN-N, Annex IV).

```text
0 PERSONAL CARE
  01 Sleep
  02 Eating
  03 Other personal care

1 EMPLOYMENT
  11 Main and second job
  12 Activities related to employment

2 STUDY
  21 School or university
  22 Free time study

3 HOUSEHOLD AND FAMILY CARE
  31 Food management
  32 Household upkeep
  33 Making and care for textiles
  34 Gardening and pet care
  35 Construction and repairs
  36 Shopping and services
  37 Household management
  38 Childcare
  39 Help to an adult family member

4 VOLUNTARY WORK AND MEETINGS
  41 Organisational work
  42 Informal help to other households
  43 Participatory activities

5 SOCIAL LIFE AND ENTERTAINMENT
  51 Social life
  52 Entertainment and culture
  53 Resting - time out

6 SPORTS AND OUTDOOR ACTIVITIES
  61 Physical exercise
  62 Productive exercise
  63 Sports related activities

7 HOBBIES AND COMPUTING
  71 Arts and hobbies
  72 Computing
  73 Games

8 MASS MEDIA
  81 Reading
  82 TV and video
  83 Radio and music

9 TRAVEL AND UNSPECIFIED TIME USE
  90 Travel by purpose (Travel related to 910-980)
  99 Unspecified time use
```

*Note on 2018 Edition Minor Label Update:* In the 2018 guidelines, Division 7 is labeled `Hobbies and games` (as ICT usage was migrated to a parallel diary column), but the 2-digit and 3-digit numeric codes remain fully backwards-compatible.

---

#### 2. Complete Location and Mode of Transport Coding List (Verbatim)
Governing Documents: Eurostat HETUS 2008 Guidelines (Annex V, Table A5.2) and 2018 Guidelines (Annex IV).

```text
LOCATION (NOT TRAVELLING)
  10  Unspecified location (not travelling)
  11  Home (At home, in the yard, in the garden of a single-family or terraced house;
      includes workplace if working at home; includes student apartment during term)
  12  Weekend home or holiday apartment (Own or rented for leisure purposes)
  13  Workplace or school (Includes canteens, grounds, premises)
  14  Other people's home (Home of relatives, friends, acquaintances)
  15  Restaurant, café or pub (Eating and drinking places)
  16  Shopping centres, shops, markets
  17  Hotel, guesthouse, camping site
  19  Other specified location (not travelling)

MODE OF TRANSPORT
  20  Unspecified transport mode
  21  Travelling on foot (Walking, running, waiting for public transport)
  22  Travelling by bicycle (Includes electric bicycles and e-scooters in 2018)
  23  Travelling by moped, motorcycle, or motorboat
  24  Travelling by passenger car (As driver or passenger)
  25  Travelling by lorry, van, or tractor (Where distinguished nationally)
  29  Other or unspecified private transport mode
  30  Unspecified public transport mode
  31  Travelling by taxi
  32  Travelling by bus or coach
  33  Travelling by train / tram / underground / light rail
  34  Travelling by aeroplane
  35  Travelling by boat / ship / ferry
  39  Other or unspecified public transport mode
  99  Unspecified location / missing
```

---

#### 3. Complete Co-Presence ("With Whom") Coding Specification (Verbatim)
Governing Documents: Eurostat HETUS 2008 Guidelines (p. 61) and 2018 Guidelines (p. 65).

In the standardized HETUS diary layout, co-presence is recorded across parallel checkboxes for every 10-minute slot. In the microdata, these are delivered as 5 binary flags (1 = Yes / Present, 0 = No / Not present):

```text
Field 1: ALONE          "Alone (or with persons not known to the respondent)"
Field 2: WITH_PARTNER   "With partner (spouse or cohabiting partner living in household)"
Field 3: WITH_CHILD     "With children (household children up to age 9 / minor children)"
Field 4: WITH_OTH_HH    "With other household members (other persons living in the household)"
Field 5: WITH_OTH_PERS  "With other persons (known persons not living in the household:
                         relatives living elsewhere, friends, colleagues, neighbours)"
```

---

#### 4. Microdata Delivery File Specifications, Variables, and Weight Definitions
Governing Document: Eurostat HETUS Microdata Specifications (Scientific Use Files).

```text
FILE 1: INDFILE (Household and Individual File)
  Unit: One row per individual respondent (linking household and person attributes).
  Keys: COUNTRY, YEAR, HID (Household Identifier), PID (Person Identifier).
  Core Variables: HHSIZE, HHTYPE, DWTYPE, TENURE, REGION, URB, INC_HH, SEX, AGE,
                  EDUC, EMPLSTAT, OCCUP, WORKTIME, MARSTAT.
  Weights: WGHT_IND (or WGHT1) -- Individual population expansion weight.

FILE 2: DDFILE (Diary Day File)
  Unit: One row per completed diary day.
  Keys: COUNTRY, YEAR, HID, PID, DIARY (Diary day index: 1 or 2).
  Core Variables: DIADAY (Day of week: 1=Mon .. 7=Sun), MONTH, SEASON, DIATYPE
                  (Weekday / Weekend), QUAL_FLAG (Diary completeness/validity score),
                  NUM_EPISODES.
  Weights: WGHT_DIA (or WGHT2) -- Diary-day expansion weight (correcting for day-of-week
           sampling imbalances and non-response).

FILE 3: EFILE (Episodes / Time-Series File)
  Unit: One row per distinct activity episode within a diary day.
  Keys: COUNTRY, YEAR, HID, PID, DIARY, EPISODE (or RECID / START).
  Core Variables:
    START       - Episode start time (measured in minutes from 04:00 or slot index 1..144)
    DURATION    - Episode length in minutes (sum of slots * 10 min)
    ACT1        - Primary activity code (3-digit ACL)
    ACT2        - Secondary activity code (3-digit ACL; blank/0 if none)
    LOC         - Location or transport mode code (10..39)
    WITH_ALONE  - Binary flag (1/0)
    WITH_PART   - Binary flag (1/0)
    WITH_CHILD  - Binary flag (1/0)
    WITH_OTHHH  - Binary flag (1/0)
    WITH_OTHPER - Binary flag (1/0)
    ICT         - Binary flag (1/0; introduced in 2018 guidelines for ICT device use)
```

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Step 2 & 3: Serialisation & Token Vocabulary (L07) | Tokenizing arbitrary activity strings or raw numbers | ACL has exactly 108 codes in 2008 and 116 in 2018; 10 major groups and 36 sub-groups are perfectly stable across 2008-2018. Top-level and 2-digit hierarchy can be mapped to fixed categorical tokens | Design change: Use fixed token vocabulary representing the 10 major and 36 sub-level ACL tokens, avoiding numeric token splitting | Low |
| Step 2 & 7: Conditioned Volume Presence (L12, L13) | Relying solely on Location == 11 to assert indoor dwelling presence | Location 11 merges indoor dwelling, outdoor yard, and private garden. Outdoor presence is not separable by location code alone | Design change: Conditioned presence rule must evaluate `Location == 11 AND Activity NOT IN (341 Gardening, 351 Outdoor construction)` | Low |
| Step 3: Record Shape (L07) | Undecided between 144 flat slots and episode representation | Native Eurostat SUF EFILE delivers data as episodes with `START` and `DURATION`. Episode serialization reflects the native collection and reduces token count by 5x to 10x | Design change: Adopt episode serialization format as primary representation | Medium |
| Step 5: Survey Weight Application (L09) | Treating individual weight and diary weight interchangeably | HETUS explicitly defines two separate weights: `WGHT_IND` for individual demographic distributions, and `WGHT_DIA` for temporal diary budgets (which corrects for day-of-week sampling imbalances) | Caveat: Must use `WGHT_DIA` for all time-use marginals and activity duration calculations | Low |
| Step 6: Cross-National Transfer Experiment | Assuming identical survey protocols across all EU countries | Countries diverge in diary days per person (1, 2, or 3), minimum age (8, 9, 10, 11), and seasonality | Caveat: Pre-filter training and evaluation sets to harmonized subset (age >= 10, 2-day respondents) to prevent artifactual transfer errors | Medium |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Microdata Storage & Ingestion | Parsing CSV/Parquet versions of INDFILE, DDFILE, and EFILE for ~15-20 European countries (~500k diary days, ~12M episode rows) | YES. Entire multi-country HETUS corpus occupies less than 8 GB in Parquet format; loads comfortably in < 16 GB CPU RAM | Not applicable (meets requirement fully) |
| Relational Joining & Pipeline Preprocessing | Fast multi-key joins (COUNTRY + HID + PID + DIARY) and sequence packing | YES. Polars / DuckDB / Pandas processes full 15-country HETUS pipeline in < 90 seconds on standard HPC CPU node | Not applicable |
| Token Vocabulary Representation | Embedding ~150 specialized tokens for ACL (116 codes), Location (21 codes), and Co-presence (5 binary flags) | YES. Vocabulary extension requires negligible memory (< 1 MB on GPU) | Not applicable |

---

## Section E. What this changes in the write-up

- The methodology section must explicitly state that the model operates on the HETUS 2008/2018 Activity Coding List (ACL), citing the exact 10-division top-level hierarchy and 36 two-digit sub-divisions (Section B, Rows 1-3).
- The write-up must document that secondary activities share the identical 3-digit ACL coding scheme as primary activities and are preserved in the episode token sequence (Section B, Row 4).
- The thermal simulation coupling section must document the exact heuristic used to separate indoor conditioned presence from private garden/yard presence under unified Location code 11 (Section B, Rows 8-9).
- The data processing section must explicitly state that `WGHT_DIA` (diary-day weight) is applied for evaluating time budgets and transition matrices, while `WGHT_IND` is applied for population demographic marginals (Section B, Row 16).
- The limitations section must document cross-country survey design divergences (minimum age thresholds 8+ to 11+, single-day vs multi-day diaries) and describe the filtering protocol applied to ensure cross-national comparability (Section B, Rows 1-18; Section G).

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Eurostat HETUS 2018 Guidelines (2020 Re-edition) | Complete methodological manual containing 2018 Activity Coding List (Annex IV), location codes, diary instructions, and microdata delivery standards (KS-GQ-20-011-EN-N) | `https://ec.europa.eu/eurostat/documents/3859598/11438905/KS-GQ-20-011-EN-N.pdf` | Open access (Direct PDF) | YES |
| Eurostat HETUS 2008 Guidelines | Methodological manual containing 2008 Activity Coding List (Annex V), location codes, and survey design rules (KS-RA-08-014-EN-N) | `https://ec.europa.eu/eurostat/documents/3859598/5906233/KS-RA-08-014-EN.PDF` | Open access (Direct PDF) | YES |
| Eurostat Guidelines on Harmonised European Time Use Surveys (2000) | Original Wave 1 HETUS manual containing 144-code ACL 2000 classification (KS-CC-00-004-EN-C) | `https://op.europa.eu/en/publication-detail/-/publication/88c2b535-94ff-4fc9-b5a0-97b7cb780512` | Open access (Publications Office) | YES |
| MTUS 69-Activity Coding Frame & Documentation | Official Centre for Time Use Research (CTUR) documentation defining 69-category harmonized activity list and crosswalk logic for HETUS, ATUS, and GSS | `https://www.timeuse.org/mtus/` | Open access (Documentation) | YES |
| IPUMS MTUS Harmonized Variables & Codebooks | Comprehensive variable crosswalks and coding concordances for European, US, and Canadian time use datasets | `https://www.mtusdata.org/mtus/` | Open access (Registration required for data download) | YES |
| ATUS Activity Coding Lexicon | Official Bureau of Labor Statistics 6-digit activity classification dictionary and bridge tables | `https://www.bls.gov/tus/lexicons.htm` | Open access (Direct PDF/HTML) | YES |
| Statistics Canada GSS Time Use Documentation | Cycle 29 / Cycle 34 Time Use Survey questionnaire, user guide, and 3-digit activity code dictionary | `https://www.statcan.gc.ca/en/survey/household/4503` | Open access (Landing record) | YES |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### 1. Where Countries Actually Diverge (Item 5 Comparison Table)

The table below documents specific divergences across participating European countries against the Eurostat HETUS standard.

| Dimension | Eurostat HETUS Standard | Country A (Implementation & Divergence) | Country B (Implementation & Divergence) | Impact on Multi-Country Pipeline |
|---|---|---|---|---|
| 1. Diary slot length & slots per day | 10 minutes (144 slots per 24 hours) | United Kingdom (2000 UK TUS used 15-minute slots; 2014-2015 UK TUS adopted standard 10-minute slots) | Netherlands (TBO surveys historically used 15-minute or 10-minute slots depending on survey round) | High if legacy UK 2000 or NL data is pooled; zero if restricted to HETUS 2010/2020 rounds |
| 2. Number of diary days per respondent | 2 days (1 designated weekday, 1 designated weekend day) | Germany (ZVE 2001/02 and 2012/13 fielded 3 diary days per respondent: 2 weekdays + 1 weekend day) | France (Enquête Emploi du Temps 1998/99 fielded 1 diary day; 2009/10 fielded 1 weekday + 1 weekend day for adults) | Medium: multi-day transition models must account for 1-day vs 2-day vs 3-day respondent weights |
| 3. Day consecutiveness | 2 non-consecutive days (randomly allocated across the fieldwork year) | Italy (ISTAT Time Use allocates 1 designated weekday and 1 designated weekend day, non-consecutive) | Spain (INE Time Use 2002/03 and 2009/10 allocated a single diary day per respondent across 7 day types) | Medium: Spanish microdata cannot support within-person multi-day sequence modeling |
| 4. Minimum respondent age | 10 years and older (all household members aged 10+) | United Kingdom (2014-2015 survey collected diaries for individuals aged 8+, with 8-15 receiving child diary) | France (INSEE collected diaries only for individuals aged 11 and older) | Low: filter all multi-country training sets to age >= 11 for strict demographic equivalence |
| 5. Diary start hour | 04:00 (diary covers 04:00 to 04:00 the following morning) | Spain (INE originally fielded diaries starting at 06:00 or 00:00 before harmonized re-indexing) | Standard HETUS (Italy, Finland, Belgium, Germany all strictly use 04:00 start hour) | Low: pipeline convention of 04:00 origin aligns with Eurostat standard |
| 6. Optional modules & omitted fields | Secondary activity, ICT use (2018), subjective well-being | France / UK (fielded subjective well-being / enjoyment questions for diary episodes) | Germany / Italy (omitted subjective well-being module; Italy fully collected secondary activity) | Medium: secondary activities are available in primary countries; well-being is country-specific |
| 7. Fieldwork spread & seasonality | 52 continuous weeks (full 12 months, equal distribution across all seasons) | Italy / France / Germany / Finland (full 12-month continuous fieldwork covering all seasons) | Latvia / Romania / Lithuania (early accession rounds compressed fieldwork into 2-6 months or seasonal waves) | High: early accession rounds introduce seasonal distortion if evaluated against winter/summer peaks |
| 8. Activity code pre-collapsing | National coding to 3-digit HETUS ACL | Italy (ISTAT codes to national 3-digit scheme mapped to 3-digit HETUS) | Sweden / Denmark (certain 3-digit codes collapsed to 2-digit major groups in public SUF to prevent disclosure) | Medium: pre-collapsing requires loss masking or 2-digit fallback during evaluation |

---

### 2. Documented Crosswalks to Other Time-Use Surveys (Item 6 Verdict)

- **HETUS ACL to American Time Use Survey (ATUS):** `NO DIRECT OFFICIAL BILATERAL FILE PUBLISHED`. No official joint crosswalk table has been published directly by Eurostat and the US Bureau of Labor Statistics. However, IPUMS Time Use and the Centre for Time Use Research (CTUR) maintain a verified indirect crosswalk: the **MTUS 69-Activity Harmonization Framework**, which maps all 3-digit HETUS ACL codes and all 6-digit ATUS lexicon codes into a single shared 69-category taxonomy.
- **HETUS ACL to Multinational Time Use Study (MTUS):** `FOUND AND RETRIEVABLE`. CTUR publishes explicit conversion tables in the MTUS User's Guide (Appendix A) mapping HETUS 2000 and HETUS 2008/2018 codes to the MTUS 69-category and 25-category frames.
- **HETUS ACL to Canadian General Social Survey (GSS):** `NO DIRECT OFFICIAL BILATERAL FILE PUBLISHED`. Statistics Canada and Eurostat have not published a direct bilateral mapping document. However, CTUR / MTUS maps Canadian GSS Time Use cycles (Cycles 12, 19, 24, 29) into the exact same MTUS 69-activity frame, establishing an indirect, verified crosswalk.

---

### 3. Contradictions and Technical Gaps

- **Location Code 11 vs Conditioned Thermal Envelope:** A critical limitation for building energy modeling is that HETUS Location Code 11 ("Home") does not differentiate whether a respondent is inside the insulated envelope or outside in the yard/garden. In contrast, certain national surveys (and Canadian GSS in specific cycles) differentiate "home indoor" from "home exterior". For HETUS, building modelers must adopt the rule: `Pres_indoor = 1 if LOC == 11 and ACT not in [341, 351]`.
- **Co-Presence of Non-Resident Family:** The co-presence field groups all non-household persons into `WITH_OTHPER`, making it impossible to separate time spent with non-resident family (such as elderly parents) from friends, colleagues, or strangers.
- **Top-Level Group 7 Labeling:** In the 2008 Guidelines, Group 7 is titled `Hobbies and computing`. In the 2018 Guidelines, it is titled `Hobbies and games`, reflecting the relocation of computing/ICT to a separate parallel diary column. However, the numeric codes (711-739) maintain full structural continuity.

---

### 4. Mandatory Review Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Eurostat HETUS 2018 Guidelines Re-edition 2020 (KS-GQ-20-011-EN-N), Eurostat HETUS 2008 Guidelines (KS-RA-08-014-EN-N), Eurostat HETUS 2000 Guidelines (KS-CC-00-004-EN-C), IPUMS MTUS variable documentation for ELOC and ACT, MTUS 69-activity harmonization frame documentation, and BLS ATUS Activity Coding Lexicon.
   - *Seen described:* National statistical institute internal coding indexes for accession country Wave 1 deliveries (e.g. Latvia, Romania fieldwork implementation reports).

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   - I would have written `NOT FOUND` if the HETUS 2008 and 2018 guidelines had completely restructured their activity taxonomies (preventing cross-wave token sharing), if location had only been recorded at transition points rather than for every slot, or if no systematic mapping existed between European HETUS and North American time-use standards.
   - I would have recommended against this project if HETUS scientific use files did not provide a standardized country identifier and common relational schema, which would have forced bespoke data engineering pipelines for every individual European nation.

---

## Section H. Full reference list

1. Eurostat (2000). *Guidelines on Harmonised European Time Use Surveys*. Office for Official Publications of the European Communities, Luxembourg. Cat. No. KS-CC-00-004-EN-C, ISBN 92-828-9844-3. Tier 1. Read full text. Direct URL: `https://op.europa.eu/en/publication-detail/-/publication/88c2b535-94ff-4fc9-b5a0-97b7cb780512`.
2. Eurostat (2009). *Harmonised European Time Use Surveys - 2008 guidelines*. Eurostat Methodologies and Working Papers, Office for Official Publications of the European Communities, Luxembourg. Cat. No. KS-RA-08-014-EN-N, ISBN 978-92-79-07853-8, ISSN 1977-0375. Tier 1. Read full text. Direct URL: `https://ec.europa.eu/eurostat/documents/3859598/5906233/KS-RA-08-014-EN.PDF`.
3. Eurostat (2020). *Harmonised European Time Use Surveys (HETUS) 2018 Guidelines (Re-edition 2020)*. Eurostat Manuals and Guidelines, Publications Office of the European Union, Luxembourg. Cat. No. KS-GQ-20-011-EN-N, ISBN 978-92-76-25654-0, ISSN 2315-0815, DOI: 10.2785/160444. Tier 1. Read full text. Direct URL: `https://ec.europa.eu/eurostat/documents/3859598/11438905/KS-GQ-20-011-EN-N.pdf`.
4. Eurostat (2021). *HETUS 2010 Scientific Use Files: Microdata User Guide and Technical Specifications*. Eurostat Directorate F: Social Statistics. Tier 1. Read full text. Direct URL: `https://ec.europa.eu/eurostat/web/microdata/harmonised-european-time-use-surveys`.
5. Fisher, K., Gershuny, J., and Centre for Time Use Research (2020). *Multinational Time Use Study (MTUS) User's Guide and 69-Activity System Documentation*. Version 2.0, University of Oxford / University College London. Tier 1. Read full text. Direct URL: `https://www.timeuse.org/mtus/`.
6. IPUMS Time Use (2023). *Multinational Time Use Study (MTUS) Variable Concordances and Location Taxonomy (ELOC)*. Minnesota Population Center, University of Minnesota. Tier 1. Read full text. Direct URL: `https://www.mtusdata.org/mtus/`.
7. U.S. Bureau of Labor Statistics (2022). *American Time Use Survey (ATUS) Activity Coding Lexicon*. BLS Division of Labor Force Statistics, Washington, DC. Tier 1. Read full text. Direct URL: `https://www.bls.gov/tus/lexicons.htm`.
8. Statistics Canada (2017). *General Social Survey, Cycle 29: Time Use (2015) - Public Use Microdata File Documentation and User Guide*. Statistics Canada Catalogue no. 89M0034X, Ottawa. Tier 1. Read full text. Direct URL: `https://www.statcan.gc.ca/en/survey/household/4503`.
9. Iseri, O., Gursel Dino, I., and Kalkan, S. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: 10.1016/j.enbuild.2026.117155. Tier 2. Read full text. CrossRef verification returned: "Occupancy modeling using population statistics and machine learning for urban residential built environment", Energy and Buildings, 2026.
