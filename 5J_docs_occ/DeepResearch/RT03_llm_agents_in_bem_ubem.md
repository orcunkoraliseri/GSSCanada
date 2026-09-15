# RT03: LLM Agents in Building Performance Simulation and UBEM

## Section A. Direct answer

No Large Language Model (LLM) agent has driven an Urban Building Energy Model (UBEM) end-to-end with validation against measured or independently simulated ground truth. Across ten published or preprint agentic systems identified in the building performance simulation literature, none have evaluated district-scale models, and only one reached class (c) comparison against a human-built model, with zero systems reaching class (d) validation against measured empirical consumption data. The existing literature remains concentrated in qualitative proof-of-concept demonstrations and self-authored prompt success benchmarks for single-building EnergyPlus input files or localized HVAC controllers. For an open-weight agent operating within an 80 GB GPU ceiling, reliable tool use is feasible using modern 70B quantized or 32B dense models, but an agentic layer over OpenUBEM faces the devastating reviewer objection that it adds stochastic instability to an already deterministic, zero-parameter scripted pipeline.

---

## Section B. Findings table (Open-weight feasibility on one 80 GB GPU)

| # | Item / Dimension | Specification or Finding | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|
| B1 | Open-weight model: Qwen 2.5 (32B / 72B) | Qwen2.5-32B-Instruct fits unquantized in bfloat16 (~65 GB VRAM); Qwen2.5-72B-Instruct fits in 4-bit GPTQ/AWQ (~42 GB VRAM) on a single 80 GB A100 node. Native tool calling and JSON schema generation supported. Model card states: "Specialized in complex reasoning, structured JSON output, and multi-turn tool calling." Released September 2024. | Qwen Team (2024), Qwen2.5 Model Card, Hugging Face | Tier 1 | 2026-09-14 | High |
| B2 | Open-weight model: Meta Llama 3.1 / 3.3 (70B) | Llama-3.1-70B-Instruct and Llama-3.3-70B-Instruct fit on one 80 GB A100 with 4-bit quantization (~40 GB) or 8-bit quantization (~72 GB). Supports native function calling via `<|python_tag|>` special tokens. Released July/December 2024. | Meta AI (2024), Llama 3.1 Release Documentation | Tier 1 | 2026-09-14 | High |
| B3 | Open-weight model: Mistral NeMo (12B) / Small (22B) | Mistral NeMo 12B (Apache 2.0) and Mistral-Small-2409 (22B) fit comfortably in FP16 on 80 GB (<30 GB and <45 GB respectively). Feature native function calling via `[AVAILABLE_TOOLS]` syntax. | Mistral AI (2024), Mistral NeMo Release Notes | Tier 1 | 2026-09-14 | High |
| B4 | Local offline execution framework: vLLM | vLLM (v0.6.x+, checked 2026-09-14) runs fully offline on a single SLURM GPU node, exposes an OpenAI-compatible `/v1/chat/completions` API supporting structured outputs (guided decoding via Outlines) and function calling schemas. | vLLM Project Documentation | Tier 3 | 2026-09-14 | High |
| B5 | Local agent orchestration: LangGraph | LangGraph (v0.2.x+, checked 2026-09-14) supports cyclic graph-based multi-agent execution, deterministic state persistence, and human-in-the-loop validation gates without external network requests. | LangChain Inc. Documentation | Tier 3 | 2026-09-14 | High |
| B6 | Tool-calling capability gap: BFCL | On the Berkeley Function Calling Leaderboard (BFCL, August 2024 / ongoing leaderboard checked 2026-09-14), frontier proprietary models (GPT-4o, Claude 3.5 Sonnet) lead overall function-calling accuracy (~88% to 92%). Leading open-weight models (Qwen2.5-72B, Llama-3.1-70B) reach competitive accuracy (80% to 85%), while smaller open-weight models (8B to 14B) drop below 70%, failing disproportionately on multi-turn error recovery. | Gorilla LLM Project, UC Berkeley | Tier 3 | 2026-09-14 | High |
| B7 | Open-weight usage in building simulation | Jiang et al. (2024) evaluated a local open-weight model (fine-tuned T5-base). It achieved high syntax validity on seen templates but failed completely when prompted with novel architectural geometries. Most subsequent agentic BEM studies reverted to proprietary commercial APIs (GPT-4 / Claude). | Jiang et al. (2024), *Applied Energy* 367: 123431 | Tier 2 | 2026-09-14 | High |

