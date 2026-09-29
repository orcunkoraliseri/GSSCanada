# Vetting RT32: time_use_versus_measured_presence

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Four of the five cited studies do not compare a diary with measured presence.**
   - McKenna 2015 is checked against time-use data itself (U3, contradicted).
   - Turley 2020 compares sensor control with fixed setpoints; its "15 to 25 % peak shift" is not there (U7, N5 contradicted).
   - Dong 2022 is a database paper with no false-negative rate (U8).
   - Gerike 2015 runs the opposite way: diary trip counts are higher, not lower (U6, contradicted).
2. **Four prompt items dropped silently:**
   - the hourly and departure/return metrics;
   - whether the populations matched;
   - day-of-week and seasonal coverage;
   - phones left at home.
3. **Same defect class as RT19.** 3 of 5 author lists are wrong. Dong et al. carries two invented names borrowed from the Doma byline. The ECO dataset has 6 households, not 5. No licence or eligibility text is quoted.
4. **Batch finding.** The tool opened no web page. The ecobee page shows no academic agreement or "Concordia eligible" text.
5. **What survives, and it matters:** Doma, Prajapati and Ouf 2024 (Building and Environment, volume **261**, 111713, not 259). Word for word in its abstract:
   - an open-source Python package with a **rule-based** generator (not Markov);
   - "applied to over 8,000 Canadian households" of ecobee data;
   - "validated by comparing them with residential occupancy profiles generated from the Canadian Time Use Survey (TUS)";
   - "3% difference in the aggregated daily occupied hours".
   - The 19.8 against 19.2 hours per day is not in the abstract and is not quoted.
   - Also confirmed: the occupant behaviour database of Dong et al. 2022 (34 field datasets, 15 countries) and Turley 2020's 5.0 % average HVAC saving.

**What this means for A14:**
- **The claim that thermostat presence has been compared with the Canadian time-use survey is now verified, but only as one aggregate number** (daily occupied hours).
- A comparison **by hour of day, by household type, or of first departure and last return** was not found in any surviving source. That narrower form stays open, pending the full text of Doma et al.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 5 (match 2, wrong author lists 3, not resolved 0); use claims 9 (supported 3,
not in abstract 3, contradicted 3); URLs 4 (opened 3, timeout 1); quoted strings 5 (found 5, all are
CrossRef titles; zero quotes attributed to the Section F dataset pages); numeric facts 8 (confirmed
4, contradicted 2, not confirmed 2); prompt items dropped 4; dashes em 0, en 0.

---

## 1. DOIs

| # | DOI | CrossRef status | CrossRef title (80 ch) | Title match | CrossRef authors (family) | Report authors | Year | Container / volume / page | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10.1016/j.buildenv.2024.111713 | 200 | Developing a residential occupancy schedule generator based on smart | Yes | Doma, Prajapati, Ouf | Doma, Prajapati, Ouf | 2024 matches | Building and Environment; CrossRef vol **261**, report states vol **259**; page 111713 matches | MATCH (volume stated wrong: 259 vs CrossRef 261) |
| 2 | 10.1016/j.enbuild.2015.03.013 | 200 | Four-state domestic building occupancy model for energy demand simul | Yes | McKenna, Krawczynski, Thomson | McKenna, Krawczynski, Thomson | 2015 matches | Energy and Buildings, 96, 30-39, all match | MATCH |
| 3 | 10.3390/en13205396 | 200 | Development and Evaluation of Occupancy-Aware HVAC Control for Resid | Yes | Turley, Jacoby, Pavlak, Henze | Turley, Bilionis, Karava, Tzempelikos | 2020 matches | Energies 13(20) 5396 matches | AUTHOR MISMATCH (3 of 4 co-authors wrong: report invents Bilionis, Karava, Tzempelikos; real co-authors are Jacoby, Pavlak, Henze) |
| 4 | 10.1038/s41597-022-01475-3 | 200 | A Global Building Occupant Behavior Database | Yes | Dong, Liu, Mu, Jiang, Pandey, Hong, ... (56 authors total) | Dong, Liu, Mu, Mortezazadeh, Ouf | 2022 matches | Scientific Data, vol 9, article 369 (no "page" field at CrossRef, consistent with an article number) | AUTHOR MISMATCH (report drops 52 real co-authors and invents 2 who are not on the paper: Mortezazadeh, Ouf) |
| 5 | 10.1016/j.tra.2015.03.030 | 200 | Time use in travel surveys and time use surveys ... Two sides of the same coin? | Yes | Gerike, Gehlert, Leisch | Gerike, Gehlert, Schulz | 2015 matches | Transportation Research Part A, 76, 4-24, all match | AUTHOR MISMATCH (3rd author invented: report says "Schulz", CrossRef says "Leisch") |

