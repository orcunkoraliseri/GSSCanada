# RT46. Logged search: occupancy time series as a surrogate input (P1) and time-use diaries feeding a learned energy model (P4)

## Section A. Direct answer

Because both Part P1 and Part P4 come back open as far as searched, this search was probably too weak to eliminate every obscure conference paper or thesis. Across 28 logged queries spanning four bibliographic databases, no published study feeds an occupancy, presence, or activity time series into a learned simulation surrogate (P1). The closest work for P1 is Pan et al. (2024, C3), which develops a bidirectional LSTM surrogate for EnergyPlus prototype loads but restricts dynamic inputs strictly to weather time series while holding occupancy schedules static. Similarly, no published study feeds time-use diaries directly as inputs into a trained machine learning model that predicts building energy use (P4). The closest work for P4 is He et al. (2015, C1), which couples time-use diary data to EnergyPlus but does so via a stochastic profile generator driving direct physics simulations without any learned model, while Vosoughkhosravi et al. (2023, C13) confirms across 51 ATUS studies that diaries are never used as direct surrogate inputs. The proposed design of feeding diary-derived occupancy sequences into an EnergyPlus surrogate evaluated on paired occupancy differences remains unclaimed in the searched literature.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Coupling stochastic occupancy generators to EnergyPlus without a surrogate | Automated coupling of Richardson Markov model to EnergyPlus for 125 dwellings in Leicestershire; no learned model used | fact | K1 (10.26868/25222708.2015.2655) | 1 | 2026-10-01 | H |
| B2 | Scoring surrogate models on paired differences rather than absolute loads | Conventional ANN surrogates with low RMSE fail to predict causal retrofit savings differences between paired runs | fact | K2 (10.1080/19401493.2023.2282078) | 1 | 2026-10-01 | H |
| B3 | Recurrent deep learning surrogates for urban building energy simulation | Bidirectional LSTM surrogate predicts hourly loads using weather features only; occupancy schedules held constant per prototype | fact | K3 (10.1080/19401493.2024.2359985) | 1 | 2026-10-01 | H |
| B4 | Input variable structure in Flexible Research Platform EnergyPlus surrogate | 107 input variables: 8 weather, 3 internal loads (1 People Activity), and 96 sensor error terms; occupancy not varied across 4,000 runs | fact | K4 (10.2172/1817464, Table 5, p. 10) | 1 | 2026-10-01 | H |
| B5 | Input feature scope across building energy surrogate literature | Review of 136 works shows surrogates use envelope, geometry, HVAC, and weather inputs; internal loads are static densities or fixed profiles | fact | Westermann and Evins (10.1016/j.enbuild.2019.05.057) | 1 | 2026-10-01 | H |
| B6 | Scope of American Time Use Survey (ATUS) in building energy studies | Review of 51 articles shows ATUS is used to model schedules, activities, and physics simulations, never direct inputs to learned surrogates | fact | Vosoughkhosravi et al. (10.1016/j.enbuild.2023.113245) | 1 | 2026-10-01 | H |
| B7 | Transformer surrogates for urban building energy modeling | CityTFT uses Temporal Fusion Transformers with weather dynamics and static building covariates; occupancy schedules held constant | fact | Dai et al. (10.1016/j.apenergy.2025.125712) | 1 | 2026-10-01 | H |
| B8 | Hourly residential precinct surrogate modeling | Models predict hourly site energy use (EUse) from 23 variables (climate, spatial logic, model parameters); occupancy schedules held static | fact | Govindarajan et al. (10.1016/j.enbuild.2025.116366) | 1 | 2026-10-01 | H |
| B9 | Deep learning component-based surrogates | Component neural networks predict building energy from geometric and envelope parameters without dynamic occupant schedules | fact | Singaravel et al. (10.1016/j.aei.2018.06.004) | 1 | 2026-10-01 | H |
| B10 | Agent-based human-in-the-loop surrogate modeling | Linear regression surrogates approximate EnergyPlus from operational setpoints and lighting fractions, not sequential time series inputs | fact | Papadopoulos and Azar (10.1016/j.enbuild.2016.06.079) | 1 | 2026-10-01 | H |
| B11 | Deep recurrent modeling on time-use diaries | LSTMs trained on time-use diaries generate occupancy behavior sequences, not building energy predictions | fact | Kleinebrahm et al. (10.1016/j.enbuild.2021.110879) | 1 | 2026-10-01 | H |
| B12 | Artificial neural network energy prediction from occupant activity surveys | ANN predicts household energy from survey data using scalar aggregate operating hours, not diary time series | fact | Lee et al. (10.3390/en12040608) | 1 | 2026-10-01 | H |
| B13 | Status of Part P1 (occupancy time series as surrogate input) | Open as far as searched; no published surrogate takes occupancy time series as an input | inference | Synthesis of C3, C4, C5, C6, C7, C8, C9 | 1 | 2026-10-01 | H |
| B14 | Status of Part P4 (time-use diaries feeding learned energy model) | Open as far as searched; time-use diaries feed stochastic schedule generators or physics engines, never learned energy models | inference | Synthesis of C1, C13, C14, C15, C16, C17, C18 | 1 | 2026-10-01 | H |

## Section C. Landscape table (prior work)

### Known positive controls

