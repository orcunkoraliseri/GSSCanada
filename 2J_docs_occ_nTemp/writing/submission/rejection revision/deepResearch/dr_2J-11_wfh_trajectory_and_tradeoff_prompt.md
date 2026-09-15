# Deep-Research Prompt dr_2J-11: work-from-home to 2030, and the home versus office energy trade-off

> SCOPE GUARD, READ FIRST. Two narrow questions, both answered with **published numbers you opened**.
> Part A: how much home working exists now and what published sources say about 2030. Part B: when people
> work from home, how much does office or commercial energy fall compared with the rise at home. This is not a
> review essay. If a number is not in a source you opened, write NOT FOUND.

---

## Why we need this

Our paper builds three 2030 occupancy scenarios for Canadian homes: all of the COVID-19 rise in time spent at
home persists to 2030, half of it persists, or none of it (return to the pre-pandemic trend). We must show that
this range is grounded in published evidence, and say whether any credible source expects home working to keep
rising. We also only simulate homes; we must state, with numbers, what the literature says happens to office and
commercial energy at the same time.

---

## Role

Evidence scout. You open sources and copy what they print. You do not forecast, you do not average sources, and
you do not treat an opinion piece as data.

---

## Part A: home-working levels, 2019 to now, and outlooks to 2030

| Item | What we need | Priority |
|---|---|---|
| A1 | Canada: share of employed people who usually or mostly work from home, by year 2019 to latest | Statistics Canada Labour Force Survey or its supplements first |
| A2 | Canada: share of hours or days worked from home (hybrid counted), latest year | Same |
| A3 | United States: share of paid full workdays done from home, by year 2019 to latest | Survey of Working Arrangements and Attitudes (SWAA) |
| A4 | Any published projection or expectation for 2025 to 2035 (employer plans, economist survey, agency outlook), with the number and its horizon year | Say who produced it and how |
| A5 | Any source that reports home working still **rising** after 2023, with the number | Report NOT FOUND if none |
| A6 | Any source that reports home working **falling back** toward 2019 levels, with the number | Report NOT FOUND if none |

**Positive control, do not skip.** Barrero, J.M., Bloom, N. and Davis, S.J. (2021), *Why working from home will
stick*, NBER Working Paper 28731, DOI 10.3386/w28731. This paper is real. If you cannot find and open it, your
method is broken: stop and say so.

## Part B: residential versus commercial energy under home working

| Item | What we need |
|---|---|
| B1 | Studies that estimate, for the same population or region, both the increase in household energy and the decrease in office or commercial building energy when people work from home. Give both numbers, units, region, year, method (measured, simulated, statistical) |
| B2 | Whether the net effect is reported, and its sign, with the conditions it depends on (commuting included or not, climate, heating fuel, office occupancy policy) |
| B3 | Any Canadian or cold-climate study of B1 or B2 |
| B4 | Any review 2020 to 2026 that summarises B1 across studies, with its stated range |

---

## Rules

- Open every source before citing it. Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`).
- Every number carries its table, figure or page and the exact definition used (for example "usually worked
  most hours at home" versus "any hours at home").
- `NOT FOUND` beats an invented number. Do not convert or combine numbers from different sources.
- Label each source DATA (survey or measurement), MODEL (simulation or projection), or OPINION (commentary).
  OPINION rows may be listed but are never USABLE.
- Newspaper or blog summaries of a survey are not the survey: open the survey release itself.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict per part:** USABLE / PARTLY USABLE / NOT FOUND.
2. **Table A, one row per number:** item (A1 to A6), value, unit and exact definition, country, year, label
   (DATA / MODEL / OPINION), source with DOI or URL, table or page.
3. **Table B, one row per study:** residential change, commercial change, net, units, region, years, method,
   label, source with DOI or URL, table or page, what the net depends on.
4. **Positive control result.**
5. **What I could not find or open**, in the first person, one line each.

Save the return as `dr_2J-11_wfh_trajectory_and_tradeoff_results.md`.
