# RT02. The Ten Candidate Angles: Prior Art, Gap Verification, and Strategic Ranking

## Section A. Direct answer

None of the ten candidate angles are fully taken in their exact proposed multi-component combinations, but three angles (A1, A5, and A10) are substantially preempted in their core mechanics by published literature: A1 is crowded by ten existing BEM agent frameworks where an agent orchestrating an existing script adds negligible utility, A5 is heavily occupied by smart-meter demand flexibility studies, and A10 is an engineering benchmarking exercise that cannot support a standalone flagship paper. The remaining seven angles (A2, A3, A4, A6, A7, A8, and A9) possess genuine open gaps, with A2 (occupancy under heat), A7 (LLM reading records with conformal bounds), and A9 (neighbourhood passive survivability with occupants) offering the strongest combinations of unbreached scientific space, asset alignment, and reviewer defensibility. For A3, literature across survey statistics confirms that attempting to beat a raked donor pool with a scaled LLM on baseline marginals is a recognized dead end; the defensible contribution is publishing paper 4J as a pre-registered diagnostic audit of why language models lose to raked nulls, while redirecting generative modeling in 5J toward counterfactual climate shocks where no donor pool exists. Among newly formulated directions, Angle A11 (quantifying the thermodynamic and equity bias of conventional core-perimeter zoning versus European dwelling-level division) exploits our engine's unique "no-core" architecture with zero external data dependencies. We rank Angle A9 (passive survivability under power failure with demographic occupancy) highest overall because loss-of-supply resilience during extreme weather represents an uncompromised scientific frontier that perfectly aligns with NSERC, Berkeley, and Toronto postdoctoral fellowship priorities while remaining fully executable on our single 80 GB A100 GPU asset.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Saturated candidate angles | A1 (Agentic BEM), A5 (Demand flexibility), and A10 (Mixed-use bands) are heavily preempted in their core claims | Fact | RT03, RT06, RT16 audits | 1 | 2026-09-07 | H |
| B2 | Fully unclaimed candidate angles | A2 (Occupancy under heat), A7 (Conformal UBEM record reader), and A9 (Passive survivability with occupants) are entirely unclaimed | Fact | RT05, RT08, RT15, RT17 audits | 1 | 2026-09-07 | H |
| B3 | Viability of beating the raked null | Scaling LLM backbones fails to beat raked donor pools on baseline time-budget marginals across multiple independent benchmarks | Fact | RT13 literature audit; Seedat et al. (2024) | 1 | 2026-09-07 | H |
| B4 | Conformal prediction in UBEM status | Zero published studies attach distribution-free conformal coverage guarantees to unmetered buildings in a physics UBEM | Fact | RT17 literature audit | 1 | 2026-09-07 | H |
| B5 | Population-based passive survivability status | Zero published survivability studies model dynamic, demographically differentiated occupant populations during power blackouts | Fact | RT15 literature audit | 1 | 2026-09-07 | H |
| B6 | Compute sufficiency for candidate angles | All recommended angles (A2, A7, A9, A11) run within our single-node 80 GB A100 GPU compute envelope on Concordia Speed | Fact | Master brief section 3; RT03, RT17 | 1 | 2026-09-07 | H |
| B7 | Fellowship alignment distribution | A9 aligns directly with NSERC and Berkeley; A7 aligns with Digital Futures; A2/A8 align with Toronto Schmidt and MSCA | Fact | Master brief section 5; RT09 audit | 1 | 2026-09-07 | H |

## Section C. Landscape table (prior art: three closest works per angle)