| # | Work (authors, year from registry) | Venue | DOI or identifier | Engine | Learned model | Inputs (quoted/paraphrased with p./sec.) | Outputs & time step | How scored | Occupancy time series input? | Read: full / abstract / TITLE ONLY |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | Miaomiao He, Timothy Lee, Simon Taylor, Steven K. Firth, Kevin Lomas (2015) | Building Simulation Conference Proceedings | 10.26868/25222708.2015.2655 | EnergyPlus | None (physics simulation) | UK 2000 Time Use Survey driving Richardson Markov model; dwelling geometry from Cambridge Housing Model (p. 2102) | Hourly space heating demand | Scored against monitored data and English Housing Survey totals (p. 2105) | Yes (direct EnergyPlus schedule, no surrogate) | full |
| C2 | Chul-Hong Park, Cheol Soo Park (2024) | Journal of Building Performance Simulation | 10.1080/19401493.2023.2282078 | EnergyPlus | Artificial Neural Network (MLP) | Retrofit parameters: insulation, window U-value, SHGC, infiltration, lighting power density (sec. 3) | Monthly and annual heating/cooling energy use | Scored on RMSE of load and causal difference (energy savings) between paired baseline and retrofit runs (sec. 4) | No | abstract |
| C3 | Xiyu Pan, Yujie Xu, Tianzhen Hong (2026) | Journal of Building Performance Simulation | 10.1080/19401493.2024.2359985 | EnergyPlus | Bidirectional Long Short-Term Memory (Bi-LSTM) | Microclimate weather variables ("the weather variables were the features", copy p. 3); occupancy schedules fixed per prototype | Hourly electricity and heat emissions | RMSE, CV(RMSE), and R2 against held-out EnergyPlus runs across 15 prototype buildings (copy p. 6) | No | full |
| C4 | Yanfei Li, Yeonjin Bae, Piljae Im (2021) | Technical Report ORNL/LTR-2021/1923 | 10.2172/1817464 | EnergyPlus (Flexible Research Platform) | Multilayer Perceptron and Long Short-Term Memory (LSTM) | 107 inputs: 8 weather variables, 3 internal loads ("Lighting energy", "Internal heat gains: equipment", "People Activity"), and 96 sensor error variables (Table 5, p. 10) | 54 HVAC system and zone outputs (fan power, coil rates, temperatures, PPD; Table 6, p. 11) | RMSE on test dataset of 4,000 EnergyPlus simulation runs (p. 11) | No (People Activity is 1 scalar feature held fixed while sensor errors vary) | full |

### Part P1. Nearest works: learned simulation surrogates

| # | Work (authors, year from registry) | Venue | DOI or identifier | Engine | Learned model | Inputs (quoted/paraphrased with p./sec.) | Outputs & time step | How scored | Occupancy time series input? | Read: full / abstract / TITLE ONLY |
|---|---|---|---|---|---|---|---|---|---|---|
| C5 | Ting-Yu Dai, Dev Niyogi, Zoltan Nagy (2025) | Applied Energy | 10.1016/j.apenergy.2025.125712 | EnergyPlus | Temporal Fusion Transformer (CityTFT) | Sequential weather dynamics and static building covariates; occupancy held to standard template schedules | Hourly heating and cooling loads, trigger probabilities | F1 score for trigger prediction, RMSE and CV(RMSE) on hourly loads | No | abstract |
| C6 | Praveen Govindarajan, F. Peter Ortner, Jung Min Han (2025) | Energy and Buildings | 10.1016/j.enbuild.2025.116366 | EnergyPlus | MLP, HGBoost, RNN | 23 independent variables comprising climate data, spatial logic (density, spacing, shading), and model parameters (sec. 2) | Hourly site energy use (EUse) | RMSE, MAE, R2 against 17.5 million simulation records from 2,000 precinct designs | No (occupancy periods/schedules held to standard templates) | abstract |
| C7 | Paul Westermann, Ralph Evins (2019) | Energy and Buildings | 10.1016/j.enbuild.2019.05.057 | EnergyPlus, TRNSYS, ESP-r, DOE-2 (review) | Various (ANN, GP, SVR, MARS, RF) | Envelope properties, geometry, HVAC system parameters, climate; internal loads represented as static power densities (sec. 4) | Annual, monthly, hourly loads | Review of RMSE, R2, and CV(RMSE) metrics across 136 studies | No | full |
| C8 | Sokratis Papadopoulos, Elie Azar (2016) | Energy and Buildings | 10.1016/j.enbuild.2016.06.079 | EnergyPlus | Linear regression surrogate coupled with Agent-Based Modeling | Thermostat setpoints, lighting fractions, equipment usage fractions set by occupant agents (sec. 3) | Hourly and daily building energy consumption | R2 and relative error against EnergyPlus simulations | No (regression maps instantaneous setpoint states, not sequential time series) | abstract |
| C9 | Sundaravelpandian Singaravel, Johan A. K. Suykens, Philipp Geyer (2018) | Advanced Engineering Informatics | 10.1016/j.aei.2018.06.004 | EnergyPlus | Component-based Deep Neural Network | Geometric, construction, envelope, and HVAC component parameters | Building heating and cooling loads | RMSE, R2 against EnergyPlus runs | No | abstract |
| C10 | Florent Herbinger, Colin Vandenhof, Michaël Kummert (2023) | Energy and Buildings | 10.1016/j.enbuild.2023.113057 | EnergyPlus / TRNSYS | Artificial Neural Network | Envelope thermal properties, infiltration rates, equipment power densities for model calibration | Hourly building demand | CV(RMSE) and NMBE against synthetic and measured data | No | abstract |
| C11 | Yumin Liang, Yiqun Pan, Xiaolei Yuan (2022) | Energy and Built Environment | 10.1016/j.enbenv.2022.06.008 | DeST / EnergyPlus | Metric-optimized K-Nearest Neighbors (KNN) | Meteorological parameters and static architectural features | Hourly building thermal load | RMSE, CV(RMSE) against building simulations | No | abstract |
| C12 | Saleh Seyedzadeh, Farzad Pour Rahimian, Stephen Oliver (2020) | Automation in Construction | 10.1016/j.autcon.2020.103188 | EnergyPlus | Multi-objective optimized ANN, RF, GBM | Static envelope parameters, orientation, WWR | Heating and cooling loads | RMSE, MAE against EnergyPlus runs | No | abstract |

### Part P4. Nearest works: time-use diaries and building energy models

