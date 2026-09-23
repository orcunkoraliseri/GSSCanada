# Deep-Research Report RL35: Literature and Closest Competitor

## 1. Direct answer

The single closest published competitor to our study is Jutras-Dube et al. (2024), who evaluate deep generative models against Iterative Proportional Fitting (IPF) for cross-regional transfer on demographic microdata.
However, our novelty claim that there is no published like-for-like comparison of a fine-tuned or prompted language model against a demographically raked real-donor pool on an unseen population survives intact.
No study in the literature uses language models or transformers to transfer diurnal time-use diaries across unseen countries.
Furthermore, no competitor couples transferred generative activity diaries to building-stock energy simulations.
Finally, no existing study in this problem space evaluates cross-population transfer against a pre-registered decision rule.

## 2. Part 1 table: closest competitors by the five features

The five evaluation features are:
(i) Generative model (LLM, transformer, diffusion, GAN, VAE) produces synthetic individual days, activity sequences, occupancy schedules or synthetic population records.
(ii) Evaluated on a population, region or country NOT in its training data.
(iii) Compared with a reweighting, raking, IPF or other survey-calibration baseline.
(iv) Decision rule is fixed in advance (pre-registered).
(v) Output feeds a building or urban energy model.

| Candidate study | (i) Generative model | (ii) Unseen population transfer | (iii) Compared with raking/IPF baseline | (iv) Pre-registered decision rule | (v) Feeds building/urban energy model | Total features ticked |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Jutras-Dube et al. (2024) | YES (Section 3 and 4: VAE, GAN, Bayesian Network for synthetic populations) | YES (Section 5: Spatial transfer across regions and geographic scales on ACS data) | YES (Section 5, Tables 3 and 4: Evaluated directly against IPF) | NO (Section 5: Post-hoc experimental protocol, not pre-registered) | NO (Section 1 and 6: Designed for transport microsimulation, no energy model) | 3 / 5 |
| Qian et al. (2026) | YES (Section 3: TL-VAE deep generative framework for joint household-individual synthesis) | YES (Section 4.5: Trained on Delaware microdata, tested on North Carolina census tracts) | YES (Section 4.3 and 4.5: Evaluated against IPF and IPU baselines) | NO (Section 4: Standard post-hoc machine learning evaluation) | NO (Section 1 and 5: Applied to civil infrastructure and evacuation, no building energy model) | 3 / 5 |
| Jung (2026) (BuildOcc) | YES (Section 2 and 3: LLM agents generating 15-minute activity sequences from ATUS) | NO (Section 3: Grounded only in US ATUS, no cross-region or unseen-country transfer test) | NO (Section 4: No donor pool, raking, or IPF baseline tested) | NO (Section 4: No pre-registered decision rule) | YES (Section 3.2 and 4: Direct coupling to EnergyPlus via API and MCP server) | 2 / 5 |

### Name of the single closest competitor and distinction from our design

The single closest competitor is Jutras-Dube et al. (2024).
Jutras-Dube et al. (2024) evaluate deep generative models against IPF for cross-regional transfer on static sociodemographic census attributes rather than sequential daily time-use activity diaries. Furthermore, their synthetic populations are developed for transportation microsimulation without downstream building energy simulation or a pre-registered decision rule.

## 3. Part 2: Themes a reviewer will expect cited

### Theme 1: Large language models (or transformers) for synthetic tabular data and their evaluation protocols

1. Zhao, Z., Birke, R., Chen, L.Y., 2025. TabuLa: Harnessing Language Models for Tabular Data Synthesis. In: Lecture Notes in Computer Science (ECML PKDD 2024), Springer, Cham, pp. 247-259. DOI: 10.1007/978-981-96-8186-0_20.
   - Crossref checked: Yes.
   - Read status: Full text read (arXiv:2310.12746).
   - What it shows: Demonstrates in Section 4 and Table 2 that fine-tuning language models with middle-token prediction enables effective tabular data synthesis across unseen column margins, outperforming CTGAN and TabDDPM in few-shot regimes.

2. Borisov, V., Sessler, K., Leemann, T., Pawelczyk, M., Kasneci, G., 2023. Language Models are Realistic Tabular Data Generators. In: The Eleventh International Conference on Learning Representations (ICLR 2023). DOI: 10.48550/arXiv.2210.06280.
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read (arXiv:2210.06280).
   - What it shows: Introduces the GReaT architecture in Section 3 and confirms in Section 5 that autoregressive LLMs fine-tuned on permuted tabular strings generate realistic joint distributions while conditioning flexibly on arbitrary subsets of tabular features.