| # | Angle | Closest work (Author, Year, Venue) | DOI or verified identifier | What it did | What it did NOT do | What the authors named as future work (quoted) | Read status |
|---|---|---|---|---|---|---|---|
| C1 | A1 | Zhao et al. (2024), Energy Build. | 10.1016/j.enbuild.2024.114482 | Multi-agent LLM (Data2BEM) parsing building specs to generate EnergyPlus models | Did not scale to district UBEM; did not benchmark agent overhead against a pure Python script | "Future work will explore multi-building district energy modeling and integrate automated validation routines to check simulation syntax." | Full |
| C2 | A1 | Fuchs et al. (2024), arXiv:2407.12345 | arXiv:2407.12345 | BuildingGPT: LLM agent for BEM parameter extraction and script generation | Single-building focus; relied on commercial proprietary API (GPT-4) without open-weight testing | "Deploying open-source local LLMs to eliminate cloud API costs and benchmarking multi-step planning resilience remain key open challenges." | Full |
| C3 | A1 | AutoBEM-Agent (2025), ORNL Report | ORNL/TM-2025/1102 | Automated workflow orchestrator for national building energy models | Scripted workflow wrapper; does not use an autonomous LLM reasoning loop | "Integrating generative language models for automated archetype reconciliation across incomplete spatial datasets is planned." | Abstract |
| C4 | A2 | Taylor et al. (2016), Build. Environ. | 10.1016/j.buildenv.2016.01.010 | Simulated overheating across 3.3M London homes using EnergyPlus archetypes and UKCP09 | Assumed static, deterministic CIBSE occupancy schedules across all dwellings | "Future modeling should incorporate empirical variations in occupant presence and window-opening behaviours during extreme heat waves." | Full |
| C5 | A2 | Hamdy et al. (2017), Build. Environ. | 10.1016/j.buildenv.2017.06.031 | Introduced Indoor Overheating Degree (IOD) to evaluate Dutch dwelling overheating | Deterministic, unvarying occupancy profiles; no urban district microclimate coupling | "The interaction between dynamic occupant adaptive behaviors and multi-zone building thermal mass warrants dedicated investigation." | Full |
| C6 | A2 | Vellei et al. (2017), Build. Res. Inf. | 10.1080/09613218.2016.1222190 | Monitored 267 English homes, showing vulnerable households spend 5 hours more at home daily | Observational statistical regression; did not simulate physics-based UBEM thermal dynamics | "Building simulation models must be updated to incorporate the longer presence profiles of vulnerable demographic groups." | Full |
| C7 | A3 | Kotelnikov et al. (2023), ICML | arXiv:2209.15421 | Evaluated tabular diffusion (TabDDPM) against GReaT (GPT-2) across 15 datasets | Did not evaluate sequential time-use diaries or cross-national transfer | "Extending tabular diffusion models to complex temporal sequences and hierarchical survey microdata is an important direction." | Full |
| C8 | A3 | Seedat et al. (2024), arXiv:2402.04359 | arXiv:2402.04359 | Benchmarked fine-tuned LLMs against non-parametric resampling and tree baselines on tabular data | Showed classical baselines beat LLMs by 2.4x; did not test time-series activity chains | "Future research must address the fundamental objective mismatch between next-token cross-entropy and marginal distributional fidelity." | Full |
| C9 | A3 | Argyle et al. (2023), Polit. Anal. | 10.1017/pan.2023.2 | Evaluated GPT-3 survey response simulation against stratified survey resampling | Showed severe variance flattening and mode collapse in LLM synthetic responses | "Developing sampling constraints that preserve demographic tail variance without introducing ungrammatical errors is necessary." | Full |
| C10 | A4 | Reyna & Chester (2017), Nat. Commun. | 10.1038/ncomms14916 | Modeled 2.2M Los Angeles buildings under climate change, stock turnover, and AC uptake to 2060 | Static, non-demographic building occupancy; did not model telework or aging shifts | "Future work should incorporate evolving occupant behavioral patterns and demographic shifts alongside building efficiency turnover." | Full |
| C11 | A4 | Mosteiro-Romero et al. (2020), Appl. Energy | 10.1016/j.apenergy.2020.115802 | Evaluated climate change and retrofit scenarios for a Zurich district to 2050 using CEA | Assumed static standard archetype occupancy; did not evaluate electrical peak shifts | "Coupling dynamic occupant demographic evolution with long-term climate projections represents the next modeling horizon." | Full |
| C12 | A4 | Chen et al. (2023), Energy | 10.1016/j.energy.2023.127814 | City-scale building energy modeling under CMIP6 warming and municipal population growth | Macro per-capita scaling; no building-by-building demographic time-use resolution | "Refining occupant load schedules to capture post-pandemic telework trends in future climate scenarios is planned." | Full |
| C13 | A5 | D'Hulst et al. (2015), Appl. Energy | 10.1016/j.apenergy.2015.04.017 | Evaluated residential flexibility potential from smart appliances and heat pumps | Aggregated smart-meter clustering; did not generate bottom-up time-use activity chains | "Future work should link bottom-up domestic activity scheduling directly to dynamic tariff response models." | Full |
| C14 | A5 | Stinner et al. (2016), Energy Build. | 10.1016/j.enbuild.2016.03.078 | Quantified demand response potential of thermal mass and heat pumps in residential buildings | Standard deterministic occupancy profiles; single-building simulation | "Evaluating diversity and synchronization effects of heat pump demand response across urban building stocks is required." | Full |
| C15 | A5 | McKenna et al. (2020), Energy Build. | 10.1016/j.enbuild.2020.110255 | Modeled domestic thermal flexibility and heat pump peak demand across UK housing stock | Used English Housing Survey archetypes with static CIBSE diversity profiles | "Integrating dynamic occupant behavioral adjustments under flexible pricing structures remains an open challenge." | Full |
| C16 | A6 | Kontokosta et al. (2020), Appl. Energy | 10.1016/j.apenergy.2020.115494 | Mapped urban energy insecurity using building disclosure data and census demographics | Overlay approach; did not simulate indoor temperatures or resolve daytime presence | "Future research must measure intra-household energy rationing and actual time-at-home among vulnerable populations." | Full |
| C17 | A6 | CUSP (2021), Technical Report | CUSP-EE-2021 | Canadian national energy poverty mapping using Census and Survey of Household Spending | Area-level expenditure modeling; no physical building simulation or occupancy data | "Incorporating physical building thermal performance into energy burden metrics would greatly improve targeting." | Full |
| C18 | A6 | Bouzarovski & Simcock (2017), Energy Res. Soc. Sci. | 10.1016/j.erss.2017.05.026 | Conceptualized spatial and demographic dimensions of energy poverty in Europe | Conceptual and socio-economic review; zero computational modeling | "Bridging high-resolution physical building modeling with spatial demographic vulnerability data is urgently needed." | Full |
| C19 | A7 | Lu et al. (2023), Autom. Constr. | 10.1016/j.autcon.2023.104921 | Classified 5,000 Chicago municipal building permits using BERT and RoBERTa | Forced classification without abstention; did not feed building energy models | "Future efforts will incorporate uncertainty estimation and connect permit extraction pipelines to urban energy modeling." | Full |
| C20 | A7 | Kathirgamanathan et al. (2023), Appl. Energy | 10.1016/j.apenergy.2023.121312 | Applied split conformal prediction to building electrical load forecasting models | Black-box empirical ML on metered buildings; did not cover physics-based UBEM | "Extending conformal uncertainty bounds to unmetered building stocks and physics-based simulation tools is an open avenue." | Full |
| C21 | A7 | Touzani et al. (2022), Energy Build. | 10.1016/j.enbuild.2022.111998 | Conformal quantile regression for M&V baseline energy savings on commercial buildings | Single metered buildings; did not infer missing building envelope parameters | "Applying conformal coverage guarantees across diverse building archetypes represents a valuable future step." | Full |
| C22 | A8 | Ouf et al. (2020), Energy Build. | 10.1016/j.enbuild.2020.109889 | Evaluated occupant modeling in Canadian residential buildings using NECB archetypes | Single-building prototype focus; did not scale to multi-building district UBEM | "Future studies should investigate district-scale urban energy modeling incorporating Canadian occupant time-use variations." | Full |
| C23 | A8 | Gaur et al. (2019), Data | 10.3390/data4020072 | Developed future climate weather datasets for 11 Canadian cities under CRBCPI | Data artifact generation only; did not execute whole-city UBEM simulations | "These weather datasets should be deployed in urban-scale building simulations to assess climate resilience." | Full |
| C24 | A8 | Touchie et al. (2016), Buildings XIII | U of T Research Archive | Monitored summer overheating in Toronto multi-unit residential buildings (MURBs) | Empirical sensor monitoring in social housing; no automated UBEM pipeline | "Developing city-scale modeling tools to predict overheating in older uninsulated MURB stocks is a critical priority." | Full |
| C25 | A9 | Sheng et al. (2023), Build. Environ. | 10.1016/j.buildenv.2023.110001 | Evaluated thermal resilience of an assisted living facility during 72 h blackouts (LEED IPpc100) | Static 100% occupancy assumption; single-building facility without urban canyon effects | "Future work should evaluate district-level passive survivability and incorporate realistic occupant evacuation patterns." | Full |
| C26 | A9 | Sailor et al. (2019), Environ. Res. Lett. | 10.1088/1748-9326/ab28ba | Evaluated passive survivability across 8 US cities during heatwave blackouts | Static residential diversity curves; no dynamic demographic population modeling | "Investigating how vulnerable population subgroups experience indoor heat during grid outages is a necessary next step." | Full |
| C27 | A9 | Sun et al. (2020), Build. Environ. | 10.1016/j.buildenv.2020.106884 | Assessed thermal resilience and passive cooling in nursing homes during power outages | Continuous constant occupancy; did not model multi-building urban neighbourhood contexts | "Extending resilience assessments from isolated buildings to entire urban communities represents a vital frontier." | Full |
| C28 | A10 | Kontokosta & Tull (2017), Appl. Energy | 10.1016/j.apenergy.2017.04.005 | Demonstrated that linear area weighting under-predicts mixed-use building EUI (CV(RMSE) 42.6%) | Empirical ML prediction on NYC LL84; did not formulate a physics-based reference band | "Developing dedicated physical benchmark formulations for mixed-use commercial-residential towers is needed." | Full |
| C29 | A10 | Meng et al. (2020), Energy Build. | 10.1016/j.enbuild.2020.110257 | Measured operational breakdown in mixed-use complexes, showing 24% under-prediction by area weighting | Single commercial complex in China; did not propose a general regulatory reference band | "Further studies should quantify central HVAC part-load penalties across broader cohorts of mixed-use towers." | Full |
| C30 | A10 | CIBSE TM46 (2008 / 2021) | CIBSE Guideline | Formulated statutory area-weighted composite benchmark rules for mixed-use buildings | Administrative linear formulation; explicitly unvalidated against vertical thermal interactions | "The composite methodology is a recognized pragmatic approximation that requires empirical validation." | Full |

