# Deep-Research Prompt dr_2J-14: why residential load TIMING matters for the grid (citation search)

> SCOPE GUARD, READ FIRST. This is a **citation search** for two sentences in a journal manuscript.
> We need 2 to 4 real, citable sources. It is not a literature review. If nothing fits, say NOT FOUND.

> Run in Gemini Antigravity with live web search.

---

## The sentences that need a source

Our paper (residential occupancy schedules, Canada, 2022 and 2030 scenarios, hourly load shape) says:

1. Introduction: "Timing matters because a home's daily load shape, not only its yearly sum, sets its
   contribution to grid peak demand, the evening ramp, and demand-response suitability [CITATION NEEDED]."
2. Discussion: "Timing, not only the annual total, is material to how a grid operator plans for peak
   demand, the evening ramp and demand-response programs [CITATION NEEDED]."

## What a good source looks like

Each source must directly support at least one of these points, in its own words:
- (a) the hourly or sub-daily shape of residential electricity demand, not only annual energy, drives
  system peak demand or capacity needs;
- (b) the evening ramp (the late-afternoon rise in net or total demand) is a planning concern for grid
  operators;
- (c) the timing of residential load determines how much of it is available or valuable for demand
  response or load shifting.

Preferred source types, in order: peer-reviewed journal articles (2010 to 2025, ideally Applied Energy,
Energy and Buildings, Energy Policy, IEEE Transactions on Power Systems, Joule, Nature Energy); reports by
grid operators or agencies (for example a North American system operator, NERC, IEA, a national lab such
as NREL or LBNL); Canadian sources are a plus (for example the Ontario IESO or a Canadian utility), but
not required.

## Rules (standing conventions for every deep-research prompt in this project)

- Open every source before citing it. Verify every DOI via Crossref. Give the page, section or figure
  where the supporting statement appears, and quote it word for word (one or two sentences).
- NOT FOUND beats an invented source. Never fill a gap with a plausible-looking reference.
- A source that only mentions "peak demand" in passing does not count; it must make the point.
- Do not paraphrase a source into a stronger claim than it makes.
- No em dashes and no en dashes anywhere in the returned report.

## Positive control

Also find and report the Crossref record for this well-known paper, as a test that your DOI checking
works: Denholm, O'Connell, Brinkman and Jorgenson (2015), NREL, "Overgeneration from solar energy in
California: a field guide to the duck chart" (report number NREL/TP-6A20-65023). Report whether it has a
DOI or only a report number, with its URL. If you cannot find even this, say your search is broken and
stop.

## Output format

1. Summary verdict: FOUND (at least one source per sentence) / PARTIAL / NOT FOUND.
2. Table, one row per source: full citation, DOI or URL, Crossref checked (yes/no), which point it
   supports (a, b or c), exact quote, page or section.
3. Recommended citation for sentence 1 and for sentence 2 (one or two sources each, from the table).
4. Positive control result.
5. What you could not find, in the first person, one line each.

Save the return as `dr_2J-14_load_timing_grid_citation_gemini_results.md`.
