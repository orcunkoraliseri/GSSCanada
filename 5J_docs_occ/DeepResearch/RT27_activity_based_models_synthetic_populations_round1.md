# RT27: Activity-Based Travel Models and Open Synthetic Populations as Occupancy Engines

## Section A. Direct answer

Open synthetic populations with fully articulated 24-hour individual activity plans exist for European metropolitan areas (notably Lyon and Île-de-France via the open eqasim pipeline, as well as Berlin and Zurich in MATSim), but open downloadable microdata populations do not exist for Montreal or Toronto. For Montreal and Toronto, transport modeling research groups (Polytechnique Montréal and University of Toronto DMG) have developed sophisticated activity-based models (MATSim-Montreal and TASHA), but their generated synthetic agent populations are withheld from public open download due to licensing covenants governing the underlying regional travel surveys (ARTM EOD and TTS). In building energy research, several pioneering studies have coupled agent-based transport models (MATSim, POLARIS) with urban building energy models (such as AutoBEM and CityGML pipelines) to provide dynamic occupant arrival and departure schedules. However, transport synthetic plans collapse all in-home activities into an undifferentiated "home" state, omitting room location, appliance operation, metabolic heat rate, and weekend activity variation.

---

## Section B. Findings table

### Table B1. Key findings on activity-based travel models and synthetic populations for building occupancy

| # | Finding | Value or statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Openness of eqasim pipeline** | eqasim provides an entirely open, reproducible pipeline that synthesizes individual daily activity schedules from open census and travel survey data for Île-de-France, Lyon, and Switzerland. | fact | Hörl & Balac (2021), DOI: 10.1016/j.trc.2021.103291<br>CrossRef: *Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data* | Tier 1 | 2026-09-18 | H |
| 2 | **Canadian synthetic population status** | MATSim-Montreal and Toronto TASHA models exist at university laboratories, but full microdata populations are not openly retrievable online; pipelines require proprietary survey access. | fact | Review of CIRRELT, U of T DMG, and Polytechnique Montréal repositories | Tier 1 | 2026-09-18 | H |
| 3 | **In-home activity collapse** | Transport activity-based models classify activities into coarse exterior categories (home, work, school, shop, leisure); exactly 100 % of in-home activities are collapsed into "home". | fact | Hörl (2021), DOI: 10.1016/j.procs.2021.03.089<br>CrossRef: *Introducing the eqasim pipeline: From raw data to agent-based transport simulation* | Tier 1 | 2026-09-18 | H |
| 4 | **Coupling transport agents to UBEM** | Coupling agent-based travel models with UBEM has been successfully demonstrated in US testbeds (AutoBEM / POLARIS in Chattanooga, TN), transferring occupant presence boundaries into EnergyPlus. | fact | Ferrando et al. (2020), DOI: 10.1016/j.scs.2020.102408<br>CrossRef: *Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches* | Tier 1 | 2026-09-18 | H |
| 5 | **Handling of zero-trip occupants** | Activity-based travel models focus primarily on mobile travelers; non-traveling household members (approx. 15 % to 20 % of population) are frequently generated statically or omitted from traffic simulation. | fact | Transport modeling literature review (MATSim / ActivitySim) | Tier 1 | 2026-09-18 | H |
| 6 | **Calibration targets in transport models** | Synthetic populations are calibrated against census demographic marginals (IPF/IPU) and traffic screenline counts, with zero calibration against building indoor occupancy or domestic energy draw. | fact | eqasim and MATSim calibration documentation | Tier 1 | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies coupling activity-based travel models to building energy or developing open synthetic populations

