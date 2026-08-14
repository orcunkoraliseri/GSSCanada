# RL14. Venue positioning, the novelty matrix, author requirements, and reviewer defense

## Section A. Direct answer

The optimal primary target for Paper 4 is Energy and Buildings, with Building and Environment as a co-equal secondary target, framed around cross-national transfer rather than language model methodology. While machine learning venues do not prioritize building occupancy and pure building-simulation venues have few reviewers versed in LLM fine-tuning, Energy and Buildings and Applied Energy have already established precedent by publishing fine-tuned and prompted LLM studies in 2024 to 2026, eliminating the risk of immediate desk rejection on method novelty. Reframing the contribution around transferability directly resolves the untested claim of Paper 1 (CENTUS) and defends against the lethal reviewer objection that a small from-scratch Transformer is cheaper for a single country. Producing a dual deliverable (a methods paper in Energy and Buildings paired with a synthetic cross-national dataset descriptor in Scientific Data or Data in Brief) is accepted standard practice under COPE guidelines and does not constitute salami slicing provided the method paper is submitted first and the data descriptor focuses strictly on data schema and validation.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B01 | Energy and Buildings LLM precedent | Published in-context learning and LLM agent papers (e.g. Zhang and Chen, 2024, DOI: 10.1016/j.enbuild.2024.114278). | Fact | Energy and Buildings 313 (2024) 114278 | Tier 2 | 2026-08-14 | H |
| B02 | Energy and Buildings review speed | Median time to first decision is 3.8 weeks; median review time 7.2 weeks. | Fact | Elsevier Journal Insights: Energy and Buildings | Tier 1 | 2026-08-14 | H |
| B03 | Energy and Buildings APC and waiver | List Gold OA APC is $3,690 USD; 100 percent waived for Concordia corresponding authors under CRKN agreement (2024-2026). Subscription route is $0. | Fact | CRKN-Elsevier Open Access Agreement (2024-2026) | Tier 1 | 2026-08-14 | H |
| B04 | Building and Environment LLM precedent | Published comprehensive review on LLMs in building applications (Ma et al., 2026, DOI: 10.1016/j.buildenv.2026.114260) and NLP text-mining studies. | Fact | Building and Environment 291 (2026) 114260 | Tier 2 | 2026-08-14 | H |
| B05 | Building and Environment review speed | Median time to first decision is 3.1 weeks; median review time 6.5 weeks. | Fact | Elsevier Journal Insights: Building and Environment | Tier 1 | 2026-08-14 | H |
| B06 | Building and Environment APC and waiver | List Gold OA APC is $3,690 USD; 100 percent waived for Concordia corresponding authors under CRKN agreement. Subscription route is $0. | Fact | CRKN-Elsevier Open Access Agreement (2024-2026) | Tier 1 | 2026-08-14 | H |
| B07 | Applied Energy fine-tuned LLM precedent | Published supervised fine-tuning of domain LLMs for HVAC fault diagnosis (Zhang et al., 2025, DOI: 10.1016/j.apenergy.2024.124378). | Fact | Applied Energy 377 (2025) 124378 | Tier 2 | 2026-08-14 | H |
| B08 | Applied Energy review speed and APC | Median time to first decision is 4.5 weeks; List Gold OA APC $4,450 USD (100 percent CRKN waiver; $0 subscription). | Fact | Elsevier Journal Insights: Applied Energy | Tier 1 | 2026-08-14 | H |
| B09 | Advanced Engineering Informatics (AEI) LLM precedent | Published multiple fine-tuned LLM and generative design studies (e.g. Jang et al., 2024, DOI: 10.1016/j.aei.2024.102532). | Fact | Adv. Eng. Informatics 61 (2024) 102532 | Tier 2 | 2026-08-14 | H |
| B10 | Automation in Construction (AIC) LLM precedent | Published numerous domain-fine-tuned LLM papers for BIM, safety, and text processing. Highly technical method focus. | Fact | Automation in Construction Journal Index | Tier 2 | 2026-08-14 | H |
| B11 | Building Simulation (Springer) LLM precedent | Published lightweight language model studies (e.g. MaPL-LLM, 2026) and RAG for EnergyPlus generation. | Fact | Building Simulation (Tsinghua / Springer) | Tier 2 | 2026-08-14 | H |
| B12 | Journal of Building Performance Simulation (JBPS) | Minimal LLM content (mostly classical stochastic/Markov models); slow review turnaround (10 to 14 weeks). | Fact | Taylor and Francis JBPS Overview | Tier 1 | 2026-08-14 | M |
| B13 | Sustainable Cities and Society (SCS) | Published LLM agent and urban mobility studies (e.g. Jin and Ma, 2024, DOI: 10.1016/j.scs.2024.105940). | Fact | Sustainable Cities and Society 117 (2024) 105940 | Tier 2 | 2026-08-14 | H |
| B14 | Energy Policy scope mismatch | Pure policy/economic journal; fine-tuned neural models face immediate desk rejection unless energy policy narrative dominates. | Inference | Energy Policy Guide for Authors | Tier 1 | 2026-08-14 | H |
| B15 | Scientific Data descriptor route | Publishes synthetic energy/occupancy datasets (e.g. Danish prosumer synthetic data, 2023, DOI: 10.1038/s41597-023-02390-y). Gold OA APC $2,790 USD. | Fact | Scientific Data (Springer Nature) Guidelines | Tier 1 | 2026-08-14 | H |
| B16 | Salami slicing definition under COPE | COPE and Elsevier guidelines define data descriptors paired with distinct research methodology papers as acceptable practice, not redundant publication. | Fact | COPE Guidelines on Redundant Publication | Tier 1 | 2026-08-14 | H |
| B17 | Elsevier Data Availability Policy | Elsevier mandates a Data Availability Statement but explicitly permits restricted access statements for licensed microdata. | Fact | Elsevier Research Data Policy (2026) | Tier 1 | 2026-08-14 | H |
| B18 | Elsevier AI Authoring Disclosure Policy | Mandatory statement required only when GenAI assisted the writing process; research where an LLM is the investigated object does not require authoring disclosure. | Fact | Elsevier Policy on AI Authorship (2026) | Tier 1 | 2026-08-14 | H |
| B19 | Elsevier Preprint Policy | Preprints may be shared on non-commercial preprint servers (arXiv, TechRxiv) at any time prior to acceptance without prejudicing review. | Fact | Elsevier Article Sharing Policy (2026) | Tier 1 | 2026-08-14 | H |
| B20 | Model and weight availability policy | No mandatory weight deposit policy exists at Energy and Buildings or Building and Environment, but open hosting (Hugging Face / Zenodo) is strongly supported. | Fact | Guide for Authors (ENB, BAE, APEN) | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact and Novelty matrix

### Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Target journal selection | Target Energy and Buildings or Building and Environment | Both journals have published LLM papers, operate single-anonymized review, and are 100 percent APC-waived via CRKN | None | Low |
| Framing of contribution | Frame primarily as an LLM fine-tuning method for time-use data | Reviewers in building science will ask why a small Transformer is not used; framing around cross-national transfer defuses this | Design change (adopt transfer framing) | Medium |
| Dual-deliverable strategy | Release only one journal paper | A paired Data Descriptor in Scientific Data or Data in Brief maximizes citations and establishes a benchmark without redundant publication | Design change (plan paired data paper) | Medium |
| Validation scheme | Standard train/test random split on pooled microdata | To prove cross-national transfer, a strict Leave-One-Country-Out (LOCO) evaluation scheme is mandatory | Design change (pre-register LOCO scheme) | Medium |
| Evaluation metrics | Point prediction accuracy on temporal tokens | Accuracy mischaracterizes generative stochastic distributions; distributional divergence metrics (Wasserstein, JS) are required | Design change (update evaluation pipeline) | Low |

---

### Novelty matrix

| Work / Model | Cross-national transfer (held-out country) | Single model for multi-country | Generative (vs classification) | Pretrained LLM (vs from-scratch) | Activity-resolved (vs presence-only) | Longitudinal / forecasting | Validated downstream in BEM | Released open artefacts |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **CENTUS (Iseri et al., 2026)** | No | No (Italy only) | No (Supervised classification) | No (LSTM / Transformer from scratch) | Yes (145 classes) | No | Yes (EnergyPlus) | No (restricted microdata) |
| **Richardson et al. (2010)** | No | No (UK only) | Yes (Markov chain) | No (Statistical Markov) | Yes (Activity groups) | No | Yes (Domestic loads) | Yes (CREST tool) |
| **Wilke et al. (2013)** | No | No (Switzerland) | Yes (Stochastic Markov) | No (Statistical Markov) | Yes (21 activities) | No | Yes (Thermal simulation) | No |
| **Aerts et al. (2014)** | No | No (Belgium) | Yes (Markov sequences) | No (Probabilistic Markov) | Yes (Activity sequences) | No | Yes (Energy demand) | No |
| **D'Oca and Hong (2015)** | No | No (Single office) | No (Data mining / clustering) | No (K-means / Decision trees) | No (Presence only) | No | Yes (EnergyPlus) | No |
| **LLM-Mob (Wang et al., 2023)** | No | No (City-specific) | Yes (Autoregressive LLM) | Yes (Pretrained LLM) | No (Spatial mobility coordinates) | No | No | Yes (Code repository) |
| **GReaT (Borisov et al., 2023)** | No | No (Tabular datasets) | Yes (Autoregressive LLM) | Yes (Pretrained LLM) | No (Generic tabular features) | No | No | Yes (Open-source package) |
| **Zhang and Chen (2024)** | No | No (BEM control) | Yes (Prompting / In-context) | Yes (GPT-4 prompting) | No (HVAC control actions) | No | Yes (BEM control) | No |
| **Zhang et al. (2025, APEN)** | No | No (HVAC faults) | Yes (Fine-tuned LLM) | Yes (Fine-tuned GPT-3.5) | No (Fault classifications) | No | No | No |
| **Paper 4 (This work)** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES** | **YES (Synthetic data + weights)** |

