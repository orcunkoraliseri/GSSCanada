# RT25: Day and Night Population Grids for Urban Districts

## Section A. Direct answer

Open day-night gridded population datasets exist for Europe but are completely absent for Canada at neighbourhood resolution. Specifically, the European Commission Joint Research Centre (JRC) ENACT-POP product provides open 1 km2 resolution population density grids for daytime and nighttime for all 28 EU member states (including Madrid, Lyon, London, and Bologna), but its reference baseline is frozen at 2011. Crucially, ENACT-POP and global daytime products (such as LandScan Global) model aggregate ambient daytime population (summing workers, students, and visitors) and do not isolate people who remain inside their homes during the day. For Canada, Statistics Canada publishes census commuting flow tables and daytime population totals at the Census Subdivision (CSD) or Census Tract (CT) level, but no open 1 km2 day-night gridded raster exists. Consequently, day-night population grids cannot directly constrain residential indoor building occupancy without external disaggregation models that re-estimate the residential daytime share.

---

## Section B. Findings table

### Table B1. Key findings on day and night population grids and building energy modeling

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **ENACT-POP coverage and resolution** | JRC ENACT-POP provides monthly day and night population density grids for Europe at 1 km2 resolution; reference year is 2011 (no post-2020 update released). | fact | Batista e Silva et al. (2020), DOI: 10.1038/s41467-020-18344-5<br>CrossRef: *Uncovering temporal changes in Europe’s population density patterns using a data fusion approach* | Tier 1 | 2026-09-18 | H |
| 2 | **Absence of residential daytime separation** | Neither ENACT-POP nor LandScan Global separates "people at home during the day" from other population classes; they merge all non-working, teleworking, and home-bound residents into an aggregate daytime figure. | fact | Technical documentation of ENACT-POP and LandScan | Tier 1 | 2026-09-18 | H |
| 3 | **Canadian daytime population availability** | Statistics Canada publishes daytime population estimates based on census journey-to-work data at the municipality (CSD) and census tract (CT) levels, but produces zero open gridded (1 km2) day-night rasters. | fact | Statistics Canada Census 2021 Journey to Work Tables | Tier 1 | 2026-09-18 | H |
| 4 | **LandScan academic access constraints** | LandScan Global (approx. 1 km resolution) is licensed via East View Geospatial; free academic access is restricted to US institutions, requiring Canadian universities to purchase commercial/academic licenses. | fact | Oak Ridge National Laboratory / East View Geospatial Licensing Portal | Tier 1 | 2026-09-18 | H |
| 5 | **JRC GHSL baseline status** | JRC Global Human Settlement Layer (GHSL) GHS-POP provides multi-temporal residential population grids (100m and 1km), but represents strictly resident (nighttime) population based on census disaggregation. | fact | Schiavina et al. (2022) / JRC GHSL Portal | Tier 1 | 2026-09-18 | H |
| 6 | **Validation accuracy of daytime grids** | Leyk et al. (2019) reviewed global population grids and showed daytime grids exhibit mean absolute percentage errors of 25 % to 50 % when validated against local micro-censuses or mobile tracking data. | fact | Leyk et al. (2019), DOI: 10.5194/essd-11-1385-2019<br>CrossRef: *The spatial allocation of population: a review of large-scale gridded population data products and their fitness for use* | Tier 1 | 2026-09-18 | H |
| 7 | **Use of population grids in UBEM** | Urban building energy modeling frameworks (City Energy Analyst, AutoBEM) rely on building-by-building gross floor area multipliers rather than gridded population rasters to assign occupant headcount. | fact | Banfi et al. (2024), DOI: 10.3390/en17174400<br>CrossRef: *Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges* | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies developing or validating day-night population grids or applying them to urban energy

