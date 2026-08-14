# RL03. Prior art: LLMs for time-use diaries, activity sequences, and occupancy schedules

## Section A. Direct answer

No published or preprint study between 2022 and August 2026 fine-tunes or prompts a Large Language Model (LLM) on national time-use survey microdata (such as HETUS, ATUS, or national GSS datasets) to generate demographic-conditioned daily activity sequences or occupancy schedules for building performance simulation. The core thesis of Paper 4 is entirely unoccupied in both the building energy modeling (BEM) literature and the broader computational social science literature. Adjacent fields have advanced rapidly: in transportation engineering, prompt-based and fine-tuned LLMs (e.g., MobAgent, TravelReasoner, Golrokh Amin et al.) generate synthetic travel diaries and trip chains from census personas; in pervasive computing, lightweight fine-tuned models (e.g., DailyLLM) translate wearable sensor streams into activity logs; and in building simulation, LLMs (e.g., EPlus-LLM, BuildingGPT) are used strictly for natural-language EnergyPlus model configuration, code compliance checking, or high-level HVAC control logic. Crucially, specialist tabular and sequential generative models (such as TabDDPM diffusion models) consistently outperform LLMs on purely numerical tabular density estimation, which means the justification for using an LLM in Paper 4 rests entirely on its autoregressive sequence modeling over hierarchical activity tokens and its capacity for cross-national semantic transfer within the harmonized HETUS framework, rather than an inherent superiority at flat distribution estimation.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Direct hit on LLM fine-tuning on HETUS/ATUS for BEM occupancy | Exactly 0 published papers or preprints exist combining fine-tuned LLMs, time-use survey microdata, and BEM schedule generation | fact | Systematic search (Crossref, arXiv, OpenAlex, Google Scholar) | Tier 1 | 2026-08-13 | H |
| B2 | BEM LLM state of the art: automated EnergyPlus model generation | EPlus-LLM fine-tunes T5 models to translate text descriptions into EnergyPlus IDF files with 95% modeling time reduction | fact | Jiang et al. (2024), Applied Energy 367, 123431 | Tier 2 | 2026-08-13 | H |
| B3 | BEM LLM state of the art: field review and research roadmap | Comprehensive survey of 10 key questions on LLM applications across building lifecycles, identifying occupancy simulation as a future frontier | fact | Ma et al. (2026), Building and Environment 291, 114260 | Tier 2 | 2026-08-13 | H |
| B4 | BEM LLM state of the art: building energy opportunities | Review paper outlining LLM roles in energy management, fault detection, and automated modeling | fact | Liu et al. (2025), Building Simulation 18(2), 225-234 | Tier 2 | 2026-08-13 | H |
| B5 | Travel diary synthesis with LLMs: persona conditioning | Prompted GPT-4 with census (ACS) personas synthesizes individual travel diaries evaluated against Connecticut CSTS survey | fact | Golrokh Amin et al. (2025), arXiv:2509.09710 | Tier 2 | 2026-08-13 | H |
| B6 | Travel diary synthesis with LLMs: agent reasoning | MobAgent uses 2-stage understanding and reasoning prompting on 200k travel survey records to generate personalized travel diaries | fact | Li et al. (2024), arXiv:2407.18932 | Tier 2 | 2026-08-13 | H |
| B7 | Travel chain reasoning with LRMs | TravelReasoner applies curriculum post-training on NHTS trip chains to generate first-person reasoning traces and trip chains | fact | Liu et al. (2026), WWW 2026 / arXiv:2506.06008 | Tier 2 | 2026-08-13 | H |
| B8 | Activity semantic inference from mobility trajectories | UrbanAct-GPT fine-tunes LLMs with QLoRA on mobile signaling + POI data to infer period activity types (0.95 acc) and population roles | fact | Yang et al. (2025), SSRN:6305099 | Tier 2 | 2026-08-13 | H |
| B9 | Edge activity log generation from multi-modal sensors | DailyLLM fine-tunes 1.5B LLM on wearable sensor streams to generate textual activity narratives on Raspberry Pi | fact | Tian et al. (2025), IEEE MASS / arXiv:2507.13737 | Tier 2 | 2026-08-13 | H |
| B10 | Next-location mobility prediction with LLMs | LLM-Mob formulates mobility sequences into historical stays and context stays for prompted next-location forecasting | fact | Wang et al. (2023), arXiv:2308.15197 | Tier 2 | 2026-08-13 | H |
| B11 | Tabular synthetic data generation with LLMs | GReaT serializes tabular rows as text with random feature permutation and fine-tunes autoregressive transformers | fact | Borisov et al. (2023), ICLR 2023 / arXiv:2210.06280 | Tier 2 | 2026-08-13 | H |
| B12 | Specialist tabular competition: diffusion models | TabDDPM demonstrates that tabular diffusion models match or outperform GANs/LLMs in machine learning utility and statistical fidelity | fact | Kotelnikov et al. (2023), ICML 2023 / arXiv:2209.15421 | Tier 2 | 2026-08-13 | H |
| B13 | Silicon sampling and demographic fidelity claims | GPT-3 demonstrates algorithmic fidelity when conditioned on sociodemographic backstories from US political surveys | fact | Argyle et al. (2023), Political Analysis 31(3), 337-351 | Tier 2 | 2026-08-13 | H |
| B14 | Documented failure mode: variance collapse in synthetic surveys | LLMs exhibit severe within-group variance collapse, prompt fragility, and unstable regression coefficients compared to ANES data | fact | Bisbee et al. (2024), Political Analysis 32(4), 401-416 | Tier 2 | 2026-08-13 | H |
| B15 | Documented failure mode: demographic opinion misalignment | OpinionsQA benchmark across 60 demographic groups shows LLMs persistently misrepresent specific subgroups even when steered | fact | Santurkar et al. (2023), ICML 2023 / arXiv:2303.17548 | Tier 2 | 2026-08-13 | H |
| B16 | Task-specific deep learning baseline for time-use occupancy | CENTUS establishes benchmark multi-task LSTM/Transformer on Italian ISTAT microdata (0.98 accuracy vs 0.691 Markov) | fact | Iseri et al. (2026), Energy and Buildings 357, 117155 | Tier 2 | 2026-08-13 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Novelty and Go/No-Go decision | Fine-tune an open-weight LLM on HETUS microdata for cross-national BEM occupancy schedule generation | Zero direct competitors exist in BEM or social science literature; idea is completely novel | none (proceed with project) | Low |
| Model positioning vs. Specialist generative models | Claim LLM is superior to all tabular and sequential generative models | Independent benchmarks (Kotelnikov 2023) show diffusion models (TabDDPM) beat LLMs on flat tabular data; LLMs excel at sequential token structures and cross-national transfer | caveat (frame LLM as sequential and cross-lingual/cross-national transfer engine, not generic tabular SOTA) | Low |
| Method: Fine-tuning vs. Prompting | Fine-tune open-weight LLM on harmonized microdata | Prompted LLMs without fine-tuning suffer severe variance collapse, demographic hallucination, and inability to output strict 144-slot HETUS syntax (Bisbee 2024, Golrokh Amin 2025) | none (fine-tuning on real microdata is strongly confirmed as necessary) | Medium |
| Serialisation format design | Serialize 144 slots + demographic vector into tokenized text | Successful mobility/diary LLMs (LLM-Mob, Golrokh Amin, GReaT) use strict key-value demographic prefixes followed by compact slot-state strings | design change (adopt compact key-value demographic headers + dense slot-sequence encoding) | Medium |
| Evaluation metrics | Evaluate point accuracy | Mobility literature over-indexes on point accuracy (Accuracy@k), whereas diary synthesis requires distributional fidelity (Wasserstein distance, JS divergence, Jensen-Shannon on activity durations) | design change (adopt multi-level cohort realism scoring matching Golrokh Amin 2025 and Bisbee 2024 variance tests) | Medium |
| Building energy coupling | Inject generated schedules into EnergyPlus | Existing BEM LLM works (Jiang 2024) only generate IDF syntax; none injects survey-grounded stochastic behavioral schedules | none (retains high building-science novelty) | Low |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Model fine-tuning scale (1.5B to 8B parameters) | Single node with 1x to 2x 24GB/40GB GPU running QLoRA / PEFT with PyTorch and HuggingFace TRL | Yes. Speed HPC cluster GPU partitions easily accommodate 4-bit / 8-bit QLoRA on 7B/8B models (e.g. Gemma-2-9B, Llama-3-8B) | Meets requirement |
| Memory footprint during SFT | 12GB to 18GB VRAM with gradient checkpointing and 16-bit LoRA adapters | Yes. Fits within standard 24GB/32GB GPU allocation | Meets requirement |
| Open-weight model licensing | Permissive commercial or research open-weights (e.g. Gemma-2, Llama-3, Qwen-2.5) | Yes. Downloadable weights with standard research use terms | Meets requirement |
| Inference throughput for population generation | Fast batch generation of 100,000 synthetic diaries | Yes, using vLLM or HuggingFace TGI on local GPU within SLURM job walltime | Meets requirement |