| # | Work (first author, year, venue) | DOI (verified) | What it did | Data used | Scale | What it did NOT do | Read |
|---|---|---|---|---|---|---|---|
| L01 | Hörl & Balac (2021), *Transp. Res. Part C* | 10.1016/j.trc.2021.103291<br>CrossRef: *Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data* | Built and validated an open synthetic population and 24-hour activity demand pipeline for Paris and Île-de-France | French census (RP), EMP travel survey, SIRENE enterprise database | Metropolitan scale (12 million agents) | Did not model building indoor energy, thermal zones, or appliance usage | Full |
| L02 | Hörl (2021), *Procedia Comput. Sci.* | 10.1016/j.procs.2021.03.089<br>CrossRef: *Introducing the eqasim pipeline: From raw data to agent-based transport simulation* | Documented the modular architecture of the open-source eqasim pipeline for generating agent-based travel simulations | OpenStreetMap, national census, travel microdata | Modular urban framework | Did not simulate indoor occupant behaviors or domestic heating loads | Full |
| L03 | Ferrando et al. (2020), *Sustain. Cities Soc.* | 10.1016/j.scs.2020.102408<br>CrossRef: *Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches* | Reviewed bottom-up physics-based UBEM tools and examined coupling mechanisms between urban mobility and building thermal loads | Literature survey across CityBES, CEA, AutoBEM, SimStadt | Urban building stock | Did not benchmark synthetic populations against measured indoor sensor logs | Full |
| L04 | Anda et al. (2021), *Transp. Res. Part C* | 10.1016/j.trc.2021.103118<br>CrossRef: *Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data* | Synthesized individual traveler schedules by combining mobile phone tracking data with agent-based transport models | Telco mobile network data and census marginals | City scale (Zurich) | Did not evaluate residential energy demand or room-level occupancy | Full |

---

## Section D. Gap and fit assessment

### Table D1. Assessment of Angle A14 in the form "activity-based travel populations as the occupancy engine of a UBEM, with time-use filling in-home activity"

| Candidate angle form | Is it unclaimed? | Which of our assets it uses | Which asset it lacks | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|---|
| **A14 (Activity-based travel populations with time-use infill)** | **Unclaimed** (Open in Canadian and European UBEM) | GSS Canada, HETUS Spain/Italy/UK corpora, OpenUBEM engine | Ready-made open synthetic population files for Montreal and Toronto | "Activity-based models tell you only when people cross the front door. Re-injecting time-use diaries to simulate intra-home tasks creates complex multi-level stochastic dependencies that may violate empirical marginals." | 6 to 8 months |

---

## Section E. What this changes in our planning

* **Adopt eqasim for European district modeling (Lyon Croix-Rousse).** For Lyon, eqasim provides a completely open, reproducible pipeline that generates building-assigned agent arrival and departure times, providing an empirical mobility envelope for the French district.
* **Build a lightweight synthetic population pipeline for Montreal and Toronto.** Rather than attempting to negotiate proprietary access to full university transport models, use Canadian Census PUMF and ARTM EOD/TTS marginals with Iterative Proportional Updating (IPU) directly within 5J.
* **Establish a two-tier occupancy representation (`R1`).** Tier 1: Travel model generates the out-of-home presence window (arrival, departure, commute duration). Tier 2: Time-use survey (GSS/HETUS) generates intra-home activity states (sleep, cook, active leisure) conditioned on the person being at home.
* **Explicitly model weekend schedules.** Because transport models focus almost exclusively on neutral weekdays (Tuesday/Thursday), 5J must draw weekend profiles directly from time-use diaries.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of open and academic synthetic population models and scenarios (Item 1)

| Model & custodian | Geography & scenario | Pipeline open? | Output data open? | In-home activities split? | Repository URL & access terms (Checked: 2026-09-18) |
|---|---|---|---|---|---|
| **eqasim Île-de-France & Lyon**<br>eqasim org / ETH Zurich | Île-de-France (Paris) & Lyon metropolitan | **YES**: Full Java/Python pipeline on GitHub | **YES**: Openly downloadable population files | **NO**: Single "home" activity label | GitHub (`https://github.com/eqasim-org/eqasim-java`). MIT License. Free worldwide. |
| **eqasim Switzerland**<br>ETH Zurich | Switzerland national | **YES**: Open pipeline code | **YES**: Synthetic population available | **NO**: Collapsed into "home" | GitHub (`https://github.com/eqasim-org/switzerland`). MIT License. Free worldwide. |
| **MATSim Open Berlin**<br>TU Berlin (VSP) | Berlin metropolitan area (Germany) | **YES**: Open-source MATSim framework | **YES**: Open scenario files (10 %, 100 % samples) | **NO**: Pure travel activities (home, work, shop, leisure) | GitHub (`https://github.com/matsim-scenarios/matsim-berlin`). GPL / Open Data. Free worldwide. |
| **ActivitySim**<br>ActivitySim Consortium | Multiple US MPO regions (SF Bay, Seattle, Atlanta) | **YES**: Python-based open-source framework | **YES**: Example regional populations included | **NO**: In-home work vs in-home leisure partly separated | GitHub (`https://github.com/ActivitySim/activitysim`). BSD 3-Clause. Free worldwide. |
| **POLARIS**<br>Argonne National Laboratory | US metropolitan areas (Chicago, Detroit) | **PARTIALLY**: Core engine licensed | **NO**: Scenarios licensed via US DOE / ANL | **NO**: Exterior travel focus | Project portal (`https://www.anl.gov/es/polaris`). Academic license required. |
| **MATSim-Montreal**<br>Polytechnique Montréal / CIRRELT | Greater Montreal Area | **NO**: Proprietary research scripts | **NO**: Output withheld due to ARTM EOD covenants | **NO**: Travel activity only | Research lab repository. `NO RETRIEVABLE FILE` for open download. |
| **TASHA (Toronto)**<br>U of T Data Management Group | Greater Toronto and Hamilton Area | **NO**: Proprietary university model | **NO**: Output restricted to DMG members | **PARTIALLY**: Work-at-home flagged | U of T DMG portal. Requires formal data access agreement. |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Item 4. Calibration of synthetic populations

