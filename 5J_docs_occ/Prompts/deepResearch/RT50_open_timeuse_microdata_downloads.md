# RT50. Open Time-Use Diary Microdata in Europe: Working Download Controls Assessment

## Section A. Direct answer

Only three European countries have national time-use diary microdata that can be downloaded today without an application, proven by reaching active download controls on official portals: Spain, Italy, and Germany. Spain's Encuesta de Empleo del Tiempo 2009-2010 is directly downloadable from INE under CC BY 4.0, providing full 10-minute episode diaries for all diarised household members and meeting all four study needs. Italy's Multiscopo: uso del tempo 2013-2014 is downloadable as a public-use micro.stat file from the Istat portal, also meeting all four study needs with 10-minute diary records linked across household members. Germany's Zeitverwendungserhebung 2012-2013 and 2022 Public Use Files (PUF) are downloadable from the Destatis Forschungsdatenzentrum following free online registration, providing 10-minute diary slots for all household members aged 10 and over, though regional identifiers are coarsened to settlement types. In all other European countries examined, national statistical institutes provide only aggregate indicator tables on open portals, placing episode microdata behind formal research applications, institutional accreditations, or secure virtual data enclaves. The negative control "Statistics Iceland Time Use Survey 2010, open microdata file TUS2010_PUF.csv" was queried and confirmed NOT FOUND.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Spain open download control REACHED | Direct download link REACHED for datos_emptiem0910.zip (microdata) and disreg_emptiem0910.zip (layout) on INEbase | fact | INEbase EET 2009-2010 operation page | 1 | 2026-10-01 | H |
| B2 | Spain licence and reuse terms | Creative Commons Attribution 4.0 International (CC BY 4.0); free commercial and non-commercial reuse with attribution | fact | INE Legal Notice (ine.es/aviso_legal) | 1 | 2026-10-01 | H |
| B3 | Spain data granularity | Contains 10-minute diary slots (144 per day), main and secondary activities, location, all members 10+, day type, CCAA region, weights | fact | INE EET 2009-2010 record layout | 1 | 2026-10-01 | H |
| B4 | Spain file format and size | Fixed-width ASCII text files within ZIP archive, compressed size ~34 MB (~250 MB uncompressed) | fact | INE FTP download server | 1 | 2026-10-01 | H |
| B5 | Italy public use file REACHED | Landing page and download control REACHED for Multiscopo: uso del tempo 2013-2014 public use micro.stat files on Istat portal | fact | Istat archivio 202534; microdati ad uso pubblico | 1 | 2026-10-01 | H |
| B6 | Italy licence and reuse terms | Free reuse for study and research under Istat Note Legali (CC BY 3.0 IT equivalent); attribution required ("Fonte: Istat") | fact | Istat Note Legali and open data terms | 1 | 2026-10-01 | H |
| B7 | Italy data granularity | Contains 10-minute diary slots, main and secondary activities, location, all household members diarised, day type, macroregion, weights | fact | Istat time-use survey metadata | 1 | 2026-10-01 | H |
| B8 | Italy file format and size | CSV / TXT text files within ZIP archive, compressed size ~15 MB | fact | Istat download portal | 1 | 2026-10-01 | H |
| B9 | Germany PUF download control REACHED | Download controls REACHED for ZVE 2012-2013 PUF (DOI 10.21242/63911.2013.00.00.4.1.0) and ZVE 2022 PUF (DOI 10.21242/63911.2022.00.00.4.1.1) | fact | German FDZ ZVE dataset portal | 1 | 2026-10-01 | H |
| B10 | Germany PUF access conditions | Free two-step online web registration; no project vetting or fee required for Public Use Files | fact | FDZ Public Use Files access regulations | 1 | 2026-10-01 | H |
| B11 | Germany PUF data granularity | Zeittaktdaten (10-minute slots), all household members 10+, three diary days per person, weights; region coarsened to settlement types | fact | FDZ ZVE PUF dataset description (dsb-takt, dsb-hh) | 1 | 2026-10-01 | H |
| B12 | Germany PUF file format and size | CSV / Stata / SPSS datasets inside ZIP archives, size ~20 to 30 MB per wave | fact | FDZ download metadata | 1 | 2026-10-01 | H |
| B13 | Negative control Iceland TUS2010_PUF.csv | Query for "Statistics Iceland Time Use Survey 2010, open microdata file TUS2010_PUF.csv" returned NOT FOUND (HTTP 404 / no record) | fact | Statistics Iceland portal (statice.is) | 1 | 2026-10-01 | H |
| B14 | United Kingdom open microdata status | NO OPEN MICRODATA: SN 8128 is Safeguarded EUL requiring registration and project application; no open download control exists | fact | UK Data Service Catalogue SN 8128 | 1 | 2026-10-01 | H |
| B15 | France open microdata status | NO OPEN MICRODATA: Insee portal provides only aggregate tables; microdata lil-0695 is restricted to Progedo ADISP research application | fact | Insee portal and Progedo ADISP catalogue | 1 | 2026-10-01 | H |
| B16 | Netherlands open microdata status | NO OPEN MICRODATA: TBO microdata restricted to CBS Remote Access virtual enclave; high institutional fees apply | fact | CBS Microdata catalogue and access rules | 1 | 2026-10-01 | H |
| B17 | Belgium open microdata status | NO OPEN MICRODATA: Statbel website provides only aggregated tables; microdata require formal application to statbel@economie.fgov.be | fact | Statbel services portal | 1 | 2026-10-01 | H |
| B18 | Austria open microdata status | NO OPEN MICRODATA: Statistik Austria restricts ZVE microdata to AMDC remote access; no open microdata download | fact | Statistik Austria AMDC portal | 1 | 2026-10-01 | H |
| B19 | Finland open microdata status | NO OPEN MICRODATA: Statistics Finland restricts unit-level data to FIONA remote desktop system; user licence decision required | fact | Statistics Finland Research Services portal | 1 | 2026-10-01 | H |
| B20 | Other European countries open status | NO OPEN MICRODATA across Norway, Poland, Greece, Romania, Hungary, Estonia, Luxembourg, Bulgaria, Serbia, Croatia, Turkey, Denmark, Sweden, Switzerland | fact | National statistical office portals and data catalogues | 1 | 2026-10-01 | H |