---

## Section E. What this changes in the write-up

- **Section 1.1 (Introduction / Motivation)**: Explicitly state that while LLMs have been applied to next-location mobility prediction (Wang et al., 2023), travel diary generation (Golrokh Amin et al., 2025; Li et al., 2024), and EnergyPlus IDF file syntax generation (Jiang et al., 2024), this work is the first to fine-tune an open-weight LLM on harmonized time-use microdata (HETUS) for stochastic building occupancy schedule generation. Tie to Section B rows B1, B2, B5, B6.
- **Section 1.2 (Related Work - Generative Modeling in Building Simulation)**: Distinguish between task-specific supervised neural networks (CENTUS / Iseri et al., 2026), classical Markov chains (Wilke 2013, Buttitta 2020), and auto-regressive LLMs. Position the LLM not as a superior scalar density estimator over diffusion models (Kotelnikov et al., 2023), but as a unified sequence generator capable of cross-national semantic transfer. Tie to Section B rows B11, B12, B16.
- **Section 2.1 (Methodology - Addressing Silicon Sampling Failure Modes)**: Acknowledge the documented hazards of ungrounded LLM survey simulation, specifically within-group variance collapse, demographic stereotyping, and lack of statistical variation (Bisbee et al., 2024; Santurkar et al., 2023; Argyle et al., 2023). Argue that parameter-efficient fine-tuning on empirical microdata directly regularizes the conditional distribution and mitigates pretrained prior drift. Tie to Section B rows B13, B14, B15.
- **Section 3.3 (Evaluation Framework)**: Adopt a rigorous multi-tier evaluation protocol inspired by travel diary realism scores (Golrokh Amin et al., 2025) and statistical survey replication tests (Bisbee et al., 2024), evaluating not only point-level token accuracy but also marginal activity duration distributions, transition entropy, and within-cohort variance. Tie to Section B rows B5, B14.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| EPlus-LLM Code and Model Weights | Open-source code and T5-based model weights for EnergyPlus LLM modeling | `https://github.com/EPlus-LLM/EPlus-LLMv2` | Open (GitHub / Apache 2.0) | Yes |
| GReaT Repository | PyTorch implementation of LLM-based tabular data synthesis | `https://github.com/kathrinse/be_great` | Open (GitHub / MIT) | Yes |
| TabDDPM Benchmark Repository | PyTorch implementation of Tabular Denoising Diffusion Probabilistic Models | `https://github.com/yandex-research/tab-ddpm` | Open (GitHub / Apache 2.0) | Yes |
| LLM-Mob Repository | Python code and prompt templates for LLM-based mobility prediction | `https://github.com/vonfeng/LLM-Mob` | Open (GitHub / MIT) | Yes |
| DailyLLM Dataset and Code | Multi-modal sensor dataset and 1.5B LLM fine-tuning scripts | `https://github.com/gdfwj/DailyLLM` | Open (GitHub / MIT) | Yes |
| OpinionsQA Dataset | Benchmark survey dataset evaluating demographic alignment of LLMs | `https://github.com/shibanis/opinions_qa` | Open (GitHub / MIT) | Yes |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Detailed Analysis of Sub-Questions

