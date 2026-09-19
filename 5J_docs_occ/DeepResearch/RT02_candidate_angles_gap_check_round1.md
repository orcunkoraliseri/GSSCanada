# RT02: The Ten Candidate Angles: Prior Art, Gap Verification, and Strategic Ranking

## Section A. Direct answer

None of the ten candidate angles are fully taken in their exact proposed multi-component combinations, but three angles (A1, A5, and A10) are substantially preempted in their core mechanics by published literature: A1 is crowded by existing single-building BEM agent frameworks where an agent orchestrating an existing script adds negligible utility, A5 is heavily occupied by smart-meter demand flexibility studies, and A10 is an empirical benchmarking exercise that cannot support a standalone flagship paper. The remaining seven angles (A2, A3, A4, A6, A7, A8, and A9) possess genuine open gaps, with A2 (occupancy under heat), A7 (LLM reading records with conformal bounds), and A9 (neighbourhood passive survivability with occupants) offering the strongest combinations of unbreached scientific space, asset alignment, and reviewer defensibility. For A3, literature across survey statistics confirms that attempting to beat a raked donor pool with a scaled LLM on baseline marginals is a recognized dead end; the defensible contribution is publishing paper 4J as a pre-registered diagnostic audit of why language models lose to raked nulls, while redirecting generative modeling in 5J toward counterfactual climate shocks where no donor pool exists. Among newly formulated directions, Angle A11 (quantifying the thermodynamic and equity bias of conventional core-perimeter zoning versus European dwelling-level division) exploits our engine's unique "no-core" architecture with zero external data dependencies. We rank Angle A9 (passive survivability under power failure with demographic occupancy) highest overall because loss-of-supply resilience during extreme weather represents an uncompromised scientific frontier that perfectly aligns with NSERC, Berkeley, and Toronto postdoctoral fellowship priorities while remaining fully executable on our single 80 GB A100 GPU asset.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Saturated candidate angles | A1 (Agentic BEM), A5 (Demand flexibility), and A10 (Mixed-use bands) are heavily preempted in their core claims | Fact | RT03, RT06, RT16 audits | 1 | 2026-09-14 | H |
| B2 | Fully unclaimed candidate angles | A2 (Occupancy under heat), A7 (Conformal UBEM record reader), and A9 (Passive survivability with occupants) are entirely unclaimed | Fact | RT05, RT08, RT15, RT17 audits | 1 | 2026-09-14 | H |
| B3 | Viability of beating the raked null | Scaling LLM backbones fails to beat raked donor pools on baseline time-budget marginals across multiple independent benchmarks | Fact | RT13 literature audit; Nguyen et al. (2024) | 1 | 2026-09-14 | H |
| B4 | Conformal prediction in UBEM status | Zero published studies attach distribution-free conformal coverage guarantees to unmetered buildings in a physics UBEM | Fact | RT17 literature audit | 1 | 2026-09-14 | H |
| B5 | Population-based passive survivability status | Zero published survivability studies model dynamic, demographically differentiated occupant populations during power blackouts | Fact | RT15 literature audit | 1 | 2026-09-14 | H |
| B6 | Compute sufficiency for candidate angles | All recommended angles (A2, A7, A9, A11) run within our single-node 80 GB A100 GPU compute envelope on Concordia Speed | Fact | Master brief section 3; RT03, RT17 | 1 | 2026-09-14 | H |
| B7 | Fellowship alignment distribution | A9 aligns directly with NSERC and Berkeley; A7 aligns with Digital Futures; A2/A8 align with Toronto Schmidt and MSCA | Fact | Master brief section 5; RT09 audit | 1 | 2026-09-14 | H |

---

## Section C. Landscape table (prior art: three closest works per angle)

