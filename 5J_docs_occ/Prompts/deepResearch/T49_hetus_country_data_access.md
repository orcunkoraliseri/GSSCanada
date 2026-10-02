# T49. Which European time-use diary datasets can this researcher actually obtain, and under what terms?

Paste `00_MASTER_BRIEF_5J.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh session. **Run it alone**
(T48 covers the UK licence in depth; here the UK appears only as one row). Written 2026-10-01 by the 5J manager at the
author's request ("include Italy, Spain and UK, if possible France as well; search other HETUS countries").
Your files are `RT49_hetus_country_data_access.md` and `RT49_pages.log` (one line per page, PDF or record you opened: URL,
what it was, full / partial / title only, date). Save both in this folder.

## Why we are asking

The study now uses household time-use diaries from **Spain** (INE, Encuesta de Empleo del Tiempo 2009-2010, open download)
and **Italy** (ISTAT, Indagine Uso del tempo 2013-2014, public-use file). The UK file (UK Time Use Survey 2014-2015, UK Data
Service SN 8128) is held but on hold for licence reasons. France was requested through Progedo (request n. 38663): the approval
covered six other files but **not** the diary file "lil-1065, Emploi du temps (version pour Eurostat) 2009-2010".

The author wants more countries, so that the surrogate can be trained and tested across more climates and household
patterns. Before any design change we need to know, country by country, **which diary microdata can be obtained by this
researcher, how, how fast, at what cost, and under which terms for derived outputs.**

The researcher: a postdoctoral researcher at Concordia University, Montreal, Canada (outside the EU), sole author, no
commercial purpose. Results would be published in a journal; the code would be released; trained model weights and simulation
outputs may or may not be shared, depending on the terms.

What the study needs from each dataset (state for each whether it is available):
* a diary of at least one full day per person, in time slots of 10 or 15 minutes, with main activity, secondary activity and
  location (at home or not);
* **all household members** diarised, or at least household composition (size, ages) linked to each diary;
* the diary day (weekday or weekend; month or season) and a region coarse enough to choose a weather city;
* survey weights.

## Part 1. The list of countries

From Eurostat's own HETUS pages, list every country in the **HETUS 2010 wave** and every country that has delivered data to
the **HETUS 2020 wave** (round around 2020 to 2024), with survey name, fieldwork years and national publisher. Quote the
Eurostat page that gives the list, with its date. Also say whether **Eurostat itself** distributes HETUS microdata to
researchers (and under which scheme), or only aggregate tables.

## Part 2. Access per country (Section F, one row per country and wave)

For each country found in Part 1, plus France (both the 2009-2010 survey and any newer survey), report:

1. Microdata release type: open download, public-use file, scientific-use file after application, remote or secure access
   only (safe centre, research data centre), or not released.
2. Who may apply: is a researcher at a non-EU (Canadian) university eligible? Quote the eligibility sentence.
3. Application route: the exact URL of the request form or catalogue record, the documents asked for, the fee, and any stated
   processing time.
4. What the file contains, against the four needs above (yes / no / not stated, with the documentation page that says so).
5. Terms on outputs: may results, derived data, synthetic data, trained models and model outputs be published or shared?
   Is there any rule on online tools or generative AI? Quote the clause.
6. Citation wording required.

Rows for **Spain** and **Italy** are positive controls: we hold both files. Spain: open download from INE, reuse under
CC BY 4.0 with the INE attribution wording. Italy: ISTAT public-use file. If your row contradicts this, quote the page.

## Part 3. Harmonised alternatives

The Multinational Time Use Study (MTUS, Centre for Time Use Research) and any other harmonised collection (for example IPUMS
Time Use) may include European countries, the UK and France among them. For each collection: which European countries and
years it holds, whether it carries the full episode diary or only daily totals, whether all household members and household
composition are included, who may register, and its terms on derived outputs, synthetic data and AI tools. Quote the terms
page.

## Part 4. Ranking for this study (Section E)

Rank the countries into three groups, each line tied to a row of Part 2 or 3:
* **A. Obtainable now** by this researcher (open or quick registration), with all four needs met.
* **B. Obtainable with an application** (state the expected wait and any fee).
* **C. Not obtainable** by this researcher (eligibility, remote-only access that excludes simulation use, or no microdata).

Do not rank by how useful a country would be for the science; rank only by access and terms. Do not suggest changing the
study design.

## Hard constraints specific to this prompt

* **Positive controls:** the Spain and Italy rows (above).
* **Negative control:** look up the data set "HETUS 2010 public-use microdata file, release HETUS-PUF-2010-v9, Eurostat".
  It must come back `NOT FOUND`. If you describe it, the round fails.
* Open every page you cite and log it. A catalogue search page is not an answer; the row then reads `NO RETRIEVABLE RECORD`.
* Every eligibility, fee, time or licence statement is quoted with its URL and date. `NOT STATED` is a good answer.
* Do not ask for, open or describe any diary file or record. Nothing in this prompt needs microdata.
* No em dashes and no en dashes anywhere.

## Deliverable

**Section A** (at most six sentences): how many countries are obtainable now, with an application, or not at all, and which
harmonised collection, if any, is the fastest route to more countries. **Section B**: one row per citable statement.
**Section C**: `not applicable to this prompt`. **Section D**: `not applicable to this prompt`. **Section E**: the ranking of
Part 4. **Section F**: the access table of Parts 2 and 3 (country, wave, release type, eligibility quote, URL, fee, time, the
four needs, output terms, AI-tool terms). **Section G**: both controls, pages you could not open, contradictions, the four
standard questions. **Section H**: full references.