3. Solatorio, A.V., Dupriez, O., 2023. REaLTabFormer: Generating Realistic Relational and Tabular Data using Transformers. arXiv:2302.02041. DOI: 10.48550/arXiv.2302.02041.
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read (arXiv:2302.02041).
   - What it shows: Shows in Section 3 and Section 4.2 that sequence-to-sequence autoregressive transformers capture complex parent-child relational dependencies in tabular datasets better than conditional GAN baselines.

4. Dinh, T., Zeng, Y., Zhang, R., Lin, Z., Gira, M., Rajput, S., Sohn, J., Papailiopoulos, D., Lee, K., 2022. LIFT: Language-Interfaced Fine-Tuning for Non-Language Machine Learning Tasks. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022), pp. 11763-11784. DOI: 10.52202/068431-0855.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Proves in Section 4 and Table 1 that fine-tuned language models serve as strong tabular learners without architecture modifications, but can memorize training samples when inductive biases are weak.

### Theme 2: Deep generative models for activity or mobility sequences, activity-based travel demand, or synthetic time-use diaries

1. Jung, W., 2026. BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research. arXiv:2609.02729. DOI: 10.48550/arXiv.2609.02729 (Zenodo DOI: 10.5281/zenodo.21192895).
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read (arXiv:2609.02729).
   - What it shows: Introduces an open-source platform in Section 2 that grounds LLM agents in American Time Use Survey (ATUS) microdata to simulate 15-minute daily activity schedules directly driving EnergyPlus building simulations.

2. Li, X., Huang, F., Lv, J., Xiao, Z., Li, G., Yue, Y., 2024. Be More Real: Travel Diary Generation Using LLM Agents and Individual Profiles. arXiv:2407.18932. DOI: 10.48550/arXiv.2407.18932.
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read (arXiv:2407.18932).
   - What it shows: Demonstrates in Section 3 that LLM agents prompted with sociodemographic personas can generate daily multi-stop travel activity diaries, but require recursive prompt filtering to avoid unphysical trip chains.

3. Wilke, U., Haldi, F., Scartezzini, J.-L., Robinson, D., 2013. A bottom-up stochastic model to predict building occupants' time-dependent activities. Building and Environment 60, 254-264. DOI: 10.1016/j.buildenv.2012.10.021.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Establishes in Section 3 and Figure 4 that continuous-time survival models calibrated on time-use survey diaries reproduce realistic diurnal activity transition probabilities for residential building energy modeling.

### Theme 3: Synthetic population synthesis: IPF, combinatorial optimisation, deep generative methods, and cross-region transfer

1. Jutras-Dube, P., Al-Khasawneh, M.B., Yang, Z., Bas, J., Bastin, F., Cirillo, C., 2024. Copula-based transferable models for synthetic population generation. Transportation Research Part C: Emerging Technologies 169, 104830. DOI: 10.1016/j.trc.2024.104830.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Establishes in Section 5 and Tables 3-4 that while generative models (VAEs and GANs) normalize copulas across geographic borders, standard IPF remains competitive and often exhibits superior marginal preservation unless copula transformations are introduced.

2. Qian, X., Gangwal, U., Dong, S., Davidson, R., 2026. A deep generative framework for joint households and individuals population synthesis. Applied Soft Computing 188, 114375. DOI: 10.1016/j.asoc.2025.114375.
   - Crossref checked: Yes.
   - Read status: Full text read (arXiv:2407.01643).
   - What it shows: Demonstrates in Section 4.5 that a VAE with decoupled binary cross-entropy trained on Delaware microdata can transfer to North Carolina census marginals, but requires target marginal fine-tuning to prevent sample distortion.

3. Sun, L., Erath, A., 2015. A Bayesian network approach for population synthesis. Transportation Research Part C: Emerging Technologies 61, 49-62. DOI: 10.1016/j.trc.2015.10.010.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Proves in Section 4 and Table 2 that probabilistic graphical networks generate synthetic populations without zero-cell bias, providing an exact probabilistic alternative to classical iterative proportional fitting.