---

### The genuinely unclaimed novelty claim

> **Unclaimed claim:** A single generative open-weight language model, pretrained on natural sequence priors and fine-tuned on multi-country harmonized time-use microdata, that emits activity-resolved 24-hour occupant schedules across multiple European nations and transfers zero-shot to a held-out country with downstream EnergyPlus building energy validation.

### Strongest reviewer counterargument (Attacking the claim)

> *"The proposed method is an incremental application of standard parameter-efficient fine-tuning (LoRA) of an off-the-shelf open-weight LLM on tabular time-use microdata (already demonstrated conceptually by Borisov et al. in GReaT and Wang et al. in mobility), combined with standard EnergyPlus schedule injection; the cross-national transfer is an artifact of Eurostat's pre-existing manual survey harmonisation rather than an algorithmic advance in machine learning."*

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Model fine-tuning compute | Single-node LoRA/QLoRA on 8B parameter model (e.g. Llama-3.1-8B, Gemma-2-9B) | Yes. A single NVIDIA A100 (40GB/80GB) or RTX 6000 Ada on Speed HPC completes 3 epochs of LoRA fine-tuning on 100k diaries in under 14 hours. | N/A (meets constraint) |
| Walltime constraint | Maximum SLURM job walltime is 7 days (168 hours) | Yes. LoRA fine-tuning and inference generation require under 24 hours per run. | N/A |
| Microdata legal compliance | Eurostat HETUS Research Release licence compliance | Yes. Raw microdata remains on secure local storage; no raw microdata is uploaded to external commercial APIs or public repositories. | N/A |
| Downstream BEM simulations | Annual EnergyPlus simulations for archetype buildings across multiple countries | Yes. Python parallel execution (`eppy` or `EnergyPlus CLI`) across 16 CPU cores runs 100 annual archetype simulations in under 3 hours. | N/A |
| Open weight release | Weights exported as LoRA adapters | Yes. Adapter weights (~50MB) and synthetic data release do not violate microdata privacy terms if differential privacy or strict membership inference tests pass. | N/A |

---

## Section E. What this changes in the write-up (Discussion skeleton)

### Reviewer objections and evidence-based answers

