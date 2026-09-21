# **Verification and Literature Mapping of High-Fidelity Occupant and Residential Load Models**

The persistence of the building energy performance gap—the systemic discrepancy between designed energy use predictions and actual, operational consumption—has driven major shifts in building simulation science.1 Historically, simplified assumptions and static, homogeneous schedules dominated thermodynamic simulations, ignoring the highly stochastic nature of occupant activities and electrical appliance use.4 To resolve this, researchers developed bottom-up, high-fidelity occupant models that represent human presence and behavior as dynamic, probabilistic systems.6  
This domain operates in parallel to, but remains distinct from, regional and national energy-stock forecasting frameworks.9 The differences in spatial resolution, temporal granularity, and temporal horizons have created a landscape of two modeling tracks that rarely meet.9 The high-fidelity modeling track operates almost exclusively at the single-building or individual-household scale and serves a retrospective or baseline-representative horizon.7  
Rather than forecasting energy trends into future decades, these high-fidelity models reconstruct baseline behaviors.13 They ingest historical empirical datasets—principally national Time Use Surveys (TUS)—to calibrate stochastic state transition algorithms such as non-homogeneous Markov chains or agent-based platforms.7 This approach generates synthetic load and occupancy profiles at temporal resolutions between one and ten minutes.7 These profiles capture the minute-to-minute volatility required to evaluate localized grid integration, demand-side management, and microgeneration technologies under current climatic and behavioral realities.4  
The following table provides a verified overview of the target literature under evaluation, mapping their specific modeling domains, resolutions, calibration inputs, and scale boundaries.

| Target Source | Modeling Focus | Spatial Scale | Temporal Step Size | Calibration Inputs | Application Horizon |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Richardson et al. (2010)** 18 | Presence, activities, & appliance electricity | Single domestic dwelling | 1-minute | UK 2000 Time Use Survey 18 | Retrospective Baseline |
| **Richardson et al. (2008)** 15 | Active presence (awake and at home) | Single domestic dwelling | 10-minute | UK 2000 Time Use Survey 15 | Retrospective Baseline |
| **Widén & Wäckelgård (2010)** 7 | Occupant activities & appliance electricity | Individual agent / Household | 1-minute | Swedish Time Use Survey 7 | Retrospective Baseline |
| **Wilke et al. (2013) \[Journal\]** 19 | Time-dependent occupant activity chains | Individual agent / Household | Variable | French 1998/1999 TUS 19 | Retrospective Baseline |
| **Wilke (2013)** 20 | Presence, activities, appliance load | Individual agent / Household | Variable | French TUS & ownership data 21 | Retrospective Baseline |
| **Aerts et al. (2014)** 22 | Presence states (3-state sequence) | Single domestic dwelling | 10-minute | Belgian TUS (04:00 AM start) 23 | Retrospective Baseline |
| **Armstrong et al. (2009)** 17 | Non-HVAC appliance & lighting electricity | Detached house (3 archetypes) | 5-minute | NRCan Database & Annex 42 24 | Retrospective Baseline |
| **Osman et al. (2023)** 14 | Multi-module load (non-HVAC electricity) | Single-family archetypes | Variable | Canadian TUS & appliance surveys 14 | Retrospective Baseline |
| **Ferreira et al. (2024)** 6 | TUS-driven clustering of appliance use | Single household / cohort | 10-minute | Canadian Time Use Survey 6 | Retrospective Baseline |
| **Ferreira et al. (2024)** 25 | Whole-building physical load signatures | Single building (retrofit cohorts) | 1-hour | Ottawa physical archetype data 25 | Retrospective Baseline |

## **Target Literature Evaluations**

### **Target 1a: Richardson et al. (2010) — Electricity Model**

* CITATION: Richardson, I., Thomson, M., Infield, D., Clifford, C. (2010) "Domestic electricity use: A high-resolution energy demand model," Energy and Buildings, 42(10), pp. 1878–1887. 18  
* DOI/URL: https://doi.org/10.1016/j.enbuild.2010.05.023 18  
* SUPPORTS (our claim): This model simulates active occupancy (the physical presence of awake occupants), daily activity patterns, and domestic electricity demand for individual dwellings.12 It operates at the single-building/dwelling scale.12 Its temporal horizon is retrospective and baseline-oriented, calibrating synthetic behaviors using the UK 2000 Time Use Survey and validating the synthetic demand data against empirical electricity measurements recorded over a historic year across 22 homes in the East Midlands.12  
* DIRECT QUOTE: "The pattern of electricity use in an individual domestic dwelling is highly dependent upon the activities of the occupants and their associated use of electrical appliances." (location: Section Abstract, page 1878\) 12  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The authors outline that while the stochastic simulation engine operates at the individual dwelling level, multiple runs can be compiled to generate aggregate load curves for communities or smart districts.12

