# 1 Introduction

This introduction proceeds as a funnel: from the building-performance gap and the static schedules that sustain it (§1.1), through the two largely disconnected modelling traditions that frame the problem (§1.2), to the non-stationarity of occupant behaviour that neither tradition is positioned to forecast (§1.3); it then states the authors' prior line as the explicit departure point (§1.4) and closes with the contributions and aim of the present study (§1.5).

---

### 1.1 The Performance Gap and Static Occupancy Schedules

The persistent discrepancy between predicted and measured building energy use — the "performance gap" — remains one of the central credibility problems of building performance simulation (de Wilde, 2014), and occupant behaviour is now widely identified as its dominant unexplained driver (Yan et al., 2015; Hong et al., 2017). The international research agenda has recognised this explicitly through IEA EBC Annex 66 and its successor Annex 79 on occupant-centric building design and operation (Yan et al., 2017; O'Brien et al., 2020). Yet routine practice still leans on static, deterministic occupancy and diversity schedules drawn from ASHRAE and national reference standards, an assumption that is especially ill-suited to residential buildings, where daily life is governed by stochastic individual routines rather than regulated operation (Mahdavi et al., 2021). Deterministic models that rely on these fixed schedules systematically fail to capture behavioural stochasticity (Wilke, Haldi and Robinson, 2011; Elsayed et al., 2023), and survey-derived residential occupancy profiles have been shown to differ from standard reference schedules by up to 41 % at individual hours — a discrepancy in *when* occupants are home, not in annual energy magnitude (Mitra et al., 2020). The emphasis of the present work is that static schedules are blind not only to a *magnitude* error in annual energy but to a *timing* error in the diurnal load shape — the quantity that matters most for grids, ramping, and demand response, and the one a single annual-energy comparison can never reveal.

---

### 1.2 Two Tracks That Rarely Meet: High-Fidelity Occupant Models versus Stock-Scale Engines

Two research traditions address occupancy in building energy modelling, and they rarely meet. The first develops high-fidelity stochastic occupant models — Markov-chain, survival-model, and time-use-survey-based generators of presence and activity — but applies them predominantly at the single-building scale and retrospectively (Richardson, Thomson and Infield, 2008; Widén and Wäckelgård, 2010; Wilke et al., 2013; Aerts et al., 2014), including a growing Canadian strand (Armstrong et al., 2009; Osman and Ouf, 2021; Ferreira et al., 2024). The second runs stock- and urban-scale energy engines across thousands of dwellings but feeds them simplified, baseline-year schedules (Reinhart and Cerezo Davila, 2016), with the paired stock-scale simulation design of Chen et al. (2022) the closest methodological precedent to the present work. The two tracks rarely meet, a disconnection that the six-dimension gap matrix of Table 1 makes explicit. Read across the matrix, Chen et al. (2022) is the nearest competitor on calibrated behavioural simulation but is retrospective; Yin et al. (2024) statistically characterises long-term (2001–2021) change in time-use behaviour — the very premise this paper builds on — yet stops at the analysis stage, neither forecasting forward nor running building-energy simulation, and explicitly names stock-scale energy projection as future work; and the nearest stock-scale forecaster, Jalilian and Kamel (2025), projects decades ahead yet holds occupant behaviour static, assuming pre-pandemic schedules persist unchanged. The open cell that none occupies is a calibrated behavioural occupancy series forecast to 2030 *through* the work-from-home break and carried into stock-scale paired building-energy simulation of the resulting load shape.

**Table 1.** *(insert `Table_01_gap_matrix.md` here)* — Six-dimension capability matrix scoring external competitors on time-series occupancy, calibrated behavioural model, forecast to a future year, activity- and end-use resolution, stock-scale simulation, and load-shape/peak focus; the all-✓ "This study" row identifies the open cell that the paper fills.

---

### 1.3 Behaviour Is Non-Stationary, and the Field Forecasts off the Wrong Baseline

The premise that occupant behaviour is stationary failed at the COVID-19 pandemic, and the failure is structural rather than transient. Work-from-home has settled at roughly four times its pre-pandemic prevalence — about 20 % of full workdays after the pandemic against 5 % before (Barrero, Bloom and Davis, 2021) — and shows every sign of persisting at a new hybrid-work equilibrium (Guo et al., 2026). Weekday residential electricity profiles have correspondingly lost their bimodal commuting peaks and taken on a weekend-like shape (Abdeen et al., 2021), accompanied by a weather-adjusted increase on the order of +7.9 % in residential electricity use through the pandemic (Cicala, 2023). Forecasting occupancy *through* this break, rather than extrapolating from a pre-pandemic baseline, has been flagged as an open problem in its own right: occupancy-prediction models trained on pre-pandemic data degrade sharply once the break is crossed (Motuzienė et al., 2022). The consequence for energy modelling is direct: any projection of residential demand to 2030 that is anchored to a pre-COVID occupancy baseline inherits the structural break as a systematic bias, mis-estimating not only how much energy is used but when.

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

*Chapter 1 is reference-heavy; citations are carried as in-text cross-references. The external-literature entries below were verified by the Chapter-1 deep-research pass (June 2026; full reports in `deepResearch/`), with DOIs and venues confirmed and several corrections applied (noted inline). Reconcile once more against the manuscript master bibliography at typesetting.*

**Self-citations (the departure point)**

- Iseri, O. and Hachem-Vermette, C. (under review) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials.* Journal of Building Performance Simulation. — *(verify final citation form / status against master bibliography)*
- Iseri, O. and Hachem-Vermette, C. (2026) *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* (companion conference paper). eSim 2026, IBPSA-Canada. — *(verify final citation form / venue against master bibliography)*
- Iseri, O.K., Dino, I.G. and Kalkan, S. (2026) Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 117155. https://doi.org/10.1016/j.enbuild.2026.117155.

**Performance gap and occupant behaviour (§1.1)**

- de Wilde, P. (2014) The gap between predicted and measured energy performance of buildings: A framework for investigation. *Automation in Construction*, 41, pp. 40–49. https://doi.org/10.1016/j.autcon.2014.02.009.
- Yan, D., O'Brien, W., Hong, T., Feng, X., Gunay, H.B., Tahmasebi, F. and Mahdavi, A. (2015) Occupant behavior modeling for building performance simulation: Current state and future challenges. *Energy and Buildings*, 107, pp. 264–278. https://doi.org/10.1016/j.enbuild.2015.08.032. — *(DR note: venue is* Energy and Buildings*, not* Building and Environment*; page range to spot-check at typesetting.)*
- Hong, T., Yan, D., D'Oca, S. and Chen, C. (2017) Ten questions concerning occupant behavior in buildings: The big picture. *Building and Environment*, 114, pp. 518–530. https://doi.org/10.1016/j.buildenv.2016.12.006.
- Yan, D., Hong, T., Dong, B., Mahdavi, A., D'Oca, S., Gaetani, I. and Feng, X. (2017) IEA EBC Annex 66: Definition and simulation of occupant behavior in buildings. *Energy and Buildings*, 156, pp. 258–270. https://doi.org/10.1016/j.enbuild.2017.09.084.
- O'Brien, W., Wagner, A., Schweiker, M., Mahdavi, A., Day, J., Kjærgaard, M.B., Carlucci, S., Dong, B., Tahmasebi, F., Yan, D., Hong, T., Gunay, H.B., Nagy, Z., Miller, C. and Berger, C. (2020) Introducing IEA EBC Annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation. *Building and Environment*, 178, 106738. https://doi.org/10.1016/j.buildenv.2020.106738. — *(DR correction: lead author is O'Brien, not Wagner.)*
- Mahdavi, A. et al. (2021) The Role of Occupants in Buildings' Energy Performance Gap: Myth or Reality? *Sustainability*, 13(6), 3146. https://doi.org/10.3390/su13063146.
- Mitra, D., Steinmetz, N., Chu, Y. and Cetin, K.S. (2020) Typical occupancy profiles and behaviors in residential buildings in the United States. *Energy and Buildings*, 210, 109713. https://doi.org/10.1016/j.enbuild.2019.109713. — *(DR correction: the "up to 41 %" figure denotes hourly occupancy-presence differences relative to ASHRAE 90.1 schedules, not an energy-magnitude discrepancy, and traces to this paper only — not to Wilke 2011 or Elsayed 2023.)*
- Wilke, U., Haldi, F. and Robinson, D. (2011) A model of occupants' activities based on time use survey data. *Proceedings of Building Simulation 2011*, IBPSA.
- Elsayed, M. et al. (2023) Post-occupancy evaluation in residential buildings: A systematic literature review of current practices in the EU. *Building and Environment*, 236, 110307. https://doi.org/10.1016/j.buildenv.2023.110307.
- Pérez-Lombard, L., Ortiz, J. and Pout, C. (2008) A review on buildings energy consumption information. *Energy and Buildings*, 40(3), pp. 394–398. https://doi.org/10.1016/j.enbuild.2007.03.007.

