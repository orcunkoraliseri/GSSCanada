# Deep-Research Prompt dr_2J-16: post-2022 work-from-home trajectory, Canada (citation search and number check)

> SCOPE GUARD, READ FIRST. This is a **citation search plus a number check** for two places in a journal
> manuscript. We need the exact primary source for two numbers we already quote, and 1 to 3 sources on
> the work-from-home trend after 2022. If something cannot be confirmed, say NOT CONFIRMED or NOT FOUND.

> Run in Gemini Antigravity with live web search.

---

## Place 1: number check (Discussion)

"In Canada the share of workers mostly working from home fell from 41.1 percent in April 2020 to 18.7
percent in May 2024 [CITATION NEEDED: StatCan Daily, telework share]."

An earlier search pointed to these sources, which you must open and check yourself:
- Statistics Canada, The Daily, 26 August 2024:
  https://www150.statcan.gc.ca/n1/daily-quotidien/240826/dq240826a-eng.htm
- Statistics Canada, The Daily, 8 May 2020 (Labour Force Survey, April 2020).
- Morissette et al. (2023), Statistics Canada Catalogue 11F0019M No. 006, DOI 10.25318/11F0019M2023006-eng.

For each of the two numbers (41.1 percent, April 2020; 18.7 percent, May 2024), report: the exact
wording on the page, what population it covers (for example employees aged 15 to 69, or all employed),
what "working from home" means there (for example "most of their hours"), and the source's full
citation. If the two numbers use different definitions or populations, say so plainly: then the
sentence cannot compare them as one series, and we need to know.

## Place 2: citation search (Introduction)

"What happens to work from home after 2022 is not settled ... the share of that shift retained in 2030
is treated as an explicit, stated assumption tested across more than one value [CITATION NEEDED: source
on the post-2022 trajectory of work-from-home prevalence in Canada or comparable economies]."

Find 1 to 3 sources that report MEASURED work-from-home prevalence for 2022 or later (2023, 2024, 2025),
showing whether it has stabilised, kept falling, or risen. Preferred: Statistics Canada (Labour Force
Survey releases or analytical papers); for comparable economies, the US Survey of Working Arrangements
and Attitudes (SWAA, Barrero, Bloom and Davis) or its peer-reviewed papers, the US Bureau of Labor
Statistics, or the UK Office for National Statistics. Report the values with their dates, exactly as
published. Do not forecast and do not fit a trend yourself.

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref; for Statistics Canada pages give the
  URL, the release date and the table or chart number.
- Quote each number's sentence word for word. Do not round, rescale or combine numbers.
- NOT FOUND or NOT CONFIRMED beats an invented or approximate number.
- Do not prefer a source because it supports a particular trend; report what the most authoritative
  sources say.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report the Statistics Canada Labour Force Survey survey page (survey number 3701) URL. It certainly
exists. If you cannot find it, say your search is broken and stop.

## Output format

1. Summary verdict: Place 1 CONFIRMED / PARTLY CONFIRMED / NOT CONFIRMED; Place 2 FOUND / PARTIAL / NOT FOUND.
2. Place 1 table: number, exact quote, population, definition, source citation, URL, date.
3. Place 2 table, one row per value: value, date, country, definition, source citation, URL or DOI,
   Crossref checked (yes/no), exact quote.
4. Recommended citation(s) for Place 1 and Place 2.
5. Positive control result.
6. What you could not find, in the first person, one line each.

Save the return as `dr_2J-16_post2022_telework_trajectory_gemini_results.md`.
