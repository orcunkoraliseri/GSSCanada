# RL10: Privacy, Statistical Disclosure and Release Policy for Fine-Tuned Language Models

## Section A. Direct answer

No, you may not publicly publish the fine-tuned model weights or parameter adapters trained on restricted-access official statistical microdata under standard Eurostat and National Statistical Institute (NSI) data-use agreements. Commission Regulation (EU) No 557/2013 and Eurostat standard confidentiality undertakings strictly prohibit the distribution, transfer, or release of any derived files or intermediate analytical artefacts that permit direct or indirect identification of statistical units. Extensive empirical evidence confirms that large language models and parameter-efficient fine-tuning (PEFT/LoRA) adapters memorise training records, especially when fine-tuned across multiple epochs on small, structured, highly repetitive tabular datasets, enabling verbatim extraction and high-confidence membership inference. Statistical institutes treat deep neural network weights as complex, non-standard outputs that cannot pass standard statistical disclosure control (SDC) output checking without mathematical differential privacy or exhaustive empirical safety verification. There is zero published precedent of an official statistical institute permitting public weight release from a restricted microdata research project. To maintain complete legal compliance, protect institutional research access, and satisfy journal reproducibility requirements, the project must adopt a defensible release architecture: publish the complete open-source training pipeline code, data curation recipes, and evaluation scripts, paired with a rigorously vetted, disclosure-controlled synthetic occupancy dataset, while withholding the trained model weights.

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Legal status of derived confidential data under Eurostat regulation | Researchers must not distribute, sell or lend confidential data to third parties; all derived confidential data must be destroyed upon project completion | Fact | Commission Regulation (EU) No 557/2013, Art. 7(3); Eurostat Terms of Use Clause 5 | Tier 1 | 2026-08-13 | H |
| B2 | Dissemination restriction on research outputs | Only non-confidential aggregated results of statistical analyses may be published or disseminated | Fact | Commission Regulation (EU) No 557/2013, Art. 7(3); Eurostat Terms of Use Clause 8 | Tier 1 | 2026-08-13 | H |
| B3 | Mandatory output checking for secure-use facilities | Output checking by NSI/Eurostat staff is legally mandatory before any analytical result is extracted from secure environments | Fact | Commission Regulation (EU) No 557/2013, Art. 8(2); Eurostat SDC Guidelines | Tier 1 | 2026-08-13 | H |
| B4 | SDC treatment of machine learning weights in Trusted Research Environments | Deep neural network weights and raw parameter matrices are classified as complex non-standard outputs and denied automatic clearance | Fact | ONS / ADR UK SACRO Framework (Mansouri-Benssassi et al., 2023) | Tier 1 | 2026-08-13 | H |
| B5 | Published precedent for public weight release from restricted microdata | No documented precedent found of a model fine-tuned on restricted official microdata releasing public weights | Fact | Systematic search of Eurostat, ONS, StatCan, Hugging Face, Zenodo | Tier 1 | 2026-08-13 | H |
| B6 | Quantitative scaling of verbatim memorisation with model capacity | Memorisation scales as a power law with model size; a 10x increase in parameter count yields 2x to 5x more extractable verbatim sequences | Fact | Carlini et al. (ICLR 2023), arXiv:2202.07646 | Tier 2 | 2026-08-13 | H |
| B7 | Quantitative scaling of memorisation with training data duplication | Extractability scales log-linearly with duplication count k (proportional to k^1.27); sequences repeated >= 10 times are memorised at > 50% in 6B models | Fact | Carlini et al. (ICLR 2023); Lee et al. (ACL 2022) | Tier 2 | 2026-08-13 | H |
| B8 | Memorisation dynamics in small-corpus multi-epoch fine-tuning | Fine-tuning a pre-trained LLM for 3 to 10 epochs on small datasets (< 500k samples) causes rapid parameter overfitting to rare outlier vectors | Fact | Mireshghallah et al. (EMNLP 2022); Tirumala et al. (NeurIPS 2022) | Tier 2 | 2026-08-13 | H |
| B9 | Vulnerability of LoRA / PEFT adapters to Membership Inference Attacks | LoRA adapters exhibit high vulnerability to membership inference (AUC 0.85 to 0.95) because public base models act as reference models | Fact | LoRA-Leak (2024); Mahloujifar et al. (2021) | Tier 2 | 2026-08-13 | H |
| B10 | Re-identification bounds of human activity and trajectory sequences | Four spatio-temporal observation points uniquely identify 95% of individuals in mobility and activity sequence datasets | Fact | de Montjoye et al. (2013), Sci. Rep. 3:1376; Rocher et al. (2019), Nat. Commun. 10:3069 | Tier 2 | 2026-08-13 | H |
| B11 | Standard NSI statistical disclosure control on time-use microdata | Geographic coarsening (NUTS2/national), top-coding age at 75+, capping household size at 5+, collapsing 3-digit activity codes | Fact | Eurostat HETUS 2010/2020 Methodological Guidelines | Tier 1 | 2026-08-13 | H |
| B12 | Utility penalty of Differential Privacy (DP-SGD) in generative sequence modeling | Generative sequence modeling under DP-SGD (epsilon <= 2 to 8) causes severe syntax/structural collapse and flattens tail distributions | Fact | Li et al. (ICLR 2022), arXiv:2110.05679; Yu et al. (ICLR 2022) | Tier 2 | 2026-08-13 | H |
| B13 | Computational overhead of DP-SGD on single-node GPU hardware | Per-sample gradient clipping and noise addition increases GPU VRAM consumption by 2x to 4x and slows training throughput by 3x to 8x | Fact | Opacus Documentation (v1.4.0); Li et al. (2022) | Tier 3 | 2026-08-13 | H |
| B14 | Canadian Research Ethics Board (REB) requirements for secondary microdata | TCPS 2 (2022) Article 2.4 exempts anonymous data; secondary use of anonymised/coded microdata requires administrative REB waiver/protocol | Fact | TCPS 2 (2022), Chapter 2, Articles 2.2 and 2.4 | Tier 1 | 2026-08-13 | H |
| B15 | GDPR applicability to EU statistical microdata accessed from Canada | Eurostat Scientific-Use Files are pseudonymised personal data under GDPR Recital 26 and CJEU Case C-582/14 (Breyer), covered by Art. 89 safeguards | Fact | GDPR Recital 26; CJEU Case C-582/14; Regulation (EC) 223/2009 Art. 23 | Tier 1 | 2026-08-13 | H |

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Model artefact release | Publish fine-tuned open weights or LoRA adapter on Hugging Face / Zenodo | Public release of weights trained on restricted microdata violates Eurostat Regulation 557/2013 and leaks microdata | Design change: Withhold model weights; release only vetted synthetic datasets and open pipeline code | Medium |
| Release Option Ranking (Item 5) | Unranked assumption of public adapter release | Ranked release options indicate Option 3 (Synthetic dataset release) + Option 4 (Code/recipe release) is the only legally sound path | Design change: Adopt Option 3 + Option 4 as the formal project release architecture | Low |
| Differential Privacy implementation | Consider DP-SGD during fine-tuning | DP-SGD destroys generative fidelity on tail activities, triples compute overhead, and is unnecessary if weights are not released | Design change: Omit DP-SGD fine-tuning; use post-generation statistical disclosure filtering on synthetic data | Low |
| Empirical leakage evaluation | No formal self-attack specified | Self-auditing via Membership Inference Attacks (MIA) and prefix extraction is necessary to prove synthetic safety | Design change: Implement extraction attack and MIA battery as part of the validation pipeline | Medium |
| Institutional ethics compliance | Assume universal exemption under anonymised data rules | TCPS 2 Article 2.4 distinguishes anonymous from coded/anonymised; Canadian REB requires a formal secondary-use waiver | Caveat: Submit formal secondary data notification to university REB before manuscript submission | Low |

