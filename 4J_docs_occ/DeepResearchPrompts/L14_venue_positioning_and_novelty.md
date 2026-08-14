# L14. Venue, positioning and the novelty matrix: where this paper goes and what it must claim to survive review

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C and E used. Run this **after** `L03`, whose competitor list it depends on.

## Why we are asking

Our series has a venue pattern: paper 1 in *Energy and Buildings*, paper 2 submitted to *Building
Simulation*, paper 3 targeting *Building and Environment*. Paper 4 is different in kind, because its
method is machine learning of a sort that building-science reviewers have not yet developed reflexes
for, while its application is one that machine-learning venues do not care about.

That is a positioning problem and it decides the paper's framing, its structure, and how much of it is
method versus application.

## What we need

### Item 1. Candidate venues, assessed

For each candidate, one row: scope fit, whether it has published LLM work and how much, typical review
turnaround, article-processing charge and whether a fee waiver exists, open-access policy, and the
typical length and structure of a methods-heavy paper there.

Candidates: *Energy and Buildings*, *Building and Environment*, *Applied Energy*, *Journal of Building
Performance Simulation*, *Building Simulation*, *Advanced Engineering Informatics*, *Automation in
Construction*, *Sustainable Cities and Society*, *Energy Policy* if the framing goes policy-ward, and
any data-focused venue such as *Scientific Data* if the deliverable is reframed as a dataset. Add
anything we have missed, including conference routes.

For each, answer specifically: **has this venue published a paper whose core method is a fine-tuned
language model?** If yes, cite it, because that establishes the venue will not desk-reject on method
unfamiliarity. If no, say so, because that is a risk.

### Item 2. The dual-deliverable question

There is a real option here that we want assessed rather than assumed away: this work produces **two**
artefacts, a method and a dataset. A synthetic, cross-national, HETUS-consistent occupancy dataset is
arguably more useful to the field than the model that made it.

1. Is a **data paper** in a data journal a credible parallel or alternative output? What are the
   requirements: deposit, format, documentation, licensing?
2. Would a data paper and a method paper from the same work be seen as salami slicing, or is the
   pairing accepted practice in this field? Give the evidence, not an opinion.
3. Which comes first, and does publishing the dataset first weaken or strengthen the method paper?

### Item 3. The novelty matrix

Build a matrix whose rows are the closest prior works from `L03` and from the occupancy-modelling
literature, and whose columns are the axes on which we could claim novelty:

* cross-national transfer, evaluated on a held-out country,
* a single model serving many countries rather than one model per country,
* generative rather than classification framing,
* pretrained language model rather than a from-scratch sequence model,
* activity-resolved rather than presence-only output,
* longitudinal, that is, multiple survey waves and a forecast to a future year,
* validated downstream in a building energy model,
* released artefacts.

Fill the matrix and then state, in one sentence, **which combination of cells is genuinely unclaimed**.
Then attack that sentence: what is the strongest argument a reviewer could make that the combination is
incremental? Our previous paper did exactly this exercise and it was the most useful single output of
that research round.

### Item 4. The objections we will receive, and the answers

Predict the reviewer objections and tell us what evidence would answer each. We expect at least:

1. "Why an LLM? A small Transformer does this better and cheaper." The honest answer depends on `L06`.
2. "You have not validated on the countries you claim to generalise to."
3. "Your accuracy metric does not measure what a generative model should be measured on."
4. "The model may have memorised the microdata."
5. "The environmental cost of an LLM is not justified for this task." Is this objection actually raised
   in building-energy venues? If so, what reporting defuses it, and is there a standard for reporting
   training energy or carbon?
6. "This is a data-engineering exercise, not research."
7. "The improvement over standard schedules is not shown to matter for energy."

For each: what experiment or number would answer it, and can we produce it. Be specific about which
objections we **cannot** answer, because those become limitations.

### Item 5. Author-side requirements at the shortlisted venues

For the top two venues:

1. Structure, word or page limits, figure and table limits, reference style.
2. **Data availability and code availability policies**, verbatim from the author guidelines. This
   interacts directly with `L10`: if a venue mandates data availability and our microdata licence
   forbids redistribution, we need to know the exact wording of the exception the venue accepts.
3. Policy on **AI use disclosure**. Most publishers now require a statement about generative AI in the
   authoring process. Ours is a paper whose *subject* is a language model, which is a different thing
   from using one to write the paper, and we should be sure the disclosure is worded correctly. Quote
   the policy.
4. Preprint policy, and whether posting to arXiv or a repository before submission is permitted.
5. Any policy on **model or weight availability** specifically. This is newer than data-availability
   policy and may not exist yet; if it does not, say so.

### Item 6. Title and framing options

Propose three candidate framings, each in one sentence, with the venue each suits:

1. A **methods** framing: the model is the contribution.
2. A **transfer** framing: cross-national generalisation is the contribution.
3. An **application** framing: the European building stock result is the contribution.

Say which you would choose and why, given that the author's series is read as building science.

## Hard constraints specific to this prompt

* Quote author guidelines verbatim for anything about data, code or AI disclosure. Give the date
  checked; these policies change.
* Verify every citation used in the novelty matrix through CrossRef.
* Do not recommend a venue purely on impact factor. Fit and reviewer competence matter more here.
* Be blunt in item 3. A novelty statement we cannot defend is worse than a modest one we can.

## Deliverable

**Section B** is the venue table.

**Section C** is the novelty matrix and the one-sentence novelty claim, with the counterargument.

**Section E** is the objection-and-answer table from item 4, which becomes our discussion section
skeleton.

**Section G** carries the objections we cannot answer, which become the limitations section, and your
negative controls.