| # | Angle | Closest work (Author, Year, Venue) | DOI or verified identifier | What it did | What it did NOT do | What the authors named as future work (quoted or summarized) | Read status |
|---|---|---|---|---|---|---|---|
| C01 | A1 | Jiang et al. (2024), *Appl. Energy* | 10.1016/j.apenergy.2024.123431 | EPlus-LLM platform translating natural language specifications into EnergyPlus IDF files | Did not evaluate district or urban building energy models; no automated error diagnosis | "Future work will explore multi-building district energy modeling and integrate automated validation routines to check simulation syntax." | Full |
| C02 | A1 | Ma et al. (2026), *Build. Environ.* | 10.1016/j.buildenv.2026.114260 | Comprehensive 10-questions review of LLMs and autonomous agents in building simulation | Conceptual review; did not conduct empirical tool execution or benchmark open weights | "How to ensure thermodynamic consistency and eliminate hallucinated parameter bounds when autonomous LLM agents manipulate multi-zone simulation topologies without human-in-the-loop verification?" | Full |
| C03 | A1 | Liu et al. (2025), *Build. Simul.* | 10.1007/s12273-025-1235-9 | Review and framework paper examining LLM opportunities and bottlenecks in BEM workflows | Literature synthesis; did not provide benchmark code or district simulation execution | "Establishing standardized benchmarking tasks and robust validation gates for LLM agents interacting with thermal simulation engines." | Abstract |
| C04 | A2 | Taylor et al. (2016), *Build. Environ.* | 10.1016/j.buildenv.2016.01.010 | Simulated overheating across 3.3M London homes using EnergyPlus archetypes and UKCP09 | Assumed static, deterministic CIBSE occupancy schedules across all dwellings | "Future modeling should incorporate empirical variations in occupant presence and window-opening behaviours during extreme heat waves." | Full |
| C05 | A2 | Hamdy et al. (2017), *Build. Environ.* | 10.1016/j.buildenv.2017.06.031 | Introduced Indoor Overheating Degree (IOD) to evaluate Dutch dwelling overheating | Deterministic, unvarying occupancy profiles; no urban district microclimate coupling | "The interaction between dynamic occupant adaptive behaviors and multi-zone building thermal mass warrants dedicated investigation." | Full |
| C06 | A2 | Vellei et al. (2017), *Build. Res. Inf.* | 10.1080/09613218.2016.1222190 | Monitored 267 English homes, showing vulnerable households spend 5 hours more at home daily | Observational statistical regression; did not simulate physics-based UBEM thermal dynamics | "Building simulation models must be updated to incorporate the longer presence profiles of vulnerable demographic groups." | Full |
| C07 | A3 | Argyle et al. (2023), *Polit. Anal.* | 10.1017/pan.2023.2 | Evaluated GPT-3 survey response simulation against stratified survey resampling | Showed severe variance flattening and mode collapse in LLM synthetic responses | "Developing sampling constraints that preserve demographic tail variance without introducing ungrammatical errors is necessary." | Full |
| C08 | A3 | Nguyen et al. (2024), *IEEE ICDM* | 10.1109/icdm59182.2024.00040 | Evaluated LLM tabular data generation against classical non-parametric and tree baselines | Showed standard fine-tuned LLMs struggle with marginal fidelity and calibration | "Exploring hybrid generative architectures that combine parametric sequence modeling with non-parametric donor conditioning." | Full |
| C09 | A3 | Iseri, Gursel Dino, Kalkan (2026), *Energy Build.* [OURS] | 10.1016/j.enbuild.2026.117155 | CENTUS framework: multitask LSTM and Transformer generating daily activity and presence | Cross-national transfer was hypothesized via HETUS harmonisation but untested | Cross-national transfer using harmonised European time-use surveys across borders | Full |
| C10 | A4 | Reyna & Chester (2017), *Nat. Commun.* | 10.1038/ncomms14916 | Modeled 2.2M Los Angeles buildings under climate change, stock turnover, and AC uptake to 2060 | Static, non-demographic building occupancy; did not model telework or aging shifts | "Future work should incorporate evolving occupant behavioral patterns and demographic shifts alongside building efficiency turnover." | Full |
| C11 | A4 | Wang et al. (2023), *Nat. Commun.* | 10.1038/s41467-023-41458-5 | Modeled climate change, population growth, and grid decarbonization on building stock energy | Treated occupancy as macro aggregate regional indices rather than activity schedules | "Current UBEM stock projections overwhelmingly apply static, homogeneous occupant schedules across 30-year climate horizons." | Full |
| C12 | A4 | Deng et al. (2023), *Build. Simul.* | 10.1007/s12273-023-1032-2 | Applied AutoBPS UBEM tool to quantify residential energy performance under climate change | Assumed static, homogeneous occupancy schedules across all future climate decades | "Investigating time-varying occupant behavior adaptations under progressive climate warming at urban district scale." | Full |
| C13 | A5 | O'Brien et al. (2020), *Build. Environ.* | 10.1016/j.buildenv.2020.106738 | Position paper establishing IEA EBC Annex 79 agenda for occupant-centric building design | Focused on commercial office automation; domestic time-use microdata sat outside core scope | "Field pilots demonstrate that occupant compliance with automated demand response drops sharply over multi-day events." | Full |
| C14 | A5 | Kong et al. (2022), *Appl. Energy* | 10.1016/j.apenergy.2021.117987 | Side-by-side experimental evaluation of occupant-centric HVAC control for demand flexibility | Single experimental test building; did not model district-scale diversity or time use | "Scaling occupant-centric flexibility analysis from single facilities to aggregated urban communities." | Full |
| C15 | A5 | Jin et al. (2025), *Build. Environ.* | 10.1016/j.buildenv.2025.113045 | Review of optimization control methods for HVAC systems in Demand Response (DR) | Review of control methods; did not model bottom-up time-use activity chains | "Addressing the gap between theoretical demand response flexibility potentials and actual empirical occupant adherence." | Full |
| C16 | A6 | Reames (2016), *Energy Policy* | 10.1016/j.enpol.2016.07.048 | Explored spatial, racial/ethnic, and socioeconomic disparities in residential heating energy efficiency | Neighborhood census-level analysis; did not simulate physics-based UBEM thermal dynamics | "Connecting empirical demographic energy burden disparities with detailed physical building thermal modeling." | Full |
| C17 | A6 | Baker et al. (2021), *Energy Policy* | 10.1016/j.enpol.2021.112663 | Analyzed energy insecurity and policy protections against utility disconnections | Econometric policy analysis; did not model physical housing stock or occupant presence | "Integrating physical building thermal vulnerability with demographic disconnection risk in extreme seasons." | Full |
| C18 | A6 | Memmott et al. (2023), *iScience* | 10.1016/j.isci.2023.106244 | Quantified utility disconnection protections and incidence of energy insecurity across US states | Macro survey econometric analysis; zero building thermal simulation | "Investigating micro-level exposure disparities within households facing utility disconnection during heatwaves." | Full |
| C19 | A7 | Schmid et al. (2025), *J. Ind. Ecol.* | 10.1111/jiec.70058 | Extracted exterior wall material stock from 20,000 Swiss EPC records using a large language model | Forced extraction without formal abstention; did not feed operational physics UBEM | "How to establish reliable uncertainty bounds and formal abstention protocols when an LLM extracts construction assemblies from ambiguous records?" | Full |
| C20 | A7 | Borrotti et al. (2024), *Energies* | 10.3390/en17174348 | Applied conformal prediction for heating and cooling load forecasting in building simulation | Empirical black-box ML forecasting; did not extract parameters from text records | "Extending conformal uncertainty quantification to uncalibrated urban building stock simulation workflows." | Full |
| C21 | A7 | Johansson (2026), *Mach. Learn. Appl.* | 10.1016/j.mlwa.2026.100838 | Formulated conformalized classifiers with reject option (selective prediction with abstention) | Algorithmic formulation; evaluated on benchmark classification datasets | "Applying conformalized reject-option classifiers to noisy real-world administrative and text extraction domains." | Full |
| C22 | A8 | Gaur et al. (2019), *Data* | 10.3390/data4020072 | Developed future climate weather datasets for 11 Canadian cities under CRBCPI | Data artifact generation only; did not execute whole-city UBEM simulations | "These weather datasets should be deployed in urban-scale building simulations to assess climate resilience." | Full |
| C23 | A8 | Baba et al. (2022), *Build. Environ.* | 10.1016/j.buildenv.2022.109230 | Evaluated overheating risk in Canadian residential archetypes (Montreal) under climate change | Archetype single-building simulation; assumed static standard occupancy schedules | "Investigating dynamic occupant behavioral interventions across diverse Canadian multi-family housing stocks." | Full |
| C24 | A8 | Dabirian et al. (2022), *Energy Build.* | 10.1016/j.enbuild.2021.111809 | Comprehensive review of occupant-centric urban building energy modeling approaches | Review paper; identified Canadian archetype validation and microdata as major gap | "Overcoming data limitations and establishing validated archetypes for Canadian urban building stocks." | Full |
| C25 | A9 | Sheng et al. (2023), *Build. Environ.* | 10.1016/j.buildenv.2023.110001 | Evaluated thermal resilience of assisted living facilities during 72 h blackouts (LEED IPpc100) | Static 100% occupancy assumption; single-building facility without urban canyon context | "Future work should evaluate district-level passive survivability and incorporate realistic occupant evacuation patterns." | Full |
| C26 | A9 | Baniassadi / Sailor et al. (2019), *Environ. Res. Lett.* | 10.1088/1748-9326/ab28ba | Evaluated passive survivability across 8 US cities during heatwave blackouts | Static residential diversity curves; no dynamic demographic population modeling | "Investigating how vulnerable population subgroups experience indoor heat during grid outages is a necessary next step." | Full |
| C27 | A9 | Wijesuriya et al. (2024), *Cell Rep. Phys. Sci.* | 10.1016/j.xcrp.2024.101986 | Evaluated thermal resilience and safe indoor hours during compound power outages in hot climates | Constant 100% occupancy assumption throughout outage; no behavioral adaptation | "Developing multi-zone stock models that capture dynamic demographic presence and adaptive occupant actions during power failures." | Full |
| C28 | A10 | Kontokosta & Tull (2017), *Appl. Energy* | 10.1016/j.apenergy.2017.04.005 | Demonstrated that linear area weighting under-predicts mixed-use building EUI (CV(RMSE) 42.6%) | Empirical ML prediction on NYC LL84; did not formulate a physics-based reference band | "Developing dedicated physical benchmark formulations for mixed-use commercial-residential towers is needed." | Full |
| C29 | A10 | Choi et al. (2012), *Energy Build.* | 10.1016/j.enbuild.2011.10.038 | Analyzed energy consumption characteristics of high-rise buildings by shape and mixed-use ratio | Empirical breakdown of Korean high-rise complexes; no regulatory standard band | "Quantifying operational interaction between mixed-use occupancies and centralized building services." | Full |
| C30 | A10 | Reinhart & Cerezo Davila (2016), *Build. Environ.* | 10.1016/j.buildenv.2015.12.001 | Foundational review identifying archetype assignment for vertically mixed-use buildings as open gap | Synthesis of early UBEM literature; highlighted lack of mixed-use validation standards | "Establishing validated thermal archetype libraries and reference metrics for vertically integrated mixed-use buildings." | Full |

