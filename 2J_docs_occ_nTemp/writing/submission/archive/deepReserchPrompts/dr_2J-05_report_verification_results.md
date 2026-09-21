# Deep-Research Report dr_2J-05: Falsification and Verification Results

**Scope Guard:** Falsification pass over `dr_2J-01_journal_fit_shortlist_results.md` and `dr_2J-02_rejection_repositioning_report.md`. Every load-bearing claim is marked CONFIRMED, CORRECTED, or NOT FOUND with its primary verification link.

---

## REQUIRED OUTPUT TABLES

### Table 1: DOI verification across all cited articles in both reports and controls

Positive controls:
- Osman and Ouf (2021), Building and Environment 202, 108037: CONFIRMED (DOI: 10.1016/j.buildenv.2021.108037).
- Widen and Wackelgard (2010), Applied Energy 87(6), 1880-1892: CONFIRMED (DOI: 10.1016/j.apenergy.2009.11.006).
- Aerts et al. (2014), Building and Environment 75, 257-268: CONFIRMED (DOI: 10.1016/j.buildenv.2014.01.021).

| # | Report and table | DOI as given | Resolves? | Actual title / authors / journal / year at that DOI | Verdict | Correct DOI if paper is real but DOI is wrong |
|---|---|---|---|---|---|---|
| 1 | dr_2J-01 Table 2 | 10.1007/s12273-023-1032-2 | Yes | "Using urban building energy modeling to quantify the energy performance of residential buildings under climate change" / Deng, Javanroodi, Nik, Chen / Building Simulation / 2023 | CONFIRMED | [10.1007/s12273-023-1032-2](https://doi.org/10.1007/s12273-023-1032-2) |
| 2 | dr_2J-01 Table 2 | 10.1007/s12273-021-0878-4 | Yes | "Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets" / Deng, Chen, Yang, Chen / Building Simulation / 2022 | CONFIRMED | [10.1007/s12273-021-0878-4](https://doi.org/10.1007/s12273-021-0878-4) |
| 3 | dr_2J-01 Table 2 | 10.1007/s12273-025-1235-9 | Yes | "Large language models for building energy applications: Opportunities and challenges" / Liu, Zhang, Chen, Chen, Yang, Lo, Wen, O'Neill / Building Simulation / 2025 | CONFIRMED | [10.1007/s12273-025-1235-9](https://doi.org/10.1007/s12273-025-1235-9) |
| 4 | dr_2J-01 Table 2 | 10.1016/j.scs.2023.104478 | Yes | "Can smart city construction improve carbon productivity? A quasi-natural experiment based on China's smart city pilot" / Song, Dian, Chen / Sustainable Cities and Society / 2023 | CORRECTED (Claimed title and authors are fabricated; DOI belongs to different paper) | [10.1016/j.scs.2023.104478](https://doi.org/10.1016/j.scs.2023.104478) |
| 5 | dr_2J-01 Table 2 | 10.1016/j.scs.2024.105120 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated DOI and citation) |
| 6 | dr_2J-01 Table 2 | 10.1016/j.scs.2022.104310 | Yes | "Spatial decision support system for low-carbon sustainable cities development: An interactive storytelling dashboard for the city of Turin" / Pignatelli, Torabi Moghadam, Genta, Lombardi / Sustainable Cities and Society / 2023 | CORRECTED (Claimed Martinez et al. title is fabricated; DOI belongs to Turin dashboard paper) | [10.1016/j.scs.2022.104310](https://doi.org/10.1016/j.scs.2022.104310) |
| 7 | dr_2J-01 Table 2 | 10.1016/j.apenergy.2023.121607 | Yes | "Interpretable building energy consumption forecasting using spectral clustering algorithm and temporal fusion transformers architecture" / Zheng, Zhou, Liu, Nakanishi / Applied Energy / 2023 | CORRECTED (Authors are Zheng, Zhou, Liu, Nakanishi, not Zhang et al.) | [10.1016/j.apenergy.2023.121607](https://doi.org/10.1016/j.apenergy.2023.121607) |
| 8 | dr_2J-01 Table 2 | 10.1016/j.apenergy.2025.125421 | Yes | "Flattening the peak demand curve through energy efficient buildings: A holistic approach towards net-zero carbon" / Akhmetov, Fedotova, Frysztacki / Applied Energy / 2025 | CORRECTED (Claimed Perez et al. title is fabricated; DOI belongs to Akhmetov et al.) | [10.1016/j.apenergy.2025.125421](https://doi.org/10.1016/j.apenergy.2025.125421) |
| 9 | dr_2J-01 Table 2 | 10.1016/j.apenergy.2022.120443 | Yes | "Blockchain + IoT sensor network to measure, evaluate and incentivize personal environmental accounting and efficient energy use in indoor spaces" / Ma, Waegel, Hakkarainen, Braham, Glass, Aviv / Applied Energy / 2023 | CORRECTED (Authors are Ma, Waegel, et al., not Chen, Y. et al.) | [10.1016/j.apenergy.2022.120443](https://doi.org/10.1016/j.apenergy.2022.120443) |
| 10 | dr_2J-01 Table 2 | 10.1016/j.enbuild.2024.113854 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated DOI and citation) |
| 11 | dr_2J-01 Table 2 | 10.1016/j.enbuild.2022.112754 | Yes | "Modeling of occupant behavior considering spatial variation: Geostatistical analysis and application based on American time use survey data" / Li, Yamaguchi, Torriti, Shimoda / Energy and Buildings / 2023 | CONFIRMED (Authored by Li, Yamaguchi, Torriti, Shimoda) | [10.1016/j.enbuild.2022.112754](https://doi.org/10.1016/j.enbuild.2022.112754) |
| 12 | dr_2J-01 Table 2 | 10.1016/j.enbuild.2024.114639 | Yes | "Informing targeted Demand-Side Management: Leveraging appliance usage patterns to model residential energy demand heterogeneity" / Barsanti, Yilmaz, Binder / Energy and Buildings / 2024 | CONFIRMED | [10.1016/j.enbuild.2024.114639](https://doi.org/10.1016/j.enbuild.2024.114639) |
| 13 | dr_2J-01 Table 2 | 10.1080/19401493.2025.2474121 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Anonymous T&F placeholder fabricated) |
| 14 | dr_2J-01 Table 2 | 10.1080/19401493.2024.2445123 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Anonymous T&F placeholder fabricated) |
| 15 | dr_2J-01 Table 2 | 10.1016/j.energy.2023.126680 | Yes | "A new technique for estimation of photovoltaic system and tracking power peaks of PV array under partial shading" / Ragb, Bakr / Energy / 2023 | CORRECTED (Claimed Zhao et al. title is fabricated; DOI belongs to solar PV tracking paper) | [10.1016/j.energy.2023.126680](https://doi.org/10.1016/j.energy.2023.126680) |
| 16 | dr_2J-01 Table 2 | 10.1016/j.energy.2024.130150 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated competitor paper) |
| 17 | dr_2J-01 Table 2 | 10.1016/j.jobe.2024.108710 | Yes | "Optimization of global energy consumption of buildings based on photothermal coupling effect of exterior windows in Qinghai-Tibet plateau" / Wang, Wu, Dong, Liu, Lei, Mai / Journal of Building Engineering / 2024 | CORRECTED (Claimed Li et al. title is fabricated; DOI belongs to Qinghai-Tibet window study) | [10.1016/j.jobe.2024.108710](https://doi.org/10.1016/j.jobe.2024.108710) |
| 18 | dr_2J-01 Table 2 | 10.1016/j.adapen.2023.100145 | Yes | "Global transition of operational carbon in residential buildings since the millennium" / Xiang, Zhou, Ma, Feng, Yan / Advances in Applied Energy / 2023 | CORRECTED (Claimed Gupta et al. title is fabricated; DOI belongs to global operational carbon paper) | [10.1016/j.adapen.2023.100145](https://doi.org/10.1016/j.adapen.2023.100145) |
| 19 | dr_2J-01 Table 2 | 10.1016/j.egai.2024.100340 | No (404) | Corrupted DOI stem (j.egai does not resolve) | CORRECTED (Resolves under valid stem 10.1016/j.egyai.2024.100340 to Zhang et al., not Yang et al.) | [10.1016/j.egyai.2024.100340](https://doi.org/10.1016/j.egyai.2024.100340) |
| 20 | dr_2J-01 Table 2 | 10.3390/buildings14020412 | Yes | "Structural Behaviour of FRP-Reinforced Tubular T-Joint Subjected to Combined In-Plane Bending and Axial Load" / Deng, Chen, Zhu, Liu, Zhao, Guo / Buildings / 2024 | CORRECTED (Claimed Sun et al. load shape title is fabricated; DOI belongs to structural steel joint paper) | [10.3390/buildings14020412](https://doi.org/10.3390/buildings14020412) |
| 21 | dr_2J-01 Table 2 | 10.3390/en16083412 | Yes | "Critical Review on Community-Shared Solar: Advantages, Challenges, and Future Directions" / Narjabadifam, Fouladvand, Gul / Energies / 2023 | CORRECTED (Claimed Kim et al. synthetic schedule title is fabricated; DOI belongs to solar review) | [10.3390/en16083412](https://doi.org/10.3390/en16083412) |
| 22 | dr_2J-01 Table 2 | 10.1016/j.buildenv.2024.111220 | Yes | "Ten questions concerning absolute sustainability in the built environment" / Andersen, Petersen, Ryberg, Molander, Birkved / Building and Environment / 2024 | CORRECTED (Claimed Xu et al. post-COVID paper is fabricated; DOI belongs to 10 questions paper) | [10.1016/j.buildenv.2024.111220](https://doi.org/10.1016/j.buildenv.2024.111220) |
| 23 | dr_2J-01 Table 2 | 10.1016/j.enpol.2023.113450 | Yes | "Impacts of income poverty and high housing costs on fuel poverty in Egypt: An empirical modeling approach" / Belaid, Flambard / Energy Policy / 2023 | CORRECTED (Claimed Smith et al. WFH paper is fabricated; DOI belongs to Egypt fuel poverty paper) | [10.1016/j.enpol.2023.113450](https://doi.org/10.1016/j.enpol.2023.113450) |
| 24 | dr_2J-01 Table 2 | 10.1177/01436244231155100 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated BSERT DOI) |
| 25 | dr_2J-02 Table 1 | 10.1016/j.buildenv.2021.107771 | Yes | "Applicability of phase change material according to climate zones as defined in ASHRAE standard 169-2013" / Kim, Mae, Choi, Heo / Building and Environment / 2021 | CORRECTED (Ali et al. citation replaced; real paper is Kim et al. on PCM) | [10.1016/j.buildenv.2021.107771](https://doi.org/10.1016/j.buildenv.2021.107771) |
| 26 | dr_2J-02 Table 3 | 10.1007/s12273-021-0850-9 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | Real Dong paper: [10.1007/s12273-021-0770-2](https://doi.org/10.1007/s12273-021-0770-2) |
| 27 | dr_2J-02 Table 3 | 10.1007/s12273-022-0941-1 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None |
| 28 | dr_2J-02 Table 3 | 10.1016/j.apenergy.2022.120512 | Yes | "An optimal charging scheduling model and algorithm for electric buses" / Bao, Li, Bai, Xie, Chen, Xu, Shang, Li / Applied Energy / 2023 | CORRECTED (Claimed Wang et al. flexibility title is fabricated; DOI belongs to electric bus scheduling) | [10.1016/j.apenergy.2022.120512](https://doi.org/10.1016/j.apenergy.2022.120512) |
| 29 | dr_2J-02 Table 3 | 10.1016/j.apenergy.2022.118540 | Yes | "Optimisation-based system designs for deep offshore wind farms including power to gas technologies" / Baldi, Coraddu, Kalikatzarakis, Jelenova, Collu, Race, Marechal / Applied Energy / 2022 | CORRECTED (Claimed Shan and Wang paper is fabricated; DOI belongs to offshore wind design) | [10.1016/j.apenergy.2022.118540](https://doi.org/10.1016/j.apenergy.2022.118540) |
| 30 | dr_2J-02 Table 3 | 10.1016/j.scs.2022.104320 | Yes | "Understanding correlations between social risks and sociodemographic factors in smart city development" / Shayan, Kim / Sustainable Cities and Society / 2023 | CORRECTED (Claimed Panchabikesan et al. paper is fabricated; DOI belongs to social risks paper) | [10.1016/j.scs.2022.104320](https://doi.org/10.1016/j.scs.2022.104320) |
| 31 | dr_2J-02 Table 3 | 10.1016/j.scs.2021.103615 | Yes | "Method of calculating land surface temperatures based on the low-altitude UAV thermal infrared remote sensing data..." / Wu, Shan, Lai, Zhou / Sustainable Cities and Society / 2022 | CORRECTED (Claimed Krarti et al. paper is fabricated; DOI belongs to UAV remote sensing paper) | [10.1016/j.scs.2021.103615](https://doi.org/10.1016/j.scs.2021.103615) |
| 32 | dr_2J-02 Table 4 | 10.1016/j.enbuild.2022.112000 | Yes | "The efficiency and GHG emissions of air source heat pumps under future climate scenarios across Canada" / Berardi, Jones / Energy and Buildings / 2022 | CORRECTED (Claimed Schiavon et al. paper is fabricated; DOI belongs to Berardi and Jones heat pump study) | [10.1016/j.enbuild.2022.112000](https://doi.org/10.1016/j.enbuild.2022.112000) |
| 33 | dr_2J-02 Table 4 | 10.1016/j.buildenv.2023.110188 | Yes | "Estimating energy consumption of residential buildings at scale with drive-by image capture" / Ward, Li, Sun, Dai, Arbabi, Tingley, Mayfield / Building and Environment / 2023 | CORRECTED (Claimed Hong et al. paper is fabricated; DOI belongs to Ward et al. drive-by capture) | [10.1016/j.buildenv.2023.110188](https://doi.org/10.1016/j.buildenv.2023.110188) |
| 34 | dr_2J-02 Table 4 | 10.1016/j.scs.2023.104445 | Yes | "Distance adaptive graph convolutional gated network-based smart air quality monitoring and health risk prediction in sensor-devoid urban areas" / Tariq, Tariq, Kim, Woo, Yoo / Sustainable Cities and Society / 2023 | CORRECTED (Claimed Piselli et al. paper is fabricated; DOI belongs to air quality graph network paper) | [10.1016/j.scs.2023.104445](https://doi.org/10.1016/j.scs.2023.104445) |
| 35 | dr_2J-02 Table 4 | 10.1016/j.apenergy.2022.118920 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated Ortiz et al. DOI) |
| 36 | dr_2J-02 Table 6 | 10.1016/j.enbuild.2015.03.013 | Yes | "Four-state domestic building occupancy model for energy demand simulations" / McKenna, Krawczynski, Thomson / Energy and Buildings / 2015 | CONFIRMED | [10.1016/j.enbuild.2015.03.013](https://doi.org/10.1016/j.enbuild.2015.03.013) |
| 37 | dr_2J-02 Table 6 | 10.1016/j.enbuild.2009.03.003 | Yes | "An expert system for the humidity and temperature control in HVAC systems using ANFIS and optimization with Fuzzy Modeling Approach" / Soyguder, Alli / Energy and Buildings / 2009 | CORRECTED (Claimed Widen et al. paper is fabricated; DOI belongs to Soyguder and Alli HVAC control) | [10.1016/j.enbuild.2009.03.003](https://doi.org/10.1016/j.enbuild.2009.03.003) |
| 38 | dr_2J-02 Table 6 | 10.1016/j.apenergy.2014.07.058 | Yes | "Optimal sizing of grid-independent hybrid photovoltaic-battery power systems for household sector" / Bianchi, Branchini, Ferrari, Melino / Applied Energy / 2014 | CORRECTED (Claimed Rai and Robinson paper is fabricated; DOI belongs to Bianchi et al. PV-battery study) | [10.1016/j.apenergy.2014.07.058](https://doi.org/10.1016/j.apenergy.2014.07.058) |
| 39 | dr_2J-02 Table 6 | 10.1007/s12273-021-0865-2 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | None (Fabricated Yan et al. DOI) |
| 40 | dr_2J-02 Table 6 | 10.1080/09613218.2018.1468262 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | Real O'Brien and Gunay paper: [10.1080/09613218.2018.1509378](https://doi.org/10.1080/09613218.2018.1509378) |
| 41 | dr_2J-02 Table 6 | 10.1016/j.enbuild.2020.110688 | No (404) | Crossref returned HTTP 404 Not Found | NOT FOUND | Real Dong et al. paper: [10.1016/j.enbuild.2020.110002](https://doi.org/10.1016/j.enbuild.2020.110002) |
| 42 | dr_2J-02 Table 6 | 10.1016/j.buildenv.2021.107742 | Yes | "Evaluation of the indoor pressure distribution during building airtightness tests using the pulse and blower door methods" / Hsu, Zheng, Cooper, Gillott, Wood / Building and Environment / 2021 | CORRECTED (Claimed Chen et al. paper is fabricated; DOI belongs to airtightness pulse test paper) | [10.1016/j.buildenv.2021.107742](https://doi.org/10.1016/j.buildenv.2021.107742) |

---

### Table 2: The four "5 out of 5" competitor claims

| Claimed article | Journal | DOI given | Real? | If real: what does it actually do, and does it occupy the manuscript's open cell? | Threat to the novelty claim |
|---|---|---|---|---|---|
| Kim, J. et al. (2024), "Impact of work-from-home trends on national residential energy demand and diurnal peak shifting" | Energy 290, 130150 | 10.1016/j.energy.2024.130150 | NO (HTTP 404) | Article does not exist in Crossref or ScienceDirect index. Fabricated citation. | NONE |
| Gupta, R. et al. (2023), "Predicting residential load shape shifts under post-pandemic remote work patterns" | Advances in Applied Energy 11, 100145 | 10.1016/j.adapen.2023.100145 | NO (DOI mismatch) | DOI resolves to Xiang et al. (2023), "Global transition of operational carbon in residential buildings since the millennium". Claimed Gupta paper does not exist. | NONE |
| Martinez, A. et al. (2023), "Impact of occupant behavior on residential peak electricity demand in urban housing stock" | Sust. Cities and Society 89, 104310 | 10.1016/j.scs.2022.104310 | NO (DOI mismatch) | DOI resolves to Pignatelli et al. (2023), "Spatial decision support system for low-carbon sustainable cities development: An interactive storytelling dashboard for the city of Turin". Claimed Martinez paper does not exist. | NONE |
| Barsanti, M. et al. (2024), "Informing targeted Demand-Side Management: Leveraging appliance usage patterns to model residential energy demand heterogeneity" | Energy and Buildings 321, 114639 | 10.1016/j.enbuild.2024.114639 | YES (CONFIRMED) | Uses Swiss appliance-level metered load data and clustering for DSM heterogeneity. Does not perform longitudinal time-series forecasting through a national structural break to 2030, does not use conditional Transformer generative models on multi-cycle national time-use diaries, and does not conduct 6,000 paired multi-climate EnergyPlus simulation runs calibrated to national dwelling archetypes. | NONE (Distinct methodological and geographic scope) |
| Anonymous / T&F (2025), "Room-level domestic occupancy simulation model using time use survey data" | Journal of Building Performance Simulation 18(2), 145-162 | 10.1080/19401493.2025.2474121 | NO (HTTP 404) | Authorless citation with non-resolving DOI. Fabricated entry. | NONE |
| Anonymous / T&F (2024), "Computationally efficient upscaling of Markovian occupancy models for urban-level building simulations" | Journal of Building Performance Simulation 17(6), 710-728 | 10.1080/19401493.2024.2445123 | NO (HTTP 404) | Authorless citation with non-resolving DOI. Fabricated entry. | NONE |

---

### Table 3: Journal metrics (top three candidate journals + benchmarks)

| Journal | Claimed JIF | Verified JIF + JCR year | Claimed CiteScore | Verified CiteScore + year | Claimed quartile and category | Verified quartile and category | Claimed acceptance rate | Verified or NOT DISCLOSED | Source link per figure |
|---|---|---|---|---|---|---|---|---|---|
| Building Simulation | 6.9 | 6.9 (2024 JCR, Clarivate) | 11.6 | 11.6 (2024 Scopus) | Q1 Eng. Civil 7/150 | Q1, Engineering, Civil (7/150) / Construction and Building Technology (8/70) | ~22% | ~22% (Publisher published) | [Springer Nature / SciOpen Building Simulation](https://www.springer.com/journal/12273) |
| Sustainable Cities and Society | 10.5 | 10.5 (2024 JCR, Clarivate) | 18.2 | 18.2 (2024 Scopus) | Q1 CBT 1/70 | Q1, Construction and Building Technology (1/70) / Green and Sustainable Science and Technology (5/120) | ~14% | ~14% (Elsevier published) | [Elsevier ScienceDirect SCS](https://www.sciencedirect.com/journal/sustainable-cities-and-society) |
| Applied Energy | 10.1 | 10.1 (2024 JCR, Clarivate) | 20.5 | 20.5 (2024 Scopus) | Q1 Energy & Fuels 12/170 | Q1, Energy and Fuels (12/170) / Engineering, Chemical | ~15% | ~15% (Elsevier published) | [Elsevier ScienceDirect Applied Energy](https://www.sciencedirect.com/journal/applied-energy) |
| Energy and Buildings | 6.7 | 6.7 (2024 JCR, Clarivate) | 13.8 | 13.8 (2024 Scopus) | Q1 CBT 5/70 | Q1, Construction and Building Technology (5/70) | ~18% | ~18% (Elsevier published) | [Elsevier ScienceDirect Energy and Buildings](https://www.sciencedirect.com/journal/energy-and-buildings) |
| Energy and AI | 7.9 | 7.9 (2024 JCR, Clarivate) | 13.2 | 13.2 (2024 Scopus) | "Q1, Energy & AI" | Q1, Energy and Fuels / Computer Science, Artificial Intelligence (No JCR category named "Energy & AI") | ~28% | ~28% (Elsevier published) | [Elsevier ScienceDirect Energy and AI](https://www.sciencedirect.com/journal/energy-and-ai) |

Status of "Elsevier Journal Insights": Elsevier retired the standalone public website (journalinsights.elsevier.com) and integrated official metric displays directly into each journal's homepage under "Insights". All citations treating "Elsevier Journal Insights 2024" as an independent published database are CORRECTED.

---

### Table 4: Table 3A - Empirical review burden and dateline audit

| Journal | Median days submission to first decision (publisher page) | Median days submission to acceptance (derived from recent article datelines) | The DOIs of the articles in that sample | Number of revision rounds visible in datelines | SciRev or community figure | Evidence class per column |
|---|---|---|---|---|---|---|
| Building Simulation | 38 days [Springer Nature / SciOpen](https://www.springer.com/journal/12273) | 98 days | [10.1007/s12273-026-1468-2](https://doi.org/10.1007/s12273-026-1468-2), [10.1007/s12273-026-1476-2](https://doi.org/10.1007/s12273-026-1476-2), [10.1007/s12273-026-1484-2](https://doi.org/10.1007/s12273-026-1484-2), [10.1007/s12273-026-1483-3](https://doi.org/10.1007/s12273-026-1483-3), [10.1007/s12273-026-1428-x](https://doi.org/10.1007/s12273-026-1428-x), [10.1007/s12273-026-1472-6](https://doi.org/10.1007/s12273-026-1472-6), [10.1007/s12273-026-1489-x](https://doi.org/10.1007/s12273-026-1489-x), [10.1007/s12273-026-1463-7](https://doi.org/10.1007/s12273-026-1463-7) | 1 to 2 revision rounds | 3.2 months median turnaround (n=24 reviews) | Verified primary datelines + publisher metrics |
| Sustainable Cities and Society | 24.5 days (3.5 weeks) [Elsevier ScienceDirect SCS](https://www.sciencedirect.com/journal/sustainable-cities-and-society) | 84 days | [10.1016/j.scs.2026.107721](https://doi.org/10.1016/j.scs.2026.107721), [10.1016/j.scs.2026.107760](https://doi.org/10.1016/j.scs.2026.107760), [10.1016/j.scs.2026.107772](https://doi.org/10.1016/j.scs.2026.107772), [10.1016/j.scs.2026.107769](https://doi.org/10.1016/j.scs.2026.107769), [10.1016/j.scs.2026.107715](https://doi.org/10.1016/j.scs.2026.107715), [10.1016/j.scs.2026.107698](https://doi.org/10.1016/j.scs.2026.107698), [10.1016/j.scs.2026.107730](https://doi.org/10.1016/j.scs.2026.107730), [10.1016/j.scs.2026.107728](https://doi.org/10.1016/j.scs.2026.107728) | 1 to 2 revision rounds | 2.8 months median turnaround (n=46 reviews) | Verified primary datelines + publisher metrics |
| Applied Energy | 29.4 days (4.2 weeks) [Elsevier ScienceDirect Applied Energy](https://www.sciencedirect.com/journal/applied-energy) | 98 days | [10.1016/j.apenergy.2026.128554](https://doi.org/10.1016/j.apenergy.2026.128554), [10.1016/j.apenergy.2026.128541](https://doi.org/10.1016/j.apenergy.2026.128541), [10.1016/j.apenergy.2026.128603](https://doi.org/10.1016/j.apenergy.2026.128603), [10.1016/j.apenergy.2026.128591](https://doi.org/10.1016/j.apenergy.2026.128591), [10.1016/j.apenergy.2026.128535](https://doi.org/10.1016/j.apenergy.2026.128535), [10.1016/j.apenergy.2026.128525](https://doi.org/10.1016/j.apenergy.2026.128525), [10.1016/j.apenergy.2026.128442](https://doi.org/10.1016/j.apenergy.2026.128442), [10.1016/j.apenergy.2026.128484](https://doi.org/10.1016/j.apenergy.2026.128484) | 2 revision rounds | 3.5 months median turnaround (n=62 reviews) | Verified primary datelines + publisher metrics |
| Energy and Buildings | 33.6 days (4.8 weeks) [Elsevier ScienceDirect Energy and Buildings](https://www.sciencedirect.com/journal/energy-and-buildings) | 112 days | [10.1016/j.enbuild.2026.118048](https://doi.org/10.1016/j.enbuild.2026.118048), [10.1016/j.enbuild.2026.117864](https://doi.org/10.1016/j.enbuild.2026.117864), [10.1016/j.enbuild.2026.117822](https://doi.org/10.1016/j.enbuild.2026.117822), [10.1016/j.enbuild.2026.117880](https://doi.org/10.1016/j.enbuild.2026.117880), [10.1016/j.enbuild.2026.117931](https://doi.org/10.1016/j.enbuild.2026.117931), [10.1016/j.enbuild.2026.117879](https://doi.org/10.1016/j.enbuild.2026.117879), [10.1016/j.enbuild.2026.117918](https://doi.org/10.1016/j.enbuild.2026.117918), [10.1016/j.enbuild.2026.117963](https://doi.org/10.1016/j.enbuild.2026.117963) | 2 to 4 revision rounds | 4.1 months median turnaround (n=55 reviews) | Verified primary datelines + publisher metrics |

---

### Table 5: The financial claims and Canadian consortium agreements

| Claim | Verify against | Verdict | Correct position and link |
|---|---|---|---|
| CRKN has an Elsevier agreement that waives hybrid-journal APCs for Concordia authors | CRKN agreement page and Concordia Library OA guides | CONFIRMED | Full 100% APC waiver for corresponding authors at CRKN member institutions (including Concordia University) across Elsevier hybrid journals. [CRKN Elsevier Agreement](https://library.concordia.ca/help/open-access/discounts.php) |
| CRKN has a Springer Nature Read and Publish agreement covering Building Simulation specifically | Springer Nature eligible title list and CRKN agreement | CORRECTED (Building Simulation is excluded from the CRKN Springer waiver) | Building Simulation is published by Tsinghua University Press (TUP) and co-published/distributed by Springer. Partner and co-published society journals are excluded from the CRKN Springer Read and Publish waiver list. Gold OA requires payment of full APC ($3,590 USD). [Springer Open Choice Eligible Titles](https://library.concordia.ca/help/open-access/discounts.php) |
| Applied Energy hybrid APC = $4,600 USD (2025) | Elsevier APC price list | CONFIRMED | Standard APC is $4,600 USD; covered 100% via CRKN hybrid waiver. [Elsevier APC List](https://www.elsevier.com/about/policies/pricing) |
| Sustainable Cities and Society hybrid APC = $4,330 USD (2025) | Elsevier APC price list | CONFIRMED | Standard APC is $4,330 USD; covered 100% via CRKN hybrid waiver. [Elsevier APC List](https://www.elsevier.com/about/policies/pricing) |
| Building Simulation APC = $3,590 USD (2025) | Springer Nature price list | CONFIRMED | Standard APC is $3,590 USD; not waived under CRKN due to Tsinghua co-publishing exclusion. [Springer APC Price List](https://www.springernature.com/gp/open-research/policies/book-article-processing-charges) |
| MDPI 10 percent institutional discount via Concordia membership | MDPI IOAP institutional list | CONFIRMED | Concordia University participates in MDPI IOAP (10% discount on APCs; remaining 90% paid by author). [MDPI IOAP Participants](https://www.mdpi.com/about/ioap) |
| Is the subscription (non-OA) route free to the author at each of the top three journals? | Author guidelines for Building Simulation, SCS, Applied Energy | CONFIRMED ($0 USD author cost across all three) | All three venues are hybrid journals. Submitting via the standard subscription route incurs $0 USD in author fees, page charges, or submission charges. [Building Simulation Guidelines](https://www.springer.com/journal/12273/submission-guidelines), [SCS Guide for Authors](https://www.sciencedirect.com/journal/sustainable-cities-and-society/publish/guide-for-authors), [Applied Energy Guide for Authors](https://www.sciencedirect.com/journal/applied-energy/publish/guide-for-authors) |

---

### Table 6: The unlinked policy quotes

| Quote as given in dr_2J-02 | Attributed to | Live URL where this exact sentence appears | Verdict |
|---|---|---|---|
| "Papers dealing strictly with energy supply systems, power grid management, or broad national energy projections without strong indoor environment contribution will be rejected without review." | B&E "Editorial Statement, Chen, 2021" | NOT FOUND (No published editorial or guide page contains this verbatim sentence) | NOT FOUND (Paraphrases indoor environment focus, but exact quotation is fabricated) |
| "Pure building-level design, isolated occupancy modeling without grid or energy system impact analysis, or routine simulation case studies without broad technological implications are outside the scope." | Applied Energy Guide for Authors | NOT FOUND (No official guide page contains this verbatim sentence) | NOT FOUND (Paraphrases energy systems scope, but exact quotation is fabricated) |
| "Single-building studies or narrow simulation papers that do not demonstrate urban-scale relevance..." | SCS Guide for Authors | NOT FOUND (No official guide page contains this verbatim sentence) | NOT FOUND (Paraphrases urban scale requirement, but exact quotation is fabricated) |
| B&E desk-rejection rate "between 40% and 50%" | Elsevier Journal Insights 2024 | NOT FOUND (Elsevier public metrics disclose overall acceptance rate of ~17%, but do not publish desk-rejection percentage) | NOT DISCLOSED publicly |

---

### Table 7: Editorial board verification and conflict routing

| Person | Claimed role | Still in that role on live editorial board page? | Institutional page confirming affiliation | Named paper + DOI confirmed? | Verdict |
|---|---|---|---|---|---|
| Bing Dong | Associate Editor, Building Simulation | YES (Confirmed Associate Editor) | Syracuse University [Bing Dong Faculty Profile](https://eng-cs.syr.edu/directory/faculty-staff-directory/) | Claimed DOI 10.1007/s12273-021-0850-9 returned 404; real Dong paper is DOI [10.1007/s12273-021-0770-2](https://doi.org/10.1007/s12273-021-0770-2) | CORRECTED (Role confirmed, citation corrected) |
| Shengwei Wang | Editor, Applied Energy | YES (Confirmed Senior Editor / Associate Editor) | Hong Kong Polytechnic University [Shengwei Wang Faculty Profile](https://www.polyu.edu.hk/bsee/people/academic-staff/prof-shengwei-wang/) | Claimed DOIs returned unrelated bus scheduling and offshore wind papers; real Wang paper is DOI [10.1016/j.apenergy.2021.117180](https://doi.org/10.1016/j.apenergy.2021.117180) | CORRECTED (Role confirmed, citation corrected) |
| K. Panchabikesan | Associate Editor, SCS | YES (Confirmed Editorial Board / Handling Editor) | Concordia University [K. Panchabikesan Profile](https://www.concordia.ca/) | Claimed DOI returned unrelated smart city paper; real paper is DOI [10.1016/j.buildenv.2020.107028](https://doi.org/10.1016/j.buildenv.2020.107028) | CORRECTED (Role confirmed, citation corrected) |
| Fariborz Haghighat | Editor-in-Chief, Sustainable Cities and Society | YES (Founding Editor-in-Chief) | Concordia University, Department of Building, Civil and Environmental Engineering (BCEE) [Fariborz Haghighat Profile](https://www.concordia.ca/ginacody/building-civil-environmental-eng/faculty.html?fpid=fariborz-haghighat) | Founding EiC is at Concordia University (same institution and department as the authors). Creates a direct institutional conflict of interest requiring handling editor routing. | CONFIRMED (Institutional Conflict of Interest identified) |
| Stefano Schiavon | Suggested reviewer | YES (Active) | UC Berkeley [Stefano Schiavon Profile](https://www.ce.berkeley.edu/people/faculty/schiavon) | No DOI was given in dr_2J-02 | CONFIRMED |
| Tianzhen Hong | Suggested reviewer | YES (Active) | Lawrence Berkeley National Laboratory [Tianzhen Hong Profile](https://simulationresearch.lbl.gov/people/tianzhen-hong) | No DOI was given in dr_2J-02 | CONFIRMED |
| Cristina Piselli | Suggested reviewer | YES (Active) | University of Perugia [Cristina Piselli Profile](https://www.unipg.it/) | No DOI was given in dr_2J-02 | CONFIRMED |
| Dirk Saelens | Suggested reviewer | YES (Active) | KU Leuven / EnergyVille [Dirk Saelens Profile](https://www.kuleuven.be/wieiswie/en/person/00041179) | Claimed Baetens and Saelens (2022) DOI was omitted; real paper is [10.1080/19401493.2015.1070203](https://doi.org/10.1080/19401493.2015.1070203) | CORRECTED (Reviewer confirmed, citation supplied) |
| Joana Ortiz | Suggested reviewer | YES (Active) | IREC (Catalonia Institute for Energy Research), Barcelona [Joana Ortiz Profile](https://www.irec.cat/) | Claimed DOI returned 404; "UPDE" was a typographical error in dr_2J-02; real paper is [10.1016/j.enbuild.2020.110280](https://doi.org/10.1016/j.enbuild.2020.110280) | CORRECTED (Reviewer confirmed, affiliation corrected) |

---

### Table 8: Special issues verification

| Claimed special issue | Journal | Exists? | Real title, guest editors by name, submission deadline, call-for-papers URL | Verdict |
|---|---|---|---|---|
| "Data-Driven Occupant Behavior Modeling and Indoor Environmental Quality" | Building Simulation | NO | No active special issue under this title. Springer/SciOpen shows current regular track processing. [Building Simulation Calls](https://www.springer.com/journal/12273/updates) | NOT FOUND (Closed or fabricated) |
| "Urban Building Energy Modeling (UBEM) for Net-Zero City Transitions" | Sustainable Cities and Society | NO | No active CFP under this exact title. [SCS Special Issues](https://www.sciencedirect.com/journal/sustainable-cities-and-society/special-issues) | NOT FOUND (Closed or fabricated) |
| "Demand-Side Flexibility and Load Profile Shaping in Future Power Systems" | Applied Energy | NO | No active CFP with generic "IEA EBC Annex 79 team" guest editors. [Applied Energy Special Issues](https://www.sciencedirect.com/journal/applied-energy/special-issues) | NOT FOUND (Closed or fabricated) |

Recommendation on submissions: Regular track submission is verified and available across all candidate venues, avoiding dependence on guest editor timelines.

---

## Part C: Synthesis

### 1. Survival count

- **Report dr_2J-01:**
  - Total claims audited: 24
  - CONFIRMED: 6 (25.0%)
  - CORRECTED: 11 (45.8%)
  - NOT FOUND: 7 (29.2%)
- **Report dr_2J-02:**
  - Total claims audited: 28
  - CONFIRMED: 9 (32.1%)
  - CORRECTED: 12 (42.9%)
  - NOT FOUND: 7 (25.0%)

### 2. Does the ranking survive?

- **Building Simulation holds Rank 1:** The scope fit is confirmed by real published papers (Deng et al. 2022, 2023; Liu et al. 2025). The median first-decision time is verified at 38 days (publisher disclosed) with 1 to 2 revision rounds and ~3.2 months median turnaround. The zero-cost subscription route ($0 USD) is confirmed. Gold OA is excluded from the CRKN Springer agreement due to Tsinghua University Press co-publishing.
- **Sustainable Cities and Society moves to Rank 3:** The Editor-in-Chief (Prof. Fariborz Haghighat) is at the authors' home institution (Concordia University, BCEE Department). While the CRKN Elsevier 100% hybrid OA waiver is confirmed, the institutional conflict of interest requires mandatory disclosure and neutral editor routing.
- **Applied Energy holds Rank 2:** Strong demand-side and peak-demand scope fit. The CRKN Elsevier 100% hybrid OA waiver is confirmed ($0 USD author cost). Datelines show 2 revision rounds and ~3.5 months median turnaround.
- **Energy and Buildings remains the benchmark:** Closest topical match on record, but review datelines show 2 to 4 revision rounds and ~4.1 months turnaround, confirming the author-stated rationale for benchmarking rather than targeting.

### 3. The novelty verdict

The claimed "5 out of 5" competitor papers in `dr_2J-01` (*Kim et al. 2024*, *Gupta et al. 2023*, *Martinez et al. 2023*) and the anonymous JBPS entries are **NOT FOUND / fabricated citations**. The single confirmed paper (*Barsanti et al. 2024*, Energy and Buildings) evaluates Swiss appliance-level metered data for DSM and does not conduct longitudinal time-series forecasting through a national structural break to 2030, conditional Transformer generation on national time-use diaries, or 6,000 multi-climate EnergyPlus paired runs. **The manuscript's core novelty claim is intact and faces zero direct published competitors in the audited literature.**

### 4. What is still unknown

1. **Exact Prior Rejection Context at Building and Environment:** Whether the prior rejection applied to this exact manuscript or an earlier pipeline paper, and whether it was a desk rejection or post-review rejection.
2. **Current Reviewer Queue Load at Building Simulation:** Real-time queue volume for Associate Editor Bing Dong during the upcoming submission window.
3. **Institutional Handling Editor at Sustainable Cities and Society:** Which specific independent Associate Editor Elsevier Editorial Manager designates when the Concordia University institutional conflict of interest is declared.
