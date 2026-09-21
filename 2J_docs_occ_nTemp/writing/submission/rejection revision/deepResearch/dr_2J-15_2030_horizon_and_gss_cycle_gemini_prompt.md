# Deep-Research Prompt dr_2J-15: 2030 as a planning horizon, and the next Canadian time-use survey (citation search)

> SCOPE GUARD, READ FIRST. This is a **citation search** for one sentence that makes two claims. We need
> real, citable sources for each claim. If a claim has no source, say NOT FOUND for it. That is useful:
> the author will then cut that half of the sentence.

> Run in Gemini Antigravity with live web search.

---

## The sentence that needs a source

"This study uses 2030 as its scenario horizon because it sits beyond the latest available survey data,
requiring an explicit assumption about how far the pandemic-era change has settled or receded, and
because 2030 is a commonly used planning horizon [CITATION NEEDED: source establishing 2030 as a
recognized planning horizon, and the timing of the next comparable time-use survey cycle]."

The latest survey data we use is Statistics Canada's General Social Survey (GSS) on Time Use, 2022 cycle
(earlier cycles used: 2005, 2010, 2015).

## Claim A: 2030 is a recognized planning horizon (energy or buildings, Canada preferred)

Find 2 to 3 official documents that plan to, or set targets for, the year 2030 in energy, electricity or
buildings. Canadian federal or Ontario/Quebec sources are best; one international source (IEA, UN, EU)
is acceptable as a second. Examples of the kind of document we mean, which you must still find and open
yourself: a national emissions reduction plan with 2030 targets, a system operator's long-term demand or
resource outlook that runs to or past 2030, an IEA scenario report with 2030 milestones.

For each: the exact passage that names 2030 as a target or planning year, with page or section.

## Claim B: timing of the next comparable GSS Time Use cycle

Find what Statistics Canada has published about the GSS Time Use cycle schedule: past cycle years, the
usual interval between cycles, and whether a next Time Use cycle after 2022 has been announced, with a
year. If nothing is announced, report the published interval pattern and say plainly that no next cycle
year was found. Do not guess a year.

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref; for government pages, give the URL
  and the page's own publication or modification date.
- Quote the supporting passage word for word, with page or section.
- NOT FOUND beats an invented source or an inferred date.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Report the Statistics Canada survey page (survey number and URL) for the GSS Time Use 2022 cycle
(sometimes listed as GSS Cycle 37). This certainly exists. If you cannot find it, say your search is
broken and stop; do not report Claim B as NOT FOUND.

## Output format

1. Summary verdict per claim: FOUND / PARTIAL / NOT FOUND.
2. Table, one row per source: full citation, URL or DOI, Crossref checked (yes/no), claim (A or B),
   exact quote, page or section.
3. Recommended citation(s) for claim A and for claim B.
4. Positive control result.
5. What you could not find, in the first person, one line each.

Save the return as `dr_2J-15_2030_horizon_and_gss_cycle_gemini_results.md`.