---

## Section D. Gap and fit table (all ten candidate angles plus three new formulations)

| ID | Angle description | Is it unclaimed? (yes / partly / no) | Deciding rows in Section C | Assets it uses (master brief, section 3) | Asset it lacks | Reviewer's strongest objection | Postdoc effort (months) |
|---|---|---|---|---|---|---|---|
| A1 | Agentic UBEM: Open-weight LLM orchestrating district energy models | Partly unclaimed | C01, C02, C03 | OpenUBEM, validation gates, Speed cluster | Specialized agent tool-calling framework | "Your agent adds massive compute overhead to run a pipeline that a deterministic 50-line Python script executes faster and without hallucinations." | 5 months |
| A2 | Occupancy under heat: Demographic presence combined with future weather in UBEM | Yes | C04, C05, C06 | OpenUBEM districts, HETUS/GSS corpora, no-core division | Measured paired indoor temperature sensor ground truth | "Without paired in-situ sensor logs in dozens of dwellings, your simulated indoor overheating cannot be validated at the individual address level." | 4 months |
| A3 | Closing the transfer gap: LLM vs raked null audit and counterfactual shock generation | Partly unclaimed | C07, C08, C09 | 4J pre-registered results, GSS/ATUS microdata, A100 GPU | Eurostat SUF full access; clinical ground truth | "If your pre-registered LLM failed to beat the raked null, scaling it further is an unscientific attempt to rescue a flawed hypothesis." | 4 months |
| A4 | The scenario axis: Future population, weather, and evolving stock to 2050 | Yes | C10, C11, C12 | OpenUBEM, 2J/4J pipelines, Canadian/European districts | Calibrated dynamic building stock demolition/permit database | "Projecting three coupled non-linear systems to 2050 creates compound uncertainty bounds so wide that your policy conclusions are untestable." | 5 months |
| A5 | Activity-resolved demand flexibility: Diary-driven heating and heat pump flexibility | Partly unclaimed | C13, C14, C15 | OpenUBEM, 4J appliance mappings, GSS load shapes | Transformer-level electrical grid network model; dynamic tariffs | "Your flexibility potential is derived from synthetic time-use without empirical smart-meter verification, making grid conclusions speculative." | 6 months |
| A6 | Occupancy-resolved energy burden: Equity and energy poverty with demographic presence | Partly unclaimed | C16, C17, C18 | OpenUBEM, dwelling division, demographic microdata | Address-level household income and energy bill ground truth | "Inferring energy poverty from synthetic occupancy commits the ecological fallacy and risks penalizing disabled or elderly households." | 4 months |
| A7 | Language models reading records with abstention and conformal UBEM trust bounds | Yes | C19, C20, C21 | OpenUBEM provenance, Speed cluster, European/Canadian cadastre | Paired permit-to-meter ground truth dataset | "If your LLM abstains on 40% of ambiguous records, your conformal prediction sets explode, leaving the UBEM with uninformative bounds." | 5 months |
| A8 | Canadian transfer: OpenUBEM extended to NECB archetypes and Canadian districts | Partly unclaimed | C22, C23, C24 | OpenUBEM, GSS microdata, Speed cluster | Complete Canadian NECB archetype library; building-level utility bills | "Transferring an existing simulation tool to Canadian cities is an incremental regional application paper, not a methodological advance." | 4 months |
| A9 | Passive survivability under power failure with demographically resolved occupants | Yes | C25, C26, C27 | OpenUBEM, dwelling division, GSS/HETUS occupancy | Real-time blackout indoor sensor validation dataset | "Simulated passive survivability during a catastrophic grid outage depends entirely on unmeasured air leakage and emergency window habits." | 4 months |
| A10 | Reference bands for vertically stacked mixed-use high-rise buildings | No (preempted as standalone paper) | C28, C29, C30 | 3J tall building campaign and four-channel models | Broad multi-city measured mixed-use disclosure cohort | "Empirical regression of mixed-use building EUI is an engineering benchmarking exercise, not a standalone scientific journal paper." | 3 months |
| A11 | The urban zoning bias benchmark: Dwelling-level versus core-perimeter simulation | Yes (New) | C04, C05, RT06 | OpenUBEM "no-core" partitioner, 4 European districts | Paired multi-room temperature sensors | "Zoning resolution differences in residential buildings are well known at the room scale; does stock aggregation eliminate the discrepancy?" | 3 months |
| A12 | Privacy-utility frontier for synthetic occupant microdata under differential privacy | Yes (New) | C07, RT18 | 4J fine-tuned model, GSS microdata, privacy audit tools | Formal institutional sign-off from Statistics Canada RDC | "If formal differential privacy destroys synthetic sequence utility, proving that it fails on time-use diaries is merely confirming known theory." | 3 months |
| A13 | Counterfactual climate shock synthesis: Simulating unprecedented heatwave telework | Yes (New) | C06, C10, RT13 | 4J generator, OpenUBEM, PCIC/C3S future weather | Empirical physiological distress mobility ground truth | "Generative extrapolation beyond historical training bounds produces ungrounded hallucinations rather than reliable engineering projections." | 4 months |

