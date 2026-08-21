# P01. Time-use-survey-driven stochastic occupancy and activity models: the full lineage, and what the standard baseline is

Paste `00_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used except Section D, which is `not applicable to this prompt`.

## Why we are asking

We build occupancy generators from national time-use microdata and we have been citing this
literature thinly — mostly the reviews, plus whatever a given venue's editor asked for. We now
suspect there is a well-developed twenty-year lineage doing something close to what we do with
simpler machinery, and that **we do not know what the field's standard baseline actually is.**

That matters twice over. It decides whether our own contribution is stated honestly. And it decides
what a new method must be compared against to be taken seriously — we currently compare against a
high-order Markov chain, and we do not know whether that is the accepted bar or an easy one.

## What we need

### Item 1. The lineage, reconstructed properly

Reconstruct the line of work that derives **stochastic occupancy, presence, or activity models from
national time-use surveys** for building energy purposes. We believe it includes, and we want each
one confirmed or corrected with a resolvable DOI:

* Richardson et al. — UK time-use survey, Markov-chain occupancy at 10-minute resolution, and the
  domestic electricity demand model built on top of it.
* Widén and Wäckelgård — Swedish TUS, Markov Chain Monte Carlo, activity to load.
* Wilke et al. — French TUS, demographically refined activity model.
* Aerts et al. — Belgian TUS, occupancy sequences.
* Flett and Kelly — UK, occupancy for domestic energy demand.
* Any equivalent we have not named.

For each: **what survey and year, what temporal resolution, what state space (presence-only, or
activity classes, and how many), what model class (first-order Markov, higher-order, semi-Markov,
survival/duration, other), what was validated and against what, and what the authors named as the
model's own limitation.**

🔴 We specifically want the **model class** column filled in carefully. The distinction between a
model that samples each timestep independently from an hour-marginal and one that carries a
transition kernel is the crux of this prompt.

### Item 2. The ATUS branch specifically

The American Time Use Survey has its own sub-literature. Establish it:

1. Work deriving **typical residential occupancy schedules or profiles for the US** from ATUS,
   including any national-laboratory output. We are aware of work on typical occupancy profiles and
   behaviours in US residential buildings and of multi-year ATUS-derived schedules by household type
   and age range; confirm authorship, venue and year.
2. Work building **stochastic** (as opposed to typical/average) ATUS-based schedules — we have seen
   reference to a three-state model on 2019 ATUS using a first-order inhomogeneous Markov chain.
   Confirm it, and find any successors.
3. Bottom-up **US housing stock** models that use ATUS-driven occupant behaviour.
4. 🔴 There appears to be a **published review specifically of ATUS applications in modelling
   energy-related occupant–building interactions** (*Energy and Buildings*, around 2023). Find it,
   confirm it, and give us its taxonomy of applications. If it exists it is the single highest-value
   citation in this prompt.
5. A separate **comprehensive review of time-use surveys in modelling occupant presence and
   behaviour** (around 2021) is also believed to exist. Same treatment.

### Item 3. The question that actually decides things — what is the accepted baseline?

Across the papers found in Items 1 and 2, tabulate **what each one compared itself against**.

We want to know which of these is the field's normal comparator, and how often each appears:

* a fixed/deterministic schedule (ASHRAE 90.1 or similar standard reference schedule);
* the unconditional (non-demographically stratified) survey marginal;
* a first-order Markov chain fitted to the same survey;
* a higher-order or semi-Markov model;
* measured field data (metered occupancy, CO₂, PIR, smart-thermostat logs);
* nothing.

🔴 **Then answer directly: if a new generative occupancy model in 2026 compared itself only against a
deterministic hour-of-day schedule, would that be accepted as an adequate baseline by this
literature?** We want a yes or a no with reasons, not a survey.

### Item 4. Duration, and whether anyone measures it

For building energy the length of an activity episode matters as much as its marginal frequency —
dwell time drives appliance duty cycles and HVAC recovery.

1. Which papers in Items 1–2 **report a duration or bout-length statistic** (episode-length
   distribution, transitions per day, sojourn time) rather than only per-hour marginals?
2. What statistics do they use, precisely enough that we could compute the same one?
3. Is there a documented result on **how badly an independent-per-timestep sampler distorts episode
   durations** while matching marginals exactly? If someone has quantified that, it is exactly what
   we need.

### Item 5. Where an LLM-based generator would sit

Given all of the above, and treating it as an assessment rather than a literature question (put it
in Section G, labelled as your own view):

* Is a "national time-use survey → activity probability table → sampler" pipeline in 2026 a
  **novel contribution** or **established practice**?
* If established, what *is* left that is novel in this space?

## What would make this answer wrong

Tell us in Section G if you conclude that this lineage is thinner than we assume, or that the ATUS
branch does not exist as a distinct literature. We would rather be told we are wrong about its
existence than be handed a padded list.