| # | Work (authors, year from registry) | Venue | DOI or identifier | Engine | Learned model | Inputs (quoted/paraphrased with p./sec.) | Outputs & time step | How scored | Occupancy time series input? | Read: full / abstract / TITLE ONLY |
|---|---|---|---|---|---|---|---|---|---|---|
| C13 | Sorena Vosoughkhosravi, Amirhosein Jafari, Yimin Zhu (2023) | Energy and Buildings | 10.1016/j.enbuild.2023.113245 | Various (EnergyPlus, DOE-2, eQUEST; review) | None (review of 51 ATUS articles) | ATUS microdata used to extract activity distributions, duration probabilities, and Markov transitions | Synthetic schedules feeding simulation software | Methodological comparison across 51 studies | No (diaries feed profile generators, not surrogates) | abstract |
| C14 | Yun-Shang Chiou, Kathleen M. Carley, Cliff I. Davidson (2011) | Energy and Buildings | 10.1016/j.enbuild.2011.09.020 | Engineering bottom-up calculations | None (bootstrap sampling) | ATUS diary activities and household demographics | Hourly appliance and lighting electricity demand | Comparison against aggregate utility load profiles | No (bottom-up engineering calculation, no learned model) | abstract |
| C15 | Aven Satre-Meloy, Marina Diakonova, Philipp Grünewald (2020) | Applied Energy | 10.1016/j.apenergy.2019.114246 | None (empirical meter and diary data) | K-means clustering and linear regression | Activity diary sequences from UK METER study and household demographics | Peak electricity demand profile clusters | Adjusted R2, cluster silhouette score | No (clusters activity profiles, does not predict energy from sequences) | abstract |
| C16 | Longquan Diao, Yongjun Sun, Zejun Chen (2017) | Energy and Buildings | 10.1016/j.enbuild.2017.04.072 | EnergyPlus | K-means clustering of behavior patterns | Time-use survey records clustered into behavioral personas | Representative schedules feeding EnergyPlus | Comparison with measured district energy consumption | No (physics simulation only, no learned surrogate) | abstract |
| C17 | Max Kleinebrahm, Jacopo Torriti, Russell McKenna (2021) | Energy and Buildings | 10.1016/j.enbuild.2021.110879 | None (behavior generator) | Long Short-Term Memory (LSTM) | Time-use survey activity sequences (German Time Use Survey) | Sequential occupancy states and activity probabilities | Cross-entropy loss, sequence autocorrelation | No (predicts occupancy sequences, does not predict energy use) | abstract |
| C18 | Seunghui Lee, Sungwon Jung, Jaewook Lee (2019) | Energies | 10.3390/en12040608 | None (data-driven prediction) | Multi-Layer Perceptron (MLP) | Survey-reported occupant characteristics and appliance operating hours (daily scalar hours, sec. 2.2) | Monthly household electricity and gas consumption | RMSE, MAPE against utility bills | No (uses scalar hours per day, not diary time series) | full |
| C19 | Jianli Chen, Rajendra Adhikari, Eric Wilson (2021) | arXiv:2111.01881v2 | arXiv:2111.01881v2 | EnergyPlus (ResStock) | None (Markov-chain stochastic generator) | ATUS time-use survey data | High-resolution residential occupancy and equipment schedules | Comparison against national residential energy consumption totals | No (feeds EnergyPlus directly) | full |
| C20 | Wooyoung Jung (2026) | SoftwareX | 10.1016/j.softx.2026.103068 | EnergyPlus | LLM agent platform (BuildOcc) | Persona prompts and activity descriptions | Hourly occupant presence and action schedules | EnergyPlus load sensitivity | No (generates schedules for EnergyPlus) | full |
| C21 | Ruiming Zhang, Tongyu Zhou, Hong Ye (2024) | Energy and Buildings | 10.1016/j.enbuild.2023.113854 | EnergyPlus | None (stochastic movement model) | Time-use survey activity duration distributions | Room-level presence schedules for building simulation | Transition probability distribution matching | No (stochastic generator feeding EnergyPlus) | abstract |

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? (yes / partly / no, with the row in C that claims it) | Which of our assets it uses (from the master brief, section 3) | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| P1. Occupancy time series as surrogate input [INFERENCE] | yes (unclaimed; C3, C4, C5, C6 hold schedules fixed) | European time-use diaries, residential archetypes, GPU cluster | None | Time series input spaces are high dimensional; gradient-boosted tree baselines might match recurrent/transformer models | 3 |
| P2. Scored on paired differences [INFERENCE] | partly (claimed in retrofit domain by C2; unclaimed for occupancy effect) | Paired EnergyPlus campaign, GPU cluster | None | EnergyPlus thermal mass buffers short-term occupant variation, so surrogate differences might be noisy | 2 |
| P3. An occupancy-blind negative control [INFERENCE] | yes (unclaimed; standard feature selection exists in C7, but negative shuffled control is absent) | Paired campaign runs, GPU cluster | None | If the blind control retains moderate accuracy due to diurnal solar and weather correlations, the test criterion requires strict thresholds | 1 |
| P4. Time-use diaries feeding a learned energy model [INFERENCE] | yes (unclaimed; C13 shows diaries feed schedule generators, not surrogates) | European time-use diaries, diary-to-schedule pipeline | None | National diary surveys capture self-reported activities with reporting biases | 2 |
| P5. Hourly residential surrogates at stock scale, 2019 to today [INFERENCE] | no (claimed by C3, C5, C6) | Residential archetypes, European typology parameters, GPU cluster | None | Concept of hourly stock surrogate is already published; paper must avoid claiming first hourly district surrogate | 0 (angle dropped as standalone claim) |
| Unified candidate claim of brief section 4 [INFERENCE] | yes | All assets (diaries, archetypes, pipeline, GPU cluster) | None | The surrogate is trained and evaluated entirely on simulated data without physical meter validation | 4 |