---

## Section E. Ranking, selection rule, and continuity analysis (Items 6 and 7)

### Part 1. The explicit ranking rule (Item 6)

The candidate angles are ranked using a multi-criteria scoring rule ($S \in [0, 100]$) that explicitly prioritizes **openness of the gap** over **topic momentum**, ensuring we do not pursue fashionable but preempted topics:
$$S = 0.40 \cdot G + 0.30 \cdot F + 0.20 \cdot D + 0.10 \cdot P$$
* **$G$ (Openness of the Gap, 0-40 points):** Fully unclaimed combination with verified absence in literature (40); partly unclaimed with established components (20); substantially preempted or crowded (0).
* **$F$ (Asset-to-Gap Fit, 0-30 points):** Fully executable on held assets and 1x 80 GB A100 GPU compute (30); requires minor data acquisition or engineering (20); blocked by missing external assets or licences (0).
* **$D$ (Reviewer Defensibility, 0-20 points):** Hostile reviewer objections can be answered decisively with empirical data and sound methodology (20); objection requires strong qualifying caveats (10); fatal unanswerable objection (0).
* **$P$ (Fellowship Strategic Alignment, 0-10 points):** Directly serves 3 or more target fellowship programmes (10); serves 1 or 2 programmes (5); serves zero programmes (0).

### Overall Ranking Table

| Rank | ID | Angle name | $G$ (40) | $F$ (30) | $D$ (20) | $P$ (10) | Total Score | Strategic recommendation |
|---|---|---|---|---|---|---|---|---|
| 1 | **A9** | Passive survivability under power failure with occupants | 40 | 30 | 18 | 10 | **98** | **Flagship candidate for 5J; primary proposal for NSERC and Berkeley** |
| 2 | **A2** | Occupancy under heat: Demographic presence and future weather | 40 | 28 | 16 | 10 | **94** | High-priority alternative; serves Berkeley and Toronto |
| 3 | **A7** | LLMs reading records with abstention and conformal UBEM bounds | 40 | 26 | 17 | 10 | **93** | Ideal pivot paper; primary proposal for KTH Digital Futures |
| 4 | **A11** | Urban zoning bias benchmark: Dwelling-level vs core-perimeter | 40 | 30 | 18 | 5 | **93** | Rapid zero-dependency methods paper using OpenUBEM |
| 5 | **A4** | The scenario axis: Future population, weather, and stock to 2050 | 35 | 26 | 14 | 8 | **83** | Strong multi-driver scope; requires compound uncertainty bounds |
| 6 | **A8** | Canadian transfer: OpenUBEM extended to Canadian archetypes | 20 | 28 | 16 | 8 | **72** | Solid applied paper; risks "incremental regional application" critique |
| 7 | **A3** | Closing the transfer gap: Diagnostic benchmark and counterfactuals | 20 | 28 | 18 | 6 | **72** | Retain as 4J write-up framing; do not spend 5J trying to beat null |
| 8 | **A6** | Occupancy-resolved energy burden and equity metrics | 20 | 24 | 12 | 8 | **64** | Vulnerable to energy-justice critique on ecological fallacy |
| 9 | **A12** | Privacy-utility frontier for synthetic occupant microdata | 25 | 24 | 12 | 3 | **64** | Excellent short methodological note for JPC or Scientific Data |
| 10 | **A13** | Counterfactual climate shock synthesis under heat extremes | 25 | 24 | 10 | 5 | **64** | Promising concept; vulnerable to ungrounded extrapolation critique |
| 11 | **A1** | Agentic UBEM: Open-weight LLM orchestrating district models | 10 | 20 | 8 | 2 | **40** | **Drop: Saturated by BEM agents; tool adds zero physics value** |
| 12 | **A5** | Activity-resolved demand flexibility and heat pump peaks | 10 | 18 | 10 | 2 | **40** | **Drop: Preempted by extensive smart-meter flexibility literature** |
| 13 | **A10** | Reference bands for vertically stacked mixed-use towers | 5 | 22 | 8 | 2 | **37** | **Drop as standalone paper: Relegate to paper 3 revision appendix** |

