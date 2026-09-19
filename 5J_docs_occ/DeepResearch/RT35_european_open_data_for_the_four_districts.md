# RT35: European Open Data for Occupancy Around the Four Districts: Madrid, Lyon, London, and Bologna

## Section A. Direct answer

Across the four European districts modeled in OpenUBEM (Madrid Berruguete, Lyon Croix-Rousse, London St Dunstan's, and Bologna Galvani 2), the only occupancy-relevant open sources that exist for all four at comparable spatial resolution are national census demographic tables, OpenStreetMap building geometries, and continental satellite layers (JRC GHSL and ENACT-POP 1 km2 grids). Beyond these baselines, local open data provision is severely asymmetrical across countries: Lyon Croix-Rousse (France) is the best served district, benefiting from an open, reproducible agent-based travel simulation pipeline (eqasim Lyon), high-resolution census micro-zones (INSEE IRIS), and sub-municipal open electricity consumption data from Enedis. Madrid Berruguete is also strongly served by the open Spanish MITMA big-data mobile network study, which provides hourly presence and trip flows across transport zones. London St Dunstan's benefits from open low-voltage feeder data from UK Power Networks and London Datastore feeds. Bologna Galvani 2 (Italy) is the worst served district, possessing no open mobile network feeds, no open synthetic populations, and closed utility load data.

---

## Section B. Findings table

### Table B1. Unique and shared occupancy data sources across the four European districts (Item 2)

| # | Source or feature | Geographic availability across the 4 districts | Smallest spatial unit containing the district | Source details & status |
|---|---|---|---|---|
| 1 | **Open Synthetic Population Pipeline** | **Lyon only (Unique to France)**; absent in Madrid, London, Bologna | Metropolitan Lyon (eqasim open pipeline) | eqasim pipeline synthesizes 24h individual activity schedules from open census and EMP travel survey data. |
| 2 | **Open Big-Data Mobile Mobility** | **Madrid only (Unique to Spain)**; absent in Lyon, London, Bologna | Transport Analysis Zone (MITMA 3,200 zones) | MITMA open big-data mobility portal publishes hourly presence and OD matrices based on Orange network data. |
| 3 | **Open Low-Voltage Feeder Telemetry** | **London only (Unique to UK)**; absent in Madrid, Lyon, Bologna | Primary/secondary substation (UKPN Open Data) | UK Power Networks Open Data Portal provides open hourly/half-hourly load curves for secondary substations. |
| 4 | **Sub-Municipal Open Electricity Totals** | **Lyon (France)** and **London (UK)**; absent in Madrid, Bologna | IRIS (France) / LSOA (UK) | Enedis Open Data publishes annual/monthly residential electricity consumption by 200-meter carreaux and IRIS. |
| 5 | **Shared Continental Baselines** | **All four districts (Madrid, Lyon, London, Bologna)** | 1 km2 grid (ENACT-POP) / Census tracts | JRC ENACT-POP day/night population (2011), Eurostat HETUS national time-use diaries, OSM building geometries. |

---

## Section C. Landscape table (prior work)

### Table C1. Studies utilizing local European open data for building occupancy or urban energy modeling

| # | Work (first author, year, venue) | DOI (verified) | What it did | Sources used | District / Country | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Hörl & Balac (2021), *Transp. Res. Part C* | 10.1016/j.trc.2021.103291<br>CrossRef: *Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data* | Built and validated open synthetic population and travel demand pipeline using open French census and travel data | French census (RP) + EMP travel survey | France (applicable to Lyon Croix-Rousse) | Did not model indoor building energy or thermal loads | Full |
| L02 | Batista e Silva et al. (2020), *Nat. Commun.* | 10.1038/s41467-020-18344-5<br>CrossRef: *Uncovering temporal changes in Europe’s population density patterns using a data fusion approach* | Produced ENACT-POP 1 km2 day and night population grids across all EU member states | Census, commuting flows, tourism statistics | All 4 districts (Madrid, Lyon, London, Bologna) | Frozen at 2011 baseline; did not separate residential daytime presence | Full |
| L03 | Santiago et al. (2021), *Energy Policy* | 10.1016/j.enpol.2020.111964<br>CrossRef: *Electricity demand during pandemic times: The case of the COVID-19 in Spain* | Evaluated Spanish national electricity load changes during COVID lockdowns using mobility and grid data | Red Eléctrica hourly load + Google mobility | Spain (applicable to Madrid Berruguete) | Did not construct bottom-up district building models | Full |
| L04 | Banfi et al. (2024), *Energies* | 10.3390/en17174400<br>CrossRef: *Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges* | Reviewed state of occupant behavior modeling in European UBEM, identifying severe data disparities between cities | Literature survey across European UBEM projects | European urban stock | Highlighted lack of empirical calibration datasets in Italian UBEM | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of the European arm of Angle A14 across the four districts

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Local multi-country open data calibration of European UBEM districts)** | **Unclaimed** (Open in UBEM; highly attractive) | OpenUBEM 4-district GIS models, HETUS corpora, eqasim Lyon, MITMA Madrid | Equal-resolution local feeder/mobility data for Bologna | "Your four-district comparison is fundamentally asymmetrical: Lyon has a full synthetic population, Madrid has mobile network data, London has feeder load, and Bologna has almost nothing." | 6 to 8 months |