---

## Section C. Landscape table (Prior agentic systems in building performance)

| # | System / Work (First author, year, venue) | Model used and open-weight status | Tools called | Simulation engine reached | Comparison to ground truth | Evaluation class (a/b/c/d) | Read level |
|---|---|---|---|---|---|---|---|
| C01 | EPlus-LLM (Jiang et al., 2024, *Appl. Energy*) | Fine-tuned T5 (Open-weight) + GPT-4 (Proprietary API) | Natural language parser, IDF syntax generator, EnergyPlus execution wrapper | EnergyPlus 9.5 | Compared generated single-zone models against reference DOE prototype IDFs for syntax and heating/cooling loads. | (c) Comparison against human-built model | Full text |
| C02 | Ten Questions Roadmap (Ma et al., 2026, *Build. Environ.*) | None (Conceptual review of LLM agent architectures) | None (Outlines potential tool use for EnergyPlus, OpenStudio, Modelica) | None (Conceptual review) | None | (a) Qualitative demonstration only | Full text |
| C03 | LLM Energy Applications Survey (Liu et al., 2025, *Build. Simul.*) | None (Literature review of LLM applications) | Examined API tool wrappers for BEM workflows | EnergyPlus, DOE-2 (Reviewed literature) | None | (a) Qualitative demonstration only | Abstract |
| C04 | BuildingGPT (Li et al., 2026, *Build. Environ.*) | GPT-4 / Graph RAG (Proprietary API) | BIM/IFC graph query engine, vector database retriever | None (IFC semantic data extraction) | Evaluated accuracy of building element and thermal property queries against ground-truth BIM models. | (b) Task success on author benchmark | Full text |
| C05 | Conversational Comfort Agent (Liu et al., 2026, *Energy Build.*) | Lightweight fine-tuned LLM (Open-weight, 7B) | Serial thermostat controller, comfort feedback parser | Experimental climate chamber HVAC | Compared room temperature to PMV setpoints; no annual simulation or metered stock data. | (b) Task success on author benchmark | Full text |
| C06 | AutoCoSim (Li et al., 2026, SSRN preprint) | Multi-agent LLM-RAG (GPT-4o) | Geometry meshing script, CFD wrapper, EnergyPlus runner | EnergyPlus + OpenFOAM CFD | Evaluated multi-agent execution success on co-simulation case study; no empirical sensor validation. | (b) Task success on author benchmark | Abstract |
| C07 | LLM-BEM (Liu et al., 2025, IEEE Conference) | Zero-shot LLM Agent (GPT-4) | Python simulation environment, load scheduler | Building energy simulator / microgrid model | Evaluated electricity cost reduction against rule-based baselines; simulated test case only. | (b) Task success on author benchmark | Abstract |
| C08 | Interpretable ML Control (Zhang et al., 2024, *Energy Build.*) | Large Language Model + Tree RL | Policy interpreter, HVAC supervisory controller | Building HVAC simulation environment | Evaluated energy consumption reduction and rule interpretability in simulated office zone. | (b) Task success on author benchmark | Full text |
| C09 | LLM Agent Schema (Zhang et al., 2025, ASHRAE Winter Conf.) | LLM Agent Framework | Function calling schema, BEM API wrapper | EnergyPlus | Evaluated structured JSON generation validity against ASHRAE BEM simulation schema. | (b) Task success on author benchmark | Abstract |
| C10 | Cost-Optimal Home Scheduling (Raghavan et al., 2025, *J. Build. Perform. Simul.*) | Zero-shot LLM Agent + Model Predictive Control | MPC optimization solver, appliance schedule parser | Residential building energy simulation model | Evaluated residential energy cost optimization across simulated variable tariff profiles. | (b) Task success on author benchmark | Abstract |

