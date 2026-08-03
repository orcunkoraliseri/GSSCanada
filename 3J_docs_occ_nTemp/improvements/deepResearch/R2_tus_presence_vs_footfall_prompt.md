# Deep-Research Prompt R2 — Time-use "presence in a store" versus retail foot traffic, and what a peak-normalised TUS retail schedule is worth

> SCOPE GUARD, READ FIRST. This is a **measurement-reconciliation** task for a peer-reviewed
> building-simulation paper. The deliverable is **whether the gap between time-use-survey shopping
> presence and retail foot-traffic counts is a documented, quantified property, and whether a
> peak-normalised TUS-derived retail schedule has ever been validated against measured retail
> building loads**. It is NOT about retail sales forecasting, e-commerce market share as a business
> question, store-format strategy, or customer-experience research. If you find yourself writing
> prose about anything other than **the two measurement bases, the factor between them, and what
> happens when a TUS shape drives a retail energy model**, stop and return to the tables.

---

## Why this matters to the paper

A four-channel occupancy pipeline drives a mixed-use tall building in EnergyPlus. One channel is
retail customer presence, derived from Canadian General Social Survey time-use diaries: a respondent
counts as `AT_RETAIL` in a 30-minute slot if their harmonized location code is "shopping" (or their
activity is "purchasing goods and services" while at a plausible retail location).

The project set a validation target from an earlier deep-research round: **weekday 12:00–14:00
population retail presence rate of 0.06–0.10, central ≈ 0.079**, sourced from retail-sector foot-traffic
evidence. The measured GSS rate is **0.033–0.049 across all four cycles** — roughly **half** the
target — and the generative model reproduces the observed rate faithfully to within 0.4 pp. The gap
is therefore in the input data, not the model.

The project's working explanation is that time-use **presence** and retail **foot traffic** are
structurally different quantities: foot traffic counts entries/visits at store or mall scale,
time-use counts a person-time share of the whole population in a shopping location. That explanation
is plausible and entirely unsourced.

Two further facts make this worth resolving properly rather than waving through:

1. **The level is discarded downstream.** The injector uses a peak-normalised, shape-only multiplier,
   `0.95 × [ rate(t) / max_t rate(t) ]`, so the absolute level never reaches EnergyPlus. The level
   re-enters only through a 2030 amplitude scenario lever (0.90 / 0.97 / 1.05 relative to 2022). So
   the 2× gap may be immaterial to the result — or it may indicate the *shape* is drawn from a
   population that shops differently from the one the foot-traffic band describes.
2. **The measured series declines 25 % over the study period.** Weighted episode-time share in
   shopping locations: 2.00 % (2005), 2.14 % (2010), 1.66 % (2015), 1.50 % (2022). The project's
   design documents assert this share is "~2.1–2.3 %, stable across cycles". It is neither. And the
   2030 lever, centred at 0.97, implies near-flat in-store presence going forward — which does not sit
   comfortably next to a 25 % historical decline.

## Role

You are a building-occupancy measurement analyst. Every number must cite a named, dated source:
peer-reviewed work, a national statistical agency, an IEA Annex report, or a commercial footfall
dataset that is explicitly labelled as such. Vendor foot-traffic marketing material may be used only
as a bound and must be flagged.

---

## Part A — The two measurement bases

| Basis | What it counts | Denominator | Typical reported magnitude | Sources |
|---|---|---|---|---|
| Time-use survey "in a shopping location" | | | | |
| Retail foot-traffic / footfall counters | | | | |
| Mobile-device / SafeGraph-style visit data | | | | |
| Store point-of-sale transaction counts | | | | |
| Retail zone occupant density in energy codes (NECB / ASHRAE 90.1 prototypes) | | | | |

Then answer directly: **is there a published conversion, ratio or reconciliation between any two of
these bases?** If someone has measured, for the same population and period, both the TUS shopping
share and a footfall-derived presence rate, that study is the single most valuable thing this prompt
can return. If no such study exists, say so explicitly and count how many studies use each basis
without acknowledging the other.

## Part B — Time-use shopping shares, internationally