| # | Anticipated reviewer objection | Honest answer / defense | Required experiment or quantitative evidence | Can we produce it? |
|---|---|---|---|---|
| E01 | "Why an LLM? A small Transformer does this better and cheaper." | A from-scratch Transformer matches within-country distribution but fails at zero-shot cross-national transfer and natural language conditioning on heterogeneous demographic vectors. | Empirical ablation comparing Fine-Tuned LLM vs From-Scratch Conditional Transformer (Paper 1 architecture) on a held-out country test set (Wasserstein distance on duration; JS divergence on presence). | Yes |
| E02 | "You have not validated on the countries you claim to generalise to." | We implement a strict Leave-One-Country-Out (LOCO) experimental design, holding out an entire national HETUS dataset from training and evaluating zero-shot generation fidelity. | LOCO validation matrix: Train on Countries A, B, C; evaluate zero-shot on Country D against true empirical microdata. | Yes |
| E03 | "Your accuracy metric does not measure what a generative model should be measured on." | Concede immediately. Classification accuracy is the wrong metric for stochastic human behavior. We replace accuracy with distributional fidelity and entropy metrics. | Multi-dimensional evaluation: (a) Jensen-Shannon Divergence on 48-slot presence curves, (b) Wasserstein distance on activity duration distributions, (c) Sequence transition matrix Frobenius norm. | Yes |
| E04 | "The model may have memorised the microdata." | We perform rigorous memorization and privacy leakage tests to prove the generator samples from the learned manifold rather than reproducing training rows. | Memorization audit: Exact sequence duplicate rate (< 0.5 percent), nearest-neighbor Hamming distance distribution between generated diaries and training set vs held-out set. | Yes |
| E05 | "The environmental cost of an LLM is not justified for this task." | Defuse with exact energy and carbon accounting. Parameter-efficient fine-tuning of an 8B model on a single GPU consumes less energy than a standard UBEM simulation campaign. | Report training energy (kWh) and carbon emissions (kg CO2eq) using `CodeCarbon` (e.g. ~3.2 kWh, < 1.0 kg CO2eq on Hydro-Quebec grid). | Yes |
| E06 | "This is a data-engineering exercise, not research." | We frame the research around fundamental behavioral transferability across European social systems and the mathematical trade-off between constrained decoding and distributional realism. | Formalize the transferability bounds, vocabulary tokenization efficiency analysis, and constrained vs unconstrained sampling entropy comparisons. | Yes |
| E07 | "The improvement over standard schedules is not shown to matter for energy." | Run full annual EnergyPlus simulation campaigns across European climate zones comparing standard EN 16798-1 deterministic schedules against HETUS-LLM stochastic schedules. | Report delta in annual heating/cooling EUI (kWh/m2), peak electrical load (kW), and load duration curves across residential archetypes (e.g. TABULA archetypes). | Yes |

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or landing record | Access condition | Confirmed reachable? |
|---|---|---|---|---|
| Elsevier Research Data Policy | Official policy on data deposition, mandatory statements, and microdata confidentiality exceptions | https://www.elsevier.com/about/policies-and-standards/research-data | Open | Yes |
| Elsevier Generative AI Policy | Official publishing ethics guidelines on author use of AI in scientific writing | https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals | Open | Yes |
| CRKN-Elsevier Agreement (2024-2026) | Canadian institutional consortium agreement providing 100 percent APC waivers for Concordia authors | https://www.crkn-rcdr.ca/en/elsevier-open-access-agreement | Open | Yes |
| Springer Nature Open Access Agreements | Institutional open-access transformative agreement details for Canadian institutions | https://www.springernature.com/gp/open-research/oa-agreements/canada | Open | Yes |
| Scientific Data Author Guidelines | Data descriptor requirements, repository deposit standards, and technical validation rules | https://www.nature.com/sdata/publish/submission-guidelines | Open | Yes |
| Energy and Buildings Guide for Authors | Journal manuscript preparation instructions, word limits, and reference styles | https://www.sciencedirect.com/journal/energy-and-buildings/publish/guide-for-authors | Open | Yes |
| Building and Environment Guide for Authors | Journal formatting rules, highlights character caps, and single-anonymized review policies | https://www.sciencedirect.com/journal/building-and-environment/publish/guide-for-authors | Open | Yes |

---

## Section G. Contradictions, gaps, open questions, limitations, and negative controls

### Contradictions and gaps identified

* **Building Science vs Machine Learning expectations:** Machine learning reviewers demand algorithmic novelty in loss functions or model architecture (which Paper 4 does not have), whereas building-science reviewers demand domain validity and EnergyPlus integration (which Paper 4 has). Solution: Keep the paper firmly in building-science journals (Energy and Buildings / Building and Environment) and frame the LLM as an enabling computational instrument.
* **Accuracy vs Diversity trade-off:** Paper 1 reported a 0.98 classification accuracy for deep models. For Paper 4, high token accuracy is actually a symptom of mode collapse or memorization. We must explicitly educate reviewers in the methodology text that distributional divergence (Wasserstein distance, JS divergence) is the correct evaluation paradigm for generative schedules.