*Summary of Evaluation Rigour across the 10 systems:*
* Class (a) Qualitative demonstration only: 2 systems (20%)
* Class (b) Task success rate on author-made benchmark: 7 systems (70%)
* Class (c) Comparison against human-built reference model: 1 system (10%)
* Class (d) Comparison against measured empirical ground truth: 0 systems (0%)

---

## Section D. Gap and fit assessment

| Candidate angle | Is it unclaimed? | Assets used | Assets lacked | Reviewer's strongest objection | Effort |
|---|---|---|---|---|---|
| `A1` (Agentic UBEM) | **Yes**, entirely unclaimed at district/UBEM scale. No paper has demonstrated an LLM agent driving a multi-building UBEM engine end-to-end against measured stock data. | OpenUBEM engine, Concordia Speed HPC, validation discipline | Experience with agent frameworks (LangGraph); open-weight tool-use fine-tuning; real-time error-recovery wrappers | "The agent is an unnecessary, non-reproducible wrapper over a deterministic pipeline. What can an LLM do that an explicit Python configuration script with a YAML file cannot do faster, cheaper, and deterministically?" | 6 to 8 months |

---

## Section E. What an agent over a UBEM would have to prove

To publish an Agentic UBEM paper in *Energy and Buildings* or *Applied Energy* in 2027, an author must satisfy a significantly higher validation bar than the 2024-2025 exploratory papers:

1. **Rigorous Ablation against a Scripted Baseline:** The paper cannot merely demonstrate that an agent can execute a district simulation. It must run a head-to-head ablation: Agentic Pipeline versus Scripted Pipeline across identical districts. The evaluation must measure:
   * Wall-clock execution time and compute cost (GPU watt-hours per district).
   * Schema failure rate and syntax recovery rate.
   * Final Energy Use Intensity (EUI) accuracy against the unaugmented baseline.
2. **Evaluation Across Multiple Real Urban Districts:** The agent must be tested on diverse, real-world urban geometries (e.g., all four European districts in OpenUBEM: Madrid, Lyon, London, Bologna, plus US validation cells), not a single hand-crafted synthetic neighbourhood.
3. **Comparison Against Measured Ground Truth (Class d):** The simulated district outputs produced by the agent must be compared against actual metered utility data or calibrated stock benchmarks (e.g., the 12 US cities in OpenUBEM).
4. **Autonomous Error Recovery Under Adversarial Inputs:** The core claim of an "agent" is adaptive reasoning. The benchmark must deliberately introduce corrupted inputs (e.g., missing building heights, invalid OSM tags, non-convex polygons) and demonstrate that the agent autonomously inspects error logs, diagnoses EnergyPlus fatal crashes, repairs the IDF or archetype tier, and completes the run.
5. **The Strongest "Agent Adds Nothing" Argument:** The central objection that reviewers will raise is:
   > "Urban building energy modeling is a data-engineering problem requiring deterministic geometric operations, topological polygon clipping, and standardized lookup tables. Placing a non-deterministic, hallucinatory language model in the loop introduces run-to-run stochasticity, massive GPU overhead, and security/reliability risks without improving the thermodynamic fidelity of EnergyPlus."

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL / Access record | Access condition | Confirmed reachable? | Date checked |
|---|---|---|---|---|---|
| EPlus-LLM Publication Record | Applied Energy paper and computing platform details | `https://doi.org/10.1016/j.apenergy.2024.123431` | Open access / Elsevier | Yes | 2026-09-14 |
| BuildingGPT Publication Record | Building and Environment paper on vector-graph RAG for BIM | `https://doi.org/10.1016/j.buildenv.2025.113855` | Open access / Elsevier | Yes | 2026-09-14 |
| Berkeley Function Calling Leaderboard (BFCL) | Standardized evaluation dataset and leaderboard for LLM tool calling | `https://gorilla.cs.berkeley.edu/leaderboard.html` | Open | Yes | 2026-09-14 |
| vLLM Serving Framework | High-throughput offline LLM inference engine with guided JSON decoding | `https://github.com/vllm-project/vllm` | Open (Apache 2.0) | Yes | 2026-09-14 |
| LangGraph Framework | Cyclic agentic workflow orchestration library with state machine guards | `https://github.com/langchain-ai/langgraph` | Open (MIT) | Yes | 2026-09-14 |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### 1. Benchmark finding (Item 3)
* There is **no accepted community benchmark or shared task** for evaluating LLM agents on building energy simulation or urban building performance workflows.
* Searched: Papers with Code, Hugging Face Benchmarks, IBPSA conference proceedings, BuildSys archives, and Google Scholar using queries `("building energy modeling" OR "EnergyPlus" OR "UBEM") AND ("benchmark" OR "shared task") AND ("LLM" OR "agent")`.
* Closest existing analogues:
  * General software engineering benchmarks (e.g. SWE-bench), which evaluate Python bug fixing but have zero awareness of thermal building physics or EnergyPlus input formats.
  * Information extraction benchmarks on building codes, which evaluate regulatory text parsing but do not execute simulation engines.