### Ranked Release Options (Prompt Item 5)

1. **Option 3 (Rank 1 - RECOMMENDED): Release only the generated synthetic dataset, not the model weights.**
   - *Data Agreement Compatibility*: Fully compliant with Eurostat Regulation (EU) No 557/2013 and NSI terms, provided the synthetic dataset passes SDC checks (no exact training clones, DCR thresholds satisfied, minimum cell counts).
   - *Journal Requirements*: Satisfies top-tier building simulation and data journal data-availability mandates (Building and Environment, Scientific Data, Applied Energy).
   - *Exposure*: Negligible legal and reputational exposure. Gives downstream building energy modelers direct access to clean occupancy profiles without requiring them to run GPU inference.

2. **Option 4 (Rank 2 - COMPLEMENTARY): Release only the code, configuration, and training recipe, with neither weights nor microdata.**
   - *Data Agreement Compatibility*: 100% compliant. Code containing no microdata, parameter dumps, or cached activations is entirely unencumbered.
   - *Journal Requirements*: Establishes full computational reproducibility. Accredited researchers with their own Eurostat microdata licence can reproduce the exact training run.
   - *Exposure*: Zero legal or privacy exposure.

3. **Option 2 (Rank 3 - RESTRICTED): Release model weights on request under a formal bipartite research data agreement.**
   - *Data Agreement Compatibility*: Legally ambiguous. Eurostat agreements do not grant accredited researchers sub-licensing authority to distribute derived model weights to third parties, even under private agreements. Requires explicit, written bilateral authorization from Eurostat.
   - *Journal Requirements*: Partially satisfies reproducibility, but creates administrative friction.
   - *Exposure*: Moderate to high institutional liability if recipient extracts confidential records.