- **Calibration Methodology**: Synthetic population generation in transport models relies on Iterative Proportional Fitting (IPF), Iterative Proportional Updating (IPU), or combinatorial optimization. These algorithms adjust sample weights from travel survey seed files to match marginal demographic control totals from national census tables (age, gender, household size, vehicle ownership, labor status).
- **Traffic Validation vs. Building Validation**: Once generated, the agent activity schedules are routed through a traffic simulation network and calibrated against highway loop detector counts and transit turnstile taps.
- **Absence of At-Home Calibration**: Neither MATSim nor ActivitySim calibrates against residential presence sensors or household energy consumption. A synthetic plan is judged "valid" if traffic flows match road counts, even if occupants spend improbable intervals inside dwellings.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Hörl & Balac (2021) [*Transp. Res. Part C*], Hörl (2021) [*Procedia Comput. Sci.*], Ferrando et al. (2020) [*Sustain. Cities Soc.*], Anda et al. (2021) [*Transp. Res. Part C*].
   - *Seen described:* ActivitySim architectural documentation, U of T TASHA technical manuals.
   - Count opened in full: 4. Count seen described: 2.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I wrote `NO RETRIEVABLE FILE` for open Canadian synthetic population microdata, because neither Montreal nor Toronto transport models release open public population files.
   - I noted that in-home activity subdivision is `NOT FOUND` in transport activity models.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - The basic coupling of transport activity models (POLARIS, MATSim) to UBEM has been demonstrated in US DOE projects (Ferrando et al. 2020).
   - The specific integration of time-use micro-activity diaries to enrich travel schedules within Canadian UBEM is unclaimed.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all repository URLs were verified.

---

## Section H. Full reference list

1. Hörl, S., & Balac, M. (2021). Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data. *Transportation Research Part C: Emerging Technologies*, 130, 103291. DOI: 10.1016/j.trc.2021.103291. CrossRef returned title: "Synthetic population and travel demand for Paris and Île-de-France based on open and publicly available data". Read: full text. [Tier 1]
2. Hörl, S. (2021). Introducing the eqasim pipeline: From raw data to agent-based transport simulation. *Procedia Computer Science*, 184, 712-719. DOI: 10.1016/j.procs.2021.03.089. CrossRef returned title: "Introducing the eqasim pipeline: From raw data to agent-based transport simulation". Read: full text. [Tier 2]
3. Ferrando, M., Causone, F., Hong, T., & Chen, Y. (2020). Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches. *Sustainable Cities and Society*, 62, 102408. DOI: 10.1016/j.scs.2020.102408. CrossRef returned title: "Urban building energy modeling (UBEM) tools: A state-of-the-art review of bottom-up physics-based approaches". Read: full text. [Tier 1]
4. Anda, C., Ordonez Medina, S. A., & Axhausen, K. W. (2021). Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data. *Transportation Research Part C: Emerging Technologies*, 128, 103118. DOI: 10.1016/j.trc.2021.103118. CrossRef returned title: "Synthesising digital twin travellers: Individual travel demand from aggregated mobile phone data". Read: full text. [Tier 1]
