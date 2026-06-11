# 1 Introduction

This introduction proceeds as a funnel: from the building-performance gap and the static schedules that sustain it (§1.1), through the two largely disconnected modelling traditions that frame the problem (§1.2), to the non-stationarity of occupant behaviour that neither tradition is positioned to forecast (§1.3); it then states the authors' prior line as the explicit departure point (§1.4) and closes with the contributions and aim of the present study (§1.5).

---

### 1.1 The Performance Gap and Static Occupancy Schedules

The persistent discrepancy between predicted and measured building energy use — the "performance gap" — remains one of the central credibility problems of building performance simulation (de Wilde, 2014), and occupant behaviour is now widely identified as its dominant unexplained driver (Yan et al., 2015; Hong et al., 2017). The international research agenda has recognised this explicitly through IEA EBC Annex 66 and its successor Annex 79 on occupant-centric building design and operation (Wagner et al., 2020). Yet routine practice still leans on static, deterministic occupancy and diversity schedules drawn from ASHRAE and national reference standards, an assumption that is especially ill-suited to residential buildings, where daily life is governed by stochastic individual routines rather than regulated operation (Mahdavi et al., 2021). Deterministic models that rely on these fixed schedules systematically fail to capture behavioural stochasticity and have been associated with energy discrepancies of up to 41 % (Wilke, Haldi and Robinson, 2011; Mitra, Chu and Cetin, 2020; Elsayed et al., 2023). The emphasis of the present work is that static schedules are blind not only to a *magnitude* error in annual energy but to a *timing* error in the diurnal load shape — the quantity that matters most for grids, ramping, and demand response, and the one a single annual-energy comparison can never reveal.

---

### 1.2 Two Tracks That Rarely Meet: High-Fidelity Occupant Models versus Stock-Scale Engines

Two research traditions address occupancy in building energy modelling, and they rarely meet. The first develops high-fidelity stochastic occupant models — Markov-chain, survival-model, and time-use-survey-based generators of presence and activity — but applies them predominantly at the single-building scale and retrospectively (Richardson, Thomson and Infield, 2008; Widén and Wäckelgård, 2010; Wilke et al., 2013; Aerts et al., 2014), including a growing Canadian strand (Armstrong et al., 2009; Osman and Ouf, 2021; Ferreira et al., 2024). The second runs stock- and urban-scale energy engines across thousands of dwellings but feeds them simplified, baseline-year schedules (Reinhart and Cerezo Davila, 2016), with the paired stock-scale simulation design of Chen et al. (2022) the closest methodological precedent to the present work. The two tracks rarely meet, a disconnection that the six-dimension gap matrix of Table 1 makes explicit. Read across the matrix, Chen et al. (2022) is the nearest competitor but is retrospective, and Yin et al. (2025) is the nearest on forecasting yet stops at statistical probability modelling with no bottom-up simulation. The open cell that neither occupies is a calibrated behavioural occupancy series forecast to 2030 *through* the work-from-home break and carried into stock-scale paired building-energy simulation of the resulting load shape.

**Table 1.** *(insert `Table_01_gap_matrix.md` here)* — Six-dimension capability matrix scoring external competitors on time-series occupancy, calibrated behavioural model, forecast to a future year, activity- and end-use resolution, stock-scale simulation, and load-shape/peak focus; the all-✓ "This study" row identifies the open cell that the paper fills.

---

### 1.3 Behaviour Is Non-Stationary, and the Field Forecasts off the Wrong Baseline

The premise that occupant behaviour is stationary failed at the COVID-19 pandemic, and the failure is structural rather than transient. Work-from-home has settled at roughly twice its pre-pandemic prevalence and shows every sign of persisting (Barrero, Bloom and Davis, 2021; Guo et al., 2026); weekday residential electricity profiles have taken on a weekend-like shape, with a weather-adjusted increase on the order of +7.9 % in residential electricity use through the pandemic (Cicala, 2023). Forecasting occupancy *through* this break, rather than extrapolating from a pre-pandemic baseline, has been flagged as an open problem in its own right (Bielskus et al., 2021; Yin et al., 2025). The consequence for energy modelling is direct: any projection of residential demand to 2030 that is anchored to a pre-COVID occupancy baseline inherits the structural break as a systematic bias, mis-estimating not only how much energy is used but when.

---

### 1.4 The Authors' Prior Line: The Departure Point

