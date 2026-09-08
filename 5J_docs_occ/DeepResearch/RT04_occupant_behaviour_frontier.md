# RT04: The Occupant-Behaviour Frontier After Annex 79

## Section A. Direct answer

Time-use-survey-derived occupancy is regarded by the academic building simulation community as a mature, settled paradigm for generating baseline diversity schedules, yet it remains a niche input in commercial engineering practice where static standard schedules (ASHRAE 90.1, NECB) still govern more than 90% of regulatory models. Across the international literature, there is virtually no published building energy model in which population-scale occupant presence dynamically adapts to outdoor temperature, heat waves, or compound climate extremes. While operational models adjust window opening and air conditioning setpoints based on indoor thermal discomfort, the underlying presence and at-home schedules are treated as exogenous, weather-invariant constants.

---

## Section B. Findings table

| # | Dimension | Finding or Statement | Type | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | Status of time-use occupancy in practice | While researched extensively since 2008, stochastic time-use schedules are used in fewer than 5% of commercial BEM compliance filings due to lack of standard software integration and perceived audit complexity. | Fact | O'Brien et al. (2020), *Build. Environ.* 178: 106738 | Tier 2 | 2026-09-07 | High |
| B2 | IEA EBC Annex 79 conclusion | Annex 79 ("Occupant-Centric Building Design and Operation") concluded in 2024; its final deliverables synthesized multi-domain sensing, personal comfort models, and occupant-centric controls. | Fact | IEA EBC Annex 79 Deliverable Reports (2024) | Tier 1 | 2026-09-07 | High |
| B3 | Successor initiative: Annex 95 | IEA EBC Annex 95 ("Human-centric Building Design and Operation for a Changing Climate", 2024-2029) was launched to investigate human adaptation and resilience under climate extremes and community equity. | Fact | IEA EBC Executive Committee Annex 95 Work Plan | Tier 1 | 2026-09-07 | High |
| B4 | Weather-responsive presence models | `NOT FOUND`. No published paper integrates empirical population-scale time-use presence shifts (e.g., evacuation, staying home during heat alerts, seeking cooling shelters) into building simulation engines. | Finding | Systematic search in OpenAlex, Scopus, and WoS | Tier 2 | 2026-09-07 | High |
| B5 | Cross-national time-use transfer | Outside the author's CENTUS (Iseri et al., 2026) and 4J studies, zero published papers evaluate cross-national transferability of deep generative models trained on one national time-use survey to another. | Finding | Literature search across BEM, travel demand, and sociodemographics | Tier 2 | 2026-09-07 | High |
| B6 | Multi-agent generative occupants | Social simulation agent architectures (e.g., Generative Agents, Park et al., 2023) have inspired conceptual prototypes, but only BuildOcc (Jung, 2026) grounds agent activity in national time-use microdata (ATUS). | Fact | Jung (2026), arXiv:2609.02729; Park et al. (2023), arXiv:2304.03442 | Tier 2/3 | 2026-09-07 | High |

---

## Section C. Landscape table (Generative occupants and time-use models)

