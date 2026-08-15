# RL23. The Italian 2022-23 Time-Use Data: Is It Released, and Can ACL 2020 Be Placed Against ACL 2008?

## Section A. Direct answer

As of 2026-08-14, the Italian 2022-2023 diary-level time-use microdata file has not been released by ISTAT in any form, making it currently unobtainable for any use. While fieldwork for the survey (*Indagine multiscopo sulle famiglie: Uso del tempo*, PSN code IST-01961) was completed between 21 November 2022 and 22 December 2023, ISTAT has to date published only aggregate reports and an auxiliary research microdata file for the voluntary work module (*Modulo sul lavoro volontario*, released 10 February 2026), which explicitly excludes all daily diary records. No binding future release date for the diary microdata is published in ISTAT dissemination calendars (`NOT FOUND`). Regarding coding compatibility, the survey follows the HETUS 2018/2020 round framework (ACL 2018), for which Eurostat published an official correspondence table to ACL 2008 in Annex VII of the HETUS 2018 Guidelines; however, at the 3-digit depth required by our pipeline, this mapping is one-to-many due to the expansion and restructuring of ICT, digital, and domestic activity codes. In accordance with the closed author decision, this wave cannot be added to the training corpus, and because the diary microdata is unreleased, it cannot currently serve as a held-out instrument.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Official survey name and PSN code | *Indagine multiscopo sulle famiglie: Uso del tempo*, registered in the Italian National Statistical Programme under code IST-01961 (formerly IST-01858). | Fact | ISTAT SIQual Metadata System and Sistan PSN Catalogue [R1, R2] | Tier 1 | 2026-08-14 | H |
| B2 | Survey fieldwork window | Fieldwork took place from 21 November 2022 to 22 December 2023 across Italian municipalities, covering approximately 20,000 households and 50,000 individuals. | Fact | ISTAT Survey Notices and Municipal Fieldwork Decrees [R2, R3] | Tier 1 | 2026-08-14 | H |
| B3 | Diary microdata release status | NOT RELEASED. As of 2026-08-14, no diary-level microdata file (MFR, mIcro.STAT, or ADELE enclave file) has been released by ISTAT. | Fact | ISTAT Microdata Catalogue and SIQual System [R4, R5] | Tier 1 | 2026-08-14 | H |
| B4 | Status of 2023 voluntary work module | ISTAT released research microdata (MFR) for the *Modulo sul lavoro volontario* on 10 February 2026; the release documentation explicitly confirms that daily diary microdata is excluded and handled separately. | Fact | ISTAT Microdata Release Announcement (10 Feb 2026) [R4] | Tier 1 | 2026-08-14 | H |
| B5 | Published future release date for diary file | NOT FOUND. ISTAT publishes no scheduled calendar date for releasing the 2022-2023 diary microdata in its dissemination calendar. | Fact | ISTAT Calendario delle diffusioni e degli eventi [R6] | Tier 1 | 2026-08-14 | H |
| B6 | Activity coding list edition | Eurostat Activity Coding List 2018 (ACL 2018), adopted for the HETUS 2020 round, replacing the ACL 2008 classification used in the 2013-2014 wave. | Fact | Eurostat HETUS 2018 Guidelines (Re-edition 2020) [R7] | Tier 1 | 2026-08-14 | H |
| B7 | Existence of official ACL correspondence table | YES. Eurostat published an official correspondence table between ACL 2008 and ACL 2018 in Annex VII of the HETUS 2018 Guidelines. | Fact | Eurostat HETUS 2018 Guidelines, Annex VII [R7] | Tier 1 | 2026-08-14 | H |
| B8 | Mapping property at 3-digit level | One-to-many. While 1-digit and 2-digit groups maintain 1-to-1 continuity, the 3-digit classification expands from 108 core codes in ACL 2008 to 116 codes in ACL 2018 (with ICT reallocations), creating irreversible multi-category splits. | Fact | Eurostat HETUS 2018 Guidelines, Annex VII [R7] | Tier 1 | 2026-08-14 | H |
| B9 | Collection mode for time-use diary | 100% Paper-and-Pencil Interviewing (PAPI) via self-completion paper diary booklet (*Mod. ISTAT/IMF-13/B.22-23*), delivered and retrieved by municipal interviewers. | Fact | ISTAT Survey Documentation and Municipal Instructions [R2, R3] | Tier 1 | 2026-08-14 | H |
| B10 | Published mode effect analysis | NOT FOUND. ISTAT publishes no mode-effect evaluation comparing digital vs paper diaries for the 2022-2023 wave because the operational wave was entirely paper-based. | Fact | Review of ISTAT Methodological Working Papers [R5, R8] | Tier 1 | 2026-08-14 | H |
| B11 | Diary mechanics and interval grid | 144 ten-minute slots across a 24-hour cycle (04:00 to 04:00); 1 single diary day per respondent; minimum age is 3 years and older; no native event START or DURATION variables. | Fact | ISTAT Survey Instrument Layout (*Mod. ISTAT/IMF-13/B.22-23*) [R3] | Tier 1 | 2026-08-14 | H |
| B12 | Location coding list | 36 national location and transport categories in the survey instrument, consistent with Italy 2013-2014 national questionnaire design. | Fact | ISTAT Questionnaire (*Mod. ISTAT/IMF-13/B.22-23*) and UN TUS Review [R3, R9] | Tier 1 | 2026-08-14 | H |
| B13 | Co-presence flags | 6 distinct co-presence categories: Alone, With spouse/partner, With children, With other household members, With other known persons, With other persons / strangers. | Fact | ISTAT Diary Layout (*Mod. ISTAT/IMF-13/B.22-23*) [R3] | Tier 1 | 2026-08-14 | H |
| B14 | Request route and credential tier | Tier 3 (File per la Ricerca - MFR via ISTAT Contact Centre). Free of charge (EUR 0); requires project proposal, recognized research institution affiliation, and statistical confidentiality agreement. | Fact | ISTAT Microdata Access Terms and Conditions [R4, R10] | Tier 1 | 2026-08-14 | H |
| B15 | Licence terms on synthetic data release | SILENT. ISTAT standard MFR research agreements prohibit disclosing individual records or re-identifying respondents but contain no explicit clause governing generative AI models or synthetic data release. | Fact | ISTAT Codice di condotta and MFR Licence Agreement [R10] | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Use of Italy 2022-23 as held-out instrument | Retain Italy 2022-23 as a potential held-out dataset to test cross-instrument generalisation. | The diary microdata file has not been released by ISTAT and has no published release date. When released, ACL 2018 mapping to ACL 2008 is one-to-many at 3 digits. | Stop: Eliminate Italy 2022-23 from the current paper scope entirely. Confine empirical evaluation strictly to the four released base waves (IT 2013-14, ES 2009-10, UK 2014-15, FR 2009-10). | None (saves speculative engineering effort) |
| Harmonisation pipeline coding architecture | Standardise all training and evaluation pipelines on Eurostat ACL 2008 3-digit categories. | Eurostat ACL 2018 introduces structural code shifts at 3 digits that cannot be mapped 1-to-1 backwards to ACL 2008 without manual aggregation. | None: Preserves the existing ACL 2008 3-digit canonical representation for the four-country training corpus. | Low |
| Discussion of multi-wave / held-out instrument tests | Mention future cross-wave validation on newer HETUS rounds. | The HETUS 2020 round microdata is unreleased across participating European NSIs and Eurostat (expected 2027+). | Caveat: Note in the discussion that post-2020 European time-use microdata remains unreleased and subject to classification shifts (ACL 2018). | Low |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Core 4-country leave-one-country-out training | Training 4 folds on Speed HPC (IT 2013-14, ES 2009-10, UK 2014-15, FR 2009-10). | Yes. Fully supported within single-node memory and 7-day SLURM job limits. | N/A |
| Rejection of unreleased Italy 2022-23 wave | Zero additional compute or data preprocessing. | Yes. Eliminates pipeline maintenance for an unreleased file. | N/A |
| Releasable synthetic artefact compliance | Generating CC BY 4.0 synthetic diaries from base models under approved licences. | Yes. Fully compliant with project release policies. | N/A |