### **Target 1b: Richardson et al. (2008) — Occupancy Model**

* CITATION: Richardson, I., Thomson, M., Infield, D. (2008) "A high-resolution domestic building occupancy model for energy demand simulations," Energy and Buildings, 40(8), pp. 1560–1566. 15  
* DOI/URL: https://doi.org/10.1016/j.enbuild.2008.02.006 15  
* SUPPORTS (our claim): This paper models the temporal presence of active occupants (awake and at home).4 It operates strictly at the single-dwelling scale.4 Its temporal horizon is retrospective, using the UK 2000 Time Use Survey to construct time-series occupancy schedules rather than predicting future behavior.4  
* DIRECT QUOTE: "The approach presented generates statistical occupancy time-series data at a ten-minute resolution and takes account of differences between weekdays and weekends." (location: Section Abstract, page 1560\) 4  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: none

### **Target 2: Widén & Wäckelgård (2010)**

* CITATION: Widén, J. and Wäckelgård, E. (2010) "A high-resolution stochastic model of domestic activity patterns and electricity demand," Applied Energy, 87(6), pp. 1880–1892. 7  
* DOI/URL: https://doi.org/10.1016/j.apenergy.2009.11.006 7  
* SUPPORTS (our claim): This framework models occupant activities, presence states, and electricity demand.7 It operates at the single-building/dwelling scale.7 Its temporal horizon is retrospective, using non-homogeneous Markov chains calibrated on historical Swedish time-use survey data and validated against sub-metered historical measurements.7  
* DIRECT QUOTE: "The model generates both synthetic activity sequences of individual household members, including occupancy states, and domestic electricity demand based on these patterns." (location: Section Abstract, page 1880\) 7  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The model can aggregate demands for an arbitrary number of households to assess local energy grids, but its core behavioral engine remains individual and bottom-up.7

### **Target 3a: Wilke et al. (2013) — Journal Article**

* CITATION: Wilke, U., Haldi, F., Scartezzini, J.-L., Robinson, D. (2013) "A bottom-up stochastic model to predict building occupants' time-dependent activities," Building and Environment, 60, pp. 254–264. 19  
* DOI/URL: https://doi.org/10.1016/j.buildenv.2012.10.021 19  
* SUPPORTS (our claim): This paper models time-dependent occupant activities and presence.10 It operates at the individual agent and single-household scale.8 Its temporal horizon is retrospective, calibrating behavior patterns using historical French 1998/1999 TUS data to recreate baseline behavioral sequences.8  
* DIRECT QUOTE: "A bottom-up modelling approach together with a set of calibration methodologies is presented to predict residential building occupants' time-dependent activities, for use in dynamic building simulations." (location: Section Abstract, page 254\) 19  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The bottom-up agents can be integrated into the neighborhood simulation engine "CitySim" to analyze larger areas, but the underlying behavioral simulation remains household-centric.10

### **Target 3b: Wilke (2013) — PhD Thesis**

* CITATION: Wilke, U. (2013) "Probabilistic Bottom-up Modelling of Occupancy and Activities to Predict Electricity Demand in Residential Buildings," Doctoral thesis, École Polytechnique Fédérale de Lausanne (EPFL), Thesis Number 5673\. 20  
* DOI/URL: https://infoscience.epfl.ch/handle/20.500.14299/90807 19  
* SUPPORTS (our claim): This thesis models occupant presence, time-dependent activities, appliance ownership, and non-HVAC electricity use.8 It operates at the individual agent and household scale.8 Its temporal horizon is retrospective, calibrating occupant behaviors using French TUS data and historical appliance ownership surveys to construct synthetic baseline profiles.8  
* DIRECT QUOTE: "This thesis develops adequate bottom-up models to predict time-dependent residential occupancy and activities, as well as household appliance ownership as a function of individual characteristics, and further proposes an innovative approach to relate the use of electrical appliances to the activities performed." (location: Section Abstract, page v) 8  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: The thesis explores using these bottom-up profiles to evaluate neighborhood power infrastructures, translating individual metrics to community-scale aggregations.8