**High-fidelity occupant models — §1.2 track (a)**

- Richardson, I., Thomson, M. and Infield, D. (2008) A high-resolution domestic building occupancy model for energy demand simulations. *Energy and Buildings*, 40(8), pp. 1560–1566. https://doi.org/10.1016/j.enbuild.2008.02.006.
- Richardson, I., Thomson, M., Infield, D. and Clifford, C. (2010) Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings*, 42(10), pp. 1878–1887. https://doi.org/10.1016/j.enbuild.2010.05.023.
- Widén, J. and Wäckelgård, E. (2010) A high-resolution stochastic model of domestic activity patterns and electricity demand. *Applied Energy*, 87(6), pp. 1880–1892. https://doi.org/10.1016/j.apenergy.2009.11.006.
- Wilke, U., Haldi, F., Scartezzini, J.-L. and Robinson, D. (2013) A bottom-up stochastic model to predict building occupants' time-dependent activities. *Building and Environment*, 60, pp. 254–264. https://doi.org/10.1016/j.buildenv.2012.10.021.
- Aerts, D., Minnen, J., Glorieux, I., Wouters, I. and Descamps, F. (2014) A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. *Building and Environment*, 75, pp. 67–78. https://doi.org/10.1016/j.buildenv.2014.01.021.
- Armstrong, M.M., Swinton, M.C., Ribberink, H., Beausoleil-Morrison, I. and Millette, J. (2009) Synthetically derived profiles for representing occupant-driven electric loads in Canadian housing. *Journal of Building Performance Simulation*, 2(1), pp. 15–30. https://doi.org/10.1080/19401490802706653.
- Osman, M. and Ouf, M. (2021) A comprehensive review of time use surveys in modelling occupant presence and behavior. *Building and Environment*, 196, 107785. https://doi.org/10.1016/j.buildenv.2021.107785.
- Osman, M., Ouf, M., Azar, E. and Dong, B. (2023) Stochastic bottom-up load profile generator for Canadian households' electricity demand. *Building and Environment*, 241, 110490. https://doi.org/10.1016/j.buildenv.2023.110490. — *(DR note: primary modelling paper, distinct from the Osman & Ouf 2021 review above.)*
- Ferreira, S., Gunay, B., Papineau, M. and Nojedehi, P. (2024) From time to energy use: shaping high-resolution residential Canadian appliance use models. *eSim 2024 (IBPSA-Canada)*. https://publications.ibpsa.org/proceedings/esim/2024/esim2024_149.pdf.

