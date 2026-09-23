# Deep-Research Prompt L36: measured hourly household electricity profiles for Spain, Italy and the United Kingdom

> SCOPE GUARD, READ FIRST. This is a **data-source search**. We need published, MEASURED (or
> officially standardised) average hourly electricity demand profiles of RESIDENTIAL customers in Spain,
> Italy and the United Kingdom, so that we can compare the TIMING of the daily peak of a modelled
> appliance load against real data. Your job is to find the datasets or publications, verify that they
> exist and say exactly what they contain. Do not compute anything for us, do not compare anything with
> our model, and do not guess numbers. If a source cannot be confirmed, write NOT FOUND. An honest
> NOT FOUND is better than a guessed profile.

> Run in Gemini Antigravity with live web search. Save the return as
> `RL36_measured_residential_load_profiles.md` in this folder (`4J_docs_occ/DeepResearchPrompts/`).

---

## Context (for you, not to be cited)

A journal paper (target *Energy and Buildings*) drives one appliance-electricity model with daily
time-use diaries from three countries (Spain 2009-10, Italy 2013-14, United Kingdom 2014-15) and reports
the hour of the stock-average daily appliance peak per country. The only external check so far used a
British reference profile built around the year 2000 for all three countries, which is not a fair test for
Spain or Italy. We want one independent, country-specific check per country: the hour of the peak and the
normalised shape (each hour's share of daily energy) of real household demand. We will do the comparison
ourselves; we only need the sources. Our own modelled values are deliberately NOT given here.

---

## What we need

For EACH of Spain, Italy and the United Kingdom, find up to three sources, best first, of an hourly (or
finer) average residential electricity demand profile. For each source report:

1. What it is: measured smart-meter or panel data, a regulator's or system operator's standard load
   profile used for settlement, a survey with metering, or a modelled profile. Say which. Modelled
   profiles are the last resort and must be labelled as such.
2. Population: households only, or mixed with small business; number of households metered; region;
   whether electric heating or electric water heating is included or can be excluded.
3. Period: years covered; whether weekday and weekend (or day types) are separated; season or month
   resolution.
4. Resolution: hourly, half-hourly, 15-minute.
5. Access: exact URL of the data file or table, licence, whether free download or registration needed,
   file format. Give the page where the numbers are, not only the home page.
6. The HOUR OF THE DAILY PEAK and the hour of any secondary peak, for a weekday, as printed in the source
   (a table or a figure you actually saw). If you only saw a figure, say "read from figure" and give the
   figure number. If you did not see it, write NOT SEEN; do not estimate.
7. Citation in Elsevier author-year style, with DOI where one exists, Crossref-checked.

## Named leads (candidates only, NOT verified by us; confirm or reject each)

- **Spain:** Red Electrica de Espana (REE) and the CNMC regulator publish "perfiles de consumo" (standard
  initial consumption profiles, for example tariff 2.0TD or the older 2.0A / 2.0DHA) used for billing
  households without hourly meters; REE's e-sios platform; datadis (distributors' smart-meter portal);
  IDAE's SPAHOUSEC household energy study (2011).
- **Italy:** ARERA (the energy regulator) and Terna; standard load profiles for household customers
  (for example "profili di prelievo standard" or residential load profiles published by the
  distribution operators such as e-distribuzione); the RSE (Ricerca sul Sistema Energetico) residential
  studies; the MICENE or earlier eERG Politecnico di Milano metering campaigns.
- **United Kingdom:** Elexon standard settlement Profile Class 1 (domestic unrestricted) and Profile
  Class 2 (domestic Economy 7); the Household Electricity Survey 2010-11 (DEFRA/DECC, 250 households,
  appliance-level metering); the Low Carbon London or Customer-Led Network Revolution smart-meter trials;
  the Smart Energy Research Lab (SERL) data.
- Cross-country: any European Commission JRC or EU project (for example REMODECE, 2008, residential
  monitoring in several EU countries) that gives per-country household daily profiles on one basis.

## Specific questions

A. Is there ONE source that gives household hourly profiles for all three countries on a comparable
   basis? If yes, it is preferred over three separate sources.
B. For the standard settlement profiles (REE/CNMC, ARERA, Elexon): do they reflect measured household
   demand, and from which year's sample? Are they appliance-only or total household demand?
C. Which of these sources lets us separate appliance and lighting demand from space heating and water
   heating? If none does, say so.

---

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref (https://api.crossref.org/works/<DOI>)
  and say for each whether you did. State whether you opened the data file itself or only a page
  describing it.
- A peak hour must come from a table or figure you actually saw, with its number. NOT SEEN is acceptable;
  an estimate is not.
- Do not relax the standard because a source is convenient: a settlement profile for mixed small business
  and households must be labelled as mixed.
- NOT FOUND beats an invented or approximate source.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report what Elexon's Profile Class 1 is (one sentence) and the URL of Elexon's page describing the
standard load profiles. It certainly exists. If you cannot find it, say your search is broken and stop.

## Output format

1. Direct answer (5 lines): the best usable source per country, and whether one common source exists.
2. One table per country: source, type (measured / standard settlement / survey with metering / modelled),
   households, years, day types, resolution, heating included or separable, weekday peak hour (or NOT
   SEEN), where seen (table/figure number), access URL, licence.
3. Answers to questions A, B and C.
4. Full reference list, Elsevier author-year style.
5. Positive control result.
6. What you could not find, in the first person, one line each.