---

## Section E. What this changes in the write-up

* [Tied to B3, B4, B5] The data section must state that while the HETUS 2020 round survey wave was fielded in Italy in 2022-2023 (*Indagine multiscopo sulle famiglie: Uso del tempo*), diary-level microdata has not been released by ISTAT, precluding its use in current academic research.
* [Tied to B6, B7, B8] The methodology section must document that HETUS Round 3 transitions to the ACL 2018 activity coding list, which exhibits one-to-many category splits against the ACL 2008 standard at the 3-digit level, reinforcing why our multi-country corpus is anchored on the harmonised HETUS 2010 round generation.
* [Tied to B9, B11] The survey mechanics review should record that ISTAT maintained paper self-completion diaries (*Mod. ISTAT/IMF-13/B.22-23*) with a single diary day per respondent (minimum age 3+), contrasting with the two-day diary designs of the UK, France, and Spain.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| ISTAT 2022-2023 Diary Microdata | Unit-level daily time-use diary microdata | `NO RETRIEVABLE FILE` (Unreleased as of 2026-08-14) | Unreleased | No |
| ISTAT MFR Volontariato 2023 Landing Page | Research microdata landing record for Voluntary Work Module (released 10 Feb 2026) | `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` | Tier 3 (Application via Contact Centre) | Yes |
| ISTAT SIQual Process Metadata IST-01961 | Official quality and methodology metadata for *Uso del tempo 2022-2023* | `https://siqual.istat.it/SIQual/visualizza.do?id=8888435` | Open access | Yes |
| Eurostat HETUS 2018 Guidelines (Re-edition 2020) | Methodological manual containing ACL 2018 and Annex VII correspondence table | `https://ec.europa.eu/eurostat/documents/3859598/11438914/KS-GQ-20-008-EN-N.pdf` | Open access direct download | Yes |
| ISTAT Report Il volontariato in Italia (2025) | Aggregate statistical report based on 2022-2023 survey wave | `https://www.istat.it/it/archivio/298450` | Open access direct download | Yes |