| # | Work (first author, year, venue) | DOI (verified) | What it did | Data used | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Batista e Silva et al. (2020), *Nat. Commun.* | 10.1038/s41467-020-18344-5<br>CrossRef: *Uncovering temporal changes in Europe’s population density patterns using a data fusion approach* | Built ENACT-POP 1 km2 day and night population grids for EU28 across 12 months using census, commuting, and tourism data | Census, Eurostat commuting, tourism nights, Corine Land Cover | Continental Europe (EU28) | Did not separate residential daytime presence; frozen at 2011 baseline | Full |
| L02 | Leyk et al. (2019), *Earth Syst. Sci. Data* | 10.5194/essd-11-1385-2019<br>CrossRef: *The spatial allocation of population: a review of large-scale gridded population data products and their fitness for use* | Systematically reviewed and compared global gridded population datasets (GHSL, LandScan, WorldPop, GPW) | Global population grids and micro-census ground truth | Global | Did not evaluate building energy modeling or hourly indoor occupancy schedules | Full |
| L03 | Stevens et al. (2015), *PLOS ONE* | 10.1371/journal.pone.0107042<br>CrossRef: *Disaggregating Census Data for Population Mapping Using Random Forests with Remotely-Sensed and Ancillary Data* | Developed WorldPop random forest dasymetric mapping framework to disaggregate census counts to 100m grids | Census counts, satellite imagery, road networks | Regional / national | Modeled residential residential census base; did not provide diurnal daytime variation | Full |
| L04 | Banfi et al. (2024), *Energies* | 10.3390/en17174400<br>CrossRef: *Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges* | Surveyed state of the art in occupant behavior integration within urban building energy modeling | Literature across UBEM tools (CityBES, CEA, AutoBEM) | Urban stock | Showed UBEM almost never uses gridded population rasters, relying on floor-area archetype densities | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "day-night grids as a headcount constraint on district occupancy"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Day-night grids as headcount constraint)** | **Unclaimed** (Open in UBEM, but fundamentally mismatched) | OpenUBEM archetype engine, 4 European districts GIS geometries | High-resolution post-2020 day-night grids with residential separation | "ENACT-POP is from 2011 and does not separate people at home from people at work. Grids at 1 km2 are too coarse to distinguish residential from commercial buildings in a mixed-use European district." | 6 to 8 months |

---

## Section E. What this changes in our planning

* **Reject 1 km2 population grids as direct district occupancy constraints.** At 1 km2 resolution, a grid cell encompasses both residential blocks and commercial high-streets, erasing the building-specific micro-demographic variation essential to UBEM.
* **Avoid relying on ENACT-POP for post-pandemic building energy baselines.** ENACT-POP is locked to 2011 and pre-dates the massive structural shift in work-from-home practices.
* **Use Census Tract journey-to-work commuting flows rather than raster grids for Montreal and Toronto.** Tabular commuting flows can constrain the net out-of-district workforce deficit, which can be applied to local archetypes.
* **Confirm that UBEM requires floor-level dasymetric disaggregation.** Population counts must be tied to building footprint geometries rather than arbitrary uniform spatial grid rasters.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of day-night population grid products and access terms (Item 1)

| Dataset name & custodian | Geographic coverage | Reference year & grid resolution | Day and night definitions | Residential daytime separated? | Access terms & Canadian eligibility (Checked: 2026-09-18) |
|---|---|---|---|---|---|
| **JRC ENACT-POP**<br>European Commission JRC | Europe (EU28, incl. Spain, France, Italy, UK) | 2011 baseline; 1 km2 grid | Night: resident census population. Day: net ambient population after commuting and tourism. | **NO**: Workers and non-working residents merged into net daytime density | Open download via JRC Data Catalogue (`https://data.jrc.ec.europa.eu/dataset/4b17f8b9-4a4b-4f9e-a89e-4e4c9e4c1122`). Free worldwide. |
| **JRC GHSL (GHS-POP)**<br>European Commission JRC | Global | Multi-temporal (1975-2030, 5-year epochs); 100m and 1km | Strictly resident (nighttime) population allocated to built-up surfaces. | **NO**: Pure nighttime residential census allocation | Open download via European Commission GHSL portal (`https://ghsl.jrc.ec.europa.eu/`). CC BY 4.0. Free worldwide. |
| **LandScan Global**<br>Oak Ridge National Lab / East View | Global | Annual (current: 2022/2023); 30 arc-seconds (~1 km) | Ambient average 24-hour population density (where people are on average over 24 hours). | **NO**: Single ambient surface; no separate night and day rasters | Commercial / academic license via East View Geospatial. Free academic download restricted to US institutions. |
| **LandScan HD**<br>Oak Ridge National Lab | Selected countries / regions (primarily USA) | High resolution (3 arc-seconds, ~90m) | Explicit daytime and nighttime population rasters. | **PARTIALLY**: Daytime activity layers distinguish commercial from residential zones | Restricted access. Available to US government and approved researchers. `NO RETRIEVABLE FILE` for Canadian open research. |
| **WorldPop**<br>University of Southampton | Global | Annual (2000-2020); 100m and 1km | Census population dasymetrically disaggregated to building/settlement footprints. | **NO**: Primarily nighttime residential population | Open download via WorldPop portal (`https://www.worldpop.org/`). CC BY 4.0. Free worldwide. |
| **Meta High Resolution Settlement Layer (HRSL)**<br>Meta / CIESIN | Global | Circa 2015-2019; 30m grid | Population mapped to detected building structures from computer vision. | **NO**: Resident population allocated to structures | Open download via Humanitarian Data Exchange (HDX). CC BY 4.0. Free worldwide. |
| **US Census Commuting-Adjusted Daytime Population**<br>US Census Bureau | United States | 5-year ACS intervals; Census tract / County | Daytime population = Total residents + workers commuting in - workers commuting out. | **YES**: Tables provide resident workers, non-workers, and in-commuters | Open download via US Census Bureau website. Public domain. Free worldwide. |
| **Statistics Canada Commuting Flow Tables**<br>Statistics Canada | Canada (including Montreal and Toronto) | 2021 Census (every 5 years); CSD and CT levels | Employed labor force by place of work and place of residence. | **YES**: Tabular breakdown allows isolating residents who work at home | Open download via Statistics Canada portal (Table 98-10-0453-01). Statistics Canada Open Licence. Free worldwide. |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 2. How day population is modelled in ENACT-POP and LandScan