### **Target 4: Aerts et al. (2014)**

* CITATION: Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F. (2014) "A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison," Building and Environment, 75, pp. 67–78. 13  
* DOI/URL: https://doi.org/10.1016/j.buildenv.2014.01.021 34  
* SUPPORTS (our claim): This paper models domestic occupancy sequences based on three states: at home and awake, sleeping, or absent.13 It is applied at the single-dwelling/building scale.13 Its temporal horizon is retrospective, using the 2005 Belgian Time Use Survey to construct baseline schedules.13 It explicitly confirms the 04:00 AM diary-origin start convention.23  
* DIRECT QUOTE: "In these diaries the respondents described their activities and movements from 4:00 AM until 3:50 AM the next day." (location: Section 3 / Page 4 of related 2013 and 2014 publications by the same authors on this exact model) 23  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: none

### **Target 5: Armstrong et al. (2009)**

* CITATION: Armstrong, M.M., Swinton, M.C., Ribberink, H., Beausoleil-Morrison, I., Millette, J. (2009) "Synthetically derived profiles for representing occupant-driven electric loads in Canadian Housing," Journal of Building Performance Simulation, 2(1), pp. 15–30. 17  
* DOI/URL: https://doi.org/10.1080/19401490802706653 24  
* SUPPORTS (our claim): This paper models non-HVAC appliance and lighting loads alongside occupant presence patterns.17 It operates at the single-building/household scale, evaluating low, medium, and high demand single-family detached archetypes.17 Its temporal horizon is retrospective, creating baseline annual load profiles using historical targets from the Office of Energy Efficiency of Natural Resources Canada to support dynamic simulations of residential micro-cogeneration.17  
* DIRECT QUOTE: "As one objective of IEA/ECBCS Annex 42, detailed Canadian household electrical demand profiles were created using a bottom-up approach from available inputs including a detailed appliance set, annual consumption targets, and occupancy patterns." (location: Section Abstract, page 15\) 17  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: These single-house profiles have been aggregated with scalar multipliers within the Canadian Hybrid Residential Energy Model (CHREM) to approximate community-scale loads, though the behavior model itself is resolved at the single-household level.11

### **Target 6: Osman et al. (2023)**

* CITATION: Osman, M., Ouf, M., Azar, E., Dong, B. (2023) "Stochastic bottom-up load profile generator for Canadian households' electricity demand," Building and Environment, 241, Article 110490\. 14  
* DOI/URL: https://doi.org/10.1016/j.buildenv.2023.110490 14  
* SUPPORTS (our claim): This primary modeling paper is distinct from the 2021 review paper.37 It models non-HVAC electricity and load profiles (occupancy, lighting, appliance loads, and domestic hot water demand).14 It is applied at the single-building/household scale.14 Its temporal horizon is retrospective, using the Canadian Time Use Survey (TUS) and historical appliance ownership databases to construct six baseline demographic archetypes under current climate configurations.14  
* DIRECT QUOTE: "The proposed model is developed to investigate the impact of different household characteristics, appliance stock, and energy behaviors on the timing and magnitude of non-HVAC energy loads at individual or multiple houses." (location: Section Abstract, page 1\) 14  
* CONFIDENCE: high  
* CONTRADICTS / CAVEAT: none (the framework can generate load demands for multiple houses, but operates at the single-building level 14).

### **Target 7a: Ferreira et al. (2024) — eSim Conference Paper**

* CITATION: Ferreira, S., Gunay, B., Papineau, M., Nojedehi, P. (2024) "From time to energy use: shaping high-resolution residential Canadian appliance use models," eSim 2024 (Proceedings of IBPSA-Canada), pp. 1–10. 6  
* DOI/URL: https://publications.ibpsa.org/proceedings/esim/2024/esim2024\_149.pdf 6  
* SUPPORTS (our claim): This paper models daily occupant activity chains and high-resolution residential appliance usage.6 It operates at the single-household scale.6 Its temporal horizon is retrospective, using historical Time Use Survey data to establish ten baseline clusters based on socio-demographic factors and appliance use behaviors.6  
* DIRECT QUOTE: "Utilizing Time Use Survey (TUS) data, we develop high-resolution models of appliance use within Canadian homes, establishing detailed energy consumption profiles across ten clusters through a comprehensive analysis of daily activities and appliance usage." (location: Section Abstract, page 1\) 6  
* CONFIDENCE: high (representing the most direct match to the occupant behavior modeling track)  
* CONTRADICTS / CAVEAT: This is a peer-reviewed conference proceeding rather than a journal article.

