# T32. How wrong are time-use surveys about presence at home? The measured evidence

> **Corrections 2026-09-18 (round 2).** Round 1 of this prompt failed vetting: invented co-authors,
> quotes that are not on their pages, named items dropped without a word, and no page opened. These
> rules add to everything below and win where they differ.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the same CrossRef record
>   (`api.crossref.org/works/<DOI>`), never typed. If CrossRef lists two authors, you list two.
> * Every page you open, CrossRef and OpenAlex calls included, gets a line in `RT<NN>_pages.log`
>   (format in the runner). Every quote, variable name, licence, count and URL in the report must be
>   traceable to a log line. A claim with no log line is not admitted.
> * Every item and every named source below gets its own heading or card. If you could not find it,
>   write `NOT FOUND` and list the URLs you tried; they must be in the log.
> * Known prior work, supplied by us and therefore not a finding: Doma, Prajapati and Ouf 2024,
>   *Building and Environment* 261, 111713, compared ecobee occupancy with the Canadian Time Use
>   Survey. Say from its full text, if you can open it, which metric it used; else `COULD NOT OPEN`.
> * A Section C row is admitted only if one side is a time-use diary and the other a measured presence
>   source, both named, with the sentence stating the direction of the difference quoted.
> * Round 1 dropped four items; each now gets its own heading: hourly and departure or return metrics,
>   whether the populations matched, day-of-week and seasonal coverage, phones left at home.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. The negative answer ("they agree well") is as useful as
the positive one; say which the evidence supports.

## Why we are asking

All our papers treat the time-use diary as the truth about when people are home. The diary is
self-reported, covers one or two days per person, and is weighted to the population. If measured
presence (sensors, thermostats, phones, meters) disagrees with diaries in a systematic way, for
example more daytime presence than diaries report, or earlier return times, then every occupancy
model built on diaries inherits the bias, and that bias is a paper. If the two agree, the diary is
vindicated and the new sources matter only for scale and frequency. We need the measured evidence
either way.

## What we need

### Item 1. Direct comparisons

Every work that compared presence at home from a time-use survey (national or purpose-built diary)
with a measured source for comparable homes or populations. Section C rows with: countries and years;
the two sources; the metric (at-home share by hour, time of first departure and last return, daily
hours at home); **the direction and size of the difference**; whether the populations were the same
people, matched, or only comparable.

### Item 2. Known biases of diaries on presence

Evidence from the survey-methodology literature on diary error relevant to presence: recall and
rounding of start times to the hour or half hour, under-reporting of short episodes and short trips,
the single-day problem (within-person variability lost), day-of-week and seasonal coverage, non-response
by people who are rarely home. Section B rows with the quantified effect where the source gives one.

### Item 3. Known biases of the measured sources

The same for measured sources: sensors missing sleepers, thermostats in owner-occupied detached homes
only, phones not at home with the person. So that the comparison is fair in both directions.

### Item 4. Consequences in energy

Works that simulated the same buildings with diary-derived and with measured presence and reported the
energy or peak difference. Section C rows.

## Named leads

*Electronic International Journal of Time Use Research*, *Social Indicators Research*, *Journal of
Official Statistics*, *Transportation*, *Energy and Buildings*, *Building and Environment*, *Journal of
Building Performance Simulation*, *Applied Energy*; Centre for Time Use Research publications; IEA EBC
Annex 79 reports.

## Hard constraints specific to this prompt

* A comparison row must name both sources and the metric. "Surveys overestimate presence" without a
  number and a source is not admitted.
* Do not cite any number from our own papers except what brief section 2 states.
* If fewer than three direct comparisons exist, say so in the first sentence of Section A; that
  scarcity is the finding.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: how many studies compared diary presence with measured presence, and in
which direction the diaries err, if any consistent direction exists.

**Section B** is items 2 and 3. **Section C** is items 1 and 4. **Section D** assesses "the diary bias
on presence, measured, and what it does to simulated demand" as a form of `A14`. **Section G** carries
your negative controls.