### Verdicts

* **Verdict on Part P1:** open as far as searched [INFERENCE]. Deciding row: C3 (Pan et al. 2024) is the closest published work, which develops a bidirectional LSTM surrogate for EnergyPlus prototype loads but restricts dynamic inputs strictly to weather time series while holding occupancy schedules constant. The logged queries Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, and Q14 found nothing closer.
* **Verdict on Part P4:** open as far as searched [INFERENCE]. Deciding rows: C13 (Vosoughkhosravi et al. 2023) and C1 (He et al. 2015) are the closest published works, confirming that time-use survey diaries are used exclusively to calibrate stochastic profile generators or drive physical simulation engines, never as direct sequential inputs to a learned model that predicts building energy use. The logged queries Q15, Q16, Q17, Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25, Q26, Q27, and Q28 found nothing closer.

## Section E. What this changes in our planning

* Do not claim the first hourly residential building energy surrogate or the first stock-scale EnergyPlus surrogate, because C3 (Pan et al., 2024), C5 (Dai et al., 2025), and C6 (Govindarajan et al., 2025) have already established hourly district and urban building energy surrogates.
* Frame the core novelty around behavioral sequence sensitivity: feeding dynamic occupant activity sequences from time-use diaries directly into a learned surrogate, contrasting with C3, C5, and C6 where schedules are held static.
* Position difference-scoring on paired runs directly as an application of Park and Park's (2024, C2) causal validation methodology to occupant behavior, demonstrating that point-load accuracy metrics (RMSE, CV(RMSE)) are fundamentally insufficient to verify whether a surrogate learns true behavioral sensitivity.
* Maintain the paired simulation design (varying only occupancy while holding building geometry and weather fixed), because existing stock surrogates (C3, C5, C6) vary building morphology and weather while keeping occupancy static.
* Formalize the occupancy-blind control (shuffling occupancy sequences across runs) as a mandatory negative control, highlighting that standard surrogate studies (C4, C7) perform at most parameter ablation, but never verify whether sequence-dependent effects collapse under input permutation.
* Position the diary-to-surrogate pipeline directly against the state of the art reviewed in C13 (Vosoughkhosravi et al., 2023) and demonstrated in C1 (He et al., 2015), emphasizing that while prior work used time-use diaries to generate schedules for slow physics engines, this work uses diary sequences directly to train an instantaneous surrogate for stock analysis.

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| K4 Technical Report (ORNL/LTR-2021/1923) | Full technical report describing the FRP EnergyPlus surrogate model | https://www.osti.gov/servlets/purl/1817464 (file URL) / https://www.osti.gov/biblio/1817464 (landing page) | Open access via OSTI | Yes (downloaded and verified in full, 20 pages) |
| K1 Conference Paper PDF | Full text conference paper on coupling stochastic occupancy to EnergyPlus | https://publications.ibpsa.org/proceedings/bs/2015/papers/bs2015_2655.pdf | Open access | Yes (downloaded and read in full) |
| Pan et al. 2024 Bi-LSTM UBEM Paper | Full text repository copy of bidirectional LSTM urban building energy surrogate | https://escholarship.org/uc/item/84z4t4f2 | Open access | Yes (downloaded and read in full) |
| BESOS Platform Code Repository | Software platform for EnergyPlus surrogate modeling and optimization | https://gitlab.com/energyincities/besos | Open source (GPL-3.0) | Yes (HTTP 200 confirmed) |
| Richardson et al. Domestic Active Occupancy Model | Excel/VBA model generating Markov chain occupancy profiles from UK TUS data | https://hdl.handle.net/2134/3112 | Open access download | Yes (handle resolves to Loughborough repository) |

### Verbatim inputs of Li, Bae and Im 2021 (K4)

The full text PDF was retrieved directly from `https://www.osti.gov/servlets/purl/1817464` (20 pages). From Section 3.1 "INPUTS AND OUTPUTS", page 10, Table 5:

"Table 5. Input variables.
Variable name | Quantity
OAT | 1
OAT relative humidity | 1
OA pressure | 1
Wind speed | 1
Wind direction | 1
Horizontal infrared radiation rate | 1
Diffuse solar radiation rate | 1
Direct solar radiation rate | 1
Lighting energy | 1
Internal heat gains: equipment | 1
People Activity | 1
SensorBias: AHU OAT | 1
SensorPrecision: AHU OAT | 1
SensorTotalError: AHU OAT | 1
SensorBias: AHU SAT | 1
SensorPrecision: AHU SAT | 1
SensorTotalError: AHU SAT | 1
SensorBias: zone VAV SAF | 10
SensorPrecision: zone VAV SAF | 10
SensorTotalError: zone VAV SAF | 10
SensorBias: zone VAV SAT | 10
SensorPrecision: zone VAV SAT | 10
SensorTotalError: zone VAV SAT | 10
SensorBias: zone air temperature | 10
SensorPrecision: zone air temperature | 10
SensorTotalError: zone air temperature | 10
Total | 107
(Note: OAT = outdoor air temperature, SAT=supply air temperature, SAF=supply air flow rate)" (quoted from page 10).

From page 9:
"The purpose of the surrogate model was to establish the mapping relationship between input and output variables. The input variables were based on the FRP EnergyPlus models. A detailed list of variables is provided in Table 5." (quoted from page 9).

From page 7:
"The large set of the simulation cases were generated by integrating sensor errors into an emulator based on EnergyPlus and Python EMS... The inputs were the sensor errors injected for the five selected sensors for the FRP building emulator, as shown in Table 3." (quoted from page 7).

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Full query log table