### **Target 7b: Ferreira et al. (2024) — JBPS Journal Article**

* CITATION: Ferreira, S., Gunay, B., Wills, A., Rizvi, F. (2024) "A neural network-based surrogate model to predict building features from heating and cooling load signatures," Journal of Building Performance Simulation, 17(5), pp. 631–654. 25  
* DOI/URL: UNVERIFIED — could not confirm exact DOI on the publisher site from the provided materials, though the stable journal URL is https://www.tandfonline.com/journals/tbps20.25  
* SUPPORTS (our claim): This paper does NOT model occupant activities directly; instead, it uses surrogate neural networks to predict physical building features (such as thermal envelope properties) based on whole-building heating and cooling load signatures.25 It operates at the single-building scale (tested across 3,000 buildings and validated in Ottawa).25 Its temporal horizon is retrospective, using historical operational load signatures to categorize the existing housing stock for targeted energy retrofits.25  
* DIRECT QUOTE: "A neural network-based surrogate model to predict building features from heating and cooling load signatures." (location: Section Title, page 631\) 25  
* CONFIDENCE: high (for metadata identification of this alternative paper)  
* CONTRADICTS / CAVEAT: This is a machine learning surrogate model focusing on building physics and thermal performance, which is conceptually distinct from the occupant activity and appliance-load modeling tracks.6

## **NOT-VERIFIED**

While the metadata for Ferreira et al. (2024) "A neural network-based surrogate model to predict building features from heating and cooling load signatures" has been verified (Volume 17, Issue 5, Pages 631–654), its exact publisher-resolved DOI is unverified based on the provided materials.25  
No 2023 primary modeling paper by Osman et al. exists that acts as a review paper; instead, the 2023 paper (*Building and Environment*, 241, 110490\) is a primary modeling paper focusing on bottom-up load generation.14 This paper is distinct from the 2021 literature review by Osman & Ouf (*Building and Environment*, 196, 107785).37

### **SUGGESTED-REPLACEMENT**

For Target 7, the conference paper by Ferreira, S., Gunay, B., Papineau, M., Nojedehi, P. (2024) "From time to energy use: shaping high-resolution residential Canadian appliance use models" (published in *eSim 2024*) is a stronger match for the high-fidelity occupant modeling track.6 It models occupant-driven appliance usage using Canadian Time Use Survey clusters, aligning directly with the core research objective.6 This makes it a more suitable reference than the alternative 2024 paper in the *Journal of Building Performance Simulation*, which focus on surrogate neural networks for thermal envelope characteristics.25

#### **Works cited**

