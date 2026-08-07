# Front Matter — Abstract, Keywords, Highlights

**Manuscript:** From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)
**Authors:** O. Iseri and C. Hachem-Vermette · Concordia University

---

## Abstract

Stock-scale building energy models still run on static, pre-COVID occupancy schedules, yet the pandemic changed *when* residential energy is used, not only *how much*. This study forecasts the Canadian residential load shape from 2005 to 2030 from a calibrated behavioural occupancy time-series carried through the COVID/work-from-home structural break. Four General Social Survey time-use cycles (64,061 diaries) are harmonized, augmented with a gate-selected hybrid conditional Transformer, linked to the 2021 Census stock (144,507 households), and forecast by progressive fine-tuning under a True-Future-Test protocol. A campaign of 6,000 paired EnergyPlus runs — fixed 50-household panels held constant within each of two cycle-year spans (2005-2015; 2022-2030), with archetypes and weather frozen throughout — isolates the pure occupancy effect, while activity-resolved end uses are anchored to the national household-energy survey (48 of 48 cell-years within ±2.7%). Weekday at-home occupancy breaks +5.2 pp at COVID and persists to 2030 (+2.2 to +3.9 pp), yet annual electricity follows by only +1.4 to +2.6% across the break and a further +0.6 to +1.2% to 2030. The load shape, however, changes structurally — midday fill and flattening (Δmidday share +0.37 pp; Δload factor +0.012; both confidence intervals exclude zero) with the evening peak fixed at ~17:30, and activity resolution restructures the intraday equipment profile without displacing that peak (building-level shift 0 ± 1 h). Time-varying, survey-grounded schedules are therefore feasible at stock scale and materially change the ramping- and demand-response-relevant load metrics that static schedules cannot see.


---

## Keywords

Occupancy Modelling; Building Performance Simulation; Time-Use Survey; Load Shape; Longitudinal Forecasting; COVID-19 / Work-From-Home

---

## Highlights

- Gate-selected Transformer augments 64,061 GSS diaries to ~192k calibrated days.
- 2030 occupancy forecast through the COVID/WFH break, validated by True-Future-Test.
- 6,000 paired EnergyPlus runs isolate the pure occupancy effect at stock scale.
- WFH fills the midday valley and flattens load; the evening peak near 17:30 holds.
- Activity-resolved end uses match SHEU within ±2.7% in all 48 dwelling-by-year cells.

---

## Author Information

**Orcun Koral Iseri**¹,\* · **Caroline Hachem-Vermette**¹

¹ Concordia University, Montréal, Québec, Canada — *(department/institute to confirm — e.g., Gina Cody School of Engineering and Computer Science / Next-Generation Cities Institute)*

\* *Corresponding author:* orcunkoral.oseri@concordia.ca

*ORCID:* Iseri — [confirm]; Hachem-Vermette — [confirm]

---

## Declarations

**Funding.** This postdoctoral research was financially supported by the Natural Sciences and Engineering Research Council of Canada (NSERC) and the Voltage-Age Seed fund.

**Acknowledgements.** The authors gratefully acknowledge the financial support provided for this postdoctoral research by NSERC and the Voltage-Age Seed fund.

**Data availability.** The General Social Survey Time-Use and Census Public-Use Microdata Files analysed in this study are publicly available from Statistics Canada under the catalogue numbers listed in §2 (GSS Time Use, Cat. 45-25-0001; 2021 Census PUMF, Cat. 98M0001X). The derived behavioural-occupancy schedules, the calibrated BEM schedule files, and the analysis code are available from the corresponding author on reasonable request.

**Declaration of competing interest.** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

**CRediT authorship contribution statement.** **Orcun Koral Iseri:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Writing – original draft. **Caroline Hachem-Vermette:** Conceptualization, Supervision, Funding acquisition, Resources, Writing – review & editing.

---

# 1 Introduction

This introduction proceeds as a funnel: from the building-performance gap and the static schedules that sustain it (§1.1), through the two largely disconnected modelling traditions that frame the problem (§1.2), to the non-stationarity of occupant behaviour that neither tradition is positioned to forecast (§1.3); it then states the authors' prior line as the explicit departure point (§1.4) and closes with the contributions and aim of the present study (§1.5).

---

### 1.1 The Performance Gap and Static Occupancy Schedules

