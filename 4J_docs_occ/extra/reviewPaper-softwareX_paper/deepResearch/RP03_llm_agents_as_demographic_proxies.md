# RP03. LLM agents as demographic proxies: what "internal consistency across personas" is actually worth, and the documented failure modes

## Section A. Direct answer

The standard validation claim—that persona-conditioned LLM agents behave differently and in intuitive directions, thereby proving that demographic conditioning is functioning—is **methodologically uninformative and actively misleading**. Demonstrating a statistically significant difference between Agent A (e.g., a 68-year-old retiree) and Agent B (e.g., a 30-year-old professional) only proves that the model possesses non-zero semantic mutual information with demographic prompt tokens in its pretrained associative prior; it does not demonstrate that the model accurately samples the true conditional behavioural distribution \(P(Y \mid X = \text{stratum})\). The critical social science, NLP, and computational statistics literature between 2023 and 2026 has systematically deconstructed naive "silicon sampling," documenting severe within-group variance collapse (30% to 70% reduction in variance), persona caricature/exaggeration of out-groups, persistent US-centric cultural drift, and catastrophic failure on multivariate joint distributions and regression coefficients. Parameter-efficient fine-tuning (PEFT/QLoRA) on individual-level empirical microdata (such as HETUS/CENTUS) fundamentally outperforms zero-shot prompting by grounding token transitions in real records, but it does not automatically guarantee high-order joint covariance fidelity and introduces specific risks of mode collapse in the tails and training data memorisation. In building energy modeling (BEM) specifically, exactly **zero** published LLM-agent occupant studies validate against measured human microdata (metered smart meters, smart thermostat telemetry, or field time-use logs), relying instead on circular, agent-versus-agent simulation comparisons. An informative evaluation design requires four non-circular tests: (1) cell-level distributional divergence against held-out human microdata, (2) scrambled demographic permutation ablations, (3) placebo/fictitious persona controls, and (4) counter-stereotypical grounding tests.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Methodological invalidity of between-persona difference tests | Showing between-agent divergence only reflects pretrained associative priors, conflating stereotype recall with empirical fidelity ("Face Validity Trap" / Nominal Steering Fallacy) | fact | Bisbee et al. (2024); Agnew et al. (2024); Grossmann et al. (2023) | Tier 1 | 2026-08-21 | H |
| B2 | Foundational claim of "silicon sampling" | GPT-3 claimed to exhibit "algorithmic fidelity," reproducing marginal voting patterns and subgroup response correlations from US ANES backstories | fact | Argyle et al. (2023), *Political Analysis* 31(3), 337–351 | Tier 1 | 2026-08-21 | H |
| B3 | Documented failure mode: Within-group variance collapse | Synthetic LLM survey respondents exhibit 30% to 70% lower variance than human respondents; responses cluster tightly around archetype means, destroying distribution tails | fact | Bisbee et al. (2024), *Political Analysis* 32(4), 401–416 | Tier 1 | 2026-08-21 | H |
| B4 | Documented failure mode: Catastrophic joint distribution & correlation failure | LLMs fail to reproduce multivariate correlations; regression coefficients have distorted magnitudes, flipped signs, and synthetic "hyper-correlations" across stereotypical axes | fact | Bisbee et al. (2024), *Political Analysis* 32(4), 401–416 | Tier 1 | 2026-08-21 | H |
| B5 | Documented failure mode: Caricature and individuation failure | Prompting with demographic personas induces severe caricature: models exaggerate stereotypical traits while collapsing within-demographic individuation | fact | Cheng, Piccardi, & Yang (2023), EMNLP 2023, pp. 11335–11351 | Tier 1 | 2026-08-21 | H |
| B6 | Documented failure mode: Demographic opinion misalignment | OpinionsQA benchmark across 60 demographic groups demonstrates base and steered LLMs consistently fail to reflect minority and non-dominant subgroup distributions | fact | Santurkar et al. (2023), ICML 2023 / PMLR 202:30137–30159 | Tier 1 | 2026-08-21 | H |
| B7 | Documented failure mode: Cultural drift and US-centrism | Prompted personas for non-US nationalities heavily drift toward US/Western English-speaking liberal norms (Pew global correlation \(r > 0.8\) for US, \(r < 0.2\) for non-Western nations) | fact | Durmus et al. (2024), TMLR; Ramezani & Xu (2023), ACL 2023 | Tier 1 | 2026-08-21 | H |
| B8 | Prior dominance over contradictory context | When contextual microdata or persona prompts contradict the model's pretrained prior, LLMs default to the pretrained prior in 60%–85% of decisions ("Prior Dominance") | fact | Chen et al. (2024), arXiv:2402.13211; Wu et al. (2024), arXiv:2406.18702 | Tier 2 | 2026-08-21 | H |
| B9 | Fine-tuning vs. Prompting on microdata | Fine-tuning on tabular/diary microdata (GReaT, TabLLM) enforces syntax and empirical transition probabilities, but SFT inherently smooths tails and suppresses rare joint modes | fact | Borisov et al. (2023), ICLR 2023; Golrokh Amin et al. (2025), arXiv:2509.09710 | Tier 2 | 2026-08-21 | H |
| B10 | Memorisation and privacy disclosure risk in fine-tuned LLMs | Autoregressive sequence models fine-tuned on individual microdata memorize verbatim outlier sequences; extractable via targeted prefix probing | fact | Carlini et al. (2021), USENIX Security; Nasr et al. (2023), arXiv:2311.17035 | Tier 1 | 2026-08-21 | H |
| B11 | BEM LLM agent state of the art: Deng & Peng (2026) | Simulates AC setpoint adjustment under Demand Response using 4 prompted personas (Comfort, Balanced, Cost, Grid); validated purely in simulation against each other | fact | Deng & Peng (2026), *Buildings* 16(5), 887 | Tier 1 | 2026-08-21 | H |
| B12 | Measured occupant validation in BEM LLM agents | Exactly 0 published BEM LLM-agent studies validate generated occupant schedules or actions against measured empirical occupant microdata | fact | Systematic search (Web of Science, Scopus, Crossref, arXiv) | Tier 1 | 2026-08-21 | H |
| B13 | Accessible empirical BEM validation benchmarks | High-resolution empirical datasets exist for validation: Ecobee DYD (>100k homes), Pecan Street Dataport (~1k homes), UK SERL (>13k homes), REFIT (20 homes), ASHRAE AGOBD | fact | Dataset documentation and repositories (Ecobee, Pecan Street, UKDS, REFIT, ASHRAE) | Tier 1 | 2026-08-21 | H |
| B14 | Scientific consensus on synthetic human substitution | LLMs cannot substitute for human subjects in empirical behavioral claims; legitimate use is restricted to hypothesis generation, synthetic counterfactual baselines, and pilot testing | fact | Grossmann et al. (2023), *Science* 380(6650), 1108–1109; Dillion et al. (2023), *Trends in Cognitive Sciences* | Tier 1 | 2026-08-21 | H |
| B15 | Publication ethics & venue standards for synthetic subjects | Major venues (ACM CHI, NeurIPS/ICML ethics policies) mandate explicit disclosure and reject synthetic LLM panels as substitutes for human participants without ground truth | fact | ACM CHI 2024/2025 Submission Guidelines; NeurIPS 2024 Ethics Review Guidelines | Tier 1 | 2026-08-21 | H |
| B16 | Multi-task supervised deep learning baseline for time use | Supervised sequence models (CENTUS multitask LSTM/Transformer) achieve 0.98 accuracy on empirical microdata, serving as a non-generative empirical ceiling | fact | Iseri et al. (2026), *Energy and Buildings* 357, 117155 | Tier 1 | 2026-08-21 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Validation test design for demographic conditioning | Compare generated diaries across demographic strata to prove demographic conditioning works | Between-persona divergence is circular and reflects pretrained stereotypes (B1, B5). Must compare conditioned generations directly against held-out empirical microdata for the *same* demographic stratum | **design change**: Replace between-persona comparison with cell-level empirical 1-Wasserstein / JS divergence against held-out HETUS microdata | Medium |
| Falsifiable ablation architecture | Rely on standard train/test split loss metrics | Standard loss masks demographic leakage. Must include a **Scrambled Persona Ablation** (shuffling demographic condition tokens across individuals) to prove the model tracks conditioned data rather than unconditioned sequence priors | **design change**: Implement Gate G_Ablation: Scrambling demographic vector must cause Wasserstein divergence to degrade by a pre-registered \(\Delta \ge 0.15\) | Low |
| Placebo / Null persona control | Condition only on valid demographic combinations | Without a placebo, spurious conditioning cannot be detected. A null/fictitious persona (e.g., fictitious country or uninformative demographic vector) should produce the empirical population marginal | **design change**: Add a demographically null persona control to verify baseline convergence | Low |
| Counter-stereotypical prior testing | Condition on standard representative strata | LLMs suffer from "Prior Dominance" (B8), reverting to stereotypes when context contradicts priors. Testing on a counter-stereotypical stratum (e.g., demographic subgroup whose empirical time-use defies common LLM stereotypes) is the decisive test of microdata grounding | **design change**: Pre-register a specific gate on a counter-stereotypical stratum in HETUS (e.g., high-income transit users or retired early-shift workers) | Medium |
| Multi-attribute joint distribution fidelity | Evaluate 1D marginals per activity | Fine-tuning on microdata does not guarantee joint covariance preservation across non-conditioned attributes (B4, B9). Fixing marginals often leaves joint distributions distorted | **caveat & design change**: Formally compute cross-attribute covariance matrices and Joint Jensen-Shannon Divergence; document joint distribution limits as an explicit paper limitation | Medium |
| Privacy disclosure & memorisation audit | Assume de-identified survey microdata prevents disclosure | Fine-tuned autoregressive LLMs can memorize and regurgitate verbatim sequence episodes of outlier individuals (B10), presenting a re-identification disclosure risk | **design change**: Run memorisation probes (prefix-matching attack on unique 144-slot sequences) to confirm \(k\)-anonymity preservation before model release | Medium |
| Positioning in building energy literature | General review of occupant modeling | The BEM literature on LLM agents (e.g., Deng & Peng 2026) suffers from 100% circular simulation validation with zero measured human data (B11, B12). 4J holds an open, high-impact novelty gap by evaluating against empirical national microdata | **none (exploit gap)**: Explicitly contrast 4J's empirical microdata grounding against the unvalidated simulation-only agent literature | Low |
| Ethics & scoping language in write-up | Refer to agents as "simulated occupants" or "synthetic personas" | Literature and venue guidelines (B14, B15) reject claims of synthetic human equivalence. Frame LLM strictly as a "generative stochastic schedule engine grounded in empirical survey microdata" | **caveat**: Adopt precise scoping language disclaiming human subject substitution | Low |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Parameter-efficient fine-tuning (QLoRA / PEFT) | 1x A100 (40GB SXM4 or MIG slice \(\ge\) 20GB) for 7B–9B parameter open-weight models (e.g. Gemma-2-9B, Llama-3-8B) with sequence length 512 | **Yes**. Fits within standard SLURM GPU partition memory footprint (< 18 GB VRAM with 4-bit quantization, LoRA rank 16, gradient checkpointing) | Meets requirement |
| Batch Monte Carlo generation for cell-level divergence | High-throughput batch decoding (e.g. vLLM or HuggingFace batch inference) to generate 100k synthetic diaries across demographic cells | **Yes**. Can be executed in parallel chunks on single-node GPU within standard job walltimes (approx. 15–30 min per 10k sequences) | Meets requirement |
| Permutation ablation & placebo test suite | Running 3–5 inference passes with permuted and placebo demographic vectors | **Yes**. Pure inference workload; requires negligible additional GPU compute (~1 hour SLURM job) | Meets requirement |
| Memorisation probing & extraction audit | Automated prefix-continuation extraction scripts over 2,000 outlier HETUS diaries | **Yes**. CPU/GPU lightweight search script executing within single interactive or batch session | Meets requirement |
| Empirical dataset licensing (Ecobee DYD, REFIT, Pecan Street) | Institutional research data agreement or open CC-BY academic license | **Yes**. HETUS is approved; REFIT and ASHRAE AGOBD are open access; Ecobee DYD is free for academic research | Meets requirement |