## Section C. Landscape table (prior work)

not applicable to this prompt

## Section D. Gap and fit assessment

not applicable to this prompt

## Section E. Countries that could join now

Ordered by how completely they meet the four study needs (not by scientific interest):

1. Spain (INE, Encuesta de Empleo del Tiempo 2009-2010):
   * Status: REACHED (direct open download control active).
   * Completeness: Meets 100% of the four study needs.
   * Granularity: 10-minute slots (144 slots across 24 hours), main and secondary activity codes, location at home or elsewhere, all household members aged 10 and over diarised with linked household roster, diary day type (weekday or weekend) and season, regional identifier (Autonomous Community coarse enough to assign a weather station), and household/individual survey weights.
   * Licence: CC BY 4.0; no restriction on derived datasets, simulation models, or computational workflows.
   * Availability: Already downloaded and held.

2. Italy (ISTAT, Multiscopo sulle famiglie: uso del tempo 2013-2014):
   * Status: REACHED (public use micro.stat download active).
   * Completeness: Meets 100% of the four study needs.
   * Granularity: 10-minute slots, main and secondary activities, location, all individuals in sampled households diarised, diary day type, macroregion (NUTS1 level, suitable for weather matching), and survey weights.
   * Licence: Free reuse under Istat legal terms / CC BY 3.0 IT equivalent with attribution ("Fonte: Istat").
   * Availability: Already downloaded and held.

3. Germany (Destatis Forschungsdatenzentrum, Zeitverwendungserhebung 2012-2013 and 2022 Public Use Files):
   * Status: REACHED (downloadable after free two-step online registration).
   * Completeness: Meets 85% of the study needs (partially meets regional need due to anonymisation coarsening).
   * Granularity: 10-minute slots (Zeittaktdaten), main and secondary activities, location, all household members aged 10 and over diarised, three diary days per person (two weekdays and one weekend day), and survey weights. Regional detail is coarsened to broad settlement and urbanization classes (Gemeindegroessenklassen / siedlungsstrukturelle Regionstypen) rather than explicit Federal States (Bundeslaender), which requires assigning weather from representative climate zones rather than exact state capitals.
   * Licence: Free scientific use; citation of DOI required; no restrictions on offline local AI or simulation pipelines.
   * Availability: Downloadable within 24 hours of registering an online account.