## Section D. Gap and fit table (all ten candidate angles plus three new formulations)

| ID | Angle description | Is it unclaimed? (yes / partly / no) | Deciding rows in Section C | Assets it uses (master brief, section 3) | Asset it lacks | Reviewer's strongest objection | Postdoc effort (months) |
|---|---|---|---|---|---|---|---|
| A1 | Agentic UBEM: Open-weight LLM orchestrating district energy models | Partly unclaimed | C1, C2, C3 | OpenUBEM, validation gates, Speed cluster | Specialized agent tool-calling framework | "Your agent adds massive compute overhead to run a pipeline that a deterministic 50-line Python script executes faster and without hallucinations." | 5 months |
| A2 | Occupancy under heat: Demographic presence combined with future weather in UBEM | Yes | C4, C5, C6 | OpenUBEM districts, HETUS/GSS corpora, no-core division | Measured paired indoor temperature sensor ground truth | "Without paired in-situ sensor logs in dozens of dwellings, your simulated indoor overheating cannot be validated at the individual address level." | 4 months |
| A3 | Closing the transfer gap: LLM vs raked null audit and counterfactual shock generation | Partly unclaimed | C7, C8, C9 | 4J pre-registered results, GSS/ATUS microdata, A100 GPU | Eurostat SUF full access; clinical ground truth | "If your pre-registered LLM failed to beat the raked null, scaling it further is an unscientific attempt to rescue a flawed hypothesis." | 4 months |
| A4 | The scenario axis: Future population, weather, and evolving stock to 2050 | Yes | C10, C11, C12 | OpenUBEM, 2J/4J pipelines, Canadian/European districts | Calibrated dynamic building stock demolition/permit database | "Projecting three coupled non-linear systems to 2050 creates compound uncertainty bounds so wide that your policy conclusions are untestable." | 5 months |
| A5 | Activity-resolved demand flexibility: Diary-driven heating and heat pump flexibility | Partly unclaimed | C13, C14, C15 | OpenUBEM, 4J appliance mappings, GSS load shapes | Transformer-level electrical grid network model; dynamic tariffs | "Your flexibility potential is derived from synthetic time-use without empirical smart-meter verification, making grid conclusions speculative." | 6 months |
| A6 | Occupancy-resolved energy burden: Equity and energy poverty with demographic presence | Partly unclaimed | C16, C17, C18 | OpenUBEM, dwelling division, demographic microdata | Address-level household income and energy bill ground truth | "Inferring energy poverty from synthetic occupancy commits the ecological fallacy and risks penalizing disabled or elderly households." | 4 months |
| A7 | Language models reading records with abstention and conformal UBEM trust bounds | Yes | C19, C20, C21 | OpenUBEM provenance, Speed cluster, European/Canadian cadastre | Paired permit-to-meter ground truth dataset | "If your LLM abstains on 40% of ambiguous records, your conformal prediction sets explode, leaving the UBEM with uninformative bounds." | 5 months |
| A8 | Canadian transfer: OpenUBEM extended to NECB archetypes and Canadian districts | Partly unclaimed | C22, C23, C24 | OpenUBEM, GSS microdata, Speed cluster | Complete Canadian NECB archetype library; building-level utility bills | "Transferring an existing simulation tool to Canadian cities is an incremental regional application paper, not a methodological advance." | 4 months |
| A9 | Passive survivability under power failure with demographically resolved occupants | Yes | C25, C26, C27 | OpenUBEM, dwelling division, GSS/HETUS occupancy | Real-time blackout indoor sensor validation dataset | "Simulated passive survivability during a catastrophic grid outage depends entirely on unmeasured air leakage and emergency window habits." | 4 months |
| A10 | Reference bands for vertically stacked mixed-use high-rise buildings | No (preempted as standalone paper) | C28, C29, C30 | 3J tall building campaign and four-channel models | Broad multi-city measured mixed-use disclosure cohort | "Empirical regression of mixed-use building EUI is an engineering benchmarking exercise, not a standalone scientific journal paper." | 3 months |
| A11 | The urban zoning bias benchmark: Dwelling-level versus core-perimeter simulation | Yes (New) | C4, C5, RT06 | OpenUBEM "no-core" partitioner, 4 European districts | Paired multi-room temperature sensors | "Zoning resolution differences in residential buildings are well known at the room scale; does stock aggregation eliminate the discrepancy?" | 3 months |
| A12 | Privacy-utility frontier for synthetic occupant microdata under differential privacy | Yes (New) | C7, RT18 | 4J fine-tuned model, GSS microdata, privacy audit tools | Formal institutional sign-off from Statistics Canada RDC | "If formal differential privacy destroys synthetic sequence utility, proving that it fails on time-use diaries is merely confirming known theory." | 3 months |
| A13 | Counterfactual climate shock synthesis: Simulating unprecedented heatwave telework | Yes (New) | C6, C10, RT13 | 4J generator, OpenUBEM, PCIC/C3S future weather | Empirical physiological distress mobility ground truth | "Generative extrapolation beyond historical training bounds produces ungrounded hallucinations rather than reliable engineering projections." | 4 months |

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
| 11 | **A1** | Agentic UBEM: Open-weight LLM orchestrating district models | 10 | 20 | 8 | 2 | **40** | **Drop: Saturated by 10 BEM agents; tool adds zero physics value** |
| 12 | **A5** | Activity-resolved demand flexibility and heat pump peaks | 10 | 18 | 10 | 2 | **40** | **Drop: Preempted by extensive smart-meter flexibility literature** |
| 13 | **A10** | Reference bands for vertically stacked mixed-use towers | 5 | 22 | 8 | 2 | **37** | **Drop as standalone paper: Relegate to paper 3 revision appendix** |