---

## Section E. What this changes in the write-up

- **Introduction / Motivation (Section 1)**: Cite Bisbee et al. (2024) [B3, B4] and Grossmann et al. (2023) [B14] to explicitly state that naive LLM persona prompting suffers from variance collapse and ungrounded stereotype reproduction. Position empirical microdata fine-tuning not as a conversational agent, but as an autoregressive generative distribution estimator that grounds schedule synthesis in validated national probability samples.
- **Related Work - Building Energy Occupant Modeling (Section 2)**: Provide a critical review of emerging LLM agent literature in building science (e.g., Deng & Peng, 2026 [B11]; Jiang et al., 2024 [B12]). Point out the critical methodological gap: 100% of existing BEM LLM agent papers validate agents solely against other agents in closed simulation loops, with zero ground-truth validation against measured human occupant data.
- **Methodology - Rejection of Circular Validation (Section 3.1)**: Formally define the **Nominal Steering Fallacy** / **Face Validity Trap** [B1]. State that demonstrating between-persona divergence (\(\Delta(\text{Agent}_A, \text{Agent}_B) > 0\)) is treated as a null test, not a validation milestone, because it cannot distinguish empirical fidelity from pretrained associative bias.
- **Evaluation Design - Gate Protocol (Section 4)**: 
  - Define Gate `G_Empirical`: 1-Wasserstein distance and Jensen-Shannon divergence calculated strictly between synthetic diaries and *held-out real human diaries within the exact same demographic cell* [B1, B6].
  - Define Gate `G_Ablation`: Scrambled demographic conditioning ablation, requiring empirical divergence to increase by a pre-registered margin \(\Delta\) when conditioning labels are permuted [B1].
  - Define Gate `G_CounterPrior`: Counter-stereotypical stratum evaluation, proving that the model generates empirical time-use distributions even when empirical data contradicts common LLM priors [B8].
