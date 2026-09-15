# Deep-Research Prompt dr_2J-06: MEASURED hourly residential electricity data for Canada

> SCOPE GUARD, READ FIRST. This is a **search for measured data**, not a literature review and not a
> modelling task. We need real, metered, residential electricity load profiles at hourly resolution
> (or finer) in Canada, around 2019 to 2023, that we can compare a simulated profile against.
> **A modelled, synthetic, or simulated profile is not an answer, however good it is.** If you find
> nothing usable, say NOT FOUND. That is a useful result and it changes a real decision.

---

## Why we need this

We simulate the hourly electricity use of Canadian homes with EnergyPlus, driven by occupancy
schedules built from national time-use surveys. The simulated profile is currently checked only
indirectly (occupancy against a held-out survey year; annual end-use totals against a national
end-use survey). We want to add a **direct check of the hourly shape** against measured household
electricity for the same period.

What we will compare, so you know what the data must support:

| Our simulated output | What the measured data must allow |
|---|---|
| Hourly electricity per household, one typical weather year | Hourly (or 15-min) household or residential-class electricity |
| Six cities: Toronto (ON), Kelowna (BC), Vancouver (BC), Montréal (QC), Calgary (AB), Winnipeg (MB) | Any of those provinces; city level is a bonus |
| Four dwelling types: single detached, attached, mid-rise and high-rise apartment | Dwelling type split if available |
| Years 2015, 2022 (and a 2030 scenario) | **2021 to 2023** is essential; 2019 as well if possible (before and after COVID) |
| Weekday and weekend average daily profile | Day type separable |
| Metrics: normalized 24-hour profile, peak hour, load factor (mean / peak), share of daily energy between about 10:00 and 16:00 | Enough to compute these, or published values of them |
| Space heating is simulated separately from plug loads and lighting | **Heating fuel must be known**, or electric heating separable; gas-heated homes are the easiest match |

---

## Role

Data scout. You find sources, open them, and report exactly what they contain and how to get them.
You do not estimate, you do not fill gaps with typical values, and you do not treat a paper that
*mentions* smart-meter data as if it *published* the data.

---

## Where to look (search all of these, report on each)

1. **Provincial smart-meter data programmes and utility data-access schemes** in ON, QC, BC, AB, MB,
   and any other province: de-identified or aggregated residential interval data available to
   researchers, the application route, fees, and lead time.
2. **Utility load-research or rate-class load profiles**: published hourly profiles for the
   residential customer class (e.g., load-profile tables filed with provincial energy regulators in
   rate cases). Report the filing, year, and whether the numbers are downloadable.
3. **System-operator data** (hourly provincial demand). Report it, but mark it clearly as
   **SYSTEM LEVEL**: it mixes residential, commercial and industrial load and is not a residential
   profile unless the operator publishes a residential split.
4. **Peer-reviewed studies using Canadian household interval data**, 2019 to 2025. For each: did the
   paper **publish** hourly profile values (table, supplementary file, data repository), or only
   figures, or only summary statistics? Is the underlying data shared or available on request?
   **Positive control:** Abdeen, A., Kharvari, F., O'Brien, W. and Gunay, B. (2021), *The impact of
   the COVID-19 on households' hourly electricity consumption in Canada*, Energy and Buildings 250,
   111280, DOI 10.1016/j.enbuild.2021.111280. This paper is real. Report what data it used, from
   where, how many households, which years, and whether its profiles can be reused. If your search
   cannot find this paper, your method is broken: stop and say so.
5. **Open data repositories** (government open-data portals, Zenodo, Figshare, Mendeley Data,
   Borealis/Dataverse, IEEE DataPort, Kaggle). For any Kaggle or aggregator copy, trace it to the
   original publisher; a copy with no traceable origin is NOT USABLE.
6. **Government and research programmes** (e.g., federal or provincial energy agencies, national
   laboratories, university research consortia) that collected residential interval data in Canada.
7. **Near substitutes, reported separately and labelled as such:** measured hourly residential data
   from cold-climate northern US states (e.g., bordering states) for the same years. Only if Canadian
   data is thin. Never mix these into the Canadian table.

---

## REQUIRED OUTPUT TABLES, fill every cell

### Table 1: Every candidate source found

| # | Source name | Publisher / owner | Live URL you opened | Measured or modelled? | Province(s) / city | Residential only? | Resolution | Years covered | Number of homes | Heating fuel known? | Dwelling type known? | Weekday/weekend separable? | Access: OPEN DOWNLOAD / PUBLISHED VALUES ONLY / APPLICATION / NOT AVAILABLE | Cost and lead time for access | Licence / reuse terms | Verdict: USABLE / PARTLY USABLE / NOT USABLE, with the reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Rules for this table:
- "Measured or modelled" must be read off the source itself. Tools and databases built from
  simulation (for example end-use load-profile libraries calibrated to meters) are **MODELLED**, even
  when they were calibrated to measured data. List them, mark MODELLED, verdict NOT USABLE for this
  purpose.
- A cell you could not determine is written **NOT STATED**, never guessed.
- If the access route is an application, give the named programme and its page, not a general
  contact page.

### Table 2: Published hourly profile values you can actually read

Only for sources where numbers (not just a figure) are available.

| Source # from Table 1 | Where the numbers are (table number, supplementary file name, repository DOI) | Province / year / day type | Peak hour reported | Load factor reported or computable | Midday (about 10:00 to 16:00) share reported or computable | Pre-COVID vs post-COVID change reported? Give the values |
|---|---|---|---|---|---|---|

### Table 3: Near substitutes (non-Canadian), same columns as Table 1

Leave empty if Canadian data is sufficient, and say so.

---

## Part C: Summary (short, facts only)

1. **Count:** how many sources are USABLE, PARTLY USABLE, NOT USABLE.
2. **The best single source** for a 2022 comparison, and what it lacks.
3. **The best source for a before/after COVID comparison** (2019 vs 2021 to 2023), if any.
4. **Fastest route to data in hand:** which usable source can be obtained soonest, and how long it
   takes (open download today, or an application with a stated turnaround).
5. **What does not exist:** state plainly any requirement that no source meets (for example, no
   dwelling-type split anywhere, no heating fuel anywhere, no open 2022 data in any province).

## Output format (follow exactly)

1. Tables 1, 2, 3, fully populated, then Part C.
2. Every row carries the live link that produced it.
3. **No recommendations about journals, methods or papers.** This is a data inventory.
4. **No em dashes and no en dashes in the returned text.**

## Hard requirements

- **Open every source you list.** Recognising a dataset name is not confirmation it exists.
- **Every DOI is checked** against `https://api.crossref.org/works/<DOI>`: the title, authors, journal
  and year at that DOI must match what you report. A DOI that resolves to a different paper is wrong.
- **NOT FOUND is a success.** Do not substitute a near match silently; put substitutes in Table 3.
- **Do not invent access terms, sample sizes or years.** NOT STATED is always allowed.
- **Do not describe a paper's data as available** unless the paper or its data statement says so.
- **No em dashes and no en dashes in the returned text.**
