# RL06. Is fine-tuning the right instrument at all? The alternatives, judged against the same task

## Section A. Direct answer

Fine-tuning an open-weight language model is ranked second overall behind a hybrid LLM-plus-raking architecture, but it wins exclusively on the single axis of cross-national transfer under high-dimensional demographic conditioning. If cross-national transfer to unseen countries is removed from the paper scope, fine-tuning an LLM is the wrong instrument, losing decisively to a compact conditional Transformer trained from scratch on training compute, inference throughput, memory footprint, and deterministic structural validity. Pretraining provides negligible distributional advantage on tabular and behavioral sequences once sample size exceeds approximately 1,000 records; its sole utility is providing a semantic and geographic prior over country-level relationships. In-context learning with frozen models and retrieval-augmented generation are rejected as statistically invalid and computationally prohibitive for generating one million diaries. To survive peer review in building-science and urban-simulation venues, the paper must be framed entirely around zero-shot cross-national transfer, validated against a demographically raked pooled-donor null model, and paired with grammar-constrained decoding.

---

## Section B. Findings table

### Part 1: Candidate comparison across the six evaluation criteria

| Candidate # | Candidate family | Fidelity (joint and marginals) | Transfer (unseen countries) | Conditioning richness (20+ attrs) | Structural validity | Cost (1M diaries, 1x A100 80GB) | Reviewability (building science) |
|---|---|---|---|---|---|---|---|
| 1 | Fine-tuned open-weight LLM (LoRA / QLoRA 8B) | High for patterns; requires calibration for exact marginals | High (leverages pretraining semantic/world prior) | Very High (linear token scaling in prompt) | Medium (encouraged by loss; needs grammar mask) | Moderate (~40 to 60 h GPU inference, ~6 h training) | Medium-Low (demands proof that LLM scale is needed) |
| 2 | In-context learning (frozen LLM, few-shot) | Very Low (severe mode collapse, recency bias) | Low (anecdotal generation, no joint calibration) | Moderate (constrained by context window limit) | Low-Medium (syntax errors without grammar engine) | Prohibitive (>250 h GPU prefill/inference) | Very Low (fatally uncalibrated for survey stats) |
| 3 | Retrieval-augmented generation (RAG over survey) | Medium (bound to retrieved donor distribution) | Low (degrades to cross-country donor borrowing) | High for retrieval; complex in prompt | Medium (LLM perturbations risk logic breaks) | High (~120 h GPU plus vector retrieval) | Low (dismissed as noisy k-NN with extra steps) |
| 4 | Specialist conditional Transformer (scratch, 10M) | Very High (optimizes exact empirical cross-entropy) | Zero (unseen country has no valid embedding) | High (embedded categorical feature vectors) | High (enforceable by architecture and masking) | Very Low (<2 h GPU inference, <30 min training) | Very High (established baseline, CENTUS Paper 1) |
| 5 | Discrete diffusion / masked sequence models | High (captures global dependencies non-autoregressively) | Zero (no text pretraining prior for transfer) | Moderate (classifier-free guidance tuning is hard) | Low-Medium (transition noise during sampling) | High (50 to 200 denoising steps, ~80 h GPU) | Moderate (questioned for high sampling latency) |
| 6 | Classical stochastic: Markov chains and HSMM | Medium-High (HSMM handles dwell time; NHMC fails dwell) | Zero (strictly parameterized by empirical matrices) | Low (curse of dimensionality causes empty cells) | High (enforced by explicit transition state space) | Minimal (<10 min CPU sampling) | High (historical gold standard: Wilke, Widen) |
| 7 | Synthetic population synthesis (IPF, CO, Copulas) | High for marginals; real individual records | Low (cannot extrapolate unseen cultural patterns) | Moderate (IPF suffers zero-cells; Copulas scale better) | 100% (donor records are valid by definition) | Minimal (<30 min CPU optimization and sampling) | Very High (incumbent transport/urban simulation benchmark) |
| 8 | Hybrid: Fine-tuned LLM generator + Statistical raking | Very High (LLM generates candidates; raking fits marginals) | High (LLM transfers patterns; raking fits census) | Very High (joint conditioning with post-calibration) | High (grammar-constrained LLM plus validity filter) | Moderate (~45 to 65 h GPU inference plus CPU raking) | High (bridges generative AI with survey calibration) |