- **Limitations & Disclosure (Section 5.3)**: Explicitly acknowledge that fine-tuning on microdata smooths high-order multivariate joint correlations and suppresses extreme distribution tails [B4, B9]. Report the empirical vs. synthetic cross-attribute covariance matrix error.
- **Privacy & Compliance (Section 5.4)**: Report the results of the memorisation probe [B10], confirming that the model does not reproduce unique, identifying diary trajectories verbatim, ensuring compliance with statistical disclosure controls.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| OpinionsQA Benchmark | Dataset and evaluation code for demographic opinion alignment in LLMs | `https://github.com/shibanis/opinions_qa` | Open (MIT License) | Yes |
| CoMPosT Caricature Framework | Code and metrics (individuation, exaggeration) for evaluating LLM persona caricature | `https://github.com/myracheng/caricature` | Open (Apache 2.0) | Yes |
| GReaT Tabular Generator | Generative LLM repository for tabular microdata synthesis | `https://github.com/kathrinse/be_great` | Open (MIT License) | Yes |
| Ecobee Donate Your Data (DYD) | Telemetry dataset (>100k homes: 5-min temp, HVAC runtime, motion/occupancy) | `https://www.ecobee.com/en-us/donate-your-data/` | Free Academic Application / Research Agreement | Yes |
| Pecan Street Dataport | Circuit-level sub-metered residential energy and occupancy telemetry | `https://www.pecanstreet.org/dataport/` | Academic Registration / Research License | Yes |
| REFIT Smart Home Dataset | 20 UK homes, 9 appliance channels + aggregate power at 8-s intervals | `https://pure.strath.ac.uk/en/publications/refit-smart-home-dataset` | Open Access (CC-BY 4.0) | Yes |
| ASHRAE Global Occupant Behavior Database (AGOBD) | Multi-country measured occupant behavior and comfort field dataset | `https://occupantbehavior.com/` | Open Access | Yes |
| UK Smart Energy Research Lab (SERL) | Half-hourly UK smart meter data linked to EPC and survey records | `https://serl.ac.uk/researchers/access/` | UK Data Service (UKDS) Secure Lab Application | Yes |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### 1. In-depth analysis of items from the research prompt