| Country | TUS wave(s) | Weighted share of episode-time in shopping locations / activities | Weekday midday peak rate if reported | Trend across waves | Source |
|---|---|---|---|---|---|

Cover at least: Canada (GSS), the United States (ATUS — which reports shopping as an activity
category with a long consistent series), the UK, and the Multinational Time Use Study / HETUS
harmonised European waves.

The two questions this table must answer:

1. **Is a ~1.5–2.1 % episode-time share for shopping the normal international magnitude?** If ATUS or
   HETUS report the same order of magnitude, the Canadian figure is corroborated and the foot-traffic
   band is simply a different quantity.
2. **Do other national time-use series also show a decline in in-person shopping time from the
   mid-2000s to the early 2020s, and of what size?** ATUS is annual and continuous, so it can answer
   this far more precisely than four Canadian cycles can. If ATUS shows a comparable decline, the
   Canadian trend is behavioural. If ATUS is flat, the Canadian decline is more likely instrumental —
   and the project has independent evidence pointing that way, since its 2022 cycle shows a coding
   concentration (episodes coded "purchasing" with a home location fell from 8.5 % to 4.4 % of
   purchasing episodes, while store-located ones rose from 75 % to 90 %).

## Part C — Does a peak-normalised TUS retail schedule work?

1. **Has any study driven a retail-building energy model from time-use data?** Name them. What did
   they do with the level — inject the raw fraction, peak-normalise, or calibrate to a measured load?
2. **Has any TUS-derived or footfall-derived retail occupancy schedule been validated against
   measured retail building energy or measured occupant counts?** This is the key question. If the
   answer is "nobody has done this", that is the honest state of the art and the paper should say so.
3. **What is the documented sensitivity of retail-building energy to the occupancy schedule shape, as
   opposed to its level?** Retail zones are typically lighting- and ventilation-dominated with high
   occupant density; the literature may well show that People-schedule shape is a second-order driver
   compared with lighting and opening hours. If so, that considerably reduces what rides on this
   entire question, and the paper should say that too.
4. **Is the 0.95 peak fraction in the Canadian and US energy-code retail prototypes documented, and
   what does it represent?** The injector multiplies the normalised shape by 0.95, sourced to
   NECB 2017/2020. Confirm the value and what it is a fraction *of*.

## Part D — The 2030 in-store share

The project's 2030 scenario lever is 0.90 / 0.97 / 1.05 relative to 2022. Independently of that
earlier work, state what the evidence now supports for **Canadian in-store retail presence in 2030
relative to 2022**, and say whether a central value of 0.97 is consistent with a series that fell
~25 % between 2005 and 2022. If the two are in tension, say so and give the reconciliation — for
example, if most of the historical decline is concentrated in 2015→2022 and is COVID-driven with a
documented partial recovery, that would reconcile them cleanly.

## Output format, follow exactly

1. Part A table, then the direct answer on whether a published conversion exists.
2. Part B table, then the two questions answered explicitly with numbers.
3. Part C, four short answers with citations.
4. Part D, one paragraph with a verdict on the 0.97 central value.
5. A **confidence and caveats** section: where footfall data is proprietary and unverifiable, where
   TUS definitions differ between countries (location-based versus activity-based coding is the
   critical one), and where COVID-period data should not be extrapolated.
6. A **reference list** with full citations, dates and direct links.

## Hard requirements

- **Never treat a footfall rate and a time-use presence share as the same quantity** without stating
  the conversion. The entire prompt exists because they were compared directly once already.
- **A clean negative is a result.** If no study has validated a TUS-derived retail schedule against
  measured loads, report that as the finding. It changes the paper from "our schedule is validated"
  to "no schedule of this class has been validated, and here is our population-level evidence" —
  which is a weaker but honest and publishable claim.
- **Report findings that weaken the paper plainly.** If the evidence says a peak-normalised TUS shape
  is not defensible for retail, or that the shape itself differs from footfall-derived shapes in
  timing (not just level), say so with the numbers. Timing matters more than level here, because
  timing survives the normalisation.
- Do not re-derive: the retail EUI plausibility bands, the hotel channel, the exclusivity projection,
  or the 2030 office WFH bands. Those are frozen and sourced elsewhere in this project.