The persistent discrepancy between predicted and measured building energy use — the "performance gap" — remains one of the central credibility problems of building performance simulation (de Wilde, 2014), and occupant behaviour is now widely identified as its dominant unexplained driver (Yan et al., 2015; Hong et al., 2017). The international research agenda has recognized this explicitly through IEA EBC Annex 66 and its successor Annex 79 on occupant-centric building design and operation (Yan et al., 2017; O'Brien et al., 2020). Yet routine practice still leans on static, deterministic occupancy and diversity schedules drawn from ASHRAE and national reference standards, an assumption that is especially ill-suited to residential buildings, where daily life is governed by stochastic individual routines rather than regulated operation (Mahdavi et al., 2021). Deterministic models that rely on these fixed schedules systematically fail to capture behavioural stochasticity (Wilke, Haldi and Robinson, 2011; Elsayed et al., 2023), and survey-derived residential occupancy profiles have been shown to differ from standard reference schedules by up to 41% at individual hours — a discrepancy in *when* occupants are home, not in annual energy magnitude (Mitra et al., 2020). The emphasis of the present work is that static schedules are blind not only to a *magnitude* error in annual energy but to a *timing* error in the diurnal load shape — the quantity that matters most for grids, ramping, and demand response, and the one a single annual-energy comparison can never reveal.

---

### 1.2 Two Tracks That Rarely Meet: High-Fidelity Occupant Models versus Stock-Scale Engines

Two research traditions address occupancy in building energy modelling, and they rarely meet. The first develops high-fidelity stochastic occupant models — Markov-chain, survival-model, and time-use-survey-based generators of presence and activity — but applies them predominantly at the single-building scale and retrospectively (Richardson, Thomson and Infield, 2008; Widén and Wäckelgård, 2010; Wilke et al., 2013; Aerts et al., 2014), including a growing Canadian strand (Armstrong et al., 2009; Osman and Ouf, 2021; Ferreira et al., 2024). The second runs stock- and urban-scale energy engines across thousands of dwellings but feeds them simplified, baseline-year schedules (Reinhart and Cerezo Davila, 2016), with the paired stock-scale simulation design of Chen et al. (2022) the closest methodological precedent to the present work. Table 1 makes this disconnection explicit as a six-dimension gap matrix. The open cell that none occupies is a calibrated behavioural occupancy series forecast to 2030 *through* the work-from-home (WFH) break and carried into stock-scale paired building-energy simulation of the resulting load shape.

**Table 1.** — Six-dimension capability matrix scoring external competitors on time-series occupancy, calibrated behavioural model, forecast to a future year, activity- and end-use resolution, stock-scale simulation, and load-shape/peak focus; the all-✓ "This study" row identifies the open cell that the paper fills.

| Study | Time-series occupancy | Calibrated behavioural model | Forecast to future year | Activity & end-use resolved | Stock-scale | Load-shape & peak focus |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Chiou et al. (2011) | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Widén & Wäckelgård (2010) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Reinhart & Cerezo Davila (2016) | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Fischer et al. (2020) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Motuzienė et al. (2022) | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Chen et al. (2022, ResStock) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Osman et al. (2023, Canada) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Yin et al. (2024) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Jalilian & Kamel (2025) | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| **This study** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** |

> *Note.* The matrix scores **external** competitors only. The authors' own prior C-VAE work (Iseri and Hachem-Vermette, under review; Iseri and Hachem-Vermette, 2026) would satisfy most of these columns; its delta against the present paper is not a matter of these six binary axes but of the four pipeline-stage advances set out in §1.4 and §1.5.

**Reading of the matrix:** **Chen et al. (2022)** is the strongest competitor — stock-scale, calibrated, activity-resolved, and load-shape-focused — but retrospective: it does not forecast to a future year. **Yin et al. (2024)** tracks the very premise this paper builds on — long-term (2001–2021) change in time-use behaviour — but stops at statistical analysis: it neither forecasts forward nor runs building-energy simulation, and explicitly names stock-scale energy projection as *future work*. **Jalilian and Kamel (2025)** forecasts at stock scale to a future year yet holds occupancy static at pre-pandemic schedules. The open cell that none occupies — and that this study fills — is the simultaneous combination of a *calibrated behavioural occupancy forecast carried through the COVID/WFH structural break* with *stock-scale paired BEM simulation of the resulting load shape*.


---

### 1.3 Behaviour Is Non-Stationary, and the Field Forecasts off the Wrong Baseline

The premise that occupant behaviour is stationary failed at the COVID-19 pandemic, and the failure is structural rather than transient. Work-from-home has settled at roughly four times its pre-pandemic prevalence — about 20% of full workdays after the pandemic against 5% before (Barrero, Bloom and Davis, 2021) — and shows every sign of persisting at a new hybrid-work equilibrium (Guo et al., 2026). Weekday residential electricity profiles have correspondingly lost their bimodal commuting peaks and taken on a weekend-like shape (Abdeen et al., 2021), accompanied by a weather-adjusted increase on the order of +7.9% in residential electricity use through the pandemic (Cicala, 2023). Forecasting occupancy *through* this break, rather than extrapolating from a pre-pandemic baseline, has been flagged as an open problem in its own right: occupancy-prediction models trained on pre-pandemic data degrade sharply once the break is crossed (Motuzienė et al., 2022). The consequence for energy modelling is direct: any projection of residential demand to 2030 that is anchored to a pre-COVID occupancy baseline inherits the structural break as a systematic bias, mis-estimating not only how much energy is used but when.

---

### 1.4 The Authors' Prior Line: The Departure Point

The present study departs from a specific prior line of work by the authors. A conditional variational-autoencoder (C-VAE) pipeline, paired with a cluster-based vector-momentum scheme, was developed to synthesize longitudinally consistent Canadian residential occupancy schedules from successive General Social Survey (GSS) time-use cycles and to carry them into building energy simulation: a journal treatment across six Montréal neighbourhood-unit typologies in climate Zone 6A over 2005–2025 (Iseri and Hachem-Vermette, under review), a companion conference study across three climate-zone cities (Iseri and Hachem-Vermette, 2026), and a related population-statistics-and-machine-learning occupancy framework (Iseri, Dino and Kalkan, 2026). That line established what this paper does not re-claim: that survey-grounded, time-series occupancy can be generated for Canadian building energy models and that it moves annual demand relative to default assumptions — increasing predicted heating demand by roughly +4 to +13% and reducing cooling demand by roughly −10 to −27% — together with a first look at the diurnal and peak consequences. The contribution of the present paper is to advance that line on four specific axes, set out in §1.5, while treating its core premise — time-series GSS occupancy in Canadian BEM — as established rather than novel.

**Originality with respect to the prior journal paper.** The two studies put different questions to the same survey base. The predecessor asked *how much*: it contrasted five period-specific occupancy datasets (2005, 2010, 2015, 2022, and a synthetic 2025) against a single standardized default schedule across six Montréal neighbourhood-unit typologies in one climate zone, and delivered annual magnitude corrections, residential code calibration factors, and a first default-referenced reading of peak cooling timing. The present paper asks *when*: the default-versus-cycle magnitude contrast is replaced by a cycle-versus-cycle, within-household paired contrast; the occupancy series is carried *through* the COVID/work-from-home structural break to 2030 rather than stopping at a synthetic present-day cycle; the domain widens from six Montréal neighbourhood units to four Canadian code archetypes across six ASHRAE climate zones; the end uses are anchored to a national household-energy survey instead of being filtered from default profiles; and the primary result is the diurnal load shape — midday share, load factor, and peak hour — rather than annual totals. What this paper carries over, and deliberately does not re-claim as novel, is the premise that survey-grounded time-series occupancy can be built for Canadian building energy models at all; what is new is every stage of the pipeline that turns that premise into a forecast load shape.

---

### 1.5 Contributions and Aim of the Study

This paper makes four advances over the authors' prior line, one per pipeline stage.

1. **Generator.** The C-VAE is replaced by a gate-selected hybrid autoregressive/non-autoregressive conditional Transformer with post-hoc marginal calibration ("calibrated J3") — the only model to clear all four distributional gates in a search of more than 40 trials that included masked discrete diffusion (MDLM/SEDD) — preserving the sharp activity peaks that a variational autoencoder tends to smooth.
2. **Loads.** Presence-filtered default end uses are replaced by a SHEU-calibrated, activity-resolved bottom-up end-use model (presence, co-presence, and equipment), matching the national survey benchmark within ±2.7% in all 48 dwelling-by-year cells (maximum +2.33% equipment, +2.63% lighting).
3. **Horizon and validation.** A 2025 hindcast is replaced by a 2030 forecast carried *through* the structural break and validated under a True-Future-Test protocol that evaluates each cycle against the next unseen one.
4. **Attribution.** Sum-of-squared-error-matched per-scenario ensembles are replaced by a paired within-household Monte-Carlo design — 50 households held fixed within each of two cycle-year panels (2005-2015; 2022-2030) — yielding 6,000 EnergyPlus runs whose within-panel household differencing isolates the behavioural signal.

The aim of the study follows directly. *This paper asks whether, and when, forecast behavioural change reshapes the residential load curve at stock scale.* The full pipeline that operationalizes this question is summarized in Figure 1, with each stage detailed in the sections that follow: the datasets (§2), the methods spanning harmonization through activity-resolved loads (§3), the paired experimental design (§4), the results from behavioural driver to end-use timing (§5), and the discussion, limitations, and conclusion (§6–§8).

Although the instantiation reported here is Canadian, none of the four advances is specific to Canada. The pipeline requires three inputs that exist in many countries: a repeated national time-use survey whose activity coding can be harmonized across cycles, a census or equivalent household microdata frame through which diaries can be linked to a dwelling stock, and a national end-use benchmark against which the resulting loads can be calibrated — a trio supplied elsewhere by instruments such as the American Time Use Survey, already shown to support residential energy modelling in the United States (Chiou et al., 2011), and the Harmonised European Time Use Survey (Eurostat, 2018), to whose guidelines the activity vocabulary used here is already aligned (§3.1). What is country-specific is the calibration data, and therefore the magnitudes; the generator, the True-Future-Test protocol, and the paired frozen-frame attribution design carry over unchanged. The study is accordingly presented as a transferable method for forecasting stock-scale load shape from behavioural microdata, of which the Canadian result is the first full demonstration.

**Figure 1.** — **End-to-end occupancy-to-energy pipeline (Steps 1–9).** Block schematic from the four GSS Time-Use cycles and the Census PUMF through harmonization and 30-minute diary construction, generative day-type augmentation, Census linkage, longitudinal forecasting to 2030, BEM schedule conversion, paired Monte-Carlo simulation, and activity-resolved end-use loads; each block labelled with its section number and the key validation gate it passes.

![Figure 1](figures/Figure_01_pipeline.png)


---

# 2 Datasets

The dataset inventory is summarized in Table 2; the preprocessing path from raw microdata to analysis-ready diaries is shown in Figure 2.

---

### 2.1 General Social Survey Time-Use Microdata (2005–2022)

The behavioural backbone of the analysis is four cross-sectional waves of the Statistics Canada General Social Survey (GSS) Time-Use program: Cycle 19 (2005), Cycle 24 (2010), Cycle 29 (2015), and the GSS Time Use 2022 cycle (GSSP) (Statistics Canada, 2022). Each respondent contributes a full 24-hour episode diary recording primary activity, co-presence, and location at fine temporal resolution. Time-use surveys are an established basis for deriving occupant presence and activity schedules in building performance simulation (Osman and Ouf, 2021; Wilke et al., 2011). After applying a 1,440-minute diary-closure filter — retaining only records whose episode durations sum to exactly one day — the analysis corpus comprises 64,061 valid respondent-diaries: 19,221 (2005), 15,114 (2010), 17,390 (2015), and 12,336 (2022). The closure-filter exclusion rate is negligible in all cycles (1.92%, 1.79%, 0.00%, and 0.00% respectively), indicating near-complete diary recording (Table 2). Population-weighted at-home fractions computed from the diary data are 62.7% (2005), 62.3% (2010), 64.5% (2015), and 70.6% (2022). The +6.1 pp jump at 2022 relative to 2015 is the COVID-19 and work-from-home behavioural signature; it is the primary non-stationarity the paper traces into residential load shape (§5.1).

Two cross-cycle design constraints shape the harmonization and modelling strategy. First, SURVMNTH (survey month) is absent for the 2005 and 2010 cycles; the temporal denominator therefore collapses to three day-type strata — Weekday, Saturday, Sunday — applied uniformly across all four cycles (§3.1). Second, TUI_10 (subjective episode-level well-being) was not collected in 2005 or 2010 and is available only for 2015 and 2022; it is used as an auxiliary signal for those two cycles only and is excluded from cross-cycle model inputs. Collection mode evolved across the series: the 2005 and 2010 cycles were conducted entirely by Computer-Assisted Telephone Interviewing (CATI) on a random-digit-dial frame, whereas the 2015 and 2022 cycles used a multi-mode design that added a self-administered electronic questionnaire (EQ, administered online) alongside CATI, with electronic self-administration becoming the predominant channel by the 2022 GSSP redesign. This progressive shift toward self-administration constitutes a potential measurement break that is absorbed by the harmonization protocol and addressed explicitly via a per-cycle COLLECT_MODE conditioning feature in the generative model (§3.2) — a binary indicator that marks the predominant-mode transition at 2022; its residual risk is examined in the Limitations section (§7). Each respondent contributes exactly one observed day-type, with the other two synthesized by the generative model (§3.2) — this is the methodological justification for the generative augmentation step. Raw activity codes and co-presence columns are harmonized to a common 14-category scheme and nine unified channels as described in §3.1.

**Table 2.** — Per-cycle valid-diary counts, DIARY_VALID closure-filter exclusion rate, population-weighted at-home fraction, collection mode (CATI-only for 2005/2010 vs multi-mode CATI + electronic questionnaire for 2015/2022), and TUI_10 availability across the four GSS Time-Use cycles, with column totals.

| Cycle year | n valid diaries | DIARY_VALID exclusion % | Weighted AT_HOME % | Collection mode | TUI_10 available |
|---|---|---|---|---|---|
| 2005 | 19,221 | 1.92 | 62.7 | CATI | No (0) |
| 2010 | 15,114 | 1.79 | 62.3 | CATI | No (0) |
| 2015 | 17,390 | 0.00 | 64.5 | Multi-mode (CATI + EQ) | Yes (1) |
| 2022 | 12,336 | 0.00 | 70.6 | Multi-mode (CATI + EQ; EQ predominant) | Yes (1) |
| **Total** | **64,061** | — | — | — | — |

**Notes:** CATI = computer-assisted telephone interviewing; EQ = self-administered electronic questionnaire. Exclusion % refers to the 1,440-minute diary-closure filter; at-home fractions are population-weighted, observed diaries only (§2.1).

**Figure 2.** — **Dataset preprocessing and harmonization flow.** Raw GSS Main and Episode files across the four cycles pass through the 1,440-minute closure filter and cross-cycle schema harmonization to the common 14-category activity scheme, episode-to-HETUS 144×10-min tiling, and presence-priority majority-vote downsampling to the analysis-ready 48×30-min diary, with the mandatory 04:00→00:00 clock convention; the Census PUMF enters separately at the Census–GSS linkage (§3.3) and bypasses diary preprocessing.

![Figure 2](figures/Figure_02_dataprep.png)


---

### 2.2 Census Public-Use Microdata for Dwelling-Stock Linkage

The Statistics Canada Census Public-Use Microdata File (PUMF), 2021 edition — supplemented by the 2006, 2011, and 2016 cycles for contextual continuity — provides the dwelling-stock variables required to situate diary respondents within a representative building population (Statistics Canada, 2021; 2012). The relevant variables include period of construction, dwelling type, number of bedrooms and rooms, condominium status, repair status, and assessed value. These attributes are not available in the GSS time-use files and cannot be inferred from diary data alone. The Census PUMF enters the pipeline exclusively at the probabilistic Census–GSS linkage (§3.3), which maps 286,537 individuals onto the building stock and, after a plausibility-exclusion gate, yields the final 144,507-household building energy model (BEM) frame used for the 2005, 2010, and 2015 simulation cycles. A subsequent region-tier relink (2026-07-09) refined this frame specifically for the 2022 and 2030 cycles to 144,465 households (a ~0.03% ID churn); the consequence of this refinement for the paired sampling design is detailed in §4.3. The Census PUMF bypasses diary preprocessing entirely (Figure 2) and does not contribute to the activity harmonization or generative modelling stages.

---

### 2.3 NRCan SHEU End-Use Calibration Reference

The NRCan Survey of Household Energy Use (SHEU 2019) serves as the external end-use calibration anchor for the activity-resolved load model (§3.6 and §5.4) (Natural Resources Canada, 2019). SHEU provides independently measured annual electricity consumption disaggregated by end-use category and dwelling type, making it the appropriate benchmark against which the simulated equipment and lighting channels are validated. The per-dwelling annual equipment (plug-load) targets used in calibration are: SingleDetached 3,700 kWh, OtherDwelling (attached) 3,139 kWh, MidRise 2,166 kWh, and HighRise 1,922 kWh. The corresponding annual lighting targets are: SingleDetached 1,262 kWh, OtherDwelling 1,100 kWh, MidRise 736 kWh, and HighRise 736 kWh. These targets define the per-end-use scalars that constrain each archetype's simulated annual energy to the survey benchmark; the validation outcome is reported in §5.4.

---

### 2.4 Weather Files and Building Archetypes

The simulation domain spans six Canadian cities selected to cover the principal ASHRAE climate zones of the inhabited Canadian stock (5A through 7A): Toronto (5A), Kelowna (5B), Vancouver (5C), Montréal (6A), Calgary (6B), and Winnipeg (7A). Typical Meteorological Year (TMY) EnergyPlus weather files (EPW) are used for each city, and the building stock is represented by four Canadian code-compliant residential archetypes — SingleDetached, OtherDwelling (attached), MidRise, and HighRise — developed under NECB 2017 and NBC 9.36 Zone-6 envelope assumptions (National Research Council Canada, 2017; 2020); these are Canadian code archetypes, not US DOE prototype buildings. All simulations are executed in EnergyPlus v24.2 (U.S. Department of Energy, 2024). The full 4 × 6 archetype-by-city matrix, the weather file specifications, and the held-versus-varied factorial design are defined in the Experimental Design section (§4, Tables 3–4); this subsection inventories the inputs only.

---

# 3 Methods

Each pipeline stage is presented with its design rationale, its methodological precedent, and its validation result. The conditional generator architecture is shown in Figure 3 and the occupancy-to-simulation coupling in Figure 4; supporting workflow schematics for the model-selection search, Census–GSS linkage, longitudinal forecasting, and activity-resolved end-use layer are provided in the Appendix (Figures S1–S4).

---

### 3.1 Harmonization and 30-Minute Diary Construction

The four GSS cross-sections span two decades and were coded under distinct cycle-specific classification schemes, requiring ex-post output harmonization to a shared activity vocabulary before any cross-cycle modelling can proceed. Each wave's raw episode codes are mapped to a common 14-category occupant-activity (occACT) scheme aligned with the Eurostat (2018) HETUS guidelines, producing a unified activity alphabet without loss: the mapping covers 182, 264, 64, and 121 raw codes for the 2005, 2010, 2015, and 2022 cycles respectively, with zero coding conflicts and 0.00% unmapped episodes in every cycle (SI Table B2). This complete mapping reflects the deliberate conservatism of the harmonization design — where a raw code was ambiguous, it was assigned to the closest HETUS parent category rather than left unclassified. Co-presence is OR-merged from the ten raw episode columns into nine unified channels; the `colleagues` channel was not collected in the 2005 and 2010 cycles and is treated as structurally absent for those waves in all downstream modelling.

Each harmonized episode diary is tiled onto the standard HETUS 144×10-minute temporal grid, then downsampled to 48×30-minute slots via a presence-priority majority-vote rule. The 48-slot (30-minute) resolution represents the documented optimal accuracy-to-computation compromise for this application: relative to the full 144-slot representation, it reduces the self-attention cost of the generative model by approximately nine-fold, since attention complexity is quadratic in sequence length, while retaining sufficient temporal granularity to capture the intraday occupancy transitions that drive building thermal response. The three-way tie rate in the majority-vote downsampling procedure is 0.82%, a negligible source of ambiguity resolved in favour of the at-home state. Seasonal stratification was considered but ultimately discarded as a conditioning dimension: the cross-cycle Jensen–Shannon divergence on the harmonized diaries falls below 0.001 across all seasons, indicating a negligible seasonal signal that would not justify the additional data fragmentation. The day-type stratification is therefore DDAY_STRATA = {Weekday, Saturday, Sunday}, the three strata available uniformly across all four cycles.

The GSS diary day is anchored at 04:00 rather than 00:00, following HETUS convention (Aerts et al., 2014). A mandatory circular shift of −4 hours (04:00→00:00) is required to align the diary time-slots with the EnergyPlus simulation clock before schedule injection. The design and correctness of this shift — and the consequences of an earlier implementation in which it was inadvertently omitted — are discussed in §4; the shift is stated here as a method requirement of the diary-construction stage. The full harmonization and tiling flow is illustrated in Figure 2 (§2).

---

### 3.2 Day-Type Augmentation with a Gate-Selected Generative Model

Each GSS respondent contributes exactly one observed day-type diary; the other two day-types must be synthesized to equip every respondent with a complete Weekday/Saturday/Sunday profile set prior to Census linkage. This augmentation problem is framed as conditional sequence generation: given a respondent's demographic conditioning vector, the generator must produce plausible 48-slot, 14-category activity sequences for the unobserved day-types, along with the corresponding AT_HOME and co-presence binary channels.

Model selection was conducted as a gated search across a broad generative family, summarized in Figure S1. Over 40 trials were evaluated under a progressive 2%→20%→100% data funnel, spanning Markov chains, autoregressive sequence models, variational autoencoders, GAN-adjacent frameworks, cross-attention architectures, and masked discrete-diffusion models including MDLM (Sahoo et al., 2024) and SEDD (Lou et al., 2024) — the latter tracing a lineage to the structured discrete denoising diffusion framework of Austin et al. (2021). Candidate models were retained only if they cleared four hard distributional gates simultaneously: activity Jensen–Shannon divergence ≤ 0.05; AT_HOME root-mean-square error ≤ 5.3 percentage points; per-channel co-presence maximum gap ≤ 5.0 pp; and a composite score below 1.045. The stringency of the four-gate requirement proved consequential: the MDLM variant produced the best composite score in the entire search (0.559) yet failed two of the four gates, with its AT_HOME RMS reaching 7.81 pp — more than two percentage points above the 5.3 pp threshold. The best-performing cross-attention autoregressive decoders failed more dramatically still, collapsing at inference to co-presence gaps of 19–23 pp despite achieving the lowest training losses in their family, demonstrating that training loss is an unreliable proxy for inference-time distributional fidelity. These negative findings are reported honestly because they constrain the design space for future work in this domain.

The sole model to clear all four gates across the full search is the calibrated J3 architecture. J3 comprises a shared 6-layer Transformer encoder operating over the 48-slot multivariate diary token stream; a 6-layer autoregressive (AR) activity decoder producing the categorical sequence slot by slot; and a set of parallel non-autoregressive (NAT) binary heads predicting AT_HOME and the nine co-presence channels, positioned behind a gradient-detach barrier that isolates the binary-head loss gradients from the AR trunk. The model has d_model = 384 and approximately 29.25 million parameters. Conditioning is supplied through a 90-dimensional vector (d_cond = 90) injected at both the encoder and decoder, encoding respondent demographics (age group, sex, marital status, household size, province, and labour-force and work-hours variables), cycle-year, survey collection mode (COLLECT_MODE), and the behavioural drivers ATTSCH (school attendance), POWST (place of work and work-from-home status), and MODE (commute mode). The gradient-detach topology is the architectural feature that distinguishes J3 from the competing cross-attention variants: it prevents the binary-head signal from destabilizing the autoregressive trunk during training, and topology diagnosis identified it — together with the autoregressive activity decoder and the non-autoregressive co-presence heads — as load-bearing for J3's inference-time gate performance. The full J3 architecture is illustrated in Figure 3 and summarized in SI Table B1.

J3's gate scores are: activity JS 0.0191; AT_HOME RMS 4.57 pp; co-presence maximum gap approximately 2.03 pp; and composite score 0.6355. A post-hoc per-(cycle × stratum × slot) marginal raking step — the post-hoc calibration stage — snaps the AT_HOME marginals to their observed or projected targets after generation. The coherence cost of raking is modest: approximately 1.8–2.1% of slot-records become activity/at-home incoherent following the marginal adjustment. This is operationally harmless for the building energy model, which keys exclusively off the AT_HOME channel rather than the activity label; the activity labels are consumed by the end-use layer (§3.6) at a stage where the at-home channel is already fixed. The augmented output is approximately 192,183 diary-days, representing the full respondent pool equipped with a complete three-day-type profile.

**Figure 3.** — **Conditional generator (calibrated J3) architecture.** Shared multi-head Transformer encoder over the 48-slot multivariate diary token stream, an autoregressive activity decoder, and parallel non-autoregressive binary heads for AT\_HOME and the nine co-presence channels behind a gradient-detach barrier; the conditioning vector (demographics, cycle-year, COLLECT\_MODE, ATTSCH/POWST/MODE) injected at both encoder and decoder, and the post-hoc per-(cycle×stratum×slot) marginal raking shown as the terminal calibration block.

![Figure 3](figures/Figure_03_J3_architecture.png)


---

### 3.3 Probabilistic Census–GSS Linkage

The augmented diary pool must be attached to a representative dwelling stock before simulation. Each of the 286,537 individual agents in the Census 2021 Public-Use Microdata File is matched to one augmented diary row via a slot-native, four-tier hierarchical demographic fallback match — a probabilistic statistical linkage in the hot-deck tradition (Rässler, 2002; D'Orazio et al., 2006; Beckman et al., 1996; Putra et al., 2021). This method replaces the episode-based profile-matcher of earlier pipeline iterations with a slot-native match that is directly compatible with the augmented 48-slot representation. The procedure is illustrated schematically in Figure S2.

The four tiers descend in demographic specificity. Tier 1 ("Perfect") requires exact agreement on all seven demographic match keys — age group, sex, marital status, household size, labour-force status, province, and census-metropolitan-area or urban-rural class — plus the day-type stratum; each Census agent is first sought in this maximally specific pool. If no eligible donor exists at Tier 1, the agent falls through to Tier 2 ("Core"), which retains age group, sex, labour-force status, and province plus stratum. If Tier 2 yields no donor, the agent proceeds to Tier 3 ("Constraints"), which matches on age group, sex, and stratum only. A final Tier 4 ("FailSafe"), matching on stratum alone, exists as a logical backstop but was never invoked: the match-tier distribution over the 286,537 agents is 44.94% at Tier 1, 21.39% at Tier 2, 33.67% at Tier 3, and 0.00% at the FailSafe tier. The complete absence of FailSafe placements confirms that the augmented diary pool is sufficiently dense across all demographic combinations that every Census agent finds a stratum-coherent behavioural donor within Tier 3 or above.

Dwelling-stock variables — dwelling type, period of construction, number of bedrooms and rooms, condominium status, repair status, and assessed value — are carried directly from the matched Census record onto each agent. Households are then formed by aggregating agents sharing a dwelling unit and taking the per-slot maximum AT_HOME indicator across household members, so that a slot is classified as occupied if any member is present. A per-household plausibility gate removes physically implausible cases — specifically the small residue of single-occupant synthetic-only weekday agents whose mean at-home fraction falls below 0.30 — yielding the final 144,507-household building-energy-model frame used for the 2005, 2010, and 2015 simulation cycles (a subsequent 2026-07-09 relink refines this to 144,465 households for 2022 and 2030 only; §4.3).

The conditional-independence assumption (CIA) implicit in treating diary selection as independent of unobserved dwelling characteristics given the observed match keys is an acknowledged limitation of the hot-deck approach; its plausibility is examined in the context of the study's scope in §7.

---

### 3.4 Longitudinal Forecasting to 2030

The four GSS cycles span 2005 to 2022, a period encompassing substantial behavioural change including the COVID-19-era work-from-home transition. Rather than treating the cycles as independent data sources and pooling them naively, the forecasting strategy encodes their temporal ordering through progressive fine-tuning with weight inheritance: the model is first trained on 2005 data, and each successive phase loads the previous cycle's checkpoint as its initialization rather than reinitializing from scratch. This chain — 2005 → +2010 → +2015 → +2022 — treats later cycles as behavioural refinements of earlier ones, preserving distributional memory while allowing the model to shift towards more recent patterns. The procedure is illustrated in Figure S3.

At every cycle transition, a DRIFT_MATRIX is computed by applying the current checkpoint to the next cycle's held-out set and measuring Jensen–Shannon divergence per activity-category and day-type stratum before any fine-tuning on that cycle's data. This makes concept drift explicit and auditable at each step, distinguishing the real concept drift in the conditional distribution P(activity | demographics, year) from the virtual drift in the covariate distribution P(demographics) — a distinction formalized in the concept-drift adaptation literature (Gama et al., 2014). The fine-tuning phase then addresses the real drift; demographic virtual drift is addressed separately at inference through scenario injection (below). Recency-weighted pooling assigns sample weights of 0.10, 0.20, 0.30, and 0.40 to the 2005, 2010, 2015, and 2022 cycles respectively in the joint training stage, up-weighting the most recent, post-COVID behavioural signal.

The 2030 cohort is produced by demographic scenario injection: the age-group distribution (and the labour-force composition that follows from it) is resampled to the Statistics Canada M1 medium-growth population projection (Statistics Canada, 2026), producing a 37,008-row synthetic 2030 diary cohort. This captures the demographic virtual drift in P(demographics) between 2022 and 2030 without modifying the conditional behavioural model — the two drift channels are handled independently, as the conceptual framework requires.

Validation is conducted as a True-Future-Test in which each fine-tuning phase is scored on the next, withheld cycle. The final True-Future-Test phase — the model fine-tuned through 2015 and evaluated on the entirely unseen 2022 cycle — achieves a weekday JS divergence of 0.0619, a clear PASS against the < 0.20 True-Future-Test gate. A separate 2022 backcast reconstruction, in which the fully trained model is applied to observed 2022 conditioning features, achieves a weekday JS divergence of 0.0630, a clear PASS against the tighter < 0.10 reconstruction gate. The weekend JS sits near 0.16–0.18, a data-intrinsic ceiling rather than a model failure: weekend diaries are fewer in each cycle and more behaviourally variable, and because the combined evaluation set mixes observed and synthetic rows, the synthetic rows alone sit 0.14–0.18 from the observed distribution, placing a mathematical floor on the achievable combined-set JS. The observed-only rows themselves score 0.036–0.046, confirming that the model's weekend representation is acceptable when evaluated on the comparable basis. The full forecasting-stage validation scorecard is 35/35 PASS. Inference operates in two phases: a 2022 backcast used for validation and the 2030 forward forecast as the operational deliverable. The 2030 forecast preserves the COVID-era work-from-home break — a +6.6 pp raw (+5.2 pp demographically standardized) weekday at-home displacement at the 2015→2022 transition — carrying it forward at +2.2 to +3.9 pp above the pre-pandemic baseline as a single high-persistence scenario; the sensitivity of this assumption is bounded in §7.

---

### 3.5 Conversion to Building Energy Model Schedules

Each household's predicted diary is materialized as a per-household EnergyPlus `Schedule:Compact` object. The diary basis is 48 half-hour slots; paired slots are averaged to 24 hourly values at the IDF interface. Each schedule carries a two-day-type profile — a Weekday profile and a pooled Weekend profile in which Saturday and Sunday diaries are combined — matching the temporal structure used throughout the simulation campaign (§4). Four parallel schedule channels are derived per household: occupancy (AT_HOME fraction) and metabolic heat gain together load the EnergyPlus `People` object, while the equipment and lighting channels, added by the activity-resolved end-use model described in §3.6, load the `ElectricEquipment` and `Lights` objects respectively. The occupancy channel is the per-slot mean AT_HOME indicator across household members — the fraction of the household present in each slot — and is computed independently of the per-slot maximum used for household formation in §3.3, which serves only to define dwelling-level occupancy for the plausibility gate and does not propagate to the injected schedule. All four channels are injected into EnergyPlus together (§4).

The metabolic channel maps each of the 14 activity categories to a per-person internal-gain wattage using metabolic-equivalent (MET) values drawn from the 2024 Adult Compendium of Physical Activities (Herrmann et al., 2024), scaled at 70 W/MET and referenced to an approximate 60 kg adult. This basis is deliberately conservative relative to the ASHRAE 55 / ISO 7730 convention of approximately 105 W/MET for a standard adult (ASHRAE, 2023; ISO, 2005): the lower per-MET wattage follows from referencing a 60 kg rather than a ~70 kg standard body (which would imply ~83 W/MET), and consequently yields slightly lower internal-gain estimates than the comfort-standard default. The conservatism is appropriate here because the primary inferential target is the relative change in load shape across years rather than the absolute internal-gain magnitude.

For households whose record spans only one observed day-type — the modal case in the GSS, where each respondent contributes a single diary — the missing day-type is completed by a donor-draw procedure: a genuine diary of the needed type is drawn from the in-frame pool, matched per household member, preserving the calibrated weekend marginal. An earlier copy-day completion, which replicated the observed weekday diary onto the weekend slot, had diluted the weekend marginal by −2.76 percentage points; the donor-draw approach eliminates this artefact and was adopted as the standard completion method for the final BEM schedule files.

A per-cycle raking step is applied uniformly across all five cycle-year schedule files (2005, 2010, 2015, 2022, and 2030), standardizing the diary basis so that the longitudinal series is produced by one uniform procedure; the resulting standardized at-home series is reported in §5.1. The mandatory 04:00→00:00 circular clock-alignment shift is applied to all four channels at this stage; the discovery of an earlier injection-time phase error and the full re-simulation campaign that corrected it are narrated in §4.

**Figure 4.** — **Occupancy-to-EnergyPlus schedule integration.** The per-household predicted occupancy time-series passes through the 04:00→00:00 clock-alignment rotation and the activity-to-metabolic mapping, fans into four schedule channels (occupancy, metabolic, equipment, lighting), and converges into the per-household `Schedule:Compact` IDF block injected into EnergyPlus v24.2.

![Figure 4](figures/Figure_04_schedule_integration.png)


---

### 3.6 Activity-Resolved End-Use Loads

The equipment and lighting schedule channels are populated by an activity-resolved end-use layer that translates the modelled occupant activity sequence into plug-load and lighting demand at each half-hour slot. The layer is positioned as a precedented adaptation of bottom-up activity-driven domestic load modelling (Richardson et al., 2010; Yamaguchi and Shimoda, 2017), driven by the externally predicted activity sequence from the calibrated J3 generator rather than a standalone stochastic activity process — it is not itself a novel load-modelling contribution but an application of established methods to the pipeline's output representation. The full crosswalk and calibration parameters are documented in SI Tables A1–A3, with the overall layer architecture illustrated in Figure S4.

The end-use structure is two-tiered. A flat 24/7 baseload representing continuously operating appliances — refrigerator (~448 kWh/yr), freezer (~343 kWh/yr), and standby and miscellaneous background draw (~400–430 kWh/yr) — is held fixed throughout the simulation and is not modulated by occupancy or activity. A transient activity tier overlays this baseload by mapping modelled occupant activity to per-slot plug-load and lighting demand via a 9-end-use × 14-activity crosswalk. Co-presence modulates device demand through a sub-linear shared-device scaling function: the effective occupancy multiplier EFF(N) takes values of 1.0, 1.4, 1.7, 1.9, and 2.0 for one through five-or-more co-present occupants respectively for shared devices, while personal devices scale linearly with occupant count. Lighting is modelled as a binary occupied-and-awake indicator multiplied by the dwelling's SHEU lighting scale factor, without a daylight-availability gate; this simplification is documented as deviation R1 (SI Appendix D) and its effect on the results is discussed in §7.

Calibration constrains each archetype's simulated annual end-use to the NRCan SHEU 2019 survey benchmark (§2.3 and §5.4). For each end-use e and dwelling archetype, a scalar f_e = SHEU_target_e / simulated_annual_e is computed and applied uniformly across all time-slots, with the baseload held fixed outside the calibration loop. This per-end-use calibration ensures that the layer reproduces the correct annual energy totals by end-use category while allowing the intraday and inter-year variation to be driven entirely by the activity-sequence input. The layer was executed across 4,800 paired baseline-versus-activity EnergyPlus runs, of which 4,795 carried complete meter output; the end-use-layer validation scorecard is 6 PASS / 1 WARN / 3 INFO / 0 FAIL, with no failures. The single WARN and the three INFO items do not affect the load-shape metrics that constitute the paper's primary inferential targets.

---

# 4 Experimental Design

The simulation campaign is organized as a fully specified factorial experiment whose domain, schedule-integration procedure, paired Monte-Carlo structure, and output metrics are summarized in Table 3 and Table 4 below; the schedule-integration procedure itself is shown in Figure 4 (§3.5).

---

### 4.1 Building-Archetype and Climate-Zone Domain

The simulation domain spans four Canadian residential dwelling archetypes crossed with six cities representing the principal ASHRAE climate zones found in the inhabited Canadian stock. The four archetypes — SingleDetached, OtherDwelling (attached), MidRise, and HighRise — are drawn from the Canadian NECB 2017 and NBC 9.36 Zone-6 code-compliant geometry and envelope specifications (National Research Council Canada, 2017, 2020); they are not US DOE prototype buildings. Their representation in the 144,507-household analytical frame is unequal: SingleDetached accounts for 52.9% of the stock, MidRise for 21.3%, OtherDwelling for 13.0%, and HighRise for 12.8%, a distribution that reflects the urban-dominant character of the Canadian General Social Survey sample. The six cities and their ASHRAE climate-zone designations, inventoried in §2.4, are Toronto 5A (ON), Kelowna 5B (BC), Vancouver 5C (BC), Montréal 6A (QC), Calgary 6B (AB), and Winnipeg 7A (MB). Each city is assigned its own city-specific Typical Meteorological Year (TMY) EnergyPlus weather file (EPW), one per city, ensuring that the thermal boundary condition reflects the local long-run climate rather than a regional or national composite. The simulation engine throughout is EnergyPlus v24.2 (U.S. Department of Energy, 2024).

A deliberate isolation choice underlies the archetype geometry: the base building model is a single Montréal (MTL) Zone-6 envelope set held fixed across all six climate cities. Because the paired within-household design described in §4.3 differences out the envelope by construction, this fixed-envelope strategy ensures that the cross-climate and cross-year variation in the simulated outputs is attributable to the interaction of occupancy time-series with weather, not to co-varying building physics. The practical limitations introduced by this choice — most notably the single-envelope generalization across diverse thermal climates and the mapping of Atlantic-province households onto a Montréal EPW — are acknowledged in full in §7.

**Table 3.** — The 4 archetypes × 6 cities simulation domain, each city with its ASHRAE climate zone and representative TMY weather file, all built on the Canadian NECB 2017 / NBC 9.36 Zone-6 code archetype geometry and envelope; the 24 archetype-by-city cells simulated per cycle-year, with the single fixed Montréal Zone-6 envelope held across all six climates.

| City | Province | ASHRAE climate zone | TMY weather file (EPW) | Archetype standard |
|---|---|---|---|---|
| Toronto | Ontario | 5A | `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw` | NECB17/NBC936 Z6 |
| Kelowna | British Columbia | 5B | `CAN_BC_Kelowna.Intl.AP.712030_TMYx_5B.epw` | NECB17/NBC936 Z6 |
| Vancouver | British Columbia | 5C | `CAN_BC_Vancouver.Harbour.CS.712010_TMYx_5C.epw` | NECB17/NBC936 Z6 |
| Montréal | Québec | 6A | `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw` | NECB17/NBC936 Z6 |
| Calgary | Alberta | 6B | `CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw` | NECB17/NBC936 Z6 |
| Winnipeg | Manitoba | 7A | `CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw` | NECB17/NBC936 Z6 |


---

### 4.2 Occupancy-Schedule Integration into the Building Energy Model

The per-household occupancy time-series produced by the calibrated J3 generative model (§3.2) and the activity-driven end-use model (§3.6) are materialized as the per-cycle-year schedule files, covering the full analytical frame for each cycle-year: 144,507 households for 2005, 2010, and 2015, and the refined 144,465-household frame for 2022 and 2030 (§2.2, §4.3). Each household's schedule is injected into EnergyPlus as a `Schedule:Compact` object carrying a 2-day-type profile: a Weekday profile and a pooled Weekend profile (Saturday and Sunday are combined). The temporal resolution at the IDF interface is hourly, with 24 values per day-type.

Four parallel schedule channels are derived per household. The occupancy channel (AT\_HOME fraction) and the metabolic channel (activity-driven internal heat gain) load the EnergyPlus `People` object; the equipment channel (plug-loads) and the lighting channel load the `ElectricEquipment` and `Lights` objects respectively. The equipment and lighting magnitudes are SHEU-calibrated through the procedure described in §3.6. Metabolic heat gain is mapped from the 14 activity categories to per-person watts via the conservative 70 W/MET basis described in §3.5.

A clock-alignment step rotates the 04:00-origin GSS diary time-slots onto the EnergyPlus 00:00 hour-of-day convention via a circular shift. Correcting this alignment proved to be the single most consequential correctness intervention in the simulation campaign. In the original implementation, the 04:00-origin diary slots were written directly into the EnergyPlus hour field without rotation, injecting all four schedule channels four hours early relative to the EPW clock — a systematic intraday phase error discovered during campaign verification. Following restoration of the circular-shift rotation, a full re-simulation was executed to produce the corrected campaign. The error was strictly phase-related: annual energy totals were phase-invariant across the original and corrected campaigns (the maximum archetype EUI change was +2.85%, leaving the per-household SHEU calibration intact), confirming that the bug affected intraday timing only. The timing results unlocked by the corrected campaign are reported in §5.3; the transferable validation lesson the episode carries is drawn in §6, and it is noted among the limitations in §7.

Households missing an observed day-type receive the donor-draw completion described in §3.5, preserving the calibrated weekend marginal. Schedule-integration validation confirmed clean passage for both target years: 29 PASS / 0 WARN / 0 FAIL for 2022 and 28 PASS / 0 WARN / 0 FAIL for 2030 (2030 lacks one observed-future gate). Injected weekday at-home means reproduce calibration targets to within approximately 0.5 percentage points or better — for example, the 2030 weekday at-home mean of 78.48% against a target of 78.44%.

The full occupancy-to-EnergyPlus schedule-integration flow — the 04:00→00:00 clock-alignment rotation, the activity-to-metabolic mapping, the four schedule channels (occupancy, metabolic, equipment, lighting), and the per-household `Schedule:Compact` IDF block injected into EnergyPlus v24.2 — is shown in Figure 4 (§3.5).

---

### 4.3 Paired Frozen-Frame Monte-Carlo Design

The full factorial comprises 4 archetypes × 6 cities × 5 cycle-years × 50 paired households = 6,000 EnergyPlus v24.2 annual runs. The five cycle-years are 2005, 2010, 2015, the calibrated-observed year 2022, and the longitudinal forecast year 2030. Within each archetype-by-climate-region cell, N = 50 household IDs are sampled once, stratified by dwelling type (DTYPE) and province (PR), and that identical household set is carried forward across 2005, 2010, and 2015 — a frozen-frame design in which the dwelling stock for these three cycles is held at the original 144,507-household Census linkage (§2.2). A subsequent region-tier relink (2026-07-09) refined the analytical frame for the 2022 and 2030 cycles to 144,465 households; because this refinement post-dates the historical panel, a second, independently-sampled N = 50 household set — again stratified by DTYPE × PR — was drawn once per cell from the refined frame and is carried forward across 2022 and 2030 only. The design therefore comprises two fixed panels rather than one five-cycle panel: household identity is held constant within 2005-2015 and, separately, within 2022-2030, but is not carried across the two groups.

Two elements are held constant across all five cycle-years within each cell: the archetype IDF (geometry and envelope) and the city TMY weather file. Household IDs are held constant only within each panel described above, not across the 2015→2022 boundary. The single varied factor within a panel is the per-household occupancy and end-use time-series, which differs across years as the calibrated generative model (§3.2) and the activity-driven end-use model (§3.6) produce cycle-year-specific predictions for each household. This design follows the paired stock-scale simulation rationale articulated by Chen et al. (2022): because building physics, climate, and household composition are all held invariant within a panel, the within-household cross-year difference in energy output is attributable solely to the predicted change in the occupancy time-series for any comparison made within that panel. Envelope effects, climate variation, and between-household Monte-Carlo sampling variance difference out simultaneously, yielding paired deltas with substantially tighter confidence intervals than a conventional independent-sample design would achieve. The paper's primary inferential targets (§5.3) — the 2022→2030 load-shape metrics — are fully within-panel and retain the full attribution benefit and precision; the 2005-2010-2015 comparisons are likewise within-panel. Only the longitudinal trajectory's 2015→2022 step (Figure S8, §5.3, §7) crosses the panel boundary and is a cross-sectional, not within-household, comparison.

Monte-Carlo convergence at N = 50 was assessed empirically. The 95% confidence-interval half-width of the cell-mean annual energy averages 1.80% across cells, with a worst-case cell of 4.04%; the load-shape metrics are considerably more precise, consistent with their lower household-to-household variance relative to annual kWh.

**Table 4.** — The held-versus-varied paired frozen-frame design: the archetype IDF and TMY weather file held constant across all five cycle-years; household IDs held constant within each of two independent panels (2005-2015; 2022-2030) against the single varied factor (the occupancy time-series), yielding the 6,000-run factorial and the within-panel household differencing that isolates the behavioural signal.

**Section A — Factors held constant**

| Factor | Description |
|---|---|
| IDF geometry & envelope | Canadian NECB17/NBC936 Z6 archetype IDF; held fixed across all 6 cities and all 5 cycle-years |
| TMY weather file | City-specific EPW (one per city); the same file used for every cycle-year run within a city |
| Household IDs (SIM_HH_ID) | Two independent fixed panels, each held constant *within* its own cycle-years: (i) 2005/2010/2015 — N = 50 household IDs sampled once per cell from the original 144,507-household frame, stratified to DTYPE × PR; (ii) 2022/2030 — a *separate* N = 50 household IDs sampled once per cell from the refined 144,465-household frame (2026-07-09 region-tier relink; ~0.03% ID churn vs. the original linkage), also stratified to DTYPE × PR. Household identity is not carried across the two panels — see Attribution logic below. |
| n per cell | 50 households |

**Section B — Factors varied**

| Factor | Values |
|---|---|
| Occupancy time-series | One calibrated 30-min AT_HOME + metabolic + equipment + lighting schedule per household per cycle-year, drawn from the per-cycle-year schedule files |
| Cycle-years | 2005 · 2010 · 2015 · 2022 (calibrated observed) · 2030 (forecast) |

**Total = 4 archetypes × 6 cities × 5 years × 50 HH = 6,000 runs**; within-HH differencing removes between-HH MC variance *within each panel*; cross-year Δ = purely behavioural for comparisons made within a panel (2005↔2010↔2015 among themselves; 2022↔2030 between themselves).

**Attribution logic:** IDF and weather are held constant across all five cycle-years; household IDs are held constant *within* each of the two panels (2005-2015; 2022-2030) but differ *between* the panels. The within-household paired difference in energy output is attributable *solely* to the change in the predicted occupancy time-series for any comparison made within a single panel — this covers the paper's primary inferential target, the 2022→2030 comparison (§5.3-§5.4), which is fully within-panel. The 2015→2022 transition in the longitudinal trajectory (Figure S8) crosses the panel boundary — it compares two independently-drawn household samples and is a cross-sectional trend, not a matched within-household difference (§7 Limitations).

**MC convergence:** 95% CI half-width mean 1.80%, worst cell 4.04% at N = 50 (load-shape precision, not annual-kWh precision).

---

### 4.4 Simulation Outputs and Campaign Verification

Each of the 6,000 EnergyPlus runs produces an 8,760-hour annual load profile. Seven meter streams are collected: Electricity:Facility, InteriorLights, InteriorEquipment, Fan, Heating:EnergyTransfer, Cooling:EnergyTransfer, and WaterSystems:EnergyTransfer. From these hourly profiles, four categories of derived product are computed. Load-shape metrics — load factor, midday energy share, peak-to-average ratio, and coincidence factor — constitute the primary inferential targets, reported in §5.3. Peak-load and hour-of-peak statistics characterize intraday timing. The stock-weighted ensemble load shape aggregates individual household profiles to the dwelling-type and national levels. Annual energy use intensity (EUI, kWh/m²·yr) serves as a secondary plausibility anchor against NRCan SHEU benchmarks, with results presented in §5.2.

The campaign completed at 6,000 / 6,000 runs. One run — OtherDwelling × Kelowna 5B × 2010 — encountered a deterministic EnergyPlus DX-coil sizing fatal caused by a negative coil bypass factor; it was recovered by a one-field fix (Gross Rated Sensible Heat Ratio changed from autosize to 0.75), with a negligible effect on results (archetype EUI delta ≤ 0.013 kWh/m²·yr). The final verification scorecard for the corrected campaign reads 24 PASS / 0 WARN / 3 INFO / 0 FAIL. Schedule round-trip fidelity is exact across all five cycle-years. The mean peak hour falls between 17.5 and 17.7 hours across all years, consistent with the expected residential evening demand peak. The confirmed phase-invariance of annual energy across the correction (maximum archetype EUI change +2.85%) establishes that the 04:00 rotation fix altered intraday timing exclusively, and that the timing results now reported in §5.3 reflect the corrected, physically consistent simulation.

---

# 5 Results

The four subsections below trace a single chain of evidence: from the behavioural shift itself (§5.1), to its annual energy consequence and model credibility (§5.2), to its reshaping of the diurnal load curve and what that means for peak demand (§5.3), and finally to what activity-resolution adds — and does not add — over a presence-only model (§5.4).

---

### 5.1 Non-Stationarity in At-Home Occupancy

The central empirical question of this section is whether the at-home distribution shifted in a manner that could plausibly propagate into building load. The weighted fraction of households at home stood at 62.7% in 2005, was essentially unchanged at 62.3% in 2010, and rose only marginally to 64.5% by 2015, suggesting a near-stable pre-pandemic baseline. The 2022 survey cycle breaks this pattern decisively: the aggregate at-home share reaches 70.6%, a rise of +6.1 percentage points relative to the 2015 level, with the weekday component showing an even larger raw displacement of +6.6 pp. This COVID-era break — now embedded in household behaviour rather than representing a transient disruption — is the dominant signal in the data. The forecast 2030 synthetic diaries carry the break forward at +2.2 to +3.9 pp above the pre-pandemic level, consistent with a partial but sustained work-from-home adoption rather than a full reversal (Figure 5); this magnitude is provisional pending a calibration-provenance check described in §7.

The apparent pre-pandemic upward drift between 2005 and 2015 requires interpretation. An age–sex–labour-force status (AGEGRP × SEX × LFTAG) direct standardization reveals that the drift is compositional rather than behavioural: once the 2005–2015 samples are standardized to a common demographic structure, the at-home series is essentially flat (64.2 / 64.2 / 63.3% across those three cycles). The 2022 jump, by contrast, survives standardization and therefore reflects a genuine change in daily behaviour, not a shift in who responded to the survey: after the same demographic standardization, the weekday at-home break at the 2015→2022 transition settles at +5.2 pp — the headline behavioural shift carried through the remainder of the paper. Visually, the signature of this change is a filling of the midday "everyone out" trough: the most recent cycles sit consistently higher through the 10:00–15:00 window, the hours when working-age residents were historically absent (Figure 5). The 2030 projection extends this elevated midday presence, establishing the behavioural premise that all downstream energy calculations depend on.

**Figure 5.** — **Occupancy driver: diurnal at-home shift.** Average fraction of households at home across the hours of the day, weekday and weekend panels, one line per survey/forecast cycle (2005–2030), with the work-from-home midday window shaded; the behavioural starting point traced into electricity demand.

![Figure 5](figures/Figure_05_occupancy_driver.png)


---

### 5.2 Annual Energy Magnitude and Benchmark Plausibility

Given the magnitude of the behavioural shift, a key credibility question is whether the simulated annual electricity consumption is plausible relative to independent survey benchmarks. The answer on both fronts is conservative. Across the 6,000 paired EnergyPlus runs comprising the corrected Step-8 campaign (§4.4), annual electricity rises by only +1.4 to +2.6% across the COVID break, and by a further +0.6 to +1.2% from the 2022 cycle to the 2030 forecast. These modest increments reflect the thermal decoupling of internal gains from total electricity in well-insulated Canadian housing stock: occupants alter the timing and distribution of demand far more than its annual sum.

The principal calibration anchor is at the per-household end-use level: equipment and lighting energy were SHEU-calibrated (§3.6) to within ±2.7% of the survey benchmark across all 48 dwelling-by-year cells (maximum +2.33% equipment, +2.63% lighting), so the model's representation of residential electricity *magnitude* rests on the household-kWh comparison rather than on any per-area figure. As a secondary plausibility cross-check, the stock-representative annual energy use intensities for the recent observed cycle — 115 kWh/m² for single-detached, 108 kWh/m² for mid-rise, 100 kWh/m² for other dwelling, and 78 kWh/m² for high-rise (2030 forecast: 116, 108, 101, and 79 kWh/m² respectively) — are read against the NRCan Survey of Household Energy Use (SHEU-2019) regional-average intensity ranges for each archetype (SHEU Tables 3.3a/3.3b; Table 5; Figure S9, Appendix). **All four archetypes sit below their SHEU regional-average ranges**, by margins of roughly 3% (mid-rise), 12% (single-detached), 27% (other dwelling) and 31% (high-rise). The deviation is therefore one-directional rather than mixed, and its most likely origin is a property of the simulated stock rather than of the behavioural model: every archetype is built on a single NECB 2017 / NBC 9.36 envelope, i.e. a current-code building, whereas the SHEU regional averages are drawn from the existing occupied stock, the large majority of which predates those requirements. A current-code envelope consuming less per heated square metre than the standing stock average is the expected direction, and the EUI-per-m² metric is a *total-energy* quantity dominated by space heating, which — unlike the equipment and lighting channels — was set by that envelope and Zone-6 weather and was never itself SHEU-calibrated; the per-area comparison therefore tests envelope physics, not the behavioural model that the per-household end-use gate validates. To rule out the most obvious artefact, the floor-area denominator was reconciled directly against the simulated IDFs: the EUI divides by EnergyPlus *Net Conditioned Building Area*, which excludes the unconditioned basement and attic and so coincides with SHEU's heated-area-excluding-basement basis (for single-detached both denominators equal ≈ 221 m²), so the offset is not a denominator mismatch. For the two apartment archetypes the building-level denominator additionally includes common corridors; re-normalizing to per-dwelling-unit area (× 1.11) raises mid-rise to ≈ 120 kWh/m², inside its SHEU range, while high-rise remains below its lower bound at ≈ 87 kWh/m². The ordering by envelope-to-occupant ratio (colder zones attaining higher intensities within each archetype class) is physically coherent and consistent with the climatological gradient across the six cities. One adjustment was required during campaign assembly: a deterministic DX-coil sizing correction was applied to the OtherDwelling × Kelowna × 2010 cell, with an effect of no more than 0.013 kWh/m² on that cell's EUI, altering neither the archetype-level reported values nor the cross-check outcome. The household-level SHEU agreement, established here before any timing analysis, is the credibility anchor that validates the model's representation of residential electricity use in the Canadian context; the per-area comparison is reported as a plausibility check whose one-directional offset is attributed to stock vintage and is not used to support any claim in this paper.

**Table 5.** — Stock-weighted annual EUI per archetype against the NRCan SHEU-2019 regional-average intensity ranges (secondary plausibility cross-check), ordered by envelope-to-occupant ratio.

| Archetype | SHEU dwelling type | Simulated EUI 2022 (kWh/m²) | Simulated EUI 2030 (kWh/m²) | SHEU national central (kWh/m²) | SHEU band (regional range, kWh/m²) | Within band? 2022 | Within band? 2030 |
|---|---|---|---|---|---|---|---|
| SingleDetached | Single detached | 115 | 116 | 155.6 | 130.6 – 186.1 | **No — below lower (≈ 12%)** | **No — below lower (≈ 11%)** |
| OtherDwelling | Single attached (double / row / terrace / duplex) | 100 | 101 | 144.4 | 136.1 – 186.1 | **No — below lower (≈ 27%)** | **No — below lower (≈ 26%)** |
| MidRise | Apartment, low-rise (< 5 storeys) | 108 | 108 | 144.4 | 111.1 – 216.7 | **No — below lower (≈ 3%)** | **No — below lower (≈ 3%)** |
| HighRise | Apartment, high-rise (≥ 5 storeys) | 78 | 79 | 130.6 | 113.9 – 147.2 | **No — below lower (≈ 31%)** | **No — below lower (≈ 31%)** |

**Notes:**
- SHEU central values and bands: NRCan *Survey of Household Energy Use 2019*, Table 3.3b (national central) and Table 3.3a (regional range) — total all-fuels site energy per heated area excluding basement and garage; 1 GJ = 277.78 kWh; suppressed regional cells excluded from the range.
- Simulated EUI (rounded to the nearest integer) is computed on the EnergyPlus net conditioned building area, which coincides with the SHEU heated-area basis; the apartment values divide by building floor area including common corridors, and per-dwelling-unit normalization (×1.11) raises mid-rise to ≈ 120 kWh/m², placing it inside its SHEU range, while high-rise remains below its lower bound at ≈ 87 kWh/m² (§5.2).
- The binding calibration gate is the per-household end-use comparison (48 of 48 dwelling-by-year cells within ±2.7%; §5.4); the per-area comparison above is a secondary plausibility cross-check.
- **Values corrected 2026-08-06.** An earlier version of this table reported 200 / 115 / 170 / 128 kWh/m² for 2022. Those figures were inflated by a defect in the end-use extraction routine that summed the EnergyPlus peak-demand report into the annual energy total, and, in runs written in inch-pound units, also summed water volume as if it were energy. The defect was identified and quantified against all 6,000 campaign runs; the corrected values above are computed from each run's own annual end-use report and agree with the independent hourly-meter stream to within 0.07%. The SHEU reference bands are unchanged.


---

### 5.3 Diurnal Load-Shape Reshaping and Peak-Hour Stability

The grid-relevant question is not whether annual energy changes — §5.2 shows it barely does — but whether the timing of demand shifts in a way that alters coincident peak load. The answer is a reshaping of the midday profile with a stable evening peak. Summing all households' hourly demand into a stock-level building profile before locating the daily maximum — the metric that determines coincident peak load — the mean hour of peak demand remains within a narrow 17.0–17.7 h band across all five survey and forecast cycles (17.70 h in 2005, narrowing to 17.02 h by 2030), with the equipment electricity channel dominant in the 17:00–18:00 window. Work-from-home adoption does not push this system-level peak later into the evening, nor does it create a new midday secondary peak sufficient to exceed the evening maximum. Instead, the signature effect is a filling of the midday valley and a modest flattening of the load ratio between off-peak and on-peak hours (Figure 6a).

The paired within-household design (§4) isolates this reshaping cleanly by controlling for dwelling-level fixed effects. The midday energy share increases by +0.367 percentage points (95% CI [+0.208, +0.526]), excluding zero. The load factor — the ratio of mean to peak daily demand — increases by +0.0117 (95% CI [+0.0085, +0.0150]), also excluding zero. Both metrics confirm that the diurnal profile becomes more uniform: more energy is consumed outside the evening peak window, not additional energy during it. For the paired annual energy differential the confidence interval is wide and includes zero, which is expected given the Monte Carlo sample size of N = 50 households per cell and a 95% CI half-width averaging 1.80% (worst cell 4.04%); the shape metrics, being less sensitive to household-level variance in annual consumption, achieve the separation needed for inference (Figure 6b).

The longitudinal trajectory of all four shape metrics — midday energy share, load factor, peak-to-average ratio, and mean peak hour — places this finding in the multi-cycle context that the cross-sectional paired delta cannot provide (Figure S8, Appendix); because the household panel changes at the 2015→2022 boundary (§4.3), this trajectory is a cross-sectional trend across cycle-years rather than a single six-cycle matched-household series, and the 2015→2022 step should be read accordingly. The COVID break at 2022 is visible in the trajectory as a step in the shape metrics (load factor increment approximately +0.009 at that cycle), with the 2030 forecast extending rather than reversing the shift — the 2022→2030 leg of that extension is fully within-panel and retains the complete paired attribution. The mean peak hour panel is the most diagnostic, and from 2022 onward it resolves two distinct quantities that are reported together rather than conflated. At the building-stock level — the quantity that determines coincident peak load and the one plotted as the panel's primary series — dispersion around the 17.0–17.7 h band stays minimal across all five cycles, confirming that peak-hour stability is a systematic property of the stock rather than a cancellation artefact. At the household level, however, a genuine post-COVID behavioural signal emerges: the circular mean of individual households' own peak hours drops to approximately 15.1 h in both 2022 and 2030 (circular standard deviation ≈ 3.8–4.1 h, shown as a secondary annotation on the same panel), because roughly a quarter of households — 22–25% nationally, ranging 14–38% by archetype — now individually peak in the morning rather than the evening, a pattern that was effectively absent in 2005–2015 (household-level circular SD ≤ 1.0 h in those cycles). This household-level diversification does not threaten the system-level peak because the stock aggregate is load-weighted, not household-weighted: the evening-peaking majority carries more combined demand than the morning-peaking minority, so the two statistics diverge without contradiction — a stationary coincident peak and a diversifying population of individual schedules are simultaneously true. At the system level, the stock-weighted ensemble daily load shape (Figure 6c) replicates the midday fill seen in individual archetypes, with the coincidence factor remaining below unity — occupant diversity across households flattens the aggregate peak relative to any single dwelling, a standard attenuation that WFH does not reverse. The central finding of this subsection is therefore two-sided: individual household schedules are diversifying under work-from-home, while the coincident system peak they collectively produce remains stationary at ~17:30 — the demand-timing headline for grid planning purposes is a stable evening peak accompanied by a more uniform intraday load and a growing minority of morning-leaning households, not a new peak-hour threat.

**Figure 6.** — **Diurnal load-shape reshaping under work-from-home.** (a) Average hourly electricity demand over a day, most recent observed cycle vs 2030 forecast, each with a shaded uncertainty band; (b) average hour-by-hour paired within-household difference (forecast − recent), with a confidence band read against the zero line and the WFH midday window highlighted; (c) stock-weighted ensemble daily load shape (archetypes/cities combined by stock share), recent vs forecast, with the coincidence factor annotated.

![Figure 6](figures/Figure_06_loadshape.png)

---

### 5.4 End-Use Resolution: Magnitude Correction without Peak Displacement

The question addressed here is what the activity-derived equipment model (Step 9) adds over a presence-only occupancy baseline in terms of annual magnitude and intraday shape. On annual magnitude the contribution is substantial. The presence-only baseline substantially over-predicts plug-load electricity for detached and attached dwelling types, with simulated baseline values in the range 6,550–6,870 kWh per household per year against SHEU survey-based targets of 3,139–3,700 kWh. The activity model corrects this by tying equipment operation to modelled activity events rather than to occupant presence alone, and the single-detached activity arm lands on the SHEU annual anchor of approximately 3,700 kWh (Figure 7a). Across all 48 dwelling-by-year cells (4 archetypes × 6 cities × 2 years), the activity model passes the calibration gate: every cell falls within ±2.7% of the SHEU target (maximum deviations: +2.33% for equipment, +2.63% for lighting), comfortably within both the design tolerance of ±10% and the hard gate of ±15% (Figures S5–S6, Appendix). Climate stability is also confirmed, with deviations remaining below 3% across all six climate zones. The absolute SHEU annual targets used as calibration anchors are: equipment — SingleDetached 3,700 kWh, OtherDwelling 3,139 kWh, MidRise 2,166 kWh, HighRise 1,922 kWh; lighting — SingleDetached 1,262 kWh, OtherDwelling 1,100 kWh, MidRise 736 kWh, HighRise 736 kWh. The 4,800 paired baseline-versus-activity runs — of which 4,795 carried complete meter output (5 documented exclusions, no more than 0.11% of the analysis grid; every retained bucket n ≥ 48) — yielded zero failures at final validation.

On intraday shape, deriving equipment activation from modelled activity produces a discernibly different profile than a fixed schedule baseline: the activity arm exhibits a more pronounced morning rise and a sharper evening concentration. However, this reshaping does not move the peak hour. Across all 24 archetype-by-city cells, the building-level equipment peak-hour shift is 0 ± 1 h (mean −0.12 h, σ = 0.39 h), with both arms cresting in the evening — equipment in the 17:00–18:00 window and lighting in the 18:00–21:00 window (Figure 7b). The per-cell stem plot confirms this null result directly: stem lengths are near-zero throughout, and the convergence of baseline and activity peak markers is itself the finding (Figure S7, Appendix). The activity model's contribution is therefore end-use magnitude correction and behaviourally timed intraday shape, not peak displacement. The timing headline established in §5.3 — a stable ~17:30 peak — holds for both occupancy-driven and activity-driven demand representations. All timing results in this section derive from the corrected, fully re-simulated campaigns (§4.2).

**Figure 7.** — **Activity-driven equipment: magnitude correction and intraday shape.** (a) Default versus activity-driven equipment demand — one panel per archetype, single-detached in absolute terms with the annual total held to the survey-based energy anchor and the others normalized to daily mean, each overlaying default vs activity-driven with peak-hour markers; (b) activity-driven equipment diurnal load shape — daily shape of equipment demand per archetype, each curve normalized to its own daily mean, baseline vs activity-driven with peak-hour markers, showing a more pronounced morning rise and sharper evening concentration yet both curves peaking at essentially the same evening hour.

![Figure 7](figures/Figure_07_activity_equipment.png)

---

# 6 Discussion

The six-dimension gap matrix of §1.2 (Table 1) identified an open cell that no prior study occupies — a calibrated behavioural occupancy forecast carried through the COVID/work-from-home structural break to 2030 and run through paired stock-scale building-energy simulation that resolves the load *shape* rather than the annual total. The present results fill it with a specific and partly counter-intuitive finding: the behavioural break is large and persistent (§5.1), yet its annual-energy footprint is small (+1.4 to +2.6% across the break, +0.6 to +1.2% to 2030; Table 5), while its effect on the diurnal load shape is structural, a filling of the midday valley and a measurable flattening of the load factor with the evening peak held stationary at ~17:30 (Figure 6), so the "how much" versus "when" distinction is not rhetorical — in well-insulated Canadian housing the occupant redistributes demand far more than augments it, and a model reporting only annual energy is blind to the change that matters most for the grid.

This positions the work against the nearest competitors in the matrix: the closest methodological precedent supplies a paired stock-scale simulation design but applies it retrospectively; the nearest behavioural study documents long-term time-use change yet stops at statistical analysis without forecasting forward or running building-energy simulation; and the nearest stock-scale forecaster projects future building energy while holding occupant behaviour static at pre-pandemic schedules — so the contribution here is to join forecast-through-the-break occupancy to physical load-shape simulation in a single calibrated chain.

The conservative annual-electricity increments are attributional rather than physical: the paired frozen-frame design (§4.3) varies only the occupancy time-series, holding envelope, weather, appliance stock, and tariff fixed, so the reported delta is the pure occupancy channel and necessarily sits well below all-cause pandemic figures such as the weather-adjusted +7.9% residential electricity increase that also absorbs equipment acquisition, thermostat behaviour, and dwelling-occupancy turnover; the behavioural premise itself is consistent with the independent literature, aligning with the roughly fourfold post-pandemic settling of work-from-home — about 20% of full workdays against 5% before — and with the order of the ~+12% structural increase in residential in-home energy demand documented for the Canadian context, so that the occupant's principal effect is on the timing and intraday distribution of load while the annual-magnitude channel, taken alone, is genuinely modest.

Activity resolution earns its place on two honest grounds: it corrects a substantial presence-only over-prediction of plug load in the detached and attached archetypes (baseline ≈ 6,550–6,870 kWh against SHEU targets of 3,139–3,700 kWh), bringing every one of the 48 dwelling-by-year cells within ±2.7% of its benchmark with total energy conserved (Figure 7a), and it produces a more pronounced morning rise and sharper evening concentration than a fixed schedule — yet what it does not do is move the peak, the building-level equipment peak-hour shift being a verified null of 0 ± 1 h (mean −0.12 h, σ = 0.39 h) across all 24 archetype-by-city cells (Figure 7b), so the activity layer's contribution is end-use magnitude calibration plus behaviourally timed shape while the paper's timing headline remains the occupancy-driven midday fill at a stationary evening peak, with co-presence entering only as a load-shaping refinement and not an independent novelty claim.

The operational reading follows directly: a stationary evening peak combined with a filled midday valley is a benign annual-energy story but a consequential operational one, because at the fleet level a flatter intraday profile with an unmoved ~17:30 maximum and a coincidence factor below unity (Figure 6c) reshapes the ramp into the evening peak and widens the midday window available for demand-response and distributed-generation absorption without relieving the capacity constraint set by the evening coincident peak itself — work-from-home does not defuse the residential peak, it redistributes the hours around a peak that stays put.

For code and standards practice the implication is sharper still: static ASHRAE/NECB diversity schedules encode a pre-pandemic intraday shape that this study shows to be structurally outdated in its midday segment, and where the authors' prior line proposed an occupancy-driven code-calibration factor for the *magnitude* error, the present results extend that proposal from magnitude to *shape*, arguing for schedule-shape recalibration synchronized with the national time-use survey cycle so that the diversity profiles embedded in stock-scale modelling track the behavioural break rather than lag a decade behind it.

Finally, the paired within-household Monte-Carlo design is what makes a small signal legible — differencing each household against itself cancels envelope, climate, and stock variation and removes between-household sampling noise, so that load-shape shifts whose confidence intervals exclude zero are recoverable at only N = 50 households per cell (Figure 6b) — and the campaign's phase-alignment check (§4) underlines a transferable lesson for occupancy-driven simulation: annual-energy validation, however thorough, is phase-invariant and therefore cannot certify a timing result, so a load-shape claim demands a dedicated phase-level check.

---

# 7 Limitations

Several limitations bound the interpretation of the results, each stated with the design choice, mitigation, or sensitivity analysis that contains it. The most consequential correctness issue — the four-hour schedule-injection phase error — was diagnosed and fully resolved by re-simulation during the campaign and is documented in §4; because annual energy is phase-invariant the magnitude and SHEU-calibration results were never affected, and the corrected timing is what the results report.

Of the standing scope limitations, the metabolic (internal-heat-gain) channel rides the raw J3 activity mix and is not independently calibrated against a survey benchmark, unlike the SHEU-anchored equipment and lighting channels; this is bounded rather than open, because occupancy — the dominant residential internal-gain driver — is itself calibrated, the activity-to-watts mapping is grounded in recognized standards (2024 Adult Compendium MET values referenced to ASHRAE 55 / ISO 7730) and applied conservatively at 70 W/MET against a ~60 kg reference adult, and an activity-side raking facility exists and could anchor the metabolic mix should a suitable benchmark become available.

Two resolution choices simplify the temporal representation — Saturday and Sunday are pooled into a single weekend day-type and the EnergyPlus reporting interval is hourly — but both are deliberate cost compromises rather than data losses, since the finer 30-minute structure is preserved upstream through harmonization, augmentation, and calibration and the hourly down-sampling occurs only at the simulation interface, where it does not alter the evening-weekday peak-stability finding.

The simulation also holds a single Montréal Zone-6 envelope fixed across all six climate cities, freezes the dwelling stock at two fixed analytical frames (144,507 households for 2005-2015; a refined 144,465-household frame for 2022-2030, §4.3), uses Typical Meteorological Year rather than future weather, and maps Atlantic-province households onto the Montréal EPW; these are isolation choices whose effect the paired design cancels exactly within each panel — each household is differenced against itself, so envelope, climate file, and frozen stock cannot bias the within-panel behavioural signal — though they do bound the absolute EUI levels and limit cross-climate generalization of the magnitude figures, with a Zone-7A cold-zone EUI sensitivity the natural check and future weather files and stock turnover the appropriate vehicle for projecting absolute future demand. A related scope limitation is that the household panel is not identical across the full 2005-2030 span: the 2026-07-09 region-tier relink refined the analytical frame for 2022 and 2030 only, so the longitudinal trajectory (Figure S8, §5.3) is a cross-sectional trend across two independently-sampled panels rather than a single six-cycle matched-household series; the paper's primary paired comparison (2022→2030, §5.3-§5.4) is unaffected, since both cycles share the same refined-frame panel.

A further, more consequential provenance issue affects the reported 2022→2030 at-home magnitude specifically. The 2030 forecast's occupancy (AT_HOME) calibration was raked against the pre-relink 2022 reference population, and this calibration was not re-run after the 2026-07-09 household-frame relink that the rest of the 2022 and 2030 analytical frame now uses. Because the pre-relink reference carried a materially higher weekday at-home level than the post-relink 2022 population that Figure 5 and §5.1 otherwise report, the 2022→2030 at-home gap as currently plotted is inflated relative to what a fully recalibrated 2030 forecast would show. The qualitative direction of the finding — a persistent, elevated work-from-home signal in 2030 relative to the pre-pandemic baseline — is not in question, since it is independently corroborated by the Step-6 calibration validation; but the specific magnitude of the 2022→2030 step reported in §5.1 (+2.2 to +3.9 percentage points) and visualized in Figure 5 should be treated as provisional pending a recalibration of the 2030 occupancy forecast against the current, post-relink household frame.

The Census–GSS linkage is a statistical match and, like all such matches, rests on a conditional-independence assumption between the carried diary behaviour and the dwelling variables given the match keys; this is mitigated by a parsimonious, predictive seven-key match vector, a probabilistic rather than deterministic assignment, and a transparently reported match-tier distribution (Tier-1 44.94%, Tier-2 21.39%, Tier-3 33.67%, FailSafe 0.00%) in which the FailSafe tier is never invoked, so the risk is contained rather than eliminated.

The four GSS cycles span a collection-mode transition from telephone interviewing to an electronic questionnaire that could in principle confound a cross-cycle comparison, but the effect is absorbed by ex-post harmonization, per-cycle calibration, and explicit COLLECT_MODE conditioning, and in any case the headline COVID break (+5.2 pp weekday at-home at 2015→2022) is far larger than any plausible mode effect and survives demographic standardization.

Finally, the 2030 forecast is generated under a single scenario in which the work-from-home shift persists with probability one; this is framed explicitly as the high-persistence upper bound rather than a central estimate, with a high-reversion counter-scenario the natural sensitivity analysis that would convert the point forecast into a bracketed range, so the 2030 numbers should be read as a persistence-conditioned projection rather than an unconditional prediction.

---

# 8 Conclusion

This paper asked whether a calibrated, behaviourally grounded occupancy time-series — built from four Canadian General Social Survey time-use cycles, augmented by a gate-selected conditional Transformer, linked to the 2021 Census stock, and forecast through the COVID/work-from-home structural break to 2030 — changes *when* Canadian residential energy is used, not merely *how much*. Answering it required assembling the full chain end to end and then isolating the behavioural channel with a paired stock-scale simulation design, so that the resulting load-shape change could be attributed to occupancy alone. The evidence supports a clear answer: the behavioural break reshapes the residential load curve structurally while leaving its annual magnitude and its evening peak hour essentially intact.

The principal findings are the following.

1. An end-to-end national pipeline — 64,061 valid GSS diaries augmented to roughly 192,183 calibrated diary-days, linked to a 144,507-household Census frame, and simulated through 6,000 paired EnergyPlus runs — produces physically plausible energy at stock scale, calibrated to within ±2.7% of NRCan SHEU-2019 per-household end-use benchmarks across all 48 dwelling-by-year cells, with archetype energy-use intensities consistent with the SHEU regional-average ranges.

2. The COVID/work-from-home break is the dominant behavioural signal in the data: weekday at-home occupancy rises by +5.2 percentage points at the 2015→2022 transition, persists at +2.2 to +3.9 percentage points above the pre-pandemic baseline in the 2030 forecast, and is separable from compositional sample aging by demographic standardization.

3. The load-shape consequence of that break is a filling of the midday valley and a flattening of the intraday profile, accompanied by a stationary evening peak at approximately 17:30; the paired within-household differentials place both shape changes with confidence intervals that exclude zero, while annual electricity magnitude moves only +1.4 to +2.6% across the break and +0.6 to +1.2% to 2030.

4. Activity-resolved end uses reproduce the SHEU benchmark within ±2.7% in all 48 dwelling-by-year cells (maximum +2.33% equipment, +2.63% lighting) and correct the presence-only baseline's over-prediction of detached and attached plug load while conserving annual energy; the activity arm restructures the intraday equipment shape but leaves the building-level peak hour unchanged — a verified null peak shift of 0 ± 1 h. The paper's timing headline is therefore the occupancy-driven midday fill, and the activity layer delivers magnitude calibration and behaviourally timed shape rather than peak displacement.

5. The paired frozen-frame Monte-Carlo design — fixed household panels held constant within each of two cycle-year spans (2005-2015; 2022-2030), with envelope and weather held fixed throughout — attributes the within-panel shifts to the occupancy time-series alone, and is what renders a small but real load-shape signal statistically legible at stock scale; the paper's headline 2022→2030 comparison is fully within-panel.

Taken together, these results establish that time-varying, survey-grounded occupancy schedules are feasible at building-stock scale and that they materially change the ramping- and demand-response-relevant load metrics that static schedules cannot represent. The methodological reach of the study is bounded by the scope choices set out in §7, and several of them point directly to the next steps. The 2030 projection should be bracketed with a high-reversion persistence scenario to complement the high-persistence bound reported here; absolute future demand should be projected with future weather files and an evolving dwelling stock rather than the frozen-frame isolation used for attribution; the metabolic channel invites independent calibration; and finer temporal and spatial resolution — a Saturday/Sunday split, sub-hourly reporting, and room-level or multi-zone occupancy — would sharpen the intraday and within-dwelling picture. The most direct extension is geographic rather than technical: the pipeline is tied to Canada only through its calibration data, and any country holding a repeated national time-use survey, a household microdata frame, and a national end-use benchmark can rebuild the same forecast for its own stock — the magnitudes reported here are Canadian, but the method that produces them is not. The central message, however, is already firm: in the Canadian residential stock the behavioural future is mostly a question of *when*, and a forecasting pipeline that resolves timing, not just totals, is what the grid-facing questions now require.

---

## References

- Abdeen, A., Kharvari, F., O'Brien, W. and Gunay, B. (2021). The impact of the COVID-19 on households' hourly electricity consumption in Canada. *Energy and Buildings*, 250, 111280. https://doi.org/10.1016/j.enbuild.2021.111280.

- Aerts, D., Minnen, J., Glorieux, I., Wouters, I. and Descamps, F. (2014). A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. *Building and Environment*, 75, pp. 67–78. https://doi.org/10.1016/j.buildenv.2014.01.021.

- Armstrong, M.M., Swinton, M.C., Ribberink, H., Beausoleil-Morrison, I. and Millette, J. (2009). Synthetically derived profiles for representing occupant-driven electric loads in Canadian housing. *Journal of Building Performance Simulation*, 2(1), pp. 15–30. https://doi.org/10.1080/19401490802706653.

- ASHRAE (2023). *ANSI/ASHRAE Standard 55-2023: Thermal Environmental Conditions for Human Occupancy*. Atlanta, GA: American Society of Heating, Refrigerating and Air-Conditioning Engineers.

- Austin, J., Johnson, D.D., Ho, J., Tarlow, D. and van den Berg, R. (2021). Structured denoising diffusion models in discrete state-spaces. *Advances in Neural Information Processing Systems*, 34, pp. 17981–17993. https://proceedings.neurips.cc/paper/2021/hash/958c530554f78bcd8e97125b70e6973d-Abstract.html.

- Barrero, J.M., Bloom, N. and Davis, S.J. (2021). Why working from home will stick. *NBER Working Paper No. 28731*. https://doi.org/10.3386/w28731.

- Beckman, R.J., Baggerly, K.A. and McKay, M.D. (1996). Creating synthetic baseline populations. *Transportation Research Part A: Policy and Practice*, 30(6), pp. 415–429. https://doi.org/10.1016/0965-8564(96)00004-3.

- Chen, J., Adhikari, R., Wilson, E., Robertson, J., Fontanini, A., Polly, B. and Olawale, O. (2022). Stochastic simulation of occupant-driven energy use in a bottom-up residential building stock model. *Applied Energy*, 325, 119890. https://doi.org/10.1016/j.apenergy.2022.119890.

- Chiou, Y.-S., Carley, K.M., Davidson, C.I. and Johnson, M.P. (2011). A high spatial resolution residential energy model based on American Time Use Survey data and the bootstrap sampling method. *Energy and Buildings*, 43(12), pp. 3528–3538. https://doi.org/10.1016/j.enbuild.2011.09.020.

- Cicala, S. (2023). JUE Insight: Powering work from home. *Journal of Urban Economics*, 133, 103474. https://doi.org/10.1016/j.jue.2022.103474.

- D'Orazio, M., Di Zio, M. and Scanu, M. (2006). *Statistical Matching: Theory and Practice*. Chichester: John Wiley & Sons. https://doi.org/10.1002/0470023554.

- de Wilde, P. (2014). The gap between predicted and measured energy performance of buildings: A framework for investigation. *Automation in Construction*, 41, pp. 40–49. https://doi.org/10.1016/j.autcon.2014.02.009.

- Elsayed, M. et al. (2023). Post-occupancy evaluation in residential buildings: A systematic literature review of current practices in the EU. *Building and Environment*, 236, 110307. https://doi.org/10.1016/j.buildenv.2023.110307.

- Eurostat (2018). *Harmonised European Time Use Surveys (HETUS): 2018 Guidelines*. Luxembourg: Publications Office of the European Union (KS-GQ-19-003; re-edition 2020, KS-GQ-20-011). https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/ks-gq-19-003.

- Ferreira, S., Gunay, B., Papineau, M. and Nojedehi, P. (2024). From time to energy use: shaping high-resolution residential Canadian appliance use models. *eSim 2024 (IBPSA-Canada)*. https://publications.ibpsa.org/proceedings/esim/2024/esim2024_149.pdf.

- Fischer, D., Surmann, A., Biener, W. and Selinger-Lutz, O. (2020). From residential electric load profiles to flexibility profiles — A stochastic bottom-up approach. *Energy and Buildings*, 224, 110133. https://doi.org/10.1016/j.enbuild.2020.110133.

- Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M. and Bouchachia, A. (2014). A survey on concept drift adaptation. *ACM Computing Surveys*, 46(4), pp. 1–37. https://doi.org/10.1145/2523813.

- Guo, N., Jiang, W., Pothuru, Y. and Yang, B. (2026). Mapping the midweek mountain: The new geography of hybrid work. *arXiv:2603.18440*. https://doi.org/10.48550/arXiv.2603.18440.

- Herrmann, S.D., Willis, E.A., Ainsworth, B.E., Barreira, T.V., Hastert, M., Kracht, C.L., Schuna, J.M. Jr., Cai, Z., Quan, M., Tudor-Locke, C., Whitt-Glover, M.C. and Jacobs, D.R. Jr. (2024). 2024 Adult Compendium of Physical Activities: A third update of the energy costs of human activities. *Journal of Sport and Health Science*, 13(1), pp. 6–12. https://doi.org/10.1016/j.jshs.2023.10.010.

- Hong, T., Yan, D., D'Oca, S. and Chen, C. (2017). Ten questions concerning occupant behavior in buildings: The big picture. *Building and Environment*, 114, pp. 518–530. https://doi.org/10.1016/j.buildenv.2016.12.006.

- ISO (2005). *ISO 7730:2005 — Ergonomics of the thermal environment: Analytical determination and interpretation of thermal comfort using calculation of the PMV and PPD indices and local thermal comfort criteria*. Geneva: International Organization for Standardization.

- Iseri, O.K., Dino, I.G. and Kalkan, S. (2026). Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 117155. https://doi.org/10.1016/j.enbuild.2026.117155.

- Iseri, O.K. and Hachem-Vermette, C. (under review). *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials*. Journal of Building Performance Simulation. ⚠ *check source — confirm final venue and status at typesetting.*

- Iseri, O.K. and Hachem-Vermette, C. (2026). Longitudinal analysis of occupancy-driven energy demand in Canadian residential buildings (2005–2025). *eSim 2026 (IBPSA-Canada)*.

- Jalilian, M. and Kamel, R. (2025). Urban-scale building energy modeling under future climate scenarios. *Frontiers in Energy Research*, 13, 1683787. https://doi.org/10.3389/fenrg.2025.1683787.

- Lou, A., Meng, C. and Ermon, S. (2024). Discrete diffusion modeling by estimating the ratios of the data distribution. In: *Proceedings of the 41st International Conference on Machine Learning (ICML 2024)*, PMLR 235, pp. 32819–32848. https://proceedings.mlr.press/v235/lou24a.html.

- Mahdavi, A. et al. (2021). The Role of Occupants in Buildings' Energy Performance Gap: Myth or Reality? *Sustainability*, 13(6), 3146. https://doi.org/10.3390/su13063146.

- Mitra, D., Steinmetz, N., Chu, Y. and Cetin, K.S. (2020). Typical occupancy profiles and behaviors in residential buildings in the United States. *Energy and Buildings*, 210, 109713. https://doi.org/10.1016/j.enbuild.2019.109713.

- Motuzienė, V., Bielskus, J., Lapinskienė, V., Rynkun, G. and Bernatavičienė, J. (2022). Office buildings occupancy analysis and prediction associated with the impact of the COVID-19 pandemic. *Sustainable Cities and Society*, 76, 103557. https://doi.org/10.1016/j.scs.2021.103557.

- National Research Council Canada (2017). *National Energy Code of Canada for Buildings 2017*, Fourth Edition. Ottawa: Canadian Commission on Building and Fire Codes (Cat. NR24-24/2017E-PDF; ISBN 0-660-24321-4; https://doi.org/10.4224/40002011). https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-energy-code-canada-buildings-2017.

- National Research Council Canada (2020). *National Building Code of Canada 2020*, Division B, Section 9.36 (Energy Efficiency), Fifteenth Edition. Ottawa: Canadian Commission on Building and Fire Codes (Cat. NR24-28/2020E-PDF; ISBN 978-0-660-37912-8; https://doi.org/10.4224/w324-hv93). https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications.

- Natural Resources Canada (2019). *Survey of Household Energy Use (SHEU), 2019* — Data Tables. Office of Energy Efficiency, Natural Resources Canada (comparative energy-intensity series: CODR table 25-10-0061-01). https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm (accessed 10 June 2026).

- O'Brien, W., Wagner, A., Schweiker, M., Mahdavi, A., Day, J., Kjærgaard, M.B., Carlucci, S., Dong, B., Tahmasebi, F., Yan, D., Hong, T., Gunay, H.B., Nagy, Z., Miller, C. and Berger, C. (2020). Introducing IEA EBC Annex 79: Key challenges and opportunities in the field of occupant-centric building design and operation. *Building and Environment*, 178, 106738. https://doi.org/10.1016/j.buildenv.2020.106738.

- Osman, M. and Ouf, M. (2021). A comprehensive review of time use surveys in modelling occupant presence and behavior. *Building and Environment*, 196, 107785. https://doi.org/10.1016/j.buildenv.2021.107785.

- Osman, M., Ouf, M., Azar, E. and Dong, B. (2023). Stochastic bottom-up load profile generator for Canadian households' electricity demand. *Building and Environment*, 241, 110490. https://doi.org/10.1016/j.buildenv.2023.110490.

- Putra, H.C., Andrews, C. and Hong, T. (2021). Generating synthetic occupants for use in building performance simulation. *Journal of Building Performance Simulation*, 14(6), pp. 712–729. https://doi.org/10.1080/19401493.2021.2000029.

- Rässler, S. (2002). *Statistical Matching: A Frequentist Theory, Practical Applications, and Alternative Bayesian Approaches*. Lecture Notes in Statistics, vol. 168. New York: Springer. https://doi.org/10.1007/978-1-4613-0053-3.

- Reinhart, C.F. and Cerezo Davila, C. (2016). Urban building energy modeling — A review of a nascent field. *Building and Environment*, 97, pp. 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001.

- Richardson, I., Thomson, M. and Infield, D. (2008). A high-resolution domestic building occupancy model for energy demand simulations. *Energy and Buildings*, 40(8), pp. 1560–1566. https://doi.org/10.1016/j.enbuild.2008.02.006.

- Richardson, I., Thomson, M., Infield, D. and Clifford, C. (2010). Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings*, 42(10), pp. 1878–1887. https://doi.org/10.1016/j.enbuild.2010.05.023.

- Sahoo, S.S., Arriola, M., Gokaslan, A., Marroquin, E.M., Rush, A.M., Schiff, Y., Chiu, J.T. and Kuleshov, V. (2024). Simple and effective masked diffusion language models. In: *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*. https://openreview.net/forum?id=L4uaAR4ArM.

- Statistics Canada (2012). *2011 National Household Survey*. https://www12.statcan.gc.ca/nhs-enm/index-eng.cfm (accessed 15 February 2026).

- Statistics Canada (2021). *Census of Population, 2021: Public Use Microdata Files* (Series Catalogue no. 98M0001X). Individuals File: 98M0001X2021001 (released 12 September 2023); Hierarchical File: 98M0001X2021002 (released 20 March 2024). https://www150.statcan.gc.ca/n1/en/catalogue/98M0001X (accessed 15 February 2026).

- Statistics Canada (2022). *General Social Survey – Time Use: Public Use Microdata Files* (Series Catalogue no. 45-25-0001; series DOI https://doi.org/10.25318/45250001-eng). Individual cycles: 12M0019X (Cycle 19, 2005), 12M0024X (Cycle 24, 2010), 89M0034X (Cycle 29, 2015), and 45-25-0001 issue 2025001 (Time Use, 2022). https://www150.statcan.gc.ca/n1/pub/45-25-0001/index-eng.htm (accessed 15 February 2026).

- Statistics Canada (2026). *Population Projections for Canada (2025 to 2075), Provinces and Territories* (Catalogue no. 17-20-0003, M1 medium-growth scenario, base year 2025; supersedes the discontinued series 91-520-X). https://www150.statcan.gc.ca/n1/pub/17-20-0003/172000032026001-eng.htm (accessed 15 February 2026).

- U.S. Department of Energy (2024). *EnergyPlus™ (Version 24.2.0)*. National Renewable Energy Laboratory (NREL). https://energyplus.net/.

- Widén, J. and Wäckelgård, E. (2010). A high-resolution stochastic model of domestic activity patterns and electricity demand. *Applied Energy*, 87(6), pp. 1880–1892. https://doi.org/10.1016/j.apenergy.2009.11.006.

- Wilke, U., Haldi, F. and Robinson, D. (2011). A model of occupants' activities based on time use survey data. *Proceedings of Building Simulation 2011 (IBPSA)*.

- Wilke, U., Haldi, F., Scartezzini, J.-L. and Robinson, D. (2013). A bottom-up stochastic model to predict building occupants' time-dependent activities. *Building and Environment*, 60, pp. 254–264. https://doi.org/10.1016/j.buildenv.2012.10.021.

- Yamaguchi, Y. and Shimoda, Y. (2017). A stochastic model to predict occupants' activities at home for community-/urban-scale energy demand modelling. *Journal of Building Performance Simulation*, 10(5–6), pp. 565–581. https://doi.org/10.1080/19401493.2017.1336255.

- Yan, D., O'Brien, W., Hong, T., Feng, X., Gunay, H.B., Tahmasebi, F. and Mahdavi, A. (2015). Occupant behavior modeling for building performance simulation: Current state and future challenges. *Energy and Buildings*, 107, pp. 264–278. https://doi.org/10.1016/j.enbuild.2015.08.032.

- Yan, D., Hong, T., Dong, B., Mahdavi, A., D'Oca, S., Gaetani, I. and Feng, X. (2017). IEA EBC Annex 66: Definition and simulation of occupant behavior in buildings. *Energy and Buildings*, 156, pp. 258–270. https://doi.org/10.1016/j.enbuild.2017.09.084.

- Yin, R., Yamaguchi, Y., Zajch, A.M., Uchida, H. and Shimoda, Y. (2024). Long-term changes in time use and impacts on residential energy demand. In: *Proceedings of ASim 2024: 5th Asia Conference of IBPSA*, Osaka, Japan, 8–10 December 2024 (Paper E17_asim2024_1285). Available at: https://publications.ibpsa.org/proceedings/asim/2024/papers/E17_asim2024_1285.pdf.

---

# Appendix — Supplementary Figures

**Figure S1.** — **Gated generative architecture search.** Progressive 2%→20%→100% data funnel across 40+ model families (Markov, autoregressive, VAE, GAN-adjacent, cross-attention, masked diffusion MDLM/SEDD) filtered by four hard distributional gates (activity JS ≤ 0.05; AT_HOME RMS ≤ 5.3 pp; co-presence max ≤ 5.0 pp; composite threshold); only the calibrated J3 architecture clears all four, while MDLM posts the best composite (0.559) yet fails two gates.

![Figure S1](figures/SI/Figure_S01_search_funnel.png)

**Figure S2.** — **Census–GSS probabilistic linkage workflow.** The augmented GSS diary pool (~192,183 diary-days, by day-type stratum) and the 2021 Census PUMF (286,537 individuals) converge on a four-tier hierarchical demographic key-descent match (Tier-1 Perfect 44.94%, Tier-2 Core 21.39%, Tier-3 Constraints 33.67%, Tier-4 FailSafe 0.00%), followed by household aggregation and a plausibility gate, yielding the 144,507-household BEM frame.

![Figure S2](figures/SI/Figure_S02_linkage.png)

**Figure S3.** — **Progressive fine-tuning and True-Future-Test protocol.** The five-node cycle-year rail (2005 → 2010 → 2015 → 2022 → 2030) is connected by weight-inheriting fine-tuning steps (recency weights 0.10 / 0.20 / 0.30 / 0.40), with True-Future-Test holdout evaluations on each next unseen cycle and per-transition DRIFT_MATRIX markers; the 2030 node carries the StatCan M1 demographic scenario injection (37,008 diary-rows).

![Figure S3](figures/SI/Figure_S03_forecasting.png)

**Figure S4.** — **Activity-driven end-use load model structure.** A fixed 24/7 baseload lane (fridge, freezer, standby) sits above the activity tier, in which the 14-category activity sequence passes through the 9-end-use × 14-activity crosswalk, sub-linear co-presence scaling, and per-end-use SHEU calibration before producing the per-household equipment and lighting schedules injected into EnergyPlus v24.2.

![Figure S4](figures/SI/Figure_S04_enduse_model.png)

**Figure S5.** — **Equipment annual calibration against SHEU.** Per-cell annual equipment energy, baseline vs activity, against NRCan SHEU dwelling targets (SingleD 3,700 / OtherDwelling 3,139 / MidRise 2,166 / HighRise 1,922 kWh) and the ±15% band.

![Figure S5](figures/SI/Figure_S05_calibration.png)

**Figure S6.** — **Percent deviation from SHEU, all 48 cell-years (the calibration gate).** Per-cell % deviation across every archetype × city × year, ±15% gate marked; every cell passes, max +2.33% equipment / +2.63% lighting.

![Figure S6](figures/SI/Figure_S06_sheu_pct.png)

**Figure S7.** — **Equipment baseline→activity peak-hour shift, all cells (null result).** Per cell, equipment peak hour baseline vs activity, drawn as a stem; markers coincide (0 ± 1 h, mean −0.12 h), the near-zero stem lengths are themselves the finding.

![Figure S7](figures/SI/Figure_S07_peak_shift_null.png)

**Figure S8.** — **Longitudinal load-shape trajectory.** Four summary load-shape metrics (midday energy share, load factor, peak-to-average ratio, mean peak hour) across all cycles, each panel with error bars and a marked COVID break; the mean peak hour panel plots the building-stock aggregate as its primary series with the household-level circular-mean dispersion annotated separately (§5.3).

![Figure S8](figures/SI/Figure_S08_longitudinal.png)

**Figure S9.** — **Annual energy use intensity by archetype and city.** Grouped bar chart of annual EUI for every archetype-and-city combination, paired bars for the recent observed cycle versus the 2030 forecast with error bars (secondary plausibility cross-check; see Table 5, §5.2).

![Figure S9](figures/SI/Figure_S09_eui.png)