### 2. Reproducibility finding (Item 5)
* Reporting of agent reproducibility in building simulation literature is **NOT FOUND**.
* Across the papers in Section C, run-to-run variance across repeated random seeds is virtually never reported. Authors routinely set `temperature = 0` and report a single trial as representative.
* When temperature is zero, open-weight models running on vLLM are largely deterministic on identical hardware, but batching concurrency and floating-point non-associativity on CUDA can still cause token divergence. No paper in the building literature has measured the distribution of simulated EUIs resulting from repeated agent invocations.

### 3. The "Agent Adds Nothing" argument
If OpenUBEM already features a rule-based archetype classifier, tiered geometric imputation, and zero fitted parameters, what does an agent actually do?
* If the agent merely translates "Simulate Lyon Croix-Rousse with modern heat pumps" into `python run_openubem.py --district lyon --hvac heat_pump`, it is an expensive command-line wrapper.
* An agent only provides measurable value if it acts as an **expert diagnostician**: reading EnergyPlus `.err` files, identifying why a zone failed to converge, adjusting time steps or solver tolerances, and reporting why an archetype gate was violated.

### 4. Negative controls
1. **Which specific documents were opened in full?**
   * *Opened in full:* Jiang et al. (2024), Ma et al. (2026), Li et al. (2026 BuildingGPT), Liu et al. (2026), Zhang et al. (2024).
   * *Read at abstract / repository level:* Liu et al. (2025), Li et al. (2026 AutoCoSim), Liu et al. (2025 LLM-BEM), Zhang et al. (2025), Raghavan et al. (2025).
2. **What would have caused NOT FOUND?** If no open-weight model had supported structured JSON tool calling, Section B would have declared offline open-weight tool use impossible. (Modern models like Qwen 2.5 and Llama 3.3 have solved native tool calling).
3. **Which candidate angles are taken?** Single-building natural-language IDF translation is taken by EPlus-LLM (Jiang et al., 2024). District-scale Agentic UBEM (`A1`) is completely untaken, but vulnerable to the "adds nothing" critique.
4. **Did you invent any paper or benchmark?** No. Every paper was verified against CrossRef with resolving DOI, and framework repositories were verified on GitHub.

---

## Section H. Full reference list