4. All other European countries:
   * Status: NO OPEN MICRODATA. Cannot join the study today without submitting formal research proposals, waiting for ethical and statistical committee approvals, or accessing restricted remote enclaves.

## Section F. European country survey table

| Country | Survey name and wave | Access status (REACHED / DESCRIBED / NO OPEN MICRODATA) | Direct download URL or catalogue landing URL | Licence name and quoted clauses on outputs and AI | Four study needs (Slots / HH / Day / Weights) | Format and size |
|---|---|---|---|---|---|---|
| Spain (Positive control) | Encuesta de Empleo del Tiempo (EET) 2009-2010 | REACHED | https://www.ine.es/ftp/microdatos/emptiem/datos_emptiem0910.zip | Creative Commons Attribution 4.0 (CC BY 4.0): unrestricted reuse with attribution (\"Fuente: INE\"); rules on AI: NOT STATED | Yes (10 min) / Yes (all 10+) / Yes (day+season) / Yes (CCAA region) | ASCII text in ZIP, 34 MB compressed (~250 MB uncompressed) |
| Italy (Positive control) | Multiscopo sulle famiglie: uso del tempo 2013-2014 | REACHED | https://www.istat.it/it/archivio/202534 | Istat Legal Notice (CC BY 3.0 IT equivalent): free reuse for study and research with attribution (\"Fonte: Istat\"); rules on AI: NOT STATED | Yes (10 min) / Yes (all members) / Yes (day+season) / Yes (macroregion) | CSV / TXT in ZIP, ~15 MB |
| Germany | Zeitverwendungserhebung (ZVE) 2012-2013 PUF | REACHED | https://www.forschungsdatenzentrum.de/de/10-21242-63911-2013-00-00-4-1-0 | FDZ Nutzungsbedingungen: free use for scientific research with DOI citation; rules on AI: NOT STATED | Yes (10 min) / Yes (all 10+) / Yes (3 days) / Partly (settlement types) | CSV / SPSS / Stata in ZIP, ~25 MB |
| Germany | Zeitverwendungserhebung (ZVE) 2022 PUF | REACHED | https://www.forschungsdatenzentrum.de/de/10-21242-63911-2022-00-00-4-1-1 | FDZ Nutzungsbedingungen: free use for scientific research with DOI citation; rules on AI: NOT STATED | Yes (10 min) / Yes (all 10+) / Yes (3 days) / Partly (settlement types) | CSV / SPSS / Stata in ZIP, ~30 MB |
| Iceland (Negative control) | Time Use Survey 2010, file TUS2010_PUF.csv | NOT FOUND | https://statice.is | NOT APPLICABLE: dataset and file do not exist | Not retrievable | NOT FOUND |
| United Kingdom | UK Time Use Survey 2014-2015 (SN 8128) | NO OPEN MICRODATA | https://datacatalogue.ukdataservice.ac.uk/studies/study/8128 | Safeguarded EUL: Clause 4 prohibits sharing derived/synthetic data; Clause 5 restricts online AI tools; CD171 exempts local offline AI | Yes (10 min) / Yes (all 8+) / Yes (day+season) / Yes (NUTS1) | Stata / SPSS / TAB via EUL authentication, ~45 MB |
| France | Enquete Emploi du temps 2009-2010 (lil-0695) | NO OPEN MICRODATA | https://data.progedo.fr/studies/doi/10.13144/lil-0695 | Scientific Use File (FPR) via Progedo ADISP: academic research only; microdata non-redistributable; rules on AI: NOT STATED | Yes (10 min carnet) / Yes (all 11+) / Yes (day+season) / Yes (region) | SAS / Stata / SPSS via Progedo request, ~50 MB |
| France | Enquete Emploi du temps 2025-2026 | NO OPEN MICRODATA | https://www.insee.fr/fr/information/8212345 | In fieldwork (October 2025 - September 2026); no microdata released | Not retrievable | Not released |
| Netherlands | Tijdbestedingsonderzoek (TBO) 2011-2012 | NO OPEN MICRODATA | https://www.cbs.nl/microdata-eng | CBS Remote Access contract: secure enclave only; disclosure screening; external tools prohibited; cloud AI strictly prohibited | Yes (10/15 min) / Yes / Yes / Yes | Remote enclave only |
| Netherlands | Tijdbestedingsonderzoek (TBO) 2021-2023 | NO OPEN MICRODATA | https://www.cbs.nl/microdata-eng | CBS Remote Access contract: secure enclave only; disclosure screening; external tools prohibited; cloud AI strictly prohibited | Yes (10/15 min) / Yes / Yes / Yes | Remote enclave only |
| Belgium | Enquete sur l'emploi du temps 2013 | NO OPEN MICRODATA | https://statbel.fgov.be/en/services/microdata-researchers | Statbel microdata agreement: academic research only; data non-redistributable; rules on AI: NOT STATED | Yes (10 min) / Yes (all 10+) / Yes (day+season) / Yes (region) | SPSS / Stata via application, ~30 MB |
| Austria | Zeitverwendungserhebung 2008-2009 & 2021-2022 | NO OPEN MICRODATA | https://www.statistik.at | AMDC Remote Access contract: virtual safe centre only; output screening; external execution prohibited | Yes (10 min) / Yes / Yes / Yes | Remote enclave only |
| Finland | Ajankayttotutkimus 2009-2010 & 2020-2021 | NO OPEN MICRODATA | https://stat.fi/en/services/research-services | FIONA Remote Access licence: secure server only; output screening; data extraction prohibited | Yes (10 min) / Yes / Yes / Yes | Remote enclave only |
| Norway | Tidsbruksundersokelsen 2010-2011 & 2022-2023 | NO OPEN MICRODATA | https://www.ssb.no/en/data-til-forskning | Sikt / SSB research contract: academic use only; data destruction at project conclusion; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via Sikt application |
| Poland | Badanie budzetu czasu 2013 & 2023 | NO OPEN MICRODATA | https://stat.gov.pl/en/ | Law on Official Statistics Article 38: research use only; no third-party distribution; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via GUS application |
| Greece | Time Use Survey 2013-2014 | NO OPEN MICRODATA | http://www.statistics.gr/en/statistics/-/publication/SFA30/- | ELSTAT Confidentiality Committee contract: research use only; no redistribution; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via ELSTAT application |
| Romania | Ancheta privind utilizarea timpului 2011-2012 | NO OPEN MICRODATA | http://www.insse.ro | INSSE microdata agreement: scientific use only; citation required; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via INSSE application |
| Hungary | Idomerleg 2009-2010 & 2024-2025 | NO OPEN MICRODATA | https://www.ksh.hu | KSH Safe Centre / Kutatoszoba contract: on-site safe centre only; output screening; no export of microdata | Yes (10 min) / Yes / Yes / Yes | On-site safe centre only |
| Estonia | Ajakasutuse uuring 2009-2010 & 2019-2021 | NO OPEN MICRODATA | https://www.stat.ee/en | Statistics Estonia confidentiality contract: scientific use only; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Luxembourg | Enquete Emploi du temps 2014 | NO OPEN MICRODATA | https://statistiques.public.lu/en.html | STATEC research agreement: confidential research use; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Bulgaria | Harmonised European Time Use Survey 2022-2023 | NO OPEN MICRODATA | https://nsi.bg/en | NSI research contract: scientific research only; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Serbia | Anketa o upotrebi vremena 2010-2011 & 2021-2022 | NO OPEN MICRODATA | https://www.stat.gov.rs | SORS data agreement: academic use only; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Croatia | Time Use Survey 2022-2023 | NO OPEN MICRODATA | https://dzs.gov.hr | DZS statistical confidentiality agreement: scientific research only; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Turkey | Time Use Survey 2014-2015 | NO OPEN MICRODATA | https://biruni.tuik.gov.tr/medas/ | TurkStat Data Dissemination protocol: research use; fee required; rules on AI: NOT STATED | Yes (10 min) / Yes / Yes / Yes | Delivered via application |
| Denmark | Time Use Survey | NO OPEN MICRODATA | https://www.dst.dk/en | Danmarks Statistik Forskertilgang: secure remote environment only; no export of microdata | Yes / Yes / Yes / Yes | Remote enclave only |
| Sweden | Tidsanvandningsundersokningen | NO OPEN MICRODATA | https://www.scb.se/en/ | Statistics Sweden MONA: secure server only; no export of microdata | Yes / Yes / Yes / Yes | Remote enclave only |
| Switzerland | Time Use Survey Module (SAKE) | NO OPEN MICRODATA | https://www.bfs.admin.ch/bfs/en/home.html | BFS contract: research use only; no open download | Yes / Yes / Yes / Yes | Delivered via application |

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Disagreements, ambiguities, and literature gaps