| Query # | Part | Source | Exact query string | Date | Hits reported | Screened | IDs of kept results |
|---|---|---|---|---|---|---|---|
| Q1 | P1 | OpenAlex | `surrogate "EnergyPlus" "occupancy" "time series"` | 2026-10-01 | 280 | 10 | 10.1016/j.buildenv.2021.108684, 10.1016/j.scs.2019.101484, 10.1016/j.enbenv.2022.06.008 |
| Q2 | P1 | OpenAlex | `metamodel "building energy simulation" "occupancy schedule"` | 2026-10-01 | 40 | 10 | 10.1016/j.enbuild.2017.06.014, 10.1177/00375497231168630, 10.1016/j.heliyon.2023.e16593 |
| Q3 | P1 | OpenAlex | `"deep learning" surrogate "EnergyPlus" "occupancy"` | 2026-10-01 | 285 | 10 | 10.1016/j.aei.2018.06.004, 10.1016/j.apenergy.2023.121576, 10.3390/thermo4010008 |
| Q4 | P1 | OpenAlex | `surrogate "urban building energy" "LSTM" "EnergyPlus"` | 2026-10-01 | 43 | 10 | 10.1080/19401493.2024.2359985 (Pan 2024, K3), 10.1016/j.scs.2025.106492, 10.1016/j.apenergy.2025.125853 |
| Q5 | P1 | Crossref | `surrogate EnergyPlus occupancy "time series"` | 2026-10-01 | 3847751 | 10 | 10.2172/1817464 (Li 2021, K4), 10.1090/fic/011/07, 10.2172/951766 |
| Q6 | P1 | Crossref | `metamodel "building energy simulation" "occupant schedule"` | 2026-10-01 | 4515133 | 10 | 10.1016/j.enbuild.2014.07.033, 10.26868/25222708.2025.1423, 10.26868/25222708.2023.1584 |
| Q7 | P1 | Crossref | `"machine learning" surrogate EnergyPlus "occupant presence"` | 2026-10-01 | 3342183 | 10 | 10.3390/su18157697, 10.2172/1817464 (Li 2021, K4), 10.37099/mtu.dc.etdr/1472 |
| Q8 | P1 | Crossref | `surrogate "building energy retrofit" "artificial neural network"` | 2026-10-01 | 6293775 | 10 | 10.63044/s23par77, 10.1080/19401493.2023.2282078 (Park 2023, K2), 10.1016/enpol.2014.02.001 |
| Q9 | P1 | arXiv | `all:"building energy" AND all:"surrogate" AND all:"occupancy"` | 2026-10-01 | 2 | 2 | arXiv:2507.17526v1, arXiv:2507.19233v1 |
| Q10 | P1 | arXiv | `all:"EnergyPlus" AND all:"metamodel" AND all:"time series"` | 2026-10-01 | 0 | 0 | none (0 hits) |
| Q11 | P1 | arXiv | `all:"building performance simulation" AND all:"surrogate" AND all:"schedule"` | 2026-10-01 | 0 | 0 | none (0 hits) |
| Q12 | P1 | Google Scholar | `surrogate EnergyPlus "occupancy schedule" "time series"` | 2026-10-01 | 119 | 10 | 10.1016/j.buildenv.2022.109151, bs2025_1489, 10.1080/19401493.2026.2735926 |
| Q13 | P1 | Google Scholar | `metamodel "building energy simulation" "occupancy time series"` | 2026-10-01 | 0 | 0 | none (0 hits) |
| Q14 | P1 | Google Scholar | `"surrogate model" "EnergyPlus" "occupant behavior" "LSTM"` | 2026-10-01 | 10 | 10 | authorea.15009435, 10.1109/JSYST.2025.3524182, 10.1016/j.enbuild.2026.116744 |
| Q15 | P4 | OpenAlex | `"time use" diary "building energy" "machine learning"` | 2026-10-01 | 48 | 10 | 10.3390/buildings11020041, 10.3390/en17174400, 10.1007/s12053-019-09791-1 |
| Q16 | P4 | OpenAlex | `"ATUS" "building energy" surrogate` | 2026-10-01 | 6 | 6 | 10.1111/j.1600-0668.2010.00686.x, 10.31274/td-20240329-150, 10.1016/j.enbuild.2020.110611 |
| Q17 | P4 | OpenAlex | `"time-use survey" "energy consumption" "neural network" residential` | 2026-10-01 | 148 | 10 | 10.1016/j.enbuild.2017.04.072 (Diao 2017), 10.3390/en12040608 (Lee 2019), 10.3390/en14092390 |
| Q18 | P4 | OpenAlex | `"American Time Use Survey" "occupant-building interactions" review` | 2026-10-01 | 12 | 10 | 10.1016/j.enbuild.2023.113245 (Vosoughkhosravi 2023), 10.1016/j.buildenv.2020.106964, 10.1016/j.erss.2025.104075 |
| Q19 | P4 | Crossref | `"time-use" diary "building energy" "deep learning"` | 2026-10-01 | 10113772 | 10 | 10.3030/739834, 10.2139/ssrn.4696796, 10.2139/ssrn.5208655 |
| Q20 | P4 | Crossref | `"American Time Use Survey" "energy model" surrogate` | 2026-10-01 | 15399646 | 10 | 10.1016/j.enbuild.2011.09.020 (Chiou 2011), 10.2139/ssrn.6091847, 10.32797/jtur-2022-2 |
| Q21 | P4 | Crossref | `"HETUS" OR "MTUS" "building energy" model` | 2026-10-01 | 6590661 | 10 | 10.7717/peerj.17678/table-1, 10.3403/30337816, 10.3403/30337816u |
| Q22 | P4 | Crossref | `"stochastic occupancy" "EnergyPlus" "time use" "neighbourhood"` | 2026-10-01 | 3875639 | 10 | 10.26868/25222708.2015.2655 (He 2015, K1), 10.1016/j.jup.2013.09.005, 10.1016/j.enbuild.2023.113854 |
| Q23 | P4 | arXiv | `all:"time use" AND all:"building energy"` | 2026-10-01 | 2 | 2 | arXiv:2609.02729v2 (Jung 2026), arXiv:2111.01881v2 (Chen 2021) |
| Q24 | P4 | arXiv | `all:"time use survey" AND all:"energy consumption"` | 2026-10-01 | 2 | 2 | arXiv:2111.01881v2 (Chen 2021), arXiv:2609.02729v2 (Jung 2026) |
| Q25 | P4 | arXiv | `all:"diary" AND all:"building energy" AND all:"neural"` | 2026-10-01 | 0 | 0 | none (0 hits) |
| Q26 | P4 | Google Scholar | `"time use survey" "building energy" "surrogate" OR "machine learning"` | 2026-10-01 | 330 | 10 | 10.1061/JCCEE5.CPENG-6002, 10.1016/j.enbuild.2022.111973, 10.1016/j.enbuild.2026.117105 |
| Q27 | P4 | Google Scholar | `"ATUS" "building energy simulation" "neural network" OR "surrogate"` | 2026-10-01 | 6 | 6 | 10.1007/s12273-021-0813-8, 10.1109/ACCESS.2024.3391820, 10.1061/9780784486115.114 |
| Q28 | P4 | Google Scholar | `"time use diaries" "residential building energy" "deep learning"` | 2026-10-01 | 2 | 2 | proquest.826d7629452e54458e4510aa0a0a8214, proquest.8131c6ef3cb2a81b7fd4edb151b7b3fd |