**Stock-scale engines and forecasting competitors — §1.2 track (b)**

- Reinhart, C.F. and Cerezo Davila, C. (2016) Urban building energy modeling — A review of a nascent field. *Building and Environment*, 97, pp. 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001.
- Chen, J., Adhikari, R., Wilson, E., Robertson, J., Fontanini, A., Polly, B. and Olawale, O. (2022) Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model. *Applied Energy*, 325, 119890. https://doi.org/10.1016/j.apenergy.2022.119890. — *(DR note: first author Jianli Chen [cited as "Chen et al."]; closest paired stock-scale precedent — all six matrix dimensions met except future-year forecasting.)*
- Yin, R., Yamaguchi, Y., Zajch, A.M., Uchida, H. and Shimoda, Y. (2024) Long-term changes in time use and impacts on residential energy demand. *Proc. ASim 2024, 5th Asia Conference of IBPSA*, Osaka, Japan, 8–10 December 2024, pp. 1321–1328 (paper E17_asim2024_1285). — *(Verified against the source: a logistic-regression analysis of long-term Japanese time-use change 2001–2021 by the Osaka group; it does NOT forecast to a future year and runs NO building-energy simulation — both are named as future work — so it tracks this paper's premise but stops at statistics. Earlier mis-cited as "Yin et al. 2025"; correct venue/year is ASim 2024 Osaka. IBPSA proceedings DOI to confirm at typesetting.)*
- Jalilian, M. and Kamel, R. (2025) Urban-scale building energy modeling under future climate scenarios. *Frontiers in Energy Research*, 13, 1683787. https://doi.org/10.3389/fenrg.2025.1683787. — *(DR note: nearest purely stock-scale future-year forecaster, but holds occupancy static — Nassau County, NY, 346,827 buildings under 2099 climate scenarios.)*

**Behavioural non-stationarity at the structural break (§1.3)**

- Barrero, J.M., Bloom, N. and Davis, S.J. (2021) Why working from home will stick. *NBER Working Paper No. 28731*. https://doi.org/10.3386/w28731. — *(DR correction: WFH settles at 20 % of full workdays vs 5 % before — a roughly fourfold, not twofold, shift.)*
- Guo, N., Jiang, W., Pothuru, Y. and Yang, B. (2026) Mapping the midweek mountain: The new geography of hybrid work. *arXiv:2603.18440*. https://doi.org/10.48550/arXiv.2603.18440.
- Cicala, S. (2023) JUE Insight: Powering work from home. *Journal of Urban Economics*, 133, 103474. https://doi.org/10.1016/j.jue.2022.103474.
- Khalil, M.A. and Fatmi, M.R. (2022) How residential energy consumption has changed due to COVID-19 pandemic? An agent-based model. *Sustainable Cities and Society*, 81, 103832. https://doi.org/10.1016/j.scs.2022.103832.
- Motuzienė, V., Bielskus, J., Lapinskienė, V., Rynkun, G. and Bernatavičienė, J. (2022) Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic. *Sustainable Cities and Society*, 76, 103557. https://doi.org/10.1016/j.scs.2021.103557. — *(DR correction: replaces the earlier short form "Bielskus et al. 2021"; R² of a pre-pandemic-trained model falls to 0.27–0.56 across the break.)*
- Abdeen, A., Kharvari, F., O'Brien, W. and Gunay, B. (2021) The impact of the COVID-19 on households' hourly electricity consumption in Canada. *Energy and Buildings*, 250, 111280. https://doi.org/10.1016/j.enbuild.2021.111280. — *(DR addition: Canadian smart-meter evidence that weekday profiles became weekend-like after the break.)*

**Other supporting reference**

- Vellei, M. et al. (2022) Documenting occupant models for building performance simulation: a state-of-the-art. *Journal of Building Performance Simulation*, 15, pp. 634–655. https://doi.org/10.1080/19401493.2022.2061050.

**Statistics Canada data sources** — full catalogue metadata (GSS Time Use Cat. 45-25-0001 / DOI 10.25318/45250001-eng; 2021 Census PUMF Cat. 98M0001X; population projections M1 Cat. 17-20-0003) is given with the dataset descriptions in §2 and §3 and is not duplicated here.

**Citation correction (formerly flagged "removed")**

- **"Yin et al. (2025)" → Yin et al. (2024) — corrected, not removed.** The Chapter-1 deep-research pass was handed only a partial short form and returned domain-mismatched candidates (a depression-incidence forecasting study and a computer-vision pedestrian-occupancy paper), so the citation was provisionally dropped. A subsequent web check (June 2026) confirmed the intended paper is real: Yin, Yamaguchi, Zajch, Uchida and Shimoda (2024), *ASim 2024* (5th Asia Conference of IBPSA), Osaka — long-term time-use change carried into a bottom-up residential energy model. It is restored as the closest behavioural-forecasting competitor (§1.2, Table 1) with the corrected ASim-2024 Osaka venue/year (the earlier "2025/Brisbane" form was wrong). Jalilian and Kamel (2025) is retained as the purely stock-scale future-year forecaster, and Motuzienė et al. (2022) as the "forecasting through the break is an open problem" citation (§1.3).
