# L21. How does the literature turn one or two diary days into a whole year?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief was written before nineteen reports came back and before the author took six
decisions. **Four things in it are now wrong.**

1. **The corpus is HETUS only. Canada and the United States are out of the paper.**
2. **One survey wave per country, not several.**
3. **The corpus is four countries: Italy 2013-14, Spain 2009-10, United Kingdom 2014-15, France
   2009-10.**
4. **There is no forecast and no temporal claim anywhere in the paper.** This one matters here: chaining
   days into a year is **not** a time-series prediction and must not be answered as one.

Everything else in the brief still holds, including that **the fine-tuned model will never be
released** and that **the evaluation is leave-one-country-out transfer**.

---

## The question, in one sentence

**When a published study takes cross-sectional time-use diary days and produces a continuous annual
occupancy or load profile for building simulation, what rule does it use to chain the days, what
evidence supports that rule, and how much does the choice change the simulated result?**

## Why it is being asked, so you can tell a useful answer from a complete one

Time-use surveys give each respondent **one or two** diary days. EnergyPlus needs **8,760 continuous
hours** per household. Our pipeline generates single days conditioned on demographics, season and day
type, and nothing in it currently says how 365 of those become one household's year.

The two obvious rules are wrong in **opposite** directions, which is why this cannot be settled by
picking the tidier one:

* **Independent daily resampling** — draw a fresh diary for every calendar day. This is a person with
  no habits. It washes out individual persistence and, when many dwellings are aggregated, it
  **damps** coincident peak demand.
* **Static repetition** — generate one weekday and one weekend day and repeat them all year. This has
  no day-to-day entropy at all and **exaggerates** coincidence.
* **Habit-coupled resampling** — some persistence mechanism between consecutive days, Markovian or
  otherwise, sitting between the two.

🔴 **The risk this prompt exists to size.** If the annual peak moves substantially between rules, then
the chaining convention dominates the building energy result, and our reported numbers would be
measuring our own bookkeeping rather than the cross-national transfer the paper is about. A prior round
in this series proposed testing three rules on 100 households and treating a peak difference above
roughly 25 percent as disqualifying. **That 25 percent is a project-chosen number with no literature
behind it, and one purpose of this round is to find out whether the literature supports any threshold
at all.** Do not treat it as established and do not quote it back to us as though it were.

🔴 **The convenient answer is "everyone uses one standard method and the choice does not matter
much."** That answer would let us skip an experiment, which is exactly why it must be tested hardest.
If you conclude the choice is unimportant, you must support it with a paper that **measured** the
difference, not with the absence of papers discussing it.

## What we are not asking

* Not how to model occupancy from scratch. We have the diaries.
* Not how to forecast future behaviour. There is no forecast in this paper.
* Not how to calibrate a building model against measured energy bills.
* Not weather-year selection. That is a separate and well-standardised question.

---

# PART A — THE METHODS, AS ACTUALLY PUBLISHED

## A1. Name the methods and who uses them

One row per **named method**, not per paper. For each, list the papers that use it.

| Field | What is required |
|---|---|
| Method name | As the literature calls it |
| One-sentence mechanism | What is drawn, and conditioned on what |
| Does it preserve within-person persistence across consecutive days? | Yes / No / Partially, and how |
| What it is conditioned on | Day type, season, weather, previous day, employment status, other |
| Representative papers | Author, year, title, DOI, and the journal the DOI resolved to |
| Stated justification in the paper | Quote or close paraphrase. If the paper simply asserts the rule with no justification, **say so** |

**Cover at minimum**, and add any others you find:

* Independent daily resampling from a pooled or stratified diary set.
* Static repetition of one representative weekday and one weekend day.
* Bootstrapping days **from the same respondent** where multi-day designs allow it.
* Markov chain models built on transition probabilities between activity or presence states.
* Survival or dwell-time models where the duration distribution carries the persistence.
* Any explicit day-to-day **habit** or **autocorrelation** term.
* Whole-year synthetic population approaches that assign each dwelling a persistent behavioural type.

## A2. The stochastic occupancy model lineage specifically

This literature is where the question was first faced, so treat it as a named subject rather than
letting it dissolve into the general list. For each of the following, state what the model actually
does about consecutive days, and whether the paper says so explicitly or whether you inferred it from
the method description:

* Richardson, Thomson and Infield type occupancy and demand models built from UK time-use data.
* Widén and Wäckelgård type Markov chain models built from Swedish time-use data. 🔴 **Two prior
  reports in this series gave conflicting volume and page numbers for the 2010 Applied Energy paper.
  Resolve it through CrossRef and report the title, volume, issue and pages the API returned.**
* CREST and its descendants.
* The IEA EBC Annex 66 and Annex 79 occupant behaviour outputs, if they address the chaining question
  at all. **If they do not, say that plainly** — an authoritative source that is silent on our question
  is a useful finding.
* Any activity-based model that has been coupled to EnergyPlus or to an equivalent whole-building
  engine.

## A3. What is standard practice, if anything is

Is there a **default** that reviewers in building energy simulation would expect to see? Name it, and
name the document that makes it a default: a standard, a guideline, a widely cited methods paper, or
nothing. **If the honest answer is that practice is heterogeneous and undocumented, that is the
answer**, and it changes what we have to justify in our own methods section.