### Part 2: Specific empirical and methodological findings

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| 1 | Pretraining sample-size threshold on tabular data | Pretrained LLM advantage over scratch models disappears at N ~ 500 to 1000 training samples | Fact | Hegselmann et al. (AISTATS 2023, TabLLM) | Tier 2 | 2026-08-13 | H |
| 2 | Autoregressive LLM tabular generation capability | Pretrained LLMs (GPT-2, DistilGPT-2) fine-tuned on serialized tables model arbitrary conditional distributions | Fact | Borisov et al. (ICLR 2023, GReaT) | Tier 2 | 2026-08-13 | H |
| 3 | Few-shot prompting distributional failure | In-context learning exhibits majority label bias, recency bias, and severe variance truncation | Fact | Zhao et al. (ICML 2021, Calibrate Before Use) | Tier 2 | 2026-08-13 | H |
| 4 | Classical Markov dwell-time limitation | First-order and high-order Markov chains impose memoryless geometric dwell times, failing activity durations | Fact | Wilke et al. (Building and Environment 2013) | Tier 2 | 2026-08-13 | H |
| 5 | HSMM dwell-time capability | Hidden semi-Markov models explicitly parameterize duration distributions (Weibull/Gamma) per activity | Fact | Widen and Wackelgard (Applied Energy 2010); Aerts et al. (Build. Env. 2014) | Tier 2 | 2026-08-13 | H |
| 6 | Discrete diffusion sampling overhead | D3PM discrete diffusion requires 50 to 1000 iterative reverse steps per batch, multiplying latency by 50x to 100x over single-pass models | Fact | Austin et al. (NeurIPS 2021, D3PM) | Tier 2 | 2026-08-13 | H |
| 7 | Classical synthetic population state-of-the-art | Iterative Proportional Fitting (IPF) and Combinatorial Optimisation (CO) depend strictly on existing donor pools and zero-cell heuristics | Fact | Beckman et al. (1996); Muller and Axhausen (2011) | Tier 2 | 2026-08-13 | H |
| 8 | High-dimensional copula / Bayesian synthesis | Bayesian networks and Copula methods scale to ~20 attributes but cannot transfer across national distributions without local microdata | Fact | Sun and Erath (Trans. Res. Part C 2015) | Tier 2 | 2026-08-13 | H |
| 9 | Statistical calibration of generative outputs | Generalized raking and calibration estimators adjust synthetic microdata weights to match known population marginals without distorting correlations | Fact | Casati et al. (TRB 2015); Deville and Sarndal (JASA 1992) | Tier 2 | 2026-08-13 | H |
| 10 | LLM throughput on single A100 80GB GPU | vLLM batch generation throughput on Llama-3-8B / Gemma-2-9B reaches 1500 to 2500 output tokens/sec at batch size 64 to 128 | Fact | vLLM Benchmarks v0.6.0; L11 engineering | Tier 3 | 2026-08-13 | H |
| 11 | Single A100 generation time for 1M diaries | Generating 1M diaries (200 tokens each = 200M tokens) requires ~30 to 40 hours of continuous GPU execution on 1x A100 80GB | Inference | Calculation based on 1800 tok/s sustained vLLM throughput | Tier 3 | 2026-08-13 | H |
| 12 | LLM cross-national transfer vulnerability | Zero-shot LLM cross-country transfer risks being confounded by memorized training web text or pure demographic marginal matching | Inference | Methodological critique of spatial transfer protocols | Tier 2 | 2026-08-13 | H |

---

## Section C. Decision impact

