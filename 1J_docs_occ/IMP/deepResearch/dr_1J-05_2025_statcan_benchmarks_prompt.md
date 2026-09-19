# Deep-Research Prompt dr_1J-05: which official 2025 Statistics Canada figures can check a projected 2025 population?

> SCOPE GUARD, READ FIRST. This is mainly a **where-is-the-table** question. For each item we want the
> official table that exists (its number, title, URL, reference period and geography). Copy a value only
> when it sits in that table, and copy it exactly with the table number and reference date next to it.
> An item with no table must be written `NO TABLE FOUND`. That is an acceptable answer.

Run in: Gemini (live search). Save the answer as `dr_1J-05_2025_statcan_benchmarks_results.md` in this
folder.

---

## Why we are asking

Our paper generates a synthetic 2025 population of households. There was no census in 2025, so we want to
compare our projection against independent official 2025 figures from Statistics Canada. We first need to
know which figures exist, for which geography, and with which categories.

## What we need

For each variable below, for **Quebec** and for **the Montreal census metropolitan area** (and for Canada
if the other two are missing), the most recent Statistics Canada table with a reference period in 2024,
2025 or 2026:

1. Population by age group and sex.
2. Households by household size.
3. Dwellings or households by structural type of dwelling (single-detached, row house, apartment, etc.).
4. Marital status.
5. Labour force status (employed, unemployed, not in the labour force).
6. Class of worker (employee, self-employed).
7. Usual weekly hours worked.
8. Occupation (broad groups).
9. **Where people work**: share working at home all or part of the time (for example from the Labour Force
   Survey).
10. Main mode of commuting.
11. Household income.
12. Tenure (owner or renter).

For each table also say: survey source (Labour Force Survey, demographic estimates, Canadian Housing
Survey, other), whether its categories match the Census categories, and whether it is monthly, annual or
occasional.

**Control item, do not skip.** From the 2021 Census, transcribe the official table of **private households
by household size for Quebec** (table number, all size categories, counts). We hold the 2021 Census
microdata and will check your transcription against it.

## Named leads

Statistics Canada data tables (the 17-10, 14-10, 98-10 and 46-10 table families), the Labour Force Survey
monthly and annual releases, the Canadian Housing Survey, and The Daily. These are leads: confirm each
table number on the page you open.

---

## Rules

- Every table number must be one you opened. Give its full URL.
- Copy values exactly as published. Do not compute, convert, interpolate or combine values.
- Do not say whether any value supports or contradicts a projection.
- `NO TABLE FOUND` beats a guess.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A:** one row per variable and geography. Columns: variable, geography, table number, table
   title, URL, survey source, reference period, frequency, categories match the Census (yes/no/partly),
   note.
2. **Table B (control item):** 2021 Census, Quebec, private households by household size, exactly as
   published, with table number and URL.
3. **Tables opened in full**, as a list, and for each `NO TABLE FOUND`, one line on where you looked.