---

## Section E. What this changes in our planning

* **Establish a tiered data architecture for the four European districts:**
  1. *Common Tier (All 4 Districts)*: National HETUS time-use schedules (`R1`), Census demographic marginals, and JRC GHSL/ENACT-POP day-night density boundaries (`R2`).
  2. *District-Specific Empirical Enhancers*:
     - **Madrid Berruguete**: Calibrate hourly daytime occupancy fractions using the open Spanish MITMA big-data mobile dataset.
     - **Lyon Croix-Rousse**: Use the open eqasim synthetic population pipeline to generate building-assigned arrival and departure times.
     - **London St Dunstan's**: Benchmark simulated district electrical demand against open UK Power Networks LV feeder telemetry.
     - **Bologna Galvani 2**: Rely strictly on Istat census small-area statistics and HETUS Italy diaries, serving as the "minimal data" baseline district.
* **Avoid claiming uniform multi-country calibration.** 5J must explicitly frame the data asymmetry as a core research question: How much does local data availability (e.g. eqasim in Lyon vs. minimal data in Bologna) reduce simulated energy prediction uncertainty?

---

## Section F. Concrete artefacts to retrieve

### Table F1. District-by-district registry of local open data sources (Item 1)

| District & city | Dataset name & custodian | Smallest spatial unit containing the district | Data type & resolution | Access conditions & Canadian eligibility (Checked: 2026-09-18) | URL or stable pointer |
|---|---|---|---|---|---|
| **Madrid Berruguete**<br>(Spain) | MITMA Open Big Data Mobility<br>Min. Transportes (Spain) | Distrital / Transport Analysis Zone (Tetuán / Berruguete) | Hourly origin-destination matrices and population present | Open download via MITMA portal. Free worldwide. | `https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data` |
| **Madrid Berruguete**<br>(Spain) | Geoportal del Ayuntamiento de Madrid<br>Ayuntamiento de Madrid | Barrio de Berruguete (District of Tetuán) | Cadastral building heights, uses, and population register | Open download. Creative Commons CC BY 4.0. Free worldwide. | `https://geoportal.madrid.es/` |
| **Lyon Croix-Rousse**<br>(France) | eqasim Lyon Synthetic Population<br>eqasim org / ETH Zurich | 4ème arrondissement de Lyon (Croix-Rousse) | 24-hour individual agent activity schedules | Open download on GitHub. MIT License. Free worldwide. | `https://github.com/eqasim-org/eqasim-java` |
| **Lyon Croix-Rousse**<br>(France) | Données d'énergie Enedis<br>Enedis Open Data | IRIS / 200m carreaux (Lyon 4e) | Annual/monthly residential electricity consumption | Open download via Enedis portal. Open License. Free worldwide. | `https://data.enedis.fr/` |
| **London St Dunstan's**<br>(UK) | UKPN Open Data Portal<br>UK Power Networks | Secondary substation (Tower Hamlets / Stepney) | Half-hourly real and reactive electrical feeder loads | Open download via UKPN Open Data. Free worldwide. | `https://connecteddata.ukpowernetworks.co.uk/` |
| **London St Dunstan's**<br>(UK) | London Datastore<br>Greater London Authority | Lower Super Output Area (LSOA Tower Hamlets) | Small-area population, housing tenure, energy consumption | Open download. UK Open Government Licence. Free worldwide. | `https://data.london.gov.uk/` |
| **Bologna Galvani 2**<br>(Italy) | Open Data Comune di Bologna<br>Comune di Bologna | Sezione di censimento (Quartiere Santo Stefano) | Resident population by age and nationality, building cadastral data | Open download via Bologna Open Data. CC BY 4.0. Free worldwide. | `https://dati.comune.bologna.it/` |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Critical gaps in European district open data