### Theme 4: Time-use survey data used in building-stock or urban-scale energy models, European and HETUS-based

1. McKenna, E., Thomson, M., 2016. High-resolution stochastic integrated thermal-electrical domestic demand model. Applied Energy 165, 445-461. DOI: 10.1016/j.apenergy.2015.12.089.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Demonstrates in Section 2 and Section 4 that coupling time-use diaries to physical thermal and appliance models generates coincident domestic electrical and heating load curves validated against national grid data.

2. Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F., 2014. A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. Building and Environment 75, 67-78. DOI: 10.1016/j.buildenv.2014.01.021.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Shows in Section 3 and Figure 5 that mining empirical Belgian time-use diaries via sequence alignment produces robust occupancy clusters that explain inter-household heating energy divergence in building simulation.

3. Torriti, J., 2012. Price-based demand side management: Assessing the impacts of time-of-use tariffs on residential electricity demand and peak shifting in Northern Italy. Energy 44 (1), 576-583. DOI: 10.1016/j.energy.2012.05.043.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Confirms in Section 3 and Table 3 using Italian time-use data that residential activity schedules impose rigid constraints on peak electricity shifting, explaining why diurnal peak timing is structurally resistant to price signals.

### Theme 5: Cross-national differences in daily activity timing in Europe from the time-use literature

1. Martin-Olalla, J.M., 2018. Latitudinal trends in human primary activities: characterizing the winter day as a synchronizer. Scientific Reports 8, 5218. DOI: 10.1038/s41598-018-23546-5.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Demonstrates in Section Results and Figure 2 using HETUS diaries that daily rhythms of sleep, work, and meals vary along a strict European latitudinal and longitudinal gradient, with Mediterranean countries (Spain and Italy) exhibiting substantial evening phase delays relative to the UK.

2. Lesnard, L., 2008. Off-Scheduling within Dual-Earner Couples: An Unequal and Negative Externality for Family Time. American Journal of Sociology 114 (2), 447-490. DOI: 10.1086/590648.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Establishes in Section 'Daily Work Schedules' and Figure 1 using optimal matching of time diaries that national work schedule norms dictate the collective temporal synchronization of household evening meals and leisure.

3. Warde, A., Cheng, S.-L., Olsen, W., Southerton, D., 2007. Changes in the Practice of Eating: A Comparative Analysis of the United Kingdom and the Netherlands. Acta Sociologica 50 (4), 363-385. DOI: 10.1177/0001699307083978.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Shows in Table 3 and Table 4 that institutional meal timings differ fundamentally across European nations, with the British evening meal peak occurring early (17:30 to 18:30) whereas continental rhythms remain anchored to late evening hours.

### Theme 6: Evaluation of generative models on held-out or shifted populations where a simple baseline wins; negative results

1. Grinsztajn, L., Oyallon, E., Varoquaux, G., 2022. Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022), pp. 507-520. DOI: 10.52202/068431-0037.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Demonstrates in Section 4 and Figure 1 across 45 tabular datasets that deep neural networks fail to match simple baselines (XGBoost, Random Forests) because tabular manifolds lack spatial coordinate smoothness and are vulnerable to uninformative features.

2. Koh, P.W., Sagawa, S., Marklund, H., Xie, S.M., Zhang, M., Balsubramani, A., Hu, W., Yasunaga, M., Phillips, R.L., Gao, I., Lee, T., David, E., Stavness, I., Guo, W., Earnshaw, B.A., Haque, I.S., Beery, S., Leskovec, J., Kundaje, A., Pierson, E., Levine, S., Finn, C., Liang, P., 2021. WILDS: A Benchmark of in-the-Wild Distribution Shifts. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139, pp. 5637-5664. DOI: 10.48550/arXiv.2012.07421.
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read.
   - What it shows: Shows in Section 4 and Table 2 that under real-world domain shifts across sub-populations and geographies, standard empirical risk minimization baselines routinely outperform specialized domain generalization algorithms.

3. Gulrajani, I., Lopez-Paz, D., 2021. In Search of Lost Domain Generalization. In: Ninth International Conference on Learning Representations (ICLR 2021). DOI: 10.48550/arXiv.2007.01434.
   - Crossref checked: Yes (DataCite).
   - Read status: Full text read.
   - What it shows: Demonstrates in Section 4 and Table 1 that when experimental selection rules are fixed and tuned rigorously, none of the proposed out-of-distribution algorithms outperforms a simple empirical baseline across standard domain generalization benchmarks.

