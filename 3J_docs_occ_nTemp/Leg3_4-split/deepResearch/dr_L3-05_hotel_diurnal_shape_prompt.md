# Deep-Research Prompt dr_L3-05 — HOTEL GUEST-ROOM DIURNAL SHAPE s(t), numeric (48 half-hour slots)

> SCOPE GUARD — READ FIRST. This is the **diurnal-shape** task of the Leg-3 set. Its deliverable is a
> **numeric, unit-normalized 24-hour guest-room presence curve at 30-minute resolution** (48 slots,
> max = 1.0), weekday + weekend variants, that we will scale by Statistics Canada monthly occupancy
> rates. Do NOT hunt for the monthly occupancy data itself (that is `dr_L3-01`), do NOT produce EUI
> benchmarks (that is `dr_L3-03`), and do NOT cover retail (`dr_L3-02`, `dr_L3-04`). See
> `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A shape-extraction brief. Our hotel channel schedules the guest-room zones of a LargeHotel-style
prototype as `hotel_multiplier(t, month, PR) = s(t) × StatCan_occupancy_rate(month, PR)`. The monthly
amplitude is handled elsewhere; **this prompt is only about `s(t)`** — the within-day presence shape.
National time-use surveys cannot provide it (hotel guests are outside their sampling frame), so it must
come from standards, prototype schedules, and measured hospitality studies. Report slots in **00:00 →
23:30 order** (we re-index to our internal 04:00-origin grid ourselves).

## Role

Hospitality-operations and building-energy researcher. Ground the standards side in the actual
published schedule fractions — ASHRAE 90.1 Appendix G hotel schedules, the US DOE / PNNL Large Hotel
prototype guest-room schedules (the schedule objects in the prototype models themselves, or their
documentation), and Canada's NECB 2017/2020 hotel space schedules. Ground the measured side in sensor /
keycard / smart-thermostat studies of when guests are physically in their rooms. Ground the market-mix
side in Montreal and Calgary downtown market reports (business vs leisure demand). **Distinguish
measured numbers from standard-assumed numbers in every cell** — that distinction decides how much we
trust each segment of the curve.

## Why this matters (so you scope correctly)

`s(t)` multiplies every guest-room People / Lights / Equipment schedule for all 26 simulated years and
all scenarios. Errors in the overnight plateau or the daytime trough propagate directly into the hotel
EUI trajectory and the peak-timing claims — and unlike the GSS channels, there is no diary data to
correct it downstream. The choice "one fixed shape × monthly amplitude" is also a standing design
assumption of the whole hotel side-track; if the literature shows the *shape itself* varies strongly by
season or market mix, we must know before the build, because it changes the lookup-table schema.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Standard / prototype guest-room occupancy fractions (the as-published numbers)

Give the actual fractions at the segment level; attach the full hourly listings in an appendix if long.

| Source | Overnight plateau (≈23:00–06:00) | Morning ramp-down (≈06:00–10:00) | Daytime trough (≈10:00–17:00) | Evening return (≈17:00–23:00) | Weekend deviation | Citation |
|---|---|---|---|---|---|---|
| ASHRAE 90.1 Appendix G hotel schedule |  |  |  |  |  |  |
| DOE / PNNL Large Hotel prototype (guest-room schedule object) |  |  |  |  |  |  |
| NECB 2017/2020 hotel space schedule |  |  |  |  |  |  |

### Table 2 — Measured guest-room presence (sensor / keycard / thermostat studies)

| Study | Method + sample | Overnight plateau | Daytime trough | Evening return timing | Business vs leisure noted? | Citation |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

### Table 3 — Business vs leisure mix, Montreal and Calgary

| Market | Business : leisure demand mix (best available) | Implied shape difference (weekday trough depth, weekend evening) | Citation |
|---|---|---|---|
| Downtown Montreal |  |  |  |
| Downtown Calgary |  |  |  |

### Table 4 — Shape stability (is fixed-shape × monthly-amplitude defensible?)

| Question | Evidence | Verdict (YES / NO / partial) | Citation |
|---|---|---|---|
| Does the diurnal *shape* (not level) vary materially by month/season? |  |  |  |
| Does it vary materially weekday vs weekend? |  |  |  |
| Does it vary materially business- vs leisure-dominated markets? |  |  |  |
| Do published hotel energy models use fixed shape × occupancy amplitude? |  |  |  |

### Table 5 — THE DELIVERABLE: recommended unit-normalized s(t), 48 slots

Unit-normalized: max = 1.0. Slots in 00:00 → 23:30 order. Give every slot; group rows by segment for
readability. Two variants.

| Slot (start time) | s(t) weekday | s(t) weekend | Basis (measured / standard / interpolated) |
|---|---|---|---|
| 00:00 |  |  |  |
| 00:30 |  |  |  |
| … (all 48 slots — do not skip any) |  |  |  |
| 23:30 |  |  |  |

---

## Part C — Synthesis (the shape verdict)

Give: (1) a segment-by-segment justification of the recommended curve (overnight / morning / daytime /
evening), naming which source anchors each segment and where sources disagreed; (2) an explicit
**defensibility statement**: is one fixed `s(t)` (weekday + weekend variants) × monthly amplitude
defensible for Canadian downtown hotels, with citations — and if only partially, the smallest extension
that fixes it (e.g., summer-vs-winter shape pair); (3) coupling notes: what fraction of guest-room load
the literature treats as presence-independent (feeds how the multiplier is applied to Lights vs
Equipment vs HVAC setpoints); (4) how far the recommended curve deviates from the NECB baseline
schedule we are modulating — large deviations mean the multiplier does real work, near-identity means
the channel adds little; say which it is.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated** (Table 5 with all 48 slots — this is the deliverable).
2. Then Part C synthesis.
3. Inline citations; measured vs standard-assumed flagged in every cell of Tables 1–2 and in Table 5's
   basis column.
4. **"Confidence and caveats":** which curve segment is least certain.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Table 5 must contain all 48 numeric slots, both variants, max = 1.0** — a prose description of the
  shape does not close this prompt.
- **Every number tagged measured vs standard-assumed vs interpolated.**
- **No fabricated precision:** where no source gives a segment, mark it interpolated and say between
  which anchors.
- **Stay on topic** — the within-day shape only; monthly amplitude, forecasting, and EUI belong to
  `dr_L3-01` / `dr_L3-03`.