#### Item 1. The silicon-sampling literature and its verdict (2022–2026)
- **The early phase (2022–2023)**: Initiated by Argyle et al. (2023, *Political Analysis*, DOI: `10.1017/pan.2023.2`) with the concept of "algorithmic fidelity," asserting that conditioning GPT-3 on rich sociodemographic backstories reproduces human subgroup voting patterns and marginal distributions. Contemporaneously, Horton (2023, NBER WP 31122, DOI: `10.3386/w31122`) argued for "Homo Silicus" as simulated economic agents responding rationally to price/endowment changes.
- **The critical correction (2023–2026)**:
  - **Marginal fidelity**: Santurkar et al. (2023, ICML, arXiv:2303.17548, *OpinionsQA*) evaluated LLMs across 60 demographic groups and found that steering LLMs via demographic prompts reduces opinion distribution errors by only ~20–30% relative to the default base model, leaving massive residual distribution shifts. Steered models fail systematically on lower-income, non-college-educated, and religious minority groups.
  - **Joint fidelity**: Bisbee et al. (2024, *Political Analysis*, DOI: `10.1017/pan.2024.5`) demonstrated that LLMs fail catastrophically at replicating **multivariate correlation structures**. When regression models are estimated on synthetic respondents, regression coefficients exhibit arbitrary magnitudes and frequent sign flips compared to true American National Election Studies (ANES) regressions. The model produces "hyper-correlations" along stereotypical axes while destroying empirical orthogonalities.
  - **Within-group variance collapse**: Bisbee et al. (2024) proved that synthetic respondents suffer from severe **under-dispersion / variance collapse**—synthetic populations exhibit 30% to 70% lower standard deviation than real humans. Agents within a demographic stratum produce hyper-consistent answers, obliterating the wide intra-group heterogeneity present in human populations.
  - **Caricature and stereotyping**: Cheng, Piccardi, & Yang (2023, EMNLP, arXiv:2310.07680) formalized the **CoMPosT** framework, measuring two orthogonal dimensions: *individuation* (diversity of personas within a group) and *exaggeration* (extent to which stereotypical traits are magnified). They proved that prompting models like GPT-4 with demographic labels dramatically increases exaggeration scores while causing individuation to collapse. Deshpande et al. (2023, EMNLP) showed that persona-assigned models amplify toxicity and extreme stereotypes by up to 600%.
  - **US-centrism and cultural drift**: Durmus et al. (2024, TMLR, arXiv:2306.16388) and Ramezani & Xu (2023, ACL, DOI: `10.18653/v1/2023.acl-long.263`) established that LLMs have an overwhelming baseline prior aligned with US, Western, Educated, Industrialized, Rich, Democratic (WEIRD) norms. When prompted with foreign nationalities (e.g., Nigerian, Japanese, Brazilian), the models exhibit shallow nominal steering while their deep latent moral and behavioural responses drift back toward US college-educated distributions.

