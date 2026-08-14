# L01. Can we actually get HETUS microdata? Access route, eligibility, coverage, and how long it takes

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections are used. **Section F is the deliverable of this prompt.**

> **Run this prompt first.** Every other prompt in the series assumes an answer to it. If the answer is
> that microdata cannot be obtained, the paper becomes a different paper, and we would rather learn that
> in week one than in month six.

## Why we are asking

Our plan is to fine-tune an open-weight language model on harmonised European time-use diaries so that
one model serves every participating country. We currently hold **Italian ISTAT** time-use and census
microdata (used in Energy and Buildings 357 (2026) 117155) and **Canadian GSS** time-use microdata. We
hold **no** HETUS file of any kind.

We do not know, and cannot establish from the Eurostat portal alone, whether "HETUS" is:

* a **microdata product** that a researcher can be granted, respondent by respondent, diary by diary; or
* only a **tabulation service**, where Eurostat publishes aggregated statistics computed centrally and
  the underlying records never leave the national statistical institutes; or
* both, on different terms, for different waves.

This distinction decides the whole project. Training a generative model requires records. Aggregate
tables can validate a model but cannot train one.

## What we need

### Item 1. What HETUS actually releases, precisely

1. State plainly, in one sentence each: does Eurostat release **HETUS individual-level microdata** to
   external researchers, and does Eurostat release **HETUS diary-level records** (the slot-by-slot
   sequence, which is the object we need). These may have different answers and the diary file is the
   one that matters to us. Do not merge them.
2. Name the exact product or dataset code, as Eurostat names it, for each thing that is released. If
   the diary file is not released, say so as its own sentence.
3. Distinguish the **HETUS online database of aggregated tables** from any microdata product, and give
   the URL of each separately.

### Item 2. The access instrument, step by step

For every route that exists, one row each:

1. **Which instrument.** Eurostat scientific-use file, secure-use file, remote-access facility,
   on-site safe centre visit, or an application to each national statistical institute individually.
2. **Who is eligible.** Specifically: is a **postdoctoral researcher at a Canadian university** eligible
   for the European route, or is eligibility restricted to research entities established in the EU or
   EEA? This is the single question we most need answered and we suspect the answer is unfavourable. If
   a Canadian institution is not eligible, say so in the first sentence of Section A.
3. **What the applicant submits.** The forms, the research proposal requirements, whether an
   institutional signature or a recognised-research-entity status is required, and what that status
   requires.
4. **Cost.** Fee or no fee, and if there is a fee, the amount and the date you checked it.
5. **Time.** The published or documented turnaround from application to data, and where that figure
   comes from. If no turnaround is published, write `NOT PUBLISHED` rather than guessing.
6. **What comes back.** File format, whether the activity codes are the full ACL or a collapsed
   version, whether survey weights are included, and whether the diary sequence arrives as one row per
   slot, one row per episode, or one row per diary with wide columns. This shapes our entire
   preprocessing stage.
7. **What is forbidden with it.** Redistribution, derived-data publication, model publication. Note the
   clause numbers; prompt `L10` goes deep on this and will build on your answer here.

### Item 3. Coverage: which countries, which waves, which variables

We need a table we can plan a training corpus from.

* Which **waves** exist. Our understanding is that there have been roughly three rounds, around 2000,
  around 2010, and a round conducted approximately 2018 to 2020 whose results have been appearing since.
  **Correct this if it is wrong.** Give each wave its proper Eurostat name and its reference years.
* Which **countries** are in each wave, and for each country the fieldwork years. A country that appears
  in one wave and not another matters to us because our previous papers are longitudinal.
* Whether the **diary slot resolution** is genuinely uniform across countries and waves, or whether some
  countries used a different interval or a different number of diary days per respondent.
* Whether **each respondent contributes one diary day or two** (a weekday and a weekend day is the
  pattern we expect), because that decides whether we can model day-to-day dependence at all. Our own
  published work names the single-day limitation of time-use diaries as a structural weakness, so if
  HETUS gives two linked days that is a finding worth its own row.