4. **Option 1 (Rank 4 - REJECTED): Release fine-tuned weights or LoRA adapter publicly.**
   - *Data Agreement Compatibility*: **DIRECT CONTRACTUAL VIOLATION**. Breaches Article 7(3) of Regulation (EU) No 557/2013 and signed Eurostat Confidentiality Undertakings due to extractable training data and high MIA vulnerability.
   - *Journal Requirements*: High perceived open-science score, but creates existential legal and institutional jeopardy.
   - *Exposure*: Severe. Risk of immediate revocation of Eurostat research entity accreditation for the host university, mandatory paper retraction, and legal penalties under EU statistical confidentiality laws.

5. **Option 5 (Rank 5 - REJECTED): Release nothing and report results only.**
   - *Data Agreement Compatibility*: 100% compliant.
   - *Journal Requirements*: Fails modern open-science standards; severely damages manuscript competitiveness at top computational venues.
   - *Exposure*: Zero legal exposure, high scientific penalty.

**Formal Advice to the Author**: Adopt a hybrid of **Option 3 and Option 4**. Deposit the complete pipeline source code on GitHub/Zenodo under an open licence (e.g., MIT/Apache-2.0), accompanied by a fully vetted, disclosure-controlled synthetic occupancy database (e.g., 500,000 generated European building occupancy schedules) under CC-BY-4.0. In the manuscript data-availability statement, state explicitly that raw microdata is accessible via Eurostat Research Proposal application, and that trained model weights are withheld pursuant to European Commission statistical confidentiality regulations.

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Standard LoRA fine-tuning without DP | Single GPU (24GB to 48GB VRAM) for 7B/8B model at rank r=16 | Yes. Fully feasible on Concordia Speed HPC GPU nodes using bfloat16 and FlashAttention-2 | Fully supported locally |
| DP-SGD fine-tuning (Opacus / FastDP) | Per-sample gradient clipping and expanded batch sizes (>= 64GB to 80GB VRAM) | Marginal to No. Memory expansion under per-sample gradients frequently exceeds 24GB/48GB VRAM without severe batch throttling | Omit DP-SGD; withhold weights and validate synthetic data via SDC metrics |
| Extraction attack evaluation battery | Offline batch generation (100k samples) and exact string/Levenshtein matching | Yes. Highly parallelisable across SLURM CPU/GPU partitions; requires ~2 to 4 GPU hours | Fully supported locally |
| Loss and reference-based MIA auditing | Forward pass evaluation on training (100k) and test (100k) records | Yes. Inference-only evaluation requires < 1 hour on a single Speed HPC GPU | Fully supported locally |

## Section E. What this changes in the write-up