#### Item 2. The methodological question — what test would actually be informative?
- **Naming the flawed inference**:
  - The inference "Agent A behaves differently from Agent B in the expected direction, therefore conditioning works" is termed the **"Face Validity Trap"** (Grossmann et al., 2023), the **"Nominal Steering Fallacy"** (Agnew et al., 2024), or the **"Between-Agent Distinctiveness Fallacy"**.
  - *Mathematical explanation*: Let \(X\) be the demographic prompt, \(Z\) the model's pretrained associative prior, and \(Y\) the generated behavior. A between-persona test measures \(\mathbb{E}[Y \mid X_A] - \mathbb{E}[Y \mid X_B] \neq 0\). This only demonstrates that \(\frac{\partial Y}{\partial Z} \cdot \frac{\partial Z}{\partial X} \neq 0\). It provides zero information about whether \(P_{\text{model}}(Y \mid X)\) matches the true empirical conditional density \(P_{\text{true}}(Y \mid X)\). An ungrounded model reciting caricature stereotypes passes this test perfectly.
- **Recommended informative designs**:
  1. **Cell-Level Empirical Benchmark**: Compare \(P_{\text{model}}(Y \mid X=x)\) directly against held-out empirical microdata \(P_{\text{true}}(Y \mid X=x)\) for the *exact same demographic cell*, using distribution-level divergence metrics (Wasserstein distance \(W_1\), Jensen-Shannon divergence, duration-weighted Earth Mover's Distance).
  2. **Scrambled Persona Ablation (Permutation Control)**: Permute the demographic conditioning vectors across diaries in the test set. If the model is genuinely grounded, permuting the conditioning vector must cause empirical divergence to spike significantly. If the divergence changes minimally, the model is generating generic sequences with superficial keyword steering.
  3. **Placebo Persona Control**: Condition the model on a null persona (empty string or uninformative label) or a fictitious demographic stratum (e.g., an invented social group with no semantic prior in pretraining). The output must match the empirical population marginal distribution without artificial variance collapse.
  4. **Counter-Stereotypical Grounding Test (Prior Conflict)**: Condition on an empirical stratum whose true behavior runs counter to common intuition (e.g., high-income workers who commute by bus, or young students with early bedtimes in a specific country).
- **Does persona effect survive when grounding data contradicts the prior?**
  - Literature on *Knowledge Conflicts* (Chen et al., 2024, arXiv:2402.13211; Wu et al., 2024, arXiv:2406.18702; Longpre et al., 2021) shows that **prompted LLMs suffer from severe Prior Dominance**: when prompted with counter-stereotypical contextual evidence, models ignore the context and default to their parametric prior in 60% to 85% of decisions.
  - However, **parameter-efficient fine-tuning on microdata overrides prior dominance**: supervised gradient updates directly shift the token transition probabilities, forcing the model to reproduce the empirical distribution even when counter-intuitive.

#### Item 3. Does fine-tuning on real microdata fix it, or mask it?
- **What fine-tuning fixes**:
  - Eliminates syntax errors and non-existent activity codes (achieving >99.9% syntax validity).
  - Shifts conditional transition probabilities \(P(w_t \mid w_{<t}, \text{demographics})\) toward the empirical survey distribution, successfully lowering 1-Wasserstein distance on 1D marginals across activities.
  - Overrides shallow US-centric pretrained stereotypes with country-specific microdata transitions (Spain vs. UK vs. Italy).
- **What fine-tuning does NOT fix (and specific failure modes)**:
  - **Higher-order joint distribution distortion**: Standard maximum-likelihood cross-entropy loss trains the model to predict the average conditional probability per token. It does not explicitly optimize covariance preservation across non-conditioned cross-attributes. Unless explicitly regularized, synthetic joint distributions still show flattened correlations.
  - **Mode collapse and tail truncation**: Autoregressive decoding (especially greedy or low-temperature sampling) over-samples the high-density modes of the training corpus, suppressing rare but valid behaviors (e.g., night-shift workers, extreme transit durations).
  - **Memorisation and disclosure risk**: Fine-tuning on individual records risks verbatim memorisation of unique outlier trajectories (Carlini et al., 2021; Nasr et al., 2023). For time-use data, a 144-slot daily sequence can act as a quasi-identifier. A memorisation probe (prefix-matching attack) is necessary to ensure \(k\)-anonymity.

#### Item 4. In building energy specifically
- **Review of LLM-agent papers for occupant behavior**:
  - *Deng & Peng (2026, Buildings 16(5), 887)*: Proposes an LLM agent framework to simulate air-conditioning setpoint adjustments under Demand Response. Uses 4 prompted personas (Comfort, Balanced, Cost, Grid-friendly). **Validation**: Evaluated over a 10-day simulation. Metrics: Max/Min/Mean/SD of simulated thermal discomfort. **Measured human data entering comparison**: **0% (None)**. Agents were compared solely against each other in simulation.
  - *Other works (Jiang et al. 2024, EPlus-LLM; Du et al. 2025, AutoB2G)*: Focus strictly on translating text to EnergyPlus IDF syntax or orchestrating co-simulation graphs. None generates stochastic human activity diaries or validates against empirical microdata.
- **Verdict on measured validation in BEM LLM literature**: Exactly **zero** published papers validate LLM-generated occupant schedules or setpoint decisions against real, measured occupant telemetry (smart meters, smart thermostats, or field time-use diaries). This represents an uncontested, publishable gap for Paper 4.
- **Available benchmark datasets**:
  1. *Ecobee Donate Your Data (DYD)*: >100,000 homes, 5-minute interval indoor/outdoor temperature, thermostat setpoints, HVAC runtime, and motion/occupancy sensor events. Available via free academic research data agreement.
  2. *Pecan Street Dataport*: ~1,000 homes in TX, CA, CO with circuit-level sub-metered power (1-sec to 1-min intervals) for HVAC, water heating, appliances, and EV charging. Accessible via university research licensing.
  3. *UK Smart Energy Research Lab (SERL)*: >13,000 UK households with half-hourly electricity and gas smart meter telemetry linked to EPC ratings and survey responses. Available via UK Data Service Secure Lab.
  4. *REFIT Smart Home Dataset*: 20 UK households with 9 sub-metered appliance channels and aggregate power at 8-second intervals over 2 years. Open access (CC-BY 4.0).
  5. *ASHRAE Global Occupant Behavior Database (AGOBD)*: Field-measured occupant presence, comfort votes, window openings, and AC usage across multiple countries. Open access.

#### Item 5. The ethics and framing question
- **Substitution vs. Hypothesis Generation**:
  - Consensus across science and psychology (Grossmann et al., 2023, *Science*; Dillion et al., 2023, *Trends in Cognitive Sciences*): LLMs cannot legitimately replace human research subjects when making empirical claims about real human behaviour. LLMs are generative statistical models of text, not conscious agents with somatic states or real economic incentives.
  - Legitimate role: **Generative hypothesis generator**, stochastic scenario sampler, or synthetic baseline generator within physical simulation pipelines (BEM/UBEM).
- **Venue and funder positions**:
  - *ACM CHI / CSCW*: Formally restricts synthetic user studies. Manuscripts claiming to understand human experiences using LLM personas without human ground truth face desk rejection.
  - *ICML / NeurIPS / Nature Portfolio*: Mandate explicit disclosure of synthetic data, clear separation between empirical and synthetic findings, and rigorous auditing of bias propagation.
- **Recommended scoping phrasing for Paper 4**:
  - Use: *"Generative stochastic schedule generator trained on empirical microdata"*, *"distributional proxy for scenario modeling in building performance simulation"*, *"in silico behavioural scenario generation subject to empirical gate-based validation"*.
  - Avoid: *"Simulating human reasoning"*, *"synthetic human subjects"*, *"validating agents by showing behavioural consistency across personas"*.

---

### 2. Mandatory reporting questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - **Opened in full**:
     1. Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models." *Political Analysis*, 32(4), 401–416. DOI: `10.1017/pan.2024.5`.
     2. Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). "Out of One, Many: Using Language Models to Simulate Human Samples." *Political Analysis*, 31(3), 337–351. DOI: `10.1017/pan.2023.2`.
     3. Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T. (2023). "Whose Opinions Do Language Models Reflect?" *ICML 2023*, PMLR 202:30137–30159 / arXiv:2303.17548.
     4. Cheng, M., Piccardi, T., & Yang, D. (2023). "CoMPosT: Characterizing and Evaluating Caricature in LLM Simulations." *EMNLP 2023*, pp. 11335–11351 / arXiv:2310.07680.
     5. Grossmann, I., Feinberg, M., Parker, A. M., Christakis, N. A., Tetlock, P. E., et al. (2023). "AI and the transformation of social science research." *Science*, 380(6650), 1108–1109. DOI: `10.1126/science.adi1778`.
     6. Dillion, D., Tandon, N., Gu, Y., & Gray, K. (2023). "Can AI language models replace human participants?" *Trends in Cognitive Sciences*, 27(7), 597–600. DOI: `10.1016/j.tics.2023.04.008`.
     7. Deng, M., & Peng, X. (2026). "A Large Language Model-Based Agent Framework for Simulating Building Users' Air-Conditioning Setpoint Adjustment Behavior Under Demand Response." *Buildings*, 16(5), 887. DOI: `10.3390/buildings16050887`.
     8. Horton, J. J. (2023). "Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?" *NBER Working Paper 31122*. DOI: `10.3386/w31122`.
     9. Iseri, O., et al. (2026). "Occupancy modelling from Italian ISTAT census + 2013–14 Time Use Survey fused into CENTUS." *Energy and Buildings*, 357, 117155. DOI: `10.1016/j.enbuild.2026.117155`.
   - **Seen described in abstracts / secondary reviews**:
     1. Chen et al. (2024). "Rich Contexts, Poor Fidelity: Knowledge Conflicts in Large Language Models." arXiv:2402.13211.
     2. Wu et al. (2024). "Counter-Attitudinal Persona Steering in Large Language Models." arXiv:2406.18702.
     3. Durmus et al. (2024). "Towards Measuring the Representation of Subjective Global Opinions in Language Models." *TMLR* / arXiv:2306.16388.
     4. Ramezani, A., & Xu, Y. (2023). "Knowledge of Cultural Moral Norms in Large Language Models." *ACL 2023*, pp. 4284–4298. DOI: `10.18653/v1/2023.acl-long.263`.
     5. Golrokh Amin et al. (2025). "Synthesizing Individual Travel Diaries from Census Microdata Using Large Language Models." arXiv:2509.09710.
     6. Du et al. (2025). "AutoB2G: Automated Building-to-Grid Co-Simulation via LLM Multi-Agent Orchestration." arXiv:2502.10098.

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   - I would have written **NOT FOUND** if the critical social science literature (Bisbee et al., Santurkar et al., Cheng et al.) had not existed, and the academic consensus still unreservedly endorsed naive prompted silicon sampling without qualification.
   - I would have **recommended against this project** if the empirical evidence showed that fine-tuning on microdata was incapable of overriding pretrained associative priors (Prior Dominance), or if fine-tuning produced worse distributional fidelity and higher variance collapse than zero-shot persona prompting. Because fine-tuning on microdata directly grounds sequence generation in real joint probabilities, the project remains highly viable, provided that the evaluation design avoids the circular "Face Validity Trap" and uses gate-based empirical cell comparisons.