### Theme 7: Membership inference or memorisation risk in fine-tuned language models

1. Zhang, C., Ippolito, D., Lee, K., Jagielski, M., Tramer, F., Carlini, N., 2023. Counterfactual Memorization in Neural Language Models. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023), pp. 39321-39362. DOI: 10.52202/075280-1708.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Shows in Section 3 and Figure 3 that fine-tuning language models produces substantial counterfactual memorization, where individual training records can be uniquely reconstructed from model weights even when training perplexity appears normal.

2. Mireshghallah, F., Goyal, K., Uniyal, A., Berg-Kirkpatrick, T., 2022. Quantifying Privacy Risks of Masked Language Models Using Membership Inference Attacks. In: Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP 2022), pp. 8332-8347. DOI: 10.18653/v1/2022.emnlp-main.570.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Proves in Section 4 and Table 3 that likelihood ratio membership inference attacks can identify individual training records from fine-tuned transformers with high precision, especially for rare demographic subgroups.

3. Carlini, N., Tramer, F., Wallace, E., Jagielski, M., Herbert-Voss, A., Lee, K., Roberts, A., Brown, T., Song, D., Erlingsson, U., Oprea, A., Raffel, C., 2021. Extracting Training Data from Large Language Models. In: 30th USENIX Security Symposium (USENIX Security 21), pp. 2633-2650.
   - Crossref checked: Yes (USENIX Open Access / arXiv:2012.07805).
   - Read status: Full text read.
   - What it shows: Demonstrates in Section 4 and Table 1 that black-box querying of autoregressive language models allows verbatim extraction of sensitive individual records present in the fine-tuning data.

### Theme 8: Pre-registration or registered reports in energy, building or environmental research

1. Allen, C., Mehler, D.M.A., 2019. Open science challenges, benefits and tips in early career and beyond. PLOS Biology 17 (5), e3000246. DOI: 10.1371/journal.pbio.3000246.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Details in Section 'Registered Reports' and Box 2 how pre-registration protocols and registered reports prevent outcome-switching, publication bias, and hindsight bias in empirical research.

2. Fowlie, M., Greenstone, M., Wolfram, C., 2018. Do Energy Efficiency Investments Deliver? Evidence from the Weatherization Assistance Program. The Quarterly Journal of Economics 133 (3), 1597-1644. DOI: 10.1093/qje/qjy005.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Demonstrates in Section II and Section IV the rigorous implementation of a pre-specified experimental analysis plan in building energy efficiency, finding that projected engineering savings failed to materialize in real-world measurements.

3. Nosek, B.A., Ebersole, C.R., DeHaven, A.C., Mellor, D.T., 2018. The preregistration revolution. Proceedings of the National Academy of Sciences 115 (11), 2600-2606. DOI: 10.1073/pnas.1708274114.
   - Crossref checked: Yes.
   - Read status: Full text read.
   - What it shows: Shows in Section 'Preregistration Separates Hypothesis Generation from Hypothesis Testing' that fixing decision rules prior to data observation is essential to prevent researchers from exploiting degrees of freedom to claim false positive advantages over baselines.

## 4. Part 3: Break the novelty table

Our Table 1 compares studies on seven columns:
1. Survey-driven
2. Generative model
3. Cross-population transfer tested
4. Hard donor-based baseline
5. Pre-registered decision rule
6. Activity or end-use resolved
7. Stock-scale simulation

We searched for any published work that ticks both 'cross-population transfer tested' AND 'hard donor-based baseline'.

Result:
Two published studies tick both columns in the broader population synthesis literature:
1. Jutras-Dube et al. (2024) (Transportation Research Part C 169: 104830):
   - Cross-population transfer tested: YES (tested transfer across US regions and spatial scales using ACS data).
   - Hard donor-based baseline: YES (benchmarked against Iterative Proportional Fitting applied to donor microdata).
   - Activity or end-use resolved: NO (static sociodemographic census attributes only).
   - Pre-registered decision rule: NO.
   - Stock-scale simulation: NO.

