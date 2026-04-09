# Future Research — O5: Synthetic Co-presence Schedules for BEM

**Source:** SWOT analysis of the GSS Occupancy Pipeline
(`docs_debug/00_SWOT_pipeline.md`, opportunity O5).

**Status:** Parked for future work. Not in scope for the eSim 2026 paper.

---

## The opportunity in plain language

Almost every BEM occupancy schedule used today is a single binary signal:
"the building is occupied" or "the building is empty." That hides a lot of
behavior. When *who* is home matters — for plug loads, internal gains,
demand response targeting, or per-room thermal comfort — a single binary
flag is not enough.

This pipeline produces 9 binary co-presence columns (Alone, Spouse,
Children, parents, otherInFAMs, otherHHs, friends, others, colleagues) at
30-minute resolution. That is enough to answer questions like:

- "Is someone home alone, or is the household together in one room?"
- "Are children present? (changes plug-load and lighting profiles)"
- "Are guests present? (raises internal gains and DHW demand)"

## Why this is worth coming back to

- This is genuinely novel for BEM. Most synthetic occupancy work in the
  building energy literature stops at presence/absence.
- The data exists *now* — it does not need any extra collection. It just
  needs to be wired into a BEM run end-to-end.
- It opens doors to per-room and per-occupant disaggregated energy use
  research, which is currently bottlenecked by lack of co-presence data.

## What a future project would look like

1. Take one detailed multi-zone EnergyPlus model (e.g. a 3-bedroom
   detached house from `0_BEM_Setup/`).
2. For one archetype, generate co-presence-aware schedules from the Step 4
   model output.
3. Run two BEM simulations:
   - Run A: standard binary occupancy schedule.
   - Run B: co-presence-aware schedule, with per-occupant metabolic gain
     and per-room presence routing.
4. Report: differences in EUI, peak load, and per-room comfort metrics.
5. Identify which building types and which archetypes show the biggest
   sensitivity to co-presence-aware modelling. Those are the ones where
   the standard binary schedule is most wrong.

## Possible follow-on directions

- **Per-room internal gain attribution.** If you know that 3 people are
  in the living room from 7–9 PM and 1 person is in the bedroom, you can
  put internal gains in the right zone instead of smearing them.
- **Plug-load disaggregation.** Children present → games console / TV
  load profile. Adults working from home → laptop / monitor profile.
- **Demand response targeting.** Programs that defer DHW or HVAC are
  more acceptable when no one is home, or when only one person is home,
  vs. when the whole family is present.

## What is needed before this is feasible

- A clean Step 4 model output with co-presence columns validated
  (depends on Task 4 / W7 from the SWOT — confirm the encoding is
  consistent across cycles first).
- A multi-zone IDF that has rooms defined separately, not lumped into
  one thermal zone.
- A small extension to `eSim_bem_utils/integration.py` to route
  co-presence into per-zone schedules.

## Risk if delayed

Low. The data does not go stale and the idea is unlikely to be scooped
exactly — it requires the unusual combination of (a) survey-derived
co-presence data, (b) multi-zone BEM, and (c) someone who understands
both halves. Worth coming back to once the eSim paper is out.