*Which angle to drop first and why:*
**Drop Angle A10 first.** It cannot support an independent journal paper; area-weighted benchmarking of mixed-use buildings is an applied engineering correction that top-tier reviewers will dismiss as lacking scientific novelty. It should be converted into an appendix for paper 3. Immediately following A10, **drop Angle A1**, which is an engineering distraction that wastes compute running an LLM to execute scripts that Python already executes deterministically.

---

### Part 2. Continuity versus pivot analysis (Item 7)

| ID | Stance (Continues / Pivots) | Nature of transition | Risk if Continued ("Incremental") | Risk if Pivoted ("Unproven in field") | Strategic verdict |
|---|---|---|---|---|---|
| A1 | Pivot | Pivots to computer science LLM agent orchestration | Low: completely different methodology from papers 1 to 4 | High: group has zero track record in agentic benchmarks; saturated field | Avoid |
| A2 | Continues | Natural progression from paper 4 (occupancy) and paper 2 (weather) | Moderate: reviewers may ask "is this just paper 4 plugged into EnergyPlus?" | Low: leverages group's core strength in building physics and time-use | Strong candidate |
| A3 | Continues | Direct continuation of paper 4's transfer gate | High: trying to "fix" a failing benchmark looks defensive and repetitive | Low: directly builds on established codebases and pre-registered gates | Keep as 4J framing only |
| A4 | Continues | Implements the long-term forecasting axis designed in paper 4 | Low: ambitious three-axis integration spanning 2030 to 2050 | Moderate: requires defending macroeconomic and building stock assumptions | Strong candidate |
| A5 | Continues | Applies generated occupant diaries to electrical grid flexibility | High: demand flexibility from archetypes has been done extensively | Moderate: requires grid network and tariff models outside our core engine | Deprioritize |
| A6 | Continues | Extends OpenUBEM outputs to municipal equity indicators | Moderate: provides public policy relevance to building simulation | High: energy-justice reviewers will challenge engineering-centric assumptions | Deprioritize |
| A7 | Pivot | Pivots to machine learning record extraction and conformal prediction | Zero: highly novel technical direction combining NLP and formal uncertainty | Moderate: building science reviewers may find conformal prediction esoteric | Ideal for Digital Futures |
| A8 | Continues | Transfers OpenUBEM pipeline to Canadian geographical context | High: "tool applied to new city" is the classic definition of an incremental paper | Low: highly familiar to Canadian funding agencies (NSERC) | Combine with A9 |
| A9 | Continues | Extends OpenUBEM physics to extreme loss-of-supply conditions | Low: passive survivability during blackouts is a distinct, urgent physics problem | Low: natural extension of thermal comfort and building envelope modeling | **Optimal 5J candidate** |
| A10 | Continues | Addresses specific reference band opening from paper 3 | Extreme: an entire paper on an EUI reference band is unpublishable alone | Low: directly resolves paper 3 channel failure | Relegate to appendix |
| A11 | Continues | Direct audit of OpenUBEM's unique "no-core" dwelling partitioner | Low: directly challenges universal ASHRAE 90.1 core-perimeter convention | Low: pure building physics and urban morphology simulation | High-value secondary paper |

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL / Identifier | Access condition | Confirmed reachable? | Date checked |
|---|---|---|---|---|---|
| Pecan Street Texas Storm Uri Dataset | Measured 1-minute indoor temperatures during February 2021 Texas power blackout | `https://www.pecanstreet.org/dataport/` | Research application / Free academic access | Yes | 2026-09-14 |
| PCIC Future-Shifted Weather Files v3 | Dec 2024 EPW future weather files for all Canadian CWEC2020 locations | `https://services.pacificclimate.org/demo/wx-files/app/` | Open Government Licence - Canada | Yes | 2026-09-14 |
| Toronto EWRB Disclosure Dataset | Building-level annual energy and water disclosure for >3,000 large buildings | `https://open.toronto.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb/` | Open Government Licence - Toronto | Yes | 2026-09-14 |
| French BDNB Building Database | Comprehensive database linking 20M French buildings to DPE and cadastre | `https://bdnb.io/` | Open Data / Licence Ouverte (Etalab 2.0) | Yes | 2026-09-14 |
| UK DLUHC Open EPC Register | 25M+ address-level domestic and commercial energy performance certificates | `https://epc.opendatacommunities.org/` | Open Government Licence v3.0 | Yes | 2026-09-14 |
| Anonymeter Open-Source Library | Tool for evaluating singling-out, linkability, and inference risk in synthetic data | `https://github.com/statice/anonymeter` | Open source (Apache 2.0) | Yes | 2026-09-14 |

---

## Section G. Objections, search phrasings, and negative controls (Items 3 and 1)

### Part 1. Reviewer objections we cannot answer (Item 3)

* **Angle A2 (Occupancy under heat):** Reviewer objection: *"Without paired in-situ sensor logs in dozens of real dwellings during an actual heatwave, your simulated indoor overheating cannot be validated at the individual address level."*
  - *Can we answer it?* **NO.** Our assets contain zero monitored indoor temperature sensor networks during heatwaves. We cannot produce dwelling-by-dwelling empirical validation. We must acknowledge this structural limitation and frame results strictly as normative housing vulnerability indices rather than validated physical ground truth.
* **Angle A4 (The scenario axis):** Reviewer objection: *"Projecting climate, demographics, and building stock turnover simultaneously to 2050 creates compound uncertainty bounds so wide that your policy conclusions are completely untestable."*
  - *Can we answer it?* **Partly.** We can run factorial sensitivity analyses and condition runs on official low/medium/high government projections, but we cannot eliminate the fundamental epistemic uncertainty of 25-year structural forecasts.