- **The Italian Utility Data Void**: Unlike France (Enedis) and the UK (UK Power Networks), Italian distribution system operators (E-Distribuzione) publish zero sub-municipal or low-voltage feeder load data on open portals. Research in Bologna Galvani 2 must rely entirely on top-down statistical energy benchmarks.
- **Temporal Baseline Divergence**: Cross-district modeling faces significant temporal baseline shifts: eqasim Lyon is parameterized on pre-2020 travel surveys; MITMA Madrid captures continuous 2020-2022 pandemic and post-pandemic mobility; UKPN London feeds reflect continuous real-time smart grid measurements.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Hörl & Balac (2021) [*Transp. Res. Part C*], Batista e Silva et al. (2020) [*Nat. Commun.*], Santiago et al. (2021) [*Energy Policy*], Banfi et al. (2024) [*Energies*].
   - *Seen described:* Enedis Open Data user guides, UK Power Networks portal technical documentation, Comune di Bologna open data manuals.
   - Count opened in full: 4. Count seen described: 3.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote that an open synthetic population pipeline is `NOT FOUND` for Bologna Galvani 2.
   - I wrote that open low-voltage feeder load data is `NOT FOUND` for Madrid, Lyon, and Bologna.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The generation of continental day-night population grids is claimed by JRC ENACT-POP (Batista e Silva et al. 2020).
   - In UBEM, multi-country district modeling exploiting asymmetrical national open data (eqasim, MITMA, UKPN) across four European cities is unclaimed.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all district boundaries and portal access conditions reflect confirmed geospatial registers.

---

## Section H. Full reference list

1. Hörl, S., & Balac, M. (2021). Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data. *Transportation Research Part C: Emerging Technologies*, 130, 103291. DOI: 10.1016/j.trc.2021.103291. CrossRef returned title: "Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data". Read: full text. [Tier 1]
2. Batista e Silva, F., Poelman, H., Vandecasteele, I., Lavalle, C., & Schiavina, M. (2020). Uncovering temporal changes in Europe’s population density patterns using a data fusion approach. *Nature Communications*, 11(1), 4631. DOI: 10.1038/s41467-020-18344-5. CrossRef returned title: "Uncovering temporal changes in Europe’s population density patterns using a data fusion approach". Read: full text. [Tier 1]
3. Santiago, I., Moreno-Munoz, A., Quintero-Jiménez, P., Garcia-Torres, F., & Gonzalez-Redondo, M. J. (2021). Electricity demand during pandemic times: The case of the COVID-19 in Spain. *Energy Policy*, 148, 111964. DOI: 10.1016/j.enpol.2020.111964. CrossRef returned title: "Electricity demand during pandemic times: The case of the COVID-19 in Spain". Read: full text. [Tier 1]
4. Banfi, A., Fabrizio, E., & Causone, F. (2024). Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges. *Energies*, 17(17), 4400. DOI: 10.3390/en17174400. CrossRef returned title: "Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges". Read: full text. [Tier 1]
