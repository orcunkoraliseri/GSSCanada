# T03. LLM agents in building performance simulation and UBEM: what is built, what is validated, and what runs on one open-weight GPU

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, C, E, F, G, H used. Run in wave 1, after `T01`.

## Why we are asking

Angle `A1` in the master brief is an agentic layer over our own UBEM engine: a language model that
takes a natural-language brief for a district and drives geometry, archetype enrichment, IDF
generation, simulation and validation, with every step gated by the engine's existing report-only
checks. Our fourth paper's prior-art round mapped LLMs *in* BEM up to mid 2026 at the level of IDF
editing and natural-language interfaces. This prompt asks about the **agentic** layer specifically,
because that literature moved fast in 2025 and 2026 and we do not know where the bar is now.

We have no commercial API budget. Whatever we build must run with open weights on a single GPU node.
That constraint is part of the question, not an afterthought.

## What we need

### Item 1. The agent systems that exist

For each published or preprint system in which a language model **plans and executes** a building
simulation workflow (as opposed to answering questions about one), give a Section C row plus: the
model used and whether it is open-weight; the tools it calls; whether the workflow reached EnergyPlus,
Modelica, DOE-2, TRNSYS, IES, or a UBEM tool; whether **any output was compared to measured or
independently simulated ground truth**; and how success was scored. Include work on IDF or
Modelica generation, calibration agents, code-compliance agents, retrofit-recommendation agents, and
multi-agent design assistants.

### Item 2. Rigour, honestly

For the systems in item 1, classify the evaluation: (a) qualitative demonstration only; (b) task
success rate on a benchmark the authors made; (c) comparison against a human-built model; (d)
comparison against measured data. Count how many fall in each class. If most are (a) and (b), say so
in Section A, because that is where our validation discipline becomes a contribution rather than a
chore.

### Item 3. Benchmarks and shared tasks

Is there any benchmark or shared task for LLM agents on building simulation, building codes, or
energy modelling? Name it, its tasks, its metric, its leaderboard, and its licence. If `NOT FOUND`,
say what you searched; a missing benchmark is itself a finding.

### Item 4. Open-weight feasibility

For agentic tool use with open weights on one GPU (assume 80 GB or less, no API):

1. Which open-weight model families released by the date you check support reliable structured tool
   calling, with the model card wording that says so and the release date. Do not confirm a model
   because the prompt or the brief named one.
2. Which agent frameworks run fully offline with a local model, at which version, checked when.
3. Published evidence, if any, of the gap between open-weight and frontier models on tool-use
   benchmarks relevant to code and scientific workflows, with the benchmark named.
4. Whether any building-simulation agent paper used an open-weight model, and what happened.

### Item 5. Reproducibility of agent runs

Agent outputs are stochastic. What do the papers in item 1 report about run-to-run variance, seeds,
temperature, and repeated trials? Is there any accepted protocol for reporting agent reproducibility
in scientific-workflow papers? If not, say `NOT FOUND` and name the closest thing.

### Item 6. What an agent over a UBEM would have to prove

From items 1 to 5, state what a reviewer in *Energy and Buildings* or *Applied Energy* would demand of
an agentic UBEM paper in 2027 that the existing papers did not provide. Be concrete: the comparison,
the ground truth, the number of districts, the ablation against a scripted pipeline with no agent.
Then state the strongest argument that the agent adds nothing a scripted pipeline lacks.

## Named leads

arXiv `cs.AI`, `cs.CL`, `cs.SE`, `cs.MA`; *Automation in Construction*, *Advanced Engineering
Informatics*, *Energy and Buildings*, *Building and Environment*, *Journal of Building Performance
Simulation*, *Applied Energy*; BuildSys, IBPSA Building Simulation 2025, CISBAT 2025, SimAUD; the
EnergyPlus and OpenStudio developer forums for agent tooling; model cards on Hugging Face for
tool-calling claims; the Berkeley Function Calling Leaderboard and comparable tool-use benchmarks.

## Hard constraints specific to this prompt

* Every model version and framework version carries the date checked. This literature rots monthly.
* Say per system whether you read the full paper, the abstract, or only the repository README.
* Do not describe a system's capability from its own abstract when the paper's evaluation section
  contradicts it. Report the evaluation, not the claim.
* Do not recommend that we buy API access or use a hosted model. Not available.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers two questions in its first two sentences: has an LLM agent driven a UBEM end to
end with a comparison to ground truth, yes or no; and how many systems in item 1 reached class (c) or
(d) in item 2.

**Section B** is the open-weight feasibility table from item 4.

**Section C** is the agent-systems table from item 1.

**Section E** is item 6.

**Section G** carries the benchmark finding from item 3, the reproducibility finding from item 5, the
"agent adds nothing" argument, and your negative controls.