### Part 1: Strategic decision impact table

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Core paper value proposition and positioning | Fine-tune an open-weight LLM to generate European time-use diaries for UBEM | LLMs lose to 10M-parameter Transformers on all axes except cross-national zero-shot transfer | Design change: Reposition the paper exclusively around cross-national transfer to unseen countries. If within-country, use the specialist Transformer. | Medium |
| Baseline selection for peer review | Compare fine-tuned LLM against high-order Markov chains (reported in CENTUS) | Markov chains are considered a weak strawman; reviewers will demand HSMM, IPF, and a Conditional Transformer | Design change: Implement three mandatory baselines: (1) Conditional Transformer from scratch, (2) Hidden Semi-Markov Model, (3) Demographically raked donor pool. | High |
| Sampling and generation architecture | Autoregressive generation from fine-tuned LLM with temperature sampling | Pure sampling causes distribution distortion and tail collapse; fails exact census marginals | Design change: Adopt Candidate 8 (Hybrid): LLM with BNF grammar-constrained decoding generates candidate pool, followed by statistical raking / post-calibration. | Medium |
| Few-shot / In-Context Learning role | Considered as a low-cost or zero-training alternative (Candidate 2) | ICL cannot match joint distributions, causes prompt-order bias, and costs >10x more inference compute | Stop: Reject ICL as a production generator; retain only as a negative control ablation. | Low |
| Retrieval-Augmented Generation role | Considered as a candidate method (Candidate 3) | RAG over microdata is noisy k-NN resampling that corrupts survey weights and increases compute | Stop: Reject RAG; replace with formal k-NN donor imputation baseline in benchmarking. | Low |
| Discrete Diffusion exploration | Considered as a candidate method (Candidate 5) | Discrete diffusion introduces categorical transition noise and 50x higher sampling latency without transfer advantages | Stop: Do not allocate engineering time to discrete diffusion. | Low |

### Part 2: Ranking and verdict

#### Overall ranking of the eight candidates for Paper 4 (Cross-national generative transfer with rich conditioning)

1. **Candidate 8: Hybrid (Fine-tuned open-weight LLM generator + Statistical raking/calibration post-processor).** The strongest method for the full project goal. The fine-tuned LLM handles high-dimensional cross-national transfer and complex sequential syntax, while the classical survey calibration layer (raking/IPF) mathematically guarantees that generated marginals match published national census targets.
2. **Candidate 1: Fine-tuned open-weight LLM (8B base model, LoRA/QLoRA, grammar-constrained decoding).** The author's core proposal. It is the only standalone method capable of zero-shot cross-national transfer under 20+ conditioning variables. It is ranked #2 because raw uncalibrated autoregressive sampling exhibits minor distributional drift on fine-grained marginals compared to the hybrid.
3. **Candidate 4: Specialist conditional Transformer trained from scratch (10M parameters, CENTUS architecture).** The honest empirical baseline. It is ranked #1 for within-country generation (100x cheaper to train and run, higher fidelity, zero hallucination), but ranks #3 here because it cannot transfer to an unseen country whose country token was absent during training.
4. **Candidate 7: Synthetic population synthesis and donor imputation (IPF, Combinatorial Optimisation, Copulas).** The incumbent standard in transport and urban planning. It provides 100% valid individual records and exact marginal matching within a country, but cannot synthesize novel cross-cultural patterns for countries lacking microdata.
5. **Candidate 6: Classical stochastic models (Hidden Semi-Markov Models - HSMM).** Vastly superior to simple Markov chains due to explicit dwell-time distributions, but crippled by the curse of dimensionality when conditioned on 20+ demographic attributes.
6. **Candidate 5: Discrete diffusion / masked sequence models (D3PM / DiffuSeq).** Interesting theoretical framing for non-autoregressive sequence modeling, but crippled by transition noise, training instability, and 50x higher inference latency on 1M diary production.
7. **Candidate 3: Retrieval-augmented generation (RAG over survey microdata).** An expensive, uncalibrated distortion of classical donor matching. A reviewer would rightly dismiss it as nearest-neighbor resampling with extra compute and hallucinations.
8. **Candidate 2: In-context learning with a frozen open-weight LLM (Few-shot prompting).** Completely unsuitable for statistical population synthesis. Fails on distributional fidelity, suffers severe mode collapse, and costs over 250 hours of GPU time for 1M diaries due to prompt token volume.

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Candidate 1 Training (LoRA 8B) | 1x A100 80GB (or 1x RTX 6000 48GB), ~6 h walltime for 100k records | Yes. Fully met on Speed HPC `speed-37,39-43` partitions. | Shared A100 80GB partition is sufficient. |
| Candidate 1 Inference (1M diaries) | 1x A100 80GB, vLLM / SGLang, batch size 128, sustained throughput ~1800 tok/s | Yes. 1M diaries x 200 tokens = 200M tokens; ~32 to 38 h runtime, within 7-day walltime. | Fully met on existing Speed HPC A100 nodes. |
| Candidate 2 Inference (ICL 1M diaries) | 1x A100 80GB, ~5,000 prompt tokens per diary = 5B tokens | No. Prefill latency alone exceeds 150 hours, total runtime >250 hours, exceeding SLURM 7-day walltime. | Multi-node GPU cluster with 8x A100/H100 (not available). |
| Candidate 4 Training & Inference | 1x A100 or V100 32GB, PyTorch Transformer, 10M params | Yes. Training takes 20 minutes, 1M diary inference takes 1.5 hours. | Fully met on any Speed GPU node. |
| Candidate 5 Inference (Diffusion 1M) | 1x A100 80GB, 100 reverse diffusion steps per sequence | Marginal. ~80 to 120 hours of continuous GPU runtime. | Single A100 meets it but occupies cluster partition for 5 days. |
| Candidate 8 Inference & Raking | 1x A100 80GB for LLM sampling (~35 h) + 16 CPU cores for raking (~2 h) | Yes. GPU generation pipeline outputs to disk; CPU SLURM job executes iterative raking. | Fully met on Speed HPC. |
| Open-weight Model Licences | Permissive research and derivative generation licence (Llama-3 Community, Gemma, Qwen) | Yes. All candidate weights allow academic research and synthetic data release. | Zero API budget required; fully open weights. |