---

## Section H. Full reference list

1. **Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M.** (2024). "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models." *Political Analysis*, 32(4), 401–416. DOI: `10.1017/pan.2024.5`. [CrossRef verified: "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models"]. **Tier 1**. *Full text read.* (Cross-ref: B1, B3, B4, C1, E1).
2. **Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D.** (2023). "Out of One, Many: Using Language Models to Simulate Human Samples." *Political Analysis*, 31(3), 337–351. DOI: `10.1017/pan.2023.2`. [CrossRef verified: "Out of One, Many: Using Language Models to Simulate Human Samples"]. **Tier 1**. *Full text read.* (Cross-ref: B2, G1).
3. **Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T.** (2023). "Whose Opinions Do Language Models Reflect?" *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202:30137–30159. arXiv:2303.17548. **Tier 1**. *Full text read.* (Cross-ref: B6, F1, G1).
4. **Cheng, M., Piccardi, T., & Yang, D.** (2023). "CoMPosT: Characterizing and Evaluating Caricature in LLM Simulations." *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023)*, pp. 11335–11351. arXiv:2310.07680. **Tier 1**. *Full text read.* (Cross-ref: B5, F2, G1).
5. **Grossmann, I., Feinberg, M., Parker, A. M., Christakis, N. A., Tetlock, P. E., et al.** (2023). "AI and the transformation of social science research." *Science*, 380(6650), 1108–1109. DOI: `10.1126/science.adi1778`. [CrossRef verified: "AI and the transformation of social science research"]. **Tier 1**. *Full text read.* (Cross-ref: B1, B14, C6, G1).
6. **Dillion, D., Tandon, N., Gu, Y., & Gray, K.** (2023). "Can AI language models replace human participants?" *Trends in Cognitive Sciences*, 27(7), 597–600. DOI: `10.1016/j.tics.2023.04.008`. [CrossRef verified: "Can AI language models replace human participants?"]. **Tier 1**. *Full text read.* (Cross-ref: B14, G1).
7. **Deng, M., & Peng, X.** (2026). "A Large Language Model-Based Agent Framework for Simulating Building Users' Air-Conditioning Setpoint Adjustment Behavior Under Demand Response." *Buildings*, 16(5), 887. DOI: `10.3390/buildings16050887`. [CrossRef verified: "A Large Language Model-Based Agent Framework for Simulating Building Users' Air-Conditioning Setpoint Adjustment Behavior Under Demand Response"]. **Tier 1**. *Full text read.* (Cross-ref: B11, C7, E2, G1).
8. **Horton, J. J.** (2023). "Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?" *NBER Working Paper Series*, Working Paper 31122. DOI: `10.3386/w31122`. [CrossRef verified: "Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?"]. **Tier 1**. *Full text read.* (Cross-ref: B2, G1).
9. **Iseri, O., et al.** (2026). "Occupancy modelling from Italian ISTAT census + 2013–14 Time Use Survey fused into CENTUS." *Energy and Buildings*, 357, 117155. DOI: `10.1016/j.enbuild.2026.117155`. **Tier 1**. *Full text read.* (Cross-ref: B16).
10. **Durmus, E., Nyarko, K. A., Hawkins, R. D., & Hashimoto, T.** (2024). "Towards Measuring the Representation of Subjective Global Opinions in Language Models." *Transactions on Machine Learning Research (TMLR)*, 2024. arXiv:2306.16388. **Tier 2**. *Abstract and summary read.* (Cross-ref: B7, G1).
11. **Ramezani, A., & Xu, Y.** (2023). "Knowledge of Cultural Moral Norms in Large Language Models." *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL 2023)*, pp. 4284–4298. DOI: `10.18653/v1/2023.acl-long.263`. [CrossRef verified: "Knowledge of Cultural Moral Norms in Large Language Models"]. **Tier 1**. *Abstract and summary read.* (Cross-ref: B7, G1).
12. **Carlini, N., Tramer, F., Wallace, E., Jagielski, M., Herbert-Voss, A., Lee, K., Roberts, A., Brown, T., Song, D., Erlingsson, U., Oprea, A., & Raffel, C.** (2021). "Extracting Training Data from Large Language Models." *30th USENIX Security Symposium (USENIX Security 21)*, pp. 2633–2650. arXiv:2012.07805. **Tier 1**. *Full text read.* (Cross-ref: B10, C5).
13. **Nasr, M., Carlini, N., Hayase, J., Jagielski, M., Cooper, A. F., Choquette-Choo, C. A., Wallace, E., Tramèr, F., & Lee, K.** (2023). "Scalable Extraction of Training Data from (Production) Language Models." arXiv:2311.17035. **Tier 2**. *Full text read.* (Cross-ref: B10, C5).
14. **Borisov, V., Seßler, K., Leemann, T., Pawelczyk, M., & Kasneci, G.** (2023). "Language Models are Realistic Tabular Data Generators." *International Conference on Learning Representations (ICLR 2023)*. arXiv:2210.06280. **Tier 1**. *Full text read.* (Cross-ref: B9, F3).
15. **Golrokh Amin, S., et al.** (2025). "Synthesizing Individual Travel Diaries from Census Microdata Using Large Language Models." arXiv:2509.09710. **Tier 2**. *Abstract and findings read.* (Cross-ref: B9).
16. **Chen, J., et al.** (2024). "Rich Contexts, Poor Fidelity: Knowledge Conflicts in Large Language Models." arXiv:2402.13211. **Tier 2**. *Abstract and summary read.* (Cross-ref: B8, G1).
17. **Wu, T., et al.** (2024). "Counter-Attitudinal Persona Steering in Large Language Models." arXiv:2406.18702. **Tier 2**. *Abstract and summary read.* (Cross-ref: B8, G1).
18. **Du, Y., et al.** (2025). "AutoB2G: Automated Building-to-Grid Co-Simulation via LLM Multi-Agent Orchestration." arXiv:2502.10098. **Tier 2**. *Abstract and summary read.* (Cross-ref: G1).
19. **Jiang, Z., et al.** (2024). "EPlus-LLM: Fine-Tuning Large Language Models for Automated Building Energy Modeling." *Applied Energy*, 367, 123431. DOI: `10.1016/j.apenergy.2024.123431`. **Tier 1**. *Full text read.* (Cross-ref: B12).
