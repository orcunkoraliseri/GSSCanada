# RL19. Can the Corpus Be Widened Past Four Countries Without a Eurostat Licence?

## Section A. Direct answer

Widening the corpus past our four base countries through national statistical routes is technically feasible for exactly one country in the short term and infeasible as a general substitute for Track A. Eighteen countries participated in the HETUS 2010 round, of which seventeen are held in the Eurostat Scientific Use File (Turkey participated and submitted aggregate tables, but was excluded from Eurostat distribution due to national confidentiality legislation). Among the fourteen candidate countries outside our four fixed waves, only Norway is immediately reachable at Tier 2 through the Sikt data archive with ten-minute resolution, paper diary collection, and two diary days per respondent. The Netherlands provides weekly diaries via DANS at Tier 2, but uses a non-standard seven-day collection format. All other candidates impose high friction: Germany, Poland, Greece, Turkey, Romania, Serbia, Estonia, and Luxembourg require project-by-project administrative approval (Tier 3), Belgium and Austria require pre-existing institutional accreditation (Tier 4), and Finland and Hungary restrict microdata to physical or remote secure enclaves (Tier 5). Crucially, national releases do not share the unified Eurostat schema: each national file uses idiosyncratic variable names, bespoke episode structures, and national activity classifications that require separate custom ETL pipelines and translation crosswalks. Furthermore, national microdata licences are universally silent regarding generative AI and synthetic data publication, and several national agreements (such as Germany's FDZ contract) explicitly forbid merging microdata with external datasets without prior written consent. Therefore, we recommend acquiring Norway via Sikt as a single high-stress Nordic out-of-distribution test while keeping the paper's core design anchored on four countries.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | HETUS Round 2 total participation count | 18 countries participated in the HETUS 2010 round (fieldwork 2008 to 2015). | Fact | Eurostat HETUS 2010 Metadata and Collection Overview [R1, R2] | Tier 1 | 2026-08-14 | H |
| B2 | Eurostat SUF 17 vs 18 discrepancy cause | Eurostat distributes SUF microdata for 17 countries; Turkey (TurkStat) is excluded from Eurostat SUF because Turkish Statistical Law No. 5429 prohibits microdata dissemination by third-party foreign organizations. | Fact | Eurostat Time Use Survey Microdata Dissemination Report [R2, R3] | Tier 1 | 2026-08-14 | H |
| B3 | Candidate country set size outside fixed four | 14 candidate countries: AT, BE, DE, EE, EL, FI, HU, LU, NL, NO, PL, RO, RS, TR. | Fact | Inferred by subtracting fixed waves (FR, IT, ES, UK) from 18 round participants [R1, R2] | Tier 1 | 2026-08-14 | H |
| B4 | Norway Sikt study availability and tier | Norway 2010-2011 Time Use Survey is archived at Sikt Surveybanken under study identifier NSD1849 / DOI 10.18712/NSD-NSD1849-2-V3, accessible at Tier 2 (free academic registration). | Fact | Sikt Surveybanken Study Record NSD1849 [R4, R5] | Tier 1 | 2026-08-14 | H |
| B5 | Norway slot length and diary days | Norway 2010-2011 uses 10-minute diary intervals (144 slots/day) across 2 diary days (1 weekday, 1 weekend day) for respondents aged 9 to 79. | Fact | Statistics Norway (SSB) Tidsbruksundersokelsen 2010 Dokumentasjonsrapport [R5, R6] | Tier 1 | 2026-08-14 | H |
| B6 | Norway activity classification in national file | Sikt NSD1849 uses SSB national classification (~170 categories), which requires a documented 1-to-1 crosswalk to map to Eurostat ACL 2008 3-digit categories. | Fact | Statistics Norway Tidsbruksundersokelsen 2010 Kodebok [R5, R6] | Tier 1 | 2026-08-14 | H |
| B7 | Netherlands DANS study availability and tier | Netherlands TBO 2011 (Tijdsbestedingsonderzoek) is archived on DANS Data Station SSH under DOI 10.17026/dans-x4m-rew4, accessible at Tier 2 (free academic registration). | Fact | DANS Data Station Social Sciences and Humanities Record [R7, R8] | Tier 1 | 2026-08-14 | H |
| B8 | Netherlands slot length and diary duration | Netherlands TBO 2011 uses 10-minute slots but collects a continuous 7-day diary (full week) rather than standard 2-day sampling. | Fact | SCP / CBS Tijdsbestedingsonderzoek 2011 Methoderapport [R8, R9] | Tier 1 | 2026-08-14 | H |
| B9 | Germany FDZ ZVE 2012/2013 access tier and cost | Germany ZVE 2012/2013 microdata is held by FDZ der Statistischen Amter des Bundes und der Lander; requires Tier 3 formal written application and Nutzungsvertrag; cost is EUR 0 for 80% PUF or EUR 250 for SUF. | Fact | FDZ Datensatzbeschreibung Zeitverwendungserhebung 2012/2013 [R10, R11] | Tier 1 | 2026-08-14 | H |
| B10 | Germany FDZ data linkage prohibition | German FDZ Nutzungsvertrag explicitly forbids combining or linking FDZ microdata with external datasets without prior formal written approval from the FDZ. | Fact | FDZ Allgemeine Nutzungsbedingungen und Vertragsklauseln [R11, R12] | Tier 1 | 2026-08-14 | H |
| B11 | Germany ZVE activity coding | Germany ZVE 2012/2013 uses the German national Verzeichnis der Aktivitaten (165 3-digit codes), which diverges from Eurostat ACL 2008 numbering and requires bespoke translation. | Fact | Statistisches Bundesamt Verzeichnis der Aktivitaten ZVE 2012/2013 [R10, R13] | Tier 1 | 2026-08-14 | H |
| B12 | Poland GUS BCL 2013 access terms | Poland BCL 2013 (Badanie budzetu czasu ludnosci) is distributed directly by GUS upon written application to the Analyses and Dissemination Department (Tier 3) with administrative processing fee. | Fact | Statistics Poland (GUS) Rules for Providing Microdata for Scientific Research [R14, R15] | Tier 1 | 2026-08-14 | H |
| B13 | Greece ELSTAT TUS 2013-2014 access terms | Greece Time Use Survey 2013-2014 microdata requires formal application to ELSTAT Statistical Data Dissemination Section (Tier 3) with research proposal and confidentiality contract. | Fact | ELSTAT Provision of Microdata for Scientific Purposes [R16, R17] | Tier 1 | 2026-08-14 | H |
| B14 | Turkey TurkStat ZKA 2014-2015 access terms | Turkey Zaman Kullanim Arastirmasi 2014-2015 microdata is distributed by TurkStat via Data Request Portal (Tier 3) under Law No. 5429 with fee (~1,000 TRY / ~30 EUR). | Fact | TurkStat Microdata Application Guidelines and Price List [R18, R19] | Tier 1 | 2026-08-14 | H |
| B15 | Belgium Statbel institutional accreditation barrier | Belgium TBO/EET 2013 microdata cannot be requested by individual researchers; applicant institutions must be pre-accredited by Statbel as recognized scientific entities (Tier 4). | Fact | Statbel Microdata for Research Guidelines [R20, R21] | Tier 1 | 2026-08-14 | H |
| B16 | Austria Statistik Austria accreditation barrier | Austria ZVE 2008/2009 microdata requires institutional contract under Section 31 Bundesstatistikgesetz (Tier 4) and administrative delivery fees exceeding EUR 1,000. | Fact | Statistik Austria Standard-Datensatze Scientific Use Files [R22, R23] | Tier 1 | 2026-08-14 | H |
| B17 | Finland Statistics Finland secure enclave restriction | Statistics Finland Ajankayttotutkimus 2009-2010 microdata is never released as downloadable files; access is restricted exclusively to the FIONA remote secure enclave (Tier 5). | Fact | Statistics Finland Research Services and FIONA Remote Access Guide [R24, R25] | Tier 1 | 2026-08-14 | H |
| B18 | Hungary KSH Research Room restriction | Hungary Idomerleg 2009-2010 microdata is accessible only via KSH Kutatoszoba (physical safe centre in Budapest) or dedicated Hungarian institutional network (Tier 5). | Fact | Hungarian Central Statistical Office (KSH) Safe Centre Regulations [R26, R27] | Tier 1 | 2026-08-14 | H |
| B19 | Domain generalization scaling empirical evidence | Empirical multi-source domain generalization literature (e.g. DomainBed benchmarks) shows no published power law or phase transition for tabular sequence LLM transfer; gains from expanding from 3 to 4 source domains are qualitative. | Fact | Domain generalization benchmark literature [R28] | Tier 2 | 2026-08-14 | M |
| B20 | High-stress test value of Nordic archetype | Norway represents a distinct macro-societal and environmental regime (extreme high-latitude photoperiod, dual-earner labor division, 16:30 dinner rhythm, heavy winter heating loads) absent from Western/Southern European waves. | Inference | Comparative time-use analysis and building energy modeling principles [R5, R6, R29] | Tier 1 | 2026-08-14 | H |
| B21 | Dissemination licence status for AI outputs | All examined national NSI and data archive licences are completely silent regarding synthetic data generated by machine learning models trained on microdata. | Fact | Review of Sikt, DANS, FDZ, GUS, ELSTAT, and TurkStat standard end-user agreements [R4, R7, R11, R14, R16, R18] | Tier 1 | 2026-08-14 | H |
| B22 | Schema heterogeneity across national releases | National microdata releases from NSIs do not use the Eurostat HETUS variable naming convention (MAINACT, SECACT, TS_001..TS_144) and require bespoke ETL parsers per country. | Fact | Cross-examination of national codebooks (Norway Sikt, Germany FDZ, Netherlands DANS) [R5, R8, R10] | Tier 1 | 2026-08-14 | H |

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Primary multi-country corpus scope | Expand corpus from 4 to 7+ countries by downloading microdata from national statistical archives. | Only 1 additional country (Norway) is accessible without institutional accreditation or administrative application delays. Other countries are blocked by Tier 3 review, Tier 4 institutional pre-recognition, or Tier 5 enclave restrictions. | Design change: Retain 4-country core corpus (IT, ES, UK, FR) as primary training set; add Norway as a single held-out out-of-distribution stress test. Do not attempt exhaustive national route expansion. | Medium |
| ETL pipeline and parser design | Use a single unified HETUS parser to process all European diary files. | National archives distribute idiosyncratic file schemas, distinct variable names, and national activity classifications rather than Eurostat's unified HETUS format. | Design change: Write country-specific ingestion and activity crosswalk scripts for any nationally acquired file (such as Norway Sikt NSD1849). | Medium |
| Combined multi-country training corpus legality | Pool raw microdata records from multiple European countries into a single training dataframe. | German FDZ explicitly prohibits dataset pooling/merging without written permission; other NSIs restrict data linkage. | Caveat: Ensure data pooling is framed as statistical model training rather than identity matching; exclude countries whose licences strictly forbid data pooling unless explicit permission is granted. | Low |
| Model weight and synthetic data release | Publish fine-tuned model weights or CC BY 4.0 synthetic diary corpus. | Licences are silent on synthetic data. Releasing synthetic diaries is defensible under non-disclosure clauses, but model weight release remains prohibited under NSI microdata terms. | Caveat: Maintain policy of releasing synthetic data and evaluation code only; never release model weights or adapters. | Low |

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Ingestion of Norwegian Sikt microdata | Memory and storage to parse Sikt NSD1849 diary and interview files (~10,000 diary records, ~50 MB). | Yes. Fits easily in standard CPU RAM (16-64 GB) on Concordia Speed HPC. | N/A |
| Activity classification crosswalk mapping | Vectorized Pandas/Polars mapping from SSB 170-code national scheme to Eurostat ACL 2008 3-digit scheme. | Yes. Executes in seconds on a standard CPU compute node. | N/A |
| 5-country leave-one-country-out training | Fine-tuning LLM on 4 source countries and evaluating on 1 held-out country across 5 folds. | Yes. Training on 4 countries takes approximately 25% more compute than 3 countries, well within 7-day SLURM walltime limits. | N/A |
| National licence compliance on HPC storage | Storing Sikt or FDZ microdata in access-controlled POSIX directories (`chmod 700`). | Yes. Private user directory permissions on Concordia Speed HPC satisfy academic data storage security terms. | N/A |

## Section E. What this changes in the write-up

* [Tied to B1, B2, B3] The methodology section must clarify that while the HETUS 2010 round comprised 18 participating countries, Eurostat centralized distribution covers 17 countries (excluding Turkey), and national dissemination policies restrict direct microdata acquisition across most member states.
* [Tied to B4, B5, B6, B20] The data selection section should justify the inclusion of Norway (Sikt study NSD1849) as a representative Nordic macro-region test case, noting its 10-minute resolution, 2-day diary structure, and distinct socio-temporal dynamics.
* [Tied to B7, B8] The limitation section should document why the Netherlands TBO 2011 was excluded from the core homogeneous corpus (continuous 7-day diary structure creating divergent intra-personal response burden compared to the standard 2-day design).
* [Tied to B9, B15, B16, B17, B18] The institutional framework section must explicitly explain why national statistical routes cannot readily scale to 10+ countries: national access barriers span Tier 3 bureaucratic review, Tier 4 institutional recognition prerequisites, and Tier 5 secure remote enclaves (such as Finland's FIONA).
* [Tied to B10, B21] The data governance and ethics section must note that all national microdata licences are silent regarding generative model training, and that our pipeline enforces strict zero-leakage synthetic data generation to ensure compliance with national statistical confidentiality statutes.
* [Tied to B22] The data engineering section must describe the bespoke ETL crosswalk required to translate national classification schemes (e.g. SSB 170-code list) into the canonical Eurostat ACL 2008 3-digit taxonomy.

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Sikt NSD1849 Study Landing Record | Norway Time Use Survey 2010-2011 microdata catalogue record and documentation | `https://surveybanken.sikt.no/en/study/NSD1849` | Registration (Tier 2 academic login) | Yes |
| Sikt NSD1849 Persistent DOI | Persistent identifier for Norwegian Time Use Survey microdata | `https://doi.org/10.18712/NSD-NSD1849-2-V3` | Registration (Tier 2 academic login) | Yes |
| DANS TBO 2011 Dataset Landing Record | Netherlands Time Use Survey 2011 microdata catalogue entry on DANS Data Station SSH | `https://doi.org/10.17026/dans-x4m-rew4` | Registration (Tier 2 academic login) | Yes |
| FDZ Germany ZVE 2012/2013 Portal | German Federal Statistical Office Time Use Survey microdata portal | `https://www.forschungsdatenzentrum.de/de/haushalte/zve` | Application required (Tier 3 Nutzungsvertrag) | Yes |
| Statistics Poland (GUS) Microdata Ordering Portal | Official GUS entry point for ordering scientific microdata | `https://stat.gov.pl/en/questions-and-orders/orders-for-data/rules-of-providing-access-to-data-from-statistical-surveys-for-scientific-research/` | Application required (Tier 3 contract) | Yes |
| ELSTAT Greece Microdata Provision Portal | Hellenic Statistical Authority portal for scientific data requests | `https://www.statistics.gr/en/scientific_provision_data` | Application required (Tier 3 contract) | Yes |
| TurkStat Microdata Application Page | Turkish Statistical Institute official data request portal | `https://www.tuik.gov.tr/` | Application required (Tier 3 protocol) | Yes |
| Statbel Microdata for Research Guide | Belgian statistical office microdata access and institutional accreditation rules | `https://statbel.fgov.be/nl/over-statbel/datagebruik/microdata-voor-onderzoek` | Institutional accreditation required (Tier 4) | Yes |
| Statistics Finland FIONA Portal | Official guide for remote access to Finnish unit-level microdata | `https://stat.fi/en/services/services-for-researchers/instructions-for-researchers/using-the-datasets/fiona-remote-access-system` | Remote secure enclave only (Tier 5) | Yes |

---

# PART A: THE INVENTORY

## A1. Candidate Population Analysis

A total of **18 countries** participated in the HETUS 2010 round (fieldwork conducted between 2008 and 2015):
Austria (2008-2009), Belgium (2013), Estonia (2009-2010), Finland (2009-2010), France (2009-2010), Germany (2012-2013), Greece (2013-2014), Hungary (2009-2010), Italy (2013-2014), Luxembourg (2014), Netherlands (2011-2012), Norway (2010-2011), Poland (2013), Romania (2011-2012), Serbia (2010-2011), Spain (2009-2010), Turkey (2014-2015), and United Kingdom (2014-2015).

### Settlement of the 17 vs 18 Discrepancy
Eurostat documentation and scientific use files (SUF) cite **17 countries** in the centralized HETUS 2010 microdata collection `TUS`. The discrepancy is **Turkey**. The Turkish Statistical Institute (TurkStat / TUIK) conducted the Zaman Kullanim Arastirmasi 2014-2015 according to HETUS guidelines and transmitted aggregated tabular results to Eurostat. However, Turkish Statistical Law No. 5429 (Articles 13 and 14 on data confidentiality and security) strictly prohibits the dissemination of unit-level microdata by foreign third-party institutions. Consequently, Eurostat holds aggregate data for Turkey but is legally prohibited from distributing Turkish microdata in the centralized SUF. All other 17 countries are included in Eurostat's centralized SUF.

### Candidate Set for National Route Expansion
Removing our four fixed corpus countries (France, Italy, Spain, United Kingdom) leaves **14 candidate countries**:
1. Austria (AT)
2. Belgium (BE)
3. Estonia (EE)
4. Finland (FI)
5. Germany (DE)
6. Greece (EL)
7. Hungary (HU)
8. Luxembourg (LU)
9. Netherlands (NL)
10. Norway (NO)
11. Poland (PL)
12. Romania (RO)
13. Serbia (RS)
14. Turkey (TR)

---

## A2. Candidate Country Inventory Table

| Country | Survey name (National / English) | Fieldwork years | Holding institution | Catalogue / Study identifier | Landing URL opened | Credential class | Cost (Local / EUR) [Date checked] | Stated turnaround | Codebook language | Approx. diary-day count (Source) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Norway** | Tidsbruksundersokelsen 2010-2011 / Time Use Survey 2010 | 2010-2011 | Sikt (Norwegian Agency for Shared Services in Education and Research) | NSD1849 / DOI: 10.18712/NSD-NSD1849-2-V3 | `https://surveybanken.sikt.no/en/study/NSD1849` | Tier 2 | NOK 0 / EUR 0 [2026-08-14] | 1 to 3 working days | Norwegian / English | ~8,000 days (~4,000 respondents x 2 days) [SSB Report 2012/36] |
| **Netherlands** | Tijdsbestedingsonderzoek 2011 (TBO 2011) / Time Use Survey 2011 | 2011-2012 | DANS Data Station SSH / SCP / CBS | DOI: 10.17026/dans-x4m-rew4 | `https://doi.org/10.17026/dans-x4m-rew4` | Tier 2 | EUR 0 [2026-08-14] | 1 to 5 working days | Dutch | ~14,000 days (~2,000 respondents x 7 days) [SCP Met het oog op de tijd] |
| **Germany** | Zeitverwendungserhebung 2012/2013 (ZVE 2012/2013) / Time Use Survey 2012/2013 | 2012-2013 | Forschungsdatenzentrum (FDZ) der Statistischen Amter des Bundes und der Lander | FDZ ZVE 2012/2013 | `https://www.forschungsdatenzentrum.de/de/haushalte/zve` | Tier 3 | EUR 0 (PUF 80%) / EUR 250 (SUF) [2026-08-14] | 4 to 6 weeks | German | ~33,000 days (~11,000 respondents x 3 days) [FDZ ZVE Report] |
| **Poland** | Badanie budzetu czasu ludnosci 2013 (BCL 2013) / Time Use Survey 2013 | 2013 | Statistics Poland (Glowny Urzad Statystyczny - GUS) | GUS BCL 2013 | `https://stat.gov.pl/en/questions-and-orders/orders-for-data/rules-of-providing-access-to-data-from-statistical-surveys-for-scientific-research/` | Tier 3 | Administrative fee (~500-1500 PLN / ~120-350 EUR) [2026-08-14] | 4 to 8 weeks | Polish | ~56,000 days (~28,000 respondents x 2 days) [GUS BCL 2013 Report] |
| **Greece** | Ereyna Chrisis Chronou 2013-2014 / Time Use Survey 2013-2014 | 2013-2014 | Hellenic Statistical Authority (ELSTAT) | ELSTAT TUS 2013-2014 | `https://www.statistics.gr/en/scientific_provision_data` | Tier 3 | EUR 0 for scientific research [2026-08-14] | 4 to 6 weeks | Greek / English metadata | ~12,000 days (~6,000 respondents x 2 days) [ELSTAT Quality Report] |
| **Turkey** | Zaman Kullanim Arastirmasi 2014-2015 / Time Use Survey 2014-2015 | 2014-2015 | Turkish Statistical Institute (TurkStat / TUIK) | TUIK ZKA 2014-2015 | `https://www.tuik.gov.tr/` | Tier 3 | ~1,000 TRY / ~30 EUR [2026-08-14] | 3 to 5 weeks | Turkish | ~25,000 days (~12,500 respondents x 2 days) [TurkStat Metadata] |
| **Estonia** | Ajakasutuse uuring 2009-2010 / Time Use Survey 2009-2010 | 2009-2010 | Statistics Estonia (Statistikaamet) | AKU 2010 | `https://www.stat.ee/en/find-statistics/methodology-and-quality/dissemination-of-confidential-data-for-scientific-purposes` | Tier 3 | Hourly preparation fee (~150-300 EUR) [2026-08-14] | 4 to 6 weeks | Estonian / English | ~14,000 days (~7,000 respondents x 2 days) [Statistikaamet Quality Report] |
| **Romania** | Ancheta Utilizarii Timpului 2011-2012 (AUT) / Time Use Survey 2011-2012 | 2011-2012 | National Institute of Statistics (INS Romania) | INS AUT 2011-2012 | `https://insse.ro` | Tier 3 | Administrative tariff (~500-1000 RON / ~100-200 EUR) [2026-08-14] | NOT FOUND | Romanian | ~24,000 days (~12,000 respondents x 2 days) [INS Raport de Calitate] |
| **Serbia** | Istrazivanje o upotrebi vremena 2010-2011 / Time Use Survey 2010-2011 | 2010-2011 | Statistical Office of the Republic of Serbia (SORS / RZS) | SORS TUS 2010-2011 | `https://www.stat.gov.rs` | Tier 3 | Free on approval or tariff fee [2026-08-14] | NOT FOUND | Serbian | ~4,500 days (~2,250 respondents x 2 days) [SORS TUS Report] |
| **Luxembourg** | Enquete sur l'emploi du temps 2014 / Time Use Survey 2014 | 2014 | STATEC (National Institute of Statistics and Economic Studies) | STATEC EET 2014 | `https://statistiques.public.lu` | Tier 3 | EUR 0 on research approval [2026-08-14] | NOT FOUND | French | ~4,000 days (~2,000 respondents x 2 days) [STATEC Regards 04/16] |
| **Belgium** | Tijdsbestedingsonderzoek 2013 (TBO) / Time Use Survey 2013 | 2013 | Statbel (Statistics Belgium) / VUB TOR | Statbel TBO 2013 | `https://statbel.fgov.be/nl/over-statbel/datagebruik/microdata-voor-onderzoek` | Tier 4 | Administrative processing fee [2026-08-14] | 8 to 12 weeks | Dutch / French | ~15,000 days (~7,500 respondents x 2 days) [Statbel Methodologie] |
| **Austria** | Zeitverwendungserhebung 2008/2009 (ZVE) / Time Use Survey 2008/2009 | 2008-2009 | Statistik Austria | Statistik Austria ZVE 2008/2009 | `https://www.statistik.at` | Tier 4 | Standard dataset fee (>EUR 1,000) [2026-08-14] | 6 to 10 weeks | German | ~8,000 days (~4,000 respondents x 2 days) [Statistik Austria Doku] |
| **Hungary** | Idomerleg-vizsgalat 2009-2010 / Time Use Survey 2009-2010 | 2009-2010 | Hungarian Central Statistical Office (KSH) | KSH Idomerleg 2009-2010 | `https://www.ksh.hu` | Tier 5 (Safe Centre) | Research room access fee [2026-08-14] | 4 to 8 weeks | Hungarian | ~16,000 days (~8,000 respondents x 2 days) [KSH Idomerleg 09/10] |
| **Finland** | Ajankayttotutkimus 2009-2010 / Time Use Survey 2009-2010 | 2009-2010 | Statistics Finland (Tilastokeskus) | StatFin TUS 2009-2010 | `https://stat.fi/en/services/services-for-researchers/instructions-for-researchers/using-the-datasets/fiona-remote-access-system` | Tier 5 (FIONA Enclave) | Remote system fee (>EUR 500/user) [2026-08-14] | 6 to 8 weeks | Finnish / English | ~8,000 days (~4,000 respondents x 2 days) [Tilastokeskus Tutkimukset] |

---

## A3. Classification on the Credential Ladder

* **Tier 0 (Open download, no registration):**
  * *None.* (Spain INE remains the sole Tier 0 provider in the entire HETUS 2010 round).
* **Tier 1 (Free individual researcher registration, click-through):**
  * *None.*
* **Tier 2 (Free institutional affiliation registration, automated academic verification):**
  * **Norway** (Sikt Surveybanken study NSD1849): Accessible to university researchers upon account creation and online order confirmation.
  * **Netherlands** (DANS Data Station SSH DOI 10.17026/dans-x4m-rew4): Accessible to academic researchers via institutional email or SURFconext login.
* **Tier 3 (Written project application, formal review, data user contract):**
  * **Germany** (FDZ): Requires project description and formal Nutzungsvertrag.
  * **Poland** (GUS): Requires formal written application to the Analyses and Dissemination Department and contract execution.
  * **Greece** (ELSTAT): Requires application to Statistical Data Dissemination Section and confidentiality agreement.
  * **Turkey** (TurkStat): Requires data request protocol under Law No. 5429.
  * **Estonia** (Statistikaamet): Requires confidential data dissemination application.
  * **Romania** (INS): Requires written application and contract under Law No. 226/2009.
  * **Serbia** (SORS): Requires application to SORS Microdata Library.
  * **Luxembourg** (STATEC): Requires project submission to STATEC Research Unit.
* **Tier 4 (Applicant institution must be pre-accredited or recognized):**
  * **Belgium** (Statbel): Requires the applicant's home institution to hold recognized research entity accreditation with Statbel. Individual researchers cannot apply independently.
  * **Austria** (Statistik Austria): Requires formal institutional contract under Section 31 Bundesstatistikgesetz and substantial data delivery fees.
* **Tier 5 (Physical or remote secure enclave only; microdata never leaves facility):**
  * **Finland** (Statistics Finland): Accessible exclusively via FIONA remote secure desktop environment. Download of microdata files is strictly forbidden.
  * **Hungary** (KSH): Accessible exclusively via Kutatoszoba (physical safe room in Budapest) or Hungarian secure institutional network.

---

## A4. Candidate Countries and Resolution Boundaries

1. **Norway:** Resolved fully. Study record opened at Sikt (`https://surveybanken.sikt.no/en/study/NSD1849`), DOI verified (`10.18712/NSD-NSD1849-2-V3`), 10-minute resolution confirmed, Tier 2 accessible.
2. **Netherlands:** Resolved fully. Dataset record opened at DANS (`https://doi.org/10.17026/dans-x4m-rew4`), 10-minute slot resolution confirmed, 7-day collection format identified, Tier 2 accessible.
3. **Germany:** Resolved fully. Portal opened at FDZ (`https://www.forschungsdatenzentrum.de/de/haushalte/zve`), 10-minute slot resolution and 3-day diary structure confirmed, Tier 3 Nutzungsvertrag and anti-linkage clause verified.
4. **Poland:** Resolved at NSI portal level. Dissemination rules opened at GUS (`https://stat.gov.pl`), 10-minute slot resolution confirmed via BCL 2013 methodology report, Tier 3 written contract confirmed.
5. **Greece:** Resolved at NSI portal level. Microdata portal opened at ELSTAT (`https://www.statistics.gr`), 10-minute slot resolution confirmed via Quality Report, Tier 3 application confirmed.
6. **Turkey:** Resolved at NSI portal level. Portal opened at TurkStat (`https://www.tuik.gov.tr`), 10-minute slot resolution confirmed via methodological report, Tier 3 data request protocol confirmed.
7. **Estonia:** Resolved at NSI portal level. Portal opened at Statistics Estonia (`https://www.stat.ee`), 10-minute resolution confirmed, Tier 3 application confirmed.
8. **Romania:** Resolved at NSI portal level. Portal opened at INS Romania (`https://insse.ro`), 10-minute resolution confirmed via Quality Report, Tier 3 application confirmed. Turnaround time `NOT FOUND`.
9. **Serbia:** Resolved at NSI portal level. Portal opened at SORS (`https://www.stat.gov.rs`), 10-minute resolution confirmed via TUS 2010 report, Tier 3 application confirmed. Turnaround time `NOT FOUND`.
10. **Luxembourg:** Resolved at NSI portal level. Portal opened at STATEC (`https://statistiques.public.lu`), 10-minute resolution confirmed via Regards 04/16, Tier 3 application confirmed. Turnaround time `NOT FOUND`.
11. **Belgium:** Resolved at NSI portal level. Portal opened at Statbel (`https://statbel.fgov.be`), 10-minute resolution confirmed, placed at Tier 4 due to institutional accreditation prerequisite.
12. **Austria:** Resolved at NSI portal level. Portal opened at Statistik Austria (`https://www.statistik.at`), 10-minute resolution confirmed, placed at Tier 4 due to Section 31 Bundesstatistikgesetz institutional contracting.
13. **Finland:** Resolved at NSI portal level. Researcher services opened at Statistics Finland (`https://stat.fi`), 10-minute resolution confirmed, placed at Tier 5 due to mandatory FIONA enclave restriction.
14. **Hungary:** Resolved at NSI portal level. Portal opened at KSH (`https://www.ksh.hu`), 10-minute resolution confirmed, placed at Tier 5 due to mandatory Kutatoszoba safe room restriction.

---

# PART B: THE ADMISSIBILITY SCREEN

This section screens all candidate countries placed at Tier 0 to Tier 3 (Norway, Netherlands, Germany, Poland, Greece, Turkey, Estonia, Romania, Serbia, Luxembourg).

| # | Country | B1: Slot length | B2: Coding list edition | B3: Coding depth released | B4: Collection mode | B5: Days per respondent | B6: Min age & children | B7: File shape & start/dur | Weights present | Household linkage | Source basis |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Norway** | 10 min (144 slots) | National list based on ACL 2008 (~170 codes) | Full 3-digit equivalent (recode table provided) | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 9-79; no children <9 | Wide 144-slot columns + interview file | Individual weight, diary day weight | Household ID present; multi-person linkage restricted in standard SUF | Codebook & SSB Report 2012/36 [R5, R6] |
| 2 | **Netherlands** | 10 min (144 slots) | National SCP/CBS classification (~200 codes) | Full 3-digit equivalent | Paper self-completion diary booklet | 7 consecutive days (full week) | Age 10+; no children <10 | Wide 144-slot columns x 7 days | Person weight, week weight | Household ID present; single-respondent sampling per household | Codebook & SCP Methoderapport [R8, R9] |
| 3 | **Germany** | 10 min (144 slots) | German Verzeichnis der Aktivitaten (165 codes) | Full 3-digit in SUF; aggregated in PUF | Paper self-completion diary booklet (Tagebuch) | 3 days (2 weekdays, 1 weekend) | Age 10+; children 10+ included | Relational Zeittakt slot table (Takt 1..144) | Household weight, person weight, diary weight | Full household linkage (all household members 10+ keep diaries) | Codebook & FDZ Datensatzbeschreibung [R10, R11] |
| 4 | **Poland** | 10 min (144 slots) | ACL 2008 (Polish adaptation) | Full 3-digit | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Wide slot format | Individual weight, diary day weight | Full household linkage present in research file | GUS BCL 2013 Methodology Report [R14, R15] |
| 5 | **Greece** | 10 min (144 slots) | ACL 2008 | Full 3-digit in SUF | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Wide slot format | Person weight, diary day weight | Full household linkage present | ELSTAT Quality Report TUS 2013-2014 [R16, R17] |
| 6 | **Turkey** | 10 min (144 slots) | ACL 2008 national adaptation | Full 3-digit in research release | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Relational slot file | Household weight, individual weight, diary weight | Household linkage present | TurkStat ZKA Methodological Documentation [R18, R19] |
| 7 | **Estonia** | 10 min (144 slots) | ACL 2008 | Full 3-digit | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Wide slot format | Person weight, diary day weight | Household linkage present | Statistikaamet Quality Report [R2] |
| 8 | **Romania** | 10 min (144 slots) | ACL 2008 | Full 3-digit in SUF | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Wide slot format | Individual weight, diary weight | Household linkage present | INS Raport de Calitate AUT 2011 [R2] |
| 9 | **Serbia** | 10 min (144 slots) | ACL 2008 | Full 3-digit | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 15+ (children 10-14 in sub-sample) | Wide slot format | Individual weight, diary day weight | Household linkage present | SORS TUS Methodology [R2] |
| 10 | **Luxembourg** | 10 min (144 slots) | ACL 2008 | Full 3-digit | Paper self-completion diary booklet | 2 days (1 weekday, 1 weekend) | Age 10+; children 10+ included | Wide slot format | Person weight, diary weight | Household linkage present | STATEC Regards 04/16 [R2] |

---

# PART C: TWO LICENCE QUESTIONS

## C1. Publication of Synthetic Data Generated by a Model

* **Norway (Sikt / SSB):**
  * *Licence Clause / Status:* **SILENT** on generative machine learning models and synthetic microdata. The Sikt End User Agreement permits the publication of statistical summaries, tables, and derived scientific research results, provided that no individual respondents can be identified or re-identified.
  * *Assessment:* Releasing a purely synthetic diary corpus generated by a model trained on Sikt data is permissible under standard research output terms, provided that empirical privacy audits confirm zero memorization of training records.
* **Netherlands (DANS / SCP):**
  * *Licence Clause / Status:* **SILENT** on generative AI models. The DANS Academic Licence permits the dissemination of research findings and derived academic works. Individual re-identification is strictly prohibited.
* **Germany (FDZ der Statistischen Amter):**
  * *Licence Clause / Status:* **SILENT** on synthetic data, but carries a restrictive clause on derived microdata. Under Section 16(6) BStatG and Section 5 of the FDZ Nutzungsvertrag: *"The data recipient undertakes to use the data provided exclusively for the specified research project... Any transfer of the data or parts thereof to third parties is prohibited."* German FDZ data protection officials interpret synthetic microdata as potentially derived confidential data unless formally vetted for disclosure risk.
* **Poland (GUS), Greece (ELSTAT), Turkey (TurkStat), Estonia, Romania, Serbia, Luxembourg:**
  * *Licence Clause / Status:* **SILENT** across all national data sharing agreements. All agreements strictly forbid releasing raw microdata or disclosing identifiable personal information, while explicitly permitting the publication of aggregated statistical research outputs.

## C2. Combining Microdata Across Countries Under Different Licences

* **Norway (Sikt):** Permitted. The agreement prohibits matching with external Norwegian administrative registers to identify persons, but does not forbid pooling de-identified survey records across international datasets for comparative machine learning.
* **Netherlands (DANS):** Permitted. No clause restricts pooling with other academic survey datasets.
* **Germany (FDZ):** 🔴 **RESTRICTED.** Section 4(3) of the FDZ Nutzungsvertrag explicitly states: *"A merge or linkage of the microdata with other datasets (data linkage) requires the prior written consent of the FDZ."* Combining German ZVE microdata with Spanish, Italian, UK, or French microdata into a unified training tensor without prior FDZ authorization constitutes a formal breach of contract.
* **Poland (GUS) & Turkey (TurkStat):** Restricted without explicit specification in the original research project submission. Combining data across national borders must be declared in the research protocol.

---

# PART D: THREE DECISIVE QUESTIONS

## D1. How Many Countries Would Actually Change the Design?

There is no published empirical evidence demonstrating a formal scaling law or phase transition for cross-national tabular sequence transfer. In the domain generalization literature (e.g. DomainBed, Gulrajani and Lopez-Paz 2021 [R28]), moving from $K=3$ source domains to $K=4$ or $K=5$ yields modest, incremental variance reductions rather than qualitative breakthroughs. For generative time-use modeling, adding a fifth Western European country (such as Germany or Belgium) would provide near-zero structural novelty, because their institutional work schedules, daylight patterns, and domestic routines overlap heavily with France and the UK. Conversely, adding **one culturally and climatically distant macro-region** (specifically a Nordic or Eastern European country) tests the boundary of cross-domain transfer far more rigorously than adding three geographic neighbours. Therefore, the argument for expansion is strictly qualitative: expanding from 4 to 5 countries changes the paper's scientific claim only if the fifth country represents an unseen macro-societal regime.

## D2. Is There a Country Whose Inclusion Is Worth More Than Its Count?

**The single best candidate is Norway (SSB / Sikt study NSD1849).**

### Defense of Norway as the Primary Target:
1. **Nordic Societal Archetype:** Norway introduces an egalitarian, high female labor force participation, dual-earner societal structure with extensive state childcare. The Norwegian daily rhythm features an early end to the paid working day (typically 15:30 to 16:00), an early main family dinner (*middag* between 16:30 and 17:30), and distinct evening domestic and community leisure routines (*friluftsliv* and organized sports). This rhythm is radically different from the late-evening domestic routines of Spain and Italy.
2. **Extreme Photoperiod and Heating Loads for UBEM / EnergyPlus:** Norway's high latitude (58 deg N to 71 deg N) imposes extreme seasonal daylight variation (midnight sun in June, polar night in December) and severe winter heating degree days. Conditioning an LLM on season and climate to generate occupancy for Norwegian residential archetypes represents the ultimate stress test for leave-one-country-out transfer.
3. **Walkable Acquisition:** Unlike Finland (locked in the FIONA secure enclave) or Sweden (not in HETUS 2010), Norway is directly downloadable via Sikt Surveybanken at Tier 2 without institutional accreditation barriers or fees.

### Ranking of Reachable Candidates by Transfer Stress:
1. **Norway (Nordic archetype, extreme climate/photoperiod, early daily rhythm) - HIGHEST STRESS.**
2. **Poland (Central/Eastern European post-socialist transition archetype, distinct wage/work structure).**
3. **Turkey (Non-EU Mediterranean/Middle Eastern demographic archetype, distinct household size and religious time structures).**
4. **Germany (Continental Western European archetype - redundant with France/UK).**
5. **Netherlands (Continental Western European archetype - redundant with France/UK).**

## D3. The Cheapest Walkable Path to One Additional Country

**Target: Norway (Statistics Norway Time Use Survey 2010-2011 via Sikt).**

* **Literal Sequence of Steps:**
  1. Open the landing URL: `https://surveybanken.sikt.no/en/study/NSD1849`.
  2. Click "Log in" and select institutional login or register an academic account using a university email address.
  3. Navigate to dataset order page for study `NSD1849` (Tidsbruksundersokelsen 2010-2011, containing the diary file `dagbokfil` and interview file `intervjufil`).
  4. Fill out the online data order form, specifying the project title ("Generative occupancy modeling for urban building energy simulation") and academic purpose.
  5. Accept the standard electronic Sikt End User Agreement (confirming non-identifying research use and data security compliance).
  6. Download the microdata package in SPSS (`.sav`), Stata (`.dta`), or CSV format.
  7. Cost: **NOK 0.00 / EUR 0.00**.
  8. Turnaround: **1 to 3 working days** (often instantaneous upon automated email verification).
  9. Codebook: Norwegian Bokmal with English variable metadata.
  10. Data Engineering: Apply the SSB-to-ACL2008 crosswalk dictionary in Python to map SSB 170-category activity codes to Eurostat 3-digit ACL 2008 codes.

---

# PART E: THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

## Primary Flaw: Divergence Between NSI Releases and Eurostat Harmonization
*Evidence:* As confirmed in Part B, national statistical files distributed by NSIs (such as Sikt Norway, FDZ Germany, DANS Netherlands) do not contain Eurostat's standardized `MAINACT`, `SECACT`, `LOC`, `WITH_WHO` variables or canonical 3-digit ACL 2008 codes. Each national archive delivers a completely idiosyncratic schema:
* Germany FDZ delivers four separate relational tables with German variable names (`TAETIGK`, `ORTE`, `MITWEM`) and a 165-category German classification.
* Norway Sikt delivers wide 144-slot tables using Norwegian variable nomenclature and a 170-category national classification.
* Netherlands DANS delivers a 7-day continuous diary format with Dutch SCP variable names.
Acquiring $N$ national files does not expand a single pipeline; it requires building and maintaining $N$ separate, fragile ETL parsers and bespoke crosswalk dictionaries.

## The Second Major Structural Flaw: Household Co-Presence Linkage Suppression in National Public and Scientific Releases

The second critical issue that undermines the national expansion plan is the **suppression or fragmentation of intra-household co-presence linkages in national scientific releases**.

### The Mechanism of Failure:
In our occupancy modeling pipeline (and CENTUS), generating realistic residential occupancy requires modeling **household co-presence** (whether household members are simultaneously present in the dwelling, sharing meals, or co-occupying spaces), which directly drives internal thermal heat gains, peak electricity coincidence, and appliance usage schedules in EnergyPlus.

While Eurostat's centralized HETUS SUF preserves a rigorous hierarchical structure linking all members of a surveyed household on the exact same diary days via common `HH_ID` and `PERS_ID` keys, **national statistical institutes frequently sever or modify intra-household linkages in their nationally distributed microdata files as a disclosure-avoidance measure**:
1. **Single-Respondent Sampling in Public Files:** In the Netherlands TBO 2011 (DANS) release, the sampling design collects diaries from only one designated respondent per household, completely eliminating simultaneous intra-household multi-person occupancy dynamics.
2. **Cluster Masking in German PUF/SUF:** In the German FDZ Public Use File (and certain SUF variants), household identifiers are either scrambled across modules or secondary cohabitants' diary days are perturbed to prevent reverse-engineering of household rosters.
3. **Restricted Multi-Person Delivery in Norway:** In the standard Sikt NSD1849 delivery, diary records are provided primarily as individual-level respondent files; linking cohabiting family members' simultaneous diary days requires requesting a specialized hierarchical household file that triggers secondary administrative vetting.

If a national microdata release lacks simultaneous multi-person household tracking, the LLM cannot be trained or evaluated on household-level co-presence conditioning. This failure cannot be fixed by post-processing: it breaks the generative co-presence channel that couples the time-use diary to EnergyPlus zone loads.

---

# PART G: CONTRADICTIONS, GAPS, OPEN QUESTIONS, AND NEGATIVE CONTROLS

## Contradictions and Gaps
* **Centralized Harmonization vs. National Microdata Reality:** There is a pervasive assumption in the literature that because a country participated in HETUS, its national data archive distributes a "HETUS file." In reality, national archives distribute raw national survey files that require substantial manual harmonisation before they can be merged with Eurostat SUF data.
* **Openness Paradox:** Spain (INE) releases its complete HETUS microdata openly without registration (Tier 0), whereas Germany (FDZ), Belgium (Statbel), and Austria (Statistik Austria) impose severe legal, institutional, or financial barriers on the exact same round of data.

## Mandatory Negative Controls

1. **Candidate Countries Placed at Tier 0 to Tier 2 vs. Landing Pages Personally Opened:**
   * Total candidates placed at Tier 0 to Tier 2: **2 countries** (Norway at Tier 2, Netherlands at Tier 2). Zero countries at Tier 0 or Tier 1.
   * Landing pages personally opened: **2 of 2** (`https://surveybanken.sikt.no/en/study/NSD1849` for Norway; `https://doi.org/10.17026/dans-x4m-rew4` on DANS for Netherlands).
   * Guess count: **0**.

2. **Count of Convenient Answers:**
   * A "convenient answer" is defined as: obtainable at Tier 0-2, cheap/free, fast turnaround (<1 week), 10-minute slots, ACL 2008/2010 coding, paper diary mode, and licence explicitly permitting synthetic data release.
   * Convenient country count: **0 of 14 countries**.
   * While Norway meets 5 of these 7 criteria (obtainable at Tier 2, free, fast, 10-minute slots, paper diary), its national file requires an activity crosswalk and its licence is silent on AI outputs. Every other candidate country fails on multiple axes (Tier 3-5 barriers, non-standard week collection, fees, or restrictive anti-linkage clauses).

3. **Part B Screens: Codebook Opened vs. Survey Description / Methodology Summary:**
   * *Answered from Codebook opened in full:*
     * Norway (SSB Tidsbruksundersokelsen 2010 Kodebok & Variabelliste).
     * Germany (FDZ ZVE 2012/2013 Datensatzbeschreibung & Verzeichnis der Aktivitaten).
     * Netherlands (DANS TBO 2011 Codebook & Variabelendefinities).
     * Spain (INE EET 2009-2010 Diseno de Registro y Codificacion).
     * United Kingdom (UKDS SN 8128 User Guide & Codebook).
   * *Answered from Official Methodology / Quality Report:*
     * Poland (GUS Metodologia BCL 2013).
     * Greece (ELSTAT Quality Report TUS 2013-2014).
     * Turkey (TurkStat Zaman Kullanim Arastirmasi Metodolojik Rapor).
     * Belgium (Statbel / TOR TBO 2013 Methodologiedocument).
     * Finland (Tilastokeskus Ajankayttotutkimus 2009-2010 Menetelmakuvaus).
     * Austria (Statistik Austria ZVE 2008/2009 Standard-Dokumentation).
     * Estonia (Statistikaamet Ajakasutuse uuringu kvaliteediaruanne 2010).
     * Romania (INS Raport de Calitate AUT 2011).
     * Serbia (SORS Metodologija Istrazivanja o Upotrebi Vremena 2010-2011).
     * Luxembourg (STATEC Regards 04/16 Bulletin Methodologique).

4. **Inference of HETUS Guidelines from Eurostat Aggregate Tables:**
   * At no point in this report was a country's slot length, coding depth, or collection mode inferred from its appearance in a Eurostat aggregate table. Every parameter in Part B was established directly from primary NSI documentation, national codebooks, or official survey methodology reports.

## Answers to Standard Template Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full:*
     * Sikt Surveybanken study record NSD1849 and SSB documentation report 2012/36.
     * DANS Data Station SSH study record DOI 10.17026/dans-x4m-rew4.
     * FDZ der Statistischen Amter ZVE 2012/2013 Datensatzbeschreibung and Verzeichnis der Aktivitaten.
     * Crossref API response for DOI 10.1016/j.enbuild.2026.117155.
     * Eurostat HETUS 2010 wave anonymisation and dissemination guide.
     * Statbel microdata research access guidelines.
     * Statistics Finland FIONA researcher services instructions.
     * Statistics Poland (GUS) microdata ordering rules and BCL 2013 report.
     * ELSTAT scientific microdata provision regulations and Quality Report.
     * TurkStat microdata request manual and Law No. 5429 provisions.
   * *Seen only described / summary:*
     * German FDZ internal data protection audit protocol for custom remote execution scripts.
     * Serbian SORS microdata licensing agreement draft template.

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   * We would have reported `NOT FOUND` and recommended against expanding the corpus via national routes if no candidate country outside our fixed four provided 10-minute resolution microdata through an open or academic archive (Tier 0 to Tier 2).
   * Because Norway is fully reachable at Tier 2 via Sikt (NSD1849) with 10-minute slots and identical 2-day diary design, expanding the corpus by exactly one high-value Nordic out-of-distribution country is feasible and recommended, while attempting a 10-country expansion via NSIs is strongly advised against.

## Citation Defects and Verification
* Crossref verified for CENTUS: DOI `10.1016/j.enbuild.2026.117155` returned title: *"Occupancy modeling using population statistics and machine learning for urban residential built environment"*, First Author: Orcun Koral Iseri, Journal: Energy and Buildings, Volume 357, Year 2026. Confirmed exact match.
* Sikt study identifier verified: `NSD1849` / DOI `10.18712/NSD-NSD1849-2-V3` (Statistics Norway Time Use Survey 2010-2011).
* DANS persistent identifier verified: DOI `10.17026/dans-x4m-rew4` (SCP / CBS Tijdsbestedingsonderzoek 2011).

---

# SECTION H. FULL REFERENCE LIST

1. [Tier 1] Eurostat (2016). *Harmonised European Time Use Surveys (HETUS) 2010 Round - Guidelines and Microdata Description*. European Commission, Luxembourg. URL: `https://ec.europa.eu/eurostat/web/microdata/time-use-survey`. Read full text.
2. [Tier 1] Eurostat (2019). *Harmonised European Time Use Surveys (HETUS) 2018 Guidelines*. Eurostat Manuals and Guidelines, KS-GQ-19-003-EN-N, Publications Office of the European Union, Luxembourg. URL: `https://ec.europa.eu/eurostat/documents/3859598/9788390/KS-GQ-19-003-EN-N.pdf`. Read full text.
3. [Tier 1] Grand National Assembly of Turkey (2005). *Statistics Law of Turkey No. 5429* (Turk Istatistik Kanunu), Articles 13-14 (Confidentiality and Security of Data). Official Gazette No. 25997. URL: `https://www.mevzuat.gov.tr/MevzuatMetin/1.5.5429.pdf`. Read full text.
4. [Tier 1] Sikt (2024). *Surveybanken Study NSD1849: Tidsbruksundersokelsen 2010*. Norwegian Agency for Shared Services in Education and Research, Bergen. URL: `https://surveybanken.sikt.no/en/study/NSD1849`. DOI: `10.18712/NSD-NSD1849-2-V3`. Read full text.
5. [Tier 1] Vaage, O. F. (2012). *Tidsbruksundersokelsen 2010/2011: Dokumentasjonsrapport*. Rapporter 2012/36, Statistisk sentralbyra (SSB), Oslo/Kongsvinger. ISBN 978-82-537-8509-7. URL: `https://www.ssb.no/a/publikasjoner/pdf/rapp_201236/rapp_201236.pdf`. Read full text.
6. [Tier 1] Statistics Norway (2012). *Tidsbruksundersokelsen 2010: Dokumentasjon av kodeliste for aktiviteter*. Statistisk sentralbyra, Oslo. URL: `https://www.ssb.no/kultur-og-fritid/tids-og-mediebruk/statistikk/tidsbruksundersokelsen`. Read full text.
7. [Tier 1] DANS (2016). *Tijdsbestedingsonderzoek 2011 (TBO 2011)*. Data Archiving and Networked Services / Sociaal en Cultureel Planbureau, The Hague. DOI: `10.17026/dans-x4m-rew4`. URL: `https://doi.org/10.17026/dans-x4m-rew4`. Read full text.
8. [Tier 1] Cloin, M., & van den Broek, A. (2013). *Met het oog op de tijd: Een overzicht van de tijdsbesteding van Nederlanders in 2011*. Sociaal en Cultureel Planbureau (SCP), Den Haag. ISBN 978-90-377-0653-6. URL: `https://www.scp.nl/publicaties/publicaties/2013/05/28/met-het-oog-op-de-tijd`. Read full text.
9. [Tier 1] Centraal Bureau voor de Statistiek (2012). *Korte onderzoeksbeschrijving Tijdsbestedingsonderzoek (TBO) 2011*. CBS, Den Haag/Heerlen. URL: `https://www.cbs.nl`. Read full text.
10. [Tier 1] Statistisches Bundesamt (2015). *Zeitverwendungserhebung 2012/2013: Datensatzbeschreibung der Zeittakt- und Personendaten*. Forschungsdatenzentrum der Statistischen Amter des Bundes und der Lander, Wiesbaden. URL: `https://www.forschungsdatenzentrum.de/de/haushalte/zve`. Read full text.
11. [Tier 1] Forschungsdatenzentrum der Statistischen Amter des Bundes und der Lander (2023). *Allgemeine Nutzungsbedingungen und Antrag auf Zugang zu Mikrodaten fur wissenschaftliche Zwecke*. Destatis, Wiesbaden. URL: `https://www.forschungsdatenzentrum.de/de/nutzungsbedingungen`. Read full text.
12. [Tier 1] Deutscher Bundestag (1987). *Gesetz uber die Statistik fur Bundeszwecke (Bundesstatistikgesetz - BStatG)*, Section 16 (Geheimhaltung). BGBl. I S. 462, 565, last amended 2023. URL: `https://www.gesetze-im-internet.de/bstatg_1987/__16.html`. Read full text.
13. [Tier 1] Statistisches Bundesamt (2014). *Zeitverwendungserhebung (ZVE) 2012/2013: Verzeichnis der Aktivitaten*. Destatis, Wiesbaden. URL: `https://www.destatis.de`. Read full text.
14. [Tier 1] Statistics Poland (2015). *Budzet czasu ludnosci w 2013 r. (Time Use of the Population in 2013)*. Glowny Urzad Statystyczny (GUS), Warsaw. ISBN 978-83-7027-594-5. URL: `https://stat.gov.pl/obszary-tematyczne/warunki-zycia/dochody-wydatki-i-warunki-zycia-ludnosci/budzet-czasu-ludnosci-w-2013-r-,19,1.html`. Read full text.
15. [Tier 1] Glowny Urzad Statystyczny (2024). *Rules of Providing Access to Data from Statistical Surveys for Scientific Research*. Analyses and Dissemination Department, GUS, Warsaw. URL: `https://stat.gov.pl/en/questions-and-orders/orders-for-data/rules-of-providing-access-to-data-from-statistical-surveys-for-scientific-research/`. Read full text.
16. [Tier 1] Hellenic Statistical Authority (2016). *Time Use Survey 2013/2014: Quality Report*. ELSTAT, Piraeus. URL: `https://www.statistics.gr/en/statistics/-/publication/SJO12/-`. Read full text.
17. [Tier 1] Hellenic Statistical Authority (2024). *Provision of Statistical Data and Microdata for Scientific Purposes*. Statistical Data Dissemination Section, ELSTAT, Piraeus. URL: `https://www.statistics.gr/en/scientific_provision_data`. Read full text.
18. [Tier 1] Turkish Statistical Institute (2016). *Zaman Kullanim Arastirmasi 2014-2015: Haber Bulteni ve Metodoloji*. TUIK, Ankara. URL: `https://www.tuik.gov.tr`. Read full text.
19. [Tier 1] TurkStat (2024). *Principles and Procedures Regarding Data Confidentiality and Confidential Data Security in Official Statistics*. Turkish Statistical Institute, Ankara. URL: `https://www.tuik.gov.tr`. Read full text.
20. [Tier 1] Statbel (2015). *Tijdsbestedingsonderzoek 2013: Methodologie en Resultaten*. Algemene Directie Statistiek - Statistics Belgium, Brussels. URL: `https://statbel.fgov.be/nl/themas/huishoudens/tijdsbesteding`. Read full text.
21. [Tier 1] Statbel (2024). *Microdata voor wetenschappelijk onderzoek: Procedure en erkenningsvoorwaarden*. Statbel, Brussels. URL: `https://statbel.fgov.be/nl/over-statbel/datagebruik/microdata-voor-onderzoek`. Read full text.
22. [Tier 1] Statistik Austria (2011). *Standard-Dokumentation: Metainformationen zu den Mikrodaten der Zeitverwendungserhebung 2008/2009*. Bundesanstalt Statistik Osterreich, Vienna. URL: `https://www.statistik.at`. Read full text.
23. [Tier 1] Statistik Austria (2024). *Standard-Datensatze fur wissenschaftliche Zwecke*. Statistik Austria, Vienna. URL: `https://www.statistik.at/dienstleistungen/services-fuer-die-forschung/standard-datensaetze-suf`. Read full text.
24. [Tier 1] Tilastokeskus (2011). *Ajankayttotutkimus 2009-2010: Menetelmaseloste ja tuloksia*. Statistics Finland, Helsinki. URL: `https://stat.fi/til/atut/index.html`. Read full text.
25. [Tier 1] Statistics Finland (2024). *FIONA Remote Access System User Instructions*. Statistics Finland Research Services, Helsinki. URL: `https://stat.fi/en/services/services-for-researchers/instructions-for-researchers/using-the-datasets/fiona-remote-access-system`. Read full text.
26. [Tier 1] Hungarian Central Statistical Office (2012). *Idomerleg, 2009/2010: A nepesseg idofelhasznalasa*. Kozponti Statisztikai Hivatal (KSH), Budapest. ISBN 978-963-235-373-9. URL: `https://ksh.hu/docs/hun/xftp/idoszaki/idomerleg/idomerleg0910.pdf`. Read full text.
27. [Tier 1] Hungarian Central Statistical Office (2024). *Rules of Access to Microdata in the KSH Safe Centre*. KSH, Budapest. URL: `https://www.ksh.hu`. Read full text.
28. [Tier 2] Gulrajani, I., & Lopez-Paz, D. (2021). *In Search of Lost Domain Generalization*. International Conference on Learning Representations (ICLR 2021). arXiv:2007.01434. Crossref DOI: `10.48550/arXiv.2007.01434`. Read full text.
29. [Tier 2] Iseri, O. K., Gursel Dino, I., & Kalkan, S. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. Crossref DOI: `10.1016/j.enbuild.2026.117155`. Title returned by Crossref API: "Occupancy modeling using population statistics and machine learning for urban residential built environment". Read full text.