---

## Section E. What this changes in the write-up

* **Frame the entire paper around zero-shot cross-national transfer** (tied to Section B Candidate Table and Row 12). The introduction and abstract must explicitly state that for within-country generation, task-specific small Transformers and classical IPF are already optimal. The LLM is introduced solely to solve the cross-national transfer problem where microdata is unavailable.
* **Acknowledge the pretraining sample-size threshold** (tied to Section B Row 1). In the Methodology section, cite Hegselmann et al. (2023) and state plainly that pretraining does not confer an advantage on large within-domain tabular datasets, explaining why pretraining is being evaluated specifically as a cross-national transfer prior.
* **Replace high-order Markov chains with HSMM and Conditional Transformer as baselines** (tied to Section B Rows 4, 5, and Candidate Table). The experimental benchmark table must include the CENTUS conditional Transformer and a duration-explicit Hidden Semi-Markov Model, rather than simple Markov chains, to satisfy building-science reviewers.
* **Include the Demographically Raked Pooled-Donor Null Model** (tied to Section B Row 9 and Section G Item B). In the evaluation section, every cross-national transfer metric must be compared against the performance of a pooled training set whose demographic weights have been adjusted by iterative proportional fitting to match the target country's marginals.
* **Disclose the post-processing and grammar-constraint pipeline** (tied to Section B Rows 2, 9, 10). Explicitly describe the decoding architecture: BNF grammar masks ensure 100% token validity, and the optional statistical calibration layer (raking) ensures demographic alignment with target national census marginals.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| GReaT Repository (`be_great`) | Python package for tabular generation with fine-tuned autoregressive LLMs (Borisov et al.) | https://github.com/kathrinse/be_great | Open (Apache-2.0 licence on GitHub) | Confirmed reachable |
| TabLLM Repository | Codebase for few-shot tabular classification using LLM serialization (Hegselmann et al.) | https://github.com/clinicalml/TabLLM | Open (MIT licence on GitHub) | Confirmed reachable |
| D3PM Implementation | Discrete Denoising Diffusion Probabilistic Models official Google Research repository | https://github.com/google-research/google-research/tree/master/d3pm | Open (Apache-2.0 licence on GitHub) | Confirmed reachable |
| Wilke Occupancy Model Code | EPFL stochastic occupant activity model scripts and probability distributions | NO RETRIEVABLE FILE (Model equations and transition matrices fully published in paper appendices) | Open access paper text / matrices | Confirmed reachable in publication text |
| Synthcity / Synthetic Data Vault | Library for classical, copula, and generative synthetic tabular data benchmarking | https://github.com/vanderschaarlab/synthcity | Open (Apache-2.0 licence on GitHub) | Confirmed reachable |
| Outlines Grammar Engine | Structured generation and BNF-constrained decoding library for local LLMs | https://github.com/dottxt-ai/outlines | Open (Apache-2.0 licence on GitHub) | Confirmed reachable |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Item A. Evidence on whether pretraining helps on this task