1. Jiang, G., Ma, Z., Zhang, L., Chen, J. (2024). EPlus-LLM: A large language model-based computing platform for automated building energy modeling. *Applied Energy*, 367: 123431. DOI: `10.1016/j.apenergy.2024.123431`. CrossRef verified title: "EPlus-LLM: A large language model-based computing platform for automated building energy modeling". [Tier 2; Read full text].
2. Li, H., et al. (2026). BuildingGPT: Query building semantic data using large language models and vector-graph retrieval-augmented generation. *Building and Environment*, 288: 113855. DOI: `10.1016/j.buildenv.2025.113855`. CrossRef verified title: "BuildingGPT: Query building semantic data using large language models and vector-graph retrieval-augmented generation". [Tier 2; Read full text].
3. Li, X., et al. (2026). AutoCoSim: An LLM-RAG-based Multi-agent Framework for Automating Building Energy and CFD Co-simulation. *SSRN Preprint*. DOI: `10.2139/ssrn.6172101`. CrossRef verified title: "AutoCoSim: An LLM-RAG-based Multi-agent Framework for Automating Building Energy and CFD Co-simulation". [Tier 2; Read abstract].
4. Liu, D., Zhou, X., Li, Y. (2026). Conversational preference learning for personalized thermal comfort control with a lightweight large language model. *Energy and Buildings*, 357: 117181. DOI: `10.1016/j.enbuild.2026.117181`. CrossRef verified title: "Conversational preference learning for personalized thermal comfort control with a lightweight large language model". [Tier 2; Read full text].
5. Liu, M., Zhang, L., Chen, J., Chen, W.-A., Yang, Z., Lo, L.J., Wen, J., O'Neill, Z. (2025). Large language models for building energy applications: Opportunities and challenges. *Building Simulation*, 18(2): 225-234. DOI: `10.1007/s12273-025-1235-9`. CrossRef verified title: "Large language models for building energy applications: Opportunities and challenges". [Tier 2; Read abstract].
6. Liu, Y., et al. (2025). LLM-BEM: Zero-shot LLM-Agent Scheduling for Smart Building Energy Management. *2025 IEEE 26th China Conference on System Simulation Technology and its Applications (CCSSTA)*. DOI: `10.1109/ieeeconf65522.2025.11137227`. CrossRef verified title: "LLM-BEM: Zero-shot LLM-Agent Scheduling for Smart Building Energy Management". [Tier 2; Read abstract].
7. Ma, N., Labib, R., Amor, R., Chong, A., Fan, C., Forth, K., Fu, X., Fuchs, S., Hong, T., Klimenkova, N., Koo, J., Li, S., McCullough, S.T., Park, J.Y., Shraga, R., Yoon, S., Zhang, L., Zhang, Y. (2026). Ten questions concerning Large Language Models (LLMs) for building applications. *Building and Environment*, 291: 114260. DOI: `10.1016/j.buildenv.2026.114260`. CrossRef verified title: "Ten questions concerning Large Language Models (LLMs) for building applications". [Tier 2; Read full text].
8. Meta AI (2024). Introducing Llama 3.1: Our most capable models to date. Meta AI Research Blog, July 23, 2024. URL: `https://ai.meta.com/blog/meta-llama-3-1/`. [Tier 1; Read documentation].
9. Qwen Team (2024). Qwen2.5: A Party of Foundation Models. Alibaba Cloud / QwenLM Blog, September 19, 2024. URL: `https://qwenlm.github.io/blog/qwen2.5/`. [Tier 1; Read documentation].
10. Raghavan, S., et al. (2025). Cost-optimal residential energy scheduling via a zero-shot LLM agent and model predictive control. *Journal of Building Performance Simulation*. DOI: `10.1080/19401493.2025.2605465`. CrossRef verified title: "Cost-optimal residential energy scheduling via a zero-shot LLM agent and model predictive control". [Tier 2; Read abstract].
11. Zhang, L., et al. (2024). Large language model-based interpretable machine learning control in building energy systems. *Energy and Buildings*, 319: 114278. DOI: `10.1016/j.enbuild.2024.114278`. CrossRef verified title: "Large language model-based interpretable machine learning control in building energy systems". [Tier 2; Read full text].
12. Zhang, L., et al. (2025). Large Language Model-Based Agent Schema and Library for Building Energy Analysis and Modeling. *2025 ASHRAE Winter Conference*. DOI: `10.63044/w25zha5`. CrossRef verified title: "Large Language Model-Based Agent Schema and Library for Building Energy Analysis and Modeling". [Tier 2; Read abstract].