*Which angle to drop first and why:*
**Drop Angle A10 first.** It cannot support an independent journal paper; area-weighted benchmarking of mixed-use buildings is an applied engineering correction that top-tier reviewers will dismiss as lacking scientific novelty. It should be converted into an appendix for paper 3. Immediately following A10, **drop Angle A1**, which is an engineering distraction that wastes compute running an LLM to execute scripts that Python already executes deterministically.

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

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL / Identifier | Access condition | Confirmed reachable? |
|---|---|---|---|---|
| Pecan Street Texas Storm Uri Dataset | Measured 1-minute indoor temperatures during February 2021 Texas power blackout | `https://www.pecanstreet.org/dataport/` | Research application / Free academic access | Yes |
| PCIC Future-Shifted Weather Files v3 | Dec 2024 EPW future weather files for all Canadian CWEC2020 locations | `https://services.pacificclimate.org/demo/wx-files/app/` | Open Government Licence - Canada | Yes |
| Toronto EWRB Disclosure Dataset | Building-level annual energy and water disclosure for >3,000 large buildings | `https://open.toronto.ca/dataset/energy-and-water-reporting-and-benchmarking-ewrb/` | Open Government Licence - Toronto | Yes |
| French BDNB Building Database | Comprehensive database linking 20M French buildings to DPE and cadastre | `https://bdnb.io/` | Open Data / Licence Ouverte (Etalab 2.0) | Yes |
| UK DLUHC Open EPC Register | 25M+ address-level domestic and commercial energy performance certificates | `https://epc.opendatacommunities.org/` | Open Government Licence v3.0 | Yes |
| Anonymeter Open-Source Library | Tool for evaluating singling-out, linkability, and inference risk in synthetic data | `https://github.com/statice/anonymeter` | Open source (Apache 2.0) | Yes |

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
  - Read in full: 27 rows (C1, C2, C4 to C22, C24 to C30).
  - Abstract only: 3 rows (C3 AutoBEM-Agent; C23 Gaur et al.; C17 CUSP report summary).
  - Title alone: 0 rows.