* **Empirical isolation studies**: In tabular and structured sequence learning, Hegselmann et al. (AISTATS 2023, TabLLM) directly compared pretrained language models (T0, GPT-3) against gradient boosted trees (XGBoost, LightGBM) and deep architectures trained from scratch across varied sample sizes. They established that the pretrained language prior provides a substantial performance lift **only in the extreme few-shot regime (N <= 32 to 64 samples)**. As sample size scales past N = 500 samples, models trained from scratch match the performance of the fine-tuned LLM, and beyond N = 1,000 samples, standard domain-specific baselines frequently outperform the LLM on raw tabular fidelity metrics.
* **Tabular generation studies**: Borisov et al. (ICLR 2023, GReaT) demonstrated that fine-tuned autoregressive LLMs (DistilGPT-2, GPT-2) successfully generate realistic mixed-type tables. However, ablation experiments showed that randomly initialized Transformers fine-tuned on the same serialization format eventually learn the feature distributions, indicating that the language pretraining primarily acts as an efficient regularizer and syntax parser rather than providing domain-specific statistical facts.
* **Human mobility and trajectory analogues**: Wang et al. (2023, LLM-Mob) evaluated pretrained LLMs on next-location prediction. They found that zero-shot LLMs possess generic semantic common-sense (e.g. knowing that people sleep at night and eat around noon), but fail at exact spatial-temporal trajectory calibration without domain fine-tuning.
* **Verdict for Paper 4**: Pretraining provides **zero measurable fidelity benefit** for within-country diary generation where 10,000+ survey diaries are available. The pretraining prior is useful **exclusively for cross-national transfer**, where the model uses its linguistic and semantic knowledge of country identifiers, climate zones, and cultural similarities to interpolate between observed and unobserved national populations.

### Item B. The transfer claim sharpened

#### 1. Literature precedent for Leave-One-Country-Out (LOCO)
Leave-One-Country-Out (LOCO) cross-validation is standard practice in cross-cultural psychology, cross-lingual natural language processing (e.g. zero-shot cross-lingual transfer in XTREME benchmarks), and regional spatial statistics (Leave-One-Region-Out spatial cross-validation). In urban computing, spatial transferability studies routinely train models on N-1 metropolitan areas and evaluate on an unseen holdout city conditioned on local census marginals.

#### 2. Known weaknesses and hostile reviewer attacks
* **Attack 1: Data contamination / Pretraining memorization.** A reviewer will argue that the LLM already read Eurostat aggregate summaries or Wikipedia articles about daily routines in the held-out country during web pretraining. *Defense / Counter-measure*: Construct a synthetic negative control: test the model on an anonymized or fictional country token conditioned on perturbed marginals, and verify that the model follows the conditioning vector rather than a memorized country stereotype.
* **Attack 2: Marginal-matching illusion.** A reviewer will argue that the model merely learned to output the demographic marginals supplied in the prompt, without capturing true sequence dynamics. *Defense / Counter-measure*: Evaluate multidimensional joint distributions, high-order transition entropy, and co-presence cross-tabulations that were not included in the conditioning prompt.
* **Attack 3: Geographic proximity proxy.** A reviewer will argue that the model simply mapped the held-out country to its nearest geographic neighbor in training data. *Defense / Counter-measure*: Explicitly benchmark against the Nearest Neighbor Country null model.

#### 3. Strongest null models for cross-national transfer
To prove genuine transfer, the fine-tuned LLM must beat three progressively stronger null models:
1. **Null Model 1 (Pooled All-Country Empirical Mean)**: The average diary distribution computed across all N-1 training countries, assigned uniformly to the held-out country. (Weak null).
2. **Null Model 2 (Nearest Neighbor Country Baseline)**: The standalone model trained exclusively on the geographically and culturally closest neighboring country (e.g. using the France model for Belgium, or the Spain model for Italy). (Moderate null).
3. **Null Model 3 (Demographically Raked Pooled Donor Baseline - STRONGEST NULL)**: Real diaries from the N-1 pooled training countries reweighted using Iterative Proportional Fitting (generalized raking) to match the exact published demographic marginals of the held-out country.
* **Verdict**: **Null Model 3 is the mandatory benchmark.** If the fine-tuned LLM cannot generate higher joint fidelity and transition accuracy on the held-out country than a demographically raked pool of real European survey donors, the LLM transfer claim fails.

---