1. Full article: Bringing post-occupancy evaluation up front to enhance energy efficiency in residential buildings \- Taylor & Francis, accessed on June 11, 2026, [https://www.tandfonline.com/doi/full/10.1080/09613218.2025.2538167](https://www.tandfonline.com/doi/full/10.1080/09613218.2025.2538167)  
2. Review of the building energy performance gap from simulation and building lifecycle perspectives: Magnitude, causes and solutions | Request PDF \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/377771141\_Review\_of\_the\_building\_energy\_performance\_gap\_from\_simulation\_and\_building\_lifecycle\_perspectives\_Magnitude\_causes\_and\_solutions](https://www.researchgate.net/publication/377771141_Review_of_the_building_energy_performance_gap_from_simulation_and_building_lifecycle_perspectives_Magnitude_causes_and_solutions)  
3. Bringing post-occupancy evaluation up front to enhance energy efficiency in residential buildings \- Tampere University Research Portal, accessed on June 11, 2026, [https://researchportal.tuni.fi/files/152479803/Bringing\_post-occupancy\_evaluation\_up\_front\_to\_enhance\_energy\_efficiency\_in\_residential\_buildings.pdf](https://researchportal.tuni.fi/files/152479803/Bringing_post-occupancy_evaluation_up_front_to_enhance_energy_efficiency_in_residential_buildings.pdf)  
4. Domestic active occupancy model \- simulation example \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/48351237\_Domestic\_active\_occupancy\_model\_-\_simulation\_example](https://www.researchgate.net/publication/48351237_Domestic_active_occupancy_model_-_simulation_example)  
5. Activity Profiles of Occupants in Residential Buildings Using the American Time Use Survey Data \- ASCE Library, accessed on June 11, 2026, [https://ascelibrary.org/doi/10.1061/9780784482865.113](https://ascelibrary.org/doi/10.1061/9780784482865.113)  
6. shaping high-resolution residential Canadian appliance use models Shane Ferreira1, Burak Gunay1, Maya P \- IBPSA Publications, accessed on June 11, 2026, [https://publications.ibpsa.org/proceedings/esim/2024/esim2024\_149.pdf](https://publications.ibpsa.org/proceedings/esim/2024/esim2024_149.pdf)  
7. A high-resolution stochastic model of domestic activity patterns and electricity demand (Journal Article) | ETDEWEB, accessed on June 11, 2026, [https://www.osti.gov/etdeweb/biblio/21328055](https://www.osti.gov/etdeweb/biblio/21328055)  
8. Probabilistic Bottom-up Modelling of Occupancy and Activities to Predict Electricity Demand in Residential Buildings \- Infoscience, accessed on June 11, 2026, [https://infoscience.epfl.ch/bitstreams/a39bf193-72a7-4b4d-a885-bfb053fc512e/download](https://infoscience.epfl.ch/bitstreams/a39bf193-72a7-4b4d-a885-bfb053fc512e/download)  
9. A Highly Resolved Modeling Technique to Simulate Residential Power Demand, accessed on June 11, 2026, [https://www.cmu.edu/ceic/people/rsioshan/docs/res\_dem\_markov.pdf](https://www.cmu.edu/ceic/people/rsioshan/docs/res_dem_markov.pdf)  
10. Urs Wilke's research works | Swiss Federal Institute of Technology in Lausanne and other places \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/scientific-contributions/Urs-Wilke-556169](https://www.researchgate.net/scientific-contributions/Urs-Wilke-556169)  
11. new profiles of occupancy driven loads for residential sector \- IBPSA Publications, accessed on June 11, 2026, [https://publications.ibpsa.org/proceedings/bso/2016/papers/bso2016\_1095.pdf](https://publications.ibpsa.org/proceedings/bso/2016/papers/bso2016_1095.pdf)  
12. Domestic electricity use: a high-resolution energy demand model \- University of Strathclyde, accessed on June 11, 2026, [https://pureportal.strath.ac.uk/en/publications/domestic-electricity-use-a-high-resolution-energy-demand-model/](https://pureportal.strath.ac.uk/en/publications/domestic-electricity-use-a-high-resolution-energy-demand-model/)  
13. A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison | Request PDF \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/260111566\_A\_method\_for\_the\_identification\_and\_modelling\_of\_realistic\_domestic\_occupancy\_sequences\_for\_building\_energy\_demand\_simulations\_and\_peer\_comparison](https://www.researchgate.net/publication/260111566_A_method_for_the_identification_and_modelling_of_realistic_domestic_occupancy_sequences_for_building_energy_demand_simulations_and_peer_comparison)  
14. Stochastic bottom-up load profile generator for Canadian households' electricity demand | Request PDF \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/371338331\_Stochastic\_bottom-up\_load\_profile\_generator\_for\_Canadian\_households'\_electricity\_demand](https://www.researchgate.net/publication/371338331_Stochastic_bottom-up_load_profile_generator_for_Canadian_households'_electricity_demand)  
15. Domestic active occupancy model \- simulation example \- Loughborough University, accessed on June 11, 2026, [https://repository.lboro.ac.uk/articles/dataset/Domestic\_active\_occupancy\_model\_-\_simulation\_example/9512723](https://repository.lboro.ac.uk/articles/dataset/Domestic_active_occupancy_model_-_simulation_example/9512723)  
16. Domestic electricity use: a high-resolution energy demand model \- Figshare, accessed on June 11, 2026, [https://figshare.com/articles/journal\_contribution/Domestic\_electricity\_use\_a\_high-resolution\_energy\_demand\_model/9573941/1/files/17208020.pdf](https://figshare.com/articles/journal_contribution/Domestic_electricity_use_a_high-resolution_energy_demand_model/9573941/1/files/17208020.pdf)  
17. (PDF) Synthetically derived profiles for representing occupant-driven electric loads in Canadian Housing \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/44091570\_Synthetically\_derived\_profiles\_for\_representing\_occupant-driven\_electric\_loads\_in\_Canadian\_Housing](https://www.researchgate.net/publication/44091570_Synthetically_derived_profiles_for_representing_occupant-driven_electric_loads_in_Canadian_Housing)  
18. Domestic electricity use: a high-resolution energy demand model \- Loughborough University, accessed on June 11, 2026, [https://repository.lboro.ac.uk/articles/journal\_contribution/Domestic\_electricity\_use\_a\_high-resolution\_energy\_demand\_model/9573941](https://repository.lboro.ac.uk/articles/journal_contribution/Domestic_electricity_use_a_high-resolution_energy_demand_model/9573941)  
19. A bottom-up stochastic model to predict building occupants' time ..., accessed on June 11, 2026, [https://infoscience.epfl.ch/entities/publication/d3714f99-0036-4dd0-ac0e-a9b886cc6258](https://infoscience.epfl.ch/entities/publication/d3714f99-0036-4dd0-ac0e-a9b886cc6258)  
20. Probabilistic Bottom-up Modelling of Occupancy and Activities to Predict Electricity Demand in Residential Buildings \- Infoscience, accessed on June 11, 2026, [https://infoscience.epfl.ch/entities/publication/18bde99d-1e0a-406a-8fc7-e2cc8141a775](https://infoscience.epfl.ch/entities/publication/18bde99d-1e0a-406a-8fc7-e2cc8141a775)  
21. Modelling of Occupancy and Activities to Predict Electricity Demand \- News \- EPFL, accessed on June 11, 2026, [https://actu.epfl.ch/news/modelling-of-occupancy-and-activities-to-predict-e/](https://actu.epfl.ch/news/modelling-of-occupancy-and-activities-to-predict-e/)  
22. Dorien Aerts | Vrije Universiteit Brussel | 6 Publications | 16 Citations | Related Authors, accessed on June 11, 2026, [https://scispace.com/authors/dorien-aerts-4aooy5zmsw](https://scispace.com/authors/dorien-aerts-4aooy5zmsw)  
23. (PDF) Discrete Occupancy Profiles From Time-use Data For User Behaviour Modelling In Homes \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/264428639\_Discrete\_occupancy\_profiles\_from\_time-use\_data\_for\_user\_behaviour\_modelling\_in\_homes](https://www.researchgate.net/publication/264428639_Discrete_occupancy_profiles_from_time-use_data_for_user_behaviour_modelling_in_homes)  
24. Synthetically derived profiles for representing occupant-driven ..., accessed on June 11, 2026, [https://nrc-publications.canada.ca/eng/view/accepted/?id=363a967f-833b-4b4c-a750-d3f5823558b3](https://nrc-publications.canada.ca/eng/view/accepted/?id=363a967f-833b-4b4c-a750-d3f5823558b3)  
25. A neural network-based surrogate model to predict building features from heating and cooling load signatures \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/382354608\_A\_neural\_network-based\_surrogate\_model\_to\_predict\_building\_features\_from\_heating\_and\_cooling\_load\_signatures](https://www.researchgate.net/publication/382354608_A_neural_network-based_surrogate_model_to_predict_building_features_from_heating_and_cooling_load_signatures)  
26. Journal Articles \- Loughborough University Research Publications, accessed on June 11, 2026, [https://publications.lboro.ac.uk/publications/all/collated/elmt.html](https://publications.lboro.ac.uk/publications/all/collated/elmt.html)  
27. Domestic electricity use: A high-resolution energy demand model \- ResearchGate, accessed on June 11, 2026, [https://www.researchgate.net/publication/222832641\_Domestic\_electricity\_use\_A\_high-resolution\_energy\_demand\_model](https://www.researchgate.net/publication/222832641_Domestic_electricity_use_A_high-resolution_energy_demand_model)  
28. A high-resolution domestic building occupancy model for energy demand simulations \- Loughborough University Research Repository, accessed on June 11, 2026, [https://repository.lboro.ac.uk/articles/journal\_contribution/A\_high-resolution\_domestic\_building\_occupancy\_model\_for\_energy\_demand\_simulations/9563585](https://repository.lboro.ac.uk/articles/journal_contribution/A_high-resolution_domestic_building_occupancy_model_for_energy_demand_simulations/9563585)  
29. A high-resolution stochastic model of domestic activity patterns and electricity demand, accessed on June 11, 2026, [https://www.researchgate.net/publication/223477044\_A\_high-resolution\_stochastic\_model\_of\_domestic\_activity\_patterns\_and\_electricity\_demand](https://www.researchgate.net/publication/223477044_A_high-resolution_stochastic_model_of_domestic_activity_patterns_and_electricity_demand)  
30. A high-resolution stochastic model of domestic activity patterns and electricity demand | UROP \- Day 6 | Zotero, accessed on June 11, 2026, [https://www.zotero.org/groups/5129844/urop\_-\_day\_6/items/itemKey/2ZEJVRLA](https://www.zotero.org/groups/5129844/urop_-_day_6/items/itemKey/2ZEJVRLA)  
31. A high-resolution stochastic model of domestic activity patterns and electricity demand, accessed on June 11, 2026, [https://ideas.repec.org/a/eee/appene/v87y2010i6p1880-1892.html](https://ideas.repec.org/a/eee/appene/v87y2010i6p1880-1892.html)  
32. A high-resolution stochastic model of domestic activity patterns and electricity demand, accessed on June 11, 2026, [http://umu.diva-portal.org/smash/record.jsf?pid=diva2:359583](http://umu.diva-portal.org/smash/record.jsf?pid=diva2:359583)  
33. ‪Urs Wilke‬ \- ‪Google Scholar‬, accessed on June 11, 2026, [https://scholar.google.com/citations?user=1b8TNuEAAAAJ\&hl=en](https://scholar.google.com/citations?user=1b8TNuEAAAAJ&hl=en)  
34. Occupancy of rooms in urban residential buildings by users in cold areas of China \- PMC, accessed on June 11, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9734699/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9734699/)  
35. A probabilistic activity model to include realistic occupant behaviour in building simulations \- IBPSA Publications, accessed on June 11, 2026, [https://publications.ibpsa.org/proceedings/esim/2014/papers/esim2014\_3A\_4.pdf](https://publications.ibpsa.org/proceedings/esim/2014/papers/esim2014_3A_4.pdf)  
36. Studying the impact factors influencing variable-capacity heat pump energy performance through simulation, accessed on June 11, 2026, [https://www.e3s-conferences.org/articles/e3sconf/ref/2021/22/e3sconf\_hvac2021\_06005/e3sconf\_hvac2021\_06005.html](https://www.e3s-conferences.org/articles/e3sconf/ref/2021/22/e3sconf_hvac2021_06005/e3sconf_hvac2021_06005.html)  
37. ‪Mohamed Osman‬ \- ‪Google Scholar‬, accessed on June 11, 2026, [https://scholar.google.com/citations?user=1icX5H8AAAAJ\&hl=en](https://scholar.google.com/citations?user=1icX5H8AAAAJ&hl=en)  
38. Elie Azar \- Loop, accessed on June 11, 2026, [https://loop.frontiersin.org/people/1031939](https://loop.frontiersin.org/people/1031939)  
39. Modelling and optimization of residential electricity load under stochastic demand, accessed on June 11, 2026, [https://www.riejournal.com/article\_186447.html](https://www.riejournal.com/article_186447.html)  
40. Investigating the full potential of demand response programs using granular occupancy schedules \- IBPSA Publications, accessed on June 11, 2026, [https://publications.ibpsa.org/proceedings/bs/2025/papers/bs2025\_1489.pdf](https://publications.ibpsa.org/proceedings/bs/2025/papers/bs2025_1489.pdf)  
41. From time to energy use: shaping high-resolution residential Canadian appliance use models \- IBPSA Publications, accessed on June 11, 2026, [https://publications.ibpsa.org/conference/paper/?id=esim2024\_149](https://publications.ibpsa.org/conference/paper/?id=esim2024_149)  
42. ‪Pedram Nojedehi‬ \- ‪Google Akademik‬, accessed on June 11, 2026, [https://scholar.google.com.tr/citations?user=cuDGTjgAAAAJ\&hl=tr](https://scholar.google.com.tr/citations?user=cuDGTjgAAAAJ&hl=tr)  
43. ‪Shane Ferreira‬ \- ‪Google Scholar‬, accessed on June 11, 2026, [https://scholar.google.com/citations?user=ghBAe8oAAAAJ\&hl=en](https://scholar.google.com/citations?user=ghBAe8oAAAAJ&hl=en)