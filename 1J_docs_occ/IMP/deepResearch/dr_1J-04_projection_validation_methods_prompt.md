# Deep-Research Prompt dr_1J-04: how are generative population projections validated in published work?

> SCOPE GUARD, READ FIRST. We want **methods that published papers used**, quoted from the source. Our
> pass rule for the validation is **already fixed and is not a question here**: the method must beat a
> simple carry-forward baseline on most variables, or we drop the claim. Do not propose thresholds, pass
> marks or acceptable error sizes.

Run in: Gemini (live search). Save the answer as `dr_1J-04_projection_validation_methods_results.md` in
this folder.

---

## Why we are asking

Our paper uses a conditional variational autoencoder (C-VAE) with a clustering-based drift in the
latent space to generate a synthetic household population one step past the last census. A reviewer
called this the strongest part of the paper but the least validated. We plan a hindcast: fit on the
2006, 2011 and 2016 census files, generate 2021, and compare with the real 2021 census, against simple
baselines (carry the 2016 population forward; extrapolate the marginals linearly; shift the latent space
by the plain mean drift). We need to design this the way the field already does it.

## What we need

1. **Distance metrics** used to compare a synthetic population with a real one: for single variables
   (marginals) and for combinations of variables (joint distributions). For example standardised root
   mean square error (SRMSE), Jensen-Shannon divergence, total variation distance, Hellinger distance,
   Wasserstein distance, and measures of impossible or missing combinations ("structural zeros" and
   "sampling zeros"). For each: the papers that used it, and how they computed it.
2. **Temporal hindcasts**: published studies that fitted a population synthesis or projection model on
   earlier census or survey years and tested it on a later year held out. What baselines did they compare
   against?
3. **Deep generative population synthesis**: papers using VAEs, conditional VAEs, GANs or similar to
   synthesise populations or households, and how each validated its output.
4. **Projection through the latent space**: any paper that moves a generative model's latent space over
   time to produce a future population, and how it was checked.
5. **Randomness**: how papers report run-to-run variation of a generated population (number of seeds,
   what spread statistic).

## Named leads (open them; they are leads, not answers)

- Borysov, Rich and Pereira (2019), *How to generate micro-agents? A deep generative modeling approach to
  population synthesis*, Transportation Research Part C. **Positive control**: this paper is real. If you
  cannot find and open it, stop and say so.
- Work by Garrido and colleagues on rare attribute combinations in deep population synthesis.
- Reviews of population synthesis methods (iterative proportional fitting, combinatorial optimisation,
  Markov chain Monte Carlo, deep generative) in transportation and urban energy modelling.
- Building-energy papers that generate synthetic occupant populations for stock or neighbourhood models.

---

## Rules

- Open every paper before citing it. Give an exact quote for each method you attribute to it, with page
  or section.
- Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`) and give title, journal, year.
- Do not report any paper's error values as a benchmark for us. Methods only.
- `NOT FOUND` beats a guess. Do not invent papers, DOIs or quotes.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A, metrics:** metric, formula as the paper states it, marginal or joint, papers using it (with
   DOI), quote and page.
2. **Table B, validation designs:** paper, DOI checked (yes/no), model type, held-out data (which years),
   baselines compared, metrics, seeds reported (yes/no, how many), quote and page.
3. **The three designs closest to ours**, one paragraph each, quoted.
4. **Positive control result.**
5. **Search log** and **what I could not open**, in the first person, one line each.