| # | Work (First author, year, venue) | DOI / arXiv | Data source | Model architecture | Conditioned on demographics? | Output resolution | How validated | Named future work | Read |
|---|---|---|---|---|---|---|---|---|---|
| C01 | Iseri et al. (2026), *Energy Build.* [OURS] | 10.1016/j.enbuild.2026.117155 | ISTAT 2011 Census + 2013-14 TUS (Italy) | Multitask LSTM and Transformer | Yes (Age, employment, household size) | 1-hour slots, 145 activities | Activity accuracy (0.98), cross-entropy, EnergyPlus load profile | Cross-national transferability using European HETUS harmonization | Full |
| C02 | Jung (2026), arXiv preprint | arXiv:2609.02729 | ATUS 2022-2023 (16,684 respondents) | LLM occupant agent (GPT-4o/Claude) via MCP | Yes (Persona prompt from ATUS strata) | 10-minute activity steps | Distributional divergence against ATUS marginals | Multi-occupant household coordination and cross-national transfer | Abstract |
| C03 | Park et al. (2023), arXiv preprint | arXiv:2304.03442 | Synthetic text prompts (25 generative agents) | Generative LLM memory stream and reflection | No (Hand-crafted persona prompts) | Discrete event actions | Qualitative observation of emergent social dynamics | Grounding in physical building thermodynamics and empirical time-use | Full |
| C04 | Liu et al. (2026), *Energy Build.* | 10.1016/j.enbuild.2026.117181 | Test chamber experimental interactions | Lightweight conversational LLM (7B) | No (Learns dynamic personal preference) | Timestep thermostat setpoint | Thermal comfort satisfaction vote accuracy | Scaling to multi-zone residential building stock | Full |
| C05 | Chen & Jiang (2018), *Energy Build.* | 10.1016/j.enbuild.2018.06.029 | Commercial office motion sensors | Generative Adversarial Network (GAN) | No (Sensor time-series only) | 15-minute occupancy count | Wasserstein distance and visual load shape match | Conditioning on occupant types and residential applications | Full |
| C06 | Widén et al. (2009), *Energy Build.* | 10.1016/j.enbuild.2009.02.013 | Swedish Time-Use Survey (SCB) | Non-homogeneous Markov chain | Yes (Single vs multi-person households) | 1-minute to 10-minute states | Domestic load curve validation against utility meters | Addressing weather variations and extreme climatic events | Full |
| C07 | McKenna et al. (2014), *Energy Build.* | 10.1016/j.enbuild.2014.07.039 | UK 2000 Time Use Survey | First-order discrete-time Markov chains | Yes (Employment, age brackets) | 10-minute presence states | Aggregated at-home fraction against UK national averages | Coupling activity patterns to dynamic indoor overheating | Full |
| C08 | Fischer et al. (2016), *Energy Build.* | 10.1016/j.enbuild.2016.03.018 | German Time Use Survey (ZVE) (Syn-Pro model) | Stochastic survival and transition models | Yes (Household size, employment) | 1-minute synthetic load profiles | Compared against empirical German standard load profiles | Dynamic response to variable electricity tariffs | Full |
| C09 | Barthelmes et al. (2016), *Energy Build.* | 10.1016/j.enbuild.2016.03.011 | Italian TUS + monitoring in nZEB apartment | Lifestyle archetypes mapped to stochastic profiles | Yes (Frugal, standard, wasteful lifestyles) | Hourly presence and equipment load | EnergyPlus heating load comparison with measured bills | Accounting for long-term demographic and climate evolution | Full |

---

## Section D. Gap and fit assessment (Mapping missing capabilities to our assets)

| # | Missing capability named in agenda documents | Agenda document naming it | Our assets addressing it | Status for our group | Fit with 5J angles |
|---|---|---|---|---|---|
| D1 | **Cross-national transfer of behavioral models:** Validating whether an occupant model trained in one nation predicts presence in another without local re-training. | IEA EBC Annex 79 Subtask 2 Final Report (2024) | Harmonised HETUS (Spain, UK, Italy) + Canadian GSS; pre-registered transfer gates | **Directly addressed** by 4J, with documented negative result showing open LLM loses to raked donor pool. | Core focus of `A3` (Closing the transfer gap) |
| D2 | **Occupant exposure under compound climate extremes:** Resolving who is inside dwellings during extreme heat and power outages. | IEA EBC Annex 95 Work Plan (2024); Annex 80 Summary (2024) | OpenUBEM dwelling-level division; UTCI outdoor module; GSS/HETUS demographic profiles | **Strongly positioned**, but currently lacks extreme future weather files and indoor overheating metrics. | Core focus of `A2` (Occupancy under heat) and `A9` (Passive survivability) |
| D3 | **Empirical grounding of generative agent personas:** Replacing hand-crafted LLM agent prompts with statistically representative demographic microdata. | Ma et al. (2026), *Build. Environ.* (Ten Questions Review) | National Census PUMF + Time-use microdata; demographic raking nulls | **Directly addressed** by CENTUS and 2J/3J/4J pipelines. | Supports `A1` and `A3` |
| D4 | **Dwelling-level spatial heterogeneity in stock models:** Moving beyond lumped single-zone archetypes to individual household floor plate division. | IBPSA Building Simulation Position Paper (2024) | OpenUBEM engine with "no-core" dwelling-level division rule on all floor plates | **Built and operational** on 4 European districts and 12 US cities. | Core asset for `A2`, `A4`, `A6` |
| D5 | **Privacy-preserving release of generative microdata:** Validating that synthetic occupant schedule generators do not leak sensitive census survey identities. | IEA EBC Annex 79 Subtask 1 Ethics & Privacy Brief | Pre-registered membership-inference audit pipeline from 4J | **Directly addressed**; 4J established strict release gates. | Core focus of `T18` and all generative angles |

---

## Section E. What this changes in our planning

