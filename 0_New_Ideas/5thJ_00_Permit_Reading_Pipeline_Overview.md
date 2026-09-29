# Permit-Reading Retrofit and Cooling State for an Occupied Building Stock
### Cross-check of Montreal and Toronto permit text, abstention, and GSS occupancy — Paper 5 of the series
#### Full Pipeline Overview — one language reader, one stock model (Montreal first)

Written 2026-09-26 from `5thJ_01_Methods_Design.md` (design v1, ruled D-5J-2 (a)). This file is the
one-page picture; the step-by-step checklist is `5thJ_00_Permit_Reading_Pipeline.md`. Nothing here
overrides the design doc: if they disagree, the design doc and its Progress Log win. Edit in place.

---

## AIM

Canadian cities do not know which homes have new windows, added insulation, a heat pump or air
conditioning. Permits record some of this work in short clerk text (French in Montreal, English in
Toronto). Much of it needs no permit at all (all heat pumps and air conditioners in Montreal), so a
missing permit means **unknown**, never **none**.

Read that text with an open-weight language model that either answers or **abstains**, with coverage
stated per group (split conformal). Combine what it reads with area shares (EnerGuide by postal area,
StatCan by city) into a probability for each building's state. Carry that uncertainty through paired
EnergyPlus runs driven by GSS time-use occupancy, and show how much the unknown state changes heating
and cooling demand and the indoor heat felt by the people actually at home.

> **Series position.** Paper 1 = Italy, ML occupancy. Paper 2 (2J) = Canada residential + temperature.
> Paper 3 (3J) = four channels, mixed-use tower. Paper 4 (4J) = HETUS, one language model, many
> countries. **Paper 5 (this doc) moves the unknown from the occupant to the building: what state is
> the house in?** It keeps the series spine (paired EnergyPlus, occupancy effect isolated) and stays
> distinct from the NSERC subject: no power failure, no survivability window, supply is always on.

> **Status convention.** ✅ DONE = artefact on disk and reviewed. 🟡 PARTIAL = artefact exists, part
> void or unreviewed. ⬜ NOT STARTED. 🔴 = must be read before acting. Status as of **2026-09-26**.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WP0 — FREEZE AND INVENTORY                       ✅ A done · 🟡 B open (B2) ║
║  permits, roll, EnerGuide, StatCan, 2J model inventory -> _5J_data/          ║
║  traps found: roll year 9999 = placeholder; 3.9 % of joins hit mixed ages    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP1 — LABELS AND SAMPLING                                       ⬜ next    ║
║  5thJ_02_Label_Spec.md -> 7 labels (W I HP AC F + resets N D)                ║
║  Montreal 2,000 + Toronto 600 permit texts; yes / no / cannot tell           ║
║  400 texts labelled twice; kappa >= 0.6 or the label is merged/dropped       ║
║  sealed test sets, checksummed             <- WAITING ON D-5J-3 (who labels) ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FREEZE section 7 gates by checksum BEFORE any test row is scored            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP2 — FOUR READERS (RQ1)                                        ⬜         ║
║  keyword rule · Gunay-style rules · small fine-tuned encoder · open LLM      ║
║  LLM must beat the best of the other three by 0.05 macro-F1, or it is a tie  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP3 — ABSTENTION WITH STATED COVERAGE (RQ2)                     ⬜         ║
║  split conformal, alpha 0.10, Mondrian groups (type, decade, borough)        ║
║  shift: Montreal -> Toronto, before/after 2010 (reported, not gated)         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP4 — PERMIT EVENTS -> BUILDING STATE (RQ3)                     ⬜         ║
║  join permits to roll; N/D reset history; prior from EnerGuide + StatCan     ║
║  unpermitted work: P(up | nothing read) = pi(1-d) / (1 - pi d)               ║
║  check: 90 % interval contains area shares                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP5 — ENERGYPLUS CAMPAIGN (RQ4)                                 ⬜         ║
║  4 geometries x 3 vintages x ~24 states x 50 GSS draws x 2 weathers          ║
║  ~ 29,000 paired runs on Speed, within 32 CPUs, 1 to 2 days                  ║
║  needs O-1 (envelope values by vintage) and baseboard/heat-pump variants     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP6 — PROPAGATION AND SPLIT OF THE SPREAD (RQ4)                 ⬜         ║
║  1,000 stock draws; heating, cooling, peaks, occupied-hour overheating       ║
║  spread split: unknown state vs occupancy vs interaction                     ║
║  counterfactual: prior only / keyword reader / LLM reader with abstention    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## RESEARCH QUESTIONS