### Item 4. The fallback corpus, if HETUS microdata is closed to us

If item 2 concludes that we cannot get HETUS microdata from Canada in a reasonable time, we need a
second corpus that is **genuinely multi-country and genuinely accessible**. Assess each of these, one
row each, with the same access columns as item 2:

1. The **Multinational Time Use Study (MTUS)**, Centre for Time Use Research. Is it harmonised at the
   episode or diary level, how many countries and years, and what is the access instrument for a
   non-EU academic?
2. The **American Time Use Survey (ATUS)**, US Bureau of Labor Statistics, including its ATUS-X or IPUMS
   Time Use distribution. We believe this is fully public. Confirm, and say whether the activity coding
   can be crosswalked to the HETUS ACL, and whether such a crosswalk has been published by anyone.
3. **National open microdata releases** from individual HETUS participating countries that publish their
   own time-use microdata directly, without going through Eurostat. Spain's INE, the UK's time use
   survey via the UK Data Service, Italy's ISTAT (which we already hold), France's INSEE, and any
   others you find. For each: is the diary file itself downloadable, on what terms, and by whom.
4. The **Canadian GSS time-use** cycles, which we already hold, as a non-European member of a multi-
   country corpus.

We would rather build the paper on five countries we can actually download than on twenty we cannot.
**Say explicitly which combination you would build a corpus from, given a Canadian-based applicant and
a twelve-month horizon.**

### Item 5. What the aggregate tables can and cannot do for us

Independently of microdata, Eurostat publishes HETUS results as aggregate tables. Tell us:

1. What the finest granularity of the published tables is: by country, by sex, by age band, by
   employment status, by day type, by activity category, and at what time resolution. Can a published
   table give the **share of the population performing activity X at time-of-day T**, per country?
2. Whether those tables are downloadable in bulk, machine-readable, and under what licence.

The reason this matters is that a public table of that shape is an **external validation target we do
not have to negotiate for**. It would let us score a model trained on whatever microdata we can get,
against the population statistics of countries whose microdata we cannot get. That is a strong paper
design and it depends entirely on the granularity of those tables, so please be precise.

## Named leads

`ec.europa.eu/eurostat/web/time-use-surveys` and the Eurostat microdata access pages
(`ec.europa.eu/eurostat/web/microdata`); the Eurostat *Harmonised European Time Use Surveys*
guidelines documents (there have been successive editions, we believe around 2000, 2008 and 2018, and
the 2018 edition is the one that governs the most recent wave); Commission Regulation and Commission
Implementing Regulation texts governing access to confidential data for scientific purposes;
`timeuse.org` and the Centre for Time Use Research at University College London for MTUS;
`bls.gov/tus` and `timeuse.ipums.org` for ATUS; `ine.es`, `ukdataservice.ac.uk`, `istat.it`,
`insee.fr` for national releases.

## Hard constraints specific to this prompt

* **Do not report an eligibility rule you have not read in a governing document or an official access
  page.** This is exactly the kind of claim that is easy to state plausibly and wrong. If you can only
  find a secondary description, label the row `INFERENCE` and say what document would settle it.
* **Do not report a turnaround time as a fact unless it is published.** An anecdote in a forum post is
  not a source for this.
* Do not propose that we simply use synthetic or simulated time-use data instead. That is the thing we
  are building, not an input we can assume.
* Do not recommend a commercial data broker.

## Deliverable

**Section A** opens with a one-sentence verdict: can a Canadian-based postdoctoral researcher obtain
HETUS diary-level microdata, yes, no, or only under a named condition.

**Section F** is the artefact table: every access page, every application form, every guidelines PDF,
every fallback dataset landing page, each with a direct URL and a confirmed reachability flag.

**Section G** carries the corpus recommendation from item 4, and your negative controls.
