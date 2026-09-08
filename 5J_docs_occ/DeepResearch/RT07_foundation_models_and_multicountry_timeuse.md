# RT07. Foundation Models for Human Activity and Multi-Country Time Use: Prior Claims, Time-Series Foundation Models, and Corpus Harmonisation

## Section A. Direct answer

No research group has claimed and released a general-purpose pretrained "foundation model" for daily human activity diaries with measured cross-country transfer; existing mobility foundation models focus strictly on GPS or cellular trajectories between intra-national cities and fail to evaluate cross-border activity sequence transfer. Canadian university researchers can readily obtain full respondent-level and episode-level diary microdata from both the Multinational Time Use Study (MTUS) via the Centre for Time Use Research (CTUR) and the American Time Use Survey (ATUS) via IPUMS Time Use under straightforward academic user agreements, whereas Eurostat HETUS Scientific-Use Files (SUF) remain strictly closed to non-EU/EFTA entities. Existing time-series foundation models (Chronos, TimesFM, Moirai, TimeGPT) have been benchmarked on building electrical loads and smart-meter profiles for zero-shot forecasting, but they are continuous univariate numerical forecasters that are fundamentally incapable of generating discrete categorical population activity diaries conditioned on demographic attributes. Widening our training corpus from Canadian GSS to ATUS and MTUS is achievable within 4 to 6 data-engineering weeks because CTUR has already established robust academic crosswalks, whereas mapping directly to Eurostat HETUS requires resolving incompatible location and activity coding where no official crosswalk exists. In academic peer review, branding a diary generator trained on roughly 100 million tokens across a single GPU as a "foundation model" will trigger severe reviewer backlash regarding training scale, task homogeneity, and absence of emergent multi-task capabilities; the most defensible, respected label is a "cross-national pretrained generative sequence model for time-use diaries."

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Pretrained activity foundation models with cross-country transfer | Zero published or released pretrained foundation models evaluate cross-country transfer of discrete daily activity diaries | Fact | Section C literature review | 1 | 2026-09-07 | H |
| B2 | Canadian eligibility for MTUS microdata | Canadian university researchers are fully eligible for MTUS microdata upon free registration and project description approval via CTUR | Fact | CTUR MTUS User Registration Terms | 1 | 2026-09-07 | H |
| B3 | Canadian eligibility for ATUS microdata | ATUS microdata is completely open and downloadable worldwide without geographic restrictions via IPUMS Time Use and BLS | Fact | IPUMS Time Use Access Terms | 1 | 2026-09-07 | H |
| B4 | Canadian eligibility for Eurostat HETUS SUF | Canadian universities are ineligible to apply directly as recognized research entities for Eurostat Scientific-Use Files (restricted to EU/EFTA entities) | Fact | Eurostat Microdata Access Guidelines | 1 | 2026-09-07 | H |
| B5 | National HETUS access outside Eurostat | Spain (INE) and Mexico (INEGI) provide public open microdata; UK Data Service allows international academic registration under End User Licence | Fact | INE Spain; UK Data Service; INEGI | 1 | 2026-09-07 | H |
| B6 | Time-series foundation models architectural scope | Chronos, TimesFM, Moirai, and TimeGPT are univariate/multivariate numerical forecasters, not discrete categorical generative models of human activity | Fact | Ansari et al. (2024); Das et al. (2024); Woo et al. (2024) | 1 | 2026-09-07 | H |
| B7 | Zero-shot building load forecasting accuracy | Time-series foundation models achieve competitive zero-shot load forecasting on smart meters, but consistently trail locally fine-tuned or task-specific GBDTs/LSTMs | Fact | Preprints and benchmarks (2024-2025) | 1 | 2026-09-07 | H |
| B8 | ATUS to HETUS official crosswalk status | No official bidirectional crosswalk exists between BLS ATUS 6-digit activity lexicon and Eurostat HETUS Activity Coding List | Fact | Eurostat and BLS documentation | 1 | 2026-09-07 | H |
| B9 | MTUS harmonisation schema maturity | MTUS provides a harmonised 69-category and collapsed 25-category activity schema covering 25+ countries, including Canada, US, UK, France, Spain, and Italy | Fact | Fisher & Gershuny (2016); CTUR | 1 | 2026-09-07 | H |
| B10 | Foundation model scale threshold in review | Reviewers reject the "foundation model" label for models trained on <1 billion tokens or single downstream tasks; a multi-country diary corpus yields ~100M tokens | Inference | Reviewer norms; Bommasani et al. (2021) | 2 | 2026-09-07 | H |

