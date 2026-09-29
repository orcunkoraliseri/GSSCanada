# T43. Which occupancy paper that trains a model on our own GPUs is still open, and can be scored without people

Paste `00_MASTER_BRIEF.md` first (read its section 11), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. **Run it alone: do not run any other prompt in this session, before or
after.** Written 2026-09-28. Your files are `RT43_training_based_occupancy_forms.md` and
`RT43_pages.log`.

## Why we are asking

We need a new subject for the fifth paper (brief section 11). It must be about occupancy for building
energy, it must train or fine-tune a model on our cluster, and it must be scored only against records
that already exist. Below are seven candidate forms. For each, we need to know whether it has already
been done, what the nearest work did not do, and whether it can be scored without people.

## The candidate forms

* **B1. Diary to meter.** Train a model on a dataset that links time-use diaries to measured household
  electricity for the same household and day, so that generated activity sequences come with the load
  they cause. Scored on held-out households' measured load.
* **B2. Household load conditioned on who lives there.** Train a generator on smart-meter data joined
  to a household survey (size, ages, work status, dwelling), producing load profiles for household
  types. Scored on held-out households.
* **B3. Pretraining across open time-use corpora.** Pretrain on several open corpora (for example US
  ATUS, MTUS, the Canadian GSS public files, the UK time-use survey) and adapt to Canada. Scored on a
  held-out GSS cycle. Known neighbour: BuildOcc (brief section 11, rule 5).
* **B4. An occupancy-aware simulation surrogate.** Train a model on paired EnergyPlus runs (occupancy
  varied, building frozen) to predict hourly heating, cooling and electricity from an occupancy
  sequence and a building description. Scored on held-out simulations.
* **B5. Predicting the next survey cycle.** Train on earlier survey cycles (for example GSS 2005 to
  2015, ATUS before 2020) and predict the time-use distribution of a later cycle that the model never
  saw. Scored on the real later cycle.
* **B6. Occupancy detected from meter or sensor data.** Train a model to infer presence from
  electricity or smart-home data, in homes that also record measured presence. Scored on the measured
  presence. We expect this field to be crowded; say so if it is.
* **B7. Language-model households.** Prompt or fine-tune a language model to act as household members
  and write their daily plans, compared with time-use surveys. Scored on survey distributions. We
  expect this to be crowded in transport research; say so if it is.

You may add **up to three further forms** of your own, each meeting all six rules of brief section 11.

## What we need

### Item 1. Prior work per form

For each form, search studies from 2019 to today and list the nearest ones in Section C. Every Section
C row carries: authors copied from the CrossRef record, year, venue, DOI or arXiv ID; which form it is
near; data used; model and whether it was trained by the authors; how it was scored; whether any
person labelled or rated anything; what it did not do; `Read:` full, abstract, or `TITLE ONLY`.

### Item 2. Verdict per form

One Section D row per form: taken, partly taken, or open as far as searched, with the Section C row
that decides it; which brief section 11 rule it breaks, if any; the data it needs and whether that
data is open, registration or application; the truth it is scored against; a training shape on one
A100 node (records, GPU hours, labelled `INFERENCE`); the reviewer's strongest objection.

### Item 3. Ranking

Rank only the forms that break no rule and can finish training within the four-week GPU window (brief
section 11, time limit): by how open they are first, and by how fast the data is in hand second. Say
plainly if none survives.

## Named leads

OpenAlex, Semantic Scholar, arXiv, CrossRef, IBPSA proceedings (Building Simulation, SimBuild, eSim),
ACM BuildSys and e-Energy, NeurIPS and ICLR climate workshops, Tackling Climate Change with Machine
Learning. Journals: Energy and Buildings, Building and Environment, Applied Energy, Energy and AI,
Journal of Building Performance Simulation, Sustainable Cities and Society, Transportation Research
Part C (for `B7`). Query terms, alone and combined: "time use", "occupancy", "household load profile",
"smart meter", "synthetic load", "generative model", "transformer", "foundation model", "diffusion",
"large language model", "surrogate model", "EnergyPlus", "activity sequence", "occupancy detection",
"generative agents", "daily activity plan".

## Hard constraints specific to this prompt

* **Positive controls.** Your searches must surface, through logged search lines, (a) BuildOcc and
  (b) at least one published study of occupancy detection from smart-meter data (`B6`). If they do
  not, say so in Section G; it means the searches are too weak to support any "open" verdict.
* **Negative control.** If every one of the seven forms comes back open, treat your own searches as
  too weak and say so in the first sentence of Section A.
* Before writing `TITLE ONLY`, try at least one open copy (publisher abstract page, arXiv, Semantic
  Scholar or OpenAlex abstract) and log each try.
* Authors are copied from the CrossRef record of that DOI, never from memory or a citing paper.
* A verdict of "open" lists its queries with their log lines: "these queries found nothing", never
  "no such work exists".
* Do not name any person connected to the researcher's funding proposals or host laboratory.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first, in at most eight sentences: which forms are taken, which survive the six
rules, and which one you would test first. **Section C** is item 1. **Section D** is item 2 plus the
ranking of item 3, each verdict marked `[INFERENCE]`. **Section F** lists the datasets each surviving
form needs (landing page opened, access condition quoted). **Section G** carries the control results,
the queries that found nothing with their log lines, and any work you could not open.