The present study departs from a specific prior line of work by the authors. A conditional variational-autoencoder (C-VAE) pipeline, paired with a cluster-based vector-momentum scheme, was developed to synthesise longitudinally consistent Canadian residential occupancy schedules from successive General Social Survey (GSS) time-use cycles and to carry them into building energy simulation: a journal treatment across six Montréal neighbourhood-unit typologies in climate Zone 6A over 2005–2025 (Iseri and Hachem-Vermette, under review), a companion conference study across three climate-zone cities (Iseri and Hachem-Vermette, 2026), and a related population-statistics-and-machine-learning occupancy framework (Iseri, Dino and Kalkan, 2026). That line established what this paper does not re-claim: that survey-grounded, time-series occupancy can be generated for Canadian building energy models and that it moves annual demand relative to default assumptions — increasing predicted heating demand by roughly +4 to +13 % and reducing cooling demand by roughly −10 to −27 % — together with a first look at the diurnal and peak consequences.[^selfdelta] The contribution of the present paper is to advance that line on four specific axes, set out in §1.5, while treating its core premise — time-series GSS occupancy in Canadian BEM — as established rather than novel.

---

### 1.5 Contributions and Aim of the Study

This paper makes four advances over the authors' prior line, one per pipeline stage.

1. **Generator.** The C-VAE is replaced by a hard-gate-selected hybrid autoregressive/non-autoregressive conditional Transformer with post-hoc marginal calibration ("calibrated J3") — the only model to clear all four distributional gates in a search of more than forty trials that included masked discrete diffusion (MDLM/SEDD) — preserving the sharp activity peaks that a variational autoencoder tends to smooth.
2. **Loads.** Presence-filtered default end uses are replaced by an SHEU-calibrated, activity-resolved bottom-up end-use model (presence, co-presence, and equipment), matching the national survey benchmark within ±2.7 % in all forty-eight dwelling-by-year cells (maximum +2.33 % equipment, +2.63 % lighting).
3. **Horizon and validation.** A 2025 hindcast is replaced by a 2030 forecast carried *through* the structural break and validated under a True-Future-Test protocol that evaluates each cycle against the next unseen one.
4. **Attribution.** Sum-of-squared-error-matched per-scenario ensembles are replaced by a paired within-household Monte-Carlo design — the same fifty households simulated across all five cycle-years — yielding 6,000 EnergyPlus runs whose within-household differencing isolates the behavioural signal.

The aim of the study follows directly. *This paper asks whether, and when, forecast behavioural change reshapes the residential load curve at stock scale.* The full pipeline that operationalises this question is summarised in Figure 1, with each stage detailed in the sections that follow: the datasets (§2), the methods spanning harmonization through activity-resolved loads (§3), the paired experimental design (§4), the results from behavioural driver to end-use timing (§5), and the discussion, limitations, and conclusion (§6–§8).

**Figure 1.** *(insert `Figure_01_pipeline.png` here)* — **End-to-end occupancy-to-energy pipeline (Steps 1–9).** Block schematic from the four GSS Time-Use cycles and the Census PUMF through harmonization and 30-minute diary construction, generative day-type augmentation, Census linkage, longitudinal forecasting to 2030, BEM schedule conversion, paired Monte-Carlo simulation, and activity-resolved end-use loads; each block labelled with its section number and the key validation gate it passes.

[^selfdelta]: Two self-delta cross-checks anchor the prior line to this paper's corrected pipeline and are kept deliberately distinct. First, the prior journal study independently places the equipment (appliance-driven) electricity peak in the evening, at 17:00–18:00, which is the clock-correct anchor that this paper's corrected simulation pipeline reproduces. Second, the companion conference study reports a descriptive "−4 h" difference in the argmax of the occupancy schedule (a default-schedule peak at 00:00 against a GSS-derived peak at 04:00, both overnight); this is a schedule-shape argmax comparison and is unrelated to the four-hour schedule-injection artefact identified and corrected in the present work (§4.2, §7.1) — the two four-hour quantities must not be conflated.

---

## References (this chapter)

*Chapter 1 is reference-heavy. Citations are carried as in-text cross-references; the entries below are grouped by verification status. The external-literature group must be reconciled before submission against the master bibliography (the verified DOI list in `methodology_assessment_and_paper_skeleton.md`, Part 5) and against the Chapter-1 deep-research prompts in `DR_prompts_chapter1_introduction.md`.*

**Self-citations (the departure point)**

- Iseri, O. and Hachem-Vermette, C. (under review) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials.* Journal of Building Performance Simulation. — *(verify final citation form / status against master bibliography)*
- Iseri, O. and Hachem-Vermette, C. (2026) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* (companion conference paper). eSim 2026, IBPSA-Canada. — *(verify final citation form / venue against master bibliography)*
- Iseri, O.K., Dino, I.G. and Kalkan, S. (2026) Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 117155. https://doi.org/10.1016/j.enbuild.2026.117155.