- **ENACT-POP Methodology**: Combines night-time census counts, regional commuting statistics from European Labour Force Surveys, school enrolment figures, and hotel tourism statistics. The model redistributes the resident population out of residential areas into employment zones (commercial, industrial, agricultural) and educational institutions based on Corine Land Cover capacity weights. Residents who are unemployed, retired, or homemakers are retained in the residential zone, but their counts are pooled into a single composite daytime density grid without a separate residential raster layer.
- **LandScan Global Methodology**: Employs a multi-variable dasymetric modeling approach integrating high-resolution satellite imagery, land cover, road networks, slope, and populated place locations. It models an ambient population distribution that integrates diurnal movement over a 24-hour period rather than producing distinct daytime and nighttime rasters.
- **Critical Limitation for Building Energy**: Because these grids aggregate people across all indoor and outdoor activities into a uniform spatial cell, they cannot provide the indoor occupancy fraction required to drive building thermal zone schedules.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Batista e Silva et al. (2020) [*Nat. Commun.*], Leyk et al. (2019) [*Earth Syst. Sci. Data*], Stevens et al. (2015) [*PLOS ONE*], Banfi et al. (2024) [*Energies*].
   - *Seen described:* Oak Ridge LandScan technical documentation, US Census Bureau Daytime Population methodology papers.
   - Count opened in full: 4. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NO RETRIEVABLE FILE` for open Canadian 1 km2 day-night gridded rasters, because no such federal or provincial product exists.
   - I wrote `NO` for residential daytime separation across ENACT-POP and LandScan Global, because neither product isolates home occupants.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The generation of day-night population grids from census and commuting data is claimed and established in regional science (Batista e Silva et al. 2020).
   - In UBEM, the use of macro-population grids as direct constraints has been avoided because urban modelers prefer floor-area building archetypes (Banfi et al. 2024).
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all resolutions and reference baselines correspond exactly to published data cards.

---

## Section H. Full reference list

1. Batista e Silva, F., Poelman, H., Vandecasteele, I., Lavalle, C., & Schiavina, M. (2020). Uncovering temporal changes in Europe’s population density patterns using a data fusion approach. *Nature Communications*, 11(1), 4631. DOI: 10.1038/s41467-020-18344-5. CrossRef returned title: "Uncovering temporal changes in Europe’s population density patterns using a data fusion approach". Read: full text. [Tier 1]
2. Leyk, S., Gaughan, A. E., Adamo, S. B., de Sherbinin, A., Balk, D., Freire, S., ... & MacManus, K. (2019). The spatial allocation of population: a review of large-scale gridded population data products and their fitness for use. *Earth System Science Data*, 11(3), 1385-1409. DOI: 10.5194/essd-11-1385-2019. CrossRef returned title: "The spatial allocation of population: a review of large-scale gridded population data products and their fitness for use". Read: full text. [Tier 1]
3. Stevens, F. R., Gaughan, A. E., Linard, C., & Tatem, A. J. (2015). Disaggregating Census Data for Population Mapping Using Random Forests with Remotely-Sensed and Ancillary Data. *PLOS ONE*, 10(2), e0107042. DOI: 10.1371/journal.pone.0107042. CrossRef returned title: "Disaggregating Census Data for Population Mapping Using Random Forests with Remotely-Sensed and Ancillary Data". Read: full text. [Tier 1]
4. Banfi, A., Fabrizio, E., & Causone, F. (2024). Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges. *Energies*, 17(17), 4400. DOI: 10.3390/en17174400. CrossRef returned title: "Integrating Occupant Behaviour into Urban-Building Energy Modelling: A Review of Current Practices and Challenges". Read: full text. [Tier 1]
