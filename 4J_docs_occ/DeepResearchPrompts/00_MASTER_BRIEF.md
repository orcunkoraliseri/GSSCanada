# 4J Deep Research: Master Brief (paste this block ahead of EVERY prompt)

This brief gives the shared context for the L-series prompts (`L01`, `L02`, `L03`, ...). Read it, then
answer only the prompt that follows it. Do not restate this brief in your answer.

---

## 1. Who is asking and what has already been built

A postdoctoral building-performance group that generates **occupancy data for building energy
modelling (BEM) and urban building energy modelling (UBEM)** from **national time-use and census
microdata**, and injects the result into EnergyPlus. Three pieces of work are finished and published or
submitted:

* **Paper 1 (CENTUS).** Iseri, Gursel Dino and Kalkan, *Occupancy modeling using population statistics
  and machine learning for urban residential built environment*, **Energy and Buildings 357 (2026)
  117155**, `https://doi.org/10.1016/j.enbuild.2026.117155`. Italian ISTAT 2011 CENSUS plus 2013-2014
  Time Use Survey, fused into a dataset called CENTUS. An LSTM and a Transformer, trained multitask,
  classify three temporal targets per hour (`Occupant Activity` with 145 classes, `Presence`,
  `Co-Presence`) conditioned on embedded demographic attributes, and augment a single diary day into a
  full year of season-by-daytype daily sets. Reported accuracy 0.98 for both deep models against 0.691
  for a high-order Markov chain with full context. The paper explicitly claims **HETUS
  standardisation as the route to cross-national transfer**, and does not test that claim on a second
  country. That untested claim is the seed of the present work.
* **Paper 2 (2J).** Statistics Canada GSS time-use plus Census PUMF, residential channel only, coupled
  to EnergyPlus. Submitted to *Building Simulation*.
* **Paper 3 (3J).** The same machinery extended to a **four-channel** occupancy generator (residential,
  office, retail, hotel) driving a mixed-use tall building, 2005 to 2030, with a conditional
  Transformer, a hotel side-track built from provincial tourism statistics, and a full EnergyPlus
  campaign. Target venue *Building and Environment*.

Across all three, the generator is a **task-specific supervised model trained on one country's
microdata**. It has never been shown to transfer.

## 2. What paper 4 is meant to be

**One open-weight large language model, fine-tuned once, that generates time-use diaries and the
occupant attributes attached to them, for any country inside the HETUS harmonised framework.**

The HETUS framework (Eurostat, `https://ec.europa.eu/eurostat/web/time-use-surveys`) is attractive
precisely because it already did the harmonisation work: a common diary structure, a common
hierarchical Activity Coding List, common location and co-presence fields, and common household and
individual questionnaires across the participating countries. If a single model can be conditioned on
`country + demographic vector + day type + season` and emit a **structurally valid, statistically
faithful diary**, then the occupancy input to a UBEM stops being a per-country data-engineering
project.

The candidate method the author has in mind is **parameter-efficient fine-tuning of an open-weight LLM**
(the Gemma family was named as an example). The author has **no prior LLM engineering experience** and
has explicitly asked whether fine-tuning is even the right instrument, or whether in-context learning,
constrained decoding, retrieval, or a purpose-built sequence model would beat it. **Treat the method as
an open question, not a settled decision.** A well-argued answer of "an LLM is the wrong tool for this
sub-problem, and here is why, and here is what would be right" is a valuable answer, not a failure to
comply.

## 3. What is genuinely uncertain, and therefore what these prompts are for

Ranked by how badly a wrong answer would hurt:

1. **Can the microdata be obtained at all, by whom, on what legal instrument, and how long does it
   take?** If HETUS microdata is not obtainable, the entire paper changes shape. This is prompt `L01`
   and it is the only true blocker.
2. **May a model trained on that microdata be published, and may its weights be released?** A model
   that cannot be shared is a much weaker paper. Prompt `L10`.
3. **Has this already been done?** Prompt `L03`. If a 2025 or 2026 paper already fine-tunes an LLM on
   time-use diaries for building energy modelling, we need to know before we spend a year on it.
4. **Which open-weight model, at which size, under which licence.** Prompt `L04`.
5. Everything else: method, serialisation, evaluation, compute, downstream coupling.

## 4. The compute we have

Concordia University's **Speed HPC cluster**, `https://nag-devops.github.io/speed-hpc/`, SLURM, shared
GPU partitions, walltime up to seven days per job. Previous papers trained conditional Transformers of
a few million parameters there. Nothing at LLM scale has ever been run on it by this group. Assume
**no access to a multi-node A100/H100 reservation** unless a source says otherwise, and assume the
budget for commercial API training is **zero**. Open weights, single-node, memory-constrained. This is
a hard design constraint, not a preference.