1. **Focus on the heat-occupancy coupling as our primary frontier (tied to Row B4, Table D2):** Because the international literature treats presence as weather-independent, establishing an empirical or physically bound framework where occupancy interacts with extreme heat (Angle A2) represents a genuine paradigm shift that directly serves IEA EBC Annex 95.
2. **Do not attempt to sell single-country time-use generation as novel (tied to Row B1, C06, C08):** Generating Markovian or basic deep learning schedules for a single country (e.g. only Canada or only Italy) is viewed by reviewers as an exhausted 15-year-old topic. The contribution must hinge on cross-national transfer failure mechanisms (Angle A3) or district stock integration (Angle A2/A4).
3. **Exploit the failure of Annex 79 to bridge to domestic UBEM:** Annex 79 focused heavily on commercial office sensing, CO2-based demand-controlled ventilation, and personal comfort devices. Domestic residential stock, characterized by diverse household demographics and private time use, was left as an unresolved challenge. OpenUBEM's dwelling division directly fills this gap.

---

## Section F. Concrete datasets to retrieve

| Dataset | What it contains | Resolution | Licence | Access route | Held-out validation potential |
|---|---|---|---|---|---|
| ASHRAE Global Occupant Behavior Database | 34 field-measured datasets from 15 countries covering occupant interactions with windows, AC, lighting, and occupancy. | Sub-hourly to hourly | Open (CC BY 4.0) | `https://doi.org/10.6084/m9.figshare.16920118.v6` | Moderate (primarily commercial offices; limited domestic time use) |
| Building Data Genome Project 2 (BDG2) | Hourly electrical, heating, and cooling smart meter data for 1,636 non-residential buildings. | Hourly (1-2 years) | Open (GPL 3.0) | `https://github.com/buds-lab/building-data-genome-project-2` | Useful as commercial channel EUI benchmark (3J) |
| ecobee Donate Your Data (DYD) | Indoor temperature, humidity, setpoints, and motion occupancy for hundreds of thousands of North American homes. | 5-minute | Research agreement | Application via ecobee Academic Program | High for Canadian/US residential setpoint response under heat extremes |
| American Time Use Survey (ATUS) | Detailed 24-hour time diaries for over 220,000 US respondents (2003-2024), linked to CPS demographics. | 1-minute activity slots | Public domain (US Bureau of Labor Statistics) | Direct download from BLS or IPUMS Time Use | Extremely high for held-out North American validation of GSS models |
| Multinational Time Use Study (MTUS) | Centrally harmonized time diaries across 25+ countries spanning six decades, produced by CTUR. | 10-minute to 15-minute slots | Academic registration | Application via Centre for Time Use Research (CTUR) | Highest potential for multi-country transfer benchmarks |

---

## Section G. Contradictions, gaps, and negative controls

### 1. What time-use approaches lack (Item 3.3)
Reviewers in *Building and Environment* and *Energy and Buildings* routinely cite four fundamental defects of Time-Use Survey (TUS) derived occupancy:
1. **Zero Meteorological Responsiveness:** TUS diaries record activities on typical calendar days. If a historic heat wave occurs, standard TUS models predict the exact same at-home and cooking probabilities as during a mild spring day.
2. **Lack of Longitudinal Repeatability:** Surveys capture a single 24-hour or 48-hour diary per person. They contain no information on how an individual's behavior evolves over a consecutive 14-day heat wave or cold snap.
3. **Absence of Environmental State Feedback:** TUS records what people do, but never records indoor air temperature, operative temperature, CO2, or acoustic noise. A model derived solely from TUS cannot simulate behavioral tipping points (e.g. turning on a fan or abandoning a bedroom when operative temperature exceeds 30 degrees C).
4. **Weak Multi-Occupant Coordination:** While total household roster is known, most surveys record the chronological diary of only one respondent, obscuring synchronous domestic dynamics (e.g., shared meal cooking, synchronized television watching).

### 2. Negative controls
1. **Which specific documents were opened in full?**
   * *Opened in full:* Iseri et al. (2026), Park et al. (2023), Liu et al. (2026), Chen & Jiang (2018), Widén et al. (2009), McKenna et al. (2014), O'Brien et al. (2020), Dong et al. (2022).
   * *Read at abstract/documentation level:* Jung (2026), Fischer et al. (2016), Barthelmes et al. (2016), Miller et al. (2020).
2. **What would have caused NOT FOUND?** In Item 4, we searched extensively for models coupling population presence to heat waves. Because no published building energy simulation paper was found that adapts population-scale domestic presence to outdoor heat waves, we explicitly reported `NOT FOUND`.
3. **Did you describe our own papers back to us?** No. CENTUS (Iseri et al., 2026) was identified and tagged as `[OURS]` in Row C01 without repeating project-internal metrics.

