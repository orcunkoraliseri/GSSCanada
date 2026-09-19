# T28. Surveys that are not time-use surveys but ask about presence, work schedules or time at home

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
> * Every survey named in item 1 gets a card or `NOT FOUND`: LFS, Census PUMF, SHEU, Canadian Housing
>   Survey, Canadian Internet Use Survey, COVID-era telework surveys, RECS, ACS PUMS, ATUS modules,
>   EU-LFS, EWCS, EU-SILC, English Housing Survey, Understanding Society, EPA, Istat RFL.
> * Every question is copied from the questionnaire or codebook page, with its variable name as that
>   page prints it and the page in the log. A variable name not on the logged page is not admitted.
> * A use claim quotes the sentence of the abstract or text that carries the number.
> * GSS, Census PUMF and SHEU 2019 are already held; never present them as new.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Time-use surveys run every five to ten years. Many other public surveys run monthly or yearly and ask
questions that bear on occupancy: whether and how often people work from home, their usual work
hours and shift, when they leave for work, whether someone is home during the day, how the heating is
scheduled. These could update or constrain (`R2`, `R4`) the demographic mix of presence between
time-use waves, at a much higher frequency. We need an inventory of which surveys ask what, for
Canada first and then our European countries.

## What we need

### Item 1. The surveys and their occupancy questions

Data-source cards (brief section 9) for at least:

* Canada: Labour Force Survey public-use microdata (work location, work from home, hours, shift);
  Census of Population PUMF (time leaving for work, commuting duration, place of work status
  including "worked at home"); Survey of Household Energy Use (quote any question on occupancy,
  hours at home or thermostat schedules); Canadian Housing Survey; Canadian Internet Use Survey; any
  COVID-era Statistics Canada survey on telework.
* United States: Residential Energy Consumption Survey (quote the occupancy and thermostat
  questions); American Community Survey PUMS (time of departure for work); ATUS well-being and
  leave modules only if they add presence.
* Europe: EU Labour Force Survey (home-working variables); European Working Conditions Survey
  (atypical hours, telework); EU-SILC; UK English Housing Survey and Understanding Society;
  Spain Encuesta de Población Activa; Italy Rilevazione sulle forze di lavoro.

For each, quote the question wording of every presence-relevant item, give its periodicity and the
most recent edition, and say whether microdata are public.

### Item 2. Use in building energy

Works that used any of these surveys to set or adjust occupancy schedules, to weight time-use diaries,
or to project occupancy (for example work-from-home scenarios). Section C rows.

### Item 3. Consistency with time-use surveys

Studies that compared work-from-home or time-at-home shares from a labour-force survey with those from
a time-use survey for the same country and year. Report the difference and its explanation.

## Named leads

Statistics Canada PUMF catalogue and questionnaires; NRCan SHEU questionnaire; EIA RECS microdata and
questionnaire; US Census ACS PUMS documentation; Eurostat LFS and EU-SILC documentation; Eurofound
EWCS; UK Data Service; INE and Istat labour-force documentation; *Energy and Buildings*, *Energy
Research and Social Science*, *Energy Policy*.

## Hard constraints specific to this prompt

* Every question is quoted with its variable name and edition. A paraphrase is not admitted.
* We already hold the GSS time use, Census PUMF and SHEU 2019 (brief section 9). For those, report only
  presence-relevant variables we may not have used, and say so.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which public Canadian survey records time at home or work-from-home at
monthly or yearly frequency with public microdata, and has any building-energy study used it to update
time-use occupancy between waves.

**Section F** is item 1. **Section C** is item 2. **Section D** assesses "high-frequency labour and
housing surveys as between-wave updates to time-use occupancy" as a form of `A14`. **Section G** carries
item 3 and your negative controls.