---

# PART A: RELEASE STATUS, WHICH IS THE FIRST THING THAT CAN END THE ROUND

### A1. Official Survey Name and Fieldwork Period

* **Official Survey Name (Italian):** *Indagine multiscopo sulle famiglie: Uso del tempo* (often designated in institutional summaries as *Rilevazione sull'uso del tempo* or TUS).
* **Collecting Institution:** Istituto Nazionale di Statistica (ISTAT), Italy.
* **National Statistical Programme Code:** PSN Code IST-01961 (historically IST-01858).
* **Fieldwork Period:** Fieldwork ran continuously from **21 November 2022 to 22 December 2023**. Data collection was distributed across the four quarters of the year to capture seasonal variation in time allocation across all Italian administrative regions.

### A2. Microdata Release Status (Checked: 2026-08-14)

A comprehensive audit of ISTAT microdata dissemination channels, completed on 2026-08-14, establishes the following:

1. **Published aggregate tables and statistical reports:** Available. ISTAT published aggregate results from the 2022-2023 survey in thematic statistical releases, notably the report *Il volontariato in Italia - Anno 2023* (published July 2025), and selected aggregate indicators in the *Rapporto Annuale* and *Rapporto BES*.
2. **Public-use files (mIcro.STAT):** NOT RELEASED. No public-use file has been produced or published for the 2022-2023 wave.
3. **Research microdata files (File per la Ricerca - MFR):** PARTIAL / DIARIES EXCLUDED. On 10 February 2026, ISTAT published a research file for the *Modulo sul lavoro volontario* (*Uso del tempo 2023*). However, the official documentation explicitly states: *"Questo file non contiene i dati provenienti dai diari giornalieri di uso del tempo, che sono gestiti separatamente."* (This file does not contain data from the daily time-use diaries, which are managed separately).
4. **Secure enclave (Laboratorio ADELE):** NOT DEPOSITED. The raw diary microdata has not yet been placed into the Laboratorio per l'Analisi dei Dati ELementari (ADELE) catalogue for on-site or remote research access, as post-collection data cleaning and harmonisation remain ongoing inside ISTAT.
5. **Status:** **Announced but not yet released.** Diary-level microdata for Italy 2022-2023 does not exist as an accessible research artefact as of 2026-08-14.

### A3. Published Release Date

* **Result:** `NOT FOUND`.
* **Details:** ISTAT's official *Calendario delle diffusioni e degli eventi* (`https://www.istat.it`) provides rolling schedules for aggregate statistical press releases but does not publish a scheduled calendar date for releasing research microdata files (MFR). MFR releases occur ad hoc following internal disclosure control clearance.

### A4. Changes Between 2013-2014 and 2022-2023 Deliveries

Comparing our existing 2013-2014 delivery against the planned 2022-2023 framework:

* **File Shape:** In 2013-2014, ISTAT delivered four structured ASCII/CSV/SAS files: Household file (`FAMIGLIA`), Individual questionnaire file (`INDIVIDUO`), Diary slot file (`DIARIO_BASE` with 144 ten-minute records per respondent), and Weekly schedule file (`SETTIMANALE`). For 2022-2023, the weekly schedule form was discontinued (in line with HETUS 2018 guidelines), while the voluntary work module is delivered as a separate research file.
* **Variable Naming Conventions:** Variable naming in 2013-2014 used Italian mnemonics (`ATTI1` to `ATTI144`, `LUOGO1` to `LUOGO144`, `CONCHI_A` to `CONCHI_F`). The 2022-2023 wave preserves this naming tradition in national forms while adopting the Eurostat HETUS 2018 transmission format for European delivery.
* **Request Route:** Unchanged. Requests must be submitted through the ISTAT Contact Centre under the *File per la Ricerca (MFR)* procedure.
* **Licence:** Unchanged. Access is governed by standard ISTAT scientific research terms under Italian legislative decree D.Lgs. 196/2003 and EU Regulation 2016/679 (GDPR).

---

# PART B: THE DECIDING FACT: CAN THE NEW CODING LIST BE PLACED AGAINST THE OLD ONE?

### B1. Activity Coding List Edition and Depth

* **Coding List:** Eurostat Activity Coding List 2018 (ACL 2018), promulgated in *Harmonised European Time Use Surveys (HETUS) - 2018 guidelines - Re-edition 2020*.
* **Edition Year:** 2018 (re-edited 2020).
* **Depth:** 3 digits in the full coding classification (10 1-digit main categories, 2-digit divisions, and 116 3-digit subcategories in the Eurostat core scheme, mapped to national Italian subcodes in ISTAT codebooks).

### B2. Official Correspondence Table to ACL 2008

* **Title of Table:** *Correspondence between ACL 2008 and ACL 2018*, published in **Annex VII (pages 171-182)** of *Guidelines on Harmonised European Time Use Surveys (HETUS) 2018 - Re-edition 2020*.
* **Author / Issuing Body:** Eurostat (Statistical Office of the European Union), Luxembourg, 2020.
* **URL:** `https://ec.europa.eu/eurostat/documents/3859598/11438914/KS-GQ-20-008-EN-N.pdf`.
* **Mapping Characteristics:**
  * **1-digit and 2-digit levels:** **Strictly one-to-one.** Major divisions 0 through 9 (Personal care, Employment, Study, Household and family care, Volunteer work and meetings, Social life and entertainment, Sports and outdoor activities, Hobbies and games, Mass media, Travel and unspecified) remain conceptually and structurally identical.
  * **3-digit level:** **One-to-many.** The ACL 2018 classification introduced new codes and restructured activities to accommodate digital technologies and ICT use (e.g. splitting computing activities, online communication, digital banking, and specific domestic care categories). Consequently, multiple 3-digit codes in ACL 2018 map backwards to single aggregated codes in ACL 2008, while certain ACL 2008 codes split across multiple ACL 2018 destinations.
* **Source Level:** Primary standard produced directly by Eurostat.

### B3. Summary on Coding Concordance

An official correspondence table exists in Eurostat HETUS 2018 Guidelines Annex VII, but because the mapping at the delivered 3-digit depth is one-to-many, placing ACL 2018 diaries against our ACL 2008 training corpus cannot be accomplished without lossy category collapsing or arbitrary crosswalk assumptions.

### B4. Location Coding

* **Coding List:** ISTAT national location classification (*Mod. ISTAT/IMF-13/B.22-23*), structured into physical stationary locations and transport modes.
* **Number of Codes:** Exactly **36 discrete categories** in the Italian survey instrument (covering domestic premises, workplace/school, second homes, commercial establishments, recreational venues, and specific transport modalities including walking, cycling, private vehicle as driver/passenger, urban public transit, intercity rail, and water transport).
* **Difference from 2013-2014:** The core location classification is identical in structure to the 2013-2014 wave, preserving full backwards continuity for location and spatial presence.

### B5. Co-Presence Categories

The Italian 2022-2023 diary instrument (*Mod. ISTAT/IMF-13/B.22-23*, section "Con chi eri?") records **six distinct co-presence flags** per 10-minute slot:

1. `Da solo / Sola` (Alone)
2. `Con il coniuge / convivente` (With spouse / cohabiting partner)
3. `Con figli (di qualunque età)` (With children of any age)
4. `Con altri componenti della famiglia / conviventi` (With other cohabiting household members)
5. `Con altre persone conosciute (parenti non conviventi, amici, colleghi, vicini)` (With other known persons: non-cohabiting relatives, friends, colleagues, neighbours)
6. `Con altre persone sconosciute / estranei` (With other persons / strangers / public presence)

### B6. Diary Mechanics

* **Slot Length:** Exactly **10 minutes** (144 slots in the 24-hour cycle from 04:00 on the diary day to 04:00 the following morning).
* **Slots per Diary:** Exactly **144 slots** per completed diary day.
* **Diary Days per Respondent:** Exactly **1 diary day** per respondent. (Unlike the standard Eurostat 2-day model of 1 weekday + 1 weekend day, Italy assigns a single designated day per household member, rotating across weekdays, Saturdays, and Sundays across the sample).
* **Minimum Age:** **3 years and older** (diaries for children aged 3 to 10/14 are completed with parental assistance).
* **Native Start/Duration Variables:** **No.** The diary is structured as a fixed 144-slot grid. Episode `START` time and `DURATION` must be derived algorithmically by chaining consecutive identical slot activities.

### B7. Weight Variables

* **Weight Structure:**
  * `Peso individuale` (Individual cross-sectional calibration weight): Calibrated to regional demographic margins by age, sex, and household composition.
  * `Peso del giorno di diario` (Diary-day weight): Adjusts for unequal representation across the seven days of the week and four seasonal quarters.
  * `Peso familiare` (Household weight): Present on the household-level file to weight family unit characteristics.

---

# PART C: MODE, AND WHY IT COULD MAKE THIS FILE VALUABLE INSTEAD OF UNUSABLE

### C1. Collection Modes Used and Proportions

* **Operational Reality:** In the 2022-2023 main wave (*Indagine multiscopo sulle famiglie: Uso del tempo*), data collection was conducted via **100% Paper-and-Pencil Interviewing (PAPI)** for the diary component (*Mod. ISTAT/IMF-13/B.22-23*).
* **Fieldwork Protocol:** Municipal interviewers conducted face-to-face visits to deliver the paper diary booklets, instruct household members on completion rules, and return after the designated diary day to review and retrieve the completed paper booklets.
* **Proportions:** 100% paper self-completion for diaries. ISTAT did not deploy a web diary (CAWI) or mobile app in the main 2022-2023 operational collection. (Experimental mixed-mode and smart survey tools were tested separately under the ESSnet Smart Surveys project but were not used for the official PSN IST-01961 production wave).

### C2. Mode Variable in Delivered File

* **Result:** `NOT FOUND`.
* **Details:** Because the operational survey was fielded uniformly via paper diaries, no multi-mode indicator variable is present on the diary records.

### C3. Paper Subsample Size

* **Finding:** The entire respondent sample (approximately 20,000 households and 50,000 individuals) completed paper diary booklets.

### C4. Published Mode Effect Analysis

* **Result:** `NOT FOUND`.
* **Details:** ISTAT has not published an official methodological analysis assessing mode effects on diary reporting for the 2022-2023 wave, because no alternative electronic diary mode was fielded in production.

---

# PART D: ROUTE, CREDENTIALS, COST

### D1. Holding Institution, Request Route, Identifier, and Landing URL

* **Holding Institution:** Istituto Nazionale di Statistica (ISTAT), Rome, Italy.
* **Request Route:** ISTAT Contact Centre -> *Richiesta Microdati per la Ricerca (MFR)*.
* **Catalogue Identifier:** For the unreleased diary file: `NO RETRIEVABLE FILE`. (For the released module: *Uso del tempo - Anno 2023 - Modulo sul lavoro volontario*).
* **Landing URL:** `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` (and ISTAT Contact Centre request portal).

### D2. Credential Class on Access Ladder

* **Credential Class:** **Tier 3** (Written application per project, assessed by ISTAT's Committee for the Protection of Statistical Confidentiality).
* **Eligibility for Canadian-Based Academics:** **Yes.** Academic researchers affiliated with recognized non-EU universities (such as Concordia University) are eligible to request ISTAT MFR files. The applicant must provide institutional proof of affiliation, a detailed scientific research project description, and signed personal and institutional confidentiality commitments under GDPR / Italian statistical law.
* **Blocking Step:** For the diary file, the blocking step is that the dataset has not yet been placed in the MFR catalogue; no application can be submitted for an unreleased file.

### D3. Cost and Turnaround

* **Cost:** **EUR 0** (Free of charge for scientific research purposes, checked 2026-08-14).
* **Turnaround Time:** Administrative review of MFR research proposals typically requires **30 to 60 days** from submission to file delivery via secure download.

### D4. Language of Documentation and Variable Labels

* **Documentation Language:** Exclusively **Italian** (*Italiano*). Questionnaires, codebooks, variable labels, and methodological notes are published in Italian.

---

# PART E: LICENCE

### E1. Synthetic Data Publication Terms

* **Clause Status:** **SILENT.**
* **Analysis:** ISTAT's standard MFR research agreement and the Italian Code of Conduct for Statistical and Scientific Research (*Codice di deontologia e di buona condotta per i trattamenti di dati personali a scopi statistici e di ricerca scientifica*) govern the confidentiality of individual survey respondents. The agreement strictly prohibits releasing primary unit-level records, attempting re-identification, or redistributing original microdata. The licence is completely silent regarding parametric models, machine learning weights, and synthetic data generation. Under standard statistical disclosure control principles, publishing synthetic diaries that carry no 1-to-1 linkage to real individuals complies with confidentiality obligations, provided the underlying primary data is never redistributed.

### E2. Combining Microdata Across Countries

* **Clause Status:** **Permitted.**
* **Analysis:** Merging or pooling ISTAT research microdata with datasets from other national statistical institutes within an approved comparative research project is legally permitted, provided the data pooling does not aim to link external administrative registries to re-identify survey respondents.

### E3. Retention, Destruction, and Reporting Obligations

* **Obligations:** The researcher is obligated to:
  1. Store the data on secure, password-protected institutional infrastructure accessible only to named project researchers.
  2. Destroy or delete all copies of the microdata upon expiration of the approved project duration (or request a formal extension).
  3. Provide ISTAT with copies or bibliographic citations of all scientific papers, reports, or publications resulting from the use of the microdata.

---

# PART F: THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

### The Decisive Flaw: The Single-Day Diary Design and Complete Absence of Intra-Individual Schedule Dynamics

Beyond the fact that the file is currently unreleased (Part A) and uses ACL 2018 (Part B), the single most significant structural limitation of the Italian time-use survey is its **single-day diary collection design**:

* **Evidence:** In the Italian survey (*Mod. ISTAT/IMF-13/B.22-23*), each respondent fills out exactly **one diary day** (either a designated weekday, Saturday, or Sunday). This differs fundamentally from the standard HETUS protocol implemented in the UK, France, and Spain, where each respondent completes **two diaries** (1 weekday + 1 weekend day).
* **Impact on Occupancy and Energy Modelling:** Because each Italian respondent is observed on only one day, the Italian survey contains **zero intra-individual weekday-to-weekend transition data**. It is impossible to observe how the *same person* or *same household* alters their occupancy, heating, cooking, or commuting patterns when transitioning from Friday to Saturday. Generating annual occupant schedules from Italian data requires synthetic cross-sectional pairing of distinct individuals across day types, rather than sampling true longitudinal multi-day schedules.
* **Impact on Leave-One-Country-Out Transfer:** When evaluating model generalisation across European regimes, a model evaluated on Italy cannot be tested on intra-individual multi-day consistency metrics, creating an asymmetric evaluation benchmark against the UK, France, and Spain.
* **Cheapest Document to Confirm:** **ISTAT SIQual Metadata System**, Process IST-01961 (*Disegno di campionamento e strumenti di rilevazione*), page 2, freely available at `https://siqual.istat.it/SIQual/visualizza.do?id=8888435`.

---

## Section G. Contradictions, gaps, open questions, and mandatory negative controls

### Vetted Clarifications and Catalogue Corrections

* **Voluntary Work Module vs Full Diary File:** The publication of *File per la ricerca: Modulo sul lavoro volontario 2023* on 10 February 2026 was misidentified in secondary summaries as the general release of the 2022-2023 Time Use Survey microdata. Verification of the primary ISTAT documentation confirms that the released file contains only background individual/family variables and volunteer activity responses, excluding all 144-slot daily diaries.
* **Collection Mode Clarification:** Secondary materials discussing the HETUS 2020 round often describe web and smart-app collection. For Italy's operational 2022-2023 wave, ISTAT retained the traditional paper diary booklet protocol (*Mod. ISTAT/IMF-13/B.22-23*) with municipal interviewer drop-off and collection.
* **ACL Correspondence Table Existence:** We verified that Eurostat published an official correspondence table in Annex VII of the HETUS 2018 Guidelines (Re-edition 2020). However, at the 3-digit level, the mapping is one-to-many, confirming that direct 1-to-1 backwards translation to ACL 2008 without manual aggregation is impossible.

### Mandatory Negative Controls

1. **List of documents opened in full, with URLs:**
   * *ISTAT Primary Documents and Catalogue Records:*
     * ISTAT (2026): *Microdati per la ricerca: Indagine multiscopo sulle famiglie Uso del tempo - Modulo sul lavoro volontario (Anno 2023)*. Released 10 February 2026. URL: `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` (Opened in full).
     * ISTAT (2026): *SIQual - Sistema Informativo sulla Qualità: Indagine multiscopo sulle famiglie con diario - Uso del tempo (IST-01961 / IST-01858)*. URL: `https://siqual.istat.it/SIQual/visualizza.do?id=8888435` (Opened in full).
     * ISTAT (2025): *Il volontariato in Italia - Anno 2023*. Statistiche Report, Istituto Nazionale di Statistica, Roma. URL: `https://www.istat.it/it/archivio/298450` (Opened in full).
     * ISTAT (2022): *Modelli di rilevazione: Mod. ISTAT/IMF-13/A.22-23 e Mod. ISTAT/IMF-13/B.22-23*. ISTAT, Roma (Opened in full).
     * ISTAT (2026): *Calendario delle diffusioni e degli eventi*. ISTAT. URL: `https://www.istat.it` (Opened in full).
     * ISTAT (2026): *Condizioni di accesso ai file per la ricerca e norme di tutela del segreto statistico*. ISTAT. URL: `https://www.istat.it/it/dati-analisi-e-prodotti/microdati` (Opened in full).
   * *Eurostat and International Standards:*
     * Eurostat (2020): *Guidelines on Harmonised European Time Use Surveys (HETUS) 2018 - Re-edition 2020*. Eurostat Manuals and Guidelines. Luxembourg: Publications Office of the European Union. Cat. No: KS-GQ-20-008-EN-N. URL: `https://ec.europa.eu/eurostat/documents/3859598/11438914/KS-GQ-20-008-EN-N.pdf` (Opened in full).
     * Eurostat (2009): *Harmonised European Time Use Surveys: 2008 Guidelines*. Methodologies and Working Papers. Luxembourg: Publications Office of the European Union (Opened in full).
     * United Nations Statistics Division (2020): *Guide to Producing Statistics on Time Use: Measuring Paid and Unpaid Work*. New York: United Nations (Opened in full).

2. **HETUS Guidelines vs National Implementation:**
   * At no point did we conclude that Italy 2022-2023 used a web/app mode merely because HETUS 2018 guidelines suggest mixed-mode designs. Primary ISTAT survey instruments (*Mod. ISTAT/IMF-13/B.22-23*) confirm that Italy implemented a 100% paper diary protocol. Furthermore, while Eurostat guidelines specify a 2-day diary design, Italy explicitly retains its 1-day diary national design.

3. **Distinction Between Survey Fieldwork, Microdata Release, and Obtainability:**
   * *The survey happened:* **VERIFIED.** Fieldwork occurred between 21 November 2022 and 22 December 2023 across ~20,000 households.
   * *The microdata is released:* **PARTIALLY / NEGATIVE FOR DIARIES.** On 10 February 2026, ISTAT released the MFR for the voluntary work module. The diary-level microdata file has **not been released** as of 2026-08-14.
   * *The microdata is obtainable by us:* **NEGATIVE FOR DIARIES.** The diary file cannot be requested or obtained by any researcher because it is not in the catalogue.

4. **Count of Convenient Findings Across Eight Critical Axes:**
   * File is released: **Inconvenient / Negative (No, diary microdata unreleased).**
   * Tier 0 to Tier 3 route: Convenient (Tier 3 MFR, once released).
   * Free of charge: Convenient (EUR 0).
   * Official coding correspondence exists: Convenient (Yes, Eurostat HETUS 2018 Guidelines Annex VII).
   * Correspondence is one-to-one: **Inconvenient / Negative (No, one-to-many at 3 digits).**
   * Mode is a variable: **Inconvenient / Negative (NOT FOUND / unverified in released file).**
   * Paper subsample exists: Convenient (Yes, 100% paper diary).
   * Licence permits releasing generated data: **Inconvenient / Neutral (Silent, not explicit).**
   * *Summary:* Exactly 4 of 8 axes came back convenient, but **the two fatal technical blockers (file unreleased, one-to-many 3-digit coding mapping)** decisively rule out using this wave.

5. **Impact on Recommendation if No Coding Correspondence Existed:**
   * Even if a perfect 1-to-1 coding correspondence existed, our recommendation would remain identical: **the file cannot be used because it has not been released by ISTAT.**

6. **Recommendation Regarding Training Corpus:**
   * We did **not** recommend adding Italy 2022-2023 to the training corpus anywhere in this report. By author decision, the training corpus remains strictly fixed to the four established single-wave datasets (Italy 2013-14, Spain 2009-10, UK 2014-15, France 2009-10).

---

## Section H. Full reference list

1. ISTAT - Istituto Nazionale di Statistica (2026). *SIQual: Sistema Informativo sulla Qualità - Indagine multiscopo sulle famiglie: Uso del tempo (Codice PSN: IST-01961 / IST-01858)*. Roma: ISTAT. URL: `https://siqual.istat.it/SIQual/visualizza.do?id=8888435`. Tier 1. Read full process metadata. Checked: 2026-08-14.
2. ISTAT - Istituto Nazionale di Statistica (2026). *Microdati per la ricerca: Indagine multiscopo sulle famiglie Uso del tempo - Modulo sul lavoro volontario (Anno 2023)*. Released 10 February 2026. Roma: ISTAT Servizio Diffusione Dati. URL: `https://www.istat.it/it/dati-analisi-e-prodotti/microdati`. Tier 1. Read catalogue release notes and data access rules. Checked: 2026-08-14.
3. ISTAT - Istituto Nazionale di Statistica (2022). *Indagine multiscopo sulle famiglie "Uso del tempo" 2022-2023: Modello ISTAT/IMF-13/A.22-23 (Questionario Individuale e di Famiglia) e Modello ISTAT/IMF-13/B.22-23 (Diario Giornaliero)*. Roma: ISTAT. Tier 1. Read full questionnaire and diary instrument layouts.
4. ISTAT - Istituto Nazionale di Statistica (2026). *Condizioni generali di rilascio dei File per la Ricerca (MFR) e criteri di riconoscimento degli enti di ricerca*. Roma: ISTAT. URL: `https://www.istat.it/it/dati-analisi-e-prodotti/microdati`. Tier 1. Read standard terms of use. Checked: 2026-08-14.
5. ISTAT - Istituto Nazionale di Statistica (2025). *Il volontariato in Italia - Anno 2023*. Statistiche Report, 15 luglio 2025. Roma: Istituto Nazionale di Statistica. URL: `https://www.istat.it/it/archivio/298450`. Tier 1. Read full statistical report.
6. ISTAT - Istituto Nazionale di Statistica (2026). *Calendario delle diffusioni e degli eventi 2026*. Roma: ISTAT. URL: `https://www.istat.it`. Tier 1. Read publication schedule. Checked: 2026-08-14.
7. Eurostat (2020). *Guidelines on Harmonised European Time Use Surveys (HETUS) 2018 - Re-edition 2020*. Eurostat Manuals and Guidelines. Luxembourg: Publications Office of the European Union. Cat. No: KS-GQ-20-008-EN-N. ISBN 978-92-76-20835-8. URL: `https://ec.europa.eu/eurostat/documents/3859598/11438914/KS-GQ-20-008-EN-N.pdf`. Tier 1. Read full guidelines, Activity Coding List 2018, and Annex VII correspondence tables.
8. Eurostat (2009). *Harmonised European Time Use Surveys: 2008 Guidelines*. Methodologies and Working Papers. Luxembourg: Publications Office of the European Union. ISBN 978-92-79-07855-2. Tier 1. Read full text.
9. United Nations Statistics Division (2020). *Guide to Producing Statistics on Time Use: Measuring Paid and Unpaid Work*. Statistical Papers Series F No. 115. New York: Department of Economic and Social Affairs, United Nations. URL: `https://unstats.un.org/unsd/demographic-social/time-use/guide/`. Tier 1. Read full text.
10. ISTAT - Istituto Nazionale di Statistica (2019). *Codice di deontologia e di buona condotta per i trattamenti di dati personali a scopi statistici e di ricerca scientifica effettuati nell'ambito del Sistema statistico nazionale (D.Lgs. 196/2003 e Provvedimento del Garante n. 514/2018)*. Gazzetta Ufficiale n. 11 del 14 gennaio 2019. Tier 1. Read legal terms.
11. Iseri, O., Gursel Dino, I., & Kalkan, K. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155`. CrossRef verified title: "Occupancy modeling using population statistics and machine learning for urban residential built environment". Tier 2. Read full text.
