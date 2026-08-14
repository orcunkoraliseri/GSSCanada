# L03. Prior art: has anyone already used an LLM to generate time-use diaries, activity sequences, or occupancy schedules?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections are used. **The most valuable possible answer to this prompt is that the work already
exists.** Please try hard to find it before concluding it does not.

## Why we are asking

We are about to commit roughly a year to fine-tuning an open-weight language model on harmonised
time-use microdata to generate occupant schedules for building energy modelling. Before we do, we need
to know whether that idea is already in print, and if so how far it got and what it left undone.

We are aware that the surrounding fields have moved fast. LLMs have been applied to human mobility
trajectory generation, to travel diary synthesis, to survey response simulation, and to tabular data
synthesis. We do not know how much of that has reached time-use surveys specifically, or building
energy modelling specifically, or the intersection.

**We would rather find a competitor and reposition than publish a duplicate.**

## What we need

### Item 1. The direct hit: LLMs on time-use or activity-diary data

Search hard for any published or preprint work that does any of the following, and report each as its
own Section B row with a full citation and a verified DOI or arXiv ID:

1. Fine-tunes or prompts an LLM to **generate a daily activity sequence** for a synthetic person,
   conditioned on demographics.
2. Uses an LLM on **time-use survey microdata** of any country, for any purpose, including imputation,
   coding, augmentation or synthesis.
3. Uses an LLM to **generate building occupancy schedules** or occupancy profiles.
4. Uses an LLM to **generate household appliance-use or activity-driven load profiles**.

For each hit, report: what data, what model and size, fine-tuned or prompted, what was evaluated and
against what, what the reported result was, and **what the authors named as future work**. That last
column is where our contribution lives or dies.

### Item 2. The adjacent field: LLMs for human mobility and travel behaviour

This field is more mature than ours and its methods will transfer. We are aware of a line of work on
LLMs for next-location prediction and trajectory generation, sometimes under names such as LLM-Mob, and
of work on synthesising travel diaries and activity-based travel demand model inputs with LLMs. Please
establish the actual state of it:

1. The leading methods, with citations.
2. Whether they **fine-tune** or **prompt**, and if they fine-tune, at what model scale and with what
   technique.
3. **How they serialise a sequence into text**, in enough detail that we could reproduce the format.
   This is directly reusable by us and is one of the highest-value items in this prompt.
4. How they evaluate. Specifically whether they evaluate on distributional realism of a generated
   population or on point prediction accuracy for individuals. We care about the former; much of this
   literature reports the latter, and if so that is a gap we can occupy.

### Item 3. LLMs as survey respondents, and its known failure modes

There is a body of work, sometimes labelled silicon sampling or synthetic respondents, on prompting
LLMs to answer surveys as if they were people with given demographics. It bears directly on whether an
LLM's pretrained prior about "what a 45-year-old employed mother in Poland does on a Tuesday" is an
asset or a liability.

1. What does the evidence say about **demographic fidelity** of LLM-simulated respondents: do they
   reproduce marginal distributions, and do they reproduce the correlations between attributes?
2. What are the documented failure modes: flattening of within-group variance, caricature of
   minority groups, refusal, and drift toward the majority or toward US-centric behaviour. Name the
   studies that measured each.
3. Is there evidence on whether **fine-tuning on real microdata fixes** these failure modes, or only
   masks them?

This item matters because our reviewers will raise it, and because if the failure mode is variance
collapse then our evaluation must be built to detect variance collapse specifically. See `L08`.

### Item 4. Tabular and sequential synthetic data generation with LLMs, versus the specialists

Our alternative to an LLM is a purpose-built generative model. Establish the honest comparison:

1. The state of LLM-based tabular data synthesis (the GReaT line of work and whatever succeeded it):
   what it claims, and what independent evaluations found.
2. The state of the specialist competition: CTGAN and TVAE, tabular diffusion models, and
   sequence-specific generative models. Are LLMs actually winning on tabular or sequential synthesis in
   2025 to 2026 evaluations, or losing to smaller specialised models?
3. **If the honest answer is that specialist models beat LLMs on this class of task, say so in Section
   A's first sentence.** We can still write a paper about cross-national transfer, but we need to know
   we are trading fidelity for transferability rather than getting both.

### Item 5. The building energy side: LLMs in BEM and UBEM

1. What has actually been published on LLMs inside building performance simulation, 2023 to 2026?
   We expect to find work on generating or editing IDF files, on natural-language interfaces to
   simulation tools, on retrieval over standards and codes, and on agentic control of simulation
   workflows. Map it.
2. Is there anything on **LLMs generating simulation inputs that are then validated against measured or
   surveyed ground truth**, as opposed to being demonstrated qualitatively? Rigour is uneven in this
   corner and we need to know where the bar actually is.
3. Which venues published them. `Energy and Buildings`, `Building and Environment`, `Applied Energy`,
   `Journal of Building Performance Simulation`, `Building Simulation`, `Advanced Engineering
   Informatics`, `Automation in Construction`. This feeds `L13`.

### Item 6. The gap statement

Close with an explicit, falsifiable gap statement of the form: *"No published work does X on Y
evaluated by Z."* Then immediately try to break your own statement by naming the nearest thing that
does. If you cannot state a gap that survives that test, say so plainly.

## Named leads

Scopus, Web of Science, Google Scholar and Semantic Scholar for the journals named in item 5; arXiv
categories `cs.CL`, `cs.LG` and `cs.CY` for the mobility and synthetic-respondent lines; the IEA EBC
Annex 79 and Annex 87 outputs for occupant-behaviour modelling state of the art; the proceedings of
`IBPSA Building Simulation`, `eSim`, `SimAUD` and `BuildSys`, which is where applied work of this kind
often appears before it reaches a journal; the Centre for Time Use Research working paper series.

## Hard constraints specific to this prompt

* **Every citation must be verified through CrossRef or arXiv before it appears in your answer**, and
  Section H must show the title the API returned. On a previous round of this project 9 of 15 DOIs
  resolved to unrelated papers. We will check every one.
* **Do not pad the answer with generically relevant occupancy-modelling papers.** We have read that
  literature and cited it in three papers. A row belongs in your answer only if it involves a language
  model or a directly competing generative method.
* **Do not invent a plausible-sounding paper title.** If you believe something exists but cannot reach
  it, write `BELIEVED TO EXIST, NOT REACHED` and say what search you ran.
* If a work is a preprint only, say so, and give its date. In this field a 2024 preprint may already be
  superseded.

## Deliverable

**Section A** answers one question in its first sentence: is our idea already published, yes or no.

**Section B** is the competitor table, one row per work, with the columns named in item 1.

**Section G** carries the gap statement from item 6, the failure-mode evidence from item 3, and your
negative controls.
