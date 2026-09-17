# Deep-Research Prompt dr_2J-13: measured residential end-use energy split for Canada (calibration closure)

> SCOPE GUARD, READ FIRST. This is a **search for a measured or survey-based end-use split** of
> residential energy use, not a literature review and not a modelling task. We need numbers that
> describe what real Canadian homes actually use energy for, broken into space heating, water
> heating, appliances, lighting and space cooling. **A code-compliance estimate or a modelled
> archetype value is not an answer.** If you find nothing usable for an end use, say NOT FOUND for
> that end use. That is a useful result.

> **Gemini only, no Fable twin.** This prompt is run in Gemini Antigravity with live web search.
> Fable has no live search in this setup, and a hunt for published numeric values without search is
> worthless, so no Fable version of this prompt is planned. Do not add one later.

---

## Why we need this

We simulate four Canadian residential archetypes in EnergyPlus. The simulated total energy use per
floor area sits below Canada's national end-use household survey, and we do not yet know which end
use carries that gap. Our own simulated space heating is roughly **12.6 to 29.5 kWh per square
metre per year**, which is low for Canada. We want the measured (or survey) end-use split so the
paper can show *where* the gap sits, instead of leaving the whole EUI difference unexplained.

**This is calibration, not validation.** Whatever end-use split comes back, the paper will not
claim that agreement with the survey validates the model. It will state, at most, a **calibration
closure**: that the simulated and measured/surveyed values line up for one or more end uses, within
a stated basis. Carry this wording constraint into the report itself: do not use the word
"validate" or "validates" anywhere in what you write back to us; use "calibration" or "calibration
closure" instead.

---

## What the numbers must allow

| Requirement | Detail |
|---|---|
| End uses, named individually | space heating, water heating, appliances, lighting, space cooling |
| Units | kWh (or MJ/GJ, converted and shown) |
| Denominator, stated explicitly | energy per household, or energy per square metre of floor area; total energy or electricity only |
| Why the denominator matters | our simulated space heating is expressed per square metre of floor area, at roughly 12.6 to 29.5 kWh/m2/year, which is low for Canada; a mismatched denominator (e.g. per-household compared with per-m2) would produce a fake agreement or a fake gap. Any unit conversion you perform must be shown as a step, not silent, and the floor-area basis must be named in the source or the comparison is invalid |
| Geography | national acceptable; Ontario specifically is more useful, because our measured hourly comparison elsewhere in the paper is Toronto and Ontario |
| Dwelling type | report by dwelling type where the source allows it; our paper covers four archetypes |
| Vintage | as close to 2022 as the data allows; state the actual survey/collection year. If the nearest available year is far from 2022, report that gap as a caveat, do not smooth over it |

---

## Role

Data scout. You find sources, open them, and report exactly what they contain. You do not estimate,
you do not fill a gap with a typical value, and you do not treat a source that mentions an end-use
split as if it published the numbers.

---

## Where to look (search all of these, report on each)

1. **Canada's national household energy use survey programme** (the end-use survey NRCan runs
   periodically): the most recent published edition with an end-use breakdown by household, and, if
   available, an Ontario-specific table.
2. **Statistics Canada** household energy reports or supply-and-demand tables that break out
   residential end uses.
3. **Provincial or utility-published residential end-use studies** for Ontario specifically (for
   example a utility or system-planning end-use load research study), if they publish absolute
   intensities or shares by end use.
4. **Peer-reviewed studies 2010 to 2025** that report a measured or survey-based Canadian
   residential end-use split, by dwelling type where possible.
5. **Positive control:** find and report **total residential (household) sector energy use in Canada
   for the most recent published year**, with its publisher, table number, year and unit. This is
   widely published and trivially easy to find, and it is **deliberately not one of the five end-use
   values we need**: it is a test of whether your search works at all, kept independent of the
   values this request depends on, so that a `NOT FOUND` on an end use can be read as genuinely
   absent data rather than a broken search. Do not state its value in this prompt; report what you
   find. If your search cannot find even this, your method is broken: stop and say so, and do not
   report the end-use values as `NOT FOUND`, because at that point you have not established that
   they are.

---

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI or identifier (Crossref for DOIs).
- `NOT FOUND` beats an invented number. Do not average sources yourself; list each value as
  published, with its own source, table/figure number, and year.
- Never relax a band, or rescale a number, to make our model agree with the survey. Our simulated
  values are never adjusted to fit; report the measured/surveyed values as printed.
- **Do not let our own number steer the search.** Our simulated space heating range is given above
  only so you can spot a denominator mismatch, never as a target. Do not prefer a source because it
  sits closer to our value, and do not omit one because it sits far from it. A large disagreement is
  a useful result here: it is the answer the paper needs, not a problem to be tidied away. Report the
  most authoritative source you find, whatever it says.
- Report a partial answer as partial. If you find shares but not absolute intensities, say so
  plainly rather than presenting shares as if they were the fuller answer.
- For every number: publisher, the specific table or figure number, the reference year, and a
  resolvable URL or DOI.
- No em dashes and no en dashes anywhere in the returned report.

---

## Pre-registered decision rule (fixed before any result is read)

1. If the split is found with the end uses, the units and the denominator all unambiguous, the
   paper reports the Table 5 EUI gap broken down by end use.
2. If only percentage shares are found and not absolute intensities, the paper reports shares only
   and states plainly that it is reporting shares, not intensities.
3. If the **space heating** figure specifically is NOT FOUND, the breakdown is **not run at all**:
   the paper states that the measured end-use split was unavailable and attributes the EUI gap to
   no single end use.
4. Our simulated values are never rescaled, and no band is ever widened, to make the comparison
   agree.

---

## Output format

1. **Summary verdict:** USABLE (space heating, water heating, appliances, lighting and cooling all
   found, with units and denominator unambiguous) / SHARES ONLY / NOT FOUND.
2. **Table, one row per value:** end use, value, unit, denominator (per household or per m2, total
   energy or electricity only), geography, dwelling type, survey/collection year, source (full
   citation), table or figure number, URL or DOI.
3. **Positive control result** (total residential sector energy use for the most recent published
   year, with publisher, table number, year, unit and source). State plainly whether the control
   succeeded, because every `NOT FOUND` below is only meaningful if it did.
4. **What you could not find**, in the first person, one line each.

Save the return as `dr_2J-13_sheu_enduse_split_gemini_results.md`.