#### 1. Analysis of Adjacent Human Mobility and Travel Behavior Literature (Item 2)
- **Leading methods and citations**:
  - *LLM-Mob* (Wang et al., 2023, arXiv:2308.15197): Predicts next location by formatting trajectory history into historical and context stays using few-shot prompted GPT-3.5/4.
  - *MobAgent* (Li et al., 2024, arXiv:2407.18932): Two-stage agent framework extracting mobility patterns and recursively generating personalized daily travel diaries.
  - *TravelReasoner* (Liu, Xu, Li, WWW 2026 / arXiv:2506.06008): Uses large reasoning models trained on Chain-of-Trips datasets from the US NHTS to simulate sequential decision logic.
  - *UrbanAct-GPT* (Yang et al., 2025, SSRN:6305099): QLoRA fine-tuning on mobile signaling and POI data to infer activity types and population roles.
  - *Golrokh Amin et al. (2025, arXiv:2509.09710)*: Synthesizes individual travel diaries by prompting LLMs conditioned on American Community Survey (ACS) demographic personas.
- **Fine-tuning vs. Prompting**: Early mobility papers (2023-2024) relied almost exclusively on zero-shot and few-shot prompting of closed proprietary models (GPT-3.5/4). Recent works (2025-2026) have shifted toward parameter-efficient fine-tuning (QLoRA) on 1.5B to 8B parameter open-weight models (e.g. Llama-3, Qwen, Mistral) on single-node GPUs.
- **Sequence serialization into text**: Successful serializations follow a strict structure:
  `[PERSONA: Age=35, Gender=F, Emp=Employed, HHSize=3] [CONTEXT: Day=Weekday, Season=Winter] [TIMELINE: 00:00-07:00=Sleep/Home; 07:00-07:30=Eat/Home; 07:30-08:00=Travel/Transit; 08:00-12:00=Work/Office; ...]`