Wrong author lists: 3 of 5 (Turley, Dong, Gerike). Note the "Ouf" and "Mortezazadeh" names invented
for the Dong et al. paper are real co-authors of the Doma et al. paper cited two rows above it in the
same report, consistent with cross-paper author bleed rather than a lookup of the actual byline.

---

## 2. Use claims

Abstracts rebuilt from OpenAlex `abstract_inverted_index`.

| # | Claim (where) | Claim text | Abstract words | Verdict |
|---|---|---|---|---|
| U1 | Table C1 L01, "What it did" | "Developed Markov schedule generator from ecobee data" | "this study introduces an open-source Python package... a rule-based framework that addresses the limitations of relying on motion-detection data" | CONTRADICTED (abstract says rule-based, not Markov; Markov chain is the method of the McKenna paper, not Doma) |
| U2 | Table C1 L01 / Table B1 row 1 | "compared presence against Statistics Canada GSS Time Use" / 3% difference | "validated by comparing them with residential occupancy profiles generated from the Canadian Time Use Survey (TUS)... 3% difference in the aggregated daily occupied hours" | SUPPORTED |
| U3 | Table C1 L02, "What it did" | "evaluated against measured domestic electricity loads" | "The model is constructed from and verified against UK time-use survey data" (no mention of electricity loads or smart meters anywhere in the abstract) | CONTRADICTED |
| U4 | Table C1 L03, "What it did" | "Evaluated occupancy-driven HVAC setback controls using smart thermostat and motion sensor presence logs" | "Occupancy-aware HVAC control... connected thermostat, which already include occupancy sensors... hybrid HVAC control" | SUPPORTED |
| U5 | Table C1 L04, "What it did" | "Compiled and published global building occupant behavior database across 34 field studies" | "a database of 34 field-measured building occupant behavior datasets collected from 15 countries" | SUPPORTED |
| U6 | Table B1 row 3, attributed to Gerike et al. 2015 | "Diary respondents systematically omit short out-of-home trips... under-reporting trip episodes by 15% to 25%" | "The number of trips per person is higher in the German TUS when changes in location without a trip are included... TUS provide reliable travel estimates. The number of trips even seems preferable to NTS" (direction is the opposite: diary trip counts are higher, not lower, than the comparator survey; no 15-25% figure anywhere) | CONTRADICTED |
| U7 | Table B1 row 7, attributed to Turley et al. 2020 | "shifts simulated peak heating/cooling loads by 15% to 25% due to sudden setback recovery transients" | Abstract reports "savings on average of 5.0%" and "between 1% and 13.3%"; no peak-load-shift number; no comparison against diary-derived schedules anywhere (comparator is "manually-adjusted or constant setpoint temperatures") | NOT IN ABSTRACT |
| U8 | Table B1 row 5, attributed to Dong et al. 2022 | "registering false-negative vacancies of 20% to 40% during nighttime hours" | Abstract describes the database's contents (occupancy patterns, device interactions) but gives no PIR false-negative rate | NOT IN ABSTRACT |
| U9 | Table C1 L04, "Reported discrepancy" | "Measured field occupancy exhibited 35% to 55% greater temporal variance than code schedules" | No such figure or comparison to code schedules in the abstract | NOT IN ABSTRACT |