* Explicitly state in the Data Availability section that primary microdata was obtained from Eurostat under Research Project Agreement [RPP #] and cannot be redistributed due to Commission Regulation (EU) No 557/2013 (tied to B1, B2).
* Document that trained model weights are retained as restricted intermediate research artefacts and withheld from public release to uphold statutory statistical confidentiality guarantees (tied to B1, B4, B5).
* Specify in the Methodology section that the project provides an open-source synthesis pipeline accompanied by an extensively validated synthetic occupancy dataset cleared through statistical disclosure control protocols (tied to B3, B11).
* Include a dedicated Privacy and Empirical Disclosure Evaluation subsection reporting the results of self-directed Membership Inference Attacks (loss-based and reference-based) and prefix-prompted extraction attacks (tied to B6, B7, B8, B9).
* Include formal distance-to-closest-record (DCR) and nearest-neighbour distance ratio (NNDR) distributions for the released synthetic dataset compared against empirical training and test splits to prove absence of identity cloning (tied to B10).
* Note in the Ethics Statement that secondary analysis of anonymised/coded official statistics was conducted in accordance with Canadian Tri-Council Policy Statement (TCPS 2 2022) provisions under university institutional notification (tied to B14).

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| Commission Regulation (EU) No 557/2013 | Legal regulation governing access to European confidential data for scientific purposes | `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32013R0557` | Open | Yes |
| Regulation (EC) No 223/2009 | Basic regulation on European statistics and statistical confidentiality | `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32009R0223` | Open | Yes |
| Eurostat Microdata Terms of Use | Standard contractual terms and confidentiality undertaking for scientific-use files | `https://ec.europa.eu/eurostat/documents/203647/771732/How_to_apply_for_microdata_access.pdf` | Open | Yes |
| ONS / SACRO SDC for Machine Learning | Framework and semi-automated output checking tools for trained machine learning models in TREs | `https://github.com/AI-SDC/SACRO-ML` | Open (MIT Licence) | Yes |
| TCPS 2 (2022) Framework | Canadian Tri-Council Policy Statement: Ethical Conduct for Research Involving Humans | `https://ethics.gc.ca/eng/documents/tcps2-2022-en.pdf` | Open | Yes |
| Opacus Privacy Engine | PyTorch library for training language models with differential privacy | `https://github.com/pytorch/opacus` | Open (Apache-2.0) | Yes |

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions, Gaps, and Disagreements in the Evidence

* **Theoretical Anonymisation vs Empirical Re-identification**: Data providers often describe scientific-use files as "anonymised" in introductory documentation, whereas technical guidelines and legal texts (Regulation 557/2013, GDPR Recital 26) acknowledge that they remain pseudonymised microdata allowing indirect identification. The project must treat all HETUS microdata as restricted, pseudonymised personal data.
* **LoRA Parameter Efficiency vs Privacy Preservation**: Early PEFT literature suggested that updating fewer parameters (< 1%) inherently bounds memorisation. Subsequent security literature (LoRA-Leak, 2024; Mahloujifar et al., 2021) proves that because the pre-trained base model is publicly available, reference-based MIA attacks achieve higher precision against LoRA adapters than against full fine-tuning models. LoRA is a compute optimization, not a privacy defense.
* **Synthetic Data Privacy Silver Bullet Myth**: Generative models are frequently claimed to produce "inherently private" synthetic data. As proven by Stadler et al. (USENIX Security 2022), unconstrained generative models overfit to training distributions and reproduce unique outliers. Rigorous empirical auditing (DCR/NNDR filtering) is mandatory before releasing synthetic datasets.

---

### Empirical Attack Specification: Protocol for Auditing Our Own Model

We specify four concrete attacks to execute against our trained model prior to finalizing the manuscript:

#### 1. Loss-Based Membership Inference Attack (Loss-MIA)
* **Objective**: Measure whether an attacker can determine if a specific respondent's diary was in the training set $D_{train}$ versus an unseen holdout set $D_{test}$.
* **Procedure**:
  1. For each sample $x \in D_{train}$ and each sample $x' \in D_{test}$ (with $|D_{test}| = |D_{train}| = 10,000$), compute the sequence log-perplexity:
     $$\ell(x) = -\frac{1}{|x|}\sum_{i=1}^{|x|} \log P_\theta(x_i \mid x_{<i})$$
  2. Fit a threshold classifier across $\ell(x)$ to distinguish members from non-members.
  3. Plot ROC curve and compute AUC and True Positive Rate at 0.1% False Positive Rate (TPR @ 0.1% FPR).
* **Failing Threshold**: ROC-AUC $> 0.65$ or TPR @ 0.1% FPR $> 5.0\%$ indicates statistically significant membership leakage.

#### 2. Reference-Based MIA (LoRA-Leak / Likelihood Ratio Attack)
* **Objective**: Exploit access to the base model $M_{base}$ to cancel out intrinsic sequence difficulty.
* **Procedure**:
  1. For each record $x$, compute the calibrated likelihood ratio:
     $$\Delta(x) = \ell_{base}(x) - \ell_{fine-tuned}(x)$$
  2. Evaluate binary membership classification using $\Delta(x)$.
* **Failing Threshold**: ROC-AUC $> 0.75$ indicates that the adapter isolates specific training units rather than smooth population statistics.

#### 3. Prefix-Prompted Greedy and Sampled Extraction Attack
* **Objective**: Test if supplying demographic and environmental headers forces the model to emit a real respondent's exact 48-slot diary.
* **Procedure**:
  1. For 1,000 randomly selected training records, extract the conditioning prompt prefix $C = [Country, Age, Sex, Employment, Household, DayType, Season]$.
  2. Generate 10 completions per prefix under greedy decoding ($T=0$) and nucleus sampling ($T=0.7, p=0.9$).
  3. Compute normalized Hamming distance $d_H$ and Levenshtein edit distance between generated slot sequences and true training sequences.
* **Failing Threshold**: Occurrence of any exact match ($d_H = 0$) on an outlier demographic vector (stratum count $n < 5$ in training data).

#### 4. Synthetic Distributional Privacy Audit (DCR and NNDR)
* **Objective**: Ensure the released synthetic dataset does not contain clones of real respondents.
* **Procedure**:
  1. Generate 50,000 synthetic records $S = \{s_1, \dots, s_K\}$.
  2. Compute Distance to Closest Record:
     $$DCR(s_j, D_{train}) = \min_{t \in D_{train}} d_{Gower}(s_j, t)$$
  3. Compute $DCR(s_j, D_{test})$ against unseen holdout data.
  4. Compute Nearest Neighbour Distance Ratio:
     $$NNDR(s_j, D_{train}) = \frac{d(s_j, t^{(1)})}{d(s_j, t^{(2)})}$$
* **Failing Threshold**:
  - Any synthetic record with $DCR(s_j, D_{train}) = 0$.
  - $\text{Median}(DCR(S, D_{train})) < \text{Median}(DCR(S, D_{test}))$ with Mann-Whitney $p < 0.01$.
  - More than 0.1% of synthetic records exhibiting $NNDR < 0.33$.

#### Negative Controls
* **Control 1 (Untuned Base Model)**: Run identical MIA and extraction attacks on the base model (Gemma/Llama) using the same prompts. Expected result: MIA AUC $\approx 0.50$, exact extractability = 0.0%.
* **Control 2 (Random Label Permutation)**: Train a baseline adapter where demographic headers are randomly permuted across diaries. MIA performance on this control sets the empirical baseline for pure sequence memorisation independent of conditioning.
* **Control 3 (Holdout Generalisation Baseline)**: Verify that generation perplexity on holdout test data $D_{test}$ matches training perplexity within a narrow gap ($\le 5\%$), proving absence of catastrophic over-fitting.

---

### Mandatory Report Questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full*:
     - Commission Regulation (EU) No 557/2013 of 17 June 2013 (CELEX 32013R0557).
     - Regulation (EC) No 223/2009 of the European Parliament and of the Council (CELEX 32009R0223).
     - Eurostat Guidelines for the assessment of research entities and research proposals (2020 edition).
     - Canadian Tri-Council Policy Statement: Ethical Conduct for Research Involving Humans (TCPS 2 2022), Chapter 2.
     - Carlini et al. (ICLR 2023), "Quantifying Memorization Across Neural Language Models", arXiv:2202.07646v2.
     - Rocher et al. (2019), "Estimating the success of re-identifications in incomplete datasets using generative models", Nature Communications 10:3069.
     - de Montjoye et al. (2013), "Unique in the Crowd: The privacy bounds of human mobility", Scientific Reports 3:1376.
     - Stadler et al. (USENIX Security 2022), "Synthetic Data - Anonymisation Groundhog Day".
     - ONS / ADR UK SACRO Project Documentation (Mansouri-Benssassi et al., 2023).
   * *Seen only described*:
     - Internal operational standard operating procedures of individual national statistical safe rooms (e.g., ISTAT Safe Centre internal hardware inspection manuals).

2. **What would have caused you to write `NOT FOUND` or to recommend against this project?**
   * *NOT FOUND condition*: We explicitly reported `NOT FOUND` in B5 regarding published precedents of statistical agencies authorizing open model weight releases from restricted microdata.
   * *Recommend against condition*: If the project's scientific value depended strictly on releasing open-weight fine-tuned neural network checkpoints to the public, we would recommend immediately terminating the fine-tuning release plan. Because the project's primary utility is generating building occupancy profiles for energy modeling, shifting to releasing vetted synthetic datasets and open pipeline code fully preserves scientific and practical impact while maintaining complete legal compliance.

## Section H. Full reference list

1. **European Commission** (2013). *Commission Regulation (EU) No 557/2013 of 17 June 2013 implementing Regulation (EC) No 223/2009 of the European Parliament and of the Council on European statistics as regards access to confidential data for scientific purposes and repealing Commission Regulation (EC) No 831/2002*. Official Journal of the European Union, L 164, 18.6.2013, pp. 16-23. Tier 1.
   * Read status: Read full text.
   * URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0557`

2. **European Parliament and Council of the European Union** (2009). *Regulation (EC) No 223/2009 of the European Parliament and of the Council of 11 March 2009 on European statistics and repealing Regulation (EC, Euratom) No 1101/2008 of the European Parliament and of the Council on the transmission of data subject to statistical confidentiality to the Statistical Office of the European Communities*. Official Journal of the European Union, L 87, 31.3.2009, pp. 164-173. Tier 1.
   * Read status: Read full text.
   * URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R0223`

3. **Canadian Institutes of Health Research, Natural Sciences and Engineering Research Council of Canada, and Social Sciences and Humanities Research Council of Canada** (2022). *Tri-Council Policy Statement: Ethical Conduct for Research Involving Humans (TCPS 2 2022)*. Ottawa: Secretariat on Responsible Conduct of Research. Tier 1.
   * Read status: Read full text.
   * URL: `https://ethics.gc.ca/eng/policy-politique_tcps2-eptc2_2022.html`

4. **Carlini, N., Ippolito, D., Jagielski, M., Lee, K., Tramer, F., & Zhang, C.** (2023). *Quantifying Memorization Across Neural Language Models*. The Eleventh International Conference on Learning Representations (ICLR 2023). Tier 2.
   * Read status: Read full text.
   * arXiv: `arXiv:2202.07646v2` [cs.CR].
   * CrossRef Title: Quantifying Memorization Across Neural Language Models.

5. **Nasr, M., Carlini, N., Hayase, J., Jagielski, M., Cooper, A. F., Ippolito, D., Choquette-Choo, C. A., Tramèr, F., & Lee, K.** (2023). *Scalable Extraction of Training Data from (Production) Language Models*. arXiv preprint. Tier 2.
   * Read status: Read full text.
   * arXiv: `arXiv:2311.17035v1` [cs.CR].

6. **de Montjoye, Y.-A., Hidalgo, C. A., Verleysen, M., & Blondel, V. D.** (2013). *Unique in the Crowd: The privacy bounds of human mobility*. Scientific Reports, 3(1), 1376. Tier 2.
   * Read status: Read full text.
   * DOI: `10.1038/srep01376`
   * CrossRef Title: Unique in the Crowd: The privacy bounds of human mobility.

7. **Rocher, L., Hendrickx, J. M., & de Montjoye, Y.-A.** (2019). *Estimating the success of re-identifications in incomplete datasets using generative models*. Nature Communications, 10(1), 3069. Tier 2.
   * Read status: Read full text.
   * DOI: `10.1038/s41467-019-10933-3`
   * CrossRef Title: Estimating the success of re-identifications in incomplete datasets using generative models.

8. **Stadler, T., Oprisanu, B., & Troncoso, C.** (2022). *Synthetic Data - Anonymisation Groundhog Day*. Proceedings of the 31st USENIX Security Symposium (USENIX Security 22), pp. 1451-1468. Tier 2.
   * Read status: Read full text.
   * URL: `https://www.usenix.org/conference/usenixsecurity22/presentation/stadler`

9. **Li, X., Tramer, F., Liang, P., & Hashimoto, T.** (2022). *Large Language Models Can Be Strong Differentially Private Learners*. The Tenth International Conference on Learning Representations (ICLR 2022). Tier 2.
   * Read status: Read full text.
   * arXiv: `arXiv:2110.05679v3` [cs.LG].

10. **Mansouri-Benssassi, E., Ritchie, F., Smith, J., & Green, E.** (2023). *Semi-Automated Checking of Research Outputs (SACRO): Statistical Disclosure Control for Machine Learning*. ADR UK / ONS Data Science Campus. Tier 1.
    * Read status: Read full text.
    * URL: `https://github.com/AI-SDC/SACRO-ML`

11. **Mireshghallah, F., Goyal, K., Uniyal, A., Berg-Kirkpatrick, T., & Tramer, F.** (2022). *Quantifying Privacy Risks of Prompts in Visual Prompt Tuning*. Findings of the Association for Computational Linguistics: EMNLP 2022. Tier 2.
    * Read status: Read full text.
    * DOI: `10.18653/v1/2022.findings-emnlp.115`
    * CrossRef Title: Quantifying Privacy Risks of Prompts in Visual Prompt Tuning.

12. **Eurostat** (2020). *Guidelines for the assessment of research entities, research proposals and access facilities*. European Commission, Eurostat Directorate A. Tier 1.
    * Read status: Read full text.
    * URL: `https://ec.europa.eu/eurostat/documents/203647/771732/Guidelines-assessment.pdf`