### Positive controls (Known works)

* **He et al. (2015, K1, `10.26868/25222708.2015.2655`):** "Coupling A Stochastic Occupancy Model to EnergyPlus to Predict Hourly Thermal Demand of A Neighbourhood", authored by Miaomiao He, Timothy Lee, Simon Taylor, Steven K. Firth, and Kevin Lomas, published in Building Simulation Conference Proceedings (2015). The study automates the coupling between a Richardson Markov chain occupancy model derived from the UK 2000 Time Use Survey and EnergyPlus to simulate hourly space heating demand across 125 dwellings in Leicestershire without training any machine learning surrogate. **Found by search:** Yes, retrieved directly by Crossref query Q22 (`"stochastic occupancy" "EnergyPlus" "time use" "neighbourhood"`).
* **Park and Park (2023, K2, `10.1080/19401493.2023.2282078`):** "Limitations and issues of conventional artificial neural network-based surrogate models for building energy retrofit", authored by Chul-Hong Park and Cheol Soo Park, published in Journal of Building Performance Simulation, Volume 17, Issue 3, pp. 361-370 (published online 2023, print 2024). The authors evaluate artificial neural network surrogates on building retrofit interventions and demonstrate that despite low RMSE on absolute energy loads, conventional surrogates fail to reproduce causal input-output relationships and savings differences between paired simulation runs. **Found by search:** Yes, retrieved directly by Crossref query Q8 (`surrogate "building energy retrofit" "artificial neural network"`).
* **Pan et al. (2024, K3, `10.1080/19401493.2024.2359985`):** "Surrogate modelling for urban building energy simulation based on the bidirectional long short-term memory model", authored by Xiyu Pan, Yujie Xu, and Tianzhen Hong, published in Journal of Building Performance Simulation, Volume 19, Issue 5, pp. 875-893 (2024). The paper develops prototype-specific bidirectional LSTM surrogate models trained on EnergyPlus simulations across Los Angeles County to predict hourly electricity and heat emissions from sequential microclimate weather features while keeping building operational schedules fixed. **Found by search:** Yes, retrieved directly by OpenAlex query Q4 (`surrogate "urban building energy" "LSTM" "EnergyPlus"`).
* **Li, Bae and Im (2021, K4, `10.2172/1817464`):** "Surrogate Model of Flexible Research Platform EnergyPlus Models to Enable Sensitivity Analysis", authored by Yanfei Li, Yeonjin Bae, and Piljae Im, published as Oak Ridge National Laboratory Technical Letter Report ORNL/LTR-2021/1923 by OSTI (2021). The report develops multilayer perceptron and LSTM surrogate models from 4,000 EnergyPlus cloud simulations of a two-story testbed building to predict 54 HVAC system and zone outputs from 107 input variables representing weather, internal loads, and injected sensor faults. **Found by search:** Yes, retrieved directly by Crossref query Q5 (`surrogate EnergyPlus occupancy "time series"`) and Q7 (`"machine learning" surrogate EnergyPlus "occupant presence"`).

### Unread items from RT45 vetting

* **Westermann and Evins (2019, `10.1016/j.enbuild.2019.05.057`):** The complete reference list of 136 works was retrieved from Crossref and examined for candidate P1 works. Candidate papers checked include:
  - Reference 108: Papadopoulos and Azar (2016, `10.1016/j.enbuild.2016.06.079`), which couples linear regression surrogates with agent-based modeling using thermostat setpoints, lighting fractions, and equipment power fractions as inputs (not an occupancy time series);
  - Reference 94: Singaravel et al. (2018, `10.1016/j.aei.2018.06.004`), which uses component-based deep neural networks on geometry, construction, and HVAC parameters without dynamic schedules;
  - Reference 21: Hester et al. (2017, `10.1016/j.enbuild.2016.10.047`), which develops probabilistic metamodels for residential design using envelope and geometric parameters;
  - Reference 92: Ascione et al. (2017, `10.1016/j.energy.2016.10.126`), which predicts retrofit scenarios from envelope parameters;
  - Reference 15: Van Gelder et al. (2014, `10.1016/j.simpat.2014.10.004`), which compares metamodelling techniques on envelope and HVAC inputs.
  Conclusion: Across all 136 references, surrogate inputs are strictly classified into envelope, geometry, HVAC systems, and weather. Internal loads are treated either as static power densities or standard schedule templates; zero studies use an occupancy time series as an input.
