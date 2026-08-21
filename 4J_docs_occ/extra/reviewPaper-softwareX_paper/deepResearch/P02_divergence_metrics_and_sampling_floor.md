# P02. Divergence metrics for generated activity sequences: the finite-sample floor, the circularity trap, and duration-sensitive alternatives

Paste `00_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used except Section D, which is `not applicable to this prompt`.

## Why we are asking

We are auditing how generated occupancy and activity sequences get validated, our own work included,
and we have two specific worries. Both are statistical questions with answers in the literature, and
we want the answers rather than our intuitions.

**Worry 1 — the comparison can be circular.** A common pattern: fit an empirical distribution `P`
from survey microdata, sample a synthetic population from `P`, then "validate" by computing a
divergence between `P` and the empirical distribution `Q̂` of the samples. If the sampler is correct,
that divergence is not zero — it is the finite-sample estimation error — and it is bounded below by
the number of draws, not by the quality of the grounding. Our concern is that such a test **cannot
fail**, and that reported small divergences are being read as evidence of fidelity when they are
evidence of nothing but a working random number generator.

**Worry 2 — the metric can be blind to the failure that matters.** Divergences computed on per-hour
**marginals** are invariant to temporal reordering. A generator that samples each timestep
independently from the correct hour-marginal scores perfectly while producing activity episodes of
completely wrong length. For building energy, episode length is the quantity that drives load.

## What we need

### Item 1. The finite-sample floor, stated properly

1. Give the standard result for the **expected Kullback–Leibler divergence between a true discrete
   distribution and its empirical estimate from `n` i.i.d. draws** over `K` categories. We believe
   the leading term is `(K−1)/(2n)`. Confirm it, state the exact conditions, name the source
   (Miller–Madow bias, the asymptotic chi-square/`G²` relationship, or whichever is canonical), and
   give the next-order correction if the leading term is a poor approximation at small `n`.
2. State how the answer changes for **`D_KL(P‖Q̂)`** versus **`D_KL(Q̂‖P)`** — the two directions
   behave very differently when the estimate has empty cells, and papers rarely say which they used.
3. Give the **variance** or an upper percentile, not only the mean, since what we actually want is a
   null distribution to compare an observed value against.
4. 🔴 What is the **recommended practice** for reporting a divergence against a fitted distribution?
   Is there a standard reference that says "report the null / bootstrap distribution of the statistic
   under a correct sampler and show the observed value against it"? We want something citable.

### Item 2. Zeros, smoothing constants, and unbounded divergence

Papers comparing a generated distribution against a reference routinely add a small constant `ε`
(e.g. `10⁻⁹`) to avoid division by zero.

1. Explain precisely how the reported KL value then depends on `ε` when the comparator places zero
   probability on a category the reference records as occurring. What is the magnitude of the
   resulting number, and what does it actually measure?
2. 🔴 Is a **ratio between two such KL values** (a "our model is 1200× better" claim) a meaningful
   effect size? Give the argument, with a citation if the point has been made in print.
3. What are the recommended **bounded** alternatives for exactly this situation — Jensen–Shannon
   divergence, total variation distance, Hellinger, Wasserstein/earth-mover on an ordered support —
   and what does each buy and cost? Which is standard in synthetic-population or synthetic-data
   evaluation?

### Item 3. Duration-sensitive statistics — the important item

We need a concrete, citable menu of statistics that **detect the independent-sampling failure mode**
described in Worry 2.

1. What statistics does the sequence-generation literature use to compare **episode/bout length**
   distributions? Name them precisely (mean sojourn time, survival curves, transitions per day,
   Kolmogorov–Smirnov on bout lengths, run-length entropy, autocorrelation of the state sequence,
   *n*-gram or transition-matrix distance).
2. Which of these appear in the **occupancy/activity modelling** literature specifically, as opposed
   to general sequence modelling?
3. 🔴 Has anyone **quantified the damage**? That is: measured how far episode durations depart from
   truth for a sampler that matches per-timestep marginals exactly but samples independently. Any
   published figure — number of transitions per day, mean bout length ratio, resulting error in
   simulated load — is directly usable to us.
4. Is there a documented case of a published occupancy model that matched marginals and was later
   shown to have wrong dwell times?

### Item 4. Downstream: does it matter for energy?

1. Is there evidence on **how much simulated building energy use changes** when occupancy schedules
   have correct marginals but wrong episode durations? A sensitivity study, an EnergyPlus comparison,
   anything with numbers.
2. Which end uses are most sensitive — HVAC cycling, appliance duty cycles, DHW, lighting?

This decides whether Worry 2 is a methodological purity point or a real modelling error, and we want
to state it correctly either way.

### Item 5. Held-out evaluation for survey-fitted generators

1. What is the accepted way to make a survey-grounded generator's evaluation **falsifiable**? Split
   respondents within stratum, hold out a survey wave/year, hold out a country, compare against
   independent measured data?
2. Are there worked examples in the occupancy or synthetic-population literature we can imitate?
3. What is standard in the **synthetic population** literature (transport, microsimulation), which
   has faced this exact problem for longer than building energy has?

## Section E is important here

We will change how our own Step 6 results are reported based on this answer. Please make Section E
concrete: name the sentences and the statistics we should be reporting, tied to Section B rows.