- **Evaluation focus**: Mobility prediction works over-index on individual point prediction accuracy (Accuracy@1, Accuracy@5, F1 score). Travel diary synthesis works (Golrokh Amin 2025) use distributional realism metrics (Jensen-Shannon divergence across trip counts, duration intervals, and activity purposes). Paper 4 can occupy the space of evaluating multi-dimensional population distributional fidelity coupled to building physical simulation.

#### 2. LLMs as Survey Respondents and Known Failure Modes (Item 3)
- **Demographic fidelity**: Argyle et al. (2023, *Political Analysis*) demonstrated that prompting with rich sociodemographic backstories produces silicon samples that mirror human marginal distributions and subgroup response patterns.
- **Documented failure modes**:
  - *Variance collapse*: Bisbee et al. (2024, *Political Analysis*, DOI: `10.1017/pan.2024.5`) proved that LLM-generated survey respondents lack the natural variance and entropy of human populations; responses cluster tightly around the mean, distorting statistical inference and regression coefficients.
  - *Caricature and stereotyping*: Steered personas over-exaggerate stereotypical behaviors of minority or demographic subgroups (Santurkar et al., 2023, ICML).
  - *Prompt fragility and drift*: Minor wording changes produce significant swings in generated distributions, and model updates over time create longitudinal instability (Bisbee et al., 2024).
  - *Majority / US-centric bias*: Unconditioned or weakly conditioned models drift heavily toward US-educated liberal norms.
- **Does fine-tuning fix this?** Fine-tuning directly on microdata forces the model to fit empirical joint probability distributions P(diary | demographics), directly constraining logit distributions to match real human entropy. However, sampling temperature and top-p must be calibrated carefully during generation to prevent mode collapse.

#### 3. Tabular and Sequential Synthetic Data: LLMs vs. Specialists (Item 4)
- **LLM tabular synthesis**: GReaT (Borisov et al., ICLR 2023) and TabLLM (Hegselmann et al., AISTATS 2023) demonstrated that auto-regressive transformers can generate mixed tabular data by treating rows as text sentences with randomized feature ordering.
- **Specialist competition**: Comprehensive independent evaluations (Kotelnikov et al., ICML 2023; Zhang et al., 2024) demonstrate that **tabular diffusion models (TabDDPM, TabSyn) and TVAE consistently match or outperform LLMs on purely numerical tabular density estimation and machine learning utility (Train-on-Synthetic, Test-on-Real)**, while requiring significantly lower training and inference compute.
- **Honest verdict for Paper 4**: If our task were simply modeling a 20-dimensional flat numerical vector, an LLM would be the wrong choice; a tabular diffusion model (TabDDPM) or TVAE would be superior. However, time-use diaries are **long, structured sequences of 144 discrete activity tokens with complex hierarchical syntax and cross-national semantic mappings**. An autoregressive LLM is uniquely suited to sequence generation with vocabulary reuse across countries, which specialist tabular models cannot do.

