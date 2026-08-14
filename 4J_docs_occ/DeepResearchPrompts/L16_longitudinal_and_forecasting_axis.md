# L16. The longitudinal axis: can a fine-tuned model be pushed to a future year, and what would make that defensible?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, E and F used.

## Why we are asking

The signature of this paper series is **time**. Paper 2 and paper 3 do not merely reproduce observed
occupancy; they run 2005 to 2022 across four survey cycles and then forecast to 2030, by progressive
fine-tuning across cycles with a continuous year variable, with named scenario levers, and with the
COVID period treated as signal rather than noise. That is the thing that distinguishes them from the
occupancy-generation literature.

If paper 4 drops the time axis it is a weaker paper than its predecessors, however good the
cross-national result is. So we want to know whether the longitudinal design survives the change of
method and of data source.

The obstacle is that the European waves are sparse in time. Where the Canadian GSS gave us four cycles,
HETUS gives roughly three waves spread over twenty years, and not every country is in every wave.
Three points is very little to extrapolate from, and we would rather say so than pretend otherwise.

## What we need

### Item 1. What temporal coverage actually exists

Building on `L01` item 3, and stated as a matrix we can plan from:

1. Country by wave, with fieldwork years, and the gaps marked. Which countries have **two or more**
   waves, which have exactly one, and which changed methodology between waves in a way that breaks
   comparability.
2. Are there **national** time-use surveys conducted outside the HETUS waves that extend a country's
   time series? Several countries run their own on a different cycle. If a country has five national
   surveys but two HETUS waves, that changes what is possible for that country.
3. Is there any documented **comparability warning** from Eurostat about comparing waves, for example a
   change in the coding list, in the diary instrument or in the sampling frame between the 2010 wave
   and the most recent one? A break we do not know about would be read as a behavioural trend, which is
   exactly the error our previous work guards against. **This is the single most important item in this
   prompt.**

### Item 2. Is there enough signal to forecast at all?

Ask this honestly rather than assuming the answer.

1. With two or three waves per country, what forms of temporal modelling are defensible? We expect the
   answer is: a documented **change between waves**, a **decomposition** of that change into
   compositional and behavioural parts, and a **scenario projection**, but not a fitted trend, and
   certainly not extrapolation of a two-point line. Confirm or correct.
2. Is there an established method for **decomposing** a change in aggregate behaviour into the part
   explained by the population's changing composition (ageing, employment, household size) and the part
   that is a genuine change in behaviour within demographic groups? This is a standard technique in
   several social science fields and it is exactly what our conditional model enables, since we can hold
   the conditioning distribution fixed and vary only the model, or the reverse. Name the method, its
   canonical references, and any published application to time-use data. **We think this is the
   strongest available formulation of the longitudinal claim and we want it properly sourced.**
3. What is the documented magnitude of change in European time-use between waves, for the categories
   that matter to building energy: time at home, work at home, sleep timing, meal timing? A published
   number here anchors everything.

### Item 3. COVID, which sits in the middle of the most recent wave

The most recent HETUS wave was fielded across roughly 2018 to 2020, which means some countries were
surveyed before the pandemic and some during it.

1. Establish, per country, whether fieldwork was interrupted, extended, or conducted during lockdown
   conditions. This is a data-quality landmine and it may be documented in the quality reports.
2. How have published analyses handled it? Is the accepted treatment to exclude affected months, to
   flag them, or to model them as a covariate?
3. Is there a **post-pandemic** European time-use data source that captures the durable shift in working
   from home? Our third paper found the shift in at-home presence to be substantial and it is the most
   energy-relevant behavioural change of the period. If HETUS cannot see it, what can: labour force
   survey teleworking series, national statistics on remote work, or dedicated surveys. Give the
   sources with URLs, since they become a scenario lever rather than training data.

### Item 4. Scenario levers, European edition

Our previous papers used named, re-runnable scenario levers: a working-from-home rate band for the
office channel, an in-store retail share band, a tourism trend for hotels. Each was sourced externally
and each produced a low, central and high variant, which is the design reviewers found persuasive.

For a European residential-focused paper, what are the equivalent levers, and what published projection
series would source each?

1. **Teleworking prevalence** by country to 2030 or beyond.
2. **Household composition and ageing** projections, which change the conditioning distribution rather
   than the behaviour. Eurostat publishes population projections; do they publish household
   projections at the granularity we would need?
3. **Employment and working-time** projections.
4. Anything else that plausibly moves at-home presence: retirement age changes, school calendars,
   urbanisation.

For each: is there an official projection with low, central and high variants published by Eurostat or a
comparable body, with a direct data URL? A lever we can cite to an official projection is worth far more
than one we invent.

### Item 5. The mechanism, given a language model

1. Should the year enter as a **conditioning token**, and if so, is a model conditioned on discrete
   observed years able to interpolate or extrapolate to an unobserved year at all? Our previous work
   used a continuous year projection specifically so that a future year was representable. What is the
   analogue for a token-based model, and is there evidence it works?
2. Is **progressive fine-tuning across waves**, each stage initialised from the last, sound for an LLM,
   or does it simply cause forgetting of the earlier waves? This overlaps `L05` item 5; here we want the
   temporal-specific answer, particularly whether the model retains the ability to generate an early
   year after training on a later one.
3. What diagnostic would distinguish a model that has **learned a temporal trend** from one that has
   merely memorised each wave separately? We want to pre-register this, because it is the check that
   makes the forecast claim falsifiable rather than decorative.
4. If the honest conclusion is that **a forecast is not defensible** from two or three waves, say so
   plainly. A paper that reports a well-characterised change between waves, decomposed into
   compositional and behavioural components, and declines to extrapolate, is a better paper than one
   that extrapolates from two points. We would take that answer.

## Named leads

Eurostat HETUS wave documentation and quality reports, especially any comparability notes between
waves; national time-use survey series outside the HETUS cycle; the decomposition methods literature in
demography and labour economics; Eurostat population and household projections; the labour force survey
teleworking series; published analyses of time-use change across HETUS waves.

## Hard constraints specific to this prompt

* **Do not report a trend without reporting the number of time points behind it.** Two points is not a
  trend and we want that stated wherever it applies.
* Flag every methodological break between waves that you find, even if it seems minor. A break in the
  coding list is more dangerous to us than a large genuine change, because it is invisible in the
  results.
* Distinguish a **projection published by a statistical body** from a **forecast in a research paper**.
  Only the former can serve as a scenario lever we cite.
* If the honest answer to item 5 item 4 is negative, put it in the first sentence of Section A.

## Deliverable

**Section B** carries the coverage matrix, the comparability breaks, and the measured between-wave
changes.

**Section C** carries the recommended temporal design: what we can claim with the data that exists.

**Section F** carries the projection data sources for the scenario levers, with direct URLs.

**Section G** carries the COVID fieldwork situation per country, the forecast-defensibility verdict,
and your negative controls.