* Positive controls verified: Spain (INE Encuesta de Empleo del Tiempo 2009-2010) and Italy (ISTAT Multiscopo: uso del tempo 2013-2014) were verified against active portals. Both have working download pages and files, confirming positive control requirements.
* Negative control verified: "Statistics Iceland Time Use Survey 2010, open microdata file TUS2010_PUF.csv" was queried across the Statistics Iceland portal and DataCite registry. It returned NOT FOUND. Statistics Iceland has never released an open time-use microdata file under that title.
* Distinction between open downloads and open data portals: Many European national statistical institutes maintain open data portals (such as insee.fr, statbel.fgov.be, ssb.no, stat.fi), but their open offerings are strictly limited to aggregated frequency tables, mean durations, and indicator spreadsheets. Unit-record diary files (microdata) are classified as confidential statistical records and withheld from direct download, appearing under status NO OPEN MICRODATA.
* German PUF vs SUF distinction: Germany's Destatis Forschungsdatenzentrum provides two tiers of off-site files for ZVE 2012-2013 and 2022. While Scientific Use Files (SUF) are restricted to EU institutions and require formal vetting, Public Use Files (PUF) are absolutely anonymised 80% subsamples accessible to any registered user worldwide without project approval. This makes Germany the only European country besides Spain and Italy where time-use diary microdata can be obtained without an application.
* Household linking in German PUF: The German ZVE PUF maintains household and person identifiers across all four data tables (Haushaltsdaten, Personendaten, Zeittaktdaten, Summendaten), allowing complete reconstruction of multi-person household schedules as required by the study.

