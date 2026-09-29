# T13. Why a fine-tuned LLM loses to a raked pool of real diaries, and what the literature says would beat that null

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 1, after `T01`. Read together with `T07`.

## Why we are asking

Our fourth paper measured something we did not expect: on a pre-registered transfer gate, a pool of
real diaries from two training countries, re-weighted to the held-out country's demographic marginals,
reproduced that country's time budget two to six times better than an open-weight LLM fine-tuned on
the same diaries, on every age band of every fold, and a 4.7-fold larger backbone did not help (master
brief section 3, item 2). We are writing that up as the finding. Angle `A3` asks what comes next. We
want the literature's answer to three questions: is this pattern known, what explains it, and which
alternative designs have been shown, with numbers, to beat a strong nonparametric donor baseline on
distributional fidelity.

**Do not tell us how to make our gate pass.** Tell us what is known.

## What we need

### Item 1. Is the pattern known?

Find every 2022 to 2026 evaluation in which a fine-tuned or prompted language model generating
tabular, sequential or survey-like records was compared against a **nonparametric baseline built from
the real data**: resampling, hot-deck or donor imputation, raked or post-stratified pools,
nearest-neighbour synthesis, copula or Bayesian-network synthesisers. Report, per study: data type,
model and size, baseline, the fidelity metric, who won, by how much. Section C rows. Say in Section A
whether LLM generators typically lose to strong resampling baselines on marginal and joint fidelity.

### Item 2. Explanations offered

Collect the explanations the literature gives when a pretrained generator underperforms a simple
donor pool: mode collapse or variance flattening; tokenisation of numeric fields; loss mismatch
between next-token likelihood and distributional fidelity; the pretrained prior dominating a small
fine-tuning corpus; conditioning signals being ignored (attribute dropout, weak prefix attention);
the baseline having access to the marginals the model is scored on. For each, the study that measured
it and the diagnostic it used. Then say which explanations our own design (leave-one-country-out,
conditioning on a demographic vector, raking the null to published marginals) makes **testable** and
which it makes moot.

### Item 3. The unfair-null question

Our null is raked to the held-out country's published marginals; our generator is conditioned on the
same demographic categories but never sees the held-out country. Is there literature on **whether that
comparison is fair**, that is, on baselines that use target-population marginals versus generators
that do not? Cite the synthetic-population and survey-methodology work on this. Give both sides. Do
not resolve it in our favour.

### Item 4. Designs shown to beat the donor pool

For each of the following, the strongest published evidence that it beats a resampling or raked
baseline on distributional fidelity for sequential or survey data, with the metric and margin, or
`NOT FOUND`:

1. Retrieval-augmented generation over exemplar records (retrieve donors, condition the generator on
   them).
2. Hybrid donor-plus-edit: sample a real record, let the model modify it toward target attributes.
3. Mixture or ensembling of a donor pool and a generator.
4. Purpose-built sequence generators (diffusion, VAE, flow, GAN) for activity sequences or diaries.
5. Larger and more diverse pretraining corpora across countries (the argument that three countries
   are too few).
6. Different conditioning: continuous attribute embeddings, marginal-matching losses, constrained
   decoding toward target marginals, rejection sampling.
7. Population synthesis methods from transport research (iterative proportional fitting with
   synthesis, Bayesian networks, deep generative population synthesisers) applied to activity
   schedules.

### Item 5. What a negative result needs to be publishable

Which building-science, energy or machine-learning venues have published negative results on generative
or LLM methods, 2023 to 2026, and how were they framed? Cite three. What did reviewers or editors
require: pre-registration, a strong baseline, ablations, a mechanism? This shapes 4J's write-up and
decides whether 5J can be "the design that closes the gap" without 4J being read as a failure.

### Item 6. The honest reading

State in one paragraph what the evidence in items 1 to 4 implies for `A3`: whether a redesign is
likely to beat a raked donor null, whether the paper should instead be about when generation is worth
it at all, or whether the null itself is the useful product. Then give the strongest counterargument
to your own paragraph.

## Named leads

arXiv `cs.LG`, `cs.CL`, `stat.ML`; NeurIPS, ICML and ICLR datasets-and-benchmarks tracks; *Journal of
Official Statistics*, *Journal of Survey Statistics and Methodology*, *Transactions on Data Privacy*;
*Transportation Research Part C* and *Part B* for population synthesis; the GReaT, TabDDPM, TabSyn,
CTGAN, TVAE, REaLTabFormer and synthetic-population literature; IBPSA and *Energy and Buildings* for
negative results in building science.

## Hard constraints specific to this prompt

* Every comparison in item 1 carries the metric and the number. A study that reports "competitive"
  without a number is `NO NUMBER`.
* Do not propose a change to our gate, our null or our threshold. If a reader finds one in your
  answer, the round has failed.
* Item 3 must present both sides with citations. A one-sided answer is a failed item.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers in its first sentence whether LLM generators are known to lose to strong
resampling baselines on distributional fidelity, and in its second which single design in item 4 has
the best measured evidence.

**Section C** is the comparison table from item 1 and the design-evidence table from item 4.

**Section E** is items 5 and 6.

**Section G** carries the explanations from item 2 with their diagnostics, the fairness argument from
item 3, and your negative controls: did you propose any change to our gate; which studies you read in
full; whether any row in item 4 rests on the authors' own baseline rather than an independent one.
