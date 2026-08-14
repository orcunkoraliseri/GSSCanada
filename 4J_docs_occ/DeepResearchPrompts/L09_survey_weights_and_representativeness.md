# L09. Survey weights and population representativeness: how to make a generated population match a real one

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and E used.

## Why we are asking

Time-use surveys are **not simple random samples**. They carry design weights, non-response
adjustments, and often a separate diary-day weight that corrects for the fact that respondents are
easier to reach on some days than others. A model trained on unweighted records learns the sample, not
the population.

Downstream, we do not want a sample at all: we want to populate a city model with **the right number of
the right kinds of households**, drawn from census marginals for that city. Our previous papers did
this by matching survey respondents to census households. With a generative model the mechanism is
different and we do not know the accepted practice.

Three distinct problems, and we want them kept distinct:

1. **Training under complex survey weights.** How does a weight enter the training of a neural model.
2. **Generating a representative population.** How to draw so the synthetic population matches target
   marginals for a specific place.
3. **Correcting a generated population after the fact.** Raking or reweighting the output.

## What we need

### Item 1. Weights in training

1. What are the established options: weighted loss, weighted sampling of training examples,
   replication of records proportional to weight, or ignoring weights and correcting later? Give the
   evidence for each, and say which the survey-statistics literature endorses versus which the machine
   learning literature endorses. They may disagree, and if they do, say so.
2. **Weight trimming or clipping.** Extreme weights produce high-variance gradients. What is standard
   practice for trimming, and at what quantile? Cite the survey methodology source, not folklore.
3. Does weighting interact badly with **stratified batching**? We stratify batches by season and day
   type in our existing pipeline and want to know whether the two corrections conflict.
4. Is there any published work on **fine-tuning a language model on weighted survey data**
   specifically? If not, say `NOT FOUND` and name the nearest analogue, which may be class-imbalance
   or importance-weighting work.

### Item 2. Generating a population for a specific place

We want to instantiate, say, all residential dwellings in a district, with the right joint distribution
of household size, family type, age and employment for that district.

1. What is the accepted method for **synthetic population generation** in urban simulation: iterative
   proportional fitting, combinatorial optimisation, copulas, or the newer generative approaches?
   Give the canonical references, because this literature is mature and our reviewers know it.
2. Given a generative model that emits a diary conditioned on a demographic vector, what is the correct
   pipeline: synthesise the population first with an established method and then condition the model on
   each synthetic person, or have the model emit both the person and the diary jointly? State the
   trade-off explicitly. **We lean toward the first**, because it separates two claims that a reviewer
   can then attack separately, but we want the argument.
3. What census or register data is available for European cities at a granularity fine enough to serve
   as the target marginals? Eurostat census hub, national census outputs, the GEOSTAT population grid,
   and anything else. Name what is downloadable, at what spatial unit, with URLs, in Section F.

### Item 3. Post-hoc correction

1. **Raking and iterative proportional fitting on generated output**: how it is done, when it is
   legitimate, and what it cannot fix. Specifically, raking can fix marginals but cannot fix a wrong
   joint structure; confirm and cite.
2. **Rejection sampling** against target marginals: cost, and the risk of collapsing diversity by
   rejecting exactly the unusual cases we most want to keep.
3. Is there a defensible way to **report** a post-hoc-corrected result? The tension is that correcting
   the output weakens the claim that the model learned the distribution. Is there a convention, for
   instance reporting both corrected and uncorrected results? Name it if it exists.

### Item 4. Sampling temperature and diversity, as a representativeness instrument

Our published work already exposes three generation modes: deterministic argmax, probabilistic sampling
from the softmax, and temperature-plus-top-k stochastic sampling, and reports that argmax produces
overly uniform occupants at neighbourhood scale.

1. Is there evidence relating **decoding temperature** to distributional calibration? Specifically: is
   there a temperature at which a generated population's entropy matches the real population's, and is
   that the same temperature that maximises fidelity on other metrics?
2. What is the relationship between top-k or top-p truncation and **tail loss**? Truncated sampling
   systematically discards rare behaviours, and rare behaviours are exactly where the interesting
   energy loads live: the household that runs laundry at 03:00 is the one that matters for a peak-load
   study.
3. Is there a principled calibration procedure, as opposed to tuning temperature until the output looks
   right? If the honest answer is that there is not, say so, and say what we should report instead.

### Item 5. Non-response and coverage bias in the source survey

Whatever the model learns, it inherits the survey's biases.

1. What are the documented coverage and non-response biases of European time-use surveys? Which groups
   are under-represented, and is this documented in the Eurostat quality reports?
2. Do the published weights correct for these, and to what extent do the quality reports themselves say
   they do not?
3. What should we write as a limitation? Our papers carry an explicit consolidated limitations section
   with a measured bound on each item wherever possible, so a **number** here is worth much more than a
   caution.

## Named leads

Eurostat HETUS quality reports and methodological manuals; the survey-statistics literature on weighted
estimation and weight trimming; the synthetic population literature in transport and urban simulation;
Eurostat census hub and GEOSTAT population grid documentation; national statistical institute
small-area statistics; published work on calibration of generative model sampling.

## Hard constraints specific to this prompt

* Keep the three problems in the introduction separate throughout. Conflating them is the main way this
  answer could mislead us.
* **Do not recommend ignoring the weights without an argument.** It may well be the right answer for the
  training stage, but it needs defending, not assuming.
* Give URLs for every marginals dataset in Section F, with the spatial unit named.

## Deliverable

**Section C** is the recommended end-to-end design: how weights enter training, how a place-specific
population is instantiated, and whether any post-hoc correction is applied.

**Section F** is the target-marginals data catalogue.

**Section G** carries the survey bias limitations with numbers where they exist, and your negative
controls.