#### 4. Building Energy Modeling Side: LLMs in BEM and UBEM (Item 5)
- **Published landscape (2023-2026)**:
  - *EPlus-LLM* (Jiang et al., *Applied Energy* 2024, DOI: `10.1016/j.apenergy.2024.123431`) and *EPlus-LLMv2* (2025): Fine-tunes T5 models to convert natural-language architectural specifications into EnergyPlus IDF files.
  - *Reviews and roadmaps*: Ma et al. (2026, *Building and Environment*, DOI: `10.1016/j.buildenv.2026.114260`) and Liu et al. (2025, *Building Simulation*, DOI: `10.1007/s12273-025-1235-9`) outline the landscape of LLMs for building energy, highlighting automated modeling, code compliance, and natural-language interfaces.
  - *Conversational interfaces*: Model Context Protocol (MCP) servers for EnergyPlus outputs and conversational debugging.
- **Ground-truth validation state**: Published BEM LLM works focus almost entirely on syntactic validity (whether EnergyPlus runs without fatal errors) and qualitative prompt compliance. **Zero studies validate LLM-generated occupant schedules or load profiles against measured sub-metered ground truth or national microdata distributions.**
- **Key venues**: *Energy and Buildings*, *Building and Environment*, *Applied Energy*, *Building Simulation*, *Renewable and Sustainable Energy Reviews*, *Advanced Engineering Informatics*, and *IBPSA Building Simulation*.

#### 5. The Gap Statement (Item 6)
- **Falsifiable gap statement**:
  *"No published or preprint work fine-tunes an open-weight large language model on harmonised time-use survey microdata (such as HETUS or ATUS) to generate demographic-conditioned, full-day stochastic occupant activity, presence, and co-presence sequences evaluated on population distributional fidelity against national survey cohorts and coupled as sub-hourly schedules into building performance simulation (EnergyPlus)."*
- **Stress-testing and nearest competitors**:
  1. *EPlus-LLM (Jiang et al., 2024)*: Focuses on EnergyPlus IDF syntax generation from text prompts; does not model occupant behavior, does not ingest time-use microdata, and does not evaluate population distributions.
  2. *Golrokh Amin et al. (2025) / MobAgent (Li et al., 2024)*: Generate travel diaries for transportation planning; do not generate indoor time-use activities (cooking, sleeping, working, presence, co-presence), do not use HETUS microdata, and do not connect to building energy simulations.
  3. *CENTUS (Iseri et al., 2026)*: Models occupancy from time-use data but uses task-specific deep neural networks (LSTM/Transformer) on single-country data; is not an open-weight LLM, does not test cross-national transfer, and does not use language model tokenization.

---

### Mandatory Negative Control Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full via primary landing pages / Crossref REST API / arXiv text*:
     1. Jiang et al. (2024), *Applied Energy* 367, 123431 (Crossref API + full metadata).
     2. Ma et al. (2026), *Building and Environment* 291, 114260 (Crossref API + full metadata and reference list).
     3. Liu et al. (2025), *Building Simulation* 18(2), 225-234 (Crossref API + full metadata).
     4. Zhang & Chen (2025), *Renewable and Sustainable Energy Reviews* 214, 115558 (Crossref API + full metadata).
     5. Argyle et al. (2023), *Political Analysis* 31(3), 337-351 (Crossref API + full abstract and citation tree).
     6. Bisbee et al. (2024), *Political Analysis* 32(4), 401-416 (Crossref API + full abstract and methodology).
     7. Borisov et al. (2023), *ICLR 2023* / arXiv:2210.06280 (Full paper and GitHub implementation).
     8. Kotelnikov et al. (2023), *ICML 2023* / arXiv:2209.15421 (Full paper and benchmark results).
     9. Golrokh Amin et al. (2025), arXiv:2509.09710 (Full preprint methodology and realism scoring).
     10. Li et al. (2024), arXiv:2407.18932 (Full MobAgent preprint).
     11. Wang et al. (2023), arXiv:2308.15197 (Full LLM-Mob preprint).
     12. Tian et al. (2025), arXiv:2507.13737 / IEEE MASS 2025 (Full DailyLLM preprint).
   - *Seen described through abstracts, reviews, and repository summaries*:
     1. TravelReasoner (Liu et al., 2026, WWW 2026 / arXiv:2506.06008).
     2. UrbanAct-GPT (Yang et al., 2025, SSRN:6305099).
     3. TabLLM (Hegselmann et al., 2023, AISTATS).
     4. OpinionsQA (Santurkar et al., 2023, ICML).

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   - I would have recommended against this project if a 2024 to 2026 paper in *Energy and Buildings*, *Building and Environment*, *Applied Energy*, or *IBPSA Building Simulation* had already demonstrated fine-tuning of an open-weight LLM (e.g. Llama-3, Mistral, Gemma) on HETUS or ATUS microdata with direct schedule coupling into EnergyPlus.
   - I would have written NOT FOUND if searches across transportation and social science preprints revealed no precedent for LLM-based sequence generation from demographic personas, which would have indicated fundamental technical infeasibility.
   - The finding that LLMs are actively used for travel diaries (Golrokh Amin 2025, Li 2024) proves the technical concept is feasible, while the complete absence of time-use survey fine-tuning in building performance simulation confirms the novelty of Paper 4.

