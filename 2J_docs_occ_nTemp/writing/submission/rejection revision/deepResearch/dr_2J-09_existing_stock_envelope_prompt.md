# Deep-Research Prompt dr_2J-09: envelope of the EXISTING Canadian single-detached housing stock

> SCOPE GUARD, READ FIRST. This is a **search for measured or survey-based envelope values** of the
> existing housing stock, not a literature review and not a modelling task. We need numbers that describe
> the homes people live in today, not what a building code requires for new homes. **A code minimum is not
> an answer for the existing stock.** If you find nothing usable, say NOT FOUND. That is a useful result.

---

## Why we need this

We simulate Canadian homes in EnergyPlus with a single-detached house model whose envelope meets the
current national energy code for new houses (roughly: wall insulation layer about RSI 4.4, ceiling about
RSI 8.5, windows U 1.6 W/m2K and SHGC 0.4, and a tight air barrier). Our simulated energy use per floor
area is below the national end-use survey for the existing stock, and the most likely reason is that real
existing homes are older and leakier. We want to rerun the model once with an envelope that represents
the **existing** single-detached stock and see whether the gap closes.

What the numbers must allow:

| Parameter | Unit we need | Notes |
|---|---|---|
| Above-grade wall effective thermal resistance | RSI (m2K/W), effective or nominal, say which | Stock average or median |
| Ceiling / attic effective thermal resistance | RSI | |
| Foundation wall or slab insulation | RSI | Say if basements dominate |
| Window U-value and SHGC | W/m2K, fraction | Stock average, or glazing type mix |
| Air-tightness | ACH at 50 Pa (blower door) | Stock average or median |
| Scope | Single-detached houses | Split by construction period if available |
| Region | Ontario, Quebec, British Columbia, Alberta, Manitoba | National values acceptable if regional are absent; say so |
| Years | Measurements or survey data collected 2000 to 2023 | Report the collection years |

---

## Role

Data scout. You find sources, open them, and report exactly what they contain. You do not estimate, you do
not fill gaps with typical values, and you do not treat a paper that mentions a database as if it
published values from it.

---

## Where to look (search all of these, report on each)

1. **Home energy audit databases** in Canada (for example the national home energy rating programme and its
   evaluation database): published statistics of pre-retrofit wall, ceiling and foundation RSI, window type
   and blower-door air-tightness for existing single-detached houses, by province and construction period.
2. **Housing stock models built for Canada** (bottom-up residential energy models, archetype libraries,
   national energy use databases): the envelope values they assign to existing single-detached archetypes,
   and **where those values came from** (measured audits, or assumptions). Values that are only assumptions
   must be marked ASSUMED, not MEASURED.
3. **Government reports** on the residential building stock (federal and provincial energy agencies,
   housing agencies): tables of insulation levels, window types and air leakage of existing homes.
4. **Peer-reviewed studies 2005 to 2025** that report blower-door or audit statistics for large samples of
   Canadian houses.
5. **Positive control:** Swan, L.G. and Ugursal, V.I. (2009), *Modeling of end-use energy consumption in the
   residential sector: A review of modeling techniques*, Renewable and Sustainable Energy Reviews 13(8),
   1819 to 1835, DOI 10.1016/j.rser.2008.09.033. This paper is real. Report whether it, or later work by
   the same group, points to a Canadian housing database with envelope values. If your search cannot find
   this paper, your method is broken: stop and say so.

---

## Rules

- Open every source before citing it. Verify every DOI on Crossref. Give the table or page number for
  every value.
- `NOT FOUND` beats an invented number. Do not average sources yourself; list each value as published.
- Label each value MEASURED (audit or blower-door sample), SURVEY (occupant-reported), or ASSUMED (model
  input without a measured basis).
- Never give a building code requirement as a stock value.
- No em dashes and no en dashes in the report.

---

## Output format

1. **Summary verdict:** USABLE (at least wall, ceiling, window and air-tightness values for existing
   single-detached houses, MEASURED or SURVEY, national or better) / PARTLY USABLE / NOT FOUND.
2. **Table, one row per value:** parameter, value, unit, region, construction period, sample size, collection
   years, label (MEASURED / SURVEY / ASSUMED), source (full citation, DOI or URL), table or page.
3. **Positive control result.**
4. **What you could not find**, in the first person, one line each.