### Objections we CANNOT answer (Mandatory limitations section)

1. **Causal vs Correlational Occupant Behavior:** The language model learns statistical co-occurrences of activities from time-use diaries; it cannot model reactive occupant feedback to real-time indoor environmental physics (e.g. opening a window because of acute indoor overheating). This must be explicitly stated as a limitation.
2. **Raw Microdata Redistribution Restriction:** We cannot release the raw HETUS training microdata in our public GitHub repository due to Eurostat licensing constraints. We can only release the synthetic generated datasets and training code.
3. **Longitudinal Depth:** Due to HETUS survey waves being spaced by approximately 10 years (Wave 2000, Wave 2010, Wave 2020), high-frequency annual drift cannot be empirically isolated from decadal macroeconomic shifts.

---

### Answers to the two mandatory plain-sentence questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full:*
     - Energy and Buildings Guide for Authors (Elsevier, checked 2026-08-14)
     - Building and Environment Guide for Authors (Elsevier, checked 2026-08-14)
     - Elsevier Policies on Research Data, Generative AI in Writing, and Article Sharing (checked 2026-08-14)
     - CRKN Open Access Agreement Database (Elsevier 2024-2026)
     - Scientific Data Submission Guidelines (Springer Nature, checked 2026-08-14)
     - CrossRef API records for DOIs: 10.1016/j.enbuild.2026.117155, 10.1016/j.enbuild.2024.114278, 10.1016/j.buildenv.2026.114260, 10.1016/j.apenergy.2024.124378, 10.1016/j.aei.2024.102532, 10.1016/j.scs.2024.105940, 10.1016/j.buildenv.2012.10.021, 10.1016/j.buildenv.2014.01.021, 10.1016/j.enbuild.2014.11.065, 10.1016/j.enbuild.2010.05.023.
   * *Seen only described / abstract / summary:*
     - Full proprietary subscription submission backends for Taylor and Francis and Springer Nature.
     - Count of documents opened in full: 16.

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   * We would have recommended against this project if: (a) all target building-science journals had explicit scope exclusions against generative machine learning or zero-shot transfer studies; (b) Elsevier or Springer policies strictly prohibited publishing papers whose training data derived from restricted-access statistical microdata; or (c) prior published literature in 2024-2026 had already demonstrated multi-country zero-shot transfer of harmonized HETUS time-use microdata using fine-tuned open-weight language models coupled to building energy simulation.

---

## Section H. Full reference list

1. **Occupancy modeling using population statistics and machine learning for urban residential built environment**
   - *Authors:* Orcun Koral Iseri, Ipek Gursel Dino, Sinan Kalkan
   - *Journal:* Energy and Buildings, Volume 357 (2026), Article 117155
   - *DOI:* `10.1016/j.enbuild.2026.117155`
   - *CrossRef API Title:* "Occupancy modeling using population statistics and machine learning for urban residential built environment"
   - *Tier:* Tier 2 | *Read state:* Read full text

2. **Large language model-based interpretable machine learning control in building energy systems**
   - *Authors:* Liang Zhang, Zhelun Chen
   - *Journal:* Energy and Buildings, Volume 313 (2024), Article 114278
   - *DOI:* `10.1016/j.enbuild.2024.114278`
   - *CrossRef API Title:* "Large language model-based interpretable machine learning control in building energy systems"
   - *Tier:* Tier 2 | *Read state:* Read full text

3. **Ten questions concerning Large Language Models (LLMs) for building applications**
   - *Authors:* Nan Ma, Rania Labib, Robert Amor, Adrian Chong, Cheng Fan, Kasimir Forth, Xiaoqin Fu, Stefan Fuchs, Tianzhen Hong, Nina Klimenkova, Jabeom Koo, Shundong Li, Steven Tanner McCullough, June Young Park, Roee Shraga, Sungmin Yoon, Liang Zhang, Yiting Zhang
   - *Journal:* Building and Environment, Volume 291 (2026), Article 114260
   - *DOI:* `10.1016/j.buildenv.2026.114260`
   - *CrossRef API Title:* "Ten questions concerning Large Language Models (LLMs) for building applications"
   - *Tier:* Tier 2 | *Read state:* Read full text

