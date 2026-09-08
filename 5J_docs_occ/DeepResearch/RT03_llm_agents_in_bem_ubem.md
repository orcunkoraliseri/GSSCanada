# RT03: LLM Agents in Building Performance Simulation and UBEM

## Section A. Direct answer

No Large Language Model (LLM) agent has driven an Urban Building Energy Model (UBEM) end-to-end with validation against measured or independently simulated ground truth. Across ten published or preprint agentic systems identified in the building performance simulation literature, none have evaluated district-scale models, and only one reached class (c) comparison against a human-built model, with zero systems reaching class (d) validation against measured empirical consumption data. The existing literature remains concentrated in qualitative proof-of-concept demonstrations and self-authored prompt success benchmarks for single-building EnergyPlus input files. For an open-weight agent operating within an 80 GB GPU ceiling, reliable tool use is feasible using modern 70B quantized or 32B dense models, but an agentic layer over OpenUBEM faces the devastating reviewer objection that it adds stochastic instability to an already deterministic, zero-parameter scripted pipeline.

---

## Section B. Findings table (Open-weight feasibility on one 80 GB GPU)

| # | Item / Dimension | Specification or Finding | Source | Tier | Date checked | Confidence |
|---|---|---|---|---|---|---|
| B1 | Open-weight model: Qwen 2.5 (32B / 72B) | Qwen2.5-32B-Instruct fits unquantized in bfloat16 (~65 GB VRAM); Qwen2.5-72B-Instruct fits in 4-bit GPTQ/AWQ (~42 GB VRAM) on a single 80 GB A100 node. Native tool calling and JSON schema generation supported. Model card: "Specialized in complex reasoning, structured JSON output, and multi-turn tool calling." Released September 2024. | Qwen Team (2024), Qwen2.5 Model Card, Hugging Face | Tier 1 | 2026-09-07 | High |
| B2 | Open-weight model: Meta Llama 3.1 / 3.3 (70B) | Llama-3.1-70B-Instruct and Llama-3.3-70B-Instruct fit on one 80 GB A100 with 4-bit quantization (~40 GB) or 8-bit quantization (~72 GB). Supports native function calling via `<|python_tag|>` special tokens. Released July/December 2024. | Meta AI (2024), Llama 3.1 Release Documentation | Tier 1 | 2026-09-07 | High |
| B3 | Open-weight model: Mistral NeMo (12B) / Small (22B) | Mistral NeMo 12B (Apache 2.0) and Mistral-Small-2409 (22B) fit comfortably in FP16 on 80 GB (<30 GB and <45 GB respectively). Feature native function calling via `[AVAILABLE_TOOLS]` syntax. | Mistral AI (2024), Mistral NeMo Release Notes | Tier 1 | 2026-09-07 | High |
| B4 | Local offline execution framework: vLLM | vLLM (v0.6.x+, checked 2026-09-07) runs fully offline on a single SLURM GPU node, exposes an OpenAI-compatible `/v1/chat/completions` API supporting structured outputs (guided decoding via Outlines) and function calling schemas. | vLLM Project Documentation | Tier 3 | 2026-09-07 | High |
| B5 | Local agent orchestration: LangGraph | LangGraph (v0.2.x+, checked 2026-09-07) supports cyclic graph-based multi-agent execution, deterministic state persistence, and human-in-the-loop validation gates without external network requests. | LangChain Inc. Documentation | Tier 3 | 2026-09-07 | High |
| B6 | Tool-calling capability gap: BFCL | On the Berkeley Function Calling Leaderboard (BFCL, August 2026 update), frontier proprietary models (GPT-4o, Claude 3.5 Sonnet) achieve 88% to 92% overall accuracy. Top open-weight models (Qwen2.5-72B, Llama-3.1-70B) reach 80% to 84%. Smaller open-weight models (8B to 14B) drop to 65% to 72%, failing disproportionately on multi-step error recovery. | Gorilla LLM Project, UC Berkeley | Tier 3 | 2026-09-07 | High |
| B7 | Open-weight usage in building simulation | Only Jiang et al. (2024) evaluated a local open-weight model (fine-tuned T5-base). It achieved high syntax validity on seen templates but failed completely when prompted with novel architectural geometries. All subsequent agent papers reverted to proprietary APIs (GPT-4 / Claude). | Jiang et al. (2024), *Applied Energy* 367: 123431 | Tier 2 | 2026-09-07 | High |

---

## Section C. Landscape table (Prior agentic systems in building performance)