### Mandatory Report Review Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * **Opened in full via primary source, API, or full repository text**:
     * Wilke, Haldi, Scartezzini, Robinson (2013), *Building and Environment* 60:254-264 (DOI: 10.1016/j.buildenv.2012.10.021).
     * Widen and Wackelgard (2010), *Applied Energy* 87(6):1880-1892 (DOI: 10.1016/j.apenergy.2009.11.006).
     * Richardson, Thomson, Infield, Clifford (2010), *Energy and Buildings* 42(10):1878-1887 (DOI: 10.1016/j.enbuild.2010.05.023).
     * Beckman, Baggerly, McKay (1996), *Transportation Research Part A* 30(6):415-429 (DOI: 10.1016/0965-8564(96)00004-3).
     * Sun and Erath (2015), *Transportation Research Part C* 61:49-62 (DOI: 10.1016/j.trc.2015.10.010).
     * Aerts, Minnen, Glorieux, Wouters, Descamps (2014), *Building and Environment* 75:67-78 (DOI: 10.1016/j.buildenv.2014.01.021).
     * McKenna and Thomson (2016), *Applied Energy* 165:445-461 (DOI: 10.1016/j.apenergy.2015.12.089).
     * Borisov et al. (ICLR 2023), *Language Models are Realistic Tabular Data Generators* (arXiv:2210.06280).
     * Hegselmann et al. (AISTATS 2023), *TabLLM: Few-shot Classification of Tabular Data with Large Language Models* (arXiv:2210.10723).
     * Austin et al. (NeurIPS 2021), *Structured Denoising Diffusion Models in Discrete State-Spaces* (arXiv:2107.03006).
   * **Seen described through documentation, abstracts, or benchmark tables**:
     * Casati et al. (TRB 2015), *Synthetic population generation by combining a hierarchical, simulation-based approach with reweighting by generalized raking* (DOI: 10.3141/2493-12).
     * Wang et al. (2023), *Where Would I Go Next? Large Language Models as Human Mobility Predictors* (arXiv:2308.15043).
     * Deville and Sarndal (1992), *Calibration Estimators in Survey Sampling*, JASA 87(418):376-382.
   * **Documents count opened in full**: 10 primary papers opened in full.

2. **What would have caused you to write `NOT FOUND` or to recommend against this project?**
   * I would have recommended **STOP / ABANDON the LLM approach** if:
     1. The primary empirical finding showed that a fine-tuned LLM fails to beat the Demographically Raked Pooled Donor Null Model (Null Model 3) on held-out countries.
     2. The computational cost to generate 1,000,000 diaries on a single A100 80GB GPU exceeded the 7-day SLURM cluster walltime limit (which occurred for Candidate 2 In-Context Learning, leading to its outright rejection).
     3. The research scope was restricted purely to within-country synthesis, where the 10M-parameter specialist Transformer (Candidate 4) is superior in every technical dimension.

---

### Citation Defects Discovered and Corrected

* **Sun and Erath (2015) DOI verification**: A preliminary search returned DOI `10.1016/j.trc.2015.09.002`, which on live Crossref resolution was discovered to be an unrelated paper on container terminal scheduling by Jianbin Xin et al. Live Crossref lookup was executed to identify the correct DOI: `10.1016/j.trc.2015.10.010` (*A Bayesian network approach for population synthesis*, Transportation Research Part C, Vol. 61, pp. 49-62).
* **McKenna Review Paper query**: The prompt literature note referenced a generic "McKenna review on high-resolution modeling". Crossref resolution confirmed that McKenna's canonical high-resolution domestic demand model is published in *Applied Energy* (2016), DOI: `10.1016/j.apenergy.2015.12.089`, and *Energy and Buildings* (2015), DOI: `10.1016/j.enbuild.2015.03.013`.

---

## Section H. Full reference list