## 5. What is out of scope, and must not be re-derived

* The Canadian GSS pipeline, its channels, its EnergyPlus coupling and its validation gates. Finished.
* Whether occupancy matters for building energy. Settled in the literature and in papers 1 to 3.
* Any recommendation to buy commercial API access or rent cloud GPUs. Not available.
* Re-deriving the CENTUS results. We have them.

## 6. Source-quality rules (apply to every prompt)

1. **Tier 1 (preferred)**: primary institutional documents. Eurostat's own HETUS methodological manuals
   and their microdata access documentation; national statistical institute survey documentation and
   codebooks; the model developers' own model cards, technical reports and licence texts; the official
   documentation of the software libraries named.
2. **Tier 2**: peer-reviewed literature, and arXiv preprints where the preprint is the canonical
   reference for a method (which is normal in this field). For an arXiv preprint, give the arXiv ID and
   the version, and say whether it has since been published in a venue.
3. **Tier 3**: well-documented open-source repositories, benchmark leaderboards with a stated
   evaluation protocol, and technical blog posts **from the organisation that built the thing**.
4. **Rejected**: content-farm summaries, undated posts, tutorials that do not name a library version,
   marketing pages, and any AI-generated overview presented as a source.

Every claim must carry: the claim, the source's own wording or a tight paraphrase, document title,
issuing body, year or version, and a URL or stable identifier. Where a claim is your inference, label
it `INFERENCE` and give the assumption it rests on.

## 7. Answer discipline (this project has been burned, repeatedly, and specifically)

* Answer only what the prompt asks.
* **A citation is not evidence until opened.** Report only what you have actually read in a source you
  reached. Anything unreachable is `COULD NOT OPEN`, never a confirmation. State per claim whether you
  read the full text, only the abstract, or neither.
* **Verify every DOI and every identifier before citing it.** For DOIs, fetch
  `https://api.crossref.org/works/<DOI>` and report the title, first author, journal and year that the
  API actually returned, so the match can be checked without re-fetching. On a previous round of this
  project, **9 of 15 DOIs resolved to unrelated papers**, several of them one character away from the
  correct DOI, and a cited technical report number turned out to be a nuclear-materials study.
* **`NOT FOUND` is a valid and valuable answer.** If something cannot be sourced, write `NOT FOUND` and
  say what you searched for. Do not invent a plausible number, a plausible model name, a plausible
  version number, or a plausible licence clause.
* **Do not state, estimate or reproduce any result of our models.** You cannot see them. Anything you
  say about our numbers is either copied from this brief or invented, and in previous rounds it was
  invented.
* **Never recommend the option that happens to rescue us.** If the honest reading of the evidence is
  that the plan is infeasible, or that the data cannot be obtained, or that the method will not work at
  the scale we have, say so in the first sentence of Section A. Three of five rounds on the previous
  paper proposed exactly the change that would have made our failing test pass, after being told in
  writing not to. We read that pattern as a signal about the report, not about the world.
* **Distinguish what exists today from what is announced.** For anything model-related, give the
  release date and say plainly whether you verified the artefact is downloadable now, or are repeating
  an announcement. The author has named a model version that may or may not exist; **do not confirm a
  version because a prompt mentioned it.** Report what is actually published.
* **Version-pin everything.** A library recommendation without a version is not usable to us. Say which
  version you checked and when.
* Report negative results. Phrase them as absence of evidence, not evidence of absence.
* Return results in the schema given by `_RESPONSE_TEMPLATE.md`.
* **No em dashes and no en dashes anywhere in the output text.**

## 8. Vocabulary, so we do not talk past each other

| Term | What we mean by it |
|---|---|
| **Diary** | One respondent's one day, as a sequence of time slots, each carrying an activity code, a location code and a co-presence flag. HETUS nominally uses 144 ten-minute slots; our own pipelines resample to 48 half-hour slots. |
| **Daily set** | One diary plus the season and day-type it belongs to. A full year is assembled from a small number of daily sets. |
| **Non-temporal attributes** | Household and individual demographics: household size, family type, age class, education, employment, dwelling attributes. |
| **Temporal attributes** | Activity, presence, co-presence, per slot. |
| **Channel** | A building use whose occupancy is generated separately: residential, office, retail, hotel. |
| **Fidelity** | How closely the generated population's *distributions* match the survey's, not how well a single diary is predicted. This is a distribution-matching problem, not a forecasting problem. |
| **Structural validity** | The generated diary is well-formed: correct slot count, codes inside the coding list, exactly one location per slot, no impossible transitions. |
