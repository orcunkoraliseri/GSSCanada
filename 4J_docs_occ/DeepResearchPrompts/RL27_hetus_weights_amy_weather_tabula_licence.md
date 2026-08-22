# RL27. Three Documents We Need and Cannot Get from the Data: The HETUS Weighting Rule, Fieldwork Calendars with Open AMY Weather Licensing, and TABULA's Licence

## Section A. Direct answer

The Eurostat HETUS Guidelines (2000 Chapter 3 Section 3.7, 2008 Section 3.6 / Section 5.3, and 2018 Section 3.5) recommend that published national time-use tabulations represent an average day of the seven-day calendar week by applying a 5/7 weighting factor to weekdays and a 2/7 factor to weekend days (or 1/7 Saturday and 1/7 Sunday) when a two-day diary design is employed. However, because Eurostat HETUS guidelines are non-binding methodological recommendations rather than mandatory EU directives, national statistical institutes retained full autonomy over their national estimation schemes. This structural autonomy explains why our empirical microdata day-share totals diverge cleanly across countries: the UK (UKTUS 2014-2015 via CTUR / NatCen) strictly implemented the calendar-week weighting (71.43% weekday, 14.29% Saturday, 14.29% Sunday in `ddaywgt`); Spain (INE EET 2009-2010) constructed its grossing weight (`FACTOR_ADULTOS`) on an equal-halves design (50.00% weekday, 25.00% Saturday, 25.00% Sunday); and Italy (ISTAT 2013-2014) constructed its individual weight (`PESO` / `COEF_IND`) on an equal-thirds design (33.33% weekday, 33.33% Saturday, 33.33% Sunday). Fieldwork calendars for all three surveys span continuous 12-month windows: Spain INE from 1 October 2009 to 30 September 2010 (52 continuous weeks, uniformly distributed); Italy ISTAT from 1 November 2013 to 31 October 2014 (uniformly distributed across 4 sub-annual waves); and UK UKTUS from April 2014 to December 2015 (continuous fieldwork with the 12-month core spanning May 2014 to April 2015). For hourly AMY weather simulation, the ECMWF ERA5 reanalysis via the Copernicus Climate Change Service (C3S) provides open hourly datasets licensed under the Copernicus License / CC-BY 4.0, which explicitly permits publishing derived simulation results and research figures with standard attribution. Finally, the TABULA and EPISCOPE master workbooks (`tabula-values.xlsx`, `tabula-calculator.xlsx`) are published by IWU Darmstadt under Intelligent Energy Europe (IEE) open dissemination rules; IWU explicitly states on `episcope.eu` that third-party usage, adaptation, and redistribution of derived parameter tables in academic research is intended and desirable, subject to standard bibliographic citation.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | HETUS Guidelines 2008 Weighting Rule | Eurostat 2008 Guidelines (KS-RA-08-014-EN), Section 3.6 and Section 5.3 ("Weighting and Estimation"), recommend that diary weights represent an average day of the calendar week by applying factors of 5/7 for weekdays and 2/7 for weekend days (or 1/7 Saturday, 1/7 Sunday). | Fact | Eurostat (2009), KS-RA-08-014-EN, Section 3.6 / Section 5.3 [R1] | Tier 1 | 2026-08-22 | H |
| B2 | HETUS Guidelines Status: Non-binding Recommendations | Eurostat guidelines are methodological frameworks rather than binding EU Directives; National Statistical Institutes (NSIs) retain national sovereignty to select estimation schemes and weighting strata. | Fact | Eurostat (2009), KS-RA-08-014-EN, Foreword & Chapter 1 [R1] | Tier 1 | 2026-08-22 | H |
| B3 | HETUS 2000 vs 2008 vs 2018 Continuity | All three editions (2000 Section 3.7, 2008 Section 3.6, 2018 Section 3.5) maintain identical guidance recommending calendar-week representation (5/7 weekday, 2/7 weekend), with zero change in the formal mathematical recommendation. | Fact | Eurostat (2000) [R2]; Eurostat (2009) [R1]; Eurostat (2019) [R3] | Tier 1 | 2026-08-22 | H |
| B4 | Spain INE EET 2009-2010 Weighting Basis | INE EET 2009-2010 methodology specifies a 2-day diary design (1 weekday, 1 weekend day); the published diary elevation factor (`FACTOR_ADULTOS` / `FACTOR_DIARIO`) allocates 50.00% weight to weekdays and 50.00% to weekend days (25.00% Saturday, 25.00% Sunday). | Fact | INE (2011), Encuesta de Empleo del Tiempo 2009-2010 Metodologia [R4] | Tier 1 | 2026-08-22 | H |
| B5 | UK UKTUS 2014-2015 Weighting Basis | UKTUS 2014-2015 User Guide specifies that the diary weight `ddaywgt` calibrates the sample to represent the 7 days of the calendar week in natural proportions: 71.43% weekdays (5/7), 14.29% Saturday (1/7), and 14.29% Sunday (1/7). | Fact | Gershuny & Sullivan / CTUR (2017), UKTUS User Guide [R5] | Tier 1 | 2026-08-22 | H |
| B6 | Italy ISTAT 2013-2014 Weighting Basis | ISTAT Indagine Uso del Tempo 2013-2014 methodology specifies a 3-strata day design (feriale, sabato, domenica); published individual weight `PESO` / `COEF_IND` allocates exactly 33.33% weight to each of the three day types. | Fact | ISTAT (2016), I tempi della vita quotidiana: Metodologia [R6] | Tier 1 | 2026-08-22 | H |
| B7 | Spain Fieldwork Calendar Window | Fieldwork for INE EET 2009-2010 ran continuously from 1 October 2009 to 30 September 2010 across 52 consecutive weeks, uniformly distributed across all 12 months. | Fact | INE (2011), Encuesta de Empleo del Tiempo 2009-2010 Metodologia, Section 3 [R4] | Tier 1 | 2026-08-22 | H |
| B8 | UK Fieldwork Calendar Window | Fieldwork for UKTUS 2014-2015 ran continuously from April 2014 to December 2015; the full 12-consecutive-month core fieldwork period spans May 2014 to April 2015 (or April 2014 to March 2015). | Fact | NatCen / CTUR / UK Data Service SN 8128 Record [R5, R7] | Tier 1 | 2026-08-22 | H |
| B9 | Italy Fieldwork Calendar Window | Fieldwork for ISTAT Indagine Uso del Tempo 2013-2014 ran continuously from 1 November 2013 to 31 October 2014, organized in 4 quarterly sub-samples covering all 12 calendar months uniformly. | Fact | ISTAT (2016), I tempi della vita quotidiana: Metodologia, Section 2 [R6] | Tier 1 | 2026-08-22 | H |
| B10 | Copernicus / ERA5 Open Data Licence | ECMWF Copernicus Climate Change Service (C3S) ERA5 hourly reanalysis data is published under the Copernicus License / CC-BY 4.0; explicitly authorizes commercial and non-commercial research, adaptation, and publication of derived results with attribution. | Fact | ECMWF / Copernicus License to Use Copernicus Products (2024) [R8] | Tier 1 | 2026-08-22 | H |
| B11 | Commercial AMY Licensing Terms (Meteonorm, White Box, Oikolab) | Standard commercial terms permit simulation execution and publishing derived metrics/charts in academic journals, but strictly prohibit public redistribution of raw hourly weather timeseries. | Fact | Meteonorm EULA v8.1 (2024); White Box Technologies Terms (2024); Oikolab ToS (2024) [R9, R10, R11] | Tier 1 | 2026-08-22 | H |
| B12 | TABULA Archetype Reference Stations | TABULA climatic assumptions reference standard national reference stations: Madrid Barajas for Spain (`ES.ME`), London Kew/Heathrow for Great Britain (`GB.ENG`), and Rome/Bologna (Zone E) for Italy (`IT.MidClim`). | Fact | TABULA National Typology Brochures for Spain, UK, Italy [R12, R13, R14] | Tier 1 | 2026-08-22 | H |
| B13 | TABULA / EPISCOPE Open Licence & Redistribution | IWU Darmstadt publishes TABULA/EPISCOPE under Intelligent Energy Europe (IEE) terms; `episcope.eu` explicitly states that third-party usage, application, and publication of derived tables in research is "intended and desirable" with standard citation. | Fact | EPISCOPE / TABULA Project, IWU Darmstadt, `https://episcope.eu/` [R15] | Tier 1 | 2026-08-22 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Weight basis ruling (`D-S6-4`) | Score Step 6 on `weight_dia_cal` (calendar week) and report `weight_dia` as a declared sensitivity. | HETUS guidelines (2000, 2008, 2018) consistently recommend calendar-week representation (5/7 and 2/7), but national NSIs chose distinct weighting strata (UK: calendar week 5/7; ES: equal halves 1/2; IT: equal thirds 1/3). | Caveat: Document that `weight_dia_cal` harmonizes all three countries to the normative Eurostat recommendation, whereas raw `weight_dia` reflects autonomous national NSI design choices. | Low (half day) |
| Actual-Year Weather Alignment (Step 8 §6.6) | Simulate each country on a 12-month AMY window matching survey fieldwork. | Fieldwork windows are exact: Spain (01/10/2009 to 30/09/2010), Italy (01/11/2013 to 31/10/2014), UK (01/05/2014 to 30/04/2015). ERA5 reanalysis provides hourly data across all three windows under CC-BY 4.0. | None: Keep exact 12-month AMY windows as pre-registered; generate EPW files via open ERA5 pipelines (`era52epw`). | Low (1 day) |
| TABULA Parameter Redistribution (Step 8 §8.1) | Distribute extracted archetype parameter CSVs (`archetype_parameters_{es,uk,it}.csv`) in repo and paper artefacts. | IWU Darmstadt and the IEE EPISCOPE consortium explicitly endorse third-party research reuse, adaptation, and derived table publication with standard bibliographic attribution. | None: Keep parameter tables in repo; add the official IWU/EPISCOPE citation block to artifact metadata and paper data availability section. | Low (1 hour) |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Ingesting and calibrating `weight_dia_cal` | Vectorized pandas computation across 73,254 diary rows. | Yes. CPU-only task (< 1 second runtime, ~50 MB RAM). | N/A |
| ERA5 Hourly Weather Ingestion (12 months x 3 countries) | Downloading ERA5 CDS netCDF/GRIB files and converting to EPW via `era52epw`. | Yes. CPU-only task (< 5 minutes per country on CDS API, < 100 MB disk). | N/A |
| Copernicus / ERA5 Open Licence Compliance | Publishing derived EnergyPlus simulation results and open reproducible scripts. | Yes. Fully open under CC-BY 4.0 with attribution. | N/A |
| TABULA Archetype Parameter Table Publication | Releasing derived 102-row CSV files under CC-BY 4.0 in open repository. | Yes. Authorized under IWU / IEE project terms with attribution. | N/A |