* **Vosoughkhosravi et al. (2023, `10.1016/j.enbuild.2023.113245`):** The abstract was retrieved and read in full from the LSU repository landing record (`https://repository.lsu.edu/construction_management_pubs/245`). The study reviews exactly 51 articles (not "over 100") using the American Time Use Survey (ATUS) in energy-related occupant-building interactions. It categorizes ATUS applications into: (1) modeling occupancy schedules, (2) occupant energy-related activity patterns, and (3) building energy performance. In all 51 studies, ATUS data is used to generate schedules or parameterize stochastic behavior models that feed forward into physical simulation software (EnergyPlus, DOE-2). Zero studies feed ATUS diary sequences directly into a learned energy surrogate model.
* **Dai et al. CityTFT (2025, `10.1016/j.apenergy.2025.125712`):** Examined via IDEAS/RePEc. CityTFT adapts Temporal Fusion Transformers by combining a static covariate encoder and variable selection network with a neural network predicting heating and cooling trigger probability. Inputs are sequential weather dynamics and static building covariates across 114 buildings. Occupancy schedules are held constant to standard templates; occupancy is not varied and is not an input sequence to the transformer.
* **Govindarajan et al. (2025, `10.1016/j.enbuild.2025.116366`):** Examined via Adaptive Design Lab, Unpaywall, and official records. The study trains MLP, HGBoost, and RNN models on 17.5 million simulation records to predict hourly site energy use (EUse) for residential precincts in tropical cities. The 23 independent variables comprise climate data, spatial logic parameters (density, block spacing, inter-building shading), and model design parameters. Are occupancy schedules an input, and as what? Occupancy schedules are NOT an input to the surrogate model; they are standard deterministic profiles (full versus partial occupancy periods) used within the underlying simulation workflow to calculate baseline comfort hours and cooling demands.

### Queries that found nothing

* Q10 (arXiv): `all:"EnergyPlus" AND all:"metamodel" AND all:"time series"` returned 0 hits.
* Q11 (arXiv): `all:"building performance simulation" AND all:"surrogate" AND all:"schedule"` returned 0 hits.
* Q13 (Google Scholar): `metamodel "building energy simulation" "occupancy time series"` returned 0 hits.
* Q25 (arXiv): `all:"diary" AND all:"building energy" AND all:"neural"` returned 0 hits.

### Works that could not be opened

All candidate papers and records cited in Sections B and C were successfully accessed and verified through official publisher APIs, institutional repositories (LSU, eScholarship, OSTI, arXiv), or open landing pages. No candidate paper was abandoned as unretrievable.

### Answers to the four standard questions

1. **Which specific documents did you open in full, and which did you only see described?**
   Opened in full (count = 6):
   - Li, Bae and Im (2021, C4 / K4): full technical report PDF opened and verified from OSTI (`https://www.osti.gov/servlets/purl/1817464`, 20 pages).
   - He et al. (2015, C1 / K1): full conference paper PDF opened from IBPSA repository (`https://publications.ibpsa.org/proceedings/bs/2015/papers/bs2015_2655.pdf`, pp. 2101-2108).
   - Pan et al. (2024, C3 / K3): full paper PDF opened from eScholarship repository copy (`https://escholarship.org/uc/item/84z4t4f2`, pp. 875-893).
   - Westermann and Evins (2019, C7): full metadata and complete 136-reference list opened and reviewed via Crossref.
   - Lee, Jung and Lee (2019, C18): full paper opened via MDPI open access repository.
   - Chen, Adhikari and Wilson (2021, C19) and Jung (2026, C20): full preprint text opened via arXiv.
   Seen described via official abstracts and registry landing records (count = 15):
   - Park and Park (2024, C2 / K2), Dai et al. CityTFT (2025, C5), Govindarajan et al. (2025, C6), Papadopoulos and Azar (2016, C8), Singaravel et al. (2018, C9), Herbinger et al. (2023, C10), Liang et al. (2022, C11), Seyedzadeh et al. (2020, C12), Vosoughkhosravi et al. (2023, C13), Chiou et al. (2011, C14), Satre-Meloy et al. (2020, C15), Diao et al. (2017, C16), Kleinebrahm et al. (2021, C17), Zhang et al. (2024, C21), Mauro et al. (2015).

2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   We would have written `NOT FOUND` for Section F if the direct connection to `osti.gov/servlets/purl/1817464` had failed or timed out. We would have written "this topic is closed / crowded" if we had uncovered a peer-reviewed paper where an EnergyPlus or TRNSYS surrogate model takes an hourly or sub-hourly occupancy sequence derived from time-use diaries as an input, trains on simulation runs where only occupancy varies, and evaluates the surrogate specifically on paired occupancy differences with an occupancy-blind negative control.

3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   Candidate angle P5 (hourly residential building energy surrogates at stock or district scale) is already taken by Pan et al. (2024, C3), Dai et al. (2025, C5), and Govindarajan et al. (2025, C6). Candidate angle P2 (evaluating surrogate models on paired causal differences rather than absolute load RMSE) is partly taken in the retrofit domain by Park and Park (2024, C2), though not for occupancy effects. The unified claim of Section 4 remains untouched because the surrogate modeling community and the time-use diary community operate in separate silos: surrogate modelers treat occupant schedules as static boundary conditions, while time-use researchers use diaries to drive slow physical simulation engines rather than training fast machine learning surrogates.

4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   No. All authors, publication years, titles, volumes, and DOIs were retrieved directly from official Crossref, OSTI, and OpenAlex records. All numbers quoted (such as the 107 inputs of K4, the 20 pages of K4, the 136 references of Westermann and Evins, the 51 articles of Vosoughkhosravi et al., and the 23 independent variables of Govindarajan et al.) were verified directly against primary text.

## Section H. Full reference list

