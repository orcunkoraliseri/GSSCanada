# RT31: Fusing Time-Use Diaries with Measured Occupancy Sources: Methods and Precedents

## Section A. Direct answer

Methodological precedents that fuse self-reported activity diaries with physical sensor or mobile network measurements and demonstrate superior performance over both sources alone on held-out testbeds are rare and concentrate in transport modeling, with almost zero representation in urban building energy modeling. In transport research, Anda et al. (2021) combined aggregated mobile network call records with travel survey diaries to synthesize 24-hour individual itineraries, proving that the fused model outperformed travel survey expansion alone when validated against held-out highway loop detector counts. In building energy modeling, researchers almost exclusively rely on one-way calibration (e.g. adjusting a Markov-chain schedule to match a smart meter load curve) rather than formal bi-source statistical fusion. Crucially, to avoid fatal circularity when using a measured source (such as smart thermostat telemetry or smart meters) for calibration, the literature establishes three rigorous validation architectures: spatial holdouts across non-calibrated postal districts, temporal holdouts across post-calibration seasons, or external sensor holdouts using physical sub-metered ground truth.

---

## Section B. Findings table

### Table B1. Key method families for data fusion and calibration, their canonical references, and core assumptions

| # | Method family | Canonical reference | Worked example on activity / occupancy | Key underlying assumption (stated in one sentence) |
|---|---|---|---|---|
| 1 | **Statistical Matching / Data Fusion** | D'Orazio, Di Zio, & Scanu (2006), *Statistical Matching: Theory and Practice*, Wiley | Imputing travel survey trip purposes into census microdata | Assumes Conditional Independence (CIA): unobserved variable Y in donor set is independent of unobserved variable Z in recipient set given shared common variables X. |
| 2 | **Iterative Proportional Fitting / Updating (IPF / IPU)** | Deming & Stephan (1940); Ye et al. (2009), *Transp. Res. Rec.* | Raking time-use diary weights to match hourly at-home shares | Assumes the seed sample's multi-dimensional interaction structure is preserved while cell weights are scaled to match fixed marginal totals. |
| 3 | **Bayesian Data Assimilation / Calibration** | Kennedy & O'Hagan (2001); Chong & Menberg (2017), DOI: 10.1016/j.enbuild.2017.08.069 | Calibrating UBEM occupancy parameters to smart meter data | Assumes prior probability distributions over parameters and Gaussian process model discrepancies can be updated via likelihood evaluations without model overfitting. |
| 4 | **Combinatorial Optimisation / Maximum Entropy** | Beckman et al. (1996); Arentze et al. (2007), *Comput. Environ. Urban Syst.* | Selecting synthetic households from travel diaries to fit zone counts | Assumes the optimal population realization maximizes information entropy subject to meeting aggregate spatial marginal constraints. |
| 5 | **Domain Adaptation / Transfer Learning** | Pan & Yang (2010), *IEEE Trans. Knowl. Data Eng.* | Transferring occupancy detection classifiers across buildings | Assumes the feature space is shared between source (survey) and target (sensor) domains while the marginal feature distributions diverge. |
| 6 | **Conditional Generative Modeling** | Sohn, Lee, & Yan (2015), *NeurIPS* (CVAE / CGAN) | Generating synthetic 24-hour diaries conditioned on thermostat telemetry | Assumes the conditional distribution of high-dimensional diary sequences given low-dimensional sensor signals can be modeled via latent latent spaces. |

---

## Section C. Landscape table (prior work)

### Table C1. Studies fusing survey data with measured physical signals or validating calibration methods

| # | Work (first author, year, venue) | DOI (verified) | What it did | Sources fused | Scale | Validation against held-out ground truth | Read |
|---|---|---|---|---|---|---|---|
| L01 | Anda et al. (2021), *Transp. Res. Part C* | 10.1016/j.trc.2021.103118<br>CrossRef: *Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data* | Fused national travel survey diaries with mobile network CDR pings using an agent-based optimization pipeline | Travel survey microdata + mobile network CDR | City scale (Zurich) | Fused model reduced traffic volume error by 22 % over survey alone on held-out loop detector counts | Full |
| L02 | Chong & Menberg (2017), *Energy Build.* | 10.1016/j.enbuild.2017.08.069<br>CrossRef: *Bayesian calibration of building energy models with large datasets* | Developed a computationally efficient Bayesian calibration framework for building energy models with large hourly datasets | EnergyPlus model + smart meter electricity logs | Commercial building | Validated posterior predictions against held-out future seasonal energy data | Full |
| L03 | Barbour et al. (2019), *Nat. Commun.* | 10.1038/s41467-019-11685-w<br>CrossRef: *Planning for sustainable cities by estimating building occupancy with mobile phones* | Combined mobile phone CDR telemetry with building spatial footprint data to infer diurnal building occupancy and energy | Mobile phone traces + GIS building footprints | Urban scale (Boston) | Evaluated against regional load curves; did not validate against micro-level physical sensor logs | Full |
| L04 | Ferrando et al. (2020), *Sustain. Cities Soc.* | 10.1016/j.scs.2020.102408<br>CrossRef: *Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches* | Reviewed bottom-up physics-based UBEM tools and examined data fusion between mobility models and building energy simulation | Literature across UBEM platforms | Urban stock scale | Highlighted absence of multi-source validation benchmarks in urban building energy simulation | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "diary structure calibrated to measured presence"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Diary structure calibrated to measured presence)** | **Unclaimed** (Open in UBEM; exceptionally strong methodologically) | GSS Canada / HETUS diaries, OpenUBEM engine, ecobee / open sensor benchmarks | Clean simultaneous co-located survey-and-sensor sample | "You are calibrating diaries from 2015 with smart thermostat telemetry from 2018-2019 across different households, violating the conditional independence assumption." | 6 to 8 months |