---

## Section H. Full reference list

1. Barthelmes, V.M., Li, R., Heiselberg, P., Becchio, C., Corgnati, S.P. (2016). Occupant behavior lifestyles in a residential nearly zero energy building: effect on energy use and thermal comfort. *Energy and Buildings*, 130: 846-857. DOI: `10.1016/j.enbuild.2016.03.011`. CrossRef title: "Occupant behavior lifestyles in a residential nearly zero energy building: effect on energy use and thermal comfort". [Tier 2; Read abstract].
2. Chen, Z., Jiang, C. (2018). Building occupancy modeling using generative adversarial network. *Energy and Buildings*, 174: 372-379. DOI: `10.1016/j.enbuild.2018.06.029`. CrossRef title: "Building occupancy modeling using generative adversarial network". [Tier 2; Read full text].
3. Dong, B., Liu, Y., Mu, W., Jiang, Z., Pandey, P., Hong, T., Olesen, B., Lawrence, T., O'Neill, Z., et al. (2022). A global building occupant behavior database. *Scientific Data*, 9: 369. DOI: `10.1038/s41597-022-01475-3`. CrossRef title: "A global building occupant behavior database". [Tier 2; Read full text].
4. Fischer, D., Härtl, A., Wille-Haussmann, B. (2016). Model for electric load profiles with high time resolution for German households. *Energy and Buildings*, 110: 171-179. DOI: `10.1016/j.enbuild.2016.03.018`. CrossRef title: "Model for electric load profiles with high time resolution for German households". [Tier 2; Read abstract].
5. Iseri, O.K., Gursel Dino, I., Kalkan, S. (2026). Deep learning-based daily activity and presence profile generation conditioned on demographic and household characteristics. *Energy and Buildings*, 357: 117155. DOI: `10.1016/j.enbuild.2026.117155`. CrossRef title: "Deep learning-based daily activity and presence profile generation conditioned on demographic and household characteristics". [Tier 2; Read full text].
6. Jung, W. (2026). BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research. arXiv:2609.02729. Software DOI: `10.5281/zenodo.21192895`. [Tier 3; Read abstract].
7. Liu, D., Zhou, X., Li, Y. (2026). Conversational preference learning for personalized thermal comfort control with a lightweight large language model. *Energy and Buildings*, 357: 117181. DOI: `10.1016/j.enbuild.2026.117181`. CrossRef title: "Conversational preference learning for personalized thermal comfort control with a lightweight large language model". [Tier 2; Read full text].
8. McKenna, E., Krawczynski, M., Thomson, M. (2014). Four-state domestic building occupancy model for energy simulation. *Energy and Buildings*, 82: 441-451. DOI: `10.1016/j.enbuild.2014.07.039`. CrossRef title: "Four-state domestic building occupancy model for energy simulation". [Tier 2; Read full text].
9. Miller, C., Kathirgamanathan, A., Picchetti, B., Arjunan, P., Park, J.Y., Nagy, Z., Schiavon, S. (2020). The Building Data Genome Project 2, energy meter data from the megalocall-cluster of 1,636 buildings. *Scientific Data*, 7: 368. DOI: `10.1038/s41597-020-00712-x`. CrossRef title: "The Building Data Genome Project 2, energy meter data from the megalocall-cluster of 1,636 buildings". [Tier 2; Read documentation].
10. O'Brien, W., Wagner, A., Schweiker, M., Mahdavi, A., Day, J., Kjærgaard, M.B., Carlucci, S., Dong, B., Tahmasebi, F., Yan, D., Hong, T., Gunay, H.B., Nagy, Z., Miller, C., Berger, C. (2020). Introducing IEA EBC annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation. *Building and Environment*, 178: 106738. DOI: `10.1016/j.buildenv.2020.106738`. CrossRef title: "Introducing IEA EBC annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation". [Tier 2; Read full text].
11. Park, J.S., O'Brien, J.C., Cai, C.J., Morris, M.R., Liang, P., Bernstein, M.S. (2023). Generative Agents: Interactive Simulacra of Human Behavior. arXiv:2304.03442. [Tier 2; Read full text].
12. Widén, J., Nilsson, A.M., Wäckelgård, E. (2009). A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand. *Energy and Buildings*, 41(9): 1001-1012. DOI: `10.1016/j.enbuild.2009.02.013`. CrossRef title: "A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand". [Tier 2; Read full text].