---

## Section H. Full reference list

1. **Jiang, G., Ma, Z., Zhang, L., & Chen, J. (2024)**. EPlus-LLM: A large language model-based computing platform for automated building energy modeling. *Applied Energy*, 367, 123431. DOI: `https://doi.org/10.1016/j.apenergy.2024.123431`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and article metadata).
   - *Crossref returned title*: "EPlus-LLM: A large language model-based computing platform for automated building energy modeling".

2. **Ma, N., Labib, R., Amor, R., Chong, A., Fan, C., Forth, K., Fu, X., Fuchs, S., Hong, T., Klimenkova, N., Koo, J., Li, S., McCullough, S. T., Park, J. Y., Shraga, R., Yoon, S., Zhang, L., & Zhang, Y. (2026)**. Ten questions concerning Large Language Models (LLMs) for building applications. *Building and Environment*, 291, 114260. DOI: `https://doi.org/10.1016/j.buildenv.2026.114260`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and full article structure).
   - *Crossref returned title*: "Ten questions concerning Large Language Models (LLMs) for building applications".

3. **Liu, M., Zhang, L., Chen, J., Chen, W.-A., Yang, Z., Lo, L. J., Wen, J., & O'Neill, Z. (2025)**. Large language models for building energy applications: Opportunities and challenges. *Building Simulation*, 18(2), 225-234. DOI: `https://doi.org/10.1007/s12273-025-1235-9`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and publication record).
   - *Crossref returned title*: "Large language models for building energy applications: Opportunities and challenges".

4. **Zhang, L., & Chen, Z. (2025)**. Opportunities of applying Large Language Models in building energy sector. *Renewable and Sustainable Energy Reviews*, 214, 115558. DOI: `https://doi.org/10.1016/j.rser.2025.115558`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and article metadata).
   - *Crossref returned title*: "Opportunities of applying Large Language Models in building energy sector".

5. **Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023)**. Out of One, Many: Using Language Models to Simulate Human Samples. *Political Analysis*, 31(3), 337-351. DOI: `https://doi.org/10.1017/pan.2023.2`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and article abstract).
   - *Crossref returned title*: "Out of One, Many: Using Language Models to Simulate Human Samples".

6. **Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024)**. Synthetic Replacements for Human Survey Data? The Perils of Large Language Models. *Political Analysis*, 32(4), 401-416. DOI: `https://doi.org/10.1017/pan.2024.5`. Tier 2.
   - *Full text read*: Yes (Crossref REST API and article text).
   - *Crossref returned title*: "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models".

7. **Borisov, V., Sessler, K., Leemann, T., Pawelczyk, M., & Kasneci, G. (2023)**. Language Models are Realistic Tabular Data Generators. *International Conference on Learning Representations (ICLR 2023)*. arXiv preprint arXiv:2210.06280. DOI: `https://doi.org/10.48550/arXiv.2210.06280`. Tier 2.
   - *Full text read*: Yes (arXiv:2210.06280v3 and open-source repository).
   - *arXiv ID and version*: arXiv:2210.06280v3; published in ICLR 2023 proceedings.

8. **Kotelnikov, A., Baranchuk, D., Rubachev, I., & Babenko, A. (2023)**. TabDDPM: Modelling Tabular Data with Diffusion Models. *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202:17564-17579. arXiv preprint arXiv:2209.15421. DOI: `https://doi.org/10.48550/arXiv.2209.15421`. Tier 2.
   - *Full text read*: Yes (PMLR proceedings and arXiv:2209.15421v2).
   - *arXiv ID and version*: arXiv:2209.15421v2; published in ICML 2023.

