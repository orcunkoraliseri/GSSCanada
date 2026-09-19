# Deep-Research Prompt dr_1J-02: what do other countries' time-use studies report about how time at home changed over the decades?

> SCOPE GUARD, READ FIRST. We want **published findings from other studies**, quoted from the source. We
> do not tell you our own results, on purpose. Do not guess what they are, and do not write anything about
> Canada's General Social Survey unless a paper you opened reports it.

Run in: Gemini (live search). Save the answer as `dr_1J-02_crossnational_occupancy_findings_results.md`
in this folder.

---

## Why we are asking

A journal reviewer asked us to compare the occupant-behaviour patterns in our Canadian study with those
reported in earlier time-use studies (the US studies based on the American Time Use Survey, and others),
"even qualitatively", and to say which patterns are specific to Canada. We will write a short comparison
table in the Discussion. We need the other side of that table: what each country's studies actually found.

## What we need (six themes; for each theme, as many countries as you can find)

- **T1. Total time at home**, and how it changed across survey years (up, down, flat or non-monotonic),
  for adults and, if reported, for households.
- **T2. Sleep duration**, and how it changed across survey years.
- **T3. Weekday versus weekend time at home**: the size of the gap, and whether it changed after 2020.
- **T4. Household size and occupancy**: whether larger households have more or fewer hours with at least
  one member at home, and whether the study defines household occupancy as "at least one member home".
- **T5. Timing of in-home activity and heat gains**: whether studies found that fixed schedules or constant
  occupant heat gains misplace the timing of presence during the day, as opposed to its total.
- **T6. The COVID-19 break**: measured time at home in 2020 to 2023 against the pre-2020 level, from
  time-use surveys (not mobility data), and whether the change persisted.

Countries, in priority order: United States (ATUS), Japan, United Kingdom, at least one EU country from
HETUS, South Korea, Australia. Other Canadian studies count too.

## Named leads (open them; they are leads, not answers)

- Sekar, Williams and Chen (2018), Joule 2, 521 to 536, DOI 10.1016/j.joule.2018.01.003.
- The Mitra, Chu and Cetin line of papers on residential activity profiles from ATUS.
- Vosoughkhosravi, Jafari and Zhu (2023), Energy and Buildings 294, 113245, a review of ATUS in energy
  modelling. Use it to find more leads.
- Yin, Yamaguchi, Zajch, Uchida and Shimoda (2024), ASim 2024,
  https://publications.ibpsa.org/proceedings/asim/2024/papers/E17_asim2024_1285.pdf (Japan, 2001 to 2021).
  **We hold the full text of this paper.** Your quotes from it will be checked against our copy word for
  word, so quote exactly.
- The US Bureau of Labor Statistics annual ATUS news releases (2019 to 2024), the UK Office for National
  Statistics time-use releases (2020 to 2023), and the Centre for Time Use Research (MTUS).

---

## Rules

- Open every source before quoting it. A finding counts only with an exact quote and a page, table or
  section number.
- Give the survey years each finding covers and its population (adults 15+, employed, households, etc.).
- Copy magnitudes exactly as written, with their unit (hours per day, minutes, percentage points). Do not
  convert or round. If the source gives only a direction, write the direction and "no magnitude stated".
- Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`).
- `NOT FOUND` beats a guess. An empty theme for a country is an acceptable answer.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Table A:** one row per finding. Columns: theme (T1 to T6), country, survey and years, population,
   direction, magnitude as written, exact quote, page or table, source with DOI or URL, DOI checked
   (yes/no).
2. **Per theme, two lines:** where the countries agree, and where they disagree.
3. **Findings that contradict each other** for the same country and theme, side by side.
4. **Search log:** sources, query strings, number opened in full.
5. **What I could not open**, in the first person, one line each.