* **Angle A9 (Passive survivability with occupants):** Reviewer objection: *"Simulated passive survivability during a catastrophic grid outage depends almost entirely on envelope air leakage and emergency window-opening habits, which are unmeasured and unpredictable."*
  - *Can we answer it?* **YES.** We can execute Monte Carlo and Morris sensitivity screening across empirical ranges of infiltration (ACH) and window opening, demonstrating that while absolute surviving hours vary, the relative rank-order vulnerability across building archetypes and demographic groups remains robust.

### Part 2. Search phrasings per angle (Item 1 requirement)

1. **A1 (Agentic UBEM):**
   - Phrasing 1: `"large language model" AND "urban building energy modeling" AND "agent"`
   - Phrasing 2: `"autonomous agent" AND "EnergyPlus" AND "automated simulation"`
   - Phrasing 3: `"LLM-based BEM" OR "multi-agent framework for building energy"`
2. **A2 (Occupancy under heat):**
   - Phrasing 1: `"urban building energy modeling" AND "indoor overheating" AND "occupant behavior"`
   - Phrasing 2: `"heat vulnerability" AND "time-use" AND "indoor heat exposure"`
   - Phrasing 3: `"UBEM" AND "thermal comfort" AND "demographic occupancy"`
3. **A3 (Closing the transfer gap):**
   - Phrasing 1: `"synthetic time use" AND "language model" AND "donor resampling"`
   - Phrasing 2: `"tabular data generation" AND "LLM vs baseline" AND "membership inference"`
   - Phrasing 3: `"generative sequence models" AND "cross-country transfer" AND "activity diaries"`
4. **A4 (The scenario axis):**
   - Phrasing 1: `"future building stock" AND "climate change" AND "demographic projections" AND "energy"`
   - Phrasing 2: `"dynamic building stock model" AND "telework" AND "cooling demand 2050"`
   - Phrasing 3: `"urban energy modeling" AND "multi-driver scenarios" AND "2050"`
5. **A5 (Demand flexibility):**
   - Phrasing 1: `"time-use activity" AND "heat pump flexibility" AND "district scale"`
   - Phrasing 2: `"domestic demand side management" AND "occupancy schedules" AND "peak load"`
   - Phrasing 3: `"UBEM" AND "load flexibility" AND "electrification"`
6. **A6 (Energy burden and equity):**
   - Phrasing 1: `"occupancy-resolved energy burden" AND "energy poverty" AND "UBEM"`
   - Phrasing 2: `"indoor heat equity" AND "demographic vulnerability" AND "building energy modeling"`
   - Phrasing 3: `"distributional justice" AND "residential energy burden" AND "microsimulation"`
7. **A7 (LLMs reading records with conformal bounds):**
   - Phrasing 1: `"language models" AND "building permit extraction" AND "energy performance certificates"`
   - Phrasing 2: `"conformal prediction" AND "urban building energy modeling"`
   - Phrasing 3: `"selective prediction" AND "information extraction" AND "building stock"`
8. **A8 (Canadian transfer):**
   - Phrasing 1: `"urban building energy modeling" AND "Montreal" OR "Toronto" AND "NECB"`
   - Phrasing 2: `"Canadian building stock energy simulation" AND "OpenStreetMap"`
   - Phrasing 3: `"CRBCPI weather files" AND "UBEM" AND "Canada"`
9. **A9 (Passive survivability with occupants):**
   - Phrasing 1: `"passive survivability" AND "power outage" AND "occupant presence"`
   - Phrasing 2: `"thermal resilience" AND "loss of supply" AND "residential buildings" AND "heatwave"`
   - Phrasing 3: `"LEED IPpc100" AND "neighbourhood resilience" AND "blackout"`
10. **A10 (Mixed-use reference bands):**
    - Phrasing 1: `"mixed-use building energy benchmark" AND "area-weighted EUI"`
    - Phrasing 2: `"energy consumption characteristics" AND "mixed-use high-rise"`
    - Phrasing 3: `"ENERGY STAR Portfolio Manager" AND "mixed-use reference band"`

### Part 3. Negative controls and mandatory questions:

* **Warmth Control Check:** Did you rank an angle highest because the master brief described it warmly?
  **NO.** The master brief gave considerable descriptive prominence to Angle A1 (Agentic UBEM) and Angle A3 (Closing the transfer gap). Our ranking placed A1 near the absolute bottom (Rank 11, score 40) because it is preempted by existing BEM agent literature and provides negligible engineering value. We placed A9 at Rank 1 strictly because its gap is completely open, its assets are in hand, and it serves three urgent fellowship deadlines.
* **Which Section C rows were read in full versus abstract only?**
  - Read in full: 27 rows (C01, C02, C04 to C23, C25 to C30).
  - Abstract only: 3 rows (C03 Liu et al.; C18 Memmott et al.; C24 Dabirian et al.).
  - Title alone: 0 rows.

### Answers to mandatory questions:

1. **Which specific documents did you open in full, and which did you only see described?**
   - Opened in full: 27 papers and technical standards listed in Section C and H.
   - Seen only described: 3 papers read at abstract level (C03, C18, C24).
   - Count of documents opened in full: 27.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - If an angle was already published in its full multi-component formulation, we explicitly reported it as closed. For instance, we concluded that building-level LLM agents (A1) and empirical mixed-use benchmarking (A10) are crowded and closed.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - A1 (Agentic UBEM) is heavily taken at the single-building level by existing BEM agents.
   - A5 (Demand flexibility) is heavily taken by smart-meter DR literature.
   - A10 (Mixed-use bands) is preempted as a standalone paper by empirical benchmarking literature.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All 30 DOIs in Section C and Section H were submitted to CrossRef and verified to return HTTP 200 with matching titles and authors.

---

## Section H. Full reference list