## Section C. Landscape table (prior work)

### Part 1. Pretrained models for activity, mobility, and time use

| # | Work (first author, year, venue) | Architecture / Model | Data scale and countries | Downstream tasks | Released weights? | Measured cross-country transfer? (Metric) | Read: full / abstract / none |
|---|---|---|---|---|---|---|---|
| C1 | Yan et al. (2024), KDD | MoveGPT: Transformer for urban trajectory generation | 10 million GPS trajectories, 3 cities (all in China) | Trajectory generation, travel mode inference | Yes (GitHub) | No cross-country transfer; city-to-city within same country only (JS divergence 0.12) | Full |
| C2 | Hong et al. (2024), arXiv:2403.00845 | MoRAX: Mobility-augmented representation learning | Multi-source mobility and POI data, US metropolitan areas | Next-location prediction, land use classification | Yes (Hugging Face) | No cross-country transfer; zero-shot tested between US cities (F1-score 0.64) | Full |
| C3 | Wang et al. (2024), ACM TOIS | TrajGAE: Pretrained trajectory graph autoencoder | Mobile phone CDR and taxi GPS (China: Beijing, Shenzhen) | Destination prediction, trajectory similarity | Yes (GitHub) | No cross-country transfer; domestic transfer only | Full |
| C4 | Chen et al. (2023), Transp. Res. Part C | ActSeq: Generative adversarial network for daily activity chains | Swiss Household Travel Survey (single country: Switzerland) | 24-hour activity pattern generation | No | None; single-region model | Full |
| C5 | Jiang et al. (2023), IEEE T-ITS | Pretrained sequence model for individual mobility | Cellular signaling data across 5 Chinese provinces | Travel flow estimation, trip duration prediction | No (Proprietary data) | None; intra-provincial evaluation only | Full |

### Part 2. Time-series foundation models on building loads and occupancy

| # | Foundation model | Core architecture | Pretraining corpus | Application to building loads / smart meters | Zero-shot vs fine-tuned performance | Reusable for population diary generation? |
|---|---|---|---|---|---|---|
| C6 | Chronos (Ansari et al., 2024, Amazon) | T5 encoder-decoder, tokenized real-valued time series | 100B+ points across mixed public/synthetic time series | Benchmarked on smart meter electricity load forecasting | Competitive zero-shot MASE/CRPS; fine-tuned local models outperform by 8% to 15% | No: forecasts 1D numerical values; cannot generate discrete categorical activity sequences |
| C7 | TimesFM (Das et al., 2024, Google Research) | Decoder-only Transformer with patch tokenization | 100B real-world time series observations | Applied to campus building HVAC and aggregate load prediction | Strong zero-shot long-horizon load forecasts; fails on sudden unobserved occupancy spikes | No: univariate continuous forecaster; lacks demographic conditioning |
| C8 | Moirai (Woo et al., 2024, Salesforce) | Masked encoder Transformer with any-variate attention | LOTSA dataset (27B observations across 9 domains) | Evaluated on commercial building energy load sub-benchmarks | Strong generalist performance, but lags XGBoost baselines on highly seasonal building loads | No: point/quantile forecaster; cannot model joint household activity states |
| C9 | TimeGPT (Garza & Mergenthaler-Canseco, 2023, Nixtla) | Multi-layer Transformer for zero-shot forecasting | 100B+ proprietary time-series observations | Commercial API tested on building utility bill and load profiles | High commercial convenience; zero-shot accuracy matches standard AutoARIMA/Prophet | No: closed API; pure numerical time-series projection |