**Grounded from the prior papers' reference lists** *(DOIs carried over verbatim; spot-check at typesetting):*

- Pérez-Lombard, L., Ortiz, J. and Pout, C. (2008) A review on buildings energy consumption information. *Energy and Buildings*, 40(3), pp. 394–398. https://doi.org/10.1016/j.enbuild.2007.03.007.
- Wilke, U., Haldi, F. and Robinson, D. (2011) A model of occupants' activities based on time use survey data. *Proceedings of Building Simulation 2011*, IBPSA.
- Hong, T., Yan, D., D'Oca, S. and Chen, C. (2017) Ten questions concerning occupant behavior in buildings: The big picture. *Building and Environment*, 114, pp. 518–530. https://doi.org/10.1016/j.buildenv.2016.12.006.
- Mitra, D., Chu, Y. and Cetin, K. (2020) Activity Profiles of Occupants in Residential Buildings Using the American Time Use Survey Data. https://doi.org/10.1061/9780784482865.113.
- Wagner, A., Schweiker, M., Mahdavi, A., Yan, D., Hong, T., Nagy, Z. and Shah, S. (2020) Introducing IEA EBC Annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation. *Building and Environment*. — *(verify volume/pages/DOI against master bibliography)*
- Mahdavi, A. et al. (2021) The Role of Occupants in Buildings' Energy Performance Gap: Myth or Reality? *Sustainability*, 13(6), 3146. https://doi.org/10.3390/su13063146.
- Vellei, M. et al. (2022) Documenting occupant models for building performance simulation: a state-of-the-art. *Journal of Building Performance Simulation*, 15, pp. 634–655. https://doi.org/10.1080/19401493.2022.2061050.
- Elsayed, M. et al. (2023) Post-occupancy evaluation in residential buildings: A systematic literature review of current practices in the EU. *Building and Environment*, 236, 110307. https://doi.org/10.1016/j.buildenv.2023.110307.
- Osman, M. and Ouf, M. (2021) A comprehensive review of time use surveys in modelling occupant presence and behavior. *Building and Environment*, 196, 107785. https://doi.org/10.1016/j.buildenv.2021.107785.
- Richardson, I., Thomson, M. and Infield, D. (2008) A high-resolution domestic building occupancy model for energy demand simulations. *Energy and Buildings*, 40(8), pp. 1560–1566. https://doi.org/10.1016/j.enbuild.2008.02.006.

**External literature requiring deep-research verification** *(see `DR_prompts_chapter1_introduction.md`; several already have verified DOIs in the methodology-assessment Part 5 — reconcile, do not duplicate):*

- de Wilde, P. (2014) — the building performance gap.
- Yan, D. et al. (2015) — occupant behaviour modelling in building performance simulation.
- IEA EBC Annex 66 (occupant behaviour) — programmatic reference.
- O'Brien, W. et al. (2020) — occupant-centric building performance / Annex 79 synthesis.
- Richardson, I., Thomson, M., Infield, D. and Clifford, C. (2010) — domestic electricity-use high-resolution model.
- Widén, J. and Wäckelgård, E. (2010) — high-resolution stochastic household activity/electricity model.
- Wilke, U. et al. (2013) — bottom-up stochastic occupant-activity model (thesis/journal form).
- Aerts, D. et al. (2014) — domestic occupancy sequences for building energy simulation.
- Armstrong, M.M. et al. (2009) — Canadian residential occupancy/load modelling.
- Osman, M. et al. (2023) — Canadian time-use-based occupancy modelling.
- Ferreira, ... et al. (2024) — recent Canadian occupancy/load strand.
- Reinhart, C.F. and Cerezo Davila, C. (2016) — urban building energy modelling review.
- Chen, Y. et al. (2022) — paired stock-scale building energy simulation (closest methodological precedent).
- Yin, ... et al. (2025) — occupancy forecasting through the structural break (statistical, no bottom-up simulation).
- Barrero, J.M., Bloom, N. and Davis, S.J. (2021) — work-from-home persistence (NBER WP 28731).
- Cicala, S. (2023) — pandemic-era residential electricity demand (weather-adjusted +7.9 %).
- Guo, ... et al. (2026) — work-from-home prevalence/persistence.
- Bielskus, J. et al. (2021) — occupancy forecasting / prediction under disruption.
- Statistics Canada — population projections (M1 scenario) and GSS/Census catalogue references.
