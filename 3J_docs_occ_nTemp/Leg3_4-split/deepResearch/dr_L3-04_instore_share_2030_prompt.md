# Deep-Research Prompt dr_L3-04 — IN-STORE RETAIL SHARE to 2030 (the retail scenario lever)

> SCOPE GUARD — READ FIRST. This is the **retail-trend / scenario-lever** task of the Leg-3 set. Its
> job is to turn the in-store vs e-commerce evidence into **three named, numeric 2030 scenarios for
> physical in-store customer presence**, exactly parallel to the office channel's WFH scenario bands.
> Do NOT research retail diurnal/footfall shapes (foundational Prompt-7 report already covers them), do
> NOT produce EUI benchmarks (that is `dr_L3-02`), and do NOT touch hotels (`dr_L3-01`, `dr_L3-03`,
> `dr_L3-05`). See `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A scenario-lever brief. Our pipeline models retail customer presence from Canadian GSS time-use diaries
(cycles 2005 / 2010 / 2015 / 2022) as a 48-slot presence fraction, forecast to 2030 by a fine-tuned
generative model. The office channel's 2030 forecast carries one dominant, reviewer-facing uncertainty
— the WFH rate — handled as three named sensitivity bands (conservative / hybrid / fullyhybrid) that
are a re-run, not a retrain. The retail channel needs its equivalent lever: **how much in-person retail
presence to assume in 2030**, with three defensible named bands.

> **Anchor — our own data (pre-filled, project-internal; your evidence must be reconciled with it).**
> In our harmonized GSS episode data, the weighted share of episode-time spent at shopping locations is
> **~2.1–2.3 %, roughly stable across all four cycles 2005→2022** — i.e., through fifteen years of
> e-commerce growth and one pandemic, diary-measured in-store *time* barely moved, while e-commerce
> *sales share* moved a lot. A credible 2030 lever must explain this divergence (trips vs basket size?
> time-per-trip? category mix?), not ignore it.

## Role

Retail-trends and e-commerce analyst for a building-energy study. Ground the sales side in Statistics
Canada retail-trade and e-commerce series (name exact table IDs); the physical side in foot-traffic /
mobility-data studies (mall traffic indices, post-COVID recovery analyses); the time side in time-use
research (Canadian GSS, US ATUS shopping-time trends); and the forward side in published e-commerce
projections for Canada / North America. Keep sales-share, visit-count, and time-spent evidence clearly
separated — they are three different quantities and the lever is built from the third.

## Why this matters (so you scope correctly)

The 2030 retail forecast will be challenged by reviewers with "e-commerce is killing stores — why does
your 2030 retail presence barely drop?" or the opposite ("foot traffic recovered — why does it drop at
all?"). The office channel survived the same challenge because WFH was a single explicit scalar with
three cited bands. This prompt gives the retail channel the same defence. The bands directly set the
2030 retail simulation scenarios; a wrong lever propagates into the podium-retail EUI trajectory and
the paper's longitudinal claims.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Canadian e-commerce share of retail sales, year by year

Name the exact StatCan table(s) used. One row per year (compress 2005–2014 if only sparse data exists,
but 2015–2024 must be yearly).

| Year | E-commerce share of retail sales (%) | Source table + notes (definition changes, COVID spike) |
|---|---|---|
| 2005 |  |  |
| 2010 |  |  |
| 2015 |  |  |
| 2016–2019 (yearly) |  |  |
| 2020 |  |  |
| 2021 |  |  |
| 2022 |  |  |
| 2023 |  |  |
| 2024 |  |  |

### Table 2 — Physical visit evidence (foot traffic, mobility)

| Study / index | Geography | Metric | Pre-COVID → trough → latest recovery level | Structural change noted (trip frequency vs basket size) | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### Table 3 — Time-spent-shopping evidence (the quantity our lever actually scales)

| Source | Period | Metric (min/day, participation rate, time per trip) | Trend | Citation |
|---|---|---|---|---|
| Canadian GSS analyses (published) |  |  |  |  |
| US ATUS shopping-time analyses |  |  |  |  |
| **Our GSS anchor (pre-filled)** | 2005–2022 | weighted episode-time share at shopping locations | ~2.1–2.3 %, roughly stable | project-internal (harmonized episode data) |

### Table 4 — Category heterogeneity

| Category | In-person resilience (High/Med/Low) + evidence | Implication for one aggregated podium-retail channel | Citation |
|---|---|---|---|
| Grocery |  |  |  |
| General merchandise |  |  |  |
| Personal services (salon, bank, pharmacy) |  |  |  |
| Food service adjacency (if evidence separates it) |  |  |  |

### Table 5 — THE DELIVERABLE: three named 2030 scenarios

| Scenario name | 2030 in-store presence multiplier (relative to 2022 = 1.00) | One-paragraph justification (below table) | Key sources |
|---|---|---|---|
| (e.g., Continued-Shift) |  |  |  |
| (e.g., Plateau) |  |  |  |
| (e.g., In-Store Renaissance) |  |  |  |

---

## Part C — Synthesis (the lever specification)

Give: (1) the three scenarios restated, with the central one identified as the default; (2) a
**reconciliation paragraph**: why diary-measured in-store time stayed ~flat 2005–2022 while e-commerce
sales share multiplied, and what that implies for extrapolating to 2030 (if the divergence is
trips-vs-time or category-mix, the lever should be milder than sales-share trends suggest — say so
explicitly); (3) a **mechanics recommendation**: should the lever scale presence *amplitude only*
(multiply the 48-slot fraction) or also *reshape the diurnal curve* (e.g., evening/weekend shifts)?;
(4) whether grocery-anchored podium retail justifies a more resilient central scenario than
retail-at-large.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations; StatCan table IDs explicit.
4. **"Confidence and caveats":** which scenario bound is least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **The three scenarios must be numeric multipliers on 2022 presence** — a narrative without numbers
  does not close this prompt.
- **Reconcile with the pre-filled GSS anchor** (~2.1–2.3 % stable) — any scenario implying a large
  presence collapse must explain why diary time never showed it.
- **Keep sales share, visit counts, and time spent distinct** — never substitute one for another
  without saying so.
- **No fabricated precision;** flag GAPs. **Stay on topic** — the 2030 lever only; no diurnal shapes,
  no EUI.