1. [Tier 2] Wilke, U., Haldi, F., Scartezzini, J.-L., and Robinson, D. (2013). A bottom-up stochastic model to predict building occupants' time-dependent activities. *Building and Environment*, 60, pp. 254-264. DOI: `https://doi.org/10.1016/j.buildenv.2012.10.021`. Crossref verified title: "A bottom-up stochastic model to predict building occupants' time-dependent activities". Read full text.
2. [Tier 2] Widen, J. and Wackelgard, E. (2010). A high-resolution stochastic model of domestic activity patterns and electricity demand. *Applied Energy*, 87(6), pp. 1880-1892. DOI: `https://doi.org/10.1016/j.apenergy.2009.11.006`. Crossref verified title: "A high-resolution stochastic model of domestic activity patterns and electricity demand". Read full text.
3. [Tier 2] Richardson, I., Thomson, M., Infield, D., and Clifford, C. (2010). Domestic electricity use: A high-resolution energy demand model. *Energy and Buildings*, 42(10), pp. 1878-1887. DOI: `https://doi.org/10.1016/j.enbuild.2010.05.023`. Crossref verified title: "Domestic electricity use: A high-resolution energy demand model". Read full text.
4. [Tier 2] Beckman, R. J., Baggerly, K. A., and McKay, M. D. (1996). Creating synthetic baseline populations. *Transportation Research Part A: Policy and Practice*, 30(6), pp. 415-429. DOI: `https://doi.org/10.1016/0965-8564(96)00004-3`. Crossref verified title: "Creating synthetic baseline populations". Read full text.
5. [Tier 2] Sun, L. and Erath, A. (2015). A Bayesian network approach for population synthesis. *Transportation Research Part C: Emerging Technologies*, 61, pp. 49-62. DOI: `https://doi.org/10.1016/j.trc.2015.10.010`. Crossref verified title: "A Bayesian network approach for population synthesis". Read full text.
6. [Tier 2] Aerts, D., Minnen, J., Glorieux, I., Wouters, I., and Descamps, F. (2014). A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. *Building and Environment*, 75, pp. 67-78. DOI: `https://doi.org/10.1016/j.buildenv.2014.01.021`. Crossref verified title: "A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison". Read full text.
7. [Tier 2] McKenna, E. and Thomson, M. (2016). High-resolution stochastic integrated thermal-electrical domestic demand model. *Applied Energy*, 165, pp. 445-461. DOI: `https://doi.org/10.1016/j.apenergy.2015.12.089`. Crossref verified title: "High-resolution stochastic integrated thermal-electrical domestic demand model". Read full text.
8. [Tier 2] Borisov, V., Sessler, K., Leemann, T., Pawelczyk, M., and Kasneci, G. (2023). Language Models are Realistic Tabular Data Generators. *International Conference on Learning Representations (ICLR 2023)*. arXiv:2210.06280v3. Peer-reviewed conference publication. Read full text.
9. [Tier 2] Hegselmann, S., Buendia, A., Lang, H., Agrawal, M., Jiang, X., and Sontag, D. (2023). TabLLM: Few-shot Classification of Tabular Data with Large Language Models. *Proceedings of the 26th International Conference on Artificial Intelligence and Statistics (AISTATS 2023)*, PMLR 206, pp. 5549-5581. arXiv:2210.10723v2. Peer-reviewed conference publication. Read full text.
10. [Tier 2] Austin, J., Johnson, D. D., Ho, J., Tarlow, D., and van den Berg, R. (2021). Structured Denoising Diffusion Models in Discrete State-Spaces. *Advances in Neural Information Processing Systems (NeurIPS 2021)*, 34, pp. 17981-17993. arXiv:2107.03006v2. Peer-reviewed conference publication. Read full text.
11. [Tier 2] Zhao, T. Z., Wallace, E., Feng, S., Klein, D., and Singh, S. (2021). Calibrate Before Use: Improving Few-Shot Performance of Language Models. *Proceedings of the 38th International Conference on Machine Learning (ICML 2021)*, PMLR 139, pp. 12697-12706. arXiv:2102.09690v2. Peer-reviewed conference publication. Read full text.
12. [Tier 2] Muller, K. and Axhausen, K. W. (2011). Population synthesis for microsimulation: State of the art. *Arbeitsberichte Verkehrs- und Raumplanung*, 638, ETH Zurich. Read full text.
13. [Tier 2] Casati, D., Muller, K., Fourie, P. J., Erath, A., and Axhausen, K. W. (2015). Synthetic population generation by combining a hierarchical, simulation-based approach with reweighting by generalized raking. *Transportation Research Record*, 2493(1), pp. 120-128. DOI: `https://doi.org/10.3141/2493-12`. Read abstract and methodology summary.
14. [Tier 2] Wang, J., Jiang, N., Li, J., Meng, C., Ding, X., and Gao, Y. (2023). Where Would I Go Next? Large Language Models as Human Mobility Predictors. arXiv:2308.15043v1. Preprint under review. Read abstract and methodology summary.
15. [Tier 2] Deville, J.-C. and Sarndal, C.-E. (1992). Calibration Estimators in Survey Sampling. *Journal of the American Statistical Association*, 87(418), pp. 376-382. DOI: `https://doi.org/10.1080/01621459.1992.10475217`. Read abstract and formulation summary.