---

# PART B — THE EVIDENCE THAT ANY OF IT MATTERS

Part A is a survey. **Part B is the part that decides our work.**

**B1. Has anyone measured the effect of the chaining rule on a simulated building energy result?**
Compare two or more chaining rules, same building, same weather, same everything else. For each such
study give: the rules compared, the number of dwellings, the outputs compared, and **the magnitude of
the difference with its unit**. Annual energy, annual peak power, ramp rates, and load coincidence are
all of interest, and they behave differently, so keep them separate.

🔴 **If you find no study that made this comparison, say so in one sentence and do not pad Part B with
studies that merely used one rule.** A clean negative here is a finding, and it tells us the
experiment has to be run rather than cited.

**B2. Where has the aggregate effect been quantified?** Coincidence factor, diversity factor, peak
demand per dwelling as a function of the number of dwellings. This is where independent resampling and
static repetition differ most, so any paper that reports diversity factors from time-use-derived
profiles is relevant even if it never names the chaining question.

**B3. Is there validation against measured data?** Any study comparing time-use-derived annual profiles
against measured smart meter, submetered, or sensor occupancy data, at any aggregation. State what was
compared, over what period, and what the agreement was. **This is the only kind of evidence that can
say a chaining rule is right rather than merely conventional.**

**B4. What is known about real day-to-day persistence in human activity?** From multi-day diary
designs, from panel time-use data, from mobility or smartphone traces. We need to know whether real
consecutive days are strongly autocorrelated, weakly autocorrelated, or effectively independent once
day type and season are controlled. **Give effect sizes where they exist**, and say plainly if the
question has been asked mostly in mobility research rather than in time use.

**B5. Does the multi-day structure in our own corpus help?** Three of our four countries field two
diary days per respondent, usually one weekday and one weekend day; Spain fields one. **Is a two-day
design enough to estimate a day-to-day persistence parameter at all?** Name any study that estimated
persistence from a two-day design, and state what it could and could not identify. If two days are
formally insufficient, say so and say what the minimum is.

---

# PART C — THE EXPERIMENT, IF ONE IS NEEDED

Answer these only after Part B, and let Part B decide them.

**C1.** If the comparison has not been published, what is the **smallest** experiment that would settle
it for our case? Number of dwellings, number of rules, simulation length, and the output metric that
discriminates most sharply between rules. **Name the discriminating metric and defend it**: annual
energy may be nearly insensitive while peak power is not, and picking the insensitive metric would
produce a reassuring result that means nothing.

**C2.** Is there a published basis for **any** threshold at which a modelling convention is considered
to dominate a result in building simulation? A sensitivity-analysis convention, a calibration
tolerance such as those in ASHRAE Guideline 14 or equivalent, anything citable. **If there is none, say
so**, and we will label our own threshold project-chosen, which is what we do with every unsourced
number in this project.

**C3.** What is the cheapest **diagnostic** that would tell us the rule matters, without running a full
annual simulation campaign? For example a statistic computed on the generated schedules alone that is
known to correlate with simulated peak.

---

# PART D — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: activity-resolved daily diaries generated by a fine-tuned language model
conditioned on demographics, day type and season, assembled into annual schedules, driving EnergyPlus
residential archetypes, with the paper's claim resting on cross-national transfer rather than on
absolute energy accuracy.

**Name the one thing most likely to be wrong with our day-to-year assembly specifically.** Not a
generic risk. One specific checkable thing, with the evidence that makes you suspect it and the
cheapest test that would confirm or kill it.

Two candidates we have already thought of, so do not offer either as your answer: that independent
resampling damps coincident peaks, and that static repetition exaggerates them.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all five in plain sentences in Section G.

1. **List the papers you opened in full**, separated from the papers you cite from abstract or from a
   secondary description. **A citation is not evidence until opened.** Any quantitative value in Part B
   must come from a paper in the first list.

2. **How many studies did you find that actually compared two or more chaining rules on the same
   building?** Give the number. **If it is zero, say zero.** Zero is the answer we half expect and it
   would be acted on immediately.

3. **Count the convenient findings.** The convenient answers here are: a standard method exists, it is
   well validated, the choice of rule changes results only slightly, and a defensible threshold is
   published. 🔴 **If most of those came back convenient, stop and re-check**, because it would mean a
   question that two prior rounds in this series flagged as unaddressed has in fact been settled, and
   that is surprising.

4. **Verify every DOI through CrossRef and report the title the API returned.** State explicitly
   whether any DOI resolved to a different paper than the one you cited. This series has already been
   caught three times by a real author from the right field attached to the wrong document, including
   for the Widén and Wäckelgård paper named in A2.

5. **Did you at any point answer a question about persistence in human activity from a general
   psychological or sociological claim about habit, rather than from a measurement in diary, panel or
   trace data?** Say where. A plausible statement about habit is not an effect size.

Also required, as in every round of this series:

* `NOT FOUND` beats an invented answer, always.
* Every version, threshold, quantity or tolerance carries the date it was checked and the document it
  came from.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware,
  our storage or our cluster. You cannot see them.
* Do not recommend a chaining rule on aesthetic or computational-convenience grounds. Recommend the
  one the evidence supports, or report that the evidence does not support one.
* No em dashes and no en dashes in the returned text.