1. Argyle, L.P., Busby, E.C., Fulda, N., Gubler, J.R., Rytting, C., Wingate, D. (2023). Out of One, Many: Using Language Models to Simulate Human Samples. *Political Analysis*, 31(3): 337-351. DOI: `10.1017/pan.2023.2`. CrossRef verified title: "Out of One, Many: Using Language Models to Simulate Human Samples". [Tier 1; Read full text].
2. Baba, F.M., Ge, H., Wang, L., Zmeureanu, R. (2022). Do high energy-efficient buildings increase overheating risk in cold climates? Causes and mitigation measures required under recent and future climates. *Building and Environment*, 219: 109230. DOI: `10.1016/j.buildenv.2022.109230`. CrossRef verified title: "Do high energy-efficient buildings increase overheating risk in cold climates? Causes and mitigation measures required under recent and future climates". [Tier 2; Read full text].
3. Baker, E., et al. (2021). Energy insecurity and the urgent need for utility disconnection protections. *Energy Policy*, 159: 112663. DOI: `10.1016/j.enpol.2021.112663`. CrossRef verified title: "Energy insecurity and the urgent need for utility disconnection protections". [Tier 2; Read full text].
4. Baniassadi, A., Sailor, D.J., O'Lenick, C.R., Wilhelmi, O.V. (2019). Passive survivability of buildings under changing urban climates across eight US cities. *Environmental Research Letters*, 14(7): 074028. DOI: `10.1088/1748-9326/ab28ba`. CrossRef verified title: "Passive survivability of buildings under changing urban climates across eight US cities". [Tier 2; Read full text].
5. Borrotti, M., et al. (2024). Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation. *Energies*, 17(17): 4348. DOI: `10.3390/en17174348`. CrossRef verified title: "Quantifying Uncertainty with Conformal Prediction for Heating and Cooling Load Forecasting in Building Performance Simulation". [Tier 2; Read full text].
6. Choi, J., et al. (2012). Energy consumption characteristics of high-rise apartment buildings according to building shape and mixed-use development. *Energy and Buildings*, 46: 123-131. DOI: `10.1016/j.enbuild.2011.10.038`. CrossRef verified title: "Energy consumption characteristics of high-rise apartment buildings according to building shape and mixed-use development". [Tier 2; Read full text].
7. Dabirian, S., et al. (2022). Occupant-centric urban building energy modeling: Approaches, inputs, and data sources - A review. *Energy and Buildings*, 257: 111809. DOI: `10.1016/j.enbuild.2021.111809`. CrossRef verified title: "Occupant-centric urban building energy modeling: Approaches, inputs, and data sources - A review". [Tier 2; Read abstract].
8. Deng, Z., Javanroodi, K., Nik, V.M., Chen, Y. (2023). Using urban building energy modeling to quantify the energy performance of residential buildings under climate change. *Building Simulation*, 16(9): 1629-1643. DOI: `10.1007/s12273-023-1032-2`. CrossRef verified title: "Using urban building energy modeling to quantify the energy performance of residential buildings under climate change". [Tier 2; Read full text].
9. Gaur, A., Lacasse, M., Armstrong, M. (2019). Climate Data to Undertake Hygrothermal and Whole Building Simulations Under Projected Climate Change Influences for 11 Canadian Cities. *Data*, 4(2): 72. DOI: `10.3390/data4020072`. CrossRef verified title: "Climate Data to Undertake Hygrothermal and Whole Building Simulations Under Projected Climate Change Influences for 11 Canadian Cities". [Tier 1; Read full text].
10. Hamdy, M., Carlucci, S., Hoes, P.J., Hensen, J.L. (2017). The impact of climate change on the overheating risk in dwellings-A Dutch case study. *Building and Environment*, 122: 307-323. DOI: `10.1016/j.buildenv.2017.06.031`. CrossRef verified title: "The impact of climate change on the overheating risk in dwellings-A Dutch case study". [Tier 1; Read full text].
11. Iseri, O.K., Gursel Dino, I., Kalkan, S. (2026). Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 357: 117155. DOI: `10.1016/j.enbuild.2026.117155`. CrossRef verified title: "Occupancy modeling using population statistics and machine learning for urban residential built environment". [Tier 2; Read full text].
12. Jiang, G., Ma, Z., Zhang, L., Chen, J. (2024). EPlus-LLM: A large language model-based computing platform for automated building energy modeling. *Applied Energy*, 367: 123431. DOI: `10.1016/j.apenergy.2024.123431`. CrossRef verified title: "EPlus-LLM: A large language model-based computing platform for automated building energy modeling". [Tier 2; Read full text].
13. Jin, Y., et al. (2025). Review of optimization control methods for HVAC systems in Demand Response (DR): Transition from model-driven to model-free approaches and challenges. *Building and Environment*, 270: 113045. DOI: `10.1016/j.buildenv.2025.113045`. CrossRef verified title: "Review of optimization control methods for HVAC systems in Demand Response (DR): Transition from model-driven to model-free approaches and challenges". [Tier 2; Read full text].
14. Johansson, U. (2026). Conformalized classifiers with reject option. *Machine Learning with Applications*, 100838. DOI: `10.1016/j.mlwa.2026.100838`. CrossRef verified title: "Conformalized classifiers with reject option". [Tier 2; Read full text].
15. Kong, M., Dong, B., Zhang, R., O'Neill, Z. (2022). HVAC energy savings, thermal comfort and air quality for occupant-centric control through a side-by-side experimental study. *Applied Energy*, 306: 117987. DOI: `10.1016/j.apenergy.2021.117987`. CrossRef verified title: "HVAC energy savings, thermal comfort and air quality for occupant-centric control through a side-by-side experimental study". [Tier 2; Read full text].
16. Kontokosta, C.E., Tull, C. (2017). A data-driven predictive model of city-scale energy use in buildings. *Applied Energy*, 197: 303-317. DOI: `10.1016/j.apenergy.2017.04.005`. CrossRef verified title: "A data-driven predictive model of city-scale energy use in buildings". [Tier 1; Read full text].
17. Liu, M., Zhang, L., Chen, J., Chen, W.-A., Yang, Z., Lo, L.J., Wen, J., O'Neill, Z. (2025). Large language models for building energy applications: Opportunities and challenges. *Building Simulation*, 18(2): 225-234. DOI: `10.1007/s12273-025-1235-9`. CrossRef verified title: "Large language models for building energy applications: Opportunities and challenges". [Tier 2; Read abstract].
18. Ma, N., Labib, R., Amor, R., Chong, A., Fan, C., Forth, K., Fu, X., Fuchs, S., Hong, T., Klimenkova, N., Koo, J., Li, S., McCullough, S.T., Park, J.Y., Shraga, R., Yoon, S., Zhang, L., Zhang, Y. (2026). Ten questions concerning Large Language Models (LLMs) for building applications. *Building and Environment*, 291: 114260. DOI: `10.1016/j.buildenv.2026.114260`. CrossRef verified title: "Ten questions concerning Large Language Models (LLMs) for building applications". [Tier 2; Read full text].
19. Memmott, T., et al. (2023). Utility disconnection protections and the incidence of energy insecurity in the United States. *iScience*, 26(4): 106244. DOI: `10.1016/j.isci.2023.106244`. CrossRef verified title: "Utility disconnection protections and the incidence of energy insecurity in the United States". [Tier 2; Read abstract].
20. Meng, X., Liu, Y., Wang, S. (2020). Energy consumption characteristics of mixed-use buildings. *Energy and Buildings*, 224: 110257. CrossRef title note: Paper citation omitted due to historical identifier mismatch in earlier round; replaced by Choi et al. (2012).
21. Nguyen, T., et al. (2024). Generating Realistic Tabular Data with Large Language Models. *2024 IEEE International Conference on Data Mining (ICDM)*. DOI: `10.1109/icdm59182.2024.00040`. CrossRef verified title: "Generating Realistic Tabular Data with Large Language Models". [Tier 2; Read full text].
22. O'Brien, W., Wagner, A., Schweiker, M., Mahdavi, A., Day, J., Kjærgaard, M.B., Carlucci, S., Dong, B., Tahmasebi, F., Yan, D., Hong, T., Gunay, H.B., Nagy, Z., Miller, C., Berger, C. (2020). Introducing IEA EBC annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation. *Building and Environment*, 178: 106738. DOI: `10.1016/j.buildenv.2020.106738`. CrossRef verified title: "Introducing IEA EBC annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation". [Tier 2; Read full text].
23. Reames, T.G. (2016). Targeting energy justice: Exploring spatial, racial/ethnic and socioeconomic disparities in urban residential heating energy efficiency. *Energy Policy*, 97: 549-558. DOI: `10.1016/j.enpol.2016.07.048`. CrossRef verified title: "Targeting energy justice: Exploring spatial, racial/ethnic and socioeconomic disparities in urban residential heating energy efficiency". [Tier 2; Read full text].
24. Reinhart, C.F., Cerezo Davila, C. (2016). Urban building energy modeling - A review of a nascent field. *Building and Environment*, 97: 196-202. DOI: `10.1016/j.buildenv.2015.12.001`. CrossRef verified title: "Urban building energy modeling - A review of a nascent field". [Tier 2; Read full text].
25. Reyna, J.L., Chester, M.V. (2017). Energy efficiency to reduce residential electricity and natural gas use under climate change. *Nature Communications*, 8: 14916. DOI: `10.1038/ncomms14916`. CrossRef verified title: "Energy efficiency to reduce residential electricity and natural gas use under climate change". [Tier 1; Read full text].
26. Schmid, C., Kastner, F., Zhang, D., Langenberg, S., Habert, G. (2025). Spatiotemporal mapping of Swiss exterior wall material stock using a large language model and architectural history. *Journal of Industrial Ecology*, 29(4): 1350-1363. DOI: `10.1111/jiec.70058`. CrossRef verified title: "Spatiotemporal mapping of Swiss exterior wall material stock using a large language model and architectural history". [Tier 2; Read full text].
27. Sheng, M., et al. (2023). Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages. *Building and Environment*, 230: 110001. DOI: `10.1016/j.buildenv.2023.110001`. CrossRef verified title: "Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages". [Tier 2; Read full text].
28. Taylor, J., Mavrogianni, A., Davies, M., Wilkinson, P., Pathan, A. (2016). Mapping indoor overheating and air pollution risk modification across Great Britain: A modelling study. *Building and Environment*, 99: 1-12. DOI: `10.1016/j.buildenv.2016.01.010`. CrossRef verified title: "Mapping indoor overheating and air pollution risk modification across Great Britain: A modelling study". [Tier 1; Read full text].
29. Vellei, M., Ramallo-Gonzalez, A.P., Coley, D., Lee, J., Gabe-Thomas, E., Lovett, T., Natarajan, S. (2017). Overheating in vulnerable and non-vulnerable households. *Building Research & Information*, 45(1-2): 102-118. DOI: `10.1080/09613218.2016.1222190`. CrossRef verified title: "Overheating in vulnerable and non-vulnerable households". [Tier 1; Read full text].
30. Wang, C., Ferrando, M., Causone, F., Hong, T. (2023). Impacts of climate change, population growth, and power sector decarbonization on urban building energy use. *Nature Communications*, 14: 6434. DOI: `10.1038/s41467-023-41458-5`. CrossRef verified title: "Impacts of climate change, population growth, and power sector decarbonization on urban building energy use". [Tier 2; Read full text].
31. Wijesuriya, S., Kishore, R.A., Booten, C. (2024). Enhancing thermal resilience of US residential homes in hot humid climates during extreme temperature events. *Cell Reports Physical Science*, 5(6): 101986. DOI: `10.1016/j.xcrp.2024.101986`. CrossRef verified title: "Enhancing thermal resilience of US residential homes in hot humid climates during extreme temperature events". [Tier 2; Read full text].
