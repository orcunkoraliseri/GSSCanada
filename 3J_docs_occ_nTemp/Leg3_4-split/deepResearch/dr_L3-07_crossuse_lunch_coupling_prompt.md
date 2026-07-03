# Deep-Research Prompt dr_L3-07 — CROSS-USE COUPLING: the office→retail lunch transition (model it or not?)

> SCOPE GUARD — READ FIRST. This is the **design-decision** task for OPEN DECISION 7 of the Leg-3
> plan: should the pipeline explicitly model intra-day cross-use transitions (office workers becoming
> retail customers at lunch) or keep the four channels independent? The deliverable is an evidence-based
> recommendation, not a model. Do NOT survey mixed-use occupancy modelling in general (the foundational
> Prompt-10 report covers it), do NOT produce diurnal targets (`dr_L3-06`), and do NOT touch hotels.
> See `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A decision brief. Our four channels are derived from the *same* GSS respondents' diaries, so at the
**population level** cross-use consistency is automatic: when a respondent's diary moves from workplace
to store at 12:30, AT_WORK loses them and AT_RETAIL gains them in the same slot. The open question is
strictly about the **within-building** level: in a mixed-use tower, the podium retail's lunch peak is
partly fed by the *same building's* office floors. Channels-independent modelling treats those as
uncorrelated populations; explicit coupling would tie the podium-retail lunch surge to the tower's own
office presence. Is the added realism worth the machinery — and does anyone have evidence it changes
energy results?

> **What "coupling" could mean here (evaluate each):** (a) nothing — population-level consistency is
> deemed sufficient; (b) diagnostic only — report the GSS-derived office→retail transition statistics
> as a paper figure without wiring them into simulation; (c) schedule-level coupling — scale the podium
> retail lunch peak by the building's own office presence multiplier; (d) full agent-level flows —
> out of scope by construction (our generator is diary-level, not agent-in-building).

## Role

UBEM / mixed-use-buildings researcher with an activity-based-modelling side. Ground the behavioural
side in time-use / mobility evidence of lunch-hour worker flows into retail and food service; the
modelling side in any occupancy or UBEM study that couples uses within one building or district
(shared-population models, activity-chain models, agent-based downtown simulations); the energy side in
any study quantifying whether cross-use coupling *changes simulated energy* versus independent
schedules. Also cover the criticisms: double-counting people across uses and identifiability of
coupled schedules.

## Why this matters (so you scope correctly)

This is a freeze-blocking decision: the Step-4 Transformer head and the Step-7 injector are built
differently under options (a)–(c), and retrofitting coupling after the head is trained means retraining.
It is also a paper-positioning question — the office→retail lunch transition measured from national
diaries could be a novelty claim (option b) even if simulation-side coupling (option c) is rejected.
What we must not do is choose by taste: if the literature shows within-building coupling moves retail
zone loads by ~nothing (retail HVAC/lights follow opening hours regardless), option (c)'s cost is
unjustifiable and the decision writes itself.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Behavioural evidence: lunch-hour office→retail/food flows

| Study | Data (time-use / mobility / footfall) | Magnitude of the flow (share of office workers leaving at lunch; where they go; dwell time) | Relevance to a downtown tower podium | Citation |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

### Table 2 — Modelling precedents: who couples uses, who keeps them independent

| Study / tool | Uses modelled | Coupling mechanism (shared population / activity chains / none) | Stated reason | Citation |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

### Table 3 — Energy materiality: does coupling change simulated results?

| Study | Compared coupled vs independent schedules? | Reported effect on loads / EUI / peaks | Citation |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |

### Table 4 — Risks of coupling (the criticisms to design against)

| Risk | How it arises in a shared-diary 4-channel design like ours | Documented instance / reviewer criticism | Mitigation | Citation |
|---|---|---|---|---|
| Double-counting a person in two uses at once |  |  |  |  |
| Identifiability (coupled schedules can't be validated separately) |  |  |  |  |
| Frame mismatch (building's workers ≠ national diary population) |  |  |  |  |

### Table 5 — Decision matrix (the deliverable)

| Option | Build cost | Evidence of energy benefit | Paper value | Risk | Verdict (recommend / viable / reject) |
|---|---|---|---|---|---|
| (a) Independent channels, population-consistency only |  |  |  |  |  |
| (b) Diagnostic coupling figure, no simulation wiring |  |  |  |  |  |
| (c) Schedule-level coupling (podium retail × own-tower office presence) |  |  |  |  |  |
| (d) Agent-level flows |  |  |  | (pre-filled) out of scope by construction | reject |

---

## Part C — Synthesis (the recommendation)

Give: (1) a single recommended option from Table 5 with its two strongest citations; (2) if (b) is
recommended (or part of the recommendation), specify the diagnostic exactly — which GSS transition
statistic to compute (e.g., P(AT_RETAIL at t | AT_WORK at t−1..t−k), by cycle) and what figure it
makes; (3) if (c) is rejected, the one-sentence sourced justification the paper can cite when a
reviewer asks "why didn't you couple the uses?"; (4) an explicit statement of what would change the
verdict (the evidence threshold at which coupling becomes worth building).

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C recommendation.
3. Inline citations; behavioural vs modelling vs energy-materiality sources kept distinct.
4. **"Confidence and caveats":** where the evidence is thinnest.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **End with ONE recommended option** — a balanced survey without a verdict does not close this prompt.
- **The energy-materiality table is mandatory** — if no study measured it, state that GAP explicitly
  (that absence is itself decision-relevant).
- **No fabricated precision;** flag GAPs. **Stay on topic** — this one decision only.
