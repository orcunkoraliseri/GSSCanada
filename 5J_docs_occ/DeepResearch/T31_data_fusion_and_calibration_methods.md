# T31. Fusing time-use diaries with other occupancy sources: methods and precedents

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. Independent of the source-family prompts; it asks about
methods, not datasets.

## Why we are asking

No single non-survey source (`T20` to `T30`) carries everything a building model needs: thermostats
have presence but not activity or demographics; mobility data have area counts but no households;
travel surveys have trips but not in-home activity. Time-use diaries have activity and demographics
but no measurement. The natural design is a **fusion**: diaries give the structure, another source
calibrates or corrects it. We already rake diaries to census marginals by iterative proportional
fitting. We need to know which fusion methods exist beyond that, which were used for occupancy or
activity data, and what they cost in assumptions.

## What we need

### Item 1. The method families

For each, a definition with a canonical reference, a worked example on activity, mobility or
occupancy data if one exists, and the assumption it rests on (for example conditional independence
in statistical matching):

1. Statistical matching and data fusion (donor imputation, hot deck, constrained matching).
2. Calibration and raking to aggregate targets, including targets that are time profiles rather than
   counts (calibrating a population of schedules to an hourly at-home share).
3. Bayesian data assimilation or hierarchical models combining survey and sensor data.
4. Entropy maximisation and combinatorial optimisation for synthetic populations.
5. Domain adaptation and transfer learning between survey and sensor distributions.
6. Conditional generative models trained on one source and constrained by another.

### Item 2. Precedents on activity, travel or occupancy

Works that fused a time-use or travel survey with a measured source (phone data, sensors, meters,
counts). Section C rows with the two sources, the method, the validation, and whether the fused
result beat each source alone on a held-out measure.

### Item 3. Validation design for a fused source

When the second source is used to calibrate, it can no longer validate. How do the precedents keep a
held-out check (split by region, time, or a third source)? This matters to us: our validation
discipline requires a test the model was not fitted to.

## Named leads

*Journal of Official Statistics*, *Survey Methodology* (Statistics Canada), *Journal of the Royal
Statistical Society Series A*, *Transportation Research Part C*, *Computers, Environment and Urban
Systems*, *Journal of Artificial Societies and Social Simulation*, *Energy and Buildings*; D'Orazio,
Di Zio and Scanu on statistical matching as a lead only.

## Hard constraints specific to this prompt

* State each method's key assumption in one sentence; a method listed without its assumption is not
  admitted.
* Item 3 must answer the circularity question directly; "use cross-validation" is not an answer.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which fusion method has a precedent of combining diary-type data with a
measured source and beating both on a held-out test, and whether any such precedent exists for building
occupancy.

**Section B** is item 1. **Section C** is item 2. **Section E** is item 3 as design rules for us.
**Section D** assesses "diary structure calibrated to measured presence" as a form of `A14`.
**Section G** carries your negative controls.