Material point: of the 5 references used to build Section A's headline, only Doma et al. (2024) is an
actual empirical comparison of a time-use diary against a measured presence source. McKenna (2015)
validates its model against time-use data itself, not against measured presence. Turley (2020)
compares occupancy-sensor-driven HVAC control against constant-setpoint control, not against diary
schedules. Dong et al. (2022) is a database-compilation paper, not a comparison study. Gerike (2015)
compares two self-report surveys (a travel diary and a time-use diary) against each other, not a
diary against a measured source, and its own finding runs in the opposite direction from the one
the report attributes to it.

---

## 3. URLs and quotes

| # | URL | Status | Notes |
|---|---|---|---|
| 1 | https://www.ecobee.com/en-ca/donate-your-data/ | 200 | Page text searched (case-insensitive) for "academic", "8,000", "8000", "Concordia", "CC BY", "licence": none found. The report's claim "Academic agreement with ecobee DYD program... Concordia eligible" is not a quote and is NOT FOUND on the page. |
| 2 | https://www.vs.inf.ethz.ch/res/show.html?what=eco-data | 200 | Page text: "It was collected in 6 Swiss households over a period of 8 months." Report's Section F states "5 households; 8 months". Household count NOT FOUND as stated (page says 6, not 5); "8 months" FOUND. |
| 3 | https://www.cmpe.boun.edu.tr/aras/ | timeout (2 attempts, 15-30 s) | PAGE NOT READABLE. Report labels this source's access route "Open download via web archive" but gives the live institutional URL, not an archive.org URL; the two are inconsistent with each other. |
| 4 | https://doi.org/10.1038/s41597-022-01475-3 (Section F licence cell for the Dong dataset) | 200, redirects to nature.com | Page body retrieved is 3,036 characters (JS-rendered shell), too short to contain the article text. PAGE NOT READABLE for the "CC BY 4.0" licence claim; could not confirm or contradict it this way (Scientific Data articles are conventionally CC BY 4.0, but that is a convention, not a reading of this page). |

Quoted strings: the only double-quoted strings anywhere in the report are the 5 CrossRef titles
placed next to each DOI in the reference list (Section H), all 5 of which match CrossRef's returned
title (see Section 1 above). No double-quoted string is attributed to any of the four Section F / URL
sources, which means the access-eligibility and licence statements in Section F are asserted, not
quoted from a page, despite `00_MASTER_BRIEF.md` section 9 rule 4 requiring terms to be "quoted, not
summarised."

---

## 4. Key numeric facts

| # | Fact | Where in report | Check | Verdict |
|---|---|---|---|---|
| 1 | 8,000+ Canadian homes in the ecobee study | Section A, Table B1 row 1, Table C1 L01 | OpenAlex abstract: "applied to over 8,000 Canadian households" | CONFIRMED |
| 2 | 3% difference in aggregate daily occupied hours | Section A, Table B1 row 1 | OpenAlex abstract: "3% difference in the aggregated daily occupied hours" | CONFIRMED |
| 3 | 19.8 h/day (GSS) vs 19.2 h/day (ecobee) | Section A, Table B1 row 1 | Not stated anywhere in the OpenAlex or CrossRef abstract text; only the aggregate 3% figure is given, no absolute hour values | NOT CONFIRMED (abstract does not carry this level of detail; full text not opened) |
| 4 | Diaries underestimate midday intermittency by 12% to 18% | Section A | No source cited for this number in Section A; not present in any of the 5 abstracts checked | NOT CONFIRMED |
| 5 | Peak heating/cooling loads shift by 15% to 25% when diary schedules are replaced by measured sensor schedules | Section A, Table B1 row 7 (sourced to Turley 2020) | Turley abstract gives 5.0% average and 1% to 13.3% range, for sensor-driven control vs constant setpoint, not diary vs sensor | CONTRADICTED |
| 6 | Turley et al. HVAC energy savings about 5% | Table C1 L03 | Abstract: "savings on average of 5.0%" | CONFIRMED |
| 7 | ECO dataset: 5 households | Section F, Table F1 | ETH page: "collected in 6 Swiss households" | CONTRADICTED |
| 8 | Global Building Occupant Behavior Database: 34 field studies across 15 countries | Section F, Table F1 / Table C1 L04 | OpenAlex abstract: "34 field-measured building occupant behavior datasets collected from 15 countries and 39 institutions" | CONFIRMED |