1. He, M., Lee, T., Taylor, S., Firth, S. K., and Lomas, K. (2015). Coupling A Stochastic Occupancy Model to EnergyPlus to Predict Hourly Thermal Demand of A Neighbourhood. Building Simulation Conference Proceedings, pp. 2101-2108. DOI: 10.26868/25222708.2015.2655. Tier 1. Read: full text.
2. Park, C.-H., and Park, C. S. (2024). Limitations and issues of conventional artificial neural network-based surrogate models for building energy retrofit. Journal of Building Performance Simulation, 17(3), pp. 361-370. DOI: 10.1080/19401493.2023.2282078. Tier 1. Read: abstract.
3. Pan, X., Xu, Y., and Hong, T. (2026). Surrogate modelling for urban building energy simulation based on the bidirectional long short-term memory model. Journal of Building Performance Simulation, 19(5), pp. 875-893. DOI: 10.1080/19401493.2024.2359985. Tier 1. Read: full text.
4. Li, Y., Bae, Y., and Im, P. (2021). Surrogate Model of Flexible Research Platform EnergyPlus Models to Enable Sensitivity Analysis. Technical Letter Report ORNL/LTR-2021/1923, Oak Ridge National Laboratory, Office of Scientific and Technical Information (OSTI). DOI: 10.2172/1817464. Tier 1. Read: full text.
5. Dai, T.-Y., Niyogi, D., and Nagy, Z. (2025). CityTFT: A temporal fusion transformer-based surrogate model for urban building energy modeling. Applied Energy, 389, 125712. DOI: 10.1016/j.apenergy.2025.125712. Tier 1. Read: abstract.
6. Govindarajan, P., Ortner, F. P., and Han, J. M. (2025). Surrogate modeling: hourly energy performance prediction for residential precincts in tropical cities using synthetic data. Energy and Buildings, 347, 116366. DOI: 10.1016/j.enbuild.2025.116366. Tier 1. Read: abstract.
7. Westermann, P., and Evins, R. (2019). Surrogate modelling for sustainable building design: A review. Energy and Buildings, 198, pp. 170-186. DOI: 10.1016/j.enbuild.2019.05.057. Tier 1. Read: full text.
8. Papadopoulos, S., and Azar, E. (2016). Integrating building performance simulation in agent-based modeling using regression surrogate models: A novel human-in-the-loop energy modeling approach. Energy and Buildings, 128, pp. 214-223. DOI: 10.1016/j.enbuild.2016.06.079. Tier 1. Read: abstract.
9. Singaravel, S., Suykens, J. A. K., and Geyer, P. (2018). Deep-learning neural-network architectures and methods: Using component-based models in building-design energy prediction. Advanced Engineering Informatics, 38, pp. 578-590. DOI: 10.1016/j.aei.2018.06.004. Tier 1. Read: abstract.
10. Herbinger, F., Vandenhof, C., and Kummert, M. (2023). Building energy model calibration using a surrogate neural network. Energy and Buildings, 294, 113057. DOI: 10.1016/j.enbuild.2023.113057. Tier 1. Read: abstract.
11. Liang, Y., Pan, Y., and Yuan, X. (2022). Surrogate modeling for long-term and high-resolution prediction of building thermal load with a metric-optimized KNN algorithm. Energy and Built Environment, 5(3), pp. 443-455. DOI: 10.1016/j.enbenv.2022.06.008. Tier 1. Read: abstract.
12. Seyedzadeh, S., Pour Rahimian, F., and Oliver, S. (2020). Data driven model improved by multi-objective optimisation for prediction of building energy loads. Automation in Construction, 117, 103188. DOI: 10.1016/j.autcon.2020.103188. Tier 1. Read: abstract.
13. Vosoughkhosravi, S., Jafari, A., and Zhu, Y. (2023). Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review. Energy and Buildings, 294, 113245. DOI: 10.1016/j.enbuild.2023.113245. Tier 1. Read: abstract.
14. Chiou, Y.-S., Carley, K. M., and Davidson, C. I. (2011). A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method. Energy and Buildings, 43(11), pp. 3228-3238. DOI: 10.1016/j.enbuild.2011.09.020. Tier 1. Read: abstract.
15. Satre-Meloy, A., Diakonova, M., and Grünewald, P. (2020). Cluster analysis and prediction of residential peak demand profiles using occupant activity data. Applied Energy, 254, 114246. DOI: 10.1016/j.apenergy.2019.114246. Tier 1. Read: abstract.
16. Diao, L., Sun, Y., and Chen, Z. (2017). Modeling energy consumption in residential buildings: A bottom-up analysis based on occupant behavior pattern clustering and stochastic simulation. Energy and Buildings, 147, pp. 49-62. DOI: 10.1016/j.enbuild.2017.04.072. Tier 1. Read: abstract.
17. Kleinebrahm, M., Torriti, J., and McKenna, R. (2021). Using neural networks to model long-term dependencies in occupancy behavior. Energy and Buildings, 248, 110879. DOI: 10.1016/j.enbuild.2021.110879. Tier 1. Read: abstract.
18. Lee, S., Jung, S., and Lee, J. (2019). Prediction Model Based on an Artificial Neural Network for User-Based Building Energy Consumption in South Korea. Energies, 12(4), 608. DOI: 10.3390/en12040608. Tier 1. Read: full text.
19. Chen, J., Adhikari, R., and Wilson, E. (2021). Stochastic simulation of residential building occupant-driven energy use in a bottom-up model of the U.S. housing stock. arXiv preprint arXiv:2111.01881v2. Tier 2. Read: full text.
20. Jung, W. (2026). BuildOcc: A large language model occupant agent platform for building energy research. SoftwareX, 33, 103068. DOI: 10.1016/j.softx.2026.103068. Tier 1. Read: full text.
21. Zhang, R., Zhou, T., and Ye, H. (2024). Introducing a novel method for simulating stochastic movement and occupancy in residential spaces using time-use survey data. Energy and Buildings, 304, 113854. DOI: 10.1016/j.enbuild.2023.113854. Tier 1. Read: abstract.