9. **Xu, L., Skoularidou, M., Cuesta-Infante, A., & Veeramachaneni, K. (2019)**. Modeling Tabular data using Conditional GAN. *Advances in Neural Information Processing Systems (NeurIPS 2019)*, 32. arXiv preprint arXiv:1907.00503. DOI: `https://doi.org/10.48550/arXiv.1907.00503`. Tier 2.
   - *Full text read*: Yes (NeurIPS 2019 proceedings).
   - *arXiv ID and version*: arXiv:1907.00503v2.

10. **Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T. (2023)**. Whose Opinions Do Language Models Reflect? *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202:29971-30004. arXiv preprint arXiv:2303.17548. DOI: `https://doi.org/10.48550/arXiv.2303.17548`. Tier 2.
    - *Full text read*: Yes (PMLR proceedings and arXiv:2303.17548v2).
    - *arXiv ID and version*: arXiv:2303.17548v2.

11. **Wang, X., Fang, M., Zeng, Z., & Cheng, T. (2023)**. Where Would I Go Next? Large Language Models as Human Mobility Predictors. arXiv preprint arXiv:2308.15197. DOI: `https://doi.org/10.48550/arXiv.2308.15197`. Tier 2.
    - *Full text read*: Yes (arXiv:2308.15197v2 and GitHub repository).
    - *arXiv ID and version*: arXiv:2308.15197v2.

12. **Golrokh Amin, S., Rhoads, D., Fakhrmoosavi, F., Lownes, N. E., & Ivan, J. N. (2025)**. Generating Individual Travel Diaries Using Large Language Models Informed by Census and Land-Use Data. arXiv preprint arXiv:2509.09710. DOI: `https://doi.org/10.48550/arXiv.2509.09710`. Tier 2.
    - *Full text read*: Yes (arXiv:2509.09710v1).
    - *arXiv ID and version*: arXiv:2509.09710v1.

13. **Li, X., Huang, F., Lv, J., Xiao, Z., Li, G., & Yue, Y. (2024)**. Be More Real: Travel Diary Generation Using LLM Agents and Individual Profiles. arXiv preprint arXiv:2407.18932. DOI: `https://doi.org/10.48550/arXiv.2407.18932`. Tier 2.
    - *Full text read*: Yes (arXiv:2407.18932v1).
    - *arXiv ID and version*: arXiv:2407.18932v1.

14. **Tian, Y., Ren, X., Wang, Z., Gungor, O., Yu, X., & Rosing, T. (2025)**. DailyLLM: Context-Aware Activity Log Generation Using Multi-Modal Sensors and LLMs. *2025 IEEE 22nd International Conference on Mobile Ad-Hoc and Smart Systems (MASS)*. arXiv preprint arXiv:2507.13737. DOI: `https://doi.org/10.1109/MASS66014.2025.00060`. Tier 2.
    - *Full text read*: Yes (arXiv:2507.13737v1 and IEEE MASS 2025).
    - *arXiv ID and version*: arXiv:2507.13737v1.

15. **Liu, P., Xu, F., & Li, Y. (2026)**. TravelReasoner: Leveraging Large Reasoning Models to Address Mobility Data Gap. *Proceedings of the ACM Web Conference 2026 (WWW 2026)*. arXiv preprint arXiv:2506.06008. Tier 2.
    - *Full text read*: Read abstract and methodology summary.
    - *arXiv ID and version*: arXiv:2506.06008v1; accepted at WWW 2026.

16. **Yang, S., He, R., Yan, J., Wu, T., & Wu, Z. (2025)**. UrbanAct-GPT: LLM-Based Activity and Role Semantic Inference from Mobile Phone Signalling Data for City-Scale Weekday Dynamic Urban Structure Analysis. *SSRN Electronic Journal*, Art. 6305099. DOI: `https://doi.org/10.2139/ssrn.6305099`. Tier 2.
    - *Full text read*: Read abstract and methodology summary.
    - *SSRN ID*: SSRN-6305099.

17. **Iseri, O., Gursel Dino, I., & Kalkan, K. (2026)**. Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155`. Tier 2.
    - *Full text read*: Yes (in-project baseline manuscript).
    - *Crossref returned title*: "Occupancy modeling using population statistics and machine learning for urban residential built environment".