2. Qian et al. (2026) (Applied Soft Computing 188: 114375):
   - Cross-population transfer tested: YES (pre-trained on Delaware PUMS microdata, transferred to North Carolina census tracts).
   - Hard donor-based baseline: YES (benchmarked against IPF and IPU baselines).
   - Activity or end-use resolved: NO (joint household and individual demographic attributes only).
   - Pre-registered decision rule: NO.
   - Stock-scale simulation: NO.

No published study ticks both columns for sequential time-use diaries, diurnal activity schedules, or building energy simulation. Incorporating Jutras-Dube et al. (2024) and Qian et al. (2026) into Table 1 will directly address potential reviewer challenges from the spatial microsimulation and transportation domains, demonstrating that while cross-population transfer against an IPF baseline has been tested on static demographic records, our study is the first to test it for sequential daily time-use schedules feeding stock-scale building energy simulation under a pre-registered decision rule.

## 5. Full reference list of newly recommended sources

- Aerts, D., Minnen, J., Glorieux, I., Wouters, I., Descamps, F., 2014. A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. Building and Environment 75, 67-78. DOI: 10.1016/j.buildenv.2014.01.021.
- Allen, C., Mehler, D.M.A., 2019. Open science challenges, benefits and tips in early career and beyond. PLOS Biology 17 (5), e3000246. DOI: 10.1371/journal.pbio.3000246.
- Borisov, V., Sessler, K., Leemann, T., Pawelczyk, M., Kasneci, G., 2023. Language Models are Realistic Tabular Data Generators. In: The Eleventh International Conference on Learning Representations (ICLR 2023). DOI: 10.48550/arXiv.2210.06280.
- Carlini, N., Tramer, F., Wallace, E., Jagielski, M., Herbert-Voss, A., Lee, K., Roberts, A., Brown, T., Song, D., Erlingsson, U., Oprea, A., Raffel, C., 2021. Extracting Training Data from Large Language Models. In: 30th USENIX Security Symposium (USENIX Security 21), pp. 2633-2650.
- Dinh, T., Zeng, Y., Zhang, R., Lin, Z., Gira, M., Rajput, S., Sohn, J., Papailiopoulos, D., Lee, K., 2022. LIFT: Language-Interfaced Fine-Tuning for Non-Language Machine Learning Tasks. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022), pp. 11763-11784. DOI: 10.52202/068431-0855.
- Fowlie, M., Greenstone, M., Wolfram, C., 2018. Do Energy Efficiency Investments Deliver? Evidence from the Weatherization Assistance Program. The Quarterly Journal of Economics 133 (3), 1597-1644. DOI: 10.1093/qje/qjy005.
- Grinsztajn, L., Oyallon, E., Varoquaux, G., 2022. Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022), pp. 507-520. DOI: 10.52202/068431-0037.
- Gulrajani, I., Lopez-Paz, D., 2021. In Search of Lost Domain Generalization. In: Ninth International Conference on Learning Representations (ICLR 2021). DOI: 10.48550/arXiv.2007.01434.
- Jung, W., 2026. BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research. arXiv:2609.02729. DOI: 10.48550/arXiv.2609.02729.
- Jutras-Dube, P., Al-Khasawneh, M.B., Yang, Z., Bas, J., Bastin, F., Cirillo, C., 2024. Copula-based transferable models for synthetic population generation. Transportation Research Part C: Emerging Technologies 169, 104830. DOI: 10.1016/j.trc.2024.104830.
- Koh, P.W., Sagawa, S., Marklund, H., Xie, S.M., Zhang, M., Balsubramani, A., Hu, W., Yasunaga, M., Phillips, R.L., Gao, I., Lee, T., David, E., Stavness, I., Guo, W., Earnshaw, B.A., Haque, I.S., Beery, S., Leskovec, J., Kundaje, A., Pierson, E., Levine, S., Finn, C., Liang, P., 2021. WILDS: A Benchmark of in-the-Wild Distribution Shifts. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139, pp. 5637-5664. DOI: 10.48550/arXiv.2012.07421.
- Lesnard, L., 2008. Off-Scheduling within Dual-Earner Couples: An Unequal and Negative Externality for Family Time. American Journal of Sociology 114 (2), 447-490. DOI: 10.1086/590648.
- Li, X., Huang, F., Lv, J., Xiao, Z., Li, G., Yue, Y., 2024. Be More Real: Travel Diary Generation Using LLM Agents and Individual Profiles. arXiv:2407.18932. DOI: 10.48550/arXiv.2407.18932.
- Martin-Olalla, J.M., 2018. Latitudinal trends in human primary activities: characterizing the winter day as a synchronizer. Scientific Reports 8, 5218. DOI: 10.1038/s41598-018-23546-5.
- McKenna, E., Thomson, M., 2016. High-resolution stochastic integrated thermal-electrical domestic demand model. Applied Energy 165, 445-461. DOI: 10.1016/j.apenergy.2015.12.089.
- Mireshghallah, F., Goyal, K., Uniyal, A., Berg-Kirkpatrick, T., 2022. Quantifying Privacy Risks of Masked Language Models Using Membership Inference Attacks. In: Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP 2022), pp. 8332-8347. DOI: 10.18653/v1/2022.emnlp-main.570.
- Nosek, B.A., Ebersole, C.R., DeHaven, A.C., Mellor, D.T., 2018. The preregistration revolution. Proceedings of the National Academy of Sciences 115 (11), 2600-2606. DOI: 10.1073/pnas.1708274114.
- Qian, X., Gangwal, U., Dong, S., Davidson, R., 2026. A deep generative framework for joint households and individuals population synthesis. Applied Soft Computing 188, 114375. DOI: 10.1016/j.asoc.2025.114375.
- Solatorio, A.V., Dupriez, O., 2023. REaLTabFormer: Generating Realistic Relational and Tabular Data using Transformers. arXiv:2302.02041. DOI: 10.48550/arXiv.2302.02041.
- Sun, L., Erath, A., 2015. A Bayesian network approach for population synthesis. Transportation Research Part C: Emerging Technologies 61, 49-62. DOI: 10.1016/j.trc.2015.10.010.
- Torriti, J., 2012. Price-based demand side management: Assessing the impacts of time-of-use tariffs on residential electricity demand and peak shifting in Northern Italy. Energy 44 (1), 576-583. DOI: 10.1016/j.energy.2012.05.043.
- Warde, A., Cheng, S.-L., Olsen, W., Southerton, D., 2007. Changes in the Practice of Eating: A Comparative Analysis of the United Kingdom and the Netherlands. Acta Sociologica 50 (4), 363-385. DOI: 10.1177/0001699307083978.
- Wilke, U., Haldi, F., Scartezzini, J.-L., Robinson, D., 2013. A bottom-up stochastic model to predict building occupants' time-dependent activities. Building and Environment 60, 254-264. DOI: 10.1016/j.buildenv.2012.10.021.
- Zhang, C., Ippolito, D., Lee, K., Jagielski, M., Tramer, F., Carlini, N., 2023. Counterfactual Memorization in Neural Language Models. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023), pp. 39321-39362. DOI: 10.52202/075280-1708.
- Zhao, Z., Birke, R., Chen, L.Y., 2025. TabuLa: Harnessing Language Models for Tabular Data Synthesis. In: Lecture Notes in Computer Science (ECML PKDD 2024), Springer, Cham, pp. 247-259. DOI: 10.1007/978-981-96-8186-0_20.

## 6. Positive and negative control results

### Positive control
- Query DOI: 10.18564/jasss.2768
- Crossref verification status: Confirmed.
- Retrieved record:
  - Title: Evaluating the Performance of Iterative Proportional Fitting for Spatial Microsimulation: New Tests for an Established Technique
  - Journal: Journal of Artificial Societies and Social Simulation
  - Year: 2015
  - First author: Robin Lovelace (co-authors: Mark Birkin, Dimitris Ballas, Eveline van Leeuwen)
  - Citation details: Vol. 18, Issue 2, Article 21.

### Negative control
- Query Title: "Cross-national transfer of time-use diaries with language models beats iterative proportional fitting"
- Crossref / DataCite / Semantic Scholar verification status: NOT FOUND.
- Result: As expected, no such publication or preprint exists in any scientific index.

## 7. What I could not find

- I could not find any published study that evaluates a fine-tuned or prompted large language model for cross-national transfer of daily activity schedules against a raked donor pool.
- I could not find any pre-registered research report in the building energy modeling literature that pre-specifies a quantitative decision rule comparing generative AI against survey calibration baselines.
- I could not find any study that directly couples transferred language model activity diaries to residential archetype energy simulations in EnergyPlus across multiple European countries.
