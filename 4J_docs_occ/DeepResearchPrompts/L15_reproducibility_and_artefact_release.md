# L15. Reproducibility and artefact release: model cards, dataset cards, hosting, licences, and what a 2026 reviewer expects

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, E and F used. Depends on `L10` for what we are permitted to release, and on `L14` for what
the venue requires.

## Why we are asking

Our previous papers released code and documentation. Releasing a **model** is new territory, and it
comes with conventions we do not know: model cards, dataset cards, licence choice for derived weights,
where to host large files, how to make the artefact citable, and how to keep it reproducible when the
data behind it cannot be shared.

We also have a specific structural problem: **the artefact people would most want is the one we are
least likely to be allowed to release.** We need a release design that is honest, useful, and
compliant, and we would rather design it at the start than retrofit it at proof stage.

## What we need

### Item 1. The documentation conventions

1. **Model cards**: what is the current expected content, and who defines it? Give the canonical
   reference and any venue or platform requirement. What sections are mandatory, and what does a good
   card include about training data provenance when the data itself is restricted?
2. **Dataset cards** and datasheets for datasets: the same questions.
3. Is there a **domain-specific** reporting standard for machine learning in building energy or in
   energy research generally, as there is in medicine? If one exists, name it, because following it is
   cheap and defuses reviewer objections.
4. What should be reported about **training compute and energy**? Is there an accepted format, is it
   required by any of our candidate venues, and what tooling measures it on a SLURM cluster.

### Item 2. Hosting and citability

1. Where should a fine-tuned adapter or model be hosted so that it remains available and citable for
   ten years: a model hub, a general-purpose research repository with a DOI, an institutional
   repository, or several? Give the trade-offs, including file-size limits and long-term availability
   guarantees.
2. How do we make a **model** citable with a persistent identifier, and is there a convention for
   versioning it as it changes?
3. What are the size limits and cost, if any, for each option, given that even a LoRA adapter is
   modest but a merged model is not.
4. Is there a convention for hosting a **large synthetic dataset**, potentially millions of records?
   Format matters here too: is a columnar format expected, and is there a domain convention for
   time-use or schedule data specifically.

### Item 3. Licensing the derived artefacts

1. What licence may we apply to a **fine-tuned adapter** derived from a base model under the licences
   surveyed in `L04`? Does the base licence propagate, and if so how must we express that?
2. What licence should the **synthetic dataset** carry, given that it was derived from restricted
   microdata? Does a synthetic derivative inherit obligations from the source agreement? This is the
   question we least know how to answer and it may not be settled; say so if it is not, and name what
   would settle it.
3. What licence for the **code**? Any conventional choice is fine; we ask only because the code will
   embed the serialisation format and the coding lists, and if a coding list is itself under a
   restrictive licence that matters. Check whether the HETUS activity coding list can be redistributed
   in a code repository.

### Item 4. Reproducibility when the data cannot be shared

This is the hard case and we want a concrete design.

1. What is accepted practice for a paper whose training data is restricted? Options include: a full
   recipe plus a synthetic or public stand-in dataset, a reproduction package that runs end to end on a
   public survey such as ATUS, deposit of the data at a secure facility with a documented access route,
   or a reproducibility statement explaining what cannot be shared and why.
2. **Is there a precedent in our field?** A published building-energy or occupancy paper trained on
   restricted national microdata, with a release design we could copy. If you find one, describe its
   release design precisely; that is worth more than any general advice.
3. We are inclined to make the **fully public path the primary experiment**: build the whole pipeline on
   a completely open time-use survey, so that everything is reproducible by anyone, and treat the
   restricted-microdata results as the extension. Is that a recognised and respected design, and what
   does it cost us in the strength of the claim? Give the argument both ways.

### Item 5. Determinism and the seed problem

1. Is bit-exact reproducibility achievable for LLM fine-tuning and generation on GPU? Be honest: we
   believe the answer involves non-deterministic kernels and is at best qualified. State the actual
   situation, name the flags and environment variables that improve it, and say what they cost in
   speed.
2. What should we therefore promise in the paper: bit-exact reproduction, statistical reproduction
   within a stated tolerance, or reproduction of conclusions? Name the convention and its source.
3. For the **generation** step specifically, is seeded sampling reproducible across library versions and
   hardware? If not, and we distribute a generated dataset, the dataset itself becomes the artefact of
   record rather than the seed. Confirm or correct that reasoning.

### Item 6. The reproduction package, specified

Close with a checklist of exactly what our release should contain, in the order a reader would use it,
assuming the most restrictive plausible answer from `L10`. We want a list we can build against from day
one, not assemble in a panic at revision stage.

## Named leads

The model card and datasheets-for-datasets literature; platform documentation for model and dataset
hosting; research repository documentation for DOI minting and file-size limits; publisher policies on
data and code availability; the machine-learning reproducibility checklists used by major venues; the
open-source licence texts; published guidance on reproducibility with restricted data in the social
sciences, where this problem is much older than it is in ours.

## Hard constraints specific to this prompt

* Give the current version and date of every policy or convention you cite.
* Distinguish what is **required** by a venue from what is **good practice**. We will do both, but we
  need to know which is which.
* Do not recommend a hosting platform without stating its file-size limit and its long-term
  availability policy.
* If something is genuinely unsettled, especially the licence status of synthetic data derived from
  restricted microdata, say it is unsettled rather than picking an answer.

## Deliverable

**Section C** is the release design: what we publish, where, under what licence, with what
documentation.

**Section E** is the checklist from item 6.

**Section F** is the links: card templates, repository landing pages, policy documents.

**Section G** carries the unsettled questions and your negative controls.