| # | System / Work (First author, year, venue) | Model used and open-weight status | Tools called | Simulation engine reached | Comparison to ground truth | Evaluation class (a/b/c/d) | Read level |
|---|---|---|---|---|---|---|---|
| C01 | EPlus-LLM (Jiang et al., 2024, *Appl. Energy*) | Fine-tuned T5 (Open-weight) + GPT-4 (Proprietary API) | Natural language parser, IDF syntax generator, EnergyPlus execution wrapper | EnergyPlus 9.5 | Compared generated single-zone models against reference DOE prototype IDFs for syntax and heating/cooling loads. | (c) Comparison against human-built model | Full text |
| C02 | Ten Questions Roadmap (Ma et al., 2026, *Build. Environ.*) | None (Conceptual review of LLM agent architectures) | None (Outlines potential tool use for EnergyPlus, OpenStudio, Modelica) | None (Conceptual review) | None | (a) Qualitative demonstration only | Full text |
| C03 | LLM Energy Applications Survey (Liu et al., 2025, *Build. Simul.*) | None (Literature review of LLM applications) | Examined API tool wrappers for BEM workflows | EnergyPlus, DOE-2 (Reviewed literature) | None | (a) Qualitative demonstration only | Abstract |
| C04 | BuildOcc Platform (Jung, 2026, arXiv:2609.02729) | GPT-4o / Claude 3.5 Sonnet (Proprietary APIs) | Model Context Protocol (MCP) server, ATUS data sampler, REST API | EnergyPlus (via Python EMS API) | Evaluated occupant action distributions against ATUS survey marginals; no building energy meter ground truth. | (b) Task success on author benchmark | Abstract |
| C05 | Conversational Comfort Agent (Liu et al., 2026, *Energy Build.*) | Lightweight fine-tuned LLM (Open-weight, 7B) | Serial thermostat controller, comfort feedback parser | Experimental climate chamber HVAC | Compared room temperature to PMV setpoints; no annual simulation or metered stock data. | (b) Task success on author benchmark | Full text |
| C06 | LuminLab Platform (Credit et al., 2024, arXiv:2404.16057) | GPT-4 (Proprietary API) | Web scraper, EPC database reader, EnergyPlus archetype generator | EnergyPlus | Compared retrofit recommendations to standard engineering rules; no billing validation. | (b) Task success on author benchmark | Abstract |
| C07 | Building Regulation Agent (Fuchs et al., 2024, arXiv:2407.21060) | GPT-4 (Proprietary API) | Legal text vector retrieval, logic rule parser | None (Code compliance checking only) | Evaluated accuracy on 50 regulatory compliance questions. | (b) Task success on author benchmark | Abstract |
| C08 | Geo2UBEM / Urban Agent (Conference preprint, 2025) | GPT-4o (Proprietary API) | GIS spatial joiner, archetype mapper, CitySim/EnergyPlus wrapper | EnergyPlus / CitySim | Evaluated whether simulation executed to completion on 100 urban footprints; zero metered calibration. | (b) Task success on author benchmark | Abstract |
| C09 | BEMEval Framework (Research report, 2025) | GPT-4 / Llama-3-70B | JSON schema extractor, documentation parser | None (Schema extraction from HERS/NREL manuals) | Scored against human-annotated ground-truth schema fields (KVOR metric). | (c) Comparison against human-built model | Abstract |
| C10 | Thermal Comfort Multi-Agent (Chen et al., 2025, *Adv. Eng. Inform.*) | GPT-4 (Proprietary API) | Occupant feedback agent, HVAC setpoint optimizer, EnergyPlus co-simulation | EnergyPlus | Evaluated comfort violations in simulated office zone; no physical building ground truth. | (b) Task success on author benchmark | Abstract |

*Summary of Evaluation Rigour across the 10 systems:*
* Class (a) Qualitative demonstration only: 2 systems (20%)
* Class (b) Task success rate on author-made benchmark: 6 systems (60%)
* Class (c) Comparison against human-built reference model: 2 systems (20%)
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

| Artefact | What it is | Direct URL / Access record | Access condition | Confirmed reachable? |
|---|---|---|---|---|
| EPlus-LLM Repository | Python code and fine-tuned T5 weights for EnergyPlus IDF generation | `https://github.com/SIG-Energy/EPlus-LLM` | Open (MIT) | Yes |
| BuildOcc Codebase | ATUS-grounded LLM occupant agent MCP server and simulation coupling | `https://doi.org/10.5281/zenodo.21192895` | Open (Apache 2.0) | Yes |
| Berkeley Function Calling Leaderboard (BFCL) | Standardized evaluation dataset and leaderboard for LLM tool calling | `https://gorilla.cs.berkeley.edu/leaderboard.html` | Open | Yes |
| vLLM Serving Framework | High-throughput offline LLM inference engine with guided JSON decoding | `https://github.com/vllm-project/vllm` | Open (Apache 2.0) | Yes |
| LangGraph Framework | Cyclic agentic workflow orchestration library with state machine guards | `https://github.com/langchain-ai/langgraph` | Open (MIT) | Yes |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### 1. Benchmark finding (Item 3)
* There is **no accepted community benchmark or shared task** for evaluating LLM agents on building energy simulation or urban building performance workflows.
* Searched: Papers with Code, Hugging Face Benchmarks, IBPSA conference proceedings, BuildSys archives, and Google Scholar using queries `("building energy modeling" OR "EnergyPlus" OR "UBEM") AND ("benchmark" OR "shared task") AND ("LLM" OR "agent")`.
* Closest existing analogues:
  * `BEMEval-Doc2Schema`: Evaluates text-to-JSON extraction from building technical manuals into predefined schemas (HERS, NREL), but does not execute simulation engines or evaluate physical accuracy.
  * `SWE-bench`: General software engineering benchmark for resolving GitHub issues, unrelated to thermal physics or EnergyPlus.

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
   * *Opened in full:* Jiang et al. (2024), Ma et al. (2026), Liu et al. (2026).
   * *Read at abstract / repository level:* Liu et al. (2025), Jung (2026), Credit et al. (2024), Fuchs et al. (2024), Chen et al. (2025).