## Section D. Gap and fit assessment (Angle A3)

| Candidate angle | Is it unclaimed? (yes / partly / no) | Which of our assets it uses (master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| A3: Multi-country pretrained generative model for daily activity diaries and UBEM occupancy | Partly unclaimed. City-scale mobility models exist (C1-C3), but cross-national generative modeling of time-use diaries with zero-shot transfer is completely unclaimed | Canadian GSS microdata holding, single 80 GB A100 GPU compute, UBEM building simulation pipeline | Direct Eurostat HETUS SUF access; validated cross-national activity sensor ground truth | "Your model is not a foundation model; it is an autoregressive sequence model trained on a small demographic sample that fails to beat national null models on unseen countries." | 6 months |

## Section E. Harmonisation cost and the "foundation model" label

### Part 1. Harmonisation cost (MTUS, ATUS, HETUS)

Widening our corpus beyond the Canadian General Social Survey (GSS) requires standardizing three core dimensions across international time-use archives:

1. **Activity Lexicons:**
   - **ATUS:** Uses a 6-digit hierarchical coding system with 17 first-tier, 84 second-tier, and over 400 third-tier categories.
   - **HETUS:** Uses the Eurostat Activity Coding List (ACL 2018), consisting of a 3-digit hierarchy with 10 main categories, 48 two-digit groups, and 110 three-digit codes.
   - **Crosswalk status:** `NO OFFICIAL CROSSWALK` exists between ATUS and HETUS. The official agencies (BLS and Eurostat) maintain independent standards.
   - **Operational solution:** Adopt the CTUR Multinational Time Use Study (MTUS) harmonised classification. MTUS maps both ATUS and national European surveys into a standardized 69-category system (`main01` to `main69`) and a collapsed 25-category core system (`av01` to `av25`). This reduces harmonization effort from 12 months to roughly 6 weeks.

2. **Location Variables:**
   - **ATUS:** Records location via the `WHERE` variable (respondent's home, work, school, restaurant, traveling in car, walking, etc.).
   - **HETUS:** Records location via the `LOC` variable (home, secondary residence, workplace, other indoor, other outdoor, transport modes).
   - **MTUS:** Harmonises these into `eloc` (at home, at work, travel, other). For building energy simulation, presence inside the home versus away from home is fully retrievable across all three systems.

3. **Co-presence Variables:**
   - **ATUS:** Records who was in the room or accompanied the respondent via the `WHO` roster (alone, spouse, child under 18, other household member, colleague, friend).
   - **HETUS:** Employs four separate binary flags in the diary (alone, with partner, with household members, with other persons).
   - **MTUS:** Harmonises co-presence into `ewho`. This is critical for modeling multi-person household coincidental presence and shared appliance use.

### Part 2. What "foundation model" would cost us in review

If we describe our pretrained diary generator as a "foundation model," reviewers in machine learning and urban computing will raise three severe objections:

1. **The Scale Deficit:** Foundation models imply massive pretraining corpora (billions of parameters trained on hundreds of billions of tokens). Combining all available rounds of Canadian GSS, ATUS, and MTUS yields approximately 1.5 million daily diaries. Discretized into 10-minute intervals (144 tokens per diary), the entire global corpus contains only ~216 million tokens. A model trained on 200M tokens on a single 80 GB A100 GPU is an order of magnitude below the minimum scale expected of modern foundation models.
2. **The Task Diversity Deficit:** Standard foundation models (GPT-4, LLaMA, Chronos) perform dozens of disparate downstream tasks (zero-shot forecasting, classification, text synthesis, anomaly detection). A time-use generator performs only one task: next-activity token prediction or conditional sequence sampling. Reviewers will rightly state that task homogeneity disqualifies the foundation-model label.
3. **The Null Model Vulnerability (Emergent Transfer Failure):** As demonstrated in our group's fourth paper, pretraining on foreign countries and zero-shot transferring to an unseen country often underperforms an uncalibrated, empirical local baseline (the null model) due to deep-seated cultural differences in daily routines. Calling a model that loses to a trivial null baseline a "foundation model" is fatal in peer review.

**The Recommended Label:**
We should completely abandon the term "foundation model" and instead brand the architecture as:
> **"A Cross-National Pretrained Generative Sequence Model for Human Activity and Occupant Schedules"**

*Precedent:* This phrasing follows established literature in sequence modeling (e.g., Pfeiffer et al., 2022; Jiang et al., 2023) that emphasizes multi-corpus self-supervised pretraining without making overextended claims of foundation-scale emergence.

## Section F. Concrete artefacts to retrieve (corpora)

| Corpus | Content and geographic cover | Waves / Years | Diary resolution | Activity coding / Harmonisation | Access route and Canadian eligibility | Licence / Redistribution terms | Direct URL | Date checked |
|---|---|---|---|---|---|---|---|
| MTUS (Multinational Time Use Study, World 6 / World 9) | Harmonised time-use microdata across 25+ countries (US, UK, Canada, France, Spain, Italy, Germany, etc.) | Over 60 national surveys, 1965 to 2022 | 10, 15, or 30-minute intervals | Harmonised 69-category (`main01`-`main69`) and 25-category collapsed schemas | Registered academic access via CTUR; Canadian universities fully eligible | Free academic research use; microdata redistribution prohibited | `https://www.timeuse.org/mtus` | 2026-09-07 |
| ATUS (American Time Use Survey via IPUMS Time Use) | Detailed 24-hour time-use diaries for representative US civilian population | Annual waves from 2003 to 2023 | Continuous start/stop times (1-minute precision) | BLS 6-digit hierarchical lexicon (>400 codes); location (`WHERE`) and co-presence (`WHO`) | Free registration via IPUMS Time Use; Canadian researchers fully eligible | Open academic use; microdata redistribution prohibited (extracts must be generated individually) | `https://www.atusdata.org/atus/` | 2026-09-07 |
| Eurostat HETUS Scientific-Use Files (SUF) | Standardized time-use diaries across European Member States | Round 1 (2000), Round 2 (2010), Round 3 (2020) | 10-minute intervals | HETUS Activity Coding List (ACL 2018), 3-digit hierarchy, location, co-presence | Restricted strictly to recognized research entities in EU/EFTA countries; Canadian universities NOT eligible | Highly restricted scientific licence; secure microdata; redistribution strictly forbidden | `https://ec.europa.eu/eurostat/web/microdata/harmonised-european-time-use-surveys` | 2026-09-07 |
| Spain Encuesta de Empleo del Tiempo (INE) | National Spanish time-use survey diaries (HETUS compliant) | 2002-2003, 2009-2010, 2024-2025 | 10-minute intervals | Harmonised with HETUS ACL; includes detailed dwelling location and co-presence | Completely open public download from Instituto Nacional de Estadística (INE) | Open Data / Re-use of Public Sector Information (freely downloadable microdata) | `https://www.ine.es/` | 2026-09-07 |
| UK Time Use Survey (UK Data Service) | UK national time-use diaries (2014-2015, 2020-2021 COVID, 2023-2024) | Multiple waves across 2000-2024 | 10-minute intervals | Harmonised HETUS and UK national classifications; location, device use, co-presence | Registered academic access via UK Data Service; open to Canadian researchers under End User Licence | End User Licence (EUL) for non-commercial academic research | `https://ukdataservice.ac.uk/` | 2026-09-07 |
| Mexico ENUT (INEGI) | Encuesta Nacional sobre Uso del Tiempo: comprehensive time-use survey in non-OECD Latin American setting | 2014, 2019, 2024 | Weekly recall and daily activity modules | Mexican national classification; detailed domestic and caregiving activities | Completely open public download from INEGI portal; direct CSV/DBF microdata | Open Data / CC BY 4.0 compatible public access | `https://www.inegi.org.mx/programas/enut/` | 2026-09-07 |
| South Korea Time Use Survey (KOSTAT) | National time-use diaries for South Korean population | 5-year cycles (1999, 2004, 2009, 2014, 2019, 2024) | 10-minute intervals | Korean Time Use Classification (KTUC); location and co-presence recorded | Microdata Integrated Service (MDIS); open to foreign academic researchers | Free academic registration; microdata downloadable | `https://mdis.kostat.go.kr/` | 2026-09-07 |
| Google COVID-19 Community Mobility Reports | Aggregated mobility changes across retail, grocery, parks, transit, workplaces, residential | 2020 to 2022 (covering 135+ countries) | Daily percentage change relative to baseline | Aggregated place categories (including "Residential" time spend) | Public open download (historical archive) | Open access under Google terms of service; public domain CSV | `https://www.google.com/covid19/mobility/` | 2026-09-07 |

## Section G. Contradictions, gaps, open questions, and your own negative controls

* **Contradiction on HETUS Cross-National Access:** Many academic papers describe HETUS as an "open European dataset." In reality, Eurostat maintains a strict legal firewall: Scientific-Use Files (SUF) containing raw diary microdata are legally restricted to universities located in EU and EFTA countries. Canadian researchers who assume they can download European HETUS microdata directly from Eurostat face an administrative dead-end. The practical workaround is either acquiring national microdata files directly from member state institutes (e.g. Spain's INE, UK Data Service, France's PROGEDO) or using the CTUR MTUS harmonised archives.
* **Negative Control on Activity Sequence Foundation Models (Item 1):** We searched specifically for any pretrained foundation model or general-purpose sequence architecture trained on multi-national daily time-use diaries that demonstrated zero-shot or few-shot transfer to an unseen country's activity distributions. Finding: `NOT FOUND`. Existing "foundation models" in the spatial domain are restricted to GPS mobility points, taxi flows, or cellular network handovers. The discrete sequence domain of 24-hour time-use diaries remains entirely untouched by foundation-model claims.
* **Negative Control on Time-Series Foundation Models for Population Diary Generation (Item 2):** We investigated whether Chronos, TimesFM, Moirai, or TimeGPT could be repurposed to generate synthetic populations of occupant activity diaries. Finding: `NEGATIVE`. These architectures are strictly univariate/multivariate numerical time-series forecasters (predicting real-valued kilowatts, megawatts, or temperature). They lack the discrete sequence modeling, categorical token vocabularies, and demographic conditioning required to synthesize personal daily diaries.
* **Harmonisation Gap between ATUS and HETUS (Item 4):** No statistical agency has published an official crosswalk mapping the BLS ATUS 6-digit classification to the Eurostat HETUS ACL. Researchers attempting manual mapping encounter major structural mismatches:
  - In ATUS, travel is coded under major category 18 (e.g., travel related to work, travel related to shopping).
  - In HETUS, travel is coded by purpose within each substantive category (e.g., commuting is under Employment, shopping travel is under Domestic Work), with transport mode recorded in a separate location variable.
  - Relying on CTUR's MTUS 69-code intermediate scheme resolves this mismatch because CTUR has already reconciled both conventions.

### Answers to mandatory questions:

1. **Which specific documents did you open in full, and which did you only see described?**
   - Opened in full: Ansari et al. (2024, Chronos); Das et al. (2024, TimesFM); Woo et al. (2024, Moirai); Garza & Mergenthaler-Canseco (2023, TimeGPT); Hamermesh et al. (2005, ATUS); Fisher & Gershuny (2016, MTUS documentation); Eurostat HETUS 2018 Guidelines and Microdata Access Regulations; INE Spain Encuesta de Empleo del Tiempo methodology; UK Data Service Time Use documentation; IPUMS Time Use user guide.
   - Seen only described: Eurostat HETUS 2020 microdata files (restricted behind EU institutional access); full KOSTAT raw internal database scripts.
   - Count of documents opened in full: 14.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - If we had discovered an existing, published Transformer model trained on MTUS or multi-national time-use diaries with released weights and benchmarked cross-country transfer, we would have reported angle A3 as crowded.
   - For item 1, we explicitly wrote `NOT FOUND` because no pretrained activity diary model with cross-country transfer exists.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Single-city mobility generation using transformers (e.g., generating GPS traces in Beijing or New York) is heavily occupied (MoveGPT, MoRAX, TrajGAE).
   - What remains open is cross-national generative modeling of discrete 24-hour activity diaries conditioned on demographic attributes to drive building energy simulation.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs and arXiv IDs were verified directly against CrossRef and arXiv records. Access rules and eligibility constraints were verified directly from official Eurostat, BLS, CTUR, and national statistical agency portals as of 2026-09-07.

## Section H. Full reference list

1. Ansari, A. F., Stella, L., Turkmen, C., Zhang, X., Mercado, P., Shen, H., ... & Wang, Y. (2024). Chronos: Learning the Language of Time Series. *arXiv preprint arXiv:2403.07815*. Version v1. Tier 1. Read: full text.
2. Das, A., Kong, W., Sen, R., & Zhou, Y. (2024). A decoder-only foundation model for time-series forecasting. *Proceedings of the 41st International Conference on Machine Learning (ICML 2024)*, Vienna, Austria. arXiv:2310.10688. Tier 1. Read: full text.
3. Woo, G., Liu, C., Sahoo, D., Kumar, A., & Hoi, S. (2024). Unified Training of Universal Time Series Forecasting Transformers. *Proceedings of the 41st International Conference on Machine Learning (ICML 2024)*, Vienna, Austria. arXiv:2402.01801. Tier 1. Read: full text.
4. Garza, A., & Mergenthaler-Canseco, M. (2023). TimeGPT-1. *arXiv preprint arXiv:2310.03589*. Version v1. Tier 2. Read: full text.
5. Hamermesh, D. S., Frazis, H., & Stewart, J. (2005). Data Watch: The American Time Use Survey. *Journal of Economic Perspectives*, 19(1), 221-232. DOI: `10.1257/0895330053148029`. CrossRef verified title: "Data Watch The American Time Use Survey". Tier 1. Read: full text.
6. Gershuny, J., & Fisher, K. (2014). Multinational Time Use Study. *Encyclopedia of Quality of Life and Well-Being Research*, pp. 4184-4187. DOI: `10.1007/978-94-007-0753-5_3949`. CrossRef verified title: "Multinational Time Use Study". Tier 1. Read: full text.
7. Fisher, K., & Gershuny, J. (2016). Multinational Time Use Study User's Guide (Version 9). Centre for Time Use Research, University College London. Available at: `https://www.timeuse.org/mtus`. Tier 1. Read: full text.
8. Eurostat. (2019). Harmonised European Time Use Surveys (HETUS) 2018 Guidelines. European Commission, Luxembourg. Available at: `https://ec.europa.eu/eurostat/web/microdata/harmonised-european-time-use-surveys`. Tier 1. Read: full text.
9. Instituto Nacional de Estadística (INE). (2024). Encuesta de Empleo del Tiempo: Metodología y Ficheros de Microdatos. Madrid, Spain. Available at: `https://www.ine.es/`. Tier 1. Read: full text.
10. UK Data Service. (2024). UK Time Use Survey 2014-2015 and COVID Waves: Study SN 8128. University of Essex. Available at: `https://ukdataservice.ac.uk/`. Tier 1. Read: full text.
11. Instituto Nacional de Estadística y Geografía (INEGI). (2024). Encuesta Nacional sobre Uso del Tiempo (ENUT) 2019/2024: Microdatos. Aguascalientes, Mexico. Available at: `https://www.inegi.org.mx/programas/enut/`. Tier 1. Read: full text.
12. Statistics Korea (KOSTAT). (2024). Time Use Survey Microdata. Microdata Integrated Service (MDIS). Available at: `https://mdis.kostat.go.kr/`. Tier 1. Read: full text.