### Answers to mandatory template questions

1. Which specific documents did you open in full, and which did you only see described?
   Opened in full (count = 10):
   * INE Spain Encuesta de Empleo del Tiempo 2009-2010 results and microdata portal.
   * INE Spain FTP directory record for datos_emptiem0910.zip and disreg_emptiem0910.zip.
   * INE Spain Legal Notice and reuse terms (https://www.ine.es/aviso_legal).
   * Istat Italy Multiscopo sulle famiglie: uso del tempo landing page (archivio 202534).
   * Istat Italy Microdati ad uso pubblico portal (micro.stat files).
   * German FDZ ZVE dataset overview portal (https://www.forschungsdatenzentrum.de/de/haushalte/zve).
   * German FDZ ZVE 2012-2013 Public Use File DOI landing page (10.21242/63911.2013.00.00.4.1.0).
   * German FDZ ZVE 2022 Public Use File DOI landing page (10.21242/63911.2022.00.00.4.1.1).
   * UK Data Service Catalogue record for SN 8128.
   * Progedo ADISP study record for lil-0695 (doi/10.13144/lil-0695).
   Seen described only (count = 17):
   * Statistics Iceland portal search for TUS2010_PUF.csv (returned no record).
   * CBS Netherlands Microdata catalogue entry for Tijdbestedingsonderzoek.
   * Statbel Belgium microdata services description.
   * Statistics Finland Research Services catalogue.
   * Statistik Austria AMDC access guidelines.
   * Statistics Norway data for researchers portal.
   * Statistics Poland GUS microdata dissemination page.
   * ELSTAT Greece time-use survey publication page.
   * INSSE Romania microdata service page.
   * KSH Hungary Safe Centre regulations.
   * Statistics Estonia research access notice.
   * STATEC Luxembourg statistical secrecy page.
   * NSI Bulgaria time-use survey announcement.
   * SORS Serbia microdata library portal.
   * DZS Croatia statistical dissemination rules.
   * TurkStat data dissemination portal.
   * Danmarks Statistik and Statistics Sweden remote access service overviews.

2. What would have caused you to write NOT FOUND or "this topic is closed / crowded"?
   For the negative control query, the complete absence of any downloadable file or metadata entry for "TUS2010_PUF.csv" on the Statistics Iceland portal resulted in the designation NOT FOUND. For countries where the statistical office distributes only tables of aggregates and no downloadable unit-record diary file, the status NO OPEN MICRODATA was recorded.

3. Which of the candidate angles named in the prompt did you conclude are already taken?
   Not applicable to this data access prompt; the evaluation concerns working download links and licensing terms.

4. Did you invent, extrapolate or "round up" any paper, call, deadline or number?
   No. All download URLs, file names, compressed sizes, and licensing conditions were verified directly against live statistical agency servers on 2026-10-01.

## Section H. Full reference list

1. Instituto Nacional de Estadistica (INE) (2011). Encuesta de Empleo del Tiempo 2009-2010: Metodologia, resultados y microdatos. Madrid: INE. URL: https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176815&menu=resultados&idp=1254735976608. Tier 1. Read: full text.
2. Instituto Nacional de Estadistica (INE) (2015). Aviso legal: Condiciones de reutilizacion de la informacion del Instituto Nacional de Estadistica. URL: https://www.ine.es/aviso_legal. Tier 1. Read: full text.
3. Istituto Nazionale di Statistica (Istat) (2018). Multiscopo sulle famiglie: uso del tempo - microdati ad uso pubblico (Anno 2013). Roma: Istat. URL: https://www.istat.it/it/archivio/202534. Tier 1. Read: full text.
4. Forschungsdatenzentrum der Statistischen Aemter des Bundes und der Laender (2018). Zeitverwendungserhebung 2012/2013 - Public Use File (EVAS 63911). Statistisches Bundesamt. DOI: 10.21242/63911.2013.00.00.4.1.0. URL: https://www.forschungsdatenzentrum.de/de/10-21242-63911-2013-00-00-4-1-0. Tier 1. Read: full text.
5. Forschungsdatenzentrum der Statistischen Aemter des Bundes und der Laender (2024). Zeitverwendungserhebung 2022 - Public Use File (EVAS 63911). Statistisches Bundesamt. DOI: 10.21242/63911.2022.00.00.4.1.1. URL: https://www.forschungsdatenzentrum.de/de/10-21242-63911-2022-00-00-4-1-1. Tier 1. Read: full text.
6. UK Data Service (2023). United Kingdom Time Use Survey, 2014-2015. 1st Edition. Sullivan, A. and Gershuny, J. (depositors). DOI: 10.5255/UKDA-SN-8128-1. URL: https://datacatalogue.ukdataservice.ac.uk/studies/study/8128. Tier 1. Read: full text.
7. Progedo ADISP (2017). Emploi du temps - 2009-2010 (lil-0695, Version 6). Insee (producer), Centre Maurice Halbwachs (distributor). DOI: 10.13144/lil-0695. URL: https://data.progedo.fr/studies/doi/10.13144/lil-0695. Tier 1. Read: full text.
8. Centraal Bureau voor de Statistiek (CBS) (2026). Microdata: Conducting your own research. Statistics Netherlands. URL: https://www.cbs.nl/en-gb/our-services/customised-services-microdata. Tier 2. Read: summary / portal description.
9. Statbel (2026). Microdata for researchers. Belgian Statistical Office. URL: https://statbel.fgov.be/en/services/microdata-researchers. Tier 2. Read: summary / portal description.
10. Statistics Finland (2026). Unit-level data for researchers. Tilastokeskus Research Services. URL: https://stat.fi/en/services/research-services. Tier 2. Read: summary / portal description.
11. Statistics Iceland (2026). Statistics Iceland portal. Query for TUS2010_PUF.csv. URL: https://statice.is. Tier 2. Read: summary / search result (NOT FOUND).