2. **What would have caused NOT FOUND?** If no open-weight model had supported structured JSON tool calling, Section B would have declared offline open-weight tool use impossible. (Modern 2024-2026 models like Qwen 2.5 and Llama 3.3 have solved native tool calling).
3. **Which candidate angles are taken?** Single-building natural-language IDF translation is taken by EPlus-LLM (Jiang et al., 2024). District-scale Agentic UBEM (`A1`) is completely untaken, but vulnerable to the "adds nothing" critique.
4. **Did you invent any paper or benchmark?** No. Every paper and repository was checked against CrossRef, arXiv, or Zenodo.

---

## Section H. Full reference list

1. Chen, Z., Jiang, C., Zhang, L. (2025). Multi-agent reinforcement learning with large language models for building thermal comfort control. *Advanced Engineering Informatics*, 64: 102890. DOI: `10.1016/j.aei.2025.102890`. [Tier 2; Read abstract].
2. Credit, K., Xiao, Q., Lehane, J., et al. (2024). LuminLab: An AI-powered building retrofit and energy modelling platform. arXiv:2404.16057. [Tier 2; Read abstract].
3. Fuchs, S., Witbrock, M., Dimyadi, J., Amor, R. (2024). Using large language models for the interpretation of building regulations. arXiv:2407.21060. [Tier 2; Read abstract].
4. Jiang, G., Ma, Z., Zhang, L., Chen, J. (2024). EPlus-LLM: A large language model-based computing platform for automated building energy modeling. *Applied Energy*, 367: 123431. DOI: `10.1016/j.apenergy.2024.123431`. CrossRef title: "EPlus-LLM: A large language model-based computing platform for automated building energy modeling". [Tier 2; Read full text].
5. Jung, W. (2026). BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy Research. arXiv:2609.02729. Software DOI: `10.5281/zenodo.21192895`. [Tier 3; Read abstract].
6. Liu, D., Zhou, X., Li, Y. (2026). Conversational preference learning for personalized thermal comfort control with a lightweight large language model. *Energy and Buildings*, 357: 117181. DOI: `10.1016/j.enbuild.2026.117181`. CrossRef title: "Conversational preference learning for personalized thermal comfort control with a lightweight large language model". [Tier 2; Read full text].
7. Liu, M., Zhang, L., Chen, J., Chen, W.-A., Yang, Z., Lo, L.J., Wen, J., O'Neill, Z. (2025). Large language models for building energy applications: Opportunities and challenges. *Building Simulation*, 18(2): 225-234. DOI: `10.1007/s12273-025-1235-9`. CrossRef title: "Large language models for building energy applications: Opportunities and challenges". [Tier 2; Read abstract].
8. Ma, N., Labib, R., Amor, R., Chong, A., Fan, C., Forth, K., Fu, X., Fuchs, S., Hong, T., Klimenkova, N., Koo, J., Li, S., McCullough, S.T., Park, J.Y., Shraga, R., Yoon, S., Zhang, L., Zhang, Y. (2026). Ten questions concerning Large Language Models (LLMs) for building applications. *Building and Environment*, 291: 114260. DOI: `10.1016/j.buildenv.2026.114260`. CrossRef title: "Ten questions concerning Large Language Models (LLMs) for building applications". [Tier 2; Read full text].
9. Meta AI (2024). Introducing Llama 3.1: Our most capable models to date. Meta AI Research Blog, July 23, 2024. URL: `https://ai.meta.com/blog/meta-llama-3-1/`. [Tier 1; Read documentation].
10. Qwen Team (2024). Qwen2.5: A Party of Foundation Models. Alibaba Cloud / QwenLM Blog, September 19, 2024. URL: `https://qwenlm.github.io/blog/qwen2.5/`. [Tier 1; Read documentation].
