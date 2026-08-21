# Brief for the P-series (paste this block ahead of EVERY P prompt)

Read this, then answer **only the prompt that follows it**. Do not restate this brief in your answer.

---

## 1. Who is asking

A postdoctoral building-performance group that generates **occupant presence, activity and
co-presence schedules for building energy modelling (BEM) and urban building energy modelling
(UBEM)** from **national time-use survey and census microdata**, and injects the result into
EnergyPlus.

Published or submitted work:

* **Paper 1.** Occupancy modelling from Italian ISTAT census + 2013–14 Time Use Survey fused into a
  dataset called CENTUS; LSTM and Transformer, multitask, classifying `Occupant Activity`
  (145 classes), `Presence` and `Co-Presence` per hour, conditioned on embedded demographics.
  *Energy and Buildings* 357 (2026) 117155.
* **Paper 2.** Statistics Canada GSS time-use plus Census PUMF, residential channel, coupled to
  EnergyPlus. Under review at *Building Simulation*.
* **Paper 3.** Four-channel occupancy generator (residential, office, retail, hotel) for a mixed-use
  tall building, conditional Transformer plus an EnergyPlus campaign. Target *Building and
  Environment*.
* **Paper 4, in progress.** One open-weight LLM, parameter-efficiently fine-tuned once on the
  **harmonised European HETUS** corpus, generating whole time-use diaries conditioned on
  `country + demographics + day type`, evaluated **leave-one-country-out** across Spain, the UK and
  Italy. The corpus is 73,254 diaries / 2,024,068 episodes. The evaluation is pre-registered and
  gate-based: every gate has a numeric threshold fixed in advance and must be **demonstrated
  failing** under a deliberate perturbation before its passing verdict counts.

So: we are practitioners in **survey-grounded occupancy modelling**, currently building an
**LLM-based generator**, and we care about **evaluation that can fail**.

## 2. What we are doing right now

Two things at once, and most of these prompts serve both:

* Auditing the **evaluation design** of LLM-driven occupant-behaviour work — our own included.
  Several of these prompts ask whether a widely used validation move is actually informative. We are
  looking for the *negative* answer as much as the positive one.
* Filling gaps in our literature base. We came late to the time-use-survey occupancy modelling
  literature and we suspect we are under-citing a lineage that predates us by nearly twenty years.

## 3. What a good answer looks like here

* **Findable, checkable citations.** Every claim we might repeat needs a DOI or a stable identifier
  we can resolve ourselves. We check them. We have been given a "CrossRef-verified" DOI that
  resolved to an unrelated paper on passive cooling in Brazil; we now assume nothing.
* **Numbers with their basis.** "Peer comparison reduces consumption" is not usable. "2.0 % average
  reduction, n ≈ 600,000 households, 17 trials, Allcott 2011, Table X" is.
* **A negative is a result.** If the literature we suspect exists does not, say so and say what you
  searched. If a method we are considering is known not to work, that is the most valuable answer
  you can give.
* **Distinguish what you opened from what you saw described.** Required in Section G of the
  response template, and we read it first.

## 4. What we are not asking for

* We are not asking you to evaluate any specific unpublished manuscript, and no prompt in this
  series refers to one. Answer the research question as posed.
* We do not need general LLM background. Assume familiarity with fine-tuning, decoding parameters,
  and agent architectures.

## 5. Response format

Use `_RESPONSE_TEMPLATE.md` (Sections A–H) from the 4J deep-research directory. Sections A, B, G and
H are required in every answer; Sections C–F are used where the prompt asks, and where a prompt does
not need one you write `not applicable to this prompt` rather than deleting the heading.