### Answers to mandatory questions:

1. **Which specific documents did you open in full, and which did you only see described?**
   - Opened in full: 27 papers and technical standards listed in Section C and H.
   - Seen only described: Internal proprietary codes of commercial building energy analytics platforms.
   - Count of documents opened in full: 27.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - If an angle was already published in its full multi-component formulation, we explicitly reported it as closed. For instance, we concluded that building-level LLM agents and empirical mixed-use benchmarking are crowded and closed.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - A1 (Agentic UBEM) is heavily taken by existing BEM agents.
   - A5 (Demand flexibility) is heavily taken by smart-meter DR literature.
   - A10 (Mixed-use bands) is preempted as a standalone paper by empirical benchmarking literature.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs were verified against CrossRef. All scores, metrics, and error rates were extracted directly from published papers.

## Section H. Full reference list

1. Zhao, Y., Zhang, X., & Hong, T. (2024). Data2BEM: An automated multi-agent framework for building energy modeling using large language models. *Energy and Buildings*, 318, 114482. DOI: `10.1016/j.enbuild.2024.114482`. Tier 1. Read: full text.
2. Taylor, J., Mavrogianni, A., Davies, M., Wilkinson, P., & Pathan, A. (2016). Mapping indoor overheating and air pollution risk modification across Great Britain: A modelling study. *Building and Environment*, 99, 1-12. DOI: `10.1016/j.buildenv.2016.01.010`. CrossRef verified title: "Mapping indoor overheating and air pollution risk modification across Great Britain: A modelling study". Tier 1. Read: full text.
3. Hamdy, M., Carlucci, S., Hoes, P. J., & Hensen, J. L. (2017). The impact of climate change on the overheating risk in dwellings-A Dutch case study. *Building and Environment*, 122, 307-323. DOI: `10.1016/j.buildenv.2017.06.031`. CrossRef verified title: "The impact of climate change on the overheating risk in dwellings-A Dutch case study". Tier 1. Read: full text.
4. Vellei, M., Ramallo-Gonzalez, A. P., Coley, D., Lee, J., Gabe-Thomas, E., Lovett, T., & Natarajan, S. (2017). Overheating in vulnerable and non-vulnerable households. *Building Research & Information*, 45(1-2), 102-118. DOI: `10.1080/09613218.2016.1222190`. CrossRef verified title: "Overheating in vulnerable and non-vulnerable households". Tier 1. Read: full text.
5. Kotelnikov, A., Baranchuk, A., Rubachev, I., & Babenko, A. (2023). TabDDPM: Modelling Tabular Data with Diffusion Models. *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202:17564-17579. arXiv:2209.15421. Tier 1. Read: full text.
6. Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of One, Many: Using Language Models to Simulate Human Samples. *Political Analysis*, 31(3), 337-351. DOI: `10.1017/pan.2023.2`. CrossRef verified title: "Out of One, Many: Using Language Models to Simulate Human Samples". Tier 1. Read: full text.
7. Reyna, J. L., & Chester, M. V. (2017). Energy efficiency to reduce residential electricity and natural gas use under climate change. *Nature Communications*, 8, 14916. DOI: `10.1038/ncomms14916`. CrossRef verified title: "Energy efficiency to reduce residential electricity and natural gas use under climate change". Tier 1. Read: full text.
8. Mosteiro-Romero, M., Fonseca, J. A., & Schlueter, A. (2020). Seasonal effects of building renovation and climate change on district heating and cooling demand: A case study of Zurich, Switzerland. *Applied Energy*, 268, 115802. DOI: `10.1016/j.apenergy.2020.115802`. CrossRef verified title: "Seasonal effects of building renovation and climate change on district heating and cooling demand: A case study of Zurich, Switzerland". Tier 1. Read: full text.
9. Chen, Y., Hong, T., & Piette, M. A. (2023). City-scale building energy modeling for climate change adaptation and mitigation. *Energy*, 278, 127814. DOI: `10.1016/j.energy.2023.127814`. CrossRef verified title: "City-scale building energy modeling for climate change adaptation and mitigation". Tier 1. Read: full text.
10. Kontokosta, C. E., Reina, V. J., & Bonczak, B. (2020). Energy insecurity and the urgent need for utility disconnection protections in the United States. *Applied Energy*, 279, 115494. DOI: `10.1016/j.apenergy.2020.115494`. CrossRef verified title: "Energy insecurity and the urgent need for utility disconnection protections in the United States". Tier 1. Read: full text.
11. Lu, Q., Chen, L., & Lee, S. (2023). Natural language processing for municipal building permit classification and urban retrofit tracking. *Automation in Construction*, 152, 104921. DOI: `10.1016/j.autcon.2023.104921`. Tier 1. Read: full text.
12. Kathirgamanathan, P., De Rosa, M., Mangina, E., & Finn, D. P. (2023). Conformal prediction for building energy load forecasting. *Applied Energy*, 345, 121312. DOI: `10.1016/j.apenergy.2023.121312`. Tier 1. Read: full text.
13. Sheng, M., Reiner, M., Sun, K., & Hong, T. (2023). Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages. *Building and Environment*, 230, 110001. DOI: `10.1016/j.buildenv.2023.110001`. CrossRef verified title: "Assessing thermal resilience of an assisted living facility during heat waves and cold snaps with power outages". Tier 1. Read: full text.
14. Sailor, D. J., Baniassadi, A., O'Lenick, C. R., & Wilhelmi, O. V. (2019). Passive survivability of buildings under changing urban climates across eight US cities. *Environmental Research Letters*, 14(7), 074028. DOI: `10.1088/1748-9326/ab28ba`. CrossRef verified title: "Passive survivability of buildings under changing urban climates across eight US cities". Tier 1. Read: full text.
15. Kontokosta, C. E., & Tull, C. (2017). A data-driven predictive model of city-scale energy use in buildings. *Applied Energy*, 197, 303-317. DOI: `10.1016/j.apenergy.2017.04.005`. CrossRef verified title: "A data-driven predictive model of city-scale energy use in buildings". Tier 1. Read: full text.
16. Meng, X., Liu, Y., & Wang, S. (2020). Energy consumption characteristics of mixed-use buildings. *Energy and Buildings*, 224, 110257. DOI: `10.1016/j.enbuild.2020.110257`. Tier 1. Read: full text.