| RQ | Question in plain words | Work package |
|---|---|---|
| RQ1 | How well does an open-weight language model recover five retrofit events from short French and English permit text, against human labels and three simpler readers? | WP2 |
| RQ2 | With conformal prediction, what coverage and abstention rate does it reach per group, and does it survive a change of city, language or period? | WP3 |
| RQ3 | When read events, area shares and a detection rate for unpermitted work are combined, how far is each building's state known, and do the shares match EnerGuide and StatCan? | WP4 |
| RQ4 | How much of the spread in heating, cooling, peaks and occupied-hour overheating comes from the unknown state, compared with who is at home? | WP5, WP6 |

## SCOPE, DECIDED

| Item | Decision |
|---|---|
| Development city | Montreal (permits CC BY 4.0, 560,309 rows; open assessment roll for vintage and dwelling count) |
| Held-out city | Toronto, reading only (RQ1, RQ2); no open roll with vintage, so no Toronto stock run |
| Stock and simulation | Montreal only |
| Labels | Windows replaced (W), insulation added (I), heat pump (HP), central air conditioning (AC), heating system or fuel change (F); resets: new construction (N), demolition (D) |
| Reference year | State at end of 2022 (matches GSS 2022 and StatCan tables) |
| Weather | Montreal CWEC 2020 typical year plus the actual 2018 year (July heat wave); present climate only |
| Outside benchmark | New York City named as the route to per-building truth; **not run in v1** |

## VALIDATION GATES (DRAFT; frozen by checksum at the end of WP1)

| Gate | What | DRAFT threshold |
|---|---|---|
| G5J.1 | Label agreement | kappa ≥ 0.6 per kept label |
| G5J.2 | Reader gain | LLM macro-F1 ≥ best baseline + 0.05, bootstrap interval excludes 0 |
| G5J.3 | Coverage, Montreal | in [0.87, 0.93] at alpha 0.10, overall and in every group with ≥ 50 test rows |
| G5J.4 | Coverage, shift | reported, not gated |
| G5J.5 | Abstention usefulness | ≤ 40 % on W at the gate alpha; reported for every label |
| G5J.6 | Area check | 90 % interval holds the EnerGuide share in ≥ 80 % of Montreal FSAs with ≥ 30 audited homes, and the StatCan city share for AC and heat pump |
| G5J.7 | Base stock | energy intensity inside a report-only band from NRCan SHEU 2019 (Quebec) |

A gate that cannot be computed is NOT_EVALUABLE, never PASS. Each gate must be seen failing under one
named perturbation before it is trusted (design doc section 7).

## WHAT MAKES IT NEW

Retrofit and cooling state read from French and English record text, with abstention at stated
coverage, carried as uncertainty into a stock model with time-use occupancy. Nearest work (all read at
source): Gunay et al. 2023 (keywords and rules, no equipment, no abstention), Zhang et al. 2020 (BERT,
work type, no abstention, no French), Wu et al. 2026 Geo2UBEM (language model tunes model inputs, reads
no records), Borrotti 2024 (conformal on simulated loads, not text), Geske and Voelker 2025
(refurbishment uncertainty, Germany). **Not** "first language model for urban energy model inputs".

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Missing permit = unknown, not none | Heat pumps and air conditioners need no permit in Montreal |
| Abstain with stated coverage | The building state is only as good as the reader knows its own limits |
| Human labels, never model labels | The labels are the only per-text truth in the paper |
| Sealed test sets, gates frozen first | No threshold is tuned after seeing the test rows |
| EnerGuide is an area check, never a per-building label | Audited homes chose to be audited, so shares lean towards upgraded homes |
| Paired runs, redraw stock by weighting | No new simulations are needed to redraw the stock |
| Duplexes and triplexes use the attached-house model | No own model; written as a limitation |

## OPEN DECISIONS AND ITEMS

* **D-5J-3** Who writes the labels (WP1)? Recommend (a): the author labels about 2,600 texts
  (10 to 12 hours); a colleague labels 400 of them blind. (b) two paid assistants; (c) author alone,
  400 re-labelled after two weeks (weaker). **The only decision that belongs to the author.**
* **O-1** Canadian envelope values by vintage (U-values, air-tightness). Needs one external deep
  research prompt, run by the author in Gemini, only when the author agrees.
* **O-3** EnerGuide file contents and Montreal FSA counts (B2 redo); G5J.6 may shrink if few FSAs pass
  the 30-home floor.
* **O-4** Mostly closed: all 2J models have a gas furnace and DX cooling; baseboard and heat-pump
  variants must be built, one test run per variant.
* **O-5** Pauling 2026 (SSRN) and Jiang et al. 2025 (Energy) unread; before submission.
* **O-6** Venue, decided when RQ1 results exist.

## LIMITATIONS — pointer, not a copy

Written as they arise in the design doc, sections 3 to 6. Already known: Montreal only for the stock;
the attached house stands in for plexes; EnerGuide shares are biased towards upgraded homes; no future
weather; no Toronto stock run.