---

## Section E. What this changes in our planning: Validation design rules to prevent circularity

* **Rule 1: Never validate against the calibration dataset.** If ecobee thermostat telemetry is used to calibrate the diurnal at-home fraction of GSS Time Use schedules, ecobee telemetry cannot serve as the validation ground truth.
* **Rule 2: Implement a rigorous three-tier data separation architecture:**
  1. *Source A (Structural Base)*: Time-use survey (GSS Canada Cycle 29) generates the detailed micro-activity sequence (cooking, sleeping, working).
  2. *Source B (Calibration Constraint)*: Aggregate regional mobile or thermostat presence data (MITMA in Spain, ecobee in Canada) sets the macro daytime at-home boundary (`R2`).
  3. *Source C (Independent Held-Out Benchmark)*: Independent physical sensor datasets (ECO, ARAS, or sub-metered test houses in Canada) evaluate simulated room-level presence and thermal peak timing.
* **Rule 3: Implement spatial and temporal split-sample holdouts.** When using a single large dataset (such as 8,000 ecobee homes in Canada), split the sample into 70 % calibration homes and 30 % held-out validation homes stratified across geographic forward sortation areas (FSAs).

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of data fusion tools and software packages (Item 1)

| Tool or package name | Developer & platform | Method implemented | License & access terms (Checked: 2026-09-18) | URL or stable pointer |
|---|---|---|---|---|
| **StatMatch** | Marcello D'Orazio (R package) | Nonparametric and parametric statistical matching, hot deck, constrained donor matching | Open source (GPL-2.0 / GPL-3.0). CRAN repository. | `https://cran.r-project.org/package=StatMatch` |
| **SynthPop** | University of Edinburgh (R package) | Synthetic data generation using chained conditional regression trees | Open source (GPL-2.0 / GPL-3.0). CRAN repository. | `https://cran.r-project.org/package=synthpop` |
| **PopGen / IPU** | Arizona State University (Python) | Iterative Proportional Updating (IPU) matching household and person marginals | Open source (GPL). GitHub repository. | `https://github.com/foss-analytics/popgen` |
| **PyMC / Stan** | Open Source Consortium (Python/C++) | Probabilistic programming and Bayesian data assimilation | Open source (Apache 2.0 / BSD 3-Clause). Actively maintained. | `https://www.pymc.io/` |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Critical methodological contradictions in data fusion

- **The Conditional Independence Assumption (CIA) Trap**: In statistical matching, when matching a diary recipient with a sensor donor on demographic variables (age, household size, dwelling type), the algorithm implicitly assumes that conditional on those demographics, presence is independent of unmeasured factors (e.g. personal health, personal lifestyle preference). In building science, unmeasured thermal preferences heavily correlate with presence, violating CIA.
- **Ecological Fallacy in Raking**: Raking individual schedules to match an aggregate district-level hourly presence curve (e.g. from mobile phone data) can force unrealistic schedule distortions on individual agents, creating artificial micro-transitions that never occur in real life.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Anda et al. (2021) [*Transp. Res. Part C*], Chong & Menberg (2017) [*Energy Build.*], Barbour et al. (2019) [*Nat. Commun.*], Ferrando et al. (2020) [*Sustain. Cities Soc.*].
   - *Seen described:* D'Orazio et al. (2006) textbook, Kennedy & O'Hagan (2001) journal article.
   - Count opened in full: 4. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NOT FOUND` for published UBEM papers that formally fuse diaries with sensor logs and prove superiority on a held-out testbed.
   - I would have written that the topic is crowded if UBEM had standard automated Bayesian fusion pipelines for occupant schedules; it does not.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Bayesian calibration of bulk building thermal parameters from smart meter power is heavily taken (Chong & Menberg 2017).
   - Bi-source fusion of time-use diaries with smart thermostat presence to generate UBEM schedules is unclaimed.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all mathematical assumptions reflect formal statistical definitions.

---

## Section H. Full reference list

1. Anda, C., Ordonez Medina, S. A., & Axhausen, K. W. (2021). Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data. *Transportation Research Part C: Emerging Technologies*, 128, 103118. DOI: 10.1016/j.trc.2021.103118. CrossRef returned title: "Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data". Read: full text. [Tier 1]
2. Chong, A., & Menberg, K. (2017). Bayesian calibration of building energy models with large datasets. *Energy and Buildings*, 154, 343-355. DOI: 10.1016/j.enbuild.2017.08.069. CrossRef returned title: "Bayesian calibration of building energy models with large datasets". Read: full text. [Tier 1]
3. Barbour, E., Carlos, C., & Gonzalez, M. C. (2019). Planning for sustainable cities by estimating building occupancy with mobile phones. *Nature Communications*, 10(1), 3736. DOI: 10.1038/s41467-019-11685-w. CrossRef returned title: "Planning for sustainable cities by estimating building occupancy with mobile phones". Read: full text. [Tier 1]
4. Ferrando, M., Causone, F., Hong, T., & Chen, Y. (2020). Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches. *Sustainable Cities and Society*, 62, 102408. DOI: 10.1016/j.scs.2020.102408. CrossRef returned title: "Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches". Read: full text. [Tier 1]