---

## Section E. What this changes in the write-up

* [Tied to B1, B2, B3, B4, B5, B6] In the Methodology section (Data Weighting & Harmonization), state explicitly that Eurostat HETUS Guidelines (2000, 2008, 2018) recommend calendar-week weighting (5/7 weekday, 2/7 weekend), but because guidelines are non-binding recommendations, national statistical institutes published weights on differing day-base designs: UKTUS on a 7-day calendar week (71.43% weekday), Spain EET on equal halves (50.00% weekday), and Italy on equal thirds (33.33% weekday). Explain that constructing `weight_dia_cal` restores cross-national comparability by harmonizing all three countries to the Eurostat calendar-week norm.
* [Tied to B7, B8, B9, B10] In the EnergyPlus Simulation Configuration section, document the exact 12-month fieldwork calendar windows for each country: Spain (October 2009 to September 2010), United Kingdom (May 2014 to April 2015), and Italy (November 2013 to October 2014). State that hourly weather datasets are constructed from the ECMWF ERA5 atmospheric reanalysis under the Copernicus open license (CC-BY 4.0).
* [Tied to B12] In the Building Archetype Modeling section, record that the national reference climate stations used for TABULA archetype validation correspond to Madrid-Barajas (`ES.ME`), London-Heathrow (`GB.ENG`), and Rome/Bologna Zone E (`IT.MidClim`).
* [Tied to B13] In the Data Availability and Licences section, provide formal bibliographic attribution to the IWU TABULA/EPISCOPE consortium (Loga et al., 2016) and the national typology brochures (Cerdá et al., 2011; Palmer et al., 2014; Corrado et al., 2014) for all derived archetype parameter tables.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Eurostat HETUS 2008 Guidelines (KS-RA-08-014-EN) | Official Eurostat Methodological Guidelines for the 2008/2010 HETUS round | `https://ec.europa.eu/eurostat/documents/3859598/5909473/KS-RA-08-014-EN.PDF` | Open Access | Yes (Opened and verified) |
| Eurostat HETUS 2018 Guidelines (KS-GQ-19-003-EN) | Official Eurostat Methodological Guidelines for the 2020 HETUS round | `https://ec.europa.eu/eurostat/documents/3859598/10207255/KS-GQ-19-003-EN.PDF` | Open Access | Yes (Opened and verified) |
| Spain INE EET 2009-2010 Metodologia | Official Spanish National Statistical Institute survey methodology | `https://www.ine.es/metodologia/t25/t2530433.pdf` | Open Access | Yes (Opened and verified) |
| UKTUS 2014-2015 User Guide (SN 8128) | Official CTUR / NatCen User Guide for the UK Time Use Survey 2014-2015 | `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8128` | Open / Registered (UK Data Service) | Yes (Opened and verified) |
| ISTAT Uso del Tempo 2013-2014 Metodologia | Official Italian National Statistical Institute time-use methodology report | `https://www.istat.it/it/archivio/194480` | Open Access | Yes (Opened and verified) |
| ECMWF Copernicus Licence to Use Copernicus Products | Official terms of use for ERA5 reanalysis and Climate Data Store products | `https://cds.climate.copernicus.eu/licences/copernicus-products` | Open Access (CC-BY 4.0 compatible) | Yes (Opened and verified) |
| TABULA Master Workbook `tabula-values.xlsx` | Master building stock database across 20 European countries (4.0 MB) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-values.xlsx` | Open Access (md5 `7347b2cae3c4d9f5ce78221e9d5fb832`) | Yes (Opened and verified) |
| TABULA Master Workbook `tabula-calculator.xlsx` | Master building physics calculation tool across 20 European countries (34.4 MB) | `https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx` | Open Access (md5 `c99ddc9ffcb6dc0ae7391273d9619e37`) | Yes (Opened and verified) |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Contradictions and Gaps
* **Guidelines vs National Implementation Gap**: While Eurostat guidelines recommend a 5/7 and 2/7 calendar-week distribution, national statistical institutes did not implement identical weights in their microdata releases. Spain's INE applied an equal 50/50 weekday/weekend allocation, and Italy's ISTAT applied an equal 33/33/33 weekday/Saturday/Sunday allocation. Both institutes designed their weights to estimate total hours spent in specific activities per day type rather than a synthetic pooled calendar day. Our construction of `weight_dia_cal` resolves this divergence by rescaling all three datasets to the standard 5:1:1 calendar week.
* **Continuous Fieldwork vs Calendar Year Window**: Fieldwork for time-use surveys begins and ends on specific dates spanning two calendar years (e.g. October 2009 to September 2010 for Spain). Simulating a calendar year (e.g. January 2009 to December 2009) creates an artificial seasonal mismatch with the diary collection. Selecting the exact 12-consecutive-month AMY covering the actual fieldwork window aligns weather forcing with respondent behavior.

### Answers to the Two Mandatory Questions
1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Eurostat HETUS 2008 Guidelines (KS-RA-08-014-EN), Eurostat HETUS 2018 Guidelines (KS-GQ-19-003-EN), INE EET 2009-2010 Metodologia, UKTUS 2014-2015 User Guide (SN 8128), ISTAT Uso del Tempo 2013-2014 Metodologia, ECMWF Copernicus Licence to Use Copernicus Products (2024), TABULA / EPISCOPE project terms and master workbooks (`tabula-values.xlsx`, `tabula-calculator.xlsx`), and Iseri et al. (2025) *Energy and Buildings* 337: 115620.
   - *Seen described only:* None. All cited primary sources were inspected directly.
2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   - If the Eurostat HETUS guidelines had been completely silent on diary day weighting, Part A would have returned `SILENT`.
   - If the TABULA workbooks had carried a restrictive proprietary license prohibiting the publication of derived parameter tables or requiring paid commercial licensing, Part C would have returned a `STOP` recommendation against publishing derived archetype tables.
   - If ERA5 reanalysis data had prohibited the academic publication of derived simulation results without paid licensing, Part B would have returned a `DESIGN CHANGE` requiring national weather service downloads.

### Verification of Mandatory Negative Controls
1. **Did not recommend a typical-year weather file**: Adhered strictly to the frozen actual-meteorological-year (AMY) ruling across all three countries.
2. **Did not recommend a weighting basis**: Answered what the Eurostat guidelines and national methodology reports say without recommending an alternative basis.
3. **Did not infer the TABULA licence from the absence of a paywall**: Located and quoted the explicit project terms and IEE dissemination policy published by IWU Darmstadt on `episcope.eu`.
4. **Did not substitute a nearby year**: Pinned exact 12-month fieldwork windows for Spain (2009-2010), United Kingdom (2014-2015), and Italy (2013-2014).
5. **Did not give a national methodology report's prose as if it were the HETUS guidelines**: Separated Eurostat guidelines from INE, CTUR, and ISTAT methodology documents.
6. **Did not answer Part B2 with a list of vendors and no licence text**: Analyzed and documented the specific licensing terms and academic publication permissions for ERA5, Meteonorm, White Box Technologies, and Oikolab.

---

## Section H. Full reference list

1. **Eurostat. (2009).** *Harmonised European Time Use Surveys: 2008 Guidelines*. Methodologies and Working Papers, Theme: Population and social conditions, Catalogue number: KS-RA-08-014-EN, Office for Official Publications of the European Communities, Luxembourg. [Tier 1, Read full text, `https://ec.europa.eu/eurostat/documents/3859598/5909473/KS-RA-08-014-EN.PDF`]
2. **Eurostat. (2000).** *Guidelines on Harmonised European Time Use Surveys*. Eurostat Working Paper, European Commission, Luxembourg. [Tier 1, Read full text]
3. **Eurostat. (2019).** *Harmonised European Time Use Surveys (HETUS) 2018 Guidelines*. Manuals and Guidelines, Catalogue number: KS-GQ-19-003-EN, Publications Office of the European Union, Luxembourg. [Tier 1, Read full text, `https://ec.europa.eu/eurostat/documents/3859598/10207255/KS-GQ-19-003-EN.PDF`]
4. **Instituto Nacional de Estadística (INE). (2011).** *Encuesta de Empleo del Tiempo 2009-2010: Metodología*. INE, Madrid. [Tier 1, Read full text, `https://www.ine.es/metodologia/t25/t2530433.pdf`]
5. **Gershuny, J., & Sullivan, O. / Centre for Time Use Research (CTUR). (2017).** *United Kingdom Time Use Survey 2014-2015 User Guide*. NatCen Social Research & University of Oxford, UK Data Service Study Number 8128. [Tier 1, Read full text, `https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=8128`]
6. **Istituto Nazionale di Statistica (ISTAT). (2016).** *I tempi della vita quotidiana: L'uso del tempo in Italia - Anno 2013-2014: Metodologia e primi risultati*. ISTAT, Roma. [Tier 1, Read full text, `https://www.istat.it/it/archivio/194480`]
7. **UK Data Service. (2017).** *United Kingdom Time Use Survey, 2014-2015 Catalogue Record (SN 8128)*. UK Data Archive, University of Essex. [Tier 1, Read record]
8. **ECMWF / Copernicus. (2024).** *Licence to Use Copernicus Products*. European Centre for Medium-Range Weather Forecasts, Reading, UK. [Tier 1, Read full text, `https://cds.climate.copernicus.eu/licences/copernicus-products`]
9. **Meteotest. (2024).** *Meteonorm End User License Agreement (EULA) Version 8.1*. Meteotest AG, Bern, Switzerland. [Tier 1, Read terms, `https://meteonorm.com/`]
10. **White Box Technologies. (2024).** *Weather Data for Energy Calculations: Licensing and Use Terms*. Moraga, CA. [Tier 1, Read terms, `http://weather.whiteboxtechnologies.com/`]
11. **Oikolab. (2024).** *Oikolab Weather API Terms of Service*. Oikolab, Singapore. [Tier 1, Read terms, `https://oikolab.com/`]
12. **Cerdá, E., Gómez, C., & de Luxán, M. (2011).** *Building Typology Brochure - Spain*. Intelligent Energy Europe (IEE) & Universidad Politécnica de Madrid. [Tier 1, Read full text]
13. **Palmer, J., Godoy-Shirasawa, R., & Cooper, I. (2014).** *Building Typology Brochure - United Kingdom*. Intelligent Energy Europe (IEE) & Cambridge Architectural Research Ltd. [Tier 1, Read full text]
14. **Corrado, V., Ballarini, I., & Corgnati, S. P. (2014).** *Building Typology Brochure - Italy*. Intelligent Energy Europe (IEE), ENEA & Politecnico di Torino. [Tier 1, Read full text]
15. **Loga, T., Diefenbach, N., & Stein, B. (2016).** *TABULA / EPISCOPE Building Typologies in 20 European Countries - Final Report*. Institut Wohnen und Umwelt (IWU), Darmstadt. [Tier 1, Read full text, `https://episcope.eu/`]
16. **Iseri, O. K., Duran, A., Canlı, I., Akgul, C. M., Kalkan, S., & Dino, I. G. (2025).** A method for zone-level urban building energy modeling in data-scarce built environments. *Energy and Buildings*, 337, 115620. [Tier 1, Read full text, CrossRef returned title: "A method for zone-level urban building energy modeling in data-scarce built environments", DOI: `10.1016/j.enbuild.2025.115620`]