---

## 5. Completeness

### Against `T32_time_use_versus_measured_presence.md`

| Prompt item | Verdict | Note |
|---|---|---|
| Item 1: direct comparisons, countries/years, two sources, metric | ANSWERED | Table C1 L01-L04 |
| Item 1: "at-home share by hour, time of first departure and last return" as metrics | DROPPED | Only "daily hours" is reported anywhere; no hourly-share or first-departure/last-return metric appears for any row |
| Item 1: "whether the populations were the same people, matched, or only comparable" | DROPPED | No column or sentence in Table C1 addresses population overlap for any of the 4 rows |
| Item 2: rounding to hour/half-hour | ANSWERED | Table B1 row 2 |
| Item 2: under-reporting of short episodes/trips | ANSWERED (but see use-claim U6: the cited source contradicts the direction claimed) | Table B1 row 3 |
| Item 2: single-day problem | ANSWERED | Table B1 row 4 |
| Item 2: day-of-week and seasonal coverage | DROPPED | Not mentioned anywhere in the report |
| Item 2: non-response by people who are rarely home | DROPPED | Not mentioned anywhere in the report |
| Item 3: sensors missing sleepers | ANSWERED | Table B1 row 5 |
| Item 3: thermostats in owner-occupied detached homes only | ANSWERED | Table B1 row 6 |
| Item 3: phones not at home with the person | DROPPED | Not mentioned; no source in the report discusses phone-based location data at all |
| Item 4: energy/peak consequence works | ANSWERED (but the cited study, Turley, does not do a diary-vs-measured comparison; see U7) | Table B1 row 7, Table C1 L03 |
| Section A: "how many studies... and in which direction" | ANSWERED | States fewer than 3; states no consistent adverse direction (vindicates diaries on volume) |
| Section D: A14 assessment | ANSWERED | Table D1 |
| Section G: negative controls | ANSWERED | All 4 standard questions present |

Dropped count: 4 (hourly/departure-return metric, population-match column, day-of-week/seasonal
coverage, phone-based measured-source bias).

### Against `00_MASTER_BRIEF.md` section 9 (Section F data-source card columns)

Required columns: source name and custodian; country and geography; years covered and whether still
updated; unit (person/household/dwelling/device/grid cell/area); what occupancy variable it actually
contains (quoted from documentation); temporal resolution; spatial resolution; sample size; roles R1
to R4; access route and eligibility for a Canadian-university researcher (quoted, dated); licence and
whether derived schedules may be redistributed (quoted); known selection bias; one verified example of
use in building energy research, or NONE FOUND.

Table F1 actual columns: Benchmark dataset | Custodian & country | Sample size & monitoring span |
Sensor modalities | Access route & Canadian eligibility (Checked: 2026-09-18).

Missing columns: years covered / still updated; unit; occupancy variable quoted from documentation;
temporal resolution and spatial resolution as separate fields; roles R1 to R4; licence and
redistribution terms (quoted); known selection bias as a table column (it appears only as prose in
Section G, not per-row in Table F1); one verified example of use in building energy research or NONE
FOUND (no row states this, even though the whole report's subject is such uses).

---

## 6. Dashes

`py` count on `RT32_time_use_versus_measured_presence.md`: em dash (U+2014) = 0, en dash (U+2013) = 0.

---

## 7. Rules

- No named individual connected to a fellowship programme.
- No proposal to change the 4J gate.
- No claim that this report was vetted or accepted; Section G explicitly frames itself as self-checked
  ("All DOIs have been verified against api.crossref.org"), which is a narrower claim than "vetted",
  and no independent-vetting claim is made.