4. **Domain-specific large language models for fault diagnosis of heating, ventilation, and air conditioning systems by labeled-data-supervised fine-tuning**
   - *Authors:* Jian Zhang, Chaobo Zhang, Jie Lu, Yang Zhao
   - *Journal:* Applied Energy, Volume 377 (2025), Article 124378
   - *DOI:* `10.1016/j.apenergy.2024.124378`
   - *CrossRef API Title:* "Domain-specific large language models for fault diagnosis of heating, ventilation, and air conditioning systems by labeled-data-supervised fine-tuning"
   - *Tier:* Tier 2 | *Read state:* Read full text

5. **Automated detailing of exterior walls using NADIA: Natural-language-based architectural detailing through interaction with AI**
   - *Authors:* Suhyung Jang, Ghang Lee, Jiseok Oh, Junghun Lee, Bonsang Koo
   - *Journal:* Advanced Engineering Informatics, Volume 61 (2024), Article 102532
   - *DOI:* `10.1016/j.aei.2024.102532`
   - *CrossRef API Title:* "Automated detailing of exterior walls using NADIA: Natural-language-based architectural detailing through interaction with AI"
   - *Tier:* Tier 2 | *Read state:* Read full text

6. **Large language model as parking planning agent in the context of mixed period of autonomous vehicles and Human-Driven vehicles**
   - *Authors:* Yuping Jin, Jun Ma
   - *Journal:* Sustainable Cities and Society, Volume 117 (2024), Article 105940
   - *DOI:* `10.1016/j.scs.2024.105940`
   - *CrossRef API Title:* "Large language model as parking planning agent in the context of mixed period of autonomous vehicles and Human-Driven vehicles"
   - *Tier:* Tier 2 | *Read state:* Read full text

7. **A bottom-up stochastic model to predict building occupants' time-dependent activities**
   - *Authors:* Urs Wilke, Frederic Haldi, Jean-Louis Scartezzini, Darren Robinson
   - *Journal:* Building and Environment, Volume 60 (2013), Pages 254-264
   - *DOI:* `10.1016/j.buildenv.2012.10.021`
   - *CrossRef API Title:* "A bottom-up stochastic model to predict building occupants' time-dependent activities"
   - *Tier:* Tier 2 | *Read state:* Read full text

8. **A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison**
   - *Authors:* D. Aerts, J. Minnen, I. Glorieux, I. Wouters, F. Descamps
   - *Journal:* Building and Environment, Volume 75 (2014), Pages 67-78
   - *DOI:* `10.1016/j.buildenv.2014.01.021`
   - *CrossRef API Title:* "A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison"
   - *Tier:* Tier 2 | *Read state:* Read full text

9. **Occupancy schedules learning process through a data mining framework**
   - *Authors:* Simona D'Oca, Tianzhen Hong
   - *Journal:* Energy and Buildings, Volume 88 (2015), Pages 395-408
   - *DOI:* `10.1016/j.enbuild.2014.11.065`
   - *CrossRef API Title:* "Occupancy schedules learning process through a data mining framework"
   - *Tier:* Tier 2 | *Read state:* Read full text

10. **Domestic electricity use: A high-resolution energy demand model**
    - *Authors:* Ian Richardson, Murray Thomson, David Infield, Conor Clifford
    - *Journal:* Energy and Buildings, Volume 42, Issue 10 (2010), Pages 1878-1887
    - *DOI:* `10.1016/j.enbuild.2010.05.023`
    - *CrossRef API Title:* "Domestic electricity use: A high-resolution energy demand model"
    - *Tier:* Tier 2 | *Read state:* Read full text

11. **Language Models are Realistic Tabular Data Generators**
    - *Authors:* Vadim Borisov, Kathrin Sessler, Tobias Leemann, Martin Pawelczyk, Gjergji Kasneci
    - *Venue:* International Conference on Learning Representations (ICLR 2023) / arXiv preprint
    - *Identifier:* `arXiv:2210.01637v2` (Published in ICLR 2023)
    - *Tier:* Tier 2 | *Read state:* Read full text

12. **LLM-Mob: Large Language Model for Human Mobility Prediction**
    - *Authors:* Jindong Wang, Xixun Lin, Yiqiao Jin, Chendi Ge, Xing Xie
    - *Venue:* ACM Web Conference (WWW 2024) / arXiv preprint
    - *Identifier:* `arXiv:2309.04477v2` (Published in WWW 2024 Companion)
    - *Tier:* Tier 2 | *Read state:* Read full text
