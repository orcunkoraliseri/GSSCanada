# Deep-Research Prompt dr_L3-06 — RETAIL DIURNAL PRESENCE: numeric validation targets + multiplier normalization

> SCOPE GUARD — READ FIRST. This is the **retail shape-and-targets** task of the Leg-3 set. Its job is
> to turn the retail-occupancy literature into (a) **numeric per-day-type validation targets** for our
> GSS-derived AT_RETAIL channel and (b) a sourced answer to the **normalization question** — how a
> population presence *fraction* becomes a schedule *multiplier*. Do NOT forecast retail trends to 2030
> (that is `dr_L3-04`), do NOT produce EUI benchmarks (`dr_L3-02`), and do NOT redo the general retail
> occupancy landscape (the foundational Prompt-7 report in `deepResearch_Resources/` covers it). See
> `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A targets-and-normalization brief. Our AT_RETAIL channel is a 48-slot binary presence track derived
from Canadian GSS time-use diaries: for each 30-min slot, the *weighted fraction of the whole
population* currently at a shopping location. Known anchors from our own data and planning docs:
weekday peak ~11:00–14:00, weekend ~12:00–16:00, all-day episode-time share **~2.1–2.3 %**, and a
project-chosen validation gate of **0.06–0.10 population fraction at weekday 12:00–14:00** that has
never been checked against external evidence. This prompt hardens those targets and resolves how the
population fraction should scale the NECB retail baseline schedule.

> **The normalization question, precisely.** NECB/ASHRAE retail schedules are *fractions of design
> occupancy* (peak ≈ 0.9 at busy hours). Our `at_retail_fraction(t)` is a *fraction of the population*
> (peak ≈ 0.08). Multiplying the baseline by the raw fraction would collapse retail occupancy to ~8 %
> of design load — obviously wrong. Candidate mappings: peak-normalize the GSS curve (shape-only
> injection, amplitude stays code); anchor amplitude to a per-cycle reference year; or scale by an
> external footfall-per-area statistic. We need the literature's answer, not an ad-hoc choice.

## Role

Retail-analytics and building-schedules researcher. Ground the standards side in the actual published
schedule fractions (NECB 2017/2020 retail, ASHRAE 90.1 Appendix G retail, DOE / PNNL Standalone Retail
prototype schedule objects). Ground the empirical side in measured footfall / traffic-counter /
mobility studies (malls, high-street, grocery, big-box). Ground the normalization side in any published
time-use-driven or survey-driven commercial schedule study — how did *they* map a population-level
presence signal onto a building-level schedule? Distinguish customer presence from staff presence
throughout.

## Why this matters (so you scope correctly)

These numbers become the Step-4 validation gates for the new Transformer head: if the targets are
wrong, the head is tuned to reproduce the wrong curve for 26 simulated years. And the normalization
choice decides what the retail channel physically *means* in EnergyPlus — shape-only injection vs
amplitude injection produce different EUI trajectories from identical GSS data. The Leg-2 office
channel ducked this by construction (workforce fraction ≈ office-attendance fraction); retail has no
such luck, because shoppers are a small share of the population but fill stores to design capacity at
peak.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Standard retail schedule fractions (fractions of design occupancy)

| Source | Weekday: open hours + peak fraction + peak window | Saturday | Sunday | Night / closed fraction | Citation |
|---|---|---|---|---|---|
| NECB 2017/2020 retail schedule |  |  |  |  |  |
| ASHRAE 90.1 Appendix G retail |  |  |  |  |  |
| DOE / PNNL Standalone Retail prototype |  |  |  |  |  |

### Table 2 — Measured customer footfall curves (empirical)

| Study / dataset | Retail format (mall / high-street / grocery / big-box) | Weekday peak window + relative level | Saturday | Sunday | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### Table 3 — Customer vs staff timing (who is in the store when)

| Quantity | Value / timing | Source |
|---|---|---|
| Staff arrival before opening / departure after close (typical lead/lag) |  |  |
| Staff-to-customer ratio at peak vs off-peak |  |  |
| Which end-uses follow customers vs staff vs opening hours |  |  |

### Table 4 — The normalization question (population fraction → schedule multiplier)

| Mapping option | Any published precedent? (cite) | Pros | Cons / bias | Verdict (recommended / viable / reject) |
|---|---|---|---|---|
| Peak-normalize GSS curve per cycle (shape-only; amplitude stays code) |  |  |  |  |
| Fix normalization to one reference cycle (longitudinal amplitude changes carried) |  |  |  |  |
| External anchor (footfall-per-m² or sales-per-m² statistic sets amplitude) |  |  |  |  |
| Raw population fraction as multiplier |  |  |  | (expected: reject — state why in sourced terms) |

### Table 5 — RECOMMENDED VALIDATION TARGETS (the deliverable)

| Day type | Peak window | Peak value (state basis: population fraction / normalized shape) | Midday 12:00–14:00 population fraction (verdict on our 0.06–0.10 gate) | Night (00:00–05:00) | Basis (measured / standard) |
|---|---|---|---|---|---|
| Weekday |  |  |  |  |  |
| Saturday |  |  |  |  |  |
| Sunday |  |  |  |  |  |

---

## Part C — Synthesis (targets + normalization verdict)

Give: (1) the recommended per-day-type targets restated, flagging any where evidence contradicts our
pre-set 0.06–0.10 weekday-midday gate (say plainly "keep", "widen to X–Y", or "replace"); (2) the
**normalization recommendation** from Table 4 with its strongest citation, and the exact formula the
Step-7 injector should implement; (3) how the longitudinal signal survives the chosen normalization —
if the shape is peak-normalized per cycle, state explicitly where the 2005→2022 retail *level* change
is carried (amplitude term, conditioning, or lost); (4) a one-paragraph note on Sunday-shopping
regulation differences (Quebec vs Alberta store-hours law) if the evidence shows they matter for a
two-city sweep.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations; measured vs standard-assumed flagged per cell.
4. **"Confidence and caveats":** which target is least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Table 4 must reach a single recommended mapping with a precedent citation** — "it depends" does not
  close this prompt.
- **Always state the basis of every fraction** (population fraction vs fraction-of-design-occupancy vs
  normalized shape) — mixing these bases is the exact failure this prompt exists to prevent.
- **Customer and staff presence never merged in one number.**
- **No fabricated precision;** flag GAPs. **Stay on topic** — shapes, targets, normalization only.
